"""   QuArK  -  Quake Army Knife

Tag commands toolbar
"""
#
# Copyright (C) 1996-03 The QuArK Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapselecttoolbar.py,v 1.9 2013/03/17 14:15:09 danielpharos Exp $

Info = {
   "plug-in":       "Selection Commands Toolbar",
   "desc":          "Toolbar for selection commands",
   "date":          "July 12 2003",
   "author":        "cdunde",
   "author e-mail": "cdunde1@attbi.com",
   "quark":         "Version 6" }


import quarkx
from quarkpy.maputils import *
import quarkpy.mapselection    # need
import mapmadsel               # need


def parentclick(m):
    editor = mapeditor()
    if editor is not None:
        try:
            sides = [m.side]
        except (AttributeError):
            sides = editor.layout.explorer.sellist
        if (len(sides) > 1):
            quarkx.msgbox("You have made\na multiple selection.\n\nYou need to select a single face\nor side for this function to work.", MT_ERROR, MB_OK)
            return
        uniquesel = editor.layout.explorer.uniquesel
        if  uniquesel is not None:
            if uniquesel.treeparent is not None:
                quarkpy.mapselection.parentClick(m)
            else:
                quarkx.msgbox("You have reached the top\nlevel for this function.", MT_INFORMATION, MB_OK)
        else:
            quarkx.msgbox("No selection has been made.\n\nYou must select a single face\nor side for this function to work.", MT_ERROR, MB_OK)


def childclick(m):
    editor = mapeditor()
    if editor is not None:
        try:
            sides = [m.side]
        except (AttributeError):
            sides = editor.layout.explorer.sellist
        if (len(sides) > 1):
            quarkx.msgbox("You have made\na multiple selection.\n\nYou need to select a single group\nor face for this function to work.", MT_ERROR, MB_OK)
            return
        uniquesel = editor.layout.explorer.uniquesel
        if  uniquesel is not None:
            if len(uniquesel.subitems)>0:
                quarkpy.mapselection.childClick(m)
            else:
                quarkx.msgbox("You have reached the lowest\nlevel for this function.", MT_INFORMATION, MB_OK)
        else:
            quarkx.msgbox("No selection has been made.\n\nYou must select a single group\nor face for this function to work.", MT_ERROR, MB_OK)


def getnext(m):
    editor = mapeditor()
    editor, sel = quarkpy.mapselection.getEditorSelection(editor=None)
    if editor is not None:
        try:
            sides = [m.side]
        except (AttributeError):
            sides = editor.layout.explorer.sellist
        if (len(sides) > 1):
            quarkx.msgbox("You have made\na multiple selection.\n\nYou need to select a single group, face\nor side for this function to work.", MT_ERROR, MB_OK)
            return
        uniquesel = editor.layout.explorer.uniquesel
        if  uniquesel is not None:
            quarkpy.mapselection.nextClick(m)
        else:
            quarkx.msgbox("No selection has been made.\n\nYou need to select a single group, face\nor side for this function to work.", MT_ERROR, MB_OK)


def freezeclick(m):
    editor = mapeditor()
    if editor is not None:
        try:
            sides = [m.side]
        except (AttributeError):
            sides = editor.layout.explorer.sellist
        if (len(sides) < 1):
            quarkx.msgbox("No selection has been made\nto Freeze.", MT_ERROR, MB_OK)
            return
        else:
            quarkpy.mapselection.FreezeClick(m)


def InvertFaceSelClick(m):
    editor = mapeditor()
    if editor is not None:
        sides = editor.layout.explorer.sellist
        if (len(sides) < 1):
            quarkx.msgbox("No face(s) has been selected\nto Invert.", MT_ERROR, MB_OK)
            return
        if len(sides) > 0:
            sel = sides[0]
            try:
                item = m.obj
                if item.type == ":f":
                    sel = item
            except (AttributeError) :
                if sel.type == ":f":
                    mapmadsel.invertFaceSelClick(m)
                    return
                else:
                    quarkx.msgbox("You can only select\nfaces to Invert.", MT_ERROR, MB_OK)
                    return


def extendSelClick(m):
    editor = mapeditor()
    if editor is not None:
        selection = editor.layout.explorer.sellist
        if len(selection) == 1:
            sel = selection[0]
            try:
                item = m.obj
                if item.type == ":f":
                    sel = item
            except (AttributeError) :
                if sel.type == ":f":
                    mapmadsel.ExtendSelClick(m)
                else:
                    quarkx.msgbox("You can only select a\nsingle face to Extend from.", MT_ERROR, MB_OK)
                return
        if len(selection) < 1:
            quarkx.msgbox("No face has been selected\nto Extend from.", MT_ERROR, MB_OK)
        if len(selection) > 1:
            quarkx.msgbox("You can only select a\nsingle face to Extend from.", MT_ERROR, MB_OK)
            return


