#-------------------------------------------------------------------------------
# Module: maplocaltexturesexport.py
#-------------------------------------------------------------------------------
# $Header: /cvsroot/quark/runtime/plugins/mapexportlocaltextures.py,v 1.5 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Export used textures",
   "desc":          "Exports a list of used textures in this map, to a text-file",
   "date":          "2002.04.24",
   "author":        "Decker",
   "author e-mail": "decker@planetquake.com",
   "quark":         "Version 6.3"
}

import quarkx
import quarkpy.qeditor
from quarkpy.qutils import *
import quarkpy.mapcommands

def ExportLocalTexturesClick(m):
    # Function to start the dialog
    editor = quarkpy.qeditor.mapeditor()
    if editor is None:
        return
    files = quarkx.filedialogbox("Export local texture-names to...", "*.txt", ["*.txt", "Text files (*.txt)"], 1, "texturenames.txt")
    if len(files) != 0:
        text = ""
        for tex in quarkx.texturesof([editor.Root]):
            text = text + tex + "\r\n"
        file = quarkx.newfileobj(files[0])
        file["Data"] = text
        file.savefile(files[0], 0) # Save binary, since we don't have true QuArK object-data in 'file["Data"]'.
        del file
        quarkx.msgbox("Texture-names used in this map, have been written/exported to the text-file: "+files[0], MT_INFORMATION, MB_OK)

# Register the Export local textures menu item
quarkpy.mapcommands.items.append(quarkpy.qmenu.item("Export texture-names", ExportLocalTexturesClick,"|Export texture-names:\n\nExports a list of used textures in this map, to a text-file.|intro.mapeditor.menu.html#disdupimages"))

#----------- REVISION HISTORY ------------
# $Log: mapexportlocaltextures.py,v $
# Revision 1.5  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.2  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.1  2002/04/24 18:53:22  decker_dk
# Banana requested in IRC, a function to export used textures in a map. This is the first version of it.
#

