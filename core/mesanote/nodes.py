from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List as PyList
import html


@dataclass()
class Node(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


@dataclass()
class Document(Node):
    elements: PyList[Element]

    def render(self) -> str:
        return "".join(element.render() for element in self.elements)


@dataclass()
class Element(Node):
    def render(self) -> str:
        return ""


@dataclass()
class Grouping(Element):
    elements: PyList[Element]

    def render(self) -> str:
        return "".join(element.render() for element in self.elements)


# region String nodes
@dataclass()
class String(Element):
    substrings: list[Substring]

    def render(self) -> str:
        return f"<p>{self.render_substrings()}</p>"

    def render_substrings(self) -> str:
        return "".join(element.render() for element in self.substrings)


@dataclass()
class Substring(Node):
    pass


@dataclass()
class Text(Substring):
    value: str

    def render(self) -> str:
        return html.escape(self.value)


@dataclass()
class Emphasis(Substring):
    substring: Substring

    def render(self) -> str:
        return f"<em>{self.substring.render()}</em>"


@dataclass()
class StrongEmphasis(Emphasis):
    substring: Substring

    def render(self) -> str:
        return f"<strong>{self.substring.render()}</strong>"


# endregion


# region Structure nodes
@dataclass()
class Structure(Element): ...


@dataclass()
class Section(Structure):
    title: String
    element: Element
    depth: int

    def render(self) -> str:
        return f"<h{self.depth}>{self.title.render_substrings()}</h{self.depth}>{self.element.render()}"


@dataclass()
class List(Structure):
    grouping: Grouping

    def render(self) -> str:
        return f"<ul>{''.join(f'<li>{element.render()}</li>' for element in self.grouping.elements)}</ul>"


# endregion
