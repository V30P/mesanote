# MesaNote

A frill-free markup language built for efficient, organized note taking.

## Overview

MesaNote is designed as a markdown replacement for notetakers seeking a more rigidly structured syntax. Markdown’s flexibility is powerful, but its loose structure can make large notes messy and difficult to interpret. MesaNote aims to solve this by taking some beloved elements of markdown and adding structure through features borrowed from classic C syntax. By convention, files in MesaNote format have the `.mdoc` (mesa document) extension, although this is by no means required.

In developing MesaNote, my goals are both to explore language creation and build something that I can use myself. For these reasons, the project includes minimal dependencies and focuses on simple, practical features focused on everyday notetaking.

This repository contains the following projects:

1. [Parser and CLI](core)
    - Low-dependency, pure Python implementation
    - Custom tokenizer, recursive descent parser, and AST
    - Simple, intuitive CLI
    - Comprehensive unit tests

2. [VS Code extension](extensions/vscode)
    - Syntax highlighting
    - Markdown-like preview

## Examples

A basic document in MesaNote looks something like this:

```cpp
> Project Launch 
{
    // Assign launch responsibilities
    + Tasks 
    {
        > Setup Repository | Alice  

        > Create Roadmap + 
        {
            Bob
            Linda
        }
    }
}
```

For more sample documents, see the examples directory [here](examples). To see the rendered form of a document, look for the `.html` file of the same name or use the CLI to parse the document yourself.

## Design

From a design perspective, MesaNote is intentionally minimal, being small enough to fully describe with a compact EBNF grammar and parse using a hand-written recursive descent parser. Each element of MesaNote's syntax has been carefully designed to optimize for intuitive, fast notetaking.

### Goals

- Fast, easy-to-type syntax
- Deterministic grammar (LL(1)-friendly)
- Familiar bracket-based structure
- C-style comments
- Quotation mark-free strings

### Tokenization

Tokens are either a structure symbol (like `>`), a grouping (`{}`), or raw text. Text tokens are divided by a newline or a vertical bar `|`. Since the opening bracket of a grouping implicitly starts a new token, both K&R and Allman style bracketing are valid in MesaNote.

To start a comment use `//` which will exclude the whole line from the tokenization process. A single `\` can be used to escape characters with special meaning, so `\>` will be interpreted as an actual `>` rather than the start of a section. 

### Parsing

MesaNote's grammar can be described in EBNF format as follows:

```
document = { element };
element = string | grouping | structure;
grouping = "{" , { element } , "}";
structure = section | list;
```

Strings are defined as:

```
string = { substring } 
substring = TEXT | emphasis
emphasis = weak_emphasis | strong_emphasis
weak_emphasis = "*" , TEXT , "*"
strong_emphasis =  "**" , (TEXT | weak_emphasis), "**"
```

And structures are:

```
section = ">" TITLE, element;
list = "+" grouping;
```

Since this grammar is LL(1), it is easily parsed by a recursive descent parser.

## Getting Started

To get started with MesaNote, clone the repository and run the `setup.sh` script located in the root directory:

```bash
./setup.sh
```

This will install the core python package, which includes the MesaNote CLI accessible via the command `mesa`. For help working with the CLI, use:

```bash
mesa --help
```

For those seeking a more complete notetaking experience, `setup.sh` also packages the VS Code extension to `artifacts/mesanote.vsix`. To add the extension to VSCode, use the "install from VSIX" option in the extensions menu.

## License

This project is licensed under the MIT License. See the LICENSE file for details.