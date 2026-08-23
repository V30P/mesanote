from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List as PyList
import html
import textwrap


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
class String(Element):
    substrings: list[Substring]

    def render(self) -> str:
        return f"<p>{"".join(element.render() for element in self.substrings).rstrip()}</p>"

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


@dataclass()
class Code(Substring):
    value: str

    def render(self):
        value = html.escape(self.value)
        if "\n" in value:
            value = (
                "<pre>"
                + textwrap.dedent(value.removeprefix("\n").removesuffix("\n"))
                + "</pre>"
            )

        return "<code>" + value + "</code>"


@dataclass()
class Grouping(Element):
    elements: PyList[Element]

    def render(self) -> str:
        return "".join(element.render() for element in self.elements)


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
