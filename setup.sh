#!/usr/bin/env bash

set -Eeuo pipefail
trap 'echo "Error: Command \"${BASH_COMMAND}\" failed"; exit 1' ERR

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$root_dir"

# Install core language package
command -v pipx >/dev/null || { echo "pipx not installed"; exit 1; }

echo "Installing core language package..."
pipx install --force "$root_dir/core" > /dev/null 2>&1

# Package VS Code extension
echo "Packaging VS Code extension..."

command -v vsce >/dev/null || { echo "vsce not installed"; exit 1; }
command -v realpath >/dev/null || { echo "realpath not installed"; exit 1; }

artifacts_dir=$(realpath "$root_dir/artifacts")
mkdir -p "$artifacts_dir"

cd extensions/vscode
cp ../../LICENSE .
vsce pack --out "$artifacts_dir/mesanote.vsix" > /dev/null

rm LICENSE