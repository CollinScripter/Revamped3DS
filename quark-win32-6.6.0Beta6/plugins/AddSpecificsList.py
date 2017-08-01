"""   QuArK  -  Quake Army Knife

 AddSpecificsList.py - Adds all entitie's Specifics to the "New file.qrk" file
                -   using the .spf file created earlier and rename the .qrk file properly.
            - cdunde March 30, 2008
            - This file is used by the "ConvertToolQ3typeEnts.py" file which is used
                - by the QuArK ConvertionTool on the QuArK Explorer main Files menu.
            - The completed file will be created in the game's folder in QuArK's main folder.
            - See "Additional Optional Settings" below. Changed using this tools dialog.
"""

#
#$Header: /cvsroot/quark/runtime/plugins/AddSpecificsList.py,v 1.7 2008/06/25 14:32:32 danielpharos Exp $
#

#
#$Log: AddSpecificsList.py,v $
#Revision 1.7  2008/06/25 14:32:32  danielpharos
#Change to ASCII file property
#
#Revision 1.5  2008/04/06 06:47:41  cdunde
#Added file back without version control to stop overwriting of internal code.
#
#Revision 1.4  2008/04/06 06:46:50  cdunde
#Trying to remove file from version control to get into cvs
#system without overwriting internal file code.
#
#Revision 1.3  2008/04/04 20:46:45  cdunde
#Are you kidding me 8-\
#
#Revision 1.2  2008/04/04 20:42:51  cdunde
#To try and fix their system over writing internal code for logging....nice!
#
#Revision 1.1  2008/04/04 20:19:27  cdunde
#Added a new Conversion Tools for making game support QuArK .qrk files.
#
#

import os, os.path

