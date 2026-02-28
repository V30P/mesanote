class Token:
    pass


class TextToken(Token):
    def __init__(self, value: str) -> None:
        self.value = value


class GroupStartToken(Token):
    pass


class GroupEndToken(Token):
    pass


class StructureStartToken(Token):
    pass


class SectionStartToken(StructureStartToken):
    pass


class ListStartToken(StructureStartToken):
    pass


comment_characters = "//"
delimiter = "|"
escape_character = "\\"
structures = {
    "{": GroupStartToken,
    "}": GroupEndToken,
    ">": SectionStartToken,
    "+": ListStartToken,
}

def tokenize(text: str) -> list[Token]:
    tokens = []
    accumulated_text = ""

    def tokenize_accumulation():
        nonlocal accumulated_text
        accumulated_text = accumulated_text.strip()

        if accumulated_text != "":
            tokens.append(TextToken(accumulated_text))
            accumulated_text = ""

    for line in text.splitlines():
        for virtual_line in line.split(delimiter):
            if virtual_line.lstrip().startswith(comment_characters):
                continue

            for char in virtual_line:
                if len(accumulated_text) > 0 and accumulated_text[-1] == escape_character:
                    if char in [delimiter, *structures]:
                        accumulated_text = accumulated_text.replace("\\", char)
                        continue
                    else:
                        raise Exception()

                if char == delimiter:
                    tokenize_accumulation()
                elif char in structures.keys():
                    tokenize_accumulation()
                    tokens.append((structures[char]()))
                else:
                    accumulated_text += char

            tokenize_accumulation()

    return tokens
