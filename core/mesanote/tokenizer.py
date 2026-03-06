from mesanote.tokens import (
    Token,
    TextToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)

DELIMITER = "|"
SYMBOLS = {
    "{": GroupStartToken,
    "}": GroupEndToken,
    ">": SectionStartToken,
    "+": ListStartToken,
}


class TokenizationError(Exception):
    pass


def tokenize(text: str) -> list[Token]:
    tokens = []
    accumulated_text = ""

    # Create a text token from the characters that haven't been tokenized
    # Will skip creating a token if it would be empty
    def tokenize_accumulation() -> None:
        nonlocal accumulated_text
        accumulated_text = accumulated_text.strip()

        if accumulated_text != "":
            tokens.append(TextToken(accumulated_text))
            accumulated_text = ""

    # Begin a new chunk, resetting chunk-based state
    def start_chunk() -> None:
        nonlocal commenting, escaping

        tokenize_accumulation()
        commenting = escaping = False

    commenting = escaping = False
    for char in text:
        # Escape the character
        if escaping:
            if char in [DELIMITER, *SYMBOLS.keys()]:
                accumulated_text += char
                escaping = False
            else:
                raise TokenizationError(f"Cannot escape character: '{char}'")
        # Start a chunk via newline
        elif char == "\n":
            start_chunk()
        # Skip comment characters
        elif commenting:
            continue
        # Start a chunk via delimiter (lower priority, so | can appear in comments)
        elif char == DELIMITER:
            start_chunk()
        # Start escaping
        elif char == "\\":
            escaping = True
        elif char == "/" and len(accumulated_text) > 0 and accumulated_text[-1] == "/":
            accumulated_text = accumulated_text[:-1]
            commenting = True
        # Create a token from a symbol
        elif char in SYMBOLS.keys():
            tokenize_accumulation()
            tokens.append((SYMBOLS[char]()))
        # Accumulate the character as text
        else:
            accumulated_text += char

    # Tokenize leftover text
    tokenize_accumulation()

    return tokens
