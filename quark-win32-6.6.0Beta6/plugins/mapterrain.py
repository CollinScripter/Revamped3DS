"""   QuArK  -  Quake Army Knife Bezier shape makers

"""
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#py2.4 indicates upgrade change for python 2.4

#$Header: /cvsroot/quark/runtime/plugins/mapterrain.py,v 1.8 2008/04/16 12:39:51 danielpharos Exp $

Info = {
   "plug-in":       "Terrainmaker plugin",
   "desc":          "Making terrain from brushes",
   "date":          "2005-02-20",
   "author":        "cdunde and Rowdy",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6.4"
}


import quarkx                    # may not need
import quarkpy.mapoptions        # may not need
from quarkpy.maputils import *   # may not need
from quarkpy.qhandles import *   # may not need
from quarkpy.qutils import *     # may not need
from quarkpy.mapduplicator import *

import quarkpy.mapentities
import quarkpy.mapmenus
StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator
from quarkpy.perspective import *

#
#  --- Duplicators ---
#

replygiven = 0   # new Rowdys suggestion stops repeated error msgs of size

class TerrainDuplicator2(StandardDuplicator):

  def stretchgrid(editor,undo,movee,tagdict):
      mapdict = getspecdict("_tag",editor.Root)
      for key in tagdict.keys():
          face1 = tagdict[key][0]
          faces = mapdict[key]
          for face in faces:
            if checktree(movee,face) or coplanar(face,face1):
                continue
            movegrid(undo,face,face1)

  def makeTerrain2(self, loops, wedges, o, wedgeunits=32, sameheight="", detailmesh=""):

      global replygiven  # new Rowdys suggestion stops repeted error msgs

      def newfinishdrawing(editor, view, oldfinish=quarkpy.mapeditor.MapEditor.finishdrawing):
          oldfinish(editor, view)

      loops = 0
      wedges = 0
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
          leftnormal = faces['l'].normal
          rightnormal = faces['r'].normal
          leftdist = faces['l'].dist
          rightdist = faces['r'].dist
          leftrightlength = abs((leftnormal*leftdist) - (rightnormal*rightdist)) #total length of strech box
          leftrightinterval = wedgeunits
          frontnormal = faces['f'].normal
          backnormal = faces['b'].normal
          frontdist = faces['f'].dist
          backdist = faces['b'].dist
          frontbacklength = abs((frontnormal*frontdist) - (backnormal*backdist))
          frontbackinterval = wedgeunits
          wedges = leftrightlength/wedgeunits
          upnormal = faces['u'].normal
          downnormal = faces['d'].normal
          updist = faces['u'].dist
          downdist = faces['d'].dist
          updownlength = abs((upnormal*updist) - (downnormal*downdist))
          updowninterval = updownlength/wedgeunits
          loops = frontbacklength / frontbackinterval

          if loops > 25 or wedges > 25:
              if detailmesh!="1":
                  if replygiven == 1:
                      replygiven = 1
                      return

                  replygiven = 1
                  response = quarkx.msgbox("This Grid will create a lot of polys !\n\nYou can select 'Cancel' and reset\nyour wedgeunits to a larger size\n\nor select 'OK' to continue to\nmake the Grid for detail work", MT_WARNING, MB_OK_CANCEL)

                  quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                  editor = mapeditor()
                  editor.invalidateviews(1)

                  if response == MR_CANCEL:
                      replygiven = 0
                      obj = editor.layout.explorer.uniquesel.parent
                      quarkx.undostate(obj)
                      quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                      return

                  if response == MR_OK:
                      replygiven = 1
                      dupObject = o.parent                # new code by Rowdy
                      if dupObject.type == ":d":          # new code by Rowdy
                          dupObject["detailmesh"]="1"       # new code by Rowdy
                      quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing

          for loop in range(int(loops)):   #py2.4
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['l'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * (leftrightinterval * (wedges - wedge - 1)) + (backnormal * (frontbackinterval*(loops-loop-1))))
                  upperback = points["blb"] + rightnormal * (leftrightinterval * (wedges - wedge - 1)) + (backnormal * (frontbackinterval*(loops-loop-1)))
                  topfront = points["blb"] + rightnormal * (leftrightinterval * (wedges-wedge)) - (backnormal * (frontbackinterval*loop))

                  poly.appenditem(face)
                  left = face

                  face = faces['b'].copy()  #draws back face of each brush
                  face.translate(- backnormal * (frontbackinterval * loop))
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['f'].copy()  #draws the slice face of each brush
                  poly.appenditem(face)
                  front = face
                  front.setthreepoints((topfront, points["tlf"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(loops-loop-1))), points["blf"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(loops-loop-1)))),0) #beleave down face prob is here
                  face.shortname = "back"

                  result.append(poly)

              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(-rightnormal * (leftrightinterval * wedge))
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['f'].copy()  #draws the slice face of each brush
                  face.translate(backnormal * (frontbackinterval * (loops-loop-1)))
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws back face of each brush
                  poly.appenditem(face)
                  back = face
                  lowerback = points["brf"] - rightnormal * (leftrightinterval * wedge) + (backnormal * (frontbackinterval*(-loops+loop+1)))
                  bottomfront = points["brf"] - rightnormal * (leftrightinterval * (wedge + 1)) + (backnormal * (frontbackinterval*(loops-loop-1)))
                  back.setthreepoints((bottomfront, points["trb"] - rightnormal * leftrightinterval * wedge + (backnormal * (frontbackinterval*(-loop))), points["brb"] - rightnormal * leftrightinterval * wedge + (backnormal * (frontbackinterval*(-loop)))),0) #beleave down face prob is here

                  result.append(poly)
          return result

  def buildimages(self, singleimage=None):
      loops = 0
      wedges = 0
      if singleimage is not None and singleimage>0:
          return []
      editor = mapeditor()
      wedges, sameheight, detailmesh = map(lambda spec, self=self: self.dup[spec],
          ("wedgeunits", "sameheight", "detailmesh"))
      list = self.sourcelist()
      for o in list:
          facelist = o.dictitems
          if o.type==":p": # just grab the first one, who cares
              return self.makeTerrain2(loops, wedges, o, int(wedges), sameheight, detailmesh)

