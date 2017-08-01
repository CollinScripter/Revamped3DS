# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for Alice, EF2 and FAKK2 .tan model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_tan_export.py,v 1.5 2013/02/20 05:19:41 cdunde Exp $


Info = {
   "plug-in":       "ie_tan_exporter",
   "desc":          "This script exports a Alice, EF2 and FAKK2 file (.tan), textures, and animations from QuArK.",
   "date":          "July 13 2010",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import struct, math
import quarkx
import quarkpy.mdleditor
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
editor = None
logging = 0
exportername = "ie_tan_export.py"
textlog = "tan_ie_log.txt"
progressbar = None

# Global .tan file limits and values.
MAX_PATH = 64


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
    bboxMin = [0.0]*3  # Min. bounding box coords.
    bboxMax = [0.0]*3  # Max. bounding box coords.
    scale = [0.0]*3    # See computation of this later in the code. Need to multiply every Vertex Coord by this.
    offset = [0.0]*3   # Center of bbox = (bboxMin + bboxMax) / 2. Need to add every Vertex Coords by this.
    delta = [0.0]*3    # unknown.
    radius = 0.0       # Radius from center of bounding box.
    frameTime = 0.0    # Length of Frame in sec -> useless ...

    binary_format="<17f" #little-endian (<), 17 float

    def __init__(self):
        self.bboxMin = [0.0]*3
        self.bboxMax = [0.0]*3
        self.scale = [0.0]*3
        self.offset = [0.0]*3
        self.delta = [0.0]*3
        self.radius = 0.0
        self.frameTime = 0.04 # 25FPS (Frames Per Second).

    def save(self, file):
        # file is the model file & full path, ex: C:\FAKK2\fakk\models\animal\bird\bird_flyfast.tan
        # self.bboxMin[0] through self.bboxMin[2] ex: 0.0, -12.008715629577637, -12.461215019226074
        # self.bboxMax[3] through self.bboxMax[5] ex: 17.164989471435547, 11.542054176330566, 5.1593317985534668
        # self.scale[6] through self.scale[8] ex: 0.00026192094082944095, 0.0003593617002479732, 0.00026887230342254043
        # self.offset[9] through self.offset[11] ex: 0.0, -12.008715629577637, -12.461215019226074
        # self.delta[12] through self.delta[14] ex: -5.104235503814077e+038, -5.104235503814077e+038, -5.104235503814077e+038
        # self.radius[15] ex: 24.3747406006
        # self.frameTime[16] ex: 0.0500000007451
        tmpData = [0.0]*17
        tmpData[0] = self.bboxMin[0]
        tmpData[1] = self.bboxMin[1]
        tmpData[2] = self.bboxMin[2]
        tmpData[3] = self.bboxMax[0]
        tmpData[4] = self.bboxMax[1]
        tmpData[5] = self.bboxMax[2]
        tmpData[6] = self.scale[0]
        tmpData[7] = self.scale[1]
        tmpData[8] = self.scale[2]
        tmpData[9] = self.offset[0]
        tmpData[10] = self.offset[1]
        tmpData[11] = self.offset[2]
        tmpData[12] = self.delta[0]
        tmpData[13] = self.delta[1]
        tmpData[14] = self.delta[2]
        tmpData[15] = self.radius
        tmpData[16] = self.frameTime
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12], tmpData[13], tmpData[14], tmpData[15], tmpData[16])
        file.write(data)


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


class TAN_TexCoord:
    #Header Structure    #item of data file, size & type,   description.
    uv = [0.0]*2      # item   0-1    2 float, a vertex's U,V values.

    binary_format="<2f" #little-endian (<), 2 floats

    def __init__(self):
        self.uv = [0.0]*2

    def fill(self, Ctri):
        self.uv = [float(Ctri[1]), float(Ctri[2])]


class TAN_Triangle:
    #Header Structure    #item of data file, size & type,   description.
    indices = [0]*3      # item   0-2    3 ints, a triangles 3 vertex indexes.

    binary_format="<3i" #little-endian (<), 3 int

    def __init__(self):
        self.indices = [0]*3

    def fill(self, tri):
        self.indices = [tri[0][0], tri[1][0], tri[2][0]]

    def save(self, file):
        tmpData = [0]*3
        tmpData[0] = self.indices[0]
        tmpData[1] = self.indices[1]
        tmpData[2] = self.indices[2]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2])
        file.write(data)


