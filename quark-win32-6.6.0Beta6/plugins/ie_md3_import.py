# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Quake3 .md3 model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md3_import.py,v 1.27 2012/10/01 20:28:57 cdunde Exp $


Info = {
   "plug-in":       "ie_md3_importer",
   "desc":          "This script imports .md3 model files, textures, and animations into QuArK for editing. Original code from Blender, md3import.py version 0.7, author - Bob Holcomb.",
   "date":          "Aug. 8 2009",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 3" }

import os, struct, math
import quarkx
from quarkpy.qutils import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
SS_MODEL = 3
logging = 0
importername = "ie_md3_import.py"
textlog = "md3_ie_log.txt"
editor = None

# Matrix for QuArK.
### Taken from source\prog\qmatrices.pas lines 139-141
def vector_by_matrix(p, m):
    x = p[0] * m[0][0] + p[1] * m[0][1] + p[2] * m[0][2]
    y = p[0] * m[1][0] + p[1] * m[1][1] + p[2] * m[1][2]
    z = p[0] * m[2][0] + p[1] * m[2][1] + p[2] * m[2][2]
    return [x, y, z]

# Global .md3 file limits and values.
MAX_QPATH = 64
MD3_XYZ_SCALE = (1.0 / 64.0)

def asciiz(s):
    n = 0
    while( n < MAX_QPATH and ord(s[n]) != 0):
        n = n + 1
    return s[0:n]

# copied from PhaethonH <phaethon@linux.ucla.edu> md3.py
def Decode(latlng):
    lat = (latlng >> 8) & 0xFF;
    lng = (latlng) & 0xFF;
    lat *= math.pi / 128;
    lng *= math.pi / 128;
    x = math.cos(lat) * math.sin(lng)
    y = math.sin(lat) * math.sin(lng)
    z =                 math.cos(lng)
    retval = [ x, y, z ]
    return retval


class md3Vert(object):
    __slots__ = 'xyz', 'normal', 'binaryFormat'

    binaryFormat = "<3hh" # Each h = 2 bytes.

    def __init__(self):
        self.xyz = [0, 0, 0]
        self.normal = 0

    def Load(self, file):
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.xyz[0] = data[0] * MD3_XYZ_SCALE
        self.xyz[1] = data[1] * MD3_XYZ_SCALE
        self.xyz[2] = data[2] * MD3_XYZ_SCALE
        self.normal = data[3]
        return self


class md3TexCoord(object):
    __slots__ = 'u', 'v', 'binaryFormat'

    binaryFormat = "<2f" # Each f = 4 bytes.

    def __init__(self):
        self.u = 0.0
        self.v = 0.0

    def Load(self, file):
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.u = data[0]
        self.v = data[1]
        return self


class md3Triangle(object):
    __slots__ = 'indexes', 'binaryFormat'

    binaryFormat = "<3i" # Each i = 4 bytes.

    def __init__(self):
        self.indexes = [ 0, 0, 0 ]

    def Load(self, file):
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.indexes[0] = data[0]
        self.indexes[1] = data[1]
        self.indexes[2] = data[2]
        return self


class md3Shader(object):
    __slots__ = 'name', 'index', 'binaryFormat'

    binaryFormat = "<%dsi" % MAX_QPATH  # name, then 1 int

    def __init__(self):
        self.name = ""
        self.index = 0

    def Load(self, file):
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.name = asciiz(data[0])
        self.index = data[1]
        return self


class md3Surface(object):
    __slots__ = \
        'ident', 'name', 'flags', 'numFrames', 'numShaders', 'numVerts', 'numTriangles', \
        'ofsTriangles', 'ofsShaders', 'ofsUV', 'ofsVerts', 'ofsEnd', 'shaders', 'triangles', 'uv', \
        'verts', 'binaryFormat'

    binaryFormat = "<4s%ds10i" % MAX_QPATH  # 1 int, name, then 10 ints * 4 bytes per int

    def __init__(self):
        self.ident = ""
        self.name = ""
        self.flags = 0
        self.numFrames = 0
        self.numShaders = 0
        self.numVerts = 0
        self.numTriangles = 0
        self.ofsTriangles = 0
        self.ofsShaders = 0
        self.ofsUV = 0
        self.ofsVerts = 0
        self.ofsEnd = 0
        self.shaders = []
        self.triangles = []
        self.uv = []
        self.verts = []

    def Load(self, file):
        # where are we in the file (for calculating real offsets)
        ofsBegin = file.tell()
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.ident = data[0]
        self.name = asciiz(data[1])
        self.flags = data[2]
        self.numFrames = data[3]
        self.numShaders = data[4]
        self.numVerts = data[5]
        self.numTriangles = data[6]
        self.ofsTriangles = data[7]
        self.ofsShaders = data[8]
        self.ofsUV = data[9]
        self.ofsVerts = data[10]
        self.ofsEnd = data[11]

        # load the shader info
        file.seek(ofsBegin + self.ofsShaders, 0)
        for i in xrange(self.numShaders):
            self.shaders.append(md3Shader())
            self.shaders[i].Load(file)

        # load the tri info
        file.seek(ofsBegin + self.ofsTriangles, 0)
        for i in xrange(self.numTriangles):
            self.triangles.append(md3Triangle())
            self.triangles[i].Load(file)

        # load the uv info
        file.seek(ofsBegin + self.ofsUV, 0)
        for i in xrange(self.numVerts):
            self.uv.append(md3TexCoord())
            self.uv[i].Load(file)

        # load the verts info
        file.seek(ofsBegin + self.ofsVerts, 0)
        for i in xrange(self.numFrames):
            for j in xrange(self.numVerts):
                self.verts.append(md3Vert())
                #i*self.numVerts+j=where in the surface vertex list the vert position for this frame is
                self.verts[(i * self.numVerts) + j].Load(file)

        # go to the end of this structure
        file.seek(ofsBegin+self.ofsEnd, 0)

        return self


class md3Tag(object):
    __slots__ = 'name', 'origin', 'axis', 'binaryFormat'

    binaryFormat="<%ds3f9f" % MAX_QPATH  # name, then 12 ints * 4 bytes per int

    def __init__(self):
        self.name = ""
        self.origin = [0.0, 0.0, 0.0]
        self.axis = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]

    def Load(self, file):
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.name = asciiz(data[0])
        self.origin[0] = data[1]
        self.origin[1] = data[2]
        self.origin[2] = data[3]
        self.axis[0] = data[4]
        self.axis[1] = data[5]
        self.axis[2] = data[6]
        self.axis[3] = data[7]
        self.axis[4] = data[8]
        self.axis[5] = data[9]
        self.axis[6] = data[10]
        self.axis[7] = data[11]
        self.axis[8] = data[12]
        return self


class md3Frame(object):
    __slots__ = 'mins', 'maxs', 'localOrigin', 'radius', 'name', 'binaryFormat'

    binaryFormat="<3f3f3ff16s" # 10 f * 4 bytes per f + 16 s * 1 byte per s

    def __init__(self):
        self.mins = [0, 0, 0]
        self.maxs = [0, 0, 0]
        self.localOrigin = [0, 0, 0]
        self.radius = 0.0
        self.name = ""

    def Load(self, file):
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.mins[0] = data[0]
        self.mins[1] = data[1]
        self.mins[2] = data[2]
        self.maxs[0] = data[3]
        self.maxs[1] = data[4]
        self.maxs[2] = data[5]
        self.localOrigin[0] = data[6]
        self.localOrigin[1] = data[7]
        self.localOrigin[2] = data[8]
        self.radius = data[9]
        self.name = asciiz(data[10])
        return self


class md3Object(object):
    __slots__ = \
        'ident', 'version', 'name', 'flags', 'numFrames', 'numTags', 'numSurfaces', 'numSkins', \
        'ofsFrames', 'ofsTags', 'ofsSurfaces', 'ofsEnd', 'frames', 'tags', 'surfaces', 'binaryFormat'

    binaryFormat="<4si%ds9i" % MAX_QPATH  # little-endian (<), 4 char[] string, 1 int, size of string 'name' max 64 char[], integers (9i)

    def __init__(self):
        self.ident = ""
        self.version = 0
        self.name = ""
        self.flags = 0
        self.numFrames = 0
        self.numTags = 0
        self.numSurfaces = 0
        self.numSkins = 0
        self.ofsFrames = 0
        self.ofsTags = 0
        self.ofsSurfaces = 0
        self.ofsEnd = 0
        self.frames = []
        self.tags = []
        self.surfaces = []

    def Load(self, file):
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)

        self.ident = data[0]
        self.version = data[1]

        if(self.ident != "IDP3" or self.version != 15):
            quarkx.beep() # Makes the computer "Beep" once if a file is not valid.
            quarkx.msgbox("Not a valid MD3 file\n\nIdent: " + self.ident + "\nVersion: " + self.version, MT_ERROR, MB_OK)
            editor = None   #Reset the global again
            return

        self.name = asciiz(data[2])
        self.flags = data[3]
        self.numFrames = data[4]
        self.numTags = data[5]
        self.numSurfaces = data[6]
        self.numSkins = data[7]
        self.ofsFrames = data[8]
        self.ofsTags = data[9]
        self.ofsSurfaces = data[10]
        self.ofsEnd = data[11]

        # load the frame info
        file.seek(self.ofsFrames, 0)
        for i in xrange(self.numFrames):
            self.frames.append(md3Frame())
            self.frames[i].Load(file)

        # load the tags info
        file.seek(self.ofsTags, 0)
        for i in xrange(self.numFrames):
            for j in xrange(self.numTags):
                tag = md3Tag()
                tag.Load(file)
                self.tags.append(tag)

        # load the surface info
        file.seek(self.ofsSurfaces, 0)
        for i in xrange(self.numSurfaces):
            self.surfaces.append(md3Surface())
            self.surfaces[i].Load(file)
        return self


