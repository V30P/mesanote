import pytest

from mesanote.nodes import (
    Document,
    Grouping,
    Section,
    List,
    Emphasis,
    StrongEmphasis,
    Text,
)

from tests.utils import string_of


def assert_render(input, expected):
    assert input.render() == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            Document([string_of("A"), string_of("B")]),
            "<p>A</p><p>B</p>",
        ),
        (
            Document(
                [
                    string_of("A"),
                    Grouping([string_of("B")]),
                    Section(string_of("Title"), string_of("C"), 1),
                ]
            ),
            "<p>A</p><p>B</p><h1>Title</h1><p>C</p>",
        ),
    ],
)
def test_document(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize("input, expected", [(string_of("Text"), "<p>Text</p>")])
def test_text(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            Grouping([string_of("A"), string_of("B")]),
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
        (
            Section(string_of("Title"), string_of("Text"), 1),
            "<h1>Title</h1><p>Text</p>",
        ),
        (
            Section(string_of("Title"), string_of("Text"), 2),
            "<h2>Title</h2><p>Text</p>",
        ),
    ],
)
def test_section(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            List(Grouping([string_of("A"), string_of("B")])),
            "<ul><li><p>A</p></li><li><p>B</p></li></ul>",
        ),
        (
            List(Grouping([])),
            "<ul></ul>",
        ),
    ],
)
def test_list(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            List(Grouping([Section(string_of("Title"), Grouping([]), 2)])),
            "<ul><li><h2>Title</h2></li></ul>",
        ),
        (
            Section(string_of("Title"), List(Grouping([])), 1),
            "<h1>Title</h1><ul></ul>",
        ),
    ],
)
def test_nested(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (Emphasis(Text("Italics")), "<em>Italics</em>"),
        (StrongEmphasis(Text("Bold")), "<strong>Bold</strong>"),
        (
            StrongEmphasis(Emphasis(Text("Bold and italics"))),
            "<strong><em>Bold and italics</em></strong>",
        ),
    ],
)
def test_emphasis(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (string_of("A<B"), "<p>A&lt;B</p>"),
        (string_of("A>B"), "<p>A&gt;B</p>"),
        (string_of("A&B"), "<p>A&amp;B</p>"),
        (string_of('A"B'), "<p>A&quot;B</p>"),
        (string_of("A'B"), "<p>A&#x27;B</p>"),
        (Emphasis(Text("A<B")), "<em>A&lt;B</em>"),
    ],
)
def test_html_escaping(input, expected):
    assert_render(input, expected)

