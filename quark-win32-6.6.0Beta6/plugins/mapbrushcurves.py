"""   QuArK  -  Quake Army Knife Bezier shape makers


"""


# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

########################################################
#
#                          Brush Curves Plugin
#                          v1.0, Dec 2000
#                      works with Quark 6.1
#
#
#                    by tiglari@hexenworld.net
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & improvements to tiglari@hexenworld.com
#
###
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/mapbrushcurves.py,v 1.18 2005/10/15 00:49:51 cdunde Exp $


Info = {
   "plug-in":       "Brush Curves plugin",
   "desc":          "Pseudo-curves made of brushes, etc.",
   "date":          "30 Dec 2000",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.net",
   "quark":         "Version 6.1" }


import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.mapeditor
import quarkpy.mapcommands
import quarkpy.mapoptions
import quarkpy.qhandles
import quarkpy.maphandles
#import quarkpy.dlgclasses
import quarkpy.mapduplicator
StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator
from quarkpy.maputils import *
from quarkpy.perspective import *

#import quarkpy.mapbezier
#from quarkpy.b2utils import *

#############################
#
#  MAJOR SECTIONS
#
#
#  - image builders: implementation of buildimages for the
#      shape-builders
#




#
# the underlying equation is matrix*invect=outvect
#   as colums, uses tr(M*N)=tr(M)*tr(N) transpositionfact
#
def matrixFromMap(v1, v2, v3, w1, w2, w3):
    invect = quarkx.matrix(v1,v2,v3)
    outvect = quarkx.matrix(w1,w2,w3)
    if abs(invect)==0:
        return None
    return outvect*~invect

#
# Temp from maputils to help run with older quark versions
#
#
def matrix_u_v(u,v):
    return quarkx.matrix(u, v, quarkx.vect(0,0,1))

def intersectionPoint2d(p0, d0, p1, d1):
    "intersection in 2D plane, point, direction"
    for v in p0, d0, p1, d1:
        if v.z != 0.0:
            return None
    det = d0.x*d1.y-d1.x*d0.y
    if det==0.0:
        return 0  # lines paralell
    s = (p0.y*d1.x - p1.y*d1.x - d1.y*p0.x +d1.y*p1.x)/det
    return p0+s*d0



#
# -- Image builders
#
#    many of these below should probably be stuck inside
#    the appropriate cap/bevel/columnImages method
#

#
# a variant of arcSubdivideLine from quarkpy.b2utils.py.
#
# n line-segments are generated, approximating an ellipse
#   nested in the corner formed by (p1, p0) and (p2, p0),
#   lines inside, touchning at corners.
#
# derived from a suggestion by Alex Haarer.
#
def innerArcLine(n, p0, p1, p2):
    mat = matrix_u_v(p0-p1, p2-p1)
    halfpi = math.pi/2.0
    points = [quarkx.vect(1,0,0)]
    for i in range(n):
        a = halfpi*(i+1)/n
        next = quarkx.vect(1.0-math.sin(a), 1.0-math.cos(a), 0)
        points.append(next)
    points = map (lambda v,mat=mat,d=p1:d+mat*v, points)
    return points

#
# Approximates quarter-circle with lines outside,
#  touching as tangent
#
def outerArcLine(n, p0, p1, p2):
    mat = matrix_u_v(p0-p1, p2-p1)
    halfpi = math.pi/2.0
    points = []
    prev = quarkx.vect(1,0,0)
    prevdir = quarkx.vect(-1,0,0)
    for i in range(n+1):
        if i==n:
            current = quarkx.vect(0,1,0)
            currdir = quarkx.vect(0,-1,0)
        else:
            a = halfpi*(i+1)/(n+1)
            current = quarkx.vect(1.0-math.sin(a), 1.0-math.cos(a), 0)
            currdir = quarkx.vect(-math.cos(a), math.sin(a), 0)
        mid = intersectionPoint2d(prev,prevdir, current, currdir)
#        squawk(`mid`)
        points.append(mid)
        prev = current
        prevdir = currdir
    points = map (lambda v,mat=mat,d=p1:d+mat*v, points)
    return points


def arcLength(points):
    length=0.0
    for i in range(len(points)-1):
        length=length+abs(points[i+1]-points[i])
    return length

#
# These three won't be used until or unless the `thick'
#   variants are implemented.
#
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


