"""   QuArK  -  Quake Army Knife

Python code to find faces with bad texture scales
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapbadtexscale.py,v 1.13 2009/09/25 22:55:56 danielpharos Exp $

Info = {
   "plug-in":       "Bad Texture Scale Finder",
   "desc":          "Finds brush faces with bad texture scales",
   "date":          "1 April 2002",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Version 6.3" }


from quarkpy.maputils import *
import quarkpy.mapmenus
import quarkpy.mapcommands
import quarkpy.dlgclasses
import quarkpy.mapsearch
from quarkpy import guiutils

import mapmadsel
import quarkx

#
# A `Live Edit' dialog.  Note the action buttons, which
#   use a rather convoluted technique to produce their
#   effects (when a button is bushed,
#   quarkpy.qmacro.MACRO_zapview is executed with an index
#   saying which, this calls the appropriate function of the
#   dialog, which was attached to the editor when executed).
#
# A ListBox would be better than a ComboBox for data entry,
#   but FormCFG.pas doesn't at the moment support ListBoxes.
#   In principle, this could be fixed.
#

class BadTexScaleDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (240,180)
    dfsep = 0.40

    dlgdef = """
        {
        Style = "9"
        Caption = "Bad Texture Scale Finder"

        micros: = {
          Typ = "C"
          Txt = "Bad Tex:"
          Items = "%s"
          Values = "%s"
          Hint = "These are the faces with bad texture scales.  Pick one," $0D " then push buttons on row below for action."
        }

          
        sep: = { Typ="S" Txt=""}

        buttons: = {
        Typ = "PM"
        Num = "1"
        Macro = "viewbadtex"
        Caps = "I"
        Txt = "Actions:"
        Hint1 = "Inspect the chosen one"
        }

        num: = {
          Typ = "EF1"
          Txt = "# found"
        }

        badangle: = {
          Typ = "EF001"
          Txt = "smallest angle: "
          Hint = "Faces whose texture axes make an angle smaller than this (degrees) are deemed bad"
        }
        
        badtexaxis: = {
          Typ = "EF001"
          Txt = "smallest axis: "
          Hint = "Faces with a texture axis smaller than this (units) are deemed bad"
        }
        
        
        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

    def inspect(self):
        index = eval(self.chosen)
        #
        # FIXME: dumb hack, revise mapmadsel
        #
        m = qmenu.item("",None)
        m.object=self.pack.baddies[index]
        mapmadsel.ZoomToMe(m)
        mapmadsel.SelectMe(m)
        #
        # Some grotty crap to set the mpp to the face page
        #
        Spec1 = qmenu.item("", quarkpy.mapmenus.set_mpp_page, "")
        Spec1.page = 3 # face properties page
        quarkpy.mapmenus.set_mpp_page(Spec1) 
        

#
# Define the viewbadtex macro here, put the definition into
#  quarkpy.qmacro, which is where macros called from delphi
#  live.
#
def macro_viewbadtex(self, index=0):
    editor = mapeditor()
    if editor is None: return
    if index==1:
        editor.badtexscaledlg.inspect()
        
quarkpy.qmacro.MACRO_viewbadtex = macro_viewbadtex

#
# For a face, for each other different face, the vertex furthest
#  away from the other face must be far enough away/
#
def texIsBad(face, badsize, badangle):
    (p0, p1, p2) = face.threepoints(2)
    u = (p1-p0)
    v = (p2-p0)
#    debug("%s - %.2d:%.2f"%(face.name,badsize,badangle))
    if abs(u)<badsize or abs(v)<badsize:
        return 1
#    debug('yo dude')
    cos = u.normalized*v.normalized
    angle = math.fabs(math.acos(u.normalized*v.normalized))/deg2rad
#    debug("%s: %.6f"%(face.name, angle))
    return angle<badangle
                    
           
def getBad(badsize, badangle, editor):
    baddies = []
    for face in editor.Root.findallsubitems("",":f"):
        if texIsBad(face,badsize, badangle):
            baddies.append(face)
    return baddies
    
def badClick(m):
    editor=mapeditor()

    badangle = guiutils.getSetupOption("badangle","5")
    badtexaxis = guiutils.getSetupOption("badtexaxis", "1")
    
    baddies = getBad(eval(badtexaxis), eval(badangle), editor)
    
    
    #
    # Here we start the Live Edit dialog invocation sequence.
    #  Data to be tracked during the life of the dialog goes
    #  here.
    #
    class pack:
        "stick stuff in this"
    pack.baddies=baddies
    pack.badangle=badangle
    pack.badtexaxis=badtexaxis
    pack.seen = 0
      
    #
    # This loads the relevant data into the dialog, gets
    #  recalled after changes.
    #
    def setup(self, pack=pack, editor=editor):
        self.pack=pack
        #
        # Part of the convolution for the buttons, to communicate
        #  which objects methods should be called when one pushed.
        # Cleaned up in onclosing below.
        #
        editor.badtexscaledlg=self
        
        #
        # Names and list-indexes of thin brushes
        #
        ran = range(len(pack.baddies))
        pack.slist = map(lambda obj,num:"%d) %s:%s"%(num+1,obj.parent.shortname,obj.shortname), pack.baddies, ran)
        pack.klist = map(lambda d:`d`, ran)

        self.src["micros$Items"] = ("\015").join(pack.slist)
        self.src["micros$Values"] = ("\015").join(pack.klist)
        if not pack.seen and len(ran)>0:
            self.src["micros"] = '0'
            self.chosen = '0'
            pack.seen = '0'
        elif len(ran)==0:
            self.chosen = ''
            pack.seen = ''
            
        #
        # Note the commas, EF..1 controls take 1-tuples as data
        #
        self.src["num"]=len(pack.klist),
        self.src["badangle"]=eval(pack.badangle),
        self.src["badtexaxis"]=eval(pack.badtexaxis),

        

    #
    # When data is entered, this gets executed.
    #
    def action(self, pack=pack, editor=editor):
        src = self.src
        #
        # note what's been chosen
        #
        self.chosen = src["micros"]
        #
        # see if thinness threshold has been changed
        #
        anglechange, newangle = guiutils.dlgNumberCheck(self, pack, "badangle", 5.00)
        axischange, newaxis = guiutils.dlgNumberCheck(self, pack, "badtexaxis", 1.00)
        if anglechange or axischange:
            pack.baddies = getBad(newaxis, newangle, editor)
            
    #
    # Cleanup when dialog closes (not needed if no mess has
    #  been created)
    #
    def onclosing(self,editor=editor):
        del editor.badtexscaledlg
        
    #
    # And here's the invocation. 2nd arg is a label for storing
    #  position info in setup.qrk.
    #
    BadTexScaleDlg(quarkx.clickform, 'badtexscale', editor, setup, action, onclosing)


quarkpy.mapsearch.items.append(qmenu.item('Find Bad Tex Scale', badClick,
 "|Find Bad Tex Scale:\n\nThis finds faces whose texture axes are almost parallel.|intro.mapeditor.menu.html#searchmenu"))

#$Log: mapbadtexscale.py,v $
#Revision 1.13  2009/09/25 22:55:56  danielpharos
#Added some missing import-statements.
#
#Revision 1.12  2005/11/27 05:56:33  cdunde
#Fixed function error due to python reliant
#conversion to python.dll, for string module.
#
#Revision 1.11  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.8  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.7  2003/03/21 05:47:45  cdunde
#Update infobase and add links
#
#Revision 1.6  2002/05/21 10:24:12  tiglari
#make collected item numbering start with 1)
#
#Revision 1.5  2002/05/21 09:16:16  tiglari
#fix problems with selection dialog: the first of two with identical names was
# always being chosen, and first item on list wouldn't load
#
#Revision 1.4  2002/05/12 08:00:15  tiglari
#minor corrections
#
#Revision 1.3  2002/04/30 22:55:33  tiglari
#add import quarkpy.mapsearch  statement
#
#Revision 1.2  2002/04/27 23:00:13  tiglari
#add import statement
#
#Revision 1.1  2002/04/01 08:31:48  tiglari
#modelled on mapmicrobrush.py, but some stuff abstracted into quarkpy.guiutils
#
