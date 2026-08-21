import pytest
from itertools import repeat

from mesanote.parser import parse, ParseError
from mesanote.tokens import (
    StringStartToken,
    StringEndToken,
    TextToken,
    EmphasisToken,
    CodeToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)
from mesanote.nodes import (
    String,
    Text,
    Emphasis,
    StrongEmphasis,
    Code,
    Grouping,
    Section,
    List,
)


def assert_parse(input, expected):
    assert parse(input).elements == expected


def test_empty():
    assert_parse([], [])


def test_invalid_start():
    with pytest.raises(ParseError):
        parse([GroupEndToken()])


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [StringStartToken(), TextToken("Text"), StringEndToken()],
            [String([Text("Text")])],
        ),
        (
            [
                StringStartToken(),
                TextToken("A"),
                StringEndToken(),
                StringStartToken(),
                TextToken("B"),
                StringEndToken(),
            ],
            [String([Text("A")]), String([Text("B")])],
        ),
    ],
)
def test_text(input, expected):
    assert_parse(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                StringStartToken(),
                EmphasisToken(),
                TextToken("Italics"),
                EmphasisToken(),
                StringEndToken(),
            ],
            [String([Emphasis(Text("Italics"))])],
        ),
        (
            [
                StringStartToken(),
                *repeat(EmphasisToken(), 2),
                TextToken("Bold"),
                *repeat(EmphasisToken(), 2),
                StringEndToken(),
            ],
            [String([StrongEmphasis(Text("Bold"))])],
        ),
        (
            [
                StringStartToken(),
                *repeat(EmphasisToken(), 3),
                TextToken("Bold and italics"),
                *repeat(EmphasisToken(), 3),
                StringEndToken(),
            ],
            [String([StrongEmphasis(Emphasis(Text("Bold and italics")))])],
        ),
        (
            [
                StringStartToken(),
                *repeat(EmphasisToken(), 4),
                TextToken("Just bold"),
                *repeat(EmphasisToken(), 4),
                StringEndToken(),
            ],
            [String([StrongEmphasis(StrongEmphasis(Text("Just bold")))])],
        ),
        (
            [
                StringStartToken(),
                EmphasisToken(),
                TextToken("Bold"),
                EmphasisToken(),
                TextToken("Normal"),
                StringEndToken(),
            ],
            [String([Emphasis(Text("Bold")), Text("Normal")])],
        ),
        (
            [
                StringStartToken(),
                TextToken("Normal"),
                EmphasisToken(),
                TextToken("Bold"),
                EmphasisToken(),
                StringEndToken(),
            ],
            [String([Text("Normal"), Emphasis(Text("Bold"))])],
        ),
    ],
)
def test_emphasis(input, expected):
    assert_parse(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [StringStartToken(), CodeToken("Code"), StringEndToken()],
            [String([Code("Code")])],
        ),
        (
            [
                StringStartToken(),
                TextToken("Normal"),
                CodeToken("Code"),
                TextToken("Normal"),
                StringEndToken(),
            ],
            [String([Text("Normal"), Code("Code"), Text("Normal")])],
        ),
    ],
)
def test_codeblock(input, expected):
    assert_parse(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                GroupStartToken(),
                StringStartToken(),
                TextToken("A"),
                StringEndToken(),
                StringStartToken(),
                TextToken("B"),
                StringEndToken(),
                GroupEndToken(),
            ],
            [Grouping([String([Text("A")]), String([Text("B")])])],
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
            [
                SectionStartToken(),
                StringStartToken(),
                TextToken("Title"),
                StringEndToken(),
                StringStartToken(),
                TextToken("Text"),
                StringEndToken(),
            ],
            [Section(String([Text("Title")]), String([Text("Text")]), 1)],
        ),
        (
            [
                SectionStartToken(),
                StringStartToken(),
                EmphasisToken(),
                TextToken("Title"),
                EmphasisToken(),
                StringEndToken(),
                StringStartToken(),
                TextToken("Content"),
                StringEndToken(),
            ],
            [
                Section(
                    String([Emphasis(Text("Title"))]),
                    String([Text("Content")]),
                    1,
                )
            ],
        ),
        (
            [
                SectionStartToken(),
                StringStartToken(),
                TextToken("Title"),
                StringEndToken(),
                SectionStartToken(),
                StringStartToken(),
                TextToken("Title"),
                StringEndToken(),
                StringStartToken(),
                TextToken("Text"),
                StringEndToken(),
            ],
            [
                Section(
                    String([Text("Title")]),
                    Section(String([Text("Title")]), String([Text("Text")]), 2),
                    1,
                )
            ],
        ),
        (
            [
                SectionStartToken(),
                StringStartToken(),
                TextToken("Title"),
                StringEndToken(),
                StringStartToken(),
                TextToken("Text"),
                StringEndToken(),
                SectionStartToken(),
                StringStartToken(),
                TextToken("Title"),
                StringEndToken(),
                StringStartToken(),
                TextToken("Text"),
                StringEndToken(),
            ],
            [
                Section(String([Text("Title")]), String([Text("Text")]), 1),
                Section(String([Text("Title")]), String([Text("Text")]), 1),
            ],
        ),
    ],
)
def test_section(input, expected):
    assert_parse(input, expected)


def test_no_title_section():
    with pytest.raises(ParseError):
        parse([SectionStartToken(), GroupStartToken(), GroupEndToken()])


def test_no_content_section():
    with pytest.raises(ParseError):
        parse([SectionStartToken(), TextToken("Text")])


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                ListStartToken(),
                GroupStartToken(),
                StringStartToken(),
                TextToken("A"),
                StringEndToken(),
                StringStartToken(),
                TextToken("B"),
                StringEndToken(),
                GroupEndToken(),
            ],
            [List(Grouping([String([Text("A")]), String([Text("B")])]))],
        ),
    ],
)
def test_list(input, expected):
    assert_parse(input, expected)


def test_no_grouping_list():
    with pytest.raises(ParseError):
        parse([ListStartToken(), TextToken("Title")])
