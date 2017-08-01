"""   QuArK  -  Quake Army Knife

"Background image" dialog box for map views.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/qbackbmp.py,v 1.13 2009/07/06 18:17:58 danielpharos Exp $



import quarkx
import qmacro
import qtoolbar
from qeditor import *

class BackBmpDlg(qmacro.dialogbox):

    #
    # dialog layout for the Map Editor
    #

    dfsep = 0.5
    dlgflags = FWF_KEEPFOCUS
    size = (300,310)

    dlgdef = """
      {
        Style = "15"
        Caption = "Background image"
        info: = {Typ="S" Bold="0" Txt="use this feature to display a image"}
        info: = {Typ="S" Bold="0" Txt="from your scanner or from another program."}
        sep: = {Typ="S" Txt=""}
        filename: = {Typ="EP" DefExt="*" Txt="Background image file"}
        center: = {Typ="EF3" Txt="Coordinates of the center"}
        scale: = {Typ="EF1" Txt="Scale"}
        offset: =
        {
            Txt = "Center on picture center"
            Typ = "X"
            Hint = "Center on the center of the picture."
        }
        multiple: =
        {
            Txt = "Copy picture"
            Typ = "X"
            Hint = "Fill up the view with copies of the picture."
        }
        PolySelectNoFill: =
        {
            Txt = "Poly No Fill (map editor only)"
            Typ = "X"
            Hint = "Stops the filling of the selected Poly with color."$0D
                   "Makes it see through."
        }
        NoFillSel: =
        {
            Txt = "Color Guide (map editor only)"
            Typ = "LI"
            Hint = "The selected Poly(s) outline color."
        }
        sep: = {Typ="S" Txt=""}
        ok:py = {Txt="Apply and view changes"}
        remove:py = {Txt="Remove background image"}
        no:py = {Txt="Close this dialog"}
      }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, view):
        ico_maped=ico_dict['ico_maped']
        self.view = view
        #FIXME
        #DanielPharos: We should check if it's a 3D window. If so, don't allow a background!
        src = quarkx.newobj(":")
        if view.backgroundimage is None:
            src["filename"] = quarkx.setupsubset(SS_MAP, "Options")["BGImage_filename"]
            src["center"] = quarkx.setupsubset(SS_MAP, "Options")["BGImage_center"]
            src["scale"] = quarkx.setupsubset(SS_MAP, "Options")["BGImage_scale"]
            src["offset"] = quarkx.setupsubset(SS_MAP, "Options")["BGImage_offset"]
            src["multiple"] = quarkx.setupsubset(SS_MAP, "Options")["BGImage_multiple"]
            src["PolySelectNoFill"] = quarkx.setupsubset(SS_MAP, "Options")["PolySelectNoFill"]
            src["NoFillSel"] = quarkx.setupsubset(SS_MAP, "Colors").getint("NoFillSel")
        else:
            filename, center, scale, offset, multiple = view.background
            src["filename"] = filename
            src["center"] = center.tuple
            src["scale"] = scale,
            if offset == 0:
                src["offset"] = ""
            else:
                src["offset"] = "1"
            if multiple == 0:
                src["multiple"] = ""
            else:
                src["multiple"] = "1"
            src["PolySelectNoFill"] = quarkx.setupsubset(SS_MAP, "Options")["PolySelectNoFill"]
            src["NoFillSel"] = quarkx.setupsubset(SS_MAP, "Colors").getint("NoFillSel")
        qmacro.dialogbox.__init__(self, form, src,
            ok = qtoolbar.button(
                self.ok,
                "apply and view changes",
                ico_editor, 1,
                "Ok"),
            remove = qtoolbar.button(
                self.remove,
                "remove background image",
                ico_maped, 2,
                "No image"),
            no = qtoolbar.button(
                self.no,
                "close this dialog",
                ico_editor, 0,
                "Close"))

    def ok(self, m):
        quarkx.globalaccept()
        src = self.src
        filename = src["filename"]
        if filename:
            center = quarkx.vect(src["center"])
            scale, = src["scale"]
            if src["offset"] is None or src["offset"] == "":
                offset = 0
            else:
                offset = 1
            if src["multiple"] is None or src["multiple"] == "":
                multiple = 0
            else:
                multiple = 1
            PolySelectNoFill = src["PolySelectNoFill"]
            NoFillSel = src["NoFillSel"]
            self.view.background = center, scale, offset, multiple
            self.view.backgroundimage = filename,
          ### Save the settings...
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_filename"] = src["filename"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_center"] = src["center"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_scale"] = src["scale"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_offset"] = src["offset"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_multiple"] = src["multiple"]
            quarkx.setupsubset(SS_MAP, "Options")["PolySelectNoFill"] = PolySelectNoFill
            quarkx.setupsubset(SS_MAP, "Colors")["NoFillSel"] = NoFillSel
        else:
          ### Save the settings...
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_filename"] = src["BGImage_filename"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_center"] = src["BGImage_center"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_scale"] = src["BGImage_scale"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_offset"] = src["BGImage_offset"]
            quarkx.setupsubset(SS_MAP, "Options")["BGImage_multiple"] = src["BGImage_multiple"]
            quarkx.setupsubset(SS_MAP, "Options")["PolySelectNoFill"] = src["PolySelectNoFill"]
            quarkx.setupsubset(SS_MAP, "Colors")["NoFillSel"] = src["NoFillSel"]
        self.view.invalidate(1)

    def remove(self, m):
        src = self.src
        self.view.backgroundimage = None,
        filename = None
        src["filename"] = None
        center = src["BGImage_center"]
        scale = src["BGImage_scale"]
        offset = src["BGImage_offset"]
        multiple = src["BGImage_multiple"]
        PolySelectNoFill = src["PolySelectNoFill"]
        NoFillSel = src["NoFillSel"]
          ### Save the settings...
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_filename"] = None
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_center"] = src["center"]
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_scale"] = src["scale"]
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_offset"] = src["offset"]
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_multiple"] = src["multiple"]
        quarkx.setupsubset(SS_MAP, "Options")["PolySelectNoFill"] = PolySelectNoFill
        quarkx.setupsubset(SS_MAP, "Colors")["NoFillSel"] = NoFillSel
        self.view.invalidate(1)

    def no(self, m):
        src = self.src
        filename = src["BGImage_filename"]
        center = src["BGImage_center"]
        scale = src["BGImage_scale"]
        offset = src["BGImage_offset"]
        multiple = src["BGImage_multiple"]
        PolySelectNoFill = src["PolySelectNoFill"]
        NoFillSel = src["NoFillSel"]
          ### Save the settings...
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_filename"] = src["filename"]
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_center"] = src["center"]
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_scale"] = src["scale"]
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_offset"] = src["offset"]
        quarkx.setupsubset(SS_MAP, "Options")["BGImage_multiple"] = src["multiple"]
        quarkx.setupsubset(SS_MAP, "Options")["PolySelectNoFill"] = PolySelectNoFill
        quarkx.setupsubset(SS_MAP, "Colors")["NoFillSel"] = NoFillSel
        self.view.invalidate(1)
        self.close()