def Import(basepath, filename):
    global tobj, logging, importername, textlog

    logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

### This area is where we make the different elements of a QuArK Component, for each Component.
    # First we check for any other "Import Component"s,
    # if so we name the first component 1 more then the largest number
    # and increase each following component by 1.
    CompNbr = "None"
    comparenbr = 0
    for item in editor.Root.dictitems:
        if editor.Root.dictitems[item].shortname.startswith('Import Component'):
            getnbr = editor.Root.dictitems[item].shortname
            getnbr = getnbr.replace('Import Component', '')
            if getnbr == "":
               nbr = 0
            else:
                nbr = int(getnbr)
            if nbr > comparenbr:
                comparenbr = nbr
            nbr = comparenbr + 1
            CompNbr = nbr
    if CompNbr != "None":
        pass
    else:
        CompNbr = 1

    ComponentList = []
    message = ""

    ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.

    # FullPathName is the full path and the full file name being imported with forward slashes.
    FullPathName = filename.replace("\\", "/")
    # FolderPath is the full path to the model's folder w/o slash at end.
    FolderPath = FullPathName.rsplit("/", 1)
    FolderPath, ModelName = FolderPath[0], FolderPath[1]
    # ModelFolder is just the .md3 model file's FOLDER name without any path, slashes or the ".md3" file name.
    # Probably best to use ModelFolder to keep all the tags and bones (if any) together for a particular modle.
    ModelFolder = FolderPath.rsplit("/", 1)[1]
    # BasePath is the full path to and the name of the game folder or any folder that has the "models" and "scripts" (shader or material) folders in it, w/o slash at end.
    BasePath = FolderPath.rsplit("/models/", 1)[0]
    # ModelsPath is just the path starting with the "models/" FOLDER on without the ".md3" file name or slash at the end of the path.
    ModelsPath = FolderPath.replace(BasePath+"/", "")
    # ModelName is just the .md3 model file name without any path or the ".md3" type.
    ModelName = ModelName.rsplit(".", 1)[0]
    # PlayerModelName is just the .md3 player model file name, for special code handling, without any path or the ".md3" type.
    PlayerModelName = "None"
    if ModelsPath.find("players/") != -1:
        PlayerModelName = ModelName.split("_")[0]

    # read the file in
    file = open(filename,"rb")
    md3 = md3Object()
    md3.Load(file)
    file.close()

    # To get to current torso tag frames that will be needed later if they exist in the editor already.
    old_torso_tag_frames = None
    if ModelName.find("upper") != -1:
        editor_dictitems = editor.Root.dictitems
        for t in xrange(md3.numTags):
            cktag = md3.tags[t]
            if cktag.name.find("torso") != -1:
                tag_name = ModelFolder + '_' + cktag.name + ':tag'
                if editor_dictitems['Misc:mg'].dictitems.has_key(tag_name):
                    old_torso_tag_frames = editor_dictitems['Misc:mg'].dictitems[tag_name].subitems
    if quarkx.setupsubset(SS_MODEL, "Options")['IEMaxTagFrames'] != "1":
        old_torso_tag_frames = None

    for k in xrange(md3.numSurfaces):
        surface = md3.surfaces[k]
        ### Create the Frames:fg group and each "name:mf" frame.
        framesgroup = quarkx.newobj('Frames:fg')
        if surface.numFrames > 1 : # Make the animation frames if they exist for this model.
            for i in xrange(surface.numFrames):
                frame = quarkx.newobj('Frame ' + str(i+1) + ':mf')
                mesh = ()
                for j in xrange(surface.numVerts):
                    # This is a new vertex, so we add it to the frame['Vertices'] mesh
                    x,y,z = surface.verts[(i * surface.numVerts) + j].xyz
                    mesh = mesh + (x,y,z)
                frame['Vertices'] = mesh
                if i == 0:
                    baseframe = frame.copy()
                    baseframe.shortname = 'baseframe'
                framesgroup.appenditem(frame)
                if i == surface.numFrames-1:
                    if old_torso_tag_frames is not None:
                        for old_frame in range(i+1, len(old_torso_tag_frames)):
                            if old_frame == len(old_torso_tag_frames)-1:
                                framesgroup.appenditem(baseframe)
                            else:
                                extra_frame = frame.copy()
                                extra_frame.shortname = 'Frame ' + str(old_frame+1)
                                framesgroup.appenditem(extra_frame)
                    else:
                        framesgroup.appenditem(baseframe)
        else: # Make a baseframe for this model if no animation frames.
            verts = []
            verts.extend( [surface.verts[i].xyz for i in xrange(surface.numVerts)] )
            frame = quarkx.newobj('baseframe:mf')
            mesh = ()
            for vert in verts:
                # This is a new vertex, so we add it to the frame['Vertices'] mesh
                x,y,z = vert
                mesh = mesh + (x,y,z)
            frame['Vertices'] = mesh
            framesgroup.appenditem(frame)

        # Create the "Skins:sg" group.
        ImageTypes = [".tga", ".jpg", ".bmp", ".png", ".dds"]
        skinsize = (0, 0)
        skingroup = quarkx.newobj('Skins:sg')
        skingroup['type'] = chr(2)
        mesh_shader = None

        def check4skin(skin, skingroup=skingroup):
            checkname = skin.name.rsplit(".", 1)[0]
            for keyname in skingroup.dictitems.keys():
                for type in ImageTypes:
                    if checkname + type == keyname:
                        return keyname
            return None

        shaderlist = []
        for i in xrange(surface.numShaders):
            # This is for removing duplicated shader names.
            if surface.shaders[i].name in shaderlist:
                continue
            shaderlist = shaderlist + [surface.shaders[i].name]
            # Now it checks if the model has any shader textures specified with it
            # or any other textures if it does not use a shader file and trys to load those.
            foundshader = foundtexture = foundimage = imagefile = None
            shader_file = shader_name = shader_keyword = None

            skinfiles = os.listdir(FolderPath) # Usually, only "player" models use ".skin" type files, like a shader. So we check for that.
            # If they exist we load the defalut.skin first, then all others.
            for file in skinfiles:
                if file == PlayerModelName + "_default.skin":
                    #read the file in
                    read_skin_file=open(FolderPath+"/"+file,"r")
                    skinlines=read_skin_file.readlines()
                    read_skin_file.close()
                    for line in skinlines:
                        line = line.split(",")
                        if len(line) == 2 and (PlayerModelName.find(line[0]) != -1 or surface.name.find(line[0]) != -1):
                            for type in ImageTypes:
                                if line[1].lower().find(type) != -1:
                                    line = line[1].rsplit(".", 1)[0]
                                    line = line.strip()
                                    foundtexture = line + type
                                    if os.path.isfile(BasePath + "/" + foundtexture):
                                        foundimage = BasePath + "/" + foundtexture
                                        skin = quarkx.newobj(foundtexture)
                                    else:
                                        tryskin = foundtexture.rsplit(".", 1)[0]
                                        for type in ImageTypes:
                                            if os.path.isfile(BasePath + "/" + tryskin + type):
                                                foundimage = BasePath + "/" + tryskin + type
                                                skin = quarkx.newobj(tryskin + type)
                                                break
                                    if foundimage is not None:
                                        image = quarkx.openfileobj(foundimage)
                                        name = check4skin(skin)
                                        if name is None:
                                            skin['Image1'] = image.dictspec['Image1']
                                            skin['Size'] = image.dictspec['Size']
                                            skin['shader_keyword'] = shader_keyword
                                            skingroup.appenditem(skin)
                                            if skin['Size'][0] > skinsize[0] and skin['Size'][1] > skinsize[1]:
                                                skinsize = skin['Size']
                                            break
                                    else:
                                        message = message + "Component: " + ModelFolder + "_" + surface.name + "\r\nuses the file:\r\n    " + FolderPath+"/"+file + "\r\nBut an image:\r\n    " + foundtexture + "\r\nit uses in that file does not exist in that folder or the folder has not been extracted.\r\nLocate image file and place in that extracted folder.\r\n\r\n"
                    break
            # If they exist we load all others.
            for file in skinfiles:
                if file == PlayerModelName + "_default.skin":
                    continue
                elif file.startswith(PlayerModelName) and file.endswith(".skin"):
                    #read the file in
                    read_skin_file=open(FolderPath+"/"+file,"r")
                    skinlines=read_skin_file.readlines()
                    read_skin_file.close()
                    for line in skinlines:
                        line = line.split(",")
                        if len(line) == 2 and (PlayerModelName.find(line[0]) != -1 or surface.name.find(line[0]) != -1):
                            for type in ImageTypes:
                                if line[1].find(type) != -1:
                                    line = line[1].rsplit(".", 1)[0]
                                    line = line.strip()
                                    foundtexture = line + type
                                    if os.path.isfile(BasePath + "/" + foundtexture):
                                        foundimage = BasePath + "/" + foundtexture
                                        skin = quarkx.newobj(foundtexture)
                                    else:
                                        tryskin = foundtexture.rsplit(".", 1)[0]
                                        for type in ImageTypes:
                                            if os.path.isfile(BasePath + "/" + tryskin + type):
                                                foundimage = BasePath + "/" + tryskin + type
                                                skin = quarkx.newobj(tryskin + type)
                                                break
                                    if foundimage is not None:
                                        image = quarkx.openfileobj(foundimage)
                                        name = check4skin(skin)
                                        if name is None:
                                            skin['Image1'] = image.dictspec['Image1']
                                            skin['Size'] = image.dictspec['Size']
                                            skin['shader_keyword'] = shader_keyword
                                            skingroup.appenditem(skin)
                                            if skin['Size'][0] > skinsize[0] and skin['Size'][1] > skinsize[1]:
                                                skinsize = skin['Size']
                                            break
                                    else:
                                        message = message + "Component: " + ModelFolder + "_" + surface.name + "\r\nuses the file:\r\n    " + FolderPath+"/"+file + "\r\nBut an image:\r\n    " + foundtexture + "\r\nit uses in that file does not exist in that folder.\r\nLocate image file and place in that folder.\r\n\r\n"
            imagefile = foundimage

            # Now we look for this component's texture directly if still no image but we have a "surface.shader.name".
            if foundimage is None:
                if surface.shaders[i].name != "":

                    foundtexture = surface.shaders[i].name.rsplit(".", 1)[0]
                    for type in ImageTypes:
                        findtexture = foundtexture + type
                        if os.path.isfile(BasePath + "/" + findtexture):
                            foundimage = BasePath + "/" + findtexture
                            skinname = foundtexture = findtexture
                            skin = quarkx.newobj(skinname)
                            image = quarkx.openfileobj(foundimage)
                            name = check4skin(skin)
                            if name is None:
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                skin['shader_keyword'] = shader_keyword
                                skingroup.appenditem(skin)
                                if skin['Size'][0] > skinsize[0] and skin['Size'][1] > skinsize[1]:
                                    skinsize = skin['Size']
                                break
                    # If still no image we try the model's folder.
                    if foundimage is None:
                        for type in ImageTypes:
                            findtexture = foundtexture + type
                            if os.path.isfile(BasePath + "/" + ModelsPath + "/" + findtexture):
                                foundimage = BasePath + "/" + ModelsPath + "/" + findtexture
                                skinname = foundtexture = findtexture
                                skin = quarkx.newobj(skinname)
                                image = quarkx.openfileobj(foundimage)
                                name = check4skin(skin)
                                if name is None:
                                    skin['Image1'] = image.dictspec['Image1']
                                    skin['Size'] = image.dictspec['Size']
                                    skin['shader_keyword'] = shader_keyword
                                    skingroup.appenditem(skin)
                                    if skin['Size'][0] > skinsize[0] and skin['Size'][1] > skinsize[1]:
                                        skinsize = skin['Size']
                                    break
                imagefile = foundimage
                foundimage = None

            # Now we look for any shaders for this component'.
            if foundimage is None:
                if surface.shaders[i].name != "":
                    shader_name = surface.shaders[i].name.rsplit(".", 1)[0]
                else:
                    shader_name = ModelsPath

                shaderspath = BasePath + "/scripts"
                try:
                    shaderfiles = os.listdir(shaderspath)
                except:
                    quarkx.msgbox("Folder Not Found!\n\nThe folder 'scripts' can not be found in the game folder:\n    " + BasePath + "\nExtract the 'scripts' folder to that location and try again.", MT_ERROR, MB_OK)
                    return
                for shaderfile in shaderfiles:
                    if shaderfile.endswith(".shader") and foundshader is None:
                        read_shader_file=open(shaderspath+"/"+shaderfile,"r")
                        shaderlines=read_shader_file.readlines()
                        read_shader_file.close()
                        left_cur_braket = 0
                        # Dec character code for space = chr(32), for tab = chr(9)
                        for line in range(len(shaderlines)):
                            # To first try to find if a specific shader exist.
                            if foundshader is None and shaderlines[line].startswith(shader_name+"\n"):
                                shaderline = shaderlines[line].replace(chr(9), "    ")
                                shaderline = shaderline.rstrip()
                                if mesh_shader is None:
                                    mesh_shader = ""
                                mesh_shader = mesh_shader + "\r\n" + shaderline + "\r\n"
                                shader_file = shaderspath + "/" + shaderfile
                                foundshader = shader_name
                                left_cur_braket = 0
                                continue
                            elif foundshader is None and shaderlines[line].find(surface.name) != -1 and (shaderlines[line].startswith("textures/") or shaderlines[line].startswith("models/")):
                                shaderline = shaderlines[line].replace(chr(9), "    ")
                                shaderline = shaderline.rstrip()
                                shader_name = shaderline
                                if mesh_shader is None:
                                    mesh_shader = ""
                                mesh_shader = mesh_shader + "\r\n" + shaderline + "\r\n"
                                shader_file = shaderspath + "/" + shaderfile
                                foundshader = shader_name
                                left_cur_braket = 0
                                continue
                            if foundshader is not None and shaderlines[line].find("{") != -1:
                                left_cur_braket = left_cur_braket + 1
                            if foundshader is not None and shaderlines[line].find("}") != -1:
                                left_cur_braket = left_cur_braket - 1
                                if left_cur_braket == 0:
                                    shaderline = shaderlines[line].replace(chr(9), "    ")
                                    shaderline = shaderline.rstrip()
                                    mesh_shader = mesh_shader + shaderline + "\r\n"
                                    break
                            if foundshader is not None:
                                shaderline = shaderlines[line].replace(chr(9), "    ")
                                shaderline = shaderline.rstrip()
                                mesh_shader = mesh_shader + shaderline + "\r\n"
                                testline = shaderlines[line].strip()
                                if testline.startswith("//"):
                                    continue
                                if shaderlines[line].find(".tga") != -1 or (shaderlines[line].find("/") != -1 and (shaderlines[line].find("models") != -1 or shaderlines[line].find("textures") != -1)):
                                    words = shaderlines[line].split()
                                    for word in words:
                                        if word.endswith(".tga"):
                                            foundtexture = word
                                            shader_keyword = words[0]
                                            skinname = foundtexture
                                            skin = quarkx.newobj(skinname)
                                            break
                                        elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")):
                                            foundtexture = word
                                            shader_keyword = words[0]
                                            skinname = foundtexture
                                            skin = quarkx.newobj(skinname)
                                            break
                                    if foundtexture is not None:
                                        foundtexture = foundtexture.rsplit(".", 1)[0]
                                        for type in ImageTypes:
                                            findtexture = foundtexture + type
                                            if os.path.isfile(BasePath + "/" + findtexture):
                                                foundimage = BasePath + "/" + findtexture
                                                image = quarkx.openfileobj(foundimage)
                                                name = check4skin(skin)
                                                if name is None:
                                                    skin['Image1'] = image.dictspec['Image1']
                                                    skin['Size'] = image.dictspec['Size']
                                                    skin['shader_keyword'] = shader_keyword
                                                    skingroup.appenditem(skin)
                                                    if skin['Size'][0] > skinsize[0] and skin['Size'][1] > skinsize[1]:
                                                        skinsize = skin['Size']
                                                    break
                                                else:
                                                    if shader_keyword is not None and (not skingroup.dictitems[name].dictspec.has_key('shader_keyword') or not skingroup.dictitems[name].dictspec['shader_keyword'] == "None"):
                                                        skingroup.dictitems[name]['shader_keyword'] = shader_keyword
                                        if foundimage is None:
                                            message = message + "Component: " + ModelFolder + "_" + surface.name + "\r\nuses the shader:\r\n    " + shader_name + "\r\nin the file:\r\n    " + shaderspath+"/"+shaderfile + "\r\nBut the image it uses in that file:\r\n    " + foundtexture + "\r\ndoes not exist in that folder or the folder has not been extracted.\r\nLocate image file and place in that extracted folder.\r\n\r\n"
                    else:
                        if foundshader is not None:
                            break

            if foundshader is None:
                if imagefile is None:
                    if surface.shaders[i].name != "":
                        tryskin = surface.shaders[i].name.rsplit(".", 1)[0]
                        tryskin = tryskin.replace("\\", "/")
                        tryskin = tryskin.rsplit("/", 1)[1]
                        for type in ImageTypes:
                            if os.path.isfile(FolderPath + "/" + tryskin + type):
                                foundimage = FolderPath + "/" + tryskin + type
                                tryskin = "models/" + FolderPath.split("/models/")[1] + "/" + tryskin
                                skin = quarkx.newobj(tryskin + type)
                                break
                        if foundimage is not None:
                            image = quarkx.openfileobj(foundimage)
                            name = check4skin(skin)
                            if name is None:
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                skin['shader_keyword'] = shader_keyword
                                skingroup.appenditem(skin)
                                if skin['Size'][0] > skinsize[0] and skin['Size'][1] > skinsize[1]:
                                    skinsize = skin['Size']
                                break
                        else:
                            message = message + "Component: " + ModelFolder + "_" + surface.name + "\r\nuses the texture:\r\n    " + surface.shaders[i].name + "\r\nBut the image does not exist in that folder\r\nand there are no shaders by that name.\r\nLocate image file and place in that folder.\r\n\r\n"
                    else:
                        message = message + "Component: " + ModelFolder + "_" + surface.name + "\r\ndid not give any shader or texture to use in its folder:\r\n    " + FolderPath + "\r\nYou will need to locate an image file,\r\nplace in that folder and skin the model.\r\n\r\n"
                shader_name = None

        if skinsize == (0, 0):
            skinsize = (256, 256)

        ###  Create the Component's "Tris", this needs to be in binary so we use the 'struct' function.
        faces = []
        faces.extend([surface.triangles[i].indexes for i in xrange(surface.numTriangles)])
        Tris = ''
        TexWidth, TexHeight = skinsize
        for face in faces:
            for vert_index in face:
                u = TexWidth * surface.uv[vert_index].u
                v = TexHeight * surface.uv[vert_index].v
                Tris = Tris + struct.pack("Hhh", vert_index, u, v)

        # Now we start creating our Import Component and name it.
        if surface.name != "":
            Component = quarkx.newobj(ModelFolder + '_' + surface.name + ':mc')
        else:
            Component = quarkx.newobj(ModelFolder + '_' + "Import Component " + str(CompNbr) + ':mc')
            CompNbr = CompNbr + 1
        # Set it up in the ModelComponentList.
        editor.ModelComponentList[Component.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}

        if shader_file is not None: # The path and name of the shader file.
            Component['shader_file'] = shader_file
        if shader_name is not None: # The name of the shader in the shader file.
            if len(shaderlist) == 1:
                Component['shader_name'] = shader_name
            else:
                Component['shader_name'] = "multiple shaders - see mesh shader below"
        if mesh_shader is not None: # The actual text, to display, of the shader itself.
            Component['mesh_shader'] = mesh_shader
        Component['skinsize'] = skinsize
        Component['Tris'] = Tris
        Component['show'] = chr(1)
        sdogroup = quarkx.newobj('SDO:sdo')
        Component.appenditem(sdogroup)
        Component.appenditem(skingroup)
        Component.appenditem(framesgroup)
        ComponentList = ComponentList + [Component]

    # create tags
    tagsgroup = []
    tag_comp = ComponentList[len(ComponentList)-1]
    for comp in ComponentList:
        if comp.shortname.endswith("torso"):
            tag_comp = comp
        # We need to put a list of component names in ALL components because some people may not have things in the right order.
        if md3.numTags != 0 or ModelsPath.find("weapons") != -1: # But not all models have tags, we only want ones that do or should.
            for comp2 in range(len(ComponentList)):
                if comp2 == 0:
                    comp['tag_components'] = ComponentList[comp2].name
                else:
                    comp['tag_components'] = comp.dictspec['tag_components'] + ", " + ComponentList[comp2].name

    if ModelsPath.find("weapons") != -1: # And other people do not know how to setup things right at all.
        if md3.numTags == 0:
            tag_types = ("barrel", "flash")
            tag = md3Tag()
            tag.name = "tag_weapon"
            md3.tags.append(tag)
            tagnames = ModelName.split("_")
            for name in range(len(tagnames)):
                if tagnames[name] in tag_types:
                    tagname = "tag_" + tagnames[name]
                    break
                if name == len(tagnames)-1:
                    tagname = "tag_" + tagnames[len(tagnames)-1]
            tag = md3Tag()
            tag.name = tagname
            md3.tags.append(tag)
            md3.numTags = 2
        else:
            for i in xrange(md3.numTags):
                if md3.tags[i].name == "tag_weapon":
                    break
                if i == md3.numTags-1:
                    tag = md3Tag()
                    tag.name = "tag_weapon"
                    md3.tags.append(tag)
                    md3.numTags = md3.numTags + 1
    for i in xrange(md3.numTags):
        tag = md3.tags[i]
        # We need to keep these sepperate for each complete model loaded.
        newtag = quarkx.newobj(ModelFolder + '_' + tag.name + ':tag')
        tagname = tag.name.split("_", 1)[1]
        if ModelName.find(tagname) != -1:
            newtag['Component'] = tag_comp.name
        elif editor.Root.dictitems['Misc:mg'].dictitems.has_key(newtag.name):
            if editor.Root.dictitems['Misc:mg'].dictitems[newtag.name].dictspec.has_key("Component"):
                newtag['Component'] = editor.Root.dictitems['Misc:mg'].dictitems[newtag.name].dictspec['Component']
        tagsgroup = tagsgroup + [newtag]
        if i == 0:
            tag_comp['Tags'] = tag.name
        else:
            tag_comp['Tags'] = tag_comp.dictspec['Tags'] + ", " + tag.name

        if surface.numFrames > 0 :
            for j in xrange(md3.numFrames):
                try:
                    tag = md3.tags[j * md3.numTags + i]
                except:
                    continue

                # Note: Quake3 uses left-hand geometry
              #  forward = [tag.axis[0], tag.axis[1], tag.axis[2]] # Blinder's way.
              #  left = [tag.axis[3], tag.axis[4], tag.axis[5]] # Blinder's way.
              #  right = [tag.axis[3], tag.axis[4], tag.axis[5]] # Quark's way.
              #  forward = [tag.axis[0], tag.axis[1], tag.axis[2]] # Quark's way.
              #  up = [tag.axis[6], tag.axis[7], tag.axis[8]]
                p = tag.origin
                tagframe = quarkx.newobj('Tag Frame ' + str(j+1) + ':tagframe')
                tagframe['show'] = (1.0,)
                tagframe['origin'] = (p[0], p[1], p[2])
                tagframe['rotmatrix'] = (tag.axis[0], tag.axis[1], tag.axis[2], tag.axis[3], tag.axis[4], tag.axis[5], tag.axis[6], tag.axis[7], tag.axis[8])
                if j == 0:
                    baseframe = tagframe.copy()
                    baseframe.shortname = "Tag baseframe"
                    if surface.numFrames == 1:
                        newtag.appenditem(baseframe)
                        continue
                newtag.appenditem(tagframe)
                if j == md3.numFrames-1:
                    if old_torso_tag_frames is not None:
                        for frame in range(j+1, len(old_torso_tag_frames)):
                            if frame == len(old_torso_tag_frames)-1:
                                newtag.appenditem(baseframe)
                            else:
                                extra_tagframe = tagframe.copy()
                                extra_tagframe.shortname = 'Tag Frame ' + str(frame+1)
                                newtag.appenditem(extra_tagframe)
                    else:
                        newtag.appenditem(baseframe)

    ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.

    if ComponentList == []:
        if logging == 1:
            tobj.logcon ("Can't read file %s" %filename)
        return [None, None, ""]

    ### Use the 'ModelRoot' below to test opening the QuArK's Model Editor with, needs to be qualified with main menu item.
    ModelRoot = quarkx.newobj('Model:mr')
  #  ModelRoot.appenditem(Component)

    return ModelRoot, ComponentList, message, tagsgroup, ModelFolder, ModelName


