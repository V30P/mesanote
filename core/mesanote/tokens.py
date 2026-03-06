from dataclasses import dataclass


@dataclass(eq=True)
class Token:
    pass


@dataclass(eq=True)
class TextToken(Token):
    value: str 


@dataclass(eq=True)
class GroupStartToken(Token):
    pass


@dataclass(eq=True)
class GroupEndToken(Token):
    pass


@dataclass(eq=True)
class StructureStartToken(Token):
    pass


@dataclass(eq=True)
class SectionStartToken(StructureStartToken):
    pass


@dataclass(eq=True)
class ListStartToken(StructureStartToken):
    pass