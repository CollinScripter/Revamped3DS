"""   QuArK  -  Quake Army Knife

 AddTextureList.py - Makes a games .qrk list of Textures by folder to use as a QuArK addon game file.
            - cdunde Feb. 25, 2008
            - This file is used by the QuArK ConvertionTool on the QuArK Explorer main Files menu.
            - The completed file will be created in the game's folder in QuArK's main folder.
            - The game's "textures" folder (with its sub-folders) must be extracted.
            - This code will process files in the main "textures" folder and all sub-folders on down.
"""

#
#$Header: /cvsroot/quark/runtime/plugins/AddTextureList.py,v 1.8 2008/06/25 14:32:32 danielpharos Exp $
#

#
#$Log: AddTextureList.py,v $
#Revision 1.8  2008/06/25 14:32:32  danielpharos
#Change to ASCII file property
#
#Revision 1.6  2008/04/11 18:33:20  cdunde
#Changed code to try to adapt to proper version writing.
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

def AddTextures(QuArKpath, gamename, gamefileslocation, texturesfolder, texturesfiletype):
    WorkDirectory = (QuArKpath + '\\' + gamename)  ### Sets work folder (where .qrk file will be) Path here.
    GameFolder = gamefileslocation.split('\\')
    GameFolder = GameFolder[len(GameFolder)-1]

    TexFileTypeList = texturesfiletype
    TexFileTypeList = TexFileTypeList.replace(" ","")
    TexFileTypeList = TexFileTypeList.replace("*","")
    TexFileTypeList = TexFileTypeList.split(";")

    ### Write the textures list:
    def listfiles(basefolder, foldername, filenames):
        count = 0
        for name in filenames:
            for filetype in TexFileTypeList:
                if filetype.lower() in name.lower():
                    if count == 0:
                        if foldername == texturesfolder:
                            mainfoldername = texturesfolder.replace(gamefileslocation + "\\", "")
                            mainfoldername = mainfoldername.replace("\\", "/")
                            o.write("      " + mainfoldername + ".txlist =\n")
                        else:
                            foldername = foldername.replace(texturesfolder + "\\", "")
                            foldername = foldername.replace("\\", "/")
                            o.write("      " + foldername + ".txlist =\n")
                        o.write("      {\n")
                        count = 1
                    shortname = name.rsplit(".", 1)  ### This removes the file type suffix.
                    if foldername == texturesfolder:
                        o.write("        " + shortname[0] + ".wl")
                        line = len("        " + shortname[0] + ".wl")
                    else:
                        o.write("        " + foldername + "/" + shortname[0] + ".wl")
                        line = len("        " + foldername + "/" + shortname[0] + ".wl")
                    while line < 51:
                        o.write(" ")
                        line = line + 1
                    o.write("= { t_" + GameFolder + "=! }\n")
        if count == 1:
            o.write("      }\n")

    filenames = []

    o = open(WorkDirectory + "\\" + gamename + "Textures.qrk", "w")

    ### Writes the new .qrk file header.
    o.write("QQRKSRC1\n")
    o.write("// " + gamename + " Textures file for Quark\n")
    o.write("\n")
    o.write("//$" + "Header: Exp $" + "\n")
    o.write("// ----------- REVISION HISTORY ------------\n")
    o.write("//$" + "Log: " + gamename + "Textures.qrk,v $" + "\n")
    o.write("//\n")

    ### Writes the setup part for the Texture Browser folders and needed path "include".
    o.write("\n")
    o.write("{\n")
    o.write("  QuArKProtected = \"1\"\n")
    o.write("  Description = \"" + gamename + " Textures\"\n")
    o.write("\n")
    o.write("  Textures.qtx =\n")
    o.write("  {\n")
    o.write("    Toolbox = \"Texture Browser...\"\n")
    o.write("    Root = \"" + gamename + " Textures.qtxfolder\"\n")
    o.write("\n")
    o.write("    t_" + GameFolder + ":incl =      { a = \"" + GameFolder + "\" }\n")
    o.write("\n")
    o.write("    " + gamename + " Textures.qtxfolder =\n")
    o.write("    {\n")

    ### Writes all the texture sub-folders textures list here.
    os.path.walk(texturesfolder, listfiles, filenames)

    ### Finishes writing the closing part of the new .qrk file here and closes it.
    o.write("    }\n")
    o.write("  }\n")
    o.write("}\n")
    o.close()
