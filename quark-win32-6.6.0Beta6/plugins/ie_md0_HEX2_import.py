# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for HexenII .mdl model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md0_HEX2_import.py,v 1.2 2012/10/13 21:54:33 cdunde Exp $


Info = {
   "plug-in":       "ie_md0_HEX2_import",
   "desc":          "This script imports a HexenII file (MDL), textures, and animations into QuArK for editing.",
   "date":          "Oct. 6, 2012",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 6" }

import struct, sys, os, time, operator
import quarkx
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
editor = None
logging = 0
importername = "ie_md0_HEX2_import.py"
textlog = "HEX2_ie_log.txt"
progressbar = None
mdl = None

######################################################
# MDL Model Constants
######################################################
MDL_MAX_TRIANGLES = 2048
MDL_MAX_VERTICES = 1024
MDL_MAX_TEXCOORDS = 1024
MDL_MAX_FRAMES = 256
MDL_MAX_NORMALS = 162
MDL_MAX_SKINS = 32 # Need to find and change to correct number.
MDL_MAX_FRAMESIZE = (MDL_MAX_VERTICES * 4 + 128) # Need to find and change to correct number.

######################################################
# MDL Vector Constants
######################################################
MDL_NORMAL_VECTORS = (( -0.525731, 0.000000, 0.850651 ), ( -0.442863, 0.238856, 0.864188 ), ( -0.295242, 0.000000, 0.955423 ), ( -0.309017, 0.500000, 0.809017 ), ( -0.162460, 0.262866, 0.951056 ), ( 0.000000, 0.000000, 1.000000 ), ( 0.000000, 0.850651, 0.525731 ), ( -0.147621, 0.716567, 0.681718 ), ( 0.147621, 0.716567, 0.681718 ), ( 0.000000, 0.525731, 0.850651 ), ( 0.309017, 0.500000, 0.809017 ), ( 0.525731, 0.000000, 0.850651 ), ( 0.295242, 0.000000, 0.955423 ), ( 0.442863, 0.238856, 0.864188 ), ( 0.162460, 0.262866, 0.951056 ), ( -0.681718, 0.147621, 0.716567 ), ( -0.809017, 0.309017, 0.500000 ), ( -0.587785, 0.425325, 0.688191 ), ( -0.850651, 0.525731, 0.000000 ), ( -0.864188, 0.442863, 0.238856 ), ( -0.716567, 0.681718, 0.147621 ), ( -0.688191, 0.587785, 0.425325 ), ( -0.500000, 0.809017, 0.309017 ), ( -0.238856, 0.864188, 0.442863 ), ( -0.425325, 0.688191, 0.587785 ), ( -0.716567, 0.681718, -0.147621 ), ( -0.500000, 0.809017, -0.309017 ), ( -0.525731, 0.850651, 0.000000 ), ( 0.000000, 0.850651, -0.525731 ), ( -0.238856, 0.864188, -0.442863 ), ( 0.000000, 0.955423, -0.295242 ), ( -0.262866, 0.951056, -0.162460 ), ( 0.000000, 1.000000, 0.000000 ), ( 0.000000, 0.955423, 0.295242 ), ( -0.262866, 0.951056, 0.162460 ), ( 0.238856, 0.864188, 0.442863 ), ( 0.262866, 0.951056, 0.162460 ), ( 0.500000, 0.809017, 0.309017 ), ( 0.238856, 0.864188, -0.442863 ), ( 0.262866, 0.951056, -0.162460 ), ( 0.500000, 0.809017, -0.309017 ), ( 0.850651, 0.525731, 0.000000 ), ( 0.716567, 0.681718, 0.147621 ), ( 0.716567, 0.681718, -0.147621 ), ( 0.525731, 0.850651, 0.000000 ), ( 0.425325, 0.688191, 0.587785 ), ( 0.864188, 0.442863, 0.238856 ), ( 0.688191, 0.587785, 0.425325 ), ( 0.809017, 0.309017, 0.500000 ), ( 0.681718, 0.147621, 0.716567 ), ( 0.587785, 0.425325, 0.688191 ), ( 0.955423, 0.295242, 0.000000 ), ( 1.000000, 0.000000, 0.000000 ), ( 0.951056, 0.162460, 0.262866 ), ( 0.850651, -0.525731, 0.000000 ), ( 0.955423, -0.295242, 0.000000 ), ( 0.864188, -0.442863, 0.238856 ), ( 0.951056, -0.162460, 0.262866 ), ( 0.809017, -0.309017, 0.500000 ), ( 0.681718, -0.147621, 0.716567 ), ( 0.850651, 0.000000, 0.525731 ), ( 0.864188, 0.442863, -0.238856 ), ( 0.809017, 0.309017, -0.500000 ), ( 0.951056, 0.162460, -0.262866 ), ( 0.525731, 0.000000, -0.850651 ), ( 0.681718, 0.147621, -0.716567 ), ( 0.681718, -0.147621, -0.716567 ), ( 0.850651, 0.000000, -0.525731 ), ( 0.809017, -0.309017, -0.500000 ), ( 0.864188, -0.442863, -0.238856 ), ( 0.951056, -0.162460, -0.262866 ), ( 0.147621, 0.716567, -0.681718 ), ( 0.309017, 0.500000, -0.809017 ), ( 0.425325, 0.688191, -0.587785 ), ( 0.442863, 0.238856, -0.864188 ), ( 0.587785, 0.425325, -0.688191 ), ( 0.688191, 0.587785, -0.425325 ), ( -0.147621, 0.716567, -0.681718 ), ( -0.309017, 0.500000, -0.809017 ), ( 0.000000, 0.525731, -0.850651 ), ( -0.525731, 0.000000, -0.850651 ), ( -0.442863, 0.238856, -0.864188 ), ( -0.295242, 0.000000, -0.955423 ), ( -0.162460, 0.262866, -0.951056 ), ( 0.000000, 0.000000, -1.000000 ), ( 0.295242, 0.000000, -0.955423 ), ( 0.162460, 0.262866, -0.951056 ), ( -0.442863, -0.238856, -0.864188 ), ( -0.309017, -0.500000, -0.809017 ), ( -0.162460, -0.262866, -0.951056 ), ( 0.000000, -0.850651, -0.525731 ), ( -0.147621, -0.716567, -0.681718 ), ( 0.147621, -0.716567, -0.681718 ), ( 0.000000, -0.525731, -0.850651 ), ( 0.309017, -0.500000, -0.809017 ), ( 0.442863, -0.238856, -0.864188 ), ( 0.162460, -0.262866, -0.951056 ), ( 0.238856, -0.864188, -0.442863 ), ( 0.500000, -0.809017, -0.309017 ), ( 0.425325, -0.688191, -0.587785 ), ( 0.716567, -0.681718, -0.147621 ), ( 0.688191, -0.587785, -0.425325 ), ( 0.587785, -0.425325, -0.688191 ), ( 0.000000, -0.955423, -0.295242 ), ( 0.000000, -1.000000, 0.000000 ), ( 0.262866, -0.951056, -0.162460 ), ( 0.000000, -0.850651, 0.525731 ), ( 0.000000, -0.955423, 0.295242 ), ( 0.238856, -0.864188, 0.442863 ), ( 0.262866, -0.951056, 0.162460 ), ( 0.500000, -0.809017, 0.309017 ), ( 0.716567, -0.681718, 0.147621 ), ( 0.525731, -0.850651, 0.000000 ), ( -0.238856, -0.864188, -0.442863 ), ( -0.500000, -0.809017, -0.309017 ), ( -0.262866, -0.951056, -0.162460 ), ( -0.850651, -0.525731, 0.000000 ), ( -0.716567, -0.681718, -0.147621 ), ( -0.716567, -0.681718, 0.147621 ), ( -0.525731, -0.850651, 0.000000 ), ( -0.500000, -0.809017, 0.309017 ), ( -0.238856, -0.864188, 0.442863 ), ( -0.262866, -0.951056, 0.162460 ), ( -0.864188, -0.442863, 0.238856 ), ( -0.809017, -0.309017, 0.500000 ), ( -0.688191, -0.587785, 0.425325 ), ( -0.681718, -0.147621, 0.716567 ), ( -0.442863, -0.238856, 0.864188 ), ( -0.587785, -0.425325, 0.688191 ), ( -0.309017, -0.500000, 0.809017 ), ( -0.147621, -0.716567, 0.681718 ), ( -0.425325, -0.688191, 0.587785 ), ( -0.162460, -0.262866, 0.951056 ), ( 0.442863, -0.238856, 0.864188 ), ( 0.162460, -0.262866, 0.951056 ), ( 0.309017, -0.500000, 0.809017 ), ( 0.147621, -0.716567, 0.681718 ), ( 0.000000, -0.525731, 0.850651 ), ( 0.425325, -0.688191, 0.587785 ), ( 0.587785, -0.425325, 0.688191 ), ( 0.688191, -0.587785, 0.425325 ), ( -0.955423, 0.295242, 0.000000 ), ( -0.951056, 0.162460, 0.262866 ), ( -1.000000, 0.000000, 0.000000 ), ( -0.850651, 0.000000, 0.525731 ), ( -0.955423, -0.295242, 0.000000 ), ( -0.951056, -0.162460, 0.262866 ), ( -0.864188, 0.442863, -0.238856 ), ( -0.951056, 0.162460, -0.262866 ), ( -0.809017, 0.309017, -0.500000 ), ( -0.864188, -0.442863, -0.238856 ), ( -0.951056, -0.162460, -0.262866 ), ( -0.809017, -0.309017, -0.500000 ), ( -0.681718, 0.147621, -0.716567 ), ( -0.681718, -0.147621, -0.716567 ), ( -0.850651, 0.000000, -0.525731 ), ( -0.688191, 0.587785, -0.425325 ), ( -0.587785, 0.425325, -0.688191 ), ( -0.425325, 0.688191, -0.587785 ), ( -0.425325, -0.688191, -0.587785 ), ( -0.587785, -0.425325, -0.688191 ), ( -0.688191, -0.587785, -0.425325 ))
# Line below defines the HexenII palette to force its use later.
MDL_COLORMAP = (( 0, 0, 0), ( 0, 0, 0), ( 8, 8, 8), ( 16, 16, 16), ( 24, 24, 24), ( 32, 32, 32), (40, 40, 40), (48, 48, 48), (56, 56, 56), (64, 64, 64), (72, 72, 72), (80, 80, 80), (84, 84, 84), (88, 88, 88), (96, 96, 96), ( 104, 104, 104), ( 112, 112, 112), ( 120, 120, 120), ( 128, 128, 128), ( 136, 136, 136), ( 148, 148, 148), ( 156, 156, 156), ( 168, 168, 168), ( 180, 180, 180), ( 184, 184, 184), ( 196, 196, 196), (204, 204, 204), (212, 212, 212), (224, 224, 224), (232, 232, 232), (240, 240, 240), ( 252, 252, 252), ( 8, 8, 12), ( 16, 16, 20), ( 24, 24, 28), ( 28, 32, 36), ( 36, 36, 44), ( 44, 44, 52), ( 48, 52, 60), ( 56, 56, 68), ( 64, 64, 72), ( 76, 76, 88), (92, 92, 104), (108, 112, 128), (128, 132, 152), (152, 156, 176), (168, 172, 196), ( 188, 196, 220), ( 32, 24, 20), ( 40, 32, 28), ( 48, 36, 32), ( 52, 44, 40), ( 60, 52, 44), ( 68, 56, 52), ( 76, 64, 56), ( 84, 72, 64), ( 92, 76, 72), ( 100, 84, 76), ( 108, 92, 84), ( 112, 96, 88), ( 120, 104, 96), ( 128, 112, 100), (136, 116, 108), ( 144, 124, 112), ( 20, 24, 20), ( 28, 32, 28), ( 32, 36, 32), ( 40, 44, 40), ( 44, 48, 44), ( 48, 56, 48), ( 56, 64, 56), ( 64, 68, 64), ( 68, 76, 68), ( 84, 92, 84), ( 104, 112, 104), (120, 128, 120), (140, 148, 136), (156, 164, 152), (172, 180, 168), ( 188, 196, 184), ( 48, 32, 8), ( 60, 40, 8), ( 72, 48, 16), ( 84, 56, 20), ( 92, 64, 28), ( 100, 72, 36), ( 108, 80, 44), ( 120, 92, 52), (136, 104, 60), (148, 116, 72), (160, 128, 84), (168, 136, 92), (180, 144, 100), (188, 152, 108), (196, 160, 116), ( 204, 168, 124), ( 16, 20, 16), ( 20, 28, 20), ( 24, 32, 24), ( 28, 36, 28), ( 32, 44, 32), (36, 48, 36), (40, 56, 40), (44, 60, 44), (48, 68, 48), (52, 76, 52), (60, 84, 60), (68, 92, 64), (76, 100, 72), (84, 108, 76), (92, 116, 84), ( 100, 128, 92), ( 24, 12, 8), ( 32, 16, 8), ( 40, 20, 8), ( 52, 24, 12), ( 60, 28, 12), ( 68, 32, 12), (76, 36, 16), (84, 44, 20), (92, 48, 24), (100, 56, 28), (112, 64, 32), (120, 72, 36), (128, 80, 44), (144, 92, 56), (168, 112, 72), (192, 132, 88), (24, 4, 4), (36, 4, 4), (48, 0, 0), (60, 0, 0), (68, 0, 0), (80, 0, 0), ( 88, 0, 0), ( 100, 0, 0), ( 112, 0, 0), ( 132, 0, 0), ( 152, 0, 0), ( 172, 0, 0), ( 192, 0, 0), ( 212, 0, 0), ( 232, 0, 0), (252, 0, 0), (16, 12, 32), (28, 20, 48), (32, 28, 56), (40, 36, 68), (52, 44, 80), (60, 56, 92), (68, 64, 104), ( 80, 72, 116), ( 88, 84, 128), ( 100, 96, 140), ( 108, 108, 152), ( 120, 116, 164), ( 132, 132, 176), ( 144, 144, 188), ( 156, 156, 200), (172, 172, 212), (36, 20, 4), (52, 24, 4), (68, 32, 4), (80, 40, 0), (100, 48, 4), (124, 60, 4), (140, 72, 4), (156, 88, 8), ( 172, 100, 8), ( 188, 116, 12), ( 204, 128, 12), ( 220, 144, 16), ( 236, 160,20), ( 252, 184, 56), ( 248, 200, 80), (248, 220, 120), (20, 16, 4), ( 28, 24, 8), ( 36, 32, 8), ( 44, 40, 12), ( 52, 48, 16), ( 56, 56, 16), ( 64, 64, 20), ( 68, 72, 24), ( 72, 80, 28), ( 80, 92, 32), ( 84, 104, 40), ( 88, 116, 44), ( 92, 128, 52), ( 92, 140, 52), ( 92, 148, 56), (96, 160, 64), (60, 16, 16), (72, 24, 24), (84, 28, 28), (100, 36, 36), (112, 44, 44), (124, 52, 48), (140, 64, 56), (152, 76, 64), (44, 20, 8), ( 56, 28, 12), ( 72, 32, 16), ( 84, 40, 20), ( 96, 44, 28), ( 112, 52, 32), ( 124, 56, 40), ( 140, 64, 48), ( 24, 20, 16), ( 36, 28, 20), ( 44, 36, 28), ( 56, 44, 32), ( 64, 52, 36), ( 72, 60, 44), ( 80, 68, 48), ( 92, 76, 52), ( 100, 84, 60), ( 112, 92, 68), ( 120, 100, 72), ( 132, 112, 80), ( 144, 120, 88), ( 152, 128, 96), ( 160, 136, 104), ( 168, 148, 112), ( 36, 24, 12), ( 44, 32, 16), ( 52, 40, 20), (60, 44, 20), (72, 52, 24), (80, 60, 28), (88, 68, 28), (104, 76, 32), (148, 96, 56), (160, 108, 64), (172, 116, 72), (180, 124, 80), (192, 132, 88), (204, 140, 92), (216, 156, 108), (60, 20, 92), (100, 36, 116), (168, 72, 164), (204, 108, 192), (4, 84, 4), (4, 132, 4), (0, 180, 0), (0, 216, 0), (4, 4, 144), (16, 68, 204), (36, 132, 224), (88, 168, 232), (216, 4, 4), (244, 72, 0), (252, 128, 0), (252, 172, 24), (252, 252, 252))

######################################################
# MDL data structures
######################################################
class mdl_face:
    facesfront = 1
    vertex_index = [0, 0, 0]
    binary_format = "<4i" # little-endian (<), 4 ints.
    
    def __init__(self):
        self.facesfront = 1
        self.vertex_index = [0, 0, 0]

    def load(self, file):
        # file is the model file & full path, ex: C:\HexenII\data1\models\arrow.mdl
        # data[0] int 0 = backface, 1 = frontface, data[1],[2],[3] ints, 3 vertex indexes as integers.
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.facesfront = data[0]
        self.vertex_index[0] = data[1]
        self.vertex_index[1] = data[2]
        self.vertex_index[2] = data[3]
        return self

    def dump(self):

        print "MDL Face Structure"
        print "facesfront: ", self.facesfront
        print "vertex index: ", self.vertex_index[0]
        print "vertex index: ", self.vertex_index[1]
        print "vertex index: ", self.vertex_index[2]
        print "------------------"

class mdl_tex_coord:
    binary_format = "<3i" # little-endian (<), 3 ints.
    onseam = 0
    u = 0
    v = 0

    def __init__(self):
        self.onseam = 0
        self.u = 0
        self.v = 0

    def load(self, file):
        # file is the model file & full path, ex: C:\HexenII\data1\models\arrow.mdl
        # data[0] flag for "onseam", data[1] and data[2] ex: (169, 213), are 2D skin texture coords as integers.
        # Texture are generally divided in two pieces:
        #     one for the frontface of the model,
        #     and one for the backface.
        # The backface piece must be translated by skinwidth/2 from the frontface piece.
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.onseam = data[0]
        self.u = data[1]
        self.v = data[2]
        return self



    def dump(self):
        print "MDL Texture Coordinate Structure"
        print "texture coord onseam: ", self.onseam
        print "texture coordinate u: ", self.u
        print "texture coordinate v: ", self.v
        print "------------------"

class mdl_skin:
    skinwidth = 0
    skinheight = 0
    data = ()
    binary_format = "<%iB" % (skinwidth * skinheight) #little-endian (<), (skinwidth * skinheight) of unsigned char int

    def __init__(self):
        self.skinwidth = 0
        self.skinheight = 0
        self.data = ()
        self.binary_format = "<%iB" % (self.skinwidth * self.skinheight)

    def load(self, file, skinwidth, skinheight):
        # file is the model file & full path, ex: C:\HexenII\data1\models\arrow.mdl
        self.skinwidth = skinwidth
        self.skinheight = skinheight
        self.binary_format = "<%iB" % (self.skinwidth * self.skinheight)
        temp_data = file.read(struct.calcsize(self.binary_format))
        self.data = struct.unpack(self.binary_format, temp_data)
        return self

    def dump(self):
        print "MDL Skin"
        print "skinwidth: ", self.skinwidth
        print "skinheight: ", self.skinheight
      #  print "data: ", self.data # un-comment this line for the list of data integer color indexes of the .lmp colormap pallet.
        print "len data: ", len(self.data)
        print "--------------------"

class mdl_texture_info:
    group = 0   #item  0   int, This is the texture group setting, 0 = single, 1 = group (for animation textures)
    nb = 0 # (used in load function below), int, number of pics for an animation texture
    time = 0.0 # (used in load function below), float, time duration for each pic above
    data = None # (used in load function below), texture data, an array of nb arrays of skinwidth * skinheight elements (picture size)
    skins = []
    binary_format = "<i" #little-endian (<), 1 int for group setting

    def __init__(self):
        self.group = 0
        self.nb = 0
        self.time = 0.0
        self.data = None
        self.binary_format = "<i" #little-endian (<), 1 int for group setting, changed in load function if animation textures exist.
        self.skins = []

    def load(self, file, num_skins, skin_width, skin_height):
        # file is the model file & full path, ex: C:\HexenII\data1\models\arrow.mdl
        for i in xrange(0,num_skins):
            temp_data = file.read(struct.calcsize(self.binary_format))
            data = struct.unpack(self.binary_format, temp_data)
            self.group = data[0]
            if self.group == 0:
                #make the single skin object(s) for model
                self.skins.append(mdl_skin())
                self.skins[i].load(file, skin_width, skin_height)
                #self.skins[i].dump() # for testing only, comment out when done
            else:
                #make the animated skin objects for model
                #reset the binary data to read for the texture info section since animation textures exist.
                binary_format = "<if" #little-endian (<), 1 integer and 1 float
                temp_data = file.read(struct.calcsize(binary_format))
                data = struct.unpack(binary_format, temp_data)
                self.nb = data[0]
                self.time = data[1]
                self.skins.append(mdl_skin())
                self.skins[i].load(file, skin_width, skin_height)
                #self.skins[i].dump() # for testing only, comment out when done
        return self

    def dump(self):
        print "MDL Texture Info"
        print "group setting: ", self.group
        print "self.nb: ", self.nb
        print "self.time: ", self.time
        print "self.skins: ", self.skins
        print "==============="

class mdl_vertex:
    v = [0, 0, 0]
    normalIndex = 0
    binary_format = "<3B1B" #little-endian (<), 3  unsigned chars for coordinate, 1 unsigned char for normalIndex.

    def __init__(self):
        self.v = [0, 0, 0]
        self.normalIndex = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.v = [data[0], data[1], data[2]]
        self.normalIndex = MDL_NORMAL_VECTORS[data[3]]
        return self

    def dump(self):
        print "MDL Vertex"
        print "v: ",self.v[0], self.v[1], self.v[2]
        print "normalIndex: ", self.normalIndex
        print "===================="

class mdl_frame:
    group = 0   # int, This is the frame group setting, 0 = simple single frame, not 0 = group of frames.
    time = 0.0  # (used in load function below), float, time duration for each frame above.
    bboxmin = []
    bboxmax = []
    name = ""
    vertices = []
    frames = [] # For group of frames.
    binary_format = "<i" # little-endian (<), 1 int for group setting.

    def __init__(self):
        self.group = 0 # 0 = simple single frame, not 0 = group of frames.
        self.time = 0.0
        self.binary_format = "<i" # little-endian (<), 1 int for group setting, changed in load function of this class.
        self.bboxmin = [0.0]*3
        self.bboxmax = [0.0]*3
        self.name = ""
        self.vertices = []
        self.frames = []

    def load(self, file, num_verts):
        # file is the model file & full path, ex: C:\HexenII\data1\models\arrow.mdl
        # self.bboxmin, bouding box min
        # self.bboxmax, bouding box max
        # self.name is the frame name ex: attack1
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.group = data[0]
        if self.group == 0:
            self.bboxmin = mdl_vertex()
            self.bboxmin.load(file)
            #self.bboxmin.dump() # for testing only, comment out when done
            self.bboxmax = mdl_vertex()
            self.bboxmax.load(file)
            #self.bboxmax.dump() # for testing only, comment out when done
            temp_data = file.read(struct.calcsize(">16c"))
            data = struct.unpack(">16c", temp_data)
            self.name = "".join(data).split("\0")[0]
            for i in xrange(0,num_verts):
                self.vertices.append(mdl_vertex())
                self.vertices[i].load(file)
                #self.vertices[i].dump() # for testing only, comment out when done
        else: # HAVE DAN CHECK IF THIS IS CORRECT
            self.bboxmin = mdl_vertex()
            self.bboxmin.load(file)
            #self.bboxmin.dump() # for testing only, comment out when done
            self.bboxmax = mdl_vertex()
            self.bboxmax.load(file)
            #self.bboxmax.dump() # for testing only, comment out when done
            binary_format = "<f" #little-endian (<), 1 float for "time" till next frame.
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            self.time=data[0]
            for i in xrange(0,self.group):
                self.frames.append(mdl_frame())
                self.frames[i].bboxmin=mdl_vertex()
                self.frames[i].bboxmin.load(file)
                self.frames[i].bboxmax=mdl_vertex()
                self.frames[i].bboxmax.load(file)
                temp_data = file.read(struct.calcsize(">16c"))
                data = struct.unpack(">16c", temp_data)
                self.frames[i].name = "".join(data).split("\0")[0]
                for j in xrange(0,num_verts):
                    self.frames[i].vertices.append(mdl_vertex())
                    self.frames[i].vertices[j].load(file)
        return self

    def dump(self):
        print "MDL Frame"
        print "group: ", self.group
        print "time: ", self.time
        print "bboxmin: ", self.bboxmin
        print "bboxmax: ", self.bboxmax
        print "name: ", self.name
        print "===================="

class mdl_obj:
    # Header Structure.
    ident = 0              #item  0   int, This is used to identify the file.
    version = 0            #item  1   int, The version number of the file (Must be 8).
    scale = [0.0]*3        #item  2   3 floats, the scale factor, as a vector.
    translate = [0.0]*3    #item  3   3 floats, the translation vector.
    boundingradius = 0.0   #item  4   float, the radius of the bounding box, for collision.
    eyeposition = [0.0]*3  #item  5   3 floats, the eye's position, as a vector.
    num_skins = 0          #item  6   int, The number of skins associated with the model.
    skin_width = 0         #item  7   int, The skin width in pixels.
    skin_height = 0        #item  8   int, The skin height in pixels.
    num_verts = 0          #item  9   int, The number of vertices (constant for each frame).
    num_tris = 0           #item 10   int, The number of triangle faces (polygons).
    num_frames = 0         #item 11   int, The number of animation frames.
    synctype = 0           #item 12   int, 0 = synchron, 1 = random.
    flags = 0              #item 13   int, State flag.
    size = 0.0             #item 14   float, Don't know what this is.

    binary_format = "<2i3f3ff3f8if"  #little-endian (<), see "#item" descriptions above.

    texture_info = None

    #mdl data objects
    tex_coords = []
    faces = []
    vertices = []
    frames = []

    # Texture are generally divided in two pieces:
    #     one for the frontface of the model, and one for the backface.
    # The backface piece must be translated of skinwidth/2 from the frontface piece.
    def __init__ (self):
        self.tex_coords = [] # A list of integers, 1 for "onseam" and 2 for the s,t or u,v texture coordinates.
        self.faces = []      # A list of the triangles.
        self.vertices = []   # A list of the vertexes.
        self.frames = []     # A list of the animation frames.

    def load(self, file):
        # file is the model file & full path, ex: C:\HexenII\data1\models\arrow.mdl
        # data is all of the header data amounts.
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.ident = data[0]
        self.version = data[1]

        if (self.ident != 1330660425 or self.version != 6): # Not a valid MDL file.
            return None, self.version

        self.scale = data[2],data[3],data[4]
        self.translate = data[5],data[6],data[7]



        self.boundingradius = data[8]
        self.eyeposition = data[9],data[10],data[11]
        self.num_skins = data[12]
        self.skin_width = data[13]
        self.skin_height = data[14]
        self.num_verts = data[15]
        self.num_tris = data[16]
        self.num_frames = data[17]
        self.synctype = data[18]
        self.flags = data[19]
        self.size = data[20]

        # sets the Model Root dictspec items and flag settings for the editor.
        editor.Root['synctype_setting'] = editor.Root['synctype'] = str(self.synctype)
        editor.Root['flags_setting'] = editor.Root['flags'] = str(self.flags)

        # get the skin(s) texture information
        self.texture_info = mdl_texture_info()
        self.texture_info.load(file, self.num_skins, self.skin_width, self.skin_height)





        # load the # of raw texture coordinates data for model, some get updated later.
        for i in xrange(0,self.num_verts):
            self.tex_coords.append(mdl_tex_coord())
            self.tex_coords[i].load(file)
         #   self.tex_coords[i].dump() # for testing only, comment out when done

        #make the # of triangle faces for model
        for i in xrange(0,self.num_tris):
            self.faces.append(mdl_face())
            self.faces[i].load(file)
         #   self.faces[i].dump() # for testing only, comment out when done

        #make the # of frames for the model
        for i in xrange(0,self.num_frames):
            self.frames.append(mdl_frame())
            #make the # of vertices for each frame
            for j in xrange(0,self.num_verts):
                self.frames[i].vertices.append(mdl_vertex())

        #load the frames
        for i in xrange(0, self.num_frames):
            self.frames[i].load(file, self.num_verts)
          #  self.frames[i].dump() # for testing only, comment out when done

        return self, self.version

    def dump(self):
        global tobj, logging
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + str(self.ident))
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("scale: " + str(self.scale))
            tobj.logcon ("translate: " + str(self.translate))
            tobj.logcon ("boundingradius: " + str(self.boundingradius))
            tobj.logcon ("eyeposition: " + str(self.eyeposition))
            tobj.logcon ("number of skins: " + str(self.num_skins))
            tobj.logcon ("skin width: " + str(self.skin_width))
            tobj.logcon ("skin height: " + str(self.skin_height))
            tobj.logcon ("number of vertices per frame: " + str(self.num_verts))
            tobj.logcon ("number of faces: " + str(self.num_tris))
            tobj.logcon ("number of frames: " + str(self.num_frames))
            tobj.logcon ("synctype: " + str(self.synctype))
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("size: " + str(self.size))
            tobj.logcon ("")

