"""nautilus-new-folder-from-template.py -- add menu items to copy template
folders as subfolders of the current or selected nautilus folder.

To install, put this file in the ~/.local/share/nautilus-python/extensions
directory.

2014-01-06, Mark Edgington


Moddified from Mark Edgington's Nautilus-new-folder-from-template
# https://bitbucket.org/edgimar/nautilus-new-folder-from-template

Now applys date formmating to files and not just folders. 
Futhermore users can now put a init.sh file in there template that will be 
run on template creation. Could be used to download a git repository or more.

2018-12-5, Joseph Pitts
"""

import os
import urllib
import shutil
import re
import time
import subprocess
import sys

import locale
import gettext

from gi.repository import Nautilus, GObject, GConf

print("Program Started!")
    
# localize language if translation is available
default_locale = locale.getdefaultlocale()[0]
# localization folder must contain subfolders / files like:
#     <loc_folder>/en/LC_MESSAGES/messages.mo
#
# This .mo file must be generated from a .po file, by using the 'msgfmt'
# executable from the commandline:  for example, run 'msgfmt messages.po'
#
localization_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'locales-nautilus-new-folder-from-template')
try:
    trans = gettext.translation('messages', localization_folder, languages=[default_locale])
    trans.install()
except IOError:
    # default locale not found / translation doesn't exist
    # define _ function to use default behavior
    def _(message): return message


