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
   - Comprehensive test suite

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
structure = section | list | definitions | table ;
section = ">" , string , element ;
list = "+" , grouping ;
definitions = { "@", string , string }- ;
table = "#" , grouping;
```

Because this grammar is LL(1), it is a prime candidate for parsing using recursive descent, which is how MesaNote's parser is implemented.

For a more practical look at MesaNote's sytnax, see the [syntax guide](SYNTAX.md).

## Getting Started

MesaNote is packaged through the [Nix](https://github.com/nixos/nix) package manager. To install, run:

```bash
nix profile install github:V30P/mesanote
```

This installs the core Python package, including the `mesa` CLI.

```bash
# Learn about the CLI
mesa --help

# Run a command
mesa COMMAND
```

Additionally, the MesaNote VSCode extension is available at `github:V30P/mesanote#extension` and can be built via `nix build`.

For a cleaner installation experience, MesaNote provides a module for Nix's [Home Manager](https://github.com/nix-community/home-manager) system. It is also possible to automatically install the VSCode extension by including it in your `Programs.VSCode` config in Home Manager.

## License

This project is licensed under the MIT License. See the LICENSE file for details.