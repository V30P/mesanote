from typing import Callable, List as PyList, TypeVar, cast

from mesanote.cursors import Cursor, CursorDepletedError
from mesanote.tokens import (
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
    DefinitionStartToken,
    TableStartToken,
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
    Table,
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
        content.append(_parse_element(cursor))

    return Document(content)


def _parse_element(cursor: Cursor, section_depth: int = 0) -> Element:
    if cursor.check_type(StringStartToken):
        return _parse_string(cursor)
    elif cursor.check_type(GroupStartToken):
        return _parse_grouping(cursor, section_depth)
    elif cursor.check_type(StructureStartToken):
        return _parse_structure(cursor, section_depth)

    token = cursor.peek()
    raise ParseError(
        f"Started an element at {token.source} with invalid token: '{type(token).__name__}'."
    )


def _parse_grouping(cursor: Cursor, section_depth: int) -> Grouping:
    _match_type_or_raise(cursor, GroupStartToken)
    source = cursor.previous().source

    elements = []
    try:
        while not cursor.match_type(GroupEndToken):
            elements.append(
                _with_context(
                    lambda: _parse_element(cursor, section_depth), f"in grouping at {source}."
                )
            )
    except CursorDepletedError:
        raise ParseError(f"Grouping at {source} was not closed.")

    return Grouping(elements)


def _parse_string(cursor: Cursor) -> String:
    _match_type_or_raise(cursor, StringStartToken)
    source = cursor.previous().source

    substrings = []
    try:
        while not cursor.match_type(StringEndToken):
            substrings.append(
                _with_context(lambda: _parse_substring(cursor), f"in string at {source}.")
            )
    except CursorDepletedError:
        raise ParseError(f"String at {source} was not closed.")

    return String(substrings)


def _parse_substring(cursor: Cursor) -> Substring:
    if cursor.check_type(TextToken):
        return _parse_text(cursor)
    elif cursor.check_type(EmphasisToken):
        return _parse_emphasis(cursor)
    elif cursor.check_type(CodeToken):
        return _parse_code(cursor)

    token = cursor.peek()
    raise ParseError(
        f"Started a substring at {token.source} with invalid token: "
        f"'{token.__class__.__name__}' at {token.source}."
    )


def _parse_text(cursor: Cursor) -> Text:
    _check_type_or_raise(cursor, TextToken)
    return Text(cast(TextToken, cursor.advance()).value)


def _parse_emphasis(cursor: Cursor) -> Emphasis:
    cursor.match_type(EmphasisToken)
    source = cursor.previous().source

    if cursor.check_type(TextToken):
        text = _parse_text(cursor)
        if not cursor.match_type(EmphasisToken):
            raise ParseError(f"Emphasis at {source} was not closed.")
        return Emphasis(text)
    elif cursor.check_type(EmphasisToken):
        return _parse_strong_emphasis(cursor)

    raise ParseError(
        f"Invalid token in emphasis at {source}: '{type(cursor.peek()).__name__}'."
    )


def _parse_strong_emphasis(cursor: Cursor) -> StrongEmphasis:
    cursor.match_type(EmphasisToken)
    source = cursor.previous().source

    if cursor.check_type(TextToken):
        text = _parse_text(cursor)
        if not cursor.match_many([EmphasisToken(), EmphasisToken()]):
            raise ParseError(f"Strong emphasis at {source} was not closed.")
        return StrongEmphasis(text)
    elif cursor.check_type(EmphasisToken):
        emphasis = _parse_emphasis(cursor)
        if not cursor.match_many([EmphasisToken(), EmphasisToken()]):
            raise ParseError(f"Strong emphasis at {source} was not closed.")
        return StrongEmphasis(emphasis)

    raise ParseError(
        f"Invalid token in strong emphasis at {source}: '{type(cursor.peek()).__name__}'."
    )


def _parse_code(cursor: Cursor) -> Code:
    _check_type_or_raise(cursor, CodeToken)
    return Code(cast(CodeToken, cursor.advance()).value)


def _parse_structure(cursor: Cursor, section_depth: int) -> Structure:
    section_depth += 1

    if cursor.check_type(SectionStartToken):
        return _parse_section(cursor, section_depth)
    elif cursor.check_type(ListStartToken):
        return _parse_list(cursor, section_depth)
    elif cursor.check_type(DefinitionStartToken):
        return _parse_definitions(cursor)
    elif cursor.check_type(TableStartToken):
        return _parse_table(cursor, section_depth)

    token = cursor.peek()
    raise ParseError(
        f"Started a structure at {token.source} with invalid token: '{type(token).__name__}'."
    )


def _parse_section(cursor: Cursor, section_depth: int) -> Section:
    _match_type_or_raise(cursor, SectionStartToken)
    source = cursor.previous().source

    title = _with_context(
        lambda: _parse_string(cursor), f"in title for section at {source}."
    )
    element = _with_context(
        lambda: _parse_element(cursor, section_depth), f"in element for section at {source}."
    )

    return Section(title, element, section_depth)


def _parse_list(cursor: Cursor, section_depth: int) -> List:
    _match_type_or_raise(cursor, ListStartToken)
    source = cursor.previous().source

    grouping = _with_context(
        lambda: _parse_grouping(cursor, section_depth), f"in grouping for list at {source}."
    )

    return List(grouping)


def _parse_definitions(cursor: Cursor) -> Definitions:
    terms = []
    while True:
        _match_type_or_raise(cursor, DefinitionStartToken)
        source = cursor.previous().source

        term = _with_context(
            lambda: _parse_string(cursor), f"in term for definition at {source}."
        )
        definition = _with_context(
            lambda: _parse_string(cursor), f"in value for definition at {source}."
        )
        terms.append((term, definition))

        if cursor.is_at_end() or not cursor.check_type(DefinitionStartToken):
            break

    return Definitions(terms)


def _parse_table(cursor: Cursor, section_depth) -> Table:
    _match_type_or_raise(cursor, TableStartToken)
    source = cursor.previous().source

    rows_group = _with_context(
        lambda: _parse_grouping(cursor, section_depth), f"in content for table at {source}."
    )

    # Break grouping down into rows of elements
    rows = []
    for row_element in rows_group.elements:
        row = []
        if isinstance(row_element, Grouping):
            for element in row_element.elements:
                row.append(element)
        else:
            row.append(row_element)
        rows.append(row)
    
        
    return Table(rows)


def _with_context[T](func: Callable[[], T], context: str) -> T:
    try:
        return func()
    except CursorDepletedError:
        raise ContextualParseError(ParseError("Unexpected end of file."), context)
    except ContextualParseError:
        raise
    except ParseError as e:
        raise ContextualParseError(e, context)


def _check_type_or_raise[T: Token](cursor: Cursor, token_type: type[T]) -> None:
    if not cursor.check_type(token_type):
        _raise_expected_error(token_type, type(cursor.peek()))


def _match_type_or_raise[T: Token](cursor: Cursor, token_type: type[T]) -> None:
    if not cursor.match_type(token_type):
        _raise_expected_error(token_type, type(cursor.peek()))


def _raise_expected_error(expected: type[Token], got: type[Token]):
    raise ParseError(f"Expected '{expected.__name__}' but got '{got.__name__}'.")
