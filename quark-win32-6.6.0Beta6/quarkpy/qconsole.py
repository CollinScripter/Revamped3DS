"""   QuArK  -  Quake Army Knife

Console code
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/qconsole.py,v 1.5 2005/10/15 00:47:57 cdunde Exp $


#
# This module defines the class 'console',
# which can be subclassed to analyse the output of
# other programs run by quarkx.runprogram.
#
# Important : DO NOT MODIFY this module, make
# subclassing elsewhere. If you make a syntax error
# here, QuArK will not be able to display it at all.
#
# All you can safely change are the default colors
# for the console, below. These colors are copied
# here from qutils.py because we don't want to
# import qutils from here; we must import as little
# as possible.
#


import quarkx
import sys


SILVER    = 0xC0C0C0
RED       = 0x0000FF
WHITE     = 0xFFFFFF


class console:
    "A link to QuArK's console."

    def __init__(self, color=WHITE):
        self.color = color     # the color could be changed later if you call write("") immediately after to refresh the display

    def write(self, str):
        quarkx.writeconsole(self, str)   # this method can be overridden

    def close(self):
        pass       # called when the process terminates. This can also be overridden


sys.stdout = console()
sys.stderr = console(RED)


firstwarning = 7

def runprogram(cmdline, currentdir, stdout=0, stderr=None):
    "Runs a program in the QuArK console with default colors."
    if stdout!=0:
        global firstwarning
        if firstwarning:
            import qdictionnary
            sys.stderr.write(qdictionnary.Strings[firstwarning])
            firstwarning = None
    print currentdir+">", cmdline
    try:
        if stdout==0:
            return quarkx.runprogram(cmdline, currentdir)
        else:
            return quarkx.runprogram(cmdline, currentdir, stdout or console(SILVER), stderr or console(RED))
    except:
        print "Could not execute this program."
        quarkx.msgbox("Cannot execute this program :\n\n    %s\n\nCheck the path and required DLLs." % cmdline, 1, 4)
        raise quarkx.aborted

# ----------- REVISION HISTORY ------------
#
#
#$Log: qconsole.py,v $
#Revision 1.5  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#