quarkpy.mapduplicator.DupCodes.update({"dup terrain2":  TerrainDuplicator2,})


class TerrainDuplicator2X(StandardDuplicator):

  def stretchgrid2X(editor,undo,movee,tagdict):
      mapdict = getspecdict("_tag",editor.Root)
      for key in tagdict.keys():
          face1 = tagdict[key][0]
          faces = mapdict[key]
          for face in faces:
            if checktree(movee,face) or coplanar(face,face1):
                continue
            movegrid(undo,face,face1)

  def makeTerrain2X(self, loops, wedges, o, wedgeunits=32, sameheight="", detailmesh=""):

      global replygiven  # new Rowdys suggestion stops repeted error msgs

      def newfinishdrawing(editor, view, oldfinish=quarkpy.mapeditor.MapEditor.finishdrawing):
          oldfinish(editor, view)

      loops = 0
      wedges = 0
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
          leftnormal = faces['l'].normal
          rightnormal = faces['r'].normal
          leftdist = faces['l'].dist
          rightdist = faces['r'].dist
          leftrightlength = abs((leftnormal*leftdist) - (rightnormal*rightdist)) #total length of strech box
          leftrightinterval = wedgeunits
          frontnormal = faces['f'].normal
          backnormal = faces['b'].normal
          frontdist = faces['f'].dist
          backdist = faces['b'].dist
          frontbacklength = abs((frontnormal*frontdist) - (backnormal*backdist)) #total length of strech box
          frontbackinterval = wedgeunits
          wedges = leftrightlength/(wedgeunits*2)
          upnormal = faces['u'].normal
          downnormal = faces['d'].normal
          updist = faces['u'].dist
          downdist = faces['d'].dist
          updownlength = abs((upnormal*updist) - (downnormal*downdist))
          updowninterval = updownlength/wedgeunits
          loops = frontbacklength / (frontbackinterval*2)

          if loops > 12.5 or wedges > 12.5:
              if detailmesh!="1":
                  if replygiven == 1:
                      replygiven = 1
                      return
                  replygiven = 1
                  response = quarkx.msgbox("This Grid will create a lot of polys !\n\nYou can select 'Cancel' and reset\nyour wedgeunits to a larger size\n\nor select 'OK' to continue to\nmake the Grid for detail work", MT_WARNING, MB_OK_CANCEL)

                  quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                  editor = mapeditor()
                  editor.invalidateviews(1)

                  if response == MR_CANCEL:
                      replygiven = 0
                      obj = editor.layout.explorer.uniquesel.parent
                      quarkx.undostate(obj)
                      quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                      return

                  if response == MR_OK:
                      replygiven = 1
                      dupObject = o.parent                # new code by Rowdy
                      if dupObject.type == ":d":          # new code by Rowdy
                          dupObject["detailmesh"]="1"       # new code by Rowdy
                      quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing

          for loop in range(int(loops)):   #py2.4
