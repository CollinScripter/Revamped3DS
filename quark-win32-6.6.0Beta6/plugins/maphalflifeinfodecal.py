"""   QuArK  -  Quake Army Knife
"""

#$Header: /cvsroot/quark/runtime/plugins/maphalflifeinfodecal.py,v 1.6 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Half-Life infodecal helper",
   "desc":          "A macro to help making strings of HL-infodecals.",
   "date":          "29 jan 98",
   "author":        "Decker",
   "author e-mail": "decker@post1.tele.dk",
   "quark":         "Version 5.4" }


from quarkpy.maputils import *
from quarkpy.maphandles import *
import quarkpy.mapduplicator
import plugins.deckerutils
StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator
DuplicatorManager = quarkpy.mapduplicator.DuplicatorManager
# DupOffsetHandle = quarkpy.mapduplicator.DupOffsetHandle

class HalfLifeInfodecalHelper(StandardDuplicator):

    def readvalues(self):
	StandardDuplicator.readvalues(self)
	s = self.dup["text"]		# The string to convert to infodecals
	if s:
	   self.text = s
	else:
	   self.text = None
	s = self.dup["wildchar"]
	if s:
	   self.wildchar = s
	else:
	   self.wildchar = '@'
	s = self.dup["tex_upper"]	# Texture-templatename of Upper characters
	if s:
	   self.tex_upper = s
	else:
	   self.tex_upper = None
	s = self.dup["char_upper"]	#
	if s:
	   self.char_upper = s
	else:
	   self.char_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	s = self.dup["tex_lower"]	# Texture-templatename of Lower characters
	if s:
	   self.tex_lower = s
	else:
	   self.tex_lower = None
	s = self.dup["char_lower"]	#
	if s:
	   self.char_lower = s
	else:
	   self.char_lower = "abcdefghijklmnopqrstuvwxyz"
	s = self.dup["tex_numeric"]		# Texture-templatename of Numeric characters
	if s:
	   self.tex_numeric = s
	else:
	   self.tex_numeric = None
	s = self.dup["char_numeric"]		# Texture-templatename of Numeric characters
	if s:
	   self.char_numeric = s
	else:
	   self.char_numeric = "+-,.0123456789"

    def do(self, item, character=None, translate=None):
	if not character:
	   return item
	if translate:
	   StandardDuplicator.do(self, item)	# Do standard offset/matrix calculations
	if character in self.char_numeric:	# Is it a numeric char?
	   if self.tex_numeric:			# Is numeric texture-template specified?
	      pos = self.tex_numeric.find(self.wildchar) # Try to find wildchar in texture-templatename
	      if pos > -1:
	         item["texture"] = self.tex_numeric[:pos] + character + self.tex_numeric[pos + 1:]
	      else:
	         item["texture"] = self.tex_numeric + character	# Just append the character, and hope thats going to work
	elif character in self.char_upper:
	   if self.tex_upper:			# Is upper texture-template specified?
	      pos = self.tex_upper.find(self.wildchar) # Try to find wildchar in texture-templatename
	      if pos > -1:
	         item["texture"] = self.tex_upper[:pos] + character + self.tex_upper[pos + 1:]
	      else:
	         item["texture"] = self.tex_upper + character	# Just append the character, and hope thats going to work
	elif character in self.char_lower:
	   if self.tex_lower:			# Is lower texture-template specified?
	      pos = self.tex_lower.find(self.wildchar) # Try to find wildchar in texture-templatename
	      if pos > -1:
	         item["texture"] = self.tex_lower[:pos] + character + self.tex_lower[pos + 1:]
	      else:
	         item["texture"] = self.tex_lower + character	# Just append the character, and hope thats going to work
	return item

    def buildimages(self, singleimage=None):
        try:
            self.readvalues()
        except:
            print "Note: Invalid HL-InfoDecal Specific/Args."
            return
	if not self.text:
	   return
	thissingleimage = singleimage
        newobjs = []
        for i in range(len(self.text)):
	   if i == 0:
	      item = quarkx.newobj("infodecal:e")
	      item["origin"] = self.dup["origin"]
	      item.translate(quarkx.vect("0 0 0"))	# Force the item to show up, when doing an "Dissociate items"
	      item = self.do(item, self.text[i])
	   else:
	      if self.text[i - 1] <= ' ' or self.text[i - 1] > '~': # If previous item was illegal char, don't make a new item, but reuse it.
		 item = self.do(item, self.text[i], 1)
	      else:
	         item = self.do(item.copy(), self.text[i], 1)
	   if ((thissingleimage is None) or (0==thissingleimage)) and (self.text[i] > ' ' and self.text[i] <= '~'):
	      newobjs = newobjs + [item]
        return newobjs


    def handles(self, editor, view):
#        h = DuplicatorManager.handles(self, editor, view)
        h = quarkpy.maphandles.CenterEntityHandle(self.dup, view, quarkpy.maphandles.IconHandle)
        try:
            self.readvalues()
            if not self.offset:
                return h
        except:
            return h
        try:
	    self.text = self.dup["text"]
	    count = int(len(self.text))
        except:
            count = 0
        for i in range(1, count):
	   if (self.text[i] > ' ' and self.text[i] <= '~'): # Skip illegal characters
#              h.append(DupOffsetHandle(self.origin + self.offset*i, self.dup, self.offset, i))
              h.append(HalfLifeInfoDecalDupOffsetHandle(self.origin + self.offset*i, self.dup, self.offset, i))
        return h


class HalfLifeInfoDecalDupOffsetHandle(quarkpy.mapduplicator.DupOffsetHandle):

    def drag(self, v1, v2, flags, view):
        import quarkpy.qhandles
        delta = v2-v1
        if flags&MB_CTRL:
            delta = quarkpy.qhandles.aligntogrid(self.pos + delta, 1) - self.pos
        else:
            delta = quarkpy.qhandles.aligntogrid(delta, 0)
        if delta or (flags&MB_REDIMAGE):
            new = self.centerof.copy()
            new["offset"] = str(self.dupoffset + delta/self.divisor)
            new = [new]
        else:
            new = None
        return [self.centerof], new


def HalfLifeInfoDecalRegister():
    # Register HalfLifeInfoDecalHelper in Duplicators & misc folder
    newdup = quarkx.newobj("Half-Life Infodecal Helper:d")
    newdup["text"] = "HALFLIFE"
    newdup["wildchar"] = "@"
    newdup["tex_upper"] = "{CAPS@"
    newdup["tex_lower"] = " "
    newdup["tex_numeric"] = "{MED#S@"
    newdup["origin"] = "0 0 0"
    newdup["offset"] = "12 0 0"
    newdup["macro"] = "dup hlinfodecal"
    plugins.deckerutils.RegisterInToolbox("New map items...", "Duplicators & misc", newdup)

### HalfLifeInfoDecalRegister()

quarkpy.mapduplicator.DupCodes.update({
  "dup hlinfodecal":	     HalfLifeInfodecalHelper,
})


# ----------- REVISION HISTORY ------------
# $Log: maphalflifeinfodecal.py,v $
# Revision 1.6  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.3  2003/12/18 21:51:46  peter-b
# Removed reliance on external string library from Python scripts (second try ;-)
#
# Revision 1.2  2001/02/18 20:21:56  decker_dk
# Do not register itself in 'New map items...'
#
#History:
#1999-11-14  Added self-registering
#1999-01-29  Made so only one group gets created, when "Dissociate items"
#1999-01-23  Removed redimage when moving center/duphandles of the HalfLifeInfodecalHelper duplicator.
