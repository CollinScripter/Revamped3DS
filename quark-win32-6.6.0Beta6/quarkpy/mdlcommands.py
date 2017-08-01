"""   QuArK  -  Quake Army Knife

Model editor commands menu.
"""

#
# $Header: /cvsroot/quark/runtime/quarkpy/mdlcommands.py,v 1.25 2012/07/09 18:11:33 cdunde Exp $


import quarkx
from mdlutils import *
import mdlhandles
import qmenu
import dlgclasses
import mdleditor


def newframeclick(m):
    editor = mapeditor()
    addframe(editor)

def matchframesclick(m):
    editor = mdleditor.mdleditor
    hasmostframes = None
    framecount = 0
    countsdontmatch = None
    old_comps = []
    new_comps = []
    for item in range(len(editor.layout.explorer.sellist)):
        if editor.layout.explorer.sellist[item].type == ":mc":
            if len(editor.layout.explorer.sellist[item].dictitems['Frames:fg'].subitems) > framecount:
                if framecount != 0:
                    countsdontmatch = 1
                framecount = len(editor.layout.explorer.sellist[item].dictitems['Frames:fg'].subitems)
                hasmostframes = item
            elif len(editor.layout.explorer.sellist[item].dictitems['Frames:fg'].subitems) < framecount:
                countsdontmatch = 1
    if countsdontmatch is not None:
        newsellist = []
        for item in range(len(editor.layout.explorer.sellist)):
            if editor.layout.explorer.sellist[item].type == ":mc":
                if item == hasmostframes:
                    newsellist = newsellist + [editor.layout.explorer.sellist[item]]
                    continue
                else:
                    old_comps = old_comps + [editor.layout.explorer.sellist[item]]
                    new_comp = editor.layout.explorer.sellist[item].copy()
                    donorcomp = editor.layout.explorer.sellist[hasmostframes].dictitems['Frames:fg']
                    compframesgroup = new_comp.dictitems['Frames:fg']
                    compframes = compframesgroup.subitems
                    compframecount = len(compframes)
                    complastframe = compframesgroup.subitems[len(compframes)-1]
                    framecount = 0
                    for frame in donorcomp.subitems:
                        if framecount < compframecount:
                            framecount = framecount + 1
                            continue
                        newframe = quarkx.newobj(frame.name)
                        newframe['Vertices'] = complastframe.dictspec['Vertices']
                        compframesgroup.appenditem(newframe)
                        framecount = framecount + 1
                    new_comp.dictitems['Frames:fg'] = compframesgroup
                    compframes = new_comp.findallsubitems("", ':mf')   # get all frames
                    for compframe in compframes:
                        compframe.compparent = new_comp # To allow frame relocation after editing.
                    new_comps = new_comps + [new_comp]
            else:
                newsellist = newsellist + [editor.layout.explorer.sellist[item]]
        undo = quarkx.action()
        for i in range(len(new_comps)):
            undo.exchange(old_comps[i], None)
            undo.put(editor.Root, new_comps[i])
        editor.ok(undo, "Match Frame Count")
        editor.layout.explorer.sellist = newsellist + new_comps


def checkcomponents(m):
    editor = mapeditor()
    componentlist = []
    for item in editor.layout.explorer.sellist:
        try:
            if item.type == ":mc":
                componentlist = componentlist + [item]
        except:
            continue
    # checks for matching frame counts.
    framecount = 0
    countsdontmatch = None
    donorcomp = None
    compcountlist = []
    for component in componentlist:
        compcountlist = compcountlist + [(component, len(component.dictitems['Frames:fg'].subitems))]
        if len(component.dictitems['Frames:fg'].subitems) > framecount:
            if framecount != 0:
                countsdontmatch = 1
            framecount = len(component.dictitems['Frames:fg'].subitems)
            donorcomp = component
        elif len(component.dictitems['Frames:fg'].subitems) < framecount:
            countsdontmatch = 1
    if countsdontmatch is not None:
        def showlist(donorcomp=donorcomp, compcountlist=compcountlist):
            list = ""
            for i in compcountlist:
                if i[0] == donorcomp:
                    continue
                list = list + "   " + i[0].shortname + " = " + str(i[1]) + " frames\n"
            return list
        if quarkx.msgbox("Selected components frames counts do not match.\n\n" + donorcomp.shortname + " has the most frames = " + str(framecount) + "\n\n" + showlist() + "\nDo you want to match these frames\nfor the other selected components?",MT_CONFIRMATION, MB_OK_CANCEL) != MR_OK:
            return
        matchframesclick(m)

    quarkx.msgbox("Component checking completed.", MT_INFORMATION, MB_OK)


def autobuild(m):
    editor = mapeditor()
    editor.Root.tryautoloadparts()
    editor.fileobject = editor.fileobject


NewFrame = qmenu.item("&Duplicate Current Frame", newframeclick, "|Duplicate Current Frame:\n\nThis copies a single frame that is currently selected and adds that copy to that model component's animation frames list.\n\nFor multiple frame copies use the 'Duplicate' function on the 'Edit' menu.|intro.modeleditor.menu.html#commandsmenu")

MatchFrameCount = qmenu.item("&Match Frame Count", matchframesclick, "|Match Frame Count:\n\nThis will duplicate the number of frames in the selected components with the one that has the most frames in it. It will not copy the frames, only how many there are.|intro.modeleditor.menu.html#commandsmenu")

CheckC = qmenu.item("Check Components", checkcomponents, "|Check Components:\n\nThis checks components for any errors in them that might exist.|intro.modeleditor.menu.html#commandsmenu")

