import pytest
from itertools import repeat

from mesanote.parser import parse, ParseError
from mesanote.tokens import (
    StringStartToken,
    StringEndToken,
    EmphasisToken,
    TextToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)
from mesanote.nodes import (
    Grouping,
    Section,
    List,
    String,
    Emphasis,
    StrongEmphasis,
    Text,
)
from tests.utils import tokens_of, string_of


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
            [*tokens_of("Text")],
            [string_of("Text")],
        ),
        (
            [*tokens_of("A"), *tokens_of("B")],
            [string_of("A"), string_of("B")],
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
                GroupStartToken(),
                *tokens_of("A"),
                *tokens_of("B"),
                GroupEndToken(),
            ],
            [Grouping([string_of("A"), string_of("B")])],
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
            [SectionStartToken(), *tokens_of("Title"), *tokens_of("Text")],
            [Section(string_of("Title"), string_of("Text"), 1)],
        ),
        (
            [
                SectionStartToken(),
                StringStartToken(),
                EmphasisToken(),
                TextToken("Title"),
                EmphasisToken(),
                StringEndToken(),
                *tokens_of("Content"),
            ],
            [
                Section(
                    String([Emphasis(Text("Title"))]),
                    string_of("Content"),
                    1,
                )
            ],
        ),
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
                GroupStartToken(),
                *tokens_of("A"),
                *tokens_of("B"),
                GroupEndToken(),
            ],
            [List(Grouping([string_of("A"), string_of("B")]))],
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
                *tokens_of("Title"),
                SectionStartToken(),
                *tokens_of("Title"),
                *tokens_of("Text"),
            ],
            [
                Section(
                    string_of("Title"),
                    Section(string_of("Title"), string_of("Text"), 2),
                    1
                )
            ],
        ),
        (
            [
                SectionStartToken(),
                *tokens_of("Title"),
                *tokens_of("Text"),
                SectionStartToken(),
                *tokens_of("Title"),
                *tokens_of("Text"),
            ],
            [
                Section(string_of("Title"), string_of("Text"), 1),
                Section(string_of("Title"), string_of("Text"), 1),
            ],
        ),
    ],
)
def test_depth(input, expected):
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
