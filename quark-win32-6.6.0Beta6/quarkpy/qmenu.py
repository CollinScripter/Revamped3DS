"""   QuArK  -  Quake Army Knife

Menu Bars and Popup Menus code
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/quarkpy/qmenu.py,v 1.12 2010/10/20 06:40:37 cdunde Exp $


import quarkx
from qdictionnary import Strings
from qutils import *


# menu state
normal     = 0
checked    = 2
radiocheck = 3
disabled   = 4    # can be added to the above
default    = 8    # can be added to the above


class item:
    "A menu item."

    #
    # A menu item's onclick attribute must be a callback function,
    # called by QuArK when the user chooses the item in the menu.
    # It will be called with the menu item object itself as parameter.
    #

    def __init__(self, text, onclick=None, hint=None, infobaselink=""):
        self.text = text
        self.onclick = onclick
        self.state = normal
        if hint:
            self.hint = hintPlusInfobaselink(hint,infobaselink)


class popup:
    "A pop-up menu item."

    def __init__(self, text, items=[], onclick=None, hint=None, infobaselink=""):
        self.text = text
        self.onclick = onclick   # called when the popup menu is opened;
        self.items = items       # this lets you modify 'items' to reflect the current menu state
        self.state = normal
        if hint:
            self.hint = hintPlusInfobaselink(hint,infobaselink)


#
# Note: menus may have an attribute "menuicon" with an icon to display next to the menu item.
#

# a separator line in the menu
sep = None



def macroitem(text, macro, hint=None, infobaselink=""):
    "A menu item that executes a single macro command."
    if hint:
        hint = hintPlusInfobaselink(hint,infobaselink)
    m = item(text, macroclick, hint)
    m.macro = macro
    return m

def macroclick(m):
    if not (quarkx.clickform is None):
        import mdleditor
        if isinstance(quarkx.clickform.info, mdleditor.ModelEditor) and (m.macro == "UNDO" or m.macro == "REDO" or m.macro == "MURD"):
            editor = quarkx.clickform.info
            import mdlutils
            mdlutils.SaveTreeView(editor)
        quarkx.clickform.macro(m.macro)   # returns True (1) or False (0) depending on success or failure


def catmenus(list1, list2):
    "Concat the two lists of menu items, adding a separator if required."
    if len(list1):
        if len(list2):
            return list1 + [sep] + list2
        return list1
    return list2



#
# Standard menus.
#

def DefaultFileMenu():
    "The standard File menu, with its shortcuts."

    #NewMap1 = item("&New map")  # not implemented yet
    Open1 = macroitem("&Open...", "FOPN", "|You can open a file of ANY type.", "intro.mapeditor.menu.html#filemenu")
    savehint = "|You have several ways to save your maps :\n\nAs .map files : the .map format is standard among all Quake editors, but you should only use it to exchange data with another editor, because QuArK cannot store its own data in .map files (e.g. groups, duplicators, etc).\n\nAs .qkm files : this is QuArK's own file format for maps.\n\nInside .qrk files : this is the best solution if you want to organize several maps inside a single file. Choose the menu command 'Save in QuArK Explorer'."
    infobaselink = "intro.mapeditor.menu.html#filemenu"
    Save1 = macroitem("&Save", "FSAV", savehint, infobaselink)
    SaveQE1 = macroitem("Save in QuArK &Explorer", "FSAN", savehint, infobaselink)
    SaveAs1 = macroitem("Save &as file...", "FSAA", savehint, infobaselink)
    SaveAll1 = macroitem("Save a&ll", "FSAL", savehint, infobaselink)
    Close1 = macroitem("&Close", "EXIT", "close the map editor")
    File1 = popup("&File", [Open1, Save1, SaveQE1,
     SaveAs1, sep, SaveAll1, sep, Close1])
    sc = {}
    MapHotKeyList("Open", Open1, sc)
    MapHotKeyList("Save", Save1, sc)
    MapHotKeyList("Close", Close1, sc)
    return File1, sc



def DefaultFileMenuBsp():
    "The standard File menu for .bsp files."

    Open1 = macroitem("&Open...", "FOPN", "open a file of ANY type")
    Close1 = macroitem("&Close BSP editor", "EXIT", "close the BSP editor")
    File1 = popup("&File", [Open1, sep, Close1])
    sc = {}
    MapHotKeyList("Open", Open1, sc)
    MapHotKeyList("Close", Close1, sc)
    return File1, sc



def Edit1Click(Edit1):
    undo, redo = quarkx.undostate(Edit1.Root)
    if undo is None:
        Edit1.Undo1.text = Strings[113]   # nothing to undo
        Edit1.Undo1.state = disabled
    else:
        Edit1.Undo1.text = Strings[44] % undo
        Edit1.Undo1.state = normal
    if redo is None:
        if Edit1.Redo1 in Edit1.items:
            Edit1.items.remove(Edit1.Redo1)  # nothing to redo
    else:
        if not (Edit1.Redo1 in Edit1.items):
            Edit1.items.insert(Edit1.items.index(Edit1.Undo1)+1, Edit1.Redo1)
        Edit1.Redo1.text = Strings[45] % redo
    Edit1.editcmdgray(Edit1.Cut1, Edit1.Copy1, Edit1.Delete1)
    Edit1.Duplicate1.state = Edit1.Copy1.state
    Edit1.Paste1.state = not quarkx.pasteobj() and disabled


editmenu = {}

def DefaultEditMenu(editor):
    "The standard Edit menu, with its shortcuts."

    infobaselink = "intro.mapeditor.menu.html#editmenu"
    Undo1 = macroitem("&Undo", "UNDO", "|undo the previous action (unlimited)", infobaselink)
    Redo1 = macroitem("&Redo", "REDO", "|redo what you have just undone", infobaselink)
    UndoRedo1 = macroitem("U&ndo / Redo...", "MURD", "|list of actions to undo/redo", infobaselink)
    Cut1 = item("&Cut", editor.editcmdclick, "|cut the selection to the clipboard", infobaselink)
    Cut1.cmd = "cut"
    Copy1 = item("Cop&y", editor.editcmdclick, "|copy the selection to the clipboard", infobaselink)
    Copy1.cmd = "copy"
    Paste1 = item("&Paste", editor.editcmdclick, "|paste a map object from the clipboard", infobaselink)
    Paste1.cmd = "paste"
    Duplicate1 = item("Dup&licate", editor.editcmdclick, "|This makes a copy of the selected object(s). The copies are created at exactly the same position as the original, so don't be surprised if you don't see them : they are there, waiting to be moved elsewhere.", infobaselink)
    Duplicate1.cmd = "dup"
    Delete1 = item("&Delete", editor.editcmdclick, "|delete the selection", infobaselink)
    Delete1.cmd = "del"
    Edit1 = popup("&Edit", [Undo1, Redo1, UndoRedo1, sep,
     Duplicate1, sep, Cut1, Copy1, Paste1, sep, Delete1], Edit1Click)
    Edit1.Root = editor.Root
    Edit1.Undo1 = Undo1
    Edit1.Redo1 = Redo1
    Edit1.Cut1 = Cut1
    Edit1.Copy1 = Copy1
    Edit1.Paste1 = Paste1
    Edit1.Duplicate1 = Duplicate1
    Edit1.Delete1 = Delete1
    Edit1.editcmdgray = editor.editcmdgray
    sc = {}
    MapHotKeyList("Cut", Cut1, sc)
    MapHotKeyList("Copy", Copy1, sc)
    MapHotKeyList("Paste", Paste1, sc)
    MapHotKeyList("Delete", Delete1, sc)
    MapHotKeyList("Undo", Undo1, sc)
    MapHotKeyList("Redo", Redo1, sc)
    MapHotKeyList("Duplicate", Duplicate1, sc)
    return Edit1, sc

# ----------- REVISION HISTORY ------------
#
#
#$Log: qmenu.py,v $
#Revision 1.12  2010/10/20 06:40:37  cdunde
#Fixed the loss of selections and expanded items in the Model Editor from UNDO and REDO actions.
#
#Revision 1.11  2009/05/03 08:06:06  cdunde
#Edit menu, moved Duplicate and separated Delete from other items.
#
#Revision 1.10  2007/09/05 18:43:10  cdunde
#Minor comment addition and grammar corrections.
#
#Revision 1.9  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.6  2003/03/21 05:57:05  cdunde
#Update infobase and add links
#
#Revision 1.5  2003/03/16 02:43:09  tiglari
#fixed minor errors (unnecessary assignments)
#
#Revision 1.4  2003/03/15 20:41:07  cdunde
#To update hints and add infobase links
#
#Revision 1.3  2001/03/20 07:59:40  tiglari
#customizable hot key support
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#