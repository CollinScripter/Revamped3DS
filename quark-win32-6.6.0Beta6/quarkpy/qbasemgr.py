"""   QuArK  -  Quake Army Knife

Map and Model editor Layout managers.
"""
#
# Copyright (C) 1996-2000 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/qbasemgr.py,v 1.41 2011/06/29 20:43:28 cdunde Exp $



#
# See comments in file mapmgr.py.
#


import math
import quarkx
import qtoolbar
import qmenu
from qdictionnary import Strings
from qeditor import *
import quarkpy.qhandles # To add change of "Floating 3D view" mouse control between Map and Model editors.

#py2.4 indicates upgrade change for python 2.4

ModesHint = "|Each view can be set to one of three rendering modes :\n\nWireframe : all polygons are drawn as lines, entities as points, etc.\n\nSolid : each polygon is drawn in a single, solid color.\n\nTextured : polygon and models are displayed with their texture."

class BaseLayout:
    "An abstract base class for Map and Model Editor screen layouts."

    Floating3DWindows = []

    def __init__(self):
        # debug("Creation of layout '%s'" % self.__class__.__name__)
        self.clearrefs()

    def clearrefs(self):
        self.rotateviews = self.views = []
        self.baseviews = []
        self.sblinks = []       # list of tuples (0 or 1, sourceview, 0 or 1, destview)
        self.oldsblinks = None   # where 0 means horizontal and 1 means vertical
        self.explorer = None
        self.mpp = None
        self.buttons = {}
        self.toolbars = {}
        self.leftpanel = None
        self.hintcontrol = None
        self.hinttext = ""
        self.compass = None
        self.editor = None

   # def __del__(self):
   #     debug("Destruction of layout '%s'" % self.__class__.__name__)

    def destroyscreen(self, form):
        "Closes everything on the screen and clears all references."

        try:
            setup = quarkx.setupsubset(self.MODE, "Layouts")
            config = setup.findshortname(self.shortname)
            if config is None:
                config = quarkx.newobj(self.shortname+":config")
                setup.appenditem(config)
            self.writeconfig(config)
            writetoolbars(self, config)

        finally:
            for c in form.floatings():           c.close()
            for c in form.mainpanel.controls():  c.close()
            for c in form.toolbars():            c.close()
            form.mainpanel.sections = ((),())
            if self.explorer != None: self.explorer.clear()
            if self.mpp      != None: self.mpp.clear()
            self.clearrefs()
            del self.editor


    def setupchanged(self, level):
        "Reads setup-dependant information for the layout."
        setup = quarkx.setupsubset(SS_GENERAL, "3D View")
        if setup["CloseOnSetup"]:
            try:
                if self.buttons["3D"].state == qtoolbar.selected:
                    self.buttons["3D"].state = 0
                    quarkx.update(self.editor.form)
            except KeyError:
                pass
            for floating in BaseLayout.Floating3DWindows:
                floating.close()
            self.editor.layout.mpp.viewpage(0)
        if len(self.views):
            if MapOption("CrossCursor", self.MODE):
                ncursor = CR_CROSS
                nhandlecursor = CR_ARROW
            else:
                ncursor = CR_ARROW
                nhandlecursor = CR_CROSS
            for v in self.views:
                v.cursor = ncursor
                v.handlecursor = nhandlecursor
                v.setup = None   # reload setup from default source
            self.editor.invalidateviews(1)
            setup = quarkx.setupsubset(self.MODE, "Colors")
            self.views[0].color = setup.getint("ViewXY")
            self.views[0].darkcolor = setup.getint("SelXY")
            for v in self.views[1:]:
                v.color = setup.getint("ViewXZ")
                v.darkcolor = setup.getint("SelXZ")
            self.views[0].info["onsetangle"] = self.fffsetangle
            self.views[0].info["onsetscale"] = self.zoombar.ScaleChanged
            self.views[0].info["onsetvangle"] = self.vbar.VAngleChanged
        if MapOption("NoScrollBars", self.MODE):
            for v in self.views:
                v.flags = v.flags | MV_NOSCROLLBAR
        else:
            for v in self.views:
                v.flags = v.flags &~ MV_NOSCROLLBAR
        if self.mpp is not None:
            self.mpp.lock.state = (qtoolbar.selected,0)[not MapOption("PagesLocked", self.MODE)]
        if level is None:
            setup = quarkx.setupsubset(self.MODE, "Layouts")
            config = setup.findshortname(self.shortname)
            self.readtoolbars(config)
            if config is not None:
                self.readconfig(config)
        if self.editor is not None:
            self.setgrid(self.editor)
            try:
                self.buttons["linear"].state = self.editor.linearbox and qtoolbar.selected
            except KeyError:
                pass
            try:
                self.buttons["lockv"].state = self.editor.lockviews and qtoolbar.selected
            except KeyError:
                pass
        ex = self.explorer
        if MapOption("TreeKeybDelay", self.MODE):
            ex.flags = ex.flags &~ EF_NOKEYBDELAY
        else:
            ex.flags = ex.flags | EF_NOKEYBDELAY
        if self.hintcontrol is not None:
            self.hintcontrol.color = MapColor("ViewXY", self.MODE)
        if self.compass is not None:
            self.compass.setupchanged(self.MODE)


    def updateviewproj(self):
        for v in self.views:
            setprojmode(v)

    def drawing(self, view):
        #
        # Update the map view's display limit, to know what should
        # be normal or grayed out
        #
        self.setupdepth(view)
        #
        # Scroll the views whose position are linked together
        #
        for ifrom, linkfrom, ito, linkto in self.sblinks:
            if linkfrom is view:
                pos = view.scrollbars[ifrom][0]
                if ito:      # if the dest. view is to be scrolled vertically
                    linkto.scrollto(None, pos)
                else:
                    linkto.scrollto(pos, None)


    def getlayoutmenu(self, text="level"):
        "Builds a default Layout menu (may be overridden)."
        modhint = ModesHint + "\n\nThe commands in this menu lets you change the mode for all views at once. To set the mode of a single view, right-click on it.|intro.mapeditor.menu.html#layoutmenu"
        infobaselink = "intro.mapeditor.menu.html#layoutmenu"
        Mod1 = qmenu.item("&Wireframe", self.setviewmode, modhint)
        Mod1.mode = "wire"
        Mod2 = qmenu.item("&Solid", self.setviewmode, modhint)
        Mod2.mode = "solid"
        Mod3 = qmenu.item("&Textured", self.setviewmode, modhint)
        Mod3.mode = "tex"
        New3D = qmenu.item("3D view", self.full3Dclick, "|3D view:\n\nThis will create a new free-floating 3D edit window.", infobaselink)
        cliphint = "|While you edit your "+text+", some parts of it may be visible on one view but not on the others. Such parts are considered to be 'out of view', and these commands control how they are displayed :\n\n'Show whole "+text+"': no out-of-view masking\n'Gray out of view': grayed out (default)\n'Hide out of view': simply hidden"
        DrM1 = qmenu.item("Show &whole "+text, self.setdrawmode, cliphint, infobaselink)
        DrM1.mode = DM_NORMAL
        DrM2 = qmenu.item("&Gray out of view", self.setdrawmode, cliphint, infobaselink)
        DrM2.mode = DM_GRAYOOV
        DrM3 = qmenu.item("&Hide out of view", self.setdrawmode, cliphint, infobaselink)
        DrM3.mode = DM_HIDEOOV
        PanelRight = qmenu.item("Panel at &right", self.panelatright, "|Panel at right:\n\nThis will move the main panel to the right side of your screen. Unselecting this function will move it back to the left side.", infobaselink)
         #
         # NOTE: this menu is accessed by position in the function "layoutmenuclick"
         #
        return [Mod1, Mod2, Mod3, New3D, qmenu.sep, DrM1, DrM2,
         DrM3, qmenu.sep, PanelRight], {"Ctrl+1":Mod1, "Ctrl+2":Mod2,
         "Ctrl+3":Mod3, "Ctrl+4": New3D}
        #return [Mod1, Mod2, Mod3, New3D, NewOGL, NewF3D, qmenu.sep, DrM1, DrM2,
        # DrM3, qmenu.sep, PanelRight], {"Ctrl+1":Mod1, "Ctrl+2":Mod2,
        # "Ctrl+3":Mod3, "Ctrl+4": New3D, "Ctrl+5": NewOGL, "Ctrl+6": NewF3D} Daniel

    def layoutmenuclick(self, menu):
        common = None
        if len(self.views):
            test = self.baseviews[0].viewmode
            for v in self.baseviews[1:]:
                if v.viewmode != test:
                    break
            else:
                common = test
        for m in menu.items[0:3]: # position of (self.getlayoutmenu) Mod1, Mod2 and Mod3
            m.state = (m.mode == common) and qmenu.radiocheck
        #menu.items[4].state = (self is BaseLayout.CurrentRendererOwner) and qmenu.checked  #DanielPharos: CurrentRendererOwner is not used anymore anyway...
        for m in menu.items[5:8]: # position of (self.getlayoutmenu) DrM1, DrM2 and DrM3
            m.state = (m.mode == (self.editor.drawmode&DM_MASKOOV)) and qmenu.radiocheck
        menu.items[9].state = (self.leftpanel.align=="right") and qmenu.checked # position of (self.getlayoutmenu) PanelRight

    def setviewmode(self, menu):
        for v in self.baseviews:
            v.viewmode = menu.mode
        self.editor.lastscale = 0    # force a call to buildhandles()

    def setdrawmode(self, menu):
        self.editor.drawmode = menu.mode | (self.editor.drawmode &~ DM_MASKOOV)
        self.editor.savesetupinfos()
        for v in self.views:
            if v.viewmode == "wire":
                v.invalidate()

    def panelatright(self, menu):
        self.leftpanel.align = ("right", "left")[self.leftpanel.align=="right"]

    def full3Dclick(self, menu):
        setup = quarkx.setupsubset(SS_GENERAL, "3D View")
        if self.buttons["3D"].state == 0:
            if setup["Warning3D"]:
                if quarkx.msgbox(Strings[-104], MT_WARNING, MB_YES|MB_NO) != MR_YES:
                    raise quarkx.abort
            self.openfull3Dview()
            setup["Warning3D"] = ""
            if not setup["AllowMultiple"]:
                self.buttons["3D"].state = qtoolbar.selected
                quarkx.update(self.editor.form)
        else:
            if not setup["AllowMultiple"]:
                for floating in BaseLayout.Floating3DWindows:
                    floating.close()

    def openfull3Dview(self):
        "Opens the 3D view."
        setup = quarkx.setupsubset(SS_GENERAL, "3D View")
        if not setup["AllowMultiple"]:
            for floating in BaseLayout.Floating3DWindows:
                floating.close()
        #DanielPharos: Check for FullScreen. If set, go fullscreen!
        floating = quarkx.clickform.newfloating(0, "Full 3D view")
        view = floating.mainpanel.newmapview()
        #floating.rect = view.setup["FullScreenSize"]
        #floating.rect = view.setup["WndRect"]
        view.info = {"type": "3D", "viewname": "3Dwindow"}
        #view.info = {"type": "3D", "noclick": None, "viewname": "full3Dview"}
        view.viewmode = "tex"
        if self.editor.MODE == 3:
            view.showprogress=0
        view.viewtype = "window"

    ### Calling this function causes the 3D view mouse maneuvering to change,
    ### rotation is based on the center of the editor view or the model (0,0,0).
    ### But only for the Model Editor, so we first test for that.
        if isinstance(self.editor, quarkpy.mdleditor.ModelEditor):
            view.viewtype = "editor"
            quarkpy.qhandles.flat3Dview(view, self)
            del view.info["noclick"]
            view.info["viewname"]="3Dwindow"
            import mdlmgr, mdlhandles
            mdlmgr.treeviewselchanged = 0

        setprojmode(view)
        self.editor.setupview(view)
        floating.info = view
        floating.onclose = self.closefull3Dview
        mode = view.full3Dview()
        if mode!=2: #Check for fullscreen
            #if mode==1: #Check for hidden?
                #floating.close()
                #return
            #else:
                #floating.windowrect = quarkx.screenrect()
                setup = quarkx.setupsubset(SS_GENERAL, "3D View")
                r = setup["WndRect"]
                temp = (int(r[0]), int(r[1]), int(r[2]), int(r[3]))   #py2.4
                r = temp   #py2.4
                floating.windowrect = r
                r = r[2:]
                floating.rect = r
                floating.show()
        if not (view in self.views):
            self.views.append(view)
            if self.editor.MODE == 3:
                mdlhandles.AddRemoveEyeHandles(self.editor, view)
            else:
                self.update3Dviews(view)
        BaseLayout.Floating3DWindows.append(floating)
        if self.editor.MODE == 3:
            pass
        else:
            self.editor.layout.explorer.selchanged()

    def closefull3Dview(self, floating):
        "Closes the 3D view."
        view = floating.mainpanel.controls()[0]
        view.full3Dview()
        #if not offscreen:  #This should be used!
        r = floating.windowrect
        r = r[:2] + floating.rect
        setup = quarkx.setupsubset(SS_GENERAL, "3D View")
        setup["WndRect"] = r
        if view in self.views:
            self.views.remove(view)
            if self.editor.MODE == 3:
                pass
            else:
                self.update3Dviews()
        BaseLayout.Floating3DWindows.remove(floating)
        if not setup["AllowMultiple"]:
            self.buttons["3D"].state = 0
            quarkx.update(self.editor.form)
        if self.editor.MODE == 3:
            pass
        else:
            self.editor.layout.explorer.selchanged()

    def setupdepth(self, view):
        pass    # abstract

    def readconfig(self, config):
          # can be overridden
        if self.leftpanel is not None:
            self.leftpanel.align = ("right", "left")[not config["LPAtLeft"]]
            i = config.getint("LeftPanel")
            if i>0:
                self.leftpanel.size = i
            i = config["LeftPanelV"]
            if type(i) is type(()):
                self.leftpanel.sections = ((), i)
        cfg = config["ViewMode"]
        if type(cfg)==type("") and len(cfg)==len(self.baseviews):
            for v in self.baseviews:
                try:
                    v.viewmode = {"w": "wire", "s": "solid", "t": "tex"} [ cfg[0] ]
                except:
                    pass
                cfg = cfg[1:]

    def writeconfig(self, config):
          # can be overridden
        if self.leftpanel is not None:
            config["LPAtLeft"] = "1"[:self.leftpanel.align=="right"]
            config.setint("LeftPanel", self.leftpanel.size)
            config["LeftPanelV"] = self.leftpanel.sections[1]
        if len(self.baseviews):
            cfg = ""
            for v in self.baseviews:
                cfg = cfg + v.viewmode[0]
            config["ViewMode"] = cfg


    def bs_multipagespanel(self, panel):
        "Builds the multi-pages panel (usually bottom left)."
        ico_maped=ico_dict['ico_maped']
        self.explorer = panel.newexplorer()
        self.explorer.flags = EF_AUTOFOCUS
        self.explorer.hint = "||Data displays:\n\nThese are the various displays to help you build and organize your map.\n\nThere are five specific displays, they are:\n\nTree-view (hierarchy-view)\nSpecifics/Args-view\nPolyhedron-view\nFace-view\n3D-view\n\nFor a detailed description and use of these displays, see the infobase documents.|intro.mapeditor.dataforms.html"
        page0 = qtoolbar.button(None, "Tree-view (hierarchy-view)||Tree-view (hierarchy-view):\n\nThis view displays a  list of everything in your map : entities, polyhedrons, groups, etc.\n\n You should consider it as the best way to organize your map so that you can easily find what you are looking for.\n\nUse groups (the button above) to organize your map.\nFor more information about the available object types, see the tutorials.\n\nAlso see the infobase for a more detailed description and use of this view display.", ico_maped, 8, "Tree-view (hierarchy-view)", infobaselink='intro.mapeditor.dataforms.html#treeview')
        page0.pc = [self.explorer]
        plist, mppages = self.bs_additionalpages(panel)
        plist.insert(0, page0)
        for f in mppages:
            mppg = f(self, panel)
            plist.append(mppg.button())
        count = 0
        for btn in plist:
            count = count + 1
            if count<=9:
                # See also qbaseeditor.BaseEditor.initquickkeys
                #
                # Split up the hint, into its components delimited by a "|".
                hintstrings = btn.hint.split("|");
                # Then alter the first flyover-hint, suffix with a "(keyboard shortcut..)" string.
                hintstrings[0] = "%s\n(keyboard shortcut: '%d')" % (hintstrings[0], count) # To indicate what is a shortcut-key
                # Put it all together again as a string, with the "|" delimiter
                try:
                    def hintprefix(hint):
                        return "|"+hint
                    concathints = reduce(lambda x,y: x+y, map(hintprefix, hintstrings[1:]))
                except:
                    concathints = ""
                # Give the modified hint-string back to btn.hint
                btn.hint = hintstrings[0] + concathints
        self.mpp = MultiPanesPanel(panel, plist, 0)
        self.mpp.lock = qtoolbar.button(maptogglebtn, "lock the current page||When this button is activated, QuArK no longer automatically switches between the pages when you select or unselect objects.", ico_maped, 9)
        self.mpp.lock.mode = self.MODE
        self.mpp.lock.tag = "PagesLocked"
        import mapeditor
        if isinstance(self.editor, mapeditor.MapEditor):
            self.mpp.btnpanel.buttons = self.mpp.btnpanel.buttons + [qtoolbar.padright, self.mpp.lock]
        else:
            import mdlbtns
            TexBtn = qtoolbar.button(mdlbtns.texturebrowser, "choose texture||Click this button to open the 'Texture Browser'.", ico_maped, 0)
            self.mpp.btnpanel.buttons = self.mpp.btnpanel.buttons + [TexBtn] + [qtoolbar.padright, self.mpp.lock]

    def bs_leftpanel(self, form, right=0):
        "Default-looking panel at the left or right of the screen."
        ico_maped=ico_dict['ico_maped']
        if right:
            LeftPanel = form.mainpanel.newrightpanel(180)
        else:
            LeftPanel = form.mainpanel.newleftpanel(180)
        self.leftpanel = LeftPanel
        toppanel = LeftPanel.newpanel()
        bottompanel = LeftPanel.newpanel()
        bottompanel.section = (0,1)
        LeftPanel.sections = ((), (0.37,))
        CompassPanel = toppanel.newbottompanel(96,0)

        self.vbar = VBar(self.rotateviews, CompassPanel.newrightpanel(36,0))
        self.compass = Compass(self.rotateviews, CompassPanel.newrightpanel(96,0))
        self.zoombar = ZoomBar(self.views, CompassPanel.newrightpanel(16,0), self.MODE)

        if ico_maped[0][0].size[1] <= 16:
            NewItem = [qtoolbar.button(self.NewItem1Click, "New item||New item:\n\nThis window contains all objects thats possible to use in the map-views and dataform-display.|intro.mapeditor.misctools.html#newmapitem", ico_objects, iiNewFolder)]
        else:
            NewItem = []
        Trash = qtoolbar.button(self.editor.editcmdclick, "Delete selected item, just drag & drop||Delete selected item|intro.mapeditor.misctools.html#trashcan", ico_maped, 2)
        Trash.cmd = "del"
        Trash.ondrop = self.editor.trash1drop
        Undo = qtoolbar.macrobtn("MURD", "Multiple undo/redo||Multiple undo/redo:\n\nThe icon will open up the undo/redo display. |intro.mapeditor.misctools.html#undoredo", ico_maped, 6)
        try:
            bb = CompassPanel.newbtnpanel(NewItem + [Trash, Undo, NewGroup])
            bb.margins = (2,1)
        except:
            try:
                if isinstance(self.editor, quarkpy.mdleditor.ModelEditor):
                    if not ico_dict.has_key('mdlobjs'):
                        ico_dict['mdlobjs'] = LoadIconSet("images\\mdlobjs", 16)
                    ico_mdlobjs = ico_dict['mdlobjs']
                    NewBBoxGroup = qtoolbar.button(self.editor.editcmdclick, "New BBox sub-group||New BBox sub-group:\n\nCreates a new BBox sub-group in the tree-view 'Misc' folder, where you can place bbox (poly bounding and collision) objects in.|intro.modeleditor.misctools.html#bboxsubgroup", ico_mdlobjs, 8)
                    NewBBoxGroup.cmd = "newbboxgroup"
                    NewSkinsGroup = qtoolbar.button(self.editor.editcmdclick, "New skins sub-group||New skins sub-group:\n\nCreates a new Skins sub-group in the selected component's 'Skins' folder, where you can place skin objects in, used for Quake1 animation skins.|intro.modeleditor.misctools.html#skinsubgroup", ico_mdlobjs, 0)
                    NewSkinsGroup.cmd = "newskingroup"
                    bb = CompassPanel.newbtnpanel(NewItem + [Trash, Undo, NewBBoxGroup, NewSkinsGroup])
                    bb.margins = (2,1)
                else:
                    NewGroup = qtoolbar.button(self.editor.editcmdclick, "New group||New group:\n\nCreates a new group in the tree-view, where you can place other objects in, so they are neatly grouped together.|intro.mapeditor.misctools.html#newgroup", ico_maped, 16)
                    NewGroup.cmd = "newgroup"
                    bb = CompassPanel.newbtnpanel(NewItem + [Trash, Undo, NewGroup])
                    bb.margins = (2,1)
            except:
                NewGroup = qtoolbar.button(self.editor.editcmdclick, "New group||New group:\n\nCreates a new group in the tree-view, where you can place other objects in, so they are neatly grouped together.|intro.mapeditor.misctools.html#newgroup", ico_maped, 16)
                NewGroup.cmd = "newgroup"
                bb = CompassPanel.newbtnpanel(NewItem + [Trash, Undo, NewGroup])
                bb.margins = (2,1)

        self.bs_multipagespanel(bottompanel)
        self.bs_userobjects(toppanel)
        HintPanel = bottompanel.newbottompanel(16,0)
        self.hintcontrol = HintPanel.newimagectrl()
        self.hintcontrol.ondraw = self.drawhint
        self.hintcontrol.hint = "|Your mouse is in the hint box."


    def setgrid(self, editor):
        "Update the display on the 'grid' button."
        try:
            gridbtn = self.buttons["grid"]
        except:
            return
        if editor.gridstep:
            gridbtn.caption = quarkx.ftos(editor.gridstep)
        else:
            gridbtn.caption = "off"
        gridbtn.state = editor.grid and qtoolbar.selected
        quarkx.update(self.editor.form)


    def fffsetangle(self, view):
        if hasattr(self.mpp.currentpage(), "needangle"):
            self.mpp.resetpage()
        self.compass.AngleChanged(view)



    def autozoom1click(self, m):
        "The zoom button, when we click on the text, not the icon."
        def autozoom(list, self=self):
            scale1, center1 = AutoZoom(self.views, quarkx.boundingboxof(list), scale1=self.MAXAUTOZOOM)
            return (scale1 is not None) and self.editor.setscaleandcenter(scale1, center1)
        autozoom([self.editor.Root]) or autozoom(self.explorer.sellist)


    def getgridmenu(self, gridbtn):
        grid = self.editor.gridstep
        gridmenu = []
        for g in (0, 4096, 2048, 1024,512,256,128,64,32,16,8,4,2,1,.5,.25,.1):
            if g:
                cap = "grid \t%s" % g
            else:
                cap = "no grid"
            item = qmenu.item(cap, self.editor.gridmenuclick)
            item.grid = g
            item.state = g==grid and qmenu.radiocheck
            gridmenu.append(item)
        gridmenu.append(qmenu.sep)
        if grid==0:
            txt = "&Other..."
        else:
            txt = "&Other...\t%s" % quarkx.ftos(grid)
        gridmenu.append(qmenu.item(txt, self.editor.customgrid))
        return gridmenu


    def screencenter(self):
        pt = self.editor.interestingpoint()
        if pt is None:
            return self.views[0].screencenter
        else:
            return pt


    def helpbtnclick(self, m):
        htmldoc("")

    def update3Dviews(self, newview=None):
        if newview is not None:
            newview.oncameramove = self.cameramoved
        import mdleditor
        if isinstance(self.editor, mdleditor.ModelEditor) and quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] is not None:
            from qbaseeditor import currentview
            if currentview.info['viewname'] == "editors3Dview":
                pass
            else:
                self.editor.lastscale = 0    # force a call to buildhandles()
                for v in self.views:
                    if v is not newview:
                        v.info["timer"] = 1
                        quarkx.settimer(RefreshView, v, 200)
        else:
            self.editor.lastscale = 0    # force a call to buildhandles()
            for v in self.views:
                if v is not newview:
                    v.info["timer"] = 1
                    quarkx.settimer(RefreshView, v, 200)

    cameramoved = update3Dviews

    def postinitviews(self):
        for v in self.views:
            if v.info["type"] == "3D":
                v.oncameramove = self.cameramoved

    def drawhint(self, ctrl):
        cv = ctrl.canvas()
        cv.brushcolor = ctrl.color
        if quarkx.setupsubset(SS_MAP, "Colors")["InvertedColors"]:
            fg = WHITE
        else:
            fg = BLACK
        cv.fontcolor = fg
        w,h = ctrl.clientarea
        #cv.penstyle = PS_CLEAR
        #cv.rectangle(0,0, w,h)
        w=w-1
        h=h-1
        cv.penstyle = PS_SOLID
        bg = cv.brushcolor
        cv.pencolor = quarkx.middlecolor(fg, bg, 0.5)
        cv.line(0,h, 0,0)
        cv.line(0,0, w,0)
        cv.pencolor = quarkx.middlecolor(fg, bg, -0.3)
        cv.line(w,h, 0,h)
        s = self.hinttext
        if s[:1] == "|":
            cv.textout(13,2, "Press")
            x = 14+cv.textsize("Press")[0]
            cv.fontbold = 1
            cv.textout(x, 2, " F1 ")
            x = x+cv.textsize(" F1 ")[0]
            cv.fontbold = 0
            cv.textout(x, 2, "for help")
            delay = 1
        else:
            cv.textout(4,2, s)
            delay = 0
        cv.line(w,0, w,h)


    def UnlockViews(self):
        if self.oldsblinks is None:
            self.oldsblinks = self.sblinks
        self.sblinks = []
        for view in self.views:
            if not view.info.has_key("custom"):
                view.info["custom"] = defsetprojmode
                view.info["oldflags"] = view.flags
                view.flags = view.flags | MV_HSCROLLBAR | MV_VSCROLLBAR

    def LockViews(self):
        if self.oldsblinks is not None:
            self.sblinks = self.oldsblinks
            self.oldsblinks = None
        scale = None
        for view in self.views:
            if scale is None:
                try:
                    scale = view.info["scale"]
                except:
                    pass
            try:
                test = view.info["custom"]
            except:
                continue
            if test is defsetprojmode:
                view.invalidate()
                del view.info["custom"]
                view.flags = view.info["oldflags"]
                del view.info["oldflags"]
        if scale is not None:
            setviews(self.views, "scale", scale)


