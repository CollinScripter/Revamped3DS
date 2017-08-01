########################################################
#
#               Submenu promote/demote Plugin
#                      v1, Dec 27, 2000
#                     works with Quark 6.1
#
#
#                by tiglari@hexenworld.net     
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & possible improvements to
#   tiglari@planetquake.com
#  
#
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/mapzzzmenus.py,v 1.5 2005/10/15 00:51:56 cdunde Exp $


Info = {
   "plug-in":       "Menu Fixup",
   "desc":          "Promoting & Demoting submenus",
   "date":          "Dec 27, 2000",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.net",
   "quark":         "Version 6.1" }

import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.qmenu
from quarkpy.maputils import *

#
# This plugin must run last, the name is intended to promote this, but
#  if it doesn't work, plugins finding the 'texpop' and 'tagpop' popup
#  menus need to be imported first:
#
import mapcaulk

#
# There must be a way to do this with greater generality.
#  But there's also fiddly bits
#
def facemenu(o, editor, oldfacemenu = quarkpy.mapentities.FaceType.menu.im_func):
    menu = oldfacemenu(o, editor)

    promote = quarkx.setupsubset(SS_MAP, "Options")["Texpop"]

    def promoteClick(m):
        quarkx.setupsubset(SS_MAP, "Options")["Texpop"]="1"
         
    def demoteClick(m):
        quarkx.setupsubset(SS_MAP, "Options")["Texpop"]="0"

    if promote=="1":
        promoteItem = qmenu.item('Demote Texture',demoteClick, "|Texture menu items get demoted to submenu")
    else:
        promoteItem = qmenu.item('Promote texture',promoteClick, "|Texture menu subitems get promoted onto main vertex menu")


    promoteWrap = quarkx.setupsubset(SS_MAP, "Options")["Wrappop"]

    def promoteWrapClick(m):
        quarkx.setupsubset(SS_MAP, "Options")["Wrappop"]="1"
         
    def demoteWrapClick(m):
        quarkx.setupsubset(SS_MAP, "Options")["Wrappop"]="0"

    if promoteWrap=="1":
        promoteWrapItem = qmenu.item('Demote Wrapping',demoteWrapClick, "|Wrapping menu items get demoted to submenu")
    else:
        promoteWrapItem = qmenu.item('Promote Wrapping',promoteWrapClick, "|Wrapping submenu items get promoted onto main vertex menu")


    texpop = findlabelled(menu,'texpop')
    texpop.items.append(promoteItem)
    wrappop = findlabelled(texpop.items,'wrappopup')
    wrappop.items.append(promoteWrapItem)
    if promoteWrap=="1":
        wrapind = texpop.items.index(wrappop)
        #
        # Fix up texts
        #
        for item in wrappop.items:
            #
            # The stuff below the separator is options
            #  that don't need a prefix to be intelligible
            #
            if item == qmenu.sep:
                break
            try:
                item.text = "Wrap texture "+item.text
            except (AttributeError):
                pass
        #
        # Put wrap items after promote texture
        #
        texpop.items.remove(wrappop)
        texpop.items=texpop.items+[qmenu.sep]+wrappop.items
    if promote=="1":
        texind = menu.index(texpop)
        menu[texind:texind+1]=texpop.items
    return menu

quarkpy.mapentities.FaceType.menu = facemenu

# ----------- REVISION HISTORY ------------
#$Log: mapzzzmenus.py,v $
#Revision 1.5  2005/10/15 00:51:56  cdunde
#To reinstate headers and history
#
#Revision 1.2  2003/01/31 20:15:04  tiglari
#add import to get new mapcaulk.py to load first
#
#Revision 1.1  2001/05/29 10:13:21  tiglari
#kickoff
#
