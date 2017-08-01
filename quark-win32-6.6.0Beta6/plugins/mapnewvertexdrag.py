"""   QuArK  -  Quake Army Knife

Start of plugin for advance vertex-dragging
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapnewvertexdrag.py,v 1.4 2005/11/10 17:50:28 cdunde Exp $

Info = {
   "plug-in":       "Advanced vertex dragging",
   "desc":          "Advanced vertex dragging",
   "date":          "30 Jan 2003",
   "author":        "tiglari, mbassie",
   "author e-mail": "tiglari@planetquake.com, groups.yahoo.com/group/quark-python",
   "quark":         "Version 6.3" }

#
# The reason for doing this is a plugin is that everything in the plugins
# folder whose name begins with 'map' gets loaded when the map editor
# starts up, whereas stuff in quarkpy is only loaded when some plugin
# imports it.
#

import quarkx
from quarkpy.maputils import *
import quarkpy.maphandles

#
# get the original version; the im_func is a bit of mumbo-jumbo
#  needed to pass around a method as an independent object (a function)
#
oldvertexdrag = quarkpy.maphandles.VertexHandle.drag.im_func

#
# note the final default argument, this and the previous line could have
#  been combined into one.
#
def newvertexdrag(self, v1, v2, flags, view, oldvertexdrag=oldvertexdrag):
    if quarkx.keydown('N') != 1:
        #
        # if the special key isn't being held down, use the old version
        #
        return oldvertexdrag(self, v1, v2, flags, view)

    # 
    # functional new code goes here, for now we just write something to the
    #  console and make a copy of the original poly
    #
    newpoly = self.poly.copy()
    delta = (v2-v1)
    newpoint = self.pos+delta
    

    #  Loop through faces
    for f in newpoly.faces:
        faceverts = []
        newfaces = []

    #  Get vertices for each valid face
        vertices = f.verticesof(newpoly)       # fetch vertices for polygon 'f'
        for i in range(len(vertices)):         # loop through vertices
            if not (vertices[i]-self.pos):     # if found self
                faceverts.extend(vertices[i+1:len(vertices)]) # add all vertices from self
                faceverts.extend(vertices[0:i]) # add all vertices before self
	
                #  check if self is coplanar with all other vertices. If so, just recalculate
                if abs(v2*f.normal-f.dist) < epsilon:
                    break
                    #debug('Still seems to be in the same face')
                #  If just 3 vertices, recalculate face, else check
                elif (len(faceverts)==2):
                    #debug('Face only has 3 vertices')
                    newface=f.copy()
                    newface.setthreepoints((newpoint,faceverts[0],faceverts[1]),0)
                    newfaces.append(newface)
                #  If more than 3 vertices
                else:
                    #debug('Face has %d+1 vertices' % len(faceverts))
                    #  If moving outward, split face in tris and replace
                    if (delta*f.normal) < 0:
                        newface=f.copy()
                        newface.setthreepoints((newpoint,faceverts[0],faceverts[-1]),0)
                        newfaces.append(newface)
                        newface=f.copy()
                        newface.setthreepoints((faceverts[0],faceverts[1],faceverts[2]),0)
                        newfaces.append(newface)

                    #  If moving inward, drop self from current face, and generate new tri with neighbours
                    else:
                        for j in range(len(faceverts)-1):
                            newface=f.copy()
                            newface.setthreepoints((newpoint,faceverts[j],faceverts[j+1]),0)
                            newfaces.append(newface)

		#Remove old face and replace with new ones.
                newpoly.removeitem(f)
                for j in range(len(newfaces)):
                    newface=newfaces[j]
                    if (newface.normal*f.normal) < 0: #reset face normals if
                        newface.swapsides()
                    newpoly.appenditem(newface)
                    
    #Return old polygon, new polygon
    return [self.poly], [newpoly]

#
# now set the function as a replacement for the original method
#
quarkpy.maphandles.VertexHandle.drag = newvertexdrag

# ----------- REVISION HISTORY ------------
#$Log: mapnewvertexdrag.py,v $
#Revision 1.4  2005/11/10 17:50:28  cdunde
#Activate history log
#
#