def RefreshView(v):
    try:
        del v.info["timer"]
    except:
        pass
    v.invalidate()


class MPPage:
    "A page in the multi-pages panel."

    def __init__(self, layout, panel):
        self.layout = layout
        self.panel = panel

    def button(self):
        raise "You must override the method 'button' of the class 'MPPage'" # abstract

# ----------- REVISION HISTORY ------------
#
#
#$Log: qbasemgr.py,v $
#Revision 1.41  2011/06/29 20:43:28  cdunde
#Fixed problem with icon buttons sometimes disappearing next to compass.
#
#Revision 1.40  2011/03/10 20:56:39  cdunde
#Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
#and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
#Revision 1.39  2011/03/02 04:19:45  cdunde
#InfoBase link update.
#
#Revision 1.38  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.37  2010/06/06 04:04:24  cdunde
#Fix to draw Eye handles in model editor floating 3D views when first opened.
#
#Revision 1.36  2010/05/12 08:07:13  cdunde
#Added Eye camera handle when in True 3D mode for easier navigation.
#
#Revision 1.35  2010/04/07 21:12:12  cdunde
#To fix crash from pervious update change when switching editors without closing QuArK.
#
#Revision 1.34  2010/03/26 07:28:42  cdunde
#To add new Model Editor sub-group folders to the Skins group.
#
#Revision 1.33  2008/02/03 00:55:08  cdunde
#To stop the progress bar from showing in the OpenGL window for the Model Editor
#
#Revision 1.32  2007/10/11 09:58:34  cdunde
#To keep the fillcolor correct for the editors 3D view after a
#tree-view selection is made with the floating 3D view window open and
#to stop numerous errors and dupe drawings when the floating 3D view window is closed.
#
#Revision 1.31  2007/07/28 23:11:58  cdunde
#To open and close floating 3D window(s) in Model Editor and
#try to keep all views 3D Options color settings correct.
#
#Revision 1.30  2007/03/27 22:36:29  danielpharos
#Fixed a stupid bug.
#
#Revision 1.29  2007/03/27 22:28:43  danielpharos
#Fixed a stupid bug with some new options. CloseOnSetup is now enabled by default too.
#
#Revision 1.28  2007/03/27 15:48:58  danielpharos
#Re-added the ability to open multiple floating 3D windows! This time there's an option to toggle it on and off in the options.
#
#Revision 1.27  2007/01/21 19:44:44  cdunde
#To change view name for floating Full 3D view for separate
#control of options from Model Editor 3D view.
#
#Revision 1.26  2006/12/17 08:59:54  cdunde
#Needed to reverse this change, caused an error when the floating 3D window is opened.
#
#Revision 1.25  2006/12/13 04:51:44  cdunde
#The def update3Dviews has to be there or an error occurs when you try to open
#the Floating 3D view window, but other than that, it does not seem to do anything
#but maybe add one EXTRA build cycle of all the views (2D and 3D) handles
#which seems to get done ANYWAY by some other function someplace. So another slow down.
#The update3Dviews is also called in the mapmgr.py file and again has no effect.
#The same goes for the cameramoved just below that calls it.
#update3Dviews is called a number of places from within qbasemgr.py when the
#Floating 3D window is opened and closed but still is not effective and should
#be removed completely and from all other files that call it, mapmgr.py.
#I believe its function was to cause a redraw of everything in all views primarily
#when the Floating 3D view was closed to eliminate things being erased from those view.
#But apparently other functions are doing that anyway so this is not needed any more.
#
#Revision 1.24  2006/12/03 21:21:51  danielpharos
#Disable fade in the model editors floating 3D window
#
#Revision 1.23  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.22  2006/11/29 07:00:28  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.21.2.8  2006/11/04 00:52:59  cdunde
#To navigate with the mouse just like it does
#in the Map Editor and the Model Editor 3D views.
#
#Revision 1.21.2.7  2006/11/03 23:38:09  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.21.2.6  2006/11/01 22:22:41  danielpharos
#BackUp 1 November 2006
#Mainly reduce OpenGL memory leak
#
#Revision 1.21  2006/01/31 08:43:46  cdunde
#Increased scale range to allow displaying for increased zoom range.
#
#Revision 1.20  2006/01/30 10:07:13  cdunde
#Changes by Nazar to the scale, zoom and map sizes that QuArK can handle
#to allow the creation of much larger maps for the more recent games.
#
#Revision 1.19  2005/10/20 03:16:12  cdunde
#Added to open 3D window title for clarity
#as to which type was being viewed
#
#Revision 1.18  2005/10/17 21:27:35  cdunde
#To add new key word "viewname" to all 3D views for easier
#detection and control of those views and Infobase documentation.
#
#Revision 1.17  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.14  2004/02/03 06:33:18  cdunde
#To turn off annoying hint
#
#Revision 1.13  2003/12/17 13:58:59  peter-b
#- Rewrote defines for setting Python version
#- Removed back-compatibility with Python 1.5
#- Removed reliance on external string library from Python scripts
#
#Revision 1.12  2003/07/07 07:18:31  cdunde
#To correct caption exclusion error and hint display
#
#Revision 1.11  2003/03/24 08:58:07  cdunde
#To update info and link to infobase
#
#Revision 1.10  2003/03/21 05:57:05  cdunde
#Update infobase and add links
#
#Revision 1.8  2003/02/01 02:13:22  cdunde
#Add items to grid selection
#
#Revision 1.7  2001/10/22 10:26:17  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.6  2001/01/26 19:07:26  decker_dk
#bs_multipagespanel. Better indication of keys '1'-'5', which are actually shortcut-keys to the tree-view and  alike panels.
#
#Revision 1.5  2000/12/17 09:43:41  decker_dk
#Some comments about menu settings, as the indexes are hardcoded!
#
#Revision 1.4  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#
