"""   QuArK  -  Quake Army Knife

Tag commands toolbar
"""
#
# Copyright (C) 1996-03 The QuArK Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/maptagtoolbar.py,v 1.13 2013/03/17 14:15:09 danielpharos Exp $

Info = {
   "plug-in":       "Tag Commands Toolbar",
   "desc":          "Toolbar for brush tag & wrap commands",
   "date":          "February 10 2003",
   "author":        "cdunde-tiglari-Decker-Nerdlll",
   "author e-mail": "cdunde1@attbi.com",
   "quark":         "Version 6" }


import quarkx
from tagging import *
import maptagside
import maptexpos


def addtoTaggedClick(m):
    editor = mapeditor()
    if editor is None: return
    if gettaggedlist(editor) is None and gettagged(editor) is None:
        quarkx.msgbox("No Tagged items exist.\n\nYou must first tag one side or vertex\nbefore you can use this function to add more.\n\nNothing done.", MT_ERROR, MB_OK)
        return
    try:
        sides = [m.side]
    except (AttributeError):
        sides = editor.layout.explorer.sellist
    if (len(sides) < 1):
        quarkx.msgbox("No selection has been made\n\nYou must first select a single\nface or vertex point to add", MT_ERROR, MB_OK)
        return
    for side in sides:
        if (side.type != ":f"):
            quarkx.msgbox("Nothing has been done\n\nYou have selected a brush or multiple brushes\n\nYou need to select a single face or vertex point\nof a single brush to be able to add it", MT_ERROR, MB_OK)
            return
    else:
        taglist = gettaggedlist(editor)
        side = editor.layout.explorer.uniquesel
        if side is not None:
            addtotaggedfaces(side, editor)


def removefromTaggedClick(m):
    editor = mapeditor()
    if editor is None: return
    if gettaggedlist(editor) is None and gettagged(editor) is None:
        quarkx.msgbox("No Tagged items exist.\n\nThere must first be a tagged side or vertex\nbefore you can use this function to remove one\nof the items from the Tag List.\n\nNothing done.", MT_ERROR, MB_OK)
        return
    try:
        sides = [m.side]
    except (AttributeError):
        sides = editor.layout.explorer.sellist
    if (len(sides) < 1):
        quarkx.msgbox("No selection has been made.\n\nYou must first select a single\nface or vertex point to remove its tag.", MT_ERROR, MB_OK)
        return
    for side in sides:
        if (side.type != ":f"):
            quarkx.msgbox("Nothing has been done\n\nYou have selected a brush or multiple brushes\n\nYou need to select a single face or vertex point\nof a single brush to be able to remove it", MT_ERROR, MB_OK)
            return
    else:
        side = editor.layout.explorer.uniquesel
        if side is not None:
            removefromtaggedfaces(side, editor)


def selectTaggedClick(m):
  editor = mapeditor()
  if editor is None:
    return
  if gettaggedlist(editor) is None and gettagged(editor) is None:
    quarkx.msgbox("No Tagged items exist.\n\nNothing to select.", MT_ERROR, MB_OK)
    return
  else:
    if gettagged(editor) is None:
      taglist = gettaggedlist(editor)
      editor.layout.explorer.sellist = taglist
      return
    else:
      tagged = gettagged(editor)
      tagged = [tagged]
      editor.layout.explorer.sellist = tagged


def linkFaceClick(m):
  editor = mapeditor()
  tagged = gettagged(editor)
  m.side = editor.layout.explorer.uniquesel
  if gettagged(editor) is None:
    quarkx.msgbox("Nothing done\n\nEither you have not selected anything,\nmade multiple selections,\nor not tagged the face\nyou want to link to\nand selected one beside it\nto link.\n\nSee the button F1 help for more info.", MT_ERROR, MB_OK)
    return
  if m.side == tagged:
    quarkx.msgbox("Nothing done\n\nYou have selected the tagged face\nSelect a face beside it to link to.\n\nSee the button F1 help for more info.", MT_ERROR, MB_OK)
    return
  maptagside.LinkFaceClick(m, glue=1)


