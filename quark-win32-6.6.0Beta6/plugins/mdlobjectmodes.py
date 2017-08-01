"""   QuArK  -  Quake Army Knife

Mouse drag Object modes
"""
#
# Copyright (C) 1996-2007 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mdlobjectmodes.py,v 1.21 2011/11/17 01:19:02 cdunde Exp $



Info = {
   "plug-in":       "Object Drag Modes",
   "desc":          "Creates objects by mouse dragging",
   "date":          "Sept. 16, 2007",
   "author":        "cdunde",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.5" }


import quarkx
import quarkpy.qtoolbar
import quarkpy.qhandles
from quarkpy.maputils import *
import quarkpy.mdltoolbars
import quarkpy.maphandles
import quarkpy.mapbtns
from math import pi, sin, cos, fmod
import mapdragmodes
import quarkpy.qbaseeditor
import quarkpy.dlgclasses
import quarkpy.mdlutils
import mdlgridscale
# For hollowing Torus
import quarkpy.mapcommands
import quarkpy.mapentities
import plugins.mapcsg

#
# Additionnal Quick Object Maker modes (other plug-ins may add other Quick Object Maker modes).
#

parent = quarkpy.qhandles.RectangleDragObject


### General def's that can be used by any Dialog ###

def newfinishdrawing(editor, view, oldfinish=quarkpy.mdleditor.ModelEditor.finishdrawing):
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
    size = (190,120)
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
        Hint = "Checking this box will make the object hollow"$0D
               "when the LMB is released, no end faces."$0D
               "This function only applies to"$0D
               "the Pyramid and Cylinder Objects."
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
        if (quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"] is None):
            src["distortion"] = "0"
            src["makehollow"] = "0"
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"] = src["distortion"]
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"] = src["makehollow"]
        else:
            src["distortion"] = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"]
            src["makehollow"] = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"]

        if src["distortion"]:
            distort = src["distortion"]
        else:
            distort = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"]

        if src["makehollow"]:
            makehollow = src["makehollow"]
        else:
            makehollow = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"]


    def action(self, editor=editor):
        distort = (self.src["distortion"])
        if distort is None:
            distort = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"]

        makehollow = (self.src["makehollow"])
        if makehollow is None:
            makehollow = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"]

      ### Save the settings...
        quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"] = distort
        quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"] = makehollow
        self.src["distortion"] = distort
        self.src["distortion"] = makehollow


    def onclosing(self, editor=editor):

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "3D":
                quarkpy.mdleditor.ModelEditor.finishdrawing = newfinishdrawing
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
    size = (190,300)
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
        if (quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_segs_faces"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_radiuses"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_zupdistort"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"] is None):
            src["segs_faces"] = "0 0"
            src["radiuses"] = "2 1"
            src["xydistort"] = "2 2"
            src["zupdistort"] = "2 0"
            src["ring_seg_edges"] = "2 2"
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_segs_faces"] = src["segs_faces"]
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_radiuses"] = src["radiuses"]
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"] = src["xydistort"]
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"] = src["zupdistort"]
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"] = src["ring_seg_edges"]
        else:
            src["segs_faces"] = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_segs_faces"]
            src["radiuses"] = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_radiuses"]
            src["xydistort"] = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"]
            src["zupdistort"] = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_zupdistort"]
            src["ring_seg_edges"] = quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"]


        if src["segs_faces"]:
            segments, rings = read2values(src["segs_faces"])
        else:
            segments, rings = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_segs_faces"])
        if src["radiuses"]:
            hole, sections = read2values(src["radiuses"])
        else:
            hole, sections = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_radiuses"])

        if src["xydistort"]:
            xdistort, ydistort = read2values(src["xydistort"])
        else:
            xdistort, ydistort = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"])

        if src["zupdistort"]:
            zdistort, updistort = read2values(src["zupdistort"])
        else:
            zdistort, updistort = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_zupdistort"])

        if src["ring_seg_edges"]:
            ring_edges, seg_edges = read2values(src["ring_seg_edges"])
        else:
            ring_edges, seg_edges = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"])


        self.src["segs_faces"] = "%.0f %.0f"%(segments, rings)
        self.src["radiuses"] = "%.1f %.1f"%(hole, sections)
        self.src["xydistort"] = "%.1f %.1f"%(xdistort, ydistort)
        self.src["zupdistort"] = "%.1f %.1f"%(zdistort, updistort)
        self.src["ring_seg_edges"] = "%.1f %.1f"%(ring_edges, seg_edges)


    def action(self, editor=editor):
        segments, rings = read2values(self.src["segs_faces"])
        if segments is None:
            segments, rings = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_segs_faces"])

        hole, sections = read2values(self.src["radiuses"])
        if hole is None:
            hole, sections = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_radiuses"])

        xdistort, ydistort = read2values(self.src["xydistort"])
        if xdistort is None:
            xdistort, ydistort = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"])

        zdistort, updistort = read2values(self.src["zupdistort"])
        if zdistort is None:
            zdistort, updistort = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_zupdistort"])

        ring_edges, seg_edges = read2values(self.src["ring_seg_edges"])
        if ring_edges is None:
            ring_edges, seg_edges = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"])

      ### Save the settings...
        if segments < 0:
            segments = 0
        if rings < 0:
            rings = 0
        else:
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_segs_faces"] = (str(segments) +" "+ str(rings))

        if hole < 1.0:
            hole = 1.0
        if sections >= hole:
            sections = hole - 0.5
        if sections < 0.5:
            sections = 0.5
        else:
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_radiuses"] = (str(hole) +" "+ str(sections))

        if xdistort < 1:
            xdistort = 1
        if ydistort < 1:
            ydistort = 1
        else:
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"] = (str(xdistort) +" "+ str(ydistort))

        if zdistort < 1:
            zdistort = 1
        if updistort < 0:
            updistort = 0
        else:
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_zupdistort"] = (str(zdistort) +" "+ str(updistort))

        if ring_edges < .5:
            ring_edges = .5
        if ring_edges >= 20:
            ring_edges = 20
        if seg_edges < .5:
            seg_edges = .5
        if seg_edges >= 20:
            seg_edges = 20
        else:
            quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"] = (str(ring_edges) +" "+ str(seg_edges))

        self.src["segs_faces"] = None
        self.src["radiuses"] = None
        self.src["xydistort"] = None
        self.src["zupdistort"] = None
        self.src["ring_seg_edges"] = None

    def onclosing(self, editor=editor):

        for view in editor.layout.views:
            type = view.info["type"]
            if type == "3D":
                quarkpy.mdleditor.ModelEditor.finishdrawing = newfinishdrawing
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
    if quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode") > 0 and quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode") < 8:
        if quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode") == 19:
            if editor.layout.explorer.sellist == []:
                quarkx.msgbox("No selection has been made.\n\nYou must first select an Object\nto activate this tool and\nchange your settings for this Object Maker.", MT_ERROR, MB_OK)
                return
            else:
                o = editor.layout.explorer.sellist
                m = qmenu.item("Dummy", None, "")
                m.o = o
                DistortionClick(m)

        elif quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode") < 7:

            m = qmenu.item("Dummy", None, "")
            DistortionClick(m)

        elif quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode") == 7:

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

       if not MapOption("All2DviewsRulers", SS_MODEL) and not MapOption("AllTopRulers", SS_MODEL) and not MapOption("AllSideRulers", SS_MODEL) and not MapOption("XviewRulers", SS_MODEL) and not MapOption("XyTopRuler", SS_MODEL) and not MapOption("XzSideRuler", SS_MODEL):
           return

       if not MapOption("AllSideRulers", SS_MODEL) and not MapOption("XzSideRuler", SS_MODEL):
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
           cv.textout(int(x),int(y),"0")
        # Prints above the right marker line the distance, on the Y axis
           x = view.proj(ylendt).tuple[0]
           y = view.proj(ylendt).tuple[1]-12
           dist = abs(y2-y1)
           cv.textout(int(x),int(y),quarkx.ftos(dist))


       if not MapOption("AllTopRulers", SS_MODEL) and not MapOption("XyTopRuler", SS_MODEL):
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
           cv.textout(int(x),int(y),"0")
        # Prints right of top marker line the distance, on the Z axis
           x = view.proj(yrendt).tuple[0]+8
           y = view.proj(yrendt).tuple[1]-2
           higth = abs(z2-z1)
           cv.textout(int(x),int(y),quarkx.ftos(higth))


# ===============
# Y view settings
# ===============

    elif type == "XZ":

       if not MapOption("All2DviewsRulers", SS_MODEL) and not MapOption("AllTopRulers", SS_MODEL) and not MapOption("AllSideRulers", SS_MODEL) and not MapOption("YviewRulers", SS_MODEL) and not MapOption("YxTopRuler", SS_MODEL) and not MapOption("YzSideRuler", SS_MODEL):
           return

       if not MapOption("AllSideRulers", SS_MODEL) and not MapOption("YzSideRuler", SS_MODEL):

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
           cv.textout(int(x),int(y),"0")
        # Prints above the right marker line the distance, on the X axis
           x = view.proj(xrendt).tuple[0]
           y = view.proj(xrendt).tuple[1]-12
           dist = abs(x1-x2)
           cv.textout(int(x),int(y),quarkx.ftos(dist))


       if not MapOption("AllTopRulers", SS_MODEL) and not MapOption("YxTopRuler", SS_MODEL):
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
           cv.textout(int(x),int(y),"0")
        # Prints right of top marker line the distance, on the Y axis
           x = view.proj(yrendt).tuple[0]+8
           y = view.proj(yrendt).tuple[1]-2
           higth = abs(z2-z1)
           cv.textout(int(x),int(y),quarkx.ftos(higth))