def bevelImages(o, editor, inverse=0, left=0, lower=0, rotate=0, grid=0, thick=0, inner=0, (subdivide,)=1):
    "makes a bevel/inverse bevel on the basis of brush o"
    #
    #  Set stuff up
    #
    o.rebuildall()
    fdict = faceDict(o)
    if fdict is None:
        return
    if left:
        fdict = facedict_hflip(fdict)
    if rotate:
        fdict = facedict_rflip(fdict)
    if lower:
       fdict = facedict_fflip(fdict)
    subdivide = int(subdivide)
    def makestuff(pd, fdict, subdivide=subdivide, inner=inner, grid=grid):
        if inner:
            curve = innerArcLine(subdivide, pd["tlb"],pd["trb"],pd["trf"])
        else:
            curve = outerArcLine(subdivide, pd["tlb"],pd["trb"],pd["trf"])
        #
        # assumes that the box points are already on the grid,
        #  so that we only have to force the curve points
        #
        if grid:
            for i in range(len(curve)):
                curve[i]=quarkpy.qhandles.aligntogrid(curve[i],1)
        cornerlength=arcLength((curve[0],pd["trb"],curve[len(curve)-1]))
        #
        # get line of equal length of curve, in back face plane
        #
        span = (pd["trb"]-pd["tlb"]).normalized
        depth = (pd["tlb"]-pd["blb"]).normalized
        cross = (span^depth).normalized
        texmat = matrixFromMap(depth,cross,span*cornerlength,depth,cross,span*arcLength(curve))

        #
        # make texture source face
        #
        texface = fdict["b"].copy()
        texface.linear(curve[0],texmat)

        texface.swapsides()
        return curve, texface

    pd = pointdict(vtxlistdict(fdict,o))
    curve, texface = makestuff(pd, fdict)

    brushes = []
    #
    #  Generate the brushes
    #
    def makeFace(tag,fdict=fdict):
        return fdict[tag].copy()
    depth = pd["tlb"]-pd["blb"]
    bottom, top = map(makeFace, ("d","u"))
    bottom.shortname, top.shortname = "bottom", "top"
    final = subdivide-1
    if left:
        texface.swapsides()
    if not inverse:
        texface.swapsides()
    if lower:
        texface.swapsides()

    def transfertex(face,texface, pivot):
        texface.distortion(face.normal,pivot)
        face.setthreepoints(texface.threepoints(2),2)
        return texface.copy()

    if thick:
        pd2 = smallerbevelbox(pd, thick)
        curve2, texface2 = makestuff(pd2, fdict)
        base=quarkx.newobj('front:f')
        base.setthreepoints((curve[0],curve2[0],curve[0]+depth),0)
#        base["tex"]=fdict["r"]["tex"]
        base["tex"]=CaulkTexture()
        if not inner:
            brush=quarkx.newobj('brush:p')
            capper=texface.copy()
            if lower:
                capper.swapsides()
            if not left:
                capper.swapsides()
            brush.appenditem(capper)
            capperbot=capper.copy()
            capperbot.translate(curve2[0]-curve[0])
            capperbot.swapsides()
            brush.appenditem(capperbot)
            base0=base.copy()
            if not left:
               base0.swapsides()
            if lower:
               base0.swapsides()
            brush.appenditem(base0)
            brush.appenditem(bottom.copy())
            brush.appenditem(top.copy())
            end = fdict['l'].copy()
            end.shortname = "end"
            brush.appenditem(end)
            brushes.append(brush)

        side=quarkx.newobj('side:f')
#        side["tex"]=fdict["b"]["tex"]
        side["tex"]=CaulkTexture()
        side.setthreepoints((curve[subdivide],curve[subdivide]+depth,curve2[subdivide]),0)
        if left:
            base.swapsides()
            side.swapsides()
        if lower:
            base.swapsides()
            side.swapsides()
        for i in range(subdivide):
            brush = quarkx.newobj('brush'+`i`+':p')
            brush.appenditem(base)
            face=quarkx.newobj('face'+`i`+':f')
            face.setthreepoints((curve[i],curve[i+1],curve[i]+depth),0)
            face = transfertex(face, texface,curve[i])
            face.swapsides()
            def gettex(v, texp=face.threepoints(2)):
                return texCoords(v, texp)
            texpoints = map(gettex, (curve[i], curve[i+1], curve[i]+depth))
            face2=quarkx.newobj('face2'+`i`+':f')
            face2.setthreepoints((curve2[i],curve2[i+1],curve2[i]+depth),0)
            face2["tex"]=face["tex"]
            texp2 = solveForThreepoints((curve2[i],texpoints[0]),
              (curve2[i+1],texpoints[1]), (curve2[i]+depth, texpoints[2]))
            face2.setthreepoints(texp2,2)
            if left:
                face.swapsides()
                face2.swapsides()
            if not inverse:
                face.swapsides()
                face2.swapsides()
            if lower:
                face.swapsides()
                face2.swapsides()
            brush.appenditem(face)
            brush.appenditem(face2)
            brush.appenditem(bottom.copy())
            brush.appenditem(top.copy())
            if i<final:
                div=quarkx.newobj('div'+`i`+':f')
