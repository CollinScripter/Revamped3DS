# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for original Half-Life .mdl model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md0_HL1_import.py,v 1.17 2012/03/10 08:10:12 cdunde Exp $


Info = {
   "plug-in":       "ie_md0_HL1_import",
   "desc":          "This script imports an original Half-Life file (MDL), textures, and animations into QuArK for editing.",
   "date":          "March 27, 2010",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import struct, sys, os, time, operator, math
import quarkx
from types import *
import quarkpy.mdlutils
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings
from quarkpy.qeditor import MapColor # Strictly needed for QuArK bones MapColor call.

# Globals
SkipAnimation = 0 # 0 = makes animation frames, 1 = does not.
logging = 0
importername = "ie_md0_HL1_import.py"
textlog = "HL1mdl_ie_log.txt"
progressbar = None
mdl = None
UseName = ""

######################################################
# MDL Flag Settings from -> hlmviewer source file -> studio.h
######################################################
# lighting options from -> lighting options
STUDIO_NF_FLATSHADE  = 1
STUDIO_NF_CHROME     = 2
STUDIO_NF_FULLBRIGHT = 4

# motion flags from -> motion flags
STUDIO_X     =     1
STUDIO_Y     =     2
STUDIO_Z     =     4
STUDIO_XR    =     8
STUDIO_YR    =    16
STUDIO_ZR    =    32
STUDIO_LX    =    64
STUDIO_LY    =   128
STUDIO_LZ    =   256
STUDIO_AX    =   512
STUDIO_AY    =  1024
STUDIO_AZ    =  2048
STUDIO_AXR   =  4096
STUDIO_AYR   =  8192
STUDIO_AZR   = 16384
STUDIO_TYPES = 32767
STUDIO_RLOOP = 32768 # controller that wraps shortest distance

# sequence flags from -> sequence flags
STUDIO_LOOPING      = 1

# bone flags from -> bone flags
STUDIO_HAS_NORMALS  = 1
STUDIO_HAS_VERTICES = 2
STUDIO_HAS_BBOX     = 4
STUDIO_HAS_CHROME   = 8 # if any of the textures have chrome on them

RAD_TO_STUDIO       = (32768.0/math.pi)
STUDIO_TO_RAD       = (math.pi/32768.0)


######################################################
# MDL Model Constants from -> hlmviewer source file -> studio.h -> STUDIO MODELS
######################################################
MDL_MAX_TRIANGLES   = 20000
MDL_MAX_VERTICES    = 2048
MDL_MAX_SEQUENCES   = 256  # total animation sequences
MDL_MAX_SKINS       = 100         # total textures
MDL_MAX_SRCBONES    = 512   # bones allowed at source movement
MDL_MAX_BONES       = 128      # total bones actually used
MDL_MAX_MODELS      = 32      # sub-models per model
MDL_MAX_BODYPARTS   = 32
MDL_MAX_GROUPS      = 4
MDL_MAX_ANIMATIONS  = 512 # per sequence
MDL_MAX_MESHES      = 256
MDL_MAX_EVENTS      = 1024
MDL_MAX_PIVOTS      = 256
MDL_MAX_CONTROLLERS = 8

######################################################
# MDL Functions, from -> hlmviewer source file -> mathlib.c
######################################################
# m_frame = 0.0 for an interpolation's base frame.
# If we were using interpolation it would be a value between 0.0 and 1.0.
def QuaternionSlerp(q1, q2, m_frame=0.0):
    # Decide if one of the quaternions is backwards.
    q = [0.0, 0.0, 0.0, 0.0]
    a = 0
    b = 0
    for i in xrange(4):
        a += (q1[i]-q2[i])*(q1[i]-q2[i])
        b += (q1[i]+q2[i])*(q1[i]+q2[i])

    if a > b:
        for i in xrange(4):
            q2[i] = -q2[i]

    cosom = q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2] + q1[3]*q2[3]

    if (1.0 + cosom) > 0.00000001:
        if (1.0 - cosom) > 0.00000001:
            omega = math.acos(cosom)
            sinom = math.sin(omega)
            sclp = math.sin((1.0 - m_frame)*omega) / sinom
            sclq = math.sin(m_frame * omega) / sinom
        else:
            sclp = 1.0 - m_frame
            sclq = m_frame

        for i in xrange(4):
            q[i] = sclp * q1[i] + sclq * q2[i]

    else:
        q[0] = -q1[1]
        q[1] = q1[0]
        q[2] = -q1[3]
        q[3] = q1[2]
        sclp = math.sin((1.0 - m_frame) * 0.5 * math.pi)
        sclq = math.sin(m_frame * 0.5 * math.pi)
        for i in xrange(3):
            q[i] = sclp * q1[i] + sclq * q[i]
    return q


def SlerpBones(pos1, quat1, pos2, quat2, s):
    pos = [[]] * len(pos1)
    quat = [[]] * len(pos1)

    if (s < 0):
        s = 0
    elif (s > 1.0):
        s = 1.0

    s1 = 1.0 - s

    for i in xrange(len(pos1)):
        quat[i] = QuaternionSlerp(quat1[i], quat2[i], s)
        pos[i] = [pos1[i][0] * s1 + pos2[i][0] * s,
                  pos1[i][1] * s1 + pos2[i][1] * s,
                  pos1[i][2] * s1 + pos2[i][2] * s]
    return pos, quat


# ================================================
# ALL FOLLOWING CODE FROM:
# http://www.ros.org/wiki/geometry/RotationMethods#transformations.py
# LINKING TO:
# http://code.google.com/p/ros-geometry/source/browse/tf/src/tf/transformations.py
# --------------------------------------------------------------------------------
# from transformations.py, def quaternion_from_euler function, if statement (else section only).
def EulerAngle2Quaternion(angles):
    # x = roll, y = pitch, z = yaw
    angleX = angles[0] * 0.5
    cx = math.cos(angleX)
    sx = math.sin(angleX)
    angleY = angles[1] * 0.5
    cy = math.cos(angleY)
    sy = math.sin(angleY)
    angleZ = angles[2] * 0.5
    cz = math.cos(angleZ)
    sz = math.sin(angleZ)

    return [sx*cy*cz - cx*sy*sz, # X
            cx*sy*cz + sx*cy*sz, # Y
            cx*cy*sz - sx*sy*cz, # Z
            cx*cy*cz + sx*sy*sz] # W


#Minimum difference to consider float "different"
EQUAL_EPSILON = 0.001


######################################################
# MDL Functions, from -> hlmviewer source file -> studio_render.cpp
######################################################
def VectorCompare(v1, v2):
    for i in range(3):
        if (math.fabs(v1[i]-v2[i]) > EQUAL_EPSILON):
            return 0
    return 1


######################################################
# MDL Functions, QuArK's own
######################################################
def quaternion2matrix(quaternion):
    q = quaternion
    return [[1.0-2.0*q[1]*q[1] - 2.0*q[2]*q[2], 2.0*q[0]*q[1] - 2.0*q[3]*q[2], 2.0*q[0]*q[2] + 2.0*q[3]*q[1], 0.0],
            [2.0*q[0]*q[1] + 2.0*q[3]*q[2], 1.0-2.0*q[0]*q[0] - 2.0*q[2]*q[2], 2.0*q[1]*q[2] - 2.0*q[3]*q[0], 0.0],
            [2.0*q[0]*q[2] - 2.0*q[3]*q[1], 2.0*q[1]*q[2] + 2.0*q[3]*q[0], 1.0-2.0*q[0]*q[0] - 2.0*q[1]*q[1], 0.0],
            [0.0                          , 0.0                          , 0.0                              , 1.0]]


def Read_mdl_bone_anim_value(self, file, file_offset):
    file.seek(file_offset, 0)
    anim_value = mdl_bone_anim_value()
    anim_value.load(file)
   # anim_value.dump()
    return anim_value

# Creates a bbox (hit box) if any.
def MakePoly(bname, bpos, brot, bbox):
    m = bbox[0]
    M = bbox[1]
    name = bname.replace(":bone", ":p") # Use the bone name for better identification.
    p = quarkx.newobj(name)
    p["assigned2"] = bname
    p['show'] = (1.0,)
    face = quarkx.newobj("north:f") # BACK FACE
    vtx0 = (bpos + (brot * quarkx.vect(m[0],M[1],M[2]))).tuple
    vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
    vtx1 = (bpos + (brot * quarkx.vect(M[0],M[1],M[2]))).tuple
    vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
    vtx2 = (bpos + (brot * quarkx.vect(m[0],M[1],m[2]))).tuple
    vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("east:f") # RIGHT FACE
    vtx0 = (bpos + (brot * quarkx.vect(M[0],M[1],M[2]))).tuple
    vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
    vtx1 = (bpos + (brot * quarkx.vect(M[0],m[1],M[2]))).tuple
    vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
    vtx2 = (bpos + (brot * quarkx.vect(M[0],M[1],m[2]))).tuple
    vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("south:f") # FRONT FACE
    vtx0 = (bpos + (brot * quarkx.vect(M[0],m[1],M[2]))).tuple
    vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
    vtx1 = (bpos + (brot * quarkx.vect(m[0],m[1],M[2]))).tuple
    vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
    vtx2 = (bpos + (brot * quarkx.vect(M[0],m[1],m[2]))).tuple
    vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("west:f") # LEFT FACE
    vtx0 = (bpos + (brot * quarkx.vect(m[0],m[1],M[2]))).tuple
    vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
    vtx1 = (bpos + (brot * quarkx.vect(m[0],M[1],M[2]))).tuple
    vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
    vtx2 = (bpos + (brot * quarkx.vect(m[0],m[1],m[2]))).tuple
    vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("up:f") # TOP FACE
    vtx0 = (bpos + (brot * quarkx.vect(m[0],M[1],M[2]))).tuple
    vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
    vtx1 = (bpos + (brot * quarkx.vect(m[0],m[1],M[2]))).tuple
    vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
    vtx2 = (bpos + (brot * quarkx.vect(M[0],M[1],M[2]))).tuple
    vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("down:f") # BOTTOM FACE
    vtx0 = (bpos + (brot * quarkx.vect(m[0],M[1],m[2]))).tuple
    vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
    vtx1 = (bpos + (brot * quarkx.vect(M[0],M[1],m[2]))).tuple
    vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
    vtx2 = (bpos + (brot * quarkx.vect(m[0],m[1],m[2]))).tuple
    vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)

    return p



######################################################
# MDL data structures
######################################################
class mdl_bone:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiobone_t
    #Header Structure      #item of file, type, description.
    bone_index = 0         # For our own use later.
    name = ""              #item  0-31   32 char, bone name for symbolic links.
    parent = 0             #item  32     int, parent bone.
    flags = 0              #item  33     int, unknown item.
    bonecontroller = [0]*6 #item  34-39  6 int, bone controller index, -1 == none
    value = [0.0]*6        #item  40-45  6 floats, default DoF values
    scale = [0.0]*6        #item  46-51  6 floats, scale for delta DoF values

    binary_format = "<32cii6i6f6f" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone_index = 0
        self.name = ""
        self.parent = 0
        self.flags = 0
        self.bonecontroller = [0]*6
        self.value = [0.0]*6
        self.scale = [0.0]*6

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        char = 32
        for i in xrange(0, char):
            if data[i] == "\x00":
                continue
            self.name = self.name + data[i]
        self.parent = data[32]
        self.flags = data[33]
        self.bonecontroller = [data[34], data[35], data[36], data[37], data[38], data[39]]
        self.value = [data[40], data[41], data[42], data[43], data[44], data[45]]
        self.scale = [data[46], data[47], data[48], data[49], data[50], data[51]]
        return self

    def dump(self):
        print "MDL Bone"
        print "bone_index: ", self.bone_index
        print "name: ", self.name
        print "parent: ", self.parent
        print "flags: ", self.flags
        print "bonecontroller: ", self.bonecontroller
        print "value: ", self.value
        print "scale: ", self.scale
        print "===================="


class mdl_bone_control:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiobonecontroller_t
    #Header Structure      #item of file, type, description.
    bone = 0               #item   0      int, -1 = 0.
                           #                   types = X, Y, Z, XR, YR, ZR or M.
    type = 0               #item   1      int, types = 1, 2, 4,  8, 16, 32 or 64
    start = 0.0            #item   2      float.
    end = 0.0              #item   3      float.
    rest = 0               #item   4      int, byte index value at rest.
    index = 0              #item   5      int, 0-3 user set controller, 4 mouth.

    binary_format = "<2i2f2i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone = 0
        self.type = 0
        self.start = 0.0
        self.end = 0.0
        self.rest = 0
        self.index = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.bone = data[0]
        self.type = data[1]
        self.start = data[2]
        self.end = data[3]
        self.rest = data[4]
        self.index = data[5]
        return self

    def dump(self):
        print "MDL Bone Control"
        print "bone: ", self.bone
        print "type: ", self.type
        print "start: ", self.start
        print "end: ", self.end
        print "rest: ", self.rest
        print "index: ", self.index
        print "===================="


