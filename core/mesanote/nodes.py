from abc import ABC, abstractmethod


class Node(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class Document(Node):
    def __init__(self):
        super().__init__()
        self.contents = []

    def render(self) -> str:
        render = ""
        for element in self.contents:
            render += element.render()

        return render


class Element(Node):
    def render(self) -> str:
        return ""


class Text(Element):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def render(self) -> str:
        return f"<p>{self.value}</p>"


class Grouping(Element):
    def __init__(self, contents: list[Element]):
        super().__init__()
        self.contents = contents

    def render(self) -> str:
        render = ""
        for element in self.contents:
            render += element.render()

        return render


class Structure(Element):
    def __init__(self, depth: int) -> None:
        super().__init__()
        self.depth = depth


class Section(Structure):
    def __init__(self, depth: int, title: str, content: Element):
        super().__init__(depth)
        self.title = title
        self.content = content

    def render(self) -> str:
        return f"<h{self.depth}>{self.title}</h{self.depth}>{self.content.render()}"


class List(Structure):
    def __init__(self, depth: int, title: str, grouping: Grouping):
        super().__init__(depth)
        self.title = title
        self.grouping = grouping

    def render(self) -> str:
        render = (
            f"<h{self.depth}>{self.title}</h{self.depth}>" if self.title != "" else ""
        )

        render += "<ul>"
        for element in self.grouping.contents:
            render += f"<li>{element.render()}</li>"

        return render + "</ul>"
