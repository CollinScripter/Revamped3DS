"""   QuArK  -  Quake Army Knife

The map editor's "Toolbars" menu (to be extended by plug-ins)
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/maptools.py,v 1.12 2008/11/17 19:10:00 danielpharos Exp $


import qmenu
from maputils import *
import qeditor


class DisplayBar(qeditor.ToolBar):
    "The standard Display tool bar."

    Caption = "Display"
    DefaultPos = ((0,0,0,0), "topdock", 0, 0, 1)

    def buildbuttons(self, layout):
        ico_maped=ico_dict['ico_maped']
        gridbtn = qtoolbar.doublebutton(layout.editor.togglegrid, layout.getgridmenu, "Grid||Grid:\n\nThe grid is the pattern of dots on the map that 'snaps' mouse moves. It helps you align polyhedrons and entities. You should always keep it active; otherwise, you could create slightly misaligned polyhedrons with small gaps between them, which is very bad for the game.\n\nThis 'grid' button has two parts : you can click either on the icon and get a menu that lets you select the grid size you like, or you can click on the text itself, which toggles the grid on/off without hiding it. As noted above, be careful when the grid is off.", ico_maped, 7, infobaselink="intro.mapeditor.toolpalettes.display.html#grid")

        gridbtn.caption = "128"  # to determine the button width

        zoombtn = qtoolbar.doublebutton(layout.autozoom1click, getzoommenu, "Choose zoom factor / zoom to fit the level or the selection||Choose zoom factor:\n\nThis button lets you zoom in or out. This button has two parts.\n\nClick on the icon to get a list of common zoom factors, or to enter a custom factor with the keyboard.\n\nClick on the text ('zoom') besides the icon to 'auto-zoom' in and out : the first time you click, the scale is choosen so that you can see the whole level at a glance; the second time you click, the views zoom in on the selected objects.", ico_maped, 14, infobaselink="intro.mapeditor.toolpalettes.display.html#zoom")
        zoombtn.near = 0
        zoombtn.views = layout.views
        zoombtn.caption = "zoom"

        Btn3D = qtoolbar.button(layout.full3Dclick, "3D view||3D view:\n\nThis will take you to a floating 3D-display.", ico_maped, 21, infobaselink="intro.mapeditor.toolpalettes.display.html#3dwindows")

        LinearVBtn = qtoolbar.button(layout.editor.linear1click, "Linear mapping circle on selection||Linear mapping circle on selection:\n\nWhen this button is selected, QuArK always displays a pink circle around the selected objects; otherwise, it only appears if multiple objects are selected.\n\nThis circle and its attached handles let you apply 'linear mappings' on the objects. 'Linear mapping' means any transformation like rotation, enlarging/shrinking, symmetry, or a combination of them all. When you use the rotate, enlarge, shrink, and symmetry buttons of the movement tool palette, you actually apply a linear mapping on the selected objects. This is only interesting to know for a special kind of Duplicators, the one that can apply linear mappings. It means that this kind of Duplicator can create images with any of the previous movement commands applied, for example to create spiral stairs.", ico_maped, 19, infobaselink="intro.mapeditor.toolpalettes.display.html#linear")

        LockViewsBtn = qtoolbar.button(layout.editor.lockviewsclick, "Lock views||Lock views:\n\nThis will cause all of the 2D views to move and zoom together.\n\nWhen this is in the unlocked mode, the 2d views can then be moved and zoomed on individually.\n\nIf the lock is reset then the 2D views will realign themselves.", ico_maped, 28)

        helpbtn = qtoolbar.button(layout.helpbtnclick, "Contextual help||Contextual help:\n\nWill open up your web-browser, and display the QuArK main help page.", ico_maped, 13, infobaselink="intro.mapeditor.toolpalettes.display.html#helpbook")

        layout.buttons.update({"grid": gridbtn, "3D": Btn3D, "linear": LinearVBtn, "lockv": LockViewsBtn})

        return [gridbtn, zoombtn, Btn3D, LinearVBtn, LockViewsBtn, helpbtn]


#
# Initialize "toolbars" with the standard tool bars. Plug-ins can
# register their own toolbars in the "toolbars" dictionnary.
#

import qmovepal
toolbars = {"tb_display": DisplayBar, "tb_movepal": qmovepal.ToolMoveBar}

# ----------- REVISION HISTORY ------------
#
#
#$Log: maptools.py,v $
#Revision 1.12  2008/11/17 19:10:00  danielpharos
#Fixed a typo.
#
#Revision 1.11  2008/08/21 12:11:53  danielpharos
#Fixed an import failure.
#
#Revision 1.10  2006/11/30 01:19:33  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.9  2006/11/29 07:00:26  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.8.2.6  2006/11/01 22:22:42  danielpharos
#BackUp 1 November 2006
#Mainly reduce OpenGL memory leak
#
#Revision 1.8  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.5  2003/03/15 20:42:09  cdunde
#To update hints and add infobase links
#
#Revision 1.4  2003/02/14 03:12:55  cdunde
#To add F1 help popup info
#
#Revision 1.3  2001/10/22 10:24:32  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#