class mdl_hitbox:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiobbox_t
    #Header Structure      #item of file, type, description.
    bone = 0               #item   0      int, the bone's index.
    group = 0              #item   1      int, intersection group.
    bbmin = (0.0)*3        #item   2-4    3 floats, bounding box min x,y,z Vector.
    bbmax = (0.0)*3        #item   5-7    3 floats, bounding box max x,y,z Vector.

    binary_format = "<2i3f3f" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone = 0
        self.group = 0
        self.bbmin = (0.0)*3
        self.bbmax = (0.0)*3

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.bone = data[0]
        self.group = data[1]
        self.bbmin = (data[2], data[3], data[4])
        self.bbmax = (data[5], data[6], data[7])
        return self

    def dump(self):
        print "MDL Hitbox"
        print "bone: ", self.bone
        print "group: ", self.group
        print "bbmin: ", self.bbmin
        print "bbmax: ", self.bbmax
        print "===================="


class mdl_attachment:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioattachment_t
    #Header Structure      #item of file, type, description.
    name = ""              #item   0-31   32 char, attachment name.
    type = 0               #item   32     int, type of attachment.
    bone = 0               #item   33     int, bone index.
    org = [0.0]*3          #item   34-36  3 floats, attachment point.
    vectors = [[0.0]*3]*3  #item   37-45  3 floats each for 3 vectors.

    binary_format = "<32c2i3f9f" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.name = ""
        self.type = 0
        self.bone = 0
        self.org = [0.0]*3
        self.vectors = [[0.0]*3]*3

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        char = 32
        for i in xrange(0, char):
            if data[i] == "\x00":
                continue
            self.name = self.name + data[i]
        self.type = data[32]
        self.bone = data[33]
        self.org = [data[34], data[35], data[36]]
        self.vectors = [[data[37], data[38], data[39]], [data[40], data[41], data[42]], [data[43], data[44], data[45]]]
        return self

    def dump(self):
        print "MDL Attachment"
        print "name: ", self.name
        print "type: ", self.type
        print "bone: ", self.bone
        print "org: ", self.org
        print "vectors: ", self.vectors
        print "===================="


class mdl_bodypart:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiobodyparts_t
                            #item of data file, size & type,   description
    name = ""               #item  0-63   64 char, bodypart name.
    nummodels = 0           #item  64     int, number of bodypart models.
    base = 0                #item  65     int, unknown item.
    model_offset = 0        #item  66     int, index (Offset) into models array (data).
    models = []                           # A list containing its models.

    binary_format = "<64c3i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.name = ""
        self.nummodels = 0
        self.base = 0
        self.model_offset = 0
        self.models = []

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        char = 64
        for i in xrange(0, char):
            if data[i] == "\x00":
                continue
            self.name = self.name + data[i]
        self.nummodels = data[64]
        self.base = data[65]
        self.model_offset = data[66]
        return self

    def dump(self):
        print "MDL Bodyparts"
        print "name: ", self.name
        print "nummodels: ", self.nummodels
        print "base: ", self.base
        print "model_offset: ", self.model_offset
        print "===================="


class mdl_model:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiomodel_t
    #Header Structure      #item of file, type, description.
    name = ""              #item   0-63   64 char, model name.
    type = 0               #item   64     int, type of model.
    boundingradius = 0.0   #item   65     float, boundingradius of this model's 1st frame's bbox.
    nummesh = 0            #item   66     int, number of a mesh (its real index).
    mesh_offset = 0        #item   67     int, index (Offset) into models data.
    numverts = 0           #item   68     int, number of unique vertices.
    vert_info_offset = 0   #item   69     int, vertex bone info Offset.
    vert_offset = 0        #item   70     int, vertex index (Offset) to its vector.
    numnorms = 0           #item   71     int, number of unique surface normals.
    norm_info_offset = 0   #item   72     int, normal bone info Offset.
    norm_offset = 0        #item   73     int, normal index (Offset) to its vector.
    numgroups = 0          #item   74     int, deformation groups.
    group_offset = 0       #item   75     int, deformation groups Offset.

    binary_format = "<64cif10i" #little-endian (<), see #item descriptions above.

    meshes = []                           # List of meshes.
    verts = []                            # List of vertex vector poistions.
    verts_info = []                       # List of vertex bone indexes.
    normals = []                          # List of normal vector poistions.
    groups = []                           # List of groups, unknown items.

    def __init__(self):
        self.name = ""
        self.type = 0
        self.boundingradius = 0.0
        self.nummesh = 0
        self.mesh_offset = 0
        self.numverts = 0
        self.vert_info_offset = 0
        self.vert_offset = 0
        self.numnorms = 0
        self.norm_info_offset = 0
        self.norm_offset = 0
        self.numgroups = 0
        self.group_offset = 0

        self.meshes = []
        self.verts = []
        self.verts_info = []
        self.normals = []
        self.groups = []

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        char = 64
        for i in xrange(0, char):
            if data[i] == "\x00":
                continue
            self.name = self.name + data[i]
        self.type = data[64]
        self.boundingradius = data[65]
        self.nummesh = data[66]
        self.mesh_offset = data[67]
        self.numverts = data[68]
        self.vert_info_offset = data[69]
        self.vert_offset = data[70]
        self.numnorms = data[71]
        self.norm_info_offset = data[72]
        self.norm_offset = data[73]
        self.numgroups = data[74]
        self.group_offset = data[75]
        return self

    def dump(self):
        print "MDL Bodypart Model"
        print "name: ", self.name
        print "type: ", self.type
        print "boundingradius: ", self.boundingradius
        print "nummesh: ", self.nummesh
        print "mesh_offset: ", self.mesh_offset
        print "numverts: ", self.numverts
        print "vert_info_offset: ", self.vert_info_offset
        print "vert_offset: ", self.vert_offset
        print "numnorms: ", self.numnorms
        print "norm_info_offset: ", self.norm_info_offset
        print "norm_offset: ", self.norm_offset
        print "numgroups: ", self.numgroups
        print "group_offset: ", self.group_offset
        print "===================="


class mdl_mesh:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiomesh_t
    #Header Structure      #item of file, type, description.
    numtris = 0            #item  0   int, attachment name.
    tri_offset = 0         #item  1   int, offset of triangle data.
    skinref = 0            #item  2   int, unknown item.
    numnorms = 0           #item  3   int, per mesh normals.
    normindex = 0          #item  4   int, normal vec3_t.

    triangles = []                     # List of mdl_triangle. These are NOT really full triangles,
                                       #    just ONE vertex to make up a "fan" or "strip" of triangles.
    normals = []                       # List of normals. Use these for the UV's, tile when needed.

    binary_format = "<5i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.numtris = 0
        self.tri_offset = 0
        self.skinref = 0
        self.numnorms = 0
        self.normindex = 0

        self.triangles = []
        self.normals = []

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.numtris = data[0]
        self.tri_offset = data[1]
        self.skinref = data[2]
        self.numnorms = data[3]
        self.normindex = data[4]
        return self

    def dump(self):
        print "MDL Mesh"
        print "numtris: ", self.numtris
        print "tri_offset: ", self.tri_offset
        print "skinref: ", self.skinref
        print "numnorms: ", self.numnorms
        print "normindex: ", self.normindex
        print "===================="


class mdl_sequence_desc:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioseqdesc_t
    #Header Structure        #item of file, type, description.
    label = ""               #item   0-31   32 char, sequence label.
    fps = 25                 #item   32     float, frames per second.
    flags = 0                #item   33     int, non-looping/looping flags...0/1
    activity = 0             #item   34     int, unknown item.
    actweight = 0            #item   35     int, unknown item.
    numevents = 0            #item   36     int, number of events.
    event_offset = 0         #item   37     int, index (Offset) to THIS events data.
    numframes = 0            #item   38     int, number of frames per sequence.
    numpivots = 0            #item   39     int, number of foot pivots.
    pivot_offset = 0         #item   40     int, index (Offset) to the pivot data.
    motiontype = 0           #item   41     int, unknown item.
    motionbone = 0           #item   42     int, unknown item.
    linearmovement = [0.0]*3 #item   43-45  3 floats, bounding box min.
    automoveposindex = 0     #item   46     int, unknown item.
    automoveangleindex = 0   #item   47     int, unknown item.
    bbmin = [0.0]*3          #item   48-50  3 floats, per sequence bounding box min.
    bbmax = [0.0]*3          #item   51-53  3 floats, per sequence bounding box max.
    numblends = 0            #item   54     int, unknown item.
    anim_offset = 0          #item   55     int, start (Offset) to the sequence group data ex: [blend][bone][X, Y, Z, XR, YR, ZR].
    blendtype = [0]*2        #item   56-57  2 ints, X, Y or Z and XR, YR or ZR.
    blendstart = [0.0]*2     #item   58-59  2 floats, starting values.
    blendend = [0.0]*2       #item   60-61  2 floats, ending values.
    blendparent = 0          #item   62     int, unknown item.
    seqgroup = 0             #item   63     int, sequence group for demand loading.
    entrynode = 0            #item   64     int, transition node at entry.
    exitnode = 0             #item   65     int, transition node at exit.
    nodeflags = 0            #item   66     int, transition rules.
    nextseq = 0              #item   67     int, auto advancing sequences.

    binary_format = "<32cf10i3f2i6f4i4f6i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.label = ""
        self.fps = 25
        self.flags = 0
        self.activity = 0
        self.actweight = 0
        self.numevents = 0
        self.event_offset = 0
        self.numframes = 0
        self.numpivots = 0
        self.pivot_offset = 0
        self.motiontype = 0
        self.motionbone = 0
        self.linearmovement = [0.0]*3
        self.automoveposindex = 0
        self.automoveangleindex = 0
        self.bbmin = [0.0]*3
        self.bbmax = [0.0]*3
        self.numblends = 0
        self.anim_offset = 0
        self.blendtype = [0]*2
        self.blendstart = [0.0]*2
        self.blendend = [0.0]*2
        self.blendparent = 0
        self.seqgroup = 0
        self.entrynode = 0
        self.exitnode = 0
        self.nodeflags = 0
        self.nextseq = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        char = 32
        for i in xrange(0, char):
            if data[i] == "\x00":
                continue
            self.label = self.label + data[i]
        self.fps = data[32]
        self.flags = data[33]
        self.activity = data[34]
        self.actweight = data[35]
        self.numevents = data[36]
        self.event_offset = data[37]
        self.numframes = data[38]
        self.numpivots = data[39]
        self.pivot_offset = data[40]
        self.motiontype = data[41]
        self.motionbone = data[42]
        self.linearmovement = [data[43], data[44], data[45]]
        self.automoveposindex = data[46]
        self.automoveangleindex = data[47]
        self.bbmin = [data[48], data[49], data[50]]
        self.bbmax = [data[51], data[52], data[53]]
        self.numblends = data[54]
        self.anim_offset = data[55]
        self.blendtype = [data[56], data[57]]
        self.blendstart = [data[58], data[59]]
        self.blendend = [data[60], data[61]]
        self.blendparent = data[62]
        self.seqgroup = data[63]
        self.entrynode = data[64]
        self.exitnode = data[65]
        self.nodeflags = data[66]
        self.nextseq = data[67]

        global SkipAnimation
        if SkipAnimation:
            self.numframes = 0
            self.numblends = 0

        return self

    def dump(self):
        print "MDL Sequence Desc"
        print "label: ", self.label
        print "fps: ", self.fps
        print "flags: ", self.flags
        print "activity: ", self.activity
        print "actweight: ", self.actweight
        print "numevents: ", self.numevents
        print "event_offset: ", self.event_offset
        print "numframes: ", self.numframes
        print "numpivots: ", self.numpivots
        print "pivot_offset: ", self.pivot_offset
        print "motiontype: ", self.motiontype
        print "motionbone: ", self.motionbone
        print "linearmovement: ", self.linearmovement
        print "automoveposindex: ", self.automoveposindex
        print "automoveangleindex: ", self.automoveangleindex
        print "bbmin: ", self.bbmin
        print "bbmax: ", self.bbmax
        print "numblends: ", self.numblends
        print "anim_offset: ", self.anim_offset
        print "blendtype: ", self.blendtype
        print "blendstart: ", self.blendstart
        print "blendend: ", self.blendend
        print "blendparent: ", self.blendparent
        print "seqgroup: ", self.seqgroup
        print "entrynode: ", self.entrynode
        print "exitnode: ", self.exitnode
        print "nodeflags: ", self.nodeflags
        print "nextseq: ", self.nextseq
        print "===================="


class mdl_bone_anim_value:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioanimvalue_t
    #Header Structure   #item of file, type, description.
    valid = 0               #item  0     unsigned char int, 1 byte.
    total = 0               #item  1     unsigned char int, 1 byte.
    value = 0               #item  0+1   signed short int, 2 bytes.

    #This is a C++ union (two different ways to read the same bitstream); we'll do both at the same time
    binary_format1 = "<2B" #little-endian (<), see #item descriptions above.
    binary_format2 = "<h" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.valid = 0
        self.total = 0
        self.value = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format1))
        data = struct.unpack(self.binary_format1, temp_data)
        self.valid = data[0]
        self.total = data[1]
        data = struct.unpack(self.binary_format2, temp_data)
        self.value = data[0]
        return self

    def dump(self):
        print "MDL Anim Frames"
        print "valid: ", self.valid
        print "total: ", self.total
        print "value: ", self.value
        print "===================="


