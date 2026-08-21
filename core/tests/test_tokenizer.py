import pytest

from mesanote.cursor import CursorError
from mesanote.tokenizer import tokenize, TokenizationError
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


def assert_tokenize(input, expected):
    assert tokenize(input) == expected


@pytest.mark.parametrize("input", ["", " "])
def test_empty(input):
    assert_tokenize(input, [])


def test_delimiter():
    assert tokenize("A\nB") == tokenize("A|B")


@pytest.mark.parametrize(
    "input, expected",
    [
        ("Text", [StringStartToken(), TextToken("Text"), StringEndToken()]),
        (
            "Text\nText",
            [
                StringStartToken(),
                TextToken("Text"),
                StringEndToken(),
                StringStartToken(),
                TextToken("Text"),
                StringEndToken(),
            ],
        ),
    ],
)
def test_text(input, expected):
    assert_tokenize(input, expected)


def test_escape():
    assert_tokenize("\\|", [StringStartToken(), TextToken("|"), StringEndToken()])


def test_invalid_escape():
    with pytest.raises(TokenizationError):
        tokenize("\\A")


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "**",
            [StringStartToken(), EmphasisToken(), EmphasisToken(), StringEndToken()],
        ),
        (
            "*Italics*Text",
            [
                StringStartToken(),
                EmphasisToken(),
                TextToken("Italics"),
                EmphasisToken(),
                TextToken("Text"),
                StringEndToken(),
            ],
        ),
    ],
)
def test_emphasis(input, expected):
    assert_tokenize(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "`Code`",
            [
                StringStartToken(),
                CodeToken("Code"),
                StringEndToken(),
            ],
        ),
        (
            "`````Code`````",
            [
                StringStartToken(),
                CodeToken("Code"),
                StringEndToken(),
            ],
        ),
        (
            "Text`Code`Text",
            [
                StringStartToken(),
                TextToken("Text"),
                CodeToken("Code"),
                TextToken("Text"),
                StringEndToken(),
            ],
        ),
        (
            "`\nCode\n`",
            [
                StringStartToken(),
                CodeToken("\nCode\n"),
                StringEndToken(),
            ],
        ),
    ],
)
def test_codeblock(input, expected):
    assert_tokenize(input, expected)


@pytest.mark.parametrize("input", ["``", "` ``", "`` `"])
def test_mismatched_codeblock(input):
    with pytest.raises(CursorError):
        tokenize(input)


def test_grouping():
    assert_tokenize("{}", [GroupStartToken(), GroupEndToken()])


@pytest.mark.parametrize(
    "input, expected",
    [
        ("{", [GroupStartToken()]),
        ("}", [GroupEndToken()]),
        (">", [SectionStartToken()]),
        ("+", [ListStartToken()]),
    ],
)
def test_structure_symbols(input, expected):
    assert_tokenize(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "> Title { Text }",
            [
                SectionStartToken(),
                StringStartToken(),
                TextToken("Title"),
                StringEndToken(),
                GroupStartToken(),
                StringStartToken(),
                TextToken("Text"),
                StringEndToken(),
                GroupEndToken(),
            ],
        ),
        (
            "+ Title { A | B }",
            [
                ListStartToken(),
                StringStartToken(),
                TextToken("Title"),
                StringEndToken(),
                GroupStartToken(),
                StringStartToken(),
                TextToken("A"),
                StringEndToken(),
                StringStartToken(),
                TextToken("B"),
                StringEndToken(),
                GroupEndToken(),
            ],
        ),
    ],
)
def test_full_structure(input, expected):
    assert_tokenize(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("// Comment", []),
        ("Text // Comment", [StringStartToken(), TextToken("Text"), StringEndToken()]),
        ("// Comment | Comment", []),
        (
            "// Comment \n Text",
            [StringStartToken(), TextToken("Text"), StringEndToken()],
        ),
    ],
)
def test_comment(input, expected):
    assert_tokenize(input, expected)