#                div["tex"]=fdict["b"]["tex"]
                div["tex"]=CaulkTexture()
                div.setthreepoints((curve[i+1], curve2[i+1], curve[i+1]+depth),0)
                div.swapsides()
                if left:
                    div.swapsides()
                if not inverse:
                    div.swapsides()
                if lower:
                    div.swapsides()
                brush.appenditem(div)
                base=div.copy()
                base.swapsides()
            else:
                brush.appenditem(side)
            brushes.append(brush)

        #
        # make the 'legs'
        #
        if not inner:
            brush = quarkx.newobj('brush'+':p')
            brush.appenditem(bottom.copy())
            brush.appenditem(top.copy())
            base=side.copy()
            base.swapsides()
            brush.appenditem(base)
            brush.appenditem(fdict['f'].copy())
            brushes.append(brush)
            out = fdict['b'].copy()
            out.distortion(fdict['r'].normal,pd["trb"])
 #           out = fdict['r'].copy()
            brush.appenditem(out)
            innit = out.copy()
            innit.translate(pd2["trf"]-pd["trf"])
            innit.swapsides()
            brush.appenditem(innit)

        return brushes

    if inverse:
        pivot=pd["trb"]
    else:
        pivot=pd["tlf"]

    if inverse:
        base, side = map(makeFace, ("b","r"))
    else:
        base, side = map(makeFace, ("l","f"))
    base.shortname, side.shortname = "base", "side"
    base["tex"]=fdict["b"]["tex"]
    for i in range(subdivide):
        brush = quarkx.newobj('bevelImage brush'+`i`+':p') # DECKER 2002-08-09: A more descriptive name for debugging. The previous made it a bit confusing to read in .MAP comments.
        brush.appenditem(base)
        if i==0 and not inverse and not inner:
            brush.appenditem(fdict["b"].copy())
        face=quarkx.newobj('face'+`i`+':f')
        face.setthreepoints((curve[i],curve[i+1],curve[i]+depth),0)
        face = transfertex(face, texface, curve[i])
        if left:
            face.swapsides()
        if not inverse:
            face.swapsides()
        if lower:
            face.swapsides()
        brush.appenditem(face)
        brush.appenditem(bottom.copy())
        brush.appenditem(top.copy())
        if i<final:
            div=quarkx.newobj('div'+`i`+':f')
#            div["tex"]=fdict["b"]["tex"]
            div["tex"]=CaulkTexture()
            div.setthreepoints((pivot, pivot+depth, curve[i+1]),0)
            if left:
                div.swapsides()
            if not inverse:
                div.swapsides()
            if lower:
                div.swapsides()
            brush.appenditem(div)
            base=div.copy()
            base.swapsides()
        else:
            brush.appenditem(side)
            if not inverse and not inner:
                brush.appenditem(fdict["r"].copy())
        brushes.append(brush)
    return brushes


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

class BrushCapDuplicator(StandardDuplicator):

  def buildimages(self, singleimage=None):
    if singleimage is not None and singleimage>0:
      return []
    editor = mapeditor()
    inverse, lower, onside, grid, thick, inner, subdivide = map(lambda spec,self=self:self.dup[spec],
      ("inverse", "lower", "onside", "grid", "thick", "inner", "subdivide"))
    if thick:
      thick, = thick
    if not onside:
      standup="1"
    else:
      standup=None
    if subdivide is None:
        subdivide=1,
    list = self.sourcelist()
    for o in list:
       if o.type==":p": # just grab the first one, who cares
           o.rebuildall()
           fdict = faceDict(o)
           if fdict is None:
               return
           pd = pointdict(vtxlistdict(fdict,o))
           mtf = (pd["trf"]+pd["tlf"])/2
           mtb = (pd["trb"]+pd["tlb"])/2
           mbf = (pd["brf"]+pd["blf"])/2
           face = quarkx.newobj("left:f")
           face.setthreepoints((mtf, mtb, mbf),0)
           face2 = face.copy()

           face2.swapsides()
           face2.shortname = "right"

           face["tex"]  = o.findallsubitems('left' ,':f')[0]["tex"] # DECKER 2002-08-09: Remember to give the newly created faces a texture.
           face2["tex"] = o.findallsubitems('right',':f')[0]["tex"] # Thanks to "Adam K" <sentrymaster@hotmail.com> for indirectly pointing out this error.

           o1, o2 = o.copy(), o.copy()
           o1.removeitem(o1.findallsubitems('left',':f')[0])
           o2.removeitem(o2.findallsubitems('right',':f')[0])
           o1.appenditem(face)
           o2.appenditem(face2)

           im1 = images(bevelImages, (o1, editor, inverse, 0, lower, standup, grid, thick, inner, subdivide))
           im2 = images(bevelImages, (o2, editor, inverse, 1, lower, standup, grid, thick, inner, subdivide))

           if thick and not inner:
               end1 = (im1[0].findallsubitems("end",":f"))[0]
               end2 = (im2[0].findallsubitems("front",":f"))[0]
               im1[0].removeitem(end1)
               im1[0].appenditem(end2.copy())
               im2 = im2[1:]
               pass
           return im1+im2
    return None # DECKER 2002-08-09: Always return something, even if we're never supposed to end here!

