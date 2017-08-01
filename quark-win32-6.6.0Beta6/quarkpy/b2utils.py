"""   QuArK  -  Quake Army Knife

Various quadratic bezier utilities.
"""

#
# by tiglari@hexenworld.com, May 2000
#
#THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/b2utils.py,v 1.22 2007/12/14 21:48:00 cdunde Exp $


import math
import quarkx
from maputils import *

#
# Here should go things of general utility for managing
#  quadratic bezier patches
# 



within45 = math.cos(deg2rad*45)

def iseven(num):
  return not divmod(num,2)[1]

def linearcomb(C, P):
 "linear combination"
 return reduce(lambda x,y:x+y, map(lambda p,c:c*p,C,P))

def extend_distance_by(v1, v2, ext):
  "v1 plus distance from v1 to v2 times ext"
  return v1 + ext*(v2-v1)


#
# Some useful things for Quadratic Beziers
#

def rowofcp(cp, i):
    return cp[i]
    
def colofcp(cp, j):
    return map(lambda row,j=j:row[j], cp)

def lengthof(line, divs):
    if divs<0:
      return
    sum=0
    for i in range((len(line)-1)/2):
      k = 2*i
      sum=sum+lengthofseg(line[k], line[k+1], line[k+2], divs)
    return sum

#
# If this were going to get out into generally applying non-UI
#   routines, it might be worth shifting it into delphi.
#
def lengthofseg(p0, p1, p2, divs):
    "approximates length of b2 line segment, splitting into 2^divs segments"
    if divs == 0:
       return abs(p2-p0)
    else:
       m = b2midpoint(p0, p1, p2)
       q1 = b2qtpoint(p0, p1, p2)
       q3 = b2qt3point(p0, p2, p2)
       m0 = b2midcp(p0, q1, m)
       m1 = b2midcp(m, q3, p2)
       return lengthofseg(p0, m0, m, divs-1)+lengthofseg(m, m1, p2, divs-1)
       
def b2midpoint(p0, p1, p2):
  "midpoint of the b2 line for the three points"
  return 0.25*p0 + 0.5*p1 + 0.25*p2
  
def b2qtpoint(p0, p1, p2):
  "1 quarter point of the b2 line for the three points"
  return (9/16.0)*p0+(3/8.0)*p1+(1/16.0)*p2

def b2qt3point(p0, p1, p2):
  "3 quarter point of the b2 line for the three points"
  return (1/16.0)*p0+(3/8.0)*p1+(9/16.0)*p2

def b2midcp(p0, m, p2):
  "cp to get b2 line from p0 to p2 passing thru m"
  return 2.0*m-0.5*(p0+p2)



def interpolateGrid(p0, p1, p2, p3, h=3, w=3):
    "makes a bezier from the four points"
    "p0, ..., p1 top row, p2,..., p3 bottom"
    cp = []
    h, w = float(h), float(w)
    H, W = h-1, w-1
    upfront, upback = (p2-p0)/(h-1), (p3-p1)/(h-1)
    for i in range(h):
        front, back = p0+i*upfront, p1+i*upback
        across = (back-front)/(w-1)
        row = []
        for j in range(w):
            #
            # non 3x3 cp's need to be 5-space
            #
            row.append(quarkx.vect((front+j*across).tuple+(i/H,j/W)))
        cp.append(row)
    return cp


def transposeCp(cp):
    "returns cp transposed"
    new = map(lambda x:[],range(len(cp[0])))
    for j in range(len(new)):
        for row in cp:
            new[j].append(row[j])
    return new


#
# This seems to be needed because copy.deepcopy() non sembra functionare
#
def copyCp(cp):
    "returns a copy of the cp array"
    return map(lambda row:map(lambda v:v, row), cp)

def mapCp(f, cp):
    "returns a new cp array with f applied to each member of cp"
    return map(lambda row,f=f:map(f, row), cp)

def texcpFromCp(cp, cp2):
    "tex coords of 2nd cp net are transferred to first"
    if len(cp)!=len(cp2) or len(cp[0])!=len(cp2[0]):
      quarkx.msgbox("transferTexcp dimension mismatch",2,4)
      return
    def maprow(row, row2):
        return map(lambda v, v2:quarkx.vect(v.xyz+v2.st), row, row2)
    return map(maprow, cp, cp2)

    
def listCp(cp):
    cp2 = []
    for row in cp:
        cp2.append(list(row))
    return cp2

