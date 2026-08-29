from typing import Callable, List as PyList, TypeVar, cast

from mesanote.cursors import Cursor, CursorDepletedError
from mesanote.tokens import (
    DefinitionStartToken,
    Token,
    StringStartToken,
    StringEndToken,
    TextToken,
    EmphasisToken,
    CodeToken,
    GroupStartToken,
    GroupEndToken,
    StructureStartToken,
    SectionStartToken,
    ListStartToken,
)
from mesanote.nodes import (
    Document,
    Element,
    String,
    Substring,
    Text,
    Emphasis,
    StrongEmphasis,
    Code,
    Grouping,
    Structure,
    Section,
    List,
    Definitions,
)


class ParseError(Exception):
    pass


class ContextualParseError(ParseError):
    def __init__(self, original: ParseError, context: str):
        message = str(original).removesuffix(".")
        super().__init__(f"{message} {context}")


def parse(tokens: PyList[Token]) -> Document:
    cursor = Cursor(tokens)

    content = []
    while not cursor.is_at_end():
        content.append(parse_element(cursor))

    return Document(content)


def parse_element(cursor: Cursor, depth: int = 0) -> Element:
    if cursor.check_type(StringStartToken):
        return parse_string(cursor)
    elif cursor.check_type(GroupStartToken):
        return parse_grouping(cursor, depth)
    elif cursor.check_type(StructureStartToken):
        return parse_structure(cursor, depth)

    token = cursor.peek()
    raise ParseError(
        f"Started an element at {token.source} with invalid token: '{type(token).__name__}'."
    )


def parse_grouping(cursor: Cursor, depth: int) -> Grouping:
    match_type_or_raise(cursor, GroupStartToken)
    source = cursor.previous().source

    elements = []
    try:
        while not cursor.match_type(GroupEndToken):
            elements.append(
                with_context(
                    lambda: parse_element(cursor, depth), f"in grouping at {source}."
                )
            )
    except CursorDepletedError:
        raise ParseError(f"Grouping at {source} was not closed.")

    return Grouping(elements)


def parse_string(cursor: Cursor) -> String:
    match_type_or_raise(cursor, StringStartToken)
    source = cursor.previous().source

    substrings = []
    try:
        while not cursor.match_type(StringEndToken):
            substrings.append(
                with_context(lambda: parse_substring(cursor), f"in string at {source}.")
            )
    except CursorDepletedError:
        raise ParseError(f"String at {source} was not closed.")

    return String(substrings)


def parse_substring(cursor: Cursor) -> Substring:
    if cursor.check_type(TextToken):
        return parse_text(cursor)
    elif cursor.check_type(EmphasisToken):
        return parse_emphasis(cursor)
    elif cursor.check_type(CodeToken):
        return parse_code(cursor)

    token = cursor.peek()
    raise ParseError(
        f"Started a substring at {token.source} with invalid token: "
        f"'{token.__class__.__name__}' at {token.source}."
    )


def parse_text(cursor: Cursor) -> Text:
    check_type_or_raise(cursor, TextToken)
    return Text(cast(TextToken, cursor.advance()).value)


def parse_emphasis(cursor: Cursor) -> Emphasis:
    cursor.match_type(EmphasisToken)
    source = cursor.previous().source

    if cursor.check_type(TextToken):
        text = parse_text(cursor)
        if not cursor.match_type(EmphasisToken):
            raise ParseError(f"Emphasis at {source} was not closed.")
        return Emphasis(text)
    elif cursor.check_type(EmphasisToken):
        return parse_strong_emphasis(cursor)

    raise ParseError(
        f"Invalid token in emphasis at {source}: '{type(cursor.peek()).__name__}'."
    )


def parse_strong_emphasis(cursor: Cursor) -> StrongEmphasis:
    cursor.match_type(EmphasisToken)
    source = cursor.previous().source

    if cursor.check_type(TextToken):
        text = parse_text(cursor)
        if not cursor.match_many([EmphasisToken(), EmphasisToken()]):
            raise ParseError(f"Strong emphasis at {source} was not closed.")
        return StrongEmphasis(text)
    elif cursor.check_type(EmphasisToken):
        emphasis = parse_emphasis(cursor)
        if not cursor.match_many([EmphasisToken(), EmphasisToken()]):
            raise ParseError(f"Strong emphasis at {source} was not closed.")
        return StrongEmphasis(emphasis)

    raise ParseError(
        f"Invalid token in strong emphasis at {source}: '{type(cursor.peek()).__name__}'."
    )


def parse_code(cursor: Cursor) -> Code:
    check_type_or_raise(cursor, CodeToken)
    return Code(cast(CodeToken, cursor.advance()).value)


def parse_structure(cursor: Cursor, depth: int) -> Structure:
    depth += 1

    if cursor.check_type(SectionStartToken):
        return parse_section(cursor, depth)
    elif cursor.check_type(ListStartToken):
        return parse_list(cursor, depth)
    elif cursor.check_type(DefinitionStartToken):
        return parse_definitions(cursor)

    token = cursor.peek()
    raise ParseError(
        f"Started a structure at {token.source} with invalid token: '{type(token).__name__}'."
    )


def parse_section(cursor: Cursor, depth: int) -> Section:
    match_type_or_raise(cursor, SectionStartToken)
    source = cursor.previous().source

    title = with_context(
        lambda: parse_string(cursor), f"in title for section at {source}."
    )
    element = with_context(
        lambda: parse_element(cursor, depth), f"in element for section at {source}."
    )

    return Section(title, element, depth)


def parse_list(cursor: Cursor, depth: int) -> List:
    match_type_or_raise(cursor, ListStartToken)
    source = cursor.previous().source

    grouping = with_context(
        lambda: parse_grouping(cursor, depth), f"in grouping for list at {source}."
    )

    return List(grouping)


def parse_definitions(cursor) -> Definitions:
    terms = []
    while True:
        match_type_or_raise(cursor, DefinitionStartToken)
        source = cursor.previous().source

        term = with_context(
            lambda: parse_string(cursor), f"in term for definition at {source}."
        )
        definition = with_context(
            lambda: parse_string(cursor), f"in value for definition at {source}."
        )
        terms.append((term, definition))

        if cursor.is_at_end() or not cursor.check_type(DefinitionStartToken):
            break

    return Definitions(terms)


def with_context[T](func: Callable[[], T], context: str) -> T:
    try:
        return func()
    except CursorDepletedError:
        raise ContextualParseError(ParseError("Unexpected end of file."), context)
    except ContextualParseError:
        raise
    except ParseError as e:
        raise ContextualParseError(e, context)


def check_type_or_raise[T: Token](cursor: Cursor, token_type: type[T]) -> None:
    if not cursor.check_type(token_type):
        raise_expected_error(token_type, type(cursor.peek()))


def match_type_or_raise[T: Token](cursor: Cursor, token_type: type[T]) -> None:
    if not cursor.match_type(token_type):
        raise_expected_error(token_type, type(cursor.peek()))


def raise_expected_error(expected: type[Token], got: type[Token]):
    raise ParseError(f"Expected '{expected.__name__}' but got '{got.__name__}'.")
