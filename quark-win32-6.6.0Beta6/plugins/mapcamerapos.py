# QuArK  -  Quake Army Knife
#
# Copyright (C) 2001 The Quark Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/mapcamerapos.py,v 1.19 2011/03/13 20:30:56 cdunde Exp $
 
Info = {
   "plug-in":       "Camera Position Duplicator",
   "desc":          "storeable camera positions",
   "date":          "13 June 2001",
   "author":        "tiglari",
   "author e-mail": "tiglari@planetquake.com",
   "quark":         "Quark 6.3" }

#
#  Lots of design suggestions by quantum_red.
#

import quarkx
#
# The style of import statement here makes it unnecessary to
#  put 'quarkpy' into references to things in these modules.
#  This would make it easier to shift this material directly
#  into say the 'maphandles' module
#
from quarkpy import mapentities
from quarkpy import mapduplicator
from quarkpy import qhandles
from quarkpy import qutils
from quarkpy import mapsearch
from quarkpy import dlgclasses
from quarkpy import qmacro
from quarkpy import mapselection
from quarkpy import mapmenus

import mapmadsel

#
# and because of this, things from maphhandles can be used
#  w/o qualification
#
from quarkpy.maphandles import *


#
# Tries to find the last 3D view clicked on
#
def get3DView(editor,makeone=0):
    #
    # A bit of showoff coding, see the onlne Python tutorial,
    #   functional programming techiques
    #
    views = filter(lambda v:v.info["type"]=="3D",editor.layout.views)
    if len(views)==0:
        if makeone:
            editor.layout.full3Dclick(None)
            views = filter(lambda v:v.info["type"]=="3D",editor.layout.views)
            return views[0]
        else:
            quarkx.msgbox("Open a 3D view",2,4)
            return
    elif len(views)==1:
        return views[0]
    for view in views:
        #
        # put it in an exception-catching block for in case
        #   editor doesn't have a last3DView
        #
        try:
            if view is editor.last3DView:
                return view
        except (AttributeError):
            pass
    #
    # If intelligent selection fails, take the first.
    #
    return views[0]

#
# We're going to trigger these actions both by menu
#  items and buttons in a dialog, so we define them
#  independently of the UI elements that call them.
#
def setView(o,editor):
    view = get3DView(editor,makeone=1)
    if view is None:
        return
    view.cameraposition = o.origin, o["yaw"][0], o["pitch"][0]
    editor.invalidateviews()
    editor.currentcampos=o

def storeView(o,editor):
    view = get3DView(editor)
    if view is None:
        return
    pos, yaw, pitch = view.cameraposition
    undo = quarkx.action()
    undo.setspec(o,"origin",str(pos))
    #
    # note setting values as 1-element tuples (Python docco)
    #
    undo.setspec(o,"yaw",(yaw,))
    undo.setspec(o,"pitch",(pitch,))
    editor.ok(undo,"store camera position")
    editor.currentcampos=o

#
# The menu redefinition trick, as discussed in the plugin tutorial
#  in the infobase.  'o' is the duplicator object
#
def camposmenu(o, editor, oldmenu=mapentities.DuplicatorType.menu.im_func):
    "camera position entity menu"

    menu = oldmenu(o, editor)
    if o["macro"] !="cameraposition":
        return menu

    def setViewClick(m,o=o,editor=editor):
        setView(o,editor)

    def storeViewClick(m,o=o,editor=editor):
        storeView(o,editor)

    storeitem=qmenu.item("Store View",storeViewClick,"|Store 3D view position in this position item.")
    getitem=qmenu.item("Set View", setViewClick,"|Set 3D view position from this position item.\n\nThen use PgUp/Down with 'C' depressed to cycle prev/next camera positions in the same group as this one.\n\nThis won't work until a view has been set or stored in the group with the menu item")
    return [getitem, storeitem]

mapentities.DuplicatorType.menu = camposmenu

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
class CamPosDuplicator(mapduplicator.StandardDuplicator):

    def handles(self, editor, view):
        org = self.dup.origin
        if org is None:
            org = quarkx.vect(self.dup["origin"])
        hndl = CamPosHandle(org, self.dup)
        return [hndl]

