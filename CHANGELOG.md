# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-11

### Added
- Codeblocks, definitions, and tables
- Improved extension syntax highlighting
- CLI, extension, and Home Manager module derivations in `flake.nix`

## Changed
- `TokenizationError` and `ParseError` to include source location and context
- README to use Nix for installation instructions (replaces setup.sh)

### Fixed
- Extension failing when trying to re-open the preview after closing it
- Errors in README EBNF grammar

## Removed
- `setup.sh` script
- `examples/` directory

## [0.1.0] - 2026-03-16

### Added
- Core tokenizer and parser
- Support for strings, groupings, sections, lists, and comments
- Basic CLI functionality for the core package
- `parse`, `text`, and `open` CLI commands
- Minimal VS Code extension with syntax highlighting and preview
- Initial documentation and README