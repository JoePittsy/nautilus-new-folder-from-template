Description
===========

This Nautilus extension allows you to create template directories within the
`FolderTemplates` directory which should be made in the same parent folder as 
the templates directory.  A "New Folder from Template" menu-item will be added
to the context menu when you right click on things in Nautilus. From this
 menu-item, you can choose a template directory structureto be created.

The following three cases are supported -- right-clicking on:

  * empty background => template copied to subfolder of current folder
  * a directory => template copied to subfolder of selected dir
  * a file => template copied to subfolder of file's parent

The main motivation for creating this extension is to be able to create entire
directory structures from templates, just as you can create new individual files
from templates.  This is convenient if you have several projects which require
the same kinds of files.  A LaTeX project, for example, might be well suited to
this, since one document may require multiple files -- preamble, bibliography,
main document, etc.

Templates will be coppied over exactly, unless the template has an init.sh
file, if so then this file will be executed within the destination folder. 
This could be used to say clone a Git Hub repository every time a template
is coppied for example. 

Another feature is having a date in either the Template folder or template 
files names, such as Joe's Template %date[%Y-%m-%d]. This we be cloned but
with the current date. As stated this also works with files. 




Installation
============

To install, simply run the `install.sh` script included in this repository.

This script checks that required dependencies are installed, and copies the `nautilus-new-folder-from-template.py` file to the `~/.local/share/nautilus-python/extensions` directory, as well as copying over language translation files to the same directory.


About
=====

Author/License
--------------

- License: GPLv3
- Original Author: Mark Edgington ([bitbucket site](https://bitbucket.org/edgimar/nautilus-new-folder-from-template))
- Latest Author: Joseph Pitts ([github site](https://bitbucket.org/edgimar/nautilus-new-folder-from-template))

Contributing
------------

Patches / pull-requests are welcome.
