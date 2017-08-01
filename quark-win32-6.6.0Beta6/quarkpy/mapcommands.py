"""   QuArK  -  Quake Army Knife

The map editor's "Commands" menu (to be extended by plug-ins)
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapcommands.py,v 1.10 2008/08/18 20:37:04 danielpharos Exp $



import quarkx
import qmenu
from qutils import *
# from qutils import MapHotKeyList

def newitem1click(m):
    quarkx.opentoolbox("New map items...")

def ConvertHiddenToNoDrawClick(m):
    editor = None
    forms = quarkx.forms(2)
    for form in forms:
        if (form is not None) and (form.info is not None):
            if(form.info.Root.shortname.lower() == "worldspawn"):
                editor = form.info
                break
            
    if editor is None:
        return

    worldspawn = editor.Root

    faces = worldspawn.findallsubitems("", ":f")

    for face in faces:
        if (face["Flags"] is not None and int(face["Flags"])&128) != 0:
            face.texturename  = "engine/nodraw"
            
    return

#BUILD Brush prefabs list

def PutItemFolder(Folder, Item):
    ItemName = Item

    CurrentFolder = Folder
    nChar=ItemName.find("/")
    
    while nChar != -1:
        FolderName = ItemName[:nChar]
        ItemName = ItemName[nChar+1:]
        nChar=ItemName.find("/")
        
        bFound = 0
        for iFolder in CurrentFolder.subitems:
            if iFolder.shortname==FolderName:
                CurrentFolder = iFolder
                bFound = 1
                break

        if bFound == 0:
            NewFolder = quarkx.newobj(FolderName + ".qtxfolder")
            CurrentFolder.appenditem(NewFolder)
            CurrentFolder = NewFolder

    return CurrentFolder


def FindTemplateNames():
    TemplateNamesListLocal = []

    PrefabDir = quarkx.setupsubset()["Templates"]
    try:
        import nt
        Directory = nt.listdir(PrefabDir)
    except:
        if quarkx.msgbox("The 'Directory of Templates' has not been\nchosen in this 'Games' configuration section.\nYou can not use any templates until\nyou select a folder to keep them in.\n\nWould you like to go there now to do so?", MT_CONFIRMATION, MB_YES | MB_NO) == MR_YES:
            quarkx.openconfigdlg(":")
            return None
        else:
            return []
    
    for FileName in Directory:
        if FileName.endswith(".qkm"):
            TemplateFile = quarkx.openfileobj(PrefabDir + "\\" + FileName)
            ItemList = []
            
            worldspawn = None
            for worldspawn in TemplateFile.subitems:
                if worldspawn.shortname == "worldspawn":
                    break
            for item in worldspawn.subitems:
                if item.type == ":g" and item.shortname != "group" and (item[";view"] is None or item[";view"] == "0") and item.shortname[0]!="$":
                    szDescription = ""
                    if item["Description"] is not None:
                        szDescription = item["Description"]
                    ItemI = item.shortname, szDescription
                    ItemList.append(ItemI)
            LevelDescription = ""
            if worldspawn["LevelInfo.Description"] is not None:
                LevelDescription = worldspawn["LevelInfo.Description"]
            if len(ItemList) > 0:
                FileItem = FileName, LevelDescription, ItemList
                TemplateNamesListLocal.append(FileItem)
    return TemplateNamesListLocal

def BuildTemplatesListClick(m):
    TemplateNames = FindTemplateNames()
    if TemplateNames is None:
        return
    if TemplateNames == []:
        PrefabDir = quarkx.setupsubset()["Templates"]
        quarkx.msgbox("No templates found in template folder:\n" + PrefabDir, MT_ERROR, MB_OK)
        return
    TemplateFileName = "Addons\\" + quarkx.setupsubset(SS_GAMES)['GameCfg'].replace(' ', '_') + "\\" + quarkx.setupsubset(SS_GAMES)['GameCfg'] + "Templates.qrk"
    TemplateFile = quarkx.newfileobj(TemplateFileName)
    TemplateFile.filename = TemplateFileName

    r_tbx = quarkx.newobj("Toolbox Folders.qtx")
    r_tbx["Toolbox"] = "New map items..."
    r_tbx.flags = r_tbx.flags | OF_TVSUBITEM
    TemplateFile.appenditem(r_tbx)

#    e_tbx = quarkx.newobj("Gorge Tour prefabs.qtxfolder")
    e_tbx = quarkx.newobj(quarkx.setupsubset(SS_GAMES)['GameCfg'] + " Templates.qtxfolder")
#    e_tbx[";desc"] = "Created from "
    r_tbx.appenditem(e_tbx)

    r_tbx["Root"] = e_tbx.name

    f_tbx = quarkx.newobj("Entity forms.qctx")
    f_tbx.flags = f_tbx.flags | OF_TVSUBITEM
    TemplateFile.appenditem(f_tbx)

#  Writing entities
    PrefabDir = quarkx.setupsubset()["Templates"]
    for PrefabFile in TemplateNames:
        FileName, LevelDescription, Prefabs = PrefabFile
        Folder = quarkx.newobj(FileName + ".qtxfolder")
        Folder[";desc"] = LevelDescription
        e_tbx.appenditem(Folder)
        for Prefab in Prefabs:
            PrefabName, PrefabDescription = Prefab
            ItemFolder = PutItemFolder(Folder, PrefabName)
            PrefabItem = quarkx.newobj(PrefabName+":d")
            PrefabItem[";desc"] = PrefabDescription
            PrefabItem["origin"] = "0 0 0"
            PrefabItem["scale"] = "1 1 1"
            PrefabItem["mangle"] = "0 0 0"
            PrefabItem["macro"] = "Template"
            PrefabItem["templatefilename"] = PrefabDir + "\\" + FileName
            ItemFolder.appenditem(PrefabItem)

    TemplateFile.refreshtv()
    TemplateFile.savefile(TemplateFileName, 1)
    return

NewItem1 = qmenu.item("&Insert map item...", newitem1click, "|Opens the 'New Map items' window:\n\nThis window contains all objects thats possible to use in the map-views and dataform-display. |intro.mapeditor.misctools.html#newmapitem")
ConvertHiddenToNoDrawItem = qmenu.item("Convert Hidden flag to NoDraw", ConvertHiddenToNoDrawClick)
BuildPrefabsListItem = qmenu.item("Build templates list", BuildTemplatesListClick, "|This function will build a list of all .qkm files that exist in the templates folder (if any) and place that list on 'New map items...' to select from.\n\nEach game can have its own templates and list, which this function also creates as a Templates.qrk file with the current game mode name in front of it and places that file in this games 'addons' folder.|intro.mapeditor.misctools.html#templates")


def onclick(menu):
    pass

items = []
shortcuts = {}

def CommandsMenu():
    "The Commands menu, with its shortcuts."
    
    #
    # Global variables to update from plug-ins.
    #

    # This 'if' section is for the Shine game engine even though QuArK does not support it at this time.
    # Because of the contributions they have made to QuArK please leave this in - cdunde Dec. 17, 2007.
    if quarkx.setupsubset(SS_GAMES)['GameCfg'] == "Shine":
        items2 = [NewItem1, qmenu.sep, ConvertHiddenToNoDrawItem, qmenu.sep, BuildPrefabsListItem]
    else:
        items2 = [NewItem1, qmenu.sep, BuildPrefabsListItem]
    items2 = items2 + items
    
    MapHotKeyList("Insert", NewItem1, shortcuts)
    return qmenu.popup("&Commands", items2, onclick), shortcuts

# ----------- REVISION HISTORY ------------
#
#
#$Log: mapcommands.py,v $
#Revision 1.10  2008/08/18 20:37:04  danielpharos
#Moved import to proper place
#
#Revision 1.9  2007/12/21 20:39:23  cdunde
#Added new Templates functions and Templates.
#
#Revision 1.8  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.5  2003/03/24 08:58:07  cdunde
#To update info and link to infobase
#
#Revision 1.4  2001/04/28 02:22:08  tiglari
#add 'insert' shortcut loader
#
#Revision 1.3  2001/03/20 07:59:40  tiglari
#customizable hot key support
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#