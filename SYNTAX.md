# MesaNote Syntax Guide

This document serves as a reference for MesaNote syntax. If you want to use MesaNote but have not set up the project yet, see the README’s [Getting Started](README.md#getting-started) section.

MesaNote documents are composed of three primary elements: strings, groupings, and structures. This guide describes each of them and how they are used.

## Strings

Strings are the most basic element of MesaNote and represent plain text. Any text that is not part of another syntactic construct is treated as a string.

```cpp
This is a string
```

Strings can be separated by either a newline or a vertical bar (`|`). Both behave equivalently:

```cpp
String A
String B

String A | String B
```

### Emphasis (`*`)

Text can be emphasized using asterisks:

```cpp
*This is important*
**This is very important**
***This is super important***
```

### Escaping (`\`)

Special syntax characters can be escaped using a backslash:

```cpp
3 \* 5 = 15
```

## Groupings (`{}`)

Groupings allow multiple elements to be treated as a single unit. This is useful when a structure expects one element but multiple elements are needed.

```cpp
{
    String A
    String B
}
```

## Sections (`>`)

Sections assign a title to an element. A section begins with `>` followed by a string (title) and an element (content).

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

## Lists (`+`)

Lists define an unordered collection of elements. A list begins with `+` followed by a grouping of items.

```cpp
+ {
    String A
    String B
    String C
}
```

## Comments (`//`)

Comments begin with `//` and extend to the end of the line. They are ignored by the parser.

```cpp
This is a normal string // This is a comment
```

## Further Reading

After reviewing this guide, you should have a working understanding of MesaNote syntax. You can now create and parse Mesa Documents using either the CLI or the VS Code extension.

For more information, see:

- The [`examples`](examples) directory for sample documents
- The README’s [Design](README.md#design) section for technical background