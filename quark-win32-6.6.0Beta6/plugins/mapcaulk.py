"""   QuArK  -  Quake Army Knife Bezier shape makers

"""

# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"

########################################################
#
#                          Caulk Plugin
#                          v1.0, Jan 2003
#                      works with Quark 6.3
#
#
#                    by tiglari@planetquake.com
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to the QuArK
#   Community. (It's free software, just like Quark itself.)
#
#   Please notify bugs & improvements to tiglari@planetquake.com
#   or http://groups.yahoo.com/group/quark-python
#
###
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/mapcaulk.py,v 1.6 2007/02/03 00:40:19 cdunde Exp $

Info = {
   "plug-in":       "Caulk plugin",
   "desc":          "Caulking tthings",
   "date":          "Jan 26 2003",
   "author":        "tiglari",
   "author e-mail": "tiglari@planetquake.com",
   "quark":         "Version 6.3" 
}

#
# FIXME: this plugin should incorporate the contents of mb2caulk.py,
#  which should be abolished, since the workings of this plugin are
#  triggered by the presence of a CaulkTexture in the game config,
#  whereas the other one is triggered less soundly, by the presence
#  of patch-support.  The change should be made in the main branch,
#  but not in 6.3, at least yet.
#

import quarkx
import quarkpy.mapentities
import tagging
from quarkpy.maputils import *

#
# Caulk all-but-selected faces of poly
#


def polymenu(o, editor, oldmenu=quarkpy.mapentities.PolyhedronType.menu.im_func):
    menu = oldmenu(o, editor)
    caulk = quarkx.setupsubset()["DefaultTextureCaulk"]
    if caulk is not None:
    
        #
        # try to find the texture-selection menu-item, in order
        #  to put the caulker after it
        #
        for item in menu:
            try:
                if item.text == "&Texture...":
                    texitem = item
            except (AttributeError):
                pass
                
        def applyCaulk(m,o=o,editor=editor):
            tagged = tagging.gettaggedfaces(editor)
            #
            # FIXME: gettaggedfaces should return [] if nothing is tagged
            #
            if tagged==None:
                tagged=[]
            debug('tagged: %s'%tagged)
            sellist = editor.layout.explorer.sellist + tagged
            undo = quarkx.action()
            for face in o.faces:
                    debug('face: %s'%face.name)
                    if not face in sellist:
                        undo.setspec(face,'tex',CaulkTexture())
            editor.ok(undo,'Caulk poly')
            
        caulkItem = qmenu.item('Caulk non-selected',applyCaulk,"|Caulk texture faces that aren't selected or tagged")
        #
        # fancy Python list-management to put the item where we want it
        #
        menu.insert(menu.index(texitem)+1,caulkItem)
    
    return menu

quarkpy.mapentities.PolyhedronType.menu=polymenu


def facemenu(o, editor, oldmenu=quarkpy.mapentities.FaceType.menu.im_func):
    menu = oldmenu(o, editor)
    caulk = quarkx.setupsubset()["DefaultTextureCaulk"]
    if caulk is not None:

        def applyCaulk(m, o=o, editor=editor):
            undo = quarkx.action()
            undo.setspec(o,'tex',CaulkTexture())
            editor.ok(undo, 'caulk face')
            
     #   for item in menu:
     #       try:
     #           debug(`item.label`)
     #       except (AttributeError):
     #           pass
                
        texpop = findlabelled(menu,'texpop')
        caulkItem = qmenu.item('Caulk face',applyCaulk,"|Put caulk texture on the face")
        texpop.items.append(caulkItem)

    return menu

quarkpy.mapentities.FaceType.menu=facemenu

#
# Log: #
