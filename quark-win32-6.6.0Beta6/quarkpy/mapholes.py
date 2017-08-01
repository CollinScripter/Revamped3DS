"""   QuArK  -  Quake Army Knife

Map editor "Line through hole" displayer
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapholes.py,v 1.9 2005/10/15 00:47:57 cdunde Exp $



#
# This version can only load .lin files from Quake 2.
#

import quarkx
import qmacro
import qtoolbar
from maputils import *
import mapeditor
import mapoptions



class LinesDlg(qmacro.dialogbox):

    #
    # dialog layout
    #

    dfsep = 0.2
    dlgflags = 0

    dlgdef = """
      {
        Style = "15"
        Caption = "...found a hole..."
        sep: = {Typ="S" Bold="0" Txt="There is a hole in your map."}
        sep: = {Typ="S" Bold="0" Txt="Use the red line to locate it,"}
        sep: = {Typ="S" Bold="0" Txt="and then click Ok below."}
        close:py = {Txt="" }
      }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, editor):
        self.editor = editor
        src = quarkx.newobj(":")
        qmacro.dialogbox.__init__(self, form, src,
           close = qtoolbar.button(
              self.close,
              "click here to remove the arrow from your map",
              ico_editor, 0,
              "Ok, hide arrow"))

    def windowrect(self):
        x1,y1,x2,y2 = quarkx.screenrect()
        return (x2-180, 20, x2-15, 132)

    def onclose(self, dlg):
        try:
            del self.editor.LinesThroughHole
            self.editor.invalidateviews()
        except:
            pass
        qmacro.dialogbox.onclose(self, dlg)


def LoadLinFile(editor, filename):
    f = open(filename, "r")
    data = f.readlines()
    f.close()
    pts = []
    for txt in data:
        try:
            pts.append(quarkx.vect(txt))
        except:
            pass
    if len(pts)>=1:
        LinesDlg(editor.form, editor)
        editor.LinesThroughHole = pts
        editor.invalidateviews()


def WateryChecker(editor):
    "Returns a function that checks if a face is watery or not."

    watery = quarkx.setupsubset()["WateryTex"]
    if watery:
        #
        # Quake 1 or Hexen II : faces whose texture name begins with
        # a special symbol (e.g. a star "*") are not solid, so should be ignored.
        #
        filterfn = lambda p, w=watery: p.texturename[:1]==w
    else:
        #
        # Quake 2 : watery faces are determined by "content" flags.
        #
        def filterfn(p, cachetex = {}, texsrc = editor.TexSource):
            s = p["Contents"]
            if s:
                try:
                    return int(s) & 16777336     # some flags that define non-blocking polyhedrons
                except:
                    return 0
            try:
                return cachetex[p.texturename]
            except:
                tex = p.texturename
                texobj = quarkx.loadtexture(tex, texsrc)
                if texobj is not None:
                    try:
                        texobj = texobj.disktexture
                    except quarkx.error:
                        texobj = None
                result = 1
                if texobj is not None:
                    s = texobj["Contents"]
                    try:
                        result = int(s) & 16777336     # some flags that define non-blocking polyhedrons
                    except:
                        result = 0
                cachetex[tex] = result
                return result

    return filterfn


def SearchForHoles(editor):
    polys = filter(lambda p, watery=WateryChecker(editor): not watery(p.faces[0]), editor.Root.listpolyhedrons)
    pts = quarkx.searchforholes(polys, editor.Root.listentities)
    if pts is None:
        quarkx.msgbox("No hole found.", MT_INFORMATION, MB_OK)
    else:
        LinesDlg(editor.form, editor)
        editor.LinesThroughHole = pts
        editor.invalidateviews()



def DrawLines(editor, view, oldFinishDrawing = mapeditor.MapEditor.finishdrawing):
    try:
        points = editor.LinesThroughHole
        cv = view.canvas()
        cv.pencolor = MapColor("Tag")
        cv.penwidth = mapoptions.getLineThickness()
        if len(points)==1:
            pt0 = view.proj(points[0])
            if pt0.visible:
                cv.line(pt0.x-5, pt0.y-5, pt0.x+6, pt0.y+6)
                cv.line(pt0.x-5, pt0.y+5, pt0.x+6, pt0.y-6)
        else:
            Arrow(cv, view, points[1], points[0])
            pt0 = view.proj(points[1])
            for p in points[2:]:
                pt1 = view.proj(p)
                cv.line(pt0, pt1)
                pt0 = pt1
    except AttributeError:
        pass
    oldFinishDrawing(editor, view)


mapeditor.MapEditor.finishdrawing = DrawLines

# ----------- REVISION HISTORY ------------
#
#
#$Log: mapholes.py,v $
#Revision 1.9  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.6  2003/03/21 10:56:08  tiglari
#support for line-thickness specified by mapoption
#
#Revision 1.5  2003/03/19 22:27:10  tiglari
#remove debug; there was no parsing error in this file (previous commit mistaken)
#
#Revision 1.4  2003/03/19 22:23:35  tiglari
#fix bug in parsing
#
#Revision 1.3  2001/06/17 21:05:27  tiglari
#fix button captions
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#