
########################################################
#
#                         Snap Object Plugin
#                          v1.0, Aug 2001
#                      works with Quark 6.3        
#
#
#                    by tiglari@hexenworld.com     
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & improvements to tiglari@planetquake.com
#
###
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/mapsnapobject.py,v 1.7 2005/11/10 17:50:28 cdunde Exp $



Info = {
   "plug-in":       "Snap objects",
   "desc":          "Snapping objects to faces",
   "date":          "6 Aug 2001",
   "author":        "tiglari",
   "author e-mail": "tiglari@planetquake.com",
   "quark":         "Version 6.3" }


import quarkx

import mapmadsel
import quarkpy.mapentities
import quarkpy.dlgclasses
from tagging import *
from quarkpy.maputils import *



#
# WTF ---
#
# First the function that does the real work is defined, then the interface
# (a popup menu of parents with a Live Button Dialog) is set up.
#

#
# --  The Function that Does the Real Work
#
# Returns newface, newobj, rotated and shifted in accordance with the following
#  rather complex scheme.  The idea behind all of this is so that if an object has
#  to be rotated to make the selected plane parallel to the tagged one, this
#  rotation will preserve vertical orientation to the greatest extent possible,
#  that is the object won't tilt unnecessarily in intuitively annoying ways.
#
# Or so I hope.  This is pretty complicated :)
#
# The idea is that the object is swivelled around the Z axis and the tilted around
#  a horizontal axis (both thru its center) so that the selected face is paralell
#  to the tagged one, then the object is moved so that the selected face is the
#  specified distance from the tagged one (along the latter's normal).
#
# The rotations are determined as follows:
#
#   if both planes are horizontal (parallel to the xy plane), no rotations are performed
#
#   if one of the planes is horizontal, no swivelling is performed, but the
#     object is tilted around an axis paralell to a horizontal axis lying in
#     the non-horizontal plane, so that the two planes become parallel.
#
#   otherwise, horizontal axes are found in both planes (the bestaxes function).
#     then the object is swivelled so that these axes are parallel, and then the
#     object is tilted, around the now-swivelled horizontal axis in the selected
#     face, so that the two planes are parallel.
#
# Well actually none of these rotations are actually performed yet, rather a rotation
#     matrix has been assembled and is finally applied to the object.
#
# OK, now, finally, the object is translated along the now identically opposite noramls
#     of the two planes to be the specified distance/

def snapObjectToPlane(face, object, tagged, separation, doswivel=1, dotilt=1, doshift=1):

    #
    # FIXME: things sometimes get spun around 180 from what they
    #  ought to be, if tagged face is horizontal
    #
    facehoriz=face.axisbase()[0]
    taggedhoriz=tagged.axisbase()[0]
    
    if math.fabs(face.normal*Z_axis)==1 :
        doswivel=0
    
    face2, object2 = face.copy(), object.copy()
    idmat = quarkx.matrix(X_axis, Y_axis, Z_axis)
    if doswivel:
        #
        # think of the taggedhoriz as the x axis, facehoriz
        #  is then some vector making an angle with it, use
        #  atan2 to recover the actual angle
        #
        yax = (Z_axis^taggedhoriz).normalized
        swivelangle=-math.atan2(facehoriz*yax,facehoriz*taggedhoriz)+math.pi
        swivelmat=matrix_rot_z(swivelangle)
    else:
        swivelmat = idmat
    if dotilt:
        facenormal=-swivelmat*face.normal
        #
        # Same idea, but this time we're interested
        #  in the angle that the negative normal of the
        #  tilted makes with the normal of the tagged one
        #
        yax=tagged.normal^taggedhoriz
#        debug('yaxx')
        tiltangle=math.atan2(yax*facenormal,tagged.normal*facenormal)
#        debug('horiz '+`facehoriz`)
        tiltmat=ArbRotationMatrix(taggedhoriz, tiltangle)
    else:
        tiltmat=idmat
    mat = tiltmat*swivelmat
    object2.linear(object.origin,mat)
    face2.linear(object.origin,mat)
#    object2.linear(object.origin,tiltmat)
#    face2.linear(object.origin,tiltmat)
#    debug('linear')
    if doshift:
        pt1 = projectpointtoplane(object2.origin,tagged.normal,face2.dist*face2.normal,tagged.normal)
        pt2 = projectpointtoplane(object2.origin,tagged.normal,tagged.dist*tagged.normal,tagged.normal)
#        debug('separation '+`separation`)
        diff = pt2+separation*tagged.normal-pt1
        object2.translate(diff)
        face2.translate(diff)
    return face2, object2


