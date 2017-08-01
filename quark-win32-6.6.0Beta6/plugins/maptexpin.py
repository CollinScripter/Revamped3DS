########################################################
#
#               Alternate Texture Position Plugin
#
#
#                  by tiglari@hexenworld.met
#     
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & possible improvements to
#   tiglari@hexenworld.net
#  
#
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/maptexpin.py,v 1.8 2008/02/22 09:52:21 danielpharos Exp $


Info = {
   "plug-in":       "Texture Pinning Plugin",
   "desc":          "Texture positioning by `pinning'",
   "date":          "Nov 18, 2000",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.net",
   "quark":         "Version 6.x" }

import quarkx
import quarkpy.dlgclasses
import tagging
from quarkpy.maputils import *

#
#  - These utilities should go to qutils or some such place,
#    when this is prepared for stable release
#

#
# A utility for accessing attributes of objects
#  (class instances) that might not be defined
#
def getAttr(object, attr, default=None):
    if hasattr(object, attr):
        return getattr(object,attr)
    else:
        return default
#
# ditto for deleting attributes
#
def delAttr(object, attr):
    if hasattr(object, attr):
         delattr(object, attr)

def appendToAttr(object, attr, thing):
    if hasattr(object, attr):
        getattr(object,attr).append(thing)
    else:
        setattr(object,attr,[thing])

def removeFromAttr(object, attr, thing):
    getattr(object,attr).remove(thing)
    if getattr(object,attr)==[]:
        delattr(object,attr)



    
#
# Pinning dialog
#
#  ppdb's (quarkpy.dlgclasses) are set up like ordinary ones
#   except for an additional initialization parameter 'label'
#   that is used as a key for storing size/position info.
#
class VtxPinDlg(quarkpy.dlgclasses.placepersistent_dialogbox):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (140,140)
    dfsep = 0.30

    dlgdef = """
    {
        Style = "9"
        Caption = "Vertex Pinning"
        
        st:= { Txt = "st" Typ = "EF02"
               Hint = "Tex coordinates for this vertex, W, H." }
        
        pin:= { Txt = "pin:" Typ = "ER"
                   Hint = "# vertex being pinned (read-only)" }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
        cancel:py = {Txt="" }
    }"""

    def __init__(self,form,editor,label,msg,pos,face,facepins, repin):
       self.editor = editor
       self.src = quarkx.newobj(":")
       texp = face.threepoints(2)

       self.src["pin"] = msg
       
       self.oldtex=texCoords(pos, texp, 128)
       self.src["st"] = self.oldtex
       self.facepins = facepins
       self.pos = pos
       self.face = face
       self.repin = repin

       quarkpy.dlgclasses.placepersistent_dialogbox.__init__(self, form, self.src, label,
          cancel = quarkpy.qtoolbar.button(
            self.cancel,
            "Cancel dialog",
            ico_editor, 0,
            "Cancel"),
          exit = quarkpy.qtoolbar.button(
            self.exit,
            "Exit & apply changes",
            ico_editor, 2,
            "Exit & Apply")
        )

    def exit(self, dlg):
        quarkx.globalaccept()
        st = self.src["st"]
        st = st[0]/128, st[1]/128
        editor=self.editor
        pos = self.pos
        pinned = getAttr(editor,'pinned')
        facepins = self.facepins
        if pinned is None:
             pinned = editor.pinned = [(pos, st)]
        else:
             if self.repin:  # repin kludge
                 for pin in editor.pinned[:]: # don't remove from orig.
                     if not pin[0]-pos:
                         editor.pinned.remove(pin)
                         # could stop, but why not clearemall out?
             editor.pinned.append((pos,st))
             facepins.append((pos,st))
        numpins = len(facepins)
        if numpins == 3:
            face = self.face
            texp = solveForThreepoints(facepins[0], facepins[1], facepins[2])
            newface = face.copy()
            newface.setthreepoints(texp, 2)
            undo = quarkx.action()
            undo.exchange(face, newface)
            editor.ok(undo, "move texture")
        editor.invalidateviews()
        qmacro.dialogbox.close(self, dlg)


    def cancel(self, dlg):
          qmacro.dialogbox.close(self, dlg)


    