def BrowseSelClick(m):
    editor = mapeditor()
    if editor is None: return
    sellist = editor.layout.explorer.sellist
    if len(sellist) > 1:
        mapmadsel.browseListFunc(editor,sellist)
    else:
        quarkx.msgbox("You must select more than one item\nto look at for this function to work.", MT_ERROR, MB_OK)


def unrestrictClick(m):
    editor = mapeditor()
    if editor is None: return
    editor.restrictor = editor.layout.explorer.uniquesel
    if editor.restrictor is not None:
        mapmadsel.UnrestrictClick(m)
    else:
        quarkx.msgbox("No selection made.", MT_ERROR, MB_OK)


def restSelClick(m):
    editor = mapeditor()
    if editor is None: return
    editor.restrictor = editor.layout.explorer.uniquesel
    if editor.restrictor is not None:
        mapmadsel.RestSelClick(m)
    else:
        quarkx.msgbox("No selection made.", MT_ERROR, MB_OK)


def zoomToMe(m):
    editor = mapeditor()
    m.object = editor.layout.explorer.uniquesel
    if m.object is None:
        quarkx.msgbox("You must select a single item\nor group to use this function.", MT_ERROR, MB_OK)
        return
    else:
        mapmadsel.ZoomToMe(m)


def stashMe(m):
    editor = mapeditor()
    if editor is None: return
    m.object = editor.layout.explorer.uniquesel
    if m.object is None:
        quarkx.msgbox("You must select a single item\nto use this function.", MT_ERROR, MB_OK)
        return
    else:
        mapmadsel.StashMe(m)
        quarkx.msgbox("The selected item\nhas been marked.", MT_INFORMATION, MB_OK)


def clearMarkClick(m):
    editor = mapeditor()
    if editor is None: return
    mapmadsel.ClearMarkClick(m)
    quarkx.msgbox("All items have\nbeen unmarked.", MT_INFORMATION, MB_OK)



# This defines and builds the toolbar.

class SelectModesBar(ToolBar):
    "The Select Commands Tool Palette."

    Caption = "Select Tool Palette"
    DefaultPos = ((0, 0, 0, 0), 'topdock', 2, 1, 1)

    def buildbuttons(self, layout):
        if not ico_dict.has_key('ico_select'):
            ico_dict['ico_select']=LoadIconSet1("select", 1.0)
        icons = ico_dict['ico_select']


# See the quarkpy/qtoolbar.py file for the class button: definition
# which gives the layout for each of the  " "  attribut
# assignments below.

