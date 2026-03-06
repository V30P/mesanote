from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List as TypingList


@dataclass(eq=True)
class Node(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


@dataclass(eq=True)
class Document(Node):
    contents: TypingList[Node]

    def render(self) -> str:
        return "".join(element.render() for element in self.contents)


@dataclass(eq=True)
class Element(Node):
    def render(self) -> str:
        return ""


@dataclass(eq=True)
class Text(Element):
    value: str

    def render(self) -> str:
        return f"<p>{self.value}</p>"


@dataclass(eq=True)
class Grouping(Element):
    contents: TypingList[Element]

    def render(self) -> str:
        return "".join(element.render() for element in self.contents)


@dataclass(eq=True)
class Structure(Element):
    depth: int


@dataclass(eq=True)
class Section(Structure):
    title: str
    content: Element

    def render(self) -> str:
        return f"<h{self.depth}>{self.title}</h{self.depth}>{self.content.render()}"


@dataclass(eq=True)
class List(Structure):
    title: str
    grouping: Grouping

    def render(self) -> str:
        header = f"<h{self.depth}>{self.title}</h{self.depth}>" if self.title else ""
        items = "".join(
            f"<li>{element.render()}</li>" for element in self.grouping.contents
        )
        return f"{header}<ul>{items}</ul>"
