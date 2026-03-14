import tempfile
import webbrowser
from pathlib import Path
import click

from mesanote import tokenizer
from mesanote import parser


def _parse_text(text: str):
    try:
        tokens = tokenizer.tokenize(text)
        root = parser.parse(tokens)
    except (tokenizer.TokenizationError, parser.ParseError) as error:
        raise click.UsageError(message=error.args[0])

    return root.render()


def _validate_document_path(_, __, value: str) -> Path:
    path = Path(value)
    if path.is_file():
        return path

    mdoc_path = path.with_suffix(".mdoc")
    if mdoc_path.is_file():
        return mdoc_path

    raise click.BadParameter(f"Could not find file for path: '{path}'.")


def _parse_document(document_path: Path, output_path: Path) -> None:
    with open(document_path, "r") as file:
        html = _parse_text(file.read())

    with open(output_path or document_path.with_suffix(".html"), "w") as file:
        file.write(html)


# region CLI
@click.group()
def cli():
    """The core CLI for the MesaNote markup language."""


@cli.command()
@click.argument(
    "text",
    type=str,
    required=False,
    default=None,
)
def text_command(text: str):
    """Parse text and print the output. If no text is provided, it will be read from stdin."""

    if text is None:
        stdin = click.get_text_stream("stdin")
        if not stdin.isatty():
            text = stdin.read().strip()
        else:
            raise click.UsageError(
                "No text argument was provided and nothing was written to stdin."
            )

    click.echo(_parse_text(text))


@cli.command()
@click.argument(
    "document", type=click.Path(path_type=Path), callback=_validate_document_path
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
    "document", type=click.Path(path_type=Path), callback=_validate_document_path
)
def open_command(document: Path):
    """Parse a document and open it in the default web browser."""

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_path = Path(temp_file.name)

    _parse_document(document, temp_path)
    webbrowser.open(temp_path.as_uri())


if __name__ == "__main__":
    cli()
# endregion
