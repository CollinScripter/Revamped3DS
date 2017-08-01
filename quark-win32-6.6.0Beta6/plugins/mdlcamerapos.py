# QuArK  -  Quake Army Knife
#
# Copyright (C) 2001 The Quark Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/mdlcamerapos.py,v 1.5 2011/03/28 00:47:22 cdunde Exp $
 
Info = {
   "plug-in":       "Camera Position Duplicator",
   "desc":          "storeable camera positions",
   "date":          "March 10 2011",
   "author":        "cdunde",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

#
#  Lots of design suggestions by quantum_red.
#

import quarkx
#
# The style of import statement here makes it unnecessary to
#  put 'quarkpy' into references to things in these modules.
#  This would make it easier to shift this material directly
#  into say the 'mdlhandles' module
#
from quarkpy import mdlentities
from quarkpy import mdlduplicator
from quarkpy import qhandles
from quarkpy import qutils
from quarkpy import dlgclasses
from quarkpy import qmacro
from quarkpy import mdlmenus
from quarkpy.mdlhandles import *


def giveMessage(o, view):
    if o.parent.name.startswith("Editor"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1" and o.parent.name.startswith("Editor Std 3D"):
            quarkx.msgbox("You must uncheck the Options menu item\nEditor True 3D mode\nto use this camera view.",2,4)
            return
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] != "1" and o.parent.name.startswith("Editor True 3D"):
            quarkx.msgbox("You must check the Options menu item\nEditor True 3D mode\nto use this camera view.",2,4)
            return
    else:
        if view is None:
            if o.parent.name.startswith("Full3D True 3D"):
                quarkx.msgbox("You must open a 'Full 3D view'\nand check the Options menu item\nFull3D True 3D mode\nto use this camera view.",2,4)
                return
            else:
                quarkx.msgbox("You must open a 'Full 3D view'\nand uncheck the Options menu item\nFull3D True 3D mode\nif checked, to use this camera view.",2,4)
                return
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1" and o.parent.name.startswith("Full3D Standard"):
            quarkx.msgbox("You must uncheck the Options menu item\nFull3D True 3D mode\nto use this camera view.",2,4)
            return
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] != "1" and o.parent.name.startswith("Full3D True 3D"):
            quarkx.msgbox("You must check the Options menu item\nFull3D True 3D mode\nto use this camera view.",2,4)
            return

#
# Tries to find the correct 3D view for the 'o' (object) cameraposition duplicator.
#
def get3DView(o, editor):
    got3DView = action = None
    if o.parent.name.startswith("Editor"):
        for view in editor.layout.views:
            if view.info['viewname'] == "editors3Dview":
                got3DView = view
                break
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1" and o.parent.name.startswith("Editor Std 3D"):
            return got3DView, 1
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] != "1" and o.parent.name.startswith("Editor True 3D"):
            return got3DView, 1
    else:
        for view in editor.layout.views:
            if view.info['viewname'] == "3Dwindow":
                got3DView = view
                break
        if got3DView is None:
            if o.parent.name.startswith("Full3D True 3D"):
                return got3DView, 1
            else:
                return got3DView, 1
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1" and o.parent.name.startswith("Full3D Standard"):
            return got3DView, 1
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] != "1" and o.parent.name.startswith("Full3D True 3D"):
            return got3DView, 1
    return got3DView, action

#
# We're going to trigger these actions both by menu
#  items and buttons in a dialog, so we define them
#  independently of the UI elements that call them.
#
def setView(o, editor):
    import quarkpy.qbaseeditor
    from quarkpy.qbaseeditor import currentview
    view, action = get3DView(o, editor)
    if view is None or action is not None:
        giveMessage(o, view)
        return
    quarkpy.qbaseeditor.currentview = view
    try: # For True 3D modes.
        view.cameraposition = o.origin, o["yaw"][0], o["pitch"][0]
        editor.currentcampos=o
    except: # For Standard 3D modes.
        import quarkpy.qeditor
        view.info["scale"] = o["scale"][0]
        view.info["angle"] = o["angle"][0]
        view.info["center"] = quarkx.vect(o["center"])
        view.info["vangle"] = o["vangle"][0]
        view.info["sfx"] = o["sfx"][0]
        quarkpy.qeditor.setprojmode(view)
        view.scrollto(o["hscrollbar"][0], o["vscrollbar"][0])
        view.update() # Needs to be here to stop early and dupe drawing of vertexes if suppose to.