#1st pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['l'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * (leftrightinterval * (wedges*2- wedge*2 - 1)) + (backnormal * (frontbackinterval*(loops-loop*2-1))))
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws back face of each brush
                  face.translate(backnormal * (frontbackinterval * -loop*2))
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws back face of each brush
                  poly.appenditem(face)
                  right = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2-1)) + (backnormal * (frontbackinterval * ((-loop*2-1))))
                  right.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2) + (backnormal * (frontbackinterval * (-loop*2))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2) + (backnormal * (frontbackinterval * (-loop*2)))),0) #beleave down face prob is here
                  face.swapsides()
                  face.shortname = "back"
                  result.append(poly)

#2nd pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * (leftrightinterval * (- wedge*2)) + (backnormal * (frontbackinterval*(loops-loop*2-1))))
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws the slice face of each brush
                  face.translate(backnormal * (frontbackinterval * (-loop*2-1)))
                  face.swapsides()
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws back face of each brush
                  poly.appenditem(face)
                  right = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2-1)) + (backnormal * (frontbackinterval * ((-loop*2-1))))
                  right.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2) + (backnormal * (frontbackinterval * (-loop*2))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2) + (backnormal * (frontbackinterval * (-loop*2)))),0) #beleave down face prob is here
                  face.shortname = "back"
                  result.append(poly)

#3rd pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws back face of each brush
                  face.translate(backnormal * (frontbackinterval * (-loop*2)))
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws right face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * leftrightinterval * (-wedge*2-1))
                  upperback = points["trb"] + rightnormal * (leftrightinterval * ((-wedge*2)-1)) + backnormal * (frontbackinterval*(loops-(loop*2)))
                  poly.appenditem(face)

                  face = faces['l'].copy()  #draws the slice face of each brush
                  poly.appenditem(face)
                  left = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2-1)) + (backnormal * (frontbackinterval * ((-loop*2-1))))
                  left.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2-2) + (backnormal * (frontbackinterval * (-loop*2))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2-2) + (backnormal * (frontbackinterval * (-loop*2)))),0) #beleave down face prob is here
                  face.shortname = "back"
                  result.append(poly)

#4th pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws the slice face of each brush
                  face.translate(backnormal * (frontbackinterval * (-loop*2-1)))
                  face.swapsides()
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * leftrightinterval * (-wedge*2-2))
                  upperback = points["trb"] + rightnormal * (leftrightinterval * ((-wedge*2)-2)) + backnormal * (frontbackinterval*(loops-(loop*2)))
                  face.swapsides()
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws back face of each brush
                  poly.appenditem(face)
                  right = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2-1)) + (backnormal * (frontbackinterval * ((-loop*2-1))))
                  right.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2-2) + (backnormal * (frontbackinterval * (-loop*2))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2-2) + (backnormal * (frontbackinterval * (-loop*2)))),0) #beleave down face prob is here
                  face.swapsides()
                  face.shortname = "back"
                  result.append(poly)

#5th pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws back face of each brush
                  face.translate(backnormal * (frontbackinterval * (-loop*2-1)))
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws right face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * leftrightinterval * (-wedge*2))
                  upperback = points["trb"] + rightnormal * (leftrightinterval * ((-wedge*2))) + backnormal * (frontbackinterval*(loops-(loop*2-1)))
                  poly.appenditem(face)

                  face = faces['l'].copy()  #draws the slice face of each brush
                  poly.appenditem(face)
                  left = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2)) + (backnormal * (frontbackinterval * ((-loop*2-2))))
                  left.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1)))),0) #beleave down face prob is here
                  face.shortname = "back"
                  result.append(poly)

