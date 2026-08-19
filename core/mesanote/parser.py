from typing import List as PyList, cast

from mesanote.cursor import Cursor, CursorError
from mesanote.tokens import (
    Token,
    StringStartToken,
    StringEndToken,
    TextToken,
    EmphasisToken,
    CodeStartToken,
    CodeEndToken,
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
        except Exception as e:
            raise ParseError(f"Error while parsing {self.context}: {e}")

    def peek_type[T: Token](self, token_type: type) -> bool:
        return isinstance(self.cursor.peek(), token_type)

    def match_type[T: Token](self, token_type: type) -> bool:
        matched = self.peek_type(token_type)
        if matched:
            self.cursor.advance()
        return matched

    def parse_document(self) -> Document:
        content = []
        while not self.cursor.is_at_end():
            content.append(self.parse_element())
        return Document(content)

    def parse_element(self) -> Element:
        self.context = "element"

        if self.peek_type(StringStartToken):
            return self.parse_string()
        elif self.peek_type(GroupStartToken):
            return self.parse_grouping()
        elif self.peek_type(StructureStartToken):
            return self.parse_structure()

        raise Exception(
            f"Cannot start an element with token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_grouping(self) -> Grouping:
        self.context = "grouping"
        self.cursor.advance()

        elements = []
        while not self.peek_type(GroupEndToken):
            elements.append(self.parse_element())

        self.cursor.advance()
        return Grouping(elements)

    def parse_string(self) -> String:
        self.context = "string"
        self.cursor.advance()

        substrings = []
        while not self.peek_type(StringEndToken):
            substrings.append(self.parse_substring())

        self.cursor.advance()
        return String(substrings)

    def parse_substring(self) -> Substring:
        self.context = "substring"
        token = self.cursor.peek()

        if self.peek_type(TextToken):
            return self.parse_text()
        elif self.peek_type(EmphasisToken):
            return self.parse_emphasis()
        elif self.peek_type(CodeStartToken):
            return self.parse_code()

        raise Exception(
            f"Cannot start a substring with token of type: '{token.__class__.__name__}'."
        )

    def parse_text(self) -> Text:
        return Text(cast(TextToken, self.cursor.advance()).value)

    def parse_emphasis(self) -> Emphasis:
        self.context = "emphasis"
        self.match_type(EmphasisToken)

        if self.peek_type(TextToken):
            text = self.parse_text()
            if not self.match_type(EmphasisToken):
                raise Exception("Emphasis was not closed.")

            return Emphasis(text)
        elif self.peek_type(EmphasisToken):
            return self.parse_strong_emphasis()

        raise Exception(
            f"Emphasis cannot contain token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_strong_emphasis(self) -> StrongEmphasis:
        self.context = "strong emphasis"
        self.match_type(EmphasisToken)

        if self.peek_type(TextToken):
            text = self.parse_text()
            if not self.cursor.match_many([EmphasisToken(), EmphasisToken()]):
                raise Exception("Strong emphasis was not closed.")

            return StrongEmphasis(text)
        elif self.peek_type(EmphasisToken):
            emphasis = self.parse_emphasis()
            if not self.cursor.match_many([EmphasisToken(), EmphasisToken()]):
                raise Exception("Strong emphasis was not closed.")

            return StrongEmphasis(emphasis)

        raise Exception(
            f"Strong emphasis cannot contain token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_code(self) -> Code:
        self.context = "code"
        self.match_type(CodeStartToken)

        if not self.peek_type(TextToken):
            raise Exception("Code block must contain text.")
        text = self.parse_text()

        if not self.match_type(CodeEndToken):
            raise Exception("Code block was not closed.")

        return Code(text)

    def parse_structure(self) -> Structure:
        self.context = "structure"
        self.depth += 1

        if self.peek_type(SectionStartToken):
            structure = self.parse_section()
        elif self.peek_type(ListStartToken):
            structure = self.parse_list()
        else:
            raise Exception(
                f"Cannot start a structure with token of type: '{type(self.cursor.peek()).__name__}'."
            )

        self.depth -= 1
        return structure

    def parse_section(self) -> Section:
        self.context = "section"
        self.match_type(SectionStartToken)

        title = self.parse_string()
        element = self.parse_element()
        return Section(title, element, self.depth)

    def parse_list(self) -> List:
        self.context = "list"
        self.match_type(ListStartToken)

        if not self.peek_type(GroupStartToken):
            raise Exception("List must be followed by a grouping.")

        return List(self.parse_grouping())


def parse(tokens: PyList[Token]) -> Document:
    return Parse(tokens).result
