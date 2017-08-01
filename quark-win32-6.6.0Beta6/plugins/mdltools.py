"""   QuArK  -  Quake Army Knife

Plug-in to show distance of selected faces in 2D views.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mdltools.py,v 1.19 2010/05/05 15:46:39 cdunde Exp $


Info = {
   "plug-in":       "Model tools",
   "desc":          "Shows distance of selected faces in 2D views",
   "date":          "October 6 2007",
   "author":        "cdunde",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.5" }


import quarkpy.mdloptions
from quarkpy.mdlutils import *

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
#  of the model editor, only the functions they define are.
#

def gridfinishdrawing(editor, view, gridoldfinish=quarkpy.mdleditor.ModelEditor.finishdrawing):

    #
    # execute the old method
    #

    gridoldfinish(editor, view)

    # Stops jerky movement during panning in 2D views.
    from quarkpy.qbaseeditor import flagsmouse
    if (flagsmouse == 528 or flagsmouse == 1040):
        view.handles = []

# The selection bases for setting up the rulers.
    rulerlist = editor.layout.explorer.sellist
    bmin = None
    if len(rulerlist) == 1 and rulerlist[0].type==":mc":
        # Shows the entire model component size when the
        # main component folder is selected in the tree-view
        # and clears the rulers if another item of another component
        # is selected in the tree-view.
        try:
            org = rulerlist[0].originst
        except:
            return
        else:
            rulerlist = editor.layout.explorer.sellist
    else:
        # Shows the model component selected triangle(s) size
        # when one or more frames are selected in the tree-view.
        rulerlist = editor.EditorObjectList
        try:
            if rulerlist[0].name.endswith(":f"):
                pass
        except:
            if rulerlist != []:
                return
        if rulerlist != [] and rulerlist[0].name.endswith(":f"):
            Xmax = Xmin = rulerlist[0]['v'][0]
            Ymax = Ymin = rulerlist[0]['v'][1]
            Zmax = Zmin = rulerlist[0]['v'][2]
            for facenbr in range(len(rulerlist)):
                vtxcount = 0
                if facenbr == len(rulerlist):
                    break
                vtxlist = rulerlist[facenbr]['v']
                while vtxcount < 9:
                    if (vtxcount == 0) or (vtxcount == 3) or (vtxcount == 6):
                        if vtxlist[vtxcount] > Xmax:
                            Xmax = vtxlist[vtxcount]
                        if vtxlist[vtxcount] < Xmin:
                            Xmin = vtxlist[vtxcount]
                        vtxcount = vtxcount + 1
                    if (vtxcount == 1) or (vtxcount == 4) or (vtxcount == 7):
                        if vtxlist[vtxcount] > Ymax:
                            Ymax = vtxlist[vtxcount]
                        if vtxlist[vtxcount] < Ymin:
                            Ymin = vtxlist[vtxcount]
                        vtxcount = vtxcount + 1
                    if (vtxcount == 2) or (vtxcount == 5) or (vtxcount == 8):
                        if vtxlist[vtxcount] > Zmax:
                            Zmax = vtxlist[vtxcount]
                        if vtxlist[vtxcount] < Zmin:
                            Zmin = vtxlist[vtxcount]
                        vtxcount = vtxcount + 1
            bmax = quarkx.vect(Xmax,Ymax,Zmax)
            bmin = quarkx.vect(Xmin,Ymin,Zmin)
        # Shows the size of any Quick Object Maker item
        # while it is being dragged to create it in any 2D view.
        elif len(rulerlist) > 1:
            newlist = []
            for item in rulerlist:
                newlist.append(item)
            rulerlist = newlist

    if quarkx.boundingboxof(rulerlist) is not None and bmin is None:
        bbox = quarkx.boundingboxof(rulerlist)
        bmin, bmax = bbox
    else:
        if bmin is None:
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
    cv.fontsize = 9
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

       if not MdlOption("All2DviewsRulers") and not MdlOption("AllTopRulers") and not MdlOption("AllSideRulers") and not MdlOption("XviewRulers") and not MdlOption("XyTopRuler") and not MdlOption("XzSideRuler"):
           return

       quarkpy.mdleditor.setsingleframefillcolor(editor, view)
       if not MdlOption("AllSideRulers") and not MdlOption("XzSideRuler"):
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


       if not MdlOption("AllTopRulers") and not MdlOption("XyTopRuler"):
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

       if not MdlOption("All2DviewsRulers") and not MdlOption("AllTopRulers") and not MdlOption("AllSideRulers") and not MdlOption("YviewRulers") and not MdlOption("YxTopRuler") and not MdlOption("YzSideRuler"):
           return

       quarkpy.mdleditor.setsingleframefillcolor(editor, view)
       if not MdlOption("AllSideRulers") and not MdlOption("YzSideRuler"):

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


       if not MdlOption("AllTopRulers") and not MdlOption("YxTopRuler"):
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

       if not MdlOption("All2DviewsRulers") and not MdlOption("AllTopRulers") and not MdlOption("AllSideRulers") and not MdlOption("ZviewRulers") and not MdlOption("ZxTopRuler") and not MdlOption("ZySideRuler"):
           return

       quarkpy.mdleditor.setsingleframefillcolor(editor, view)
       if not MdlOption("AllSideRulers") and not MdlOption("ZySideRuler"):
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


       if not MdlOption("AllTopRulers") and not MdlOption("ZxTopRuler"):
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

quarkpy.mdleditor.ModelEditor.finishdrawing = gridfinishdrawing


# ********* This creates the Options menu 2D grid items ***************


def All2DviewsRulersClick(m):
    editor = mapeditor()
    if not MdlOption("All2DviewsRulers"):
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XzSideRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YzSideRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def All2DviewsTopRulers(m):
    editor = mapeditor()
    if not MdlOption("AllTopRulers"):
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XzSideRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YzSideRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def All2DviewsSideRulers(m):
    editor = mapeditor()
    if not MdlOption("AllSideRulers"):
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XzSideRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YzSideRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def XviewRulerClick(m):
    editor = mapeditor()
    if not MdlOption("XviewRulers"):
        quarkx.setupsubset(SS_MODEL, "Options")['XviewRulers'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XyTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['XviewRulers'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def XviewYtopRuler(m):
    editor = mapeditor()
    if not MdlOption("XyTopRuler"):
        quarkx.setupsubset(SS_MODEL, "Options")['XyTopRuler'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['XyTopRuler'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def XviewZsideRuler(m):
    editor = mapeditor()
    if not MdlOption("XzSideRuler"):
        quarkx.setupsubset(SS_MODEL, "Options")['XzSideRuler'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['XyTopRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['XzSideRuler'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def YviewRulerClick(m):
    editor = mapeditor()
    if not MdlOption("YviewRulers"):
        quarkx.setupsubset(SS_MODEL, "Options")['YviewRulers'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['YviewRulers'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def YviewXtopRuler(m):
    editor = mapeditor()
    if not MdlOption("YxTopRuler"):
        quarkx.setupsubset(SS_MODEL, "Options")['YxTopRuler'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YzSideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['YxTopRuler'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def YviewZsideRuler(m):
    editor = mapeditor()
    if not MdlOption("YzSideRuler"):
        quarkx.setupsubset(SS_MODEL, "Options")['YzSideRuler'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['YxTopRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['YzSideRuler'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def ZviewRulerClick(m):
    editor = mapeditor()
    if not MdlOption("ZviewRulers"):
        quarkx.setupsubset(SS_MODEL, "Options")['ZviewRulers'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZxTopRuler'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['ZviewRulers'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def ZviewXtopRuler(m):
    editor = mapeditor()
    if not MdlOption("ZxTopRuler"):
        quarkx.setupsubset(SS_MODEL, "Options")['ZxTopRuler'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZySideRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['ZxTopRuler'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)

def ZviewYsideRuler(m):
    editor = mapeditor()
    if not MdlOption("ZySideRuler"):
        quarkx.setupsubset(SS_MODEL, "Options")['ZySideRuler'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['All2DviewsRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllTopRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['AllSideRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZviewRulers'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['ZxTopRuler'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['ZySideRuler'] = None
    quarkpy.mdlutils.Update_Editor_Views(editor, 6)


def View2DrulerMenu(editor):

    X0 = quarkpy.qmenu.item("All 2D views rulers", All2DviewsRulersClick, "|All 2D views rulers:\n\nIf this menu item is checked, it will display the distance across the 'top' and 'side' of the current selected face(s) in all 2D views and deactivate this menu's individual items.|intro.mapeditor.menu.html#optionsmenu")

    X1 = quarkpy.qmenu.item("   all top rulers", All2DviewsTopRulers, "|all top rulers:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected face(s) in all 2D views and deactivate this menu's individual items.|intro.mapeditor.menu.html#optionsmenu")

    X2 = quarkpy.qmenu.item("   all side rulers", All2DviewsSideRulers, "|all side rulers:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected face(s) in all 2D views and deactivate this menu's individual items.|intro.mapeditor.menu.html#optionsmenu")

    X3 = quarkpy.qmenu.item("X-Back 2D view", XviewRulerClick, "|X-Back 2D view:\n\nIf this menu item is checked, it will display a scale of the current grid setting in the ' X - Back ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X4 = quarkpy.qmenu.item("   y (top) ruler", XviewYtopRuler, "|X view, y (top) ruler:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected face(s) in the ' X - Face ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X5 = quarkpy.qmenu.item("   z (side) ruler", XviewZsideRuler, "|X view, z (side) ruler:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected face(s) in the ' X - Face ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X6 = quarkpy.qmenu.item("Y-Side 2D view", YviewRulerClick, "|Y-Side 2D view:\n\nIf this menu item is checked, it will display a scale of the current grid setting in the ' Y-Side ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X7 = quarkpy.qmenu.item("   x (top) ruler", YviewXtopRuler, "|Y view, x (top) ruler:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected face(s) in the ' Y-Side ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X8 = quarkpy.qmenu.item("   z (side) ruler", YviewZsideRuler, "|Y view, z (side) ruler:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected face(s) in the ' Y-Side ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X9 = quarkpy.qmenu.item("Z-Top 2D view", ZviewRulerClick, "|Z-Top 2D view:\n\nIf this menu item is checked, it will display a scale of the current grid setting in the ' Z-Top ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X10 = quarkpy.qmenu.item("   x (top) ruler", ZviewXtopRuler, "|Z view, x (top) ruler:\n\nIf this menu item is checked, it will display the distance across the 'top' of the current selected face(s) in the ' Z-Top ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    X11 = quarkpy.qmenu.item("   y (side) ruler", ZviewYsideRuler, "|Z view, y (side) ruler:\n\nIf this menu item is checked, it will display the distance across the 'side' of the current selected face(s) in the ' Z-Top ' 2D view and deactivate this menu's conflicting item(s) such as  'All 2D views'  if they are currently checked.|intro.mapeditor.menu.html#optionsmenu")

    menulist = [X0, X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, X11]

    items = menulist
    X0.state = quarkx.setupsubset(SS_MODEL,"Options").getint("All2DviewsRulers")
    X1.state = quarkx.setupsubset(SS_MODEL,"Options").getint("AllTopRulers")
    X2.state = quarkx.setupsubset(SS_MODEL,"Options").getint("AllSideRulers")
    X3.state = quarkx.setupsubset(SS_MODEL,"Options").getint("XviewRulers")
    X4.state = quarkx.setupsubset(SS_MODEL,"Options").getint("XyTopRuler")
    X5.state = quarkx.setupsubset(SS_MODEL,"Options").getint("XzSideRuler")
    X6.state = quarkx.setupsubset(SS_MODEL,"Options").getint("YviewRulers")
    X7.state = quarkx.setupsubset(SS_MODEL,"Options").getint("YxTopRuler")
    X8.state = quarkx.setupsubset(SS_MODEL,"Options").getint("YzSideRuler")
    X9.state = quarkx.setupsubset(SS_MODEL,"Options").getint("ZviewRulers")
    X10.state = quarkx.setupsubset(SS_MODEL,"Options").getint("ZxTopRuler")
    X11.state = quarkx.setupsubset(SS_MODEL,"Options").getint("ZySideRuler")

    return menulist

shortcuts = {}


# ************************************************************
# ******************Creates the Popup menu********************

def ViewAmendMenu2click(m):
    editor = mapeditor(SS_MODEL)
    if editor is None: return
    m.items = View2DrulerMenu(editor)


RulerMenuCmds = [quarkpy.qmenu.popup("Ruler guide in 2D views", [], ViewAmendMenu2click, "|Ruler guide in 2D views:\n\nThese functions allow you to display a line with the unit distance of total selected items in any one, combination, or all of the 2D views of the Editor.", "intro.mapeditor.menu.html#optionsmenu")]
    

# ----------- REVISION HISTORY ------------
#
#$Log: mdltools.py,v $
#Revision 1.19  2010/05/05 15:46:39  cdunde
#To stop jerky movement in Model Editor when scrolling, panning.
#
#Revision 1.18  2008/07/15 23:16:27  cdunde
#To correct typo error from MldOption to MdlOption in all files.
#
#Revision 1.17  2008/02/22 09:52:21  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.16  2007/11/29 16:34:35  danielpharos
#Prevent some model editor functions from triggering in the map editor. This should fix some errors that that popped-up when switching from the model editor to the map editor.
#
#Revision 1.15  2007/11/18 02:40:57  cdunde
#To fix error in mdltools.py with rulers when a single new triangle is created.
#
#Revision 1.14  2007/10/22 02:22:27  cdunde
#To remove use of the "dictspec" function which at this time causes a memory leak in the source code.
#
#Revision 1.13  2007/10/09 22:05:43  cdunde
#To change rulers selection measurement items for the Model Editor.
#
#Revision 1.12  2007/10/08 16:47:39  cdunde
#Tying to get version control and change to ASCII.
#
#Revision 1.11  2007/10/06 20:46:09  cdunde
#To reset version.
#
#Revision 1.10  2007/10/06 20:46:09  cdunde
#To reset version.
#
#Revision 1.9  2007/10/06 20:46:09  cdunde
#To reset version.
#
#Revision 1.7  2007/10/06 20:42:54  cdunde
#To reset version.
#
#