######################################################
# Import functions
######################################################
def load_textures(mdl, texture_name):
    global tobj, logging
    # Checks if the model has textures specified with it.
    skinsize = (256, 256)
    skingroup = quarkx.newobj('Skins:sg')
    skingroup['type'] = chr(2)
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Skins group data: " + str(mdl.num_skins) + " skins")
        tobj.logcon ("#####################################################################")
    if int(mdl.num_skins) > 0:
        #Build the palette
        Palette=''
        for i in xrange(0, 256):
            Palette += struct.pack("BBB", MDL_COLORMAP[i][0], MDL_COLORMAP[i][1], MDL_COLORMAP[i][2])
        for i in xrange(0,mdl.num_skins):
            if mdl.num_skins == 1:
                skinname = texture_name + ".pcx"
            else:
                skinname = texture_name + " " + str(i+1) + ".pcx"
            if logging == 1:
                tobj.logcon (skinname)
            skin = quarkx.newobj(skinname)
            Padding=(int(((mdl.skin_width * 8) + 31) / 32) * 4) - (mdl.skin_width * 1)
            ImageData = ''
            for y in xrange(0,mdl.skin_height):
                for x in xrange(0,mdl.skin_width):
                    ImageData += struct.pack("B", mdl.texture_info.skins[i].data[(mdl.skin_height-y-1) * mdl.skin_width+x])
                ImageData += "\0" * Padding
            skin['Image1'] = ImageData
            skin['Pal'] = Palette
            skin['Size'] = (float(mdl.skin_width), float(mdl.skin_height))
            skingroup.appenditem(skin)
            skinsize = (mdl.skin_width, mdl.skin_height) # Used for QuArK.
          #  mdl.texture_info.skins[i].dump() # Comment out later, just prints to the console what the skin(s) are.

        return skinsize, skingroup # Used for QuArK.
    else:
        return skinsize, skingroup # Used for QuArK.
	

