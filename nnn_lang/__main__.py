from nnn_lang.tokenizer import tokenize
from nnn_lang.parser import parse
from sys import argv
from pathlib import Path


def main():
    path = Path(argv[1])

    with open(path, "r") as file:
        tokens = tokenize(file.read())
        root = parse(tokens)
        html = root.render()

    with open(path.with_suffix(".html"), "w") as file:
        file.write(html)


if __name__ == "__main__":
    main()
