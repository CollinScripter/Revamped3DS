"""   QuArK  -  Quake Army Knife

Various utilities for making gui devices.

"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/guiutils.py,v 1.6 2008/02/22 09:52:24 danielpharos Exp $


import quarkx
from quarkpy.maputils import *
#
# FIXME: ugh hideous hack refactoring time!!!
#
from plugins.mapmadsel import menrestsel



def getSetupOption(name, default):
    result = quarkx.setupsubset(SS_MAP, "Options")[name]
#    debug("result: "+`result`)
    if result==None:
      result=default
    return result

#
# In LiveEditDialogs, monitors changes in numeric parameters stored as EF1's.
#   returns (1, newvalue) if there's been a change, (0, value) otherwise
#   see plugins.mapbadtexscale for an example of use
#
def dlgNumberCheck(dlg, pack, attribute, defaultvalue, format="%.2f"):
    newvalue, = dlg.src[attribute]
#       debug('pack: '+getattr(pack, attribute))
    if newvalue!=eval(getattr(pack,attribute)):
#           debug("%s : %s"%(`newvalue`, `eval(getattr(pack,attribute))`))
        if newvalue==defaultvalue:
#              debug('clearing')
            quarkx.setupsubset(SS_MAP, "Options")[attribute]=None
        else:
            quarkx.setupsubset(SS_MAP, "Options")[attribute]=format%newvalue
        setattr(pack, attribute, format%newvalue)
        return (1, newvalue)
    return (0, newvalue)

#
# For an object o, uses the parentpopupitems function to
#   construct a menu of popups, one for each object that
#   contains o in the tree hierarchy
#   
#   see plugins/mapmadsel, plugins/mapmovevertex for examples
#     of use
#
def getrestrictor(e):
  try:
    return e.restrictor
  except (AttributeError) : return None

def buildParentPopupList(o, parentpopupitems, editor):
    current=o
    list = []
    if editor is None:
        editor = mapeditor()
    restrictor = getrestrictor(editor)
    restricted = 0
  #  while current.name != "worldspawn:b":
    while current != None:
        list.append(parentpopupitems(current, editor, restricted))
        if current==restrictor and menrestsel.state == qmenu.checked:
            list.append(qmenu.sep)
            restricted = 1
        current = current.treeparent;
  #  list.reverse()
    return list    



# $Log: guiutils.py,v $
# Revision 1.6  2008/02/22 09:52:24  danielpharos
# Move all finishdrawing code to the correct editor, and some small cleanups.
#
# Revision 1.5  2005/10/15 00:47:57  cdunde
# To reinstate headers and history
#
# Revision 1.2  2003/01/01 10:08:16  tiglari
# fix for console errors on RMB on vertex in restricted selection
#
# Revision 1.1  2002/04/01 08:29:10  tiglari
# start off with some stuff from mapmadsel.py, and abstracted from mapmicrobrush.py
#
#