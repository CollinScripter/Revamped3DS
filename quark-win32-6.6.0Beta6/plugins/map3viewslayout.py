"""   QuArK  -  Quake Army Knife

Plug-in which define the Classical screen layout.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/map3viewslayout.py,v 1.8 2006/11/30 01:17:48 cdunde Exp $



Info = {
   "plug-in":       "3-Views Layout",
   "desc":          "QuArK's 3-views Screen Layout.",
   "date":          "23 nov 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.2" }


from quarkpy.mapmgr import *


#
# The 3-views Layout is implemented as a subclass of the base class MapLayout.
#

class ThreeViewsLayout(MapLayout):
    "The 3-views QuArK layout."

    shortname = "3 views"

    def buildscreen(self, form):

        #
        # We put the standard left panel first.
        #

        self.bs_leftpanel(form)

        #
        # Divide the main panel into two sections.
        # horizontally, 1 section;
        # vertically, 2 sections split at 40% of the height
        #  (use "-0.4" instead of "0.4" to disable user resizing)
        #

        form.mainpanel.sections = ((), (0.4,))

        #
        # Create the XY view in the section (0,1), i.e. down.
        #

        self.ViewXY = form.mainpanel.newmapview()
        self.ViewXY.section = (0,1)
        self.ViewXY.viewtype="editor"

        #
        # Create a panel in the top section.
        #

        self.threeviews_toppanel = form.mainpanel.newpanel()
        self.threeviews_toppanel.sections = ((0.65,), ())

        #
        # Create the 3D and XZ views
        #

        self.ViewXZ = self.threeviews_toppanel.newmapview()
        self.ViewXZ.viewtype="editor"
        self.View3D = self.threeviews_toppanel.newmapview()
        self.View3D.section = (1,0)
        self.View3D.viewtype="editor"

        #
        # Put these three views in the view lists.
        #

        self.views[:] = [self.ViewXY, self.ViewXZ, self.View3D]
        self.baseviews = self.views[:]

        #
        # Setup initial display parameters.
        #

        scale = 0.25   # default value

        self.ViewXY.info = {
          "type": "XY",     # XY view
          "angle": 0.0,     # compass angle
          "scale": scale,   # scale
          "vangle": 0.0}    # vertical angle

        self.ViewXZ.info = {
          "type": "XZ",     # XZ view
          "angle": 0.0,
          "scale": scale,
          "vangle": 0.0}

        self.View3D.info = {
          "type": "3D",     # 3D view
          "viewname": "editors3Dview"}

        #
        # Link the horizontal position of the XZ view to that of the
        # XY view, and remove the horizontal scroll bar of the XZ view.
        #

        self.sblinks.append((0, self.ViewXZ, 0, self.ViewXY))
        self.ViewXY.flags = self.ViewXY.flags &~ MV_HSCROLLBAR


    #
    # The following function is called when the configuration changed.
    # We show or hide the red lines here.
    #

    def setupchanged(self, level):

        #
        # First call the inherited "setupchanged".
        #

        MapLayout.setupchanged(self, level)


        #
        # Read the old flags and set both red lines by default.
        #

        flagsXY = self.ViewXY.flags | MV_TOPREDLINE | MV_BOTTOMREDLINE
        flagsXZ = self.ViewXZ.flags | MV_TOPREDLINE | MV_BOTTOMREDLINE

        #
        # Remove the 2nd red line if required.
        #

        if not MapOption("RedLines2"):
            flagsXY = flagsXY &~ MV_TOPREDLINE
            flagsXZ = flagsXZ &~ MV_BOTTOMREDLINE

        #
        # Update the flags.
        #

        self.ViewXY.flags = flagsXY
        self.ViewXZ.flags = flagsXZ



    #
    # The following function is called to compute the limits of
    # the visible (non-grayed-out) areas for each map view.
    #

    def setupdepth(self, view):

        #
        # First check the "view" parameter.
        #

        if (view is not self.ViewXY) and (view is not self.ViewXZ):
            return

        #
        # To compute the visible areas for the XY view, we
        # get the rectangular area (in pixels) of the XZ view.
        #

        x1,y1,x2,y2 = self.ViewXZ.redlinesrect

        #
        # The line below does this :
        #  * take a corner of the above rectangle
        #  * compute the 3D coordinates of any point above this corner
        # This gives a 3D point that is at the top limit of the visible area for the XY view.
        #  * project this 3D point on the XY view
        #  * keep only the z coordinate (i.e. the depth) of this projection
        # This gives the depth of the top limit, which is what we wanted.
        #
        # The second line does the same for the other corner, which gives
        # the bottom limit of the visible area.
        #

        xydepth = (self.ViewXY.proj(self.ViewXZ.space(x1, y1, 0.0)).z,
                   self.ViewXY.proj(self.ViewXZ.space(x2, y2, 0.0)).z)

        #
        # Do it again for the XZ view...
        #

        x1,y1,x2,y2 = self.ViewXY.redlinesrect
        xzdepth = (self.ViewXZ.proj(self.ViewXY.space(x2, y2, 0.0)).z,
                   self.ViewXZ.proj(self.ViewXY.space(x1, y1, 0.0)).z)

        #
        # Depending on the draw mode, items may or may not be grayed
        # out. If they are, we must redraw a view when the other one
        # is scrolled, in case objects came in or out of view. This
        # is done by calling "setdepth". Otherwise, we directly set
        # the map view's "depth" attribute, which doesn't redraw the
        # view.
        #

        redraw = self.editor.drawmode & DM_MASKOOV

        if redraw and (view is not self.ViewXY):
            self.ViewXY.setdepth(xydepth)
        else:
            self.ViewXY.depth = xydepth

        if redraw and (view is not self.ViewXZ):
            self.ViewXZ.setdepth(xzdepth)
        else:
            self.ViewXZ.depth = xzdepth


    #
    # Functions to read and store the layout (window positions,...)
    # in the Setup.
    #

    def readconfig(self, config):
        MapLayout.readconfig(self, config)
        vsec = config["hvsec"]
        if type(vsec)==type(()) and len(vsec)==2:
            self.editor.form.mainpanel.sections = ((), vsec[:1])
            self.threeviews_toppanel.sections = (vsec[1:], ())

    def writeconfig(self, config):
        MapLayout.writeconfig(self, config)
        hsec, vsec = self.editor.form.mainpanel.sections
        hsec2, vsec2 = self.threeviews_toppanel.sections
        config["hvsec"] = vsec + hsec2



#
# Register the new layout.
#

LayoutsList.append(ThreeViewsLayout)


# ----------- REVISION HISTORY ------------
#
#
# $Log: map3viewslayout.py,v $
# Revision 1.8  2006/11/30 01:17:48  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.7  2006/11/29 06:58:36  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.6.2.5  2006/11/01 22:22:42  danielpharos
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