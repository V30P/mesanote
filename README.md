# MesaNote

A frill-free markup language for quickly creating structured notes.

## Overview

MesaNote is a markdown replacement for notetakers seeking a more rigid syntax. Markdown’s flexibility makes it easy to use, but its loose structure can make large notes messy and difficult to interpret. MesaNote aims to solve this by taking some elements of Markdown and adding structure through C-style syntax. By convention, files use the `.mdoc` (Mesa document) extension, although this is not required.

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

A basic Mesa Document might look like this:

```cpp
> Project Launch 
{
    // Assign launch responsibilities
    > Tasks +  
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

For more sample documents, see the [`examples`](examples) directory. Rendered output can be found in corresponding `.html` files.

## Design

### Goals

The design of MesaNote is guided by the following objectives:

- Fast, easy-to-type syntax
- Deterministic grammar (LL(1)-friendly)
- Overall C-family stylization
- Rigid, bracket-based structure
- Quotation-mark-free strings

### Tokenization

Tokens consist of strings, groupings (`{}`), or structural markers (such as `>` and `+`). Strings can be split using newline or `|` to allow multiple values per line. Outside of strings, grouping and structural symbols map directly to tokens.

Comments begin with `//` and extend to the end of the line. A backslash (`\`) can be used to escape special characters, e.g. `\>`.

### Parsing

MesaNote’s grammar can be described in EBNF as:

```ebnf
document = { element } ;
element = string | grouping | structure ;
grouping = "{" , { element } , "}" ;

(* Strings *)
string = { substring } ;
substring = TEXT | emphasis ;
emphasis = weak_emphasis | strong_emphasis ;
weak_emphasis = "*" , TEXT , "*" ;
strong_emphasis = "**" , (TEXT | emphasis) , "**" ;

(* Structures *)
structure = section | list ;
section = ">" , string , element ;
list = "+" , grouping ;
```

Because this grammar is LL(1), it is a prime candidate for parsing using recursive descent, which is how MesaNote's parser is implemented.

## Getting Started

To get started with MesaNote, clone the repository and run the setup script:

```bash
./setup.sh
```

This installs the core Python package, including the `mesa` CLI:

```bash
# Help
mesa --help

# Run a command
mesa COMMAND
```

For full functionality including syntax highlighting and preview support, the script also generates a VS Code extension package at `artifacts/mesanote.vsix`. Install it via “Install from VSIX” in VS Code.

After setup, refer to the [syntax guide](SYNTAX.md) for language details.

## License

This project is licensed under the MIT License. See the LICENSE file for details.