"""   QuArK  -  Quake Army Knife

Map editor pop-up menus.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapmenus.py,v 1.19 2008/11/17 19:10:23 danielpharos Exp $



import quarkx
from qdictionnary import Strings
import qmenu
import qhandles
from maputils import *
import mapcommands
import bspcommands
import plugins.map1addonsamendmenu
import plugins.map1addonsmenu
import mapselection
import mapbtns
from mapentities import CallManager


def ViewGroup1click(m):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    m.items = ViewGroupMenu(editor)

def EscClick(m):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    if editor.layout.mpp.n:
        editor.layout.mpp.viewpage(0)
    else:
        editor.layout.explorer.uniquesel = None


EditMenuCmds = [#qmenu.item("Remove selection", EscClick, "|The first time to press Esc, you are sent back to the 1st page; the second time, or if you where already at the 1st page, the currently selected objects are unselected."),
                #qmenu.sep,
                qmenu.popup("View Group", [], ViewGroup1click, "|options for groups", "intro.mapeditor.menu.html#viewgroup")]
EditMenuShortcuts = {}
#MapHotKeyList("Remove",  EditMenuCmds[0], EditMenuShortcuts)


#
# QuickKey shortcuts
#

def GridMinus(editor, view=None):
    editor.setgrid(editor.gridstep*0.5)

def GridPlus(editor, view=None):
    editor.setgrid(editor.gridstep*2.0)

def ZoomIn(editor, view=None):
    scale = commonscale(editor.layout.views)
    if not scale:
        scale = 1.0
    scale = scale*qhandles.MOUSEZOOMFACTOR
    if scale>100:
        scale=100 #DECKER clamp zoom-in
    setviews(editor.layout.views, "scale", scale)

def ZoomOut(editor, view=None):
    scale = commonscale(editor.layout.views)
    if not scale:
        scale = 1.0
    scale = scale/qhandles.MOUSEZOOMFACTOR
    if scale<0.001:
        scale=0.001 #DECKER clamp zoom-out
    setviews(editor.layout.views, "scale", scale)

def MoveLeft(editor, view=None):
    editor.movekey(view, -1,0)

def MoveRight(editor, view=None):
    editor.movekey(view, 1,0)

def MoveUp(editor, view=None):
    editor.movekey(view, 0,-1)

def MoveDown(editor, view=None):
    editor.movekey(view, 0,1)

# Note: the function *names* are used to look up the key from Defaults.qrk
QuickKeys = [GridMinus, GridPlus, ZoomIn, ZoomOut,
             MoveLeft, MoveRight, MoveUp, MoveDown]


#
# Menu bar builder
#
def BuildMenuBar(editor):
    import mapmgr
    import mapcommands
    import mapsearch
    import mapquakemenu
    import maptools
    import mapoptions

    if IsBsp(editor):
        File1, sc1 = qmenu.DefaultFileMenuBsp()
    else:
        File1, sc1 = qmenu.DefaultFileMenu()

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
    for l in mapmgr.LayoutsList:
        m = qmenu.item('%s layout' % l.shortname, editor.setlayoutclick, "switch to layout '%s'" % l.shortname)
        m.state = (l is lcls) and qmenu.radiocheck
        m.layout = l
        l1.append(m)
    Layout1 = qmenu.popup("&Layout", l1, lclick)

    Edit1, sc2 = qmenu.DefaultEditMenu(editor)
    sc1.update(sc2)   # merge shortcuts
    l1 = EditMenuCmds + MenuTexFlags(editor)
    if len(l1):
        Edit1.items = Edit1.items + [qmenu.sep] + l1
    sc1.update(EditMenuShortcuts)   # merge shortcuts

    Search1, sc2 = mapsearch.SearchMenu()
    sc1.update(sc2)   # merge shortcuts

    if IsBsp(editor):
        Commands1, sc2 = bspcommands.CommandsMenu()
    else:
        Commands1, sc2 = mapcommands.CommandsMenu()
    sc1.update(sc2)   # merge shortcuts

    Addons1, sc2 = plugins.map1addonsmenu.AddonsMenuCmds()
    sc1.update(sc2)   # merge shortcuts
    l1 = plugins.map1addonsamendmenu.AmendMenuCmds
    l2 = [qmenu.sep]
    if len(l1):
        Addons1.items = l1 + l2 + Addons1.items
        sc1.update(sc2)   # merge shortcuts

    Selection1, sc2 = mapselection.SelectionMenu()
    sc1.update(sc2)   # merge shortcuts

    Quake1, sc2 = mapquakemenu.QuakeMenu(editor)
    sc1.update(sc2)   # merge shortcuts

    Tools1, sc2 = maptools.ToolsMenu(editor, maptools.toolbars)
    sc1.update(sc2)   # merge shortcuts

    Options1, sc2 = mapoptions.OptionsMenu()
    sc1.update(sc2)   # merge shortcuts
    l1 = plugins.mapgridscale.GridMenuCmds
    l2 = [qmenu.sep]
    l3 = plugins.maptools.RulerMenuCmds
    l4 = [qmenu.sep]
    if len(l1):
        Options1.items = l1 + l2 + l3 + l4 + Options1.items
        sc1.update(sc2)   # merge shortcuts

    return [File1, Layout1, Edit1, quarkx.toolboxmenu,
     Search1, Commands1, Addons1, Selection1, Quake1, Tools1, Options1], sc1



def ViewGroupMenu(editor):

    grouplist = filter(lambda o: o.type==':g', editor.layout.explorer.sellist)

    onclick = mapbtns.groupview1click
    X0 = qmenu.item("Group is &visible",    onclick, "display the group normally")
    X1 = qmenu.item("Group is &grayed out", onclick, "always gray out the group")
    X2 = qmenu.item("Group is &hidden",     onclick, "completely hide the group")
    menulist = [X0, X1, X2, qmenu.sep]
    for text, flag, hint in (
      ("Hide on &textured views", VF_HIDEON3DVIEW, "don't show on 'camera' views"),
      ("&Cannot select with the mouse", VF_CANTSELECT, "cannot select by clicking on map views"),
      ("&Ignore to build maps", VF_IGNORETOBUILDMAP, "|Groups with this flag are not included in the map when you select commands from the '"+quarkx.setupsubset().shortname+"' menu. This lets you disable parts of the map that you don't want to try playing now.\n\nNote that you can force this flag to be ignored and all groups to be included, thanks to the corresponding command in the 'Options' menu.")):
        m = qmenu.item(text, onclick, hint)
        m.flag = flag
        menulist.append(m)

    if len(grouplist)==0:
        for m in menulist:
            if m is not qmenu.sep:
                m.state = qmenu.disabled
    else:
        common = 0
        mode1 = None
        for g in grouplist:
            try:
                viewstate = int(g[";view"])
            except:
                viewstate = 0
            common = common | viewstate
            viewstate = viewstate & (VF_GRAYEDOUT|VF_HIDDEN)
            if mode1 is None:
                mode1 = viewstate
            elif mode1 != viewstate:
                mode1 = -1
        X0.flag = 0
        X1.flag = VF_GRAYEDOUT
        X2.flag = VF_HIDDEN
        for m in menulist[:3]:
            m.state = (mode1==m.flag) and qmenu.radiocheck
        for m in menulist[4:]:
            m.state = (common & m.flag) and qmenu.checked

    return menulist


def BackgroundMenu(editor, view=None, origin=None):
    "Menu that appears when the user right-clicks on nothing."

    undo, redo = quarkx.undostate(editor.Root)
    if undo is None:   # to undo
        Undo1 = qmenu.item(Strings[113], None)
        Undo1.state = qmenu.disabled
    else:
        Undo1 = qmenu.macroitem(Strings[44] % undo, "UNDO", "undo the previous action (unlimited)")
    if redo is None:
        extra = []
    else:
        extra = [qmenu.macroitem(Strings[45] % redo, "REDO", "redo what you have just undone")]
    if origin is None:
        paste1 = qmenu.item("Paste", editor.editcmdclick, "paste from clipboard")
    else:
        paste1 = qmenu.item("Paste here", editor.editcmdclick, "paste objects at '%s'" % str(editor.aligntogrid(origin)))
        paste1.origin = origin
    paste1.cmd = "paste"
    paste1.state = not quarkx.pasteobj() and qmenu.disabled
    extra = extra + [qmenu.sep, paste1]
    if view is not None:
        def backbmp1click(m, view=view, form=editor.form):
            import qbackbmp
            qbackbmp.BackBmpDlg(form, view)
        backbmp1 = qmenu.item("Background image...", backbmp1click, "|Background image:\n\nWhen selected, this will open a dialog box where you can choose a .bmp image file to place and display in the 2D view that the cursor was in when the RMB was clicked.\n\nClick on the 'InfoBase' button below for full detailed information about its functions and settings.|intro.mapeditor.rmb_menus.noselectionmenu.html#background")
        extra = extra + [qmenu.sep] + TexModeMenu(editor, view) + [qmenu.sep, backbmp1]
    return [mapcommands.NewItem1, Undo1] + extra



def set_mpp_page(btn):
    "Switch to another page on the Multi-Pages Panel."

    editor = mapeditor(SS_MAP)
    if editor is None: return
    editor.layout.mpp.viewpage(btn.page)


#def NoTexFlags():
#    "true when the current game doesn't use Texture Flags"
#    game = quarkx.setupsubset().shortname
#    return game=="Quake 3"

#
# Texture Flags pop-up menu.
#

def MenuTexFlags(editor):
    if editor.texflags:

        def tfclick(m, editor=editor):

            #if NoTexFlags(): return None

            def checklist(flist, items):
               for p in items:
                  if p is not qmenu.sep:
                    spec = p.spec
                    check = 0
                    for face, default in flist:
                        s = face[spec]
                        if not s:
                            if default is not None:
                                s = default[spec]
                            if not s:
                                break
                        try:
                            n = int(s)
                        except:
                            break
                        if not (n&p.n):
                            break
                    else:
                        if len(flist):
                            check = qmenu.checked
                        else:
                            check = qmenu.disabled
                    p.state = check



            if not len(m.items):

                def flag1click(m, editor=editor):
                    flist = editor.layout.loadtfflist()
                    undo = quarkx.action()
                    setme = not m.state
                    for face, default in flist:
                        s = face[m.spec]
                        if (not s) and (default is not None):
                            s = default[m.spec]
                        try:
                            n = int(s)
                        except:
                            n = 0
                        if setme:
                            n = n | m.n
                        else:
                            n = n &~ m.n
                        undo.setspec(face, m.spec, `n`)
                    undo.ok(editor.Root, Strings[596])


                def makelist(formname, sep1, flag1click=flag1click):
                  flist =  quarkx.getqctxlist(":form", formname)
                  if not len(flist):
                    raise formname+" form not found"
                  form = flist[-1]
                  l1 = []
                  for p in form.subitems:
                    s = p["Typ"]
                    if s[:1] == "X":    # check box
                        try:
                            n = int(s[1:])
                        except:
                            n = 0
                        if n:
                            if sep1:
                                l1.append(qmenu.sep)
                                sep1 = 0
                            m1 = qmenu.item(p["Cap"], flag1click, p["Hint"])
                            m1.spec = p.shortname
                            m1.n = n
                            l1.append(m1)
                    elif s == "S":    # separator
                        sep1 = 1
                  return l1


                def makeflagsclick(form, label, title, help="", editor=editor):
                   item = qmenu.item(label, editor.layout.flagsclick2, help);
                   item.whatform = form
                   item.floattitle= title
                   return item
                   
                
                game = quarkx.setupsubset().shortname
                if game == "Sin":
                  cont = makelist("ContFlags",0)
                  surf = makelist("SurfFlags",0)
                  l1 = [qmenu.item("All Flags/Reset",
                          editor.layout.flagsclick, "All the flags"),
                        qmenu.popup("Content Flags",cont), 
                        qmenu.popup("Surface Flags",surf)] 
                else:
                  l1 = [qmenu.item("&Flags...", editor.layout.flagsclick, "open the flags window")]
                  l1[2:] = makelist("TextureFlags",1)
                m.items = l1
             
            flist = editor.layout.loadtfflist()
            game = quarkx.setupsubset().shortname
            if game == "Sin":
               checklist(flist, m.items[1].items)
               checklist(flist, m.items[2].items)
            else:
               checklist(flist, m.items[2:])
        texpop = qmenu.popup("Texture Flags", [], tfclick, "|surface property flags", "intro.texturebrowser.details.html#textureflags")
        #if NoTexFlags():
        #   texpop.state = qmenu.disabled
        #   texpop.hint = "|No Texture Flags for Quake 3; their function is performed by shaders."
        return [texpop]
    else:
        return []



#
# Entities pop-up menus.
#

def EntityMenuPart(sellist, editor):

    Spec1 = qmenu.item("&Specifics...", set_mpp_page, "view Specifics/Args")
    Spec1.page = 1
    Spec1.state = qmenu.default

    return [Spec1, qmenu.sep]



def MultiSelMenu(sellist, editor):

    Spec1 = qmenu.item("&Multiple specifics...", set_mpp_page, "Specifics/Args common to all entities")
    Spec1.page = 1
    Spec1.state = qmenu.default
    Tex1 = qmenu.item("&Texture...", mapbtns.texturebrowser, "choose texture of polyhedrons")

    return [Spec1, Tex1, qmenu.sep] + BaseMenu(sellist, editor)



def BaseMenu(sellist, editor):
    "The base pop-up menu for a given list of objects."

    mult = len(sellist)>1 or (len(sellist)==1 and sellist[0].type==':g')
    Force1 = qmenu.item(("&Force to grid", "&Force everything to grid")[mult],
      editor.ForceEverythingToGrid, "|This command forces the selected object(s) to the grid. It snaps their center to the nearest grid point.\n\nNote that for a polyhedron, this forces its center to the grid, not all its faces. For cubic polyhedron, you may need to divide the grid size by two before you get the expected results.")
    Force1.state = not editor.gridstep and qmenu.disabled


    Cancel1 = qmenu.item("&Cancel Selections", mapselection.EscClick, "cancel all items selected")
    #Cut1.cmd = "cut"
    Cut1 = qmenu.item("&Cut", editor.editcmdclick, "cut this to the clipboard")
    Cut1.cmd = "cut"
    Copy1 = qmenu.item("Cop&y", editor.editcmdclick, "copy this to the clipboard")
    Copy1.cmd = "copy"
    Delete1 = qmenu.item("&Delete", editor.editcmdclick, "delete this")
    Delete1.cmd = "del"

    return [Force1, qmenu.sep, Cancel1, qmenu.sep, Cut1, Copy1, Delete1]

# ----------- REVISION HISTORY ------------
#
#
#$Log: mapmenus.py,v $
#Revision 1.19  2008/11/17 19:10:23  danielpharos
#Centralized and fixed BSP file detection.
#
#Revision 1.18  2006/05/19 17:07:53  cdunde
#To add links to docs on RMB menus and background image function.
#
#Revision 1.17  2006/01/30 10:07:13  cdunde
#Changes by Nazar to the scale, zoom and map sizes that QuArK can handle
#to allow the creation of much larger maps for the more recent games.
#
#Revision 1.16  2005/11/18 02:21:53  cdunde
#To add new '2D Rulers' function, menu and
#updated Infobase docs covering it.
#
#Revision 1.15  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.12  2003/12/13 22:13:39  cdunde
#To add new Grid in 2D views feature plugin menu to Options menu
#
#Revision 1.11  2003/07/04 19:59:57  cdunde
#To add new Addons main menu item and sub-menus
#
#Revision 1.10  2003/03/21 05:57:05  cdunde
#Update infobase and add links
#
#Revision 1.9  2003/02/01 07:37:50  cdunde
#To add Cancel Selections to RMB menu
#
#Revision 1.8  2001/07/27 11:32:57  tiglari
#bsp study: special commands menu when bsp is loaded
#
#Revision 1.7  2001/04/28 02:21:04  tiglari
#move 'remove' to mapselection.py, add selection menu therefrom
#
#Revision 1.6  2001/03/20 07:59:40  tiglari
#customizable hot key support
#
#Revision 1.5  2001/01/26 19:07:04  decker_dk
#Clamped the scalefactors for keyboard zoom-modification to in:100 and out:0.01.
#
#Revision 1.4  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#