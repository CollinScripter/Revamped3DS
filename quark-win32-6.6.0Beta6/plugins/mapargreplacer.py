"""
QuArK  -  Quake Army Knife
"""

#$Header: /cvsroot/quark/runtime/plugins/mapargreplacer.py,v 1.8 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Arg Replacer",
   "desc":          "",
   "date":          "6 Sep 99",
   "author":        "Decker",
   "author e-mail": "decker@post1.tele.dk",
   "quark":         "Version 5.10"
}

from quarkpy.maputils import *
import quarkpy.mapduplicator

class ArgReplacer(quarkpy.mapduplicator.DuplicatorManager):

    Icon = (ico_dict['ico_mapdups'], 2)

    def filterspecs(self, specs):
        "Removes MACRO and ORIGIN if they exists in the dictspec.keys() array"
        replacerspecs = []
        for i in specs:
           if (not ((i == "macro") or (i == "origin"))):
              replacerspecs = replacerspecs + [i]
        return replacerspecs

    def searchandreplace(self, item, replacerspecs):
        for r in replacerspecs:
           searchstring = '%' + r + '%'
           for key in item.dictspec.keys():
              item[key] = item[key].replace(searchstring, self.dup.dictspec[r])
              newkey = key.replace(searchstring, self.dup.dictspec[r])
              if (newkey != key):
                 keyvalue = item[key]
                 item[key] = None
                 item[newkey] = keyvalue

    def replace(self, items, replacerspecs):
        for i in items:
           if ((i.type == ':g') or (i.type == ':d')):
              self.replace(i.subitems, replacerspecs)
           elif (i.type == ':e' or i.type == ':b'):
              self.searchandreplace(i, replacerspecs)

    def buildimages(self, singleimage=None):
        items = []
        if ((singleimage is None) or (singleimage == 0)):
           if (self.dup.subitems is not None):
              # why wont a "items = self.dup.subitems.copy()" work?
              for i in self.dup.subitems:
                 items.append(i.copy())
              replacerspecs = self.filterspecs(self.dup.dictspec.keys())
              self.replace(items, replacerspecs)
        return items

quarkpy.mapduplicator.DupCodes.update({
  "arg replacer":            ArgReplacer,
})

# ----------- REVISION HISTORY ------------
#
# $Log: mapargreplacer.py,v $
# Revision 1.8  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.5  2003/12/18 21:51:46  peter-b
# Removed reliance on external string library from Python scripts (second try ;-)
#
# Revision 1.4  2001/10/22 10:21:59  tiglari
# live pointer hunt, revise icon loading
#
# Revision 1.3  2001/06/24 14:47:58  decker_dk
# Can now also replace specific-names.
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