# ===============
# Z view settings
# ===============

    elif type == "XY":

       if not MapOption("All2DviewsRulers", SS_MODEL) and not MapOption("AllTopRulers", SS_MODEL) and not MapOption("AllSideRulers", SS_MODEL) and not MapOption("ZviewRulers", SS_MODEL) and not MapOption("ZxTopRuler", SS_MODEL) and not MapOption("ZySideRuler", SS_MODEL):
           return

       if not MapOption("AllSideRulers", SS_MODEL) and not MapOption("ZySideRuler", SS_MODEL):
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
           cv.textout(int(x),int(y),"0")
        # Prints above the right marker line the distance, on the X axis
           x = view.proj(xrendt).tuple[0]
           y = view.proj(xrendt).tuple[1]-12
           dist = abs(x1-x2)
           cv.textout(int(x),int(y),quarkx.ftos(dist))


       if not MapOption("AllTopRulers", SS_MODEL) and not MapOption("ZxTopRuler", SS_MODEL):
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
           cv.textout(int(x),int(y),"0")
        # Prints right of top marker line the distance, on the Y axis
           x = view.proj(yrendt).tuple[0]+8
           y = view.proj(yrendt).tuple[1]-2
           higth = abs(y2-y1)
           cv.textout(int(x),int(y),quarkx.ftos(higth))

    else:
       return



###################################

class SphereMakerDragObject(parent):
    "A sphere maker."

    Hint = hintPlusInfobaselink("Quick sphere maker||Quick sphere maker:\n\nAfter you click this button, you can create sphere model objects in the editor with the left mouse button. Each sphere will be added to the component that is currently selected.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.\nLarge number of faces may 'freeze' QuArK up, but it will return.", "intro.modeleditor.toolpalettes.objectmodes.html#sphere")

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
        X = int(X)
        Y = int(Y)
        Z = int(Z)
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        mX = int(mX)
        mY = int(mY)
        mZ = int(mZ)
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)
        centerY = int(centerY)
        centerZ = int(centerZ)
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)
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
    ## The original trigger is set in the def of this Sphere class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.handles = []
            quarkpy.mdleditor.setsingleframefillcolor(editor, self.view)
            self.view.repaint() # this just cleans the current view if no object is being drawn
            mdlgridscale.gridfinishdrawing(editor, self.view)
        else:
            if facecount < 3 and self.trigger > 0:
                facecount = 0
                self.trigger = self.trigger - 1
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)
            else:
                self.trigger = 2
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)

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
            drawline = int(drawline)
            screengridstep = int(screengridstep)
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
            view.handles = []
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()
                mdlgridscale.gridfinishdrawing(editor, v)
                self.trigger = 0


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
        sphere_res = int(sphere_res)

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"])
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

    #### This line calls for the ruler
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

      ## This section calls to convert the Sphere drag object for the Model Editor.
        ConvertPolyObject(editor, [rectangle], self.view.flags, self.view, "new sphere", 1, facecount)


### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    ## This draws the red dragging shapes during a pause and at the end of drag.
                    for v in editor.layout.views:
                        for r in self.redimages:
                            v.drawmap(r, mode, self.redcolor)
## This causes the red dragging shapes to be drawn, but also draws wrong on pause sometimes.
             #   else:
             #       if editor is not None:
             #           for v in editor.layout.views:
             #               for r in self.redimages:
             #                   v.drawmap(r, mode, self.redcolor)

#####################################


class PyramidMakerDragObject(parent):
    "A pyramid-cone maker."

    Hint = hintPlusInfobaselink("Quick pyramid-cone maker||Quick pyramid-cone maker:\n\nAfter you click this button, you can create pyramids-cones model objects in the editor with the left mouse button. Each pyramid-cone will be added to the component that is currently selected.\n\nThe more sides that are added the more it becomes a cone shape.\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.\nClick ' InfoBase ' for special vertex movement details.", "intro.modeleditor.toolpalettes.objectmodes.html#pyramid_cone")

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
        X = int(X)
        Y = int(Y)
        Z = int(Z)
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        mX = int(mX)
        mY = int(mY)
        mZ = int(mZ)
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)
        centerY = int(centerY)
        centerZ = int(centerZ)
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)
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
    ## The original trigger is set in the def of this Pyramid class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.handles = []
            quarkpy.mdleditor.setsingleframefillcolor(editor, self.view)
            self.view.repaint() # this just cleans the current view if no object is being drawn
            mdlgridscale.gridfinishdrawing(editor, self.view)
        else:
            if facecount < 3 and self.trigger > 0:
                facecount = 0
                self.trigger = self.trigger - 1
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)
            else:
                self.trigger = 2
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)

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
            view.handles = []
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()
                mdlgridscale.gridfinishdrawing(editor, v)
                self.trigger = 0


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
        sphere_res = int(sphere_res)

       ## Stops faces from being drawn if there are less then 3, can't make a poly with only 2 faces
        if facecount < 3:
            return None, None

     ## This is the Dialog box input factor that effects the length shape
        factor = float(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"])
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

      ## End of Pyramid object creation section

    #### This line calls for the ruler
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

      ## This section calls to convert the Pyramid drag object for the Model Editor.
        ConvertPolyObject(editor, [rectangle], self.view.flags, self.view, "new pyramid", 1, facecount)



### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    ## This draws the red dragging shapes during a pause and at the end of drag.
                    for v in editor.layout.views:
                        for r in self.redimages:
                            v.drawmap(r, mode, self.redcolor)
## This causes the red dragging shapes to be drawn, but also draws wrong on pause sometimes.
             #   else:
             #       if editor is not None:
             #           for v in editor.layout.views:
             #               for r in self.redimages:
             #                   v.drawmap(r, mode, self.redcolor)


###################################

class DoubleConeMakerDragObject(parent):
    "A double-cone maker."

    Hint = hintPlusInfobaselink("Quick double-cone maker||Quick double-cone maker:\n\nAfter you click this button, you can create double-cones model objects in the editor with the left mouse button. Each double-cone will be added to the component that is currently selected.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.modeleditor.toolpalettes.objectmodes.html#double_cone")

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
        X = int(X)
        Y = int(Y)
        Z = int(Z)
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        mX = int(mX)
        mY = int(mY)
        mZ = int(mZ)
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)
        centerY = int(centerY)
        centerZ = int(centerZ)
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)
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
    ## The original trigger is set in the def of this DoubleCone class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.handles = []
            quarkpy.mdleditor.setsingleframefillcolor(editor, self.view)
            self.view.repaint() # this just cleans the current view if no object is being drawn
            mdlgridscale.gridfinishdrawing(editor, self.view)
        else:
            if facecount < 3 and self.trigger > 0:
                facecount = 0
                self.trigger = self.trigger - 1
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)
            else:
                self.trigger = 2
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)

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
        drawline = int(drawline)
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
            view.handles = []
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()
                mdlgridscale.gridfinishdrawing(editor, v)
                self.trigger = 0


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
        factor = float(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"])
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

   #### End of Double-cone object creation area

    #### This line calls for the ruler
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

      ## This section calls to convert the Double-cone drag object for the Model Editor.
        ConvertPolyObject(editor, [rectangle], self.view.flags, self.view, "new double-cone", 1, facecount)



### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    ## This draws the red dragging shapes during a pause and at the end of drag.
                    for v in editor.layout.views:
                        for r in self.redimages:
                            v.drawmap(r, mode, self.redcolor)
## This causes the red dragging shapes to be drawn, but also draws wrong on pause sometimes.
             #   else:
             #       if editor is not None:
             #           for v in editor.layout.views:
             #               for r in self.redimages:
             #                   v.drawmap(r, mode, self.redcolor)


###################################


class CylinderMakerDragObject(parent):
    "A cylinder maker."

    Hint = hintPlusInfobaselink("Quick cylinder maker||Quick cylinder maker:\n\nAfter you click this button, you can create cylinder model objects in the editor with the left mouse button. Each cylinder will be added to the component that is currently selected. This can make angled sides or a more curved style cylinder by adding more faces.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.modeleditor.toolpalettes.objectmodes.html#cylinder")

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
        X = int(X)
        Y = int(Y)
        Z = int(Z)
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        mX = int(mX)
        mY = int(mY)
        mZ = int(mZ)
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)
        centerY = int(centerY)
        centerZ = int(centerZ)

        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)
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
    ## The original trigger is set in the def of this Cylinder class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.handles = []
            quarkpy.mdleditor.setsingleframefillcolor(editor, self.view)
            self.view.repaint() # this just cleans the current view if no object is being drawn
            mdlgridscale.gridfinishdrawing(editor, self.view)
        else:
            if facecount < 3 and self.trigger > 0:
                facecount = 0
                self.trigger = self.trigger - 1
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)
            else:
                self.trigger = 2
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)

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
        drawline = int(drawline)
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
            view.handles = []
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()
                mdlgridscale.gridfinishdrawing(editor, v)
                self.trigger = 0


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
        factor = float(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"])
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

   #### End of Cylinder object creation area

    #### This line calls for the ruler
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

      ## This section calls to convert the Cylinder drag object for the Model Editor.
        ConvertPolyObject(editor, [rectangle], self.view.flags, self.view, "new cylinder", 1, facecount)

### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    ## This draws the red dragging shapes during a pause and at the end of drag.
                    for v in editor.layout.views:
                        for r in self.redimages:
                            v.drawmap(r, mode, self.redcolor)
## This causes the red dragging shapes to be drawn, but also draws wrong on pause sometimes.
             #   else:
             #       if editor is not None:
             #           for v in editor.layout.views:
             #               for r in self.redimages:
             #                   v.drawmap(r, mode, self.redcolor)

###################################

class DomeMakerDragObject(parent):
    "A dome maker."

    Hint = hintPlusInfobaselink("Quick dome maker||Quick dome maker:\n\nAfter you click this button, you can create dome model objects in the editor with the left mouse button. Each dome will be added to the component that is currently selected.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.modeleditor.toolpalettes.objectmodes.html#dome")

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
        X = int(X)
        Y = int(Y)
        Z = int(Z)
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        mX = int(mX)
        mY = int(mY)
        mZ = int(mZ)
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)
        centerY = int(centerY)
        centerZ = int(centerZ)
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)
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
    ## The original trigger is set in the def of this Dome class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.handles = []
            quarkpy.mdleditor.setsingleframefillcolor(editor, self.view)
            self.view.repaint() # this just cleans the current view if no object is being drawn
            mdlgridscale.gridfinishdrawing(editor, self.view)
        else:
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()  # this cleans all the views and allows the redlines to be drawn
                mdlgridscale.gridfinishdrawing(editor, v)
            if facecount < 3:
                facecount = 0
                self.trigger = 2
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)
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
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()
                mdlgridscale.gridfinishdrawing(editor, v)
                self.trigger = 0


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
        factor = float(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"])
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

   #### End of Dome object creation area

    #### This line calls for the ruler
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

      ## This section calls to convert the Dome drag object for the Model Editor.
        ConvertPolyObject(editor, [rectangle], self.view.flags, self.view, "new dome", 1, facecount)



### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    ## We don't want internal when it equals one, so we just return.
                    return
                ## This causes the red dragging shapes to be drawn.
                else:
                    if editor is not None:
                        for v in editor.layout.views:
                            for r in self.redimages:
                                v.drawmap(r, mode, self.redcolor)


#####################################


class FanMakerDragObject(parent):
    "A fan maker."

    Hint = hintPlusInfobaselink("Quick fan maker||Quick fan maker:\n\nAfter you click this button, you can create fan model objects in the editor with the left mouse button. Each fan will be added to the component that is currently selected.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.modeleditor.toolpalettes.objectmodes.html#fan")

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
        X = int(X)
        Y = int(Y)
        Z = int(Z)
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        mX = int(mX)
        mY = int(mY)
        mZ = int(mZ)
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)
        centerY = int(centerY)
        centerZ = int(centerZ)
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)
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
    ## The original trigger is set in the def of this Fan class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.handles = []
            quarkpy.mdleditor.setsingleframefillcolor(editor, self.view)
            self.view.repaint() # this just cleans the current view if no object is being drawn
            mdlgridscale.gridfinishdrawing(editor, self.view)
        else:
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()  # this cleans all the views and allows the redlines to be drawn
                mdlgridscale.gridfinishdrawing(editor, v)
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
        drawline = int(drawline)
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
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()
                mdlgridscale.gridfinishdrawing(editor, v)
                self.trigger = 0


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
        factor = float(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"])
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

        editor = mapeditor()
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
        trinbr = 1
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

                    face = quarkx.newobj("triangle top "+str(trinbr)+" :f")
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

                    face = quarkx.newobj("triangle bottom "+str(trinbr)+" :f")
                    face.setthreepoints((A, B, C), 0)
                    face.texturename = "[auto]" # gives texture to the face
                    poly.appenditem(face)
                    trinbr = trinbr + 1

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

   #### End of Fan object creation area

    #### This line calls for the ruler
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

      ## This section calls to convert the Fan drag object for the Model Editor.
        ConvertPolyObject(editor, [rectangle], self.view.flags, self.view, "new fan", 3, facecount)


### This section needs to be here to retain the BLUE circle and lines when you pause in a drag

    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    ## We don't want internal when it equals one, so we just return.
                    return
                ## This causes the red dragging shapes to be drawn.
                else:
                    if editor is not None:
                        for v in editor.layout.views:
                            for r in self.redimages:
                                v.drawmap(r, mode, self.redcolor)

#####################################



class TorusMakerDragObject(parent):
    "A torus maker."

    Hint = hintPlusInfobaselink("Quick torus maker||Quick torus maker:\n\nAfter you click this button, you can create torus model objects in the editor with the left mouse button. Each torus will be added to the component that is currently selected.\n\nMove the mouse forward to add more faces, backwards for fewer faces, right to make it larger and left to make it smaller.\n\nNOTE: Less than 3 faces will not draw anything.", "intro.modeleditor.toolpalettes.objectmodes.html#torus")

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
        X = int(X)
        Y = int(Y)
        Z = int(Z)
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        mX = int(mX)
        mY = int(mY)
        mZ = int(mZ)
        dx = X-cx
        dy = Y-cy
        dz = Z-cz

        centerX = self.startpoint.tuple[0] # given in screen value
        centerY = self.startpoint.tuple[1] # given in screen value
        centerZ = self.startpoint.tuple[2] # given in screen value
        centerX = int(centerX)
        centerY = int(centerY)
        centerZ = int(centerZ)
        actualgrid = mapeditor().gridstep
        if not actualgrid:
            actualgrid = 1.0
        screengrid = self.view.proj(actualgrid,actualgrid,actualgrid)
        screengridstep = screengrid.tuple[2] # have to use Z because others change value
        screengridstep = int(screengridstep)
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
    ## The original trigger is set in the def of this Torus class, above.
        if facecount == 0 and self.trigger == 0:
            self.view.handles = []
            quarkpy.mdleditor.setsingleframefillcolor(editor, self.view)
            self.view.repaint() # this just cleans the current view if no object is being drawn
            mdlgridscale.gridfinishdrawing(editor, self.view)
        else:
            if facecount < 3 and self.trigger > 0:
                facecount = 0
                self.trigger = self.trigger - 1
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)
            else:
                self.trigger = 2
                for v in editor.layout.views:
                    v.handles = []
                    quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()  # this cleans all the views and allows the redlines to be drawn
                    mdlgridscale.gridfinishdrawing(editor, v)


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

        ring_edges, seg_edges = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"])
        segments, rings = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_segs_faces"])
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
            for v in editor.layout.views:
                v.handles = []
                quarkpy.mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()
                mdlgridscale.gridfinishdrawing(editor, v)
                self.trigger = 0


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
        ring_edges, seg_edges =  read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_ring_seg_edges"])
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
        xdistort, ydistort = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_xydistort"])
        zdistort, updistort = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_zupdistort"])
        rxv = float(xdistort)*.5 # works, makes oval left to right
        ryv = float(ydistort)*.5 # works, makes oval front to back
        rzv = float(zdistort)*.5 # works, makes oval top to bottom

           # ellipticity of segments, also scales in z-direction
           # zero gives no effect, positive 'tapers' the top, negative tapers the bottom
        elliptv = float(updistort)*.5  # only positive works makes straight hollow tube, neg. breaks

           # r0: base radius of the torus
           # r1: radius of cross section of ring
        hole, holesections = read2values(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_torus_radiuses"])
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

            ###################### End of Torus object creation area #######################

    #### This line calls for the ruler
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
        #        f.texturename = "[auto]"
                if editor.Root.currentcomponent is not None and editor.Root.currentcomponent.currentskin is not None:
                    f.texturename = editor.Root.currentcomponent.currentskin.shortname
                else:
                    f.texturename = "None"
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
        ConvertPolyObject(editor, [group], self.view.flags, self.view, "new torus", 2)


    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    ## This draws the red dragging shapes during a pause and at the end of drag.
                    for v in editor.layout.views:
                        for r in self.redimages:
                            v.drawmap(r, mode, self.redcolor)
## This causes the red dragging shapes to be drawn, but also draws wrong on pause sometimes.
             #   else:
             #       if editor is not None:
             #           for v in editor.layout.views:
             #               for r in self.redimages:
             #                   v.drawmap(r, mode, self.redcolor)

class DeactivateDragObject(quarkpy.mdlhandles.RectSelDragObject):
    "This is just a place holder to turn off the Object Maker."

    Hint = hintPlusInfobaselink("Deactivator button||Deactivator button:\n\nTo return to regular operation mode you must click this button to turn 'Off' the 'Quick Object Maker'. To reactivate it simply click on any of the 'Quick Object Maker' shapes you wish to use.", "intro.modeleditor.toolpalettes.objectmodes.html#deactivator")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)