# --- The Interface
#
class SnapObjectDlg (quarkpy.dlgclasses.LiveButtonDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (220,170)
    dfsep = 0.35

    dlgdef = """
        {
        Style = "9"
        Caption = "Snap Object to Plane"

        swivel: = {
          Typ = "X"
          Hint = "If this is checked, the object is swivelled around the Z-axis so that horizontal lines in the tagged and selected faces are parallel"
        }

        orient: = {
          Typ = "X"
          Hint = "if this is checked, the object is swivelled and then tilted so the tagged and selected faces are parallel." 
        }

        shift: = {
          Typ = "X"
          Hint = "if this is checked, the object is shifted so that the selected plane is the distance specified in 'separate' from the tagged plane."
        }

        separation: = {
          Typ = "EF00001"
          Hint = "The separation from the tagged face that the object is moved to, if shift is checked"
        }
        
        sep: = { Typ="S" Txt=""}

        buttons: = {
          Typ = "PM"
          Num = "1"
          Macro = "snapobject"
          Caps = "S"
          Txt = "Actions:"
          Hint1 = "Perform the specified movement"
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

    def snap(self):
        pack=self.pack
        #
        # We need to get a snapped copy of the face so that if we want to adjust
        #   the parameters we can.
        #
        newface, newobj = snapObjectToPlane(pack.face, pack.current, pack.tagged, pack.separation, pack.doswivel, pack.dotilt, pack.doshift)
        undo=quarkx.action()
        undo.exchange(pack.current, newobj)
        pack.editor.ok(undo,'snap object to plane')
        pack.face, pack.current = newface, newobj
        
         


def macro_snapobject(self, index=0):
    editor = mapeditor()
    if editor is None: return
    if index==1:
        editor.dlg_snapobject.snap()

quarkpy.qmacro.MACRO_snapobject = macro_snapobject


#
# These are for when you want the usual value of a checkbox option to
#   checked (so that it will come up that way first time no fuss
#   in defaults.qrk)
#
def readFlippedSetupCheckVal(attr):
    if quarkx.setupsubset(SS_MAP, "Options")[attr]=="1":
        return ""
    else:
        return "1"
        
def writeFlippedSetupCheckVal(attr, val):
    if val=="1":
        quarkx.setupsubset(SS_MAP, "Options")[attr]=""
    else:
        quarkx.setupsubset(SS_MAP, "Options")[attr]="1"


def readWithDefault(attr,default):
    val = quarkx.setupsubset(SS_MAP, "Options")[attr]
    if val is None:
        return default
    return val
     
def writeWithDefault(attr, val, default):
    if val==default:
        quarkx.setupsubset(SS_MAP, "Options")[attr]=""
    else:
        quarkx.setupsubset(SS_MAP, "Options")[attr]=val

SMALL = .0001

def snapFunc(o, current, editor):
    
    class pack:
        "stick stuff here"
    pack.current=current
    pack.face=o
    pack.tagged = gettaggedplane(editor)
    pack.editor=editor
    pack.separation,=readWithDefault('snapobject_separation',(1,))

    def setup(self, pack=pack, editor=editor):
        
        src = self.src
        self.pack=pack
        for (dattr, oattr) in (('swivel','snapobject_noswivel'), ('orient','snapobject_noorient'), ('shift','snapobject_noshift' )):
            src[dattr]=readFlippedSetupCheckVal(oattr)
        
        src['separation']=readWithDefault('snapobject_separation',(1,))
        src['separation'] = pack.separation,
        pack.doswivel=pack.dotilt=pack.doshift=0
        if src['swivel']:
            pack.doswivel=1
        if src['orient']:
            pack.dotilt=1
            pack.doswivel=1
        if src['shift']:
            pack.doshift=1
        
    def action(self, pack=pack, editor=editor):
        src = self.src
        for (dattr, oattr) in (('swivel','snapobject_noswivel'), ('orient','snapobject_noorient'), ('shift','snapobject_noshift' )):
            writeFlippedSetupCheckVal(oattr,src[dattr])
        
        writeWithDefault('snapobject_separation',src['separation'], (1,))
        pack.separation,=src['separation']

    SnapObjectDlg('snapobject',editor,setup,action)
    
#
# Build the 'select a parent' menu
#
def snapItems(current, editor, restricted):
    name = current.shortname
    
    def snapClick(m, current=current, editor=editor):
        snapFunc(editor.layout.explorer.sellist[0], current, editor)
    
    snapItem=qmenu.item("Snap to tagged",snapClick)
    snapItem.state=qmenu.default
    
    item = qmenu.popup(name,[snapItem],None,"|This is the name of some group or brush entity that contains what you have selected.\n\nLook at its submenu for stuff you can do!\n\nIf there's a bar in the menu, then the `Restrict Selections' menu item is checked, and you can only select stuff above the bar.")
    item.menuicon = current.geticon(1)
    item.object = current
    return item

def parentSnapPopup(o, editor):
    parentSnap = qmenu.popup("&Snap Parent", hint = "|The submenu that appears comprises the currently selected object at the top, and below it, the map objects (polys, groups & brush entities) that are above it in the group tree-structure.\n\nIf you put the cursor over one of these, you will get the snap-to-selected face command.")
    item = mapmadsel.buildParentPopup(o, parentSnap, snapItems, editor)
    tagged=gettaggedplane(editor)
    if tagged is None:
         item.state=qmenu.disabled
    return item


#
# Put it on the face menu
#  (actually no, we import into maptagside)
#
#def snapfacemenu(o, editor, oldmenu=quarkpy.mapentities.FaceType.menu.im_func):
#    "the new right-mouse menu for faces"
#    menu = oldmenu(o, editor)
#
#    menu[:0] = [parentSnapPopup(o,editor),
#
#                quarkpy.qmenu.sep]
#    return menu  

#quarkpy.mapentities.FaceType.menu = snapfacemenu


# ----------- REVISION HISTORY ------------
#$Log: mapsnapobject.py,v $
#Revision 1.7  2005/11/10 17:50:28  cdunde
#Activate history log
#
#