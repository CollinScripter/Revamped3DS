"""   QuArK  -  Quake Army Knife

Plug-in which rebuild all views.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mdl3drebuild.py,v 1.7 2008/02/22 09:52:21 danielpharos Exp $

Info = {
   "plug-in":       "Rebuild 3D views in Model Editor",
   "desc":          "Rebuilds 3D view to try and clear lockups in Model Editor",
   "date":          "August 30 2005",
   "author":        "cdunde",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6" }


import quarkpy.mdloptions
from quarkpy.qutils import *


Rebuild3Ds = quarkpy.mdloptions.toggleitem("&Rebuild 3D views", "Rebuild3D", (1,1),
      hint="|Rebuild 3D views in Model Editor:\n\nThis rebuilds the 3D views (actually all views) in the Model Editor in case of a lockup. You may have to do this a few times to clear the views up.\n\nThe easiest way is to just push the HotKey 'Tab' until the views unlock and clear up.|intro.modeleditor.menu.html#optionsmenu")

quarkpy.mdloptions.items.append(Rebuild3Ds)
for menitem, keytag in [(Rebuild3Ds, "Rebuild3D")]:
    MapHotKey(keytag,menitem,quarkpy.mdloptions)


def newfinishdrawing(editor, view, oldfinish=quarkpy.mdleditor.ModelEditor.finishdrawing):

    oldfinish(editor, view)
  #  if not MapOption("Rebuild3D"):return

quarkpy.mdleditor.ModelEditor.finishdrawing = newfinishdrawing


# ----------- REVISION HISTORY ------------
#
#$Log: mdl3drebuild.py,v $
#Revision 1.7  2008/02/22 09:52:21  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.6  2006/11/30 01:17:48  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.5  2006/11/29 06:58:35  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.4.2.1  2006/11/28 00:55:35  cdunde
#Started a new Model Editor Infobase section and their direct function links from the Model Editor.
#
#Revision 1.4  2005/10/15 00:51:56  cdunde
#To reinstate headers and history
#
#Revision 1.1  2005/08/31 05:37:32  cdunde
#To add Tab key 3D view rebuild function for Model Editor.
#
#