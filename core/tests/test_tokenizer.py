import pytest

from mesanote.tokenizer import tokenize, TokenizationError
from mesanote.tokens import (
    TextToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)


def assert_tokenize(input, expected):
    assert tokenize(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("Text", [TextToken("Text")]),
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
        ("Text // Comment", [TextToken("Text")]),
        ("// Comment | Comment", []),
        ("// Comment \n Text", [TextToken("Text")]),
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
                TextToken("Title"),
                GroupStartToken(),
                TextToken("Text"),
                GroupEndToken(),
            ],
        ),
        (
            "+ Title { Text | Text }",
            [
                ListStartToken(),
                TextToken("Title"),
                GroupStartToken(),
                TextToken("Text"),
                TextToken("Text"),
                GroupEndToken(),
            ],
        ),
    ],
)
def test_mixed(input, expected):
    assert_tokenize(input, expected)


@pytest.mark.parametrize("input", ["", " ", "|", " | ", "||"])
def test_empty(input):
    assert_tokenize(input, [])


def test_escape():
    assert_tokenize("\\|", [TextToken("|")])


def test_invalid_escape():
    with pytest.raises(TokenizationError):
        tokenize("\\A")
