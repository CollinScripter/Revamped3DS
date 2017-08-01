"""   QuArK  -  Quake Army Knife

Base of the Map editor "Search" menu
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapsearch.py,v 1.6 2005/10/15 00:47:57 cdunde Exp $



import quarkx
from qdictionnary import Strings
from maputils import *
import qmenu


def SearchResult(editor, list):
    #
    # For commands that make a simple search, you can call this
    # function with the 'list' of objects found and the results
    # will be displayed for the user. If someone wants to extend
    # this code, we could let the user choose if he wants to select
    # all items found (current behaviour) or if he wants to browse
    # step-by-step through the objects -- for this case, add a menu
    # item "find next" to the Search menu.
    #
    if len(list):
        editor.layout.explorer.sellist = list
        list = editor.layout.explorer.sellist  # re-read this, to remove sub-items of items also in the list
        if len(list)==1:
            editor.layout.explorer.uniquesel = list[0]
            quarkx.msgbox(Strings[194], MT_INFORMATION, MB_OK)
        else:
            quarkx.msgbox(Strings[195]%len(list), MT_INFORMATION, MB_OK)
    else:
        quarkx.msgbox(Strings[193], MT_INFORMATION, MB_OK)


#
# Search for Holes
#

def sholes1click(m):
    editor = mapeditor()
    if editor is None: return
    import mapholes
    mapholes.SearchForHoles(editor)



#
# Perform Checks on the map
#

def noproblem(menu):
    if menu is not None:
        quarkx.msgbox(Strings[5668], MT_INFORMATION, MB_OK)
    return 1

def problem(description, sellist=None):
    if quarkx.msgbox(Strings[5669] % description, MT_ERROR, MB_OK | MB_IGNORE) == MR_OK:
        editor = mapeditor()
        if (editor is not None) and (editor.layout is not None) and (sellist is not None):
            editor.layout.explorer.sellist = sellist
        return 0

def CheckMap(menu=None):
    progr = quarkx.progressbar(501, len(checkitems))
    try:
        for i in checkitems:
            result = i.onclick()
            if not result:
                return result
            progr.progress()
    finally:
        progr.close()
    return noproblem(menu)


#
# Global variables to update from plug-ins.
#

items = []
checkitems = []
shortcuts = {}

def onclick(menu):
    pass


def SearchMenu():
    "The Search menu, with its shortcuts."
    sholes1 = qmenu.item("&Holes in map", sholes1click, "|Holes in map:\n\nThis function will search for a hole in your map.\n\nA map must not contain any hole, that is, there must be no path from 'inside' to 'outside' the map. All entities must be completely enclosed by polyhedrons. With this command, QuArK will search for such holes, and if it finds one, it displays an arrow that starts from an entity and goes outside through a hole or a gap. Generally, the end of the arrow is exactly in the hole.\n\nNote that the path found by QuArK is maybe not the most direct way to reach the hole, and there are maybe other holes in your map.", "intro.mapeditor.menu.html#searchmenu")
    if len(checkitems)>1:
        allchecks = [qmenu.item("&ALL CHECKS", CheckMap, "perform all map checks")]
    else:
        allchecks = []
    it1 = items + [qmenu.sep, sholes1, qmenu.sep] + checkitems + allchecks
    return qmenu.popup("&Search", it1, onclick), shortcuts

# ----------- REVISION HISTORY ------------
#
#
#$Log: mapsearch.py,v $
#Revision 1.6  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.3  2003/03/21 05:57:05  cdunde
#Update infobase and add links
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#