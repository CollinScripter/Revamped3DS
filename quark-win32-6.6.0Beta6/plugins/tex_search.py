# QuArK  -  Quake Army Knife
#
# Copyright (C) 2001 The Quark Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/tex_search.py,v 1.9 2007/12/09 23:36:36 danielpharos Exp $

Info = {
   "plug-in":       "Texture Search",
   "desc":          "searches textures",
   "date":          "16 June 2001",
   "author":        "Andy",
   "author e-mail": "personx@planetquake.com",
   "quark":         "Version 6.3"
}

import quarkx
import quarkpy.mapsearch
import quarkpy.qmacro
import quarkpy.qtoolbar
from quarkpy import qutils
from quarkpy.maputils import *

def tex_search(s):
    s = s.upper()
    tbxs = quarkx.findtoolboxes("Texture Browser...");
    result = []
    for tbx in tbxs:
        txlist = tbx[1].findallsubitems("", ".wl")
        for tx in txlist:
            n = tx.name.upper()
            if (n.find(s) != -1):
                result = result + [tx]
    return result

def findsearchtoolbox():
    tbx_list = quarkx.findtoolboxes("Texture Browser...")
    for tbx in tbx_list:
        if (tbx[1].name == "Searched.qtxfolder") and (tbx[1]["SearchBox"]=="1"):
            return tbx[1].findname("Searched Textures.txlist")
    return None

def tex_doit(s):
    tbx = findsearchtoolbox()
    if tbx is None:
        raise "Searched.qtxfolder not found!"
    for tex in tbx.subitems:
        tbx.removeitem(tex)
    tex = tex_search(s)
    for t in tex:
        x = t.copy();
        x.flags = x.flags | qutils.OF_TVSUBITEM
        tbx.appenditem(x)
    quarkx.opentoolbox("Texture Browser...", None)

class TextureSearchDlg(quarkpy.qmacro.dialogbox):
    # Dialog layout
    size = (290, 117)
    dfsep = 0.4     # separation at 40% between labels and edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE

    dlgdef = """ {
                     Style = "15"
                     Caption = "Search for Texture"
                     searchfor: =
                     {
                         Txt = "Search for:"
                         Typ = "E"
                         Hint= "Enter full or partial texture name" $0D " Results appear in 'searched textures' folder at top of toolbox"
                     }
                     Sep: = {Typ="S" Txt=" "}
                     Search:py = {Txt=""}
                     close:py = {Txt=""}
                 } """

    def __init__(self, form):
        # Create the data source
        src = quarkx.newobj(":")
        src["searchfor"] = ""

        # Create the dialog form and the buttons
        quarkpy.qmacro.dialogbox.__init__(self, form, src,
            close = quarkpy.qtoolbar.button(self.close,"close this box",ico_editor, 0,"Close"),
            Search = quarkpy.qtoolbar.button(self.doSearch,"Search",ico_editor, 3, "Search")
        )

    def doSearch(self, btn):
        quarkx.globalaccept()
        tex = self.src["searchfor"]
        if (tex == "")or(tex == None):
           quarkx.msgbox("Search text must not be blank!", qutils.MT_ERROR, qutils.MB_OK)
           return
        tex_doit(tex)
        self.close(btn)
        return

def openbox():
    f = quarkx.newform("temp")
    TextureSearchDlg(f)

# $Log: tex_search.py,v $
# Revision 1.9  2007/12/09 23:36:36  danielpharos
# Fixed a typo.
#
# Revision 1.8  2005/10/15 00:51:56  cdunde
# To reinstate headers and history
#
# Revision 1.5  2003/12/17 13:58:59  peter-b
# - Rewrote defines for setting Python version
# - Removed back-compatibility with Python 1.5
# - Removed reliance on external string library from Python scripts
#
# Revision 1.4  2002/04/07 12:46:06  decker_dk
# Pretty separator.
#
# Revision 1.3  2001/06/19 20:59:03  aiv
# added cvs headers + small bug fix
#
