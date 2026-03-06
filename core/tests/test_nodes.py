import pytest

from mesanote.nodes import (
    Document,
    Text,
    Grouping,
    Section,
    List,
)


def assert_render(input, expected):
    assert input.render() == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            Document([Text("A"), Text("B")]),
            "<p>A</p><p>B</p>",
        ),
        (
            Document(
                [Text("A"), Grouping([Text("B")]), Section(1, "Title", Text("C"))]
            ),
            "<p>A</p><p>B</p><h1>Title</h1><p>C</p>",
        ),
    ],
)
def test_document(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize("input, expected", [(Text("Text"), "<p>Text</p>")])
def test_text(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            Grouping([Text("A"), Text("B")]),
            "<p>A</p><p>B</p>",
        ),
        (Grouping([]), ""),
    ],
)
def test_grouping(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (Section(1, "Title", Text("Text")), "<h1>Title</h1><p>Text</p>"),
        (Section(2, "Title", Text("Text")), "<h2>Title</h2><p>Text</p>"),
    ],
)
def test_section(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            List(1, "Title", Grouping([Text("A"), Text("B")])),
            "<h1>Title</h1><ul><li><p>A</p></li><li><p>B</p></li></ul>",
        ),
        (
            List(1, "", Grouping([Text("A"), Text("B")])),
            "<ul><li><p>A</p></li><li><p>B</p></li></ul>",
        ),
        (
            List(2, "Title", Grouping([])),
            "<h2>Title</h2><ul></ul>",
        ),
    ],
)
def test_list(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            List(1, "", Grouping([Section(2, "Title", Grouping([]))])),
            "<ul><li><h2>Title</h2></li></ul>",
        ),
        (
            Section(1, "Title", List(2, "", Grouping([]))),
            "<h1>Title</h1><ul></ul>",
        ),
    ],
)
def test_nested(input, expected):
    assert_render(input, expected)
