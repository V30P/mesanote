from typing import List as PyList, cast

from mesanote.cursor import Cursor, CursorError
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


# TODO: Improve error handling here
class Parse:
    def __init__(self, tokens: PyList[Token]):
        self.cursor = Cursor(tokens)
        self.depth = 0
        self.context = ""

        try:
            self.result = self.parse_document()
        except Exception as e:
            raise ParseError(f"Error while parsing {self.context}: {e}")

    @staticmethod
    def raise_expected_error(expected: type[Token], got: type[Token]):
        raise Exception(f"Expected '{expected}' but got '{got}'")

    def check_type(self, token_type: type[Token]) -> bool:
        return isinstance(self.cursor.peek(), token_type)

    def match_type[T: Token](self, token_type: type[Token]) -> bool:
        matched = self.check_type(token_type)
        if matched:
            self.cursor.advance()
        return matched

    def check_type_or_raise[T: Token](self, token_type: type[Token]) -> bool:
        if not self.check_type(token_type):
            Parse.raise_expected_error(token_type, type(self.cursor.peek()).__name__)

    def match_type_or_raise[T: Token](self, token_type: type[Token]) -> bool:
        if not self.match_type(token_type):
            Parse.raise_expected_error(token_type, type(self.cursor.peek()).__name__)

    def parse_document(self) -> Document:
        content = []
        while not self.cursor.is_at_end():
            content.append(self.parse_element())
        return Document(content)

    def parse_element(self) -> Element:
        self.context = "element"

        if self.check_type(StringStartToken):
            return self.parse_string()
        elif self.check_type(GroupStartToken):
            return self.parse_grouping()
        elif self.check_type(StructureStartToken):
            return self.parse_structure()

        raise Exception(
            f"Cannot start an element with token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_grouping(self) -> Grouping:
        self.context = "grouping"
        self.match_type_or_raise(GroupStartToken)

        elements = []
        while not self.check_type(GroupEndToken):
            elements.append(self.parse_element())

        self.cursor.advance()
        return Grouping(elements)

    def parse_string(self) -> String:
        self.context = "string"
        self.match_type_or_raise(StringStartToken)

        substrings = []
        while not self.match_type(StringEndToken):
            substrings.append(self.parse_substring())

        return String(substrings)

    def parse_substring(self) -> Substring:
        self.context = "substring"
        token = self.cursor.peek()

        if self.check_type(TextToken):
            return self.parse_text()
        elif self.check_type(EmphasisToken):
            return self.parse_emphasis()
        elif self.check_type(CodeToken):
            return self.parse_code()

        raise Exception(
            f"Cannot start a substring with token of type: '{token.__class__.__name__}'."
        )

    def parse_text(self) -> Text:
        self.context = "text"
        self.check_type_or_raise(TextToken)
        return Text(cast(TextToken, self.cursor.advance()).value)

    def parse_emphasis(self) -> Emphasis:
        self.context = "emphasis"
        self.match_type(EmphasisToken)

        if self.check_type(TextToken):
            text = self.parse_text()
            if not self.match_type(EmphasisToken):
                raise Exception("Emphasis was not closed.")

            return Emphasis(text)
        elif self.check_type(EmphasisToken):
            return self.parse_strong_emphasis()

        raise Exception(
            f"Emphasis cannot contain token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_strong_emphasis(self) -> StrongEmphasis:
        self.context = "strong emphasis"
        self.match_type(EmphasisToken)

        if self.check_type(TextToken):
            text = self.parse_text()
            if not self.cursor.match_many([EmphasisToken(), EmphasisToken()]):
                raise Exception("Strong emphasis was not closed.")

            return StrongEmphasis(text)
        elif self.check_type(EmphasisToken):
            emphasis = self.parse_emphasis()
            if not self.cursor.match_many([EmphasisToken(), EmphasisToken()]):
                raise Exception("Strong emphasis was not closed.")

            return StrongEmphasis(emphasis)

        raise Exception(
            f"Strong emphasis cannot contain token of type: '{type(self.cursor.peek()).__name__}'."
        )

    def parse_code(self) -> Code:
        self.context = "code"
        self.check_type_or_raise(CodeToken)
        return Code(cast(CodeToken, self.cursor.advance()).value)

    def parse_structure(self) -> Structure:
        self.context = "structure"
        self.depth += 1

        if self.check_type(SectionStartToken):
            structure = self.parse_section()
        elif self.check_type(ListStartToken):
            structure = self.parse_list()
        else:
            raise Exception(
                f"Cannot start a structure with token of type: '{type(self.cursor.peek()).__name__}'."
            )

        self.depth -= 1
        return structure

    def parse_section(self) -> Section:
        self.context = "section"
        self.match_type_or_raise(SectionStartToken)

        title = self.parse_string()
        element = self.parse_element()
        return Section(title, element, self.depth)

    def parse_list(self) -> List:
        self.context = "list"
        self.match_type_or_raise(ListStartToken)

        return List(self.parse_grouping())


def parse(tokens: PyList[Token]) -> Document:
    return Parse(tokens).result