AutoBuild = qmenu.item("Auto Assemble", autobuild, "|Auto Assemble:\n\nSome models are made up of seperate model files for example .md3 files. This function attempts to auto-load those related models model files and attach them using what is known as tags to match them up correctly.|intro.modeleditor.menu.html#commandsmenu")

NewFrame.state = qmenu.disabled
MatchFrameCount.state = qmenu.disabled
CheckC.state = qmenu.disabled

#
# Global variables to update from plug-ins.
#

items = [NewFrame, MatchFrameCount, qmenu.sep, CheckC, AutoBuild]
shortcuts = {"Ins": NewFrame}


def onclick(menu):
    pass


def CommandsMenu():
    "The Commands menu, with its shortcuts."
    return qmenu.popup("&Commands", items, onclick), shortcuts


def commandsclick(menu, oldcommand=onclick):
    oldcommand(menu)
    editor = mapeditor()
    if editor is None:
        return
    try:
        if (len(editor.layout.explorer.sellist) == 0) or editor.layout.explorer.sellist[0].type != ":mf" or len(editor.layout.explorer.sellist) > 1:
            NewFrame.state = qmenu.disabled
        else:
            NewFrame.state = qmenu.normal
        if (len(editor.layout.explorer.sellist) < 2):
            MatchFrameCount.state = qmenu.disabled
            CheckC.state = qmenu.disabled
        else:
            mc_count = 0
            for item in editor.layout.explorer.sellist:
                if item.type == ":mc":
                    mc_count = mc_count + 1
            if mc_count > 1:
                MatchFrameCount.state = qmenu.normal
                CheckC.state = qmenu.normal
            else:
                MatchFrameCount.state = qmenu.disabled
                CheckC.state = qmenu.disabled
    except AttributeError:
        pass


onclick = commandsclick


# ----------- REVISION HISTORY ------------
# $Log: mdlcommands.py,v $
# Revision 1.25  2012/07/09 18:11:33  cdunde
# Updated Tree-view RMB menu for correct single frame Duplication function in the Model Editor.
#
# Revision 1.24  2009/06/03 05:16:22  cdunde
# Over all updating of Model Editor improvements, bones and model importers.
#
# Revision 1.23  2009/04/28 21:30:56  cdunde
# Model Editor Bone Rebuild merge to HEAD.
# Complete change of bone system.
#
# Revision 1.22  2009/01/29 02:13:51  cdunde
# To reverse frame indexing and fix it a better way by DanielPharos.
#
# Revision 1.21  2008/07/26 03:37:38  cdunde
# Minor correction for frames matching count.
#
# Revision 1.20  2008/07/25 22:57:23  cdunde
# Updated component error checking and added frame matching and\or
# duplicating with independent names to avoid errors with other functions.
#
# Revision 1.19  2008/07/17 00:36:44  cdunde
# Added new function "Match Frame Count" to the Commands & RMB menus
# which duplicates the number of frames in selected components.
#
# Revision 1.18  2008/07/15 23:16:26  cdunde
# To correct typo error from MldOption to MdlOption in all files.
#
# Revision 1.17  2007/09/12 05:25:51  cdunde
# To move Make New Component menu function from Commands menu to RMB Face Commands menu and
# setup new function to move selected faces from one component to another.
#
# Revision 1.16  2007/09/07 23:55:29  cdunde
# 1) Created a new function on the Commands menu and RMB editor & tree-view menus to create a new
#      model component from selected Model Mesh faces and remove them from their current component.
# 2) Fixed error of "Pass face selection to Skin-view" if a face selection is made in the editor
#      before the Skin-view is opened at least once in that session.
# 3) Fixed redrawing of handles in areas that hints show once they are gone.
#
# Revision 1.15  2007/07/09 18:36:47  cdunde
# Setup editors Rectangle selection to properly create a new triangle if only 3 vertexes
# are selected and a new function to reverse the direction of a triangles creation.
#
# Revision 1.14  2007/07/02 22:49:42  cdunde
# To change the old mdleditor "picked" list name to "ModelVertexSelList"
# and "skinviewpicked" to "SkinVertexSelList" to make them more specific.
# Also start of function to pass vertex selection from the Skin-view to the Editor.
#
# Revision 1.13  2007/06/11 19:52:31  cdunde
# To add message box for proper vertex order of selection to add a triangle to the models mesh.
# and changed code for deleting a triangle to stop access violation errors and 3D views graying out.
#
# Revision 1.12  2007/04/22 21:06:04  cdunde
# Model Editor, revamp of entire new vertex and triangle creation, picking and removal system
# as well as its code relocation to proper file and elimination of unnecessary code.
#
# Revision 1.11  2007/04/19 03:30:27  cdunde
# First attempt to get newly created triangles to draw correctly on the Skin-view. Still needs work.
#
# Revision 1.10  2007/04/17 13:27:48  cdunde
# Added safeguard on menu item until it can be used correctly.
#
# Revision 1.9  2007/04/17 12:55:34  cdunde
# Fixed Duplicate current frame function to stop Model Editor views from crashing
# and updated its popup help and Infobase link description data.
#
# Revision 1.8  2007/04/16 16:55:07  cdunde
# Stopped Add Triangle and Delete Triangle from causing errors and added menu links to the Infobase.
#
# Revision 1.7  2005/10/15 00:47:57  cdunde
# To reinstate headers and history
#
# Revision 1.4  2001/03/15 21:07:49  aiv
# fixed bugs found by fpbrowser
#
# Revision 1.3  2001/02/01 22:03:15  aiv
# RemoveVertex Code now in Python
#
# Revision 1.2  2000/10/11 19:09:00  aiv
# added cvs header and triangle adding dialog (not finished)
#
#