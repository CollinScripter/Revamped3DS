"""   QuArK  -  Quake Army Knife

Model editor mouse handles.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mdlhandles.py,v 1.237 2013/02/26 02:57:29 cdunde Exp $

#
# See comments in maphandles.py.
#

import quarkx
import math
from qdictionnary import Strings
import qhandles
import mdlutils
from mdlutils import *
import mdlentities
import qmenu
import qbaseeditor
import mdleditor

#py2.4 indicates upgrade change for python 2.4

# Globals
cursorposatstart = None
lastmodelfaceremovedlist = []
SkinView1 = None  # Used to get the Skin-view at any time because
                  # it is not in the "editors.layout.views" list.


def alignskintogrid(v, mode):
    #
    # mode=0: normal behaviour
    # mode=1: if v is a 3D point that must be forced to skingrid (when the Ctrl key is down)
    #
    import mdleditor
    editor = mdleditor.mdleditor
    g = editor.skingrid
    if g<=0.0:
        return v   # no skingrid
    rnd = quarkx.rnd
    return quarkx.vect(rnd(v.x/g)*g, rnd(v.y/g)*g, rnd(v.z/g)*g)


def vec2rads(v):
    "returns pitch, yaw, in radians"
    v = v.normalized
    pitch = -math.sin(v.z)
    yaw = math.atan2(v.y, v.x)
    return pitch, yaw


def GetUserCenter(obj):
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
        uc = mdlentities.ObjectOrigin(obj).tuple
    return quarkx.vect(uc)

#
# The handle classes.
#

class CenterHandle(qhandles.CenterHandle):
    "Like qhandles.CenterHandle, but specifically for the Model editor."
    def menu(self, editor, view):
        def seePointClick(m, self=self, editor=editor):
            for v in editor.layout.views:
                if v.info['viewname'] == "editors3Dview":
                    view = v
                    break
            pos, yaw, pitch = view.cameraposition
            dir = (self.pos-pos).normalized
            pitch, yaw = vec2rads(dir)
            view.cameraposition = pos, yaw, pitch
            editor.invalidateviews()

        seeitem = qmenu.item("Look To",seePointClick,"|Aims an open 3d view at object")
        org_menu = self.OriginItems(editor, view)
        return [seeitem, qmenu.sep, org_menu[len(org_menu)-1]]



class IconHandle(qhandles.IconHandle):
    "Like qhandles.IconHandle, but specifically for the Model editor."
    def menu(self, editor, view):
        return mdlentities.CallManager("menu", self.centerof, editor) + self.OriginItems(editor, view)



def CenterEntityHandle(o, view, handleclass=IconHandle, pos=None):
    if pos is None:
        pos = o.origin
    if pos is not None:
        # Build a "circle" icon handle at the object origin.
        new = handleclass(pos, o)   # The "circle" icon would be qhandles.mapicons[10], but it looks better with the entity icon itself.
        # Set the hint as the entity classname in blue ("?").
        new.hint = "?" + o.shortname + "||This point represents an entity, i.e. an object that appears and interacts in the game when you play the map. The exact kind of entity depends on its 'classname' (its name).\n\nThis handle lets you move the entity with the mouse. Normally, the movement is done by steps of the size of the grid : if the entity was not aligned on the grid before the movement, it will not be after it. Hold down Ctrl to force the entity to the grid.|maped.duplicators.extruder.html"

        return [new]
    else:
        # No "origin".
        return []



class MdlEyeDirection(qhandles.EyeDirection):
    MODE = SS_MODEL



def AddRemoveEyeHandles(editor, v):
    if v.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
        v.handles = []
        return
    elif v.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
        v.handles = []
        return
    elif v.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
        v.handles = []
        return
    elif v.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
        v.handles = []
        return
    elif v.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
        v.handles = []
        return

    True3Dview = None
    FullTrue3Dview = None
    for view in editor.layout.views:
        if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] == "1":
            True3Dview = view
        if view.info["viewname"] == "3Dwindow" and view.info['type'] == "3D" and quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] == "1":
            FullTrue3Dview = view

    while 1:
        try:
            if isinstance(v.handles[-1], MdlEyeDirection) or isinstance(v.handles[-1], qhandles.EyePosition):
                del v.handles[-1]
            else:
                break
        except:
            break

    if True3Dview is not None or FullTrue3Dview is not None:
        if True3Dview is not None:
            handle = qhandles.EyePosition(v, True3Dview)
            handle.hint = "camera for the Editor 3D view"
            v.handles.append(handle)
            handle = MdlEyeDirection(v, True3Dview)
            handle.hint = "Editor 3D view camera direction"
            v.handles.append(handle)
        if FullTrue3Dview is not None:
            handle = qhandles.EyePosition(v, FullTrue3Dview)
            handle.hint = "camera for the floating 3D view"
            v.handles.append(handle)
            handle = MdlEyeDirection(v, FullTrue3Dview)
            handle.hint = "floating 3D view camera direction"
            v.handles.append(handle)



class ModelFaceHandle(qhandles.GenericHandle):
    "Model Mesh Face selection and edit."

    size = None

    def __init__(self, pos):
        qhandles.GenericHandle.__init__(self, pos)
        self.cursor = CR_CROSSH
        self.undomsg = "model mesh face edit"


    def menu(self, editor, view):

        def cleancomponentclick(m, self=self, editor=editor, view=view):
            addcomponent(editor, 1)

        def newcomponentclick(m, self=self, editor=editor, view=view):
            addcomponent(editor, 2)

        def movefacestoclick(movetocomponent, option, self=self, editor=editor, view=view):
            movefaces(editor, movetocomponent, option)

        def onclick1(m):
            movefacestoclick(m.text, 1)

        def onclick2(m):
            movefacestoclick(m.text, 2)

        def onclick3(m, editor=editor):
            movefacestoclick(None, 3)
            # Clear these lists to avoid errors.
            editor.ModelFaceSelList = []
            editor.EditorObjectList = []

        def movefacesclick(m, self=self, editor=editor, view=view):
            componentnames = []
            hiddenlist = []
            for item in editor.Root.dictitems:
                if item.endswith(":mc"):
                    if (editor.Root.dictitems[item].name == editor.Root.currentcomponent.name) or (len(editor.Root.dictitems[item].triangles) == 0): # This last one indicates that the component is "Hidden"
                        if item.startswith('new clean') and item != editor.Root.currentcomponent.name:
                            componentnames.append(editor.Root.dictitems[item].shortname)
                        elif (len(editor.Root.dictitems[item].triangles) == 0):
                            hiddenlist = hiddenlist + [editor.Root.dictitems[item].shortname]
                        else:
                            pass
                    else:
                        componentnames.append(editor.Root.dictitems[item].shortname)
            if len(componentnames) < 1:
                if hiddenlist == []:
                    quarkx.msgbox("Improper Selection!\n\nThere are no other components available\nto move the selected faces to.\n\nUse the 'Create New Component'\nfunction to make one.", MT_ERROR, MB_OK)
                    return None, None
                else:
                    quarkx.msgbox("Improper Selection!\n\nThere are no other components available\nto move the selected faces to\nbecause they are ALL HIDDEN.\n\nPress 'F1' for InfoBase help\nof this function for details.\n\nAction Canceled.", MT_ERROR, MB_OK)
                    return None, None
            else:
                componentnames.sort()
                menu = []
                for name in componentnames:
                    menu = menu + [qmenu.item(name, onclick2)]
                m.items = menu

        def copyfacesclick(m, self=self, editor=editor, view=view):
            componentnames = []
            hiddenlist = []
            for item in editor.Root.dictitems:
                if item.endswith(":mc"):
                    if (editor.Root.dictitems[item].name == editor.Root.currentcomponent.name) or (len(editor.Root.dictitems[item].triangles) == 0): # This last one indicates that the component is "Hidden"
                        if item.startswith('new clean') and item != editor.Root.currentcomponent.name:
                            componentnames.append(editor.Root.dictitems[item].shortname)
                        elif (len(editor.Root.dictitems[item].triangles) == 0):
                            hiddenlist = hiddenlist + [editor.Root.dictitems[item].shortname]
                        else:
                            pass
                    else:
                        componentnames.append(editor.Root.dictitems[item].shortname)
            if len(componentnames) < 1:
                if hiddenlist == []:
                    quarkx.msgbox("Improper Selection!\n\nThere are no other components available\nto copy the selected faces to.\n\nUse the 'Create New Component'\nfunction to make one.", MT_ERROR, MB_OK)
                    return None, None
                else:
                    quarkx.msgbox("Improper Selection!\n\nThere are no other components available\nto copy the selected faces to\nbecause they are ALL HIDDEN.\n\nPress 'F1' for InfoBase help\nof this function for details.\n\nAction Canceled.", MT_ERROR, MB_OK)
                    return None, None
            else:
                componentnames.sort()
                menu = []
                for name in componentnames:
                    menu = menu + [qmenu.item(name, onclick1)]
                m.items = menu

        def forcegrid1click(m, self=self, editor=editor, view=view):
            self.Action(editor, self.pos, self.pos, MB_CTRL, view, Strings[560])

        def addhere1click(m, self=self, editor=editor, view=view):
            addvertex(editor, editor.Root.currentcomponent, self.pos)

        def removevertex1click(m, self=self, editor=editor, view=view):
            removevertex(editor.Root.currentcomponent, self.index)
            editor.ModelVertexSelList = []

        def pick_vertex(m, self=self, editor=editor, view=view):
            itemcount = 0
            if editor.ModelVertexSelList == []:
                editor.ModelVertexSelList = editor.ModelVertexSelList + [self.index]
            else:
                for item in editor.ModelVertexSelList:
                    itemcount = itemcount + 1
                    if self.index == item:
                        editor.ModelVertexSelList.remove(item)
                        for v in editor.layout.views:
                            mdleditor.setsingleframefillcolor(editor, v)
                            v.repaint()
                        return
                    if itemcount == len(editor.ModelVertexSelList):
                        if len(editor.ModelVertexSelList) == 3:
                            quarkx.msgbox("Improper Selection!\n\nYou can not choose more then\n3 vertexes for a triangle.\n\nSelection Canceled", MT_ERROR, MB_OK)
                            return None, None
                        else:
                            editor.ModelVertexSelList = editor.ModelVertexSelList + [self.index]
            for v in editor.layout.views:
                cv = v.canvas()
                self.draw(v, cv, self)

        def pick_cleared(m, editor=editor, view=view):
            editor.ModelVertexSelList = []
            for v in editor.layout.views:
                mdleditor.setsingleframefillcolor(editor, v)
                v.repaint()

        CleanComponent = qmenu.item("&Empty Component", cleancomponentclick, "|Empty Component:\n\nYou need to select a single frame to use this function.\n\nThis will create a new 'Clean' Model component. To use this function you must select at least one face of another component and have the 'Linear button' active (clicked on).\n\nAll Frames will be there but without any vertexes or triangle faces. Also the 'Skins' sub-item will be empty as well for a fresh start.\n\nSkins or faces can then be moved or copied there from other components but do NOT change its name until you have at least one face (triangle) created or it will not appear on the 'move\copy to' menus.\n\nSkin textures can also be selected from the 'Texture Browser' if you have those setup.|intro.modeleditor.rmbmenus.html#facermbmenu")
        NewComponent = qmenu.item("&New Component", newcomponentclick, "|New Component:\n\nYou need to select a single frame to use this function.\n\nThis will create a new model component of currently selected Model Mesh faces only, including its Skins and Frames sub-items.\n\nThe selected faces will also be removed from their current components group.\n\nOnce created you can change the temporary name 'new component' to something else by clicking on it.|intro.modeleditor.rmbmenus.html#facermbmenu")
        MoveFaces = qmenu.popup("&Move Faces To", [], movefacesclick, "|Move Faces To:\n\nYou need to select a single frame to use this function.\n\nThis will move currently selected Model Mesh faces from one component to another (if NOT Hidden) by means of a menu that will appear listing all available components to choose from.\n\nIf none others exist it will instruct you to create a 'New Component' first using the function above this one in the RMB menu.", "intro.modeleditor.rmbmenus.html#facermbmenu")
        CopyFaces = qmenu.popup("&Copy Faces To", [], copyfacesclick, "|Copy Faces To:\n\nYou need to select a single frame to use this function.\n\nThis will copy currently selected Model Mesh faces from one component to another (if NOT Hidden) by means of a menu that will appear listing all available components to choose from.\n\nIf none others exist it will instruct you to create a 'New Component' first using the function above this one in the RMB menu.", "intro.modeleditor.rmbmenus.html#facermbmenu")
        DeleteFaces = qmenu.item("&Delete Faces", onclick3, "|Delete Faces:\n\nYou need to select a single frame to use this function.\n\nThis will delete currently selected Model Mesh faces from the currently selected component and any unused vertexes, by other faces (triangles), of those faces.|intro.modeleditor.rmbmenus.html#facermbmenu")

        if (len(editor.layout.explorer.sellist) == 0) or (editor.layout.explorer.sellist[0].type != ":mf"):
            CleanComponent.state = qmenu.disabled
            NewComponent.state = qmenu.disabled
            MoveFaces.state = qmenu.disabled
            CopyFaces.state = qmenu.disabled
            DeleteFaces.state = qmenu.disabled
        else:
            CleanComponent.state = qmenu.normal
            NewComponent.state = qmenu.normal
            MoveFaces.state = qmenu.normal
            CopyFaces.state = qmenu.normal
            DeleteFaces.state = qmenu.normal

        menu = [CleanComponent, NewComponent, MoveFaces, CopyFaces, DeleteFaces]
        return menu

    def selection(self, editor, view, modelfacelist, flagsmouse, draghandle=None):
        global lastmodelfaceremovedlist
        comp = editor.Root.currentcomponent
        
        if view.info["viewname"] == "skinview": return
        if flagsmouse == 536:
            for v in editor.layout.views:
                v.handles = []
            lastmodelfaceremovedlist = []
        itemsremoved = 0
        faceremoved = 0
        templist = editor.ModelFaceSelList
        for item in modelfacelist:
            if item[1].name == comp.name:
                if templist == []:
                    templist = templist + [item[2]]
                    lastmodelfaceremovedlist = []
                    faceremoved = -1
                    break
                elif lastmodelfaceremovedlist != [] and item[2] == lastmodelfaceremovedlist[0]:
                    pass
                else:
                    listsize = len(templist)
                    lastface = templist[listsize-1]
                    if item[2] == lastface:
                        pass
                    else:
                        facecount = 0
                        for face in templist:
                            if face == item[2]:
                                templist.remove(templist[facecount])
                                lastmodelfaceremovedlist = [item[2]]
                                faceremoved = 1
                                itemsremoved = itemsremoved + 1
                                break
                            facecount = facecount + 1
                        if faceremoved == 0:
                            templist = templist + [item[2]]
                            faceremoved = -1
                break ### This limits the faces that can be selected to the closest face to the camera.
        editor.ModelFaceSelList = templist
        list = MakeEditorFaceObject(editor)
        # Sets these lists up for the Linear Handle drag lines to be drawn.
        editor.SelCommonTriangles = []
        editor.SelVertexes = []
        if quarkx.setupsubset(SS_MODEL, "Options")['NFDL'] is None:
            for tri in editor.ModelFaceSelList:
                for vtx in range(len(comp.triangles[tri])):
                    if comp.triangles[tri][vtx][0] in editor.SelVertexes:
                        pass
                    else:
                        editor.SelVertexes = editor.SelVertexes + [comp.triangles[tri][vtx][0]] 
                        editor.SelCommonTriangles = editor.SelCommonTriangles + findTrianglesAndIndexes(comp, comp.triangles[tri][vtx][0], None)
        if quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] == "1":
            if SkinView1 is not None:
                if quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] == "1":
                    try:
                        skindrawobject = comp.currentskin
                    except:
                        skindrawobject = None
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_ISV'] == "1":
                        editor.SkinVertexSelList = []
                    PassEditorSel2Skin(editor, 2)
                    buildskinvertices(editor, SkinView1, editor.layout, comp, skindrawobject)
                else:
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_ISV'] == "1":
                        editor.SkinVertexSelList = []
                    SkinView1.repaint()

        for v in editor.layout.views:
            if v.info["viewname"] == "skinview":
                pass
            else:
                if faceremoved != 0 or itemsremoved != 0:
                    if v.info["viewname"] == "XY":
                        fillcolor = MapColor("Options3Dviews_fillColor2", SS_MODEL)
                        comp.filltris = mdleditor.faceselfilllist(v, fillcolor)
                        mdleditor.setsingleframefillcolor(editor, v)
                        v.repaint()
                        plugins.mdlgridscale.gridfinishdrawing(editor, v)
                    if v.info["viewname"] == "XZ":
                        fillcolor = MapColor("Options3Dviews_fillColor4", SS_MODEL)
                        comp.filltris = mdleditor.faceselfilllist(v, fillcolor)
                        mdleditor.setsingleframefillcolor(editor, v)
                        v.repaint()
                        plugins.mdlgridscale.gridfinishdrawing(editor, v)
                    if v.info["viewname"] == "YZ":
                        fillcolor = MapColor("Options3Dviews_fillColor3", SS_MODEL)
                        comp.filltris = mdleditor.faceselfilllist(v, fillcolor)
                        mdleditor.setsingleframefillcolor(editor, v)
                        v.repaint()
                        plugins.mdlgridscale.gridfinishdrawing(editor, v)
                    if v.info["viewname"] == "editors3Dview":
                        fillcolor = MapColor("Options3Dviews_fillColor1", SS_MODEL)
                        comp.filltris = mdleditor.faceselfilllist(v, fillcolor)
                        mdleditor.setsingleframefillcolor(editor, v)
                        v.repaint()
                    if v.info["viewname"] == "3Dwindow":
                        fillcolor = MapColor("Options3Dviews_fillColor5", SS_MODEL)
                        comp.filltris = mdleditor.faceselfilllist(v, fillcolor)
                        mdleditor.setsingleframefillcolor(editor, v)
                        v.repaint()
                if quarkx.setupsubset(SS_MODEL,"Options")['NFO'] != "1":
                    self.draw(editor, v, list)


    def draw(self, editor, view, list):
        if view.info["viewname"] == "skinview":
            return
        if quarkx.setupsubset(SS_MODEL,"Options")['NFO'] == "1":
            return
        from qbaseeditor import flagsmouse, currentview
        if (flagsmouse == 2056 or flagsmouse == 2060) and not isinstance(editor.dragobject, RectSelDragObject):
            return
        if (flagsmouse == 1032 or flagsmouse == 1036):
            if ((isinstance(editor.dragobject.handle, LinSideHandle)) or (isinstance(editor.dragobject.handle, LinCornerHandle)) or (isinstance(editor.dragobject.handle, BoneCornerHandle)) or (quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1" and not isinstance(editor.dragobject, qhandles.Rotator2D))) and quarkx.setupsubset(SS_MODEL, "Options")['NFDL'] is None:
                return

        if (flagsmouse == 1040 or flagsmouse == 1056):
            if (currentview.info["viewname"] != "editors3Dview" and currentview.info["viewname"] != "3Dwindow"):
                if quarkx.setupsubset(SS_MODEL,"Options")['NFOWM'] == "1":
                    return

        cv = view.canvas()
        cv.pencolor = faceseloutline
        try:
            cv.penwidth = float(quarkx.setupsubset(SS_MODEL,"Options")['linethickness'])
        except:
            cv.penwidth = 2
        cv.brushcolor = faceseloutline
        cv.brushstyle = BS_SOLID
        try:
            if len(list) != 0:
                for obj in list:
                    vect0X ,vect0Y, vect0Z, vect1X ,vect1Y, vect1Z, vect2X ,vect2Y, vect2Z = obj["v"]
                    vect0X ,vect0Y, vect0Z = view.proj(vect0X ,vect0Y, vect0Z).tuple
                    vect1X ,vect1Y, vect1Z = view.proj(vect1X ,vect1Y, vect1Z).tuple
                    vect2X ,vect2Y, vect2Z = view.proj(vect2X ,vect2Y, vect2Z).tuple
                    cv.line(int(vect0X), int(vect0Y), int(vect1X), int(vect1Y))
                    cv.line(int(vect1X), int(vect1Y), int(vect2X), int(vect2Y))
                    cv.line(int(vect2X), int(vect2Y), int(vect0X), int(vect0Y))
        except:
            editor.ModelFaceSelList = []
            editor.EditorObjectList = []
            editor.SelVertexes = []
            editor.SelCommonTriangles = []

        return

  #  For setting stuff up at the beginning of a drag
  #
  #  def start_drag(self, view, x, y):
  #      editor = mapeditor()


    def drag(self, v1, v2, flags, view):
        return
        editor = mapeditor()
        pv2 = view.proj(v2)  ### v2 is the SINGLE handle's (being dragged) 3D position (x,y and z in space).
                             ### And this converts its 3D position to the monitor's FLAT screen 2D and 3D views
                             ### 2D (x,y) position to draw it, (NOTICE >) using the 3D "y" and "z" position values.
        p0 = view.proj(self.pos)

        if not p0.visible: return
        if flags&MB_CTRL:
            v2 = qhandles.aligntogrid(v2, 0)
        delta = v2-v1
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)

        if view.info["viewname"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["viewname"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.z+delta.z)
        elif view.info["viewname"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            s = "was %s"%self.pos + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        self.draghint = s

        new = self.frame.copy()
        if delta or (flags&MB_REDIMAGE):
            vtxs = new.vertices
            vtxs[self.index] = vtxs[self.index] + delta
            new.vertices = vtxs
        if flags == 1032:             ## To stop drag starting lines from being erased.
            mdleditor.setsingleframefillcolor(editor, view) ## Sets the modelfill color.
            view.repaint()            ## Repaints the view to clear the old lines.
            plugins.mdlgridscale.gridfinishdrawing(editor, view)
        cv = view.canvas()            ## Sets the canvas up to draw on.
        cv.pencolor = drag3Dlines     ## Gives the pen color of the lines that will be drawn.

        component = editor.Root.currentcomponent
        if component is not None:
            if component.name.endswith(":mc"):
                handlevertex = self.index
                tris = findTriangles(component, handlevertex)
                for tri in tris:
                    if len(view.handles) == 0: continue
                    for vtx in tri:
                        if self.index == vtx[0]:
                            pass
                        else:
                            projvtx = view.proj(view.handles[vtx[0]].pos)
                            cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(projvtx.tuple[0]), int(projvtx.tuple[1]))

        return [self.frame], [new]


  #  For setting stuff up at the end of a drag
  #
  #  def ok(self, editor, undo, old, new):
  #  def ok(self, editor, x, y, flags):
  #      undo=quarkx.action()
  #      editor.ok(undo, self.undomsg)



class TagHandle(qhandles.GenericHandle):
    "Tag handle, location based on tagframe.dictspec['origin']."

    def __init__(self, pos, tagframe=None):
        qhandles.GenericHandle.__init__(self, pos)
        self.tagframe = tagframe
        self.cursor = CR_CROSSH
        self.undomsg = "mesh tag move"
        self.editor = mdleditor.mdleditor
        if not ico_dict.has_key('ico_objects'):
            ico_dict['ico_objects'] = LoadIconSet("images\\objects", 16)


    def extrasmenu(self, editor, view):
        complist = []
        for item in editor.layout.explorer.sellist:
            if item.type == ":mc":
                complist = complist + [item]

        def add_tag_click(m, self=self, editor=editor, view=view, complist=complist):
            import mdlmgr
            mdlmgr.savefacesel = 1
            addtag(editor, complist, self.pos)

        def ShowTags(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            quarkx.setupsubset(SS_MODEL, "Options")['HideTags'] = None
            ST1.state = qmenu.disabled
            HT1.state = qmenu.normal
            mdlutils.Update_Editor_Views(editor)
            editor.layout.explorer.invalidate()

        def HideTags(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            quarkx.setupsubset(SS_MODEL, "Options")['HideTags'] = "1"
            ST1.state = qmenu.normal
            HT1.state = qmenu.disabled
            mdlutils.Update_Editor_Views(editor)
            editor.layout.explorer.invalidate()

        AddTag = qmenu.item("&Add Tag Here", add_tag_click, "|Add Tag Here:\n\nYou must select one or more components to use this function.\n\nThis will add a single tag to the 'Misc' group.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.editelements.html#tags")
        ST1 = qmenu.item("&Show Tags", ShowTags, "|Show Tags:\n\nThis allows all tags to be displayed in the editor's views.|intro.modeleditor.editelements.html#tags")
        HT1 = qmenu.item("&Hide Tags", HideTags, "|Hide Tags:\n\nThis stops all tags from being displayed in the editor's views.|intro.modeleditor.editelements.html#tags")

        AddTag.state = qmenu.disabled

        if len(complist) != 0:
            AddTag.state = qmenu.normal

        if quarkx.setupsubset(SS_MODEL, "Options")['HideTags'] is not None:
            ST1.state = qmenu.normal
            HT1.state = qmenu.disabled
        else:
            ST1.state = qmenu.disabled
            HT1.state = qmenu.normal

        menu = [AddTag, qmenu.sep, ST1, HT1]

        return menu


    def menu(self, editor, view):

        def select_tag_click(m, self=self, editor=editor, view=view):
            # self.tagframe = first tag frame, self.tagframe.parent = the tag itself.
            import mdlmgr
            mdlmgr.savefacesel = 1
            editor.layout.explorer.sellist = [self.tagframe.parent] + editor.layout.explorer.sellist
            editor.layout.explorer.expand(self.tagframe.parent.parent)

        def hide_this_tag_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            self.tagframe.parent['show'] = (0.0,)
            mdlutils.Update_Editor_Views(editor)
            editor.layout.explorer.invalidate()

        def force_to_grid_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            gridpos = qhandles.aligntogrid(self.pos, 1)
            undo = quarkx.action()
            movediff = gridpos - self.pos
            old_tag = self.tagframe.parent
            new_tag = old_tag.copy()
            tag_frames = new_tag.subitems # Get all its tag frames.
            for frame in tag_frames:
                new_frame = frame.copy()
                new_frame['origin'] = (quarkx.vect(new_frame.dictspec['origin']) + movediff).tuple
                undo.exchange(frame, new_frame)
            undo.exchange(old_tag, new_tag)
            self.editor.ok(undo, new_tag.shortname + ' snapped to grid')

        def delete_tag_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            deletetag(editor, self.tagframe.parent)

        SelectTag = qmenu.item("&Select this tag", select_tag_click, "|Select this tag:This will select the single tag clicked on.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.editelements.html#tags")
        HTT = qmenu.item("&Hide this tag", hide_this_tag_click)
        Forcetogrid = qmenu.item("&Force to grid", force_to_grid_click,"|Force to grid:\n\nThis will cause a tag or tag frame to 'snap' to the nearest location on the editor's grid and change all of its other tag frames accordingly.\n\nIf a tag frame is not selected then the first tag frame will be used.|intro.modeleditor.rmbmenus.html#bonecommands")
        DeleteTag = qmenu.item("&Delete this tag", delete_tag_click, "|Delete this tag:This will delete the single tag clicked on and its tag frames from the 'Misc' group, all components it belongs to will remain.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.editelements.html#tags")

        Forcetogrid.state = qmenu.disabled
        if editor.gridstep:
            Forcetogrid.state = qmenu.normal

        menu = [SelectTag, qmenu.sep, HTT, qmenu.sep, Forcetogrid, qmenu.sep, DeleteTag]

        return menu


    def draw(self, view, cv, draghandle=None):
        editor = self.editor
        from qbaseeditor import flagsmouse
        import qhandles

        # This stops the drawing of all the vertex handles during a Linear drag to speed drawing up.
        if flagsmouse == 1032:
            if isinstance(editor.dragobject, qhandles.Rotator2D) or draghandle is None:
                pass
            else:
                return

        if flagsmouse == 528 or flagsmouse == 1040: return # RMB pressed or dragging to pan (scroll) in the view.

        if view.info["viewname"] == "editors3Dview":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                return
        elif view.info["viewname"] == "XY":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                return
        elif view.info["viewname"] == "YZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                return
        elif view.info["viewname"] == "XZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                return
        elif view.info["viewname"] == "3Dwindow":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                return

        if self.tagframe in editor.layout.explorer.sellist or self.tagframe.parent in editor.layout.explorer.sellist:
            icon = ico_dict['ico_objects'][1][46]
        else:
            icon = ico_dict['ico_objects'][0][46]
        if self.pos.visible:
            point = view.proj(self.pos)
            if self.tagframe.dictspec.has_key('bone'):
                tag_bonename = self.tagframe.dictspec['bone']
                if editor.ModelComponentList['bonelist'].has_key(tag_bonename):
                    frame_name = self.tagframe.shortname
                    if frame_name.find("baseframe") != -1:
                        frame_name = "baseframe"
                    frame_name = frame_name.replace("Tag ", "")
                    frame_name = frame_name.replace("tag ", "")
                    frame_name = frame_name + ":mf"
                    bone_pos = editor.ModelComponentList['bonelist'][tag_bonename]['frames'][frame_name]['position']
                    bp = view.proj(quarkx.vect(bone_pos))
                    if view.viewmode == "wire":
                        cv.pencolor = BLACK
                    else:
                        cv.pencolor = WHITE
                    cv.line(int(bp.x), int(bp.y), int(point.x), int(point.y))
            cv.draw(icon, int(point.x-7), int(point.y-7))


    def drag(self, v1, v2, flags, view):
        editor = mapeditor()
        p0 = view.proj(self.pos)

        if not p0.visible: return
        view.repaint()
        if flags&MB_CTRL:
            v2 = qhandles.aligntogrid(v2, 0)
            plugins.mdlgridscale.gridfinishdrawing(editor, view)
        pv2 = view.proj(v2)        ### v2 is the SINGLE handle's (being dragged) 3D position (x,y and z in space).
                                   ### And this converts its 3D position to the monitor's FLAT screen 2D and 3D views
                                   ### 2D (x,y) position to draw it, (NOTICE >) using the 3D "y" and "z" position values.
        delta = v2-v1
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)

        if view.info["viewname"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["viewname"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + " " + ftoss(self.pos.z+delta.z)
        elif view.info["viewname"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            s = "was %s"%self.pos + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        self.draghint = s

        new_tagframe = self.tagframe.copy()
        new_tagframe['origin'] = (self.pos + delta).tuple
        cv = view.canvas()
        icon = ico_dict['ico_objects'][1][46]
        cv.draw(icon, int(pv2.x-7), int(pv2.y-7))

        return [self.tagframe], [new_tagframe]


    def ok(self, editor, undo, old_tagframe_list, new_tagframe_list): # x_tagframe_list only contains the single tag_frame whos tag handle was being dragged.
        movediff = quarkx.vect(new_tagframe_list[0].dictspec['origin']) - quarkx.vect(old_tagframe_list[0].dictspec['origin'])
        for tag_frame in new_tagframe_list[0].parent.subitems:
            if tag_frame.name == new_tagframe_list[0].name:
                continue
            new_tag_frame = tag_frame.copy()
            new_tag_frame['origin'] = (quarkx.vect(tag_frame.dictspec['origin']) + movediff).tuple
            undo.exchange(tag_frame, new_tag_frame)
        editor.ok(undo, self.undomsg)


#
# Poly Classes and Functions.
#
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
    # Complete a red image with the whole polyhedron.
    # (red images cannot be reduced to a single face; even if
    #  we drag just a face, we want to see the whole polyhedron)
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


def perptonormthru(source, dest, normthru):
    "The line from source to dest that is perpendicular to (normalized) normthru."
    diff = source-dest
    dot = diff*normthru
    return diff - dot*normthru


def getotherfixed(v, vtxes, axis):
    "If vtxes contains a point close to the line thru v along axis, return it, otherwise v+axis."
    for v2 in vtxes:
        if not (v-v2):
            continue;
        perp = perptonormthru(v2,v,axis.normalized)
        if abs(perp)<.05:
            return v2
    return v+axis


#
# Poly Handle Classes.
#
class FaceHandle(qhandles.GenericHandle):
    "Center of a face."

    undomsg = Strings[516]
    hint = "move this face (Ctrl key: force center to grid)||This handle lets you scroll this face, thus distort the polyhedron(s) that contain it.\n\nNormally, the face can be moved by steps of the size of the grid; holding down the Ctrl key will force the face center to be exactly on the grid."

    def __init__(self, pos, face):
        qhandles.GenericHandle.__init__(self, pos)
        self.newpoly = None
        self.face = face
        cur = FaceHandleCursor()
        cur.pos = pos
        cur.face = face
        self.cursor = cur.getcursor

    def menu(self, editor, view):
        Force1 = qmenu.item("&Force center to grid", editor.ForceEverythingToGrid, "force to grid")
        Force1.state = not editor.gridstep and qmenu.disabled
        return [Force1] + self.OriginItems(editor, view)

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
            else: # Goes through this section twice at the end of a face drag, when the LMB is released.
                if self.newpoly is not None: # 2nd time through.
                    # Gets the original poly before the face drag.
                    oldpoly = self.face.faceof[0]
                    # Makes a brand new work poly, gives it the oldpoly name, to get all things correct.
                    poly = quarkx.newobj(oldpoly.name)
                    poly['show'] = (1.0,)
                    # Gets the oldpoly faces in their proper order.
                    polykeys = []
                    for p in oldpoly.subitems:
                        polykeys = polykeys + [p.name]
                    # Copies the newpoly faces, at the end of the drag, to our poly.
                    for key in polykeys:
                        new_face = self.newpoly.dictitems[key].copy()
                        poly.appenditem(new_face)
                    # Does the same for all the dictspec items of the newpoly.
                    for spec in self.newpoly.dictspec.keys():
                        poly[spec] = self.newpoly.dictspec[spec]
                    # Updates what the tree-view selections, expanded folders and objects are so oldpoly.flags are current.
                    RestoreTreeView(mdleditor.mdleditor)
                    # Passes the current updated oldpoly.flags to our work poly.
                    poly.flags = oldpoly.flags
                    # Finally, returns our work poly as the new poly at the end of the drag with all things correct and intact.
                    return [oldpoly], [poly]
                else: # 1st time through, newpoly is not complete, the poly name is incorrect and no dictspec data is in it.
                    self.newpoly = completeredimage(self.face, new)[0]
                    oldpoly = self.face.faceof[0]
                    self.newpoly.shortname = oldpoly.shortname # Fix the newpoly name to the same as the oldpoly name.
                    self.newpoly["assigned2"] = oldpoly.dictspec["assigned2"] # Add a missing dictspec that we need.
                    new = [new]
        else:
            new = None
        return [self.face], new

    def ok(self, editor, undo, old, new, view=None):
        newpoly = new[0]
        if newpoly.broken:
            undo.cancel()
            quarkx.beep()
            editor.layout.explorer.uniquesel = old[0]
            editor.layout.explorer.sellist = [old[0]]
            quarkx.msgbox("Invalid Drag !\n\nWill cause broken poly.\nAction canceled.", qutils.MT_ERROR, qutils.MB_OK)
            Update_Editor_Views(editor)
            return
        for face in newpoly.subitems:
            if face.broken:
                undo.cancel()
                quarkx.beep()
                editor.layout.explorer.uniquesel = old[0]
                editor.layout.explorer.sellist = [old[0]]
                quarkx.msgbox("Invalid Drag !\n\nWill cause broken poly.\nAction canceled.", qutils.MT_ERROR, qutils.MB_OK)
                Update_Editor_Views(editor)
                return
        UpdateBBoxList(editor, newpoly)
        editor.ok(undo, self.undomsg)
        editor.layout.explorer.uniquesel = newpoly
        editor.layout.explorer.sellist = [newpoly]



class PFaceHandle(FaceHandle):
    "Center of a face, but unselected (as part of a selected poly)."

    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = view.darkcolor
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)



class PolyHandle(qhandles.CenterHandle):
    "BBox polyhedron Center Handle."

    undomsg = Strings[515]
    hint = "move polyhedron (Ctrl key: force center to grid)||Lets you move this polyhedron.\n\nYou can move it by steps equal to the grid size. This means that if it is not on the grid now, it will not be after the move, either. You can force it on the grid by holding down the Ctrl key, but be aware that this forces its center to the grid, not all its faces. For cubic polyhedron, you may need to divide the grid size by two before you get the expected results."

    def __init__(self, pos, poly):
        qhandles.CenterHandle.__init__(self, pos, poly, 0x202020, 1)
        self.poly = poly

    def click(self, editor):
        if not self.poly.selected:   # case of the polyhedron center handle if only a face is selected this causes the poly to become selected instead.
            editor.layout.explorer.uniquesel = self.poly
            return "S"

    def comp_extras_menu(self, editor, view=None):
        "This is the BBox's extras menu for items that can be placed on other menus involving components."

        choice_comps = []
        for obj in editor.Root.dictitems:
            if obj.endswith(":mc"):
                choice_comps = choice_comps + [obj]

        bboxes = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':p')
        bboxlist_comps = []
        for bbox in bboxes:
            if bbox.dictspec['assigned2'].endswith(":mc") and not bbox.dictspec['assigned2'] in bboxlist_comps:
                bboxlist_comps = bboxlist_comps + [bbox.dictspec['assigned2']]

        bboxlist = editor.ModelComponentList['bboxlist']
        sellist = editor.layout.explorer.sellist

        def onclick1(m, editor=editor): # for assign_bbox_click
            poly = editor.layout.explorer.sellist[0]
            Old_poly = poly.copy()
            Old_poly['assigned2'] = m.text + ":mc"
            name = m.text + " " + poly.shortname
            polys = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':p')
            count = 1
            for p in polys:
                if p.shortname == name:
                    count = count + 1
            if count != 1:
                name = m.text + " bbox " + str(count)
            Old_poly.shortname = name
            New_poly = UpdateBBoxList(editor, Old_poly)
            explorer = editor.layout.explorer
            undo = quarkx.action()
            undo.exchange(poly, New_poly)
            editor.ok(undo, "bbox assigned to component")
            DrawBBoxes(editor, explorer, editor.Root.currentcomponent)
            editor.layout.explorer.uniquesel = New_poly
            editor.layout.explorer.sellist = [New_poly]

        def onclick2(m, editor=editor, bboxlist=bboxlist): # for release_bbox_click
            poly = editor.layout.explorer.sellist[0]
            del bboxlist[poly.name]
            New_poly = poly.copy()
            New_poly['assigned2'] = "None"
            parent = editor.Root.dictitems['Misc:mg']
            polys = parent.findallsubitems("", ':p')
            count = 1
            for p in polys:
                if p.shortname.startswith("bbox "):
                    nbr = None
                    try:
                        nbr = p.shortname.split(" ")[1]
                    except:
                        pass
                    if nbr is not None:
                        if int(nbr) >= count:
                            count = int(nbr) + 1
                    else:
                        count = count + 1
            New_poly.shortname = "bbox " + str(count)
            undo = quarkx.action()
            undo.exchange(poly, New_poly)
            editor.ok(undo, "bbox released")
            editor.layout.explorer.uniquesel = New_poly
            editor.layout.explorer.sellist = [New_poly]

        def onclick3(m, editor=editor): # for select_bboxs_click
            comp_name = m.text + ':mc'
            parent = editor.Root.dictitems['Misc:mg']
            polys = parent.findallsubitems("", ':p')
            sellist = []
            for poly in polys:
                if poly.dictspec['assigned2'] == comp_name:
                    sellist = sellist + [poly]
            editor.layout.explorer.sellist = sellist

        def onclick4(m, editor=editor, bboxlist=bboxlist): # for release_bboxs_click
            comp_name = m.text + ':mc'
            parent = editor.Root.dictitems['Misc:mg']
            polys = parent.findallsubitems("", ':p')
            count = 1
            for p in polys:
                if p.shortname.startswith("bbox "):
                    nbr = None
                    try:
                        nbr = p.shortname.split(" ")[1]
                    except:
                        pass
                    if nbr is not None:
                        if int(nbr) >= count:
                            count = int(nbr) + 1
                    else:
                        count = count + 1
            undo = quarkx.action()
            for poly in polys:
                if poly.dictspec['assigned2'] == comp_name:
                    del bboxlist[poly.name]
                    New_poly = poly.copy()
                    New_poly['assigned2'] = "None"
                    New_poly.shortname = "bbox " + str(count)
                    count = count + 1
                    undo.exchange(poly, New_poly)
            editor.ok(undo, "bboxes released")


        def assign_bbox_click(m, self=self, editor=editor, choice_comps=choice_comps, view=view):
            componentnames = choice_comps
            if len(componentnames) == 0:
                quarkx.msgbox("Improper Selection!\n\nThere are no components available to assign this bbox to.", MT_ERROR, MB_OK)
                return None, None
            else:
                componentnames.sort()
                menu = []
                for compname in componentnames:
                    menu = menu + [qmenu.item(compname.split(":")[0], onclick1)]
                m.items = menu

        def assign_vtxs_click(m, self=self, editor=editor, view=view):
            comp = editor.Root.currentcomponent
            explorer = editor.layout.explorer
            poly = editor.layout.explorer.sellist[0]
            New_poly = poly.copy()
            name = comp.shortname + " " + poly.shortname
            polys = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':p')
            count = 1
            for p in polys:
                if p.shortname == name:
                    count = count + 1
            if count != 1:
                name = comp.shortname + " bbox " + str(count)
            New_poly.shortname = name
            New_poly['assigned2'] = comp.name
            bboxlist = editor.ModelComponentList['bboxlist']
            bboxlist[New_poly.name] = {}
            bboxlist[New_poly.name]['vtx_list'] = editor.ModelVertexSelList
            undo = quarkx.action()
            undo.exchange(poly, New_poly)
            editor.ok(undo, "bbox assigned vertexes")
            DrawBBoxes(editor, explorer, comp)
            editor.layout.explorer.uniquesel = New_poly
            editor.layout.explorer.sellist = [New_poly]

        def release_bbox_click(m, self=self, editor=editor, view=view):
            poly = editor.layout.explorer.sellist[0]
            assigned2 = poly.dictspec['assigned2']
            menu = [qmenu.item(assigned2.split(":")[0], onclick2)]
            m.items = menu
        
        def select_bboxes_click(m, self=self, editor=editor, bboxlist_comps=bboxlist_comps, view=view):
            componentnames = bboxlist_comps
            componentnames.sort()
            menu = []
            for compname in componentnames:
                menu = menu + [qmenu.item(compname.split(":")[0], onclick3)]
            m.items = menu

        def release_bboxes_click(m, self=self, editor=editor, bboxlist_comps=bboxlist_comps, view=view):
            componentnames = bboxlist_comps
            componentnames.sort()
            menu = []
            for compname in componentnames:
                menu = menu + [qmenu.item(compname.split(":")[0], onclick4)]
            m.items = menu

        AssignBBoxTo = qmenu.popup("Assign BBox To", [], assign_bbox_click, "|Assign BBox To:\n\nYou need to select a single BBox to use this function.\n\nThis will assign a selected bounding box to the component (if NOT Hidden) you select by means of a menu that will appear listing all available components to choose from, if any.", "intro.modeleditor.rmbmenus.html#bboxrmbmenu")
        AssignBBoxVtxs = qmenu.item("Assign Vtxs To BBox", assign_vtxs_click, "|Assign Vtxs To BBox:\n\nYou need to have some vertexes and a single BBox selected to use this function.\n\nThis will assign a selected bounding box to the selected vertexes of a component (if NOT Hidden) you must first select the vertexes then Ctrl select a bbox.|intro.modeleditor.rmbmenus.html#bboxrmbmenu")
        ReleaseBBox = qmenu.popup("Release BBox", [], release_bbox_click, "|Release BBox:\n\nThis will release the selected bounding box assigned to the component (if NOT Hidden) you select by means of a menu that will appear listing the component it is assigned to.", "intro.modeleditor.rmbmenus.html#bboxrmbmenu")
        SelectBBoxes = qmenu.popup("Select BBoxes", [], select_bboxes_click, "|Select BBoxes:\n\nThis will select all the bounding boxes assigned to the component (if NOT Hidden) you select by means of a menu that will appear listing all available components to choose from, if any.", "intro.modeleditor.rmbmenus.html#bboxrmbmenu")
        ReleaseBBoxes = qmenu.popup("Release BBoxes", [], release_bboxes_click, "|Release BBoxes:\n\nThis will release all the bounding boxes assigned to the component (if NOT Hidden) you select by means of a menu that will appear listing all available components to choose from, if any.", "intro.modeleditor.rmbmenus.html#bboxrmbmenu")

        AssignBBoxTo.state = qmenu.disabled
        AssignBBoxVtxs.state = qmenu.disabled
        SelectBBoxes.state = qmenu.disabled
        ReleaseBBoxes.state = qmenu.disabled

        menu = [AssignBBoxTo, AssignBBoxVtxs, SelectBBoxes, ReleaseBBoxes]
        if len(sellist) >= 1 and sellist[0].type == ":p":
            if sellist[0].dictspec['assigned2'] == "None":
                AssignBBoxTo.state = qmenu.normal
                if len(editor.ModelVertexSelList) != 0:
                    AssignBBoxVtxs.state = qmenu.normal
            elif sellist[0].dictspec['assigned2'].endswith(":mc"):
                menu = [ReleaseBBox, SelectBBoxes, ReleaseBBoxes]
            if len(bboxlist_comps) != 0:
                SelectBBoxes.state = qmenu.normal
                ReleaseBBoxes.state = qmenu.normal
        elif len(bboxlist_comps) != 0:
            SelectBBoxes.state = qmenu.normal
            ReleaseBBoxes.state = qmenu.normal

        return menu


    def bone_extras_menu(self, editor, obj=None, view=None):
        "This is the BBox's extras menu for items that can be placed on other menus involving bones."
        # obj is a bone that a bbox can be assigned to.

        bone_bbox_list = []
        if obj is not None:
                bboxes = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':p')
                for bbox in bboxes:
                    if bbox.dictspec['assigned2'] == obj.name and not bbox in bone_bbox_list:
                        bone_bbox_list = bone_bbox_list + [bbox]

        bboxlist = editor.ModelComponentList['bboxlist']
        sellist = editor.layout.explorer.sellist
        if self.poly is None:
            for item in sellist:
                if item.type == ":p":
                    self.poly = item
                    break

        def assign_bbox_click(m, editor=editor, obj=obj):
            bboxlistkeys = editor.ModelComponentList['bboxlist'].keys()
            name = obj.name.replace(":bone", ":p")
            if name in bboxlistkeys:
                count = 1
                while 1:
                    name = obj.shortname + str(count) + ":p"
                    if name in bboxlistkeys:
                        count = count + 1
                    else:
                        name = name.replace(":p", "")
                        break
            else:
                name = name.replace(":p", "")
            New_poly = self.poly.copy()
            New_poly['assigned2'] = obj.name
            New_poly.shortname = name
            New_poly = UpdateBBoxList(editor, New_poly)
            explorer = editor.layout.explorer
            undo = quarkx.action()
            undo.exchange(self.poly, New_poly)
            editor.ok(undo, "bbox assigned to bone")
            DrawBBoxes(editor, explorer, editor.Root.currentcomponent)
            editor.layout.explorer.uniquesel = New_poly
            editor.layout.explorer.sellist = [New_poly]

        def release_bbox_click(m, editor=editor, bboxlist=bboxlist, obj=obj, bone_bbox_list=bone_bbox_list):
            Old_poly = self.poly
            if obj is None:
                bones = editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone')
                bone_name = Old_poly.dictspec['assigned2']
                for bone in bones:
                    if bone.name == bone_name:
                         obj = bone
                         break
            if obj is None and Old_poly is not None and Old_poly.dictspec['assigned2'] != "None":
                New_poly = UpdateBBoxList(editor, Old_poly)
                New_poly['assigned2'] = "None"
                del bboxlist[Old_poly.name]
                undo = quarkx.action()
                undo.exchange(Old_poly, New_poly)
                editor.ok(undo, "bbox released")
                editor.layout.explorer.uniquesel = New_poly
                editor.layout.explorer.sellist = [New_poly]
            elif obj.type == ":bone":
                poly_name = obj.shortname + ":p"
                if Old_poly is None:
                    polys = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':p')
                    for poly in polys:
                        if poly.name == poly_name:
                            Old_poly = poly
                            break
                if Old_poly is None:
                    Old_poly = bone_bbox_list[0]
                New_poly = UpdateBBoxList(editor, Old_poly)
                New_poly['assigned2'] = "None"
                del bboxlist[Old_poly.name]
                undo = quarkx.action()
                undo.exchange(Old_poly, New_poly)
                editor.ok(undo, "bbox released")
                editor.layout.explorer.uniquesel = New_poly
                editor.layout.explorer.sellist = [New_poly]

        def select_bbox_click(m, editor=editor, bboxlist=bboxlist, obj=obj, bone_bbox_list=bone_bbox_list):
            if self.poly is not None:
                editor.layout.explorer.sellist = [self.poly]
            elif obj is not None and obj.shortname + ":p" in bboxlist.keys():
                poly_name = obj.shortname + ":p"
                polys = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':p')
                for poly in polys:
                    if poly.name == poly_name:
                        editor.layout.explorer.sellist = [poly]
                        break
            else:
                editor.layout.explorer.sellist = [bone_bbox_list[0]]
            editor.layout.selchange()

        def onclick1(m, editor=editor, bone_bbox_list=bone_bbox_list): # for select_bbox_click2
            bbox_name = m.text + ':p'
            sellist = []
            for poly in bone_bbox_list:
                if poly.name == bbox_name:
                    sellist = sellist + [poly]
                    break
            editor.layout.explorer.sellist = sellist

        def onclick2(m, editor=editor, bboxlist=bboxlist, bone_bbox_list=bone_bbox_list): # for release_bbox_click2
            bbox_name = m.text + ':p'
            sellist = []
            for poly in bone_bbox_list:
                if poly.name == bbox_name:
                    Old_poly = poly
                    break
            New_poly = UpdateBBoxList(editor, Old_poly)
            New_poly['assigned2'] = "None"
            del bboxlist[Old_poly.name]
            undo = quarkx.action()
            undo.exchange(Old_poly, New_poly)
            editor.ok(undo, "bbox released")
            editor.layout.explorer.uniquesel = New_poly
            editor.layout.explorer.sellist = [New_poly]
        
        def select_bbox_click2(m, editor=editor, bone_bbox_list=bone_bbox_list):
            menu = []
            for bbox in bone_bbox_list:
                menu = menu + [qmenu.item(bbox.shortname, onclick1)]
            m.items = menu

        def release_bbox_click2(m, editor=editor, bone_bbox_list=bone_bbox_list):
            menu = []
            for bbox in bone_bbox_list:
                menu = menu + [qmenu.item(bbox.shortname, onclick2)]
            m.items = menu

        def select_bboxes_click(m, editor=editor, bone_bbox_list=bone_bbox_list):
            editor.layout.explorer.sellist = bone_bbox_list
            editor.layout.selchange()

        def release_bboxes_click(m, editor=editor, bboxlist=bboxlist, obj=obj, bone_bbox_list=bone_bbox_list):
            parent = editor.Root.dictitems['Misc:mg']
            polys = parent.findallsubitems("", ':p')
            count = 1
            for p in polys:
                if p.shortname.startswith("bbox "):
                    nbr = None
                    try:
                        nbr = p.shortname.split(" ")[1]
                    except:
                        pass
                    if nbr is not None:
                        if int(nbr) >= count:
                            count = int(nbr) + 1
                    else:
                        count = count + 1
            undo = quarkx.action()
            for bbox in bone_bbox_list:
                Old_poly = bbox
                New_poly = UpdateBBoxList(editor, Old_poly, count)
                New_poly['assigned2'] = "None"
                del bboxlist[Old_poly.name]
                undo.exchange(Old_poly, New_poly)
                count = count + 1
            editor.ok(undo, "bboxes released")
            editor.layout.explorer.uniquesel = None
            editor.layout.explorer.sellist = []

        AssignReleaseBBox = qmenu.item("Assign \ Release BBox", None, "|Assign \ Release BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        AssignReleaseBBox.state = qmenu.disabled
        menulist = [AssignReleaseBBox]

        if len(bone_bbox_list) < 2 or (len(sellist) == 1 and sellist[0].type == ":p"):
            if obj is not None and self.poly is not None and self.poly.dictspec['assigned2'] == "None":
                if obj.type == ":bone": # Bone can have multiple bboxes.
                    assign_bbox = qmenu.item("Assign BBox "+self.poly.shortname, assign_bbox_click, "|Assign BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                    menulist = [assign_bbox]
            elif self.poly is not None and self.poly.dictspec['assigned2'] != "None":
                if obj is not None and obj.name == self.poly.dictspec['assigned2']:
                    release_bbox = qmenu.item("Release BBox "+self.poly.shortname, release_bbox_click, "|Release BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                    select_bbox = qmenu.item("Select BBox "+self.poly.shortname, select_bbox_click, "|Select BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                    menulist = [release_bbox, select_bbox]
                else:
                    release_bbox = qmenu.item("Release BBox "+self.poly.shortname, release_bbox_click, "|Release BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                    menulist = [release_bbox]
            elif obj is not None:
                if obj.type == ":bone": # Bone can have multiple bboxes.
                    if obj.shortname + ":p" in bboxlist.keys():
                        release_bbox = qmenu.item("Release BBox "+obj.shortname, release_bbox_click, "|Release BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                        select_bbox = qmenu.item("Select BBox "+obj.shortname, select_bbox_click, "|Select BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                        menulist = [release_bbox, select_bbox]
                    elif len(bone_bbox_list) != 0:
                        release_bbox = qmenu.item("Release BBox "+bone_bbox_list[0].shortname, release_bbox_click, "|Release BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                        select_bbox = qmenu.item("Select BBox "+bone_bbox_list[0].shortname, select_bbox_click, "|Select BBox:\n\nBBox is a polyhedron box that is called by different names\nand are used for different things based on a game models format.\nCommonly it surrounds an area for a 'hitbox', 'collision', 'bounding box'...\n\nWhen a BBox is selected and a RMB click on the center of a bone is made, then that BBox can be assigned to that bone, or release from that bone\nif both have not already been assigned to something else that would cause a conflict.\n\nTo properly position the BBox on the bone, use its center handle and drag it to the coords 0,0,0 in the editor's views BEFORE you assign it to a bone. Once assigned you can change the BBox size by dragging its side handles, the corner handles will NOT hold its shape.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                        menulist = [release_bbox, select_bbox]
        else:
            SelectBBox = qmenu.popup("Select BBox", [], select_bbox_click2, "|Select BBox:\n\nThis will select a bounding box assigned to the bone (if NOT Hidden). You select by means of a menu that will appear listing all of a bone's bounding boxes to choose from.", "intro.modeleditor.rmbmenus.html#facermbmenu")
            ReleaseBBox = qmenu.popup("Release BBox", [], release_bbox_click2, "|Release BBox:\n\nThis will release a bounding box assigned to the bone (if NOT Hidden). You select by means of a menu that will appear listing all of a bone's bounding boxes to choose from.", "intro.modeleditor.rmbmenus.html#facermbmenu")
            SelectBBoxes = qmenu.item("Select BBoxes", select_bboxes_click, "|Select BBoxes:\n\nThis will select all the bounding boxes assigned to the bone (if NOT Hidden).|intro.modeleditor.rmbmenus.html#facermbmenu")
            ReleaseBBoxes = qmenu.item("Release BBoxes", release_bboxes_click, "|Release BBoxes:\n\nThis will release all the bounding boxes assigned to the bone (if NOT Hidden).|intro.modeleditor.rmbmenus.html#facermbmenu")
            menulist = [SelectBBox, ReleaseBBox, SelectBBoxes, ReleaseBBoxes]

        return menulist


    def menu(self, editor, view=None): # for Bounding Box Center Handle (PolyHandle)
        editor.layout.clickedview = view

        def hide_this_bbox_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            self.poly['show'] = (0.0,)
            mdlutils.Update_Editor_Views(editor)
            editor.layout.explorer.invalidate()

        def forcegrid1click(m, self=self, editor=editor, view=view):
            self.Action(editor, self.pos, self.pos, MB_CTRL, view, Strings[560])

        HTBB = qmenu.item("&Hide this bbox", hide_this_bbox_click)

        if self.poly.dictspec['assigned2'].endswith(":bone"):
            BBoxBoneExtras = self.bone_extras_menu(editor)
            return BBoxBoneExtras + [qmenu.sep, HTBB, qmenu.sep, qmenu.item("&Force to grid", forcegrid1click, "force vertex to grid")] + self.OriginItems(editor, view)
        elif self.poly.dictspec['assigned2'].endswith(":mc"):
            BBoxCompExtras = self.comp_extras_menu(editor, view)
            return BBoxCompExtras + [qmenu.sep, HTBB, qmenu.sep, qmenu.item("&Force to grid", forcegrid1click, "force vertex to grid")] + self.OriginItems(editor, view)
        elif self.poly.dictspec['assigned2'] == "None":
            BBoxAssignComp = self.comp_extras_menu(editor, view)[0]
            BBoxAssignVtxs = self.comp_extras_menu(editor, view)[1]
            return [BBoxAssignComp, qmenu.sep, BBoxAssignVtxs] + [qmenu.sep, HTBB, qmenu.sep, qmenu.item("&Force to grid", forcegrid1click, "force vertex to grid")] + self.OriginItems(editor, view)


    def ok(self, editor, undo, old, new, view=None):
        newpoly = new[0]
        UpdateBBoxList(editor, newpoly)
        editor.ok(undo, self.undomsg)


class PVertexHandle(qhandles.GenericHandle):
    "A polyhedron vertex."

    undomsg = Strings[525]
    hint = "Move vertex and distort polyhedron\n'n' key: move only one vertex\nAlt key: restricted to one face only\nCtrl key: force the vertex to the grid||Move vertex and distort polyhedron:\nBy dragging this point, you can distort the polyhedron.\n\nHolding down the 'n' key: This allows the movement of only ONE vertex and may add additional faces to obtain the shape.\n\nHolding down the Alt key: This allows only one face to move. It appears like you are moving the vertex of the polyhedron. In this case be aware that you might not always get the expected results, because you are not really dragging the vertex, but just rotating the adjacent faces in a way that simulates the vertex movement. If you move the vertex too far away, it might just disappear.|intro.terraingenerator.shaping.html#othervertexmovement"

    def __init__(self, pos, poly):
        qhandles.GenericHandle.__init__(self, pos)
        self.poly = poly
        self.cursor = CR_CROSSH


    def menu(self, editor, view):
        def forcegrid1click(m, self=self, editor=editor, view=view):
            v2 = qhandles.aligntogrid(self.pos, 1)
            self.Action(editor, self.pos, v2, MB_CTRL, view, Strings[560])

        def cutcorner1click(m, self=self, editor=editor, view=view):
            # Find all edges and faces issuing from the given vertex.
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

            # Remove duplicates.
            edgeends1 = []
            for i in range(len(edgeends)):
                e1 = edgeends[i]
                for e2 in edgeends[:i]:
                    if not (e1-e2):
                        break
                else:
                    edgeends1.append(e1)

            # Compute the mean point of edgeends1.
            # The new face will go through the point in the middle between this and the vertex.
            pt = reduce(lambda x,y: x+y, edgeends1)/len(edgeends1)

            # Compute the mean normal vector from the adjacent faces' normal vector.
            n = reduce(lambda x,y: x+y, map(lambda f: f.normal, faces))

            # Force "n" to be perpendicular to the screen direction.
            vertical = view.vector("z").normalized   # Vertical vector at this point.

            # Correction for 3D views, still needs some work though.
            if view.info["type"] == "3D":
                vertX, vertY, vertZ = vertical.tuple
                vertX = round(vertX)
                vertY = round(vertY)
                vertZ = round(vertZ)
                vertical = quarkx.vect(vertX, vertY, vertZ)
            n = (n - vertical * (n*vertical)).normalized

            # Find a "model" face for the new one.
            bestface = faces[0]
            for f in faces[1:]:
                if abs(f.normal*vertical) < abs(bestface.normal*vertical):
                    bestface = f

            # Build the new face.
            newface = bestface.copy()
            newface.shortname = "corner"
            newface.distortion(n, self.pos)

            # Move the face to its correct position.
            delta = 0.5*(pt-self.pos)
            delta = n * (delta*n)
            newface.translate(delta)

            # Insert the new face into the polyhedron.
            undo = quarkx.action()
            undo.put(self.poly, newface)
            editor.ok(undo, Strings[563])

  #      return [qmenu.item("&Cut out corner", cutcorner1click, "|This command cuts out the corner of the polyhedron. It does so by adding a new face near the vertex you right-clicked on. The new face is always perpendicular to the view."),
  #              qmenu.sep,
  #              qmenu.item("&Force to grid", forcegrid1click,
  #                "force vertex to grid")] + self.OriginItems(editor, view)
        return [qmenu.item("&Force to grid", forcegrid1click, "force vertex to grid")] + self.OriginItems(editor, view)


    def draw(self, view, cv, draghandle=None):
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = view.color
            cv.rectangle(int(p.x)-int(0.501), int(p.y)-int(0.501), int(p.x)+int(2.499), int(p.y)+int(2.499))


    def drag(self, v1, v2, flags, view):
        #### Vertex Dragging Code by Tim Smith ####

        # Compute the projection of the starting point? onto the screen.
        p0 = view.proj(self.pos)
        if not p0.visible: return

        # Save a copy of the original faces.
        orgfaces = self.poly.subitems

        # First, loop through the faces to see if we are draging
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

        # If the ALT key is pressed.
        if (flags&MB_ALT) != 0:

            # Loop through the list of points looking for the edge
            # that is closest to the new position.
            #
            # WARNING - THIS CODE ASSUMES THAT THE VERTECIES ARE ORDERED.
            #   IT ASSUMES THAT V1->V2 MAKE AND EDGE, V2->V3 etc...
            #
            # Note by Armin: this assumption is correct.
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

            # If a edge was found.
            if mindist < 99999999:
                # Compute the orthogonal projection of the destination point onto the edge.
                # Use the projection to compute a new value for delta.
                temp = dv1 - vtu1
                if not temp:
                    vtu1, vtu2 = vtu2, vtu1
                temp = dv1 - vtu1
                vtu2 = vtu2 - vtu1
                k = (temp * vtu2) / (abs (vtu2) * abs (vtu2))
                projdv1 = k * vtu2
                temp = projdv1 + vtu1

                #
                # Compute the final value for the delta.
                #
                if flags&MB_CTRL:
                    delta = qhandles.aligntogrid (temp, 1) - self.pos
                else:
                    delta = qhandles.aligntogrid (temp - self.pos, 0)

        # If the ALT key is NOT pressed.
        else:
            # If the control key is pressed, align the destination point to grid.
            if flags&MB_CTRL:
                v2 = qhandles.aligntogrid(v2, 1)

            # Compute the change in position.
            delta = v2-v1

            # If the control is not pressed, align delta to the grid.
            if not (flags&MB_CTRL):
                delta = qhandles.aligntogrid(delta, 0)

        # If we are dragging.
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
            # Make a copy of the polygon being drug.
            new = self.poly.copy()

            # Loop through the faces.
            for f in self.poly.faces:
                # If this face is part of the original group.
                if f in orgfaces:
                    # If the point is on the face.
                    if abs(self.pos*f.normal-f.dist) < epsilon:
                        # Collect a list of verticies on the face along
                        # with the distances from the destination point.
                        # Also, count the number of vertices.
                        # NOTE: this loop uses the actual distance between the
                        #       two points and not the screen distance.
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

                        # Sort the list of vertecies, this places the most distant point at the end.
                        vlist.sort ()
                        vmax = vlist [-1][1]

                        # If we are draging two vertecies.
                        if dragtwo:
                            # If this face does not have more than one vertex selected, then skip it.
                            if foundcount != 2:
                                continue

                            # The rotational axis is between the two points being drug.
                            # The reference point is the most distant point.
                            rotationaxis = mvlist [0] - mvlist [1]
                            otherfixed = getotherfixed(vmax, mvlist, rotationaxis)
                            fixedpoints = vmax, otherfixed

                        # Otherwise, we are draging one vertex.
                        else:
                            # If this face does not have any of the selected vertecies, then skip it.
                            if foundcount == 0:
                                continue

                            # METHOD A: Using the two most distant points as the axis of rotation.
                            if not (flags&MB_SHIFT):
                                rotationaxis = (vmax - vlist [-2] [1])
                                fixedpoints = vmax, vlist[-2][1]

                            # METHOD B: Using the most distant point,
                            # rotate along the perpendicular to the vector between
                            # the most distant point and the position.
                            else:
                                rotationaxis = (vmax - self .pos) ^ f .normal
                                otherfixed =getotherfixed(vmax, vlist, rotationaxis)
                                fixedpoints = vmax, otherfixed

                        # Apply the rotation axis to the face (requires that rotationaxis and vmax to be set).
                        newpoint = self.pos+delta
                        nf = new.subitem(orgfaces.index(f))

                        def pointsok(new,fixed):
                            # Coincident not OK.
                            if not new-fixed[0]: return 0
                            if not new-fixed[1]: return 0
                            # Colinear also not OK.
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
                            # Code 4 for NuTex.
                            nf.setthreepoints(tp ,2)

                # If the face is not part of the original group.
                else:
                    if not (flags&MB_DRAGGING):
                        continue   # Face is outside the polyhedron.
                    nf = f.copy()   # Put a copy of the face for the red image only.
                    new.appenditem(nf)
        # Final code.
            new = [new]
        else:
            new = None
        return [self.poly], new

    def ok(self, editor, undo, old, new, view=None):
        newpoly = new[0]
        if newpoly.broken:
            undo.cancel()
            quarkx.beep()
            quarkx.msgbox("Invalid Drag !\n\nWill cause broken poly.\nAction canceled.", qutils.MT_ERROR, qutils.MB_OK)
            Update_Editor_Views(editor)
            return
        for face in newpoly.subitems:
            if face.broken:
                undo.cancel()
                quarkx.beep()
                quarkx.msgbox("Invalid Drag !\n\nWill cause broken poly.\nAction canceled.", qutils.MT_ERROR, qutils.MB_OK)
                Update_Editor_Views(editor)
                return
        UpdateBBoxList(editor, newpoly)
        editor.ok(undo, self.undomsg)


#
# Model Handle Classes and functions.
#
class VertexHandle(qhandles.GenericHandle):
    "Frame Vertex handle."

    size = (3,3)

    def __init__(self, pos):
        qhandles.GenericHandle.__init__(self, pos)
        self.cursor = CR_CROSSH
        self.undomsg = "mesh vertex move"
        self.editor = mdleditor.mdleditor
        self.selection = []


    def menu(self, editor, view):

        def force_to_grid_click(m, self=self, editor=editor, view=view):
            v2 = qhandles.aligntogrid(self.pos, 1)
            self.Action(editor, self.pos, v2, view.flags, view, Strings[560])

        def add_vertex_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            addvertex(editor, editor.Root.currentcomponent, self.pos)

        def remove_vertex_click(m, self=self, editor=editor, view=view):
            removevertex(editor.Root.currentcomponent, self.index)
            editor.ModelVertexSelList = []

        def pick_base_vertex(m, self=self, editor=editor, view=view):
            if editor.ModelVertexSelList == []:
                editor.ModelVertexSelList = editor.ModelVertexSelList + [self.index]
                Update_Editor_Views(editor, 4)
                if (quarkx.setupsubset(SS_MODEL, "Options")["PVSTSV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1") and SkinView1 is not None:
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1":
                        editor.SkinVertexSelList = []
                    PassEditorSel2Skin(editor)
                    SkinView1.invalidate(1)
            else:
                if self.index == editor.ModelVertexSelList[0]:
                    editor.ModelVertexSelList = []
                    Update_Editor_Views(editor, 4)
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1" and SkinView1 is not None:
                        editor.SkinVertexSelList = []
                        SkinView1.invalidate(1)

        def change_base_vertex(m, self=self, editor=editor, view=view):
            vertices = editor.Root.currentcomponent.currentframe.vertices
            for item in editor.ModelVertexSelList:
                if str(view.proj(self.pos)) == str(vertices[item]) and str(view.proj(self.pos)) != str(vertices[editor.ModelVertexSelList[0]]):
                    quarkx.msgbox("Improper Selection!\n\nYou can not choose this vertex\nuntil you remove it from the Mesh list.\n\nSelection Canceled", MT_ERROR, MB_OK)
                    return None, None
                if str(view.proj(self.pos)) == str(vertices[item]):
                    pick_cleared(self)
                    break
            else:
                editor.ModelVertexSelList[0] = self.index
                Update_Editor_Views(editor, 4)
                if (quarkx.setupsubset(SS_MODEL, "Options")["PVSTSV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1") and SkinView1 is not None:
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1" and SkinView1 is not None:
                        editor.SkinVertexSelList = []
                    PassEditorSel2Skin(editor)
                    SkinView1.invalidate(1)

        def pick_vertex(m, self=self, editor=editor, view=view):
            itemcount = 0
            if editor.ModelVertexSelList == []:
                editor.ModelVertexSelList = editor.ModelVertexSelList + [self.index]
            else:
                for item in editor.ModelVertexSelList:
                    itemcount = itemcount + 1
                    if self.index == item:
                        editor.ModelVertexSelList.remove(item)
                        Update_Editor_Views(editor)
                        if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1" and SkinView1 is not None:
                            editor.SkinVertexSelList = []
                            PassEditorSel2Skin(editor)
                            try:
                                skindrawobject = editor.Root.currentcomponent.currentskin
                            except:
                                skindrawobject = None
                            buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
                            SkinView1.invalidate(1)
                        return
                    if itemcount == len(editor.ModelVertexSelList):
                        editor.ModelVertexSelList = editor.ModelVertexSelList + [self.index]

            Update_Editor_Views(editor)
            if (quarkx.setupsubset(SS_MODEL, "Options")["PVSTSV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1") and SkinView1 is not None:
                if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1":
                    editor.SkinVertexSelList = []
                PassEditorSel2Skin(editor)
                try:
                    skindrawobject = editor.Root.currentcomponent.currentskin
                except:
                    skindrawobject = None
                buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
                SkinView1.invalidate(1)

        def align_vertexes_click(m, self=self, editor=editor, view=view):
            if editor.Root.currentcomponent is None:
                return
            else:
                comp = editor.Root.currentcomponent
            if len(editor.ModelVertexSelList) > 1:
                oldpos = editor.Root.currentcomponent.currentframe.vertices[editor.ModelVertexSelList[1]]
            else:
                oldpos = self.pos

            pickedpos = editor.Root.currentcomponent.currentframe.vertices[editor.ModelVertexSelList[0]]

            import mdlmgr
            mdlmgr.savefacesel = 1
            if len(editor.ModelVertexSelList) > 1:
                replacevertexes(editor, comp, editor.ModelVertexSelList, 0, view, "multi Mesh vertex alignment", 0)
                editor.ModelVertexSelList = []
            else:
                self.Action(editor, oldpos, pickedpos, 0, view, "single Mesh vertex alignment")
                if len(editor.ModelVertexSelList) > 1:
                    editor.ModelVertexSelList.remove(editor.ModelVertexSelList[1])

        def pick_cleared(m, editor=editor, view=view):
            editor.ModelVertexSelList = []
            editor.dragobject = None
            Update_Editor_Views(editor)
            if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1" and SkinView1 is not None:
                editor.SkinVertexSelList = []
                SkinView1.invalidate()

        def AlignVertOpsMenu(editor):
            def mAPVexs_Method1(m, editor=editor):
                "Align Picked Vertexes to 'Base vertex' - Method 1"
                "Other selected vertexes move to the 'Base' vertex"
                "position of each tree-view selected 'frame'."
                if not MdlOption("APVexs_Method1"):
                    quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method1'] = "1"
                    quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method2'] = None
                else:
                    quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method1'] = None

            def mAPVexs_Method2(m, editor=editor):
                "Align Picked Vertexes to 'Base vertex' - Method 2"
                "Other selected vertexes move to the 'Base' vertex"
                "position of the 1st tree-view selected 'frame'."
                if not MdlOption("APVexs_Method2"):
                    quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method2'] = "1"
                    quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method1'] = None
                else:
                    quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method2'] = None
            
            Xapv_m1 = qmenu.item("Align vertexes-method 1", mAPVexs_Method1, "|Align vertexes-method 1:\n\nThis method will align, move, other selected vertexes to the 'Base' vertex position of each tree-view selected 'frame'.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
            Xapv_m2 = qmenu.item("Align vertexes-method 2", mAPVexs_Method2, "|Align vertexes-method 2:\n\nThis method will align, move, other selected vertexes to the 'Base' vertex position of the 1st tree-view selected 'frame'.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
            menulist = [Xapv_m1, Xapv_m2]
            items = menulist
            Xapv_m1.state = quarkx.setupsubset(SS_MODEL,"Options").getint("APVexs_Method1")
            Xapv_m2.state = quarkx.setupsubset(SS_MODEL,"Options").getint("APVexs_Method2")
            return menulist

        def align_vert_ops_click(m):
            editor = mdleditor.mdleditor
            m.items = AlignVertOpsMenu(editor)

        if len(editor.ModelVertexSelList) > 2:
            AlignText = "&Align mesh vertexes"
        else:
            AlignText = "&Align mesh vertex"

        def merge_vertexes_click(m, self=self, editor=editor, view=view):
            if editor.Root.currentcomponent is None:
                return
            else:
                comp = editor.Root.currentcomponent
            if len(editor.ModelVertexSelList) > 1:
                oldpos = editor.Root.currentcomponent.currentframe.vertices[editor.ModelVertexSelList[1]]
            else:
                oldpos = self.pos

            pickedpos = editor.Root.currentcomponent.currentframe.vertices[editor.ModelVertexSelList[0]]

            import mdlmgr
            mdlmgr.savefacesel = 1
            replacevertexes(editor, comp, editor.ModelVertexSelList, 0, view, "merged 2 vertexes", 2)

        def addtriclick(m, self=self, editor=editor, view=view):
            if len(editor.ModelVertexSelList) == 3:
                if (editor.ModelVertexSelList[0] < editor.ModelVertexSelList[1]) or (editor.ModelVertexSelList[0] < editor.ModelVertexSelList[2]):
                    if editor.ModelVertexSelList[1] > editor.ModelVertexSelList[2]:
                        quarkx.msgbox("You need to select\nvertex "+str(editor.ModelVertexSelList[1])+" first.", MT_ERROR, MB_OK)
                        return
                    else:
                        quarkx.msgbox("You need to select\nvertex "+str(editor.ModelVertexSelList[2])+" first.", MT_ERROR, MB_OK)
                        return
                else:
                  ### This will reverse the direction the triangle face is facing, when it is created, if the "Reverse Direction" command is active (checked).
                    templist = editor.ModelVertexSelList
                    if quarkx.setupsubset(SS_MODEL, "Options")["RevDir"] == "1":
                        editor.ModelVertexSelList = [templist[0], templist[2], templist[1]]
                    addtriangle(editor)

        def revdir(m, self=self, editor=editor, view=view):
            if not MdlOption("RevDir"):
                quarkx.setupsubset(SS_MODEL, "Options")['RevDir'] = "1"
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['RevDir'] = None
            ReverseDirection.state = quarkx.setupsubset(SS_MODEL,"Options").getint("RevDir")

        def remtriclick(m, self=self, editor=editor, view=view):
            if len(editor.ModelVertexSelList) == 3:
                removeTriangle_v3(editor)

        Forcetogrid = qmenu.item("&Force to grid", force_to_grid_click,"|Force to grid:\n\nThis will cause any vertex to 'snap' to the nearest location on the editor's grid for the view that the RMB click was made in.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        AddVertex = qmenu.item("&Add Vertex Here", add_vertex_click, "|Add Vertex Here:\n\nThis will add a single vertex to the currently selected model component (and all of its animation frames) to make a new triangle.\n\nYou need 3 new vertexes to make a triangle.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        RemoveVertex = qmenu.item("&Remove Vertex", remove_vertex_click, "|Remove Vertex:\n\nThis will remove a vertex from the component and all of its animation frames.\n\nWARNING, if the vertex is part of an existing triangle it will ALSO remove that triangle as well. If this does happen and is an unwanted action, simply use the Undo function to reverse its removal.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        PickBaseVertex = qmenu.item("&Pick Base Vertex", pick_base_vertex, "|Pick Base Vertex:\n\n This is used to pick, or remove, the 'Base' vertex to align other vertexes to in one of the editor's views. It also works in conjunction with the 'Clear Pick list' below it.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        ChangeBaseVertex = qmenu.item("&Change Base Vertex", change_base_vertex, "|Change Base Vertex:\n\n This is used to select another vertex as the 'Base' vertex to align other vertexes to in one of the editor's views. It also works in conjunction with the 'Clear Pick list' below it.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        PickVertex = qmenu.item("&Pick Vertex", pick_vertex, "|Pick Vertex:\n\n This is used for picking 3 vertexes to create a triangle with. It also works in conjunction with the 'Clear Pick list' below.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        AlignVertexes = qmenu.item(AlignText, align_vertexes_click,"|Align mesh vertex(s):\n\nOnce a set of vertexes have been 'Picked' in one of the editor views all of those vertexes will be moved to the 'Base' (stationary) vertex (the first one selected) location and aligned with that 'Base' vertex. It also works in conjunction with the 'Clear Pick list' above it.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        ClearPicklist = qmenu.item("&Clear Pick list", pick_cleared, "|Clear Pick list:\n\nThis Clears the 'Pick Vertex' list of all vertexes and it becomes active when one or more vertexes have been selected.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        AlignVertOpsPop = qmenu.popup("Align Vertex Options", [], align_vert_ops_click, "|Align Vertex Options:\n\nThis menu gives different methods of aligning 'Picked' vertexes to the 'Base' vertex.\n\nSee the help for each method for detail on how they work.", "intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        MergeVertexes = qmenu.item("&Merge Vertexes", merge_vertexes_click,"|Merge Vertexes:\n\nWhen two or more vertexes have been 'Picked' in one of the editor views this function becomes active allowing the 'picked' vertexes be moved to the 'Base' (stationary) vertex (the first one selected) location and aligned with that 'Base' vertex where they will then be merged into the one 'Base' vertex.\n\nTwo vertexes of the same face (triangle) can not be selected.\n\nThis function also works in conjunction with the 'Clear Pick list' above it.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        AddTriangle = qmenu.item("&Add Triangle", addtriclick, "|Add Triangle:\n\nThis adds a new triangle to the currently selected component.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.menu.html#commandsmenu")
        ReverseDirection = qmenu.item("Reverse Direction", revdir, "|Reverse Direction:\n\nNormally, in QuArK, creating a new triangles vertexes in a 'clockwise' direction will produce a triangle that faces 'outwards'.\n\nBut sometimes this does not work for adding new triangles to existing ones.\n\nActivating this function (checking it) will reverse that direction causing the triangle to face the opposite way.\n\nClick on the 'InfoBase' button for more detail.|intro.modeleditor.menu.html#commandsmenu")
        RemoveTriangle = qmenu.item("&Delete Triangle", remtriclick, "|Delete Triangle:\n\nThis removes a triangle from the currently selected component.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.menu.html#commandsmenu")

        AddTriangle.state = qmenu.disabled
        ReverseDirection.state = quarkx.setupsubset(SS_MODEL,"Options").getint("RevDir")
        RemoveTriangle.state = qmenu.disabled

        if len(editor.ModelVertexSelList) == 3:
            AddTriangle.state = qmenu.normal
            RemoveTriangle.state = qmenu.normal
        else:
            AddTriangle.state = qmenu.disabled
            RemoveTriangle.state = qmenu.disabled

        if not MdlOption("GridActive") or editor.gridstep <= 0:
            Forcetogrid.state = qmenu.disabled

        if len(editor.ModelVertexSelList) == 0:
            ClearPicklist.state = qmenu.disabled

        if editor.layout.explorer.sellist != [] and (editor.layout.explorer.sellist[0].type == ":mc" or editor.layout.explorer.sellist[0].type == ":fg" or editor.layout.explorer.sellist[0].type == ":mf"):
            AddVertex.state = qmenu.normal
        else:
            AddVertex.state = qmenu.disabled

        try:
            if len(editor.ModelVertexSelList) <= 1:
                MergeVertexes.state = qmenu.disabled
            if self.index is not None:
                if len(editor.ModelVertexSelList) == 0:
                    AlignVertexes.state = qmenu.disabled
                    PickVertex.state = qmenu.disabled
                    ClearPicklist.state = qmenu.disabled
                    menu = [AddVertex, RemoveVertex, qmenu.sep, PickBaseVertex, PickVertex, qmenu.sep, ClearPicklist, qmenu.sep, AlignVertexes, AlignVertOpsPop, qmenu.sep, MergeVertexes, qmenu.sep, Forcetogrid]
                else:
                    if len(editor.ModelVertexSelList) < 2:
                        AlignVertexes.state = qmenu.disabled
                    menu = [AddVertex, RemoveVertex, qmenu.sep, ChangeBaseVertex, PickVertex, qmenu.sep, ClearPicklist, qmenu.sep, AlignVertexes, AlignVertOpsPop, qmenu.sep, MergeVertexes, qmenu.sep, Forcetogrid]
            else:
                if len(editor.ModelVertexSelList) < 2:
                    AlignVertexes.state = qmenu.disabled
                menu = [AddVertex, qmenu.sep, ClearPicklist, qmenu.sep, AlignVertexes, AlignVertOpsPop, qmenu.sep, MergeVertexes]
        except:
            if len(editor.ModelVertexSelList) <= 1:
                MergeVertexes.state = qmenu.disabled
            if len(editor.ModelVertexSelList) < 2:
                AlignVertexes.state = qmenu.disabled
                MergeVertexes.state = qmenu.disabled
            menu = [AddVertex, qmenu.sep, ClearPicklist, qmenu.sep, AlignVertexes, AlignVertOpsPop, qmenu.sep, MergeVertexes, qmenu.sep, AddTriangle, ReverseDirection, RemoveTriangle]

        return menu

    def draw(self, view, cv, draghandle=None):
        editor = self.editor
        from qbaseeditor import flagsmouse, currentview # To stop all drawing, causing slowdown, during a zoom.
        import qhandles

        # This stops the drawing of all the vertex handles during a Linear drag to speed drawing up.
        if flagsmouse == 1032 or flagsmouse == 1036:
            if isinstance(editor.dragobject, qhandles.Rotator2D) or draghandle is None:
                pass
            else:
                return

        if flagsmouse == 2064:
            editor.dragobject = None
      #  else:
      #      if isinstance(editor.dragobject, qhandles.ScrollViewDragObject):
      #          return # RMB pressed or dragging to pan (scroll) in the view.
        if quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['AnimationCFGActive'] == "1":
            view.handles = []
            return
        if (flagsmouse == 520 or flagsmouse == 1032) and draghandle is not None: return # LMB pressed or dragging model mesh handle.
        if flagsmouse == 528 or flagsmouse == 1040: return # RMB pressed or dragging to pan (scroll) in the view.

        if view.info["viewname"] == "editors3Dview":
            if (flagsmouse == 1048 or flagsmouse == 1056) and currentview.info["viewname"] != "editors3Dview": return # Doing zoom in a 2D view, stop drawing the Editors 3D view handles.
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                return
        elif view.info["viewname"] == "XY":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                return
        elif view.info["viewname"] == "YZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                return
        elif view.info["viewname"] == "XZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                return
        elif view.info["viewname"] == "3Dwindow":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                return

        p = view.proj(self.pos)
        if p.visible:
            from mdlentities import vtxpaint
            # Here "color" is just a dummy item to pass the vertex's
            # color to so we can use the MapColor function to set the cv.pencolor correctly.
            color = None
            if editor.Root.currentcomponent.dictspec.has_key("show_vtx_color") and editor.ModelComponentList[editor.Root.currentcomponent.name]['colorvtxlist'].has_key(self.index) and editor.ModelComponentList[editor.Root.currentcomponent.name]['colorvtxlist'][self.index].has_key('vtx_color'):
                color = editor.ModelComponentList[editor.Root.currentcomponent.name]['colorvtxlist'][self.index]['vtx_color']
                quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
                cv.pencolor = cv.brushcolor = MapColor("color", SS_MODEL)
                cv.brushstyle = BS_SOLID
                if MdlOption("Ticks") == "1":
                    cv.ellipse(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
                else:
                    cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
            elif vtxpaint == 0 and quarkx.setupsubset(3, "Options")['VertexPaintMode'] is not None and quarkx.setupsubset(3, "Options")['VertexPaintMode'] == "1" and (flagsmouse == 552 or flagsmouse == 1064 or flagsmouse == 2088) and self == draghandle:
                foundbone = None
                for item in editor.layout.explorer.sellist:
                    if item.type == ":bone":
                        if item.dictspec.has_key(item.shortname + "_weight_color"):
                            color = item.dictspec[item.shortname + "_weight_color"]
                            foundbone = 1
                            break
                quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
                cv.pencolor = cv.brushcolor = MapColor("color", SS_MODEL)
                cv.brushstyle = BS_SOLID
                if MdlOption("Ticks") == "1":
                    cv.ellipse(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
                else:
                    cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
                if foundbone is not None:
                    update_weightvtxlist(editor, self.index) # Updates the ModelComponentList weightvtxlist HERE.
            elif editor.Root.currentcomponent.dictspec.has_key("show_weight_color") and editor.ModelComponentList[editor.Root.currentcomponent.name]['weightvtxlist'].has_key(self.index):
                if len(editor.layout.explorer.sellist) != 0 and editor.layout.explorer.sellist[0].type == ":bone" and editor.ModelComponentList[editor.Root.currentcomponent.name]['weightvtxlist'][self.index].has_key(editor.layout.explorer.sellist[0].name):
                    color = editor.ModelComponentList[editor.Root.currentcomponent.name]['weightvtxlist'][self.index][editor.layout.explorer.sellist[0].name]['color']
                else:
                    bones = editor.ModelComponentList[editor.Root.currentcomponent.name]['weightvtxlist'][self.index].keys()
                    if len(bones) != 0:
                        color = editor.ModelComponentList[editor.Root.currentcomponent.name]['weightvtxlist'][self.index][bones[0]]['color']
                if color is not None:
                    quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
                    cv.pencolor = cv.brushcolor = MapColor("color", SS_MODEL)
                cv.brushstyle = BS_SOLID
                if MdlOption("Ticks") == "1":
                    cv.ellipse(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
                else:
                    cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
            elif editor.ModelComponentList[editor.Root.currentcomponent.name]['bonevtxlist'] != {}:
                color = None
                for bone in editor.ModelComponentList[editor.Root.currentcomponent.name]['bonevtxlist'].keys():
                    if editor.layout.explorer.sellist[0].type == ":bone":
                        if bone == editor.layout.explorer.sellist[0].name:
                            if editor.ModelComponentList[editor.Root.currentcomponent.name]['bonevtxlist'][bone].has_key(self.index):
                                color = editor.ModelComponentList[editor.Root.currentcomponent.name]['bonevtxlist'][bone][self.index]['color']
                            break
                    elif editor.ModelComponentList[editor.Root.currentcomponent.name]['bonevtxlist'][bone].has_key(self.index):
                        color = editor.ModelComponentList[editor.Root.currentcomponent.name]['bonevtxlist'][bone][self.index]['color']
                if color is not None:
                    quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
                    cv.pencolor = cv.brushcolor = MapColor("color", SS_MODEL)
                    cv.brushstyle = BS_SOLID
                    if MdlOption("Ticks") == "1":
                        cv.ellipse(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
                    else:
                        cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
                else:
                    cv.pencolor = vertexdotcolor
                    cv.brushstyle = BS_SOLID
                    if MdlOption("Ticks") == "1":
                        cv.brushcolor = WHITE
                        cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
                    else:
                        cv.brushcolor = vertexdotcolor
                        cv.ellipse(int(p.x)-1, int(p.y)-1, int(p.x)+1, int(p.y)+1)
            else:
                cv.pencolor = vertexdotcolor
                cv.brushstyle = BS_SOLID
                if MdlOption("Ticks") == "1":
                    cv.brushcolor = WHITE
                    cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
                else:
                    cv.brushcolor = vertexdotcolor
                    cv.ellipse(int(p.x)-1, int(p.y)-1, int(p.x)+1, int(p.y)+1)

            editor = mdleditor.mdleditor
            if editor is not None:
                if editor.ModelVertexSelList != []:
                    if quarkx.setupsubset(3, "Options")['VertexPaintMode'] is not None and quarkx.setupsubset(3, "Options")['VertexPaintMode'] == "1":
                        cv.brushcolor = vertexsellistcolor
                        foundbone = None
        #                selsize = int(quarkx.setupsubset(SS_MODEL,"Building")['LinearSelected'][0])
                        for item in editor.ModelVertexSelList:
                            if self.index == item:
                                color = None
                                for sel in editor.layout.explorer.sellist:
                                    if sel.type == ":bone":
                                        if sel.dictspec.has_key(sel.shortname + "_weight_color"):
                                            color = sel.dictspec[sel.shortname + "_weight_color"]
                                            foundbone = 1
                                            break
                                if color is not None:
                                    quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
                                    cv.pencolor = cv.brushcolor = MapColor("color", SS_MODEL)
                                cv.brushstyle = BS_SOLID
                                if MdlOption("Ticks") == "1":
                                    cv.ellipse(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
                                else:
                                    cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
                                if foundbone is not None:
                                    update_weightvtxlist(editor, item) # Updates the ModelComponentList weightvtxlist HERE.
                    else:
                        cv.brushcolor = vertexsellistcolor
                        selsize = int(quarkx.setupsubset(SS_MODEL,"Building")['LinearSelected'][0])
                        for item in editor.ModelVertexSelList:
                            if self.index == item and item == editor.ModelVertexSelList[0]:
                                cv.brushcolor = drag3Dlines
                                cv.rectangle(int(p.x)-selsize, int(p.y)-selsize, int(p.x)+selsize, int(p.y)+selsize)
                            elif self.index == item:
                                cv.rectangle(int(p.x)-selsize, int(p.y)-selsize, int(p.x)+selsize, int(p.y)+selsize)


  #  For setting stuff up at the beginning of a drag
  #
    def start_drag(self, view, x, y):
        import mdleditor
        editor = mdleditor.mdleditor
        for item in editor.layout.explorer.sellist:
            if item.type == ':mf':
                self.selection = self.selection + [item]


    def drag(self, v1, v2, flags, view):
        editor = mapeditor()
        p0 = view.proj(self.pos)

        if not p0.visible: return
        if len(self.selection) == 0:
            for item in editor.layout.explorer.sellist:
                if item.type == ':mf':
                    self.selection = self.selection + [item]
        if flags&MB_CTRL:
            v2 = qhandles.aligntogrid(v2, 0)
            view.repaint()
            plugins.mdlgridscale.gridfinishdrawing(editor, view)
        pv2 = view.proj(v2)        ### v2 is the SINGLE handle's (being dragged) 3D position (x,y and z in space).
                                   ### And this converts its 3D position to the monitor's FLAT screen 2D and 3D views
                                   ### 2D (x,y) position to draw it, (NOTICE >) using the 3D "y" and "z" position values.
        delta = v2-v1
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)

        if view.info["viewname"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["viewname"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + " " + ftoss(self.pos.z+delta.z)
        elif view.info["viewname"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            s = "was %s"%self.pos + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        self.draghint = s

     #1   new = self.frame.copy() # Didn't know you could call a specific handles 'frame' like this. 8-o

        oldlist = self.selection
        newlist = []
        for frame in range(len(oldlist)):
            new = oldlist[frame].copy()
            if oldlist[frame].type != ":mf":
                newlist = newlist + [new]
            else:
                if frame == 0:
                    if delta or (flags&MB_REDIMAGE):
                        vtxs = new.vertices
                        vtxs[self.index] = vtxs[self.index] + delta
                        new.vertices = vtxs
                        newlist = newlist + [new]
                    # Drag handle drawing section using only the 1st frame of the 'sellist' for speed.
                    if flags == 1032:             ## To stop drag starting lines from being erased.
                        mdleditor.setsingleframefillcolor(editor, view)
                        view.repaint()            ## Repaints the view to clear the old lines.
                        plugins.mdlgridscale.gridfinishdrawing(editor, view) ## Sets the modelfill color.
                    cv = view.canvas()            ## Sets the canvas up to draw on.
                    cv.pencolor = drag3Dlines     ## Gives the pen color of the lines that will be drawn.

                    component = editor.Root.currentcomponent
                    if component is not None:
                        if component.name.endswith(":mc"):
                            handlevertex = self.index
                            tris = findTriangles(component, handlevertex)
                            for tri in tris:
                                if len(view.handles) == 0: continue
                                for vtx in tri:
                                    if self.index == vtx[0]:
                                        pass
                                    else:
                                        projvtx = view.proj(view.handles[vtx[0]].pos)
                                        cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(projvtx.tuple[0]), int(projvtx.tuple[1]))
                else:
                    if delta or (flags&MB_REDIMAGE):
                        vtxs = new.vertices
                        vtxs[self.index] = vtxs[self.index] + delta
                        new.vertices = vtxs
                        newlist = newlist + [new]

        return oldlist, newlist


  #  For setting stuff up at the end of a drag
  #
  #  def ok(self, editor, undo, old, new):
  #  def ok(self, editor, x, y, flags):
  #      undo=quarkx.action()
  #      editor.ok(undo, self.undomsg)



class SkinHandle(qhandles.GenericHandle):
    "Skin Handle for skin\texture positioning"

    size = (3,3)
    def __init__(self, pos, tri_index, ver_index, comp, texWidth, texHeight, triangle):
        qhandles.GenericHandle.__init__(self, pos)
        self.editor = mdleditor.mdleditor
        self.cursor = CR_CROSSH
        self.tri_index = tri_index
        self.ver_index = ver_index
        self.comp = comp
        self.texWidth = texWidth
        self.texHeight = texHeight
        self.triangle = triangle
        self.undomsg = "Skin-view drag"


    def menu(self, editor, view):

        def forcegrid1click(m, self=self, editor=editor, view=view):
            self.Action(editor, self.pos, self.pos, MB_CTRL, view, Strings[560])

        def pick_basevertex(m, self=self, editor=editor, view=view):
            if editor.SkinVertexSelList == []:
                editor.SkinVertexSelList = editor.SkinVertexSelList + [[self.pos, self, self.tri_index, self.ver_index]]
                cv = view.canvas()
                self.draw(view, cv, self)
                if quarkx.setupsubset(SS_MODEL, "Options")["PVSTEV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                        editor.ModelVertexSelList = []
                    PassSkinSel2Editor(editor)
                    Update_Editor_Views(editor, 1)

        def change_basevertex(m, self=self, editor=editor, view=view):
            for item in editor.SkinVertexSelList:
                if str(self.pos) == str(item[0]) and str(self.pos) != str(editor.SkinVertexSelList[0][0]):
                    quarkx.msgbox("Improper Selection!\n\nYou can not choose this vertex\nuntil you remove it from the Skin list.\n\nSelection Canceled", MT_ERROR, MB_OK)
                    return None, None
            if str(self.pos) == str(editor.SkinVertexSelList[0][0]):
                skinpick_cleared(self)
            else:
                editor.SkinVertexSelList[0] = [self.pos, self, self.tri_index, self.ver_index]
                if quarkx.setupsubset(SS_MODEL, "Options")["PVSTEV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                        editor.ModelVertexSelList = []
                    PassSkinSel2Editor(editor)
                    Update_Editor_Views(editor, 1)
                try:
                    skindrawobject = editor.Root.currentcomponent.currentskin
                except:
                    skindrawobject = None
                buildskinvertices(editor, view, editor.layout, editor.Root.currentcomponent, skindrawobject)
                view.invalidate()

        def pick_skinvertex(m, self=self, editor=editor, view=view):
            itemcount = 0
            removedcount = 0
            holdlist = []
                
            if editor.SkinVertexSelList == []:
                editor.SkinVertexSelList = editor.SkinVertexSelList + [[self.pos, self, self.tri_index, self.ver_index]]
            else:
                if str(self.pos) == str(editor.SkinVertexSelList[0][0]):
                    editor.SkinVertexSelList = []
                else:
                    setup = quarkx.setupsubset(SS_MODEL, "Options")
                    for item in editor.SkinVertexSelList:
                        if not setup["SingleVertexDrag"]:
                            if str(self.pos) == str(item[0]):
                                removedcount = removedcount + 1
                            else:
                                holdlist = holdlist + [item]
                        else:
                            if str(self.pos) == str(item[0]):
                                editor.SkinVertexSelList.remove(editor.SkinVertexSelList[itemcount])
                                try:
                                    skindrawobject = editor.Root.currentcomponent.currentskin
                                except:
                                    skindrawobject = None
                                buildskinvertices(editor, view, editor.layout, editor.Root.currentcomponent, skindrawobject)
                                view.invalidate(1)
                                if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                                    editor.ModelVertexSelList = []
                                    PassSkinSel2Editor(editor)
                                    Update_Editor_Views(editor, 1)
                                return
                            itemcount = itemcount + 1

                    if removedcount != 0:
                        editor.SkinVertexSelList = holdlist
                        try:
                            skindrawobject = editor.Root.currentcomponent.currentskin
                        except:
                            skindrawobject = None
                        buildskinvertices(editor, view, editor.layout, editor.Root.currentcomponent, skindrawobject)
                        view.invalidate(1)
                        if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                            editor.ModelVertexSelList = []
                            PassSkinSel2Editor(editor)
                            Update_Editor_Views(editor, 1)
                        return
                    else:
                        if not setup["SingleVertexDrag"]:
                            editor.SkinVertexSelList = holdlist

                    editor.SkinVertexSelList = editor.SkinVertexSelList + [[self.pos, self, self.tri_index, self.ver_index]]

                    if not setup["SingleVertexDrag"]:
                        dragtris = find2DTriangles(self.comp, self.tri_index, self.ver_index) # This is the funciton that gets the common vertexes in mdlutils.py.
                        for index,tri in dragtris.iteritems():
                            vtx_index = 0
                            for vtx in tri:
                                if str(vtx) == str(self.comp.triangles[self.tri_index][self.ver_index]):
                                    drag_vtx_index = vtx_index
                                    editor.SkinVertexSelList = editor.SkinVertexSelList + [[self.pos, self, index, drag_vtx_index]]
                                vtx_index = vtx_index + 1
            try:
                skindrawobject = editor.Root.currentcomponent.currentskin
            except:
                skindrawobject = None
            buildskinvertices(editor, view, editor.layout, editor.Root.currentcomponent, skindrawobject)
            view.invalidate(1)
            if quarkx.setupsubset(SS_MODEL, "Options")["PVSTEV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                    editor.ModelVertexSelList = []
                PassSkinSel2Editor(editor)
                Update_Editor_Views(editor, 1)

        def alignskinvertexesclick(m, self=self, editor=editor, view=view):
            if len(editor.SkinVertexSelList) > 1:
                self = editor.SkinVertexSelList[1][1]
                oldpos = editor.SkinVertexSelList[1][0]
            else:
                oldpos = self.pos

            pickedpos = editor.SkinVertexSelList[0][0]
            setup = quarkx.setupsubset(SS_MODEL, "Options")

            if len(editor.SkinVertexSelList) > 1:
                if self.comp is None:
                    self.comp = editor.Root.currentcomponent
                replacevertexes(editor, self.comp, editor.SkinVertexSelList, MB_CTRL, view, "multi Skin vertex alignment")
                editor.SkinVertexSelList = []
            else:
                self.Action(editor, oldpos, pickedpos, 0, view, "single Skin vertex alignment")
                if len(editor.SkinVertexSelList) > 1:
                    editor.SkinVertexSelList.remove(editor.SkinVertexSelList[1])

        def skinpick_cleared(m, editor=editor, view=view):
            editor.SkinVertexSelList = []
            view.invalidate()
            if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                editor.ModelVertexSelList = []
                Update_Editor_Views(editor)

        setup = quarkx.setupsubset(SS_MODEL, "Options")
        if len(editor.SkinVertexSelList) > 2 or not setup["SingleVertexDrag"]:
            AlignText = "&Align skin vertexes"
        else:
            AlignText = "&Align skin vertex"

        Forcetogrid = qmenu.item("&Force to grid", forcegrid1click,"|Force to grid:\n\nThis will cause any vertex to 'snap' to the nearest location on the Skin-view's grid.|intro.modeleditor.rmbmenus.html#vertexrmbmenu")
        PickBaseVertex = qmenu.item("&Pick Base Vertex", pick_basevertex, "|Pick Base Vertex:\n\n This is used to pick, or remove, the 'Base' (stationary) vertex to align other vertexes to on the Skin-view. It also works in conjunction with the 'Clear Skin Pick list' below it.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.skinview.html#funcsnmenus")
        ChangeBaseVertex = qmenu.item("&Change Base Vertex", change_basevertex, "|Change Base Vertex:\n\n This is used to select another vertex as the 'Base' (stationary) vertex to align other vertexes to on the Skin-view. It also works in conjunction with the 'Clear Skin Pick list' below it.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.skinview.html#funcsnmenus")
        ClearBaseVertex = qmenu.item("&Clear Base Vertex", change_basevertex, "|Clear Base Vertex:\n\n This Clears the 'Base' (stationary) vertex and the 'Pick Skin Vertex' list of all selected vertexes, if any.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.skinview.html#funcsnmenus")
        PickSkinVertex = qmenu.item("&Pick Skin Vertex", pick_skinvertex, "|Pick Skin Vertex:\n\n This is used to pick, or remove, skin vertexes to align them with the 'Base' (stationary) vertex on the Skin-view. A base Vertex must be chosen first. It also works in conjunction with the 'Clear Skin Pick list' below it and the multi or single drag mode button on the Skin-view page.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.skinview.html#funcsnmenus")
        AlignSkinVertexes = qmenu.item(AlignText, alignskinvertexesclick,"|Align skin vertex(s):\n\nOnce a set of vertexes have been 'Picked' on the Skin-view all of those vertexes will be moved to the 'Base' (stationary) vertex (the first one selected) location and aligned for possible multiple vertex movement. It also works in conjunction with the 'Clear Skin Pick list' above it and the multi or single drag mode button on the Skin-view page.|intro.modeleditor.skinview.html#funcsnmenus")
        ClearSkinPicklist = qmenu.item("&Clear Skin Pick list", skinpick_cleared, "|Clear Skin Pick list:\n\nThis Clears the 'Base' (stationary) vertex and the 'Pick Skin Vertex' list of all vertexes and it becomes active when one or more vertexes have been selected.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.skinview.html#funcsnmenus")

        if not MdlOption("SkinGridActive") or editor.skingridstep <= 0:
            Forcetogrid.state = qmenu.disabled

        if len(editor.SkinVertexSelList) == 0:
            ClearSkinPicklist.state = qmenu.disabled

        try:
            if self.ver_index is not None:
                if len(editor.SkinVertexSelList) == 0:
                    AlignSkinVertexes.state = qmenu.disabled
                    PickSkinVertex.state = qmenu.disabled
                    menu = [PickBaseVertex, PickSkinVertex, qmenu.sep, ClearSkinPicklist, qmenu.sep, AlignSkinVertexes, qmenu.sep, Forcetogrid]
                else:
                    if str(self.pos) == str(editor.SkinVertexSelList[0][0]):
                        AlignSkinVertexes.state = qmenu.disabled
                        PickSkinVertex.state = qmenu.disabled
                        menu = [ClearBaseVertex, PickSkinVertex, qmenu.sep, ClearSkinPicklist, qmenu.sep, AlignSkinVertexes, qmenu.sep, Forcetogrid]
                    else:
                        menu = [ChangeBaseVertex, PickSkinVertex, qmenu.sep, ClearSkinPicklist, qmenu.sep, AlignSkinVertexes, qmenu.sep, Forcetogrid]
            else:
                if len(editor.SkinVertexSelList) < 2:
                    AlignSkinVertexes.state = qmenu.disabled
                menu = [ClearSkinPicklist, qmenu.sep, AlignSkinVertexes]
        except:
            if len(editor.SkinVertexSelList) < 2:
                AlignSkinVertexes.state = qmenu.disabled
            menu = [ClearSkinPicklist, qmenu.sep, AlignSkinVertexes]

        return menu


    def optionsmenu(self, editor, view=None): # SkinHandle
        "This is the Skin-view Options menu items."

        # Sync Editor views with Skin-view function.
        def mSYNC_EDwSV(m, self=self, editor=editor, view=view):
            if not MdlOption("SYNC_EDwSV"):
                quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = "1"
                quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = None
                quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = None
                quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = None
                quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
                if editor.layout.views[0].handles == 0:
                    viewhandles = BuildHandles(editor, editor.layout.explorer, editor.layout.views[0])
                else:
                    viewhandles = editor.layout.views[0].handles
                if editor.SkinVertexSelList != []:
                    editor.ModelVertexSelList = []
                    PassSkinSel2Editor(editor)
                    for v in editor.layout.views:
                        if v.info["viewname"] == "skinview":
                            continue
                        v.handles = viewhandles
                    Update_Editor_Views(editor, 1)
                else:
                    editor.ModelVertexSelList = []
                    for v in editor.layout.views:
                        if v.info["viewname"] == "skinview":
                            continue
                        v.handles = viewhandles
                    Update_Editor_Views(editor, 1)
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = None

        # Pass (Skin-view) Vertex Selection To Editors Views function.
        def mPVSTEV(m, self=self, editor=editor, view=view):
            if not MdlOption("PVSTEV"):
                quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = "1"
                quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
                quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = None
                quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = None
                quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = None
                if editor.SkinVertexSelList != []:
                    PassSkinSel2Editor(editor)
                    if editor.layout.views[0].handles == 0:
                        viewhandles = BuildHandles(editor, editor.layout.explorer, editor.layout.views[0])
                    else:
                        viewhandles = editor.layout.views[0].handles
                    for v in editor.layout.views:
                        if v.info["viewname"] == "skinview":
                            continue
                        v.handles = viewhandles
                    Update_Editor_Views(editor, 5)
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = None

        # Clear Selected Faces function.
        def mCSF(m, self=self, editor=editor, view=view):
            if quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] == "1":
                quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
            if quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] == "1":
                quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] = None
            editor.SkinFaceSelList = []
            mdleditor.ModelEditor.finishdrawing(editor, view)

        def TicksViewingMenu(editor):
            # Rectangle Drag Ticks_Method 1
            def mRDT_M1(m):
                editor = mdleditor.mdleditor
                if not MdlOption("RDT_M1"):
                    quarkx.setupsubset(SS_MODEL, "Options")['RDT_M1'] = "1"
                    quarkx.setupsubset(SS_MODEL, "Options")['RDT_M2'] = None
                else:
                    quarkx.setupsubset(SS_MODEL, "Options")['RDT_M1'] = None

            # Rectangle Drag Ticks_Method 2
            def mRDT_M2(m):
                editor = mdleditor.mdleditor
                if not MdlOption("RDT_M2"):
                    quarkx.setupsubset(SS_MODEL, "Options")['RDT_M2'] = "1"
                    quarkx.setupsubset(SS_MODEL, "Options")['RDT_M1'] = None
                else:
                    quarkx.setupsubset(SS_MODEL, "Options")['RDT_M2'] = None

            Xrdt_m1 = qmenu.item("Rectangle drag-method 1", mRDT_M1, "|Rectangle drag-method 1:\n\nThis function will draw the Skin-view mesh vertex 'Ticks' during a rectangle drag with a minimum amount of flickering, but is a slower drawing method.|intro.modeleditor.menu.html#optionsmenu")
            Xrdt_m2 = qmenu.item("Rectangle drag-method 2", mRDT_M2, "|Rectangle drag-method 2:\n\nThis function will draw the Skin-view mesh vertex 'Ticks', using the fastest method, during a rectangle drag, but will cause the greatest amount of flickering.|intro.modeleditor.menu.html#optionsmenu")

            menulist = [Xrdt_m1, Xrdt_m2]

            items = menulist
            Xrdt_m1.state = quarkx.setupsubset(SS_MODEL,"Options").getint("RDT_M1")
            Xrdt_m2.state = quarkx.setupsubset(SS_MODEL,"Options").getint("RDT_M2")

            return menulist

        def TicksViewingClick(m):
            editor = mdleditor.mdleditor
            m.items = TicksViewingMenu(editor)

        # Turn taking Skin-view coors from editors 3D view on or off.
        def mSF3DV(m, self=self, editor=editor, view=view):
            if not MdlOption("SkinFrom3Dview"):
                quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] = "1"
                quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] = None
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] = None

        # When taking Skin-view coors from the Skin-view, turns using its "scale" factor on or off.
        def mUSVS(m, self=self, editor=editor, view=view):
            if not MdlOption("UseSkinViewScale"):
                quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] = "1"
                quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] = None
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] = None
            Xsf3Dv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SkinFrom3Dview")
            Xusvs.state = quarkx.setupsubset(SS_MODEL,"Options").getint("UseSkinViewScale")

        # Turn Model Options function SkinGridVisible on or off.
        def mSGV(m, self=self, editor=editor, view=view):
            if not MdlOption("SkinGridVisible"):
                quarkx.setupsubset(SS_MODEL, "Options")['SkinGridVisible'] = "1"
                if SkinView1 is not None:
                    SkinView1.invalidate()
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['SkinGridVisible'] = None
                if SkinView1 is not None:
                    SkinView1.invalidate()
            Xsf3Dv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SkinFrom3Dview")
            Xusvs.state = quarkx.setupsubset(SS_MODEL,"Options").getint("UseSkinViewScale")

        # Turn Model Options function SkinGridActive on or off.
        def mSGA(m, self=self, editor=editor, view=view):
            if not MdlOption("SkinGridActive"):
                quarkx.setupsubset(SS_MODEL, "Options")['SkinGridActive'] = "1"
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['SkinGridActive'] = None

        # Turn Model Options function SingleSelDragLines on or off.
        def mSSDL(m, self=self, editor=editor, view=view):
            if not MdlOption("SingleSelDragLines"):
                quarkx.setupsubset(SS_MODEL, "Options")['SingleSelDragLines'] = "1"
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['SingleSelDragLines'] = None

        Xsync_edwsv = qmenu.item("&Sync Editor views with Skin-view", mSYNC_EDwSV, "|Sync Editor views with Skin-view:\n\nThis function will turn off other related options and synchronize selected Skin-view mesh vertexes, passing and selecting the coordinated 'Model mesh' vertexes in the Editors views, where they can be used for editing purposes. Any selection changes in the Skin-view will be updated to the Editors views as well.\n\nOnce the selection has been passed, if this function is turned off, the selection will remain in both the Editor and the Skin-view for further use.\n\nThe 'Skin-view' and Editor views selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.skinview.html#funcsnmenus")
        Xpvstev = qmenu.item("&Pass selection to Editor views", mPVSTEV, "|Pass selection to Editor views:\n\nThis function will pass selected Skin-view mesh vertexes and select the coordinated 'Model mesh' vertexes in the Editors views, along with any others currently selected, where they can be used for editing purposes.\n\nOnce the selection has been passed, if this function is turned off, the selection will remain in the Editor for its use there.\n\nThe 'Skin-view' selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.skinview.html#funcsnmenus")
        Xcsf = qmenu.item("&Clear Selected Faces", mCSF, "|Clear Selected Faces:\n\nThis function will clear all faces in the Skin-view that have been drawn as 'Selected' or 'Show' but any related selected vertexes will remain that way for editing purposes.\n\nThe 'Skin-view' selected face, show face and selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.skinview.html#funcsnmenus")
        TicksViewing = qmenu.popup("Draw Ticks During Drag", [], TicksViewingClick, "|Draw Ticks During Drag:\n\nThese functions give various methods for drawing the Models Skin Mesh Vertex Ticks while doing a drag.\n\nPress the 'F1' key again or click the button below for further details.", "intro.modeleditor.skinview.html#funcsnmenus")
        Xsf3Dv = qmenu.item("Skin From 3D view", mSF3DV, "|Skin From 3D view:\n\nThis turns the function on or off to take co-ordnances for the 'Skin-view' from the editors 3D view when new objects are created using the 'Quick Object Maker'\n\nIt will place that object on the skin exactly the same way you see it in the 3D view when the object is created. This same process applies to selected faces in the editor.\n\nBecause the 3D view uses its own 'scale' factor, activating this function will also turn off the 'Use Skin-view scale' function.|intro.modeleditor.skinview.html#funcsnmenus")
        Xusvs = qmenu.item("Use Skin-view scale", mUSVS, "|Use Skin-view scale:\n\nThis turns the function on or off for applying of the views 'zoom' or 'scale' factor when taking co-ordnances from the 'Skin-view' and which works in reverse.\n\nMeaning, when this option is checked, if the Skin-view is zoomed out (skin looks small) it will skin new triangles with fewer repetitions (skin looks larger) of that image and visa-versa. Because the 3D view uses its own 'scale' factor, activating this function will also turn off the 'Skin From 3D view' function.|intro.modeleditor.skinview.html#funcsnmenus")
        Xsgv = qmenu.item("Skin Grid Visible", mSGV, "|Skin Grid Visible:\n\nThis function gives quick access to the Model Options setting to turn the Skin-view grid on or off so that it is not visible, but it is still active for all functions that use it, such as 'Snap to grid'.|intro.modeleditor.skinview.html#funcsnmenus")
        Xsga = qmenu.item("Skin Grid Active", mSGA, "|Skin Grid Active:\n\nThis function gives quick access to the Model Options setting to make the Skin-view grid Active or Inactive making it available or unavailable for all functions that use it, such as 'Snap to grid', even though it will still be displayed in the Skin-view.|intro.modeleditor.skinview.html#funcsnmenus")
        Xssdl = qmenu.item("Single Sel Drag Lines", mSSDL, "|Single Sel Drag Lines:\n\nThis function stops the multiple selection drag lines of the 'Linear Handle' from being drawn in the Skin-view to speed up the Skin-view selection and handle creation.|intro.modeleditor.skinview.html#funcsnmenus")

        opsmenulist = [Xsync_edwsv, Xpvstev, Xcsf, qmenu.sep, Xsf3Dv, Xusvs, Xsgv, Xsga, Xssdl, qmenu.sep, TicksViewing]

        items = opsmenulist
        Xsync_edwsv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SYNC_EDwSV")
        Xpvstev.state = quarkx.setupsubset(SS_MODEL,"Options").getint("PVSTEV")
        Xsf3Dv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SkinFrom3Dview")
        Xusvs.state = quarkx.setupsubset(SS_MODEL,"Options").getint("UseSkinViewScale")
        Xsgv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SkinGridVisible")
        Xsga.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SkinGridActive")
        Xssdl.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SingleSelDragLines")

        return opsmenulist


    def draw(self, view, cv, draghandle=None): # SkinHandle
        editor = self.editor
        from qbaseeditor import flagsmouse
        # To stop all drawing, causing slowdown, during a Linear, pan and zoom drag.
        if flagsmouse == 2056 or flagsmouse == 1032 or flagsmouse == 1040 or flagsmouse == 1056:
            return # Stops duplicated handle drawing at the end of a drag.
        texWidth = self.texWidth
        texHeight = self.texHeight
        triangle = self.triangle

        if self.pos.x > (self.texWidth * .5):
            Xstart = int((self.pos.x / self.texWidth) -.5)
            Xstartpos = -self.texWidth + self.pos.x - (self.texWidth * Xstart)
        elif self.pos.x < (-self.texWidth * .5):
            Xstart = int((self.pos.x / self.texWidth) +.5)
            Xstartpos = self.texWidth + self.pos.x + (self.texWidth * -Xstart)
        else:
            Xstartpos = self.pos.x

        if -self.pos.y > (self.texHeight * .5):
            Ystart = int((-self.pos.y / self.texHeight) -.5)
            Ystartpos = -self.texHeight + -self.pos.y - (self.texHeight * Ystart)
        elif -self.pos.y < (-self.texHeight * .5):
            Ystart = int((-self.pos.y / self.texHeight) +.5)
            Ystartpos = self.texHeight + -self.pos.y + (self.texHeight * -Ystart)
        else:
            Ystartpos = -self.pos.y

        ### shows the true vertex position in relation to each tile section of the texture.
        if MapOption("HandleHints", SS_MODEL):
            self.hint = "      Skin tri \\ vertex " + quarkx.ftos(self.tri_index) + " \\ " + quarkx.ftos((self.tri_index*3) + self.ver_index)

        p = view.proj(self.pos)
        if p.visible:
            cv.pencolor = skinviewmesh
            pv2 = p.tuple
            if flagsmouse == 16384:
                if editor.SkinVertexSelList == []:
                    for vertex in triangle:
                        fixedvertex = quarkx.vect(vertex[1]-int(texWidth*.5), vertex[2]-int(texHeight*.5), 0)
                        fixedX, fixedY,fixedZ = view.proj(fixedvertex).tuple
                        cv.line(int(pv2[0]), int(pv2[1]), int(fixedX), int(fixedY))

                    cv.reset()
                    if MdlOption("Ticks") == "1":
                        cv.brushcolor = WHITE
                        cv.ellipse(int(p.x)-2, int(p.y)-2, int(p.x)+2, int(p.y)+2)
                    else:
                        cv.ellipse(int(p.x)-1, int(p.y)-1, int(p.x)+1, int(p.y)+1)

                else:
                    item = editor.SkinVertexSelList[0]
                    if self.tri_index == item[2] and self.ver_index == item[3]:
                        selsize = int(quarkx.setupsubset(SS_MODEL,"Building")['SkinLinearSelected'][0])
                        cv.brushcolor = skinviewdraglines
                        cv.rectangle(int(p.x)-selsize, int(p.y)-selsize, int(p.x)+selsize, int(p.y)+selsize)
                        item[0] = item[1].pos = self.pos
                        item[1] = self


 #  For setting stuff up at the beginning of a handle drag.
 #
 #   def start_drag(self, view, x, y):


    def drag(self, v1, v2, flags, view): # SkinHandle
        editor = self.editor
        from qbaseeditor import flagsmouse
        # To stop all drawing, causing slowdown, during a Linear, pan and zoom drag.
        if flagsmouse == 1032 and (editor.dragobject.handle is not self): return
        if flagsmouse == 1040 or flagsmouse == 1056: return # Stops duplicated handle drawing at the end of a drag.
        texWidth = self.texWidth
        texHeight = self.texHeight
        p0 = view.proj(self.pos)
        if not p0.visible: return
        if flags&MB_CTRL and quarkx.setupsubset(SS_MODEL, "Options")['SkinGridActive'] is not None:
            v2 = alignskintogrid(v2, 0)
        delta = v2-v1
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, 0)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, 0)
        ### just gives how far you have moved the mouse.
     #   self.draghint = "moving Skin-view vertex: " + ftoss(delta.x) + ", " + ftoss(delta.y)
        ### shows how far from the center of the skin texture the vertex is, its true position.
     #   self.draghint = "x, y pos from ctr: " + ftoss(self.pos.x+delta.x) + ", " + ftoss(-self.pos.y-delta.y)

        if self.pos.x > (self.texWidth * .5):
            Xstart = int((self.pos.x / self.texWidth) -.5)
            Xstartpos = -self.texWidth + self.pos.x - (self.texWidth * Xstart)
        elif self.pos.x < (-self.texWidth * .5):
            Xstart = int((self.pos.x / self.texWidth) +.5)
            Xstartpos = self.texWidth + self.pos.x + (self.texWidth * -Xstart)
        else:
            Xstartpos = self.pos.x

        if (self.pos.x+delta.x) > (self.texWidth * .5):
            Xhowmany = int(((self.pos.x+delta.x) / self.texWidth) -.5)
            Xtogo = -self.texWidth + (self.pos.x+delta.x) - (self.texWidth * Xhowmany)

        elif (self.pos.x+delta.x) < (-self.texWidth * .5):
            Xhowmany = int(((self.pos.x+delta.x) / self.texWidth) +.5)
            Xtogo = self.texWidth + (self.pos.x+delta.x) + (self.texWidth * -Xhowmany)
        else:
            Xtogo = (self.pos.x+delta.x)

        if -self.pos.y > (self.texHeight * .5):
            Ystart = int((-self.pos.y / self.texHeight) -.5)
            Ystartpos = -self.texHeight + -self.pos.y - (self.texHeight * Ystart)
        elif -self.pos.y < (-self.texHeight * .5):
            Ystart = int((-self.pos.y / self.texHeight) +.5)
            Ystartpos = self.texHeight + -self.pos.y + (self.texHeight * -Ystart)
        else:
            Ystartpos = -self.pos.y

        if (-self.pos.y-delta.y) > (self.texHeight * .5):
            Ystart = int(((-self.pos.y-delta.y) / self.texHeight) -.5)
            Ytogo = -self.texHeight + (-self.pos.y-delta.y) - (self.texHeight * Ystart)
        elif (-self.pos.y-delta.y) < (-self.texHeight * .5):
            Ystart = int(((-self.pos.y-delta.y) / self.texHeight) +.5)
            Ytogo = self.texHeight + (-self.pos.y-delta.y) + (self.texHeight * -Ystart)
        else:
            Ytogo = (-self.pos.y-delta.y)

        ### shows the true vertex position as you move it and in relation to each tile section of the texture.
        if self.comp.currentskin is not None:
            self.draghint = "was " + ftoss(Xstartpos) + ", " + ftoss(Ystartpos) + " now " + ftoss(int(Xtogo)) + ", " + ftoss(int(Ytogo))
        else:
            self.draghint = "was " + ftoss(int(view.proj(v1).tuple[0])) + ", " + ftoss(int(view.proj(v1).tuple[1])) + " now " + ftoss(view.proj(v2).tuple[0]) + ", " + ftoss(view.proj(v2).tuple[1])

        new = self.comp.copy()
        if delta or (flags&MB_REDIMAGE):
            tris = new.triangles ### These are all the triangle faces of the model mesh.

            ### Code below draws the Skin-view green guide lines for the triangle face being dragged.
        try:
            if flags == 2056:
                pass
            else:
                view.repaint()
                cv = view.canvas()
                cv.pencolor = skinviewdraglines
         #       editor.finishdrawing(view) # This could be used if we want to add something to the Skin-view drawing in the future.
      ### To draw the dragging 'guide' lines.
            pv2 = view.proj(v2)
            oldtri = tris[self.tri_index]
            oldvert = oldtri[self.ver_index]
            newvert = (int(oldvert[0]), int(oldvert[1])+int(delta.x), int(oldvert[2])+int(delta.y))
            if flags == 2056:
                if (self.ver_index == 0):
                    newtri = (newvert, oldtri[1], oldtri[2])
                elif (self.ver_index == 1):
                    newtri = (oldtri[0], newvert, oldtri[2])
                elif (self.ver_index == 2):
                    newtri = (oldtri[0], oldtri[1], newvert)
            else:
                if (self.ver_index == 0):
                    newtri = (newvert, oldtri[1], oldtri[2])
                    facev3 = quarkx.vect(oldtri[1][1]-int(texWidth*.5), oldtri[1][2]-int(texHeight*.5), 0)
                    facev4 = quarkx.vect(oldtri[2][1]-int(texWidth*.5), oldtri[2][2]-int(texHeight*.5), 0)
                    oldvect3X, oldvect3Y,oldvect3Z = view.proj(facev3).tuple
                    oldvect4X, oldvect4Y,oldvect4Z = view.proj(facev4).tuple
                    cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(oldvect3X), int(oldvect3Y))
                    cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(oldvect4X), int(oldvect4Y))
                elif (self.ver_index == 1):
                    newtri = (oldtri[0], newvert, oldtri[2])
                    facev3 = quarkx.vect(oldtri[0][1]-int(texWidth*.5), oldtri[0][2]-int(texHeight*.5), 0)
                    facev4 = quarkx.vect(oldtri[2][1]-int(texWidth*.5), oldtri[2][2]-int(texHeight*.5), 0)
                    oldvect3X, oldvect3Y,oldvect3Z = view.proj(facev3).tuple
                    oldvect4X, oldvect4Y,oldvect4Z = view.proj(facev4).tuple
                    cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(oldvect3X), int(oldvect3Y))
                    cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(oldvect4X), int(oldvect4Y))
                elif (self.ver_index == 2):
                    newtri = (oldtri[0], oldtri[1], newvert)
                    facev3 = quarkx.vect(oldtri[0][1]-int(texWidth*.5), oldtri[0][2]-int(texHeight*.5), 0)
                    facev4 = quarkx.vect(oldtri[1][1]-int(texWidth*.5), oldtri[1][2]-int(texHeight*.5), 0)
                    oldvect3X, oldvect3Y,oldvect3Z = view.proj(facev3).tuple
                    oldvect4X, oldvect4Y,oldvect4Z = view.proj(facev4).tuple
                    cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(oldvect3X), int(oldvect3Y))
                    cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(oldvect4X), int(oldvect4Y))

            tris[self.tri_index] = newtri
        except:
            new.triangles = self.comp

    ####### new code for Skin-view mesh to drag using common handles option. ########
        setup = quarkx.setupsubset(SS_MODEL, "Options")
        if not setup["SingleVertexDrag"]:
            component = editor.Root.currentcomponent
            if component is not None:
                if component.name.endswith(":mc"):
                    handlevertex = self.tri_index
                    dragtris = find2DTriangles(self.comp, self.tri_index, self.ver_index) # This is the funciton that gets the common vertexes in mdlutils.py.

                    newvert = (int(oldvert[0]), int(oldvert[1])+int(delta.x), int(oldvert[2])+int(delta.y))
                    for index,tri in dragtris.iteritems():
                        vtx_index = 0
                        for vtx in tri:
                            if str(vtx) == str(self.comp.triangles[self.tri_index][self.ver_index]):
                                drag_vtx_index = vtx_index
                            else:
                                vtx_index = vtx_index + 1
                                fixedvertex = quarkx.vect(vtx[1]-int(texWidth*.5), vtx[2]-int(texHeight*.5), 0)
                                fixedX, fixedY,fixedZ = view.proj(fixedvertex).tuple
                                if flags == 2056:
                                    pass
                                else:
                                    cv.line(int(pv2.tuple[0]), int(pv2.tuple[1]), int(fixedX), int(fixedY))
                        if drag_vtx_index == 0:
                            newtriangle = (newvert, tri[1], tri[2])
                        elif drag_vtx_index == 1:
                            newtriangle = (tri[0], newvert, tri[2])
                        else:
                            newtriangle = (tri[0], tri[1], newvert)
                        tris[index] = newtriangle
        new.triangles = tris
        if (flags == 2056 or flags == 2060) and len(editor.SkinVertexSelList) > 1:
            new_pos = self.pos + delta
            newvert = quarkx.vect((int(new_pos.x), int(new_pos.y), 0))
            if quarkx.setupsubset(SS_MODEL, "Options")['SingleVertexDrag'] == "1":
                for i in range(len(editor.SkinVertexSelList)):
                    if editor.SkinVertexSelList[i][2] == self.tri_index and editor.SkinVertexSelList[i][3] == self.ver_index:
                        editor.SkinVertexSelList[i][0] = newvert
                        editor.SkinVertexSelList[i][1].pos = newvert
                        break
            else:
                for i in range(len(editor.SkinVertexSelList)):
                    if str(editor.SkinVertexSelList[i][0]) == str(self.pos):
                        editor.SkinVertexSelList[i][0] = newvert
                        editor.SkinVertexSelList[i][1].pos = newvert
        return [self.comp], [new]


#    def ok(self, editor, undo, old, new):
#        editor.undo.ok(editor.Root, self.undomsg)



def buildskinvertices(editor, view, layout, component, skindrawobject):
    "builds a list of handles to display on the skinview"
    global SkinView1
    from qbaseeditor import flagsmouse

    ### This sets the location of the skin texture in the Skin-view when it is first opened
    ### and I believe keeps it centered if the view is stretched to a different size.
    center =  quarkx.vect(view.clientarea[0]/2, view.clientarea[1]/2, 0)
    origin = center
    viewscale = .5

    #DECKER - begin
    #FIXME - Put a check for an option-switch here, so people can choose which they want (fixed-zoom/scroll, or reseting-zoom/scroll)
    oldx, oldy, doautozoom = center.tuple
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

    if doautozoom:  ### This sets the view.info scale for the Skin-view when first opened, see ###Decker below.
        oldscale = viewscale
    #DECKER - end

    # Line below to stop doautozoom.
    if flagsmouse == 1056 or (flagsmouse == 16384 and view.info is None):
     #   view.viewmode = "wire" # Don't know why, but making this "tex" causes it to mess up...bad!
        view.info = {"type": "2D",
                     "matrix": matrix_rot_z(pi2),
                     "bbox": quarkx.boundingboxof(map(lambda h: h.pos, view.handles)),
                     "scale": oldscale, ###DECKER This method leaves the scale unchanged from the last zoom (which is what sets the "scale" factor).
                  #   "scale": viewscale, ###DECKER This method resets the texture size of a component to the size of the Skin-view
                                          ### each time that component is re-selected, but not while any item within it is selected.
                     "custom": singleskinzoom,
                     "origin": origin,
                     "noclick": None,
                     "center": quarkx.vect(0,0,0),
                     "viewname": "skinview",
                     "mousemode": None
                     }
    SkinView1 = view

    if flagsmouse == 544 or flagsmouse == 552:
        return
    ### begin code from maphandles def viewsinglebezier
    if skindrawobject is not None:
        view.viewmode = "tex" # Don't know why, but if model HAS skin, making this "wire" causes black lines on zooms.
        try:
            tex = skindrawobject
            texWidth, texHeight = tex["Size"]
            viewWidth,viewHeight = view.clientarea
            ### Calculates the "scale" factor of the Skin-view
            ### and sets the scale based on the largest size (Height or Width) of the texture
            ### to fill the Skin-view. The lower the scale factor, the further away the image is.
            Width = viewWidth/texWidth
            Height = viewHeight/texHeight
            if Width < Height:
                viewscale = Width
            else:
                viewscale = Height
        except:
            pass
        else:
            def draw1(view, finish=layout.editor.finishdrawing, texWidth=texWidth, texHeight=texHeight):
                ### This draws the lines from the center location point.
                try:
                    view.drawgrid(quarkx.vect(texWidth*view.info["scale"],0,0), quarkx.vect(0,texHeight*view.info["scale"],0), MAROON, DG_LINES, 0, quarkx.vect(-int(texWidth*.5),-int(texHeight*.5),0))
                    finish(view)
                except:
                    return None

            view.ondraw = draw1
            view.onmouse = layout.editor.mousemap
               ### This sets the texture, its location and scale size in the Skin-view.
            view.background = quarkx.vect(-int(texWidth*.5),-int(texHeight*.5),0), 1.0, 0, 1
            view.backgroundimage = tex,
    else:
           ### This handles models without any skin(s).
        texWidth,texHeight = view.clientarea
        viewscale = .5
        view.viewmode = "wire" # Don't know why, but if model has NO skin, making this "tex" causes it to mess up...bad!
    ### end code from maphandles def viewsinglebezier


    def drawsingleskin(view, layout=layout, skindrawobject=skindrawobject, component=component, editor=editor):

      ### Special handling if model has no skins.
      ### First to draw its lines.
      ### Second to keep the background yellow to avoid color flickering.
        if skindrawobject is None:
            editor.finishdrawing(view)
        else:
            view.color = BLACK

    if component is None and editor.Root.name.endswith(":mr"):
        for item in editor.Root.dictitems:
            if item.endswith(":mc"):
                component = editor.Root.dictitems[item]
                org = component.originst
    else:
        try:
            org = component.originst
        except:
            if len(component.dictitems["Frames:fg"].subitems[0].vertices) == 0:
                org = quarkx.vect(0,0,0)

    n = quarkx.vect(1,1,1)
    v = orthogonalvect(n, view)
    view.flags = view.flags &~ (MV_HSCROLLBAR | MV_VSCROLLBAR)

    if skindrawobject is None:
        editor.setupview(view, drawsingleskin, 0)

    # Section below does the "Auto Scaling".
    tris = component.triangles
    if skindrawobject is not None and MdlOption("AutoScale_SkinHandles") and component.dictspec['show'] == '\x01':
        old_texWidth, old_texHeight = component.dictspec['skinsize']
        texWidth_scale = texWidth / old_texWidth
        texHeight_scale = texHeight / old_texHeight
        component['skinsize'] = skindrawobject["Size"]
        newtris = tris
        for i in range(len(tris)): # i is the tri_index based on its position in the 'Tris' frame list.
            tri = tris[i]
            for j in range(len(tri)): # j is the vert_index, either 0, 1 or 2 vertex of the triangle.
                                        # To calculate a triangle's vert_index number = (i * 3) + j
                u = int(round(tri[j][1] * texWidth_scale))
                v = int(round(tri[j][2] * texHeight_scale))
                if j == 0:
                    vtx0 = (tri[j][0], u, v)
                elif j == 1:
                    vtx1 = (tri[j][0], u, v)
                else:
                    vtx2 = (tri[j][0], u, v)
            tri = (vtx0, vtx1, vtx2)
            newtris[i:i+1] = [tri]
        component.triangles = tris = newtris

    h = []
    handlepos = []
    for i in range(len(tris)): # i is the tri_index based on its position in the 'Tris' frame list.
        tri = tris[i]
        for j in range(len(tri)): # j is the vert_index, either 0, 1 or 2 vertex of the triangle.
                                  # To calculate a triangle's vert_index number = (i * 3) + j
            vtx = tri[j]
            ### This sets the Skin-view model mesh vertexes and line drawing location(s).
            h.append(SkinHandle(quarkx.vect(vtx[1]-int(texWidth*.5), vtx[2]-int(texHeight*.5), 0), i, j, component, texWidth, texHeight, tri))
            handlepos.append(h[i*3+j].pos)
    editor.SkinViewList['handlepos'][component.name] = handlepos

    if len(editor.SkinVertexSelList) >= 2:
        view.handles = h
        vtxlist = []
        for vtx in editor.SkinVertexSelList:
            vtxlist = vtxlist + [vtx[0]]
        box = quarkx.boundingboxof(vtxlist)
        if box is None:
            return
        elif box is not None and len(box) != 2:
            editor.SkinVertexSelList = []
        else:
            i = len(view.handles)-1
            while 1:
                if i == -1 or isinstance(view.handles[i], SkinHandle):
                    break
                view.handles.remove(view.handles[i])
                i = i - 1
            h = h + ModelEditorLinHandlesManager(MapColor("LinearHandleCircle", SS_MODEL), box, vtxlist, view).BuildHandles()

    view.handles = qhandles.FilterHandles(h, SS_MODEL)

    singleskinzoom(view)
    return 1



def singleskinzoom(view):
    sc = view.screencenter
    try:
        view.setprojmode("2D", view.info["matrix"]*view.info["scale"], 0)
    except:
        pass
    view.screencenter = sc


#
# Functions to build common lists of handles.
#
def BuildCommonHandles(editor, explorer, option=1):
    "Build a list of handles to display in all of the editor views."
    "option=1: Clears all exising handles in the 'h' list and rebuilds it for specific handle type."
    "option=2: Does NOT clear the list but adds to it to allow a combination of view handles to use."

    # Just in case the 'Skeleton:bg' gets deleted we need to create a new one.
    if editor.Root.dictitems.has_key("Skeleton:bg"):
        pass
    else:
        clearbones(editor, "deleted Skeleton group replaced")

    th = []

    # Just in case the 'Misc:mg' gets deleted we need to create a new one.
    if editor.Root.dictitems.has_key("Misc:mg"):
        pass
    else:
        clearMiscGroup(editor, "deleted Misc group replaced")

    for item in editor.Root.dictitems["Misc:mg"].subitems:
        if item.type == ":tag":
            tag_group_name = item.name.split("_")[0]
            for item2 in editor.Root.dictitems:
                tag_frame_index = 0
                if editor.Root.dictitems[item2].type == ":mc" and editor.Root.dictitems[item2].name.startswith(tag_group_name + "_") and editor.Root.dictitems[item2].dictspec.has_key("Tags"):
                    item_currentframe_name = editor.Root.dictitems[item2].currentframe.name
                    for frame in editor.Root.dictitems[item2].dictitems['Frames:fg'].subitems:
                        if frame.name == item_currentframe_name:
                            break
                        tag_frame_index = tag_frame_index + 1
                    break

            if len(item.subitems)-1 >= tag_frame_index:
                tag_frame = item.subitems[tag_frame_index]
                th = th + mdlentities.CallManager("handlesopt", tag_frame, editor)
            else:
                tag_frame = item.subitems[0]
                th = th + mdlentities.CallManager("handlesopt", tag_frame, editor)

    bh = th
    if quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['AnimationCFGActive'] == "1":
        if len(editor.ModelFaceSelList) != 0:
            MakeEditorFaceObject(editor)
        return bh

    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1" and quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is None:

        bones = editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone') # Get all bones.
        if len(bones) != 0:
            # Checks if something has changed the frame selection.
            import operator
            try:
                currentindex = operator.indexOf(editor.Root.currentcomponent.dictitems['Frames:fg'].subitems, editor.Root.currentcomponent.currentframe)
                if currentindex != editor.bone_frame:
                    editor.bone_frame = currentindex
            except:
                pass

        for bone in bones:
            bh = bh + mdlentities.CallManager("handlesopt", bone, editor)
        bh.reverse() # Stops connecting bone lines from drawing over rotation handles.
        for item in explorer.sellist:
            if item.type == ':p' or item.type == ':f':
                if item.type == ':f':
                    item = item.parent
                bh = bh + mdlentities.CallManager("handles", item, editor)
                break

    h = bh
    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
        #
        # Linear Handles and Selected Face Object Build call section.
        #
        if len(editor.ModelFaceSelList) != 0 and len(editor.layout.explorer.sellist) != 0 and editor.layout.explorer.sellist[0].type == ":mf":
            h = []
            list = MakeEditorFaceObject(editor)
        else:
            h = []
            for item in explorer.sellist:
                if item.type == ':g' or item.type == ':d':
                    h = h + mdlentities.CallManager("handles", item, editor)
            return h
        box = quarkx.boundingboxof(list)
        if box is None:
            h = []
        else:
            h = ModelEditorLinHandlesManager(MapColor("LinearHandleCircle", SS_MODEL), box, list).BuildHandles()
    else:
        if editor.Root.currentcomponent.dictspec['show'] == "\x00": # Component is hidden.
            for item in explorer.sellist:
                if item.type == ':g' or item.type == ':d':
                    h = h + mdlentities.CallManager("handles", item, editor)
            return h
        #
        # Call the Entity Manager in mdlentities.py to build the Vertex handles.
        #
        if len(editor.ModelFaceSelList) != 0:
            MakeEditorFaceObject(editor)
        if quarkx.setupsubset(SS_MODEL, "Options")['BHandles_Only'] is None:
            for item in explorer.sellist:
                if item.type == ':mf':
                    compairframe = item
                    break
            for item in explorer.sellist: # Makes and adds the vertex handles before any bone handles.
                if item.type == ':mf':
                    if len(editor.ModelVertexSelList) >= 2:
                        option = 2
                        vtxlist = []
                        vh = mdlentities.CallManager("handlesopt", compairframe, editor)
                    elif quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is not None:
                        h = mdlentities.CallManager("handlesopt", compairframe, editor)
                    else:
                        h = mdlentities.CallManager("handlesopt", compairframe, editor) + h
                    break
            if option == 2: # Makes the vertex linear handle, if any, and adds before any bone handles.
                try: # Need to do it in a try statement in case the component's current frame has no vertexes to avoid an error.
                    editor.ModelVertexSelListPos = []
                    editor.ModelVertexSelListBBox = None
                    vertices = editor.Root.currentcomponent.currentframe.vertices
                    for vtxpos in editor.ModelVertexSelList:
                        editor.ModelVertexSelListPos = editor.ModelVertexSelListPos + [vertices[vtxpos]]
                    editor.ModelVertexSelListBbox = quarkx.boundingboxof(editor.ModelVertexSelListPos)
                    box = editor.ModelVertexSelListBbox
                    if len(box) != 2:
                        editor.ModelVertexSelList = []
                    else:
                        h = vh + ModelEditorLinHandlesManager(MapColor("LinearHandleCircle", SS_MODEL), box, vtxlist).BuildHandles() + bh
                except:
                    pass

    for item in explorer.sellist:
        if item.type == ':g' or item.type == ':d':
            h = h + mdlentities.CallManager("handles", item, editor)

    try:
        return qhandles.FilterHandles(h, SS_MODEL)
    except:
        pass



def BuildHandles(editor, explorer, view, option=1):
    "Builds a list of handles to display in one specific map view, or more if calling for each one."
    "This function is called from quarkpy\mdleditor.py, class ModelEditor,"
    "def buildhandles function and returns the list of handles to that function."
    "option=1: Clears all exising handles in the 'h' list and rebuilds it for specific handle type."
    "option=2: Does NOT clear the list but adds to it to allow a combination of view handles to use."

    #
    # The 3D view "eyes".
    #
    if quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] is not None:
        eye_handles = []
        if view.info["viewname"] == "editors3Dview" or view.info["viewname"] == "3Dwindow":
            pass
        else:
            for v in editor.layout.views:
                if (v is not view) and (v.info["type"] == "3D"):
                    handle = qhandles.EyePosition(view, v)
                    handle.hint = "camera for the Editor 3D view"
                    eye_handles.append(handle)
                    handle = MdlEyeDirection(view, v)
                    handle.hint = "Editor 3D view camera direction"
                    eye_handles.append(handle)

    # Just in case the 'Skeleton:bg' gets deleted we need to create a new one.
    if editor.Root.dictitems.has_key("Skeleton:bg"):
        pass
    else:
        clearbones(editor, "deleted Skeleton group replaced")

    th = []

    # Just in case the 'Misc:mg' gets deleted we need to create a new one.
    if editor.Root.dictitems.has_key("Misc:mg"):
        pass
    else:
        clearMiscGroup(editor, "deleted Misc group replaced")

    for item in editor.Root.dictitems["Misc:mg"].subitems:
        if item.type == ":tag":
            tag_group_name = item.name.split("_")[0]
            for item2 in editor.Root.dictitems:
                tag_frame_index = 0
                if editor.Root.dictitems[item2].type == ":mc" and editor.Root.dictitems[item2].name.startswith(tag_group_name + "_") and editor.Root.dictitems[item2].dictspec.has_key("Tags"):
                    item_currentframe_name = editor.Root.dictitems[item2].currentframe.name
                    for frame in editor.Root.dictitems[item2].dictitems['Frames:fg'].subitems:
                        if frame.name == item_currentframe_name:
                            break
                        tag_frame_index = tag_frame_index + 1
                    break

            if len(item.subitems)-1 >= tag_frame_index:
                tag_frame = item.subitems[tag_frame_index]
                th = th + mdlentities.CallManager("handlesopt", tag_frame, editor)
            else:
                tag_frame = item.subitems[0]
                th = th + mdlentities.CallManager("handlesopt", tag_frame, editor)

    bh = th
    if quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['AnimationCFGActive'] == "1":
        view.handles = []
        if len(editor.ModelFaceSelList) != 0:
            MakeEditorFaceObject(editor)
        for item in explorer.sellist:
            if item.type == ':g' or item.type == ':d':
                bh = bh + mdlentities.CallManager("handles", item, editor, view)
        return bh

    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
        if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1" and quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is None:

            bones = editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone') # Get all bones.
            if len(bones) != 0:
                # Checks if something has changed the frame selection.
                import operator
                try:
                    currentindex = operator.indexOf(editor.Root.currentcomponent.dictitems['Frames:fg'].subitems, editor.Root.currentcomponent.currentframe)
                    if currentindex != editor.bone_frame:
                        editor.bone_frame = currentindex
                except:
                    pass

            for bone in bones:
                bh = bh + mdlentities.CallManager("handlesopt", bone, editor)
            bh.reverse() # Stops connecting bone lines from drawing over rotation handles.
            for item in explorer.sellist:
                if item.type == ':p' or item.type == ':f':
                    if item.type == ':f':
                        item = item.parent
                    bh = bh + mdlentities.CallManager("handles", item, editor)
                    break
    h = bh
    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
        #
        # Linear Handles and Selected Face Object Build call section.
        #
        if len(editor.ModelFaceSelList) != 0 and len(editor.layout.explorer.sellist) != 0 and editor.layout.explorer.sellist[0].type == ":mf":
            h = []
            list = MakeEditorFaceObject(editor)
        else:
            h = []
            if quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] is not None:
                h = h + eye_handles
            for item in explorer.sellist:
                if item.type == ':g' or item.type == ':d':
                    h = h + mdlentities.CallManager("handles", item, editor, view)
            return h
        box = quarkx.boundingboxof(list)
        if box is None:
            h = []
        else:
            h = ModelEditorLinHandlesManager(MapColor("LinearHandleCircle", SS_MODEL), box, list, view).BuildHandles()
    else:
        if editor.Root.currentcomponent.dictspec['show'] == "\x00": # Component is hidden.
            if quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] is not None:
                h = h + eye_handles
            for item in explorer.sellist:
                if item.type == ':g' or item.type == ':d':
                    h = h + mdlentities.CallManager("handles", item, editor, view)
            return h
        #
        # Call the Entity Manager in mdlentities.py to build the Vertex handles.
        #
        if len(editor.ModelFaceSelList) != 0:
            MakeEditorFaceObject(editor)
        if quarkx.setupsubset(SS_MODEL, "Options")['BHandles_Only'] is None:
            for item in explorer.sellist:
                if item.type == ':mf':
                    compairframe = item
                    break
            for item in explorer.sellist: # Makes and adds the vertex handles before any bone handles.
                if item.type == ':mf':
                    if len(editor.ModelVertexSelList) >= 2:
                        option = 2
                        vtxlist = []
                        vh = mdlentities.CallManager("handlesopt", compairframe, editor)
                    elif quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is not None:
                        h = mdlentities.CallManager("handlesopt", compairframe, editor)
                    else:
                        h = mdlentities.CallManager("handlesopt", compairframe, editor) + h
                    break
            if option == 2: # Makes the vertex linear handle, if any, and adds before any bone handles.
                try: # Need to do it in a try statement in case the component's current frame has no vertexes to avoid an error.
                    editor.ModelVertexSelListPos = []
                    editor.ModelVertexSelListBBox = None
                    vertices = editor.Root.currentcomponent.currentframe.vertices
                    for vtxpos in editor.ModelVertexSelList:
                        editor.ModelVertexSelListPos = editor.ModelVertexSelListPos + [vertices[vtxpos]]
                    editor.ModelVertexSelListBbox = quarkx.boundingboxof(editor.ModelVertexSelListPos)
                    box = editor.ModelVertexSelListBbox
                    if len(box) != 2:
                        editor.ModelVertexSelList = []
                    else:
                        h = vh + ModelEditorLinHandlesManager(MapColor("LinearHandleCircle", SS_MODEL), box, vtxlist, view).BuildHandles() + bh
                except:
                    pass
    try:
        if quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] is not None:
            h = h + eye_handles
    except:
        pass

    for item in explorer.sellist:
        if item.type == ':g' or item.type == ':d':
            h = h + mdlentities.CallManager("handles", item, editor, view)

    try:
        return qhandles.FilterHandles(h, SS_MODEL)
    except:
        pass


#
# Drag Objects
#

class RectSelDragObject(qhandles.RectangleDragObject):
    "A red rectangle that selects the model vertexes it touches or inside it."

    def rectanglesel(self, editor, x,y, rectangle, view):
        import mdleditor
        comp = editor.Root.currentcomponent
        cursordragstartpos = (self.x0, self.y0)
        cursordragendpos = (x, y)
        ### To stop selection or selection change if nothing, or something
        ### other then a components "frame(s)" is selected in the tree-view.
        ### And to retain existing selected items, if any, in the ModelVertexSelList.
        if view.info["viewname"] != "skinview":
            if len(editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone')) != 0 and len(view.handles) == 0:
                view.handles = BuildHandles(editor, editor.layout.explorer, view)
            if len(editor.layout.explorer.sellist) == 0:
                mdleditor.setsingleframefillcolor(editor, view)
                view.repaint()
                plugins.mdlgridscale.gridfinishdrawing(editor, view)
                if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
                    cv = view.canvas()
                    for h in view.handles:
                        h.draw(view, cv, h)
                return
            else:
                if editor.layout.explorer.sellist[0].type == ":mf":
                    pass
                elif quarkx.setupsubset(3, "Options")['VertexPaintMode'] is not None and editor.layout.explorer.sellist[0].type == ":bone" and editor.layout.explorer.sellist[len(editor.layout.explorer.sellist)-1].type == ":mf":
                    pass
                elif (len(editor.layout.explorer.sellist) == 2) and (editor.layout.explorer.sellist[0].type == ":bg" or editor.layout.explorer.sellist[0].type == ":bone") and (editor.layout.explorer.sellist[1].type == ":mf"):
                    pass
                else:
                    mdleditor.setsingleframefillcolor(editor, view)
                    view.repaint()
                    plugins.mdlgridscale.gridfinishdrawing(editor, view)
                    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
                        cv = view.canvas()
                        for h in view.handles:
                            h.draw(view, cv, h)
                    return

        ### This is the selection Grid section for the Skin-view's view.
        if view.info["viewname"] == "skinview":
            sellist = []
            tris = comp.triangles
            try:
                tex = comp.currentskin
                texWidth,texHeight = tex["Size"]
            except:
                texWidth,texHeight = view.clientarea
            for vertex in range(len(view.handles)):
                # Below passes up any non-vertex handles in the view.handles list so we don't cause an error.
                if (isinstance(view.handles[vertex], LinRedHandle)) or (isinstance(view.handles[vertex], LinSideHandle)) or (isinstance(view.handles[vertex], LinCornerHandle)) or (isinstance(view.handles[vertex], BoneCornerHandle)):
                    continue
                pos = view.handles[vertex].pos
                handle = view.handles[vertex]
                tri_index = view.handles[vertex].tri_index
                ver_index = view.handles[vertex].ver_index
                tri_vtx = tris[tri_index][ver_index]
                trivertex = quarkx.vect(tri_vtx[1]-int(texWidth*.5), tri_vtx[2]-int(texHeight*.5), 0)
                vertexX, vertexY,vertexZ = view.proj(trivertex).tuple
                vertexpos = view.proj(trivertex)

                # Grid quad 1 - top left to bottom right drag
                if (cursordragstartpos[0] < cursordragendpos[0] and cursordragstartpos[1] < cursordragendpos[1]):
                    if (vertexpos.tuple[0] >= cursordragstartpos[0] and vertexpos.tuple[1] >= cursordragstartpos[1])and (vertexpos.tuple[0] <= cursordragendpos[0] and vertexpos.tuple[1] <= cursordragendpos[1]):
                        sellist = sellist + [[pos, handle, tri_index, ver_index]]
                # Grid quad 2 - top right to bottom left drag
                elif (cursordragstartpos[0] > cursordragendpos[0] and cursordragstartpos[1] < cursordragendpos[1]):
                    if (vertexpos.tuple[0] <= cursordragstartpos[0] and vertexpos.tuple[1] >= cursordragstartpos[1])and (vertexpos.tuple[0] >= cursordragendpos[0] and vertexpos.tuple[1] <= cursordragendpos[1]):
                        sellist = sellist + [[pos, handle, tri_index, ver_index]]
                # Grid quad 3 - bottom left to top right drag
                elif (cursordragstartpos[0] < cursordragendpos[0] and cursordragstartpos[1] > cursordragendpos[1]):
                    if (vertexpos.tuple[0] >= cursordragstartpos[0] and vertexpos.tuple[1] <= cursordragstartpos[1])and (vertexpos.tuple[0] <= cursordragendpos[0] and vertexpos.tuple[1] >= cursordragendpos[1]):
                        sellist = sellist + [[pos, handle, tri_index, ver_index]]
                # Grid quad 4 - bottom right to top left drag
                elif (cursordragstartpos[0] > cursordragendpos[0] and cursordragstartpos[1] > cursordragendpos[1]):
                    if (vertexpos.tuple[0] <= cursordragstartpos[0] and vertexpos.tuple[1] <= cursordragstartpos[1])and (vertexpos.tuple[0] >= cursordragendpos[0] and vertexpos.tuple[1] >= cursordragendpos[1]):
                        sellist = sellist + [[pos, handle, tri_index, ver_index]]
        else:
            ### This is the selection Grid section for the Editor's views.
            sellist = []
            vertexes = comp.currentframe.vertices
            vertexindex = -1
            for vertex in vertexes:
                vertexindex = vertexindex + 1
                vertexpos = view.proj(vertex)

                # Grid quad 1 - top left to bottom right drag
                if (cursordragstartpos[0] < cursordragendpos[0] and cursordragstartpos[1] < cursordragendpos[1]):
                    if (vertexpos.tuple[0] >= cursordragstartpos[0] and vertexpos.tuple[1] >= cursordragstartpos[1])and (vertexpos.tuple[0] <= cursordragendpos[0] and vertexpos.tuple[1] <= cursordragendpos[1]):
                        sellist = sellist + [vertexindex]
                # Grid quad 2 - top right to bottom left drag
                elif (cursordragstartpos[0] > cursordragendpos[0] and cursordragstartpos[1] < cursordragendpos[1]):
                    if (vertexpos.tuple[0] <= cursordragstartpos[0] and vertexpos.tuple[1] >= cursordragstartpos[1])and (vertexpos.tuple[0] >= cursordragendpos[0] and vertexpos.tuple[1] <= cursordragendpos[1]):
                        sellist = sellist + [vertexindex]
                # Grid quad 3 - bottom left to top right drag
                elif (cursordragstartpos[0] < cursordragendpos[0] and cursordragstartpos[1] > cursordragendpos[1]):
                    if (vertexpos.tuple[0] >= cursordragstartpos[0] and vertexpos.tuple[1] <= cursordragstartpos[1])and (vertexpos.tuple[0] <= cursordragendpos[0] and vertexpos.tuple[1] >= cursordragendpos[1]):
                        sellist = sellist + [vertexindex]
                # Grid quad 4 - bottom right to top left drag
                elif (cursordragstartpos[0] > cursordragendpos[0] and cursordragstartpos[1] > cursordragendpos[1]):
                    if (vertexpos.tuple[0] <= cursordragstartpos[0] and vertexpos.tuple[1] <= cursordragstartpos[1])and (vertexpos.tuple[0] >= cursordragendpos[0] and vertexpos.tuple[1] >= cursordragendpos[1]):
                        sellist = sellist + [vertexindex]

        ### This area for the Skin-view code only. Must return at the end to stop erroneous model drawing.
        if view.info["viewname"] == "skinview":
            SkinVertexSel(editor, sellist)
            try:
                skindrawobject = comp.currentskin
            except:
                skindrawobject = None
            buildskinvertices(editor, view, editor.layout, comp, skindrawobject)
            if quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] == "1":
                    editor.ModelVertexSelList = []
                PassSkinSel2Editor(editor)
                if editor.layout.views[0].handles == 0:
                    viewhandles = BuildHandles(editor, editor.layout.explorer, editor.layout.views[0])
                else:
                    viewhandles = editor.layout.views[0].handles
                for v in editor.layout.views:
                    if v.info["viewname"] == "skinview" or v == view:
                        continue
                    v.handles = viewhandles
                Update_Editor_Views(editor, 4)
            return


        ### From here down deals with all the Editor views.
        else:
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                if editor.ModelFaceSelList != [] and sellist == []:
                    editor.ModelFaceSelList = []
                    editor.EditorObjectList = []
                    editor.SelCommonTriangles = []
                    editor.SelVertexes = []
                    Update_Editor_Views(editor, 4)
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_ISV'] == "1" and SkinView1 is not None:
                        editor.SkinVertexSelList = []
                        editor.SkinFaceSelList = []
                        if MdlOption("PFSTSV"):
                            PassEditorSel2Skin(editor)
                        try:
                            skindrawobject = comp.currentskin
                        except:
                            skindrawobject = None
                        buildskinvertices(editor, SkinView1, editor.layout, comp, skindrawobject)
                        SkinView1.invalidate(1)
                    return
            else:
                if editor.ModelVertexSelList != [] and sellist == []:
                    editor.ModelVertexSelList = []
                    Update_Editor_Views(editor, 4)
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1" and SkinView1 is not None:
                        editor.SkinVertexSelList = []
                        PassEditorSel2Skin(editor)
                        SkinView1.invalidate()
                    return
            if sellist == []:
                if view.info["viewname"] == "skinview":
                    return
                elif view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                    view.handles = []
                elif view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                    view.handles = []
                elif view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                    view.handles = []
                elif view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                    view.handles = []
                elif view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                    view.handles = []
                else:
                    if len(view.handles) == 0:
                        view.handles = BuildHandles(editor, editor.layout.explorer, view)
                return

            removeditem = 0
            # This section selects faces in the editor using the rectangle selector
            # if in the Linear Handles button is in the face mode.
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                tris = comp.triangles
                for tri in range(len(tris)):
                    for vtx in range(len(sellist)):
                        if (sellist[vtx] == tris[tri][0][0]) or (sellist[vtx] == tris[tri][1][0]) or (sellist[vtx] == tris[tri][2][0]):
                            if not (tri in editor.ModelFaceSelList):
                                editor.ModelFaceSelList = editor.ModelFaceSelList + [tri]
                # Sets these lists up for the Linear Handle drag lines to be drawn.
                editor.SelCommonTriangles = []
                editor.SelVertexes = []
                if quarkx.setupsubset(SS_MODEL, "Options")['NFDL'] is None:
                    for tri in editor.ModelFaceSelList:
                        for vtx in range(len(comp.triangles[tri])):
                            if comp.triangles[tri][vtx][0] in editor.SelVertexes:
                                pass
                            else:
                                editor.SelVertexes = editor.SelVertexes + [comp.triangles[tri][vtx][0]] 
                                editor.SelCommonTriangles = editor.SelCommonTriangles + findTrianglesAndIndexes(comp, comp.triangles[tri][vtx][0], None)

                MakeEditorFaceObject(editor)
                if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_ISV'] == "1" and SkinView1 is not None:
                    editor.SkinVertexSelList = []
                    editor.SkinFaceSelList = []
                    if MdlOption("PFSTSV"):
                        PassEditorSel2Skin(editor, 2)
                    try:
                        skindrawobject = editor.Root.currentcomponent.currentskin
                    except:
                        skindrawobject = None
                    buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
                    SkinView1.invalidate(1)
            else:
                for vertex in sellist:
                    itemcount = 0
                    if editor.ModelVertexSelList == []:
                        editor.ModelVertexSelList = editor.ModelVertexSelList + [vertex]
                    else:
                        for item in editor.ModelVertexSelList:
                            itemcount = itemcount + 1
                            if vertex == item:
                                editor.ModelVertexSelList.remove(item)
                                removeditem = removeditem + 1
                                break
                            elif itemcount == len(editor.ModelVertexSelList):
                                editor.ModelVertexSelList = editor.ModelVertexSelList + [vertex]
            if removeditem != 0:
                viewhandles = BuildHandles(editor, editor.layout.explorer, view)

                for v in editor.layout.views:
                    if v.info["viewname"] == "skinview":
                        continue
                    elif v.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                        v.handles = []
                        continue
                    elif v.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                        v.handles = []
                        continue
                    elif v.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                        v.handles = []
                        continue
                    elif v.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                        v.handles = []
                        continue
                    elif v.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                        v.handles = []
                        continue
                    else:
                        v.handles = viewhandles
                    mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()
                    plugins.mdlgridscale.gridfinishdrawing(editor, v)
                    plugins.mdlaxisicons.newfinishdrawing(editor, v)
                    cv = v.canvas()
                    ### To avoid an error if something is selected that does not display the view handles.
                    if len(v.handles) == 0:
                        pass
                    else:
                        for h in v.handles:
                            h.draw(v, cv, h)
                        try:
                            for vtx in editor.ModelVertexSelList:
                                h = v.handles[vtx]
                                h.draw(v, cv, h)
                        except:
                            pass
                if (quarkx.setupsubset(SS_MODEL, "Options")["PVSTSV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1") and SkinView1 is not None:
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1":
                        editor.SkinVertexSelList = []
                    PassEditorSel2Skin(editor)
                    # Has to be in this order because the function call above needs
                    # the SkinView1.handles to pass the selection first, or it crashes.
                    if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1":
                        SkinView1.handles = []
                    try:
                        skindrawobject = editor.Root.currentcomponent.currentskin
                    except:
                        skindrawobject = None
                    buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
                    SkinView1.invalidate()
            else:
                if editor.ModelVertexSelList != [] or editor.ModelFaceSelList != []:
                    Update_Editor_Views(editor, 4)
                    if (quarkx.setupsubset(SS_MODEL, "Options")["PVSTSV"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1") and SkinView1 is not None:
                        if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1":
                            editor.SkinVertexSelList = []
                        PassEditorSel2Skin(editor)
                        try:
                            skindrawobject = editor.Root.currentcomponent.currentskin
                        except:
                            skindrawobject = None
                        buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
                        SkinView1.invalidate(1)
                else:
                    for v in editor.layout.views:
                        if v.info["viewname"] == "skinview":
                            continue
                        elif v.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                            v.handles = []
                        elif v.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                            v.handles = []
                        elif v.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                            v.handles = []
                        elif v.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                            v.handles = []
                        elif v.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                            v.handles = []

            from qbaseeditor import flagsmouse
            if flagsmouse == 2056 and quarkx.setupsubset(3, "Options")['VertexPaintMode'] is not None and len(editor.layout.explorer.sellist) != 0 and editor.layout.explorer.sellist[0].type == ":bone":
                # This section calls to save the vertex weights to the undo list if set to do so.
                if editor.Root.currentcomponent.dictspec.has_key("apply_vtx_weights"):
                    mdlentities.macro_applychanges(None)
                # This section updates the the "Vertex Weights Dialog" if it is opened.
                formlist = quarkx.forms(1)
                for f in formlist:
                    try:
                        if f.caption == "Vertex Weights Dialog":
                            mdlentities.macro_updatedialog(None)
                    except:
                        pass

        ### This section test to see if there are only 3 vertexes selected.
        ### If so, then it sorts them for proper order based on if the face
        ### vertexes were created in a clockwise direction (facing outwards, towards the 2D view)
        ### or a counter clockwise direction (facing inwards, away from the 2D view).
        ### The direction of the selection makes no difference. It's all in the order the vertexes were made.
            if editor.ModelVertexSelList != [] and len(editor.ModelVertexSelList) == 3:
                templist = editor.ModelVertexSelList
                if templist[1] > templist[0] and templist[1] > templist[2]:
                    editor.ModelVertexSelList = [templist[1], templist[0], templist[2]]
                elif templist[2] > templist[0] and templist[2] > templist[1]:
                    editor.ModelVertexSelList = [templist[2], templist[0], templist[1]]
                else:
                    pass


#
# Classes that manage and create the linear handle, its center box, corner & side handles and its circle.
# The normal redimages, drawn in the Map Editor, needed to be stopped for the Model Editor since we use triangles
#   instead of rectangles and that is all it will draw until a new drawing function can be added to the source code.
# The redimages drawing is stopped in the qhandles.py "def drawredimages" function for the "class RedImageDragObject".
# Each Linear handle must be stopped there using that handles class name specifically. See the qhandels code that does that.
#

class ModelEditorLinHandlesManager:
    "Linear Handle manager. This is the class called to manage and build"
    "the Linear Handle by calling its other related classes below this one."

    def __init__(self, color, bbox, list, view=None):

        self.editor = mdleditor.mdleditor
        self.color = color
        self.bbox = bbox
        self.view = view
        bmin, bmax = bbox
        bmin1 = bmax1 = ()
        for dir in "xyz":
            cmin = getattr(bmin, dir)
            cmax = getattr(bmax, dir)
            diff = cmax-cmin
            try:
                if self.view.info["viewname"] == "skinview":
                    linhdlsetting = quarkx.setupsubset(SS_MODEL,"Building")['SkinLinearSetting'][0] * 20
                else:
                    linhdlsetting = quarkx.setupsubset(SS_MODEL,"Building")['LinearSetting'][0]
            except:
                linhdlsetting = quarkx.setupsubset(SS_MODEL,"Building")['LinearSetting'][0]
            if diff<linhdlsetting:
                diff = 0.5*(linhdlsetting-diff)
                cmin = cmin - diff
                cmax = cmax + diff
            bmin1 = bmin1 + (cmin,)
            bmax1 = bmax1 + (cmax,)
        self.bmin = quarkx.vect(bmin1)
        self.bmax = quarkx.vect(bmax1)
        self.list = list
        self.tristodrawlist = []

        # To get all the triangles that need to be drawn during the drag
        # including ones that have vertexes that will be stationary.
        comp = self.editor.Root.currentcomponent
        if self.view is not None and self.view.info["viewname"] == "skinview":
            pass
        else:
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                self.tristodrawlist = []
                self.selvtxlist = []
                tris = comp.triangles
                for tri_index in self.editor.ModelFaceSelList:
                    for vtx in tris[tri_index]:
                        if vtx[0] in self.selvtxlist:
                            pass
                        else:
                            self.selvtxlist = self.selvtxlist + [vtx[0]] 
                        self.tristodrawlist = self.tristodrawlist + findTrianglesAndIndexes(comp, vtx[0], vtx[1])
            else:
                if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] == "1" and len(self.editor.ModelVertexSelList) > 1:
                    if len(self.editor.ModelVertexSelList) > 1:
                        self.editor.SelVertexes = []
                        self.editor.SelCommonTriangles = []
                        for vtx in self.editor.ModelVertexSelList:
                            if vtx in self.editor.SelVertexes:
                                pass
                            else:
                                self.editor.SelVertexes = self.editor.SelVertexes + [vtx]
                        for vtx in self.editor.SelVertexes:
                            checktris = findTrianglesAndIndexes(comp, vtx, None)
                            for tri in checktris:
                                if self.editor.SelCommonTriangles == []:
                                    self.editor.SelCommonTriangles = self.editor.SelCommonTriangles + [tri]
                                    continue
                                for comtri in range(len(self.editor.SelCommonTriangles)):
                                    if tri[2] == self.editor.SelCommonTriangles[comtri][2]:
                                        break
                                    if comtri == len(self.editor.SelCommonTriangles)-1:
                                        self.editor.SelCommonTriangles = self.editor.SelCommonTriangles + [tri]
                        templist = []
                        keepvtx = []
                        if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] == "1":
                            for tri in self.editor.SelCommonTriangles:
                                vtxcount = 0
                                keep1 = keep2 = keep3 = None
                                for vtx in self.editor.SelVertexes:
                                    if vtx == tri[4][0][0] or vtx == tri[4][1][0] or vtx == tri[4][2][0]:
                                        vtxcount = vtxcount + 1
                                        if keep1 is None:
                                            keep1 = vtx
                                        elif keep2 is None:
                                            keep2 = vtx
                                        else:
                                            keep3 = vtx
                                if vtxcount > 1:
                                    templist = templist + [tri]
                                    if not (keep1 in keepvtx):
                                        keepvtx = keepvtx + [keep1]
                                    if not (keep2 in keepvtx):
                                        keepvtx = keepvtx + [keep2]
                                    if keep3 is not None and not (keep3 in keepvtx):
                                        keepvtx = keepvtx + [keep3]

                            perimeter_edge = []
                            for tri in range(len(templist)):
                                if (templist[tri][4][0][0] in keepvtx) and (templist[tri][4][1][0] in keepvtx) and not (templist[tri][4][2][0] in keepvtx):
                                    temp = (templist[tri][2], templist[tri][4][0][0], templist[tri][4][1][0])
                                    if not (temp in perimeter_edge):
                                        perimeter_edge = perimeter_edge + [temp]
                                if (templist[tri][4][1][0] in keepvtx) and (templist[tri][4][2][0] in keepvtx) and not (templist[tri][4][0][0] in keepvtx):
                                    temp = (templist[tri][2], templist[tri][4][1][0], templist[tri][4][2][0])
                                    if not (temp in perimeter_edge):
                                        perimeter_edge = perimeter_edge + [temp]
                                if (templist[tri][4][2][0] in keepvtx) and (templist[tri][4][0][0] in keepvtx) and not (templist[tri][4][1][0] in keepvtx):
                                    temp = (templist[tri][2], templist[tri][4][2][0], templist[tri][4][0][0])
                                    if not (temp in perimeter_edge):
                                        perimeter_edge = perimeter_edge + [temp]

                            edgevtxs = []
                            for edge in perimeter_edge:
                                if not (edge[1] in edgevtxs):
                                    edgevtxs = edgevtxs + [edge[1]]
                                if not (edge[2] in edgevtxs):
                                    edgevtxs = edgevtxs + [edge[2]]

                            self.editor.SelCommonTriangles = perimeter_edge
                            if self.editor.SelCommonTriangles == [] and self.editor.ModelVertexSelList != [] and self.view is not None:
                                quarkx.msgbox("Improper Selection !\nFunction will falter !\n\nYou should select the two\nvertexes of each triangle's edge\nthat is to be extruded.\n\nOnly one vertex of a triangle\nis in your selection.", MT_ERROR, MB_OK)
                                self.editor.SelVertexes = []
                                self.editor.SelCommonTriangles = []

                            if len(self.editor.SelVertexes) != len(edgevtxs):
                                self.editor.SelVertexes = edgevtxs
                                templist = []
                                for vtx in self.editor.ModelVertexSelList:
                                   if not (vtx in self.editor.SelVertexes):
                                       pass
                                   else:
                                       templist = templist + [vtx]
                                self.editor.ModelVertexSelList = templist
                                self.editor.ModelVertexSelListPos = []
                                self.editor.ModelVertexSelListBBox = None
                                vertices = comp.currentframe.vertices
                                for vtxpos in self.editor.ModelVertexSelList:
                                    self.editor.ModelVertexSelListPos = self.editor.ModelVertexSelListPos + [vertices[vtxpos]]
                                self.editor.ModelVertexSelListBbox = quarkx.boundingboxof(self.editor.ModelVertexSelListPos)

                        else:
                            for tri in self.editor.SelCommonTriangles:
                                vtxcount = 0
                                keep1 = keep2 = keep3 = None
                                for vtx in self.editor.SelVertexes:
                                    if vtx == tri[4][0][0] or vtx == tri[4][1][0] or vtx == tri[4][2][0]:
                                        vtxcount = vtxcount + 1
                                        if keep1 is None:
                                            keep1 = vtx
                                        elif keep2 is None:
                                            keep2 = vtx
                                        else:
                                            keep3 = vtx
                                if vtxcount > 1:
                                    if not (keep1 in keepvtx):
                                        keepvtx = keepvtx + [keep1]
                                    if not (keep2 in keepvtx):
                                        keepvtx = keepvtx + [keep2]
                                    if keep3 is not None and not (keep3 in keepvtx):
                                        keepvtx = keepvtx + [keep3]
                                        templist = templist + [(tri[2], keep1, keep2, keep3)]
                                    else:
                                        templist = templist + [(tri[2], keep1, keep2)]
                            self.editor.SelCommonTriangles = templist
                            if self.editor.SelCommonTriangles == [] and self.editor.ModelVertexSelList != [] and self.view is not None:
                                quarkx.msgbox("Improper Selection !\nFunction will falter !\n\nYou should select at least two\nvertexes of each triangle's edge\nthat is to be extruded.\n\nOnly one vertex of a triangle\nis in your selection.", MT_ERROR, MB_OK)
                                self.editor.SelVertexes = []
                                self.editor.SelCommonTriangles = []

                            if len(self.editor.SelVertexes) != len(keepvtx):
                                self.editor.SelVertexes = keepvtx
                                templist = []
                                for vtx in self.editor.ModelVertexSelList:
                                   if not (vtx in self.editor.SelVertexes):
                                       pass
                                   else:
                                       templist = templist + [vtx]
                                self.editor.ModelVertexSelList = templist
                                self.editor.ModelVertexSelListPos = []
                                self.editor.ModelVertexSelListBBox = None
                                vertices = self.editor.Root.currentcomponent.currentframe.vertices
                                for vtxpos in self.editor.ModelVertexSelList:
                                    self.editor.ModelVertexSelListPos = self.editor.ModelVertexSelListPos + [vertices[vtxpos]]
                                self.editor.ModelVertexSelListBbox = quarkx.boundingboxof(self.editor.ModelVertexSelListPos)

    def BuildHandles(self, center=None, minimal=None): # for ModelEditorLinHandlesManager
        "Build a list of handles to put around the circle for linear distortion."

        if center is None:
            center = 0.5 * (self.bmin + self.bmax)
        self.center = center
        if minimal is not None:
            view, grid = minimal
            if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                view.handles = []
                h = []
                return h
            elif view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                view.handles = []
                h = []
                return h
            elif view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                view.handles = []
                h = []
                return h
            elif view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                view.handles = []
                h = []
                return h
            elif view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                view.handles = []
                h = []
                return h
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


    def drawbox(self, view): # for ModelEditorLinHandlesManager
        "Draws the circle around all objects. Started as a box, but didn't look right."

        from qbaseeditor import flagsmouse
        if flagsmouse == 528 or flagsmouse == 1040: return # RMB pressed or dragging to pan (scroll) in the view.

        if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
            view.handles = []
            return
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
# Linear Drag Handle Circle's handles.
#

class LinearHandle(qhandles.GenericHandle):
    "Linear Circle handles."

    def __init__(self, pos, mgr):
        qhandles.GenericHandle.__init__(self, pos)
        self.mgr = mgr    # a LinHandlesManager instance
        self.g1 = 0
        if (self.mgr.view is not None and self.mgr.view.info["viewname"] != "skinview") or (quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1"):
            self.oldverticespos = None
            self.newverticespos = None
            self.selvtxlist = None

    def start_drag(self, view, x, y):
        editor = self.mgr.editor
        currentcomponent = editor.Root.currentcomponent
        if view.info["viewname"] == "skinview" or quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
            if view.info["viewname"] == "skinview":
                self.mgr.tristodrawlist = editor.SkinViewList['tristodraw'][currentcomponent.name]
                if self.oldverticespos is None:
                    #The "tuple" bit is to force Python to make a copy of the list (the original is changed during the drag)
                    self.oldverticespos = tuple(editor.SkinViewList['handlepos'][currentcomponent.name])
                if self.newverticespos is None:
                    self.newverticespos = editor.SkinViewList['handlepos'][currentcomponent.name]
                if self.selvtxlist is None:
                    self.selvtxlist = editor.SkinVertexSelList
        else:
            self.mgr.tristodrawlist = editor.ModelComponentList['tristodraw'][currentcomponent.name]
            if self.oldverticespos is None:
                self.oldverticespos = currentcomponent.currentframe.vertices
            if self.newverticespos is None:
                self.newverticespos = currentcomponent.currentframe.vertices
            if self.selvtxlist is None:
                self.selvtxlist = editor.ModelVertexSelList

    def getvtxpos(self, view, new, item, count, item_vtx, tri_index, item_tri_index, projvtx0, projvtx1, projvtx2):
        try:  # To avoid division by zero errors.
            if item_vtx == 0 and tri_index == item_tri_index:
                vtx0bbox = quarkx.boundingboxof([new[0].subitems[item]])
                vtx0pos = (vtx0bbox[0] + vtx0bbox[1]) * .5
                projvtx0 = view.proj(vtx0pos.tuple[0], vtx0pos.tuple[1], 0)
                count = count + 1
            if item_vtx == 1 and tri_index == item_tri_index:
                vtx1bbox = quarkx.boundingboxof([new[0].subitems[item]])
                vtx1pos = (vtx1bbox[0] + vtx1bbox[1]) * .5
                projvtx1 = view.proj(vtx1pos.tuple[0], vtx1pos.tuple[1], 0)
                count = count + 1
            if item_vtx == 2 and tri_index == item_tri_index:
                vtx2bbox = quarkx.boundingboxof([new[0].subitems[item]])
                vtx2pos = (vtx2bbox[0] + vtx2bbox[1]) * .5
                projvtx2 = view.proj(vtx2pos.tuple[0], vtx2pos.tuple[1], 0)
                count = count + 1
            return [count, projvtx0, projvtx1, projvtx2]
        except:
            return[None, None, None, None]

    def drawface(self, view, cv, count, comp, tri_index, texWidth, texHeight, projvtx0, projvtx1, projvtx2):
        if count != 3:
            ###  Get missing vtx's
            if projvtx0 is None:
                projvtx0 = view.proj(quarkx.vect((comp.triangles[tri_index][0][1]-int(texWidth*.5), comp.triangles[tri_index][0][2]-int(texHeight*.5), 0)))
            if projvtx1 is None:
                projvtx1 = view.proj(quarkx.vect((comp.triangles[tri_index][1][1]-int(texWidth*.5), comp.triangles[tri_index][1][2]-int(texHeight*.5), 0)))
            if projvtx2 is None:
                projvtx2 = view.proj(quarkx.vect((comp.triangles[tri_index][2][1]-int(texWidth*.5), comp.triangles[tri_index][2][2]-int(texHeight*.5), 0)))
            cv.line(int(projvtx0.tuple[0]), int(projvtx0.tuple[1]), int(projvtx1.tuple[0]), int(projvtx1.tuple[1]))
            cv.line(int(projvtx1.tuple[0]), int(projvtx1.tuple[1]), int(projvtx2.tuple[0]), int(projvtx2.tuple[1]))
            cv.line(int(projvtx2.tuple[0]), int(projvtx2.tuple[1]), int(projvtx0.tuple[0]), int(projvtx0.tuple[1]))
            count = 0
            projvtx0 = projvtx1 = projvtx2 = None
        else:
            cv.line(int(projvtx0.tuple[0]), int(projvtx0.tuple[1]), int(projvtx1.tuple[0]), int(projvtx1.tuple[1]))
            cv.line(int(projvtx1.tuple[0]), int(projvtx1.tuple[1]), int(projvtx2.tuple[0]), int(projvtx2.tuple[1]))
            cv.line(int(projvtx2.tuple[0]), int(projvtx2.tuple[1]), int(projvtx0.tuple[0]), int(projvtx0.tuple[1]))
            count = 0
            projvtx0 = projvtx1 = projvtx2 = None
        return [count, projvtx0, projvtx1, projvtx2]

    def drag(self, v1, v2, flags, view): # for LinearHandle
        delta = v2-v1
        editor = self.mgr.editor
        comp = editor.Root.currentcomponent
        from qbaseeditor import flagsmouse
        if flags&MB_CTRL:
            if view.info["viewname"] == "skinview":
                if isinstance(self, LinRedHandle) and quarkx.setupsubset(SS_MODEL, "Options")['SkinGridActive'] is not None:
                    delta = alignskintogrid(delta, 0)
                    self.g1 = 0
                else:
                    self.g1 = 1
            else:
                if isinstance(self, LinRedHandle) and quarkx.setupsubset(SS_MODEL, "Options")['GridActive'] is not None:
                    delta = qhandles.aligntogrid(delta, 0)
                self.g1 = 1
        else:
            self.g1 = 0

        if delta or (flags&MB_REDIMAGE):
            if view.info["viewname"] == "skinview" or quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                if view.info["viewname"] == "skinview":
                    if isinstance(self, LinRedHandle):
                        new = []
                    else:
                        if flagsmouse == 2056 or flagsmouse == 2060:
                            list = []
                            self.linoperation(list, delta, self.g1, view)
                            new = delta = None
                        else:
                            list = []
                            new = self.linoperation(list, delta, self.g1, view)
                else:
                    new = map(lambda obj: obj.copy(), self.mgr.list)
                if not self.linoperation(new, delta, self.g1, view):
                    if not flags&MB_REDIMAGE:
                        new = None
            else:
                list = []
                new = self.linoperation(list, delta, self.g1, view)
        else:
            new = None

        # This draws all of the views, including the Skin-view, Linear handles and drag lines
        # except for center handle drags which is done in class LinRedHandle, linoperation function.
        cv = view.canvas()
        # This section draws the Skin-view drag lines, except for the center Linear handle.
        if view.info["viewname"] == "skinview" and new is not None and not isinstance(self, LinRedHandle):
            # We do this to draw just the Linear handles.
            view.handles.reverse()
            for h in view.handles:
                if isinstance(h, SkinHandle):
                    break
                h.draw(view, cv, h)
            view.handles.reverse()

            vtxs = editor.SkinViewList['handlepos'][comp.name]
            dragcolor = MapColor("SkinDragLines", SS_MODEL)
            cv.pencolor = dragcolor
            tex = comp.currentskin

            if tex is not None:
                texWidth,texHeight = tex["Size"]
            else:
                texWidth,texHeight = view.clientarea

            projvtx0 = projvtx1 = projvtx2 = None
            compvtx = self.newverticespos
            for vtx in self.selvtxlist:
                index = vtx[2]*3+vtx[3]
                p = view.proj(compvtx[index])
                if quarkx.setupsubset(SS_MODEL, "Options")['SingleSelDragLines'] is None:
                    if index in self.mgr.tristodrawlist:
                        cv.pencolor = dragcolor
                        for vtx2 in self.mgr.tristodrawlist[index]:
                            p2 = view.proj(compvtx[vtx2])
                            cv.line(p, p2)
                if p.visible:
                    cv.pencolor = skinvertexsellistcolor
                    cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)

        # This section draws all the editor views drag lines, except for the center Linear handle.
        elif new is not None and not isinstance(self, LinRedHandle):
            framevtxs = comp.currentframe.vertices
            dragcolor = MapColor("Drag3DLines", SS_MODEL)
            cv.pencolor = dragcolor
            projvtx0 = projvtx1 = projvtx2 = None
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
                cv.penwidth = 1
                cv.penstyle = PS_INSIDEFRAME
                cv.brushstyle = BS_CLEAR
                compvtx = self.newverticespos
            #    handle_radius = (self.pos0.tuple[0] - self.center.tuple[0]) * .5
                for vtx in self.selvtxlist:
                    p = view.proj(compvtx[vtx])
                    if quarkx.setupsubset(SS_MODEL, "Options")['NVDL'] is None:
                        if vtx in self.mgr.tristodrawlist:
                            cv.pencolor = dragcolor
                            for vtx2 in self.mgr.tristodrawlist[vtx]:
                                p2 = view.proj(compvtx[vtx2])
                                cv.line(p, p2)
                    if p.visible:
                        cv.pencolor = vertexsellistcolor
                        cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
            else:
                for tri in self.mgr.tristodrawlist:
                    if new[0].subitems != [] and quarkx.setupsubset(SS_MODEL, "Options")['NVDL'] is not None:
                        break
                    if new[0].subitems == [] and quarkx.setupsubset(SS_MODEL, "Options")['NFDL'] is not None:
                        break
                    for tri_vtx in range(len(tri[4])):
                        # This section draws the vertex drag lines.
                        if new[0].subitems != []:
                            try: # To stop unsubscriptable object errors.
                                for item in new[0].subitems:
                                    if int(item.shortname) == tri[4][tri_vtx][0]:
                                        if tri_vtx == 0:
                                            vtx0bbox = quarkx.boundingboxof([item])
                                            vtx0pos = (vtx0bbox[0] + vtx0bbox[1]) * .5
                                            projvtx0 = view.proj(vtx0pos.tuple[0], vtx0pos.tuple[1], vtx0pos.tuple[2])
                                        if tri_vtx == 1:
                                            vtx1bbox = quarkx.boundingboxof([item])
                                            vtx1pos = (vtx1bbox[0] + vtx1bbox[1]) * .5
                                            projvtx1 = view.proj(vtx1pos.tuple[0], vtx1pos.tuple[1], vtx1pos.tuple[2])
                                        if tri_vtx == 2:
                                            vtx2bbox = quarkx.boundingboxof([item])
                                            vtx2pos = (vtx2bbox[0] + vtx2bbox[1]) * .5
                                            projvtx2 = view.proj(vtx2pos.tuple[0], vtx2pos.tuple[1], vtx2pos.tuple[2])
                            except:
                                projvtx0 = projvtx1 = projvtx2 = None
                        # This section draws the face drag lines.
                        if new[0].subitems == []:
                            if tri[4][tri_vtx][0] not in self.mgr.selvtxlist:
                                for face in new:
                                    objvtxs = face["v"]
                                    vtxs = face.shortname.split(',')
                                    vtxs = [int(vtxs[2]), int(vtxs[3]), int(vtxs[4])]
                                    for vtx in range(len(vtxs)):
                                        if vtxs[vtx] == tri[0]:
                                            if vtx == 0:
                                                projvtx0 = view.proj(quarkx.vect(objvtxs[0], objvtxs[1], objvtxs[2]))
                                            if vtx == 1:
                                                projvtx1 = view.proj(quarkx.vect(objvtxs[3], objvtxs[4], objvtxs[5]))
                                            if vtx == 2:
                                                projvtx2 = view.proj(quarkx.vect(objvtxs[6], objvtxs[7], objvtxs[8]))

                                 ###  Draw face stationary vtx line.
                                if projvtx0 is not None:
                                    trivtx = view.proj(framevtxs[tri[4][tri_vtx][0]])
                                    cv.line(int(projvtx0.tuple[0]), int(projvtx0.tuple[1]), int(trivtx.tuple[0]), int(trivtx.tuple[1]))
                                if projvtx1 is not None:
                                    trivtx = view.proj(framevtxs[tri[4][tri_vtx][0]])
                                    cv.line(int(projvtx1.tuple[0]), int(projvtx1.tuple[1]), int(trivtx.tuple[0]), int(trivtx.tuple[1]))
                                if projvtx2 is not None:
                                    trivtx = view.proj(framevtxs[tri[4][tri_vtx][0]])
                                    cv.line(int(projvtx2.tuple[0]), int(projvtx2.tuple[1]), int(trivtx.tuple[0]), int(trivtx.tuple[1]))
                                projvtx0 = projvtx1 = projvtx2 = None

                    ###  Get stationary vtx's to draw for vertex drag.
                    if new[0].name.endswith(":g"):
                        if projvtx0 is None:
                            projvtx0 = view.proj(framevtxs[tri[4][0][0]])
                        if projvtx1 is None:
                            projvtx1 = view.proj(framevtxs[tri[4][1][0]])
                        if projvtx2 is None:
                            projvtx2 = view.proj(framevtxs[tri[4][2][0]])
                        cv.line(int(projvtx0.tuple[0]), int(projvtx0.tuple[1]), int(projvtx1.tuple[0]), int(projvtx1.tuple[1]))
                        cv.line(int(projvtx1.tuple[0]), int(projvtx1.tuple[1]), int(projvtx2.tuple[0]), int(projvtx2.tuple[1]))
                        cv.line(int(projvtx2.tuple[0]), int(projvtx2.tuple[1]), int(projvtx0.tuple[0]), int(projvtx0.tuple[1]))

                    # Section below draws the selected faces if any.
                    if editor.EditorObjectList != []:
                        if quarkx.setupsubset(SS_MODEL, "Options")["NFDL"] is None: # NFDL = no face drag lines.
                            cv.pencolor = faceseloutline
                            try:
                                cv.penwidth = float(quarkx.setupsubset(SS_MODEL,"Options")['linethickness'])
                            except:
                                cv.penwidth = 2
                            cv.brushcolor = faceseloutline
                            cv.brushstyle = BS_SOLID
                        for obj in new:
                            if obj.name.endswith(":g"):
                                if (quarkx.setupsubset(SS_MODEL,"Options")['NFO'] != "1"):
                                    for face in editor.EditorObjectList:
                                        objvtxs = face["v"]
                                        projvtx0 = view.proj(quarkx.vect(objvtxs[0], objvtxs[1], objvtxs[2]))
                                        projvtx1 = view.proj(quarkx.vect(objvtxs[3], objvtxs[4], objvtxs[5]))
                                        projvtx2 = view.proj(quarkx.vect(objvtxs[6], objvtxs[7], objvtxs[8]))
                                        cv.line(int(projvtx0.tuple[0]), int(projvtx0.tuple[1]), int(projvtx1.tuple[0]), int(projvtx1.tuple[1]))
                                        cv.line(int(projvtx1.tuple[0]), int(projvtx1.tuple[1]), int(projvtx2.tuple[0]), int(projvtx2.tuple[1]))
                                        cv.line(int(projvtx2.tuple[0]), int(projvtx2.tuple[1]), int(projvtx0.tuple[0]), int(projvtx0.tuple[1]))
                            else:
                                objvtxs = obj["v"]
                                projvtx0 = view.proj(quarkx.vect(objvtxs[0], objvtxs[1], objvtxs[2]))
                                projvtx1 = view.proj(quarkx.vect(objvtxs[3], objvtxs[4], objvtxs[5]))
                                projvtx2 = view.proj(quarkx.vect(objvtxs[6], objvtxs[7], objvtxs[8]))
                                cv.line(int(projvtx0.tuple[0]), int(projvtx0.tuple[1]), int(projvtx1.tuple[0]), int(projvtx1.tuple[1]))
                                cv.line(int(projvtx1.tuple[0]), int(projvtx1.tuple[1]), int(projvtx2.tuple[0]), int(projvtx2.tuple[1]))
                                cv.line(int(projvtx2.tuple[0]), int(projvtx2.tuple[1]), int(projvtx0.tuple[0]), int(projvtx0.tuple[1]))
                                editor.EditorObjectList = new
                        cv.pencolor = dragcolor
                        cv.penwidth = 1

                    projvtx0 = projvtx1 = projvtx2 = None

        if view.info['viewname'] == "skinview":
            pass
        else:
            for h in view.handles:
                h.draw(view, cv, h)
        return self.mgr.list, new

    def linoperation(self, list, delta, g1, view): # for LinearHandle
        if list is None:
            return
        self.g1 = g1
        matrix = self.buildmatrix(delta, self.g1, view)
        if matrix is None:
            matrix = quarkx.matrix(quarkx.vect(1, 0, 0), quarkx.vect(0, 1, 0), quarkx.vect(0, 0, 1))

        if view.info["viewname"] == "skinview":
            from qbaseeditor import flagsmouse
            if flagsmouse == 2056 or flagsmouse == 2060:
                editor = self.mgr.editor
                comp = editor.Root.currentcomponent
                tex = comp.currentskin
                if tex is not None:
                    texWidth,texHeight = tex["Size"]
                else:
                    texWidth,texHeight = view.clientarea
                new_comp = comp.copy()
                triangles = new_comp.triangles
                undo = quarkx.action()
                for dragvtx in self.selvtxlist:
                    dragvtx[0] = self.newverticespos[dragvtx[2]*3+dragvtx[3]]
                    dragvtx[1].pos = dragvtx[0]
                    pos1 = dragvtx[0].tuple
                    tri = triangles[dragvtx[2]]
                    vtx = tri[dragvtx[3]][0]
                    if dragvtx[3] == 0:
                        triangles[dragvtx[2]] = ((vtx,int(pos1[0]+texWidth*.5),int(pos1[1]+texHeight*.5)), tri[1], tri[2])
                    elif dragvtx[3] == 1:
                        triangles[dragvtx[2]] = (tri[0], (vtx,int(pos1[0]+texWidth*.5),int(pos1[1]+texHeight*.5)), tri[2])
                    else:
                        triangles[dragvtx[2]] = (tri[0], tri[1], (vtx,int(pos1[0]+texWidth*.5),int(pos1[1]+texHeight*.5)))
                editor.SkinVertexSelList = self.selvtxlist
                new_comp.triangles = triangles
                oldobjectslist = [comp]
                newobjectslist = [new_comp]
                self.ok(editor, undo, oldobjectslist, newobjectslist, view)
            else:
                view.repaint()
                rotationorigin = self.mgr.center
                # Use this if the radius should also be changed:
                #try:
                #    changedradius = sqrt(pow(newpos.x, 2) + pow(newpos.y, 2) + pow(newpos.z, 2)) / sqrt(pow(oldpos.x, 2) + pow(oldpos.y, 2) + pow(oldpos.z, 2))
                #except:
                #    changedradius = 1.0
                changedradius = 1.0
                # Reset the self.newverticespos list
                for vtx in self.selvtxlist:
                    changedpos = self.oldverticespos[vtx[2]*3+vtx[3]] - rotationorigin
                    changedpos = changedradius * matrix * changedpos
                    self.newverticespos[vtx[2]*3+vtx[3]] = changedpos + rotationorigin
        else:
            view.repaint()
            editor = self.mgr.editor
            mdleditor.setsingleframefillcolor(editor, view)
            plugins.mdlgridscale.gridfinishdrawing(editor, view)
            plugins.mdlaxisicons.newfinishdrawing(editor, view)
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
                rotationorigin = self.mgr.center
                # Use this if the radius should also be changed:
                #try:
                #    changedradius = sqrt(pow(newpos.x, 2) + pow(newpos.y, 2) + pow(newpos.z, 2)) / sqrt(pow(oldpos.x, 2) + pow(oldpos.y, 2) + pow(oldpos.z, 2))
                #except:
                #    changedradius = 1.0
                changedradius = 1.0
                # Reset the self.newverticespos list
                for vtx in self.selvtxlist:
                    changedpos = self.oldverticespos[vtx] - rotationorigin
                    changedpos = changedradius * matrix * changedpos
                    self.newverticespos[vtx] = changedpos + rotationorigin
            else:
                for obj in list: # Moves and draws the models triangles or vertexes correctly for the matrix handles.
                    obj.linear(self.mgr.center, matrix)
                    if obj.name.endswith(":g"):
                        newobj = obj.copy()
                        dragcolor = vertexsellistcolor
                        # To avoid division by zero errors.
                        try:
                            view.drawmap(newobj, DM_OTHERCOLOR, dragcolor)
                        except:
                            pass
        return 1


class LinRedHandle(LinearHandle): # for LinRedHandle, the center handle.
    "Linear Circle: handle at the center."

    hint = "           move selection free floating (Ctrl key = on grid)"

    def __init__(self, pos, mgr):
        LinearHandle.__init__(self, pos, mgr)
        self.cursor = CR_MULTIDRAG
        self.undomsg = "linear center handle drag"
        self.oldverticespos = None
        self.newverticespos = None
        self.selvtxlist = None

    def draw(self, view, cv, draghandle=None):
        from qbaseeditor import flagsmouse
        if flagsmouse == 528 or flagsmouse == 1040: return # RMB pressed or dragging to pan (scroll) in the view.

        if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
            view.handles = []
            return

        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = MapColor("LinearHandleCenter", SS_MODEL)
            cv.pencolor = MapColor("LinearHandleOutline", SS_MODEL)
            cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+4, int(p.y)+4)

    def drawred(self, redimages, view, redcolor): # To draw the drag lines for Linear Center Handle.
        cv = view.canvas()
        cv.penwidth = 1
        cv.penstyle = PS_INSIDEFRAME
        cv.brushstyle = BS_CLEAR
        vertices = self.selvtxlist
        compvtx = self.newverticespos
        if (quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] is not None or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None):
            oldvtxs = self.mgr.editor.Root.currentcomponent.currentframe.vertices
            cv.pencolor = MapColor("Drag3DLines", SS_MODEL)
            # Section below draws the drag lines.
            if quarkx.setupsubset(SS_MODEL, "Options")['NVDL'] is None: # NVDL = no vertex drag lines.
                for tri in self.mgr.editor.SelCommonTriangles:
                    if len(tri) == 3:
                        oldtri, oldver1 ,oldver0 = tri
                    else:
                        oldtri, oldver1 ,oldver0 ,oldver2 = tri
                    for vtx in vertices:
                        if vtx == oldver1:
                            oldver0X ,oldver0Y, oldver0Z = view.proj(oldvtxs[oldver0]).tuple
                            ver0X ,ver0Y, ver0Z = view.proj(self.newverticespos[vtx]).tuple
                        if vtx == oldver0:
                            oldver1X ,oldver1Y, oldver1Z = view.proj(oldvtxs[oldver1]).tuple
                            ver1X ,ver1Y, ver1Z = view.proj(self.newverticespos[vtx]).tuple
                        if len(tri) == 4:
                            if vtx == oldver2:
                                oldver2X ,oldver2Y, oldver2Z = view.proj(oldvtxs[oldver2]).tuple
                                ver2X ,ver2Y, ver2Z = view.proj(self.newverticespos[vtx]).tuple
                    cv.line(int(ver0X), int(ver0Y), int(ver1X), int(ver1Y)) # Top line
                    cv.line(int(ver1X), int(ver1Y), int(oldver0X), int(oldver0Y)) # right line
                    cv.line(int(oldver1X), int(oldver1Y), int(ver0X), int(ver0Y)) # left line
            # Section below draws the vertexes being dragged.
            for vtx in vertices:
                p = view.proj(compvtx[vtx])
                if p.visible:
                    cv.pencolor = vertexsellistcolor
                    cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
        else:
            tristodraw = self.mgr.editor.ModelComponentList['tristodraw'][self.mgr.editor.Root.currentcomponent.name]
            for vtx in vertices:
                p = view.proj(compvtx[vtx])
                # Section below draws the drag lines.
                if quarkx.setupsubset(SS_MODEL, "Options")['NVDL'] is None: # NVDL = no vertex drag lines.
                    cv.pencolor = redcolor
                    if vtx in tristodraw:
                        for vtx2 in tristodraw[vtx]:
                            p2 = view.proj(compvtx[vtx2])
                            cv.line(p, p2)
                # Section below draws the vertexes being dragged.
                if p.visible:
                    cv.pencolor = vertexsellistcolor
                    cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)

    def linoperation(self, list, delta, g1, view): # for LinRedHandle, the center handle.
        editor = self.mgr.editor
        self.g1 = g1

        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)

        cv = view.canvas()
        if view.info["viewname"] == "skinview":
            # This is for the drag lines color.
            dragcolor = MapColor("SkinDragLines", SS_MODEL)
        else:
            dragcolor = MapColor("Drag3DLines", SS_MODEL)
            view.repaint()
            cv.pencolor = dragcolor
            mdleditor.setsingleframefillcolor(editor, view)
            plugins.mdlgridscale.gridfinishdrawing(editor, view)
            plugins.mdlaxisicons.newfinishdrawing(editor, view)
        comp = self.mgr.editor.Root.currentcomponent
        if view.info["viewname"] == "skinview":
            from qbaseeditor import flagsmouse
            if flagsmouse == 2056 or flagsmouse == 2060:
                tex = comp.currentskin
                if tex is not None:
                    texWidth,texHeight = tex["Size"]
                else:
                    texWidth,texHeight = view.clientarea
                new_comp = comp.copy()
                triangles = new_comp.triangles
                undo = quarkx.action()
                for dragvtx in editor.SkinVertexSelList:
                    dragvtx[0] = dragvtx[0]+delta
                    dragvtx[1].pos = dragvtx[0]
                    pos1 = dragvtx[0].tuple
                    tri = triangles[dragvtx[2]]
                    vtx = tri[dragvtx[3]][0]
                    if dragvtx[3] == 0:
                        triangles[dragvtx[2]] = ((vtx,int(pos1[0]+texWidth*.5),int(pos1[1]+texHeight*.5)), tri[1], tri[2])
                    elif dragvtx[3] == 1:
                        triangles[dragvtx[2]] = (tri[0], (vtx,int(pos1[0]+texWidth*.5),int(pos1[1]+texHeight*.5)), tri[2])
                    else:
                        triangles[dragvtx[2]] = (tri[0], tri[1], (vtx,int(pos1[0]+texWidth*.5),int(pos1[1]+texHeight*.5)))
                new_comp.triangles = triangles
                oldobjectslist = [comp]
                newobjectslist = [new_comp]
                self.ok(editor, undo, oldobjectslist, newobjectslist, view)
            else:
                view.repaint()
                cv.pencolor = dragcolor
                tris = editor.SkinViewList['tristodraw'][comp.name]
                handles = view.handles
                triangles = comp.triangles
                if quarkx.setupsubset(SS_MODEL, "Options")['SingleSelDragLines'] is None:
                    import operator
                    drag_vtxs = []
                    for i in editor.SkinVertexSelList:
                        drag_vtxs = drag_vtxs + [i[2]*3 + i[3]]
                else:
                    selsize = int(quarkx.setupsubset(SS_MODEL,"Building")['SkinLinearSelected'][0])
                    cv.pencolor = skinvertexsellistcolor
                    cv.brushstyle = BS_CLEAR
                for dragvtx in editor.SkinVertexSelList:
                    pos1 = view.proj(dragvtx[0]+delta).tuple
                    if quarkx.setupsubset(SS_MODEL, "Options")['SingleSelDragLines'] is None:
                        dragindex = dragvtx[2]*3 + dragvtx[3]
                        vtxs = tris[dragindex]
                        for i in vtxs:
                            if i in drag_vtxs:
                                index = operator.indexOf(drag_vtxs, i)
                                vtx2 = editor.SkinVertexSelList[index][0]
                                pos2 = view.proj(vtx2+delta).tuple
                            else:
                                vtx2 = handles[i].pos
                                pos2 = view.proj(vtx2).tuple
                            cv.line(int(pos1[0]), int(pos1[1]), int(pos2[0]), int(pos2[1]))
                    else:
                        cv.rectangle(int(pos1[0])-selsize, int(pos1[1])-selsize, int(pos1[0])+selsize, int(pos1[1])+selsize)
        else:
            self.newverticespos = comp.currentframe.vertices
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] is not None or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
                    pass
                else:
                    if quarkx.setupsubset(SS_MODEL, "Options")["NFDL"] is None: # NFDL = no face drag lines.
                        # This draws the selected faces drag lines for a regular Linear Center Handle drag.
                        for tri in editor.SelCommonTriangles:
                            dragprojvtx = view.proj(self.newverticespos[tri[0]]+delta)
                            for vtx in range(len(tri[4])):
                                if tri[4][vtx][0] == tri[0]:
                                    continue
                                else:
                                    if tri[4][vtx][0] in editor.SelVertexes:
                                        projvtx = view.proj(self.newverticespos[tri[4][vtx][0]]+delta)
                                    else:
                                        projvtx = view.proj(self.newverticespos[tri[4][vtx][0]])
                                    cv.line(int(dragprojvtx.tuple[0]), int(dragprojvtx.tuple[1]), int(projvtx.tuple[0]), int(projvtx.tuple[1]))
            else:
                if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] is not None or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
                    # This updates the selected drag vertex positions for a Linear Center Handle drag.
                    vertices = self.selvtxlist
                    for vtx in vertices:
                        self.newverticespos[vtx] = self.newverticespos[vtx] + delta
                else:
                    # This updates the selected drag vertex positions for a Linear Center Handle drag.
                    vertices = self.selvtxlist
                    for vtx in vertices:
                        self.newverticespos[vtx] = self.newverticespos[vtx] + delta

        for obj in list: # Draws the models triangles or vertexes, that are being dragged, correctly during a drag in all views.
            obj.translate(delta)
            if obj.name.endswith(":g"):
                if view.info["viewname"] != "skinview" and (quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] is not None or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None) and quarkx.setupsubset(SS_MODEL, "Options")["NVDL"] is None: # NVDL = no vertex drag lines.
                    # If Extruding faces this section draws the drag lines.
                    oldvtxs = comp.currentframe.vertices
                    cv.pencolor = MapColor("Drag3DLines", SS_MODEL)
                    for tri in editor.SelCommonTriangles:
                        if len(tri) == 3:
                            oldtri, oldver1 ,oldver0 = tri
                        else:
                            oldtri, oldver1 ,oldver0 ,oldver2 = tri
                        for poly in range(len(obj.subitems)):
                            if int(obj.subitems[poly].shortname) == oldver1:
                                oldver0X ,oldver0Y, oldver0Z = view.proj(oldvtxs[oldver0]).tuple
                                ver0X ,ver0Y, ver0Z = view.proj(obj.subitems[poly].subitems[0]["v"][0], obj.subitems[poly].subitems[0]["v"][1], obj.subitems[poly].subitems[0]["v"][2]).tuple
                            if int(obj.subitems[poly].shortname) == oldver0:
                                oldver1X ,oldver1Y, oldver1Z = view.proj(oldvtxs[oldver1]).tuple
                                ver1X ,ver1Y, ver1Z = view.proj(obj.subitems[poly].subitems[0]["v"][0] ,obj.subitems[poly].subitems[0]["v"][1], obj.subitems[poly].subitems[0]["v"][2]).tuple
                            if len(tri) == 4:
                                if int(obj.subitems[poly].shortname) == oldver2:
                                    oldver2X ,oldver2Y, oldver2Z = view.proj(oldvtxs[oldver2]).tuple
                                    ver2X ,ver2Y, ver2Z = view.proj(obj.subitems[poly].subitems[0]["v"][0] ,obj.subitems[poly].subitems[0]["v"][1], obj.subitems[poly].subitems[0]["v"][2]).tuple
                        cv.line(int(ver0X), int(ver0Y), int(ver1X), int(ver1Y)) # Top line
                        cv.line(int(ver1X), int(ver1Y), int(oldver0X), int(oldver0Y)) # right line
                        cv.line(int(oldver1X), int(oldver1Y), int(ver0X), int(ver0Y)) # left line

                # This section draws the selected vertexes that are being dragged.
             #   dragcolor = vertexsellistcolor
             #   view.drawmap(obj, DM_OTHERCOLOR, dragcolor)
            else:
                # This section draws the selected faces that are being dragged.
                vect0X ,vect0Y, vect0Z, vect1X ,vect1Y, vect1Z, vect2X ,vect2Y, vect2Z = obj["v"]
                vect0X ,vect0Y, vect0Z = view.proj(vect0X ,vect0Y, vect0Z).tuple
                vect1X ,vect1Y, vect1Z = view.proj(vect1X ,vect1Y, vect1Z).tuple
                vect2X ,vect2Y, vect2Z = view.proj(vect2X ,vect2Y, vect2Z).tuple
                if (quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] is not None or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None) and quarkx.setupsubset(SS_MODEL, "Options")["NFDL"] is None:
                    # If Extruding faces this section draws the drag lines.
                    tuplename = tuple(str(s) for s in obj.shortname.split(','))
                    compname, tri_index, ver_index0, ver_index1, ver_index2 = tuplename
                    ver0X ,ver0Y, ver0Z = view.proj(self.newverticespos[int(ver_index0)]).tuple
                    ver1X ,ver1Y, ver1Z = view.proj(self.newverticespos[int(ver_index1)]).tuple
                    ver2X ,ver2Y, ver2Z = view.proj(self.newverticespos[int(ver_index2)]).tuple
                    cv.pencolor = dragcolor
                    cv.line( int(ver0X), int(ver0Y), int(vect0X), int(vect0Y))
                    cv.line( int(ver1X), int(ver1Y), int(vect1X), int(vect1Y))
                    cv.line( int(ver2X), int(ver2Y), int(vect2X), int(vect2Y))
                cv.pencolor = faceseloutline
                try:
                    cv.penwidth = float(quarkx.setupsubset(SS_MODEL,"Options")['linethickness'])
                except:
                    cv.penwidth = 2
                cv.brushcolor = faceseloutline
                cv.brushstyle = BS_SOLID
                cv.line(int(vect0X), int(vect0Y), int(vect1X), int(vect1Y))
                cv.line(int(vect1X), int(vect1Y), int(vect2X), int(vect2Y))
                cv.line(int(vect2X), int(vect2Y), int(vect0X), int(vect0Y))
                cv.pencolor = dragcolor
                cv.penwidth = 1

        if view.info["type"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["type"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + " " + ftoss(self.pos.z+delta.z)
        elif view.info["type"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            if view.info["viewname"] == "skinview":
                try:
                    tex = editor.Root.currentcomponent.currentskin
                    texWidth,texHeight = tex["Size"]
                except:
                    texWidth,texHeight = view.clientarea


                if self.pos.x > (texWidth * .5):
                    Xstart = int((self.pos.x / texWidth) -.5)
                    Xstartpos = -texWidth + self.pos.x - (texWidth * Xstart)
                elif self.pos.x < (-texWidth * .5):
                    Xstart = int((self.pos.x / texWidth) +.5)
                    Xstartpos = texWidth + self.pos.x + (texWidth * -Xstart)
                else:
                    Xstartpos = self.pos.x

                if (self.pos.x+delta.x) > (texWidth * .5):
                    Xhowmany = int(((self.pos.x+delta.x) / texWidth) -.5)
                    Xtogo = -texWidth + (self.pos.x+delta.x) - (texWidth * Xhowmany)

                elif (self.pos.x+delta.x) < (-texWidth * .5):
                    Xhowmany = int(((self.pos.x+delta.x) / texWidth) +.5)
                    Xtogo = texWidth + (self.pos.x+delta.x) + (texWidth * -Xhowmany)
                else:
                    Xtogo = (self.pos.x+delta.x)

                if -self.pos.y > (texHeight * .5):
                    Ystart = int((-self.pos.y / texHeight) -.5)
                    Ystartpos = -texHeight + -self.pos.y - (texHeight * Ystart)
                elif -self.pos.y < (-texHeight * .5):
                    Ystart = int((-self.pos.y / texHeight) +.5)
                    Ystartpos = texHeight + -self.pos.y + (texHeight * -Ystart)
                else:
                    Ystartpos = -self.pos.y

                if (-self.pos.y-delta.y) > (texHeight * .5):
                    Ystart = int(((-self.pos.y-delta.y) / texHeight) -.5)
                    Ytogo = -texHeight + (-self.pos.y-delta.y) - (texHeight * Ystart)
                elif (-self.pos.y-delta.y) < (-texHeight * .5):
                    Ystart = int(((-self.pos.y-delta.y) / texHeight) +.5)
                    Ytogo = texHeight + (-self.pos.y-delta.y) + (texHeight * -Ystart)
                else:
                    Ytogo = (-self.pos.y-delta.y)

                ### shows the true vertex position as you move it and in relation to each tile section of the texture.
                if editor.Root.currentcomponent.currentskin is not None:
                    s = "was " + ftoss(Xstartpos) + ", " + ftoss(Ystartpos) + " now " + ftoss(int(Xtogo)) + ", " + ftoss(int(Ytogo))
                else:
                    s = "was " + ftoss(self.pos.x) + ", " + ftoss(-self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + ", " + ftoss(-self.pos.y+delta.y)
            else:
                s = "was: " + vtoposhint(self.pos) + " now: " + vtoposhint(delta + self.pos)
        self.draghint = s

        return delta


    def ok(self, editor, undo, oldobjectslist, newobjectslist, view=None): # for LinRedHandle, the center handle.
        "Returned final lists of objects to convert back into Model mesh or Skin-view vertexes."

        from qbaseeditor import currentview
        if not isinstance(newobjectslist, quarkx.vector_type) and newobjectslist[0].name.endswith(":f"):
            undomsg = "editor-linear face movement"
            if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] is not None or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
                # This call handles the editor's selected faces extrusion functions.
                ConvertEditorFaceObject(editor, newobjectslist, currentview.flags, currentview, undomsg, 2)
            else:
                # This call handles a normal editor selected faces drag.
                ConvertEditorFaceObject(editor, newobjectslist, currentview.flags, currentview, undomsg)
        else:
            if currentview.info["viewname"] == "skinview":
                undomsg = "skin view-linear vertex movement"
                undo.exchange(oldobjectslist[0], newobjectslist[0])
                editor.ok(undo, undomsg)
                for view in editor.layout.views:
                    if view.viewmode == "tex":
                        view.invalidate(1)
            else:
                undomsg = "editor-linear vertex movement"
                if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] is not None or quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
                    # This call handles the editor's selected vertexes extrusion functions.
                    if str(newobjectslist) != str(quarkx.vect(0., 0., 0.)):
                        delta = newobjectslist
                        UpdateFramesVertexes(editor, delta, view, undomsg, 2)
                elif str(newobjectslist) != str(quarkx.vect(0., 0., 0.)):
                    # This call handles a normal editor selected vertexes drag.
                    delta = newobjectslist
                    UpdateFramesVertexes(editor, delta, view, undomsg, 0)


class LinSideHandle(LinearHandle): # for LinSideHandle
    "Linear Circle: handles at the sides for enlarge/shrink holding Ctrl key allows distortion/shearing."

    hint = "enlarge/shrink selection (Ctrl key = distort/shear selection)"

    def __init__(self, center, side, dir, mgr, firstone):
        pos1 = quarkx.vect(center.tuple[:dir] + (side.tuple[dir],) + center.tuple[dir+1:])
        LinearHandle.__init__(self, pos1, mgr)
        self.center = center - (pos1-center)
        self.dir = dir
        self.firstone = firstone
        self.inverse = side.tuple[dir] < center.tuple[dir]
        self.cursor = CR_LINEARV
        self.side = side
        self.oldverticespos = None
        self.newverticespos = None
        self.selvtxlist = None

    def draw(self, view, cv, draghandle=None): # for LinSideHandle
        from qbaseeditor import flagsmouse
        if flagsmouse == 528 or flagsmouse == 1040: return # RMB pressed or dragging to pan (scroll) in the view.

        if self.firstone:
            self.mgr.drawbox(view)   # Draws the full circle and all handles during drag and Ctrl key is NOT being held down.

        if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
            view.handles = []
            return

        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = MapColor("LinearHandleSides", SS_MODEL)
            cv.pencolor = MapColor("LinearHandleOutline", SS_MODEL)
            cv.ellipse(int(p.x)-5, int(p.y)-3, int(p.x)+5, int(p.y)+3)

    def buildmatrix(self, delta, g1, view): # for LinSideHandle
        editor = self.mgr.editor
        self.g1 = g1
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)

        if view.info["viewname"] == "skinview" or quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
            npos = self.pos+delta
            #normal = view.vector("Z").normalized
            dir = self.dir
            v = (npos - self.center) / abs(self.pos - self.center)
            if self.inverse:
                v = -v
            m = [quarkx.vect(1,0,0), quarkx.vect(0,1,0), quarkx.vect(0,0,1)]
            if self.g1:
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

        else:
            npos = self.pos+delta
            #normal = view.vector("Z").normalized
            dir = self.dir
            v = (npos - self.center) / abs(self.pos - self.center)
            if self.inverse:
                v = -v
            self.m = [quarkx.vect(1,0,0), quarkx.vect(0,1,0), quarkx.vect(0,0,1)]
            if self.g1:
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
            self.m[dir] = v

            return quarkx.matrix(tuple(self.m))

    def ok(self, editor, undo, oldobjectslist, newobjectslist, view=None): # for LinSideHandle
        "Returned final lists of objects to convert back into Model mesh or Skin-view vertexes."

        if view is not None and view.info['viewname'] != "skinview" and quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
            undomsg = "skin view-linear vertex distort/shear"
            UpdateFramesVertexes(editor, self.newverticespos, view, undomsg, 3)
        else:
            from qbaseeditor import currentview
            if newobjectslist[0].name.endswith(":f"):
                undomsg = "editor-linear face distort/shear"
                ConvertEditorFaceObject(editor, newobjectslist, currentview.flags, currentview, undomsg)
            else:
                if currentview.info["viewname"] == "skinview":
                    undomsg = "skin view-linear vertex distort/shear"
                    undo.exchange(oldobjectslist[0], newobjectslist[0])
                    editor.ok(undo, undomsg)
                    for view in editor.layout.views:
                        if view.viewmode == "tex":
                            view.invalidate(1)


class LinCornerHandle(LinearHandle):
    "Linear Circle: handles at the corners for rotation/zooming."

    hint = "rotate selection (Ctrl key = scale selection)"

    def __init__(self, center, pos1, mgr, realpoint=None):
        LinearHandle.__init__(self, pos1, mgr)
        if realpoint is None:
            self.pos0 = pos1
        else:
            self.pos0 = realpoint
        self.center = center - (pos1-center)
        self.cursor = CR_CROSSH
        self.m = None
        self.diff = 1.0  # pure rotation
        self.oldverticespos = None
        self.newverticespos = None
        self.selvtxlist = None

    def draw(self, view, cv, draghandle=None): # for LinCornerHandle
        from qbaseeditor import flagsmouse
        if flagsmouse == 528 or flagsmouse == 1040: return # RMB pressed or dragging to pan (scroll) in the view.

        if view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
            view.handles = []
            return
        elif view.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
            view.handles = []
            return

        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = MapColor("LinearHandleCorners", SS_MODEL)
            cv.pencolor = MapColor("LinearHandleOutline", SS_MODEL)
            cv.polygon([(int(p.x)-3,int(p.y)), (int(p.x),int(p.y)-3), (int(p.x)+3,int(p.y)), (int(p.x),int(p.y)+3)])

    def buildmatrix(self, delta, g1, view): # for LinCornerHandle
        editor = self.mgr.editor
        self.g1 = g1
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)
        normal = view.vector("Z").normalized
        if view.info["viewname"] == "skinview" or quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
            ### Rotation section.
            if self.g1 == 0:
                rotationorigin = self.mgr.center
                oldpos = self.pos - rotationorigin
                newpos = (self.pos + delta) - rotationorigin
                oldpos = oldpos - normal*(normal*oldpos)
                newpos = newpos - normal*(normal*newpos)
                self.m = qhandles.UserRotationMatrix(normal, newpos, oldpos, 0)
                if self.m is None:
                    return
            ### Scaling section.
            else:
                texp4 = self.pos-self.mgr.center
                texp4 = texp4 - normal*(normal*texp4)
                npos = self.pos + delta
                npos = npos-self.mgr.center
                npos = npos - normal*(normal*npos)
                v = self.mgr.center
                if self.m is None:
                    self.m = quarkx.matrix(quarkx.vect(1, 0, 0), quarkx.vect(0, 1, 0), quarkx.vect(0, 0, 1))  # Forces pure scaling.
                self.diff = abs(npos) / abs(texp4)
            ### Drag Hint section.
            if view.info['type'] == 'YZ':
                rotate = math.acos(self.m[1,1])*180.0/math.pi
            else:
                rotate = math.acos(self.m[0,0])*180.0/math.pi
            scaling = 100.0 * self.diff
            self.draghint = "rotate %d deg.   scale %d %%" % (rotate, scaling)
            return self.m * self.diff
        else:
            ### Rotation section.
            if self.g1 == 0:
                rotationorigin = self.mgr.center
                oldpos = self.pos - rotationorigin
                newpos = (self.pos + delta) - rotationorigin
                oldpos = oldpos - normal*(normal*oldpos)
                newpos = newpos - normal*(normal*newpos)
                self.m = qhandles.UserRotationMatrix(normal, newpos, oldpos, 0)
            ### Scaling section.
            else:
                texp4 = self.pos-self.mgr.center
                texp4 = texp4 - normal*(normal*texp4)
                npos = self.pos + delta
                npos = npos-self.mgr.center
                npos = npos - normal*(normal*npos)
                v = self.mgr.center
                if self.m is None:
                    self.m = quarkx.matrix(quarkx.vect(1, 0, 0), quarkx.vect(0, 1, 0), quarkx.vect(0, 0, 1))  # Forces pure scaling.
                self.diff = abs(npos) / abs(texp4)
            ### Drag Hint section.
            if self.m is None:
                self.m = quarkx.matrix(quarkx.vect(1, 0, 0), quarkx.vect(0, 1, 0), quarkx.vect(0, 0, 1))
            if view.info['type'] == 'YZ':
                rotate = math.acos(self.m[1,1])*180.0/math.pi
            else:
                rotate = math.acos(self.m[0,0])*180.0/math.pi
            scaling = 100.0 * self.diff
            self.draghint = "rotate %d deg.   scale %d %%" % (rotate, scaling)

            return self.m * self.diff


    def ok(self, editor, undo, oldobjectslist, newobjectslist, view=None): # for LinCornerHandle
        "Returned final lists of objects to convert back into Model mesh or Skin-view vertexes."

        if view is not None and view.info['viewname'] != "skinview" and quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
            undomsg = "editor-linear vertex rotate/scaling"
            UpdateFramesVertexes(editor, self.newverticespos, view, undomsg, 3)
        else:
            from qbaseeditor import currentview
            if newobjectslist[0].name.endswith(":f"):
                undomsg = "editor-linear face rotate/scaling"
                ConvertEditorFaceObject(editor, newobjectslist, currentview.flags, currentview, undomsg)
            else:
                if currentview.info["viewname"] == "skinview":
                    undomsg = "skin view-linear vertex rotate/scaling"
                    undo.exchange(oldobjectslist[0], newobjectslist[0])
                    editor.ok(undo, undomsg)
                    for view in editor.layout.views:
                        if view.viewmode == "tex":
                            view.invalidate(1)



class ModelEditorBoneHandlesManager:
    "Bone Handle manager. This is the class called to manage and build"
    "the Bone Handles by calling its other related classes below this one."

    def __init__(self, editor, color, bbox, bone):
        self.editor = editor
        self.color = color # The start or end handle color, which ever is being called.
        self.bbox = bbox # The min and max size of the handle linear circle, set in mdlentities.py, handlesopt function.
        self.bone = bone # The bone object itself.
        bmin, bmax = bbox
        bmin1 = bmax1 = ()
        for dir in "xyz":
            cmin = getattr(bmin, dir)
            cmax = getattr(bmax, dir)
            diff = cmax-cmin
            bmin1 = bmin1 + (cmin,)
            bmax1 = bmax1 + (cmax,)
        self.bmin = quarkx.vect(bmin1)
        self.bmax = quarkx.vect(bmax1)
        self.list = [bone]

    def BuildHandles(self, center=None, minimal=None): # for ModelEditorBoneHandlesManager
        "Build a list of handles to put around the bone handle."

        if center is None:
            center = self.bone.position

        self.center = center # The handle's center position with any "offset" applied in mdlentities.py, handlesopt function.
        if minimal is not None:
            view, grid = minimal
            closeto = view.space(view.proj(self.center) + quarkx.vect(-99,-99,0))
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
        try:
            handle_scale = self.bone.dictspec['scale'][0]
        except:
            handle_scale = 1.0

        from math import sqrt
        bonenormallength = quarkx.setupsubset(SS_MODEL,"Building")['RotationHandleLength'][0]
        h.append(BoneCornerHandle(center, center + quarkx.matrix((sqrt(2)/2, -sqrt(2)/2, 0), (sqrt(2)/2, sqrt(2)/2, 0), (0, 0, 1)) * quarkx.vect(bonenormallength * handle_scale, 0, 0), self, self.bone))
        return h + [BoneCenterHandle(center, self, self.bone)]

    def drawbox(self, view):
        return


#
# Linear Bone Drag Handle Circle's handles.
#

class BoneHandle(qhandles.GenericHandle):
    "Bone Circle handles."

    def __init__(self, pos, mgr, bone):
        qhandles.GenericHandle.__init__(self, pos)
        self.mgr = mgr    # a ModelEditorBoneHandlesManager instance
        self.bone = bone
        self.attachedbones = None
        self.newverticespos = None

    #
    # This function finds any attached bones that should also be dragged
    # and stationary bones that should not be included in the drag.
    # It also checks if a frame is selected if any of the drag bones have vertexes assigned to them.
    # If so, and a frame is not selected then it stops the drag from occurring.
    # "option" is set to 1 for automatic drags, such as Keyframe drags, to take place.
    #
    def start_drag(self, view, x, y, option=0):
        editor = self.mgr.editor
        if quarkx.setupsubset(SS_MODEL, "Options")['Drag_Bones_Only'] == "1":
            view.handles = []
        bones = editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone') # Get all bones.
        if self.attachedbones is None:
            self.attachedbones = []
            connectedlist = {}
            connectedlist[self.bone] = 1 #Bone counts as connected to itself

            if (isinstance(self, BoneCornerHandle)) or (self.mgr.editor.layout.explorer.sellist[0] != self.bone and isinstance(self, BoneCenterHandle)):
                def isconnected(bone):
                    if bone.dictspec['parent_name'] == "None":
                        connectedlist[bone] = -1 #Not connected
                    else:
                        for parentbone in bones:
                            if parentbone.name == bone.dictspec['parent_name']:
                                # found parentbone
                                break
                        if not connectedlist.has_key(parentbone):
                            isconnected(parentbone) #Recursive call
                        connectedlist[bone] = connectedlist[parentbone]

                for bone in bones:
                    if not connectedlist.has_key(bone):
                        isconnected(bone)
                for bone in bones:
                    if bone is self.bone:
                        #Skip own bone
                        continue
                    if self.mgr.editor.layout.explorer.sellist[0] == self.bone and bone.dictspec['parent_name'] != self.bone.name:
                        continue
                    if connectedlist[bone] == 1: #Connected
                        self.attachedbones = self.attachedbones + [bone]

        if self.newverticespos is None:
            self.newverticespos = {}
            for bone in [self.bone] + self.attachedbones:
                oldvertices = bone.vtxlist
                for compname in oldvertices.keys():
                    if not self.newverticespos.has_key(compname):
                        comp = editor.Root.dictitems[compname]
                        self.newverticespos[compname] = comp.currentframe.vertices
        # Gets all bones that are stationary, not being moved
        foundframe = 0
        for item in editor.layout.explorer.sellist:
            if item.type == ":mf":
                foundframe = 1
                break
        self.fixedbones = []
        for bone in bones:
            if bone in self.attachedbones:
                if len(bone.vtxlist) != 0 and foundframe == 0:
                    self.attachedbones = None
                    self.fixedbones = []
                    return
                else:
                    continue
            if bone == self.bone and len(bone.vtxlist) != 0 and foundframe == 0:
                self.attachedbones = None
                self.fixedbones = []
                return
            self.fixedbones = self.fixedbones + [bone]

    def sortbonelist(self, oldobjectslist, newobjectslist):
        # Sort the list to stop re-arranging in the tree-view
        compbones = self.mgr.editor.Root.findallsubitems("", ':bone')      # get all bones
        tempoldlist = []
        if newobjectslist is None:
            tempnewlist = None
        else:
            tempnewlist = []
        for bone in compbones:
            try:
                i = oldobjectslist.index(bone)
            except ValueError:
                pass
            else:
                tempoldlist = tempoldlist + [oldobjectslist[i]]
                if newobjectslist is not None:
                    tempnewlist = tempnewlist + [newobjectslist[i]]
        for i in range(len(oldobjectslist)):
            if not oldobjectslist[i] in tempoldlist:
                tempoldlist = tempoldlist + [oldobjectslist[i]]
                if newobjectslist is not None:
                    tempnewlist = tempnewlist + [newobjectslist[i]]
        return tempoldlist, tempnewlist

    def ok(self, editor, undo, old, new): # for BoneHandle
        undomsg = "bone dragged"
        undo = quarkx.action()
        oldskelgroup = editor.Root.dictitems['Skeleton:bg']
        newskelgroup = boneundo(editor, old, new)
        undo.exchange(oldskelgroup, newskelgroup)
        newbones = newskelgroup.findallsubitems("", ':bone')    # get all bones
        for parent in newbones:
            for old_bone in newbones:
                if old_bone.dictspec.has_key("parent_name") and old_bone.dictspec['parent_name'] == parent.name:
                    new_bone = old_bone.copy()
                    new_bone['bone_length'] = (new_bone.position - parent.position).tuple
                    undo.exchange(old_bone, new_bone)
        if self.newverticespos is not None:
            editor = self.mgr.editor
            for mesh in editor.Root.subitems:
                if not (mesh.type == ":mc"):
                    continue
                meshname = mesh.name
                if not (meshname in self.newverticespos.keys()):
                    continue
                oldmesh = editor.Root.dictitems[meshname]
                newmesh = oldmesh.copy()
                newmesh.currentframe = newmesh.dictitems["Frames:fg"].dictitems[oldmesh.currentframe.name]
                newmesh.currentframe.vertices = self.newverticespos[meshname]
                undo.exchange(oldmesh, newmesh)
        framename = editor.Root.currentcomponent.currentframe.name
        for bone in new:
            if editor.ModelComponentList['bonelist'].has_key(bone.name) and editor.ModelComponentList['bonelist'][bone.name].has_key('frames') and editor.ModelComponentList['bonelist'][bone.name]['frames'].has_key(framename):
                editor.ModelComponentList['bonelist'][bone.name]['frames'][framename]['position'] = bone.position.tuple
                if isinstance(self, BoneCornerHandle):
                    editor.ModelComponentList['bonelist'][bone.name]['frames'][framename]['rotmatrix'] = bone.rotmatrix.tuple
        editor.ok(undo, undomsg)

def DrawBoneHandle(p, cv, color, scale, handle_scale, view=None):
    if view is not None:
        if (view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] == "1") or (view.info["viewname"] == "3Dwindow" and view.info['type'] == "3D" and quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] == "1"):
            # Correct scale for true 3D view, as scale is always 1.0 in those views
            scale = 10.0
    bonehalfsize = 1.0*scale*handle_scale
    cv.pencolor = color
    cv.ellipse(int(p.x-bonehalfsize), int(p.y-bonehalfsize), int(p.x+bonehalfsize), int(p.y+bonehalfsize))
    cv.line(int(p.x-bonehalfsize), int(p.y), int(p.x+bonehalfsize), int(p.y))
    cv.line(int(p.x), int(p.y-bonehalfsize), int(p.x), int(p.y+bonehalfsize))

def DrawBoneLine(p, p2, cv, color, scale, handle_scale, view=None):
    if view is not None:
        if (view.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] == "1") or (view.info["viewname"] == "3Dwindow" and view.info['type'] == "3D" and quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] == "1"):
            # Correct scale for true 3D view, as scale is always 1.0 in those views
            scale = 10.0
    bonehalfsize = 1.0*scale*handle_scale
    cv.pencolor = color
    cv.line(int(p2.x), int(p2.y-bonehalfsize), int(p.x), int(p.y))
    cv.line(int(p2.x+bonehalfsize), int(p2.y), int(p.x), int(p.y))
    cv.line(int(p2.x), int(p2.y+bonehalfsize), int(p.x), int(p.y))
    cv.line(int(p2.x-bonehalfsize), int(p2.y), int(p.x), int(p.y))


class BoneCenterHandle(BoneHandle):
    "Center Bone Handle, handle at the center."

    size = (3,3)
    def __init__(self, pos, mgr, bone):
        BoneHandle.__init__(self, pos, mgr, bone)
        self.cursor = CR_CROSSH
        self.undomsg = "bone joint move"

        if bone is None:
            self.component = None
        else:
            self.component = bone.dictspec['component']
        self.dict = {}


    def extrasmenu(self, editor, bone=None, view=None):
        "This is the Bone's extras menu for items that can be placed on other menus."

        def StructureBones(m, editor=editor, bone=bone):
            bones = editor.Root.findallsubitems("", ':bone')  # get all bones
            parentbones = bones
            undo = quarkx.action()
            undo_msg = "structured bones"
            for parent in parentbones:
                for bone in bones:
                    if bone.dictspec['parent_name'] != "None":
                        if parent.name == bone.dictspec['parent_name']:
                            undo.move(bone, parent)
            editor.ok(undo, undo_msg)
            editor.layout.explorer.invalidate()

        def ExtractBones(m, editor=editor, bone=bone):
            bones = editor.Root.findallsubitems("", ':bone')  # get all bones
            skeletongroup = editor.Root.dictitems['Skeleton:bg']
            undo = quarkx.action()
            undo_msg = "extracted bones"
            for bone in bones:
                undo.move(bone, skeletongroup)
            editor.ok(undo, undo_msg)
            editor.layout.explorer.invalidate()

        structure_bones = qmenu.item("Structure Bones", StructureBones, "|Structure Bones:\n\nWhen clicked this function will place all bones\ninside their 'parent' bones in the 'tree-view'.|intro.modeleditor.editelements.html#specificsettings")
        extract_bones = qmenu.item("Extract Bones", ExtractBones, "|Extract Bones:\n\nWhen clicked this function will move all bones\noutside of their 'parent' bones in the 'tree-view'.|intro.modeleditor.editelements.html#specificsettings")

        bones = editor.Root.findallsubitems("", ':bone')  # get all bones
        if len(bones) == 0:
            structure_bones.state = qmenu.disabled
            extract_bones.state = qmenu.disabled

        menulist = [structure_bones, extract_bones]
        return menulist


    def menu(self, editor, view): # for BoneCenterHandle

        def add_bone_control_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            add_bone_control(editor, self.bone)

        def remove_bone_control_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            remove_bone_control(editor, self.bone)

        def CalcBoneScaleValue(bone, parent_bone_scale):
            scale = 1.0
            if abs(bone.dictspec['bone_length'][0]) > abs(bone.dictspec['bone_length'][1]):
                if  abs(bone.dictspec['bone_length'][0]) > abs(bone.dictspec['bone_length'][2]):
                    testscale = abs(bone.dictspec['bone_length'][0])
                else:
                    testscale = abs(bone.dictspec['bone_length'][2])
            else:
                if  abs(bone.dictspec['bone_length'][1]) > abs(bone.dictspec['bone_length'][2]):
                    testscale = abs(bone.dictspec['bone_length'][1])
                else:
                    testscale = abs(bone.dictspec['bone_length'][2])
            if testscale < 8:
                scale = scale - (testscale * .08)

            if scale < 0.1:
                scale = 0.1
            elif scale > parent_bone_scale:
                scale = parent_bone_scale
            return scale

        def CalcBoneScale(bone_index, bonelist, bones, new_scales):
            bone = bonelist[bone_index]
            if bone.dictspec['parent_name'] == 'None':
                # Bone has no parent. (Poor orphaned bone!)
                new_scales[bone_index] = bone.dictspec['scale'][0]
            else:
                parent_bone_index = -1
                for bone_index2 in range(len(bonelist)):
                    bone2 = bonelist[bone_index2]
                    if bone2.name == bone.dictspec['parent_name']:
                        # Found it!
                        parent_bone_index = bone_index2
                        break
                if parent_bone_index == -1:
                    # Parent bone is not in bonelist. Use the original one.
                    parent_bone = None
                    for bone_index2 in range(len(bones)):
                        bone2 = bones[bone_index2]
                        if bone2.name == bone.dictspec['parent_name']:
                            # Found it!
                            parent_bone = bone2
                            break
                    new_scales[bone_index] = CalcBoneScaleValue(bone, parent_bone.dictspec['scale'][0])
                else:
                    # Parent bone is in bonelist.
                    parent_bone = bonelist[parent_bone_index]
                    if new_scales[parent_bone_index] is None:
                        CalcBoneScale(parent_bone_index, bonelist, bones, new_scales)
                    new_scales[bone_index] = CalcBoneScaleValue(bone, new_scales[parent_bone_index])
            return

        def ScaleSelHandlesClick(m, self=self, editor=editor, view=view):
            bonelist = []
            bones = editor.Root.findallsubitems("", ':bone')  # get all bones

            for item in editor.layout.explorer.sellist:
                if item.type == ":bone" and not item in bonelist:
                    bonelist = addtolist(bonelist, item)

            new_scales = []
            for bone in bonelist:
                new_scales = new_scales + [None]

            bone_index = 0
            while bone_index < len(bonelist):
                if new_scales[bone_index] == None:
                    CalcBoneScale(bone_index, bonelist, bones, new_scales)
                bone_index = bone_index + 1

            undo = quarkx.action()
            undo_msg = "sel bone handle scaling"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new_bone['scale'] = (new_scales[bone_index],) # Written this way to store it as a tuple.
                new = new + [new_bone]
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def ResetSelHandleScalesClick(m, self=self, editor=editor, view=view):
            bonelist = []
            bones = editor.Root.findallsubitems("", ':bone')  # get all bones

            for item in editor.layout.explorer.sellist:
                if item.type == ":bone" and not item in bonelist:
                    bonelist = addtolist(bonelist, item)
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new = new + [new_bone]

            for bone in new:
                if bone.dictspec.has_key("org_scale"):
                    bone['scale'] = bone.dictspec['org_scale']
                else:
                    bone['scale'] = (1.0,) # Written this way to store it as a tuple.

            undo = quarkx.action()
            undo_msg = "sel bone handle scaling reset"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def SetSelHandleScalesTo1Click(m, self=self, editor=editor, view=view):
            bonelist = []
            bones = editor.Root.findallsubitems("", ':bone')  # get all bones

            for item in editor.layout.explorer.sellist:
                if item.type == ":bone" and not item in bonelist:
                    bonelist = addtolist(bonelist, item)
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new = new + [new_bone]

            for bone in new:
                bone['scale'] = (1.0,) # Written this way to store it as a tuple.

            undo = quarkx.action()
            undo_msg = "sel bone handle scales set to 1"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def SaveSelHandleScalesClick(m, self=self, editor=editor, view=view):
            bonelist = []
            bones = editor.Root.findallsubitems("", ':bone')  # get all bones

            for item in editor.layout.explorer.sellist:
                if item.type == ":bone" and not item in bonelist:
                    bonelist = addtolist(bonelist, item)
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new = new + [new_bone]

            for bone in new:
                bone['org_scale'] = bone.dictspec['scale']

            undo = quarkx.action()
            undo_msg = "sel handle scales saved"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def ScaleHandlesClick(m, self=self, editor=editor, view=view):
            bonelist = bones = editor.Root.findallsubitems("", ':bone')  # get all bones

            new_scales = []
            for bone in bonelist:
                new_scales = new_scales + [None]

            bone_index = 0
            while bone_index < len(bonelist):
                if new_scales[bone_index] == None:
                    CalcBoneScale(bone_index, bonelist, bones, new_scales)
                bone_index = bone_index + 1

            undo = quarkx.action()
            undo_msg = "all bone handles scaled"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new_bone['scale'] = (new_scales[bone_index],) # Written this way to store it as a tuple.
                new = new + [new_bone]
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def ResetHandleScalesClick(m, self=self, editor=editor, view=view):
            bonelist = bones = editor.Root.findallsubitems("", ':bone')  # get all bones
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new = new + [new_bone]

            for bone in new:
                if bone.dictspec.has_key("org_scale"):
                    bone['scale'] = bone.dictspec['org_scale']
                else:
                    bone['scale'] = (1.0,) # Written this way to store it as a tuple.

            undo = quarkx.action()
            undo_msg = "all bone handle scaling reset"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def SetHandleScalesTo1Click(m, self=self, editor=editor, view=view):
            bonelist = bones = editor.Root.findallsubitems("", ':bone')  # get all bones
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new = new + [new_bone]

            for bone in new:
                bone['scale'] = (1.0,) # Written this way to store it as a tuple.

            undo = quarkx.action()
            undo_msg = "all bone handle scales set to 1"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def SaveHandleScalesClick(m, self=self, editor=editor, view=view):
            bonelist = bones = editor.Root.findallsubitems("", ':bone')  # get all bones
            old = bonelist
            new = []
            for bone_index in range(len(old)):
                bone = old[bone_index]
                new_bone = bone.copy()
                new = new + [new_bone]

            for bone in new:
                bone['org_scale'] = bone.dictspec['scale']

            undo = quarkx.action()
            undo_msg = "all bone handle scaling saved"
            oldskelgroup = editor.Root.dictitems['Skeleton:bg']
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
            editor.ok(undo, undo_msg)

        def IndividualBonesSel(m, self=self, editor=editor, view=view):
            if not MdlOption("IndividualBonesSel"):
                quarkx.setupsubset(SS_MODEL, "Options")['IndividualBonesSel'] = "1"
            else:
                quarkx.setupsubset(SS_MODEL, "Options")['IndividualBonesSel'] = None

        def handlescalemenu(m):
            scale_sel_handles = qmenu.item("Scale selected bone handles", ScaleSelHandlesClick, "|Scale selected bone handles:\n\nIf this menu item is checked, all bones that are currently selected, and their attached bones, will have their handles set to different scale sizes for easer access.\n\nSee 'Individual Bones Selection' below for additional option.|intro.modeleditor.rmbmenus.html#handlescaling")
            scale_sel_handles.state = qmenu.disabled
            reset_sel_handle_scales = qmenu.item("Reset selected handles to org. scale", ResetSelHandleScalesClick, "|Reset selected bone handles to org. scale:\n\nIf this menu item is checked, all bones that are currently selected, and their attached bones, will have their handles reset to their original imported or saved scale sizes.\n\nSee 'Individual Bones Selection' below for additional option.|intro.modeleditor.rmbmenus.html#handlescaling")
            reset_sel_handle_scales.state = qmenu.disabled
            set_sel_handle_scales_to1 = qmenu.item("Set selected bone handles to 1.0", SetSelHandleScalesTo1Click, "|Set selected bone handles to 1.0:\n\nIf this menu item is checked, all bones that are currently selected, and their attached bones, will have their handles reset to the default scale size of 1.0.\n\nSee 'Individual Bones Selection' below for additional option.|intro.modeleditor.rmbmenus.html#handlescaling")
            set_sel_handle_scales_to1.state = qmenu.disabled
            save_sel_handle_scales = qmenu.item("Save selected handle scales", SaveSelHandleScalesClick, "|Save selected handle scales:\n\nIf this menu item is checked, all bones that are currently selected, and their attached bones, will have their handles scale sizes saved, becoming their original setting.\n\nSee 'Individual Bones Selection' below for additional option.|intro.modeleditor.rmbmenus.html#handlescaling")
            save_sel_handle_scales.state = qmenu.disabled
            scale_handles = qmenu.item("Scale all bone handles", ScaleHandlesClick, "|Scale all bone handles:\n\nIf this menu item is checked, all bones will have their handles set to different scale sizes for easer access.|intro.modeleditor.rmbmenus.html#handlescaling")
            reset_handle_scales = qmenu.item("Reset all handles to org. scale", ResetHandleScalesClick, "|Reset all handles to org. scale:\n\nIf this menu item is checked, all bones will have their handles reset to their original imported or saved scale sizes.|intro.modeleditor.rmbmenus.html#handlescaling")
            set_handle_scales_to1 = qmenu.item("Set all handles to 1.0", SetHandleScalesTo1Click, "|Set all handles to 1.0:\n\nIf this menu item is checked, all bones will have their handles reset to the default scale size of 1.0.|intro.modeleditor.rmbmenus.html#handlescaling")
            save_handle_scales = qmenu.item("Save all handle scales", SaveHandleScalesClick, "|Save all handle scales:\n\nIf this menu item is checked, all bones will have their handles scale sizes saved, becoming their original setting.|intro.modeleditor.rmbmenus.html#handlescaling")

            for item in editor.layout.explorer.sellist:
                if item.type == ":bone":
                    scale_sel_handles.state = qmenu.normal
                    reset_sel_handle_scales.state = qmenu.normal
                    set_sel_handle_scales_to1.state = qmenu.normal
                    save_sel_handle_scales.state = qmenu.normal
                    break

            menulist = [scale_sel_handles, reset_sel_handle_scales, set_sel_handle_scales_to1, qmenu.sep, save_sel_handle_scales, qmenu.sep, scale_handles, reset_handle_scales, set_handle_scales_to1, qmenu.sep, save_handle_scales]
            return menulist

        def force_to_grid_click(m, self=self, editor=editor, view=view):
            sellist = editor.layout.explorer.sellist
            if not self.bone in sellist and not editor.Root.dictitems['Skeleton:bg'] in sellist:
                quarkx.beep() # Makes the computer "Beep" once.
                quarkx.msgbox("Invalid Action\n\nTo use this function you must\neither select the 'Skeleton' folder\nor the specific bone itself in that folder.", qutils.MT_ERROR, qutils.MB_OK)
                return
            x = self.pos.x
            y = self.pos.y
            self.start_drag(view, x, y)
            if self.attachedbones is None:
                self.attachedbones = []
            v2 = qhandles.aligntogrid(self.pos, 1)
            self.Action(editor, self.pos, v2, 0, view, Strings[560])

        def add_bone_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            addbone(editor, self.component, self.pos)

        def continue_bones_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            continue_bone(editor, self.bone, self.pos)

        def attach_bone1to2_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            if self.bone is None:
                bone = editor.layout.explorer.sellist[0]
            else:
                bone = self.bone
            attach_bone1to2(editor, bone, editor.layout.explorer.sellist[1])

        def attach_bone2to1_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            if self.bone is None:
                bone = editor.layout.explorer.sellist[0]
            else:
                bone = self.bone
            attach_bone2to1(editor, bone, editor.layout.explorer.sellist[1])

        def detach_bones_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            if self.bone is None:
                bone = editor.layout.explorer.sellist[0]
            else:
                bone = self.bone
            detach_bone(editor, bone)

        def align__bone1to2_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            if self.bone is None:
                bone = editor.layout.explorer.sellist[0]
            else:
                bone = self.bone
            align__bone1to2(editor, bone, editor.layout.explorer.sellist[1])

        def align__bone2to1_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            if self.bone is None:
                bone = editor.layout.explorer.sellist[0]
            else:
                bone = self.bone
            align__bone2to1(editor, bone, editor.layout.explorer.sellist[1])

        def assign_release_vertices_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            if self.bone is None:
                bone = editor.layout.explorer.sellist[0]
            else:
                bone = self.bone
            vtxsellist = map(lambda x: x, editor.ModelVertexSelList)
            comp = item.parent.parent
            assign_release_vertices(editor, bone, comp, vtxsellist)

        def set_handle_position_click(m, self=self, editor=editor, view=view):
            import mdlmgr
            mdlmgr.savefacesel = 1
            comp = editor.Root.currentcomponent
            old_vertices = self.bone.vtx_pos
            vtx_pos = []
            frames = editor.Root.dictitems[comp.name].dictitems['Frames:fg'].subitems
            frame = frames[editor.bone_frame]
            for vtx in range(len(editor.ModelVertexSelList)):
                vtx_pos = vtx_pos + [editor.ModelVertexSelList[vtx]]
            vtx_pos.sort()
            vtxs = len(vtx_pos)
            old_vertices[comp.name] = vtx_pos
            self.bone.vtx_pos = old_vertices
            for frame2 in frames:
                vertices = frame2.vertices
                vtxpos = quarkx.vect(0.0, 0.0, 0.0)
                for vtx in vtx_pos:
                    try:
                        vtxpos = vtxpos + vertices[vtx]
                    except:
                        return
                vtxpos = vtxpos/ float(vtxs)
                editor.ModelComponentList['bonelist'][self.bone.name]['frames'][frame2.name]['position'] = (vtxpos + quarkx.vect(self.bone.dictspec['draw_offset'])).tuple
                if frame2.name == frame.name:
                    self.bone.position = vtxpos + quarkx.vect(self.bone.dictspec['draw_offset'])
                    self.bone['position'] = self.bone.position.tuple
                    self.bone['component'] = comp.name
            Update_Editor_Views(editor)
            editor.layout.mpp.resetpage()

        def ShowBones(m, self=self, editor=editor, view=view):
            quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] = None
            SB1.state = qmenu.disabled
            HB1.state = qmenu.normal
            mdlutils.Update_Editor_Views(editor)
            editor.layout.explorer.invalidate()

        def HideBones(m, self=self, editor=editor, view=view):
            quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] = "1"
            SB1.state = qmenu.normal
            HB1.state = qmenu.disabled
            mdlutils.Update_Editor_Views(editor)
            editor.layout.explorer.invalidate()

        def select_handle_vertexes_click(m, self=self, editor=editor, view=view):
            sel_comp = m.text.split("for ")[1] + ":mc"
            comp = editor.Root.currentcomponent
            compchanged = None
            frame = comp.currentframe
            if (sel_comp != comp.name) or (len(editor.layout.explorer.sellist) == 0):
                for item in range(len(comp.dictitems['Frames:fg'].subitems)):
                    if comp.dictitems['Frames:fg'].subitems[item] == frame:
                        framenbr = item
                comp = editor.Root.dictitems[sel_comp]
                editor.layout.explorer.sellist = [self.bone, comp.dictitems['Frames:fg'].subitems[framenbr]]
                frame = editor.layout.explorer.sellist[1]
                editor.layout.selchange()
                compchanged = 1
            handle = self.bone.dictspec['position']
            if not editor.Root.dictitems['Skeleton:bg'] in editor.layout.explorer.sellist:
                editor.layout.explorer.sellist = [self.bone, frame]
                editor.layout.selchange()
                compchanged = 1
                editor.layout.explorer.expand(self.bone.parent)
            editor.layout.explorer.expand(comp)
            editor.layout.explorer.expand(frame.parent)
            bone_vtxlist = []
            vtxlist = self.bone.vtxlist[sel_comp]
            for vtx in vtxlist:
                bone_vtxlist = bone_vtxlist + [vtx]
            editor.ModelVertexSelList = bone_vtxlist
            if compchanged is None:
                Update_Editor_Views(editor)

        def select_handle_pos_vertexes_click(m, self=self, editor=editor, view=view):
            sel_comp = self.bone.dictspec['component']
            comp = editor.Root.currentcomponent
            compchanged = None
            frame = comp.currentframe
            if (sel_comp != comp.name) or (len(editor.layout.explorer.sellist) == 0):
                for item in range(len(comp.dictitems['Frames:fg'].subitems)):
                    if comp.dictitems['Frames:fg'].subitems[item] == frame:
                        framenbr = item
                comp = editor.Root.dictitems[sel_comp]
                editor.layout.explorer.sellist = [self.bone, comp.dictitems['Frames:fg'].subitems[framenbr]]
                frame = editor.layout.explorer.sellist[1]
                editor.layout.selchange()
                compchanged = 1
            handle = self.bone.dictspec['position']
            if not editor.Root.dictitems['Skeleton:bg'] in editor.layout.explorer.sellist:
                editor.layout.explorer.sellist = [self.bone, frame]
                editor.layout.selchange()
                compchanged = 1
                editor.layout.explorer.expand(self.bone.parent)
            editor.layout.explorer.expand(comp)
            editor.layout.explorer.expand(frame.parent)
            bone_vtxlist = []
            vtxlist = self.bone.vtx_pos[sel_comp]
            for vtx in vtxlist:
                bone_vtxlist = bone_vtxlist + [vtx]
            editor.ModelVertexSelList = bone_vtxlist
            if compchanged is None:
                Update_Editor_Views(editor)

        Forcetogrid = qmenu.item("&Force to grid", force_to_grid_click,"|Force to grid:\n\nThis will cause a bone's center handle to 'snap' to the nearest location on the editor's grid for the view that the RMB click was made in.|intro.modeleditor.rmbmenus.html#bonecommands")
        m = qmenu.item
        m.editor = editor
        if self.bone is None:
            bone_control = qmenu.item("Add \ Remove Control", None, "|Add \ Remove Control:\n\nThis will add or remove a single bone controle, connected to the bone handle when the RMB was clicked in the editor's view.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        else:
            bone_control = qmenu.item("Add &Bone Control", add_bone_control_click, "|Add Bone Control:\n\nThis will add a single bone controle, connected to the bone handle when the RMB was clicked in the editor's view.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
            for key in self.bone.dictspec.keys():
                if key.startswith("control_"):
                    bone_control = qmenu.item("&Remove Bone Control", remove_bone_control_click, "|Remove Bone Control:\n\nThis will remove a single bone controle, connected to the bone handle when the RMB was clicked in the editor's view.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                    break
        individual_bones_sel = qmenu.item("Individual Bones Selection", IndividualBonesSel, "|Individual Bones Selection:\n\n(Unless a function specifically deals with all bones)\n\nWhen this item is checked ONLY the INDIVIDUAL bone handles that are selected will be effected and NOT any sub-bones that are NOT specifically selected, Which IS the case if this is un-checked.|intro.modeleditor.editelements.html#specificsettings")
        individual_bones_sel.state = quarkx.setupsubset(SS_MODEL,"Options").getint("IndividualBonesSel")
        handlescalepop = qmenu.popup("Handle Scaling", handlescalemenu(m), None, "|Handle Scaling:\n\nThese functions deal with setting the scale size of the bone handles for better work size.", "intro.modeleditor.editelements.html#specificsettings")
        AddBone = qmenu.item("&Add Bone Here", add_bone_click, "|Add Bone Here:\n\nThis will add a single bone to the 'Skeleton' group.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        ContinueBones = qmenu.item("&Continue Bones", continue_bones_click, "|Continue Bones:\n\nThis will add a single bone, connected to the bone handle when the RMB was clicked, in the 'Skeleton' group.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        AttachBone1to2 = qmenu.item("Attach Bone &1 to 2", attach_bone1to2_click, "|Attach Bone 1 to 2:\n\nThis will attach the first selected bone in the tree-view to the second selected bone in the tree-view.|intro.modeleditor.rmbmenus.html#bonecommands")
        AttachBone2to1 = qmenu.item("Attach Bone &2 to 1", attach_bone2to1_click, "|Attach Bone 2 to 1:\n\nThis will attach the second selected bone in the tree-view to the first selected bone in the tree-view.|intro.modeleditor.rmbmenus.html#bonecommands")
        DetachBones = qmenu.item("&Detach Bones", detach_bones_click, "|Detach Bones:\n\nThis will detach two selected bones attached handles from one another in the 'Skeleton' group.|intro.modeleditor.rmbmenus.html#bonecommands")
        AssignReleaseVertices = qmenu.item("Assign \ Release &Vertices", assign_release_vertices_click, "|Assign \ Release Vertices:\n\nWhen vertices of a component are selected, RMB click on the center of a bone, then click this item to assign them to, or release them from ,that bone.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        AlignBone1to2 = qmenu.item("Align  Bone 1 to 2", align__bone1to2_click, "|Align Bone 1 to 2:\n\nThis will align the first selected bone in the tree-view to the second selected bone in the tree-view, but not attach them.|intro.modeleditor.rmbmenus.html#bonecommands")
        AlignBone2to1 = qmenu.item("Align  Bone 2 to 1", align__bone2to1_click, "|Align Bone 2 to 1:\n\nThis will align the second selected bone in the tree-view to the first selected bone in the tree-view, but not attach them.|intro.modeleditor.rmbmenus.html#bonecommands")
        SetHandlePosition = qmenu.item("Set Handle Position", set_handle_position_click, "|Set Handle Position:\n\nActive when one or more vertexes are selected that are assigned to that bone handle. Click this item to position and set that bone handle centered within those vertexes. An 'offset' can also be applied to this setting.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        SetHandlePosition.state = qmenu.disabled
        SB1 = qmenu.item("&Show Bones", ShowBones, "|Show Bones:\n\nThis allows all bones to be displayed in the editor's views.|intro.modeleditor.rmbmenus.html#bonecommands")
        HB1 = qmenu.item("&Hide Bones", HideBones, "|Hide Bones:\n\nThis stops all bones from being displayed in the editor's views.|intro.modeleditor.rmbmenus.html#bonecommands")
        SelectHandleVertexes = qmenu.item("Se&lect Handle Vertexes", select_handle_vertexes_click, "|Select (bone handle name) Vertexes:\n\nWhen the cursor is over a bone's Center handle with vertexes assigned to it, click this item to select all of them from that bone's handle.\n\nOr, if another handle is attached that has the vertexes assigned to it instead, then those are the vertexes that will be selected.\n\nIf no vertexes have been assigned to any handle at that location, then the menu item will show disabled.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        SelectHandleVertexes.state = qmenu.disabled
        SelectHandlePosVertexes = qmenu.item("Select Handle &Position Vertexes", select_handle_pos_vertexes_click, "|Select (bone handle name) handle position Vertexes:\n\nWhen the cursor is over a bone's Center handle with vertexes assigned to it, click this item to select the vertexes used to set that bone's handle position.\n\nOr, if another handle is attached that has the vertexes assigned to it instead, then those are the position vertexes for that handle that will be selected.\n\nIf no vertexes have been assigned to any handle at that location, then the menu item will show disabled.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
        SelectHandlePosVertexes.state = qmenu.disabled
        BoneExtras = self.extrasmenu(editor)
        BBoxBoneExtras = PolyHandle(None, None).bone_extras_menu(editor, self.bone)
        try:
            if (len(self.bone.vtxlist) != 0) and (len(editor.ModelVertexSelList) != 0) and (editor.Root.currentcomponent.name in self.bone.vtxlist.keys()):
                SetHandlePosition.state = qmenu.normal
        except:
            pass
        sel_vtx_list = [SelectHandleVertexes, SelectHandlePosVertexes]
        try:
            if isinstance(self, BoneCenterHandle):
                if len(self.bone.vtxlist) == 0:
                    pass
                else:
                    name = self.bone.shortname
                    sel_vtx_list = []
                    for comp in self.bone.vtxlist.keys():
                        compname = comp.split(":")[0]
                        sel_vtx_list = sel_vtx_list + [qmenu.item("Se&lect " + name + " Vertexes for " + compname, select_handle_vertexes_click, "|Select (bone handle name) Vertexes:\n\nWhen the cursor is over a bone's Center handle with vertexes assigned to it, click this item to select all of them from that bone's handle.\n\nOr, if another handle is attached that has the vertexes assigned to it instead, then those are the vertexes that will be selected.\n\nIf no vertexes have been assigned to any handle at that location, then the menu item will show disabled.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")]
                    SelectHandlePosVertexes = qmenu.item("Select " + name + " Handle &Position Vertexes", select_handle_pos_vertexes_click, "|Select (bone handle name) handle position Vertexes:\n\nWhen the cursor is over a bone's Center handle with vertexes assigned to it, click this item to select the vertexes used to set that bone's handle position.\n\nOr, if another handle is attached that has the vertexes assigned to it instead, then those are the position vertexes for that handle that will be selected.\n\nIf no vertexes have been assigned to any handle at that location, then the menu item will show disabled.\n\nClick on the InfoBase button below for more detail on its use.|intro.modeleditor.rmbmenus.html#bonecommands")
                    sel_vtx_list = sel_vtx_list + [SelectHandlePosVertexes]
                    if len(self.bone.vtx_pos) == 0:
                        SelectHandlePosVertexes.state = qmenu.disabled
        except:
            pass

        AddBone.state = qmenu.normal
        if self.bone is None:
            ContinueBones.state = qmenu.disabled
            bone_control.state = qmenu.disabled
            DetachBones.state = qmenu.disabled
            AssignReleaseVertices.state = qmenu.disabled
        else:
            ContinueBones.state = qmenu.normal
            bone_control.state = qmenu.normal
            if self.bone.dictspec['parent_name'] == "None":
                DetachBones.state = qmenu.disabled
            else:
                DetachBones.state = qmenu.normal
            if editor.ModelVertexSelList != [] and (":mf" in map(lambda x: x.type, editor.layout.explorer.sellist)):
                AssignReleaseVertices.state = qmenu.normal
            else:
                AssignReleaseVertices.state = qmenu.disabled

        if len(editor.layout.explorer.sellist) == 3:
            count = 0
            for item in editor.layout.explorer.sellist:
                if item.type == ":bg" and len(item.subitems) != 0:
                    count = count + 10
                if item.type == ":mf":
                    count = count + 5

        AttachBone1to2.state = qmenu.disabled
        AttachBone2to1.state = qmenu.disabled
        AlignBone1to2.state = qmenu.disabled
        AlignBone2to1.state = qmenu.disabled
        count = 0
        for item in editor.layout.explorer.sellist:
            if item.type == ":bone":
                count = count + 1
        if count == 2:
            AttachBone1to2.state = qmenu.normal
            AttachBone2to1.state = qmenu.normal
            AlignBone1to2.state = qmenu.normal
            AlignBone2to1.state = qmenu.normal

        if quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is not None:
            SB1.state = qmenu.normal
            HB1.state = qmenu.disabled
        else:
            SB1.state = qmenu.disabled
            HB1.state = qmenu.normal

        if not MdlOption("GridActive") or editor.gridstep <= 0:
            Forcetogrid.state = qmenu.disabled

        menu = [AddBone, ContinueBones, qmenu.sep, AttachBone1to2, AttachBone2to1, qmenu.sep, DetachBones, qmenu.sep, AlignBone1to2, AlignBone2to1, qmenu.sep] + BBoxBoneExtras + [qmenu.sep, AssignReleaseVertices, qmenu.sep, SetHandlePosition, qmenu.sep] + sel_vtx_list + [qmenu.sep, bone_control, qmenu.sep, individual_bones_sel, qmenu.sep, handlescalepop, qmenu.sep, SB1, HB1, qmenu.sep] + BoneExtras + [qmenu.sep, Forcetogrid]

        return menu


    def draw(self, view, cv, draghandle=None): # for BoneCenterHandle
        editor = self.mgr.editor
        from qbaseeditor import flagsmouse
        if quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is not None:
            return

        if isinstance(editor.dragobject, qhandles.ScrollViewDragObject) and flagsmouse == 1040:
            return # RMB pressed or dragging to pan (scroll) in the view.

        if view.info["viewname"] == "editors3Dview":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                return
        if view.info["viewname"] == "XY":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                return
        if view.info["viewname"] == "YZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                return
        if view.info["viewname"] == "XZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                return
        if view.info["viewname"] == "3Dwindow":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                return

        if self.pos is not None:
            p = view.proj(self.pos)
        else:
            p = view.proj(0,0,0)

        if p.visible:
            bonecount = 0
            for item in editor.layout.explorer.sellist:
                if item.type == ":bone" or item.type == ":mf":
                    bonecount = bonecount + 1
            cv.reset()
            cv.penwidth = 1
            cv.penstyle = PS_INSIDEFRAME
            cv.brushstyle = BS_CLEAR
            scale = view.scale()
            handle_scale = self.bone.dictspec['scale'][0]
            if (bonecount == 1 and self.bone in editor.layout.explorer.sellist) or (bonecount == len(editor.layout.explorer.sellist) and self.bone in editor.layout.explorer.sellist):
                line_color = MapColor("BoneHandles", SS_MODEL)
            else:
                line_color = MapColor("BoneLines", SS_MODEL)
            handle_color = self.bone.getint('_color')

            if self.bone.dictspec['parent_name'] != "None":
                parentbone = findbone(self.mgr.editor, self.bone.dictspec['parent_name'])
                parent_handle_scale = parentbone['scale'][0]
                p2 = view.proj(parentbone.position)
                DrawBoneLine(p, p2, cv, line_color, scale, parent_handle_scale, view)
            DrawBoneHandle(p, cv, handle_color, scale, handle_scale, view)

    def drawred(self, redimages, view, redcolor): # for BoneCenterHandle
        view.repaint()
        cv = view.canvas()
        cv.penwidth = 1
        cv.penstyle = PS_INSIDEFRAME
        cv.brushstyle = BS_CLEAR
        scale = view.scale()
        # Draws all the bones in their original positions first.
        bones = self.mgr.editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone') # Get all bones.
        for bone in bones:
            if bone == self.bone:
                continue
            if quarkx.setupsubset(SS_MODEL, "Options")['Drag_Bones_Only'] == "1" and (bone.name != self.bone.dictspec['parent_name'] and self.bone.name != bone.dictspec['parent_name']):
                continue
            p = view.proj(bone.position)
            if p.visible:
                if quarkx.setupsubset(SS_MODEL, "Options")['Drag_Bones_Only'] == "1" and (bone.name == self.bone.dictspec['parent_name'] or self.bone.name == bone.dictspec['parent_name']):
                    pass
                elif bone.dictspec['parent_name'] != "None":
                    parentbone = findbone(self.mgr.editor, bone.dictspec['parent_name'])
                    parent_handle_scale = parentbone['scale'][0]
                    p2 = view.proj(parentbone.position)
                    line_color = MapColor("BoneLines", SS_MODEL)
                    DrawBoneLine(p, p2, cv, line_color, scale, parent_handle_scale, view)
                handle_scale = bone.dictspec['scale'][0]
                handle_color = bone.dictspec['_color']
                quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
                handle_color = MapColor("handle_color", SS_MODEL)
                DrawBoneHandle(p, cv, handle_color, scale, handle_scale)
                if (self.mgr.editor.layout.explorer.sellist[0] == self.bone) and (bone.dictspec['parent_name'] == self.bone.name):
                    parentbone = self.bone
                    for obj2 in redimages:
                        if parentbone.name == obj2.name:
                            parentbone = obj2
                            break
                    parent_handle_scale = parentbone['scale'][0]
                    p2 = view.proj(parentbone.position)
                    
                    handle_color = self.bone.dictspec['_color']
                    quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
                    handle_color = MapColor("handle_color", SS_MODEL)
                    if quarkx.setupsubset(SS_MODEL, "Options")['MBLines_Color'] is not None:
                        line_color = handle_color
                    else:
                        line_color = MapColor("BoneHandles", SS_MODEL)
                    DrawBoneLine(p, p2, cv, line_color, scale, parent_handle_scale, view)
                    
        for obj in redimages:
            if obj.type != ":bone":
                continue
            vertices = obj.vtxlist
            cv.pencolor = redcolor
            # Draws the vertexes assigned to the bone joint DURING the drag.
            for compname in vertices:
                compvtx = self.newverticespos[compname]
                tristodraw = self.mgr.editor.ModelComponentList['tristodraw'][compname]
                for vtx in vertices[compname]:
                    p = view.proj(compvtx[vtx])
                    if vtx in tristodraw:
                        for vtx2 in tristodraw[vtx]:
                            p2 = view.proj(compvtx[vtx2])
                            cv.line(p, p2)
                    if p.visible:
                        cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
            handle_color = self.bone.dictspec['_color']
            quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
            handle_color = MapColor("handle_color", SS_MODEL)
            if quarkx.setupsubset(SS_MODEL, "Options")['MBLines_Color'] is not None:
                line_color = handle_color
            else:
                line_color = MapColor("BoneHandles", SS_MODEL)
            p = view.proj(obj.position)
            if p.visible:
                if obj.dictspec['parent_name'] != "None":
                    parentbone = findbone(self.mgr.editor, obj.dictspec['parent_name'])
                    for obj2 in redimages:
                        # If the bone is in redimages, it's also moving, and we need to use the moving bone instead
                        if parentbone.name == obj2.name:
                            parentbone = obj2
                            break
                    parent_handle_scale = parentbone['scale'][0]
                    p2 = view.proj(parentbone.position)
                    if obj.name == self.bone.name:
                        if (self.mgr.editor.layout.explorer.sellist[0] == self.bone):
                            pass
                        else:
                            line_color = MapColor("BoneHandles", SS_MODEL)
                    DrawBoneLine(p, p2, cv, line_color, scale, parent_handle_scale, view)
                handle_scale = obj.dictspec['scale'][0]
                DrawBoneHandle(p, cv, handle_color, scale, handle_scale, view)

    def drag(self, v1, v2, flags, view, undo=None): # for BoneCenterHandle
        delta = v2-v1
        if flags&MB_CTRL:
            g1 = 1
            delta = qhandles.aligntogrid(delta, 1)
        else:
            g1 = 0
        editor = self.mgr.editor
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)

        if view.info["viewname"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["viewname"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.z+delta.z)
        elif view.info["viewname"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            s = "was %s"%self.pos + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        self.draghint = s # If we get all the rotation hints to work for the YZ view below these "s" lines can be deleted.

        old = [self.bone]
        new = None
        if delta or (flags&MB_REDIMAGE):
            newbone = self.bone.copy()
            frame_name = editor.Root.currentcomponent.currentframe.name
            if editor.ModelComponentList['bonelist'].has_key(newbone.name) and editor.ModelComponentList['bonelist'][newbone.name].has_key('frames') and editor.ModelComponentList['bonelist'][newbone.name]['frames'].has_key(frame_name):
                newbone.position = quarkx.vect(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['position'])
                newbone.rotmatrix = quarkx.matrix(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['rotmatrix'])
                if editor.dragobject is None:
                    editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['position'] = (newbone.position + delta).tuple
            new = [newbone]
            for bone in self.attachedbones:
                old = old + [bone]
                newbone = bone.copy()
                if editor.ModelComponentList['bonelist'].has_key(newbone.name) and editor.ModelComponentList['bonelist'][newbone.name].has_key('frames') and editor.ModelComponentList['bonelist'][newbone.name]['frames'].has_key(frame_name):
                    newbone.position = quarkx.vect(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['position'])
                    newbone.rotmatrix = quarkx.matrix(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['rotmatrix'])
                    if editor.dragobject is None:
                        editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['position'] = (newbone.position + delta).tuple
                new = new + [newbone]
            self.linoperation(new, delta, g1, view, undo)
        else:
            new = None
        old, new = self.sortbonelist(old, new)

        return old, new

    def linoperation(self, list, delta, g1, view, undo=None): # for BoneCenterHandle
        # Reset the self.newverticespos list
        editor = self.mgr.editor
        for compname in self.newverticespos:
            comp = editor.Root.dictitems[compname]
            self.newverticespos[compname] = comp.currentframe.vertices

        for obj in list:
            obj.position = obj.position + delta
            obj['position'] = obj.position.tuple
            vertices = obj.vtxlist
            for compname in vertices:
                if editor.dragobject is None:
                    for vtx in vertices[compname]:
                        self.newverticespos[compname][vtx] = self.newverticespos[compname][vtx] + delta
                else:
                    for vtx in vertices[compname]:
                        if editor.ModelComponentList[compname]['weightvtxlist'].has_key(vtx) and editor.ModelComponentList[compname]['weightvtxlist'][vtx].has_key(obj.name):
                            weight_value = editor.ModelComponentList[compname]['weightvtxlist'][vtx][obj.name]['weight_value']
                        else:
                            weight_value = 1.0
                        self.newverticespos[compname][vtx] = self.newverticespos[compname][vtx] + (delta * weight_value)

        if editor.dragobject is None:
            for compname in self.newverticespos:
                comp = editor.Root.dictitems[compname]
                old_frame = comp.currentframe
                new_frame = old_frame.copy()
                new_frame.vertices = self.newverticespos[compname]
                undo.exchange(old_frame, new_frame)

        return delta


class BoneCornerHandle(BoneHandle):
    "handle to rotate bone."

    undomsg = "bone joint rotation"
    def __init__(self, center, pos1, mgr, bone, realpoint=None):
        BoneHandle.__init__(self, pos1, mgr, bone)
        if realpoint is None:
            self.pos0 = pos1
        else:
            self.pos0 = realpoint
        self.center = center
        self.cursor = CR_CROSSH

    def draw(self, view, cv, draghandle=None): # for BoneCornerHandle
        editor = self.mgr.editor
        from qbaseeditor import flagsmouse
        if quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is not None:
            return

        if isinstance(editor.dragobject, qhandles.ScrollViewDragObject) and flagsmouse == 1040:
            return # RMB pressed or dragging to pan (scroll) in the view.

        if view.info["viewname"] == "editors3Dview":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles1"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                return
        if view.info["viewname"] == "XY":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles2"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                return
        if view.info["viewname"] == "YZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles3"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                return
        if view.info["viewname"] == "XZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles4"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                return
        if view.info["viewname"] == "3Dwindow":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_drawnohandles5"] == "1" or quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                return
        # Draws the line and ball (p) at the end of the rotation handle and fills in its color.
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.penwidth = 1
            cv.penstyle = PS_INSIDEFRAME
            cv.pencolor = MapColor("LinearHandleOutline", SS_MODEL)
            p2 = view.proj(self.center)
            cv.line(p2, p)
            if self.bone.getint('_color') == MapColor("BoneHandles", SS_MODEL):
                handle_color = MapColor("LinearHandleCorners", SS_MODEL)
            else:
                handle_color = self.bone.getint('_color')
            cv.brushcolor = handle_color
            cv.brushstyle = BS_SOLID
            cv.ellipse(int(p.x)-5, int(p.y)-3, int(p.x)+5, int(p.y)+3)

    def linoperation(self, list, delta, g1, view): # for BoneCornerHandle
        # Reset the self.newverticespos list
        editor = self.mgr.editor
        for compname in self.newverticespos:
            comp = editor.Root.dictitems[compname]
            self.newverticespos[compname] = comp.currentframe.vertices

        rotationorigin = self.center
        oldpos = self.pos - rotationorigin
        newpos = (self.pos + delta) - rotationorigin
        normal = view.vector("Z").normalized
        oldpos = oldpos - normal*(normal*oldpos)
        newpos = newpos - normal*(normal*newpos)
        m = qhandles.UserRotationMatrix(normal, newpos, oldpos, 0)
        if m is None:
            m = quarkx.matrix(quarkx.vect(1.0, 0.0, 0.0), quarkx.vect(0.0, 1.0, 0.0), quarkx.vect(0.0, 0.0, 1.0))
        # Use this if the radius should also be changed:
        #try:
        #    changedradius = sqrt(pow(newpos.x, 2) + pow(newpos.y, 2) + pow(newpos.z, 2)) / sqrt(pow(oldpos.x, 2) + pow(oldpos.y, 2) + pow(oldpos.z, 2))
        #except:
        #    changedradius = 1.0
        changedradius = 1.0

        for obj in list:
            obj.rotmatrix = changedradius * m * obj.rotmatrix
            #The dragged bone can't move (only rotate), so:
            if obj.name != self.bone.name:
                changedpos = obj.position - rotationorigin
                changedpos = changedradius * m * changedpos
                obj.position = changedpos + rotationorigin
                obj['position'] = obj.position.tuple

            #Update the draw_offset
            old_draw_offset = quarkx.vect(obj.dictspec['draw_offset'])
            new_draw_offset = changedradius * m * old_draw_offset
            obj['draw_offset'] = new_draw_offset.tuple

        oldverticespos = self.newverticespos
        newverticespos = {}
        verticesweight = {}
        for compname in oldverticespos.keys():
            newverticespos[compname] = [[]] * len(oldverticespos[compname])
            verticesweight[compname] = [[]] * len(oldverticespos[compname])
            for vtx in range(len(oldverticespos[compname])):
                newverticespos[compname][vtx] = None
                verticesweight[compname][vtx] = 0.0
        for obj in list:
            vertices = obj.vtxlist
            for compname in vertices:
                for vtx in vertices[compname]:
                    if editor.ModelComponentList[compname]['weightvtxlist'].has_key(vtx) and editor.ModelComponentList[compname]['weightvtxlist'][vtx].has_key(obj.name):
                        weight_value = editor.ModelComponentList[compname]['weightvtxlist'][vtx][obj.name]['weight_value']
                    else:
                        weight_value = 1.0
                    changedpos = oldverticespos[compname][vtx] - rotationorigin
                    changedpos = changedradius * m * changedpos
                    if newverticespos[compname][vtx] is None:
                        newverticespos[compname][vtx] = quarkx.vect(0, 0, 0)
                    newverticespos[compname][vtx] = newverticespos[compname][vtx] + (changedpos + rotationorigin) * weight_value
                    verticesweight[compname][vtx] = verticesweight[compname][vtx] + weight_value
        for compname in newverticespos.keys():
            for vtx in range(len(newverticespos[compname])):
                if newverticespos[compname][vtx] is None:
                    newverticespos[compname][vtx] = oldverticespos[compname][vtx]
                    verticesweight[compname][vtx] = 1.0
                if abs(verticesweight[compname][vtx] - 1.0) > 0.001:
                    oldpartpos = oldverticespos[compname][vtx] * (1.0 - verticesweight[compname][vtx])
                    newverticespos[compname][vtx] = newverticespos[compname][vtx] + oldpartpos
        self.newverticespos = newverticespos

        if view.info['type'] == 'YZ':
            return (math.acos(m[1,1])*180.0/math.pi)
        return (math.acos(m[0,0])*180.0/math.pi)

    def drawred(self, redimages, view, redcolor): # for BoneCornerHandle
        view.repaint()
        cv = view.canvas()
        cv.reset()
        cv.penwidth = 1
        cv.penstyle = PS_INSIDEFRAME
        cv.brushstyle = BS_CLEAR
        scale = view.scale()
        # Draw all of the stationary bone joints first.
        if quarkx.setupsubset(SS_MODEL, "Options")['Drag_Bones_Only'] != "1":
            for bone in self.fixedbones:
                if bone == self.bone:
                    continue
                p = view.proj(bone.position)
                if bone.dictspec['parent_name'] != "None":
                    if (self.mgr.editor.layout.explorer.sellist[0] == self.bone):
                        parentbone = bone.dictspec['parent_name']
                        drewlines = 0
                        for obj2 in range(len(redimages)):
                            if parentbone == redimages[obj2].name:
                                parentbone = redimages[obj2]
                                parent_handle_scale = parentbone['scale'][0]
                                p2 = view.proj(parentbone.position)
                                if quarkx.setupsubset(SS_MODEL, "Options")['MBLines_Color'] is not None:
                                    line_color = self.bone.dictspec['_color']
                                    quarkx.setupsubset(SS_MODEL, "Colors")["line_color"] = line_color
                                    line_color = MapColor("line_color", SS_MODEL)
                                else:
                                    line_color = MapColor("BoneHandles", SS_MODEL)
                                DrawBoneLine(p, p2, cv, line_color, scale, parent_handle_scale)
                                drewlines = 1
                                break
                        if drewlines == 1:
                            try:
                                handle_scale = bone.dictspec['scale'][0]
                            except:
                                handle_scale = 1.0
                            handle_color = bone.dictspec['_color']
                            quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
                            handle_color = MapColor("handle_color", SS_MODEL)
                            DrawBoneHandle(p, cv, handle_color, scale, handle_scale)
                            continue
                    bone_parent = findbone(self.mgr.editor, bone.dictspec['parent_name'])
                    bone_parent_handle_scale = bone_parent['scale'][0]
                    p2 = view.proj(bone_parent.position)
                    line_color = MapColor("BoneLines", SS_MODEL)
                    DrawBoneLine(p, p2, cv, line_color, scale, bone_parent_handle_scale)
                    try:
                        handle_scale = bone_parent.dictspec['scale'][0]
                    except:
                        handle_scale = 1.0
                    handle_color = bone_parent.dictspec['_color']
                    quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
                    handle_color = MapColor("handle_color", SS_MODEL)
                    DrawBoneHandle(p2, cv, handle_color, scale, handle_scale)
                try:
                    handle_scale = bone.dictspec['scale'][0]
                except:
                    handle_scale = 1.0
                handle_color = bone.dictspec['_color']
                quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
                handle_color = MapColor("handle_color", SS_MODEL)
                DrawBoneHandle(p, cv, handle_color, scale, handle_scale)
        if quarkx.setupsubset(SS_MODEL, "Options")['MBLines_Color'] is not None:
            line_color = self.bone.dictspec['_color']
            quarkx.setupsubset(SS_MODEL, "Colors")["line_color"] = line_color
            line_color = MapColor("line_color", SS_MODEL)
        else:
            line_color = MapColor("BoneHandles", SS_MODEL)
        for obj in redimages:
            if obj.type != ":bone":
                continue
            vertices = obj.vtxlist
            cv.pencolor = redcolor
            # Draws the vertexes assigned to the bone joint DURING the drag.
            for compname in vertices:
                compvtx = self.newverticespos[compname]
                tristodraw = self.mgr.editor.ModelComponentList['tristodraw'][compname]
                for vtx in vertices[compname]:
                    p = view.proj(compvtx[vtx])
                    if vtx in tristodraw:
                        for vtx2 in tristodraw[vtx]:
                            p2 = view.proj(compvtx[vtx2])
                            cv.line(p, p2)
                    if p.visible:
                        cv.rectangle(int(p.x)-3, int(p.y)-3, int(p.x)+3, int(p.y)+3)
            try:
                handle_scale = obj.dictspec['scale'][0]
            except:
                handle_scale = 1.0
            if obj.name != self.bone.name:
                p = view.proj(obj.position)
                if p.visible:
                    if obj.dictspec['parent_name'] != "None":
                        parentbone = findbone(self.mgr.editor, obj.dictspec['parent_name'])
                        for obj2 in redimages:
                            # If the bone is in redimages, it's also moving, and we need to use the moving bone instead
                            if parentbone.name == obj2.name:
                                parentbone = obj2
                                break
                        parent_handle_scale = parentbone['scale'][0]
                        p2 = view.proj(parentbone.position)
                        DrawBoneLine(p, p2, cv, line_color, scale, parent_handle_scale)
                    handle_color = self.bone.dictspec['_color']
                    quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
                    handle_color = MapColor("handle_color", SS_MODEL)
                    DrawBoneHandle(p, cv, handle_color, scale, handle_scale)
            bonenormallength = quarkx.setupsubset(SS_MODEL,"Building")['RotationHandleLength'][0]
            if obj.name == self.bone.name:
                p = view.proj(obj.position + obj.rotmatrix * quarkx.vect(bonenormallength * handle_scale, 0, 0))
            else:
                from math import sqrt
                p = view.proj(obj.position + quarkx.matrix((sqrt(2)/2, -sqrt(2)/2, 0), (sqrt(2)/2, sqrt(2)/2, 0), (0, 0, 1)) * quarkx.vect(bonenormallength * handle_scale, 0, 0))
            # Draws the line and ball ( p) at the end of the rotation handle and fills in its color.
            if p.visible:
                cv.penstyle = PS_INSIDEFRAME
                cv.pencolor = MapColor("LinearHandleOutline", SS_MODEL)
                p2 = view.proj(obj.position)
                cv.line(p2, p)
                handle_color = obj.getint('_color')
                cv.brushcolor = handle_color
                cv.brushstyle = BS_SOLID
                cv.ellipse(int(p.x)-5, int(p.y)-3, int(p.x)+5, int(p.y)+3)
                cv.brushstyle = BS_CLEAR
        p = view.proj(self.bone.position)
        try:
            handle_scale = self.bone.dictspec['scale'][0]
        except:
            handle_scale = 1.0
        handle_color = self.bone.dictspec['_color']
        quarkx.setupsubset(SS_MODEL, "Colors")["handle_color"] = handle_color
        handle_color = MapColor("handle_color", SS_MODEL)
        DrawBoneHandle(p, cv, handle_color, scale, handle_scale)

    def drag(self, v1, v2, flags, view): # for BoneCornerHandle
        delta = v2-v1
        if flags&MB_CTRL:
            g1 = 1
            delta = qhandles.aligntogrid(delta, 1)
        else:
            g1 = 0
        editor = self.mgr.editor
        if editor is not None:
            if editor.lock_x==1:
                delta = quarkx.vect(0, delta.y, delta.z)
            if editor.lock_y==1:
                delta = quarkx.vect(delta.x, 0, delta.z)
            if editor.lock_z==1:
                delta = quarkx.vect(delta.x, delta.y, 0)

        if view.info["viewname"] == "XY":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.y) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y)
        elif view.info["viewname"] == "XZ":
            s = "was " + ftoss(self.pos.x) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.z+delta.z)
        elif view.info["viewname"] == "YZ":
            s = "was " + ftoss(self.pos.y) + " " + ftoss(self.pos.z) + " now " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        else:
            s = "was %s"%self.pos + " now " + ftoss(self.pos.x+delta.x) + " " + ftoss(self.pos.y+delta.y) + " " + ftoss(self.pos.z+delta.z)
        self.draghint = s

        old = [self.bone]
        new = None
        if delta or (flags&MB_REDIMAGE):
            newbone = self.bone.copy()
            frame_name = editor.Root.currentcomponent.currentframe.name
            if editor.ModelComponentList['bonelist'].has_key(newbone.name) and editor.ModelComponentList['bonelist'][newbone.name].has_key('frames') and editor.ModelComponentList['bonelist'][newbone.name]['frames'].has_key(frame_name):
                newbone.position = quarkx.vect(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['position'])
                newbone.rotmatrix = quarkx.matrix(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['rotmatrix'])
            new = [newbone]
            for bone in self.attachedbones:
                old = old + [bone]
                newbone = bone.copy()
                if editor.ModelComponentList['bonelist'].has_key(newbone.name) and editor.ModelComponentList['bonelist'][newbone.name].has_key('frames') and editor.ModelComponentList['bonelist'][newbone.name]['frames'].has_key(frame_name):
                    newbone.position = quarkx.vect(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['position'])
                    newbone.rotmatrix = quarkx.matrix(editor.ModelComponentList['bonelist'][newbone.name]['frames'][frame_name]['rotmatrix'])
                new = new + [newbone]

            angle = self.linoperation(new, delta, g1, view)
            self.draghint = "rotate %d deg." % angle
        else:
            new = None
        old, new = self.sortbonelist(old, new)

        return old, new


#
# Mouse Clicking and Dragging on Model Editor views.
#

def MouseDragging(self, view, x, y, s, handle):
    "Mouse Drag on a Model View, self is an instance of the model editor."
    global cursorposatstart

  # Commented out lines below locks up editor if component is hidden and another component is not selected.
  #  if self.Root.currentcomponent.dictspec['show'] == "\x00": # Component is hidden.
      #  self.dragobject = None
      #  quarkx.beep()
      #  return None
  #  if isinstance(handle, BoneCenterHandle) or isinstance(handle, BoneCornerHandle) or self.Root.currentcomponent.dictspec['show'] == "\x00": # Used for auto selection feature.
    if isinstance(handle, BoneCenterHandle) or isinstance(handle, BoneCornerHandle): # Used for auto selection feature.
        if (len(self.layout.explorer.sellist) == 0):
            self.dragobject = None
            quarkx.beep()
            return None
        elif (len(self.layout.explorer.sellist) == 1) and (self.layout.explorer.sellist[0].type == ':bone'):
            if self.layout.explorer.sellist[0] != handle.bone:
                self.layout.explorer.sellist = [handle.bone]
                Update_Editor_Views(self)
                self.layout.mpp.resetpage()
        elif (len(self.layout.explorer.sellist) == 1) and (self.layout.explorer.sellist[0].type == ':bg'):
            compbones = self.Root.findallsubitems("", ':bone')      # get all bones
            allow = 1
            for bone in compbones:
                if bone == handle.bone:
                    allow = 0
                if allow == 1:
                    continue
        elif len(self.layout.explorer.sellist) == 2 and ((self.layout.explorer.sellist[0].type == ':bg' and self.layout.explorer.sellist[1].type == ':mf') or (self.layout.explorer.sellist[0].type == ':bone' and self.layout.explorer.sellist[1].type == ':mf')):
            if self.layout.explorer.sellist[0].type == ':bone' and self.layout.explorer.sellist[0] != handle.bone:
                self.layout.explorer.sellist = [handle.bone] + [self.layout.explorer.sellist[1]]
                Update_Editor_Views(self)
                self.layout.mpp.resetpage()
        else:
            self.dragobject = None
            quarkx.beep()
            return None
    for item in view.info:
        if item == 'center':
            center = view.info["center"]
            cursorposatstart = view.space(x,y,view.proj(center).z) # Used for start where clicked for Model Editor rotation.

    #
    # qhandles.MouseDragging builds the DragObject.
    #

    if handle is not None:
        s = handle.click(self)
        if s and ("S" in s):
            self.layout.actionmpp()  # update the multi-pages-panel

    if handle is not None:
        if isinstance(handle, BoneHandle):
            handle.start_drag(view, x, y)
            if handle.attachedbones is None:
                self.dragobject = None
                quarkx.beep()
                return None

    return qhandles.MouseDragging(self, view, x, y, s, handle, MapColor("DragImage", SS_MODEL))



def ClickOnView(editor, view, x, y):
    "Constantly reads what the mouse cursor is over"
    "in the view and returns those items if any."

    #
    # defined in PyMapview.pas
    #
    return view.clicktarget(editor.Root, int(x), int(y))



def MouseClicked(self, view, x, y, s, handle):
    "Mouse Click on a Model view."

    #
    # qhandles.MouseClicked manages the click but doesn't actually select anything
    #
    flags = qhandles.MouseClicked(self, view, x, y, s, handle)

    if "1" in flags:

        #
        # This mouse click must select something.
        #

        self.layout.setupdepth(view)
        choice = view.clicktarget(self.Root, x, y)
         # this is the list of frame triangles we clicked on
        if len(choice):
            choice.sort()   # list of (clickpoint,component,triangleindex) tuples - sort by depth
            clickpoint, obj, tridx = choice[0]
            if (obj.type != ':mc') or (type(tridx) is not type(0)):   # should not occur
                return flags
            if ("M" in s) and obj.selected:    # if Menu, we try to keep the currently selected objects
                return flags
            if "T" in s:    # if Multiple selection request
                obj.togglesel()
                if obj.selected:
                    self.layout.explorer.focus = obj
                self.layout.explorer.selchanged()
     #       else:
     #           self.layout.explorer.uniquesel = obj
        else:
      #      if not ("T" in s):    # clear current selection
      #          self.layout.explorer.uniquesel = None
            if not ("T" in s):    # clear current selection *** NOT ANY MORE, leave what's selected.
                pass
        return flags+"S"
    return flags


# ----------- REVISION HISTORY ------------
#
#
#$Log: mdlhandles.py,v $
#Revision 1.237  2013/02/26 02:57:29  cdunde
#Linear handle instruction correction.
#
#Revision 1.236  2012/04/01 07:50:58  cdunde
#Additional changes to previous changes.
#
#Revision 1.235  2012/03/31 22:28:34  cdunde
#Fixed rotation values for YZ view not working in Model Editor.
#
#Revision 1.234  2011/11/12 06:01:12  cdunde
#Changed needed functions to affect bonelist.
#
#Revision 1.233  2011/05/28 15:58:20  cdunde
#Menu updates.
#
#Revision 1.232  2011/05/27 20:57:04  cdunde
#Update for bbox handling for undo system.
#
#Revision 1.231  2011/05/26 22:57:48  cdunde
#Removed OLD bones system Keyframe rotation function not used anymore.
#
#Revision 1.230  2011/05/26 09:32:19  cdunde
#Setup component bbox vertex assignment support.
#
#Revision 1.229  2011/04/02 01:08:10  cdunde
#Added Half-Life 2 importer animation support with bone, attachment and bbox movement.
#
#Revision 1.228  2011/03/15 19:49:55  cdunde
#Bone handle fix by DanielPharos for True3Dview mode.
#
#Revision 1.227  2011/03/15 08:25:46  cdunde
#Added cameraview saving duplicators and search systems, like in the Map Editor, to the Model Editor.
#
#Revision 1.226  2011/02/28 00:33:51  cdunde
#Fixed face outlines not drawing, when they should, after rectangle selection.
#
#Revision 1.225  2011/02/21 20:17:26  cdunde
#Fixed error when faces are deleted.
#
#Revision 1.224  2011/02/13 03:37:47  cdunde
#Fixed all force to grid functions for model editor bones, vertexes, tags and bboxes.
#
#Revision 1.223  2010/12/19 17:24:54  cdunde
#Changes so a bone can have multiple bounding boxes assigned to it.
#
#Revision 1.222  2010/12/12 20:19:55  cdunde
#Update to release bbox function.
#
#Revision 1.221  2010/12/07 20:10:16  cdunde
#Update for bbox face handle.
#
#Revision 1.220  2010/12/07 11:17:15  cdunde
#More updates for Model Editor bounding box system.
#
#Revision 1.219  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.218  2010/10/20 20:17:54  cdunde
#Added bounding boxes (hit boxes) and bone controls support used by Half-Life, maybe others.
#
#Revision 1.217  2010/10/10 03:24:59  cdunde
#Added support for player models attachment tags.
#To make baseframe name uniform with other files.
#
#Revision 1.216  2010/09/23 20:29:32  cdunde
#Update for new Skin-view drag method.
#
#Revision 1.215  2010/09/23 04:57:24  cdunde
#Various improvements for Model Editor Skin-view Linear Handle drawing time.
#
#Revision 1.214  2010/09/16 06:33:34  cdunde
#Model editor, Major change of Skin-view Linear Handle selection and dragging system, massively improving drawing time.
#
#Revision 1.213  2010/09/01 08:49:08  cdunde
#Code speedup by DanielPharos.
#
#Revision 1.212  2010/07/02 04:26:59  cdunde
#Needed small fix for last change to avoid problems.
#
#Revision 1.211  2010/06/25 05:28:00  cdunde
#Setup 'Auto Scaling' function for the Skin-view that resets the skin handles and Component's UV's
#to fit the currently selected and viewable skin texture of that Component.
#
#Revision 1.210  2010/05/29 04:34:45  cdunde
#Update for Model Editor camera EYE handles for editor and floating 3D view.
#
#Revision 1.209  2010/05/14 06:12:32  cdunde
#Needed fix, in case user deletes Misc group or components with tags, to avoid errors.
#
#Revision 1.208  2010/05/14 00:26:45  cdunde
#Need fix, in case user deletes Skeleton group, to avoid errors and update ModelComponentList.
#
#Revision 1.207  2010/05/12 08:07:13  cdunde
#Added Eye camera handle when in True 3D mode for easier navigation.
#
#Revision 1.206  2010/05/06 21:57:01  cdunde
#Speed improvement by DanielPharos.
#
#Revision 1.205  2010/05/06 03:10:54  cdunde
#Menu functions update to eliminate dupe and unnecessary redraws.
#
#Revision 1.204  2010/05/02 06:20:26  cdunde
#To remove Model Editor unused and duplicating handle build code causing slowdowns.
#
#Revision 1.203  2010/05/01 04:25:37  cdunde
#Updated files to help increase editor speed by including necessary ModelComponentList items
#and removing redundant checks and calls to the list.
#
#Revision 1.202  2010/04/30 08:37:17  cdunde
#Fix for vertex handles not drawing when switching from face to vertex mode after view scroll.
#
#Revision 1.201  2010/04/23 23:15:48  cdunde
#Proper bone movement code update by DanielPharos.
#
#Revision 1.200  2010/04/09 13:11:18  cdunde
#Fix to stop editor lockup after hiding a component.
#
#Revision 1.199  2010/04/08 04:50:58  cdunde
#Needed fixes for some broken bone specifics items.
#
#Revision 1.198  2010/03/10 04:24:06  cdunde
#Update to support added ModelComponentList for 'bonelist' updating.
#
#Revision 1.197  2010/02/03 08:41:14  cdunde
#Fix for bone corner handle not rotating if assigned vertexes do not have a weight_value.
#
#Revision 1.196  2010/01/22 22:07:33  cdunde
#Fix by DanielPharos for bone handles offset updating after corner handle drag.
#
#Revision 1.195  2009/11/25 23:51:49  cdunde
#Fix by DanielPharos to stop component folders shifting around in tree-view after bone drag.
#
#Revision 1.194  2009/11/15 02:44:40  cdunde
#Update of grnreader.exe to eliminate multiple outputs of group mesh vertices to .ms file,
#of .gr2 importer to eliminate multiple output.ms file listings of bones and proper vertex weight assigning.
#and of mdlhandles.py to set its code back to the way it was and should be for all model types.
#
#Revision 1.193  2009/11/13 06:15:05  cdunde
#Updates for .gr2 bones to use our same code.
#
#Revision 1.192  2009/11/10 04:41:34  cdunde
#Added option to only draw drag bones to speed up drag drawing if a lot of bones exist.
#
#Revision 1.191  2009/11/06 06:10:45  cdunde
#Minor error message fix.
#
#Revision 1.190  2009/11/05 22:54:10  cdunde
#DanielPharos's great fix for bones corner handle drag code.
#
#Revision 1.189  2009/10/16 21:29:06  cdunde
#Menu update.
#
#Revision 1.188  2009/10/12 20:49:56  cdunde
#Added support for .md3 animationCFG (configuration) support and editing.
#
#Revision 1.187  2009/10/07 18:13:19  cdunde
#Fix to move tags correctly with their own components tag and animation frames.
#
#Revision 1.186  2009/09/30 19:37:26  cdunde
#Threw out tags dialog, setup tag dragging, commands, and fixed saving of face selection.
#
#Revision 1.185  2009/09/07 06:46:24  cdunde
#Update for Linear and tag handle drawing.
#
#Revision 1.184  2009/09/07 01:38:45  cdunde
#Setup of tag menus and icons.
#
#Revision 1.183  2009/09/06 11:54:44  cdunde
#To setup, make and draw the TagFrameHandles. Also improve animation rotation.
#
#Revision 1.182  2009/08/31 08:52:16  cdunde
#To try and stop errors from opening the Model Editor Skin-view for the first time.
#
#Revision 1.181  2009/08/27 03:59:31  cdunde
#To setup a bone's "flags" dictspec item for model importing and exporting support that use them.
#
#Revision 1.180  2009/08/02 20:16:52  cdunde
#Fix to avoid error of bone handle drawing.
#
#Revision 1.179  2009/07/14 09:43:03  cdunde
#Attempt to speed up vertex drawing caused non-picked vertexes not to draw.
#Reversing new code to previous code until this can be corrected.
#
#Revision 1.178  2009/07/14 00:27:33  cdunde
#Completely revamped Model Editor vertex Linear draglines system,
#increasing its reaction and drawing time to twenty times faster.
#
#Revision 1.177  2009/06/09 05:51:48  cdunde
#Updated to better display the Model Editor's Skeleton group and
#individual bones and their sub-bones when they are hidden.
#
#Revision 1.176  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.175  2009/05/03 20:49:57  cdunde
#Moved menu item for individual bone handle selection and
#stopped all vertexes from being drawn and assigned bone movement if component is hidden.
#
#Revision 1.174  2009/05/01 06:07:03  cdunde
#Moved bones undo function to mdlutils.py for generic use elsewhere.
#Added bone handle scaling functions and selection option.
#
#Revision 1.173  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.172  2009/03/28 20:24:42  cdunde
#Minor comment corrections.
#
#Revision 1.171  2009/03/26 07:17:20  cdunde
#Update for editing vertex color support.
#
#Revision 1.170  2009/03/25 19:46:03  cdunde
#Changed dictionary list keyword to be more specific.
#
#Revision 1.169  2009/03/25 05:30:20  cdunde
#Added vertex color support.
#
#Revision 1.168.2.6  2009/03/23 20:01:26  danielpharos
#All vertices should now move properly!
#
#Revision 1.168.2.5  2009/03/16 21:10:28  danielpharos
#Final result now being applied to vertices.
#
#Revision 1.168.2.4  2009/03/16 18:33:31  danielpharos
#Fix red-drawing of BoneCenterHandle.
#
#Revision 1.168.2.3  2009/03/11 15:50:36  danielpharos
#Added vertex assigning and some draw-n-drag code.
#
#Revision 1.168.2.2  2009/03/02 22:50:07  danielpharos
#Added vertex assigning code.
#
#Revision 1.168.2.1  2009/02/25 20:46:37  danielpharos
#Initial changes.
#
#Revision 1.168  2009/02/17 04:58:03  cdunde
#Removed line of code causing problem by killing the view handles.
#
#Revision 1.167  2009/01/29 02:13:51  cdunde
#To reverse frame indexing and fix it a better way by DanielPharos.
#
#Revision 1.166  2009/01/27 20:56:24  cdunde
#Update for frame indexing.
#Added new bone function 'Attach End to Start'.
#Code reorganization for consistency of items being created.
#
#Revision 1.165  2009/01/27 05:03:02  cdunde
#Full support for .md5mesh bone importing with weight assignment and other improvements.
#
#Revision 1.164  2009/01/14 09:36:22  cdunde
#Added LinBoneCornerHandle color to match bone color if set for easer ID.
#
#Revision 1.163  2008/12/22 05:06:17  cdunde
#Added new function to attach bones end handles.
#
#Revision 1.162  2008/12/19 07:13:20  cdunde
#Minor change for bone name splitting to stop improper procedure of doing so.
#
#Revision 1.161  2008/12/09 11:04:07  cdunde
#Fixed face mode not drawing selection outlines while rotating.
#
#Revision 1.160  2008/11/22 05:09:42  cdunde
#Selects bone and first frame of bone handle component if not currentcomponent
#to avoid errors of menu vertex selection.
#
#Revision 1.159  2008/11/19 06:16:23  cdunde
#Bones system moved to outside of components for Model Editor completed.
#
#Revision 1.158  2008/10/25 23:41:15  cdunde
#Fix for errors from the editor.ModelComponentList if a model component is not in it.
#
#Revision 1.157  2008/10/23 04:42:24  cdunde
#Infobase links and updates for Bones.
#
#Revision 1.156  2008/10/21 04:35:33  cdunde
#Bone corner handle rotation fixed correctly by DanielPharos
#and stop all drawing during Keyframe Rotation function.
#
#Revision 1.155  2008/10/18 22:57:32  cdunde
#A bunch of fixes for reassigning vertexes between bone handles.
#
#Revision 1.154  2008/10/18 22:37:01  cdunde
#To fix vertex not being removed from end handle end_vtx_pos list
#when a vertex is re-assigned to another handle.
#
#Revision 1.153  2008/10/17 22:29:05  cdunde
#Added assigned vertex count (read only) to Specifics/Args page for each bone handle.
#
#Revision 1.152  2008/10/15 00:01:30  cdunde
#Setup of bones individual handle scaling and Keyframe matrix rotation.
#Also removed unneeded code.
#
#Revision 1.151  2008/10/13 06:42:10  cdunde
#To add drag lines that were missed for a single bone corner handle rotation drag.
#
#Revision 1.150  2008/10/08 20:00:47  cdunde
#Updates for Model Editor Bones system.
#
#Revision 1.149  2008/10/04 05:48:06  cdunde
#Updates for Model Editor Bones system.
#
#Revision 1.148  2008/09/23 08:07:44  cdunde
#Added code to make bones positions frame independent.
#
#Revision 1.147  2008/09/23 05:14:49  cdunde
#Removed unneeded code check.
#
#Revision 1.146  2008/09/22 23:11:12  cdunde
#Updates for Model Editor Linear and Bone handles.
#
#Revision 1.145  2008/09/15 04:47:50  cdunde
#Model Editor bones code update.
#
#Revision 1.144  2008/08/21 12:13:34  danielpharos
#Fixed a minor mistake.
#
#Revision 1.143  2008/08/08 05:35:50  cdunde
#Setup and initiated a whole new system to support model bones.
#
#Revision 1.142  2008/07/23 01:56:39  cdunde
#Oops..that was a test file, reversing last change.
#
#Revision 1.141  2008/07/23 01:35:29  cdunde
#Fix to stop erroneous errors some time ago but forgot to commit until now.
#
#Revision 1.140  2008/07/22 23:14:23  cdunde
#Fixed menu items that were not interacting with their config settings in the Defaults.qrk file.
#
#Revision 1.139  2008/07/15 23:16:27  cdunde
#To correct typo error from MldOption to MdlOption in all files.
#
#Revision 1.138  2008/07/10 21:21:33  danielpharos
#Remove redundant code
#
#Revision 1.137  2008/07/05 19:11:42  cdunde
#Comment addition for a triangle's UV vert_index number computation formula.
#
#Revision 1.136  2008/06/17 20:59:22  cdunde
#To stop some minor errors from occurring.
#
#Revision 1.135  2008/06/01 04:39:53  cdunde
#Some Linear Handle fixes and added drag lines drawing.
#
#Revision 1.134  2008/05/30 08:22:55  cdunde
#Added full Linear Handles drag line drawing for all views in the Model Editor.
#
#Revision 1.133  2008/05/29 05:07:49  cdunde
#Added Skin-view Linear rotation and distortion drag lines drawing.
#
#Revision 1.132  2008/05/27 19:36:16  danielpharos
#Fixed another bunch of wrong imports
#
#Revision 1.131  2008/05/03 21:48:25  cdunde
#To fix multiple face selection error while keeping multiple vertex merging function working.
#
#Revision 1.130  2008/05/01 15:39:51  danielpharos
#Made an import more consistent with all others
#
#Revision 1.129  2008/05/01 13:52:32  danielpharos
#Removed a whole bunch of redundant imports and other small fixes.
#
#Revision 1.128  2008/02/23 05:29:18  cdunde
#Fixed conflicts with multiple vertex merging function.
#
#Revision 1.127  2008/02/23 04:41:11  cdunde
#Setup new Paint modes toolbar and complete painting functions to allow
#the painting of skin textures in any Model Editor textured and Skin-view.
#
#Revision 1.126  2008/02/22 09:52:22  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.125  2008/02/07 13:25:57  danielpharos
#Removed redundant import-line
#
#Revision 1.124  2008/02/06 00:12:44  danielpharos
#The skinview now properly updates to reflect changes made to textures.
#
#Revision 1.123  2008/01/26 06:32:38  cdunde
#To stop doautozoom in Skin-view, causing unexpected view jumps.
#
#Revision 1.122  2007/12/06 02:06:29  cdunde
#Minor corrections.
#
#Revision 1.121  2007/12/05 04:45:57  cdunde
#Added two new function methods to Subdivide selected faces into 3 and 4 new triangles each.
#
#Revision 1.120  2007/12/02 07:02:25  cdunde
#Some selected vertexes edge extrusion function code missed in last change.
#
#Revision 1.119  2007/12/02 06:47:12  cdunde
#Setup linear center handle selected vertexes edge extrusion function.
#
#Revision 1.118  2007/11/22 07:31:05  cdunde
#Setup to allow merging of a base vertex and other multiple selected vertexes.
#
#Revision 1.117  2007/11/20 02:27:55  cdunde
#Added check to stop merging of two vertexes of the same triangle.
#
#Revision 1.116  2007/11/19 07:45:56  cdunde
#Minor corrections for option number and activating menu item.
#
#Revision 1.115  2007/11/19 01:09:17  cdunde
#Added new function "Merge 2 Vertexes" to the "Vertex Commands" menu.
#
#Revision 1.114  2007/11/19 00:08:39  danielpharos
#Any supported picture can be used for a view background, and added two options: multiple, offset
#
#Revision 1.113  2007/11/14 00:11:13  cdunde
#Corrections for face subdivision to stop models from drawing broken apart,
#update Skin-view "triangles" amount displayed and proper full redraw
#of the Skin-view when a component is un-hidden.
#
#Revision 1.112  2007/11/11 11:41:54  cdunde
#Started a new toolbar for the Model Editor to support "Editing Tools".
#
#Revision 1.111  2007/11/04 00:33:33  cdunde
#To make all of the Linear Handle drag lines draw faster and some selection color changes.
#
#Revision 1.110  2007/10/29 17:56:31  cdunde
#Added option for Skin-view multiple drag lines drawing.
#
#Revision 1.109  2007/10/29 12:45:41  cdunde
#To setup drag line drawing for multiple selected vertex drags in the Skin-view.
#
#Revision 1.108  2007/10/28 21:49:07  cdunde
#To fix Skin-view Linear handle not drawing in correct position sometimes.
#
#Revision 1.107  2007/10/27 23:34:45  cdunde
#To remove test print statements missed.
#
#Revision 1.106  2007/10/27 01:51:32  cdunde
#To add the drawing of drag lines for editor vertex Linear center handle drags.
#
#Revision 1.105  2007/10/25 17:25:20  cdunde
#To remove unnecessary import calls.
#
#Revision 1.104  2007/10/22 02:26:09  cdunde
#To stop drawing of all editor handles during animation to fix problem if pause is used
#and then turned off and to make for cleaner animation drawing of views.
#
#Revision 1.103  2007/10/18 23:53:16  cdunde
#To remove dupe call to make selected face objects.
#
#Revision 1.102  2007/10/11 09:58:34  cdunde
#To keep the fillcolor correct for the editors 3D view after a
#tree-view selection is made with the floating 3D view window open and
#to stop numerous errors and dupe drawings when the floating 3D view window is closed.
#
#Revision 1.101  2007/10/09 04:16:25  cdunde
#To clear the EditorObjectList when the ModelFaceSelList is cleared for the "rulers" function.
#
#Revision 1.100  2007/10/08 16:20:21  cdunde
#To improve Model Editor rulers and Quick Object Makers working with other functions.
#
#Revision 1.99  2007/10/06 05:24:56  cdunde
#To add needed comments and finish setting up rectangle selection to work fully
#with passing selected faces in the editors view to the Skin-view.
#
#Revision 1.98  2007/10/05 20:47:50  cdunde
#Creation and setup of the Quick Object Makers for the Model Editor.
#
#Revision 1.97  2007/09/18 19:52:07  cdunde
#Cleaned up some of the Defaults.qrk item alignment and
#changed a color name from GrayImage to DragImage for clarity.
#Fixed Rectangle Selector from redrawing all views handles if nothing was selected.
#
#Revision 1.96  2007/09/17 06:24:49  cdunde
#Changes missed.
#
#Revision 1.95  2007/09/17 06:10:17  cdunde
#Update for Skin-view grid button and forcetogrid functions.
#
#Revision 1.94  2007/09/16 19:14:16  cdunde
#To redraw Skin-view handles, if any appear, when selecting RMB grid setting items.
#
#Revision 1.93  2007/09/16 18:16:17  cdunde
#To disable all forcetogrid menu items when a grid is inactive.
#
#Revision 1.92  2007/09/16 07:05:08  cdunde
#Minor Skin-view RMB menu item relocation.
#
#Revision 1.91  2007/09/16 02:20:39  cdunde
#Setup Skin-view with its own grid button and scale, from the Model Editor's,
#and color setting for the grid dots to be drawn in it.
#Also Skin-view RMB menu additions of "Grid visible" and Grid active".
#
#Revision 1.90  2007/09/13 06:58:01  cdunde
#Minor function description correction.
#
#Revision 1.89  2007/09/13 06:07:47  cdunde
#Update of selection for available component sub-menu creation.
#
#Revision 1.88  2007/09/13 01:04:59  cdunde
#Added a new function, to the Faces RMB menu, for a "Empty Component" to start fresh from.
#
#Revision 1.87  2007/09/12 05:25:51  cdunde
#To move Make New Component menu function from Commands menu to RMB Face Commands menu and
#setup new function to move selected faces from one component to another.
#
#Revision 1.86  2007/09/07 23:55:29  cdunde
#1) Created a new function on the Commands menu and RMB editor & tree-view menus to create a new
#     model component from selected Model Mesh faces and remove them from their current component.
#2) Fixed error of "Pass face selection to Skin-view" if a face selection is made in the editor
#     before the Skin-view is opened at least once in that session.
#3) Fixed redrawing of handles in areas that hints show once they are gone.
#
#Revision 1.85  2007/09/05 18:53:11  cdunde
#Changed "Pass Face Selection to Skin-view" to real time updating and
#added function to Sync Face Selection in the Editor to the Skin-view.
#
#Revision 1.84  2007/09/05 05:34:53  cdunde
#To fix XY (Z top) view lagging behind drawing Face selections and de-selections.
#
#Revision 1.83  2007/09/04 23:16:22  cdunde
#To try and fix face outlines to draw correctly when another
#component frame in the tree-view is selected.
#
#Revision 1.82  2007/09/01 20:32:06  cdunde
#Setup Model Editor views vertex "Pick and Move" functions with two different movement methods.
#
#Revision 1.81  2007/09/01 19:36:40  cdunde
#Added editor views rectangle selection for model mesh faces when in that Linear handle mode.
#Changed selected face outline drawing method to greatly increase drawing speed.
#
#Revision 1.80  2007/08/24 00:33:08  cdunde
#Additional fixes for the editor vertex selections and the View Options settings.
#
#Revision 1.79  2007/08/23 20:32:59  cdunde
#Fixed the Model Editor Linear Handle to work properly in
#conjunction with the Views Options dialog settings.
#
#Revision 1.78  2007/08/21 11:08:40  cdunde
#Added Model Editor Skin-view 'Ticks' drawing methods, during drags, to its Options menu.
#
#Revision 1.77  2007/08/20 23:14:42  cdunde
#Minor file cleanup.
#
#Revision 1.76  2007/08/20 19:58:24  cdunde
#Added Linear Handle to the Model Editor's Skin-view page
#and setup color selection and drag options for it and other fixes.
#
#Revision 1.75  2007/08/08 21:07:48  cdunde
#To setup red rectangle selection support in the Model Editor for the 3D views using MMB+RMB
#for vertex selection in those views.
#Also setup Linear Handle functions for multiple vertex selection movement using same.
#
#Revision 1.74  2007/08/06 02:37:14  cdunde
#To tie the Linear Handle movements to the X, Y and Z limitation selections.
#
#Revision 1.73  2007/08/02 08:33:54  cdunde
#To get the model axis to draw and other things to work corretly with Linear handle toolbar button.
#
#Revision 1.72  2007/08/01 06:52:25  cdunde
#To allow individual model mesh vertex movement for multiple frames of the same model component
#to work in conjunction with the new Linear Handle functions capable of doing the same.
#
#Revision 1.71  2007/08/01 06:09:25  cdunde
#Setup variable setting for Model Editor 'Linear Handle (size) Setting' and
#'Rotation Speed' using the 'cfg' button on the movement toolbar.
#
#Revision 1.70  2007/07/28 23:12:53  cdunde
#Added ModelEditorLinHandlesManager class and its related classes to the mdlhandles.py file
#to use for editing movement of model faces, vertexes and bones (in the future).
#
#Revision 1.69  2007/07/15 02:00:19  cdunde
#To fix error when redrawing handles in a list when one has been removed.
#
#Revision 1.68  2007/07/14 22:42:45  cdunde
#Setup new options to synchronize the Model Editors view and Skin-view vertex selections.
#Can run either way with single pick selection or rectangle drag selection in all views.
#
#Revision 1.67  2007/07/11 20:40:49  cdunde
#Opps, forgot a couple of things with the last change.
#
#Revision 1.66  2007/07/11 20:00:56  cdunde
#Setup Red Rectangle Selector in the Model Editor Skin-view for multiple selections.
#
#Revision 1.65  2007/07/10 00:24:26  cdunde
#Was still selecting model mesh vertexes when nothing was selected in the tree-view.
#
#Revision 1.64  2007/07/09 18:36:47  cdunde
#Setup editors Rectangle selection to properly create a new triangle if only 3 vertexes
#are selected and a new function to reverse the direction of a triangles creation.
#
#Revision 1.63  2007/07/04 19:11:47  cdunde
#Missed this in the last change.
#
#Revision 1.62  2007/07/04 18:51:23  cdunde
#To fix multiple redraws and conflicts of code for RectSelDragObject in the Model Editor.
#
#Revision 1.61  2007/07/02 22:49:44  cdunde
#To change the old mdleditor "picked" list name to "ModelVertexSelList"
#and "skinviewpicked" to "SkinVertexSelList" to make them more specific.
#Also start of function to pass vertex selection from the Skin-view to the Editor.
#
#Revision 1.60  2007/07/01 04:56:52  cdunde
#Setup red rectangle selection support in the Model Editor for face and vertex
#selection methods and completed vertex selection for all the editors 2D views.
#Added new global in mdlhandles.py "SkinView1" to get the Skin-view,
#which is not in the editors views.
#
#Revision 1.59  2007/06/19 06:16:05  cdunde
#Added a model axis indicator with direction letters for X, Y and Z with color selection ability.
#Added model mesh face selection using RMB and LMB together along with various options
#for selected face outlining, color selections and face color filltris but this will not fill the triangles
#correctly until needed corrections are made to either the QkComponent.pas or the PyMath.pas
#file (for the TCoordinates.Polyline95f procedure).
#Also setup passing selected faces from the editors views to the Skin-view on Options menu.
#
#Revision 1.58  2007/06/11 21:31:45  cdunde
#To fix model mesh vertex handles not always redrawing
#when picked list is cleared or a vertex is deselected.
#
#Revision 1.57  2007/06/07 04:23:21  cdunde
#To setup selected model mesh face colors, remove unneeded globals
#and correct code for model colors.
#
#Revision 1.56  2007/06/05 22:55:57  cdunde
#To stop it from drawing the model mesh selected faces in the Skin-view
#and to try and stop it from loosing the editor. Also removed try statement
#to allow errors to show up so we can TRY to fix them right.
#
#Revision 1.55  2007/06/05 01:17:12  cdunde
#To stop Skin-view not drawing handles and skin mesh if SkinVertexSelList list has not been
#cleared or a component is not selected and the editors layout is changed.
#
#Revision 1.54  2007/06/05 01:08:13  cdunde
#To stop exception error when ModelFaceSelList is not cleared and component is changed.
#
#Revision 1.53  2007/06/03 23:45:23  cdunde
#Changed what was kept in the ModelFaceSelList to only the triangle index number to stop
#Access Violation errors when a drag is made and the objects them selves are changed.
#
#Revision 1.52  2007/06/03 21:58:55  cdunde
#Added new Model Editor lists, ModelFaceSelList and SkinFaceSelList,
#Implementation of the face selection function for the model mesh.
#(To setup a new class, ModelFaceHandle, for the face selection, drawing and menu functions.)
#
#Revision 1.51  2007/06/03 21:09:26  cdunde
#To stop selection from changing on RMB click over model to get RMB menu.
#
#Revision 1.50  2007/06/03 20:56:07  cdunde
#To free up L & RMB combo dragging for Model Editor Face selection use
#and start model face selection and drawing functions.
#
#Revision 1.49  2007/05/25 07:31:57  cdunde
#To stop the drawing of handles in all views after just rotating in a 3D view.
#
#Revision 1.48  2007/05/20 09:13:13  cdunde
#Substantially increased the drawing speed of the
#Model Editor Skin-view mesh lines and handles.
#
#Revision 1.47  2007/05/19 21:23:41  cdunde
#Committed incorrect copy of previous changes.
#
#Revision 1.46  2007/05/19 21:12:39  cdunde
#Changed picked vertex functions to much faster drawing method.
#
#Revision 1.45  2007/05/18 16:56:23  cdunde
#Minor file cleanup and comments.
#
#Revision 1.44  2007/05/18 14:06:35  cdunde
#A little faster way to draw picked model mesh vertexes and clearing them.
#
#Revision 1.43  2007/05/18 04:57:38  cdunde
#Fixed individual view modelfill color to display correctly during a model mesh vertex drag.
#
#Revision 1.42  2007/05/18 02:16:48  cdunde
#To remove duplicate definition of the qbaseeditor.py files def invalidateviews function called
#for in some functions and not others. Too confusing, unnecessary and causes missed functions.
#Also fixed error message when in the Skin-view after a new triangle is added.
#
#Revision 1.41  2007/05/17 23:56:54  cdunde
#Fixed model mesh drag guide lines not always displaying during a drag.
#Fixed gridscale to display in all 2D view(s) during pan (scroll) or drag.
#General code proper rearrangement and cleanup.
#
#Revision 1.40  2007/05/16 20:59:04  cdunde
#To remove unused argument for the mdleditor paintframefill function.
#
#Revision 1.39  2007/05/16 19:39:46  cdunde
#Added the 2D views gridscale function to the Model Editor's Options menu.
#
#Revision 1.38  2007/05/16 06:56:23  cdunde
#To increase drawing speed of Skin-view during drag
#and fix picked vertexes for snapping to base location
#if dragged in the Skin-view before the action is completed.
#
#Revision 1.37  2007/04/27 17:27:42  cdunde
#To setup Skin-view RMB menu functions and possable future MdlQuickKeys.
#Added new functions for aligning, single and multi selections, Skin-view vertexes.
#To establish the Model Editors MdlQuickKeys for future use.
#
#Revision 1.36  2007/04/22 21:06:04  cdunde
#Model Editor, revamp of entire new vertex and triangle creation, picking and removal system
#as well as its code relocation to proper file and elimination of unnecessary code.
#
#Revision 1.35  2007/04/19 03:20:06  cdunde
#To move the selection retention code for the Skin-view vertex drags from the mldhandles.py file
#to the mdleditor.py file so it can be used for many other functions that cause the same problem.
#
#Revision 1.34  2007/04/16 16:55:59  cdunde
#Added Vertex Commands to add, remove or pick a vertex to the open area RMB menu for creating triangles.
#Also added new function to clear the 'Pick List' of vertexes already selected and built in safety limit.
#Added Commands menu to the open area RMB menu for faster and easer selection.
#
#Revision 1.33  2007/04/12 23:57:31  cdunde
#Activated the 'Hints for handles' function for the Model Editors model mesh vertex hints
#and Bone Frames hints. Also added their position data display to the Hint Box.
#
#Revision 1.32  2007/04/12 03:50:22  cdunde
#Added new selector button icons image set for the Skin-view, selection for mesh or vertex drag
#and advanced Skin-view vertex handle positioning and coordinates output data to hint box.
#Also activated the 'Hints for handles' function for the Skin-view.
#
#Revision 1.31  2007/04/11 15:52:16  danielpharos
#Removed a few tabs.
#
#Revision 1.30  2007/04/10 06:00:36  cdunde
#Setup mesh movement using common drag handles
#in the Skin-view for skinning model textures.
#
#Revision 1.29  2007/04/04 21:34:17  cdunde
#Completed the initial setup of the Model Editors Multi-fillmesh and color selection function.
#
#Revision 1.28  2007/03/22 20:14:15  cdunde
#Proper selection and display of skin textures for all model configurations,
#single or multi component, skin or no skin, single or multi skins or any combination.
#
#Revision 1.27  2007/03/10 00:03:27  cdunde
#Start of code to retain selection in Model Editor when making a Skin-view drag.
#
#Revision 1.26  2007/03/04 19:38:52  cdunde
#To redraw handles when LMB is released after rotating model in Model Editor 3D views.
#To stop unneeded redrawing of handles in other views
#
#Revision 1.25  2007/02/20 01:33:59  cdunde
#To stop errors if model component is hidden but shown in Skin-view.
#
#Revision 1.24  2007/01/30 09:13:31  cdunde
#To cut down on more duplicated handle drawing which increases editor response speed.
#
#Revision 1.23  2007/01/30 06:31:40  cdunde
#To get all handles and lines to draw in the Skin-view when not zooming
#and only the minimum lines to draw when it is, to make zooming smoother.
#Also to removed previously added global mouseflags that was giving delayed data
#and replace with global flagsmouse that gives correct data before other functions.
#
#Revision 1.22  2007/01/21 20:37:47  cdunde
#Missed item that should have been commented out in last version.
#
#Revision 1.21  2007/01/21 19:46:57  cdunde
#Cut down on lines and all handles being drawn when zooming in Skin-view to increase drawing speed
#and to fix errors in Model Editor, sometimes there is no currentcomponent.
#
#Revision 1.20  2006/12/18 05:38:14  cdunde
#Added color setting options for various Model Editor mesh and drag lines.
#
#Revision 1.19  2006/12/17 08:58:13  cdunde
#Setup Skin-view proper handle dragging for various model skin(s)
#and no skins combinations.
#
#Revision 1.18  2006/12/13 04:48:18  cdunde
#To draw the 2D and 3D view model vertex handle lines while dragging and
#To remove un-needed redundancy of looping through all of the editors views,
#since they are being passed to the function one at a time anyway and
#sending handles list to another function to go through them again to do nothing.
#
#Revision 1.17  2006/12/06 04:06:31  cdunde
#Fixed Model Editor's Skin-view to draw model mesh correctly and fairly fast.
#
#Revision 1.16  2006/12/03 18:27:38  cdunde
#To draw the Skin-view drag lines when paused with drag.
#
#Revision 1.15  2006/11/30 07:36:19  cdunde
#Temporary fix for view axis icons being lost when vertex on Skin-view is moved.
#
#Revision 1.14  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.13  2006/11/29 07:00:27  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.12.2.14  2006/11/29 03:12:33  cdunde
#To center texture and model mesh in Model Editors Skin-view.
#
#Revision 1.12.2.13  2006/11/28 00:52:48  cdunde
#One more attempt to fix view drag error.
#
#Revision 1.12.2.12  2006/11/27 19:23:45  cdunde
#To fix error message on Skin-view page when drag is started.
#
#Revision 1.12.2.11  2006/11/27 08:31:56  cdunde
#To add the "Rotate at start position" method to the Model Editors rotation options menu.
#
#Revision 1.12.2.10  2006/11/23 06:25:21  cdunde
#Started dragging lines support for Skin-view vertex movement
#and rearranged need code for 4 place indention format.
#
#Revision 1.12.2.9  2006/11/22 19:26:52  cdunde
#To add new globals mdleditorsave, mdleditorview and cursorposatstart for the
#Model Editor, view the LMB is pressed in and the cursors starting point location,
#as a vector, on that view. These globals can be imported to any other file for use.
#
#Revision 1.12.2.8  2006/11/17 05:06:55  cdunde
#To stop blipping of background skin texture,
#fix Python 2.4 Depreciation Warning messages,
#and remove unneeded code at this time.
#
#Revision 1.12.2.7  2006/11/16 01:01:54  cdunde
#Added code to activate the movement of the Skin-view skin handles for skinning.
#
#Revision 1.12.2.6  2006/11/16 00:49:13  cdunde
#Added code to draw skin mesh lines in Skin-view.
#
#Revision 1.12.2.5  2006/11/16 00:08:21  cdunde
#To properly align model skin with its mesh movement handles and zooming function.
#
#Revision 1.12.2.4  2006/11/15 23:06:14  cdunde
#Updated bone handle size and to allow for future variable of them.
#
#Revision 1.12.2.3  2006/11/15 22:34:20  cdunde
#Added the drawing of misc model items and bones to stop errors and display them.
#
#Revision 1.12.2.2  2006/11/04 21:41:23  cdunde
#To setup the Model Editor's Skin-view and display the skin
#for .mdl, .md2 and .md3 models using .pcx, .jpg and .tga files.
#
#Revision 1.12.2.1  2006/11/03 23:38:09  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.12  2006/03/07 08:08:28  cdunde
#To enlarge model Tick Marks hard to see 1 pixel size
#and added item to Options menu to make 1 size bigger.
#
#Revision 1.11  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.8  2001/03/15 21:07:49  aiv
#fixed bugs found by fpbrowser
#
#Revision 1.7  2001/02/07 18:40:47  aiv
#bezier texture vertice page started.
#
#Revision 1.6  2001/02/05 20:03:12  aiv
#Fixed stupid bug when displaying texture vertices
#
#Revision 1.5  2000/10/11 19:07:47  aiv
#Bones, and some kinda skin vertice viewer
#
#Revision 1.4  2000/08/21 21:33:04  aiv
#Misc. Changes / bugfixes
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#