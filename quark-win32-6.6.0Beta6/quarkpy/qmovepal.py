"""   QuArK  -  Quake Army Knife

The Movement Toolbar Palette.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/quarkpy/qmovepal.py,v 1.24 2009/06/03 05:16:22 cdunde Exp $


import qtoolbar
import qmacro
from qeditor import *
from qdictionnary import Strings



def readmpvalues(spec, mode):
    quarkx.globalaccept()
    try:
        setup = qmacro.dialogboxes[ConfigDialog.__name__].info.src
    except:
        setup = quarkx.setupsubset(mode, "Building")
    return setup[spec]


def btnclick(btn, mode=SS_MAP):
    if mode == 3:
        import mdleditor
        editor = mdleditor.mdleditor
    else:
        editor = mapeditor(mode)
    if editor is None: return
    offset = matrix = inflate = val = None
    try:
        val = readmpvalues(btn.spec, mode)
    except:
        pass
    try:
        offset = btn.offset
        offset = apply(offset, val)
    except:
        pass
    try:
        matrix = btn.matrix
        matrix = apply(matrix, val)
    except:
        pass
    try:
        inflate = btn.inflate
        inflate = apply(inflate, val)
    except:
        pass
    if mode==SS_MAP:
        import mapbtns
        mapbtns.moveselection(editor, btn.text, offset, matrix, inflate=inflate)
    else:
        import mdlbtns
        mdlbtns.moveselection(editor, btn.text, offset, matrix, inflate=inflate)



class ConfigDialog(qmacro.dialogbox):
    "The Map Editor's Movement Tool Palette configuration dialog box."

    #
    # Dialog box shape
    #

    dlgflags = FWF_NOESCCLOSE
    begincolor = RED
    endcolor = MAROON
    size = (300,198)
    dlgdef = """
      {
        Style = "9"
        Caption = "Movement Tool Palette"
        sep: = {Typ="S" Txt=" "}    // some space
        mpOffset: = {
          Txt="Move selection (x, y, z) :"
          Typ="EF3"
          Hint="x, y, z values to add to the coordinates in order to move the selection"
        }
        mpZoom: = {
          Txt="Zoom factor :"
          Typ="EF1"
          Min='1'
          Hint="scaling factor for enlarge and shrink"
        }
        WallWidth: = {
          Txt="Inflate/Deflate by :"
          Typ="EF1"
          Hint="positive values inflate the polyhedrons, negative values deflate them"
        }
        mpRotate: = {
          Txt="Rotation angle :"
          Typ="EF1"
          Hint="the angle that each rotation makes the objects turn"
        }
        sep: = {Typ="S" Txt=" "}    // some space
        sep: = {Typ="S" Txt=""}    // a separator line
        ok:py = {Txt="" }
        cancel:py = {Txt="" }
      }
    """

    def __init__(self, menu):
        try:
            self.mode = menu.mode
        except:
            self.mode = menu
        setup = quarkx.setupsubset(self.mode, "Building").copy()
        qmacro.dialogbox.__init__(self, quarkx.clickform, setup,
          ok = qtoolbar.button(self.close, "close this box", ico_editor, 3, "Close"),
          cancel = qtoolbar.button(self.cancel, "cancel changes", ico_editor, 0, "Cancel"))

    def onclose(self, dlg):
        if self.src is not None:
            quarkx.globalaccept()
            setup = quarkx.setupsubset(self.mode, "Building")
            setup.copyalldata(self.src)
        qmacro.dialogbox.onclose(self, dlg)

    def cancel(self, reserved):
        self.src = None
        self.close()



class MdlConfigDialog(qmacro.dialogbox):
    "The Model Editor's Movement Tool Palette configuration dialog box."

    #
    # Dialog box shape
    #

    dlgflags = FWF_NOESCCLOSE
    begincolor = RED
    endcolor = MAROON
    size = (300,390)
    dlgdef = """
      {
        Style = "9"
        Caption = "Movement Tool Palette"
        sep: = {Typ="S" Txt=" "}    // some space
        mpOffset: = {
          Txt="Move selection (x, y, z) :"
          Typ="EF3"
          Hint="x, y, z values to add to the coordinates in order to move the selection"
        }
        mpZoom: = {
          Txt="Zoom factor :"
          Typ="EF1"
          Min='1'
          Hint="scaling factor for enlarge and shrink"
        }
        WallWidth: = {
          Txt="Shift Left/Right by :"
          Typ="EF1"
          Hint="negative values shifts the selection to the left,"$0D"positive values shifts the selection to the right"
        }
        mpRotate: = {
          Txt="Rotation angle :"
          Typ="EF1"
          Hint="the angle that each rotation makes the objects turn"
        }
        sep: = {Typ="S" Txt="Linear Handle settings"}    // designator title
        LinearSetting: = {
          Txt="Linear Handle Setting :"
          Typ="EF"
          Min="0.01"
          Hint="larger value makes the handle bigger & visa-versa, default is 4"
        }
        LinearSelected: = {
          Txt="Linear Items Size :"
          Typ="EF"
          Min="0.01"
          Hint="larger value makes the selected items bigger & visa-versa, default is 5"
        }
        SkinLinearSetting: = {
          Txt="Skin-view Linear Setting :"
          Typ="EF"
          Min="0.01"
          Hint="larger value makes the handle bigger & visa-versa, default is 4"
        }
        SkinLinearSelected: = {
          Txt="Skin-view Items Size :"
          Typ="EF"
          Min="0.01"
          Hint="larger value makes the selected items & visa-versa, default is 5"
        }
        sep: = {Typ="S" Txt="Bone Handle settings"}    // designator title
        RotationHandleLength: = {
          Txt="Rotation Handle Length :"
          Typ="EF"
          Min="0.01"
          Hint="larger value makes the handle longer & visa-versa, default is 1"
        }
        sep: = {Typ="S" Txt=" "}    // some space
        sep: = {Typ="S" Txt=""}    // a separator line
        applychange:py = {Txt="" }
        ok:py = {Txt="" }
        cancel:py = {Txt="" }
      }
    """

    def __init__(self, menu):
        try:
            self.mode = menu.mode
        except:
            self.mode = menu
        import mdleditor
        editor = mdleditor.mdleditor
        self.editor = editor
        setup = quarkx.setupsubset(self.mode, "Building").copy()
        qmacro.dialogbox.__init__(self, quarkx.clickform, setup,
          applychange = qtoolbar.button(self.apply, "apply the change", ico_editor, 1, "Apply"),
          ok = qtoolbar.button(self.close, "apply and close", ico_editor, 3, "Close"),
          cancel = qtoolbar.button(self.cancel, "cancel changes", ico_editor, 0, "Cancel"))

    def apply(self, dlg):
        if self.src is not None:
            quarkx.globalaccept()
            setup = quarkx.setupsubset(self.mode, "Building")
            setup.copyalldata(self.src)
            import mdlmgr
            mdlmgr.treeviewselchanged = 1
            bones = self.editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone')   # get all bones
            if len(bones) != 0 or len(self.editor.ModelVertexSelList) > 1 or len(self.editor.ModelFaceSelList) > 1 or len(self.editor.SkinVertexSelList) > 1:
                quarkx.reloadsetup()
                from mdlhandles import SkinView1
                if SkinView1 is not None:
                    import mdlhandles
                    try:
                        skindrawobject = self.editor.Root.currentcomponent.currentskin
                    except:
                        skindrawobject = None
                    mdlhandles.buildskinvertices(self.editor, SkinView1, self.editor.layout, self.editor.Root.currentcomponent, skindrawobject)

    def onclose(self, dlg):
        if self.src is not None:
            quarkx.globalaccept()
            setup = quarkx.setupsubset(self.mode, "Building")
            setup.copyalldata(self.src)
            import mdlmgr
            mdlmgr.treeviewselchanged = 1
            bones = self.editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone')   # get all bones
            if len(bones) != 0 or len(self.editor.ModelVertexSelList) > 1 or len(self.editor.ModelFaceSelList) > 1 or len(self.editor.SkinVertexSelList) > 1:
                quarkx.reloadsetup()
                from mdlhandles import SkinView1
                if SkinView1 is not None:
                    import mdlhandles
                    try:
                        skindrawobject = self.editor.Root.currentcomponent.currentskin
                    except:
                        skindrawobject = None
                    mdlhandles.buildskinvertices(self.editor, SkinView1, self.editor.layout, self.editor.Root.currentcomponent, skindrawobject)
        qmacro.dialogbox.onclose(self, dlg)

    def cancel(self, reserved):
        self.src = None
        self.close()



class ToolMoveBar(ToolBar):
    "The Movement Tool Palette."

    Caption = "Movement Tool Palette"
    DefaultPos = ((0, 0, 0, 0), 'topdock', 0, 1, 1)

    def buildbuttons(self, layout):
        if not ico_dict.has_key('ico_movepal'):
            ico_dict['ico_movepal']=LoadIconSet1("movepal", 1.0)
        icons = ico_dict['ico_movepal']

        def sendbtnclickmode(self, layout=layout):
            mode = layout.editor.MODE
            btnclick(self, mode)
        btn1 = qtoolbar.button(sendbtnclickmode, "Move selection||Move selection:\n\nOffsets the selected objects by the distance specified in the toolbar settings (last button of this toolbar).", icons, 1, infobaselink="intro.mapeditor.toolpalettes.movement.html#move")
        btn1.text = Strings[552]
        btn1.spec = "mpOffset"
        btn1.offset = quarkx.vect

        mdlbtn1 = qtoolbar.button(sendbtnclickmode, "Move selection||Move selection:\n\nOffsets the selected objects by the distance specified in the toolbar settings (last button of this toolbar).", icons, 1, infobaselink="intro.modeleditor.toolpalettes.movement.html#move")
        mdlbtn1.text = Strings[552]
        mdlbtn1.spec = "mpOffset"
        mdlbtn1.offset = quarkx.vect

        btn2 = qtoolbar.button(sendbtnclickmode, "Enlarge||Enlarge:\n\nEnlarges the selected objects by a factor specified in the toolbar settings (last button of this toolbar).", icons, 2, infobaselink="intro.mapeditor.toolpalettes.movement.html#enlargeshrink")
        btn2.text = Strings[548]
        btn2.spec = "mpZoom"
        btn2.matrix = matrix_zoom

        mdlbtn2 = qtoolbar.button(sendbtnclickmode, "Enlarge||Enlarge:\n\nEnlarges the selected objects by a factor specified in the toolbar settings (last button of this toolbar).", icons, 2, infobaselink="intro.modeleditor.toolpalettes.movement.html#enlargeshrink")
        mdlbtn2.text = Strings[548]
        mdlbtn2.spec = "mpZoom"
        mdlbtn2.matrix = matrix_zoom

        btn3 = qtoolbar.button(sendbtnclickmode, "Shrink||Shrink:\n\nShrinks the selected objects by a factor specified in the toolbar settings (last button of this toolbar).", icons, 3, infobaselink="intro.mapeditor.toolpalettes.movement.html#enlargeshrink")
        btn3.text = Strings[548]
        btn3.spec = "mpZoom"
        btn3.matrix = lambda f: matrix_zoom(1.0/f)

        mdlbtn3 = qtoolbar.button(sendbtnclickmode, "Shrink||Shrink:\n\nShrinks the selected objects by a factor specified in the toolbar settings (last button of this toolbar).", icons, 3, infobaselink="intro.modeleditor.toolpalettes.movement.html#enlargeshrink")
        mdlbtn3.text = Strings[548]
        mdlbtn3.spec = "mpZoom"
        mdlbtn3.matrix = lambda f: matrix_zoom(1.0/f)

        btn4 = qtoolbar.button(sendbtnclickmode, "X symmetry||X-symmetry:\n\n Mirror around the selection's common X-axis.\n\nThese buttons will mirror your selection, around its common center. To see the common center of your selected object(s), you must be able to see the 'Linear handle' of the selection.", icons, 5, infobaselink="intro.mapeditor.toolpalettes.movement.html#mirror")
        btn4.text = Strings[551]
        btn4.matrix = matrix_sym('x')

        mdlbtn4 = qtoolbar.button(sendbtnclickmode, "X symmetry||X-symmetry:\n\n Mirror around the selection's common X-axis.\n\nThese buttons will mirror your selection, around its common center. To see the common center of your selected object(s), you must be able to see the 'Linear handle' of the selection.", icons, 5, infobaselink="intro.modeleditor.toolpalettes.movement.html#mirror")
        mdlbtn4.text = Strings[551]
        mdlbtn4.matrix = matrix_sym('x')

        btn5 = qtoolbar.button(sendbtnclickmode, "Y symmetry||Y-symmetry:\n\n Mirror around the selection's common Y-axis.\n\nThese buttons will mirror your selection, around its common center. To see the common center of your selected object(s), you must be able to see the 'Linear handle' of the selection.", icons, 6, infobaselink="intro.mapeditor.toolpalettes.movement.html#mirror")
        btn5.text = Strings[551]
        btn5.matrix = matrix_sym('y')

        mdlbtn5 = qtoolbar.button(sendbtnclickmode, "Y symmetry||Y-symmetry:\n\n Mirror around the selection's common Y-axis.\n\nThese buttons will mirror your selection, around its common center. To see the common center of your selected object(s), you must be able to see the 'Linear handle' of the selection.", icons, 6, infobaselink="intro.modeleditor.toolpalettes.movement.html#mirror")
        mdlbtn5.text = Strings[551]
        mdlbtn5.matrix = matrix_sym('y')

        btn6 = qtoolbar.button(sendbtnclickmode, "Z symmetry||Z-symmetry:\n\n Mirror around the selection's common Z-axis.\n\nThese buttons will mirror your selection, around its common center. To see the common center of your selected object(s), you must be able to see the 'Linear handle' of the selection.", icons, 4, infobaselink="intro.mapeditor.toolpalettes.movement.html#mirror")
        btn6.text = Strings[551]
        btn6.matrix = matrix_sym('z')

        mdlbtn6 = qtoolbar.button(sendbtnclickmode, "Z symmetry||Z-symmetry:\n\n Mirror around the selection's common Z-axis.\n\nThese buttons will mirror your selection, around its common center. To see the common center of your selected object(s), you must be able to see the 'Linear handle' of the selection.", icons, 4, infobaselink="intro.modeleditor.toolpalettes.movement.html#mirror")
        mdlbtn6.text = Strings[551]
        mdlbtn6.matrix = matrix_sym('z')

        btn7 = qtoolbar.button(sendbtnclickmode, "X-axis rotation\nclockwise||X-axis rotation clockwise:\n\nRotates the selected objects clockwise around the X axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 8, infobaselink="intro.mapeditor.toolpalettes.movement.html#rotate")
        btn7.text = Strings[550]
        btn7.spec = "mpRotate"
        btn7.matrix = lambda f: matrix_rot_x(f * deg2rad)

        mdlbtn7 = qtoolbar.button(sendbtnclickmode, "X-axis rotation\nclockwise||X-axis rotation clockwise:\n\nRotates the selected objects clockwise around the X axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 8, infobaselink="intro.modeleditor.toolpalettes.movement.html#rotate")
        mdlbtn7.text = Strings[550]
        mdlbtn7.spec = "mpRotate"
        mdlbtn7.matrix = lambda f: matrix_rot_x(f * deg2rad)

        btn8 = qtoolbar.button(sendbtnclickmode, "X-axis rotation\ncounterclockwise||X-axis rotation counterclockwise:\n\nRotates the selected objects counterclockwise around the X axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 11, infobaselink="intro.mapeditor.toolpalettes.movement.html#rotate")
        btn8.text = Strings[550]
        btn8.spec = "mpRotate"
        btn8.matrix = lambda f: matrix_rot_x(-f * deg2rad)

        mdlbtn8 = qtoolbar.button(sendbtnclickmode, "X-axis rotation\ncounterclockwise||X-axis rotation counterclockwise:\n\nRotates the selected objects counterclockwise around the X axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 11, infobaselink="intro.modeleditor.toolpalettes.movement.html#rotate")
        mdlbtn8.text = Strings[550]
        mdlbtn8.spec = "mpRotate"
        mdlbtn8.matrix = lambda f: matrix_rot_x(-f * deg2rad)

        btn9 = qtoolbar.button(sendbtnclickmode, "Y-axis rotation\nclockwise||Y-axis rotation clockwise:\n\nRotates the selected objects clockwise around the Y axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 9, infobaselink="intro.mapeditor.toolpalettes.movement.html#rotate")
        btn9.text = Strings[550]
        btn9.spec = "mpRotate"
        btn9.matrix = lambda f: matrix_rot_y(-f * deg2rad)

        mdlbtn9 = qtoolbar.button(sendbtnclickmode, "Y-axis rotation\nclockwise||Y-axis rotation clockwise:\n\nRotates the selected objects clockwise around the Y axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 9, infobaselink="intro.modeleditor.toolpalettes.movement.html#rotate")
        mdlbtn9.text = Strings[550]
        mdlbtn9.spec = "mpRotate"
        mdlbtn9.matrix = lambda f: matrix_rot_y(-f * deg2rad)

        btn10 = qtoolbar.button(sendbtnclickmode, "Y-axis rotation\ncounterclockwise||Y-axis rotation counterclockwise:\n\nRotates the selected objects counterclockwise around the Y axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 12, infobaselink="intro.mapeditor.toolpalettes.movement.html#rotate")
        btn10.text = Strings[550]
        btn10.spec = "mpRotate"
        btn10.matrix = lambda f: matrix_rot_y(f * deg2rad)

        mdlbtn10 = qtoolbar.button(sendbtnclickmode, "Y-axis rotation\ncounterclockwise||Y-axis rotation counterclockwise:\n\nRotates the selected objects counterclockwise around the Y axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 12, infobaselink="intro.modeleditor.toolpalettes.movement.html#rotate")
        mdlbtn10.text = Strings[550]
        mdlbtn10.spec = "mpRotate"
        mdlbtn10.matrix = lambda f: matrix_rot_y(f * deg2rad)

        btn11 = qtoolbar.button(sendbtnclickmode, "Z-axis rotation\nclockwise||Z-axis rotation clockwise:\n\nRotates the selected objects clockwise around the Z axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 10, infobaselink="intro.mapeditor.toolpalettes.movement.html#rotate")
        btn11.text = Strings[550]
        btn11.spec = "mpRotate"
        btn11.matrix = lambda f: matrix_rot_z(-f * deg2rad)

        mdlbtn11 = qtoolbar.button(sendbtnclickmode, "Z-axis rotation\nclockwise||Z-axis rotation clockwise:\n\nRotates the selected objects clockwise around the Z axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 10, infobaselink="intro.modeleditor.toolpalettes.movement.html#rotate")
        mdlbtn11.text = Strings[550]
        mdlbtn11.spec = "mpRotate"
        mdlbtn11.matrix = lambda f: matrix_rot_z(-f * deg2rad)

        btn12 = qtoolbar.button(sendbtnclickmode, "Z-axis rotation\ncounterclockwise||Z-axis rotation counterclockwise:\n\nRotates the selected objects counterclockwise around the Z axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 7, infobaselink="intro.mapeditor.toolpalettes.movement.html#rotate")
        btn12.text = Strings[550]
        btn12.spec = "mpRotate"
        btn12.matrix = lambda f: matrix_rot_z(f * deg2rad)

        mdlbtn12 = qtoolbar.button(sendbtnclickmode, "Z-axis rotation\ncounterclockwise||Z-axis rotation counterclockwise:\n\nRotates the selected objects counterclockwise around the Z axis by an angle specified in the toolbar CFG settings (last button of this toolbar).\nTo display an X, Y or Z axis icon in their respective 2-D view window,\nClick on the Options menu and select the Axis XYZ letter item.", icons, 7, infobaselink="intro.modeleditor.toolpalettes.movement.html#rotate")
        mdlbtn12.text = Strings[550]
        mdlbtn12.spec = "mpRotate"
        mdlbtn12.matrix = lambda f: matrix_rot_z(f * deg2rad)

        btn13 = qtoolbar.button(sendbtnclickmode, "Inflate/Deflate||Inflate/Deflate:\n\nInflate or deflate the selected objects by an amount specified in the toolbar settings (last button of this toolbar).\n\nInflating or deflating means moving the planes of the faces of the polyhedrons by a fixed amount of pixels. This is not the same as simply zooming, which preserves the aspect of the polyhedron.\n\nThis setting is also used for the Make Hollow function for two different atributes.\n\n1)  The number set will be the thickness of the walls created in units.\n\n2)  If the number is positive, the walls will be created outside the perimeter of the current solid polygon.\nIf the number is negative, the walls will be created inside the perimeter of the current solid polygon.", icons, 13, infobaselink="intro.mapeditor.toolpalettes.movement.html#inflatedeflate")
        btn13.text = Strings[549]
        btn13.spec = "WallWidth"
        btn13.inflate = lambda f: f

        mdlbtn13 = qtoolbar.button(sendbtnclickmode, "Shift Left/Right||Shift Left/Right:\n\nShift the selected vertexes or faces (not dependable for faces) Left or Right by an amount specified in the toolbar settings (last button of this toolbar).\n\nShifting Left or Right means moving the selected items by a fixed amount of pixels, negative values shifts the selection to the left, positive values shifts the selection to the right.", icons, 13, infobaselink="intro.modeleditor.toolpalettes.movement.html#inflatedeflate")
        mdlbtn13.text = Strings[2549]
        mdlbtn13.spec = "WallWidth"
        mdlbtn13.inflate = lambda f: f

        btncfg = qtoolbar.button(ConfigDialog, "Change this toolbar settings||Change this toolbar settings:\n\nThis opens the Movement toolbar configuration window.\n\nIf you hold your mouse cursor over each of the setting input areas, a description- help display will appear to give you information about what settings to use and how they work.\n\nClick the check mark to apply the new settings.\n\nClick the X to close the window without changing the current settings.", icons, 0, infobaselink="intro.mapeditor.toolpalettes.movement.html#configuration")
        btncfg.icolist = icons
        btncfg.mode = layout.MODE

        mdlbtncfg = qtoolbar.button(MdlConfigDialog, "Change this toolbar settings||Change this toolbar settings:\n\nThis opens the Movement toolbar configuration window.\n\nIf you hold your mouse cursor over each of the setting input areas, a description- help display will appear to give you information about what settings to use and how they work.\n\nClick the check mark to apply the new settings.\n\nClick the X to close the window without changing the current settings.", icons, 0, infobaselink="intro.modeleditor.toolpalettes.movement.html#configuration")
        mdlbtncfg.icolist = icons
        mdlbtncfg.mode = layout.MODE

        if layout.MODE == 2:
            return [btn1, btn2, btn3, btn13, qtoolbar.sep, btn4, btn5, btn6,
              btn7, btn8, btn9, btn10, btn11, btn12, qtoolbar.sep, btncfg]
        else:
            return [mdlbtn1, mdlbtn2, mdlbtn3, mdlbtn13, qtoolbar.sep, mdlbtn4, mdlbtn5, mdlbtn6,
              mdlbtn7, mdlbtn8, mdlbtn9, mdlbtn10, mdlbtn11, mdlbtn12, qtoolbar.sep, mdlbtncfg]

# ----------- REVISION HISTORY ------------
#
#
#$Log: qmovepal.py,v $
#Revision 1.24  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.23  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.22  2008/12/20 08:39:34  cdunde
#Minor adjustment to various Model Editor dialogs for recent fix of item over lapping by Dan.
#
#Revision 1.21  2008/09/22 23:11:12  cdunde
#Updates for Model Editor Linear and Bone handles.
#
#Revision 1.20  2008/05/01 19:15:24  danielpharos
#Fix treeviewselchanged not updating.
#
#Revision 1.19  2008/05/01 13:52:32  danielpharos
#Removed a whole bunch of redundant imports and other small fixes.
#
#Revision 1.18  2007/10/31 03:47:52  cdunde
#Infobase button link updates.
#
#Revision 1.17  2007/10/24 14:58:12  cdunde
#To activate all Movement toolbar button functions for the Model Editor.
#
#Revision 1.16  2007/10/11 09:57:33  cdunde
#To separate Map and Model editor's movepal toolbars and config dialogs.
#
#Revision 1.15  2007/09/07 23:55:29  cdunde
#1) Created a new function on the Commands menu and RMB editor & tree-view menus to create a new
#     model component from selected Model Mesh faces and remove them from their current component.
#2) Fixed error of "Pass face selection to Skin-view" if a face selection is made in the editor
#     before the Skin-view is opened at least once in that session.
#3) Fixed redrawing of handles in areas that hints show once they are gone.
#
#Revision 1.14  2007/08/20 19:58:23  cdunde
#Added Linear Handle to the Model Editor's Skin-view page
#and setup color selection and drag options for it and other fixes.
#
#Revision 1.13  2007/08/01 06:09:24  cdunde
#Setup variable setting for Model Editor 'Linear Handle (size) Setting' and
#'Rotation Speed' using the 'cfg' button on the movement toolbar.
#
#Revision 1.12  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.9  2004/01/24 16:27:03  cdunde
#To reset defaults for toolbars
#
#Revision 1.8  2003/03/15 20:41:07  cdunde
#To update hints and add infobase links
#
#Revision 1.7  2003/02/14 04:23:11  cdunde
#To add and update F1 popup info.
#
#Revision 1.6  2002/12/27 07:38:02  cdunde
#Rearranged icons with added help info
#
#Revision 1.5  2001/10/22 10:28:20  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.4  2001/06/17 21:05:27  tiglari
#fix button captions
#
#Revision 1.3  2001/06/16 03:20:48  tiglari
#add Txt="" to separators that need it
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#