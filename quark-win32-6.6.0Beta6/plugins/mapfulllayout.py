"""   QuArK  -  Quake Army Knife

Example Plug-in which define a new screen layout.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapfulllayout.py,v 1.8 2006/11/30 01:17:47 cdunde Exp $


Info = {
   "plug-in":       "Full-screen 3D Layout",
   "desc":          "The full-screen 3D wireframe Screen Layout.",
   "date":          "31 oct 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.1" }


from quarkpy.mapmgr import *


#
# See comments in mapclassiclayout.py.
#

class Full3DLayout(MapLayout):
    "The full-screen 3D layout."

    shortname = "Full 3D"

    def buildscreen(self, form):
        self.bs_leftpanel(form)
        self.View3D = form.mainpanel.newmapview()
        self.View3D.viewtype="editor"
        self.views[:] = [self.View3D]
        self.baseviews = self.views[:]
        self.View3D.info = {"type": "3D", "viewname": "editors3Dview"}
        self.View3D.viewmode = "tex"



LayoutsList.append(Full3DLayout)


# ----------- REVISION HISTORY ------------
#
#
# $Log: mapfulllayout.py,v $
# Revision 1.8  2006/11/30 01:17:47  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.7  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.6.2.6  2006/11/04 21:36:22  cdunde
# To add 3DView viewmode of "tex"
#
# Revision 1.6.2.5  2006/11/01 22:22:43  danielpharos
# BackUp 1 November 2006
# Mainly reduce OpenGL memory leak
#
# Revision 1.6  2005/10/17 21:27:35  cdunde
# To add new key word "viewname" to all 3D views for easier
# detection and control of those views and Infobase documentation.
#
# Revision 1.5  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#