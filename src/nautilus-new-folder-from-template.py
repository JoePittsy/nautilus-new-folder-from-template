import gi
import sys
gi.require_version('Nautilus', '3.0')
gi.require_version('GObject', '2.0')
from gi.repository import Nautilus, GObject
import subprocess
import shutil
import urllib
import time
import re
import os


def substitute_name(file_name):
    """
    :param file_name: The file name
    :return: the file_name with %date[] replaced
    """
    regex = r"\%date\[.*?\]"   
    
    try:
        matches = re.finditer(regex, file_name, re.MULTILINE)
    except AttributeError:
        # there were no matches
        matches = []

    for match in matches:    
        date_str = time.strftime(match.group()[6:-1])
        file_name = file_name.replace(match.group(), date_str)

    
    return file_name


def create_unique_folder(path):
    """
    :param path: Creates a folder at this path if not present
    :return: None
    """
    if not os.path.isdir(path):
        subprocess.check_output(['mkdir', '-p', path])


def create_folder(path):
    """
    :param path: Creates a folder at this path if not present else create a new folder with an incrementing number
    ex. folder(2)
    :return: the path of the created folder
    """
    if not os.path.isdir(path):
        subprocess.check_output(['mkdir', '-p', path])
        return path
    else:
        i = 1
        while True:
            new_path = path + "(%d)" % i
            if not os.path.isdir(new_path):
                subprocess.check_output(['mkdir', '-p', new_path])
                return new_path
            else:
                i += 1


def copy_into_folder(source, destination):
    """
    :param source: The folder to copy from
    :param destination: The folder to copy to
    :return: None
    """
    for sub_level in os.walk(source):
        cwd, folders, files = sub_level
        diff = set(cwd.split(source))
        dest = destination.join(diff) if len(diff) != 1 else destination
        for folder in folders:
            folder = substitute_name(folder)
            create_unique_folder(dest + "/" + folder)
        for file in files:
            shutil.copy2(cwd + "/" + file, dest + "/" + substitute_name(file))


class NewFolderFromTemplate(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        GObject.Object.__init__(self)
        # Get the template folders directory
        with open(os.path.abspath(os.path.expanduser("~/.config/user-dirs.dirs"))) as config_file:
            data = config_file.read()
            template_line = data[data.find("XDG_TEMPLATES_DIR"):data.find("XDG_PUBLICSHARE_DIR=")]
            self.template_folders_directory = template_line[template_line.find('"') + 1:-2] + "/../FolderTemplates"
            if "$HOME" in self.template_folders_directory: 
                self.template_folders_directory = self.template_folders_directory.replace("$HOME", os.environ["HOME"])

        # If the folder doesn't exist then create it
        create_unique_folder(self.template_folders_directory)
        create_unique_folder(self.template_folders_directory + "/New Folder")

    def button_clicked(self, state, folder, current_directory):
        path = create_folder(current_directory + "/" + substitute_name(folder))
        print(folder + " Created")
        copy_into_folder(self.template_folders_directory + "/" + folder, path)

    def get_background_items(self, window, file):
        
        current_directory = urllib.unquote(file.get_uri()[7:])

        submenu = Nautilus.Menu()

        for item in os.listdir(self.template_folders_directory):
            if os.path.isdir(self.template_folders_directory + "/" + item):
                menu_item = Nautilus.MenuItem(name='NewFolderFromTemplate::Template', label=item, tip='', icon='')
                menu_item.connect("activate", self.button_clicked, item, current_directory)
                submenu.append_item(menu_item)

        menuitem = Nautilus.MenuItem(name='NewFolderFromTemplate::FolderTemplates',
                                     label='New Folder from Template',
                                     tip='',
                                     icon='')
        menuitem.set_submenu(submenu)

        return menuitem,

