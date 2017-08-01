"""   QuArK  -  Quake Army Knife

Finds faces that don't have three integral threepoints, or vertices that
can be used as threepoints, and fixes them.  A preliminary of something that
might go into QuArK 6.3e if it seems stable and useful enough, in spite
of the supposed feature-freeze for Q6.3.  Maps created with 6.2 containing
dragged around textures are likely to provide work for this plugin.

Puts Find Non-integral Faces commands on search menu; this produces a multiselection
 of such faces

If a group has specific 'nonintegral' (value 1), then any non-integral faces it
  contains will be ignored (maybe wanted for detail brushes, exotic decorations
  or something).

Puts Integralize Faces command on commands menu; this forces very close threepoints
  to integer, or uses integral vertexes as threepoints if possible.

"""
#
# Copyright (C) 1996-2002 The QuArK Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapfindnonintegralfaces.py,v 1.10 2009/09/25 22:55:56 danielpharos Exp $



Info = {
   "plug-in":       "Find & fix non-integral faces",
   "desc":          "finds faces that don't have three integral threepoints or vertices, tries to fix them",
   "date":          "29 Dec 2002",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Version 6.3c or later (**not** 6.2)" }


from quarkpy.maputils import *
import quarkpy.mapmenus
import quarkpy.mapcommands
import quarkpy.mapsearch
import quarkpy.dlgclasses

import quarkx

def is_integral_float(p):
    if p==int(p):
       return 1
    debug(" p:  %s"%p)

def is_integral_vect(p):
    if not is_integral_float(p.x):
        return 0
    if not is_integral_float(p.y):
        return 0
    if not is_integral_float(p.z):
        return 0
    return 1
    
SMALL = 0.0001

def oneof(v, vlist):
    for v2 in vlist:
        if abs(v-v2)<SMALL:
            return 1

def inNonIntegralGroup(face):
    parent = face.treeparent
    while parent is not None:
        if parent['nonintegral']:
            return 1
        parent = parent.treeparent

def findNonIntegralFaces(m):
    editor=mapeditor()
    if editor is None: return
    results = []
    for face in editor.Root.findallsubitems("",":f"):
        if inNonIntegralGroup(face):
            continue
        icount = 0
        threepoints = face.threepoints(0)
        for p in threepoints:
            if is_integral_vect(p):
                icount = icount+1
        if icount<3:
            debug("face %s, threepoints: %s"%(face.shortname, threepoints))
            results.append(face)
    if len(results)>0:
        editor.layout.explorer.sellist=results
        editor.invalidateviews()
    else:
        quarkx.msgbox("None found",MT_INFORMATION,MB_OK)
        

def integralize_vect(v):
    return quarkx.vect(round(v.x), round(v.y), round(v.z))

def integralizeFace(face):
    points = []
    #
    # first make sure that it isn't OK as is
    #
    for p in face.threepoints(0):
        if is_integral_vect(p):
            points.append(p)
    if len(points)==3:
        return # no need to do anything so return nothing to do
    #
    # now see if a bit of forcing will do the trick
    #
    points = []
    for p in face.threepoints(0):
        intp = integralize_vect(p)
#        debug('p: %s, intp: %s'%(p,intp))
        if abs(p-intp)<SMALL:
            points.append(intp)
    newface = face.copy()
    if len(points)<3:
        #
        # Now see if we have threepoint vertices that can be used
        #
        for vtxlist in face.vertices:
            for vtx in vtxlist:
                debug('vtx: %s'%vtx)
                if is_integral_vect(vtx):
                    if not oneof(vtx,points):
                        debug(' appended')
                        points.append(vtx)
                if len(points)==3:
                    break
        if len(points)<3:
            debug(' not enough points')
            return # can't do nothing so return nothing to do
        d1 = points[1]-points[0]
        d1.normalized
        d2 = points[2]-points[0]
        d2.normalized
        length = abs(d1+d2)
        if length<SMALL or math.fabs(2-length)<SMALL:
            debug('colinear')
            return # can't do anything because points colinear
        normal=d1^d2
        if abs(normal-face.normal)<SMALL:
            newface.setthreepoints((points[0], points[1], points[2]), 0)
        else:
            newface.setthreepoints((points[0], points[2], points[1]), 0)
    newface.setthreepoints(face.threepoints(2),2)
    return newface
        

def integralizeFaces(m):
    editor=mapeditor()
    if editor is None: return
    undo=quarkx.action()
    sel = editor.layout.explorer.sellist
    if sel == []:
        quarkx.msgbox("Nothing selected", MT_INFORMATION, MB_OK)
        return
    changed = []
    for face in sel:
        newface = integralizeFace(face)
        if newface is not None:
            changed.append(newface)
            undo.exchange(face,newface)
    if changed==[]:
        quarkx.msgbox("Couldn't fix nuthin', all too hard", MT_INFORMATION, MB_OK)
        return
    editor.ok(undo, "integralize faces")
    quarkx.msgbox("integralized %d faces"%len(changed), MT_INFORMATION, MB_OK)
    editor.layout.explorer.sellist=changed
    editor.invalidateviews()
        

quarkpy.mapsearch.items.append(qmenu.item('Find &Non-integral Faces', findNonIntegralFaces,
 "|Find Non-integral Faces:\n\nThis finds faces that don't have integral threepoints.\n\nUse integralize Selected Faces on the command menu to try to automatically fix them.\n\nIf you want a particular group to be allowed to contain faces with non-integral threepoints, give it a nonintegral specific with a value such as 1.|intro.mapeditor.menu.html#searchmenu"))

quarkpy.mapcommands.items.append(qmenu.item('Integralize Selected Faces', integralizeFaces,
 "|Integralize Selected Faces:\n\nIf faces without integral threepoints have enough integral vertices to be used as threepoints, changes the face to use them (also forces nearly integral ones).\n\nSelects the ones it changes, for checking.\n\nUse Find Non-integral Faces on the search menu to find suitable victims.\n\nResearch and fix the remaining ones by hand.|intro.mapeditor.menu.html#orientation"))





# ----------- REVISION HISTORY ------------
# $Log: mapfindnonintegralfaces.py,v $
# Revision 1.10  2009/09/25 22:55:56  danielpharos
# Added some missing import-statements.
#
# Revision 1.9  2009/07/22 09:46:46  danielpharos
# Added missing import statement.
#
# Revision 1.8  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.5  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.4  2003/03/21 06:28:52  cdunde
# To correct typo error
#
# Revision 1.2  2003/01/02 22:36:26  tiglari
# transferred from rel-c63a branch
#
# Revision 1.1.2.1  2003/01/01 06:54:10  tiglari
# added to 6.3 in spite of feature-freeze, due to importance
#
#
