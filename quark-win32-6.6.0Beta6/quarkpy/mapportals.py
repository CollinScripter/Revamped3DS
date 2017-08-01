"""   QuArK  -  Quake Army Knife

Map editor portal viewer
"""
#
# Copyright (C) 1996-2003 The QuArK community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapportals.py,v 1.11 2007/12/17 00:50:00 danielpharos Exp $

import quarkx
import qmacro
import qtoolbar
from maputils import *
import mapeditor
import mapoptions


class PortalsDlg(qmacro.dialogbox):

    #
    # dialog layout
    #

    dfsep = 0.2
    dlgflags = 0

    dlgdef = """
      {
        Style = "15"
        Caption = "Portals"
        sep: = {Typ="S" Bold="0" Txt="Here are the portals from the"}
        sep: = {Typ="S" Bold="0" Txt="last build, as blue lines."}
        close:py = {Txt="" }
      }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, editor):
        self.editor = editor
        src = quarkx.newobj(":")
        qmacro.dialogbox.__init__(self, form, src,
           close = qtoolbar.button(
              self.close,
              "click here to remove portals from your map",
              ico_editor, 0,
              "Ok, hide portals"))

    def windowrect(self):
        x1,y1,x2,y2 = quarkx.screenrect()
        return (x2-180, 20, x2-15, 132)

    def onclose(self, dlg):
        try:
            del self.editor.Portals
            self.editor.invalidateviews()
        except:
            pass
        qmacro.dialogbox.onclose(self, dlg)


def readPortal(pos0, line):
    result = []
    while pos0!=-1:
        pos1 = line.find(')',pos0+1)
        vecstr = line[pos0+1:pos1]
        vec = quarkx.vect(vecstr)
        result.append(quarkx.vect(vecstr))
        pos0 = line.find('(',pos1+1)
    return result

#
# This code is very messy due to the chaotic variation in portal
#  file formats. The Q3 portal files seem rather richer than the
#  others, see portals.cpp in the bobtoolz source (GtkRadiant)
#
def LoadPortalFile(editor, filename):
    
    f = open(filename, "r")
    data = f.readlines()
    f.close()
    portals = []
    index = 0
    #
    # skip over introductory lines without actual portals
    #
    while index<len(data):
        pos = data[index].find('(')
        if pos!=-1:
            break
        index = index+1
    else:
        quarkx.msgbox('No portals found',MT_INFORMATION,MB_OK)
        return
    #
    # Now read in portal lines beginning with at least three numbers
    #  these are real, two-sided portals; the ones beginning with 2
    #  numbers are one-sided; we ignore them, and quit when they appear.
    #
    while index<len(data):
        pos = data[index].find('(')
        line = data[index]
        numbers = line[:pos].split()
        if len(numbers)<3:
            break
        portals.append(readPortal(pos,line))
        index=index+1
    #
    # And now show the dialog to make them go awayS
    #

    PortalsDlg(editor.form, editor)
    editor.Portals = portals
    editor.invalidateviews()


def DrawLines(editor, view, oldFinishDrawing = mapeditor.MapEditor.finishdrawing):
    try:
        Portals = editor.Portals
        cv = view.canvas()
        cv.pencolor = MapColor("Duplicator")
        cv.penwidth = mapoptions.getLineThickness()
        for portal in Portals:
            pt0 = view.proj(portal[-1])
            for i in range(len(portal)):
                pt1 = view.proj(portal[i])
                cv.line(pt0, pt1)
                pt0 = pt1
    except:
        pass
    oldFinishDrawing(editor, view)


mapeditor.MapEditor.finishdrawing = DrawLines


#$Log: mapportals.py,v $
#Revision 1.11  2007/12/17 00:50:00  danielpharos
#Fix the map portals not drawing anymore.
#
#Revision 1.10  2007/01/09 23:11:46  danielpharos
#Fixed an annoying crash with map portals (for instance when you set the light-entity's color too high)
#
#Revision 1.9  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.6  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.5  2003/03/21 10:56:08  tiglari
#support for line-thickness specified by mapoption
#
#Revision 1.4  2003/03/19 22:24:10  tiglari
#fix bug in parsing
#
#Revision 1.3  2003/03/19 11:27:47  tiglari
#remove debug statement
#
#Revision 1.2  2003/03/19 11:26:15  tiglari
#expand info in dialog box
#
#Revision 1.1  2003/03/19 11:07:52  tiglari
#first version, only tested for Q1
#
#

