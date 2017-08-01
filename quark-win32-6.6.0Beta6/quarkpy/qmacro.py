"""   QuArK  -  Quake Army Knife

Python macros available for direct call by QuArK
"""
#
# Copyright (C) 1996-2000 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/quarkpy/qmacro.py,v 1.33 2012/03/08 20:37:21 danielpharos Exp $

#
# Macros are called by QuArK based on name. These are the
# only direct calls that QuArK can make to Python. Usually,
# Python provides callback to QuArK.
#


import quarkx
import qtoolbar
import qutils

#
# Macros called when there is an object to display in a window.
#

def MACRO_displaymap(self, what=None):
    "Called when there is a map to display."
    qutils.loadmapeditor(what)
    import mapeditor
    if isinstance(self.info, mapeditor.MapEditor):
        self.info.ReopenRoot(self)
    else:
        mapeditor.MapEditor(self)   # new map editor

def MACRO_displaybsp(self):
    MACRO_displaymap(self,'bsp')


def MACRO_displaymdl(self):
    "Called when there is a model to display."
    qutils.loadmdleditor()
    import mdleditor
    if isinstance(self.info, mdleditor.ModelEditor):
        self.info.ReopenRoot(self)
    else:
        mdleditor.ModelEditor(self)   # new model editor



#
# Macro called when QuArK needs the images of a Duplicator.
#

def MACRO_duplicator(dup):
    "Computes Duplicator images."
    if quarkx.setupsubset(qutils.SS_MAP, "Options")["IgnoreDup"]:
        return []

    qutils.loadmapeditor()
    import mapduplicator
    import mapquakemenu
    items = mapduplicator.DupManager(dup).buildimages()
    if (dup["MapObjectName"] is not None):
        ObjectName = dup["MapObjectName"]
        mapquakemenu.recursivelycreateierarchy(items, ObjectName)
    return items


#
# Macro called when a linear operation is applied.
#

def MACRO_applylinear(entity, matrix):
    "Applies a linear distortion (rotate, zoom, etc) on an entity or a Duplicator."
    # Note : "origin" is updated by QuArK before it calls this macro.
    qutils.loadmapeditor()
    import mapentities
    mapentities.CallManager("applylinear", entity, matrix)


#
# Macro called when the mouse is over a control with a hint
#

def MACRO_hint(form, text=None):
    if form is None:
        return ""
    import qbaseeditor
    if not isinstance(form.info, qbaseeditor.BaseEditor):
        return
    return form.info.showhint(text)


#
# Macro called to build a map (when the big GO! button is pressed).
#

def MACRO_buildmaps(maps, mode, extracted, cfgfile="", defaultbsp=None):
    "Builds maps and runs Quake."

    if mode is None:
        code = "P"
        text = "Play"
    else:
        code = quarkx.buildcodes[mode]
        text = quarkx.buildmodes[mode]
    forcepak = "K" in code
    runquake = "P" in code
    build = quarkx.newobj(":")

    if "C" in code:                #
        build["Textures"] = "1"    # Complete rebuild
        build["QCSG1"] = "1"       #
        build["QBSP1"] = "1"
        build["VIS1"] = "1"
        build["LIGHT1"] = "1"
        build["LIGHTCmd"] = "-extra"

    elif "F" in code:              #
        build["Textures"] = "1"    # Fast rebuild
        build["QCSG1"] = "1"       #
        build["QBSP1"] = "1"

    else:                          #
        pass                       # Don't build maps
                                   #
    maplist = []
    for map in maps:
        root = map['Root']
        if root is None: continue
        root = map.findname(root)
        if root is None: continue
        maplist.append((map, root, build))

    qutils.loadmapeditor()
    import mapquakemenu
    mapquakemenu.RebuildAndRun(maplist, None, runquake, text, forcepak, extracted, cfgfile, defaultbsp)



#
# Macro called to "pack" a model.
#

def MACRO_pack_model(model):
    import mdlpack
    return mdlpack.PackModel(model)

#
# Macro called when a model component is modified.
#

def MACRO_update_model(component):
    import mdlpack
    mdlpack.UpdateModel(component)


#
# Macro called when an item in the '?' menu is selected.
#

helpfn = {}
def MACRO_helpmenu(text):
    import qeditor
    getattr(qeditor, helpfn[text])()


def MACRO_shutdown(text):
#    quitfile=open(quarkx.exepath+'quit.txt','w')
#    quitfile.write('quitting\n')
    import qutils

    del qutils.ico_objects
    del qutils.ico_editor
    
    for key in qutils.ico_dict.keys():
        del qutils.ico_dict[key]
#        quitfile.write('zapping '+key+'\n')
    del qutils.ico_dict

#    quitfile.write('done\n')
#    quitfile.close()
    
#
#    ---- Dialog Boxes ----
#

dialogboxes = {}

def closedialogbox(name):
    try:
        dialogboxes[name].close()
        del dialogboxes[name]
    except KeyError:
        pass


