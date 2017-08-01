"""   QuArK  -  Quake Army Knife

Various Map editor utilities.
"""

#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

# $Header: /cvsroot/quark/runtime/quarkpy/qentbase.py,v 1.5 2005/10/15 00:47:57 cdunde Exp $

def RegisterEntityConverter(Text, Ext, Desc, Proc):
    import qmacro
    qmacro.entfn.update( { Text: ([Ext, Desc],  Proc) } )
    import quarkx
    quarkx.entitymenuitem(Text)
    
# ----------- REVISION HISTORY ------------
# $Log: qentbase.py,v $
# Revision 1.5  2005/10/15 00:47:57  cdunde
# To reinstate headers and history
#
# Revision 1.2  2001/06/16 01:17:29  aiv
# * added cvs headers
# * removed console spam
#
#