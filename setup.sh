#!/bin/bash
#
# Install MesaNote language support

artifacts_dir=$(realpath artifacts)

# Install the core language package
echo "Installing core language package..."
pipx install --force ./core  > /dev/null 2>&1

# Pack the vscode extension
echo "Packaging VS Code extension..."
cd extensions/vscode
cp ../../LICENSE .
vsce pack --out "$artifacts_dir/mesanote.vsix" > /dev/null 2>&1
rm LICENSE