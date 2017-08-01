"""   QuArK  -  Quake Army Knife

# ConvertToolD3typeEnts.py - Makes a list of all entities, their Specifics and ;desc\Help\hint data in each
#                -  game definition file by folder to use in creating the (gamename)Entities.qrk file.
#            - cdunde March 16, 2008 - bulk of code form Rowdy's ent2.py file for getting Doom3 entities.
            - This file is used by the QuArK ConvertionTool on the QuArK Explorer main Files menu.
            - The completed file will be created in the game's folder in QuArK's main folder.
            - This program can use any file type that uses the 'entityDef' key.
"""

#
#$Header: /cvsroot/quark/runtime/plugins/ConvertToolD3typeEnts.py,v 1.5 2010/08/19 08:04:27 cdunde Exp $
#

import os, os.path
from ConvertToolGet_tokens import *

def D3typeEntList(root, QuArKpath, gamename, gamefileslocation,
         gamepakfiletype, entitiesfolder, entitiesfiletype, modelfolder,
         modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
         WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint,
         WriteSoundBrowser, UseSoundBrowser, UseDefaultSoundHint, SoundHint, MakeSoundList, SoundListFileFolder, SoundListFileType,
         WriteMusicBrowser, UseMusicBrowser, UseDefaultMusicHint, MusicHint, MakeModelList, MakeClipMdlList, ClipMdlFileFolder, ClipMdlFileType,
         UseColorPicker):

    def deQuote(s):
        if s.startswith('"') and s.endswith('"'):
            s = s[1:len(s) - 1]
        s = s.replace('"', '').replace("'", '')
        return s

    def parseIntoDict(tokens):
        "Input: a while bunch of tokens from one .def file, Output: a dict of entities"

        result = {}
        iToken = iter(tokens)
        tokenType, tokenValue = iToken.next()
    #    print "%s/%s" % (str(tokenType), str(tokenValue))
        while tokenType != T_EOF:
            if (tokenType == T_COMMENT) or (tokenType == T_EOF):
                tokenType, tokenValue = iToken.next()
                #print "%s/%s" % (str(tokenType), str(tokenValue))
                continue
            if (tokenType == T_IDENTIFIER) and (tokenValue == 'entityDef'):
                tokenType, tokenValue = iToken.next()
        #        print "%s/%s" % (str(tokenType), str(tokenValue))
        #        print "    found entity: %s" % tokenValue
                entityName = tokenValue
                tokenType, tokenValue = iToken.next()
                if (tokenType != T_SPECIAL) or (tokenValue != '{'):
        #            print 'expected "{" after token name missing'
                    break
                # now we should have a series of:
                # "specific" "arg"
                # pairs (with a couple of special exceptions) until the next '}'
                specificList = {}
                while 1:
                    tokenType, tokenValue = iToken.next()
                    if (tokenType == T_COMMENT):
                        continue
                    if (tokenType == T_EOF) or ((tokenType == T_SPECIAL) and (tokenValue == '}')):
                        break
                    specificName = tokenValue.replace('"', '')
       #             print "specificName",specificName
                    tokenType, tokenValue = iToken.next()
       #             print "tokenType",tokenType
       #             print "tokenValue",tokenValue
                    argValue = tokenValue
       #             print '        %s = %s' % (str(specificName), str(argValue))

                    # Here are some specifics and improper code we are going to skip.
                    # "editor_color"				"0 .5 .8"
                    # "editor_mover"				"1"
                    # "spawnclass"				"idDoor"
                    if specificName in ["editor_color",
                                        "editor_combatnode",
                                        "editor_copy1",
                                        "editor_copy2",
                                        "editor_copy3",
                                        "editor_copy4",
                                        "editor_copy5",
                                        "editor_def",
                                        "editor_float",
                                        "editor_gui",
                                        "editor_light",
                                        "editor_mat",
                                        "editor_material",
                                        "editor_model",
                                        "editor_mover",
                                        "editor_ragdoll",
                                        "editor_rotatable",
                                        "editor_showangle",
                                        "editor_showangles",
                                        "\\",
                                        "",
                                        "inv_weapon",
                                        "spawnclass"]:
         #               print '            -- skipped'
                        continue
                    # otherwise if the specific starts with "editor_" it is a new one that also defines it's type
                    # note: we might need the editor_model spec later on
                    if specificName.startswith('editor_') and (specificName != 'editor_model'):
                        s = specificName
                        s = s.replace('"', '')
                        s = ' '.join(s.split())
                        c = s.split(' ')
         #               print "line 232 c is >>>", c
                        specDesc = deQuote(argValue)
                        try:
                            specName = c[1]
                        except:
                            specName = c[0]
                        if c[0] == 'editor_mins' or c[0] == 'editor_maxs':
                            specType = 'x'
                        if c[0].startswith('editor_usage'):
                            specType = 'h'
                        if c[0] == 'editor_var':
                            specType = 'v'
                        elif c[0] == 'editor_bool':
                            specType = 'b'
                        elif c[0] == 'editor_snd':
                            specType = 's'
                        else:
         #                   print '            -- undefined type: %s' % specificName
                            specType = '?'
                        specDefault = '' # the default might appear later
                        specDesc = specDesc.replace("\\n", "")
                        specificList[specName] = (specType, specDefault, specDesc)
                    else:
                        # this is probably a default value
                        s = specificName
                        s = s.replace('"', '')
                        if specificList.has_key(s):
                            # found it in the list - update the default
                            specType, specDefault, specDesc = specificList[s]
                            specDefault = argValue.replace('"', '')
                            specDesc = specDesc.replace("\\n", "")
                            specificList[s] = (specType, specDefault, specDesc)
                        else:
                            # not in the list - add it with an unknown type
                            specName = s
                            specType = '?'
                            specDefault = argValue.replace('"', '')
                            specDesc = ''
                            specificList[specName] = (specType, specDefault, specDesc)
         #           print specificList
                result[entityName] = specificList

            tokenType, tokenValue = iToken.next()
         #   print "%s/%s" % (str(tokenType), str(tokenValue))

        return result

    def findEntity(name):
    #    print 'looking for an entity called "%s" ...' % name
        for name1 in allEntities.keys():
            #print '    looking in file: %s' % name1
            entities = allEntities[name1]
            for entName in entities.keys():
         #       print '        looking at entity: %s' % entName
         #       print '        comparing "%s" to "%s"' % (str(entName.strip()), str(name.strip()))
                if str(entName.strip()) == str(name.strip()):
                    return entities[entName]
        return None

    def SetupEntities(foldername):
        try:
            names = os.listdir(foldername)
        except:
            return
        names.sort()
        for name in names:
            if name.endswith(entitiesfiletype):
         #       print "processing: %s" % name
                tokens = getTokens(foldername + '\\' + name)

                ## dump all tokens
                #for tokenType, tokenValue in tokens:
                #    if tokenType == T_EOF:
                #        print "end of file"
                #    elif tokenType == T_NUMBER:
                #        print "number: %s" % tokenValue
                #    elif tokenType == T_COMMENT:
                #        print "comment: %s" % tokenValue
                #    elif tokenType == T_QSTRING:
                #        print "quoted string: %s" % tokenValue
                #    elif tokenType == T_IDENTIFIER:
                #         print "identifier: %s" % tokenValue
                #    elif tokenType == T_SPECIAL:
                #        print "special: %s" % tokenValue
                #    else:
                #        print "internal error: unrecognised token type: %d" % tokenType
                #        break

                ## looking for number tokens
                #for tokenType, tokenValue in tokens:
                #    if tokenType == T_NUMBER:
                #       print "    found number: %s" % tokenValue

                entities = parseIntoDict(tokens)
                #print entities

                allEntities[name] = entities

        #print allEntities

        # now process the inherits hopefully there are no nested inherits)
  #      print "processing inherits ..."
        kount = 1
        while kount > 0:
            # we want to keep doing this until all recursive inheritance is done
            # we have to loop as the inheritance is no in particular order
            kount = 0
            # if kount is 0 at the end of this for loop, then we didn't find
            # anything that needs to be inherited
            for name in allEntities.keys():
       #         print "    doing: %s" % name[:name.find('.')]
                entities = allEntities[name]
                for entName in entities.keys():
       #             print "        %s" % entName
                    thisEnt = entities[entName]
                    for specName in thisEnt.keys():
                        if specName != "inherit":
                            continue
                        kount += 1
                        # now we inherit (i.e. copy) from the entity called specDefault
                        # gotta find it first
                        specType, specDefault, specDesc = thisEnt[specName]
                        sourceEntity = findEntity(specDefault)
                        if sourceEntity is None:
                            # oops, couldn't find it
                     #       print "            ** failed to inherit from: %s" % specDefault
                            thisEnt["not_inherited"] = thisEnt["inherit"]
                            del thisEnt["inherit"]
                        else:
                            # found it - copy all the source entity's specifics to the current (destination) entity
                     #       print "            ** inherited from: %s" % specDefault
                            for sourceSpec in sourceEntity.keys():
                                thisEnt[sourceSpec] = sourceEntity[sourceSpec]
                            thisEnt["inherited"] = thisEnt["inherit"]
                            del thisEnt["inherit"]

        ### Does the upper :e or :b section for all entities being processed at this time.
        # one section per entity file (more or less groups them logically)
        names = allEntities.keys()
        names.sort()
        for name in names:
            entities = allEntities[name]
            entNames = entities.keys()
            entNames.sort()
            if len(entNames) == 0:
                continue
            eo.write('      %s Entities.qtxfolder =\n' % name[:name.find('.')])
            eo.write('      {\n')
            for entName in entNames:
                thisEnt = entities[entName]
         #       print "line 368 entName",entName
         #       print "line 369 thisEnt",thisEnt
                # this will need to be name:e for point entities, and name:b for block entities
                # but, how to differentiate based on info in the .def files, "?" is a name:b type.
                if thisEnt.has_key('editor_mins'):
                    if thisEnt['editor_mins'][2] != "?":
                        eo.write('        %s:e =\n' % entName)
                        eo.write('        {\n')
                    else:
                        eo.write('        %s:b =\n' % entName)
                        eo.write('        {\n')
                        eo.write('          ;incl = "defpoly"\n')
                else:
                    eo.write('        %s:e =\n' % entName)
                    eo.write('        {\n')
                # write one line for each specific that has a default value
                # we might omit some of these later on
                # note: the existing QuArK entity defs seem to include the bare minimum of values here
                eo.write('          name = "renameme"\n')
                done_origin = 0
                done_angle = 0
                specNames = thisEnt.keys()
                specNames.sort()
                for specName in specNames:
                    # if we succeeded to inherit above then we have updated the specific to
                    # "inherited" and we do not want to write it here
                    if specName == 'not_inherited':
                        continue

                    specType, specDefault, specDesc = thisEnt[specName]
                    if specName.startswith('editor_'):
                        continue

                    if specDefault != '':
                        eo.write('          %s = "%s"\n' % (specName, specDefault))
                        if specName == "origin":
                            done_origin = 1
                        if specName == "angle":
                            done_angle = 1
                if done_origin == 0:
                    eo.write('          origin = "0 0 0"\n')
                if done_angle == 0:
                    eo.write('          angle = "360"\n')
                # for block entities we need to write ';incl = "defpoly"'
                # make the next bit more meaningful!!!
                eo.write('          ;desc = "This is the %s entity."\n' % entName)
                eo.write('        }\n') # end of this entity
            eo.write('      }\n') # end of this .def file (i.e. group of related entities)

        ### Does the :form section for all entities being processed at this time.
        names = allEntities.keys()
        names.sort()
        for name in names:
            entities = allEntities[name]
            entNames = entities.keys()
            entNames.sort()
            if len(entNames) == 0:
                continue
            for entName in entNames:
                thisEnt = entities[entName]
                fo.write('    %s:form =\n' % entName)
                fo.write('    {\n')
                # need this for block entities?
                #fo.write('      mdl = "[model2]"\n')
                Help = 0
                for key in thisEnt.keys():
                    if key.startswith('editor_usage'):
                        comment = thisEnt[key][2].replace("  ", "\"\n          $0D\"")
                        if Help == 0:
                            fo.write('      Help = "' + comment + '"\n')
                            Help = 1
                        else:
                            fo.write('          $0D"' + comment + '"\n')
                if Help == 0:
                    fo.write('      Help = "This is a %s entity."\n' % entName)
                if thisEnt.has_key('editor_mins'):
                    if thisEnt['editor_mins'][2] != "?":
                        bbmin = thisEnt['editor_mins'][2]
                        bbmax = thisEnt['editor_maxs'][2]
                        fo.write("      bbox = '" + bbmin + " " + bbmax +"'\n")
                if (UseCommonSpecifics != "0") and (WriteCommonSpecifics != "0") and (entName != "worldspawn"):
                    fo.write("      t_commonspecifics = !\n") # Adds the common specifics.
                if thisEnt.has_key('target'):
                    pass
                else:
                    if (entName != "worldspawn") and (not entName.startswith("info_player")):
                        fo.write('      target: =\n')
                        fo.write('      {\n')
                        fo.write('        txt = "&"\n')
                        fo.write('        hint = "The entity\'s name this one will target or trigger."\n')
                        fo.write('      }\n')

                # write one section for each specific that has a default value
                # we might omit some of these later on
                specNames = thisEnt.keys()
                specNames.sort()
                for specName in specNames:
                    # if we failed to inherit above (there is one of these) then we have updated
                    # the specific to "not_inherited" and we do not want to write it here
                    if specName == 'not_inherited':
                        continue
                    # if we succeeded to inherit above then we have updated the specific to
                    # "inherited" and we do not want to write it here
                    if specName == 'not_inherited':
                        continue
                    # These are items used above for "Help" and "bbox" and not specifics.
                    if specName.startswith('editor_'):
                        continue

                    specType, specDefault, specDesc = thisEnt[specName]
                    if entName == 'light' and specName == 'color':
                        specName = '_color'
                    # actually, it would appear that there are no bitmapped values (until Rowdy is proved wrong)
                    if specType in ['v', 'b', 's', '?']:
                        # value (variable?) and those with no type
                        if specName.startswith("music"):
                            fo.write('      s_shader: =\n')
                        else:
                            fo.write('      %s: =\n' % specName)
                        fo.write('      {\n')
                        fo.write('        Txt = "&"\n')
                        if specDesc == '':
                            if specType == 'b':
                                fo.write('        Hint = "Check to activate or deactivate this specific."\n')
                                fo.write('        Typ = "X"\n')
                            elif specName.find("color") != -1 or specName.find("_color") != -1:
                                fo.write('        Hint = "The RGB color to use for this specific."\n')
                                if (UseColorPicker != "0"):
                                    fo.write("        Typ = \"LN\"\n")
                            elif specName.find("model") != -1:
                                if (UseModelBrowser != "0") and (WriteModelBrowser != "0"):
                                    fo.write("        t_modelbrowser = !\n")
                            elif specName.find("noise") != -1 or specName.find("sound") != -1 or specName.find("snd_") != -1 or specName.find("s_shader") != -1:
                                if (UseSoundBrowser != "0") and (WriteSoundBrowser != "0"):
                                    fo.write("        t_soundbrowser = !\n")
                            elif specName.find("music") != -1:
                                if (UseMusicBrowser != "0") and (WriteMusicBrowser != "0"):
                                    fo.write("        t_musicbrowser = !\n")
                            else:
                                fo.write('        Hint = "There is no hint for this."\n')
                        else:
                            fo.write('        Hint = "%s"\n' % specDesc)
                            if specType == 'b':
                                fo.write('        Typ = "X"\n')
                            elif specName.find("color") != -1 or specName.find("_color") != -1:
                                fo.write("        Typ = \"LN\"\n")
                            elif specName.find("model") != -1:
                                if (UseModelBrowser != "0") and (WriteModelBrowser != "0"):
                                    fo.write("        t_modelbrowser = !\n")
                            elif specName.find("noise") != -1 or specName.find("sound") != -1 or specName.find("snd_") != -1 or specName.find("s_shader") != -1:
                                if (UseSoundBrowser != "0") and (WriteSoundBrowser != "0"):
                                    fo.write("        t_soundbrowser = !\n")
                            elif specName.find("music") != -1:
                                if (UseMusicBrowser != "0") and (WriteMusicBrowser != "0"):
                                    fo.write("        t_musicbrowser = !\n")
                        fo.write('      }\n')
                        if specName.startswith("music"):
                            if MakeSoundList != "0":
                                fo.write('      t_sounds = !\n')
                        elif specName.find("s_shader") != -1:
                            if MakeSoundList != "0":
                                fo.write('      t_sounds = !\n')
                        elif specName == "model":
                            if MakeModelList != "0":
                                fo.write('      t_model = !\n')
                        elif specName == "clipmodel":
                            if MakeClipMdlList != "0":
                                fo.write('      t_clipmdl = !\n')
                    else:
                        # undefined
                        if specName.find("color") != -1 or specName.find("_color") != -1:
                            fo.write('        Hint = "The RGB color to use for this specific."\n')
                            if (UseColorPicker != "0"):
                                fo.write("        Typ = \"LN\"\n")
                        elif specName.find("model") != -1:
                            if (UseModelBrowser != "0") and (WriteModelBrowser != "0"):
                                fo.write("        t_modelbrowser = !\n")
                        elif specName.find("noise") != -1 or specName.find("sound") != -1 or specName.find("snd_") != -1 or specName.find("s_shader") != -1:
                            if (UseSoundBrowser != "0") and (WriteSoundBrowser != "0"):
                                fo.write("        t_soundbrowser = !\n")
                        elif specName.find("music") != -1:
                            if (UseMusicBrowser != "0") and (WriteMusicBrowser != "0"):
                                fo.write("        t_musicbrowser = !\n")
                        else:
                            fo.write('        Hint = "There is no hint for this."\n')

                    # do we need this???
                    #fo.write('      model2: =\n')
                    #fo.write('      {\n')
                    #if (UseModelBrowser != "0") and (WriteModelBrowser != "0"):
                    #    fo.write('        t_modelbrowser = !\n')
                    #fo.write('        Txt = "&"\n')
                    #fo.write('        Hint = "Path and name of a model to use for door."\n')
                    #fo.write('      }\n')
                    #fo.write('      t_model2 = !\n')

                    # template for bitmapped values:
                    #fo.write('      spawnflags: =\n')
                    #fo.write('      {\n')
                    #fo.write('        Txt = "&"\n')
                    #fo.write('        Typ = "X1"\n')
                    #fo.write('        Cap = "START_OPEN"\n')
                    #fo.write('        Hint = "This door will start open."\n')
                    #fo.write('      }\n')
                    #fo.write('      spawnflags: =\n')
                    #fo.write('      {\n')
                    #fo.write('        Txt = "&"\n')
                    #fo.write('        Typ = "X4"\n')
                    #fo.write('        Cap = "CRUSHER"\n')
                    #fo.write('        Hint = "This will crush the player."\n')
                    #fo.write('      }\n')

                fo.write('    }\n') # end of this entity

    ### Start of processing code
    mainworkfoldername = entitiesfolder
    eo = open(QuArKpath + '\\' + gamename + '\\' + 'Entities.txt', 'w')
    fo = open(QuArKpath + '\\' + gamename + '\\' + 'Forms.txt', 'w')
    allnames = os.listdir(mainworkfoldername)
    allnames.sort()

    ### The line below sends the "main work folder" FIRST for any individual files in it to be processed.
    allEntities = {}
    SetupEntities(mainworkfoldername)

    ### This section handles all the files in the SUB-FOLDERS, starting with the 1st sub-folder.
    for name in allnames:
        allEntities = {}
        if name.find(".") != -1:   ### Checks if this is a file name or a folder name
            pass
        else:
            foldername = mainworkfoldername + "\\" + name
            SetupEntities(foldername)

    ### Closes the temp output files for the entities and forms sections and makes the final .qrk file.
    eo.close()
    fo.close()
    o = open(QuArKpath + '\\' + gamename + '\\' + gamename + 'Entities.qrk', 'w')
    ### Writes start of Entities.qrk file here
    o.write('QQRKSRC1\n')
    o.write('// ' + gamename + ' Entities file for Quark\n')
    o.write('\n')
    o.write('//$' + 'Header: Exp $' + '\n')
    o.write('// ----------- REVISION HISTORY ------------\n')
    o.write('//$' + 'Log: ' + gamename + 'Entities.qrk,v $' + '\n')
    o.write('//\n')
    o.write('\n')
    o.write('{\n')
    o.write('  QuArKProtected = "1"\n')
    o.write('  Description = "' + gamename + ' Entities"\n')
    o.write('\n')
    o.write('  Toolbox Folders.qtx =\n')
    o.write('  {\n')
    o.write('    Toolbox = "New map items..."\n')
    o.write('    Root = "' + gamename + ' Entities.qtxfolder"\n')
    o.write('    ' + gamename + ' Entities.qtxfolder =\n')
    o.write('    {\n')
    o.write('      ;desc = "Created from ' + gamename + ' ' + entitiesfiletype + ' files"\n')

    ### Copys all data from the temp 'Entities.txt' to the .qrk file.
    ei = open(QuArKpath + '\\' + gamename + '\\' + 'Entities.txt')
    while 1:
        s = ei.readline()
        if s == "":
            ei.close()
            break
        o.write(s)

    ### Closes the entity section written above.
    o.write('    }\n')
    o.write('  }\n')

    ### Writes the :form section opening lines and include statements
    GamePakFileType = gamepakfiletype.replace('.', "")
    GamePakFileType = GamePakFileType.strip()
    ModelFileType = modelfiletype.replace('.', "")
    ModelFileType = ModelFileType.strip()
    GameFolderName = gamefileslocation.split('\\')
    GameFolderName = GameFolderName[len(GameFolderName)-1]

    o.write('  Entity Forms.fctx =\n')
    o.write('  {\n')
    # Writes the include statements first.
    o.write('    // Definition of includes\n')
    o.write('\n')
    o.write('    t_player_size:incl = { bbox = \'-16 -16 -24 16 16 32\' }\n')
    o.write('    t_ammo_size:incl = { bbox = \'-16 -16 -16 16 16 16\' }\n')
    o.write('    t_weapon_size:incl = { bbox = \'-16 -16 -16 16 16 16\' }\n')
    o.write('    t_teleport_size:incl = { bbox = \'-32 -32 -4 32 32 4\' }\n')
    o.write('    t_item_size:incl = { bbox = \'-16 -16 -16 16 16 16\' }\n')
    o.write('\n')
    if WriteCommonSpecifics != "0":
        o.write('    t_commonspecifics:incl =\n')
        o.write('    {\n')
        o.write('      name: =\n')
        o.write('      {\n')
        o.write('        txt = "&"\n')
        o.write('        hint = "To work, you need to give each entity its own name."\n')
        o.write('      }\n')
        o.write('      origin: =\n')
        o.write('      {\n')
        o.write('        txt = "&"\n')
        o.write('        hint = "You may need to set the x,y,z position in the map by hand."\n')
        o.write('      }\n')
        o.write('      angle: =\n')
        o.write('      {\n')
        o.write('        txt = "&"\n')
        o.write('        hint = "You may need to set this by hand."\n')
        o.write('      }\n')
        o.write('    }\n')
        o.write('\n')


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
    if WriteModelBrowser != "0":
        o.write(modelbrowser)
        o.write("\n")

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
    if WriteSoundBrowser != "0":
        o.write(soundbrowser)
        o.write("\n")

    ### Write the sound list form:
    if MakeSoundList == "38":
        o.write('    t_sounds:incl =\n')
        o.write('    {\n')
        o.write('      s_shader: =\n')
        o.write('      {\n')
        o.write('        Txt = " "\n')
        o.write('        Typ = "B"\n')
        o.write('        Cap = "sounds..."\n')
        o.write('        form = "t_sounds_form:form"\n')
        o.write('        hint = "Available sound files"\n')
        o.write('      }\n')
        o.write('    }\n')
        o.write('\n')
        o.write('    t_sounds_form:form =\n')
        o.write('    {\n')
        soundshaders = os.listdir(SoundListFileFolder)
        for name in soundshaders:
            if name.endswith(SoundListFileType):
                shaders = []
                si = open(SoundListFileFolder + '\\' + name)
                while 1:
                    s = si.readline()
                    if s == "":
                        si.close()
                        break
                    if s.startswith('sound '):
                        s = s.replace('sound ', "", 1)
                        s = s.strip()
                        shaders = shaders + [s]
                    elif s.find('{') != -1:
                        s = s.replace('{', "")
                        s = s.strip()
                        shaders = shaders + [s]
                    elif s[0].isalnum():
                        s = s.strip()
                        shaders = shaders + [s]
                if len(shaders) == 0:
                    continue
                shaders.sort()
                o.write('      s_shader: =\n')
                o.write('      {\n')
                o.write('        typ = "CL"\n')
                file = name.replace(SoundListFileType, "")
                o.write('        txt = "' + file + '"\n')
                o.write('        items =\n')
                for shader in range(len(shaders)):
                    if shaders[shader].startswith('//'):
                        continue
                    shaders[shader] = shaders[shader].strip()
                    shaders[shader] = shaders[shader].split(' ')
                    shaders[shader] = shaders[shader][0]
                    shaders[shader] = shaders[shader].replace('"', "")
                    if len(shaders[shader]) > 3 and shaders[shader][len(shaders[shader])-4] == ".":
                        continue
                    if len(shaders[shader]) == 0:
                        continue
                    if shader == len(shaders)-1:
                        o.write('          "' + shaders[shader] +'"\n')
                    else:
                        o.write('          "' + shaders[shader] +'"$0D\n')
                o.write('        values =\n')
                for shader in range(len(shaders)):
                    if shaders[shader].startswith('//'):
                        continue
                    shaders[shader] = shaders[shader].strip()
                    shaders[shader] = shaders[shader].split(' ')
                    shaders[shader] = shaders[shader][0]
                    shaders[shader] = shaders[shader].replace('"', "")
                    if len(shaders[shader]) > 3 and shaders[shader][len(shaders[shader])-4] == ".":
                        continue
                    if len(shaders[shader]) == 0:
                        continue
                    if shader == len(shaders)-1:
                        o.write('          "' + shaders[shader] +'"\n')
                    else:
                        o.write('          "' + shaders[shader] +'"$0D\n')
                o.write('      }\n')
        o.write('    }\n')
        o.write('\n')

    ### Write the model list form:
    def listfiles(basefolder, foldername, filenames):
        for name in filenames:
            if modelfiletype.lower() in name.lower():
                o.write('      model: =\n')
                o.write('      {\n')
                o.write('        typ = "CL"\n')
                foldername = foldername.replace(gamefileslocation + "\\", "")
                foldername = foldername.replace("\\", "/")
                o.write('        txt = "' + foldername + '"\n')
                o.write('        items =\n')
                break
        shorttempnames = []
        tempnames = []
        for name in range(len(filenames)):
            if not modelfiletype.lower() in filenames[name].lower():
                continue
            shorttempname = filenames[name].lower().replace(modelfiletype.lower(), "")
            shorttempnames = shorttempnames + [shorttempname]
            tempnames = tempnames + [filenames[name]]
        for name in range(len(shorttempnames)):
            if name == len(shorttempnames)-1:
                o.write('          "' + shorttempnames[name] +'"\n')
            else:
                o.write('          "' + shorttempnames[name] +'"$0D\n')
        for name in filenames:
            if modelfiletype.lower() in name.lower():
                o.write('        values =\n')
                break
        for name in range(len(tempnames)):
            if name == len(tempnames)-1:
                o.write('          "' + foldername + '/' + tempnames[name] +'"\n')
            else:
                o.write('          "' + foldername + '/' + tempnames[name] +'"$0D\n')
        for name in filenames:
            if modelfiletype.lower() in name.lower():
                o.write('      }\n')
                break

    filenames = []
    if MakeModelList == "28":
        o.write('    t_model:incl =\n')
        o.write('    {\n')
        o.write('      model: =\n')
        o.write('      {\n')
        o.write('        Txt = " "\n')
        o.write('        Typ = "B"\n')
        o.write('        Cap = "models..."\n')
        o.write('        form = "t_model_form:form"\n')
        o.write('        hint = "Available model ' + modelfiletype.lower() +' files"\n')
        o.write('      }\n')
        o.write('    }\n')
        o.write('\n')
        o.write('    t_model_form:form =\n')
        o.write('    {\n')
        os.path.walk(modelfolder, listfiles, filenames)
        o.write('    }\n')
        o.write('\n')

    ### Write the clipmodel list form:
    def listfiles(basefolder, foldername, filenames):
        for name in filenames:
            if ClipMdlFileType.lower() in name.lower():
                o.write('      clipmodel: =\n')
                o.write('      {\n')
                o.write('        typ = "CL"\n')
                foldername = foldername.replace(gamefileslocation + "\\", "")
                foldername = foldername.replace("\\", "/")
                o.write('        txt = "' + foldername + '"\n')
                o.write('        items =\n')
                break
        shorttempnames = []
        tempnames = []
        for name in range(len(filenames)):
            if not ClipMdlFileType.lower() in filenames[name].lower():
                continue
            shorttempname = filenames[name].lower().replace(ClipMdlFileType.lower(), "")
            shorttempnames = shorttempnames + [shorttempname]
            tempnames = tempnames + [filenames[name]]
        for name in range(len(shorttempnames)):
            if name == len(shorttempnames)-1:
                o.write('          "' + shorttempnames[name] +'"\n')
            else:
                o.write('          "' + shorttempnames[name] +'"$0D\n')
        for name in filenames:
            if ClipMdlFileType.lower() in name.lower():
                o.write('        values =\n')
                break
        for name in range(len(tempnames)):
            if name == len(tempnames)-1:
                o.write('          "' + foldername + '/' + tempnames[name] +'"\n')
            else:
                o.write('          "' + foldername + '/' + tempnames[name] +'"$0D\n')
        for name in filenames:
            if ClipMdlFileType.lower() in name.lower():
                o.write('      }\n')
                break

    filenames = []
    if MakeClipMdlList == "29":
        o.write('    t_clipmdl:incl =\n')
        o.write('    {\n')
        o.write('      clipmodel: =\n')
        o.write('      {\n')
        o.write('        Txt = " "\n')
        o.write('        Typ = "B"\n')
        o.write('        Cap = "clip models..."\n')
        o.write('        form = "t_clipmdl_form:form"\n')
        o.write('        hint = "Available clip model ' + ClipMdlFileType.lower() +' files"\n')
        o.write('      }\n')
        o.write('    }\n')
        o.write('\n')
        o.write('    t_clipmdl_form:form =\n')
        o.write('    {\n')
        os.path.walk(ClipMdlFileFolder, listfiles, filenames)
        o.write('    }\n')
        o.write('\n')

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
    if WriteMusicBrowser != "0":
        o.write(musicbrowser)
        o.write("\n")

    ### Copys all data from the temp 'Forms.txt' to the .qrk file.
    fi = open(QuArKpath + '\\' + gamename + '\\' + 'Forms.txt')
    while 1:
        s = fi.readline()
        if s == "":
            fi.close()
            break
        o.write(s)

    o.write('  }\n') # Closes end of the :form section.
    o.write('}\n') # Closes end of the .qrk file.
    o.close() # Closes the .qrk file.
    WorkDirectory = (QuArKpath + '\\' + gamename)
    WorkDirectory = WorkDirectory.replace("\\", "/")
    os.remove(WorkDirectory + '/' + 'Entities.txt') # Deletes this temp file.
    os.remove(WorkDirectory + '/' + 'Forms.txt') # Deletes this temp file.
    
#
#$Log: ConvertToolD3typeEnts.py,v $
#Revision 1.5  2010/08/19 08:04:27  cdunde
#Some small fixes for the Conversion Tool system.
#
#Revision 1.4  2009/02/11 15:38:57  danielpharos
#Use correct kind of combobox.
#
#Revision 1.3  2008/04/12 18:16:19  cdunde
#Removed color picker for all editor_color keyword entities.
#
#Revision 1.2  2008/04/12 18:11:48  cdunde
#Added color picker for all editor_color keyword entities.
#
#Revision 1.1  2008/04/11 22:28:48  cdunde
#To add Doom 3 type game engine support for ConvertTool.
#
#

