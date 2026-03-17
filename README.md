# MesaNote

A frill-free markup language built for efficient, organized note taking.

## Overview

MesaNote is designed as a markdown replacement for notetakers seeking a more rigidly structured syntax. Markdown’s flexibility makes it easy to use, but its loose structure can make large notes messy and difficult to interpret. MesaNote aims to solve this by taking some beloved elements of markdown and adding structure through features borrowed from classic C syntax. By convention, files in MesaNote format have the `.mdoc` (mesa document) extension, although this is by no means required.

In developing MesaNote, my goals are both to explore language creation and build something that I can use myself. For these reasons, the project includes minimal dependencies and focuses on simple, practical features built for everyday notetaking. This document is aimed at giving an overview of the design and functionality of the project, but if you wish to jump straight into learning MesaNote's syntax, see the syntax guide [here](SYNTAX.md).

This repository contains the following projects:

1. [Parser and CLI](core)
    - Low-dependency, pure Python implementation
    - Custom tokenizer, recursive descent parser, and AST
    - Simple, intuitive CLI
    - Test suite for core functionality

2. [VS Code extension](extensions/vscode)
    - Automatic language detection
    - Syntax highlighting
    - Markdown-like preview

## Examples

A basic Mesa Document might look something like this:

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

Which would render to this HTML:

```html
<h1>Project Launch</h1>
<h2>Tasks</h2>
<ul>
    <li>
        <h4>Setup Repository</h4>
        <p>Alice</p>
    </li>
    <li>
        <h4>Create Roadmap</h4>
        <ul>
            <li>
                <p>Bob</p>
            </li>
            <li>
                <p>Linda</p>
            </li>
        </ul>
    </li>
</ul>
```

For more sample documents, see the examples directory [here](examples). To see the rendered output of a document, look for the `.html` file of the same name, or use the CLI to parse the document yourself.

## Design

From a design perspective, MesaNote is intentionally minimal, being small enough to fully describe with a compact EBNF grammar and parse using a hand-written recursive descent parser. Each element of MesaNote's syntax has been carefully designed to optimize for intuitive, fast notetaking.

### Goals

- Fast, easy-to-type syntax
- Deterministic grammar (LL(1)-friendly)
- Familiar bracket-based structure
- C-style comments
- Quotation mark-free strings

### Tokenization

Tokens are either part of a string, a grouping (`{}`), or a structure (like `>`). Strings can be divided by a newline or a vertical bar `|` which allows for multiple to be written on the same line. Outside of strings, grouping and structure symbols both translate to their token equivalent 1 to 1.

To start a comment use `//`. This will exclude the rest of the line from the tokenization process. A single `\` can be used to escape characters with special meaning, so `\>` will be interpreted as an actual `>` rather than the start of a section. 

### Parsing

MesaNote's grammar can be described in EBNF format as follows:

```
document = { element } ;
element = string | grouping | structure ;
grouping = "{" , { element } , "}" ;
structure = section | list ;
```

Strings are defined as:

```
string = { substring } ;
substring = TEXT | emphasis ; ;
emphasis = weak_emphasis | strong_emphasis ;
weak_emphasis = "*" , TEXT , "*" ;
strong_emphasis =  "**" , (TEXT | emphasis), "**" ;
```

And structures are defined as:

```
section = ">" string, element ;
list = "+" grouping ;
```

Since this grammar is fully LL(1), it can be easily parsed by MesaNote's custom recursive descent parser implementation.

## Getting Started

To get started with MesaNote, clone the repository and run the `setup.sh` script located in the root directory:

```bash
./setup.sh
```

This will install the core python package, which includes the MesaNote CLI accessible via the command `mesa`. For help working with the CLI, use:

```bash
mesa --help
```

For those seeking a more complete notetaking experience including syntax highlighting and preview support, `setup.sh` also packages MesaNote's VS Code extension to `artifacts/mesanote.vsix`. To add the extension to VS Code, use the "install from VSIX" option in the extensions menu.

After everything is set up, see the syntax guide [here](SYNTAX.md) for information on how to use MesaNote's features to create your own documents.

## License

This project is licensed under the MIT License. See the LICENSE file for details.