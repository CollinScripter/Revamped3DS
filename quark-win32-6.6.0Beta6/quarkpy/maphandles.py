# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

Map editor mouse handles.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"

#$Header: /cvsroot/quark/runtime/quarkpy/maphandles.py,v 1.73 2008/09/29 21:59:51 danielpharos Exp $



#
# This module manages the map "handles", i.e. the small active areas
# that can be grabbed and dragged by the user on the map views.
#
# Generic handles are implemented in qhandles.py. This modules has
# only the map-editor-specific handles.
#

#py2.4 indicates upgrade change for python 2.4

import quarkx
import math
from qdictionnary import Strings
import qhandles
from maputils import *
import mapentities
import qmacro

from plugins.tagging import *

#
# The handle classes.
#

class CenterHandle(qhandles.CenterHandle):
    "Like qhandles.CenterHandle, but specifically for the map editor."
    def menu(self, editor, view):
        #
        # FIXME: this is a pretty clunky way of making the
        #  clicked on view available to entity menus, mebbe
        #  should be cleaned up (view as 3rd parameter to entity
        #  menus, perhaps?)
        #
        try:
            editor.layout.clickedview = view
        except:
            editor.layout.clickedview = None
        return mapentities.CallManager("menu", self.centerof, editor) + self.OriginItems(editor, view)

class IconHandle(qhandles.IconHandle):
    "Like qhandles.IconHandle, but specifically for the map editor."
    def menu(self, editor, view):
        return mapentities.CallManager("menu", self.centerof, editor) + self.OriginItems(editor, view)


class PointSpecHandle(qhandles.CenterHandle):
    "3D point0 handle-like Specifics."

    def __init__(self, pos, entity, spec):
        qhandles.CenterHandle.__init__(self, pos, entity)
        self.entity = entity
        self.spec = spec

    def drag(self, v1, v2, flags, view):
        delta = v2-v1
        if flags&MB_CTRL:
            g1 = grid[1]
        else:
            delta = qhandles.aligntogrid(delta, 0)
            g1 = 0
        self.draghint = vtohint(delta)
        if delta or (flags&MB_REDIMAGE):
            new=self.entity.copy()
            s=new[self.spec]
            if s:
              pointpos=quarkx.vect(s)
              pointpos= pointpos + delta
              new[self.spec]=str(pointpos)
              new=[new]
            else:
              new = None
        else:
            new = None
        return [self.entity],new


def CenterEntityHandle(o, view, handleclass=IconHandle, pos=None):
    if pos is None:
        pos = o.origin
    if pos is not None:
        #
        # Compute a handle for the entity angle.
        #
        h = []
        #
        for spec, cls in mapentities.ListAngleSpecs(o):
            s = o[spec]
            if s:
                stov, vtos = cls.map
                try:
                    normal = stov(s)
                except:
                    continue
                h = [cls(pos, normal, view.scale(), o, spec)]
                break
        #
        # Build a "circle" icon handle at the object origin.
        #
        new = handleclass(pos, o)   # the "circle" icon would be qhandles.mapicons[10], but it looks better with the entity icon itself
        #
        # Set the hint as the entity classname in blue ("?").
        #
        new.hint = "?" + o.shortname + "||This point represents an entity, i.e. an object that appears and interacts in the game when you play the map. The exact kind of entity depends on its 'classname' (its name).\n\nThis handle lets you move the entity with the mouse. Normally, the movement is done by steps of the size of the grid : if the entity was not aligned on the grid before the movement, it will not be after it. Hold down Ctrl to force the entity to the grid.|maped.duplicators.extruder.html"

        #
        # Compute a handle for aditional control points.
        #
        hp = []

        for spec in mapentities.ListAddPointSpecs(o):
            s = o[spec]
            if s:
                pointpos=quarkx.vect(s)
                obj=PointSpecHandle(pointpos, o, spec)
                obj.hint=spec
                hp.append(obj)
        #
        # Return the handle
        #
        return h+[new]+hp

    else:
        #
        # No "origin".
        #
        return []



class FaceHandleCursor:
    "Special class to compute the mouse cursor shape based on the visual direction of a face."

    def getcursor(self, view):
        n = view.proj(self.pos + self.face.normal) - view.proj(self.pos)
        dx, dy = abs(n.x), abs(n.y)
        if dx*2<=dy:
            if (dx==0) and (dy==0):
                return CR_ARROW
            else:
                return CR_SIZENS
        elif dy*2<=dx:
            return CR_SIZEWE
        elif (n.x>0)^(n.y>0):
            return CR_SIZENESW
        else:
            return CR_SIZENWSE


def completeredimage(face, new):
    #
    # Complete a red image with the whole polyhedron.
    # (red images cannot be reduced to a single face; even if
    #  we drag just a face, we want to see the whole polyhedron)
    #
    gr = []
    for src in face.faceof:
        if src.type == ":p":
            poly = quarkx.newobj("redimage:p")
            t = src
            while t is not None:
                for q in t.subitems:
                    if (q.type==":f") and not (q is face):
                         poly.appenditem(q.copy())
                t = t.treeparent
            poly.appenditem(new.copy())
            gr.append(poly)
    if len(gr):
        return gr
    else:
        return [new]



class FaceHandle(qhandles.GenericHandle):
    "Center of a face."

    undomsg = Strings[516]
    hint = "move this face (Ctrl key: force center to grid)||This handle lets you scroll this face, thus distort the polyhedron(s) that contain it.\n\nNormally, the face can be moved by steps of the size of the grid; holding down the Ctrl key will force the face center to be exactly on the grid."

    def __init__(self, pos, face):
        qhandles.GenericHandle.__init__(self, pos)
        self.face = face
        cur = FaceHandleCursor()
        cur.pos = pos
        cur.face = face
        self.cursor = cur.getcursor

    def menu(self, editor, view):
        self.click(editor)
        return mapentities.CallManager("menu", self.face, editor) + self.OriginItems(editor, view)

    def drag(self, v1, v2, flags, view):
        delta = v2-v1
        g1 = 1
        if flags&MB_CTRL:
            pos0 = self.face.origin
            if pos0 is not None:
                pos1 = qhandles.aligntogrid(pos0+delta, 1)
                delta = pos1 - pos0
                g1 = 0
        if g1:
            delta = qhandles.aligntogrid(delta, 0)

        s = ""
        if view.info["type"] == "XY":
            if abs(self.face.normal.tuple[0]) > abs(self.face.normal.tuple[1]):
                s = "was x: " + ftoss(v1.x) + " now x: " + ftoss(v1.x+delta.x)
            else:
                s = "was y: " + ftoss(v1.y) + " now y: " + ftoss(v1.y+delta.y)
        elif view.info["type"] == "XZ":
            if abs(self.face.normal.tuple[0]) > abs(self.face.normal.tuple[2]):
                s = "was x: " + ftoss(self.pos.x) + " now x: " + ftoss(self.pos.x+delta.x)
            else:
                s = "was z: " + ftoss(self.pos.z) + " now z: " + ftoss(self.pos.z+delta.z)
        elif view.info["type"] == "YZ":
            if abs(self.face.normal.tuple[1]) > abs(self.face.normal.tuple[2]):
                s = "was y: " + ftoss(self.pos.y) + " now y: " + ftoss(self.pos.x+delta.y)
            else:
                s = "was z: " + ftoss(self.pos.z) + " now z: " + ftoss(self.pos.z+delta.z)
        if s == "":
            if self.face.normal.tuple[0] == 1 or self.face.normal.tuple[0] == -1:
                s = "was x: " + ftoss(self.pos.x) + " now x: " + ftoss(self.pos.x+delta.x)
            elif self.face.normal.tuple[1] == 1 or self.face.normal.tuple[1] == -1:
                s = "was y: " + ftoss(self.pos.y) + " now y: " + ftoss(self.pos.y+delta.y)
            elif self.face.normal.tuple[2] == 1 or self.face.normal.tuple[2] == -1:
                s = "was z: " + ftoss(self.pos.z) + " now z: " + ftoss(self.pos.z+delta.z)
            else:
                s = "was: " + vtoposhint(self.pos) + " now: " + vtoposhint(delta + self.pos)
        self.draghint = s

        if delta or (flags&MB_REDIMAGE):
            new = self.face.copy()
            if self.face.faceof[0].type == ":p":
                delta = self.face.normal * (self.face.normal*delta)  # projection of 'delta' on the 'normal' line
            new.translate(delta)
            if flags&MB_DRAGGING:    # the red image contains the whole polyhedron(s), not the single face
                new = completeredimage(self.face, new)
            else:
                new = [new]
        else:
            new = None
        return [self.face], new

    def leave(self, editor):
        src = self.face.faceof
        if (len(src)==1) and (src[0].type == ":p"):
            editor.layout.explorer.uniquesel = src[0]


class PFaceHandle(FaceHandle):
    "Center of a face, but unselected (as part of a selected poly)."

    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = view.darkcolor
#py2.4            cv.rectangle(p.x-3, p.y-3, p.x+4, p.y+4)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)

    def click(self, editor):
        editor.layout.explorer.uniquesel = self.face
        return "S"

    def leave(self, editor):
        pass



