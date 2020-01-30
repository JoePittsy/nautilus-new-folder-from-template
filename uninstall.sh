#!/bin/bash


echo -ne "\nUninstalling extension..."
TARGET=~/.local/share/nautilus-python/extensions/nautilus-new-folder-from-template.py*

rm -rf $TARGET
echo "DONE."
