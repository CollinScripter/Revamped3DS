"""   QuArK  -  Quake Army Knife

Tool to create QuArK .qrk format files,
for new or added game support,
using the actual game files and other .qrk files as templates.
"""

#
#$Header: /cvsroot/quark/runtime/plugins/ent1conversiontools.py,v 1.17 2013/03/17 14:15:09 danielpharos Exp $
#

#
#$Log: ent1conversiontools.py,v $
#Revision 1.17  2013/03/17 14:15:09  danielpharos
#Fixed a typo.
#
#Revision 1.16  2010/09/01 08:11:22  cdunde
#Added entity extraction from game map .bsp files for .qrk file creation of Conversion Tool system.
#
#Revision 1.15  2010/08/21 03:17:41  cdunde
#Additional small fix for the Conversion Tool system.
#
#Revision 1.14  2010/08/19 08:04:26  cdunde
#Some small fixes for the Conversion Tool system.
#
#Revision 1.13  2008/08/26 15:18:54  danielpharos
#Fixed a typo and re-added missing log entries.
#
#Revision 1.12  2008/06/25 14:32:33  danielpharos
#Change to ASCII file property
#
#Revision 1.11  2008/05/27 19:33:32  danielpharos
#Fix redundant import
#
#Revision 1.10  2008/04/23 20:22:27  cdunde
#Minor improvements.
#
#Revision 1.9  2008/04/15 11:16:24  cdunde
#To add main and all sub-folders level processing of texture listing.
#
#Revision 1.8  2008/04/11 22:28:48  cdunde
#To add Doom 3 type game engine support for ConvertTool.
#
#Revision 1.7  2008/04/11 18:33:20  cdunde
#Changed code to try to adapt to proper version writing.
#
#Revision 1.6  2008/04/06 06:37:07  cdunde
#Added file back without version control to stop overwriting of internal code.
#
#Revision 1.5  2008/04/06 06:34:00  cdunde
#Trying to remove file from version control to get into cvs
#system without overwriting internal file code.
#
#Revision 1.4  2008/04/06 06:20:29  cdunde
#Added making of game Weapon-ModelEntities.qrk file creation to Conversion Tools.
#
#Revision 1.3  2008/04/04 20:46:46  cdunde
#Are you kidding me 8-\
#
#Revision 1.2  2008/04/04 20:42:52  cdunde
#To try and fix their system over writing internal code for logging....nice!
#
#Revision 1.1  2008/04/04 20:19:28  cdunde
#Added a new Conversion Tools for making game support QuArK .qrk files.
#
#

import os, sys
import quarkx
import quarkpy.qmacro
from quarkpy.qutils import *

def FilesDone(gamename, hadfolder):
    "Notifies that the process is complete and ends."

    if hadfolder == 0:
        quarkx.msgbox("Your game folder " + gamename + " has been created with the new files\nand placed into your main QuArK folder.\n\nPlease move the game folder to the QuArK addons folder\nmaking sure, if a folder with the same name already exist,\nyou do not overwrite wanted existing files\nthat might have the same file name.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return
    else:
        quarkx.msgbox("Your new files have been created in the " + gamename + " game folder\nlocated in your main QuArK folder.\n\nPlease move the game folder to the QuArK addons folder\nmaking sure, if a folder with the same name already exist,\nyou do not overwrite wanted existing files\nthat might have the same file name.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return


def MakeListFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                 gamepakfiletype,
                 modelfolder, modelfiletype, soundfolder, soundfiletype,
                 musicfolder, musicfiletype, hadfolder,
                 listfilefolder, listfiletype):
    "Makes a new list file for the gamename"
    "using the files in the listfilefolder."

    FilesDone(gamename, hadfolder)


def MakeMdlEntsFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype):
    "Makes a new 'gamename'Weapon-ModelEntities.qrk file"
    "using the files in the mdlentsfolder."

    import AddModelEnts
    AddModelEnts.AddMdlEnts(QuArKpath, gamename, gamefileslocation, modelfiletype, mdlentsfolder, mdlentsfiletype)

    if makelistfile == "60":
        MakeListFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     listfilefolder, listfiletype)
    else:
        FilesDone(gamename, hadfolder)


def MakeTexturesFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype):
    "Makes a new 'gamename'Textures.qrk file"
    "using the files in the texturesfolder."

    import AddTextureList
    AddTextureList.AddTextures(QuArKpath, gamename, gamefileslocation, texturesfolder, texturesfiletype)

    if makemdlentsfile == "51":
        MakeMdlEntsFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makelistfile == "60":
        MakeListFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     listfilefolder, listfiletype)
    else:
        FilesDone(gamename, hadfolder)


def MakeShadersFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                    gamepakfiletype, shadersfolder, shadersfiletype,
                    texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                    musicfolder, musicfiletype, hadfolder,
                    maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype):
    "Makes a new 'gamename'Shaders.qrk file"
    "using the files in the shadersfolder."

    import AddShaderList
    AddShaderList.AddShaders(QuArKpath, gamename, gamefileslocation, shadersfolder, shadersfiletype)

    if maketexturesfile == "50":
        MakeTexturesFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                         gamepakfiletype,
                         texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                         musicfolder, musicfiletype, hadfolder,
                         makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makemdlentsfile == "51":
        MakeMdlEntsFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makelistfile == "60":
        MakeListFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     listfilefolder, listfiletype)
    else:
        FilesDone(gamename, hadfolder)



class EntitiesFileDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (300, 500)
    dfsep = 0.5     # sets 50% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """
        {
        Style = "13"
        Caption = "Entity Includes Selections"
        sep: = {
            Typ="S"
            Txt="Instructions: place cursor here"
            Hint = "Includes are special items that make things such as"$0D
                   "selecting model, sound and music files, or a color for"$0D
                   "a light entity, much easer and faster for a specific."$0D$0D
                   "These special items default settings,"$0D
                   "for what will be used, are already set below."$0D
                   "Or you can change these for the games own particular needs."
               }
        sep: = { Typ="S" Txt="" }
        WriteCommonSpecifics: =
            {
            Txt = "Write Common Specifics:"
            Typ = "X15"
            Hint = "Will write the common specifics"$0D
                   "to the GameEntities.qrk file"$0D
                   "for adding to entities that you do by hand."$0D
                   "These specifics are 'target:' and 'targetname:'."$0D
                   "You can add others by hand to the list."
            }

        UseCommonSpecifics: =
            {
            Txt = "    Use Common Specifics:"
            Typ = "X16"
            Hint = "Adds the above common specifics"$0D
                   "to each entity automatically."
            }

        WriteModelBrowser: =
            {
            Txt = "Write Model Browser:"
            Typ = "X25"
            Hint = "Will write a model file selection browser"$0D
                   "to the GameEntities.qrk file"$0D
                   "for adding to entities that you do by hand."
            }

        UseModelBrowser: =
            {
            Txt = "    Use Model Browser:"
            Typ = "X26"
            Hint = "Adds the above model file selection browser"$0D
                   "to each entity that uses models automatically."
            }

        UseDefaultModelHint: =
            {
            Txt = "        Use Default Hint:"
            Typ = "X27"
            Hint = "Uses a standard 'Hint' for the above"$0D
                   "model file selection browser, or"$0D
                   "un-check this and enter your own hint below."
            }

        ModelHint: =
            {
            Txt = "        Model Hint:"
            Typ = "E"
            Hint = "Un-check 'Use Default Hint' above"$0D
                   "and type in your own hint here to use it."
            }

        MakeModelList: =
            {
            Txt = "    Make Model List:"
            Typ = "X28"
            Hint = "Besides the 'Model browser', when checked this makes"$0D
                   "a selection list, by folder, of all available game models."
            }

        MakeClipMdlList: =
            {
            Txt = "    Make Model Clip List:"
            Typ = "X29"
            Hint = "Some games (Doom 3 type) use text '.ase' files"$0D
                   "to establish the collision boundaries of its models."$0D
                   "When checked this makes a selection list of all"$0D
                   "available 'Clip Models' from those type of files."
            }

        ClipMdlFileFolder: =
            {
            Txt = "        List folder:"
            Typ = "ED"
            Hint = "To insure the proper FULL path and folder name"$0D
                   "Click the '...' button and select"$0D
                   "the EXTRACTED folder or sub-folder"$0D
                   "that these files are in. DO NOT HAND ENTER."
            }

        ClipMdlFileType: =
            {
            Txt = "        List file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Some games (Doom 3 type) use text '.ase' files"$0D
                   "to establish the collision boundaries of its models."$0D
                   "The files with their folder(s) must be extracted."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter the file suffix here by hand."$0D
                   "For example: .ase"
            }

        WriteSoundBrowser: =
            {
            Txt = "Write Sound Browser:"
            Typ = "X35"
            Hint = "Will write a sound file selection browser"$0D
                   "to the GameEntities.qrk file"$0D
                   "for adding to entities that you do by hand."
            }

        UseSoundBrowser: =
            {
            Txt = "    Use Sound Browser:"
            Typ = "X36"
            Hint = "Adds the above sound file selection browser"$0D
                   "to each entity that uses sounds automatically."
            }

        UseDefaultSoundHint: =
            {
            Txt = "        Use Default Hint:"
            Typ = "X37"
            Hint = "Uses a standard 'Hint' for the above"$0D
                   "sound file selection browser, or"$0D
                   "un-check this and enter your own hint below."
            }

        SoundHint: =
            {
            Txt = "        Sound Hint:"
            Typ = "E"
            Hint = "Un-check 'Use Default Hint' above"$0D
                   "and type in your own hint here to use it."
            }

        MakeSoundList: =
            {
            Txt = "    Make Sound List:"
            Typ = "X38"
            Hint = "Some games (Doom 3 type) use text '.sndshd'"$0D
                   "sound shader files as well as regular sound files."$0D
                   "When checked this makes a selection list of all"$0D
                   "available sounds developed from those type of files."
            }

        SoundListFileFolder: =
            {
            Txt = "        List folder:"
            Typ = "ED"
            Hint = "To insure the proper FULL path and folder name"$0D
                   "Click the '...' button and select"$0D
                   "the EXTRACTED folder or sub-folder"$0D
                   "that these files are in. DO NOT HAND ENTER."
            }

        SoundListFileType: =
            {
            Txt = "        List file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Some games (Doom 3 type) use text '.sndshd'"$0D
                   "sound shader files as well as regular sound files."$0D
                   "The files with their folder must be extracted."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter the file suffix here by hand."$0D
                   "For example: .sndshd"
            }

        WriteMusicBrowser: =
            {
            Txt = "Write Music Browser:"
            Typ = "X45"
            Hint = "Will write a music file selection browser"$0D
                   "to the GameEntities.qrk file"$0D
                   "for adding to entities that you do by hand."
            }

        UseMusicBrowser: =
            {
            Txt = "    Use Music Browser:"
            Typ = "X46"
            Hint = "Adds the above music file selection browser"$0D
                   "to each entity that uses music automatically."
            }

        UseDefaultMusicHint: =
            {
            Txt = "        Use Default Hint:"
            Typ = "X47"
            Hint = "Uses a standard 'Hint' for the above"$0D
                   "music file selection browser, or"$0D
                   "un-check this and enter your own hint below."
            }

        MusicHint: =
            {
            Txt = "        Music Hint:"
            Typ = "E"
            Hint = "Un-check 'Use Default Hint' above"$0D
                   "and type in your own hint here to use it."
            }

        UseColorPicker: =
            {
            Txt = "Write & Use Color Picker:"
            Typ = "X55"
            Hint = "Will write a color setting selection button"$0D
                   "to the GameEntities.qrk file and add it"$0D
                   "to each entity that uses 'color' automatically."
            }

        sep: = { Typ="S" Txt="" }
        UseTheseSelections:py = {Txt="Use These Selections"}
        }
        """

    # creates the dialogbox
    def __init__(self, entitiesfiledialog, root, QuArKpath, gamename, gameenginetype, gamefileslocation,
                 gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                 texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                 musicfolder, musicfiletype, hadfolder, makeshadersfile,
                 maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype):
        src = quarkx.newobj(":")
        src["WriteCommonSpecifics"] = "15"
        src["UseCommonSpecifics"] = "16"
        src["WriteModelBrowser"] = "25"
        src["UseModelBrowser"] = "26"
        src["UseDefaultModelHint"] = "27"
        src["ModelHint"] = None
        src["WriteSoundBrowser"] = "35"
        src["UseSoundBrowser"] = "36"
        src["UseDefaultSoundHint"] = "37"
        src["SoundHint"] = None
        src["MakeSoundList"] = None
        src["SoundListFileFolder"] = None
        src["SoundListFileType"] = None
        src["WriteMusicBrowser"] = "45"
        src["UseMusicBrowser"] = "46"
        src["UseDefaultMusicHint"] = "47"
        src["MusicHint"] = None
        src["MakeModelList"] = None
        src["MakeClipMdlList"] = None
        src["ClipMdlFileFolder"] = None
        src["ClipMdlFileType"] = None
        src["UseColorPicker"] = "55"
        self.src = src
        self.root = root
        self.QuArKpath = QuArKpath
        self.gamename = gamename
        self.gameenginetype = gameenginetype
        self.gamefileslocation = gamefileslocation
        self.gamepakfiletype = gamepakfiletype
        self.entitiesfolder = entitiesfolder
        self.entitiesfiletype = entitiesfiletype
        self.shadersfolder = shadersfolder
        self.shadersfiletype = shadersfiletype
        self.texturesfolder = texturesfolder
        self.texturesfiletype = texturesfiletype
        self.modelfolder = modelfolder
        self.modelfiletype = modelfiletype
        self.soundfolder = soundfolder
        self.soundfiletype = soundfiletype
        self.musicfolder = musicfolder
        self.musicfiletype = musicfiletype
        self.hadfolder = hadfolder
        self.makeshadersfile = makeshadersfile
        self.maketexturesfile = maketexturesfile
        self.makemdlentsfile = makemdlentsfile
        self.mdlentsfolder = mdlentsfolder
        self.mdlentsfiletype = mdlentsfiletype
        self.makelistfile = makelistfile
        self.listfilefolder = listfilefolder
        self.listfiletype = listfiletype
        # Create the dialog form and the buttons
        quarkpy.qmacro.dialogbox.__init__(self, entitiesfiledialog, src,
            UseTheseSelections = quarkpy.qtoolbar.button(self.UseTheseSelections,"Use These Selections",ico_editor, 3, "Use These Selections")
            )

    def datachange(self, df):
        if self.src["SoundListFileFolder"] is None and self.gamefileslocation is not None:
            self.src["SoundListFileFolder"] = self.gamefileslocation
        if self.src["ClipMdlFileFolder"] is None and self.gamefileslocation is not None:
            self.src["ClipMdlFileFolder"] = self.gamefileslocation

    def UseTheseSelections(self, btn):
        "Accepts all entries and passes them to the MakeEntitiesFile function."

        quarkx.globalaccept()
        root = self.root
        WriteCommonSpecifics = self.src["WriteCommonSpecifics"]
        UseCommonSpecifics = self.src["UseCommonSpecifics"]
        if WriteCommonSpecifics != "15" and UseCommonSpecifics == "16":
            quarkx.msgbox("You checked 'Use Common Specifics'\nbut 'Write Common Specifics' is un-checked.\nIt needs to be written to the file to use it.\n\nPlease correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        WriteModelBrowser = self.src["WriteModelBrowser"]
        UseModelBrowser = self.src["UseModelBrowser"]
        UseDefaultModelHint = self.src["UseDefaultModelHint"]
        ModelHint = self.src["ModelHint"]
        if WriteModelBrowser != "25" and UseModelBrowser == "26":
            quarkx.msgbox("You checked 'Use Model Browser'\nbut 'Write Model Browser' is un-checked.\nIt needs to be written to the file to use it.\n\nPlease correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if ModelHint is not None and UseDefaultModelHint == "27":
            quarkx.msgbox("You entered something for 'Model Hint'\nbut 'Use Default Hint' is checked.\nIt needs to be un-checked to use your hint.\n\nPlease correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        WriteSoundBrowser = self.src["WriteSoundBrowser"]
        UseSoundBrowser = self.src["UseSoundBrowser"]
        UseDefaultSoundHint = self.src["UseDefaultSoundHint"]
        SoundHint = self.src["SoundHint"]
        if WriteSoundBrowser != "35" and UseSoundBrowser == "36":
            quarkx.msgbox("You checked 'Use Sound Browser'\nbut 'Write Sound Browser' is un-checked.\nIt needs to be written to the file to use it.\n\nPlease correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if SoundHint is not None and UseDefaultSoundHint == "37":
            quarkx.msgbox("You entered something for 'Sound Hint'\nbut 'Use Default Hint' is checked.\nIt needs to be un-checked to use your hint.\n\nPlease correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        MakeSoundList = self.src["MakeSoundList"]
        SoundListFileFolder = self.src["SoundListFileFolder"]
        SoundListFileType = self.src["SoundListFileType"]
        if (MakeSoundList != "38" or SoundListFileFolder is None or SoundListFileFolder == self.gamefileslocation or SoundListFileType is None) and (MakeSoundList == "38" or (SoundListFileFolder is not None and SoundListFileFolder != self.gamefileslocation) or SoundListFileType is not None):
            quarkx.msgbox("You entered something for Make Sound List,\nbut you did not do all three items.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        if SoundListFileType is not None and SoundListFileType.find(SoundListFileFolder) != -1:
            SoundListFileType = SoundListFileType.split(".", 1)
            SoundListFileType = SoundListFileType[len(SoundListFileType)-1]
        if SoundListFileType is not None and not SoundListFileType.startswith("."):
            SoundListFileType = "." + SoundListFileType
        WriteMusicBrowser = self.src["WriteMusicBrowser"]
        UseMusicBrowser = self.src["UseMusicBrowser"]
        UseDefaultMusicHint = self.src["UseDefaultMusicHint"]
        MusicHint = self.src["MusicHint"]
        if WriteMusicBrowser != "45" and UseMusicBrowser == "46":
            quarkx.msgbox("You checked 'Use Music Browser'\nbut 'Write Music Browser' is un-checked.\nIt needs to be written to the file to use it.\n\nPlease correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if MusicHint is not None and UseDefaultMusicHint == "47":
            quarkx.msgbox("You entered something for 'Music Hint'\nbut 'Use Default Hint' is checked.\nIt needs to be un-checked to use your hint.\n\nPlease correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        MakeModelList = self.src["MakeModelList"]
        MakeClipMdlList = self.src["MakeClipMdlList"]
        ClipMdlFileFolder = self.src["ClipMdlFileFolder"]
        ClipMdlFileType = self.src["ClipMdlFileType"]
        if (MakeClipMdlList != "29" or ClipMdlFileFolder is None or ClipMdlFileFolder == self.gamefileslocation or ClipMdlFileType is None) and (MakeClipMdlList == "29" or (ClipMdlFileFolder is not None and ClipMdlFileFolder != self.gamefileslocation) or ClipMdlFileType is not None):
            quarkx.msgbox("You entered something for Make Model Clip List,\nbut you did not do all three items.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        if ClipMdlFileType is not None and ClipMdlFileType.find(ClipMdlFileFolder) != -1:
            ClipMdlFileType = ClipMdlFileType.split(".", 1)
            ClipMdlFileType = ClipMdlFileType[len(ClipMdlFileType)-1]
        if ClipMdlFileType is not None and not ClipMdlFileType.startswith("."):
            ClipMdlFileType = "." + ClipMdlFileType
        UseColorPicker = self.src["UseColorPicker"]

        self.close(btn) # This will close this dialog.
        MakeEntitiesFile(root, self.QuArKpath, self.gamename, self.gameenginetype, self.gamefileslocation,
            self.gamepakfiletype, self.entitiesfolder, self.entitiesfiletype, self.shadersfolder,
            self.shadersfiletype, self.texturesfolder, self.texturesfiletype, self.modelfolder,
            self.modelfiletype, self.soundfolder, self.soundfiletype, self.musicfolder, self.musicfiletype,
            self.hadfolder, self.makeshadersfile, self.maketexturesfile, self.makemdlentsfile, self.mdlentsfolder, self.mdlentsfiletype,
            self.makelistfile, self.listfilefolder, self.listfiletype, WriteCommonSpecifics, UseCommonSpecifics,
            WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint,
            WriteSoundBrowser, UseSoundBrowser, UseDefaultSoundHint, SoundHint, MakeSoundList, SoundListFileFolder, SoundListFileType,
            WriteMusicBrowser, UseMusicBrowser, UseDefaultMusicHint, MusicHint, MakeModelList, MakeClipMdlList, ClipMdlFileFolder, ClipMdlFileType,
            UseColorPicker)


def MakeEntitiesFile(root, QuArKpath, gamename, gameenginetype, gamefileslocation,
            gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder,
            shadersfiletype, texturesfolder, texturesfiletype, modelfolder,
            modelfiletype, soundfolder, soundfiletype, musicfolder, musicfiletype,
            hadfolder, makeshadersfile, maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype,
            makelistfile, listfilefolder, listfiletype, WriteCommonSpecifics, UseCommonSpecifics,
            WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint,
            WriteSoundBrowser, UseSoundBrowser, UseDefaultSoundHint, SoundHint, MakeSoundList, SoundListFileFolder, SoundListFileType,
            WriteMusicBrowser, UseMusicBrowser, UseDefaultMusicHint, MusicHint, MakeModelList, MakeClipMdlList, ClipMdlFileFolder, ClipMdlFileType,
            UseColorPicker):
    "Makes a new 'gamename'Entities.qrk file"
    "using the files in the entitiesfolder."

    if entitiesfiletype != ".bsp" and (gameenginetype == "Quake 2" or gameenginetype == "Quake 3"):
        import ConvertToolQ3typeEnts
        ConvertToolQ3typeEnts.Q3typeEntList(root, QuArKpath, gamename, gamefileslocation,
            gamepakfiletype, entitiesfolder, entitiesfiletype,
            modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
            WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint,
            WriteSoundBrowser, UseSoundBrowser, UseDefaultSoundHint, SoundHint,
            WriteMusicBrowser, UseMusicBrowser, UseDefaultMusicHint, MusicHint,
            UseColorPicker)

    elif entitiesfiletype != ".bsp" and gameenginetype == "Doom 3":
        import ConvertToolD3typeEnts
        ConvertToolD3typeEnts.D3typeEntList(root, QuArKpath, gamename, gamefileslocation,
            gamepakfiletype, entitiesfolder, entitiesfiletype, modelfolder,
            modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
            WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint,
            WriteSoundBrowser, UseSoundBrowser, UseDefaultSoundHint, SoundHint, MakeSoundList, SoundListFileFolder, SoundListFileType,
            WriteMusicBrowser, UseMusicBrowser, UseDefaultMusicHint, MusicHint, MakeModelList, MakeClipMdlList, ClipMdlFileFolder, ClipMdlFileType,
            UseColorPicker)

    elif entitiesfiletype == ".bsp":
        import ConvertToolBSPtypeEnts
        ConvertToolBSPtypeEnts.BSPtypeEntList(root, QuArKpath, gamename, gamefileslocation,
            gamepakfiletype, entitiesfolder, entitiesfiletype,
            modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
            WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint,
            WriteSoundBrowser, UseSoundBrowser, UseDefaultSoundHint, SoundHint,
            WriteMusicBrowser, UseMusicBrowser, UseDefaultMusicHint, MusicHint,
            UseColorPicker)

    if makeshadersfile == "40":
        MakeShadersFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
        gamepakfiletype, shadersfolder, shadersfiletype,
        texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
        musicfolder, musicfiletype, hadfolder,
        maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif maketexturesfile == "50":
        MakeTexturesFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
        gamepakfiletype,
        texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
        musicfolder, musicfiletype, hadfolder,
        makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makemdlentsfile == "51":
        MakeMdlEntsFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makelistfile == "60":
        MakeListFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     listfilefolder, listfiletype)
    else:
        FilesDone(gamename, hadfolder)


def MakeUserDataFile(root, QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                     texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder, makeentitiesfile, makeshadersfile,
                     maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype):
    "Makes a new UserData' gamename'.qrk file"
    "using the UserData file of the gameenginetype."

    newfilesfolderpath = QuArKpath + '\\' + gamename

    if gameenginetype == "Half-Life":
        input = open(QuArKpath + '\\addons\\Half-Life\\UserData Half-Life.qrk')
    elif gameenginetype == "Half-Life2":
        input = open(QuArKpath + '\\addons\\Half-Life2\\UserData Half-Life2.qrk')
    elif gameenginetype == "Quake 1":
        input = open(QuArKpath + '\\addons\\Quake_1\\UserData Quake 1.qrk')
    elif gameenginetype == "Quake 2":
        input = open(QuArKpath + '\\addons\\Quake_2\\UserData Quake 2.qrk')
    elif gameenginetype == "Quake 3":
        input = open(QuArKpath + '\\addons\\Quake_3\\UserData Quake 3.qrk')
    elif gameenginetype == "Doom 3":
        input = open(QuArKpath + '\\addons\\Doom_3\\UserData Doom 3.qrk')
    else:
        input = open(QuArKpath + '\\addons\\Quake_3\\UserData Quake 3.qrk')
    output = open(newfilesfolderpath + '\\' + ('UserData ' + gamename + '.qrk'), "w")

    while 1:
        line = input.readline()
        if line == '':
            input.close()
            output.close()
            break
        if line.startswith('{'):
            output.write(line)
            break
        if line.startswith('QQRKSRC1'):
            output.write(line)
            output.write('\n')
            output.write('//$' + 'Header: Exp $' + '\n')
            output.write('// ----------- REVISION HISTORY ------------\n')
            output.write('//$' + 'Log: ' + ('UserData\\040' + gamename + '.qrk') + ',v $' + '\n')
            output.write('//\n')
            output.write('\n')
    while 1:
        line = input.readline()
        if line == '':
            input.close()
            output.close()
            break
        if line.startswith('//'):
            continue
        if gameenginetype == "Half-Life":
            line = line.replace('Half-Life', gamename)
        elif gameenginetype == "Half-Life2":
            line = line.replace('Half-Life 2', gamename)
        elif gameenginetype == "Quake 1":
            line = line.replace('Quake 1', gamename)
        elif gameenginetype == "Quake 2":
            line = line.replace('Quake 2', gamename)
        elif gameenginetype == "Quake 3":
            line = line.replace('Quake 3', gamename)
        elif gameenginetype == "Doom 3":
            line = line.replace('Doom 3', gamename)
        output.write(line)

    input.close()
    output.close()

    if makeentitiesfile == "30":
        entitiesfiledialog = quarkx.newform("entitiesdialogform")
        EntitiesFileDlg(entitiesfiledialog, root, QuArKpath, gamename, gameenginetype, gamefileslocation,
                        gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                        texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                        musicfolder, musicfiletype, hadfolder, makeshadersfile,
                        maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makeshadersfile == "40":
        MakeShadersFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                        gamepakfiletype, shadersfolder, shadersfiletype,
                        texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                        musicfolder, musicfiletype, hadfolder,
                        maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif maketexturesfile == "50":
        MakeTexturesFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                         gamepakfiletype,
                         texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                         musicfolder, musicfiletype, hadfolder,
                         makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makemdlentsfile == "51":
        MakeMdlEntsFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makelistfile == "60":
        MakeListFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     listfilefolder, listfiletype)
    else:
        FilesDone(gamename, hadfolder)



class DataFileDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (300, 185)
    dfsep = 0.4     # sets 40% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """
        {
        Style = "13"
        Caption = "Default Room Texture Selection"
        sep: = {
            Typ="S"
            Txt="Instructions: place cursor here"
            Hint = "Because the 'DataGame.qrk' file makes up"$0D
                   "the default room for a Newmap to start editing,"$0D
                   "You need to select these textures or shaders for it."$0D$0D
                   "when done making your selections click the"$0D
                   "'Return Selections' button below to complete this process."
               }
        sep: = { Typ="S" Txt="" }

        WallTexFile: =
            {
            Txt = "Wall Texture:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Select a wall texture to use."
            }

        FloorTexFile: =
            {
            Txt = "Floor Texture:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Select a floor texture to use."
            }

        CeilTexFile: =
            {
            Txt = "Ceiling Texture:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Select a ceiling texture to use."
            }

        CaulkTexFile: =
            {
            Txt = "Caulking Texture:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Select a caulking texture to use."
            }

        sep: = { Typ="S" Txt="" }
        ReturnSelections:py = {Txt="Return Selections"}
        }
        """

    # creates the dialogbox
    def __init__(self, datafiledialog, root, QuArKpath, gamename, gameenginetype, gamefileslocation,
                 gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                 texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                 musicfolder, musicfiletype, hadfolder, makeuserdatafile, makeentitiesfile, makeshadersfile,
                 maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype):
        src = quarkx.newobj(":")
        src["WallTexFile"] = None
        src["FloorTexFile"] = None
        src["CeilTexFile"] = None
        src["CaulkTexFile"] = None
        self.src = src
        self.root = root
        self.QuArKpath = QuArKpath
        self.gamename = gamename
        self.gameenginetype = gameenginetype
        self.gamefileslocation = gamefileslocation
        self.gamepakfiletype = gamepakfiletype
        self.entitiesfolder = entitiesfolder
        self.entitiesfiletype = entitiesfiletype
        self.shadersfolder = shadersfolder
        self.shadersfiletype = shadersfiletype
        self.texturesfolder = texturesfolder
        self.texturesfiletype = texturesfiletype
        self.modelfolder = modelfolder
        self.modelfiletype = modelfiletype
        self.soundfolder = soundfolder
        self.soundfiletype = soundfiletype
        self.musicfolder = musicfolder
        self.musicfiletype = musicfiletype
        self.hadfolder = hadfolder
        self.makeuserdatafile = makeuserdatafile
        self.makeentitiesfile = makeentitiesfile
        self.makeshadersfile = makeshadersfile
        self.maketexturesfile = maketexturesfile
        self.makemdlentsfile = makemdlentsfile
        self.mdlentsfolder = mdlentsfolder
        self.mdlentsfiletype = mdlentsfiletype
        self.makelistfile = makelistfile
        self.listfilefolder = listfilefolder
        self.listfiletype = listfiletype
        # Create the dialog form and the buttons
        quarkpy.qmacro.dialogbox.__init__(self, datafiledialog, src,
            ReturnSelections = quarkpy.qtoolbar.button(self.ReturnSelections,"Return Selections",ico_editor, 3, "Return Selections")
            )

    def ReturnSelections(self, btn):
        "Accepts all entries and checks for invalid or missing ones."
        "If complete, it returns them to the MakeDataFile function."

        quarkx.globalaccept()
        root = self.root
        walltex = self.src["WallTexFile"]
        floortex = self.src["FloorTexFile"]
        ceiltex = self.src["CeilTexFile"]
        caulktex = self.src["CaulkTexFile"]
        if walltex is None or floortex is None or ceiltex is None or caulktex is None:
            quarkx.msgbox("You did not make all of the selections.\nPlease do so and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return

        defaulttexs = {}
        defaulttexs['walltex'] = walltex
        defaulttexs['floortex'] = floortex
        defaulttexs['ceiltex'] = ceiltex
        defaulttexs['caulktex'] = caulktex
        texlabels = {}
        texlabels['walltex'] = "Wall Texture\n"
        texlabels['floortex'] = "Floor Texture\n"
        texlabels['ceiltex'] = "Ceiling Texture\n"
        texlabels['caulktex'] = "Caulking Texture\n"

        errors = []
        for key in defaulttexs.keys():
            if defaulttexs[key].find(self.shadersfolder) != -1:
                continue
            elif defaulttexs[key].find(self.texturesfolder) != -1:
                continue
            else:
                errors = errors + [key]
        if len(errors) != 0:
            printerrors = ""
            for error in errors:
                printerrors = printerrors + (texlabels[error])
                quarkx.beep() # Makes the computer "Beep" once if a file is not found.
            if len(errors) == 1:
                quarkx.msgbox("INCORRECT SELECTION !\n\n" + str(len(errors)) + " selection\n" + printerrors + "does NOT match your settings for\nthe 'Shaders Folder' or 'Textures Folder'.\nCorrect the above selection and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            else:
                quarkx.msgbox("INCORRECT SELECTIONS !\n\n" + str(len(errors)) + " selections\n" + printerrors + "do NOT match your settings for\nthe 'Shaders Folder' or 'Textures Folder'.\nCorrect the above selections and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

        self.close(btn) # This will close this dialog.
        MakeDataFile(root, self.QuArKpath, self.gamename, self.gameenginetype, self.gamefileslocation,
                     self.gamepakfiletype, self.entitiesfolder, self.entitiesfiletype, self.shadersfolder, self.shadersfiletype,
                     self.texturesfolder, self.texturesfiletype, self.modelfolder, self.modelfiletype, self.soundfolder, self.soundfiletype,
                     self.musicfolder, self.musicfiletype, self.hadfolder, self.makeuserdatafile, self.makeentitiesfile, self.makeshadersfile,
                     self.maketexturesfile, self.makemdlentsfile, self.mdlentsfolder, self.mdlentsfiletype, self.makelistfile, self.listfilefolder, self.listfiletype, defaulttexs)


def MakeDataFile(root, QuArKpath, gamename, gameenginetype, gamefileslocation,
                 gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                 texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                 musicfolder, musicfiletype, hadfolder, makeuserdatafile, makeentitiesfile, makeshadersfile,
                 maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype, defaulttexs):
    "Makes a new 'gamename'Data.qrk file"
    "using the Data file of the gameenginetype."

    for key in defaulttexs.keys():
        if defaulttexs[key].find(shadersfolder) != -1:
            tex = defaulttexs[key]
            tex = tex.replace(shadersfolder + '\\', "")
            tex = tex.replace('\\', '/')
            tex = tex.split('.')
            defaulttexs[key] = tex[0]
        elif defaulttexs[key].find(texturesfolder) != -1:
            tex = defaulttexs[key]
            tex = tex.replace(texturesfolder + '\\', "")
            tex = tex.replace('\\', '/')
            tex = tex.split('.')
            defaulttexs[key] = tex[0]
        else:
            quarkx.beep() # Makes the computer "Beep" once if a file is not found.
            quarkx.msgbox("Something went wrong with the Default Room Textures section.\nPlease check your folder and file type settings then try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

    gamefileslocation = gamefileslocation.replace('/', '\\')
    gamefileslocation = gamefileslocation.strip()
    shadersfolder = shadersfolder.replace('/', '\\')
    shaderfolder = shadersfolder.rsplit('\\', 1)
    shaderfolder = shaderfolder[len(shaderfolder)-1]
    shaderfolder = shaderfolder.strip()

    shadertype = shadersfiletype.replace('.', "")
    shadertype = shadertype.strip()

    pakfile = gamepakfiletype.replace('.', "")
    pakfile = pakfile.strip()

    newfilesfolderpath = QuArKpath + '\\' + gamename

    if gameenginetype == "Half-Life":
        input = open(QuArKpath + '\\addons\\Half-Life\\DataHL.qrk')
    elif gameenginetype == "Half-Life2":
        input = open(QuArKpath + '\\addons\\Half-Life2\\DataHL2.qrk')
    elif gameenginetype == "Quake 1":
        input = open(QuArKpath + '\\addons\\Quake_1\\DataQ1.qrk')
    elif gameenginetype == "Quake 2":
        input = open(QuArKpath + '\\addons\\Quake_2\\DataQ2.qrk')
    elif gameenginetype == "Quake 3":
        input = open(QuArKpath + '\\addons\\Quake_3\\DataQ3.qrk')
    elif gameenginetype == "Doom 3":
        input = open(QuArKpath + '\\addons\\Doom_3\\DataD3.qrk')

    output = open(newfilesfolderpath + '\\' + ('Data' + gamename + '.qrk'), "w")

    while 1:
        line = input.readline()
        if line == '':
            input.close()
            output.close()
            break
        if line.startswith('{'):
            output.write(line)
            break
        if line.startswith('QQRKSRC1'):
            output.write(line)
            output.write('// ' + gamename + ' definition file for Quark\n')
            output.write('\n')
            output.write('//$' + 'Header: Exp $' + '\n')
            output.write('// ----------- REVISION HISTORY ------------\n')
            output.write('//$' + 'Log: ' + ('Data' + gamename + '.qrk') + ',v $' + '\n')
            output.write('//\n')
            output.write('\n')
    while 1:
        line = input.readline()
        if line == '':
            input.close()
            output.close()
            break
        if line.startswith('//'):
            continue
        if gameenginetype == "Half-Life":
            line = line.replace('Half-Life', gamename)
        elif gameenginetype == "Half-Life2":
            line = line.replace('Half-Life2', gamename)
        elif gameenginetype == "Quake 1":
            line = line.replace('Quake 1', gamename)
        elif gameenginetype == "Quake 2":
            line = line.replace('Quake 2', gamename)
        elif gameenginetype == "Quake 3":
            line = line.replace('Quake 3', gamename)
        elif gameenginetype == "Doom 3":
            line = line.replace('Doom 3', gamename)

   ### Changes everything with "shader".
   #     if line.find("shader") != -1:
   #         line = line.replace('shader', shadertype)
   #     if line.find(shadertype + 's/') != -1:
   #         line = line.replace(shadertype + 's', shaderfolder)

   ### Only changes the folder name "shader".
        if line.find('scripts/') != -1:
            line = line.replace('scripts/', shaderfolder + '/')
        elif line.find('shaders/') != -1:
            line = line.replace('shaders/', shaderfolder + '/')

        if line.find('Wad.wad') != -1:
            line = line.replace('Wad.wad', pakfile.capitalize() + '.' + pakfile)
        elif line.find('Pk3.pk3') != -1:
            line = line.replace('Pk3.pk3', pakfile.capitalize() + '.' + pakfile)
        elif line.find('Pk4.pk4') != -1:
            line = line.replace('Pk4.pk4', pakfile.capitalize() + '.' + pakfile)

        for key in defaulttexs.keys():
            if line.find(key + ':incl') != -1:
                output.write(line)
                while 1:
                    line = input.readline()
                    if line == '':
                        break
                    if line.startswith('  }'):
                        break
                    if line.startswith('    tex ='):
                        output.write('    tex = "' + defaulttexs[key] + '"\n')
                    else:
                        output.write(line)
                break

        output.write(line)

    input.close()
    output.close()

    if makeuserdatafile == "20":
        MakeUserDataFile(root, QuArKpath, gamename, gameenginetype, gamefileslocation,
                         gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                         texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                         musicfolder, musicfiletype, hadfolder, makeentitiesfile, makeshadersfile,
                         maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makeentitiesfile == "30":
        entitiesfiledialog = quarkx.newform("entitiesdialogform")
        EntitiesFileDlg(entitiesfiledialog, root, QuArKpath, gamename, gameenginetype, gamefileslocation,
                        gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                        texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                        musicfolder, musicfiletype, hadfolder, makeshadersfile,
                        maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makeshadersfile == "40":
        MakeShadersFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                        gamepakfiletype, shadersfolder, shadersfiletype,
                        texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                        musicfolder, musicfiletype, hadfolder,
                        maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif maketexturesfile == "50":
        MakeTexturesFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
        gamepakfiletype,
        texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
        musicfolder, musicfiletype, hadfolder,
        makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makemdlentsfile == "51":
        MakeMdlEntsFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
    elif makelistfile == "60":
        MakeListFile(QuArKpath, gamename, gameenginetype, gamefileslocation,
                     gamepakfiletype,
                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                     musicfolder, musicfiletype, hadfolder,
                     listfilefolder, listfiletype)
    else:
        FilesDone(gamename, hadfolder)


class TypeOfConversionDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (300, 735)
    dfsep = 0.45     # sets 45% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """
        {
        Style = "13"
        Caption = "Conversion Tool"
        sep: = {
            Typ="S"
            Txt="Instructions: place cursor here"
            Hint = "Place your cursor over each item"$0D
                   "below for instructions on what to do."$0D$0D
                   "If a bold title exist such as this one,"$0D
                   "place your cursor over it for additional instructions."$0D$0D
                   "You can cancel this entire process at any time"$0D
                   "by clicking the 'Cancel function' button"$0D
                   "but some files may have already been created."$0D$0D
                   "A game folder with any new files will be"$0D
                   "created in this QuArK main folder."
               }
        sep: = { Typ="S" Txt="" }
        sep: = {
            Typ="S"
            Txt="Step 1: Preliminary Game Setup"
            Hint = "Needed GAME settings to make the .qrk file(s)."$0D$0D
                   "Place your cursor over each item"$0D
                   "below for instructions on what to do."$0D
                   "When ready, proceed to 'Step 2'."
               }
        GameFilesLocation: =
            {
            Txt = "Game Files Location:"
            Typ = "ED"
            Hint = "If not done so already, extract the entire folder(s),"$0D
                   "with the file types you will be SELECTING BELOW,"$0D
                   "from the game's pak files and place them in the same folder"$0D
                   "where the pak files are. If needed make DUMMY folders"$0D
                   "to MEMIC EXACTLY how they are arranged in the pak files."$0D
                   "Then click this Path Selector's '...' button"$0D
                   "and select the folder that the PAK files are in, the game folder."$0D
                   "After Steps 1 & 2 selections are made, click the 'Make .qrk files' button."
            }

        GamePakFileType: =
            {
            Txt = "Pak file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Type of file containing the game files."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter this file's type suffix here by hand."$0D
                   "For example: .pk3"
            }

        GameName: =
            {
            Txt = "Game Name:"
            Typ = "E"
            Hint = "Enter a short name for the game"$0D
                   "that QuArK can use, for example"$0D$0D
                   "If the full game name is something like:"$0D
                   "Heavy Metal - FAKK2"$0D
                   "Just use:"$0D
                   "FAKK2"
            }

        GameEngineType: =
            {
            Txt = "Game Engine type:"
            Typ = "CL"
            Items = "Half-Life"$0D"Half-Life2"$0D"Quake 1"$0D"Quake 2"$0D"Quake 3"$0D"Doom 3"
            Hint = "This is a list of the type of"$0D
                   "game engines that QuArK supports."$0D$0D
                   "Select the one this game uses"$0D
                   "or is most similar to."
            }

        EntitiesFolder: =
            {
            Txt = "Entities folder path:"
            Typ = "ED"
            Hint = "To insure the proper FULL path and folder name"$0D
                   "Click the '...' button and select"$0D
                   "the EXTRACTED folder or sub-folder"$0D
                   "that these files are in. DO NOT HAND ENTER."
            }

        EntitiesFileType: =
            {
            Txt = "   Entities file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "File(s) that define the entities."$0D
                   "These can be .def or .cpp files with their folder extracted."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter this file's type suffix here by hand."$0D
                   "For example: .def"
            }

        ShadersFolder: =
            {
            Txt = "Shaders folder path:"
            Typ = "ED"
            Hint = "To insure the proper FULL path and folder name"$0D
                   "Click the '...' button and select"$0D
                   "the EXTRACTED folder or sub-folder"$0D
                   "that these files are in. DO NOT HAND ENTER."
            }

        ShadersFileType: =
            {
            Txt = "   Shaders file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Files that effect the games textures."$0D
                   "These can be .shader, .mat or something else."$0D
                   "The files with their folder must be extracted."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter this file's type suffix here by hand."$0D
                   "For example: .shader"
            }

        TexturesFolder: =
            {
            Txt = "Textures folder path:"
            Typ = "ED"
            Hint = "To insure the proper FULL path and folder name"$0D
                   "Click the '...' button and select"$0D
                   "the EXTRACTED folder or sub-folder"$0D
                   "that these files are in. DO NOT HAND ENTER."
            }

        TexturesFileType: =
            {
            Txt = "   Textures file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "The actual 'image' files, the games textures."$0D
                   "These can be .tga, .png or something else."$0D
                   "The files with their folder must be extracted."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter this file's type suffix here by hand."$0D
                   "A single file example: tga"$0D
                   "A multiple file example: tga; *.png"$0D
                   "The ( ; *.png ) can be added at the end of a seleced file as well."
            }

        ModelFolder: =
            {
            Txt = "Model folder path:"
            Typ = "ED"
            Hint = "You DO NOT need to extract all of these files."$0D
                   "To insure the proper FULL path and folder name"$0D
                   "Make a DUMMY folder or sub-folder that these"$0D
                   "files WOULD be in, but they must MEMIC EXACTLY"$0D
                   "how the folder structure is in the pak files."$0D
                   "Click the '...' button and select the DUMMY folder."$0D
                   "If you enter the path by hand again, DUPLICATE EXACTLY."
            }

        ModelFileType: =
            {
            Txt = "   Model file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Type of file that will DISPLAY a model."$0D
                   "This might be a 'text script' file."$0D
                   "Quake 1, 2 & 3 use actual model files."$0D
                   "EF2, FAKK2 use .tik 'text script' files."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter this file's type suffix here by hand."$0D
                   "For example: .tik"
            }

        SoundFolder: =
            {
            Txt = "Sound folder path:"
            Typ = "ED"
            Hint = "You DO NOT need to extract all of these files."$0D
                   "To insure the proper FULL path and folder name"$0D
                   "Make a DUMMY folder or sub-folder that these"$0D
                   "files WOULD be in, but they must MEMIC EXACTLY"$0D
                   "how the folder structure is in the pak files."$0D
                   "Click the '...' button and select the DUMMY folder."$0D
                   "If you enter the path by hand again, DUPLICATE EXACTLY."
            }

        SoundFileType: =
            {
            Txt = "   Sound file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Type of file that plays GAME SOUNDS."$0D
                   "Some games have more then one type."$0D
                   "One for game sounds, one for music or both."$0D
                   "Quake 1 & 2 (.wav only), 3 (.wav & .mp3)"$0D
                   "EF2, FAKK2 use .wav for game sounds"$0D
                   "and .mus for the game's music (enter below)."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter the GAME SOUND file(s) here by hand."$0D
                   "A single file example: wav"$0D
                   "A multiple file example: wav; *.mp3"$0D
                   "The ( ; *.mp3 ) can be added at the end of a seleced file as well."
            }

        MusicFolder: =
            {
            Txt = "Music folder path:"
            Typ = "ED"
            Hint = "You DO NOT need to extract all of these files."$0D
                   "To insure the proper FULL path and folder name"$0D
                   "Make a DUMMY folder or sub-folder that these"$0D
                   "files WOULD be in, but they must MEMIC EXACTLY"$0D
                   "how the folder structure is in the pak files."$0D
                   "Click the '...' button and select the DUMMY folder."$0D
                   "If you enter the path by hand again, DUPLICATE EXACTLY."$0D
                   "If your game does not have these use your 'Sound' folder."
            }

        MusicFileType: =
            {
            Txt = "   Music file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Type of file that plays GAME MUSIC."$0D
                   "Some games use SPECIAL type files for music"$0D
                   "which is primarily use as a 'worldspawn' setting."$0D
                   "EF2, FAKK2 use .wav for game sounds (enter above)"$0D
                   "and .mus for the game's SPECIAL music type."$0D
                   "If your game does not have these use your 'Sound' type."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter the GAME MUSIC file(s) here by hand."$0D
                   "A single file example: mus"$0D
                   "A multiple file example: mus; *.mp3"$0D
                   "The ( ; *.mp3 ) can be added at the end of a seleced file as well."
            }

        sep: = { Typ="S" Txt="" }
        sep: = {
            Typ="S"
            Txt="Step 2: QuArK .qrk files to make"
            Hint = "Needed settings to make the .qrk file(s)."$0D$0D
                   "Place your cursor over each item"$0D
                   "below for instructions on what to do."$0D
                   "When ready, click the 'Make .qrk files' button."
               }
        MakeDataFile: =
            {
            Txt = "Make Data file:"
            Typ = "X10"
            Hint = "To make a 'Data(game name).qrk'"$0D
                   "file check this box."$0D$0D
                   "1st Basic file needed for QuArK NEW game support."$0D
                   "DO NOT MAKE THIS FILE FOR ONLY A MOD OF AN EXISTING GAME."$0D
                   "It contains things such as the default 'worldspawn'"$0D
                   "and 'Newmap' room to start editing with."
            }

        MakeUserDataFile: =
            {
            Txt = "Make UserData file:"
            Typ = "X20"
            Hint = "To make a 'UserData (game name).qrk'"$0D
                   "file check this box."$0D$0D
                   "2nd Basic file needed for QuArK game support."$0D
                   "It contains specific things such as the QuArK games 'Menu'"$0D
                   "that contain items to compile a map and run the game."
            }

        MakeEntitiesFile: =
            {
            Txt = "Make Entities file:"
            Typ = "X30"
            Hint = "To make a '(game name)Entities.qrk'"$0D
                   "file check this box."$0D$0D
                   "Creates a file with all of the"$0D
                   "game's entities for QuArK game support."$0D$0D
                   "If checked, extract the game folders with these files now."$0D
                   "You can delete this folder once this process is done."
            }

        MakeShadersFile: =
            {
            Txt = "Make Shaders file:"
            Typ = "X40"
            Hint = "To make a '(game name)Shaders.qrk'"$0D
                   "file check this box."$0D$0D
                   "Not all games can use textures directly,"$0D
                   "'shader', 'material', 'script, files are used instead."$0D
                   "If you are not sure, check this box anyway."$0D$0D
                   "If checked, extract the game folders with these files now."$0D
                   "You can delete this folder once this process is done."
            }

        MakeTexturesFile: =
            {
            Txt = "Make Textures file:"
            Typ = "X50"
            Hint = "To make a '(game name)Textures.qrk'"$0D
                   "file check this box."$0D$0D
                   "Creates a file with all of the"$0D
                   "game's textures for QuArK game support."$0D
                   "Not all games can use textures directly,"$0D
                   "'shader', 'material', 'script, files are used instead."$0D
                   "If you are not sure, check this box anyway."$0D$0D
                   "If checked, extract the game folders with these files now."$0D
                   "You can delete this folder once this process is done."
            }

        MakeMdlEntsFile: =
            {
            Txt = "Make Mdl Entity file:"
            Typ = "X51"
            Hint = "To make a '(game name)Weapon-ModelEntities.qrk'"$0D
                   "file check this box."$0D$0D
                   "Some games such as 'EF2' and 'FAKK2' use special"$0D
                   "entity classes for their game models and weapons."$0D
                   "They are defined by text script files (.lst for the above)."$0D$0D
                   "If checked, extract the game folder with these files now."$0D
                   "Enter below the 'file type' and 'folder path' EXACTLY as shown."$0D$0D
                   "You can delete this folder once this process is done."
            }

        MdlEntsFolder: =
            {
            Txt = "   Mdl Entity folder path:"
            Typ = "ED"
            Hint = "To insure the proper FULL path and folder name"$0D
                   "Click the '...' button and select"$0D
                   "the EXTRACTED folder containing the .lst"$0D
                   "or equivalent files in it. DO NOT HAND ENTER."
            }

        MdlEntsFileType: =
            {
            Txt = "      Mdl Entity file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "File(s) that define model type entities (ex: .lst files)."$0D
                   "The files with their folder must be extracted."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter this file's type suffix here by hand."$0D
                   "For example: .lst"
            }

        MakeListFile: =
            {
            Txt = "Make List file:"
            Typ = "X60"
            Hint = "To make a '(game name)(type of)List.qrk'"$0D
                   "file check this box."$0D$0D
                   "Creates a 'list' file with all of the"$0D
                   "designated 'type' items such as models,"$0D
                   "sounds, misc. items for QuArK game support."$0D$0D
                   "If checked, extract the game folders with these files now."$0D
                   "Enter below the 'file type' and 'folder path' EXACTLY as shown."$0D$0D
                   "You can delete this folder once this process is done."
            }

        ListFileFolder: =
            {
            Txt = "   List File folder path:"
            Typ = "ED"
            Hint = "To insure the proper FULL path and folder name"$0D
                   "Click the '...' button and select"$0D
                   "the EXTRACTED folder or sub-folder"$0D
                   "that these files are in. DO NOT HAND ENTER."
            }

        ListFileType: =
            {
            Txt = "      List file type:"
            Typ = "EP"
            DefExt = "*"
            Hint = "Any type of file that you want to make a 'list' of"$0D
                   "which then must be added to the proper .qrk file by hand."$0D
                   "The files with their folder must be extracted."$0D
                   "Select any one of these files with the '...' button"$0D
                   "or enter the file suffix here by hand."$0D
                   "For example: .mdl"
            }

        sep: = { Typ="S" Txt="" }
        MakeFiles:py = {Txt="Make .qrk files"}
        close:py = {Txt="Close this dialog"}
        }
        """

    def __init__(self, form1, root):       # creates the dialogbox
        self.QuArKpath = quarkx.exepath # Gets the path where QuArK is installed, our "Current Work Directory".
        self.QuArKpath = self.QuArKpath.rstrip('\\')
        src = quarkx.newobj(":")
        src["GameFilesLocation"] = None
        src["GamePakFileType"]   = None
        src["GameName"]          = None
        src["GameEngineType"]    = None
        src["EntitiesFolder"]    = None
        src["EntitiesFileType"]  = None
        src["ShadersFolder"]     = None
        src["ShadersFileType"]   = None
        src["TexturesFolder"]    = None
        src["TexturesFileType"]  = None
        src["ModelFolder"]       = None
        src["ModelFileType"]     = None
        src["SoundFolder"]       = None
        src["SoundFileType"]     = None
        src["MusicFolder"]       = None
        src["MusicFileType"]     = None
        src["MakeDataFile"]      = None
        src["MakeUserDataFile"]  = None
        src["MakeEntitiesFile"]  = None
        src["MakeShadersFile"]   = None
        src["MakeTexturesFile"]  = None
        src["MakeMdlEntsFile"]   = None
        src["MdlEntsFolder"]     = None
        src["MdlEntsFileType"]   = None
        src["MakeListFile"]      = None
        src["ListFileFolder"]    = None
        src["ListFileType"]      = None
        self.src = src
        self.root = root

        # Create the dialog form and the buttons
        quarkpy.qmacro.dialogbox.__init__(self, form1, src,
            MakeFiles = quarkpy.qtoolbar.button(self.MakeFiles,"Make .qrk Files",ico_editor, 3, "Make .qrk Files"),
            close = quarkpy.qtoolbar.button( self.close, "DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.", ico_editor, 0, "Cancel function")
            )

    def datachange(self, df):
        if self.src["EntitiesFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["EntitiesFolder"] = self.src["GameFilesLocation"]
        if self.src["ShadersFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["ShadersFolder"] = self.src["GameFilesLocation"]
        if self.src["TexturesFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["TexturesFolder"] = self.src["GameFilesLocation"]
        if self.src["ModelFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["ModelFolder"] = self.src["GameFilesLocation"]
        if self.src["SoundFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["SoundFolder"] = self.src["GameFilesLocation"]
        if self.src["MusicFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["MusicFolder"] = self.src["GameFilesLocation"]
        if self.src["MdlEntsFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["MdlEntsFolder"] = self.src["GameFilesLocation"]
        if self.src["ListFileFolder"] is None and self.src["GameFilesLocation"] is not None:
            self.src["ListFileFolder"] = self.src["GameFilesLocation"]

    def MakeFiles(self, btn):
        "Accepts all entries and checks for invalid ones."
        "Then starts making the processing function calls."

        quarkx.globalaccept()
        root = self.root
        gamefileslocation = self.src["GameFilesLocation"]
        if gamefileslocation is None:
            quarkx.msgbox("You did not select a 'Game Files Location'.\nPlease do so and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        gamepakfiletype = self.src["GamePakFileType"]
        if gamepakfiletype is None:
            quarkx.msgbox("You did not enter a 'Pak file type'.\nPlease do so and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        gamepakfiletype = gamepakfiletype.rsplit(".")
        gamepakfiletype = gamepakfiletype[len(gamepakfiletype)-1]
        if gamepakfiletype is not None and not gamepakfiletype.startswith("."):
            gamepakfiletype = "." + gamepakfiletype
        gamename = self.src["GameName"]
        if gamename is None:
            quarkx.msgbox("You did not enter a 'Game Name'.\nPlease do so and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        gameenginetype = self.src["GameEngineType"]
        if gameenginetype is None:
            quarkx.msgbox("You did not select a 'Game Engine'.\nPlease do so and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        entitiesfolder = self.src["EntitiesFolder"]
        entitiesfiletype = self.src["EntitiesFileType"]
        if (entitiesfolder == gamefileslocation or entitiesfiletype is None or entitiesfolder is None):
            quarkx.msgbox("Entities items incomplete in Step 1.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        entitiesfiletype = entitiesfiletype.rsplit(".")
        entitiesfiletype = entitiesfiletype[len(entitiesfiletype)-1]
        if entitiesfiletype is not None and not entitiesfiletype.startswith("."):
            entitiesfiletype = "." + entitiesfiletype
        shadersfolder = self.src["ShadersFolder"]
        shadersfiletype = self.src["ShadersFileType"]
        if (shadersfolder == gamefileslocation or shadersfiletype is None or shadersfolder is None):
            quarkx.msgbox("Shaders items incomplete in Step 1.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        shadersfiletype = shadersfiletype.rsplit(".")
        shadersfiletype = shadersfiletype[len(shadersfiletype)-1]
        if shadersfiletype is not None and not shadersfiletype.startswith("."):
            shadersfiletype = "." + shadersfiletype
        texturesfolder = self.src["TexturesFolder"]
        texturesfiletype = self.src["TexturesFileType"]
        if (texturesfolder == gamefileslocation or texturesfiletype is None or texturesfolder is None):
            quarkx.msgbox("Textures items incomplete in Step 1.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        if texturesfiletype.find(texturesfolder) != -1:
            texturesfiletype = texturesfiletype.split(".", 1)
            texturesfiletype = texturesfiletype[len(texturesfiletype)-1]
        if texturesfiletype is not None and not texturesfiletype.startswith("."):
            texturesfiletype = "." + texturesfiletype
        modelfolder = self.src["ModelFolder"]
        modelfiletype = self.src["ModelFileType"]
        if (modelfolder == gamefileslocation or modelfiletype is None or modelfolder is None):
            quarkx.msgbox("Model items incomplete in Step 1.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        modelfiletype = modelfiletype.rsplit(".")
        modelfiletype = modelfiletype[len(modelfiletype)-1]
        if modelfiletype is not None and not modelfiletype.startswith("."):
            modelfiletype = "." + modelfiletype
        soundfolder = self.src["SoundFolder"]
        soundfiletype = self.src["SoundFileType"]
        if (soundfolder == gamefileslocation or soundfiletype is None or soundfolder is None):
            quarkx.msgbox("Sound items incomplete in Step 1.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        if soundfiletype.find(soundfolder) != -1:
            soundfiletype = soundfiletype.split(".", 1)
            soundfiletype = soundfiletype[len(soundfiletype)-1]
        if soundfiletype is not None and not soundfiletype.startswith("."):
            soundfiletype = "." + soundfiletype
        musicfolder = self.src["MusicFolder"]
        musicfiletype = self.src["MusicFileType"]
        if (musicfolder == gamefileslocation or musicfiletype is None or musicfolder is None):
            quarkx.msgbox("Music items incomplete in Step 1.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        if musicfiletype.find(musicfolder) != -1:
            musicfiletype = musicfiletype.split(".", 1)
            musicfiletype = musicfiletype[len(musicfiletype)-1]
        if musicfiletype is not None and not musicfiletype.startswith("."):
            musicfiletype = "." + musicfiletype

        makedatafile = self.src["MakeDataFile"]
        makeuserdatafile = self.src["MakeUserDataFile"]
        makeentitiesfile = self.src["MakeEntitiesFile"]
        makeshadersfile = self.src["MakeShadersFile"]
        maketexturesfile = self.src["MakeTexturesFile"]
        makemdlentsfile = self.src["MakeMdlEntsFile"]
        mdlentsfolder = self.src["MdlEntsFolder"]
        mdlentsfiletype = self.src["MdlEntsFileType"]
        makelistfile = self.src["MakeListFile"]
        listfilefolder = self.src["ListFileFolder"]
        listfiletype = self.src["ListFileType"]
        if (mdlentsfolder == gamefileslocation or mdlentsfiletype is None or mdlentsfolder is None) and (makemdlentsfile == "51"):
            quarkx.msgbox("You entered something for Mdl Entity files,\nbut you did not do all three items.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        if mdlentsfiletype is not None:
            mdlentsfiletype = mdlentsfiletype.rsplit(".")
            mdlentsfiletype = mdlentsfiletype[len(mdlentsfiletype)-1]
        if mdlentsfiletype is not None and not mdlentsfiletype.startswith("."):
            mdlentsfiletype = "." + mdlentsfiletype
        if (listfilefolder == gamefileslocation or listfiletype is None or listfilefolder is None) and (makelistfile == "60"):
            quarkx.msgbox("You entered something for List files,\nbut you did not do all three items.\nPlease correct and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return
        if listfiletype is not None:
            listfiletype = listfiletype.rsplit(".")
            listfiletype = listfiletype[len(listfiletype)-1]
        if listfiletype is not None and not listfiletype.startswith("."):
            listfiletype = "." + listfiletype
        if makedatafile != "10" and makeuserdatafile != "20" and makeentitiesfile != "30" and makeshadersfile != "40" and maketexturesfile != "50" and makemdlentsfile != "51" and makelistfile != "60":
            quarkx.msgbox("You did not check for any files to be created.\nPlease do so and try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            return

### Crates the game folder, does an existing game folder test and make the function calls if ok to do so.
   #     self.close(btn) # This will close the master dialog too soon.
        if not os.path.exists(self.QuArKpath + '\\' + gamename):
            os.mkdir(self.QuArKpath + '\\' + gamename)
            hadfolder = 0
            # Makes the calls to the processing functions.
            if makedatafile == "10":
                datafiledialog = quarkx.newform("datadialogform")
                DataFileDlg(datafiledialog, root, self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                            gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                            texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                            musicfolder, musicfiletype, hadfolder, makeuserdatafile, makeentitiesfile, makeshadersfile,
                            maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
            elif makeuserdatafile == "20":
                MakeUserDataFile(root, self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                 gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                                 texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                 musicfolder, musicfiletype, hadfolder, makeentitiesfile, makeshadersfile,
                                 maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
            elif makeentitiesfile == "30":
                entitiesfiledialog = quarkx.newform("entitiesdialogform")
                EntitiesFileDlg(entitiesfiledialog, root, self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                                texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                musicfolder, musicfiletype, hadfolder, makeshadersfile,
                                maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
            elif makeshadersfile == "40":
                MakeShadersFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                gamepakfiletype, shadersfolder, shadersfiletype,
                                texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                musicfolder, musicfiletype, hadfolder,
                                maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
            elif maketexturesfile == "50":
                MakeTexturesFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                 gamepakfiletype,
                                 texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                 musicfolder, musicfiletype, hadfolder,
                                 makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
            elif makemdlentsfile == "51":
                MakeMdlEntsFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                 gamepakfiletype,
                                 modelfolder, modelfiletype, soundfolder, soundfiletype,
                                 musicfolder, musicfiletype, hadfolder,
                                 mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
            elif makelistfile == "60":
                MakeListFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                             gamepakfiletype,
                             modelfolder, modelfiletype, soundfolder, soundfiletype,
                             musicfolder, musicfiletype, hadfolder,
                             listfilefolder, listfiletype)

        else:
            result = quarkx.msgbox("A folder with the same name " + gamename + " already exist in your main QuArK folder.\n\nCAUTION:\nAny file in that folder with the same name\nas a new file will be overwritten.\n\nDo you wish to continue making new files for that folder?", quarkpy.qutils.MT_WARNING, quarkpy.qutils.MB_YES_NO_CANCEL)
            if result == MR_YES:
                hadfolder = 1
                # Makes the calls to the processing functions.
                if makedatafile == "10":
                    datafiledialog = quarkx.newform("datadialogform")
                    DataFileDlg(datafiledialog, root, self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                                texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                musicfolder, musicfiletype, hadfolder, makeuserdatafile, makeentitiesfile, makeshadersfile,
                                maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
                elif makeuserdatafile == "20":
                    MakeUserDataFile(root, self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                     gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                                     texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                     musicfolder, musicfiletype, hadfolder, makeentitiesfile, makeshadersfile,
                                     maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
                elif makeentitiesfile == "30":
                    entitiesfiledialog = quarkx.newform("entitiesdialogform")
                    EntitiesFileDlg(entitiesfiledialog, root, self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                    gamepakfiletype, entitiesfolder, entitiesfiletype, shadersfolder, shadersfiletype,
                                    texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                    musicfolder, musicfiletype, hadfolder, makeshadersfile,
                                    maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
                elif makeshadersfile == "40":
                    MakeShadersFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                    gamepakfiletype, shadersfolder, shadersfiletype,
                                    texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                    musicfolder, musicfiletype, hadfolder,
                                    maketexturesfile, makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
                elif maketexturesfile == "50":
                    MakeTexturesFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                     gamepakfiletype,
                                     texturesfolder, texturesfiletype, modelfolder, modelfiletype, soundfolder, soundfiletype,
                                     musicfolder, musicfiletype, hadfolder,
                                     makemdlentsfile, mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
                elif makemdlentsfile == "51":
                    MakeMdlEntsFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                     gamepakfiletype,
                                     modelfolder, modelfiletype, soundfolder, soundfiletype,
                                     musicfolder, musicfiletype, hadfolder,
                                     mdlentsfolder, mdlentsfiletype, makelistfile, listfilefolder, listfiletype)
                elif makelistfile == "60":
                    MakeListFile(self.QuArKpath, gamename, gameenginetype, gamefileslocation,
                                 gamepakfiletype,
                                 modelfolder, modelfiletype, soundfolder, soundfiletype,
                                 musicfolder, musicfiletype, hadfolder,
                                 listfilefolder, listfiletype)
            else:
                quarkx.msgbox("PROCESS CANCELED:\n\nNothing was written to the " + gamename + " folder\nand all files in that folder remain unchanged.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
                return


def Intro(root):
    "Sets up the new window form for the main dialog and calls its class."

    quarkx.msgbox("This is the main tool that will step you through the process of\nconverting various game files to the QuArK *.qrk file format.\n\nIt is primarily used to add new game support for editing in QuArK.\nBut it can also be used to add new elements for existing games\nsuch as Entity, Texture, Shader, Model and Sound '.qrk' files.\n\nIf you encounter any problems using this 'Conversion Tool' utility,\nplease make a posting on the 'QuArK's Forums site'\nwhich is directly accessible from the QuArK '?' main menu.\n\nSome folders may need to be extracted from the game's pak files\nfor this process and to edit with in QuArK.\nIf so, place those folders in the same folder that the pak files are in.\nYou will be prompted to do so, if needed, during this process.\n\nPlease click the 'OK' button to continue to 'Step 1'.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
    form1 = quarkx.newform("masterform")
    TypeOfConversionDlg(form1, root)

text = "Conversion Tool - use this first"
import quarkpy.qentbase
quarkpy.qentbase.RegisterEntityConverter(text, None, None, Intro)

