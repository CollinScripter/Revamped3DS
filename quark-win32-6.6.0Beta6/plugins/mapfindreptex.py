#-------------------------------------------------------------------------------
#
#       Module:         mapfindreptex.py
#       Subsystem:      mapfindreptex
#       Program:        mapfindreptex
#
#       Copyright (c) 1998 - Descartes Systems Sciences
#
#-------------------------------------------------------------------------------
#
#       Description:
#
#-------------------------------------------------------------------------------
#
#       $History: mapfindreptex $
#
#-------------------------------------------------------------------------------

#$Header: /cvsroot/quark/runtime/plugins/mapfindreptex.py,v 1.12 2005/10/15 00:49:51 cdunde Exp $



Info = {
   "plug-in":       "Search and replace textures",
   "desc":          "Search/replace textures dialog box, available from the Search menu.",
   "date":          "17 oct 98",
   "author":        "Tim Smith & Armin Rigo",
   "author e-mail": "",
   "quark":         "Version 5.0.c5" }


import quarkx
import quarkpy.qmacro
import quarkpy.qtoolbar
import quarkpy.mapsearch
from quarkpy.maputils import *

class SearchReplaceTextureDlg(quarkpy.qmacro.dialogbox):

    #
    # dialog layout
    #

    size = (300, 240)
    dfsep = 0.4        # separation at 40% between labels and edit boxes
    dlgflags = FWF_KEEPFOCUS

    dlgdef = """
      {
        Style = "15"
        Caption = "Search/replace textures"
        sep: = {Typ="S" Txt="By leaving the 'Replace with texture' blank or"}
        sep: = {Typ="S" Txt="equal to the 'Search for texture', this will"}
        sep: = {Typ="S" Txt="only perform a search-and-select-objects."}
        sep: = {Typ="S" Txt=" "}
        fromtex: = {
          Txt = "Search for texture:"
          Typ = "ET"
          SelectMe = "1"
        }
        totex: = {
          Txt = "Replace with texture:"
          Typ = "ET"
        }
        scope: = {
          Typ = "CL"
          Txt = "Search in:"
          Items = "%s"
          Values = "%s"
        }
        sep: = {Typ="S" Txt=" "}
        ReplaceAll:py = {Txt=""}
        close:py = {Txt=""}
      }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, editor):

        #
        # General initialization of some local values
        #

        self.editor = editor
        uniquesel = editor.layout.explorer.uniquesel
        self.sellist = self.editor.visualselection()

        #
        # Create the data source
        #

        src = quarkx.newobj(":")

        #
        # Based on the textures in the selections, initialize the
        # from and to textures
        #

        if len(self.sellist) == 0:
            texlist = quarkx.texturesof(editor.Root.findallsubitems("", ':f'))
        elif uniquesel is not None and uniquesel.type==":f":
            texlist = quarkx.texturesof([uniquesel])
        else:
            texlist = quarkx.texturesof(self.sellist);
        if len(texlist) == 0:
            texlist.append(quarkx.setupsubset()["DefaultTexture"])
        src["fromtex"] = texlist[0]
        src["totex"] = texlist[0]

        #
        # Based on the selection, populate the range combo box
        #

        if len(self.sellist) == 0:
            src["scope"] = "W"
            src["scope$Items"] = "Whole map"
            src["scope$Values"] = "W"
        else:
            src["scope"] = "S"
            src["scope$Items"] = "Selection\nWhole map"
            src["scope$Values"] = "S\nW"

        #
        # Create the dialog form and the buttons
        #

        quarkpy.qmacro.dialogbox.__init__(self, form, src,
           close      = quarkpy.qtoolbar.button(self.close, "Close this box", ico_editor, 0, "Close", 1),
           ReplaceAll = quarkpy.qtoolbar.button(self.ReplaceAll, "Search/replace textures", ico_editor, 2, "Search/replace", 1)
        )


    def deepsearch(self, objs, find, newsellist):
        # Performs a recursive search of ':f' objects, and appends them to a list
        for o in objs:
            if o.type == ':f':
                if o.texturename == find:
                    newsellist.append(o)
            else:
                if len(o.subitems) > 0:
                    self.deepsearch(o.subitems, find, newsellist)

    def ReplaceAll(self, btn):

        #
        # commit any pending changes in the dialog box
        #

        quarkx.globalaccept()

        #
        # read back data from the dialog box
        #

        whole = self.src["scope"] == "W"
        find = self.src["fromtex"]
        replace = self.src["totex"]
        if not find:
            quarkx.msgbox("Please specify texture name to search for.", MT_ERROR, MB_OK)
            return

        list = None
        if whole:
            list = self.editor.Root.findallsubitems("", ':f')
        else:
            list = self.sellist

        if not replace or replace == find:
            # No replace texture-name have been given. Then it must just be a "Search" the user intended.
            newsellist = []
            self.deepsearch(list, find, newsellist)

            # Set views to the new selection
            self.editor.layout.explorer.sellist = newsellist

            # Notify the user, we're finished searching
            txt = "%d faces selected" % len(newsellist)
            result = quarkx.msgbox(txt, MT_INFORMATION, MB_OK)

            # Close the search-dialogbox
            self.close()
        else:
            #
            # do the changes
            #
            changes = 0
            undo = quarkx.action()

            for o in list: # loop through the list
                changes = changes + o.replacetex(find, replace, 1)
            txt = None
            if changes:
                txt = "%d textures replaced" % changes
                mb = MB_OK_CANCEL
            else:
                txt = "No textures replaced"
                mb = MB_CANCEL
            result = quarkx.msgbox(txt, MT_INFORMATION, mb)

            #
            # commit or cancel the undo action
            #

            if result == MR_OK:
                undo.ok(self.editor.Root, "replace textures")   # note: calling undo.ok() when nothing has actually been done is the same as calling undo.cancel()
                #
                # Sorry, we have to close the dialog box, because the selection changed.
                # Allowing the user to make multiple replacements in the selection before committing them all
                #  would be a bit more complicated.
                #
                self.close()
            else:
                undo.cancel()

#
# Function to start the replace dialog
#

def SearchReplaceTexClick(m):
    editor = mapeditor()

    if editor is None:
        return
    SearchReplaceTextureDlg(quarkx.clickform, editor)

#
# Register the replace texture menu item
#

quarkpy.mapsearch.items.append(quarkpy.qmenu.item("Search/replace textures...", SearchReplaceTexClick, "|Search/replace textures:\n\nThis function can either just search for a particular texture, or\nit can replace it with another texture of your choice.", "intro.mapeditor.menu.html#searchmenu"))


# ----------- REVISION HISTORY ------------
# $Log: mapfindreptex.py,v $
# Revision 1.12  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.9  2003/03/21 05:47:45  cdunde
# Update infobase and add links
#
# Revision 1.8  2002/06/10 09:27:39  decker_dk
# Updated to allow only search-for-texture, without replacing any.
# TODO: Switch to specify search (and replace) for brushes that have the texture either on _all_ its faces _or_ only partly.
#
# Revision 1.7  2002/05/16 03:05:41  tiglari
# If just a face is selected, the texture on the face is loaded into the dialog
#  (bug report from fpbrowser)
#
# Revision 1.6  2002/04/07 12:46:06  decker_dk
# Pretty separator.
#
# Revision 1.5  2001/06/17 21:21:18  tiglari
# re-fix button captions, there are tabs in this file, need to be cleared out
#
# Revision 1.3  2001/01/27 18:25:29  decker_dk
# Renamed 'TextureDef' -> 'DefaultTexture'
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