class mdl_skin_info:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiotexture_t
    #Header Structure       #item of file, type, description.
    name = ""               #item  0-63   64 char, skin name.
    flags = 0               #item  64     int, skin flags setting for special texture handling ex: None=0 (default), Chrome=2 (cstrike), Chrome=3 (valve), Additive=32, Chrome & Additive=34, Transparent=64.
    width = 0               #item  65     int, skinwidth in pixels.
    height = 0              #item  66     int, skinheight in pixels.
    skin_offset = 0         #item  67     int, index (Offset) to skin data.
    binary_format = "<64c4i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.name = ""
        self.flags = 0
        self.width = 0
        self.height = 0
        self.skin_offset = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        char = 64
        for i in xrange(0, char):
            if data[i] == "\x00":
                continue
            self.name = self.name + data[i]
        self.flags = data[64]
        self.width = data[65]
        self.height = data[66]
        self.skin_offset = data[67]
        return self

    def dump(self):
        print "MDL Skin"
        print "name: ", self.name
        print "flags: ", self.flags
        print "width: ", self.width
        print "height: ", self.height
        print "skin_offset: ", self.skin_offset
        print "--------------------"


class mdl_bone_anim:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioanim_t
                            #item of data file, size & type,   description
    offset = [0]*6          #item  0-5   6 unsigned short ints, file offsets to read animation data for bone(s) for EACH SET of ANIMATION FRAMES sequences.
    file_position = 0       #QuArK hack: file offset of this structure

    binary_format = "<6H" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.offset = [0]*6
        self.file_position = 0

    def load(self, file):
        self.file_position = file.tell()
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.offset = [data[0], data[1], data[2], data[3], data[4], data[5]]

    def dump(self):
        print "MDL Bone Anim"
        print "offset: ", self.offset
        print "-------------------"


class mdl_triangle:
# Done cdunde
                            #item of data file, size & type,   description
    index0vert = 0          #item  0   short, index into vertex array.
    index1uv = 0            #item  1   short, index into normal array.
    index2u = 0             #item  2   short, u or s position on skin.
    index3v = 0             #item  3   short, v or t position on skin.

    binary_format = "<4h" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.index0vert = 0
        self.index1uv = 0
        self.index2u = 0
        self.index3v = 0

    def load(self, file, byte_count):
        size = struct.calcsize(self.binary_format)
        byte_count = byte_count + size
        temp_data = file.read(size)
        data = struct.unpack(self.binary_format, temp_data)
        self.index0vert = data[0]
        self.index1uv = data[1]
        self.index2u = data[2]
        self.index3v = data[3]
        return self, byte_count

    def dump(self):
        print "MDL Triangle"
        print "index0vert: ", self.index0vert
        print "index1uv: ", self.index1uv
        print "index2u: ", self.index2u
        print "index3v: ", self.index3v
        print "===================="


class mdl_vert_info:
# Gives a bone_index for each Component's vertex that is assigned to that bone.
    bone_index = 0
    binary_format = "<B" #little-endian (<), 1 single byte (unsigned int).

    def __init__(self):
        self.bone_index = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.bone_index = data[0]
        return self

    def dump(self, bodypart, model, vtx):
        print "MDL Vertex Info for, bodypart, model, vtx:", bodypart, model, vtx
        print "bone_index: ",self.bone_index
        print "===================="


class mdl_vertex:
# Gives each vertex's x,y,z position.
    v = [0.0]*3
    binary_format = "<3f" #little-endian (<), 3 floats.

    def __init__(self):
        self.v = [0.0]*3

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.v = [data[0], data[1], data[2]]
        return self

    def dump(self):
        print "MDL Vertex"
        print "v: ",self.v[0], self.v[1], self.v[2]
        print "===================="


### NOT USED
class mdl_demand_hdr_group:
# Done cdunde from -> hlmviewer source file -> studio.h -> studioseqhdr_t
                            #item of data file, size & type,   description
    id = 0                  #item  0      int, group id.
    version = 0             #item  1      int, group version.
    name = ""               #item  2-65   64 char, group name.
    length = 0              #item  66     int, group length.

    binary_format = "<2i64ci" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.id = 0
        self.version = 0
        self.name = ""
        self.length = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.id = data[0]
        self.version = data[1]
        char = 64 + 2 # The above data items = 2.
        for c in xrange(2, char):
            if data[c] == "\x00":
                continue
            self.name = self.name + data[c]
        self.length = data[66]
        return self

    def dump(self):
        print "MDL Demand Seq Group"
        print "id: ", self.id
        print "version: ", self.version
        print "name: ", self.name
        print "length: ", self.length
        print "===================="

class mdl_demand_group:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioseqgroup_t
                            #item of data file, size & type,   description
    label = ""              #item  0-31   32 char, group label
    name = ""               #item  32-95  64 char, group name
    cache = 0               #item  96     int, cache index pointer
    data = 0                #item  97     int, hack for group 0

    binary_format = "<32c64c2i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.label = ""
        self.name = ""
        self.cache = 0
        self.data = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        char = 32 # The above data items = 0.
        for c in xrange(0, char):
            if data[c] == "\x00":
                continue
            self.label = self.label + data[c]

        char = 64 + 32 # The above data items = 32.
        for c in xrange(32, char):
            if data[c] == "\x00":
                continue
            self.name = self.name + data[c]
        self.cache = data[96]
        self.data = data[97]
        return self

    def dump(self):
        print "MDL Demand Seq Group"
        print "label: ", self.label
        print "name: ", self.name
        print "cache: ", self.cache
        print "data: ", self.data
        print "===================="


class mdl_events:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioevent_t
                            #item of data file, size & type,   description
    frame = 0               #item  0     int, frame number.
    event = 0               #item  1     int, event number.
    type = 0                #item  2     int, type of event indicator.
    options = ""            #item  3-66  64 char, unknown item.

    binary_format = "<3i64c" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.frame = 0
        self.event = 0
        self.type = 0
        self.options = ""

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.frame = data[0]
        self.event = data[1]
        self.type = data[2]
        char = 64
        for i in xrange(0, char):
            if data[i+3] == "\x00":
                continue
            self.options = self.options + data[i+3]
        return self

    def dump(self):
        print "MDL Events"
        print "frame: ", self.frame
        print "event: ", self.event
        print "type: ", self.type
        print "options: ", self.options
        print "===================="

class mdl_pivots:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiopivot_t
                            #item of data file, size & type,   description
    org = [0.0]*3           #item  0-2   3 floats, pivot point.
    start = 0               #item  3     int.
    end = 0                 #item  4     int.

    binary_format = "<3f2i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.org = [0.0]*3
        self.start = 0
        self.end = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.org = [data[0], data[1], data[2]]
        self.start = data[3]
        self.end = data[4]
        return self

    def dump(self):
        origin = str(self.org)
        tobj.logcon ("    org: %s" % origin)
        tobj.logcon ("  start: " + str(self.start))
        tobj.logcon ("    end: " + str(self.end))


def CalcBoneAdj(self, m_controller, m_mouth):
    m_adj = []

    for j in range(self.num_bone_controls):
        pbonecontroller = self.bone_controls[j]
        i = pbonecontroller.index;
        if (i <= 3):
            # check for 360% wrapping
            if (pbonecontroller.type & STUDIO_RLOOP):
                value = m_controller[i] * (360.0/256.0) + pbonecontroller.start
            else:
                value = m_controller[i] / 255.0
                if (value < 0):
                    value = 0.0
                elif (value > 1.0):
                    value = 1.0
                value = (1.0 - value) * pbonecontroller.start + value * pbonecontroller.end
        else:
            value = m_mouth / 64.0
            if (value > 1.0):
                value = 1.0
            value = (1.0 - value) * pbonecontroller.start + value * pbonecontroller.end

        if ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_XR) \
        or ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_YR) \
        or ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_ZR):
            m_adj += [value * (math.pi / 180.0)]
        elif ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_X) \
          or ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_Y) \
          or ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_Z):
            m_adj += [value]

    return m_adj

def CalcBoneQuaternion(self, m_frame, s, pbone, panim, m_adj):
    file = self.file
    angle1 = [0.0, 0.0, 0.0]
    angle2 = [0.0, 0.0, 0.0]

    quat = [0.0, 0.0, 0.0, 0.0]

    bone = self.bones[pbone]

    for i in range(3):
        if panim.offset[i+3] == 0:
            angle1[i] = bone.value[i+3] #default
            angle2[i] = bone.value[i+3] #default
        else:
            panimvalue = panim.file_position + panim.offset[i+3]
            animvalue = Read_mdl_bone_anim_value(self, file, panimvalue)
            k = m_frame
            # find span of values that includes the frame we want
            while (animvalue.total <= k):
                k -= animvalue.total
                panimvalue += (animvalue.valid + 1) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                animvalue = Read_mdl_bone_anim_value(self, file, panimvalue)
            # Bah, missing blend!
            if (animvalue.valid > k):
                panimvalueX = panimvalue + (k+1) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                animvalueX = Read_mdl_bone_anim_value(self, file, panimvalueX)
                angle1[i] = animvalueX.value
                if (animvalue.valid > k + 1):
                    panimvalueX = panimvalue + (k+2) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalueX = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    angle2[i] = animvalueX.value
                else:
                    if (animvalue.total > k + 1):
                        angle2[i] = angle1[i]
                    else:
                        panimvalueX = panimvalue + (animvalue.valid+2) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                        animvalueX = Read_mdl_bone_anim_value(self, file, panimvalueX)
                        angle2[i] = animvalueX.value
            else:
                panimvalueX = panimvalue + (animvalue.valid) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                animvalueX = Read_mdl_bone_anim_value(self, file, panimvalueX)
                angle1[i] = animvalueX.value
                if (animvalue.total > k + 1):
                    angle2[i] = angle1[i]
                else:
                    panimvalueX = panimvalue + (animvalue.valid+2) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalueX = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    angle2[i] = animvalueX.value
            angle1[i] = bone.value[i+3] + angle1[i] * bone.scale[i+3]
            angle2[i] = bone.value[i+3] + angle2[i] * bone.scale[i+3]

        if (bone.bonecontroller[i+3] != -1):
            angle1[i] += m_adj[bone.bonecontroller[i+3]]
            angle2[i] += m_adj[bone.bonecontroller[i+3]]

    if not VectorCompare(angle1, angle2):
        q1 = EulerAngle2Quaternion(angle1)
        q2 = EulerAngle2Quaternion(angle2)
        quat = QuaternionSlerp(q1, q2, s)
    else:
        quat = EulerAngle2Quaternion(angle1)

    return quat

def CalcBonePosition(self, m_frame, s, pbone, panim, m_adj):
    file = self.file
    pos = [0.0, 0.0, 0.0]

    bone = self.bones[pbone]

    for i in range(3):
        pos[i] = bone.value[i] # default
        if panim.offset[i] != 0:
            panimvalue = panim.file_position + panim.offset[i]
            animvalue = Read_mdl_bone_anim_value(self, file, panimvalue)
            k = m_frame
            # find span of values that includes the frame we want
            while (animvalue.total <= k):
                k -= animvalue.total
                panimvalue += (animvalue.valid + 1) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                animvalue = Read_mdl_bone_anim_value(self, file, panimvalue)
            # if we're inside the span
            if (animvalue.valid > k):
                # and there's more data in the span
                if (animvalue.valid > k + 1):
                    panimvalueX = panimvalue + (k+1) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue1 = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    panimvalueX = panimvalue + (k+2) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue2 = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += (animvalue1.value * (1.0 - s) + s * animvalue2.value) * bone.scale[i]
                else:
                    panimvalueX = panimvalue + (k+1) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalueX = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += animvalueX.value * bone.scale[i]
            else:
                # are we at the end of the repeating values section and there's another section with data?
                if (animvalue.total <= k + 1):
                    panimvalueX = panimvalue + (animvalue.valid) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue1 = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    panimvalueX = panimvalue + (animvalue.valid+2) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue2 = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += (animvalue1.value * (1.0 - s) + s * animvalue2.value) * bone.scale[i]
                else:
                    panimvalueX = panimvalue + (animvalue.valid) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalueX = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += animvalueX.value * bone.scale[i]
        if (bone.bonecontroller[i] != -1):
            pos[i] += m_adj[bone.bonecontroller[i]]

    return pos


