# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

Terrain mouse dragging  and other modes
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapterrainmodes.py,v 1.28 2008/07/24 23:34:11 cdunde Exp $



Info = {
   "plug-in":       "Terrain Modes Toolbar",
   "desc":          "Terrain Modes Toolbar",
   "date":          "March 3 2005",
   "author":        "cdunde and Rowdy",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6.5" }

#py2.4 indicates upgrade change for python 2.4

import quarkpy.qhandles
from quarkpy.maputils import *
import mapmovevertex
import mapterrainpos # this is for the dialog boxes.
import faceutils     # this is for getting a vertex the cursor is near.

ico_dict['ico_terrmodes'] = LoadIconSet1("maptrm", 1.0)

## below are new, not sure what is needed to keep
import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.mapeditor
import quarkpy.mapcommands
import quarkpy.mapoptions
import quarkpy.mapbtns
import mapsnapobject
import mergepolys
import quarkpy.maphandles
from quarkpy.maputils import *
import maptagpoint
from math import *

import quarkpy.qhandles
from quarkpy.qhandles import *

## think I need these below

from quarkpy.qeditor import *
from quarkpy.qdictionnary import Strings
import quarkpy.qmenu
import quarkpy.qbaseeditor
from tagging import *
from faceutils import *
from  maptagside import *


########## not sure if I need these items below-test later ############

MOUSEZOOMFACTOR = math.sqrt(2)     # with this value, the zoom factor doubles every two click
STEP3DVIEW = 64.0

vfSkinView = 0x80 # 2d only - used for skin page for mdl editor and bezier page for map editor


############### I know I need these def's and stuff below ##############


#
# Global variables that are set by the map editor.
#
# There are two grid values : they are the same, excepted when
# there is a grid but disabled; in this case, the first value
# is 0 and the second one is the disabled grid step - which is
# used only if the user hold down Ctrl while dragging.
#

grid = (0,0)
lengthnormalvect = 0
mapicons_c = -1
saveeditor = None
newpoly = newface = newpoint = None
selectlist = []
allupFaces = []
alldownmovesFaces = []
commonfaces = []
commonitems = []
selfpolylist = []
newlist = []
set_error_reset = None

def getfaces(editor):
    global allupFaces, alldownmovesFaces
    allupFaces = editor.Root.findallsubitems("up", ':f')
    alldownmovesFaces = editor.Root.findallsubitems("downmoves", ':f')

#
# For dialog menu button.
# As new selectors are added that can use a dialog box
# run them through this menu selection button.
# A maximum of 20 buttons can use this feature.
#
def DialogClick(m):
    editor = mapeditor()
    if quarkx.setupsubset(SS_MAP, "Building").getint("TerrMode") < 20 and quarkx.setupsubset(SS_MAP, "Building").getint("DragMode") > 4:
        if quarkx.setupsubset(SS_MAP, "Building").getint("TerrMode") == 0:
            if editor.layout.explorer.sellist == []:
                quarkx.msgbox("No selection has been made.\n\nYou must first select a group\nof faces to activate this tool and\nchange your settings for this selector.", MT_ERROR, MB_OK)
                return
            else:
                o = editor.layout.explorer.sellist
                m = qmenu.item("Dummy", None, "")
                m.o = o
                mapterrainpos.Selector1Click(m)

        elif quarkx.setupsubset(SS_MAP, "Building").getint("TerrMode") > 0:

            m = qmenu.item("Dummy", None, "")
            mapterrainpos.PaintBrushClick(m)

        else:
            quarkx.msgbox("Your current Terrain Selector does not use this function.\n\nIt only applyies to one that shows it (uses 'Dialog Box')\n                      in its discription popup.", MT_INFORMATION, MB_OK)
            return
    else:
        quarkx.msgbox("This 'Dialog Box' function is only used with\n'QuArK's Terrain Generator' selectors.\n\nSelect one that shows it (uses 'Dialog Box')\n               in its discription popup.", MT_ERROR, MB_OK)
        return


def Dialog3DviewsClick(m):
    editor = mapeditor()
    if quarkx.setupsubset(SS_MAP, "Building").getint("TerrMode") < 20 and quarkx.setupsubset(SS_MAP, "Building").getint("DragMode") > 4:

        m = qmenu.item("Dummy", None, "")
        mapterrainpos.Options3DviewsClick(m)

    else:
        quarkx.msgbox("This 'Dialog Box' function is only used with\n'QuArK's Terrain Generator' selectors.\n\nSelect one that shows it (uses 'Dialog Box')\n               in its discription popup.", MT_ERROR, MB_OK)
        return

#
# return top, bottom, left, right, back w.r.t. view
#  perspective if possible.
#
def terrainWedgeFaceDict(o, view):

    faces = o.subitems
    if len(faces)!=5:
        return None
    axes = quarkpy.perspective.perspectiveAxes(view)
    pool = faces[:]
    faceDict = {}
## This determins if the imported terrain is from GenSurf or Nems Terrain Generator
    if o.subitem(0).normal.tuple[2] > 0:

## Start ----This is the Nems Terrain Generator Seciton

        for face in o.subitems:
            polyofface = face.parent # get the ploy of the UP face
            facevertexes = face.verticesof(polyofface)
            if face.normal.tuple[2] > 0:
                if facevertexes[1].tuple[0] == facevertexes[2].tuple[0] and facevertexes[2].tuple[1] > facevertexes[0].tuple[1]:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('b',1,-1)
                                            ,('l',0, 1)
                                            ,('r',0,-1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)
                    continue
                if facevertexes[0].tuple[0] == facevertexes[1].tuple[0] and facevertexes[2].tuple[1] > facevertexes[1].tuple[1]:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('l',1,-1)
                                            ,('r',0, 1)
                                            ,('b',0,-1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)
                    continue
                if facevertexes[1].tuple[0] == facevertexes[2].tuple[0] and facevertexes[0].tuple[1] > facevertexes[1].tuple[1]:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('l',0,-1)
                                            ,('r',1,-1)
                                            ,('b',0, 1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)
                    continue
                else:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('b',0,-1)
                                            ,('l',1,-1)
                                            ,('r',0, 1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)

## End ----This is the Nems Terrain Generator Seciton

    else:

## Start ----This is the GenSurf Terrain Seciton
        for face in o.subitems:
            polyofface = face.parent # get the ploy of the UP face
            facevertexes = face.verticesof(polyofface)
            if face.normal.tuple[2] > 0:
                if facevertexes[1].tuple[0] == facevertexes[2].tuple[0] and facevertexes[0].tuple[0] > facevertexes[1].tuple[0]:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('b',0, 1)
                                            ,('r',0,-1)
                                            ,('l',1,-1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)
                    continue
                if facevertexes[0].tuple[0] == facevertexes[2].tuple[0] and facevertexes[1].tuple[1] > facevertexes[0].tuple[1]:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('l',1,-1)
                                            ,('r',0, 1)
                                            ,('b',0,-1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)
                    continue
                if facevertexes[0].tuple[0] == facevertexes[1].tuple[0] and facevertexes[1].tuple[1] > facevertexes[0].tuple[1]:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('l',0,-1)
                                            ,('r',1,-1)
                                            ,('b',0, 1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)
                    continue
                else:
                    for (label, ax, dir) in (('u',2, 1)
                                            ,('d',2,-1)
                                            ,('b',1,-1)
                                            ,('r',0,-1)
                                            ,('l',0, 1)):
                        chosenface = pool[0]
                        axis = axes[ax]*dir
                        chosendot = chosenface.normal*axis
                        for face in pool[1:]:
                            if face.normal*axis>chosendot:
                                chosenface=face
                                chosendot=face.normal*axis
                        faceDict[label]=chosenface
                        pool.remove(chosenface)

## End ----This is the GenSurf Terrain Seciton

    return faceDict


def terrainWedgeRename(oldpoly, view):
    "renames the faces of a 5-face polyhedron wedge in accord with perspective of last-clicked-on view"

    dict = terrainWedgeFaceDict(oldpoly, view)
    newpoly = quarkx.newobj("terrain wedge:p")
    for (key, name) in (('u','up'   )
                       ,('d','down' )
                       ,('l','left' )
                       ,('r','right')
                       ,('b','back' )):
        newface = dict[key].copy()
        newface.shortname = name
        newpoly.appenditem(newface)

    return newpoly

def newfinishdrawing(editor, view, oldfinish=quarkpy.mapeditor.MapEditor.finishdrawing):
    oldfinish(editor, view)


def aligntogrid(v, mode):
    #
    # mode=0: normal behaviour
    # mode=1: if v is a 3D point that must be forced to grid (when the Ctrl key is down)
    #
    g = grid[mode]
    if g<=0.0:
        return v   # no grid
    rnd = quarkx.rnd
    return quarkx.vect(rnd(v.x/g)*g, rnd(v.y/g)*g, rnd(v.z/g)*g)

def setupgrid(editor):
    #
    # Set the grid variable from the editor's current grid step.
    #
    global grid
    grid = (editor.grid, editor.gridstep)

def cleargrid():
    global grid
    grid = (0,0)


def clickedbutton(editor):
    "Rebuilds all the handles depending on active toolbar button"

    tb2 = editor.layout.toolbars["tb_terrmodes"]
    if tb2.tb.buttons[10].state == 2:
        for view in editor.layout.views:
            type = view.info["type"]
            if type == "3D":
                view.handles = []
                uniquesel = editor.layout.explorer.uniquesel
                if editor.layout.explorer.sellist != [] and uniquesel == [] or uniquesel == "None":
                    view.repaint()
                    selectlist = editor.layout.explorer.sellist
                    drawredfaces(view, selectlist)
                else:
                    editor.layout.explorer.selchanged()
            else:
                pass
    else:
        editor.layout.explorer.selchanged()


def drawredfaces(view, selectlist):
    "draws the selected faces red"

    def draw(view, selectlist):
        cv = view.canvas()
        cv.pencolor = MapColor("Tag") # red
        cv.penwidth = 1
        cv.penstyle = PS_SOLID
        for face in selectlist:
            if face.type!=(":f"): return
            polylist = face.faceof
            for poly in polylist:
                if poly.type !=(":p"): return
            for vtx in face.vertices: # is a list of a list item
                sum = quarkx.vect(0, 0, 0)
                p2 = view.proj(vtx[-1])  # the last one
                for v in vtx:
                    p1 = p2
                    p2 = view.proj(v)
                    sum = sum + p2
                    cv.line(p1,p2)

    type = view.info["type"]
    if type == "3D":
        viewname = view.info["viewname"]
        if viewname == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_redfaces1"] == "1":
            draw(view, selectlist)
        if viewname == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_redfaces2"] == "1":
            draw(view, selectlist)
    else:
        draw(view, selectlist)


def paintcursor(view, x, y, flags):
    "Changes cursor in views based on view type"

    editor = saveeditor
    tb2 = editor.layout.toolbars["tb_terrmodes"]
    type = view.info["type"]
    if type == "3D" and flags & MB_CLICKED is not None or view.viewmode == "tex":
        if tb2.tb.buttons[10].state == 2 and view.cursor != -21:
            view.cursor = CR_HAND

        if tb2.tb.buttons[11].state == 2:
            if view.viewmode == "tex" and view.cursor != 12:
                view.cursor = CR_BRUSH
            if view.viewmode != "tex" and view.cursor == 12 or view.cursor == -21:
                if MapOption("CrossCursor", editor.MODE):
                    view.cursor = CR_CROSS
                    view.handlecursor = CR_ARROW
                else:
                    view.cursor = CR_ARROW
                    view.handlecursor = CR_CROSS


def terrainpaint(editor, view, x, y, flags, facelist):
    "Temporarily paints the outline shape of a face"

    def paint(editor, view, x, y, facelist):
        if facelist is None:
            choice = quarkpy.maphandles.ClickOnView(editor, view, x, y) #checks if pointing at poly or something
            if choice == []: return
            facelist = []
            for lists in choice:
                face = lists[2]
                facelist.append(face)

        for face in facelist:
            if face is None: continue
            temp = face.faceof
            for item in temp:
                poly = item
            if poly is None: continue
            if poly.shortname.startswith("terrain wedge"):

    # this section just deals with outlining the side faces before painting
    # but seemed too cluttered in the 3D views with all these face lines drawn
             #   tb2 = editor.layout.toolbars["tb_terrmodes"]
             #   if tb2.tb.buttons[11].state == 2: # The Paint Brush Tool button
             #       sidestoo = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_sidestoo"]
             #       sidesonly = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_sidesonly"]

             #       for face in poly.subitems:
             #           if face.name == ("upstop:f") or face.name == ("up:f") or face.name == ("down:f") or face.name == ("downmoves:f"):
             #               continue

             #           if (sidestoo == "0" and sidesonly == "0" and face.name == ("left:f")) or (sidestoo == "0" and sidesonly == "0" and face.name == ("right:f")) or (sidestoo == "0" and sidesonly == "0" and face.name == ("back:f")):
             #               continue

             #           if (sidesonly == "1" and face.name == ("up:f")) or (sidesonly == "1" and face.name == ("downmoves:f")):
             #               continue

             #           elif (sidesonly == "0" and sidestoo == "0" and face.name == ("left:f")) or (sidesonly == "0" and sidestoo == "0" and face.name == ("right:f")) or (sidesonly == "0" and sidestoo == "0" and face.name == ("back:f")):
             #               continue
             #           else:

          # sets up to draw LIME outline of just side faces to get texture
                  #          cv = view.canvas()
                  #          cv.pencolor = LIME
                  #          cv.penwidth = 1
                  #          cv.penstyle = PS_SOLID
                  #          cv.fontcolor = LIME

                            # Draws LIME outline of just side faces to get texture
                 #           for vtx in face.vertices: # is a list of lists
                 #               p2 = view.proj(vtx[-1])  # the last one
                 #               print "p2",p2
                 #               sum = quarkx.vect(0, 0, 0)
                 #               for v in vtx:
                 #                   if len(vtx) == 3: continue
                 #                   p1 = p2
                 #                   p2 = view.proj(v)
                 #                   print "p1",p1
                 #                   print "p2",p2
                 #                   sum = sum + p2
                 #                   cv.line(p1,p2)
                 #                   print "----------------------"

    ### draws the individual FUCHSIA (terrain "up") faces
    ### and Dk. blue (terrain "downmove") faces
    ### outlines but nothing is selected
                cv = view.canvas()
                cv.penwidth = 1
                cv.penstyle = PS_SOLID
                if poly.findname("up:f") is not None:
                    face = poly.findname("up:f")
                    cv.pencolor = FUCHSIA
                    cv.fontcolor = FUCHSIA
                    h = []  # define list for face vextor handles
                    for vtx in face.vertices: # is a list of lists
                        sum = quarkx.vect(0, 0, 0)
                        p2 = view.proj(vtx[-1])  # the last vector in the list vtx of vectors
                        for v in vtx:
                            p1 = p2
                            p2 = view.proj(v)
                            sum = sum + p2
                            cv.line(p1,p2)

                        quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing

                if poly.findname("downmoves:f") is not None:
                    face = poly.findname("downmoves:f")
                    cv.pencolor = MapColor("Duplicator")   # Dk. blue
                    cv.fontcolor = MapColor("Duplicator")  # Dk. blue
                    for vtx in face.vertices: # is a list of lists
                        sum = quarkx.vect(0, 0, 0)
                        p2 = view.proj(vtx[-1])  # the last one
                        for v in vtx:
                            p1 = p2
                            p2 = view.proj(v)
                            sum = sum + p2
                            cv.line(p1,p2)
                    quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing


    type = view.info["type"]
    if type == "3D":
        viewname = view.info["viewname"]
        if viewname == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_color1"] == "1":
            paint(editor, view, x, y, facelist)
        if viewname == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_color2"] == "1":
            paint(editor, view, x, y, facelist)


def viewsingleface(editor, view, vertex, poly):
    "Creates the handle to move the primary face."

    view.handles = []
    h = []
     # add just the selected verttex of the primary face to the handle
    h.append(TerrainVertexHandle(vertex, poly))

    view.handles = quarkpy.qhandles.FilterHandles(h, SS_MAP)


################### I know I need the above def's and stuff ############

########### start of buttons and their funcitons ############
#
# Additionnal drag modes (other plug-ins may add other drag modes).
#

### This selects polys only and bases for creating red select square ##
##### This MUST be left in for the other selectors to work #####

parent = quarkpy.qhandles.RectangleDragObject


###  1st button -- creates the basic Terrain Mesh 2 triangle style ###

class BasicPoly2:

    def __init__(self, editor, face):
        editor = mapeditor()
        dup = quarkx.newobj("Terrain Maker 2:d")
        dup["macro"]="dup terrain2"
        dup["wedgeunits"]="32"
        dup["sameheight"]=""
        dup["detailmesh"]=""
        undo=quarkx.action()
        undo.exchange(dup, face)

        p = quarkx.newobj("cube:p");

        face = quarkx.newobj("up:f")
        face["v"] = (0,0,32, 128,0,32, 0,128,32)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("down:f")
        face["v"] = (0,0,0, 0,128,0, 128,0,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("left:f")
        face["v"] = (-64,0,0, -64,0,128, -64,128,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("back:f")
        face["v"] = (0,64,0, 0,64,128, 128,64,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("right:f")
        face["v"] = (64,0,0, 64,128,0, 64,0,128)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("front:f")
        face["v"] = (0,-64,0, 128,-64,0, 0,-64,128)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        dup.appenditem(p)

        quarkpy.mapbtns.dropitemsnow(editor, [dup], "create Terrain Maker 2")
        editor.invalidateviews()

def MakeTerrain2Click(m):

    editor = mapeditor()
    BasicPoly2(quarkx.clickform, editor)
    editor.invalidateviews()


###  2nd button -- creates the basic Terrain Mesh 2 triangle X style ###

class BasicPoly2X:

    def __init__(self, editor, face):
        editor = mapeditor()
        dup = quarkx.newobj("Terrain Maker 2X:d")
        dup["macro"]="dup terrain2X"
        dup["wedgeunits"]="32"
        dup["sameheight"]=""
        dup["detailmesh"]=""
        undo=quarkx.action()
        undo.exchange(dup, face)

        p = quarkx.newobj("cube:p");

        face = quarkx.newobj("up:f")
        face["v"] = (0,0,32, 128,0,32, 0,128,32)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("down:f")
        face["v"] = (0,0,0, 0,128,0, 128,0,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("left:f")
        face["v"] = (-64,0,0, -64,0,128, -64,128,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("back:f")
        face["v"] = (0,64,0, 0,64,128, 128,64,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("right:f")
        face["v"] = (64,0,0, 64,128,0, 64,0,128)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("front:f")
        face["v"] = (0,-64,0, 128,-64,0, 0,-64,128)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        dup.appenditem(p)

        quarkpy.mapbtns.dropitemsnow(editor, [dup], "create Terrain Maker 2X")
        editor.invalidateviews()

def MakeTerrain2XClick(m):

    editor = mapeditor()
    BasicPoly2X(quarkx.clickform, editor)
    editor.invalidateviews()


###  3rd button -- creates the basic Terrain Mesh 4 triangle style ###

class BasicPoly4:

    def __init__(self, editor, face):
        editor = mapeditor()
        dup = quarkx.newobj("Terrain Maker 4:d")
        dup["macro"]="dup terrain4"
        dup["wedgeunits"]="32"
        dup["sameheight"]=""
        dup["detailmesh"]=""
        undo=quarkx.action()
        undo.exchange(dup, face)

        p = quarkx.newobj("cube:p");

        face = quarkx.newobj("up:f")
        face["v"] = (0,0,32, 128,0,32, 0,128,32)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("down:f")
        face["v"] = (0,0,0, 0,128,0, 128,0,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("left:f")
        face["v"] = (-64,0,0, -64,0,128, -64,128,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("back:f")
        face["v"] = (0,64,0, 0,64,128, 128,64,0)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("right:f")
        face["v"] = (64,0,0, 64,128,0, 64,0,128)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        face = quarkx.newobj("front:f")
        face["v"] = (0,-64,0, 128,-64,0, 0,-64,128)
        face["tex"] = "[terrain]"
        p.appenditem(face)

        dup.appenditem(p)

        quarkpy.mapbtns.dropitemsnow(editor, [dup], "create Terrain Maker 4")
        editor.invalidateviews()

def MakeTerrain4Click(m):

    editor = mapeditor()
    BasicPoly4(quarkx.clickform, editor)
    editor.invalidateviews()


### 4th button -- Converts other Imported terrains into the proper format to use with the QuArK Terrain Generator. ###

def Convert2TerrainClick(m):
    "Converts other Imported terrains into the proper format to use with the QuArK Terrain Generator"

    editor = mapeditor()
    if editor is None:
        return
    view = quarkx.clickform.focus

    selectitems = []
    selectlist = editor.layout.explorer.sellist

    ok = 1
    if (len(selectlist) < 1):
        quarkx.msgbox("Nothing has been selected\n\nUse a 'STANDARD' selection method to select the Imported Terrain\npoly or group of polys you wish to convert so that they can be\nedited using the QuArK Terrain Generator.\n\nThey must be of a triangular shape to convert and edit properly.", MT_ERROR, MB_OK)
        ok = 0
        return

    if selectlist is not None:
        counter = 0
        errors = 0
        terrainpoly = 0
        for item in selectlist:

            if item.type == ":p":
                counter = counter + 1
                if item.itemcount <> 5:
                    errors = errors + 1
                    continue
                else:
                    if item.shortname.startswith("terrain wedge"):
                        terrainpoly = terrainpoly + 1
                    else:
                        selectitems.append(item)
 
            else:
                newlist = FindSelectable(item,None,[":p"])
                for item in newlist:
                    counter = counter + 1
                    if item.itemcount <> 5:
                        errors = errors + 1
                    else:
                        if item.shortname.startswith("terrain wedge"):
                            terrainpoly = terrainpoly + 1
                        else:
                            selectitems.append(item)

    oldpolys = []
    newpolys = []
    for oldpoly in selectitems:
        oldpolys.append(oldpoly)
        newpoly = plugins.mapterrainmodes.terrainWedgeRename(oldpoly, view)
        newpolys.append(newpoly)

    undo=quarkx.action()
    for i in range(len(oldpolys)):
        undo.exchange(oldpolys[i], newpolys[i])
    editor.ok(undo, "Convert imported terrain")
    editor.invalidateviews()
    quarkx.msgbox("Your selection has been processed properly\nand now usable with QuArK Terrain Generator.\n\nThey remain in the same location as before."+"\n\nNumber of items processed      "+str(counter)+"\nErrors found and removed       "+str(errors)+"\nItem conversions not needed   "+str(terrainpoly)+"\nItems converted successfully   "+str(counter-errors-terrainpoly), MT_CONFIRMATION, MB_OK)


### 5th button -- Converts selected up and down faces so ONLY the UP faces are allowed to move ###

def ConvOnlyUpmoveClick(m):
    "Converts selected up and down faces so ONLY the UP faces are allowed to move"

    editor = mapeditor()
    if editor is None:
        return

    selectlist = editor.layout.explorer.sellist
    ok = 1
    if (len(selectlist) < 1):
        quarkx.msgbox("Nothing has been selected\n\nSelect the Terrain sections you wish to\nallow ONLY the 'up' faces to be moved,\nthen click the conversion button again.", MT_ERROR, MB_OK)
        ok = 0

    templist = []
    for face in selectlist:
            if face.shortname == "downmoves":
                face.shortname = "down"
                faces = face.faceof
                for face in faces:
                    if face.findname("up:f") is None:
                        face = face.findname("upstop:f")
                        face.shortname = "up"
            if face.shortname == "upstop":
                face.shortname = "up"
            if face.shortname == "up":
                templist.append(face)
    editor.layout.explorer.sellist = templist
    templist = None
    editor.invalidateviews()


### 6th button -- Converts selected up and down faces so ONLY the DOWN faces are allowed to move ###

def ConvOnlyDownmoveClick(m):
    "Converts selected up and down faces so ONLY the DOWN faces are allowed to move"

    editor = mapeditor()
    if editor is None:
        return

    selectlist = editor.layout.explorer.sellist
    ok = 1
    if (len(selectlist) < 1):
        quarkx.msgbox("Nothing has been selected\n\nSelect the Terrain sections you wish to\nallow ONLY the 'down' faces to be moved,\nthen click the conversion button again.", MT_ERROR, MB_OK)
        ok = 0

    templist = []
    for face in selectlist:
        poly = face.parent
        for face in poly.subitems:
            if face.shortname == "down":
                face.shortname = "downmoves"
            if face.shortname == "downmoves":
                templist.append(face)
            if face.shortname == "up":
                face.shortname = "upstop"
    editor.layout.explorer.sellist = templist
    templist = None
    editor.invalidateviews()


### 7th button -- Converts selected up and down faces so they BOTH are allowed to move ###

def ConvBothmoveClick(m):
    "Converts selected up and down faces so they BOTH are allowed to move"

    editor = mapeditor()
    if editor is None:
        return

    selectlist = editor.layout.explorer.sellist
    ok = 1
    if (len(selectlist) < 1):
        quarkx.msgbox("Nothing has been selected\n\nSelect the Terrain sections you wish to allow\nBOTH the 'up' and 'down' faces to be moved,\nthen click the conversion button again.", MT_ERROR, MB_OK)
        ok = 0

    templist = []
    for face in selectlist:
        poly = face.parent
        for face in poly.subitems:
            if face.shortname == "down":
                face.shortname = "downmoves"
            if face.shortname == "downmoves":
                templist.append(face)
            if face.shortname == "upstop":
                face.shortname = "up"
            if face.shortname == "up":
                templist.append(face)
    editor.layout.explorer.sellist = templist
    templist = None
    editor.invalidateviews()



# 8th button - Rowdys new code to test to get adjasent unselected vertexes 4-20-05

def GetAdjFacesClick(m):
     editor = mapeditor()
     if editor is None:
         return
     if editor.layout.explorer.sellist != []:
         selected = editor.layout.explorer.sellist
     else:
         selected = editor.layout.explorer.uniquesel
     ok = 1
     if selected is None:
         quarkx.msgbox("Select 1 movable face only", MT_ERROR, MB_OK)
         ok = 0
     elif (len(selected) > 1):
         quarkx.msgbox("Select 1 movable face only", MT_ERROR, MB_OK)
         ok = 0

     if ok:
         # ensure everything selected is a proper movable face
         for select1 in selected:
             if select1.shortname == "up" or select1.shortname == "downmoves":
                 ok = 1
                 continue
             if select1.shortname == "upstop" or select1.shortname == "down":
                 quarkx.msgbox("This face has not\nbeen set as movable.\nSelect the proper button\nabove to set it then the\n'Adjacent Faces' again.", MT_ERROR, MB_OK)
                 return
             else:
                 quarkx.msgbox("Improper Selection\n\nYou must select a\nsingle movable face", MT_ERROR, MB_OK)
                 selected = []
                 return
     if ok:
         selectedFaces = selected
         # find all 'up' or 'downmoves' faces
         allFaces = editor.Root.findallsubitems("", ':f')
         upFaces = []
         for face in allFaces:
             if face.shortname == "up" or face.shortname == "downmoves":
                 upFaces.append(face)

         # select all adjacent 'up' or 'downmoves' faces (hopefully)
         adjacentFaces = shared_vertices(selectedFaces, upFaces)
         if (len(adjacentFaces) <= 1):
             quarkx.msgbox("There are no movable\nadjacent faces to this one", MT_INFORMATION, MB_OK)
             return

         editor.layout.explorer.sellist = adjacentFaces
         editor.invalidateviews()


### 9th button -- or 1st selector -- selects Terrain Mesh area ###

class TerrainRectSelDragObject(quarkpy.qhandles.RectangleDragObject):

    "A red rectangle that selects the Terrain movable faces"
    "that have their center points inside the rectangle."
    "This allows for more specific selection of them."

    Hint = hintPlusInfobaselink("Basic Selector of\nTerrain Wedge Faces\n(uses 'Dialog Box')\ndefault settings:\n'Top'   0.5  1.0\n'Base'  0.5  1.0||Basic Selector of Terrain Wedge Faces:\n\nThis works like 'rectangular selection of polyhedron', but selects just the Terrain Wedge ('up') Faces on top, instead of the entire polyhedrons, for movement.\n\nUnless any of the ('down') bottom faces have been set for selection as well.\n\nIn which case, those will be selected and moved as well.", "intro.terraingenerator.selection.html#basicselector")

    def __init__(self, view, x, y, redcolor, todo):
        self.todo = todo
        self.view = view
        self.x = x
        self.y = y

        quarkpy.qhandles.RectangleDragObject.__init__(self, view, x, y, redcolor, todo)

        z = 0
        quarkx.clickform = view.owner  # Rowdys -important, gets the
                                       # mapeditor and view clicked in
        editor = mapeditor()

    def rectanglesel(self, editor, x,y, rectangle):

        global set_error_reset
        from plugins.faceutils import set_error
        if set_error == 1:
            set_error_reset = None

        if rectangle is None: return
        if not ("T" in self.todo):
            editor.layout.explorer.uniquesel = None
        grouplist = FindSelectable(editor.Root, None, [":p"])
        polylist = []
        facelist = []

        for poly in grouplist:
            if poly.shortname.startswith("terrain wedge"):
                polylist.append(poly)
        for poly in polylist:

# Moves the UP faces if they exist
            if poly.findname("up:f") is not None:
                face = poly.findname("up:f")

# This limits the selection area.
                if rectangle.intersects(face):
                    org = face.origin
                    if org is None: continue
                    for f in rectangle.faces:
                        if org*f.normal < f.dist/.05:
                            break
                    else: # the point is inside the polyhedron
                        face.selected = 1
                facelist.append(face)

# Moves the downmoves faces if they exist
            if poly.findname("downmoves:f") is not None:
                face = poly.findname("downmoves:f")
# This limits the selection area.
                if rectangle.intersects(face):
                    org = face.origin
                    if org is None: continue
                    for f in rectangle.faces:
                        if org*f.normal < f.dist/.05:
                            break
                    else: # the point is inside the polyhedron
                        face.selected = 1
                facelist.append(face)

        lastsel = None
        for face in facelist:
            org = face.origin
            if org is None: continue
            for f in rectangle.faces:
                if org*f.normal > f.dist:
                    break
            else: # the point is inside the polyhedron up face
                face.selected = 1
                lastsel = face

        if lastsel is not None:
            list = editor.layout.explorer.sellist
            color = 255
            bbox = quarkx.boundingboxof(list)
            for face in list:
                poly = face.parent
                if len(face.verticesof(poly)) != 3:
                    quarkx.msgbox("You have an improper triangle in your selection !\n\nYou need to repair this poly and try again.\nWhen you click 'OK' the invalid poly will be selected for you.", MT_WARNING, MB_OK)
                    list = []
                    editor.layout.explorer.sellist = []
                    editor.layout.explorer.uniquesel = poly
                    editor.layout.explorer.selchanged()
                    editor.invalidateviews()
                    return
            else:
                editor.layout.explorer.selchanged()
                editor.invalidateviews()
    #    perimfaces, non_perimfaces, perimvertexs, movablevertexes = perimeter_edges(editor)
    #    editor.lockedVertices = perimvertexs

#
# Linear Mapping Circle handle.
#

class TerrainLinearHandle(quarkpy.qhandles.GenericHandle):
    "Creates all the Linear Circle handle items."

    def __init__(self, pos, mgr):
        quarkpy.qhandles.GenericHandle.__init__(self, pos)
        self.mgr = mgr    # a LinHandlesManager instance

    def drag(self, v1, v2, flags, view):
        delta = v2-v1
        if flags&MB_CTRL:
            g1 = 1
        else:
            delta = aligntogrid(delta, 0)
            g1 = 0
        if delta or (flags&MB_REDIMAGE):
            new = map(lambda obj: obj.copy(), self.mgr.list)
            if not self.linoperation(new, delta, g1, view):          
                if not flags&MB_REDIMAGE:
                    new = None
        else:
            new = None

        return self.mgr.list, new


class TerrainLinHandlesManager:
    "Controls the blue Liner Handle and draws the selected faces in red"

    def __init__(self, color, bbox, list, view):
        self.color = color
        self.bbox = bbox
        self.view = view

# New code to draw just the handles I want - copied from LinHandlesManager class

        bmin, bmax = bbox
        bmin1 = bmax1 = ()
        for dir in "xyz":
            cmin = getattr(bmin, dir)
            cmax = getattr(bmax, dir)
            diff = cmax-cmin
            if diff<32:
                diff = 0.5*(32-diff)
                cmin = cmin - diff
                cmax = cmax + diff
            bmin1 = bmin1 + (cmin,)
            bmax1 = bmax1 + (cmax,)
        self.bmin = quarkx.vect(bmin1)
        self.bmax = quarkx.vect(bmax1)
        self.list = list

# Sometimes we don't can't get the mapeditor(), so this test for it and gets it.

        if mapeditor() is not None:
            editor = mapeditor()
        else:
            quarkx.clickform = view.owner  # Rowdys -important, gets the
            editor = mapeditor()
        self.editor = editor # so we can pass it along to other def's

        if editor.layout.explorer.sellist is not None:
            selectlist = editor.layout.explorer.sellist

    def BuildHandles(self, center=None, minimal=None):
        "Builds ONLY the handle CONTOLE & LOCATION - but not the handle DRAWING"
        "That is done in the 'def draw' function further down."

        editor = self.editor
            
        list = editor.layout.explorer.sellist
        view = self.view

        if center is None:
            center = 0.5 * (self.bmin + self.bmax)
        self.center = center
        if minimal is not None:
            view, grid = minimal
            closeto = view.space(view.proj(center) + quarkx.vect(-99,-99,0))
            distmin = 1E99
            mX, mY, mZ = self.bmin.tuple
            X, Y, Z = self.bmax.tuple
            for x in (X,mX):
                for y in (Y,mY):
                    for z in (Z,mZ):
                        ptest = quarkx.vect(x,y,z)
                        dist = abs(ptest-closeto)
                        if dist<distmin:
                            distmin = dist
                            pmin = ptest
            f = -grid * view.scale(pmin)

        h = []

        mX, mY, mZ = self.bmin.tuple
        X, Y, Z = self.bmax.tuple
        self.center = self.center #+ quarkx.vect(0,0,48)
                                       # This is the actual control handle
                                       # location and adds 48 grid units to "z"
                                       # to raise it above the selected face group.
##      self.center is the center of the selected faces and the movement "handle"

        h = h + [plugins.mapterrainmodes.TerrainLinCenterHandle(self.center, self)]
        return h


    def DrawLinHandleCircle(self, view):
        "Draws the blue circle around all objects."

        cx, cy = [], []
        mX, mY, mZ = self.bmin.tuple
        X, Y, Z = self.bmax.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    p = view.proj(x,y,z)
                    if not p.visible: return
                    cx.append(p.x)
                    cy.append(p.y)
        mX = min(cx)
        mY = min(cy)
        X = max(cx)
        Y = max(cy)
        cx = (X+mX)*0.5
        cy = (Y+mY)*0.5
        mX = int(mX)   #py2.4
        mY = int(mY)   #py2.4
        X = int(X)     #py2.4
        Y = int(Y)     #py2.4
        cx = int(cx)   #py2.4
        cy = int(cy)   #py2.4
        dx = X-cx
        dy = Y-cy
        radius = math.sqrt(dx*dx+dy*dy)
        radius = int(radius)   #py2.4
        cv = view.canvas()
        cv.pencolor = self.color
        cv.brushstyle = BS_CLEAR
        cv.ellipse(cx-radius, cy-radius, cx+radius+1, cy+radius+1)
        cv.line(mX, cy, cx-radius, cy)
        cv.line(cx, mY, cx, cy-radius)
        cv.line(cx+radius, cy, X, cy)
        cv.line(cx, cy+radius, cx, Y)


class TerrainLinCenterHandle(TerrainLinearHandle):
    "Draws the blue drag handle at the center of the blue Linear circle."

    hint = "          move selection in grid steps (Ctrl key: gives free movement)|move selection"

    def __init__(self, pos, mgr):
        TerrainLinearHandle.__init__(self, pos, mgr)
        self.cursor = CR_MULTIDRAG
        if mapeditor() is not None:
            editor = mapeditor()
        else:
            quarkx.clickform = view.owner  # Rowdys -important, gets the
            editor = mapeditor()
        self.editor = editor


    def draw(self, view, cv, draghandle=None): # Just draws the handle and circle
                                               # but does not actualy drag anything
                                               # that is done in "def BuildHandles" above
        quarkx.clickform = view.owner  # Rowdys -important, gets the
                                       # mapeditor and view clicked in
        editor = self.editor
        selectlist = editor.layout.explorer.sellist

# Regulates which 3D view selected faces redlines are to be drawn

        type = view.info["type"]
        if type == "3D":
            viewname = view.info["viewname"]
            if viewname == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_redfaces1"] != "0":
                drawredfaces(view, selectlist)  # calls to draw the red faces
            if viewname == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_redfaces2"] != "0":
                drawredfaces(view, selectlist)  # calls to draw the red 

        else:
            drawredfaces(view, selectlist)  # calls to draw the red faces

# Regulates which 3D view handles are to be drawn

        type = view.info["type"]
        if type == "3D":
            tb2 = editor.layout.toolbars["tb_terrmodes"]
            if tb2.tb.buttons[10].state == 2:
                self.cursor = CR_HAND
                self.hint = "?"
                return
            viewname = view.info["viewname"]
            if viewname == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_drag1"] == "0":
                if tb2.tb.buttons[11].state == 2 and view.viewmode == "tex":
                    self.cursor = CR_BRUSH
                    self.hint = "?"
                    return
                else:
                    if MapOption("CrossCursor", editor.MODE):
                        self.cursor = CR_CROSS
                        self.handlecursor = CR_CROSS
                    else:
                        self.cursor = CR_ARROW
                        self.handlecursor = CR_ARROW
                    self.hint = "?"
                    return
            if viewname == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_drag2"] == "0":
                if tb2.tb.buttons[11].state == 2 and view.viewmode == "tex":
                    self.cursor = CR_BRUSH
                    self.hint = "?"
                    return
                else:
                    if MapOption("CrossCursor", editor.MODE):
                        self.cursor = CR_CROSS
                        self.handlecursor = CR_CROSS
                    else:
                        self.cursor = CR_ARROW
                        self.handlecursor = CR_ARROW
                    self.hint = "?"
                    return

        # Draws the 2D and 3D view center handle and circle as they come through one at a time
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = self.mgr.color
            cv.rectangle(int(p.x)-4, int(p.y)-4, int(p.x)+4, int(p.y)+4)  #py2.4  # Gives the handle size from center point

        self.mgr.DrawLinHandleCircle(view)  # calls to draw the circle

    def linoperation(self, list, delta, g1, view):  # This conroles face movment

        editor = self.editor
        self.delta = delta
        self.view = view
        g1 = 0
        grid = (editor.grid, editor.gridstep)
        self.TerrainSoftMove(view)
        for obj in list:
            obj.translate(delta, g1 and grid[0])
        self.draghint = vtohint(delta)
        return delta  # Where the face "group" is moved to in x, y and z corrds.
                      # But we only use z for Terrain Generator or polys will break.

    def TerrainSoftMove(self, view):
        "Takes the selected terrain faces and"
        "recreates their polys for each drag move"

        global set_error_reset
        editor = self.editor
        if editor.layout.explorer.sellist is None: return
        selectlist = editor.layout.explorer.sellist

        perimfaces, non_perimfaces, perimvertexs, movablevertexes = plugins.faceutils.perimeter_edges(editor)
  
        from plugins.faceutils import set_error
        if set_error == 1:
            set_error_reset = 1

  #    editor.lockedVertices = perimvertexs
    #    perimvertexs = editor.lockedVertices

        # This section, to return, needed for Touch-up dragging error after undo
        if perimvertexs is None:

           # stops from errasing stuff in the view after undo of Touch-up drag
            holdlist = editor.layout.explorer.sellist
            editor.layout.explorer.sellist = []
            editor.layout.explorer.sellist = holdlist
            holdlist = []

            return None

        strperimvertexs=[]
        for edge in perimvertexs:
            strperimvertexs.append(str(edge))
           
        grid = (editor.grid, editor.gridstep)
        pos = self.pos
        delta = self.delta
        view = self.view
        bbox = self.mgr.bbox
        pX, pY, pZ = pos.tuple
        dX, dY, dZ = delta.tuple
        Zpos = quarkx.vect(0, 0, pZ)
        Zdelta = delta + quarkx.vect(-dX, -dY, 0)
        oldfaces=[]
        newfaces=[]

## Start of feeding faces in 1 at a time for movement processing.
        for face in selectlist:
            polyofface = face.parent # get the ploy of the UP face
            oldface=[] #all other faces of UPs poly
            TGlockvertex=[]
            non_perimvertex=[]
            facemoved = None  # same as delta augment
            facevectlist = face.vertices

## This is the current code for passing the perimeter vertexes of this one face.

            item=None
            for vertex in face.verticesof(polyofface):
                if not(str(vertex) in strperimvertexs):
                    non_perimvertex.append(vertex)
                else:
                    TGlockvertex.append(vertex)

            if len(non_perimvertex) == 0:
                oldverpos = TGlockvertex[1]
            else:
                if face.shortname == "up":
                    for vertex in non_perimvertex:
                        oldverpos = vertex
                if face.shortname == "downmoves":
                    if len(non_perimvertex) == 1:
                        oldverpos = non_perimvertex[0]
                    else:
                        oldverpos = face.verticesof(polyofface)[1]
                    if TGlockvertex != []:
                        if str(oldverpos) == str(TGlockvertex[0]):
                            TGlockvertex.reverse()
                            oldverpos = non_perimvertex[0]

            vX, vY, vZ = oldverpos.tuple
            Zfactor = Zdelta.tuple[2]

## Method to try and stop faces from crashing into others and breaking poly
## but creates problems when moving up and down faces togeather.
       #     if face.name == "up:f":
       #         for face2 in polyofface.subitems:
       #             if face2.name == "down:f" or face2.name == "downmoves:f":
       #                 downface = face2.verticesof(polyofface)
       #                 tfX, tfY, tfZ = downface[1].tuple
       #         if vZ > tfZ+16:
       #             facemoved = Zdelta*.15
       #         else:
       #             if Zfactor <= 0:
       #                 facemoved = quarkx.vect(0, 0, 0)
       #             else:
       #                 facemoved = Zdelta*.15

       #     if face.name == "downmoves:f":
       #         for face2 in polyofface.subitems:
       #             if face2.name == "upstop:f" or face2.name == "up:f":
       #                 upface = face2.verticesof(polyofface)
       #                 tfX, tfY, tfZ = upface[2].tuple
       #         if vZ < tfZ-32:
       #             facemoved = Zdelta*.15
       #         else:
       #             if Zfactor >= 0:
       #                 facemoved = quarkx.vect(0, 0, 0)
       #             else:
       #                 facemoved = Zdelta*.15

## This area slows down the movement of the handle for better control.
            facemoved = Zdelta*.15

## This sets up the face into a single item list as required for movement function.
            oldface.append(face)
            oldface, newface = plugins.mapmovetrianglevertex.moveTriangleFaces(oldface, oldverpos, facemoved, polyofface, TGlockvertex, pos, bbox)

## This builds a list of all the returned old and new faces to be swapped a one time.
            for old in oldface:
                oldfaces.append(old)
            for new in newface:
                newfaces.append(new)

    # swap the old and new faces into the map
        undo=quarkx.action()
        for i in range(len(oldfaces)):
            undo.exchange(oldfaces[i], newfaces[i])
        editor.ok(undo, "Move Terrain")
        editor.invalidateviews() # test for just 3D view only


#====================================================
# Below deals with the TerrainManager to pass mouse actions to specific buttons

def TerrainManager(editor, view, x, y, flags, handle):
    global saveeditor, commonfaces, commonitems
    saveeditor = editor
    facelist = None
    tb2 = editor.layout.toolbars["tb_terrmodes"]
    color = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_color"]  # Get Dialog box setting if to draw the color guides is on or off.
    if tb2.tb.buttons[10].state == 2 or tb2.tb.buttons[11].state == 2: # The Touch-up and Paint Brush Tool buttons
        type = view.info["type"]

        pointervect = quarkx.vect(x,y,0) # This gives the cursor's location in the view.

        if type == "3D":
            editor.layout.setupdepth(view)
            paintcursor(view, x, y, flags)
            if tb2.tb.buttons[10].state == 2:
                getfaces(editor)
                face = None
                choice = quarkpy.maphandles.ClickOnView(editor, view, x, y) #checks if pointing at poly or something
                for lists in choice:
                    poly = lists[1]
                    if poly.shortname.startswith("terrain wedge"):
                        testfaces = []
                        commonfaces = []
                        commonitem = []
                        commonitems = []
                        cv = view.canvas()
                        cv.penwidth = 1
                        cv.penstyle = PS_SOLID
                        if poly.findname("up:f") is not None:
                            face = poly.findname("up:f")
                            results = faceutils.cursor2vertex(view, face, poly, pointervect) #returns the face vertex if the cursor is close enough to it.
                            vpos, vertex = results
                            if vpos is not None and vertex is not None and poly is not None:

                                commonfaces.append(face) # to add the selected face, with the handle, last
                                commonitem = (vertex,poly) # to add the selected vertex, with the handle, last
                                commonitems.append(commonitem) # to add the selected vertex, with the handle, last

                                # This section gets the faces that shair the common vertex location
                                for a_face in allupFaces:
                                    if a_face == face:
                                            continue
                                    testfaces.append(a_face)
                                for a_face in testfaces:
                                    temp = []
                                    temp = a_face.faceof
                                    for item in temp:
                                        a_facepoly = item

                                    # Rowdys fixed method
                                #1    a_face_vertexes = a_face.verticesof(a_facepoly)
                                #1    results = faceutils.vertex_in_vertices(vertex, a_face_vertexes)
                                #1    if results == 1:
                                #1        commonfaces.append(a_face)
                                #1        commonitem = (vertex,a_facepoly)
                                #1        commonitems.append(commonitem)

                                    # Cdundes fixed method
                                #2    results = faceutils.cursor2vertex(view, a_face, a_facepoly, pointervect) #returns the face vertex if the cursor is close enough to it.
                                #2    a_face_vpos, a_face_vertex = results
                                #2    if a_face_vpos is not None and a_face_vertex is not None and a_facepoly is not None:
                                #2        commonfaces.append(a_face)
                                #2        commonitem = (a_face_vertex,a_facepoly)
                                #2        commonitems.append(commonitem)
                                #2    else:
                                #2        continue

                                    # Cdundes variable method
                                    variance = float(quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_variance"])
                                    compvtx = faceutils.common_vertexes(vertex, a_face, a_facepoly, variance)
                                    if compvtx is not None:
                                        commonfaces.append(a_face)
                                        commonitem = (compvtx,a_facepoly)
                                        commonitems.append(commonitem)


                                if face is not None and vertex is not None and poly is not None:
                                    viewsingleface(editor, view, vertex, poly) # sends to have handle made for primary face only
                                    view.repaint()
                                    if editor.layout.explorer.sellist != []:
                                        selectlist = editor.layout.explorer.sellist
                                        drawredfaces(view, selectlist)
                                    terrainpaint(editor, view, x, y, flags, commonfaces)
                                    if len(editor.layout.explorer.sellist) == 1:
                                        editor.layout.explorer.sellist = []
                                        return
                                    for p in face.faceof:
                                        if p.type == ':p':
                                            color = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_color"]  # Get Dialog box setting if to draw the color guides is on or off.
                                            if color == "1":
                                                for vtx in face.vertices: # is a list of a list item
                                                    sum = quarkx.vect(0, 0, 0)
                                                    p2 = view.proj(vtx[-1])  # the last one
                                                    cv.reset()
                                                    cv.pencolor = YELLOW
                                                    for v in vtx:
                                                        p1 = p2
                                                        p2 = view.proj(v)
                                                        sum = sum + p2
                                                        cv.line(p1,p2)
                                                for v in face.verticesof(p):
                                                    p = view.proj(v)
                                                    if p.visible:
                                                        cv.reset()
                                                        cv.brushcolor = RED
                                                        cv.rectangle(int(p.x)-1, int(p.y)-1, int(p.x)+5, int(p.y)+5)  #py2.4

                                    cv.reset()
                                    cv.brushcolor = NAVY
                                    cv.rectangle(int(vpos.x)-3, int(vpos.y)-3, int(vpos.x)+5, int(vpos.y)+5)  #py2.4


                        if poly.findname("downmoves:f") is not None:
                            face = poly.findname("downmoves:f")
                            results = faceutils.cursor2vertex(view, face, poly, pointervect) #returns the face vertex if the cursor is close enough to it.
                            vpos, vertex = results
                            if vpos is not None and vertex is not None and poly is not None:

                                commonfaces.append(face) # to add the selected face, with the handle, last
                                commonitem = (vertex,poly) # to add the selected vertex, with the handle, last
                                commonitems.append(commonitem) # to add the selected vertex, with the handle, last

                                # This section gets the faces that shair the common vertex location
                                for a_face in alldownmovesFaces:
                                    if a_face == face:
                                            continue
                                    testfaces.append(a_face)
                                for a_face in testfaces:
                                    temp = []
                                    temp = a_face.faceof
                                    for item in temp:
                                        a_facepoly = item

                                    # Rowdys fixed method
                                #1    a_face_vertexes = a_face.verticesof(a_facepoly)
                                #1    results = faceutils.vertex_in_vertices(vertex, a_face_vertexes)
                                #1    if results == 1:
                                #1        commonfaces.append(a_face)
                                #1        commonitem = (vertex,a_facepoly)
                                #1        commonitems.append(commonitem)

                                    # Cdundes fixed method
                                #2    results = faceutils.cursor2vertex(view, a_face, a_facepoly, pointervect) #returns the face vertex if the cursor is close enough to it.
                                #2    a_face_vpos, a_face_vertex = results
                                #2    if a_face_vpos is not None and a_face_vertex is not None and a_facepoly is not None:
                                #2        commonfaces.append(a_face)
                                #2        commonitem = (a_face_vertex,a_facepoly)
                                #2        commonitems.append(commonitem)
                                #2    else:
                                #2        continue

                                    # Cdundes variable method
                                    variance = float(quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_variance"])
                                    compvtx = faceutils.common_vertexes(vertex, a_face, a_facepoly, variance)
                                    if compvtx is not None:
                                        commonfaces.append(a_face)
                                        commonitem = (compvtx,a_facepoly)
                                        commonitems.append(commonitem)

                                if face is not None and vertex is not None and poly is not None:
                                    viewsingleface(editor, view, vertex, poly) # sends to have handle made for primary face only
                                    view.repaint()
                                    if editor.layout.explorer.sellist != []:
                                        selectlist = editor.layout.explorer.sellist
                                        drawredfaces(view, selectlist)
                                    terrainpaint(editor, view, x, y, flags, commonfaces)
                                    if len(editor.layout.explorer.sellist) == 1:
                                        editor.layout.explorer.sellist = []
                                        return
                                    for p in face.faceof:
                                        if p.type == ':p':
                                            color = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_color"]  # Get Dialog box setting if to draw the color guides is on or off.
                                            if color == "1":
                                                for vtx in face.vertices: # is a list of a list item
                                                    sum = quarkx.vect(0, 0, 0)
                                                    p2 = view.proj(vtx[-1])  # the last one
                                                    cv.reset()
                                                    cv.pencolor = YELLOW
                                                    for v in vtx:
                                                        p1 = p2
                                                        p2 = view.proj(v)
                                                        sum = sum + p2
                                                        cv.line(p1,p2)
                                                for v in face.verticesof(p):
                                                    p = view.proj(v)
                                                    if p.visible:
                                                        cv.reset()
                                                        cv.brushcolor = RED
                                                        cv.rectangle(int(p.x)-1, int(p.y)-1, int(p.x)+5, int(p.y)+5)  #py2.4

                                    cv.reset()
                                    cv.brushcolor = AQUA
                                    cv.rectangle(int(vpos.x)-3, int(vpos.y)-3, int(vpos.x)+5, int(vpos.y)+5)  #py2.4

                    break # This only allows us to get the first item of the list

            else:
                terrainpaint(editor, view, x, y, flags, facelist)


### 10th button -- or 2nd selector -- selects a Terrain Mesh Vertex ###

class TerrainTouchupClick(TerrainRectSelDragObject):

    "Select Terrain in 2D views and"
    "Adjoining terrain face vertexes in 3D views."

    Hint = hintPlusInfobaselink("Touch-up Selector of\nTerrain Wedge Vertexes\n(uses 'Dialog Box')\npress 'Alt' for single face\nselection and movement||Touch-up Selector of Terrain Wedge Vertexes:\n\nThis Selector will highlight the movable Terrain Wedge ('up') Faces on top, or the ('down') bottom faces if any are set for movement and their common vertexes as the cursor pass over them.\n\nWhen the LMB (left mouse button) is held down, these common vertexes can then be moved up or down to shape that one area of terrain surface for detailed touchup work.\n\nIf the 'Alt' key is held down when the selection is made then just the 'primary (yellow) face' will be moved ONLY.", "intro.terraingenerator.selection.html#touchup")

    def __init__(self, view, x, y, redcolor, todo):
        self.todo = todo
        self.view = view
        self.x = x
        self.y = y

        plugins.mapterrainmodes.TerrainRectSelDragObject.__init__(self, view, x, y, redcolor, todo)

        z = 0

        quarkx.clickform = view.owner  # Rowdys -important, gets the
                                       # mapeditor and view clicked in
        self.editor = mapeditor()
        if self.editor is None:
            self.editor = saveeditor

    def dragto(self, x, y, flags):

        global set_error_reset
        from plugins.faceutils import set_error
        if set_error == 1:
            set_error_reset = None

        self.flags = flags
        editor = self.editor
        view = self.view
        type = view.info["type"]
        if type == "3D" and view.viewmode == "tex":

### This section just keeps the rectangle from working in the 3D views

            if editor is None:
                editor = saveeditor
                editor.layout.setupdepth(view)

### below to get the "red rectangle" to work in 2D views only

        else:
            if flags&MB_DRAGGING:
                self.autoscroll(x,y)
            old, ri = self.buildredimages(x, y, flags)
            self.drawredimages(self.view, 1)
            self.redimages = ri
            self.old = old
            if flags&MB_DRAGGING:
                self.drawredimages(self.view, 2)
            return old


class TerrainVertexHandle(quarkpy.qhandles.GenericHandle):
    "A terrain polyhedron face vertex."

    undomsg = Strings[525]
    hint = "||By dragging this point, you can move all of the adjoining face vertexes for fine detail work.\n\nHolding down the Ctrl key while dragging will snap them to the grid.\n\nHolding down the Alt key will cause only the 'primary' face (outlined in red) to be moved.\n\nIf you wish to only have the 'primary' face snap to the grid then first use the Alt key to move it away from the others, then reselect it using the Ctrl key.|intro.terraingenerator.selection.html#paintbrush"

    def __init__(self, pos, poly):
        quarkpy.qhandles.GenericHandle.__init__(self, pos)

        # This makes sure we have the editor if we are in the 3D window view or FullScreen 3D view
        editor = mapeditor()
        if editor is None:
            self.editor = saveeditor
        else:
            self.editor = mapeditor()

        self.pos = pos
        self.poly = poly
        self.cursor = CR_CROSSH
        global selectlist
        self.selectlist = selectlist


    def menu(self, editor, view):

        def forcegrid1click(m, self=self, editor=editor, view=view):
            self.Action(editor, self.pos, self.pos, MB_CTRL, view, Strings[560])

        def cutcorner1click(m, self=self, editor=editor, view=view):
            #
            # Find all edges and faces issuing from the given vertex.
            #
            edgeends = []
            faces = []
            for f in self.poly.faces:
                vertices = f.verticesof(self.poly)
                for i in range(len(vertices)):
                    if not (vertices[i]-self.pos):
                        edgeends.append(vertices[i-1])
                        edgeends.append(vertices[i+1-len(vertices)])
                        if not (f in faces):
                            faces.append(f)
            #
            # Remove duplicates.
            #
            edgeends1 = []
            for i in range(len(edgeends)):
                e1 = edgeends[i]
                for e2 in edgeends[:i]:
                    if not (e1-e2):
                        break
                else:
                    edgeends1.append(e1)
            #
            # Compute the mean point of edgeends1.
            # The new face will go through the point in the middle between this and the vertex.
            #
            pt = reduce(lambda x,y: x+y, edgeends1)/len(edgeends1)
            #
            # Compute the mean normal vector from the adjacent faces' normal vector.
            #
            n = reduce(lambda x,y: x+y, map(lambda f: f.normal, faces))
            #
            # Force "n" to be perpendicular to the screen direction.
            #
            vertical = view.vector(self.pos).normalized   # vertical vector at this point
            n = (n - vertical * (n*vertical)).normalized
            #
            # Find a "model" face for the new one.
            #
            bestface = faces[0]
            for f in faces[1:]:
                if abs(f.normal*vertical) < abs(bestface.normal*vertical):
                    bestface = f
            #
            # Build the new face.
            #
            newface = bestface.copy()
            newface.shortname = "corner"
            newface.distortion(n, self.pos)
            #
            # Move the face to its correct position.
            #
            delta = 0.5*(pt-self.pos)
            delta = n * (delta*n)
            newface.translate(delta)
            #
            # Insert the new face into the polyhedron.
            #
            undo = quarkx.action()
            undo.put(self.poly, newface)
            editor.ok(undo, Strings[563])

        return [qmenu.item("&Cut out corner", cutcorner1click, "|This command cuts out the corner of the polyhedron. It does so by adding a new face near the vertex you right-clicked on. The new face is always perpendicular to the view."),
                qmenu.sep,
                qmenu.item("&Force to grid", forcegrid1click,
                  "force vertex to grid")] + self.OriginItems(editor, view)


    def drawred(self, redimages, view, redcolor):
        "Draw a handle while it is being dragged."

        global newface

        cv = view.canvas()
        cv.penwidth = 1
        cv.penstyle = PS_SOLID
        cv.pencolor = WHITE
        cv.brushstyle = BS_SOLID
        p = view.proj(self.pos)
        if p.visible:
            cv.brushcolor = GREEN
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+5, int(p.y)+5)  #py2.4

        if newface == []:
      #      v1 = v2 = self.pos
            v1 = view.vector("X").normalized
            v2 = view.vector("Y").normalized
            flags = MB_DRAGGING
            newitem = self.drag(v1, v2, flags, view)
            if newface == []:
                return

        if newface.name == ("up:f"):
            cv.reset()
            cv.brushcolor = NAVY
            p = view.proj(newpoint)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+5, int(p.y)+5)  #py2.4

        if newface.name == ("downmoves:f"):
            cv.reset()
            cv.brushcolor = AQUA
            p = view.proj(newpoint)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+5, int(p.y)+5)  #py2.4


    def ok(self, editor,undo,old,new):

        editor.layout.explorer.sellist = []

        if old != [] and new != []:
            quarkpy.qhandles.GenericHandle.ok(self,editor,undo,old,new)

        if self.selectlist != []:
            for poly in new:
                if poly.findname("up:f") is not None:
                    face = poly.findname("up:f")
                    self.selectlist.append(face)

                if poly.findname("downmoves:f") is not None:
                    face = poly.findname("downmoves:f")
                    self.selectlist.append(face)

            editor.layout.explorer.sellist = self.selectlist
            for view in editor.layout.views:
                type = view.info["type"]
                if type == "3D":
                    drawredfaces(view, self.selectlist)
            self.selectlist = []
        else:
            editor.layout.explorer.sellist = []
            self.selectlist = []


    def drag(self, v1, v2, flags, view):

        global newpoly, newface, newpoint, selfpolylist, newlist, commonitems
        newpoly = newface = newpoint = []
        editor = self.editor
        if editor.layout.explorer.sellist != []:
            self.selectlist = editor.layout.explorer.sellist
            editor.layout.explorer.sellist = []

      # Giving the option to use the Alt key to drag just the "primary yellow face's vertex"
        if flags&MB_ALT:
            temp = []
            if len(commonitems) > 0:
                temp = (commonitems[0])
                commonitems = []
                commonitems.append(temp)
            else:
                return None, None

        # If a single face is being dragged qhandles.RedImageDragObject.dragto will send back to here
        # causing selfpolylist and newlist to reset to nothing and face will not be drawn in undo function.
        # The line below will return the old poly and last new poly created allowing it to complete the cycle.

        if flags&MB_DRAGEND: return selfpolylist, newlist

        selfpolylist = []
        newlist = []

        for commonitem in commonitems:

            vertex, poly = commonitem
            if poly.type != ":p": continue
            self.pos = vertex
            self.poly = poly

            # restricts to only Z, up and down movement
            v1 = quarkx.vect(0, 0, v1.tuple[2])
            v2 = quarkx.vect(0, 0, v2.tuple[2])

        #### Vertex Dragging Code by Tim Smith ####

        # compute the projection of the starting point? onto the screen.
            p0 = view.proj(self.pos)
            if not p0.visible: return

        # save a copy of the original faces
            orgfaces = self.poly.subitems

        # first, loop through the faces to see if we are draging
        # more than one point at a time.  This loop uses the distance
        # between the projected screen position of the starting point
        # and the project screen position of the vertex.
            dragtwo = 0
            for f in self.poly.faces:
                if f in orgfaces:
                    if abs(self.pos*f.normal-f.dist) < epsilon:
                        foundcount = 0
                        for v in f.verticesof(self.poly):
                            p1 = view.proj(v)
                            if p1.visible:
                                dx, dy = p1.x-p0.x, p1.y-p0.y
                                d = dx*dx + dy*dy
                                if d < epsilon:
                                    foundcount = foundcount + 1
                        if foundcount == 2:
                            dragtwo = 1

            # if the control key is pressed, align the destination point to grid
            if flags&MB_CTRL:
                v2 = quarkpy.qhandles.aligntogrid(v2, 1)

            # compute the change in position
            delta = v2-v1

            # if the control is not pressed, align delta to the grid
            if not (flags&MB_CTRL):
                delta = quarkpy.qhandles.aligntogrid(delta, 0)

        # if we are dragging
            self.draghint = vtohint(delta)
            if delta or (flags&MB_REDIMAGE):

            # make a copy of the polygon being drug
                new = self.poly.copy()
                newpoly = new

            # loop through the faces
                for f in self.poly.faces:

                # if this face is part of the original group
                    if f in orgfaces:

                    # if the point is on the face
                        if abs(self.pos*f.normal-f.dist) < epsilon:
                            newface = f

                        # collect a list of verticies on the face along
                        # with the distances from the destination point.
                        # also, count the number of vertices.  NOTE:
                        # this loop uses the actual distance between the
                        # two points and not the screen distance.
                            foundcount = 0
                            vlist = []
                            mvlist = []
                            for v in f.verticesof(self.poly):
                                p1 = view.proj(v)
                                if p1.visible:
                                    dx, dy = p1.x-p0.x, p1.y-p0.y
                                    d = dx*dx + dy*dy
                                else:
                                    d = 1
                                if d < epsilon:
                                    foundcount = foundcount + 1
                                    mvlist .append (v)
                                else:
                                    d = v - self .pos
                                    vlist.append((abs (d), v))

                        # sort the list of vertecies, this places the
                        # most distant point at the end
                            vlist.sort ()
                            vmax = vlist [-1][1]

                        # if we are draging two vertecies
                            if dragtwo:

                            # if this face does not have more than one vertex
                            # selected, then skip
                                if foundcount != 2:
                                    continue

                            # the rotational axis is between the two
                            # points being drug.  the reference point is
                            # the most distant point
                                rotationaxis = mvlist [0] - mvlist [1]
                                otherfixed =getotherfixed(vmax, mvlist, rotationaxis)
                                fixedpoints = vmax, otherfixed

                        # otherwise, we are draging one
                            else:

                            # if this face does not have any of the selected
                            # vertecies, then skip
                                if foundcount == 0:
                                    continue

                            # Using the two most distant points
                            # as the axis of rotation
                                rotationaxis = (vmax - vlist [-2] [1])
                                fixedpoints = vmax, vlist[-2][1]

                        # apply the rotation axis to the face (requires that
                        # rotationaxis and vmax to be set).
                        # "newpoint" is the face vertex being dragged of the red poly.
                        # below that, "new" is the poly parent of that newly created red face.
                        # These are used as "globals" and passed to the "drawred" function above.
                            newpoint = self.pos+delta
                            nf = new.subitem(orgfaces.index(f))

                            def pointsok(new,fixed):

                            # coincident not OK
                                if not new-fixed[0]: return 0
                                if not new-fixed[1]: return 0

                            # colinear also not OK
                                if abs((new-fixed[0]).normalized*(new-fixed[1]).normalized)>.999999:
                                   return 0
                                return 1

                            if pointsok(newpoint,fixedpoints):
                                tp = nf.threepoints(2)
                                x,y = nf.axisbase()
                                def proj1(p, x=x,y=y,v=vmax):
                                    return (p-v)*x, (p-v)*y
                                tp = tuple(map(proj1, tp))
                                nf.setthreepoints((newpoint,fixedpoints[0],fixedpoints[1]),0)

                                newnormal = rotationaxis ^ (self.pos+delta-vmax)
                                testnormal = rotationaxis ^ (self.pos-vmax)
                                if newnormal:
                                    if testnormal * f.normal < 0.0:
                                        newnormal = -newnormal


                                if nf.normal*newnormal<0.0:
                                    nf.swapsides()
                                x,y=nf.axisbase()
                                def proj2(p,x=x,y=y,v=vmax):
                                    return v+p[0]*x+p[1]*y
                                tp = tuple(map(proj2,tp))

                            # Code 4 for NuTex
                                nf.setthreepoints(tp ,2)


                # if the face is not part of the original group
                    else:
                        if not (flags&MB_DRAGGING):
                            continue   # face is outside the polyhedron
                        nf = f.copy()   # put a copy of the face for the red image only
                        new.appenditem(nf)

        # final code
                new = [new]
                for newpoly in new:
                    newlist.append(newpoly)
            else:
                continue

            for oldpoly in [self.poly]:
                selfpolylist.append(oldpoly)

        return selfpolylist, newlist



### 11th button -- or 2nd selector -- paints Terrain Mesh area ###


class TerrainPaintClick(TerrainRectSelDragObject):

    "A pass over selector when the LMB is held down to"
    "apply the current texture to a 'moveable' face."

    Hint = hintPlusInfobaselink("Texture Applicator of\nTerrain Wedge Faces\n(uses 'Dialog Box')||Texture Applicator of Terrain Wedge Faces:\n\nThis works like a 'Paint Brush Selector' that will apply the current texture to movable Terrain Wedge ('up') Faces on top, or the ('down') bottom faces if any are set for movement. In which case, the texture will be applied to those faces as well.\n\nIf the 'Sides Too' and 'Sides Only' settings on the 'Touch-up & Paint Brush' dialog box are used, then the sides can also have texture applied to them as well.\n\nThis function only works in the '3D' views. To apply the texture hold down the LMB as you pass the cursor over the desired faces.", "intro.terraingenerator.selection.html#paintbrush")

    def __init__(self, view, x, y, redcolor, todo):
        self.todo = todo
        self.view = view
        self.x = x
        self.y = y

        plugins.mapterrainmodes.TerrainRectSelDragObject.__init__(self, view, x, y, redcolor, todo)

        z = 0
        quarkx.clickform = view.owner  # Rowdys -important, gets the
                                       # mapeditor and view clicked in
        self.editor = mapeditor()

    def dragto(self, x, y, flags):
        editor = self.editor
        view = self.view
        type = view.info["type"]
        if type == "3D" and view.viewmode == "tex":

### Start of new section to get face and apply texture in 3D view only

            if editor is None:
                editor = saveeditor
            editor.layout.setupdepth(view)

            tb2 = editor.layout.toolbars["tb_terrmodes"]
            if tb2.tb.buttons[11].state == 2:
             ## Checks to see that a valid texture has been chosen
                texture = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_tex"]
                if texture is not None and texture != "" and texture != "Select a texture":
                    pass
                else:
                    if flags == 1032 or flags == 1024:
                        return
                    else:
                        quarkx.msgbox("You must select a texture to use.\nClick the dialog button to chose one.", MT_ERROR, MB_OK)
                        view.invalidate()
                        return


            sidestoo = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_sidestoo"]
            sidesonly = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_sidesonly"]
            choicelist = quarkpy.maphandles.ClickOnView(editor, view, x, y) #checks if pointing at poly or something
### Draws the YELLOW face that will be "painted" (re-textured).
            for items in choicelist:

                poly = items[1]
                if poly.shortname.startswith("terrain wedge"):
                    for face in poly.subitems:
                        if face.name == ("upstop:f") or face.name == ("down:f"):
                            continue

                        if (sidestoo == "0" and sidesonly == "0" and face.name == ("left:f")) or (sidestoo == "0" and sidesonly == "0" and face.name == ("right:f")) or (sidestoo == "0" and sidesonly == "0" and face.name == ("back:f")):
                            continue

                        if (sidesonly == "1" and face.name == ("up:f")) or (sidesonly == "1" and face.name == ("downmoves:f")):
                            continue

                        elif (sidesonly == "0" and sidestoo == "0" and face.name == ("left:f")) or (sidesonly == "0" and sidestoo == "0" and face.name == ("right:f")) or (sidesonly == "0" and sidestoo == "0" and face.name == ("back:f")):
                            continue
                        else:

          # sets up to draw YELLOW outline of faces to get texture
                            cv = view.canvas()
                            cv.pencolor = YELLOW
                            cv.penwidth = 1
                            cv.penstyle = PS_SOLID
                            cv.fontcolor = YELLOW

          # Regulates which 3D view the YELLOW outline of faces are to be drawn

                            # Draws YELLOW outline of faces to get texture
                            for vtx in face.vertices: # is a list of lists
                                sum = quarkx.vect(0, 0, 0)
                                p2 = view.proj(vtx[-1])  # the last one
                                for v in vtx:
                                    p1 = p2
                                    p2 = view.proj(v)
                                    sum = sum + p2
                                    cv.line(p1,p2)

          ### This part changes the face texture.
          # This part gets the "Actual" texture image size.
                            tex = face.texturename
                            texobj = quarkx.loadtexture(tex, editor.TexSource)
                            if texobj is not None:
                                try:
                                    texobj = texobj.disktexture # this gets "linked"
                                except quarkx.error:    # and non-linked textures size
                                    texobj = None
                                texX, texY = texobj['Size']
                            else:
                                if flags == 1032 or flags == 1024:
                                    return
                                else:
                                    quarkx.msgbox("A brush has been found with a texture\nthat is not in the Texture Browser.\n\nIt will be selected now so you can choose another texture for it,\nUse the 'Search' > 'Search/replace textures...' function to find others\nor so you know which texture you need to add.", MT_INFORMATION, MB_OK)
                                    editor.layout.explorer.uniquesel = face
                                    editor.layout.explorer.selchanged()
                                    return

          ### Gets the stored dialog box values to be used below.

                            texname = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_tex"]
                     #       originX, originY, originZ = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_origin"]
                            originX, originY, originZ = plugins.mapterrainpos.read3values(quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_origin"]) # fix for linux
                            retain = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_retain"]
                     #       scaleX, scaleY = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_scale"]
                            scaleX, scaleY = plugins.mapterrainpos.read2values(quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_scale"]) # fix for linux
                     #       angleX, angleY = (quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_angles"])
                            angleX, angleY = plugins.mapterrainpos.read2values(quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_angles"]) # fix for linux

          ## The texX and texY are the size of the actual texture image
          ## and are used here to be applied to the scale x and y factors.
          ## .01 sets the percentage factor that 1 in the dialog gives the texture.

                            scaleX = scaleX * texX * .01
                            scaleY = scaleY * texY * .01

          ## Start of "modified" formula from maptexpos.py "def action" section

                            angleY = angleX - angleY*-1
                            angleY = angleX - angleY
                            angleX, angleY = angleX*deg2rad, angleY*deg2rad
                            if  quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_retain"] == "1":
                                p0 = vc = quarkx.vect(originX, originY, originZ)
                            else:
                                p0 = vc = face.origin  # center of the face
                            n = face.normal   # 1 0 0 or x,y,z direction textured side of face is facing - = opposite direction
                            v1, v2 = bestaxes(n, editor.layout.views[0])

                            p1 = p0 + (v1*math.cos(angleX) + v2*math.sin(angleX))*scaleX
                            p2 = p0 + (v1*math.cos(angleY*-1) + v2*math.sin(angleY*-1))*scaleY

                            face.setthreepoints((p0, p1, p2), 2) # Applies distortion. 2nd augment "2" only
                                                                 # applies to positioning texture on the face.
                            tx1 = face.texturename
                            if texname is None:
                                texname = quarkx.setupsubset(SS_MAP, "Options")["PaintBrush_tex"]
                            tx2 = texname
                            tb2 = editor.layout.toolbars["tb_terrmodes"]
                            if tb2.tb.buttons[11].state == 2:
                                face.replacetex(tx1, tx2)

            # Rebuilds all 3D views only
            for view in editor.layout.views:
                type = view.info["type"]
                if type == "3D":
                    view.invalidate(1)

          ### End of new section to get face and apply texture in 3D view only
          ### below to get the "red rectangle" to work in 2D views only

        else:
            if flags&MB_DRAGGING:
                self.autoscroll(x,y)
            old, ri = self.buildredimages(x, y, flags)
            self.drawredimages(self.view, 1)
            self.redimages = ri
            self.old = old     # trying to move actual faces 051505
            if flags&MB_DRAGGING:
                self.drawredimages(self.view, 2)
            return old



### START OF THE TOOLBAR AND BUTTON SETUP ###########
#
# The SELECTION PART of the tool bar with the available terrain modes.
# Add other terrain modes from other plug-ins into this list :
#

TerrModes = [(TerrainRectSelDragObject                 ,9)
            ,(TerrainTouchupClick                       ,10)
            ,(TerrainPaintClick                       ,11)
            ]

### this part effects each buttons selection mode

def selectmode(btn):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    try:
        tb1 = editor.layout.toolbars["tb_terrmodes"]
        tb2 = editor.layout.toolbars["tb_dragmodes"]
        tb3 = editor.layout.toolbars["tb_objmodes"]
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
    quarkx.setupsubset(SS_MAP, "Building").setint("TerrMode", btn.i)
    quarkx.setupsubset(SS_MAP, "Building").setint("DragMode", 5)
    quarkx.setupsubset(SS_MAP, "Building").setint("ObjectMode", 20)

def select1(btn, toolbar, editor):
    editor.MouseDragMode, dummyicon = TerrModes[btn.i]
    btn.state = quarkpy.qtoolbar.selected
    editor.layout.explorer.sellist = []
    editor.layout.explorer.uniquesel = []
    editor.layout.explorer.selchanged()
    try:
        tb2 = editor.layout.toolbars["tb_terrmodes"]
        if tb2.tb.buttons[9].state == 2:
            for view in editor.layout.views:
                if MapOption("CrossCursor", editor.MODE):
                    view.cursor = CR_CROSS
                    view.handlecursor = CR_ARROW
                else:
                    view.cursor = CR_ARROW
                    view.handlecursor = CR_CROSS
    except:
        pass

##### Below makes the toolbar and arainges its buttons #####

class TerrModesBar(ToolBar):
    "The new toolbar with TerrModes buttons. Created from plugins\mapdragmodes.py"

    Caption = "Terrain modes"
    DefaultPos = ((0, 0, 0, 0), 'topdock', 300, 2, 1)

    def buildbuttons(self, layout):
                          # to build the single click button
        ico_dict['ico_terrmodes'] = LoadIconSet1("maptrm", 1.0)
        ico_terrmodes = ico_dict['ico_terrmodes']

        Builderbtn = qtoolbar.button(MakeTerrain2Click, "Terrain Maker 2\n(makes the 2 triangle grig)||Terrain Maker 2:\n\nThis will drop a prefab size of terrain into the editor that you can resize and start working with.\n\nIt can also be found on the ' New Polyhedrons ' > ' Shape Builders ' menu. \n\nAlso, if you create a new rectangular brush and RMB click on it, you will see 'Make Terrain 2' on that menu. This will make a terrain section out of that particular brush. ", ico_terrmodes, 0, infobaselink="intro.terraingenerator.setup.html")

        Builderbtn2X = qtoolbar.button(MakeTerrain2XClick, "Terrain Maker 2X\n(makes the 2 triangle X grig)||Terrain Maker 2X:\n\nThis will drop a prefab size of terrain into the editor that you can resize and start working with.\n\nIt can also be found on the ' New Polyhedrons ' > ' Shape Builders ' menu. \n\nAlso, if you create a new rectangular brush and RMB click on it, you will see 'Make Terrain 2X' on that menu. This will make a terrain section out of that particular brush. ", ico_terrmodes, 1, infobaselink="intro.terraingenerator.setup.html")

        Builderbtn2 = qtoolbar.button(MakeTerrain4Click, "Terrain Maker 4\n(makes the 4 triangle grig)||Terrain Maker 4:\n\nThis will drop a prefab size of terrain into the editor that you can resize and start working with.\n\nIt can also be found on the ' New Polyhedrons ' > ' Shape Builders ' menu. \n\nAlso, if you create a new rectangular brush and RMB click on it, you will see 'Make Terrain 4' on that menu. This will make a terrain section out of that particular brush. ", ico_terrmodes, 2, infobaselink="intro.terraingenerator.setup.html")

        Convert2Terrain = qtoolbar.button(Convert2TerrainClick, "Convert Imported Terrains||Convert Imported Terrains:\n\nThis will convert other Imported terrains into the proper format to use with the QuArK Terrain Generator.\n\nUse a 'STANDARD' selection method to select the Imported Terrain poly or group of polys you wish to convert.\n\nThey must be of a triangular shape to convert and edit properly.", ico_terrmodes, 3, infobaselink="intro.terraingenerator.selection.html#importconverter")

        ConvOnlyUpmove = qtoolbar.button(ConvOnlyUpmoveClick, "Allows ONLY 'up' faces to be moved||Allows ONLY 'up' faces to be moved:\n\nThis will convert all the faces of the current selection group so ONLY the 'up' faces will be allowed to move.", ico_terrmodes, 4, infobaselink="intro.terraingenerator.selection.html#faceconverters")

        ConvOnlyDownmove = qtoolbar.button(ConvOnlyDownmoveClick, "Allows ONLY 'down' faces to be moved||Allows ONLY 'down' faces to be moved:\n\nThis will convert all the faces of the current selection group so ONLY the 'downmove' faces will be allowed to move.", ico_terrmodes, 5, infobaselink="intro.terraingenerator.selection.html#faceconverters")

        ConvBothmove = qtoolbar.button(ConvBothmoveClick, "Allows BOTH 'up' and 'down' faces\nto be moved together||Allows BOTH 'up' and 'down' faces to be moved together:\n\nThis will convert all the faces of the current selection group so BOTH the 'up' and 'down' faces will be allowed to move together.", ico_terrmodes, 6, infobaselink="intro.terraingenerator.selection.html#faceconverters")

        GetAdjFacesbtn = qtoolbar.button(GetAdjFacesClick, "Get Adjacent Faces||Get Adjacent Faces:\n\nSelect one movable face of a poly, 'up' or 'downmove'.\nThen clinking this button will cause any other faces,\ntouching the selected one, to be added to the selection.\n\nYou must select a single movable face for this function to work.", ico_terrmodes, 7, infobaselink="intro.terraingenerator.selection.html#adjacentfaces")

        BuildDialogbtn = qtoolbar.button(DialogClick, "Selector Dialog Input\nopens all dialog boxes||Selector Dialog Input:\n\nThis will open a dialog input box for the 'Terrain Toolbar' item currently in use if it takes input to change the way the terrain is created.\n\nNot all item buttons will have this feature. In which case a message will be displayed as such.\n\nThe items that do have this function will display that it uses the 'Dialog Box' in its description popup.", ico_terrmodes, 8, infobaselink="intro.terraingenerator.selection.html#basicselector")

        Build3DviewsDialogbtn = qtoolbar.button(Dialog3DviewsClick, "3D views Options\nDialog Input\n(opens the input box)||3D views Options Dialog Input:\n\nThis will open its own 'Dialog Box' and is laid out in the same order as the 'Display tool-palette'. \n\nThis dialog gives you the ability to customize every 3D view that QuArK provides and does so independently from one 3D view to the next.", ico_terrmodes, 12, infobaselink="intro.terraingenerator.selection.html#options3d")


                  # to build the Mode buttons
        btns = []
        for i in range(len(TerrModes)):
            obj, icon = TerrModes[i]
            btn = qtoolbar.button(selectmode, obj.Hint, ico_dict['ico_terrmodes'], icon)
            btn.i = i
            btns.append(btn)
        i = quarkx.setupsubset(SS_MAP, "Building").getint("TerrMode")

        dm = quarkx.setupsubset(SS_MAP, "Building").getint("DragMode")
        om = quarkx.setupsubset(SS_MAP, "Building").getint("ObjectMode")
        if i == 20 or dm == 0 or om == 0:

            leave = 0
        else:
            select1(btns[i], self, layout.editor)

        revbtns = [] # to put the single click Builderbtns first then the others.
        revbtns.append(Builderbtn)
        revbtns.append(Builderbtn2X)
        revbtns.append(Builderbtn2)
        revbtns.append(Convert2Terrain)
        revbtns.append(ConvOnlyUpmove)
        revbtns.append(ConvOnlyDownmove)
        revbtns.append(ConvBothmove)
        revbtns.append(GetAdjFacesbtn)
        revbtns.append(BuildDialogbtn)
        revbtns = revbtns + btns
        revbtns.append(Build3DviewsDialogbtn)

        return revbtns


#--- register the new toolbar ---

quarkpy.maptools.toolbars["tb_terrmodes"] = TerrModesBar


# ----------- REVISION HISTORY ------------
#
# $Log: mapterrainmodes.py,v $
# Revision 1.28  2008/07/24 23:34:11  cdunde
# To fix non-ASCII character from causing python depreciation errors.
#
# Revision 1.27  2008/02/22 09:52:22  danielpharos
# Move all finishdrawing code to the correct editor, and some small cleanups.
#
# Revision 1.26  2007/01/31 15:12:16  danielpharos
# Removed bogus OpenGL texture mode
#
# Revision 1.25  2006/11/30 01:17:48  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.24  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.23.2.9  2006/11/26 12:54:04  cdunde
# To reset toolbars default location for removal of unneeded 3D buttons.
#
# Revision 1.23.2.8  2006/11/09 23:17:44  cdunde
# Changed Paint Brush dialog to work with new version view setup and names.
#
# Revision 1.23.2.7  2006/11/03 23:38:10  cdunde
# Updates to accept Python 2.4.4 by eliminating the
# Depreciation warning messages in the console.
#
# Revision 1.23.2.6  2006/11/01 22:22:42  danielpharos
# BackUp 1 November 2006
# Mainly reduce OpenGL memory leak
#
# Revision 1.23.2.4  2006/10/04 21:33:32  danielpharos
# BackUp 4 October 2006 (2)
#
# Revision 1.23  2006/01/30 08:20:00  cdunde
# To commit all files involved in project with Philippe C
# to allow QuArK to work better with Linux using Wine.
#
# Revision 1.22  2006/01/12 07:21:01  cdunde
# To commit all new and related files for
# new Quick Object makers and toolbar.
#
# Revision 1.21  2006/01/10 01:05:16  cdunde
# To fix TG cursors to change according to textured
# and non-textured modes and button changes properly
#
# Revision 1.20  2006/01/09 19:32:37  cdunde
# To fix error and add selection function to TG Paint Brush
# when an unknown texture is found.
#
# Revision 1.19  2006/01/07 08:56:14  cdunde
# To fix a few minor bugs with TG paint brush
# function and make more universal game mode
#
# Revision 1.18  2006/01/07 05:47:48  cdunde
# Update so new paint brush cursor does not
# change if no drag option is chosen for a 3D view
#
# Revision 1.17  2005/12/10 07:19:18  cdunde
# To add new paint brush cursor for Terrain Generator
#
# Revision 1.16  2005/11/15 17:15:49  cdunde
# Removed unneeded code that was
# braking changing modes in 3D views
#
# Revision 1.15  2005/11/14 08:07:41  cdunde
# Again with the cursor fix, hopefully right this time
#
# Revision 1.14  2005/11/13 10:53:54  cdunde
# To correct for key error
#
# Revision 1.13  2005/11/13 10:17:55  cdunde
# Previous fix caused another problem.
# This fix's that cursor setting problem
#
# Revision 1.12  2005/11/10 03:30:50  cdunde
# To finally fix cursor setting problem
#
# Revision 1.11  2005/11/07 00:06:40  cdunde
# To commit all files for addition of new Terrain Generator items
# Touch-up Selector and 3D Options Dialog
#
# Revision 1.10  2005/10/16 00:24:05  cdunde
# Fixed Terrain Generator Paint Brush function to allow
# texture application in all 3D views and update of those views.
#
# Revision 1.9  2005/10/15 00:51:56  cdunde
# To reinstate headers and history
#
# Revision 1.6  2005/09/16 18:08:40  cdunde
# Commit and update files for Terrain Paintbrush addition
#
# Revision 1.5  2005/08/31 22:46:21  cdunde
# To properly fix interference with Model Editor
#
# Revision 1.4  2005/08/26 07:11:13  cdunde
# To temporarily fix interference with Model Editor
#
# Revision 1.3  2005/08/16 22:46:32  cdunde
# To fix 2 first time start bugs:
# terrain button was selected and
# dialog box would open with std selector
#
# Revision 1.2  2005/08/16 04:03:12  cdunde
# Fix toolbar arraignment
#
# Revision 1.1  2005/08/15 05:49:23  cdunde
# To commit all files for Terrain Generator
#

