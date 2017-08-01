"""   QuArK  -  Quake Army Knife Bezier shape makers

"""

# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"

########################################################
#
#                          Caulk Plugin
#                          v1.0, Aug 2000
#                      works with Quark 6.0b2
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

#$Header: /cvsroot/quark/runtime/plugins/mb2caulk.py,v 1.7 2005/10/16 18:48:04 cdunde Exp $

Info = {
   "plug-in":       "Caulk shader plugin",
   "desc":          "Pasting caulk shader on stuff",
   "date":          "20 Aug 2000",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Version 6.0b2" 
}


import quarkx
import quarkpy.mapmenus
from quarkpy.maputils import *

from quarkpy.b2utils import *
from tagging import *

def gettaggedcorners(editor):
    face = gettaggedface(editor)
    if face is not None:
        vtxes = face.vertices
        if len(vtxes)==1:  # don't do this with shared faces
            return vtxes[0]
    b2cp = gettaggedb2cp(editor)
    if b2cp is not None:
        cp = b2cp.b2.cp
        m, n = len(cp)-1, len(cp[0])-1
        #
        # clockwise traversal
        #
        return cp[0][0], cp[0][n], cp[m][n], cp[m][0]
    return None


def cleanpoly(poly):
    used = poly.faces
    for face in poly.subitems[:]:
        if not face in used:
            poly.removeitem(face)


#
# project outline (a vertex-cycle) onto face of poly
# if there's no impingement, return None.
# otherwise return a poly or group, suitablefor replacing
# original poly
#
def projectOutlineTex(face,poly,outline,tex):
    "returns None, if outline doesn't project onto face of poly"
    "a poly with texture replaced, or a group where member has replement"
    undo = quarkx.action()
    core = poly.copy()    # the `central' piece that will get the tex
    periphery = []    # the surrounding pieces that don't
    for i in range(len(outline)):
        #
        # kewl Python feature: when index=-1, last element of
        #    list is picked
        #
        p0, p1 = outline[i-1], outline[i]
        edge = quarkx.vect((p0-p1).xyz)
        normal,dist = face.normal, face.dist
        p3 = projectpointtoplane(p0,normal,dist*normal,normal)
        cutter = face.copy()
        cutter.distortion(edge^normal,p3)
        offcut = core.copy()
        cutter2 = cutter.copy()
        cutter2.swapsides()
        offcut.appenditem(cutter)
        if not offcut.broken:
            cleanpoly(offcut)
            core.appenditem(cutter2)
            periphery.append(offcut)
    cleanpoly(core)
    for aface in core.faces:
       if not (aface.normal-normal):
           aface["tex"]=tex
           break
    if periphery:
        result=quarkx.newobj(poly.shortname+'_group:g')
        result.appenditem(core)
        for item in periphery:
            result.appenditem(item)
        return result
    return core



def tagmenu(o, editor, oldfacemenu = quarkpy.mapentities.FaceType.menu.im_func):
    "the new right-mouse for sides"
    menu = oldfacemenu(o, editor)
    tagpop = findlabelled(menu, 'tagpop')
    corners = gettaggedcorners(editor)

    def nodrawclick(m,face=o,editor=editor,corners=corners):
        faces = face.faceof
        if faces[0].type==":f":  # unused face
            return
        if len(faces)>1:
            quarkx.msgbox("Sorry, doing this to shared faces is too hard for me today",
              MT_INFORMATION, MB_OK)
            return
        poly = faces[0]
        #
        # FIXME: get the name of the caulk texture out of
        #   the game config files.
        #
        new = projectOutlineTex(face, poly, corners, 'common/caulk')
        if new is not None:
            undo = quarkx.action()
            undo.exchange(poly, new)
            editor.ok(undo, "caulk from tagged")

    nodraw = qmenu.item("Caulk from tagged",nodrawclick)
    if corners is None:
        nodraw.state=qmenu.disabled
    tagpop.items.append(nodraw)
    return menu

quarkpy.mapentities.FaceType.menu = tagmenu


# ----------- REVISION HISTORY ------------
#$Log: mb2caulk.py,v $
#Revision 1.7  2005/10/16 18:48:04  cdunde
#To remove letters referring to depository folders that
# made filtering them out for distribution harder to do
#
#Revision 1.6  2005/10/15 00:51:56  cdunde
#To reinstate headers and history
#
#Revision 1.3  2001/03/01 19:13:54  decker_dk
#Corrected log and header tags.
#
#