#
# The class "dialogbox" is a base for actual dialog boxes.
# See qeditor.py and mapfindreptex.py for examples.
#

class dialogbox:

    dlgdef = ""
    size = (300,170)
    begincolor = None
    endcolor = None
    name = None
    dfsep = 0.6
    dlgflags = qutils.FWF_KEEPFOCUS | qutils.FWF_POPUPCLOSE

    def __init__(self, form, src, **buttons):
        name = self.name or self.__class__.__name__
        closedialogbox(name)
        f = quarkx.newobj("Dlg:form")
        if self.dlgdef is not None:
            f.loadtext(self.dlgdef)
            self.f = f
            for pybtn in f.findallsubitems("", ':py'):
                pybtn["sendto"] = name
            self.buttons = buttons
            dlg = form.newfloating(self.dlgflags, f["Caption"])
            dialogboxes[name] = dlg
            dlg.windowrect = self.windowrect()
            if self.begincolor is not None: dlg.begincolor = self.begincolor
            if self.endcolor is not None: dlg.endcolor = self.endcolor
            dlg.onclose = self.onclose
            dlg.info = self
            self.dlg = dlg
            self.src = src
            df = dlg.mainpanel.newdataform()
            self.df = df
            df.header = 0
            df.sep = self.dfsep
            df.setdata(src, f)
            df.onchange = self.datachange
            import qeditor
            df.flags = qeditor.DF_AUTOFOCUS
            dlg.show()

    def windowrect(self):
        x1,y1,x2,y2 = quarkx.screenrect()
        cx = (x1+x2)/2
        cy = (y1+y2)/2
        size = self.size
        return (cx-size[0]/2, cy-size[1]/2, cx+size[0]/2, cy+size[1]/2)

    def datachange(self, df):
        pass   # abstract

    def onclose(self, dlg):
        dlg.info = None
        dlg.onclose = None   # clear refs
        if self.df is not None:
            self.df.onchange = None
            self.df = None
        self.dlg = None
        del self.buttons

    def close(self, reserved=None):
        self.dlg.close()


def MACRO_pybutton(pybtn):
    dlg = dialogboxes[pybtn["sendto"]]
    return dlg.info.buttons[pybtn.shortname]

def MACRO_makeaddon(self):
    import qutils
    a = quarkx.getqctxlist()
    a.reverse()
    i = 0
    while (a[i]["GameDir"] == None):
        i = i + 1
        if i == len(a):
            raise "No GameDir found"
    a[i].makeentitiesfromqctx();

def MACRO_makeaddon_tex(self):
    import qutils
    a = quarkx.getqctxlist()
    a.reverse()
    i = 0
    while (a[i]["GameDir"] == None):
        i = i + 1
        if i == len(a):
            raise "No GameDir found"
    a[i].maketexturesfromqctx();

def MACRO_loadentityplugins(self):
    import plugins
    plugins.LoadPlugins("ENT")
    global MACRO_loadentityplugins
    MACRO_loadentityplugins = lambda x: None    # next calls to loadmdleditor() do nothing

def MACRO_loadmdlimportexportplugins(self):
    import plugins
    plugins.LoadPlugins("IE_")
    # Fill the importer menu with menu items
    orderedlist = mdlimportmenuorder.keys()
    orderedlist.sort()
    for menuindex in orderedlist:
        for importer in mdlimportmenuorder[menuindex]:
            quarkx.mdlimportmenu(importer)
    global MACRO_loadmdlimportexportplugins
    MACRO_loadmdlimportexportplugins = lambda x: None    # next calls to loadmdleditor() do nothing

### A list, used below, to pass items to for the main QuArK menu Conversion section.
### See the plugins files that start with "ent" for its use.
entfn = {}

def MACRO_ent_convertfrom(text):
    import qeditor
    import qutils
    a = quarkx.getqctxlist()
    a.reverse()
    # Decker - Some menuitem-captions contains a '&'-character (you know, the one which tells what mnemonic-key can be used)
    # These '&'-characters has to be removed, for the entfn[text] to work properly.
    text = text.replace("&", "")
    entf = entfn[text]
    if entf is not None and entf[0][0] is not None:
        files = quarkx.filedialogbox("Select File", text, entf[0], 0)
        if len(files) != 0:
            file = files[0]
            gn = a[0]["GameDir"]
            if (gn is None) or (gn == ""):
                gn = file
            entf[1](a[0].parent, file, gn)
    if entf[0][0] is None and entf[1] is not None:
        entf[1](a[0].parent) # This calls the function that is stored in the "entfn" list above.

### A list, used below, to pass items to for the main QuArK menu 'Model Importers' section.
### See the plugins files that start with "ie_" for its use.
mdlimport = {}
mdlimportmenuorder = {}

