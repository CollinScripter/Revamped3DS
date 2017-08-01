"""   QuArK  -  Quake Army Knife

Mouse drag Object modes
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapobjectmodes.py,v 1.14 2008/09/12 19:08:40 cdunde Exp $



Info = {
   "plug-in":       "Object Drag Modes",
   "desc":          "Creates objects by mouse dragging",
   "date":          "Dec. 1, 2005",
   "author":        "cdunde",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6.5" }


import quarkx
import quarkpy.qtoolbar
import quarkpy.qhandles
from quarkpy.maputils import *
import quarkpy.maptools
import quarkpy.maphandles
import quarkpy.mapbtns
from math import pi, sin, cos, fmod
import mapdragmodes
import quarkpy.qbaseeditor
import quarkpy.dlgclasses
# For hollowing Torus
import quarkpy.mapcommands
import quarkpy.mapentities
import plugins.mapcsg


#py2.4 indicates upgrade change for python 2.4

#
# Additionnal Quick Object Maker modes (other plug-ins may add other Quick Object Maker modes).
#

parent = quarkpy.qhandles.RectangleDragObject


### General def's that can be used by any Dialog ###

def newfinishdrawing(editor, view, oldfinish=quarkpy.mapeditor.MapEditor.finishdrawing):
    oldfinish(editor, view)


def read2values(vals):
    try:
        strings = vals.split()
        if len(strings) != 2:
            quarkx.msgbox("Improper Data Entry!\n\nYou must enter 2 values\nseparated by a space.", MT_ERROR, MB_OK)
            return None, None
        else:
            return eval(strings[0]), eval(strings[1])
    except (AttributeError):
        quarkx.msgbox("Improper Data Entry!\n\nYou must enter 2 values\nseparated by a space.", MT_ERROR, MB_OK)
        return None, None


########### This section makes the  Basic Distortion Dialog input ###############

class DistortionDlg(quarkpy.dlgclasses.LiveEditDlg):
    "The Quick Object Makers Basic Input dialog box."
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (190,115)
    dlgflags = FWF_KEEPFOCUS   # keeps dialog box open
    dfsep = 0.57    # sets 57% for labels and the rest for edit boxes
    dlgdef = """
        {
        Style = "13"
        Caption = "Object Distortion Dialog"

        distortion: =
            {
            Txt = "Distortion"
            Typ = "EU"
            Hint = "This box allows you to set an 'amount' factor"$0D
               "to elongate (positive amount)"$0D
               "or shrink (negitive amount)"$0D
               "the height of an object."$0D
               "This 'amount' is set to a 1/8th factor to try and"$0D
               "keep the top and bottom touch points on the grid."$0D
               "The default value is 0 for a normal shape."
            }

        sep: = {Typ="S" Txt=""}

        makehollow: =
        {
        Txt = "Make hollow"
        Typ = "X1"
        Cap="on/off" 
        Hint = "Checking this box will make the object hollow when the LMB is released."$0D
               "This will take added time to compute and may ' freeze ' the program temporarily."$0D$0D
               "WARNING: when using with the 'Sphere' object,"$0D
               "over 10 faces will take about 30 seconds."$0D
               "over 15 faces will take about 10 minutes."
        }

        sep: = {Typ="S" Txt=""}

        exit:py = {Txt="" }
        }
    """


def DistortionClick(m):
    editor = mapeditor()
    if editor is None: return
  
    def setup(self):
        editor.distortiondlg=self
        src = self.src
      ### To populate settings...
        if (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"] is None) and (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"] is None):
            src["distortion"] = "0"
            src["makehollow"] = "0"
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"] = src["distortion"]
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"] = src["makehollow"]
        else:
            src["distortion"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"]
            src["makehollow"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]

        if src["distortion"]:
            distort = src["distortion"]
        else:
            distort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"]

        if src["makehollow"]:
            hollow = src["makehollow"]
        else:
            hollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]


    def action(self, editor=editor):
        distort = (self.src["distortion"])
        if distort is None:
            distort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"]

        hollow = (self.src["makehollow"])
        if hollow is None:
            hollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]

      ### Save the settings...
        quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"] = distort
        quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"] = hollow

        self.src["distortion"] = distort
        self.src["distortion"] = hollow


    def onclosing(self, editor=editor):

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "3D":
                quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                view.invalidate(1)


    DistortionDlg(quarkx.clickform, 'distortiondlg', editor, setup, action, onclosing)



########### This section makes the  Torus Distortion Dialog input ###############

class TorusDistortionDlg(quarkpy.dlgclasses.LiveEditDlg):
    "The Quick Object Makers Torus Input dialog box."
    #
    # dialog layout
    #

    endcolor = AQUA
        # width,length add 40 for new button
    size = (190,310)
    dlgflags = FWF_KEEPFOCUS   # keeps dialog box open
    dfsep = 0.52    # sets 52% for labels and the rest for edit boxes
    dlgdef = """
        {
        Style = "13"
        Caption = "Torus Distortion Dialog"

        segs_faces: =
            {
            Txt = "Segments\Faces"
            Typ = "EQ"
            Hint = "This allows additional sections"$0D
               "or faces to be added above the base count."$0D
               "Only positive amounts can be entered."$0D
               "If 'Segments' and 'Faces' are both set to '0'"$0D
               "then the number of sections and faces will be the same."$0D
               "The default values are '0 0' for a normal shape."
            }

        sep: = {Typ="S" Txt=""}

        radiuses: =
            {
            Txt = "Hole\Seg size"
            Typ = "EQ"
            Hint = "This changes the radius of the torus."$0D
               "'Hole' is the overall size radius, has min. setting of 1.0."$0D
               "'Seg' is the radius of the segments, will not exceed 'Hole'."$0D
               "The default values are '2.0 1.0' for a normal shape."
            }

        sep: = {Typ="S" Txt=""}

        xydistort: =
            {
            Txt = "X\Y distortion"
            Typ = "EQ"
            Hint = "This distorts or elongates the torus X and Y axis."$0D
               "Both have a minimum setting of 1."$0D
               "The default values are '2 2' for a normal shape."
            }

        sep: = {Typ="S" Txt=""}

        zupdistort: =
            {
            Txt = "Z\Up distortion"
            Typ = "EQ"
            Hint = "This distorts or elongates the torus Z axis and"$0D
               "will make it hollow and tapered towards the top."$0D
               "Z axis has a minimum setting of 1, tapering is 0."$0D
               "The default values are '2 0' for a normal shape."
            }

        sep: = {Typ="S" Txt=""}

        ring_seg_edges: =
            {
            Txt = "Ring\Seg edges"
            Typ = "EQ"
            Hint = "This changes the edges of the torus."$0D
               "'Ring' is the overall edge effect, has min. setting of 0.5."$0D
               "'Seg' is the edge effect of the segments, min. setting of 0.5."$0D
               "The default values are '2.0 2.0' for a normal shape."
            }

        sep: = {Typ="S" Txt=""}

        hollowtorus: =
        {
        Txt = "Extrude hollow"
        Typ = "X1"
        Cap="on/off" 
        Hint = "Checking this box will make the object hollow when the LMB is released."$0D
               "This will take added time to compute and may ' freeze ' the program temporarily."$0D
               "Un-checking this feature will automatically deactivate the 'No bulkheads' box below."$0D
        }

        nobulkheads: =
        {
        Txt = "No bulkheads"
        Typ = "X1"
        Cap="on/off" 
        Hint = "You can not use this feature unless 'Extrude hollow' above is already checked."$0D
               "Checking this box will automatically remove all interior 'bulkhead' walls."$0D
               "This may cause 'leaks' in the map requiring the use of a 'hollow'"$0D
               "box surrounding the entire map to allow it to build without any errors."
        }

        sep: = {Typ="S" Txt=""}

        Reset: =       // Reset button
        {
          Cap = "defaults"      // button caption
          Typ = "B"                     // "B"utton
          Hint = "Reset all the default settings"
          Delete: =
          {
            segs_faces = "0 0"         // the button resets these items to these amounts
            radiuses = "2 1"
            xydistort = "2 2"
            zupdistort = "2 0"
            ring_seg_edges = "2 2"
            hollowtorus = "0"
            nobulkheads = "0"
          }
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
        }
    """


def TorusDistortionClick(m):
    editor = mapeditor()
    if editor is None: return
  
    def setup(self):
        editor.torusdistortiondlg=self
        src = self.src
      ### To populate settings...
        if (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"] is None) and (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"] is None) and (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"] is None) and (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"] is None) and (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"] is None) and (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_hollowtorus"] is None) and (quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"] is None):
    #        src["segs_faces"] = 0, 0
            src["segs_faces"] = "0 0" # fix for linux
    #        src["radiuses"] = 2, 1
            src["radiuses"] = "2 1" # fix for linux
    #        src["xydistort"] = 2, 2
            src["xydistort"] = "2 2" # fix for linux
    #        src["zupdistort"] = 2, 0
            src["zupdistort"] = "2 0" # fix for linux
    #        src["ring_seg_edges"] = 2, 2
            src["ring_seg_edges"] = "2 2" # fix for linux
            src["hollowtorus"] = "0"
            src["nobulkheads"] = "0"
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"] = src["segs_faces"]
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"] = src["radiuses"]
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"] = src["xydistort"]
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"] = src["zupdistort"]
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"] = src["ring_seg_edges"]
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_hollowtorus"] = src["hollowtorus"]
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"] = src["nobulkheads"]
        else:
            src["segs_faces"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"]
            src["radiuses"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"]
            src["xydistort"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"]
            src["zupdistort"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"]
            src["ring_seg_edges"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]
            src["hollowtorus"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_hollowtorus"]
            src["nobulkheads"] = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"]


        if src["segs_faces"]:
    #        segments, rings = src["segs_faces"]
            segments, rings = read2values(src["segs_faces"]) # fix for linux
        else:
    #        segments, rings = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"]
            segments, rings = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"]) # fix for linux

        if src["radiuses"]:
    #        hole, sections = src["radiuses"]
            hole, sections = read2values(src["radiuses"]) # fix for linux
        else:
    #        hole, sections = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"]
            hole, sections = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"]) # fix for linux

        if src["xydistort"]:
    #        xdistort, ydistort = src["xydistort"]
            xdistort, ydistort = read2values(src["xydistort"]) # fix for linux
        else:
    #        xdistort, ydistort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"]
            xdistort, ydistort = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"]) # fix for linux

        if src["zupdistort"]:
    #        zdistort, updistort = src["zupdistort"]
            zdistort, updistort = read2values(src["zupdistort"]) # fix for linux
        else:
    #        zdistort, updistort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"]
            zdistort, updistort = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"]) # fix for linux

        if src["ring_seg_edges"]:
    #        ring_edges, seg_edges = src["ring_seg_edges"]
            ring_edges, seg_edges = read2values(src["ring_seg_edges"]) # fix for linux
        else:
    #        ring_edges, seg_edges = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]
            ring_edges, seg_edges = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]) # fix for linux


        if src["hollowtorus"]:
            hollow = src["hollowtorus"]
            plugins.mapterrainmodes.clickedbutton(editor)
        else:
            hollow = "0"
            plugins.mapterrainmodes.clickedbutton(editor)


        if src["nobulkheads"]:
            noheads = src["nobulkheads"]
            plugins.mapterrainmodes.clickedbutton(editor)
        else:
            noheads = "0"
            plugins.mapterrainmodes.clickedbutton(editor)


        self.src["segs_faces"] = "%.0f %.0f"%(segments, rings)
        self.src["radiuses"] = "%.1f %.1f"%(hole, sections)
        self.src["xydistort"] = "%.1f %.1f"%(xdistort, ydistort)
        self.src["zupdistort"] = "%.1f %.1f"%(zdistort, updistort)
        self.src["ring_seg_edges"] = "%.1f %.1f"%(ring_edges, seg_edges)


    def action(self, editor=editor):
        segments, rings = read2values(self.src["segs_faces"])
        if segments is None:
    #        segments, rings = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"]
            segments, rings = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"]) # fix for linux

        hole, sections = read2values(self.src["radiuses"])
        if hole is None:
    #        hole, sections = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"]
            hole, sections = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"]) # fix for linux

        xdistort, ydistort = read2values(self.src["xydistort"])
        if xdistort is None:
    #        xdistort, ydistort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"]
            xdistort, ydistort = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"]) # fix for linux

        zdistort, updistort = read2values(self.src["zupdistort"])
        if zdistort is None:
    #        zdistort, updistort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"]
            zdistort, updistort = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"]) # fix for linux

        ring_edges, seg_edges = read2values(self.src["ring_seg_edges"])
        if ring_edges is None:
    #        ring_edges, seg_edges = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]
            ring_edges, seg_edges = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]) # fix for linux

        if (self.src["hollowtorus"]) == "0" and quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"] == "1":
            hollow = (self.src["hollowtorus"])
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_hollowtorus"] = hollow
            (self.src["nobulkheads"]) = "0"
            noheads = (self.src["nobulkheads"])
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"] = noheads
        else:
            hollow = (self.src["hollowtorus"])
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_hollowtorus"] = hollow


        if (self.src["nobulkheads"]) == "1" and quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_hollowtorus"] == "0":
            (self.src["nobulkheads"]) = "0"
            noheads = (self.src["nobulkheads"])
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"] = noheads

        else:
            noheads = (self.src["nobulkheads"])
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"] = noheads


      ### Save the settings...
        if segments < 0:
            segments = 0
        if rings < 0:
            rings = 0
        else:
    #        quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"] = segments, rings
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"] = (str(segments) +" "+ str(rings)) # fix for linux

        if hole < 1.0:
            hole = 1.0
        if sections >= hole:
            sections = hole - 0.5
        if sections < 0.5:
            sections = 0.5
        else:
    #        quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"] = hole, sections
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"] = (str(hole) +" "+ str(sections)) # fix for linux

        if xdistort < 1:
            xdistort = 1
        if ydistort < 1:
            ydistort = 1
        else:
    #        quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"] = xdistort, ydistort
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"] = (str(xdistort) +" "+ str(ydistort)) # fix for linux

        if zdistort < 1:
            zdistort = 1
        if updistort < 0:
            updistort = 0
        else:
    #        quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"] = zdistort, updistort
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"] = (str(zdistort) +" "+ str(updistort)) # fix for linux

        if ring_edges < .5:
            ring_edges = .5
        if ring_edges >= 20:
            ring_edges = 20
        if seg_edges < .5:
            seg_edges = .5
        if seg_edges >= 20:
            seg_edges = 20
        else:
    #        quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"] = ring_edges, seg_edges
            quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"] = (str(ring_edges) +" "+ str(seg_edges)) # fix for linux


        self.src["segs_faces"] = None
        self.src["radiuses"] = None
        self.src["xydistort"] = None
        self.src["zupdistort"] = None
        self.src["ring_seg_edges"] = None


    def onclosing(self, editor=editor):

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "3D":
                quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                view.invalidate(1)


    TorusDistortionDlg(quarkx.clickform, 'torusdistortiondlg', editor, setup, action, onclosing)



########################################
# For dialog menu button.
# As new selectors are added that can use a dialog box
# run them through this menu selection button.
# A maximum of 20 buttons can use this feature.
#
def DialogClick(m):
    editor = mapeditor()
    if quarkx.setupsubset(SS_MAP, "Building").getint("ObjectMode") < 20 and quarkx.setupsubset(SS_MAP, "Building").getint("DragMode") > 4:
        if quarkx.setupsubset(SS_MAP, "Building").getint("ObjectMode") == 19:
            if editor.layout.explorer.sellist == []:
                quarkx.msgbox("No selection has been made.\n\nYou must first select an Object\nto activate this tool and\nchange your settings for this Object Maker.", MT_ERROR, MB_OK)
                return
            else:
                o = editor.layout.explorer.sellist
                m = qmenu.item("Dummy", None, "")
                m.o = o
                DistortionClick(m)

        elif quarkx.setupsubset(SS_MAP, "Building").getint("ObjectMode") < 6:

            m = qmenu.item("Dummy", None, "")
            DistortionClick(m)

        elif quarkx.setupsubset(SS_MAP, "Building").getint("ObjectMode") == 6:

            m = qmenu.item("Dummy", None, "")
            TorusDistortionClick(m)

        else:
            quarkx.msgbox("Your current Quick Object Maker does not use this function.\n\nIt only applyies to one that shows it (uses 'Dialog Box')\n                      in its discription popup.", MT_INFORMATION, MB_OK)
            return
    else:
        quarkx.msgbox("This 'Dialog Box' function is only used with\n'QuArK's Quick Object Makers' on this toolbar.", MT_ERROR, MB_OK)
        return



########### This section makes the rulers ###############
#### and is dependent on the Options - Ruler guide settings ####

def objectruler(editor, view, poly):
    rulerlist = poly
    if quarkx.boundingboxof(rulerlist) is not None:
        bbox = quarkx.boundingboxof(rulerlist)
        bmin, bmax = bbox
    else:
        return
    x1 = bmin.tuple[0]
    y1 = bmin.tuple[1]
    z1 = bmin.tuple[2]
    x2 = bmax.tuple[0]
    y2 = bmax.tuple[1]
    z2 = bmax.tuple[2]

# The following sets the canvas function to draw the images.
    cv = view.canvas()
    cv.fontname = "Terminal"
    cv.fontbold = 0
    cv.transparent = 1
    cv.fontcolor = FUCHSIA
    cv.fontsize = 8
    cv.penwidth = 1
    cv.penstyle = PS_SOLID
    cv.pencolor = FUCHSIA

    grid = editor.gridstep    # Gives grid setting
    type = view.info["type"]  # These type values are set
                              #  in the layout-defining plugins.

# ===============
# X view settings
# ===============

    if type == "YZ":

       if not MapOption("All2DviewsRulers") and not MapOption("AllTopRulers") and not MapOption("AllSideRulers") and not MapOption("XviewRulers") and not MapOption("XyTopRuler") and not MapOption("XzSideRuler"):
           return

       if not MapOption("AllSideRulers") and not MapOption("XzSideRuler"):
     # Makes the X view top ruler
        # Makes the line for Y axis
           ypoint1 = quarkx.vect(x1, y1, z2+grid)
           ypoint2 = quarkx.vect(x2, y2, z2+grid)
           p1 = view.proj(ypoint1)
           p2 = view.proj(ypoint2)
           cv.line(p1, p2)
        # Makes right end line for Y axis
           ylendt = quarkx.vect(x1, y1, z2+grid+(grid*.5))
           ylendb = quarkx.vect(x1, y1, z2+grid-(grid*.5))
           p1 = view.proj(ylendt)
           p2 = view.proj(ylendb)
           cv.line(p1, p2)
        # Makes left end line for Y axis
           yrendt = quarkx.vect(x2, y2, z2+grid+(grid*.5))
           yrendb = quarkx.vect(x2, y2, z2+grid-(grid*.5))
           p1 = view.proj(yrendt)
           p2 = view.proj(yrendb)
           cv.line(p1, p2)
        # Prints above the left marker line "0"
           x = view.proj(yrendt).tuple[0]-4
           y = view.proj(yrendt).tuple[1]-12
           cv.textout(x,y,"0")
        # Prints above the right marker line the distance, on the Y axis
           x = view.proj(ylendt).tuple[0]
           y = view.proj(ylendt).tuple[1]-12
           dist = abs(y2-y1)
           cv.textout(x,y,quarkx.ftos(dist))


       if not MapOption("AllTopRulers") and not MapOption("XyTopRuler"):
     # Makes the Z view side ruler
        # Makes the line for Z axis
           ypoint2 = quarkx.vect(x2, y1-grid, z2)
           ypoint1 = quarkx.vect(x2, y1-grid, z1)
           p2 = view.proj(ypoint2)
           p1 = view.proj(ypoint1)
           cv.line(p1, p2)
        # Makes top end line for Z axis
           yrendt = quarkx.vect(x2, y1-grid-(grid*.5), z2)
           ylendt = quarkx.vect(x2, y1-grid+(grid*.5), z2)
           p1 = view.proj(yrendt)
           p2 = view.proj(ylendt)
           cv.line(p1, p2)
        # Makes bottom end line for Z axis
           yrendb = quarkx.vect(x2, y1-grid-(grid*.5), z1)
           ylendb = quarkx.vect(x2, y1-grid+(grid*.5), z1)
           p1 = view.proj(yrendb)
           p2 = view.proj(ylendb)
           cv.line(p1, p2)
        # Prints right of bottom marker line "0"
           x = view.proj(yrendb).tuple[0]+8
           y = view.proj(yrendb).tuple[1]-2
           cv.textout(x,y,"0")
        # Prints right of top marker line the distance, on the Z axis
           x = view.proj(yrendt).tuple[0]+8
           y = view.proj(yrendt).tuple[1]-2
           higth = abs(z2-z1)
           cv.textout(x,y,quarkx.ftos(higth))


# ===============
# Y view settings
# ===============

    elif type == "XZ":

       if not MapOption("All2DviewsRulers") and not MapOption("AllTopRulers") and not MapOption("AllSideRulers") and not MapOption("YviewRulers") and not MapOption("YxTopRuler") and not MapOption("YzSideRuler"):
           return

       if not MapOption("AllSideRulers") and not MapOption("YzSideRuler"):

     # Makes the Y view top ruler
        # Makes the line for X axis
           xpoint1 = quarkx.vect(x1, y1, z2+grid)
           xpoint2 = quarkx.vect(x2, y2, z2+grid)
           p1 = view.proj(xpoint1)
           p2 = view.proj(xpoint2)
           cv.line(p1, p2)
        # Makes left end line for X axis
           xlendt = quarkx.vect(x1, y1, z2+grid+(grid*.5))
           xlendb = quarkx.vect(x1, y1, z2+grid-(grid*.5))
           p1 = view.proj(xlendt)
           p2 = view.proj(xlendb)
           cv.line(p1, p2)
        # Makes right end line for X axis
           xrendt = quarkx.vect(x2, y1, z2+grid+(grid*.5))
           xrendb = quarkx.vect(x2, y1, z2+grid-(grid*.5))
           p1 = view.proj(xrendt)
           p2 = view.proj(xrendb)
           cv.line(p1, p2)
        # Prints above the left marker line "0"
           x = view.proj(xlendt).tuple[0]-4
           y = view.proj(xlendt).tuple[1]-12
           cv.textout(x,y,"0")
        # Prints above the right marker line the distance, on the X axis
           x = view.proj(xrendt).tuple[0]
           y = view.proj(xrendt).tuple[1]-12
           dist = abs(x1-x2)
           cv.textout(x,y,quarkx.ftos(dist))


       if not MapOption("AllTopRulers") and not MapOption("YxTopRuler"):
     # Makes the Y view side ruler
        # Makes the line for Y axis
           ypoint2 = quarkx.vect(x2+grid, y2, z2)
           ypoint1 = quarkx.vect(x2+grid, y1, z1)
           p2 = view.proj(ypoint2)
           p1 = view.proj(ypoint1)
           cv.line(p1, p2)
        # Makes top end line for Y axis
           ylendt = quarkx.vect(x2+grid-(grid*.5), y1, z2)
           yrendt = quarkx.vect(x2+grid+(grid*.5), y1, z2)
           p1 = view.proj(ylendt)
           p2 = view.proj(yrendt)
           cv.line(p1, p2)
        # Makes bottom end line for Y axis
           ylendb = quarkx.vect(x2+grid-(grid*.5), y1, z1)
           yrendb = quarkx.vect(x2+grid+(grid*.5), y1, z1)
           p1 = view.proj(ylendb)
           p2 = view.proj(yrendb)
           cv.line(p1, p2)
        # Prints right of bottom marker line "0"
           x = view.proj(yrendb).tuple[0]+8
           y = view.proj(yrendb).tuple[1]-2
           cv.textout(x,y,"0")
        # Prints right of top marker line the distance, on the Y axis
           x = view.proj(yrendt).tuple[0]+8
           y = view.proj(yrendt).tuple[1]-2
           higth = abs(z2-z1)
           cv.textout(x,y,quarkx.ftos(higth))


# ===============
# Z view settings
# ===============

    elif type == "XY":

       if not MapOption("All2DviewsRulers") and not MapOption("AllTopRulers") and not MapOption("AllSideRulers") and not MapOption("ZviewRulers") and not MapOption("ZxTopRuler") and not MapOption("ZySideRuler"):
           return

       if not MapOption("AllSideRulers") and not MapOption("ZySideRuler"):
     # Makes the Z view top ruler
        # Makes the line for X axis
           xpoint1 = quarkx.vect(x1, y2+grid, z2)
           xpoint2 = quarkx.vect(x2, y2+grid, z2)
           p1 = view.proj(xpoint1)
           p2 = view.proj(xpoint2)
           cv.line(p1, p2)
        # Makes left end line for X axis
           xlendt = quarkx.vect(x1, y2+grid+(grid*.5), z2)
           xlendb = quarkx.vect(x1, y2+grid-(grid*.5), z2)
           p1 = view.proj(xlendt)
           p2 = view.proj(xlendb)
           cv.line(p1, p2)
        # Makes right end line for X axis
           xrendt = quarkx.vect(x2, y2+grid+(grid*.5), z2)
           xrendb = quarkx.vect(x2, y2+grid-(grid*.5), z2)
           p1 = view.proj(xrendt)
           p2 = view.proj(xrendb)
           cv.line(p1, p2)
        # Prints above the left marker line "0"
           x = view.proj(xlendt).tuple[0]-4
           y = view.proj(xlendt).tuple[1]-12
           cv.textout(x,y,"0")
        # Prints above the right marker line the distance, on the X axis
           x = view.proj(xrendt).tuple[0]
           y = view.proj(xrendt).tuple[1]-12
           dist = abs(x1-x2)
           cv.textout(x,y,quarkx.ftos(dist))


       if not MapOption("AllTopRulers") and not MapOption("ZxTopRuler"):
     # Makes the Z view side ruler
        # Makes the line for Y axis
           ypoint2 = quarkx.vect(x2+grid, y2, z2)
           ypoint1 = quarkx.vect(x2+grid, y1, z1)
           p2 = view.proj(ypoint2)
           p1 = view.proj(ypoint1)
           cv.line(p1, p2)
        # Makes top end line for Y axis
           ylendt = quarkx.vect(x2+grid-(grid*.5), y2, z2)
           yrendt = quarkx.vect(x2+grid+(grid*.5), y2, z2)
           p1 = view.proj(ylendt)
           p2 = view.proj(yrendt)
           cv.line(p1, p2)
        # Makes bottom end line for Y axis
           ylendb = quarkx.vect(x2+grid-(grid*.5), y1, z1)
           yrendb = quarkx.vect(x2+grid+(grid*.5), y1, z1)
           p1 = view.proj(ylendb)
           p2 = view.proj(yrendb)
           cv.line(p1, p2)
        # Prints right of bottom marker line "0"
           x = view.proj(yrendb).tuple[0]+8
           y = view.proj(yrendb).tuple[1]-2
           cv.textout(x,y,"0")
        # Prints right of top marker line the distance, on the Y axis
           x = view.proj(yrendt).tuple[0]+8
           y = view.proj(yrendt).tuple[1]-2
           higth = abs(y2-y1)
           cv.textout(x,y,quarkx.ftos(higth))

    else:
       return



###################################

class SphereMakerDragObject(parent):
    "A sphere maker."

    Hint = hintPlusInfobaselink("Quick sphere maker||Quick sphere maker:\n\nAfter you click this button, you can draw spheres on the map with the left mouse button and each sphere will be turned into an actual poly.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.\nOver 20 faces will 'freeze' QuArK but it will return.", "intro.mapeditor.toolpalettes.objectmodes.html#sphere")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1) # give point on the grid
        p = view.proj(self.pt0) # converts to point on the screen view
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y
            self.z0 = p.z
    #
    # For setting stuff up at the beginning of a drag
    #
        self.startpoint = p # holds the starting point value (does not change)
        self.trigger = 0    # Sets trigger for editor.invalidateviews() for their 1 time cleanup, below.

### This draws the circle and red image and sets size as you drag across the view with LMB pressed.

    def buildredimages(self, x, y, flags, depth=None):
        editor = mapeditor()
        if editor is None:
            return None, None
        type = self.view.info["type"]

       ## This section creates the rectangle selector in the 3D view only
        if type == "3D":
            if x==self.x0 or y==self.y0:
                return None, None
            if depth is None:
                min, max = self.view.depth
                max = max - 0.0001
            else:
                min, max = depth
            pts = [self.view.space(self.x0, self.y0, min),
                   self.view.space(x, self.y0, min),
                   self.view.space(x, y, min),
                   self.view.space(self.x0, y, min)]
            pts.append(pts[0])
            pts2 = [self.view.space(self.x0, self.y0, max),
                    self.view.space(x, self.y0, max),
                    self.view.space(x, y, max),
                    self.view.space(self.x0, y, max)]
            if (x<self.x0)^(y<self.y0):
                pts.reverse()
                pts2.reverse()
            poly = quarkx.newobj("redbox:p")
            for i in (0,1,2,3):
                face = quarkx.newobj("side:f")
                face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
                poly.appenditem(face)
            face = quarkx.newobj("front:f")
            face.setthreepoints((pts[0], pts[3], pts[1]), 0)
            poly.appenditem(face)
            face = quarkx.newobj("back:f")
            face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
            poly.appenditem(face)
            if self.view.info["type"] == "3D":
                for f in poly.subitems:
                    f.swapsides()
            if poly.rebuildall() != (0,0):
                return None, None
            return None, [poly]


        ## point always means x, y and z values are given

        z = 0
        drag2gridpt = quarkpy.qhandles.aligntogrid(self.view.space(x, y, z), 1) # converts to point dragged to on grid
        startgridpoint = self.pt0 # gives starting point of drag on grid
        dragpointamount = drag2gridpt - startgridpoint # gives drag distance on grid for x, y and z
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))

        minrad = p  # mine
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        maxrad = p  # mine
        if p.visible:
            min = p.z
        max = min + dx

  ## Draws the Blue circle
        cx, cy, cz = [], [], []
        mX, mY, mZ = minrad.tuple
        X, Y, Z = maxrad.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = self.view.proj(x,y,z)
                    cx.append(p.x)
                    cy.append(p.y)
                    cz.append(p.z)
        mX = minrad.tuple[0]
        mY = minrad.tuple[1]
        mZ = minrad.tuple[2]
        X = maxrad.tuple[0]
        Y = maxrad.tuple[1]
        Z = maxrad.tuple[2]
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        cz = (Z+mZ)*0.5
        X = int(X)      #py2.4
        Y = int(Y)      #py2.4
        Z = int(Z)      #py2.4
        cx = int(cx)    #py2.4
        cy = int(cy)    #py2.4
        cz = int(cz)    #py2.4
        mX = int(mX)    #py2.4
        mY = int(mY)    #py2.4
        mZ = int(mZ)    #py2.4
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)   #py2.4
        centerY = int(centerY)   #py2.4
        centerZ = int(centerZ)   #py2.4
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)  #py2.4
        radius = int(screengridstep)

    ## This section sets up not to draw any faces if there are less than 3
        type = self.view.info["type"]
        if type == "XY":
            facecount = abs(int(dragpointamount.tuple[1]/actualgrid))
            if dragpointamount.tuple[0] == 0:
                facecount = 0
        else:
            facecount = abs(int(dragpointamount.tuple[2]/actualgrid))
            if type == "XZ" and dragpointamount.tuple[0] == 0 or type == "YZ" and dragpointamount.tuple[1] == 0:
                facecount = 0
        if facecount < 3:
            facecount = 0

    ## This section just cleans the single view we are in or all of the views if there are red faces to draw
    ## and sets up the trigger device for one final cleaning of all the views, below, to remove old red lines.
    ## The original trigger is set in the def of this class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.repaint() # this just cleans the current view if no object is being drawn
        else:
            for view in editor.layout.views:
                view.repaint()  # this cleans all the views and allows the redlines to be drawn
            if facecount < 3:
                facecount = 0
                self.trigger = 2
            else:
                self.trigger = 1

        self.facecount = facecount # To pass value to def rectanglesel below for error message testing

  #### This section sets up the curent view to draw the BLUE circle, lines, GREEN crosshairs and face lable
        cv = self.view.canvas()
        cv.pencolor = BLUE
        cv.brushstyle = BS_CLEAR

        # All code below given in screen values, not grid

    ## The next line draws the BLUE circle only
        cv.ellipse(centerX-radius, centerY-radius, centerX+radius+1, centerY+radius+1)

    ## This seciton draws all the BLUE grid lines, including the center ones
        if screengridstep != 0:
            segments = abs(radius/screengridstep)
        else:
            segments = 0
        drawline = float(int(segments))
        dif = segments - drawline
        if dif > .01 and dif < 1:
            drawline = drawline + 1
        while drawline >= 1:
            drawline = int(drawline)  #py2.4
            screengridstep = int(screengridstep)  #py2.4
            drawline = drawline - 1
            cv.line(centerX-radius, centerY+(screengridstep*drawline), centerX+radius, centerY+(screengridstep*drawline)) # draws X axis line on and ABOVE 0 in Z view
            cv.line(centerX+(screengridstep*drawline), centerY-radius, centerX+(screengridstep*drawline), centerY+radius) # draws Y axis line on and to the left of 0 in Z view
            if drawline <= 0:
                pass
            else:
                cv.line(centerX-radius, centerY-(screengridstep*drawline), centerX+radius, centerY-(screengridstep*drawline)) # draws X axis line BELOW 0 only in Z view
                cv.line(centerX-(screengridstep*drawline), centerY-radius, centerX-(screengridstep*drawline), centerY+radius) # draws Y axis line to the right of 0 only in Z view

    ## This section draws the cross hairs
        cv.penwidth = 1
        cv.pencolor = GREEN
        radius = 10
        cv.line(mX, cy, cx-radius, cy) # draws left screen X axis line
        cv.line(cx+radius, cy, X, cy)  # draws right screen X axis line
        cv.line(cx, mY, cx, cy-radius) # draws top screen Y axis line
        cv.line(cx, cy+radius, cx, Y)  # draws bottom screen Y axis line

    ## This section draws the face lable and gives the color warning scale
        cv.fontsize = 10
        cv.fontname = "MS Serif"
        cv.fontbold = 1

        if facecount > 10:
            cv.fontcolor = FUCHSIA
        if facecount > 15:
            cv.fontcolor = PURPLE
        if facecount > 19:
            cv.fontcolor = RED
        if facecount < 11:
            cv.fontcolor = GREEN
        if type == "YZ":
            if dragpointamount.tuple[1] < 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")
        else:
            if dragpointamount.tuple[0] > 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")

    ## This section cleans all the views 1 time and is the last part of the trigger device further above
        if facecount == 0 and self.trigger == 2:
            for view in editor.layout.views:
                view.repaint()
                self.trigger = 0
                editor.invalidateviews()


  #### This section creates the actual object, using its formula
     #   (all code uses grid amounts for x, y and z positions)

    ## This section regulates the object (sphere) size by the mouse drag

        if type == "YZ":
            objectsize = abs(dragpointamount.tuple[1])
        else:
            objectsize = abs(dragpointamount.tuple[0])

    ## This section gives the number of faces per layer and number of layers

        if type == "XY":
            sphere_res = abs(dragpointamount.tuple[1]/actualgrid)
        else:
            sphere_res = abs(dragpointamount.tuple[2]/actualgrid)
        sphere_res = int(sphere_res)   #py2.4

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"])
        if factor < -15:
            factor = -15
        oblong = 1+(factor*.0625)

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "XZ":
                XZ_xcenter = view.screencenter.tuple[0] # gives x center point used below for 2D view
                XZ_zcenter = view.screencenter.tuple[2] # gives z center point used below for 2D view
            if type == "XY":
                XY_ycenter = view.screencenter.tuple[1] # gives y center point used below for 2D view

     ## This section creates the actual Sphere object

        type = self.view.info["type"]
        poly = quarkx.newobj("sphere:p")
        for Group in range(sphere_res-2):
            for angle0 in range(sphere_res):

         ## Only allows the first pass to create the Top and Bottom groups which are triangle faces
                if Group == 0:

                 ###################### Top group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    A = quarkx.vect(x1, y1, y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    B = quarkx.vect(x1, y1, y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    C = quarkx.vect(x1, y1, y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

                 ###################### Bottom group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    A = quarkx.vect(x1, -y1, -y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    B = quarkx.vect(x1, -y1, -y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    C = quarkx.vect(x1, -y1, -y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

          ## Creates the Middle face groups which are rectangle faces
                 ###################### Middle groups #######################

                else:

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    A = quarkx.vect(x1, y1, y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    B = quarkx.vect(x1, y1, y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    C = quarkx.vect(x1, y1, y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

   #### End of Sphere object creation area

      ## This line calls for the ruler
        for view in editor.layout.views:
            objectruler(editor, view, [poly])

        return None, [poly]


### This section actually creates the finished object and drops it into the map.
### It also calls for the 3D view selection mode instead of creating object, causes lockup.

    def rectanglesel(self, editor, x,y, rectangle):

      ## Allows only selection rectangle in 3D views, not creation of sphere - causes lockup

        type = self.view.info["type"]
        if type == "3D":
            view = self.view
            redcolor = RED
            todo = "R"
            plugins.mapdragmodes.EverythingRectSelDragObject(view, x, y, redcolor, todo).rectanglesel(editor, x, y, rectangle)
            return

      ## Creates actual sphere object
        facecount = self.facecount # Gets value from above for message testing
        if facecount >= 65:
            quarkx.msgbox("This sphere object contains\n" + str(facecount) + " faces\nexceeding the maximum limit\nof 64 and can not be created.", MT_ERROR, MB_CANCEL)
            return None, None

        for f in rectangle.faces:

            # Prepare to set the default texture on the faces

            f.texturename = "[auto]"

           ## This section resizes the texture so that their scales are 1,1 and their angles are 0,90.

            tp = f.threepoints(0)
            n = f.normal
            v = orthogonalvect(n, editor.layout.views[0])
            tp = (tp[0],
                  v * 128 + tp[0],
                  (n^v) * 128 + tp[0])
            f.setthreepoints(tp, 0)

      ## This section is for the option to hollow the Sphere, actually Extrude, Make Hollow takes too long
        makehollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]
        if makehollow == "0":
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new sphere object", "0")
        else:
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new sphere group", "0")
            m = None
            plugins.mapcsg.ExtWall1click(m)


### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        import quarkpy.mdleditor
        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
            pass

        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    for r in self.redimages:
                        view.drawmap(r, mode)
                    type = view.info["type"]
                    if type == "3D":
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                    else:
                        import quarkpy.mdleditor
                        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
                            return
## This causes the red dragging shapes to be drawn
                        for r in self.redimages:
                            view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)


#####################################


class PyramidMakerDragObject(parent):
    "A pyramid-cone maker."

    Hint = hintPlusInfobaselink("Quick pyramid-cone maker||Quick pyramid-cone maker:\n\nAfter you click this button, you can draw pyramids-cones on the map with the left mouse button and each pyramid-cone will be turned into an actual poly.\n\nThe more sides that are added the more it becomes a cone shape.\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.\nClick ' InfoBase ' for special vertex movement details.", "intro.mapeditor.toolpalettes.objectmodes.html#pyramid_cone")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1) # give point on the grid
        p = view.proj(self.pt0) # converts to point on the screen view
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y
            self.z0 = p.z
    #
    # For setting stuff up at the beginning of a drag
    #
        self.startpoint = p # holds the starting point value (does not change)
        self.trigger = 0    # Sets trigger for editor.invalidateviews() for their 1 time cleanup, below.

### This draws the circle and red image and sets size as you drag across the view with LMB pressed.

    def buildredimages(self, x, y, flags, depth=None):
        editor = mapeditor()
        if editor is None:
            return None, None
        type = self.view.info["type"]

       ## This section creates the rectangle selector in the 3D view only
        if type == "3D":
            if x==self.x0 or y==self.y0:
                return None, None
            if depth is None:
                min, max = self.view.depth
                max = max - 0.0001
            else:
                min, max = depth
            pts = [self.view.space(self.x0, self.y0, min),
                   self.view.space(x, self.y0, min),
                   self.view.space(x, y, min),
                   self.view.space(self.x0, y, min)]
            pts.append(pts[0])
            pts2 = [self.view.space(self.x0, self.y0, max),
                    self.view.space(x, self.y0, max),
                    self.view.space(x, y, max),
                    self.view.space(self.x0, y, max)]
            if (x<self.x0)^(y<self.y0):
                pts.reverse()
                pts2.reverse()
            poly = quarkx.newobj("redbox:p")
            for i in (0,1,2,3):
                face = quarkx.newobj("side:f")
                face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
                poly.appenditem(face)
            face = quarkx.newobj("front:f")
            face.setthreepoints((pts[0], pts[3], pts[1]), 0)
            poly.appenditem(face)
            face = quarkx.newobj("back:f")
            face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
            poly.appenditem(face)
            if self.view.info["type"] == "3D":
                for f in poly.subitems:
                    f.swapsides()
            if poly.rebuildall() != (0,0):
                return None, None
            return None, [poly]

        ## point always means x, y and z values are given

        z = 0
        drag2gridpt = quarkpy.qhandles.aligntogrid(self.view.space(x, y, z), 1) # converts to point dragged to on grid
        startgridpoint = self.pt0 # gives starting point of drag on grid
        dragpointamount = drag2gridpt - startgridpoint # gives drag distance on grid for x, y and z
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))

        minrad = p  # mine
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        maxrad = p  # mine
        if p.visible:
            min = p.z
        max = min + dx

  ## Draws the circle
        cx, cy, cz = [], [], []
        mX, mY, mZ = minrad.tuple
        X, Y, Z = maxrad.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = self.view.proj(x,y,z)
                    cx.append(p.x)
                    cy.append(p.y)
                    cz.append(p.z)
        mX = minrad.tuple[0]
        mY = minrad.tuple[1]
        mZ = minrad.tuple[2]
        X = maxrad.tuple[0]
        Y = maxrad.tuple[1]
        Z = maxrad.tuple[2]
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        cz = (Z+mZ)*0.5
        X = int(X)      #py2.4
        Y = int(Y)      #py2.4
        Z = int(Z)      #py2.4
        cx = int(cx)    #py2.4
        cy = int(cy)    #py2.4
        cz = int(cz)    #py2.4
        mX = int(mX)    #py2.4
        mY = int(mY)    #py2.4
        mZ = int(mZ)    #py2.4
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)   #py2.4
        centerY = int(centerY)   #py2.4
        centerZ = int(centerZ)   #py2.4
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)   #py2.4
        radius = screengridstep

    ## This section sets up not to draw any faces if there are less than 3
        type = self.view.info["type"]
        if type == "XY":
            facecount = abs(int(dragpointamount.tuple[1]/actualgrid))
            if dragpointamount.tuple[0] == 0:
                facecount = 0
        else:
            facecount = abs(int(dragpointamount.tuple[2]/actualgrid))
            if type == "XZ" and dragpointamount.tuple[0] == 0 or type == "YZ" and dragpointamount.tuple[1] == 0:
                facecount = 0
        if facecount < 3:
            facecount = 0

    ## This section just cleans the single view we are in or all of the views if there are red faces to draw
    ## and sets up the trigger device for one final cleaning of all the views, below, to remove old red lines.
    ## The original trigger is set in the def of this class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.repaint() # this just cleans the current view if no object is being drawn
        else:
            for view in editor.layout.views:
                view.repaint()  # this cleans all the views and allows the redlines to be drawn
            if facecount < 3:
                facecount = 0
                self.trigger = 2
            else:
                self.trigger = 1

        self.facecount = facecount # To pass value to def rectanglesel below for error message testing


  #### This section sets up the curent view to draw the BLUE circle, lines, GREEN crosshairs and face lable
        cv = self.view.canvas()
        cv.pencolor = BLUE
        cv.brushstyle = BS_CLEAR

        # All code below given in screen values, not grid

    ## The next line draws the BLUE circle only
        cv.ellipse(centerX-radius, centerY-radius, centerX+radius+1, centerY+radius+1)

    ## This seciton draws all the BLUE grid lines, including the center ones
        if screengridstep != 0:
            segments = abs(radius/screengridstep)
        else:
            segments = 0
        drawline = float(int(segments))
        drawline = int(drawline)   #py2.4
        dif = segments - drawline
        if dif > .01 and dif < 1:
            drawline = drawline + 1
        while drawline >= 1:
            drawline = drawline - 1
            cv.line(centerX-radius, centerY+(screengridstep*drawline), centerX+radius, centerY+(screengridstep*drawline)) # draws X axis line on and ABOVE 0 in Z view
            cv.line(centerX+(screengridstep*drawline), centerY-radius, centerX+(screengridstep*drawline), centerY+radius) # draws Y axis line on and to the left of 0 in Z view
            if drawline <= 0:
                pass
            else:
                cv.line(centerX-radius, centerY-(screengridstep*drawline), centerX+radius, centerY-(screengridstep*drawline)) # draws X axis line BELOW 0 only in Z view
                cv.line(centerX-(screengridstep*drawline), centerY-radius, centerX-(screengridstep*drawline), centerY+radius) # draws Y axis line to the right of 0 only in Z view

    ## This section draws the cross hairs
        cv.penwidth = 1
        cv.pencolor = GREEN
        radius = 10
        cv.line(mX, cy, cx-radius, cy) # draws left screen X axis line
        cv.line(cx+radius, cy, X, cy)  # draws right screen X axis line
        cv.line(cx, mY, cx, cy-radius) # draws top screen Y axis line
        cv.line(cx, cy+radius, cx, Y)  # draws bottom screen Y axis line

    ## This section draws the face lable and gives the color warning scale
        cv.fontsize = 10
        cv.fontname = "MS Serif"
        cv.fontbold = 1

        if facecount > 10:
            cv.fontcolor = FUCHSIA
        if facecount > 15:
            cv.fontcolor = PURPLE
        if facecount > 19:
            cv.fontcolor = RED
        if facecount < 11:
            cv.fontcolor = GREEN
        if type == "YZ":
            if dragpointamount.tuple[1] < 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")
        else:
            if dragpointamount.tuple[0] > 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")

    ## This section cleans all the views 1 time and is the last part of the trigger device further above
        if facecount == 0 and self.trigger == 2:
            for view in editor.layout.views:
                view.repaint()
                self.trigger = 0
                editor.invalidateviews()


  #### This section creates the actual object, using its formula
     #   (all code uses grid amounts for x, y and z positions)

    ## This section regulates the object (pyramid) size by the mouse drag

        if type == "YZ":
            objectsize = abs(dragpointamount.tuple[1])
        else:
            objectsize = abs(dragpointamount.tuple[0])

    ## This section gives the number of faces per layer and number of layers

        if type == "XY":
            sphere_res = abs(dragpointamount.tuple[1]/actualgrid)
        else:
            sphere_res = abs(dragpointamount.tuple[2]/actualgrid)
        sphere_res = int(sphere_res)   #py2.4

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"])
        if factor < -15:
            factor = -15
        oblong = 1+(factor*.0625)

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "XZ":
                XZ_xcenter = view.screencenter.tuple[0] # gives x center point used below for 2D view
                XZ_zcenter = view.screencenter.tuple[2] # gives z center point used below for 2D view
            if type == "XY":
                XY_ycenter = view.screencenter.tuple[1] # gives y center point used below for 2D view

    ## This section creates the actual object

        type = self.view.info["type"]

        poly = quarkx.newobj("pyramid:p")

        for Group in range(sphere_res-1):

         ## Only allows the first pass to create the Pyramid group which are triangle faces
            if Group < 1:
                for angle0 in range(sphere_res):

                 ###################### Pyramid group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = startgridpoint.tuple[2]

                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = quarkpy.qhandles.aligntogrid(quarkx.vect(0, 0, XZ_zcenter), 1).tuple[2]

                    A = quarkx.vect(x1, y1, y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]

                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + quarkpy.qhandles.aligntogrid(quarkx.vect(0, 0, XZ_zcenter), 1).tuple[2]

                    B = quarkx.vect(x1, y1, y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = startgridpoint.tuple[2]

                      ## Creates the base for this view
                        base1 = quarkx.vect(-20, -20, y0)
                        base2 = quarkx.vect(20, 20, y0)
                        base3 = quarkx.vect(20, -20, y0)

                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = startgridpoint.tuple[2]

                      ## Creates the base for this view
                        base1 = quarkx.vect(-20, -20, y0)
                        base2 = quarkx.vect(20, 20, y0)
                        base3 = quarkx.vect(20, -20, y0)

                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = quarkpy.qhandles.aligntogrid(quarkx.vect(0, 0, XZ_zcenter), 1).tuple[2]

                      ## Creates the base for this view
                        base1 = quarkx.vect(-20, -20, y0)
                        base2 = quarkx.vect(20, 20, y0)
                        base3 = quarkx.vect(20, -20, y0)

                    C = quarkx.vect(x1, y1, y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

                face = quarkx.newobj("BaseFace:f") 
                face.setthreepoints((base1, base2, base3), 0)
                face.texturename = "[auto]"    
                poly.appenditem(face)

            else:
                break

      ## This line calls for the ruler
        for view in editor.layout.views:
            objectruler(editor, view, [poly])

        if self.view.info["type"] == "3D":
            for f in poly.subitems:
                f.swapsides()
        if self.x0-x == 0:
            return None, None
        return None, [poly]

      ## End of object creation section


### This section actually creates the finished object and drops it into the map.
### It also calls for the 3D view selection mode instead of creating object, causes lockup.

    def rectanglesel(self, editor, x,y, rectangle):

      ## Allows only selection rectangle in 3D views, not creation of pyramid - causes lockup

        type = self.view.info["type"]
        if type == "3D":
            view = self.view
            redcolor = RED
            todo = "R"
            plugins.mapdragmodes.EverythingRectSelDragObject(view, x, y, redcolor, todo).rectanglesel(editor, x, y, rectangle)
            return 

      ## Creates actual pyramid object
        facecount = self.facecount # Gets value from above for message testing
        if facecount >= 65:
            quarkx.msgbox("This pyramid object contains\n" + str(facecount) + " faces\nexceeding the maximum limit\nof 64 and can not be created.", MT_ERROR, MB_CANCEL)
            return None, None

        for f in rectangle.faces:
            # Prepare to set the default texture on the faces

            f.texturename = "[auto]"

           ## This section resizes the texture so that their scales are 1,1 and their angles are 0,90.

            tp = f.threepoints(0)
            n = f.normal
            v = orthogonalvect(n, editor.layout.views[0])
            tp = (tp[0],
                  v * 128 + tp[0],
                  (n^v) * 128 + tp[0])
            f.setthreepoints(tp, 0)

      ## This section is for the option to hollow the object
        makehollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]
        if makehollow == "0":
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new pyramid object", "0")
        else:
            group = quarkx.newobj("Pyramid group:g")
            for poly in [rectangle]:
                newpoly = poly.copy()
                group.appenditem(newpoly)
            quarkpy.mapbtns.dropitemsnow(editor, [group], "new pyramid group", "0")
            m = None
            plugins.mapcsg.Hollow1click(m)



### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        import quarkpy.mdleditor
        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
            pass

        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    for r in self.redimages:
                        view.drawmap(r, mode)
                    type = view.info["type"]
                    if type == "3D":
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                    else:
                        import quarkpy.mdleditor
                        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
                            return
## This causes the red dragging shapes to be drawn
                        for r in self.redimages:
                            view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)



###################################

class DoubleConeMakerDragObject(parent):
    "A double-cone maker."

    Hint = hintPlusInfobaselink("Quick double-cone maker||Quick double-cone maker:\n\nAfter you click this button, you can draw double-cones on the map with the left mouse button and each double-cone will be turned into an actual poly.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.mapeditor.toolpalettes.objectmodes.html#double_cone")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1) # give point on the grid
        p = view.proj(self.pt0) # converts to point on the screen view
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y
            self.z0 = p.z
    #
    # For setting stuff up at the beginning of a drag
    #
        self.startpoint = p # holds the starting point value (does not change)
        self.trigger = 0    # Sets trigger for editor.invalidateviews() for their 1 time cleanup, below.

### This draws the circle and red image and sets size as you drag across the view with LMB pressed.

    def buildredimages(self, x, y, flags, depth=None):
        editor = mapeditor()
        if editor is None:
            return None, None
        type = self.view.info["type"]

       ## This section creates the rectangle selector in the 3D view only
        if type == "3D":
            if x==self.x0 or y==self.y0:
                return None, None
            if depth is None:
                min, max = self.view.depth
                max = max - 0.0001
            else:
                min, max = depth
            pts = [self.view.space(self.x0, self.y0, min),
                   self.view.space(x, self.y0, min),
                   self.view.space(x, y, min),
                   self.view.space(self.x0, y, min)]
            pts.append(pts[0])
            pts2 = [self.view.space(self.x0, self.y0, max),
                    self.view.space(x, self.y0, max),
                    self.view.space(x, y, max),
                    self.view.space(self.x0, y, max)]
            if (x<self.x0)^(y<self.y0):
                pts.reverse()
                pts2.reverse()
            poly = quarkx.newobj("redbox:p")
            for i in (0,1,2,3):
                face = quarkx.newobj("side:f")
                face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
                poly.appenditem(face)
            face = quarkx.newobj("front:f")
            face.setthreepoints((pts[0], pts[3], pts[1]), 0)
            poly.appenditem(face)
            face = quarkx.newobj("back:f")
            face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
            poly.appenditem(face)
            if self.view.info["type"] == "3D":
                for f in poly.subitems:
                    f.swapsides()
            if poly.rebuildall() != (0,0):
                return None, None
            return None, [poly]


        ## point always means x, y and z values are given

        z = 0
        drag2gridpt = quarkpy.qhandles.aligntogrid(self.view.space(x, y, z), 1) # converts to point dragged to on grid
        startgridpoint = self.pt0 # gives starting point of drag on grid
        dragpointamount = drag2gridpt - startgridpoint # gives drag distance on grid for x, y and z
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))

        minrad = p  # mine
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        maxrad = p  # mine
        if p.visible:
            min = p.z
        max = min + dx

  ## Draws the Blue circle
        cx, cy, cz = [], [], []
        mX, mY, mZ = minrad.tuple
        X, Y, Z = maxrad.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = self.view.proj(x,y,z)
                    cx.append(p.x)
                    cy.append(p.y)
                    cz.append(p.z)
        mX = minrad.tuple[0]
        mY = minrad.tuple[1]
        mZ = minrad.tuple[2]
        X = maxrad.tuple[0]
        Y = maxrad.tuple[1]
        Z = maxrad.tuple[2]
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        cz = (Z+mZ)*0.5
        X = int(X)      #py2.4
        Y = int(Y)      #py2.4
        Z = int(Z)      #py2.4
        cx = int(cx)    #py2.4
        cy = int(cy)    #py2.4
        cz = int(cz)    #py2.4
        mX = int(mX)    #py2.4
        mY = int(mY)    #py2.4
        mZ = int(mZ)    #py2.4
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)   #py2.4
        centerY = int(centerY)   #py2.4
        centerZ = int(centerZ)   #py2.4
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)  #py2.4
        radius = screengridstep

    ## This section sets up not to draw any faces if there are less than 3
        type = self.view.info["type"]
        if type == "XY":
            facecount = abs(int(dragpointamount.tuple[1]/actualgrid))
            if dragpointamount.tuple[0] == 0:
                facecount = 0
        else:
            facecount = abs(int(dragpointamount.tuple[2]/actualgrid))
            if type == "XZ" and dragpointamount.tuple[0] == 0 or type == "YZ" and dragpointamount.tuple[1] == 0:
                facecount = 0
        if facecount < 3:
            facecount = 0

    ## This section just cleans the single view we are in or all of the views if there are red faces to draw
    ## and sets up the trigger device for one final cleaning of all the views, below, to remove old red lines.
    ## The original trigger is set in the def of this class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.repaint() # this just cleans the current view if no object is being drawn
        else:
            for view in editor.layout.views:
                view.repaint()  # this cleans all the views and allows the redlines to be drawn
            if facecount < 3:
                facecount = 0
                self.trigger = 2
            else:
                self.trigger = 1

        self.facecount = facecount # To pass value to def rectanglesel below for error message testing

  #### This section sets up the curent view to draw the BLUE circle, lines, GREEN crosshairs and face lable
        cv = self.view.canvas()
        cv.pencolor = BLUE
        cv.brushstyle = BS_CLEAR

        # All code below given in screen values, not grid

    ## The next line draws the BLUE circle only
        cv.ellipse(centerX-radius, centerY-radius, centerX+radius+1, centerY+radius+1)

    ## This seciton draws all the BLUE grid lines, including the center ones
        if screengridstep != 0:
            segments = abs(radius/screengridstep)
        else:
            segments = 0
        drawline = float(int(segments))
        drawline = int(drawline)  #py2.4
        dif = segments - drawline
        if dif > .01 and dif < 1:
            drawline = drawline + 1
        while drawline >= 1:
            drawline = drawline - 1
            cv.line(centerX-radius, centerY+(screengridstep*drawline), centerX+radius, centerY+(screengridstep*drawline)) # draws X axis line on and ABOVE 0 in Z view
            cv.line(centerX+(screengridstep*drawline), centerY-radius, centerX+(screengridstep*drawline), centerY+radius) # draws Y axis line on and to the left of 0 in Z view
            if drawline <= 0:
                pass
            else:
                cv.line(centerX-radius, centerY-(screengridstep*drawline), centerX+radius, centerY-(screengridstep*drawline)) # draws X axis line BELOW 0 only in Z view
                cv.line(centerX-(screengridstep*drawline), centerY-radius, centerX-(screengridstep*drawline), centerY+radius) # draws Y axis line to the right of 0 only in Z view

    ## This section draws the cross hairs
        cv.penwidth = 1
        cv.pencolor = GREEN
        radius = 10
        cv.line(mX, cy, cx-radius, cy) # draws left screen X axis line
        cv.line(cx+radius, cy, X, cy)  # draws right screen X axis line
        cv.line(cx, mY, cx, cy-radius) # draws top screen Y axis line
        cv.line(cx, cy+radius, cx, Y)  # draws bottom screen Y axis line

    ## This section draws the face lable and gives the color warning scale
        cv.fontsize = 10
        cv.fontname = "MS Serif"
        cv.fontbold = 1

        if facecount > 10:
            cv.fontcolor = FUCHSIA
        if facecount > 15:
            cv.fontcolor = PURPLE
        if facecount > 19:
            cv.fontcolor = RED
        if facecount < 11:
            cv.fontcolor = GREEN
        if type == "YZ":
            if dragpointamount.tuple[1] < 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")
        else:
            if dragpointamount.tuple[0] > 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")

    ## This section cleans all the views 1 time and is the last part of the trigger device further above
        if facecount == 0 and self.trigger == 2:
            for view in editor.layout.views:
                view.repaint()
                self.trigger = 0
                editor.invalidateviews()


  #### This section creates the actual object, using its formula
     #   (all code uses grid amounts for x, y and z positions)

    ## This section regulates the object (double-cone) size by the mouse drag

        if type == "YZ":
            objectsize = abs(dragpointamount.tuple[1])
        else:
            objectsize = abs(dragpointamount.tuple[0])

    ## This section gives the number of faces per layer and number of layers

        if type == "XY":
            sphere_res = abs(dragpointamount.tuple[1]/actualgrid)
        else:
            sphere_res = abs(dragpointamount.tuple[2]/actualgrid)
        sphere_res = int(sphere_res)   #py2.4

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"])
        if factor < -1 and facecount < 25:
            factor = -1
        if factor < -1 and facecount > 24:
            factor = 0
        if factor < 1 and facecount > 35:
            factor = 1
        if factor < 2 and facecount > 44:
            factor = 2
        if factor < 3 and facecount > 50:
            factor = 3
        if factor < 4 and facecount > 55:
            factor = 4
        if factor < 5 and facecount > 59:
            factor = 5
        if factor < 6 and facecount > 63:
            factor = 6
        else:
            factor = factor
        factor = factor * 10
        oblong = 1+(factor*.0625)

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "XZ":
                XZ_xcenter = view.screencenter.tuple[0] # gives x center point used below for 2D view
                XZ_zcenter = view.screencenter.tuple[2] # gives z center point used below for 2D view
            if type == "XY":
                XY_ycenter = view.screencenter.tuple[1] # gives y center point used below for 2D view

     ## This section creates the actual Double-cone object

        type = self.view.info["type"]
        poly = quarkx.newobj("double-cone:p")
        for Group in range(sphere_res-1):

         ## Only allows the first pass to create the Top and Bottom groups which are triangle faces
            if Group == 0:
                for angle0 in range(sphere_res):

                 ###################### Top group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    A = quarkx.vect(x1, y1, y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    B = quarkx.vect(x1, y1, y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    C = quarkx.vect(x1, y1, y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

                 ###################### Bottom group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    A = quarkx.vect(x1, -y1, -y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    B = quarkx.vect(x1, -y1, -y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    C = quarkx.vect(x1, -y1, -y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

            else:
                break

   #### End of double-cone object creation area

      ## This line calls for the ruler
        for view in editor.layout.views:
            objectruler(editor, view, [poly])

        return None, [poly]


### This section actually creates the finished object and drops it into the map.
### It also calls for the 3D view selection mode instead of creating object, causes lockup.

    def rectanglesel(self, editor, x,y, rectangle):

      ## Allows only selection rectangle in 3D views, not creation of double-cone - causes lockup

        type = self.view.info["type"]
        if type == "3D":
            view = self.view
            redcolor = RED
            todo = "R"
            plugins.mapdragmodes.EverythingRectSelDragObject(view, x, y, redcolor, todo).rectanglesel(editor, x, y, rectangle)
            return

      ## Creates actual double-cone object
        facecount = self.facecount # Gets value from above for message testing
        if facecount >= 65:
            quarkx.msgbox("This double-cone object contains\n" + str(facecount) + " faces\nexceeding the maximum limit\nof 64 and can not be created.", MT_ERROR, MB_CANCEL)
            return None, None

        for f in rectangle.faces:

            # Prepare to set the default texture on the faces

            f.texturename = "[auto]"

           ## This section resizes the texture so that their scales are 1,1 and their angles are 0,90.

            tp = f.threepoints(0)
            n = f.normal
            v = orthogonalvect(n, editor.layout.views[0])
            tp = (tp[0],
                  v * 128 + tp[0],
                  (n^v) * 128 + tp[0])
            f.setthreepoints(tp, 0)

      ## This section is for the option to hollow the object, actually Extrude, Make Hollow not as clean
        makehollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]
        if makehollow == "0":
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "double-cone object", "0")
        else:
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "double-cone object", "0")
            m = None
            plugins.mapcsg.ExtWall1click(m)



### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        import quarkpy.mdleditor
        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
            pass

        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    for r in self.redimages:
                        view.drawmap(r, mode)
                    type = view.info["type"]
                    if type == "3D":
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                    else:
                        import quarkpy.mdleditor
                        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
                            return
## This causes the red dragging shapes to be drawn
                        for r in self.redimages:
                            view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)



###################################


class CylinderMakerDragObject(parent):
    "A cylinder maker."

    Hint = hintPlusInfobaselink("Quick cylinder maker||Quick cylinder maker:\n\nAfter you click this button, you can draw cylinders on the map with the left mouse button and each cylinder will be turned into an actual poly. This can make angled sides or a more curved style cylinder by adding more faces.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.mapeditor.toolpalettes.objectmodes.html#cylinder")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1) # gives point on the grid
        p = view.proj(self.pt0) # converts to point on the screen view
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y
            self.z0 = p.z
    #
    # For setting stuff up at the beginning of a drag
    #
        self.startpoint = p # holds the starting point value (does not change)
        self.trigger = 0    # Sets trigger for editor.invalidateviews() for their 1 time cleanup, below.

### This draws the circle and red image and sets size as you drag across the view with LMB pressed.

    def buildredimages(self, x, y, flags, depth=None):
        editor = mapeditor()
        if editor is None:
            return None, None
        type = self.view.info["type"]

       ## This section creates the rectangle selector in the 3D view only
        if type == "3D":
            if x==self.x0 or y==self.y0:
                return None, None
            if depth is None:
                min, max = self.view.depth
                max = max - 0.0001
            else:
                min, max = depth
            pts = [self.view.space(self.x0, self.y0, min),
                   self.view.space(x, self.y0, min),
                   self.view.space(x, y, min),
                   self.view.space(self.x0, y, min)]
            pts.append(pts[0])
            pts2 = [self.view.space(self.x0, self.y0, max),
                    self.view.space(x, self.y0, max),
                    self.view.space(x, y, max),
                    self.view.space(self.x0, y, max)]
            if (x<self.x0)^(y<self.y0):
                pts.reverse()
                pts2.reverse()
            poly = quarkx.newobj("redbox:p")
            for i in (0,1,2,3):
                face = quarkx.newobj("side:f")
                face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
                poly.appenditem(face)
            face = quarkx.newobj("front:f")
            face.setthreepoints((pts[0], pts[3], pts[1]), 0)
            poly.appenditem(face)
            face = quarkx.newobj("back:f")
            face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
            poly.appenditem(face)
            if self.view.info["type"] == "3D":
                for f in poly.subitems:
                    f.swapsides()
            if poly.rebuildall() != (0,0):
                return None, None
            return None, [poly]


        ## point always means x, y and z values are given

        z = 0
        drag2gridpt = quarkpy.qhandles.aligntogrid(self.view.space(x, y, z), 1) # converts to point dragged to on grid
        startgridpoint = self.pt0 # gives starting point of drag on grid
        dragpointamount = drag2gridpt - startgridpoint # gives drag distance on grid for x, y and z
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))

        minrad = p  # mine
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        maxrad = p  # mine
        if p.visible:
            min = p.z
        max = min + dx

  ## Draws the circle
        cx, cy, cz = [], [], []
        mX, mY, mZ = minrad.tuple
        X, Y, Z = maxrad.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = self.view.proj(x,y,z)
                    cx.append(p.x)
                    cy.append(p.y)
                    cz.append(p.z)
        mX = minrad.tuple[0]
        mY = minrad.tuple[1]
        mZ = minrad.tuple[2]
        X = maxrad.tuple[0]
        Y = maxrad.tuple[1]
        Z = maxrad.tuple[2]
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        cz = (Z+mZ)*0.5
        X = int(X)      #py2.4
        Y = int(Y)      #py2.4
        Z = int(Z)      #py2.4
        cx = int(cx)    #py2.4
        cy = int(cy)    #py2.4
        cz = int(cz)    #py2.4
        mX = int(mX)    #py2.4
        mY = int(mY)    #py2.4
        mZ = int(mZ)    #py2.4
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)   #py2.4
        centerY = int(centerY)   #py2.4
        centerZ = int(centerZ)   #py2.4

        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)  #py2.4
        radius = screengridstep

    ## This section sets up not to draw any faces if there are less than 3
        type = self.view.info["type"]
        if type == "XY":
            facecount = abs(int(dragpointamount.tuple[1]/actualgrid))
            if dragpointamount.tuple[0] == 0:
                facecount = 0
        else:
            facecount = abs(int(dragpointamount.tuple[2]/actualgrid))
            if type == "XZ" and dragpointamount.tuple[0] == 0 or type == "YZ" and dragpointamount.tuple[1] == 0:
                facecount = 0
        if facecount < 3:
            facecount = 0

    ## This section just cleans the single view we are in or all of the views if there are red faces to draw
    ## and sets up the trigger device for one final cleaning of all the views, below, to remove old red lines.
    ## The original trigger is set in the def of this class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.repaint() # this just cleans the current view if no object is being drawn
        else:
            for view in editor.layout.views:
                view.repaint()  # this cleans all the views and allows the redlines to be drawn
            if facecount < 3:
                facecount = 0
                self.trigger = 2
            else:
                self.trigger = 1

        self.facecount = facecount # To pass value to def rectanglesel below for error message testing


  #### This section sets up the curent view to draw the BLUE circle, lines, GREEN crosshairs and face lable
        cv = self.view.canvas()
        cv.pencolor = BLUE
        cv.brushstyle = BS_CLEAR

        # All code below given in screen values, not grid

    ## The next line draws the BLUE circle only
        cv.ellipse(centerX-radius, centerY-radius, centerX+radius+1, centerY+radius+1)

    ## This seciton draws all the BLUE grid lines, including the center ones
        if screengridstep != 0:
            segments = abs(radius/screengridstep)
        else:
            segments = 0
        drawline = float(int(segments))
        drawline = int(drawline)  #py2.4
        dif = segments - drawline
        if dif > .01 and dif < 1:
            drawline = drawline + 1
        while drawline >= 1:
            drawline = drawline - 1
            cv.line(centerX-radius, centerY+(screengridstep*drawline), centerX+radius, centerY+(screengridstep*drawline)) # draws X axis line on and ABOVE 0 in Z view
            cv.line(centerX+(screengridstep*drawline), centerY-radius, centerX+(screengridstep*drawline), centerY+radius) # draws Y axis line on and to the left of 0 in Z view
            if drawline <= 0:
                pass
            else:
                cv.line(centerX-radius, centerY-(screengridstep*drawline), centerX+radius, centerY-(screengridstep*drawline)) # draws X axis line BELOW 0 only in Z view
                cv.line(centerX-(screengridstep*drawline), centerY-radius, centerX-(screengridstep*drawline), centerY+radius) # draws Y axis line to the right of 0 only in Z view

    ## This section draws the cross hairs
        cv.penwidth = 1
        cv.pencolor = GREEN
        radius = 10
        cv.line(mX, cy, cx-radius, cy) # draws left screen X axis line
        cv.line(cx+radius, cy, X, cy)  # draws right screen X axis line
        cv.line(cx, mY, cx, cy-radius) # draws top screen Y axis line
        cv.line(cx, cy+radius, cx, Y)  # draws bottom screen Y axis line

    ## This section draws the face lable and gives the color warning scale
        cv.fontsize = 10
        cv.fontname = "MS Serif"
        cv.fontbold = 1

        if facecount > 10:
            cv.fontcolor = FUCHSIA
        if facecount > 15:
            cv.fontcolor = PURPLE
        if facecount > 19:
            cv.fontcolor = RED
        if facecount < 11:
            cv.fontcolor = GREEN
        if type == "YZ":
            if dragpointamount.tuple[1] < 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")
        else:
            if dragpointamount.tuple[0] > 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")

    ## This section cleans all the views 1 time and is the last part of the trigger device further above
        if facecount == 0 and self.trigger == 2:
            for view in editor.layout.views:
                view.repaint()
                self.trigger = 0
                editor.invalidateviews()


  #### This section creates the actual object, using its formula
     #   (all code uses grid amounts for x, y and z positions)

    ## This section regulates the object (cylinder) size by the mouse drag

        if type == "YZ":
            objectsize = abs(dragpointamount.tuple[1])
        else:
            objectsize = abs(dragpointamount.tuple[0])

    ## This section gives the number of faces per layer and number of layers

        if type == "XY":
            sphere_res = abs(dragpointamount.tuple[1]/actualgrid)
        else:
            sphere_res = abs(dragpointamount.tuple[2]/actualgrid)
        sphere_res = int(sphere_res)   #py2.4

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"])
        if factor < -15:
            factor = -15
        oblong = 1+(factor*.0625)

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "XZ":
                XZ_xcenter = view.screencenter.tuple[0] # gives x center point used below for 2D view
                XZ_zcenter = view.screencenter.tuple[2] # gives z center point used below for 2D view
            if type == "XY":
                XY_ycenter = view.screencenter.tuple[1] # gives y center point used below for 2D view

        type = self.view.info["type"]

     ## This section creates the actual object

        poly = quarkx.newobj("cylinder:p")

        ###################### Creates the Cylinder faces #######################

        for angle0 in range(sphere_res):

        # Point A
            ang0 = math.pi*(sphere_res*.5)/(sphere_res-1) + math.pi*.5
            x0 = math.cos (ang0) * objectsize
            y0 = math.sin (ang0) * objectsize
            ang1 = math.pi*2*(angle0+1)/(sphere_res)
            x1 = x0*math.cos (ang1)
            y1 = x0*math.sin (ang1)
          #### To set start point of drag by view
            if type == "YZ":
                x1 = x1 + XZ_xcenter
                y1 = y1 + startgridpoint.tuple[1]
                y0 = startgridpoint.tuple[2]
            if type == "XZ":
                x1 = x1 + startgridpoint.tuple[0]
                y1 = y1 + XY_ycenter
                y0 = startgridpoint.tuple[2]
            if type == "XY":
                x1 = x1 + startgridpoint.tuple[0]
                y1 = y1 + startgridpoint.tuple[1]
                y0 = quarkpy.qhandles.aligntogrid(quarkx.vect(0, 0, XZ_zcenter), 1).tuple[2]

            A = quarkx.vect(x1, y1, y0)

        # Point B
            ang0 = math.pi*((sphere_res*.5)-1)/(sphere_res-1) + math.pi*.5
            x0 = math.cos (ang0) * objectsize
            y0 = math.sin (ang0) * objectsize
            ang1 = math.pi*2*(angle0+1)/(sphere_res)
            x1 = x0*math.cos (ang1)
            y1 = x0*math.sin (ang1)
          #### To set start point of drag by view
            if type == "YZ":
                x1 = x1 + XZ_xcenter
                y1 = y1 + startgridpoint.tuple[1]
                y0 = startgridpoint.tuple[2] + abs(dragpointamount.tuple[1])*2*oblong

              ## Creates the top for this view
                top1 = quarkx.vect(20, -20, y0)
                top2 = quarkx.vect(20, 20, y0)
                top3 = quarkx.vect(-20, -20, y0)

            if type == "XZ":
                x1 = x1 + startgridpoint.tuple[0]
                y1 = y1 + XY_ycenter
                y0 = startgridpoint.tuple[2] + abs(dragpointamount.tuple[0])*2*oblong

              ## Creates the top for this view
                top1 = quarkx.vect(20, -20, y0)
                top2 = quarkx.vect(20, 20, y0)
                top3 = quarkx.vect(-20, -20, y0)

            if type == "XY":
                x1 = x1 + startgridpoint.tuple[0]
                y1 = y1 + startgridpoint.tuple[1]
                y0 = quarkpy.qhandles.aligntogrid(quarkx.vect(0, 0, XZ_zcenter), 1).tuple[2] + abs(dragpointamount.tuple[0])*2*oblong

              ## Creates the top for this view
                top1 = quarkx.vect(20, -20, y0)
                top2 = quarkx.vect(20, 20, y0)
                top3 = quarkx.vect(-20, -20, y0)


            B = quarkx.vect(x1, y1, y0)

        # Point C
            ang0 = math.pi*(sphere_res*.5)/(sphere_res-1) + math.pi*.5
            x0 = math.cos (ang0) * objectsize
            y0 = math.sin (ang0) * objectsize
            ang1 = math.pi*2*angle0/(sphere_res)
            x1 = x0*math.cos (ang1)
            y1 = x0*math.sin (ang1)
          #### To set start point of drag by view
            if type == "YZ":
                x1 = x1 + XZ_xcenter
                y1 = y1 + startgridpoint.tuple[1]
                y0 = startgridpoint.tuple[2]

              ## Creates the base for this view
                base1 = quarkx.vect(-20, -20, y0)
                base2 = quarkx.vect(20, 20, y0)
                base3 = quarkx.vect(20, -20, y0)

            if type == "XZ":
                x1 = x1 + startgridpoint.tuple[0]
                y1 = y1 + XY_ycenter
                y0 = startgridpoint.tuple[2]

              ## Creates the base for this view
                base1 = quarkx.vect(-20, -20, y0)
                base2 = quarkx.vect(20, 20, y0)
                base3 = quarkx.vect(20, -20, y0)

            if type == "XY":
                x1 = x1 + startgridpoint.tuple[0]
                y1 = y1 + startgridpoint.tuple[1]
                y0 = quarkpy.qhandles.aligntogrid(quarkx.vect(0, 0, XZ_zcenter), 1).tuple[2]

              ## Creates the base for this view
                base1 = quarkx.vect(-20, -20, y0)
                base2 = quarkx.vect(20, 20, y0)
                base3 = quarkx.vect(20, -20, y0)

            C = quarkx.vect(x1, y1, y0)

            face = quarkx.newobj("object face:f")
            face.setthreepoints((A, B, C), 0)
            face.texturename = "[auto]" # gives texture to the face
            poly.appenditem(face)

       ## Adds the top to the poly
        face = quarkx.newobj("TopFace:f")
        face.setthreepoints((top1, top2, top3), 0)
        face.texturename = "[auto]"
        poly.appenditem(face)

       ## Adds the base to the poly
        face = quarkx.newobj("BaseFace:f")
        face.setthreepoints((base1, base2, base3), 0)
        face.texturename = "[auto]"
        poly.appenditem(face)

   #### end of object creation area

      ## This line calls for the ruler
        for view in editor.layout.views:
            objectruler(editor, view, [poly])


        if self.view.info["type"] == "3D":
            for f in poly.subitems:
                f.swapsides()
        if self.x0-x == 0:
            return None, None

        return None, [poly]


### This section actually creates the finished object and drops it into the map.
### It also calls for the 3D view selection mode instead of creating object, causes lockup.

    def rectanglesel(self, editor, x,y, rectangle):

      ## Allows only selection rectangle in 3D views, not creation of cylinder - causes lockup

        type = self.view.info["type"]
        if type == "3D":
            view = self.view
            redcolor = RED
            todo = "R"
            plugins.mapdragmodes.EverythingRectSelDragObject(view, x, y, redcolor, todo).rectanglesel(editor, x, y, rectangle)
            return 

      ## Creates actual cylinder object
        facecount = self.facecount # Gets value from above for message testing
        if facecount >= 65:
            quarkx.msgbox("This cylinder object contains\n" + str(facecount) + " faces\nexceeding the maximum limit\nof 64 and can not be created.", MT_ERROR, MB_CANCEL)
            return None, None

        for f in rectangle.faces:

            # Prepare to set the default texture on the faces

            f.texturename = "[auto]"

           ## This section resizes the texture so that their scales are 1,1 and their angles are 0,90.

            tp = f.threepoints(0)
            n = f.normal
            v = orthogonalvect(n, editor.layout.views[0])
            tp = (tp[0],
                  v * 128 + tp[0],
                  (n^v) * 128 + tp[0])
            f.setthreepoints(tp, 0)

      ## This section is for the option to hollow the object
        makehollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]
        if makehollow == "0":
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new cylinder object", "0")
        else:
            group = quarkx.newobj("Cylinder group:g")
            for poly in [rectangle]:
                newpoly = poly.copy()
                group.appenditem(newpoly)
            quarkpy.mapbtns.dropitemsnow(editor, [group], "new cylinder group", "0")
            m = None
            plugins.mapcsg.Hollow1click(m)

### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        import quarkpy.mdleditor
        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
            pass

        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    for r in self.redimages:
                        view.drawmap(r, mode)
                    type = view.info["type"]
                    if type == "3D":
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                    else:
                        import quarkpy.mdleditor
                        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
                            return
## This causes the red dragging shapes to be drawn
                        for r in self.redimages:
                            view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)


###################################

class DomeMakerDragObject(parent):
    "A dome maker."

    Hint = hintPlusInfobaselink("Quick dome maker||Quick dome maker:\n\nAfter you click this button, you can draw domes on the map with the left mouse button and each dome will be turned into an actual poly.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.mapeditor.toolpalettes.objectmodes.html#dome")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1) # give point on the grid
        p = view.proj(self.pt0) # converts to point on the screen view
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y
            self.z0 = p.z
    #
    # For setting stuff up at the beginning of a drag
    #
        self.startpoint = p # holds the starting point value (does not change)
        self.trigger = 0    # Sets trigger for editor.invalidateviews() for their 1 time cleanup, below.

### This draws the circle and red image and sets size as you drag across the view with LMB pressed.

    def buildredimages(self, x, y, flags, depth=None):
        editor = mapeditor()
        if editor is None:
            return None, None
        type = self.view.info["type"]

       ## This section creates the rectangle selector in the 3D view only
        if type == "3D":
            if x==self.x0 or y==self.y0:
                return None, None
            if depth is None:
                min, max = self.view.depth
                max = max - 0.0001
            else:
                min, max = depth
            pts = [self.view.space(self.x0, self.y0, min),
                   self.view.space(x, self.y0, min),
                   self.view.space(x, y, min),
                   self.view.space(self.x0, y, min)]
            pts.append(pts[0])
            pts2 = [self.view.space(self.x0, self.y0, max),
                    self.view.space(x, self.y0, max),
                    self.view.space(x, y, max),
                    self.view.space(self.x0, y, max)]
            if (x<self.x0)^(y<self.y0):
                pts.reverse()
                pts2.reverse()
            poly = quarkx.newobj("redbox:p")
            for i in (0,1,2,3):
                face = quarkx.newobj("side:f")
                face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
                poly.appenditem(face)
            face = quarkx.newobj("front:f")
            face.setthreepoints((pts[0], pts[3], pts[1]), 0)
            poly.appenditem(face)
            face = quarkx.newobj("back:f")
            face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
            poly.appenditem(face)
            if self.view.info["type"] == "3D":
                for f in poly.subitems:
                    f.swapsides()
            if poly.rebuildall() != (0,0):
                return None, None
            return None, [poly]


        ## point always means x, y and z values are given

        z = 0
        drag2gridpt = quarkpy.qhandles.aligntogrid(self.view.space(x, y, z), 1) # converts to point dragged to on grid
        startgridpoint = self.pt0 # gives starting point of drag on grid
        dragpointamount = drag2gridpt - startgridpoint # gives drag distance on grid for x, y and z
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))

        minrad = p  # mine
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        maxrad = p  # mine
        if p.visible:
            min = p.z
        max = min + dx

  ## Draws the Blue circle
        cx, cy, cz = [], [], []
        mX, mY, mZ = minrad.tuple
        X, Y, Z = maxrad.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = self.view.proj(x,y,z)
                    cx.append(p.x)
                    cy.append(p.y)
                    cz.append(p.z)
        mX = minrad.tuple[0]
        mY = minrad.tuple[1]
        mZ = minrad.tuple[2]
        X = maxrad.tuple[0]
        Y = maxrad.tuple[1]
        Z = maxrad.tuple[2]
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        cz = (Z+mZ)*0.5
        X = int(X)      #py2.4
        Y = int(Y)      #py2.4
        Z = int(Z)      #py2.4
        cx = int(cx)    #py2.4
        cy = int(cy)    #py2.4
        cz = int(cz)    #py2.4
        mX = int(mX)    #py2.4
        mY = int(mY)    #py2.4
        mZ = int(mZ)    #py2.4
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)   #py2.4
        centerY = int(centerY)   #py2.4
        centerZ = int(centerZ)   #py2.4
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)  #py2.4
        radius = screengridstep

    ## This section sets up not to draw any faces if there are less than 3
        type = self.view.info["type"]
        if type == "XY":
            facecount = abs(int(dragpointamount.tuple[1]/actualgrid))
            if dragpointamount.tuple[0] == 0:
                facecount = 0
        else:
            facecount = abs(int(dragpointamount.tuple[2]/actualgrid))
            if type == "XZ" and dragpointamount.tuple[0] == 0 or type == "YZ" and dragpointamount.tuple[1] == 0:
                facecount = 0
        if facecount < 3:
            facecount = 0

    ## This section just cleans the single view we are in or all of the views if there are red faces to draw
    ## and sets up the trigger device for one final cleaning of all the views, below, to remove old red lines.
    ## The original trigger is set in the def of this class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.repaint() # this just cleans the current view if no object is being drawn
        else:
            for view in editor.layout.views:
                view.repaint()  # this cleans all the views and allows the redlines to be drawn
            if facecount < 3:
                facecount = 0
                self.trigger = 2
            else:
                self.trigger = 1

        self.facecount = facecount # To pass value to def rectanglesel below for error message testing

  #### This section sets up the curent view to draw the BLUE circle, lines, GREEN crosshairs and face lable
        cv = self.view.canvas()
        cv.pencolor = BLUE
        cv.brushstyle = BS_CLEAR

        # All code below given in screen values, not grid

    ## The next line draws the BLUE circle only
        cv.ellipse(centerX-radius, centerY-radius, centerX+radius+1, centerY+radius+1)

    ## This seciton draws all the BLUE grid lines, including the center ones
        if screengridstep != 0:
            segments = abs(radius/screengridstep)
        else:
            segments = 0
        drawline = float(int(segments))
        drawline = int(drawline)  #py2.4
        dif = segments - drawline
        if dif > .01 and dif < 1:
            drawline = drawline + 1
        while drawline >= 1:
            drawline = drawline - 1
            cv.line(centerX-radius, centerY+(screengridstep*drawline), centerX+radius, centerY+(screengridstep*drawline)) # draws X axis line on and ABOVE 0 in Z view
            cv.line(centerX+(screengridstep*drawline), centerY-radius, centerX+(screengridstep*drawline), centerY+radius) # draws Y axis line on and to the left of 0 in Z view
            if drawline <= 0:
                pass
            else:
                cv.line(centerX-radius, centerY-(screengridstep*drawline), centerX+radius, centerY-(screengridstep*drawline)) # draws X axis line BELOW 0 only in Z view
                cv.line(centerX-(screengridstep*drawline), centerY-radius, centerX-(screengridstep*drawline), centerY+radius) # draws Y axis line to the right of 0 only in Z view

    ## This section draws the cross hairs
        cv.penwidth = 1
        cv.pencolor = GREEN
        radius = 10
        cv.line(mX, cy, cx-radius, cy) # draws left screen X axis line
        cv.line(cx+radius, cy, X, cy)  # draws right screen X axis line
        cv.line(cx, mY, cx, cy-radius) # draws top screen Y axis line
        cv.line(cx, cy+radius, cx, Y)  # draws bottom screen Y axis line

    ## This section draws the face lable and gives the color warning scale
        cv.fontsize = 10
        cv.fontname = "MS Serif"
        cv.fontbold = 1

        if facecount > 10:
            cv.fontcolor = FUCHSIA
        if facecount > 15:
            cv.fontcolor = PURPLE
        if facecount > 19:
            cv.fontcolor = RED
        if facecount < 11:
            cv.fontcolor = GREEN
        if type == "YZ":
            if dragpointamount.tuple[1] < 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")
        else:
            if dragpointamount.tuple[0] > 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")

    ## This section cleans all the views 1 time and is the last part of the trigger device further above
        if facecount == 0 and self.trigger == 2:
            for view in editor.layout.views:
                view.repaint()
                self.trigger = 0
                editor.invalidateviews()


  #### This section creates the actual object, using its formula
     #   (all code uses grid amounts for x, y and z positions)

    ## This section regulates the object (dome) size by the mouse drag

        if type == "YZ":
            objectsize = abs(dragpointamount.tuple[1])
        else:
            objectsize = abs(dragpointamount.tuple[0])

    ## This section gives the number of faces per layer and number of layers

        if type == "XY":
            sphere_res = abs(dragpointamount.tuple[1]/actualgrid)
        else:
            sphere_res = abs(dragpointamount.tuple[2]/actualgrid)
        sphere_res = int(sphere_res)   #py2.4

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"])
        if factor < 1:
            factor = 1
        oblong = 1+(factor*.0625)

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "XZ":
                XZ_xcenter = view.screencenter.tuple[0] # gives x center point used below for 2D view
                XZ_zcenter = view.screencenter.tuple[2] # gives z center point used below for 2D view
            if type == "XY":
                XY_ycenter = view.screencenter.tuple[1] # gives y center point used below for 2D view

     ## This section creates the actual dome object

        type = self.view.info["type"]
        poly = quarkx.newobj("dome:p")
        for Group in range(sphere_res-2):
            for angle0 in range(sphere_res):

         ## Only allows the first pass to create the Top and Bottom groups which are triangle faces
                if Group == 0:

                 ###################### Top group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    A = quarkx.vect(x1, y1, y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    B = quarkx.vect(x1, y1, y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    C = quarkx.vect(x1, y1, y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

                 ###################### Bottom group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    A = quarkx.vect(x1, -y1, -y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    B = quarkx.vect(x1, -y1, -y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    C = quarkx.vect(x1, -y1, -y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

          ## Creates the Middle face groups which are rectangle faces
                 ###################### Middle groups #######################

                else:

                    if Group > factor: continue # This causes a dome of 5 segments and tapered walls

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    A = quarkx.vect(x1, y1, y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    B = quarkx.vect(x1, y1, y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    C = quarkx.vect(x1, y1, y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

   #### End of dome object creation area

      ## This line calls for the ruler
        for view in editor.layout.views:
            objectruler(editor, view, [poly])

        return None, [poly]


### This section actually creates the finished object and drops it into the map.
### It also calls for the 3D view selection mode instead of creating object, causes lockup.

    def rectanglesel(self, editor, x,y, rectangle):

      ## Allows only selection rectangle in 3D views, not creation of dome - causes lockup

        type = self.view.info["type"]
        if type == "3D":
            view = self.view
            redcolor = RED
            todo = "R"
            plugins.mapdragmodes.EverythingRectSelDragObject(view, x, y, redcolor, todo).rectanglesel(editor, x, y, rectangle)
            return

      ## Creates actual dome object
        facecount = self.facecount # Gets value from above for message testing
        if facecount >= 65:
            quarkx.msgbox("This dome object contains\n" + str(facecount) + " faces\nexceeding the maximum limit\nof 64 and can not be created.", MT_ERROR, MB_CANCEL)
            return None, None

        for f in rectangle.faces:

            # Prepare to set the default texture on the faces

            f.texturename = "[auto]"

           ## This section resizes the texture so that their scales are 1,1 and their angles are 0,90.

            tp = f.threepoints(0)
            n = f.normal
            v = orthogonalvect(n, editor.layout.views[0])
            tp = (tp[0],
                  v * 128 + tp[0],
                  (n^v) * 128 + tp[0])
            f.setthreepoints(tp, 0)

      ## This section is for the option to hollow the object, actually Extrude, Make Hollow not as clean
        makehollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]
        if makehollow == "0":
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new dome object", "0")
        else:
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new dome group", "0")
            m = None
            plugins.mapcsg.ExtWall1click(m)



### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        import quarkpy.mdleditor
        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
            pass

        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    for r in self.redimages:
                        view.drawmap(r, mode)
                    type = view.info["type"]
                    if type == "3D":
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                    else:
                        import quarkpy.mdleditor
                        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
                            return
## This causes the red dragging shapes to be drawn
                        for r in self.redimages:
                            view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)



#####################################


class FanMakerDragObject(parent):
    "A fan maker."

    Hint = hintPlusInfobaselink("Quick fan maker||Quick fan maker:\n\nAfter you click this button, you can draw fans on the map with the left mouse button and each fan will be turned into an actual poly.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.mapeditor.toolpalettes.objectmodes.html#fan")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1) # give point on the grid
        p = view.proj(self.pt0) # converts to point on the screen view
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y
            self.z0 = p.z
    #
    # For setting stuff up at the beginning of a drag
    #
        self.startpoint = p # holds the starting point value (does not change)
        self.trigger = 0    # Sets trigger for editor.invalidateviews() for their 1 time cleanup, below.

### This draws the circle and red image and sets size as you drag across the view with LMB pressed.

    def buildredimages(self, x, y, flags, depth=None):
        editor = mapeditor()
        if editor is None:
            return None, None
        type = self.view.info["type"]

       ## This section creates the rectangle selector in the 3D view only
        if type == "3D":
            if x==self.x0 or y==self.y0:
                return None, None
            if depth is None:
                min, max = self.view.depth
                max = max - 0.0001
            else:
                min, max = depth
            pts = [self.view.space(self.x0, self.y0, min),
                   self.view.space(x, self.y0, min),
                   self.view.space(x, y, min),
                   self.view.space(self.x0, y, min)]
            pts.append(pts[0])
            pts2 = [self.view.space(self.x0, self.y0, max),
                    self.view.space(x, self.y0, max),
                    self.view.space(x, y, max),
                    self.view.space(self.x0, y, max)]
            if (x<self.x0)^(y<self.y0):
                pts.reverse()
                pts2.reverse()
            poly = quarkx.newobj("redbox:p")
            for i in (0,1,2,3):
                face = quarkx.newobj("side:f")
                face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
                poly.appenditem(face)
            face = quarkx.newobj("front:f")
            face.setthreepoints((pts[0], pts[3], pts[1]), 0)
            poly.appenditem(face)
            face = quarkx.newobj("back:f")
            face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
            poly.appenditem(face)
            if self.view.info["type"] == "3D":
                for f in poly.subitems:
                    f.swapsides()
            if poly.rebuildall() != (0,0):
                return None, None
            return None, [poly]


        ## point always means x, y and z values are given

        z = 0
        drag2gridpt = quarkpy.qhandles.aligntogrid(self.view.space(x, y, z), 1) # converts to point dragged to on grid
        startgridpoint = self.pt0 # gives starting point of drag on grid
        dragpointamount = drag2gridpt - startgridpoint # gives drag distance on grid for x, y and z
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))

        minrad = p  # mine
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        maxrad = p  # mine
        if p.visible:
            min = p.z
        max = min + dx

  ## Draws the Blue circle
        cx, cy, cz = [], [], []
        mX, mY, mZ = minrad.tuple
        X, Y, Z = maxrad.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = self.view.proj(x,y,z)
                    cx.append(p.x)
                    cy.append(p.y)
                    cz.append(p.z)
        mX = minrad.tuple[0]
        mY = minrad.tuple[1]
        mZ = minrad.tuple[2]
        X = maxrad.tuple[0]
        Y = maxrad.tuple[1]
        Z = maxrad.tuple[2]
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        cz = (Z+mZ)*0.5
        X = int(X)      #py2.4
        Y = int(Y)      #py2.4
        Z = int(Z)      #py2.4
        cx = int(cx)    #py2.4
        cy = int(cy)    #py2.4
        cz = int(cz)    #py2.4
        mX = int(mX)    #py2.4
        mY = int(mY)    #py2.4
        mZ = int(mZ)    #py2.4
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)   #py2.4
        centerY = int(centerY)   #py2.4
        centerZ = int(centerZ)   #py2.4
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)  #py2.4
        radius = screengridstep

    ## This section sets up not to draw any faces if there are less than 3
        type = self.view.info["type"]
        if type == "XY":
            facecount = abs(int(dragpointamount.tuple[1]/actualgrid))
            if dragpointamount.tuple[0] == 0:
                facecount = 0
        else:
            facecount = abs(int(dragpointamount.tuple[2]/actualgrid))
            if type == "XZ" and dragpointamount.tuple[0] == 0 or type == "YZ" and dragpointamount.tuple[1] == 0:
                facecount = 0
        if facecount < 3:
            facecount = 0

    ## This section just cleans the single view we are in or all of the views if there are red faces to draw
    ## and sets up the trigger device for one final cleaning of all the views, below, to remove old red lines.
    ## The original trigger is set in the def of this class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.repaint() # this just cleans the current view if no object is being drawn
        else:
            for view in editor.layout.views:
                view.repaint()  # this cleans all the views and allows the redlines to be drawn
            if facecount < 3:
                facecount = 0
                self.trigger = 2
            else:
                self.trigger = 1

        self.facecount = facecount # To pass value to def rectanglesel below for error message testing

  #### This section sets up the curent view to draw the BLUE circle, lines, GREEN crosshairs and face lable
        cv = self.view.canvas()
        cv.pencolor = BLUE
        cv.brushstyle = BS_CLEAR

        # All code below given in screen values, not grid

    ## The next line draws the BLUE circle only
        cv.ellipse(centerX-radius, centerY-radius, centerX+radius+1, centerY+radius+1)

    ## This seciton draws all the BLUE grid lines, including the center ones
        if screengridstep != 0:
            segments = abs(radius/screengridstep)
        else:
            segments = 0
        drawline = float(int(segments))
        drawline = int(drawline)  #py2.4
        dif = segments - drawline
        if dif > .01 and dif < 1:
            drawline = drawline + 1
        while drawline >= 1:
            drawline = drawline - 1
            cv.line(centerX-radius, centerY+(screengridstep*drawline), centerX+radius, centerY+(screengridstep*drawline)) # draws X axis line on and ABOVE 0 in Z view
            cv.line(centerX+(screengridstep*drawline), centerY-radius, centerX+(screengridstep*drawline), centerY+radius) # draws Y axis line on and to the left of 0 in Z view
            if drawline <= 0:
                pass
            else:
                cv.line(centerX-radius, centerY-(screengridstep*drawline), centerX+radius, centerY-(screengridstep*drawline)) # draws X axis line BELOW 0 only in Z view
                cv.line(centerX-(screengridstep*drawline), centerY-radius, centerX-(screengridstep*drawline), centerY+radius) # draws Y axis line to the right of 0 only in Z view

    ## This section draws the cross hairs
        cv.penwidth = 1
        cv.pencolor = GREEN
        radius = 10
        cv.line(mX, cy, cx-radius, cy) # draws left screen X axis line
        cv.line(cx+radius, cy, X, cy)  # draws right screen X axis line
        cv.line(cx, mY, cx, cy-radius) # draws top screen Y axis line
        cv.line(cx, cy+radius, cx, Y)  # draws bottom screen Y axis line

    ## This section draws the face lable and gives the color warning scale
        cv.fontsize = 10
        cv.fontname = "MS Serif"
        cv.fontbold = 1

        if facecount > 10:
            cv.fontcolor = FUCHSIA
        if facecount > 15:
            cv.fontcolor = PURPLE
        if facecount > 19:
            cv.fontcolor = RED
        if facecount < 11:
            cv.fontcolor = GREEN
        if type == "YZ":
            if dragpointamount.tuple[1] < 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")
        else:
            if dragpointamount.tuple[0] > 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(facecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(facecount) + " faces")

    ## This section cleans all the views 1 time and is the last part of the trigger device further above
        if facecount == 0 and self.trigger == 2:
            for view in editor.layout.views:
                view.repaint()
                self.trigger = 0
                editor.invalidateviews()


  #### This section creates the actual object, using its formula
     #   (all code uses grid amounts for x, y and z positions)

    ## This section regulates the object (fan) size by the mouse drag

        if type == "YZ":
            objectsize = abs(dragpointamount.tuple[1])
        else:
            objectsize = abs(dragpointamount.tuple[0])

    ## This section gives the number of faces per layer and number of layers

        if type == "XY":
            sphere_res = abs(dragpointamount.tuple[1]/actualgrid)
        else:
            sphere_res = abs(dragpointamount.tuple[2]/actualgrid)
        sphere_res = int(sphere_res)   #py2.4

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_distortion"])
        if factor < -1 and facecount < 25:
            factor = -1
        if factor < -1 and facecount > 24:
            factor = 0
        if factor < 10 and facecount > 35:
            factor = 10
        if factor < 20 and facecount > 44:
            factor = 20
        if factor < 30 and facecount > 50:
            factor = 30
        if factor < 50 and facecount > 55:
            factor = 50
        if factor < 60 and facecount > 62:
            factor = 60
        else:
            factor = factor
        oblong = 1+(factor*.0625)

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "XZ":
                XZ_xcenter = view.screencenter.tuple[0] # gives x center point used below for 2D view
                XZ_zcenter = view.screencenter.tuple[2] # gives z center point used below for 2D view
            if type == "XY":
                XY_ycenter = view.screencenter.tuple[1] # gives y center point used below for 2D view

     ## This section creates the actual fan object

        type = self.view.info["type"]
        poly = quarkx.newobj("fan:p")
        for Group in range(sphere_res-1):

         ## Only allows the first pass to create the Top and Bottom groups which are triangle faces
            if Group == 0:
                for angle0 in range(sphere_res):

                 ###################### Top group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    A = quarkx.vect(x1, y1, y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    B = quarkx.vect(x1, y1, y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + XY_ycenter
                        y0 = y0 + startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 + startgridpoint.tuple[1]
                        y0 = y0 + XZ_zcenter

                    C = quarkx.vect(x1, y1, y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

                 ###################### Bottom group #######################

                # Point A
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*(angle0+1)/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    A = quarkx.vect(x1, -y1, -y0)

                # Point B
                    ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*Group/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    B = quarkx.vect(x1, -y1, -y0)

                # Point C
                    ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                    x0 = math.cos (ang0) * objectsize
                    y0 = math.sin (ang0) * objectsize*oblong
                    ang1 = math.pi*2*angle0/(sphere_res)
                    x1 = x0*math.cos (ang1)
                    y1 = x0*math.sin (ang1)
                  #### To set start point of drag by view
                    if type == "YZ":
                        x1 = x1 + XZ_xcenter
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XZ":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - XY_ycenter
                        y0 = y0 - startgridpoint.tuple[2]
                    if type == "XY":
                        x1 = x1 + startgridpoint.tuple[0]
                        y1 = y1 - startgridpoint.tuple[1]
                        y0 = y0 - XZ_zcenter

                    C = quarkx.vect(x1, -y1, -y0)

                    face = quarkx.newobj("object face:f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)

              # Eliminates unwanted extra group of broken faces
            elif Group == sphere_res-2:
                pass

          ## Creates the Middle face groups which are rectangle faces
                 ###################### Middle groups #######################

            else:

            # Point A
                ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                x0 = math.cos (ang0) * objectsize
                y0 = math.sin (ang0) * objectsize*oblong
                ang1 = math.pi*2*(angle0+1)/(sphere_res)
                x1 = x0*math.cos (ang1)
                y1 = x0*math.sin (ang1)
              #### To set start point of drag by view
                if type == "YZ":
                    x1 = x1 + XZ_xcenter
                    y1 = y1 + startgridpoint.tuple[1]
                    y0 = y0 + startgridpoint.tuple[2]
                if type == "XZ":
                    x1 = x1 + startgridpoint.tuple[0]
                    y1 = y1 + XY_ycenter
                    y0 = y0 + startgridpoint.tuple[2]
                if type == "XY":
                    x1 = x1 + startgridpoint.tuple[0]
                    y1 = y1 + startgridpoint.tuple[1]
                    y0 = y0 + XZ_zcenter

                A = quarkx.vect(x1, y1, y0)

            # Point B
                ang0 = math.pi*Group/(sphere_res-1) + math.pi*.5
                x0 = math.cos (ang0) * objectsize
                y0 = math.sin (ang0) * objectsize*oblong
                ang1 = math.pi*2*(angle0+1)/(sphere_res)
                x1 = x0*math.cos (ang1)
                y1 = x0*math.sin (ang1)
              #### To set start point of drag by view
                if type == "YZ":
                    x1 = x1 + XZ_xcenter
                    y1 = y1 + startgridpoint.tuple[1]
                    y0 = y0 + startgridpoint.tuple[2]
                if type == "XZ":
                    x1 = x1 + startgridpoint.tuple[0]
                    y1 = y1 + XY_ycenter
                    y0 = y0 + startgridpoint.tuple[2]
                if type == "XY":
                    x1 = x1 + startgridpoint.tuple[0]
                    y1 = y1 + startgridpoint.tuple[1]
                    y0 = y0 + XZ_zcenter

                B = quarkx.vect(x1, y1, y0)

            # Point C
                ang0 = math.pi*(Group+1)/(sphere_res-1) + math.pi*.5
                x0 = math.cos (ang0) * objectsize
                y0 = math.sin (ang0) * objectsize*oblong
                ang1 = math.pi*2*angle0/(sphere_res)
                x1 = x0*math.cos (ang1)
                y1 = x0*math.sin (ang1)
              #### To set start point of drag by view
                if type == "YZ":
                    x1 = x1 + XZ_xcenter
                    y1 = y1 + startgridpoint.tuple[1]
                    y0 = y0 + startgridpoint.tuple[2]
                if type == "XZ":
                    x1 = x1 + startgridpoint.tuple[0]
                    y1 = y1 + XY_ycenter
                    y0 = y0 + startgridpoint.tuple[2]
                if type == "XY":
                    x1 = x1 + startgridpoint.tuple[0]
                    y1 = y1 + startgridpoint.tuple[1]
                    y0 = y0 + XZ_zcenter

                C = quarkx.vect(x1, y1, y0)

                face = quarkx.newobj("object face:f")
                face.setthreepoints((A, B, C), 0)
                face.texturename = "[auto]" # gives texture to the face
                poly.appenditem(face)

   #### End of fan object creation area

      ## This line calls for the ruler
        for view in editor.layout.views:
            objectruler(editor, view, [poly])

        if self.view.info["type"] == "3D":
            for f in poly.subitems:
                f.swapsides()
        if self.x0-x == 0:
            return None, None
        return None, [poly]


### This section actually creates the finished object and drops it into the map.
### It also calls for the 3D view selection mode instead of creating object, causes lockup.

    def rectanglesel(self, editor, x,y, rectangle):

      ## Allows only selection rectangle in 3D views, not creation of fan - causes lockup

        type = self.view.info["type"]
        if type == "3D":
            view = self.view
            redcolor = RED
            todo = "R"
            plugins.mapdragmodes.EverythingRectSelDragObject(view, x, y, redcolor, todo).rectanglesel(editor, x, y, rectangle)
            return

      ## Creates actual fan object
        facecount = self.facecount # Gets value from above for message testing
        if facecount >= 65:
            quarkx.msgbox("This fan object contains\n" + str(facecount) + " faces\nexceeding the maximum limit\nof 64 and can not be created.", MT_ERROR, MB_CANCEL)
            return None, None

        for f in rectangle.faces:

            # Prepare to set the default texture on the faces

            f.texturename = "[auto]"

           ## This section resizes the texture so that their scales are 1,1 and their angles are 0,90.

            tp = f.threepoints(0)
            n = f.normal
            v = orthogonalvect(n, editor.layout.views[0])
            tp = (tp[0],
                  v * 128 + tp[0],
                  (n^v) * 128 + tp[0])
            f.setthreepoints(tp, 0)

      ## This section is for the option to hollow the object, actually Extrude, Make Hollow not as clean
        makehollow = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_makehollow"]
        if makehollow == "0":
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new fan object", "0")
        else:
            quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new fan object", "0")
            m = None
            plugins.mapcsg.ExtWall1click(m)


### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        import quarkpy.mdleditor
        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
            pass

        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    for r in self.redimages:
                        view.drawmap(r, mode)
                    type = view.info["type"]
                    if type == "3D":
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                    else:
                        import quarkpy.mdleditor
                        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
                            return
## This causes the red dragging shapes to be drawn
                        for r in self.redimages:
                            view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)


#####################################



class TorusMakerDragObject(parent):
    "A torus maker."

    Hint = hintPlusInfobaselink("Quick torus maker||Quick torus maker:\n\nAfter you click this button, you can draw a torus group on the map with the left mouse button and each torus will be turned into an actual poly.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.mapeditor.toolpalettes.objectmodes.html#torus")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1) # gives point on the grid
        p = view.proj(self.pt0) # converts to point on the screen view
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y
            self.z0 = p.z
    #
    # For setting stuff up at the beginning of a drag
    #
        self.startpoint = p # holds the starting point value (does not change)
        self.trigger = 0    # Sets trigger for editor.invalidateviews() for their 1 time cleanup, below.

### This draws the circle and red image and sets size as you drag across the view with LMB pressed.

    def buildredimages(self, x, y, flags, depth=None):
        editor = mapeditor()
        if editor is None:
            return None, None
        type = self.view.info["type"]

       ## This section creates the rectangle selector in the 3D view only
        if type == "3D":
            if x==self.x0 or y==self.y0:
                return None, None
            if depth is None:
                min, max = self.view.depth
                max = max - 0.0001
            else:
                min, max = depth
            pts = [self.view.space(self.x0, self.y0, min),
                   self.view.space(x, self.y0, min),
                   self.view.space(x, y, min),
                   self.view.space(self.x0, y, min)]
            pts.append(pts[0])
            pts2 = [self.view.space(self.x0, self.y0, max),
                    self.view.space(x, self.y0, max),
                    self.view.space(x, y, max),
                    self.view.space(self.x0, y, max)]
            if (x<self.x0)^(y<self.y0):
                pts.reverse()
                pts2.reverse()
            poly = quarkx.newobj("redbox:p")
            for i in (0,1,2,3):
                face = quarkx.newobj("side:f")
                face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
                poly.appenditem(face)
            face = quarkx.newobj("front:f")
            face.setthreepoints((pts[0], pts[3], pts[1]), 0)
            poly.appenditem(face)
            face = quarkx.newobj("back:f")
            face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
            poly.appenditem(face)
            if self.view.info["type"] == "3D":
                for f in poly.subitems:
                    f.swapsides()
            if poly.rebuildall() != (0,0):
                return None, None
            return None, [poly]


        ## point always means x, y and z values are given

        z = 0
        drag2gridpt = quarkpy.qhandles.aligntogrid(self.view.space(x, y, z), 1) # converts to point dragged to on grid
        startgridpoint = self.pt0 # gives starting point of drag on grid
        dragpointamount = drag2gridpt - startgridpoint # gives drag distance on grid for x, y and z
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))

        minrad = p  # mine
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        maxrad = p  # mine
        if p.visible:
            min = p.z
        max = min + dx

  ## Draws the circle
        cx, cy, cz = [], [], []
        mX, mY, mZ = minrad.tuple
        X, Y, Z = maxrad.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = self.view.proj(x,y,z)
                    cx.append(p.x)
                    cy.append(p.y)
                    cz.append(p.z)
        mX = minrad.tuple[0]
        mY = minrad.tuple[1]
        mZ = minrad.tuple[2]
        X = maxrad.tuple[0]
        Y = maxrad.tuple[1]
        Z = maxrad.tuple[2]
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        cz = (Z+mZ)*0.5
        X = int(X)      #py2.4
        Y = int(Y)      #py2.4
        Z = int(Z)      #py2.4
        cx = int(cx)    #py2.4
        cy = int(cy)    #py2.4
        cz = int(cz)    #py2.4
        mX = int(mX)    #py2.4
        mY = int(mY)    #py2.4
        mZ = int(mZ)    #py2.4
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)   #py2.4
        centerY = int(centerY)   #py2.4
        centerZ = int(centerZ)   #py2.4
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)  #py2.4
        radius = screengridstep

    ## This section sets up not to draw any faces if there are less than 3
        type = self.view.info["type"]
        if type == "XY":
            facecount = abs(int(dragpointamount.tuple[1]/actualgrid))
            if dragpointamount.tuple[0] == 0:
                facecount = 0
        else:
            facecount = abs(int(dragpointamount.tuple[2]/actualgrid))
            if type == "XZ" and dragpointamount.tuple[0] == 0 or type == "YZ" and dragpointamount.tuple[1] == 0:
                facecount = 0
        if facecount < 3:
            facecount = 0

    ## This section just cleans the single view we are in or all of the views if there are red faces to draw
    ## and sets up the trigger device for one final cleaning of all the views, below, to remove old red lines.
    ## The original trigger is set in the def of this class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.repaint() # this just cleans the current view if no object is being drawn
        else:
            for view in editor.layout.views:
                view.repaint()  # this cleans all the views and allows the redlines to be drawn
            if facecount < 3:
                facecount = 0
                self.trigger = 2
            else:
                self.trigger = 1

  #### This section sets up the curent view to draw the BLUE circle, lines, GREEN crosshairs and face lable
        cv = self.view.canvas()
        cv.pencolor = BLUE
        cv.brushstyle = BS_CLEAR

        # All code below given in screen values, not grid

    ## The next line draws the BLUE circle only
        cv.ellipse(centerX-radius, centerY-radius, centerX+radius+1, centerY+radius+1)

    ## This seciton draws all the BLUE grid lines, including the center ones
        if screengridstep != 0:
            segments = abs(radius/screengridstep)
        else:
            segments = 0
        drawline = float(int(segments))
        drawline = int(drawline)  #py2.4
        dif = segments - drawline
        if dif > .01 and dif < 1:
            drawline = drawline + 1
        while drawline >= 1:
            drawline = drawline - 1
            cv.line(centerX-radius, centerY+(screengridstep*drawline), centerX+radius, centerY+(screengridstep*drawline)) # draws X axis line on and ABOVE 0 in Z view
            cv.line(centerX+(screengridstep*drawline), centerY-radius, centerX+(screengridstep*drawline), centerY+radius) # draws Y axis line on and to the left of 0 in Z view
            if drawline <= 0:
                pass
            else:
                cv.line(centerX-radius, centerY-(screengridstep*drawline), centerX+radius, centerY-(screengridstep*drawline)) # draws X axis line BELOW 0 only in Z view
                cv.line(centerX-(screengridstep*drawline), centerY-radius, centerX-(screengridstep*drawline), centerY+radius) # draws Y axis line to the right of 0 only in Z view

    ## This section draws the cross hairs
        cv.penwidth = 1
        cv.pencolor = GREEN
        radius = 10
        cv.line(mX, cy, cx-radius, cy) # draws left screen X axis line
        cv.line(cx+radius, cy, X, cy)  # draws right screen X axis line
        cv.line(cx, mY, cx, cy-radius) # draws top screen Y axis line
        cv.line(cx, cy+radius, cx, Y)  # draws bottom screen Y axis line

    ## This section draws the face lable and gives the color warning scale
        cv.fontsize = 10
        cv.fontname = "MS Serif"
        cv.fontbold = 1

    ## This section adjust the face count for added faces and sections
    ## And provides some testing to avoid broken poly caused by those additions above

    #    ring_edges, seg_edges = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]
        ring_edges, seg_edges = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]) # fix for linux
    #    segments, rings = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"]
        segments, rings = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_segs_faces"]) # fix for linux
        if facecount == 0:
            sections = 0
            adjfacecount = 0
        else:
            sections = facecount + int(segments)
            adjfacecount = facecount + int(rings)
            if float(seg_edges) >= 4:
                if float(seg_edges) == 4 and adjfacecount >= 8:
                    adjfacecount = facecount = 7
                if float(seg_edges) >= 5 and adjfacecount >= 9:
                    adjfacecount = facecount = 8
            if float(ring_edges) >= 19 and adjfacecount >= 7 and adjfacecount != 8:
                adjfacecount = facecount = 8

        self.adjfacecount = adjfacecount # To pass value to def rectanglesel below for error message testing

    ## This section creates the color warning scale
        if adjfacecount > 10:
            cv.fontcolor = FUCHSIA
        if adjfacecount > 15:
            cv.fontcolor = PURPLE
        if adjfacecount > 19:
            cv.fontcolor = RED
        if adjfacecount < 11:
            cv.fontcolor = GREEN
        if type == "YZ":
            if dragpointamount.tuple[1] < 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(sections) + " segments, " + str(adjfacecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(sections) + " segments, " + str(adjfacecount) + " faces")
        else:
            if dragpointamount.tuple[0] > 0:
                cv.textout(cx+radius+5, cy-(radius*2), str(sections) + " segments, " + str(adjfacecount) + " faces")
            else:
                cv.textout(cx-(radius*6), cy-(radius*2), str(sections) + " segments, " + str(adjfacecount) + " faces")

    ## This section cleans all the views 1 time and is the last part of the trigger device further above
        if facecount == 0 and self.trigger == 2:
            for view in editor.layout.views:
                view.repaint()
                self.trigger = 0
                editor.invalidateviews()


  #### This section creates the actual object, using its formula
     #   (all code uses grid amounts for x, y and z positions)

    ## This section regulates the object (torus) size by the mouse drag

        if type == "YZ":
            objectsize = abs(dragpointamount.tuple[1])
        else:
            objectsize = abs(dragpointamount.tuple[0])

    ## This section gives the number of faces per layer and number of layers

        if type == "XY":
            sphere_res = abs(dragpointamount.tuple[1]/actualgrid)
        else:
            sphere_res = abs(dragpointamount.tuple[2]/actualgrid)
        sphere_res = int(sphere_res)   #py2.4

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

        torusgroup = quarkx.newobj("Torus:g")

    ### This section sets up the variable names with the dialog input values

           # 1 for both gives normal torus shape, 2 gives straight edges, 0 creates doubles-breaks
           # powers of sines and cosines
    #    ring_edges, seg_edges = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]
        ring_edges, seg_edges =  read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_ring_seg_edges"]) # fix for linux
        n1v = float(ring_edges)*.5  # shape of torus ring        # if this up to 10 other set to 1, breaks at 11 faces
        n2v = float(seg_edges)*.5  # shape of cross section of ring  # if this 2 other set to 1, breaks at 8 faces
                                                     # if this 2 other set to 2, breaks at 8 faces
                                                     # if this 2 other set to 3..., breaks at 8 faces
                                                     # if this 3 other set to 1, breaks at 9 faces
                                                     # if this 5 other set to 1, breaks at 9 faces

           # added segments (vertical)
           # added rings-faces (horizontal)
           # dialog input and adjustments for sections and adjfacecount done above
        segmentsv = sections
        ringsv = adjfacecount

           # scale factors in x,y and z direction
           # note: these are scale factors wrt to the mathematical function, not
           #       the parameterization
    #    xdistort, ydistort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"]
        xdistort, ydistort = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_xydistort"]) # fix for linux
    #    zdistort, updistort = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"]
        zdistort, updistort = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_zupdistort"]) # fix for linux
        rxv = float(xdistort)*.5 # works, makes oval left to right
        ryv = float(ydistort)*.5 # works, makes oval front to back
        rzv = float(zdistort)*.5 # works, makes oval top to bottom

           # ellipticity of segments, also scales in z-direction
           # zero gives no effect, positive 'tapers' the top, negative tapers the bottom
        elliptv = float(updistort)*.5  # only positive works makes straight hollow tube, neg. breaks

           # r0: base radius of the torus
           # r1: radius of cross section of ring
    #    hole, holesections = quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"]
        hole, holesections = read2values(quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_radiuses"]) # fix for linux
        r0v = float(hole)*.5 # works, makes bigger donut hole
        r1v = float(holesections)*.5 # works, makes fatter sections look, don't allow to pass donut hole - brakes

            ###################### Start of torus object creation area #######################

        dtheta = 2*pi/segmentsv
        dphi = 2*pi/ringsv

        # make verts
        verts = []
        for i in range(0,segmentsv):
            for j in range(0, ringsv):
                c1 = cos(i*dtheta)
                s1 = sin(i*dtheta)
                c2 = cos(j*dphi)
                s2 = sin(j*dphi)

                # make sure to take a fractional power of a negative number
                if c1 < 0:
                    c1m = -((-c1)**n1v)
                else:
                    c1m = c1**n1v
                if s1 < 0:
                    s1m = -((-s1)**n1v)
                else:
                    s1m = s1**n1v
                if c2 < 0:
                    c2m = -((-c2)**n2v)
                else:
                    c2m = c2**n2v
                if s2 < 0:
                    s2m = -((-s2)**n2v)
                else:
                    s2m = s2**n2v

                # x, y and z coordinates of the current vertex
                x = c1m*(r0v+r1v*c2m)*rxv
                y = s1m*(r0v+r1v*c2m)*ryv
                # modification from supertoroid primitve by substraction ellipt*c2m from r1*s2m
                z = (r1v*s2m-elliptv*c2m)*rzv

             #### Gets the center points of each view
                for view in editor.layout.views:
                    type = view.info["type"]
                    if type == "XZ":
                        XZ_xcenter = view.screencenter.tuple[0] # gives x center point used below for 2D view
                        XZ_zcenter = view.screencenter.tuple[2] # gives z center point used below for 2D view
                    if type == "XY":
                        XY_ycenter = view.screencenter.tuple[1] # gives y center point used below for 2D view

                type = self.view.info["type"]

             #### To set start point of drag by view
                if type == "YZ":
                    x = (x*objectsize)+XZ_xcenter
                    y = (y*objectsize)+startgridpoint.tuple[1]
                    z = (z*objectsize)+startgridpoint.tuple[2]

                if type == "XZ":
                    x = (x*objectsize)+startgridpoint.tuple[0]
                    y = (y*objectsize)+XY_ycenter
                    z = (z*objectsize)+startgridpoint.tuple[2]

                if type == "XY":
                    x = (x*objectsize)+startgridpoint.tuple[0]
                    y = (y*objectsize)+startgridpoint.tuple[1]
                    z = (z*objectsize)+XZ_zcenter

                v = quarkx.vect(x,y,z)
                verts.append(v)

                ############ Makes The Faces #############

        for i in range(0, segmentsv):
            poly = quarkx.newobj("torus"+`i`+":p")
            for j in range(0, ringsv):

                face = quarkx.newobj("group"+`i`+" face"+`j`+":f")

         ## This is original code, converted below, left here for future reference
              #A  face.v.append(verts[i*ringsv + j])
              #C  face.v.append(verts[i*ringsv + int(fmod(j+1, ringsv))])
              #D  face.v.append(verts[int(fmod((i+1)*ringsv, segmentsv*ringsv)) + int(fmod(j+1, ringsv))])
              #B  face.v.append(verts[int(fmod((i+1)*ringsv, segmentsv*ringsv)) + j])
              #   face.v.reverse()

         # This uses verts list crated above to set the face vector points
                A = (verts[i*ringsv + j])
                B = (verts[int(fmod((i+1)*ringsv, segmentsv*ringsv)) + j])
                C = (verts[i*ringsv + int(fmod(j+1, ringsv))])
                D = (verts[int(fmod((i+1)*ringsv, segmentsv*ringsv)) + int(fmod(j+1, ringsv))])

         # This actually sets the vector points for a face
                A = quarkx.vect(A.tuple[0],A.tuple[1],A.tuple[2])
                B = quarkx.vect(B.tuple[0],B.tuple[1],A.tuple[2])
                C = quarkx.vect(C.tuple[0],C.tuple[1],C.tuple[2])

                face.setthreepoints((A, B, C), 0)
                face.texturename = "[auto]" # gives texture to the face

                poly.appenditem(face)

                ############ Makes both ends #############

                if j == 0:
                    front2 = A
                if j <= ringsv*.5:
                    front1 = C
                    front3 = quarkx.vect(C.tuple[0],C.tuple[1],C.tuple[2]+(A.tuple[2]-C.tuple[2]))


                if j == 0:
                    back1 = B
                    back3 = quarkx.vect(B.tuple[0],B.tuple[1],B.tuple[2]+(A.tuple[2]-C.tuple[2]))
                if j <= (ringsv*.5)+1:
                    back2 = quarkx.vect(B.tuple[0],B.tuple[1],B.tuple[2]-A.tuple[2])


            frontface = quarkx.newobj("FrontFace:f")
            frontface.setthreepoints((front1, front2, front3), 0)
            frontface.texturename = "[auto]"
            poly.appenditem(frontface)

            face = quarkx.newobj("BackFace:f")
            face.setthreepoints((back1, back2, back3), 0)
            face.swapsides()  # turns face to outward direction
            face.texturename = "[auto]"
            poly.appenditem(face)

            torusgroup.appenditem(poly)

            ###################### End of torus object creation area #######################

      ## This line calls for the ruler
        for view in editor.layout.views:
            objectruler(editor, view, [torusgroup])

        if self.view.info["type"] == "3D":
            for f in poly.subitems:
                f.swapsides()
        if self.x0-x == 0:
            return None, None

      ### To remove any broken polys
        p = torusgroup
        list = p.findallsubitems("", ':p')+p.findallsubitems("", ':f')
        list = filter(lambda p: p.broken, list)
        faces = list
        for face in faces:
            if face.broken:
                face.parent.removeitem(face)

        return None, [torusgroup]


##This actually creates the finished object and drops it into the map.
### It also calls for the 3D view selection mode instead of creating object, causes lockup.

    def rectanglesel(self, editor, x,y, rectangle):

      ## Allows only selection rectangle in 3D views, not creation of torus - causes lockup
        type = self.view.info["type"]
        if type == "3D":
            view = self.view
            redcolor = RED
            todo = "R"
            plugins.mapdragmodes.EverythingRectSelDragObject(view, x, y, redcolor, todo).rectanglesel(editor, x, y, rectangle)
            return 

      ## Creates actual torus object
        adjfacecount = self.adjfacecount # Gets value from above for message testing
        if adjfacecount >= 65:
            quarkx.msgbox("This torus object contains\n" + str(adjfacecount) + " faces\nexceeding the maximum limit\nof 64 and can not be created.", MT_ERROR, MB_CANCEL)
            return None, None

        group = quarkx.newobj("Torus group:g")
        for poly in rectangle.subitems:

            for f in poly.faces:

            # Prepares to set the default texture on the faces
            #
                f.texturename = "[auto]"
            #
            # Resize the texture so that their scales are 1,1 and their angles are 0,90.
            #
                tp = f.threepoints(0)
                n = f.normal
                v = orthogonalvect(n, editor.layout.views[0])
                tp = (tp[0],
                      v * 128 + tp[0],
                      (n^v) * 128 + tp[0])
                f.setthreepoints(tp, 0)

            newpoly = poly.copy()

            group.appenditem(newpoly)
        quarkpy.mapbtns.dropitemsnow(editor, [group], "new torus group", "0")
        if quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_hollowtorus"] == "1":
            m = None
            plugins.mapcsg.ExtWall1click(m)


    def drawredimages(self, view, internal=0):
        editor = self.editor
        import quarkpy.mdleditor
        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
            pass

        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    for r in self.redimages:
                        view.drawmap(r, mode)
                    type = view.info["type"]
                    if type == "3D":
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                    else:
                        import quarkpy.mdleditor
                        if isinstance(editor, quarkpy.mdleditor.ModelEditor):
                            return
## This causes the red dragging shapes to be drawn
                        for r in self.redimages:
                            view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)



##############################################################
#
# The tool bar with the available object modes.
# Add other object modes from other plug-ins into this list :
#
            ## (the_object                          ,icon_index)
ObjectModes = [(SphereMakerDragObject               ,1)
              ,(PyramidMakerDragObject              ,2)
              ,(DoubleConeMakerDragObject           ,3)
              ,(CylinderMakerDragObject             ,4)
              ,(DomeMakerDragObject                 ,5)
              ,(FanMakerDragObject                  ,6)
              ,(TorusMakerDragObject                ,7) # If this Torus button number is changed
              ]                                         # be sure to also change it in the plugins\mapcsg.py file
                                                        # or the Hollow-No bulkheads dialog option will not work.
### This part effects each buttons selection mode and
### interacts with the Dragmodes and Terrainmodes toolbar buttons

def selectmode(btn):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    try:
        tb1 = editor.layout.toolbars["tb_objmodes"]
        tb2 = editor.layout.toolbars["tb_terrmodes"]
        tb3 = editor.layout.toolbars["tb_dragmodes"]
    except:
        return
    for b in tb1.tb.buttons:
        b.state = quarkpy.qtoolbar.normal
    select1(btn, tb1, editor)
    for b in tb2.tb.buttons:
        b.state = quarkpy.qtoolbar.normal
    for b in tb3.tb.buttons:
        b.state = quarkpy.qtoolbar.normal
    quarkx.update(editor.form)
    quarkx.setupsubset(SS_MAP, "Building").setint("ObjectMode", btn.i)
    quarkx.setupsubset(SS_MAP, "Building").setint("DragMode", 5)
    quarkx.setupsubset(SS_MAP, "Building").setint("TerrMode", 20)

def select1(btn, toolbar, editor):
    editor.MouseDragMode, dummyicon = ObjectModes[btn.i]
    btn.state = quarkpy.qtoolbar.selected
    editor.layout.explorer.sellist = []
    editor.layout.explorer.uniquesel = []
    editor.layout.explorer.selchanged()
    for view in editor.layout.views:
        if MapOption("CrossCursor", editor.MODE):
            view.cursor = CR_CROSS
            view.handlecursor = CR_ARROW
        else:
            view.cursor = CR_ARROW
            view.handlecursor = CR_CROSS

##### Below makes the toolbar and arainges its buttons #####

class ObjectModesBar(ToolBar):
    "The new toolbar with ObjectModes buttons."

    Caption = "Object modes"
    DefaultPos = ((0, 0, 0, 0), 'topdock', 362, 2, 2)

    def buildbuttons(self, layout):
                          # to build the single click button
        ico_dict['ico_objectmodes'] = LoadIconSet1("mapobjm", 1.0)
        ico_objectmodes = ico_dict['ico_objectmodes']

        BuildDialogbtn = qtoolbar.button(DialogClick, "Object Dialog Input||Object Dialog Input:\n\nThis will open a dialog input box for the 'Object modes Toolbar' item currently in use. Not all objects will use the same dialog input box. Which ever object button is active at the time this button is clicked, will produce that objects dialog input box.\n\nThese dialogs will remain open until they are closed manually.\n\nIf a particular object has its own dialog then that objects name will appear in the title. Other wise the standard ' Object Distortion Dialog ' will be used for all other objects.\n\nYou can have one or more dialogs open and active at a time. But they will only effect the objects that use them.", ico_objectmodes, 0, infobaselink="intro.mapeditor.toolpalettes.objectmodes.html#dialog")

                  # to build the Mode buttons
        btns = []
        for i in range(len(ObjectModes)):
            obj, icon = ObjectModes[i]
            btn = qtoolbar.button(selectmode, obj.Hint, ico_dict['ico_objectmodes'], icon)
            btn.i = i
            btns.append(btn)
        i = quarkx.setupsubset(SS_MAP, "Building").getint("ObjectMode")

        dm = quarkx.setupsubset(SS_MAP, "Building").getint("DragMode")
        tm = quarkx.setupsubset(SS_MAP, "Building").getint("TerrMode")
        if i == 20 or dm == 0 or tm == 0:
            leave = 0
        else:
            select1(btns[i], self, layout.editor)

        revbtns = [] # to put the single click Builderbtns first then the others.
        revbtns.append(BuildDialogbtn)
        revbtns = revbtns + btns

        return revbtns



#--- register the new toolbar ---

quarkpy.maptools.toolbars["tb_objmodes"] = ObjectModesBar


# ----------- REVISION HISTORY ------------
#
# $Log: mapobjectmodes.py,v $
# Revision 1.14  2008/09/12 19:08:40  cdunde
# Minor code cleanup.
#
# Revision 1.13  2008/02/22 09:52:21  danielpharos
# Move all finishdrawing code to the correct editor, and some small cleanups.
#
# Revision 1.12  2007/10/08 18:47:30  cdunde
# To stop both editor's Quick Object Makers from braking when zoomed in close.
#
# Revision 1.11  2006/11/30 01:17:48  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.10  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.9.2.2  2006/11/09 23:00:02  cdunde
# Updates to accept Python 2.4.4 by eliminating the
# Depreciation warning messages in the console.
#
# Revision 1.9.2.1  2006/11/01 22:22:42  danielpharos
# BackUp 1 November 2006
# Mainly reduce OpenGL memory leak
#
# Revision 1.9  2006/02/25 03:19:04  cdunde
# To fix Torus Hollow-No bulkheads function
# missed with addition of new items.
#
# Revision 1.8  2006/02/12 19:03:54  cdunde
# To add all new, updated and Infobase documentation files
# for new Object makers, Double-cone, Dome and Fan.
#
# Revision 1.7  2006/02/11 20:21:41  cdunde
# Changed Sphere hollow to extrude to substancialy increase speed
# and cleaned up code to also try and help with redline drawing speed.
#
# Revision 1.6  2006/02/10 04:03:26  cdunde
# To remove unneeded test code.
#
# Revision 1.5  2006/01/31 11:04:30  cdunde
# Fixed  distance displayed amount from drifting away from
# marker on screen view x-axis when the scale size is changed.
#
# Revision 1.4  2006/01/30 08:20:00  cdunde
# To commit all files involved in project with Philippe C
# to allow QuArK to work better with Linux using Wine.
#
# Revision 1.3  2006/01/17 19:25:45  cdunde
# To add all file updates for new Object modes
# dialog boxes hollowing functions.
#
# Revision 1.2  2006/01/13 07:12:48  cdunde
# To commit all new and updated Infobase docs and
# toolbar links for new Quick Object makers and toolbar.
#
# Revision 1.1  2006/01/12 07:21:01  cdunde
# To commit all new and related files for
# new Quick Object makers and toolbar.
#
#

