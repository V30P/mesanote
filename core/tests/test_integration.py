import pytest

from mesanote.tokenizer import tokenize
from mesanote.parser import parse


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", ""),
        (
            "Text `Code`Text \>**Bold** *Italics*Text \+",
            "<p>Text <code>Code</code>Text &gt;<strong>Bold</strong> <em>Italics</em>Text +</p>",
        ),
        (
            """
            // Comment
            > Title {
                A
                B | C
                D
            }
            """,
            "<h1>Title</h1><p>A</p><p>B</p><p>C</p><p>D</p>",
        ),
        (
            """
            > A> B + 
            {
                1
                2
                3 // Comment
                4
            }
            """,
            "<h1>A</h1><h2>B</h2><ul><li><p>1</p></li><li><p>2</p></li><li><p>3</p></li><li><p>4</p></li></ul>",
        ),
        (
            """
            + {A
            B
            > C {
                }
            }

            `
            CODE
            CODE
            CODE
            `
            """,
            "<ul><li><p>A</p></li><li><p>B</p></li><li><h2>C</h2></li></ul><p></p><pre><code>CODE\nCODE\nCODE\n</code></pre><p></p>",
        ),
        (
            """
            + {
                # { A| B} Text}
            """,
            "<ul><li><table><tr><td><p>A</p></td></tr><tr><td><p>B</p></td></tr></table></li><li><p>Text</p></li></ul>",
        ),
        (
            """
            > //Comment 
            Title
            {
                @ A | 1
                @ B 
                2
                \>
            }
            """,
            "<h1>Title</h1><dl><dt>A</dt><dd>1</dd><dt>B</dt><dd>2</dd></dl><p>&gt;</p>",
        ),
    ],
)
def test_integration(input, expected):
    assert parse(tokenize(input)).render() == expected
