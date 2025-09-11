#!/bin/sh

OS=$(uname -s)

if [ "$OS" = "Darwin" ]; then
    echo "Running macOS executable..."
    ../bin/darwin/pack ../script-files/pse-script-og.pak scn.pak ../script-files/pse-modified/*.DAT
elif [ "$OS" = "Linux" ]; then
    echo "Running Linux executable..."
    ../pack      # replace with your Linux binary name
else
    echo "Unsupported OS: $OS"
    exit 1
fi
