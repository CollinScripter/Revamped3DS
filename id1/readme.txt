PakExplorer v1.2
=================

A Quake .pak browser for Windows95 and WindowsNT 4.0

Copyright 1997 by Ashley Bone

This program requires mfc42.dll and msvcrt.dll.  These files should be
place in your windows/system directory.

PakExplorer is freeware.  You may distribute this program freely and without
charge, as long as all the files in the zip archive are included and not
modified in any way.

PakExplorer may not be included with or as part of any commercial product.

PakExplorer has NOT been tested on windowsNT.  It should run on NT4.0, but
I'm not very familiar with it, so I can't guarantee that.

USERS OF PAKEXPLORER V1.0 should check the Options dialog for new settings
after installing v1.1.


Features
========

PakExplorer is a browser for Quake PAK files which uses a Windows
Explorer-style interface.  Some of the features of PakExplorer are:

- Registers .pak files from with the shell, so you can open them by
  double-clicking in explorer.

- Supports drag and drop to _and_ from windows explorer, between two
  PakExplorer windows, and within a single pak file.

- Supports cut and paste to and from explorer, between two .pak files, and
  within a single pak file.

- Creates new pak files, using the command in PakExplorer _or_ through
  the Windows 'New' menu, the same menu used to create new folders.

- Supports all internal operations - you can rename, move, and delete
  folders and files, create new folders, and restore deleted files.

- Shows file names, sizes, and types in the list view.  You can sort
  by any of these attributes, in ascending or descending order.

- Removes unused space from pak files introduced when deleting or overwriting
  files.

- Extract files, retaining all path information.  This feature is common in
  most pak rippers, so I included it here.

- Launch files directly from the pak.  Just double-click on the file to open it
  with the program you normally use to view that type.  PakExplorer keeps track
  of the file and saves any changes you make back to the .pak.

- Play wave files without extracting them.  Just highlight the wave file and
  click the 'Play' toolbar button.

- Right-click context menus provide easy access to most commands.

- Many of PakExplorer's features are optional - you choose whether or not to
  use them.  You can configure PakExplorer's shell registration, choose when
  to display confirmation messages, and more.

---------------------------------------------------------------------------------------
Installation
============

To install PakExplorer, simply extract pakexpl.exe from the zip file and place
it in the directory of your choice.  If you move PakExplorer after using it,
you'll have to run the executable by itself once so it can register its new
location with the shell.

The first time you run PakExplorer, the Options dialog will appear.  Set the
options you want, then click ok.  If you want to change these options in the
future, choose 'Options' from the View menu.

After setting the options, place and size the PakExplorer window to your
satisfaction.  You can now open pak files by doubling-clicking on them or
choosing "Open Pak" in the file menu.


Uninstalling
============

To uninstall, run the uninstall.exe program included with PakExplorer.  This will remove
all of PakExplorer's settings from the registry.  You can then delete all of the files
from the archive.

----------------------------------------------------

Notes
=====

- When cutting, deleting, or overwriting files, only the entry name of the
  file is removed.  The data remains intact.  Use the Restore command to
  'undelete' the file, or the Recover Unused space to permanently delete it.

- The maximum length of a pathname in a pak is 56 characters.  That applies
  to the entire path, not just the filename.

- PakExplorer requires filenames to follow the 8.3 rules, since Quake
  is a DOS program.

- Files cannot be cut from Windows Explorer - only copied.  They can be
  moved during a drag operation.

- Dragging to the desktop without holding any keys down doesn't behave
  correctly.  The drag icon signifies a copy operation, but the file gets
  moved.  Dragging with the SHIFT or CONTROL keys works correctly.

- Creating a new folder also creates a zero-length file in the new folder.
  This is because empty folders don't really exist inside pak files.  You
  can delete the file once you add something else to the new folder.

- Each of the Extract commands overwrites any files with duplicate names
  in the directory they are extracted to.  This behavior is by design.  There
  is an optional confirmation dialog which you can enable by opening the Options
  dialog.  The confirmation dialog doesn't check to see if any of the files
  exists, it just warns you that they'll be blown away if they do.


Version Info
============

v1.2	December 8, 1997

- fixed a few bugs related to uppercase names in the quake2 pak files

v1.12 (ok, maybe not the absolute final) - April 15, 1997
---------------------------------------------------------

- added several minor UI improvements - open/new tool bar buttons,
  pressing enter opens files and folders, list control keeps focus
  after opening a folder, backspace backs up one level in the hier-
  archy, put borders around toolbar play and stop icons in case user
  has a REALLY ugly color scheme and can't see the icons
- playing a wave sound while another is in progress now stops the first
  and plays the second

v1.1 (Final Release) - March 31, 1997
-------------------------------------

- improved status bar updating
- added ability to move files during drag from windows explorer
- fixed one other minor bug

v1.1 BETA 2 - March 13, 1997
----------------------------

- created a new icon for the application
- added sorting by column in the list view
- refresh command actually does something now
- added most recently used list
- added optional overwrite warning when extracting files
- added 'extract to' command
- added launching files from pak
- added playing wave files from pak
- added new ui elements and Options dialog controls for new
  features

- trying to access pak file on non-present removable media no
  longer crashes windows95
- fixed user interface updating in tree when invalid pak file is opened
- fixed several other user interface updating issues
- fixed file renaming bugs
- fixed conflict between in-place filename editing and accelerator keys

v1 BETA 1 - March 2, 1997
-------------------------

- Initial release