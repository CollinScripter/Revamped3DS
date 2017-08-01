"""   QuArK  -  Quake Army Knife

Implementation of "Addons" menu Load Any Map function
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/map1loadanymap.py,v 1.5 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Map1 Load Any Map",
   "desc":          "This Item function allows you to load any map file and is located on the Addons menu>Other Programs category.",
   "date":          "June 7 2003",
   "author":        "cdunde, Decker and others",
   "author e-mail": "cdunde1@attbi.com",
   "quark":         "Version 6.4" }

import quarkpy.mapmenus
from quarkpy.maputils import *


class LoadMapDlg(quarkpy.qmacro.dialogbox):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (400,120)
    dfsep = 0.35
    flags = FWF_KEEPFOCUS
    
    dlgdef = """
        {
        Style = "9"
        Caption = "LoadMap Dialog"

        loadmap: =
        {
        Txt = "Select a map file to load:"
        Typ = "EP"
        DefExt = "map"
        BasePath = "$Game\\tmpQuArK\maps"
        DirSep="/"
        Hint = "Type in the name of the map file (.map file),"$0D
               "preceded with its full path and forward slashes,"$0D
               "(ex. C:/Quake2/tmpQuArK/maps/your.map),"$0D
               "or just use the file browser ... to the right."$0D
        }

        sep: = { Typ="S" Txt=" " }

        close:py = {Txt="" }
        cancel:py = {Txt="" }

        }
        """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, editor, action):

    #
    # General initialization of some local values
    #

        self.editor = editor
        src = quarkx.newobj(":")
        self.src = src
        self.action = action
        self.form = form
        self.src["loadmap"] = None

    #
    # Create the dialog form and the buttons
    #

        quarkpy.qmacro.dialogbox.__init__(self, form, src,
        close = quarkpy.qtoolbar.button(
            self.close,
            "Load the selected map file",
            ico_editor, 3,
            "Load map file"),
        cancel = quarkpy.qtoolbar.button(
            self.cancel,
            "Cancel & close window",
            ico_editor, 0,
            "Cancel"))

    def onclose(self, dlg):
        if self.src is None:
            qmacro.dialogbox.onclose(self, dlg)
            return
        quarkx.globalaccept()
        self.action(self)
        qmacro.dialogbox.onclose(self, dlg)

    def cancel(self, dlg):
        self.src = None 
        qmacro.dialogbox.close(self, dlg)

#        ********** FUNCTION Starts Here **********

def LoadMapClick(m):
    def action(self):
        if self.src["loadmap"] is None:
            quarkx.msgbox("No map file entered, nothing done", MT_ERROR, MB_OK)
            return

        editor = self.editor
        tmpquark = self.src["loadmap"]
        objfile = tmpquark.replace("/", "\\")
        info = quarkx.openfileobj(objfile)
        mygroup = quarkx.newobj('group:g')
        mygroup.copyalldata(info.subitem(0))
        quarkpy.mapbtns.dropitemsnow(editor, [mygroup], 'draw map')

    editor = mapeditor()
    if editor is None: return
    LoadMapDlg(quarkx.clickform,editor,action)



# ----------- REVISION HISTORY ------------
#
#$Log: map1loadanymap.py,v $
#Revision 1.5  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.2  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.1  2003/07/04 20:01:16  cdunde
#To add new Addons main menu item and sub-menus
#
