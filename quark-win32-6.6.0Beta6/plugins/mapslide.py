 
########################################################
#
#                          Slider Plugin
#                          v2.0, Aug 2001
#                      works with Quark 6.3        
#
#
#                    by tiglari@planetquake.com     
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & improvements to tiglari@hexenworld.com
#
###
##########################################################

#$Header: /cvsroot/quark/runtime/plugins/mapslide.py,v 1.9 2005/10/15 00:51:24 cdunde Exp $



Info = {
   "plug-in":       "Slide Plugin",
   "desc":          "Sliding things along and around axes",
   "date":          "10 Aug 2001",
   "author":        "tiglari",
   "author e-mail": "tiglari@planetquake.com",
   "quark":         "Version 6.3" }


import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.qmenu
import quarkpy.mapeditor
import quarkpy.mapcommands
import quarkpy.mapoptions
import quarkpy.maphandles
import quarkpy.dlgclasses
from tagging import *
import mapmadsel   # to make mad selector load first
from quarkpy.maputils import *

#
#------------  WTF -----------
#
#  First we define the slider's dialog, then a Click function
#   to bring it up when an appropriate menu-button, and finally
#   redefine a bunch of menus to put the Click function on them.
#  

#
# see the dialogs in quarkpy.qeditor and plugins.mapsearch
#  for commented basic dilaog code.  LiveEditDlg is a jazzed
#  up descendent of quarkpy.qmacro.dialogbox, adapted for
#  dialogs that are supposed to drive things around on the
#  screen While U Watch.
#

class SlideDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (150,150)
    dfsep = 0.40

    dlgdef = """
        {
        Style = "9"
        Caption = "Slide Object Dialog"

        along: = 
        {
        Txt = "Along"
        Typ = "EU"
        Hint = "Movement Along Axis, offset from present position." $0D "  Increment 1 or gridstep"
        }

        sep: = {Typ="S" Txt=" "} 
        
        around: = 
        {
        Txt = "Around"
        Typ = "EU"
        Hint = "Movement Around Axis, offset from preset position." $0D "  In degrees, regardless of grid" $0D "  But FORCE option will force to grid after movement."
        }

        sep: = {Typ="S" Txt=" "} 
        
        force: =
        {
        Txt = "Grid"
        Typ = "X"
        Hint = "Object forced to grid after movement"
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }

    }
    """

#
# ---- Click Function
#
       
#
#    First an auxiliary:
#
# delta is the cumulative difference between starting and
#  current positions.
# diff is the difference from the last position.
# if there is a gridstep, we want to round diff up or down
#   to the gridstep, and revise delta accordingly
#
def gridify(delta, diff, gridstep):
#    debug('diff %d, delta %d'%(diff,delta))
    if not gridstep:
            return delta
    orig = delta-diff
    (rem, quot) = math.modf(diff/gridstep)
#    debug("%d, %d"%(rem,quot))
    if diff < 0:
        sign = -1
    else:
        sign = 1
    if rem:
    #    squawk("d: %s, r: %s"%(delta, quot+gridstep))
        diff = (quot+sign)*gridstep
    return orig+diff

#
# Now for the click
#
def EdgeSlideClick(m):
    editor = m.editor
    edge = m.tagged
    
    #
    # parameters are stuffed into the pack class/object,
    #  and passed thereby
    #
    class pack:
        "a place to stick stuff"
    pack.edge = edge
    pack.axis = (edge[0]-edge[1]).normalized
    pack.o = m.o
    pack.along = 0
    pack.around = 0
    #
    # orig_object is the original, o will be replaced as
    #  the dlg's changes are executed
    #
    pack.orig_object=pack.o
      
    #
    # this initializes the dialog's values, via code in
    #  dlgclasses.LiveEdit dialog that runs the function
    #  passed as its `setup' parameter
    #
    # pack=pack below is a `closure', which effectively passes
    #  some locally defined info to the function which is then
    #  passed as an argument (similar to callbacks in effect,
    #  but easier to use once you get used to it).
    #
    def setup(self, pack=pack):
        src = self.src

        self.axis = set_sign(pack.axis)
        self.pack = pack
        self.point = pack.edge[0]
        src["along"] = str(pack.along)
        src["around"] = str(int(pack.around/deg2rad))
      
    #
    # And here's the `action' function that gets called
    #  every time you change the data in the dialog box.
    #
    def action(self, pack=pack, editor=m.editor):
        src = self.src
        delta = eval(src["along"]) # cumulative displacement from inital position
        if delta != pack.along:
            delta = gridify(delta, delta-pack.along, editor.gridstep)
        pack.along=delta
        phi = eval(src["around"])*deg2rad
        new = pack.orig_object.copy()
        matrix = ArbRotationMatrix(self.axis, phi)
        new.linear(self.point, matrix)
        new.translate(delta*self.axis)
        if src["force"] and editor.gridstep:
            new.forcetogrid(editor.gridstep)

        undo=quarkx.action()
        undo.exchange(pack.o, new)
        editor.ok(undo, "move object wrt axis")
        #
        # And this little trick is necessary to keep the undo
        #  mechanism happy, each data change swaps in the newly
        #  created object for the old pack.o, undo-ably.
        #
        pack.o = new
        pack.along = delta
        pack.around = phi

    #
    # And finally call the dialog, with the functions we have
    #  created as parameters, and also a label, 'axis slide',
    #  to file the position of this dialog under between
    #  uses (and across sessions).
    #
    SlideDlg(quarkx.clickform, 'axis_slide', editor, setup, action)
    

#
# And a whole new one for sliding things around over a tagged face
#  (such as after executing snap object to tagged plane_
#

class PlaneSlideDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (150,160)
    dfsep = 0.40

    dlgdef = """
        {
        Style = "9"
        Caption = "Slide Object above Plane "

        away: = 
        {
        Txt = "Away"
        Typ = "EU"
        Hint = "Movement along the normal to plane, offset from present position." $0D "  Increment 1 or gridstep"
        }

        sep: = {Typ="S" Txt=" "} 
        
        across: = 
        {
        Txt = "Across"
        Typ = "EQ"
        Hint = "Movement across the surface of the plane, offset from preset position."
        }

        sep: = {Typ="S" Txt=" "} 
        
        force: =
        {
        Txt = "Force"
        Typ = "X"
        Hint = "Object forced to grid after movement"
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }

    }
    """


#
# Now for the click
#
def PlaneSlideClick(m):
    editor = m.editor
    plane = m.tagged
    
    #
    # parameters are stuffed into the pack class/object,
    #  and passed thereby
    #
    class pack:
        "a place to stick stuff"
    pack.plane = plane
    pack.normal = plane.normal
    pack.o = m.o
    pack.away = 0
    pack.across = 0,0
    pack.axes = bestaxes(pack.normal)
    #
    # orig_object is the original, o will be replaced as
    #  the dlg's changes are executed
    #
    pack.orig_object=pack.o
    
    def setup(self, pack=pack):
        src = self.src

        src["away"] = str(pack.away)
        src["across"] = "%.1f %.1f"%pack.across
      
      
    #
    # And here's the `action' function that gets called
    #  every time you change the data in the dialog box.
    #
    def action(self, pack=pack, editor=m.editor):
        src = self.src
        away = eval(src["away"]) # cumulative displacement from inital position

        def griddo(new, old, step=editor.gridstep):
            if new != old:
                return gridify(new, new-old, step)
            else:
                return new
            
        if away != pack.away:
            away = gridify(away, away-pack.away, editor.gridstep)
        pack.away=away
        across = read2vec(src["across"])
        across = tuple(map(griddo,across,pack.across))
        new=pack.orig_object.copy()
        new.translate(away*pack.normal+across[0]*pack.axes[0]+across[1]*pack.axes[1])
        if src["force"] and editor.gridstep:
            new.forcetogrid(editor.gridstep)

        undo=quarkx.action()
        undo.exchange(pack.o, new)
        editor.ok(undo, "move object wrt axis")
        #
        # And this little trick is necessary to keep the undo
        #  mechanism happy, each data change swaps in the newly
        #  created object for the old pack.o, undo-ably.
        #
        pack.o = new
        pack.away = away
        pack.across = across

    #
    # And finally call the dialog, with the functions we have
    #  created as parameters, and also a label, 'axis slide',
    #  to file the position of this dialog under between
    #  uses (and across sessions).
    #
    PlaneSlideDlg(quarkx.clickform, 'plane_slide', editor, setup, action)
    
#
#  --- Now for the menus:
#
 
types = {
    ":e": "Entity",
    ":g": "Group",
    ":b": "Entity",
    ":p": "Poly"}


def slidePopup(o, editor):
    label = types[o.type]
    list = [makeEdgeSlide(o,editor),makePlaneSlide(o,editor)]
    popup=qmenu.popup('Slide %s'%label,list,hint="|Slide %s along tagged edge or above tagged plane"%label)
    return popup

#
# returns the menu item, and disables it if appropriate
#
def makeEdgeSlide(o, editor):
    label = types[o.type]
    item = qmenu.item("along/around tagged edge",
        EdgeSlideClick, "|Slides %s along or around tagged axis."%label.lower())
    tagged = gettaggededge(editor)
    if tagged is None:
        item.state = qmenu.disabled
        #
        # Add some stuff to the disabler to explain why the item
        #   is enabled.
        #
        item.hint = item.hint + "\n\nTag an edge in order to enable this menu item."
    else:
        item.o = o
        item.editor=editor
        item.tagged=tagged
    return item


def makePlaneSlide(o, editor):
    label = types[o.type]
    item = qmenu.item("above tagged plane",
        PlaneSlideClick, "|Slides %s above tagged plane."%label.lower())
    tagged = gettaggedplane(editor)
    if tagged is None:
        item.state = qmenu.disabled
        #
        # Add some stuff to the disabler to explain why the item
        #   is enabled.
        #
        item.hint = item.hint + "\n\nTag an plane in order to enable this menu item."
    else:
       item.o = o
       item.editor=editor
       item.tagged=tagged
    return item


for Type in (quarkpy.mapentities.PolyhedronType,
             quarkpy.mapentities.GroupType,
             quarkpy.mapentities.BrushEntityType):
             
    def newmenu(o, editor, oldmenu=Type.menu.im_func):
        menu = oldmenu(o, editor)
        menu[:0] = [slidePopup(o,editor)]
        return menu
        
    Type.menu = newmenu


# ----------- REVISION HISTORY ------------
#
#
# $Log: mapslide.py,v $
# Revision 1.9  2005/10/15 00:51:24  cdunde
# To reinstate headers and history
#
# Revision 1.6  2003/12/17 13:58:59  peter-b
# - Rewrote defines for setting Python version
# - Removed back-compatibility with Python 1.5
# - Removed reliance on external string library from Python scripts
#
# Revision 1.5  2001/08/11 02:53:02  tiglari
# refurbish & add slide above tagged plane facility
#
# Revision 1.4  2001/06/17 21:10:56  tiglari
# fix button captions
#
# Revision 1.3  2001/06/16 03:19:05  tiglari
# add Txt="" to separators that need it
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#