def AddSpecifics(QuArKpath, gamename, gamefileslocation, gamepakfiletype,
                 modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
                 WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint, WriteSoundBrowser,
                 UseSoundBrowser, UseDefaultSoundHint, SoundHint, WriteMusicBrowser, UseMusicBrowser,
                 UseDefaultMusicHint, MusicHint, UseColorPicker):
    WorkDirectory = (QuArKpath + '\\' + gamename)  ### Sets work folder (where .qrk file will be) Path here.
    Description = (gamename + " Entities")

    ### Additional Optional Settings (start):
    ### ====================================

    #            - Common specifics are items used by most entities except 'worldspawn' and 'info_' entities.
    #            - Here you have two choices, by setting their values to 1, they are:
    #            - To "WriteCommonSpecifics" which just writes them to the file to set them up.
    #            - To "UseCommonSpecifics" which writes their "include" code to each entity that might use them.
    #            - If the second is set to 1 and the first is not,
    #            -     it will not write the "include" code because it doesn't exist.
    #            - Right now they only include "target" and "targetname". You can change or add to the "commonspecifics",
    #            -     but remember to also change or add to the "commonspecificslist" to avoid duplication of these
    #            -     specifics that may already exist in the original file(s) that are being copied.
    commonspecifics = "    t_commonspecifics:incl =\n    {\n      target: =\n      {\n        txt = \"&\"\n        hint = \"Name of the entity that this one targets.\"\n      }\n      targetname: =\n      {\n        txt = \"&\"\n        hint = \"Name of this entity, used as a target by another entity.\"\n            $0D\"Click the 'Help Book' above for more possible detail.\"\n      }\n    }\n"
    commonspecificslist = ["target", "targetname"]

    #            - Does and operates the same as common specifics above but you also need to give the proper settings for:
    #            -     "GamePakFileType", "ModelFileType" and "GameFolderName".
    #            - The actual game file folder that those files are in makes no difference, QuArK uses the folder selected.
    #            - But the files and their folder and sub-folders must be extracted from the game's "Pak" file and placed in the
    #            -     proper location, which is usually the same place where the "Pak" files are located.
    #            - Some games use a "script" file instead of the actual model file. If this is the case then
    #            -    the type of script file, ex: cik, can be used as the setting for the "ModelFileType".
    #            - Adding something to "ModelHint" will display that hint, other wise if one exist it will be used instead.
    #            -    If "UseDefaultModelHint" is set to 1 then that hint will be used.
    #            -    What ever hint method is used for one entity, that same method will be used for all entities.
    GamePakFileType = gamepakfiletype.replace('.', "")
    GamePakFileType = GamePakFileType.strip()
    ModelFileType = modelfiletype.replace('.', "")
    ModelFileType = ModelFileType.strip()
    GameFolderName = gamefileslocation.split('\\')
    GameFolderName = GameFolderName[len(GameFolderName)-1]

    if ModelHint is None:
        ModelHint = ""
    if ModelHint != "":
        ModelHint = ModelHint.replace("\"", "\'")
        if len(ModelHint) > 45:
            lines = ""
            lettercount = 0
            for letter in range(len(ModelHint)):
                lettercount = lettercount + 1
                if lettercount > 40 and ModelHint[letter] == " ":
                    lines = lines + '"$0D\n             "'
                    lettercount = 0
                    continue
                lines = lines + ModelHint[letter]
            ModelHint = lines
        ModelHint = "      hint = \"" + ModelHint + "\"\n"
    if UseDefaultModelHint != "0":
        ModelHint = "      hint = \"Use this to select any ." + ModelFileType + " file you want.\"$0D\n            \"You must extract the folder with the ." + ModelFileType + " files\"$0D\n            \"from the ." + GamePakFileType + " file and put it in your '" + GameFolderName + "' folder.\"\n            $0D\"Click the 'Help Book' above for more possible detail.\"\n"
    modelbrowser = "    t_modelbrowser:incl =\n    {\n" + ModelHint + "      Typ = \"EP\"\n      BasePath = \"$Game\\" + GameFolderName + "\"\n      CutPath = \"$Game\\?\\" + "\"\n" + "      DefExt = \"" + ModelFileType + "\"\n" + "      DirSep = \"/\"\n" + "    }\n"

    #            - Does and operates the same as common specifics above but you also need to give the proper settings for:
    #            -     "GamePakFileType", "SoundFileType" and "GameFolderName".
    #            - The actual game file folder that those files make no difference, QuArK uses the folder selected.
    #            - But the files and their folder must be extracted from the game's "Pak" file and placed in the
    #            -     proper location, which is usually the same place where the "Pak" files are located.
    #            - Adding something to "SoundHint" will display that hint, other wise if one exist it will be used instead.
    #            -    If "UseDefaultSoundHint" is set to 1 then that hint will be used.
    #            -    What ever hint method is used for one entity, that same method will be used for all entities.
    ### Coded to allow nore then one type of file when written like this "wav; *.mp3" in the dialog input box.
    SoundFileType = soundfiletype
    if SoundFileType.startswith('.'):
        SoundFileType = SoundFileType.strip('.')
    SoundFileType = SoundFileType.strip()

    if SoundHint is None:
        SoundHint = ""
    if SoundHint != "":
        SoundHint = SoundHint.replace("\"", "\'")
        if len(SoundHint) > 45:
            lines = ""
            lettercount = 0
            for letter in range(len(SoundHint)):
                lettercount = lettercount + 1
                if lettercount > 40 and SoundHint[letter] == " ":
                    lines = lines + '"$0D\n             "'
                    lettercount = 0
                    continue
                lines = lines + SoundHint[letter]
            SoundHint = lines
        SoundHint = "      hint = \"" + SoundHint + "\"\n"
    if UseDefaultSoundHint != "0":
        SoundHint = "      hint = \"Use this to select any ." + SoundFileType + " file you want.\"$0D\n            \"You must extract the folder with the ." + SoundFileType + " files\"$0D\n            \"from the ." + GamePakFileType + " file and put it in your '" + GameFolderName + "' folder.\"\n            $0D\"Click the 'Help Book' above for more possible detail.\"\n"
    soundbrowser = "    t_soundbrowser:incl =\n    {\n" + SoundHint + "      Typ = \"EP\"\n      BasePath = \"$Game\\" + GameFolderName + "\"\n      CutPath = \"$Game\\?\\" + "\"\n" + "      DefExt = \"" + SoundFileType + "\"\n" + "      DirSep = \"/\"\n" + "    }\n"

    #            - Because some games have a setting in their "worldspawn" entity to play "music" which might not be
    #            -    an actual "sound" file but a "script" file instead. Using the settings below for that entity.
    #            - Does and operates the same as common specifics above but you also need to give the proper settings for:
    #            -     "GamePakFileType", "MusicFileType" and "GameFolderName".
    #            - The actual game file folder that those files make no difference, QuArK uses the folder selected.
    #            - But the files and their folder must be extracted from the game's "Pak" file and placed in the
    #            -     proper location, which is usually the same place where the "Pak" files are located.
    #            - Adding something to "MusicHint" will display that hint, other wise if one exist it will be used instead.
    #            -    If "UseDefaultMusicHint" is checked then that hint will be used.
    #            -    This hint method and settings only apply to the "worldspawn" entity.
    #            -    But can be copied and pasted to others once the new GameEntities.qrk file is created.
    ### Coded to allow nore then one type of file when written like this "mus; *.mp3" in the dialog input box.
    MusicFileType = musicfiletype
    if MusicFileType.startswith('.'):
        MusicFileType = MusicFileType.strip('.')
    MusicFileType = MusicFileType.strip()

    if MusicHint is None:
        MusicHint = ""
    if MusicHint != "":
        MusicHint = MusicHint.replace("\"", "\'")
        if len(MusicHint) > 45:
            lines = ""
            lettercount = 0
            for letter in range(len(MusicHint)):
                lettercount = lettercount + 1
                if lettercount > 40 and MusicHint[letter] == " ":
                    lines = lines + '"$0D\n             "'
                    lettercount = 0
                    continue
                lines = lines + MusicHint[letter]
            MusicHint = lines
        MusicHint = "      hint = \"" + MusicHint + "\"\n"
    if UseDefaultMusicHint != "0":
        MusicHint = "      hint = \"Use this to select any ." + MusicFileType + " file you want.\"$0D\n            \"You must extract the folder with the ." + MusicFileType + " files\"$0D\n            \"from the ." + GamePakFileType + " file and put it in your '" + GameFolderName + "' folder.\"\n            $0D\"Click the 'Help Book' above for more possible detail.\"\n"
    musicbrowser = "    t_musicbrowser:incl =\n    {\n" + MusicHint + "      Typ = \"EP\"\n      BasePath = \"$Game\\" + GameFolderName + "\"\n      CutPath = \"$Game\\?\\" + "\"\n" + "      DefExt = \"" + MusicFileType + "\"\n" + "      DirSep = \"/\"\n" + "    }\n"

    #            - "UseColorPicker" checked adds a color setting selector button to all specifics with "color" in its name.
    #            - If un-check or "0" it will not be added. Used for things such as "light" color, "sun" color...

    ### Additional Optional Settings (end):
    ### ==================================

    names = os.listdir(WorkDirectory)
    for name in range(len(names)):
        if names[name].endswith(".spf"):
            OutPutList = spffile = names[name]
            OutPutList = OutPutList.replace(".spf" , ".qrk")
            break
        if name == len(names)-1:
            print "No .spf file found !"
            print "See & use the 'GetQ3typeEntitiesList.py' file first to create the needed .spf file"
            print "Operation Terminated !"
            print "\a" # Makes the computer "Beep" once if a file is not found.
    for name in range(len(names)):
        if names[name] == "New file.qrk":
            break
        if name == len(names)-1:
            print "No 'New file.qrk' file found !"
            print "See & use the 'GetQ3typeEntitiesList.py' file to create the needed .def and .spf files."
            print "Then use QuArK to create the needed 'New file.qrk' file needed."
            print "Operation Terminated !"
            print "\a" # Makes the computer "Beep" once if a file is not found.

    output = open(WorkDirectory + '\\' + OutPutList, "w")
    qrkinput = open(os.path.join(WorkDirectory, "New file.qrk"))
    spfinput = open(os.path.join(WorkDirectory, spffile))

    while 1: ### Sets up the first entity name in the .spf file for comparison later.
        spfline = spfinput.readline()
        if spfline == '':
            break
        if spfline == "ENTITY\n":
            spfline = spfinput.readline()
            spfline = spfline.strip()
            break

    output.write("QQRKSRC1\n")
    output.write("// " + Description + " file for Quark\n")
    output.write("\n")
    output.write("//$" + "Header: Exp $" + "\n")
    output.write("// ----------- REVISION HISTORY ------------\n")
    output.write("//$" + "Log: " + OutPutList + ",v $" + "\n")
    output.write("//\n")
    output.write("\n")
    output.write("{\n")
    output.write("  QuArKProtected = \"1\"\n")
    output.write("  Description = \"" + Description + "\"\n")
    output.write("\n")

    while 1: ### Sets up the first entity name in the .spf file for comparison later.
        qrkline = qrkinput.readline()
        if qrkline.find("Toolbox Folders.qtx =") != -1:  ### Finds the "Toolbox Folders" starting point.
            output.write(qrkline) ### Writes the above line to the new .qrk file.
            while 1: ### Creates the new game.qrk file.
                qrkline = qrkinput.readline()
                if qrkline == '':
                    break
                if qrkline.find("Root =") != -1:  ### Finds the "Root =" line so it can be written properly.
                    output.write("    Root = \"" + Description + ".qtxfolder\"\n")
                    qrkline = qrkinput.readline()
                    output.write("    " + Description + ".qtxfolder =\n")
                    break
                output.write(qrkline)
            while 1: ### Creates the new game.qrk file.
                qrkline = qrkinput.readline()
                if qrkline == '':
                    break
                if qrkline.find("Entity Forms.fctx =") != -1:  ### Finds the entities:forms starting point.
                    includes = 0
                    while qrkline != "  }\n":
                        if qrkline == '':
                            break
                        if qrkline.find(":form =") != -1:
                            if includes == 0:
                                includes = 1
                                output.write("    // Definition of includes\n")
                                output.write("\n")
                                if WriteCommonSpecifics != "0":
                                    output.write(commonspecifics)
                                    output.write("\n")
                                if WriteModelBrowser != "0":
                                    output.write(modelbrowser)
                                    output.write("\n")
                                if WriteSoundBrowser != "0":
                                    output.write(soundbrowser)
                                    output.write("\n")
                                if WriteMusicBrowser != "0":
                                    output.write(musicbrowser)
                                    output.write("\n")
                            Entity = qrkline.split(":") ### Gets the old .ark files entity name ready for comparison.
                            EntityName = Entity[0]
                            EntityName = EntityName.strip()
                            while qrkline != "    }\n": ### Copys all of the old entity:form section first before closing it with this line.
                                output.write(qrkline)
                                qrkline = qrkinput.readline()
                                if qrkline == "    }\n":
                                    break
                            if spfline == EntityName:
                                openbracket = 0
                                incommonspecifics = 0
                                ### Writes common specifics include here if set to do so.
                                if (UseCommonSpecifics != "0") and (WriteCommonSpecifics != "0") and (EntityName != "worldspawn") and (not EntityName.startswith("info_")):
                                    output.write("      t_commonspecifics = !\n")
                                while spfline != "\n": ### Starts coping all the specifics, for a matched entity, from the .spf file to the new game.qrk file.
                                    spfline = spfinput.readline()
                                    if spfline == '':
                                        if openbracket  == 1:
                                            output.write("      }\n") ### Closes last entity's specific item here.
                                            openbracket = 0
                                            incommonspecifics = 0
                                        break
                                    if spfline == "\n":
                                        if openbracket  == 1:
                                            output.write("      }\n") ### Closes last entity's specific item here.
                                            openbracket = 0
                                            incommonspecifics = 0
                                        break
                                    if spfline.startswith("\""): ### Indicates a new entity's specific item.
                                        spfline = spfline.split("\"", 2)
                                        blank, spfname, spfhint = spfline
                                        incommonspecifics = 0
                                        if (UseCommonSpecifics != "0"):
                                            for specific in commonspecificslist:
                                                if spfname == specific:
                                                    incommonspecifics = 1
                                                    continue
                                        if incommonspecifics != 0:
                                            continue
                                        if openbracket  == 1:
                                            output.write("      }\n") ### Closes previous specific item here, if any.
                                        output.write("      " + spfname + ": =\n")
                                        output.write("      {\n") ### Opens for new entity here.
                                        ### Section below writes the individual "specific's" "include" file selectors if set to do so.
                                        if spfname.find("model") != -1:
                                            if (UseModelBrowser != "0") and (WriteModelBrowser != "0"):
                                                output.write("        t_modelbrowser = !\n")
                                        if (spfname.find("sound") != -1 or spfname.find("noise") != -1):
                                            if EntityName == "worldspawn":
                                                if (UseMusicBrowser != "0") and (WriteMusicBrowser != "0"):
                                                    output.write("        t_musicbrowser = !\n")
                                            else:
                                                if (UseSoundBrowser != "0") and (WriteSoundBrowser != "0"):
                                                    output.write("        t_soundbrowser = !\n")
                                        openbracket = 1
                                        output.write("        txt = \"&\"\n")
                                        if spfname.find("color") != -1:
                                            if (UseColorPicker != "0"):
                                                output.write("        Typ = \"LN\"\n")
                                        spfhint = spfhint.strip()
                                        output.write("        hint = \"" + spfhint + "\"\n")
                                    else: ### Writes additional hint lines here, if any.
                                        if incommonspecifics != 0:
                                            continue
                                        spfline = spfline.strip()
                                        output.write("            $0D\"" + spfline + "\"\n")

                                while 1: ### Sets up the next entity name in the .spf file for comparison later.
                                    spfline = spfinput.readline()
                                    if spfline == '':
                                        break
                                    if spfline == "ENTITY\n":
                                        spfline = spfinput.readline()
                                        spfline = spfline.strip()
                                        break

                        output.write(qrkline) ### Copys all of the 'Forms.fctx section needed to the new .qrk game file.
                        qrkline = qrkinput.readline()
                        if qrkline == "  }":
                           break

                output.write(qrkline) ### Copys everything before the :forms section and closing brackets from the 'New file.qrk' to the DataGame.qrk file.

        if qrkline == '':
            break

    spfinput.close()
    qrkinput.close()
    output.close()
    WorkDirectory = WorkDirectory.replace("\\", "/")
    os.remove(WorkDirectory + '/New file.qrk') # Deletes this temp file.
    os.remove(WorkDirectory + '/' + gamename + 'Entities' + '.def') # Deletes this temp file.
    os.remove(WorkDirectory + '/' + gamename + 'Entities' + '.spf') # Deletes this temp file.

