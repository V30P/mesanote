from dataclasses import dataclass


@dataclass()
class Token:
    pass

@dataclass()
class StringStartToken(Token):
    pass

@dataclass()
class StringEndToken(Token):
    pass

@dataclass()
class TextToken(Token):
    value: str 

@dataclass()
class EmphasisToken(Token):
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

    