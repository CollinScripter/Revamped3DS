"""   QuArK  -  Quake Army Knife

Implementation of the menu commands related to faces
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapfacemenu.py,v 1.9 2005/10/15 00:49:51 cdunde Exp $


Info = {
   "plug-in":       "Face Menu",
   "desc":          "Various polyhedron face menu commands.",
   "date":          "1 nov 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.1" }


import math
import quarkx
from quarkpy.maputils import *
import quarkpy.qmenu
import quarkpy.qtoolbar
import quarkpy.qhandles
import quarkpy.mapcommands
import quarkpy.mapentities
import quarkpy.maphandles
import quarkpy.qmacro



def ForceAngle(m):
    editor = mapeditor()
    if editor is None: return
    obj = editor.layout.explorer.uniquesel
    if obj is None: return
    new = None
    if obj.type == ':f':   # face
        normal = quarkpy.qhandles.alignanglevect(obj.normal, SS_MAP)
        new = obj.copy()
        new.distortion(normal, obj.origin)
    elif obj.type == ':b' or obj.type == ':e':
        for spec, cls in quarkpy.mapentities.ListAngleSpecs(obj):
            s = obj[spec]
            if s:
                stov, vtos = cls.map
                try:
                    normal = stov(s)
                except:
                    continue
                normal = quarkpy.qhandles.alignanglevect(normal, SS_MAP)
                new = obj.copy()
                new[spec] = vtos(normal)
                break
    if new is not None:
        undo = quarkx.action()
        undo.exchange(obj, new)
        editor.ok(undo, "force angle")



class Orientation(quarkpy.qmacro.dialogbox):

    endcolor = PURPLE
    size = (300,140)
    dfsep = 0.4
    dlgdef = """
      {
        Style = "9"
        Caption = "Face orientation"
        sep: = {Typ="S" Txt=" "}    // some space
        compass: = {
          Txt=" Compass angle :"
          Typ="EF1"
          SelectMe="1"
          Hint="Direction (on compass) towards which the side points"
        }
        incline: = {
          Txt=" Incline :"
          Typ="EF1"
          Hint="positive: toward up,  negative: toward down"
        }
        sep: = {Typ="S" Txt=" "}    // some space
        sep: = {Typ="S" Txt=""}    // a separator line
        cancel:py = {Txt="" }
      }
    """

    def __init__(self, m):
        self.face = None
        src = quarkx.newobj(":")
        quarkpy.qmacro.dialogbox.__init__(self, quarkx.clickform, src,
          cancel = quarkpy.qtoolbar.button(self.close, "close this box", ico_editor, 0, "Close"))
        editor = mapeditor()
        if editor is None: return
        face = editor.layout.explorer.uniquesel
        if (face is None) or (face.type != ':f'): return

        pitch, roll, yaw = quarkpy.qhandles.vec2angles1(face.normal)
        src["compass"] = roll,
        src["incline"] = pitch,
        self.editor = editor
        self.face = face

    def datachange(self, df):
        if self.face is not None:
            roll = self.src["compass"]
            pitch = self.src["incline"]
            if (roll is not None) and (pitch is not None):
                normal = apply(quarkpy.qhandles.angles2vec1, pitch + roll + (0,))
                new = self.face.copy()
                new.distortion(normal, self.face.origin)
                undo = quarkx.action()
                undo.exchange(self.face, new)
                self.editor.ok(undo, "set orientation")
                self.face = new



def deleteside(m):
    editor = mapeditor()
    if editor is None: return
    face = editor.layout.explorer.uniquesel
    if (face is None) or (face.type != ':f'): return
    for poly in face.faceof:
        if poly.type == ':p':
            test = quarkx.newobj("test:p")
            for f in poly.faces:
                if f != face:
                    test.appenditem(f.copy())
            if test.broken:
                if quarkx.msgbox("Without this face, the polyhedron(s) will no longer be closed. You can continue, but the polyhedron(s) will be broken as long as you don't close it again.", MT_WARNING, MB_OK_CANCEL) != MR_OK:
                    return
                break
    undo = quarkx.action()
    undo.exchange(face, None)
    editor.ok(undo, "delete face")


def makecone(m):
    editor = mapeditor()
    if editor is None: return
    face = editor.layout.explorer.uniquesel
    if (face is None) or (face.type != ':f'): return

    poly = face.parent
    if poly.type != ':p':     # can't conify shared faces
        quarkx.msgbox("Cannot build a cone from a shared face.", MT_ERROR, MB_OK)
        return
    normal = face.normal
    d1 = map(lambda f,n1=normal: f.normal*n1, filter(lambda f,f0=face: f!=f0, poly.faces))
    d1.append(0.0)
    d0 = min((max(d1), 0.95))
    d1 = math.sqrt(1-d0*d0)
    n0 = normal*(d0+1.0)

    undo = quarkx.action()
    vertices = face.verticesof(poly)
    v0 = vertices[-1]
    for v1 in vertices:
        n = (n0 + d1*(normal^(v1-v0)).normalized).normalized
        f = face.copy()
        f.distortion(n, v0)
        undo.put(poly, f, face)
        v0 = v1
    undo.exchange(face, None)
    editor.ok(undo, "conify")


warnonce = 1

def swapsides(m):
    editor = mapeditor()
    if editor is None: return
    face = editor.layout.explorer.uniquesel
    if (face is None) or (face.type != ':f'): return

    global warnonce
    if warnonce:
        if quarkx.msgbox("This command will return the face inside out. It is rarely used, and it is likely to break polyhedrons. Try it anyway, and keep in mind that you can always undo everything.",
          MT_WARNING, MB_OK_CANCEL) == MR_CANCEL:
            return
        warnonce = 0

    undo = quarkx.action()
    new = face.copy()
    new.swapsides()
    undo.exchange(face, new)
    undo.ok(editor.Root, "swap sides")


def vec2rads(v):
    "returns pitch, yaw, in radians"
    v = v.normalized
    import math
    pitch = -math.sin(v.z)
    yaw = math.atan2(v.y, v.x)
    return pitch, yaw

def find3DView(editor):
    views = []
    for v in editor.layout.views:
        if v.info["type"]=="3D":
            views.append(v)
    if views == []:
        return
    return views[0]

def LookAtMe(m):
    editor=mapeditor()
    face = editor.layout.explorer.uniquesel
    if quarkx.keydown('\020')==1: # shift is down
        reverse = 1
    else:
        reverse = 0
    clickview = quarkx.clickform.focus 
    #
    # clickform doesn't seem to work for floating 3d windows
    #  so we just take the first.
    #
    if clickview is not None and clickview.info["type"]=="3D":
        view = clickview
    else:
        view = find3DView(editor)
        if view is None:
            quarkx.msgbox("Need an open 3D view for this one!",
               MT_ERROR,MB_OK)
            return
    #
    # Should have a 3D view here
    #
    pos, yaw, pitch = view.cameraposition
    dist = abs(pos - face.origin)
    if reverse:
        norm = -face.normal
    else:
        norm = face.normal
    newpos = face.origin+dist*(norm)
    pitch, yaw = vec2rads(-norm)
    view.cameraposition = newpos, yaw, pitch
    editor.invalidateviews()
    

#--- add the new menu items into the "Commands" menu ---

ForceAngle1 = quarkpy.qmenu.item("&Adjust angle", ForceAngle,"|Adjust angle:\n\nThis is only active when you have selected a face. This will bring the angle of the face on the polyhedron, to the nearest angle by which you specified in the 'Building'.|intro.mapeditor.menu.html#orientation")

Orientation1 = quarkpy.qmenu.item("&Orientation...", Orientation,"|Orientation:\n\nThis is only active when you have selected a face. It will bring up a window where you can edit some attribures about the face.\n\nHowever, its not recommended that you do it this way, unless you know what you're doing!|intro.mapeditor.menu.html#orientation")

DeleteSide1 = quarkpy.qmenu.item("&Delete face", deleteside,"|Delete face:\n\nAs it says. However, deleting a face will very likely make a polyhedron invalid.|intro.mapeditor.menu.html#orientation")

MakeCone1 = quarkpy.qmenu.item("&Cone over face", makecone,"|Cone over face:\n\nThis will create a new set of faces in style as a cone, over the selected face. The number of new faces will be the number of edges the selected face has.|intro.mapeditor.menu.html#orientation")

SwapSides1 = quarkpy.qmenu.item("&Swap face sides", swapsides,"|Swap face sides:\n\nWill swap the face inside-out. Do not use this, unless you really want to!|intro.mapeditor.menu.html#orientation")

LookAt1 = quarkpy.qmenu.item("Look &At", LookAtMe, "|Look At:\n\nAn open 3D view shifts to look at this face head on.\n (SHIFT to look at the face from the back)|intro.mapeditor.menu.html#orientation")

quarkpy.mapcommands.items.append(quarkpy.qmenu.sep)   # separator
quarkpy.mapcommands.items.append(Orientation1)
quarkpy.mapcommands.items.append(ForceAngle1)
quarkpy.mapcommands.items.append(DeleteSide1)
quarkpy.mapcommands.items.append(MakeCone1)
quarkpy.mapcommands.items.append(SwapSides1)
quarkpy.mapcommands.items.append(LookAt1)


def newclick(popup, oldclick = quarkpy.mapcommands.onclick):
    editor = mapeditor()
    if editor is None: return
    obj = editor.layout.explorer.uniquesel
    ForceAngle1.state = (obj is None or not (obj.type in (':f', ':e', ':b'))) and qmenu.disabled
    faceonly = (obj is None or (obj.type != ':f')) and qmenu.disabled
    Orientation1.state = faceonly
    DeleteSide1.state = faceonly
    MakeCone1.state = faceonly
    SwapSides1.state = faceonly
    LookAt1.state = faceonly
    oldclick(popup)

quarkpy.mapcommands.onclick = newclick



#-- add the new menu items into the face pop-up menu --

def newmenu(o, editor, oldmenu = quarkpy.mapentities.FaceType.menu.im_func):
    Orientation1.state = 0
    DeleteSide1.state = 0
    MakeCone1.state = 0
    return oldmenu(o, editor) + [Orientation1, DeleteSide1, MakeCone1, LookAt1]

quarkpy.mapentities.FaceType.menu = newmenu


# ----------- REVISION HISTORY ------------
#
#
# $Log: mapfacemenu.py,v $
# Revision 1.9  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.6  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.5  2001/06/17 21:10:57  tiglari
# fix button captions
#
# Revision 1.4  2001/06/16 03:29:36  tiglari
# add Txt="" to separators that need it
#
# Revision 1.3  2001/02/20 21:30:20  tiglari
# LookAt added
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#