#
# The basic idea here is that if the patch is sitting right over
#  the face, the three points p0, p1, p2 should get the patch .st
#  coordinates (0,0), (1,0) and (0, 1) respectively.
#
def texcpFromFace(cp, face, editor):
    "returns a copy of cp with the texture-scale of the face projected"
    #
    # Note special code, which inhibits recentering threepoints
    #
    p0, p1, p2 = face.threepoints(6)
    
    def axis(p, p0=p0):
        "turns a texp point into axis for computing b2 texcp's"
        return (p-p0).normalized/abs(p-p0)

    def project(v, p0=p0, (s_axis, t_axis)=map(axis, (p1, p2))):
        # note the wacko sign-flip for t
        return quarkx.vect(v.xyz + ((v-p0)*s_axis, -(v-p0)*t_axis))

    return mapCp(project, cp)

def texFromFaceToB2(b2, face, editor):
    "copies texture and scale from face to bezier"
    b2["tex"] = face["tex"]
    b2.cp = texcpFromFace(b2.cp, face, editor)

def b2FromCpFace(cp, name, face, editor):
    b2 = quarkx.newobj(name+':b2')
    b2.cp =  texcpFromFace(cp, face, editor)
    b2["tex"]=face["tex"]
    return b2

def cpFrom2Rows(row0, row2, bulge=None):
    "makes cp from top & bottom rows & fills in middle"
    if bulge is None:
      bulge=(0.5, 1.0)
    cp = [row0, None, row2]
    cp[1] = map(lambda x, y, h=bulge[0]:h*x+(1-h)*y, cp[0], cp[2]) 
    if bulge[1]!=1:
        c=reduce(lambda x,y:x+y,cp[1])/float(len(cp[1]))
        cp[1]=map(lambda v,c=c,b=bulge[1]:c+b*(v-c), cp[1])
    return cp


def b2From2Rows(row0, row2, texface, name, bulge=None, subdivide=1, subfunc=None):
     cp = cpFrom2Rows(row0, row2, bulge)
     if subdivide>1:
         cp = subdivideRows(subdivide,cp, subfunc)
     b2 = quarkx.newobj(name+":b2")
     b2["tex"] = texface["tex"]
     b2.cp = texcpFromFace(cp, texface, None)
     return b2


#
# If u and v are images of the parameter axes, this matrix
#  gives the associated linear mapping
#
def colmat_uv1(u,v):
    "returns column matrix of u, v, and z axis vector tuples"
    return quarkx.matrix((u[0], v[0], 0),
                         (u[1], v[1], 0),
                         (u[2], v[2], 1))

#
# bcp is a flat array of control points, cp an array `rolled up'
# along the columns.  The idea is to readjust the texture coordinates
# of the bcp to compensate for distortion along the columns
#
def undistortColumns(cp):
    ncp = copyCp(cp)   # this is what we return, after diddling it
    h, w = len(cp), len(cp[0])
    for j in range(w):  # for each column
#        squawk(" col %d"%j)
        #
        # get info about distances between cp's
        #
        lengths = []
        sum = 0
        for i in range(1, h):
            dist = abs(cp[i][j]-cp[i-1][j])
            sum = sum + dist
            lengths.append(sum)
        if sum == 0:
            sum = 1
        #
        # now rearrange texture cp's of bcp
        #
        start, end = cp[0][j], cp[h-1][j]
        texstart, texend = map(lambda v:quarkx.vect(v.s, v.t, 0), (start,end))
        texgap = texend-texstart
        #
        #  Now do it
        #
#        squawk('rockin')
        for i in range(1,h-1):
            s, t, x = (texstart + (lengths[i-1]/sum)*texgap).tuple
            ncp[i][j]=quarkx.vect(cp[i][j].xyz+(s, t))
#    squawk(`nbcp`)
    return ncp
      
def undistortRows(cp):
    cp = transposeCp(cp)
    cp = undistortColumns(cp)
    return transposeCp(cp)

# 2 case of working
def undistortColumnsCaseB(cp):
    ncp = copyCp(cp)   # this is what we return, after diddling it
    h, w = len(cp), len(cp[0])

    length = []
    bestlength = 0

    for j in range(w):  # for each column
        Locallengths = []
        sum = 0
        for i in range(1, h):
            dist = abs(cp[i][j]-cp[i-1][j])
            sum = sum + dist
            Locallengths.append(sum)
        if sum > bestlength:
            bestlength = sum
            length = Locallengths

    for j in range(w):  # for each column
        start, end = cp[0][j], cp[h-1][j]
        texstart, texend = map(lambda v:quarkx.vect(v.s, v.t, 0), (start,end))
        texgap = texend-texstart
        for i in range(1,h-1):
            s, t, x = (texstart + (length[i-1]/bestlength)*texgap).tuple
            ncp[i][j]=quarkx.vect(cp[i][j].xyz+(s, t))

    return ncp      
      
