
########################################################
#
#               Alternate Texture Position Plugin
#
#
#                  by tiglari@hexenworld.com
#     
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & possible improvements to
#   tiglari@hexenworld.com
#  
#
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/maptexpos.py,v 1.11 2007/11/29 23:39:00 cdunde Exp $


Info = {
   "plug-in":       "Alternate Texture Positioning",
   "desc":          "Alternate Texture Positioning",
   "date":          "Nov 4, 1999",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Version 5.11" }

import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.qmenu
import quarkpy.mapeditor
import quarkpy.qbaseeditor
import quarkpy.mapcommands
import quarkpy.mapoptions
import quarkpy.qhandles
import quarkpy.mapbtns
import quarkpy.dlgclasses
from quarkpy.maputils import *


class TexPosDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (180,200)
    dlgflags = FWF_KEEPFOCUS   # keeps dialog box open
    dfsep = 0.35

    dlgdef = """
        {
            Style = "9"
        Caption = "Texture Positioning Dialog"

        scale: = 
        {
        Txt = "Scale"
        Typ = "EQ"
        Hint = "x, y scales; map units per texture tile" $0D "  y is the direction along the edge away from the closest corner," $0D "  x is the direction along the other edge at that corner, away from it"
        }

        sep: = {Typ="S" Txt=" "} 

        offset: =
        {
        Txt = "Offset"
        Typ = "EQ"
        Hint = "x, y offsets; floats map units" $0D "  y is the direction along the edge away from the closest corner," $0D "  x is the direction along the other edge at that corner, away from it"
        }

        sep: = {Typ="S" Txt=" "} 

        tilt: = {
        Txt = "Tilt"
        Typ = "EU"
        Hint = "`tilt' angle, in degrees."
        }
        
        sep: = {Typ="S" Txt=" "} 

        shear: = {
        Txt = "Shear"
        Typ = "EU"
        Hint = "`shear' angle, in degrees." $0D "  (angle between texture y-axis and perp to texture x-axis)"
        }
        
      
        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

def read2vec(vals):
  strings = vals.split()
  return eval(strings[0]), eval(strings[1])

def PosTexClick(m):
  editor = mapeditor()
  if editor is None: return
  
  class pack:
    "just a place to stick stuff"
  
  pack.o = m.o
  
  def setup(self, pack=pack):
    editor.findtargetdlg=self
    src = self.src
    face = pack.o
    p0, p1, p2 = face.threepoints(2)
    tp1, tp2 = p1-p0, p2-p0
    scalex, scaley = abs(p1-p0), abs(p2-p0)
    n = face.normal
    vc = face.origin
    v1, v2 = bestaxes(n, self.editor.layout.views[0])
#      squawk("v1: %s, v2: %s"%(v1, v2))
    anglex, angley = (math.atan2(v2*tp1, v1*tp1), math.atan2(v2*tp2, v1*tp2))
    self.src["offset"] = "%.1f %.1f"%(-v1*(vc-p0), -v2*(vc-p0))
    anglex, angley = anglex/deg2rad, angley/deg2rad
    self.src["scale"] = "%.1f %.1f"%(scalex, scaley)

    tilt = anglex
    shear = anglex + 90 - angley

    self.src["tilt"] = "%.1f"%degcycle(tilt)
    self.src["shear"] = "%.1f"%degcycle(shear)
    
    
  def action(self, pack=pack, editor=editor):
    face = pack.o
    offsetx, offsety = read2vec(self.src["offset"])
    scalex, scaley = read2vec(self.src["scale"])
    tilt = eval(self.src["tilt"])
    shear = eval(self.src["shear"])

    anglex = tilt
    angley = anglex + 90 - shear

    anglex, angley = anglex*deg2rad, angley*deg2rad

    f2 = face.copy()
    vc = face.origin
    n = face.normal
    v1, v2 = bestaxes(n, self.editor.layout.views[0])
#      squawk("1: %s, 2: %s"%(`v1`, `v2`))
    p0 = vc + offsetx*v1 + offsety*v2
    p1 = p0 + (v1*math.cos(anglex) + v2*math.sin(anglex))*scalex
    p2 = p0 + (v1*math.cos(angley) + v2*math.sin(angley))*scaley
#      squawk("0: %s, 1: %s, 2: %s"%(`p0`, `p1-p0`, `p2-p0`))
    f2.setthreepoints((p0, p1, p2), 2)

    undo_exchange(editor, face, f2, "position texture")
    pack.o = f2


    
  TexPosDlg(quarkx.clickform, 'texpos', editor, setup, action)
    

def texmenu(o, editor, oldmenu = quarkpy.mapentities.FaceType.menu.im_func):
  "the new right-mouse for sides"
  menu = oldmenu(o, editor)
  texpop = findlabelled(menu, 'texpop')
  texitem = qmenu.item("Position Texture",PosTexClick)
  texitem.o = o
  texpop.items[1:1] = [texitem]
  return menu
  
quarkpy.mapentities.FaceType.menu = texmenu

# ----------- REVISION HISTORY ------------
#
#
# $Log: maptexpos.py,v $
# Revision 1.11  2007/11/29 23:39:00  cdunde
# Changed to keep Texture Position dialog open and update dynamically.
#
# Revision 1.10  2005/10/15 00:51:56  cdunde
# To reinstate headers and history
#
# Revision 1.7  2005/09/16 18:09:13  cdunde
# Set dialog box to remain open
#
# Revision 1.6  2003/12/18 21:51:46  peter-b
# Removed reliance on external string library from Python scripts (second try ;-)
#
# Revision 1.5  2001/06/17 21:10:56  tiglari
# fix button captions
#
# Revision 1.4  2001/06/16 03:19:47  tiglari
# add Txt="" to separators that need it
#
# Revision 1.3  2000/07/24 09:18:11  tiglari
# Put texture-position dialog into a submenu labelled 'texpop', for texture menu cleanup as suggested by Brian Audette
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#