def glueLinkedClick(m):
  editor = mapeditor()
  o = editor.layout.explorer.uniquesel 
  m = qmenu.item("Dummy", None, "") 
  m.object = o
  side = o
  tagged = gettagged(editor)
  if tagged is None:
    quarkx.msgbox("Nothing done\n\nEither you have not selected anything,\nmade multiple selections,\nselected a single brush,\nor not tagged a side.\n\nSee this buttons F1 help for use info.", MT_ERROR, MB_OK)
    return
  if side == tagged:
    quarkx.msgbox("Nothing done\n\nYou have selected the tagged face\nSelect another face to link and glue to this one.\n\nSee the button F1 help for more info.", MT_ERROR, MB_OK)
    return
  tag = tagged.getint("_tag")
  if tag == 0:
    quarkx.msgbox("Nothing done\n\nYou must first use the\n'Link face to tagged' function\nfor this face.\nThen the 'Glue linked' function.", MT_ERROR, MB_OK)
    return
  m.tag = o.getint("_tag")
  maptagside.GlueLinkedClick(m)


def unlinkFaceClick(m):
  editor = mapeditor()
  o = editor.layout.explorer.uniquesel 
  m = qmenu.item("Dummy", None, "") 
  m.object = o
  tagged = gettagged(editor)
  if m.object is None:
    quarkx.msgbox("No selection has been made\nor a multiple selection has.\n\nYou must first select a single\nlinked face to be removed", MT_ERROR, MB_OK)
    return
  if tagged is None:
    quarkx.msgbox("Nothing done\n\nNothing Tagged", MT_ERROR, MB_OK)
    return
  if o == tagged:
    quarkx.msgbox("Nothing done\n\nYou have selected the tagged face.\nSelect a linked face to have it removed.", MT_ERROR, MB_OK)
    return
  m.tag = tagged.getint("_tag")
  if m.tag == 0:
    quarkx.msgbox("Nothing done\n\nNothing Linked", MT_ERROR, MB_OK)
    return
  allfaces = editor.Root.findallsubitems("",":f")
  linkedfaces = maptagside.getlinkedfaces(m.tag, allfaces)
  if not (o in linkedfaces): 
    quarkx.msgbox("Nothing done\n\nYou have selected a brush\nor a non-linked face.\n\nYou need to select a linked face to have it removed.", MT_ERROR, MB_OK)
    return
  maptagside.UnlinkFaceClick(m)


def selectClick(m): 
  editor = mapeditor()
  o = editor.layout.explorer.uniquesel
  if o is None:
    quarkx.msgbox("No selection\nor multiple selections\nhave been made.\n\nOnly select and tag one face\nto use this function.", MT_ERROR, MB_OK)
    return
  tagged = gettaggedlist(editor)
  if tagged is not None:
    quarkx.msgbox("Nothing done\n\nOther tags exist.\nThis function will not work\nwith multiple tags set.\n\nYou must clear all tags,\nand retag your selection again\nfor this function to work.", MT_ERROR, MB_OK)
    return
  tagged = gettagged(editor)
  if o == tagged:
    m.tag = tagged.getint("_tag")
    if m.tag == 0:
      quarkx.msgbox("Nothing done\n\nNothing Linked", MT_ERROR, MB_OK)
      return
    maptagside.SelectClick(m)
  else:
    quarkx.msgbox("Nothing done\n\nSelection is not tagged\nor you have not selected a tagged side.", MT_ERROR, MB_OK)


