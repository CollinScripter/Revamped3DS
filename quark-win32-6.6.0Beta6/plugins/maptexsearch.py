# QuArK  -  Quake Army Knife
#
# Copyright (C) 2001 The Quark Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/maptexsearch.py,v 1.7 2005/10/15 00:51:56 cdunde Exp $

Info = {
   "plug-in":       "Texture Search",
   "desc":          "searches textures",
   "date":          "16 June 2001",
   "author":        "Andy",
   "author e-mail": "personx@planetquake.com",
   "quark":         "Version 6.3"
}

import quarkpy.mapsearch
import tex_search
import quarkx

def TextureSearchClick(m):
    # Function to start the dialog
    tex_search.TextureSearchDlg(quarkx.clickform)

quarkpy.mapsearch.items.append(quarkpy.qmenu.item("&Search for Texture...", TextureSearchClick, "|Search for Texture:\n\nThis function will search for the texture you specify.", "intro.mapeditor.menu.html#searchmenu"))

# $Log: maptexsearch.py,v $
# Revision 1.7  2005/10/15 00:51:56  cdunde
# To reinstate headers and history
#
# Revision 1.4  2003/03/21 05:47:45  cdunde
# Update infobase and add links
#
# Revision 1.3  2002/08/09 10:03:53  decker_dk
# A minor correction. Appended an ellipsis ("...") to the menu-item, to indicate that
# additional action is required, in the dialog-box which pops up, when this menu-item
# is activated.
#
# Revision 1.2  2001/06/19 20:59:03  aiv
# added cvs headers + small bug fix
#
