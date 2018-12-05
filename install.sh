#!/bin/bash
PKGS_TO_INSTALL=""

function check_installed {
    dpkg -s "$1" >/dev/null 2>&1 || {
        PKGS_TO_INSTALL="$PKGS_TO_INSTALL $1"
    }
}

function install_missing {
    if [ "$PKGS_TO_INSTALL" != "" ]; then
        echo "Installing missing dependencies..." ; sudo apt-get install $PKGS_TO_INSTALL
    fi
}

# needed for extension to work
check_installed python-nautilus
check_installed gir1.2-gconf-2.0

install_missing


echo -ne "\nInstalling extension..."
TARGET=~/.local/share/nautilus-python/extensions
TARGET_LOCALES=$TARGET/locales-nautilus-new-folder-from-template
mkdir -p $TARGET
cp nautilus-new-folder-from-template.py $TARGET

mkdir -p $TARGET_LOCALES
cp -r -t $TARGET_LOCALES locales/*

TPL_FOLDER=$(xdg-user-dir TEMPLATES)
FT_PARENT=$TPL_FOLDER/FolderTemplates
mkdir -p $FT_PARENT/"Example Folder Template"
echo "This example file will be overwritten every time the nautilus new-folder-from-template extension is re-installed." > $FT_PARENT/"Example Folder Template"/"Example File.txt"

echo "DONE."
echo -e "\nYou will need to restart Nautilus for the extension to take effect.\n"
