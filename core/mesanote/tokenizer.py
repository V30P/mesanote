from typing import List

from mesanote.cursor import Cursor
from mesanote.tokens import (
    Token,
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

COMMENT = "//"
GROUPING = ("{", "}")
SECTION = ">"
LIST = "+"

BASE_SYMBOLS = [*GROUPING, COMMENT, SECTION, LIST]

EMPHASIS = "*"
ESCAPE = "\\"
CODE = "`"

STRING_SYMBOLS = [EMPHASIS, ESCAPE, CODE]

STRING_TERMINATORS = ["\n", "|"]
ESCAPABLES = [*BASE_SYMBOLS, *STRING_SYMBOLS, *STRING_TERMINATORS]


class TokenizationError(Exception):
    pass


# TODO: Add catching and formatting other errors as TokenizationErrors
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
            text += get_escaped_text(cursor)
        # Emphasis
        elif cursor.match_many(EMPHASIS):
            if text:
                tokens.append(TextToken(text))
                text = ""
            tokens.append(EmphasisToken())
        # Codeblocks
        elif cursor.match_many(CODE):
            if text:
                tokens.append(TextToken(text))
                text = ""
            tokens += tokenize_code(cursor)
        # Text
        else:
            text += cursor.advance()

    if text:
        tokens.append(TextToken(text.rstrip()))
    tokens.append(StringEndToken())
    return tokens


def get_escaped_text(cursor: Cursor[str]) -> str:
    if cursor.is_at_end():
        raise TokenizationError("Must provide a character to escape.")

    for escapable in ESCAPABLES:
        if cursor.check_many(escapable):
            return cursor.advance_many(len(escapable))

    raise TokenizationError("Escape is not followed by an escapable sequence.")


def tokenize_code(cursor: Cursor[str]) -> List[Token]:
    code_symbol_count = 1
    while cursor.match_many(CODE):
        code_symbol_count += 1

    text = ""
    while not cursor.match_many(CODE * code_symbol_count):
        text += cursor.advance()

    return [CodeToken(text)]