class TAN_XyzNormal:
    #Header Structure    #item of data file, size & type,   description.
    position = [0]*3     # item   0-2    3 ints, a vertex's x,y,z values as unsigned short INTIGERS.
    normal = 0           # item   3      int, a vertex's normal value, as an unsigned short INTIGER.

    binary_format="<4H" #little-endian (<), 4 unsigned short ints (2 bytes each)

    def __init__(self):
        self.position = [0]*3
        self.normal = 0

    def fill(self, vert, scale, offset, frame_maxs):
        pos = [vert[0], vert[1], vert[2]]
        self.normal = 0
        for i in xrange(0, 3):
            if pos[i] == frame_maxs[i]:
                pos[i] = 65535
            else:
                pos[i] = int(((pos[i] - offset[i]) / scale[i]) + 32768)
        self.position = [pos[0], pos[1], pos[2]]

        # We don't need this but it's here as a ref for writing the exporter, may not need anyway.
       # import math
       # unpackAngle = 360.0 / 255.0
       # longitude = float(normal / 256 ) * unpackAngle
       # latitude = (normal & 255) * unpackAngle
       # norm = [0,0,0]
       # norm[0] = math.cos(longitude) * math.sin(latitude)
       # norm[1] = math.sin(longitude) * math.sin(latitude)
       # norm[2] = math.cos(latitude)
       # self.normal = norm

    def save(self, file):
        tmpData = [0]*4
        tmpData[0] = self.position[0]
        tmpData[1] = self.position[1]
        tmpData[2] = self.position[2]
        tmpData[3] = self.normal
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
        file.write(data)


class TAN_Surface:
    # ident = 541999444 = "TAN "
    #Header Structure    #item of data file, size & type,   description.
    ident = "TAN "       #item   0    int but written as 4s string to convert to alpha, used to identify the file (see above).
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

    Triangles = []
    CollapseMapVerts = []
    tex_coords = {}
    Frames = []

    binary_format="<4s%ds9i" % MAX_PATH #little-endian (<), see #item descriptions above.

    def __init__ (self):
        self.ident = "TAN "
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

        self.Triangles = []
        self.CollapseMapVerts = []
        self.tex_coords = {}
        self.Frames = []

    def fill(self, Component, surf_frames):
        surf_offset_pointer = struct.calcsize(self.binary_format) # Add its header size in bytes (see above).

        comp_frames = Component.dictitems['Frames:fg'].subitems
        self.numFrames = len(comp_frames)
        frame = comp_frames[0]
        self.numVerts = len(frame.vertices)
        if self.minLod == 0:
            self.minLod = self.numVerts
        elif self.numVerts < self.minLod:
            self.minLod = self.numVerts
        self.numTriangles = len(Component.triangles)
        self.ofsTriangles = surf_offset_pointer
        surf_offset_pointer = surf_offset_pointer + (self.numTriangles * (3 * 4))
        self.ofsCollapseMap = surf_offset_pointer
        surf_offset_pointer = surf_offset_pointer + (self.numVerts * 4)
        self.ofsUVs = surf_offset_pointer
        surf_offset_pointer = surf_offset_pointer + (self.numVerts * (2 * 4))
        self.ofsVerts = surf_offset_pointer
        surf_offset_pointer = surf_offset_pointer + (self.numFrames * (self.numVerts * (4 * 2)))
        self.ofsEnd = surf_offset_pointer

        # Fill the Triangles data and Tex UVs Coords data.
        Tris = Component.triangles
        user_skins_list = Component.dictitems['Skins:sg']
        if str(Component.dictspec['skinsize']) != str(user_skins_list.subitems[0].dictspec['Size']):
            Component['skinsize'] = user_skins_list.subitems[0].dictspec['Size']
        size = Component.dictspec['skinsize']
        for i in xrange(0, self.numTriangles):
            tri = TAN_Triangle()
            Ctri = Tris[i]
            tri.fill(Ctri)
            for j in xrange(3):
                if not Ctri[j][0] in self.tex_coords.keys():
                    tex_coord = TAN_TexCoord()
                    tex_coord.fill(Ctri[j])
                    self.tex_coords[Ctri[j][0]] = [tex_coord.uv[0]/size[0], tex_coord.uv[1]/size[1]]
            self.Triangles.append(tri)

        # Fill the CollapseMap data.
        # Gives which vertex_indexes to use to create a low poly count model, Level Of Detail (LoD). Unsupported, for now just use all vertexes.
        for i in xrange(0, self.numVerts): # Each = 1 4 byte signed "i" int.
            self.CollapseMapVerts = self.CollapseMapVerts + [i]

        # Fill the Tex UVs Coords data (already done above with the Triangles data.

        # Fill the Verts (XyzNormals for each frame) data.
        for i in xrange(0, self.numFrames):
            Verts = []
            vertices = comp_frames[i].vertices
            frame_scale = surf_frames[i].scale
            frame_offset = surf_frames[i].offset
            frame_maxs = surf_frames[i].bboxMax 
            for j in xrange(0, self.numVerts):
                vert = TAN_XyzNormal()
                Cvert = vertices[j].tuple
                vert.fill(Cvert, frame_scale, frame_offset, frame_maxs)
                Verts.append(vert)
            self.Frames.append(Verts)

    def save(self, file):
        # Write this surface (Component's) header.
        tmpData = [0]*11
        tmpData[0] = self.ident
        tmpData[1] = self.name
        tmpData[2] = self.numFrames
        tmpData[3] = self.numVerts
        tmpData[4] = self.minLod
        tmpData[5] = self.numTriangles
        tmpData[6] = self.ofsTriangles
        tmpData[7] = self.ofsCollapseMap
        tmpData[8] = self.ofsUVs
        tmpData[9] = self.ofsVerts
        tmpData[10] = self.ofsEnd
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10])
        file.write(data)

        # Write this surface (Component's) Triangles.
        for tri in self.Triangles:
            tri.save(file)

        # Write this surface (Component's) CollapseMap.
        binary_format = "<i"
        for Vert in self.CollapseMapVerts:
            data = struct.pack(binary_format, Vert)
            file.write(data)

        # Write this surface (Component's) UVs.
        binary_format = "<2f"
        for i in xrange(0, self.numVerts):
            UV = self.tex_coords[i]
            data = struct.pack(binary_format, UV[0], UV[1])
            file.write(data)

        # Write this surface (Component's) frames and Verts for each frame.
        for i in xrange(0, self.numFrames):
            Verts = self.Frames[i]
            for j in xrange(0, self.numVerts):
                vert = Verts[j]
                vert.save(file)
                


