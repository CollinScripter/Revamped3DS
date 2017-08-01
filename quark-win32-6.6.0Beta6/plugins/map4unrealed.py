"""   QuArK  -  Quake Army Knife

Plug-in which define the 4-views screen layouts.
"""
#
# Copyright (C) 2001 Andy Vincent
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#
# $Header: /cvsroot/quark/runtime/plugins/map4unrealed.py,v 1.4 2005/10/15 00:49:51 cdunde Exp $


Info = {
   "plug-in":       "4-Views Layout (UnrealEd Style)",
   "desc":          "4-views Screen Layouts. (UnrealEd Style)",
   "date":          "2 Feb 2001",
   "author":        "Andy Vincent",
   "author e-mail": "andyvinc@hotmail.com",
   "quark":         "Version 6.2" }


from quarkpy.mapmgr import *
from plugins.map4viewslayout import FourViewsLayout

class FourViewsLayoutUEd(FourViewsLayout):

    shortname = "4 views (UnrealEd Style)"

    def buildscreen(self, form):

        #
        # Build the base.
        #

        self.buildbase(form)

        #
        # Divide the main panel into 4 sections.
        # horizontally, 2 sections split at 45% of the width
        # vertically, 2 sections split at 55% of the height
        #

        form.mainpanel.sections = ((0.45, ), (0.55,))

        #
        # Put the XY view in the section (0,0) top-left
        #

        self.ViewXY.section = (0,0)

        #
        # Put the XZ view in the section (0,1) top-right
        #

        self.ViewXZ.section = (1,0)

        #
        # Put the YZ view in the section (1,1) bottom-right
        #

        self.ViewYZ.section = (1,1)

        #
        # The 3D view is in the section (1,0) bottom-left
        #

        self.View3D.section = (0,1)

        #
        # Link the horizontal position of the XZ view to that of the
        # XY view, and the vertical position of the XZ and YZ views,
        # and remove the extra scroll bars.
        #

        self.sblinks.append((0, self.ViewXZ, 0, self.ViewXY))
        self.sblinks.append((1, self.ViewXZ, 1, self.ViewYZ))
        self.sblinks.append((1, self.ViewXY, 0, self.ViewYZ))
        self.ViewYZ.flags = self.ViewYZ.flags &~ (MV_HSCROLLBAR | MV_VSCROLLBAR)
        self.ViewXY.flags = self.ViewXY.flags &~ MV_HSCROLLBAR
        
LayoutsList.append(FourViewsLayoutUEd)

# ----------- REVISION HISTORY ------------
# $Log: map4unrealed.py,v $
# Revision 1.4  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.1  2001/02/05 20:09:11  aiv
# Initial Release
#
#
