"""   QuArK  -  Quake Army Knife

 ConvertToolQ3typeEnts.py - Makes a list of all entities, their Specifics and ;desc\Help\hint data in each
                -  game definition file by folder to use in creating the (gamename)Entities.qrk file.
            - cdunde March 28, 2008
            - This file is used by the QuArK ConvertionTool on the QuArK Explorer main Files menu.
            - The completed file will be created in the game's folder in QuArK's main folder.
            - This program will go one sub-folder deep and can use any file type that uses the '/*QUAKED' key.
"""

#
#$Header: /cvsroot/quark/runtime/plugins/ConvertToolQ3typeEnts.py,v 1.4 2010/08/19 08:04:27 cdunde Exp $
#

import os, os.path

def Q3typeEntList(root, QuArKpath, gamename, gamefileslocation,
         gamepakfiletype, entitiesfolder, entitiesfiletype,
         modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
         WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint, WriteSoundBrowser,
         UseSoundBrowser, UseDefaultSoundHint, SoundHint, WriteMusicBrowser, UseMusicBrowser,
         UseDefaultMusicHint, MusicHint, UseColorPicker):
 #   WorkDirectory = "c:\\cdunde_EF2\\"  ### Set Path here to your WorkDirectory.
 #   entitiesfolder = "game"  ### Set the name of the entitiesfolder to be scanned here (where any files & sub-folders are).
 #   entitiesfiletype = ".cpp"  ### Set the entitiesfiletype to scan here.
    OutPutList = (gamename + "Entities")  ### Change the output list name here to what you want.

    OutPutList = OutPutList + ".def" 
    dirname = entitiesfolder
    o = open(QuArKpath + '\\' + gamename + '\\' + OutPutList, "w")
    SpcList = OutPutList.replace(".def" , ".spf")
    specifics = open(QuArKpath + '\\' + gamename + '\\' + SpcList, "w")

    names = os.listdir(dirname)

    def HandleInput(input):
        def_format = 1
     #   linecount = 0  # Do not remove, used for problem solving.
        while 1:
            line = input.readline()
     #       linecount = linecount + 1  # Do not remove, used for problem solving.
     #       print "linecount",linecount  # Do not remove, used for problem solving.
     #       print line  # Do not remove, used for problem solving.
            if line.startswith("--") and entitiesfiletype == ".def":
                def_format = 2
            if line == '':
                input.close()
                return
            if line.startswith('/*QUAKED') or line.startswith('/* QUAKED'):
                if line.startswith('/* QUAKED'):
                    line = line.replace('/* QUAKED','/*QUAKED')
                while 1:
     #               print "linecount",linecount  # Do not remove, used for problem solving.
     #               print line  # Do not remove, used for problem solving.
                    if line == '':
                        input.close()
                        return

                    if line.startswith("--") and entitiesfiletype == ".def":
                        def_format = 2

                    if def_format == 2:
                        if line.startswith('keys:') or line.startswith('flags:') or line.startswith('none'):
                            line = input.readline()

                    if def_format == 2:
                        if line.startswith('/*QUAKED') and " ? " in line and " - " in line:
                            line = line.replace("-", "x")

                    if def_format == 2:
                        if " : " in line:
                            if (line[0].isalpha() or (line[0]=="_" and line[1].isalpha())):
                                line = line.split(":", 1)
                                line[0] = line[0].replace("\"", "")
                                line[0] = line[0].strip()
                                if " OR " in line[0]:
                                    newline = line[0].split(" OR ")
                                    line[0] = newline[1]
                                    line[0] = line[0].strip()

                                line[1] = line[1].strip()
                                line[1] = line[1].replace("\"", "\'")
      #                          print line  # Do not remove, used for problem solving.
                                if len(line[0]) > 0 and (line[0][0].islower() or line[0][1].islower()):
                                    line = ("\"" + line[0] + "\" " + line[1] + "\n")
                                else:
                                    line = (line[0] + " " + line[1] + "\n")
                            else:
                                line = line.replace(" :", "", 1)
                        else:
                            pass

                    while line.find("  ") != -1:
                        line = line.replace("  ", " ")
                    if line.startswith('/******') or line.startswith('******') or line.startswith('*/'):
                        if line.startswith('/******'):
                            line = "\n******************************************************************************/\n"
                        o.write('\n')
                        specifics.write('\n')
                        break
                    if def_format == 2:
                        if line.endswith('*/\n'):
                            line = line.replace('*/\n', '\n*/\n')
                            specifics.write('\n')
                            spec = 0
                            break
                         ### chr(32)=space, chr(9)=tab, chr(10)=newline, chr(92)=\
                    line = line.replace(chr(9), ' ')  ### chr(9) is one 'tab'.

                    if line.endswith(' \n'):
                        line = line.replace(' \n','\n')

                    if line.endswith(chr(92) + '\n'):
                        line = line.replace(chr(92),"")

                    if line.startswith("set \"message\""):
                        line = line.replace("set \"message\"", "\"message\" set")

                    if line.startswith("If \""):
                        line = line.replace("If \"", "if \"")

                    if line.startswith("if \"") and line[4].islower() is True:
                        line = line.replace("if \"", "\"")
                        line = line.replace("\" is set", "\" if set")

                    line = line.lstrip(chr(32))
                    line = line.lstrip(chr(9))

                    if line.startswith("\"") and line[1].islower() is True:
                        line = line.replace("\"", "'")
                        line = line.replace("'", "\"", 2)
                        while line.find("  ") != -1:
                            line = line.replace("  ", " ")
                        spec = 1
                    else:
                        if def_format == 2:
                            if len(line) >= 2 and line[1] == "_":
                                pass
                        else:
                            line = line.replace("\"", "'")

                    if line.startswith('/*QUAKED'):
                        words = line.replace('(', ' ')
                        words = words.split()
                        specifics.write('ENTITY\n')
                        specifics.write(words[1] + '\n')
                        spec = 0

                    if spec == 1:
                        if line == '\n':
                            spec = 0
                        else:
                            while line.find("  ") != -1:
                                line = line.replace("  ", " ")
                            if def_format == 2:
                                if line.startswith("\""):
                                    specifics.write(line)
                            else:
                                specifics.write(line)

                    if def_format == 2:
                        if line.startswith("--") or line.startswith("("):
                            pass
                        else:
                            if line.startswith("\""):
                                if line[2].islower() is True:
                                    line = line.replace("\"", "'")
                                    line = line.replace("'", "\"", 2)
                                else:
                                    line = line.replace("\"", "")
                            o.write(line)
                    else:
                        o.write(line)
                    line = input.readline()
      #              linecount = linecount + 1  # Do not remove, used for problem solving.

                if line.startswith('*/'):
                    line = "\n******************************************************************************/\n"
                if def_format == 2:
                    if not line.startswith("\"") and "\"" in line:
                        line = line.replace("\"", "")
                o.write(line)
                o.write('\n')


    ### This section handles all the files in the main "files to check" folder, FIRST.
    for name in names:
        if name.endswith(entitiesfiletype) and name != OutPutList:   ### Checks if this is a file name or a folder name.
            input = open(os.path.join(dirname, name))
            HandleInput(input)


    ### This section handles all the files in the SUB-FOLDERS, starting with the 1st sub-folder.
    for name in names:
        if name.endswith(entitiesfiletype) or name.find(".") != -1:   ### Checks if this is a file name or a folder name
            pass
        else:
            foldername = dirname + "\\" + name
            try:
                filenames = os.listdir(foldername)
            except:
                continue
            for name in filenames:
                if name.endswith(entitiesfiletype) and name != OutPutList:
                    input = open(os.path.join(foldername, name))
                    HandleInput(input)

    o.close()
    specifics.close()

    import quarkx
    import entdef2qrk
    filepath = (QuArKpath + '\\' + gamename + '\\' + OutPutList)
    file = entdef2qrk.makeqrk(root, filepath, filepath, 1)
    if file is None:
        WorkDirectory = (QuArKpath + '\\' + gamename)
        WorkDirectory = WorkDirectory.replace("\\", "/")
        os.remove(WorkDirectory + '/' + gamename + 'Entities' + '.def') # Deletes this temp file.
        os.remove(WorkDirectory + '/' + gamename + 'Entities' + '.spf') # Deletes this temp file.
    else:
        savepath = (QuArKpath + '\\' + gamename + '\\' + file.name)
        file.savefile(savepath, 1)
        import AddSpecificsList
        AddSpecificsList.AddSpecifics(QuArKpath, gamename, gamefileslocation, gamepakfiletype,
                                      modelfiletype, soundfiletype, musicfiletype, WriteCommonSpecifics, UseCommonSpecifics,
                                      WriteModelBrowser, UseModelBrowser, UseDefaultModelHint, ModelHint, WriteSoundBrowser,
                                      UseSoundBrowser, UseDefaultSoundHint, SoundHint, WriteMusicBrowser, UseMusicBrowser,
                                      UseDefaultMusicHint, MusicHint, UseColorPicker)
    
#
#$Log: ConvertToolQ3typeEnts.py,v $
#Revision 1.4  2010/08/19 08:04:27  cdunde
#Some small fixes for the Conversion Tool system.
#
#Revision 1.3  2008/04/23 20:22:27  cdunde
#Minor improvements.
#
#Revision 1.2  2008/04/04 23:20:48  cdunde
#To add another read file format.
#
#Revision 1.1  2008/04/04 20:19:29  cdunde
#Added a new Conversion Tools for making game support QuArK .qrk files.
#
#