#
# New menu for vertexes
#
def vertexmenu(self, editor, view, oldmenu=quarkpy.maphandles.VertexHandle.menu.im_func):

    #
    # enable/disable info
    #
    pinned = getAttr(editor,'pinned')
    face = editor.layout.explorer.uniquesel
    if face is not None:
        if face.type!=":f":
            face = None
    facepins = []
    repin = 0
    if face is not None and pinned is not None:
        #
        # The idea here is that we only pay attention to
        # pins on the selected face; we can't set more
        # than three per face, but we can reset existing
        # ones.  Ugh messy.
        #
        def onface(pin, face=face, pos = self.pos):
            for cycle in face.vertices:
                for vertex in cycle:
                    if not (pin[0]-vertex):
                        return 1
            return 0
        facepins = filter(onface, pinned)
        #
        # The treatment of `repinning' seems awkward; it's removed
        #   from facepins, and replaced in editor.pinned if the
        #   dialog is executed.  Is there a cleaner way to do this?
        #
        for pin in facepins[:]:  # don't remove from original for loop
            if not pin[0]-self.pos:
                repin=1
                facepins.remove(pin)

    def pinClick(m, self=self, editor=editor, facepins=facepins, face=face,repin=repin):
        if len(facepins)==0:
            msg = "first"
        elif len(facepins)==1:
            msg = "second"
        elif len(facepins)==2:
            msg = "third"
        else:
            quarkx.msgbox('3 pins, clear some',MT_ERROR,MB_OK)
            return

        VtxPinDlg(quarkx.clickform, editor, 'vtxpin', msg, self.pos, face, facepins, repin)

    def clearPinClick(m, pos=self.pos, editor=editor, facepins=facepins):
        for pin in facepins[:]:
            if not (pos-pin[0]):
               facepins.remove(pin)
        for pin in editor.pinned[:]:
            if not pos-pin[0]:
                editor.pinned.remove(pin)
          
        editor.invalidateviews()
                
    def clearAllClick(m, editor=editor):
        delattr(editor,'pinned')
        editor.invalidateviews()
    
    if face is not None:
        stString = " (%.1f, %.1f)"%texCoords(self.pos, face.threepoints(2), 128) 
    else:
        stString = ""
    pinItem = qmenu.item('&Pin Vertex '+stString,pinClick,"|`pin' the texture on the face at the vertex. A face must be selected.\n\nAfter three pins have been set, the texture is repositioned so that the texture coordinates for the pinned points are as specified.")
    stItem = qmenu.item(stString, None,"No action")
    clearPin = qmenu.item('Clear Pin', clearPinClick)
    clearPins = qmenu.item('Clear All Pins', clearAllClick)
    
    clearPin.state= qmenu.disabled
    if pinned is None:
        clearPins.state = qmenu.disabled
    if (face is None) or (face.type != ':f'):
        pinItem.state = qmenu.disabled
        pinItem.hint = "|"+pinItem.hint + "\n\nThis menu item is disabled because it requires a face be selected"
    if repin:
        pinItem.text = 'Re&pin Vertex'
        clearPin.state = qmenu.normal
        
    #
    #  Promote/Demote of submenu seems like a good idea to
    #   apply to other submenus.
    #
    promote = quarkx.setupsubset(SS_MAP, "Options")["Pinners"]

    def promoteClick(m):
        quarkx.setupsubset(SS_MAP, "Options")["Pinners"]="1"
         
    def demoteClick(m):
        quarkx.setupsubset(SS_MAP, "Options")["Pinners"]="0"

    if promote=="1":
        promoteItem = qmenu.item('Demote Pinning',demoteClick, "|Pinning menu items get demoted to submenu")
    else:
        promoteItem = qmenu.item('Promote Pinning',promoteClick, "|Pinning menu items get promoted onto main vertex menu")

    pinList = [pinItem, clearPin, clearPins, promoteItem]
    
    if promote=="1":
        pinners = pinList
    else:
        pinners = [qmenu.popup('Texture Pinning', pinList)]


    return  pinners+oldmenu(self,editor,view)
    
quarkpy.maphandles.VertexHandle.menu = vertexmenu


#
# Now for drawing little boxes around pinned vertices
#
from tagging import drawredface # misnamed, oh well

def pinfinishdrawing(editor, view, oldmore=quarkpy.mapeditor.MapEditor.finishdrawing):
      cv = view.canvas()
      try:
         pins = editor.pinned
      except (AttributeError):
         pass
      else:
         cv.pencolor = MapColor("Duplicator")
         for pin in pins:
             p1 = view.proj(pin[0])
             tagging.drawsquare(cv,p1,8)
      try:
         moving = editor.movingvertex
         p1 = view.proj(moving)
      except (AttributeError):
         pass
      else:
         if view.info["type"] == "3D":
              scalefactor = 50
         else:
             scalefactor = 30
         scale = view.scale(moving)
         for (color, axis) in (MapColor("Tag"), (1,0,0)), (MapColor("Bezier"), (0,1,0)),(MapColor("Duplicator"), (0,0,1)):
             cv.pencolor = color
             p0 = view.proj(moving)
             p1 = view.proj(moving+(scalefactor/scale)*quarkx.vect(axis))
             cv.line(p0, p1)
                 
#         else:
#             cv.pencolor = MapColor("Bezier")
#             tagging.drawsquare(cv,p1,8)
              

      cv.pencolor=MapColor("Duplicator")
      try:
          for face in editor.frozenFaces:
              drawredface(view,cv,face)
      except (AttributeError):
          pass
      
      oldmore(editor, view)

quarkpy.mapeditor.MapEditor.finishdrawing = pinfinishdrawing

# ----------- REVISION HISTORY ------------
#$Log: maptexpin.py,v $
#Revision 1.8  2008/02/22 09:52:21  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.7  2005/11/10 18:03:04  cdunde
#Activate history log
#
#