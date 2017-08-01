"""   QuArK  -  Quake Army Knife

A tricky "force-the-whole-map-polyhedrons-to-grid"
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/map2grid.py,v 1.8 2005/10/15 00:49:51 cdunde Exp $



Info = {
   "plug-in":       "Force All Polyhedrons to grid",
   "desc":          'A tricky "force-the-whole-map-polyhedrons-to-grid".',
   "date":          "11 feb 99",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.6" }


import quarkx
from quarkpy.maputils import *
import quarkpy.qmenu
import quarkpy.mapcommands
import quarkpy.qmacro


class TFTGDlg (quarkpy.qmacro.dialogbox):

    #
    # dialog layout
    #

    size = (350, 260)
    dfsep = 0.4        # separation at 40% between labels and edit boxes
    dlgflags = FWF_KEEPFOCUS

    dlgdef = """
        {
            Style = "15"
        Caption = "Tricky Force to Grid"
        sep: = {Typ="S" Txt=" "}
            info: = {Typ="S" Bold="0" Txt="Use this to detect and repair slightly off-the-grid polyhedrons."}
            info: = {Typ="S" Bold="0" Txt="Warning ! This is a bad trick and should only be used to repair"}
            info: = {Typ="S" Bold="0" Txt="maps that are really messed up ! You should make a backup copy"}
            info: = {Typ="S" Bold="0" Txt="of your map before proceeding..."}
        sep: = {Typ="S" Txt=" "}
        epsilon: =
        {
        Txt = "Move not more than"
        Typ = "EF1"
        SelectMe = "1"
        }
            nepsilon: =
            {
                Txt = "Normal at least"
                Typ = "EF1"
            }
        sep: = { Typ = "S" Txt=""}
        ok1:py = {Txt="" }
        //ok2:py = {Txt="" }
            cancel:py = {Txt="" }
    }
    """

    def __init__(self, form, editor):
        self.editor = editor
        src=quarkx.newobj(":")
        src["epsilon"] = 0.01,
        src["nepsilon"] = 0.99,
        quarkpy.qmacro.dialogbox.__init__(self, form, src,
        ok1 = quarkpy.qtoolbar.button(
                self.TFTG,
                "force all faces to match the grid",
                ico_editor, 2,
                "Force Faces"),
        #ok2 = quarkpy.qtoolbar.button(
            #    self.TFTG,
            #    "do it",
            #    ico_editor, 2,
            #    "Force Faces"),
        cancel = quarkpy.qtoolbar.button(
            self.close,
            "close this box",
            ico_editor, 0,
            "Cancel"))

    def TFTG(self, btn):
        editor = self.editor
        flist = editor.Root.findallsubitems("", ':f')    # all faces
        grid = editor.gridstep
        if not grid:
            grid = 1.0
        quarkx.globalaccept()
        epsilon, = self.src["epsilon"]
        nepsilon, = self.src["nepsilon"]
        def fix(f):
            if f>0:
                return 1
            else:
                return -1
        undo = quarkx.action()
        for f in flist:
            if f.broken: continue
           # tp = list(f.threepoints(0))
           # change = 0
           # for i in range(3):
           #     v = list(tp[i].tuple)
           #     for j in range(3):
           #         test = v[j]/grid
           #         if test != int(test):
           #             delta = test-int(test)
           #             if delta>0.5: delta = delta-1
           #             if abs(delta)<epsilon:
           #                 v[j] = int(test+0.5)*grid
           #                 change = 1
           #     tp[i] = quarkx.vect(v[0], v[1], v[2])
           # if change:
           #     new = f.copy()
           #     new.setthreepoints((tp[0], tp[1], tp[2]), 0)
           #     undo.exchange(f, new)

            new = None
            n = f.normal
            if not n: continue
            n = n.normalized
            if abs(n.x)==1:
                dir = 0
            elif abs(n.y)==1:
                dir = 1
            elif abs(n.z)==1:
                dir = 2
            elif abs(n.x)>nepsilon:
                new = f.copy()
                new.distortion(quarkx.vect(fix(n.x), 0, 0), f.origin)
                dir = 0
            elif abs(n.y)>nepsilon:
                new = f.copy()
                new.distortion(quarkx.vect(0, fix(n.y), 0), f.origin)
                dir = 1
            elif abs(n.z)>nepsilon:
                new = f.copy()
                new.distortion(quarkx.vect(0, 0, fix(n.z)), f.origin)
                dir = 2
            else:
                continue
            if new is None:
                k = f
            else:
                k = new
            p1, p2, p3 = k.threepoints(0)
            v = p1.tuple
            test = v[dir]/grid
            if test != int(test):
                delta = test-int(test)
                if delta>0.5: delta = delta-1
                if abs(delta)<epsilon:
                    v = [0,0,0]
                    v[dir] = -grid*delta
                    if new is None: new = f.copy()
                    new.translate(quarkx.vect(tuple(v)))
            if new is not None:
                undo.exchange(f, new)
        editor.ok(undo, "Faces To Grid")
        self.close()


def TFTGclick (m):
    editor = mapeditor ()
    if editor is None: return
    TFTGDlg(quarkx.clickform, editor)


#--- add the new menu item into the "Commands" menu ---

quarkpy.mapcommands.items.append(quarkpy.qmenu.sep)   # separator
quarkpy.mapcommands.items.append(
  quarkpy.qmenu.item("Tricky force to grid...", TFTGclick, "|Tricky force to grid:\n\nRepairs maps that are off-the-grid.|intro.mapeditor.menu.html#commandsmenu"))


# ----------- REVISION HISTORY ------------
#
#
# $Log: map2grid.py,v $
# Revision 1.8  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.5  2003/09/14 05:57:08  cdunde
# Typ separator correction
#
# Revision 1.4  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.3  2001/06/17 21:10:57  tiglari
# fix button captions
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#