def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename is the full path and name of the .md3 file selected."
    "gamename is None."
    "For example:  C:\Quake 3 Arena\baseq3\models\mapobjects\banner\banner5.md3"

    global editor, basepath
    import quarkpy.mdleditor
    editor = quarkpy.mdleditor.mdleditor
    # Step 1 to import model from QuArK's Explorer.
    if editor is None:
        editor = quarkpy.mdleditor.ModelEditor(None)
        editor.Root = quarkx.newobj('Model Root:mr')
        misc_group = quarkx.newobj('Misc:mg')
        misc_group['type'] = chr(6)
        editor.Root.appenditem(misc_group)
        skeleton_group = quarkx.newobj('Skeleton:bg')
        skeleton_group['type'] = chr(5)
        editor.Root.appenditem(skeleton_group)
        editor.form = None

    ### First we test for a valid (proper) model path.
    basepath = ie_utils.validpath(filename)
    try:
        basepath = basepath.replace("\\", "/")
    except:
        editor = None # Reset the global again.
        return
    if basepath is None:
        editor = None # Reset the global again.
        return

    ### Line below just runs the importer without the editor being open.
    ### Need to figure out how to open the editor with it & complete the ModelRoot.
  #  Import( basepath, filename)

    ### Lines below here loads the model into the opened editor's current model.
    ModelRoot, ComponentList, message, tagsgroup, ModelFolder, ModelName = Import(basepath, filename)

    if ModelRoot is None or ComponentList is None or ComponentList == []:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid.
        quarkx.msgbox("Invalid .md3 model.\nEditor can not import it.", MT_ERROR, MB_OK)
        editor = None # Reset the global again.
        return

    # FullPathName is the full path and the full file name being imported with forward slashes.
    FullPathName = filename.replace("\\", "/")
    # FolderPath is the full path to the model's folder w/o slash at end.
    FolderPath = FullPathName.rsplit("/", 1)[0]

    if editor.form is not None:
        undo = quarkx.action()
    editor_dictitems = editor.Root.dictitems
    miscgroup = editor_dictitems['Misc:mg'].subitems
    old_torso_tag_frames = new_torso_tag_frames = old_tag_subitems = None
    
    if len(tagsgroup) > 1:
        # To remove incorrect duplicate tags with the lowest tag_frame count.
        fixed_tagsgroup = []
        for tag in range(len(tagsgroup)):
            if tagsgroup[tag] in fixed_tagsgroup:
                for item in range(len(fixed_tagsgroup)):
                    if tagsgroup[tag].name == fixed_tagsgroup[item].name:
                        if len(tagsgroup[tag].subitems) > len(fixed_tagsgroup[item].subitems):
                            fixed_tagsgroup[item] = tagsgroup[tag]
                            break
            else:
                fixed_tagsgroup = fixed_tagsgroup + [tagsgroup[tag]]
        tagsgroup = fixed_tagsgroup

        # To make sure the order of the tags is correct.
        for tag in range(len(tagsgroup)):
            if tagsgroup[tag].name.find("torso") != -1 and not tagsgroup[len(tagsgroup)-1].name.find("torso") != -1:
                fixed_tagsgroup = []
                for tag2 in range(len(tagsgroup)):
                    if tagsgroup[tag2].name.find("torso") != -1:
                        holdtag = tagsgroup[tag2]
                        continue
                    fixed_tagsgroup = fixed_tagsgroup + [tagsgroup[tag2]]
                    if tag2 == len(tagsgroup)-1:
                        fixed_tagsgroup = fixed_tagsgroup + [holdtag]
                        tagsgroup = fixed_tagsgroup

        # To get to current torso tag frames that will be needed later if they exist in the editor already.
        for tag in range(len(tagsgroup)):
            if tagsgroup[tag].name.find("torso") != -1:
                if editor_dictitems['Misc:mg'].dictitems.has_key(tagsgroup[tag].name):
                    old_torso_tag_frames = editor_dictitems['Misc:mg'].dictitems[tagsgroup[tag].name].subitems
                new_torso_tag_frames = tagsgroup[tag].subitems

    # Start importing the tags and making the animation frames.
    for tag in range(len(tagsgroup)):
        if len(miscgroup) == 0:
            if editor.form is not None:
                undo.put(editor_dictitems['Misc:mg'], tagsgroup[tag])
            else:
                editor_dictitems['Misc:mg'].appenditem(tagsgroup[tag])
        for item in range(len(miscgroup)):
            if tagsgroup[tag].name == miscgroup[item].name:
                if ModelName.find("upper") != -1:
                    # This is where we need to update all of the model's components frames and vertex positions.
                    # using "ModelFolder" which is the first part of each of its component's name to distinguish them.
                    for key in editor_dictitems.keys():
                        tagname = None
                        if editor_dictitems[key].dictspec.has_key("Tags"):
                            tagname = editor_dictitems[key].dictspec['Tags']
                        if tagname is None:
                            continue
                        if editor_dictitems[key].type == ":mc" and editor_dictitems[key].name.startswith(ModelFolder) and tagsgroup[tag].name.find(tagname) != -1:
                            if tagsgroup[tag].name.find("head") != -1 and (editor_dictitems[key].name.find("head") != -1 or editor_dictitems[key].name.find("_h_") != -1):
                                if old_torso_tag_frames is not None:
                                    if editor_dictitems['Misc:mg'].dictitems.has_key(ModelFolder + "_tag_head:tag"):
                                        old_taggroup = editor_dictitems['Misc:mg'].dictitems[ModelFolder + "_tag_head:tag"]
                                        old_tag_subitems = old_taggroup.subitems
                                tag_subitems = tagsgroup[tag].subitems
                                miscgroup_subitems = miscgroup[item].subitems
                                tag_comp = editor_dictitems[key]
                                tag_comps_list = tag_comp.dictspec['tag_components'].split(", ")
                                editor_comps_frames = []
                                newcomps = []
                                newframesgroups = []
                                for comp in range(len(tag_comps_list)):
                                    editor_comps_frames = editor_comps_frames + [editor_dictitems[tag_comps_list[comp]].dictitems['Frames:fg'].subitems]
                                    newcomp = editor_dictitems[tag_comps_list[comp]].copy()
                                    newcomps = newcomps + [newcomp]
                                    newframesgroup = quarkx.newobj('Frames:fg')
                                    newframesgroups = newframesgroups + [newframesgroup]
                                for frame in range(len(tag_subitems)):
                                    if frame == len(tag_subitems)-1 and old_tag_subitems is not None:
                                        tag_subitems[frame]['origin'] = old_tag_subitems[len(old_tag_subitems)-1].dictspec['origin']
                                        tag_subitems[frame]['rotmatrix'] = old_tag_subitems[len(old_tag_subitems)-1].dictspec['rotmatrix']
                                    elif old_torso_tag_frames is not None and old_tag_subitems is not None:
                                        if frame >= len(old_tag_subitems)-1:
                                            ot_r = old_tag_subitems[len(old_tag_subitems)-1].dictspec['rotmatrix'] # This is the ORIGINAL ROTATION matrix for the "head's" tag frame matrix.
                                            ot_r = ((ot_r[0],ot_r[1],ot_r[2]), (ot_r[3],ot_r[4],ot_r[5]), (ot_r[6],ot_r[7],ot_r[8]))
                                            old_tag_rotation = quarkx.matrix(ot_r)
                                            old_tag_origin = old_tag_subitems[len(old_tag_subitems)-1].dictspec['origin'] # This is the ORIGINAL ORIGIN for the "head's" tag frame.
                                        else:
                                            ot_r = old_tag_subitems[frame].dictspec['rotmatrix'] # This is the ORIGINAL ROTATION matrix for the "head's" tag frame matrix.
                                            ot_r = ((ot_r[0],ot_r[1],ot_r[2]), (ot_r[3],ot_r[4],ot_r[5]), (ot_r[6],ot_r[7],ot_r[8]))
                                            old_tag_rotation = quarkx.matrix(ot_r)
                                            old_tag_origin = old_tag_subitems[frame].dictspec['origin'] # This is the ORIGINAL ORIGIN for the "head's" tag frame.
                                        o_r = old_torso_tag_frames[frame].dictspec['rotmatrix'] # This is the ORIGINAL ROTATION matrix for the "torso's" tag frame matrix.
                                        o_r = ((o_r[0],o_r[1],o_r[2]), (o_r[3],o_r[4],o_r[5]), (o_r[6],o_r[7],o_r[8]))
                                        org_rotation = quarkx.matrix(o_r)
                                        org_origin = old_torso_tag_frames[frame].dictspec['origin'] # This is the ORIGINAL ORIGIN for the "torso's" tag frame.

                                    n_r = tag_subitems[frame].dictspec['rotmatrix'] # This is the NEW ROTATION matrix for the "head's" tag frame matrix.
                                    n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                    new_rotation = quarkx.matrix(n_r)
                                    new_origin = tag_subitems[frame].dictspec['origin'] # This is the NEW ORIGIN for the "head's" tag frame.
                                    for comp in range(len(tag_comps_list)):
                                        comp_frames = editor_comps_frames[comp]
                                        comp_framecount = len(comp_frames)-1
                                        if frame == len(tag_subitems)-1:
                                            newframesgroups[comp].appenditem(comp_frames[len(comp_frames)-1].copy())
                                            continue
                                        # Get the NEWTag position and rotation data.
                                        if comp == 0 and old_torso_tag_frames is not None and old_tag_subitems is not None:
                                            tag_subitems[frame]['origin'] = (quarkx.vect(org_origin) + ((~org_rotation) * old_tag_rotation * (quarkx.vect(new_origin) - quarkx.vect(old_tag_origin)))).tuple
                                            new_rotation = ~(((~org_rotation) * old_tag_rotation) * (~new_rotation))
                                            n_r = new_rotation.tuple
                                            tag_subitems[frame]['rotmatrix'] = (n_r[0][0], n_r[0][1], n_r[0][2], n_r[1][0], n_r[1][1], n_r[1][2], n_r[2][0], n_r[2][1], n_r[2][2])
                                        # Now, move the tags.
                                        if frame >= comp_framecount:
                                            comp_frame = comp_frames[comp_framecount].copy()
                                            comp_frame.shortname = "Frame " + str(frame+1)
                                        else:
                                            comp_frame = comp_frames[frame]
                                            comp_frame.shortname = "Frame " + str(frame+1)
                                        # Now, move the component's vertexes.
                                        vertices = []
                                        for vtx in comp_frame.vertices:
                                            vtx = (~new_rotation * vtx) + quarkx.vect(tag_subitems[frame]['origin'])
                                            vertices = vertices + [vtx]
                                        comp_frame.vertices = vertices
                                        newframe = comp_frame.copy()
                                        newframesgroups[comp].appenditem(newframe)
                                if editor.form is not None:
                                    for i in range(len(tag_comps_list)):
                                        undo.exchange(newcomps[i].dictitems['Frames:fg'], newframesgroups[i])
                                        undo.exchange(editor_dictitems[tag_comps_list[i]], newcomps[i])
                                break

                            elif tagsgroup[tag].name.find("weapon") != -1 and editor_dictitems[key].name.find("weapon") != -1:
                                tag_subitems = tagsgroup[tag].subitems
                                for frame in range(len(tag_subitems)):
                                    if frame == len(tag_subitems)-1:
                                        continue
                                    if old_torso_tag_frames is not None and new_torso_tag_frames is not None:
                                        if frame >= len(new_torso_tag_frames)-1:
                                            ntr = new_torso_tag_frames[len(new_torso_tag_frames)-1].dictspec['rotmatrix'] # This is the NEW ROTATION matrix for the "torso's" tag frame matrix.
                                            ntr = ((ntr[0],ntr[1],ntr[2]), (ntr[3],ntr[4],ntr[5]), (ntr[6],ntr[7],ntr[8]))
                                            new_torso_rotation = quarkx.matrix(ntr)
                                            new_torso_origin = new_torso_tag_frames[len(new_torso_tag_frames)-1].dictspec['origin'] # This is the NEW ORIGIN for the "torso's" tag frame.
                                        else:
                                            ntr = new_torso_tag_frames[frame].dictspec['rotmatrix'] # This is the NEW ROTATION for the "torso's" tag frame.
                                            ntr = ((ntr[0],ntr[1],ntr[2]), (ntr[3],ntr[4],ntr[5]), (ntr[6],ntr[7],ntr[8]))
                                            new_torso_rotation = quarkx.matrix(ntr)
                                            new_torso_origin = new_torso_tag_frames[frame].dictspec['origin'] # This is the NEW ORIGIN for the "torso's" tag frame.
                                        otr = old_torso_tag_frames[frame].dictspec['rotmatrix'] # This is the ORIGINAL ROTATION matrix for the "torso's" tag frame matrix.
                                        otr = ((otr[0],otr[1],otr[2]), (otr[3],otr[4],otr[5]), (otr[6],otr[7],otr[8]))
                                        old_torso_rotation = quarkx.matrix(otr)
                                        old_torso_origin = old_torso_tag_frames[frame].dictspec['origin'] # This is the ORIGINAL ORIGIN for the "torso's" tag frame.
                                    n_r = tag_subitems[frame].dictspec['rotmatrix'] # This is the NEW ROTATION matrix for the "weapon's" tag frame matrix.
                                    n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                    new_rotation = quarkx.matrix(n_r)
                                    new_origin = tag_subitems[frame].dictspec['origin'] # This is the NEW ORIGIN for the "weapon's" tag frame.
                                    if old_torso_tag_frames is not None and new_torso_tag_frames is not None:
                                        # Now, move the tags.
                                        tag_subitems[frame]['origin'] = (quarkx.vect(old_torso_origin) + ((~old_torso_rotation) * new_torso_rotation * (quarkx.vect(new_origin) - quarkx.vect(new_torso_origin)))).tuple
                                        new_rotation = (old_torso_rotation * (~new_torso_rotation)) * new_rotation
                                        n_r = new_rotation.tuple
                                        tag_subitems[frame]['rotmatrix'] = (n_r[0][0], n_r[0][1], n_r[0][2], n_r[1][0], n_r[1][1], n_r[1][2], n_r[2][0], n_r[2][1], n_r[2][2])
                                break
                            elif tagsgroup[tag].name.find("torso") != -1:
                                # This is where we read in the players model animation.cfg file if one exist.
                                if os.path.isfile(FolderPath + "/animation.cfg"):
                                    read_CFG_file = open(FolderPath + "/animation.cfg","r")
                                    CFGlines = read_CFG_file.readlines()
                                    read_CFG_file.close()
                                    animationCFG = ""
                                    # Dec character code for space = chr(32), for tab = chr(9)
                                    for line in range(len(CFGlines)):
                                        CFGline = CFGlines[line].replace(chr(9), "    ")
                                        CFGline = CFGline.rstrip()
                                        animationCFG = animationCFG + CFGline + "\r\n"
                                    tagsgroup[tag]['animationCFG'] = animationCFG
                                    tagsgroup[tag]['animCFG_file'] = FolderPath + "/animation.cfg"
                                # Now we work on the tag.
                                tag_subitems = tagsgroup[tag].subitems
                                miscgroup_subitems = miscgroup[item].subitems
                                newcomp = editor_dictitems[key].copy()
                                comp_frames = newcomp.dictitems['Frames:fg'].subitems
                                newframesgroup = quarkx.newobj('Frames:fg')
                                for frame in range(len(tag_subitems)):
                                    if old_torso_tag_frames is not None:
                                        old_torso_tag_rotmatrix = old_torso_tag_frames[frame].dictspec['rotmatrix']
                                        if frame == len(tag_subitems)-1:
                                            tag_subitems[frame]['origin'] = old_torso_tag_frames[len(old_torso_tag_frames)-1].dictspec['origin']
                                            tag_subitems[frame]['rotmatrix'] = old_torso_tag_frames[len(old_torso_tag_frames)-1].dictspec['rotmatrix']
                                            old_torso_tag_rotmatrix = old_torso_tag_frames[len(old_torso_tag_frames)-1].dictspec['rotmatrix']
                                            newframe = comp_frames[len(comp_frames)-1].copy()
                                            newframesgroup.appenditem(newframe)
                                            continue
                                        o_r = old_torso_tag_frames[frame].dictspec['rotmatrix'] # This is the ORIGINAL ROTATION matrix for the "torso's" tag frame matrix.
                                        o_r = ((o_r[0],o_r[1],o_r[2]), (o_r[3],o_r[4],o_r[5]), (o_r[6],o_r[7],o_r[8]))
                                        org_rotation = quarkx.matrix(o_r)
                                        org_origin = old_torso_tag_frames[frame].dictspec['origin'] # This is the ORIGINAL ORIGIN for the "torso's" tag frame.
                                    n_r = tag_subitems[frame].dictspec['rotmatrix'] # This is the NEW ROTATION matrix for the "torso's" tag frame matrix.
                                    if old_torso_tag_frames is not None:
                                        tag_subitems[frame]['rotmatrix'] = old_torso_tag_rotmatrix # But we need to reset it back to the old matrix after we use it above to save the matrix data.
                                    n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                    new_rotation = quarkx.matrix(n_r)
                                    new_origin = tag_subitems[frame].dictspec['origin'] # This is the NEW ORIGIN for the "head's" tag frame.
                                    if old_torso_tag_frames is not None:
                                        # Now, move the tags
                                        tag_subitems[frame]['origin'] = (quarkx.vect(org_origin) + ((~org_rotation) * new_rotation * (quarkx.vect(new_origin) - quarkx.vect(new_origin)))).tuple
                                        new_rotation2 = (org_rotation * (~new_rotation)) * new_rotation
                                        n_r2 = new_rotation2.tuple
                                        tag_subitems[frame]['rotmatrix'] = (n_r2[0][0], n_r2[0][1], n_r2[0][2], n_r2[1][0], n_r2[1][1], n_r2[1][2], n_r2[2][0], n_r2[2][1], n_r2[2][2])
                                    # To try and rotate upper components properly when they come through.
                                    if ModelName.find("upper") != -1:
                                        for Component in ComponentList:
                                            vertices = []
                                            comp_subitems = Component.dictitems['Frames:fg'].subitems # To fix slowdown.
                                            for vtx in comp_subitems[frame].vertices:
                                                if old_torso_tag_frames is None: # use OLD method.
                                                    comp_rotation = vector_by_matrix(vtx.tuple, n_r)
                                                    comp_rotation = quarkx.vect(comp_rotation[0], comp_rotation[1], comp_rotation[2])
                                                    vtx = new_rotation * comp_rotation # new_rotation is the UPPER'S torso's" tag frame matrix.
                                                else: # use NEW method.
                                                    vtx = quarkx.vect(org_origin) + ((~org_rotation) * new_rotation * (vtx - quarkx.vect(new_origin)))
                                                vertices = vertices + [vtx]
                                            Component.dictitems['Frames:fg'].subitems[frame].vertices = vertices
                                    tag_adj_vect = quarkx.vect(tag_subitems[frame].dictspec['origin']) - quarkx.vect(miscgroup_subitems[frame].dictspec['origin'])
                                    vertices = []
                                    for vtx in comp_frames[frame].vertices:
                                        # To try and rotate lower components properly when they come through.
                                        if old_torso_tag_frames is not None: # use OLD method.
                                            comp_rotation = vector_by_matrix(vtx.tuple, n_r)
                                            comp_rotation = quarkx.vect(comp_rotation[0], comp_rotation[1], comp_rotation[2])
                                            vtx = comp_rotation
                                            vertices = vertices + [vtx + tag_adj_vect]
                                        else: # use NEW method.
                                            vtx = quarkx.vect(org_origin) + ((~org_rotation) * new_rotation * (vtx - quarkx.vect(new_origin)))
                                            vertices = vertices + [vtx]
                                    comp_frames[frame].vertices = vertices
                                    newframe = comp_frames[frame].copy()
                                    newframesgroup.appenditem(newframe)
                                if editor.form is not None:
                                    undo.exchange(newcomp.dictitems['Frames:fg'], newframesgroup)
                                    undo.exchange(editor_dictitems[key], newcomp)
                                break
                    if editor.form is not None:
                        undo.exchange(miscgroup[item], tagsgroup[tag]) # This replaces the ORIGINAL Torso tag frames with FEWER tag frames.
                    break
                else: # This is where the weapons would come through.
                    if tagsgroup[tag].dictspec.has_key("Component"):
                        update_tag = miscgroup[item].copy()
                        update_tag['Component'] = tagsgroup[tag].dictspec['Component']
                        if editor.form is not None:
                            undo.exchange(miscgroup[item], update_tag)
                        for comp in ComponentList:
                            if comp.name == tagsgroup[tag].dictspec['Component']:
                                for comp in ComponentList:
                                    vertices = []
                                    comp_frames = comp.dictitems['Frames:fg'].subitems
                                    misc_tag_frames = miscgroup[item].subitems
                                    tag_frames = tagsgroup[tag].subitems
                                    for frame in range(len(comp_frames)):
                                        try:
                                            vtx_adj = quarkx.vect(misc_tag_frames[frame].dictspec['origin']) - quarkx.vect(tag_frames[frame].dictspec['origin'])
                                            for vtx in comp_frames[frame].vertices:
                                                vtx = vtx + vtx_adj
                                                vertices = vertices + [vtx]
                                            comp_frames[frame].vertices = vertices
                                        except:
                                            continue
                    break
            if item == len(miscgroup)-1:
                if tagsgroup[tag].name.find("weapon") != -1 and ModelName.find("upper") != -1:
                    tag_subitems = tagsgroup[tag].subitems
                    for frame in range(len(tag_subitems)):
                        if frame == len(tag_subitems)-1:
                            continue
                        if old_torso_tag_frames is not None and new_torso_tag_frames is not None:
                            if frame >= len(new_torso_tag_frames)-1:
                                ntr = new_torso_tag_frames[len(new_torso_tag_frames)-1].dictspec['rotmatrix'] # This is the NEW ROTATION matrix for the "torso's" tag frame matrix.
                                ntr = ((ntr[0],ntr[1],ntr[2]), (ntr[3],ntr[4],ntr[5]), (ntr[6],ntr[7],ntr[8]))
                                new_torso_rotation = quarkx.matrix(ntr)
                                new_torso_origin = new_torso_tag_frames[len(new_torso_tag_frames)-1].dictspec['origin'] # This is the NEW ORIGIN for the "torso's" tag frame.
                            else:
                                ntr = new_torso_tag_frames[frame].dictspec['rotmatrix'] # This is the NEW ROTATION for the "torso's" tag frame.
                                ntr = ((ntr[0],ntr[1],ntr[2]), (ntr[3],ntr[4],ntr[5]), (ntr[6],ntr[7],ntr[8]))
                                new_torso_rotation = quarkx.matrix(ntr)
                                new_torso_origin = new_torso_tag_frames[frame].dictspec['origin'] # This is the NEW ORIGIN for the "torso's" tag frame.
                            otr = old_torso_tag_frames[frame].dictspec['rotmatrix'] # This is the ORIGINAL ROTATION matrix for the "torso's" tag frame matrix.
                            otr = ((otr[0],otr[1],otr[2]), (otr[3],otr[4],otr[5]), (otr[6],otr[7],otr[8]))
                            old_torso_rotation = quarkx.matrix(otr)
                            old_torso_origin = old_torso_tag_frames[frame].dictspec['origin'] # This is the ORIGINAL ORIGIN for the "torso's" tag frame.
                        n_r = tag_subitems[frame].dictspec['rotmatrix'] # This is the NEW ROTATION matrix for the "weapon's" tag frame matrix.
                        n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                        new_rotation = quarkx.matrix(n_r)
                        new_origin = tag_subitems[frame].dictspec['origin'] # This is the NEW ORIGIN for the "weapon's" tag frame.
                        if old_torso_tag_frames is not None and new_torso_tag_frames is not None:
                            # Now, move the tags.
                            tag_subitems[frame]['origin'] = (quarkx.vect(old_torso_origin) + ((~old_torso_rotation) * new_torso_rotation * (quarkx.vect(new_origin) - quarkx.vect(new_torso_origin)))).tuple
                            new_rotation = (old_torso_rotation * (~new_torso_rotation)) * new_rotation
                            n_r = new_rotation.tuple
                            tag_subitems[frame]['rotmatrix'] = (n_r[0][0], n_r[0][1], n_r[0][2], n_r[1][0], n_r[1][1], n_r[1][2], n_r[2][0], n_r[2][1], n_r[2][2])

                if editor.form is not None:
                    undo.put(editor_dictitems['Misc:mg'], tagsgroup[tag])
                else:
                    editor_dictitems['Misc:mg'].appenditem(tagsgroup[tag])

    # Now we process the Components.
    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        md2fileobj = quarkx.newfileobj("New model.md2")
        md2fileobj['FileName'] = 'New model.qkl'
        for Component in ComponentList:
            editor.Root.appenditem(Component)
        md2fileobj['Root'] = editor.Root.name
        md2fileobj.appenditem(editor.Root)
        md2fileobj.openinnewwindow()
    else: # Imports a model properly from within the editor.
        for Component in ComponentList:
            dupeitem = 0
            for item in editor.Root.subitems:
                if item.type == ":mc":
                    if item.name == Component.name:
                        dupeitem = 1
                        break
            if dupeitem == 1:
                undo.exchange(editor.Root.dictitems[item.name], Component)
            else:
                undo.put(editor.Root, Component)
            editor.Root.currentcomponent = Component
            if len(Component.dictitems['Skins:sg'].subitems) != 0:
                editor.Root.currentcomponent.currentskin = Component.dictitems['Skins:sg'].subitems[0] # To try and set to the correct skin.
                quarkpy.mdlutils.Update_Skin_View(editor, 2) # Sends the Skin-view for updating and center the texture in the view.
            else:
                editor.Root.currentcomponent.currentskin = None

            compframes = editor.Root.currentcomponent.findallsubitems("", ':mf')   # get all frames
            for compframe in compframes:
                compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.

            # This needs to be done for each component or bones will not work if used in the editor.
            quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
        editor.ok(undo, str(len(ComponentList)) + " .md3 Components imported")

        editor = None   #Reset the global again
        if message != "":
            message = message + "================================\r\n\r\n"
            message = message + "You need to find and supply the proper texture(s) and folder(s) above.\r\n"
            message = message + "Extract the folder(s) and file(s) to the 'game' folder.\r\n\r\n"
            message = message + "If a texture does not exist it may be a .dds or some other type of image file.\r\n"
            message = message + "If so then you need to make a .tga file copy of that texture, perhaps in PaintShop Pro.\r\n\r\n"
            message = message + "You may also need to rename it to match the exact name above.\r\n"
            message = message + "Either case, it would be for editing purposes only and should be placed in the model's folder.\r\n\r\n"
            message = message + "Once this is done, then delete the imported components and re-import the model."
            quarkx.textbox("WARNING", "Missing Skin Textures:\r\n\r\n================================\r\n" + message, MT_WARNING)

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_md3_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
if quarkx.setupsubset(SS_MODEL, "Options")['IEMaxTagFrames'] == "1":
    quarkpy.qmdlbase.RegisterMdlImporter(".md3 Quake3 Importer - max. tag frames", ".md3 file", "*.md3", loadmodel, ie_md3_import)