##############################################################
#
# The tool bar with the available object modes.
# Add other object modes from other plug-ins into this list :
#
            ## (the_object                          ,icon_index)
ObjectModes = [(DeactivateDragObject                ,8)
              ,(SphereMakerDragObject               ,1)
              ,(PyramidMakerDragObject              ,2)
              ,(DoubleConeMakerDragObject           ,3)
              ,(CylinderMakerDragObject             ,4)
              ,(DomeMakerDragObject                 ,5)
              ,(FanMakerDragObject                  ,6)
              ,(TorusMakerDragObject                ,7) # If this Torus button number is changed
              ]                                         # be sure to also change it in the plugins\mapcsg.py file
                                                        # or the Hollow-No bulkheads dialog option will not work.
### This part effects each buttons selection mode and
### interacts with other toolbar buttons

def selectmode(btn):
    editor = mapeditor(SS_MODEL)
    if editor is None: return
    try:
        tb1 = editor.layout.toolbars["tb_objmodes"]
        tb2 = editor.layout.toolbars["tb_paintmodes"]
        tb3 = editor.layout.toolbars["tb_animation"]
        tb4 = editor.layout.toolbars["tb_edittools"]
        tb5 = editor.layout.toolbars["tb_AxisLock"]
    except:
        return
    for b in tb1.tb.buttons:
        b.state = quarkpy.qtoolbar.normal
    select1(btn, tb1, editor)
    for b in range(len(tb2.tb.buttons)):
        tb2.tb.buttons[b].state = quarkpy.qtoolbar.normal
    for b in range(len(tb3.tb.buttons)):
        if b == 0 or b == 5:
            tb3.tb.buttons[b].state = quarkpy.qtoolbar.normal
    for b in range(len(tb4.tb.buttons)):
        if b == 7:
            tb4.tb.buttons[b].state = quarkpy.qtoolbar.normal
    for b in range(len(tb5.tb.buttons)):
        if b == 5:
            tb5.tb.buttons[b].state = quarkpy.qtoolbar.normal
    quarkx.update(editor.form)
    quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", btn.i)
    quarkx.setupsubset(SS_MODEL, "Building").setint("PaintMode", 0)
    quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
    quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
    from quarkpy.mdlanimation import playlist, playNR
    if quarkpy.mdlanimation.playlist != []:
        editor.layout.explorer.sellist = quarkpy.mdlanimation.playlist
        quarkpy.mdlanimation.playNR = 0
        quarkpy.mdlanimation.playlist = []
    quarkx.settimer(quarkpy.mdlanimation.drawanimation, editor, 0)
    quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] = None
    quarkx.setupsubset(SS_MODEL, "Options")['AnimationCFGActive'] = None
    quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] = None

