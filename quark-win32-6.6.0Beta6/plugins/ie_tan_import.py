# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Alice, EF2 and FAKK2 .tan model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_tan_import.py,v 1.10 2011/03/13 00:41:47 cdunde Exp $


Info = {
   "plug-in":       "ie_tan_importer",
   "desc":          "This script imports a Alice, EF2 and FAKK2 file (.tan), textures, and animations into QuArK for editing.",
   "date":          "June 11 2010",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import struct, sys, os, time, operator
import quarkx
import quarkpy.qutils
from types import *
import quarkpy.mdlutils
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
logging = 0
importername = "ie_tan_import.py"
textlog = "tan_ie_log.txt"
editor = None
progressbar = None
used_skin_names = []


######################################################
# CString to Python string function
######################################################
def CString(data, length, start=0):
    result = ''
    for i in xrange(length):
        char = data[start+i]
        if char == "\x00":
            #NULL character found: End of string
            break
        result += char
    return result

######################################################
# TAN data structures
######################################################
class TAN_Frame:
    bboxMin = (0.0)*3  # Min. bounding box coords.
    bboxMax = (0.0)*3  # Max. bounding box coords.
    scale = (0.0)*3    # You will have to multiply every Vertex Coord by this.
    offset = (0.0)*3   # Center of bbox = (bboxMin + bboxMax) / 2. Need to add every Vertex Coords by this.
    delta = (0.0)*3    # unknown.
    radius = 0.0       # Radius from center of bounding box.
    frameTime = 0.0    # Length of Frame in sec -> useless ...

    binary_format="<17f" #little-endian (<), 17 float

    def __init__(self):
        self.bboxMin = (0.0)*3
        self.bboxMax = (0.0)*3
        self.scale = (0.0)*3
        self.offset = (0.0)*3
        self.delta = (0.0)*3
        self.radius = 0.0
        self.frameTime = 0.0

    def load (self, file):
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        # self.bboxMin[0] through self.bboxMin[2] ex: 0.0, -12.008715629577637, -12.461215019226074
        # self.bboxMax[3] through self.bboxMax[5] ex: 17.164989471435547, 11.542054176330566, 5.1593317985534668
        # self.scale[6] through self.scale[8] ex: 0.00026192094082944095, 0.0003593617002479732, 0.00026887230342254043
        # self.offset[9] through self.offset[11] ex: 0.0, -12.008715629577637, -12.461215019226074
        # self.delta[12] through self.delta[14] ex: -5.104235503814077e+038, -5.104235503814077e+038, -5.104235503814077e+038
        # self.radius[15] ex: 24.3747406006
        # self.frameTime[16] ex: 0.0500000007451
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.bboxMin = (data[0], data[1], data[2])
        self.bboxMax = (data[3], data[4], data[5])
        self.scale = (data[6], data[7], data[8])
        self.offset = (data[9], data[10], data[11])
        self.delta = (data[12], data[13], data[14])
        self.radius = data[15]
        self.frameTime = data[16]
        return self

    def dump (self):
        print "bboxMin: ",self.bboxMin
        print "bboxMax: ",self.bboxMax
        print "scale: ",self.scale
        print "offset: ",self.offset
        print "delta: ",self.delta
        print "radius: ",self.radius
        print "frameTime: ",self.frameTime
        print ""


class TAN_TagName:
    #Header Structure    #item of data file, size & type,   description.
    name = ""            #item   0    0-63 64 char, the tag name.

    binary_format="<64c"  #little-endian (<), see #item descriptions above.

    def __init__ (self):
        self.name = ""

    def load (self, file):
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.name = CString(data, 64)

    def dump (self):
        print "Tag Name: ",self.name
        print ""


class TAN_TagData:
    #Header Structure    #item of data file, size & type,   description.
    origin = (0.0)*3            # item   0-2    3 floats, read this was useless.
    axisRow1 = (1.0, 0.0, 0.0)  # item   3-5    3 floats, read this was useless.
    axisRow2 = (0.0, 1.0, 0.0)  # item   6-8    3 floats, read this was useless.
    axisRow3 = (0.0, 0.0, 1.0)  # item   9-11   3 floats, read this was useless.

    binary_format="<12f" #little-endian (<), 12 float

    def __init__(self):
        self.origin = (0.0)*3
        self.axisRow1 = (1.0, 0.0, 0.0)
        self.axisRow2 = (0.0, 1.0, 0.0)
        self.axisRow3 = (0.0, 0.0, 1.0)

    def load (self, file):
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        # ex: matrix = quarkx.matrix(axisRow1, axisRow2, axisRow3)
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.origin = (data[0], data[1], data[2])
        self.axisRow1 = (data[3], data[4], data[5])
        self.axisRow2 = (data[6], data[7], data[8])
        self.axisRow3 = (data[9], data[10], data[11])

    def dump (self):
        print "origin: ",self.origin
        print "axisRow1: ",self.axisRow1
        print "axisRow2: ",self.axisRow2
        print "axisRow3: ",self.axisRow3
        print ""


class TAN_TexCoord:
    #Header Structure    #item of data file, size & type,   description.
    uv = [0]*2      # item   0-1    2 float, a vertex's U,V values.

    binary_format="<2f" #little-endian (<), 2 floats

    def __init__(self):
        self.uv = [0]*2

    def load (self, file):
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.uv = [data[0], data[1]]


class TAN_Triangle:
    #Header Structure    #item of data file, size & type,   description.
    indices = [0]*3      # item   0-2    3 ints, a triangles 3 vertex indexes.

    binary_format="<3i" #little-endian (<), 3 int

    def __init__(self):
        self.indices = [0]*3

    def load (self, file):
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.indices = [data[0], data[1], data[2]]


class TAN_XyzNormal:
    #Header Structure    #item of data file, size & type,   description.
    position = [0]*3     # item   0-2    3 ints, a vertex's x,y,z values as unsigned short INTIGERS.
    normal = 0           # item   3      int, a vertex's normal value, as an unsigned short INTIGER.

    binary_format="<4H" #little-endian (<), 4 unsigned short ints

    def __init__(self):
        self.position = [0]*3
        self.normal = 0

    def load (self, file, scale, offset):
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        pos = [data[0], data[1], data[2]]
        normal = data[3]

        if logging == 1:
            tobj.logcon ("data pos: " + str(pos))
        for i in xrange(3):
            pos[i] = float(((pos[i] - 32768) * scale[i]) + offset[i])
        self.position = [pos[0], pos[1], pos[2]]

        # We don't need this but it's here as a ref for writing an exporter.
       # import math
       # unpackAngle = 360.0 / 255.0
       # longitude = float(normal / 256 ) * unpackAngle
       # latitude = (normal & 255) * unpackAngle
       # norm = [0,0,0]
       # norm[0] = math.cos(longitude) * math.sin(latitude)
       # norm[1] = math.sin(longitude) * math.sin(latitude)
       # norm[2] = math.cos(latitude)
       # self.normal = norm

    def dump (self):
        print "vertex position: ",self.position
        print "vertex normal: ",self.normal


class TAN_Surface:
    # ident = 541999444 = "TAN "
    #Header Structure    #item of data file, size & type,   description.
    ident = ""           #item   0    int but read as 4s string to convert to alpha, used to identify the file (see above).
    name = ""            #item   1    1-64 64 char, the surface (mesh) name.
    numFrames = 0        #item  65    int, number of animation frames in this surface, usually 1.
    numVerts = 0         #item  66    int, number of verts.
    minLod = 0           #item  67    int, unknown.
    numTriangles = 0     #item  68    int, number of triangles.
    ofsTriangles = 0     #item  69    int, offset for triangle 3 vert_index data.
    ofsCollapseMap = 0   #item  70    int, offset where Collapse Map begins, NumVerts * int.
    ofsUVs = 0           #item  71    int, offset for Texture UV data.
    ofsVerts = 0         #item  72    int, offset for VERTICES data.
    ofsEnd = 0           #item  73    int, next Surface data follows ex: (header) ofsSurfaces + (1st surf) ofsEnd = 2nd surface offset.

    binary_format="<4s64c9i" #little-endian (<), see #item descriptions above.

    def __init__ (self):
        self.ident = ""
        self.name = ""
        self.numFrames = 0
        self.numVerts = 0
        self.minLod = 0
        self.numTriangles = 0
        self.ofsTriangles = 0
        self.ofsCollapseMap = 0
        self.ofsUVs = 0
        self.ofsVerts = 0
        self.ofsEnd = 0

    def load (self, file, Component, frame_scale, frame_offset, message):
        this_offset = file.tell() #Get current file read position
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        name = file.name.rsplit("\\", 1)[1]
        name = name.split(".")[0]

        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.ident = data[0] # TAN ident = 541999444, we already checked this in the header.
        self.name = CString(data, 64, 1)
        # Update the Component name by adding its material name at the end.
        # This is needed to use that material name later to get its skin texture from the .tik file.
        Component.shortname = Component.shortname + "_" + self.name
        comp_name = Component.name
        message = check4skin(file, Component, self.name, message)
        # Now setup the ModelComponentList using the Component's updated name.
        editor.ModelComponentList[comp_name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}

        self.numFrames = data[65]
        self.numVerts = data[66]
        self.minLod = data[67]
        self.numTriangles = data[68]
        self.ofsTriangles = data[69]
        self.ofsCollapseMap = data[70]
        self.ofsUVs = data[71]
        self.ofsVerts = data[72]
        self.ofsEnd = data[73]

        # Load Tex Coords
        if logging == 1:
            tobj.logcon ("-----------------------------")
            tobj.logcon ("Vert UV's, numVerts: " + str(self.numVerts))
            tobj.logcon ("-----------------------------")
        tex_coords = []
        file.seek(this_offset + self.ofsUVs,0)
        for i in xrange(0, self.numVerts):
            tex_coord = TAN_TexCoord()
            tex_coord.load(file)
            tex_coords.append(tex_coord)
            if logging == 1:
                tobj.logcon ("vert " + str(i) + " U,V: " + str(tex_coord.uv))
        if logging == 1:
            tobj.logcon ("")

        # Load tris
        if logging == 1:
            tobj.logcon ("-----------------------------------")
            tobj.logcon ("Triangle vert_indexes, numTriangles: " + str(self.numTriangles))
            tobj.logcon ("-----------------------------------")
        file.seek(this_offset + self.ofsTriangles,0)
        Tris = ''
        size = Component.dictspec['skinsize']
        for i in xrange(0, self.numTriangles):
            tri = TAN_Triangle()
            tri.load(file)
            if logging == 1:
                tobj.logcon ("tri " + str(i) + " " + str(tri.indices))
            tri = tri.indices
            for j in xrange(3):
                Tris = Tris + struct.pack("Hhh", tri[j], tex_coords[tri[j]].uv[0]*size[0], tex_coords[tri[j]].uv[1]*size[1])
        Component['Tris'] = Tris
        if logging == 1:
            tobj.logcon ("")

        # load frames
        if logging == 1:
            tobj.logcon ("-----------------------------")
            tobj.logcon ("Frame vertices, numFrames: " + str(self.numFrames))
            tobj.logcon ("-----------------------------")
        framesgroup = quarkx.newobj('Frames:fg')
        framesgroup['type'] = chr(1)
        file.seek(this_offset + self.ofsVerts,0)
        for i in xrange(0, self.numFrames):
            if i == 0:
                frame = quarkx.newobj(name + ' baseframe:mf')
            else:
                frame = quarkx.newobj(name + ' frame ' + str(i) + ':mf')
            if logging == 1:
                tobj.logcon (frame.shortname + ", numVerts: " + str(self.numVerts) + " [x,y,z position] normal")
                tobj.logcon ("  frame_scale : " + str(frame_scale))
                tobj.logcon ("  frame_offset: " + str(frame_offset))
                tobj.logcon ("-----------------------")
            mesh = ()
            for j in xrange(0, self.numVerts):
                Vert = TAN_XyzNormal()
                Vert.load(file, frame_scale, frame_offset)
                if logging == 1:
                    tobj.logcon ("vert " + str(j) + ": " + str(Vert.position) + " " + str(Vert.normal))
                x,y,z = Vert.position
                mesh = mesh + (x,y,z)
            if logging == 1:
                tobj.logcon ("")
            frame['Vertices'] = mesh
            framesgroup.appenditem(frame)
        Component.appenditem(framesgroup)

        # Ignore CollapseMap data for now. Gives which vertex_indexes to use to create a low poly count model, Level Of Detail (LoD).
    #    file.seek(this_offset + self.ofsCollapseMap,0)
    #    for i in xrange(0, self.numVerts):
    #        file.read(4) # 1 int.

        return message

    def dump(self):
            tobj.logcon ("ident: " + self.ident)
            tobj.logcon ("name: " + self.name)
            tobj.logcon ("numFrames: " + str(self.numFrames))
            tobj.logcon ("numVerts: " + str(self.numVerts))
            tobj.logcon ("minLod: " + str(self.minLod))
            tobj.logcon ("numTriangles: " + str(self.numTriangles))
            tobj.logcon ("ofsTriangles: " + str(self.ofsTriangles))
            tobj.logcon ("ofsCollapseMap: " + str(self.ofsCollapseMap))
            tobj.logcon ("ofsUVs: " + str(self.ofsUVs))
            tobj.logcon ("ofsVerts: " + str(self.ofsVerts))
            tobj.logcon ("ofsEnd: " + str(self.ofsEnd))


class tan_obj:
    # TAN ident = 541999444 version = 2 Same for Alice, EF2 and FAKK2.
    #Header Structure    #item of data file, size & type,   description.
    ident = ""           #item   0    int but read as 4s string to convert to alpha, used to identify the file (see above).
    version = 0          #item   1    int, version number of the file (see above).
    name = ""            #item   2    2-65 64 char, the models path and full name.
    numFrames = 0        #item  66    int, number of animation frames, should be same as numFrames in every Surface Header.
    numTags = 0          #item  67    int, number of tags.
    numSurfaces = 0      #item  68    int, number of surfaces (meshes).
    totalTime = 0        #item  69    float, total length of animation duration time in seconds.
    local_X = 0          #item  70    float, x coordinate.
    local_Y = 0          #item  71    float, y coordinate.
    local_Z = 0          #item  72    float, z coordinate.
    totalDelta = [local_X, local_Y, local_Z] # Above values, use unknown.
    ofsFrames = 0        #item  73    int, the file offset for the frames data (for the 1st frame).
    ofsSurfaces = 0      #item  74    int, the file offset for the surface (mesh) data (for the 1st surface).
    ofsTags = []         #item  75-90 16 int, the file offsets for the 16 sets of tags data, if less they are set to zero.
    ofsEnd = 0           #item  91    int, end (or length) of the file.

    binary_format="<4si64c3i4f19i"  #little-endian (<), see #item descriptions above.

    #tan data objects
    frames = []
    tags = []
    surfaceList = []
    ComponentList = [] # QuArK list to place our Components into when they are created.

    def __init__ (self):
        self.ident = ""
        self.version = 0
        self.name = ""
        self.numFrames = 0
        self.numTags = 0
        self.numSurfaces = 0
        self.totalTime = 0
        self.local_X = 0
        self.local_Y = 0
        self.local_Z = 0
        self.totalDelta = [self.local_X, self.local_Y, self.local_Z]
        self.ofsFrames = 0
        self.ofsSurfaces = 0
        self.ofsTags = []
        self.ofsEnd = 0

        self.frames = []
        self.tags = []
        self.surfaceList = []
        self.ComponentList = []

    def load (self, file):
        global used_skin_names
        # file.name is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        # FullPathName is the full path and the full file name being imported with forward slashes.
        FullPathName = file.name.replace("\\", "/")
        # FolderPath is the full path to the model's folder w/o slash at end.
        FolderPath = FullPathName.rsplit("/", 1)
        FolderPath, ModelName = FolderPath[0], FolderPath[1]
        # ModelFolder is just the model file's FOLDER name without any path, slashes or the ".tan" file name.
        # Probably best to use ModelFolder to keep all the tags and bones (if any) together for a particular model.
        ModelFolder = FolderPath.rsplit("/", 1)[1]
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        # To avoid dupeicate skin names from being imported, we change the name.
        used_skin_names = []
        for item in editor.Root.subitems:
            if item.type == ":mc" and not item.name.startswith(ModelFolder + "_" + ModelName):
                for skin in item.dictitems['Skins:sg'].subitems:
                    used_skin_names = used_skin_names + [skin.shortname]

        # "data" is all of the header data amounts.
        self.ident = data[0]
        self.version = data[1]

        # TAN ident = 541999444 version = 2
        if self.ident != "TAN ": # Not a valid .tan file.
            quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
            quarkx.msgbox("Invalid model.\nEditor can not import it.\n\nTAN ident = TAN version = 2\n\nFile has:\nident = " + self.ident + " version = " + str(self.version), quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return None

        self.name = CString(data, 64, 2)
        self.name = self.name.split(".")[0]
        self.numFrames = data[66]
        self.numTags = data[67]
        self.numSurfaces = data[68]
        self.totalTime = data[69]
        self.local_X = data[70]
        self.local_Y = data[71]
        self.local_Z = data[72]
        self.totalDelta = [self.local_X, self.local_Y, self.local_Z]
        self.ofsFrames = data[73]
        self.ofsSurfaces = data[74]
        self.ofsTags = []
        nbr = 16 + 75 # The above data items = 75.
        for i in xrange(75, nbr):
            self.ofsTags = self.ofsTags + [data[i]]
        self.ofsEnd = data[91]

        #load the frames
        file.seek(self.ofsFrames,0)
        for i in xrange(0, self.numFrames):
            self.frames.append(TAN_Frame())
            self.frames[i].load(file)
          #  print "TAN Frame " + str(i)
          #  self.frames[i].dump()

        #load the tags, not sure what to do with these. Seems only FAKK2 uses them sometimes.
        tagNames = []
        tagData = []
        tagObjects = []
        for i in xrange(0, self.numFrames):
            curTagName = TAN_TagName()
            for j in xrange(0, self.numTags):
                file.seek(self.ofsTags[j],0)
                curTagName.load(file)
                tagNames.append(curTagName.name)
              #  curTagName.dump()
                curTag = TAN_TagData()
                tagData.append(curTag)
                tagData[j].load(file)
              #  tagData[j].dump()
                if i == 1:
                    tagObject = CreateTagObject(ModelFolder, tagNames[j], curTag)
                    tagObjects.append(tagObject)
                    
                  #  in coordsys world tagObject.transform = curTag.GetMatrix()
                    
                  #  animate on
                  #  (
                  #      at time 0
                  #      (
                  #          in coordsys world tagObject.transform = curTag.GetMatrix()
                  #      )
                  #  )
                else:
                    pass
                  #  animate on
                  #  (
                  #      at time (i-1)
                  #      (
                  #          in coordsys world tagObjects[j].transform = curTag.GetMatrix()
                  #      )
                  #  )
        self.tags = [tagNames, tagData, tagObjects]

        #load the surfaces (meshes) ****** QuArK basic, empty Components are made and passed along here to be completed. ******
        next_surf_offset = 0
        message = ""
        for i in xrange(0, self.numSurfaces):
            if logging == 1:
                tobj.logcon ("=====================")
                tobj.logcon ("PROCESSING SURFACE " + str(i))
                tobj.logcon ("=====================")
                tobj.logcon ("")
            file.seek(self.ofsSurfaces + next_surf_offset,0)
            surface = TAN_Surface()
            Comp_name = ModelFolder + "_" + self.name + str(i+1)
            Component = quarkx.newobj(Comp_name + ':mc')
            Component['skinsize'] = (256, 256)
            Component['show'] = chr(1)
            sdogroup = quarkx.newobj('SDO:sdo')
            Component.appenditem(sdogroup)
            skingroup = quarkx.newobj('Skins:sg')
            skingroup['type'] = chr(2)
            Component.appenditem(skingroup)
    #        surface.offsetStart = self.ofsSurfaces + next_surf_offset # Used to add to this surface's header offsets to get its data sections.
            message = surface.load(file, Component, self.frames[0].scale, self.frames[0].offset, message)
            next_surf_offset = next_surf_offset + surface.ofsEnd
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("----------------")
                tobj.logcon ("Surface " + str(i) + " Header")
                tobj.logcon ("----------------")
                surface.dump()
                tobj.logcon ("")
            self.surfaceList.append(surface)
            self.ComponentList.append(Component)

        return self, message

    def dump(self):
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + self.ident)
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("name: " + self.name)
            tobj.logcon ("number of frames: " + str(self.numFrames))
            tobj.logcon ("number of tags: " + str(self.numTags))
            tobj.logcon ("number of meshes: " + str(self.numSurfaces))
            tobj.logcon ("anim time duration: " + str(self.totalTime))
            tobj.logcon ("Delta position: " + str(self.totalDelta))
            tobj.logcon ("offset for frames data: " + str(self.ofsFrames))
            tobj.logcon ("offset for meshes data: " + str(self.ofsSurfaces))
            tobj.logcon ("offsets for tags data: " + str(self.ofsTags))
            tobj.logcon ("offset for end (or length) of file: " + str(self.ofsEnd))
            tobj.logcon ("")

######################################################
# Import functions
######################################################
def check_skin_name(skin_name):
    test_name = skin_name.split(".")
    count = 0
    if test_name[0] in used_skin_names:
        for name in used_skin_names:
            if name == test_name[0]:
                count += 1
        skin_name = test_name[0] + "Dupe" + str(count) + "." + test_name[1]
    return skin_name

def check4skin(file, Component, material_name, message):
    # Try to locate and load Component's skin textures.
    ImageTypes = [".ftx", ".tga", ".jpg", ".bmp", ".png", ".dds"]
    if logging == 1:
        tobj.logcon ("----------------------------------------------------------")
        tobj.logcon ("Skins group data: " + Component.name + " skins")
        tobj.logcon ("----------------------------------------------------------")
    path = file.name
    if path.find("models\\") != -1:
        pass
    else:
        message = message + "Invalid folders setup !!!\r\nTo import a model you MUST have its folder WITHIN another folder named 'models'\r\nalong with its '.tik' file to locate its skin texture name in.\r\nWill now try to find a texture file in the models folder.\r\n\r\n"
    skin_name = None
    path = path.rsplit('\\', 1)
    model_name = path[1]
    path = skin_path = path[0]
    while 1:
        files = os.listdir(path)
        check_files = []
        for file in files:
            if file.endswith(".tik") and not file.endswith(".tiki"):
                check_files.append(file)
        if check_files != []:
            for file in check_files:
                #read the file in
                read_tik_file = open(path + "\\" + file,"r")
                filelines = read_tik_file.readlines()
                read_tik_file.close()
                foundmodel = None
                count = 0
                for line in filelines:
                    if line.find(model_name) != -1:
                        foundmodel = 1
                    if foundmodel is not None and line.find(material_name) != -1:
                        items = line.split(" ")
                        for item in items:
                            for type in ImageTypes:
                                if item.find(type) != -1:
                                    file_skin_name = item
                                    skin_name = item.split(".")[0]
                                    tik_file = path + "\\" + file
                                    break
                    if skin_name is not None or count == 20:
                        break
                    count = count + 1
                if skin_name is not None:
                    break
        if path.endswith("\\models") or skin_name is not None:
            break
        path = path.rsplit('\\', 1)[0]
    path = skin_path # Reset to the full path to try and find the skin texture.
    found_skin_file = None
    if skin_name is not None:
        while 1:
            files = os.listdir(path)
            for file in files:
                for type in ImageTypes:
                    if os.path.isfile(path + "\\" + skin_name + type): # We found the skin texture file.
                        found_skin_file = path + "\\" + skin_name + type
                        new_skin_name = check_skin_name(skin_name)
                        skin = quarkx.newobj(new_skin_name + type)
                        image = quarkx.openfileobj(found_skin_file)
                        skin['Image1'] = image.dictspec['Image1']
                        Component['skinsize'] = skin['Size'] = image.dictspec['Size']
                        Component.dictitems['Skins:sg'].appenditem(skin)
                        if logging == 1:
                            tobj.logcon (skin.name)
                        break
                if found_skin_file is not None:
                    break
            if path.endswith("\\models") or found_skin_file is not None:
                if found_skin_file is None:
                    message = message + "The .tik file:\r\n  " + tik_file + "\r\nshows a texture name: " + file_skin_name + "\r\nbut cound not locate any type of skin texture named: " + skin_name + "\r\nNo texture loaded for Component: " + Component.shortname + "\r\n\r\n"
                break
            path = path.rsplit('\\', 1)[0]
    else: # Last effort, try to find and load any skin texture files in the models folder.
        files = os.listdir(path)
        skinsize = [0, 0]
        skingroup = Component.dictitems['Skins:sg']
        for file in files:
            for type in ImageTypes:
                if file.endswith(type):
                    found_skin_file = path + "\\" + file
                    new_skin_name = check_skin_name(file)
                    skin = quarkx.newobj(new_skin_name)
                    image = quarkx.openfileobj(found_skin_file)
                    skin['Image1'] = image.dictspec['Image1']
                    skin['Size'] = size = image.dictspec['Size']
                    if size[0] > skinsize[0] and size[1] > skinsize[1]:
                        skinsize[0] = size[0]
                        skinsize[1] = size[1]
                        Component['skinsize'] = skin['Size']
                    skingroup.appenditem(skin)
                    if logging == 1:
                        tobj.logcon (skin.name)
        if found_skin_file is None:
            message = message + "Cound not locate any type of skin textures for Component:\r\n  " + Component.shortname + "\r\n\r\n"
    if logging == 1:
        tobj.logcon ("")
    return message


def CreateTagObject(ModelFolder, tagName, curTag):
    tagObject = quarkx.newobj(ModelFolder + '_' + tagName + ':tag')
  #  local verts = #([0, 0, 0], [0, -1, 0], [2, 0, 0])
  #  local tri = #([1, 2, 3])
  #  local tagObject = mesh name:name vertices:verts faces:tri pos:(tanTag.GetTranslation())

  #  in coordsys local tagObject.rotation = tanTag.GetRotation()
    
    return tagObject


############################
# CALL TO IMPORT MESH (.tan) FILE
############################
def load_tan(filename):
    global progressbar, tobj, logging, Strings
    #read the file in
    file = open(filename, "rb")
    tan = tan_obj()
    MODEL, message = tan.load(file)
    file.close()
    if logging == 1:
        tan.dump() # Writes the file Header last to the log for comparison reasons.
    if MODEL is None:
        return None
    
    return MODEL.ComponentList, message


##########################
# CALLS TO IMPORT MESH (.tan) FILE
##########################

def import_tan_model(filename):

    ComponentList, message = load_tan(filename) # Loads the model.
    if ComponentList is None:
        return None
    return ComponentList, message


def loadmodel(root, filename, gamename, nomessage=0):
    #   Loads the model file: root is the actual file,
    #   filename is the full path and name of the .tan file selected,
    #   for example:  C:\FAKK2\fakk\models\monster\claw\claw.tan
    #   gamename is None.

    global editor, progressbar, tobj, logging, importername, textlog, Strings
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
    if basepath is None:
        return

    logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

    ### Lines below here loads the model into the opened editor's current model.
    ComponentList, message = import_tan_model(filename)

    if ComponentList is None:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        quarkx.msgbox("Invalid .tan model.\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        try:
            progressbar.close()
        except:
            pass
        return

    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        md2fileobj = quarkx.newfileobj("New model.md2")
        md2fileobj['FileName'] = 'New model.qkl'
        for Component in ComponentList:
            editor.Root.appenditem(Component)
        md2fileobj['Root'] = editor.Root.name
        md2fileobj.appenditem(editor.Root)
        md2fileobj.openinnewwindow()
    else: # Imports a model properly from within the editor.
        undo = quarkx.action()
        for Component in ComponentList:
            undo.put(editor.Root, Component)
            editor.Root.currentcomponent = Component
            compframes = editor.Root.currentcomponent.findallsubitems("", ':mf')   # get all frames
            for compframe in compframes:
                compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.

            try:
                progressbar.close()
                ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.
            except:
                pass

            # This needs to be done for each component or bones will not work if used in the editor.
            quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
        editor.ok(undo, str(len(ComponentList)) + " .tan Components imported")

        if message != "":
            message = message + "================================\r\n\r\n"
            message = message + "You need to find and supply the proper texture(s) and folder(s) above.\r\n"
            message = message + "Extract the folder(s) and file(s) to the 'game' folder.\r\n\r\n"
            message = message + "If a texture does not exist it may be listed else where in a .tik and\or .shader file.\r\n"
            message = message + "If so then you need to track it down, extract the files and folders to their proper location.\r\n\r\n"
            message = message + "Once this is done, then delete the imported components and re-import the model."
            quarkx.textbox("WARNING", "Missing Skin Textures:\r\n\r\n================================\r\n" + message, quarkpy.qutils.MT_WARNING)

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_tan_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".tan Alice\EF2\FAKK2 Importer", ".tan file", "*.tan", loadmodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_tan_import.py,v $
# Revision 1.10  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.9  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.8  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.7  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.6  2010/08/03 22:40:06  cdunde
# Logging and comments update.
#
# Revision 1.5  2010/07/31 22:41:35  cdunde
# Commented out unused file read data.
#
# Revision 1.4  2010/07/28 04:27:13  cdunde
# File ident update.
#
# Revision 1.3  2010/07/08 18:05:15  danielpharos
# Removed unused variable.
#
# Revision 1.2  2010/07/08 18:04:04  danielpharos
# Removed left-over MD2 constants, and added proper function for CString converting.
#
# Revision 1.1  2010/07/07 03:35:28  cdunde
# Setup importers for Alice, EF2 and FAKK2 .skb, .ska and
# .tan models (static and animated) with bone and skin support.
#
#
