"""   QuArK  -  Quake Army Knife

Tool Bars and Buttons
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/quarkpy/qtoolbar.py,v 1.7 2005/10/15 00:47:57 cdunde Exp $
#
import quarkx
from qutils import *

# button state
normal     = 0
selected   = 2
disabled   = 4    # can be added to the above



class button:
    "A ToolBar button."

    #
    # A button's onclick attribute must be a callback function,
    # called by QuArK when the user clicks on the button.
    # It will be called with the button object itself as parameter.
    #

    def __init__(self, onclick, hint, iconlist, iconindex, caption=None, capalways=0, infobaselink=''):
        self.onclick = onclick
        self.hint = hint
        self.state = normal
        self.caption = caption
        self.hint = hintPlusInfobaselink(hint, infobaselink)
        if capalways:
            self.capalways = 1
        if iconindex is None:
            if iconlist is None:
                self.icons = None
                self._icons = None
                self._cap = None
                return
            if len(iconlist)<3:
                icon, iconmouse = iconlist
                iconsel = iconmouse
            else:
                icon, iconmouse, iconsel = iconlist
        else:
            icon = iconlist[0][iconindex]
            iconmouse = iconlist[1][iconindex]
            if len(iconlist)<3:
                iconsel = iconmouse
            else:
                iconsel = iconlist[2][iconindex]
        self._icons = (icon, iconmouse, iconmouse, iconsel, iconsel, icon.disabledimage)
        self._cap = caption
        if caption:
            if BtnText:
                self.icons = None
            else:
                self.icons = self._icons
                if not capalways:
                    self.caption = None
        else:
            self.icons = self._icons
            self._icons = None

    def getcaption(self):
        if self.caption: return self.caption
        if self._cap: return self._cap
        s = self.hint
        try:
            return s[list(s).index('|')+1:]
        except:
            return s


def menubutton(menu, hint, iconlist, iconindex, infobaselink=''):
    "A button that drops down a menu."

    m = button(None, hint, iconlist, iconindex, infobaselink)
    m.menu = menu
    return m


def doublebutton(onclick, menu, hint, iconlist, iconindex, infobaselink=''):
    "A button with both a menu and direct clicks (e.g. the grid and zoom buttons)."

    hint = hintPlusInfobaselink(hint, infobaselink)
    m = button(onclick, hint, iconlist, iconindex)
    m.menu = menu
    return m


def toggle(btn):
    "Toggles the state of a button."
    btn.state = btn.state ^ selected
    quarkx.update()


def macrobtn(macro, hint, iconlist, iconindex, caption=None, infobaselink=""):
    "A button that executes a single macro command."
    b = button(macroclick, hint, iconlist, iconindex, caption, infobaselink)
    b.macro = macro
    return b

def macroclick(b):
    if not (quarkx.clickform is None):
        quarkx.clickform.macro(b.macro)


# a separator line in the toolbar
sep = None

# special separators for button panels (not for toolbars)
smallgap  = None
widegap   = 1
padright  = 2   # the next button only is sent at the right end of the line
newline   = 3


def BtnPrefChanged(level):
    global BtnText
    BtnText1 = quarkx.setupsubset(qutils.SS_GENERAL, "Display")["BtnText"]
    if (not BtnText) == (not BtnText1):
        return
    BtnText = BtnText1
    for f in quarkx.forms():
        for tb in f.toolbars() + f.btnpanels():
            for b in tb.buttons:
                if not (b in (sep, smallgap, widegap, padright, newline)):
                    if BtnText:
                        if b.icons is b._icons:
                            b.icons = None
                        if not b.caption:
                            b.caption = b._cap
                    else:
                        if b.caption is b._cap and not hasattr(b, "capalways"):
                            b.caption = None
                        if b.icons is None:
                            b.icons = b._icons
            tb.update()

import qutils
qutils.SetupRoutines.append(BtnPrefChanged)
BtnText = quarkx.setupsubset(qutils.SS_GENERAL, "Display")["BtnText"]

# ----------- REVISION HISTORY ------------
#
#
#$Log: qtoolbar.py,v $
#Revision 1.7  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.4  2003/03/16 02:42:34  tiglari
#Added infobaselink arg to a few more buttons
#
#Revision 1.3  2003/03/15 20:40:50  cdunde
#To update hints and add infobase links
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#