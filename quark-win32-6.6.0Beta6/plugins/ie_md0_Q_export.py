# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for Quake .mdl model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md0_Q_export.py,v 1.6 2012/10/13 21:54:33 cdunde Exp $


Info = {
   "plug-in":       "ie_md0_Q_export",
   "desc":          "This script exports a Quake file (MDL), textures, and animations from QuArK.",
   "date":          "March 23, 2010",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import struct, sys, os, time, operator, math
import quarkx
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
editor = None
logging = 0
exportername = "ie_md0_Q_export.py"
textlog = "Qmdl_ie_log.txt"
progressbar = None
g_scale = 1.0

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
# Line below defines the Quake1 palette to force its use later.
MDL_COLORMAP = (( 0, 0, 0), ( 15, 15, 15), ( 31, 31, 31), ( 47, 47, 47), ( 63, 63, 63), ( 75, 75, 75), ( 91, 91, 91), (107, 107, 107), (123, 123, 123), (139, 139, 139), (155, 155, 155), (171, 171, 171), (187, 187, 187), (203, 203, 203), (219, 219, 219), (235, 235, 235), ( 15, 11, 7), ( 23, 15, 11), ( 31, 23, 11), ( 39, 27, 15), ( 47, 35, 19), ( 55, 43, 23), ( 63, 47, 23), ( 75, 55, 27), ( 83, 59, 27), ( 91, 67, 31), ( 99, 75, 31), (107, 83, 31), (115, 87, 31), (123, 95, 35), (131, 103, 35), (143, 111, 35), ( 11, 11, 15), ( 19, 19, 27), ( 27, 27, 39), ( 39, 39, 51), ( 47, 47, 63), ( 55, 55, 75), ( 63, 63, 87), ( 71, 71, 103), ( 79, 79, 115), ( 91, 91, 127), ( 99, 99, 139), (107, 107, 151), (115, 115, 163), (123, 123, 175), (131, 131, 187), (139, 139, 203), ( 0, 0, 0), ( 7, 7, 0), ( 11, 11, 0), ( 19, 19, 0), ( 27, 27, 0), ( 35, 35, 0), ( 43, 43, 7), ( 47, 47, 7), ( 55, 55, 7), ( 63, 63, 7), ( 71, 71, 7), ( 75, 75, 11), ( 83, 83, 11), ( 91, 91, 11), ( 99, 99, 11), (107, 107, 15), ( 7, 0, 0), ( 15, 0, 0), ( 23, 0, 0), ( 31, 0, 0), ( 39, 0, 0), ( 47, 0, 0), ( 55, 0, 0), ( 63, 0, 0), ( 71, 0, 0), ( 79, 0, 0), ( 87, 0, 0), ( 95, 0, 0), (103, 0, 0), (111, 0, 0), (119, 0, 0), (127, 0, 0), ( 19, 19, 0), ( 27, 27, 0), ( 35, 35, 0), ( 47, 43, 0), ( 55, 47, 0), ( 67, 55, 0), ( 75, 59, 7), ( 87, 67, 7), ( 95, 71, 7), (107, 75, 11), (119, 83, 15), (131, 87, 19), (139, 91, 19), (151, 95, 27), (163, 99, 31), (175, 103, 35), ( 35, 19, 7), ( 47, 23, 11), ( 59, 31, 15), ( 75, 35, 19), ( 87, 43, 23), ( 99, 47, 31), (115, 55, 35), (127, 59, 43), (143, 67, 51), (159, 79, 51), (175, 99, 47), (191, 119, 47), (207, 143, 43), (223, 171, 39), (239, 203, 31), (255, 243, 27), ( 11, 7, 0), ( 27, 19, 0), ( 43, 35, 15), ( 55, 43, 19), ( 71, 51, 27), ( 83, 55, 35), ( 99, 63, 43), (111, 71, 51), (127, 83, 63), (139, 95, 71), (155, 107, 83), (167, 123, 95), (183, 135, 107), (195, 147, 123), (211, 163, 139), (227, 179, 151), (171, 139, 163), (159, 127, 151), (147, 115, 135), (139, 103, 123), (127, 91, 111), (119, 83, 99), (107, 75, 87), ( 95, 63, 75), ( 87, 55, 67), ( 75, 47, 55), ( 67, 39, 47), ( 55, 31, 35), ( 43, 23, 27), ( 35, 19, 19), ( 23, 11, 11), ( 15, 7, 7), (187, 115, 159), (175, 107, 143), (163, 95, 131), (151, 87, 119), (139, 79, 107), (127, 75, 95), (115, 67, 83), (107, 59, 75), ( 95, 51, 63), ( 83, 43, 55), ( 71, 35, 43), ( 59, 31, 35), ( 47, 23, 27), ( 35, 19, 19), ( 23, 11, 11), ( 15, 7, 7), (219, 195, 187), (203, 179, 167), (191, 163, 155), (175, 151, 139), (163, 135, 123), (151, 123, 111), (135, 111, 95), (123, 99, 83), (107, 87, 71), ( 95, 75, 59), ( 83, 63, 51), ( 67, 51, 39), ( 55, 43, 31), ( 39, 31, 23), ( 27, 19, 15), ( 15, 11, 7), (111, 131, 123), (103, 123, 111), ( 95, 115, 103), ( 87, 107, 95), ( 79, 99, 87), ( 71, 91, 79), ( 63, 83, 71), ( 55, 75, 63), ( 47, 67, 55), ( 43, 59, 47), ( 35, 51, 39), ( 31, 43, 31), ( 23, 35, 23), ( 15, 27, 19), ( 11, 19, 11), ( 7, 11, 7), (255, 243, 27), (239, 223, 23), (219, 203, 19), (203, 183, 15), (187, 167, 15), (171, 151, 11), (155, 131, 7), (139, 115, 7), (123, 99, 7), (107, 83, 0), ( 91, 71, 0), ( 75, 55, 0), ( 59, 43, 0), ( 43, 31, 0), ( 27, 15, 0), ( 11, 7, 0), ( 0, 0, 255), ( 11, 11, 239), ( 19, 19, 223), ( 27, 27, 207), ( 35, 35, 191), ( 43, 43, 175), ( 47, 47, 159), ( 47, 47, 143), ( 47, 47, 127), ( 47, 47, 111), ( 47, 47, 95), ( 43, 43, 79), ( 35, 35, 63), ( 27, 27, 47), ( 19, 19, 31), ( 11, 11, 15), ( 43, 0, 0), ( 59, 0, 0), ( 75, 7, 0), ( 95, 7, 0), (111, 15, 0), (127, 23, 7), (147, 31, 7), (163, 39, 11), (183, 51, 15), (195, 75, 27), (207, 99, 43), (219, 127, 59), (227, 151, 79), (231, 171, 95), (239, 191, 119), (247, 211, 139), (167, 123, 59), (183, 155, 55), (199, 195, 55), (231, 227, 87), (127, 191, 255), (171, 231, 255), (215, 255, 255), (103, 0, 0), (139, 0, 0), (179, 0, 0), (215, 0, 0), (255, 0, 0), (255, 243, 147), (255, 247, 199), (255, 255, 255), (159, 91, 83))

######################################################
# Exporter Functions section
######################################################
#q_math
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

######################################################
# MDL data structures
######################################################
class mdl_face:

    tris_list = [] # A list of integers. 0 = backface, 1 = frontface, data[1],[2],[3] ints, 3 vertex indexes as integers.
    binary_format = "<4i" # little-endian (<), 4 ints.
    
    def __init__(self):
        self.tris_list = []

    def save(self, file, num_tris):
        for i in xrange(0, num_tris):
            data = struct.pack(self.binary_format, self.tris_list[i][0], self.tris_list[i][1], self.tris_list[i][2], self.tris_list[i][3])
            file.write(data)

    def dump(self):
        for i in xrange(0, len(self.tris_list)):
            print "MDL Face Structure"
            print "facesfront: ", self.tris_list[i][0]
            print "vertex index: ", self.tris_list[i][1]
            print "vertex index: ", self.tris_list[i][2]
            print "vertex index: ", self.tris_list[i][3]
            print "------------------"

class mdl_tex_coord:
    binary_format = "<3i" # little-endian (<), 3 ints.
    uv_list = [] # A list of integers, 1 for "onseam" and 2 for the s,t or u,v texture coordinates.


    def __init__(self):
        self.uv_list = []

    def save(self, file, num_verts):
        # Texture are generally divided in two pieces:
        #     one for the frontface of the model,
        #     and one for the backface.
        # The backface piece must be translated by skinwidth/2 from the frontface piece.
        for i in xrange(0, num_verts):
            data = struct.pack(self.binary_format, self.uv_list[i][0], self.uv_list[i][1], self.uv_list[i][2])
            file.write(data)

    def dump(self):
        for i in xrange(0, len(self.uv_list)):
            print "MDL Texture Coordinate Structure"
            print "texture coord onseam: ", self.uv_list[i][0]
            print "texture coordinate u: ", self.uv_list[i][1]
            print "texture coordinate v: ", self.uv_list[i][2]
            print "------------------"

class mdl_texture_info:
    group = 0  # int, This is the texture group setting, 0 = single, 1 = group (for animation textures).
    nb = 0     # (used in save function below), int, number of pics for an animation texture.
    time = 0.0 # (used in save function below), float, time duration for each pic above.
    binary_format = "<i" # little-endian (<), 1 int for group setting.

    def __init__(self):
        self.group = 0
        self.nb = 0
        self.time = 0.0
        self.binary_format = "<i" # little-endian (<), 1 int for group setting, changed in save function if animation textures exist.

    def save(self, file, num_skins, skins, skin_width, skin_height):
        if self.group == 0:
            # Write the skin data.
            for i in xrange(0,num_skins):
                data = struct.pack(self.binary_format, self.group)
                file.write(data)
                Padding=(int(((skin_width * 8) + 31) / 32) * 4) - (skin_width * 1)
                ImageData = skins[i].dictspec['Image1']
                i = 0
                MdlSkinData = ''
                for y in xrange(0,skin_height):
                    for x in xrange(0,skin_width):
                        MdlSkinData += struct.pack("B", ord(ImageData[i+(skin_width+Padding)*(skin_height-1-y*2)]))
                        i += 1
                    i += Padding
                file.write(MdlSkinData)
        else:
            # Reset the binary data to write the added texture info section since animation textures exist.
            self.binary_format = "<if" # little-endian (<), 1 integer and 1 float.
            data = struct.pack(self.binary_format, self.nb, self.time)
            file.write(data)

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

    def save(self, file):
        data = struct.pack(self.binary_format, self.v[0], self.v[1], self.v[2], self.normalIndex)
        file.write(data)

    def dump(self):
        print "MDL Vertex"
        print "v: ",self.v[0], self.v[1], self.v[2]
        print "normalIndex: ", self.normalIndex
        print "===================="

class mdl_frame:
    group = 0   # int, This is the frame group setting, 0 = simple single frame, not 0 = group of frames.
    time = 0.0  # (used in save function below), float, time duration for each frame above.
    name = ""
    vertices = []
    frames = [] # For group of frames.
    binary_format = "<i" # little-endian (<), 1 int for group setting.

    def __init__(self):
        self.group = 0 # 0 = simple single frame, not 0 = group of frames.
        self.time = 0.0
        self.binary_format = "<i" # little-endian (<), 1 int for group setting, changed in save function of this class.
        self.bboxmin = [0.0]*3
        self.bboxmax = [0.0]*3
        self.name = ""
        self.vertices = []
        self.frames = []

    def save(self, file, num_verts):
        # file is the model file & full path, ex: C:\Quake\id1\progs\dog.mdl
        # self.name is the frame name ex: attack1
        data = struct.pack(self.binary_format, self.group)
        file.write(data)
        if self.group == 0:
            self.bboxmin = mdl_vertex()
            self.bboxmin.save(file)
            self.bboxmax = mdl_vertex()
            self.bboxmax.save(file)
            if len(self.name) > 15:
                output_name = self.name[:15] + '\0'
            else:
                output_name = self.name + ('\0'*(16-len(self.name)))
            binary_format = "<16s"
            data = struct.pack(binary_format, output_name)
            file.write(data)
            for i in xrange(0,num_verts):
                self.vertices[i].save(file)
               # self.vertices[i].dump() # For testing only, comment out when done.
        else: # HAVE DAN CHECK IF THIS IS CORRECT
            binary_format = "<f" # little-endian (<), 1 float for "time" till next frame.
            data = struct.pack(self.binary_format, self.group)
            file.write(data)
            for i in xrange(0,self.group):
                self.frames.append(mdl_frame())
                self.bboxmin = mdl_vertex()
                self.bboxmin.save(file)
                self.bboxmax = mdl_vertex()
                self.bboxmax.save(file)
                if len(self.frames[i].name) > 15:
                    output_name = self.frames[i].name[:15] + '\0'
                else:
                    output_name = self.frames[i].name + ('\0'*(16-len(self.frames[i].name)))
                binary_format = "<16s"
                data = struct.pack(binary_format, output_name)
                file.write(data)
                for j in xrange(0,num_verts):
                    self.frames[i].vertices[j].save(file)

    def dump(self):
        print "MDL Frame"
        print "group: ", self.group
        print "time: ", self.time
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

    def save(self, file, component):
        # Get the data we need.
        frames = component.dictitems['Frames:fg'].subitems
        vertices = frames[0].vertices
        # We need to start with the bounding box of the component's first frame's vertices only.
        bounding_box = quarkx.boundingboxof(vertices)
        mins = bounding_box[0].tuple
        maxs = bounding_box[1].tuple
        skins = component.dictitems['Skins:sg'].subitems
        skin = skins[0]
        skin_size = skin.dictspec['Size']

        # Fill in the header data.
        self.ident = 1330660425
        self.version = 6
        #the scale is the difference between the min and max (on that axis) / 255
        frame_scale_x=(bounding_box[1].x-bounding_box[0].x)/255
        frame_scale_y=(bounding_box[1].y-bounding_box[0].y)/255
        frame_scale_z=(bounding_box[1].z-bounding_box[0].z)/255
        self.scale = (frame_scale_x, frame_scale_y, frame_scale_z)
        #translate value of the mesh to center it on the origin
        frame_trans_x=bounding_box[0].x
        frame_trans_y=bounding_box[0].y
        frame_trans_z=bounding_box[0].z
        self.translate = (frame_trans_x, frame_trans_y, frame_trans_z)


        self.boundingradius = abs(RadiusFromBounds(mins, maxs))
        self.eyeposition = (0.0, 0.0, -24.0)
        self.num_skins = len(skins)
        self.skin_width = int(skin_size[0])
        self.skin_height = int(skin_size[1])
        self.num_verts = len(vertices)
        self.num_tris = len(component.triangles)
        self.num_frames = len(frames)
        if editor.Root.dictspec.has_key('synctype'):
            self.synctype = int(editor.Root.dictspec['synctype'])
        else:
            self.synctype = 0
        if editor.Root.dictspec.has_key('flags'):
            self.flags = int(editor.Root.dictspec['flags'])
        else:
            self.flags = 0
        self.size = 8.45938873291

        # Writes all of the header data to the model file.
        data = struct.pack(self.binary_format, self.ident, self.version, self.scale[0], self.scale[1], self.scale[2], self.translate[0], self.translate[1], self.translate[2], self.boundingradius, self.eyeposition[0], self.eyeposition[1], self.eyeposition[2], self.num_skins, self.skin_width, self.skin_height, self.num_verts, self.num_tris, self.num_frames, self.synctype, self.flags, self.size)
        file.write(data)

        # Write the skin(s) texture information and skin(s).
        self.texture_info = mdl_texture_info()
        for item in skins:
            if item.type == ":ssg":
                self.texture_info.group = 1
                self.texture_info.nb = self.num_skins
                self.texture_info.time = 0.025
        self.texture_info.save(file, self.num_skins, skins, self.skin_width, self.skin_height)





        # Write the texture coordinates and faces data for model.
        self.tex_coords = mdl_tex_coord()
        self.faces = mdl_face()
        get_tris_data(file, self, component)
        self.tex_coords.save(file, self.num_verts)
        self.faces.save(file, self.num_tris)
       # self.tex_coords.dump() # For testing only, comment out when done.
       # self.faces.dump() # For testing only, comment out when done.

        # Write the # of frames, and their vertices, for the model.
        animate_mdl(self, file, frames)

        return self

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
# Export functions
######################################################
def get_tris_data(file, mdl, component):
    global progressbar, tobj, logging, Strings
    uv_list = [[0, 0, 0]] * mdl.num_verts
    tris_list = [[]] * mdl.num_tris
    tris = component.triangles
    skinsize = mdl.skin_width
    seam = skinsize / 2
    name = component.shortname
    Strings[2454] = name + "\n" + Strings[2454]
    progressbar = quarkx.progressbar(2454, mdl.num_tris + mdl.num_frames)
    for i in xrange(0, mdl.num_tris):
        tri = tris[i]
        tris_list[i] = [0, 0, 0, 0]
        u_values = [0, 0, 0]
        for j in xrange(0, 3):
            vtx, u, v = tri[j]
            if u < seam:
                u_values[j] = 1
        if u_values[0] == 1 and u_values[1] == 1 and u_values[2] == 1:
            frontface = 1
        else:
            frontface = 0
        for j in xrange(0, 3):
            vtx, u, v = tri[j]
            tris_list[i][j+1] = vtx
            onseam = 32
            if u == seam:
                onseam = 0
            if u > seam:
                u = u - seam
            uv_list[vtx] = [onseam, u, v]
        tris_list[i][0] = frontface
        progressbar.progress()
    mdl.tex_coords.uv_list = uv_list
    mdl.faces.tris_list = tris_list


def animate_mdl(mdl, file, frames): # The Frames Group is made here & returned to be added to the Component.
    global progressbar, tobj, logging
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Frame group data: " + str(mdl.num_frames) + " frames")
        tobj.logcon ("frame: frame name")
        tobj.logcon ("#####################################################################")

	######### Process the verts from the QuArK Frames lists.
    # Write the # of frames for the model.
    for i in xrange(0,mdl.num_frames):
        ### name is the frame name, ex: attack1
        name = frames[i].name.split(":")[0]
        if logging == 1:
            tobj.logcon (str(i) + ": " + name)

        mdl.frames.append(mdl_frame())
        vertices = frames[i].vertices
        mdl.frames[i].name = name
        #make the # of vertices for each frame
        for j in xrange(0,mdl.num_verts):
            mdl.frames[i].vertices.append(mdl_vertex())
            vert = vertices[j].tuple
            x = int((vert[0] - mdl.translate[0]) / mdl.scale[0])
            y = int((vert[1] - mdl.translate[1]) / mdl.scale[1])
            z = int((vert[2] - mdl.translate[2]) / mdl.scale[2])
            mdl.frames[i].vertices[j].v = [x, y, z]
        mdl.frames[i].save(file, mdl.num_verts)
        progressbar.progress()


######################################################
# Save MDL Format
######################################################
def save_mdl(filename):
    global editor, tobj, logging, exportername, textlog, Strings
    editor = quarkpy.mdleditor.mdleditor
    if editor is None:
        return
    # "objects" is a list of one or more selected model components for exporting.
    objects = editor.layout.explorer.sellist

    if not objects:
        quarkx.msgbox("No Components have been selected for exporting.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return
    for object in objects:
        if not object.name.endswith(":mc"):
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select one component\nfolder at a time for exporting.\n\nAn item that is not a component folder\nis in your selections.\n\nDeselect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
    if len(objects) > 1:
        quarkx.msgbox(str(len(objects)) + " Components have been selected for exporting.\nYou can ONLY select one component folder at a time for exporting.\n\nComponents can be combined or copied into one,\nbut only one skin can be used at a time.\n\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        return
    else:
        if not objects[0].dictitems['Frames:fg'] or len(objects[0].dictitems['Frames:fg'].subitems) == 0:
            quarkx.msgbox("No frames exist for exporting.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if len(objects[0].dictitems['Frames:fg'].subitems[0].dictspec['Vertices']) == 0:
            quarkx.msgbox("Nothing exist for exporting.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    mdl = mdl_obj()  # Blank mdl object to save.

    # Get the component.
    component = editor.layout.explorer.sellist[0] # This gets the first component (should be only one).

    # Actually write it to disk.
    file = open(filename, "wb")
    mdl.save(file, component)
    if logging == 1:
        mdl.dump() # Writes the file Header last to the log for comparison reasons.
    file.close()
    progressbar.close()
    Strings[2455] = Strings[2455].replace(component.shortname + "\n", "")

    # Cleanup.
    mdl = 0

    add_to_message = "The skin texture for this model\nhas been embedded with the model."
    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

# Saves the model file: root is the actual file,
# filename is the full path and name of the .mdl file to create.
# For example:  C:\Quake\id1\progs\dog.mdl
# gamename is None.
def savemodel(root, filename, gamename, nomessage=0):
    save_mdl(filename)

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".mdl Quake 1 Exporter", ".mdl file", "*.mdl", savemodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_md0_Q_export.py,v $
# Revision 1.6  2012/10/13 21:54:33  cdunde
# To correct and update model settings.
#
# Revision 1.5  2012/10/09 06:22:38  cdunde
# To split up Quake1 and HexenII importers and exporters due to different skin texture image game palettes
# and to handle possible other differences in the future.
#
# Revision 1.4  2011/10/03 08:12:13  cdunde
# Removed unused dictspecs and fixed related exporter model distortion problem.
#
# Revision 1.3  2011/09/29 02:24:26  cdunde
# To match up importer and exporter code better for comparison, make needed corrections and file cleanup.
#
# Revision 1.2  2011/02/11 18:49:57  cdunde
# Small name update.
#
# Revision 1.1  2010/03/30 17:19:37  cdunde
# Needed to change file name for proper listing on menu.
#
# Revision 1.2  2010/03/27 04:29:10  cdunde
# Fixed the U,V exporting.
#
# Revision 1.1  2010/03/26 07:27:41  cdunde
# New exporter for Quake .mdl models.
#
#
