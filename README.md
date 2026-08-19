# MesaNote

A frill-free markup language for quickly creating structured notes.

## Overview

MesaNote is a markdown replacement for notetakers seeking a more rigid syntax. Markdown’s flexibility makes it easy to use, but its loose structure can make large notes messy and difficult to interpret. MesaNote aims to solve this by taking some elements of Markdown and adding structure through C-style syntax. By convention, files written in MesaNote use the `.mdoc` (mesa document) extension.

## Contents

This repository contains the following projects:

1. [Parser and CLI](core)
   - Low-dependency, pure Python implementation
   - Custom tokenizer, recursive descent parser, and AST
   - Easy-to-use CLI
   - Core test suite

2. [VS Code extension](extension)
   - Automatic language detection
   - Syntax highlighting
   - Markdown-like preview

## Examples

A basic mesa document might look like this:

```cpp
> Project Launch {
    // Assign launch responsibilities
    > Tasks +  {
        > Setup Repository | Alice  

        > Create Roadmap + {
            Bob
            Linda
        }
    }
}
```

Which is roughly equivalent to Markdown:

```markdown
# Project Launch
## Tasks
- ### Setup Repository
    Alice

- ### Create Roadmap
    - Bob
    - Linda
```

For more sample documents, see the [`examples/`](examples) directory. Rendered output can be found in corresponding `.html` files.

## Design

### Goals

The design of MesaNote is guided by the following objectives:

- Fast, easy-to-type syntax
- Deterministic grammar (LL(1)-friendly)
- Overall C-family stylization
- Rigid, bracket-based structure
- Quotation-mark-free strings

### Tokenization

Tokens consist of strings, groupings (`{}`), or structural markers (such as `>` and `+`). Strings can be split using newline or `|`, which allows for multiple values per line. Outside of strings, grouping and structural symbols map directly to tokens.

Comments begin with `//` and extend to the end of the line. A backslash (`\`) can be used to escape special characters, e.g. `\>`.

### Parsing

MesaNote’s grammar can be described in EBNF as:

```ebnf
document = { element } ;
element = string | grouping | structure | comment ;
grouping = "{" , { element } , "}" ;
comment = "//", TEXT, "\n"; 

(* Strings *)
string = { substring } ;
substring = TEXT | emphasis | inline_code_block;
emphasis = weak_emphasis | strong_emphasis ;
weak_emphasis = "*" , TEXT , "*" ;
strong_emphasis = "**" , (TEXT | emphasis) , "**" ;
code_block = { "`" }- TEXT { "`" }- ;

(* Structures *)
structure = section | list | table ;
section = ">" , string , element ;
list = "+" , grouping ;
table = "#" , grouping;
```

Because this grammar is LL(1), it is a prime candidate for parsing using recursive descent, which is how MesaNote's parser is implemented.

For a more practical look at MesaNote's sytnax, see the [syntax guide](SYNTAX.md).

## Getting Started

To get started with MesaNote, clone the repository and run the setup script:

```bash
./setup.sh
```

This installs the core Python package, including the `mesa` CLI:

```bash
# Learn about the CLI
mesa --help

# Run a command
mesa COMMAND
```

For functionality like syntax highlighting and preview support, the script also generates a VS Code extension package at `artifacts/mesanote.vsix`. Install it via “Install from VSIX” in VS Code.

Additionally, MesaNote includes a `flake.nix` file which allows MesaNote to be used as a package or home-manager module via the Nix package manager.

## License

This project is licensed under the MIT License. See the LICENSE file for details.