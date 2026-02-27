# Nate's Neat Notetaking Language

A frill-free markup Language built for efficient, organized note taking

## Overview

NNN-Lang is designed as a markdown replacement for notetakers seeking a more rigidly structured syntax. Markdown’s flexibility is powerful, but its loose structure can make large notes messy and difficult to interpret. NNN-Lang aims to solve this by taking some beloved elements of markdown and adding structure through features borrowed from classic C syntax.

This parser and renderer for Nate's Neat Notetaking Language is written from scratch in Python 3.12. In developing NNN-Lang, my goals are both to explore language creation and build something that I can use myself. For these reasons, the project includes minimal dependencies and focuses on simple, practical features.

## Examples


## Features

- Deterministic grammar (LL(1)-friendly)
- Explicit hierarchical grouping
- Comment-aware tokenization
- Zero-dependency, pure Python implementation
- Custom recursive descent parser
- HTML renderer

## Design

From a design perspective, NNN-Lang is intentionally minimal, being small enough to fully describe with a compact EBNF grammar and parse using a hand-written recursive descent parser.

### Tokenization

Tokens are either a structure symbol (like `>`), a grouping (`{}`), or raw text. Text tokens are divided by a newline or a vertical bar `|`. Since the opening bracket of a grouping implicitly starts a new token, both K&R and Allman style bracketing are valid in NNN-Lang.

To start a comment use `//` which will exclude the whole line from the tokenization process. A single `\` can be used to escape characters with special meaning, so `\>` will be interpreted as an actual `>` rather than the start of a section. 

### Parsing

NNN-Lang's grammar can be described in EBNF format as follows, where `TEXT` and `TITLE` are raw text tokens.

```
document = { element };
element = TEXT | grouping | structure;
grouping = "{" , { element } , "}";
structure = section | list;
```

With these definitions for specific structures:

```
section = ">" TITLE, element;
list = "+" [TITLE] , element;
```

Since this grammar is mostly LL(1) (although technically LL(2) due to the extra token of look ahead needed for optional list titles), it is easily parsed by a recursive descent parser.

After the main parser constructs the AST, a secondary inline parser processes only text nodes to recognize inline formatting constructs (like `**`). The final AST resulting from this secondary parse is what is eventually rendered to HTML.

## Getting Started

## License

This project is licensed under the MIT License. See the LICENSE file for details.