def MACRO_mdl_pythonimporter(text):
    import qeditor
    import qutils
    a = quarkx.getqctxlist()
    a.reverse()
    # Decker - Some menuitem-captions contains a '&'-character (you know, the one which tells what mnemonic-key can be used)
    # These '&'-characters has to be removed, for the entfn[text] to work properly.
    text = text.replace("&", "")
    mdlf = mdlimport[text]
    if mdlf is not None and mdlf[0][0] is not None:
        files = quarkx.filedialogbox("Select File", text, mdlf[0], 0)
        if len(files) != 0:
            filename = files[0]
            gamename = a[0]["GameDir"]
            if (gamename is None) or (gamename == ""):
                gamename = filename
            mdlf[1](a[0].parent, filename, gamename)
    if mdlf[0][0] is None and mdlf[1] is not None:
        mdlf[1](a[0].parent) # This calls the function that is stored in the "mdlimport" list above.

### A list, used below, to pass items to for the main QuArK menu 'Model Exporters' section.
### See the plugins files that start with "ie_" for its use.
mdlexport = {}
mdlexportmenuorder = {}

def MACRO_mdl_pythonexporter(text):
    import qeditor
    import qutils
    a = quarkx.getqctxlist()
    a.reverse()
    # Decker - Some menuitem-captions contains a '&'-character (you know, the one which tells what mnemonic-key can be used)
    # These '&'-characters has to be removed, for the entfn[text] to work properly.
    text = text.replace("&", "")
    mdlf = mdlexport[text]
    if mdlf is not None and mdlf[0][0] is not None:
        # See plugins\mapbotwaypointer.py file for example of line below for use.
        files = quarkx.filedialogbox("Save file as...", text, mdlf[0], 1)
        if len(files) != 0:
            file = files[0]
            gn = a[0]["GameDir"]
            if (gn is None) or (gn == ""):
                gn = file
            mdlf[1](a[0].parent, file, gn)
    if mdlf[0][0] is None and mdlf[1] is not None:
        mdlf[1](a[0].parent) # This calls the function that is stored in the "mdlexport" list above.

# ----------- REVISION HISTORY ------------
#
#$Log: qmacro.py,v $
#Revision 1.33  2012/03/08 20:37:21  danielpharos
#Produce error instead of crash if gamedir not found.
#
#Revision 1.32  2009/03/04 23:32:13  cdunde
#For proper importer exporter listing one menus, code by DanielPharos.
#
#Revision 1.31  2008/08/21 12:01:30  danielpharos
#Removed a magic number
#
#Revision 1.30  2008/06/28 14:44:52  cdunde
#Some minor corrections.
#
#Revision 1.29  2008/06/04 03:56:39  cdunde
#Setup new QuArK Model Editor Python model import export system.
#
#Revision 1.28  2008/04/04 20:19:27  cdunde
#Added a new Conversion Tools for making game support QuArK .qrk files.
#
#Revision 1.27  2008/03/09 21:44:11  cdunde
#To reinstate fix for error if Addons Delete item is opened and closed with no items to delete.
#Over written by old file used for Revision 1.20.2.1 commit and Revision 1.22 file merging.
#
#Revision 1.26  2008/02/07 13:17:57  danielpharos
#Removed redundant variable
#
#Revision 1.25  2007/12/21 20:39:23  cdunde
#Added new Templates functions and Templates.
#
#Revision 1.24  2007/12/14 21:48:00  cdunde
#Added many new beizer shapes and functions developed by our friends in Russia,
#the Shine team, Nazar and vodkins.
#
#Revision 1.23  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.22  2006/11/29 07:00:28  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.20.2.1  2006/11/23 20:04:49  danielpharos
#Removed a macro that isn't used anymore
#
#Revision 1.20  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.17  2003/12/17 13:58:59  peter-b
#- Rewrote defines for setting Python version
#- Removed back-compatibility with Python 1.5
#- Removed reliance on external string library from Python scripts
#
#Revision 1.16  2003/07/24 18:22:36  peter-b
#Marco's fix for the lambda bug
#
#Revision 1.15  2001/10/22 10:28:20  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.14  2001/10/20 02:13:18  tiglari
#live pointer hunt: redo shutdown macro
#
#Revision 1.13  2001/07/27 11:31:47  tiglari
#bsp study: plane viewing, faces in treeview
#
#Revision 1.12  2001/06/18 20:30:12  decker_dk
#Replace all '&'-characters with nothing, for menuitem-captions used as indexes into python-style dictionaries.
#
#Revision 1.11  2001/06/13 23:01:13  aiv
#Moved 'Convert From' stuff to python code (plugin type)
#
#Revision 1.10  2001/03/28 19:23:15  decker_dk
#Added '(*.fgd)' to the filedialogbox-call.
#
#Revision 1.9  2001/03/15 21:09:01  aiv
#moved .fgd reading to menu, sepearted texture & entity reading
#
#Revision 1.5  2000/06/02 16:00:22  alexander
#added cvs headers
#