def animate_mdl(mdl): # The Frames Group is made here & returned to be added to the Component.
    global progressbar, tobj, logging
	######### Animate the verts through the QuArK Frames lists.
    framesgroup = quarkx.newobj('Frames:fg')

    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Frame group data: " + str(mdl.num_frames) + " frames")
        tobj.logcon ("frame: frame name")
        tobj.logcon ("#####################################################################")

    for i in xrange(0, mdl.num_frames):
        ### mdl.frames[i].name is the frame name, ex: attack1
        if logging == 1:
            tobj.logcon (str(i) + ": " + mdl.frames[i].name)

        frame = quarkx.newobj(mdl.frames[i].name + ':mf')
        mesh = ()
        #update the vertices
        for j in xrange(0,mdl.num_verts):
            x = (mdl.scale[0] * mdl.frames[i].vertices[j].v[0]) + mdl.translate[0]
            y = (mdl.scale[1] * mdl.frames[i].vertices[j].v[1]) + mdl.translate[1]
            z = (mdl.scale[2] * mdl.frames[i].vertices[j].v[2]) + mdl.translate[2]

            #put the vertex in the right spot
            mesh = mesh + (x,)
            mesh = mesh + (y,)
            mesh = mesh + (z,)

        frame['Vertices'] = mesh
        framesgroup.appenditem(frame)
        progressbar.progress()
    return framesgroup

