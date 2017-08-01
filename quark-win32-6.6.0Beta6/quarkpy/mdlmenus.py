"""   QuArK  -  Quake Army Knife

Model editor pop-up menus.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mdlmenus.py,v 1.56 2012/07/09 18:11:33 cdunde Exp $



import quarkx
from qdictionnary import Strings
import qmenu
from mdlutils import *
import mdlcommands

### Setup for future use. See mapmenus.py for examples
MdlEditMenuCmds = []
MdlEditMenuShortcuts = {}


#
# Model Editor MdlQuickKey shortcuts
# The area below is for future def's for those MdlQuickKeys, see mapmenus.py for examples.



# Note: the function *names* are used to look up the key from Defaults.qrk
# See mapmenus.py file for examples of these key names def's.
# To start using function def are made in the above section.
# Each def becomes a keyname which is inserted in the MdlQuickKeys list below and
# in the Defaults.qrk file in the Keys:config section of Model:config.
MdlQuickKeys = []


def runimporter(m):
    from qmacro import mdlimport
    try:
        mdlf = mdlimport[m.text]
    except:
        return
    editor = mapeditor()
    files = quarkx.filedialogbox("Select File", m.text, mdlf[0], 0)
    if len(files) != 0:
        mdlf[1](None, files[0], None)

def runexporter(m):
    from qmacro import mdlexport
    try:
        mdlf = mdlexport[m.text]
    except:
        return
    editor = mapeditor()
    files = quarkx.filedialogbox("Save file as...", m.text, mdlf[0], 1)
    if len(files) != 0:
        mdlf[1](None, files[0], None)


#
# Menu bar builder
#
def BuildMenuBar(editor):
    import mdlmgr
    import mdlcommands
    import mdlsearch
    import mdltoolbars
    import mdloptions

    def modelimporters():
        from qmacro import mdlimport, mdlimportmenuorder
        mdlimportmenu = []
        orderedlist = mdlimportmenuorder.keys()
        orderedlist.sort()
        for menuindex in orderedlist:
            for importer in mdlimportmenuorder[menuindex]:
                mdlimportmenu = mdlimportmenu + [qmenu.item(importer, runimporter, "load a "+str(importer).replace('Importer', 'model'))]
        if mdlimportmenu == []:
            mdlimportmenu = mdlimportmenu + [qmenu.item("none available", None, "no importers available")]
        return mdlimportmenu

    def modelexporters():
        from qmacro import mdlexport, mdlexportmenuorder
        mdlexportmenu = []
        orderedlist = mdlexportmenuorder.keys()
        orderedlist.sort()
        for menuindex in orderedlist:
            for exporter in mdlexportmenuorder[menuindex]:
                format = str(exporter).split(' ')[0]
                format = format.replace('.', '')
                mdlexportmenu = mdlexportmenu + [qmenu.item(exporter, runexporter, "|save as a "+str(exporter).replace('Exporter', 'model')+".\n\nFor details on how to setup and export this type of model format press F1 again or click on the InfoBase button.|intro.modeleditor.exportmodelformats.html#"+str(format))]
        if mdlexportmenu == []:
            mdlexportmenu = mdlexportmenu + [qmenu.item("none available", None, "no exporters available")]
        return mdlexportmenu

    File1, sc1 = qmenu.DefaultFileMenu()
    MdlImport = qmenu.popup("Model &Importers", modelimporters(), runimporter, "|Model Importers:\n\nList of all available Python plugins model importers to load a model.", "intro.modeleditor.menu.html#filemenu")
    MdlExport = qmenu.popup("&Model Exporters", modelexporters(), runexporter, "|Model Exporters:\n\nList of all available Python plugins model exporters to save a model.", "intro.modeleditor.menu.html#filemenu")
    NewFile1items = []
    for item in range(len(File1.items)):
        if File1.items[item] is None:
            NewFile1items = NewFile1items + [qmenu.sep]
        else:
            if File1.items[item].text == "&Open...":
                NewFile1items = NewFile1items + [File1.items[item]] + [qmenu.sep ,MdlImport, MdlExport, qmenu.sep]
            else:
                NewFile1items = NewFile1items + [File1.items[item]]
    File1.items = NewFile1items

    if editor.layout is None:
        l1 = []
        lcls = None
        lclick = None
    else:
        l1, sc2 = editor.layout.getlayoutmenu()
        sc1.update(sc2)   # merge shortcuts
        if len(l1):
            l1.append(qmenu.sep)
        lcls = editor.layout.__class__
        lclick = editor.layout.layoutmenuclick
    for l in mdlmgr.LayoutsList:
        m = qmenu.item('%s layout' % l.shortname, editor.setlayoutclick)
        m.state = (l is lcls) and qmenu.radiocheck
        m.layout = l
        l1.append(m)
    Layout1 = qmenu.popup("&Layout", l1, lclick)

    Edit1, sc2 = qmenu.DefaultEditMenu(editor)
    sc1.update(sc2)   # merge shortcuts
    l1 = MdlEditMenuCmds
    if len(l1):
        Edit1.items = Edit1.items + [qmenu.sep] + l1
    sc1.update(MdlEditMenuShortcuts)   # merge shortcuts

    Search1, sc2 = mdlsearch.SearchMenu()
    sc1.update(sc2)   # merge shortcuts

    Commands1, sc2 = mdlcommands.CommandsMenu()
    sc1.update(sc2)   # merge shortcuts

    Tools1, sc2 = mdltoolbars.ToolsMenu(editor, mdltoolbars.toolbars)
    sc1.update(sc2)   # merge shortcuts

    Options1, sc2 = mdloptions.OptionsMenu()
    sc1.update(sc2)   # merge shortcuts
    l1 = plugins.mdlgridscale.GridMenuCmds
    l2 = [qmenu.sep]
    l3 = plugins.mdltools.RulerMenuCmds
    l4 = [qmenu.sep]
    if len(l1):
        Options1.items = l1 + l2 + l3 + l4 + Options1.items
        sc1.update(sc2)   # merge shortcuts

    return [File1, Layout1, Edit1, quarkx.toolboxmenu, Search1, Commands1, Tools1, Options1], sc1



def MdlBackgroundMenu(editor, view=None, origin=None):
    "Menu that appears when the user right-clicks on nothing in one of the"
    "editor views or Skin-view or on something or nothing in the tree-view."

    import mdlhandles
    import mdlsearch
    import mdlcommands
    import mdloptions

    File1, sc1 = qmenu.DefaultFileMenu()
    Search1, sc2 = mdlsearch.SearchMenu()
    Commands1, sc2 = mdlcommands.CommandsMenu()
    sc1.update(sc2)   # merge shortcuts
    BoneOptions, FaceSelOptions, VertexSelOptions = mdloptions.OptionsMenuRMB()
    sellist = editor.layout.explorer.sellist

    undo, redo = quarkx.undostate(editor.Root)
    if undo is None:   # to undo
        Undo1 = qmenu.item(Strings[113], None)
        Undo1.state = qmenu.disabled
    else:
        Undo1 = qmenu.macroitem(Strings[44] % undo, "UNDO")
    if redo is None:
        extra = []
    else:
        extra = [qmenu.macroitem(Strings[45] % redo, "REDO")]
    if origin is None:
        paste1 = qmenu.item("Paste", editor.editcmdclick)
    else:
        paste1 = qmenu.item("Paste here", editor.editcmdclick, "paste objects at '%s'" % str(editor.aligntogrid(origin)))
        paste1.origin = origin
    paste1.cmd = "paste"
    paste1.state = not quarkx.pasteobj() and qmenu.disabled
    extra = extra + [qmenu.sep, paste1]

    if view is not None:
        if view.info["viewname"] != "skinview":
            import mdloptions

            def keyframeclick(editor=editor):
                if len(sellist) == 0:
                    return
                frame1parent = frame2parent = None
                framecount = 0
                for item in sellist:
                    if item.type == ":mf":
                        framecount = framecount + 1
                        if frame1parent is None:
                            frame1parent = item.parent.parent
                        elif frame2parent is None:
                            frame2parent = item.parent.parent
                if frame2parent == frame1parent and framecount == 2:
                    sellistPerComp = []
                    IPF = float(1/quarkx.setupsubset(SS_MODEL, "Display")["AnimationIPF"][0])
                    frameindex1 = frameindex2 = None
                    framecomp = None
                    for item in sellist:
                        if frameindex2 is not None:
                            break
                        if item.type == ":mf":
                            frames = item.parent.subitems
                            for frame in range(len(frames)):
                                if frames[frame].name == item.name and frameindex1 is None:
                                    frameindex1 = frame
                                    framecomp = item.parent.parent
                                    break
                                elif frames[frame].name == item.name and frameindex2 is None:
                                    frameindex2 = frame
                                    break
                    FrameGroup = framecomp.dictitems['Frames:fg'].subitems # Get all the frames for this component.
                    sellistPerComp = [[framecomp, [FrameGroup[frameindex1], FrameGroup[frameindex2]]]]
                    if framecomp.dictspec.has_key("tag_components"):
                        comp_names = framecomp.dictspec['tag_components'].split(", ")
                        for comp_name in comp_names:
                            comp = editor.Root.dictitems[comp_name]
                            if comp.dictspec.has_key("Tags"):
                                comp_tags = comp.dictspec['Tags'].split(", ")
                            if comp_name == framecomp.name:
                                continue
                            for item in range(len(sellistPerComp)):
                                if comp_name == sellistPerComp[item][0].name:
                                    break
                                if item == len(sellistPerComp)-1:
                                    comp_frames = comp.dictitems['Frames:fg'].subitems # Get all the frames for this component.
                                    sellistPerComp = sellistPerComp + [[comp, [comp_frames[frameindex1], comp_frames[frameindex2]]]]

                        group = framecomp.name.split("_")[0]
                        misc_group = editor.Root.dictitems['Misc:mg']
                        for tag_name in comp_tags:
                            tag = misc_group.dictitems[group + "_" + tag_name + ":tag"]
                            tagframes = tag.subitems
                            sellistPerComp = sellistPerComp + [[tag, [tagframes[frameindex1], tagframes[frameindex2]]]]
                    for comp in sellist:
                        if comp.type == ":mc":
                            if comp.name == framecomp.name:
                                continue
                            for item in range(len(sellistPerComp)):
                                if comp.name == sellistPerComp[item][0].name:
                                    break
                                if item == len(sellistPerComp)-1:
                                    FrameGroup = comp.dictitems['Frames:fg'].subitems # Get all the frames for this component.
                                    sellistPerComp = sellistPerComp + [[comp, [FrameGroup[frameindex1], FrameGroup[frameindex2]]]]
                            if comp.dictspec.has_key("tag_components"):
                                comp_names = comp.dictspec['tag_components'].split(", ")
                                for comp_name in comp_names:
                                    comp2 = editor.Root.dictitems[comp_name]
                                    if comp2.dictspec.has_key("Tags"):
                                        comp_tags = comp2.dictspec['Tags'].split(", ")
                                    for item in range(len(sellistPerComp)):
                                        if comp_name == sellistPerComp[item][0].name:
                                            break
                                        if item == len(sellistPerComp)-1:
                                            comp_frames = comp2.dictitems['Frames:fg'].subitems # Get all the frames for this component.
                                            sellistPerComp = sellistPerComp + [[comp2, [comp_frames[frameindex1], comp_frames[frameindex2]]]]
                                group = comp.name.split("_")[0]
                                misc_group = editor.Root.dictitems['Misc:mg']
                                for tag_name in comp_tags:
                                    tag = misc_group.dictitems[group + "_" + tag_name + ":tag"]
                                    tagframes = tag.subitems
                                    for item in range(len(sellistPerComp)):
                                        if tag.name == sellistPerComp[item][0].name:
                                            break
                                        if item == len(sellistPerComp)-1:
                                            sellistPerComp = sellistPerComp + [[tag, [tagframes[frameindex1], tagframes[frameindex2]]]]

                def linear_interpolation_click(m, editor=editor):
                    import mdlmgr
                    mdlmgr.savefacesel = 1
                    frame1parent = frame2parent = None
                    framecount = 0
                    for item in sellist:
                        if item.type == ":mf":
                            framecount = framecount + 1
                            if frame1parent is None:
                                frame1parent = item.parent.parent
                            elif frame2parent is None:
                                frame2parent = item.parent.parent
                    if frame2parent == frame1parent and framecount == 2:
                        KeyframeLinearInterpolation(editor, sellistPerComp, IPF, frameindex1, frameindex2)

                linear_interpolation = qmenu.item("&Linear Interpolation", linear_interpolation_click, "|Linear Interpolation:\n\nThis will create movement in a straight line from the first frame selected to the second frame selected for all components selected (if more then one).|intro.modeleditor.rmbmenus.html#keyframecommands")

                keyframe_menu = [linear_interpolation]
                return keyframe_menu

            bboxpop = qmenu.popup("BBox Commands", mdlhandles.PolyHandle(origin, None).comp_extras_menu(editor, view), hint="clicked x,y,z pos %s"%str(editor.aligntogrid(origin)))
            tagpop = qmenu.popup("Tag Commands", mdlhandles.TagHandle(origin).extrasmenu(editor, view), hint="clicked x,y,z pos %s"%str(editor.aligntogrid(origin)))
            bonepop = qmenu.popup("Bone Commands", mdlhandles.BoneCenterHandle(origin,None,None).menu(editor, view), hint="clicked x,y,z pos %s"%str(editor.aligntogrid(origin)))
            mdlfacepop = qmenu.popup("Face Commands", mdlhandles.ModelFaceHandle(origin).menu(editor, view), hint="clicked x,y,z pos %s"%str(editor.aligntogrid(origin)))
            vertexpop = qmenu.popup("Vertex Commands", mdlhandles.VertexHandle(origin).menu(editor, view), hint="clicked x,y,z pos %s"%str(editor.aligntogrid(origin)))
            keyframepop = qmenu.popup("Keyframe Commands", keyframeclick(), hint="|Keyframe Commands:\n\nKeyframe functions create additional animation frames for movement between two selected frames.\n\nThe number of additional frames to be created is the amount set on the 'Animation' toolbar 'IPF' button - 1.\n\nTo use these functions you must select two frames of the same component. If they are not consecutive frames (one right after the other) then all frames in between the two will be replaced with the newly created frames.\n\nYou can also select other components for their same frames to be included. Click 'InfoBase' for Tags info.|intro.modeleditor.rmbmenus.html#viewsrmbmenus")

            keyframepop.state = qmenu.disabled
            frame1parent = frame2parent = None
            framecount = 0
            for item in sellist:
                if item.type == ":mf":
                    framecount = framecount + 1
                    if frame1parent is None:
                        frame1parent = item.parent.parent
                    elif frame2parent is None:
                        frame2parent = item.parent.parent
            if frame2parent == frame1parent and framecount == 2:
                keyframepop.state = qmenu.normal

            AFR = quarkx.setupsubset(SS_MODEL,"Options").getint("AutoFrameRenaming")
            if AFR == 0:
                mdloptions.AutoFrameRenaming.state = qmenu.normal
            else:
                mdloptions.AutoFrameRenaming.state = qmenu.checked

            if len(sellist) >= 1:
                import mdlmgr
                item = sellist[0]
                if (item.type == ':fg' or item.type == ':mf' or item.type == ':bg' or item.type == ':bone') and (quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] != "1"):
                    bonepop.state = qmenu.normal
                comp =  editor.layout.componentof(item)
            if sellist == [] or quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1" or (len(sellist) == 1 and sellist[0].type != ':mf'):
                vertexpop.state = qmenu.disabled
            else:
                for item in sellist:
                    if item.type != ':bg' and item.type != ':bone' and item.type != ':fg' and item.type != ':mf':
                        vertexpop.state = qmenu.disabled
                        break
            def backbmp1click(m, view=view, form=editor.form):
                import qbackbmp
                qbackbmp.MdlBackBmpDlg(form, view)
            backbmp1 = qmenu.item("Background image...", backbmp1click, "|Background image:\n\nWhen selected, this will open a dialog box where you can choose a .bmp image file to place and display in the 2D view that the cursor was in when the RMB was clicked.\n\nClick on the 'InfoBase' button below for full detailed information about its functions and settings.|intro.mapeditor.rmb_menus.noselectionmenu.html#background")
            if editor.ModelFaceSelList != []:
                extra = extra + [qmenu.sep, bboxpop, tagpop, bonepop, mdlfacepop, vertexpop, Search1, Commands1, qmenu.sep, keyframepop, qmenu.sep, BoneOptions, FaceSelOptions, VertexSelOptions, mdloptions.AutoFrameRenaming, qmenu.sep] + TexModeMenu(editor, view) + [qmenu.sep, backbmp1]
            else:
                extra = extra + [qmenu.sep, bboxpop, tagpop, bonepop, vertexpop, Search1, Commands1, qmenu.sep, keyframepop, qmenu.sep, BoneOptions, FaceSelOptions, VertexSelOptions, mdloptions.AutoFrameRenaming, qmenu.sep] + TexModeMenu(editor, view) + [qmenu.sep, backbmp1]
        else:
            def resetSkinview(menu, editor=editor, view=view):
                viewWidth, viewHeight = view.clientarea
                try:
                    texWidth, texHeight = editor.Root.currentcomponent.currentskin["Size"]
                except:
                    texWidth, texHeight = view.clientarea
                if texWidth > texHeight:
                    view.info["scale"] = viewWidth / texWidth
                elif texWidth < texHeight:
                    view.info["scale"] = viewHeight / texHeight
                elif viewWidth > viewHeight:
                    view.info["scale"] = viewHeight / texHeight
                else:
                    view.info["scale"] = viewWidth / texWidth
                view.info["center"] = view.screencenter = quarkx.vect(0,0,0)
                setprojmode(view)

            def rescaleskinhandles(menu, editor=editor):
                skinrescale(editor)

            def autoscaleskinhandles(menu, editor=editor):
                if not MdlOption("AutoScale_SkinHandles"):
                    quarkx.setupsubset(SS_MODEL, "Options")['AutoScale_SkinHandles'] = "1"
                else:
                    quarkx.setupsubset(SS_MODEL, "Options")['AutoScale_SkinHandles'] = None

            ResetSkinView = qmenu.item("&Reset Skin-view", resetSkinview, "|Reset Skin-view:\n\nIf the model skinning image becomes 'lost', goes out of the Skin-view, you can use this function to reset the view and bring the model back to its starting position.|intro.modeleditor.skinview.html#funcsnmenus")
            RescaleSkinHandles = qmenu.item("Rescale Skin &Handles", rescaleskinhandles, "|Rescale Skin Handles:\n\nIf the skin handles do not fit the image, you can use this function to rescale the handles to fit the current skin texture size.|intro.modeleditor.skinview.html#funcsnmenus")
            AutoScaleSkinHandles = qmenu.item("&Auto Scale", autoscaleskinhandles, "|Auto Scale:\n\nIf active, automatically scales the skin handles\nand Component's UVs to fit the current skin image texture size.|intro.modeleditor.skinview.html#funcsnmenus")
            skinviewcommands = qmenu.popup("Vertex Commands", mdlhandles.SkinHandle(origin, None, None, None, None, None, None).menu(editor, view), hint="clicked x,y,z pos %s"%str(editor.aligntogrid(origin)))
            skinviewoptions = qmenu.popup("Skin-view Options", mdlhandles.SkinHandle(origin, None, None, None, None, None, None).optionsmenu(editor, view), hint="clicked x,y,z pos %s"%str(editor.aligntogrid(origin)))
            extra = [qmenu.sep, ResetSkinView, qmenu.sep, AutoScaleSkinHandles, RescaleSkinHandles, qmenu.sep, skinviewcommands, skinviewoptions]

            AutoScaleSkinHandles.state = quarkx.setupsubset(SS_MODEL,"Options").getint("AutoScale_SkinHandles")

        # Add importer/exporter specific menu items
        from mdlmgr import SFTexts, IEfile
        sfbtn = editor.layout.buttons["sf"]
        for filetype in range(len(SFTexts)):
            if sfbtn.caption == SFTexts[filetype]:
                try:
                    filename = IEfile[filetype]
                    extra = filename.newmenuitems(editor, extra)
                except:
                    pass

    return [Undo1] + extra



def set_mpp_page(btn):
    "Switch to another page on the Multi-Pages Panel."

    editor = mapeditor(SS_MODEL)
    if editor is None: return
    editor.layout.mpp.viewpage(btn.page)


#
# Entities pop-up menus.
#

def MultiSelMenu(sellist, editor):
    return BaseMenu(sellist, editor)



def BaseMenu(sellist, editor):
    "The base pop-up menu for a given list of objects."

    mult = len(sellist)>1 or (len(sellist)==1 and sellist[0].type==':g')
    Force1 = qmenu.item(("&Force to grid", "&Force everything to grid")[mult],
      editor.ForceEverythingToGrid)
    if not MdlOption("GridActive") or quarkx.setupsubset(SS_MODEL, "Display")["GridStep"][0] == 0:
        Force1.state = qmenu.disabled

    Cut1 = qmenu.item("&Cut", editor.editcmdclick)
    Cut1.cmd = "cut"
    Copy1 = qmenu.item("Cop&y", editor.editcmdclick)
    Copy1.cmd = "copy"
    paste1 = qmenu.item("Paste", editor.editcmdclick)
    paste1.cmd = "paste"
    paste1.state = not quarkx.pasteobj() and qmenu.disabled
    Duplicate1 = qmenu.item("Dup&licate", editor.editcmdclick)
    Duplicate1.cmd = "dup"
    Delete1 = qmenu.item("&Delete", editor.editcmdclick)
    Delete1.cmd = "del"

    modelframe = 0
    for item in editor.layout.explorer.sellist:
        if item.type  == ":mf":
            modelframe += 1
    if modelframe == 1:
        return [Cut1, Copy1, paste1, qmenu.sep, Delete1]
    else:
    #  return [Force1, qmenu.sep, Duplicate1, qmenu.sep, Cut1, Copy1, paste1, qmenu.sep, Delete1]
        return [Duplicate1, qmenu.sep, Cut1, Copy1, paste1, qmenu.sep, Delete1]

# ----------- REVISION HISTORY ------------
#
#
#$Log: mdlmenus.py,v $
#Revision 1.56  2012/07/09 18:11:33  cdunde
#Updated Tree-view RMB menu for correct single frame Duplication function in the Model Editor.
#
#Revision 1.55  2011/05/30 20:46:32  cdunde
#Added frame name change to complete updatings and AutoFrameRenaming function.
#
#Revision 1.54  2011/02/11 18:55:20  cdunde
#Added InfoBase section and direct links for Model Editor exporters to assist people in their use.
#
#Revision 1.53  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.52  2010/06/25 05:27:59  cdunde
#Setup 'Auto Scaling' function for the Skin-view that resets the skin handles and Component's UV's
#to fit the currently selected and viewable skin texture of that Component.
#
#Revision 1.51  2010/06/13 15:37:55  cdunde
#Setup Model Editor to allow importing of model from main explorer File menu.
#
#Revision 1.50  2010/05/04 05:30:52  cdunde
#Added new function to rescale Skin-view handles to current skin texture size.
#
#Revision 1.49  2009/11/10 22:49:55  cdunde
#Added update to fix broken RMB menu.
#
#Revision 1.48  2009/11/10 18:58:55  cdunde
#To fix broken RMB menu.
#
#Revision 1.47  2009/10/21 06:28:26  cdunde
#Update to keyframes functions for handling tags.
#
#Revision 1.46  2009/10/20 21:42:03  cdunde
#Correction of previous menu link update.
#
#Revision 1.45  2009/10/20 21:09:45  cdunde
#Update of InfoBase menu links.
#
#Revision 1.44  2009/10/20 07:03:21  cdunde
#Added keyframe fill-in frames creation support for single and multiple component selections.
#
#Revision 1.43  2009/09/07 01:38:45  cdunde
#Setup of tag menus and icons.
#
#Revision 1.42  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.41  2009/05/03 08:06:06  cdunde
#Edit menu, moved Duplicate and separated Delete from other items.
#
#Revision 1.40  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.39  2009/03/04 23:32:16  cdunde
#For proper importer exporter listing one menus, code by DanielPharos.
#
#Revision 1.38  2009/01/27 05:03:01  cdunde
#Full support for .md5mesh bone importing with weight assignment and other improvements.
#
#Revision 1.37  2008/11/19 06:16:23  cdunde
#Bones system moved to outside of components for Model Editor completed.
#
#Revision 1.36  2008/10/04 05:48:06  cdunde
#Updates for Model Editor Bones system.
#
#Revision 1.35  2008/09/22 23:38:21  cdunde
#Updates for Model Editor Linear and Bone handles.
#
#Revision 1.34  2008/09/15 04:47:47  cdunde
#Model Editor bones code update.
#
#Revision 1.33  2008/08/08 05:35:49  cdunde
#Setup and initiated a whole new system to support model bones.
#
#Revision 1.32  2008/07/26 03:41:33  cdunde
#Add functions to RMB menus.
#
#Revision 1.31  2008/07/15 23:16:26  cdunde
#To correct typo error from MldOption to MdlOption in all files.
#
#Revision 1.30  2008/07/14 18:06:53  cdunde
#To sort the exporters menu.
#
#Revision 1.29  2008/06/28 14:44:52  cdunde
#Some minor corrections.
#
#Revision 1.28  2008/06/14 08:18:41  cdunde
#Fixed error if model import file selection window is closed without selecting anything.
#
#Revision 1.27  2008/06/04 03:56:40  cdunde
#Setup new QuArK Model Editor Python model import export system.
#
#Revision 1.26  2008/01/26 23:28:55  cdunde
#To compute for different texture and Skin-view sizes for Reset Skin-view function.
#
#Revision 1.25  2008/01/25 20:58:03  cdunde
#Setup function to reset Skin-view.
#
#Revision 1.24  2007/11/22 05:13:47  cdunde
#Separated editors background image dialogs and setup to save all of their settings.
#
#Revision 1.23  2007/10/06 20:15:00  cdunde
#Added Ruler Guides to Options menu for Model Editor.
#
#Revision 1.22  2007/10/04 01:50:48  cdunde
#To fix error if RMB is clicked in a view for the popup menu
#but nothing is selected in the tree-view.
#
#Revision 1.21  2007/09/16 18:16:17  cdunde
#To disable all forcetogrid menu items when a grid is inactive.
#
#Revision 1.20  2007/09/15 18:36:52  cdunde
#To make "Vertex Commands" RMB active only if a model frame is selected.
#
#Revision 1.19  2007/09/15 18:17:54  cdunde
#To turn off "Vertex Commands" menu when Linear Handle button is active.
#
#Revision 1.18  2007/09/11 00:09:37  cdunde
#Added paste to tree-view RMB menu when a component sub-folder is selected.
#
#Revision 1.17  2007/09/05 18:43:10  cdunde
#Minor comment addition and grammar corrections.
#
#Revision 1.16  2007/07/14 22:42:44  cdunde
#Setup new options to synchronize the Model Editors view and Skin-view vertex selections.
#Can run either way with single pick selection or rectangle drag selection in all views.
#
#Revision 1.15  2007/07/09 18:59:23  cdunde
#Setup RMB menu sub-menu "skin-view Options" and added its "Pass selection to Editor views"
#function. Also added Skin-view Options to editors main Options menu.
#
#Revision 1.14  2007/06/03 22:50:55  cdunde
#To add the model mesh Face Selection RMB menus.
#(To add the RMB Face menu items when the cursor is not over one of the selected model mesh faces)
#
#Revision 1.13  2007/05/16 19:39:46  cdunde
#Added the 2D views gridscale function to the Model Editor's Options menu.
#
#Revision 1.12  2007/04/27 17:27:42  cdunde
#To setup Skin-view RMB menu functions and possable future MdlQuickKeys.
#Added new functions for aligning, single and multi selections, Skin-view vertexes.
#To establish the Model Editors MdlQuickKeys for future use.
#
#Revision 1.11  2007/04/22 22:41:50  cdunde
#Renamed the file mdltools.py to mdltoolbars.py to clarify the files use and avoid
#confliction with future mdltools.py file to be created for actual tools for the Editor.
#
#Revision 1.10  2007/04/16 16:55:59  cdunde
#Added Vertex Commands to add, remove or pick a vertex to the open area RMB menu for creating triangles.
#Also added new function to clear the 'Pick List' of vertexes already selected and built in safety limit.
#Added Commands menu to the open area RMB menu for faster and easer selection.
#
#Revision 1.9  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.8  2006/11/29 07:00:28  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.7.2.1  2006/11/28 00:55:35  cdunde
#Started a new Model Editor Infobase section and their direct function links from the Model Editor.
#
#Revision 1.7  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.4  2000/08/21 21:33:04  aiv
#Misc. Changes / bugfixes
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#