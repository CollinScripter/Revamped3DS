"""   QuArK  -  Quake Army Knife

Implementation of the Brush Subtraction commands
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapmovesel.py,v 1.7 2005/10/15 00:51:24 cdunde Exp $



Info = {
   "plug-in":       "Selection Movement",
   "desc":          "Various movements involving multiple selections",
   "date":          "8 June 2001",
   "author":        "tiglari",
   "author e-mail": "tiglari@planetquake.com",
   "quark":         "Version 6.3" }

import quarkx
import quarkpy.mapmenus
import quarkpy.mapcommands
import quarkpy.maphandles
import mapmadsel

from quarkpy.maputils import *


def SwapClick(m):
    editor=mapeditor()
    if editor is None: return
    centers = map(lambda item:quarkpy.maphandles.GetUserCenter(item), m.sel)
    diff = centers[1]-centers[0]
    newitems = map(lambda item:item.copy(),m.sel)
    newitems[0].translate(diff)
    newitems[1].translate(-diff)
    undo=quarkx.action()
    for i in 0, 1:
        undo.exchange(m.sel[i], newitems[i])
    editor.ok(undo,"swap selection")


def AlignClick(m):
    editor=mapeditor()
    if editor is None: return
    sel=editor.layout.explorer.sellist
    marked = mapmadsel.getstashed(editor)
    if marked is None:
       box = quarkx.boundingboxof(sel)
    else:
       box = quarkx.boundingboxof([marked])
    def shift(item,box=box,mode=m.mode):
        ibox=quarkx.boundingboxof([item])
        if mode in ["up","east","north"]:
            i =1
        else:
            i= 0
        if mode in ["east","west"]:
            shift=quarkx.vect(box[i].x-ibox[i].x,0,0)
        elif mode in ["north","south"]:
            shift=quarkx.vect(0,box[i].y-ibox[i].y,0)
        else:
            shift=quarkx.vect(0,0,box[i].z-ibox[i].z)
        return shift
    undo=quarkx.action()
    for item in sel:
        item2 = item.copy()
        item2.translate(shift(item))
        undo.exchange(item,item2)
    editor.ok(undo,"align "+m.mode)

    
def makeitem(mode):
    item=qmenu.item("Align "+mode,AlignClick)
    item.mode=mode
    return item

alignlist = map(makeitem,["east","west","north","south","up","down"])

menswap = qmenu.item("Swap Selection",SwapClick)
menalign = qmenu.popup("Align Group",alignlist)

def commandsclick(menu, oldcommand=quarkpy.mapcommands.onclick):
    oldcommand(menu)
    editor=mapeditor()
    if editor is None : return
    sel = editor.layout.explorer.sellist
    menhint = "|Swap Selection:\n\nSwap first and second elements of 2 selected items."
    menswap.state=qmenu.disabled
    if len(sel)<2:
        menhint=menhint+"\n\nThis menu item requires that two items be selected; you don't have enough.|intro.mapeditor.menu.html#makeprism"
    elif len(sel)>2:
        menhint=menhint+"\n\nThis menu item requires that two items be selected, you have too many.|intro.mapeditor.menu.html#makeprism"
    menswap.hint = menhint
    if len(sel)==2:
        menswap.state=qmenu.normal
    menswap.state=qmenu.normal

    alignhint = "|Align selected:\n\nAlign items in selection along their bounding box edges, or along the edges of a marked object (RMB I Navigate Tree I <item> \ Mark)."
    menalign.state=qmenu.normal
    marked=mapmadsel.getstashed(editor)
    if marked is None:
        menalign.text = "Align selected (to bbox edge)"
    else:
        menalign.text = "Align selected (to marked)"
    if len(sel)<2:
        if marked is None:
            alignhint=alignhint+"\n\nThis menu item requires that two or more items be selected, or that something be marked; neither of these are true.|intro.mapeditor.menu.html#makeprism"
            menalign.state=qmenu.disabled
        elif len(sel)<1:
            alignhhint=alignhint+"\n\nNothing to align.|intro.mapeditor.menu.html#makeprism"
            menaligned.state=qmenu.disabled
        elif sel[0] is marked:
            alignhint=alignhint+"\n\nNo point in aligning something to itself (the selected item is also the marked one).|intro.mapeditor.menu.html#makeprism"
            menalign.state=qmenu.disabled
    menalign.hint=alignhint

quarkpy.mapcommands.onclick = commandsclick

# ----------- REVISION HISTORY ------------
#
quarkpy.mapcommands.items.append(menswap)
quarkpy.mapcommands.items.append(menalign)

# $Log: mapmovesel.py,v $
# Revision 1.7  2005/10/15 00:51:24  cdunde
# To reinstate headers and history
#
# Revision 1.4  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.3  2001/07/24 01:10:39  tiglari
# menu item text now says whether to marked or not
#
# Revision 1.2  2001/07/23 23:41:13  tiglari
# Now aligns to marked, if anything is marked
#
# Revision 1.1  2001/06/07 21:30:15  tiglari
# swap & align (suggestions by Alan Donald (swap) & quantum_red (align)
#
#
