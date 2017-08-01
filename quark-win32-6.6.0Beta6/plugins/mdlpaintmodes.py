# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

Model Texture Paint modes and their dialog input boxes.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mdlpaintmodes.py,v 1.13 2012/03/11 05:26:38 cdunde Exp $



Info = {
   "plug-in":       "Paint Modes Toolbar",
   "desc":          "Texture painting by mouse dragging",
   "date":          "January 12 2008",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.5" }


import math
import quarkx
import quarkpy.qtoolbar
import quarkpy.dlgclasses
import quarkpy.mdleditor
import quarkpy.mdlhandles
import quarkpy.mdlutils
from quarkpy import qmacro
from quarkpy.maputils import *
from quarkpy.qdictionnary import Strings


#
# Additionnal Paint modes (other plug-ins may add other Paint modes).
#

parent = quarkpy.qhandles.RectangleDragObject

#====================================================
# General functions for this file.
def paintcursor(editor):
    "Changes cursor in views based on viewmode type"

    tb2 = editor.layout.toolbars["tb_paintmodes"]
    if editor.layout.skinview is not None:
        if MapOption("CrossCursor", SS_MODEL):
            if tb2.tb.buttons[1].state == 2:
                editor.layout.skinview.cursor = CR_BRUSH
            elif tb2.tb.buttons[2].state == 2:
                editor.layout.skinview.cursor = CR_AIRBRUSH
            elif tb2.tb.buttons[3].state == 2:
                editor.layout.skinview.cursor = CR_CROSS
            else:
                editor.layout.skinview.cursor = CR_CROSS
        else:
            if tb2.tb.buttons[1].state == 2:
                editor.layout.skinview.cursor = CR_BRUSH
            elif tb2.tb.buttons[2].state == 2:
                editor.layout.skinview.cursor = CR_AIRBRUSH
            elif tb2.tb.buttons[3].state == 2:
                editor.layout.skinview.cursor = CR_ARROW
            else:
                editor.layout.skinview.cursor = CR_ARROW
    for view in editor.layout.views:
        if MapOption("CrossCursor", SS_MODEL):
            if tb2.tb.buttons[1].state == 2 and view.viewmode == "tex":
                view.cursor = CR_BRUSH
            elif tb2.tb.buttons[2].state == 2 and view.viewmode == "tex":
                view.cursor = CR_AIRBRUSH
            elif tb2.tb.buttons[3].state == 2 and view.viewmode == "tex":
                view.cursor = CR_CROSS
            else:
                view.cursor = CR_CROSS
        else:
            if tb2.tb.buttons[1].state == 2 and view.viewmode == "tex":
                view.cursor = CR_BRUSH
            elif tb2.tb.buttons[2].state == 2 and view.viewmode == "tex":
                view.cursor = CR_AIRBRUSH
            elif tb2.tb.buttons[3].state == 2 and view.viewmode == "tex":
                view.cursor = CR_ARROW
            else:
                view.cursor = CR_ARROW


def checkUVs(mdl_editor, pixU, pixV, skin):
    texWidth, texHeight = skin["Size"]
    if (pixU < 0) or (pixU > texWidth-1) or (pixV < 0) or (pixV > texHeight-1):
        return 0
    else:
        return 1


def ClampUV(U, V, texWidth, texHeight):
    U = U - texWidth * int(math.floor(U / texWidth))
    V = V - texHeight * int(math.floor(V / texHeight))
    return U, V


def GetPixel(U_V, texshortname, texparent, skinuvlist=None):
    U, V = U_V
    UV = str(U) + "," + str(V)
    if skinuvlist is not None and skinuvlist.has_key(UV):
        return quarkpy.qutils.ColorToRGB(skinuvlist[UV][0])
    return quarkpy.qutils.ColorToRGB(quarkx.getpixel(texshortname, texparent, U, V))


def GetHeight(RGB):
    return ((RGB[0] * 0.3) + (RGB[1] * 0.59) + (RGB[2] * 0.11)) / 255.0


NormalPalette = (
[69,57,220], [65,74,230], [58,82,228], [82,82,239], [93,49,227], [92,61,237], [90,75,242], [99,74,243], [52,94,229], [66,94,239], [76,93,243], [82,99,247], [90,86,247], [99,82,247], [90,99,247], [90,99,255],
[107,47,228], [117,46,231], [112,63,239], [123,61,239], [107,66,247], [111,70,247], [115,74,247], [123,70,247], [107,82,247], [99,93,249], [99,99,255], [107,90,247], [111,86,251], [115,82,255], [115,90,255], [123,84,252],
[41,107,226], [42,116,227], [54,109,233], [49,120,236], [57,115,239], [66,107,243], [61,119,239], [66,115,247], [66,123,239], [66,123,247], [74,107,247], [74,115,247], [82,107,247], [74,123,247], [82,115,247], [82,119,251],
[90,107,247], [90,107,255], [82,123,255], [90,119,255], [99,107,255], [99,115,255], [99,123,255], [107,99,255], [107,107,255], [107,115,255], [107,123,255], [115,99,255], [115,107,255], [115,115,255], [115,123,255], [123,99,255],
[132,45,230], [132,57,239], [140,49,235], [146,55,235], [132,66,239], [132,66,247], [140,66,239], [144,66,243], [148,66,247], [132,74,247], [140,74,247], [148,74,247], [132,82,251], [140,82,247], [140,90,247], [148,82,247],
[123,107,255], [132,90,255], [132,99,255], [132,107,255], [140,90,255], [140,99,255], [148,90,251], [148,99,255], [140,107,255], [148,107,255], [123,115,255], [132,115,255], [140,115,255], [123,123,255], [132,123,255], [140,123,255],
[160,63,236], [162,79,244], [165,82,247], [156,90,247], [156,99,247], [160,94,251], [165,99,247], [165,99,255], [173,65,235], [186,70,228], [175,86,243], [194,91,234], [165,107,247], [173,99,247], [185,101,241], [204,105,232],
[148,115,255], [148,123,255], [156,107,255], [156,115,255], [165,107,255], [165,115,247], [169,111,251], [173,115,247], [173,115,255], [173,123,247], [181,107,247], [181,115,247], [189,112,244], [186,123,244], [198,117,236], [210,119,227],
[43,137,228], [57,142,237], [66,136,243], [74,132,247], [74,140,247], [82,132,247], [82,132,255], [82,140,247], [57,154,235], [66,152,243], [74,152,243], [78,152,247], [57,165,230], [78,162,243], [67,181,230], [82,185,235],
[90,132,255], [90,140,251], [90,148,247], [90,148,255], [99,136,255], [107,132,255], [107,140,255], [99,148,255], [90,160,247], [99,156,247], [99,156,255], [99,165,247], [94,171,247], [94,181,239], [94,185,243], [95,202,229],
[115,132,255], [123,132,255], [132,132,255], [115,140,255], [123,140,255], [132,140,255], [107,148,255], [115,148,255], [107,160,251], [107,165,255], [115,156,255], [115,165,247], [115,165,255], [123,148,255], [123,156,255], [123,165,255],
[107,173,247], [107,181,247], [107,189,239], [115,173,251], [115,181,247], [123,173,247], [123,173,255], [123,181,247], [111,198,231], [112,189,244], [123,189,239], [123,189,247], [107,198,239], [115,198,239], [123,198,239], [115,211,228],
[132,148,255], [140,132,255], [140,140,255], [140,148,255], [148,132,255], [148,140,255], [148,148,255], [156,123,255], [165,123,255], [173,123,255], [156,132,255], [156,140,255], [165,136,251], [165,140,255], [160,148,251], [165,148,255],
[173,132,247], [173,132,255], [177,136,247], [189,132,243], [181,140,247], [173,148,247], [181,148,247], [181,156,239], [189,144,239], [198,140,231], [211,137,227], [206,153,226], [189,140,247], [198,136,239], [189,148,247], [193,152,239],
[132,156,255], [132,165,255], [132,173,247], [140,160,251], [140,165,255], [148,156,255], [148,165,247], [148,165,255], [132,173,255], [132,181,247], [140,177,247], [148,177,243], [140,186,241], [148,189,239], [140,192,242], [140,208,229],
[156,156,247], [165,156,247], [156,160,251], [165,169,243], [156,177,243], [165,173,247], [162,181,244], [156,202,228], [173,162,244], [173,173,239], [182,164,239], [201,167,227], [173,178,239], [166,200,228], [174,192,230], [188,188,225],
)

### NORMALMAP test code
scale = 0.1

def NORMALIZE(v):
    len = math.sqrt((v[0]*v[0]) + (v[1]*v[1]) + (v[2]*v[2]))
   
    if len > 0:
       len = 1.0 / len
       v[0] *= len
       v[1] *= len
       v[2] *= len
    else:
       v[0] = v[1] = v[2] = 0
    return v

num_elements = 20
kernel_du = []
kernel_dv = []
# case FILTER_SOBEL_5x5:
kernel_du.append([-2, 2, -1.0])
kernel_du.append([-2, 1, -4.0])
kernel_du.append([-2, 0, -6.0])
kernel_du.append([-2, -1, -4.0])
kernel_du.append([-2, -2, -1.0])
kernel_du.append([-1, 2, -2.0])
kernel_du.append([-1, 1, -8.0])
kernel_du.append([-1, 0, -12.0])
kernel_du.append([-1, -1, -8.0])
kernel_du.append([-1, -2, -2.0])
kernel_du.append([1, 2, 2.0])
kernel_du.append([1, 1, 8.0])
kernel_du.append([1, 0, 12.0])
kernel_du.append([1, -1, 8.0])
kernel_du.append([1, -2, 2.0])
kernel_du.append([2, 2, 1.0])
kernel_du.append([2, 1, 4.0])
kernel_du.append([2, 0, 6.0])
kernel_du.append([2, -1, 4.0])
kernel_du.append([2, -2, 1.0])
        
kernel_dv.append([-2, 2, 1.0])
kernel_dv.append([-1, 2, 4.0])
kernel_dv.append([ 0, 2, 6.0])
kernel_dv.append([ 1, 2, 4.0])
kernel_dv.append([ 2, 2, 1.0])
kernel_dv.append([-2, 1, 2.0])
kernel_dv.append([-1, 1, 8.0])
kernel_dv.append([ 0, 1, 12.0])
kernel_dv.append([ 1, 1, 8.0])
kernel_dv.append([ 2, 1, 2.0])
kernel_dv.append([-2, -1, -2.0])
kernel_dv.append([-1, -1, -8.0])
kernel_dv.append([ 0, -1, -12.0])
kernel_dv.append([ 1, -1, -8.0])
kernel_dv.append([ 2, -1, -2.0])
kernel_dv.append([-2, -2, -1.0])
kernel_dv.append([-1, -2, -4.0])
kernel_dv.append([ 0, -2, -6.0])
kernel_dv.append([ 1, -2, -4.0])
kernel_dv.append([ 2, -2, -1.0])



#====================================================
# Below deals with the different sections of the editor's TexViews and SkinView.
# Below deals with the different sections of the editor's TexViews Solid paint functions.
def TexViewSolid(mdl_editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, paintcolor, PenWidth):
    editor = mdl_editor
    newImage = skin
    ### Saves the original color for the pixel about to be colored.
    UV = str(pixU) + "," + str(pixV)
    if not skinuvlist.has_key(UV):
        OrgColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
        if OrgColor == 0:
            OrgColor = 1
        skinuvlist[UV] = [OrgColor]

    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
        UV = str(pixU) + "," + str(pixV)
        if skinuvlist.has_key(UV):
            color = skinuvlist[UV][0]
            quarkx.setpixel(texshortname, texparent, pixU, pixV, color) # Draws the center pixel, where clicked.
            del skinuvlist[UV]

    else:
        quarkx.setpixel(texshortname, texparent, pixU, pixV, paintcolor) # Draws the center pixel, where clicked.

    # For rectangle shape.
    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"] == "rectangle":
        if not PenWidth&1: # PenWidth is even, solid paint, rectangle.
            radius = 1
            while radius <= PenWidth*.5:

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius+1:
                    U=pixU+fill
                    V=pixV+radius
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = radius-1      ### Draws left line, bottom to top.
                negradius = -radius
                while fill > negradius:
                    U=pixU-radius+1
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius+1     ### Draws top line, left to right.
                while fill <= radius:
                    U=pixU+fill
                    V=pixV-radius+1
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius+1     ### Draws right line, top to bottom.
                while fill <= radius:
                    U=pixU+radius
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # PenWidth is odd, solid paint, rectangle.
            radius = 1
            while radius <= int(PenWidth*.5):

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius:
                    U=pixU+fill
                    V=pixV+radius
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = radius        ### Draws left line, bottom to top.
                negradius = -radius
                while fill >= negradius:
                    U=pixU-radius
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius       ### Draws top line, left to right.
                while fill <= radius:
                    U=pixU+fill
                    V=pixV-radius
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius       ### Draws right line, top to bottom.
                while fill <= radius:
                    U=pixU+radius
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    else:  # For ellipse (round) shape.
           # Formula adapted from http://www.mathopenref.com/chord.html

        if not PenWidth&1: # PenWidth is even, solid paint, ellipse (round).
            radius = 1
            while radius <= PenWidth*.5+1:
                r = PenWidth*.5+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord+1:
                    U=int(pixU+fill)
                    V=int(pixV+radius)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill > negcord:
                    U=int(pixU-radius+1)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord+1:
                    U=int(pixU+fill)
                    V=int(pixV-radius+1)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord+1:
                    U=int(pixU+radius)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # PenWidth is odd, solid paint, ellipse (round).
            radius = 1
            while radius <= int(PenWidth*.5)+1:
                r = int(PenWidth*.5)+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord:
                    U=int(pixU+fill)
                    V=int(pixV+radius)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill >= negcord:
                    U=int(pixU-radius)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord:
                    U=int(pixU+fill)
                    V=int(pixV-radius)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord:
                    U=int(pixU+radius)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            paintcolor = None

                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                paintcolor = skinuvlist[UV][0]

                        if paintcolor:
                            quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    editor.Root.currentcomponent.currentskin = newImage
    for v in editor.layout.views:
        if v.viewmode == "tex":
            v.invalidate(1)

    if editor.layout.skinview is not None:
        skin = editor.Root.currentcomponent.currentskin
        editor.layout.skinview.background = quarkx.vect(-int(skin["Size"][0]*.5),-int(skin["Size"][1]*.5),0), 1.0, 0, 1
        editor.layout.skinview.backgroundimage = skin,
        editor.layout.skinview.repaint()


# Below deals with the different sections of the editor's TexViews Airbrush functions.
def TexViewAirbrush(mdl_editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, airbrushcolor, BrushWidth, StartPalette=None, EndPalette=None, RGBStart=None, RGBEnd=None):
    editor = mdl_editor
    newImage = skin
    radius = 1
    ### Saves the original color for the pixel about to be colored.
    UV = str(pixU) + "," + str(pixV)
    if not skinuvlist.has_key(UV):
        OrgColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
        if OrgColor == 0:
            OrgColor = 1
        skinuvlist[UV] = [OrgColor]

    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
        OldPixelColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
        if Pal:
            rFactor = abs((float(radius-1)/float((BrushWidth*.5)-1)) * (1 - Opacity))
            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
        else:
            NewPaintColor = RGBEnd
            NewColor = [0, 0, 0]
            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
            for i in range(0, 3):
                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                NewColor[2-i] = int(check)
            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
        quarkx.setpixel(texshortname, texparent, pixU, pixV, NewPaintColor) # Draws the center pixel, where clicked.

    elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
        if skinuvlist.has_key(UV):
            color = skinuvlist[UV][0]
            quarkx.setpixel(texshortname, texparent, pixU, pixV, color) # Draws the center pixel, where clicked.
            del skinuvlist[UV]

    else:
        quarkx.setpixel(texshortname, texparent, pixU, pixV, airbrushcolor) # Draws the center pixel, where clicked.

    # For rectangle shape
    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] == "rectangle":
        if not BrushWidth&1: # BrushWidth is even, airbrush, rectangle.
            while radius <= BrushWidth*.5:

                # Below resets the airbrush color as rings are draw from center, outwards.
                rFactor = abs((float(radius-1)/float((BrushWidth*.5)-1)) * (1 - Opacity))
                if Pal:
                    NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                else:
                    NewColor = [0, 0, 0]
                    for i in range (0, 3):
                        NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                    NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                color = NewPaintColor

                # Below draws the rings from center, outwards.

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius+1:
                    U=pixU+fill
                    V=pixV+radius
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if NewPaintColor > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if NewPaintColor < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = radius-1      ### Draws left line, bottom to top.
                negradius = -radius
                while fill > negradius:
                    U=pixU-radius+1
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius+1     ### Draws top line, left to right.
                while fill <= radius:
                    U=pixU+fill
                    V=pixV-radius+1
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]  # To setup an empty list to use below.
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius+1     ### Draws right line, top to bottom.
                while fill <= radius:
                    U=pixU+radius
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]  # To setup an empty list to use below.
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # BrushWidth is odd, airbrush, rectangle.
            while radius <= int(BrushWidth*.5):

                # Below resets the airbrush color as rings are draw from center, outwards.
                rFactor = abs((float(radius+1)/float(((BrushWidth+1)*.5))) * (1 - Opacity))
                if Pal:
                    NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                else:
                    NewColor = [0, 0, 0]
                    for i in range (0, 3):
                        NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                    NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                color = NewPaintColor

                # Below draws the rings from center, outwards.

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius:
                    U=pixU+fill
                    V=pixV+radius
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if NewPaintColor > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if NewPaintColor < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1 # This IS correct, do not change.
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = radius        ### Draws left line, bottom to top.
                negradius = -radius
                while fill >= negradius:
                    U=pixU-radius
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]  # To setup an empty list to use below.
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius       ### Draws top line, left to right.
                while fill <= radius:
                    U=pixU+fill
                    V=pixV-radius
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius       ### Draws right line, top to bottom.
                while fill <= radius:
                    U=pixU+radius
                    V=pixV+fill
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    else:  # For airbrush, ellipse (round) shape.
           # Formula adapted from http://www.mathopenref.com/chord.html

        if not BrushWidth&1: # BrushWidth is even, airbrush, ellipse (round).
            while radius <= BrushWidth*.5+1:

                # Below resets the airbrush color as rings are draw from center, outwards.
                rFactor = abs((float(radius-1)/float((BrushWidth*.5)-1)) * (1 - Opacity))
                if Pal:
                    NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                else:
                    NewColor = [0, 0, 0]
                    for i in range (0, 3):
                        NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                    NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                color = NewPaintColor

                # Below draws the rings from center, outwards.
                r = BrushWidth*.5+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord+1:
                    U=int(pixU+fill)
                    V=int(pixV+radius)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if NewPaintColor > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if NewPaintColor < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill > negcord:
                    U=int(pixU-radius+1)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord+1:
                    U=int(pixU+fill)
                    V=int(pixV-radius+1)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord+1:
                    U=int(pixU+radius)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # BrushWidth is odd, airbrush, ellipse (round).
            while radius <= int(BrushWidth*.5)+1:

                # Below resets the airbrush color as rings are draw from center, outwards.
                rFactor = abs((float(radius+1)/float(((BrushWidth+1)*.5))) * (1 - Opacity))
                if Pal:
                    NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                else:
                    NewColor = [0, 0, 0]
                    for i in range (0, 3):
                        NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                    NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                color = NewPaintColor

                # Below draws the rings from center, outwards.

                r = int(BrushWidth*.5)+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord:
                    U=int(pixU+fill)
                    V=int(pixV+radius)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if NewPaintColor > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if NewPaintColor < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill >= negcord:
                    U=int(pixU-radius)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill - 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord:
                    U=int(pixU+fill)
                    V=int(pixV-radius)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord:
                    U=int(pixU+radius)
                    V=int(pixV+fill)
                    if checkUVs(editor, U, V, skin) == 1:
                        UV = str(U) + "," + str(V)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                            OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OrgColor == 0:
                                OrgColor = 1
                            skinuvlist[UV] = [OrgColor]

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                            color = None

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                            rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                if int(NewPaintColor) > 255:
                                    NewPaintColor = NewPaintColor - 255
                                if int(NewPaintColor) < 0:
                                    NewPaintColor = NewPaintColor + 255
                            else:
                                NewColor = [0, 0, 0]
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                    if NewColor[2-i] > 255:
                                        adj = int(NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                    if NewColor[2-i] < 0:
                                        adj = int(-NewColor[2-i]/255)
                                        NewColor[2-i] = NewColor[2-i] + (255 * adj)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if Pal:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                                NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            else:
                                NewPaintColor = RGBEnd
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                    NewColor[2-i] = int(check)
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                            color = int(NewPaintColor)

                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                color = skinuvlist[UV][0]

                        if color:
                            quarkx.setpixel(texshortname, texparent, U, V, color)
                            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                                if skinuvlist.has_key(UV):
                                    del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    editor.Root.currentcomponent.currentskin = newImage
    for v in editor.layout.views:
        if v.viewmode == "tex":
            v.invalidate(1)

    if editor.layout.skinview is not None:
        skin = editor.Root.currentcomponent.currentskin
        editor.layout.skinview.background = quarkx.vect(-int(skin["Size"][0]*.5),-int(skin["Size"][1]*.5),0), 1.0, 0, 1
        editor.layout.skinview.backgroundimage = skin,
        editor.layout.skinview.repaint()



#====================================================
# Below deals with the different sections of the SkinView.
# Below deals with the different sections of the SkinView Solid paint functions.
def SkinViewSolid(mdl_editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, paintcolor, PenWidth):
    editor = mdl_editor
    newImage = skin
    texWidth, texHeight = skin["Size"]
    texWidth, texHeight = int(texWidth), int(texHeight)
    ### Saves the original color for the pixel about to be colored.
    UV = str(pixU) + "," + str(pixV)
    if not skinuvlist.has_key(UV):
        OrgColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
        if OrgColor == 0:
            OrgColor = 1
        skinuvlist[UV] = [OrgColor]

    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
        if skinuvlist.has_key(UV):
            color = skinuvlist[UV][0]
            quarkx.setpixel(texshortname, texparent, pixU, pixV, color) # Draws the center pixel, where clicked.
            del skinuvlist[UV]

    else:
        quarkx.setpixel(texshortname, texparent, pixU, pixV, paintcolor) # Draws the center pixel, where clicked.

    # For rectangle shape.
    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"] == "rectangle":
        if not PenWidth&1: # PenWidth is even, solid paint, rectangle.
            radius = 1
            while radius <= PenWidth*.5:

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius+1:
                    U=pixU+fill
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = radius-1      ### Draws left line, bottom to top.
                negradius = -radius
                while fill > negradius:
                    U=pixU-radius+1
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeighttexHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius+1     ### Draws top line, left to right.
                while fill <= radius:
                    U=pixU+fill
                    V=pixV-radius+1
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius+1     ### Draws right line, top to bottom.
                while fill <= radius:
                    U=pixU+radius
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # PenWidth is odd, solid paint, rectangle.
            radius = 1
            while radius <= int(PenWidth*.5):

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius:
                    U=pixU+fill
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = radius        ### Draws left line, bottom to top.
                negradius = -radius
                while fill >= negradius:
                    U=pixU-radius
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius       ### Draws top line, left to right.
                while fill <= radius:
                    U=pixU+fill
                    V=pixV-radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius       ### Draws right line, top to bottom.
                while fill <= radius:
                    U=pixU+radius
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    else:  # For ellipse (round) shape.
           # Formula adapted from http://www.mathopenref.com/chord.html

        if not PenWidth&1: # PenWidth is even, solid paint, ellipse (round).
            radius = 1
            while radius <= PenWidth*.5+1:
                r = PenWidth*.5+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord+1:
                    U=pixU+int(fill)
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill > negcord:
                    U=pixU-radius+1
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord+1:
                    U=pixU+int(fill)
                    V=pixV-radius+1
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord+1:
                    U=pixU+radius
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # PenWidth is odd, solid paint, ellipse (round).

            radius = 1
            while radius <= int(PenWidth*.5)+1:
                r = int(PenWidth*.5)+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord:
                    U=pixU+int(fill)
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill >= negcord:
                    U=pixU-radius
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord:
                    U=pixU+int(fill)
                    V=pixV-radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord:
                    U=pixU+radius
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        paintcolor = None
                        if skinuvlist.has_key(UV):
                            paintcolor = skinuvlist[UV][0]

                    if paintcolor:
                        quarkx.setpixel(texshortname, texparent, U, V, paintcolor)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    editor.Root.currentcomponent.currentskin = newImage

    skin = editor.Root.currentcomponent.currentskin
    editor.layout.skinview.background = quarkx.vect(-int(skin["Size"][0]*.5),-int(skin["Size"][1]*.5),0), 1.0, 0, 1
    editor.layout.skinview.backgroundimage = skin,
    editor.layout.skinview.repaint()

    for v in editor.layout.views:
        if v.viewmode == "tex":
            v.invalidate(1)


# Below deals with the different sections of the SkinView Airbrush functions.
def SkinViewAirbrush(mdl_editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, airbrushcolor, BrushWidth, StartPalette=None, EndPalette=None, PenStartColor=None, RGBStart=None, RGBEnd=None):
    editor = mdl_editor
    newImage = skin
    texWidth, texHeight = skin["Size"]
    texWidth, texHeight = int(texWidth), int(texHeight)
    radius = 1
    ### Saves the original color for the pixel about to be colored.
    UV = str(pixU) + "," + str(pixV)
    if not skinuvlist.has_key(UV):
        OrgColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
        if OrgColor == 0:
            OrgColor = 1
        skinuvlist[UV] = [OrgColor]

    ### Sections below draw the First Pixel in the Center for each as needed.
    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "2":
        if Pal:
            OldPalColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
            if OldPalColor < StartPalette:
                NewPaintColor = StartPalette
            else:
                NewPaintColor = int(OldPalColor - (Opacity*10))
            if NewPaintColor > 255:
                NewPaintColor = NewPaintColor - 255
            if NewPaintColor < 0:
                NewPaintColor = NewPaintColor + 255
        else:
            OldPixelColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
            if OldPixelColor < PenStartColor:
                NewPaintColor = PenStartColor
            else:
                NewColor = [0, 0, 0]
                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                for i in range(0, 3):
                    NewColor[2-i] = abs(int((OldPixelColor[i] - (Opacity*200))))
                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
        quarkx.setpixel(texshortname, texparent, pixU, pixV, NewPaintColor) # Draws the center pixel, where clicked.

    elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "3": ### Draws the center pixel
        if Pal:
            OldPalColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
            if (OldPalColor < StartPalette and StartPalette <= EndPalette) or (OldPalColor > StartPalette and StartPalette > EndPalette):
                OldPalColor = StartPalette
            if (OldPalColor > EndPalette and StartPalette <= EndPalette) or (OldPalColor < EndPalette and EndPalette < StartPalette):
                OldPalColor = EndPalette
            NewPaintColor = OldPalColor
        else:
            if skinuvlist.has_key(UV):
                OrgPixelColor = skinuvlist[UV][0]
                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                NewColor = [0, 0, 0]
                OldPixelColor = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                for i in range(0, 3):
                    NewColor[2-i] = abs(int((OldPixelColor[i] - (Opacity*200))))
                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
        quarkx.setpixel(texshortname, texparent, pixU, pixV, NewPaintColor) # Draws the center pixel, where clicked.

    elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
        if Pal:
            if Opacity == 0:
                Opacity = 1
            rFactor = abs((float(radius-1)/float((BrushWidth*.5)-1)) * (1 - Opacity))
        else:
            UV = str(pixU) + "," + str(pixV)
            if skinuvlist.has_key(UV):
                OrgPixelColor = skinuvlist[UV][0]
                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                quarkx.setpixel(texshortname, texparent, pixU, pixV, NewPaintColor) # Draws the center pixel, where clicked.

    elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
        OldPixelColor = quarkx.getpixel(texshortname, texparent, pixU, pixV)
        if Pal:
            rFactor = abs((float(radius-1)/float((BrushWidth*.5)-1)) * (1 - Opacity))
            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
        else:
            NewPaintColor = RGBEnd
            NewColor = [0, 0, 0]
            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
            for i in range(0, 3):
                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                NewColor[2-i] = int(check)
            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
        quarkx.setpixel(texshortname, texparent, pixU, pixV, NewPaintColor) # Draws the center pixel, where clicked.

    elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
        UV = str(pixU) + "," + str(pixV)
        if skinuvlist.has_key(UV):
            color = skinuvlist[UV][0]
            quarkx.setpixel(texshortname, texparent, pixU, pixV, color) # Draws the center pixel, where clicked.
            del skinuvlist[UV]

    else:
        quarkx.setpixel(texshortname, texparent, pixU, pixV, airbrushcolor) # Draws the center pixel, where clicked.

    # For rectangle shape
    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] == "rectangle":

        if not BrushWidth&1: # BrushWidth is even, airbrush, rectangle.
            while radius <= BrushWidth*.5:

                # Below resets the airbrush color as rings are drawn from center, outwards.
                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "0":
                    rFactor = abs((float(radius-1)/float((BrushWidth*.5)-1)) * (1 - Opacity))
                    if Pal:
                        NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                    else:
                        NewColor = [0, 0, 0]
                        for i in range (0, 3):
                            NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                        NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                    color = NewPaintColor

                # Below draws the rings from center, outwards.

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius+1:
                    U=pixU+fill
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "2":
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPalColor < StartPalette:
                                NewPaintColor = StartPalette
                            else:
                                NewPaintColor = int(OldPalColor - (Opacity*10))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPixelColor < PenStartColor:
                                NewPaintColor = PenStartColor
                            else:
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((OldPixelColor[i] - (Opacity*200))))
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "3":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if (OldPalColor < StartPalette and StartPalette <= EndPalette) or (OldPalColor > StartPalette and StartPalette > EndPalette):
                                OldPalColor = StartPalette
                            if (OldPalColor > EndPalette and StartPalette <= EndPalette) or (OldPalColor < EndPalette and EndPalette < StartPalette):
                                OldPalColor = EndPalette

                            if OldPalColor <= (StartPalette + EndPalette)*.5:
                                NewPaintColor = int((OldPalColor * (1 - rFactor)) + (EndPalette * rFactor))
                            else:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (OldPalColor * rFactor))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                        ### CURRENT CODE
                         #  if skinuvlist.has_key(UV):
                         #      OrgPixelColor = skinuvlist[UV][0]
                         #      RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                         #      NewColor = [0, 0, 0]
                         #      OldPixelColor = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                         #      for i in range(0, 3):
                         #          NewColor[2-i] = abs(int((OldPixelColor[i] - (Opacity*200))))
                         #      NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        ### New test code
                            if skinuvlist.has_key(UV):
                                du = 0.0
                                dv = 0.0
                                for i in range(num_elements):
                                    du += GetHeight(GetPixel(ClampUV(U + kernel_du[i][0], V + kernel_du[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_du[i][2]
                                for i in range(num_elements):
                                    dv += GetHeight(GetPixel(ClampUV(U + kernel_dv[i][0], V + kernel_dv[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_dv[i][2]
                                vec = quarkx.vect((-du * Opacity, -dv * Opacity, 1.0)).normalized
                                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((-vec.x, -vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1":
                                    vec = quarkx.vect((-vec.x, vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((vec.x, -vec.y, vec.z))
                                RGB = [int((vec.x + 1.0) * 127.5), int((vec.y + 1.0) * 127.5), int((vec.z + 1.0) * 127.5)]
                                NewPaintColor = quarkpy.qutils.RGBToColor(RGB)
                        ### NormalPalette test code
                         #   if skinuvlist.has_key(UV):
                         #       OrgPixelColor = skinuvlist[UV][0]
                         #       RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                         #       NewColor = 0
                         #       OldPixelColor = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                         #       for i in range(0, 3):
                         #           NewColor += OldPixelColor[i]
                         #       NewColor = int((RGB[0]+RGB[1]) * .5)
                         #       NewColor = NormalPalette[NewColor]
                         #       NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        ### NORMALMAP test code
                         #   if skinuvlist.has_key(UV):
                         #       print "----------------------"
                         #       du = 0
                         #       dv = 0
                         #       for i in range(num_elements):
                         #           du += (kernel_du[i][0] * kernel_du[i][2]) + (kernel_du[i][1] * kernel_du[i][2])
                         #       for i in range(num_elements):
                         #           dv += (kernel_dv[i][0] * kernel_dv[i][2]) + (kernel_dv[i][1] * kernel_dv[i][2])

                         #       RGB = [-du * scale, -dv * scale, 1.0]

                         #       RGB = NORMALIZE(RGB)
                         
                         #       if RGB[2] < 0.0:
                         #          RGB[2] = 0.0
                         #          RGB = NORMALIZE(RGB)
                         #       print "RGB NORMALIZE", RGB
                         #       OrgPixelColor = skinuvlist[UV][0]
                         #       NC = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                         #       print "ORGrgb", NC
                         #       print "du, dv", du, dv
                         #       NewColor = [(NC[0]*0.3)*RGB[0], (NC[1]*0.59)*RGB[1], (NC[2]*0.11)*RGB[2]] # ERRORS OUT
                         #       NewColor = [(NC[0]*0.3), (NC[1]*0.59), (NC[2]*0.11)]
                         #       print "NewColor", NewColor
                         #       print "CONVERT1", abs(int(NewColor[0])), abs(int(NewColor[1])), abs(int(NewColor[2]))
                              #  NewColor = [NC[0]*RGB[0], NC[1]*RGB[1], NC[2]*RGB[2]]
                              #  print "RGB2", NewColor
                              #  print "CONVERT2", abs(int(NewColor[0])), abs(int(NewColor[1])), abs(int(NewColor[2]))
                         #       NewColor = abs(int(NewColor[0])) + abs(int(NewColor[1]))
                         #       print "NewColor CONV", NewColor
                         #       NewColor = NormalPalette[NewColor]
                         #       print "NewColor", NewColor
                         #       NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = radius-1      ### Draws left line, bottom to top.
                negradius = -radius
                while fill > negradius+1:
                    U=pixU-radius+1
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "2":
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPalColor < StartPalette:
                                NewPaintColor = StartPalette
                            else:
                                NewPaintColor = int(OldPalColor - (Opacity*10))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPixelColor < PenStartColor:
                                NewPaintColor = PenStartColor
                            else:
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((OldPixelColor[i] - (Opacity*200))))
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "3":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if (OldPalColor < StartPalette and StartPalette <= EndPalette) or (OldPalColor > StartPalette and StartPalette > EndPalette):
                                OldPalColor = StartPalette
                            if (OldPalColor > EndPalette and StartPalette <= EndPalette) or (OldPalColor < EndPalette and EndPalette < StartPalette):
                                OldPalColor = EndPalette

                            if OldPalColor > (StartPalette + EndPalette)*.5:
                                NewPaintColor = int((EndPalette * (1 - rFactor)) + (StartPalette * rFactor))
                            else:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))

                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            if skinuvlist.has_key(UV):
                                du = 0
                                dv = 0
                                for i in range(num_elements):
                                    du += GetHeight(GetPixel(ClampUV(U + kernel_du[i][0], V + kernel_du[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_du[i][2]
                                for i in range(num_elements):
                                    dv += GetHeight(GetPixel(ClampUV(U + kernel_dv[i][0], V + kernel_dv[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_dv[i][2]
                                vec = quarkx.vect((-du * Opacity, -dv * Opacity, 1.0)).normalized
                                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((-vec.x, -vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1":
                                    vec = quarkx.vect((-vec.x, vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((vec.x, -vec.y, vec.z))
                                RGB = [int((vec.x + 1.0) * 127.5), int((vec.y + 1.0) * 127.5), int((vec.z + 1.0) * 127.5)]
                                NewPaintColor = quarkpy.qutils.RGBToColor(RGB)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius+1     ### Draws top line, left to right.
                while fill < radius:
                    U=pixU+fill
                    V=pixV-radius+1
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "2":
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPalColor < StartPalette:
                                NewPaintColor = StartPalette
                            else:
                                NewPaintColor = int(OldPalColor - (Opacity*10))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPixelColor < PenStartColor:
                                NewPaintColor = PenStartColor
                            else:
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((OldPixelColor[i] - (Opacity*200))))
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "3":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if (OldPalColor < StartPalette and StartPalette <= EndPalette) or (OldPalColor > StartPalette and StartPalette > EndPalette):
                                OldPalColor = StartPalette
                            if (OldPalColor > EndPalette and StartPalette <= EndPalette) or (OldPalColor < EndPalette and EndPalette < StartPalette):
                                OldPalColor = EndPalette

                            if OldPalColor <= (StartPalette + EndPalette)*.5:
                                NewPaintColor = int((OldPalColor * (1 - rFactor)) + (EndPalette * rFactor))
                            else:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (OldPalColor * rFactor))

                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            if skinuvlist.has_key(UV):
                                du = 0
                                dv = 0
                                for i in range(num_elements):
                                    du += GetHeight(GetPixel(ClampUV(U + kernel_du[i][0], V + kernel_du[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_du[i][2]
                                for i in range(num_elements):
                                    dv += GetHeight(GetPixel(ClampUV(U + kernel_dv[i][0], V + kernel_dv[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_dv[i][2]
                                vec = quarkx.vect((-du * Opacity, -dv * Opacity, 1.0)).normalized
                                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((-vec.x, -vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1":
                                    vec = quarkx.vect((-vec.x, vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((vec.x, -vec.y, vec.z))
                                RGB = [int((vec.x + 1.0) * 127.5), int((vec.y + 1.0) * 127.5), int((vec.z + 1.0) * 127.5)]
                                NewPaintColor = quarkpy.qutils.RGBToColor(RGB)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius+1     ### Draws right line, top to bottom.
                while fill < radius:
                    U=pixU+radius
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "2":
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPalColor < StartPalette:
                                NewPaintColor = StartPalette
                            else:
                                NewPaintColor = int(OldPalColor - (Opacity*10))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if OldPixelColor < PenStartColor:
                                NewPaintColor = PenStartColor
                            else:
                                NewColor = [0, 0, 0]
                                OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                                for i in range(0, 3):
                                    NewColor[2-i] = abs(int((OldPixelColor[i] - (Opacity*200))))
                                NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "3":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            OldPalColor = quarkx.getpixel(texshortname, texparent, U, V)
                            if (OldPalColor < StartPalette and StartPalette <= EndPalette) or (OldPalColor > StartPalette and StartPalette > EndPalette):
                                OldPalColor = StartPalette
                            if (OldPalColor > EndPalette and StartPalette <= EndPalette) or (OldPalColor < EndPalette and EndPalette < StartPalette):
                                OldPalColor = EndPalette

                            if OldPalColor > (StartPalette + EndPalette)*.5:
                                NewPaintColor = int((StartPalette * (1 - rFactor)) + (OldPalColor * rFactor))
                            else:
                                NewPaintColor = int((OldPalColor * (1 - rFactor)) + (EndPalette * rFactor))

                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            if skinuvlist.has_key(UV):
                                du = 0
                                dv = 0
                                for i in range(num_elements):
                                    du += GetHeight(GetPixel(ClampUV(U + kernel_du[i][0], V + kernel_du[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_du[i][2]
                                for i in range(num_elements):
                                    dv += GetHeight(GetPixel(ClampUV(U + kernel_dv[i][0], V + kernel_dv[i][1], texWidth, texHeight), texshortname, texparent, skinuvlist)) * kernel_dv[i][2]
                                vec = quarkx.vect((-du * Opacity, -dv * Opacity, 1.0)).normalized
                                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((-vec.x, -vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] == "1":
                                    vec = quarkx.vect((-vec.x, vec.y, vec.z))
                                elif quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] == "1":
                                    vec = quarkx.vect((vec.x, -vec.y, vec.z))
                                RGB = [int((vec.x + 1.0) * 127.5), int((vec.y + 1.0) * 127.5), int((vec.z + 1.0) * 127.5)]
                                NewPaintColor = quarkpy.qutils.RGBToColor(RGB)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # BrushWidth is odd, airbrush, rectangle.
            while radius <= int(BrushWidth*.5):

                # Below resets the airbrush color as rings are draw from center, outwards.
                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "0":
                    rFactor = abs((float(radius+1)/float(((BrushWidth+1)*.5))) * (1 - Opacity))
                    if Pal:
                        NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                    else:
                        NewColor = [0, 0, 0]
                        for i in range (0, 3):
                            NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                        NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                    color = NewPaintColor

                # Below draws the rings from center, outwards.

                fill = radius        ### Draws bottom line, right to left.
                negradius = -radius
                while fill >= negradius:
                    U=pixU+fill
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = radius        ### Draws left line, bottom to top.
                negradius = -radius
                while fill >= negradius:
                    U=pixU-radius
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = -radius       ### Draws top line, left to right.
                while fill <= radius:
                    U=pixU+fill
                    V=pixV-radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = -radius       ### Draws right line, top to bottom.
                while fill <= radius:
                    U=pixU+radius
                    V=pixV+fill
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    else:  # For airbrush, ellipse (round) shape.
           # Formula adapted from http://www.mathopenref.com/chord.html

        if not BrushWidth&1: # BrushWidth is even, airbrush, ellipse (round).
            while radius <= BrushWidth*.5+1:

                # Below resets the airbrush color as rings are draw from center, outwards.
                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "0":
                    rFactor = abs((float(radius-1)/float((BrushWidth*.5)-1)) * (1 - Opacity))
                    if Pal:
                        NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                    else:
                        NewColor = [0, 0, 0]
                        for i in range (0, 3):
                            NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                        NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                    color = NewPaintColor

                # Below draws the rings from center, outwards.
                r = BrushWidth*.5+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord+1:
                    U=pixU+int(fill)
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill > negcord:
                    U=pixU-radius+1
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord+1:
                    U=pixU+int(fill)
                    V=pixV-radius+1
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = ((round(cord*.5 - .5)-1)*-1)+1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord+1:
                    U=pixU+radius
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

        else: # BrushWidth is odd, airbrush, ellipse (round).
            while radius <= int(BrushWidth*.5)+1:

                # Below resets the airbrush color as rings are draw from center, outwards.
                if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "0":
                    rFactor = abs((float(radius+1)/float(((BrushWidth+1)*.5))) * (1 - Opacity))
                    if Pal:
                        NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                    else:
                        NewColor = [0, 0, 0]
                        for i in range (0, 3):
                            NewColor[2-i] = int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor))
                        NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                    color = NewPaintColor

                # Below draws the rings from center, outwards.
                r = int(BrushWidth*.5)+1
                d = radius
                cord = math.sqrt((r*r)-(d*d)) * 2

                fill = round(cord*.5 - .5)-1  ### Draws bottom line, right to left.
                negcord = -fill
                while fill >= negcord:
                    U=pixU+int(fill)
                    V=pixV+radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if NewPaintColor > 255:
                                NewPaintColor = NewPaintColor - 255
                            if NewPaintColor < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = round(cord*.5 - .5)-1  ### Draws left line, bottom to top.
                while fill >= negcord:
                    U=pixU-radius
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(radius-fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill - 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill - 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill - 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws top line, left to right.
                negcord = -fill
                while fill <= negcord:
                    U=pixU+int(fill)
                    V=pixV-radius
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1

                fill = (round(cord*.5 - .5)-1)*-1  ### Draws right line, top to bottom.
                negcord = -fill
                while fill <= negcord:
                    U=pixU+radius
                    V=pixV+int(fill)
                    if U > texWidth - 1:
                        U = U - texWidth
                    if U < 0:
                        U = U + texWidth
                    if V > texHeight - 1:
                        V = V - texHeight
                    if V < 0:
                        V = V + texHeight
                    UV = str(U) + "," + str(V)
                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "6" and not skinuvlist.has_key(UV):
                        OrgColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if OrgColor == 0:
                            OrgColor = 1
                        skinuvlist[UV] = [OrgColor]

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != "0":
                        color = None

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "1":
                        rFactor = abs((float(fill)/float(radius)) * (1 - Opacity))
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            if int(NewPaintColor) > 255:
                                NewPaintColor = NewPaintColor - 255
                            if int(NewPaintColor) < 0:
                                NewPaintColor = NewPaintColor + 255
                        else:
                            NewColor = [0, 0, 0]
                            for i in range(0, 3):
                                NewColor[2-i] = abs(int((RGBStart[i] * (1 - rFactor)) + (RGBEnd[i] * rFactor)))
                                if NewColor[2-i] > 255:
                                    adj = int(NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] - (255 * adj)
                                if NewColor[2-i] < 0:
                                    adj = int(-NewColor[2-i]/255)
                                    NewColor[2-i] = NewColor[2-i] + (255 * adj)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "4":
                        if Pal:
                            if U == pixU and V == pixV:
                                fill = fill + 1
                                continue
                            OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                            color = int(NewPaintColor)
                        else:
                            if skinuvlist.has_key(UV):
                                OrgPixelColor = skinuvlist[UV][0]
                                RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
                                NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
                                NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
                                color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "5":
                        if U == pixU and V == pixV:
                            fill = fill + 1
                            continue
                        OldPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
                        if Pal:
                            NewPaintColor = int((StartPalette * (1 - rFactor)) + (EndPalette * rFactor))
                            NewPaintColor = (NewPaintColor * Opacity) + (OldPixelColor * (1 - Opacity))
                        else:
                            NewPaintColor = RGBEnd
                            NewColor = [0, 0, 0]
                            OldPixelColor = quarkpy.qutils.ColorToRGB(OldPixelColor)
                            for i in range(0, 3):
                                check = NewPaintColor[i] * (Opacity*.1) + (OldPixelColor[i] * (1-(Opacity*.1)))
                                NewColor[2-i] = int(check)
                            NewPaintColor = quarkpy.qutils.RGBToColor(NewColor)
                        color = int(NewPaintColor)

                    if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                        if skinuvlist.has_key(UV):
                            color = skinuvlist[UV][0]

                    if color:
                        quarkx.setpixel(texshortname, texparent, U, V, color)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] == "6":
                            if skinuvlist.has_key(UV):
                                del skinuvlist[UV]

                    fill = fill + 1
                radius = radius + 1

    editor.Root.currentcomponent.currentskin = newImage

    skin = editor.Root.currentcomponent.currentskin
    editor.layout.skinview.background = quarkx.vect(-int(skin["Size"][0]*.5),-int(skin["Size"][1]*.5),0), 1.0, 0, 1
    editor.layout.skinview.backgroundimage = skin,
    editor.layout.skinview.repaint()

    for v in editor.layout.views:
        if v.viewmode == "tex":
            v.invalidate(1)



#====================================================
# Below deals with the different sections of the PaintManager.
# Handles all textured views of the editor.
def TexViews(mdl_editor, view, x, y, flagsmouse, skin, Pal, skinuvlist, pixelpositions, tb2, Opacity):
    editor = mdl_editor
    texshortname = skin.shortname
    texparent = skin.parent
    StartPalette = EndPalette = RGBStart = RGBEnd = None

    # Sets what color sources are available based on texture image file type.
    if Pal: # 8 bit textures
        paintcolor = airbrushcolor = StartPalette = int(quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"])
        EndPalette = int(quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"])
    else: # 24 bit textures
        paintcolor = airbrushcolor = PenStartColor = MapColor("Paint_RGBPenColor", SS_MODEL)
        PenEndColor = MapColor("Paint_RGBBrushColor", SS_MODEL)
        if (paintcolor < 0) or (airbrushcolor < 0) or (PenStartColor < 0) or (PenEndColor < 0):
            quarkx.msgbox("You have an improper 'Black'\nRGB color selection.\n\nReselect your 'Black' color\nfrom the top color panel section.", MT_ERROR, MB_OK)
            return
        RGBStart = quarkpy.qutils.ColorToRGB(PenStartColor)
        RGBEnd = quarkpy.qutils.ColorToRGB(PenEndColor)

    pixU, pixV = pixelpositions[0]
    if checkUVs(editor, pixU, pixV, skin) == 0:
        return

    # Paints a single solid color in one of the editor's textured views, Skin-view repaints to show changes.
    if tb2.tb.buttons[1].state == 2:
        PenWidth = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"])
        TexViewSolid(mdl_editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, paintcolor, PenWidth)

    # Paints an airbrush effect using selected Start and End colors and changes\spreads the color
    # as the "radius" increases, from center to outer ring, based on the "Airbrush" width setting.
    if tb2.tb.buttons[2].state == 2:
        BrushWidth = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"])
        TexViewAirbrush(mdl_editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, airbrushcolor, BrushWidth, StartPalette, EndPalette, RGBStart, RGBEnd)

    # This button paint area is setup for patterns but not being used yet.
    if tb2.tb.buttons[3].state == 2:
        cv = view.canvas()
        cv.penwidth = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"])
        spray = 0
        cv.pencolor = cv.brushcolor = cv.getpixel(x,y) # Gets the color from the view.
        brushwidth = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"])
        cv.brushstyle = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"])
        while spray != brushwidth:
            cv.pencolor = cv.pencolor + (2 * spray) # Make colorspread amount variable
            if quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] == "rectangle":
                cv.rectangle(x-(3 * spray),y-(3 * spray),x+(3 * spray),y+(3 * spray)) # Make fanspray amount variable
            else:
                cv.ellipse(x-(3 * spray),y-(3 * spray),x+(3 * spray),y+(3 * spray)) # Make fanspray amount variable
            spray = spray + 1 # Make interval amount variable


# Handles the Skin-view.
def SkinView(mdl_editor, view, x, y, flagsmouse, skin, Pal, skinuvlist, pixU, pixV, tb2, Opacity):
    editor = mdl_editor
    texshortname = skin.shortname
    texparent = skin.parent
    StartPalette = EndPalette = PenStartColor = RGBStart = RGBEnd = None

    # Line below skips painting pixels based on setting for map grid
    # Might be able to use for opacity look of colors or airbrushing.
    #  list = map(quarkx.ftos, editor.aligntogrid(view.space(quarkx.vect(x, y, 0))).tuple + editor.aligntogrid(view.space(quarkx.vect(x, y, 0))).tuple)

    # Sets what color sources are available based on texture image file type.
    if Pal: # 8 bit textures
        paintcolor = airbrushcolor = StartPalette = int(quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"])
        EndPalette = int(quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"])
    else: # 24 bit textures
        paintcolor = airbrushcolor = PenStartColor = MapColor("Paint_RGBPenColor", SS_MODEL)
        PenEndColor = MapColor("Paint_RGBBrushColor", SS_MODEL)
        if (paintcolor < 0) or (airbrushcolor < 0) or (PenStartColor < 0) or (PenEndColor < 0):
            quarkx.msgbox("You have an improper 'Black'\nRGB color selection.\n\nReselect your 'Black' color\nfrom the top color panel section.", MT_ERROR, MB_OK)
            return
        RGBStart = quarkpy.qutils.ColorToRGB(PenStartColor)
        RGBEnd = quarkpy.qutils.ColorToRGB(PenEndColor)

    # Paints a single solid color in the Skin-view, editor's textured views repaints to show changes.
    if tb2.tb.buttons[1].state == 2:
        PenWidth = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"])
        SkinViewSolid(editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, paintcolor, PenWidth)

    # Paints an airbrush effect using selected Start and End colors and changes\spreads the color
    # as the "radius" increases, from center to outer ring, based on the "Airbrush" width setting.
    if tb2.tb.buttons[2].state == 2:
        BrushWidth = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"])
        SkinViewAirbrush(editor, skin, Pal, skinuvlist, Opacity, texshortname, texparent, pixU, pixV, airbrushcolor, BrushWidth, StartPalette, EndPalette, PenStartColor, RGBStart, RGBEnd)


#====================================================
# Below deals with the PaintManager to pass mouse actions
# to specific buttons that deal with the actual painting functions.
def PaintManager(editor, view, x, y, flagsmouse, modelfacelist):

    paintcursor(editor)
    if editor.Root.currentcomponent is None or editor.Root.currentcomponent.currentskin is None:
        return

    comp = editor.Root.currentcomponent
    comp_name = comp.name
    skin = comp.currentskin
    if skin.shortname is None or skin.parent is None:
        return

    skin_name = skin.name
    Pal = None
    if skin['Pal']:
        Pal = skin['Pal']

    if not editor.ModelComponentList[comp_name].has_key("paintuvlist"):
        editor.ModelComponentList[comp_name]['paintuvlist'] = {}
    paintuvlist = editor.ModelComponentList[comp_name]['paintuvlist']
    if not paintuvlist.has_key(skin_name):
        paintuvlist[skin_name] = {}
    skinuvlist = paintuvlist[skin_name]
    skinuvlistcount = len(skinuvlist)
    # Clears Eraser image list when max setting is reached to minimize operation slowdown.
    if skinuvlistcount > int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_EraserSize"]):
        paintuvlist[skin_name] = {}
        skinuvlist = paintuvlist[skin_name]

    if view.info["viewname"] != "skinview":
        if view.viewmode != "tex":
            return
        paintobject = []
        itemcount = 0
        for item in range(len(modelfacelist)):
            if modelfacelist[item][1].name == editor.Root.currentcomponent.name:
                itemcount = itemcount + 1
                paintobject = [modelfacelist[item]]
                # causes face underneith to be painted
                if itemcount == int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"]):
                    break
        if paintobject == []:
            return

    tb2 = editor.layout.toolbars["tb_paintmodes"]
    if tb2.tb.buttons[1].state == 2 or tb2.tb.buttons[2].state == 2 or tb2.tb.buttons[3].state == 2: # The Solid Paint and Airbrush Paint mode buttons
        import quarkpy.qutils
        Opacity = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"])*.01

        if view.info["viewname"] != "skinview":
            if paintobject != [] and (flagsmouse == 552 or flagsmouse == 1064):
                pixelpositions = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y, paintobject)
                TexViews(editor, view, x, y, flagsmouse, skin, Pal, skinuvlist, pixelpositions, tb2, Opacity)

              ### This section is for strictly painting in the Skin-view
        else: ### and passes to the editor's textured views when invalidated.
            if flagsmouse == 552 or flagsmouse == 1064:
                pixU, pixV = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y)
                SkinView(editor, view, x, y, flagsmouse, skin, Pal, skinuvlist, pixU, pixV, tb2, Opacity)


class SelectColors(quarkpy.dlgclasses.LiveEditDlg):
    "To open the Color Selection Dialog."

    dlgflags = FWF_KEEPFOCUS | FWF_NORESIZE # Keeps dialog box open & a fixed size.
    size = (250,470)
    dfsep = 0.35    # sets 35% for labels and the rest for edit boxes
    dlgdef = """
    {
        Style = "13"
        Caption = "Color Selector & Paint Settings"

        SkinName: =
        {
        typ   = "E R"
        Txt = "current skin"
        Hint[]= "Skin being painted"
        }

        sep: = { Typ="S" Txt=" "}

        ReachThrough: =
        {
        Txt = "reach through"
        Typ = "EU"
        Hint = "Paints or Color Picks"$0D"this many faces down"
        Min="0.0"
        }

        EraserSize: =
        {
        Txt = "eraser size"
        Typ = "EU"
        Hint = "Eraser stores original image colors by pixel."$0D"The more it stores can slow down response time."$0D"Set max size here, min = 500 pixels (default)."$0D"To use eraser set 'Airbrush: Spray Style' to 'ERASER TOOL'"$0D"to repaint the original image pixel colors."
        Min="500.0"
        }

        sep: = { Typ="S" Txt=""}
        sep: = { Typ="S" Txt="Solid:"}

        PalettePenColor: =
        {
        Txt = "Palette color"
        Typ   = "LP"
        Hint[]= "view [::Game] palette"$0D"& Airbrush Begin Color"
        }

        RGBPenColor: =
        {
        Txt = "RGB color"
        Typ = "LI"
        Hint = "RGB color for 24 bit skins"$0D"& Airbrush Begin Color"
        }

        PenWidth: =
        {
        Txt = "Brush Width"
        Typ = "EU"
        Hint = "Width of the color"
        Min="1.0"
        }

        PaintShape: =
        {
        Txt = "Brush Shape"
        Typ = "C"
        Hint = "Paint brush shape to use"
        items =
            "CIRCULAR" $0D
            "RECTANGLE"
        values =
            "ellipse" $0D
            "rectangle"
        }

        sep: = { Typ="S" Txt=""}
        sep: = { Typ="S" Txt="Airbrush:"}

        PaletteBrushColor: =
        {
        Txt = "Palette color"
        Typ   = "LP"
        Hint[]= "view [::Game] palette"$0D"& Airbrush End Color"
        }

        RGBBrushColor: =
        {
        Txt = "RGB color"
        Typ = "LI"
        Hint = "RGB color for 24 bit skins"$0D"& Airbrush End Color"
        }

        BrushWidth: =
        {
        Txt = "Spray Width"
        Typ = "EU"
        Hint = "Width of the color"
        Min="1.0"
        }

        SprayShape: =
        {
        Txt = "Spray Shape"
        Typ = "C"
        Hint = "Airbrush shape to use"
        items =
            "CIRCULAR" $0D
            "RECTANGLE"
        values =
            "ellipse" $0D
            "rectangle"
        }

        BrushStyle: =
        {
        Txt = "Spray Style"
        Typ = "C"
        Hint = "Spray style to use"
        items =
            "RING PATTERN" $0D
            "RANDOM PATTERN" $0D
            "TWO COLOR BLEND" $0D
            "NORMAL MAP-blue scale" $0D
            "HEIGHT MAP-gray scale" $0D
            "AIRBRUSH BLENDING" $0D
            "ERASER TOOL"
        values =
            "0" $0D
            "1" $0D
            "2" $0D
            "3" $0D
            "4" $0D
            "5" $0D
            "6"
        }

        InvertX: =
        {
        Txt = "Invert X"
        Typ = "X1"
        Hint = "blue scale default = unchecked"
        }

        InvertY: =
        {
        Txt = "Invert Y"
        Typ = "X1"
        Hint = "blue scale default = checked"
        }

        buttons: = {
        Txt = "One-click:"
        Typ = "PM"
        Hint = "Click a button to effect the entire image."
        Num = "3"
        Macro = "oneclick"
        Caps = "BGR"
        Hint1 = "Make NORMAL MAP-blue scale"
        Hint2 = "Make HEIGHT MAP-gray scale"
        Hint3 = "Restore original image"
        }

        Opacity: =
        {
        Txt = "Opacity %"
        Typ = "EU"
        Hint = "Percentage of Opacity 0-100"$0D"blue scale default = 10"$0D"gray scale default = 50"
        }

        sep: = { Typ="S" Txt=""}

        Reset: =       // Reset button
        {
          Cap = "defaults"      // button caption
          Typ = "B"                     // "B"utton
          Hint = "Resets all items to"$0D"their default settings"
          Delete: =
          {            // the button resets to these amounts
            ReachThrough = "0"
            EraserSize = "16000"
            PalettePenColor = "254"
            RGBPenColor = $9C8370
            PenWidth = "2"
            PaintShape = "ellipse"
            PaletteBrushColor = "254"
            RGBBrushColor = $9C8370
            BrushWidth = "6"
            SprayShape = "ellipse"
            BrushStyle = "0"
            InvertX = "0"
            InvertY = "1"
            Opacity = "0"
          }
        }

        exit:py = {Txt="Close" }
    }
    """

# Define the oneclick macro here, put the definition into
#  quarkpy.qmacro, which is where macros called from delphi live.
def macro_oneclick(self, index=0):
    editor = mapeditor()
    if editor is None: return
    image = editor.Root.currentcomponent.currentskin
    if image['Pal']:
        quarkx.msgbox("Invalid Action !\n\nSelected texture is 8 bit\nand has its own pallet.\n\nThese functions can not be used.", MT_ERROR, MB_OK)
        return
    if index == 1:
        BlueScale(editor, image)
    elif index == 2:
        GrayScale(editor, image)
    elif index == 3:
        Restore(editor, image)

qmacro.MACRO_oneclick = macro_oneclick

#
# We're going to trigger these actions both by menu
#  items and buttons in a dialog, so we define them
#  independently of the UI elements that call them.
#
save_image = None
def BlueScale(editor, image):
    global save_image
    if save_image is None:
        save_image = image.copy()
        save_image['Image1'] = image.dictspec['Image1']
    InvertX = quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"]
    InvertY = quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"]
    Opacity = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"]) * .01
    texWidth, texHeight = image["Size"]
    texWidth, texHeight = int(texWidth), int(texHeight)
    texshortname = image.shortname
    texparent = image.parent

    time = texWidth * texHeight * .0006294
    mins = time/60
    secs = int(round(60 * (mins - int(mins))))
    save_string = Strings[2462]
    Strings[2462] = "Total process time: " + str(int(mins)) + " mins. " + str(secs) + " secs."
    count = (texWidth * texHeight) * 3
    progressbar = quarkx.progressbar(2462, count)

    # Store the 'old' data; faster than retrieving it all the time
    old_data = [[]] * texWidth
    for U in xrange(texWidth):
        progressbar.progress()
        old_data[U] = [[]] * texHeight
        for V in xrange(texHeight):
            old_data[U][V] = quarkpy.qutils.ColorToRGB(quarkx.getpixel(texshortname, texparent, U, V))
            progressbar.progress()

    # new_data will contain the new image pixels data.
    new_data = [[]] * texWidth
    for U in xrange(texWidth):
        progressbar.progress()
        new_data[U] = [[]] * texHeight
        for V in xrange(texHeight):
            du = 0.0
            dv = 0.0
            for i in range(num_elements):
                U2, V2 = ClampUV(U + kernel_du[i][0], V + kernel_du[i][1], texWidth, texHeight)
                du += GetHeight(old_data[U2][V2]) * kernel_du[i][2]
            for i in range(num_elements):
                U2, V2 = ClampUV(U + kernel_dv[i][0], V + kernel_dv[i][1], texWidth, texHeight)
                dv += GetHeight(old_data[U2][V2]) * kernel_dv[i][2]
            vec = NORMALIZE([-du * Opacity, -dv * Opacity, 1.0])
            if InvertX == "1" and InvertY == "1":
                vec = (-vec[0], -vec[1], vec[2])
            elif InvertX == "1":
                vec = (-vec[0], vec[1], vec[2])
            elif InvertY == "1":
                vec = (vec[0], -vec[1], vec[2])
            RGB = [int((vec[0] + 1.0) * 127.5), int((vec[1] + 1.0) * 127.5), int((vec[2] + 1.0) * 127.5)]
            new_data[U][V] = int(quarkpy.qutils.RGBToColor(RGB))
            progressbar.progress()

    # Finally set the new image pixels.
    for U in xrange(texWidth):
        progressbar.progress()
        for V in xrange(texHeight):
            quarkx.setpixel(texshortname, texparent, U, V, new_data[U][V])
            progressbar.progress()

    Strings[2462] = save_string
    progressbar.close()
    editor.Root.currentcomponent.currentskin = image
    editor.layout.skinview.repaint()
    for v in editor.layout.views:
        if v.viewmode == "tex":
            v.invalidate(1)


def GrayScale(editor, image):
    global save_image
    if save_image is None:
        save_image = image.copy()
        save_image['Image1'] = image.dictspec['Image1']
    Opacity = int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"]) * .01
    texWidth, texHeight = image["Size"]
    texWidth, texHeight = int(texWidth), int(texHeight)
    texshortname = image.shortname
    texparent = image.parent

    secs = int(round((texWidth * texHeight) / 17500))
    save_string = Strings[2462]
    Strings[2462] = "Total process time: " + str(secs) + " secs."
    count = texWidth * texHeight
    progressbar = quarkx.progressbar(2462, count)

    for V in xrange(texHeight):
        for U in xrange(texWidth):
            OrgPixelColor = quarkx.getpixel(texshortname, texparent, U, V)
            RGB = quarkpy.qutils.ColorToRGB(OrgPixelColor)
            NEW = int(0.2989 * RGB[0] * Opacity*2 + 0.5870 * RGB[1] * Opacity*2 + 0.1140 * RGB[2])
            if NEW < 0:
                NEW = 0
            if NEW > 255:
                NEW = 255
            NewPaintColor = quarkpy.qutils.RGBToColor((NEW, NEW, NEW))
            quarkx.setpixel(texshortname, texparent, U, V, NewPaintColor)
            progressbar.progress()

    Strings[2462] = save_string
    progressbar.close()
    editor.Root.currentcomponent.currentskin = image
    editor.layout.skinview.repaint()
    for v in editor.layout.views:
        if v.viewmode == "tex":
            v.invalidate(1)


def Restore(editor, image):
    global save_image
    if save_image is not None:
        image['Image1'] = save_image.dictspec['Image1']
        editor.Root.currentcomponent.currentskin = image
        editor.layout.skinview.background = quarkx.vect(-int(image["Size"][0]*.5),-int(image["Size"][1]*.5),0), 1.0, 0, 1
        editor.layout.skinview.backgroundimage = image,
        save_image = None
        editor.layout.skinview.repaint()
        for v in editor.layout.views:
            if v.viewmode == "tex":
                v.invalidate(1)


#====================================================
# Below deals with the PaintManager to pass mouse actions to specific buttons

def ColorSelectorClick(m):
    editor = mapeditor()
    if editor is None: return

    def setup(self):
        editor.findtargetdlg = self
        self.editor = editor
        src = self.src

      ### To populate settings...

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"] is None):
            src["ReachThrough"] = "0"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"] = src["ReachThrough"]
        else:
            src["ReachThrough"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_EraserSize"] is None):
            src["EraserSize"] = "16000"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_EraserSize"] = src["EraserSize"]
        else:
            src["EraserSize"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_EraserSize"]

        if (quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"] is None):
            src["PalettePenColor"] = "254"
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"] = src["PalettePenColor"]
        else:
            src["PalettePenColor"] = quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"]

        if (quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"] is None):
            src["RGBPenColor"] = "$9C8370"
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"] = src["RGBPenColor"]
        else:
            src["RGBPenColor"] = quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"] is None):
            src["PenWidth"] = "2"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"] = src["PenWidth"]
        else:
            src["PenWidth"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"] is None):
            src["PaintShape"] = "ellipse"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"] = src["PaintShape"]
        else:
            src["PaintShape"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"]

        if (quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"] is None):
            src["PaletteBrushColor"] = "254"
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"] = src["PaletteBrushColor"]
        else:
            src["PaletteBrushColor"] = quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"]

        if (quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"] is None):
            src["RGBBrushColor"] = "$9C8370"
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"] = src["RGBBrushColor"]
        else:
            src["RGBBrushColor"] = quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"] is None):
            src["BrushWidth"] = "6"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"] = src["BrushWidth"]
        else:
            src["BrushWidth"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] is None):
            src["SprayShape"] = "ellipse"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] = src["SprayShape"]
        else:
            src["SprayShape"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] is None):
            src["BrushStyle"] = "0"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] = src["BrushStyle"]
        else:
            src["BrushStyle"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] is None):
            src["InvertX"] = "0"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] = src["InvertX"]
        else:
            src["InvertX"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] is None):
            src["InvertY"] = "1"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] = src["InvertY"]
        else:
            src["InvertY"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"]

        if (quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"] is None):
            src["Opacity"] = "0"
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"] = src["Opacity"]
        else:
            src["Opacity"] = quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"]

      ### To define dialog variables and default settings.
        if editor.Root.currentcomponent.currentskin is None:
            src["SkinName"] = "no skins exist for this component"
        else:
            src["SkinName"] = editor.Root.currentcomponent.currentskin.name

        if src["ReachThrough"]:
            try:
                if not int(src["ReachThrough"]):
                    pass
            except:
                quarkx.msgbox("Invalid Entry !\n\nMust be value\nof 0 or higher.\n\nReset to Default.", MT_ERROR, MB_OK)
                src["ReachThrough"] = "0"
                return
            if int(float(src["ReachThrough"])) < 0:
                src["ReachThrough"] = "0"
            else:
                src["ReachThrough"] = str(int(float(src["ReachThrough"])))
            ReachThrough = src["ReachThrough"]
        else:
            Reachthrough = "0"

        if src["EraserSize"]:
            try:
                if not int(src["EraserSize"]):
                    pass
            except:
                quarkx.msgbox("Invalid Entry !\n\nMust be value\nof 500 or higher.\n\nReset to Default.", MT_ERROR, MB_OK)
                src["EraserSize"] = "16000"
                return
            if int(float(src["EraserSize"])) < 500:
                src["EraserSize"] = "500"
            else:
                src["EraserSize"] = str(int(float(src["EraserSize"])))
            EraserSize = src["EraserSize"]
        else:
            EraserSize = "500"

        if src["PalettePenColor"]:
            PALpencolor = src["PalettePenColor"]
        else:
            PALpencolor = "254"

        if src["RGBPenColor"]:
            RGBpencolor = src["RGBPenColor"]
        else:
            RGBpencolor = "$9C8370"

        if src["PenWidth"]:
            try:
                if not int(src["PenWidth"]):
                    pass
            except:
                quarkx.msgbox("Invalid Entry !\n\nMust be value\nof 1 or higher.\n\nReset to Default.", MT_ERROR, MB_OK)
                src["PenWidth"] = "2"
                return
            if int(float(src["PenWidth"])) < 1:
                src["PenWidth"] = "1"
            else:
                src["PenWidth"] = str(int(float(src["PenWidth"])))
            Penwidth = src["PenWidth"]
        else:
            Penwidth = "2"

        if src["PaintShape"]:
            Paintshape = src["PaintShape"]
        else:
            Paintshape = "ellipse"

        if src["PaletteBrushColor"]:
            PALbrushcolor = src["PaletteBrushColor"]
        else:
            PALbrushcolor = "254"

        if src["RGBBrushColor"]:
            RGBbrushcolor = src["RGBBrushColor"]
        else:
            RGBbrushcolor = "$9C8370"

        if src["BrushWidth"]:
            try:
                if not int(src["BrushWidth"]):
                    pass
            except:
                quarkx.msgbox("Invalid Entry !\n\nMust be value\nof 1 or higher.\n\nReset to Default.", MT_ERROR, MB_OK)
                src["BrushWidth"] = "6"
                return
            if int(float(src["BrushWidth"])) < 1:
                src["BrushWidth"] = "1"
            else:
                src["BrushWidth"] = str(int(float(src["BrushWidth"])))
            Brushwidth = src["BrushWidth"]
        else:
            Brushwidth = "6"

        if src["SprayShape"]:
            Sprayshape = src["SprayShape"]
        else:
            Sprayshape = "ellipse"

        if src["BrushStyle"]:
            Brushstyle = src["BrushStyle"]
        else:
            Brushstyle = "0"

        if src["InvertX"]:
            invertX = src["InvertX"]
        else:
            invertX = "0"

        if src["InvertY"]:
            invertY = src["InvertY"]
        else:
            invertY = "0"

        if src["Opacity"]:
            try:
                if not int(src["Opacity"]):
                    pass
            except:
                quarkx.msgbox("Invalid Entry !\n\nMust be value\nfrom 0 to 100.\n\nReset to Default.", MT_ERROR, MB_OK)
                src["Opacity"] = "0"
                return
            if int(src["Opacity"]) < 0:
                src["Opacity"] = "0"

            elif int(src["Opacity"]) > 100:
                src["Opacity"] = "100"
            else:
                opacity = src["Opacity"]
        else:
            opacity = "0"


    def action(self, editor=editor):

        if (self.src["ReachThrough"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"] != None:
            Reachthrough = (self.src["ReachThrough"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"] = Reachthrough
        else:
            (self.src["ReachThrough"]) = "0"
            Reachthrough = (self.src["ReachThrough"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"] = Reachthrough

        if (self.src["EraserSize"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_EraserSize"] != None:
            EraserSize = (self.src["EraserSize"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_EraserSize"] = EraserSize
        else:
            (self.src["EraserSize"]) = "500"
            EraserSize = (self.src["EraserSize"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_EraserSize"] = EraserSize

        if (self.src["PalettePenColor"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"] != None:
            PALpencolor = (self.src["PalettePenColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"] = PALpencolor
        else:
            (self.src["PalettePenColor"]) = "254"
            PALpencolor = (self.src["PalettePenColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"] = PALpencolor

        if (self.src["RGBPenColor"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"] != None:
            RGBpencolor = (self.src["RGBPenColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"] = RGBpencolor
        else:
            (self.src["RGBPenColor"]) = "$9C8370"
            RGBpencolor = (self.src["RGBPenColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"] = RGBpencolor

        if (self.src["PenWidth"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"] != None:
            Penwidth = (self.src["PenWidth"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"] = Penwidth
        else:
            (self.src["PenWidth"]) = "2"
            Penwidth = (self.src["PenWidth"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_PenWidth"] = Penwidth

        if (self.src["PaintShape"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"] != None:
            Paintshape = (self.src["PaintShape"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"] = Paintshape
        else:
            (self.src["PaintShape"]) = "ellipse"
            Paintshape = (self.src["PaintShape"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_PaintShape"] = Paintshape

        if (self.src["PaletteBrushColor"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"] != None:
            PALbrushcolor = (self.src["PaletteBrushColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"] = PALbrushcolor
        else:
            (self.src["PaletteBrushColor"]) = "254"
            PALbrushcolor = (self.src["PaletteBrushColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"] = PALbrushcolor

        if (self.src["RGBBrushColor"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"] != None:
            RGBbrushcolor = (self.src["RGBBrushColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"] = RGBbrushcolor
        else:
            (self.src["RGBBrushColor"]) = "$9C8370"
            RGBbrushcolor = (self.src["RGBBrushColor"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"] = RGBbrushcolor

        if (self.src["BrushWidth"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"] != None:
            Brushwidth = (self.src["BrushWidth"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"] = Brushwidth
        else:
            (self.src["BrushWidth"]) = "6"
            Brushwidth = (self.src["BrushWidth"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"] = Brushwidth

        if (self.src["SprayShape"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] != None:
            Sprayshape = (self.src["SprayShape"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] = Sprayshape
        else:
            (self.src["SprayShape"]) = "ellipse"
            Sprayshape = (self.src["SprayShape"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_SprayShape"] = Sprayshape

        if (self.src["BrushStyle"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] != None:
            Brushstyle = (self.src["BrushStyle"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] = Brushstyle
        else:
            (self.src["BrushStyle"]) = "0"
            Brushstyle = (self.src["BrushWidth"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushStyle"] = Brushstyle

        if (self.src["InvertX"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] != None:
            invertX = (self.src["InvertX"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] = invertX
        else:
            (self.src["InvertX"]) = "None"
            invertX = (self.src["InvertX"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertX"] = invertX

        if (self.src["InvertY"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] != None:
            invertY = (self.src["InvertY"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] = invertY
        else:
            (self.src["InvertY"]) = "None"
            invertY = (self.src["InvertY"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_InvertY"] = invertY

        if (self.src["Opacity"]) != None and quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"] != None:
            opacity = (self.src["Opacity"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"] = opacity
        else:
            (self.src["Opacity"]) = "0"
            opacity = (self.src["Opacity"])
            quarkx.setupsubset(SS_MODEL, "Options")["Paint_Opacity"] = opacity


    def onclosing(self,editor=editor):
        try:
            del editor.findtargetdlg
        except:
            pass

    SelectColors(quarkx.clickform, 'selectcolors', editor, setup, action, onclosing)


def ColorPicker(editor, view, x, y, flagsmouse, modelfacelist):
    "Takes the 'clickedpixel' directly from the texture to avoid view distortion"
    "and sets the color of the pen or brush currently being used."

    if view.info["viewname"] == "skinview":
        pass
    else:
        if view.viewmode != "tex" or editor.Root.currentcomponent is None:
            return

        paintobject = []
        for item in range(len(modelfacelist)):
            paintobject = [modelfacelist[item]]
            # causes color to be picked from a face underneith
            if item == int(quarkx.setupsubset(SS_MODEL, "Options")["Paint_ReachThrough"]):
                break
        if paintobject == []:
            return

        skintexture = None
        if paintobject[0][1] == editor.Root.currentcomponent:
            skintexture = editor.Root.currentcomponent.currentskin
        else:
            from quarkpy.mdlmgr import savedskins
            if savedskins.has_key(paintobject[0][1].shortname):
                skintexture = savedskins[paintobject[0][1].shortname]
            else:
                for item in paintobject[0][1].subitems:
                    if item.name == "Skins:sg":
                        skintexture = item.subitems[0]
                        break

        if skintexture == None:
            quarkx.msgbox("There are no skins for this component.\nYou must add a proper skin 'Image'\nfrom the Toolboxes 'New File Types' list\nbefore you can use these paint functions.", MT_ERROR, MB_OK)
            return

    if view.info["viewname"] == "skinview":
        skintexture = editor.Root.currentcomponent.currentskin
        if skintexture == None:
            quarkx.msgbox("There are no skins for this component.\nYou must add a proper skin 'Image'\nfrom the Toolboxes 'New File Types' list\nbefore you can use these paint functions.", MT_ERROR, MB_OK)
            return

    tb1 = editor.layout.toolbars["tb_paintmodes"]
    if (tb1.tb.buttons[1].state == quarkpy.qtoolbar.selected and flagsmouse == 264) or (tb1.tb.buttons[2].state == quarkpy.qtoolbar.selected and flagsmouse == 264):
        if skintexture['Pal']:
            if view.info["viewname"] != "skinview":
                pixelpositions = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y, paintobject)
                pixU, pixV = pixelpositions[0]
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"] = str(clickedpixel)
            else:
                pixU, pixV = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y)
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PalettePenColor"] = str(clickedpixel)
        else:
            if view.info["viewname"] != "skinview":
                pixelpositions = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y, paintobject)
                pixU, pixV = pixelpositions[0]
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"] = clickedpixel
            else:
                pixU, pixV = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y)
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBPenColor"] = clickedpixel

        m = qmenu.item("Dummy", None, "")
        ColorSelectorClick(m)

    if tb1.tb.buttons[2].state == quarkpy.qtoolbar.selected and flagsmouse == 288:
        if skintexture['Pal']:
            if view.info["viewname"] != "skinview":
                pixelpositions = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y, paintobject)
                pixU, pixV = pixelpositions[0]
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"] = str(clickedpixel)
            else:
                pixU, pixV = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y)
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_PaletteBrushColor"] = str(clickedpixel)
        else:
            if view.info["viewname"] != "skinview":
                pixelpositions = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y, paintobject)
                pixU, pixV = pixelpositions[0]
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"] = clickedpixel
            else:
                pixU, pixV = quarkpy.mdlutils.TexturePixelLocation(editor, view, x, y)
                texshortname = skintexture.shortname
                texparent = skintexture.parent
                clickedpixel = quarkx.getpixel(texshortname, texparent, pixU, pixV)
                quarkx.setupsubset(SS_MODEL, "Colors")["Paint_RGBBrushColor"] = clickedpixel

        m = qmenu.item("Dummy", None, "")
        ColorSelectorClick(m)


#
# For dialog menu button.
# As new selectors are added that can use a dialog box
# run them through this menu selection button.
# A maximum of 20 buttons can use this feature.
#
def DialogClick(m): # Not being used right now, maybe for Airbrush or Patterns later.
    editor = quarkpy.mdleditor.mdleditor
    if quarkx.setupsubset(SS_MODEL, "Building").getint("PaintMode") < 20:
        quarkx.msgbox("No dialog settings at this time.\n\nReserved for future use.", MT_INFORMATION, MB_OK)
        return

        if quarkx.setupsubset(SS_MODEL, "Building").getint("PaintMode") == 0:
            if editor.layout.explorer.sellist == []:
                quarkx.msgbox("No selection has been made.\n\nYou must first select a group\nof faces to activate this tool and\nchange your settings for this selector.", MT_ERROR, MB_OK)
                return
            else:
                o = editor.layout.explorer.sellist
                m = qmenu.item("Dummy", None, "")
                m.o = o
 #(change)               mapterrainpos.Selector1Click(m)

        elif quarkx.setupsubset(SS_MODEL, "Building").getint("PaintMode") > 0:
            m = qmenu.item("Dummy", None, "")
 #(change)           mapterrainpos.PaintBrushClick(m)

        else:
            quarkx.msgbox("Your current Paint Selector does not use this function.\n\nIt only applyies to one that shows it (uses 'Dialog Box')\n                      in its discription popup.", MT_INFORMATION, MB_OK)
            return
    else:
        quarkx.msgbox("This 'Dialog Box' function is only used with\n'QuArK's Paint mode' selectors.\n\nSelect one that shows it (uses 'Dialog Box')\n               in its discription popup.", MT_ERROR, MB_OK)
        return


class SolidColorPaintClick(quarkpy.mdlhandles.RectSelDragObject):
    "This is just a place holder at this time."

    Hint = hintPlusInfobaselink("Solid Color Paint||Solid Color Paint:\n\nAllows Solid Color Painting of the selected model's skin texture.", "intro.modeleditor.toolpalettes.paintmodes.html#solidcolor")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)


class AirbrushPaintClick(quarkpy.mdlhandles.RectSelDragObject):
    "This is just a place holder at this time."

    Hint = hintPlusInfobaselink("Airbrush Paint||Airbrush Paint:\n\nAllows Multiple Color Painting of the selected model's skin texture.", "intro.modeleditor.toolpalettes.paintmodes.html#airbrush")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)


class PatternPaintClick(quarkpy.mdlhandles.RectSelDragObject):
    "This is just a place holder at this time."

    Hint = hintPlusInfobaselink("Pattern Paint||Pattern Paint:\n\nAllows Pattern Painting of the selected model's skin texture.\n\nNon-functional at this time, reserved for future use.", "intro.modeleditor.toolpalettes.paintmodes.html#pattern")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)


### START OF THE TOOLBAR AND BUTTON SETUP ###########
#
# The tool bar with the available paint modes.
# Add other paint modes from other plug-ins into this list :
#
#              class function      button icon number

PaintModes = [(SolidColorPaintClick        ,1)
             ,(AirbrushPaintClick          ,2)
             ,(PatternPaintClick           ,3)
             ]

### This part effects each buttons selection mode and
### interacts with the Animation and Objects modes toolbar buttons.

def selectmode(btn):
    editor = mapeditor(SS_MODEL)
    if editor is None:
        return
    if editor.Root.currentcomponent.currentskin is None:
        quarkx.msgbox("There are no skins for this component.\nYou must add a proper skin 'Image'\nfrom the Toolboxes 'New File Types' list\nbefore you can use these paint functions.", MT_ERROR, MB_OK)
        return
    try:
        tb1 = editor.layout.toolbars["tb_paintmodes"]
        tb2 = editor.layout.toolbars["tb_objmodes"]
        tb3 = editor.layout.toolbars["tb_animation"]
        tb4 = editor.layout.toolbars["tb_edittools"]
        tb5 = editor.layout.toolbars["tb_AxisLock"]
    except:
        return
    select1(btn, tb1, editor)
    for b in range(len(tb2.tb.buttons)):
        if b == 1:
            tb2.tb.buttons[b].state = quarkpy.qtoolbar.selected
        else:
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
    paintcursor(editor)
    quarkx.update(editor.form)
    quarkx.setupsubset(SS_MODEL, "Building").setint("PaintMode", PaintModes[btn.i][1])
    quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", 0)
    quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
    quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
    editor.MouseDragMode = quarkpy.mdlhandles.RectSelDragObject
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
    editor.MouseDragMode, dummyicon = PaintModes[btn.i]
    if btn.state == 2:
        btn.state = quarkpy.qtoolbar.normal
    else:
        btn.state = quarkpy.qtoolbar.selected

    for b in range(len(toolbar.tb.buttons)):
        if toolbar.tb.buttons[b] == btn:
            pass
        else:
            if b == 4:
                pass
            else:
                toolbar.tb.buttons[b].state = quarkpy.qtoolbar.normal

    if btn != toolbar.tb.buttons[4]:
        allbuttonsoff = 1
        for b in range(len(toolbar.tb.buttons)):
            if b > 0 and b < 4:
                if toolbar.tb.buttons[b].state == quarkpy.qtoolbar.selected:
                    allbuttonsoff = 0
        if allbuttonsoff == 1 and btn != toolbar.tb.buttons[4]:
            toolbar.tb.buttons[4].state = quarkpy.qtoolbar.normal
            quarkx.setupsubset(SS_MODEL, "Options")['Paint_ColorPicker'] = None

    for view in editor.layout.views:
        if MapOption("CrossCursor", SS_MODEL):
            if dummyicon == 1 and view.viewmode == "tex":
                view.cursor = CR_BRUSH
            elif dummyicon == 2 and view.viewmode == "tex":
                view.cursor = CR_CROSS
            elif dummyicon == 3 and view.viewmode == "tex":
                view.cursor = CR_CROSS
            else:
                view.cursor = CR_CROSS
            view.handlecursor = CR_ARROW
        else:
            if dummyicon == 1 and view.viewmode == "tex":
                view.cursor = CR_BRUSH
            elif dummyicon == 2 and view.viewmode == "tex":
                view.cursor = CR_ARROW
            elif dummyicon == 3 and view.viewmode == "tex":
                view.cursor = CR_ARROW
            else:
                view.cursor = CR_ARROW
            view.handlecursor = CR_CROSS


##### Below makes the toolbar and arainges its buttons #####

class PaintModesBar(ToolBar):
    "The Paint modes toolbar buttons."

    Caption = "Paint modes"
    DefaultPos = ((0, 0, 0, 0), 'topdock', 272, 1, 1)

    def ColorPickerClick(self, btn):
        "Controls the Color Picker button on this toolbar."
        editor = mapeditor()
        if btn.state == qtoolbar.normal:
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
        else:
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)

    def buildbuttons(self, layout):
              # to build the single click buttons
        if not ico_dict.has_key('ico_paintmodes'):
            ico_dict['ico_paintmodes']=LoadIconSet1("mdlpaintm", 1.0)
        ico_paintmodes = ico_dict['ico_paintmodes']

              # to build the Mode buttons
        btns = []
        for i in range(len(PaintModes)):
            obj, icon = PaintModes[i]
            btn = qtoolbar.button(selectmode, obj.Hint, ico_paintmodes, icon)
            btn.i = i
            btns.append(btn)
        i = quarkx.setupsubset(SS_MODEL, "Building").getint("PaintMode")
        om = quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode")
        if i == 0 or om == 0:
            leave = 0
        else:
            select1(btns[i], self, layout.editor)

        BuildDialogbtn = qtoolbar.button(DialogClick, "Special Paint Functions Dialog||Special Paint Functions Dialog:\n\nNot functional at this time. Reserved for future use.", ico_paintmodes, 0, infobaselink="intro.modeleditor.toolpalettes.paintmodes.html#dialog")
        ColorPicker = qtoolbar.button(self.ColorPickerClick, "Color Picker||Color Picker:\n\nWhen active along with one of the paint tools, such as the 'Solid Color Paint' tool, you can 'pick' a color to set the paint brush to use by clicking the LMB on a pixel in any of the editor's textured views or the Skin-view.\n\nIf the 'Airbrush Paint' tool is active, doing a click on a pixel using your middle mouse button will set the 'second color' of the airbrush as well.", ico_paintmodes, 4, infobaselink="intro.modeleditor.toolpalettes.paintmodes.html#colorpicker")
        ColorSelector = qtoolbar.button(ColorSelectorClick, "Color Selector\n& Paint Settings||Color Selector & Paint Settings:\n\nThis button opens the dialog to select colors manually from either a palette, if the model uses one, or the RGB color selector.\n\nThere are also various settings for all of the paint tools.", ico_paintmodes, 5, infobaselink="intro.modeleditor.toolpalettes.paintmodes.html#colorselector")

        return [BuildDialogbtn] + btns + [ColorPicker, ColorSelector]



#--- register the new toolbar ---

quarkpy.mdltoolbars.toolbars["tb_paintmodes"] = PaintModesBar


# ----------- REVISION HISTORY ------------
#
# $Log: mdlpaintmodes.py,v $
# Revision 1.13  2012/03/11 05:26:38  cdunde
# Updated Model Editor texture paint functions to do gray-scale and blue-scale
# for texture mapping and greatly improved airbrush function quality for fade in effect.
#
# Revision 1.12  2012/01/29 00:53:47  cdunde
# Missed passing one variable in previous update to this one.
#
# Revision 1.11  2012/01/28 08:12:56  cdunde
# Broke down functions to avoid crash of Python for too many if statements in one function.
# Also did some function drawing fixes and added more functions to other areas.
#
# Revision 1.10  2012/01/26 22:44:42  cdunde
# Fixed airbrush function for all textured views and skin view.
# Added eraser function for all textured views and skin view.
# Added RGB2GRAYSCALE function for skin view only.
#
# Revision 1.9  2012/01/22 07:57:44  cdunde
# File cleanup and minor corrections.
#
# Revision 1.8  2011/11/17 01:19:02  cdunde
# Setup BBox drag toolbar button to work correctly with other toolbar buttons.
#
# Revision 1.7  2011/03/04 06:50:28  cdunde
# Added new face cutting tool, for selected faces, like in the map editor with option to allow vertex separation.
#
# Revision 1.6  2011/02/12 08:36:37  cdunde
# Fixed auto turn off of Objects Maker not working with other toolbars.
#
# Revision 1.5  2009/10/12 20:49:56  cdunde
# Added support for .md3 animationCFG (configuration) support and editing.
#
# Revision 1.4  2008/12/20 08:39:34  cdunde
# Minor adjustment to various Model Editor dialogs for recent fix of item over lapping by Dan.
#
# Revision 1.3  2008/03/20 05:57:43  cdunde
# To update Infobase links.
#
# Revision 1.2  2008/02/23 20:07:45  cdunde
# To fix code error.
#
# Revision 1.1  2008/02/23 04:41:11  cdunde
# Setup new Paint modes toolbar and complete painting functions to allow
# the painting of skin textures in any Model Editor textured and Skin-view.
#
#