######################################################
# Load MDL Format
######################################################
def load_mdl(mdl_filename, name):
    global progressbar, tobj, logging, Strings, mdl
    #read the file in
    file = open(mdl_filename, "rb")
    mdl = mdl_obj()
    MODEL, version = mdl.load(file)

    file.close()
    if version != 6 or MODEL is None:
        return None, None, None, None, version

    Strings[2454] = name + "\n" + Strings[2454]
    progressbar = quarkx.progressbar(2454, mdl.num_tris + (mdl.num_frames * 2))
    texture_name = mdl_filename.rsplit("\\", 1)[1]
    texture_name = texture_name.split(".")[0]
    skinsize, skingroup = load_textures(mdl, texture_name) # Calls here to make the Skins Group.

    ######### Make the faces for QuArK, the 'component.triangles', which is also the 'Tris'.
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Face group data: " + str(mdl.num_tris) + " faces")
        tobj.logcon ("face: (vert_index, U, V)")
        tobj.logcon ("#####################################################################")

    Tris = ''
    for i in xrange(0, mdl.num_tris):
        if logging == 1:
            facelist = []
            facelist = facelist + [(mdl.faces[i].vertex_index[0], mdl.tex_coords[mdl.faces[i].vertex_index[0]].u, mdl.tex_coords[mdl.faces[i].vertex_index[0]].v)]
            facelist = facelist + [(mdl.faces[i].vertex_index[1], mdl.tex_coords[mdl.faces[i].vertex_index[1]].u, mdl.tex_coords[mdl.faces[i].vertex_index[1]].v)]
            facelist = facelist + [(mdl.faces[i].vertex_index[2], mdl.tex_coords[mdl.faces[i].vertex_index[2]].u, mdl.tex_coords[mdl.faces[i].vertex_index[2]].v)]
            tobj.logcon (str(i) + ": " + str(facelist))
        
        CurrentFace = mdl.faces[i]
        for j in xrange(0, 3):
            u = mdl.tex_coords[CurrentFace.vertex_index[j]].u
            v = mdl.tex_coords[CurrentFace.vertex_index[j]].v
            if (mdl.tex_coords[CurrentFace.vertex_index[j]].onseam != 0) and (CurrentFace.facesfront == 0):
                u = u + (skinsize[0] / 2)
            Tris = Tris + struct.pack("Hhh", CurrentFace.vertex_index[j], u, v)
        progressbar.progress()

    framesgroup = animate_mdl(mdl) # Calls here to make the Frames Group.

    if logging == 1:
        mdl.dump() # Writes the file Header last to the log for comparison reasons.

    return Tris, skinsize, skingroup, framesgroup, version