else:
    quarkpy.qmdlbase.RegisterMdlImporter(".md3 Quake3 Importer - min. tag frames", ".md3 file", "*.md3", loadmodel, ie_md3_import)

def md3_menu_text():
    if quarkx.setupsubset(SS_MODEL, "Options")['IEMaxTagFrames'] == "1":
        NewText = ".md3 Quake3 Importer - max. tag frames"
        OldText = ".md3 Quake3 Importer - min. tag frames"
    else:
        NewText = ".md3 Quake3 Importer - min. tag frames"
        OldText = ".md3 Quake3 Importer - max. tag frames"
    return OldText, NewText

import quarkpy.mdlentities
quarkpy.mdlentities.RegisterMenuImporterChanged(md3_menu_text)

def dataformname(o):
    "Returns the data form for this type of object 'o' (a model component & others) to use for the Specific/Args page."
    import quarkpy.mdlentities # Used further down in a couple of places.

    # Next line calls for the Shader Module in mdlentities.py to be used.
    external_skin_editor_dialog_plugin = quarkpy.mdlentities.UseExternalSkinEditor()

    # Next line calls for the Shader Module in mdlentities.py to be used.
    Shader_dialog_plugin = quarkpy.mdlentities.UseShaders()

    dlgdef = """
    {
      Help = "These are the Specific settings for Quake 3 (.md3) model types."$0D
             "md3 models use 'surfaces' the same way that QuArK uses 'components'."$0D
             "Each can have its own special Surface or skin texture settings."$0D
             "These textures may or may not have 'shaders' that they use for special effects."$0D
             "In particular, 'player' models use '.skin' files that specify the texture to use."$0D0D22
             "edit skin"$22" - Opens this skin texture in an external editor."$0D0D
             "Shader File - Special effects code by use of textures."$0D22
             "shader file"$22" - Gives the full path and name of the .shader"$0D
             "           file that the selected skin texture uses, if any."$0D22
             "shader name"$22" - Gives the name of the shader located in the above file"$0D
             "           that the selected skin texture uses, if any."$0D22
             "shader keyword"$22" - Gives the above shader 'keyword' that is used to identify"$0D
             "          the currently selected skin texture used in the shader, if any."$0D22
             "shader lines"$22" - Number of lines to display in window below, max. = 35."$0D22
             "edit shader"$22" - Opens shader below in a text editor."$0D22
             "mesh shader"$22" - Contains the full text of this skin texture's shader, if any."$0D
             "          This can be copied to a text file, changed and saved."
      """ + external_skin_editor_dialog_plugin + """
      """ + Shader_dialog_plugin + """
    }
    """

    from quarkpy.qeditor import ico_dict # Get the dictionary list of all icon image files available.
    import quarkpy.qtoolbar              # Get the toolbar functions to make the button with.
    editor = quarkpy.mdleditor.mdleditor # Get the editor.
    icon_btns = {}                       # Setup our button list, as a dictionary list, to return at the end.

    if (editor.Root.currentcomponent.currentskin is not None) and (o.name == editor.Root.currentcomponent.currentskin.name): # If this is not done it will cause looping through multiple times.
        if o.parent.parent.dictspec.has_key("shader_keyword") and o.dictspec.has_key("shader_keyword"):
            if o.parent.parent.dictspec['shader_keyword'] != o.dictspec['shader_keyword']:
                o.parent.parent['shader_keyword'] = o.dictspec['shader_keyword']

    DummyItem = o
    while (DummyItem.type != ":mc"): # Gets the object's model component.
        DummyItem = DummyItem.parent
    o = DummyItem

    if o.type == ":mc": # Just makes sure what we have is a model component.
        formobj = quarkx.newobj("md3_mc:form")
        formobj.loadtext(dlgdef)
        return formobj, icon_btns
    else:
        return None, None

