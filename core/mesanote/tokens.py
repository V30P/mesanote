from dataclasses import dataclass, field


@dataclass()
class Token:
    source: tuple[int, int] | None = field(default=None, kw_only=True, compare=False)
    pass


@dataclass()
class StringStartToken(Token):
    pass


@dataclass()
class StringEndToken(Token):
    pass


@dataclass()
class TextToken(Token):
    value: str = ""


@dataclass()
class EmphasisToken(Token):
    pass


@dataclass()
class CodeToken(Token):
    value: str
    pass


@dataclass()
class GroupStartToken(Token):
    pass


@dataclass()
class GroupEndToken(Token):
    pass


@dataclass()
class StructureStartToken(Token):
    pass


@dataclass()
class SectionStartToken(StructureStartToken):
    pass


@dataclass()
class ListStartToken(StructureStartToken):
    pass

@dataclass()
class DefinitionStartToken(StructureStartToken):
    pass

@dataclass()
class TableStartToken(StructureStartToken):
    pass
