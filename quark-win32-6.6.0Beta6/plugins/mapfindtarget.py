"""   QuArK  -  Quake Army Knife

Python code to find things targetting and targetted by an entity
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapfindtarget.py,v 1.7 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Target Finder",
   "desc":          "Finds entities targetting and targetted by something",
   "date":          "May 11 2002",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Version 6.3" }


from quarkpy.maputils import *
import quarkpy.mapmenus
import quarkpy.mapcommands
import quarkpy.mapentities
import quarkpy.dlgclasses
from quarkpy import guiutils
import quarkpy.mapsearch

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

class FindTargetDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (240,190)
    dfsep = 0.40

    dlgdef = """
        {
        Style = "9"
        Caption = "Target Finder"

       found: = {
          Typ = "C"
          Txt = "List of found:"
          Items = "%s"
          Values = "%s"
          Hint = "These are the entities found.  Pick one," $0D " then push buttons on row below for action."
        }

        num: = {
          Typ = "EF1"
          Txt = "# found"
        }
          
        sep: = { Typ="S" Txt=""}

        buttons: = {
        Typ = "PM"
        Num = "1"
        Macro = "viewtargetted"
        Caps = "I"
        Txt = "Actions:"
        Hint1 = "Inspect the chosen one"
        }
        
        sep: = { Typ="S" Txt=""}

        specific: = {
          Typ = "E"
          Txt = "specific:"
          Hint = "This is the targetting specific whose value is being checked"
        }
        
        value: = {
          Typ = "E"
          Txt = "value:"
          Hint = "Things with value of the specific above are to be found"
        }
        
        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

    def inspect(self):
        index = eval(self.src["found"])
        #
        # FIXME: dumb hack, revise mapmadsel
        #
        m = qmenu.item("",None)
        m.object=self.pack.found[index]
        mapmadsel.ZoomToMe(m)
        mapmadsel.SelectMe(m)
        #
        # Some grotty crap to set the mpp to the face page
        #
        Spec1 = qmenu.item("", quarkpy.mapmenus.set_mpp_page, "")
        Spec1.page = 1 # specifics page
        quarkpy.mapmenus.set_mpp_page(Spec1) 
        

#
# Define the viewtargetted macro here, put the definition into
#  quarkpy.qmacro, which is where macros called from delphi
#  live.
#
def macro_viewtargetted(self, index=0):
    editor = mapeditor()
    if editor is None: return
    if index==1:
        editor.findtargetdlg.inspect()
        
quarkpy.qmacro.MACRO_viewtargetted = macro_viewtargetted

           
def getSpecVal(spec, val, editor):
    found = []
    for item in editor.Root.findallsubitems("",":b")+editor.Root.findallsubitems("",":e"):
        if item[spec]==val:
            found.append(item)
    return found
    

def findClick(m, spec=None, val=None):
    editor=mapeditor()
    #
    # Here we start the Live Edit dialog invocation sequence.
    #  Data to be tracked during the life of the dialog goes
    #  here.  
    #
    class pack:
        "stick stuff in this"
    pack.slist = []
    pack.klist = []
    pack.seen = 0
        
    def setup(self, pack=pack, editor=editor, spec=spec, val=val):
        self.pack=pack
        #
        # Part of the convolution for the buttons, to communicate
        #  which objects methods should be called when one pushed.
        # Cleaned up in onclosing below.
        #
        editor.findtargetdlg=self
        
        if self.src['specific'] is None:
            if spec:
                self.src['specific']=spec
            
        if self.src['value'] is None:
            if val:
                self.src['value']=val
            
        if self.src['value']:
            targetted = getSpecVal(spec,self.src['value'], editor)
            ran = range(len(targetted))
            pack.slist = map(lambda obj,num:"%d) %s:%s"%(num+1, obj.parent.shortname,obj.shortname), targetted, ran)
            pack.klist = map(lambda d:`d`, ran)

            #
            #  wtf doesn't this work, item loads but function is trashed
            #
             
            self.src["found$Items"] = "\015".join(pack.slist)
            self.src["found$Values"] = "\015".join(pack.klist)
            self.src["num"]=len(pack.klist),
            if not pack.seen and len(ran)>0:
                pack.seen = 1
                self.src["found"] = '0'
                self.chosen = '0'
            elif len(ran)==0:
                self.src["found"] = ''
                self.chosen = ''
            pack.found = targetted

    #
    # When data is entered, this gets executed.
    #
    def action(self, pack=pack, editor=editor):
        pass

    #
    # Cleanup when dialog closes (not needed if no mess has
    #  been created)
    #
    def onclosing(self,editor=editor):
        del editor.findtargetdlg
        
    #
    # And here's the invocation. 2nd arg is a label for storing
    #  position info in setup.qrk.
    #
    FindTargetDlg(quarkx.clickform, 'findtarget', editor, setup, action, onclosing)


def targetpopup(o):

    #
    # If the entity we're clicking on has a target specific, we might
    #  want things with the same targetname value, and vice-versa,
    #  this target/targetname interchange is inherently confusing.
    #
    def targettingClick(m, o=o):
        findClick(m, 'target', o['targetname'])

    def targettedClick(m, o=o):
        findClick(m, 'targetname', o[m.spec])
        
    targettingItem = qmenu.item('entities targetting this one', targettingClick, "|Find entities targetting this entity")
    if o['targetname'] is None:
        targettingItem.state=qmenu.disabled

    list = [targettingItem]
    
    for specific in o.dictspec.keys():
        if specific[-6:] == 'target':
            item = qmenu.item('entities targetted by '+specific, targettedClick, "|Find entities targetted by the specific %s"%specific)
            item.spec = specific
            list.append(item)
 
    return qmenu.popup("Find targetted/ing", list, None,
       "|commands for finding entities targetting and targetted by this one")


def entmenu(o, editor, oldmenu=quarkpy.mapentities.EntityType.menu.im_func):
    "point entity menu"
    menu = oldmenu(o, editor)

    menu[:0] = [targetpopup(o),
                qmenu.sep]
    return menu

quarkpy.mapentities.EntityType.menu = entmenu

def brushmenu(o, editor, oldmenu=quarkpy.mapentities.BrushEntityType.menu.im_func):
    "brush entity menu"
    menu = oldmenu(o, editor)

    menu[:0] = [targetpopup(o),
                qmenu.sep]
    return menu

quarkpy.mapentities.BrushEntityType.menu = brushmenu


#$Log: mapfindtarget.py,v $
#Revision 1.7  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.4  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.3  2002/05/21 07:06:10  tiglari
#fix problems with selection dialog (loadiing first selection when appropriate)
#
#Revision 1.2  2002/05/20 11:07:54  tiglari
#fix bug whereby if all targetted items had the same name, the first one
#  of that name would be selected.  Also now preloading with first element works
#
#Revision 1.1  2002/05/18 05:21:39  tiglari
#Suggestion by quantum_red
#
