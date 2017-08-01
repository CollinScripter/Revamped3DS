"""   QuArK  -  Quake Army Knife

Plug-in to show distance of selected polys in 2D views.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/maptools.py,v 1.14 2007/09/16 00:38:46 cdunde Exp $


Info = {
   "plug-in":       "Map tools",
   "desc":          "Shows distance of selected polys in 2D views",
   "date":          "November 15 2005",
   "author":        "cdunde",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6.5" }


import quarkpy.mapoptions
from quarkpy.maputils import *

#py2.4 indicates upgrade change for python 2.4

#
# This part is a magical incantation.
# First the normal arguments for
#  finishdrawing, then the oldfinish=... stuff,
#  which has the effect of storing the current
#  finishdrawing method inside this function as
#  the value of the oldfinish variable.
# These def statements are executed as the plugins are being
#  loaded, but not reexecuted in later operations
#  of the map editor, only the functions they define are.
#

def gridfinishdrawing(editor, view, gridoldfinish=quarkpy.mapeditor.MapEditor.finishdrawing):

    #
    # execute the old method
    #

    gridoldfinish(editor, view)

    def MyMakeScroller(layout, view):
        sbviews = [None, None]
        for ifrom, linkfrom, ito, linkto in layout.sblinks:
            if linkto is view:
                sbviews[ito] = (ifrom, linkfrom)
        def scroller(x, y, view=view, hlink=sbviews[0], vlink=sbviews[1]):
            view.scrollto(x, y)
            if hlink is not None:
                if hlink[0]:
                    hlink[1].scrollto(None, x)
                else:
                    hlink[1].scrollto(x, None)
            if vlink is not None:
                if vlink[0]:
                    vlink[1].scrollto(None, y)
                else:
                    vlink[1].scrollto(y, None)
            if not MapOption("AxisXYZ") and not MapOption("All2DviewsScale") and not MapOption("AllScalesCentered") and not MapOption("XviewScale") and not MapOption("XyScaleCentered") and not MapOption("XzScaleCentered") and not MapOption("YviewScale") and not MapOption("YxScaleCentered") and not MapOption("YzScaleCentered") and not MapOption("ZviewScale") and not MapOption("ZxScaleCentered") and not MapOption("ZyScaleCentered") and not MapOption("All2DviewsRulers") and not MapOption("AllTopRulers") and not MapOption("AllSideRulers") and not MapOption("XviewRulers") and not MapOption("XyTopRuler") and not MapOption("XzSideRuler") and not MapOption("YviewRulers") and not MapOption("YxTopRuler") and not MapOption("YzSideRuler") and not MapOption("ZviewRulers") and not MapOption("ZxTopRuler") and not MapOption("ZySideRuler"):
                view.update()
            else:
                view.repaint()
        return scroller
    quarkpy.qhandles.MakeScroller = MyMakeScroller

# The selection bases for setting up the rulers
    rulerlist = editor.layout.explorer.sellist
    if len(rulerlist) == 1 and rulerlist[0].type==":f":
        rulerlist = rulerlist[0].faceof
    elif len(rulerlist) > 1:
        newlist = []
        for item in rulerlist:
            if item.type==":e":
                continue
            else:
                newlist.append(item)
        rulerlist = newlist
    else:
        if len(rulerlist) == 1:
            rulerlist = editor.layout.explorer.sellist
            if len(rulerlist) == 1 and rulerlist[0].type==":e": return

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
           x = int(view.proj(yrendt).tuple[0])-4    #py2.4
           y = int(view.proj(yrendt).tuple[1])-12   #py2.4
           cv.textout(x,y,"0")
        # Prints above the right marker line the distance, on the Y axis
           x = int(view.proj(ylendt).tuple[0])      #py2.4
           y = int(view.proj(ylendt).tuple[1])-12   #py2.4
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
           x = int(view.proj(yrendb).tuple[0])+8   #py2.4
           y = int(view.proj(yrendb).tuple[1])-2   #py2.4
           cv.textout(x,y,"0")
        # Prints right of top marker line the distance, on the Z axis
           x = int(view.proj(yrendt).tuple[0])+8   #py2.4
           y = int(view.proj(yrendt).tuple[1])-2   #py2.4
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
           x = int(view.proj(xlendt).tuple[0])-4    #py2.4
           y = int(view.proj(xlendt).tuple[1])-12   #py2.4
           cv.textout(x,y,"0")
        # Prints above the right marker line the distance, on the X axis
           x = int(view.proj(xrendt).tuple[0])      #py2.4
           y = int(view.proj(xrendt).tuple[1])-12   #py2.4
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
           x = int(view.proj(yrendb).tuple[0])+8   #py2.4
           y = int(view.proj(yrendb).tuple[1])-2   #py2.4
           cv.textout(x,y,"0")
        # Prints right of top marker line the distance, on the Y axis
           x = int(view.proj(yrendt).tuple[0])+8   #py2.4
           y = int(view.proj(yrendt).tuple[1])-2   #py2.4
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
           x = int(view.proj(xlendt).tuple[0])-4    #py2.4
           y = int(view.proj(xlendt).tuple[1])-12   #py2.4
           cv.textout(x,y,"0")
        # Prints above the right marker line the distance, on the X axis
           x = int(view.proj(xrendt).tuple[0])      #py2.4
           y = int(view.proj(xrendt).tuple[1])-12   #py2.4
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
           x = int(view.proj(yrendb).tuple[0])+8   #py2.4
           y = int(view.proj(yrendb).tuple[1])-2   #py2.4
           cv.textout(x,y,"0")
        # Prints right of top marker line the distance, on the Y axis
           x = int(view.proj(yrendt).tuple[0])+8   #py2.4
           y = int(view.proj(yrendt).tuple[1])-2   #py2.4
           higth = abs(y2-y1)
           cv.textout(x,y,quarkx.ftos(higth))

    else:
       return

#
# Now set our new function as the finishdrawing method.
#

quarkpy.mapeditor.MapEditor.finishdrawing = gridfinishdrawing


# ********* This creates the Options menu 2D grid items ***************


def All2DviewsRulersClick(m):
    editor = mapeditor()
    if not MapOption("All2DviewsRulers"):
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XzSideRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YzSideRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
    editor.invalidateviews()

def All2DviewsTopRulers(m):
    editor = mapeditor()
    if not MapOption("AllTopRulers"):
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XzSideRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YzSideRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
    editor.invalidateviews()

def All2DviewsSideRulers(m):
    editor = mapeditor()
    if not MapOption("AllSideRulers"):
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XzSideRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YzSideRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
    editor.invalidateviews()

def XviewRulerClick(m):
    editor = mapeditor()
    if not MapOption("XviewRulers"):
        quarkx.setupsubset(SS_MAP, "Options")['XviewRulers'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['XviewRulers'] = None
    editor.invalidateviews()

def XviewYtopRuler(m):
    editor = mapeditor()
    if not MapOption("XyTopRuler"):
        quarkx.setupsubset(SS_MAP, "Options")['XyTopRuler'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['XyTopRuler'] = None
    editor.invalidateviews()

def XviewZsideRuler(m):
    editor = mapeditor()
    if not MapOption("XzSideRuler"):
        quarkx.setupsubset(SS_MAP, "Options")['XzSideRuler'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['XyTopRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['XzSideRuler'] = None
    editor.invalidateviews()

def YviewRulerClick(m):
    editor = mapeditor()
    if not MapOption("YviewRulers"):
        quarkx.setupsubset(SS_MAP, "Options")['YviewRulers'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['YviewRulers'] = None
    editor.invalidateviews()

def YviewXtopRuler(m):
    editor = mapeditor()
    if not MapOption("YxTopRuler"):
        quarkx.setupsubset(SS_MAP, "Options")['YxTopRuler'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['YxTopRuler'] = None
    editor.invalidateviews()

def YviewZsideRuler(m):
    editor = mapeditor()
    if not MapOption("YzSideRuler"):
        quarkx.setupsubset(SS_MAP, "Options")['YzSideRuler'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['YxTopRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['YzSideRuler'] = None
    editor.invalidateviews()

def ZviewRulerClick(m):
    editor = mapeditor()
    if not MapOption("ZviewRulers"):
        quarkx.setupsubset(SS_MAP, "Options")['ZviewRulers'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['ZviewRulers'] = None
    editor.invalidateviews()

def ZviewXtopRuler(m):
    editor = mapeditor()
    if not MapOption("ZxTopRuler"):
        quarkx.setupsubset(SS_MAP, "Options")['ZxTopRuler'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['ZxTopRuler'] = None
    editor.invalidateviews()

def ZviewYsideRuler(m):
    editor = mapeditor()
    if not MapOption("ZySideRuler"):
        quarkx.setupsubset(SS_MAP, "Options")['ZySideRuler'] = "1"
        quarkx.setupsubset(SS_MAP, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MAP, "Options")['ZxTopRuler'] = None
    else:
        quarkx.setupsubset(SS_MAP, "Options")['ZySideRuler'] = None
    editor.invalidateviews()


def View2DrulerMenu(editor):

    X0 = quarkpy.qmenu.item("All 2D views rulers", All2DviewsRulersClick, "|All 2D views rulers:\n\nIf this menu item is checked, it will display the distance across the 'top' and 'side' of the current selected poly(s) in all 2D views and deactivate this menu's individual items.|intro.mapeditor.menu.html#optionsmenu")

    X1 = quarkpy.qmenu.item("   all top rulers", All2DviewsTopRulers, "|all top rulers:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected poly(s) in all 2D views and deactivate this menu's individual items.|intro.mapeditor.menu.html#optionsmenu")

    X2 = quarkpy.qmenu.item("   all side rulers", All2DviewsSideRulers, "|all side rulers:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected poly(s) in all 2D views and deactivate this menu's individual items.|intro.mapeditor.menu.html#optionsmenu")

    X3 = quarkpy.qmenu.item("X-Back 2D view", XviewRulerClick, "|X-Back 2D view:\n\nIf this menu item is checked, it will display a scale of the current grid setting in the ' X - Back ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X4 = quarkpy.qmenu.item("   y (top) ruler", XviewYtopRuler, "|X view, y (top) ruler:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected poly(s) in the ' X - Face ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X5 = quarkpy.qmenu.item("   z (side) ruler", XviewZsideRuler, "|X view, z (side) ruler:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected poly(s) in the ' X - Face ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X6 = quarkpy.qmenu.item("Y-Side 2D view", YviewRulerClick, "|Y-Side 2D view:\n\nIf this menu item is checked, it will display a scale of the current grid setting in the ' Y-Side ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X7 = quarkpy.qmenu.item("   x (top) ruler", YviewXtopRuler, "|Y view, x (top) ruler:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected poly(s) in the ' Y-Side ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X8 = quarkpy.qmenu.item("   z (side) ruler", YviewZsideRuler, "|Y view, z (side) ruler:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected poly(s) in the ' Y-Side ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X9 = quarkpy.qmenu.item("Z-Top 2D view", ZviewRulerClick, "|Z-Top 2D view:\n\nIf this menu item is checked, it will display a scale of the current grid setting in the ' Z-Top ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X10 = quarkpy.qmenu.item("   x (top) ruler", ZviewXtopRuler, "|Z view, x (top) ruler:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected poly(s) in the ' Z-Top ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X11 = quarkpy.qmenu.item("   y (side) ruler", ZviewYsideRuler, "|Z view, y (side) ruler:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected poly(s) in the ' Z-Top ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    menulist = [X0, X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, X11]

    items = menulist
    X0.state = quarkx.setupsubset(SS_MAP,"Options").getint("All2DviewsRulers")
    X1.state = quarkx.setupsubset(SS_MAP,"Options").getint("AllTopRulers")
    X2.state = quarkx.setupsubset(SS_MAP,"Options").getint("AllSideRulers")
    X3.state = quarkx.setupsubset(SS_MAP,"Options").getint("XviewRulers")
    X4.state = quarkx.setupsubset(SS_MAP,"Options").getint("XyTopRuler")
    X5.state = quarkx.setupsubset(SS_MAP,"Options").getint("XzSideRuler")
    X6.state = quarkx.setupsubset(SS_MAP,"Options").getint("YviewRulers")
    X7.state = quarkx.setupsubset(SS_MAP,"Options").getint("YxTopRuler")
    X8.state = quarkx.setupsubset(SS_MAP,"Options").getint("YzSideRuler")
    X9.state = quarkx.setupsubset(SS_MAP,"Options").getint("ZviewRulers")
    X10.state = quarkx.setupsubset(SS_MAP,"Options").getint("ZxTopRuler")
    X11.state = quarkx.setupsubset(SS_MAP,"Options").getint("ZySideRuler")

    return menulist

shortcuts = {}


# ************************************************************
# ******************Creates the Popup menu********************

def ViewAmendMenu2click(m):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    m.items = View2DrulerMenu(editor)


RulerMenuCmds = [quarkpy.qmenu.popup("Ruler guide in 2D views", [], ViewAmendMenu2click, "|Ruler guide in 2D views:\n\nThese functions allow you to display a line with the unit distance of total selected items in any one, combination, or all of the 2D views of the Editor.", "intro.mapeditor.menu.html#optionsmenu")]
    

# ----------- REVISION HISTORY ------------
#$Log: maptools.py,v $
#Revision 1.14  2007/09/16 00:38:46  cdunde
#Fixed both editors from not drawing gridscale and ruler when grid is inactive.
#
#Revision 1.13  2006/11/30 01:17:48  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.12  2006/11/29 06:58:35  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.11.2.2  2006/11/09 23:00:02  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.11.2.1  2006/11/04 21:36:52  cdunde
#To stop Depreciation message in console when dialog boxes where opened.
#
#Revision 1.11  2006/01/31 11:04:30  cdunde
#Fixed  distance displayed amount from drifting away from
#marker on screen view x-axis when the scale size is changed.
#
#Revision 1.10  2006/01/31 07:35:08  cdunde
#To stop smearing of 2D view when rulers are turned off.
#
#Revision 1.9  2005/12/11 22:03:09  cdunde
#To fix error in editor and Infobase for X 2D view of
#Y axis sign and label which was backwards
#
#Revision 1.8  2005/11/25 04:17:24  cdunde
#again 8-(
#
#Revision 1.6  2005/11/25 03:35:29  cdunde
#Still trying to get this file to pickup its version changes
#
#Revision 1.5  2005/11/24 18:01:46  cdunde
#To eliminate entities from being included in measurements.
#
#Revision 1.4  2005/11/24 17:53:08  cdunde
#To straighten out cvs logging problem
#
#Revision 1.3  2005/11/22 18:25:10  cdunde
#To eliminate entities from being included in measurements.
#
#Revision 1.2  2005/11/18 02:37:30  cdunde
#To try and add header and history log
#
#Revision 1.1  2005/11/18 02:21:53  cdunde
#To add new '2D Rulers' function, menu and
#updated Infobase docs covering it.
#
#