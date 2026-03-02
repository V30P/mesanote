from typing import cast
from mesanote.tokenizer import (
    Token,
    TextToken,
    GroupStartToken,
    GroupEndToken,
    StructureStartToken,
    SectionStartToken,
    ListStartToken,
)
from mesanote.nodes import Document, Element, Text, Grouping, Structure, Section, List


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.document = Document()
        self.depth = 0

        while len(tokens) > 0:
            self.document.contents.append(self._parse_element())

    def _parse_element(self) -> Element:
        if isinstance(self.tokens[0], TextToken):
            token = self.tokens.pop(0)
            return Text(cast(TextToken, token).value)
        elif isinstance(self.tokens[0], GroupStartToken):
            return self._parse_grouping()
        elif isinstance(self.tokens[0], StructureStartToken):
            return self._parse_structure()

        raise Exception()

    def _parse_grouping(self) -> Grouping:
        self.tokens.pop(0)

        contents = []
        while not isinstance(self.tokens[0], GroupEndToken):
            contents.append(self._parse_element())

        self.tokens.pop(0)
        return Grouping(contents)

    def _parse_structure(self) -> Structure:
        structure = None
        self.depth += 1

        if isinstance(self.tokens[0], SectionStartToken):
            structure = self._parse_section()
        elif isinstance(self.tokens[0], ListStartToken):
            structure = self._parse_list()

        if structure is not None:
            self.depth -= 1
            return structure

        raise Exception()

    def _parse_section(self) -> Section:
        self.tokens.pop(0)

        token = self.tokens.pop(0)
        title = cast(TextToken, token).value
        content = self._parse_element()

        return Section(self.depth, title, content)

    def _parse_list(self) -> List:
        self.tokens.pop(0)
        if isinstance(self.tokens[0], TextToken):
            title_token = cast(TextToken, self.tokens.pop(0))
            return List(self.depth, title_token.value, self._parse_grouping())  # type: ignore
        else:
            return List(self.depth, "", self._parse_grouping())


def parse(tokens: list[Token]) -> Document:
    return Parser(tokens).document
