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
    Definitions,
    Table,
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
            "<p></p><pre><code>Code\nCode</code></pre><p></p>",
        ),
        (
            String([Code("\nCode\n")]),
            "<p></p><pre><code>Code</code></pre><p></p>",
        ),
        (
            String([Code("\n\nCode\n\n")]),
            "<p></p><pre><code>\nCode\n</code></pre><p></p>",
        ),
        (
            String([Code("\tCode\n\t\tCode")]),
            "<p></p><pre><code>Code\n\tCode</code></pre><p></p>",
        ),
        (
            String([Text("Normal"), Code("\nCode\n"), Text("Normal")]),
            "<p>Normal</p><pre><code>Code</code></pre><p>Normal</p>",
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
            Definitions([(String([Text("Term")]), String([Text("Definition")]))]),
            "<dl><dt>Term</dt><dd>Definition</dd></dl>",
        ),
        (
            Definitions(
                [
                    (String([Text("A")]), String([Text("1")])),
                    (String([Text("B")]), String([Text("2")])),
                    (String([Text("C")]), String([Text("3")])),
                ]
            ),
            "<dl><dt>A</dt><dd>1</dd><dt>B</dt><dd>2</dd><dt>C</dt><dd>3</dd></dl>",
        ),
    ],
)
def test_definitions(input, expected):
    assert_render(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (Table([[String([Text("A")])]]), "<table><tr><td><p>A</p></td></tr></table>"),
        (
            Table(
                [
                    [String([Text("A1")]), String([Text("B1")])],
                    [String([Text("A2")]), String([Text("B2")])],
                ]
            ),
            "<table><tr><td><p>A1</p></td><td><p>B1</p></td></tr><tr><td><p>A2</p></td><td><p>B2</p></td></tr></table>",
        ),
        (
            Table(
                [
                    [String([Text("A1")])],
                    [String([Text("A2")]), String([Text("B2")])],
                ]
            ),
            "<table><tr><td><p>A1</p></td></tr><tr><td><p>A2</p></td><td><p>B2</p></td></tr></table>",
        ),
    ],
)
def test_table(input, expected):
    assert_render(input, expected)


# TODO: Add some end-to-end integration tests somewhere
