"""   QuArK  -  Quake Army Knife

AddShaderList.py - Makes the GameShaders.qrk list of Shaders by folder to use as a QuArK addon game file.
            - cdunde March 31, 2008
            - This file is used by the QuArK ConvertionTool on the QuArK Explorer main Files menu.
            - The completed file will be created in the game's folder in QuArK's main folder.
            - The game's "shaders", "scripts" or "materials" folder (with its sub-folders) must be extracted.
            - This code will process files in the main "shaders" folder and all sub-folders on down.
"""

#
#$Header: /cvsroot/quark/runtime/plugins/AddShaderList.py,v 1.9 2008/06/25 14:32:33 danielpharos Exp $
#

#
#$Log: AddShaderList.py,v $
#Revision 1.9  2008/06/25 14:32:33  danielpharos
#Change to ASCII file property
#
#Revision 1.7  2008/04/16 22:25:22  cdunde
#Updated processing for Quake 4 type shaders.
#
#Revision 1.6  2008/04/11 18:33:20  cdunde
#Changed code to try to adapt to proper version writing.
#
#Revision 1.5  2008/04/06 06:47:42  cdunde
#Added file back without version control to stop overwriting of internal code.
#
#Revision 1.4  2008/04/06 06:46:51  cdunde
#Trying to remove file from version control to get into cvs
#system without overwriting internal file code.
#
#Revision 1.3  2008/04/04 20:46:46  cdunde
#Are you kidding me 8-\
#
#Revision 1.2  2008/04/04 20:42:52  cdunde
#To try and fix their system over writing internal code for logging....nice!
#
#Revision 1.1  2008/04/04 20:19:29  cdunde
#Added a new Conversion Tools for making game support QuArK .qrk files.
#
#

###Globals
skip = []
text = "" # This is a temporary place in memory to copy an existing file's data to and
          # add to it, or write new entity data to for making an new file later.

import os, os.path
from ConvertToolGet_tokens import *