class DirectoryTemplateExtension(Nautilus.MenuProvider, GObject.GObject):
    def __init__(self):
        self.client = GConf.Client.get_default()     

        
        with open(os.path.abspath(os.path.expanduser('~/.config/user-dirs.dirs')), "r") as f:
            config_file = f.read()
        self.templates_parent_dir = os.path.join(config_file[config_file.index("XDG_TEMPLATES_DIR")+19:config_file.index("\n", config_file.index("XDG_TEMPLATES_DIR"))-1], "..", "FolderTemplates")
       

        # create the template-folders parent dir if it doesn't already exist
        subprocess.check_output(['mkdir', '-p', self.templates_parent_dir])



    def copy_template_dir(self, tpl_foldername, dir_to_create_subfolder_in,
                          dest_subfolder_name=None):
        """Copy the specified template folder to the specified parent directory.

        All of the contents of the template directory will be copied
        (recursively) into a folder inside of *dir_to_create_subfolder_in*.

        *dir_to_create_subfolder_in* is the absolute path of the directory into
        which the subfolder should be placed.

        *tpl_foldername* is only the name of the template directory, not the
        absolute path to it.  Its absolute path is formed by prefixing the
        folder-name with the *self.templates_parent_dir*.

        If *dest_subfolder_name* is specified, it will be used as the
        destination into which *tpl_foldername*'s contents are copied into.
        Otherwise, its contents are copied into a folder having the same name.

        """
        tpl_folder_abspath = os.path.abspath(os.path.join(self.templates_parent_dir, tpl_foldername))
        
        if dest_subfolder_name is None:
            dest_subfolder_name = tpl_foldername

        dest_subfolder_name = dir_to_create_subfolder_in+"/"+dest_subfolder_name
        
        try:
            os.mkdir(dest_subfolder_name)
            print("INFO: Created Folder {0}".format(dest_subfolder_name))
        except FileExistsError:
            pass

        try:
            for x in os.walk(tpl_folder_abspath):
                for file in x[2]:                    
                    if x[0] == tpl_folder_abspath:
                        print("INFO: Copying File {0}".format(x[0] +"/"+ self.substitute_name(file)))
                        shutil.copy2(x[0] +"/"+ file, dest_subfolder_name+"/"+ self.substitute_name(file))
                        if file == "init.sh":
                            p = subprocess.Popen(['bash', dest_subfolder_name+"/"+ self.substitute_name(file)], cwd = dest_subfolder_name)
                            print("INFO: Ran init.sh")
                            p.wait()
                            os.remove(dest_subfolder_name+"/"+ self.substitute_name(file))
                    else:
                        sub_folder = dest_subfolder_name+x[0][len(tpl_folder_abspath):]      
                        try:                  
                            os.mkdir(sub_folder)
                        except FileExistsError:
                            pass
                        shutil.copy2(x[0] +"/"+ file, sub_folder+"/"+ self.substitute_name(file))
      
        except OSError, e:
            # couldn't copy folder (permissions issue or dest folder already exists)
            print("Unable to create template folder: " + str(e))

    def substitute_name(self, fname):
        """Replace any parts of *fname* with other content (e.g. timestamp)

        If *fname* contains somewhere within it the special string
        "%date[...]" (where ... represents a date/time format), then this
        will be replaced by the correspondingly formatted date/time.

        For example, if *fname* is "myfile-%date[%Y-%m-%d].txt", then it might
        be modified so that it this function returns "myfile-2014-01-01.txt",
        depending on the current time/date.

        """
        try:
            matches = re.search(".*(%date\[.+\]).*", fname).groups()
        except AttributeError:
            # there were no matches
            matches = []

        for match in matches:
            timedate_pattern = re.search("%date\[(.+)\]", match).groups()[0]
            datestr = time.strftime(timedate_pattern)
            fname = fname.replace(match, datestr)

        return fname

    def menu_activate_cb(self, menu, tpl_foldername, target_parent_dir):
        target_subfolder = tpl_foldername

        self.copy_template_dir(tpl_foldername, target_parent_dir, target_subfolder)

    def add_submenu_items(self, submenu, itemlist, dir_to_create_subfolder_in):
        for i,item in enumerate(itemlist):
            sub_menuitem = Nautilus.MenuItem(name='DirectoryTemplateExtension::%s' % i,
                                             label=item,
                                             tip='',
                                             icon='')
            submenu.append_item(sub_menuitem)

            # pass 'item' to the activate_cb method when this item is selected
            sub_menuitem.connect('activate', self.menu_activate_cb, item, dir_to_create_subfolder_in)


    def get_list_of_template_dirs(self):
        "Return a list of dirs contained in *self.templates_parent_dir*"
        return os.listdir(self.templates_parent_dir)

    def get_file_items(self, window, files):
        if len(files) != 1:
            return

        f = files[0]

        # the 'file' URI scheme is used for files and for directories
        if f.get_uri_scheme() != 'file':
            return

        if f.is_directory():
            # it is already a directory, so get the absolute path to it
            target_parent_dir = urllib.unquote(f.get_uri()[7:]) # directory that this extension was called on/in
        else:
            # it is only a file, so get the absolute path of f's parent directory
            target_parent_dir = urllib.unquote(f.get_parent_uri()[7:]) # directory that this extension was called on/in

        top_menuitem = Nautilus.MenuItem(name='DirectoryTemplateExtension::NFFT',
                                         label=_('New Folder from Template'),
                                         tip='',
                                         icon='')

        submenu = Nautilus.Menu()
        top_menuitem.set_submenu(submenu)

        template_dir_choices = self.get_list_of_template_dirs()
        self.add_submenu_items(submenu, template_dir_choices,
                               dir_to_create_subfolder_in=target_parent_dir)

        return top_menuitem,

    def get_background_items(self, window, file_obj):
        """Function called by Nautilus to get menus.

        *file_obj* is a Nautilus VFS file object representing the current dir.

        """
        # the 'file' URI scheme is used for files and for directories
        if file_obj.get_uri_scheme() != 'file':
            return

        f = file_obj

        # it is already a directory, so get the absolute path to it
        target_parent_dir = urllib.unquote(f.get_uri()[7:]) # directory that this extension was called on/in

        top_menuitem = Nautilus.MenuItem(name='DirectoryTemplateExtension::NFFT',
                                         label=_('New Folder from Template'),
                                         tip='',
                                         icon='')

        submenu = Nautilus.Menu()
        top_menuitem.set_submenu(submenu)

        template_dir_choices = self.get_list_of_template_dirs()
        self.add_submenu_items(submenu, template_dir_choices,
                               dir_to_create_subfolder_in=target_parent_dir)

        return top_menuitem,

