import tempfile
import webbrowser
from pathlib import Path
import click

from mesanote import tokenizer
from mesanote import parser

def _validate_document(_, __, value: str) -> Path:
    path = Path(value)
    if path.is_file():
        return path

    mdoc_path = path.with_suffix(".mdoc")
    if mdoc_path.is_file():
        return mdoc_path

    raise click.BadParameter(f"Could not find file for path: '{path}'.")


def _parse_document(document: Path, output: Path) -> None:
    with open(document, "r") as file:
        try:
            tokens = tokenizer.tokenize(file.read())
            root = parser.parse(tokens)
        except (tokenizer.TokenizationError, parser.ParseError) as error:
            raise click.UsageError(message=error.args[0])

        html = root.render()

    with open(output or document.with_suffix(".html"), "w") as file:
        file.write(html)

# CLI
@click.group()
def cli():
    """The core CLI for the MesaNote markup language."""


@cli.command()
@click.argument(
    "document", type=click.Path(path_type=Path), callback=_validate_document
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="The output file path. Defaults to the document name with .html extension.",
    default=None,
)
def parse_command(document: Path, output: Path):
    """Parse a document and save output to a file."""

    _parse_document(document, output)


@cli.command()
@click.argument(
    "document", type=click.Path(path_type=Path), callback=_validate_document
)
def open_command(document: Path):
    """Parse a document and open it in the default web browser."""

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_path = Path(temp_file.name)

    _parse_document(document, temp_path)
    webbrowser.open(temp_path.as_uri())
