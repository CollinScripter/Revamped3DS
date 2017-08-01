"""   QuArK  -  Quake Army Knife

Implementation of QuArK Map editor's "Quake" menu
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapquakemenu.py,v 1.63 2012/10/07 17:57:35 danielpharos Exp $



import quarkx
from qdictionnary import Strings
from maputils import *
import qmenu
import qquake
import qutils


# Constants for BuildCheck extensions!
gExt_GotToExist     = "+"
gExt_MustNotExist   = "-"
gExt_Controllers    = gExt_GotToExist + gExt_MustNotExist
gExt_ValidExtChars  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
gExt_StartOfAction  = "{"
gExt_EndOfAction    = "}"
gExt_ActionFunction = ":"
gExt_SpecialChars   = gExt_StartOfAction + gExt_EndOfAction + gExt_ActionFunction
gExt_AllCharacters  = " " + gExt_Controllers + gExt_ValidExtChars + gExt_SpecialChars


def CreateCheckFileExtensionArray(instring):

    def FindSingleExtension(instring):
        # Must start with a 'gExt_Controllers' character!
        if (not instring[:1] in gExt_Controllers):
            return None, None
        # Find next char not in 'gExt_ValidExtChars', or end-of-line
        ext = instring
        for i in range(1, len(instring)):
            if (instring[i] not in gExt_ValidExtChars):
                ext = instring[0:i]
                instring = instring[i:]
                break
        action = None
        if (instring[:1] == gExt_StartOfAction):
            # Unpack action
            for i in range(1, len(instring)):
                if (instring[i] not in gExt_ValidExtChars):
                    action = instring[1:i]
                    break
        return ext, action

    # Remove all unnessary characters
    reducedstring = filter(lambda d: d in gExt_AllCharacters, instring)
    extactionlist = []
    for i in range(0, len(reducedstring)):
        ext, action = FindSingleExtension(reducedstring[i:])
        if (ext is not None):
            extactionlist = extactionlist + [(ext.upper(), action)]
    return extactionlist



class BuildPgmConsole(qquake.BatchConsole):
    "StdOut console for programs that build files."

    def __init__(self, cmdline, currentdir, bspfile, editor, next):
        qquake.BatchConsole.__init__(self, cmdline, currentdir, next)



class BuildPgmConsole_Advanced(qquake.BatchConsole):
    "StdOut console for programs that build files."

    def __init__(self, cmdline, currentdir, bspfile, editor, next, checkextensions):
        qquake.BatchConsole.__init__(self, cmdline, currentdir, next)
        self.editor=editor
        self.checkextensions = checkextensions
        # Remove file-extension
        try:
            self.bspfile_wo_ext = bspfile[:bspfile.rindex(".")]
        except:
            self.bspfile_wo_ext = bspfile
        # Initial check for files with checkextensions
        for ext, action in self.checkextensions:
            try:
                workfile = self.bspfile_wo_ext + "." + ext[1:]
                attr = quarkx.getfileattr(workfile)
                if (attr!=FA_FILENOTFOUND) and (attr&FA_ARCHIVE):
                    quarkx.setfileattr(workfile, attr-FA_ARCHIVE)
            except quarkx.error:
                pass

    def doAction(self, action, ext):
        # This is the place for the actions, that have HARDCODED names!
        if (action is None):
            return
        action = action.upper()
        if (action == "LOADLINFILE"):
            if self.editor is not None:
                import mapholes
#                debug('loading: '+ self.bspfile_wo_ext+'.'+ext)
                mapholes.LoadLinFile(self.editor, self.bspfile_wo_ext+'.'+ext)
        elif (action == "LOADPTSFILE"):
            if self.editor is not None:
                import mapholes
                mapholes.LoadLinFile(self.editor, self.bspfile_wo_ext+'.'+ext)
        else:
            print "ERROR: Unknown action \"" + action + "\" for extension \"" + ext + "\""

    def FileHasContent(self, ext, attr, filename):
        if (ext[:1] != gExt_MustNotExist):
            return 0
        if ((attr==FA_FILENOTFOUND) or not (attr&FA_ARCHIVE)):
            return 0
        if attr!=FA_FILENOTFOUND:
            f=open(filename, "r")
            data = f.readlines()
            for line in data:
                if line.strip()!='':
                    return 1
        return 0 # not actually necessary because Python functions returns None by default

    def close(self):
        errorfoundandprintet = 0
        for ext, action in self.checkextensions:
            errortext = None
            workfile = self.bspfile_wo_ext + "." + ext[1:]
            attr = quarkx.getfileattr(workfile)
            if ((ext[:1] == gExt_GotToExist) and ((attr==FA_FILENOTFOUND) or not (attr&FA_ARCHIVE))):
                errortext = "Build failed, because it did not create the (%s) file: " % ext + workfile
            elif self.FileHasContent(ext, attr, workfile):
#            elif ((ext[:1] == gExt_MustNotExist) and ((attr!=FA_FILENOTFOUND) and (attr&FA_ARCHIVE))):
                errortext = "Build failed, because it created the (%s) file: " % ext + workfile

            # Was error found?
            if (errortext is not None):
                if (not errorfoundandprintet):
                    print "!-!"*26
                    errorfoundandprintet = 1
                print errortext
                self.doAction(action, ext[1:])

        if (errorfoundandprintet):
            # Error occured!
            quarkx.console()
            del self.next
        else:
            qquake.BatchConsole.close(self)


class CloseConsole:
    def run(self):
        if self.console:
            print "Finished !"
        quarkx.console(self.console)



def checkfilename(filename):
    filename = filter(lambda c: c in r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$%'-_@{}~`!#()", filename)
    return filename or Strings[180]


def writemapfile(root, mapname, selonly, wadfile, hxstr=None, group=None):
    saveflags = 0
    if MapOption("IgnoreToBuild"):
        saveflags = saveflags | SO_IGNORETOBUILD
#    if MapOption("DisableEnhTex"):
#        saveflags = saveflags | SO_DISABLEENHTEX
    if MapOption("DisableFPCoord"):
        saveflags = saveflags | SO_DISABLEFPCOORD
#    if MapOption("EnableBrushPrim"):
#        saveflags = saveflags | SO_ENABLEBRUSHPRIM
    if MapOption("UseIntegralVertices"):
         saveflags = saveflags | SO_USEINTEGRALVERTICES
    if selonly:
        saveflags = saveflags | SO_SELONLY
    setup = quarkx.setupsubset()
    mapext = setup["MapExt"]
    if not mapext:
        mapext = '.map'
    mapfullname = mapname + mapext
    m = quarkx.newfileobj(mapfullname)

    if group == "":
        m.filename = quarkx.outputfile("%s/%s" % (quarkx.getmapdir(), mapfullname))
    else:
        m.filename = quarkx.outputfile("%s/%s/%s" % (quarkx.getmapdir(), group, mapfullname))
    worldspawn = root.copy(1)   # preserve selection while copying
    m["Root"] = worldspawn.name
    m.setint("saveflags", saveflags)
    m.appenditem(worldspawn)
    if wadfile:
        worldspawn["wad"] = wadfile
    if hxstr:
        m["hxstrings"] = hxstr
    m.savefile()
    return hxstr and m["hxstrings"]


def filesformap(map):
    setup = quarkx.setupsubset()
    map = "%s/%s" % (quarkx.getmapdir(), map)
    mapholes = setup["MapHoles"]
    if not mapholes:
        mapholes = ".lin"
    normal_files = [map+".bsp", map+mapholes]
    e1 = setup["PakExtra1"]
    if e1:
      normal_files = normal_files + [ map + e1 ]
    return normal_files


#def FirstBuildCmd():
#    setup = quarkx.setupsubset()
#    if setup["FirstBuildCmd"]:
#        return setup["FirstBuildCmd"]
#    else:
#        return "QBSP1"

def qmenuitem1click(m):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    if m.info["SelOnly"] and not len(editor.layout.explorer.sellist):
        quarkx.msgbox(Strings[223], MT_ERROR, MB_OK)
        return
#    if MapOption("AutoCheckMap", SS_MAP):
#        setup = quarkx.setupsubset()
#        if setup["NoMapChecks"]!="1":
#            import mapsearch
#            if mapsearch.CheckMap() == 0:
#                return
    if m.info["RunGame"]:
        setup = quarkx.setupsubset(SS_GENERAL, "3D View")
        if setup["CloseOnGame"]:
            editor.layout.mpp.viewpage(0)
            for floating in editor.layout.Floating3DWindows:
              floating.close()
    RebuildAndRun([(editor.fileobject, editor.Root, m.info)], editor,
      m.info["RunGame"], m.text, 0, [], "", None)


def RebuildAndRun(maplist, editor, runquake, text, forcepak, extracted, cfgfile, defaultbsp):

    #
    # Turn the "extracted" to lowercase.
    #
    for i in range(len(extracted)):
        extracted[i] = extracted[i].lower()

    #
    # First, extract all textures and compute .map file names.
    #
    if editor is None:
        texsrc = None
    else:
        texsrc = editor.TexSource

    setup = quarkx.setupsubset()
    newlist = []
    textures = {}
    texwarning = 0
    texwarninglist = ""
    gameneedwad = setup["GameNeedWad"]


    for mapfileobject, root, buildmode in maplist:

        if buildmode["ExportMapFile"]:
            if MapOption("AutoCheckMap", SS_MAP):
                if setup["NoMapChecks"]!="1":
                    import mapsearch
                    if mapsearch.CheckMap() == 0:
                        return

        map = checkfilename(mapfileobject["FileName"] or mapfileobject.shortname)
        map = map.lower()
        mapinfo = {"map": map}
        if buildmode["ExportMapFile"] \
        or buildmode["BuildPgm1"] \
        or buildmode["BuildPgm2"] \
        or buildmode["BuildPgm3"] \
        or buildmode["BuildPgm4"] \
        or buildmode["BuildPgm5"] \
        or buildmode["BuildPgm6"] \
        or buildmode["BuildPgm7"] \
        or buildmode["BuildPgm8"] \
        or buildmode["BuildPgm9"]:
            bspfile = quarkx.outputfile("%s/%s.bsp" % (quarkx.getmapdir(), map))
            if bspfile in extracted:
                continue
            extracted = extracted + filesformap(map)
            newlist.append((mapfileobject, root, buildmode, mapinfo))
        #
        # Find textures used in map
        #
        if buildmode["Textures"] or gameneedwad:
            list2 = quarkx.texturesof([root])
        if gameneedwad:
            texwad = "%s.wad" % map
            list = []
            wadlist = {}
            for t in list2:
                t1 = quarkx.loadtexture(t)
                if t1 is None:
                    texwarning = texwarning + 1
                    if len(texwarninglist):
                        texwarninglist = texwarninglist + ", "
                    texwarninglist = texwarninglist + "%s" % t
                elif (t1.type == '.wl') and t1["h"]:        # Half-Life texture link
                    wadlist["../"+t1["s"]+"/"+t1["d"]+".wad"] = None
                else:
                    list.append(t)
            list2 = list
            if len(list2):
                wadlist[texwad] = None
            mapinfo["wad"] = ';'.join(wadlist.keys())
        else:
            texwad = setup["TextureWad"]
            mapinfo["wad"] = texwad
        if buildmode["Textures"] and len(list2):
            try:       # put the textures in the list of textures to extract
                texlist = textures[texwad]
            except:
                texlist = []
                textures[texwad] = texlist
            for t in list2:
                if not (t in texlist):
                    texlist.append(t)

    if texwarning:
        errtext = Strings[-103] % texwarning
        errtext = errtext + "\n\n" + texwarninglist
        if quarkx.msgbox(errtext, MT_WARNING, MB_OK_CANCEL) != MR_OK:
            return

    texcount = None
    for texwad, texlist in textures.items():
        if gameneedwad:
            setup["TextureWad"] = texwad
        list2 = quarkx.maptextures(texlist, 2, texsrc)    # extract the textures
        texlist = len(texlist)
        list2 = len(list2)
        if texcount is not None:
            texlist = texlist + texcount[0]
            list2 = list2 + texcount[1]
        texcount = (texlist, list2)

    if gameneedwad:
        setup["TextureWad"] = "?"
    if texcount is None:    # extract at least the base files
        quarkx.maptextures([], 2)

    #
    # Precompute a few variables.
    #
    outputfilepath = quarkx.outputfile("")
    if outputfilepath[-1]=='\\':
        outputfilepath = outputfilepath[:-1]
    consolecloser = CloseConsole()   # close or reopens the console at the end
    consolecloser.console = len(maplist) and maplist[-1][2]["Pause"]
    next = consolecloser
    missing = ""
    hxstr = ""
    hxstrfile = setup["HxStrings"]
    if hxstrfile and len(maplist):
        try:
            hxstr = quarkx.needgamefile(hxstrfile)["Data"]
            extracted.append(hxstrfile.lower())
        except:
            pass

    if runquake or len(extracted):
        if runquake:    # if we have to run the game
            if defaultbsp:
                map = defaultbsp
            elif len(newlist):
                map = newlist[0][3]["map"]
            elif len(maplist)==1:
                map = mapinfo["map"]
            else:
                map = qquake.GameConsole.NO_MAP
                cfgfile = cfgfile + "echo\necho \"No map to begin with.\"\necho \"To choose a map, type: map <filename>\"\n"
        else:
            map = qquake.GameConsole.DONT_RUN
        next = qquake.GameConsole(map, extracted, cfgfile, forcepak, next)

    #
    # Loop through the maps to rebuild.
    #

    newlist.reverse()
    for mapfileobject, root, buildmode, mapinfo in newlist:

        map = mapinfo["map"]
        bspfile = quarkx.outputfile("./%s/%s.bsp" % (quarkx.getmapdir(), map))

        for pgrmnbr in range(9,0,-1):
            pgrmx = "BuildPgm%d" % pgrmnbr

            if buildmode[pgrmx]:        # Should this program be run?
                cmdline = setup[pgrmx]

                console = BuildPgmConsole_Advanced

                # Check first Default build-tool directory
                if setup["BuildPgmsDir"] is None:
                   cmdline2 = cmdline
                else:
                   cmdline2 = setup["BuildPgmsDir"] + "\\" + cmdline
                if (not quarkx.getfileattr(cmdline2)==FA_FILENOTFOUND):
                    # Success, use this build-tool!
                    cmdline = cmdline2

                if (not cmdline) or (quarkx.getfileattr(cmdline)==FA_FILENOTFOUND):
                    desc = setup["BuildDesc%d" % pgrmnbr] or cmdline or pgrmx
                    missing = "     %s\n%s" % (desc, missing)
                else:
                    # Prepare to run this program
                    cmdline = '"%s"' % cmdline
                    pgrmcmd = "BuildArgs%d" % pgrmnbr

                    # Create list of file-extensions to check for existance/non-existance after build
                    checkextensions = []
                    p1 = setup["BuildCheck%d" % pgrmnbr]
                    if p1: checkextensions = CreateCheckFileExtensionArray(p1)

                    # Fixed command-line arguments
                    p1 = setup[pgrmcmd]
                    if p1: cmdline = cmdline + " " + p1

                    # Additional command-line arguments
                    p1 = buildmode[pgrmcmd]
                    if p1: cmdline = cmdline + " " + p1

                    # Add %mapfile% if there is no filename-string present
                    if (cmdline.find("%mapfile%") == -1) and (cmdline.find("%file%") == -1) and (cmdline.find("%filename%") == -1) and (cmdline.find("%mapfile_wrongslash%") == -1):
                      cmdline = cmdline + " %mapfile%"

                    # Search and replace any user-variable
                    cmdline, toolworkdir = quarkx.resolvefilename(cmdline, FT_TOOL, map, mapfileobject)

                    # Put this build-program last in execution queue
                    next = console(cmdline, toolworkdir, bspfile, editor, next, checkextensions)

        if missing:
            msg = "%s\n%s" % (missing, Strings[5586])
            if quarkx.msgbox(msg, MT_CONFIRMATION, MB_YES | MB_NO) == MR_YES:
                quarkx.openconfigdlg(":")
            return

        if buildmode["ExportMapFile"]:
            if setup["UseQrkGroupFolder"]:
                group = argument_grouppath
            else:
                group = ""
            hxstr = writemapfile(root, map, buildmode["SelOnly"], mapinfo["wad"], hxstr, group)

    if hxstr:
        hxf = quarkx.newfileobj("hxstr.txt")
        hxf["Data"] = hxstr
        del hxstr
        hxf.savefile(quarkx.outputfile(hxstrfile))
        del hxf

    #
    # AutoSave
    #
    if quarkx.setupsubset(SS_MAP, "Building")["AutoSaveRun"] and editor is not None:
        editor.AutoSave()

    #
    # Run the above queued programs in the console.
    #

    if next is not consolecloser:
        print ""
        str = " " + filter(lambda c: c!="&", text) + " "
        l = (79-len(str))/2
        if l>0:
            str = "_"*l + str + "_"*l
        print str
        print
        if qquake.BuildConsole():
            quarkx.console()
        next.run()    # do it !

    elif texcount is not None:
        target = setup["TextureWad"] or setup["TexturesPath"]
#        quarkx.msgbox(target,2,4)
        target = quarkx.outputfile(target)
#        quarkx.msgbox(target,2,4)
        c1,c2 = texcount
        if c1<c2:
            msg = Strings[5590] % (c2, target, c2-c1)
        else:
            msg = Strings[5589] % (c2, target)
        quarkx.msgbox(msg, MT_INFORMATION, MB_OK)

    else:
        quarkx.msgbox(Strings[5653], MT_INFORMATION, MB_OK)


def Customize1Click(mnu):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    setup = quarkx.setupsubset()
    if setup["SpecialCustomQuakeMenu"]:
        form1 = setup["SpecialCustomQuakeMenu"]
    else:
        form1 = "CustomQuakeMenu"
    gamename = setup.shortname
    group = quarkx.newobj("%s menu:config" % gamename)
    sourcename = "UserData %s.qrk" % gamename
    file = LoadPoolObj(sourcename, quarkx.openfileobj, sourcename)
    ud = file.findname("Menu.qrk")
    for p in ud.subitems:
        txt = p["Txt"]
        ci = quarkx.newobj("%s.toolbar" % txt)
        ci.copyalldata(p)
        ci["Form"] = (form1, "CustomQuakeMenuSep")[txt=="-"]
        group.appenditem(ci)
    #explorer.addroot(group)
    newitem = quarkx.newobj("menu item.toolbar")
    newitem[";desc"] = "create a new menu item"
    newitem["Form"] = form1
    newsep = quarkx.newobj("-.toolbar")
    newsep[";desc"] = "create a new separator"
    newsep["Form"] = "CustomQuakeMenuSep"
    if quarkx.openconfigdlg("Customize %s menu" % gamename, group, [newsep, newitem]):
        for i in range(ud.itemcount-1, -1, -1):
            ud.removeitem(i)
        for ci in group.subitems:
            p = quarkx.newobj("item:")
            p.copyalldata(ci)
            p["Form"] = None
            p["Txt"] = ci.shortname
            ud.appenditem(p)
        editor.initmenu(quarkx.clickform)
        file.savefile()


def loadLeakFile(m):
    import mapholes
    mapholes.LoadLinFile(m.editor, m.auxfilename)

leakMenuItem = qmenu.item("Load Leak&file",loadLeakFile,hint="|Loads the leak file, if there is one.\n\nYou are responsible for making sure that the leak file actually belongs to the map you're working on (the build tools will delete previous leak files after a successful compile, but it is still possible to get confused, if you start a new map with the same name as an older one with a leak).\n\nThe thickness of the 'Leak line' that will be drawn can be changed by going to the 'Options' menu and selecting the 'Set Line Thickness' function.|intro.mapeditor.menu.html#gamemenu")


def loadPortalFile(m):
    import mapportals
    mapportals.LoadPortalFile(m.editor, m.auxfilename)

portalsMenuItem = qmenu.item("Load Portal&file",loadPortalFile,hint="|Loads the portals file, if there is one.\n\nWhat the blue lines indicate is the 'windows' between the convex ('leaf nodes') that the bsp process carves the visible spaces of your map into. So you can investigate the effects of using detail and hint-brushes, etc to make your map more efficient and run better.\n\nYou are responsible for making sure that the portals (probably .prt) file actually belongs to the map you're working on, and are up-to-date.|intro.mapeditor.menu.html#gamemenu")


def prepAuxFileMenuItem(item,extkey,defext):
    editor=item.editor
    mapfileobject = editor.fileobject
    map = checkfilename(mapfileobject["FileName"] or mapfileobject.shortname)
    map = map.lower()
    mapfilename = "%s%s\\%s" % (quarkx.outputfile(''), quarkx.getmapdir(), map)
    auxextension = quarkx.setupsubset()[extkey]
    if not auxextension:
        auxextension=defext
    auxfilename = mapfilename+auxextension
    if quarkx.getfileattr(auxfilename)==FA_FILENOTFOUND:
        item.state = qmenu.disabled
    else:
        item.state = qmenu.normal
        item.editor = editor
        item.auxfilename = auxfilename

def BrushNumClick(m):
    import mapbrushnum
    mapbrushnum.LoadBrushNums(m.editor, m.auxfilename)

brushnumsMenuItem = qmenu.item("Select Brush Number",BrushNumClick,"|Select Brush Number:\n\nTries to find brushes by number, as specified in compile tool error messages (the use of duplicators, etc. might subvert this).\n\nSee the infobase for more detailed explanations on how to use this function.|maped.builderrors.console.html")


def onclick(m):
    for args in ((leakMenuItem,"MapHoles",".lin"),
                 (portalsMenuItem,"MapPortals",".prt"),
                 (brushnumsMenuItem,"MapFileExt",".map"), # this options keyword doesn't exist
                 ):
      apply(prepAuxFileMenuItem,args)

def QuakeMenu(editor):
    "The Quake menu, with its shortcuts."

     # this menu is read from UserData.qrk.

    items = []
    sc = {}
    gamename = quarkx.setupsubset().shortname
    #firstcmd = FirstBuildCmd()
    sourcename = "UserData %s.qrk" % gamename
    ud = LoadPoolObj(sourcename, quarkx.openfileobj, sourcename)
    ud = ud.findname("Menu.qrk")
    if ud is not None:
        for p in ud.subitems:
            txt = p["Txt"]
            if txt=="-":
                items.append(qmenu.sep)
            else:
                m = qmenu.item(txt, qmenuitem1click, "|The commands in this menu lets you run your map with the game. The most common commands are the first few ones, which lets you try your map as a one-step operation.\n\nBefore a map can be played, it must be compiled (translated into a .bsp file). This is done by other programs that QuArK will call for you. See the Configuration dialog box, under the page of the game you wish to map for, where you must tell QuArK where these build programs are installed. The programs themselves are available in Build Packs, one for each game you want to make maps for, and that can be downloaded from http://dynamic.gamespy.com/~quark/.|intro.mapeditor.menu.html#gamemenu")
                m.info = p
                #if IsBsp(editor) and p[firstcmd]:
                #    m.state = qmenu.disabled
                #elif p["Shortcut"]:
                if p["Shortcut"]:
                    sc[p["Shortcut"]] = m
                items.append(m)
        items.append(qmenu.sep)
        for item in (leakMenuItem, portalsMenuItem, brushnumsMenuItem):
            item.editor=editor
            items.append(item)
        items.append(qmenu.sep)
        items.append(qmenu.item("&Customize menu...", Customize1Click, "customizes this menu"))
    Quake1 = qmenu.popup("&"+gamename, items, onclick)
    Quake1.state = not len(items) and qmenu.disabled
    return Quake1, sc


# ----------- REVISION HISTORY ------------
#
#$Log: mapquakemenu.py,v $
#Revision 1.63  2012/10/07 17:57:35  danielpharos
#Workaround for SOF1 tools needing the wrong slashes.
#
#Revision 1.62  2011/07/31 12:07:55  danielpharos
#Removed bad try-except, and fixed file-groups not working properly.
#
#Revision 1.61  2010/02/21 15:42:49  danielpharos
#Fixed orangebox compiler not finishing compile.
#
#Revision 1.60  2008/11/17 19:10:23  danielpharos
#Centralized and fixed BSP file detection.
#
#Revision 1.59  2008/10/08 21:42:12  danielpharos
#Made map extension changable.
#
#Revision 1.58  2008/09/29 23:16:38  danielpharos
#Resolve-code: Another fix. This should get Steam-games compiling and running again.
#
#Revision 1.57  2008/09/29 22:01:56  danielpharos
#Update to filename resolving code. Needs more testing, but should work.
#
#Revision 1.56  2008/09/29 21:08:55  danielpharos
#Update filename resolving code. Still untested.
#
#Revision 1.55  2008/09/27 12:08:57  danielpharos
#Added Steam %-replace texts. Still experimentally.
#
#Revision 1.54  2008/09/26 20:08:46  danielpharos
#Small changes to path-code, to make it more consistent.
#
#Revision 1.53  2008/09/26 20:07:34  danielpharos
#Removed empty parameter option for outputfile().
#
#Revision 1.52  2008/08/18 20:18:20  danielpharos
#Removed a redundant import.
#
#Revision 1.51  2007/08/21 20:34:35  danielpharos
#Another of mine upload-mistakes. I think I should have my brains checked :|
#
#Revision 1.50  2007/08/21 10:26:34  danielpharos
#Small changes to let HL2 build again.
#
#Revision 1.49  2007/04/16 11:24:15  danielpharos
#Changed some directory routines: tmpQuArK isn't hardcoded anymore.
#
#Revision 1.48  2007/03/27 15:48:58  danielpharos
#Re-added the ability to open multiple floating 3D windows! This time there's an option to toggle it on and off in the options.
#
#Revision 1.47  2006/11/30 01:19:33  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.46  2006/11/29 07:00:26  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.45.2.6  2006/11/01 22:22:41  danielpharos
#BackUp 1 November 2006
#Mainly reduce OpenGL memory leak
#
#Revision 1.45  2006/08/11 23:13:47  cdunde
#New feature by Jari, create folder(s) like qrk tree to store compiled files in.
#Tools must have output option setting like Torque to work.
#
#Revision 1.44  2006/05/07 07:02:07  rowdy
#Added a rough hack to allow %file% type substitution in the '<game> command-line' option.  Also added %filename% parameter that is replaced with the map filename (without path, without extension).
#
#Revision 1.43  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.40  2005/04/16 11:13:36  alexander
#can save non alpha textures as vtf
#can export used textures to materials folder
#
#Revision 1.39  2005/01/05 12:18:35  alexander
#introduced %gamedir% variable expansion for running tools and utilized for hl2 support
#
#Revision 1.38  2004/01/08 08:54:33  cdunde
#To commit changes for peter-b
#
#Revision 1.37  2003/12/17 13:58:59  peter-b
#- Rewrote defines for setting Python version
#- Removed back-compatibility with Python 1.5
#- Removed reliance on external string library from Python scripts
#
#Revision 1.36  2003/03/28 16:09:23  cdunde
#More infobase updates
#
#Revision 1.35  2003/03/27 20:35:48  cdunde
#Update info and links to infobase.
#
#Revision 1.34  2003/03/24 10:34:24  tiglari
#support for brush-number finder
#
#Revision 1.33  2003/03/21 05:56:26  cdunde
#Update infobase and add links
#
#Revision 1.32  2003/03/19 22:27:58  tiglari
#change default holes file to .lin
#
#Revision 1.31  2003/03/19 11:24:32  tiglari
#expand help for portal view command
#
#Revision 1.30  2003/03/19 11:06:54  tiglari
#add commands for loading leak (pts/lin) and portal (prt) files
#
#Revision 1.29  2003/03/17 00:11:05  tiglari
#Add manual leak file loading command
#
#Revision 1.28  2003/01/06 22:24:02  tiglari
#check leak files for having actual content before registering build error
#
#Revision 1.27  2002/08/09 10:01:45  decker_dk
#Fixed problem, when "warning about missing textures and do you want to continue"
#never continued regarding pressing OK or Cancel. The if-statement checked for MR_YES
#and not MR_OK.
#
#Revision 1.26  2002/05/07 09:13:02  tiglari
#prevent error when no default dir for buildpgms is specified (diagnosis and fix by nurail)
#
#Revision 1.25  2002/04/28 11:41:32  tiglari
#New command line argument substitutions (for RTCW)
#
#Revision 1.24  2002/03/26 22:19:20  tiglari
#support UseIntegralVertexes flag
#
#Revision 1.23  2002/02/05 18:33:15  decker_dk
#Added a %basepath% command-line replacement variable.
#
#Revision 1.22  2001/09/24 22:24:27  tiglari
#checks moved into RebuildandRun, made conditional on ExportMapFile
#
#Revision 1.21  2001/07/24 02:42:40  tiglari
#.hmf extension when 6dx maps committed
#
#Revision 1.20  2001/07/19 12:00:17  tiglari
#support disabling mapchecks in game config files
#
#Revision 1.19  2001/03/18 12:17:26  decker_dk
#Fixed FindSingleExtension() so it also reads the last extension at end-of-line.
#
#Revision 1.18  2001/03/15 20:53:53  tiglari
#fix for no action build control parameters (Q1/H2)
#
#Revision 1.17  2001/03/14 19:20:49  decker_dk
#Functionality for '-ext{action}'... which is not documented yet!
#
#Revision 1.16  2001/03/12 15:31:39  tiglari
#Hacked in linfile loading. Assumes that .lin/.pts is the only must-not-exist file,
#  which is true for now, but prolly not reliable.  better fix wanted
#
#Revision 1.15  2001/02/07 00:08:33  aiv
#added fixes from 6.1c release
#
#Revision 1.14  2001/01/27 18:24:39  decker_dk
#Renamed the key 'Q2TexPath' to 'TexturesPath'.
#
#Revision 1.13  2000/10/28 19:29:38  decker_dk
#Correctly export .MAP file, even if no build-tool is marked for execution
#
#Revision 1.12  2000/10/26 18:15:45  tiglari
#Enable Brush Primitives support
#
#Revision 1.11  2000/10/19 19:00:42  decker_dk
#Fix if 'BuildPgmsDir' was not filled out
#
#Revision 1.10  2000/10/09 18:18:02  decker_dk
#Build-Tool Controllers
#
#Revision 1.9  2000/07/24 23:58:11  alexander
#added: .lin file processing for bspc leaks
#
#Revision 1.8  2000/07/03 14:10:50  alexander
#fixed: removed unnecessary dialogs when extract textures
#
#Revision 1.7  2000/06/07 22:29:19  alexander
#changed: use the setup entry "SpecialCustomQuakeMenu" instead of
#         the NEEDQCSG flag to select a form for custom quake menus
#fixed: check now if aas file was built at all
#
#Revision 1.6  2000/06/05 00:11:27  alexander
#fixed history
#
#Revision 1.5  2000/06/05 00:09:49  alexander
#added: kludge for stupid tools (like those of SoF) that require to run in the games base dir)
#
#Revision 1.4  2000/06/04 21:41:29  alexander
#added: bspc console class, support for running the bsp to aas converter for bots in q3
#
#Revision 1.3  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#