# Now we can assign an opperation to each buttons attributes
# which are "onclick" (what function to perform),
# "hint" (what to display for the flyover and F1 popup window text),
# "iconlist" (the icon.bmp file to use),
# "iconindex" (a number attribute, which is the place holder
# for each icon in the icon.bmp file.
# and "infobaselink" (the infobase HTML page address and ancor,
# which is a locator for a spacific place on the page)
 

        btn0 = qtoolbar.button(quarkpy.mapselection.EscClick, "Cancel Selections||Cancel Selections:\n\n'Cancel Selections', or by pressing its HotKey, will unselect all objects that are currently selected, even frozen ones, and you are sent back to the 1st page, the treeview, if you are not already there.", icons, 0, infobaselink="intro.mapeditor.menu.html#selectionmenu")


        btn1 = qtoolbar.button(parentclick, "Select Parent||Select Parent:\n\n  The Parent is collapsed in the treeview unless 'S' is depressed.", icons,1, infobaselink="intro.mapeditor.menu.html#selectionmenu")


        btn2 = qtoolbar.button(childclick, "Select Child||Select Child:\n\nSelects first child.", icons, 2, infobaselink="intro.mapeditor.menu.html#selectionmenu")


        btn3 = qtoolbar.button(getnext, "Select Next||Select Next:\n\nThis selects the next item in the group.\n\nCycling - Depress 'S' to constrain your selection to the next item of the same type.", icons, 3, infobaselink="intro.mapeditor.menu.html#selectionmenu")


        btn4 = qtoolbar.button(getnext, "Select Previous||Select Previous:\n\nSelects the previous item in the group.\n\nCycling - Depress 'S' to constrain your selection to the next item of the same type.", icons, 4, infobaselink="intro.mapeditor.menu.html#selectionmenu")

        btn3.succ = quarkpy.mapselection.getNext
        btn4.succ = quarkpy.mapselection.getPrevious

        btn5 = qtoolbar.button(freezeclick, "Freeze Selection||Freeze Selection:\n\nIf the selection is 'frozen', then clicking in the map view will not change it unless the ALT key is depressed, which also freezes to the new selection.\n\nOther methods of changing the selection, such as the arrow keys in the treeview, will also freeze to the new selection, but clearing with ESC or choosing the menu 'Cancel Selections' function will unfreeze as well as clear it.", icons, 5, infobaselink="intro.mapeditor.menu.html#selectionmenu")


        btn6 = qtoolbar.button(quarkpy.mapselection.UnfreezeClick, "Unfreeze Selection||Unfreeze Selection:\n\nIf the selection is 'frozen', then clicking in the map view will not change it unless the ALT key is depressed, which also freezes to the new selection.\n\nOther methods of changing the selection, such as the arrow keys in the treeview, will also freeze to the new selection, but clearing with ESC or choosing the menu 'Cancel Selections' function will unfreeze as well as clear it.", icons, 6, infobaselink="intro.mapeditor.menu.html#selectionmenu")


        btn7 = qtoolbar.button(InvertFaceSelClick, "Invert Face Selection||Invert Face Selection:\n\nThis is for polys containing faces that are currently selected, deselect these and select the other, currently unselected, faces.", icons, 7, infobaselink="intro.mapeditor.menu.html#invertface")


        btn8 = qtoolbar.button(extendSelClick, "Extend Selection from Face||Extend Selection from Face:\n\nExtends the selection from this face to all the faces that make a single unbroken sheet with this one.\n\nSo you can for example move the bottom of a ceiling brush, and have the tops of the wall brushes follow, if they're on the same plane as the bottom of the ceiling.\n\nYou can also Link the selected faces, so that all of them can be snapped to the position of one of them with one click.", icons, 8, infobaselink="intro.mapeditor.menu.html#invertface")


        btn9 = qtoolbar.button(BrowseSelClick, "Browse Multiple Selection||Browse Multiple Selection:\n\nMakes a dialog for browsing the selected elements.", icons, 9, infobaselink="intro.mapeditor.menu.html#invertface")


        btn10 = qtoolbar.button(unrestrictClick, "Unrestrict Selection||Unrestrict Selection:\n\nWhen selection is restricted (see the Containing Groups right-mouse menu), clicking on this will unrestrict the selection & restore things to normal.", icons, 10, infobaselink="intro.mapeditor.menu.html#invertface")


        btn11 = qtoolbar.button(restSelClick, "Restrict to Selection||Restrict to Selection:\n\nThis restricts the map editor to working only on what is selected.", icons, 11, infobaselink="intro.mapeditor.menu.html#invertface")


        btn12 = qtoolbar.button(zoomToMe, "Zoom to selection||Zoom to selection:\n\nThis zooms the map 2D views in to the selection(s).\n\nIf there is a 3D view open, it will also look at or zoom to the selection(s) in that view as well.\n\nSee 'Look and Zoom in 3D views' under the 'Options' menu for more detail on how it works with this function.", icons, 12, infobaselink="intro.mapeditor.menu.html#invertface")


        btn13 = qtoolbar.button(stashMe, "Mark selection||Mark selection:\n\nThis command designates the selection as a special element for other (mostly somewhat advanced) commands, such as 'Lift face to marked group' on the face RMB, or the 'Reorganize Tree' commands on various map object RMB's.", icons, 13, infobaselink="intro.mapeditor.menu.html#invertface")


        btn14 = qtoolbar.button(clearMarkClick, "Clear Mark||Clear Mark:\n\nThis cancels the Mark selection.", icons, 14, infobaselink="intro.mapeditor.menu.html#invertface")


        return [btn0, btn1, btn2, btn3, btn4, btn5, qtoolbar.sep, btn6, btn7, btn8, btn9, btn10, qtoolbar.sep, btn11, btn12, btn13, btn14]


# Now we add this toolbar, to the list of other toolbars,
# in the main Toolbars menu.

# The script below initializes the item "toolbars",
# which is already defined in the file quarkpy/maptools.py
# and sets up the first two items in the standard main Toolbars menu.

# This one is added below them, because all of the files in the
# quarkpy folder are loaded before the files in the plugins folder.

quarkpy.maptools.toolbars["tb_selectmodes"] = SelectModesBar


# ----------- REVISION HISTORY ------------
#
# $Log: mapselecttoolbar.py,v $
# Revision 1.9  2013/03/17 14:15:09  danielpharos
# Fixed a typo.
#
# Revision 1.8  2005/10/15 00:51:24  cdunde
# To reinstate headers and history
#
# Revision 1.5  2005/08/16 04:03:12  cdunde
# Fix toolbar arraignment
#
# Revision 1.4  2003/11/27 08:17:22  cdunde
# To update 3D Zoom to selection feature for faces
#
# Revision 1.3  2003/11/16 08:34:02  cdunde
# To add log
#
#