def storeView(o, editor):
    view, action = get3DView(o, editor)
    if view is None or action is not None:
        giveMessage(o, view)
        return
    undo = quarkx.action()
    # For True 3D view shots.
    if (view.info['viewname'] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1") or (view.info['viewname'] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1"):
        pos, yaw, pitch = view.cameraposition
        undo.setspec(o,"origin",str(pos))
        undo.setspec(o,"yaw",(yaw,))
        undo.setspec(o,"pitch",(pitch,))
    else: # For standard 3D view shots.
        info = view.info
        import quarkpy.qeditor
        matrix = quarkpy.qeditor.defsetprojmode(view)
        undo.setspec(o,"matrix",str(matrix,))
        undo.setspec(o,"screencenter",str(view.screencenter))
        undo.setspec(o,"scale",(info['scale'],))
        undo.setspec(o,"angle",(info['angle'],))
        undo.setspec(o,"center",str(info['center'],))
        undo.setspec(o,"vangle",(info['vangle'],))
        undo.setspec(o,"sfx",(info['sfx'],))
        undo.setspec(o,"hscrollbar",(view.scrollbars[0]))
        undo.setspec(o,"vscrollbar",(view.scrollbars[1]))
    editor.ok(undo,"stored camera position")
    editor.currentcampos = o

#
# The menu redefinition trick, as discussed in the plugin tutorial
#  in the infobase.  'o' is the duplicator object
#
def camposmenu(o, editor, oldmenu=mdlentities.DuplicatorType.menu.im_func):
    "camera position entity menu"

    menu = oldmenu(o, editor)
    if o["macro"] !="cameraposition":
        return menu

    def setViewClick(m,o=o,editor=editor):
        setView(o,editor)

    def storeViewClick(m,o=o,editor=editor):
        storeView(o,editor)

    getitem=qmenu.item("Set View", setViewClick,"|Set 3D view position from this position item.")
    storeitem=qmenu.item("Store View",storeViewClick,"|Store 3D view position in this position item.")
    return [getitem, storeitem]

mdlentities.DuplicatorType.menu = camposmenu

#
# Icons in the treeview represent map objects directly,
#   while icons in the map views represent their handles.
#   the code here uses the object's menu as the handle's.
#
class CamPosHandle(qhandles.IconHandle):

    def __init__(self, origin, centerof):
        qhandles.IconHandle.__init__(self, origin, centerof)

    def menu(self, editor, view):
        return camposmenu(self.centerof, editor)

#
# The creation of an extremely simple duplicator ...
# Define a class and register it by updating the DupCodes.
#
class CamPosDuplicator(mdlduplicator.StandardDuplicator):

    def handles(self, editor, view):
        org = self.dup.origin
        if org is None:
            try: # For True 3D modes.
                org = quarkx.vect(self.dup["origin"])
            except: # For Standard 3D modes.
                if view is None:
                    view, action = get3DView(self.dup, editor)
                if view is None:
                    return
                org = quarkx.vect(self.dup["screencenter"])
                org = org - ((~(quarkx.matrix(self.dup["matrix"])) * quarkx.vect(0.0, 0.0, 500.0))) #Step the camera back
        hndl = CamPosHandle(org, self.dup)
        return [hndl]

mdlduplicator.DupCodes.update({
  "cameraposition":  CamPosDuplicator,
})

#
# See the dialog box section in the advanced customization
#  section of the infobase.  SimpleCancelDlgBox is
#  defined in quarkpy.qeditor.
#
class NameDialog(SimpleCancelDlgBox):
    "A simple dialog box to enter a name."

    endcolor = AQUA
    size = (330,140)
    dfsep = 0.35
    dlgdef = """
      {
        Style = "9"
        Caption = "Enter name"
        sep: = {Typ="S" Txt=" "}    // some space
        name: = {
          Txt=" Enter the name :"
          Typ="E"
        }
        accept: = {Typ = "P" Txt = " " Macro = "accept" Cap = "Accept above name" Hint = "Push to accept given name"$0D"or enter your own name but"$0D"it can not match any other names."}
        sep: = {Typ="S" Txt=" "}    // some space
        sep: = {Typ="S" Txt=""}    // a separator line
        cancel:py = {Txt="" }
      }
    """

    def __init__(self, form, action, initialvalue=None):
        src = quarkx.newobj(":")
        if initialvalue is not None:
           src["name"] = initialvalue
        self.initialvalue = initialvalue
        self.action = action
        SimpleCancelDlgBox.__init__(self, form, src)

    # This is executed when the data changes, close when a new name is provided.
    def datachange(self, df):
        if self.src["name"] != self.initialvalue:
            self.close()

    def ok(self):
        name = self.src["name"]
        if name is None:
            import quarkpy.qbaseeditor
            from quarkpy.qbaseeditor import currentview
            if currentview.info['viewname'] == "editors3Dview":
                type = "Editor"
            else:
                type = "Full3D"
            name = type + " True 3D Camera Position"
        self.name = name
        self.action(self)

