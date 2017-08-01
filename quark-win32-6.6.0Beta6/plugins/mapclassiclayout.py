"""   QuArK  -  Quake Army Knife

Plug-in which define the Classical screen layout.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapclassiclayout.py,v 1.7 2006/11/30 01:17:48 cdunde Exp $



Info = {
   "plug-in":       "Classic Layout",
   "desc":          "QuArK's classic 2-views Screen Layout.",
   "date":          "31 oct 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.1" }


from quarkpy.mapmgr import *


#
# The Classic Layout is implemented as a subclass of the base class MapLayout.
#

class ClassicLayout(MapLayout):
    "The classic 2-views QuArK layout."

    shortname = "Classic"

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
        # Create the XZ view in the section (0,0) (it is there by default).
        #

        self.ViewXZ = form.mainpanel.newmapview()
        self.ViewXZ.viewtype="editor"

        #
        # Put these two views in the view lists.
        #

        self.views[:] = [self.ViewXY, self.ViewXZ]
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

        #
        # Link the horizontal position of the XZ view to that of the
        # XY view, and remove the horizontal scroll bar of the XZ view.
        #

        self.sblinks.append((0, self.ViewXY, 0, self.ViewXZ))
        self.ViewXZ.flags = self.ViewXZ.flags &~ MV_HSCROLLBAR


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
        vsec = config["vsec"]
        if type(vsec)==type(()) and len(vsec)==1:
            self.editor.form.mainpanel.sections = ((), vsec)

    def writeconfig(self, config):
        MapLayout.writeconfig(self, config)
        hsec, vsec = self.editor.form.mainpanel.sections
        config["vsec"] = vsec



#
# Register the new layout. (this one is the default one, so add it at the front of the list)
#

LayoutsList.insert(0, ClassicLayout)


# ----------- REVISION HISTORY ------------
#
#
# $Log: mapclassiclayout.py,v $
# Revision 1.7  2006/11/30 01:17:48  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.6  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.5.2.5  2006/11/01 22:22:42  danielpharos
# BackUp 1 November 2006
# Mainly reduce OpenGL memory leak
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