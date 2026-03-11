import pytest

from mesanote.tokenizer import tokenize, TokenizationError
from mesanote.tokens import (
    StringStartToken,
    StringEndToken,
    TextToken,
    EmphasisToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)
from tests.utils import tokens_of


def assert_tokenize(input, expected):
    assert tokenize(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("Text", [StringStartToken(), TextToken("Text"), StringEndToken()]),
        ("{}", [GroupStartToken(), GroupEndToken()]),
        (">", [SectionStartToken()]),
        ("+", [ListStartToken()]),
    ],
)
def test_single_symbol(input, expected):
    assert_tokenize(input, expected)


def test_delimiter():
    assert tokenize("A\nB") == tokenize("A|B")


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
def test_comments(input, expected):
    assert_tokenize(input, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "> Title { Text }",
            [
                SectionStartToken(),
                *tokens_of("Title"),
                GroupStartToken(),
                *tokens_of("Text"),
                GroupEndToken(),
            ],
        ),
        (
            "+ Title { A | B }",
            [
                ListStartToken(),
                *tokens_of("Title"),
                GroupStartToken(),
                *tokens_of("A"),
                *tokens_of("B"),
                GroupEndToken(),
            ],
        ),
    ],
)
def test_mixed(input, expected):
    assert_tokenize(input, expected)


@pytest.mark.parametrize("input", ["", " "])
def test_empty(input):
    assert_tokenize(input, [])


def test_escape():
    assert_tokenize("\\|", [*tokens_of("|")])


def test_invalid_escape():
    with pytest.raises(TokenizationError):
        tokenize("\\A")


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "*",
            [StringStartToken(), EmphasisToken(), StringEndToken()],
        ),
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
