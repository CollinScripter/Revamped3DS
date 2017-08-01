"""   QuArK  -  Quake Army Knife

Various constants and routines
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#


#$Header: /cvsroot/quark/runtime/quarkpy/qutils.py,v 1.58 2011/05/26 22:59:26 cdunde Exp $

import quarkx

# a few colors
BLACK     = 0x000000
MAROON    = 0x000080
GREEN     = 0x008000
OLIVE     = 0x008080
NAVY      = 0x800000
PURPLE    = 0x800080
TEAL      = 0x808000
GRAY      = 0x808080
SILVER    = 0xC0C0C0
RED       = 0x0000FF
LIME      = 0x00FF00
YELLOW    = 0x00FFFF
BLUE      = 0xFF0000
FUCHSIA   = 0xFF00FF
AQUA      = 0xFFFF00
LTGRAY    = 0xC0C0C0
DKGRAY    = 0x808080
WHITE     = 0xFFFFFF
NOCOLOR   = 0x1FFFFFFF    # for map view backgrounds and model components

# panels 'align' values
LEFT      = "left"
RIGHT     = "right"
TOP       = "top"
BOTTOM    = "bottom"
FULL      = "full"
NOALIGN   = None

# toolbars 'dock' values
TOPDOCK   = "topdock"
BOTTOMDOCK= "bottomdock"
LEFTDOCK  = "leftdock"
RIGHTDOCK = "rightdock"
NODOCK    = None

# window states
RESTORED  = 0       # normal
MINIMIZED = 1
MAXIMIZED = 2

# filedialogbox
SAVEDIALOG     = 1   # These have to match Delpih's TOpenOptions flags, except for '1', which is overwritten in QuarkX.pas
MULTIPLEFILES  = 64

# setupset
SS_GENERAL     = 0   # These have to match the ones in Setup.pas
SS_GAMES       = 1
SS_MAP         = 2
SS_MODEL       = 3
SS_TOOLBARS    = 4
SS_FILES       = 5
#SS_TEMP        = 6

# floating windows flags
FWF_NOCAPTION  = 1
FWF_NOCLOSEBOX = 2
FWF_NORESIZE   = 4
FWF_POPUPCLOSE = 8
FWF_NOESCCLOSE = 16
FWF_KEEPFOCUS  = 32

# internal objects' "flags" value !!! WARNING !!! DO NOT MODIFY unless you know what you're doing !
OF_TVSUBITEM         = 1   # all objects in a tree-view except top-level
OF_TVINVISIBLE       = 2   # present but invisible in the tree-view
OF_TVALREADYEXPANDED = 4   # node has been expanded once
OF_TVEXPANDED        = 8   # node is expanded
OF_ONDISK            = 16  # has not been loaded yet (loading is automatic when Python code reads the object's Specifics or sub-items)
OF_FILELINK          = 32  # is a file link
OF_WARNBEFORECHANGE  = 64  # warn the user before he makes changes
OF_MODIFIED          = 128 # modified by the user

# values of the ';view' Specific (as text) of TreeMapGroup objects
# !! Must match the constants in QkMapObjects.PAS !!
VF_GRAYEDOUT        = 1    # whole group is grayed out
VF_HIDDEN           = 2    # whole group is hidden
VF_IGNORETOBUILDMAP = 4    # the group is ignored when writing the .map file with the SO_IGNORETOBUILD flag
VF_HIDEON3DVIEW     = 8    # not displayed on textured views
VF_CANTSELECT       = 16   # the objects in this group can't be selected by clicking on the map view

# values of the 'saveflags' Specific (as integer) of Map objects, to control how it should be saved
# !! Must match the constants in QkMapObjects.PAS !!
SO_SELONLY         = 1    # only the selection is saved
SO_IGNORETOBUILD   = 2    # the groups marked VF_IGNORETOBUILDMAP are not saved
#SO_DISABLEENHTEX   = 4    # don't write the "//TX1"-style comments required by TXQBSP for enhanced texture positionning
SO_DISABLEFPCOORD  = 8    # don't write floating-point coordinates in .map files, round all values
#SO_ENABLEBRUSHPRIM = 16   # enable brush primitives format
SO_USEINTEGRALVERTICES = 64 # use integral vertices as threepoints if possible

# values of the saveflags for savefileobj (must be same as in QkFileObjects.pas!)
FM_Save           = 1;
FM_SaveAsFile     = 2;
FM_SaveIfModif    = 3;
FM_SaveTagOnly    = 4;

# values of FileType parameter for resolvefilename (must be same as in QuarkX.pas!)
FT_ANY  = 0;
FT_GAME = 1;
FT_TOOL = 2;
FT_PATH = 3;

# log constants
# !! Must match the constants in Logging.PAS !!
LOG_ALWAYS   = 0;
LOG_CRITICAL = 10;
LOG_WARNING  = 20;
LOG_INFO     = 30;
LOG_VERBOSE  = 40;

# icon indexes of internal objects (to be used with quarkx.seticons)
iiUnknownFile           = 0
iiExplorerGroup         = 1
iiQuakeC                = 2
iiBsp                   = 3
iiToolBox               = 4
iiUnknown               = 5
iiPakFolder             = 6
iiLinkOverlay           = 7
iiModel                 = 8
iiMap                   = 9
iiPak                   = 10
iiEntity                = 11
iiBrush                 = 12
iiGroup                 = 13
iiDuplicator            = 14
iiPolyhedron            = 15
iiFace                  = 16
iiCfgFolder             = 17
iiCfg                   = 18
iiInvalidPolyhedron     = 19
iiInvalidFace           = 20
iiNewFolder             = 21
iiWad                   = 22
iiTexture               = 23
iiTextureLnk            = 24
iiPcx                   = 25
iiQuArK                 = 26
iiTexParams             = 27
iiQme                   = 28
iiToolbar               = 29
iiToolbarButton         = 30
 # iiFrameGroup            = 31
 # iiSkinGroup             = 32
 # iiSkin                  = 33
iiGroupXed              = 31
iiGroupHidden           = 32
iiGroupHiddenXed        = 33
iiFrame                 = 34
iiComponent             = 35
iiModelGroup            = 36
iiQCtx                  = 37
iiWav                   = 38
iiCin                   = 39
iiText                  = 40
iiCfgFile               = 41
iiImport                = 42
iiPython                = 43
iiBezier                = 44
#Sprite File Support
iiSprFile               = 45
iiMD3Tag                = 46
iiMD3Bone               = 47
iiFormElement           = 48
iiForm                  = 49
iiFormContext           = 50

iiTotalImageCount       = 51



def LoadIconSet(filename, width, transparencypt=(0,0)):
    "Load a set of bitmap files and returns a tuple of image lists."

    def loadset(tag, filename=filename, width=width, transparencypt=transparencypt, setup=quarkx.setupsubset(SS_GENERAL, "Display"), cache={}):
        if setup[tag]:
            ext = "-1.bmp"
        else:
            ext = "-0.bmp"
        try:
            return cache[ext]
        except:
            img = quarkx.loadimages(filename + ext, width, transparencypt)
            cache[ext] = img
            return img

    # load the unselected version of the icons
    unsel = loadset("Unsel")

    # load the selected version of the icons
    sel = loadset("Sel")

    # load xxx-2.bmp, the triggered version for on/off buttons
    try:
        trig = quarkx.loadimages(filename + "-2.bmp", width, transparencypt)
        return (unsel, sel, trig)
    except quarkx.error:
        return (unsel, sel)


#
# equiv to LoadIconSet, just calls a different loadimages
#  to help in leak-tracking
#
def LoadIconSet2(filename, width, transparencypt=(0,0)):
    "Load a set of bitmap files and returns a tuple of image lists."

    def loadset(tag, filename=filename, width=width, transparencypt=transparencypt, setup=quarkx.setupsubset(SS_GENERAL, "Display"), cache={}):
        if setup[tag]:
            ext = "-1.bmp"
        else:
            ext = "-0.bmp"
        try:
            return cache[ext]
        except:
            img = quarkx.loadimages(filename + ext, width, transparencypt)
            cache[ext] = img
            return img

    # load the unselected version of the icons
    unsel = loadset("Unsel")

    # load the selected version of the icons
    sel = loadset("Sel")

    # load xxx-2.bmp, the triggered version for on/off buttons
    try:
        trig = quarkx.loadimages(filename + "-2.bmp", width, transparencypt)
        return (unsel, sel, trig)
    except quarkx.error:
        return (unsel, sel)


def LoadIconSet1(filename, width, transparencypt=(0,0)):
    return LoadIconSet(quarkx.setupsubset(SS_GENERAL, "Display")["IconPath"]+filename, width, transparencypt)


#
# Map modules loader (map*.py modules require a special load order)
#
def loadmapeditor(what=None):
    global loadmapeditor
    import maputils
    import mapeditor
    import mapmenus
    #---- import the plug-ins ----
    import plugins
    plugins.LoadPlugins("MAP")

    def reLoad(what=None):
        #---- import the bezier plug-ins if so stated in Defaults.QRK ----
        #---- and bsp support if we're editing a bsp
        import quarkx
        if what=='bsp':
            plugins.LoadPlugins("BSP")

        beziersupport = quarkx.setupsubset()["BezierPatchSupport"]
        if (beziersupport is not None) and (beziersupport == "1"):
            pluginprefixes = quarkx.setupsubset()["BezierPatchPluginPrefixes"]
            if (pluginprefixes is None) or (pluginprefixes == ""):
                raise "Serious failure in quarkpy.qutils.loadmapeditor: Missing specific-value 'BezierPatchPluginPrefixes' in Defaults.QRK"
            loadmapeditor = lambda: None # next calls to loadmapeditor() do nothing. Everything is now loaded!
            import mapbezier
            for prefix in pluginprefixes.split():
                plugins.LoadPlugins(prefix.strip())

    # force an initial load of bezier-support, if any for the current game-mode.
    reLoad(what)
    # next call to loadmapeditor, will check to see if there is a new need to load
    # bezier/bsp-support, when/if the user changes game-mode in QuArK explorer.
    loadmapeditor = reLoad

#
# Model modules loader (mdl*.py modules require a special load order)
#
def loadmdleditor():
    global loadmdleditor
    loadmdleditor = lambda: None    # next calls to loadmdleditor() do nothing
    import mdlutils
    import mdleditor
    import mdlmenus
    # --- import the importers/exporters if they haven't been loaded yet
    import qmacro
    qmacro.MACRO_loadmdlimportexportplugins(None)
    #---- import the plug-ins ----
    import plugins
    plugins.LoadPlugins("MDL")


#
# Icon sets that aren't always loaded should go into this
#   dictionary, indexed by their names.  The dictionary
#   is cleaned up in qmacro.MACRO_shutdown to avoid
#   live pointer memory leaks.
#
ico_dict = {}

#
# Putting these two in the ico_dict doesn't achieve
#  any purpose (lots of code gets clunkier, no benefit)
#
# Default icons for the objects
ico_objects = LoadIconSet("images\\objects", 16)

# Generic editor icons
ico_editor = LoadIconSet("images\\editor", 16)

# Note: There are also some icon-loading calls in qeditor.py; search for "Icons for the layout of the Map/Model Editor"


#
# Variable icons handlers for Quake entities
#

def EntityIcon(entity, iconset):
    #
    # Sets the default icons for each entity type, by figuring out their type from their name.
    #
    if not ico_dict.has_key('ico_mapents'):
        ico_dict['ico_mapents'] = LoadIconSet("images\\mapents", 16)
    icons = ico_dict['ico_mapents'][iconset]
    #
    # Read the classname of the entity
    #
    name = entity.shortname
    #
    # Analyse the beginning of the classname
    #
    if name[:4]=="item" or name[:6]=="weapon" or name[:9]=="wp_weapon" or name[:4]=="art_":
        return icons[1]
    if name[:4]=="info":
        return icons[2]
    if name[:5]=="light":
        return icons[3]
    if name[:7]=="monster":
        return icons[0]
    return icons[4]

def EntityIconSel(entity):
    return EntityIcon(entity, 1)

def EntityIconUnsel(entity):
    return EntityIcon(entity, 0)


#
# Variable icons handlers for duplicators
#

def DuplicatorIconUnsel(dup):
    loadmapeditor()
    import mapduplicator
    iconlist, iconindex = mapduplicator.DupManager(dup).Icon
    if dup.name.startswith("Editor Std 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1":
            iconindex = 4
    elif dup.name.startswith("Editor True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] != "1":
            iconindex = 4
    elif dup.name.startswith("Full3D Standard"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1":
            iconindex = 4
    elif dup.name.startswith("Full3D True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] != "1":
            iconindex = 4
    return iconlist[0][iconindex]

def DuplicatorIconSel(dup):
    loadmapeditor()
    import mapduplicator
    iconlist, iconindex = mapduplicator.DupManager(dup).Icon
    if dup.name.startswith("Editor Std 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1":
            iconindex = 4
    elif dup.name.startswith("Editor True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] != "1":
            iconindex = 4
    elif dup.name.startswith("Full3D Standard"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1":
            iconindex = 4
    elif dup.name.startswith("Full3D True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] != "1":
            iconindex = 4
    return iconlist[1][iconindex]


#
# Variable icons handlers for groups
#

def GroupIconUnsel(grp, ico_objects_group_set={
  (0,0):ico_objects[0][iiGroupHidden],
  (0,1):ico_objects[0][iiGroup],
  (4,0):ico_objects[0][iiGroupHiddenXed],
  (4,1):ico_objects[0][iiGroupXed]}):
    if grp[";view"]:
        try:
            view = int(grp[";view"])
            return ico_objects_group_set[view&4, not (view&~4)]
        except:
            pass
    iiGroup = 13
    if grp.name.startswith("Editor Std 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1":
            iiGroup = 31
    elif grp.name.startswith("Editor True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] != "1":
            iiGroup = 31
    elif grp.name.startswith("Full3D Standard"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1":
            iiGroup = 31
    elif grp.name.startswith("Full3D True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] != "1":
            iiGroup = 31
    return ico_objects[0][iiGroup]

def GroupIconSel(grp, ico_objects_group_set={
  (0,0):ico_objects[1][iiGroupHidden],
  (0,1):ico_objects[1][iiGroup],
  (4,0):ico_objects[1][iiGroupHiddenXed],
  (4,1):ico_objects[1][iiGroupXed]}):
    if grp[";view"]:
        try:
            view = int(grp[";view"])
            return ico_objects_group_set[view&4, not (view&~4)]
        except:
            pass
    iiGroup = 13
    if grp.name.startswith("Editor Std 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] == "1":
            iiGroup = 31
    elif grp.name.startswith("Editor True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["EditorTrue3Dmode"] != "1":
            iiGroup = 31
    elif grp.name.startswith("Full3D Standard"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] == "1":
            iiGroup = 31
    elif grp.name.startswith("Full3D True 3D"):
        if quarkx.setupsubset(SS_MODEL, "Options")["Full3DTrue3Dmode"] != "1":
            iiGroup = 31
    return ico_objects[1][iiGroup]

#
# Variable icons handlers for Model objects
#

def ModelIcon(modelobj, iconset):

    #
    # Sets the default icons for each group type ex: ":sg", ":fg"...
    # Also individual component group type icons can be set here as well.
    # See the "EntityIcon" function above for examples.
    #
    if not ico_dict.has_key('mdlobjs'):
        ico_dict['mdlobjs'] = LoadIconSet("images\\mdlobjs", 16)
    icons = ico_dict['mdlobjs'][iconset]
    #
    # Figure out if this model group is hidden
    #
    DummyItem = modelobj
    while DummyItem is not None:
        if DummyItem.type == ":mr":
            DummyItem = None
            break
        if DummyItem.type == ":mc":
            # Found the parent component!
            break
        DummyItem = DummyItem.parent
    # If it is hidden, draw an X
    if DummyItem is not None:
        if DummyItem['show'] != chr(1):
            return ico_editor[iconset][0]

    # Needed to display the correct icons of these groups for imported models.
    if modelobj.type ==":bbg":
        if modelobj['show'][0] == 1.0:
            return icons[8]
        else:
            return icons[9]
    if modelobj.type ==":fg":
        return icons[1]
    if modelobj.type ==":bg":
        if quarkx.setupsubset(SS_MODEL, "Options")['HideBones'] is not None:
            return icons[7]
        return icons[5]

    #
    # Read the type tag of the model
    #
    tag = modelobj.getint("type")
    if tag < len(icons):
        return icons[tag]
    else:
        return ico_objects[iconset][iiUnknown]

def ModelGroupIconSel(obj):
    "This function is called from the Delphi code, QObject.DisplayDetails function,"
    "for which icon to use when the obj is selected."
    return ModelIcon(obj, 1)

def ModelGroupIconUnsel(obj):
    "This function is called from the Delphi code, QObject.DisplayDetails function,"
    "for which icon to use when the obj is un-selected."
    return ModelIcon(obj, 0)

#
# Variable icons handlers for Model component objects
#

def ComponentIcon(compobj, iconset):
    ##
    ## Sets the default icons for each component.
    ## Also individual component icons can be set here as well.
    ## See the "EntityIcon" function above for examples.
    ##
    #if not ico_dict.has_key('mdlobjs'):
    #    ico_dict['mdlobjs'] = LoadIconSet("images\\mdlobjs", 16)   CHANGE NAME!
    #icons = ico_dict['mdlobjs'][iconset]

    if compobj['show'] == chr(1):
        return ico_objects[iconset][iiComponent]
    else:
        return ico_editor[iconset][0]

def ComponentIconSel(obj):
    return ComponentIcon(obj, 1)

def ComponentIconUnsel(obj):
    return ComponentIcon(obj, 0)

#
# Variable icons handlers for Model bbox (poly:p) objects
#

def BBoxIcon(bbox, iconset):
    if not ico_dict.has_key('ico_objects'):
        ico_dict['ico_objects'] = LoadIconSet("images\\objects", 16)
    icons = ico_dict['ico_objects'][iconset]

    if bbox['show'][0] == 1.0:
        return icons[54]
    else:
        return icons[53]

def BBoxIconSel(bbox):
    import mdleditor
    if not isinstance(mdleditor.mdleditor, mdleditor.ModelEditor):
        return ico_objects[1][iiPolyhedron]
    return BBoxIcon(bbox, 1)

def BBoxIconUnsel(bbox):
    import mdleditor
    if not isinstance(mdleditor.mdleditor, mdleditor.ModelEditor):
        return ico_objects[0][iiPolyhedron]
    return BBoxIcon(bbox, 0)

#
# Variable icons handlers for Model bone objects
#

def BoneIcon(bone, iconset):
    if not ico_dict.has_key('ico_objects'):
        ico_dict['ico_objects'] = LoadIconSet("images\\objects", 16)
    icons = ico_dict['ico_objects'][iconset]

    if bone['show'][0] == 1.0:
        return icons[47]
    else:
        return icons[51]

def BoneIconSel(bone):
    return BoneIcon(bone, 1)

def BoneIconUnsel(bone):
    return BoneIcon(bone, 0)

#
# Variable icons handlers for Model tag objects
#

def TagIcon(tag, iconset):
    if not ico_dict.has_key('ico_objects'):
        ico_dict['ico_objects'] = LoadIconSet("images\\objects", 16)
    icons = ico_dict['ico_objects'][iconset]

    if not tag.dictspec.has_key("show"):
        tag['show'] = (1.0,)
    if tag['show'][0] == 1.0 and quarkx.setupsubset(SS_MODEL, "Options")['HideTags'] is None:
        return icons[46]
    else:
        return icons[52]

def TagIconSel(tag):
    return TagIcon(tag, 1)

def TagIconUnsel(tag):
    return TagIcon(tag, 0)


# quarkx.msgbox
MT_WARNING           = 0
MT_ERROR             = 1
MT_INFORMATION       = 2
MT_CONFIRMATION      = 3
MB_YES               = 1
MB_NO                = 2
MB_OK                = 4
MB_CANCEL            = 8
MB_ABORT             = 16
MB_RETRY             = 32
MB_IGNORE            = 64
MB_ALL               = 128
# MB_HELP            = 256
MB_YES_NO_CANCEL     = MB_YES | MB_NO | MB_CANCEL
MB_OK_CANCEL         = MB_OK | MB_CANCEL
MB_ABORT_RETRY_IGNORE= MB_ABORT | MB_RETRY | MB_IGNORE
MR_OK     = 1
MR_CANCEL = 2
MR_ABORT  = 3
MR_RETRY  = 4
MR_IGNORE = 5
MR_YES    = 6
MR_NO     = 7
MR_ALL    = 8

# "style" of ":form" objects (convert the numeric value into a string to assign to "style")
GF_GRAY       = 1
GF_EXTRASPACE = 2
GF_NOICONS    = 4
GF_NOBORDER   = 8

# file attributes
FA_READONLY     = 1
FA_HIDDEN       = 2
FA_ARCHIVE      = 32
FA_FILENOTFOUND = -1
FA_DELETEFILE   = -1


SetupRoutines = []

def SetupChanged(level):
    "Called by QuArK when the setup is modified."
    try:
        import mdleditor
        if isinstance(mdleditor.mdleditor, mdleditor.ModelEditor):
            import mdlmgr
            mdlmgr.treeviewselchanged = 0
        for s in SetupRoutines:
            s(level)
    except:
        for s in SetupRoutines:
            s(level)


#
# Pool Manager : when you read data that don't change, like icon
# bitmaps, you should store the result in the Pool so that if you
# need the data again you don't have to reload it. So instead of :
#     functionthatloadstuff(argument, ...)
# write :
#     LoadPoolObj(uniquestring, functionthatloadstuff, argument, ...)
#

def LoadPoolObj(tag, loadfn, *loadargs):
    "Retrieve the content of a pool object, or call a function if not found."

    obj = quarkx.poolobj(tag)
    if obj == None:
        obj = apply(loadfn, loadargs)
        quarkx.setpoolobj(tag, obj)
    return obj


def debug(text):
    import sys
    sys.stderr.write(text+"\n")
    # rowdy: debug logging
    #o = open('c:/rowdy/QuArK_debug.log', 'a')
    #o.write('%s\n' % text)
    #o.close()

def MapHotKey(keytag, keyfunc, menu):
    key = quarkx.setupsubset(SS_GENERAL,"HotKeys")[keytag]
    if key:
        menu.shortcuts[key] = keyfunc

def MapHotKeyList(keytag, keyfunc, list):
    key = quarkx.setupsubset(SS_GENERAL,"HotKeys")[keytag]
    if key:
        list[key] = keyfunc

def clearimagelist(list):
    for (im1, im2) in list:
        del im1
        del im2



#
# Utilities for accessing attributes of objects
#  (class instances) that might not be defined
#
def getAttr(object, attr, default=None):
    if hasattr(object, attr):
        return getattr(object,attr)
    else:
        return default

def delAttr(object, attr):
    if hasattr(object, attr):
         delattr(object, attr)

def appendToAttr(object, attr, thing):
    if hasattr(object, attr):
        getattr(object,attr).append(thing)
    else:
        setattr(object,attr,[thing])

def removeFromAttr(object, attr, thing):
    getattr(object,attr).remove(thing)
    if getattr(object,attr)==[]:
        delattr(object,attr)

def hintPlusInfobaselink(hint, url):
    if url:
        return "%s|%s"%(hint,url)
    return hint



#
# Texture and Color Utilities
# that can be used in both editors.
#

# Converts separate Red, Green, Blue color components into a long integer color.
def RGBToColor(RGB):
    RGB = (65536 * RGB[2]) + (256 * RGB[1]) + RGB[0]
    if RGB > 999999999:
        RGB = int(RGB*.1)
        quarkx.msgbox("RGB caused a long integer !\n\nThe file or function you have\njust used is causing this error\nin converting three R,G,B values\ninto a color integer number.\nThese values should range from 0 to 1.0\nas a percentage of 256 color per channel.\nCheck the file or function code and correct.", MT_ERROR, MB_OK)
    return RGB

# Converts long integer color number into separate color components Red Green Blue (RGB)
# Returns those components as a list of three integer numbers but backwards BGR
#   because that is how Windows and other image editing programs draw them.
def ColorToRGB(Color):
    return (int(round(Color / 65536)) & 255, int(round(Color / 256)) & 255, int(Color) & 255)

# Converts long integer color number into separate color components Red Green Blue (RGB)
# Reverses the R and the B values and returns the new color as a BGR color.
def SwapRandB(LongIntNbr):
    Color = ColorToRGB(LongIntNbr)
    TMPColor = Color[2]
    Color[2] = Color[0]
    Color[0] = TMPColor
    return RGBToColor(Color)

#---- import the plug-ins ----
import plugins
plugins.LoadPlugins("Q_")
#-----------------------------

#
# I got tired of guessing and testing what an internal object was and exactly what's in it.
# So I wrote this utility to test and print ALL that stuff to the QuArK console and
#    a hard copy in QuArK's main folder called "DEVELOPERS.txt" were you can copy Attributes
#    that can be added to the object and other output data for further testing and use.
#
# You can test an object by replacing objval's "None" value below with the object or argument.
# If the object is a class or def of a class you can also replace selfval's "None" with just "self"
#    as the 2nd argument to see what that is.
#
# If you change "openconsole" to 1 will open the console automatically when the test is done.
#
# I have found that sometimes "self" can be an item such as a "poly face", "vertex" or "vector"...
# That can be used directly to accomplish what you are trying to do.
#
# Copy the code below (change the argument val's as needed) to call it, align for proper white spaces:
#
# For quarkpy files copy the code below:
#
#      import qutils
#      objval = None
#      selfval = None
#      viewval = None
#      flagsval = None
#      openconsole = None # Replace None with 1 to open the console after testing automatically.
#      qutils.WhatIsThisObject(objval, selfval, viewval, flagsval, openconsole)
#
#
# For plugins files copy the code below:
#
#      import quarkpy.qutils
#      objval = None
#      selfval = None
#      viewval = None
#      flagsval = None
#      openconsole=None # Replace None with 1 to open the console after testing automatically.
#      quarkpy.qutils.WhatIsThisObject(objval, selfval, viewval, flagsval, openconsole)
#

def WhatIsThisObject(obj=None, self=None, view=None, flags=None, openconsole=None):
    import sys
    o = open("DEVELOPERS.txt", "w")
    print "-------------- start of test -------------"
    o.write("\n-------------- start of test -------------")
    if self is not None:
        sys.stderr.write("'self' is:")
        print" ",self
        o.write("\n\n'self' is:\n")
        o.write("  " + str(self))
    if view is not None:
        sys.stderr.write("'view' is:")
        print " ",view
        o.write("\n\n'view' is:\n")
        o.write("  " + str(view))
        try:
            sys.stderr.write("    'view.info' is ("+str(len(view.info))+"):")
            print view.info
            o.write("\n\n    'view.info' is ("+str(len(view.info))+"):\n")
            o.write(str(view.info))
        except:
            pass
        try:
            sys.stderr.write("    'view.handles' are (0 to "+str(len(view.handles)-1)+" = "+str(len(view.handles))+"):")
            print view.handles
            o.write("\n\n    'view.handles' are (0 to "+str(len(view.handles)-1)+" = "+str(len(view.handles))+"):\n")
            o.write(str(view.handles))
        except:
            pass
    if flags is not None:
        sys.stderr.write("'self flags' is:")
        print " ",flags
        print "   see qeditor.py file for brake down of this total amount, ex:"
        print "       8 (MB_LEFTBUTTON) + 2048 (MB_DRAGEND) = 2056"
        o.write("\n\n'self flags' is:\n")
        o.write("  " + str(flags))
        o.write("\n   see qeditor.py file for brake down of this total amount, ex:")
        o.write("\n          8 (MB_LEFTBUTTON) + 2048 (MB_DRAGEND) = 2056")
    if obj is not None:
        sys.stderr.write("Your test object is:")
        print " ",obj,type(obj)
        o.write("\n\nYour test object is:\n")
        o.write("  " + str(obj) + "  " + str(type(obj)))
    try:
        objclass = obj.classes
        sys.stderr.write("    '.classes' are:")
        print objclass
        o.write("\n\n    '.classes' are:\n")
        o.write(str(objclass))
    except:
        print "    It is not a '.classes' object."
        o.write("\n    It is not a '.classes' object.")
    try:
        objdict = obj.dictitems
        sys.stderr.write("    '.dictitems' are ("+str(len(objdict))+"):")
        print objdict
        o.write("\n\n    '.dictitems' are ("+str(len(objdict))+"):\n")
        o.write(str(objdict))
    except:
        print "    It has no '.dictionnary (key:value)' items."
        o.write("\n    It has no '.dictionnary (key:value)' items.")
    try:
        objflags = obj.flags
        sys.stderr.write("    '.flags' are:")
        print objflags
        o.write("\n\n    '.flags' are:\n")
        o.write(str(objflags))
    except:
        print "    It has no '.flags' items."
        o.write("\n    It has no '.flags' items.")
    try:
        objname = obj.name
        sys.stderr.write("    its '.name' is:")
        print objname
        o.write("\n\n    its '.name' is:\n")
        o.write(str(objname))
    except:
        print "    It has no '.name'."
        o.write("\n    It has no '.name'.")
    try:
        objshortname = obj.shortname
        sys.stderr.write("    its '.shortname' is:")
        print objshortname
        o.write("\n\n    its '.shortname' is:\n")
        o.write(str(objshortname))
    except:
        print "    It has no '.shortname'."
        o.write("\n    It has no '.shortname'.")
    try:
        objparent = obj.parent
        sys.stderr.write("    its '.parent' is:")
        print objparent
        o.write("\n\n    its '.parent' is:\n")
        o.write(str(objparent))
    except:
        print "    It has no '.parent'."
        o.write("\n    It has no '.parent'.")
    try:
        objtreeparent = obj.treeparent
        sys.stderr.write("   its '.treeparent' is:")
        print objtreeparent
        o.write("\n\n   its '.treeparent' is:\n")
        o.write(str(objtreeparent))
    except:
        print "    It has no '.treeparent'."
        o.write("\n    It has no '.treeparent'.")
    try:
        objsubitems = obj.subitems
        sys.stderr.write("    its '.subitems' are ("+str(len(objsubitems))+"):")
        print objsubitems
        o.write("\n\n    its '.subitems' are ("+str(len(objsubitems))+"):\n")
        o.write(str(objsubitems))
    except:
        print "    It has no '.subitems'."
        o.write("\n    It has no '.subitems'.")
    try:
        objtype = obj.type
        sys.stderr.write("    its '.type' is:")
        print objtype
        o.write("\n\n    its '.type' is:\n")
        o.write(str(objtype))
    except:
        print "    It has no '.type'."
        o.write("\n    It has no '.type'.")
    try:
        objinfo = obj.info
        sys.stderr.write("    its '.info' is:")
        print objinfo
        o.write("\n\n    its '.info' is:\n")
        o.write(str(objinfo))
    except:
        print "    It has no '.info' items."
        o.write("\n    It has no '.info' items.")
    try:
        objdictspec = obj.dictspec
        sys.stderr.write("    its '.dictspec' is ("+str(len(objdictspec))+"):")
        print objdictspec
        o.write("\n\n    its '.dictspec' is ("+str(len(objdictspec))+"):\n")
        o.write(str(objdictspec))
    except:
        print "    It has no '.dictspec' items."
        o.write("\n    It has no '.dictspec' items.")
    print "------------------------------------------"
    sys.stderr.write("   A printout of this test has been written to DEVELOPERS.txt\n")
    sys.stderr.write("     and placed in your main QuArK directory for you to use.")
    print "--------------- end of test --------------"
    o.write("\n\n--------------- end of test --------------")
    if openconsole is not None:
        quarkx.console()
    o.close()

def sortdictionary(dictionary):
    "Primarily used to sort menu dictionary lists,"
    "but may work for other dictionary list."
    "Returns just a sorted list of its keys."
    keys = dictionary.keys()
    keys.sort()
    return keys


# ----------- REVISION HISTORY ------------
#$Log: qutils.py,v $
#Revision 1.58  2011/05/26 22:59:26  cdunde
#DanielPharos fix to change bbox icons when hidden.
#
#Revision 1.57  2011/03/27 06:30:56  cdunde
#Icon updates.
#
#Revision 1.56  2011/03/12 23:19:12  cdunde
#Fix to handle Model Editor BBox icons properly.
#
#Revision 1.55  2010/12/07 06:06:52  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.54  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.53  2010/06/06 04:04:24  cdunde
#Fix to draw Eye handles in model editor floating 3D views when first opened.
#
#Revision 1.52  2009/11/28 15:48:15  danielpharos
#Added a comment explaining some flags a bit.
#
#Revision 1.51  2009/09/07 01:38:45  cdunde
#Setup of tag menus and icons.
#
#Revision 1.50  2009/07/14 12:14:54  danielpharos
#Oops: uploaded version: Added logging of plugin loading.
#
#Revision 1.49  2009/06/24 05:49:03  cdunde
#To give long integer error warning and steps for correction.
#
#Revision 1.48  2009/06/09 05:51:48  cdunde
#Updated to better display the Model Editor's Skeleton group and
#individual bones and their sub-bones when they are hidden.
#
#Revision 1.47  2008/11/25 00:22:40  cdunde
#Added new function by DanielPharos to swap RGB color and make a BGR color.
#
#Revision 1.46  2008/10/29 04:29:31  cdunde
#Minor error fix.
#
#Revision 1.45  2008/09/29 22:41:06  danielpharos
#Fixed for file resolving code. Fixes Steam-games.
#
#Revision 1.44  2008/09/29 22:01:56  danielpharos
#Update to filename resolving code. Needs more testing, but should work.
#
#Revision 1.43  2008/07/22 00:54:08  cdunde
#New function added to the Model Editor tree-view RMB to save a skin when one is selected.
#
#Revision 1.42  2008/07/14 18:06:30  cdunde
#Added new function to sort dictionary lists by their keys.
#Primarily used for menu items but may work for others.
#
#Revision 1.41  2008/07/11 19:36:13  cdunde
#Fix for imported models icons.
#
#Revision 1.40  2008/07/10 22:32:33  danielpharos
#Added additional comments and fixed some magic numbers.
#
#Revision 1.39  2008/07/10 21:21:58  danielpharos
#The model component icon changes to an X when you hide the component.
#
#Revision 1.38  2008/07/10 20:36:10  danielpharos
#Fix the model groups icons not working
#
#Revision 1.37  2008/05/01 19:15:23  danielpharos
#Fix treeviewselchanged not updating.
#
#Revision 1.36  2008/05/01 13:52:32  danielpharos
#Removed a whole bunch of redundant imports and other small fixes.
#
#Revision 1.35  2008/02/13 23:05:48  cdunde
#Needed to reverse the order of the RGB color components for the RGBToColor function.
#
#Revision 1.34  2008/02/10 19:20:43  cdunde
#Added new texture color utilities that both editors can use.
#
#Revision 1.33  2007/09/09 18:34:39  cdunde
#To stop quarkx.reloadsetup call (which just calls qutils.SetupChanged)
#from duplicate handle drawing in the Model Editor and use quarkx.reloadsetup
#in mdlmodes for setting "colors" Config. to stop the loss of settings during
#a session when the "Apply" button is clicked which calls quarkx.reloadsetup,
#wiping out all the settings if editor.layout.explorer.selchanged() is used instead.
#
#Revision 1.32  2007/06/24 20:43:29  danielpharos
#Changed the order of the SetupSet keyword for better backwards compatibility.
#
#Revision 1.31  2007/06/13 11:57:33  danielpharos
#Added FreeImage as an alternative for DevIL. PNG and JPEG file handling now also uses these two libraries. Set-up a new section in the Configuration for all of this.
#
#Revision 1.30  2007/02/02 21:16:36  danielpharos
#Fixed a typo
#
#Revision 1.29  2006/12/13 04:55:03  cdunde
#Added a new developers "tool" function "WhatIsThisObject" with various options
#to print everything about a QuArK Internal Object to the console and a hard copy
#in the QuArK main directory folder called DEVELOPERS.txt to avoid constant
#calling of each individual item to get information about what the object consist of.
#
#Revision 1.28  2006/05/07 07:02:08  rowdy
#Added a rough hack to allow %file% type substitution in the '<game> command-line' option.  Also added %filename% parameter that is replaced with the map filename (without path, without extension).
#
#Revision 1.27  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.24  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.23  2003/12/17 13:58:59  peter-b
#- Rewrote defines for setting Python version
#- Removed back-compatibility with Python 1.5
#- Removed reliance on external string library from Python scripts
#
#Revision 1.22  2003/03/15 01:57:40  tiglari
#add hintPlusInfobaselink function
#
#Revision 1.21  2002/05/11 02:15:41  tiglari
#added attribute-management methods
#
#Revision 1.20  2002/04/12 11:25:30  tiglari
#revert loadimages2 to loadimages  (a less well-thought-out leak hunt move ...)
#
#Revision 1.19  2002/03/26 22:19:20  tiglari
#support UseIntegralVertexes flag
#
#Revision 1.18  2002/03/05 11:03:50  tiglari
#revert group icon selection code to older version to restore hidden/nonhidden
# difference.
#
#Revision 1.17  2001/10/22 11:27:26  tiglari
#clean up some leak tracking stuff
#
#Revision 1.16  2001/10/22 10:28:20  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.15  2001/10/16 11:40:34  tiglari
#live pointer hunt, delete some stuff after use, very provisional
#
#Revision 1.14  2001/07/28 05:29:19  tiglari
#fix loading of bsp support so that it works after a map has been edited.
#rename patchLoad to reLoad
#
#Revision 1.13  2001/07/27 11:31:47  tiglari
#bsp study: plane viewing, faces in treeview
#
#Revision 1.12  2001/03/29 04:42:11  tiglari
#reinstate MapHotKey & MapHotKeyList
#
#Revision 1.11  2001/03/29 01:25:53  aiv
#modifable :form objects!
#
#Revision 1.8  2001/03/01 19:15:14  decker_dk
#changed loadmapeditor() so it reads the 'BezierPatchSupport' and 'BezierPatchPluginPrefixes' instead.
#
#Revision 1.7  2000/11/19 15:33:02  decker_dk
#Comment about keeping the constants equal with the .PAS source
#
#Revision 1.6  2000/10/26 18:14:34  tiglari
#added SO_BRUSHPRIM
#
#Revision 1.5  2000/06/09 23:39:02  aiv
#More MD3 Support Stuff
#
#Revision 1.4  2000/06/02 16:00:22  alexander
#added cvs headers
#
#Revision 1.3  2000/05/26 23:13:37  tiglari
#Changed patch support loading (loadmapeditor) so that it is loaded when you open a map whose game has shaders
#
#
