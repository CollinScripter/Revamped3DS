"""   QuArK  -  Quake Army Knife

The map editor's "Commands" menu (to be extended by plug-ins)
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"


#$Header: /cvsroot/quark/runtime/quarkpy/perspective.py,v 1.5 2005/10/15 00:47:57 cdunde Exp $

#
# Operations for creating boxes whose face-names reflect
#  their orientation in the view they're clicked on, plus
#  operations for building and manipulating dictionaries.
#  for accessing them.  Used for shape-from-box buildiers
#  in mb2curves, mapbrushcurves, and mapstair.
#

import quarkx
from maputils import *

# return X, Y, Z axes:
#  X to right on screen
#  Y away from viewer (toward would mean lh coord sys)
#  Z up on screen
#
#  The idea is that these should equal map coordinates in Quark's
#    default side-on view.  All the sign-flips & axis swapping
#    is kinda confusing.
#
def perspectiveAxes(view=None):
    try:
        if view is None:
            view = quarkx.clickform.focus  # gets the mapview clicked on
        x, z = view.vector("x"), -view.vector("y")
#  axes = view.vector("x"), -view.vector(view.screencenter), -view.vector("y")
        return map(lambda v:v.normalized, (x, (x^z), z))
    except:
        return map(lambda t:quarkx.vect(t), ((1,0,0), (0,-1,0), (0,0,1)))

#
# return front, back, left, right, top, bottom w.r.t. view
#  perspective if possible, otherwise None.
#
def perspectiveFaceDict(o, view):
    faces = o.subitems
    if len(faces)!=6:
        return None
    axes = perspectiveAxes(view)
    pool = faces[:]
    faceDict = {}
    for (label, ax, dir) in (('f',1, 1)
                            ,('b',1,-1)
                            ,('u',2, 1)
                            ,('d',2,-1)
                            ,('r',0, 1)
                            ,('l',0,-1)):
        chosenface = pool[0]
        axis = axes[ax]*dir
        chosendot = chosenface.normal*axis
        for face in pool[1:]:
            if face.normal*axis>chosendot:
                chosenface=face
                chosendot=face.normal*axis
        faceDict[label]=chosenface
        pool.remove(chosenface)
    return faceDict

def faceDict(o):
    result = {}
    for (key, name) in (('f','front')
                       ,('b','back' )
                       ,('u','up'   )
                       ,('d','down' )
                       ,('r','right')
                       ,('l','left' )):
        result[key]=o.findshortname(name)
    return result

def perspectiveRename(o, view):
    "renames the faces of a 6-face polyhedron in accord with perspective of last-clicked-on view"
    dict = perspectiveFaceDict(o, view)
    if dict is None:
        return None
    newpoly = quarkx.newobj(o.name)
    for (key, name) in (('f','front')
                       ,('b','back' )
                       ,('u','up'   )
                       ,('d','down' )
                       ,('r','right')
                       ,('l','left' )):
        newface = dict[key].copy()
        newface.shortname = name
        newpoly.appenditem(newface)
    return newpoly

def othervect(vector, vecpair):
  "returns member of vecpair that is different from vector"
  if (vector-vecpair[0]):
    return vecpair[0]
  else:
    return vecpair[1]

def splitpoints(edge1, edge2):
  "if edge1 & edge2 share a point, returns shared, edge1 non-shared, edge2 non-shared"
  common = shared_vertices([edge1, edge2])[0]
  if common is None:
    return None
#  squawk("removeing")
  first = othervect(common, edge1)
#  squawk("first")
  second = othervect(common,edge2)
#  squawk("second")
#  squawk(`first`+"--"+`second`)
  return common, first, second

def pointdict(dict):
  points = {}
  front, up, left = dict["f"], dict["u"], dict["l"]
#  squawk('ful')
  topfront = shared_vertices([front, up])
#  squawk('tf')
  topleft = shared_vertices([left, up])
  points["tlf"], points["trf"], points["tlb"]=splitpoints(topfront, topleft)
  right, down, back = dict["r"], dict["d"], dict["b"]
  frontright = shared_vertices([right, front])
  bottomfront = shared_vertices([front,down])
#  tagedge(frontright[0], frontright[1], editor)
  points["brf"], points["blf"], points["trf"] = splitpoints(bottomfront, frontright)
  bottomback = shared_vertices([down, back])
  rightback = shared_vertices([right, back])
  points["brb"], points["trb"], points["blb"] = splitpoints(rightback, bottomback)
  return points


#
# Might be better to code this with remove? Except that
#  I suspect that list.remove won't work for vectors.
#
def shared_vertices(vtxlists):
  "returns list of vertices that appear in every list of vtxlists"
  first = vtxlists[0]
  for vtxlist in vtxlists[1:]:
    second=[]
    for vtx in first:
      for vtx2 in vtxlist:
        if not(vtx-vtx2):
           second.append(vtx)
           break
    first=second
  return first


def vtxlistdict(faceDict,o):
    "returns a dict in which the keys are associated with vertex-lists"
    result = {}
#    squawk('doing '+`o.shortname`)
    try:
        for key in faceDict.keys():
#            squawk('key: '+`key`+'; '+faceDict[key].shortname)
            result[key]=faceDict[key].verticesof(o)
    except (AttributeError):
        return None
    return result


def pointdict_vflip(pd):
    "flips the pointdict upside down"
    flipdict = {'t':'b', 'b':'t'}
    pd2 = {}
    for key in pd.keys():
        key2 = "%s%s%s"%(flipdict[key[0]],key[1],key[2])
        pd2[key2] = pd[key]
    return pd2

def pointdict_hflip(pd):
    "flips the pointdict left-to-right"
    flipdict = {'l':'r', 'r':'l'}
    pd2 = {}
    for key in pd.keys():
        key2 = "%s%s%s"%(key[0],flipdict[key[1]],key[2])
        pd2[key2] = pd[key]
    return pd2

def pointdict_rflip(pd):
    "rotates pointdict so that front becomes top"
    pd2 = {}
    pd2["trf"], pd2["tlf"] = pd["brf"], pd["blf"]
    pd2["trb"], pd2["tlb"] = pd["trf"], pd["tlf"]
    pd2["brb"], pd2["blb"] = pd["trb"], pd["tlb"]
    pd2["brf"], pd2["blf"] = pd["brb"], pd["blb"]
    return pd2

def facedict_rflip(fd):
    fd2 = {}
    for key in ('l', 'r'):
        fd2[key]=fd[key]
    fd2['u']=fd['f']
    fd2['b']=fd['u']
    fd2['d']=fd['b']
    fd2['f']=fd['d']
    return fd2

def facedict_spin(fd):
    fd2 = {}
    for key in ('u', 'd'):
        fd2[key]=fd[key]
    fd2['f']=fd['b']
    fd2['b']=fd['f']
    fd2['r']=fd['l']
    fd2['l']=fd['r']
    return fd2

def facedict_fflip(fd):
    "flips facedict front-back"
    fd2 = {}
    for key in ('u','d','r','l'):
        fd2[key]=fd[key]
    fd2['f']=fd['b']
    fd2['b']=fd['f']
    return fd2

def facedict_hflip(fd):
    "flips the facedict left-to-right"
    fd2 = {}
    for key in ('f','b','u','d'):
        fd2[key]=fd[key]
    fd2['r']=fd['l']
    fd2['l']=fd['r']
    return fd2

def facedict_vflip(fd):
    "flips the facedict upside-down"
    fd2 = {}
    for key in ('f','b','r','l'):
        fd2[key]=fd[key]
    fd2['u']=fd['d']
    fd2['d']=fd['u']
    return fd2

#$Log: perspective.py,v $
#Revision 1.5  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.2  2002/08/09 10:00:11  decker_dk
#A minor consistency correction for facedict_*flip()
#
#Revision 1.1  2001/02/14 10:06:47  tiglari
#extracted from mb2curves, etc
#
