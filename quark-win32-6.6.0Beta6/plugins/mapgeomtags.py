# QuArK -- Quake Army Knife
# Copyright (C) 2005 Peter Brett
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

# $Header: /cvsroot/quark/runtime/plugins/mapgeomtags.py,v 1.8 2006/11/30 01:17:48 cdunde Exp $

"""
plugins.mapgeomtags
-------------------

Provides tag keys for various map geometry types, and sets up
highlighting callbacks.

  FACE:     Faces
  PLANE:    Planes
  POINT:    Points
  VTXEDGE:  Edges defined by two vertexes
  FACEEDGE: Edges of a face
  B2CP:     Bezier patches

The tag keys above are the only members of this module that should be
accessed by other code.
"""

Info = {
   "plug-in":       "Map geometry tagging",
   "desc":          "Provides tag keys and drawing callbacks for user tagging of map geometry",
   "date":          "2005-09-21",
   "author":        "peter-b",
   "author e-mail": "peter@peter-b.co.uk",
   "quark":         "6.5 or later" }
    
__all__ = ['FACE', 'PLANE', 'POINT', 'VTXEDGE', 'FACEEDGE', 'B2CP']

import quarkx
from quarkpy.maputils import checktree, BS_CLEAR
from quarkpy.qeditor import mapeditor
import quarkpy.tagging as nt

#py2.4 indicates upgrade change for python 2.4

# -- Geometry tag keys --------------------------------------------- #
#   ===================

FACE = 'mapgeomtags_face'
PLANE = 'mapgeomtags_plane'
POINT = 'mapgeomtags_point'
VTXEDGE = 'mapgeomtags_vtxedge'
FACEEDGE = 'mapgeomtags_faceedge'
B2CP = 'mapgeomtags_b2cp'

# -- Checking that items are the right type ------------------------ #
#   ========================================

# Callback for validating tagged POINTs
def _POINT_ccb(editor, key, tagged, untagged):
  for o in tagged:
    if not isinstance(o, quarkx.vector_type):
      raise TypeError("Tagged points must be of type quarkx.vector_type")

nt.tagchangefunc(POINT, _POINT_ccb)

# -- Drawing tagged items ------------------------------------------ #
#   ======================

# FIXME These next two shouldn't really be in this plugin
def _drawsquare(cv, o, side):
  "function to draw a square around o"
  if o.visible:
    dl = side/2
    cv.brushstyle = BS_CLEAR
#py2.4    cv.rectangle(o.x+dl, o.y+dl, o.x-dl, o.y-dl)
    cv.rectangle(int(o.x)+dl, int(o.y)+dl, int(o.x)-dl, int(o.y)-dl)

def _drawhighlightface(view, cv, face):
    for vtx in face.vertices: # is a list of lists
      sum = quarkx.vect(0, 0, 0)
      p2 = view.proj(vtx[-1])  # the last one
      for v in vtx:
        p1 = p2
        p2 = view.proj(v)
        sum = sum + p2
        cv.line(p1,p2)
      _drawsquare(cv, sum/len(vtx), 8)


# Draw CallBack functions for drawing tags

def _FACE_dcb(e,v,cv,face):
    if checktree(e.Root, face):
        _drawhighlightface(v,cv,face)
    else:
        nt.cleartags(e, FACE)

def _FACEEDGE_dcb(e,v,cv,obj):
  p1, p2 = v.proj(obj.vtx1), v.proj(obj.vtx2)
  p = (p1+p2)/2
  radius = 2
  oldwidth = cv.penwidth
  cv.penwidth = 3
  cv.ellipse(p.x-radius, p.y-radius, p.x+radius+1, p.y+radius+1)
  cv.penwidth=2
  cv.line(p1, p2)
  cv.penwidth = oldwidth

def _POINT_dcb(e,v,cv,obj):
  _drawsquare(cv, v.proj(obj), 8)

def _VTXEDGE_dcb(e,v,cv,obj):
  pt1, pt2 = obj
  p1 = v.proj(pt1)
  p2 = v.proj(pt2)
  cv.line(p1,p2)
  _drawsquare(cv, (p1+p2)/2, 8)

def _PLANE_dcb(e,v,cv,obj):
  p1, p2, p3 = obj
  center = (p1+p2+p3)/3.0
  center = v.proj(center)
  for pt in (p1, p2, p3):
    pt = v.proj(pt)
    cv.line(center,pt)

def _B2CP_dcb(e,v,cv,obj):
    _POINT_dcb(e,v,cv,obj.pos)
        
nt.tagdrawfunc(_FACE_dcb, FACE)
nt.tagdrawfunc(_FACEEDGE_dcb, FACEEDGE)
nt.tagdrawfunc(_POINT_dcb, POINT)
nt.tagdrawfunc(_VTXEDGE_dcb, VTXEDGE)
nt.tagdrawfunc(_PLANE_dcb, PLANE)
nt.tagdrawfunc(_B2CP_dcb, B2CP)

# ------------------------------------------------------------------ #
# log - make no changes below this line
#
# $Log: mapgeomtags.py,v $
# Revision 1.8  2006/11/30 01:17:48  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.7  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.6.2.1  2006/11/03 23:38:11  cdunde
# Updates to accept Python 2.4.4 by eliminating the
# Depreciation warning messages in the console.
#
# Revision 1.6  2005/10/16 18:48:04  cdunde
# To remove letters referring to depository folders that
#  made filtering them out for distribution harder to do
#
# Revision 1.5  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.2  2005/09/22 11:10:40  peter-b
# Resolve merge conflicts
#
# Revision 1.1.2.3  2005/09/22 10:41:27  peter-b
# Change order of arguments to tagdrawfunc() to match tagchangefunc()
#
# Revision 1.1.2.2  2005/09/22 10:32:11  peter-b
# Check type of tagged points (using tag change callback)
#
# Revision 1.1.2.1  2005/09/21 18:30:14  peter-b
# New mapgeomtags plugin provides infrastructure for tagging map geometry.
# Deprecated tagging plugin now uses mapgeomtags to do its thing.
#