def SetUpBones(self, QuArK_bones): # self = the mdl_obj. Done cdunde from -> hlmviewer source file -> studio_render.cpp -> StudioModel::SetUpBones
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#########################")
        tobj.logcon ("SetUpBones Section")
        tobj.logcon ("#########################")
    file = self.file
    pbones = self.bones
    pseqdesc = self.sequence_descs

    #Determine end of file
    oldpos = file.tell()
    file.seek(0, 2)
    endpos = file.tell()
    file.seek(oldpos, 0) #Restore old position

    # Go through all the animation sequences (frame groups) and fill the ModelComponentList['bonelist'][bone.name]['frames'] data.
    bonelist = editor.ModelComponentList['bonelist']
    if logging == 1:
        tobj.logcon ("num_anim_seq: " + str(self.num_anim_seq))
        tobj.logcon ("=========================")
    for m_sequence in xrange(self.num_anim_seq):
        seq_pivots = []
        seq_panims = []
        seq = pseqdesc[m_sequence]
        if (seq.numblends == 0) or (seq.numframes == 0):
            #Animation has no frames? Skip it!
            continue

        seq_name = seq.label
        if logging == 1:
            tobj.logcon ("========================")
            tobj.logcon ("seq %d: sequence name -> %s" % (m_sequence+1, seq_name))
            tobj.logcon ("========================")
        ### NOT USED
        file.seek(self.ofsBegin + seq.pivot_offset, 0)
        if logging == 1:
            tobj.logcon ("seq.numpivots: " + str(seq.numpivots))
        for p in xrange(seq.numpivots):
            seq_pivots.append(mdl_pivots())
            seq_pivots[p].load(file)
            if logging == 1:
                tobj.logcon ("mdl_pivot: " + str(p+1))
                tobj.logcon ("----------")
                seq_pivots[p].dump()
                tobj.logcon ("")

        #Read in the offsets
        if seq.seqgroup == 0:
            seq_fileoffset = self.ofsBegin + self.demand_seq_groups[seq.seqgroup].data
        else:
            seq_fileoffset = self.ofsBegin + self.anim_seq_offset + (m_sequence * struct.calcsize(seq.binary_format))

        file.seek(seq_fileoffset + seq.anim_offset, 0)
        if logging == 1:
            total = len(pbones)*6*2
            tobj.logcon ("----------------")
            tobj.logcon ("start mdl_bone_anim data: NumBones " + str(len(pbones)) + " x 6 offsets x 2 bytes ea. = " + str(total) + " bytes")
            tobj.logcon ("      pointer at start seq " + str(m_sequence) + ": " + str(file.tell()))
            tobj.logcon ("      frames data pointer s/b " + str(file.tell()+total))
            tobj.logcon ("----------------")
        if logging == 1:
            tobj.logcon ("seq.numblends: " + str(seq.numblends) + "  file at: " + str(file.tell()))
            tobj.logcon ("----------------")
        for m_blend in range(seq.numblends):
            seq_panims.append([])
            for pbone in range(len(self.bones)):
                seq_panims[m_blend].append(mdl_bone_anim())
                seq_panims[m_blend][pbone].load(file)
              #  seq_panims[m_blend][pbone].dump()

        #Get the bone position + rotation (vector + quaternion)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("----------------")
            tobj.logcon ("start frames data pointer at: " + str(file.tell()))
            tobj.logcon ("      seq.numframes: " + str(seq.numframes))
            tobj.logcon ("----------------")
        for m_frame in xrange(seq.numframes):
            def set_bone_controller(controller_index, value):
                our_controller = -1
                for j in range(self.num_bone_controls):
                    pbonecontroller = self.bone_controls[j]
                    if pbonecontroller.index == controller_index:
                        our_controller = j
                        break
                if our_controller == -1:
                    #Couldn't find it; nothing to do
                    return 0

                pbonecontroller = self.bone_controls[our_controller]
                # wrap 0..360 if it's a rotational controller
                if (pbonecontroller.type & (STUDIO_XR | STUDIO_YR | STUDIO_ZR)):
                    # ugly hack, invert value if end < start
                    if (pbonecontroller.end < pbonecontroller.start):
                        value = -value

                    # does the controller not wrap?
                    if (pbonecontroller.start + 359.0 >= pbonecontroller.end):
                        if (value > ((pbonecontroller.start + pbonecontroller.end) / 2.0) + 180):
                            value = value - 360
                        if (value < ((pbonecontroller.start + pbonecontroller.end) / 2.0) - 180):
                            value = value + 360
                    else:
                        if (value > 360):
                            value = value - int(value / 360.0) * 360.0
                        elif (value < 0):
                            value = value + int((value / -360.0) + 1) * 360.0

                result = int(255 * (value - pbonecontroller.start) / (pbonecontroller.end - pbonecontroller.start))
                if (result < 0):
                    result = 0
                if (result > 255):
                    result = 255
                return result

            def set_mouth(value):
                our_controller = -1
                for j in range(self.num_bone_controls):
                    pbonecontroller = self.bone_controls[j]
                    if pbonecontroller.index == 4:
                        our_controller = j
                        break
                if our_controller == -1:
                    #Couldn't find it; nothing to do
                    return 0

                pbonecontroller = self.bone_controls[our_controller]
                # wrap 0..360 if it's a rotational controller
                if (pbonecontroller.type & (STUDIO_XR | STUDIO_YR | STUDIO_ZR)):
                    # ugly hack, invert value if end < start
                    if (pbonecontroller.end < pbonecontroller.start):
                        value = -value

                    # does the controller not wrap?
                    if (pbonecontroller.start + 359.0 >= pbonecontroller.end):
                        if (value > ((pbonecontroller.start + pbonecontroller.end) / 2.0) + 180):
                            value = value - 360
                        if (value < ((pbonecontroller.start + pbonecontroller.end) / 2.0) - 180):
                            value = value + 360
                    else:
                        if (value > 360):
                            value = value - int(value / 360.0) * 360.0
                        elif (value < 0):
                            value = value + int((value / -360.0) + 1) * 360.0

                result = int(64 * (value - pbonecontroller.start) / (pbonecontroller.end - pbonecontroller.start))
                if (result < 0):
                    result = 0
                if (result > 64):
                    result = 64
                return result

            #FIXME: User may want to set these? We're currently setting them to value '0' (zero).
            m_controller = []
            for i in xrange(4):
                m_controller += [set_bone_controller(i, 0.0)]
            m_mouth = set_mouth(0.0)

            def CalcRotations(seq_panim):
                pos = [[]] * len(self.bones)
                quat = [[]] * len(self.bones)

                # add in programatic controllers
                m_adj = CalcBoneAdj(self, m_controller, m_mouth)

                for pbone in range(len(self.bones)):
                    panim = seq_panim[pbone]
                    quat[pbone] = CalcBoneQuaternion(self, m_frame, 0.0, pbone, panim, m_adj)
                    pos[pbone] = CalcBonePosition(self, m_frame, 0.0, pbone, panim, m_adj)

                if (seq.motiontype & STUDIO_X):
                    pos[seq.motionbone][0] = 0.0
                if (seq.motiontype & STUDIO_Y):
                    pos[seq.motionbone][1] = 0.0
                if (seq.motiontype & STUDIO_Z):
                    pos[seq.motionbone][2] = 0.0

                return pos, quat

            pos, quat = CalcRotations(seq_panims[0])

            if (seq.numblends > 1):
                def set_blending(blending_index, value):
                    if (seq.blendtype[blending_index] == 0):
                        return value

                    if (seq.blendtype[blending_index] & (STUDIO_XR | STUDIO_YR | STUDIO_ZR)):
                        # ugly hack, invert value if end < start
                        if (seq.blendend[blending_index] < seq.blendstart[blending_index]):
                            value = -value

                        # does the controller not wrap?
                        if (seq.blendstart[blending_index] + 359.0 >= seq.blendend[blending_index]):
                            if (value > ((seq.blendstart[blending_index] + seq.blendend[blending_index]) / 2.0) + 180):
                                value = value - 360
                            if (value < ((seq.blendstart[blending_index] + seq.blendend[blending_index]) / 2.0) - 180):
                                value = value + 360

                    result = int(255 * (value - seq.blendstart[blending_index]) / (seq.blendend[blending_index] - seq.blendstart[blending_index]))
                    if (result < 0):
                        result = 0
                    if (result > 255):
                        result = 255
                    return result

                #FIXME: User may want to set these? We're currently setting them to value '0.5'.
                m_blending = [set_blending(0, 0.5), set_blending(1, 0.5)]

                pos2, quat2 = CalcRotations(seq_panims[1])

                s = m_blending[0] / 255.0;

                pos, quat = SlerpBones(pos, quat, pos2, quat2, s)

  # FIXME:
  #  	if (pseqdesc->numblends == 4)
  #      {
  #      	panim += m_pstudiohdr->numbones;
  #      	CalcRotations( pos3, q3, pseqdesc, panim, m_frame );

  #      	panim += m_pstudiohdr->numbones;
  #      	CalcRotations( pos4, q4, pseqdesc, panim, m_frame );

  #      	s = m_blending[0] / 255.0;
  #      	SlerpBones( q3, pos3, q4, pos4, s );

  #      	s = m_blending[1] / 255.0;
  #      	SlerpBones( quat, pos, q3, pos3, s );
  #      }
  #  }

            frame_name = seq_name + " frame " + str(m_frame+1)
            tagsgroup_count = 0
            for pbone in range(len(self.bones)):
                bone = self.bones[pbone]

                bone_pos = (pos[pbone][0], pos[pbone][1], pos[pbone][2])
                tempmatrix = quaternion2matrix(quat[pbone])
                bone_matrix = ((tempmatrix[0][0], tempmatrix[0][1], tempmatrix[0][2]), (tempmatrix[1][0], tempmatrix[1][1], tempmatrix[1][2]), (tempmatrix[2][0], tempmatrix[2][1], tempmatrix[2][2]))
                if bone.parent != -1:
                    parent_name = QuArK_bones[bone.parent].name
                    parent_pos = quarkx.vect(bonelist[parent_name]['frames'][frame_name + ":mf"]['position'])
                    parent_matrix = quarkx.matrix(bonelist[parent_name]['frames'][frame_name + ":mf"]['rotmatrix'])
                    bone_pos = parent_pos + (parent_matrix * quarkx.vect(bone_pos))
                    bone_matrix = parent_matrix * quarkx.matrix(bone_matrix)
                    bone_pos = bone_pos.tuple
                    bone_matrix = bone_matrix.tuple

                if self.num_attachments != 0 and self.attachments.has_key(pbone):
                    tags = self.attachments[pbone]['tag_pos']
                    bone_name = self.attachments[pbone]['bone_name']
                    old_bone_pos = quarkx.vect(bonelist[bone_name]['frames']["baseframe:mf"]['position'])
                    new_bone_pos = quarkx.vect(bone_pos)
                    old_bone_rotmatrix = quarkx.matrix(bonelist[bone_name]['frames']["baseframe:mf"]['rotmatrix'])
                    new_bone_rotmatrix = quarkx.matrix(bone_matrix)
                    for tag in tags.keys():
                        Tpos = tags[tag]
                        Tpos = quarkx.vect((Tpos[0], Tpos[1], Tpos[2]))
                        Tpos = new_bone_pos + (new_bone_rotmatrix * Tpos)
                        Tpos = Tpos.tuple
                        tagframe = quarkx.newobj(frame_name + ':tagframe')
                        tagframe['show'] = (1.0,)
                        tagframe['origin'] = Tpos
                        tagframe['rotmatrix'] = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
                        tagframe['bone'] = bone_name
                        self.tagsgroup[tagsgroup_count].appenditem(tagframe)
                        tagsgroup_count = tagsgroup_count + 1

                # fills the ModelComponentList['bonelist'][bone.name]['frames'] data.
                bone_name = QuArK_bones[pbone].name
                if not bonelist[bone_name]['frames'].has_key(frame_name + ":mf"):
                    bonelist[bone_name]['frames'][frame_name + ":mf"] = {}
                bone_data = {}
                bone_data['position'] = bone_pos
                bone_data['rotmatrix'] = bone_matrix
                bonelist[bone_name]['frames'][frame_name + ":mf"] = bone_data