def unlinkAllClick(m): 
  editor = mapeditor()
  o = editor.layout.explorer.uniquesel
  if o is None:
    quarkx.msgbox("No selection\nor multiple selections\nhave been made.\n\nOnly select and tag one face\nto use this function.", MT_ERROR, MB_OK)
    return
  tagged = gettaggedlist(editor)
  if tagged is not None:
    quarkx.msgbox("Nothing done\n\nOther tags exist.\nThis function will not work\nwith multiple tags set.\n\nYou must clear all tags,\nand retag your selection again\nfor this function to work.", MT_ERROR, MB_OK)
    return
  tagged = gettagged(editor)
  if o == tagged:
    m.tag = tagged.getint("_tag")
    if m.tag == 0:
      quarkx.msgbox("Nothing done\n\nNothing Linked", MT_ERROR, MB_OK)
      return
    m.object = ""
    maptagside.UnlinkAllClick(m)
  else:
    quarkx.msgbox("Nothing done\n\nSelection is not tagged\nor you have not selected a tagged side.", MT_ERROR, MB_OK)


def taggedWrapClick(m): 
  editor = mapeditor() 
  o = editor.layout.explorer.uniquesel 
  m = qmenu.item("Dummy", None, "") 
  m.side = o 
  if gettaggedlist(editor) is None:
    quarkx.msgbox("Nothing done\n\nEither you have not selected anything,\nmade multiple selections,\nor not tagged your sides and\nselected the tagged face\nyou want to (copy) wrap from.", MT_ERROR, MB_OK)
    return
  maptagside.wraptaggedstate(m, o)
  taggedfaces = gettaggedfaces(editor) 
  if not (o in taggedfaces): 
    quarkx.msgbox("Nothing done\n\nYou have selected a non-tagged face\n\nYou need to select the tagged face\nyou want to (copy) wrap from ", MT_ERROR, MB_OK)
    return
  maptagside.TaggedWrapClick(m)


def pillarWrapClick(m):
  editor = mapeditor()
  o = editor.layout.explorer.uniquesel
  m = qmenu.item("Dummy", None, "")
  tagged = gettagged(editor)
  side = o
  if gettagged(editor) is None:
    quarkx.msgbox("Nothing done\n\nEither you have not selected anything,\nmade multiple selections,\nor not tagged the face\nyou want to (copy) wrap from\nand selected one beside it\nto wrap to.\n\nSee the button F1 help for more info.", MT_ERROR, MB_OK)
    return
  if side == tagged:
    quarkx.msgbox("Nothing done\n\nYou have selected the tagged face\nSelect a face beside it to wrap to.\n\nSee the button F1 help for more info.", MT_ERROR, MB_OK)
    return
  maptagside.pillarwrapdisabler(m, tagged, o)
  if not ("wraplist" in dir(m)):
    quarkx.msgbox("Nothing done\n\nYou must select one of the faces next to the tagged face on the same brush as the tagged face.\n\nSee the button F1 help for more info.", MT_ERROR, MB_OK)
    return
  maptagside.PillarWrapClick(m)


def projTexClick(m):
  editor = mapeditor()
  if gettaggedlist(editor) is None and gettagged(editor) is None:
    quarkx.msgbox("No Tagged items exist.\nNothing done.\n\nYou must first tag a face with\nthe texture you want to project.\n\nThen select a brush or face to\nproject the tagged texture to.", MT_ERROR, MB_OK)
    return
  o = editor.layout.explorer.uniquesel
  if o is None:
    quarkx.msgbox("No selection\n\nYou must select a brush or face to\nproject the tagged texture to.", MT_ERROR, MB_OK)
    return
  tagged = gettaggedplane(editor)
  if o == tagged:
    quarkx.msgbox("Nothing done\n\nYou have selected the tagged face.\n\nSelect another face or a brush\nto project the tagged texture to.", MT_ERROR, MB_OK)
    return
  m = qmenu.item("Dummy", None, "")
  m.olist = [o]
  m.tagged = gettagged(editor)
  maptagside.ProjTexClick(m)


def chooseTexture(m):
  import quarkpy.mapbtns
  quarkpy.mapbtns.texturebrowser()