########################
# To run this file
########################
def import_mdl_model(editor, mdl_filename):
    # Now we start creating our Import Component.
    # But first we check for any other "Import Component"s,
    # if so we name this one 1 more then the largest number.
    model_name = mdl_filename.rsplit("\\", 1)[1]
    name = model_name.split(".")[0]

    Tris, skinsize, skingroup, framesgroup, version = load_mdl(mdl_filename, name) # Loads the model.
    if Tris is None:
        return None, version

    # Now we can name our component that will be imported.
    Component = quarkx.newobj(name + ':mc')
    # Set it up in the ModelComponentList.
    editor.ModelComponentList[Component.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
    Component['skinsize'] = skinsize
    Component['Tris'] = Tris
    Component['show'] = chr(1)
    sdogroup = quarkx.newobj('SDO:sdo')
    Component.appenditem(sdogroup)
    Component.appenditem(skingroup)
    Component.appenditem(framesgroup)

    return Component, version


def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename and gamename is the full path to"
    "and name of the .mdl file selected."
    "For example:  C:\HexenII\data1\models\arrow.mdl"

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

    logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

    ### Lines below here loads the model into the opened editor's current model.
    Component, version = import_mdl_model(editor, filename)

    if Component is None:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        if version == 10:
            quarkx.msgbox("Invalid HexenII .mdl model.\nVersion number is " + str(version) + "\nThis is a Half-Life .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        elif version == 44:
            quarkx.msgbox("Invalid HexenII .mdl model.\nVersion number is " + str(version) + "\nThis is a Half-Life 2 .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        else:
            quarkx.msgbox("Invalid HexenII .mdl model.\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        try:
            progressbar.close()
        except:
            pass
        return

    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        md2fileobj = quarkx.newfileobj("New model.md2")
        md2fileobj['FileName'] = 'New model.qkl'
        editor.Root.appenditem(Component)
        md2fileobj['Root'] = editor.Root.name
        md2fileobj.appenditem(editor.Root)
        md2fileobj.openinnewwindow()
    else: # Imports a model properly from within the editor.
        undo = quarkx.action()
        undo.put(editor.Root, Component)
        editor.Root.currentcomponent = Component
        compframes = editor.Root.currentcomponent.findallsubitems("", ':mf') # get all frames
        for compframe in compframes:
            compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.
            progressbar.progress()

        progressbar.close()
        Strings[2454] = Strings[2454].replace(Component.shortname + "\n", "")
        ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.

        # This needs to be done for each component or bones will not work if used in the editor.
        quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
        editor.ok(undo, Component.shortname + " created")

        comp = editor.Root.currentcomponent
        skins = comp.findallsubitems("", ':sg')      # Gets the skin group.
        if len(skins[0].subitems) != 0:
            comp.currentskin = skins[0].subitems[0]      # To try and set to the correct skin.
            quarkpy.mdlutils.Update_Skin_View(editor, 2) # Sends the Skin-view for updating and center the texture in the view.
        else:
            comp.currentskin = None

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_md0_HEX2_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".mdl HexenII Importer", ".mdl file", "*.mdl", loadmodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_md0_HEX2_import.py,v $
# Revision 1.2  2012/10/13 21:54:33  cdunde
# To correct and update model settings.
#
# Revision 1.1  2012/10/09 06:22:38  cdunde
# To split up Quake1 and HexenII importers and exporters due to different skin texture image game palettes
# and to handle possible other differences in the future.
#
#