class BrushBevelDuplicator(StandardDuplicator):

  def buildimages(self, singleimage=None):
    if singleimage is not None and singleimage>0:
      return []
    editor = mapeditor()
    inverse, lower, left, standup, grid, thick, inner, subdivide = map(lambda spec,self=self:self.dup[spec],
      ("inverse", "lower", "left", "grid", "standup", "thick", "inner", "subdivide"))
    if thick:
        thick, = thick
    list = self.sourcelist()
    if subdivide is None:
        subdivide=1,
    for o in list:
        if o.type==":p": # just grab the first one, who cares
            return images(bevelImages, (o, editor, inverse, left, lower, standup, grid, thick, inner, subdivide))


quarkpy.mapduplicator.DupCodes.update({
  "dup brushcap":     BrushCapDuplicator,
  "dup brushbevel":   BrushBevelDuplicator,
})

#
#  --- Menus ---
#

def curvemenu(o, editor, view):

  def makecap(m, o=o, editor=editor):
      dup = quarkx.newobj(m.mapname+":d")
      dup["macro"]="dup brushcap"
      if m.inverse:
        dup["inverse"]=1
      dup["subdivide"]=2,
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
      dup["macro"]="dup brushbevel"
      dup["inverse"]=1
      dup["subdivide"]=2,
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

  curvehint = """|Commands for making curves out of brushes.

The brush must be roughly a box, with the usual six sides.  The curve is implemented as a `duplicator' containing the brush, which determines the overall shape of the brush.

To resize the curve, select the brush in the treeview, and manipulate the sides in the usual manner (when the brush itself is selected, the curve becomes invisible).

When the duplicator is selected, the entity page provides a variety of specifics that can be manipulated to convert from an `arch' to a `cap' (by unchecking 'inverse'), and much else besides.

The curve will be oriented w.r.t. the map view you RMB-clicked on, or, if you're RMB-ing on the treeview, the most recent mapview you clicked in.

If the brush vanishes without being replaced by a shape, the brush may have been too screwy a shape, or looked at from a bad angle. (My attempts to detect these conditions in advance are meeting with unexpected resistance. There is also a bug in that if you apply this to a brush after first opening the map editor, without inserting anything first, the orientations are wrong.)
"""
  curvepop = qmenu.popup("Brush Curves",list, hint=curvehint)
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
#$Log: mapbrushcurves.py,v $
#Revision 1.18  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.15  2002/12/09 10:34:01  tiglari
#fix bug with non-inverse brushcap (noted by quantum_red)
#
#Revision 1.14  2002/08/09 09:59:02  decker_dk
#Fixed a problem, where the bevelImage() could end up using a face without a
#texture-name attached. Look for "DECKER 2002-08-09"
#
#Revision 1.13  2001/05/13 01:08:56  tiglari
#caulk hidden joins, add missing sides to non-inverse non-outer arch/bevel
#
#Revision 1.12  2001/04/29 21:00:09  tiglari
#add missing textures to thick curves
#
#Revision 1.11  2001/04/16 12:32:39  tiglari
#thick supported for arches and bevels
#
#Revision 1.10  2001/04/10 08:56:25  tiglari
#add force vertexes to grid (grid specific); some preliminary steps towards
# implementing 'thick'
#
#Revision 1.9  2001/03/29 09:28:55  tiglari
#scale and rotate specifics for duplicators
#
#Revision 1.8  2001/02/25 08:40:01  tiglari
#`curve' faces now copy all specifics from guidebrush (esp.lightvalue for arghrad)
#
#Revision 1.7  2001/02/25 04:46:49  tiglari
#new specifics for brush&patch arch&bevel
#
#Revision 1.6  2001/02/25 02:00:34  tiglari
#fixed texture placement bug, changed default subdiv to 2, moved forms
# to defaults.qrk because of memory release problem.
#
#Revision 1.5  2001/02/17 23:12:45  tiglari
#texture positioning done
#
#Revision 1.4  2001/02/14 10:08:58  tiglari
#extract perspective stuff to quarkpy.perspective.py
#
#Revision 1.3  2001/01/03 21:38:00  tiglari
#remove column from menu, add someutils to help it work with older q v ersions
#
#Revision 1.2  2001/01/03 20:10:40  tiglari
#added outer circle approximation
#
#Revision 1.1  2001/01/02 07:56:49  tiglari
#brush curves, adapted from mb2curves.py.  Columns still produces patches,
#only provides `inner' approximation to arcs,  'outer' prolly better, coming next,
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