def posTexClick(m):
    editor = mapeditor()
    try:
        sides = [m.side]
    except (AttributeError):
        sides = editor.layout.explorer.sellist
    if (len(sides) < 1):
        quarkx.msgbox("No selection has been made\n\nYou must first select a single face\nto activate this tool\nand position its texture", MT_ERROR, MB_OK)
        return
    for side in sides:
        if (side.type != ":f"):
            quarkx.msgbox("You have selected a brush or multiple brushes\n\nYou need to select a single face of a\nsingle brush to be able to activate\nthis tool and position its texture", MT_ERROR, MB_OK)
            return
    o = editor.layout.explorer.uniquesel
    m = qmenu.item("Dummy", None, "")
    m.o = o
    maptexpos.PosTexClick(m)


def texflagsClick(m):
    editor = mapeditor()
    flist = quarkx.getqctxlist(":form", "TextureFlags")
    if not len(flist):
        quarkx.msgbox("The 'Texture Flags' function is inoperable in this game mode\nbecause this game does not support texture flags or\nthe form has not been setup in the addons Data.qrk file", MT_INFORMATION, MB_OK)
        return
    if editor.layout.explorer.uniquesel is None:
        quarkx.msgbox("No selection has been made\nor you have selected multiple brushes\n\nYou must first select a brush or single face\nto activate this tool to set its texture flags", MT_ERROR, MB_OK)
        return
    try:
        sides = [m.side]
    except (AttributeError):
        sides = editor.layout.explorer.sellist
    for side in sides:
        if (side.type != ":f"):
            editor.layout.flagsclick(None)
        else:
            quarkx.msgbox("If you have different flags\nfor the sides of a brush\nIt will NOT crash the game\nBut will cause a warning in the console like\n\n'Entity 0, Brush 63: mixed face contents'", MT_WARNING, MB_OK)
            editor.layout.flagsclick(None)



# This defines and builds the toolbar.

class TagModesBar(ToolBar):
    "The Tag Commands Tool Palette."

    Caption = "Tag Tool Palette"
    DefaultPos = ((0, 0, 0, 0), 'topdock', 0, 2, 1)

    def buildbuttons(self, layout):
        if not ico_dict.has_key('ico_tagside'):
            ico_dict['ico_tagside']=LoadIconSet1("tagside", 1.0)
        icons = ico_dict['ico_tagside']


# See the quarkpy/qtoolbar.py file for the class button: definition
# which gives the layout for each of the  " "  attribut
# assignments below.

