class Token:
    pass


class TextToken(Token):
    def __init__(self, value: str) -> None:
        self.value = value


class GroupStartToken(Token):
    pass


class GroupEndToken(Token):
    pass


class StructureStartToken(Token):
    pass


class SectionStartToken(StructureStartToken):
    pass


class ListStartToken(StructureStartToken):
    pass
