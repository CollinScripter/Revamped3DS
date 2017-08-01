# QuArK -- Quake Army Knife
# Copyright (C) 1999-2005 tiglari, Peter Brett
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#$Header: /cvsroot/quark/runtime/plugins/tagging.py,v 1.12 2006/11/30 01:17:47 cdunde Exp $

import quarkx
import quarkpy.qbaseeditor
from quarkpy.maputils import *
from quarkpy import tagging as nt
from plugins.mapgeomtags import *

#py2.4 indicates upgrade change for python 2.4

"""
plugins.tagging
---------------

  DEPRECATED.  New plugins should use the quarkpy.tagging module with
  keys defined in plugins.mapgeomtags.  This module will disappear
  soon(tm).

Emulation of old-style tagging API.  Code which uses this should
be phased out ASAP.
"""

Info = {
   "plug-in":       "Legacy map geometry tagging",
   "desc":          "Provides old-style functions for user tagging of map geometry",
   "date":          "2005-09-21",
   "author":        "peter-b",
   "author e-mail": "peter@peter-b.co.uk",
   "quark":         "6.5 or later" }


#
# This is the oldest and first - it should be phased out
#   in favor of gettaggedface below
#
def gettagged(editor):
    "safe fetch of tagging.tagged attribute"
    # According to this module, this should return a face, if only
    # one face is tagged.
    faces = gettaggedfaces(editor)
    if len(faces) == 1:
      return faces[0]
    else:
      return None

def gettaggedplane(editor):
    tagged = gettagged(editor)
    if tagged is not None:
        return tagged
    plane = nt.getuniquetag(editor, PLANE)
    if plane is not None:
        face = quarkx.newobj("tagged:f")
        face.setthreepoints(plane,0)
        return face
    return None
  
  
def gettaggedpt(editor):
  "Returns the tagged point."
  return nt.getuniquetag(editor, POINT)

def gettaggedlist(editor):
  "Returns a list of tagged faces"
  # This is daft. The original version of this returned None if
  # one or fewer faces were tagged. WTF?
  faces = gettaggedfaces(editor)
  if len(faces) > 1:
    return faces
  return None
  
def gettaggedfaces(editor):
  "tagged face or faces"
  faces = nt.gettaglist(editor, FACE)

  # Check the tagged faces actually exist in the map
  for f in faces:
    if not checktree(editor.Root, f):
      nt.untag(editor, FACE, f)
      
  return nt.gettaglist(editor, FACE)

#
# 2-point edges only
#
def gettaggedvtxedge(editor):
  return nt.getuniquetag(editor, VTXEDGE)

#
# face edges
#
def gettaggedfaceedge(editor):
  return nt.getuniquetag(editor, FACEEDGE)

#
# both kinds
#
def gettaggededge(editor):
  " safe fetch of tagging.taggededge attribute"
  tagged = gettaggedfaceedge(editor)
  if tagged is not None:
    return (tagged.vtx1, tagged.vtx2)
  return gettaggedvtxedge(editor)

#
# This is the new one, it picks up either ordinary tagged
#  faces or faces tagged via tagging of edge-handles
#
def gettaggedface(editor):
    tagged = gettagged(editor)
    if tagged is not None:
      return tagged
    tagged = gettaggedfaceedge(editor)
    if tagged is not None:
      return tagged.face
    return None


#
# Maybe this one shouldn't be here, but in quarkpy.mapbezier.py
#
def gettaggedb2cp(editor):
  return nt.getuniquetag(editor, B2CP)

def anytag(o):
  "Is anything tagged ?"
  return gettagged(o) is not None or gettaggedpt(o) is not None or gettaggedlist(o) is not None

def gettaggedtexplane(editor):
    "returns an actual tagged face, or an abstract one"
    plane = gettaggedface(editor)
    if plane is not None:
        return plane
    b2cp = gettaggedb2cp(editor)
    if b2cp is not None:
        return quarkpy.b2utils.texPlaneFromCph(b2cp, editor)
    

#
# --------- setting & clearing tags
#

def cleartag(editor):
  nt.cleartags(editor, PLANE, POINT, FACE, FACEEDGE,
               VTXEDGE, B2CP)
  
def tagface(face, editor):
  cleartag(editor)
  nt.uniquetag(editor, FACE, face)
  
def tagplane(plane, editor):
  cleartag(editor)
  nt.uniquetag(editor, PLANE, plane)

def tagpoint(point, editor):
  cleartag(editor)
  nt.uniquetag(editor, POINT, point)

def tagedge(p1, p2, editor):
  cleartag(editor)
  nt.uniquetag(editor, VTXEDGE, (p1, p2))

def tagfaceedge(edge, editor):
  cleartag(editor)
  nt.uniquetag(editor, FACEEDGE, edge)

#
# Maybe this one shouldn't be here, but in quarkpy.mapbezier.py
#
def tagb2cp(cp, editor):
    tagpoint(cp.pos, editor)
    nt.uniquetag(editor, B2CP, cp)

def addtotaggedfaces(face, editor):
  tagged = gettagged(editor)
  if (tagged is not None) or (gettaggedfaces(editor) is not None):
    nt.tag(editor, FACE, face)
  
def removefromtaggedfaces(face, editor):
  nt.untag(editor, FACE, face)


#
# -------- map drawing routines --------
# These have got to stay the same, they're used elsewhere (WTF?)

def drawsquare(cv, o, side):
  "function to draw a square around o"
  if o.visible:
    dl = side/2
    dl = int(dl)  #py2.4
    cv.brushstyle = BS_CLEAR
#py2.4    cv.rectangle(o.x+dl, o.y+dl, o.x-dl, o.y-dl)
    cv.rectangle(int(o.x)+dl, int(o.y)+dl, int(o.x)-dl, int(o.y)-dl)

def drawredface(view, cv, face):
    for vtx in face.vertices: # is a list of lists
      sum = quarkx.vect(0, 0, 0)
      p2 = view.proj(vtx[-1])  # the last one
      for v in vtx:
        p1 = p2
        p2 = view.proj(v)
        sum = sum + p2
        cv.line(p1,p2)
      drawsquare(cv, sum/len(vtx), 8)


# ----------- REVISION HISTORY ------------
#$Log: tagging.py,v $
#Revision 1.12  2006/11/30 01:17:47  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.11  2006/11/29 06:58:35  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.10.2.1  2006/11/03 23:38:11  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.10  2005/11/10 18:09:03  cdunde
#Activate history log
#
#