# Now we can assign an opperation to each buttons attributes
# which are "onclick" (what function to perform),
# "hint" (what to display for the flyover and F1 popup window text),
# "iconlist" (the icon.bmp file to use),
# "iconindex" (a number attribute, which is the place holder
# for each icon in the icon.bmp file.
# and "infobaselink" (the infobase HTML page address and ancor,
# which is a locator for a spacific place on the page)
 

        btn0 = qtoolbar.button(maptagside.TagSideClick, "Tag side||Tag side:\n\nThis function will place a tag on the side (face) that is selected.", icons, 0, infobaselink="maped.plugins.tagside.html")


        btn1 = qtoolbar.button(maptagside.ClearTagClick, "Clear all tags||Clear all tags:\n\nThis will clear (remove) all the tags that have been set.", icons,1, infobaselink="maped.plugins.tagside.html#basic")


        btn2 = qtoolbar.button(maptagside.GlueSideClick, "Glue to tagged||Glue to tagged:\n\nSee the Infobase for more detail.", icons, 2, infobaselink="maped.plugins.tagside.html#basic")


        btn3 = qtoolbar.button(addtoTaggedClick, "Add to tagged||Add to tagged:\n\nThis will tag and add more faces to create a group of tagged faces.", icons, 3, infobaselink="maped.plugins.tagside.html#basic")


        btn4 = qtoolbar.button(removefromTaggedClick, "Remove from tagged||Remove from tagged:\n\nThis will remove just the selected face, from the tagged group.", icons, 4, infobaselink="maped.plugins.tagside.html#basic")


        btn5 = qtoolbar.button(selectTaggedClick, "Select Tagged Face(s)||Select Tagged Face(s):\n\nThis will select all of the curently tagged faces.", icons, 5, infobaselink="intro.mapeditor.menu.html#selectionmenu")


        btn6 = qtoolbar.button(linkFaceClick, "Link face(s) to tagged||Link face(s) to tagged:\n\nIt's purpose to make 'permanent glue', so that faces that are meant to stay stuck together are more likely to do so.", icons, 6, infobaselink="maped.plugins.tagside.html#linking")


        btn7 = qtoolbar.button(glueLinkedClick, "Glue linked||Glue linked:\n\nIt's purpose to make 'permanent glue', so that faces that are meant to stay stuck together are more likely to do so.\n\nTo use this function:\n1) Tag a single face,\n\n2) Select another single face and use the 'Link to tagged' function,\n\n3) With the same face in step 2) still selected, now use this function.", icons, 7, infobaselink="maped.plugins.tagside.html#linking")


        btn8 = qtoolbar.button(unlinkFaceClick, "Unlink face||Unlink face:\n\nThe selected face is detached from the others it's linked to.\n\nTo use this function:\n1) Select and tag one of the linked faces,\n\n2)  Now select the face you want to unlink and click this button.", icons, 8, infobaselink="maped.plugins.tagside.html#linking")


        btn9 = qtoolbar.button(selectClick, "Select linked faces||Select linked faces:\n\nThis selects all the faces linked to this face.\n\nSo that you can for example drag or shear them as a multiselection, rather than first move one and then glue the others to it.", icons, 9, infobaselink="maped.plugins.tagside.html#linking")


        btn10 = qtoolbar.button(unlinkAllClick, "Unlink all||Unlink all:\n\nThis will unlink and cancel the linked settings for all of the faces linked to this face.", icons, 10, infobaselink="maped.plugins.tagside.html#linking")


        btn11 = qtoolbar.button(maptagside.WrapMultClick, "Texture Wrapping Multiplier||Texture Wrapping Multiplier:\n\nThis is for texture wrapping functions only.\n\nEnter how many times you want the texture pattern repeated as it is wrapped. You can also use decimals like .5 for half. If you enter 0, the multiplier is not set and will have no effect.\n\nDo not close the multiplier until you have completed your wrapping functions or it will also have no effect.", icons, 11, infobaselink="maped.plugins.tagside.html#texture")


        btn12 = qtoolbar.button(maptagside.AlignTexClick, "Wrap texture from tagged||Wrap texture from tagged:\n\nThis is primarily for column brushes only (although it can be used for other shapes with parallel sides as well).\n\nIt wraps the texture from one tag face to the next tagged face.", icons, 12, infobaselink="maped.plugins.tagside.html#texture")


        btn13 = qtoolbar.button(taggedWrapClick, "Across tagged||Across tagged:\n\nThis is primarily for column brushes only (although it can be used for other shapes with parallel sides as well).\n\nIt wraps (copies) the texture from one tag face to all the other tagged faces.\n\nIf you want to 'spread' the texture of one face\nacross all the tagged faces,\nopen the 'Texture Wrapping Multiplier'\n(do NOT close it until you are done),\nset it for how many times you want the pattern repeated,\nsellect the face with the texture you want to use\nand click this button to do your wrapping.\nIn either case, be sure the texture you want to use is at one end or the other. Other wise an error will occur.", icons, 13, infobaselink="maped.plugins.tagside.html#texture")


        btn14 = qtoolbar.button(pillarWrapClick, "Around pillar||Around pillar:\n\nThis will copy and duplicate the texture of the tagged face, to each face around the pillar in the direction of the selected face, scaling to eliminate seams.\n\nIf you want to 'spread' the texture around the pillar, open the 'Texture Wrapping Multiplier', set it to how many times you want the texture pattern repeated as it is wrapped and leave it open until you are done with the wrapping process. Select one of the faces beside the tagged one and click the 'Around pillar' button again.\n\nIf you select a face that is NOT beside the tagged face, an error will occur.\n\nWon't work if the edges to be wrapped around aren't all parallel, and scales texture minimally to fit.  `preserve aspect ratio' option controls whether one or both texture dimensions are scaled.", icons, 14, infobaselink="maped.plugins.tagside.html#texture")


        btn15 = qtoolbar.button(maptagside.MirrorFlipTexClick, "Mirror flip tex||Mirror flip tex:\n\nThis will flip (mirror) the texture on the selected face.", icons, 15)


        btn16 = qtoolbar.button(projTexClick, "Project from tagged||Project from tagged:\n\nThis will project the texture of the tagged face onto the selected one, or those in the selected item, so that a texture can be wrapped without seams over an irregular assortment of faces.\n\nTextures aren't projected onto faces that are too close to perpendicular to the projecting face.", icons, 16)


        btn17 = qtoolbar.button(chooseTexture, "Choose Texture||Choose Texture:\n\nThis will open the 'Texture Browser' window (toolbox). If a brush or face is curently sellected, it will find its texture unless the item has more than one texture.", ico_dict['ico_maped'], 0, infobaselink="intro.texturebrowser.overview.html")


        btn18 = qtoolbar.button(posTexClick, "Position Texture tool||Position Texture tool:\n\nThis tool will allow you to adjust the position of the texture on a single selected face.\n\nBy clicking on the keypad arrows, you can manipulate the texture in various ways by 1 unit or 1 degree at a time. Or you can enter amounts in the input boxes for finer adjustments to the texture.\n\nThe changes can be viewed in the Face-view and editor 3D view (if the textured view option is on) as they are made.", icons, 17, infobaselink="maped.plugins.tagside.html#texture")


        btn19 = qtoolbar.button(texflagsClick, "Texture flag settings||Texture flag settings:\n\nThis will open the texture flag settings window. The setting of these flags, or a combination of them, gives the selected brush unique characteristics. Each setting has a 'fly over hint' to help tell you what it does.", ico_dict['ico_maped'], 22, infobaselink="intro.texturebrowser.details.html#textureflags")


        return [btn0, btn2, btn3, btn4, btn5, btn1, qtoolbar.sep, btn6, btn7, btn8, btn9, btn10, qtoolbar.sep, btn11, btn12, btn13, btn14, btn15, btn16, btn17, btn18, btn19]


