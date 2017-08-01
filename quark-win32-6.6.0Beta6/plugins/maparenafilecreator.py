"""   QuArK  -  Quake Army Knife

"""
#
# Copyright (C) 2000 Alexander Haarer
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/maparenafilecreator.py,v 1.5 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Quake3 Arena script generator",
   "desc":          "creates .arena files in /scripts",
   "date":          "04 jul 2000",
   "author":        "alexander",
   "author e-mail": "mac.@gmx.net",
   "quark":         "Version 6.0" }

from quarkpy.maputils import *
import quarkpy.mapduplicator

StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator

# create a file like that
#{
#map "newmap"
#bots "ranger mynx visor crash"
#longname "my supercool q3 map"
#fraglimit 50
#type "ffa"
#}

def checkfilename(filename):
   filename = filter(lambda c: c in r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$%'-_@{}~`!#()", filename)
   return filename or Strings[180]


class ArenaFileMaker(StandardDuplicator):

    def readvalues(self):
	StandardDuplicator.readvalues(self)

	s = self.dup["bots"]
	if s:
	   self.bots = s
	else:
	   self.bots = None

	s = self.dup["longname"]	
	if s:
	   self.longname = s
	else:
	   self.longname = None

	s = self.dup["fraglimit"]	
	if s:
	   self.fraglimit = s
	else:
	   self.fraglimit = None

	s = self.dup["type"]
	if s:
	   self.type = s
	else:
	   self.type = "ffa"

    def do(self, item):
        print "do", item
        return [item]

    def buildimages(self, singleimage=None):
        try:
            self.readvalues()
        except:
            print "Note: Invalid Arenafilemaker Specific/Args."
            return

        # build arena script name
        editor = mapeditor(SS_MAP)
        mapname = checkfilename(editor.fileobject.shortname or editor.fileobject["FileName"]).lower()
        scriptname = quarkx.outputfile("scripts/"+mapname+".arena")

        try:
            f=open(scriptname,"w+")
            f.write("""{\n  map "%s"\n"""    % mapname)
            f.write("""  bots "%s"\n"""      % self.bots)
            f.write("""  longname "%s"\n"""  % self.longname)
            f.write("""  fraglimit %s\n"""   % self.fraglimit)
            f.write("""  type "%s"\n}\n"""   % self.type)
            f.close
        except:
            f.close
            squawk("Can't write the file "+scriptname)

        return []

quarkpy.mapduplicator.DupCodes.update({
  "dup arenafilemaker":	     ArenaFileMaker,
})

# ----------- REVISION HISTORY ------------
#
#
#$Log: maparenafilecreator.py,v $
#Revision 1.5  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.2  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.1  2000/07/04 17:27:26  alexander
#arenafilemaker macro
#
#
#