mapduplicator.DupCodes.update({
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
    dfsep = 0.45
    dlgdef = """
      {
        Style = "9"
        Caption = "Enter name"
        sep: = {Typ="S" Txt=" "}    // some space
        name: = {
          Txt=" Enter the name :"
          Typ="E"
        }
        local: = {Typ="X" Hint="Put camera in currently selected group, if possible" $0D " (sister to selected non-group)"}
        sep: = {Typ="S" Txt=" "}    // some space
        sep: = {Typ="S" Txt=""}    // a separator line
        cancel:py = {Txt="" }
      }
    """

    def __init__(self, form, action, initialvalue=None):
        src = quarkx.newobj(":")
        if initialvalue is not None:
           src["name"]=initialvalue
        self.initialvalue=initialvalue
        self.action=action
        SimpleCancelDlgBox.__init__(self, form, src)

    #
    # This is executed when the data changes, close when a new
    #   name is provided
    #
    def datachange(self, df):
        if self.src["name"]!=self.initialvalue:
            self.close()
 

    #
    # This is executed when the OK button is pressed
    #   FIXME: 'local' code doesn't work right, dialog
    #   would need some redesign
    #
    def ok(self):
        name = self.src["name"]
        if name is None:
            name="Camera Position"
        self.name=name
        self.local = self.src["local"]
        self.action(self)

#
# This is called by two interface items, so pulled
#  out of both of them
#
def addPosition(view3D, editor):
        #
        # Dialogs run 'asynchronously', which means
        #  that the after the creation of the dialog just
        #  runs without waiting for a value to be entered
        #  into the dialog.  So if you don't want something
        #  to happen until then, you need to code it in a
        #  function that gets passed to the dialog as
        #  a parameter, which is what this is.
        #
        def action(self, view3D=view3D,editor=editor):
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
            pozzies=None
            if self.src["local"]:
                sel = editor.layout.explorer.uniquesel
                if sel is not None:
                    if sel.type==":g":
                        pozzies = sel
                    else:
                       pozzies=sel.treeparent # returns None if parent outside of tree
            if pozzies is None:
                pozzies = editor.Root.findname("Camera Positions:g")
            undo=quarkx.action()
            if pozzies is None:
                pozzies = quarkx.newobj("Camera Positions:g")
                undo.put(editor.Root,pozzies)
            undo.put(pozzies, camdup)
            undo.setspec(camdup,"origin",str(pos))
            undo.setspec(camdup,"yaw",(yaw,))
            undo.setspec(camdup,"pitch",(pitch,))
            editor.ok(undo,'add camera position')
        #
        # Now execute the dialog
        #
        NameDialog(quarkx.clickform,action,"Camera Position")



#
# And more menu redefinition, this time for the
#  EyePositionMap handle defined in maphandles.py.
#
def newEyePosMenu(self, editor, view):
    
    def addClick(m,self=self,editor=editor):
        addPosition(self.view3D,editor)
        
    item = qmenu.item('Add position',addClick)
    return [item]

EyePositionMap.menu = newEyePosMenu

def backmenu(editor, view=None, origin=None, oldbackmenu = mapmenus.BackgroundMenu):
  menu = oldbackmenu(editor, view, origin)

  def addClick(m,view=view,editor=editor):
      addPosition(view,editor)
      
  if view is not None and view.info["type"]=="3D":
      menu.append(qmenu.item("Add Camera Position",addClick, "|Add Camera Position:\n\nWhen selected, this function is used to set and store 3D camera views. This feature will only work for the Editor's 3D view and not the 3D view window.\n\nPress F1 again or click the 'InfoBase' for more detailed information on its use.|intro.mapeditor.floating3dview.html#camera"))
  return menu

mapmenus.BackgroundMenu = backmenu



#
# A Live Edit dialog.  Closely modelled on the Microbrush
#  H/K dialog, so look at that for enlightenment
#
class FindCameraPosDlg(dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (220,160)
    dfsep = 0.35
    dlgflags = qutils.FWF_KEEPFOCUS 
    
    dlgdef = """
        {
        Style = "9"
        Caption = "Camera position finder"

        cameras: = {
          Typ = "C"
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
        index = eval(self.chosen)
        #
        # FIXME: dumb hack, revise mapmadsel
        #
        m = qmenu.item("",None)
        m.object=self.pack.cameras[index]
        mapmadsel.SelectMe(m)

    def setview(self):
        index = eval(self.chosen)
        editor=mapeditor()
        if editor is None:
            quarkx.msgbox('oops no editor',2,4)
        setView(self.pack.cameras[index],editor)
                
    def storeview(self):
        index = eval(self.chosen)
        editor=mapeditor()
        if editor is None:
            quarkx.msgbox('oops no editor',2,4)
        storeView(self.pack.cameras[index],editor)


#
# Define the zapview macro here, put the definition into
#  quarkpy.qmacro, which is where macros called from delphi
#  live.
#
def macro_camerapos(self, index=0):
    editor = mapeditor()
    if editor is None: return
    if index==1:
        editor.cameraposdlg.select()
    elif index==2:
        editor.cameraposdlg.setview()
    elif index==3:
        editor.cameraposdlg.storeview()

qmacro.MACRO_camerapos = macro_camerapos

def findClick(m):
    editor=mapeditor()

    class pack:
        "stick stuff in this"
    
    def setup(self, pack=pack, editor=editor):
        editor.cameraposdlg=self
        self.pack=pack
        cameras = filter(lambda d:d["macro"]=="cameraposition",editor.Root.findallsubitems("",":d"))
        pack.cameras = cameras
        pack.slist = map(lambda obj:obj.shortname, cameras)
        pack.klist = map(lambda d:`d`, range(len(cameras)))
        #
        #  wtf doesn't this work, item loads but function is trashed
        #
#        self.src["cameras"] = pack.klist[0]
        self.src["cameras$Items"] = "\015".join(pack.slist)
        self.src["cameras$Values"] = "\015".join(pack.klist)
        self.src["num"]=len(pack.klist),

    def action(self, pack=pack, editor=editor):
       src = self.src
       #
       # note what's been chosen
       #
       self.chosen = src["cameras"]

    FindCameraPosDlg(quarkx.clickform, 'findcamerapos', editor, setup, action)

mapsearch.items.append(qmenu.item('Find Camera Positions', findClick, "|Find Camera Positions:\n\nThis finds all the camera positions.|intro.mapeditor.menu.html#searchmenu"))


#
# Prev/Next hotkey subversion
#
def camnextClick(m, editor=None, oldnext=mapselection.nextClick):
    if quarkx.keydown('C')==1:
        editor=mapeditor()
        if editor is None:
           quarkx.msgbox('oops no editor',2,4)
           return
        try:
            current=editor.currentcampos
        except (AttributeError):
            quarkx.msgbox("You need to set or store a view first for this to work",2,4)
            return
        successor = m.succ(current) # succ=prev or next, depending on key
        #
        # Skip over any non-camera stuff
        #
        while successor is not current and successor["macro"]!="cameraposition":
            successor=m.succ(successor)
        setView(successor,editor)
    else:
        oldnext(m,editor)

mapselection.nextItem.onclick=camnextClick
mapselection.prevItem.onclick=camnextClick



# $Log: mapcamerapos.py,v $
# Revision 1.19  2011/03/13 20:30:56  cdunde
# Merged code line to avoid Python problems.
#
# Revision 1.18  2011/03/11 07:53:01  cdunde
# Fixed dialog box height.
#
# Revision 1.17  2008/02/07 13:24:49  danielpharos
# Fix a typo and remove redundant spaces
#
# Revision 1.16  2006/11/30 01:17:47  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.15  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.14.2.6  2006/11/01 22:22:43  danielpharos
# BackUp 1 November 2006
# Mainly reduce OpenGL memory leak
#
# Revision 1.14  2006/05/19 17:07:53  cdunde
# To add links to docs on RMB menus and background image function.
#
# Revision 1.13  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.10  2003/12/18 21:51:46  peter-b
# Removed reliance on external string library from Python scripts (second try ;-)
#
# Revision 1.9  2003/03/21 05:47:45  cdunde
# Update infobase and add links
#
# Revision 1.8  2002/05/21 21:30:21  tiglari
# no-selection tree-view RMB bug fixed (ut_fourdays)
#
# Revision 1.7  2001/06/17 21:10:57  tiglari
# fix button captions
#
# Revision 1.6  2001/06/17 04:46:11  tiglari
# local camera positioning, and auto 3d view opening where appropriate
#
# Revision 1.5  2001/06/16 21:55:46  tiglari
# dialog npw stays open when something else is selected,add position
# on map background menu
#
# Revision 1.4  2001/06/16 03:19:05  tiglari
# add Txt="" to separators that need it
#
# Revision 1.3  2001/06/16 02:44:09  tiglari
# Camera Position finder dialog, cycle-in group with PgUp/Down+'C'
#
# Revision 1.2  2001/06/14 12:16:47  tiglari
# nameing dialog, multiple view support (pick last clicked on)
#
# Revision 1.1  2001/06/13 22:28:09  tiglari
# kickoff
#
#