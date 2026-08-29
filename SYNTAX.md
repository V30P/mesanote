# MesaNote Syntax Guide

This file serves as a reference for MesaNote syntax. If you want to use MesaNote but still need to set it up, see the README’s [Getting Started](README.md#getting-started) section.

MesaNote documents are composed of three primary elements: strings, groupings, and structures. This guide describes each of them and how they are used.

## Contents

1. [Strings](#strings)
    - [Emphasis](#emphasis)
    - [Code Blocks](#code-blocks)
    - [Escaping](#code-blocks)
2. [Groupings](#groupings)
3. [Structures](#structures)
    - [Sections](#sections)
    - [Lists](#lists)
    - [Definitions](#definitions)
    - [Tables](#tables)
4. [Comments](#comments)

## Strings

Strings are the most basic element of MesaNote and represent some form of plain text. Any text that is not part of another syntactic construct is treated as a string.

```cpp
This is a string
```

Strings can be separated by either a newline or a vertical bar (`|`). Both behave equivalently:

```cpp
String A
String B

String A | String B
```

### Emphasis

Text in strings can be emphasized using asterisks:

```cpp
*This is important*
**This is very important**
***This is super important***
```

### Code Blocks

Code blocks are used to indicate that part of a string is code. They begin and end matching sets of one or more `` ` ``. 

Code blocks can span multiple lines.

```cpp
`
message = "HELLO WORLD"
print(message)
`
```

They can also be part of a larger string.

```cpp
This code `HELLO WORLD` is part of a string
````

### Escaping

Special syntax characters can be escaped using a backslash:

```cpp
3 \* 5 = 15
```

## Groupings

A grouping allows multiple elements to be treated as a single unit. On their own, groupings are not very useful, but they are key for working with structures.

```cpp
{
    String A
    String B
}
```

## Structures

Structures provide formatting outside of what is available with just plain text. 

In general, structures take the form:

```cpp
<strucure symbol> [args]
```

It is common practice to pass groupings to structures when the structure should contain multiple subelements.

```cpp
<structure symbol> { A | B }
```

### Sections

A sections assigns a title to an element. Section begin with `>` followed by a string (title) and an element (content).

```cpp
> My Section
My section content
```

Multiple elements can be included using a grouping:

```cpp
> My Section {
    String A
    String B
}
```

Sections can be nested, resulting in a hierarchical structure when rendered.

```cpp
> My Section > My Subsection
My subsection content
```

### Lists

A List creates an unordered collection of elements. A list begins with `+` followed by a grouping containing the list's elements.

```cpp
+ {
    String A
    String B
    String C
}
```

## Definitions

A definition assigns a meaning to a term. Each definition starts with `@` followed by two strings: one for the term and one for the definition.

```cpp
@ Term
Definition
```

Consecutive definitions will be rendered together as one definition list.

```cpp
@ Term A | Definition A
@ Term B | Definition B
```

### Tables 

A Table organizes content into a grid. Tables begin with `#` followed by a grouping where each element is one cell in the table. 

Tables can be one-dimensional.

```cpp
# {
    A
    B
    C
}
```

They can also be two-dimensional.

```cpp
# {
    { A1 | B1 | C1 }
    { A2 | B2 | C2 }
}
```

## Comments

Comments begin with `//` and extend to the end of the line. They are ignored by the parser.

```cpp
This is a normal string // This is a comment
```

## Further Reading

After reviewing this guide, you should have a working understanding of MesaNote syntax. You can now create and parse Mesa Documents using either the CLI or VS Code extension.

For more information, see:

- The [`examples/`](examples) directory for sample documents
- The README’s [Design](README.md#design) section for a more techincal look at MesaNote syntax