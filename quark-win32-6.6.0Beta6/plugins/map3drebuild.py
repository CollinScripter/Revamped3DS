"""   QuArK  -  Quake Army Knife

Plug-in which rebuild all views.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/map3drebuild.py,v 1.6 2008/02/22 09:52:22 danielpharos Exp $

Info = {
   "plug-in":       "Rebuild 3D views",
   "desc":          "Rebuilds 3D view to try and clear lockups",
   "date":          "February 12 2004",
   "author":        "cdunde",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6" }


import quarkpy.mapoptions
from quarkpy.qutils import *


Rebuild3Ds = quarkpy.mapoptions.toggleitem("&Rebuild 3D views", "Rebuild3D", (1,1),
      hint="|Rebuild 3D views:\n\nThis rebuilds the 3D views (actually all views) in case of a lockup. You may have to do this a few times to clear the views up.\n\nThe easiest way is to just push the HotKey 'Tab' untill the views unlock and clear up.|intro.mapeditor.menu.html#optionsmenu")

quarkpy.mapoptions.items.append(Rebuild3Ds)
for menitem, keytag in [(Rebuild3Ds, "Rebuild3D")]:
    MapHotKey(keytag,menitem,quarkpy.mapoptions)


def newfinishdrawing(editor, view, oldfinish=quarkpy.mapeditor.MapEditor.finishdrawing):

    oldfinish(editor, view)
  #  if not MapOption("Rebuild3D"):return

quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing


# ----------- REVISION HISTORY ------------
#
#$Log: map3drebuild.py,v $
#Revision 1.6  2008/02/22 09:52:22  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.5  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.2  2005/03/19 00:36:33  cdunde
#Took out return item to make more responsive
#
#Revision 1.1  2004/02/12 18:17:39  cdunde
#To add 'Tab' HotKey function to rebuild all views and clear lockups
#
#