class MdlBackBmpDlg(qmacro.dialogbox):

    #
    # dialog layout for the Model Editor
    #

    dfsep = 0.5
    dlgflags = FWF_KEEPFOCUS
    size = (300,260)

    dlgdef = """
      {
        Style = "15"
        Caption = "Background image"
        info: = {Typ="S" Bold="0" Txt="use this feature to display a image"}
        info: = {Typ="S" Bold="0" Txt="from your scanner or from another program."}
        sep: = {Typ="S" Txt=""}
        filename: = {Typ="EP" DefExt="*" Txt="Background image file"}
        center: = {Typ="EF3" Txt="Coordinates of the center"}
        scale: = {Typ="EF1" Txt="Scale"}
        offset: =
        {
            Txt = "Center on picture center"
            Typ = "X"
            Hint = "Center on the center of the picture."
        }
        multiple: =
        {
            Txt = "Copy picture"
            Typ = "X"
            Hint = "Fill up the view with copies of the picture."
        }
        sep: = {Typ="S" Txt=""}
        ok:py = {Txt="Apply and view changes"}
        remove:py = {Txt="Remove background image"}
        no:py = {Txt="Close this dialog"}
      }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, view):
        ico_maped=ico_dict['ico_maped']
        self.view = view
        #FIXME
        #DanielPharos: We should check if it's a 3D window. If so, don't allow a background!
        src = quarkx.newobj(":")
        if view.backgroundimage is None:
            src["filename"] = quarkx.setupsubset(SS_MODEL, "Options")["BGImage_filename"]
            src["center"] = quarkx.setupsubset(SS_MODEL, "Options")["BGImage_center"]
            src["scale"] = quarkx.setupsubset(SS_MODEL, "Options")["BGImage_scale"]
            src["offset"] = quarkx.setupsubset(SS_MODEL, "Options")["BGImage_offset"]
            src["multiple"] = quarkx.setupsubset(SS_MODEL, "Options")["BGImage_multiple"]
        else:
            filename, center, scale, offset, multiple = view.background
            src["filename"] = filename
            src["center"] = center.tuple
            src["scale"] = scale,
            if offset == 0:
                src["offset"] = ""
            else:
                src["offset"] = "1"
            if multiple == 0:
                src["multiple"] = ""
            else:
                src["multiple"] = "1"
        qmacro.dialogbox.__init__(self, form, src,
            ok = qtoolbar.button(
                self.ok,
                "apply and view changes",
                ico_editor, 1,
                "Ok"),
            remove = qtoolbar.button(
                self.remove,
                "remove background image",
                ico_maped, 2,
                "No image"),
            no = qtoolbar.button(
                self.no,
                "close this dialog",
                ico_editor, 0,
                "Close"))

    def ok(self, m):
        quarkx.globalaccept()
        src = self.src
        filename = src["filename"]
        if filename:
            center = quarkx.vect(src["center"])
            scale, = src["scale"]
            if src["offset"] is None or src["offset"] == "":
                offset = 0
            else:
                offset = 1
            if src["multiple"] is None or src["multiple"] == "":
                multiple = 0
            else:
                multiple = 1
            self.view.background = center, scale, offset, multiple
            self.view.backgroundimage = filename,
          ### Save the settings...
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_filename"] = src["filename"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_center"] = src["center"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_scale"] = src["scale"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_offset"] = src["offset"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_multiple"] = src["multiple"]
        else:
          ### Save the settings...
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_filename"] = src["BGImage_filename"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_center"] = src["BGImage_center"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_scale"] = src["BGImage_scale"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_offset"] = src["BGImage_offset"]
            quarkx.setupsubset(SS_MODEL, "Options")["BGImage_multiple"] = src["BGImage_multiple"]
        self.view.invalidate(1)

    def remove(self, m):
        src = self.src
        self.view.backgroundimage = None,
        filename = None
        src["filename"] = None
        center = src["BGImage_center"]
        scale = src["BGImage_scale"]
        offset = src["BGImage_offset"]
        multiple = src["BGImage_multiple"]
          ### Save the settings...
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_filename"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_center"] = src["center"]
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_scale"] = src["scale"]
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_offset"] = src["offset"]
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_multiple"] = src["multiple"]
        self.view.invalidate(1)

    def no(self, m):
        src = self.src
        filename = src["BGImage_filename"]
        center = src["BGImage_center"]
        scale = src["BGImage_scale"]
        offset = src["BGImage_offset"]
        multiple = src["BGImage_multiple"]
          ### Save the settings...
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_filename"] = src["filename"]
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_center"] = src["center"]
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_scale"] = src["scale"]
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_offset"] = src["offset"]
        quarkx.setupsubset(SS_MODEL, "Options")["BGImage_multiple"] = src["multiple"]
        self.view.invalidate(1)
        self.close()

# ----------- REVISION HISTORY ------------
#
#
#$Log: qbackbmp.py,v $
#Revision 1.13  2009/07/06 18:17:58  danielpharos
#Fixed vertical scrollbar showing up.
#
#Revision 1.12  2008/02/06 00:12:44  danielpharos
#The skinview now properly updates to reflect changes made to textures.
#
#Revision 1.11  2007/11/22 05:13:47  cdunde
#Separated editors background image dialogs and setup to save all of their settings.
#
#Revision 1.10  2007/11/19 00:08:39  danielpharos
#Any supported picture can be used for a view background, and added two options: multiple, offset
#
#Revision 1.9  2007/04/11 15:52:00  danielpharos
#Fixed a crash. As a happy side-effect, it now only refreshes the view changed.
#
#Revision 1.8  2006/05/19 17:10:03  cdunde
#To add new transparent poly options for viewing background image.
#
#Revision 1.7  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
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