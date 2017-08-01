"""   QuArK  -  Quake Army Knife Bezier shape makers


"""


# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

########################################################
#
#                          Curves Plugin
#                          v1.0, May 2000
#                      works with Quark 6.0b2
#
#
#                    by tiglari@hexenworld.com
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & improvements to tiglari@hexenworld.com
#
###
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/mb2curves.py,v 1.34 2005/10/15 00:51:56 cdunde Exp $


Info = {
   "plug-in":       "Curves plugin",
   "desc":          "Making curves from brushes, etc.",
   "date":          "1 May 2000",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Version 6.0b2" }


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

#############################
#
#  MAJOR SECTIONS
#
#  - image builders: implementation of buildimages for the
#      shape-builders
#
#  - duplicators: the duplicator code
#
#  - menus
#
# -- Image builders
#
#    many of these below should probably be stuck inside
#    the appropriate cap/bevel/columnImages method
#

def makearchfacecp(bl, tl, tr, br):
    mid = (tl+tr)/2.0
    cp = [[bl, tl, mid, tr, br],
          [(bl+tl)/2.0, tl, mid, tr, (br+tr)/2.0],
          [tl, (tl+mid)/2.0, mid, (mid+tr)/2.0, tr]]
    return cp

def makecapfacecp(bl, tl, tr, br):
    bm = (bl+br)/2.0
    tm = (tl+tr)/2.0
    cp = [[bl, (bl+bm)/2.0, bm, (bm+br)/2.0, br],
          [bl, (bl+bm)/2.0, (tm+bm)/2.0, (bm+br)/2.0, br],
          [bl, tl, tm, tr, br]]
    return cp


def smallerarchbox(box, thick):
    "returns a box for arch, thick smaller than input box"
    fi = thick*(box["brf"]-box["blf"]).normalized
    bi = thick*(box["brb"]-box["blb"]).normalized
    fd = thick*(box["brf"]-box["trf"]).normalized
    bd = thick*(box["brb"]-box["trb"]).normalized
    box2 = {}
    for (corner, delta) in (("blf",fi), ("blb",bi),
            ("tlf",fi+fd), ("tlb",fi+bd), ("trf",fd-fi), ("trb",bd-bi),
            ("brf",-fi), ("brb",-bi)):
        box2[corner]=box[corner]+delta
    return box2

def smallerbevelbox(box, thick):
    "returns a box for bevel, thick smaller than input box"
    def gap(goal, source, box=box, thick=thick):
        return thick*(box[goal]-box[source]).normalized
    rf = gap("tlf", "trf")
    rb = gap("tlb", "trb")
    lb = gap("tlf", "tlb")
    zip = quarkx.vect(0,0,0)
    box2 = {}
    for (corner, delta) in (("blf",zip), ("blb",lb),
            ("tlf",zip), ("tlb",lb), ("trf",rf), ("trb",rb+lb),
            ("brf",rf), ("brb",rb+lb)):
        box2[corner]=box[corner]+delta
    return box2

def smallercolumnbox(box, thick):
    "returns a box for cp;i,m, thick smaller than input box"
    def gap(goal, source, box=box, thick=thick):
        return thick*(box[goal]-box[source]).normalized
    f = gap("tlf", "trf")
    b = gap("tlb", "trb")
    l = gap("tlf", "tlb")
    r = gap("trf", "trb")
    box2 = {}
    for (corner, delta) in (
          ("tlf",-f-l), ("blf",-f-l),
          ("tlb",-b+l), ("blb",-b+l),
          ("trf",f-r), ("brf",f-r),
          ("trb",b+r), ("brb",b+r)):
        box2[corner]=box[corner]+delta
    return box2


def archline(pd, a, b, c, d):
    "returns 5-tuple with middle halfway between b and c"
    return [pd[a], pd[b], (pd[b]+pd[c])/2, pd[c], pd[d]]


def archcurve(pd):
    cp = cpFrom2Rows(archline(pd, "blf", "tlf", "trf", "brf"),
                      archline(pd, "blb", "tlb", "trb", "brb"))
    return cp


def capImages(o, editor, inverse=0, lower=0, onside=0, open=0, thick=0, faceonly=0,
    stretchtex=0, nofront=0, noback=0, noinner=0, noouter=0, (subdivide,)=1):
  "makes a 'cap' (or arch) on the basis of brush o"
  #
  # Make dictionary of faces u/d/f/b/r/l
  #
  o.rebuildall()
  fdict = faceDict(o)
  if fdict is None:
    return
  #
  # make dictionary of points, 'bottom left front' etc.
  # this one's name is short because we refer to it so often
  #
  if onside:
      fdict = facedict_rflip(facedict_rflip(facedict_rflip(fdict)))
  pd = pointdict(vtxlistdict(fdict,o))
  if lower:
      pd = pointdict_vflip(pd)
      pd = pointdict_hflip(pd)
      texface = fdict["d"].copy()
  else:
      texface = fdict["u"].copy()
  #
  # make the basic inner curved face, a 3x5 quilt
  #
  cp = archcurve(pd)
  #
  # project cps from face to patch (flat projection, distorted)
  #
  cp = texcpFromFace(cp, texface, editor)
  #
  # adjust down sides if wanted
  #
  if not stretchtex:
      if lower:
        right, left = fdict["l"], fdict["r"]
      else:
        right, left = fdict["r"], fdict["l"]
      #
      # For the right and left sides of the guide brush ...
      #
      for side, fulcrum, edge in ((right, "trf", 4), (left, "tlf", 0)):
          #
          #  make a copy of the 'top' (where the texture is being
          #   taken from)
          #
          newside = texface.copy()
          #
          # rotate around the front side corner, so that it is coincident
          #  with the side
          #
          newside.distortion(side.normal, pd[fulcrum])
          #
          # a copy of the patch's control-points with the rotated
          #  face's texture projected onto it (would look good at
          #  one end, terrible at the other)
          #
          cp2 = texcpFromFace(cp, newside, editor)
          #
          # Now set the real patch control points along the edge to
          #  the new ones.
          #
          for index in range(3):
              cp[index][edge]=cp2[index][edge]
  #
  # We have now set the cp's for both edges of the patch correctly,
  #  so we smooth things out
  #
  cp = undistortRows(cp)
  cp = undistortColumns(cp)
  inner = quarkx.newobj('inner:b2')
  cp = subdivideRows(subdivide,cp)
  inner.cp = cp
  inner["tex"] = texface["tex"]
  if thick:
      pd2 = smallerarchbox(pd, thick)
      cp2 = archcurve(pd2)
      cp2 = subdivideRows(subdivide,cp2)
      inner.shortname = "outer"
      inner2=quarkx.newobj("inner:b2")
      cp2 = texcpFromCp(cp2, cp)
      inner2.cp = cp2
      inner2["tex"] = inner["tex"]
      #
      # seams
      #
      seams = []
      if not open:
          if not nofront:
              fseam = b2From2Rows(archline(pd, "brf", "trf", "tlf", "blf"),
                           archline(pd2,"brf", "trf", "tlf", "blf"),
                          fdict["f"], "front")
              fseam.cp = subdivideRows(subdivide,fseam.cp)
              seams.append(fseam)
          if not noback:
              bseam = b2From2Rows(archline(pd, "blb", "tlb", "trb", "brb"),
                           archline(pd2,"blb", "tlb", "trb", "brb"),
                           fdict["b"], "back")
              bseam.cp = subdivideRows(subdivide,bseam.cp)
              seams.append(bseam)
      if lower:
        inner.swapsides()
        bseam.swapsides()
        fseam.swapsides()
      else:
        inner2.swapsides()
      inners = []
      if not faceonly:
          if not noouter:
              inners.append(inner)
          if not noinner:
              inners.append(inner2)
      return inners + seams
  # end if thick

#  if lower:
 #     inner.swapsides()
  if inverse:
     inner.swapsides()
  if open:
      return [inner]
  if inverse:
     fcp = makearchfacecp(pd["blf"],pd["tlf"],pd["trf"],pd["brf"])
     bcp = makearchfacecp(pd["blb"],pd["tlb"],pd["trb"],pd["brb"])
  else:
     fcp = makecapfacecp(pd["blf"],pd["tlf"],pd["trf"],pd["brf"])
     bcp = makecapfacecp(pd["blb"],pd["tlb"],pd["trb"],pd["brb"])
#  if lower:
#      fcp = transposeCp(fcp)
#  else:
  if subdivide>1:
      if not nofront:
          fcp = subdivideRows(subdivide, fcp)
      if not noback:
          bcp = subdivideRows(subdivide, bcp)
  bcp = transposeCp(bcp)
  faces = []
  if not nofront:
      front = b2FromCpFace(fcp, 'front', fdict["f"], editor)
      faces.append(front)
  if not noback:
      back = b2FromCpFace(bcp,'back', fdict["b"], editor)
      faces.append(back)
  if faceonly:
      return faces
  return [inner]+faces


def bevelImages(o, editor, inverse=0, lower=0, left=0, standup=0, open=0, thick=0,
  faceonly=0, stretchtex=0, notop=0, nobottom=0, noinner=0, noouter=0, (subdivide,)=1):
  "makes a bevel/inverse bevel on the basis of brush o"
  o.rebuildall()
  #
  # make a dictionary where faces are indexed by the first letter
  # of their name (front|back|left|right|up|down)
  #
  fdict = faceDict(o)
  if fdict is None:
    return
  if standup:
      fdict = facedict_rflip(fdict)
  if lower:
      fdict = facedict_fflip(fdict)
  #
  # get a dict of the vertices indexed by [t|b][r|l][f|b]
  #
  pd = pointdict(vtxlistdict(fdict,o))
  #
  # interchange left and right vertices for left bevel
  #
  if left:
      pd = pointdict_hflip(pd)
  #
  # make patch controlpoints, rows starting at the back, curving
  #  towards front (for regular and left versions).  For left bevels,
  #  'l' vertices will be right and vice versa
  #
  def bevelcurve(pd):
#      return cpFrom2Rows(subdivideLine(2, pd["tlb"], pd["trb"],pd["trf"]),
#                         subdivideLine(2, pd["blb"],pd["brb"],pd["brf"]))
      return cpFrom2Rows([pd["tlb"], pd["trb"],pd["trf"]],
                         [pd["blb"],pd["brb"],pd["brf"]])
  cp = bevelcurve(pd)
  inner = quarkx.newobj('inner:b2')
  #
  # project the texture from the back face onto the patch
  #
  cp = texcpFromFace(cp, fdict["b"], editor)
  if not stretchtex:
      newside = fdict["b"].copy()
      #
      # fdict has not been flipped for left brushes
      #
      if left:
          newside.distortion(fdict["l"].normal,pd["trb"])
      else:
          newside.distortion(fdict["r"].normal,pd["trb"])
      cp2 = texcpFromFace(cp, newside, editor)
      debug("cp: ")
      writecps(cp)
#      debug("cp2: ")
#      writecps(cp2)
      for index in range(3):
        cp[index][2]=cp2[index][2]

  cp = undistortRows(cp)
  cp = undistortColumns(cp)
  cp = subdivideRows(subdivide,cp)
  inner.cp = cp
  inner["tex"] = fdict["b"]["tex"]
  if thick:
      inner.shortname="outer"
      pd2 = smallerbevelbox(pd, thick)
      cp2 = bevelcurve(pd2)
      inner2=quarkx.newobj("inner:b2")
      inner2.cp = texcpFromCp(subdivideRows(subdivide,cp2), cp)
      inner2["tex"]=inner["tex"]
      tseam = b2From2Rows([pd["trf"], pd["trb"], pd["tlb"]],
                       [pd2["trf"], pd2["trb"], pd2["tlb"]],
                        fdict["u"],"top")
      bseam = b2From2Rows([pd["blb"], pd["brb"], pd["brf"]],
                       [pd2["blb"], pd2["brb"], pd2["brf"]],
                        fdict["d"],"bottom")
      tseam.cp = subdivideRows(subdivide, tseam.cp)
      bseam.cp = subdivideRows(subdivide, bseam.cp)
      if left:
          inner.swapsides()
          tseam.swapsides()
          bseam.swapsides()
      else:
          inner2.swapsides()
      if lower:
          inner.swapsides()
          inner2.swapsides()
          tseam.swapsides()
          bseam.swapsides()
      seams = [tseam, bseam]
      if notop:
          seams.remove(tseam)
      if nobottom:
          seams.remove(bseam)
      if faceonly:
         return seams
      inners = [inner, inner2]
      if noinner:
          inners.remove(inner2)
      if noouter:
          inners.remove(inner)
      return inners+seams
  if left:
    inner.swapsides()
  if inverse:
    inner.swapsides()
  if lower:
     inner.swapsides()
  if open:
      return [inner]
  if inverse:
      tcp = cpFrom2Rows([pd["tlb"], pd["trb"], pd["trf"]],
                         [pd["trb"], pd["trb"], pd["trf"]])
      bcp = cpFrom2Rows([pd["brf"], pd["brb"], pd["blb"]],
                         [pd["brf"], pd["brb"], pd["brb"]])
  else:
      tcp = subdivideRows(subdivide,cpFrom2Rows([pd["trf"], pd["trb"], pd["tlb"]],
                         [pd["tlf"], pd["tlf"], pd["tlb"]]))
      bcp = subdivideRows(subdivide,cpFrom2Rows([pd["blb"], pd["brb"], pd["brf"]],
                         [pd["blb"], pd["blf"], pd["blf"]]))
  top = b2FromCpFace(tcp,"top",fdict["u"],editor)
  bottom = b2FromCpFace(bcp,"bottom",fdict["d"],editor)
  if left:
    top.swapsides()
    bottom.swapsides()
  if lower:
    top.swapsides()
    bottom.swapsides()
  faces = [bottom, top]
  if notop:
      faces.remove(top)
  if nobottom:
      faces.remove(bottom)
  if faceonly:
    return faces
  return [inner] + faces


def circleLine(p0, p1, p2, p3):
    return [(p0+p1)/2, p1, (p1+p2)/2, p2, (p2+p3)/2, p3,
            (p3+p0)/2, p0, (p0+p1)/2]

def columnImages(o, editor, inverse=0, open=0, thick=0, stretchtex=0, bulge=(.5,1),
      funnel=None, faceonly=0, notop=0, nobottom=0, noinner=0, noouter=0, circle=0, (subdivide,)=1):
    "makes a column on the basis of brush o"
    if circle:
        subfunc=arcSubdivideLine
    else:
        subfunc=None
    o.rebuildall()
    fdict = faceDict(o)
    if fdict is None:
        return
    pdo = pointdict(vtxlistdict(fdict,o))

    if funnel is not None:

        def warpbox(pd, pdo=pdo,funnel=funnel):
            pd2 = {}
            for (i, p0, p1, p2, p3) in ((0, "tlf", "tlb", "trb", "trf"),
                                        (1, "blf", "blb", "brb", "brf")):
                c = (pd[p0]+pd[p1]+pd[p2]+pd[p3])/4.0
                for p in (p0, p1, p2, p3):
                    pd2[p] = c+funnel[i]*(pd[p]-c)
            return pd2

        pd = warpbox(pdo)
    else:
        pd = pdo


    def curveCp(pd, bulge=bulge):
        cp = cpFrom2Rows(circleLine(pd["trf"], pd["tlf"], pd["tlb"], pd["trb"]),
                        circleLine(pd["brf"], pd["blf"], pd["blb"], pd["brb"]),bulge)
        return cp

    cp = curveCp(pd)

    def makeTube (cp, pd, oldface, pdo=pdo, fdict=fdict, stretchtex=stretchtex, subfunc=subfunc, subdivide=subdivide,editor=editor):
        cp2 = interpolateGrid(pdo["tlb"], pdo["trb"], pdo["blb"], pdo["brb"], 3, 9)
        cp2 = texcpFromFace(cp2, oldface, editor)
        cp = texcpFromCp(cp, cp2)
        if subdivide>1:
            cp = subdivideRows(subdivide,cp,subfunc)
        if not stretchtex:
            for (facekey, corner) in (("r", "trb"),("f", "trf"),("l","tlf")):
                newface=oldface.copy()
                newface.setthreepoints(oldface.threepoints(2),2)
                newface.distortion(fdict[facekey].normal,pdo[corner])
                oldface = newface
            cp3 = interpolateGrid(pdo["tlf"], pdo["tlb"], pdo["blf"], pdo["blb"])
            cp3 = texcpFromFace(cp3, oldface, editor)
            for i in range(3):
                cp[i][8] = quarkx.vect(cp[i][8].xyz+cp3[i][2].st)
#    squawk(`cp`)
        cp = undistortRows(cp)
        inner = quarkx.newobj("inner:b2")
        inner.cp = cp
        inner["tex"]=oldface["tex"]
        return inner

    inner = makeTube(cp, pd, fdict["b"])
    if thick:
        pd2 = smallercolumnbox(pd, thick)
        cp2 = curveCp(pd2)
        inner2 = makeTube(cp2, pd2, fdict["f"])
        inner2.shortname="inner"
        inner.shortname="outer"
        tcp = cpFrom2Rows(cp[0],cp2[0])
        bcp = cpFrom2Rows(cp[2], cp2[2])
        if subdivide>1:
            tcp = subdivideRows(subdivide,tcp, subfunc)
            bcp = subdivideRows(subdivide,bcp, subfunc)
        top = b2FromCpFace(tcp,"top",fdict["u"],editor)
        top.swapsides()
        bottom = b2FromCpFace(bcp,"bottom",fdict["d"],editor)
        inner2.swapsides()
        seams = [top, bottom]
        if notop:
            seams.remove(top)
        if nobottom:
            seams.remove(bottom)
        if faceonly:
           return seams
        inners = [inner, inner2]
        if noinner:
            inners.remove(inner2)
        if noouter:
            inners.remove(inner)
        return inners+seams

    if open:
       if inverse:
          inner.swapsides()
       return [inner]


    if inverse:

        def squareFromCircle(row): # row = 9 pts, cp's for circle
            # first not used, passed to reduce index confusion
            def halfSquare(hr): # hr=half-row excluding center
                return [hr[1], hr[1], hr[2], hr[3], hr[3]]

            return halfSquare(row[:4]), halfSquare(row[4:8])

        def faces(circline, borderfunc, name, texface, subdivide=subdivide,subfunc=subfunc):
            out0, out1 = borderfunc(circline)
            b2a = b2From2Rows(out0, circline[0:5],texface,name+'0',subdivide=subdivide,subfunc=subfunc)
            b2b = b2From2Rows(out1, circline[4:9],texface,name+'1',subdivide=subdivide,subfunc=subfunc)
            return b2a, b2b

        topa, topb = faces(cp[0],squareFromCircle,'top',fdict['u'])
        inner.swapsides()
        topa.swapsides()
        topb.swapsides()
        bottoma, bottomb = faces(cp[2],squareFromCircle,'bottom',fdict['d'])
        result = [inner, topa, topb, bottoma, bottomb]
        if faceonly:
            result.remove(inner)
        if notop:
            result.remove(topa)
            result.remove(topb)
        if nobottom:
            result.remove(bottoma)
            result.remove(bottomb)
    else:
        def center(v):
            c = (v[1]+v[3]+v[5]+v[7])/4.0
            return map(lambda x,c=c:c,range(9))

        top = b2From2Rows(center(cp[0]),cp[0],fdict['u'],'top',subdivide=subdivide,subfunc=subfunc)
        bottom = b2From2Rows(cp[2], center(cp[2]),fdict['d'],'bottom',subdivide=subdivide,subfunc=subfunc)
        result = [inner, top, bottom]
        if faceonly:
            result.remove(inner)
        if notop:
            result.remove(top)
        if nobottom:
            result.remove(bottom)

    return result


def images(buildfn, args):
    if quarkx.setupsubset(SS_MAP, "Options")["Developer"]:
        return apply(buildfn, args)
    else:
        try:
            return apply(buildfn, args)
        except:
            return []

#
#  --- Duplicators ---
#

class CapDuplicator(StandardDuplicator):

  def buildimages(self, singleimage=None):
    if singleimage is not None and singleimage>0:
      return []
    editor = mapeditor()
    inverse, lower, onside, open, thick, faceonly, stretchtex, nofront, noback, noinner, noouter, subdivide = map(lambda spec,self=self:self.dup[spec],
      ("inverse", "lower", "onside", "open", "thick", "faceonly", "stretchtex",
         "nofront", "noback", "noinner", "noouter", "subdivide"))
    if thick:
      thick, = thick
    if subdivide is None:
        subdivide=1,
    list = self.sourcelist()
    for o in list:
      if o.type==":p": # just grab the first one, who cares
         return images(capImages, (o, editor, inverse, lower, onside, open, thick,
           faceonly, stretchtex, nofront, noback, noinner, noouter, subdivide))


class BevelDuplicator(StandardDuplicator):

  def buildimages(self, singleimage=None):
    if singleimage is not None and singleimage>0:
      return []
    editor = mapeditor()
    inverse, lower, left, standup, sidetex, open, thick, faceonly, stretchtex, notop, nobottom, noinner, noouter, subdivide = map(lambda spec,self=self:self.dup[spec],
      ("inverse", "lower", "left", "standup", "sidetex", "open", "thick", "faceonly", "stretchtex",
         "notop", "nobottom", "noinner", "noouter", "subdivide"))
    if thick:
      thick, = thick
    list = self.sourcelist()
    if subdivide is None:
        subdivide=1,
    for o in list:
      if o.type==":p": # just grab the first one, who cares
           return images(bevelImages, (o, editor, inverse, lower, left, standup, open, thick,
              faceonly, stretchtex, notop, nobottom, noinner, noouter, subdivide))

class ColumnDuplicator(StandardDuplicator):

  def buildimages(self, singleimage=None):
    if singleimage is not None and singleimage>0:
      return []
    editor = mapeditor()
    inverse, open, thick, stretchtex, bulge, funnel, faceonly,notop,nobottom, noinner, noouter, circle, subdivide = map(lambda spec,self=self:self.dup[spec],
      ("inverse", "open", "thick", "stretchtex", "bulge", "funnel", "faceonly", "notop", "nobottom", "noinner","noouter",  "circle", "subdivide"))
    if thick:
      thick, = thick
    list = self.sourcelist()
    if subdivide is None:
        subdivide=1,
    for o in list:
      if o.type==":p": # just grab the first one, who cares
           return images(columnImages, (o, editor, inverse, open, thick, stretchtex, bulge,funnel,
             faceonly,notop,nobottom, noinner, noouter, circle,subdivide))

quarkpy.mapduplicator.DupCodes.update({
  "dup cap":     CapDuplicator,
  "dup bevel":   BevelDuplicator,
  "dup column":  ColumnDuplicator
})

#
#  --- Menus ---
#

def curvemenu(o, editor, view):

  def makecap(m, o=o, editor=editor):
      dup = quarkx.newobj(m.mapname+":d")
      dup["macro"]="dup cap"
      if m.inverse:
        dup["inverse"]=1
      dup.appenditem(m.newpoly)
      undo=quarkx.action()
      undo.exchange(o, dup)
      if m.inverse:
        editor.ok(undo, "make arch")
      else:
        editor.ok(undo, "make cap")
      editor.invalidateviews()


  def makebevel(m, o=o, editor=editor):
      dup = quarkx.newobj("bevel:d")
      dup["macro"]="dup bevel"
      dup["inverse"]=1
      if m.left:
        dup["left"]=1
      dup["open"]=1  # since this is normally rounding a corner with wall & ceiling"
      dup.appenditem(m.newpoly)
      undo=quarkx.action()
      undo.exchange(o, dup)
      if m.left:
        editor.ok(undo, "make left corner")
      else:
        editor.ok(undo, "make right corner")

  def makecolumn(m, o=o, editor=editor):
      dup = quarkx.newobj("column:d")
      dup["macro"]="dup column"
      dup["open"]=1  # since this is normally rounding a corner with wall & ceiling"
      dup.appenditem(m.newpoly)
      undo=quarkx.action()
      undo.exchange(o, dup)
      editor.ok(undo, "make column")

  disable = (len(o.subitems)!=6)

  newpoly = perspectiveRename(o, view)
  list = []

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

  for (menname, mapname, inv) in (("&Arch", "arch",  1), ("&Cap", "cap", 0)):
    item = qmenu.item(menname, makecap)
    item.inverse = inv
    item.mapname = mapname
    finishitem(item)
    list.append(item)

  cornerhint = """|Makes a smooth curve from the %s side of the brush to the back.

The texture is taken from the back wall, and sized across the curve (compressed a bit) to align with this texture as wrapped onto the %s wall.

To make a rounded corner, put a brush into a corner, project the texture of one of the room walls onto the paralell & `kissing' face of the brush, arrange the camera/view so you're looking square on at the brush and this face is the back one, then and RMB|Curves|right/left corner depending on whether the room-wall you're next to is to the right or the left.

If the textures on the two adjoining walls of the room are properly aligned, the texture on the curve will be too (compressed a bit, but not so as to make much of a difference).
"""


  for (name, left, hint) in (("&Left corner", 1, cornerhint%("left","left")),
                       ("&Right corner", 0, cornerhint%("right","right"))):
    item = qmenu.item(name, makebevel)
    item.inverse = 1
    item.left = left
    item.hint = hint
    finishitem(item)
    list.append(item)

  colitem = qmenu.item("C&olumn", makecolumn, "Make a column")
  finishitem(colitem)
  list.append(colitem)

  curvehint = """|Commands for making curves out of brushes.

The brush must be roughly a box, with the usual six sides.  The curve is implemented as a `duplicator' containing the brush, which determines the overall shape of the brush.

To resize the curve, select the brush in the treeview, and manipulate the sides in the usual manner (when the brush itself is selected, the curve becomes invisible).

When the duplicator is selected, the entity page provides a variety of specifics that can be manipulated to convert from an `arch' to a `cap' (by unchecking 'inverse'), and much else besides.

The curve will be oriented w.r.t. the map view you RMB-clicked on, or, if you're RMB-ing on the treeview, the most recent mapview you clicked in.

If the brush vanishes without being replaced by a shape, the brush may have been too screwy a shape, or looked at from a bad angle. (My attempts to detect these conditions in advance are meeting with unexpected resistance. There is also a bug in that if you apply this to a brush after first opening the map editor, without inserting anything first, the orientations are wrong.)
"""
  curvepop = qmenu.popup("Bezier Curves",list, hint=curvehint)
  if newpoly is None:
    if len(o.subitems)!=6:
      morehint= "\n\nThis item is disabled because the poly doesn't have exactly 6 faces."
    else:
      morehint="\n\nThis item is disabled because I can't figure out which face is front, back, etc.  Make it more box-like, and look at it more head-on in the view."
    curvepop.hint = curvepop.hint+morehint
    curvepop.state = qmenu.disabled
  return curvepop

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

    beziersupport = quarkx.setupsubset()["BezierPatchSupport"]
    if (beziersupport is not None) and (beziersupport == "1"):
        # only allow the curves-submenu, if the game-mode supports bezierpatches
        try:
            view = editor.layout.clickedview
        except:
            view = None
        return  [curvemenu(o, editor, view)]+oldmenu(o, editor)
    else:
        return  oldmenu(o, editor)

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
#$Log: mb2curves.py,v $
#Revision 1.34  2005/10/15 00:51:56  cdunde
#To reinstate headers and history
#
#Revision 1.31  2005/04/05 23:48:37  cdunde
#To clarify bezier RMB menu
#
#Revision 1.30  2002/12/29 04:17:58  tiglari
#transfer fixes from 6.3
#
#Revision 1.29.14.2  2002/12/29 02:59:28  tiglari
#a bit of cleanup, remove failed attempt to supress centering tex coordinates
# with threepoints call; this now down in quarkpy/bqurils:texcpfromface
#
#Revision 1.29.14.1  2002/12/28 23:52:18  tiglari
#add _fixed flag to inhibit L-square recentering of tex alignment faces
#
#Revision 1.29  2001/03/01 19:14:16  decker_dk
#changed newpolymenu() so it checks 'BezierPatchSupport' to see if it should allow the Curves-menu.
#
#Revision 1.28  2001/02/25 04:46:49  tiglari
#new specifics for brush&patch arch&bevel
#
#Revision 1.27  2001/02/14 10:08:58  tiglari
#extract perspective stuff to quarkpy.perspective.py
#
#Revision 1.26  2000/09/04 21:29:03  tiglari
#added lots of specifics to column generator, fixed column & arch bugs
#
#Revision 1.25  2000/09/02 11:25:43  tiglari
#added subdivides & detail specifics to arch/cap.  last two (ends/sides) are howeer still unimplemented
#
#Revision 1.24  2000/07/26 11:37:31  tiglari
#thick arch/bevel bugz fixed
#
#Revision 1.23  2000/06/30 11:01:06  tiglari
#fixed thick bevel bug
#
#Revision 1.22  2000/06/26 22:54:58  tiglari
#renaming: antidistort_rows/columns->undistortRows/Colunmns,
#tanaxes->tanAxes, copy/map/transposecp->copy/map/transposeCP
#
#Revision 1.21  2000/06/25 23:47:01  tiglari
#Function Renaming & Reorganization, hope no breakage
#
#Revision 1.19  2000/06/25 11:30:11  tiglari
#oops, bugfix for cones & bulges for columns, some function renaming
#
#Revision 1.18  2000/06/25 11:02:23  tiglari
#cones & bulges for columns, some function renaming
#
#Revision 1.17  2000/06/25 06:09:34  tiglari
#top & bottom plates for columns, some texturing bugfixes
#
#Revision 1.16  2000/06/24 09:40:17  tiglari
#thickness for columns
#
#Revision 1.15  2000/06/22 22:39:40  tiglari
#added support for columns (and pipes)
#
#Revision 1.14  2000/06/19 11:46:22  tiglari
#Fixes to texture alignment on arches
#
#Revision 1.13  2000/06/17 09:42:53  tiglari
#yet another texture scale fix (upper arches de-borked again...
#
#Revision 1.12  2000/06/17 07:35:12  tiglari
#arch/cap texture now projected off top or bottom for normal
#and lower, respectively; stretchtex option added vs. complex
#alignment.
#
#Revision 1.11  2000/06/16 10:48:26  tiglari
#Fixed perspective-driven builder problems
#
#Revision 1.10  2000/06/16 06:02:42  tiglari
#fixed coordinate handedness screwup in floating map veiews
#
#Revision 1.9  2000/06/16 05:11:31  tiglari
#fixed antidistortion on arch underside, which got broken
#
#Revision 1.8  2000/06/14 04:41:18  tiglari
#Added `faceonly' specific for arches & bevels.
#
#Revision 1.7  2000/06/13 12:52:40  tiglari
#Supported all the current arch/cap and bevel specifics
#
#Revision 1.6  2000/06/12 11:18:20  tiglari
#Added bevel duplicator and round corner curves submenu items for Q3
#
#Revision 1.5  2000/06/04 03:23:50  tiglari
#reduced/eliminated distortion on arch/cap curve face
#
#Revision 1.4  2000/06/03 13:01:25  tiglari
#fixed arch duplicator maploading problem, hopefully, also
#arch duplicator map writing problem
#
#Revision 1.3  2000/06/03 10:25:30  alexander
#added cvs headers
#
#Revision 1.2  2000/05/28 06:28:48  tiglari
#fixed problem with revision history (2 of them, no# for first snap)
#
#Revision 1.1  2000/05/26 23:04:17  tiglari
#Arch-builders.  There's a bug in quark.clickform, which doesn't seem to work right until something has been dropped into the map.
#
#

