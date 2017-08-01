# QuArK  -  Quake Army Knife
#
# Copyright (C) 2001 The Quark Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/mapradial.py,v 1.8 2005/10/15 00:51:24 cdunde Exp $

Info = {
   "plug-in":       "Radial Duplicator",
   "desc":          "Replicate objects around an axis",
   "date":          "03 Mar 2001",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Quark 6.2" }


from quarkpy.maputils import *
from quarkpy.qdictionnary import Strings
import quarkpy.qhandles
import quarkpy.mapduplicator
import quarkpy.maphandles
StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator
DuplicatorManager = quarkpy.mapduplicator.DuplicatorManager
from quarkpy.maphandles import MapRotateHandle


class AxisHandle(MapRotateHandle):
  "a rotating handle that controls a normalized vector spec"

  def __init__(self, center, dup, spec, scale1):
      axis = quarkx.vect(dup[spec])
      MapRotateHandle.__init__(self, center, axis, scale1, quarkpy.qhandles.mapicons[11])
      self.dup = dup
      self.spec = spec

  def dragop(self, flags, av):
        new = None
        if av is not None:
            new = self.dup.copy()
            new[self.spec] = av.tuple
        return [self.dup], [new], av

def macro_dup_radial_align(self, index=0):
    editor=mapeditor()
    if editor is None:
        return
    sel = editor.layout.explorer.sellist
    #  if len(sel)!=1: return
    dup = sel[0]
    undo = quarkx.action()
    if index==1:
        undo.setspec(dup,"axis",'1 0 0')
    elif index==2:
        undo.setspec(dup,"axis",'0 1 0')
    else:
        undo.setspec(dup,"axis",'0 0 1')
    editor.ok(undo, "move axis")
    editor.invalidateviews()

quarkpy.qmacro.MACRO_dup_radial_align = macro_dup_radial_align

class RadialDuplicator(StandardDuplicator):
    "Radial Duplicator."

    def handles(self, editor, view):
        scale = view.scale()
        dup = self.dup
        org = dup.origin
        h = [AxisHandle(org, dup, "axis", scale)]
        return h + DuplicatorManager.handles(self, editor, view)


    def buildimages(self, singleimage=None):
        if singleimage is not None and singleimage>0:
            return []
        axis = quarkx.vect(self.dup["axis"]).normalized
        around, = self.dup["around"]
        spiral = self.dup["spiral"]
        if spiral is not None:
            upward, outward = spiral
        else:
            upward, outward = 0, 0
        origin = self.dup.origin
        list = self.sourcelist()
        templateorigin = quarkpy.maphandles.GetUserCenter(list)
        #
        # Axis can be tilted
        #
        tiltmat = matrix_rot_u2v(quarkx.vect(0,0,1),axis)
        result = []
        try:
            count = int(self.dup["count"])
        except:
            count = 1
        #
        # A linear matrix can apply cumulatively to the images
        #
#        dupmat = buildLinearMatrix(self.dup)

        if self.dup["linear"] is not None:
            dupmat = self.dup["linear"]
        else:
           dupmat = '1 0 0 0 1 0 0 0 1'
        dupmat = quarkx.matrix(dupmat)
        cummat = quarkx.matrix('1 0 0 0 1 0 0 0 1')
        try:
            for i in range(0, count):
                group=quarkx.newobj('radial %d:g'%i)
                for item in list:
                    group.appenditem(item.copy())
                result.append(group)
                group.linear(templateorigin,cummat)
                cummat = dupmat*cummat
                angle = i*around*deg2rad
                matrix = tiltmat*matrix_rot_z(angle)
                shift = upward*axis*i
                group.linear(origin,matrix)
                group.translate(shift)
                center=quarkpy.maphandles.GetUserCenter(group)
                radvec = perptonormthru(origin,center,axis).normalized
                radvec = matrix*radvec
                shift = -i*outward*radvec
                group.translate(shift)
        except:
            # Catch math-computation errors and return nothing if so
            result = []

        return result

#
# Register the duplicator type from this plug-in.
#

quarkpy.mapduplicator.DupCodes.update({
  "dup radial":     RadialDuplicator,
})

# ----------- REVISION HISTORY ------------
#$Log: mapradial.py,v $
#Revision 1.8  2005/10/15 00:51:24  cdunde
#To reinstate headers and history
#
#Revision 1.5  2001/08/15 17:52:01  decker_dk
#Exception-catch for math-computation errors
#
