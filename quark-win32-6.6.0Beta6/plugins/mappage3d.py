"""   QuArK  -  Quake Army Knife

Map editor "3D" page on the Multi-Pages-Panel.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mappage3d.py,v 1.11 2006/11/30 01:17:48 cdunde Exp $


Info = {
   "plug-in":       "3D Page",
   "desc":          "Displays the 3D page (bottom left).",
   "date":          "31 oct 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.1" }


import quarkpy.qhandles
from quarkpy.mapmgr import *


class Page3D(MPPage):

    def bs_3Dview(self, panel):
        fp = panel.newpanel()
        # fp.newtoppanel(ico_maped_y,0).newbtnpanel([    ])   # fill me
        self.mppview3d = fp.newmapview()
        self.mppview3d.viewtype="panel"
        quarkpy.qhandles.flat3Dview(self.mppview3d, self.layout, 1)
        setprojmode(self.mppview3d)
        return fp

    def fill3dview(self, reserved):
        list = self.layout.explorer.sellist
        self.mppview3d.invalidate(1)
        scale1, center1 = AutoZoom([self.mppview3d], quarkx.boundingboxof(list))
        if scale1 is not None:
            setviews([self.mppview3d], "scale", scale1)
            self.mppview3d.screencenter = center1
        quarkpy.qhandles.z_recenter(self.mppview3d, list)

    def button(self):
        pagebtn = qtoolbar.button(self.fill3dview, "3D view||3D view:\n\nThis displays a 3D texture view of the selected objects.\n\nSee the infobase for more detail.", ico_dict['ico_maped'], 21, "3D view", infobaselink='intro.mapeditor.dataforms.html#3dview')
        pagebtn.pc = [self.bs_3Dview(self.panel)]
        return pagebtn



# Register this new page
mppages.append(Page3D)


# ----------- REVISION HISTORY ------------
#
#
# $Log: mappage3d.py,v $
# Revision 1.11  2006/11/30 01:17:48  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.10  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.9.2.5  2006/11/01 22:22:42  danielpharos
# BackUp 1 November 2006
# Mainly reduce OpenGL memory leak
#
# Revision 1.9  2005/10/15 00:51:24  cdunde
# To reinstate headers and history
#
# Revision 1.6  2003/07/07 07:17:46  cdunde
# To correct caption exclusion error and hint display
#
# Revision 1.5  2003/03/17 01:48:49  cdunde
# Update hints and add infobase links where needed
#
# Revision 1.4  2001/10/22 10:14:25  tiglari
# live pointer hunt, revise icon loading
#
# Revision 1.3  2001/01/26 19:08:02  decker_dk
# Fix hint-problem introduced by change in [QBaseMgr.PY] bs_multipagespanel
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#
