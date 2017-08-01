"""   QuArK  -  Quake Army Knife Bezier shape makers


"""
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapstair.py,v 1.9 2005/10/15 00:51:24 cdunde Exp $

Info = {
   "plug-in":       "Stairmaker plugin",
   "desc":          "Making stairs from brushes",
   "date":          "2001-02-20",
   "author":        "decker",
   "author e-mail": "decker@planetquake.com",
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

import quarkpy.mapbezier
from quarkpy.b2utils import *
from quarkpy.perspective import *

#
#  --- Duplicators ---
#

class StairDuplicator(StandardDuplicator):

  def makeStairs(self, o, steps=8, sameheight="", oldstyle=""):
      result = []
      #
      # rebuildall() is needed in order for the pointdict function
      #  below to work, when a map with the dup is loaded up
      #  (treacherous bug, doesn't appear when dup is introduced
      #  into map, only when it's loaded).
      #
      o.rebuildall()
      faces = faceDict(o)
      if len(faces)==6:
          points = pointdict(vtxlistdict(faces,o))
          frontnormal = faces['f'].normal
          backnormal = faces['b'].normal
          frontdist = faces['f'].dist
          backdist = faces['b'].dist
          frontbacklength = abs((frontnormal*frontdist) - (backnormal*backdist))
          frontbackinterval = frontbacklength/steps

          upnormal = faces['u'].normal
          downnormal = faces['d'].normal
          updist = faces['u'].dist
          downdist = faces['d'].dist
          updownlength = abs((upnormal*updist) - (downnormal*downdist))
          updowninterval = updownlength/steps

          for step in range(steps):
              poly = quarkx.newobj("stairstep %d:p" % step)

              face = faces['l'].copy()
              poly.appenditem(face)
              face = faces['r'].copy()
              poly.appenditem(face)

              face = faces['u'].copy()
              face.translate(-upnormal * (updowninterval * (steps - step - 1)))
              poly.appenditem(face)

              face = faces['d'].copy()
              if sameheight != "":
                 face.translate(-downnormal * (updowninterval * step))
              poly.appenditem(face)
              down = face

              face = faces['f'].copy()
              face.translate(-frontnormal * (frontbackinterval * step))
              poly.appenditem(face)

              face = faces['b'].copy()
              face.translate(-backnormal * (frontbackinterval * (steps - step - 1)))
              poly.appenditem(face)
              back = face

              result.append(poly)
              #debug('oldstyle: %s'%oldstyle)

              if sameheight!="1" and oldstyle!="1":
                  #
                  # the 'back' goes from the upper back of the stairstep to the
                  #   lower back of the whole thing.
                  # the 'down' goes from the the bottom of the visible front of the
                  #   stairstep to the lower back of the whole thing
                  #
                  #debug('here')
                  upperback = points["trb"] - backnormal * frontbackinterval * (steps - step - 1) - upnormal * (updowninterval * (steps - step - 1))
                  back.setthreepoints((upperback, points["brb"], points["blb"]),0)
                  lowerfront = points["trb"] - backnormal * frontbackinterval * (steps-step) - upnormal*updowninterval*(steps-step)
                  down.setthreepoints((lowerfront, points["blb"], points["brb"]),0)


      return result

  def buildimages(self, singleimage=None):
    if singleimage is not None and singleimage>0:
      return []
    editor = mapeditor()
    steps,   sameheight, oldstyle = map(lambda spec, self=self: self.dup[spec],
     ("steps", "sameheight", "oldstyle"))
    list = self.sourcelist()
    for o in list:
      if o.type==":p": # just grab the first one, who cares
        return self.makeStairs(o, int(steps), sameheight, oldstyle)


quarkpy.mapduplicator.DupCodes.update({
  "dup stair":  StairDuplicator,
})

#
#  --- Menus ---
#

def curvemenu(o, editor, view):

  def makestair(m, o=o, editor=editor):
      dup = quarkx.newobj("Stair Maker:d")
      dup["macro"]="dup stair"
      dup["steps"]="8"
      dup["sameheight"]=""
      dup["oldstyle"]=""
      dup.appenditem(m.newpoly)
      undo=quarkx.action()
      undo.exchange(o, dup)
      editor.ok(undo, "make stair maker")
      editor.invalidateviews()

  disable = (len(o.subitems)!=6)

  newpoly = perspectiveRename(o, view)

  def finishitem(item, disable=disable, o=o, view=view, newpoly=newpoly):
      disablehint = "This item is disabled because the brush doesn't have 6 faces."
      if disable:
          item.state=qmenu.disabled
          try:
              item.hint=item.hint + "\n\n" + disablehint
          except (AttributeError):
              item.hint="|" + disablehint
      else:
          item.o=o
          item.newpoly = newpoly
          item.view = view

  item = qmenu.item("Stair", makestair)
  finishitem(item)

  return item

#
# First new menus are defined, then swapped in for the old ones.
#  `im_func' returns from a method a function that can be
#   assigned as a value.
#
def newpolymenu(o, editor, oldmenu=quarkpy.mapentities.PolyhedronType.menu.im_func):
    "the new right-mouse perspective menu for polys"
    #
    # cf FIXME in maphandles.CenterHandle.menu
    #
    try:
        view = editor.layout.clickedview
    except:
        view = None
    return  [curvemenu(o, editor, view)]+oldmenu(o, editor)

#
# This trick of redefining things in modules you're based
#  on and importing things from is something you couldn't
#  even think about doing in C++...
#
# It's actually warned against in the Python programming books
#  -- can produce hard-to-understand code -- but can do cool
#  stuff.
#
#
quarkpy.mapentities.PolyhedronType.menu = newpolymenu


# ----------- REVISION HISTORY ------------
#$Log: mapstair.py,v $
#Revision 1.9  2005/10/15 00:51:24  cdunde
#To reinstate headers and history
#
#Revision 1.6  2003/04/22 11:48:03  tiglari
#fix bug that was causing stairs not to  work right when maps reloaded;
#fix indentation
#
#Revision 1.5  2003/04/09 00:59:02  cdunde
#To comment out debugs
#
#Revision 1.4  2003/04/08 06:07:33  cdunde
#tris/overdraw-efficient fan-style stair, as suggested by foo, quakin' and Plan B
#on the quake3world editing forum.  For old non-equal-height stair, use
#'oldstyle' checkbox specific - by tiglari
#finish needed changes to activate  'oldstyle' specific - by cdunde
#
#Revision 1.3  2001/03/03 19:26:59  decker_dk
#Minor problem fixed.
#
#Revision 1.2  2001/02/14 10:08:58  tiglari
#extract perspective stuff to quarkpy.perspective.py
#
#Revision 1.1  2001/02/04 11:52:01  decker_dk
#Stair making plugin
#
