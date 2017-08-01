"""   QuArK  -  Quake Army Knife

Implementation of QuArK Model editor's "Options" menu
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mdloptions.py,v 1.53 2011/05/30 20:46:31 cdunde Exp $


import quarkx
from qdictionnary import Strings
from mdlutils import *
import qmenu
import qbaseeditor
import mdleditor

# Globals
saveEDtrue3Dcamerapos = None
saveEDflat3Dcamerapos = None
saveFLtrue3Dcamerapos = None
saveFLflat3Dcamerapos = None


def newfinishdrawing(editor, view, oldfinish=mdleditor.ModelEditor.finishdrawing):

    oldfinish(editor, view)
    MdlOption = quarkx.setupsubset(SS_MODEL, "Options")
    if not MdlOption["Ticks"]:return


def RotationMenu2click(menu):
    for item in menu.items:
        try:
            setup = apply(quarkx.setupsubset, item.sset)
            item.state = not (not setup[item.tog]) and qmenu.checked
        except:
            try:
                tas = item.tas
                item.state = (quarkx.setupsubset(SS_MODEL, "Options").getint("3DRotation")==tas) and qmenu.radiocheck
            except:
                pass


def Rotate(item):
    quarkx.setupsubset(SS_MODEL, "Options").setint("3DRotation", item.tas)
    editor = mdleditor.mdleditor
    for view in editor.layout.views:
        if view.info["type"] == "2D":
            view.info["scale"] = 2.0
            view.info["angle"] = -0.7
            view.info["vangle"] = 0.3
            view.screencenter = quarkx.vect(0,0,0)
            rotationmode = quarkx.setupsubset(SS_MODEL, "Options").getint("3DRotation")
            holdrotationmode = rotationmode
            rotationmode == 0
            setprojmode(view)
            rotationmode = holdrotationmode
            modelcenter = view.info["center"]
            if rotationmode == 2:
                center = quarkx.vect(0,0,0) + modelcenter ### Sets the center of the MODEL to the center of the view.
            elif rotationmode == 3:
                center = quarkx.vect(0,0,0) + modelcenter ### Sets the center of the MODEL to the center of the view.
            else:
                center = quarkx.vect(0,0,0) ### For the Original QuArK rotation and "Lock to center of 3Dview" methods.
            view.info["scale"] = 2.0
            view.info["angle"] = -0.7
            view.info["vangle"] = 0.3
            view.screencenter = center
            setprojmode(view)


def RotationOption(txt, mode, hint="|Original 3Dview rotation:\n   This is the way QuArK's model rotation has worked in the past.\nClick the InfoBase button below for more detail.\n\nLock to center of 3Dview:\n   This method 'locks' the center of the grid to the center of the 3D view.\nClick the InfoBase button below for more detail.\n\nLock to center of model:\n   This function 'locks' the center of the model to the center of the view.\nClick the InfoBase button below for more detail.\n\nRotate at start position:\n   This function is designed to give far more rotation consistency based on where the cursor is at the time it is clicked to start a rotation at some place on the model.\nClick the InfoBase button below for more detail.|intro.modeleditor.menu.html#optionsmenu"):
    item = qmenu.item(txt, Rotate, hint)
    item.tas = mode
    return item


rotateitems = [
    RotationOption("Original 3Dview rotation", 0),
    RotationOption("Lock to center of 3Dview", 1),
    RotationOption("Lock to center of model", 2),
    RotationOption("Rotate at start position", 3)
    ]
shortcuts = { }


def ToggleOption(item):
    "Toggle an option in the setup."
    import mdlmgr
    mdlmgr.treeviewselchanged = 1
    tag = item.tog
    setup = apply(quarkx.setupsubset, item.sset)
    newvalue = not setup[tag]
    setup[tag] = "1"[:newvalue]
    if item.sendupdate[newvalue]:
        editor = mdleditor.mdleditor
        Update_Editor_Views(editor)


def StartConsoleLogClick(m):
    "Start and stop console logging output to Console.txt file."
    if not MdlOption("ConsoleLog"):
        quarkx.setupsubset(SS_MODEL, "Options")['ConsoleLog'] = "1"
        try:
            quarkx.startconsolelog()
        except:
            pass
        consolelog.state = qmenu.checked
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['ConsoleLog'] = None
        quarkx.stopconsolelog()
        consolelog.state = qmenu.normal


def ClearConsoleLogClick(m):
    "Clears the Console.txt file."
    try:
        quarkx.clearconsolelog()
    except:
        pass


def Config1Click(item):
    "Configuration Dialog Box."
    quarkx.openconfigdlg()


def Plugins1Click(item):
    "Lists the loaded plug-ins."
    import plugins
    group = quarkx.newobj("Loaded Plug-ins:config")
    for p in plugins.LoadedPlugins:
        txt = p.__name__.split(".")[-1]
        ci = quarkx.newobj("%s.toolbar" % txt)
        try:
            info = p.Info
        except:
            info = {}
        for spec, arg in info.items():
            ci[spec] = arg
        ci["File"] = p.__name__
        ci["Form"] = "PluginInfo"
        try:
            ci.shortname = info["plug-in"]
        except:
            pass
        group.appenditem(ci)
    quarkx.openconfigdlg("List of Plug-ins", group)
    

def Options1Click(menu):
    editor = mdleditor.mdleditor
    view = None
    for v in editor.layout.views:
        if v.info['viewname'] == "3Dwindow":
            view = v
            break
    if view is None:
        ft3dmode.state = qmenu.disabled
    elif view.info["type"] == "3D":
        quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] = "1"
        ft3dmode.state = qmenu.checked
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] = None
        ft3dmode.state = qmenu.normal

    et3dmode.state = quarkx.setupsubset(SS_MODEL,"Options").getint("EditorTrue3Dmode")
    maiv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("MAIV")
    recenter.state = quarkx.setupsubset(SS_MODEL,"Options").getint("Recenter")

    for item in menu.items:
        try:
            setup = apply(quarkx.setupsubset, item.sset)
            item.state = not (not setup[item.tog]) and qmenu.checked
        except:
            pass
        if item == lineThicknessItem:
            item.thick = getLineThickness()
            item.text = "Set Line Thickness (%1.0f)"%item.thick


def toggleitem(txt, toggle, sendupdate=(1,1), sset=(SS_MODEL,"Options"), hint=None):
    item = qmenu.item(txt, ToggleOption, hint)
    item.tog = toggle
    item.sset = sset
    item.sendupdate = sendupdate
    return item

class LineThickDlg(SimpleCancelDlgBox):
    #
    # dialog layout
    #
    size = (160, 80)
    dlgflags = FWF_NORESIZE
    dfsep = 0.7 
    
    dlgdef = """
    {
        Style = "9"
        Caption = "Line Thickness Dialog"

        thick: =
        {
        Txt = "Line Thickness:"
        Typ = "EF1"
        Hint = "Needn't be an integer."
        }
        cancel:py = {Txt="" }
    }
    """

    def __init__(self, form, editor, m):
        self.editor = editor
        src = quarkx.newobj(":")
        thick =  quarkx.setupsubset(SS_MODEL,"Options")['linethickness']
        if thick:
            thick=eval(thick)
        else:
            thick=2
        src["thick"] = thick,
        self.src = src
        SimpleCancelDlgBox.__init__(self,form,src)

    def ok(self):
        pass
        thick = self.src['thick']    
        if thick is not None:
            thick, = thick
            if thick==2:
                quarkx.setupsubset(SS_MODEL,"Options")['linethickness']=""
            else:
                quarkx.setupsubset(SS_MODEL,"Options")['linethickness']="%4.2f"%thick
        for view in self.editor.layout.views:
            if view.info["viewname"] == "skinview":
                pass
            else:
                view.invalidate(1)
                mdleditor.setsingleframefillcolor(self.editor, view)
                if view.viewmode != "tex":
                    view.repaint()


def getLineThickness():
     thick =  quarkx.setupsubset(SS_MODEL,"Options")['linethickness']
     if thick:
         return eval(thick)
     else:
         return 2


def setLineThick(m):
    editor = mdleditor.mdleditor
    if editor is None:
        return
    LineThickDlg(quarkx.clickform, editor, m)


lineThicknessItem = qmenu.item("Set Line Thickness (2)",setLineThick,"|Set Line Thickness:\n\nThis lets you set the thickness of certain lines that are drawn on the Editor's views, such as the outlining of selected model mesh faces and the models axis lines.|intro.modeleditor.menu.html#optionsmenu")


def mMBLines_Color(m):
    # Matches bone lines color to the handle color during a drag.
    if not MdlOption("MBLines_Color"):
        quarkx.setupsubset(SS_MODEL, "Options")['MBLines_Color'] = "1"
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['MBLines_Color'] = None

def mBHandles_Only(m):
    # Only allows bone handles to be displayed to increase drawing speed.
    if not MdlOption("BHandles_Only"):
        quarkx.setupsubset(SS_MODEL, "Options")['BHandles_Only'] = "1"
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['BHandles_Only'] = None
    editor = mdleditor.mdleditor
    Update_Editor_Views(editor)

def mB_DragHandles_Only(m):
    # Only allows drawing of bone drag handles to be displayed to increase drawing speed.
    if not MdlOption("Drag_Bones_Only"):
        quarkx.setupsubset(SS_MODEL, "Options")['Drag_Bones_Only'] = "1"
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['Drag_Bones_Only'] = None

def mBMake_All_Draglines(m):
    # Allows all bone handles draglines to be created but will decrease drawing speed & increase model importing time.
    if not MdlOption("BMake_All_Draglines"):
        quarkx.setupsubset(SS_MODEL, "Options")['BMake_All_Draglines'] = "1"
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['BMake_All_Draglines'] = None
    quarkx.reloadsetup()

def mSYNC_ISV(m):
    # Sync editor selection in Skin-view function.
    editor = mdleditor.mdleditor
    from mdlhandles import SkinView1
    if not MdlOption("SYNC_ISV"):
        quarkx.setupsubset(SS_MODEL, "Options")['SYNC_ISV'] = "1"
        editor.SkinVertexSelList = []
        editor.SkinFaceSelList = []
        import mdlhandles
        if MdlOption("PFSTSV"):
            editor.SkinFaceSelList = editor.ModelFaceSelList
            import mdlutils
            mdlutils.PassEditorSel2Skin(editor, 2)
        try:
            skindrawobject = editor.Root.currentcomponent.currentskin
        except:
            skindrawobject = None
        if SkinView1 is not None:
            mdlhandles.buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
            SkinView1.invalidate(1)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['SYNC_ISV'] = None


def mSFSISV(m):
    # Show Face Selection In Skin-View function.
    editor = mdleditor.mdleditor
    if not MdlOption("SFSISV"):
        quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] = None
        editor.SkinFaceSelList = []
    from mdlhandles import SkinView1
    if SkinView1 is not None:
        SkinView1.invalidate(1)


def mPFSTSV(m):
    # Pass Face Selection To Skin-View function.
    editor = mdleditor.mdleditor
    from mdlhandles import SkinView1
    if not MdlOption("PFSTSV"):
        quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = None
        if quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] == "1":
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = "1"
        editor.SkinFaceSelList = editor.ModelFaceSelList
        import mdlutils
        import mdlhandles
        mdlutils.PassEditorSel2Skin(editor, 2)
        try:
            skindrawobject = editor.Root.currentcomponent.currentskin
        except:
            skindrawobject = None
        if SkinView1 is not None:
            mdlhandles.buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None


def mNFDL(m):
    # No face drag lines function.
    editor = mdleditor.mdleditor
    if not MdlOption("NFDL"):
        quarkx.setupsubset(SS_MODEL, "Options")['NFDL'] = "1"
        editor.SelCommonTriangles = []
        editor.SelVertexes = []
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['NFDL'] = None
        comp = editor.Root.currentcomponent
        for tri in editor.ModelFaceSelList:
            for vtx in range(len(comp.triangles[tri])):
                if comp.triangles[tri][vtx][0] in editor.SelVertexes:
                    pass
                else:
                    editor.SelVertexes = editor.SelVertexes + [comp.triangles[tri][vtx][0]] 
                editor.SelCommonTriangles = editor.SelCommonTriangles + findTrianglesAndIndexes(comp, comp.triangles[tri][vtx][0], None)


def mNFO(m):
    # No face outlines function.
    import mdlmgr
    mdlmgr.treeviewselchanged = 1
    if not MdlOption("NFO"):
        quarkx.setupsubset(SS_MODEL, "Options")['NFO'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['NFOWM'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['NFO'] = None
    editor = mdleditor.mdleditor
    Update_Editor_Views(editor)


def mNFOWM(m):
    # No face outlines while moving in 2D views function.
    import mdlmgr
    mdlmgr.treeviewselchanged = 1
    if not MdlOption("NFOWM"):
        quarkx.setupsubset(SS_MODEL, "Options")['NFOWM'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['NFO'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['NFOWM'] = None


def mNOSF(m):
    # No selection fill function.
    import mdlmgr
    mdlmgr.treeviewselchanged = 1
    if not MdlOption("NOSF"):
        quarkx.setupsubset(SS_MODEL, "Options")['NOSF'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['FFONLY'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['BFONLY'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['NOSF'] = None
    editor = mdleditor.mdleditor
    Update_Editor_Views(editor)


def mFFONLY(m):
    # (draw) Front faces only function.
    import mdlmgr
    mdlmgr.treeviewselchanged = 1
    if not MdlOption("FFONLY"):
        quarkx.setupsubset(SS_MODEL, "Options")['FFONLY'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['NOSF'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['BFONLY'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['FFONLY'] = None
    editor = mdleditor.mdleditor
    Update_Editor_Views(editor)


def mBFONLY(m):
    # (draw) Back faces only function.
    import mdlmgr
    mdlmgr.treeviewselchanged = 1
    if not MdlOption("BFONLY"):
        quarkx.setupsubset(SS_MODEL, "Options")['BFONLY'] = "1"
        quarkx.setupsubset(SS_MODEL, "Options")['NOSF'] = None
        quarkx.setupsubset(SS_MODEL, "Options")['FFONLY'] = None
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['BFONLY'] = None
    editor = mdleditor.mdleditor
    Update_Editor_Views(editor)


def BoneMenu():
    Xmblines_color = qmenu.item("&Match Bone Lines Color", mMBLines_Color, "|Match Bone Lines Color:\n\nWhen checked the bone lines color displayed during a drag will match the handle color being dragged.|intro.modeleditor.menu.html#optionsmenu")
    Xmbhandles_only = qmenu.item("&Draw Bone Handles Only", mBHandles_Only, "|Draw Bone Handles Only:\n\nWhen checked only the bone handles are displayed to increase drawing speed during and after a drag.|intro.modeleditor.menu.html#optionsmenu")
    Xmb_draghandles_only = qmenu.item("&Only Draw Drag Bones", mB_DragHandles_Only, "|Only Draw Drag Bones:\n\nWhen checked only all the bone handles being dragged are displayed to increase drawing speed during a drag.|intro.modeleditor.menu.html#optionsmenu")
    Xmball_draglines = qmenu.item("Make &All Draglines", mBMake_All_Draglines, "|Make All Draglines:\n\nWhen checked allows all bone handles draglines to be created but will decrease drawing speed & increase model importing time.\n\nOnly applies at time of model importing and will have no effect once it has. If not used sufficient draglines to see what is being moved and how will still be drawn.|intro.modeleditor.menu.html#optionsmenu")

    menulist = [Xmblines_color, Xmbhandles_only, Xmb_draghandles_only, Xmball_draglines]

    Xmblines_color.state = quarkx.setupsubset(SS_MODEL,"Options").getint("MBLines_Color")
    Xmbhandles_only.state = quarkx.setupsubset(SS_MODEL,"Options").getint("BHandles_Only")
    Xmb_draghandles_only.state = quarkx.setupsubset(SS_MODEL,"Options").getint("Drag_Bones_Only")
    Xmball_draglines.state = quarkx.setupsubset(SS_MODEL,"Options").getint("BMake_All_Draglines")

    return menulist


def FaceMenu():
    Xsync_isv = qmenu.item("&Sync Skin-view with Editor views ", mSYNC_ISV, "|Sync Skin-view with Editor views:\n\nWhen checked this will synchronize the Skin-view with the Editor views for either of the active selection options below.|intro.modeleditor.menu.html#optionsmenu")
    Xsfsisv = qmenu.item("S&how selection in Skin-view", mSFSISV, "|Show selection in Skin-view:\n\nBecause the Skin-view and the rest of the editor views work independently, this will pass selected editor model mesh triangle faces to the 'Skin-view' to be outlined and distinguish them.\n\nHowever, it does not actually select them in the 'Skin-view'.\n\nAny selections or deselections will not show in the 'Skin-view' until the mouse buttons have been released.\n\nThe 'Skin-view' outline color can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.menu.html#optionsmenu")
    Xpfstsv = qmenu.item("&Pass selection to Skin-view", mPFSTSV, "|Pass selection to Skin-view:\n\nThis function will pass selected editor model mesh triangle faces and select the coordinated skin triangles in the 'Skin-view' where they can be used for editing purposes.\n\nOnce the selection has been passed, if this function is turned off, the selection will remain in the 'Skin-view' for its use there.\n\nAny selections or deselections will not show in the 'Skin-view' until the mouse buttons have been released.\n\nThe 'Skin-view' selected face outline color can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.menu.html#optionsmenu")
    Xnfdl = qmenu.item("No face &drag lines", mNFDL, "|No face drag lines:\n\nThis will stop the selection and drawing of all drag lines when model mesh faces have been selected which can increase the selection speed of the editor dramatically when a model with a large number of face triangles is being edited.|intro.modeleditor.menu.html#optionsmenu")
    Xnfo = qmenu.item("&No face outlines", mNFO, "|No face outlines:\n\nThis will stop the outlining of any models mesh faces have been selected. This will increase the drawing speed of the editor dramatically when a model with a large number of face triangles is being edited.\n\nThe solid fill of selected faces will still be available.|intro.modeleditor.menu.html#optionsmenu")
    Xnfowm = qmenu.item("N&o face outlines while moving in 2D views", mNFOWM, "|No face outlines while moving in 2D views:\n\nFace outlining can be very taxing on the editors drawing speed when panning (scrolling) or zooming in the '2D views' when a lot of the models mesh faces have been selected. This is because so many views need to be redrawn repeatedly.\n\nIf you experience this problem check this option to increase the drawing and movement speed. The lines will be redrawn at the end of the move.|intro.modeleditor.menu.html#optionsmenu")
    Xnosf = qmenu.item("No s&election fill", mNOSF, "|No selection fill:\n\nThis stops the color filling and backface pattern from being drawn for any of the models mesh faces that are selected. Only the outline of the selected faces will be drawn.\n\nThis will not apply for any view that has its 'Fill in Mesh' function active (checked) in the 'Views Options' dialog.|intro.modeleditor.menu.html#optionsmenu")
    Xffonly = qmenu.item("&Front faces only", mFFONLY, "|Front faces only:\n\nThis will only allow the solid color filling of the front faces to be drawn for any of the models mesh faces that are selected. The back faces will be outlined allowing the models texture to be displayed if the view is in 'Textured' mode.\n\nThis will not apply for any view that has its 'Fill in Mesh' function active (checked) in the 'Views Options' dialog.|intro.modeleditor.menu.html#optionsmenu")
    Xbfonly = qmenu.item("&Back faces only", mBFONLY, "|Back faces only:\n\nThis will only allow the drawing of the backface pattern to be drawn for any of the models mesh faces that are selected. The front faces will be outlined allowing the models texture to be displayed if the view is in 'Textured' mode.\n\nThis will not apply for any view that has its 'Fill in Mesh' function active (checked) in the 'Views Options' dialog.|intro.modeleditor.menu.html#optionsmenu")

    menulist = [Xsync_isv, Xsfsisv, Xpfstsv, qmenu.sep, Xnfdl, Xnfo, Xnfowm, qmenu.sep, Xnosf, Xffonly, Xbfonly]

    Xsync_isv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SYNC_ISV")
    Xsfsisv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SFSISV")
    Xpfstsv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("PFSTSV")
    Xnfdl.state = quarkx.setupsubset(SS_MODEL,"Options").getint("NFDL")
    Xnfo.state = quarkx.setupsubset(SS_MODEL,"Options").getint("NFO")
    Xnfowm.state = quarkx.setupsubset(SS_MODEL,"Options").getint("NFOWM")
    Xnosf.state = quarkx.setupsubset(SS_MODEL,"Options").getint("NOSF")
    Xffonly.state = quarkx.setupsubset(SS_MODEL,"Options").getint("FFONLY")
    Xbfonly.state = quarkx.setupsubset(SS_MODEL,"Options").getint("BFONLY")

    return menulist


def VertexMenu():
    # Sync Skin-view with Editor views function.
    def mSYNC_SVwED(m):
        editor = mdleditor.mdleditor
        if not MdlOption("SYNC_SVwED"):
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = "1"
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = None
            if quarkx.setupsubset(SS_MODEL,"Options")["PFSTSV"] == "1":
                quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
                quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] = "1"
            import mdlutils
            import mdlhandles
            if editor.ModelVertexSelList != []:
                editor.SkinVertexSelList = []
                from mdlhandles import SkinView1
                if SkinView1 is not None:
                    mdlutils.PassEditorSel2Skin(editor)
                    try:
                        skindrawobject = editor.Root.currentcomponent.currentskin
                    except:
                        skindrawobject = None
                    mdlhandles.buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
            else:
                editor.SkinVertexSelList = []
                from mdlhandles import SkinView1
                if SkinView1 is not None:
                    SkinView1.repaint()
        else:
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = None

    # Pass (Editors Views) Vertex Selection To Skin-view function.
    def mPVSTSV(m):
        editor = mdleditor.mdleditor
        if not MdlOption("PVSTSV"):
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = "1"
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = None
            from mdlhandles import SkinView1
            if SkinView1 is not None:
                import mdlutils
                import mdlhandles
                mdlutils.PassEditorSel2Skin(editor)
                try:
                    skindrawobject = editor.Root.currentcomponent.currentskin
                except:
                    skindrawobject = None
                mdlhandles.buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)
        else:
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = None

    # No muti Vertex Selection drag lines function.
    def mNVDL(m):
        editor = mdleditor.mdleditor
        if not MdlOption("NVDL"):
            quarkx.setupsubset(SS_MODEL, "Options")['NVDL'] = "1"
        else:
            quarkx.setupsubset(SS_MODEL, "Options")['NVDL'] = None

    Xsync_svwed = qmenu.item("&Sync Skin-view with Editor views", mSYNC_SVwED, "|Sync Skin-view with Editor views:\n\nThis function will turn off other related options and synchronize selected Editor views mesh vertexes, passing and selecting the coordinated 'Skin mesh' vertexes in the Skin-view, where they can be used for editing purposes. Any selection changes in the Editor views will be updated to the Skin-view as well.\n\nOnce the selection has been passed, if this function is turned off, the selection will remain in both the Editor and the Skin-view for further use.\n\nThe 'Skin-view' and Editor views selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.menu.html#optionsmenu")
    Xpvstsv = qmenu.item("&Pass selection to Skin-view", mPVSTSV, "|Pass selection to Skin-view:\n\nThis function will pass selected Editor model mesh vertexes and select the coordinated 'Model Skin mesh' vertexes in the Skin-view, along with any others currently selected, where they can be used for editing purposes.\n\nOnce the selection has been passed, if this function is turned off, the selection will remain in the 'Skin-view' for its use there.\n\nThe Editor's selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.menu.html#optionsmenu")
    Xnvdl = qmenu.item("No vertex &drag lines", mNVDL, "|No vertex drag lines:\n\nThis stops the multi selected Editor model mesh vertexes drag lines from being drawn, but not the vertex outlines.\n\nSingle vertex drag lines will also still be drawn.|intro.modeleditor.menu.html#optionsmenu")

    menulist = [Xsync_svwed, Xpvstsv, qmenu.sep, Xnvdl]

    Xsync_svwed.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SYNC_SVwED")
    Xpvstsv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("PVSTSV")
    Xnvdl.state = quarkx.setupsubset(SS_MODEL,"Options").getint("NVDL")

    return menulist


def TicksViewingMenu():
    # Rectangle Drag Ticks_Method 1
    def mRDT_M1(m):
        if not MdlOption("RDT_M1"):
            quarkx.setupsubset(SS_MODEL, "Options")['RDT_M1'] = "1"
            quarkx.setupsubset(SS_MODEL, "Options")['RDT_M2'] = None
        else:
            quarkx.setupsubset(SS_MODEL, "Options")['RDT_M1'] = None

    # Rectangle Drag Ticks_Method 2
    def mRDT_M2(m):
        if not MdlOption("RDT_M2"):
            quarkx.setupsubset(SS_MODEL, "Options")['RDT_M2'] = "1"
            quarkx.setupsubset(SS_MODEL, "Options")['RDT_M1'] = None
        else:
            quarkx.setupsubset(SS_MODEL, "Options")['RDT_M2'] = None
            
    Xrdt_m1 = qmenu.item("Rectangle drag-method 1", mRDT_M1, "|Rectangle drag-method 1:\n\nThis function will draw the Skin-view mesh vertex 'Ticks' during a rectangle drag with a minimum amount of flickering, but is a slower drawing method.|intro.modeleditor.menu.html#optionsmenu")
    Xrdt_m2 = qmenu.item("Rectangle drag-method 2", mRDT_M2, "|Rectangle drag-method 2:\n\nThis function will draw the Skin-view mesh vertex 'Ticks', using the fastest method, during a rectangle drag, but will cause the greatest amount of flickering.|intro.modeleditor.menu.html#optionsmenu")

    menulist = [Xrdt_m1, Xrdt_m2]

    Xrdt_m1.state = quarkx.setupsubset(SS_MODEL,"Options").getint("RDT_M1")
    Xrdt_m2.state = quarkx.setupsubset(SS_MODEL,"Options").getint("RDT_M2")

    return menulist


def SkinViewOptionsMenu():
    # Sync Editor views with Skin-view function.
    def mSYNC_EDwSV(m):
        editor = mdleditor.mdleditor
        if not MdlOption("SYNC_EDwSV"):
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = "1"
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
            import mdlutils
            import mdlhandles
            if editor.SkinVertexSelList != []:
                editor.ModelVertexSelList = []
                mdlutils.PassSkinSel2Editor(editor)
                mdlutils.Update_Editor_Views(editor)
            else:
                editor.ModelVertexSelList = []
                mdlutils.Update_Editor_Views(editor)
        else:
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = None

    # Pass (Skin-view) Vertex Selection To Editors Views function.
    def mPVSTEV(m):
        editor = mdleditor.mdleditor
        if not MdlOption("PVSTEV"):
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = "1"
            quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_EDwSV'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['SYNC_SVwED'] = None
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTSV'] = None
            import mdlutils
            import mdlhandles
            if editor.SkinVertexSelList != []:
                mdlutils.PassSkinSel2Editor(editor)
                mdlutils.Update_Editor_Views(editor, 5)
        else:
            quarkx.setupsubset(SS_MODEL, "Options")['PVSTEV'] = None

    # Clear Selected Faces function.
    def mCSF(m):
        from mdlhandles import SkinView1
        if SkinView1 is not None:
            editor = mdleditor.mdleditor
            if quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] == "1":
                quarkx.setupsubset(SS_MODEL, "Options")['PFSTSV'] = None
            if quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] == "1":
                quarkx.setupsubset(SS_MODEL, "Options")['SFSISV'] = None
            editor.SkinFaceSelList = []
            mdleditor.ModelEditor.finishdrawing(editor, SkinView1)


    Xsync_edwsv = qmenu.item("&Sync Editor views with Skin-view", mSYNC_EDwSV, "|Sync Editor views with Skin-view:\n\nThis function will turn off other related options and synchronize selected Skin-view mesh vertexes, passing and selecting the coordinated 'Model mesh' vertexes in the Editors views, where they can be used for editing purposes. Any selection changes in the Skin-view will be updated to the Editors views as well.\n\nOnce the selection has been passed, if this function is turned off, the selection will remain in both the Editor and the Skin-view for further use.\n\nThe 'Skin-view' and Editor views selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.menu.html#optionsmenu")
    Xpvstev = qmenu.item("&Pass selection to Editor views", mPVSTEV, "|Pass selection to Editor views:\n\nThis function will pass selected Skin-view mesh vertexes and select the coordinated 'Model mesh' vertexes in the Editors views, along with any others currently selected, where they can be used for editing purposes.\n\nOnce the selection has been passed, if this function is turned off, the selection will remain in the Editor for its use there.\n\nThe 'Skin-view' selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.menu.html#optionsmenu")
    Xcsf = qmenu.item("&Clear Selected Faces", mCSF, "|Clear Selected Faces:\n\nThis function will clear all faces in the Skin-view that have been drawn as 'Selected' or 'Show' but any related selected vertexes will remain that way for editing purposes.\n\nThe 'Skin-view' selected face, show face and selected vertex colors can be changed in the 'Configuration Model Colors' section.\n\nPress the 'F1' key again or click the button below for further details.|intro.modeleditor.menu.html#optionsmenu")
    TicksViewing = qmenu.popup("Draw Ticks During Drag", [], TicksViewingClick, "|Draw Ticks During Drag:\n\nThese functions give various methods for drawing the Models Skin Mesh Vertex Ticks while doing a drag.\n\nPress the 'F1' key again or click the button below for further details.", "intro.modeleditor.skinview.html#funcsnmenus")

    menulist = [Xsync_edwsv, Xpvstev, Xcsf, qmenu.sep, TicksViewing]

    Xsync_edwsv.state = quarkx.setupsubset(SS_MODEL,"Options").getint("SYNC_EDwSV")
    Xpvstev.state = quarkx.setupsubset(SS_MODEL,"Options").getint("PVSTEV")

    return menulist


# ****************** Creates the Popup menu ********************
def BoneOptionsClick(m):
    m.items = BoneMenu()

def FaceSelOptionsClick(m):
    m.items = FaceMenu()

def VertexSelOptionsClick(m):
    m.items = VertexMenu()

def TicksViewingClick(m):
    m.items = TicksViewingMenu()

def SkinViewOptionsClick(m):
    m.items = SkinViewOptionsMenu()


# ****************** menu def's for Global items ********************
def EditorTrue3Dmode(m):
    # Changes the Editor's 3D view mode from default Flat3D to True3D and back.
    global saveEDtrue3Dcamerapos, saveEDflat3Dcamerapos
    import qeditor, qhandles, mdlmgr
    editor = mdleditor.mdleditor
    editor.dragobject = None
    view = None
    for v in editor.layout.views:
        if v.info['viewname'] == "editors3Dview":
            view = v
    if view is None:
        return
    if not MdlOption("EditorTrue3Dmode"):
        quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] = "1"
        et3dmode.state = qmenu.checked
        if saveEDflat3Dcamerapos is None and view.info["type"] == "2D":
            saveEDflat3Dcamerapos = [view.info["scale"], view.info["angle"], view.info["vangle"]]
        view.info["type"] = "3D"
        view.scale()
        if saveEDtrue3Dcamerapos is None:
            view.cameraposition = (quarkx.vect(102.59, -102.15, 46.11), 2.358, 0.288)
        else:
           view.cameraposition = saveEDtrue3Dcamerapos
        qeditor.defsetprojmode(view)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] = None
        et3dmode.state = qmenu.normal
        if view.info["type"] == "3D" and view.cameraposition is not None:
            saveEDtrue3Dcamerapos = view.cameraposition
        if saveEDflat3Dcamerapos is None:
            saveEDflat3Dcamerapos = [2.0, -0.7, 0.3]
        else:
            saveEDflat3Dcamerapos = [view.info["scale"], view.info["angle"], view.info["vangle"]]
        qhandles.flat3Dview(view, editor.layout)
        view.info["type"] = "2D"
        view.scale()
        view.info["scale"], view.info["angle"], view.info["vangle"] = saveEDflat3Dcamerapos
        rotationmode = quarkx.setupsubset(SS_MODEL, "Options").getint("3DRotation")
        holdrotationmode = rotationmode
        rotationmode == 0
        qeditor.setprojmode(view)
        rotationmode = holdrotationmode
        modelcenter = view.info["center"]
        if rotationmode == 2:
            center = quarkx.vect(0,0,0) + modelcenter ### Moves the center of the MODEL to the center of the view.
        elif rotationmode == 3:
            center = quarkx.vect(0,0,0) + modelcenter ### Moves the center of the MODEL to the center of the view.
        else:
            center = quarkx.vect(0,0,0) ### For resetting the Original QuArK rotation and "Lock to center of 3Dview" methods.
        view.info["scale"], view.info["angle"], view.info["vangle"] = saveEDflat3Dcamerapos
        view.screencenter = center
        qeditor.setprojmode(view)
    mdlmgr.treeviewselchanged = 0
    import mdlhandles
    for v in editor.layout.views:
        mdlhandles.AddRemoveEyeHandles(editor, v)
        if v.info["viewname"] == "editors3Dview":
            continue
    editor.layout.explorer.invalidate()
    editor.explorerselchange(editor)


def Full3DTrue3Dmode(m):
    # Changes the first Floating 3D view opened mode from default Flat3D to True3D and back.
    global saveFLtrue3Dcamerapos, saveFLflat3Dcamerapos
    import qeditor, qhandles, mdlmgr
    editor = mdleditor.mdleditor
    editor.dragobject = None
    view = None
    for v in editor.layout.views:
        if v.info['viewname'] == "3Dwindow":
            view = v
            break
    if view is None:
        return
    if view.info["type"] == "2D":
        quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] = "1"
        ft3dmode.state = qmenu.checked
        if saveFLflat3Dcamerapos is None and view.info["type"] == "2D":
            saveFLflat3Dcamerapos = [view.info["scale"], view.info["angle"], view.info["vangle"]]
        view.info["type"] = "3D"
        view.scale()
        if saveFLtrue3Dcamerapos is None:
            view.cameraposition = (quarkx.vect(102.59, -102.15, 46.11), 2.358, 0.288)
        else:
           view.cameraposition = saveFLtrue3Dcamerapos
        qeditor.defsetprojmode(view)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] = None
        ft3dmode.state = qmenu.normal
        if view.info["type"] == "3D" and view.cameraposition is not None:
            saveFLtrue3Dcamerapos = view.cameraposition
        if saveFLflat3Dcamerapos is None:
            saveFLflat3Dcamerapos = (2.0, -0.7, 0.3)
        else:
            saveFLflat3Dcamerapos = [view.info["scale"], view.info["angle"], view.info["vangle"]]
        qhandles.flat3Dview(view, editor.layout)
        view.info["type"] = "2D"
        view.scale()
        view.info["scale"], view.info["angle"], view.info["vangle"] = saveFLflat3Dcamerapos
        rotationmode = quarkx.setupsubset(SS_MODEL, "Options").getint("3DRotation")
        holdrotationmode = rotationmode
        rotationmode == 0
        qeditor.setprojmode(view)
        rotationmode = holdrotationmode
        modelcenter = view.info["center"]
        if rotationmode == 2:
            center = quarkx.vect(0,0,0) + modelcenter ### Moves the center of the MODEL to the center of the view.
        elif rotationmode == 3:
            center = quarkx.vect(0,0,0) + modelcenter ### Moves the center of the MODEL to the center of the view.
        else:
            center = quarkx.vect(0,0,0) ### For resetting the Original QuArK rotation and "Lock to center of 3Dview" methods.
        view.info["scale"], view.info["angle"], view.info["vangle"] = saveFLflat3Dcamerapos
        view.screencenter = center
        qeditor.setprojmode(view)
    mdlmgr.treeviewselchanged = 0
    import mdlhandles
    for v in editor.layout.views:
        mdlhandles.AddRemoveEyeHandles(editor, v)
        if v.info["viewname"] == "3Dwindow":
            continue
    editor.layout.explorer.invalidate()
    editor.explorerselchange(editor)


def mMAIV(m):
    "Toggels Model Axis In Views."
    if not MdlOption("MAIV"):
        quarkx.setupsubset(SS_MODEL, "Options")['MAIV'] = "1"
        maiv.state = qmenu.checked
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['MAIV'] = None
        maiv.state = qmenu.normal
    editor = mdleditor.mdleditor
    Update_Editor_Views(editor)


def mRecenter(m):
    "Toggels the Recenter option."
    if not MdlOption("Recenter"):
        quarkx.setupsubset(SS_MODEL, "Options")['Recenter'] = "1"
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['Recenter'] = None
    recenter.state = quarkx.setupsubset(SS_MODEL,"Options").getint("Recenter")

#
# Global variables to update from plug-ins.
#
consolelog = qmenu.item("&Log Console", StartConsoleLogClick, "|Log Console:\n\nWhen active this will write everything that is printed to the console to a text file called 'Console.txt' which is located in QuArK's main folder.|intro.modeleditor.menu.html#optionsmenu")

clearconsolelog = qmenu.item("&Clear Console Log", ClearConsoleLogClick, "|Clear Console Log:\n\nWhen clicked this will clear everything that is printed to the text file called 'Console.txt' which is located in QuArK's main folder.|intro.modeleditor.menu.html#optionsmenu")

dhwr = toggleitem("Draw &handles while rotating", "DHWR", (0,0),
      hint="|Draw handles while rotating:\n\nThis allows the models vertex handles (if active) to be drawn during rotation, but this will slow down the redrawing process and can make rotation seem jerky.|intro.modeleditor.menu.html#optionsmenu")

et3dmode = qmenu.item("&Editor True 3D mode", EditorTrue3Dmode, "|Editor True 3D mode:\n\nThis causes the Model Editor's 3D view to operate the same as the Map Editor when maneuvering and also allows passing through a component.\n\nThis is very useful when working on scenes to see ' into ' the model and work on other components within it.|intro.modeleditor.menu.html#optionsmenu")

ft3dmode = qmenu.item("&Full3D True 3D mode", Full3DTrue3Dmode, "|Full3D True 3D mode:\n\nThis causes the FIRST Full 3D view opened only, to operate the same as the Map Editor when maneuvering and also allows passing through a component.\n\nThis is very useful when working on scenes to see ' into ' the model and work on other components within it.\n\nAll other floating Full 3D views will operate as usual.\nIf the first is closed and the next uses this option the last camera position of the first one will still be in effect.|intro.modeleditor.menu.html#optionsmenu")

maiv = qmenu.item("Model A&xis in views", mMAIV, "|Model Axis in views:\n\nThis displays the models axis on which it was built in all views, showing its X, Y and Z direction.\n\nThe size of its letter indicators and line thickness can be increased or decreased by using the 'Set Line Thickness' function.\n\nTheir individual colors can be changed in the 'Configuration Model Colors' section.|intro.modeleditor.menu.html#optionsmenu")

dbf = toggleitem("Draw &back faces", "DBF", (1,1),
      hint="|Draw back faces:\n\nThis allows the back face checkerboard pattern to be drawn in all view modes when the 'Views Options', 'Mesh in Frames' is checked for that view.\n\nUsing the option in this manner will help to distinguish which direction the faces are facing for proper construction.|intro.modeleditor.menu.html#optionsmenu")

recenter = qmenu.item("&Paste objects at screen center", mRecenter, "|Paste objects at screen center:\n\nCheck this if you want objects that you paste into the editor's views to appear in the center of the current editor's view. Uncheck it, and it will paste it at the exact position as the original.|intro.modeleditor.menu.html#pasteobjectsatscreencenter")

items = [
    recenter,
    ]
shortcuts = { }

ticks = toggleitem("Enlarge Vertices &Ticks", "Ticks", (1,1),
      hint="|Enlarge Vertices Ticks:\n\nThis makes the model's ticks 1 size larger for easer viewing.|intro.modeleditor.menu.html#optionsmenu")

items.append(ticks)

ft3dmode.state = qmenu.disabled

mdleditor.ModelEditor.finishdrawing = newfinishdrawing

AutoFrameRenaming = toggleitem("Auto &Frame Renaming", "AutoFrameRenaming", (0,0), hint="|Auto Frame Renaming:\n\nSome models consist of more then one component. If so, their frame names should always match.\n\nWhen checked, if a frame of one component is renamed, this will cause the same frame of all the other related components to be renamed also automatically.|intro.modeleditor.menu.html#optionsmenu")

def OptionsMenu():
    "The Options menu, with its shortcuts."

    RotationOptions = qmenu.popup("3D Rotation Options", rotateitems, RotationMenu2click)
    BoneOptions = qmenu.popup("Bone Options", [], BoneOptionsClick, "|Bone Options:\n\nThese functions deal with the Model Bone visual tools to work with.", "intro.modeleditor.menu.html#optionsmenu")
    FaceSelOptions = qmenu.popup("Editor Face Selection Options", [], FaceSelOptionsClick, "|Editor Face Selection Options:\n\nThese functions deal with the Model Mesh selection methods available and various visual tools to work with.", "intro.mapeditor.menu.html#optionsmenu")
    VertexSelOptions = qmenu.popup("Editor Vertex Selection Options", [], VertexSelOptionsClick, "|Editor Vertex Selection Options:\n\nThese functions deal with the Model Mesh selection methods available and various visual tools to work with.", "intro.mapeditor.menu.html#optionsmenu")
    SkinViewOptions = qmenu.popup("Skin-view Options", [], SkinViewOptionsClick, "|Skin-view Options:\n\nThese functions deal with various Options pertaining directly to the Skin-view and the way certain elements can be manipulated and displayed while working on the Models Skin Mesh.\n\nPress the 'F1' key again or click the button below for further details.", "intro.modeleditor.skinview.html#funcsnmenus")
    PlugIns = qmenu.item("List of Plug-ins...", Plugins1Click)
    Config1 = qmenu.item("Confi&guration...", Config1Click,  hint = "|Configuration...:\n\nThis leads to the Configuration-Window where all elements of QuArK are setup. From the way the Editor looks and operates to Specific Game Configuration and Mapping or Modeling variables.\n\nBy pressing the F1 key one more time, or clicking the 'InfoBase' button below, you will be taken directly to the Infobase section that covers all of these areas, which can greatly assist you in setting up QuArK for a particular game you wish to map or model for.|intro.configuration.html")
    Options1 = qmenu.popup("&Options", [RotationOptions, dhwr, et3dmode, ft3dmode, qmenu.sep]+[maiv, dbf, lineThicknessItem, qmenu.sep, BoneOptions, FaceSelOptions, VertexSelOptions, SkinViewOptions, AutoFrameRenaming, qmenu.sep]+items+[qmenu.sep, PlugIns, Config1, qmenu.sep, consolelog, clearconsolelog], Options1Click)
    return Options1, shortcuts


def OptionsMenuRMB():
    "The Options RMB menu items."

    BoneOptions = qmenu.popup("Bone Options", BoneMenu(), None, "|Bone Options:\n\nThese functions deal with the Model Bone visual tools to work with.", "intro.modeleditor.menu.html#optionsmenu")
    FaceSelOptions = qmenu.popup("Editor Face Options", FaceMenu(), None, "|Editor Face Selection Options:\n\nThese functions deal with the Model Mesh selection methods available and various visual tools to work with.", "intro.mapeditor.menu.html#optionsmenu")
    VertexSelOptions = qmenu.popup("Editor Vertex Options", VertexMenu(), None, "|Editor Vertex Selection Options:\n\nThese functions deal with the Model Mesh selection methods available and various visual tools to work with.", "intro.mapeditor.menu.html#optionsmenu")
    return [BoneOptions, FaceSelOptions, VertexSelOptions]


# ----------- REVISION HISTORY ------------
#
#
#$Log: mdloptions.py,v $
#Revision 1.53  2011/05/30 20:46:31  cdunde
#Added frame name change to complete updatings and AutoFrameRenaming function.
#
#Revision 1.52  2011/03/27 06:30:56  cdunde
#Icon updates.
#
#Revision 1.51  2010/06/06 08:56:13  cdunde
#Fix to draw fillcolors correctly when true 3D is turned on or off.
#
#Revision 1.50  2010/06/02 21:23:38  cdunde
#Fixes for Model Editor Eye position handle.
#
#Revision 1.49  2010/05/29 04:34:45  cdunde
#Update for Model Editor camera EYE handles for editor and floating 3D view.
#
#Revision 1.48  2010/05/06 03:10:54  cdunde
#Menu functions update to eliminate dupe and unnecessary redraws.
#
#Revision 1.47  2009/11/10 04:41:34  cdunde
#Added option to only draw drag bones to speed up drag drawing if a lot of bones exist.
#
#Revision 1.46  2009/06/16 11:34:08  cdunde
#Small dialog setting update.
#
#Revision 1.45  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.44  2009/01/30 20:38:46  cdunde
#Added option for creation of all bone handle draglines when importing.
#
#Revision 1.43  2009/01/27 05:02:59  cdunde
#Full support for .md5mesh bone importing with weight assignment and other improvements.
#
#Revision 1.42  2008/12/05 07:44:06  cdunde
#Small update.
#
#Revision 1.41  2008/12/04 21:15:11  cdunde
#Minor update to work with the function properly.
#
#Revision 1.40  2008/12/03 08:24:05  cdunde
#Added functions for console logging and clearing of that log to the options menu.
#
#Revision 1.39  2008/10/23 04:42:24  cdunde
#Infobase links and updates for Bones.
#
#Revision 1.38  2008/10/04 05:48:06  cdunde
#Updates for Model Editor Bones system.
#
#Revision 1.37  2008/09/15 04:47:45  cdunde
#Model Editor bones code update.
#
#Revision 1.36  2008/07/22 23:14:23  cdunde
#Fixed menu items that were not interacting with their config settings in the Defaults.qrk file.
#
#Revision 1.35  2008/07/21 02:31:06  cdunde
#Added 3D view modes to Options menu to allow viewing through objects for scenes.
#
#Revision 1.34  2008/07/15 23:16:26  cdunde
#To correct typo error from MldOption to MdlOption in all files.
#
#Revision 1.33  2008/05/27 19:36:16  danielpharos
#Fixed another bunch of wrong imports
#
#Revision 1.32  2008/05/01 19:15:22  danielpharos
#Fix treeviewselchanged not updating.
#
#Revision 1.31  2008/05/01 13:52:31  danielpharos
#Removed a whole bunch of redundant imports and other small fixes.
#
#Revision 1.30  2008/02/22 09:52:24  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.29  2007/11/04 00:33:33  cdunde
#To make all of the Linear Handle drag lines draw faster and some selection color changes.
#
#Revision 1.28  2007/10/06 05:24:56  cdunde
#To add needed comments and finish setting up rectangle selection to work fully
#with passing selected faces in the editors view to the Skin-view.
#
#Revision 1.27  2007/10/06 03:23:13  cdunde
#Updated Sync Skin-view with Editor function for the Model Editor.
#
#Revision 1.26  2007/09/07 23:55:29  cdunde
#1) Created a new function on the Commands menu and RMB editor & tree-view menus to create a new
#     model component from selected Model Mesh faces and remove them from their current component.
#2) Fixed error of "Pass face selection to Skin-view" if a face selection is made in the editor
#     before the Skin-view is opened at least once in that session.
#3) Fixed redrawing of handles in areas that hints show once they are gone.
#
#Revision 1.25  2007/09/05 18:53:11  cdunde
#Changed "Pass Face Selection to Skin-view" to real time updating and
#added function to Sync Face Selection in the Editor to the Skin-view.
#
#Revision 1.24  2007/08/21 11:08:38  cdunde
#Added Model Editor Skin-view 'Ticks' drawing methods, during drags, to its Options menu.
#
#Revision 1.23  2007/08/20 19:58:23  cdunde
#Added Linear Handle to the Model Editor's Skin-view page
#and setup color selection and drag options for it and other fixes.
#
#Revision 1.22  2007/08/11 02:37:36  cdunde
#To stop crossover of face and vertex selections in
#the editor and Skin-view causing error to occur.
#
#Revision 1.21  2007/07/14 22:42:43  cdunde
#Setup new options to synchronize the Model Editors view and Skin-view vertex selections.
#Can run either way with single pick selection or rectangle drag selection in all views.
#
#Revision 1.20  2007/07/09 18:59:23  cdunde
#Setup RMB menu sub-menu "skin-view Options" and added its "Pass selection to Editor views"
#function. Also added Skin-view Options to editors main Options menu.
#
#Revision 1.19  2007/07/02 22:49:42  cdunde
#To change the old mdleditor "picked" list name to "ModelVertexSelList"
#and "skinviewpicked" to "SkinVertexSelList" to make them more specific.
#Also start of function to pass vertex selection from the Skin-view to the Editor.
#
#Revision 1.18  2007/07/01 04:56:52  cdunde
#Setup red rectangle selection support in the Model Editor for face and vertex
#selection methods and completed vertex selection for all the editors 2D views.
#Added new global in mdlhandles.py "SkinView1" to get the Skin-view,
#which is not in the editors views.
#
#Revision 1.17  2007/06/20 22:04:08  cdunde
#Implemented SkinFaceSelList for Skin-view for selection passing functions from the model editors views
#and start of face selection capabilities in the Skin-view for future functions there.
#
#Revision 1.16  2007/06/19 06:16:04  cdunde
#Added a model axis indicator with direction letters for X, Y and Z with color selection ability.
#Added model mesh face selection using RMB and LMB together along with various options
#for selected face outlining, color selections and face color filltris but this will not fill the triangles
#correctly until needed corrections are made to either the QkComponent.pas or the PyMath.pas
#file (for the TCoordinates.Polyline95f procedure).
#Also setup passing selected faces from the editors views to the Skin-view on Options menu.
#
#Revision 1.15  2007/05/18 03:11:37  cdunde
#Fixed newfinishdrawing code call to qbaseeditor.py finishdrawing function.
#
#Revision 1.14  2007/03/04 19:40:04  cdunde
#Added option to draw or not draw handles in the Model Editor 3D views
#while rotating the model to increase drawing speed.
#
#Revision 1.13  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.12  2006/11/29 07:00:26  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.11.2.6  2006/11/28 00:55:35  cdunde
#Started a new Model Editor Infobase section and their direct function links from the Model Editor.
#
#Revision 1.11.2.5  2006/11/27 19:24:04  cdunde
#To change the model centering in the view when rotation option is selected.
#
#Revision 1.11.2.4  2006/11/27 08:31:56  cdunde
#To add the "Rotate at start position" method to the Model Editors rotation options menu.
#
#Revision 1.11.2.3  2006/11/26 06:42:54  cdunde
#Added RMB menu item for all Model Editor 3D views to reset the model location,
#based on its current rotation method, in case it goes out of the view and lost.
#
#Revision 1.11.2.2  2006/11/25 23:37:52  cdunde
#To improve 3D view reset, if model lost from view, by clicking on rotation setting option.
#
#Revision 1.11.2.1  2006/11/25 04:23:57  cdunde
#Added a new sub-menu to the Model Editors "Options" menu,
#with various methods of rotation in 3D views to choose from.
#
#Revision 1.11  2006/05/01 05:34:32  cdunde
#To link Configuration menu item directly to its Infobase section.
#
#Revision 1.10  2006/03/11 17:25:59  cdunde
#Changed to invalidate views and add Infobase link.
#
#Revision 1.9  2006/03/07 08:08:28  cdunde
#To enlarge model Tick Marks hard to see 1 pixel size
#and added item to Options menu to make 1 size bigger.
#
#Revision 1.8  2006/03/06 19:21:23  cdunde
#To add hint in Infobase linking to toggle
#Model Editor Optional menu items.
#
#Revision 1.7  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.4  2005/08/31 05:36:32  cdunde
#To add hint argument for toggleitem function.
#
#Revision 1.3  2003/12/17 13:58:59  peter-b
#- Rewrote defines for setting Python version
#- Removed back-compatibility with Python 1.5
#- Removed reliance on external string library from Python scripts
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#
