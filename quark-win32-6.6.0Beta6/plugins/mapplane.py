"""   QuArK  -  Quake Army Knife Bezier shape makers


"""
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapplane.py,v 1.6 2005/10/15 00:51:24 cdunde Exp $

Info = {
   "plug-in":       "Three Pooint Plane plugin",
   "desc":          "Define a plane from three points",
   "date":          "May 25, 2001",
   "author":        "tiglari",
   "author e-mail": "tiglari@planetquake.com",
   "quark":         "Version 6.3"
}


import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.mapeditor
import quarkpy.mapcommands
import quarkpy.mapoptions
import quarkpy.maphandles
import quarkpy.dlgclasses
import quarkpy.mapduplicator
StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator
from quarkpy.maputils import *
from tagging import *

class PlaneHandle(quarkpy.maphandles.CenterHandle):

    def __init__(self, pos, dup, color):
        self.dup=dup
        quarkpy.maphandles.CenterHandle.__init__(self,pos,dup,color)

    def menu(self, editor, view):
        oldmenu = quarkpy.maphandles.CenterHandle.menu(self, editor, view)

        def tagplane(m,self=self, editor=editor):
            p0,p1,p2,p3=self.pozzies()
            tagplane((p1,p2,p3),editor)

        def glueplane(m, self=self, editor=editor):
            p1,p2,p3=editor.tagging.taggedplane
            plane=self.centerof
            undo=quarkx.action()
            for (spec,val) in (("P1", p1), ("P2",p2), ("P3",p3)):
                 undo.setspec(plane,spec,val.tuple)                 
            editor.ok(undo,"Glue plane to tagged")            

        tagitem = qmenu.item("Tag Plane",tagplane)
        glueitem = qmenu.item("Glue to tagged plane", glueplane)

        tagged = gettaggedplane(editor)
        if tagged is None:
            glueitem.state=qmenu.disabled
        return [tagitem, glueitem]+oldmenu

    def pozzies(self):
        def getpos(spec,dup=self.dup):
            return quarkx.vect(dup[spec])
        points = map(getpos,("P1","P2","P3"))
        return [reduce(lambda x,y:x+y,points)/3.0]+points



#
#  --- Duplicators ---
#
class PlaneCenterHandle(PlaneHandle):
    "A handle for accessing the center a plane."

    def __init__(self, dup):
        self.dup=dup # gotto do this first
        self.pos = self.pozzies()[0]
        PlaneHandle.__init__(self, self.pos, dup, MapColor("Axis"))

    def drag(self, v1, v2, flags, view):
        delta = v2-v1
        dup = self.centerof
        pos0 = self.pos
        if flags&MB_CTRL:
            newpos = aligntogrid(pos0+delta,1)
        else:
            delta = quarkpy.qhandles.aligntogrid(delta,1)
            newpos = pos0+delta
        newdelta = newpos-pos0
        if delta or (flags&MB_REDIMAGE):
            new = self.centerof.copy()
            for spec in ("P1", "P2", "P3"):
                new[spec]=(quarkx.vect(new[spec])+newdelta).tuple
            new = [new]
        else:
            new = None
        return [self.centerof], new

    def draw(self, view, cv, draghandle=None):
        quarkpy.maphandles.CenterHandle.draw(self,view,cv,draghandle)
        #
        # color-change isn't working. also why no show
        #   during drag?
        #
        dyn = draghandle is self
        if dyn:
            pencolor = RED
        else:
            pencolor = 0xF0CAA6
        pt = map(view.proj, self.pozzies())
        cv.penwidth-2
        cv.pencolor=pencolor
        for i in (1,2,3):
            cv.line(pt[0], pt[i])


class PlanePointHandle(PlaneHandle):
  "A point for defining a plane."

  def __init__(self, dup, spec):
      self.spec=spec
      pos = quarkx.vect(dup[spec])
      PlaneHandle.__init__(self, pos, dup, MapColor("Axis"))

  def drag(self, v1, v2, flags, view):
      delta = v2-v1
      dup, spec = self.centerof, self.spec
      pos0 = quarkx.vect(dup[spec])
      if flags&MB_CTRL:
          newpos = aligntogrid(pos0+delta,1)
      else:
          delta = quarkpy.qhandles.aligntogrid(delta,1)
          newpos = pos0+delta
      if delta or (flags&MB_REDIMAGE):
          new = self.centerof.copy()
          new[spec]=newpos.tuple
          new = [new]
      else:
          new = None
      return [self.centerof], new


class PlaneDuplicator(StandardDuplicator):

    def buildimages(self):
        return []

    def handles(self, editor, view):
        def makehandle(spec,self=self):
            return PlanePointHandle(self.dup,spec)
        list = map(makehandle,["P1", "P2", "P3"])+[PlaneCenterHandle(self.dup)]
        return list
        

quarkpy.mapduplicator.DupCodes.update({
  "dup plane":  PlaneDuplicator,
})

#
# Make a 3point plane from a tagged plane
#

#
# Probably not useful, but here it is anyway
#
def make3points(m):
    editor=mapeditor()
    if editor is None: return
    #
    # gettaggedplane returns a face, we want the points,
    #  assumes item disabled if taggedplane nexistepas
    #
    p1,p2,p3=editor.tagging.taggedplane
    plane = quarkx.newobj("plane duplicator:d")
    plane["macro"]="dup plane"
    for (spec,val) in (("P1", p1), ("P2",p2), ("P3",p3)):
#         debug('spec '+spec+'; val: '+`val`)
         plane[spec]=val.tuple
    undo=quarkx.action()
    sel = editor.layout.explorer.uniquesel
    parent=sel.treeparent
    while not parent.acceptitem(plane):
       parent=parent.treeparent
    undo.put(parent,plane,sel)
    editor.ok(undo,"Create 3point plane")
    editor.layout.explorer.uniquesel=plane

planeItem = qmenu.item("Plane from tagged points", make3points)

def commandsclick(menu, oldcommand=quarkpy.mapcommands.onclick):
    editor=mapeditor()
    if editor is None: return
    plane=gettaggedplane(editor)
    if plane is None:
       planeItem.state=qmenu.disabled
    else:
       planeItem.state=qmenu.normal
      
#quarkpy.mapcommands.onclick = commandsclick

#quarkpy.mapcommands.items.append(planeItem)


#$Log: mapplane.py,v $
#Revision 1.6  2005/10/15 00:51:24  cdunde
#To reinstate headers and history
#
#Revision 1.3  2002/05/18 22:38:31  tiglari
#remove debug statement
#
#Revision 1.2  2001/07/24 02:37:11  tiglari
#glue plane to tagged plane
#
#Revision 1.1  2001/05/25 12:27:15  tiglari
#tagged plane support
#
#
