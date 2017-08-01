"""   QuArK  -  Quake Army Knife

Implementation of QuArK Map editor's "Options" menu
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapoptions.py,v 1.19 2008/12/05 07:44:06 cdunde Exp $



import quarkx
from qdictionnary import Strings
from maputils import *
import qmenu



def ToggleOption(item):
    "Toggle an option in the setup."
    tag = item.tog
    setup = apply(quarkx.setupsubset, item.sset)
    newvalue = not setup[tag]
    setup[tag] = "1"[:newvalue]
    # We don't need to reloadsetup for the Duplicators.
    # This speeds up redrawing 3 times faster and keeps the 2D views from going blank.
    if item.text == "&Ignore Duplicators":
        pass
    else:
        if item.sendupdate[newvalue]:
            quarkx.reloadsetup()

def IgnoreDupClick(item):
    # DanielPharos: A big hack. We need to call UNDO on all the duplicators to apply the changes...
    # So we simply move the duplicators onto themselves! MUHAHA!
    def UndoMoveDups(undo, RootItem):
        import operator
        list = RootItem.subitems
        for item in list:
            try:
                if item.type==":d":
                    listindex = operator.indexOf(list, item)
                    if listindex == len(list)-1:
                        undo.move(item, RootItem)
                    else:
                        undo.move(item, RootItem, list[listindex+1])
            except:
                pass
            UndoMoveDups(undo, item)
    ToggleOption(item)
    editor = mapeditor()
    if editor is None:
        return
    undo = quarkx.action()
    UndoMoveDups(undo, editor.Root)
    editor.ok(undo, "")


def StartConsoleLogClick(m):
    "Start and stop console logging output to Console.txt file."
    if not MapOption("ConsoleLog"):
        quarkx.setupsubset(SS_MAP, "Options")['ConsoleLog'] = "1"
        try:
            quarkx.startconsolelog()
        except:
            pass
        consolelog.state = qmenu.checked
    else:
        quarkx.setupsubset(SS_MAP, "Options")['ConsoleLog'] = None
        quarkx.stopconsolelog()
        consolelog.state = qmenu.normal


def ClearConsoleLogClick(m):
    "Clears the Console.txt file."
    try:
        quarkx.clearconsolelog()
    except:
        pass

def Config1Click(item):
    "Configuration Dialog Box."
    quarkx.openconfigdlg()

def Plugins1Click(item):
    "Lists the loaded plug-ins."
    import plugins
    group = quarkx.newobj("Loaded Plug-ins:config")
    for p in plugins.LoadedPlugins:
        txt = p.__name__.split(".")[-1]
        ci = quarkx.newobj("%s.toolbar" % txt)
        try:
            info = p.Info
        except:
            info = {}
        for spec, arg in info.items():
            ci[spec] = arg
        ci["File"] = p.__name__
        ci["Form"] = "PluginInfo"
        try:
            ci.shortname = info["plug-in"]
        except:
            pass
        group.appenditem(ci)
    quarkx.openconfigdlg("List of Plug-ins", group)


def Options1Click(menu):
    for item in menu.items:
        try:
            setup = apply(quarkx.setupsubset, item.sset)
            item.state = not (not setup[item.tog]) and qmenu.checked
        except:
            try:
                tas = item.tas
                item.state = (quarkx.setupsubset(SS_MAP, "Options").getint("TexAntiScroll")==tas) and qmenu.radiocheck
            except:
                pass
        if item == lineThicknessItem:
            item.thick = getLineThickness()
            item.text = "Set Line Thickness (%1.0f)"%item.thick

def toggleitem(txt, toggle, sendupdate=(1,1), sset=(SS_MAP,"Options"), proc=None, hint=None):
    if not proc is None:
        item = qmenu.item(txt, proc, hint)
    else:
        item = qmenu.item(txt, ToggleOption, hint)
    item.tog = toggle
    item.sset = sset
    item.sendupdate = sendupdate
    return item


def TasOption(item):
    quarkx.setupsubset(SS_MAP, "Options").setint("TexAntiScroll", item.tas)
    quarkx.reloadsetup(1)

def texantiscroll(txt, mode, hint="|Default/Sticky/Axis-sticky texture:\n\nIn QuArK, the textures are attached to polyhedrons in such a way that they follow all its movements. However, for easier texture alignment, you can set these options that only apply when scrolling polyhedrons (not rotating nor zooming).\n\nSTICKY : the textures don't move when you look at it standing in front of the face.\n\nAXIS-STICKY : the textures don't move when you look at it from the nearest axis direction.\n\nTo mimic the way QuArK and most other Quake editors work, choose AXIS-STICKY.|intro.mapeditor.menu.html#optionsmenu"):
    item = qmenu.item(txt, TasOption, hint)
    item.tas = mode
    return item


class LineThickDlg(SimpleCancelDlgBox):
    #
    # dialog layout
    #
    size = (160, 75)
    dfsep = 0.7 
    
    dlgdef = """
    {
        Style = "9"
        Caption = "Line Thickness Dialog"

        thick: =
        {
        Txt = "Line Thickness:"
        Typ = "EF1"
        Hint = "Needn't be an integer."
        }
        cancel:py = {Txt="" }
    }
    """

    def __init__(self, form, editor, m):
    
        src = quarkx.newobj(":")
        thick =  quarkx.setupsubset(SS_MAP,"Options")['linethickness']
        if thick:
            thick=eval(thick)
        else:
            thick=3
        src["thick"] = thick,
        self.src = src
        SimpleCancelDlgBox.__init__(self,form,src)

    def ok(self):
        pass
        thick = self.src['thick']    
        if thick is not None:
            thick, = thick
            if thick==3:
                quarkx.setupsubset(SS_MAP,"Options")['linethickness']=""
            else:
                quarkx.setupsubset(SS_MAP,"Options")['linethickness']="%4.2f"%thick

def getLineThickness():
     thick =  quarkx.setupsubset(SS_MAP,"Options")['linethickness']
     if thick:
         return eval(thick)
     else:
         return 3
     
def getThinLineThickness():
     thick =  getLineThickness()
     if thick > 1:
         thick = thick-1
     return thick
     
def setLineThick(m):
    editor = mapeditor()
    if editor is None:
        return
    LineThickDlg(quarkx.clickform, editor, m)
    
lineThicknessItem = qmenu.item("Set Line Thickness (3)",setLineThick,"|Set Line Thickness:\n\nThis lets you set the thickness of certain lines that are drawn on the map, such as leak lines, portals, and targetting arrows.|intro.mapeditor.menu.html#optionsmenu")


#
# Global variables to update from plug-ins.
#
consolelog = qmenu.item("&Log Console", StartConsoleLogClick, "|Log Console:\n\nWhen active this will write everything that is printed to the console to a text file called 'Console.txt' which is located in QuArK's main folder.|intro.mapeditor.menu.html#optionsmenu")

clearconsolelog = qmenu.item("&Clear Console Log", ClearConsoleLogClick, "|Clear Console Log:\n\nWhen clicked this will clear everything that is printed to the text file called 'Console.txt' which is located in QuArK's main folder.|intro.mapeditor.menu.html#optionsmenu")

items = [

    toggleitem("&Delete unused faces && polys", "DeleteFaces", (0,0),
      hint="|Delete unused faces & polys:\n\nWhen you distort polyhedrons, some faces might become no longer used by the polyhedron, or the whole polyhedron could maybe become invalid (e.g. if it has no interior any more). When the option 'Delete unused faces & polys' is checked, QuArK will tell you about this and ask you if it should delete the no-longer-used objects.|intro.mapeditor.menu.html#optionsmenu"),

    toggleitem("&Secondary red lines", "RedLines2", (1,1),
      hint="|Secondary red lines:\n\nDisplay two red lines per view instead of just one. These red lines let you select which part of the map is to be considered 'visible' on the other view. Invisible parts are grayed out and not selectable with the mouse.|intro.mapeditor.menu.html#optionsmenu"),

    toggleitem("3D &Models in textured views", "Entities", (1,1), (SS_GENERAL,"3D view"),
      hint="|3D Models in textured views:\n\nDisplay actual models in solid and textured views.\n\nNote that this is not implemented for all the supported games yet. If you want to help about this, you are welcome !|intro.mapeditor.menu.html#optionsmenu"),

    toggleitem("&Quantize angles", "AutoAdjustNormal", (0,0),
      hint="|Quantize angles:\n\nIf 'Quantize angles' is checked, you cannot set any angle for faces and entities : you can only set 'round' values. This command works like a grid for angles. You can set the step of this grid in the Configuration dialog box, Map, Building, 'Force angle to'.|intro.mapeditor.menu.html#optionsmenu"),

    toggleitem("&Paste objects at screen center", "Recenter", (0,0),
      hint="|Paste objects at screen center:\n\nIf 'Paste objects at screen center' is checked, polyhedrons and entities are pasted from the clipboard near the screen center. If this option is not checked, they are pasted exactly where they were when you copied them to the clipboard. The latter option is useful to make several copies with a fixed step between them, but can be confusing because the pasted objects may be completely off the screen.|intro.mapeditor.menu.html#optionsmenu"),

    toggleitem("&Ignore groups marked so when building map", "IgnoreToBuild", (0,0),
      hint="|Ignore groups marked so when building map:\n\nTo check complex maps with the game, you can choose not to include some parts of it in the test play. Do to so, you mark some groups as 'Ignore to build map' (right-click on a group for this command).\n\nMarked groups are actually ignored only if this option 'Ignore groups marked so when building map' is checked. You can uncheck it to play the whole map again without unmarking all groups one by one.|intro.mapeditor.menu.html#optionsmenu"),

    toggleitem("&Negative polys really dig in 3D views", "ComputePolys", (1,1),
      hint="|Negative polys really dig in 3D views:\n\nIf this option is off, negative polyhedrons are shown as normal polyhedrons in textured view so that you can easily edit them. When this option is on, digging is performed and you don't see the negative polyhedron at all, but only the hole it made.\n\nIn non-software modes, in a future version of QuArK, the negative polyhedron itself should not be completely invisible, but transparent.|intro.mapeditor.menu.html#optionsmenu"),

    toggleitem("&Ignore Duplicators", "IgnoreDup", (1,1), proc=IgnoreDupClick,
      hint="|Ignore Duplicators:\n\nHides all duplicators and templates from being seen in the editors views.|intro.mapeditor.menu.html#optionsmenu"),


    qmenu.sep,
    texantiscroll("Default texture movement", 0),
    texantiscroll("Sticky textures", 1),
    texantiscroll("Axis-sticky textures", 2),
    toggleitem("&Don't center L-square","DontCenterThreePoints", (0,0),
      hint="|Don't center L-square:\n\nIf this item is on, threepoints aren't re-centered on face in texture positioning.|intro.mapeditor.menu.html#optionsmenu"),
    lineThicknessItem
    ]
shortcuts = { }


def OptionsMenu():
    "The Options menu, with its shortcuts."

    PlugIns = qmenu.item("List of Plug-ins...", Plugins1Click, "lists loaded plug-ins")
    Config1 = qmenu.item("Confi&guration...", Config1Click,  hint = "|Configuration...:\n\nThis leads to the Configuration-Window where all elements of QuArK are setup. From the way the Editor looks and operates to Specific Game Configuration and Mapping or Modeling variables.\n\nBy pressing the F1 key one more time, or clicking the 'InfoBase' button below, you will be taken directly to the Infobase section that covers all of these areas, which can greatly assist you in setting up QuArK for a particular game you wish to map or model for.|intro.configuration.html")
    Options1 = qmenu.popup("&Options", items+[qmenu.sep, PlugIns, Config1, qmenu.sep, consolelog, clearconsolelog], Options1Click)
    return Options1, shortcuts

# ----------- REVISION HISTORY ------------
#
#
#$Log: mapoptions.py,v $
#Revision 1.19  2008/12/05 07:44:06  cdunde
#Small update.
#
#Revision 1.18  2008/12/03 08:37:13  cdunde
#Added functions for console logging and clearing of that log to the options menu.
#
#Revision 1.17  2007/12/21 22:47:37  cdunde
#To avoid unneeded reloadsetup for Duplicators for faster and better redraws.
#
#Revision 1.16  2007/12/21 20:39:23  cdunde
#Added new Templates functions and Templates.
#
#Revision 1.15  2007/12/14 21:48:00  cdunde
#Added many new beizer shapes and functions developed by our friends in Russia,
#the Shine team, Nazar and vodkins.
#
#Revision 1.14  2006/05/01 05:34:32  cdunde
#To link Configuration menu item directly to its Infobase section.
#
#Revision 1.13  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.10  2003/12/17 13:58:59  peter-b
#- Rewrote defines for setting Python version
#- Removed back-compatibility with Python 1.5
#- Removed reliance on external string library from Python scripts
#
#Revision 1.9  2003/03/28 02:55:24  cdunde
#To update info and add infobase links.
#
#Revision 1.8  2003/03/24 10:36:57  tiglari
#remove debug statement
#
#Revision 1.7  2003/03/23 07:30:13  tiglari
#add getThinLineThickness function (1 unit less that ordinary line)
#
#Revision 1.6  2003/03/23 06:30:19  tiglari
#change close to cancel button in linethickness dlg to fix error
# noted by cdunde
#
#Revision 1.5  2003/03/21 10:56:08  tiglari
#support for line-thickness specified by mapoption
#
#Revision 1.4  2001/08/28 22:43:54  tiglari
#'Adjust angles automatically' renamed to `Quantize angles'
#
#Revision 1.3  2001/04/01 06:50:33  tiglari
#don't recenter threepoints option added
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#