#6th pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws the slice face of each brush
                  face.translate(backnormal * (frontbackinterval * (-loop*2-2)))
                  face.swapsides()
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * leftrightinterval * (-wedge*2-1))
                  upperback = points["trb"] + rightnormal * (leftrightinterval * ((-wedge*2)-1)) + backnormal * (frontbackinterval*(loops-(loop*2-1)))
                  face.swapsides()
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws back face of each brush
                  poly.appenditem(face)
                  right = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2)) + (backnormal * (frontbackinterval * ((-loop*2-2))))
                  right.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1)))),0) #beleave down face prob is here
                  face.swapsides()
                  face.shortname = "back"
                  result.append(poly)

#7th pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws back face of each brush
                  face.translate(rightnormal * (leftrightinterval * (- wedge*2-2)) + (backnormal * (frontbackinterval*(-loop*2-1))))
                  face.swapsides()
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * (leftrightinterval * (- wedge*2-1)) + (backnormal * (frontbackinterval*(-loop*2-1))))
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws back face of each brush
                  poly.appenditem(face)
                  right = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2-2)) + (backnormal * (frontbackinterval * ((-loop*2-2))))
                  right.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1)))),0) #beleave down face prob is here
                  face.swapsides()
                  face.shortname = "back"
                  result.append(poly)