class MapRotateHandle(qhandles.Rotate3DHandle):
    "Like Rotate3DHandle, but specifically for the map editor."

    MODE = SS_MAP



class FaceNormalHandle(MapRotateHandle):
    "3D rotating handle, for faces."

    undomsg = Strings[517]
    hint = "rotate this face (Ctrl key: force to a common angle)||This handle lets you rotate the face around its center. Use it to distort the polyhedron(s).\n\nYou can set any angle unless you hold down the Ctrl key; in this case, you can only set 'round' angle values. See the Configuration dialog box, Map, Display."

    def __init__(self, center, vtx, face, scale1):
        MapRotateHandle.__init__(self, center, face.normal, scale1, qhandles.mapicons[11])
        self.face = face
        self.vtx = vtx

    def menu(self, editor, view):
        return qmenu.catmenus(MapRotateHandle.menu(self, editor, view),
          mapentities.CallManager("menu", self.face, editor))

    def draw(self, view, cv, draghandle=None):
        cv.reset()
        p1, p2 = view.proj(self.center), view.proj(self.pos)
        fromback = view.vector(self.center)*self.face.normal < 0
        if fromback:
            self.draw1(view, cv, p1, p2, 1)
            if p1.visible:
#py2.4                cv.rectangle(p1.x-3, p1.y-3, p1.x+4, p1.y+4)
                cv.rectangle(int(p1.x)-3, int(p1.y)-3, int(p1.x)+4, int(p1.y)+4)
        else:
            oldpc = cv.pencolor
        cv.pencolor = YELLOW
        for v in self.vtx:
            p = view.proj(v)
            cv.line(p, p1)
        if not fromback:
            cv.pencolor = oldpc
            if p1.visible:
#py2.4                cv.rectangle(p1.x-3, p1.y-3, p1.x+4, p1.y+4)
                cv.rectangle(int(p1.x)-3, int(p1.y)-3, int(p1.x)+4, int(p1.y)+4)
            self.draw1(view, cv, p1, p2, 0)
        view.drawmap(self.face, 0)

    def dragop(self, flags, av):
        new = None
        if av is not None:
            new = self.face.copy()
            new.distortion(av, self.center)
            if flags&MB_DRAGGING:    # the red image contains the whole polyhedron(s), not the single face
                new = completeredimage(self.face, new)
            else:
                new = [new]
        return [self.face], new, av



class Angles3DHandle(MapRotateHandle):
    "3D rotating handle, for 'angles'-like Specifics."

    hint = "entity pointing angle (any 3D direction)||Lets you set the direction the entity is 'looking' at. Hold down Ctrl to force the angle to some 'round' value."
    map = (qhandles.angles2vec, qhandles.vec2angles)
    ii = 12

    def __init__(self, pos, normal, scale1, entity, spec):
        MapRotateHandle.__init__(self, pos, normal, scale1, qhandles.mapicons[self.ii])
        self.entity = entity
        self.spec = spec

    def menu(self, editor, view):
        return qmenu.catmenus(MapRotateHandle.menu(self, editor, view),
          mapentities.CallManager("menu", self.entity, editor))

    def dragop(self, flags, av):
        new = None
        if av is not None:
            stov, vtos = self.map
            new = self.entity.copy()
            s = vtos(av, new[self.spec])
            av = stov(s)
            new[self.spec] = s
            new = [new]
        return [self.entity], new, av


class Angle2DHandle(Angles3DHandle):
    "2D rotating handle, for 'angle'-like Specifics."

    hint = "entity pointing angle (2D direction only, or up or down)||Lets you set the direction the entity is 'looking' at. This has various meaning for various entities : for most ones, it is the direction it is facing when the map starts; for buttons or doors, it is the direction the button or door moves.\n\nYou can set any horizontal angle, as well as 'up' and 'down'. Hold down Ctrl to force the angle to a 'round' value."
    map = (qhandles.angle2vec, qhandles.vec2angle)
    ii = 13



class PolyHandle(CenterHandle):
    "Center of polyhedron Handle."

    undomsg = Strings[515]
    hint = "move polyhedron (Ctrl key: force center to grid)||Lets you move this polyhedron.\n\nYou can move it by steps equal to the grid size. This means that if it is not on the grid now, it will not be after the move, either. You can force it on the grid by holding down the Ctrl key, but be aware that this forces its center to the grid, not all its faces. For cubic polyhedron, you may need to divide the grid size by two before you get the expected results."

    def __init__(self, pos, centerof):
        CenterHandle.__init__(self, pos, centerof, 0x202020, 1)

    def click(self, editor):
        if not self.centerof.selected:   # case of the polyhedron center handle if only a face is selected
            editor.layout.explorer.uniquesel = self.centerof
            return "S"



#
# if vtxes contains a point close to the line thru v along axis, return
#  it, otherwise v+axis
#
def getotherfixed(v, vtxes, axis):
    for v2 in vtxes:
        if not (v-v2):
            continue;
        perp = perptonormthru(v2,v,axis.normalized)
        if abs(perp)<.05:
            return v2
    return v+axis


#
# A handle for edges
#
class EdgeHandle(qhandles.GenericHandle):
    undomsg = "drag edge"
    hint = "tag this edge for lining up objects, etc."

    def __init__(self, face, vtx1, vtx2):
        pos = (vtx2+vtx1)/2
        qhandles.GenericHandle.__init__(self, pos)
        self.face = face
        self.vtx1, self.vtx2 = vtx1, vtx2
        cur = FaceHandleCursor()
        cur.pos = pos
        cur.face = face
        self.cursor = cur.getcursor

    def menu(self, editor, view):
        self.click(editor)
        editor.layout.clickedview = view
        return self.OriginItems(editor, view)

    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        oldcolor = cv.pencolor
        p1 = view.proj(self.vtx1)
        p2 = view.proj(self.vtx2)
        cv.pencolor = oldcolor
        if p.visible:
            cv.reset()
            cv.brushcolor = view.darkcolor
            radius = 3
#py2.4            cv.ellipse(p.x-radius, p.y-radius, p.x+radius+1, p.y+radius+1)
            cv.ellipse(int(p.x)-radius, int(p.y)-radius, int(p.x)+radius+1, int(p.y)+radius+1)
#            cv.rectangle(p.x-3, p.y-3, p.x+4, p.y+4)

#1class SpecialHandle(FaceHandle):
#2class SpecialHandle(PointSpecHandle):
class SpecialHandle(Angles3DHandle):
    "Used to create a Half-Life 2 face displacement"
    "in mapentities class FaceType."
    undomsg = "drag edge"
    hint = "control point for height"

  #1  def __init__(self, base, face):
  #1      pos = base
  #1      FaceHandle.__init__(self, pos, face)

  #2  def __init__(self, base, face):
  #2      pos = base
  #2      PointSpecHandle.__init__(self, pos, entity, spec)

    def __init__(self, pos, normal, scale1, entity, spec):
  #3      normal = None
  #3      scale1 = None
  #3      entity = None
  #3      spec = None
  #3      face = spec
        pos = pos
        Angles3DHandle.__init__(self, pos, normal, scale1, entity, spec)

    def menu(self, editor, view):
        self.click(editor)
        editor.layout.clickedview = view
        return self.OriginItems(editor, view)

    def draw(self, view, cv, draghandle=None):
        self.cv = cv
        p = view.proj(self.pos)
        print "maphandles SpecialHandle line 490 p in draw",p
        oldcolor = cv.pencolor
#        p1 = view.proj(self.vtx1)
#        p2 = view.proj(self.vtx2)
        cv.pencolor = oldcolor
        if p.visible:
            cv.reset()
            cv.brushcolor = 0xF000F0
            radius = 9
#py2.4            cv.ellipse(p.x-radius, p.y-radius, p.x+radius+1, p.y+radius+1)
            cv.ellipse(int(p.x)-radius, int(p.y)-radius, int(p.x)+radius+1, int(p.y)+radius+1)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)

    def drag(self, v1, v2, flags, view):
        cv = self.cv
        delta = v2-v1
        g1 = 1
        if flags&MB_CTRL:
    #1        pos0 = self.face.origin
            pos0 = self.entity.origin
            if pos0 is not None:
                pos1 = qhandles.aligntogrid(pos0+delta, 1)
                delta = pos1 - pos0
                g1 = 0
        if g1:
            delta = qhandles.aligntogrid(delta, 0)
        self.draghint = vtohint(delta)
        if delta or (flags&MB_REDIMAGE):
          print "in maphandles.py file, class SpecialHandle line 514, light handle moved ",delta

           # new = self.face.copy()
           # if self.face.faceof[0].type == ":p":
           #     delta = self.face.normal * (self.face.normal*delta)  # projection of 'delta' on the 'normal' line
           # new.translate(delta)
           # if flags&MB_DRAGGING:    # the red image contains the whole polyhedron(s), not the single face
           #     new = completeredimage(self.face, new)
           # else:
           #     new = [new]
        else:
            new = None
    #1    return [self.face], None #new
        print "self.cv",self.cv
        return [self.cv], None #new