####################################
# Starts By Using the Model Object
####################################
class mdl_obj:
# Done cdunde from -> hlmviewer source file -> studio.h -> studiohdr_t
    origin = quarkx.vect(0.0, 0.0, 0.0) ### For QuArK's model placement in the editor.
    #Header Structure            #item of file, type, description.
    ident = ""                   #item   0-3    4 char, The version of the file (Must be IDST)
    version = 0                  #item   4      int, This is used to identify the file
    name = ""                    #item   5-68   64 char, the models path and full name.
    length = 0                   #item   69     int, length of the file in bytes to EOF.
    eyeposition = [0.0]*3        #item   70-72  3 floats, ideal eye position.
    min = [0.0]*3                #item   73-75  3 floats, ideal movement hull size, min.
    max = [0.0]*3                #item   76-78  3 floats, ideal movement hull size, max.
    bbmin = [0.0]*3              #item   79-81  3 floats, clipping bounding box size, min.
    bbmax = [0.0]*3              #item   82-84  3 floats, clipping bounding box size, max.
    flags = 0                    #item   85     int, unknown item.
    num_bones = 0                #item   86     int, The number of bone for the model.
    bones_offset = 0             #item   87     int, The bones data starting point in the file, in bytes.
    num_bone_controls = 0        #item   88     int, The number of bone controllers.
    bone_controls_offset = 0     #item   89     int, The bones controllers data starting point in the file, in bytes.
    num_hitboxes = 0             #item   90     int, The number of complex bounding boxes.
    hitboxes_offset = 0          #item   91     int, The hitboxes data starting point in the file, in bytes.
    num_anim_seq = 0             #item   92     int, The number of animation sequences for the model.
    anim_seq_offset = 0          #item   93     int, The animation sequences data starting point in the file, in bytes.
    num_demand_hdr_groups = 0    #item   94     int, The number of demand seq groups for the model, demand loaded sequences.
    demand_hdr_offset = 0        #item   95     int, The demand seq groups data starting point in the file, in bytes.
    num_textures = 0             #item   96     int, The number of raw textures.
    texture_index_offset = 0     #item   97     int, The textures data index starting point in the file, in bytes.
    texture_data_offset = 0      #item   98     int, The textures data starting point in the file, in bytes.
    num_skin_refs = 0            #item   99     int, The number of replaceable textures for the model.
    num_skin_groups = 0          #item   100    int, The number of texture groups for the model.
    skin_refs_offset = 0         #item   101    int, The skin ref data starting point in the file, in bytes.
    num_bodyparts = 0            #item   102    int, The number of body parts for the model.
    bodyparts_offset = 0         #item   103    int, The body parts data starting point in the file, in bytes.
    num_attachments = 0          #item   104    int, The number of queryable attachable points for the model.
    attachments_offset = 0       #item   105    int, The queryable attachable points data starting point in the file, in bytes.
    sound_table = 0              #item   106    int, unknown item.
    sound_table_offset = 0       #item   107    int, The sound table data starting point in the file, in bytes.
    sound_groups = 0             #item   108    int, unknown item.
    sound_groups_offset = 0      #item   109    int, The sound groups data starting point in the file, in bytes.
    num_transitions = 0          #item   110    int, The number of animation node to animation node transition graph.
    transitions_offset = 0       #item   111    int, The transitions data starting point in the file, in bytes.

    binary_format = "<4ci64ci3f3f3f3f3f27i" #little-endian (<), see #item descriptions above.

    #mdl data objects
    bones = []
    skins_group = []
    skinrefs = []
    demand_seq_groups = []
    bone_controls = []
    sequence_descs = []
    hitboxes = {}
    attachments = {}
    bodyparts = []

    tex_coords = []
    faces = []
    vertices = []
    tagsgroup = []

    curskinfamily = 0

    def __init__ (self):
        self.bones = []             # A list of the bones.
        self.skins_group = []       # A list of the skins.
        self.skinrefs = []          # A list of the skinref data.
        self.demand_seq_groups = [] # A list of the demand sequence groups.
        self.bone_controls = []     # A list of the bone controllers.

    #### SEE OTHER HL IMPORTER USE THIS AS WORD SEARCH
        self.sequence_descs = []    # A list of the sequence descriptions (leads into grouped frames).
        self.hitboxes = {}          # A dictionary list of the hitboxes, the key being the bone number it is attached to.
        self.attachments = {}       # A dictionary list of the attachments, the key being the bone number it is attached to.
        self.bodyparts = []         # A list of the bodyparts.

        self.tex_coords = []        # A list of integers, 1 for "onseam" and 2 for the s,t or u,v texture coordinates.
        self.faces = []             # A list of the triangles.
        self.vertices = []          # A list of the vertexes.
        self.tagsgroup = []         # A list of tag (attachment) groups to store tag frames into for each tag.

        self.curskinfamily = 0 #Select a skin family to use. Default = 0.


    def load(self, file, folder_name, mdl_name, message):
        global progressbar, UseName
        # file = the actual .mdl model file being read in, imported.
        # folder_name = name of the folder the .mdl model file is in.
        # mdl_name = just the basic name of the .mdl file, ex: barney
        # message = "" and empty string to add needed messages to.
        FolderName = folder_name
        FileName = mdl_name
        FolderName = FolderName.split("_")
        for i in range(len(FolderName)):
            if not FolderName[i][0].isdigit():
                FolderName[i] = FolderName[i].capitalize()
        FolderName = "".join(FolderName)
        FileName = FileName.split("_")
        for i in range(len(FileName)):
            if not FileName[i][0].isdigit():
                FileName[i] = FileName[i].capitalize()
        FileName = "".join(FileName)
        UseName = "".join([FolderName, FileName])

        # To avoid dupeicate skin names from being imported, we change the name.
        used_skin_names = []
        for item in editor.Root.subitems:
            if item.type == ":mc" and not item.name.startswith(UseName + "_"):
                for skin in item.dictitems['Skins:sg'].subitems:
                    used_skin_names = used_skin_names + [skin.shortname]
        def check_skin_name(skin_name, used_skin_names=used_skin_names):
            test_name = skin_name.split(".")
            count = 0
            if test_name[0] in used_skin_names:
                for name in used_skin_names:
                    if name == test_name[0]:
                        count += 1
                skin_name = test_name[0] + "Dupe" + str(count) + "." + test_name[1]
            return skin_name

        self.file = file # To pass the file being read in, when needed.
        ofsBegin = self.ofsBegin = file.tell()
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.ident = data[0] + data[1] + data[2] + data[3]
        self.version = data[4]
        char = 64 + 5 # The above data items = 5.
        for c in xrange(5, char):
            if data[c] == "\x00":
                continue
            self.name = self.name + data[c]

        if (self.ident != "IDST" or self.version != 10): # Not a valid Half-Life MDL file.
            if self.version == 6 or self.version == 44:
                return None, None, None, None, self.ident, self.version
            else:
                return None, None, None, None, self.ident, self.version

        self.length = data[69]
        self.eyeposition = data[70],data[71],data[72]
        self.min = data[73],data[74],data[75]
        self.max = data[76],data[77],data[78]
        self.bbmin = data[79],data[80],data[81]
        self.bbmax = data[82],data[83],data[84]
        self.flags = data[85]
        self.num_bones = data[86]
        self.bones_offset = data[87]
        self.num_bone_controls = data[88]
        self.bone_controls_offset = data[89]
        self.num_hitboxes = data[90]
        self.hitboxes_offset = data[91]
        self.num_anim_seq = data[92] #FIXME: Evil override to make things load faster for testing!
        self.anim_seq_offset = data[93]
        self.num_demand_hdr_groups = data[94]
        self.demand_hdr_offset = data[95]
        self.num_textures = data[96]
        self.texture_index_offset = data[97]
        self.texture_data_offset = data[98]
        self.num_skin_refs = data[99]
        self.num_skin_groups = data[100]
        self.skin_refs_offset = data[101]
        self.num_bodyparts = data[102]
        self.bodyparts_offset = data[103]
        self.num_attachments = data[104]
        self.attachments_offset = data[105]
        self.sound_table = data[106]
        self.sound_table_offset = data[107]
        self.sound_groups = data[108]
        self.sound_groups_offset = data[109]
        self.num_transitions = data[110]
        self.transitions_offset = data[111]
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Data Size in bytes: " + str(file.tell()))
            tobj.logcon ("#####################################################################")

        ## Load the bones data.
        file.seek(ofsBegin + self.bones_offset, 0)
        for i in xrange(self.num_bones):
            bone = mdl_bone()
            bone.bone_index = i
            bone.load(file)
          #  bone.dump()
            self.bones.append(bone) # Correct way! Why put in list, then dig into list to get it back! 8-| Change others where needed.

        ## Load the bone controllers data.
        file.seek(ofsBegin + self.bone_controls_offset, 0)
        for i in xrange(self.num_bone_controls):
            control = mdl_bone_control().load(file)
            self.bone_controls.append(control)
          #  control.dump()
                  
        ## Load the hitboxes data, can only have one per bone and visa versa.
        file.seek(ofsBegin + self.hitboxes_offset, 0)
        for i in xrange(self.num_hitboxes):
            hitbox = mdl_hitbox().load(file)
            self.hitboxes[hitbox.bone] = [hitbox.bbmin, hitbox.bbmax]
          #  hitbox.dump()


        ## Load the animblocks.
        # load the header for demand sequence group data
        file.seek(ofsBegin + self.demand_hdr_offset, 0)
        for i in xrange(self.num_demand_hdr_groups):
            self.demand_seq_groups.append(mdl_demand_group())
            self.demand_seq_groups[i].load(file)
          #  self.demand_seq_groups[i].dump()

        # load the skins group data
        file.seek(ofsBegin + self.texture_index_offset, 0)
        for i in xrange(self.num_textures):
            self.skins_group.append(mdl_skin_info())
            self.skins_group[i].load(file)
          #  self.skins_group[i].dump()

        # load the skin image data for each skin
        for skin in self.skins_group:
            file.seek(ofsBegin + skin.skin_offset, 0)
            #Pixel data first
            temp_data = file.read(struct.calcsize("B")*skin.width*skin.height)
            data = struct.unpack("B"*skin.width*skin.height, temp_data)
            ImageData=''
            Padding=(int(((skin.width * 8) + 31) / 32) * 4) - (skin.width * 1)
            for y in range(skin.height):
                for x in range(skin.width):
                    ImageData += struct.pack("B", data[(skin.height-y-1) * skin.width+x])
                ImageData += "\0" * Padding
            skin.ImageData = ImageData
            #Palette data is next
            Palette=''
            for i in range(0, 256):
                temp_data = file.read(struct.calcsize("BBB"))
                #No need to unpack; we would repack it immediately anyway: "BBB" --> "BBB"
                Palette += temp_data
            skin.Palette = Palette

        # load the skinref/skinfamilies data
        binary_format = "<h"
        file.seek(ofsBegin + mdl.skin_refs_offset, 0)
        for i in xrange(self.num_skin_groups):
            x_skinrefs = []
            for j in xrange(self.num_skin_refs):
                temp_data = file.read(struct.calcsize(binary_format))
                data = struct.unpack(binary_format, temp_data)
                x_skinrefs += [data[0]]
            self.skinrefs += [x_skinrefs]


        ## Setup items needed for QuArK.
        ComponentList = []
        message = ""


        ## Load the file textures info data.
        # Check if this model only has textures for another model.
        if self.num_bodyparts == 0 and len(self.skins_group) != 0:
            message = message + "This model only has textures.\r\n\r\nYou need to import the models that use them\r\nmove them to their proper skin folder\r\nand delete this component.\r\n================================\r\n\r\n"
            # Now we create a dummy Import Component to place the textures into.
            name = file.name.replace("\\", "/")
            try:
                name = name.rsplit("/", 1)
                name = name[len(name)-1]
            except:
                pass
            name = name.split(".")[0]
            Component = quarkx.newobj(UseName + '_' + name + ' textures' + ':mc')
            sdogroup = quarkx.newobj('SDO:sdo')
            # Create the "Skins:sg" group.
            skinsize = (self.skins_group[0].width, self.skins_group[0].height)
            skingroup = quarkx.newobj('Skins:sg')
            skingroup['type'] = chr(2)
            for skin in self.skins_group:
                skin_name = skin.name # Gives the skin name and type, ex: head.bmp
                skin_name = check_skin_name(skin_name)
                #Create the QuArK skin objects
                newskin = quarkx.newobj(skin_name)
                newskin['Size'] = (float(skin.width), float(skin.height))
                newskin['Image1'] = skin.ImageData
                newskin['Pal'] = skin.Palette
                newskin['HL_skin_flags'] = str(skin.flags)
                skingroup.appenditem(newskin)
            # Create the "Frames:fg" group with dummy frame.
            framesgroup = quarkx.newobj('Frames:fg')
            frame = quarkx.newobj('baseframe:mf')
            frame['Vertices'] = ''
            framesgroup.appenditem(frame)

            Component['skinsize'] = skinsize
            Component['show'] = chr(1)
            Component.appenditem(sdogroup)
            Component.appenditem(skingroup)
            Component.appenditem(framesgroup)

            ComponentList = ComponentList + [Component]

        # load the animation sequence descriptions data.
        file.seek(ofsBegin + self.anim_seq_offset, 0)
        for i in xrange(self.num_anim_seq):
            self.sequence_descs.append(mdl_sequence_desc()) # Just need to read in but not append to list if not selected to load.
            self.sequence_descs[i].load(file)
          #  self.sequence_descs[i].dump()


        ## Load the bodyparts data.
        file.seek(ofsBegin + self.bodyparts_offset, 0)
        for i in xrange(self.num_bodyparts):
            body_part_index = mdl_bodypart()
            body_part_index.load(file)
            self.bodyparts.append(body_part_index)
          #  self.bodyparts[i].dump()
            file.seek(ofsBegin + self.bodyparts[i].model_offset, 0)
            # load its models data
            for j in xrange(self.bodyparts[i].nummodels):
                self.bodyparts[i].models.append(mdl_model())
                self.bodyparts[i].models[j].load(file)
              #  self.bodyparts[i].models[j].dump()


        ## Load the bodyparts models meshes data
        for i in xrange(self.num_bodyparts):
            for j in xrange(self.bodyparts[i].nummodels):
                file.seek(ofsBegin + self.bodyparts[i].models[j].mesh_offset, 0)
                name = self.bodyparts[i].models[j].name
                name = name.replace("\\", "/")
                if name.find("/") != -1:
                    name = name.rsplit("/", 1)[1]
                name = name.replace(".", "")
                nummesh = self.bodyparts[i].models[j].nummesh


                ## Load the meshes data
                for k in xrange(nummesh):
                    self.bodyparts[i].models[j].meshes.append(mdl_mesh())
                    self.bodyparts[i].models[j].meshes[k].load(file)
                  #  self.bodyparts[i].models[j].meshes[k].dump()


                    ## Now we start creating our Import Component and name it.
                    Component = quarkx.newobj(UseName + '_' + name + ' ' + str(k) + ':mc')
                    sdogroup = quarkx.newobj('SDO:sdo')
                    # Create the "Skins:sg" group.
                    skinref = self.bodyparts[i].models[j].meshes[k].skinref
                    try:
                        skin_index = self.skinrefs[self.curskinfamily][skinref]
                    except:
                        skinsize = (256, 256)
                    else:
                        skinsize = (self.skins_group[skin_index].width, self.skins_group[skinref].height)
                    skingroup = quarkx.newobj('Skins:sg')
                    skingroup['type'] = chr(2)
                    # Create the "Frames:fg" group.
                    framesgroup = quarkx.newobj('Frames:fg')
                    
                    Component['skinsize'] = skinsize
                    Component['show'] = chr(1)
                    Component.appenditem(sdogroup)
                    Component.appenditem(skingroup)
                    Component.appenditem(framesgroup)

                    ## Add bone controls if any.
                    for control in self.bone_controls:
                        bone = self.bones[control.bone]
                        Component['bone_control_'+ str(control.index)] = UseName + '_' + bone.name + ':bone'
                    ComponentList = ComponentList + [Component]


            ## Load the attachments data, for position processing with bones they belong to.
        if len(self.bones) != 0 and len(ComponentList) != 0 and self.num_attachments != 0:
            file.seek(ofsBegin + self.attachments_offset, 0)
            tag_comp = ComponentList[0] # Reset this if needed later.
            for i in xrange(self.num_attachments):
                attachment = mdl_attachment().load(file)
                if not self.attachments.has_key(attachment.bone):
                    self.attachments[attachment.bone] = {}
                    self.attachments[attachment.bone]['bone_name'] = UseName + '_' + self.bones[attachment.bone].name + ':bone'
                    self.attachments[attachment.bone]['tag_pos'] = {}
                self.attachments[attachment.bone]['tag_pos'][i] = attachment.org
              #  attachment.dump()


                ## Create tags (attachments) groups if any. We need to keep these separate for each complete model loaded.
                tag_name = 'tag_weapon' + str(i+1)
                newtag = quarkx.newobj(UseName + '_' + tag_name + ':tag')
                newtag['Component'] = tag_comp.name
                newtag['bone'] = self.attachments[attachment.bone]['bone_name']
                self.tagsgroup = self.tagsgroup + [newtag]
                if i == 0:
                    tag_comp['Tags'] = tag_name
                else:
                    tag_comp['Tags'] = tag_comp.dictspec['Tags'] + ", " + tag_name

        ## Create the bones, if any.
        QuArK_bones = [] # A list to store all QuArK bones created.
        tagsgroup_count = 0
        if len(self.bones) != 0 and len(ComponentList) != 0:
            for mdlbone in xrange(len(self.bones)):
                bone = self.bones[mdlbone]
                new_bone = quarkx.newobj(UseName + '_' + bone.name + ':bone')
                new_bone['type'] = 'HL1' # Set our bone type.
                new_bone['flags'] = (0,0,0,0,0,0)
                new_bone['show'] = (1.0,)
                bone_pos = quarkx.vect(bone.value[0], bone.value[1], bone.value[2])
                quat = EulerAngle2Quaternion([bone.value[3], bone.value[4], bone.value[5]])
                tempmatrix = quaternion2matrix(quat)
                #new_bone['quaternion'] = (qx,qy,qz,qw)
                bone_matrix = quarkx.matrix((tempmatrix[0][0], tempmatrix[0][1], tempmatrix[0][2]), (tempmatrix[1][0], tempmatrix[1][1], tempmatrix[1][2]), (tempmatrix[2][0], tempmatrix[2][1], tempmatrix[2][2]))
                new_bone['parent_index'] = str(bone.parent)
                if bone.parent != -1:
                    parent_bone = QuArK_bones[bone.parent]
                    parent_pos = parent_bone.position
                    parent_matrix = parent_bone.rotmatrix
                    bone_pos = parent_pos + (parent_matrix * bone_pos)
                    bone_matrix = parent_matrix * bone_matrix

                if self.num_attachments != 0 and self.attachments.has_key(mdlbone):
                    tags = self.attachments[mdlbone]['tag_pos']
                    bone_name = self.attachments[mdlbone]['bone_name']
                    for tag in tags.keys():
                        Tpos = tags[tag]
                        Tpos = quarkx.vect((Tpos[0], Tpos[1], Tpos[2]))
                        Tpos = bone_pos + (bone_matrix * Tpos)
                        Tpos = Tpos.tuple
                        tagframe = quarkx.newobj('Tag baseframe:tagframe')
                        tagframe['show'] = (1.0,)
                        tagframe['origin'] = Tpos
                        tagframe['rotmatrix'] = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
                        tagframe['bone'] = bone_name
                        self.tagsgroup[tagsgroup_count].appenditem(tagframe)
                        tagsgroup_count = tagsgroup_count + 1

                new_bone.position = bone_pos
                new_bone.rotmatrix = bone_matrix
                new_bone['position'] = new_bone.position.tuple
                tempmatrix = new_bone.rotmatrix.tuple
                new_bone['rotmatrix'] = (tempmatrix[0][0], tempmatrix[0][1], tempmatrix[0][2], tempmatrix[1][0], tempmatrix[1][1], tempmatrix[1][2], tempmatrix[2][0], tempmatrix[2][1], tempmatrix[2][2])

                if bone.parent == -1:
                    new_bone['parent_name'] = "None"
                    new_bone['bone_length'] = (0.0, 0.0, 0.0)
                else:
                    new_bone['parent_name'] = parent_bone.name
                    new_bone['bone_length'] = (-quarkx.vect(QuArK_bones[int(new_bone.dictspec['parent_index'])].dictspec['position']) + quarkx.vect(new_bone.dictspec['position'])).tuple
                new_bone['component'] = ComponentList[0].name # Reset this if needed later.
                new_bone['draw_offset'] = (0.0, 0.0, 0.0)
                new_bone['_color'] = MapColor("BoneHandles", 3)
                new_bone.vtxlist = {}
                new_bone.vtx_pos = {}
                new_bone['scale'] = (1.0,) # Written this way to store it as a tuple.
                new_bone['org_scale'] = new_bone.dictspec['scale']
                # Add bone control if any.
                for control in self.bone_controls:
                    if control.bone == mdlbone:
                        new_bone['control_type'] = str(control.type)
                        new_bone['control_start'] = str(control.start)
                        new_bone['control_end'] = str(control.end)
                        new_bone['control_rest'] = str(control.rest)
                        new_bone['control_index'] = str(control.index)
                QuArK_bones = QuArK_bones + [new_bone]

                # Sets up the 'bonelist' entry of editor.ModelComponentList for the 'baseframe' of all importing bones
                bonedata = {}
                bonedata['frames'] = {}
                bonedata['frames']['baseframe:mf'] = {}
                bonedata['frames']['baseframe:mf']['position'] = new_bone.dictspec['position']
                bonedata['frames']['baseframe:mf']['rotmatrix'] = new_bone.rotmatrix.tuple
                editor.ModelComponentList['bonelist'][new_bone.name] = bonedata
                if self.hitboxes.has_key(mdlbone):
                    bboxname = new_bone.name.replace(":bone", ":p")
                    editor.ModelComponentList['bboxlist'][bboxname] = {}
                    editor.ModelComponentList['bboxlist'][bboxname]['size'] = self.hitboxes[mdlbone]

        # load the meshes triangles data
        byte_count = 0
        Component_index = -1
        for i in xrange(self.num_bodyparts):
            for j in xrange(self.bodyparts[i].nummodels):
                # Make & fill vertex dictionary list to convert vertex_indexes and
                #    breakdown by Component later in the triangles Tris section below.
                mesh_verts = {}
                file.seek(ofsBegin + self.bodyparts[i].models[j].vert_offset, 0)
                for k in xrange(self.bodyparts[i].models[j].numverts):
                    self.bodyparts[i].models[j].verts.append(mdl_vertex())
                    self.bodyparts[i].models[j].verts[k].load(file)
                  #  self.bodyparts[i].models[j].verts[k].dump()
                    mesh_verts[k] = self.bodyparts[i].models[j].verts[k].v

                # Make & fill vtxlist dictionary list to assign vertexes to their bones and
                #    breakdown by Component later in the triangles Tris section below.
                vtxlist = {}
                # load the model's verts info data.
                # Gives a bone_index for each Component's vertex that is assigned to that bone.
                file.seek(ofsBegin + self.bodyparts[i].models[j].vert_info_offset, 0)
                for k in xrange(self.bodyparts[i].models[j].numverts):
                    self.bodyparts[i].models[j].verts_info.append(mdl_vert_info())
                    self.bodyparts[i].models[j].verts_info[k].load(file)
                    vtxlist[k] = self.bodyparts[i].models[j].verts_info[k].bone_index
                  #  self.bodyparts[i].models[j].verts_info[k].dump(i, j, k)

                # load the model's normals info data. (not using these but needed for exporting)
                # Gives a bone_index for each Component's normal that is assigned to that bone.
        #        file.seek(ofsBegin + self.bodyparts[i].models[j].norm_info_offset, 0)
        #        binary_format = "<B" #little-endian (<), single byte (unsigned int).
        #        for k in xrange(self.bodyparts[i].models[j].numnorms):
        #            temp_data = file.read(struct.calcsize(binary_format))
        #            data = struct.unpack(binary_format, temp_data)

                # load the model's normals data. (not using these but needed for exporting)
                # Gives each normal's x,y,z position.
        #        file.seek(ofsBegin + self.bodyparts[i].models[j].norm_offset, 0)
        #        binary_format = "<3f" #little-endian (<), 3 floats, 4 bytes per float.
        #        for k in xrange(self.bodyparts[i].models[j].numnorms):
        #          #  normals = []
        #          #  for l in xrange(self.bodyparts[i].models[j].meshes[k].numnorms):
        #            temp_data = file.read(struct.calcsize(binary_format))
        #            data = struct.unpack(binary_format, temp_data)


                # Now get the meshes triangles data.
                for k in xrange(self.bodyparts[i].models[j].nummesh):
                    Component_index += 1
                    start = self.bodyparts[i].models[j].meshes[k].tri_offset
                    numtris = self.bodyparts[i].models[j].meshes[k].numtris
                  #  numnorms = self.bodyparts[i].models[j].meshes[k].numnorms # See about normals info and data above.
                    triangles = []
                    file.seek(ofsBegin + start, 0)
                    if k == self.bodyparts[i].models[j].nummesh-1:
                        if j == self.bodyparts[i].nummodels-1:
                            if self.texture_index_offset != 0:
                                end = self.texture_index_offset
                            else:
                                end = start + (self.bodyparts[i].models[j].meshes[k].numtris * 10) # 1 short (for id) + 4 shorts at 2 bytes per short.
                        else:
                            end = self.bodyparts[i].models[j+1].vert_info_offset
                    else:
                        end = self.bodyparts[i].models[j].meshes[k+1].tri_offset
                    tri_count = 0

                    # Note: To create the triangle faces this code doesn't actually use the self.bodyparts[i].models[j].meshes[k].numtris variable.
                    # Instead it reads through the triangle data, which is all "signed short int" (or "h") types of 2 bytes each.
                    # The first "h" read in, and for following groups, designates if the following group, or number,
                    #    of "h"s are for a "Fan", "List" or "Strip" type group. That same designating "h" also gives the
                    #    count value, or number, of how many "h"s are in that group.
                    while 1:
                        binary_format = "<h"
                        size = struct.calcsize(binary_format)
                        byte_count = byte_count + size
                        if byte_count + start >= end and len(triangles) == numtris:
                            byte_count = 0
                            break
                        temp_data = file.read(size)
                        data = struct.unpack(binary_format, temp_data)
                        tris_group = int(data[0])
                        skinref = self.bodyparts[i].models[j].meshes[k].skinref
                        try:
                            skin_index = self.skinrefs[self.curskinfamily][skinref]
                        except:
                            skinwidth = skinheight = 256
                            skinflags = 0
                        else:
                            skinwidth = float(self.skins_group[skinref].width)
                            skinheight = float(self.skins_group[skinref].height)
                            skinflags = self.skins_group[skin_index].flags
                        if tris_group < 0:
                            # If the designating "signed short int" (or "h") is a negative value then the group is a Triangle Fan.
                            # The negative designating "h" is then turned into a positive value so it can be used as the count size of the group.
                            tris_group = -tris_group
                            for l in xrange(tris_group):
                                self.bodyparts[i].models[j].meshes[k].triangles.append(mdl_triangle())
                                triangle, byte_count = self.bodyparts[i].models[j].meshes[k].triangles[tri_count].load(file, byte_count)
                                if triangle.index1uv == 0:
                                    index1uv = 1.0
                                else:
                                    index1uv = float(triangle.index1uv)
                                if l == 0:
                                    vtx0 = triangle.index0vert
                                    vtx0uv0 = int(round((skinwidth/index1uv)*skinwidth))
                                    vtx0uv1 = int(round((skinheight/index1uv)*skinheight))
                                    vtx0u = triangle.index2u
                                    vtx0v = triangle.index3v
                                elif l == 1:
                                    vtx1 = triangle.index0vert
                                    vtx1uv0 = int(round((skinwidth/index1uv)*skinwidth))
                                    vtx1uv1 = int(round((skinheight/index1uv)*skinheight))
                                    vtx1u = triangle.index2u
                                    vtx1v = triangle.index3v
                                else:
                                    vtx2 = triangle.index0vert
                                    vtx2uv0 = int(round((skinwidth/index1uv)*skinwidth))
                                    vtx2uv1 = int(round((skinheight/index1uv)*skinheight))
                                    vtx2u = triangle.index2u
                                    vtx2v = triangle.index3v
                                    if skinflags == 3:
                                        triangles = triangles + [[[vtx0,vtx0uv0,vtx0uv1], [vtx1,vtx1uv0,vtx1uv1], [vtx2,vtx2uv0,vtx2uv1]]]
                                    else:
                                        triangles = triangles + [[[vtx0,vtx0u,vtx0v], [vtx1,vtx1u,vtx1v], [vtx2,vtx2u,vtx2v]]]
                                    vtx1 = vtx2
                                    vtx1uv0 = vtx2uv0
                                    vtx1uv1 = vtx2uv1
                                    vtx1u = vtx2u
                                    vtx1v = vtx2v
                              #  self.bodyparts[i].models[j].meshes[k].triangles[tri_count].dump()
                                tri_count = tri_count + 1
                                if byte_count + start >= end and len(triangles) == numtris:
                                    break
                        else:
                            # If the designating "signed short int" (or "h") is NOT a negative value then the group is a
                            # Triangle Strip or a Triangle List, which are handled the same way.
                            for l in xrange(tris_group):
                                self.bodyparts[i].models[j].meshes[k].triangles.append(mdl_triangle())
                                triangle, byte_count = self.bodyparts[i].models[j].meshes[k].triangles[tri_count].load(file, byte_count)
                                index1uv = float(triangle.index1uv)
                                if triangle.index1uv == 0:
                                    index1uv = 1.0
                                else:
                                    index1uv = float(triangle.index1uv)
                                if l == 0:
                                    vtx0 = triangle.index0vert
                                    vtx0uv0 = int(round((skinwidth/index1uv)*skinwidth))
                                    vtx0uv1 = int(round((skinheight/index1uv)*skinheight))
                                    vtx0u = triangle.index2u
                                    vtx0v = triangle.index3v
                                elif l == 1:
                                    vtx1 = triangle.index0vert
                                    vtx1uv0 = int(round((skinwidth/index1uv)*skinwidth))
                                    vtx1uv1 = int(round((skinheight/index1uv)*skinheight))
                                    vtx1u = triangle.index2u
                                    vtx1v = triangle.index3v
                                else:
                                    vtx2 = triangle.index0vert
                                    vtx2uv0 = int(round((skinwidth/index1uv)*skinwidth))
                                    vtx2uv1 = int(round((skinheight/index1uv)*skinheight))
                                    vtx2u = triangle.index2u
                                    vtx2v = triangle.index3v
                                    if skinflags == 3:
                                        triangles = triangles + [[[vtx0,vtx0uv0,vtx0uv1], [vtx1,vtx1uv0,vtx1uv1], [vtx2,vtx2uv0,vtx2uv1]]]
                                    else:
                                        triangles = triangles + [[[vtx0,vtx0u,vtx0v], [vtx1,vtx1u,vtx1v], [vtx2,vtx2u,vtx2v]]]
                                    if not l&1: # This test if a number is even.
                                        vtx0 = vtx2
                                        vtx0uv0 = vtx2uv0
                                        vtx0uv1 = vtx2uv1
                                        vtx0u = vtx2u
                                        vtx0v = vtx2v
                                    else: # else it is odd.
                                        vtx1 = vtx2
                                        vtx1uv0 = vtx2uv0
                                        vtx1uv1 = vtx2uv1
                                        vtx1u = vtx2u
                                        vtx1v = vtx2v
                              #  self.bodyparts[i].models[j].meshes[k].triangles[tri_count].dump()
                                tri_count = tri_count + 1
                                if byte_count + start >= end and len(triangles) == numtris:
                                    break

                    # Create this Component's Tris and "baseframe".
                    Component = ComponentList[Component_index]
                    comp_name = Component.name
                    Tris = ''
                    vertex = []
                    frame = quarkx.newobj('baseframe:mf')
                    # Make a HL vert --> QuArK vert translation table
                    numverts = self.bodyparts[i].models[j].numverts
                    vert_converter = [-1] * numverts
                    QuArK_verts_so_far = 0
                    for tri in triangles:
                        for vtx in tri:
                            vert_index = vert_converter[vtx[0]]
                            if vert_index == -1:
                                # This is a new vertex
                                vert_pos = mesh_verts[vtx[0]]
                                bone = QuArK_bones[vtxlist[vtx[0]]]
                                bp = bone.position
                                br = bone.rotmatrix
                                vert_pos = quarkx.vect(vert_pos[0], vert_pos[1], vert_pos[2])
                                vert_pos = bp + (br * vert_pos)
                                vert_pos = vert_pos.tuple
                                vertex = vertex + [vert_pos[0], vert_pos[1], vert_pos[2]]
                                vert_index = QuArK_verts_so_far
                                QuArK_verts_so_far += 1
                                vert_converter[vtx[0]] = vert_index
                                list = bone.vtxlist
                                if not list.has_key(comp_name):
                                    list[comp_name] = []
                                if not vert_index in list[comp_name]:
                                    list[comp_name].append(vert_index)
                                    bone.vtxlist = list
                            u = vtx[1]
                            v = vtx[2]
                            Tris = Tris + struct.pack("Hhh", vert_index, u, v)
                    frame['Vertices'] = vertex
                    Component.dictitems['Frames:fg'].appenditem(frame)
                    Component['Tris'] = Tris

                    # Get this Component's skin(s).
                    skinref = self.bodyparts[i].models[j].meshes[k].skinref
                    try:
                        skin_index = self.skinrefs[self.curskinfamily][skinref]
                    except:
                        skin_index = -1
                    if len(self.skins_group) != 0 and skin_index != -1:
                        skin_name = self.skins_group[skin_index].name # Gives the skin name and type, ex: head.bmp
                        skin_flags = str(self.skins_group[skin_index].flags)
                        try:
                            #Create the QuArK skin objects
                            skin = self.skins_group[skin_index]
                            new_skin_name = check_skin_name(skin_name)
                            newskin = quarkx.newobj(new_skin_name)
                            skinsize = newskin['Size'] = (float(skin.width), float(skin.height))
                            newskin['Image1'] = skin.ImageData
                            newskin['Pal'] = skin.Palette
                            newskin['HL_skin_flags'] = skin_flags
                            Component.dictitems['Skins:sg'].appenditem(newskin)
                            Component['skinsize'] = skinsize
                        except:
                            # Try to find this Component's skins.
                                if os.path.isfile(skin_name): # We try to find the skin in the models folder.
                                    skinname = folder_name + "/" + skin_name
                                    skinname = check_skin_name(skinname)
                                    skin = quarkx.newobj(skinname)
                                    foundimage = os.getcwd() + "/" + skin_name
                                    image = quarkx.openfileobj(foundimage)
                                    skin['Image1'] = image.dictspec['Image1']
                                    if image.dictspec.has_key('Pal'):
                                        skin['Pal'] = image.dictspec['Pal']
                                    skin['HL_skin_flags'] = skin_flags
                                    skinsize = skin['Size'] = image.dictspec['Size']
                                    Component.dictitems['Skins:sg'].appenditem(skin)
                                    Component['skinsize'] = skinsize

                # Update the bones.vtx_list, dictspec['Component'] and ['draw_offset'] items.
                for bone_index in xrange(self.num_bones):
                    bone = QuArK_bones[bone_index]
                    if bone.vtxlist != {}:
                        vtxcount = 0
                        usekey = None
                        for key in bone.vtxlist.keys():
                            if len(bone.vtxlist[key]) > vtxcount:
                                usekey = key
                                vtxcount = len(bone.vtxlist[key])
                        if usekey is not None:
                            temp = {}
                            temp[usekey] = bone.vtxlist[usekey]
                            bone.vtx_pos = temp
                            bone['component'] = usekey
                            for Component in ComponentList:
                                if Component.name == usekey and Component.dictitems['Frames:fg'].subitems != 0:
                                    vertices = Component.dictitems['Frames:fg'].subitems[0].vertices
                                    vtxlist = temp[usekey]
                                    vtxpos = quarkx.vect(0.0, 0.0, 0.0)
                                    for vtx in vtxlist:
                                        vtxpos = vtxpos + vertices[vtx]
                                    vtxpos = vtxpos/ float(len(vtxlist))
                                    bone['draw_offset'] = (bone.position - vtxpos).tuple
                                    break

        # Setup the bones, if any, position & rotmatrix of the animation frames.
        if len(self.bones) != 0 and len(ComponentList) != 0:
            SetUpBones(self, QuArK_bones)

            pseqdesc = self.sequence_descs
            bonelist = editor.ModelComponentList['bonelist']
            for Component in range(len(ComponentList)):
                comp = ComponentList[Component]
                comp_name = comp.name
                Strings[2462] = comp.shortname + "\n" + Strings[2462]
                progressbar = quarkx.progressbar(2462, self.num_anim_seq)
                framesgroup = comp.dictitems['Frames:fg']
                baseframe = framesgroup.subitems[0]
                meshverts = baseframe.vertices
                for m_sequence in xrange(self.num_anim_seq):
                    progressbar.progress()
                    seq = pseqdesc[m_sequence]
                    seq_name = seq.label
                    for m_frame in xrange(seq.numframes):
                        frame_name = seq_name + " frame " + str(m_frame+1)
                        new_frame = baseframe.copy()
                        new_frame.shortname = frame_name
                        new_frame['frame_flags'] = str(seq.flags)
                        newverts = [quarkx.vect(0.0, 0.0, 0.0)] * len(meshverts)
                        for bone_index in range(len(QuArK_bones)):
                            pbone = QuArK_bones[bone_index]
                            if pbone.vtxlist.has_key(comp_name):
                                vtxs = pbone.vtxlist[comp_name]
                                for vert_index in vtxs:
                                    Bpos_old = quarkx.vect(bonelist[pbone.name]['frames']['baseframe:mf']['position'])
                                    Brot_old = quarkx.matrix(bonelist[pbone.name]['frames']['baseframe:mf']['rotmatrix'])
                                    Bpos_new = quarkx.vect(bonelist[pbone.name]['frames'][frame_name+':mf']['position'])
                                    Brot_new = quarkx.matrix(bonelist[pbone.name]['frames'][frame_name+':mf']['rotmatrix'])
                                    vert_pos = meshverts[vert_index]
                                    vert_pos = (~Brot_old) * (vert_pos - Bpos_old)
                                    newverts[vert_index] += Bpos_new + (Brot_new * vert_pos)
                        new_frame.vertices = newverts
                        framesgroup.appenditem(new_frame)
                Strings[2462] = Strings[2462].replace(comp.shortname + "\n", "")
                progressbar.close()

        return self, ComponentList, QuArK_bones, message, self.tagsgroup, self.version

    def dump(self):
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + str(self.ident))
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("name: " + str(self.name))
            tobj.logcon ("length: " + str(self.length))
            tobj.logcon ("eyeposition: " + str(self.eyeposition))
            tobj.logcon ("min: " + str(self.min))
            tobj.logcon ("max: " + str(self.max))
            tobj.logcon ("bbmin: " + str(self.bbmin))
            tobj.logcon ("bbmax: " + str(self.bbmax))
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("num_bones: " + str(self.num_bones))
            tobj.logcon ("bones_offset: " + str(self.bones_offset))
            tobj.logcon ("num_bone_controls: " + str(self.num_bone_controls))
            tobj.logcon ("bone_controls_offset: " + str(self.bone_controls_offset))
            tobj.logcon ("num_hitboxes: " + str(self.num_hitboxes))
            tobj.logcon ("hitboxes_offset: " + str(self.hitboxes_offset))
            tobj.logcon ("num_anim_seq: " + str(self.num_anim_seq))
            tobj.logcon ("anim_seq_offset: " + str(self.anim_seq_offset))
            tobj.logcon ("num_demand_hdr_groups: " + str(self.num_demand_hdr_groups))
            tobj.logcon ("demand_hdr_offset: " + str(self.demand_hdr_offset))
            tobj.logcon ("num_textures: " + str(self.num_textures))
            tobj.logcon ("texture_index_offset: " + str(self.texture_index_offset))
            tobj.logcon ("texture_data_offset: " + str(self.texture_data_offset))
            tobj.logcon ("num_skin_refs: " + str(self.num_skin_refs))
            tobj.logcon ("num_skin_groups: " + str(self.num_skin_groups))
            tobj.logcon ("skin_refs_offset: " + str(self.skin_refs_offset))
            tobj.logcon ("num_bodyparts: " + str(self.num_bodyparts))
            tobj.logcon ("bodyparts_offset: " + str(self.bodyparts_offset))
            tobj.logcon ("num_attachments: " + str(self.num_attachments))
            tobj.logcon ("attachments_offset: " + str(self.attachments_offset))
            tobj.logcon ("sound_table: " + str(self.sound_table))
            tobj.logcon ("sound_table_offset: " + str(self.sound_table_offset))
            tobj.logcon ("sound_groups: " + str(self.sound_groups))
            tobj.logcon ("sound_groups_offset: " + str(self.sound_groups_offset))
            tobj.logcon ("num_transitions: " + str(self.num_transitions))
            tobj.logcon ("transitions_offset: " + str(self.transitions_offset))
            tobj.logcon ("")


