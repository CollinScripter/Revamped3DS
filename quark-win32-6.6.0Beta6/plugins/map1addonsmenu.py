"""   QuArK  -  Quake Army Knife

Implementation of QuArK Map editor's "Addons" menu
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/map1addonsmenu.py,v 1.4 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Addons Main Menu",
   "desc":          "This adds the Addons Main menu item and its Categories to run and import 3rd party programs.",
   "date":          "June 7 2003",
   "author":        "cdunde, Decker and others",
   "author e-mail": "cdunde1@attbi.com",
   "quark":         "Version 6.4" }


from quarkpy.maputils import *   # Need this
import quarkpy.mapcommands   # Need this for sub-menu appending


# ************************************************************
# ************************************************************

# Deckers coding ******************************


# Global variables, the sub-menuitems/popup-menus

ShapesMenu = qmenu.popup("&Shape programs", [], None, "|Shape programs:\n\nThese are programs that can make different shapes to use in your maps.\n\nOne that I recommend is 'MGS-object builder' and can be downloaded from the Yahoo Quark group site at\n\nhttp://groups.yahoo.com/group/quark/files/\n\nIf you find any programs that may help others, please let us know by making a posting to the Quark groups site at\n\nhttp://groups.yahoo.com/group/quark/", "intro.mapeditor.menu.html#addonsmenu")

TerrainMenu = qmenu.popup("&Terrain programs", [], None, "|Terrain programs:\n\nThis category is for your terrain programs for making landscape layouts in your maps.\n\nOne that I recommend is 'Terrain Generator' and can be downloaded from its own site at\n\nhttp://countermap.counter-strike.net/Nemesis/index.php?p=1\n\nIf you find any programs that may help others, please let us know by making a posting to the Quark groups site at\n\nhttp://groups.yahoo.com/group/quark/", "intro.mapeditor.menu.html#addonsmenu")

OtherMenu = qmenu.popup("&Other programs", [], None, "|Other programs:\n\nThis category is for all other types of programs that can export to a map file for your use in QuArk.\n\nIf you find any programs that may help others, please let us know by making a posting to the Quark groups site at\n\nhttp://groups.yahoo.com/group/quark/", "intro.mapeditor.menu.html#addonsmenu")

# The main Addons-menu (and shortcuts if any)
AddonsMenu = [ShapesMenu, TerrainMenu, OtherMenu] # The Addons menu items
AddonsMenuShortcuts = {}                     # The Addons menu shortcuts

def AddonsMenuCmds():       # AddonsMenuCmds used in quarkpy/mapmenus.py
    return quarkpy.qmenu.popup("&Addons", AddonsMenu, hint="|Addons:\n\nThis Main menu category was added for 3rd party, outside programs that can be ran from within QuArK.\n\nEach item through out this menu has its own help dialog. Just high light the menu item and press F1 for further help and a link to the infobase for further details if an 'InfoBase' link button exist in the help window.\n\nHistory:\n\nThis was originally intended to be the MGS file menu:\n\n With the MGS addon program, you can create several different types of shape items to be used in you maps.\n\nYou can also give your personal input to change these shapes as well as their size.\n\nIn addition, you can create plugins for the MGS program, to enhance its abilities to create shapes and/or common standard shapes and sizes to make your own library.\n\nBut the Addons menu function has now gone well beyond that. It demonstrates how a Main menu category can be added with a plugin file. The file name is map1addonsmenu.py and it also demonstrates how even a Main menu button can have an F1 help popup window and link to the infobase pages. The only difference is that one of the buttons of the Main menu has to be activated (clicked on) to initiate this feature. One other feature of this menu category, is the sub-menu drop down buttons. All these functions can be studied by reviewing the map1addonsmenu file in the plugins folder, and the mapmenus.py file located in the quarkpy folder (to see how the 'Addons' Main menu category is done).", infobaselink="intro.mapeditor.menu.html#addonsmenu"), AddonsMenuShortcuts


### Use another .py file to add items to the menu categories ### 

def Func1Click(self):
 
#Put the function code here
    pass
    editor = mapeditor()
    import map1loadanymap
    plugins.map1loadanymap.LoadMapClick(self)

# Add a menu item to the Addons->OtherMenu category


OtherMenu.items.append(qmenu.sep)
OtherMenu.items.append(quarkpy.qmenu.item("Import any map file", Func1Click, "|Import any map file:\n\nThis item function allows you to load any map file into the existing editor to be added to the map you are working on.\n\nBecause it also may import entities, you may half to delete some of them like its info_player_start.\n\nThis function is created by the plugins/map1loadanymap.py file.|intro.mapeditor.menu.html#addonsmenu"))


# ----------- REVISION HISTORY ------------
#
#$Log: map1addonsmenu.py,v $
#Revision 1.4  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.1  2003/07/04 20:01:16  cdunde
#To add new Addons main menu item and sub-menus
#