def macro_accept(btn):
    import quarkpy.qmacro
    quarkpy.qmacro.closedialogbox("NameDialog")

import quarkpy.qmacro
quarkpy.qmacro.MACRO_accept = macro_accept

# This is called by two interface items, so pulled out of both of them.
def addPosition(view3D, editor, viewhandle):
        #
        # Dialogs run 'asynchronously', which means
        #  that after the creation of the dialog it just
        #  runs without waiting for a value to be entered
        #  into the dialog.  So if you don't want something
        #  to happen until then, you need to code it in a
        #  function that gets passed to the dialog as
        #  a parameter, which is what this is.
        #
        undo=quarkx.action()
        def action(self, view3D=view3D, editor=editor, viewhandle=viewhandle, undo=undo):
            if viewhandle.hint.find("Editor") != -1:
                type = "Editor"
            else:
                type = "Full3D"
            #
            # NB: elsewhere in the code, 'yaw' tends to
            # be misnamed as 'roll'
            #
            #  pitch = up/down angle (relative to x axis)
            #  yaw = left/right angle (relative to x axis)
            #  roll = turn around long axis (relative to y)
            #
            pos, yaw, pitch = view3D.cameraposition
            camdup = quarkx.newobj(self.name+":d")
            camdup["macro"] = "cameraposition"
            undo.put(pozzies, camdup)
            undo.setspec(camdup,"origin",str(pos))
            undo.setspec(camdup,"yaw",(yaw,))
            undo.setspec(camdup,"pitch",(pitch,))
            editor.ok(undo,'add camera position')

        # Now create the proper suggestive name and execute the dialog.
        if viewhandle.hint.find("Editor") != -1:
            type = "Editor"
        else:
            type = "Full3D"
        pozzies = None
        if pozzies is None:
            pozzies = editor.Root.findname(type + " True 3D Camera Positions:g")
        if pozzies is None:
            pozzies = quarkx.newobj(type + " True 3D Camera Positions:g")
            undo.put(editor.Root,pozzies, editor.Root.subitems[0])
        name = type + " True 3D Camera Position" + str(len(pozzies.subitems)+1)
        NameDialog(quarkx.clickform, action, name)

# And more menu redefinition, this time for the EyePosition handle defined in qhandles.py.
def newEyePosMenu(self, editor, view):
    
    def addClick(m, self=self, editor=editor):
        addPosition(self.view3D, editor, self)
        
    item = qmenu.item('Add position', addClick)
    return [item]

qhandles.EyePosition.menu = newEyePosMenu


