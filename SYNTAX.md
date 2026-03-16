# MesaNote Syntax Guide

This document serves as a reference for MesaNote's syntax. If you want to use MesaNote but haven't set up the project yet, see the README's "Getting Started" section [here](README.md#getting-started).

MesaNote documents are composed of a small set of elements: strings, groupings, and structures. This document details each element and how they should be used.

## Strings

Strings are the most basic element of MesaNote and represent plain text. Any text that is not part of MesaNote's syntax is treated as a string. 

```cpp
This is a string
```

Strings can be separated by either a newline or a vertical bar (`|`). Both act as equivalent separators:

```cpp
String A
String B

String A | String B
```

### Emphasis (`*`)

To emphasize part of a string, surround it with matching asterisks:

```cpp
*This is important*
**This is very important**
***This is super important***
```

### Escaping (`\`)

If you need to include a symbol that MesaNote normally interprets as syntax, precede it with a backslash `\` to escape it:

```cpp
3 \* 5 = 15
```

## Groupings (`{}`)

Groupings allow multiple elements to be treated as a single unit. This is useful when a structure expects one element but you want to include several.

```cpp
{
    String A
    String B
}
```

Groupings are often used with structures like sections or lists.

## Sections (`>`)

Sections assign a title to another element. A section begins with a `>` followed by a string (the title) and an element (the content).

```cpp
> My Section
My section content
```

Use a grouping to include multiple elements under one section:

```cpp
> My Section {
    String A
    String B
}
```

Sections can be nested within other sections, resulting in their titles being scaled down:

```cpp
> My Section > My Subsection
My subsection content
```

## Lists (`+`)

Lists create an unordered collection of elements. A list starts with a `+` sign followed by a grouping containing its elements.

```cpp
+ {
    String A
    String B
    String C
}
```

## Comments (`//`)

A comment begins with `//` and continues to the end of the line. Commented text is ignored by the parser.

```cpp
This is a normal string // This text is a comment
```

## Further Reading

After reading through this syntax guide you should have a decent understanding of the basics of MesaNote syntax. You are now ready to get started creating and parsing your own Mesa Documents through either the CLI or VS Code extension.

If you have any lingering questions, or want to learn more about MesaNote's development, see:

- The examples directory [here](examples) for some sample Mesa Documents
- The README's "Design" section [here](README.md#design) to learn about the technical choices behind the language.