def select1(btn, toolbar, editor):
    editor.MouseDragMode, dummyicon = ObjectModes[btn.i]
    btn.state = quarkpy.qtoolbar.selected
    for view in editor.layout.views:
        if MapOption("CrossCursor", SS_MODEL):
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
        if not ico_dict.has_key('ico_objectmodes'):
            ico_dict['ico_objectmodes']=LoadIconSet1("mdlobjm", 1.0)
        ico_objectmodes = ico_dict['ico_objectmodes']

        BuildDialogbtn = qtoolbar.button(DialogClick, "Object Dialog Input||Object Dialog Input:\n\nThis will open a dialog input box for the 'Object modes Toolbar' item currently in use. Not all objects will use the same dialog input box. Which ever object button is active at the time this button is clicked, will produce that objects dialog input box.\n\nThese dialogs will remain open until they are closed manually.\n\nIf a particular object has its own dialog then that objects name will appear in the title. Other wise the standard ' Object Distortion Dialog ' will be used for all other objects.\n\nYou can have one or more dialogs open and active at a time. But they will only effect the objects that use them.", ico_objectmodes, 0, infobaselink="intro.modeleditor.toolpalettes.objectmodes.html#dialog")

              # to build the Mode buttons
        btns = []
        for i in range(len(ObjectModes)):
            obj, icon = ObjectModes[i]
            btn = qtoolbar.button(selectmode, obj.Hint, ico_objectmodes, icon)
            btn.i = i
            btns.append(btn)
        i = quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode")

        select1(btns[i], self, layout.editor)

        revbtns = [] # to put the single click Builderbtns first then the others.
        revbtns.append(BuildDialogbtn)
        revbtns = revbtns + btns

        return revbtns



#--- register the new toolbar ---

quarkpy.mdltoolbars.toolbars["tb_objmodes"] = ObjectModesBar


# This section does the conversion from "redpolys" created during a drag
#    to triangles that the Model Editor can use.
# The "newobjectslist" list, which can be a single poly object or a "group" of polys,
#    in the functions "rectanglesel" section is passed to here where it is converted back to
#    usable model component mesh vertexes and the final 'ok' function is performed.
# option=1 does the conversion of an 'Object Maker Poly' for single polys, except for the "Fan".
# option=2 does the conversion of group 'Object Maker Polys' for "group" polys, which is the Torus.
# option=3 does the conversion of an 'Object Maker Poly' for the "Fan" only.