def undistortRowsCaseB(cp):
    cp = transposeCp(cp)
    cp = undistortColumnsCaseB(cp)
    return transposeCp(cp)

# 3 case of working
def UniformWrapCollumns(cp):
    ncp = copyCp(cp)   # this is what we return, after diddling it
    h, w = len(cp), len(cp[0])

    for j in range(w):  # for each column
        start, end = cp[0][j], cp[h-1][j]
        texstart, texend = map(lambda v:quarkx.vect(v.s, v.t, 0), (start,end))
        texgap = texend-texstart
        for i in range(1,h-1):
            s, t, x = (texstart + (float(i)/(h-1))*texgap).tuple
            ncp[i][j]=quarkx.vect(cp[i][j].xyz+(s, t))

    return ncp

def UniformWrapRows(cp):
    cp = transposeCp(cp)
    cp = UniformWrapCollumns(cp)
    return transposeCp(cp)
#
# Getting approximate tangent planes at control points.
#

#
# The idea here is that at odd-numbered and quilt-end points, you
#  take the actual derivatives, at intermedient end points you
#  take the average of the derivative in and the derivative out.
#
def dpdu(cp, i, j):
  h = len(cp)
  if i==0:
    return 2*(cp[1][j]-cp[0][j])
  elif i==h-1:
    return 2*(cp[i][j]-cp[i-1][j])
  else:
    return (cp[i+1][j]-cp[i-1][j])

def dpdv(cp, i, j):
  w = len(cp[0])
  if j==0:
    return 2*(cp[i][j+1]-cp[i][j])
  elif j==w-1:
    return 2*(cp[i][j]-cp[i][j-1])
  else:
    return cp[i][j+1]-cp[i][j-1]

def tanAxes(cp, i, j):
  return dpdu(cp, i, j).normalized, dpdv(cp, i, j).normalized

#
#  Derivative matrix for parameter->space mappings and
#    parameter->plane mappings, at corners.
#  Not defined at non-corners due to greater complexity and/or
#    ill-definition (crinkles=no deriv at even-indexed cp's)
#
def d5(cp, (i, j)):
    dSdu = dSdv = None
    if i==0:
        dSdu = cp[1][j]-cp[0][j]
    elif i==len(cp)-1:
        dSdu = cp[i][j]-cp[i-1][j]
    if j==0:
        dSdv = cp[i][1]-cp[i][0]
    elif j==len(cp[0])-1:
        dSdv = cp[i][j]-cp[i][j-1]
    return dSdu, dSdv  


#def faceTexFromCph(cph, face, editor):
def texPlaneFromCph(cph, editor):
    "projects texture-scale at cp handle to face, returning copy of face"
    b2 = cph.b2
    d5du, d5dv = d5(b2.cp, cph.ij)
    if d5du is None or d5dv is None:
        return None
    #
    # Derivatives of parameter->space and parameter->tex maps.
    # S for space, T for texture (cap so diff from patch coords)
    #
    dSdp = colmat_uv1(d5du.xyz, d5dv.xyz)
    dTdp = colmat_uv1((d5du.s, d5du.t, 1),
                      (d5dv.s, d5dv.t, 1))
    Mat = dSdp*~dTdp
    #
    # This mapping is the texture scale & offset (differential
    #   of texture->space mapping)
    #
    def mapping(t3, offset=b2.cp[0][0], Mat=Mat):
        texoffset = quarkx.vect(offset.s, offset.t, 0)
        return Mat*(quarkx.vect(t3)-texoffset)+quarkx.vect(offset.xyz)
    #
    # Apply the texture differential to origin & two axes of texture
    #   space.  Note wierdass sign-reversal (beaucoup de tah, Bill)
    #
    texp = map(mapping,((0,0,0),(1,0,0),(0,-1,0)))
    #
    # Now first project the texture onto a face tangent to the patch,
    #   then project it onto the face we want.
    #
    new = quarkx.newobj("face:f")
