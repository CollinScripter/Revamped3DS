"""   QuArK  -  Quake Army Knife

Generic Mouse handles code.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/qhandles.py,v 1.101 2011/10/06 20:13:37 danielpharos Exp $

#
# Generic handles. See maphandles.py for more information.
# This module defines only generic handle classes that are
# not related to map editing.
#

#py2.4 indicates upgrade change for python 2.4


from qeditor import *
from qdictionnary import Strings
import qmenu
import qbaseeditor

MOUSEZOOMFACTOR = math.sqrt(2)     # with this value, the zoom factor doubles every two click
STEP3DVIEW = 64.0

vfSkinView = 0x80 # 2d only - used for skin page for mdl editor and bezier page for map editor

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
modelcenter = None
skinviewold = None
skinviewnew = None
skinviewdraghandle = None

def newfinishdrawing(editor, view, oldfinish=qbaseeditor.BaseEditor.finishdrawing):
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
    try:
        return quarkx.vect(rnd(v.x/g)*g, rnd(v.y/g)*g, rnd(v.z/g)*g)
    except:
        return quarkx.vect(rnd(1/g)*g, rnd(1/g)*g, rnd(1/g)*g)

def setupgrid(editor):
    #
    # Set the grid variable from the editor's current grid step.
    #
    global grid, saveeditor
    grid = (editor.grid, editor.gridstep)
    saveeditor = editor

def cleargrid():
    global grid
    grid = (0,0)



#
# Angle-aligning function.
#

def alignanglevect(v, mode):
    anglestep = quarkx.setupsubset(mode, "Building")["ForceAngleStep"][0]

    pitch,roll,yaw = vec2angles1(v)
    pitch = quarkx.rnd(pitch/anglestep)*anglestep
    roll = quarkx.rnd(roll/anglestep)*anglestep
    return angles2vec1(pitch, roll, yaw)


#
# Various angle conversion functions.
# angles are a string of 3 numbers : "pitch roll yaw" in degrees
#

def vec2angles1(v):
    if not v:
        return (0,0,0)
    if v.z:
        hlen = math.sqrt(v.x*v.x+v.y*v.y)
        pitch = math.atan2(-v.z, hlen) * rad2deg
        if not hlen:
            return (pitch,0,0)
    else:
        pitch = 0
    return (pitch, math.atan2(v.y,v.x) * rad2deg, 0)

def vec2angles(v, oldvalue=None):
    pitch, roll, yaw = vec2angles1(v)
    if oldvalue is not None:
        try:
            yaw = quarkx.vect(oldvalue).z
        except:
            pass
    return str(quarkx.vect(pitch, roll, yaw))

def vec2angle(v, oldvalue=None):
    hlen2 = v.x*v.x+v.y*v.y
    if hlen2 > v.z*v.z:
        angle = quarkx.rnd(math.atan2(v.y,v.x) * 180.0/math.pi)
        if angle>0:
            return `angle`
        return `angle+360`
    if v:
        if v.z > 0.0:
            return "-1"    # up
        else:
            return "-2"    # down
    return "0"

def angles2vec1(pitch, roll, yaw):
    roll = roll * deg2rad
    pitch = -pitch * deg2rad
    sin = math.sin
    cos = math.cos
    cosb = cos(pitch)
    return quarkx.vect(cos(roll)*cosb, sin(roll)*cosb, sin(pitch))

def angles2vec(s):
    return apply(angles2vec1, quarkx.vect(s).tuple)

def angle2vec(angle):
    angle = int(angle)
    if angle==-1:
        return quarkx.vect(0,0,1)
    if angle==-2:
        return quarkx.vect(0,0,-1)
    angle = angle * math.pi/180.0
    return quarkx.vect(math.cos(angle), math.sin(angle), 0)



#
# The handle classes.
#

class GenericHandle:
    "A handle on a view that can be grabbed with the mouse."

    #
    # a string used for the undo texts
    #
    undomsg = Strings[514]

    #
    # a string for the hint boxes
    #
    hint = ""

    def __init__(self, pos):
        self.pos = pos
        self.cursor = CR_DEFAULT     # default mouse cursor

    def draw(self, view, cv, draghandle=None):
        "Draw a handle on the given view."
        pass    # abstract

    def drawred(self, redimages, view, redcolor):
        "Draw a handle while it is being dragged."
        pass    # abstract

    def drag(self, v1, v2, flags, view):
        "Drag a handle."
        #
        # This method must return two lists :
        #  * the old objects
        #  * the new objects that replace them
        #
        return None, None    # abstract

    #
    # For setting stuff up at the beginning of a drag
    #
    def start_drag(self, view, x, y):
      pass

    #
    # old, new allow plugins etc to define extra stuff
    #  to be done before committal of changes
    #
    def ok(self, editor, undo, old, new, view=None):
      editor.ok(undo, self.undomsg)

    def menu(self, editor, view):
        "A pop-up menu for the handle."
        return []    # abstract

    def click(self, editor):
        "Handle a simple click."
        #
        # Usually ignored - the click is passed
        # through the handle and selects the next object.
        #
        pass

    def leave(self, editor):
        # See maphandles.py.
        pass

    def getdrawmap(self):
        #
        # Special behaviour is required for special cases only,
        # see maphandles.py.
        #
        return None, refreshtimer     # default behaviour

    def Action(self, editor, v1, v2, flags, view, undomsg=None):
        "Simulates a drag of the handle."

        if flags & MB_NOGRID:
            cleargrid()
        else:
            setupgrid(editor)
        undo = quarkx.action()
        import mdleditor
        if isinstance(editor, mdleditor.ModelEditor):
            try:
                old, ri = self.drag(v1, v2, flags, view, undo)
            except:
                old, ri = self.drag(v1, v2, flags, view)
        else:
            old, ri = self.drag(v1, v2, flags, view)
        if (ri is None) or (len(old)!=len(ri)):
            return
        if isinstance(editor, mdleditor.ModelEditor):
            if ri == []:
                try:
                    old, ri = self.drag(v1, v2, flags, view, undo)
                except:
                    old, ri = self.drag(v1, v2, flags, view)
            comp = editor.Root.currentcomponent
            compframes = comp.findallsubitems("", ':mf')   # get all frames
            for compframe in compframes:
                compframe.compparent = comp # To allow frame relocation after editing.
        for i in range(0,len(old)):
            undo.exchange(old[i], ri[i])
        editor.ok(undo, undomsg or self.undomsg)
        if flags & MB_NOGRID:
            setupgrid(editor)

    def OriginItems(self, editor, view):
        "Returns a list of menu items to set the coordinates of the handle."
        if view is None:
            return []
        def origin1click(m, self=self, editor=editor, view=view):
            def origin1change(newpos, self=self, editor=editor, view=view):
                self.Action(editor, self.pos, newpos, MB_NOGRID, view)
            XYZDialog(editor.form, origin1change, self.pos)
        return [qmenu.sep, qmenu.item("C&oordinates...", origin1click, "enter coordinates")]



class Rotate3DHandle(GenericHandle):
    "3D rotating handle, to set a direction."

    undomsg = Strings[513]
    hint = "rotate (Ctrl key: force to a common angle)|rotate this"
    # MODE required !

    def __init__(self, center, normal, scale1, icon):
        GenericHandle.__init__(self, center + normal*(lengthnormalvect/scale1))
        self.center = center
        self.normal = normal
        self.icon = icon
        if mapeditor() is not None:
            self.editor = mapeditor()
        else:
            self.editor = saveeditor

    def draw(self, view, cv, draghandle=None):
        "Draws the camera position eye line and ball handle"
        p1, p2 = view.proj(self.center), view.proj(self.pos)
    ## To trun off camera position and eye icon in selected 3D views using Terrain Generator 3D views Options dialog button
        editor = self.editor
        import mdleditor
        if isinstance(editor, mdleditor.ModelEditor):
            pass # To allow Eye ball handle to draw when needed.
        elif editor is not None and editor.layout is not None:
            tb2 = editor.layout.toolbars["tb_terrmodes"]
            if view.info["type"] == "3D":
                if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons1"] == "1":
                    if tb2.tb.buttons[11].state == 2:
                        view.cursor = CR_BRUSH
                        view.handlecursor = CR_BRUSH
                    elif tb2.tb.buttons[10].state == 2:
                        view.cursor = CR_HAND
                        view.handlecursor = CR_HAND
                    else:
                        if MapOption("CrossCursor", self.MODE):
                            view.cursor = CR_CROSS
                            view.handlecursor = CR_CROSS
                        else:
                            view.cursor = CR_ARROW
                            view.handlecursor = CR_ARROW
                    return
                if view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons2"] == "1":
                    if tb2.tb.buttons[11].state == 2:
                        view.cursor = CR_BRUSH
                        view.handlecursor = CR_BRUSH
                    elif tb2.tb.buttons[10].state == 2:
                        view.cursor = CR_HAND
                        view.handlecursor = CR_HAND
                    else:
                        if MapOption("CrossCursor", self.MODE):
                            view.cursor = CR_CROSS
                            view.handlecursor = CR_CROSS
                        else:
                            view.cursor = CR_ARROW
                            view.handlecursor = CR_ARROW
                    return

                else:
                    if MapOption("CrossCursor", self.MODE):
                        view.cursor = CR_CROSS
                        view.handlecursor = CR_ARROW
                    else:
                        view.cursor = CR_ARROW
                        view.handlecursor = CR_CROSS

        self.draw1(view, cv.reset(), p1, p2, p1<p2)

    def draw1(self, view, cv, p1, p2, fromback):
        editor = self.editor
        import mdleditor
        if isinstance(editor, mdleditor.ModelEditor):
            if view.viewmode == "wire":
                cv.pencolor = BLACK
            else:
                cv.pencolor = WHITE
        if p2.visible:
            if fromback:  # viewing from backwards
#py2.4                cv.draw(self.icon, p2.x-8, p2.y-8)
                cv.draw(self.icon, int(p2.x)-8, int(p2.y)-8)
                cv.line(p1, p2)
            else:            # viewing from forwards or from the side
                cv.line(p1, p2)
#py2.4                cv.draw(self.icon, p2.x-8, p2.y-8)
                cv.draw(self.icon, int(p2.x)-8, int(p2.y)-8)
        else:
            cv.line(p1, p2)

    def drawred(self, redimages, view, redcolor, oldnormal=None):
            "Draws the camera position eye line above in red when dragging"
        ## To trun off camera position and eye icon in selected 3D views using Terrain Generator 3D views Options dialog button
            if view.info["type"] == "3D":
                if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons1"] == "1": return
                if view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons2"] == "1": return
        ##if len(redimages):
            if oldnormal is None:
                try:
                    oldnormal = self.newnormal
                except AttributeError:
                    return
                if oldnormal is None:
                    return
            cv = view.canvas()
            cv.pencolor = redcolor
            cv.line(view.proj(self.center), view.proj(self.center+oldnormal*abs(self.pos-self.center)))
            return oldnormal

    def drag(self, v1, v2, flags, view):
        if MapOption("AutoAdjustNormal", self.MODE):
            flags = flags | MB_CTRL
        delta = v2-v1
        new = None
        self.draghint = ""
        av = self.pos + delta - self.center
        if av:
            if flags&MB_CTRL:
                av = alignanglevect(av, self.MODE)
            av = av.normalized
            if (flags&MB_REDIMAGE) or (av-self.normal):
                new = av
                pitch,roll,yaw = vec2angles1(av)
                self.draghint = "pitch %s    roll %s" % (quarkx.ftos(pitch), quarkx.ftos(roll))
        old, ri, self.newnormal = self.dragop(flags, new)
        return old, ri

    def menu(self, editor, view):

        def forceangle1click(m, self=self, editor=editor, view=view):
            self.Action(editor, self.pos, self.pos, MB_CTRL, view, Strings[559])

        anglestep = quarkx.setupsubset(self.MODE, "Building")["ForceAngleStep"][0]

        return [qmenu.item("&Force to nearest %s deg.\tCtrl" % quarkx.ftos(anglestep), forceangle1click,
          "|This command forces the angle to a 'round' value. It works like a kind of grid for angles.\n\nSet the 'angle grid' in the Configuration box, Map, Building, 'Force to angle'. See also the Options menu, 'Adjust angles automatically'.")]


def updatecenters(item,delta):
    if item["usercenter"]:
        center = quarkx.vect(item["usercenter"])
        item["usercenter"]=(center+delta).tuple
    for subitem in item.subitems:
#        debug('subitem '+subitem.name)
        updatecenters(subitem,delta)

class CenterHandle(GenericHandle):
    "Handle at the center of an object."

    hint = "move (Ctrl key: force to grid)|move with the mouse"
    
    def __init__(self, pos, centerof, color=RED, caninvert=0):
        GenericHandle.__init__(self, pos)
        self.centerof = centerof
        self.color = color
        if caninvert:
            self.colormask = WHITE
        else:
            self.colormask = 0

    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            # cv.pencolor is either black or white depending on the color layout
            cv.brushcolor = (cv.pencolor & self.colormask) ^ self.color
#py2.4            cv.rectangle(p.x-3, p.y-3, p.x+4, p.y+4)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)

    def drag(self, v1, v2, flags, view):
        delta = v2-v1
        if flags&MB_CTRL:
            g1 = grid[1]
        else:
            delta = aligntogrid(delta, 0)
            g1 = 0

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
            new = self.centerof.copy()
            new.translate(delta, g1)
            updatecenters(new,delta)
            new = [new]
        else:
            new = None
        return [self.centerof], new


class IconHandle(CenterHandle):
    "Like CenterHandle but displays an icon instead of a square."

    def __init__(self, pos, centerof, icon=None):
        CenterHandle.__init__(self, pos, centerof)

        if icon is None:
            #
            # Get the default icon for the given entity.
            #
            icon = centerof.geticon(1)

        self.icon = icon
        self.size = (8,8)


    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        if p.visible:
#py2.4            cv.draw(self.icon, p.x-8, p.y-8)
            cv.draw(self.icon, int(p.x)-8, int(p.y)-8)


#
# 3D views "eye" handles.
#

class EyePosition(GenericHandle):

    hint = "camera for the 3D view||This 'eye' represents the position of the camera of the 3D perspective view. You can use it to quickly move the camera elsewhere.\n\nIf several 3D views are opened, you will see several 'eyes', one for each camera.\n\nCamera position views can also be set and stored for quick viewing. See the Infobase for details on how to use this feature.|intro.mapeditor.floating3dview.html#camera"

    def __init__(self, view, view3D):
        pos, roll, pitch = view3D.cameraposition
        GenericHandle.__init__(self, pos)
        self.view3D = view3D
        self.normal = angles2vec1(pitch * rad2deg, roll * rad2deg, 0)
        self.view = view
        if self.view.info["type"] == "3D" and self.view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons1"] == "1" or self.view.info["type"] == "3D" and self.view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons2"] == "1":
            self.hint = "?"
        else:
            self.hint = "camera for the 3D view||This 'eye' represents the position of the camera of the 3D perspective view. You can use it to quickly move the camera elsewhere.\n\nIf several 3D views are opened, you will see several 'eyes', one for each camera.\n\nCamera position views can also be set and stored for quick viewing. See the Infobase for details on how to use this feature.|intro.mapeditor.floating3dview.html#camera"


    def drag(self, v1, v2, flags, view):
        pack = self.view3D.cameraposition
        if pack is not None:
            pos, roll, pitch = pack
            delta = v2-v1
            if not (flags&MB_CTRL):
                delta = aligntogrid(delta, 0)
            self.draghint = vtohint(delta)
            pos = self.pos + delta
            if flags&MB_CTRL:
                pos = aligntogrid(pos, 1)
            self.view3D.animation = flags&MB_DRAGGING
            self.view3D.cameraposition = pos, roll, pitch
            if flags&MB_DRAGGING:
                self.newpos = pos
                return [], []
        return None, None

    def drawred(self, redimages, view, redcolor, oldpos=None):
        "Draws red x in place of camera position eye icon when dragging"
    ## To trun off camera position and eye icon in selected 3D views using Terrain Generator 3D views Options dialog button
        if view.info["type"] == "3D":
            if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons1"] == "1": return
            if view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons2"] == "1": return
        if oldpos is None:
            try:
                oldpos = self.newpos
            except AttributeError:
                return
            if oldpos is None:
                return
        p = view.proj(oldpos)
        if p.visible:
            cv = view.canvas()
            cv.pencolor = redcolor
#py2.4            cv.line(p.x-3, p.y-3, p.x+4, p.y+4)
#py2.4            cv.line(p.x-3, p.y+3, p.x+4, p.y-4)
            cv.line(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)
            cv.line(int(p.x)-3, int(p.y)+3, int(p.x)+4, int(p.y)-4)
        return oldpos

    def draw(self, view, cv, draghandle=None):
        "Draws the camera position eye icon"
    ## To trun off camera position and eye icon in selected 3D views using Terrain Generator 3D views Options dialog button
        if view.info["type"] == "3D":
            if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons1"] == "1": return
            if view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons2"] == "1": return
        p = view.proj(self.pos)
        if p.visible:
            n = self.normal
            v1 = view.vector("X").normalized * n
            v2 = view.vector("Y").normalized * n
            if abs(v1)<0.3 and abs(v2)<0.3:
                if n*view.vector(self.pos) > 0:
                    icon = 0
                else:
                    icon = 1
            else:
                icon = 2 + (quarkx.rnd(math.atan2(v2, v1) * rad2deg / 45) & 7)
#py2.4            cv.draw(mapicons[icon], p.x-8, p.y-8)
            cv.draw(mapicons[icon], int(p.x)-8, int(p.y)-8)


class EyeDirection(Rotate3DHandle):

    hint = "camera direction||This is the direction the 'eye' is looking to. You can use it to quickly rotate the camera with the mouse.\n\nThe 'eye' itself represents the position of the camera of the 3D perspective view. You can use it to quickly move the camera elsewhere.\n\nIf several 3D views are opened, you will see several 'eyes', one for each camera.\n\nCamera position views can also be set and stored for quick viewing. See the Infobase for details on how to use this feature.|intro.mapeditor.floating3dview.html#camera"
    # MODE required !

    def __init__(self, view, view3D):
        self.camera = view3D.cameraposition
        forward = angles2vec1(self.camera[2] * rad2deg, self.camera[1] * rad2deg, 0)
        if mapeditor() is not None:
            editor = mapeditor()
        else:
            editor = saveeditor
        import mdleditor
        if isinstance(editor, mdleditor.ModelEditor):
            Rotate3DHandle.__init__(self, self.camera[0], forward, view.info['scale'], mapicons[12])
        else:
            Rotate3DHandle.__init__(self, self.camera[0], forward, view.scale(), mapicons[12])
        self.view3D = view3D
        self.view = view
        if self.view.info["type"] == "3D" and self.view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons1"] == "1" or self.view.info["type"] == "3D" and self.view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MAP, "Options")["Options3Dviews_noicons2"] == "1":
            self.hint = "?"
        else:
            self.hint = "camera direction||This is the direction the 'eye' is looking to. You can use it to quickly rotate the camera with the mouse.\n\nThe 'eye' itself represents the position of the camera of the 3D perspective view. You can use it to quickly move the camera elsewhere.\n\nIf several 3D views are opened, you will see several 'eyes', one for each camera.\n\nCamera position views can also be set and stored for quick viewing. See the Infobase for details on how to use this feature.|intro.mapeditor.floating3dview.html#camera"

    def dragop(self, flags, av):
        if av is not None:
            self.view3D.animation = flags&MB_DRAGGING
            pos, roll, pitch = self.camera
            pitch, roll, yaw = vec2angles1(av)
            self.view3D.cameraposition = pos, roll * deg2rad, pitch * deg2rad
            if flags&MB_DRAGGING:
                return [], [], av
        return None, None, av


#
# Linear Mapping Circle handles.
#

class LinearHandle(GenericHandle):
    "Linear Box handles."

    def __init__(self, pos, mgr):
        GenericHandle.__init__(self, pos)
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

    def linoperation(self, list, delta, g1, view):
        matrix = self.buildmatrix(delta, g1, view)
        if matrix is None: return
        for obj in list:
            obj.linear(self.center, matrix)

        return 1


class LinRedHandle(LinearHandle):
    "Linear Box: Red handle at the center."

    hint = "           move selection (Ctrl key: force to grid)|move selection"

    def __init__(self, pos, mgr):
        LinearHandle.__init__(self, pos, mgr)
        self.cursor = CR_MULTIDRAG

    def draw(self, view, cv, draghandle=None):

        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = self.mgr.color
#py2.4            cv.rectangle(p.x-3, p.y-3, p.x+4, p.y+4)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)

    def linoperation(self, list, delta, g1, view):
        for obj in list:
            obj.translate(delta, g1 and grid[0])

        if view.info["type"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["type"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + " " + ftoss(self.pos.z+delta.z)
        elif view.info["type"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            s = "was: " + vtoposhint(self.pos) + " now: " + vtoposhint(delta + self.pos)
        self.draghint = s

        return delta


class LinSideHandle(LinearHandle):
    "Linear Box: Red handle at the side for distortion/shearing."

    undomsg = Strings[527]
    hint = "enlarge / shear (Ctrl key: either enlarge or shear)||This handle lets you distort the selected object(s).\n\nIf you move the handle in the direction of or away from the center, you will shrink or enlarge the objects correspondingly. If you move the handle in the other direction, you will 'shear' the objects. Hold down the Ctrl key to prevents the objects from being enlarged and sheared at the same time."

    def __init__(self, center, side, dir, mgr, firstone):
        pos1 = quarkx.vect(center.tuple[:dir] + (side.tuple[dir],) + center.tuple[dir+1:])
        LinearHandle.__init__(self, pos1, mgr)
        self.center = center - (pos1-center)
        self.dir = dir
        self.firstone = firstone
        self.inverse = side.tuple[dir] < center.tuple[dir]
        self.cursor = CR_LINEARV

    def draw(self, view, cv, draghandle=None):
        if self.firstone:
            self.mgr.drawbox(view)   # draw the full box
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = self.mgr.color
#py2.4            cv.rectangle(p.x-2.5, p.y-2.5, p.x+3.5, p.y+3.5)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)

    def buildmatrix(self, delta, g1, view):
        npos = self.pos+delta
        if g1:
             npos = aligntogrid(npos, 1)
        normal = view.vector("Z").normalized
        dir = self.dir
        v = (npos - self.center) / abs(self.pos - self.center)
        if self.inverse:
            v = -v
        m = [quarkx.vect(1,0,0), quarkx.vect(0,1,0), quarkx.vect(0,0,1)]
        if g1:
            w = list(v.tuple)
            x = w[dir]-1
            if x*x > w[dir-1]*w[dir-1] + w[dir-2]*w[dir-2]:
                w[dir-1] = w[dir-2] = 0   # force distortion in this single direction
            else:
                w[dir] = 1                # force pure shearing
            v = quarkx.vect(tuple(w))
        else:
            w = v.tuple
        self.draghint = "enlarge %d %%   shear %d deg." % (100.0*w[dir], math.atan2(math.sqrt(w[dir-1]*w[dir-1] + w[dir-2]*w[dir-2]), w[dir])*180.0/math.pi)
        m[dir] = v

        return quarkx.matrix(tuple(m))

       # v = self.pos - self.center
       # diff = v * (npos - self.center) / (v.x*v.x+v.y*v.y+v.z*v.z)
       # if abs(diff-1) < epsilon: return
       # dir = self.dir
       # return quarkx.matrix(
       #   (dir!=0 or diff, 0, 0),
       #   (0, dir!=1 or diff, 0),
       #   (0, 0, dir!=2 or diff))


class LinCornerHandle(LinearHandle):
    "Linear Box: Red handle at the corner for rotation/zooming."

    undomsg = Strings[528]
    hint = "zoom / rotate (Ctrl key: either zoom or rotate)||This handle lets you rotate and scale the selected object(s).\n\nIf you move the handle in the direction of or away from the center, you will zoom the objects and make them smaller or larger. If you move the handle around the center, the objects rotate. Hold down the Ctrl key to prevent zooming and rotation to occur simultaneously."

    def __init__(self, center, pos1, mgr, realpoint=None):
        LinearHandle.__init__(self, pos1, mgr)
        if realpoint is None:
            self.pos0 = pos1
        else:
            self.pos0 = realpoint
        self.center = center - (pos1-center)
        self.cursor = CR_CROSSH

    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = self.mgr.color
#py2.4            cv.polygon([(p.x-3,p.y), (p.x,p.y-3), (p.x+3,p.y), (p.x,p.y+3)])
            cv.polygon([(int(p.x)-3,int(p.y)), (int(p.x),int(p.y)-3), (int(p.x)+3,int(p.y)), (int(p.x),int(p.y)+3)])

    def buildmatrix(self, delta, g1, view):
        normal = view.vector("Z").normalized
        texp4 = self.pos-self.center
        texp4 = texp4 - normal*(normal*texp4)
        npos = self.pos + delta
        if g1:
            npos = aligntogrid(npos, 1)
        npos = npos-self.center
        npos = npos - normal*(normal*npos)
        m = diff = None
        if g1 and npos:
            v = npos.normalized * abs(texp4)
            if abs(v-texp4) > abs(v-npos):
                diff = 1.0  # force pure rotation
            else:
                m = quarkx.matrix((1,0,0),(0,1,0),(0,0,1))    # force pure zooming
        if m is None:
            m = UserRotationMatrix(normal, npos, texp4, 0)
            if m is None: return
        if diff is None: diff = abs(npos) / abs(texp4)
        self.draghint = "rotate %d deg.   zoom %d %%" % (math.acos(m[0,0])*180.0/math.pi, 100.0*diff)

        return m * diff



def AutoScrollTimer(info):
    sender, x, y = info
    view = sender.view
    try:
        layout = view.owner.info.layout
    except:
        return
    hbar, vbar = view.scrollbars
    MakeScroller(layout, view)(hbar[0] + x, vbar[0] + y)
    sender.x0 = sender.x0 - x
    sender.y0 = sender.y0 - y
    return 80

#
# Setup Handle hints.
#

def FilterHandles(handlelist, mode):
    if not MapOption("HandleHints", mode):
        for handle in handlelist:
            try:
                if handle.hint[0] != "?":
                    handle.hint = ""
            except:
                pass
    return handlelist

#
# Function that computes a rotation matrix out of a mouse movement.
#

def UserRotationMatrix(normal, newpos, oldpos, g1, rotationspeed=1.0):
    # normal: normal vector for the view plane
    # newpos: new position of the reference vector oldpos
    # oldpos: reference vector (handle position minus rotation center)
    # g1: if True, snap angle to grid
    # rotationspeed, example .5 = half rotation speed, 2.0 = twice as fast.
    if not normal: return
    SNAP = 0.998
    if not oldpos: return
    norme1 = abs(oldpos)
    if not newpos: return
    norme2 = abs(newpos)
    sinangle = (normal*(oldpos^newpos)) / (norme1*norme2)
    if rotationspeed != 1.0:
        sinangle = math.sin(math.asin(sinangle) * rotationspeed)
    norme1 = sinangle*sinangle
    if norme1 > SNAP:
        if sinangle>0:
            sinangle=1
        else:
            sinangle=-1
        cosangle=0
    else:
        cosangle=1-norme1
        if cosangle > SNAP:
            sinangle, cosangle = 0, 1
        else:
            cosangle = math.sqrt(cosangle)
        if newpos * oldpos < 0:
            cosangle = -cosangle
        if cosangle == 1:
            return
    if g1:
        if abs(cosangle)>abs(sinangle):
            sinangle = 0
            cosangle = (-1,1)[cosangle>0]
        else:
            cosangle = 0
            sinangle = (-1,1)[sinangle>0]
    m = quarkx.matrix((cosangle,  sinangle, 0),
                      (-sinangle, cosangle, 0),
                      (    0,        0,     1))
    v = orthogonalvect(normal, None)
    base = quarkx.matrix(v, v^normal, -normal)
    return base * m * (~base)

#
# Drag Objects are created when a mouse drag begins and
# destroyed when it ends. See MapEditor.dragobject.
#
# The class DragObject is only a base class; handle drags
# are handled by the HandleDragObject class.
#

class DragObject:
    "Stores information about the current mouse drag."

    redimages = None
    handle = None
    hint = None

    def __init__(self, view, x, y, z):
        self.view = view
        self.x0 = x
        self.y0 = y
        self.z0 = z
        self.pt0 = view.space(x, y, z)
        self.scrolltimer = None

    def dragto(self, x, y, flags):
        "Called by the map editor when the mouse moves."
        pass   # abstract

    def ok(self, editor, x, y, flags):
        "Called when the drag ends."
        pass   # abstract

    def drawredimages(self, view):
        pass   # abstract

    def backup(self):
        return None, None

    def autoscroll_stop(self):
        if self.scrolltimer is not None:
            quarkx.settimer(AutoScrollTimer, self.scrolltimer, 0)
            self.scrolltimer = None

    def autoscroll(self, x, y):
        if self.view.info["type"] == "3D":
            return
        w,h = self.view.clientarea
        if x>=0 and y>=0 and x<w and y<h:
            self.autoscroll_stop()
            return
        if x<0: x=-32
        elif x>=w: x=32
        else: x=0
        if y<0: y=-32
        elif y>=h: y=32
        else: y=0
        timer = (self, x, y)
        if timer != self.scrolltimer:
            quarkx.settimer(AutoScrollTimer, self.scrolltimer, 0)
            self.scrolltimer = timer
            quarkx.settimer(AutoScrollTimer, self.scrolltimer, 80)


#
# RedImageDragObject is an abstract class that can display red
# wireframe images while the user drags the mouse. Subclasses
# of this are HandleDragObject, which draws the map objects
# while they are distorted, and RectangleDragObject, which
# displays a red rectangle.
#


class RedImageDragObject(DragObject):
    "Dragging that draws a red wireframe image of something."

    def __init__(self, view, x, y, z, redcolor):
        DragObject.__init__(self, view, x, y, z)
        self.x = x        ## Added this for Terrain objects - cdunde 05-14-05
        self.y = y        ## Added this for Terrain objects - cdunde 05-14-05
        self.z = z        ## Added this for Terrain objects - cdunde 05-14-05
        ### Added these for invalidating drag rectangle area only - cdunde 08-28-08
        self.xmin = self.ymin = self.xmax = self.ymax = None
        self.redcolor = redcolor
        self.redhandledata = None
## the lines below were added for the Terrain Generator
        editor = mapeditor()
        if editor is None:
            quarkx.clickform = view.owner  # Rowdys -important, gets the editor
            editor = mapeditor()
            if editor is None:
                import mdleditor
                editor = mdleditor.mdleditor
        self.editor = editor
        self.view = view
        self.newx = x
        self.newy = y
        self.newz = z
## the lines above where added for the Terrain Generator

    def buildredimages(self, x, y, flags):
        return None, None   # abstract

    def ricmd(self):
        return None, refreshtimer     # default behaviour

    def dragto(self, x, y, flags):
        self.xmin is None
        self.xmax is None
        self.ymin is None
        self.ymax is None
        self.flags = flags
        if x < self.xmin or self.xmin is None:
            self.xmin = x
        if y < self.ymin or self.ymin is None:
            self.ymin = y
        if x > self.xmax or self.xmax is None:
            self.xmax = x
        if y > self.ymax or self.ymax is None:
            self.ymax = y
        if flags&MB_DRAGGING:
            self.autoscroll(x,y) # old is the object at its original position at the very beginning of a drag. This does not change.
        old, ri = self.buildredimages(x, y, flags) # ri stands for 'redimage'. It's the object while it's being moved in a drag.
        if self.view.info["type"] != "3D":
            self.drawredimages(self.view, 1) # 1 is 'internal' value. If commented out draws green rectangle.
            self.redimages = ri

       ### This is for the Model Editor Skin-view RedImageDragObject use only.
            try:
                import mdlhandles
                if self.view.info["viewname"] == "skinview":
                    if isinstance(self.editor.dragobject.handle, mdlhandles.SkinHandle):
                        ### To stop the Model Editor from drawing incorrect component image in Skin-view.
                        pass
                    else:
                        if self.redimages is not None:
                            mode = DM_OTHERCOLOR|DM_BBOX
                            special, refresh = self.ricmd()
                            if refresh is not None:
                                rectanglecolor = MapColor("SkinVertexSelListColor", SS_MODEL)
                                for r in self.redimages: # Draws selected vertex rectangles while dragging.
                                    self.view.drawmap(r, mode, rectanglecolor)
                else:
                    import plugins.mdlcamerapos
                    if isinstance(self.editor.dragobject.handle, plugins.mdlcamerapos.CamPosHandle) or isinstance(self.editor.dragobject.handle, mdlhandles.CenterHandle):
                        self.drawredimages(self.view, 1)
                        self.drawredimages(self.view, 2)
            except:
                pass

            if flags&MB_DRAGGING:
                self.drawredimages(self.view, 2)
        else:
            if flags&MB_DRAGGING:
                if self.view.viewmode == "tex":
                    self.redimages = ri
                #    self.view.repaint()
                    try:
                        import plugins.mdlcamerapos, mdlhandles
                        if isinstance(self.editor.dragobject.handle, plugins.mdlcamerapos.CamPosHandle) or isinstance(self.editor.dragobject.handle, mdlhandles.CenterHandle):
                            self.drawredimages(self.view, 1)
                    except:
                        pass
                    self.drawredimages(self.view, 2)
                else:
                    self.redimages = ri
                    self.drawredimages(self.view, 1)
                    self.drawredimages(self.view, 2)
            else:
                self.redimages = ri
                self.drawredimages(self.view, 1)
        return old

    def drawredimages(self, view, internal=0):
        editor = self.editor
        import mdleditor
        if isinstance(editor, mdleditor.ModelEditor):
            editor = mdleditor.mdleditor
            import mdlhandles
            ### Stops Model Editor Vertex drag handles from drawing if not returned.
            ### Also fixes a Ctrl snap to grid drag from breaking.
            if isinstance(editor.dragobject.handle, mdlhandles.VertexHandle) or isinstance(editor.dragobject.handle, mdlhandles.TagHandle):
                return
            ### Stops Model Editor Linear drag handles from drawing the model's MESH incorrectly (in miniature) in the Skin-view
            ### and stops Model Editor Linear drag handles from drawing redline drag objects incorrectly.
            if ( view.info["viewname"] == "skinview" or quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1") and (isinstance(editor.dragobject.handle, mdlhandles.LinRedHandle) or isinstance(editor.dragobject.handle, mdlhandles.LinSideHandle) or isinstance(editor.dragobject.handle, mdlhandles.LinCornerHandle)):
                return
            # Draws rectangle selector and Skin-view lines much faster this way.
            if view.info["viewname"] == "skinview":
                if isinstance(editor.dragobject.handle, mdlhandles.SkinHandle):
                    ### Stops Model Editor Skin-view Vertex drag handles from drawing if not returned and
                    ### draws erroneous image of the model in the Skin-view if allowed to continue on like below.
                    return
                else:
                    # This area draws the rectangle selector (and view handles if added)
                    #   in the Model Editor Skin-view when it pauses.
                    if self.redimages is not None:
                        mode = DM_OTHERCOLOR|DM_BBOX
                        rectanglecolor = MapColor("SkinDragLines", SS_MODEL)
                        for r in self.redimages:
                            view.drawmap(r, mode, rectanglecolor)
        else:
## Deals with Terrain Selector 3D face drawing, movement is in ok section
            if (editor is not None) and (editor.layout.toolbars["tb_terrmodes"] is not None):
                tb2 = editor.layout.toolbars["tb_terrmodes"]
                for b in tb2.tb.buttons:
                    if b.state == 2:
                        if len(editor.layout.explorer.sellist) > 1:
                            if self.redimages is not None:
                                for r in self.redimages:
                                    if r.name == ("redbox:p"):
                                        continue
                                    else:
                                        type = view.info["type"]
                                        if type == "3D":
                                            qbaseeditor.BaseEditor.finishdrawing = newfinishdrawing
                                            return
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # can draw a red image only
                if internal==1:    # erase the previous image
                    try:
                        for r in self.redimages:
                            view.drawmap(r, mode)
                    except:
                        pass
## cdunde added these 3 lines 05-14-05 to stop the
## 3d Textured view from erasing other items
## in the view when dragging redline objects in it.

## Deals with Standard Selector 3D face drawing, movement is in ok section
                    type = view.info["type"]
                    if type == "3D":
                        # during 1 face drag both go here but TG better, no hang
                        view.repaint()
                        return
                    if self.redhandledata is not None:
                        self.handle.drawred(self.redimages, view, view.color, self.redhandledata)
                else:
                    if editor is None:
                        for r in self.redimages:
                            if r.name != ("redbox:p"):
                                return
                            else:
                                view.drawmap(r, mode, self.redcolor)
                        if self.handle is not None:
                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)
                    else:
                        if isinstance(editor, mdleditor.ModelEditor):
                            # This area draws the rectangle selector and view handles
                            #   in the Model Editor 3D and 2D view while dragging.
                            # It also does one draw of the rectangle selector for the
                            #   Skin-view when a pause in the drag takes place.
                            if view.info["viewname"] == "skinview":
                                rectanglecolor = MapColor("SkinDragLines", SS_MODEL)
                                for r in self.redimages:
                                    view.drawmap(r, mode, rectanglecolor)
                                if self.handle is not None:
                                    self.redhandledata = self.handle.drawred(self.redimages, view, rectanglecolor)
                            else:
                                reccolor = MapColor("Drag3DLines", SS_MODEL)
                                # Really slows down the editors 2D view rectangle selection
                                # when the view handles are being drawn if we don't kill them here.
                                # They do still exist at the end of the drag though.
                                try:
                                    for r in self.redimages:
                                        view.drawmap(r, mode, reccolor)
                                except:
                                    pass
                                try:
                                    import plugins.mdlcamerapos
                                    if isinstance(self.editor.dragobject.handle, plugins.mdlcamerapos.CamPosHandle) or isinstance(self.editor.dragobject.handle, mdlhandles.CenterHandle):
                                        return
                                except:
                                    pass
                                if self.handle is not None:
                                    self.redhandledata = self.handle.drawred(self.redimages, view, reccolor)

## Deals with Terrain Selector 2D face drawing, movement is in ok section and
## Deals with Standard Selector 2D face drawing, movement is in ok section
                        elif editor.layout.toolbars["tb_terrmodes"] is not None:
                            tb2 = editor.layout.toolbars["tb_terrmodes"]
                            for b in tb2.tb.buttons:
                                if b.state == 2:
                                    if len(editor.layout.explorer.sellist) > 1:
                                        for r in self.redimages:
                                            if r.name != ("redbox:p"):
                                             #   TG goes here AFTER mouse release
                                             #   for multi faces drag in 3D view
                                                view.update()
                                                qbaseeditor.BaseEditor.finishdrawing = newfinishdrawing
                                                return
                                            else:
                                                view.drawmap(r, mode, self.redcolor)
                                          #      self.view.invalidate()
                                                qbaseeditor.BaseEditor.finishdrawing = newfinishdrawing

                                                return
                                        if self.handle is not None:
                                            self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

                            for r in self.redimages:
                                try:
                                    view.drawmap(r, mode, self.redcolor)
                                except:
                                    pass
                            if self.handle is not None:
                                self.redhandledata = self.handle.drawred(self.redimages, view, self.redcolor)

            else:   # must redraw everything
                if internal==2:
                    view.invalidate()
            if internal==2:    # set up a timer to update the other views as well
                if isinstance(editor, mdleditor.ModelEditor) and self.view.info["viewname"] == "skinview":
                    quarkx.settimer(refresh, self, 50)
                else:
                    try:
                        if self.handle.g1 == 1:
                            pass
                    except:
                        quarkx.settimer(refresh, self, 150)


    def backup(self):
        special, refresh = self.ricmd()
        if (special is None) or (self.redimages is None):
            return None, None
        backup = special.copy()
        special.copyalldata(self.redimages[0])
        return special, backup


    def ok(self, editor, x, y, flags, view=None):   # default behaviour is to create an object out of the red image
        global skinviewold, skinviewnew, skinviewdraghandle  # used for model editor
        self.autoscroll_stop()

        import mdleditor
        if isinstance(editor, mdleditor.ModelEditor):
            try:
                import mdlhandles
                if isinstance(self.handle, mdlhandles.PFaceHandle) or isinstance(self.handle, mdlhandles.PolyHandle) or isinstance(self.handle, mdlhandles.PVertexHandle):
                    old = self.dragto(x, y, flags)
                    if (self.redimages is None) or (len(old)!=len(self.redimages)):
                        qbaseeditor.BaseEditor.finishdrawing = newfinishdrawing
                        return
                elif self.view.info['viewname'] != "skinview" and  quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
                    self.handle.ok(editor, None, None, self.redimages, self.view)
                    return
            except:
                pass
            skinviewdraghandle = self
            old = self.dragto(x, y, flags)
        else:
            old = self.dragto(x, y, flags)
            if (self.redimages is None) or (len(old)!=len(self.redimages)):
                qbaseeditor.BaseEditor.finishdrawing = newfinishdrawing
                return

## This section added for Terrain Generator - stops broken faces - cdunde 05-19-05

        import mapeditor
        if isinstance(editor, mapeditor.MapEditor):
            tb2 = editor.layout.toolbars["tb_terrmodes"]
## Deals with Terrain Selector movement, face drawing is in drawredimages section
            for b in tb2.tb.buttons:
                if b.state == 2:
                    if len(editor.layout.explorer.sellist) > 1:
                        type = self.view.info["type"]
                        if type == "3D":
                            self.view.invalidate()
                        editor.invalidateviews()
                        qbaseeditor.BaseEditor.finishdrawing = newfinishdrawing
                        break

## Deals with Sandard Selector movement, face drawing is in drawredimages section
            else:
                undo = quarkx.action()
                for i in range(0,len(old)):
                    undo.exchange(old[i], self.redimages[i])
                self.handle.ok(editor, undo, old, self.redimages)
                qbaseeditor.BaseEditor.finishdrawing = newfinishdrawing
                return

## Deals with Model Editor Skin-view movement, face drawing is in python\mdlhandles.py class SkinHandle section
        if isinstance(editor, mdleditor.ModelEditor) and old is not None and self.redimages is not None:
            try:
                if self.redimages[0].type == ":mc":
                    compframes = self.redimages[0].findallsubitems("", ':mf')   # get all frames
                    for compframe in compframes:
                        compframe.compparent = self.redimages[0] # To allow frame relocation after editing.
                undo = quarkx.action()
                for i in range(0,len(old)):
                    undo.exchange(old[i], self.redimages[i])
                self.handle.ok(editor, undo, old, self.redimages)
                if self.redimages[0].type == ":mf":
                    compframes = editor.Root.currentcomponent.findallsubitems("", ':mf')   # get all frames
                    for compframe in compframes:
                        compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.
            except:
                pass

## End of above section for Terrain Generator changes


class HandleDragObject(RedImageDragObject):

    def __init__(self, view, x, y, handle, redcolor):
        RedImageDragObject.__init__(self, view, x, y, view.proj(handle.pos).z, redcolor)
        self.pt0 = handle.pos
        self.handle = handle
        handle.start_drag(view, x, y)

    def buildredimages(self, x, y, flags):
        pt1 = self.view.space(x, y, self.z0)
        result = self.handle.drag(self.pt0, pt1, flags, self.view)
        try:
            self.hint = self.handle.draghint
        except:
            pass
        return result

    def ricmd(self):
        return self.handle.getdrawmap()



def refreshtimer(self):
    editor = self.editor
    import mdleditor
    if editor is None:
        editor = mdleditor.mdleditor
    if isinstance(editor, mdleditor.ModelEditor):
        from qbaseeditor import flagsmouse
        if flagsmouse == 16384:
            try:
                import mdlhandles
                if isinstance(editor.dragobject.handle, mdlhandles.MdlEyeDirection) or isinstance(editor.dragobject.handle, EyePosition):
                    pass
                else:
                    editor.dragobject = None
            except:
                editor.dragobject = None
            return
        if flagsmouse != 1032:
            # This area draws the rectangle selector and view handles
            #   in the Model Editor 3D view when it pauses.
            if self.view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                self.view.handles = []
                return
            elif self.view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                self.view.handles = []
                return
            elif self.view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                self.view.handles = []
                return
            elif self.view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                self.view.handles = []
                return
            elif self.view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                self.view.handles = []
                return
            else:
                if len(self.view.handles) == 0:
                    import mdlhandles
                    self.view.handles = mdlhandles.BuildHandles(editor, editor.layout.explorer, self.view)
            if flagsmouse == 1072:
                mdleditor.setsingleframefillcolor(editor, self.view)
                self.view.repaint()
                try:
                    if editor.ModelFaceSelList != []:
                        import mdlhandles
                        mdlhandles.ModelFaceHandle(GenericHandle).draw(editor, self.view, editor.EditorObjectList)
                except:
                    pass
            cv = self.view.canvas()
            for h in self.view.handles:
                h.draw(self.view, cv, self)
            try:
                if editor.ModelVertexSelList != []:
                    for vtx in editor.ModelVertexSelList:
                        h = self.view.handles[vtx]
                        h.draw(self.view, cv, h)
            except:
                pass
            if flagsmouse == 1072:
                mode = DM_OTHERCOLOR|DM_BBOX
                reccolor = MapColor("Drag3DLines", SS_MODEL)
                if self.redimages is not None:
                    for r in self.redimages:
                        self.view.drawmap(r, mode, reccolor)
            return
        if flagsmouse == 1032:
            import mdlhandles
            if isinstance(editor.dragobject, mdlhandles.RectSelDragObject):
                # This area draws the rectangle selector and view handles
                #   in the Model Editor 2D view or Skin-view when it pauses.
                mode = DM_OTHERCOLOR|DM_BBOX
                if self.redimages is not None:
                    if self.view.info["viewname"] == "skinview":
                        self.view.repaint()
                        rectanglecolor = MapColor("SkinDragLines", SS_MODEL)
                        for r in self.redimages:
                            self.view.drawmap(r, mode, rectanglecolor)
                    else:
                        if len(self.view.handles) == 0:
                            import mdlhandles
                            self.view.handles = mdlhandles.BuildHandles(editor, editor.layout.explorer, self.view)
                  # Line below stops the editor 2D view handles from drawing during rec drag after the timer
                  # goes off one time, but does not recreate the handles if nothing is selected at end of drag.
                  #      self.view.handles = []
                        self.view.invalidaterect(self.xmin, self.ymin, self.xmax, self.ymax)
                        newxmin = newxmax = self.x
                        newymin = newymax = self.y
                        if self.newx < newxmin:
                            newxmin = self.xmin
                        if self.newx > newxmax:
                            newxmax = self.xmax
                        if self.newy < newymin:
                            newymin = self.ymin
                        if self.newy > newymax:
                            newymax = self.ymax
                        self.xmin = newxmin
                        self.xmax = newxmax
                        self.ymin = newymin
                        self.ymax = newymax
            else:
                if not isinstance(editor.dragobject, mdlhandles.LinearHandle):
                    return
        else:
            pass
    else:
        try:
            for v in self.views:
                v.invalidate()
        except:
            for v in editor.layout.views:
                v.invalidate()

def refreshtimertex(self):
    for v in self.views:
        if (v.viewmode == "tex") and (v is not self.view):
            v.invalidate(1)

#
# Free Zoom in/out following the mouse move.
#

class FreeZoomDragObject(DragObject):

    BaseSensitivity = 0.007
    AbsoluteMinimum = 0.001
    AbsoluteMaximum = 100.0
    InfiniteMouse   = 1
    # MODE required !

    def __init__(self, viewlist, view, x, y):
        self.x0 = x
        self.y0 = y
        self.scale0 = view.info["scale"]
        if view.info.has_key("custom"):
            self.viewlist = [view]
        else:
            self.viewlist = viewlist
        self.view = view

    def dragto(self, x, y, flags):
        # moving the mouse RIGHT means zoom IN
        # moving the mouse DOWN also means zoom IN
        # if you are unhappy with this, change it here...
        # or set a negative value in the Configuration dialog for this

        # For Model Editor needs.
        if self.MODE == SS_MODEL:
            # To increase zoom in ability for detailed painting selection of pixels.
            if self.view.info["viewname"] == "skinview":
                self.AbsoluteMaximum = 30.0
            else:
                self.AbsoluteMaximum = 500.0
            # To free up the L & CMB for other function use in the Model Editor.
            from qbaseeditor import flagsmouse
            if flagsmouse == 288 or flagsmouse == 296 or flagsmouse == 552 or flagsmouse == 800 or flagsmouse == 1064 or flagsmouse == 2088:
                self.dragobject = None
                return

        sensitivity, = quarkx.setupsubset(self.MODE, "Display")["FreeZoom"]

        scale = self.scale0 * math.exp((x-self.x0+y-self.y0) * sensitivity * self.BaseSensitivity)
        if scale<self.AbsoluteMinimum:
            scale=self.AbsoluteMinimum
        elif scale>self.AbsoluteMaximum:
            scale=self.AbsoluteMaximum
        setviews(self.viewlist, "scale", scale)

        ### To enable Model Editor multiple meshfill color selection zooming.
        try:
            if (self.view.info["viewname"] == "XY" or self.view.info["viewname"] == "XZ" or self.view.info["viewname"] == "YZ"):
                quarkx.clickform = self.view.owner
                editor = mapeditor()
                import mdleditor
                if isinstance(editor, mdleditor.ModelEditor):
                    mdleditor.commonhandles(editor)
            else:
                self.view.repaint()
        except:
            self.view.repaint()

#
# Scroll the view while the mouse moves.
#

def MakeScroller(layout, view):
    sbviews = [None, None]
    for ifrom, linkfrom, ito, linkto in layout.sblinks:
        if linkto is view:
            sbviews[ito] = (ifrom, linkfrom)
    def scroller(x, y, view=view, hlink=sbviews[0], vlink=sbviews[1]):
        view.scrollto(x, y)
        if hlink is not None:
            if hlink[0]:
                hlink[1].scrollto(None, x)
            else:
                hlink[1].scrollto(x, None)
        if vlink is not None:
            if vlink[0]:
                vlink[1].scrollto(None, y)
            else:
                vlink[1].scrollto(y, None)
        view.update()
    return scroller


class ScrollViewDragObject(DragObject):

    InfiniteMouse = 1

    def __init__(self, editor, view, x, y):
        hbar, vbar = view.scrollbars
        self.view = view
        self.x0 = hbar[0] + x
        self.y0 = vbar[0] + y
        self.scroller = MakeScroller(editor.layout, view)

    def dragto(self, x, y, flags):
        try:
            import mdleditor
            if isinstance(editor, mdleditor.ModelEditor):
                if view.info["viewname"] == "skinview":
                    x = self.x0-x
                    y = self.y0-y
        except:
            x = self.x0-x
            y = self.y0-y
            self.scroller(x, y)


#
# Mouse Free View like in Quake.
#

class AnimatedDragObject(DragObject):
    def ok(self, editor, x, y, flags):
        self.view.animation = 0


class FreeViewDragObject(AnimatedDragObject):

    InfiniteMouse = 1

    def __init__(self, editor, view, x, y):
        self.view = view
        self.x0 = x
        self.y0 = y
        self.pos0, self.roll0, self.pitch0 = self.view.cameraposition
        #
        # Read sensitivity (neg. numbers invert movements).
        #
        setup = quarkx.setupsubset(SS_GENERAL, "3D view")
        self.f0 = setup["MouseHLook"][0] * 0.0006, setup["MouseVLook"][0] * 0.0006

    def dragto(self, x, y, flags):
        x = self.x0-x
        y = self.y0-y
        fx, fy = self.f0
        roll = self.roll0 + x*fx
        pitch = self.pitch0 + y*fy
        if pitch<-1.5: pitch = -1.5
        elif pitch>1.5: pitch = 1.5

        self.view.animation = 1
        try:
            self.view.cameraposition = self.pos0, roll, pitch
        except:
            self.view.invalidate(1)

#
# Mouse Walk like in Quake.
#

class WalkDragObject(AnimatedDragObject):

    InfiniteMouse = 1

    def __init__(self, editor, view, x, y):
        self.view = view
        self.x0 = x
        self.y0 = y
        self.pos0, self.roll0, self.pitch0 = self.view.cameraposition
        #
        # Read sensitivity (neg. numbers invert movements).
        #
        setup = quarkx.setupsubset(SS_GENERAL, "3D view")
        self.f0 = setup["MouseHLook"][0] * 0.0006, setup["MouseWalk"][0] * 0.32

    def dragto(self, x, y, flags):
        x = self.x0-x
        y, self.y0 = self.y0-y, y
        fx, fy = self.f0
        roll = self.roll0 + x*fx
        forward = angles2vec1(self.pitch0*rad2deg, roll*rad2deg, 0)
        pos = self.pos0 + forward*y * fy

        self.view.animation = 1
        try:
            self.view.cameraposition = pos, roll, self.pitch0
        except:
            self.view.invalidate(1)
        self.pos0 = pos

#
# Mouse SideStep walk (left-right-up-down).
#

class SideStepDragObject(AnimatedDragObject):

    InfiniteMouse = 1

    def __init__(self, editor, view, x, y):
        self.view = view
        self.x0 = x
        self.y0 = y
        self.camerapos0 = self.view.cameraposition
        if self.camerapos0 is None: return
        forward = angles2vec1(self.camerapos0[2]*rad2deg, self.camerapos0[1]*rad2deg, 0)
        left = orthogonalvect(forward, editor.layout.views[0])
        #
        # Read sensitivity (neg. numbers invert movements).
        #
        setup = quarkx.setupsubset(SS_GENERAL, "3D view")
        self.vleft = left * setup["MouseSideStep"][0] * 0.12
        self.vtop = forward^left * setup["MouseUpDown"][0] * 0.12

    def dragto(self, x, y, flags):
        if self.camerapos0 is None: return
        pos, roll, pitch = self.camerapos0
        x = self.x0-x
        y = self.y0-y

        self.view.animation = 1
        try:
            self.view.cameraposition = pos + self.vleft*x + self.vtop*y, roll, pitch
        except:
            self.view.invalidate(1)

#
# circlestafe utilities
#
def vec2rads(v):
    "returns pitch, yaw, in radians"
    v = v.normalized
    import math
    pitch = -math.sin(v.z)
    yaw = math.atan2(v.y, v.x)
    return pitch, yaw


class CircleStrafeDragObject(SideStepDragObject):

    def __init__(self, editor, view, x, y):
        self.editor=editor
        SideStepDragObject.__init__(self, editor, view, x, y)
        
    def dragto(self, x, y, flags):
        sel = self.editor.layout.explorer.sellist
        if sel:
            min, max = quarkx.boundingboxof(sel)
            center = .5*(max+min)
            pos, yaw, pitch = self.camerapos0
            dist = abs(pos-center)
            x = self.x0-x
            y = self.y0-y
            newdir = (pos + self.vleft*x + self.vtop*y - center).normalized
            newpos = center+dist*newdir
            pitch, yaw = vec2rads(-newdir)
            self.view.animation = 1
            try:
                self.view.cameraposition = newpos, yaw, pitch
            except:
                self.view.invalidate(1)
        else:
            SideStepDragObject.dragto(self, x, y, flags)

#
# Displays a red rectangle created by the mouse movement.
# This is a base class for classes that do something with
# the rectangle, e.g. select all polyhedron within it, or
# zoom in or out.
#

class RectangleDragObject(RedImageDragObject):

    def __init__(self, view, x, y, redcolor, todo):
        RedImageDragObject.__init__(self, view, x, y, view.depth[0], redcolor)
        self.todo = todo

    def buildredimages(self, x, y, flags, depth=None):
        if x==self.x0 or y==self.y0:
            return None, None
        if depth is None:
            min, max = self.view.depth
            max = max - 0.0001
        else:
            min, max = depth
        pts = [self.view.space(self.x0, self.y0, min),
               self.view.space(x, self.y0, min),
               self.view.space(x, y, min),
               self.view.space(self.x0, y, min)]
        pts.append(pts[0])
        pts2 = [self.view.space(self.x0, self.y0, max),
                self.view.space(x, self.y0, max),
                self.view.space(x, y, max),
                self.view.space(self.x0, y, max)]
        if (x<self.x0)^(y<self.y0):
            pts.reverse()
            pts2.reverse()
        poly = quarkx.newobj("redbox:p")
        for i in (0,1,2,3):
            face = quarkx.newobj("side:f")
            face.setthreepoints((pts[i], pts[i+1], pts2[i]), 0)
            poly.appenditem(face)
        face = quarkx.newobj("front:f")
        face.setthreepoints((pts[0], pts[3], pts[1]), 0)
        poly.appenditem(face)
        face = quarkx.newobj("back:f")
        face.setthreepoints((pts2[0], pts2[1], pts2[3]), 0)
        poly.appenditem(face)
        if self.view.info["type"] == "3D":
            for f in poly.subitems:
                f.swapsides()
        if poly.rebuildall() != (0,0):
            return None, None
        return None, [poly]

    def ok(self, editor, x, y, flags):
        self.autoscroll_stop()
        self.dragto(x, y, flags)
        import mdleditor
        if isinstance(editor, mdleditor.ModelEditor):
            # All views including Skin-view come here at the end of a rectangle selector drag,
            # then go on to qbaseeditor.py 'finishdrawing' function then mdleditor.py 'commonhandles'.
            # Need to call to rebuild a views handles if an option is setup for no handles during drag.
            from qbaseeditor import flagsmouse
            if flagsmouse == 2056 or flagsmouse == 2096:
                # This section allows the redimage objects to be drawn
                # in the Model Editor's views when a Quick Object Maker
                # item is being created during the dragging process.
                if self.view.info["viewname"] == "skinview":
                    pass
                else:
                    if flagsmouse == 2056 and quarkx.setupsubset(SS_MODEL, "Building")["ObjectMode"] is not None and quarkx.setupsubset(SS_MODEL, "Building").getint("ObjectMode") != 0:
                        if self.redimages is not None:
                            self.rectanglesel(editor, x,y, self.redimages[0])
                        else:
                            import mdlutils
                            mdlutils.Update_Editor_Views(editor, 4)
                mdleditor.setsingleframefillcolor(editor, self.view)
                import mdlhandles, plugins.mdlmodes
                if isinstance(editor.dragobject, mdlhandles.RectSelDragObject) or isinstance(editor.dragobject, plugins.mdlmodes.BBoxMakerDragObject):
                    if self.redimages is not None:
                        self.rectanglesel(editor, x,y, self.redimages[0], self.view)
                        if self.view.info["viewname"] == "skinview":
                            pass
                        else:
                            if (quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1") and (len(editor.ModelFaceSelList) != 0 or len(editor.ModelVertexSelList) != 0):
                                if self.view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                                    self.view.handles = []
                                    return
                                elif self.view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                                    self.view.handles = []
                                    return
                                elif self.view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                                    self.view.handles = []
                                    return
                                elif self.view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                                    self.view.handles = []
                                    return
                                elif self.view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                                    self.view.handles = []
                                    return
                                else:
                                    if len(self.view.handles) == 0:
                                        import mdlhandles
                                        self.view.handles = mdlhandles.BuildHandles(editor, editor.layout.explorer, self.view)
                                    cv = self.view.canvas()
                                    for h in self.view.handles:
                                        h.draw(self.view, cv, self)
                                    try:
                                        if editor.ModelVertexSelList != []:
                                            for vtx in editor.ModelVertexSelList:
                                                h = self.view.handles[vtx]
                                                h.draw(self.view, cv, h)
                                    except:
                                        pass
                    else:
                        if len(self.view.handles) == 0:
                            import mdlhandles
                            self.view.handles = mdlhandles.BuildHandles(editor, editor.layout.explorer, self.view)
                        cv = self.view.canvas()
                        for h in self.view.handles:
                            h.draw(self.view, cv, self)
                        if editor.ModelVertexSelList != []:
                            for vtx in editor.ModelVertexSelList:
                                h = self.view.handles[vtx]
                                h.draw(self.view, cv, h)
                        return
        else:
            if self.redimages is not None:
                self.rectanglesel(editor, x,y, self.redimages[0])
            if self.view not in editor.layout.views:
                self.view.invalidate()
            editor.invalidateviews()

    def rectanglesel(self, editor, x,y, rectangle):
        "Called when the drag is over."
        pass   # abstract

#
# Class RectZoomDragObject:
# Zoom in or out of a rectangle drawn by the mouse movement.
#

def ZoomView(editor, view, zoom, clickpt):
    if editor.dragobject is not None:
        if isinstance(editor.dragobject, FreeZoomDragObject):
            editor.dragobject = None
            return
    center = clickpt + (view.screencenter-clickpt)/zoom
    if view.info.has_key("custom"):
        setviews([view], "scale", view.info["scale"]*zoom)
        view.screencenter = center
    else:
        editor.setscaleandcenter(view.info["scale"]*zoom, center)

class RectZoomDragObject(RectangleDragObject):
    def rectanglesel(self, editor, x,y, rectangle):
        view = self.view
        w,h = view.clientarea
        zoom = min((w/abs(x-self.x0), h/abs(y-self.y0)))
        if "-" in self.todo:
            zoom = 1.0/zoom
        ZoomView(editor, view, zoom, view.space((self.x0+x)*0.5, (self.y0+y)*0.5, view.screencenter.z))

#
# Class Rotator2D: a DragObject to rotate flat 3D views with the mouse.
#

class Rotator2D(DragObject):

    InfiniteMouse = 1

    def __init__(self, view, x, y, redcolor=None, todo=None):
        info = view.info
        center = info["center"]
        DragObject.__init__(self, view, x, y, view.proj(center).z)
        self.data = info, info["angle"], info["vangle"], info["sfx"]

    def dragto(self, x, y, flags):
        info, angle, vangle, scroll = self.data
        #
        # Rotate the view. You can adjust the sensibility below.
        #
        info["angle"] = angle + (x-self.x0)*0.02
        info["vangle"] = vangle + (y-self.y0)*0.01

        #
        # First part of methods for rotation in the Model Editors 3D views.
        #
        rotationmode = quarkx.setupsubset(SS_MODEL, "Options").getint("3DRotation")
        if rotationmode == 1:
            center = quarkx.vect(0,0,0) ### Keeps the center of the GRID at the center of the view.
        elif rotationmode == 2:
            center = quarkx.vect(0,0,0) + modelcenter ### Keeps the center of the  MODEL at the center of the view.
        elif rotationmode == 3:
            from mdlhandles import cursorposatstart

            if cursorposatstart is None:
                center = quarkx.vect(0,0,0) + modelcenter
            else:
                center = cursorposatstart ### Centers the model where clicked for "Rotate at start position" method.
        else:
            center = self.view.screencenter ### Defaults back to the Original QuArK rotation method.

        fixpt = center + self.view.vector(center).normalized * scroll
        setprojmode(self.view)
        self.view.screencenter = fixpt - self.view.vector(fixpt).normalized * scroll

        if quarkx.setupsubset(SS_MODEL, "Options")["DHWR"] != "1":
            self.view.handles = []

        self.view.repaint()

    def ok(self, editor, x, y, flags):
        info = self.view.info
        info["angle"] = info["angle"] % pi2

#
# Function to build a DragObject in response to a MB_STARTDRAG.
#

def MouseDragging(editor, view, x, y, s, handle, redcolor):
    "Called when the user drags the mouse on a map view."
    
    if handle is None:
        if getAttr(editor,'frozenselection') is not None:
            if editor.layout.explorer.uniquesel is not None:
                if "S" in s and "R" in s:
                    return editor.FrozenDragObject(view,x,y,s,redcolor)
        
        if "C" in s:
            if view.info["type"]=="3D":
                return CircleStrafeDragObject(editor, view, x, y)
            else:
                return SideStepDragObject(editor, view, x, y)
        elif "R" in s:     # display a rectangle
            if ("+" in s) or ("-" in s):
                if view.info["type"]=="3D":
                    return SideStepDragObject(editor, view, x, y)
                else:
                    rectselclass = RectZoomDragObject
            elif view.info.has_key("mousemode"):
                rectselclass = view.info["mousemode"]
            else:
                rectselclass = editor.MouseDragMode
            if rectselclass is None:
                return
            return rectselclass(view, x, y, redcolor, s)
        elif "Z" in s:   # free zoom
            if view.info["type"]=="3D":    # on 3D views, make the camera move and rotate, like in Quake.
                return WalkDragObject(editor, view, x, y)
            dragobj = FreeZoomDragObject(editor.layout.baseviews, view, x, y)
            dragobj.MODE = editor.MODE
            return dragobj
        elif "S" in s:   # scroll
            if view.info["type"]=="3D":    # on 3D views, make the camera rotate, like in Quake.
                return FreeViewDragObject(editor, view, x, y)
            return ScrollViewDragObject(editor, view, x, y)
    else:
        return HandleDragObject(view, x, y, handle, redcolor)

#
# Function called in answer to simple clicks (not drags).
#

def MouseClicked(editor, view, x, y, s, handle):
    "Called when the user clicks on a map view."

    if "M" in s:
        if handle is not None:   # menu on a handle
            menu = handle.menu(editor, view)
            if menu is not None:
                view.popupmenu(menu, x,y)
            return ""
        flags = "M"    # default menu
    else:
        flags = ""
    if "S" in s:    # if request to select an object
        if handle is not None:
            result = handle.click(editor)
            if result is not None:
                return flags+result
        if view.info.has_key("noclick"):
            return flags
        if not "M" in s:
            for h in view.handles:
                h.leave(editor)
        #
        #  if selection is frozen, it can't be changed,
        #    a different handle of the selected object
        #    can be manipulated
        #
        return flags+"1"
            
    if view.info["type"]=="3D":
        #
        # Zoom in and out on 3D views -- make the camera walk forward or backward.
        #
        if "+" in s:       # zoom in (forward)
            step = STEP3DVIEW
        elif "-" in s:     # zoom out (backward)
            step = -STEP3DVIEW
        else:
            return flags
        pos, roll, pitch = view.cameraposition
        forward = angles2vec1(pitch*rad2deg, roll*rad2deg, 0)
        pos = pos + forward*step
        view.cameraposition = pos, roll, pitch
        return ""
    #
    # Zoom in and out on 2D views.
    #
    if "+" in s:       # zoom in
        zoom = MOUSEZOOMFACTOR
    elif "-" in s:     # zoom out
        zoom = 1.0/MOUSEZOOMFACTOR
    else:
        return flags
    ZoomView(editor, view, zoom, view.space(x,y,view.screencenter.z))
    return ""

#
# Class that manages the linear box... er... circle.
#

class LinHandlesManager:
    "Linear Box manager."

    def __init__(self, color, bbox, list):
        self.color = color
        self.bbox = bbox
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

    def BuildHandles(self, center=None, minimal=None):
        "Build a list of handles to put around the box for linear distortion."

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
            return [LinCornerHandle(self.center, view.space(view.proj(pmin) + quarkx.vect(f, f, 0)), self, pmin)]
        h = []
        for side in (self.bmin, self.bmax):
            for dir in (0,1,2):
                h.append(LinSideHandle(self.center, side, dir, self, not len(h)))
        mX, mY, mZ = self.bmin.tuple
        X, Y, Z = self.bmax.tuple
        for x in (X,mX):
            for y in (Y,mY):
                for z in (Z,mZ):
                    h.append(LinCornerHandle(self.center, quarkx.vect(x,y,z), self))
        return h + [LinRedHandle(self.center, self)]


    def drawbox(self, view):
        "Draws the circle around all objects."

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

      #
      # The commented out version below draws a box instead of a circle
      # - but this box and the polyhedron borders often tend to get
      # in the way of each other
      #

      # def line1(x1,y1,z1,x2,y2,z2, line=cv.line, proj=view.proj):
      #     line(proj(x1,y1,z1), proj(x2,y2,z2))
      #
      # cv.pencolor = self.color
      # mX, mY, mZ = self.bmin.tuple
      # X, Y, Z = self.bmax.tuple
      # line1(mX,mY,mZ,  X,mY,mZ)
      # line1(mX,mY, Z,  X,mY, Z)
      # line1(mX, Y,mZ,  X, Y,mZ)
      # line1(mX, Y, Z,  X, Y, Z)
      # line1(mX,mY,mZ, mX, Y,mZ)
      # line1(mX,mY, Z, mX, Y, Z)
      # line1( X,mY,mZ,  X, Y,mZ)
      # line1( X,mY, Z,  X, Y, Z)
      # line1(mX,mY,mZ, mX,mY, Z)
      # line1(mX, Y,mZ, mX, Y, Z)
      # line1( X,mY,mZ,  X,mY, Z)
      # line1( X, Y,mZ,  X, Y, Z)

#
# Utility functions to multiselect objects.
#

def findnextobject(choice):
    #
    # To (multi-)select an object when Ctrl is down, we select
    # the first object whose state differs from the previous
    # objects' state
    #
    prev = None
    for z,obj,xtra in choice:
        sel = obj.selected
        #
        # if the state of this object differs from the previous'
        #
        if sel != prev:
            if prev is None:
                #
                # No previous, this is actually the first object.
                #
                prev = sel
            else:
                #
                # We got the object we wanted.
                #
                return obj
    #
    # All objects have the same state, so return the first one.
    #
    return choice[0][1]


def findlastsel(choice,keep=0):
    #
    # Find the last selected object in the choice.
    #
    for i in range(len(choice), 0, -1):
        if choice[i-1][1].selected:
            if keep:
                return i-1
            else:
                return i
    return 0

#
# Creation of flat 3D views that rotate with the mouse.
#

def z_recenter(view3d, list):
    global modelcenter
    modelcenter = view3d.info["center"]
    bbox = quarkx.boundingboxof(list)
    if bbox is None: return
    bmin, bmax = bbox
    view3d.info["center"] = (bmin+bmax)*0.5
    # bmin = bmin - quarkx.vect(32,32,32)
    # bmax = bmax + quarkx.vect(32,32,32)
    bmin = bmin - quarkx.vect(8,8,8)
    bmax = bmax + quarkx.vect(8,8,8)
    box1 = []
    for x in (bmin.x,bmax.x):      # all 8 corners of the bounding box
        for y in (bmin.y,bmax.y):
            for z in (bmin.z,bmax.z):
                box1.append(view3d.proj(x,y,z))
    bmin = min(box1).z
    bmax = max(box1).z
    view3d.info["sfx"] = (bmax-bmin)*0.5 / view3d.info["scale"]
    try:
        view3d.depth = (bmin, bmax)  # This fixes the drifting problem when in regular 3D mode.
    except:
        pass # When we are in true 3D perspective mode to avoid error.
    

def flat3Dview(view3d, layout, selonly=0):

    modelcenter = quarkx.vect(0,0,0)
    #
    # "localsetprojmode": Set the projection attributes and then automatically Z-recenter.
    #
    if selonly:
        def localsetprojmode(view, layout=layout):
            defsetprojmode(view)
            z_recenter(view, layout.explorer.sellist)
    else:
        def localsetprojmode(view, layout=layout):
            global modelcenter
            defsetprojmode(view)
            z_recenter(view, [layout.editor.Root])
            modelcenter = view3d.info["center"]

    view3d.viewmode = "tex"
    view3d.flags = view3d.flags &~ (MV_HSCROLLBAR | MV_VSCROLLBAR)
    try:
        curviewname = view3d.info["viewname"]
    except:
        curviewname = "editors3Dview"
    view3d.info = {"type": "2D",
                   "viewname": curviewname,
                   "scale": 2.0,
                   "angle": -0.7,
                   "vangle": 0.3,
                   "custom": localsetprojmode,
                   "noclick": None,
                   "mousemode": Rotator2D,
                #   "center": quarkx.vect(0,0,0), # To setup new multiple rotation methods below.
                   "center": None,
                   "sfx": 0 }

        #
        # Final part of methods for rotation in the Model Editors 3D views.
        #
    editor = mapeditor()
    import mdleditor
    if isinstance(editor, mdleditor.ModelEditor):
        from mdlhandles import cursorposatstart
        rotationmode = quarkx.setupsubset(SS_MODEL, "Options").getint("3DRotation")
        if rotationmode == 2:
            center = quarkx.vect(0,0,0) + modelcenter ### Keeps the center of the MODEL at the center of the view.
        elif rotationmode == 3:
            if cursorposatstart is None:
                center = quarkx.vect(0,0,0) + modelcenter
            else:
                center = cursorposatstart
        else:
            center = quarkx.vect(0,0,0) ### For the Original QuArK rotation and "Lock to center of 3Dview" methods.
        view3d.info["center"] = center
    else:
        view3d.info["center"] = quarkx.vect(0,0,0)

    if selonly:
        layout.editor.setupview(view3d, layout.editor.drawmapsel)
    else:
        layout.editor.setupview(view3d)
    return view3d

# ----------- REVISION HISTORY ------------
#
#
#$Log: qhandles.py,v $
#Revision 1.101  2011/10/06 20:13:37  danielpharos
#Removed a bunch of 'fixes for linux': Wine's fault (and a bit ours); let them fix it.
#
#Revision 1.100  2011/03/15 08:25:46  cdunde
#Added cameraview saving duplicators and search systems, like in the Map Editor, to the Model Editor.
#
#Revision 1.99  2011/02/13 03:37:47  cdunde
#Fixed all force to grid functions for model editor bones, vertexes, tags and bboxes.
#
#Revision 1.98  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.97  2010/10/21 07:24:56  cdunde
#Fix for occasional floating point division by zero error.
#
#Revision 1.96  2010/09/23 04:57:24  cdunde
#Various improvements for Model Editor Skin-view Linear Handle drawing time.
#
#Revision 1.95  2010/09/16 06:33:33  cdunde
#Model editor, Major change of Skin-view Linear Handle selection and dragging system, massively improving drawing time.
#
#Revision 1.94  2010/06/02 21:23:39  cdunde
#Fixes for Model Editor Eye position handle.
#
#Revision 1.93  2010/05/31 06:29:01  cdunde
#Fix for Model Editor Eye handle causing multi redraws if quick move is made.
#
#Revision 1.92  2010/05/29 04:34:45  cdunde
#Update for Model Editor camera EYE handles for editor and floating 3D view.
#
#Revision 1.91  2010/05/12 08:07:13  cdunde
#Added Eye camera handle when in True 3D mode for easier navigation.
#
#Revision 1.90  2010/05/02 06:20:26  cdunde
#To remove Model Editor unused and duplicating handle build code causing slowdowns.
#
#Revision 1.89  2009/09/30 19:37:26  cdunde
#Threw out tags dialog, setup tag dragging, commands, and fixed saving of face selection.
#
#Revision 1.88  2009/08/31 08:52:16  cdunde
#To try and stop errors from opening the Model Editor Skin-view for the first time.
#
#Revision 1.87  2009/08/11 01:03:09  cdunde
#To stop involuntary and unwanted zoom jumps in the model editor.
#
#Revision 1.86  2009/08/10 19:45:33  cdunde
#To stop involuntary and unwanted zoom jumps in the model editor.
#
#Revision 1.85  2009/07/14 00:27:33  cdunde
#Completely revamped Model Editor vertex Linear draglines system,
#increasing its reaction and drawing time to twenty times faster.
#
#Revision 1.84  2009/07/14 00:00:11  cdunde
#Missed part of last update.
#
#Revision 1.83  2009/07/13 23:53:55  cdunde
#Improvement by DanielPharos of vertex redrawing with rectangle selection movement.
#
#Revision 1.82  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.81  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.80  2009/03/28 20:03:57  cdunde
#To remove unwanted white spaces.
#
#Revision 1.79  2009/01/11 06:49:41  cdunde
#Minor fix for error when Model Editor is in True 3D mode.
#
#Revision 1.78  2008/12/19 17:23:21  cdunde
#To stop the dupe drawing of vertex boxes in the Model Editor during a bone center handle drag.
#
#Revision 1.77  2008/10/20 22:23:52  danielpharos
#Removed redundant variable.
#
#Revision 1.76  2008/10/14 00:15:00  cdunde
#Fix by DanielPharos for rotationspeed.
#
#Revision 1.75  2008/09/15 04:47:45  cdunde
#Model Editor bones code update.
#
#Revision 1.74  2008/08/21 12:02:37  danielpharos
#Removed a redundant line of code
#
#Revision 1.73  2008/05/27 19:35:41  danielpharos
#Removed redundant call to mapeditor()
#
#Revision 1.72  2008/05/25 23:19:34  cdunde
#Fixed Model Editor Skin-view Linear vertex handles from not drawing.
#
#Revision 1.71  2008/05/19 00:09:42  cdunde
#Fixed the loss of the model editor causing the Skin-view to not work properly.
#
#Revision 1.70  2008/05/01 15:38:16  danielpharos
#Don't overwrite self.editor
#
#Revision 1.69  2008/02/16 09:12:20  cdunde
#To stop error message.
#
#Revision 1.68  2008/02/07 13:25:25  danielpharos
#Add an editor-check and removed some redundant code
#
#Revision 1.67  2008/01/26 07:11:56  cdunde
#To stop doautozoom in Skin-view, causing unexpected view jumps.
#Increased zoom in amount in Model Editor views for closer work.
#
#Revision 1.66  2007/12/19 12:40:28  danielpharos
#Small code clean-up
#
#Revision 1.65  2007/11/29 22:14:23  cdunde
#To stop view error when both editors are open.
#
#Revision 1.64  2007/11/16 18:48:23  cdunde
#To update all needed files for fix by DanielPharos
#to allow frame relocation after editing.
#
#Revision 1.63  2007/11/04 00:33:33  cdunde
#To make all of the Linear Handle drag lines draw faster and some selection color changes.
#
#Revision 1.62  2007/10/18 02:31:53  cdunde
#Setup the Model Editor Animation system, functions and toolbar.
#
#Revision 1.61  2007/10/05 20:47:50  cdunde
#Creation and setup of the Quick Object Makers for the Model Editor.
#
#Revision 1.60  2007/09/04 23:16:22  cdunde
#To try and fix face outlines to draw correctly when another
#component frame in the tree-view is selected.
#
#Revision 1.59  2007/09/01 19:36:40  cdunde
#Added editor views rectangle selection for model mesh faces when in that Linear handle mode.
#Changed selected face outline drawing method to greatly increase drawing speed.
#
#Revision 1.58  2007/08/23 20:32:58  cdunde
#Fixed the Model Editor Linear Handle to work properly in
#conjunction with the Views Options dialog settings.
#
#Revision 1.57  2007/08/20 19:58:23  cdunde
#Added Linear Handle to the Model Editor's Skin-view page
#and setup color selection and drag options for it and other fixes.
#
#Revision 1.56  2007/08/11 02:38:59  cdunde
#To stop error in Model Editor if a Vertex Handle is clicked on but no movement is made.
#
#Revision 1.55  2007/08/08 21:29:52  cdunde
#Missed two line changes in the last update.
#
#Revision 1.54  2007/08/08 21:07:47  cdunde
#To setup red rectangle selection support in the Model Editor for the 3D views using MMB+RMB
#for vertex selection in those views.
#Also setup Linear Handle functions for multiple vertex selection movement using same.
#
#Revision 1.53  2007/08/01 06:12:12  cdunde
#To stop the rest of the Model Editor Linear Handles from going through code and causing problems.
#And stop error if object is moved back to where it started from at beginning of a linear drag.
#Also added a 'rotationspeed' control to the 'UserRotationMatrix' function.
#
#Revision 1.52  2007/07/28 23:12:51  cdunde
#Added ModelEditorLinHandlesManager class and its related classes to the mdlhandles.py file
#to use for editing movement of model faces, vertexes and bones (in the future).
#
#Revision 1.51  2007/07/15 00:16:49  cdunde
#To remove testing print statements missed during cleanup.
#
#Revision 1.50  2007/07/11 20:00:55  cdunde
#Setup Red Rectangle Selector in the Model Editor Skin-view for multiple selections.
#
#Revision 1.49  2007/07/09 19:33:59  cdunde
#To fix error in Model Editor when RectSelDragObject had no rectangle during drag.
#
#Revision 1.48  2007/07/04 18:51:23  cdunde
#To fix multiple redraws and conflicts of code for RectSelDragObject in the Model Editor.
#
#Revision 1.47  2007/07/02 22:49:42  cdunde
#To change the old mdleditor "picked" list name to "ModelVertexSelList"
#and "skinviewpicked" to "SkinVertexSelList" to make them more specific.
#Also start of function to pass vertex selection from the Skin-view to the Editor.
#
#Revision 1.46  2007/07/01 04:56:52  cdunde
#Setup red rectangle selection support in the Model Editor for face and vertex
#selection methods and completed vertex selection for all the editors 2D views.
#Added new global in mdlhandles.py "SkinView1" to get the Skin-view,
#which is not in the editors views.
#
#Revision 1.45  2007/05/21 15:21:31  cdunde
#To fix QuArK editors crossover errors.
#
#Revision 1.44  2007/04/13 19:48:35  cdunde
#Changed Center and Linear center Handle dragging hint to give start
#and progressive drag positions based on grid location.
#
#Revision 1.43  2007/04/04 21:34:17  cdunde
#Completed the initial setup of the Model Editors Multi-fillmesh and color selection function.
#
#Revision 1.42  2007/04/02 22:18:22  danielpharos
#Fixed the rotation in linear mode.
#
#Revision 1.41  2007/03/29 18:02:19  cdunde
#Just some comment stuff.
#
#Revision 1.40  2007/03/05 19:44:05  cdunde
#To remove print statements left in after testing.
#
#Revision 1.39  2007/03/04 20:15:15  cdunde
#Missed items in last update.
#
#Revision 1.38  2007/03/04 19:40:03  cdunde
#Added option to draw or not draw handles in the Model Editor 3D views
#while rotating the model to increase drawing speed.
#
#Revision 1.37  2007/01/31 15:12:16  danielpharos
#Removed bogus OpenGL texture mode
#
#Revision 1.36  2007/01/30 06:37:37  cdunde
#To get the Skin-view to scroll without having to redraw all the handles in every view.
#Increases response time and drawing speed.
#
#Revision 1.35  2007/01/30 06:34:13  cdunde
#Changed model rotation in the Model Editor for full rotations in all directions
#Also to removed previously added global mouseflags that was giving delayed data
#and replace with global flagsmouse that gives correct data before other functions.
#
#Revision 1.34  2007/01/21 19:45:28  cdunde
#Added the global mouseflags to get those where ever we need them and
#get control over 3D viewname items to add new Model Editor Views Options.
#
#Revision 1.33  2006/12/15 09:03:35  cdunde
#Additional code removal for redundancy of view redraws adding to slowdown.
#
#Revision 1.32  2006/12/15 07:39:51  cdunde
#Improved quality of 3D Texture mode while dragging at increased drawing speed.
#
#Revision 1.31  2006/12/03 18:28:06  cdunde
#Stopped the Model Editor from drawing incorrect image in Skin-view.
#
#Revision 1.30  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.29  2006/11/29 22:23:30  cdunde
#To fix zoom in fade problem in Model Editor for Software and Glide modes.
#
#Revision 1.28  2006/11/29 07:00:26  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.27.2.8  2006/11/27 08:31:56  cdunde
#To add the "Rotate at start position" method to the Model Editors rotation options menu.
#
#Revision 1.27.2.7  2006/11/25 04:23:57  cdunde
#Added a new sub-menu to the Model Editors "Options" menu,
#with various methods of rotation in 3D views to choose from.
#
#Revision 1.27.2.6  2006/11/22 18:26:45  cdunde
#To reset rotation to center of model rather then the view
#to account for models of grid center.
#
#Revision 1.27.2.5  2006/11/22 06:50:46  cdunde
#Fixed the Model Editors 3D pivot point at the center of the view.
#
#Revision 1.27.2.4  2006/11/09 23:17:45  cdunde
#Changed Paint Brush dialog to work with new version view setup and names.
#
#Revision 1.27.2.3  2006/11/09 23:00:02  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.27.2.2  2006/11/04 21:39:40  cdunde
#New "viewname" info added key:value "viewname": "mdleditor3Dview" to model edittors
#3D view because quarkpy\qhandles.py file redefines that view as a "2D" type.
#(who knows why but it brakes if it is not)
#
#Revision 1.27.2.1  2006/11/01 22:22:42  danielpharos
#BackUp 1 November 2006
#Mainly reduce OpenGL memory leak
#
#Revision 1.27  2006/06/03 02:31:46  cdunde
#To fix Access violation errors when rebuilding 3D textured views and panning or moving in them.
#
#Revision 1.26  2006/06/02 18:48:02  cdunde
#To fix a couple of erroneous console errors.
#
#Revision 1.25  2006/01/30 10:07:13  cdunde
#Changes by Nazar to the scale, zoom and map sizes that QuArK can handle
#to allow the creation of much larger maps for the more recent games.
#
#Revision 1.24  2006/01/30 08:20:00  cdunde
#To commit all files involved in project with Philippe C
#to allow QuArK to work better with Linux using Wine.
#
#Revision 1.23  2006/01/29 19:08:53  cdunde
#To fix error message when sometimes switching game modes
#
#Revision 1.22  2006/01/12 07:21:01  cdunde
#To commit all new and related files for
#new Quick Object makers and toolbar.
#
#Revision 1.21  2005/12/22 07:31:59  cdunde
#To fix another key error when using
#Tab key function in Model Editor.
#
#Revision 1.20  2005/11/07 00:07:01  cdunde
#To commit all files for addition of new Terrain Generator items
#Touch-up Selector and 3D Options Dialog
#
#Revision 1.19  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.16  2005/08/31 22:46:38  cdunde
#To properly fix interference with Model Editor
#
#Revision 1.15  2005/08/15 05:50:17  cdunde
#To commit all files for Terrain Generator
#
#Revision 1.14  2005/07/16 19:41:31  cdunde
#To remove improper items to fix broken handles
#
#Revision 1.13  2005/07/12 00:39:10  cdunde
#Minor correction.
#
#Revision 1.12  2005/05/18 06:32:21  cdunde
#After further testing some changes needed to be reversed.
#
#Revision 1.11  2005/05/15 06:01:34  cdunde
#To fix red wire objects erasing other items in 3D Textured views
#and commented out unnecessary dupe view invalidations,
#used finishdrawing instead, which seems more effective
#
#Revision 1.10  2005/05/12 07:19:39  cdunde
#Fix hint blocked by cursor
#
#Revision 1.9  2002/05/18 09:51:56  tiglari
#support Radiant-style dragging for frozen selections
#
#Revision 1.8  2001/04/26 22:45:03  tiglari
#face-only selection & texture L RMB
#
#Revision 1.7  2001/04/08 02:39:37  tiglari
#usercenters now update recursively thru subobjects.  If this proves to
# be too slow for large objects, maybe it could be optimized to happen only
# at the beginning and the end of the drag.
#
#Revision 1.6  2001/04/08 00:40:31  tiglari
#'usercenter' specific updated on CenterHandle drag
#
#Revision 1.5  2001/02/25 11:22:51  tiglari
#bezier page support, transplanted with permission from CryEd (CryTek)
#
#Revision 1.4  2001/02/07 18:40:47  aiv
#bezier texture vertice page started.
#
#Revision 1.3  2000/10/10 07:37:12  tiglari
#support for circlestrafe selection
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
