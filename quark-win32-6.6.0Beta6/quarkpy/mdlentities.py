"""   QuArK  -  Quake Army Knife

Model Editor Entities manager
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mdlentities.py,v 1.93 2012/10/13 21:54:20 cdunde Exp $




import quarkx
import qeditor
from mdlutils import *
import mdlhandles
import dlgclasses
import mdleditor
from qeditor import ico_dict # Get the dictionary list of all icon image files available.
import qtoolbar              # Get the toolbar functions to make buttons with.
SS_MODEL = 3 # The Model Editor mode.

#
# Classes that implement operations on all types of Model Objects.
# See comments in mapentities.py.
#


#
# Generic Model object types have type==':m', and are distinguished by a "type" Specific.
# Here is the list of reconized values.
#

MT_GROUP       = 0      # generic group
MT_FRAMEGROUP  = 1
MT_SKINGROUP   = 2
MT_SKIN        = 3      # not used
MT_TAGGROUP    = 4      # AiV
MT_BONEGROUP   = 5      # AiV
MT_MISCGROUP   = 6      # AiV

###############################
#
# Entity \ Component General Functions.
#
###############################

def ShowHideBBoxes(x):
    editor = mdleditor.mdleditor
    if editor is None: return
    templist = editor.layout.explorer.sellist
    for obj in range(len(editor.layout.explorer.sellist)):
        if editor.layout.explorer.sellist[obj].type == ":bbg" or editor.layout.explorer.sellist[obj].type == ":p":
            def group_subitems(subitems, x=x):
                for bbox in subitems:
                    bbox['show'] = (x,)
            editor.layout.explorer.sellist[obj]['show'] = (x,)
            group_subitems(editor.layout.explorer.sellist[obj].subitems)
            templist.remove(editor.layout.explorer.sellist[obj])
    editor.layout.explorer.sellist = templist
    editor.explorerselchange()

def ShowTheseBBoxes(m):
    ShowHideBBoxes(1.0)

def HideTheseBBoxes(m):
    ShowHideBBoxes(0.0)


def ShowHideTags(x):
    editor = mdleditor.mdleditor
    if editor is None: return
    templist = editor.layout.explorer.sellist
    for obj in range(len(editor.layout.explorer.sellist)):
        if editor.layout.explorer.sellist[obj].type == ":tag":
            editor.layout.explorer.sellist[obj]['show'] = (x,)
            templist.remove(editor.layout.explorer.sellist[obj])
    editor.layout.explorer.sellist = templist
    editor.explorerselchange()

def ShowTheseTags(m):
    ShowHideTags(1.0)

def HideTheseTags(m):
    ShowHideTags(0.0)


def ShowHideBones(x):
    editor = mdleditor.mdleditor
    if editor is None: return
    templist = editor.layout.explorer.sellist
    for obj in range(len(editor.layout.explorer.sellist)):
        if editor.layout.explorer.sellist[obj].type == ":bone":
            def bone_subitems(subitems, x=x):
                for bone in subitems:
                    bone['show'] = (x,)
                    bone_subitems(bone.subitems)
            editor.layout.explorer.sellist[obj]['show'] = (x,)
            bone_subitems(editor.layout.explorer.sellist[obj].subitems)
            templist.remove(editor.layout.explorer.sellist[obj])
    editor.layout.explorer.sellist = templist
    editor.explorerselchange()

def ShowTheseBones(m):
    ShowHideBones(1.0)

def HideTheseBones(m):
    ShowHideBones(0.0)


def ShowHideComp(x):
    editor = mdleditor.mdleditor
    if editor is None: return
    editor.ModelFaceSelList = []
    editor.EditorObjectList = []
    editor.SkinFaceSelList = []
    editor.SelCommonTriangles = []
    editor.SelVertexes = []
    obj = editor.layout.explorer.uniquesel
    if obj is None: return
    obj.showhide(x)
    editor.layout.explorer.uniquesel = None

    from mdlhandles import SkinView1
    if x == 0:
        if SkinView1 is not None:
            SkinView1.handles = []
        for view in editor.layout.views:
            view.handles = []
    else:
        if SkinView1 is not None:
            q = editor.layout.skinform.linkedobjects[0]
            q["triangles"] = str(len(editor.Root.currentcomponent.triangles))
            editor.layout.skinform.setdata(q, editor.layout.skinform.form)
            try:
                skindrawobject = editor.Root.currentcomponent.currentskin
            except:
                skindrawobject = None
            mdlhandles.buildskinvertices(editor, SkinView1, editor.layout, editor.Root.currentcomponent, skindrawobject)

def ShowComp(m):
    ShowHideComp(1)

def HideComp(m):
    ShowHideComp(0)


###############################
#
# Menu Module
#
###############################

# This module allows you to switch menu text when an option is changed.

#---

# More precise/technical:
# This module allows you to change the name/text of importers and exporters displayed in the menus.

# Call the appropriate RegisterMenu*Changed function to register your im-/exporter. The first and only parameter, TextProc,
# is a function that must return the old text and new text of the menuitem. Example: "return OldText, NewText"
# This text can depend on the loaded setup settings, so you can use quarkx.setupsubset(*) to determine the right text.
# Any menuitems with the OldText will then automatically be changed into NewText whenever the setup is changed.

ImpMenuProcs = [] #List of registered TextProcs of importers
#Register a TextProc for an importer
def RegisterMenuImporterChanged(TextProc):
    ImpMenuProcs.append(TextProc)

ExpMenuProcs = [] #List of registered TextProcs of exporters
#Register a TextProc for an exporter
def RegisterMenuExporterChanged(TextProc):
    ExpMenuProcs.append(TextProc)

#Don't call this directly! This is where the magic happens...
def menu_setupchanged(level):
    import mdleditor
    import qmacro
    import quarkx
    editor = mdleditor.mdleditor

    # Do the importers
    if len(ImpMenuProcs) <> 0:
        new_mdlimport = {}
        for item in qmacro.mdlimport.keys():
            new_mdlimport[item] = qmacro.mdlimport[item]
        new_mdlimportmenuorder = {}
        for item in qmacro.mdlimportmenuorder.keys():
            new_mdlimportmenuorder[item] = qmacro.mdlimportmenuorder[item]
        for TextProc in ImpMenuProcs:
            OldText, NewText = TextProc()

            # Update qmacro lists with the new Importer Text
            for item in new_mdlimportmenuorder.keys():
                textlist = []
                for text in new_mdlimportmenuorder[item]:
                    if text == OldText:
                        textlist = textlist + [NewText]
                    else:
                        textlist = textlist + [text]
                new_mdlimportmenuorder[item] = textlist
            for item in new_mdlimport.keys():
                if item == OldText:
                    new_mdlimport[NewText] = new_mdlimport[OldText]
                    del new_mdlimport[OldText]
            qmacro.mdlimportmenuorder = new_mdlimportmenuorder
            qmacro.mdlimport = new_mdlimport

        # Update File menu of main window with new text
        quarkx.mdlimportmenuclear()
        orderedlist = qmacro.mdlimportmenuorder.keys()
        orderedlist.sort()
        for menuindex in orderedlist:
            for importer in qmacro.mdlimportmenuorder[menuindex]:
                quarkx.mdlimportmenu(importer)

    # Do the exporters
    if len(ExpMenuProcs) <> 0:
        new_mdlexport = {}
        for item in qmacro.mdlexport.keys():
            new_mdlexport[item] = qmacro.mdlexport[item]
        new_mdlexportmenuorder = {}
        for item in qmacro.mdlexportmenuorder.keys():
            new_mdlexportmenuorder[item] = qmacro.mdlexportmenuorder[item]
        for TextProc in ExpMenuProcs:
            OldText, NewText = TextProc()

            # Update qmacro lists with the new Exporter Text
            for item in new_mdlexportmenuorder.keys():
                textlist = []
                for text in new_mdlexportmenuorder[item]:
                    if text == OldText:
                        textlist = textlist + [NewText]
                    else:
                        textlist = textlist + [text]
                new_mdlexportmenuorder[item] = textlist
            for item in new_mdlexport.keys():
                if item == OldText:
                    new_mdlexport[NewText] = new_mdlexport[OldText]
                    del new_mdlexport[OldText]
            qmacro.mdlexportmenuorder = new_mdlexportmenuorder
            qmacro.mdlexport = new_mdlexport

    # Update File menu of the current editor with the new text
    if editor is not None:
        editor.initmenu(editor.form)

# This registers the 'magic' function above, so it's called whenever the setup is changed
setupchanged1 = (menu_setupchanged,)
apply(SetupRoutines.append, setupchanged1)


###############################
#
# Animation Configuration Module
#
###############################

# Funcitons for AnimationCFG Module ONLY.

def CFGfileLines():
    editor = mdleditor.mdleditor # Get the editor.
    if len(editor.layout.explorer.sellist) == 0:
        return
    if editor.layout.explorer.sellist[0].type == ":tag":
        obj = editor.layout.explorer.sellist[0]
        if not obj.dictspec.has_key("animationCFG"):
            return
    else:
        return
    if obj.dictspec.has_key("CFG_lines"):
        if int(obj.dictspec['CFG_lines']) < 3:
            obj['CFG_lines'] = "3"
        if int(obj.dictspec['CFG_lines']) > 35:
            obj['CFG_lines'] = "35"
        NbrOfCFGLines = str(int(obj.dictspec['CFG_lines']))
        quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"] = NbrOfCFGLines
        if obj.type == ":tag":
            obj['CFG_lines'] = NbrOfCFGLines
    else:
        if quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"] is not None:
            NbrOfCFGLines = quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"]
            obj['CFG_lines'] = NbrOfCFGLines
        else:
            NbrOfCFGLines = "8"
            obj['CFG_lines'] = NbrOfCFGLines
            quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"] = NbrOfCFGLines
    return NbrOfCFGLines

#
# Main function to be called from other files such as this file
# (see "class TagType" 'dataformname' function further below.)
# to return a "dialog_plugin section" that will be used
# in that files dialog definition or "dlgdef".
#
def UseAnimationCFG():
    AnimationCFG_dialog_plugin =  """
      Sep:            = {Typ = "S"   Txt = ""}
      Sep:            = {Typ = "S"   Txt = "AnimationCFG File"  Hint = "Special configuration code used to:"$0D"1) Create animation sequences of the model."$0D"2) To create the 'AnimationCFG dialog' to select/run them."}
      animCFG_file:   = {
                         Typ = "E"
                         Txt = "cfg file"
                         Hint = "Gives the full path and name of the .cfg animation"$0D
                                "file that is used to animate the model components, if any."
                        }
      CFG_lines:      = {
                         Typ = "EU"
                         Txt = "cfg lines"
                         Hint = "Number of lines to display in window below, max. = 35."
                        }
      edit_cfg:       = {
                         Typ = "P"
                         Txt = "edit cfg -->"
                         Macro = "opentexteditor"
                         Hint = "Opens cfg text below in a text editor."$0D
                                "Click 'Save' in that editor to change the cfg here."$0D
                                "      The changes can then be viewed using the 'AnimationCFG' dialog."$0D
                                "      All changes can be reversed using the 'Undo / Redo' list."$0D
                                "Click 'Save As' in that editor to save a copy of the cfg file elsewhere."$0D
                                "      Rename that file from .txt to animation.cfg and move to model folder."$0D
                                "      Be sure NOT to overwrite the original cfg file in that folder."
                         Cap = "edit cfg"
                        }
      animationCFG:   = {
                         Typ = "M"
                         Rows = """ + chr(34) + CFGfileLines() + chr(34) + """
                         Scrollbars = "1"
                         Txt = "cfg text"
                         Hint = "Contains the full text of this tag's animation.cfg file, if any."$0D
                                "This can be copied to a text file, changed and saved."
                        }
    """

    return AnimationCFG_dialog_plugin


###############################
#
# Shader Module
#
###############################

# Funcitons for Shader Module ONLY.

def ShaderLines():
    editor = mdleditor.mdleditor # Get the editor.
    if len(editor.layout.explorer.sellist) == 0:
        return
    if editor.layout.explorer.sellist[0].type.startswith(".") and editor.layout.buttons["sf"].caption == ".ase":
        obj = editor.layout.explorer.sellist[0]
        if obj.parent.parent != editor.Root.currentcomponent:
            return
        comp = editor.Root.currentcomponent
    else:
        obj = comp = editor.Root.currentcomponent
    if obj.dictspec.has_key("shader_lines"):
        if int(obj.dictspec['shader_lines']) < 3:
            comp['shader_lines'] = "3"
            obj['shader_lines'] = "3"
        if int(obj.dictspec['shader_lines']) > 35:
            comp['shader_lines'] = "35"
            obj['shader_lines'] = "35"
        NbrOfShaderLines = str(int(obj.dictspec['shader_lines']))
        quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = NbrOfShaderLines
        if obj.type.startswith("."):
            comp['shader_lines'] = NbrOfShaderLines
        for skin in comp.dictitems['Skins:sg'].subitems:
            skin['shader_lines'] = NbrOfShaderLines
    else:
        if quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] is not None:
            NbrOfShaderLines = quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"]
            comp['shader_lines'] = NbrOfShaderLines
            obj['shader_lines'] = NbrOfShaderLines
        else:
            NbrOfShaderLines = "8"
            comp['shader_lines'] = NbrOfShaderLines
            obj['shader_lines'] = NbrOfShaderLines
            quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = NbrOfShaderLines
    return NbrOfShaderLines

#
# Main function to be called from other files such as the
# plugins\ie_ASE_import.py file using a button (see file)
# to return a "dialog_plugin section" that will be used
# in that files dialog definition or "dlgdef".
#
def UseShaders():
    Shader_dialog_plugin =  """
      Sep:            = {Typ = "S"   Txt = ""}
      Sep:            = {Typ = "S"   Txt = "Shader File"  Hint = "Special effects code by use of textures."}
      shader_file:    = {
                         Typ = "E"
                         Txt = "shader file"
                         Hint = "Gives the full path and name of the .mtr material"$0D
                                "shader file that the selected skin texture uses, if any."
                        }
      shader_name:    = {
                         Typ = "E"
                         Txt = "shader name"
                         Hint = "Gives the name of the shader located in the above file"$0D
                                "that the selected skin texture uses, if any."
                        }
      shader_keyword: = {
                         Typ = "E"
                         Txt = "shader keyword"
                         Hint = "Gives the above shader 'keyword' that is used to identify"$0D
                                "the currently selected skin texture used in the shader, if any."
                        }
      shader_lines:   = {
                         Typ = "EU"
                         Txt = "shader lines"
                         Hint = "Number of lines to display in window below, max. = 35."
                        }
      edit_shader:    = {
                         Typ = "P"
                         Txt = "edit shader -->"
                         Macro = "opentexteditor"
                         Hint = "Opens shader below"$0D"in a text editor."
                         Cap = "edit shader"
                        }
      mesh_shader:    = {
                         Typ = "M"
                         Rows = """ + chr(34) + ShaderLines() + chr(34) + """
                         Scrollbars = "1"
                         Txt = "mesh shader"
                         Hint = "Contains the full text of this skin texture's shader, if any."$0D
                                "This can be copied to a text file, changed and saved."
                        }
    """

    return Shader_dialog_plugin


###############################
#
# External Skin Editor Module
#
###############################

#
# Main function to be called from other files such as the
# plugins\ie_ASE_import.py file using a button (see file)
# to return a "dialog_plugin section" that will be used
# in that files dialog definition or "dlgdef".
#
def UseExternalSkinEditor():
    external_skin_editor_dialog_plugin =  """
      edit_skin:  = {
                     Typ = "P"
                     Txt = "edit skin ---->"
                     Macro = "opentexteditor"
                     Hint = "Opens this skin texture"$0D"in an external editor."
                     Cap = "edit skin"
                    }
    """

    return external_skin_editor_dialog_plugin

### Used by more then one module above.
def macro_opentexteditor(btn):
    editor = mdleditor.mdleditor # Get the editor.
    if btn.name == "edit_skin:":
        if editor.Root.currentcomponent.currentskin is None:
            quarkx.beep() # Makes the computer "Beep" once.
            quarkx.msgbox("No model skin texture !\n\nYou must provide one\nto use this function.", qutils.MT_ERROR, qutils.MB_OK)
            return
        newImage = editor.Root.currentcomponent.currentskin
        save_dictspecs = {}
        for key in newImage.dictspec.keys():
            if key == "Image1" or key == "Size":
                continue
            save_dictspecs[key] = newImage.dictspec[key]
        quarkx.externaledit(editor.Root.currentcomponent.currentskin) # Opens skin in - external editor for this texture file type.
        for key in save_dictspecs.keys():
            newImage[key] = save_dictspecs[key]
        editor.Root.currentcomponent.currentskin = newImage
        skin = editor.Root.currentcomponent.currentskin
        editor.layout.skinview.background = quarkx.vect(-int(skin["Size"][0]*.5),-int(skin["Size"][1]*.5),0), 1.0, 0, 1
        editor.layout.skinview.backgroundimage = skin,
        editor.layout.skinview.repaint()
        for v in editor.layout.views:
            if v.viewmode == "tex":
                v.invalidate(1)
    elif btn.name == "edit_cfg:":
        old_obj = editor.layout.explorer.sellist[0]
        new_obj = old_obj.copy()
        obj = quarkx.newfileobj("amCFG.txt")
        obj['Data'] = new_obj.dictspec['animationCFG']
        quarkx.externaledit(obj) # Opens this text in - external editor for changing.
        new_obj['animationCFG'] = obj['Data']
        if new_obj.dictspec['animationCFG'] != old_obj.dictspec['animationCFG']:
            undo = quarkx.action()
            undo.exchange(old_obj, new_obj)
            editor.ok(undo, new_obj.shortname + " - animCFG changed")
    else:
        old_obj = editor.Root.currentcomponent
        new_obj = old_obj.copy()
        obj = quarkx.newfileobj("temp.txt")
        obj['Data'] = new_obj.dictspec['mesh_shader']
        quarkx.externaledit(obj)
        new_obj['mesh_shader'] = obj['Data']
        if new_obj.dictspec['mesh_shader'] != old_obj.dictspec['mesh_shader']:
            if old_obj.dictspec.has_key("shader_keyword"):
                shader_keyword = old_obj.dictspec['shader_keyword']
                if old_obj.dictspec['mesh_shader'].find(shader_keyword) != -1 and new_obj.dictspec['mesh_shader'].find(shader_keyword) == -1:
                    quarkx.beep() # Makes the computer "Beep" once.
                    quarkx.msgbox("shader keyword:\n    " + shader_keyword + "\nhas changed !\n\nYou should probably copy the new keyword from the shader below and\npaste it into this dialogs 'shader keyword' to replace the old one.", qutils.MT_WARNING, qutils.MB_OK)

            undo = quarkx.action()
            undo.exchange(old_obj, new_obj)
            editor.ok(undo, new_obj.shortname + " - mesh shader changed")
    
qmacro.MACRO_opentexteditor = macro_opentexteditor


###############################
#
# Vertex U,V Color Module
#
###############################

# Imports & Globals for Vertex U,V Color Module ONLY.
import struct

#
# Main function to be called from other files such as the
# plugins\ie_ASE_import.py file using a button (see file)
# to return a "dialog_plugin section" that will be used
# in that files dialog definition or "dlgdef".
#
def UseVertexUVColors():
    vtx_UVcolor_dialog_plugin =  """
      Sep:            = {Typ = "S"   Txt = ""}
      Sep:            = {Typ = "S"   Txt = "UV Vertex Colors"  Hint = "Texture lighting characteristics of a model."}
      vtx_color:      = {            Txt = "vertex color"      }
      vtx_color:      = {
                         Typ = "L"
                         Txt = "vertex color"
                         Hint = "Color to use for this component's u,v vertex color mapping."$0D
                                "Click the color display button to select a color."
                        }
      show_vtx_color: = {
                         Typ = "X"
                         Txt = "show vertex color"
                         Hint = "When checked, if component has vertex coloring they will show."$0D
                                "If NOT checked and it has bones with vetexes, those will show."
                        }
      apply_color:    = {
                         Typ = "P"
                         Txt = "apply vertex color ---->"
                         Macro = "apply_vtx_color"
                         Hint = "Applies the selected 'Vertex Color'"$0D"to the currently selected vertexes."
                         Cap = "apply color"
                        }
      remove_color:   = {
                         Typ = "P"
                         Txt = "remove vertex color -->"
                         Macro = "remove_vtx_color"
                         Hint = "Removes all of the vertex color"$0D"from the currently selected vertexes."
                         Cap = "remove color"
                        }
    """

    return vtx_UVcolor_dialog_plugin

def macro_apply_vtx_color(btn):
    editor = mdleditor.mdleditor # Get the editor.
    if len(editor.ModelVertexSelList) == 0:
        quarkx.beep() # Makes the computer "Beep" once .
        quarkx.msgbox("No vertex selection !\n\nYou must select some vertexes\nbefore using this function.", qutils.MT_ERROR, qutils.MB_OK)
        return
    o = editor.Root.currentcomponent
    if o.dictspec.has_key('vtx_color'):
        R, G, B = o.dictspec['vtx_color'].split(" ")
        R = round(float(R)*255)
        G = round(float(G)*255)
        B = round(float(B)*255)
        rgb = struct.pack('i', qutils.RGBToColor([R, G, B]))
        if len(editor.ModelVertexSelList) != 0:
            for vtx in editor.ModelVertexSelList:
                if not editor.ModelComponentList[o.name]['colorvtxlist'].has_key(vtx):
                    editor.ModelComponentList[o.name]['colorvtxlist'][vtx] = {}
                editor.ModelComponentList[o.name]['colorvtxlist'][vtx]['vtx_color'] = rgb
    undo = quarkx.action()
    newframe = o.currentframe.copy()
    undo.exchange(o.currentframe, newframe)
    editor.ok(undo, 'applied vertex color')

def macro_remove_vtx_color(btn):
    editor = mdleditor.mdleditor # Get the editor.
    if len(editor.ModelVertexSelList) == 0:
        quarkx.beep() # Makes the computer "Beep" once .
        quarkx.msgbox("No UV Color vertexes\nselected to remove.", qutils.MT_ERROR, qutils.MB_OK)
        return
    o = editor.Root.currentcomponent
    if len(editor.ModelComponentList[o.name]['colorvtxlist']) == 0:
        quarkx.msgbox("No UV Color vertexes\nassigned to this component.", qutils.MT_INFORMATION, qutils.MB_OK)
        return
    else:
        for vtx in editor.ModelVertexSelList:
            if editor.ModelComponentList[o.name]['colorvtxlist'].has_key(vtx):
                if editor.ModelComponentList[o.name]['colorvtxlist'][vtx].has_key('vtx_color'):
                    if len(editor.ModelComponentList[o.name]['colorvtxlist'][vtx]) == 1:
                        del editor.ModelComponentList[o.name]['colorvtxlist'][vtx]
                    else:
                        del editor.ModelComponentList[o.name]['colorvtxlist'][vtx]['vtx_color']
    undo = quarkx.action()
    newframe = o.currentframe.copy()
    undo.exchange(o.currentframe, newframe)
    editor.ok(undo, 'removed vertex color')

qmacro.MACRO_apply_vtx_color = macro_apply_vtx_color
qmacro.MACRO_remove_vtx_color = macro_remove_vtx_color


###############################
#
# Vertex Paint System Module
#
###############################

# Functions, Imports & Globals for Vertex Paint System Module ONLY.
vtxpaint = 0

#
# To pass mouse actions to do the actual vertex color painting
# and possible future specific buttons that deal with vertex painting functions.
# PaintManager only applies to the vertex paint brush.
# The "rectanglesel" function in mdlhandles.py, class RectSelDragObject, applies to that method for applying vertex weights.
#
def PaintManager(editor, view, x, y, flagsmouse, vertex):
    if len(editor.layout.explorer.sellist) == 0 or editor.layout.explorer.sellist[len(editor.layout.explorer.sellist)-1].type != ":mf":
        return
    if flagsmouse == 2088:
        # "apply_vtx_weights" is for the Bone Specifics page.
        if editor.Root.currentcomponent.dictspec.has_key("apply_vtx_weights"):
            macro_applychanges(None)
        formlist = quarkx.forms(1)
        for f in formlist:
            try:
                if f.caption == "Vertex Weights Dialog":
                    macro_updatedialog(None)
            except:
                pass
    else:
        h = view.handles[vertex]
        for v in editor.layout.views:
            cv = v.canvas()
            h.draw(v, cv, h)

def vtxpaintcursor(editor):
    "Changes cursor in views when this system is active."

    if quarkx.setupsubset(SS_MODEL, "Options")['VertexPaintMode'] is not None:
        for view in editor.layout.views:
            view.cursor = CR_BRUSH

def vtxpaintclick(btn):
    editor = mdleditor.mdleditor # Get the editor.
    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
        editor.ModelVertexSelList = []
        editor.linearbox = "True"
        editor.linear1click(btn)
    else:
        if editor.ModelVertexSelList != []:
            editor.ModelVertexSelList = []
            Update_Editor_Views(editor)

def paintclick(btn):
    global vtxpaint
    if vtxpaint == 0:
        vtxpaint = 1
    editor = mdleditor.mdleditor # Get the editor.
    if not quarkx.setupsubset(SS_MODEL, "Options")['VertexPaintMode'] or quarkx.setupsubset(SS_MODEL, "Options")['VertexPaintMode'] == "0":
        quarkx.setupsubset(SS_MODEL, "Options")['VertexPaintMode'] = "1"
        qtoolbar.toggle(btn)
        btn.state = qtoolbar.selected
        quarkx.update(editor.form)
        vtxpaintclick(btn)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['VertexPaintMode'] = "0"
        qtoolbar.toggle(btn)
        btn.state = qtoolbar.normal
        quarkx.update(editor.form)
    if vtxpaint == 1:
        vtxpaint = 0

#
# Main function to be called from other files such as the
# plugins\ie_md5_import.py file using a button (see file).
# Returns the buttons and supplys the Vertex Paint Dialog.
#
def UseVertexPaintSystem(editor, icon_btns):
    # to build the single click buttons
    if not ico_dict.has_key('ico_paintmodes'):
        ico_dict['ico_paintmodes']=LoadIconSet1("mdlpaintm", 1.0)
    ico_paintmodes = ico_dict['ico_paintmodes']  # Just to shorten our call later.

    vtxpaintbtn = qtoolbar.button(paintclick, "Vertex Paint mode||When active, puts the editor into this mode to apply color to designate and set types of vertexes.\n\nIt also places the editor into Vertex Selection mode if not there already and clears any selected vertexes to protect from including unwanted ones by mistake.\n\nAny vertexes selected in this mode will become the selected color and setting if applicable. Click the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_paintmodes, 1)
    # Sets the button to its current status, that might be effected by another file, either on or off.
    if quarkx.setupsubset(SS_MODEL, "Options")['VertexPaintMode'] == "1":
        vtxpaintbtn.state = qtoolbar.selected
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['VertexPaintMode'] = "0"
        vtxpaintbtn.state = qtoolbar.normal
    vtxpaintbtn.caption = "" # Texts shows next to button and keeps the width of this button so it doesn't change.
    icon_btns['color'] = vtxpaintbtn     # Put our button in the above list to return.
    return icon_btns


###############################
#
# Vertex Weights Module
#
###############################

# Imports & Globals for Vertex Weights Module ONLY.
WeightedVTXlist = []
WeightsDlgPage = 0   #Warning: Starts counting from 0, but the control shows starting at 1
SpecsList = """ """
SRClables = {}
SRCsList = {}
vtxnbrs = []

#
# Main function to be called from other files such as the
# plugins\ie_ASE_import.py file using a button (see file).
# Setup so it can also be called as a menu item.
#
def UseVertexWeightsSpecifics():
    vertex_weights_specifics_plugin =  """
      Sep:            = {Typ = "S"   Txt = ""}
      Sep:            = {Typ = "S"   Txt = "Vertex Weight Colors"  Hint = "Bone's weighted vertex movement by color."}
      use_weights: =        {
                             Typ = "X"
                             Txt = "use weight bone sel"
                             Hint = "When checked, it puts bone selection into a special mode allowing you to"$0D
                                    "add or remove bones to the selection without having to use the 'Ctrl' key."
                            }
      show_weight_color: =  {
                             Typ = "X"
                             Txt = "show weight colors"
                             Hint = "When checked, if component has vertex weight coloring they will show."$0D
                                    "If NOT checked and it has bones with vetexes, those will show."
                            }
      apply_vtx_weights: =  {
                             Typ = "X"
                             Txt = "auto apply changes"
                             Hint = "When checked, applies all bone weight settings for any currently or"$0D
                                    "additional selected vertexes using the linear handle or applied by the paint brush."$0D0D
                                    "Weight changes made using the 'Vertex Weights Dialog' settings"$0D
                                    "will be made automatically if its 'auto save' option box is checked."
                            }
    """

    return vertex_weights_specifics_plugin

def UseVertexWeights(btn=None):
    if btn == None:
        ico_mdlskv = ico_dict['ico_mdlskv']  # Just to shorten our call later.
        btn = qtoolbar.button(vtxweightsclick, "Open or Update\nVertex Weights Dialog||When clicked, this button opens the dialog to allow the 'weight' movement setting of single vertexes that have been assigned to more then one bone handle.\n\nClick the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
    vtxweightsclick(btn)

def AddStuff(editor):
    global WeightedVTXlist, WeightsDlgPage, SpecsList, SRClables, SRCsList, vtxnbrs
    SpecsList = """ """
    SRClables = {}
    SRCsList = {}
    vtxnbrs = []
    if editor is not None and editor.Root.currentcomponent is not None:
        comp = editor.Root.currentcomponent
        if len(editor.ModelComponentList[comp.name]['weightvtxlist']) != 0:
            weightvtxlist = editor.ModelComponentList[comp.name]['weightvtxlist']
            for key in weightvtxlist.keys():
                if len(weightvtxlist[key]) > 1:
                    vtxnbrs = vtxnbrs + [key]
            if len(vtxnbrs) == 0:
                WeightedVTXlist = []
                WeightsDlgPage = 0
                return
            vtxnbrs.sort()
            if WeightsDlgPage > int(floor((len(vtxnbrs)+9)/10))-1:
                WeightsDlgPage = int(floor((len(vtxnbrs)+9)/10))-1
            LastWeight = WeightsDlgPage * 10 + 9
            if LastWeight > len(vtxnbrs) - 1:
                LastWeight = len(vtxnbrs) - 1
            skeletongroup = editor.Root.dictitems['Skeleton:bg']  # get the bones group
            bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
            WeightedVTXlist = []
            for vtx in vtxnbrs[WeightsDlgPage*10:LastWeight+1]:
                SortedKeys = []
                for bone in bones:
                    if bone.name in weightvtxlist[vtx].keys():
                        SortedKeys = SortedKeys + [bone.name]
                for bonename in SortedKeys:
                    item = [vtx, bonename]
                    WeightedVTXlist = WeightedVTXlist + [item]
            if len(WeightedVTXlist) != 0:
                vtx = WeightedVTXlist[0][0]
                for item in range(len(WeightedVTXlist)):
                    if WeightedVTXlist[item][0] != vtx:
                        SpecsList = SpecsList + """sep: = { Typ="S" Txt=""}"""
                        vtx = WeightedVTXlist[item][0]
                    bone_shortname = WeightedVTXlist[item][1].replace(":bone","")
                    specific = str(vtx) + "_" + bone_shortname
                    SpecsList = SpecsList + specific + "_label" + """: = {Txt = "Vtx \ Bone:" Typ = "E R" Hint = ""}"""
                    SRClables[specific + "_label"] = " " + str(vtx) + " \ " + bone_shortname
                    SpecsList = SpecsList + specific + """: = {Txt = "Weight value:" Typ = "EU" Hint = "Set this vertex's weight here."$0D"Total values for this vertex MUST = 1.0"}"""
                    weight_value = weightvtxlist[vtx][WeightedVTXlist[item][1]]['weight_value']
                    SRCsList[specific] = str(weight_value)
                    if item == len(WeightedVTXlist)-1:
                        SpecsList = SpecsList + """sep: = { Typ="S" Txt=""}"""
        else:
            WeightedVTXlist = []
            WeightsDlgPage = 0


class WeightsDlg(dlgclasses.LiveEditDlg):
    # Dialog layout
    size = (290, 300)
    dlgflags = qutils.FWF_KEEPFOCUS
    dfsep = 0.4      # Separation at 40% between labels and edit boxes
    dlgdef = """ """ # The dialog is created in the setup function to allow self generated items.

    def cancel(self, dlg):
        # Modified from dlgclasses.py
        qmacro.dialogbox.close(self, dlg)
        self.src = None

def WeightsClick(editor):
    if editor is None: return
    AddStuff(editor)
  
    def setup(self, editor=editor):
        global vtxnbrs
        editor.weightsdlg = self
        comp = editor.Root.currentcomponent
        self.SRClables = SRClables
        self.SRCsList = SRCsList
        # Rebuilds this dialog's form with the current, self generated, data in SpecsList.
        PageChanger = """ """
        if len(vtxnbrs) != 0:
            PageChanger = """
            page_changer: = {
              Txt = "Vertex weights page"
              Typ = "C"
              Items = """
            for page in range(int(floor((len(vtxnbrs)+9)/10))):
                firstvtx = vtxnbrs[page * 10]
                if (page * 10) + 9 > len(vtxnbrs)-1:
                    #No more vertices; this is the last and partially-filled page
                    lastvtx = vtxnbrs[len(vtxnbrs)-1]
                else:
                    lastvtx = vtxnbrs[(page * 10) + 9]
                if page == 0:
                    PageChanger = PageChanger + "    \""+str(page + 1)+" ("+str(firstvtx)+" - "+str(lastvtx)+")\""
                else:
                    PageChanger = PageChanger + "$0D \""+str(page + 1)+" ("+str(firstvtx)+" - "+str(lastvtx)+")\""
            PageChanger = PageChanger + """
              Values = """
            for page in range(int(floor((len(vtxnbrs)+9)/10))):
                if page == 0:
                    PageChanger = PageChanger + "    \""+str(page + 1)+"\""
                else:
                    PageChanger = PageChanger + "$0D \""+str(page + 1)+"\""
            PageChanger = PageChanger + """
              Hint="Select the page of vertex weights you want to display and edit."
            }
            """
        self.dlgdef = """
        {
         Style = "15"
         Caption = "Vertex Weights Dialog"
         sep: =
            {
             Typ = "S"
             Txt = "Instructions: place cursor here"
             Hint = "This dialog displays all vertexes for the selected component"$0D
                    "    that have been assigned to more then one bone."$0D
                    "All of the 'Weight' values for a particular vertex MUST add up to 1.0"$0D
                    "They are used to restrict the amount of their movement for each bone."
            }
         comp_name: =
            {
             Txt = "Component:"
             Typ = "E R"
             Hint = "The component these vertexes belong to."
            }
         """ + PageChanger + """
         sep: = { Typ = "S" Txt = ""}
         """ + SpecsList + """
         """ + PageChanger + """
         sel_vertexes: =
            {
             Typ = "P"
             Txt = "select vertexes -->"
             Macro = "selectvtxs"
             Hint = "If a bone is selected only its"$0D
                    "weighted vertexes will be selected."$0D
                    "If not, all weighted vertexes will be selected."
             Cap = "select vertexes"
            }
         update_dialog: =
            {
             Typ = "P"
             Txt = "update dialog -->"
             Macro = "updatedialog"
             Hint = "When more vertexes are assigned between bones,"$0D
                    "or other actions take place that would effect these items,"$0D
                    "this dialog will update automatically."$0D
                    "Or you can click this button to update it any time you wish."
             Cap = "update dialog"
            }
         sep: = { Typ = "S" Txt = ""}
         apply_changes: =
            {
             Typ = "P"
             Txt = "apply changes -->"
             Macro = "applychanges"
             Hint = "At any time, you can click this button to ensure"$0D
                    "that settings made thus far are saved."$0D
                    "This will also place them on the"$0D
                    "'undo' list for easy interval reversal."$0D
                    "If you wish to save all changes as they are made"$0D
                    "from this dialog check the option 'auto save'."$0D0D
                    "To change the weight values of a group of vertexes for a bone at one"$0D
                    "time check the option 'auto apply change' on the Bones Specific Page"$0D
                    "and either use the 'Paint brush' or do a 'LMB'"$0D
                    "linear handle drag to select them."$0D
                    "After an 'undo' you MUST click the 'update dialog'"$0D
                    "button to reload the old settings."$0D0D
                    "When this dialog is closed it will save all data anyway."
             Cap = "apply changes"
            }
         auto_save_weights: =
            {
             Typ = "X"
             Txt = "auto save"
             Hint = "When checked, all settings that are changed using"$0D
                    "this dialog will be saved as they are made."$0D
                    "With large models this can slow down"$0D
                    "the editor's response time dramatically."$0D
                    "If so, un-check this option and use the"$0D
                    "'apply changes' button above when desired."$0D0D
                    "When this dialog is closed it will save all data anyway."
            }
         sep: = { Typ = "S" Txt = ""}
         exit:py = {Txt = "" }
        }
        """

        src = self.src
      ### To populate settings...
        if len(editor.ModelComponentList[comp.name]['weightvtxlist']) != 0:
            weightvtxlist = editor.ModelComponentList[comp.name]['weightvtxlist']
        else:
            weightvtxlist = None
        src["comp_name"] = comp.name
        src["page_changer"] = str(WeightsDlgPage + 1)
        if comp.dictspec.has_key("auto_save_weights"):
            if comp.dictspec["auto_save_weights"] == "1":
                src["auto_save_weights"] = ""
            else:
                src["auto_save_weights"] = "1"
        else:
            src["auto_save_weights"] = "1"
        for key in self.SRClables.keys():
            src[key] = self.SRClables[key]
        for key in self.SRCsList.keys():
            if (quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] is None):
                src[key] = self.SRCsList[key]
                quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] = src[key]
                src[key] = "%.2f"%(float(src[key]))
            else:
                src[key] = quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key]
                src[key] = "%.2f"%(float(src[key]))

    def action(self, editor=editor):
        comp = editor.Root.currentcomponent
        if self.src["auto_save_weights"] == "1":
            comp["auto_save_weights"] = "0"
        else:
            comp["auto_save_weights"] = "1"

        global WeightsDlgPage
        if self.src["page_changer"].isdigit():
            if WeightsDlgPage != int(self.src["page_changer"]) - 1:
                WeightsDlgPage = int(self.src["page_changer"]) - 1
                if WeightsDlgPage < 0:
                    # If somebody types "0" or some negative number
                    WeightsDlgPage = 0
                vtxweightsclick(None)
        else:
            self.src["page_changer"] = str(WeightsDlgPage + 1)

        weightvtxlist = editor.ModelComponentList[comp.name]['weightvtxlist']
        for key in self.SRCsList.keys():
            if not (self.src[key] is None):
                vtxkey =  float(self.src[key])
                if vtxkey >= 2:
                    vtxkey = 1.0
                elif vtxkey > 1:
                    vtxkey = round(vtxkey,2) - 0.95
                elif vtxkey == 0:
                    vtxkey = 0.95
                elif vtxkey == -1.0 or vtxkey == -0.95:
                    vtxkey = 0.05
                elif vtxkey < 0:
                    vtxkey = round(vtxkey,2) + 0.95
                # Needed for hand entered amounts to keep value valid.
                if vtxkey > 1:
                    vtxkey = 1.0
                elif vtxkey < 0.01:
                    vtxkey = 0.01
                quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] = str(vtxkey)
                self.src[key] = quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key]
                vtx, bonename = key.split("_", 1)
                vtx = int(vtx)
                bonename = bonename + ":bone"
                if weightvtxlist[vtx][bonename]['weight_value'] != vtxkey:
                    try: # Need this to avoid an error in case we are in "Face mode"
                         # which means the bones are being hidden, thus causing an error.
                        weight_value = weightvtxlist[vtx][bonename]['weight_value'] = vtxkey
                        weightvtxlist[vtx][bonename]['color'] = weights_color(editor, weight_value)
                        for v in editor.layout.views:
                            cv = v.canvas()
                            h = v.handles[vtx]
                            h.draw(v, cv, h)
                        # Saves the ModelComponentList to "pickle" and updates the editor's 'ModelComponentList:sd' data.
                        if comp.dictspec.has_key("auto_save_weights") and comp.dictspec["auto_save_weights"] == "0":
                            editor.Root.dictitems['ModelComponentList:sd']['data'] = FlattenModelComponentList(editor)
                    except:
                        pass

    def onclosing(self, editor=editor):
        prev_comp = self.src["comp_name"]
        if editor.Root.dictitems[prev_comp].dictspec.has_key("auto_save_weights") and editor.Root.dictitems[prev_comp].dictspec['auto_save_weights'] != "1":
            weightvtxlist = editor.ModelComponentList[prev_comp]['weightvtxlist']
            for key in self.SRCsList.keys():
                vtx, bone = key.split("_", 1)
                if quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] is not None:
                    try:
                        weight_value = weightvtxlist[int(vtx)][bone + ":bone"]['weight_value'] = float(quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key])
                        weightvtxlist[int(vtx)][bone + ":bone"]['color'] = weights_color(editor, weight_value)
                    except:
                        pass
                    quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] = None
            o = editor.Root.currentcomponent
            undo = quarkx.action()
            newframe = o.currentframe.copy()
            undo.exchange(o.currentframe, newframe)
            prev_comp = prev_comp.replace(":mc", "")
            editor.ok(undo, prev_comp + ' weight settings saved')
        else:
            for key in self.SRCsList.keys():
                quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] = None

    WeightsDlg(quarkx.clickform, 'weightsdlg', editor, setup, action, onclosing)

def vtxweightsclick(btn):
    editor = mdleditor.mdleditor # Get the editor.
    comp = editor.Root.currentcomponent
    try: # Updates the dialog.
        for key in SRCsList.keys():
            quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] = None
        AddStuff(editor)
        name = editor.weightsdlg.name or editor.weightsdlg.__class__.__name__
        editor.weightsdlg.setup(editor.weightsdlg)
        f = quarkx.newobj("Dlg:form")
        f.loadtext(editor.weightsdlg.dlgdef)
        editor.weightsdlg.f = f
        for pybtn in f.findallsubitems("", ':py'):
            pybtn["sendto"] = name
        editor.weightsdlg.df.setdata(editor.weightsdlg.src, editor.weightsdlg.f)
    except: # Opens this dialog.
        WeightsClick(editor)
        for key in SRCsList.keys():
            quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] = None
        if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
            editor.ModelVertexSelList = []
            editor.linearbox = "True"
            editor.linear1click(btn)
        
def macro_selectvtxs(btn):
    editor = mdleditor.mdleditor # Get the editor.
    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
        quarkx.beep() # Makes the computer "Beep" once.
        quarkx.msgbox("You are in Face mode !\n\nYou must switch to Vertex\nmode to use this function.", qutils.MT_ERROR, qutils.MB_OK)
        return
    foundvtxs = 0
    foundframe = 0
    for item in editor.layout.explorer.sellist:
        if item.type == ":mf":
            foundframe = 1
            break
    if foundframe == 1 and len(WeightedVTXlist) != 0 and editor.layout.explorer.sellist[0].type == ":bone":
        for item in editor.layout.explorer.sellist:
            if item.type == ":bone":
                for weight in WeightedVTXlist:
                    if item.name == weight[1]:
                        if foundvtxs == 0:
                            editor.ModelVertexSelList = []
                            foundvtxs = 1
                        if not weight[0] in editor.ModelVertexSelList:
                            editor.ModelVertexSelList = editor.ModelVertexSelList + [weight[0]]
    else:
        if foundframe == 1 and len(WeightedVTXlist) != 0:
            if foundvtxs == 0:
                editor.ModelVertexSelList = []
                foundvtxs = 1
            for weight in WeightedVTXlist:
                if not weight[0] in editor.ModelVertexSelList:
                    editor.ModelVertexSelList = editor.ModelVertexSelList + [weight[0]]
    if foundframe == 1 and foundvtxs == 0:
        quarkx.msgbox("No weighted \ shared vertexes found.", qutils.MT_INFORMATION, qutils.MB_OK)
        return
    elif foundframe == 0:
        quarkx.beep() # Makes the computer "Beep" once.
        quarkx.msgbox("No model frame selected !\n\nYou must select one\nto use this function.", qutils.MT_ERROR, qutils.MB_OK)
        return
    else:
        Update_Editor_Views(editor)

def macro_updatedialog(btn):
    editor = mdleditor.mdleditor # Get the editor.
    comp = editor.Root.currentcomponent
    for key in SRCsList.keys():
        quarkx.setupsubset(SS_MODEL, "Options")["vtx_" + key] = None
    AddStuff(editor)
    name = editor.weightsdlg.name or editor.weightsdlg.__class__.__name__
    editor.weightsdlg.setup(editor.weightsdlg)
    f = quarkx.newobj("Dlg:form")
    f.loadtext(editor.weightsdlg.dlgdef)
    editor.weightsdlg.f = f
    for pybtn in f.findallsubitems("", ':py'):
        pybtn["sendto"] = name
    editor.weightsdlg.df.setdata(editor.weightsdlg.src, editor.weightsdlg.f)

def macro_applychanges(btn):
    editor = mdleditor.mdleditor # Get the editor.
    foundframe = 0
    for item in editor.layout.explorer.sellist:
        if item.type == ":mf":
            foundframe = 1
            break
    if foundframe == 0:
        quarkx.beep() # Makes the computer "Beep" once.
        quarkx.msgbox("No model frame selected !\n\nYou must select one\nto save these settings.", qutils.MT_ERROR, qutils.MB_OK)
        return
    if len(WeightedVTXlist) == 0:
        quarkx.msgbox("No weighted \ shared vertexes found.", qutils.MT_INFORMATION, qutils.MB_OK)
        return
    else:
        o = editor.Root.currentcomponent
        try:
            newframe = o.currentframe.copy()
        except:
            quarkx.beep() # Makes the computer "Beep" once.
            quarkx.msgbox("No Current Frame !\n\nFor some reason the current component\ndoes not have a current frame selection.\n\nClick on the component's frame and try again.", qutils.MT_ERROR, qutils.MB_OK)
            return
        undo = quarkx.action()
        undo.exchange(o.currentframe, newframe)
        compname = o.shortname
        editor.ok(undo, compname + ' weight settings saved')

qmacro.MACRO_selectvtxs = macro_selectvtxs
qmacro.MACRO_updatedialog = macro_updatedialog
qmacro.MACRO_applychanges = macro_applychanges


###############################
#
# Entity Manager base class, followed by subclasses.
#
###############################
def ObjectOrigin(o):
    "Returns the origin of the object o, or the center of its bounding box."
    pos = o.origin
    if pos is None:
        #
        # The object has no "origin", let's compute its bounding box.
        #
        box = quarkx.boundingboxof([o])
        if box is None:
            return None
        pos = 0.5*(box[0]+box[1])
    return pos


class EntityManager:
    "Base class for entity managers."

    #
    # All methods below are here to be overridden in subclasses.
    #

    def drawback(o, editor, view, mode, usecolor2=None):
        "Called to draw the Model's Mesh for the 'Component' object 'o'"
        "when in 'Textured', 'Solid' or 'Wire Frame' view mode, for each animation 'frame'."

        import qhandles
        if view.info["viewname"] == "XY":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is None:
                meshcolor = MapColor("Options3Dviews_frameColor2", SS_MODEL)
                if (o.type == ":mr") or (o.type == ":mg") or (o.type == ":bound") or (o.type == ":tag") or (o.type == ":tagframe"):
                    o = editor.Root
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines.
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            if editor.Root.dictitems[item].name != o.name:
                                view.drawmap(editor.Root.dictitems[item], mode)  # Draws default color for model mesh lines.
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines last to avoid other lines drawing over them.
            elif quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is not None:
                DummyItem = o
                while (DummyItem is not None):
                    if DummyItem.type == ":mr":
                        DummyItem = None
                        break
                    if DummyItem.type == ":mc" or DummyItem.type == ":bg":
                        break
                    else:
                        DummyItem = DummyItem.parent
                if DummyItem is None: # This section handles the drawing of non-component type items.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            comp = editor.Root.dictitems[item]
                            # This also draws the lines for a single selection item in wire frame mode.
                            if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                else:
                    if view.viewmode == "wire": # Draws multiple selection wire frame items.
                        o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                        for item in editor.Root.dictitems:
                            if editor.Root.dictitems[item].type == ":mc":
                                if editor.Root.dictitems[item].name != o.name:
                                    comp = editor.Root.dictitems[item]
                                    if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                        meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                        quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                        meshcolor = MapColor("meshcolor", SS_MODEL)
                                        view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                                    else:
                                        view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                        # Causes lines to be drawn using comp_color2 and
                        # Draws selected color for model mesh lines last to avoid other lines drawing over them.
                        if o.dictspec.has_key("usecolor2") and o.dictspec['usecolor2'] == "1":
                            if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                meshcolor = o.dictspec['comp_color2']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
                        elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                            meshcolor = o.dictspec['comp_color1']
                            quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                            meshcolor = MapColor("meshcolor", SS_MODEL)
                            view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                        else:
                            view.drawmap(o, mode)  # Draws default color for model mesh lines.
                    else: # This section handles textured and solid view modes.
                        if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] != "1":
                            pass    
                        else:
                            o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                            # Causes lines to be drawn using comp_color2.
                            if usecolor2 is not None:
                                if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                    meshcolor = o.dictspec['comp_color2']
                                    quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                    meshcolor = MapColor("meshcolor", SS_MODEL)
                                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                                else:
                                    view.drawmap(o, mode)  # Draws default color for model mesh lines.
                            elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                                meshcolor = o.dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
            else:
                if view.viewmode == "wire":
                    o = editor.Root
                view.drawmap(o, mode)  # Draws default color for model mesh lines.

        elif view.info["viewname"] == "XZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is None:
                meshcolor = MapColor("Options3Dviews_frameColor4", SS_MODEL)
                if (o.type == ":mr") or (o.type == ":mg") or (o.type == ":bound") or (o.type == ":tag") or (o.type == ":tagframe"):
                    o = editor.Root
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines.
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            if editor.Root.dictitems[item].name != o.name:
                                view.drawmap(editor.Root.dictitems[item], mode)  # Draws default color for model mesh lines.
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines last to avoid other lines drawing over them.
            elif quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is not None:
                DummyItem = o
                while (DummyItem is not None):
                    if DummyItem.type == ":mr":
                        DummyItem = None
                        break
                    if DummyItem.type == ":mc" or DummyItem.type == ":bg":
                        break
                    else:
                        DummyItem = DummyItem.parent
                if DummyItem is None: # This section handles the drawing of non-component type items.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            comp = editor.Root.dictitems[item]
                            # This also draws the lines for a single selection item in wire frame mode.
                            if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                else:
                    if view.viewmode == "wire": # Draws multiple selection wire frame items.
                        o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                        for item in editor.Root.dictitems:
                            if editor.Root.dictitems[item].type == ":mc":
                                if editor.Root.dictitems[item].name != o.name:
                                    comp = editor.Root.dictitems[item]
                                    if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                        meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                        quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                        meshcolor = MapColor("meshcolor", SS_MODEL)
                                        view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                                    else:
                                        view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                        # Causes lines to be drawn using comp_color2 and
                        # Draws selected color for model mesh lines last to avoid other lines drawing over them.
                        if o.dictspec.has_key("usecolor2") and o.dictspec['usecolor2'] == "1":
                            if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                meshcolor = o.dictspec['comp_color2']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
                        elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                            meshcolor = o.dictspec['comp_color1']
                            quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                            meshcolor = MapColor("meshcolor", SS_MODEL)
                            view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                        else:
                            view.drawmap(o, mode)  # Draws default color for model mesh lines.
                    else: # This section handles textured and solid view modes.
                        if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] != "1":
                            pass    
                        else:
                            o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                            # Causes lines to be drawn using comp_color2.
                            if usecolor2 is not None:
                                if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                    meshcolor = o.dictspec['comp_color2']
                                    quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                    meshcolor = MapColor("meshcolor", SS_MODEL)
                                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                                else:
                                    view.drawmap(o, mode)  # Draws default color for model mesh lines.
                            elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                                meshcolor = o.dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
            else:
                if view.viewmode == "wire":
                    o = editor.Root
                view.drawmap(o, mode)  # Draws default color for model mesh lines.

        elif view.info["viewname"] == "YZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is None:
                meshcolor = MapColor("Options3Dviews_frameColor3", SS_MODEL)
                if (o.type == ":mr") or (o.type == ":mg") or (o.type == ":bound") or (o.type == ":tag") or (o.type == ":tagframe"):
                    o = editor.Root
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines.
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            if editor.Root.dictitems[item].name != o.name:
                                view.drawmap(editor.Root.dictitems[item], mode)  # Draws default color for model mesh lines.
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines last to avoid other lines drawing over them.
            elif quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is not None:
                DummyItem = o
                while (DummyItem is not None):
                    if DummyItem.type == ":mr":
                        DummyItem = None
                        break
                    if DummyItem.type == ":mc" or DummyItem.type == ":bg":
                        break
                    else:
                        DummyItem = DummyItem.parent
                if DummyItem is None: # This section handles the drawing of non-component type items.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            comp = editor.Root.dictitems[item]
                            # This also draws the lines for a single selection item in wire frame mode.
                            if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                else:
                    if view.viewmode == "wire": # Draws multiple selection wire frame items.
                        o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                        for item in editor.Root.dictitems:
                            if editor.Root.dictitems[item].type == ":mc":
                                if editor.Root.dictitems[item].name != o.name:
                                    comp = editor.Root.dictitems[item]
                                    if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                        meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                        quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                        meshcolor = MapColor("meshcolor", SS_MODEL)
                                        view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                                    else:
                                        view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                        # Causes lines to be drawn using comp_color2 and
                        # Draws selected color for model mesh lines last to avoid other lines drawing over them.
                        if o.dictspec.has_key("usecolor2") and o.dictspec['usecolor2'] == "1":
                            if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                meshcolor = o.dictspec['comp_color2']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
                        elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                            meshcolor = o.dictspec['comp_color1']
                            quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                            meshcolor = MapColor("meshcolor", SS_MODEL)
                            view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                        else:
                            view.drawmap(o, mode)  # Draws default color for model mesh lines.
                    else: # This section handles textured and solid view modes.
                        if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] != "1":
                            pass    
                        else:
                            o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                            # Causes lines to be drawn using comp_color2.
                            if usecolor2 is not None:
                                if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                    meshcolor = o.dictspec['comp_color2']
                                    quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                    meshcolor = MapColor("meshcolor", SS_MODEL)
                                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                                else:
                                    view.drawmap(o, mode)  # Draws default color for model mesh lines.
                            elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                                meshcolor = o.dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
            else:
                if view.viewmode == "wire":
                    o = editor.Root
                view.drawmap(o, mode)  # Draws default color for model mesh lines.

        elif view.info["viewname"] == "editors3Dview":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is None:
                meshcolor = MapColor("Options3Dviews_frameColor1", SS_MODEL)
                if (o.type == ":mr") or (o.type == ":mg") or (o.type == ":bound") or (o.type == ":tag") or (o.type == ":tagframe"):
                    o = editor.Root
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines.
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            if editor.Root.dictitems[item].name != o.name:
                                view.drawmap(editor.Root.dictitems[item], mode)  # Draws default color for model mesh lines.
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines last to avoid other lines drawing over them.
            elif quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is not None:
                DummyItem = o
                while (DummyItem is not None):
                    if DummyItem.type == ":mr":
                        DummyItem = None
                        break
                    if DummyItem.type == ":mc" or DummyItem.type == ":bg":
                        break
                    else:
                        DummyItem = DummyItem.parent
                if DummyItem is None: # This section handles the drawing of non-component type items.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            comp = editor.Root.dictitems[item]
                            # This also draws the lines for a single selection item in wire frame mode.
                            if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                else:
                    if view.viewmode == "wire": # Draws multiple selection wire frame items.
                        o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                        for item in editor.Root.dictitems:
                            if editor.Root.dictitems[item].type == ":mc":
                                if editor.Root.dictitems[item].name != o.name:
                                    comp = editor.Root.dictitems[item]
                                    if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                        meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                        quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                        meshcolor = MapColor("meshcolor", SS_MODEL)
                                        view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                                    else:
                                        view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                        # Causes lines to be drawn using comp_color2 and
                        # Draws selected color for model mesh lines last to avoid other lines drawing over them.
                        if o.dictspec.has_key("usecolor2") and o.dictspec['usecolor2'] == "1":
                            if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                meshcolor = o.dictspec['comp_color2']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
                        elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                            meshcolor = o.dictspec['comp_color1']
                            quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                            meshcolor = MapColor("meshcolor", SS_MODEL)
                            view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                        else:
                            view.drawmap(o, mode)  # Draws default color for model mesh lines.
                    else: # This section handles textured and solid view modes.
                        if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] != "1":
                            pass    
                        else:
                            o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                            # Causes lines to be drawn using comp_color2.
                            if usecolor2 is not None:
                                if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                    meshcolor = o.dictspec['comp_color2']
                                    quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                    meshcolor = MapColor("meshcolor", SS_MODEL)
                                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                                else:
                                    view.drawmap(o, mode)  # Draws default color for model mesh lines.
                            elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                                meshcolor = o.dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
            else:
                if view.viewmode == "wire":
                    o = editor.Root
                view.drawmap(o, mode)  # draws default color for model mesh lines
            if editor.ModelFaceSelList != []:
                # draws model mesh faces, if selected, while rotating, panning or zooming.
                if isinstance(editor.dragobject, qhandles.Rotator2D) or isinstance(editor.dragobject, qhandles.ScrollViewDragObject) or isinstance(editor.dragobject, qhandles.FreeZoomDragObject):
                    mdlhandles.ModelFaceHandle(mode).draw(editor, view, editor.EditorObjectList)

        elif view.info["viewname"] == "3Dwindow":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] == "1" and quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is None:
                meshcolor = MapColor("Options3Dviews_frameColor5", SS_MODEL)
                if (o.type == ":mr") or (o.type == ":mg") or (o.type == ":bound") or (o.type == ":tag") or (o.type == ":tagframe"):
                    o = editor.Root
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines.
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            if editor.Root.dictitems[item].name != o.name:
                                view.drawmap(editor.Root.dictitems[item], mode)  # Draws default color for model mesh lines.
                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # Draws selected color for model mesh lines last to avoid other lines drawing over them.
            elif quarkx.setupsubset(SS_MODEL, "Options")["CompColors"] is not None:
                DummyItem = o
                while (DummyItem is not None):
                    if DummyItem.type == ":mr":
                        DummyItem = None
                        break
                    if DummyItem.type == ":mc" or DummyItem.type == ":bg":
                        break
                    else:
                        DummyItem = DummyItem.parent
                if DummyItem is None: # This section handles the drawing of non-component type items.
                    for item in editor.Root.dictitems:
                        if editor.Root.dictitems[item].type == ":mc":
                            comp = editor.Root.dictitems[item]
                            # This also draws the lines for a single selection item in wire frame mode.
                            if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                else:
                    if view.viewmode == "wire": # Draws multiple selection wire frame items.
                        o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                        for item in editor.Root.dictitems:
                            if editor.Root.dictitems[item].type == ":mc":
                                if editor.Root.dictitems[item].name != o.name:
                                    comp = editor.Root.dictitems[item]
                                    if comp.dictspec.has_key("comp_color1") and comp.dictspec['comp_color1'] != "\x00":
                                        meshcolor = editor.Root.dictitems[item].dictspec['comp_color1']
                                        quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                        meshcolor = MapColor("meshcolor", SS_MODEL)
                                        view.drawmap(comp, DM_OTHERCOLOR, meshcolor)
                                    else:
                                        view.drawmap(comp, mode)  # Draws default color for model mesh lines.
                        # Causes lines to be drawn using comp_color2 and
                        # Draws selected color for model mesh lines last to avoid other lines drawing over them.
                        if o.dictspec.has_key("usecolor2") and o.dictspec['usecolor2'] == "1":
                            if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                meshcolor = o.dictspec['comp_color2']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
                        elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                            meshcolor = o.dictspec['comp_color1']
                            quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                            meshcolor = MapColor("meshcolor", SS_MODEL)
                            view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                        else:
                            view.drawmap(o, mode)  # Draws default color for model mesh lines.
                    else: # This section handles textured and solid view modes.
                        if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] != "1":
                            pass    
                        else:
                            o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                            # Causes lines to be drawn using comp_color2.
                            if usecolor2 is not None:
                                if o.dictspec.has_key("comp_color2") and o.dictspec['comp_color2'] != "\x00":
                                    meshcolor = o.dictspec['comp_color2']
                                    quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                    meshcolor = MapColor("meshcolor", SS_MODEL)
                                    view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                                else:
                                    view.drawmap(o, mode)  # Draws default color for model mesh lines.
                            elif o.dictspec.has_key("comp_color1") and o.dictspec['comp_color1'] != "\x00":
                                meshcolor = o.dictspec['comp_color1']
                                quarkx.setupsubset(SS_MODEL, "Colors")["meshcolor"] = meshcolor
                                meshcolor = MapColor("meshcolor", SS_MODEL)
                                view.drawmap(o, DM_OTHERCOLOR, meshcolor)
                            else:
                                view.drawmap(o, mode)  # Draws default color for model mesh lines.
            else:
                view.drawmap(o, mode)  # draws default color for model mesh lines
            if editor.ModelFaceSelList != []:
                # draws model mesh faces, if selected, while rotating, panning or zooming.
                if isinstance(editor.dragobject, qhandles.Rotator2D) or isinstance(editor.dragobject, qhandles.ScrollViewDragObject) or isinstance(editor.dragobject, qhandles.FreeZoomDragObject):
                    mdlhandles.ModelFaceHandle(mode).draw(editor, view, editor.EditorObjectList)

    def drawsel(o, view, mode):
        "Called to draw the Model's Mesh for the 'Component' object 'o'"
        "when in 'Wireframe' view mode, for each animation 'frame'."

        import qhandles
        import mdleditor
        editor = mdleditor.mdleditor
        if view.info["viewname"] == "XY":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh2"] == "1":
                if (o.type == ":mr") or (o.type == ":mg"):
                    o = editor.Root
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                meshcolor = MapColor("Options3Dviews_frameColor2", SS_MODEL)
                view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # draws selected color for model mesh lines
            else:
                view.drawmap(o, mode)  # draws default color for model mesh lines

        elif view.info["viewname"] == "XZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh4"] == "1":
                if (o.type == ":mr") or (o.type == ":mg"):
                    o = editor.Root
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                meshcolor = MapColor("Options3Dviews_frameColor4", SS_MODEL)
                view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # draws selected color for model mesh lines
            else:
                view.drawmap(o, mode)  # draws default color for model mesh lines

        elif view.info["viewname"] == "YZ":
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh3"] == "1":
                if (o.type == ":mr") or (o.type == ":mg"):
                    o = editor.Root
                else:
                    o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
                meshcolor = MapColor("Options3Dviews_frameColor3", SS_MODEL)
                view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # draws selected color for model mesh lines
            else:
                view.drawmap(o, mode)  # draws default color for model mesh lines

        elif view.info["viewname"] == "editors3Dview":
            if (o.type == ":mr") or (o.type == ":mg"):
                o = editor.Root
            else:
                o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh1"] == "1":
                meshcolor = MapColor("Options3Dviews_frameColor1", SS_MODEL)
                view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # draws selected color for model mesh lines
            else:
                view.drawmap(o, mode)  # draws default color for model mesh lines
            if editor.ModelFaceSelList != []:
                # draws model mesh faces, if selected, while rotating, panning or zooming.
                if isinstance(editor.dragobject, qhandles.Rotator2D) or isinstance(editor.dragobject, qhandles.ScrollViewDragObject) or isinstance(editor.dragobject, qhandles.FreeZoomDragObject):
                    mdlhandles.ModelFaceHandle(mode).draw(editor, view, editor.EditorObjectList)

        elif view.info["viewname"] == "3Dwindow":
            if (o.type == ":mr") or (o.type == ":mg"):
                o = editor.Root
            else:
                o = editor.Root.currentcomponent # Redefining o like this allows the model's mesh lines to be drawn.
            if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_framemesh5"] == "1":
                meshcolor = MapColor("Options3Dviews_frameColor5", SS_MODEL)
                view.drawmap(o, DM_OTHERCOLOR, meshcolor)  # draws selected color for model mesh lines
            else:
                view.drawmap(o, mode)  # draws default color for model mesh lines
            if editor.ModelFaceSelList != []:
                # draws model mesh faces, if selected, while rotating, panning or zooming.
                if isinstance(editor.dragobject, qhandles.Rotator2D) or isinstance(editor.dragobject, qhandles.ScrollViewDragObject) or isinstance(editor.dragobject, qhandles.FreeZoomDragObject):
                    mdlhandles.ModelFaceHandle(mode).draw(editor, view, editor.EditorObjectList)

    def handles(o, editor, view):
        "Build a list of handles related to this object."
        return []

    def handlesopt(o, editor):
        "Optimized view-independant version of 'handles'."
        return []

    def applylinear(entity, matrix):
        "Apply a linear mapping on this object."
        pass

    def dataformname(o):
        "The name of the data form, or the data form itself,"
        "to use for the Specific/Args page. See 'class BoneType' below for example."
        "Returns the data form for this type of object 'o' (a bone) to use for the Specific/Args page."
        return "Default" + o.type

    def menu(o, editor):
        "A pop-up menu related to the object."
        import mdlmenus
        return CallManager("menubegin", o, editor) + mdlmenus.BaseMenu([o], editor)

    def menubegin(o, editor):
        return []


class DuplicatorType(EntityManager):
    "Duplicators"

    def applylinear(entity, matrix):
        try:
            import mdlduplicator
            mdlduplicator.DupManager(entity).applylinear(matrix)
        except:
            pass

    def dataformname(o):
        import mdlduplicator
        return mdlduplicator.DupManager(o).dataformname()

    def handles(o, editor, view=None):
        import mdlduplicator
        return mdlduplicator.DupManager(o).handles(editor, view)


class GroupType(EntityManager):
    "Generic Model object type."

    def handles(o, editor, view=None):
        pos = ObjectOrigin(o)
        if pos is None:
            return []
        h = [mdlhandles.CenterHandle(pos, o, MapColor("Tag"))]
        return h


class MiscGroupType(EntityManager):
    "Misc. Object Group, type = :mg"


# Has no subitems or dictitems items, only dictspec items (synctype and flags).
class ModelRootType(EntityManager):
    "Model Root, type = :mr"

    def dataformname(o):
        "Returns the data form for this type of object 'o' (the Model Root) to use for the Specific/Args page."

        import mdleditor
        editor = mdleditor.mdleditor
        root = editor.Root

        dlgdef = """
        {
          Help = "These are the Specific settings for the Model Root."$0D
                 "Used for Quake 1 and Hexen II .mdl models only."$0D0D22
                 "synctype"$22" - Select an item from this dropdown list."$0D22
                 "flags"$22" - Select an item from this dropdown list."
          synctype_setting: = {
              Txt="synctype"
              Typ = "C"
              Hint="Select an item from this dropdown list."
          items =
              "synchron"$0D
              "random"
          values =
              "0"$0D
              "1"
                 }

          flags_setting: = {
              Txt="flags"
              Typ = "C"
              Hint="Select an item from this dropdown list."
          items =
              "None"$0D
              "ROCKET-leave trail"$0D
              "GRENADE-leave trail"$0D
              "GIB-leave trail"$0D
              "ROTATE"$0D
              "TRACER-green split trail"$0D
              "ZOMGIB-small blood trail"$0D
              "TRACER2-orange split trail + rotate"$0D
              "TRACER3-purple trail"$0D
              "FIREBALL-Yellow transparent trail in all directions"$0D
              "ICE-Blue-white transparent trail, with gravity"$0D
              "MIP_MAP-This model has mip-maps"$0D
              "SPIT-Black transparent trail with negative light"$0D
              "TRANSPARENT-Transparent sprite"$0D
              "SPELL-Vertical spray of particles"$0D
              "HOLEY-Solid model with color 0"$0D
              "SPECIAL_TRANS-Translucency through the particle table"$0D
              "FACE_VIEW-Poly Model always faces you"$0D
              "VORP_MISSILE-leave a trail at top and bottom of model"$0D
              "SET_STAFF-slowly move up and left/right"$0D
              "MAGICMISSILE-a trickle of blue/white particles with gravity"$0D
              "BONESHARD-a trickle of brown particles with gravity"$0D
              "SCARAB-white transparent particles with little gravity"$0D
              "ACIDBALL-Green drippy acid shit"$0D
              "BLOODSHOT-Blood rain shot trail"$0D
              "MIP_MAP_FAR-Set per frame, this model will use the far mip map"$0D
          values =
              "0"$0D
              "1"$0D
              "2"$0D
              "4"$0D
              "8"$0D
              "16"$0D
              "32"$0D
              "64"$0D
              "128"$0D
              "256"$0D
              "512"$0D
              "1024"$0D
              "2048"$0D
              "4096"$0D
              "8192"$0D
              "16384"$0D
              "32768"$0D
              "65536"$0D
              "131072"$0D
              "262144"$0D
              "524288"$0D
              "1048576"$0D
              "2097152"$0D
              "4194304"$0D
              "8388608"$0D
              "16777216"
                 }
        }
        """

        if o.dictspec.has_key("synctype_setting"):
            o['synctype'] = o.dictspec['synctype_setting']
        else:
            if o.dictspec.has_key("synctype"):
                o['synctype_setting'] = o.dictspec['synctype']
            else:
                o['synctype_setting'] = "0"
        if o.dictspec.has_key("flags_setting"):
            o['flags'] = o.dictspec['flags_setting']
        else:
            if o.dictspec.has_key("flags"):
                o['flags_setting'] = o.dictspec['flags']
            else:
                o['flags_setting'] = "0"

        formobj = quarkx.newobj("root:form")
        formobj.loadtext(dlgdef)
        return formobj


# Has no subitems or dictitems items, only dictspec items (position, mins, maxs and scale).
class BoundType(EntityManager):
    "Bound Frame, type = :bound"

    def dataformname(o):
        "Returns the data form for this type of object 'o' (a Bound Frame) to use for the Specific/Args page."

        dlgdef = """
        {
          Help = "These are the Specific settings for a Bound Frame."$0D0D22
                 "position"$22" - You must enter three values here."$0D
                 "          They have an accuracy of two digits."$0D22
                 "scale"$22" - You must enter one positive float value here."$0D
                 "          They have an accuracy of two digits."$0D22
                 "maxs"$22" - You must enter three values here."$0D
                 "          They have an accuracy of two digits."$0D22
                 "mins"$22" - You must enter three values here."$0D
                 "          They have an accuracy of two digits."
          sep: = {
              Typ="S"
              Txt="(Not funtional at this time)"
                 }
          position: = {
              Typ="EF003" 
              Txt="position"
              Hint="You must enter three values here."$0D"They have an accuracy of two digits."
                 }
          scale: = {
              Typ="EF001" 
              Txt="scale"
              Hint="You must enter one positive float value here."$0D"It has an accuracy of two digits."
                 }
          maxs: = {
              Typ="EF003" 
              Txt="maxs"
              Hint="You must enter three values here."$0D"They have an accuracy of two digits."
                 }
          mins: = {
              Typ="EF003" 
              Txt="mins"
              Hint="You must enter three values here."$0D"They have an accuracy of two digits."
                 }
        }
        """

        formobj = quarkx.newobj("bound:form")
        formobj.loadtext(dlgdef)
        return formobj


# Has no dictspec items, only subitems and dictitems (TagFrames).
class TagType(EntityManager):
    "Tag, type = :tag"

    def menu(o, editor):
        import qmenu

        def AttachTags(m, editor=editor):
            tag1model = m.tag1.shortname.split(":")[0]
            tag1model = tag1model.split("_tag_")
            tag1name = "tag_" + tag1model[len(tag1model)-1]
            tag1model = tag1model[0]

            tag2model = m.tag2.shortname.split(":")[0]
            tag2model = tag2model.split("_tag_")
            tag2name = "tag_" + tag2model[len(tag2model)-1]
            tag2model = tag2model[0]

            # This section connects the tags from two sepperate tag groups, ex: a player model and a weapon.
            if (tag1model != tag2model):
                for item in editor.Root.subitems:
                    if item.type == ":mc" and item.name.startswith(tag1model) and item.dictspec.has_key("Tags"):
                        tag1comp = item
                        tag1comp_tags = tag1comp.dictspec['Tags'].split(", ")
                    if item.type == ":mc" and item.name.startswith(tag2model) and item.dictspec.has_key("Tags"):
                        tag2comp = item
                        tag2comp_tags = tag2comp.dictspec['Tags'].split(", ")
                tagmatch = None
                for tag1name in tag1comp_tags:
                    for tag2name in tag2comp_tags:
                        if tag1name == tag2name:
                            tagmatch = 1
                            tag1name = tag1model + "_" + tag1name + ":tag"
                            try:
                                tag1 = editor.Root.dictitems['Misc:mg'].dictitems[tag1name]
                            except:
                                quarkx.msgbox("Tag Missing!\n\nThe needed model tag:\n    " + tag1name.replace(":tag", "") + "\ndoes not exist, may have been deleted.\nReload that same model and try again.", MT_ERROR, MB_OK)
                                return
                            tag2name = tag2model + "_" + tag2name + ":tag"
                            try:
                                tag2 = editor.Root.dictitems['Misc:mg'].dictitems[tag2name]
                            except:
                                quarkx.msgbox("Tag Missing!\n\nThe needed model tag:\n    " + tag2name.replace(":tag", "") + "\ndoes not exist, may have been deleted.\nReload that same model and try again.", MT_ERROR, MB_OK)
                                return
                            break

                if tagmatch is None:
                    quarkx.msgbox("No Tag Match!\n\nThese models do not have matching tags\nor one has been deleted.\nThey can not be used together.", MT_ERROR, MB_OK)
                    return
                attachtag_comps_list = []
                attachtags_list = []
                if len(tag1.subitems) >= len(tag2.subitems):
                    basetag = tag1
                    basetag_comp = tag1comp
                    attachtag = tag2
                    attachtag_comp = tag2comp
                    for item in editor.Root.subitems:
                        if item.type == ":mc" and item.name.startswith(tag2model):
                            attachtag_comps_list = attachtag_comps_list + [item]
                    for item in editor.Root.dictitems['Misc:mg'].subitems:
                        if item.type == ":tag" and item.name.startswith(tag2model):
                            attachtags_list = attachtags_list + [item]
                else:
                    basetag = tag2
                    basetag_comp = tag2comp
                    attachtag = tag1
                    attachtag_comp = tag1comp
                    for item in editor.Root.subitems:
                        if item.type == ":mc" and item.name.startswith(tag1model):
                            attachtag_comps_list = attachtag_comps_list + [item]
                    for item in editor.Root.dictitems['Misc:mg'].subitems:
                        if item.type == ":tag" and item.name.startswith(tag1model):
                            attachtags_list = attachtags_list + [item]

                # Assigns the weapon to the player model.
                group = basetag.name.split("_")[0]
                tags = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':tag')  # get all tags
                weapon = attachtag.name.split("_")[0]
                for tag in tags:
                    if tag.name.startswith(group) and tag.dictspec.has_key("animationCFG"):
                        if not tag.dictspec.has_key("weapons"):
                            tag['weapons'] = "None," + weapon
                            tag['weapon'] = "None"
                        else:
                            tag['weapons'] = tag.dictspec['weapons'] + "," + weapon

                basetag_subitems = basetag.subitems
                attachtag_subitems = attachtag.subitems
                new_comps_list = []
                new_tags_list = []
                for attachtag_comp in attachtag_comps_list:
                    newcomp = attachtag_comp.copy()
                    new_comps_list = new_comps_list + [newcomp]
                for attachtag_tag in attachtags_list:
                    newtag = quarkx.newobj(attachtag_tag.name)
                    for item in attachtag_tag.dictspec:
                        newtag[item] = attachtag_tag.dictspec[item]
                    new_tags_list = new_tags_list + [newtag]
                undo = quarkx.action()
                for newcomp in range(len(new_comps_list)):
                    comp_frames = new_comps_list[newcomp].dictitems["Frames:fg"].subitems
                    newframesgroup = quarkx.newobj('Frames:fg')
                    comp_framecount = len(comp_frames)-1
                    for frame in range(len(basetag_subitems)):
                        if frame == len(basetag_subitems)-1:
                            baseframe = comp_frames[comp_framecount].copy()
                            newframesgroup.appenditem(baseframe)
                            if newcomp == 0:
                                for newtag in range(len(new_tags_list)):
                                    tag_baseframe = attachtags_list[newtag].subitems[0].copy()
                                    new_tags_list[newtag].appenditem(tag_baseframe)
                            break
                        elif frame > len(attachtag_subitems)-1:
                            attachframe = attachtag_subitems[len(attachtag_subitems)-1]
                        else:
                            attachframe = attachtag_subitems[frame]
                        tag_pos_old = quarkx.vect(attachframe.dictspec['origin'])
                        tag_pos_new = quarkx.vect(basetag_subitems[frame].dictspec['origin'])
                        n_r = basetag_subitems[frame].dictspec['rotmatrix']
                        n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                        new_rotation = quarkx.matrix(n_r)
                        if frame >= comp_framecount:
                            comp_frame = comp_frames[comp_framecount].copy()
                        else:
                            comp_frame = comp_frames[frame]
                        comp_frame.shortname = "Frame " + str(frame+1)
                        vertices = []
                        for vtx in comp_frame.vertices:
                            vtx = vtx - tag_pos_old
                            vtx = (~new_rotation) * vtx
                            vtx = vtx + tag_pos_new
                            vertices = vertices + [vtx]
                        comp_frame.vertices = vertices
                        newframe = comp_frame.copy()
                        newframesgroup.appenditem(newframe)
                        if newcomp == 0:
                            for newtag in range(len(new_tags_list)):
                                tag_frame = attachtags_list[newtag].subitems[0].copy()
                                tag_frame.shortname = "Tag Frame " + str(frame+1)
                                new_tag_frame_origin = (~new_rotation) * quarkx.vect(tag_frame.dictspec['origin'])
                                tag_frame['origin'] = (new_tag_frame_origin + quarkx.vect(basetag_subitems[frame].dictspec['origin'])).tuple
                                #tag_frame['rotmatrix'] = @
                                new_tags_list[newtag].appenditem(tag_frame)
                    undo.exchange(new_comps_list[newcomp].dictitems['Frames:fg'], newframesgroup)
                for i in range(len(new_comps_list)):
                    undo.exchange(attachtag_comps_list[i], new_comps_list[i])
                for i in range(len(new_tags_list)):
                    undo.exchange(attachtags_list[i], new_tags_list[i])
                editor.ok(undo, "Attach tags")
            else:
                quarkx.msgbox("Invalid Selection!\n\nThe model tags can not be\nfrom the same 'group' of tags.", MT_ERROR, MB_OK)
                return

        attach_tags = qmenu.item("&Attach tags", AttachTags, "|Attach Tags:\n\nWhen two tags of different groups are selected, clicking this item will attach them creating matching tag frames, based on the one that has the most frames, for animation.|intro.modeleditor.editelements.html#tags")
        STT = qmenu.item("&Show these tags", ShowTheseTags, "|Show these tags:\n\nThis allows the selected tags to be displayed in the editor's views if the function 'Hide Tags' is not active.|intro.modeleditor.editelements.html#tags")
        HTT = qmenu.item("&Hide these tags", HideTheseTags, "|Hide these tags:\n\nThis stops the selected tags from being displayed in the editor's views.|intro.modeleditor.editelements.html#tags")
        DeleteTag = mdlhandles.TagHandle(None, o.subitems[0]).menu(editor, None)[len(mdlhandles.TagHandle(None).menu(editor, None))-1]

        attach_tags.tag1 = attach_tags.tag2 = None
        for item in editor.layout.explorer.sellist:
            if item.type == ":tag":
                if attach_tags.tag1 is None:
                    attach_tags.tag1 = item
                else:
                    attach_tags.tag2 = item
        if attach_tags.tag1 is None or attach_tags.tag2 is None:
            attach_tags.state = qmenu.disabled

        if not o.dictspec.has_key("show"):
            o['show'] = (1.0,)
        if o.dictspec['show'][0] == 1.0:
            STT.state = qmenu.disabled
        else:
            HTT.state = qmenu.disabled

        if len(editor.layout.explorer.sellist) == 1:
            return [attach_tags, qmenu.sep, STT, HTT, qmenu.sep, DeleteTag]
        else:
            return [attach_tags, qmenu.sep, STT, HTT]

    def dataformname(o):
        "Returns the data form for this type of object 'o' (a :tag) to use for the Specific/Args page."
        editor = mdleditor.mdleditor # Get the editor.
        # Next line calls for the Animation Configuration Module above in this file.
        Weapons = ""
        if not o.dictspec.has_key("animationCFG"):
            AnimationCFG_dialog_plugin = ""
            PlayList1 = ""
            PlayList2 = ""
        else:
            PlayList1 = ""
            PlayList2 = ""
            play_items1 = []
            play_values1 = []
            play_items2 = []
            play_values2 = []
            list_values = []
            max_BOTH = "0"
            max_TORSO = "0"
            CFGlines = o.dictspec['animationCFG']
            CFGlines = CFGlines.split("\r\n")
            for CFGline in CFGlines:
                if len(CFGline) == 0: # Empty line.
                    continue
                CFGline = CFGline.strip()
                try:
                    framenbr = int(CFGline[0])
                    if CFGline.find("//") == -1:
                        continue
                    spacecount = 0
                    tempstring = ""
                    for item in CFGline:
                        # Dec character code for space = chr(32), for tab = chr(9)
                        if item == chr(32) or item == chr(9):
                            if spacecount == 0:
                                tempstring = tempstring + ","
                                spacecount = 1
                            else:
                                continue
                        else:
                            tempstring = tempstring + item
                            spacecount = 0
                    CFGline = tempstring
                except:
                    continue
                CFGline = CFGline.split(",")
                for item in range(len(CFGline)):
                    if CFGline[item] == "//":
                        try:
                            if CFGline[item+1].startswith("BOTH_") or CFGline[item+1].startswith("TORSO_"):
                                play_items1 = play_items1 + ['"' + CFGline[item+1] + '"' + "$0D"]
                                play_values1 = play_values1 + ['"' + CFGline[item+1]+','+CFGline[0]+','+CFGline[1]+','+CFGline[2]+','+CFGline[3]]
                            else:
                                play_items2 = play_items2 + ['"' + CFGline[item+1] + '"' + "$0D"]
                                play_values2 = play_values2 + ['"' + CFGline[item+1]+','+CFGline[0]+','+CFGline[1]+','+CFGline[2]+','+CFGline[3] + '"' + "$0D"]
                            list_values = list_values + [[CFGline[item+1],CFGline[0],CFGline[1],CFGline[2],CFGline[3]]]
                            if CFGline[item+1].startswith("TORSO_") and max_BOTH == "0":
                                max_BOTH = CFGline[0]
                            if CFGline[item+1].startswith("LEGS_") and max_TORSO == "0":
                                max_TORSO = CFGline[0]
                        except: # Something is wrong with this line of data, making it invalid so go on to the next line.
                            continue

            if len(play_items1) != 0:
                PlayList1 = PlayList1 + """sep: = { Typ="S" Txt="" } play_list1: = {Typ = "CL" Txt = "Play list upper" items = """
                PlayList2 = PlayList2 + """sep: = { Typ="S" Txt="" } play_list2: = {Typ = "CL" Txt = "Play list lower" items = """
                for item in play_items1:
                    PlayList1 = PlayList1 + item
                for item in play_items2:
                    PlayList2 = PlayList2 + item

                PlayList1 = PlayList1 + """ values = """
                PlayList2 = PlayList2 + """ values = """
                for value in play_values1:
                    PlayList1 = PlayList1 + value + ','+max_BOTH+','+max_TORSO + '"' + "$0D"
                for value in play_values2:
                    PlayList2 = PlayList2 + value

                PlayList1 = PlayList1 + """ Hint="List of available animations for this group."$0D"Click on one to play its components scquence."$0D"If 'BOTH_' is selected 'Play list lower' is ignored."}"""
                PlayList1 = PlayList1 + """first_frame1:    = {Typ="E R" Txt="first frame"    Hint="The frame animation starts at. (read only)"}"""
                PlayList1 = PlayList1 + """num_frames1:     = {Typ="E R" Txt="num frame"      Hint="The number of frames in the animation sequence. (read only)"}"""
                PlayList1 = PlayList1 + """looping_frames1: = {Typ="E R" Txt="looping frames" Hint="The frames played in a loop. (read only)"}"""
                PlayList1 = PlayList1 + """CFG_FPS1:        = {Typ="E R" Txt="CFG FPS"        Hint="The set frames per second to play this animation. (read only)"}"""

                PlayList2 = PlayList2 + """ Hint="List of available animations for this group."$0D"Click on one to play its components scquence."$0D"If 'BOTH_' is selected 'Play list lower' is ignored."}"""
                PlayList2 = PlayList2 + """first_frame2:    = {Typ="E R" Txt="first frame"    Hint="The frame animation starts at. (read only)"}"""
                PlayList2 = PlayList2 + """num_frames2:     = {Typ="E R" Txt="num frame"      Hint="The number of frames in the animation sequence. (read only)"}"""
                PlayList2 = PlayList2 + """looping_frames2: = {Typ="E R" Txt="looping frames" Hint="The frames played in a loop. (read only)"}"""
                PlayList2 = PlayList2 + """CFG_FPS2:        = {Typ="E R" Txt="CFG FPS"        Hint="The set frames per second to play this animation. (read only)"}"""

                if o.dictspec.has_key("weapons"):
                    weapons = o.dictspec['weapons'].split(",")
                    weapons_items = []
                    weapons_values = []
                    for item in range(len(weapons)):
                        weapons_items = weapons_items + ['"' + weapons[item] + '"' + "$0D"]
                        weapons_values = weapons_values + ['"' + weapons[item] + '"' + "$0D"]
                    Weapons = Weapons + """sep: = { Typ="S" Txt="" } weapon: = {Typ = "CL" Txt = "Player weapon" items = """
                    for item in weapons_items:
                        Weapons = Weapons + item

                    Weapons = Weapons + """ values = """
                    for value in weapons_values:
                        Weapons = Weapons + value
                    Weapons = Weapons + """ Hint="List of available weapons for this model."$0D"Click on one to play with components scquence."}"""

            AnimationCFG_dialog_plugin = UseAnimationCFG()

        Component = ""
        Component = Component + """Help = "These are the Specific settings for a Tag."$0D"""
        if o.dictspec.has_key("Component"):
            Component = Component + """$0D22 "component"$22" - The main component this"$0D"          tag belongs to. (read only)" Component: = {Typ="E R" Txt="component" Hint="The main component that this"$0D"tag belongs to. (read only)"}"""

        group = o.name.split("_")[0]
        TagList = ""
        TagList = TagList + """sep: = { Typ="S" Txt="" } sep: = { Typ="S" Txt="Tags" }"""
        tag_names = [o.name]
        tag_items = []
        tag_values = []
        for item in editor.Root.dictitems['Misc:mg'].subitems:
            if item.type == ":tag" and item.name.startswith(group):
                if not item.name in tag_names:
                    tag_names = tag_names + [item.name]
                if item.name == o.name:
                    continue
                tag_items = tag_items + ['"' + item.shortname + '"' + "$0D"]
                tag_values = tag_values + ['"' + item.name + '"' + "$0D"]

        if len(tag_items) != 0:
            TagList = TagList + """tag_list: = {Typ = "CL" Txt = "Tags list" items = """
            for item in tag_items:
                TagList = TagList + item 

            TagList = TagList + """ values = """
            for value in tag_values:
                TagList = TagList + value 

            TagList = TagList + """ Hint="List of other tags for this group."$0D"Click on one to jump to that tag."}"""

        comp_names = []
        comp_items = []
        comp_values = []
        for item in editor.Root.subitems:
            if item.type == ":mc" and item.name.startswith(group):
                comp_names = comp_names + [item.name]
                comp_items = comp_items + ['"' + item.shortname + '"' + "$0D"]
                comp_values = comp_values + ['"' + item.name + '"' + "$0D"]

        TagList = TagList + """comp_tag_list: = {Typ = "CL" Txt = "Comps list:" items = """
        for item in comp_items:
            TagList = TagList + item 

        TagList = TagList + """ values = """
        for value in comp_values:
            TagList = TagList + value 

        TagList = TagList + """ Hint="List of tag components for this group."$0D"Click on one to jump to that component."}"""

        dlgdef = """
        {
          """ + Component + """
          """ + TagList + """
          """ + AnimationCFG_dialog_plugin + """
          """ + PlayList1 + """
          """ + PlayList2 + """
          """ + Weapons + """
        }
        """
        if o.dictspec.has_key("animationCFG"):
            if o.dictspec.has_key("play_list1"):
                for value in list_values:
                    if value[0] == o.dictspec['play_list1'].split(",")[0]:
                        o['play_list1'] = value[0]+","+value[1]+","+value[2]+","+value[3]+","+value[4]+","+max_BOTH+","+max_TORSO
                        o['first_frame1'] = value[1]
                        o['num_frames1'] = value[2]
                        o['looping_frames1'] = value[3]
                        o['CFG_FPS1'] = value[4]
                        break
            else:
                value = list_values[0]
                o['play_list1'] = value[0]+","+value[1]+","+value[2]+","+value[3]+","+value[4]+","+max_BOTH+","+max_TORSO
                o['first_frame1'] = value[1]
                o['num_frames1'] = value[2]
                o['looping_frames1'] = value[3]
                o['CFG_FPS1'] = value[4]
            if o.dictspec.has_key("play_list2"):
                for value in list_values:
                    if value[0] == o.dictspec['play_list2'].split(",")[0]:
                        o['play_list2'] = value[0]+","+value[1]+","+value[2]+","+value[3]+","+value[4]
                        o['first_frame2'] = value[1]
                        o['num_frames2'] = value[2]
                        o['looping_frames2'] = value[3]
                        o['CFG_FPS2'] = value[4]
                        break
            else:
                for value in list_values:
                    if value[0].startswith("LEGS_"):
                        o['play_list2'] = value[0]+","+value[1]+","+value[2]+","+value[3]+","+value[4]
                        o['first_frame2'] = value[1]
                        o['num_frames2'] = value[2]
                        o['looping_frames2'] = value[3]
                        o['CFG_FPS2'] = value[4]
                        break

            if not o.dictspec.has_key('CFG_lines'):
                if quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"] is not None:
                    o['CFG_lines'] = quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"]
                else:
                    o['CFG_lines'] = "8"
                    quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"] = o.dictspec['CFG_lines']
            else:
                quarkx.setupsubset(SS_MODEL, "Options")["NbrOfCFGLines"] = o.dictspec['CFG_lines']

        if o.dictspec.has_key("tag_list"):
            if len(tag_names) > 1 and not o.dictspec['tag_list'] in tag_names: # In case one of them gets renamed.
                o['tag_list'] = tagnames[1]
            if not o.dictspec.has_key("None"):
                editor.layout.explorer.sellist = [editor.Root.dictitems['Misc:mg'].dictitems[o.dictspec['tag_list']]]
                editor.layout.explorer.expand(editor.Root.dictitems['Misc:mg'])
                o['tag_list'] = ""

        if o.dictspec.has_key("comp_tag_list"):
            if len(comp_names) > 1 and not o.dictspec['comp_tag_list'] in comp_names: # In case one of them gets renamed.
                o['comp_tag_list'] = comp_names[0]
            if not o.dictspec.has_key("None"):
                editor.layout.explorer.sellist = [editor.Root.dictitems[o.dictspec['comp_tag_list']]]
                o['comp_tag_list'] = ""

        formobj = quarkx.newobj("tagframe:form")
        formobj.loadtext(dlgdef)

        if MdlOption("AnimationCFGActive"):
            import mdlanimation
            from mdlanimation import playNR, playlist
            mdlanimation.playNR = 0
            mdlanimation.playlist = [o]
            mdlanimation.UpdateplaylistPerComp(None)

        return formobj


# Has no subitems or dictitems items, only dictspec items (origin and rotmatrix).
class TagFrameType(EntityManager):
    "Tag Frame, type = :tagframe"

    def handlesopt(o, editor):

        h = []
        if not o.parent.dictspec.has_key("show"):
            o.parent['show'] = (1.0,)
        if o.parent.dictspec['show'][0] != 1.0:
            return h
        comp = editor.Root.currentcomponent

        # In case there are tags but all components have been deleted,
        # we need to remove the tags as well.
        # If neither then just clear the selections lists and return.
        if allowitems(editor) == 0:
            if len(editor.Root.dictitems['Misc:mg'].findallsubitems("", ':tag')) == 0:
                editor.layout.explorer.sellist = []
                editor.layout.explorer.uniquesel = None
                return h
            o = None
            clearMiscGroup(editor, "no components - tags cleared")
            return h

        if quarkx.setupsubset(SS_MODEL, "Options")['HideTags'] is not None or comp is None:
            return h

        h = [mdlhandles.TagHandle(quarkx.vect(o.dictspec['origin']), o)]
        h[0].hint = o.parent.shortname + " " + o.shortname
        return h

    def dataformname(o):
        "Returns the data form for this type of object 'o' (a Tag Frame) to use for the Specific/Args page."

        dlgdef = """
        {
          Help = "These are the Specific settings for a Tag Frame."$0D0D22
                 "origin"$22" - You must enter three values here."$0D
                 "          They have an accuracy of two digits."
          origin: = {
              Typ="EF003" 
              Txt="origin"
              Hint="You must enter three values here."$0D"They have an accuracy of two digits."
                 }
        }
        """

        formobj = quarkx.newobj("tagframe:form")
        formobj.loadtext(dlgdef)
        return formobj


class BoneType(EntityManager):
    "Bone, type = :bone"

    def menu(o, editor):
        import qmenu
        STB = qmenu.item("&Show these bones", ShowTheseBones)
        HTB = qmenu.item("&Hide these bones", HideTheseBones)

        if o.dictspec['show'][0] == 1.0:
            STB.state = qmenu.disabled
        else:
            HTB.state = qmenu.disabled

        import mdlmenus
        return [STB, HTB, qmenu.sep] + CallManager("menubegin", o, editor) + mdlmenus.BaseMenu([o], editor)

    def handlesopt(o, editor):

        h = []
        if o.dictspec['show'][0] != 1.0:
            return h
        comp = editor.Root.currentcomponent
        s = None
        index = ""

        # In case there are bones but all components have been deleted,
        # we need to remove the bones as well.
        # If neither then just clear the selections lists and return.
        if allowitems(editor) == 0:
            if len(editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone')) == 0:
                editor.layout.explorer.sellist = []
                editor.layout.explorer.uniquesel = None
                return h
            o = None
            clearbones(editor, "no components - bones cleared")
            return h

        if quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is not None or comp is None:
            return h

        # Checks that at least the needed frame count for a component is there to avoid vertex selection error later on.
        try:
            frame = editor.Root.dictitems[o.dictspec['component']].dictitems['Frames:fg'].subitems[editor.bone_frame]
        except:
            try:
                frame = editor.Root.dictitems[o.dictspec['component']].dictitems['Frames:fg'].subitems[0]
                editor.bone_frame = 0
            except:
                frame = editor.layout.explorer.sellist = [comp.dictitems['Frames:fg'].subitems[0]]
                editor.bone_frame = 0
                quarkx.msgbox("FRAME COUNT ERROR !\n\nNot all components using these bones\nhave the same number of frames.\n\nCorrect and try again.", qutils.MT_ERROR, qutils.MB_OK)
                return h

        Rebuild_Bone(editor, o, frame)

        bbox = (o.position - quarkx.vect(1.0, 1.0, 1.0)*o.dictspec['scale'][0], o.position + quarkx.vect(1.0, 1.0, 1.0)*o.dictspec['scale'][0])
        manager = mdlhandles.ModelEditorBoneHandlesManager(editor, o.getint('_color'), bbox, o)
        handles = manager.BuildHandles(o.position)

        for s in handles:
            if s is None:
                continue
            if isinstance(s, mdlhandles.BoneCenterHandle):
                if MapOption("HandleHints", SS_MODEL):
                    s.hint = "       Center of %s"%o.shortname
            if isinstance(s, mdlhandles.BoneCornerHandle):
                if MapOption("HandleHints", SS_MODEL):
                    s.hint = "       Rotate for %s"%o.shortname
            h = h + [s]
        return h

    def dataformname(o):
        "Returns the data form for this type of object 'o' (a bone) to use for the Specific/Args page."

        # Next line calls for the Vertex Weights Specifics Module in mdlentities.py to be used.
        vertex_weights_specifics_plugin = UseVertexWeightsSpecifics()

        import mdleditor
        editor = mdleditor.mdleditor
        comp = editor.Root.currentcomponent.name
        if not comp in o.vtxlist.keys():
            items = ['"0 - ' + comp.replace(":mc","") + '"' + "$0D"]
            values = ['"' + comp + '"' + "$0D"]
        else:
            items = []
            values = []

        keys = o.vtxlist.keys()
        keys.sort()
        for comp in keys:
            items = items + ['"' + str(len(o.vtxlist[comp])) + " - " + comp.replace(":mc","") + '"' + "$0D"]
            values = values + ['"' + comp + '"' + "$0D"]

        SpecsList = """comp_list: = {Typ="C" Txt="comp list" items = """

        for item in items:
            SpecsList = SpecsList + item 

        SpecsList = SpecsList + """ values = """

        for value in values:
            SpecsList = SpecsList + value

        SpecsList = SpecsList + """ Hint="List of components and number of"$0D"their vertexes assigned to this bone."$0D"If the current component does not use this bone"$0D"then 'None' will be displayed as the default item."}"""

        bonelist = 'Sep: = {Typ = "S"   Txt = ""}'
        bone_control = """ """
        for item in editor.layout.explorer.sellist:
            if item.type == ":bone":
                bone = item
                bonelist = bonelist + bone.shortname + '_weight_value: = { Txt = "' + bone.shortname + ' weight value:"  Typ = "EU" Hint = "Set this vertex' + "'" + 's weight here."$0D"Total values for this vertex MUST = 1.0"}' + bone.shortname + '_weight_color: = { Typ = "LI" Txt = "' + bone.shortname + ' weight color" Hint = "Color used for this component' + "'" + 's vertex weight color mapping."$0D"You can not change this color, use button above."}'
                keys = bone.dictspec.keys()
                control = 0
                for key in keys:
                    if key.startswith("control_"):
                        bone_control = 'Sep: = {Typ = "S"   Txt = ""} Sep: = {Typ="S" Txt="Bone Control Settings" Hint="Used in some games player models"$0D"such as Half-Life 1 and 2 where"$0D"index 0-3 = bone controls, index 4 = mouth."}'
                        control = 1
                        break
                if control == 1:
                    for key in keys:
                        if key == "control_index":
                            bone_control = bone_control + 'control_index: = {Typ="E" Txt="index" Hint="Which control this one is."$0D"Half-Life 1 & 2 allows up to 5."$0D"index 0-3 = bone controls, index 4 = mouth."}'
                            break
                    for key in keys:
                        if key == "control_type":
                            bone_control = bone_control + 'control_type: = {Typ="CL" Txt="type" Hint="Default setting usually XRotation." items="1 = X"$0D"2 = Y"$0D"4 = Z"$0D"8 = XRotation"$0D"16 = YRotation"$0D"32 = ZRotation"$0D"64 = Mouth" values="1"$0D"2"$0D"4"$0D"8"$0D"16"$0D"32"$0D"64"}'
                            break
                    for key in keys:
                        if key == "control_start":
                            bone_control = bone_control + 'control_start: = {Typ="EU" Txt="start" Hint="Default setting usually -30."}'
                            break
                    for key in keys:
                        if key == "control_rest":
                            bone_control = bone_control + 'control_rest: = {Typ="EU" Txt="rest" Hint="Default setting usually 0."}'
                            break
                    for key in keys:
                        if key == "control_end":
                            bone_control = bone_control + 'control_end: = {Typ="EU" Txt="end" Hint="Default setting usually 30."}'
                            break

        dlgdef = """
        {
          Help = "These are the Specific settings for a Bone."$0D0D22
                 "classname"$22" - The name of the bone"$0D
                 "                           currently selected for setting."$0D22
                 "bone length"$22" - You must enter three values here,"$0D
                 "                              they have an accuracy of two digits."$0D22
                 "comp list"$22" - List of components and number of"$0D
                 "                        their vertexes assigned to this bone."$0D22
                 "auto expand"$22" - When checked, opens the 'Frames'"$0D
                 "                         folder, if closed, when the component"$0D
                 "                         in the 'comp list' is clicked on,"$0D
                 "                         each bone is set separately."$0D22
                 "parent"$22" - The handle name that this"$0D
                 "                    one is attached to, if any."$0D22
                 "color"$22" - Color to use for this bone handle's vertex group,"$0D
                 "                  click the color button to select a color."$0D22
                 "position"$22" - You must enter three values here,"$0D
                 "                      they have an accuracy of two digits."$0D22
                 "offset"$22" -   You must enter three values here,"$0D
                 "                     they have an accuracy of two digits,"$0D
                 "                     not all models use this."$0D22
                 "scale"$22" - You must enter one positive float value here,"$0D
                 "                   they have an accuracy of two digits,"$0D
                 "                   larger value = bigger handle size,"$0D
                 "                   smaller value = smaller handle size,"$0D
                 "                   the default value for normal size = 1.00"$0D22
                 "show weight colors"$22" - When checked, if component has vertex weight coloring they will show."$0D
                 "          If NOT checked and it has bones with vetexes, those will show."
          bone_length: = 
            {
              Typ="EF003" 
              Txt="Bone Length"
              Hint="You must enter three values here."$0D
                   "They have an accuracy of two digits."
            }
          sep: = { Typ="S" Txt="" }
          """ + SpecsList + """
          frame_autoexpand: = 
            {
              Typ="X1" 
              Txt="auto expand"
              Hint="When checked, opens the 'Frames'"$0D
                   "folder, if closed, when the component"$0D
                   "in the 'comp list' is clicked on,"$0D
                   "each bone is set separately."
            }
          parent_name: = 
            {
              Typ="E R"
              Txt="parent"
              Hint="The handle name that this"$0D
                   "one is attached to, if any."
            }
          _color: = 
            {
              Typ="LI"
              Txt="color"
              Hint="Color to use for this bone handle's vertex group color."$0D
                   "Click this color button to select a color."
            }
          position: = 
            {
              Typ="EF003" 
              Txt="position"
              Hint="You must enter three values here."$0D"They have an accuracy of two digits."
            }
          draw_offset: = 
            {
              Typ="EF003" 
              Txt="offset"
              Hint="You must enter three values here."$0D"They have an accuracy of two digits."$0D
                   "Not all models use this."
            }
          scale: = 
            {
              Typ="EF001" 
              Txt="scale"
              Hint="You must enter one positive float value here."$0D
                   "It has an accuracy of two digits."$0D"Larger value = bigger handle size."$0D
                   "Smaller value = smaller handle size."$0D
                   "The default value for normal size = 1.00"
            }
          """ + vertex_weights_specifics_plugin + """
          """ + bonelist + """
          """ + bone_control + """
        }
        """

        if not o.dictspec.has_key("comp_list"):
            o['comp_list'] = editor.Root.currentcomponent.name

        skeletongroup = editor.Root.dictitems['Skeleton:bg']  # get the bones group
        bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
        for item in editor.layout.explorer.sellist:
            if item.type == ":bone":
                for bone in bones:
                    if bone.name == item.name:
                        if not bone.dictspec.has_key(bone.shortname + "_weight_value"):
                            o[bone.shortname + "_weight_value"] = "1.0"
                            if bone.name != o.name:
                                bone[bone.shortname + "_weight_value"] = "1.0"
                            weights_color(editor, 1.0)
                            o[bone.shortname + "_weight_color"] = MapColor("temp_color", SS_MODEL) # A long integer, used to display the color in the color picker.
                            if bone.name != o.name:
                                bone[bone.shortname + "_weight_color"] = MapColor("temp_color", SS_MODEL)
                        else:
                            if bone.name == o.name:
                                continue
                            if not o.dictspec.has_key(bone.shortname + "_weight_value"):
                                o[bone.shortname + "_weight_value"] = bone.dictspec[bone.shortname + "_weight_value"]
                                o[bone.shortname + "_weight_color"] = bone.dictspec[bone.shortname + "_weight_color"]
                        break

        ico_mdlskv = ico_dict['ico_mdlskv']  # Just to shorten our call later.
        icon_btns = {}                       # Setup our button list, as a dictionary list, to return at the end.
        icon_btns = UseVertexPaintSystem(editor, icon_btns)
        # Next line calls for the Vertex Weights system in mdlentities.py to be used.
        vtxweightsbtn = qtoolbar.button(UseVertexWeights, "Open or Update\nVertex Weights Dialog||When clicked, this button opens the dialog to allow the 'weight' movement setting of single vertexes that have been assigned to more then one bone handle.\n\nClick the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
        vtxweightsbtn.state = qtoolbar.normal
        vtxweightsbtn.caption = "" # Texts shows next to button and keeps the width of this button so it doesn't change.
        icon_btns['vtxweights'] = vtxweightsbtn   # Put our button in the above list to return.

        if o['frame_autoexpand'] is None:
            o['frame_autoexpand'] = "1"

        formobj = quarkx.newobj("bone:form")
        formobj.loadtext(dlgdef)
        return formobj, icon_btns

    def dataforminput(o):
        "Returns the default settings or input data for this type of object 'o' (a bone) to use for the Specific/Args page."

        editor = mdleditor.mdleditor # Get the editor.
        if not o.dictspec.has_key("comp_list"):
            o['comp_list'] = editor.Root.currentcomponent.name

        skeletongroup = editor.Root.dictitems['Skeleton:bg']  # get the bones group
        bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
        for item in o.dictspec:
            if item.endswith("_weight_value"):
                itemname = item.replace('_weight_value', '')
                value = float(o.dictspec[item])
                if value >= 2:
                    value = 1.0
                elif value > 1:
                    value = round(value,2) - 0.95
                elif value == 0:
                    value = 0.95
                elif value == -1.0 or value == -0.95:
                    value = 0.05
                elif value < 0:
                    value = round(value,2) + 0.95
                # Needed for hand entered amounts to keep value valid.
                if value > 1:
                    value = 1.0
                elif value < 0.01:
                    value = 0.01
                o[itemname + "_weight_value"] = str(value)
                weights_color(editor, value)
                o[itemname + "_weight_color"] = MapColor("temp_color", SS_MODEL) # A long integer, used to display the color in the color picker.
                if itemname != o.shortname:
                    for bone in bones:
                        if bone.shortname == itemname:
                            bone[itemname + "_weight_value"] =  o.dictspec[itemname + "_weight_value"]
                            bone[itemname + "_weight_color"] =  o.dictspec[itemname + "_weight_color"]


class ComponentType(EntityManager):
    "Model Component, type = :mc"

    def menu(o, editor):
        import qmenu
        SC1 = qmenu.item("&Show Component", ShowComp)
        HC1 = qmenu.item("&Hide Component", HideComp)

        if len(o.triangles) == 0:
            HC1.state = qmenu.disabled
        else:
            SC1.state = qmenu.disabled

        import mdlmenus
        return [SC1, HC1, qmenu.sep] + CallManager("menubegin", o, editor) + mdlmenus.BaseMenu([o], editor)
 
    def handles(o, editor, view):
        "A Model's COMPONENT currentframe 'frame' MESH, each animation Frame has its own."
        frame = o.currentframe
        if frame is None:
            return []
        else:
            return CallManager("handles", frame, editor, view)

    def handlesopt(o, editor):
        "A Model's COMPONENT currentframe 'frame' MESH, each animation Frame has its own."
        if o.type != ':mf':
            return []
        else:
            frame = o
            return CallManager("handlesopt", frame, editor)

    def dataformname(o):
        "Returns the data form for this type of object 'o' (a model component) to use for the Specific/Args page."

        editor = mdleditor.mdleditor # Get the editor.
        BoneControls = """ """
        keys = o.dictspec.keys()
        controls = 0
        for key in keys:
            if key.startswith("bone_control_"):
                BoneControls = BoneControls + 'sep: = { Typ="S" Txt="" } sep: = { Typ="S" Txt="Bone Controls" }'
                controls = 1
                break
        if controls == 1:
            keys.sort()
            for key in keys:
                if key.startswith("bone_control_"):
                    bone_name = o.dictspec[key]
                    if bone_name.endswith("_select"):
                        o[key] = bone_name.split("_select")[0]
                        folder_name = o.name.split("_")[0]
                        bones = []
                        for bone in o.parent.dictitems['Skeleton:bg'].subitems:
                            if bone.name.startswith(folder_name + "_"):
                                bones = bones + bone.findallsubitems("", ':bone')    # get all bones
                        for bone in bones:
                            editor.layout.explorer.expand(bone.parent)
                            if bone.name == o[key]:
                                editor.layout.explorer.sellist = [bone]
                                editor.layout.selchange()
                                break
                                
                    nbr = key.split("_")[2]
                    bone_name = o.dictspec[key].split(":")
                    BoneControls = BoneControls + 'bone_control_' + nbr + ': = {Typ = "CL"  Txt = "&"  items = "' + bone_name[0] + '"$0D"select bone"'
                    BoneControls = BoneControls + ' values = "' + o.dictspec[key] + '"$0D"' + o.dictspec[key] + '_select"'
                    BoneControls = BoneControls + 'Hint = "Select bone for this control."$0D"Select this bone in Skeleton folder"$0D"to change its control settings."}'

        TagList = ""
        if o.dictspec.has_key("Tags") or o.dictspec.has_key("tag_components"):
            TagList = TagList + """sep: = { Typ="S" Txt="" } sep: = { Typ="S" Txt="Tags" }"""
            if o.dictspec.has_key("Tags"):
                items = []
                values = []
                tags = o.dictspec['Tags'].split(", ")
                alltags = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':tag')   # get all frames
                for t in alltags:
                    group = t.shortname.split("tag_")[0]
                    if o.name.startswith(group):
                        break
                for tag in tags:
                    items = items + ['"' + tag + '"' + "$0D"]
                    tag_name = group + tag + ":tag"
                    values = values + ['"' + tag_name + '"' + "$0D"]

                TagList = TagList + """tag_list: = {Typ = "CL" Txt = "Tags list" items = """
                for item in items:
                    TagList = TagList + item 

                TagList = TagList + """ values = """
                for value in values:
                    TagList = TagList + value 

                TagList = TagList + """ Hint="List of tags for this component."$0D"Click on one to jump to that tag."}"""

            if o.dictspec.has_key("tag_components"):
                items = []
                values = []
                comps = o.dictspec['tag_components'].split(", ")
                for comp in comps:
                    if comp == o.name:
                        continue
                    comp_name = comp.split(":mc")[0]
                    items = items + ['"' + comp_name + '"' + "$0D"]
                    values = values + ['"' + comp + '"' + "$0D"]

                if len(items) != 0:
                    TagList = TagList + """comp_tag_list: = {Typ = "CL" Txt = "Comps list:" items = """
                    for item in items:
                        TagList = TagList + item 

                    TagList = TagList + """ values = """
                    for value in values:
                        TagList = TagList + value 

                    TagList = TagList + """ Hint="List of tag components for this component."$0D"Click on one to jump to that component."}"""

        dlgdef = """
        {
          Help = "These are the Specific settings for a Model Component."$0D0D22
                 "skins"$22" - Number of skins of this component."$0D0D22
                 "frames"$22" - Number of frames of this component."$0D0D22
                 "triangles"$22" - Number of triangle faces of this component."$0D0D22
                 "vertices"$22" - Number of vertices of this component."$0D0D22
                 "comp color 1"$22" - Color to use for this component's tint"$0D
                 "color in texture or solid mode or line color in wire mode."$0D
                 "                        Click the selector button to pick a color."$0D0D22
                 "comp color 2"$22" - Color to use for this component's mesh"$0D
                 "color in texture or solid mode if 'use color 2' is checked."$0D
                 "                        Click the selector button to pick a color."$0D0D22
                 "use color 2"$22" - When checked, this color draws the"$0D
                 "component's mesh lines in textured or solid view mode."$0D0D
                 "When a views RMB menu item 'Use Component Colors'"$0D
                 "is checked these become active"$0D
                 "and override all other settings."$0D0D
                 " If the component is selected all meshes display their own"$0D
                 "mesh line color in wire frame views and a Tint of that"$0D
                 "color over their textured and solid views which can also"$0D
                 "display their mesh lines in a second color when a views"$0D
                 "'Mesh in Frames' option is checked on the 'Views Options' dialog."
          skins_count: = 
            {
              Typ="E R"
              Txt="skins"
              Hint="Number of skins of this component."
            }
          frames_count: = 
            {
              Typ="E R"
              Txt="frames"
              Hint="Number of frames of this component."
            }
          tri_count: = 
            {
              Typ="E R"
              Txt="triangles"
              Hint="Number of triangle faces of this component."
            }
          vtx_count: = 
            {
              Typ="E R"
              Txt="vertices"
              Hint="Number of vertices of this component."
            }
          comp_color1: = {
              Typ="LI"
              Txt="comp color 1"
              Hint="Color to use for this component's tint"$0D
              "color in texture or solid mode and line color in wire mode."$0D
              "Click the color selector button to pick a color."
                 }
          comp_color2: = {Typ="LI"
              Txt="comp color 2"
              Hint="Color to use for this component's mesh"$0D
              "color in texture or solid mode if 'use color 2' is checked."$0D
              "Click the color selector button to pick a color."
                 }
          usecolor2: = {
              Typ="X1" 
              Txt="use color 2"
              Hint="When checked, this color draws the"$0D
              "component's mesh lines in textured or solid view mode."
                 }
          """ + TagList + """
          """ + BoneControls + """
        }
        """

        o['tri_count'] = str(len(o.triangles))
        if o.dictitems.has_key('Skins:sg') and len(o.dictitems['Skins:sg'].subitems) != 0:
            o['skins_count'] = str(len(o.dictitems['Skins:sg'].subitems))
        else:
            o['skins_count'] = "0"
        if o.dictitems.has_key('Frames:fg') and len(o.dictitems['Frames:fg'].subitems) != 0:
            o['frames_count'] = str(len(o.dictitems['Frames:fg'].subitems))
        else:
            o['frames_count'] = "0"
        if o.dictitems.has_key('Frames:fg') and len(o.dictitems['Frames:fg'].subitems) != 0:
            o['vtx_count'] = str(len(o.dictitems['Frames:fg'].subitems[0].vertices))
        else:
            o['vtx_count'] = "0"

        if o.dictspec.has_key("Tags") or o.dictspec.has_key("tag_components"):
            if o.dictspec.has_key("Tags"):
                tagnames = o.dictspec['Tags'].split(", ")
                tag_name = group + tag + ":tag"
                if o.dictspec.has_key("tag_list"):
                    if not (o.dictspec['tag_list'].replace(group, "")).replace(":tag", "") in tagnames: # In case one of them gets renamed.
                        tag_name = group + tagnames[0] + ":tag"
                        o['tag_list'] = tag_name
                    if not o.dictspec.has_key("None"):
                        editor.layout.explorer.sellist = [editor.Root.dictitems['Misc:mg'].dictitems[o.dictspec['tag_list']]]
                        editor.layout.explorer.expand(editor.Root.dictitems['Misc:mg'])
                        o['tag_list'] = ""
                    
                    
            if o.dictspec.has_key("tag_components"):
                comp_names = o.dictspec['tag_components'].split(", ")
                if o.dictspec.has_key("comp_tag_list"):
                    if not o.dictspec['comp_tag_list'] in comp_names: # In case one of them gets renamed.
                        o['comp_tag_list'] = o.name
                    if not o.dictspec.has_key("None"):
                        editor.layout.explorer.sellist = [editor.Root.dictitems[o.dictspec['comp_tag_list']]]
                        o['comp_tag_list'] = ""
        # Cleans these items out of the component when they should not be there, to keep them from showing up incorrectly.
            if not o.dictspec.has_key("Tags") and o.dictspec.has_key("tag_list"):
                o['tag_list'] = ""
            if not o.dictspec.has_key("tag_components") and o.dictspec.has_key("comp_tag_list"):
                o['comp_tag_list'] = ""

        formobj = quarkx.newobj("mc:form")
        formobj.loadtext(dlgdef)
        return formobj


class SkinGroupType(EntityManager):
    "Model Skin Group, type = :sg"

    def dataformname(o):
        "Returns the data form for this type of object 'o' (the Skins:sg folder) to use for the Specific/Args page."

        skin_group_dlgdef = """
        {
          Help = "These are the Specific settings for the Skins group."$0D0D22
                 "import skin"$22" - Select a skin texture image file"$0D
                 "                    to import and add to this group."$0D
                 "                    Will not add a skin with duplicate names."
          skin_name: = {t_ModelEditor_texturebrowser = ! Txt="import skin"    Hint="Select a skin texture image file"$0D"to import and add to this group."$0D"Will not add a skin with duplicate names."}
        }
        """

        import mdleditor
        editor = mdleditor.mdleditor # Get the editor.
        if (o.dictspec.has_key("skin_name")) and (not o.dictspec['skin_name'] in o.parent.dictitems['Skins:sg'].dictitems.keys()):
            # Gives the newly selected skin texture's game folders path and file name, for example:
            #     models/monsters/cacodemon/cacoeye.tga
            skinname = o.dictspec['skin_name']
            skin = quarkx.newobj(skinname)
            # Gives the full current work directory (cwd) path up to the file name, need to add "\\" + filename, for example:
            #     E:\Program Files\Doom 3\base\models\monsters\cacodemon
            import os
            cur_folder = os.getcwd()
            # Gives just the actual file name, for example: cacoeye.tga
            tex_file = skinname.split("/")[-1]
            # Puts the full path and file name together to get the file, for example:
            # E:\Program Files\Doom 3\base\models\monsters\cacodemon\cacoeye.tga
            file = cur_folder + "\\" + tex_file
            image = quarkx.openfileobj(file)
            skin['Image1'] = image.dictspec['Image1']
            skin['Size'] = image.dictspec['Size']
            skingroup = o.parent.dictitems['Skins:sg']
            o['skin_name'] = ""
            undo = quarkx.action()
            undo.put(skingroup, skin)
            editor.ok(undo, o.parent.shortname + " - " + "new skin added")
            editor.Root.currentcomponent.currentskin = skin
            editor.layout.explorer.sellist = [editor.Root.currentcomponent.currentskin]
            import mdlutils
            mdlutils.Update_Skin_View(editor, 2) # The 2 argument resets the Skin-view to the new skin's size and centers it.
        else:
            if o.dictspec.has_key("skin_name"):
                o['skin_name'] = ""

        formobj = quarkx.newobj("sg:form")
        formobj.loadtext(skin_group_dlgdef)
        return formobj


class BBoxGroupType(EntityManager):
    "Model BBox Sub-group in the 'Misc:mg' folder for bounding poly boxes, type = :bbg"

    def menu(o, editor):
        import qmenu, mdlmenus
        STBB = qmenu.item("&Show these bboxes", ShowTheseBBoxes, "|Show these bboxes:\n\nThis allows the selected bboxes to be displayed in the editor's views if the function 'Draw Bounding Boxes' is not active.|intro.modeleditor.editelements.html#tags")
        HTBB = qmenu.item("&Hide these bboxes", HideTheseBBoxes, "|Hide these bboxes:\n\nThis stops the selected bboxes from being displayed in the editor's views.|intro.modeleditor.editelements.html#tags")

        if not o.dictspec.has_key("show"):
            o['show'] = (1.0,)
        if o.dictspec['show'][0] == 1.0:
            STBB.state = qmenu.disabled
        else:
            HTBB.state = qmenu.disabled
        return [STBB, HTBB, qmenu.sep] + CallManager("menubegin", o, editor) + mdlmenus.BaseMenu([o], editor)

class SkinSubGroupType(EntityManager):
    "Model Skin Group Sub-group for skins (like an animation set of skins), type = :ssg"

    def dataformname(o):
        "Returns the data form for this type of object 'o' (the SkinsSubGroup:ssg folder) to use for the Specific/Args page."

        skin_group_group_dlgdef = """
        {
          Help = "These are the Specific settings for the Skins sub-group."$0D0D22
                 "import skin"$22" - Select a skin texture image file"$0D
                 "                    to import and add to this group."$0D
                 "                    Will not add a skin with duplicate names."
          skin_name: = {t_ModelEditor_texturebrowser = ! Txt="import skin"    Hint="Select a skin texture image file"$0D"to import and add to this group."$0D"Will not add a skin with duplicate names."}
        }
        """

        import mdleditor
        editor = mdleditor.mdleditor # Get the editor.
        if (o.dictspec.has_key("skin_name")) and (not o.dictspec['skin_name'] in o.dictitems.keys()):
            # Gives the newly selected skin texture's game folders path and file name, for example:
            #     models/monsters/cacodemon/cacoeye.tga
            skinname = o.dictspec['skin_name']
            skin = quarkx.newobj(skinname)
            # Gives the full current work directory (cwd) path up to the file name, need to add "\\" + filename, for example:
            #     E:\Program Files\Doom 3\base\models\monsters\cacodemon
            import os
            cur_folder = os.getcwd()
            # Gives just the actual file name, for example: cacoeye.tga
            tex_file = skinname.split("/")[-1]
            # Puts the full path and file name together to get the file, for example:
            # E:\Program Files\Doom 3\base\models\monsters\cacodemon\cacoeye.tga
            file = cur_folder + "\\" + tex_file
            image = quarkx.openfileobj(file)
            skin['Image1'] = image.dictspec['Image1']
            skin['Size'] = image.dictspec['Size']
            skingroup = o
            o['skin_name'] = ""
            undo = quarkx.action()
            undo.put(skingroup, skin)
            editor.ok(undo, o.shortname + " - " + "new skin added")
            editor.Root.currentcomponent.currentskin = skin
            editor.layout.explorer.sellist = [editor.Root.currentcomponent.currentskin]
            import mdlutils
            mdlutils.Update_Skin_View(editor, 2) # The 2 argument resets the Skin-view to the new skin's size and centers it.
        else:
            if o.dictspec.has_key("skin_name"):
                o['skin_name'] = ""

        formobj = quarkx.newobj("sgg:form")
        formobj.loadtext(skin_group_group_dlgdef)
        return formobj


class SkinType(EntityManager):
    "Model Skin, types = .pcx, .tga, .dds, .png, .jpg, .bmp, .ftx, .vtf, .m8"

    def dataformname(o):
        "Returns the data form for this type of object 'o' (a model's skin texture) to use for the Specific/Args page."

        def_skin_dlgdef = """
        {
          Help = "These are the Specific default settings for a model's skins."$0D0D22
                 "skin name"$22" - The currently selected skin texture name."$0D22
                 "edit skin"$22" - Opens this skin texture in an external editor."
          skin_name:      = {t_ModelEditor_texturebrowser = ! Txt="skin name"    Hint="The currently selected skin texture name."}
          edit_skin:      = {
                             Typ = "P"
                             Txt = "edit skin ---->"
                             Macro = "opentexteditor"
                             Hint = "Opens this skin texture"$0D"in an external editor."
                             Cap = "edit skin"
                            }
        }
        """

        import mdleditor
        editor = mdleditor.mdleditor # Get the editor.
        if o.name == editor.Root.currentcomponent.currentskin.name: # If this is not done it will cause looping through multiple times.
            if (o.parent.parent.dictspec.has_key("skin_name")) and (o.parent.parent.dictspec['skin_name'] != o.name) and (not o.parent.parent.dictspec['skin_name'] in o.parent.parent.dictitems['Skins:sg'].dictitems.keys()):
                # Gives the newly selected skin texture's game folders path and file name, for example:
                #     models/monsters/cacodemon/cacoeye.tga
                skinname = o.parent.parent.dictspec['skin_name']
                skin = quarkx.newobj(skinname)
                # Gives the full current work directory (cwd) path up to the file name, need to add "\\" + filename, for example:
                #     E:\Program Files\Doom 3\base\models\monsters\cacodemon
                import os
                cur_folder = os.getcwd()
                # Gives just the actual file name, for example: cacoeye.tga
                tex_file = skinname.split("/")[-1]
                # Puts the full path and file name together to get the file, for example:
                # E:\Program Files\Doom 3\base\models\monsters\cacodemon\cacoeye.tga
                file = cur_folder + "\\" + tex_file
                image = quarkx.openfileobj(file)
                skin['Image1'] = image.dictspec['Image1']
                skin['Size'] = image.dictspec['Size']
                skingroup = o.parent.parent.dictitems['Skins:sg']
                undo = quarkx.action()
                undo.put(skingroup, skin)
                editor.ok(undo, o.parent.parent.shortname + " - " + "new skin added")
                editor.Root.currentcomponent.currentskin = skin
                editor.layout.explorer.sellist = [editor.Root.currentcomponent.currentskin]
                import mdlutils
                mdlutils.Update_Skin_View(editor, 2) # The 2 argument resets the Skin-view to the new skin's size and centers it.

        DummyItem = o
        while (DummyItem.type != ":mc"): # Gets the object's model component.
            DummyItem = DummyItem.parent
        if DummyItem.type == ":mc":
            comp = DummyItem
            # This sections handles the data for this model type skin page form.
            # This makes sure what is selected is a model skin, if so it returns the Skin page data to make the form with.
            if len(comp.dictitems['Skins:sg'].subitems) == 0 or o in comp.dictitems['Skins:sg'].subitems:
                formobj = quarkx.newobj("skin:form")
                formobj.loadtext(def_skin_dlgdef)
                return formobj
            for item in comp.dictitems['Skins:sg'].subitems:
                if item.type == ":ssg":
                    if o in item.subitems:
                        formobj = quarkx.newobj("skin:form")
                        formobj.loadtext(def_skin_dlgdef)
                        return formobj
        else:
            return None


    def dataforminput(o):
        "Returns the default settings or input data for this type of object 'o' (a model's skin texture) to use for the Specific/Args page."

        DummyItem = o
        while (DummyItem.type != ":mc"): # Gets the object's model component.
            DummyItem = DummyItem.parent
        if DummyItem.type == ":mc":
            comp = DummyItem
            # This sections handles the data for this model type skin page form.
            # This makes sure what is selected is a model skin, if so it fills the Skin page data and adds the items to the component.
            if len(comp.dictitems['Skins:sg'].subitems) != 0:
               comp['skin_name'] = o.name
            else:
               comp['skin_name'] = "no skins exist"


class FrameGroupType(EntityManager):
    "Model Frame Group, type = :fg"


class FrameType(EntityManager):
    "Model Frame, type = :mf"

    def handlesopt(o, editor):
        vtx = o.vertices
        h = map(mdlhandles.VertexHandle, vtx)
        for i in range(len(h)):
            item = h[i]
            item.frame = o
            item.index = i
            item.name = "Vertex"
            if MapOption("HandleHints", SS_MODEL):
                item.hint = item.name + " %s"%item.index
        return h


class PolyhedronType(EntityManager):
    "A Bounding Box's (BBox) Polyhedron"

    def menu(o, editor):
        import qmenu, mdlmenus
        STBB = qmenu.item("&Show this bbox", ShowTheseBBoxes, "|Show this bbox:\n\nThis allows the selected bbox to be displayed in the editor's views if the function 'Draw Bounding Boxes' is not active.|intro.modeleditor.editelements.html#tags")
        HTBB = qmenu.item("&Hide this bbox", HideTheseBBoxes, "|Hide this bbox:\n\nThis stops the selected bbox from being displayed in the editor's views.|intro.modeleditor.editelements.html#tags")

        if not o.dictspec.has_key("show"):
            o['show'] = (1.0,)
        if o.dictspec['show'][0] == 1.0:
            STBB.state = qmenu.disabled
        else:
            HTBB.state = qmenu.disabled
        return [STBB, HTBB, qmenu.sep] + CallManager("menubegin", o, editor) + mdlmenus.BaseMenu([o], editor)

    def handles(o, editor):
        h = PolyHandles(o, None)
        if h:
            return h
        return []


def PolyHandles(o, exclude):
    "Makes a list of handles for a Bounding Box's (BBox) polyhedron, o is the BBox poly."

    h = []
    if o.dictspec['show'][0] != 1.0:
        return h
    pos = o.origin
    if not (pos is None) and MdlOption("DrawBBoxes"):
        #
        # Vertex handles.
        #
        for v in o.vertices:
            h.append(mdlhandles.PVertexHandle(v, o))
        #
        # Face handles.
        #
        for f in o.faces:
            if f!=exclude:
                #
                # Compute the center of the face.
                #
                vtx = f.verticesof(o)
                center = reduce(lambda x,y: x+y, vtx)/len(vtx)
                #
                # Create the handle at this point.
                #
                h.append(mdlhandles.PFaceHandle(center, f))
        #
        # Finally, add the polyhedron center handle.
        #
        h.append(mdlhandles.PolyHandle(pos, o))

    return h

#
# Mappings between Internal Objects types and Entity Manager classes.
#

Mapping = {
    ":d":        DuplicatorType(),
    ":g":        GroupType(),
    ":p":        PolyhedronType(),
    ":bbg":      BBoxGroupType(),
    ":mr":       ModelRootType(),
    ":mc":       ComponentType(),
    ":mf":       FrameType(),
    ":sg":       SkinGroupType(),
    ":ssg":      SkinSubGroupType(),
    ".pcx":      SkinType(),
    ".tga":      SkinType(),
    ".dds":      SkinType(),
    ".png":      SkinType(),
    ".jpg":      SkinType(),
    ".bmp":      SkinType(),
    ".ftx":      SkinType(),
    ".vtf":      SkinType(),
    ".m8":       SkinType(),
    ":bound":    BoundType(),
    ":tag":      TagType(),
    ":tagframe": TagFrameType(),
    ":bone":     BoneType() }

Generics = [MiscGroupType(), FrameGroupType()]  # AiV

#
# Use the function below to call a method of the Entity Manager classes.
# "method" is the function (in quotes) being called within the class.
# Syntax is : CallManager("method", entity, arguments...)
#

def CallManager(fn, *args):
    "Calls a function suitable for the QuArK object given as second argument."
    tag = args[0].type
    try:
        if tag == ':m':
            mgr = Generics[args[0].getint("type")]
        else:
            mgr = Mapping[tag]
    except:
        mgr = EntityManager()    # unknown type
    return apply(getattr(mgr, fn).im_func, args)  # call the function



#
# Function to load the form corresponding to an entity list.
#

def LoadEntityForm(sl):
    formobj = None
    if len(sl):
        f1 = CallManager("dataformname", sl[0])
        for obj in sl[1:]:
            f2 = CallManager("dataformname", obj)
            if f2!=f1:
                f1 = None
                break
        if f1 is not None:
            flist = quarkx.getqctxlist(':form', f1)
            if len(flist):
                formobj = flist[-1]
    return formobj

# ----------- REVISION HISTORY ------------
#
#
#$Log: mdlentities.py,v $
#Revision 1.93  2012/10/13 21:54:20  cdunde
#To correct and update model settings.
#
#Revision 1.92  2012/10/09 06:10:24  cdunde
#Forgot to remove print statements...My Bad!
#
#Revision 1.91  2012/10/09 05:31:55  cdunde
#To add dictspec items for Model Root that apply to Quake1 and HexenII models.
#
#Revision 1.90  2011/11/13 04:32:41  cdunde
#Bone control hint update.
#
#Revision 1.89  2011/11/13 03:15:10  cdunde
#To allow the changing of bonecontrol indexes.
#
#Revision 1.88  2011/03/26 23:35:16  cdunde
#Updated Model Editor Camera Position system with Hotkeys to take quick shots of both Editor and Floating 3D views,
#kept in separate folders for both Standard modes and True3D modes with Hotkeys to scroll through those shots.
#
#Revision 1.87  2011/03/17 18:11:38  cdunde
#Removed code that messed all the 2D views drawing up.
#
#Revision 1.86  2011/03/15 08:25:46  cdunde
#Added cameraview saving duplicators and search systems, like in the Map Editor, to the Model Editor.
#
#Revision 1.85  2011/02/11 19:52:56  cdunde
#Added import support for Heretic II and .m8 as supported texture file type.
#
#Revision 1.84  2011/01/13 01:34:30  cdunde
#To update shader files edited in shader dialog.
#
#Revision 1.83  2011/01/04 11:10:20  cdunde
#Added .vtf as supported texture file type for game HalfLife2.
#
#Revision 1.82  2010/12/28 20:18:53  cdunde
#Changes for tags that use both the model folder and name or just the model folder.
#
#Revision 1.81  2010/12/10 20:18:32  cdunde
#Added bbox edit menu items.
#
#Revision 1.80  2010/12/07 06:06:52  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.79  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.78  2010/10/20 20:17:54  cdunde
#Added bounding boxes (hit boxes) and bone controls support used by Half-Life, maybe others.
#
#Revision 1.77  2010/06/15 20:38:36  cdunde
#Added .ftx as supported texture file type for game FAKK2.
#
#Revision 1.76  2010/06/07 02:45:28  cdunde
#Moved the 'pickle' saving call function to where it was needed to increase editor response time.
#
#Revision 1.75  2010/06/07 00:06:29  cdunde
#Changed method of updating vertex weight by dialog setting to make it more responsive and isolated.
#
#Revision 1.74  2010/05/14 06:12:32  cdunde
#Needed fix, in case user deletes Misc group or components with tags, to avoid errors.
#
#Revision 1.73  2010/05/14 00:26:45  cdunde
#Need fix, in case user deletes Skeleton group, to avoid errors and update ModelComponentList.
#
#Revision 1.72  2010/05/03 06:01:46  cdunde
#To remove unneeded code causing dupe drawing and slowdown when comps are hidden and shown.
#
#Revision 1.71  2010/05/01 04:49:04  cdunde
#Weights dialog fix by DanielPharos and reset of range from .01 to 1.0.
#
#Revision 1.70  2010/05/01 04:25:37  cdunde
#Updated files to help increase editor speed by including necessary ModelComponentList items
#and removing redundant checks and calls to the list.
#
#Revision 1.69  2010/03/26 07:28:42  cdunde
#To add new Model Editor sub-group folders to the Skins group.
#
#Revision 1.68  2009/12/12 23:45:39  cdunde
#Added skins and frames counts to component specifics page.
#
#Revision 1.67  2009/11/09 18:01:58  cdunde
#Fix for errors sometimes because of dictspec not being set.
#
#Revision 1.66  2009/10/17 09:17:31  cdunde
#Added selection and playing of .md3 weapons with player models CFG Animation.
#
#Revision 1.65  2009/10/16 21:01:18  cdunde
#Menu update.
#
#Revision 1.64  2009/10/16 04:57:42  cdunde
#To get .md3 weapon tags to rotate with the weapon when attached to a player model.
#
#Revision 1.63  2009/10/16 00:59:17  cdunde
#Add animation rotation of weapon, for .md3 imports, when attached to model.
#
#Revision 1.62  2009/10/14 00:20:47  cdunde
#Various fixes for CFG Animation and interpolation.
#
#Revision 1.61  2009/10/12 20:49:56  cdunde
#Added support for .md3 animationCFG (configuration) support and editing.
#
#Revision 1.60  2009/10/06 09:26:17  cdunde
#To create animated tag frames for all imported .md3 models with tags, such as weapons
#
#Revision 1.59  2009/10/06 05:59:26  cdunde
#To give the tags and tag_components lists something to do.
#
#Revision 1.58  2009/10/04 22:20:10  cdunde
#Added lists showing component Tags and tag_components.(not functional, just for ref.)
#
#Revision 1.57  2009/09/30 19:37:26  cdunde
#Threw out tags dialog, setup tag dragging, commands, and fixed saving of face selection.
#
#Revision 1.56  2009/09/24 06:46:02  cdunde
#md3 rotation update, baseframe creation and proper connection of weapon tags.
#
#Revision 1.55  2009/09/18 03:21:19  cdunde
#Setup dialog for selection of tags to attach for .md3 items such as weapons.
#
#Revision 1.54  2009/09/08 06:45:12  cdunde
#Setup function to attach tags for imported .md3 models, such as weapons.
#
#Revision 1.53  2009/09/07 01:38:45  cdunde
#Setup of tag menus and icons.
#
#Revision 1.52  2009/09/06 11:54:44  cdunde
#To setup, make and draw the TagFrameHandles. Also improve animation rotation.
#
#Revision 1.51  2009/09/03 18:47:54  cdunde
#To add info to component specifics page.
#
#Revision 1.50  2009/08/24 23:39:21  cdunde
#Added support for multiple bone sets for imported models and their animations.
#
#Revision 1.49  2009/08/15 09:37:14  cdunde
#To fix improper bone position on specifics page for different frame selection.
#
#Revision 1.48  2009/08/06 17:41:05  cdunde
#Weights Dialog update.
#
#Revision 1.47  2009/07/27 05:53:08  cdunde
#To fix undefined variable.
#
#Revision 1.46  2009/07/14 00:27:33  cdunde
#Completely revamped Model Editor vertex Linear draglines system,
#increasing its reaction and drawing time to twenty times faster.
#
#Revision 1.45  2009/07/08 18:53:38  cdunde
#Added ASE model exporter and completely revamped the ASE importer.
#
#Revision 1.44  2009/06/09 05:51:48  cdunde
#Updated to better display the Model Editor's Skeleton group and
#individual bones and their sub-bones when they are hidden.
#
#Revision 1.43  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.42  2009/05/01 20:39:34  cdunde
#Moved additional Specific page systems to mdlentities.py as modules.
#
#Revision 1.41  2009/05/01 05:54:46  cdunde
#Small fix to stop errors.
#
#Revision 1.40  2009/04/29 23:50:03  cdunde
#Added auto saving and updating features for weights dialog data.
#
#Revision 1.39  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.38  2009/01/27 05:03:01  cdunde
#Full support for .md5mesh bone importing with weight assignment and other improvements.
#
#Revision 1.37  2008/12/14 22:08:27  cdunde
#Added Skin group Specifics page to allow importing of skins to that group.
#Added default skin Specifics page and default model type to list.
#
#Revision 1.36  2008/12/01 04:53:54  cdunde
#Update for component colors functions for OpenGL source code corrections.
#
#Revision 1.35  2008/11/29 06:56:25  cdunde
#Setup new Component Colors and draw Textured View Tint Colors system.
#
#Revision 1.34  2008/11/19 06:16:23  cdunde
#Bones system moved to outside of components for Model Editor completed.
#
#Revision 1.33  2008/10/17 22:29:05  cdunde
#Added assigned vertex count (read only) to Specifics/Args page for each bone handle.
#
#Revision 1.32  2008/10/15 00:01:30  cdunde
#Setup of bones individual handle scaling and Keyframe matrix rotation.
#Also removed unneeded code.
#
#Revision 1.31  2008/10/04 05:48:06  cdunde
#Updates for Model Editor Bones system.
#
#Revision 1.30  2008/09/22 23:30:27  cdunde
#Updates for Model Editor Linear and Bone handles.
#
#Revision 1.29  2008/09/15 04:47:48  cdunde
#Model Editor bones code update.
#
#Revision 1.28  2008/08/08 05:35:50  cdunde
#Setup and initiated a whole new system to support model bones.
#
#Revision 1.27  2008/07/23 01:22:23  cdunde
#Added function comment for clarity.
#
#Revision 1.26  2008/07/10 21:21:58  danielpharos
#The model component icon changes to an X when you hide the component.
#
#Revision 1.25  2008/05/01 15:39:19  danielpharos
#Made an import more consistent with all others
#
#Revision 1.24  2007/11/14 00:11:13  cdunde
#Corrections for face subdivision to stop models from drawing broken apart,
#update Skin-view "triangles" amount displayed and proper full redraw
#of the Skin-view when a component is un-hidden.
#
#Revision 1.23  2007/11/04 00:33:33  cdunde
#To make all of the Linear Handle drag lines draw faster and some selection color changes.
#
#Revision 1.22  2007/10/24 14:57:43  cdunde
#Added disabled to Hide and Show Component menu items for easer distinction.
#
#Revision 1.21  2007/10/09 04:16:25  cdunde
#To clear the EditorObjectList when the ModelFaceSelList is cleared for the "rulers" function.
#
#Revision 1.20  2007/09/01 19:36:40  cdunde
#Added editor views rectangle selection for model mesh faces when in that Linear handle mode.
#Changed selected face outline drawing method to greatly increase drawing speed.
#
#Revision 1.19  2007/08/01 07:37:30  cdunde
#Changed to only allow model component frames to cause handles to be drawn, as should be the case.
#
#Revision 1.18  2007/06/20 22:04:08  cdunde
#Implemented SkinFaceSelList for Skin-view for selection passing functions from the model editors views
#and start of face selection capabilities in the Skin-view for future functions there.
#
#Revision 1.17  2007/06/03 23:44:35  cdunde
#To stop Access violation error when a component is "Hidden" that has faces selected.
#def ShowHideComp still needs a lot of work to stop any handles from being drawn while
#component is "Hidden" allowing them to be dragged still and double draw when un-Hidden.
#
#Revision 1.16  2007/05/25 08:33:18  cdunde
#To fix indention error.
#
#Revision 1.15  2007/05/25 07:44:19  cdunde
#Added new functions to 'Views Options' to set the model's
#mesh lines color and draw in frame selection.
#
#Revision 1.14  2007/05/18 16:56:22  cdunde
#Minor file cleanup and comments.
#
#Revision 1.13  2007/04/12 23:57:31  cdunde
#Activated the 'Hints for handles' function for the Model Editors model mesh vertex hints
#and Bone Frames hints. Also added their position data display to the Hint Box.
#
#Revision 1.12  2006/11/30 01:19:33  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.11  2006/11/29 07:00:25  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.10.2.3  2006/11/15 23:06:14  cdunde
#Updated bone handle size and to allow for future variable of them.
#
#Revision 1.10.2.2  2006/11/15 22:34:20  cdunde
#Added the drawing of misc model items and bones to stop errors and display them.
#
#Revision 1.10.2.1  2006/11/04 00:49:34  cdunde
#To add .tga model skin texture file format so they can be used in the
#model editor for new games and to start the displaying of those skins
#on the Skin-view page (all that code is in the mdlmgr.py file).
#
#Revision 1.10  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.7  2001/02/01 22:03:15  aiv
#RemoveVertex Code now in Python
#
#Revision 1.6  2000/10/11 19:07:47  aiv
#Bones, and some kinda skin vertice viewer
#
#Revision 1.5  2000/08/21 21:33:04  aiv
#Misc. Changes / bugfixes
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#