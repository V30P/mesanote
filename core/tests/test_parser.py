import pytest

from mesanote.parser import parse, ParseError
from mesanote.tokens import (
    TextToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)
from mesanote.nodes import (
    Text,
    Grouping,
    Section,
    List,
)


def assert_parse(input, expected):
    assert parse(input).contents == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ([TextToken("Text")], [Text("Text")]),
        ([TextToken("A"), TextToken("B")], [Text("A"), Text("B")]),
    ],
)
def test_text(input, expected):
    assert_parse(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [GroupStartToken(), TextToken("A"), TextToken("B"), GroupEndToken()],
            [Grouping([Text("A"), Text("B")])],
        ),
        (
            [GroupStartToken(), GroupStartToken(), GroupEndToken(), GroupEndToken()],
            [Grouping([Grouping([])])],
        ),
    ],
)
def test_grouping(input, expected):
    assert_parse(input, expected)


def test_grouping_mismatch():
    with pytest.raises(ParseError):
        parse([GroupStartToken()])


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [SectionStartToken(), TextToken("Title"), TextToken("Text")],
            [Section(1, "Title", Text("Text"))],
        )
    ],
)
def test_section(input, expected):
    assert_parse(input, expected)


def test_no_content_section():
    with pytest.raises(ParseError):
        parse([SectionStartToken(), TextToken("Text")])


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                ListStartToken(),
                TextToken("Title"),
                GroupStartToken(),
                TextToken("A"),
                TextToken("B"),
                GroupEndToken(),
            ],
            [List(1, "Title", Grouping([Text("A"), Text("B")]))],
        ),
        (
            [
                ListStartToken(),
                GroupStartToken(),
                TextToken("A"),
                TextToken("B"),
                GroupEndToken(),
            ],
            [List(1, "", Grouping([Text("A"), Text("B")]))],
        ),
    ],
)
def test_list(input, expected):
    assert_parse(input, expected)


def test_no_grouping_list():
    with pytest.raises(ParseError):
        parse([ListStartToken(), TextToken("Title")])


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                SectionStartToken(),
                TextToken("Title"),
                SectionStartToken(),
                TextToken("Title"),
                TextToken("Text"),
            ],
            [Section(1, "Title", Section(2, "Title", Text("Text")))],
        ),
        (
            [
                SectionStartToken(),
                TextToken("Title"),
                TextToken("Text"),
                SectionStartToken(),
                TextToken("Title"),
                TextToken("Text"),
            ],
            [Section(1, "Title", Text("Text")), Section(1, "Title", Text("Text"))],
        ),
    ],
)
def test_depth(input, expected):
    assert_parse(input, expected)


def test_empty():
    assert_parse([], [])


def test_invalid_start():
    with pytest.raises(ParseError):
        parse([GroupEndToken()])