class tan_obj:
    file_pointer = 0
    header_size = 0
    # TAN ident = 541999444 version = 2 Same for Alice, EF2 and FAKK2.
    #Header Structure    #item of data file, size & type,   description.
    ident = "TAN "       #item   0    int but written as 4s string to convert to alpha, used to identify the file (see above).
    version = 2          #item   1    int, version number of the file (see above).
    name = ""            #item   2    2-65 64 char, the models path and full name.
    numFrames = 0        #item  66    int, number of animation frames, should be same as numFrames in every Surface Header.
    numTags = 0          #item  67    int, number of tags.
    numSurfaces = 0      #item  68    int, number of surfaces (meshes).
    totalTime = 0.0      #item  69    float, total length of animation duration time in seconds.
    local_X = 0.0        #item  70    float, x coordinate.
    local_Y = 0.0        #item  71    float, y coordinate.
    local_Z = 0.0        #item  72    float, z coordinate.
    ofsFrames = 0        #item  73    int, the file offset for the frames data (for the 1st frame).
    ofsSurfaces = 0      #item  74    int, the file offset for the surface (mesh) data (for the 1st surface).
    ofsTags = [0]*16     #item  75-90 16 int, the file offsets for the 16 sets of tags data, if less they are set to zero.
    ofsEnd = 0           #item  91    int, end (or length) of the file.

    binary_format="<4si%ds3i4f19i" % MAX_PATH  #little-endian (<), see #item descriptions above.

    #tan data objects
    frames = []
    tags = [] # list to place our QuArK Tags, (in our sellist) into for exporting, if their support is added.
    surfaceList = [] # list to place our QuArK Components (in our sellist) into for exporting.

    def __init__ (self):
        self.file_pointer = 0
        self.header_size = (28 * 4) + MAX_PATH # length of ident string (1 byte per character & space * 4) + 27 integer items below, 4 bytes per integer or float items below + MAX_PATH (64).
        self.ident = "TAN "
        self.version = 2
        self.name = ""
        self.numFrames = 0
        self.numTags = 0
        self.numSurfaces = 0
        self.totalTime = 0.0
        self.local_X = 0.0
        self.local_Y = 0.0
        self.local_Z = 0.0
        self.ofsFrames = 0
        self.ofsSurfaces = 0
        self.ofsTags = [0]*16
        self.ofsEnd = 0

        # tan data objects
        self.frames = []
        self.tags = []
        self.surfaceList = []

    def save(self, file):
        # Write the header.
        tmpData = [0]*29
        tmpData[0] = self.ident
        tmpData[1] = self.version
        tmpData[2] = self.name
        tmpData[3] = self.numFrames
        tmpData[4] = self.numTags
        tmpData[5] = self.numSurfaces
        tmpData[6] = self.totalTime
        tmpData[7] = self.local_X
        tmpData[8] = self.local_Y
        tmpData[9] = self.local_Z
        tmpData[10] = self.ofsFrames
        tmpData[11] = self.ofsSurfaces
        for i in range(len(self.ofsTags)):
            tmpData[12+i] = self.ofsTags[i]
        tmpData[28] = self.ofsEnd
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12], tmpData[13], tmpData[14], tmpData[15], tmpData[16], tmpData[17], tmpData[18], tmpData[19], tmpData[20], tmpData[21], tmpData[22], tmpData[23], tmpData[24], tmpData[25], tmpData[26], tmpData[27], tmpData[28])
        file.write(data)

        # Write the frames.
        for frame in self.frames:
            frame.save(file)

        # Write the tags, not supported right now, will need code update when added. Seems only FAKK2 uses them sometimes.
        if self.numTags != 0:
            pass

        # Write the surfaces.
        for surface in self.surfaceList:
            surface.save(file)