class VertexHandle(qhandles.GenericHandle):
    "A polyhedron vertex."

    undomsg = Strings[525]
    hint = "Move vertex and distort polyhedron\n'n' key: move only one vertex\nAlt key: restricted to one face only\nCtrl key: force the vertex to the grid||Move vertex and distort polyhedron:\nBy dragging this point, you can distort the polyhedron.\n\nHolding down the 'n' key: This allows the movement of only ONE vertex and may add additional faces to obtain the shape.\n\nHolding down the Alt key: This allows only one face to move. It appears like you are moving the vertex of the polyhedron. In this case be aware that you might not always get the expected results, because you are not really dragging the vertex, but just rotating the adjacent faces in a way that simulates the vertex movement. If you move the vertex too far away, it might just disappear.|intro.terraingenerator.shaping.html#othervertexmovement"

    def __init__(self, pos, poly):
        qhandles.GenericHandle.__init__(self, pos)
        self.poly = poly
        self.cursor = CR_CROSSH

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
            vertical = view.vector("z").normalized   # vertical vector at this point
            # Correction for 3D views, still needs some work though.
            if view.info["type"] == "3D":
                vertX, vertY, vertZ = vertical.tuple
                vertX = round(vertX)
                vertY = round(vertY)
                vertZ = round(vertZ)
                vertical = quarkx.vect(vertX, vertY, vertZ)
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


    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = view.color
