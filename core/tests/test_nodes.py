import pytest

from mesanote.nodes import (
    Document,
    String,
    Text,
    Emphasis,
    StrongEmphasis,
    Code,
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
            Document([String([Text("A")]), String([Text("B")])]),
            "<p>A</p><p>B</p>",
        ),
        (
            Document(
                [
                    String([Text("A")]),
                    Grouping([String([Text("B")])]),
                    Section(String([Text("Title")]), String([Text("C")]), 1),
                ]
            ),
            "<p>A</p><p>B</p><h1>Title</h1><p>C</p>",
        ),
    ],
)
def test_document(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (String([Text("Text")]), "<p>Text</p>"),
        (String([Text("A<B")]), "<p>A&lt;B</p>"),
        (String([Text("A&B")]), "<p>A&amp;B</p>"),
    ],
)
def test_text(input, expected):
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
        (String([Code("Code")]), "<p><code>Code</code></p>"),
        (
            String([Text("Normal"), Code("Code"), Text("Normal")]),
            "<p>Normal<code>Code</code>Normal</p>",
        ),
        (
            String([Code("Code\nCode")]),
            "<p><code><pre>Code\nCode</pre></code></p>",
        ),
        (
            String([Code("\nCode\n")]),
            "<p><code><pre>Code</pre></code></p>",
        ),
        (
            String([Code("\n\nCode\n\n")]),
            "<p><code><pre>\nCode\n</pre></code></p>",
        ),
        (
            String([Code("\tCode\n\t\tCode")]),
            "<p><code><pre>Code\n\tCode</pre></code></p>",
        ),
        (String([Code("A<B")]), "<p><code>A&lt;B</code></p>"),
        (String([Code("A&B")]), "<p><code>A&amp;B</code></p>"),
    ],
)
def test_code(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            Grouping([String([Text("A")]), String([Text("B")])]),
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
            Section(String([Text("Title")]), String([Text("Text")]), 1),
            "<h1>Title</h1><p>Text</p>",
        ),
        (
            Section(String([Text("Title")]), String([Text("Text")]), 2),
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
            List(Grouping([String([Text("A")]), String([Text("B")])])),
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
            List(Grouping([Section(String([Text("Title")]), Grouping([]), 2)])),
            "<ul><li><h2>Title</h2></li></ul>",
        ),
        (
            Section(String([Text("Title")]), List(Grouping([])), 1),
            "<h1>Title</h1><ul></ul>",
        ),
    ],
)
def test_nested(input, expected):
    assert_render(input, expected)