######################################################
# FILL TAN OBJ DATA STRUCTURE
######################################################
    def fill_tan_obj(self, file, QuArK_comps):
        message = ""
        self.file_pointer = self.header_size # Update our pointer for the file header that will be written first in the "save" call.
        # Fill the frames data.
        self.ofsFrames = self.file_pointer
        for i in xrange(0, self.numFrames):
            frame = TAN_Frame()
            # We need to start with the bounding box of all the components being exported combined.
            mins = [10000.0, 10000.0, 10000.0]
            maxs = [-10000.0, -10000.0, -10000.0]
            for comp in QuArK_comps:
                frames = comp.dictitems['Frames:fg'].subitems
                bounding_box = quarkx.boundingboxof(frames[i].vertices) # Uses each component's frame.vertices
                bboxMin = bounding_box[0].tuple
                bboxMax = bounding_box[1].tuple
                for j in xrange(3):
                    if bboxMin[j] < mins[j]:
                        mins[j] = bboxMin[j]
                    if bboxMax[j] > maxs[j]:
                        maxs[j] = bboxMax[j]
            for j in xrange(0, 3):
                frame.scale[j] = (maxs[j] - mins[j]) / 65536
                
            # Fill in the frame data.
            frame.bboxMin = mins
            frame.bboxMax = maxs
            frame.offset = ((quarkx.vect(mins[0], mins[1], mins[2]) + quarkx.vect(maxs[0], maxs[1], maxs[2])) / 2).tuple
            frame.radius = RadiusFromBounds(mins, maxs)
            self.frames.append(frame)
        self.file_pointer = self.ofsFrames + (self.numFrames * (17 * 4))

        # Fill the tags data if any exist, Not supported right now, code is dupe of importer code and may need changing when supported. Seems only FAKK2 uses them sometimes.
        if self.numTags != 0:
            tagNames = []
            tagData = []
            tagObjects = []
            for i in xrange(0, self.numTags):
                self.ofsTags[i] = self.file_pointer
                self.file_pointer = self.file_pointer + (MAX_PATH + (12 * 4)) # So we don't forget to update the file_pointer do it now.
                curTagName = TAN_TagName()
                curTagName.load(file)
                tagNames.append(curTagName.name)
                curTag = TAN_TagData()
                tagData.append(curTag)
                tagData[i].load(file)

                for i in xrange(0, self.numFrames):
                    if i == 1:
                        tagObject = CreateTagObject(ModelFolder, tagNames[i], curTag)
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
                      #      at time (j-1)
                      #      (
                      #          in coordsys world tagObjects[j].transform = curTag.GetMatrix()
                      #      )
                      #  )
            self.tags = [tagNames, tagData, tagObjects]

        # Fill the surfaces (meshes) data.
        self.ofsSurfaces = self.file_pointer
        for i in xrange(0, self.numSurfaces):
            surface = TAN_Surface()
            Component = QuArK_comps[i]
            name = Component.shortname
            surf_name = None
            if name.find("_material") != -1:
                chkname = name.rsplit("_", 1)
                chkname = chkname[len(chkname)-1]
                if chkname.find("material") != -1 and chkname[len(chkname)-1].isdigit():
                    surf_name = chkname
            if surf_name is None:
                surf_name = "material" + str(i+1)
                message = message + "Component: " + name + "\r\n    did not give a surface 'material' shader link to its skin textures\r\n    and will need to be added to a '.tik' file pointing to its textures.\r\nA link name: " + surf_name +"\r\n    has been written to the file for you to use in the '.tik' file for it.\r\n\r\n"
            surface.name = surf_name
            surface.fill(Component, self.frames)
            self.surfaceList.append(surface)

        return message

