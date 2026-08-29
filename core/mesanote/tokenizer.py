from typing import List

from mesanote.cursors import StrCursor, CursorDepletedError
from mesanote.tokens import (
    DefinitionStartToken,
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
DEFINITION = "@"

SYMBOLS = [*GROUPING, COMMENT, SECTION, LIST, DEFINITION]

EMPHASIS = "*"
ESCAPE = "\\"
CODE = "`"

STRING_SYMBOLS = [EMPHASIS, ESCAPE, CODE]
STRING_TERMINATORS = ["\n", "|"]

ESCAPABLES = [*SYMBOLS, *STRING_SYMBOLS, *STRING_TERMINATORS]


class TokenizationError(Exception):
    pass


def tokenize(text: str) -> List[Token]:
    cursor = StrCursor(text)
    tokens: List[Token] = []

    while not cursor.is_at_end():
        source_pos = cursor.char_pos

        # Skip spaces
        if cursor.peek().isspace():
            cursor.advance()
        # Comments
        elif cursor.match_many(COMMENT):
            while not cursor.is_at_end() and cursor.peek() != "\n":
                cursor.advance()
        # Groupings
        elif cursor.match_many(GROUPING[0]):
            tokens.append(GroupStartToken(source=source_pos))
        elif cursor.match_many(GROUPING[1]):
            tokens.append(GroupEndToken(source=source_pos))
        # Structures
        elif cursor.match_many(SECTION):
            tokens.append(SectionStartToken(source=source_pos))
        elif cursor.match_many(LIST):
            tokens.append(ListStartToken(source=source_pos))
        elif cursor.match_many(DEFINITION):
            tokens.append(DefinitionStartToken(source=source_pos))
        # Strings
        else:
            tokens += tokenize_string(cursor)

    return tokens


def tokenize_string(cursor: StrCursor) -> List[Token]:
    tokens: List[Token] = [StringStartToken(source=cursor.char_pos)]
    current_text: TextToken | None = None

    while not cursor.is_at_end():
        source_pos = cursor.char_pos

        # Terminators
        if cursor.match_any_of(STRING_TERMINATORS) or cursor.check_any_of(SYMBOLS):
            break
        # Escapes
        elif cursor.match_many(ESCAPE):
            if not current_text:
                current_text = TextToken("", source=source_pos)
            current_text.value += get_escaped_text(cursor, source_pos)
        # Emphasis
        elif cursor.match_many(EMPHASIS):
            if current_text:
                tokens.append(current_text)
                current_text = None
            tokens.append(EmphasisToken(source=source_pos))
        # Codeblocks
        elif cursor.match_many(CODE):
            if current_text:
                tokens.append(current_text)
                current_text = None
            tokens += tokenize_code(cursor)
        # Text
        else:
            if not current_text:
                current_text = TextToken(source=source_pos)
            current_text.value += cursor.advance()

    if current_text:
        tokens.append(current_text)
    tokens.append(StringEndToken(source=source_pos))
    return tokens


def get_escaped_text(cursor: StrCursor, source: tuple[int, int]) -> str:
    if not cursor.is_at_end():
        for escapable in ESCAPABLES:
            if cursor.check_many(escapable):
                return cursor.advance_many(len(escapable))

    raise TokenizationError(
        f"Escape at {source} was not followed by an escapable sequence."
    )


def tokenize_code(cursor: StrCursor) -> List[Token]:
    source_pos = cursor.char_pos
    code_symbol_count = 1
    while cursor.match_many(CODE):
        code_symbol_count += 1

    text = ""
    while not cursor.match_many(CODE * code_symbol_count):
        try:
            text += cursor.advance()
        except CursorDepletedError:
            raise TokenizationError(f"Codeblock at {source_pos} was not closed.")

    return [CodeToken(text, source=source_pos)]
