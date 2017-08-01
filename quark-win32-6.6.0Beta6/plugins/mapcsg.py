"""   QuArK  -  Quake Army Knife

Implementation of the Brush Subtraction commands
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapcsg.py,v 1.11 2006/02/25 03:19:04 cdunde Exp $



Info = {
   "plug-in":       "CSG Brush Subtraction",
   "desc":          "Various polyhedron subtraction commands.",
   "date":          "31 oct 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.1" }


import quarkx
from quarkpy.maputils import *
import quarkpy.qmenu
import quarkpy.mapcommands
import quarkpy.mapentities


def CSGinfo():
    quarkx.msgbox("To subtract a polyhedron\n - from the map : first select the polyhedron;\n - from another : first select them both.\n\nYou can use a group of polyhedrons as subtracter instead of a single polyhedron.\n\nSee also the help (F1) of the Brush substraction menu command.",
      MT_INFORMATION, MB_OK)


def CSG1click(m):
    editor = mapeditor()
    if editor is None: return
    list = editor.visualselection()
    subtracter = editor.layout.explorer.focussel
    if subtracter is None:
        CSGinfo()
        return
    sublist = subtracter.findallsubitems("", ":p")  # find polyhedrons
    if not len(sublist):
        CSGinfo()
        return
    for sel in (list, [editor.Root]):
        plist = []
        for p in sel:
            plist = plist + p.findallsubitems("", ":p")
        for p in sublist:
            try:
                plist.remove(p)
            except:
                pass
        if plist:
            break
    if not plist:
        CSGinfo()
        return

    CSG(editor, plist, sublist, "polyhedron subtraction")



def CSG(editor, plist, sublist, undomsg, undo=None):

    # We compute the subtraction operation

    source = plist
    progr = quarkx.progressbar(508, len(sublist))
    try:
        for p in sublist:
            plist = p.subtractfrom(plist)
            progr.progress()
    finally:
        progr.close()

    # We add the pieces of broken polyhedrons into the map
    if undo is None:
        undo = quarkx.action()
    for p in plist:
        if p.pieceof is not None:    # p comes from a polyhedron in 'source' that was broken into pieces
            undo.put(p.pieceof.parent, p, p.pieceof)
            # we put 'p' into the group that was the parent of the polyhedron
            # whose 'p' is a piece of, and we insert 'p' right before it
            # (it will be removed anyway by the "exchange" command below,
            #  so before or after doesn't matter).

    # If you feel like, you can add code so that when a single polyhedron is broken into
    # several pieces, the pieces are put into a new group. You can also change the name
    # of the pieces (by default, they all have the name of the original polyhedron).

    # We remove the broken polyhedrons
    for p in source:
        if not (p in plist):     # original polyhedron was broken into pieces
            undo.exchange(p, None)   # remove it from the map

    editor.ok(undo, undomsg)

def polyintersects(p1, p2):
    p = quarkx.newobj("test:p")
    for sp in (p1, p2):
        for face in sp.faces:
            p.appenditem(face.copy())
    return len(p.faces)

mat_shrink=quarkx.matrix((0.99,0,0), (0,0.99,0), (0,0,0.99))

#
# CSG for non-map stuff
#
def CSGlist(plist, sublist):

    # We compute the subtraction operation

    source = plist
    progr = quarkx.progressbar(508, len(sublist))
    try:
        for p in sublist:
            tp = p.copy()
            tp.linear(tp.origin, mat_shrink)
 #           tp.shortname="shrunk"
 #           undo = quarkx.action()
 #           undo.put(p.parent,tp,p)

            tplist = plist[:]
            ignored = []
            for targ in tplist[:]:
              if not polyintersects(tp,targ):
                tplist.remove(targ)
                ignored.append(targ)
            plist = p.subtractfrom(tplist)+ignored
            progr.progress()
    finally:
        progr.close()

    # We add the pieces of broken polyhedrons into the map
    for p in plist:
        if p.pieceof is not None:    # p comes from a polyhedron in 'source' that was broken into pieces
            p.pieceof.parent.appenditem(p)
#            undo.put(p.pieceof.parent, p, p.pieceof)
            # we put 'p' into the group that was the parent of the polyhedron
            # whose 'p' is a piece of, and we insert 'p' right before it
            # (it will be removed anyway by the "exchange" command below,
            #  so before or after doesn't matter).

    # If you feel like, you can add code so that when a single polyhedron is broken into
    # several pieces, the pieces are put into a new group. You can also change the name
    # of the pieces (by default, they all have the name of the original polyhedron).

    # We remove the broken polyhedrons
    for p in source:
        if not (p in plist):     # original polyhedron was broken into pieces
#            undo.exchange(p, None)   # remove it from the map
            p.parent.removeitem(p)


#DECKER-begin Code by tiglari
def ExtWall1click(m):
    editor = mapeditor()
    if editor is None: return
    plist = []
    for p in editor.visualselection():
        plist = plist + p.findallsubitems("", ":p")  # find selected polyhedrons
    if not len(plist):
        quarkx.msgbox("This command lets you turn polyhedrons into rooms by extruding walls from their faces. It makes in one or several polyhedrons a room with the same shape.\n\nSelect the polyhedron(s) first. Note that wall thickness can be chosen in the Movement Palette configuration box, under 'Inflate/Deflate'.",
          MT_INFORMATION, MB_OK)
        return
    extrudewalls(editor, plist)

def extrudewalls(editor, plist, wallwidth=None):
    import quarkpy.qmovepal
    wallwidth, = quarkpy.qmovepal.readmpvalues("WallWidth", SS_MAP)
    if wallwidth > 0:           #DECKER
        wallwidth = -wallwidth  #DECKER
    if wallwidth < 0:           #DECKER
        undo = quarkx.action()
        for p in plist:
          newg = quarkx.newobj(p.shortname+" group:g")

    # Added for torus auto remove bulkheads option
          facecount = 0
          tb3 = editor.layout.toolbars["tb_objmodes"]

          for f in p.faces:
            walls = f.extrudeprism(p)

    # Added for torus auto remove bulkheads option
            if tb3.tb.buttons[7].state == 2 and quarkx.setupsubset(SS_MAP, "Options")["QuickObjects_torus_nobulkheads"] == "1":
              if facecount < 2:
                facecount = facecount + 1
                continue

            for wall in walls:
              wall.texturename=f.texturename
            inner = f.copy()
            inner.swapsides()
            outer = f.copy()
            n = f.normal
            n = n.normalized
            outer.translate(abs(wallwidth)*n)
            newp = quarkx.newobj("wall:p")
            for face in walls + [inner, outer]:
              newp.appenditem(face)
            newg.appenditem(newp)
          undo.exchange(p, newg)
        editor.ok(undo,"extrude walls")
    else: #DECKER
        quarkx.msgbox("Error! 'Inflate/Deflate' value is 0.", MT_INFORMATION, MB_OK) #DECKER
#DECKER-end



def Hollow1click(m):
    editor = mapeditor()
    if editor is None: return
    plist = []
    for p in editor.visualselection():
        plist = plist + p.findallsubitems("", ":p")  # find selected polyhedrons
    if not len(plist):
        quarkx.msgbox("This command lets you 'dig' into polyhedrons. It makes in one or several polyhedrons a room with the same shape.\n\nSelect the polyhedron(s) first. Note that wall thickness can be chosen in the Movement Palette configuration box, under 'Inflate/Deflate'.",
          MT_INFORMATION, MB_OK)
        return

    import quarkpy.qmovepal
    wallwidth, = quarkpy.qmovepal.readmpvalues("WallWidth", SS_MAP)

    if wallwidth <= 0:

        sublist = []
        for p in plist:
            new = quarkx.newobj("neg:p")
            for f in p.faces:
                new.appenditem(f.copy())
            new.inflate(wallwidth)
            if not new.broken:
                sublist.append(new)
        if not len(sublist):
            if quarkx.msgbox("Not enough room in the polyhedron(s) to make the hole.\n\nYou can set the wall width in the Movement Palette configuration box, under 'Inflate/Deflate'. Do you want to open this box now ?",
              MT_INFORMATION, MB_YES | MB_NO) == MR_YES:
                quarkpy.qmovepal.ConfigDialog(SS_MAP)
            return
        CSG(editor, plist, sublist, "make hollow")

    else:

        biglist = []
        undo = quarkx.action()
        for p in plist:
            subitems = p.subitems
            for f in p.faces:
                if not (f in subitems):
                    quarkx.msgbox("You cannot inflate a polyhedron with a shared face. Select a negative wall width and try again.",
                      MT_INFORMATION, MB_OK)
                    return
            new = p.copy()
            new.inflate(wallwidth)
            if not new.broken:
                biglist.append(new)
                undo.exchange(p, new)
        CSG(editor, biglist, plist, "make hollow", undo)


def Intersect1click(m):
    editor = mapeditor()
    if editor is None: return
    plist = []
    for p in editor.visualselection():
        plist = plist + p.findallsubitems("", ":p")  # find selected polyhedrons
    if len(plist)<=1:
        quarkx.msgbox("To compute the intersection of two or more polyhedrons, select them all, first.",
          MT_INFORMATION, MB_OK)
        return
    new = quarkx.newobj("intersection:p")
    for p in plist:
        for f in p.faces:
            new.appenditem(f.copy())
    if new.broken:
        quarkx.msgbox("The polyhedrons have no valid intersection.",
          MT_INFORMATION, MB_OK)
        return

    undo = quarkx.action()
    undo.exchange(plist[0], new)
    for p in plist[1:]:
        undo.exchange(p, None)
    editor.ok(undo, "intersection")


def FaceSubinfo():
    quarkx.msgbox("This command works like 'Brush subtraction', except that it produces shared faces. This is useful if you want to edit the subtracted polyhedrons later, but can be confusing if you are not used to shared faces.",
      MT_INFORMATION, MB_OK)


def FaceSub1click(m):
    editor = mapeditor()
    if editor is None: return
    list = editor.visualselection()
    subtracter = editor.layout.explorer.focussel
    if subtracter is None:
        FaceSubinfo()
        return
    sublist = subtracter.findallsubitems("", ":p")  # find polyhedrons
    if not len(sublist):
        FaceSubinfo()
        return
    for p in sublist:
        if p in list:
            list.remove(p)
    if not len(list):
        list = [editor.Root]    # subtract from everything
    plist = []
    for p in list:
        plist = plist + p.findallsubitems("", ":p")
    for p in sublist:
        if p in plist:
            plist.remove(p)
    if not len(plist):
        FaceSubinfo()
        return

    undo = quarkx.action()
    for neg in sublist:
        for p in plist:
            if neg.intersects(p):
                group = quarkx.newobj(p.shortname + ':g')
                for f in p.subitems:
                    group.appenditem(f.copy())
                for f in neg.faces:
                    f1 = f.copy()
                    f1.swapsides()
                    test = quarkx.newobj("test:p")
                    for f2 in p.faces:
                        test.appenditem(f2.copy())
                    test.appenditem(f1.copy())
                    if not test.broken:
                        mini = quarkx.newobj(f.shortname + ':p')
                        mini.appenditem(f1)
                        group.appenditem(mini)
                undo.exchange(p, group)
    editor.ok(undo, "face sharing subtraction")



#--- add the new menu items into the "Commands" menu ---

CSG1 = quarkpy.qmenu.item("&Brush subtraction", CSG1click, "|Brush subtraction:\n\nThis function will subtract one brush from another.\n\nFirst select the brush you want the subtraction to occur on.\nNext select the brush that should be subtracted from the first.\nThen you activate this menu item, or press the accellerator key CTRL+B.\n\nSee the infobase for more detail and other ways to use this function.|intro.mapeditor.menu.html#brushsubtraction")

FaceSub1 = quarkpy.qmenu.item("&Face Sharing subtraction", FaceSub1click, "|Face Sharing subtraction:\n\nA special version of the previous command, 'Brush subtraction'. The small broken pieces will be designed to share common faces, so that you can still resize the broken polyhedron as a whole without having to resize each piece. This command, however, may produce a result that gets a bit confusing.|intro.mapeditor.menu.html#facesharesubtract")

ExtWall1 = quarkpy.qmenu.item("&Extrude walls", ExtWall1click, "|Extrude walls:\n\nThis extrudes walls from the faces, deletes the poly(s).|intro.mapeditor.menu.html#facesharesubtract") #DECKER Code by tiglari

Hollow1 = quarkpy.qmenu.item("&Make hollow", Hollow1click, "|Make hollow:\n\nMakes the selected polyhedron or polyhedrons hollow. If several touching polyhedrons are selected, the whole shape they define will be made hollow.\n\nYou can set the wall width by clicking on the button 'change toolbar settings', under 'inflate/deflate by'. A positive value means extruded polyhedrons, a negative value means digged polyhedrons.|intro.mapeditor.menu.html#facesharesubtract")

Intersect1 = quarkpy.qmenu.item("&Intersection", Intersect1click, "|Intersection:\n\nComputes the intersection of two or more overlapping polyhedrons.\n\nThis is basically a kind of brush adding function. It will try to create a new polyhedron which occupy the common area of the selected polyhedrons.|intro.mapeditor.menu.html#facesharesubtract")

quarkpy.mapcommands.items.append(quarkpy.qmenu.sep)   # separator
quarkpy.mapcommands.items.append(CSG1)
quarkpy.mapcommands.items.append(FaceSub1)
quarkpy.mapcommands.items.append(ExtWall1) #DECKER Code by tiglari
quarkpy.mapcommands.items.append(Hollow1)
quarkpy.mapcommands.items.append(Intersect1)
MapHotKey("Brush Subtraction", CSG1, quarkpy.mapcommands)

#--- add a few items to the polyhedrons pop-up menus ---

def newmenubegin(o, editor, oldmenubegin = quarkpy.mapentities.PolyhedronType.menubegin.im_func):
    return oldmenubegin(o, editor) + [CSG1, Hollow1, quarkpy.qmenu.sep]

quarkpy.mapentities.PolyhedronType.menubegin = newmenubegin


# ----------- REVISION HISTORY ------------
#
# $Log: mapcsg.py,v $
# Revision 1.11  2006/02/25 03:19:04  cdunde
# To fix Torus Hollow-No bulkheads function
# missed with addition of new items.
#
# Revision 1.10  2006/01/17 19:25:45  cdunde
# To add all file updates for new Object modes
# dialog boxes hollowing functions.
#
# Revision 1.9  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.6  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.5  2001/03/29 20:57:45  tiglari
# added 2nd subtraction routime, some tests
#
# Revision 1.4  2001/03/20 08:02:16  tiglari
# customizable hot key support
#
# Revision 1.3.4.1  2001/03/11 22:08:15  tiglari
# customizable hot keys
#
# Revision 1.3  2000/06/03 10:25:30  alexander
# added cvs headers
#