######################################################
# Export functions
######################################################
def CreateTagObject(ModelFolder, tagName, curTag):
    tagObject = quarkx.newobj(ModelFolder + '_' + tagName + ':tag')
  #  local verts = #([0, 0, 0], [0, -1, 0], [2, 0, 0])
  #  local tri = #([1, 2, 3])
  #  local tagObject = mesh name:name vertices:verts faces:tri pos:(tanTag.GetTranslation())

  #  in coordsys local tagObject.rotation = tanTag.GetRotation()
    
    return tagObject


def VectorLength(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def RadiusFromBounds(mins, maxs):
    corner = [0, 0, 0]
    a = 0
    b = 0

    for i in range(0, 3):
        a = abs(mins[i])
        b = abs(maxs[i])
        if a > b:
            corner[i] = a
        else:
            corner[i] = b

    return VectorLength(corner)


##########################
# CALLS TO WRITE A (.tan) FILE
##########################
def savemodel(root, filename, gamename, nomessage=0):
    #   Saves the model file: root is the actual file,
    #   filename is the full path and name of the .tan file selected,
    #   for example:  C:\FAKK2\fakk\models\monster\claw\claw.tan
    #   gamename is None.

    global editor, progressbar, tobj, logging, exportername, textlog, Strings
    import quarkpy.qutils
    editor = quarkpy.mdleditor.mdleditor
    if editor is None:
        return

    # "sellist" is a list of one or more selected model components for exporting.
    sellist = editor.layout.explorer.sellist
    if not sellist:
        quarkx.msgbox("No Components have been selected for exporting.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return
    for item in sellist:
        if not item.name.endswith(":mc"):
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select\ncomponent folders for exporting.\n\nAn item that is not\na component folder\nis in your selections.\nDeselect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

    comp_count = 0
    frame_count = []
    QuArK_comps = []
    for item in sellist:
        if item.type == ":mc":
            comp_count = comp_count + 1
            QuArK_comps.append(item)
            frame_count = frame_count + [len(item.dictitems['Frames:fg'].dictitems)]

    if len(sellist) > 1 and quarkx.setupsubset(3, "Options")["ExpComponentChecks"] == "1":
        if len(frame_count) > 1:
            for item in range(len(frame_count)):
                if item >= len(frame_count)-1:
                    break
                if frame_count[item] != frame_count[item+1]:
                    results = quarkx.msgbox("Number of selected component's frames do not match\nor some frames have identical names.\n\nDo you wish to continue with this export?", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_YES|quarkpy.qutils.MB_NO)
                    if results != 6:
                        return
                    else:
                        break

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    file = open(filename, "wb")
    tan = tan_obj()
    tan.name = filename.rsplit("\\", 1)[1]
    tan.numFrames = frame_count[0]
    tan.numSurfaces = comp_count
    tan.totalTime = tan.numFrames * 0.04 # 25FPS (Frames Per Second).

    # Fill the needed data for exporting.
    message = tan.fill_tan_obj(file, QuArK_comps)

    #actually write it to disk
    tan.save(file)
    file.close()

    add_to_message = "Any used skin textures that are a\n.dds, .ftx, .tga, .png, .jpg or .bmp\nmay need to be copied to go with the model"
    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

    if message != "":
        quarkx.textbox("WARNING", "Missing Skin Texture Links:\r\n\r\n================================\r\n" + message, quarkpy.qutils.MT_WARNING)

### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".tan Alice\EF2\FAKK2 Exporter", ".tan file", "*.tan", savemodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_tan_export.py,v $
# Revision 1.5  2013/02/20 05:19:41  cdunde
# Fix for sometimes incorrect skinsize being used.
#
# Revision 1.4  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.3  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.2  2010/08/09 00:50:28  cdunde
# Removed unused code items and updated comments.
#
# Revision 1.1  2010/08/03 22:44:42  cdunde
# Setup exporter for Alice, EF2 and FAKK2 .tan models (static and animated), tags not supported at this time.
#
#