def AddShaders(QuArKpath, gamename, gamefileslocation, shadersfolder, shadersfiletype):
    global skip, text
    WorkDirectory = (QuArKpath + '\\' + gamename)  ### Sets work folder (where .qrk file will be) Path here.
    ### Sets the shader's file folder name here.
    filesfoldername = shadersfolder.split('\\')
    filesfoldername = filesfoldername[len(filesfoldername)-1]
    whatkind = filesfoldername.capitalize()  ### Sets what they are called here.
    ### Sets the game FOLDER name here (where the games .pak or "shaders" folder is).
    GameFolder = gamefileslocation.split('\\')
    GameFolder = GameFolder[len(GameFolder)-1]

    ### Write the includes list:
    def listincludes(basefolder, foldername, filenames):

        def shortName(s):
            result = s
            q = s.find(".")
            if q != -1:
                result = s[:q]
            return result

        nested = 0
        material_name = "undefined"
        kount = 0

        ### Does a name removal for files that do not have any "texture/" item in them, nothing we can use.
        tempnameslist = filenames
        for name in filenames:
            if not name.endswith(shadersfiletype):
                continue
            tokens = getTokens(foldername + "\\" + name, 1)
            iToken = iter(tokens)
            tokenType, tokenValue = iToken.next()
            hastextures = 0
            while tokenType != T_EOF:
                if (tokenType == T_SPECIAL) and (tokenValue == "{"):
                    # this is the start of a new material
                    nested = 1
                    kount += 1
                    while nested > 0:
                        tokenType, tokenValue = iToken.next()
                        if tokenType == T_EOF:
                            break
                        if (tokenType == T_SPECIAL) and (tokenValue == "{"):
                            nested += 1
                        elif (tokenType == T_SPECIAL) and (tokenValue == "}"):
                            nested -= 1

                    # for now, ignore anything that does not start with 'textures/'
                    if material_name.startswith('textures/'):
                        hastextures = 1
                        break

                if tokenType == T_IDENTIFIER:
                    material_name = tokenValue

                tokenType, tokenValue = iToken.next()

            if hastextures == 0:
                tempnameslist.remove(name)
        filenames = tempnameslist

        ### Calculates the longest shader filename so we can pad the incl lines to make it look nice.
        longestName = 0
        for name in filenames:
            if not name.endswith(shadersfiletype):
                continue
            if len(name) > longestName:
                longestName = len(name)
        longestName += 14

        ### Writes the 'include' part for each folder that has a shader file with a 'textures/' name in it.
        for name in filenames:
            if not name.endswith(shadersfiletype):
                continue
            if shortName(name) in skip:
                continue
            s = 't_' + GameFolder + filesfoldername + '_%s:incl' % shortName(name)
            while len(s) < longestName:
                s += ' '
            ### Subfolder's name gets added here.
            folder = foldername.replace(shadersfolder, "")
            if folder != "":
                folder = folder.replace("\\", "")
                folder = folder + '/'
            o.write(('    %s = { a="' + GameFolder + '" b="' + folder + name + '" }\n') % (s))

    def listfiles(basefolder, foldername, filenames):
        global skip, text

        def shortName(s):
            result = s
            q = s.find(".")
            if q != -1:
                result = s[:q]
            return result

        nested = 0
        material_name = "undefined"
        kount = 0

        ### Writes the shader files list now for each folder.
        for name in filenames:
            hasitem = 0
            tempname = [] # Holds the shader names in memory for sorting by 'filename'.txlist later.
            templist = {} # Holds the shader data needed for writing later, used by 'tempname'.
            if not name.endswith(shadersfiletype):
                continue
            tokens = getTokens(foldername + "\\" + name, 1)
            iToken = iter(tokens)
            tokenType, tokenValue = iToken.next()
            while tokenType != T_EOF:
                if (tokenType == T_SPECIAL) and (tokenValue == "{"):
                    # this is the start of a new material
                    nested = 1
                    kount += 1
                    while nested > 0:
                        tokenType, tokenValue = iToken.next()
                        if tokenType == T_EOF:
                            break
                        if (tokenType == T_SPECIAL) and (tokenValue == "{"):
                            nested += 1
                        elif (tokenType == T_SPECIAL) and (tokenValue == "}"):
                            nested -= 1

                    # For now, ignore anything that does not start with 'textures/'
                    # and use its include statement created above.
                    if material_name.startswith('textures/'):
                        if hasitem == 0:
                            text = text + ('      %s.txlist =\n') % shortName(name)
                            text = text + '      {\n'
                            hasitem = 1
                        tempname = tempname + [material_name[9:]]
                        templist[material_name[9:]] = ('        %s.wl    = { t_' + GameFolder + filesfoldername + '_%s=! }\n') % (material_name[9:], shortName(name))
                # Quake 4 (a Doom3 based game) uses 'guide' as a keyword.
                # If found does not use its include statment created above,
                # it uses what it finds in the input file for the shader texture instead.
                if tokenValue.startswith('guide'):
                    tokenType, tokenValue = iToken.next()
                    if tokenValue.startswith('textures/'):
                        if hasitem == 0:
                            text = text + ('      %s.txlist =\n') % shortName(name)
                            text = text + '      {\n'
                            hasitem = 1
                        tokenValue = tokenValue.replace('textures/', "")
                        tempname = tempname + [tokenValue]
                        templist[tokenValue] = ('        %s.wl    = { a="' + GameFolder + '" n="%s_d" }\n') % (tokenValue, tokenValue)

                if tokenType == T_IDENTIFIER:
                    material_name = tokenValue

                tokenType, tokenValue = iToken.next()

            if hasitem != 0:
                tempname.sort()
                for name in tempname:
                    text = text + templist[name]
                text = text + '      }\n'
            else:
                skip = skip + [shortName(name)]

    filenames = []

    o = open(WorkDirectory + "\\" + gamename + whatkind + ".qrk", "w")

    ### Writes the new .qrk file header.
    o.write("QQRKSRC1\n")
    o.write("// " + gamename + " " + whatkind + " file for Quark\n")
    o.write("\n")
    o.write("//$" + "Header: Exp $" + "\n")
    o.write("// ----------- REVISION HISTORY ------------\n")
    o.write("//$" + "Log: " + gamename + whatkind + ".qrk,v $" + "\n")
    o.write("//\n")

    ### Writes the setup part for the Texture Browser folders and needed path "include".
    o.write("\n")
    o.write("{\n")
    o.write("  QuArKProtected = \"1\"\n")
    o.write("  Description = \"" + gamename + " " + whatkind + "\"\n")
    o.write("\n")
    o.write("  " + whatkind + ".qtx =\n")
    o.write("  {\n")
    o.write("    Toolbox = \"Texture Browser...\"\n")
    o.write("    Root = \"" + gamename + " " + whatkind + ".qtxfolder\"\n")
    o.write("\n")

    ### Writes all the texture sub-folders textures list here.
    os.path.walk(shadersfolder, listfiles, filenames)
    os.path.walk(shadersfolder, listincludes, filenames)
    o.write('\n')
    o.write('    ' + gamename + ' ' + whatkind + '.qtxfolder =\n')
    o.write('    {\n')
    o.write(text)
    skip = []
    text = ""

    ### Finishes writing the closing part of the new .qrk file here and closes it.
    o.write('    }\n')
    o.write('  }\n')
    o.write('}\n')
    o.close()

