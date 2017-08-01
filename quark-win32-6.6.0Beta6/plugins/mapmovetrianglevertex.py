"""   QuArK  -  Quake Army Knife

Triangular Vertex moving plugin
"""

#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

# $Header: /cvsroot/quark/runtime/plugins/mapmovetrianglevertex.py,v 1.5 2005/10/15 00:51:24 cdunde Exp $

Info = {
   "plug-in":       "Triangular Vertex Movement",
   "desc":          "Functions for moving vertexes",
   "date":          "03 June 2005",
   "author":        "cdunde and Rowdy",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6.x" }


#
# The import statements make material in other files available
#  to the statements in this file
#

#
# Quarkx is the delphi-defined API
#
import quarkx
import math  # To get sqrt function
from plugins.mapterrainpos import *  # to import global input from this file
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
# May need to change to handle just triangles and not rectangles.
#

def terrainprojectpointtoplane(p,n1,o2,n2):
  "project point to plane at o2 with normal n2 along normal n1"
  v1 = o2-p
  v2 = v1*n2
  v3 = n1*n2
  v4 = v2/v3
  v5 = v4*n1
  return p + v5

#
# Main math function.
# This does the face movement to rotate them to
# A new angle when pulled up or down and handles
# the locked peremiter edges.
#
def TRrotateFace(newface, oldverpos, facemoved, TGlockvertex0, pivot2):
    "rotates newface from oldverpos by facemoved around pivots"

    rotationAxis = (pivot2-TGlockvertex0).normalized
    norm1 = (rotationAxis^(oldverpos-TGlockvertex0)).normalized
    plane1 = rotationAxis^norm1
    norm2 = (rotationAxis^(oldverpos+facemoved-TGlockvertex0)).normalized
    plane2 = rotationAxis^norm2
    points = newface.threepoints(3)
    facenorm = newface.normal
    def proj(v, org=TGlockvertex0, ax1=rotationAxis, ax2=plane1):
        return (v-org)*ax1, (v-org)*ax2
    #
    # map applies proj to each member in the tuple `points',
    #  producing the new tuple `pcoords'
    #
    pcoords = map(proj, points)
    newface.setthreepoints((pivot2, TGlockvertex0, oldverpos+facemoved),0)
    if facenorm*newface.normal<0:
        newface.swapsides()
    newpoints = newface.threepoints(0)
    def proj2plane(p,pp=newpoints[1],nn=newface.normal):
        return terrainprojectpointtoplane(p,nn,pp,nn)
    def unproj((x, y),org=TGlockvertex0,ax1=rotationAxis, ax2=plane2):
        return org+x*ax1+y*ax2

    newpoints = tuple(map(proj2plane, (map(unproj, pcoords))))
    newface.setthreepoints(newpoints,3)

def moveTriangleFaces(oldface, oldverpos, facemoved, polyofface, TGlockvertex, pos, bbox):
    "returns the moving old, new faces, of polyofface , with oldverpos moved by facemoved"

    bbmin, bbmax = bbox
    Xdist = bbmax.tuple[0] - pos.tuple[0]
    Ydist = bbmax.tuple[1] - pos.tuple[1]
    if Xdist < 0:
        Xdist = Xdist * -1
    if Ydist < 0:
        Ydist = Ydist * -1
    Xfactor = 1/Xdist
    Yfactor = 1/Ydist
    vX, vY, vZ = oldverpos.tuple
    if vX >pos.tuple[0]:
        netdist = vX - pos.tuple[0]
    else:
        netdist = pos.tuple[0] - vX
    if netdist < 0:
        netdist = netdist * -1
    movefactor = (Xdist - netdist) * Xfactor

    result = []
    old = []
    for face in oldface:
        newface = face.copy()
        norm = face.normal

### Movement adjustors and factors, creates changes by user input

        from plugins.mapterrainpos import scalex,scaley,tilt,shear,flat
        if flat == None: flat = "0"
        
        if scalex is None and scaley is None:
            if (quarkx.setupsubset(SS_MAP, "Options")["Selector1_scale"] is not None):
                topfactor, topamount = quarkx.setupsubset(SS_MAP, "Options")["Selector1_scale"]
            else:
                topamount = 1
                topfactor = .5
        else:
            topamount = scaley
            topfactor = scalex
        
        if tilt is None and shear is None:
            if (quarkx.setupsubset(SS_MAP, "Options")["Selector1_offset"] is not None):
                basefactor, baseamount = quarkx.setupsubset(SS_MAP, "Options")["Selector1_offset"]
            else:
                baseamount = 1
                basefactor = .5
        else:
            baseamount = shear
            basefactor = tilt

        topadjustor = quarkx.vect(0,0,topamount)
        baseadjustor = quarkx.vect(0,0,baseamount)

        if len(TGlockvertex) == 0:
            tempvertexlist = []
            for vertex in face.verticesof(polyofface):
                if str(oldverpos) != str(vertex):
                    tempvertexlist.append(vertex)
            basevertex0 = tempvertexlist[0]
            basevertex1 = tempvertexlist[1]
#
## This section corrects for vertexes closest to the handle center pos
#
## Checks for closeness on both the X and Y axis
            sqrt_pos=math.sqrt((pos.tuple[0]*pos.tuple[0])+(pos.tuple[1]*pos.tuple[1]))
            sqrt_ovpos=math.sqrt((oldverpos.tuple[0]*oldverpos.tuple[0])+(oldverpos.tuple[1]*oldverpos.tuple[1]))
            sqrt_bv0=math.sqrt((basevertex0.tuple[0]*basevertex0.tuple[0])+(basevertex0.tuple[1]*basevertex0.tuple[1]))
            sqrt_bv1=math.sqrt((basevertex1.tuple[0]*basevertex1.tuple[0])+(basevertex1.tuple[1]*basevertex1.tuple[1]))

            if abs(sqrt_pos-sqrt_ovpos) > abs(sqrt_pos-sqrt_bv0):
                hold = oldverpos
                oldverpos = basevertex0
                basevertex0 = hold
            if abs(sqrt_pos-sqrt_ovpos) > abs(sqrt_pos-sqrt_bv1):
                hold = oldverpos
                oldverpos = basevertex1
                basevertex1 = hold
            if abs(sqrt_pos-sqrt_bv0) > abs(sqrt_pos-sqrt_bv1):
                hold = basevertex0
                basevertex0 = basevertex1
                basevertex1 = hold
            if abs(basevertex0.tuple[0] - pos.tuple[0]) < 1 and abs(basevertex0.tuple[1] - pos.tuple[1]) < 1:
                hold = oldverpos
                oldverpos = basevertex0
                basevertex0 = hold
            if abs(basevertex1.tuple[0] - pos.tuple[0]) < 1 and abs(basevertex1.tuple[1] - pos.tuple[1]) < 1:
                hold = oldverpos
                oldverpos = basevertex1
                basevertex1 = hold

#
## This seciton starts applying the movefactor formula
#
            ovposX = abs(pos.tuple[0]-oldverpos.tuple[0])
            ovposY = abs(pos.tuple[1]-oldverpos.tuple[1])
            ovposnetdist = math.sqrt((ovposX*ovposX)+(ovposY*ovposY))

            if abs(oldverpos.tuple[0] - pos.tuple[0]) < 1 and abs(oldverpos.tuple[1] - pos.tuple[1]) < 1:
                if ovposX == 0 and ovposY == 0:
                    ovposmovefactor = (Xdist - ovposnetdist*-.15) * Xfactor
                    oldverpos = oldverpos + (facemoved * ovposmovefactor)*-.15+topadjustor*topfactor

                elif  ovposX == pos.tuple[0] and ovposY == pos.tuple[1]:
                    ovposmovefactor = (Xdist - ovposnetdist*-.15) * Xfactor
                    oldverpos = oldverpos + (facemoved * ovposmovefactor)*-.15+topadjustor*topfactor
                else:
                    oldverpos = quarkx.vect(oldverpos.tuple[0]-ovposX,oldverpos.tuple[1]-ovposY,oldverpos.tuple[2])
                    ovposmovefactor = (Xdist - ovposnetdist*-.15) * Xfactor
                    oldverpos = oldverpos + (facemoved * ovposmovefactor)*-.15+topadjustor*topfactor
            else:
                ovposmovefactor = (Xdist - ovposnetdist) * Xfactor
                oldverpos = oldverpos + (facemoved * ovposmovefactor)-facemoved+baseadjustor*basefactor

            bv0X = abs(pos.tuple[0]-basevertex0.tuple[0])
            bv0Y = abs(pos.tuple[1]-basevertex0.tuple[1])
            bv0netdist = math.sqrt((bv0X*bv0X)+(bv0Y*bv0Y))
            bv0movefactor = (Xdist - bv0netdist) * Xfactor
            basevertex0 = basevertex0 + (facemoved * bv0movefactor)+baseadjustor*basefactor

            bv1X = abs(pos.tuple[0]-basevertex1.tuple[0])
            bv1Y = abs(pos.tuple[1]-basevertex1.tuple[1])
            bv1netdist = math.sqrt((bv1X*bv1X)+(bv1Y*bv1Y))
            bv1movefactor = (Xdist - bv1netdist) * Xfactor
            basevertex1 = basevertex1 + (facemoved * bv1movefactor)+baseadjustor*basefactor
#
## The line below sends the vertexes to be moved
#
            TRrotateFace(newface, oldverpos, facemoved, basevertex0, basevertex1)

        if len(TGlockvertex)==1:
            tempvertexlist = []
            for vertex in face.verticesof(polyofface):
                if str(oldverpos) != str(vertex):
                    if str(TGlockvertex[0]) != str(vertex):
                        tempvertexlist.append(vertex)
            basevertex0 = tempvertexlist[0]

## Checks for closeness on X axis
            if abs(pos.tuple[0]-oldverpos.tuple[0]) > abs(pos.tuple[0]-basevertex0.tuple[0]):
                hold = oldverpos
                oldverpos = basevertex0
                basevertex0 = hold
## Checks for closeness on Y axis
            if abs(pos.tuple[1]-oldverpos.tuple[1]) > abs(pos.tuple[1]-basevertex0.tuple[1]):
                hold = oldverpos
                oldverpos = basevertex0
                basevertex0 = hold

            ovposX = abs(pos.tuple[0]-oldverpos.tuple[0])
            ovposY = abs(pos.tuple[1]-oldverpos.tuple[1])
            ovposnetdist = math.sqrt((ovposX*ovposX)+(ovposY*ovposY))
            ovposmovefactor = (Xdist - ovposnetdist) * Xfactor
            oldverpos = oldverpos + (facemoved * ovposmovefactor)-facemoved+baseadjustor*basefactor

            bv0X = abs(pos.tuple[0]-basevertex0.tuple[0])
            bv0Y = abs(pos.tuple[1]-basevertex0.tuple[1])
            bv0netdist = math.sqrt((bv0X*bv0X)+(bv0Y*bv0Y))
            bv0movefactor = (Xdist - bv0netdist) * Xfactor
            basevertex0 = basevertex0 + (facemoved * bv0movefactor)+baseadjustor*basefactor

            TRrotateFace(newface, oldverpos, facemoved, TGlockvertex[0], basevertex0)

        if len(TGlockvertex) == 2:
            ovposX = abs(pos.tuple[0]-oldverpos.tuple[0])
            ovposY = abs(pos.tuple[1]-oldverpos.tuple[1])
            ovposnetdist = math.sqrt((ovposX*ovposX)+(ovposY*ovposY))
            ovposmovefactor = (Xdist - ovposnetdist) * Xfactor
            oldverpos = oldverpos + (facemoved * ovposmovefactor)-facemoved+baseadjustor*basefactor

            TRrotateFace(newface, oldverpos, facemoved, TGlockvertex[0], TGlockvertex[1])

        if len(TGlockvertex) > 2:

            if flat == "0":
                continue
            else:
                if norm*(oldverpos+facemoved-TGlockvertex[0]):
                    proj = facemoved*norm      # 1 of 2 these make the face move
                    newface.translate(proj*norm)  # 2 of 2 these make the face move
        old.append(face)
        result.append(newface)
    return old, result

# $Log: mapmovetrianglevertex.py,v $
# Revision 1.5  2005/10/15 00:51:24  cdunde
# To reinstate headers and history
#
# Revision 1.2  2005/08/16 07:54:49  cdunde
# fixed need for 1st time setting
#
# Revision 1.1  2005/08/15 05:49:23  cdunde
# To commit all files for Terrain Generator
#
#