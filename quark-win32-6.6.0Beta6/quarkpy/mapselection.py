"""   QuArK  -  Quake Army Knife

The map editor's "Selection" menu (to be extended by plug-ins)
"""
#
# Copyright (C) 1996-99 Armin Rigo and the QuArK community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapselection.py,v 1.17 2005/10/15 00:47:57 cdunde Exp $


import quarkx
import qmenu
import mapmenus
from maputils import *


def getEditorSelection(editor=None):
    if editor is None:
        editor = mapeditor(SS_MAP)
    if editor is None:
        return None, None
    sel = editor.layout.explorer.uniquesel
    return editor, sel
    

def EscClick(m):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    #if editor.layout.mpp.n:
        #editor.layout.mpp.viewpage(0)
    else:
        editor.layout.mpp.viewpage(0)
        editor.layout.explorer.uniquesel = None
    delAttr(editor,'frozenselection')


def DetailClick(m):
    editor = mapeditor(SS_MAP)
    if editor is not None:
        undo = quarkx.action()
        items = editor.layout.explorer.sellist

        # Quickly defined function within function.
        def SwapFlag(ContentsString, flagvalue=134217728):
            if (ContentsString == None):
                contents_integer = 0
            else:
                contents_integer = int(ContentsString)

            if ((contents_integer & flagvalue) == flagvalue):
                contents_integer = (contents_integer - flagvalue)
            else:
                contents_integer = (contents_integer | flagvalue)
            return str(contents_integer)

        # Loop through all items, one by one
        for item in items:
            if item.type == ":f":
                # The item is a single face, so swap its flag
                undo.setspec(item, 'Contents', SwapFlag(item['Contents']))
            elif item.type == ":p":
                # The item is a polyhedron, which may consist of several faces (or other stuff)
                for subitem in item.faces:
                    if subitem.type == ":f":
                        undo.setspec(subitem, 'Contents', SwapFlag(subitem['Contents']))

        undo.ok(editor.Root, "swap detail flag")
        editor.layout.explorer.sellist = items
    
def UnfreezeClick(m):
    editor = mapeditor(SS_MAP)
    delAttr(editor, 'frozenselection')

def FreezeClick(m):
    editor = mapeditor(SS_MAP)
    editor.frozenselection = 1


same = quarkx.setupsubset(SS_GENERAL,"HotKeys")['Same Type']
collapse = quarkx.setupsubset(SS_GENERAL,"HotKeys")['Collapse Tree']

def parentClick(m,editor=None):
    editor, sel = getEditorSelection(editor)
    if sel is None: return
    parent = sel.treeparent
    if parent.name!="worldspawn:b":
        explorer = editor.layout.explorer
        explorer.uniquesel = parent
        if quarkx.keydown(collapse)!=1:
            #
            # Rigamarole to expand the treeview
            #
            Spec1 = qmenu.item("", mapmenus.set_mpp_page, "")
            Spec1.page = 0
            mapmenus.set_mpp_page(Spec1) 
            explorer.expand(parent,0)


def childClick(m, editor=None):
    editor, sel = getEditorSelection(editor)
    if sel is None:
        if editor is None: return
        sel = editor.Root
    if sel.subitems == []: return
    explorer = editor.layout.explorer
    explorer.uniquesel = sel.subitems[0]
    #
    # Rigamarole to expand the treeview
    #
    Spec1 = qmenu.item("", mapmenus.set_mpp_page, "")
    Spec1.page = 0
    mapmenus.set_mpp_page(Spec1) 
    explorer.expand(sel)

def getNext(obj):
    parent = obj.treeparent
    if parent is None:
        return
    next = obj.nextingroup()
    if next is None:
        next=parent.subitems[0]
    return next
    
def getPrevious(obj):
    parent=obj.treeparent
    if parent is None: return
    index = parent.subitems.index(obj)
    if index>0:
        prev = parent.subitem(index-1)
    else:
        prev = parent.subitem(len(parent.subitems)-1)
    return prev
    
def nextClick(m,editor=None):
    editor, sel = getEditorSelection(editor)
    if sel is None: return
    successor = m.succ(sel)
    if successor is None:
        return
    same = quarkx.setupsubset(SS_GENERAL,"HotKeys")['Same Type']

    if quarkx.keydown(same)==1:
        while successor.type!=sel.type:
            successor = m.succ(successor)
    editor.layout.explorer.uniquesel=successor


same = quarkx.setupsubset(SS_GENERAL,"HotKeys")['Same Type']

collapse = quarkx.setupsubset(SS_GENERAL,"HotKeys")['Collapse Tree']

removeItem = qmenu.item("&Cancel Selections", EscClick, "|Cancel Selections:\n\n'Cancel Selections', or by pressing its HotKey, will unselect all objects that are currently selected, even frozen ones, and you are sent back to the 1st page, the treeview, if you are not already there.|intro.mapeditor.menu.html#selectionmenu")

makedetail = qmenu.item("Make &Detail", DetailClick, "|Make Detail:\n\n'Make Detail', or by pressing its HotKey, will set the texture flag for the selected items to 'detail' so as to be ignored during the bsp file build to reduce the size of that game file.\n\nYou can select any poly, face, side or combinaition.Once you have selected them hold the Alt key and press the D key to set all of their detail flags to active. If you still have them selected and press the Alt+D keys a second time, it will deactivate their detail flags, making it a toggle switch type function. Also, if you have a brush with just one or two faces already set for detail then by selecting the brush and using the Alt+D hot key, it will invert their settings. The detail face(s) will become inactive and all the others will be set to detail.|intro.mapeditor.menu.html#selectionmenu")

