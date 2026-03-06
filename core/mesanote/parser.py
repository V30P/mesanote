from typing import cast

from mesanote.tokens import (
    Token,
    TextToken,
    GroupStartToken,
    GroupEndToken,
    StructureStartToken,
    SectionStartToken,
    ListStartToken,
)
from mesanote.nodes import (
    Document,
    Element,
    Text,
    Grouping,
    Structure,
    Section,
    List,
)


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._token = tokens[0] if len(self._tokens) > 0 else None
        self._depth = 0

        self.document = self._parse_document()

    def pop(self) -> Token:
        popped = self._tokens.pop(0)
        self._token = self._tokens[0] if len(self._tokens) > 0 else None

        return popped

    # Recursive descent parser implementation
    def _parse_document(self) -> Document:
        content = []
        while self._token is not None:
            content.append(self._parse_element())

        return Document(content)

    def _parse_element(self) -> Element:
        if isinstance(self._token, TextToken):
            return self._parse_text()
        elif isinstance(self._token, GroupStartToken):
            return self._parse_grouping()
        elif isinstance(self._token, StructureStartToken):
            return self._parse_structure()

        raise ParseError(
            f"Cannot start an element with token of type: '{self._token.__class__.__name__}'."
        )

    def _parse_text(self) -> Text:
        return Text(cast(TextToken, self.pop()).value)

    def _parse_grouping(self) -> Grouping:
        self.pop()

        contents = []
        while not isinstance(self._token, GroupEndToken):
            contents.append(self._parse_element())

        self.pop()
        return Grouping(contents)

    def _parse_structure(self) -> Structure:
        # Increment depth when entering a structure
        self._depth += 1
        structure = None

        if isinstance(self._token, SectionStartToken):
            structure = self._parse_section()
        elif isinstance(self._token, ListStartToken):
            structure = self._parse_list()

        # Decrement depth when exiting a structure
        self._depth -= 1
        return cast(Structure, structure)

    def _parse_section(self) -> Section:
        self.pop()

        title = self._parse_text().value
        content = self._parse_element()

        return Section(self._depth, title, content)

    def _parse_list(self) -> List:
        self.pop()

        # Handle optional list titles
        title = self._parse_text().value if isinstance(self._token, TextToken) else ""

        if not isinstance(self._token, GroupStartToken):
            raise ParseError("List must be followed by a grouping.")

        return List(self._depth, title, self._parse_grouping())


def parse(tokens: list[Token]) -> Document:
    return Parser(tokens).document