# Now we add this toolbar, to the list of other toolbars,
# in the main Toolbars menu.

# The script below initializes the item "toolbars",
# which is already defined in the file quarkpy/maptools.py
# and sets up the first two items in the standard main Toolbars menu.

# This one is added below them, because all of the files in the
# quarkpy folder are loaded before the files in the plugins folder.

quarkpy.maptools.toolbars["tb_tagmodes"] = TagModesBar


# ----------- REVISION HISTORY ------------
# $Log: maptagtoolbar.py,v $
# Revision 1.13  2013/03/17 14:15:09  danielpharos
# Fixed a typo.
#
# Revision 1.12  2007/12/28 23:22:41  cdunde
# Setup displaying of 'Used Textures' in current map being edited in the Texture Browser.
#
# Revision 1.11  2005/10/15 00:51:56  cdunde
# To reinstate headers and history
#
# Revision 1.8  2005/08/26 02:19:11  cdunde
# To fix error for games that do not use texture flags or the
#  texture flags form had not been setup in the data.qrk file.
#
# Revision 1.7  2005/08/16 04:03:12  cdunde
# Fix toolbar arraignment
#
# Revision 1.6  2004/11/13 11:03:25  peter-b
# Better error handling for "wrap around pillar" function.
#
# Revision 1.5  2004/01/24 16:28:39  cdunde
# To reset defaults for toolbars
#
# Revision 1.4  2003/07/15 07:51:38  cdunde
# Remove unneeded seperators to shorten toolbar for screen size.
#
# Revision 1.3  2003/07/14 20:25:14  cdunde
# To add selection toolbar and update tag toolbar
#
# Revision 1.2  2003/05/09 01:01:08  cdunde
# Added function buttons for tagtoolbar
#
# Revision 1.1  2003/03/15 07:19:30  cdunde
# To add hint updates and infobase links
#
