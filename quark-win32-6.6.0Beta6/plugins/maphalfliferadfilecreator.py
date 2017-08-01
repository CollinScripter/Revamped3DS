"""   QuArK  -  Quake Army Knife

"""
#
# Copyright (C) 2000 Alexander Haarer
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/maphalfliferadfilecreator.py,v 1.8 2010/02/21 15:42:49 danielpharos Exp $

Info = {
    # Based upon Alexander's Quake-3:Arena .ARENA files generator

    "plug-in":       "Half-Life .RAD file generator",
    "desc":          "creates .RAD file in /maps",
    "date":          "16 aug 2001",
    "author":        "Decker",
    "author e-mail": "decker@planetquake.com",
    "quark":         "Version 6.3"
}

from quarkpy.maputils import *
import quarkpy.mapduplicator
import quarkpy.qmacro
from quarkpy.qeditor import mapeditor

StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator


def macro_hlradfilemaker_apply(self):
    editor = mapeditor()
    if editor is None:
        return
    dup = editor.layout.explorer.uniquesel
    if dup is None:
        return

    undo = quarkx.action()

    # Add/update from work-area to duplicators spec/arg-list
    texture  = dup["texture"]
    lighting = dup["lighting"]
    undo.setspec(dup, texture, lighting)

    # Reset work-area
    undo.setspec(dup, "texture",  "")
    undo.setspec(dup, "lighting", "")

    editor.ok(undo, '.RAD-file apply texture settings')
    editor.invalidateviews()

quarkpy.qmacro.MACRO_hlradfilemaker_apply = macro_hlradfilemaker_apply


def checkfilename(filename):
    filename = filter(lambda c: c in r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$%'-_@{}~`!#()", filename)
    return filename or "quark"


class HalfLifeRADFileMaker(StandardDuplicator):

    def buildimages(self, singleimage=None):
        # Get specified .RAD filename
        try:
            filename = self.dup["filename"]
        except:
            filename = none

        if (filename is None or filename == ""):
            # build .RAD filename
            editor = mapeditor(SS_MAP)
            if (editor is None):    # Make sure there IS a editor available
                return []
            filename = checkfilename(editor.fileobject.shortname or editor.fileobject["FileName"]) + ".RAD"
	    filename = filename.lower()

        radfilename = quarkx.outputfile(quarkx.getmapdir()+"//"+filename)

        try:
            f = open(radfilename, "w+")

            # print self.dup.dictspec.keys()

            for texturename in self.dup.dictspec.keys():
                if (not texturename in ("macro", "filename", "texture", "lighting")):
                    # print texturename, self.dup[texturename]
                    f.write("%s\t%s\n" % (texturename, self.dup[texturename]))

            f.close
        except:
            f.close
            squawk("Can't write the file "+radfilename)

        return []

quarkpy.mapduplicator.DupCodes.update({
  "dup hlradfilemaker":      HalfLifeRADFileMaker,
})

# ----------- REVISION HISTORY ------------
#$Log: maphalfliferadfilecreator.py,v $
#Revision 1.8  2010/02/21 15:42:49  danielpharos
#Fixed orangebox compiler not finishing compile.
#
#Revision 1.7  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.4  2003/12/18 21:59:33  peter-b
#Fixed syntax error (d'oh!)
#
#Revision 1.3  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.2  2001/10/08 20:23:15  decker_dk
#Quick fix. Testing for 'editor' is None then 'return []'.
#
#Revision 1.1  2001/08/16 20:08:21  decker_dk
#A plugin which stores the texture lighting values, and exports to a LIGHTS.RAD or <mapname>.RAD file.
#