#8th pass of triangles
              for wedge in range(int(wedges)):   #py2.4
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws left face of each brush
                                            # and bases for setting slice points
                  face.translate(rightnormal * (leftrightinterval * (- wedge*2-1)) + (backnormal * (frontbackinterval*(loops-loop*2-2))))
                  face.shortname = "left"
                  poly.appenditem(face)

                  face = faces['b'].copy()  #draws the slice face of each brush
                  face.translate(backnormal * (frontbackinterval * (-loop*2-2)))
                  face.swapsides()
                  face.shortname = "right"
                  poly.appenditem(face)

                  face = faces['r'].copy()  #draws back face of each brush
                  poly.appenditem(face)
                  right = face
                  topfront = points["brb"] + rightnormal * (leftrightinterval * (-wedge*2-2)) + (backnormal * (frontbackinterval * ((-loop*2-2))))
                  right.setthreepoints((topfront, points["trb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1))), points["brb"] + rightnormal * leftrightinterval * (-wedge*2-1) + (backnormal * (frontbackinterval * (-loop*2-1)))),0) #beleave down face prob is here
                  face.shortname = "back"
                  result.append(poly)

          return result


  def buildimages(self, singleimage=None):

      loops = 0
      wedges = 0
      if singleimage is not None and singleimage>0:
          return []
      editor = mapeditor()

      wedges, sameheight, detailmesh = map(lambda spec, self=self: self.dup[spec],
          ("wedgeunits", "sameheight", "detailmesh"))
      list = self.sourcelist()
      for o in list:
          facelist = o.dictitems
          if o.type==":p": # just grab the first one, who cares
              return self.makeTerrain2X(loops, wedges, o, int(wedges), sameheight, detailmesh)


quarkpy.mapduplicator.DupCodes.update({"dup terrain2X":  TerrainDuplicator2X,})


class TerrainDuplicator4(StandardDuplicator):

  def stretchgrid4(editor,undo,movee,tagdict):
      mapdict = getspecdict("_tag",editor.Root)
      for key in tagdict.keys():
          face1 = tagdict[key][0]
          faces = mapdict[key]
          for face in faces:
            if checktree(movee,face) or coplanar(face,face1):
                continue
            movegrid(undo,face,face1)

  def makeTerrain4(self, loops, wedges, o, wedgeunits=32, sameheight="", detailmesh=""):

      global replygiven  # new Rowdys suggestion stops repeted error msgs

      def newfinishdrawing(editor, view, oldfinish=quarkpy.mapeditor.MapEditor.finishdrawing):
          oldfinish(editor, view)

      loops = 0
      wedges = 0
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
          leftnormal = faces['l'].normal
          rightnormal = faces['r'].normal
          leftdist = faces['l'].dist
          rightdist = faces['r'].dist
          leftrightlength = abs((leftnormal*leftdist) - (rightnormal*rightdist)) #total length of strech box
          leftrightinterval = wedgeunits
          frontnormal = faces['f'].normal
          backnormal = faces['b'].normal
          frontdist = faces['f'].dist
          backdist = faces['b'].dist
          frontbacklength = abs((frontnormal*frontdist) - (backnormal*backdist)) #total length of strech box
          frontbackinterval = wedgeunits
          wedges = leftrightlength/wedgeunits
          upnormal = faces['u'].normal
          downnormal = faces['d'].normal
          updist = faces['u'].dist
          downdist = faces['d'].dist
          updownlength = abs((upnormal*updist) - (downnormal*downdist))
          updowninterval = updownlength/wedgeunits
          loops = frontbacklength / frontbackinterval

          if loops > 25 or wedges > 25:
              if detailmesh!="1":
                  if replygiven == 1:
                      replygiven = 1
                      return

                  replygiven = 1
                  response = quarkx.msgbox("This Grid will create a lot of polys !\n\nYou can select 'Cancel' and reset\nyour wedgeunits to a larger size\n\nor select 'OK' to continue to\nmake the Grid for detail work", MT_WARNING, MB_OK_CANCEL)

                  quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                  editor = mapeditor()
                  editor.invalidateviews(1)

                  if response == MR_CANCEL:
                      replygiven = 0
                      obj = editor.layout.explorer.uniquesel.parent
                      quarkx.undostate(obj)
                      quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing
                      return

                  if response == MR_OK:
                      replygiven = 1
                      dupObject = o.parent                # new code by Rowdy
                      if dupObject.type == ":d":          # new code by Rowdy
                          dupObject["detailmesh"]="1"       # new code by Rowdy
                      quarkpy.mapeditor.MapEditor.finishdrawing = newfinishdrawing

          for loop in range(int(loops)):   #py2.4
#1st pass of triangles
              for wedge in range(int(wedges)):   #py2.4  #draws back quarter
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()
                  poly.appenditem(face)

                  face = faces['d'].copy()
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['r'].copy()
                  face.shortname = "left"
                  poly.appenditem(face)
                  right = face

                  face = faces['l'].copy()
                  face.shortname = "right"
                  poly.appenditem(face)
                  left = face

                  face = faces['b'].copy()
                  face.translate(backnormal * (frontbackinterval*(-loop)))

                  topleft = points["trf"] + rightnormal * (leftrightinterval * -wedge) + (backnormal * (frontbackinterval*(loops-loop-1)))
                  left.setthreepoints((topleft, points["tlb"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(-loop))), points["blb"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(-loop)))),0)

                  downright = points["trb"] + rightnormal * (leftrightinterval * (-wedge)) + (backnormal * (frontbackinterval*(-loop)))
                  right.setthreepoints((downright, points["tlf"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(loops-loop-1))), points["blf"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(loops-loop-1)))),0)

                  poly.appenditem(face)

                  result.append(poly)
#2nd pass of triangles
              for wedge in range(int(wedges)):   #py2.4  #draws left quarter
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush

                  poly.appenditem(face)

                  face = faces['d'].copy()
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['b'].copy()
                  face.shortname = "left"
                  poly.appenditem(face)
                  back = face

                  face = faces['f'].copy()
                  face.shortname = "right"
                  poly.appenditem(face)
                  front = face

                  face = faces['l'].copy()
                  face.translate(rightnormal * (leftrightinterval * (wedges - wedge - 1)))

                  downback = points["tlb"] + rightnormal * (leftrightinterval * (wedges-wedge-1)) + (backnormal * (frontbackinterval*(-loop)))
                  back.setthreepoints((downback, points["trf"] + rightnormal * leftrightinterval * -wedge + (backnormal * (frontbackinterval*(loops-loop-1))), points["brf"] + rightnormal * leftrightinterval * -wedge + (backnormal * (frontbackinterval*(loops-loop-1)))),0)

                  topfront = points["trb"] + rightnormal * (leftrightinterval * (-wedge)) + (backnormal * (frontbackinterval*(-loop)))
                  front.setthreepoints((topfront, points["tlf"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(loops-loop-1))), points["blf"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(loops-loop-1)))),0)

                  face.shortname = "back"
                  poly.appenditem(face)

                  result.append(poly)
