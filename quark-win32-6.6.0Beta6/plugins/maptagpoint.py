"""   QuArK  -  Quake Army Knife Bezier shape makers


"""
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/maptagpoint.py,v 1.4 2005/11/10 17:43:55 cdunde Exp $


########################################################
#
#               Point Tagging and Glueing for QuArK
#                     v1, Jul 16, 2000
#                   works with Quark6.x
#
#              by tiglari@hexenworld.net)
#              based on work by Armin Rigo,
#
#   Material excised from maptagside.py, to clean up that
#    file a bit.
#
###########################################################

Info = {
   "plug-in":       "Point Tag & Glue",
   "desc":          "Tagging and Glueing of points",
   "date":          "Jul 16, 2000",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.net",
   "quark":         "Quark 6.x" }


import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.qmenu
import quarkpy.mapeditor
import quarkpy.mapcommands
import quarkpy.maphandles
from quarkpy.maputils import *
from tagging import *


def disttotagged(editor,pos):
  pt = gettaggedpt(editor)
  item = qmenu.item("Distance to tagged",DistTaggedClick,"|Distance from here to the tagged point")
  if pt is None:
    item.state=qmenu.disabled
  else:
    item.dist=abs(pt-pos)
  return item

def DistTaggedClick(m):
  quarkx.msgbox("Distance = "+`m.dist`+" units",
    MT_INFORMATION,MB_OK)


def TagPointClick (m):
  "tags a single point"
  editor = mapeditor()
  if editor is None: return
  tagpoint(m.pos, editor)

def makeedge(o, editor):
  item = quarkpy.qmenu.item("Tag Edge",MakeEdgeClick,"|This command makes a `virtual edge' between the tagged point and this one, which becomes tagged, for glueing Bezier patches to.")
  taggedpt = gettaggedpt(editor)
  if taggedpt is None:
    item.state = qmenu.disabled
  else:
    item.tagged = taggedpt
    item.o = o
  return item

def makeplane(pos, editor):
    item = quarkpy.qmenu.item("Tag Plane",MakePlaneClick,"|This command makes a tagged plane with the tagged edge and this point")
    edge = gettaggededge(editor)
    if edge is None:
        item.state=qmenu.disabled
    else:
        item.pos = pos
    return item

def MakeEdgeClick(m):
  "assumes that a point is tagged"
  editor = mapeditor()
  if editor is None: return
  tagedge(m.tagged, m.o.pos, editor)

def MakePlaneClick(m):
    "assumes that an edge is tagged"
    editor = mapeditor()
    if editor is None: return
    p1, p2 = gettaggededge(editor)
    tagplane((m.pos,p1,p2), editor)
    
def tagpointitem(editor, origin):
  from maptagside import ClearTagClick
  oldtag = gettaggedpt(editor)
  if oldtag is not None and not (origin-oldtag):
    tagv = qmenu.item("Clear tag", ClearTagClick)
  else:
    tagv = qmenu.item("&Tag point", TagPointClick, "|`Tags' the point below the mouse for reference in later operations of positioning and alignment.\n\nThe tagged point then appears in red.\n\nFor more detail on the use of this fuction, click on the InfoBase button below.|maped.plugins.tagside.html#basic")
    tagv.pos = origin
    tagv.tagger = 1
  return tagv


def originmenu(self, editor, view, oldoriginmenu = quarkpy.qhandles.GenericHandle.OriginItems.im_func):

  menu = oldoriginmenu(self, editor, view)
  if isinstance(self, quarkpy.maphandles.FaceHandle):
    return menu        # nothing to do for faces

  if len(menu)==0 or menu[0] is not qmenu.sep:
    menu[:0] = [qmenu.sep]  # inserts a separator if necessary

  if view is not None:   # Point gluing for everything

    def GluePointClick(m, self=self, editor=editor, view=view):
      tagpt = gettaggedpt(editor)
      if tagpt is not None:
        self.Action(editor, self.pos, tagpt, MB_NOGRID, view)
      else:
        tagged = gettagged(editor)
        if tagged is not None:
          p = self.pos
          p = p - tagged.normal * (p*tagged.normal-tagged.dist)
          self.Action(editor, self.pos, p, MB_NOGRID, view)

    gluev = qmenu.item("&Glue to tagged", GluePointClick, "|Glue this point to the tagged point, or if a side is tagged, move this point into the plane of this side.")
    if not anytag(editor):
      gluev.state = qmenu.disabled
    menu[1:1] = [gluev]

  menu[1:1] = [tagpointitem(editor, self.pos),
               makeedge(self, editor),
               makeplane(self.pos, editor),
               disttotagged(editor, self.pos)]
  return menu

quarkpy.qhandles.GenericHandle.OriginItems = originmenu


# ----------- REVISION HISTORY ------------
#
# $Log: maptagpoint.py,v $
# Revision 1.4  2005/11/10 17:43:55  cdunde
# To add header and start history log
#
#