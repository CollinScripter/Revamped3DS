
########################################################
#
#              Poly Merging Code
#
#  formerly in maptagside, now called from there
#
#  tiglari@planetquake.com, April 15, 2001
#
#######################################

#$Header: /cvsroot/quark/runtime/plugins/mergepolys.py,v 1.4 2005/11/10 18:09:03 cdunde Exp $

import quarkx
import quarkpy.mapentities
from tagging import *
from faceutils import *

def closenough(vtx,vtx1):
    if abs(vtx-vtx1) < 1:
        return 1
    else: return 0


def same_vertices(face,tagged):
    "face and tagged must have one vtx set which must be the same"
    facevtx = face.vertices[0]
    tagvtx = tagged.vertices[0]
    length = len(facevtx)
    if length!=len(tagvtx):
        return 0
    for fvtx in facevtx:
        for tvtx in tagvtx:
            if closenough(fvtx,tvtx):
                break
        else: return 0
    return 1
  
def useableby(face, poly):
    newface=face.copy()
#
#   wtf doesn't this work?
#
#   newpoly=poly.copy()
#   newpoly.appenditem(newface)
#   newpoly.rebuildall()
#   squawk(`len(newpoly.faces)`)
    newpoly = quarkx.newobj("test:p")
    for face2 in poly.faces:
        newpoly.appenditem(face2.copy())
    newpoly.appenditem(newface)
    for face2 in newpoly.faces:
#      squawk("checking")
        if newface==face2:
            return 1
    return 0


#
# poly1 can be merged with poly2 at face of poly1,
#   returning result or None
#
def mergeable(tagged, poly1, o):

    def noncoplanar(poly, face):
        for f in poly.faces:
            if coplanar(f, face):
               return 0
        return 1

    for face in o.faces:
        if len(face.faceof)!=1 or not coplanar(face,tagged): continue
        if face.normal*tagged.normal>0: continue
        if same_vertices(face,tagged): 
            new = quarkx.newobj(o.name)
            for oldface in o.subitems: # not faces, we don't mess with shared faces
                if oldface==face or oldface.type!=":f": continue
                new.appenditem(oldface.copy())
            #
            # the merged poly will be in o's group, so we need to copy
            # all the faces.  any facees used by the tagged faces's
            # poly that are actually used by o will not be ok.
            #
            for tagface in poly1.faces:
                if noncoplanar(o,tagface): # ys
                    new.appenditem(tagface.copy())
                    #
                    # If it can be added to o and still be used by
                    # o, then it changes the shape of o and merger 
                    # should not be enabled
                    #
          #          squawk("testing useability")
                    if useableby(tagface, o):  # if it can be added to
          #             squawk("passed")
                         return None
            return new

#
# merge a poly to one with a tagged face
#
def MergePolyClick(m):
    editor=mapeditor()
    if editor is None: return
    undo = quarkx.action()
    undo.exchange(m.o, m.result)
    undo.exchange(m.tagged.faceof[0], None)
    editor.ok(undo,"merge polys")

#
# makes menu item, put on menu in maptagside
#
def mergepoly(editor,o):
    item = qmenu.item("Merge Polys",MergePolyClick,"|This command can merge two brushes which `kiss' at a face, meaning that the faces have the same location, orientation, size and shape, but are oriented in opposite directions.\n\nTo use it, tag one of the kissing faces, then select the brush that contains the other.  If this menu item becomes enabled, the operation is then supposed to be able to combine the two brushes into one.  The selected brush will be `dominant', in that the resulting brush will be in its position of the group structure, and its textures and higher shared faces will be retained where relevant.\n\nIf the operation will change the overall shape, or create an invalid brush, this menu item is supposed to remain disabled.")
    item.state=qmenu.disabled
    tagged=gettagged(editor)
    if tagged is None or len(tagged.faceof)!=1:
        return item
    new = mergeable(tagged,tagged.faceof[0],o)
    if new is not None:
        item.tagged=tagged
#            item.face=face
        item.state=qmenu.normal
        item.result=new
        item.o=o
    return item


def MergePolysInGroup(group):
    newgroup = group.copy()
    done = 'done' # to be used as a loop-break exception
    while 1:
        try:
            faces=newgroup.findallsubitems("",":f")
            polys = newgroup.findallsubitems("",":p")
            for face in faces:
                if len(face.faceof)==1:
                    poly1 = face.faceof[0]
                    for poly2 in polys:
                        if poly2 is poly1:
                            continue
                        newpoly = mergeable(face, poly1, poly2)
                        if newpoly is not None:
                            poly2.parent.appenditem(newpoly)
                            poly2.parent.removeitem(poly2)
                            poly1.parent.removeitem(poly1)
                            raise done
        except done:
            pass
        else:
            break
            
    return newgroup

#
# merge the mergeable polys in a group.
#
def MergePolysClick(m):
    editor = mapeditor()
    if editor is None: return
    undo = quarkx.action()
    new = MergePolysInGroup(m.o)
    undo.exchange(m.o, new)
    editor.ok(undo,"merge polys in group")
    
#
# makes menu item, put on menu in maptagside
#
def groupmergepoly(editor,o):
    item = qmenu.item("Merge Polys",MergePolysClick,"|This command will try to merge all mergeable polys in the group.\n\mIt doesn't necessarily get the best answer, if you think you can do better, you can use Merge Polys on the face menu.")
    item.o=o
    return item

# $Log: mergepolys.py,v $
# Revision 1.4  2005/11/10 18:09:03  cdunde
# Activate history log
#
# Revision 1.3  2005/10/15 00:51:56  cdunde
# To reinstate headers and history
#
# Revision 1.1  2001/04/15 08:53:44  tiglari
# move merge poly code to mergepolys.py; add merge polys in group functionality
#

# ----------- REVISION HISTORY ------------
#$Log: mergepolys.py,v $
#Revision 1.4  2005/11/10 18:09:03  cdunde
#Activate history log
#
#