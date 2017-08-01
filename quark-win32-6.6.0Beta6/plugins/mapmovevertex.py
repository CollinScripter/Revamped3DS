"""   QuArK  -  Quake Army Knife

Vertex moveing plugin
"""

#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

# $Header: /cvsroot/quark/runtime/plugins/mapmovevertex.py,v 1.11 2008/02/22 09:52:21 danielpharos Exp $

Info = {
   "plug-in":       "Vertex Movement Dialog",
   "desc":          "dialg for moving vertexes",
   "date":          "22 Sep 2000",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.net",
   "quark":         "Version 6.x" }


#
# The import statements make material in other files available
#  to the statements in this file
#

#
# Quarkx is the delphi-defined API
#
import quarkx

#
# This imports the maphandles.py file in the quarkpy folder
#  To use something from this file you need to `quality' its
#  name with quarkpy.maphandles, e.g. `quarkpy.maphandles.VertexHandle`
# 
import quarkpy.maphandles

#
# for face menu options
#
import quarkpy.mapoptions

#
# This imports the tagging.py plugin in this folder
#
import tagging

#
# This imports every function in quarkpy\maputils
#  things imported in this way don't need to be (& in fact
#  can't be) qualified
#
from quarkpy.maputils import *

#
# For the stuff below about moving some object containing a vertex
#
from quarkpy import guiutils

#
# repeated from maputils to make it work with older quark versions.
#

def projectpointtoplane(p,n1,o2,n2):
  "project point to plane at o2 with normal n2 along normal n1"
  v1 = o2-p
  v2 = v1*n2
  v3 = n1*n2
  v4 = v2/v3
  v5 = v4*n1
  return p + v5

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
# This is a definition of the vertex-movement dialog
# The `live edit dialog' is a rather fancy critter defined
#  in quarkpy/dlgclasses.  Don't worry about its innards,
#  but you'll see how it's used further below.
#
# Read http://..adv.quarkpy.gui.html#dialogs in the infobase
#  for details on how this stuff defines the appearance of
#  dialog and the data-entry forms in it.
#
#  `EU` is the form with a field that you can enter a numerical
#   value, and up-down buttons for increment/decrement
#
#  Somebody has really gotta gettaroundto documenting all the
#   different Typ's...
#

