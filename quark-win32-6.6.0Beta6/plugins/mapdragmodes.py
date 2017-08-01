"""   QuArK  -  Quake Army Knife

Additionnal mouse dragging modes (entity selecter, brush cutter, cube maker)
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapdragmodes.py,v 1.20 2008/07/24 23:34:11 cdunde Exp $



Info = {
   "plug-in":       "Mouse Drag Modes",
   "desc":          "Entity selecter, brush cutter, cube maker.",
   "date":          "28 dec 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.3" }


import quarkx
import quarkpy.qtoolbar
import quarkpy.qhandles
from quarkpy.maputils import *
import quarkpy.maptools
import quarkpy.maphandles
import quarkpy.mapbtns


ico_dict['ico_dragmodes'] = LoadIconSet1("mapdrm", 1.0)


#
# Additionnal drag modes (other plug-ins may add other drag modes).
#

parent = quarkpy.qhandles.RectangleDragObject


class EntRectSelDragObject(parent):
    "A red rectangle that selects the entities it touches."

    Hint = hintPlusInfobaselink("Rectangular selection of ENTITIES||Rectangular selection of ENTITIES:\n\nThis works like 'rectangular selection of polyhedron' (just on the left), but selects entities instead of polyhedrons.", "intro.mapeditor.toolpalettes.mousemodes.html#selectentity")

    def rectanglesel(self, editor, x,y, rectangle):
        if not ("T" in self.todo):
            editor.layout.explorer.uniquesel = None
        entlist = FindSelectable(editor.Root, ":e")
        lastsel = None
        for e in entlist:
            org = e.origin
            if org is None: continue
            for f in rectangle.faces:
                if org*f.normal > f.dist:
                    break
            else: # the point is inside the polyhedron
                e.selected = 1
                lastsel = e
        if lastsel is not None:
            editor.layout.explorer.focus = lastsel
            editor.layout.explorer.selchanged()

class EverythingRectSelDragObject(parent):
    "A red rectangle that selects the entities it touches."

    Hint = hintPlusInfobaselink("Rectangular selection of EVERYTHING||Rectangular selection of EVERYTHING:\n\nThis works like 'rectangular selection of polyhedron' (just on the left), but selects everything including duplicators and beziers.", "intro.mapeditor.toolpalettes.mousemodes.html#selecteverything")

    def rectanglesel(self, editor, x,y, rectangle):
        if not ("T" in self.todo):
            editor.layout.explorer.uniquesel = None
        everythinglist = FindSelectable(editor.Root, None, [":e", ":p", ":d", ":b2"])
        lastsel = None

#needed these next 2 lines because
#Shape Builders were not being selected--cdunde

        polylist = FindSelectable(editor.Root, ":p")
        everythinglist = everythinglist + polylist

        for o in everythinglist:
            if o.type == ":p":
                if rectangle.intersects(o):
                    o.selected = 1
                    lastsel = o
            else:
                org = o.origin
                if org is None: continue
                for f in rectangle.faces:
                    if org*f.normal > f.dist:
                        break
                else: # the point is inside the polyhedron
                    o.selected = 1
                    lastsel = o
        
        #
        # add groups & brush entities whose selectable
        #  subitems are all selected
        #
        brushentitylist = FindSelectable(editor.Root, None, [":g", ":b"])
        for b in brushentitylist:
            subitems = FindSelectable(b,None,[":e", ":p", ":d", ":b2"])
            for e in subitems:
                if not e.selected:
                    break
            else:
                b.selected = 1

        if lastsel is not None:
            editor.layout.explorer.focus = lastsel
            editor.layout.explorer.selchanged()


class CubeMakerDragObject(parent):
    "A cube maker."

    Hint = hintPlusInfobaselink("Quick cube maker||Quick cube maker:\n\nAfter you click this button, you can draw rectangles on the map with the mouse button and these rectangles will be turned into actual cubes. This is a quick way to make a lot of cubes all around.", "intro.mapeditor.toolpalettes.mousemodes.html#createcube")

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

    def rectanglesel(self, editor, x,y, rectangle):
        for f in rectangle.faces:
            #
            # Prepare to set the default texture on the faces
            #
            f.texturename = "[auto]"
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

        quarkpy.mapbtns.dropitemsnow(editor, [rectangle], "new quick cube", "0")


#
# Cube Cutter routines
#

def CubeCut(editor, face, choicefn=lambda face,n1: -abs(face.normal*n1)):
    n = face.normal
    sellist = editor.layout.explorer.sellist
    if len(sellist)==1 and sellist[0].type==':f' and len(sellist[0].faceof):
        #
        # Special : if a face is selected, we build a special structure to fake
        # the cutting of this face in two.
        #
        # First normalize the face texture.
        #
        center = n * face.dist
        v = orthogonalvect(n, editor.layout.views[0])
        #
        # Do it !
        #
        undo = quarkx.action()
        for poly in sellist[0].faceof:
            newgroup = quarkx.newobj(poly.shortname+':g')
            undo.put(poly.parent, newgroup, poly)
            for f in poly.subitems:
                undo.move(f, newgroup)
            for sign in (-128,128):
                newpoly = quarkx.newobj("piece:p")
                for spec,arg in poly.dictspec.items():
                    newpoly[spec] = arg
                newface = sellist[0].copy()
                newpoly.appenditem(newface)
                newface = quarkx.newobj("cut:f")
                newface.texturename = quarkpy.mapbtns.textureof(editor)
                newface.setthreepoints((center, center + v * sign, center + (n^v) * 128), 0)
                newpoly.appenditem(newface)
                undo.put(newgroup, newpoly)
            undo.exchange(poly, None)
        undo.exchange(sellist[0], None)
        editor.ok(undo, "cut face in two")
        return

    sellist = editor.visualselection()
    if len(sellist)==0:
        sellist = [editor.Root]
    elif len(sellist)==1 and sellist[0].type==':g':
        #
        # Special : if a group is selected, we just insert the new face in the group.
        # First ask the user if he agrees...
        #
        todo = quarkx.msgbox("You are cutting a whole group in two parts. Do you want to try making two groups with a single global face for each group ? If you answer No, the selected polyhedrons will be individually cut in two parts.",
          MT_CONFIRMATION, MB_YES_NO_CANCEL)
        if todo == MR_CANCEL: return
        if todo == MR_YES:
            #
            # First normalize the face texture.
            #
            center = n * face.dist
            v = orthogonalvect(n, editor.layout.views[0])
            #
            # Do it !
            #
            undo = quarkx.action()
            newgroup = sellist[0].copy()
            newface = quarkx.newobj("cut:f")
            newface.texturename = quarkpy.mapbtns.textureof(editor)
            newface.setthreepoints((center, center - v * 128, center + (n^v) * 128), 0)
            newgroup.appenditem(newface)
            undo.put(sellist[0].parent, newgroup, sellist[0].nextingroup())
            newface = quarkx.newobj("cut:f")
            newface.texturename = quarkpy.mapbtns.textureof(editor)
            newface.setthreepoints((center, center + v * 128, center + (n^v) * 128), 0)
            undo.put(sellist[0], newface)
            editor.ok(undo, "cut in two groups", [sellist[0], newgroup])
            return

    polylist = []
    for obj in sellist:
        polylist = polylist + obj.findallsubitems("", ':p')    # find all polyhedrons
    #
    # Cut the polyhedrons in polylist
    #
    autoremove = polylist[:]
    undo = quarkx.action()
    for p in polylist:
        if p.intersects(face):
            #
            # We must cut this polyhedron in two parts.
            # Find a "model" face for the new one.
            # This model face must be cutted in two.
            #
            bestface = None
            minnormal = 9
            for f1 in p.faces:
                vtx = f1.verticesof(p)
                gotv1 = vtx[-1]
                prevv = gotv1*n < face.dist
                for v in vtx:
                    nextv = v*n < face.dist    # 0 or 1
                    if prevv+nextv==1:   # the two vertices are not on the same side of the cutting plane
                        gotv2 = v
                        break
                    prevv = nextv
                    gotv1 = v
                else:
                    continue   # this face doesn't cross the cutting plane
                test = choicefn(face, f1.normal)
                if test<minnormal:
                    minnormal = test
                    bestface = f1
                    bestv1 = gotv1
                    bestv2 = gotv2
            if bestface is None:
                continue   # should not occur
            #
            # Build the new face.
            #
            newface = bestface.copy()
            newface.shortname = "cut"
            #
            # Rotate the face to its correct position.
            #
            f = (bestv2*n - face.dist) / (bestv2*n - bestv1*n)
            center = bestv1*f + bestv2*(1-f)   # the intersection of the edge "bestv1->bestv2" with the plane
            newface.distortion(n, center)
            #
            # Insert the new face into the polyhedron.
            #
            undo.put(p, newface)
            #
            # Do it again with the other orientation to make the other half.
            #
            p2 = p.copy()
            newface = bestface.copy()
            newface.shortname = "cut"
            newface.distortion(-n, center)
            p2.appenditem(newface)
            undo.put(p.parent, p2, p.nextingroup())
            autoremove.append(p2)

    editor.ok(undo, "cut in two", autoremove)


class CubeCutter(parent):
    "Cuts polyhedrons in two parts along the line drawn."

    Hint = hintPlusInfobaselink("Cut faces, polyhedrons and groups in two||Cut faces, polyhedrons and groups in two:\n\nAfter you click this button, you can draw lines on the map with the mouse, and any polyhedron touching this line will be cut in two parts along it. This is a quick way to make complex shapes out of a single polyhedron. You can for example draw 3 lines in a wall to make the contour of a passage, and then just delete the middle polyhedron to actually make the hole.\n\nAdvanced features : if you select a face, it will be cut in two but not the other faces of the polyhedron (using \"face sharing\" techniques); and if you select a group, instead of cutting each polyhedron in two individually, QuArK will give you the option of making two copies of the whole group with the cutting plane as a shared face in each group. This lets you consider the cutting plane as a unique face and later move or rotate it to reshape all polyhedrons in the group at once.", "intro.mapeditor.toolpalettes.mousemodes.html#polycutter")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = quarkpy.qhandles.aligntogrid(self.pt0, 1)
        p = view.proj(self.pt0)
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y

    def buildredimages(self, x, y, flags):
        p = self.view.proj(quarkpy.qhandles.aligntogrid(self.view.space(x, y, self.z0), 1))
        if p.visible:
            x = p.x
            y = p.y
        if x==self.x0 and y==self.y0:
            return None, None
        min, max = self.view.depth
        min, max = min*0.99 + max*0.01, min*0.01 + max*0.99
        face = quarkx.newfaceex([
          self.view.space(self.x0, self.y0, min),
          self.view.space(x, y, min),
          self.view.space(x, y, max),
          self.view.space(self.x0, self.y0, max)])
        return None, [face]

    def rectanglesel(self, editor, x,y, face):
        def choice1(face, n1, vertical=self.view.vector(self.pt0).normalized):   # vertical vector at this point
            return abs(n1*vertical)
        CubeCut(editor, face, choice1)



#class TextureCopier(parent):
#    "Copy texture settings by dragging the mouse."
#
#    Hint = "copy texture settings by dragging the mouse"


#
# The tool bar with the available drag modes.
# Add other drag modes from other plug-ins into this list :
#
            #(the_object                            ,icon_index)
DragModes = [(quarkpy.maphandles.RectSelDragObject  ,0)
            ,(EntRectSelDragObject                  ,1)
            ,(EverythingRectSelDragObject           ,5)
            ,(CubeMakerDragObject                   ,2)
            ,(CubeCutter                            ,3)
           #,(TextureCopier                         ,4)
            ]

def selectmode(btn):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    try:
        tb1 = editor.layout.toolbars["tb_dragmodes"]
        tb2 = editor.layout.toolbars["tb_terrmodes"]
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
    quarkx.setupsubset(SS_MAP, "Building").setint("DragMode", btn.i)
    quarkx.setupsubset(SS_MAP, "Building").setint("TerrMode", 20)
    quarkx.setupsubset(SS_MAP, "Building").setint("ObjectMode", 20)

def select1(btn, toolbar, editor):
    editor.MouseDragMode, dummyicon = DragModes[btn.i]
    btn.state = quarkpy.qtoolbar.selected
    editor.layout.explorer.sellist = []
    editor.layout.explorer.uniquesel = []
    editor.layout.explorer.selchanged()
    for view in editor.layout.views:
        if MapOption("CrossCursor", editor.MODE):
            view.cursor = CR_CROSS
            view.handlecursor = CR_ARROW
        else:
            view.cursor = CR_ARROW
            view.handlecursor = CR_CROSS


class DragModesBar(ToolBar):
    "The new toolbar with DragModes buttons."

    Caption = "Mouse modes"
    DefaultPos = ((0, 0, 0, 0), 'topdock', 200, 0, 1)

    def buildbuttons(self, layout):
        btns = []
        for i in range(len(DragModes)):
            obj, icon = DragModes[i]
            btn = qtoolbar.button(selectmode, obj.Hint, ico_dict['ico_dragmodes'], icon)
            btn.i = i
            btns.append(btn)
        i = quarkx.setupsubset(SS_MAP, "Building").getint("DragMode")
   #     if i>=len(DragModes): i=0
        if i == 5:
            leave = 0
        else:
            select1(btns[i], self, layout.editor)
        return btns



#--- register the new toolbar ---

quarkpy.maptools.toolbars["tb_dragmodes"] = DragModesBar


# ----------- REVISION HISTORY ------------
#
# $Log: mapdragmodes.py,v $
# Revision 1.20  2008/07/24 23:34:11  cdunde
# To fix non-ASCII character from causing python depreciation errors.
#
# Revision 1.19  2006/11/30 01:17:48  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.18  2006/11/29 06:58:36  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.17.2.2  2006/11/26 12:54:04  cdunde
# To reset toolbars default location for removal of unneeded 3D buttons.
#
# Revision 1.17.2.1  2006/11/03 23:38:10  cdunde
# Updates to accept Python 2.4.4 by eliminating the
# Depreciation warning messages in the console.
#
# Revision 1.17  2006/01/12 07:21:01  cdunde
# To commit all new and related files for
# new Quick Object makers and toolbar.
#
# Revision 1.16  2005/11/13 10:17:29  cdunde
# Previous fix caused another problem.
# This fix's that cursor setting problem
#
# Revision 1.15  2005/11/13 08:25:07  cdunde
# To finally fix cursor setting problem
#
# Revision 1.14  2005/11/06 23:53:43  cdunde
# Reset toolbar buttons to clear selections to avoid confusion switching
# from button to button and toolbar selectors to toolbar selectors.
#
# Revision 1.13  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.10  2005/08/15 05:48:45  cdunde
# To commit all files for Terrain Generator
#
# Revision 1.9  2005/03/16 10:17:15  cdunde
# To fix non-selection of Shape Builder items for Select Everyting function.
#
# Revision 1.8  2004/01/24 16:28:34  cdunde
# To reset defaults for toolbars
#
# Revision 1.7  2003/03/15 20:40:19  cdunde
# To update hints and add infobase links
#
# Revision 1.6  2001/10/22 10:15:48  tiglari
# live pointer hunt, revise icon loading
#
# Revision 1.5  2001/04/15 22:48:17  tiglari
# groups & brush entity selection in select everything mode (will be selected
#  if all of their subitems are)
#
# Revision 1.4  2001/02/19 19:15:40  decker_dk
# Added 'Select-everything'; entities, brushes, duplicators and beziers.
#
# Revision 1.3  2000/06/03 10:25:30  alexander
# added cvs headers
#