#    new = face.copy()
    new.setthreepoints(texp,1)
    new["tex"]=b2["tex"]
    new.setthreepoints(texp,2,editor.TexSource)
    return new

#
#   The counterclockwise traversal of the edges
#     supports using arithmetic to figure out how
#     to `rotate' things for patch-merger & knitting
#
P_FRONT = 0   # first column of patch
P_TOP = 1     # last row of patch 
P_BACK = 2    # last column of patch
P_BOTTOM = 3  # row 0 of patch


def RotateCpCounter1(cp):
    "returns a cp net where the old P_BACK is now P_TOP"
    ncp = []
    h = len(cp)
    w = len(cp[0])
    for j in range(w):
        ncp.append(map(lambda i,cp=cp,k=w-j-1:cp[i][k],range(h)))
    return ncp

def RotateCpCounter2(cp):
    ncp = []
    h = len(cp)
    for i in range(h):
      row = cp[h-i-1]
      row = list(row)
      row.reverse()
      ncp.append(row)
    return ncp

def RotateCpCounter(i, cp):
    if i==0:
        return copyCp(cp)
    i=i%4
    if i==0:
        return copyCp(cp)
    if i==1:
        return RotateCpCounter1(cp)
    if i==2:
        return RotateCpCounter2(cp)
    if i==3:
        return RotateCpCounter1(RotateCpCounter2(cp))

def twistedRows(cp1, cp2):
    lr, lc = len(cp1)-1, len(cp1[0])-1
    e1, e2 = cp1[0][lc], cp1[lr][lc]
    b1, b2 = cp2[0][0], cp2[lr][0]
    if abs(e1-b1)>abs(e1-b2) and abs(e2-b2)>abs(e2-b1):
       return 1
    return 0


def joinCp((tp1,X), cp1, (tp2,Y), cp2):
    "returns cp1 extended to include cp2, assumes preconditions"
#    squawk(`tp1-P_BACK`)
    cp1 = RotateCpCounter(P_BACK-tp1, cp1)
    cp2 = RotateCpCounter(P_FRONT-tp2, cp2)
#    squawk(`cp1`)
#    squawk(`cp2`)
    twisted = twistedRows(cp1,cp2)
    if twisted:
       cp1.reverse()
    ncp = map(lambda row1, row2:row1+row2[1:], cp1, cp2)
    if twisted:
       ncp.reverse()
    return RotateCpCounter(tp1-P_BACK, ncp)

def knitCp((tp1,X), cp1, (tp2,Y), cp2):
    "returns cp1 with edge knitted to cp2, assumes preconditions"
#    squawk(`tp1-P_BACK`)
    cp1 = RotateCpCounter(P_BACK-tp1, cp1)
    cp2 = RotateCpCounter(P_FRONT-tp2, cp2)
#    squawk(`cp1`)
#    squawk(`cp2`)
    last = len(cp1[0])-1
#    ncp = copyCp(cp1)
    twisted = twistedRows(cp1, cp2)
    if twisted:
      cp1.reverse()
    for i in range(len(cp1)):
        cp1[i][last]=cp2[i][0]
    if twisted:
      cp1.reverse()
    squawk('done')
    return RotateCpCounter(tp1-P_BACK, cp1)

def b2Point(u, p0, p1, p2):
    return u*u*(p0-2*p1+p2)+u*(-2*p0+2*p1)+p0
#    return (1-u)*(1-u)*p0 + 2*u*(1-u)*p1 + p2*u*u

#
# This does 1 seg with 3 cp's, the crappy way.
#
def subdivideLine(n, p0, p1, p2):
    "for n>=1, return 1+2n-tuple defining bezier quilt mesh line"
#    squawk('subdiv '+`n`)
    if n < 1: return
    if n==1: return [p0, p1, p2]
    retval = [p0]
    last = p0
    for i in range(n):
        q = b2Point((i+.5)/n, p0, p1, p2)
        p = b2Point((i+1.0)/n, p0, p1,p2)
        m = b2midcp(last,q,p)
        retval.append(m)
        retval.append(p)
        last = p
    return retval

#
# This is supposed to do a whole 1+2*n line
#
def subdivideRow(n, row, subfunc=None):
    if subfunc==None:
        subfunc=subdivideLine
    length = len(row)
    result = [row[0]]
    for i in range(0,length-1,2):
#       squawk(`i`)
#       squawk(`result`)
       line = subfunc(n, row[i], row[i+1], row[i+2])