########################
# To run this file
########################
def load_mdl(mdl_filename, folder_name, mdl_name):
    global tobj, logging, Strings, mdl
    # mdl_filename = the model file & full path being writen to, ex: C:\Half-Life\valve\models\player\barney\barney.mdl

    #read the file in
    file = open(mdl_filename, "rb")
    mdl = mdl_obj()
    message = ""
    MODEL, ComponentList, QuArK_bones, message, tagsgroup, version = mdl.load(file, folder_name, mdl_name, message)
    file.close()

    if logging == 1:
        mdl.dump() # Writes the file Header last to the log for comparison reasons.

    if MODEL is None:
        return None, None, message, tagsgroup, version

    return ComponentList, QuArK_bones, message, tagsgroup, version


def import_mdl_model(editor, mdl_filename, mdl_name):
    # mdl_filename = the full path and the full model file name that is open to write to.
    model_name = mdl_filename.split("\\")
    folder_name = model_name[len(model_name)-2]

    ComponentList, QuArK_bones, message, tagsgroup, version = load_mdl(mdl_filename, folder_name, mdl_name) # Loads the model.

    return ComponentList, QuArK_bones, message, tagsgroup, version


######################################################
# CALL TO PROCESS .mdl FILE (where it all starts off from)
######################################################
# The model file: root is the actual file,
# filename and gamename is the full path to
# and name of the .mdl file selected.
# For example:  C:\Half-Life\valve\models\player\barney\barney.mdl
# gamename is None.
def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename and gamename is the full path to"
    "and name of the .mdl file selected."
    "For example:  C:\Half-Life\valve\models\player\barney\barney.mdl"

    global editor, tobj, logging, importername, textlog, Strings
    import quarkpy.mdleditor
    editor = quarkpy.mdleditor.mdleditor
    mdl_name = filename.rsplit("\\", 1)[1]
    mdl_name = mdl_name.split(".")[0]
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
    ComponentList, QuArK_bones, message, tagsgroup, version = import_mdl_model(editor, filename, mdl_name)

    if ComponentList is None or len(ComponentList) == 0 or version is None or version != 10:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        if version == 6:
            quarkx.msgbox("Invalid Half-Life .mdl model.\nVersion number is " + str(version) + "\nThis is a Quake .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        elif version == 44:
            quarkx.msgbox("Invalid Half-Life .mdl model.\nVersion number is " + str(version) + "\nThis is a Half-Life 2 .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        elif version is not None:
            quarkx.msgbox("Invalid Half-Life .mdl model.\nID, Version number is " + str(message) + ", " + str(version) + "\nThis is another type .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        else:
            quarkx.msgbox("Invalid Half-Life .mdl model.\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        try:
            progressbar.close()
        except:
            pass
        return

    if editor.form is not None:
        undo = quarkx.action()
    editor_dictitems = editor.Root.dictitems

    # Import the tags (attachments) if any.
    for tag in range(len(tagsgroup)):
        if editor.form is not None:
            undo.put(editor_dictitems['Misc:mg'], tagsgroup[tag])
        else:
            editor_dictitems['Misc:mg'].appenditem(tagsgroup[tag])

    bonelist = editor.ModelComponentList['bonelist']
    bboxlist = editor.ModelComponentList['bboxlist']
    frame_name = ComponentList[0].dictitems['Frames:fg'].subitems[0].name
    if editor.form is not None:
        bboxgroup = quarkx.newobj("BBoxes " + UseName + ":bbg")
        bboxgroup['show'] = (1.0,)
        for bone in range(len(QuArK_bones)):
            bonename = QuArK_bones[bone].name
            bboxname = bonename.replace(":bone", ":p")
            if bboxlist.has_key(bboxname):
                bone_data = bonelist[bonename]
                bpos = quarkx.vect(bone_data['frames'][frame_name]['position'])
                brot = quarkx.matrix(bone_data['frames'][frame_name]['rotmatrix'])
                bbox = bboxlist[bboxname]['size']
                p = MakePoly(bonename, bpos, brot, bbox)
                bboxgroup.appenditem(p)

        if len(bboxgroup.subitems) !=0:
            undo.put(editor_dictitems['Misc:mg'], bboxgroup)
    else:
        bboxgroup = quarkx.newobj("BBoxes " + UseName + ":bbg")
        bboxgroup['show'] = (1.0,)
        for bone in range(len(QuArK_bones)):
            bonename = QuArK_bones[bone].name
            bboxname = bonename.replace(":bone", ":p")
            if bboxlist.has_key(bboxname):
                bone_data = bonelist[bonename]
                bpos = quarkx.vect(bone_data['frames'][frame_name]['position'])
                brot = quarkx.matrix(bone_data['frames'][frame_name]['rotmatrix'])
                bbox = bboxlist[bboxname]['size']
                p = MakePoly(bonename, bpos, brot, bbox)
                bboxgroup.appenditem(p)

        if len(bboxgroup.subitems) !=0:
            editor_dictitems['Misc:mg'].appenditem(bboxgroup)

    # Process the bones, if any.
    newbones = []
    for bone_index in range(len(QuArK_bones)): # Using list of ALL bones.
        boneobj = QuArK_bones[bone_index]
        bonename = boneobj.name
        # Builds the editor.ModelComponentList here.
        if boneobj.vtxlist != {}:
            for compname in boneobj.vtxlist.keys():
                if not editor.ModelComponentList.has_key(compname):
                    editor.ModelComponentList[compname] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
                if not editor.ModelComponentList[compname]['bonevtxlist'].has_key(bonename):
                    editor.ModelComponentList[compname]['bonevtxlist'][bonename] = {}
                for vtx_index in boneobj.vtxlist[compname]:
                    editor.ModelComponentList[compname]['bonevtxlist'][bonename][vtx_index] = {'color': '\x00\x00\xff'}
                    editor.ModelComponentList[compname]['weightvtxlist'][vtx_index] = {}
                    editor.ModelComponentList[compname]['weightvtxlist'][vtx_index][bonename] = {'weight_value': 1.0, 'color': quarkpy.mdlutils.weights_color(editor, 1.0)}
        parent_index = int(boneobj.dictspec['parent_index'])
        if parent_index < 0:
            newbones = newbones + [boneobj]
        else:
            QuArK_bones[parent_index].appenditem(boneobj)

    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        md2fileobj = quarkx.newfileobj("New model.md2")
        md2fileobj['FileName'] = 'New model.qkl'
        for bone in newbones:
            editor.Root.dictitems['Skeleton:bg'].appenditem(bone)
        for Component in ComponentList:
            editor.Root.appenditem(Component)
        md2fileobj['Root'] = editor.Root.name
        md2fileobj.appenditem(editor.Root)
        md2fileobj.openinnewwindow()
    else: # Imports a model properly from within the editor.
        for bone in newbones:
            undo.put(editor.Root.dictitems['Skeleton:bg'], bone)

        # Now we process the Components.
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

            compframes = editor.Root.currentcomponent.findallsubitems("", ':mf') # get all frames
            for compframe in compframes:
                compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.

            # This needs to be done for each component or bones will not work if used in the editor.
            quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
        editor.ok(undo, str(len(ComponentList)) + " .mdl Components imported")

        editor = None   #Reset the global again
        if message != "":
            quarkx.textbox("WARNING", message, quarkpy.qutils.MT_WARNING)

    try:
        progressbar.close()
    except:
        pass

    ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_md0_HL1_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".mdl Half-Life1 Importer", ".mdl file", "*.mdl", loadmodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_md0_HL1_import.py,v $
# Revision 1.17  2012/03/10 08:10:12  cdunde
# Added texture skin flag support.
#
# Revision 1.16  2012/03/03 07:26:35  cdunde
# Sync 2. Rearranged files and names to coincide better.
#
# Revision 1.15  2012/02/25 23:52:08  cdunde
# Fixes by DanielPharos for correct skin texture matching to components.
#
# Revision 1.14  2012/02/25 18:55:59  cdunde
# Rearranged files and names to coincide better.
#
# Revision 1.13  2012/02/18 23:27:13  cdunde
# Code by DanielPharos, final fix for correct imported animations.
#
# Revision 1.12  2012/02/11 21:46:24  cdunde
# To remove unused list and
# reposition data load call for posibale future max frames dialog feature.
#
# Revision 1.11  2012/01/11 19:25:45  cdunde
# To remove underscore lines from folder and model names then combine them with one
# underscore line at the end for proper editor functions separation capabilities later.
#
# Revision 1.10  2011/12/28 08:28:22  cdunde
# Setup importer bone['type'] not done yet.
#
# Revision 1.9  2011/12/23 03:15:18  cdunde
# To remove all importers bone ['type'] from ModelComponentList['bonelist'].
# Those should be kept with the individual bones if we decide it is needed.
#
# Revision 1.8  2011/11/19 06:28:18  cdunde
# Added frame flags importing and Specifics page setting support.
#
# Revision 1.7  2011/11/08 01:41:20  cdunde
# Removed some unused code.
#
# Revision 1.6  2011/10/25 19:47:05  cdunde
# Some file cleanup.
#
# Revision 1.5  2011/05/25 20:55:03  cdunde
# Revamped Bounding Box system for more flexibility with model formats that do not have bones, only single or multi components.
#
# Revision 1.4  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.3  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.2  2011/01/17 06:33:51  cdunde
# Removed unneeded and unused code.
#
# Revision 1.1  2010/12/18 07:21:45  cdunde
# Update and file name change, previously ie_md0_HL_import.py, for proper listing of future Half-Life2 importer.
#
# Revision 1.17  2010/12/07 06:06:52  cdunde
# Updates for Model Editor bounding box system.
#
# Revision 1.16  2010/12/06 18:29:47  cdunde
# Found a better way for the last bounding box change.
#
# Revision 1.15  2010/12/06 09:44:00  cdunde
# Needed to add model name to stuff on importing to keep isolated
# and fixed incorrect usage of ModelComponentList bonelist.
#
# Revision 1.14  2010/12/06 05:43:06  cdunde
# Updates for Model Editor bounding box system.
#
# Revision 1.13  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.12  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.11  2010/10/20 20:17:54  cdunde
# Added bounding boxes (hit boxes) and bone controls support used by Half-Life, maybe others.
#
# Revision 1.10  2010/10/08 06:02:44  cdunde
# To kill dump console printing.
#
# Revision 1.9  2010/10/08 05:33:35  cdunde
# Added support for player models attachment tags.
#
# Revision 1.8  2010/09/26 23:14:31  cdunde
# Added progress bar and did some file cleanup.
#
# Revision 1.7  2010/07/31 22:44:31  cdunde
# Removed dupe and unused code.
#
# Revision 1.6  2010/07/30 20:30:56  cdunde
# Major animation improvement, new base work copy for further development.
#
# Revision 1.5  2010/06/13 16:22:13  cdunde
# Correction update.
#
# Revision 1.4  2010/06/13 15:37:55  cdunde
# Setup Model Editor to allow importing of model from main explorer File menu.
#
# Revision 1.3  2010/05/01 07:16:40  cdunde
# Update by DanielPharos to allow removal of weight_index storage in the ModelComponentList related files.
#
# Revision 1.2  2010/05/01 04:25:37  cdunde
# Updated files to help increase editor speed by including necessary ModelComponentList items
# and removing redundant checks and calls to the list.
#
# Revision 1.1  2010/05/01 03:54:32  cdunde
# Started support for HalfLife 1 .mdl model importing.
#
#