#3rd pass of triangles
              for wedge in range(int(wedges)):   #py2.4  #draws front quarter
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()
                  poly.appenditem(face)

                  face = faces['d'].copy()
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['l'].copy()
                  poly.appenditem(face)
                  right = face

                  face = faces['r'].copy()
                  poly.appenditem(face)
                  left = face

                  face = faces['f'].copy()
                  face.translate(backnormal * (frontbackinterval*(loops-loop-1)))

                  topleft = points["tlb"] + rightnormal * (leftrightinterval * (wedges-wedge-1)) + (backnormal * (frontbackinterval*(-loop)))
                  left.setthreepoints((topleft, points["trf"] + rightnormal * leftrightinterval * -wedge + (backnormal * (frontbackinterval*(loops-loop-1))), points["brf"] + rightnormal * leftrightinterval * -wedge + (backnormal * (frontbackinterval*(loops-loop-1)))),0)

                  downright = points["tlf"] + rightnormal * (leftrightinterval * (wedges-wedge-1)) + (backnormal * (frontbackinterval*(loops-loop-1)))
                  right.setthreepoints((downright, points["trb"] + rightnormal * leftrightinterval * (-wedge) + (backnormal * (frontbackinterval*(-loop))), points["brb"] + rightnormal * leftrightinterval * (-wedge) + (backnormal * (frontbackinterval*(-loop)))),0)
                  face.shortname = "back"
                  poly.appenditem(face)

                  result.append(poly)
#4th pass of triangles
              for wedge in range(int(wedges)):   #py2.4  #draws right quarter
                  poly = quarkx.newobj("terrain wedge %d:p" % wedge)

                  face = faces['u'].copy()  #draws top face at higth of each brush
                  poly.appenditem(face)

                  face = faces['d'].copy()  #draws bottom face of each brush
                  if sameheight!="1":
                      face = face
                  else:
                      face.shortname = "downmoves"
                  poly.appenditem(face)

                  face = faces['f'].copy()  #draws the slice face of each brush
                  face.shortname = "left"
                  poly.appenditem(face)
                  front = face

                  face = faces['b'].copy()  #draws back face of each brush
                  face.shortname = "right"
                  poly.appenditem(face)
                  back = face

                  face = faces['r'].copy()  #draws right face of each brush
                                        # and bases for setting slice points
                  face.translate(rightnormal * (leftrightinterval * -wedge))

                  downback = points["tlf"] + rightnormal * (leftrightinterval * (wedges-wedge-1)) + (backnormal * (frontbackinterval*(loops-loop-1)))
                  back.setthreepoints((downback, points["trb"] + rightnormal * leftrightinterval * (-wedge) + (backnormal * (frontbackinterval*(-loop))), points["brb"] + rightnormal * leftrightinterval * (-wedge) + (backnormal * (frontbackinterval*(-loop)))),0)

                  topfront = points["trf"] + rightnormal * (leftrightinterval * (-wedge)) + (backnormal * (frontbackinterval*(loops-loop-1)))
                  front.setthreepoints((topfront, points["tlb"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(-loop))), points["blb"] + rightnormal * leftrightinterval * (wedges-wedge-1) + (backnormal * (frontbackinterval*(-loop)))),0)
                  face.shortname = "back"
                  poly.appenditem(face)

                  result.append(poly) #part of code, do not take out

          replygiven = 0
          return result

  def buildimages(self, singleimage=None):

      loops = 0
      wedges = 0
      if singleimage is not None and singleimage>0:
          return []
      editor = mapeditor()

      wedges, sameheight, detailmesh = map(lambda spec, self=self: self.dup[spec],
          ("wedgeunits", "sameheight", "detailmesh"))
      list = self.sourcelist()
      for o in list:
          facelist = o.dictitems
          if o.type==":p": # just grab the first one, who cares
              return self.makeTerrain4(loops, wedges, o, int(wedges), sameheight, detailmesh)

quarkpy.mapduplicator.DupCodes.update({"dup terrain4":  TerrainDuplicator4,})

#
#  --- Menus ---
#