def ConvertPolyObject(editor, newobjectslist, flags, view, undomsg, option=1, nbroffaces=0):

    # This area does the conversion of SINGLE ITEM 'Object Maker Polys' for the Editor,
    #    which are all of the object shapes except the Fan and Torus.
    if option == 1:
        # This first part does the convertion from poly back to Model Editor usable triangles & vertexes.
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames

        # First we go through all of the vertexes of the new poly object
        #    and create vertexes that the Model Editor knows how to use.
        new_vtxs = []
        topface_center_vtx = baseface_center_vtx = None
        for poly in newobjectslist:
            for vtx in range(len(poly.vertices)):
                v = poly.vertices[vtx]
                vertex = quarkx.vect(v.tuple[0], v.tuple[1], v.tuple[2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
                new_vtxs.append(vertex)

            if quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"] != "1":
                if poly.name == "pyramid:p":
                    baseface_center_vtx = quarkx.vect(poly.vertices[1].tuple[0], poly.vertices[1].tuple[1], poly.vertices[0].tuple[2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
                    new_vtxs.append(baseface_center_vtx)

                if poly.name == "cylinder:p":
                    face = poly.subitems[len(poly.subitems)-1]
                    bbmax, bbmin = quarkx.boundingboxof([face])
                    pointX = ((bbmax.tuple[0]-bbmin.tuple[0])*.5)+bbmin.tuple[0]
                    pointY = ((bbmax.tuple[1]-bbmin.tuple[1])*.5)+bbmin.tuple[1]
                    topface_center_vtx = quarkx.vect(pointX, pointY, poly.vertices[1].tuple[2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
                    new_vtxs.append(topface_center_vtx)
                    baseface_center_vtx = quarkx.vect(pointX, pointY, poly.vertices[0].tuple[2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
                    new_vtxs.append(baseface_center_vtx)

        # second we add those new vertex points to each of the currentcomponent's frames.
        for compframe in range(len(compframes)):
            if compframes[compframe] == 0:
                compframes[compframe].vertices = new_vtxs
            else:
                compframes[compframe].vertices = compframes[compframe].vertices + new_vtxs
            compframes[compframe].compparent = new_comp # To allow frame relocation after editing.

        if poly.name == "pyramid:p":
            baseface_index = len(compframes[0].vertices)-1
        if poly.name == "cylinder:p":
            topface_index = len(compframes[0].vertices)-2
            baseface_index = len(compframes[0].vertices)-1

        # Third we use that list of new vertexes to make the new faces,
        #    some of which are already triangles for some objects.
        # This part gives some kind of view to set skin positions by
        #    for the Skin-view if it has not been opened yet
        #    and the option to skin from the editors3Dview for an infinite variations of angles.
        from quarkpy.mdlhandles import SkinView1
        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
            for v in editor.layout.views:
                if v.info["viewname"] == "editors3Dview":
                    cordsview = v
        else:
            try:
                tex = comp.currentskin
                texWidth,texHeight = tex["Size"]
                if quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] == "1":
                    SkinViewScale = SkinView1.info["scale"]
                else:
                    SkinViewScale = 1
            except:
                texWidth,texHeight = SkinView1.clientarea
                SkinViewScale = 1

        newtris = []
        if undomsg.startswith('new dome'):
            if nbroffaces < 5:
                rings = nbroffaces - 3
            else:
                setting = int(quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_distortion"])
                if setting > 1:
                    if nbroffaces - 3 <= setting:
                        rings = nbroffaces - 3
                    else:
                        rings = setting
                else:
                    rings = 1
        elif undomsg.startswith('new pyramid') or undomsg.startswith('new double-cone'):
            rings = 0
        elif undomsg.startswith('new cylinder'):
            rings = 1
        else:
            rings = nbroffaces - 3
        if rings != 0:
            ringcount = 1
        else:
            ringcount = 0
        columncount = 1
        vtxcount = 0
        face = 1
        extvtx = len(comp.currentframe.vertices)

        while columncount < nbroffaces+1:
            # Here we qualify objects that do and do not have triangle faces at their top.
            if undomsg.startswith('new cylinder'):
                break
            else:
                # This part makes the top & bottom triangles that are needed per column.
                if columncount == 1:
                    if ringcount == 0:
                        if undomsg.startswith('new pyramid'):
                            topvtx0 = columncount+1
                            topvtx1 = 1
                            topvtx2 = columncount-1
                        else:
                            topvtx0 = 2
                            topvtx1 = 1
                            topvtx2 = 0
                            bottomvtx0 = 4
                            bottomvtx1 = 2
                            bottomvtx2 = 0
                    else:
                        topvtx0 = 2
                        topvtx1 = 1
                        topvtx2 = 0
                        bottomvtx0 = 5
                        bottomvtx1 = 4
                        bottomvtx2 = 3
                elif columncount == 2:
                    if ringcount == 0:
                        if undomsg.startswith('new pyramid'):
                            topvtx0 = 0
                            topvtx1 = 1
                            topvtx2 = columncount+1
                        else:
                            topvtx0 = 3
                            topvtx1 = 1
                            topvtx2 = 2
                            bottomvtx0 = 4
                            bottomvtx1 = 3
                            bottomvtx2 = 2
                    else:
                        topvtx0 = 6
                        topvtx1 = 0
                        topvtx2 = 1
                        bottomvtx0 = 7
                        bottomvtx1 = 3
                        bottomvtx2 = 4
                elif columncount == nbroffaces:
                    if ringcount == 0:
                        if undomsg.startswith('new pyramid'):
                            topvtx0 = columncount
                            topvtx1 = 1
                            topvtx2 = 2
                        elif undomsg.startswith('new double-cone'):
                            if nbroffaces == 3:
                                topvtx0 = columncount
                                topvtx1 = 0
                                topvtx2 = 1
                                bottomvtx0 = topvtx1
                                bottomvtx1 = topvtx0
                                bottomvtx2 = 4
                            elif nbroffaces == 4:
                                topvtx0 = columncount+1
                                topvtx1 = 0
                                topvtx2 = 1
                                bottomvtx0 = topvtx1
                                bottomvtx1 = topvtx0
                                bottomvtx2 = 4
                            else:
                                topvtx0 = 5
                                topvtx1 = 0
                                topvtx2 = 1
                                bottomvtx0 = topvtx1
                                bottomvtx1 = topvtx0
                                bottomvtx2 = 4
                        else:
                            topvtx0 = 3
                            topvtx1 = 0
                            topvtx2 = 1
                            bottomvtx0 = 4
                            bottomvtx1 = 0
                            bottomvtx2 = 3
                    else:
                        topvtx0 = nbroffaces*2
                        topvtx1 = 1
                        topvtx2 = 2
                        bottomvtx0 = nbroffaces*2+1
                        bottomvtx1 = 4
                        bottomvtx2 = 5
                else:
                    if undomsg.startswith('new pyramid'):
                        topvtx0 = columncount
                        topvtx1 = 1
                        topvtx2 = columncount+1
                    else:
                        if undomsg.startswith('new double-cone'):
                            if columncount == 3:
                                topvtx0 = columncount
                                if nbroffaces == 4:
                                    topvtx1 = topvtx0+2
                                else:
                                    topvtx1 = topvtx0+3
                                bottomvtx0 = topvtx1
                                bottomvtx1 = topvtx0
                            elif columncount == 4 and nbroffaces == 4:
                                topvtx0 = columncount+1
                                topvtx1 = topvtx0+1
                                bottomvtx0 = topvtx1
                                bottomvtx1 = topvtx0
                            else:
                                if (columncount-1)*2 == nbroffaces+1 or (columncount-1)*2 == nbroffaces:
                                    topvtx0 = ((columncount-1)*2)
                                    if not nbroffaces&1: # This test if a number is even.
                                        topvtx1 = topvtx0+1
                                    else: # else it is odd.
                                        topvtx1 = topvtx0-1
                                else:
                                    if not nbroffaces&1: # This test if a number is even.
                                        if columncount < int(nbroffaces*.5)+2:
                                            topvtx0 = (columncount*2)-2
                                            topvtx1 = topvtx0+2
                                        else:
                                            topvtx0 = nbroffaces-((columncount-(int(nbroffaces*.5+.5)+2))*2)+1
                                            topvtx1 = topvtx0-2
                                    else: # else it is odd.
                                        if columncount <= int(nbroffaces*.5)+2:
                                            topvtx0 = (columncount*2)-2
                                            topvtx1 = topvtx0+2
                                        else:
                                            topvtx0 = nbroffaces-((columncount-(int(nbroffaces*.5+.5)+2))*2)
                                            topvtx1 = topvtx0-2
                                bottomvtx0 = topvtx1
                                bottomvtx1 = topvtx0
                        else:
                            topvtx0 = 6+((columncount-2)*2)
                            topvtx1 = topvtx0-2
                            bottomvtx0 = 6+((columncount-2)*2)+1
                            bottomvtx1 = bottomvtx0-2
                        topvtx2 = 1
                        bottomvtx2 = 4
                if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                    topuv0 = cordsview.proj(new_vtxs[topvtx0])
                    topuv1 = cordsview.proj(new_vtxs[topvtx1])
                    topuv2 = cordsview.proj(new_vtxs[topvtx2])
                else:
                    topuv0 = quarkx.vect(new_vtxs[topvtx0].tuple[1], -new_vtxs[topvtx0].tuple[2], 0)/SkinViewScale*10
                    topuv1 = quarkx.vect(new_vtxs[topvtx1].tuple[1], -new_vtxs[topvtx1].tuple[2], 0)/SkinViewScale*10
                    topuv2 = quarkx.vect(new_vtxs[topvtx2].tuple[1], -new_vtxs[topvtx2].tuple[2], 0)/SkinViewScale*10
                toptri = ((extvtx+topvtx0,int(topuv0.tuple[0]),int(topuv0.tuple[1])), (extvtx+topvtx1,int(topuv1.tuple[0]),int(topuv1.tuple[1])), (extvtx+topvtx2,int(topuv2.tuple[0]),int(topuv2.tuple[1])))
                if undomsg.startswith('new pyramid'):
                    newtris = newtris + [toptri]
                  ## This section is for the option to make the end faces or not.
                    if quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"] != "1":
                        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                            topuv0 = cordsview.proj(new_vtxs[topvtx0])
                            topuv1 = cordsview.proj(new_vtxs[topvtx1])
                            topuv2 = cordsview.proj(new_vtxs[topvtx2])
                        else:
                            topuv0 = quarkx.vect(new_vtxs[topvtx0].tuple[1], -new_vtxs[topvtx0].tuple[2], 0)/SkinViewScale*10
                            topuv1 = quarkx.vect(new_vtxs[topvtx1].tuple[1], -new_vtxs[topvtx1].tuple[2], 0)/SkinViewScale*10
                            topuv2 = quarkx.vect(new_vtxs[topvtx2].tuple[1], -new_vtxs[topvtx2].tuple[2], 0)/SkinViewScale*10
                        endtri = ((baseface_index,int(topuv1.tuple[0]),int(topuv1.tuple[1])), (extvtx+topvtx0,int(topuv0.tuple[0]),int(topuv0.tuple[1])), (extvtx+topvtx2,int(topuv2.tuple[0]),int(topuv2.tuple[1])))
                        newtris = newtris + [endtri]
                else:
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        bottomuv0 = cordsview.proj(new_vtxs[bottomvtx0])
                        bottomuv1 = cordsview.proj(new_vtxs[bottomvtx1])
                        bottomuv2 = cordsview.proj(new_vtxs[bottomvtx2])
                    else:
                        bottomuv0 = quarkx.vect(new_vtxs[bottomvtx0].tuple[1], -new_vtxs[bottomvtx0].tuple[2], 0)/SkinViewScale*10
                        bottomuv1 = quarkx.vect(new_vtxs[bottomvtx1].tuple[1], -new_vtxs[bottomvtx1].tuple[2], 0)/SkinViewScale*10
                        bottomuv2 = quarkx.vect(new_vtxs[bottomvtx2].tuple[1], -new_vtxs[bottomvtx2].tuple[2], 0)/SkinViewScale*10
                    bottomtri = ((extvtx+bottomvtx0,int(bottomuv0.tuple[0]),int(bottomuv0.tuple[1])), (extvtx+bottomvtx1,int(bottomuv1.tuple[0]),int(bottomuv1.tuple[1])), (extvtx+bottomvtx2,int(bottomuv2.tuple[0]),int(bottomuv2.tuple[1])))
                    newtris = newtris + [toptri] + [bottomtri]
                columncount = columncount + 1

        # This part makes the side "face" triangles that are needed.
        if ringcount != 0:
            while ringcount < rings+1:
                base = (nbroffaces*2)+2
                # This part does the first "ring".
                if ringcount == 1:
                    if face == 1:
                        if rings == 1:
                            if undomsg.startswith('new dome'):
                                vtx10 = nbroffaces*2
                                vtx11 = 2
                                vtx12 = 3
                                vtx20 = 5
                                vtx21 = 3
                                vtx22 = 2
                            elif undomsg.startswith('new cylinder'):
                                vtx10 = 3
                                vtx11 = 2
                                vtx12 = 1
                                vtx20 = 3
                                vtx21 = 1
                                vtx22 = 0
                            else:
                                vtx10 = 9
                                vtx11 = 5
                                vtx12 = 0
                                vtx20 = 5
                                vtx21 = 2
                                vtx22 = 0
                        else:
                            vtx10 = base+1
                            vtx11 = vtxcount
                            vtx12 = base
                            vtx20 = vtx10
                            vtx21 = 2
                            vtx22 = vtxcount
                    elif face == 2:
                        if rings == 1:
                            if undomsg.startswith('new dome'):
                                vtx10 = 5
                                vtx11 = 2
                                vtx12 = 0
                                vtx20 = (nbroffaces*2)+1
                                vtx21 = 5
                                vtx22 = 0
                            elif undomsg.startswith('new cylinder'):
                                vtx10 = 5
                                vtx11 = 0
                                vtx12 = 1
                                vtx20 = 5
                                vtx21 = 4
                                vtx22 = 0
                            else:
                                vtx10 = 9
                                vtx11 = 0
                                vtx12 = 6
                                vtx20 = 9
                                vtx21 = 6
                                vtx22 = 7
                        else:
                            vtx10 = vtxcount
                            vtx11 = (nbroffaces*2)+2
                            vtx12 = vtxcount-vtxcount
                            vtx20 = vtx11+2
                            vtx21 = vtx11
                            vtx22 = vtx10
                    else:
                        if rings == 1:
                            if undomsg.startswith('new cylinder'):
                                if face == nbroffaces:
                                    vtx10 = (face*2)-1
                                    vtx11 = 2
                                    vtx12 = vtx10-1
                                    vtx20 = vtx12
                                    vtx21 = vtx11
                                    vtx22 = 3
                                else:
                                    vtx10 = (face*2)+1
                                    vtx11 = vtx10-3
                                    vtx12 = vtx10-2
                                    vtx20 = vtx10
                                    vtx21 = vtx10-1
                                    vtx22 = vtx11
                            elif undomsg.startswith('new dome'):
                                if face == 3 and nbroffaces == 4:
                                    vtx10 = 9
                                    vtx11 = 0
                                    vtx12 = 6
                                    vtx20 = 9
                                    vtx21 = 6
                                    vtx22 = 7
                                if face == nbroffaces:
                                    if face == 4:
                                        vtx10 = 8
                                        vtx11 = 7
                                        vtx12 = 6
                                        vtx20 = 8
                                        vtx21 = 3
                                        vtx22 = 7
                                    else:
                                        vtx10 = face*2
                                        vtx11 = 7
                                        vtx12 = vtx10-2
                                        vtx20 = face*2
                                        vtx21 = 3
                                        vtx22 = 7
                                else:
                                    base = (nbroffaces*2)+1
                                    vtx10 = base-((face-3)*2)
                                    vtx12 = face*2
                                    if face == 3:
                                        vtx11 = 0
                                    else:
                                        vtx11 = vtx12-2
                                    vtx20 = vtx10
                                    vtx21 = vtx12
                                    vtx22 = vtx10-2
                            elif face == 3:
                                vtx10 = 8
                                vtx11 = 3
                                vtx12 = 7
                                vtx20 = 8
                                vtx21 = 7
                                vtx22 = 6
                            else:
                                vtx10 = 8
                                vtx11 = 2
                                vtx12 = 3
                                vtx20 = 5
                                vtx21 = 3
                                vtx22 = 2
                        else:
                            if face == nbroffaces:
                                if undomsg.startswith('new dome'):
                                    vtx10 = (nbroffaces*2)+face+1
                                    vtx11 = vtxcount-2
                                    vtx12 = 2
                                    vtx20 = vtx10
                                    vtx21 = vtx12
                                    vtx22 = (nbroffaces*2)+3
                                else:
                                    vtx10 = (nbroffaces*2)+face+1
                                    vtx11 = vtxcount-2
                                    vtx12 = 2
                                    vtx20 = vtx10
                                    vtx21 = vtx12
                                    vtx22 = vtx10-rings-1
                            else:
                                vtx10 = (nbroffaces*2)+face+1
                                vtx11 = vtxcount-2
                                vtx12 = vtxcount
                                vtx20 = vtx10+1
                                vtx21 = vtx10
                                vtx22 = vtx12
                elif ringcount == rings:
                    # This part does the last "ring".
                    if face == 1:
                        vtx10 = base+nbroffaces+((ringcount-3)*nbroffaces)+face
                        vtx11 = vtx10-1
                        vtx12 = 5
                        vtx20 = vtx11
                        vtx21 = 6+((nbroffaces-face-2)*2)+1
                        vtx22 = 5
                    elif face == 2:
                        vtx10 = base+nbroffaces+((ringcount-3)*nbroffaces)+face
                        vtx11 = 6+((nbroffaces-face-2)*2)+3
                        vtx12 = vtx10-2
                        vtx20 = base+nbroffaces+((ringcount-3)*nbroffaces)+face
                        vtx21 = vtx11-2
                        vtx22 = vtx11
                    elif face == nbroffaces:
                        vtx10 = base+nbroffaces+((ringcount-3)*nbroffaces)+face-1
                        vtx11 = vtx10-nbroffaces+2
                        vtx12 = 3
                        vtx20 = vtx11
                        vtx21 = 5
                        vtx22 = 3
                    elif face == nbroffaces-1:
                        vtx10 = base+nbroffaces+((ringcount-3)*nbroffaces)+face
                        vtx11 = 6+((nbroffaces-face-2)*2)+3
                        vtx12 = vtx10-1
                        vtx20 = vtx10
                        vtx21 = 3
                        vtx22 = 7
                    else:
                        vtx10 = base+nbroffaces+((ringcount-3)*nbroffaces)+face
                        vtx11 = 6+((nbroffaces-face-2)*2)+3
                        vtx12 = vtx10-1
                        vtx20 = base+nbroffaces+((ringcount-3)*nbroffaces)+face
                        vtx21 = vtx11-2
                        vtx22 = vtx11
                else:
                    # This part does the rest of the rings.
                    if face == 1:
                        vtx10 = base+nbroffaces+((ringcount-2)*nbroffaces)+face
                        vtx11 = vtx10-nbroffaces
                        vtx12 = vtx11-1
                        vtx20 = vtx10
                        vtx21 = vtx12
                        vtx22 = vtx10-1
                    elif face == 2:
                        vtx10 = base+nbroffaces+((ringcount-2)*nbroffaces)
                        vtx11 = vtx10-nbroffaces
                        vtx12 = vtx11+face
                        vtx20 = vtx10
                        vtx21 = vtx12
                        vtx22 = vtx10+face
                    elif face == nbroffaces:
                        vtx20 = base+nbroffaces+((ringcount-2)*nbroffaces)+face-1
                        vtx21 = vtx20-nbroffaces+2-nbroffaces
                        vtx22 = vtx20-nbroffaces+2
                        vtx10 = vtx20
                        vtx11 = vtx20-nbroffaces
                        vtx12 = vtx21
                    else:
                        vtx20 = base+nbroffaces+((ringcount-2)*nbroffaces)+face
                        vtx21 = vtx20-1
                        vtx22 = vtx20-nbroffaces
                        vtx10 = vtx21
                        vtx11 = vtx21-nbroffaces
                        vtx12 = vtx20-nbroffaces

                if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                    uv10 = cordsview.proj(new_vtxs[vtx10])
                    uv11 = cordsview.proj(new_vtxs[vtx11])
                    uv12 = cordsview.proj(new_vtxs[vtx12])
                    uv20 = cordsview.proj(new_vtxs[vtx20])
                    uv21 = cordsview.proj(new_vtxs[vtx21])
                    uv22 = cordsview.proj(new_vtxs[vtx22])
                else:
                    uv10 = quarkx.vect(new_vtxs[vtx10].tuple[1], -new_vtxs[vtx10].tuple[2], 0)/SkinViewScale*10
                    uv11 = quarkx.vect(new_vtxs[vtx11].tuple[1], -new_vtxs[vtx11].tuple[2], 0)/SkinViewScale*10
                    uv12 = quarkx.vect(new_vtxs[vtx12].tuple[1], -new_vtxs[vtx12].tuple[2], 0)/SkinViewScale*10
                    uv20 = quarkx.vect(new_vtxs[vtx20].tuple[1], -new_vtxs[vtx20].tuple[2], 0)/SkinViewScale*10
                    uv21 = quarkx.vect(new_vtxs[vtx21].tuple[1], -new_vtxs[vtx21].tuple[2], 0)/SkinViewScale*10
                    uv22 = quarkx.vect(new_vtxs[vtx22].tuple[1], -new_vtxs[vtx22].tuple[2], 0)/SkinViewScale*10
                tri1 = ((extvtx+vtx10,int(uv10.tuple[0]),int(uv10.tuple[1])), (extvtx+vtx11,int(uv11.tuple[0]),int(uv11.tuple[1])), (extvtx+vtx12,int(uv12.tuple[0]),int(uv12.tuple[1])))
                tri2 = ((extvtx+vtx20,int(uv20.tuple[0]),int(uv20.tuple[1])), (extvtx+vtx21,int(uv21.tuple[0]),int(uv21.tuple[1])), (extvtx+vtx22,int(uv22.tuple[0]),int(uv22.tuple[1])))
                newtris = newtris + [tri1] + [tri2]

              ## This section is for the option to make the end faces or not.
                if poly.name == "cylinder:p" and quarkx.setupsubset(SS_MODEL, "Options")["QuickObjects_makehollow"] != "1":
                    if face == 1:
                        toptri = ((topface_index,int(uv10.tuple[0]),int(uv10.tuple[1])), (extvtx+vtx12,int(uv12.tuple[0]),int(uv12.tuple[1])), (extvtx+vtx11,int(uv11.tuple[0]),int(uv11.tuple[1])))
                        endtri = ((baseface_index,int(uv21.tuple[0]),int(uv21.tuple[1])), (extvtx+vtx20,int(uv20.tuple[0]),int(uv20.tuple[1])), (extvtx+vtx22,int(uv22.tuple[0]),int(uv22.tuple[1])))
                    elif face == nbroffaces:
                        toptri = ((topface_index,int(uv12.tuple[0]),int(uv12.tuple[1])), (extvtx+vtx11,int(uv11.tuple[0]),int(uv11.tuple[1])), (extvtx+vtx10,int(uv10.tuple[0]),int(uv10.tuple[1])))
                        endtri = ((baseface_index,int(uv21.tuple[0]),int(uv21.tuple[1])), (extvtx+vtx20,int(uv20.tuple[0]),int(uv20.tuple[1])), (extvtx+vtx22,int(uv22.tuple[0]),int(uv22.tuple[1])))
                    elif face == nbroffaces-1 or (face > 9 and face < nbroffaces) or face <= nbroffaces-2: # and rings == 1:
                        toptri = ((topface_index,int(uv11.tuple[0]),int(uv11.tuple[1])), (extvtx+vtx10,int(uv10.tuple[0]),int(uv10.tuple[1])), (extvtx+vtx12,int(uv12.tuple[0]),int(uv12.tuple[1])))
                        endtri = ((baseface_index,int(uv20.tuple[0]),int(uv20.tuple[1])), (extvtx+vtx22,int(uv22.tuple[0]),int(uv22.tuple[1])), (extvtx+vtx21,int(uv21.tuple[0]),int(uv21.tuple[1])))
                    newtris = newtris + [toptri] + [endtri]

                if face == 1 and ringcount == 1:
                    face = face + 1
                    vtxcount = 6
                elif face == nbroffaces:
                    ringcount = ringcount + 1
                    face = 1
                else:
                    face = face + 1
                    vtxcount = vtxcount + 2

        # This last part checks for any other existing currentcomponent objects,
        #    and if so adds the new object's triangles to the existing triangles list
        #    at the end, if not then is just makes the new triangles list.
        if len(comp.triangles) == 0:
            new_comp.triangles = newtris
        else:
            new_comp.triangles = comp.triangles + newtris

        # Finally the undo exchange is made and ok called to finish the function.
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        # This needs to be done for each component or bones will not work if used in the editor.
        quarkpy.mdlutils.make_tristodraw_dict(editor, new_comp)
        if rings == 0:
            editor.ok(undo, undomsg+" with "+str(nbroffaces)+" faces")
        elif rings == 1:
            editor.ok(undo, undomsg+" with "+str(nbroffaces)+" faces \\ "+str(rings)+" ring")
        else:
            editor.ok(undo, undomsg+" with "+str(nbroffaces)+" faces \\ "+str(rings)+" rings")

    # This area does the conversion of group 'Object Maker Polys' for the Editor, such as the Torus.
    if option == 2:
        # This first part does the convertion from poly back to Model Editor usable triangles & vertexes.
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        framevtxs = len(comp.currentframe.vertices)-1
        vtxperface = len(newobjectslist[0].subitems[0].subitems)-2
        # First we get the new vertex point of all of the vertexes for each new poly face.
        new_vtxs = []
        for poly in newobjectslist[0].subitems:
            skippedfaces = 0
            for f in range(len(poly.subitems)):
                face = poly.subitems[f]
                if face.name.startswith('Back') or face.name.startswith('Front'):
                    skippedfaces = skippedfaces + 1
                    continue
                vertex = quarkx.vect(face["v"][0] , face["v"][1], face["v"][2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
                new_vtxs.append(vertex)
            nbroffaces = len(poly.subitems)-skippedfaces
        nbrofpolys = len(newobjectslist[0].subitems)
        if nbrofpolys > nbroffaces:
            addedsections = nbrofpolys - nbroffaces
        else:
            addedsections = 0
        # second we add those new vertex points to each of the currentcomponent's frames.
        for compframe in range(len(compframes)):
            if compframes[compframe] == 0:
                compframes[compframe].vertices = new_vtxs
            else:
                compframes[compframe].vertices = compframes[compframe].vertices + new_vtxs
            compframes[compframe].compparent = new_comp # To allow frame relocation after editing.


        # Third we use that list of new vertexes to make the new triangle faces.
        #    some of which are already triangles for some objects.
        # This part gives some kind of view to set skin positions by
        #    for the Skin-view if it has not been opened yet
        #    and the option to skin from the editors3Dview for an infinite variations of angles.
        from quarkpy.mdlhandles import SkinView1
        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
            for v in editor.layout.views:
                if v.info["viewname"] == "editors3Dview":
                    cordsview = v
        else:
            try:
                tex = comp.currentskin
                texWidth,texHeight = tex["Size"]
                if quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] == "1":
                    SkinViewScale = SkinView1.info["scale"]
                else:
                    SkinViewScale = 1
            except:
                texWidth,texHeight = SkinView1.clientarea
                SkinViewScale = 1

        newtris = []
        polycount = 1
        facecount = -1
        extvtx = len(comp.currentframe.vertices)
        while facecount < len(new_vtxs)-1:
            facecount = facecount + 1
            if facecount == vtxperface * polycount -1:
                facecount = facecount + 1
                polycount = polycount + 1
            if facecount >= len(new_vtxs)-1 - vtxperface:
                lastpolycount = vtxperface + addedsections
                facecount = len(new_vtxs) - vtxperface
                while lastpolycount > 0:
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        uv1 = cordsview.proj(new_vtxs[facecount])
                        uv2 = cordsview.proj(new_vtxs[facecount+1])
                        uv5 = cordsview.proj(new_vtxs[facecount+vtxperface-len(new_vtxs)])
                        uv6 = cordsview.proj(new_vtxs[facecount+vtxperface-len(new_vtxs)+1])
                    else:
                        uv1 = quarkx.vect(new_vtxs[facecount].tuple[1], -new_vtxs[facecount].tuple[2], 0)/SkinViewScale*10
                        uv2 = quarkx.vect(new_vtxs[facecount+1].tuple[1], -new_vtxs[facecount+1].tuple[2], 0)/SkinViewScale*10
                        uv5 = quarkx.vect(new_vtxs[facecount+vtxperface-len(new_vtxs)].tuple[1], -new_vtxs[facecount+vtxperface-len(new_vtxs)].tuple[2], 0)/SkinViewScale*10
                        uv6 = quarkx.vect(new_vtxs[facecount+vtxperface-len(new_vtxs)+1].tuple[1], -new_vtxs[facecount+vtxperface-len(new_vtxs)+1].tuple[2], 0)/SkinViewScale*10
                    tri1 = ((extvtx+facecount,int(uv1.tuple[0]),int(uv1.tuple[1])), (extvtx+facecount+1,int(uv2.tuple[0]),int(uv2.tuple[1])), (extvtx+facecount+vtxperface-len(new_vtxs),int(uv5.tuple[0]),int(uv5.tuple[1])))
                    tri2 = ((extvtx+facecount+vtxperface-len(new_vtxs),int(uv5.tuple[0]),int(uv5.tuple[1])), (extvtx+facecount+1,int(uv2.tuple[0]),int(uv2.tuple[1])), (extvtx+facecount+vtxperface-len(new_vtxs)+1,int(uv6.tuple[0]),int(uv6.tuple[1])))
                    newtris = newtris + [tri1] + [tri2]
                    facecount = facecount + 1
                    lastpolycount = lastpolycount -1
                    if facecount >= len(new_vtxs)-1:
                        break
                lastpolycount = vtxperface + addedsections
                facecount = vtxperface -1
                while lastpolycount > 0:
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        uv1 = cordsview.proj(new_vtxs[facecount])
                        uv7 = cordsview.proj(new_vtxs[facecount+1-vtxperface])
                        uv8 = cordsview.proj(new_vtxs[vtxperface-1])
                        uv9 = cordsview.proj(new_vtxs[facecount-facecount])
                    else:
                        uv1 = quarkx.vect(new_vtxs[facecount].tuple[1], -new_vtxs[facecount].tuple[2], 0)/SkinViewScale*10
                        uv7 = quarkx.vect(new_vtxs[facecount+1-vtxperface].tuple[1], -new_vtxs[facecount+1-vtxperface].tuple[2], 0)/SkinViewScale*10
                        uv8 = quarkx.vect(new_vtxs[vtxperface-1].tuple[1], -new_vtxs[vtxperface-1].tuple[2], 0)/SkinViewScale*10
                        uv9 = quarkx.vect(new_vtxs[facecount-facecount].tuple[1], -new_vtxs[facecount-facecount].tuple[2], 0)/SkinViewScale*10
                    if facecount >= len(new_vtxs)-1:
                        tri1 = ((extvtx+facecount,int(uv1.tuple[0]),int(uv1.tuple[1])), (extvtx+facecount+1-vtxperface,int(uv7.tuple[0]),int(uv7.tuple[1])), (extvtx+vtxperface-1,int(uv8.tuple[0]),int(uv8.tuple[1])))
                        tri2 = ((extvtx+vtxperface-1,int(uv8.tuple[0]),int(uv8.tuple[1])), (extvtx+facecount+1-vtxperface,int(uv7.tuple[0]),int(uv7.tuple[1])), (extvtx+facecount-facecount,int(uv9.tuple[0]),int(uv9.tuple[1])))
                        newtris = newtris + [tri1] + [tri2]
                        break
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        uv2 = cordsview.proj(new_vtxs[facecount+1])
                        uv3 = cordsview.proj(new_vtxs[facecount+vtxperface])
                    else:
                        uv2 = quarkx.vect(new_vtxs[facecount+1].tuple[1], -new_vtxs[facecount+1].tuple[2], 0)/SkinViewScale*10
                        uv3 = quarkx.vect(new_vtxs[facecount+vtxperface].tuple[1], -new_vtxs[facecount+vtxperface].tuple[2], 0)/SkinViewScale*10
                    tri1 = ((extvtx+facecount,int(uv1.tuple[0]),int(uv1.tuple[1])), (extvtx+facecount+1-vtxperface,int(uv7.tuple[0]),int(uv7.tuple[1])), (extvtx+facecount+vtxperface,int(uv3.tuple[0]),int(uv3.tuple[1])))
                    tri2 = ((extvtx+facecount+vtxperface,int(uv3.tuple[0]),int(uv3.tuple[1])), (extvtx+facecount+1-vtxperface,int(uv7.tuple[0]),int(uv7.tuple[1])), (extvtx+facecount+1,int(uv2.tuple[0]),int(uv2.tuple[1])))
                    newtris = newtris + [tri1] + [tri2]
                    facecount = facecount + vtxperface
                    lastpolycount = lastpolycount -1
                break
            else:
                if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                    uv1 = cordsview.proj(new_vtxs[facecount])
                    uv2 = cordsview.proj(new_vtxs[facecount+1])
                    uv3 = cordsview.proj(new_vtxs[facecount+vtxperface])
                    uv4 = cordsview.proj(new_vtxs[facecount+vtxperface+1])
                else:
                    uv1 = quarkx.vect(new_vtxs[facecount].tuple[1], -new_vtxs[facecount].tuple[2], 0)/SkinViewScale*10
                    uv2 = quarkx.vect(new_vtxs[facecount+1].tuple[1], -new_vtxs[facecount+1].tuple[2], 0)/SkinViewScale*10
                    uv3 = quarkx.vect(new_vtxs[facecount+vtxperface].tuple[1], -new_vtxs[facecount+vtxperface].tuple[2], 0)/SkinViewScale*10
                    uv4 = quarkx.vect(new_vtxs[facecount+vtxperface+1].tuple[1], -new_vtxs[facecount+vtxperface+1].tuple[2], 0)/SkinViewScale*10
                tri1 = ((extvtx+facecount,int(uv1.tuple[0]),int(uv1.tuple[1])), (extvtx+facecount+1,int(uv2.tuple[0]),int(uv2.tuple[1])), (extvtx+facecount+vtxperface,int(uv3.tuple[0]),int(uv3.tuple[1])))
                tri2 = ((extvtx+facecount+vtxperface,int(uv3.tuple[0]),int(uv3.tuple[1])), (extvtx+facecount+1,int(uv2.tuple[0]),int(uv2.tuple[1])), (extvtx+facecount+vtxperface+1,int(uv4.tuple[0]),int(uv4.tuple[1])))
                newtris = newtris + [tri1] + [tri2]

        if len(comp.triangles) == 0:
            new_comp.triangles = newtris
        else:
            new_comp.triangles = comp.triangles + newtris
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        # This needs to be done for each component or bones will not work if used in the editor.
        quarkpy.mdlutils.make_tristodraw_dict(editor, new_comp)
        editor.ok(undo, undomsg+" with "+str(nbroffaces)+" faces \\ "+str(nbrofpolys)+" sections")


    # This area does the conversion of the 'Fan Object Maker' only for the Editor.
    if option == 3:
        # This first part does the convertion from poly back to Model Editor usable triangles & vertexes.
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames

        # First we go through all of the vertexes of the new poly object
        #    and create vertexes that the Model Editor knows how to use.
        new_vtxs = []
        poly = newobjectslist[0]
        for vtx in range(len(poly.vertices)):
            v = poly.vertices[vtx]
            vertex = quarkx.vect(v.tuple[0], v.tuple[1], v.tuple[2])
            new_vtxs.append(vertex)

        # Second we add those new vertex points to each of the
        #     currentcomponent's frames current vertexes, if there are any.
        for compframe in range(len(compframes)):
            if compframes[compframe] == 0:
                compframes[compframe].vertices = new_vtxs
            else:
                compframes[compframe].vertices = compframes[compframe].vertices + new_vtxs
            compframes[compframe].compparent = new_comp # To allow frame relocation after editing.


        # This part gives some kind of view to set skin positions by
        #    for the Skin-view if it has not been opened yet
        #    and the option to skin from the editors3Dview for an infinite variation of angles.
        from quarkpy.mdlhandles import SkinView1
        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
            for v in editor.layout.views:
                if v.info["viewname"] == "editors3Dview":
                    cordsview = v
        else:
            try:
                tex = comp.currentskin
                texWidth,texHeight = tex["Size"]
                if quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] == "1":
                    SkinViewScale = SkinView1.info["scale"]
                else:
                    SkinViewScale = 1
            except:
                texWidth,texHeight = SkinView1.clientarea
                SkinViewScale = 1

        # This part compairs each of the poly's faces vertexes to find them in the
        #    new_vtxs to setup up their vert_index for making the new triangles.
        # It has two sections, the first to handle triangles, the second to handle faces.
        # The second section has two parts, 1st part handles faces with only 4 vertexes,
        #    the 2nd part handles odd shape faces with more then 4 vertexes.
        newtris = []
        rings = nbroffaces - 3
        extvtx = len(comp.currentframe.vertices)
        for face in poly.subitems:
            # This first section handles the triangles of the poly.
            if len(face.verticesof(poly)) == 3:
                count = 0
                for vtx in range(len(face.verticesof(poly))):
                    for vertex in range(len(new_vtxs)):
                        if str(face.verticesof(poly)[vtx].tuple[0]) == str(new_vtxs[vertex].tuple[0]) and str(face.verticesof(poly)[vtx].tuple[1]) == str(new_vtxs[vertex].tuple[1]) and str(face.verticesof(poly)[vtx].tuple[2]) == str(new_vtxs[vertex].tuple[2]):
                            if count == 0:
                                tri0 = vertex
                                count = count +1
                            elif count == 1:
                                tri1 = vertex
                                count = count +1
                            else:
                                tri2 = vertex
                                count = 0
                                break
                if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                    uv0u = int(cordsview.proj(new_vtxs[tri0]).tuple[0])
                    uv0v = int(cordsview.proj(new_vtxs[tri0]).tuple[1])
                    uv1u = int(cordsview.proj(new_vtxs[tri1]).tuple[0])
                    uv1v = int(cordsview.proj(new_vtxs[tri1]).tuple[1])
                    uv2u = int(cordsview.proj(new_vtxs[tri2]).tuple[0])
                    uv2v = int(cordsview.proj(new_vtxs[tri2]).tuple[1])
                else:
                    uv0u = new_vtxs[tri0].tuple[1]/SkinViewScale*10
                    uv0v = -new_vtxs[tri0].tuple[2]/SkinViewScale*10
                    uv1u = new_vtxs[tri1].tuple[1]/SkinViewScale*10
                    uv1v = -new_vtxs[tri1].tuple[2]/SkinViewScale*10
                    uv2u = new_vtxs[tri2].tuple[1]/SkinViewScale*10
                    uv2v = -new_vtxs[tri2].tuple[2]/SkinViewScale*10
                tris = ((extvtx+tri0,uv0u,uv0v), (extvtx+tri1,uv1u,uv1v), (extvtx+tri2,uv2u,uv2v))
                newtris = newtris + [tris]

            # This first section handles the non-triangle faces of the poly,
            #    breaking them down into triangles that the Model Editor can use.
                # This part handles regular faces with only 4 vertexes.
            elif len(face.verticesof(poly)) == 4:
                count = 0
                for vtx in range(len(face.verticesof(poly))):
                    for vertex in range(len(new_vtxs)):
                        if str(face.verticesof(poly)[vtx].tuple[0]) == str(new_vtxs[vertex].tuple[0]) and str(face.verticesof(poly)[vtx].tuple[1]) == str(new_vtxs[vertex].tuple[1]) and str(face.verticesof(poly)[vtx].tuple[2]) == str(new_vtxs[vertex].tuple[2]):
                            if count == 0:
                                tri0 = vertex
                                count = count +1
                            elif count == 1:
                                tri1 = vertex
                                count = count +1
                            elif count == 2:
                                tri2 = vertex
                                count = count +1
                            else:
                                tri3 = vertex
                                count = 0
                                break
                if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                    uv0u = int(cordsview.proj(new_vtxs[tri0]).tuple[0])
                    uv0v = int(cordsview.proj(new_vtxs[tri0]).tuple[1])
                    uv1u = int(cordsview.proj(new_vtxs[tri1]).tuple[0])
                    uv1v = int(cordsview.proj(new_vtxs[tri1]).tuple[1])
                    uv2u = int(cordsview.proj(new_vtxs[tri2]).tuple[0])
                    uv2v = int(cordsview.proj(new_vtxs[tri2]).tuple[1])
                    uv3u = int(cordsview.proj(new_vtxs[tri3]).tuple[0])
                    uv3v = int(cordsview.proj(new_vtxs[tri3]).tuple[1])
                else:
                    uv0u = new_vtxs[tri0].tuple[1]/SkinViewScale*10
                    uv0v = -new_vtxs[tri0].tuple[2]/SkinViewScale*10
                    uv1u = new_vtxs[tri1].tuple[1]/SkinViewScale*10
                    uv1v = -new_vtxs[tri1].tuple[2]/SkinViewScale*10
                    uv2u = new_vtxs[tri2].tuple[1]/SkinViewScale*10
                    uv2v = -new_vtxs[tri2].tuple[2]/SkinViewScale*10
                    uv3u = new_vtxs[tri3].tuple[1]/SkinViewScale*10
                    uv3v = -new_vtxs[tri3].tuple[2]/SkinViewScale*10
                tris1 = ((extvtx+tri0,uv0u,uv0v), (extvtx+tri1,uv1u,uv1v), (extvtx+tri2,uv2u,uv2v))
                tris2 = ((extvtx+tri3,uv3u,uv3v), (extvtx+tri0,uv0u,uv0v), (extvtx+tri2,uv2u,uv2v))
                newtris = newtris + [tris1] + [tris2]
                # This part handles odd shape faces with more then 4 vertexes.
            elif len(face.verticesof(poly)) > 4:
                for vertex in range(len(new_vtxs)):
                    if str(face.verticesof(poly)[0].tuple[0]) == str(new_vtxs[vertex].tuple[0]) and str(face.verticesof(poly)[0].tuple[1]) == str(new_vtxs[vertex].tuple[1]) and str(face.verticesof(poly)[0].tuple[2]) == str(new_vtxs[vertex].tuple[2]):
                        tri0 = basevtx = vertex
                        prevvtx = None
                        count = 1
                        break
                for vtx in range(len(face.verticesof(poly))):
                    if vtx == 0:
                        continue
                    else:
                        for vertex in range(len(new_vtxs)):
                            if str(face.verticesof(poly)[vtx].tuple[0]) == str(new_vtxs[vertex].tuple[0]) and str(face.verticesof(poly)[vtx].tuple[1]) == str(new_vtxs[vertex].tuple[1]) and str(face.verticesof(poly)[vtx].tuple[2]) == str(new_vtxs[vertex].tuple[2]):
                                if count == 1:
                                    if prevvtx is None:
                                        tri1 = vertex
                                        count = count +1
                                        break
                                if count == 3:
                                    tri1 = prevvtx
                                    tri2 = vertex
                                if count == 2:
                                    tri2 = vertex
                                    count = count +1
                                if count >= 2:
                                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                                        uv0u = int(cordsview.proj(new_vtxs[tri0]).tuple[0])
                                        uv0v = int(cordsview.proj(new_vtxs[tri0]).tuple[1])
                                        uv1u = int(cordsview.proj(new_vtxs[tri1]).tuple[0])
                                        uv1v = int(cordsview.proj(new_vtxs[tri1]).tuple[1])
                                        uv2u = int(cordsview.proj(new_vtxs[tri2]).tuple[0])
                                        uv2v = int(cordsview.proj(new_vtxs[tri2]).tuple[1])
                                    else:
                                        uv0u = new_vtxs[tri0].tuple[1]/SkinViewScale*10
                                        uv0v = -new_vtxs[tri0].tuple[2]/SkinViewScale*10
                                        uv1u = new_vtxs[tri1].tuple[1]/SkinViewScale*10
                                        uv1v = -new_vtxs[tri1].tuple[2]/SkinViewScale*10
                                        uv2u = new_vtxs[tri2].tuple[1]/SkinViewScale*10
                                        uv2v = -new_vtxs[tri2].tuple[2]/SkinViewScale*10
                                    tris1 = ((extvtx+tri0,uv0u,uv0v), (extvtx+tri1,uv1u,uv1v), (extvtx+tri2,uv2u,uv2v))
                                    newtris = newtris + [tris1]
                                    prevvtx = tri2
                                    break


        # This last part checks for any other existing currentcomponent objects,
        #    and if so adds the new object's triangles to the existing triangles list
        #    at the end, if not then is just makes the new triangles list.
        if len(comp.triangles) == 0:
            new_comp.triangles = newtris
        else:
            new_comp.triangles = comp.triangles + newtris

        # Finally the undo exchange is made and ok called to finish the function.
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        # This needs to be done for each component or bones will not work if used in the editor.
        quarkpy.mdlutils.make_tristodraw_dict(editor, new_comp)
        if rings == 0:
            editor.ok(undo, undomsg+" with "+str(nbroffaces)+" faces")
        elif rings == 1:
            editor.ok(undo, undomsg+" with "+str(nbroffaces)+" faces \\ "+str(rings)+" ring")
        else:
            editor.ok(undo, undomsg+" with "+str(nbroffaces)+" faces \\ "+str(rings)+" rings")


# ----------- REVISION HISTORY ------------
#
# $Log: mdlobjectmodes.py,v $
# Revision 1.21  2011/11/17 01:19:02  cdunde
# Setup BBox drag toolbar button to work correctly with other toolbar buttons.
#
# Revision 1.20  2011/03/04 06:50:28  cdunde
# Added new face cutting tool, for selected faces, like in the map editor with option to allow vertex separation.
#
# Revision 1.19  2009/10/12 20:49:56  cdunde
# Added support for .md3 animationCFG (configuration) support and editing.
#
# Revision 1.18  2009/04/28 21:30:56  cdunde
# Model Editor Bone Rebuild merge to HEAD.
# Complete change of bone system.
#
# Revision 1.17  2008/12/20 08:39:34  cdunde
# Minor adjustment to various Model Editor dialogs for recent fix of item over lapping by Dan.
#
# Revision 1.16  2008/09/12 19:08:40  cdunde
# Minor code cleanup.
#
# Revision 1.15  2008/05/01 14:03:31  danielpharos
# Use local variable instead of redundant look-up.
#
# Revision 1.14  2008/02/23 04:41:11  cdunde
# Setup new Paint modes toolbar and complete painting functions to allow
# the painting of skin textures in any Model Editor textured and Skin-view.
#
# Revision 1.13  2008/02/22 09:52:22  danielpharos
# Move all finishdrawing code to the correct editor, and some small cleanups.
#
# Revision 1.12  2008/02/04 05:07:41  cdunde
# Made toolbars interactive with one another to
# turn off buttons when needed, avoiding errors and crashes.
#
# Revision 1.11  2008/02/03 17:51:22  cdunde
# To remove test print statement.
#
# Revision 1.10  2007/12/02 06:47:12  cdunde
# Setup linear center handle selected vertexes edge extrusion function.
#
# Revision 1.9  2007/11/19 01:08:45  cdunde
# To fix needed face definition and use the fastest way to get it.
#
# Revision 1.8  2007/11/18 02:40:31  cdunde
# Added "Make hollow" option to dialog & end faces for Pyramid and Cylinder Quick Object Makers
# to allow extrusion and vertex manipulation to create shapes such as arms and leg parts.
#
# Revision 1.7  2007/11/16 20:08:45  cdunde
# To update all needed files for fix by DanielPharos
# to allow frame relocation after editing.
#
# Revision 1.6  2007/10/31 03:47:52  cdunde
# Infobase button link updates.
#
# Revision 1.5  2007/10/09 04:15:40  cdunde
# Changed some of the "Fan" Quick Object Maker code
# to provide integers where needed and stop crashing.
#
# Revision 1.4  2007/10/08 18:47:31  cdunde
# To stop both editor's Quick Object Makers from braking when zoomed in close.
#
# Revision 1.3  2007/10/08 16:20:20  cdunde
# To improve Model Editor rulers and Quick Object Makers working with other functions.
#
# Revision 1.2  2007/10/06 20:15:00  cdunde
# Added Ruler Guides to Options menu for Model Editor.
#
# Revision 1.1  2007/10/05 20:47:51  cdunde
# Creation and setup of the Quick Object Makers for the Model Editor.
#
#

