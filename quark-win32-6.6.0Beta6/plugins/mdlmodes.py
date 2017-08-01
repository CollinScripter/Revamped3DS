"""   QuArK  -  Quake Army Knife

Plug-in which allows user to lock axis movement
of vertices and other mode functions.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#
# $Header: /cvsroot/quark/runtime/plugins/mdlmodes.py,v 1.32 2011/11/17 01:19:02 cdunde Exp $

Info = {
   "plug-in":       "Model Editor Modes",
   "desc":          "Model Editor Modes",
   "date":          "20 Aug 2000, 20 Jan 2007",
   "author":        "Andy Vincent and cdunde",
   "author e-mail": "andyvinc@hotmail.com, cdunde@sbcglobal.net",
   "quark":         "Version 6" }


import quarkpy.qhandles
from quarkpy.mdlmgr import *
import quarkpy.mdleditor


def lockxclick(m):
    editor = mapeditor()
    quarkpy.qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_AxisLock"]
    if editor.lock_x == 0:
        editor.lock_x = 1
        Lock_X.state = 1
        tb1.tb.buttons[0].state = quarkpy.qtoolbar.selected
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Options")["setLock_X"] = "1"
    else:
        editor.lock_x = 0
        Lock_X.state = 0
        tb1.tb.buttons[0].state = quarkpy.qtoolbar.normal
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Options")["setLock_X"] = "0"


def lockyclick(m):
    editor = mapeditor()
    quarkpy.qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_AxisLock"]
    if editor.lock_y == 0:
        editor.lock_y = 1
        Lock_Y.state = 1
        tb1.tb.buttons[1].state = quarkpy.qtoolbar.selected
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Options")["setLock_Y"] = "1"
    else:
        editor.lock_y = 0
        Lock_Y.state = 0
        tb1.tb.buttons[1].state = quarkpy.qtoolbar.normal
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Options")["setLock_Y"] = "0"


def lockzclick(m):
    editor = mapeditor()
    quarkpy.qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_AxisLock"]
    if editor.lock_z == 0:
        editor.lock_z = 1
        Lock_Z.state = 1
        tb1.tb.buttons[2].state = quarkpy.qtoolbar.selected
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Options")["setLock_Z"] = "1"
    else:
        editor.lock_z = 0
        Lock_Z.state = 0
        tb1.tb.buttons[2].state = quarkpy.qtoolbar.normal
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Options")["setLock_Z"] = "0"


Lock_X = qmenu.item("Lock &X", lockxclick, "lock x axis movement")  # Commands menu item
Lock_Y = qmenu.item("Lock &Y", lockyclick, "lock y axis movement")  # Commands menu item
Lock_Z = qmenu.item("Lock &Z", lockzclick, "lock z axis movement")  # Commands menu item


### Start of 3D views Options Dialog ###

class OptionsViewsDlg(quarkpy.dlgclasses.LiveEditDlg):
    "The Model Editors Views Options dialog box."
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (160,705)
    dlgflags = FWF_KEEPFOCUS   # keeps dialog box open
    dfsep = 0.62    # sets 62% for labels and the rest for edit boxes
    dlgdef = """
      {
        Style = "13"
        Caption = "Views Options"
        sep: = {
        Typ="S"
        Txt="Editors 3D view"
               }

        nohandles1: =
        {
        Txt = "No drag handles"
        Typ = "X1"
        Hint = "No handles will exist"
        }

        drawnohandles1: =
        {
        Txt = "Draw no handles"
        Typ = "X1"
        Hint = "No handles will be drawn"
        }

        framemesh1: =
        {
        Txt = "Mesh in Frames"
        Typ = "X1"
        Hint = "Mesh will be drawn"
        }

        frameColor1: =
        {
        Txt = "Model mesh color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

        fillmesh1: =
        {
        Txt = "Fill in Mesh"
        Typ = "X1"
        Hint = "Mesh will be solid"
        }

        fillColor1: =
        {
        Txt = "Fill in color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

      sep: = { Typ="S" Txt="" }

      sep: = {
        Typ="S"
        Txt="Z 2D view"
             }

        nohandles2: =
        {
        Txt = "No drag handles"
        Typ = "X1"
        Hint = "No handles will exist"
        }

        drawnohandles2: =
        {
        Txt = "Draw no handles"
        Typ = "X1"
        Hint = "No handles will be drawn"
        }

        framemesh2: =
        {
        Txt = "Mesh in Frames"
        Typ = "X1"
        Hint = "Mesh will be drawn"
        }

        frameColor2: =
        {
        Txt = "Model mesh color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

        fillmesh2: =
        {
        Txt = "Fill in Mesh"
        Typ = "X1"
        Hint = "Mesh will be solid"
        }

        fillColor2: =
        {
        Txt = "Fill in color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

      sep: = { Typ="S" Txt="" }

      sep: = {
        Typ="S"
        Txt="X 2D view"
             }

        nohandles3: =
        {
        Txt = "No drag handles"
        Typ = "X1"
        Hint = "No handles will exist"
        }

        drawnohandles3: =
        {
        Txt = "Draw no handles"
        Typ = "X1"
        Hint = "No handles will be drawn"
        }

        framemesh3: =
        {
        Txt = "Mesh in Frames"
        Typ = "X1"
        Hint = "Mesh will be drawn"
        }

        frameColor3: =
        {
        Txt = "Model mesh color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

        fillmesh3: =
        {
        Txt = "Fill in Mesh"
        Typ = "X1"
        Hint = "Mesh will be solid"
        }

        fillColor3: =
        {
        Txt = "Fill in color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

      sep: = { Typ="S" Txt="" }

      sep: = {
        Typ="S"
        Txt="Y 2D view"
             }

        nohandles4: =
        {
        Txt = "No drag handles"
        Typ = "X1"
        Hint = "No handles will exist"
        }

        drawnohandles4: =
        {
        Txt = "Draw no handles"
        Typ = "X1"
        Hint = "No handles will be drawn"
        }

        framemesh4: =
        {
        Txt = "Mesh in Frames"
        Typ = "X1"
        Hint = "Mesh will be drawn"
        }

        frameColor4: =
        {
        Txt = "Model mesh color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

        fillmesh4: =
        {
        Txt = "Fill in Mesh"
        Typ = "X1"
        Hint = "Mesh will be solid"
        }

        fillColor4: =
        {
        Txt = "Fill in color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

      sep: = { Typ="S" Txt="" }

      sep: = {
        Typ="S"
        Txt="Full 3D view"
             }

        nohandles5: =
        {
        Txt = "No drag handles"
        Typ = "X1"
        Hint = "No handles will exist"
        }

        drawnohandles5: =
        {
        Txt = "Draw no handles"
        Typ = "X1"
        Hint = "No handles will be drawn"
        }

        framemesh5: =
        {
        Txt = "Mesh in Frames"
        Typ = "X1"
        Hint = "Mesh will be drawn"
        }

        frameColor5: =
        {
        Txt = "Model mesh color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

        fillmesh5: =
        {
        Txt = "Fill in Mesh"
        Typ = "X1"
        Hint = "Mesh will be solid"
        }

        fillColor5: =
        {
        Txt = "Fill in color"
        Typ = "LI"
        Hint = "Mesh solid fill color"
        }

      sep: = { Typ="S" Txt="" }

        Reset: =       // Reset button
        {
          Cap = "defaults"      // button caption
          Typ = "B"                     // "B"utton
          Hint = "Resets all views to"$0D"their default settings"
          Delete: =
          {            // the button resets to these amounts
        nohandles1 = "0"
        drawnohandles1 = "0"
        framemesh1 = "0"
        frameColor1 = $FFFFFF
        fillmesh1 = "0"
        fillColor1 = $FF8080
        nohandles2 = "0"
        drawnohandles2 = "0"
        framemesh2 = "1"
        frameColor2 = $FFFFFFFF
        fillmesh2 = "0"
        fillColor2 = $FF8080
        nohandles3 = "0"
        drawnohandles3 = "0"
        framemesh3 = "1"
        frameColor3 = $FFFFFFFF
        fillmesh3 = "0"
        fillColor3 = $FF8080
        nohandles4 = "0"
        drawnohandles4 = "0"
        framemesh4 = "1"
        frameColor4 = $FFFFFFFF
        fillmesh4 = "0"
        fillColor4 = $FF8080
        nohandles5 = "0"
        drawnohandles5 = "0"
        framemesh5 = "0"
        frameColor5 = $FFFFFF
        fillmesh5 = "0"
        fillColor5 = $FF8080
          }
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="Close" }
      }
    """


def OptionsViewsClick(m):
    editor = mapeditor()
    if editor is None: return
  
    def setup(self):
        editor.findtargetdlg=self
        self.editor = editor
        src = self.src

      ### To populate settings...
        if (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor1"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh1"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor1"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor2"] is None) and  (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh2"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor2"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor3"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh3"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor3"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor4"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh4"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor4"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor5"] is None) and (quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh5"] is None) and (quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor5"] is None):

            src["nohandles1"] = "0"
            src["drawnohandles1"] = "0"
            src["framemesh1"] = "0"
            src["frameColor1"] = "$FFFFFF"
            src["fillmesh1"] = "0"
            src["fillColor1"] = "$FF8080"
            src["nohandles2"] = "0"
            src["drawnohandles2"] = "0"
            src["framemesh2"] = "1"
            src["frameColor2"] = "$FFFFFFFF"
            src["fillmesh2"] = "0"
            src["fillColor2"] = "$FF8080"
            src["nohandles3"] = "0"
            src["drawnohandles3"] = "0"
            src["framemesh3"] = "1"
            src["frameColor3"] = "$FFFFFFFF"
            src["fillmesh3"] = "0"
            src["fillColor3"] = "$FF8080"
            src["nohandles4"] = "0"
            src["drawnohandles4"] = "0"
            src["framemesh4"] = "1"
            src["frameColor4"] = "$FFFFFFFF"
            src["fillmesh4"] = "0"
            src["fillColor4"] = "$FF8080"
            src["nohandles5"] = "0"
            src["drawnohandles5"] = "0"
            src["framemesh5"] = "0"
            src["frameColor5"] = "$FFFFFF"
            src["fillmesh5"] = "0"
            src["fillColor5"] = "$FF8080"
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] = src["nohandles1"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] = src["drawnohandles1"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] = src["framemesh1"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor1"] = src["frameColor1"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh1"] = src["fillmesh1"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor1"] = src["fillColor1"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] = src["nohandles2"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] = src["drawnohandles2"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] = src["framemesh2"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor2"] = src["frameColor2"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh2"] = src["fillmesh2"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor2"] = src["fillColor2"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] = src["nohandles3"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] = src["drawnohandles3"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] = src["framemesh3"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor3"] = src["frameColor3"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh3"] = src["fillmesh3"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor3"] = src["fillColor3"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] = src["nohandles4"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] = src["drawnohandles4"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] = src["framemesh4"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor4"] = src["frameColor4"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh4"] = src["fillmesh4"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor4"] = src["fillColor4"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] = src["nohandles5"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] = src["drawnohandles5"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] = src["framemesh5"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor5"] = src["frameColor5"]
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh5"] = src["fillmesh5"]
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor5"] = src["fillColor5"]

        else:
            src["nohandles1"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"]
            src["drawnohandles1"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"]
            src["framemesh1"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"]
            src["frameColor1"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor1"]
            src["fillmesh1"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh1"]
            src["fillColor1"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor1"]
            src["nohandles2"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"]
            src["drawnohandles2"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"]
            src["framemesh2"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"]
            src["frameColor2"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor2"]
            src["fillmesh2"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh2"]
            src["fillColor2"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor2"]
            src["nohandles3"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"]
            src["drawnohandles3"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"]
            src["framemesh3"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"]
            src["frameColor3"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor3"]
            src["fillmesh3"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh3"]
            src["fillColor3"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor3"]
            src["nohandles4"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"]
            src["drawnohandles4"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"]
            src["framemesh4"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"]
            src["frameColor4"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor4"]
            src["fillmesh4"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh4"]
            src["fillColor4"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor4"]
            src["nohandles5"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"]
            src["drawnohandles5"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"]
            src["framemesh5"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"]
            src["frameColor5"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor5"]
            src["fillmesh5"] = quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh5"]
            src["fillColor5"] = quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor5"]


        if src["nohandles1"]:
            onenohandles = src["nohandles1"]
        else:
            onenohandles = "0"


        if src["drawnohandles1"]:
            onedrawnohandles = src["drawnohandles1"]
        else:
            onedrawnohandles = "0"


        if src["framemesh1"]:
            oneframemesh = src["framemesh1"]
        else:
            oneframemesh = "0"


        if src["frameColor1"]:
            oneframemesh = src["frameColor1"]
        else:
            oneframeColor = "$FFFFFF"


        if src["fillmesh1"]:
            onefillmesh = src["fillmesh1"]
        else:
            onefillmesh = "0"


        if src["fillColor1"]:
            onefillColor = src["fillColor1"]
        else:
            onefillColor = "$FF8080"


        if src["nohandles2"]:
            twonohandles = src["nohandles2"]
        else:
            twonohandles = "0"


        if src["drawnohandles2"]:
            twodrawnohandles = src["drawnohandles2"]
        else:
            twodrawnohandles = "0"


        if src["framemesh2"]:
            twoframemesh = src["framemesh2"]
        else:
            twoframemesh = "0"


        if src["frameColor2"]:
            twoframemesh = src["frameColor2"]
        else:
            twoframeColor = "$FFFFFF"


        if src["fillmesh2"]:
            twofillmesh = src["fillmesh2"]
        else:
            twofillmesh = "0"


        if src["fillColor2"]:
            twofillColor = src["fillColor2"]
        else:
            twofillColor = "$FF8080"


        if src["nohandles3"]:
            threenohandles = src["nohandles3"]
        else:
            threenohandles = "0"


        if src["drawnohandles3"]:
            threedrawnohandles = src["drawnohandles3"]
        else:
            threedrawnohandles = "0"


        if src["framemesh3"]:
            threeframemesh = src["framemesh3"]
        else:
            threeframemesh = "0"


        if src["frameColor3"]:
            threeframemesh = src["frameColor3"]
        else:
            threeframeColor = "$FFFFFF"


        if src["fillmesh3"]:
            threefillmesh = src["fillmesh3"]
        else:
            threefillmesh = "0"


        if src["fillColor3"]:
            threefillColor = src["fillColor3"]
        else:
            threefillColor = "$FF8080"


        if src["nohandles4"]:
            fournohandles = src["nohandles4"]
        else:
            fournohandles = "0"


        if src["drawnohandles4"]:
            fourdrawnohandles = src["drawnohandles4"]
        else:
            fourdrawnohandles = "0"


        if src["framemesh4"]:
            fourframemesh = src["framemesh4"]
        else:
            fourframemesh = "0"


        if src["frameColor4"]:
            fourframemesh = src["frameColor4"]
        else:
            fourframeColor = "$FFFFFF"


        if src["fillmesh4"]:
            fourfillmesh = src["fillmesh4"]
        else:
            fourfillmesh = "0"


        if src["fillColor4"]:
            fourfillColor = src["fillColor4"]
        else:
            fourfillColor = "$FF8080"


        if src["nohandles5"]:
            fivenohandles = src["nohandles5"]
        else:
            fivenohandles = "0"


        if src["drawnohandles5"]:
            fivedrawnohandles = src["drawnohandles5"]
        else:
            fivedrawnohandles = "0"


        if src["framemesh5"]:
            fiveframemesh = src["framemesh5"]
        else:
            fiveframemesh = "0"


        if src["frameColor5"]:
            fiveframemesh = src["frameColor5"]
        else:
            fiveframeColor = "$FFFFFF"


        if src["fillmesh5"]:
            fivefillmesh = src["fillmesh5"]
        else:
            fivefillmesh = "0"


        if src["fillColor5"]:
            fivefillColor = src["fillColor5"]
        else:
            fivefillColor = "$FF8080"


    def action(self, editor=editor):

        if (self.src["nohandles1"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] == "1":
            onenohandles = (self.src["nohandles1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] = onenohandles
            (self.src["drawnohandles1"]) = "0"
            onedrawnohandles = (self.src["drawnohandles1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] = onedrawnohandles

        if (self.src["drawnohandles1"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
            onedrawnohandles = (self.src["drawnohandles1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] = onedrawnohandles
            (self.src["nohandles1"]) = "0"
            onenohandles = (self.src["nohandles1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] = onenohandles

        if (self.src["framemesh1"]) == "1":
            oneframemesh = (self.src["framemesh1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] = oneframemesh
        else:
            (self.src["framemesh1"]) = "0"
            oneframemesh = (self.src["framemesh1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] = oneframemesh

        if (self.src["frameColor1"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor1"] != None:
            oneframeColor = (self.src["frameColor1"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor1"] = oneframeColor
        else:
            (self.src["frameColor1"]) = "$FFFFFF"
            oneframeColor = (self.src["frameColor1"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor1"] = oneframeColor

        if (self.src["fillmesh1"]) == "1":
            onefillmesh = (self.src["fillmesh1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh1"] = onefillmesh
        else:
            (self.src["fillmesh1"]) = "0"
            onefillmesh = (self.src["fillmesh1"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh1"] = onefillmesh

        if (self.src["fillColor1"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor1"] != None:
            onefillColor = (self.src["fillColor1"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor1"] = onefillColor
        else:
            (self.src["fillColor1"]) = "$FF8080"
            onefillColor = (self.src["fillColor1"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor1"] = onefillColor

        if (self.src["nohandles2"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] == "1":
            twonohandles = (self.src["nohandles2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] = twonohandles
            (self.src["drawnohandles2"]) = "0"
            twodrawnohandles = (self.src["drawnohandles2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] = twodrawnohandles

        if (self.src["drawnohandles2"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
            twodrawnohandles = (self.src["drawnohandles2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] = twodrawnohandles
            (self.src["nohandles2"]) = "0"
            twonohandles = (self.src["nohandles2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] = twonohandles

        if (self.src["framemesh2"]) == "1":
            twoframemesh = (self.src["framemesh2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] = twoframemesh
        else:
            (self.src["framemesh2"]) = "0"
            twoframemesh = (self.src["framemesh2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] = twoframemesh

        if (self.src["frameColor2"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor2"] != None:
            twoframeColor = (self.src["frameColor2"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor2"] = twoframeColor
        else:
            (self.src["frameColor2"]) = "$FFFFFF"
            twoframeColor = (self.src["frameColor2"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor2"] = twoframeColor

        if (self.src["fillmesh2"]) == "1":
            twofillmesh = (self.src["fillmesh2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh2"] = twofillmesh
        else:
            (self.src["fillmesh2"]) = "0"
            twofillmesh = (self.src["fillmesh2"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh2"] = twofillmesh

        if (self.src["fillColor2"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor2"] != None:
            twofillColor = (self.src["fillColor2"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor2"] = twofillColor
        else:
            (self.src["fillColor2"]) = "$FF8080"
            twofillColor = (self.src["fillColor2"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor2"] = twofillColor

        if (self.src["nohandles3"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] == "1":
            threenohandles = (self.src["nohandles3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] = threenohandles
            (self.src["drawnohandles3"]) = "0"
            threedrawnohandles = (self.src["drawnohandles3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] = threedrawnohandles

        if (self.src["drawnohandles3"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
            threedrawnohandles = (self.src["drawnohandles3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] = threedrawnohandles
            (self.src["nohandles3"]) = "0"
            threenohandles = (self.src["nohandles3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] = threenohandles

        if (self.src["framemesh3"]) == "1":
            threeframemesh = (self.src["framemesh3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] = threeframemesh
        else:
            (self.src["framemesh3"]) = "0"
            threeframemesh = (self.src["framemesh3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] = threeframemesh

        if (self.src["frameColor3"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor3"] != None:
            threeframeColor = (self.src["frameColor3"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor3"] = threeframeColor
        else:
            (self.src["frameColor3"]) = "$FFFFFF"
            threeframeColor = (self.src["frameColor3"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor3"] = threeframeColor

        if (self.src["fillmesh3"]) == "1":
            threefillmesh = (self.src["fillmesh3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh3"] = threefillmesh
        else:
            (self.src["fillmesh3"]) = "0"
            threefillmesh = (self.src["fillmesh3"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh3"] = threefillmesh

        if (self.src["fillColor3"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor3"] != None:
            threefillColor = (self.src["fillColor3"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor3"] = threefillColor
        else:
            (self.src["fillColor3"]) = "$FF8080"
            threefillColor = (self.src["fillColor3"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor3"] = threefillColor

        if (self.src["nohandles4"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] == "1":
            fournohandles = (self.src["nohandles4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] = fournohandles
            (self.src["drawnohandles4"]) = "0"
            fourdrawnohandles = (self.src["drawnohandles4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] = fourdrawnohandles

        if (self.src["drawnohandles4"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
            fourdrawnohandles = (self.src["drawnohandles4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] = fourdrawnohandles
            (self.src["nohandles4"]) = "0"
            fournohandles = (self.src["nohandles4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] = fournohandles

        if (self.src["framemesh4"]) == "1":
            fourframemesh = (self.src["framemesh4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] = fourframemesh
        else:
            (self.src["framemesh4"]) = "0"
            fourframemesh = (self.src["framemesh4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] = fourframemesh

        if (self.src["frameColor4"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor4"] != None:
            fourframeColor = (self.src["frameColor4"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor4"] = fourframeColor
        else:
            (self.src["frameColor4"]) = "$FFFFFF"
            fourframeColor = (self.src["frameColor4"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor4"] = fourframeColor

        if (self.src["fillmesh4"]) == "1":
            fourfillmesh = (self.src["fillmesh4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh4"] = fourfillmesh
        else:
            (self.src["fillmesh4"]) = "0"
            fourfillmesh = (self.src["fillmesh4"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh4"] = fourfillmesh

        if (self.src["fillColor4"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor4"] != None:
            fourfillColor = (self.src["fillColor4"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor4"] = fourfillColor
        else:
            (self.src["fillColor4"]) = "$FF8080"
            fourfillColor = (self.src["fillColor4"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor4"] = fourfillColor

        if (self.src["nohandles5"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] == "1":
            fivenohandles = (self.src["nohandles5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] = fivenohandles
            (self.src["drawnohandles5"]) = "0"
            fivedrawnohandles = (self.src["drawnohandles5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] = fivedrawnohandles

        if (self.src["drawnohandles5"]) == "1" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
            fivedrawnohandles = (self.src["drawnohandles5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] = fivedrawnohandles
            (self.src["nohandles5"]) = "0"
            fivenohandles = (self.src["nohandles5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] = fivenohandles

        if (self.src["framemesh5"]) == "1":
            fiveframemesh = (self.src["framemesh5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] = fiveframemesh
        else:
            (self.src["framemesh5"]) = "0"
            fiveframemesh = (self.src["framemesh5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] = fiveframemesh

        if (self.src["frameColor5"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor5"] != None:
            fiveframeColor = (self.src["frameColor5"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor5"] = fiveframeColor
        else:
            (self.src["frameColor5"]) = "$FFFFFF"
            fiveframeColor = (self.src["frameColor5"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor5"] = fiveframeColor

        if (self.src["fillmesh5"]) == "1":
            fivefillmesh = (self.src["fillmesh5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh5"] = fivefillmesh
        else:
            (self.src["fillmesh5"]) = "0"
            fivefillmesh = (self.src["fillmesh5"])
            quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh5"] = fivefillmesh

        if (self.src["fillColor5"]) != None and quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor5"] != None:
            fivefillColor = (self.src["fillColor5"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor5"] = fivefillColor
        else:
            (self.src["fillColor5"]) = "$FF8080"
            fivefillColor = (self.src["fillColor5"])
            quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor5"] = fivefillColor

        onenohandles = (self.src["nohandles1"])
        onedrawnohandles = (self.src["drawnohandles1"])
        oneframemesh = (self.src["framemesh1"])
        oneframeColor = (self.src["frameColor1"])
        onefillmesh = (self.src["fillmesh1"])
        onefillColor = (self.src["fillColor1"])
        twonohandles = (self.src["nohandles2"])
        twodrawnohandles = (self.src["drawnohandles2"])
        twoframemesh = (self.src["framemesh2"])
        twoframeColor = (self.src["frameColor2"])
        twofillmesh = (self.src["fillmesh2"])
        twofillColor = (self.src["fillColor2"])
        threenohandles = (self.src["nohandles3"])
        threedrawnohandles = (self.src["drawnohandles3"])
        threeframemesh = (self.src["framemesh3"])
        threeframeColor = (self.src["frameColor3"])
        threefillmesh = (self.src["fillmesh3"])
        threefillColor = (self.src["fillColor3"])
        fournohandles = (self.src["nohandles4"])
        fourdrawnohandles = (self.src["drawnohandles4"])
        fourframemesh = (self.src["framemesh4"])
        fourframeColor = (self.src["frameColor4"])
        fourfillmesh = (self.src["fillmesh4"])
        fourfillColor = (self.src["fillColor4"])
        fivenohandles = (self.src["nohandles5"])
        fivedrawnohandles = (self.src["drawnohandles5"])
        fiveframemesh = (self.src["framemesh5"])
        fiveframeColor = (self.src["frameColor5"])
        fivefillmesh = (self.src["fillmesh5"])
        fivefillColor = (self.src["fillColor5"])

      ### Save the settings...
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] = onenohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] = onedrawnohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] = oneframemesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor1"] = oneframeColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh1"] = onefillmesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor1"] = onefillColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] = twonohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] = twodrawnohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] = twoframemesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor2"] = twoframeColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh2"] = twofillmesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor2"] = twofillColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] = threenohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] = threedrawnohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] = threeframemesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor3"] = threeframeColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh3"] = threefillmesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor3"] = threefillColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] = fournohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] = fourdrawnohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] = fourframemesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor4"] = fourframeColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh4"] = fourfillmesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor4"] = fourfillColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] = fivenohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] = fivedrawnohandles
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] = fiveframemesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_frameColor5"] = fiveframeColor
        quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh5"] = fivefillmesh
        quarkx.setupsubset(SS_MODEL, "Colors")["Options3Dviews_fillColor5"] = fivefillColor

        self.src["nohandles1"] = onenohandles
        self.src["drawnohandles1"] = onedrawnohandles
        self.src["framemesh1"] = oneframemesh
        self.src["frameColor1"] = oneframeColor
        self.src["fillmesh1"] = onefillmesh
        self.src["fillColor1"] = onefillColor
        self.src["nohandles2"] = twonohandles
        self.src["drawnohandles2"] = twodrawnohandles
        self.src["framemesh2"] = twoframemesh
        self.src["frameColor2"] = twoframeColor
        self.src["fillmesh2"] = twofillmesh
        self.src["fillColor2"] = twofillColor
        self.src["nohandles3"] = threenohandles
        self.src["drawnohandles3"] = threedrawnohandles
        self.src["framemesh3"] = threeframemesh
        self.src["frameColor3"] = threeframeColor
        self.src["fillmesh3"] = threefillmesh
        self.src["fillColor3"] = threefillColor
        self.src["nohandles4"] = fournohandles
        self.src["drawnohandles4"] = fourdrawnohandles
        self.src["framemesh4"] = fourframemesh
        self.src["frameColor4"] = fourframeColor
        self.src["fillmesh4"] = fourfillmesh
        self.src["fillColor4"] = fourfillColor
        self.src["nohandles5"] = fivenohandles
        self.src["drawnohandles5"] = fivedrawnohandles
        self.src["framemesh5"] = fiveframemesh
        self.src["frameColor5"] = fiveframeColor
        self.src["fillmesh5"] = fivefillmesh
        self.src["fillColor5"] = fivefillColor

        editor.explorerselchange(editor)


    def onclosing(self,editor=editor):
        try:
            del editor.findtargetdlg
        except:
            pass
        
    OptionsViewsDlg(quarkx.clickform, 'optionsviewsdlg', editor, setup, action, onclosing)


parent = quarkpy.qhandles.RectangleDragObject
class BBoxMakerDragObject(parent):
    "A bbox cube maker."

    Hint = hintPlusInfobaselink("Quick bbox maker||Quick bbox maker:\n\nWhen active allows the LMB drag creation of a bounding box in any view.\n\nCan only be used when a single bone is selected for the bbox to be linked to.", "intro.modeleditor.toolpalettes.viewselection.html#bboxmaker")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1)
        p = view.proj(self.pt0)
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y

    def buildredimages(self, x, y, flags):
        depth = self.view.depth
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, depth[0]), 1))
        if p.visible:
            x = p.x
            y = p.y
        dx = abs(self.x0-x)
        dy = abs(self.y0-y)
        if dx>dy: dx=dy
        min = (depth[0]+depth[1]-dx)*0.5
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, min), 1))
        if p.visible:
            min = p.z
        max = min + dx
        return parent.buildredimages(self, x, y, flags, (min,max))

    def rectanglesel(self, editor, x,y, rectangle, view):
        comp = editor.Root.currentcomponent
        quarkpy.mdleditor.setsingleframefillcolor(editor, view)
        plugins.mdlgridscale.gridfinishdrawing(editor, view)
        for v in editor.layout.views:
            bbox = quarkx.boundingboxof([rectangle])
            m = bbox[0].tuple
            M = bbox[1].tuple
            box = [quarkx.vect(m), quarkx.vect(M), quarkx.vect(m[0],m[1],M[2]), quarkx.vect(m[0],M[1],m[2]), quarkx.vect(m[0],M[1],M[2]), quarkx.vect(M[0],m[1],M[2]), quarkx.vect(M[0],m[1],m[2]), quarkx.vect(M[0],M[1],m[2])]
            cv = v.canvas()
            cv.pencolor = RED
            for bp in xrange(len(box)):
                box[bp] = v.proj(box[bp])
            cv.line(int(box[0].x), int(box[0].y), int(box[2].x), int(box[2].y))
            cv.line(int(box[0].x), int(box[0].y), int(box[3].x), int(box[3].y))
            cv.line(int(box[3].x), int(box[3].y), int(box[4].x), int(box[4].y))
            cv.line(int(box[4].x), int(box[4].y), int(box[2].x), int(box[2].y))
            cv.line(int(box[0].x), int(box[0].y), int(box[6].x), int(box[6].y))
            cv.line(int(box[3].x), int(box[3].y), int(box[7].x), int(box[7].y))
            cv.line(int(box[4].x), int(box[4].y), int(box[1].x), int(box[1].y))
            cv.line(int(box[2].x), int(box[2].y), int(box[5].x), int(box[5].y))
            cv.line(int(box[6].x), int(box[6].y), int(box[7].x), int(box[7].y))
            cv.line(int(box[7].x), int(box[7].y), int(box[1].x), int(box[1].y))
            cv.line(int(box[1].x), int(box[1].y), int(box[5].x), int(box[5].y))
            cv.line(int(box[5].x), int(box[5].y), int(box[6].x), int(box[6].y))

        undo = quarkx.action()
        parent = editor.Root.dictitems['Misc:mg']
        polys = parent.findallsubitems("", ':p')
        count = 1
        newpoly = rectangle.copy()
        newpoly['assigned2'] = "None"
        newpoly['show'] = (1.0,)
        for poly in polys:
            if poly.shortname.startswith("bbox "):
                nbr = None
                try:
                    nbr = poly.shortname.split(" ")[1]
                except:
                    pass
                if nbr is not None:
                    if int(nbr) >= count:
                        count = int(nbr) + 1
                else:
                    count = count + 1
        newpoly.shortname = "bbox " + str(count)
        face_names = ['north', 'east', 'south', 'west', 'up', 'down']
        for f in range(len(newpoly.subitems)):
            newpoly.subitems[f].shortname = face_names[f]

        undo.put(parent, newpoly)
        editor.ok(undo, "bbox added")


def DialogViewsClick(m):
    editor = mapeditor()
    m = qmenu.item("Dummy", None, "")
    OptionsViewsClick(m)

def ColorsClick(m):
    editor = mapeditor()
    m = qmenu.item("Dummy", None, "")
    quarkx.openconfigdlg("Model:Colors")

def BBoxClick(m):
    editor = mapeditor()
    quarkpy.qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_AxisLock"]
    tb2 = editor.layout.toolbars["tb_objmodes"]
    tb3 = editor.layout.toolbars["tb_edittools"]
    if not MdlOption("MakeBBox"):
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
        tb1.tb.buttons[5].state = quarkpy.qtoolbar.selected
        for b in range(len(tb2.tb.buttons)):
            if b == 1:
                tb2.tb.buttons[b].state = quarkpy.qtoolbar.selected
            else:
                tb2.tb.buttons[b].state = quarkpy.qtoolbar.normal
        for b in range(len(tb3.tb.buttons)):
            if b == 7:
                tb3.tb.buttons[b].state = quarkpy.qtoolbar.normal
        quarkx.update(editor.form)
        editor.MouseDragMode = BBoxMakerDragObject
    else:
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
        tb1.tb.buttons[5].state = quarkpy.qtoolbar.normal
        quarkx.update(editor.form)
        editor.MouseDragMode = mdlhandles.RectSelDragObject


class AxisLockBar(ToolBar):
    "Creates the Axis Lock Toolbar at startup."

    Caption = "View Selection Modes"

    def buildbuttons(self, layout):
        ico_mdled=ico_dict['ico_mdled']
        LockXBtn = qtoolbar.button(lockxclick, "Lock X Axis", ico_mdled, 0)  # tb_AxisLock[0] button
        LockYBtn = qtoolbar.button(lockyclick, "Lock Y Axis", ico_mdled, 1)  # tb_AxisLock[1] button
        LockZBtn = qtoolbar.button(lockzclick, "Lock Z Axis", ico_mdled, 2)  # tb_AxisLock[2] button
        viewsDialogbtn = qtoolbar.button(DialogViewsClick, "Views Options\nDialog Input\n(opens the input box)||Views Options Dialog Input:\n\nThis will open its own 'Dialog Box' and is laid out in the same order as the 'Display tool-palette'. \n\nThis dialog gives you the ability to customize every view that QuArK provides and does so independently from one view to the next.", ico_mdled, 3, infobaselink="intro.modeleditor.toolpalettes.viewselection.html#viewoptions")
        Colorsbtn = qtoolbar.button(ColorsClick, "Color Options\nfor quick line and\nvertex color changes||Color Options:\n\nThis will open the 'Configuration Model Editor Colors' selection dialog.\n\nThis dialog allows you to quickly change a variety of line and vertex color settings for easer viewing as needed.", ico_mdled, 4, infobaselink="intro.modeleditor.toolpalettes.viewselection.html#coloroptions")
        BBoxbtn = qtoolbar.button(BBoxClick, "Quick bbox maker||Quick bbox maker:\n\nWhen active allows the LMB drag creation of a bounding box in any view.\n\nCan only be used when a single bone is selected for the bbox to be linked to.", ico_mdled, 5, infobaselink="intro.modeleditor.toolpalettes.viewselection.html#bboxmaker")
        layout.buttons.update({"lockx": LockXBtn, "locky": LockYBtn, "lockz": LockZBtn, "bboxes": BBoxbtn})

        if quarkx.setupsubset(SS_MODEL, "Options")["setLock_X"]=="1":
            LockXBtn.state = quarkpy.qtoolbar.selected
        else:
            LockXBtn.state = quarkpy.qtoolbar.normal

        if quarkx.setupsubset(SS_MODEL, "Options")["setLock_Y"]=="1":
            LockYBtn.state = quarkpy.qtoolbar.selected
        else:
            LockYBtn.state = quarkpy.qtoolbar.normal

        if quarkx.setupsubset(SS_MODEL, "Options")["setLock_Z"]=="1":
            LockZBtn.state = quarkpy.qtoolbar.selected
        else:
            LockZBtn.state = quarkpy.qtoolbar.normal

        return [LockXBtn, LockYBtn, LockZBtn, viewsDialogbtn, Colorsbtn, BBoxbtn]


quarkpy.mdlcommands.items.append(quarkpy.qmenu.sep)
quarkpy.mdlcommands.items.append(Lock_X)
quarkpy.mdlcommands.items.append(Lock_Y)
quarkpy.mdlcommands.items.append(Lock_Z)
quarkpy.mdlcommands.shortcuts["Shift+X"] = Lock_X
quarkpy.mdlcommands.shortcuts["Shift+Y"] = Lock_Y
quarkpy.mdlcommands.shortcuts["Shift+Z"] = Lock_Z

#--- register the new toolbar ---
quarkpy.mdltoolbars.toolbars["tb_AxisLock"] = AxisLockBar

Lock_X.state = int(quarkx.setupsubset(SS_MODEL, "Options")["setLock_X"])
Lock_Y.state = int(quarkx.setupsubset(SS_MODEL, "Options")["setLock_Y"])
Lock_Z.state = int(quarkx.setupsubset(SS_MODEL, "Options")["setLock_Z"])


# ----------- REVISION HISTORY ------------
# $Log: mdlmodes.py,v $
# Revision 1.32  2011/11/17 01:19:02  cdunde
# Setup BBox drag toolbar button to work correctly with other toolbar buttons.
#
# Revision 1.31  2011/11/16 07:40:29  cdunde
# Removed handle drawing call to stop dupe drawing of them.
#
# Revision 1.30  2011/03/02 04:38:24  cdunde
# InfoBase link update.
#
# Revision 1.29  2011/03/01 08:09:20  cdunde
# InfoBase link update.
#
# Revision 1.28  2010/12/07 06:06:52  cdunde
# Updates for Model Editor bounding box system.
#
# Revision 1.27  2010/12/06 05:43:06  cdunde
# Updates for Model Editor bounding box system.
#
# Revision 1.26  2010/06/05 21:43:44  cdunde
# Fix to update dialog and specifics page before redrawing views and draw fillcolors correctly.
#
# Revision 1.25  2010/05/01 04:25:37  cdunde
# Updated files to help increase editor speed by including necessary ModelComponentList items
# and removing redundant checks and calls to the list.
#
# Revision 1.24  2008/05/01 19:15:25  danielpharos
# Fix treeviewselchanged not updating.
#
# Revision 1.23  2008/05/01 14:02:31  danielpharos
# Removed redundant code (this is already done elsewhere).
#
# Revision 1.22  2008/05/01 13:52:32  danielpharos
# Removed a whole bunch of redundant imports and other small fixes.
#
# Revision 1.21  2008/02/23 04:41:11  cdunde
# Setup new Paint modes toolbar and complete painting functions to allow
# the painting of skin textures in any Model Editor textured and Skin-view.
#
# Revision 1.20  2008/02/07 13:20:23  danielpharos
# Removed redundant comment line
#
# Revision 1.19  2007/10/31 05:36:56  cdunde
# Replaced quarkx.reloadsetup() with call to invalidate views using correct filltris call.
#
# Revision 1.18  2007/09/09 18:34:39  cdunde
# To stop quarkx.reloadsetup call (which just calls qutils.SetupChanged)
# from duplicate handle drawing in the Model Editor and use quarkx.reloadsetup
# in mdlmodes for setting "colors" Config. to stop the loss of settings during
# a session when the "Apply" button is clicked which calls quarkx.reloadsetup,
# wiping out all the settings if editor.layout.explorer.selchanged() is used instead.
#
# Revision 1.17  2007/06/04 12:27:01  cdunde
# To update some default settings.
#
# Revision 1.16  2007/05/25 07:44:19  cdunde
# Added new functions to 'Views Options' to set the model's
# mesh lines color and draw in frame selection.
#
# Revision 1.15  2007/05/21 00:05:45  cdunde
# To resize default setting for dialog box.
#
# Revision 1.14  2007/05/18 18:19:32  cdunde
# Fixed console error if Views Options icon button is clicked when the
# dialog is already opened and then try to close it using its 'X' button.
#
# Revision 1.13  2007/05/16 21:45:58  cdunde
# To stop all the handles from being redrawn when just clicking the button to open the 3D Options dialog.
# This also sped up the setting changes substantially. Also fixed and put the close button back in.
#
# Revision 1.12  2007/04/22 22:41:49  cdunde
# Renamed the file mdltools.py to mdltoolbars.py to clarify the files use and avoid
# confliction with future mdltools.py file to be created for actual tools for the Editor.
#
# Revision 1.11  2007/04/05 08:13:39  cdunde
# To add toolbar button links to their Infobase data.
#
# Revision 1.10  2007/04/04 21:34:17  cdunde
# Completed the initial setup of the Model Editors Multi-fillmesh and color selection function.
#
# Revision 1.9  2007/04/01 19:27:19  cdunde
# To remove line commented out.
#
# Revision 1.8  2007/03/30 03:57:25  cdunde
# Changed Model Editor's FillMesh function to individual view settings on Views Options Dialog.
#
# Revision 1.7  2007/03/23 05:26:42  cdunde
# Added a 'Quick Color Options' button to the Model Editors
# modes tool bar for color selection settings.
#
# Revision 1.6  2007/03/22 19:05:43  cdunde
# Removed Model Editors 3D Options dialog Icon X close
# button to stop problems caused when used.
#
# Revision 1.5  2007/01/30 06:43:20  cdunde
# Added more options to the Model Editor View Modes dialog.
#
# Revision 1.4  2007/01/21 20:28:26  cdunde
# Update
#
# Revision 1.3  2007/01/21 01:17:47  cdunde
# To try to fix version numbering.
#
# Revision 1.2  2007/01/21 01:16:47  cdunde
# Changed file setting for cvs.
#
# Revision 1.1  2007/01/21 01:15:47  cdunde
# Renamed from mdllocking.py file.
# To add new Model Editor Views Options button and functions
# and changed file name from mdllocking.py for future items.
#
# Revision 1.8  2006/11/30 01:17:47  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.7  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.6.2.1  2006/11/08 09:24:20  cdunde
# To setup and activate Model Editor XYZ Commands menu items
# and make them interactive with the Lock Toolbar.
#
# Revision 1.6  2005/10/15 00:51:56  cdunde
# To reinstate headers and history
#
# Revision 1.3  2000/10/11 19:09:36  aiv
# added cvs headers
#
#