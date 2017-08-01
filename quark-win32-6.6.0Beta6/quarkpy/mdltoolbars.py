"""   QuArK  -  Quake Army Knife

The model editor's "Toolbars" menu (to be extended by plug-ins)
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mdltoolbars.py,v 1.18 2011/11/17 01:19:02 cdunde Exp $


import qmenu
from mdlutils import *
import qeditor
import qhandles
import mdleditor
import mdlhandles

parent = qhandles.RectangleDragObject


class DisplayBar(qeditor.ToolBar):
    "The standard Display tool bar."

    Caption = "Display"
    DefaultPos = ((0,0,0,0), "topdock", 0, 0, 1)

    def buildbuttons(self, layout):
        ico_maped=ico_dict['ico_maped']
        gridbtn = qtoolbar.doublebutton(layout.editor.togglegrid, layout.getgridmenu, "grid||The grid is the pattern of dots on the map that 'snaps' mouse moves.\n\nThis 'grid' button has two parts : you can click either on the icon and get a menu that lets you select the grid size you like, or you can click on the text itself, which toggles the grid on/off without hiding it.", ico_maped, 7, infobaselink="intro.modeleditor.toolpalettes.display.html#grid")

        gridbtn.caption = "128"  # to determine the button width

        zoombtn = qtoolbar.doublebutton(layout.autozoom1click, getzoommenu, "choose zoom factor / zoom to fit the level or the selection||This button lets you zoom in or out. This button has two parts.\n\nClick on the icon to get a list of common zoom factors, or to enter a custom factor with the keyboard.\n\nClick on the text ('zoom') besides the icon to 'auto-zoom' in and out : the first time you click, the scale is choosen so that you can see the entire model at a glance.", ico_maped, 14, infobaselink="intro.modeleditor.toolpalettes.display.html#zoom")
        zoombtn.near = 1
        zoombtn.views = layout.views
        zoombtn.caption = "zoom"

        Btn3D = qtoolbar.button(layout.full3Dclick, "Full 3D view||Full 3D view will create a new floating 3D-window, which you can place anywhere on your desktop and resize as you wish.\n\nAdditional 3D windows can be opened if the 'Allow multiple 3D windows' option is selected in the Configuration, General, 3D view, Additional settings section.", ico_maped, 21, infobaselink="intro.modeleditor.toolpalettes.display.html#3dwindows")

        LinearVBtn = qtoolbar.button(layout.editor.linear1click, "Linear Drag Handles||Linear Drag Handles:\n\nThis button is always active in one way or another and performs various ways in different modes in the Model Editor, depending on what is selected, and the Skin-view. When more then one item is selected it will display a 'Linear Drag Handle' circle around those selected objects for editing purposes.\n\nThis circle and its attached handles let you apply 'linear movement' to the objects. 'Linear movement' means any transformation such as group movement, rotation, enlarging/shrinking and distortion/shearing. When you use the rotate, enlarge, shrink, and symmetry buttons of the movement tool palette, you actually apply a linear movement on the selected objects.\n\nClick the 'InfoBase' button for more details on its uses.", ico_maped, 19,  infobaselink="intro.modeleditor.toolpalettes.display.html#linear")

        LockViewsBtn = qtoolbar.button(layout.editor.lockviewsclick, "Lock views||Lock views:\n\nThis will cause all of the 2D views to move and zoom together.\n\nWhen this is in the unlocked mode, the 2d views can then be moved and zoomed on individually.\n\nIf the lock is reset then the 2D views will realign themselves.", ico_maped, 28, infobaselink="intro.modeleditor.toolpalettes.display.html#lockviews")

        helpbtn = qtoolbar.button(layout.helpbtnclick, "Contextual help||Contextual help:\n\nWill open up your web-browser, and display the QuArK main help page.", ico_maped, 13, infobaselink="intro.modeleditor.toolpalettes.display.html#helpbook")

        layout.buttons.update({"grid": gridbtn, "3D": Btn3D, "linear": LinearVBtn, "lockv": LockViewsBtn})

        return [gridbtn, zoombtn, Btn3D, LinearVBtn, LockViewsBtn, helpbtn]


# Extrude selected faces in the ModelFaceSelList without bulkheads function.
def extrudeclick(m):
    editor = mdleditor.mdleditor
    qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_edittools"]
    tb2 = editor.layout.toolbars["tb_objmodes"]
    tb3 = editor.layout.toolbars["tb_AxisLock"]
    if not MdlOption("ExtrudeFaces"):
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] = "1"
        tb1.tb.buttons[0].state = qtoolbar.selected
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
        tb1.tb.buttons[1].state = qtoolbar.normal
        tb1.tb.buttons[7].state = qtoolbar.normal
        for b in tb2.tb.buttons:
            b.state = qtoolbar.normal
        tb2.tb.buttons[1].state = qtoolbar.selected
        for b in range(len(tb3.tb.buttons)):
            if b == 5:
                tb3.tb.buttons[b].state = qtoolbar.normal
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", 0)
        editor.MouseDragMode = mdlhandles.RectSelDragObject
        # All code below in this section checks for proper selection if in vertex mode.
        if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
            if len(editor.ModelVertexSelList) > 1:
                editor.SelVertexes = []
                editor.SelCommonTriangles = []
                comp = editor.Root.currentcomponent
                for vtx in editor.ModelVertexSelList:
                    if vtx in editor.SelVertexes:
                        pass
                    else:
                        editor.SelVertexes = editor.SelVertexes + [vtx]
                for vtx in editor.SelVertexes:
                    checktris = findTrianglesAndIndexes(comp, vtx, None)
                    for tri in checktris:
                        if editor.SelCommonTriangles == []:
                            editor.SelCommonTriangles = editor.SelCommonTriangles + [tri]
                            continue
                        for comtri in range(len(editor.SelCommonTriangles)):
                            if tri[2] == editor.SelCommonTriangles[comtri][2]:
                                break
                            if comtri == len(editor.SelCommonTriangles)-1:
                                editor.SelCommonTriangles = editor.SelCommonTriangles + [tri]
                templist = []
                keepvtx = []
                for tri in editor.SelCommonTriangles:
                    vtxcount = 0
                    keep1 = keep2 = keep3 = None
                    for vtx in editor.SelVertexes:
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

                editor.SelCommonTriangles = perimeter_edge
                if editor.SelCommonTriangles == [] and editor.ModelVertexSelList != []:
                    quarkx.msgbox("Improper Selection !\n\nYou must select the two\nvertexes of each triangle's edge\nthat is to be extruded.\n\nOnly one vertex of a triangle\nis in your selection.", MT_ERROR, MB_OK)
                    editor.SelVertexes = []
                    editor.SelCommonTriangles = []
                    return
                if len(editor.SelVertexes) != len(edgevtxs):
                    editor.SelVertexes = edgevtxs
                    templist = []
                    for vtx in editor.ModelVertexSelList:
                       if not (vtx in editor.SelVertexes):
                           pass
                       else:
                           templist = templist + [vtx]
                    editor.ModelVertexSelList = templist
                    Update_Editor_Views(editor)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] = None
        tb1.tb.buttons[0].state = qtoolbar.normal
        quarkx.update(editor.form)
        comp = editor.Root.currentcomponent
        editor.SelCommonTriangles = []
        editor.SelVertexes = []
        for tri in editor.ModelFaceSelList:
            for vtx in range(len(comp.triangles[tri])):
                if comp.triangles[tri][vtx][0] in editor.SelVertexes:
                    pass
                else:
                    editor.SelVertexes = editor.SelVertexes + [comp.triangles[tri][vtx][0]] 
                editor.SelCommonTriangles = editor.SelCommonTriangles + findTrianglesAndIndexes(comp, comp.triangles[tri][vtx][0], None)
        MakeEditorFaceObject(editor)



# Extrude selected faces in the ModelFaceSelList with bulkheads function.
def extrudebulkheadsclick(m):
    editor = mdleditor.mdleditor
    qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_edittools"]
    tb2 = editor.layout.toolbars["tb_objmodes"]
    tb3 = editor.layout.toolbars["tb_AxisLock"]
    if not MdlOption("ExtrudeBulkHeads"):
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] = "1"
        tb1.tb.buttons[1].state = qtoolbar.selected
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
        tb1.tb.buttons[0].state = qtoolbar.normal
        tb1.tb.buttons[7].state = qtoolbar.normal
        for b in tb2.tb.buttons:
            b.state = qtoolbar.normal
        tb2.tb.buttons[1].state = qtoolbar.selected
        for b in range(len(tb3.tb.buttons)):
            if b == 5:
                tb3.tb.buttons[b].state = qtoolbar.normal
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", 0)
        editor.MouseDragMode = mdlhandles.RectSelDragObject
        # All code below in this section checks for proper selection if in vertex mode.
        if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1":
            if len(editor.ModelVertexSelList) > 1:
                editor.SelVertexes = []
                editor.SelCommonTriangles = []
                comp = editor.Root.currentcomponent
                for vtx in editor.ModelVertexSelList:
                    if vtx in editor.SelVertexes:
                        pass
                    else:
                        editor.SelVertexes = editor.SelVertexes + [vtx]
                for vtx in editor.SelVertexes:
                    checktris = findTrianglesAndIndexes(comp, vtx, None)
                    for tri in checktris:
                        if editor.SelCommonTriangles == []:
                            editor.SelCommonTriangles = editor.SelCommonTriangles + [tri]
                            continue
                        for comtri in range(len(editor.SelCommonTriangles)):
                            if tri[2] == editor.SelCommonTriangles[comtri][2]:
                                break
                            if comtri == len(editor.SelCommonTriangles)-1:
                                editor.SelCommonTriangles = editor.SelCommonTriangles + [tri]
                templist = []
                keepvtx = []
                for tri in editor.SelCommonTriangles:
                    vtxcount = 0
                    keep1 = keep2 = keep3 = None
                    for vtx in editor.SelVertexes:
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
                editor.SelCommonTriangles = templist
                if editor.SelCommonTriangles == [] and editor.ModelVertexSelList != []:
                    quarkx.msgbox("Improper Selection !\n\nYou must select at least two\nvertexes of each triangle's edge\nthat is to be extruded.\n\nOnly one vertex of a triangle\nis in your selection.", MT_ERROR, MB_OK)
                    editor.SelVertexes = []
                    editor.SelCommonTriangles = []
                    return
                if len(editor.SelVertexes) != len(keepvtx):
                    editor.SelVertexes = keepvtx
                    templist = []
                    for vtx in editor.ModelVertexSelList:
                       if not (vtx in editor.SelVertexes):
                           pass
                       else:
                           templist = templist + [vtx]
                    editor.ModelVertexSelList = templist
                    Update_Editor_Views(editor)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] = None
        tb1.tb.buttons[1].state = qtoolbar.normal
        quarkx.update(editor.form)
        comp = editor.Root.currentcomponent
        editor.SelCommonTriangles = []
        editor.SelVertexes = []
        for tri in editor.ModelFaceSelList:
            for vtx in range(len(comp.triangles[tri])):
                if comp.triangles[tri][vtx][0] in editor.SelVertexes:
                    pass
                else:
                    editor.SelVertexes = editor.SelVertexes + [comp.triangles[tri][vtx][0]] 
                editor.SelCommonTriangles = editor.SelCommonTriangles + findTrianglesAndIndexes(comp, comp.triangles[tri][vtx][0], None)
        MakeEditorFaceObject(editor)


# Reverse selected faces direction in the ModelFaceSelList function.
def ReverseFaceClick(m):
    editor = mdleditor.mdleditor
    ReverseFaces(editor)


# Splits up selected faces in the ModelFaceSelList into 2 new triangles function.
def Subdivide2Click(m):
    editor = mdleditor.mdleditor
    SubdivideFaces(editor, 2)


# Splits up selected faces in the ModelFaceSelList into 3 new triangles function.
def Subdivide3Click(m):
    editor = mdleditor.mdleditor
    SubdivideFaces(editor, 3)


# Splits up selected faces in the ModelFaceSelList into 4 new triangles function.
def Subdivide4Click(m):
    editor = mdleditor.mdleditor
    SubdivideFaces(editor, 4)


class FaceCutter(parent):
    "Cuts selected faces into parts along the line drawn."

    Hint = hintPlusInfobaselink("Cut selected faces in two||Cut selected faces in two:\n\nAfter you click this button, you can draw lines on the map with the mouse, and any polyhedron touching this line will be cut in two parts along it. This is a quick way to make complex shapes out of a single polyhedron. You can for example draw 3 lines in a wall to make the contour of a passage, and then just delete the middle polyhedron to actually make the hole.\n\nAdvanced features : if you select a face, it will be cut in two but not the other faces of the polyhedron (using \"face sharing\" techniques); and if you select a group, instead of cutting each polyhedron in two individually, QuArK will give you the option of making two copies of the whole group with the cutting plane as a shared face in each group. This lets you consider the cutting plane as a unique face and later move or rotate it to reshape all polyhedrons in the group at once.", "intro.mapeditor.toolpalettes.mousemodes.html#polycutter")

    def __init__(self, view, x, y, redcolor, todo):
        parent.__init__(self, view, x, y, redcolor, todo)
        self.pt0 = qhandles.aligntogrid(self.pt0, 1)
        p = view.proj(self.pt0)
        if p.visible:
            self.x0 = p.x
            self.y0 = p.y

    def buildredimages(self, x, y, flags):
        p = self.view.proj(qhandles.aligntogrid(self.view.space(x, y, self.z0), 1))
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

    def drawredimages(self, view, internal=0):
        editor = self.editor
        if self.redimages is not None:
            mode = DM_OTHERCOLOR|DM_BBOX
            special, refresh = self.ricmd()
            if special is None:    # Can only draw a red image or redraw over it to make it disappear.
                if internal==1:    # Erase (hides) the previously drawn red line by redrawing over it using the VIEW background color.
                    ## This draws the red line (cutting face) during a drag.
                    for r in self.redimages:
                        view.drawmap(r, mode, view.color)
                if internal==2:    # Draw a red image.
                    for r in self.redimages:
                        view.drawmap(r, mode, self.redcolor)

    def rectanglesel(self, editor, x, y, face):
        x1, y1 = self.x0, self.y0 # cursordragstartpos
        x2, y2 = (x, y) # cursordragendpos
        view = self.view
        comp = editor.Root.currentcomponent
        import qbaseeditor
        from qbaseeditor import flagsmouse

        def redrawview(editor=editor, view=view):
            from qbaseeditor import flagsmouse
            qbaseeditor.flagsmouse = 1032
            mdleditor.setsingleframefillcolor(editor, view)
            view.repaint()
            if editor.ModelFaceSelList != []:
                mdlhandles.ModelFaceHandle(qhandles.GenericHandle).draw(editor, view, editor.EditorObjectList)
            cv = view.canvas()
            for h in view.handles:
                h.draw(view, cv, h)

        def GetIntersectionPoint(v1, v2, z=0.0):
            x3, y3 = v1[0], v1[1]
            x4, y4 = v2[0], v2[1]
            try: # To avoid division by zero errors.
                ua = (((x4-x3)*(y1-y3)) - ((y4-y3)*(x1-x3))) / (((y4-y3)*(x2-x1)) - ((x4-x3)*(y2-y1)))
            except:
                ua = 0.0
            x = x1+ua*(x2-x1)
            y = y1+ua*(y2-y1)
            return view.space(quarkx.vect(x,y,z))

        if flagsmouse == 2072: # Cancels face cutting.
            redrawview()
            return

        if (len(editor.ModelFaceSelList) < 1) or (comp is None):
            quarkx.msgbox("No selection has been made\n\nYou must first select some faces of a\nmodel component to subdivide those faces.", MT_ERROR, MB_OK)
            redrawview()
            return
        sellist = editor.layout.explorer.sellist
        if len(sellist) == 0:
            quarkx.msgbox("Improper Action - no frame selection.\n\nYou must first select a frame and some faces\nof a model component to subdivide those faces.", MT_ERROR, MB_OK)
            redrawview()
            return
        for item in range(len(sellist)):
            if sellist[item].type == ":mf":
                break
            if item == len(sellist)-1:
                quarkx.msgbox("Improper Action - no frame selection.\n\nYou must first select a frame and some faces\nof a model component to subdivide those faces.", MT_ERROR, MB_OK)
                redrawview()
                return

        selected_faces = editor.EditorObjectList
        cut_faces = []
        vtxs = comp.currentframe.vertices
        n = face.normal
        # Section below determines which selected faces will get cut because the cut line crosses
        # over them and places only those faces into the cut_faces list for processing.
        for sel_face in selected_faces:
            vs = sel_face.name.split(":")[0]
            vs = vs.split(",")
            v0, v1, v2 = vtxs[int(vs[2])], vtxs[int(vs[3])], vtxs[int(vs[4])]
            vtx = [v0, v1, v2]
            gotv1 = vtx[-1]
            prevv = gotv1*n < face.dist
            for v in vtx:
                nextv = v*n < face.dist    # 0 or 1
                if prevv+nextv==1:   # The two vertices are not on the same side of the cutting plane.
                    gotv2 = v
                    break
                prevv = nextv
                gotv1 = v
            else:
                continue   # The cutting plane doesn't cross this face.

            cut_faces = cut_faces + [sel_face]

        num_cut_faces = len(cut_faces)
        if num_cut_faces == 0:
            redrawview()
            return

        max_cut_faces = num_cut_faces-1
        new_comp = comp.copy()
        new_tris = comp.triangles # Update at very end using lists below, "new_tris_dict" FIRST then "new_tris_added" second.
        triangles = comp.triangles
        tris_index = len(triangles)-1
        newfaceselection = []
        vtx_index_start = vtx_index = len(vtxs)-1
        new_compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        curframe = comp.currentframe
        old_vtxs = curframe.vertices
        new_comp.currentframe = new_compframes[curframe.index]

        # Used to store new tris data until very end for updating the component's "Tris".
        new_tris_dict = {}  # Dictionary list for existing changed cut_faces, uses cf_nbr as key.
        new_tris_added = [] # Standard list for new triangle faces added from the cut_face cuts.

        # Used later to store new vertexes and remove dupe vertexes if desired.
        VTX_DATA_LIST = []

        ### Section below creates the new vertex cutting data for all the faces that will be cut.
        for f in xrange(num_cut_faces):
            vs = cut_faces[f].name.split(":")[0]
            vs = vs.split(",")
            comp_name = vs[0]
            cf_nbr = int(vs[1])
            cut_face = triangles[cf_nbr]
            cf_indexes = [int(vs[2]), int(vs[3]), int(vs[4])]
            v = cut_faces[f].dictspec['v']
            vtxs = [(v[0],v[1],v[2]), (v[3],v[4],v[5]), (v[6],v[7],v[8])]

            # Determines which vertices are on the same side of the cut line (which is really a  poly face).
            side0 = quarkx.vect(vtxs[0])*n < face.dist
            side1 = quarkx.vect(vtxs[1])*n < face.dist
            side2 = quarkx.vect(vtxs[2])*n < face.dist
            # These are the cut_face original vertexes.
            if side0 == side1:
                single_vertex = 2
            else:
                if side2 == side0:
                    single_vertex = 1
                else:
                    single_vertex = 0

            # Computes the intersection point for each set of vertexes x,y,z values for this cut_face.
            v0 = view.proj(quarkx.vect(vtxs[0])).tuple
            v1 = view.proj(quarkx.vect(vtxs[1])).tuple
            v2 = view.proj(quarkx.vect(vtxs[2])).tuple

            p0 = GetIntersectionPoint(v0, v1).tuple
            p1 = GetIntersectionPoint(v1, v2).tuple
            p2 = GetIntersectionPoint(v2, v0).tuple
            IP = [p0, p1, p2] # Only two are valid intersection points, the bad one will be determined later.

            ### Section below computes the new vertex cutting data for the Z view.
            if view.info['type'] == "XY": # Z view
                DATA_A = DATA_B = None

                def CalcNewVert(vtx1, vtx2, vtx_index):
                    ### Because each frame's cut_faces vertexes can be different (due to animation)
                    ### their positions must be determined as a percentage of movement.
                    ### To do this we use the current frame to compute those x, y and z percentages
                    ### that will be applied to those vert_index positions for each frame later.

                    # For Xpercent of movement.
                    diff = vtxs[vtx2][0] - vtxs[vtx1][0]
                    part = IP[vtx1][0] - vtxs[vtx1][0]
                    Xpercent = 0.0
                    if diff != 0:
                        Xpercent = part / diff
                    Xamt = (diff * Xpercent) + vtxs[vtx1][0]

                    # For Ypercent of movement.
                    diff = vtxs[vtx2][1] - vtxs[vtx1][1]
                    part = IP[vtx1][1] - vtxs[vtx1][1]
                    Ypercent = 0.0
                    if diff != 0:
                        Ypercent = part / diff
                    Yamt = (diff * Ypercent) + vtxs[vtx1][1]

                    # For Zpercent of movement.
                    item = 0
                    if (vtxs[vtx1][0] == vtxs[vtx2][0]) or (abs(vtxs[vtx1][1]) + abs(vtxs[vtx2][1]) > abs(vtxs[vtx1][0]) + abs(vtxs[vtx2][0]) and vtxs[vtx1][1] != vtxs[vtx2][1]):
                        item = 1
                    diff = vtxs[vtx2][item] - vtxs[vtx1][item]
                    part = IP[vtx1][item] - vtxs[vtx1][item]
                    Zpercent = 0.0
                    if diff != 0:
                        Zpercent = part / diff
                    Zdiff = vtxs[vtx2][2] - vtxs[vtx1][2]
                    Zamt = (Zdiff * Zpercent) + vtxs[vtx1][2]

                    # This is the new vertex position.
                    vert_pos = quarkx.vect((Xamt, Yamt, Zamt))

                    # Calculate new U, V.
                    pos_diff = quarkx.vect(vtxs[vtx2]) - quarkx.vect(vtxs[vtx1])
                    pos_new = vert_pos - quarkx.vect(vtxs[vtx1])
                    along_the_line = (pos_new * pos_diff) / (pos_diff * pos_diff)
                    U = int(round(cut_face[vtx1][1] * (1 - along_the_line) + cut_face[vtx2][1] * along_the_line))
                    V = int(round(cut_face[vtx1][2] * (1 - along_the_line) + cut_face[vtx2][2] * along_the_line))

                    vtx_index = vtx_index + 1
                    return vtx_index, (vtx_index, cut_face, vtx1, vtx2, vert_pos, U, V, Xpercent, Ypercent, Zpercent)

                ### Section below makes the data lists needed
                ### to add the two new vertexes that will be created
                ### for each face that will get cut from 1 triangle into 3 triangles.
                ### This is needed to avoid having 1 triangle and 1 rectangle (not allowed).

                if single_vertex == 0:
                    vtx_index, DATA_A = CalcNewVert(0, 1, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(2, 0, vtx_index)
                if single_vertex == 1:
                    vtx_index, DATA_A = CalcNewVert(0, 1, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(1, 2, vtx_index)
                if single_vertex == 2:
                    vtx_index, DATA_A = CalcNewVert(1, 2, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(2, 0, vtx_index)

                VTX_DATA_LIST = VTX_DATA_LIST + [DATA_A, DATA_B]
                vtx_index_A, cut_face_A, vtx1_A, vtx2_A, vert_pos_A, U_A, V_A, Xpercent, Ypercent, Zpercent = DATA_A
                vtx_index_B, cut_face_B, vtx1_B, vtx2_B, vert_pos_B, U_B, V_B, Xpercent, Ypercent, Zpercent = DATA_B

                ### Section below applys the new vertex cutting data for the component's Tris
                ### based on which face will contain only one original vertex (retains original tri_index)
                ### and two new vertexes made from lists DATA_A and DATA_B (adding two new tri_indexes & vtx_indexes).
                if single_vertex == 0:
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_A, U_A, V_A), new_tris[cf_nbr][1], (vtx_index_B, U_B, V_B))]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_B, U_B, V_B), new_tris[cf_nbr][1], new_tris[cf_nbr][2])]

                    new_tris_dict[cf_nbr] = (new_tris[cf_nbr][single_vertex], (vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B))

                if single_vertex == 1:
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B), new_tris[cf_nbr][0])]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][0], (vtx_index_B, U_B, V_B), new_tris[cf_nbr][2])]

                    new_tris_dict[cf_nbr] = ((vtx_index_A, U_A, V_A), new_tris[cf_nbr][single_vertex], (vtx_index_B, U_B, V_B))

                if single_vertex == 2:
                    # List below stores new triangle(s) only, to be added to the end of the component's Tris later.
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][0], new_tris[cf_nbr][1], (vtx_index_B, U_B, V_B))]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][1], (vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B))]

                    # List below stores resized original cut_face triangle(s) only by their tri_index, to be updated later.
                    new_tris_dict[cf_nbr] = ((vtx_index_B, U_B, V_B), (vtx_index_A, U_A, V_A), new_tris[cf_nbr][single_vertex])

            elif view.info['type'] == "YZ": # X view
                DATA_A = DATA_B = None

                def CalcNewVert(vtx1, vtx2, vtx_index):
                    ### Because each frame's cut_faces vertexes can be different (due to animation)
                    ### their positions must be determined as a percentage of movement.
                    ### To do this we use the current frame to compute those x, y and z percentages
                    ### that will be applied to those vert_index positions for each frame later.

                    # For Xpercent of movement.
                    item = 1
                    if (vtxs[vtx1][1] == vtxs[vtx2][1]) or (abs(vtxs[vtx1][2]) + abs(vtxs[vtx2][2]) > abs(vtxs[vtx1][1]) + abs(vtxs[vtx2][1]) and vtxs[vtx1][2] != vtxs[vtx2][2]):
                        item = 2
                    diff = vtxs[vtx2][item] - vtxs[vtx1][item]
                    part = IP[vtx1][item] - vtxs[vtx1][item]
                    Xpercent = 0.0
                    if diff != 0:
                        Xpercent = part / diff
                    Xdiff = vtxs[vtx2][0] - vtxs[vtx1][0]
                    Xamt = (Xdiff * Xpercent) + vtxs[vtx1][0]

                    # For Ypercent of movement.
                    diff = vtxs[vtx2][1] - vtxs[vtx1][1]
                    part = IP[vtx1][1] - vtxs[vtx1][1]
                    Ypercent = 0.0
                    if diff != 0:
                        Ypercent = part / diff
                    Yamt = (diff * Ypercent) + vtxs[vtx1][1]

                    # For Zpercent of movement.
                    diff = vtxs[vtx2][2] - vtxs[vtx1][2]
                    part = IP[vtx1][2] - vtxs[vtx1][2]
                    Zpercent = 0.0
                    if diff != 0:
                        Zpercent = part / diff
                    Zamt = (diff * Zpercent) + vtxs[vtx1][2]

                    # This is the new vertex position.
                    vert_pos = quarkx.vect((Xamt, Yamt, Zamt))

                    # Calculate new U, V.
                    pos_diff = quarkx.vect(vtxs[vtx2]) - quarkx.vect(vtxs[vtx1])
                    pos_new = vert_pos - quarkx.vect(vtxs[vtx1])
                    along_the_line = (pos_new * pos_diff) / (pos_diff * pos_diff)
                    U = int(round(cut_face[vtx1][1] * (1 - along_the_line) + cut_face[vtx2][1] * along_the_line))
                    V = int(round(cut_face[vtx1][2] * (1 - along_the_line) + cut_face[vtx2][2] * along_the_line))

                    vtx_index = vtx_index + 1
                    return vtx_index, (vtx_index, cut_face, vtx1, vtx2, vert_pos, U, V, Xpercent, Ypercent, Zpercent)

                ### Section below makes the data lists needed
                ### to add the two new vertexes that will be created
                ### for each face that will get cut from 1 triangle into 3 triangles.
                ### This is needed to avoid having 1 triangle and 1 rectangle (not allowed).

                if single_vertex == 0:
                    vtx_index, DATA_A = CalcNewVert(0, 1, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(2, 0, vtx_index)
                if single_vertex == 1:
                    vtx_index, DATA_A = CalcNewVert(0, 1, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(1, 2, vtx_index)
                if single_vertex == 2:
                    vtx_index, DATA_A = CalcNewVert(1, 2, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(2, 0, vtx_index)

                VTX_DATA_LIST = VTX_DATA_LIST + [DATA_A, DATA_B]
                vtx_index_A, cut_face_A, vtx1_A, vtx2_A, vert_pos_A, U_A, V_A, Xpercent, Ypercent, Zpercent = DATA_A
                vtx_index_B, cut_face_B, vtx1_B, vtx2_B, vert_pos_B, U_B, V_B, Xpercent, Ypercent, Zpercent = DATA_B

                ### Section below applys the new vertex cutting data for the component's Tris
                ### based on which face will contain only one original vertex (retains original tri_index)
                ### and two new vertexes made from lists DATA_A and DATA_B (adding two new tri_indexes & vtx_indexes).
                if single_vertex == 0:
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_A, U_A, V_A), new_tris[cf_nbr][1], (vtx_index_B, U_B, V_B))]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_B, U_B, V_B), new_tris[cf_nbr][1], new_tris[cf_nbr][2])]

                    new_tris_dict[cf_nbr] = (new_tris[cf_nbr][single_vertex], (vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B))

                if single_vertex == 1:
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B), new_tris[cf_nbr][0])]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][0], (vtx_index_B, U_B, V_B), new_tris[cf_nbr][2])]

                    new_tris_dict[cf_nbr] = ((vtx_index_A, U_A, V_A), new_tris[cf_nbr][single_vertex], (vtx_index_B, U_B, V_B))

                if single_vertex == 2:

                    # List below stores new triangle(s) only, to be added to the end of the component's Tris later.
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][0], new_tris[cf_nbr][1], (vtx_index_B, U_B, V_B))]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][1], (vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B))]

                    # List below stores resized original cut_face triangle(s) only by their tri_index, to be updated later.
                    new_tris_dict[cf_nbr] = ((vtx_index_B, U_B, V_B), (vtx_index_A, U_A, V_A), new_tris[cf_nbr][single_vertex])


            else: # Y view
                DATA_A = DATA_B = None

                def CalcNewVert(vtx1, vtx2, vtx_index):
                    ### Because each frame's cut_faces vertexes can be different (due to animation)
                    ### their positions must be determined as a percentage of movement.
                    ### To do this we use the current frame to compute those x, y and z percentages
                    ### that will be applied to those vert_index positions for each frame later.

                    # For Xpercent of movement.
                    diff = vtxs[vtx2][0] - vtxs[vtx1][0]
                    part = IP[vtx1][0] - vtxs[vtx1][0]
                    Xpercent = 0.0
                    if diff != 0:
                        Xpercent = part / diff
                    Xamt = (diff * Xpercent) + vtxs[vtx1][0]

                    # For Ypercent of movement.
                    item = 0
                    if (vtxs[vtx1][0] == vtxs[vtx2][0]) or (abs(vtxs[vtx1][2]) + abs(vtxs[vtx2][2]) > abs(vtxs[vtx1][0]) + abs(vtxs[vtx2][0]) and vtxs[vtx1][2] != vtxs[vtx2][2]):
                        item = 2
                    diff = vtxs[vtx2][item] - vtxs[vtx1][item]
                    part = IP[vtx1][item] - vtxs[vtx1][item]
                    Ypercent = 0.0
                    if diff != 0:
                        Ypercent = part / diff
                    Ydiff = vtxs[vtx2][1] - vtxs[vtx1][1]
                    Yamt = (Ydiff * Ypercent) + vtxs[vtx1][1]

                    # For Zpercent of movement.
                    diff = vtxs[vtx2][2] - vtxs[vtx1][2]
                    part = IP[vtx1][2] - vtxs[vtx1][2]
                    Zpercent = 0.0
                    if diff != 0:
                        Zpercent = part / diff
                    Zamt = (diff * Zpercent) + vtxs[vtx1][2]

                    # This is the new vertex position.
                    vert_pos = quarkx.vect((Xamt, Yamt, Zamt))

                    # Calculate new U, V.
                    pos_diff = quarkx.vect(vtxs[vtx2]) - quarkx.vect(vtxs[vtx1])
                    pos_new = vert_pos - quarkx.vect(vtxs[vtx1])
                    along_the_line = (pos_new * pos_diff) / (pos_diff * pos_diff)
                    U = int(round(cut_face[vtx1][1] * (1 - along_the_line) + cut_face[vtx2][1] * along_the_line))
                    V = int(round(cut_face[vtx1][2] * (1 - along_the_line) + cut_face[vtx2][2] * along_the_line))

                    vtx_index = vtx_index + 1
                    return vtx_index, (vtx_index, cut_face, vtx1, vtx2, vert_pos, U, V, Xpercent, Ypercent, Zpercent)

                ### Section below makes the data lists needed
                ### to add the two new vertexes that will be created
                ### for each face that will get cut from 1 triangle into 3 triangles.
                ### This is needed to avoid having 1 triangle and 1 rectangle (not allowed).

                if single_vertex == 0:
                    vtx_index, DATA_A = CalcNewVert(0, 1, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(2, 0, vtx_index)
                if single_vertex == 1:
                    vtx_index, DATA_A = CalcNewVert(0, 1, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(1, 2, vtx_index)
                if single_vertex == 2:
                    vtx_index, DATA_A = CalcNewVert(1, 2, vtx_index)
                    vtx_index, DATA_B = CalcNewVert(2, 0, vtx_index)

                VTX_DATA_LIST = VTX_DATA_LIST + [DATA_A, DATA_B]
                vtx_index_A, cut_face_A, vtx1_A, vtx2_A, vert_pos_A, U_A, V_A, Xpercent, Ypercent, Zpercent = DATA_A
                vtx_index_B, cut_face_B, vtx1_B, vtx2_B, vert_pos_B, U_B, V_B, Xpercent, Ypercent, Zpercent = DATA_B

                ### Section below applys the new vertex cutting data for the component's Tris
                ### based on which face will contain only one original vertex (retains original tri_index)
                ### and two new vertexes made from lists DATA_A and DATA_B (adding two new tri_indexes & vtx_indexes).
                if single_vertex == 0:
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_A, U_A, V_A), new_tris[cf_nbr][1], (vtx_index_B, U_B, V_B))]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_B, U_B, V_B), new_tris[cf_nbr][1], new_tris[cf_nbr][2])]

                    new_tris_dict[cf_nbr] = (new_tris[cf_nbr][single_vertex], (vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B))

                if single_vertex == 1:
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [((vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B), new_tris[cf_nbr][0])]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][0], (vtx_index_B, U_B, V_B), new_tris[cf_nbr][2])]

                    new_tris_dict[cf_nbr] = ((vtx_index_A, U_A, V_A), new_tris[cf_nbr][single_vertex], (vtx_index_B, U_B, V_B))

                if single_vertex == 2:

                    # List below stores new triangle(s) only, to be added to the end of the component's Tris later.
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][0], new_tris[cf_nbr][1], (vtx_index_B, U_B, V_B))]
 
                    tris_index = tris_index + 1
                    newfaceselection = newfaceselection + [tris_index]
                    new_tris_added = new_tris_added + [(new_tris[cf_nbr][1], (vtx_index_A, U_A, V_A), (vtx_index_B, U_B, V_B))]

                    # List below stores resized original cut_face triangle(s) only by their tri_index, to be updated later.
                    new_tris_dict[cf_nbr] = ((vtx_index_B, U_B, V_B), (vtx_index_A, U_A, V_A), new_tris[cf_nbr][single_vertex])

        ### Section below merges common vertexes.
        NewVertMergeList = []
        NewVertIndex = []
        for i in xrange(vtx_index_start + 1):
            NewVertMergeList += [i]
            NewVertIndex += [i]
        number_of_new_verts = 0
        if not MdlOption("KeepDupeVertexes"):
            ### Section below merges common vertexes.
            for i in xrange(len(VTX_DATA_LIST)):
                DATA_1 = VTX_DATA_LIST[i]
                vtx_index_1, cut_face_1, vtx1_1, vtx2_1, vert_pos_1, U_1, V_1, Xpercent, Ypercent, Zpercent = DATA_1
                MergeThese = 0
                for j in xrange(i):
                    DATA_2 = VTX_DATA_LIST[j]
                    vtx_index_2, cut_face_2, vtx1_2, vtx2_2, vert_pos_2, U_2, V_2, Xpercent, Ypercent, Zpercent = DATA_2

                    vert_pos_diff = (vert_pos_2 - vert_pos_1).tuple
                    if (abs(vert_pos_diff[0]) < 0.001) and (abs(vert_pos_diff[1]) < 0.001) and (abs(vert_pos_diff[2]) < 0.001):
                    
                        # Comment this in if you want to check for U,V too (not needed for QuArK, because we're awesome!)
                        #Udiff = U_2 - U_1
                        #Vdiff = V_2 - V_1
                        #if (Udiff < 0.1) and (V_diff < 0.1):
                        #    #Close enough together (both in position and U,V): merge them!
                        #    MergeThese = 1

                        # Close enough together (in position): merge them!
                        MergeThese = 1

                    if MergeThese:
                        # Merge this vertex (so merge 'i' into 'j').
                        NewVertMergeList += [NewVertMergeList[(vtx_index_start + 1) + j]] ### Chain merging.
                        NewVertIndex += [vtx_index_start + number_of_new_verts]
                        break
                if not MergeThese:
                    # Keep this vertex.
                    number_of_new_verts = number_of_new_verts + 1
                    NewVertMergeList += [(vtx_index_start + 1) + i]
                    NewVertIndex += [vtx_index_start + number_of_new_verts]
        else:
            for i in xrange(len(VTX_DATA_LIST)):
                # No merging.
                NewVertMergeList += [(vtx_index_start + 1) + i]
                NewVertIndex += [(vtx_index_start + 1) + i]

        ### Section below passes final updates to new_tris.
        def UpdateVertex(new_vert):
            vtx_index, U, V = new_vert
            if vtx_index != NewVertMergeList[vtx_index]:
                # This one is needs to be merged, do it!
                DATA_X = VTX_DATA_LIST[NewVertMergeList[vtx_index] - (vtx_index_start + 1)]
                vtx_index_X, cut_face_X, vtx1_X, vtx2_X, vert_pos_X, U_X, V_X, Xpercent, Ypercent, Zpercent = DATA_X
                return (NewVertIndex[vtx_index_X], U, V)
            else:
                # Not merged, just update the vertex index.
                return (NewVertIndex[vtx_index], U, V)

        for key in new_tris_dict.keys():
            new_one = new_tris_dict[key]
            new_tris[key] = (UpdateVertex(new_one[0]), UpdateVertex(new_one[1]), UpdateVertex(new_one[2]))
        for item in new_tris_added:
            new_item = (UpdateVertex(item[0]), UpdateVertex(item[1]), UpdateVertex(item[2]))
            new_tris = new_tris + [new_item]

        ### Applys the new Tris cutting data for the currentcomponent.
        new_comp.triangles = new_tris

        ### Section below applys the new vertex cutting data for all the frames.
        for frame in new_compframes:
            old_vtxs = frame.vertices

            number_of_new_verts = NewVertIndex[vtx_index_start]
            for DATA in VTX_DATA_LIST:
                vtx_index, tri, vtx1, vtx2, vert_pos, U, V, Xpercent, Ypercent, Zpercent = DATA

                if NewVertIndex[vtx_index] == number_of_new_verts:
                    # Same index number as previous vertex, which means this vertex is being merged, skip it!
                    continue
                number_of_new_verts = NewVertIndex[vtx_index]

                vect2 = tri[vtx2][0]
                vect1 = tri[vtx1][0]

                diff = old_vtxs[vect2].tuple[0] - old_vtxs[vect1].tuple[0]
                Xamt = (diff * Xpercent) + old_vtxs[vect1].tuple[0]

                diff = old_vtxs[vect2].tuple[1] - old_vtxs[vect1].tuple[1]
                Yamt = (diff * Ypercent) + old_vtxs[vect1].tuple[1]

                diff = old_vtxs[vect2].tuple[2] - old_vtxs[vect1].tuple[2]
                Zamt = (diff * Zpercent) + old_vtxs[vect1].tuple[2]

                vectA = quarkx.vect(Xamt, Yamt, Zamt)

                old_vtxs = old_vtxs + [vectA]

            frame.vertices = old_vtxs
            frame.compparent = new_comp

        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        editor.Root.currentcomponent = new_comp
        if num_cut_faces == 1:
            editor.ok(undo, str(num_cut_faces) + " face cut")
        else:
            editor.ok(undo, str(num_cut_faces) + " faces cut")
        editor.ModelFaceSelList = editor.ModelFaceSelList + newfaceselection
        make_tristodraw_dict(editor, editor.Root.currentcomponent)
        from mdlhandles import SkinView1
        if SkinView1 is not None:
            q = editor.layout.skinform.linkedobjects[0]
            q["triangles"] = str(len(editor.Root.currentcomponent.triangles))
            editor.layout.skinform.setdata(q, editor.layout.skinform.form)
            SkinView1.invalidate()

    def ok(self, editor, x, y, flags):
        self.autoscroll_stop()
        self.dragto(x, y, flags)
        if self.redimages is not None:
            self.rectanglesel(editor, x, y, self.redimages[0])
        editor.invalidateviews()


# Splits up each selected face in the ModelFaceSelList, that the cut line crosses, into 3 new triangles, something like in the map editor.
def FaceCutToolClick(m):
    editor = mdleditor.mdleditor
    qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_edittools"]
    tb2 = editor.layout.toolbars["tb_objmodes"]
    tb3 = editor.layout.toolbars["tb_AxisLock"]
    if not MdlOption("FaceCutTool") and not MdlOption("AnimationActive") and not MdlOption("AnimationCFGActive"):
        if not MdlOption("AnimationActive") and not MdlOption("AnimationCFGActive") and MdlOption("AnimationPaused"):
            tb1.tb.buttons[7].state = qtoolbar.normal
            quarkx.update(editor.form)
            quarkx.beep()
            quarkx.msgbox("Improper Action !\n\nYou must turn off the\n'Animation Pause' button\nbefore activating the 'Face Cut Tool'.", MT_INFORMATION, MB_OK)
            return
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = "1"
        tb1.tb.buttons[7].state = qtoolbar.selected
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeFaces"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
        tb1.tb.buttons[0].state = qtoolbar.normal
        tb1.tb.buttons[1].state = qtoolbar.normal
        for b in tb2.tb.buttons:
            b.state = qtoolbar.normal
        tb2.tb.buttons[1].state = qtoolbar.selected
        for b in range(len(tb3.tb.buttons)):
            if b == 5:
                tb3.tb.buttons[b].state = qtoolbar.normal
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", 0)
        editor.MouseDragMode = FaceCutter
    else:
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
        tb1.tb.buttons[7].state = qtoolbar.normal
        quarkx.update(editor.form)
        editor.MouseDragMode = mdlhandles.RectSelDragObject


# Option button for FaceCutTool above.
def KeepDupeVertexesClick(m):
    editor = mdleditor.mdleditor
    qtoolbar.toggle(m)
    tb1 = editor.layout.toolbars["tb_edittools"]
    if not MdlOption("KeepDupeVertexes"):
        quarkx.setupsubset(SS_MODEL, "Options")["KeepDupeVertexes"] = "1"
        tb1.tb.buttons[8].state = qtoolbar.selected
        quarkx.update(editor.form)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")["KeepDupeVertexes"] = None
        tb1.tb.buttons[8].state = qtoolbar.normal
        quarkx.update(editor.form)



class EditToolsBar(qeditor.ToolBar):
    "Special model editing tools toolbar."

    Caption = "Editing Tools"
    DefaultPos = ((0,0,0,0), "topdock", 0, 0, 1)

    def buildbuttons(self, layout):
        if not ico_dict.has_key('ico_mdltools'):
            ico_dict['ico_mdltools']=LoadIconSet1("ico_mdltools", 1.0)
        ico_mdltools=ico_dict['ico_mdltools']
        extrude = qtoolbar.button(extrudeclick, "Face mode:\n  Extrude Selected Faces\nVertex mode:\n  Extrude outside edges||Face mode:  Extrude Selected Faces\nVertex mode:  Extrude outside edges:\n\nIn Face mode - this function only works with selected faces in the Editor's views. No 'bulkheads' will be created.\nThe faces can be extruded in any of the editor's views, but the best control is done in one of its '2D' views.\n\nEach time a new drag is made a new set of faces will be created from that starting position to the position at the end of the drag with the new faces selected.\nSwitching from view to view between drags will change the extruded drag direction.\n\nIn Vertex mode - it will perform the same function for all 'outside' edges (do not share two common vertexes) that have been selected.\n\nTwo vertexes of the same triangle must be selected. If an improper vertex selection has been made it will attempt to correct that selection or notify you if it can not.", ico_mdltools, 0, infobaselink="intro.modeleditor.toolpalettes.edittools.html#extrudeselectedfaces")
        extrudebulkheads = qtoolbar.button(extrudebulkheadsclick, "Face mode:\n  Extrude with bulkheads\nVertex mode:\n  Extrude all edges||Face mode:  Extrude with bulkheads\nVertex mode:  Extrude all edges\n\nIn Face mode - this does the same function as the 'Extrude' but leaves 'bulkheads' between each drag.\nThe faces can be extruded in any of the editor's views, but the best control is done in one of its '2D' views.\n\nEach time a new drag is made a new set of faces will be created from that starting position to the position at the end of the drag with the new faces selected.\n\nSwitching from view to view between drags will change the extruded drag direction.\n\nIn Vertex mode - it will perform the same function for all edges that have been selected, including ones that share two common vertexes.\n\nAt least two vertexes of the same triangle must be selected. If an improper vertex selection has been made it will attempt to correct that selection or notify you if it can not.", ico_mdltools, 1, infobaselink="intro.modeleditor.toolpalettes.edittools.html#extrudewithbulkheads")
        revface = qtoolbar.button(ReverseFaceClick, "Reverse face direction||Reverse face direction:\n\nIf faces of a model component have been selected, the direction they face will be reversed by clicking this button.", ico_mdltools, 2, infobaselink="intro.modeleditor.toolpalettes.edittools.html#reversefacedirection")
        subdivide2 = qtoolbar.button(Subdivide2Click, "Subdivide 2||Subdivide 2:\n\nIf faces of a model component have been selected, those faces will be split, at the middle of the longest edge, into 2 new triangles when this button is clicked.", ico_mdltools, 3,  infobaselink="intro.modeleditor.toolpalettes.edittools.html#subdivide2")
        subdivide3 = qtoolbar.button(Subdivide3Click, "Subdivide 3||Subdivide 3:\n\nIf faces of a model component have been selected, those faces will be split, from the center to all 3 points of each selected face, into 3 new triangles when this button is clicked.", ico_mdltools, 4, infobaselink="intro.modeleditor.toolpalettes.edittools.html#subdivide3")
        subdivide4 = qtoolbar.button(Subdivide4Click, "Subdivide 4||Subdivide 4:\n\nIf faces of a model component have been selected, those faces will be split, at one point and the middle of all 3 edges of each selected face, into 4 new triangles when this button is clicked.", ico_mdltools, 5, infobaselink="intro.modeleditor.toolpalettes.edittools.html#subdivide4")
        facecuttool = qtoolbar.button(FaceCutToolClick, "Face Cut tool||Face Cut tool:\n\nWhen this button is active, at least one frame and faces of a model component have been selected, a LMB drag can be made to produce a red cut line, like in the map editor, across them. Where the line crosses it will divide each face into 3 individual triangles.\n\nTo cancel the cutting, press the RMB & LMB together then let go. This can be done at any time.\n\nClick the 'InfoBase' button for details for how to change the cut patterns.", ico_mdltools, 8, infobaselink="intro.modeleditor.toolpalettes.edittools.html#facecuttool")
        keepdupevertexes = qtoolbar.button(KeepDupeVertexesClick, "Keep Dupe Vertexes||Keep Dupe Vertexes:\n\nThis option ONLY works with and applies to the 'Face Cut tool'. The default setting is inactive, causing all duplicate vertexes to be combined when a face is 'CUT' so that the new faces do NOT pull apart.\n\nWhen ACTIVE (on) all common vertexes of the new cut faces CAN be pulled apart for further editing (to extrude, leave open, add new faces to and so on). At any time they can be 'WELDED' together using that function.", ico_mdltools, 9, infobaselink="intro.modeleditor.toolpalettes.edittools.html#facecuttool")

        layout.buttons.update({"Extrude": extrude, "ExtrudeBulkHeads": extrudebulkheads, "RevFace": revface, "Subdivide2": subdivide2, "Subdivide3": subdivide3, "Subdivide4": subdivide4, "FaceCutTool": facecuttool})

        return [extrude, extrudebulkheads, revface, subdivide2, subdivide3, subdivide4, qtoolbar.sep, facecuttool, keepdupevertexes]


#
# Initialize "toolbars" with the standard tool bars. Plug-ins can
# register their own toolbars in the "toolbars" dictionnary.
#

import qmovepal
import mdlanimation
toolbars = {"tb_display": DisplayBar, "tb_edittools": EditToolsBar, "tb_movepal": qmovepal.ToolMoveBar, "tb_animation": mdlanimation.AnimationBar}

# ----------- REVISION HISTORY ------------
#
#
#$Log: mdltoolbars.py,v $
#Revision 1.18  2011/11/17 01:19:02  cdunde
#Setup BBox drag toolbar button to work correctly with other toolbar buttons.
#
#Revision 1.17  2011/03/04 06:50:28  cdunde
#Added new face cutting tool, for selected faces, like in the map editor with option to allow vertex separation.
#
#Revision 1.16  2011/02/12 08:36:37  cdunde
#Fixed auto turn off of Objects Maker not working with other toolbars.
#
#Revision 1.15  2009/07/14 00:27:33  cdunde
#Completely revamped Model Editor vertex Linear draglines system,
#increasing its reaction and drawing time to twenty times faster.
#
#Revision 1.14  2008/08/21 12:11:53  danielpharos
#Fixed an import failure.
#
#Revision 1.13  2008/07/15 23:16:27  cdunde
#To correct typo error from MldOption to MdlOption in all files.
#
#Revision 1.12  2008/02/23 04:41:11  cdunde
#Setup new Paint modes toolbar and complete painting functions to allow
#the painting of skin textures in any Model Editor textured and Skin-view.
#
#Revision 1.11  2007/12/06 02:06:29  cdunde
#Minor corrections.
#
#Revision 1.10  2007/12/05 04:45:57  cdunde
#Added two new function methods to Subdivide selected faces into 3 and 4 new triangles each.
#
#Revision 1.9  2007/12/02 06:47:11  cdunde
#Setup linear center handle selected vertexes edge extrusion function.
#
#Revision 1.8  2007/11/14 05:46:18  cdunde
#To link new "Editing tools" toolbar button to Infobase sections.
#
#Revision 1.7  2007/11/11 11:41:52  cdunde
#Started a new toolbar for the Model Editor to support "Editing Tools".
#
#Revision 1.6  2007/10/18 02:31:54  cdunde
#Setup the Model Editor Animation system, functions and toolbar.
#
#Revision 1.5  2007/08/24 09:27:28  cdunde
#To update the toolbar links to new sections of the InfoBase for the Model Editor.
#
#Revision 1.4  2007/07/28 23:12:52  cdunde
#Added ModelEditorLinHandlesManager class and its related classes to the mdlhandles.py file
#to use for editing movement of model faces, vertexes and bones (in the future).
#
#Revision 1.3  2007/04/22 22:44:47  cdunde
#Renamed the file mdltools.py to mdltoolbars.py to clarify the files use and avoid
#confliction with future mdltools.py file to be created for actual tools for the Editor.
#
#Revision 1.9  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.8  2006/11/29 07:00:28  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.7.2.2  2006/11/04 21:41:44  cdunde
#To add help and Infobase links to buttons.
#
#Revision 1.7.2.1  2006/11/01 22:22:42  danielpharos
#BackUp 1 November 2006
#Mainly reduce OpenGL memory leak
#
#Revision 1.7  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.4  2003/02/15 02:03:45  cdunde
#To update and add F1 popup help info.
#Also add Lockviews button to model editor.
#
#Revision 1.3  2001/10/22 10:26:17  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#