class VtxDragDlg(quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (140,120)
    dfsep = 0.50

    dlgdef = """
        {
            Style = "9"
        Caption = "Vertex Movement"

        X: = 
        {
        Txt = "X"
        Typ = "EU"
        Hint = "X position"
        }

        Y: = 
        {
        Txt = "Y"
        Typ = "EU"
        Hint = "Y position"
        }

        Z: = 
        {
        Txt = "Z"
        Typ = "EU"
        Hint = "Z position"
        }

        sep: = { Typ="S" Txt=" " }

        gridpos: =
        {
        Txt = "Grid Position"
        Typ="X"
        Hint="If this is checked, vertexes will move to grid positions"
        }
        
        griddel: =
        {
        Txt = "Grid Delta"
        Typ="X"
        Hint="If this is checked, vertexes will move by grid increments" $0D " (overridden by Grid Position)"
        }

        sloppy: =
        {
        Txt = "Sloppy"
        Typ="X"
        Hint="If this is checked, vertexes move in the plane of a locked face, but not necessarily to where you specify"
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

#
# Main math function.  Might shift into maputils.
#
def rotateFace(face, mvtx, delta, pivot, pivot2):
    "rotates face from mvtx by delta around pivots"
#    debug('delta: '+`delta`)
    #
    # Much more laborious than Tim Smith's maphandles
    #  method, but seems to prevent `drifting' of supposedly
    #  locked vertices from their locked positions
    #
    # The idea if first to use the pivots and
    #  the new position as threepoints, then fix up
    #  the texture by rotating the texture threepoints,
    #  (code 3), and projecting them onto the new face.
    #
    # Probably a more streamlined approach will work, but
    #  the drifting problem is a pain.
    #
    rotationAxis = (pivot2-pivot).normalized
    norm1 = (rotationAxis^(mvtx-pivot)).normalized
    plane1 = rotationAxis^norm1
    norm2 = (rotationAxis^(mvtx+delta-pivot)).normalized
    plane2 = rotationAxis^norm2
    points = face.threepoints(3)
    facenorm = face.normal
    def proj(v, org=pivot, ax1=rotationAxis, ax2=plane1):
        return (v-org)*ax1, (v-org)*ax2
    #
    # map applies proj to each member in the tuple `points',
    #  producing the new tuple `pcoords'
    #
    pcoords = map(proj, points)
    face.setthreepoints((pivot2, pivot, mvtx+delta),0)
    if facenorm*face.normal<0:
        face.swapsides()
    newpoints = face.threepoints(0)
    def proj2plane(p,pp=newpoints[1],nn=face.normal):
        return projectpointtoplane(p,nn,pp,nn)
    def unproj((x, y),org=pivot,ax1=rotationAxis, ax2=plane2):
        return org+x*ax1+y*ax2
    #
    # Well I could have piled up three maps, and not
    #  used the pcoords variable, but I didn't!
    #
    newpoints = tuple(map(proj2plane, (map(unproj, pcoords))))
    face.setthreepoints(newpoints,3)
    

#
# Here's the function that does the real work of moving the faces.
# It's a good idea to separate out the functions & classes that
#  perform significant work on the data being manipulated from
#  those that are basically oriented towards the UI
#
def moveFaces(faces, mvtx, delta, poly, locklist, freezelist, sloppy=None):
    "returns the moving old, new faces, of poly , with mvtx moved by delta"
    result = []
    old = []
    for face in faces:
        if face in freezelist:
            continue
        newface = face.copy()
        norm = face.normal
        facelocked = []
        #
        # regular index method doesn't work for lists of vectors
        #
        vtxes = face.verticesof(poly)
        vtxindex = 0
        for vtx in vtxes:
            if not(vtx-mvtx):
                moveindex = vtxindex   
            for vtxh in locklist:
                #
                # Testing for closeness rather than full-precision
                #  superposition seems to be necessary to keep the
                #  locked vertices from coming adrift.  There's
                #  no theory behind the choice of value; it just
                #  seems to work.
                #
                if (vtxh.poly is poly and abs(vtxh.pos-vtx)<.1):
                    facelocked.append(vtxh.pos)
                    #
                    # we only use this if only one vertex is locked
                    #
                    lockindex=vtxindex
                vtxindex=vtxindex+1
        if len(facelocked) == 0:
            proj = delta*norm
            newface.translate(proj*norm)
#            debug('translated '+newface.shortname)    
        if len(facelocked) == 1:
            #
            # this autolock stuff isn't working right so its
            #  dialog checkbox is commented out to disableit
            #
            if 0:
#            if autolock:
                cyclelength = len(vtxes)
                if cyclelength/abs(moveindex-lockindex)!=2:
                    #
                    # I think a mathematician could do this better
                    #
                    halfcycle = cyclelength/2.0
                    if moveindex<lockindex:
                        if lockindex-moveindex<halfcycle:
                            secondlockindex=lockindex+1
                        else:
                            secondlockindex=lockindex-1
                    elif lockindex<moveindex:
                        if moveindex-lockindex<halfcycle:
                            secondlockindex=lockindex-1
                        else:
                            secondlockindex=lockindex+1
                    #
                    # the remainder operation is the go for cyclic
                    #  indexing situations.
                    #
                    facelocked.append(vtxes[secondlockindex%cyclelength])
        if len(facelocked)==1:        
                #
                # rotate around perp to line from mftx to pivot
                #
                pivot=facelocked[0]
                perp = newface.normal^(mvtx-pivot)
                rotateFace(newface, mvtx, delta, pivot, pivot+perp)
        if len(facelocked) == 2:
            rotateFace(newface, mvtx, delta, facelocked[0], facelocked[1])
#            debug('2-rotated '+newface.shortname)
        if len(facelocked) > 2:
            if sloppy:
                continue
            norm = face.normal
            #
            # Bail unless the new vertex position is on the
            #  fully locked plane.
            #
            if norm*(mvtx+delta-facelocked[0]):
                return None, None
        old.append(face)
        result.append(newface)
    return old, result

#
# Now we get going on the interface.
#

#
# First define a new menu (see the plugins tutorial for the
#  general method)
#
def vertexmenu(self, editor, view, oldmenu=quarkpy.maphandles.VertexHandle.menu.im_func):

    #
    # This is a very convenient approach to defining the `callback'
    #  functions that are called when a menu-item is clicked; the
    #  default-argument specifications make it easy to pass all
    #  sorts of info to the functions (e.g. self in the function
    #  is equated to self in the environment).
    # Won't work for callbacks that want to also be called from
    #  the command menu or a toolbar button (like some of the ones
    #  in maptagside)
    #
    def moveclick(n, self=self, editor=editor):
         pos = self.pos
         poly = self.poly
         faces = poly.faces
         #
         # find out what faces are going to move
         #
         moving = []
         for face in faces:
             for vtx in face.verticesof(poly):
                 #
                 # Remember = doesn't work right for vectors;
                 #  this is how you test for two vectors being
                 #  equal
                 #
                 if not (vtx-pos):
                    moving.append(face)
                    continue
    
         #
         # Now start setting up the live edit dialog; this is
         #  a black magic process that you just follow
         #
         
         #
         #  The objects that the dialog is going to manipulate
         #   are stuffed into a `pack' object
         #
         class pack:
             "a place to stick stuff"
         pack.poly = poly
         pack.moving = moving
         pack.pos = pos
 
         #
         # Now define a setup function with `self' as its first
         #  argument, and any number of further default arguments
         #  specified to in stuff from above. 
         #
         # `self' refers the dialog, it's .src is the object
         #  from which the displayed values in the dialog are
         #  taken
         #
         def setup(self, pack=pack, editor=editor):
             src = self.src
             options = quarkx.setupsubset(SS_MAP, "Options")
             src["gridpos"]=options["movevertex_gridpos"]
             src["griddel"]=options["movevertex_griddel"]
             src["sloppy"]=options["movevertex_sloppy"]
             pos = pack.pos
             #
             # Tell the editor the position of the moving vertex,
             #   so that a green box can be drawn around it
             #
             editor.movingvertex = pos
             editor.invalidateviews()
             #
             # this code loads the x, y and z coordinates,
             #  represented as strings, into the X, Y and Z
             #  specifics of src, and hence ultimately into
             #  the corresponding controls of the dialog
             #
             self.src["X"] = "%f"%pos.x
             self.src["Y"] = "%f"%pos.y
             self.src["Z"] = "%f"%pos.z
             
         #
         # `action' is the function that is called when the
         #   data in the dialog box is changed
         #
         def action(self, pack=pack, editor=editor):
             #
             # read the new data from self.src
             #
             src = self.src
             #
             # Showing off with lambda as well as map. Could be
             # done three statements, in the style of setup above
             #
             x,y,z = map(lambda d,src=src:eval(src[d]),("X","Y","Z"))
             newpos = quarkx.vect(x,y,z)
             #
             # calculate the desired movement, get list of locked
             #  vertices, etc.
             #
             delta = newpos-pack.pos
             #
             # grid stuff
             #
             gridstep = editor.gridstep
             #
             # There's tricky approximation stuff here, just empirical,
             #  I don't understand the math.
             #
             if gridstep:
                 if src["gridpos"]:
                     #
                     # map a delta component
                     #
                     def delcom(d, p, gridstep=gridstep):
                         offgrid = p%gridstep
                         #
                         # or should we force to grid?
                         #
                         if abs(d)<0.01:
                            return 0.0
                         #
                         # little change, increment/decrement
                         #
                         if abs(d)<=1.0:
                             if d>0:
                                 return gridstep-offgrid
                             else:
                                 return -gridstep-offgrid
                         #
                         # otherwise round off change so final
                         #  pozzie goes to nearest gridpoint
                         #
                         offgrid = (p+d)%gridstep
                         if offgrid<(gridstep/2.0):
                             return d-offgrid
                         else:
                             return d+gridstep-offgrid
                 elif src["griddel"]:
#                     debug('griddel')
                     def delcom(d, p, gridstep=gridstep):
                         if abs(d)<.01:
                             return 0.0
                         if abs(d)<=1.0:
                             if d>0:
                                 return gridstep
                             else:
                                 return -gridstep
                         offgrid = d%gridstep
                         if offgrid<(gridstep/2.0):
                             return d-offgrid
                         else:
                             return d+gridstep-offgrid
                 else:
                     def delcom(d, p, gridstep=gridstep):
                         return d
#                 debug('orig delta: '+`delta`)
                 delta = quarkx.vect(tuple(map(delcom,delta.tuple, pack.pos.tuple)))
             oldfaces=pack.moving
             locklist = getAttr(editor,'lockedVertices',[])
             freezelist = getAttr(editor,'frozenFaces',[])
             #
             # calculate the new faces
             #
             oldfaces, newfaces = moveFaces(oldfaces, pack.pos, delta, pack.poly, locklist, freezelist, src["sloppy"])
             #
             # Mere return from function produces None return value.
             #  exceptions would be the way to go if there were
             #  more different kinds of failure to deal with.
             #
             # A `computational' routine such as moveFaces shouldn't
             #  throw up error dialog boxes itself, but leave this
             #  to the callers.
             #
             if newfaces is None:
                 quarkx.msgbox("Face can't move because of locks",
                     MT_ERROR, MB_OK)
                 return
             #
             # swap them into the map
             #
             undo=quarkx.action()
             for i in range(len(oldfaces)):
                undo.exchange(oldfaces[i], newfaces[i])
             editor.ok(undo, "Move vertex")
             #
             # check for lost vertex
             #
             newpos = pack.pos+delta
             if not freezelist:
               for face in newfaces:
                 for vtx in face.verticesof(pack.poly):
                     if abs(newpos-vtx)<.01:
                         break
                 else:
                     #
                     # For some unknown magical reason, the appearance
                     #  of this dialog causes the mov
                     #
                     if not src["sloppy"]:
                         quarkx.msgbox("Moving Vertex Lost",MT_INFORMATION,MB_OK)
                 break
                 
             #
             # Now put the replacement info into pack (if
             #  this isn't done, undo won't work right for
             #  repeat entry of data info dialog
             #
             pack.moving = newfaces
             pack.pos = newpos
             #
             # For some unkoown reason, the exchange operation
             #  above causes the new stuff to become the selection;
             #  so we set things back the way they were
             #
             editor.layout.explorer.sellist=[pack.poly]
             #
             # and reset the options in case we've changed them
             #
             options = quarkx.setupsubset(SS_MAP, "Options")
             options["movevertex_gridpos"]=self.src["gridpos"]
             options["movevertex_griddel"]=self.src["griddel"]
             options["movevertex_sloppy"]=self.src["sloppy"]
             
         #
         # This is an optional callback for final cleanup
         #
         def onclosing(self, editor=editor):
             delAttr(editor,'movingvertex')
             editor.invalidateviews()
         
         #
         # And at least create the dialog.
         # quarkx.clickform is the window last clicked in,
         #  needed here by the rules of Black Magic
         # 'vtxdrag' is the tag under which the dimensions
         #  of the box are retained in setup.qrk (value of
         #  dlgdim_vtxdrag specific); to check the size that
         #  the dialog definition above is producing (size),
         #  delete this from setup.qrk after closing quark,
         #  and then reopen & fire up the dialog.
         # Then editor is required, and the first two `callback'
         #  functions we've defined, and the last as an option.
         #
         VtxDragDlg(quarkx.clickform, 'vtxdrag', editor, setup, action, onclosing)
             
    #
    # And now a bunch of simple litte menu item callbacks
    #
    def lockclick(m, self=self, editor=editor):
        try:
            editor.lockedVertices.append(self)
        except (AttributeError):
            editor.lockedVertices = [self]
        #
        # redraw the views to see the effect.
        #
        editor.invalidateviews()
        
    def clearclick(m, self=self, editor=editor):
        delAttr(editor,'lockedVertices')
        delAttr(editor,'frozenFaces')
        editor.invalidateviews()
    
    def unlockclick(m, editor=editor):
        removeFromAttr(editor,'lockedVertices',m.unlockMe)
#        editor.lockedVertices.remove(m.unlockMe)
#        if editor.lockedVertices == []:
#            del editor.lockedVertices
        editor.invalidateviews()
 

    #
    # Moving a containing group so that the vertex shifts to ongrid
    #
    def moveparentpopup(self=self,editor=editor):
        shift=self.pos-editor.aligntogrid(self.pos)

        def makeitem(object,editor,r,shift=shift):

            def Shifter(m, object=object, editor=editor, shift=shift):
                new=object.copy()
                undo=quarkx.action()
                new.translate(shift)
                undo.exchange(object, new)
                editor.ok(undo, "Move object")
                editor.invalidateviews()

            item = qmenu.item(object.name,Shifter, "Move me")
            item.menuicon = object.geticon(1)
            return item
            
        poly=self.poly
        list=guiutils.buildParentPopupList(self.poly,makeitem, editor)
        return list
     
    #
    # And their menu items
    #
    moveparentitem = qmenu.popup("&Move Containing", moveparentpopup(),
      hint="|The clicked-on containing object of this vertex will be moved so as to force the vertex onto the grid.")
    moveitem = qmenu.item("&Move Vertex", moveclick)
    lockitem = qmenu.item("&Lock Vertex", lockclick)
    unlockitem = qmenu.item("&Unlock Vertex", unlockclick)
    clearitem = qmenu.item("&Clear Locks", clearclick)
    #
    # And a bit of convoluted logic for enable/disable
    #
    locker = lockitem
    try:
        locklist = editor.lockedVertices
    except (AttributeError):
        pass
    else:
        for vtxh in locklist:
            if not(vtxh.pos-self.pos):
                unlockitem.unlockMe = vtxh
                locker = unlockitem
                moveitem.state = qmenu.disabled
                break
    #
    # And we return the menu, the new items stuck onto the
    #  front of the old.
    #
    return [moveparentitem, moveitem, locker, clearitem]+oldmenu(self,editor,view)
    
#
# And here's the magic bit; when vertexmenu got defined, the
#  original menu function for quarkpy.maphandles.VertexHandle
#  got stored within it (as `oldmenu'); now we replace
#  it in the quarkpy.maphandles.VertexHandle with out new
#  creation
#
quarkpy.maphandles.VertexHandle.menu = vertexmenu

#
# Should be generalized from tagging
#

#
# And a different version of the same trick to get the little
#  blue squares drawn around the locked vertices, this time by
#  replacing quarkpy.qbaseeditor.BaseEditor.finishdrawing
#
# Also the green square around the moving vertex
#
from tagging import drawredface # misnamed, oh well

def lockfinishdrawing(editor, view, oldmore=quarkpy.mapeditor.MapEditor.finishdrawing):
      cv = view.canvas()
      try:
         locks = editor.lockedVertices
      except (AttributeError):
         pass
      else:
         cv.pencolor = MapColor("Duplicator")
         for vtxh in locks: # these are handles
             p1 = view.proj(vtxh.pos)
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

quarkpy.mapeditor.MapEditor.finishdrawing = lockfinishdrawing


def vec2rads(v):
    "returns pitch, yaw, in radians"
    v = v.normalized
    import math
    pitch = -math.sin(v.z)
    yaw = math.atan2(v.y, v.x)
    return pitch, yaw

def find3DView(editor):
    views = []
    for v in editor.layout.views:
        if v.info["type"]=="3D":
            views.append(v)
    if views == []:
        return
    return views[0]


#
# And now the whole bizness again to lock every vertex of a face
#
def lockfacemenu(o, editor, oldfacemenu = quarkpy.mapentities.FaceType.menu.im_func):
    
    def lockclick(m,face=o,editor=editor):
        locks = getAttr(editor,'lockedVertices',[])
        for poly in face.faceof:
            for vtx in face.verticesof(poly):
                locks.append(quarkpy.maphandles.VertexHandle(vtx, poly))
        editor.lockedVertices = locks
        editor.invalidateviews()
     
    def unlockclick(m, face=o, editor=editor):
        try:
            locks = editor.lockedVertices
        except (AttributeError):
            return
        for poly in face.faceof:
            for vtx in face.verticesof(poly):
                for hvtx in locks[:]:
                    if not (hvtx.pos-vtx):
                        locks.remove(hvtx)
        editor.invalidateviews()
                        
    def viewclick(m, face=o, editor=editor):
        if quarkx.keydown('\020')==1: # shift is down
            reverse = 1
        else:
            reverse = 0
        clickview = quarkx.clickform.focus 
        #
        # clickform doesn't seem to work for floating 3d windows
        #  so we just take the first.
        #
        if clickview is not None and clickview.info["type"]=="3D":
            view = clickview
        else:
            view = find3DView(editor)
            if view is None:
                quarkx.msgbox("Need an open 3D view for this one!",
                   MT_ERROR,MB_OK)
                return
        #
        # Should have a 3D view here
        #
        pos, yaw, pitch = view.cameraposition
        dist = abs(pos - face.origin)
        if reverse:
            norm = -face.normal
        else:
            norm = face.normal
        newpos = face.origin+dist*(norm)
        pitch, yaw = vec2rads(-norm)
        view.cameraposition = newpos, yaw, pitch
        editor.invalidateviews()

    def freezeclick(m, face=o, editor=editor):
        appendToAttr(editor, 'frozenFaces', face)
        editor.invalidateviews()
        
    def unfreezeclick(m, face=o, editor=editor):
        removeFromAttr(editor, 'frozenFaces', face)
        editor.invalidateviews()

    lockitem = qmenu.item("Lock Vertices",lockclick,"Locks all vertices on this face")
    unlockitem = qmenu.item("Unlock Vertices", unlockclick,"Unlocks vertices on this face")
    freezeitem = qmenu.item("Freeze Face", freezeclick,"|Plane of face doesn't move, so vertices are confined to move within it. (So they don't go exactly where they're told to).")
    unfreezeitem = qmenu.item("Unfreeze Face", unfreezeclick, "|To unfreeze all frozen faces, clear locks on vertex menu.")
    freezer = freezeitem
    try:
        freezelist = editor.frozenFaces
    except (AttributeError):
        pass
    else:
        for face in freezelist:
            if o is face:
                freezer = unfreezeitem
                break
                
    viewitem = qmenu.item("Look At", viewclick, "|An open 3D view shifts to look at this face head on.\n (SHIFT to look at the face from the back)")

    locking = qmenu.popup("Lock/Freeze",[lockitem,unlockitem, freezer],
        hint = "|Submenu for items that are supposed to help in placing vertices by controlling which faces & vertices can move and which can't.")

    return [locking, viewitem]+oldfacemenu(o, editor)

quarkpy.mapentities.FaceType.menu = lockfacemenu


#
#  Code for looking at center of selection
#
def originmenu(self, editor, view, oldoriginmenu = quarkpy.qhandles.GenericHandle.OriginItems.im_func):
  
    menu = oldoriginmenu(self, editor, view)
    
    if view is not None:

      def seePointClick(m,self=self,editor=editor):
        view = find3DView(editor)
        pos, yaw, pitch = view.cameraposition
        dir = (self.pos-pos).normalized
        pitch, yaw = vec2rads(dir)
        view.cameraposition = pos, yaw, pitch
        editor.invalidateviews()

      seeitem = qmenu.item("Look To",seePointClick,"|Aims an open 3d view at object")
    
      menu[1:1] = [seeitem]

    return menu

quarkpy.qhandles.GenericHandle.OriginItems = originmenu


#
# Proper version of this now committed to main branch
#
#
# 3d view camera circlestrafe
#   This stuff is to be supported in qhandles as "C" mouse-drag
#   option (Shift-LMB drag by default), so this code will
#   be removed from the final version.
#

def circleinit(self, editor, view, x, y, old = quarkpy.qhandles.SideStepDragObject.__init__):
    self.editor = editor
    old(self, editor, view, x, y)
    
quarkpy.qhandles.SideStepDragObject.__init__= circleinit
    
def circledragto(self, x, y, flags, olddragto=quarkpy.qhandles.SideStepDragObject.dragto):
    sel = self.editor.layout.explorer.sellist
    if sel and quarkx.keydown('Z')==1:
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
        self.view.cameraposition = newpos, yaw, pitch
    else:
        olddragto(self, x, y, flags)

quarkpy.qhandles.SideStepDragObject.dragto = circledragto

# $Log: mapmovevertex.py,v $
# Revision 1.11  2008/02/22 09:52:21  danielpharos
# Move all finishdrawing code to the correct editor, and some small cleanups.
#
# Revision 1.10  2005/10/15 00:51:24  cdunde
# To reinstate headers and history
#
# Revision 1.7  2002/05/18 22:38:31  tiglari
# remove debug statement
#
# Revision 1.6  2002/04/01 08:30:05  tiglari
# shift out the parentpopup menu stuff (to quarkpy.guiutils)
#
# Revision 1.5  2002/03/30 09:31:14  tiglari
# Add 'move containing' item to the vertex RMB that moves a containing
#   object so that the vertex becomes on-grid.
#
# Revision 1.4  2001/06/17 21:10:57  tiglari
# fix button captions
#
# Revision 1.3  2001/06/16 03:19:05  tiglari
# add Txt="" to separators that need it
#
# Revision 1.2  2001/05/24 22:28:05  tiglari
# fix tuple bug, improved anti-drift
#
# Revision 1.1  2001/04/01 22:45:31  tiglari
# initial commit
#