parentItem = qmenu.item("Select &Parent", parentClick, "|Select Parent:\n\n  The Parent is collapsed in the treeview unless '%s' is depressed.|intro.mapeditor.menu.html#selectionmenu"%collapse)

childItem = qmenu.item("Select &Child", childClick, "|Select Child:\n\nSelects first child.|intro.mapeditor.menu.html#selectionmenu")

nextItem = qmenu.item("Select &Next", nextClick, "|Select Next:\n\nThis selects the next item in the group.\n\nCycling - Depress '%s' to constrain your selection to the next item of the same type.|intro.mapeditor.menu.html#selectionmenu"%same)

prevItem = qmenu.item("Select Pre&vious", nextClick, "|Select Previous:\n\nSelects the previous item in the group.\n\nCycling - Depress '%s' to constrain your selection to the next item of the same type.|intro.mapeditor.menu.html#selectionmenu"%same)
nextItem.succ = getNext
prevItem.succ = getPrevious

freezetext = "|Freeze/Unfreeze Selection:\n\nIf the selection is 'frozen', then clicking in the map view will not change it unless the ALT key is depressed, which also freezes to the new selection.\n\nOther methods of changing the selection, such as the arrow keys in the treeview, will also freeze to the new selection, but clearing with ESC or choosing the menu 'Cancel Selections' function will unfreeze as well as clear it.|intro.mapeditor.menu.html#selectionmenu"

unfreezeItem = qmenu.item("Unfreeze Selection", UnfreezeClick, freezetext)

freezeItem = qmenu.item("Freeze Selection", FreezeClick, freezetext)

#
# Global variables to update from plug-ins.
#

items = [removeItem, makedetail, parentItem, childItem, nextItem, prevItem, freezeItem, unfreezeItem]
shortcuts = {}

def onclick(menu):
    editor=mapeditor()
    removeItem.state=makedetail.state=parentItem.state=childItem.state=qmenu.disabled
    nextItem.state=prevItem.state=freezeItem.state=unfreezeItem.state=qmenu.disabled
    if editor is not None:
        uniquesel = editor.layout.explorer.uniquesel 
        if uniquesel is not None:
            removeItem.state=makedetail.state=nextItem.state=prevItem.state=qmenu.normal
            if len(uniquesel.subitems)>0:
                childItem.state = qmenu.normal
            if uniquesel.treeparent is not None:
                parentItem.state=qmenu.normal
            if getAttr(editor,'frozenselection') is None:
                freezeItem.state=qmenu.normal
            else:
                unfreezeItem.state=qmenu.normal
#        sellist = editor.layout.explorer.sellist
#        if sellist is not None:
#            makedetail.state=qmenu.normal
#        else:
#            makedetail.state=qmenu.disabled

def SelectionMenu():
    "The Selection menu, with its shortcuts."

    MapHotKeyList("Cancel Selections", removeItem, shortcuts)
    MapHotKeyList("Select Parent", parentItem, shortcuts)
    MapHotKeyList("Select Child", childItem, shortcuts)
    MapHotKeyList("Select Next", nextItem, shortcuts)
    MapHotKeyList("Select Previous", prevItem, shortcuts)
    MapHotKeyList("Freeze Selection", freezeItem, shortcuts)
    MapHotKeyList("Unfreeze Selection", unfreezeItem, shortcuts)
    MapHotKeyList("Make Detail", makedetail, shortcuts)

    return qmenu.popup("Selectio&n", items, onclick), shortcuts


# $Log: mapselection.py,v $
# Revision 1.17  2005/10/15 00:47:57  cdunde
# To reinstate headers and history
#
# Revision 1.14  2004/01/06 01:25:59  cdunde
# To add Make Detail function and HotKeys by Decker-cdunde
#
# Revision 1.13  2003/03/27 08:56:28  cdunde
# Update by tiglari to fix runtime and other errors.
#
# Revision 1.12  2003/03/26 03:21:31  cdunde
# To fix runtime error and gray out all menu items if no selection is made.
#
# Revision 1.11  2003/03/25 10:16:52  tiglari
# re-fix enablement bugs
#
# Revision 1.10  2003/03/25 09:56:49  cdunde
# To correct conflict and add infobase links and update
#
# Revision 1.9  2003/03/25 08:28:27  tiglari
# fix enabler and select parent logic
#
# Revision 1.8  2003/02/09 06:11:01  cdunde
# Discription update and HotKey name change
#
# Revision 1.7  2003/02/08 07:37:25  cdunde
# To reduce Cancel selection to a one click function
#
# Revision 1.5  2002/05/13 10:35:57  tiglari
# support frozen selections (don't change until another frozen selection is made,
# or they are cancelled with ESC or unfreeze selection)
#
# Revision 1.4  2001/05/04 06:36:53  tiglari
# Accelerators added to selection menu
#
# Revision 1.3  2001/05/03 05:35:17  tiglari
# fixed selection menu crash bug (failure to test for 'is not None')
#
# Revision 1.2  2001/04/30 10:57:42  tiglari
# added child, key mods for next/prev of same type, treeview control
#
# Revision 1.1  2001/04/28 02:23:12  tiglari
# initial commit
#
#
#