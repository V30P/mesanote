from mesanote.tokens import (
    Token,
    TextToken,
    GroupStartToken,
    GroupEndToken,
    SectionStartToken,
    ListStartToken,
)

comment_chars = "//"
delimiter_char = "|"
escape_char = "\\"

# Tokens that can be created from a single character
symbols = {
    "{": GroupStartToken,
    "}": GroupEndToken,
    ">": SectionStartToken,
    "+": ListStartToken,
}


def tokenize(text: str) -> list[Token]:
    tokens = []
    accumulated_text = ""

    # Create a text token from the characters that haven't been tokenized
    # Will skip creating a token if it would be empty
    def tokenize_accumulation():
        nonlocal accumulated_text
        accumulated_text = accumulated_text.strip()

        if accumulated_text != "":
            tokens.append(TextToken(accumulated_text))
            accumulated_text = ""

    for chunk in text.replace('\n', delimiter_char).split(delimiter_char):
        # Skip comments
        if chunk.lstrip().startswith(comment_chars):
            continue

        for char in chunk:
            if len(accumulated_text) > 0 and accumulated_text[-1] == escape_char:
                if char in [delimiter_char, *symbols]:
                    accumulated_text = accumulated_text.replace("\\", char)
                    continue
                else:
                    raise Exception()
                
            if char == delimiter_char:
                tokenize_accumulation()
            elif char in symbols.keys():
                tokenize_accumulation()
                tokens.append((symbols[char]()))
            else:
                accumulated_text += char

        tokenize_accumulation()

    return tokens