#py2.4            cv.rectangle(p.x-0.501, p.y-0.501, p.x+2.499, p.y+2.499)
            cv.rectangle(int(p.x)-int(0.501), int(p.y)-int(0.501), int(p.x)+int(2.499), int(p.y)+int(2.499))


    def ok2(self, editor,undo,old,new):
        qhandles.GenericHandle.ok(self,editor,undo,old,new)
        for poly in new:
            for face in poly.faces:
                face.enhrevert()
        editor.layout.explorer.sellist=new

    def drag(self, v1, v2, flags, view):

        #### Vertex Dragging Code by Tim Smith ####

        #
        # compute the projection of the starting point? onto the
        # screen.
        #
        p0 = view.proj(self.pos)
        if not p0.visible: return

        #
        # save a copy of the original faces
        #
        orgfaces = self.poly.subitems

        #
        # first, loop through the faces to see if we are draging
        # more than one point at a time.  This loop uses the distance
        # between the projected screen position of the starting point
        # and the project screen position of the vertex.
        #
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

        #
        # if the ALT key is pressed
        #
        if (flags&MB_ALT) != 0:

            #
            # loop through the list of points looking for the edge
            # that is closest to the new position.
            #
            # WARNING - THIS CODE ASSUMES THAT THE VERTECIES ARE ORDERED.
            #   IT ASSUMES THAT V1->V2 MAKE AND EDGE, V2->V3 etc...
            #
            # Note by Armin: this assumption is correct.
            #
            delta = v2 - v1
            mindist = 99999999
            dv1 = self.pos + delta
            xface = -1
            xvert = -1
            for f in self.poly.faces:
                xface = xface + 1
                if f in orgfaces:
                    if abs(self.pos*f.normal-f.dist) < epsilon:
                        vl = f.verticesof (self.poly)
                        i = 0
                        while i < len (vl):
                            v = vl [i]
                            p1 = view.proj(v)
                            if p1.visible:
                                dx, dy = p1.x-p0.x, p1.y-p0.y
                                d = dx*dx + dy*dy
                                if d < epsilon:
                                    dv2 = v - vl [i - 1]
                                    if dv2:
                                        cp = (v - dv1) ^ dv2
                                        num = (cp.x * cp.x + cp.y * cp.y + cp.z * cp.z)
                                        den = (dv2.x * dv2.x + dv2.y * dv2.y + dv2.z * dv2.z)
                                        if num / den < mindist:
                                            mindist = num / den
                                            vtu1 = v
                                            vtu2 = vl [i - 1]
                                            xvert = i - 1
                                    dv2 = v - vl [i + 1 - len (vl)]
                                    if dv2:
                                        cp = (v - dv1) ^ dv2
                                        num = (cp.x * cp.x + cp.y * cp.y + cp.z * cp.z)
                                        den = (dv2.x * dv2.x + dv2.y * dv2.y + dv2.z * dv2.z)
                                        if num / den < mindist:
                                            mindist = num / den
                                            vtu1 = v
                                            vtu2 = vl [i + 1 - len (vl)]
                                            xvert = i
                            i = i + 1

            #
            # If a edge was found
            #
            if mindist < 99999999:
                #
                # Compute the orthogonal projection of the destination point onto the
                # edge.  Use the projection to compute a new value for delta.
                #
                temp = dv1 - vtu1
                if not temp:
                    vtu1, vtu2 = vtu2, vtu1
                temp = dv1 - vtu1
                vtu2 = vtu2 - vtu1
                k = (temp * vtu2) / (abs (vtu2) * abs (vtu2))
                projdv1 = k * vtu2
                temp = projdv1 + vtu1

                #
                # Compute the final value for the delta
                #
                if flags&MB_CTRL:
                    delta = qhandles .aligntogrid (temp, 1) - self .pos
                else:
                    delta = qhandles .aligntogrid (temp - self .pos, 0)

        #
        # Otherwise
        #
        else:
            #
            # if the control key is pressed, align the destination point to grid
            #
            if flags&MB_CTRL:
                v2 = qhandles.aligntogrid(v2, 1)

            #
            # compute the change in position
            #
            delta = v2-v1

            #
            # if the control is not pressed, align delta to the grid
            #
            if not (flags&MB_CTRL):
                delta = qhandles.aligntogrid(delta, 0)

        #
        # if we are dragging
        #
        if view.info["type"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["type"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + " " + ftoss(self.pos.z+delta.z)
        elif view.info["type"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            s = "was: " + vtoposhint(self.pos) + " now: " + vtoposhint(delta + self.pos)
        self.draghint = s

        if delta or (flags&MB_REDIMAGE):

            #
            # make a copy of the polygon being drug
            #
            new = self.poly.copy()

            #
            # loop through the faces
            #
            for f in self.poly.faces:

                #
                # if this face is part of the original group
                #
                if f in orgfaces:
                    #
                    # if the point is on the face
                    #
                    if abs(self.pos*f.normal-f.dist) < epsilon:

                        #
                        # collect a list of verticies on the face along
                        # with the distances from the destination point.
                        # also, count the number of vertices.  NOTE:
                        # this loop uses the actual distance between the
                        # two points and not the screen distance.
                        #
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

                        #
                        # sort the list of vertecies, this places the
                        # most distant point at the end
                        #
                        vlist.sort ()
                        vmax = vlist [-1][1]

                        #
                        # if we are draging two vertecies
                        #
                        if dragtwo:

                            #
                            # if this face does not have more than one vertex
                            # selected, then skip
                            #
                            if foundcount != 2:
                                continue

                            #
                            # the rotational axis is between the two
                            # points being drug.  the reference point is
                            # the most distant point
                            #
                            rotationaxis = mvlist [0] - mvlist [1]
                            otherfixed =getotherfixed(vmax, mvlist, rotationaxis)
                            fixedpoints = vmax, otherfixed

                        #
                        # otherwise, we are draging one
                        #
                        else:

                            #
                            # if this face does not have any of the selected
                            # vertecies, then skip
                            #
                            if foundcount == 0:
                                continue

                            #
                            # sort the vertex list and use the last vertex as
                            # a rotational reference point
                            # (already done, seems to me)
                        #    vlist.sort()
                        #    vmax = vlist[-1][1]


                            #
                            # METHOD A: Using the two most distant points
                            # as the axis of rotation
                            #
                            if not (flags&MB_SHIFT):
                                rotationaxis = (vmax - vlist [-2] [1])
                                fixedpoints = vmax, vlist[-2][1]

                            #
                            # METHOD B: Using the most distant point, rotate
                            # along the perpendicular to the vector between
                            # the most distant point and the position
                            #
                            else:
                                rotationaxis = (vmax - self .pos) ^ f .normal
                                otherfixed =getotherfixed(vmax, vlist, rotationaxis)
                                fixedpoints = vmax, otherfixed

                        #
                        # apply the rotation axis to the face (requires that
                        # rotationaxis and vmax to be set)
                        #
                        newpoint = self.pos+delta
                        nf = new.subitem(orgfaces.index(f))

                        def pointsok(new,fixed):
                            #
                            # coincident not OK
                            #
                            if not new-fixed[0]: return 0
                            if not new-fixed[1]: return 0
                            #
                            # colinear also not OK
                            #
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
                            #
                            # Code 4 for NuTex
                            #
                            nf.setthreepoints(tp ,2)



                # if the face is not part of the original group
                #

                else:
                    if not (flags&MB_DRAGGING):
                        continue   # face is outside the polyhedron
                    nf = f.copy()   # put a copy of the face for the red image only
                    new.appenditem(nf)

        #
        # final code
        #
            new = [new]
        else:
            new = None
        return [self.poly], new



class MapEyeDirection(qhandles.EyeDirection):

    MODE = SS_MAP


class PropGlueDlg (SimpleCancelDlgBox):

    #
    # dialog layout
    #

    size = (130, 75)
    dfsep = 0.6       # separation at 40% between labels and edit boxes
    dlgflags = FWF_KEEPFOCUS

    dlgdef = """
        {
        Style = "9"
        Caption = "Glue Proportion"

        prop: =
        {
        Txt = "Proportion:"
        Typ = "EF001"
        Hint = "L-end will be moved to this proportion of the distance" $0D "from the texture origin to the tagged point"
        }
        cancel:py = {Txt="" }
    }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, action):

    #
    # General initialization of some local values
    #

        src = quarkx.newobj(":")
        initialvalue = quarkx.setupsubset(SS_MAP, "Options")["PropTexGlue"]
        if initialvalue is None:
            initialvalue = 1,
        src["prop"]=initialvalue
        self.action=action
        SimpleCancelDlgBox.__init__(self, form, src)

    #
    # This is executed when the data changes, close when a new
    #   name is provided
    #
    def datachange(self, df):
        quarkx.setupsubset(SS_MAP, "Options")["PropTexGlue"] = self.src["prop"]
        self.close()
 

    #
    # This is executed when the OK button is pressed
    #   FIXME: 'local' code doesn't work right, dialog
    #   would need some redesign
    #
    def ok(self):
        prop, = self.src["prop"]
        self.prop = prop
        self.action(self)


class CyanLHandle(qhandles.GenericHandle):
    "Texture moving of faces : cyan L vertices."

    def __init__(self, n, tp4, face, texsrc):
        self.tp4 = tp4
        qhandles.GenericHandle.__init__(self, self.tp4[n])
        self.n = n
        self.face = face
        self.cursor = (CR_DRAG, CR_LINEARV, CR_LINEARV, CR_CROSSH)[n]
        self.texsrc = texsrc
        self.undomsg = Strings[(598,617,617,618)[n]]
        self.hint = ("offset texture on face", "enlarge or distort 1st texture axis",
         "enlarge or distort 2nd texture axis", "rotate texture")[n] +   \
         "||Use the 4 handles at the corners of this 'L' to scroll or rotate the texture on the face.\n\nThe center of the 'L' lets you scroll the texture; the two ends lets you enlarge and distort the texture in the corresponding directions; the 4th point lets you rotate the texture."

    def menu(self,editor,view):
        import plugins.tagging

        norm=self.face.normal
        facepoint=self.face.dist*norm

        #
        # .axisbase() method recovers orthogonal vectors
        # in plane of face, y horizontal.
        #
        x, y = self.face.axisbase()

        #
        # converts p to coordinates with origin org,
        #  axisbase axis vectors.  See Python Tute
        #  4.7.1. for the default argument constructioin
        #  x=x, etc.  Here the x on the left represents
        #  x in the function, x on the right x outside;
        #  when the function is called, we only need to
        #  specify the first two arguments and the other
        #  two will take their default values as provided
        #  in the lines above.
        #
        def toAxisBase(p,org,x=x,y=y,z=norm):
            diff = p-org
            return quarkx.vect(diff*x, diff*y, diff*z)

        #
        # Also projects onto plane
        #
        def fromAxisBase(p, org, x=x, y=y):
            return org+p.x*x+p.y*y

        def onFace(p,norm=norm, facepoint=facepoint):
            if norm*(facepoint-p)<.0001:
                return 1
            else:
                return 0

        def toFace(p,norm=norm, facepoint=facepoint):
            return projectpointtoplane(p,norm,facepoint,norm)

        #
        # Glue to tagged point
        #
        tagged=plugins.tagging.gettaggedpt(editor)
        if tagged is not None:
            taggedonface = onFace(tagged)
        else:
            taggedonface=0

        def glueClick(m,tagged=tagged,self=self,editor=editor,toFace=toFace):
            #
            # We only want to glue to points on the plane of theface, so
            #  any off-plane points are projected to the plane.
            #
            tagged=toFace(tagged)
            #
            # These are the locations of the four Cyan handles
            #  (origin, s, t, rotation)
            #
            p1, p2, p3, p4 = self.tp4
            #
            # We'll operate on a copy, then undo.exchange()
            #
            newface = self.face.copy()
            #
            # The n-value of the handle says which of
            #   the four handles this one is, starting # 0.
            # Below assumes that menuitem is disabled for n=3
            #
            if self.n==0:
                diff = p1-tagged
                #
                # setthreepoints(texp,2) for setting a texture scale.
                #
                newface.setthreepoints((tagged,p2-diff,p3-diff),2)
            elif self.n==1:
                newface.setthreepoints((p1,tagged,p3),2)
            elif self.n==2:
                newface.setthreepoints((p1,p2,tagged),2)
            #
            # And now the undo - exchange sequence.
            #
            undo=quarkx.action()
            undo.exchange(self.face,newface)
            editor.ok(undo,'Glue to Tagged')


        glueitem = qmenu.item('Glue to tagged',glueClick)
        if not taggedonface or self.n==3:
            glueitem.state=qmenu.disabled

        #
        # Align to tagged edge (by rotation, to the one
        #   that's closest to being aligned)
        #
        edge = gettaggededge(editor)

        def alignClick(m,self=self,edge=edge,editor=editor,
                       toAxisBase=toAxisBase,fromAxisBase=fromAxisBase):
            p1, p2, p3, p4 = self.tp4
            def proj1(p,org=p1,toAxisBase=toAxisBase):
                return toAxisBase(p,org)
            p2, p3 = proj1(p2), proj1(p3)
            edge = toAxisBase(edge[1], edge[0])
            def toAngle(p):
                p = p.normalized
                return math.atan2(p.y, p.x)
            #
            # 'map' applies the function to the list/tuple.
            #  in Minipy, result is a list and needs to
            #  be coerced to tuple.
            #
            edgeang, p2ang, p3ang = tuple(map(toAngle, (edge, p2, p3)))
            #
            # Find the smallest angle that will rotate the threepoints
            #  into alignment
            #
            rotang=2*math.pi
            for edgeang0 in edgeang, -edgeang:
                for p2ang0 in p2ang, p3ang:
                    diffang = edgeang0-p2ang0
                    if abs(rotang)>abs(diffang):
                        rotang=diffang
            rotmat = matrix_rot_z(rotang)
            def convert(p,org=p1,rotmat=rotmat,fromAxisBase=fromAxisBase):
                p = rotmat*p
                return  fromAxisBase(p,org)
            p2, p3 = convert(p2), convert(p3)
            newface=self.face.copy()
            newface.setthreepoints((p1,p2,p3),2)
            undo = quarkx.action()
            undo.exchange(self.face, newface)
            editor.ok(undo, "Align Texture")

        alignitem = qmenu.item('Align to tagged edge',alignClick)
        if edge is None:
            alignitem.state=qmenu.disabled

        def action(dlgself, self=self, tagged=tagged, editor=editor, toFace=toFace):
            prop=dlgself.prop            
            tagged=toFace(tagged)
            p1, p2, p3, p4 = self.tp4
            newface = self.face.copy()
            diff=prop*(tagged-p1)
            if self.n==1:
                newface.setthreepoints((p1, p1+diff, p3),2)
            elif self.n==2:
                newface.setthreepoints((p1,p2,p1+diff),2)
            undo=quarkx.action()
            undo.exchange(self.face,newface)
            editor.ok(undo,'Proportional Glue to Tagged')
 
        def propGlueClick(m, action=action):
            PropGlueDlg(quarkx.clickform,action)
        
        propglueitem = qmenu.item('Proportional glue',propGlueClick)
        propglueitem.state=qmenu.disabled
        if tagged is not None and (self.n==1 or self.n==2):
            propglueitem.state=qmenu.normal

        return [glueitem, propglueitem, alignitem]


    def drag(self, v1, v2, flags, view):
        view.invalidate(1)
        self.dynp4 = None
        delta = v2-v1

        # force into the face plane
        normal = self.face.normal
        if not (flags&MB_CTRL):
            delta = qhandles.aligntogrid(delta, 0)
        delta = delta - normal*(normal*delta)   # back into the plane

        if not delta:
            return None, None

        p1,p2,p3,p4 = self.tp4
        p2 = p2 - p1
        p3 = p3 - p1
        if self.n==0:
            p1 = p1 + delta
            if flags&MB_CTRL:
                p1 = qhandles.aligntogrid(p1, 1)
                p1 = p1 - normal*(normal*p1-self.face.dist)   # back into the plane
            self.draghint = vtohint(p1-self.tp4[0])
        elif self.n==1:
            p2 = p2 + delta
            if flags&MB_CTRL:
                p2 = qhandles.aligntogrid(p2, 1)
                p2 = p2 - normal*(normal*p2)   # back into the plane
            self.draghint = vtohint(p2-self.tp4[1])
        elif self.n==2:
            p3 = p3 + delta
            if flags&MB_CTRL:
                p3 = qhandles.aligntogrid(p3, 1)
                p3 = p3 - normal*(normal*p3)   # back into the plane
            self.draghint = vtohint(p3-self.tp4[2])
        else:   # n==3:
            # ---- texture rotation begin ----
            if not normal:
                return None, None
            texp4 = p2+p3
            m = qhandles.UserRotationMatrix(normal, texp4+qhandles.aligntogrid(delta, 0), texp4, flags&MB_CTRL)
            if m is None:
                return None, None
            p2 = m*p2
            p3 = m*p3
            self.draghint = "%d degrees" % (math.acos(m[0,0])*180.0/math.pi)
            # ---- texture rotation end ----

#DECKER - 2001.08.13 - The 'if abs(p2^p3) < l*l*0.1:' makes it impossible to have a _huge_ first texture-axis and a _small_ second texture-axis
#        l = max((abs(p2), abs(p3)))
#        if abs(p2^p3) < l*l*0.1:
#            return None, None    # degenerate

        try:
            # Calculate the "angle" between the two texture-axes
            v = p2.normalized - p3.normalized
            len = abs(v)
            # Make sure that the "angle" isn't near "360-degrees" nor "0-degrees", else the texture would look rather weird!
            if len < 0.01 or len > 1.999:
                return None, None    # degenerate
        except:
            return None, None    # math error
#/DECKER - 2001.08.13

        self.dynp4 = (p1,p1+p2,p1+p3,p1+p2+p3)
        r = self.face.copy()
        r.setthreepoints((p1,p1+p2,p1+p3), 2, self.texsrc)
        return [self.face], [r]

    def getdrawmap(self):
        return self.face, qhandles.refreshtimertex


class CyanLHandle0(CyanLHandle):
    "Texture moving of faces : cyan L base."

    def __init__(self, tp4, face, texsrc, handles):
        CyanLHandle.__init__(self, 0, tp4, face, texsrc)
        self.friends = handles


    def draw(self, view, cv, draghandle=None):
        dyn = (draghandle is self) or (draghandle in self.friends)
        if dyn:
            pencolor = RED
            tp4 = draghandle.dynp4
        else:
            tp4 = None
        if tp4 is None:
            pencolor = 0xF0CAA6
            tp4 = self.tp4
        pt = map(view.proj, tp4)

        # draw a grid while dragging
        if dyn:
            view.drawgrid(pt[1]-pt[0], pt[2]-pt[0], MAROON, DG_LINES, 0, tp4[0])

        # draw the cyan L
        cv.reset()
        cv.pencolor = BLACK
        cv.penwidth = 5
        cv.line(pt[0], pt[2])
        cv.line(pt[3], pt[3])
        cv.pencolor = pencolor
        cv.penwidth = 3
        cv.line(pt[0], pt[2])
        cv.line(pt[3], pt[3])
        cv.pencolor = BLACK
        cv.penwidth = 5
        cv.line(pt[0], pt[1])
        cv.pencolor = pencolor
        cv.penwidth = 3
        cv.line(pt[0], pt[1])

#
# A version of LinHandlesManager for Bezier texture.
#

class BTLinHandlesManager(qhandles.LinHandlesManager):
    "Linear Box manager for Bezier texture."

    def t2p(self, p):
        w,h = self.scale
        return quarkx.vect(p.x*w, p.y*h, 0.0)

    def p2t(self, p):
        w,h = self.scale
        return quarkx.vect(p.x/w, p.y/h, 0.0)

    def linear(self, sender, obj, center, matrix):
        if obj.type==":b3":
            obj.vst = sender.dynst = map(self.p2t, map(lambda v,center=center,matrix=matrix: matrix*(v-center)+center, map(self.t2p, obj.vst)))
        else:
            def maprow(p,center=center,matrix=matrix,self=self):
                t = self.t2p(quarkx.vect(p.s, p.t, 0.0))
                t = self.p2t(matrix*(t-center)+center)
                return quarkx.vect(p.xyz + (t.x, t.y))
            tcp = []
            for row in obj.cp:
                tcp.append(map(maprow, row))
            obj.cp = sender.dynst = tcp

    def translate(self, sender, obj, delta, forcetogrid):
        if obj.type==":b3":
            obj.vst = sender.dynst = map(self.p2t, map(lambda v,delta=delta: v+delta, map(self.t2p, obj.vst)))
        else:
            def maprow(p, delta=delta, self=self):
                t = self.t2p(quarkx.vect(p.s, p.t, 0.0))
                t = self.p2t(t+delta)
                return quarkx.vect(p.xyz + (t.x, t.y))
            tcp = []
            for row in obj.cp:
                tcp.append(map(maprow, row))
            obj.cp = sender.dynst = tcp


class CyanBezier2Handle(qhandles.GenericHandle):
    "Texture moving of Bezier patches : cyan L vertices."

    undomsg = Strings[628]
    hint = "the shape is the fraction of the texture to map to the Bezier patch"

    def __init__(self, (i,j), cp, b2, scale):
        self.scale = scale
        qhandles.GenericHandle.__init__(self, self.t2p(cp[i][j]))
        self.b2 = b2
        self.ij = (i,j)
        self.hint = "Control Point (%d, %d)"%(i,j)
        self.cp = cp
        self.colormask = WHITE
        self.color = WHITE

    def t2p(self, p):
        w,h = self.scale
        return quarkx.vect(p.s*w, p.t*h, 0.0)

    def p2t(self, p, q):
        w,h = self.scale
        return quarkx.vect(q.xyz +(p.x/w, p.y/h))

    def drag(self, v1, v2, flags, view):
        view.invalidate(1)
        self.dynst = None
        new = None
        delta = v2-v1
        if not (flags&MB_CTRL):
            delta = qhandles.aligntogrid(delta, 0)

        if flags&MB_CTRL:
            delta = qhandles.aligntogrid(self.pos + delta, 1) - self.pos
        if delta or (flags&MB_REDIMAGE):
            new = self.b2.copy()
            cp = map(list, self.b2.cp)
            i, j = self.ij
            w,h = self.scale
            td = quarkx.vect(0,0,0,delta.x/w,delta.y/h)
            moverow = (quarkx.keydown('\022')==1)  # ALT
            movecol = (quarkx.keydown('\020')==1)  # SHIFT
            from mapbezier import pointsToMove
            indexes = pointsToMove(moverow, movecol, i, j, len(cp), len(cp[0]))
            for m,n in indexes:
                cp[m][n] = cp[m][n]+td
                new.cp =cp

        if new is not None:
            self.dynst = new.cp
            return [self.b2], [new]
        else:
            return [self.b2], new

    def getdrawmap(self):
        return self.b2, qhandles.refreshtimertex

    def getcenter(self):
        cp = self.cp
        m, n = len(cp)-1, len(cp[0])-1
        return self.t2p(0.25*(cp[0][0]+cp[m][0]+cp[0][n]+cp[m][n]))



class CyanBezier2Handle0(CyanBezier2Handle):
    "Texture moving of Bezier patches : cyan L base."

    def __init__(self, cp, b2, handles, scale):
        CyanBezier2Handle.__init__(self, (0,0), cp, b2, scale)
        self.friends = handles

    def draw(self, view, cv, draghandle=None):
        dyn = (draghandle is self) or (draghandle in self.friends)
        if dyn:
            pencolor = RED
            try:
                cp = draghandle.dynst
            except (AttributeError):
                cp = None
        else:
            cp = None
        if cp is None:
            pencolor = 0xF0CAA6
            cp = self.cp
        pt = []
        for row in cp:
            pt.append(map(view.proj, map(self.t2p, row)))
        m, n = len(cp), len(cp[0])
        # draw the cyan shape
        cv.reset()
        def line(frm, to, bold, cv=cv, pencolor=pencolor):
            cv.pencolor = BLACK
            cv.penwidth = (3,5)[bold]
            cv.line(frm, to)
            cv.pencolor = pencolor
            cv.penwidth = (1,3)[bold]
            cv.line(frm, to)
        # vertical thin lines
        for i in range(m-1):
            for j in range(1, n-1):
                line(pt[i][j], pt[i+1][j], 0)
        # horizontal thin lines
        for i in range(1,m-1):
            for j in range(n-1):
                line(pt[i][j], pt[i][j+1], 0)
        # vertical bold lines
        for i in range(m-1):
            for j in (0,n-1):
                line(pt[i][j], pt[i+1][j], 1)
        # horizontal bold lines
        for i in (0,m-1):
            for j in range(n-1):
                line(pt[i][j], pt[i][j+1], 1)


class EyePositionMap(qhandles.EyePosition):
      pass

#
# Functions to build common lists of handles.
#


def BuildHandles(editor, ex, view):
    "Build a list of handles to display on the map views."
    fs = ex.uniquesel
    if (fs is None) or editor.linearbox:
        #
        # Display a linear mapping box.
        #
        list = ex.sellist
        box = quarkx.boundingboxof(list)
        if box is None:
            h = []
        else:

## This section to setup for Terrain handels - cdunde 04-23-05

            if editor.layout.toolbars["tb_dragmodes"] is not None:
                tb1 = editor.layout.toolbars["tb_dragmodes"]
                for b in tb1.tb.buttons:
                    if b.state == 2:
                        manager = qhandles.LinHandlesManager(MapColor("Linear"), box, list)
                        h = manager.BuildHandles(editor.interestingpoint())


            if editor.layout.toolbars["tb_terrmodes"] is not None:
                tb2 = editor.layout.toolbars["tb_terrmodes"]
                for b in tb2.tb.buttons:
                    if b.state == 2:
                        manager = plugins.mapterrainmodes.TerrainLinHandlesManager(MapColor("Duplicator"), box, list, view)
                        h = manager.BuildHandles(editor.interestingpoint())
## End of above section for Terrain handels

## This section to setup for Objectmodes handels - cdunde 12-21-05

            if editor.layout.toolbars["tb_objmodes"] is not None:
                tb3 = editor.layout.toolbars["tb_objmodes"]
                for b in tb3.tb.buttons:
                    if b.state == 2:
                        manager = qhandles.LinHandlesManager(MapColor("Linear"), box, list)
                        h = manager.BuildHandles(editor.interestingpoint())
## End of above section for Objectmodes handels

    else:
        #
        # Get the list of handles from the entity manager.
        #
        h = mapentities.CallManager("handles", fs, editor, view)
    #
    # Add the 3D view "eyes".
    #
    for v in editor.layout.views:
        if (v is not view) and (v.info["type"] == "3D"):
            h.append(EyePositionMap(view, v))
            h.append(MapEyeDirection(view, v))
    return qhandles.FilterHandles(h, SS_MAP)


def BuildCyanLHandles(editor, face):
    "Build a list of handles to display a cyan L over a face' texture."

    tp = face.threepoints(2, editor.TexSource)
    if tp is None:
        return []
    tp4 = tp + (tp[1]+tp[2]-tp[0],)
    handles = [CyanLHandle(1,tp4,face,editor.TexSource), CyanLHandle(2,tp4,face,editor.TexSource), CyanLHandle(3,tp4,face,editor.TexSource)]
    return qhandles.FilterHandles([CyanLHandle0(tp4, face, editor.TexSource, handles)] + handles, SS_MAP)



#
# Drag Objects
#

class RectSelDragObject(qhandles.RectangleDragObject):
    "A red rectangle that selects the polyhedrons it touches."

    Hint = hintPlusInfobaselink("Rectangular selection of POLYHEDRONS||Rectangular selection of POLYHEDRONS:\n\nAfter you click on this button, click and move the mouse on the map to draw a rectangle; all polyhedrons touching this rectangle will be selected.\n\nHold down Ctrl to prevent already selected polyhedron from being unselected first.", "intro.mapeditor.toolpalettes.mousemodes.html#selectpoly")

    def rectanglesel(self, editor, x,y, rectangle):
        if not ("T" in self.todo):
            editor.layout.explorer.uniquesel = None
        polylist = FindSelectable(editor.Root, ":p")
        lastsel = None
        for p in polylist:
            if rectangle.intersects(p):
                p.selected = 1
                lastsel = p
        if lastsel is not None:
            editor.layout.explorer.focus = lastsel
            editor.layout.explorer.selchanged()


#
# Mouse Clicking and Dragging on map views.
#

def MouseDragging(self, view, x, y, s, handle):
    "Mouse Drag on a Map View."

    #
    # qhandles.MouseDragging builds the DragObject.
    #
    if handle is not None:
        s = handle.click(self)
        if s and ("S" in s):
            self.layout.actionmpp()  # update the multi-pages-panel

    return qhandles.MouseDragging(self, view, x, y, s, handle, MapColor("DragImage"))


def ClickOnView(editor, view, x, y):
    #
    # defined in QkPyMapview.pas
    #
#py2.4    return view.clicktarget(editor.Root, x, y)
    return view.clicktarget(editor.Root, int(x), int(y))


def MapAuxKey(keytag):
    return quarkx.setupsubset(SS_GENERAL, "AuxKeys")[keytag]

def wantPoly():
    return quarkx.keydown(MapAuxKey('Select Brushes'))==1

def wantFace():
    return quarkx.keydown(MapAuxKey('Select Faces'))==1
    
def wantCurve():
     return quarkx.keydown(MapAuxKey('Select Curves'))==1    

def wantEntity():
    return quarkx.keydown(MapAuxKey('Select Entities'))==1

def MouseClicked(self, view, x, y, s, handle):
    "Mouse Click on a Map view."

    #
    # qhandles.MouseClicked manages the click but doesn't actually select anything
    #

    flags = qhandles.MouseClicked(self, view, x, y, s, handle)
#    debug('flagz: '+s)
    try:
        editor = mapeditor()
        if editor is not None:
            if isinstance(handle, PFaceHandle) and isinstance(editor.findtargetdlg, plugins.maptexpos.TexPosDlg):
                o = editor.layout.explorer.uniquesel
                m = qmenu.item("Dummy", None, "")
                m.o = o
                plugins.maptexpos.PosTexClick(m)
    except:
        pass
    if view.info["type"]=="3D":
        self.last3DView = view
    if "1" in flags:
        #
        # This mouse click must select something.
        #

        self.layout.setupdepth(view)
        choice = ClickOnView(self, view, x, y)
         # this is the list of polys & entities we clicked on
         # the members of the choice list are pairs, for polys,
         #   the first is the poly, the second the face
         #
        if wantCurve():
            choice=filter(lambda obj:obj[1].type==':b2', choice)
        elif wantFace() or wantPoly():
            choice=filter(lambda obj:obj[1].type==':p', choice)
        elif wantEntity():

            def getentities(choice):
                result=[]
                for item in choice:
                    if item[1].type==':e':
                        result.append(item)
                    else:
                        parent=item[1].treeparent   
                        while parent.name!='worldspawn:b':
                            if parent.type==':b':    # eventually it will hit worldspawn
                                result.append((choice[0], parent, parent))
                                break
                            parent=parent.treeparent
                return result
                
            choice=getentities(choice)
        if len(choice):
            wantpoly = wantPoly()
            wantface = wantFace()
            choice.sort()   # list of (clickpoint,object) tuples - sort by depth
            last = qhandles.findlastsel(choice)
            #
            # Note: dropping 'and last' from below seems to deliver
            #   background menu on RMB when nothing is selected, seems
            #   better
            #
            if ("M" in s):    # if Menu, we try to keep the currently selected objects
                return flags
            if "T" in s:    # if Multiple selection request
                #
                # if selection is frozen, ignore request
                #
                if getAttr(self, 'frozenselection') is not None:
                    return flags
                obj = qhandles.findnextobject(choice)
                obj.togglesel()
                if obj.selected:
                    self.layout.explorer.focus = obj
                self.layout.explorer.selchanged()
            else:
                if wantface or wantpoly:
                    keep=1
                else:
                    keep=0
                last = qhandles.findlastsel(choice,keep)
                if last:  last = last - len(choice)
                #
                #  if the selection is 'frozen', it can only be changed
                #    by another SHIFT-selection, or the ESC key
                #
                # if the selection if frozen and this isn't a change
                #    frozen selection request, ignore it
                #
                if not "F" in s:
                    if getAttr(self,'frozenselection') is not None:
                       return flags
                if "F" in s:
                    self.frozenselection = 1
                if wantface:
                    self.layout.explorer.uniquesel = choice[last][2]
                else:
                    self.layout.explorer.uniquesel = choice[last][1]

        else:
            if not ("T" in s):    # clear current selection
                #
                # if the selection is 'frozen', we don't want to be
                #   able to clear it with a mouseclick, only ESC
                #
                if getAttr(self,'frozenselection') is not None:
                      pass
                else:
                   self.layout.explorer.uniquesel = None
        return flags+"S"
    return flags


#
# Single face map view display for the Multi-Pages Panel.
#

def viewsingleface(editor, view, face):
    "Special code to view a single face with handles to move the texture."

    def drawsingleface(view, face=face, editor=editor):
        view.drawmap(face)   # textured face
        view.solidimage(editor.TexSource)
        #for poly in face.faceof:
        #    view.drawmap(poly, DM_OTHERCOLOR, 0x2584C9)   # draw the full poly contour
        view.drawmap(face, DM_REDRAWFACES|DM_OTHERCOLOR, 0x2584C9)   # draw the face contour
        editor.finishdrawing(view)
        # end of drawsingleface

    origin = face.origin
    if origin is None: return
    n = face.normal
    if not n: return

    h = []
     # add the vertices of the face
    for p in face.faceof:
        if p.type == ':p':
            for v in face.verticesof(p):
                h.append(VertexHandle(v, p))
    view.handles = qhandles.FilterHandles(h, SS_MAP) + BuildCyanLHandles(editor, face)

#DECKER - begin
    #FIXME - Put a check for an option-switch here, so people can choose which they want (fixed-zoom/scroll, or reseting-zoom/scroll)
    oldx, oldy, doautozoom = 0, 0, 0
    try:
        oldorigin = view.info["origin"]
        if not abs(origin - oldorigin):
            oldscale = view.info["scale"]
            if oldscale is None:
                doautozoom = 1
            oldx, oldy = view.scrollbars[0][0], view.scrollbars[1][0]
        else:
            doautozoom = 1
    except:
        doautozoom = 1

    if doautozoom:
        oldscale = 0.01
#DECKER - end

    v = orthogonalvect(n, editor.layout.views[0])
    view.flags = view.flags &~ (MV_HSCROLLBAR | MV_VSCROLLBAR)
    view.viewmode = "tex"
    view.info = {"type": "2D",
                 "matrix": ~ quarkx.matrix(v, v^n, -n),
                 "bbox": quarkx.boundingboxof([face] + map(lambda h: h.pos, view.handles)),
                 "scale": oldscale, #DECKER
                 "custom": singlefacezoom,
                 "origin": origin,
                 "noclick": None,
                 "mousemode": None }
    singlefacezoom(view, origin)
    if doautozoom: #DECKER
        singlefaceautozoom(view, face) #DECKER
    editor.setupview(view, drawsingleface, 0)
    if (oldx or oldy) and not doautozoom: #DECKER
        view.scrollto(oldx, oldy) #DECKER
    return 1


def singlefaceautozoom(view, face):
    scale1, center1 = AutoZoom([view], view.info["bbox"], margin=(36,34))
    if scale1 is None:
        return 0
    if scale1>1.0:
        scale1=1.0
    if abs(scale1-view.info["scale"])<=epsilon:
        return 0
    view.info["scale"] = scale1
    singlefacezoom(view, center1)
    return 1

    #for test in (0,1):
    #    scale1, center1 = AutoZoom([view], view.info["bbox"], margin=(36,34))
    #    if (scale1 is None) or (scale1>=1.0) or (abs(scale1-view.info["scale"])<=epsilon):
    #        return test
    #    view.info["scale"] = scale1
    #    singlefacezoom(view, center1)   # do it twice because scroll bars may disappear
    #return 1


def singlefacezoom(view, center=None):
    if center is None:
        center = view.screencenter
    view.setprojmode("2D", view.info["matrix"]*view.info["scale"], 0)
    bmin, bmax = view.info["bbox"]
    x1=y1=x2=y2=None
    for x in (bmin.x,bmax.x):   # all 8 corners of the bounding box
        for y in (bmin.y,bmax.y):
            for z in (bmin.z,bmax.z):
                p = view.proj(x,y,z)
                if (x1 is None) or (p.x<x1): x1=p.x
                if (y1 is None) or (p.y<y1): y1=p.y
                if (x2 is None) or (p.x>x2): x2=p.x
                if (y2 is None) or (p.y>y2): y2=p.y
#py2.4    view.setrange(x2-x1+36, y2-y1+34, 0.5*(bmin+bmax))
    view.setrange(int(x2)-int(x1)+36, int(y2)-int(y1)+34, 0.5*(bmin+bmax))

     # trick : if we are far enough and scroll bars are hidden,
     # the code below clamb the position of "center" so that
     # the picture is completely inside the view.
    x1=y1=x2=y2=None
    for x in (bmin.x,bmax.x):   # all 8 corners of the bounding box
        for y in (bmin.y,bmax.y):
            for z in (bmin.z,bmax.z):
                p = view.proj(x,y,z)    # re-proj... because of setrange
                if (x1 is None) or (p.x<x1): x1=p.x
                if (y1 is None) or (p.y<y1): y1=p.y
                if (x2 is None) or (p.x>x2): x2=p.x
                if (y2 is None) or (p.y>y2): y2=p.y
    w,h = view.clientarea
    w,h = (w-36)/2, (h-34)/2
    x,y,z = view.proj(center).tuple
    t1,t2 = x2-w,x1+w
    if t2>=t1:
        if x<t1: x=t1
        elif x>t2: x=t2
    t1,t2 = y2-h,y1+h
    if t2>=t1:
        if y<t1: y=t1
        elif y>t2: y=t2
    view.screencenter = view.space(x,y,z)
    p = view.proj(view.info["origin"])
    view.depth = (p.z-0.1, p.z+100.0)

#
# Single bezier map view display for the Multi-Pages Panel.
#

def viewsinglebezier(view, layout, patch):
    cpts = patch.cp
    if cpts is None:
        return
    texlist = quarkx.texturesof([patch])
    ed = mapeditor()
    if len(texlist)==1:
#        tex = quarkx.loadtexture(texlist[0], layout.editor.TexSource)
        tex = quarkx.loadtexture(texlist[0], ed.TexSource)
        try:
            tex = tex.disktexture
            w,h = tex["Size"]
        except:
            pass
        else:
            if type==':b3':
                vst = patch.vst
            else:
                vst = []
                for row in patch.cp:
                    for p in row:
                        vst.append(quarkx.vect(p.s, p.t, 0))
            matrix = quarkx.matrix((1,0,0), (0,1,0), (0,0,1))
            xmin = xmax = vst[0].x
            ymin = ymax = vst[0].y
            for v in vst[1:]:
                if v.x<xmin: xmin=v.x
                if v.x>xmax: xmax=v.x
                if v.y<ymin: ymin=v.y
                if v.y>ymax: ymax=v.y
            destx, desty = view.clientarea
            scale = (destx-35) / ((xmax-xmin+0.05)*w)
            scaley = (desty-35) / ((ymax-ymin+0.05)*h)
            if scaley<scale: scale=scaley
            if scale<0.001: scale=0.001
            if scale>1.0: scale=1.0

            view.setprojmode("2D", matrix*scale)
            view.info = {"type": "2D",
                   "matrix": matrix,
                   "scale": scale,
                   "custom": singlebezierzoom,
                   "noclick": None,
                   "mousemode": None }
            def draw1(view, finish=layout.editor.finishdrawing, w=w, h=h):
                pt = view.space(quarkx.vect(0,0,0))
                pt = view.proj(quarkx.vect(math.floor(pt.x), math.floor(pt.y), 0))
                #view.canvas().painttexture(tex, (pt.x,pt.y)+view.clientarea, 0)
                view.drawgrid(quarkx.vect(w*view.info["scale"],0,0), quarkx.vect(0,h*view.info["scale"],0), MAROON, DG_LINES, 0, quarkx.vect(0,0,0))
                finish(view)
            view.ondraw = draw1
            view.onmouse = layout.editor.mousemap
            cp = patch.cp
            h2 = []
            m, n = len(cp), len(cp[0])
            for i in range(m):
                for j in range(n):
                    h2.append(CyanBezier2Handle((i,j), cp, patch, (w, h)))
            mainhandle = CyanBezier2Handle0(cp, patch, h2, (w,h))
            h2 = [mainhandle] + h2


            #
            # Display a linear mapping box.
            #
            manager = BTLinHandlesManager(MapColor("Linear"),
                  (quarkx.vect(w*xmin,h*ymin,0),quarkx.vect(w*xmax,h*ymax,0)), [patch])
            manager.scale = w,h
#
# Linear mapping in bez box, can't make it work
#
#            if layout.editor.linearbox:
#                minimal = None
#            else:
#                minimal = (view, layout.editor.gridstep or 32)
#            h1 = manager.BuildHandles(minimal=minimal)
#            getdrawmap1 = lambda patch=patch: (patch, qhandles.refreshtimertex)
#            for i in h1:
#                i.getdrawmap = getdrawmap1
#            mainhandle.friends = mainhandle.friends + h1
#            view.handles = h2 + h1
            view.handles = h2
            view.background = quarkx.vect(0,0,0), 1.0, 0, 1
            view.backgroundimage = tex,
            view.screencenter = mainhandle.getcenter()
            return 1

def singlebezierzoom(view):
    sc = view.screencenter
    view.setprojmode("2D", view.info["matrix"]*view.info["scale"], 0)
    view.screencenter = sc

def GetUserCenter(obj):
#    debug('type: '+`type(obj)`)
    if type(obj) is type([]):  # obj is list
        if len(obj)==1 and obj[0]["usercenter"] is not None:
            uc = obj[0]["usercenter"]
        else:
            try:
                box=quarkx.boundingboxof(obj)
                return (box[0]+box[1])/2
            except:
                return quarkx.vect(0,0,0)
    else:
        uc = obj["usercenter"]
    if uc is None:
        uc = mapentities.ObjectOrigin(obj).tuple
#        debug(' oo '+`uc`)
    return quarkx.vect(uc)

def SetUserCenter(obj, v):
    obj["usercenter"] = v.tuple

def macro_usercenter(self):
    from qeditor import mapeditor
    editor=mapeditor()
    if editor is None: return
    dup = editor.layout.explorer.uniquesel
    if dup is None: return
    from mapentities import ObjectOrigin
    try:
        undo = quarkx.action()
        tup = ObjectOrigin(dup).tuple
        undo.setspec(dup,'usercenter',tup)
        editor.ok(undo,'add usercenter')
        editor.invalidateviews()
    except:
        return

qmacro.MACRO_usercenter = macro_usercenter

class UserCenterHandle(CenterHandle):

    hint = "Usercenter handle (Ctrl key: force to grid)||The usercenter is used to control the pivot-point for rotations and symmetry operations."

    def __init__(self, dup):
        pos = GetUserCenter(dup)
        CenterHandle.__init__(self, pos, dup, MapColor("Axis"))

    def drag(self, v1, v2, flags, view):
        if flags&MB_CTRL:
            v2 = qhandles.aligntogrid(v2, 1)
        delta = v2-v1
        dup = self.centerof.copy()
        SetUserCenter(dup, GetUserCenter(dup)+delta)
        return [self.centerof], [dup]


# ----------- REVISION HISTORY ------------
#
#$Log: maphandles.py,v $
#Revision 1.73  2008/09/29 21:59:51  danielpharos
#Fixed a typo.
#
#Revision 1.72  2008/05/27 19:33:57  danielpharos
#Fix typo
#
#Revision 1.71  2008/05/21 18:14:55  cdunde
#To add and\or activate Half-Life 2 functions: (all original code by Alexander)
#1) to create extra Specifics setting handles for func_useableladder function (point0 & point1)
#      func_breakable_glass and func_breakable_surf functions
#      (lowerleft, upperleft, lowerright and upperright)
#2) to draw special light entity lines for functions like light_spot that have the Specifics
#      (angles, _cone, spotlightwidth and\or _inner_cone)
#3) face displacement. Commented out at this time. believe bezier type code should be used instead.
#
#Revision 1.70  2008/05/14 20:40:40  cdunde
#To fix small typo error.
#
#Revision 1.69  2008/02/06 00:12:44  danielpharos
#The skinview now properly updates to reflect changes made to textures.
#
#Revision 1.68  2007/12/21 20:12:14  cdunde
#To fix error for a group folder if nothing is in it sometimes.
#
#Revision 1.67  2007/11/29 23:39:00  cdunde
#Changed to keep Texture Position dialog open and update dynamically.
#
#Revision 1.66  2007/11/19 00:08:39  danielpharos
#Any supported picture can be used for a view background, and added two options: multiple, offset
#
#Revision 1.65  2007/10/13 18:25:14  cdunde
#Another fix for the face drag handle hint.
#
#Revision 1.64  2007/09/28 18:36:13  cdunde
#To fix hint error on drag.
#
#Revision 1.63  2007/09/18 19:52:07  cdunde
#Cleaned up some of the Defaults.qrk item alignment and
#changed a color name from GrayImage to DragImage for clarity.
#Fixed Rectangle Selector from redrawing all views handles if nothing was selected.
#
#Revision 1.62  2007/08/21 03:38:09  cdunde
#To reinstate this method for the 'Cut out corner' function that seems
#to work better then not having this code added.
#
#Revision 1.61  2007/07/24 13:54:50  danielpharos
#Revert maphandles 1.60: Fixed the underlying problem in PyMath3D.
#
#Revision 1.60  2007/07/23 20:45:43  cdunde
#Added fix for cut corner in 3D views.
#
#Revision 1.59  2007/07/23 13:55:23  danielpharos
#Fixed the 'cut out corner' function broken in Beta 1.
#
#Revision 1.58  2007/04/13 19:47:13  cdunde
#Changed face and vertex dragging hint to give start and progressive drag positions based on grid location.
#
#Revision 1.57  2007/04/12 10:50:50  danielpharos
#Fixed a very stupid typo.
#
#Revision 1.56  2007/04/11 15:53:01  danielpharos
#Added a missing call to init. Should be there, even if only for future changes.
#
#Revision 1.55  2006/11/30 01:19:33  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.54  2006/11/29 07:00:25  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.53.2.3  2006/11/26 19:26:26  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.53.2.2  2006/11/18 03:23:17  cdunde
#Fixed error when handle is moved on the Bezier Selected patch page
#but returned to starting position without completing the handle move.
#
#Revision 1.53.2.1  2006/11/03 23:38:09  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.53  2006/07/19 06:10:26  cdunde
#Updated Extruder Infobase doc and created direct link.
#
#Revision 1.52  2006/04/17 23:49:58  cdunde
#Needed to import plugins\tagging to fix RMB error
#from occurring in texture movement view window.
#
#Revision 1.51  2006/01/30 10:07:13  cdunde
#Changes by Nazar to the scale, zoom and map sizes that QuArK can handle
#to allow the creation of much larger maps for the more recent games.
#
#Revision 1.50  2006/01/12 07:21:01  cdunde
#To commit all new and related files for
#new Quick Object makers and toolbar.
#
#Revision 1.49  2005/11/29 08:17:31  cdunde
#To add F1 help and Infobase documentation
#on new vertex movement function and HotKeys.
#
#Revision 1.48  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.45  2005/09/21 22:42:25  cdunde
#To comment out else statement causing error after
#commenting out print statement previously.
#
#Revision 1.44  2005/09/21 21:33:36  cdunde
#To comment out print statement
#
#Revision 1.43  2005/08/18 02:20:50  cdunde
#Needed to reverse, still under testing of displacement display and handles
#Does not appear to effect other liner or movement  handle usage.
#
#Revision 1.42  2005/08/18 01:17:15  cdunde
#To comment out 1 print statement left open.
#
#Revision 1.41  2005/08/15 05:50:17  cdunde
#To commit all files for Terrain Generator
#
#Revision 1.40  2005/08/11 21:24:23  alexander
#displacement display and handles
#
#Revision 1.39  2005/07/30 23:07:07  alexander
#cone showed for light spots and pitch value automatically set when seleting the entity
#showing height points for displacements
#target links shown for source engine
#
#Revision 1.38  2004/12/29 16:40:22  alexander
#introduced new PointSpecHandle which allows to have additional 3d control points on entities.
#which specifics are used for these points is controlled similar to the angle specific list
#
#Revision 1.37  2003/03/15 20:54:20  cdunde
#To update hints and add infobase links
#
#Revision 1.36  2003/03/06 22:21:34  tiglari
#change for Py2.x compatibility
#
#Revision 1.35  2002/05/18 22:30:42  tiglari
#remove debug statement
#
#Revision 1.34  2002/05/13 10:36:58  tiglari
#support frozen selections (don't change until another frozen selection is made,
#or they are cancelled with ESC or unfreeze selection)
#
#Revision 1.33  2001/09/26 22:37:24  tiglari
#change close button to cancel in proportional glue dialog
#
#Revision 1.32  2001/09/24 23:56:42  tiglari
#store cyanlhandle glue proportion in setup, fix some issues
#
#Revision 1.31  2001/09/24 10:15:19  tiglari
#proportional glue for CyanLHandles
#
#Revision 1.30  2001/08/16 20:09:15  decker_dk
#Support for snap-to-grid in UserCenterHandle drag.
#Specific hint for a UserCenterHandle.
#
#Revision 1.29  2001/08/15 17:52:42  decker_dk
#Exception-catch for def GetUserCenter(), in case "return (box[0]+box[1])/2" fails.
#
#Revision 1.28  2001/08/13 17:45:46  decker_dk
#Fixed problem where a '<huge> <small>' texture-scale caused the code to ignore further changes to the texture on the face.
#
#Revision 1.27  2001/07/27 11:35:49  tiglari
#revert code 4 setthreepoints to code 2
#
#Revision 1.26  2001/07/24 00:04:48  tiglari
#more comments for texture-L RMB menu items
#
#Revision 1.25  2001/06/14 12:17:36  tiglari
#note last 3d view clicked on in mouseclicked
#
#Revision 1.24  2001/06/13 20:58:44  tiglari
#Add map-specific EyePosition handle
#
#Revision 1.23  2001/05/12 10:12:22  tiglari
#fix usercenter button macro bug (add 'is None' ...)
#
#Revision 1.22  2001/05/06 06:03:38  tiglari
#add Edge Handle
#
#Revision 1.21  2001/04/26 22:45:03  tiglari
#face-only selection & texture L RMB
#
#Revision 1.20  2001/04/17 03:18:01  tiglari
#attempt to fix vertex-drag crash
#
#Revision 1.19  2001/04/10 08:54:42  tiglari
#remove debug statements from vertex dragging code
#
#Revision 1.18  2001/04/06 04:46:04  tiglari
#clean out some debug statements
#
#Revision 1.17  2001/04/05 12:36:13  tiglari
#revise vertex move code to try to reduce drift of non-drug vertexes
#
#Revision 1.13.2.3  2001/04/04 10:30:17  tiglari
#find more fixed points, clean up code
#
#Revision 1.13.2.2  2001/04/03 08:54:51  tiglari
#more vertex drag anti-drift.  Very convoluted,if it helps, it needs to be
# cleaned up.
#
#Revision 1.15  2001/04/02 21:09:44  tiglari
#fixes to getusercenter, ntp tuple-hood
#
#Revision 1.14  2001/04/02 09:23:11  tiglari
#stuck various things to try to nail down supposed fixpoint vertices in the
#vtx movement code
#
#Revision 1.13  2001/04/01 00:07:13  tiglari
#revisions to GetUserCenter
#
#Revision 1.12  2001/03/31 10:15:22  tiglari
#support for usercenter specific
#
#Revision 1.11  2001/03/01 19:14:58  decker_dk
#Fix for CyanBezier2Handle.drag 'if new:'. Now testing for 'if new is not None:'.
#
#Revision 1.10  2001/02/28 09:46:43  tiglari
#linear mapping handles removed from bez page
#
#Revision 1.9  2001/02/25 11:22:51  tiglari
#bezier page support, transplanted with permission from CryEd (CryTek)
#
#Revision 1.8  2001/02/07 18:40:47  aiv
#bezier texture vertice page started.
#
#Revision 1.7  2000/06/17 07:32:06  tiglari
#a slight change to clickedview
#
#Revision 1.6  2000/06/16 10:44:54  tiglari
#CenterHandle menu function adds clickedview to editor.layout
#(for support of perspective-driven curve creation in mb2curves.py)
#
#Revision 1.5  2000/06/02 16:00:22  alexander
#added cvs headers
#