def dataforminput(o):
    "Returns the default settings or input data for this type of object 'o' (a model component & others) to use for the Specific/Args page."

    editor = quarkpy.mdleditor.mdleditor # Get the editor.
    DummyItem = Item = o
    while (DummyItem.type != ":mc"): # Gets the object's model component.
        DummyItem = DummyItem.parent
    o = DummyItem
    if o.type == ":mc": # Just makes sure what we have is a model component.
        if not o.dictspec.has_key('shader_file'):
            o['shader_file'] = "None"
        if not o.dictspec.has_key('shader_name'):
            o['shader_name'] = "None"
        if not o.dictspec.has_key('shader_keyword'):
            o['shader_keyword'] = "None"
        if (editor.Root.currentcomponent.currentskin is not None) and (Item.name == editor.Root.currentcomponent.currentskin.name):
            if Item.dictspec.has_key("shader_keyword"):
                o['shader_keyword'] = Item.dictspec['shader_keyword']
        else:
            o['shader_keyword'] = "None"
        if not o.dictspec.has_key('shader_lines'):
            if quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] is not None:
                o['shader_lines'] = quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"]
            else:
                o['shader_lines'] = "8"
                quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = o.dictspec['shader_lines']
        else:
            quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = o.dictspec['shader_lines']
        if not o.dictspec.has_key('mesh_shader'):
            o['mesh_shader'] = "None"