def curvemenu4(o, editor, view):

  def maketerrain4(m, o=o, editor=editor):

      dup = quarkx.newobj("Terrain Maker 4:d")
      dup["macro"]="dup terrain4"
      dup["wedgeunits"]="32"
      dup["sameheight"]=""
      dup["detailmesh"]=""
      dup.appenditem(m.newpoly)
      undo=quarkx.action()
      undo.exchange(o, dup)
      editor.ok(undo, "make terrain maker 4")
      editor.invalidateviews()

  disable = (len(o.subitems)!=6)

  newpoly = perspectiveRename(o, view)

  def finishitem4(item, disable=disable, o=o, view=view, newpoly=newpoly):
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

  item = qmenu.item("Make Terrain 4", maketerrain4)
  finishitem4(item)
  return item

#
# First new menus are defined, then swapped in for the old ones.
#  `im_func' returns from a method a function that can be
#   assigned as a value.
#
def newpolymenu2(o, editor, oldmenu=quarkpy.mapentities.PolyhedronType.menu.im_func):
    "the new right-mouse perspective menu for polys"
    #
    # cf FIXME in maphandles.CenterHandle.menu
    #
    try:
        view = editor.layout.clickedview
    except:
        view = None
    return  [curvemenu4(o, editor, view)]+oldmenu(o, editor)

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

quarkpy.mapentities.PolyhedronType.menu = newpolymenu2


def curvemenu2X(o, editor, view):

  def maketerrain2X(m, o=o, editor=editor):

      dup = quarkx.newobj("Terrain Maker 2X:d")
      dup["macro"]="dup terrain2X"
      dup["wedgeunits"]="32"
      dup["sameheight"]=""
      dup["detailmesh"]=""
      dup.appenditem(m.newpoly)
      undo=quarkx.action()
      undo.exchange(o, dup)
      editor.ok(undo, "make terrain maker 2X")
      editor.invalidateviews()

  disable = (len(o.subitems)!=6)

  newpoly = perspectiveRename(o, view)

  def finishitem2X(item, disable=disable, o=o, view=view, newpoly=newpoly):
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

  item = qmenu.item("Make Terrain 2X", maketerrain2X)
  finishitem2X(item)
  return item

def newpolymenu2X(o, editor, oldmenu=quarkpy.mapentities.PolyhedronType.menu.im_func):
    "the new right-mouse perspective menu for polys"
    try:
        view = editor.layout.clickedview
    except:
        view = None
    return  [curvemenu2X(o, editor, view)]+oldmenu(o, editor)


quarkpy.mapentities.PolyhedronType.menu = newpolymenu2X


def curvemenu(o, editor, view):

  def maketerrain2(m, o=o, editor=editor):

      dup = quarkx.newobj("Terrain Maker 2:d")
      dup["macro"]="dup terrain2"
      dup["wedgeunits"]="32"
      dup["sameheight"]=""
      dup["detailmesh"]=""
      dup.appenditem(m.newpoly)
      undo=quarkx.action()
      undo.exchange(o, dup)
      editor.ok(undo, "make terrain maker 2")
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

  item = qmenu.item("Make Terrain 2", maketerrain2)
  finishitem(item)
  return item

def newpolymenu(o, editor, oldmenu=quarkpy.mapentities.PolyhedronType.menu.im_func):
    "the new right-mouse perspective menu for polys"
    try:
        view = editor.layout.clickedview
    except:
        view = None
    return  [curvemenu(o, editor, view)]+oldmenu(o, editor)


quarkpy.mapentities.PolyhedronType.menu = newpolymenu


# ----------- REVISION HISTORY ------------
#$Log: mapterrain.py,v $
#Revision 1.8  2008/04/16 12:39:51  danielpharos
#Added error-fix by TwisteR, and cleaned up a bit of code.
#
#Revision 1.7  2008/02/22 09:52:21  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.6  2006/11/30 01:17:47  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.5  2006/11/29 06:58:35  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.4.2.2  2006/11/09 22:50:38  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.4.2.1  2006/11/01 22:22:42  danielpharos
#BackUp 1 November 2006
#Mainly reduce OpenGL memory leak
#
#Revision 1.4  2005/10/15 00:51:56  cdunde
#To reinstate headers and history
#
#Revision 1.1  2005/08/15 05:49:23  cdunde
#To commit all files for Terrain Generator
#
#