# A Live Edit dialog.  Closely modelled on the Microbrush
#  H/K dialog, so look at that for enlightenment.
class FindCameraPosDlg(dlgclasses.LiveEditDlg):
    editor = mapeditor()
    endcolor = AQUA
    size = (330,160)
    dfsep = 0.35
    dlgflags = qutils.FWF_KEEPFOCUS 
    
    dlgdef = """
        {
        Style = "9"
        Caption = "Camera position finder"

        cameras: = {
          Typ = "CL"
          Txt = "Positions:"
          Items = "%s"
          Values = "%s"
          Hint = "These are the camera positions.  Pick one," $0D " then push buttons on row below for action."
        }

        sep: = { Typ="S" Txt=""}

        buttons: = {
        Typ = "PM"
        Num = "3"
        Macro = "camerapos"
        Caps = "TVS"
        Txt = "Actions:"
        Hint1 = "Select the chosen one in the treeview"
        Hint2 = "Set the view to the chosen one"
        Hint3 = "Store the view in the chosen one"
        }

        num: = {
          Typ = "EF1"
          Txt = "# found"
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

    def select(self):
        try:
            index = eval(self.chosen)
            m = qmenu.item("",None)
            m.object = self.pack.cameras[index]
            self.editor.layout.explorer.sellist = [m.object]
            self.editor.layout.explorer.expand(m.object.parent)
        except:
            quarkx.msgbox("You need to set or store a view first for this to work",2,4)
            return

    def setview(self):
        editor = self.editor
        if editor is None:
            quarkx.msgbox('oops no editor',2,4)
        try:
            index = eval(self.chosen)
            setView(self.pack.cameras[index],editor)
        except:
            quarkx.msgbox("You need to set or store a view first for this to work",2,4)
            return
                
    def storeview(self):
        editor = self.editor
        if editor is None:
            quarkx.msgbox('oops no editor',2,4)
        try:
            index = eval(self.chosen)
            storeView(self.pack.cameras[index],editor)
        except:
            quarkx.msgbox("You need to set or store a view first for this to work",2,4)
            return

# Define the zapview macro here, put the definition into
#  quarkpy.qmacro, which is where macros called from delphi live.
def macro_camerapos(self, index=0):
    editor = mapeditor()
    if editor is None: return
    if index == 1:
        editor.cameraposdlg.select()
    elif index == 2:
        editor.cameraposdlg.setview()
    elif index == 3:
        editor.cameraposdlg.storeview()

qmacro.MACRO_camerapos = macro_camerapos

def findClick(m):
    editor=mapeditor()

    class pack:
        "stick stuff in this"
    
    def setup(self, pack=pack, editor=editor):
        editor.cameraposdlg = self
        self.pack = pack
        cameras = []
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] != "1" and editor.Root.dictitems.has_key("Editor Std 3D Camera Positions:g"):
            cameras = cameras + filter(lambda d:d["macro"] == "cameraposition",editor.Root.dictitems["Editor Std 3D Camera Positions:g"].findallsubitems("", ':d'))
        elif quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1" and editor.Root.dictitems.has_key("Editor True 3D Camera Positions:g"):
            cameras = cameras + filter(lambda d:d["macro"] == "cameraposition",editor.Root.dictitems["Editor True 3D Camera Positions:g"].findallsubitems("", ':d'))
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] != "1" and editor.Root.dictitems.has_key("Full3D Standard Camera Positions:g"):
            cameras = cameras + filter(lambda d:d["macro"] == "cameraposition",editor.Root.dictitems["Full3D Standard Camera Positions:g"].findallsubitems("", ':d'))
        elif quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1" and editor.Root.dictitems.has_key("Full3D True 3D Camera Positions:g"):
            cameras = cameras + filter(lambda d:d["macro"] == "cameraposition",editor.Root.dictitems["Full3D True 3D Camera Positions:g"].findallsubitems("", ':d'))
        pack.cameras = cameras
        pack.slist = map(lambda obj:obj.shortname, cameras)
        pack.klist = map(lambda d:`d`, range(len(cameras)))

        if self.src["cameras"] is None:
            self.chosen = self.src["cameras"] = "0"
        self.src["cameras$Items"] = "\015".join(pack.slist)
        if self.src["cameras$Items"] is None:
            self.src["cameras$Items"] = " "
        self.src["cameras$Values"] = "\015".join(pack.klist)
        if self.src["cameras$Values"] is None:
            self.src["cameras$Values"] = " "
        self.src["num"] = len(pack.klist),

    def action(self, pack=pack, editor=editor):
        src = self.src
        # note what's been chosen
        self.chosen = src["cameras"]

    FindCameraPosDlg(quarkx.clickform, 'mdlfindcamerapos', editor, setup, action)


# $Log: mdlcamerapos.py,v $
# Revision 1.5  2011/03/28 00:47:22  cdunde
# To remove unwanted hint text.
#
# Revision 1.4  2011/03/27 03:10:12  cdunde
# Removed unnecessary code.
#
# Revision 1.3  2011/03/26 23:35:16  cdunde
# Updated Model Editor Camera Position system with Hotkeys to take quick shots of both Editor and Floating 3D views,
# kept in separate folders for both Standard modes and True3D modes with Hotkeys to scroll through those shots.
#
# Revision 1.2  2011/03/16 05:43:31  cdunde
# Added F5 Hotkey function for making Model Editor 3D camera positions.
#
# Revision 1.1  2011/03/15 08:25:46  cdunde
# Added cameraview saving duplicators and search systems, like in the Map Editor, to the Model Editor.
#
#