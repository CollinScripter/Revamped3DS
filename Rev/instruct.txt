PakExplorer Instructions
========================

Most of the commands in PakExplorer are intuitive
and self-explanatory.  I'll go over ones specific
to .pak files briefly.

Menu Commands
-------------

File Menu -

Recover Unused Space:

  Eliminates all empty space from the pak file. Empty space is created when
  files are deleted or overwritten, because only the directory entry is
  deleted.  This speeds up file operations and allows files to be restored.
  Recovering space permanently destroys all deleted files.

Extract All		:  Extract all files, preserving path info, to the
			   directory containing the pak file.
Extract		:  Extract the currently select file(s) and folder(s) to
			   the directory containing the pak file.  Retains all path
			   information.
Extract To		:  Extracts the currently selected files(s) and folder(s) to
			   the specified path.  Retains all path information.

New Folder		:  

  Create a new folder in the currently selected path and adds a zero-length
  file to the folder.  This is needed because .pak files don't really have
  a true directory structure.  You can delete this file after you add another
  item to the new folder.

Restore Deleted Files:

  Opens the Restore dialog.  In the restore dialog you are given a list of
  all files deleted DURING THE CURRENT SESSION OF PAKEXPLORER.  These files
  can be restored to their original location only.  Any file which is
  deleted, cut, or overwritten will appear in this dialog, but ONLY if this
  happened during the current session.  Once you close PakExplorer, deleted
  files are LOST whether or not you recover unused space.  If you don't
  recover the space, the data is still there, but the directory entry is GONE.

View Menu
---------

Options		:  Displays the Options dialog.

  Here is a list of items in the Options dialog:

- Associate PakExplorer with .pak files - self-explanatory
- Add .pak files to the New menu - this refers to the WINDOWS "New" menu

- Automatically recover unused space on exit - on exit, reclaim space left
  by deleted, cut, or overwritted files.
- Confirm before recovering unused space - show a confirmation dialog before
  recovering space

- Prompt for target directory when using 'Extract To' - if this is chosen, you
  will be given a dialog in which to select the target directory.
- Always 'Extract To' here - any time you use the 'Extract To' command, the
  selected files will go to the directory you specify in the edit box
- Display warning before extracting files - obvious

- Confirm before updating files launched from PakExplorer - when you double-
  click a file in PakExplorer, it is opened with whatever program is associated
  with that file type.  PakExplorer detects any changes made to the file.
  If you select this option, you will be asked whether you wish to save the
  changes to the .pak file when the application used to edit the file closes,
  or when PakExplorer is closed.

  If you clear this option, PakExplorer will automatically save changes to the
  .pak.



				   