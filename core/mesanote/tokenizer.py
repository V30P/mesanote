from typing import List

from mesanote.cursor import Cursor
from mesanote.tokens import (
    Token,
    StringStartToken,
    StringEndToken,
    TextToken,
    EmphasisToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)

# region Base symbols
COMMENT = "//"
GROUPING = ("{", "}")
SECTION = ">"
LIST = "+"

BASE_SYMBOLS = [*GROUPING, COMMENT, SECTION, LIST]
# endregion

# region String symbols
EMPHASIS = "*"
ESCAPE = "\\"

STRING_SYMBOLS = [EMPHASIS, ESCAPE]

STRING_TERMINATORS = ["\n", "|"]
ESCAPABLES = [s[0] for s in [*BASE_SYMBOLS, *STRING_SYMBOLS, *STRING_TERMINATORS]]
# endregion


class TokenizationError(Exception):
    pass


def tokenize(text: str) -> List[Token]:
    cursor = Cursor(text)
    tokens: List[Token] = []

    while not cursor.is_at_end():
        # Skip spaces
        if cursor.peek().isspace():
            cursor.advance()
        # Comments
        elif cursor.match_many(COMMENT):
            while not cursor.is_at_end() and cursor.peek() != "\n":
                cursor.advance()
        # Grouping
        elif cursor.match_many(GROUPING[0]):
            tokens.append(GroupStartToken())
        elif cursor.match_many(GROUPING[1]):
            tokens.append(GroupEndToken())
        # Structure
        elif cursor.match_many(SECTION):
            tokens.append(SectionStartToken())
        elif cursor.match_many(LIST):
            tokens.append(ListStartToken())
        # Strings
        else:
            tokens += tokenize_string(cursor)

    return tokens


def tokenize_string(cursor: Cursor[str]) -> List[Token]:
    tokens: List[Token] = [StringStartToken()]
    text = ""

    while not cursor.is_at_end():
        # Terminators
        if cursor.match_any_of(STRING_TERMINATORS) or cursor.check_any_of(BASE_SYMBOLS):
            break
        # Escape
        elif cursor.match_many(ESCAPE):
            if cursor.is_at_end():
                raise TokenizationError("Must provide a character to escape.")
            escaped_char = cursor.peek()
            if escaped_char not in ESCAPABLES:
                raise TokenizationError(f"Character {escaped_char} is not escapable.")
            text += cursor.advance()
        # Emphasis
        elif cursor.match_many(EMPHASIS):
            if text:
                tokens.append(TextToken(text))
                text = ""
            tokens.append(EmphasisToken())
        # Text
        else:
            text += cursor.advance()

    if text:
        tokens.append(TextToken(text.rstrip()))
    tokens.append(StringEndToken())
    return tokens
