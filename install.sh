#!/bin/bash

# Install the core language project
pipx install --force ./core

# Pack the vscode extension
cd vscode
cp ../LICENSE .
vsce pack --out ../artifacts/mesanote.vsix
rm LICENSE