#       squawk(`line`)
       result = result + subfunc(n, row[i], row[i+1], row[i+2])[1:]
#    squawk(`result`)
    return  result


def subdivideRows(n, cp, func=None):
    return map(lambda row,n=n,f=func:subdivideRow(n, row,f),cp)


def subdivideColumns(n, cp, func=None):
    return transposeCp(subdivideRows(n,transposeCp(cp),func))


#
# Attempt at a better circle approximation.
#  the idea is to think of the b2 curve as an approximation
#  to an image of a quarter-circle.
# 
# Derived from a suggestion by Alex Haarer.
#
def arcSubdivideLine(n, p0, p1, p2):
    mat = matrix_u_v(p0-p1, p2-p1)
    halfpi = math.pi/2.0
    points = [quarkx.vect(1,0,0)]
    last = points[0]
    lastdir = quarkx.vect(-1,0,0)
    for i in range(n):
        a = halfpi*(i+1)/n
        next = quarkx.vect(1.0-math.sin(a), 1.0-math.cos(a), 0)
        nextdir = quarkx.vect(-math.cos(a), math.sin(a), 0)
        mid = intersectionPoint2d(last,lastdir, next, nextdir)
        points.append(mid)
        points.append(next)
        last = next
        lastdir = nextdir
    points = map (lambda v,mat=mat,d=p1:d+mat*v, points)
    return points

#
# get i, j from index position (row-after-row listing)
#   think of a better name for this
#
def cpPos(p,b2):
    i, j = divmod(p, b2.W)
    return int(i), int(j)

def writecps(cp):
    debug('cp: ')
    for row in range(len(cp)):
      for  col in range(len(cp[row])):
        point = cp[row][col]
        try:
#          debug(" %d,%d: s: %6.2f t: %6.2f"%(row, col, cp[row][col][3], cp[row][col][4]))
           debug(" %d,%d: s: %6.2f, t: %6.2f"%(row, col, point.s, point.t))
        except:
          debug(" notexcoords")



# ----------- REVISION HISTORY ------------
#
#
#$Log: b2utils.py,v $
#Revision 1.22  2007/12/14 21:48:00  cdunde
#Added many new beizer shapes and functions developed by our friends in Russia,
#the Shine team, Nazar and vodkins.
#
#Revision 1.21  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.18  2002/12/29 04:18:33  tiglari
#transfer fixes from 6.3
#
#Revision 1.17.10.1  2002/12/29 02:57:59  tiglari
#texcpfromface now uses threepoints(6) to avoid recentering tex coords
#
#Revision 1.17  2001/03/20 11:01:51  tiglari
#credit added
#
#Revision 1.16  2000/12/30 05:27:11  tiglari
#cpPos function for mapping index position to i, j coordinates
#
#Revision 1.15  2000/09/04 21:24:23  tiglari
#added procedures for better circular arc segments
#
#Revision 1.14  2000/09/02 11:22:35  tiglari
#generalized subdivideRows/Columns to arbitrary quilts
#
#Revision 1.13  2000/08/23 12:12:34  tiglari
#Added support for edge knitting; fixed join bug
#
#Revision 1.12  2000/07/24 12:47:40  tiglari
#listCP function added
#
#Revision 1.11  2000/07/23 08:40:44  tiglari
#faceTexFromCph removed; texPlaneFromCph added
#
#Revision 1.10  2000/06/26 22:51:55  tiglari
#renaming: antidistort_rows/columns->undistortRows/Colunmns,
#tanaxes->tanAxes, copy/map/transposecp->copy/map/transposeCP
#
#Revision 1.9  2000/06/25 23:48:01  tiglari
#Function Renaming & Reorganization, hope no breakage
#
#Revision 1.8  2000/06/25 11:00:50  tiglari
#fixed antidistortion crash when sum=0.  still wrong but doesn't crash
#
#Revision 1.7  2000/06/22 22:38:37  tiglari
#added interpolateGrid (replacing an unused fn with a goofy name)
#
#Revision 1.6  2000/06/12 11:20:45  tiglari
#Redid antidistort_columns, added antidistort_rows
#
#Revision 1.5  2000/06/04 03:21:25  tiglari
#distortion reduction (elimination) for `rolled up' columns
#
#Revision 1.4  2000/06/03 18:01:28  alexander
#added cvs header
#
#Revision 1.3  2000/06/03 12:59:33  tiglari
#fixed arch duplicator maploading problem, hopefully
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#