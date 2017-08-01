"""   QuArK  -  Quake Army Knife

Model Editor Buttons and implementation of editing commands
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mdlbtns.py,v 1.45 2012/07/10 02:04:16 cdunde Exp $

import quarkx
import qtoolbar
from qdictionnary import Strings
import qutils
from mdlutils import *

#
# Drag-and-drop functions
#

def componentof(obj):
    while not (obj is None):
        obj = obj.parent
        if obj is None:
            return None
        else:
            if obj.type == ':mc':
                return obj


def droptarget(editor, newitem):
    "Where is the new item to be inserted ? (parent, insertbefore)"
    ex = editor.layout.explorer
    fs = ex.focussel     # currently selected item
    if not newitem is None:
        if newitem.type==':mc':
            return editor.Root, None
        elif newitem.type==':mf':
            if not fs is None:
                c=componentof(fs)
                if c is None:
                    c=editor.Root.currentcomponent
                return c.dictitems['Frames:fg'], None
        elif newitem.type in ('.pcx', '.tga', '.dds', '.png', '.jpg', '.bmp', '.ftx', '.vtf', '.m8'):
            if not fs is None:
                c=componentof(fs)
                if c is None:
                    c=editor.Root.currentcomponent
                return c.dictitems['Skins:sg'], None
        elif newitem.type==(':bbg') or newitem.type==(':p'):
            return editor.Root.dictitems['Misc:mg'], None
        elif newitem.type==(':tag'):
            return editor.Root.dictitems['Misc:mg'], None
        elif newitem.type==(':bone'):
            if editor.Root["no_skeleton"]=='1':
                return editor.Root.dictitems['Misc:mg'], None
            else: 
                if not fs is None:
                    c=componentof(fs)
                    if c is None:
                        c=editor.Root
                    try:
                        return c.dictitems['Skeleton:bg'], None
                    except:
                        pass
    # cannot insert new item at all...
    return None, None


def fixname(parent, newitem):
    name = newitem.shortname
    comparenbr = 0
    if newitem.type == ":bone":
        comparenbr = comparenbr + 1
    for item in parent.subitems:
        if item.shortname.startswith(name):
            comparenbr = comparenbr + 1
    if comparenbr != 0:
        newitem.shortname = newitem.shortname + " " + str(comparenbr)
    return newitem


def dropitemsnow(editor, newlist, text=Strings[544], center="S"):
    "Drop new items into the given map editor."
    #
    # Known values of "center" :
    #   <vector>: scroll at the given point
    #   "S":      scroll at screen center or at the selected object's center
    #   "0":      don't scroll at all (ignores the Recenter setting, use when the target position shouldn't be changed)
    #   "+":      scroll at screen center or don't scroll at all
    #
    if len(newlist)==0:
        return

    incompatible_items = 0 # To filter out components from other items.
    for item in newlist:
        if item.type == ":mc":
            incompatible_items = 1
        if item.type != ":mc" and incompatible_items == 1:
            msg = Strings[-107]
            quarkx.msgbox(msg, MT_ERROR, MB_OK)
            return

    if incompatible_items == 0:
        undo = quarkx.action()
    delta = None
    if str(center) != "0":
        recenter = MapOption("Recenter", editor.MODE)
        if recenter:
            if str(center) != "+":
                delta = editor.layout.screencenter()
            else:
                delta = quarkx.vect(0,0,0)
        else:
            if str(center) != "+":
                bbox = quarkx.boundingboxof(newlist)
                if bbox is None: #DECKER
                    bbox = (quarkx.vect(-1,-1,-1),quarkx.vect(1,1,1)) #DECKER create a minimum bbox, in case a ;incl="defpoly" is added to an object in prepareobjecttodrop()
                if str(center)=="S":
                    bbox1 = quarkx.boundingboxof(editor.visualselection())
                    if bbox1 is None:
                        center = editor.layout.screencenter()
                    else:
                        center = (bbox1[0]+bbox1[1])*0.5
                delta = center - (bbox[0]+bbox[1])*0.5
            else:
                delta = quarkx.vect(0,0,0)
        delta = editor.aligntogrid(delta)
    for newitem in newlist:
        nparent, nib = droptarget(editor, newitem)
        if nparent is None and newitem.type == ".wl":
            import os
            image_type_list = ['.tga', '.dds', '.png', '.jpg', '.bmp', '.ftx', '.vtf', '.m8']  # Order from best to worst (personal judgement).
            try:
                for type in image_type_list:
                    if os.path.exists(newitem['path'] + "/" + newitem.shortname + type):
                        nparent = editor.Root.currentcomponent.dictitems['Skins:sg']
                        skin = quarkx.newobj(newitem.shortname + type)
                        image = quarkx.openfileobj(newitem['path'] + "/" + newitem.shortname + type)
                        skin['Image1'] = image.dictspec['Image1']
                        skin['Size'] = image.dictspec['Size']
                        newitem = skin
                        break
            except:
                try:
                    path = quarkx.setupsubset(SS_GAMES, 'ModelEditor')['Directory']
                    for type in image_type_list:
                        if os.path.exists(path + "/" + newitem.shortname + type):
                            nparent = editor.Root.currentcomponent.dictitems['Skins:sg']
                            skin = quarkx.newobj(newitem.shortname + type)
                            image = quarkx.openfileobj(path + "/" + newitem.shortname + type)
                            skin['Image1'] = image.dictspec['Image1']
                            skin['Size'] = image.dictspec['Size']
                            newitem = skin
                            break
                except:
                    pass
        if nparent is None:
            undo.cancel()    # not required, but it's better when it's done
            msg = Strings[-151]
            quarkx.msgbox(msg, MT_ERROR, MB_OK)
            return
        if not newitem.isallowedparent(nparent):
            undo.cancel()    # not required, but it's better when it's done
            quarkx.beep()
            quarkx.msgbox("Use Duplicate function\nto copy this item.", qutils.MT_ERROR, qutils.MB_OK)
            return
        new = newitem.copy()
        prepareobjecttodrop(editor, new)
        try:
            if delta:
                new.translate(delta)
        except:
            pass
        if incompatible_items == 0:
            new = fixname(nparent, new)
            undo.put(nparent, new, nib)

    if incompatible_items == 0:
        undo.ok(editor.Root, text)
    if newlist[0].type == ":mf":
        compframes = editor.Root.currentcomponent.findallsubitems("", ':mf')   # get all frames
        for compframe in compframes:
            compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.
    editor.layout.actionmpp()
    return 1


def dropitemnow(editor, newitem):
    "Drop a new item into the given map editor."
    dropitemsnow(editor, [newitem], Strings[616])


def replacespecifics(obj, mapping):
    pass


def prepareobjecttodrop(editor, obj):
    "Call this to prepare an object to be dropped. It replaces [auto] Specifics."
    def resetbones(bone, editor=editor): # Clears the bones of data that cause errors.
        bones = bone.findallsubitems("", ':bone')
        comp_name = editor.Root.currentcomponent.name
        for bone in bones:
            bone['component'] = comp_name
            bone.vtxlist  = {}
            bone.vtx_pos  = {}
            if bone.dictspec.has_key('comp_list'):
                bone['comp_list'] = comp_name
    if obj.type == ":bone":
        resetbones(obj)
    if obj.type == ":bg":
        for bone in obj.subitems:
            resetbones(bone)

    oldincl = obj[";incl"]
    obj[";desc"] = None
    obj[";incl"] = None


def mdlbuttonclick(self):
    "Drop a new model object from a button."
    editor = mapeditor(SS_MODEL)
    if editor is None: return
    dropitemsnow(editor, map(lambda x: x.copy(), self.dragobject))

#
# General editing commands.
#

def deleteitems(editor, root, list):
    undo = quarkx.action()
    text = None
    bonelist = []
    listcopy = []
    for item in list:
        if item.type != ":bone":
            listcopy = listcopy + [item]
    for s in list:
        if s.type == ":bone":
            bonelist = addtolist(bonelist, s)
    list = listcopy + bonelist
    import operator
    group = editor.Root.dictitems['Skeleton:bg']
    bonelist = group.findallsubitems("", ':bone') # Get all bones in the old group.
    multi_comps = -1
    for s in list:
        if s.type == ":mc":
            multi_comps = multi_comps + 1
    for s in list:
        if s.type == ":mc":
            removecomp(editor, s.name, undo, multi_comps)
            multi_comps = multi_comps - 1
        if s.type == ":bone":
            if not s in group.subitems:
                bone_index = operator.indexOf(list, s)
                list, bonelist = removebone(editor, s.name, undo, list, bonelist)
                s = list[bone_index]
            else:
                for bone in group.subitems:
                    if (bone.dictspec['parent_name'] == s.name) and (not bone in list):
                        newbone = bone.copy()
                        newbone['parent_name'] = "None"
                        undo.exchange(bone, None)
                        undo.put(group, newbone)
        if s.type == ":p" or s.type == ":bbg":
            if s.type == ":bbg":
                for bbox in s.subitems:
                    if editor.ModelComponentList['bboxlist'].has_key(bbox.name):
                        del editor.ModelComponentList['bboxlist'][bbox.name]
            else:
                if editor.ModelComponentList['bboxlist'].has_key(s.name):
                    del editor.ModelComponentList['bboxlist'][s.name]
            
        if text is None:
            text = Strings[582] % s.shortname
        else:
            text = Strings[579]   # multiple items selected
        undo.exchange(s, None)   # replace all selected objects with None
    if text is None:
        undo.cancel()
        quarkx.beep()
    else:
        editor.ok(undo, text)


def edit_del(editor, m=None):
    deleteitems(editor, editor.Root, editor.visualselection())


def edit_copy(editor, m=None):
    quarkx.copyobj(editor.visualselection())


def edit_cut(editor, m=None):
    edit_copy(editor, m)
    edit_del(editor, m)


def edit_paste(editor, m=None):
    newitems = quarkx.pasteobj(1)
    try:
        origin = m.origin
    except:
        origin = "+"
    if not dropitemsnow(editor, newitems, Strings[543], origin):
        pass
    else:
        for item in newitems:
            if item.type == ":mc":
                quarkx.beep()
                quarkx.msgbox("Use Duplicate function\nto copy a component.", qutils.MT_ERROR, qutils.MB_OK)
                return
            elif item.type == ":mf":
                quarkx.beep()
                quarkx.msgbox("Use Duplicate function\nto copy a frame.", qutils.MT_ERROR, qutils.MB_OK)
                return
        return


def edit_dup(editor, m=None):
    if not dropitemsnow(editor, editor.visualselection(), Strings[541], "0"):
        quarkx.beep()
    else:
        for item in range(len(editor.visualselection())):
            if editor.visualselection()[item].type == ":mc":
                comp_copied_name = editor.visualselection()[item].name
                # Checks for component names matching any new components and changes the new one's
                # name(s) if needed to avoid dupes which cause problems in other functions.
                components = editor.Root.findallsubitems("", ':mc')   # find all components
                itemdigit = None
                if editor.visualselection()[item].shortname[len(editor.visualselection()[item].shortname)-1].isdigit():
                    itemdigit = ""
                    count = len(editor.visualselection()[item].shortname)-1
                    while count >= 0:
                        if editor.visualselection()[item].shortname[count] == " ":
                            count = count - 1
                        elif editor.visualselection()[item].shortname[count].isdigit():
                            itemdigit = str(editor.visualselection()[item].shortname[count]) + itemdigit
                            count = count - 1
                        else:
                            break
                    itembasename = editor.visualselection()[item].shortname.split(itemdigit)[0]
                else:
                    itembasename = editor.visualselection()[item].shortname

                name = None
                comparenbr = 0
                new_comp = editor.layout.explorer.sellist[0].copy()
                for comp in components:
                    if not itembasename.endswith(" ") and comp.shortname.startswith(itembasename + " "):
                        continue
                    if comp.shortname.startswith(itembasename):
                        getnbr = comp.shortname.replace(itembasename, '')
                        if getnbr == "":
                            nbr = 0
                        else:
                            nbr = int(getnbr)
                        if nbr > comparenbr:
                            comparenbr = nbr
                        nbr = comparenbr + 1
                        name = itembasename + str(nbr)
                if name is not None:
                    pass
                else:
                    name = editor.visualselection()[item].shortname
                new_comp.shortname = name
                editor.ModelComponentList['tristodraw'][new_comp.name] = editor.ModelComponentList['tristodraw'][comp_copied_name]
                editor.ModelComponentList[new_comp.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
                undo = quarkx.action()
                undo.put(editor.Root, new_comp)
                editor.ok(undo, "duplicate")
                compframes = new_comp.dictitems['Frames:fg'].subitems   # all frames
                for compframe in compframes:
                    compframe.compparent = new_comp # To allow frame relocation after editing.

            if editor.visualselection()[item].type == ":mf":
                # Checks for component frame names matching any new components frame names and changes
                # the new one's name(s) if needed to avoid dupes which cause problems in other functions.
                compframes = editor.visualselection()[item].parent.subitems   # all frames
                itemdigit = None
                if editor.visualselection()[item].shortname[len(editor.visualselection()[item].shortname)-1].isdigit():
                    itemdigit = ""
                    count = len(editor.visualselection()[item].shortname)-1
                    while count >= 0:
                        if editor.visualselection()[item].shortname[count] == " ":
                            count = count - 1
                        elif editor.visualselection()[item].shortname[count].isdigit():
                            itemdigit = str(editor.visualselection()[item].shortname[count]) + itemdigit
                            count = count - 1
                        else:
                            break
                    itembasename = editor.visualselection()[item].shortname.split(itemdigit)[0]
                else:
                    itembasename = editor.visualselection()[item].shortname

                name = None
                comparenbr = 0
                count = 0
                stopcount = 0
                for compframe in compframes:
                    if not itembasename.endswith(" ") and compframe.shortname.startswith(itembasename + " "):
                        if stopcount == 0:
                            count = count + 1
                        continue
                    if compframe.shortname.startswith(itembasename):
                        stopcount = 1
                        getnbr = compframe.shortname.replace(itembasename, '')
                        if getnbr == "":
                            nbr = 0
                        else:
                            nbr = int(getnbr)
                        if nbr > comparenbr:
                            comparenbr = nbr
                            count = count + 1
                        nbr = comparenbr + 1
                        name = itembasename + str(nbr)
                    if stopcount == 0:
                        count = count + 1
                if name is not None:
                    pass
                else:
                    name = editor.visualselection()[item].shortname
                editor.visualselection()[item].shortname = name
                # Places the new frame at the end of its group of frames of the same name.
                itemtomove = editor.visualselection()[item]
                itemtomoveparent = itemtomove.parent
                itemtomoveparent.removeitem(itemtomove)
                try:
                    itemtomoveparent.insertitem(count, itemtomove)
                except:
                    itemtomoveparent.insertitem(count-1, itemtomove)


def edit_newbboxgroup(editor, m=None):
    "Create a new group in a 'Misc' folder for BBoxes."

    # List selected objects.
    list = editor.visualselection()

    # Only allow polys to be moved.
    ex = editor.layout.explorer
    nparent = editor.Root.dictitems['Misc:mg']
    nib = nparent
    ex.expand(nparent)
    if len(list) == 1 and list[0].type == ":mg":
        new_list = []
        for item in list[0].subitems:
            if not item.name.endswith(":p"):
                new_list += [item]
        list = new_list
    else:
        for item in list:
            if item.type != ":p":
                quarkx.beep()
                quarkx.msgbox("Improper selection!\n\nA BBox sub-group can only accept BBox polys within that folder.\nCurrent selected items to be placed into the new sub-group are not all BBoxes.\n\nAlso, you can not place a sub-group inside another sub-group.", qutils.MT_INFORMATION, qutils.MB_OK)
                return

    # Build a new group object.
    newgroup = quarkx.newobj("Bounding Boxes:bbg")
    newgroup['show'] = (1.0,)

    # The undo to perform this functions action.
    undo = quarkx.action()
    undo.put(nparent, newgroup, nib)   # actually create the new group
    moveitems = 1
    for item in ex.sellist:
        if item.type != ":p":
            moveitems = 0
            break
    if moveitems == 1:
        for s in list:
            if s is not editor.Root and s is not nparent:
                undo.move(s, newgroup)   # put the selected items into the new group
    undo.ok(editor.Root, Strings[556])

    #
    # Initially expand the new group.
    #

    ex.expand(newgroup)


def edit_newskingroup(editor, m=None):
    "Create a new group in a 'Skins' folder."

    #
    # List selected objects.
    #

    list = editor.visualselection()

    #
    # Only allow skins to be moved.
    #

    ex = editor.layout.explorer
    nib = None
    if len(list) == 1 and list[0].type == ":sg":
        nparent = list[0]
        ex.expand(nparent)
        new_list = []
        for item in list[0].subitems:
            if not item.name.endswith(":ssg"):
                new_list += [item]
        list = new_list
    else:
        for item in list:
            if (item.name.endswith(":ssg")) or (item.parent.type != ":sg"):
                quarkx.beep()
                quarkx.msgbox("Improper selection!\n\nA skin sub-group can only be added\nby having the Skins group selected.\n\nOr a skin(s) within that folder selected\nwhich will be placed into and\nname the new sub-group.\n\nAlso, you can not place a sub-group\ninside another sub-group.", qutils.MT_INFORMATION, qutils.MB_OK)
                return
        #
        # Determine where to drop the new group.
        #
        nparent = ex.focussel     # currently selected item
        if not nparent is None:
            nib = nparent
            nparent = nparent.parent
        if nparent is None:
            nparent = editor.Root
            nib = None

    if len(list) == 0:
        quarkx.beep()
        quarkx.msgbox("Improper selection!\n\nA skin sub-group can only be added\nby having the Skins group selected.\n\nOr a skin(s) within that folder selected\nwhich will be placed into and\nname the new sub-group.\n\nAlso, you can not place a sub-group\ninside another sub-group.", qutils.MT_INFORMATION, qutils.MB_OK)
        return

    #
    # Build a new group object.
    #

    newgroup = quarkx.newobj("sub-group:ssg")
    for item in range(len(ex.sellist)):
        if ex.sellist[item].type == ":sg":
            break
        if ex.sellist[item].name.find(".") != 1:
            name = ex.sellist[item].name.split(".")[0]
            name = name.split()[0]
            newgroup.shortname = "sub-group " + name
            break

    #
    # The undo to perform this functions action
    #

    for item in ex.sellist:
        if item.type == "" or item.type == ":ssg":
            quarkx.beep()
            quarkx.msgbox("Improper selection!\n\nA skin sub-group can only be added\nby having the Skins group selected.\n\nOr a skin(s) within that folder selected\nwhich will be placed into and\nname the new sub-group.\n\nAlso, you can not place a sub-group\ninside another sub-group.", qutils.MT_INFORMATION, qutils.MB_OK)
            return
    undo = quarkx.action()
    undo.put(nparent, newgroup, nib)   # actually create the new group
    moveitems = 1
    for item in ex.sellist:
        if item.type == ":sg":
            moveitems = 0
    if moveitems == 1:
        for s in list:
            if s is not editor.Root and s is not nparent:
                undo.move(s, newgroup)   # put the selected items into the new group
    undo.ok(editor.Root, Strings[556])

    #
    # Initially expand the new group.
    #

    ex.expand(newgroup)


def updateUsedTextures(reserved=None):
    "Updates the 'Used Skin Textures.qtxfolder' then opens the texture browser with the currentcomponent's currentskin selected."

    editor = mapeditor()
    if editor is None:
        seltex = None
    elif editor.Root.currentcomponent is not None and editor.Root.currentcomponent.currentskin is not None:
        tbx_list = quarkx.findtoolboxes("Texture Browser...");
        ToolBoxName, ToolBox, flag = tbx_list[0]
        UsedTexturesList = {}
        for item in editor.Root.subitems:
            if item.name.endswith(":mc"):
                for subitem in item.subitems:
                    if subitem.name.endswith(":sg"):
                        for skin in subitem.subitems:
                            UsedTexturesList[skin.name] = subitem.dictitems[skin.name]
        # Updates the "Used Skin Textures.qtxfolder" to display in the Texture Browser.
        if ToolBox.dictitems.has_key('Used Skin Textures.qtxfolder'):
            UsedTexture = ToolBox.dictitems['Used Skin Textures.qtxfolder']
        else:
            UsedTexture = quarkx.newobj('Used Skin Textures.qtxfolder')
        UsedTexture.flags = UsedTexture.flags | qutils.OF_TVSUBITEM
        for UsedTextureName in UsedTexturesList:
            if UsedTextureName in UsedTexture.dictitems.keys():
                continue
            UsedTexture.appenditem(UsedTexturesList[UsedTextureName].copy())
        if not ToolBox.dictitems.has_key('Used Skin Textures.qtxfolder'):
            ToolBox.appenditem(UsedTexture)


def texturebrowser(reserved=None):
    "Updates the 'Used Skin Textures.qtxfolder' then opens the texture browser with the currentcomponent's currentskin selected."

    editor = mapeditor()
    if editor is None:
        seltex = None
    elif editor.Root.currentcomponent is not None and editor.Root.currentcomponent.currentskin is not None:
        # Updates the "Used Skin Textures.qtxfolder" to display in the Texture Browser.
        updateUsedTextures()

        tbx_list = quarkx.findtoolboxes("Texture Browser...");
        ToolBoxName, ToolBox, flag = tbx_list[0]

        try:
            seltex = ToolBox.dictitems['Used Skin Textures.qtxfolder'].dictitems[editor.Root.currentcomponent.currentskin.name]
        except:
            seltex = None
    else:
        seltex = None

    # Open the Texture Browser tool box.
    quarkx.opentoolbox("", seltex)


def moveselection(editor, text, offset=None, matrix=None, origin=None, inflate=None):
    "Move the selection and/or apply a linear mapping on it."

    import mdlutils
    from qbaseeditor import currentview
    #
    # Get the list of selected items.
    #
    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
        items = editor.EditorObjectList
        newlist = []
    else:
        items = mdlutils.MakeEditorVertexPolyObject(editor)
    if len(items):
        if matrix and (origin is None):
            #
            # Compute a suitable origin if none is given
            #
            origin = editor.interestingpoint()
            if origin is None:
                bbox = quarkx.boundingboxof(items)
                if bbox is None:
                    origin = quarkx.vect(0,0,0)
                else:
                    origin = (bbox[0]+bbox[1])*0.5
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                if text == "symmetry":
                    if items[0].type == ":f":
                        matrix = matrix_rot_x(currentview.info["vangle"]) * matrix_rot_z(currentview.info["angle"])
                else:
                    pass
            else:
                if items[0].type == ":f":
                    matrix = matrix_rot_x(currentview.info["vangle"]) * matrix_rot_z(currentview.info["angle"])
        undo = quarkx.action()
        for obj in items:
            new = obj.copy()
            if offset:
                new.translate(offset)     # offset the objects
            if matrix:
                new.linear(origin, matrix)   # apply the linear mapping
            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                if text == "symmetry":
                    if obj.type == ":f":
                        center = obj["usercenter"]
                        if center is not None:
                            newcenter = matrix*(quarkx.vect(center)-origin)+origin
                            obj["usercenter"]=newcenter.tuple
                else:
                    pass
            else:
                if obj.type == ":f":
                    center = obj["usercenter"]
                    if center is not None:
                        newcenter = matrix*(quarkx.vect(center)-origin)+origin
                        obj["usercenter"]=newcenter.tuple
            if inflate:
                new.inflate(inflate)    # inflate / deflate

            if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
                newlist = newlist + [new]
        import mdlmgr
        mdlmgr.savefacesel = 1
        if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
            text = "face " + text
            mdlutils.ConvertEditorFaceObject(editor, newlist, currentview.flags, currentview, text)
        else:
            text = "vertex " + text
            mdlutils.ConvertVertexPolyObject(editor, [new], currentview.flags, currentview, text, 0)

    else:
        #
        # No selection.
        #
        quarkx.msgbox(Strings[222], MT_ERROR, MB_OK)


def ForceToGrid(editor, grid, sellist):
    undo = quarkx.action()
    for obj in sellist:
        new = obj.copy()
        new.forcetogrid(grid)
        undo.exchange(obj, new)
    editor.ok(undo, Strings[560])


def groupcolor(m):
    editor = mapeditor(SS_MODEL)
    if editor is None:
        return
    group = editor.layout.explorer.uniquesel
    if (group is None) or (group.type != ':mc'):
        return
    oldval = group["_color"]
    if m.rev:
        nval = None
    else:
        try:
            oldval = quakecolor(quarkx.vect(oldval))
        except:
            oldval = 0
        nval = editor.form.choosecolor(oldval)
        if nval is None:
            return
        nval = str(colorquake(nval))
    if nval != oldval:
        undo = quarkx.action()
        undo.setspec(group, "_color", nval)
        undo.ok(editor.Root, Strings[622])

# ----------- REVISION HISTORY ------------
#
#
#$Log: mdlbtns.py,v $
#Revision 1.45  2012/07/10 02:04:16  cdunde
#Fix for error when making a dupe copy of a model's baseframe.
#
#Revision 1.44  2011/03/13 00:41:47  cdunde
#Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
#Revision 1.43  2011/03/10 20:56:39  cdunde
#Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
#and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
#Revision 1.42  2011/02/11 19:52:56  cdunde
#Added import support for Heretic II and .m8 as supported texture file type.
#
#Revision 1.41  2011/01/04 11:10:20  cdunde
#Added .vtf as supported texture file type for game HalfLife2.
#
#Revision 1.40  2010/12/10 20:18:32  cdunde
#Added bbox edit menu items.
#
#Revision 1.39  2010/12/07 06:06:52  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.38  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.37  2010/06/15 20:38:36  cdunde
#Added .ftx as supported texture file type for game FAKK2.
#
#Revision 1.36  2010/05/15 18:47:28  cdunde
#Better to set looking for texture paths in game addons qrk files first.
#
#Revision 1.35  2010/05/08 07:39:16  cdunde
#Setup the QuArK Model Editor to allow obtaining textures dynamically in the Texture Browser.
#
#Revision 1.34  2010/05/05 04:47:22  cdunde
#Setup support to import model skin textures using addon .qrk file links.
#
#Revision 1.33  2010/05/03 04:06:10  cdunde
#Code update.
#
#Revision 1.32  2010/05/01 04:43:59  cdunde
#General function corrections and file cleanup.
#
#Revision 1.31  2010/05/01 04:25:37  cdunde
#Updated files to help increase editor speed by including necessary ModelComponentList items
#and removing redundant checks and calls to the list.
#
#Revision 1.30  2010/03/26 07:28:42  cdunde
#To add new Model Editor sub-group folders to the Skins group.
#
#Revision 1.29  2009/07/04 03:02:40  cdunde
#Fix to stop multiple Skeleton folders from being created when multiple components are deleted.
#
#Revision 1.28  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.27  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.26  2009/02/17 04:58:46  cdunde
#To expand on types of image texture files that can be applied from the Texture Browser to the Model editor.
#
#Revision 1.25  2009/01/29 02:13:51  cdunde
#To reverse frame indexing and fix it a better way by DanielPharos.
#
#Revision 1.24  2009/01/28 01:10:09  cdunde
#Update for frame indexing, for another function.
#
#Revision 1.23  2009/01/27 23:28:21  cdunde
#Update for frame indexing.
#
#Revision 1.22  2008/11/17 23:56:04  danielpharos
#Compensate for accidental change in behaviour in QkObjects rev 1.112.
#
#Revision 1.21  2008/07/25 22:57:24  cdunde
#Updated component error checking and added frame matching and\or
#duplicating with independent names to avoid errors with other functions.
#
#Revision 1.20  2008/05/27 19:36:16  danielpharos
#Fixed another bunch of wrong imports
#
#Revision 1.19  2008/05/01 13:52:32  danielpharos
#Removed a whole bunch of redundant imports and other small fixes.
#
#Revision 1.18  2007/11/16 18:48:23  cdunde
#To update all needed files for fix by DanielPharos
#to allow frame relocation after editing.
#
#Revision 1.17  2007/10/24 14:58:12  cdunde
#To activate all Movement toolbar button functions for the Model Editor.
#
#Revision 1.16  2007/09/21 21:19:51  cdunde
#To add message string that is model editor specific.
#
#Revision 1.15  2007/09/12 19:47:39  cdunde
#To update comment to a meaningful statement.
#
#Revision 1.14  2007/09/10 10:24:26  danielpharos
#Build-in an Allowed Parent check. Items shouldn't be able to be dropped somewhere where they don't belong.
#
#Revision 1.13  2007/04/12 03:37:34  cdunde
#Fixed error for dropitemsnow function when selecting a texture for a Model Skin.
#
#Revision 1.12  2007/04/03 15:17:45  danielpharos
#Read the recenter option for the correct editor mode.
#
#Revision 1.11  2007/03/31 14:32:43  danielpharos
#Should fix the Screen Center behaviour
#
#Revision 1.10  2007/03/29 14:46:50  danielpharos
#Fix a crash when trying to drop an item in a view.
#
#Revision 1.9  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.8  2006/11/29 07:00:27  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.7.2.2  2006/11/22 23:31:53  cdunde
#To setup Face-view click function to open Texture Browser for possible future use.
#
#Revision 1.7.2.1  2006/11/04 00:49:34  cdunde
#To add .tga model skin texture file format so they can be used in the
#model editor for new games and to start the displaying of those skins
#on the Skin-view page (all that code is in the mdlmgr.py file).
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