# ----------- REVISION HISTORY ------------
#
# $Log: ie_md3_import.py,v $
# Revision 1.27  2012/10/01 20:28:57  cdunde
# Small update.
#
# Revision 1.26  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.25  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.24  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.23  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.22  2010/06/13 15:37:55  cdunde
# Setup Model Editor to allow importing of model from main explorer File menu.
#
# Revision 1.21  2010/05/01 04:25:37  cdunde
# Updated files to help increase editor speed by including necessary ModelComponentList items
# and removing redundant checks and calls to the list.
#
# Revision 1.20  2010/03/16 07:17:13  cdunde
# Added support for .md3 model format exporting with tags, textures and shader files.
#
# Revision 1.19  2009/12/21 15:13:43  cdunde
# Update to try and handle different folder names for mods.
#
# Revision 1.18  2009/10/16 00:59:47  cdunde
# Saving old matrix data for CFG rotation in the editor.
# Add animation rotation of weapon, for .md3 imports, when attached to model.
#
# Revision 1.17  2009/10/12 20:49:56  cdunde
# Added support for .md3 animationCFG (configuration) support and editing.
#
# Revision 1.16  2009/09/30 19:37:26  cdunde
# Threw out tags dialog, setup tag dragging, commands, and fixed saving of face selection.
#
# Revision 1.15  2009/09/29 20:07:44  danielpharos
# Update menuitem-text when IEMaxTagFrames option changes.
#
# Revision 1.14  2009/09/26 03:59:01  cdunde
# Added option for Model Editor to import-export max or min tag frames.
#
# Revision 1.13  2009/09/25 21:58:57  cdunde
# To bring in extra frames, for a player model, of the torso when the upper model is loaded.
#
# Revision 1.12  2009/09/24 21:41:03  cdunde
# Small update to remove duplicate tags.
#
# Revision 1.11  2009/09/24 06:46:02  cdunde
# md3 rotation update, baseframe creation and proper connection of weapon tags.
#
# Revision 1.10  2009/09/18 03:29:09  cdunde
# Added support to import and animate multiple components for player tag groups.
#
# Revision 1.9  2009/09/14 20:12:23  cdunde
# Switch back to cdunde's coding with some of DanielPharos methods included.
# Sorry Dan, you're so advanced I couldn't follow it. 8-)
#
# Revision 1.8  2009/09/14 20:02:55  cdunde
# DanielPharos's method to improve upon this importer. Thank you Dan.
#
# Revision 1.7  2009/09/09 03:47:33  cdunde
# Fix and message for script folder if not extracted when needed.
# Fix to stop multiple duplicate components caused by imports of the same model file.
#
# Revision 1.6  2009/09/08 06:45:12  cdunde
# Setup function to attach tags for imported .md3 models, such as weapons.
#
# Revision 1.5  2009/09/07 08:12:39  cdunde
# Changed from left handed to right handed matrix values as they are read in.
#
# Revision 1.4  2009/09/07 01:38:45  cdunde
# Setup of tag menus and icons.
#
# Revision 1.3  2009/09/06 11:54:44  cdunde
# To setup, make and draw the TagFrameHandles. Also improve animation rotation.
#
# Revision 1.2  2009/09/05 06:22:29  cdunde
# To fix setup error.
#
# Revision 1.1  2009/09/04 07:11:28  cdunde
# Added Python .md3 import support with tags, animation, shader and skin files.
#
#
#