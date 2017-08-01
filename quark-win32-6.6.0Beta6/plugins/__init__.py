# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

Plug-ins Launcher
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/__init__.py,v 1.10 2009/07/14 12:14:54 danielpharos Exp $



# This code loads files from the "plugins" directory.

#   q_*.py     loaded at start-up
#   map*.py    loaded only when a map editor opens


import nt     # note: this is not portable, but I want to avoid
              # to include os.py in the MiniPython distribution.
import quarkx
from quarkpy.qutils import *

LoadedPlugins = []

def LoadPlugins(beginning):
    for dir in __path__:
        for file in nt.listdir(dir):
            f = file.upper()
            if (f[-3:]=='.PY') and (f[:len(beginning)]==beginning):
                quarkx.log("Loading plugin: %s" % (file), LOG_VERBOSE)
                module = __import__(file[:-3], globals(), locals(), [])
                if not (module in LoadedPlugins):
                    LoadedPlugins.append(module)


LoadPlugins("Q_")   # immediately loads plug-ins whose name
                    # begins with Q_


# ----------- REVISION HISTORY ------------
#
#
# $Log: __init__.py,v $
# Revision 1.10  2009/07/14 12:14:54  danielpharos
# Oops: uploaded version: Added logging of plugin loading.
#
# Revision 1.9  2009/07/14 11:29:13  danielpharos
# Added logging of plugin loading.
#
# Revision 1.8  2006/11/30 01:17:47  cdunde
# To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
# Revision 1.7  2006/11/29 06:58:35  cdunde
# To merge all runtime files that had changes from DanielPharos branch
# to HEAD for QuArK 6.5.0 Beta 1.
#
# Revision 1.6.2.1  2006/11/03 23:38:11  cdunde
# Updates to accept Python 2.4.4 by eliminating the
# Depreciation warning messages in the console.
#
# Revision 1.6  2005/10/15 00:49:05  cdunde
# To reinstate headers and history
#
# Revision 1.3  2003/12/17 13:58:59  peter-b
# - Rewrote defines for setting Python version
# - Removed back-compatibility with Python 1.5
# - Removed reliance on external string library from Python scripts
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#
