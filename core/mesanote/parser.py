from typing import List as PyList, cast

from mesanote.cursor import Cursor, CursorError
from mesanote.tokens import (
    Token,
    StringStartToken,
    StringEndToken,
    TextToken,
    EmphasisToken,
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
    Grouping,
    Structure,
    Section,
    List,
)


class ParseError(Exception):
    pass


class Parse:
    def __init__(self, tokens: PyList[Token]):
        self.cursor = Cursor(tokens)
        self.depth = 0
        self.context = ""

        try:
            self.result = self.parse_document()
        except CursorError as e:
            raise ParseError(f"Error while parsing {self.context}: {e}")

    def peek_is[T: Token](self, token_type: type):
        return isinstance(self.cursor.peek(), token_type)

    def parse_document(self) -> Document:
        content = []
        while not self.cursor.is_at_end():
            content.append(self.parse_element())
        return Document(content)

    def parse_element(self) -> Element:
        self.context = "element"

        if self.peek_is(StringStartToken):
            return self.parse_string()
        elif self.peek_is(GroupStartToken):
            return self.parse_grouping()
        elif self.peek_is(StructureStartToken):
            return self.parse_structure()

        raise ParseError(
            f"Cannot start an element with token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_grouping(self) -> Grouping:
        self.context = "grouping"
        self.cursor.advance()

        elements = []
        while not self.peek_is(GroupEndToken):
            elements.append(self.parse_element())

        self.cursor.advance()
        return Grouping(elements)

    # region String parsing
    def parse_string(self) -> String:
        self.context = "string"
        self.cursor.advance()

        substrings = []
        while not self.peek_is(StringEndToken):
            substrings.append(self.parse_substring())

        self.cursor.advance()
        return String(substrings)

    def parse_substring(self) -> Substring:
        self.context = "substring"
        token = self.cursor.peek()

        if self.peek_is(TextToken):
            return Text(cast(TextToken, self.cursor.advance()).value)
        elif self.peek_is(EmphasisToken):
            return self.parse_emphasis()

        raise ParseError(
            f"Cannot start a substring with token of type: '{token.__class__.__name__}'."
        )

    def parse_text(self) -> Text:
        return Text(cast(TextToken, self.cursor.advance()).value)

    def parse_emphasis(self) -> Emphasis:
        self.context = "emphasis"
        self.cursor.advance()  # Consume opening *

        if self.peek_is(TextToken):
            text = self.parse_text()
            if not self.cursor.match(EmphasisToken()):
                raise ParseError("Emphasis was not closed.")

            return Emphasis(text)
        elif self.peek_is(EmphasisToken):
            return self.parse_strong_emphasis()

        raise ParseError(
            f"Emphasis cannot contain token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_strong_emphasis(self) -> StrongEmphasis:
        self.context = "strong emphasis"
        self.cursor.advance()  # Consume remaining opening *

        if self.peek_is(TextToken):
            text = self.parse_text()
            if not self.cursor.match_many([EmphasisToken(), EmphasisToken()]):
                raise ParseError("Strong emphasis was not closed.")

            return StrongEmphasis(text)
        elif self.peek_is(EmphasisToken):
            emphasis = self.parse_emphasis()
            if not self.cursor.match_many([EmphasisToken(), EmphasisToken()]):
                raise ParseError("Strong emphasis was not closed.")

            return StrongEmphasis(emphasis)

        raise ParseError(
            f"Strong emphasis cannot contain token of type: '{type(self.cursor.peek()).__name__}'."
        )

    # endregion

    # region Structure parsing
    def parse_structure(self) -> Structure:
        self.context = "structure"
        self.depth += 1

        if self.peek_is(SectionStartToken):
            structure = self.parse_section()
        elif self.peek_is(ListStartToken):
            structure = self.parse_list()
        else:
            raise ParseError(
                f"Cannot start a structure with token of type: '{type(self.cursor.peek()).__name__}'."
            )

        self.depth -= 1
        return structure

    def parse_section(self) -> Section:
        self.context = "section"
        self.cursor.advance()

        title = self.parse_string()
        element = self.parse_element()
        return Section(title, element, self.depth)

    def parse_list(self) -> List:
        self.context = "list"
        self.cursor.advance()

        if not self.peek_is(GroupStartToken):
            raise ParseError("List must be followed by a grouping.")

        return List(self.parse_grouping())

    # endregion


def parse(tokens: PyList[Token]) -> Document:
    return Parse(tokens).result
