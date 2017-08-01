"""   QuArK  -  Quake Army Knife

 ConvertToolBSPtypeEnts.py - Makes a list of all entities, their Specifics and ;desc\Help\hint data in
                -  each game .bsp file by folder to use in creating the (gamename)Entities.qrk file.
            - cdunde Aug. 31, 2010
            - This file is used by the QuArK ConvertionTool on the QuArK Explorer main Files menu.
            - The completed file will be created in the game's folder in QuArK's main folder
            - along with a .log file (opened with any text editor) giving entity summery detail. 
            - This program will go one sub-folder deep and looks for the 'classname' key in the .bsp file.
"""

#
#$Header: /cvsroot/quark/runtime/plugins/ConvertToolBSPtypeEnts.py,v 1.1 2010/09/01 08:11:22 cdunde Exp $
#

import os, os.path

def BSPtypeEntList(root, QuArKpath, gamename, gamefileslocation,
         gamepakfiletype, entitiesfolder, entitiesfiletype,
         modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
         WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint,
         WriteSoundBrowser, UseSoundBrowser, UseDefaultSoundHint, SoundHint,
         WriteMusicBrowser, UseMusicBrowser, UseDefaultMusicHint, MusicHint,
         UseColorPicker):

 #   entitiesfolder = "maps"  ### Set the name of the entitiesfolder to be scanned here (where any files & sub-folders are).
 #   entitiesfiletype = ".bsp"    ### Set the entitiesfiletype to scan here.

    OutPutList = (gamename + "Entities")  ### Changes the output list name here to what you want.
    GameFolder = gamefileslocation.split("\\") # "Base"   ### Sets the game folder name here.
    GameFolder = GameFolder[len(GameFolder)-1]
    PakFile = gamepakfiletype.replace(".", "") # "pk3"    ### Sets the Pak file type (no period) to call here.
    ModelType = modelfiletype.replace(".", "") # "tik"    ### Sets the model file type (no period) to call here.
    SoundType = soundfiletype.replace(".", "") # "wav"    ### Sets the sound file type (no period) to call here to play a sound.
    MusicType = musicfiletype.replace(".", "") # "mus"    ### Sets the model file type (no period) to call here to play music.
    entitiy_count = 0
    form_count = 0

    OutPutList = OutPutList + ".log" 
    dirname = entitiesfolder
    o = open(QuArKpath + '\\' + gamename + '\\' + OutPutList, "w")
    QRKfile = OutPutList.replace(".log" , ".qrk")
    q = open(QuArKpath + '\\' + gamename + '\\' + QRKfile, "w")

    names = os.listdir(dirname)
    groupnames = {}
    classnames = {}

    def HandleInput(file, classnames):
        left_curly = 0
        lines = file.readlines()
        file.close()
        lineCount = len(lines)
        section = []

        for i in xrange(0, lineCount):
            line = lines[i]
            if line.find("\x00") != -1:
                continue
            line = line.strip()
            if line.startswith('"classname"') and left_curly == 0:
                catchup = ['{']
                left_curly = 1
                backup = i - 1
                while 1:
                    prev_line = lines[backup]
                    prev_line.strip()
                    if prev_line.endswith("{") or prev_line.find("\x00") != -1:
                        section = catchup
                        break
                    if line != '':
                        catchup = catchup + [prev_line]
                    backup = backup - 1

            if line == "{":
                left_curly = left_curly + 1
                section = [line.strip()]
                continue
            elif line == "}":
                if left_curly == 1:
                    left_curly = 0
                    section = section + [line.strip()]
            else:
                section = section + [line.strip()]
                if line.find("{") != -1:
                    left_curly = left_curly + 1
                if line.find("}") != -1:
                    left_curly = left_curly - 1
                continue

            if len(section) != 0:
                found_class = 0
                for item in xrange(len(section)):
                    if found_class != 0:
                        break
                    if section[item].find("classname") != -1:
                        name = section[item].strip()
                        name = name.split('"classname" ')[1]
                        name = name.replace('"', "")
                        found_class = 1
                        if not name in classnames.keys():
                            classnames[name] = {}
                            classnames[name]['Specs'] = {}
                        for i in xrange(len(section)):
                            spec = section[i].strip()
                            if spec == "{" or spec == "}" or spec.find("classname") != -1:
                                continue
                            spec = spec.split('" "', 1)
                            spec_name = spec[0]
                            spec_name = spec_name.replace('"', "")
                            try:
                                spec_value = spec[1].strip()
                                spec_value = spec_value.replace('"', "")
                            except:
                                break
                            # To get all values used for spawnflag settings.
                            if spec_name.find("spawnflags") != -1:
                                if classnames[name]['Specs'].has_key(spec_name):
                                    if not spec_value in classnames[name]['Specs'][spec_name]:
                                        classnames[name]['Specs'][spec_name] = classnames[name]['Specs'][spec_name] + [spec_value]
                                else:
                                    classnames[name]['Specs'][spec_name] = [spec_value]
                            # To replace reference to another model (ex: model: "*21") with an actual model's name.
                            if spec_name.find("model") != -1 and classnames[name]['Specs'].has_key(spec_name):
                                if classnames[name]['Specs'][spec_name].find("*") != -1 and spec_value.find("*") == -1:
                                    classnames[name]['Specs'][spec_name] = spec_value
                            if not spec_name in classnames[name]['Specs'].keys():
                                classnames[name]['Specs'][spec_name] = spec_value
                section = []


    ### This section handles all the files in the main "files to check" folder, FIRST.
    # o.write(dirname + "\n")         ### Writes the main directory name to our file.
    for name in names:
        if name.endswith(entitiesfiletype):              ### Checks if this is a file name or a folder name.
            print "*** READING ***", name
            file = open(os.path.join(dirname, name), "rb")
            HandleInput(file, classnames)


    ### This section handles all the files in the SUB-FOLDERS, starting with the 1st sub-folder.
    for name in names:
        if name.endswith(entitiesfiletype) or name.find(".") != -1:   ### Checks if this is a file name or a folder name
            pass
        else:
            foldername = dirname + "\\" + name
    #        o.write(foldername + "\n")   ### Writes the sub-folder name to our file.
            try:
                filenames = os.listdir(foldername)
            except:
                continue
            for name in filenames:
                if name.endswith(entitiesfiletype):
    #                o.write("       %s" % name  + "\n")  ### Lists all the files in this folder first.
                    print "*** READING ***", name
                    file = open(os.path.join(foldername, name), "rb")
                    HandleInput(file, classnames)

    ### This section creates the entity groupnames.
    if classnames != {}:
        keys = classnames.keys()
        keys.sort()
        for name in keys:
            group_keys = groupnames.keys()
            if name.find("_") != -1:
                groupname = name.split("_")[0].lower()
            else:
                groupname = name.lower()
            if not groupname in group_keys:
                groupnames[groupname] = [name]
            else:
                groupnames[groupname] = groupnames[groupname] + [name]

    ### This section writes to the data output "o" file.
    if classnames != {}:
        keys = classnames.keys()
        keys.sort()
        total_ents = 0
        for name in keys:
            o.write('\n')
            o.write('classname: "' + name + '"\n')
            total_ents = total_ents + 1
            Specs = classnames[name]['Specs'].keys()
            Specs.sort()
            for spec_name in Specs:
                if spec_name.find("spawnflags") != -1:
                    flags = []
                    for flag in classnames[name]['Specs'][spec_name]:
                        flags = flags + [int(flag)]
                    flags.sort()
                    sorted_flags = []
                    for flag in flags:
                        if flag == 0:
                            continue
                        sorted_flags = sorted_flags + [str(flag)]
                    classnames[name]['Specs'][spec_name] = sorted_flags
                    o.write(spec_name + ': "' + str(classnames[name]['Specs'][spec_name]) + '"\n')
                else:
                    o.write(spec_name + ': "' + classnames[name]['Specs'][spec_name] + '"\n')

        o.write('\nOUTPUT TOTALS\n')
        o.write('=============\n')
        o.write(str(total_ents) + ' Total Entities\n')
        o.write('=====\n\n')

        o.write('Entity Groups\n')
        o.write('=============\n')
        total_ents = 0
        group_keys = groupnames.keys()
        group_keys.sort()
        for name in group_keys:
            o.write(str(len(groupnames[name])) + ' group: ' + name + '\n')
            total_ents = total_ents + len(groupnames[name])
        o.write('-----\n')
        o.write(str(total_ents) + ' Total Group Entities\n')
        o.write('=====\n')

    ### This section creates the entity .qrk file.
    if classnames != {}:
        class_keys = classnames.keys()
        class_keys.sort()
        other_ents_list = ['detail', 'light', 'worldspawn']
        other_ents = []
        misc_ents = []
        primary_list = ['func', 'game', 'info', 'misc', 'other', 'portal', 'script', 'sound', 'trigger']
        primary_ents = {}
        game_specific_ents = []
        group_keys = groupnames.keys()
        group_keys.sort()
        for group_name in group_keys:
            for other_name in other_ents_list:
                if group_name.find(other_name) != -1:
                    for key in class_keys:
                        if key.find(group_name) != -1 and (not key in other_ents):
                            other_ents = other_ents + [key]
            if group_name.startswith("misc"):
                for key in class_keys:
                    if key.startswith(group_name) and (not key in misc_ents):
                        misc_ents = misc_ents + [key]
            elif group_name in primary_list:
                if not primary_ents.has_key(group_name):
                    primary_ents[group_name] = []
                group_classnames = primary_ents[group_name]
                for key in class_keys:
                    if key.startswith(group_name + "_") and (not key in group_classnames):
                        primary_ents[group_name] = primary_ents[group_name] + [key]
            else:
                for key in class_keys:
                    fix_key = key.lower()
                    if (fix_key.startswith(group_name + "_") or fix_key == group_name) and (not key in game_specific_ents and not key in other_ents):
                        game_specific_ents = game_specific_ents + [key]
        # Add specific groups or group items that might have been missed or not found in a .bsp file but SHOULD exist.
        if not primary_ents.has_key('game'):
            primary_ents['game'] = game_specific_ents
        else:
            primary_ents['game'] = primary_ents['game'] + game_specific_ents
        if not primary_ents.has_key('other'):
            primary_ents['other'] = other_ents
        else:
            primary_ents['other'] = primary_ents['other'] + other_ents
        if not primary_ents.has_key('misc'):
            primary_ents['misc'] = misc_ents
        else:
            primary_ents['misc'] = primary_ents['misc'] + misc_ents

        ### Writes the new .qrk file header.
        q.write("QQRKSRC1\n")
        q.write("// " + gamename + " Entities file for Quark\n")
        q.write("\n")
        q.write("//$" + "Header: Exp $" + "\n")
        q.write("// ----------- REVISION HISTORY ------------\n")
        q.write("//$" + "Log: " + gamename + "Entities.qrk,v $" + "\n")
        q.write("//\n")

        ### Writes the setup part for the Toolbox and Entities folders.
        q.write("\n")
        q.write("{\n")
        q.write("  QuArKProtected = \"1\"\n")
        q.write("  Description = \"" + gamename + " Entities\"\n")
        q.write("\n")
        q.write("  Toolbox Folders.qtx =\n")
        q.write("  {\n")
        q.write("    Toolbox = \"New map items...\"\n")
        q.write("    Root = \"" + gamename + " Entities.qtxfolder\"\n")
        q.write("    " + gamename + " Entities.qtxfolder =\n")
        q.write("    {\n")
        q.write("      ;desc = \"Created from " + gamename + ".bsp files.\"\n")

        ### Entity type list, to make them regular (:e) or "box" type (:b) or some other type, by primary group. (KEEP ALL LOWER CASE)
        func_e_types = ['base', 'beam', 'camera', 'earthquake', 'exploder', 'piece', 'spawn', 'teleportdest', 'throw']
        game_b_types = ['emitter', 'door']
        other_e_types = ['light']
        script_b_types = ['door', 'object', 'skyorigin']
        trigger_e_types = ['relay']

        ### Writes all the individual Entities e: sections here.
        for group_name in primary_list:
            if group_name == 'game' and game_specific_ents == []: # Skip processing 'game' ents if none exist.
                continue
            if not primary_ents.has_key(group_name): # Skip processing group_name ents if none exist.
                continue
            q.write("      " + group_name + "_* entities.qtxfolder =\n")
            q.write("      {\n")
         #   if group_name == 'misc' and misc_ents == []: # check 'misc' ents for misc_model, if not add it.
         #       pass
            group_ent_names = primary_ents[group_name]
            for ent_name in group_ent_names:
                entitiy_count = entitiy_count + 1 # Used just for console printout for checking all were processed.
                fix_name = ent_name.lower()
                ent_Specs = classnames[ent_name]['Specs']
                type = ":e =\n" # Sets our default entity type.
                if group_name == "func":
                    type = ":b =\n"
                    for e in func_e_types:
                        if fix_name.find(e) != -1:
                            type = ":e =\n"
                            break
                    q.write("        " + ent_name + type)
                elif group_name == "game":
                    for b in game_b_types:
                        if fix_name.find(b) != -1:
                            type = ":b =\n"
                            break
                    q.write("        " + ent_name + type)
                elif group_name == "info":
                    q.write("        " + ent_name + type)
                elif group_name == "misc":
                    q.write("        " + ent_name + type)
                elif group_name == "other":
                    type = ":b =\n"
                    for e in other_e_types:
                        if fix_name.find(e) != -1:
                            type = ":e =\n"
                            break
                    q.write("        " + ent_name + type)
                elif group_name == "portal":
                    q.write("        " + ent_name + type)
                elif group_name == "script":
                    for b in script_b_types:
                        if fix_name.find(b) != -1:
                            type = ":b =\n"
                            break
                    q.write("        " + ent_name + type)
                elif group_name == "sound":
                    q.write("        " + ent_name + type)
                elif group_name == "trigger":
                    type = ":b =\n"
                    for e in trigger_e_types:
                        if fix_name.find(e) != -1:
                            type = ":e =\n"
                            break
                    q.write("        " + ent_name + type)
                else:
                    q.write("        " + ent_name + type)

                # Opens, writes and closes each entity's default settings section.
                q.write("        {\n")
                q.write("          ;desc = \"" + ent_name + "\"\n")
                keys = ent_Specs.keys()
                for key in keys:
                    fix_key = key.lower()
                    if fix_key.find("model") != -1 and ent_Specs[key].find("*") == -1:
                        q.write("          " + key +" = \"" + ent_Specs[key] + "\"\n")
                if type.find("light:e =") != -1:
                    q.write("          light = \"300\"\n")
                    q.write("          _color = \"1 1 1\"\n")
                    q.write("          angles = \"0 0 0\"\n")
                    q.write("          origin = \"0 0 0\"\n")
                elif type.find(":e =") != -1:
                    q.write("          angle = \"360\"\n")
                    q.write("          origin = \"0 0 0\"\n")
                else:
                    q.write("          angle = \"360\"\n")
                    q.write("          ;incl = \"defpoly\"\n")
                q.write("        }\n")

            q.write("      }\n") ### Closes each entitiy's category sub-folder.

        q.write("    }\n") ### Closes the entitiy's section in the Toolbox.
        q.write("  }\n") ### Closes the Toolbox Folders section.

        ### Writes all the needed "includes" in the Entities form: section here.
        q.write("\n")
        q.write("  Entity Forms.fctx =\n")
        q.write("  {\n")
        q.write("    // Definition of 'includes'\n")
        q.write("\n")

        # Writes the commonspecifics include.
        q.write("    t_commonspecifics:incl =\n")
        q.write("    {\n")
        q.write("      target: =\n")
        q.write("      {\n")
        q.write("        txt = \"&\"\n")
        q.write("        hint = \"Name of the entity that this one targets.\"\n")
        q.write("      }\n")
        q.write("      targetname: =\n")
        q.write("      {\n")
        q.write("        txt = \"&\"\n")
        q.write("        hint = \"Name of this entity, used as a target by another entity.\"\n")
        q.write("      }\n")
        q.write("      scale: =\n")
        q.write("      {\n")
        q.write("        txt = \"&\"\n")
        q.write("        hint = \"Float amount that affects the model's size,\"\n")
        q.write("            $0D\"for ex: .05 (half size) or 2 (twice its size).\"\n")
        q.write("            $0D\"(May not work for all entities.)\"\n")
        q.write("      }\n")
        q.write("      hide: =\n")
        q.write("      {\n")
        q.write("        txt = \"&\"\n")
        q.write("        hint = \"A value of 1 will hide the model.\"\n")
        q.write("            $0D\"(May not work for all entities.)\"\n")
        q.write("      }\n")
        q.write("    }\n")
        q.write("\n")

        # Writes the modelbrowser include.
        q.write("    t_modelbrowser:incl =\n")
        q.write("    {\n")
        q.write("      hint = \"Use this to select any ." + ModelType + " file you want.\"\n")
        q.write("          $0D\"You must extract the folder with the ." + ModelType + " files\"\n")
        q.write("          $0D\"from the ." + PakFile + " file and put it in your '" + GameFolder + "' folder.\"\n")
        q.write("          $0D\"Click the 'Help Book' above for more possible detail.\"\n")
        q.write("      Typ = \"EP\"\n")
        q.write("      BasePath = \"$Game\\" + GameFolder + "\"\n")
        q.write("      CutPath = \"$Game\?\?\\\"\n")
        q.write("      DefExt = \"" + ModelType + "\"\n")
        q.write("      DirSep = \"/\"\n")
        q.write("    }\n")
        q.write("\n")

        # Writes the soundbrowser include.
        q.write("    t_soundbrowser:incl =\n")
        q.write("    {\n")
        q.write("      hint = \"Use this to select any ." + SoundType + " file you want.\"\n")
        q.write("          $0D\"You must extract the folder with the ." + SoundType + " files\"\n")
        q.write("          $0D\"from the ." + PakFile + " file and put it in your '" + GameFolder + "' folder.\"\n")
        q.write("          $0D\"Click the 'Help Book' above for more possible detail.\"\n")
        q.write("      Typ = \"EP\"\n")
        q.write("      BasePath = \"$Game\\" + GameFolder + "\"\n")
        q.write("      CutPath = \"$Game\?\"\n")
        q.write("      DefExt = \"" + SoundType + "\"\n")
        q.write("      DirSep = \"/\"\n")
        q.write("    }\n")
        q.write("\n")

        # Writes the musicbrowser include.
        q.write("    t_musicbrowser:incl =\n")
        q.write("    {\n")
        q.write("      hint = \"Use this to select any ." + MusicType + " file you want.\"\n")
        q.write("          $0D\"You must extract the folder with the ." + MusicType + " files\"\n")
        q.write("          $0D\"from the ." + PakFile + " file and put it in your '" + GameFolder + "' folder.\"\n")
        q.write("          $0D\"Click the 'Help Book' above for more possible detail.\"\n")
        q.write("      Typ = \"EP\"\n")
        q.write("      BasePath = \"$Game\\" + GameFolder + "\"\n")
        q.write("      CutPath = \"$Game\?\"\n")
        q.write("      DefExt = \"" + MusicType + "\"\n")
        q.write("      DirSep = \"/\"\n")
        q.write("    }\n")
        q.write("\n")

        ### Writes all the individual Entities form: section here.
        def ConvertFlagsToKeys(spawnflag):
            #Convert spawnflag number to flags set
            keys = []
            value = 1
            while spawnflag:
                if spawnflag % 2:
                    #Odd number; found a flag!
                    keys += [value]
                    spawnflag -= 1
                spawnflag /= 2
                value *= 2
            return keys

        # List of entity specific items we will handle specifically or just want to by pass.
        SkipSpecificItems = ['_color', 'color', 'hide', 'light', 'model', 'modelname', 'scale', 'target', 'targetname', 'spawnflags']

        for group_name in primary_list:
            if group_name == 'game' and game_specific_ents == []: # Skip processing 'game' forms if none exist.
                continue
            if not primary_ents.has_key(group_name): # Skip processing group_name ents if none exist.
                continue
            group_ent_names = primary_ents[group_name]
            for ent_name in group_ent_names:
                form_count = form_count + 1 # Used just for console printout for checking all were processed.
                fix_name = ent_name.lower()
                ent_Specs = classnames[ent_name]['Specs']
                q.write("    " + ent_name + ":form =\n")
                q.write("    {\n") ### Opens this Entitie's form: here.
                q.write("      help = \"Created from .bsp file.\"$0D\"This entity needs to be updated by hand\"$0D\"in this games addons .qrk file.\"\n")
                q.write("      bbox = '-8 -8 -8 8 8 8'\n")
                if ent_Specs.has_key("spawnflags") and len(ent_Specs['spawnflags']) != 0:
                    flags = []
                    for flag in ent_Specs['spawnflags']:
                        keys = ConvertFlagsToKeys(int(flag))
                        for key in keys:
                            if not key in flags:
                                flags = flags + [key]
                    flags.sort()
                    for flag in flags:
                        q.write("      spawnflags: = \n")
                        q.write("      {\n")
                        q.write("        txt = \"&\"\n")
                        q.write("        typ = \"X" + str(flag) + "\"\n")
                        q.write("        cap = \"unknown\"\n")
                        q.write("      }\n")
                q.write("      t_commonspecifics = !\n")
                if ent_Specs.has_key("model") or ent_Specs.has_key("modelname"):
                    if ent_Specs.has_key("model"):
                        q.write("      model: = \n")
                        q.write("      {\n")
                        q.write("        t_modelbrowser = !\n")
                        q.write("        txt = \"&\"\n")
                        q.write("        hint = \"arbitrary ." + ModelType + " file to display.\"\n")
                        q.write("      }\n")
                    else:
                        q.write("      modelname: = \n")
                        q.write("      {\n")
                        q.write("        t_modelbrowser = !\n")
                        q.write("        txt = \"&\"\n")
                        q.write("        hint = \"The name of the ." + ModelType + " file you wish to spawn. (Required)\"\n")
                        q.write("      }\n")
                if ent_Specs.has_key("light"):
                    q.write("      light: = \n")
                    q.write("      {\n")
                    q.write("        Txt = \"&\"\n")
                    q.write("        Hint = \"light value, default 300\"\n")
                    q.write("      }\n")
                if ent_Specs.has_key("_color") or ent_Specs.has_key("color"):
                    if ent_Specs.has_key("_color"):
                        q.write("      _color: = \n")
                        q.write("      {\n")
                        q.write("        Txt = \"&\"\n")
                        q.write("        Hint = \"light color (not the intensity, only the color)\"\n")
                        q.write("      }\n")
                        q.write("      _color: = \n")
                        q.write("      {\n")
                        q.write("        Txt = \"&\"\n")
                        q.write("        Typ = \"L\"\n")
                        q.write("        Hint = \"Click here to pick the light color.\"\n")
                        q.write("      }\n")
                    else:
                        q.write("      color: = \n")
                        q.write("      {\n")
                        q.write("        Txt = \"&\"\n")
                        q.write("        Hint = \"light color (not the intensity, only the color)\"\n")
                        q.write("      }\n")
                        q.write("      color: = \n")
                        q.write("      {\n")
                        q.write("        Txt = \"&\"\n")
                        q.write("        Typ = \"L\"\n")
                        q.write("        Hint = \"Click here to pick the light color.\"\n")
                        q.write("      }\n")

                # Now does the rest of the entity's specific items.
                keys = ent_Specs.keys()
                for key in keys:
                    if key in SkipSpecificItems:
                        continue
                    fix_key = key.lower()
                    q.write("      " + key + ": = \n")
                    q.write("      {\n")
                    if fix_key.find("sound") != -1 or fix_key.find("noise") != -1 or fix_key.find("music") != -1:
                        q.write("        t_soundbrowser = !\n")
                    elif fix_key.find("color") != -1 or fix_key.find("light") != -1:
                        q.write("        Typ = \"L\"\n")
                    q.write("        txt = \"&\"\n")
                    q.write("        hint = \"Created from .bsp file.\"$0D\"This item needs to be updated by hand\"$0D\"in this games addons .qrk file.\"\n")
                    q.write("      }\n")

                q.write("    }\n") ### Closes this Entitie's form: here.


        q.write("  }\n") ### Closes the Entities form: section here.
        q.write("}\n") ### Closes the new .qrk file contents here.
    print "entitiy_count check", entitiy_count
    print "form_count check", form_count

    ### This section closes all open files.
    o.close()
    q.close() ### Closes the new .qrk file here.
    
#
#$Log: ConvertToolBSPtypeEnts.py,v $
#Revision 1.1  2010/09/01 08:11:22  cdunde
#Added entity extraction from game map .bsp files for .qrk file creation of Conversion Tool system.
#
#
