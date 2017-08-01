# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Half-Life 2 .mdl model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md0_HL2_import.py,v 1.20 2012/11/11 03:54:40 cdunde Exp $


Info = {
   "plug-in":       "ie_md0_HL2_import",
   "desc":          "This script imports a Half-Life 2 file (MDL), textures, and animations into QuArK for editing.",
   "date":          "Dec. 17 2010",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import struct, os, math
import quarkx
from quarkpy.qutils import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings
from quarkpy.qeditor import MapColor # Strictly needed for QuArK bones MapColor call.

# Globals
SS_MODEL = 3
logging = 0
importername = "ie_md0_HL2_import.py"
textlog = "HL2mdl_ie_log.txt"
progressbar = None
starttime = None
editor = None
SpecsList = """ """
framename = None

######################################################
# MDL Flag Settings from -> studio.h
######################################################
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
STUDIO_LXR   =   512
STUDIO_LYR   =  1024
STUDIO_LZR   =  2048
STUDIO_LINEAR=  4096


STUDIO_TYPES = 262143
STUDIO_RLOOP = 262144 # controller that wraps shortest distance


# Flag values from mstudioanim_t
STUDIO_ANIM_RAWPOS  = 0x01 # Vector48
STUDIO_ANIM_RAWROT  = 0x02 # Quaternion48
STUDIO_ANIM_ANIMPOS = 0x04 # mstudioanim_valueptr_t
STUDIO_ANIM_ANIMROT = 0x08 # mstudioanim_valueptr_t
STUDIO_ANIM_DELTA   = 0x10 #Delta movement
STUDIO_ANIM_RAWROT2 = 0x20 # Quaternion64

# Flag values for bone flags
BONE_CALCULATE_MASK        = 0x1F
BONE_PHYSICALLY_SIMULATED  = 0x01 # bone is physically simulated when physics are active
BONE_PHYSICS_PROCEDURAL    = 0x02 # procedural when physics is active
BONE_ALWAYS_PROCEDURAL     = 0x04 # bone is always procedurally animated
BONE_SCREEN_ALIGN_SPHERE   = 0x08 # bone aligns to the screen, not constrained in motion.
BONE_SCREEN_ALIGN_CYLINDER = 0x10 # bone aligns to the screen, constrained by it's own axis.

BONE_USED_MASK           = 0x0007FF00
BONE_USED_BY_ANYTHING    = 0x0007FF00
BONE_USED_BY_HITBOX      = 0x00000100 # bone (or child) is used by a hit box
BONE_USED_BY_ATTACHMENT  = 0x00000200 # bone (or child) is used by an attachment point
BONE_USED_BY_VERTEX_MASK = 0x0003FC00
BONE_USED_BY_VERTEX_LOD0 = 0x00000400 # bone (or child) is used by the toplevel model via skinned vertex
BONE_USED_BY_VERTEX_LOD1 = 0x00000800
BONE_USED_BY_VERTEX_LOD2 = 0x00001000
BONE_USED_BY_VERTEX_LOD3 = 0x00002000
BONE_USED_BY_VERTEX_LOD4 = 0x00004000
BONE_USED_BY_VERTEX_LOD5 = 0x00008000
BONE_USED_BY_VERTEX_LOD6 = 0x00010000
BONE_USED_BY_VERTEX_LOD7 = 0x00020000
BONE_USED_BY_BONE_MERGE  = 0x00040000 # bone is available for bone merge to occur against it

BONE_TYPE_MASK         = 0x00F00000
BONE_FIXED_ALIGNMENT   = 0x00100000 # bone can't spin 360 degrees, all interpolation is normalized around a fixed orientation
BONE_HAS_SAVEFRAME_POS = 0x00200000 # Vector48
BONE_HAS_SAVEFRAME_ROT = 0x00400000 # Quaternion64

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


# Creates a bbox (hit box) if any.
def MakePoly(bname, bpos, brot, bbox, bboxname):
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

# Matrix for QuArK.
### Taken from source\prog\qmatrices.pas lines 139-141
def vector_by_matrix(p, m):
    x = p[0] * m[0][0] + p[1] * m[0][1] + p[2] * m[0][2]
    y = p[0] * m[1][0] + p[1] * m[1][1] + p[2] * m[1][2]
    z = p[0] * m[2][0] + p[1] * m[2][1] + p[2] * m[2][2]
    return [x, y, z]

# Global file limits and values.
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

# Tries to find and load skin material and texture files.
def LookForSkins(skin_names, skins_group, materials_group, folder_name, mdl_name, message):
    cur_dir = os.getcwd()

    def LookForTexture(cur_dir, material, texture, dir=None):
        mat_name = material.lower()
        tex_name = mat_name.replace('.vmt', '.vtf')
        if dir is not None:
            material = dir + '/' + material
        else:
            material = cur_dir + '/' + material
        i = open(material)
        while 1:
            s = i.readline()
            if s == '':
                break
            if s.find('$basetexture') != -1:
                s = s.replace(chr(9), ' ') # Change a tab to a single space.
                s = s.replace('"', '') # Remove all double quotes.
                s = s.replace("'", '') # Remove all single quotes.
                s = s.replace(',', ' ')
                s = ' '.join(s.split())
                s = s.split(' ')
                for word in s:
                    word.replace('\\', '/')
                    if word.find('/') != -1:
                        word = word.rsplit('/', 1)[0]
                        if dir is None:
                            dir = cur_dir.replace('\\', '/')
                            dir = dir.split('/models')[0]
                            dir = dir + '/materials/' + word
                        else:
                            dir = dir.split('/models')[0]
                            dir = dir + '/' + word

                        dir_files = os.listdir(dir)
                        for df in range(len(dir_files)):
                            df_name = dir_files[df].lower()
                            if df_name == tex_name:
                                texture = dir + '/' + dir_files[df]
                                break
                        if texture is not None:
                            break
            if texture is not None:
                break
        i.close()
        return texture, material

    for skin_name in range(len(skin_names)):
        material = texture = None
        mat_flags = tex_flags = "0"
        files = os.listdir(cur_dir) # Always check in the model's directory first.
        for item in range(len(files)):
            item_name = files[item].lower() # Make sure all text is lower case.
            if item_name == skin_names[skin_name][0] + ".vmt" and material is None:
                material = files[item]
                mat_flags = skin_names[skin_name][1]
            if item_name == skin_names[skin_name][0] + ".vtf" and texture is None:
                texture = files[item]
                tex_flags = skin_names[skin_name][1]
            if material is not None and texture is not None:
                material = cur_dir + '/' + material
                texture = cur_dir + '/' + texture
                break

        if material is None or texture is None: # Try to find "materials" folder and missing file(s) there.
            if material is not None:
                texture, material = LookForTexture(cur_dir, material, texture)
            else:
                dir = cur_dir.replace('\\', '/')
                try:
                    try:
                        trydir = dir.split('/models')[0]
                        trydir = trydir + '/materials/models/' + mdl_name
                        dir_files = os.listdir(trydir)
                    except:
                        try:
                            trydir = dir.replace('/models/', '/materials/models/')
                            trydir = trydir + '/' + mdl_name
                            dir_files = os.listdir(trydir)
                        except:
                            trydir = dir.replace('/models/', '/materials/models/')
                            dir_files = os.listdir(trydir)

                    dir = trydir
                    for df in range(len(dir_files)):
                        df_name = dir_files[df].lower()
                        if df_name.find(skin_names[skin_name][0]) != -1:
                            if df_name.endswith(".vmt") and material is None:
                                material = dir_files[df]
                            if df_name.endswith(".vtf") and texture is None:
                                texture = dir_files[df]
                        if material is not None and texture is not None:
                            material = dir + '/' + material
                            texture = dir + '/' + texture
                            break
                    if material is not None and texture is None:
                        texture, material = LookForTexture(cur_dir, material, texture, dir)
                except:
                    pass

        # If nothing, try another way.
        if material is None and texture is None:
            try:
                dir = cur_dir.replace('\\', '/')
                trydir = dir.replace('/models/', '/materials/models/')
                try_name = mdl_name.rsplit('_', 1)[0]
                trydir2 = trydir.rsplit('/', 1)[0] + '/' + try_name
                dir = trydir2
                dir_files = os.listdir(trydir2)
                for df in range(len(dir_files)):
                    df_name = dir_files[df].lower()
                    if df_name.find(skin_names[skin_name][0]) != -1:
                        if df_name.endswith(".vmt") and material is None:
                            material = dir_files[df]
                        if df_name.endswith(".vtf") and texture is None:
                            texture = dir_files[df]
                    if material is not None and texture is not None:
                        material = dir + '/' + material
                        texture = dir + '/' + texture
                        break

                if material is not None and texture is None:
                    texture, material = LookForTexture(cur_dir, material, texture, dir)

                if material is None and texture is None:
                    dir = dir + '/' + folder_name
                    dir_files = os.listdir(dir)
                    for df in range(len(dir_files)):
                        df_name = dir_files[df].lower()
                        if df_name.find(skin_names[skin_name][0]) != -1:
                            if df_name.endswith(".vmt") and material is None:
                                material = dir_files[df]
                            if df_name.endswith(".vtf") and texture is None:
                                texture = dir_files[df]
                        if material is not None and texture is not None:
                            material = dir + '/' + material
                            texture = dir + '/' + texture
                            break
                    if material is not None and texture is None:
                        texture, material = LookForTexture(cur_dir, material, texture, dir)
            except:
                pass

        if texture is None:
            skins_group.append(["None", tex_flags])
        else:
            skins_group.append([texture, tex_flags])
        if material is None:
            materials_group.append(["None", mat_flags])
        else:
            materials_group.append([material, mat_flags])

    return skins_group, materials_group

# Opens and reads in the given material file.
def ReadMaterialFile(material_path):
    file = open(material_path, "r")
    lines = file.readlines()
    file.close()
    left_cur_braket = 0
    mesh_shader = ""
    for line in range(len(lines)):
        shaderline = lines[line].replace(chr(9), "    ")
        shaderline = shaderline.rstrip()
        if left_cur_braket == 0 and shaderline.startswith('"') and shaderline.endswith('"'):
            shader_keyword = shaderline.replace('"', "")
        if lines[line].find("{") != -1:
            left_cur_braket = left_cur_braket + 1
        if lines[line].find("}") != -1:
            left_cur_braket = left_cur_braket - 1
        mesh_shader = mesh_shader + shaderline + "\r\n"

    shader_file = material_path
    shader_name = material_path.rsplit("/", 1)[1]
    mesh_shader = mesh_shader

    return shader_keyword, shader_file, shader_name, mesh_shader


######################################################
# MDL data structures
######################################################
class mdl_bone:
    #Header Structure      #item of file, type, description.
    bone_index = 0         # For our own use later.
    sznameindex = 0        #item   0      int, the bone's name index.
    pszName = ""
    parent = 0             #item   1      int, bone's parent index.
    bonecontroller = (0)*6 #item   2-7    int, bone controller index, -1 == none.
    pos = (0.0)*3          #item   8-10   3 floats, position values.
    quat = (0.0)*4         #item   11-14  4 floats, Quaternion values: x(ix), y(iy), z(iz), w(iw).
    rot = (0.0)*3          #item   15-17  3 floats, RadianEuler values.
    posscale = (0.0)*3     #item   18-20  3 floats, position compression scale.
    rotscale = (0.0)*3     #item   21-23  3 floats, rotation compression scale.
    poseToBone = (0.0)*12  #item   24-35  12 floats, bone 3x4 matrix.
    qAlignment = (0.0)*4   #item   36-39  4 floats, bone Quaternion (qx, qy, qz, qw).
    flags = 0              #item   40     int, bone flag setting.
    proctype = 0           #item   41     int.
    procindex = 0          #item   42     int, bone procedural rule.
    # inline void *pProcedure( ) const { if (procindex == 0) return NULL; else return  (void *)(((byte *)this) + procindex); };
    physicsbone = 0        #item   43     int, index into physically simulated bone.
    surfacepropidx = 0     #item   44     int, index into string table for property name.
    # inline char * const pszSurfaceProp( void ) const { return ((char *)this) + surfacepropidx; }
    contents = 0           #item   45     int, See HL2SDK bspflags.h for the contents flags.
    unused1 = 0            #item   46     int.
    unused2 = 0            #item   47     int.
    unused3 = 0            #item   48     int.
    unused4 = 0            #item   49     int.
    unused5 = 0            #item   50     int.
    unused6 = 0            #item   51     int.
    unused7 = 0            #item   52     int.
    unused8 = 0            #item   53     int.
    binary_format="<ii6i3f4f3f3f3f12f4f6i8i"  #little-endian (<), see #item descriptions above.
    data_read_in = 216 # Total binary_format byte value above, used below to set the file offset pointer back.

    value = (0.0)*6    # For QuArK's own use.
    scale = (0.0)*6    # For QuArK's own use.

    def __init__(self):
        self.bone_index = 0
        self.sznameindex = 0
        self.pszName = ""
        self.parent = 0
        self.bonecontroller = (0)*6
        self.pos = (0.0)*3
        self.quat = (0.0)*4
        self.rot = (0.0)*3
        self.posscale = (0.0)*3
        self.rotscale = (0.0)*3
        self.poseToBone = (0.0)*12
        self.qAlignment = (0.0)*4
        self.flags = 0
        self.proctype = 0
        self.procindex = 0
        self.physicsbone = 0
        self.surfacepropidx = 0
        self.contents = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.data_read_in = 216 # Total binary_format byte value above, used below to set the file offset pointer back.

        self.value = (0.0)*6    # For QuArK's own use.
        self.scale = (0.0)*6    # For QuArK's own use.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.sznameindex = data[0]
        self.pszName = ""
        self.parent = data[1]
        self.bonecontroller = (data[2], data[3], data[4], data[5], data[6], data[7])
        self.pos = (data[8], data[9], data[10])
        self.quat = (data[11], data[12], data[13], data[14])
        self.rot = (data[15], data[16], data[17])
        self.posscale = (data[18], data[19], data[20])
        self.rotscale = (data[21], data[22], data[23])
        self.poseToBone = ((data[24], data[25], data[26], data[27]), (data[28], data[29], data[30], data[31]), (data[32], data[33], data[34], data[35]))
        self.qAlignment = (data[36], data[37], data[38], data[39])
        self.flags = data[40]
        self.proctype = data[41]
        self.procindex = data[42]
        self.physicsbone = data[43]
        self.surfacepropidx = data[44]
        self.contents = data[45]
        self.unused1 = data[46]
        self.unused2 = data[47]
        self.unused3 = data[48]
        self.unused4 = data[49]
        self.unused5 = data[50]
        self.unused6 = data[51]
        self.unused7 = data[52]
        self.unused8 = data[53]

        self.value = (data[8], data[9], data[10], data[15], data[16], data[17])    # For QuArK's own use.
        self.scale = (data[18], data[19], data[20], data[21], data[22], data[23])  # For QuArK's own use.

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            Namedata = struct.unpack(binary_format, temp_data)
            if Namedata[0] == '\x00':
                break
            self.pszName = self.pszName + Namedata[0]
        if logging == 1:
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("pos: " + str(self.pos))
            tobj.logcon ("rot: " + str(self.rot))
            tobj.logcon ("-------------------------")

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


class mdl_bone_control:
    #Header Structure      #item of file, type, description.
    bone = 0               #item   0      int, -1 = 0.
                           #                   types = X, Y, Z, XR, YR, ZR or M.
    type = 0               #item   1      int, types = 1, 2, 4,  8, 16, 32 or 64
    start = 0.0            #item   2      float.
    end = 0.0              #item   3      float.
    rest = 0               #item   4      int, byte index value at rest.
    inputfield = 0         #item   5      int, 0-3 user set controller, 4 mouth (called index for HL1).
    unused1 = 0            #item   6      int.
    unused2 = 0            #item   7      int.
    unused3 = 0            #item   8      int.
    unused4 = 0            #item   9      int.
    unused5 = 0            #item   10     int.
    unused6 = 0            #item   11     int.
    unused7 = 0            #item   12     int.
    unused8 = 0            #item   13     int.

    binary_format="<2i2f10i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone = 0
        self.type = 0
        self.start = 0.0
        self.end = 0.0
        self.rest = 0
        self.inputfield = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        if logging == 1:
            tobj.logcon ("=========================")
            tobj.logcon ("mdl_bone_control data")
            tobj.logcon ("bone: " + str(self.bone))
            tobj.logcon ("type: " + str(self.type))
            tobj.logcon ("start: " + str(self.start))
            tobj.logcon ("end: " + str(self.end))
            tobj.logcon ("rest: " + str(self.rest))
            tobj.logcon ("inputfield: " + str(self.inputfield))
        self.bone = data[0]
        self.type = data[1]
        self.start = data[2]
        self.end = data[3]
        self.rest = data[4]
        self.inputfield = data[5]
        self.unused1 = data[6]
        self.unused2 = data[7]
        self.unused3 = data[8]
        self.unused4 = data[9]
        self.unused5 = data[10]
        self.unused6 = data[11]
        self.unused7 = data[12]
        self.unused8 = data[13]


class mdl_hitbox:
    #Header Structure      #item of file, type, description.
    bone = 0               #item   0      int, the bone's index.
    group = 0              #item   1      int, intersection group.
    bbmin = (0.0)*3        #item   2-4    3 floats, bounding box min x,y,z Vector.
    bbmax = (0.0)*3        #item   5-7    3 floats, bounding box max x,y,z Vector.
    szhitboxnameindex = 0  #item   8      int, offset to the name of the hitbox.
    unused1 = 0            #item   9      int.
    unused2 = 0            #item   10     int.
    unused3 = 0            #item   11     int.
    unused4 = 0            #item   12     int.
    unused5 = 0            #item   13     int.
    unused6 = 0            #item   14     int.
    unused7 = 0            #item   15     int.
    unused8 = 0            #item   16     int.
    HitBoxName = ""        # returned string of the bbox name, if any.
    poly = None            # QuArK's use only.

    binary_format="<2i3f3fi8i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone = 0
        self.group = 0
        self.bbmin = (0.0)*3
        self.bbmax = (0.0)*3
        self.szhitboxnameindex = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.HitBoxName = ""
        self.poly = None

    def load(self, file, bboxgroup, count, QuArK_bones, bboxlist):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.bone = data[0]
        self.group = data[1]
        self.bbmin = (data[2], data[3], data[4])
        self.bbmax = (data[5], data[6], data[7])
        self.szhitboxnameindex = data[8]
        self.unused1 = data[9]
        self.unused2 = data[10]
        self.unused3 = data[11]
        self.unused4 = data[12]
        self.unused5 = data[13]
        self.unused6 = data[14]
        self.unused7 = data[15]
        self.unused8 = data[16]
        if self.szhitboxnameindex != 0:
            CurOffset = file.tell() # Save the file current offset pointer.
            file.seek(self.szhitboxnameindex, 0) # change the file offset pointer position.
            binary_format="<c"
            start = 0
            while 1:
                temp_data = file.read(struct.calcsize(binary_format))
                data = struct.unpack(binary_format, temp_data)
                if data[0] == '\x00' or start < 2:
                    if data[0] == '\x00' and start < 2:
                        start = start + 1
                        continue
                    elif start < 2:
                        continue
                    else:
                        if data[0] == '\x00':
                            break
                self.HitBoxName = self.HitBoxName + data[0]
            self.HitBoxName = self.HitBoxName + str(count)
            m = self.bbmin
            M = self.bbmax
            bone = QuArK_bones[self.bone]
            bname = bone.name
            bpos = bone.position
            brot = bone.rotmatrix
            bbox = [self.bbmin, self.bbmax]
            self.poly = MakePoly(bname, bpos, brot, bbox, self.HitBoxName)
            count = 0
            for name in bboxlist.keys():
                if name.startswith(self.poly.shortname):
                    count += 1
            if count != 0:
                self.poly.shortname = self.poly.shortname + str(count)
            bboxlist[self.poly.name] = {}
            bboxlist[self.poly.name]['size'] = bbox
            bboxgroup.appenditem(self.poly)
            file.seek(CurOffset, 0) # Reset the file offset pointer back to where it should be now.

        if logging == 1:
            tobj.logcon ("--------------mdl_hitbox----------------")
            tobj.logcon ("HitBoxName: " + self.HitBoxName)
            tobj.logcon ("bone: " + str(self.bone))
            tobj.logcon ("group: " + str(self.group))
            tobj.logcon ("bbmin: " + str(self.bbmin))
            tobj.logcon ("bbmax: "  + str(self.bbmax))
            tobj.logcon ("szhitboxnameindex: " + str(self.szhitboxnameindex))


class mdl_attachment:
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int, the attachment's name index.
    pszName = ""
    flags = 0              #item   1      int, attachment's flags setting.
    localbone = 0          #item   2      int, offset to the name of the hitbox.
    local = (0.0)*12       #item   3-14   12 floats, 3x4 matrix attachment point.
    unused1 = 0            #item   15     int.
    unused2 = 0            #item   16     int.
    unused3 = 0            #item   17     int.
    unused4 = 0            #item   18     int.
    unused5 = 0            #item   19     int.
    unused6 = 0            #item   20     int.
    unused7 = 0            #item   21     int.
    unused8 = 0            #item   22     int.
    binary_format="<3i12f8i"  #little-endian (<), see #item descriptions above.
    data_read_in = 92 # Total binary_format byte value above, used below to set the file offset pointer back.

    def __init__(self):
        self.sznameindex = 0
        self.pszName = ""
        self.flags = 0
        self.localbone = 0
        self.local = (0.0)*12
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.data_read_in = 92 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.sznameindex = data[0]
        self.pszName = ""
        self.flags = data[1]
        self.localbone = data[2]
        self.local = ((data[3],  data[4], data[5], data[6]), (data[7],  data[8], data[9], data[10]), (data[11],  data[12], data[13], data[14]))
        self.unused1 = data[15]
        self.unused2 = data[16]
        self.unused3 = data[17]
        self.unused4 = data[18]
        self.unused5 = data[19]
        self.unused6 = data[20]
        self.unused7 = data[21]
        self.unused8 = data[22]

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        if logging == 1:
            tobj.logcon ("--------------mdl_attachment----------------")
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("localbone: " + str(self.localbone))
            tobj.logcon ("local: " + str(self.local))


class mdl_bodypart:
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int.
    pszName = ""
    nummodels = 0          #item   1      int.
    base = 0               #item   2      int.
    modelindex = 0         #item   3      int, index into models array.
    models = []                           # A list containing its models.
                                
    def __init__(self):
        self.sznameindex = 0
        self.pszName = ""
        self.nummodels = 0
        self.base = 0
        self.modelindex = 0
        self.models = []

    def load(self, file):
        binary_format="<4i" # data_read_in = 4i = 4*4 = 16
        data_read_in = 16   # Total binary_format byte value above, used below to set the file offset pointer back.
        temp_data = file.read(struct.calcsize(binary_format))
        data = struct.unpack(binary_format, temp_data)
        self.sznameindex = data[0]
        self.nummodels = data[1]
        self.base = data[2]
        self.modelindex = data[3]

        SaveCurOffset = file.tell() # Save the file current offset pointer.

        file.seek(SaveCurOffset - data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]

        if logging == 1:
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("nummodels: " + str(self.nummodels))
            tobj.logcon ("base: " + str(self.base))
            tobj.logcon ("modelindex: " + str(self.modelindex))

        file.seek(SaveCurOffset - data_read_in + self.modelindex, 0) # change the file offset pointer position to get the model.
        for m in xrange(self.nummodels):
            model = mdl_model()
            model.load(file)
            self.models.append(model)

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


class mdl_model:
    #Header Structure      #item of file, type, description.
    pszName = ""           #item   0      64 s.
    type = 0               #item   1      int.
    boundingradius = 0.0   #item   2      float.
    nummeshes = 0          #item   3      int.
    meshindex = 0          #item   4      int.
    numvertices = 0        #item   5      int, number of unique vertices/normals/texcoords.
    vertexindex = 0        #item   6      int, vertex Vector.
    tangentsindex = 0      #item   7      int, tangents Vector.
    numattachments = 0     #item   8      int.
    attachmentindex = 0    #item   9      int.
    numeyeballs = 0        #item   10     int.
    eyeballindex = 0       #item   11     int.
    vertexdata = (0.0)*2   #item   12-13  2 floats.
    unused1 = 0            #item   14     int.
    unused2 = 0            #item   15     int.
    unused3 = 0            #item   16     int.
    unused4 = 0            #item   17     int.
    unused5 = 0            #item   18     int.
    unused6 = 0            #item   19     int.
    unused7 = 0            #item   20     int.
    unused8 = 0            #item   21     int.

    binary_format = "<%dsif9i2f8i" % MAX_QPATH  #little-endian (<), see #item descriptions above.

    meshes = []            # List of meshes.
    verts = []             # List of vertex vector poistions.
    eyeballs = []          # List of meshe eyeballs.

    def __init__(self):
        self.pszName = ""
        self.type = 0
        self.boundingradius = 0.0
        self.nummeshes = 0
        self.meshindex = 0
        self.numvertices = 0
        self.vertexindex = 0
        self.tangentsindex = 0
        self.numattachments = 0
        self.attachmentindex = 0
        self.numeyeballs = 0
        self.eyeballindex = 0
        self.vertexdata = (0.0)*2
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.binary_format = "<%dsif9i2f8i" % MAX_QPATH  #little-endian (<), see #item descriptions above.

        self.meshes = []
        self.verts = []
        self.eyeballs = []

    def load(self, file):
        data_read_in = 148   # Total binary_format byte value above, used below to set the file offset pointer back.
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.pszName = asciiz(data[0])
        self.type = data[1]
        self.boundingradius = data[2]
        self.nummeshes = data[3]
        self.meshindex = data[4]
        self.numvertices = data[5]
        self.vertexindex = data[6]
        self.tangentsindex = data[7]
        self.numattachments = data[8]
        self.attachmentindex = data[9]
        self.numeyeballs = data[10]
        self.eyeballindex = data[11]
        self.vertexdata = (data[12], data[13])
        self.unused1 = data[14]
        self.unused2 = data[15]
        self.unused3 = data[16]
        self.unused4 = data[17]
        self.unused5 = data[18]
        self.unused6 = data[19]
        self.unused7 = data[20]
        self.unused8 = data[21]
        SaveCurOffset = file.tell() # Save the file current offset pointer.
        if logging == 1:
            tobj.logcon ("======================================")
            tobj.logcon ("HL2_Model data")
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("type: " + str(self.type))
            tobj.logcon ("boundingradius: " + str(self.boundingradius))
            tobj.logcon ("nummeshes: " + str(self.nummeshes))
            tobj.logcon ("meshindex: " + str(self.meshindex))
            tobj.logcon ("numvertices: " + str(self.numvertices))
            tobj.logcon ("vertexindex: " + str(self.vertexindex))
            tobj.logcon ("tangentsindex: " + str(self.tangentsindex))
            tobj.logcon ("numattachments: " + str(self.numattachments))
            tobj.logcon ("attachmentindex: " + str(self.attachmentindex))
            tobj.logcon ("numeyeballs: " + str(self.numeyeballs))
            tobj.logcon ("eyeballindex: " + str(self.eyeballindex))
            tobj.logcon ("vertexdata: " + str(self.vertexdata))

        file.seek(SaveCurOffset - data_read_in + self.meshindex, 0) # change the file offset pointer position to get the model.
        for m in xrange(self.nummeshes):
            mesh = mdl_mesh()
            mesh.load(file)
            self.meshes.append(mesh)

        file.seek(SaveCurOffset - data_read_in + self.eyeballindex, 0) # change the file offset pointer position to get the model.
        for m in xrange(self.numeyeballs):
            eyeball = HL2_EyeBall()
            eyeball.load(file)
            self.eyeballs.append(eyeball)

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


class mdl_mesh:
    #Header Structure      #item of file, type, description.
    material = 0           #item   0      int.
    modelindex = 0         #item   1      int.
    numvertices = 0        #item   2      int, number of unique vertices/normals/texcoords.
    vertexoffset = 0       #item   3      int, vertex mstudiovertex_t.
    numflexes = 0          #item   4      int, vertex animation.
    flexindex = 0          #item   5      int.
    materialtype = 0       #item   6      int, special codes for material operations.
    materialparam = 0      #item   7      int, special codes for material operations.
    meshid = 0             #item   8      int, a unique ordinal for this mesh.
    center = (0.0)*3       #item   9-11   3 floats.
    vertexdata = (0.0)*9   #item   12-20  9 floats, DAN WHAT IS THIS????
    unused1 = 0            #item   21     int.
    unused2 = 0            #item   22     int.
    unused3 = 0            #item   23     int.
    unused4 = 0            #item   24     int.
    unused5 = 0            #item   25     int.
    unused6 = 0            #item   26     int.
    unused7 = 0            #item   27     int.
    unused8 = 0            #item   28     int.
    binary_format = "<9i3f9f8i"  #little-endian (<), see #item descriptions above.

    vertex_weights = []    # list of each vertex's weight values, weight bones, nbr of w-bones, pos, normal, UV values.

    def __init__(self):
        self.material = 0
        self.modelindex = 0
        self.numvertices = 0
        self.vertexoffset = 0
        self.numflexes = 0
        self.flexindex = 0
        self.materialtype = 0
        self.materialparam = 0
        self.meshid = 0
        self.center = (0.0)*3
        self.vertexdata = (0.0)*9
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0

        self.vertex_weights = []

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.material = data[0]
        self.modelindex = data[1]
        self.numvertices = data[2]
        self.vertexoffset = data[3]
        self.numflexes = data[4]
        self.flexindex = data[5]
        # inline mstudioflex_t *pFlex( int i ) const { return (mstudioflex_t *)(((byte *)this) + flexindex) + i; };
        self.materialtype = data[6]
        self.materialparam = data[7]
        self.meshid = data[8]
        self.center = (data[9], data[10], data[11])
        # DAN WHAT IS THIS????
        self.vertexdata = (data[12], data[13], data[14], data[15], data[16], data[17], data[18], data[19], data[20])
        self.unused1 = data[21]
        self.unused2 = data[22]
        self.unused3 = data[23]
        self.unused4 = data[24]
        self.unused5 = data[25]
        self.unused6 = data[26]
        self.unused7 = data[27]
        self.unused8 = data[28]
        if logging == 1:
            tobj.logcon ("======================================")
            tobj.logcon ("mdl_mesh data")
            tobj.logcon ("meshid: " + str(self.meshid))
            tobj.logcon ("modelindex: " + str(self.modelindex))
            tobj.logcon ("numvertices: " + str(self.numvertices))
            tobj.logcon ("vertexoffset: " + str(self.vertexoffset))


class mdl_sequence_desc:
    #Header Structure        #item of file, type, description.
    baseptr = 0              #item   0      int.
    sznameindex = 0          #item   1      int.
    pszName = ""
    fps = 0.0                #item   2      float, frames per second. ##### HL1 fps in mdl_sequence_desc #####
    flags = 0                #item   3      int, non-looping/looping flags...0/1 ##### HL1 flags in mdl_sequence_desc #####
    numframes = 0            #item   4      int.    ##### HL1 numframes in mdl_sequence_desc #####
    nummovements = 0         #item   5      int, piecewise movement. ##### HL1 numpivots in mdl_sequence_desc I think. #####
    movementindex = 0        #item   6      int, piecewise movement. ##### HL1 pivot_offset in mdl_sequence_desc I think. #####
    bboxmin = (0.0)*3        #item   7-9    3 floats, per animation bounding box min.
    bboxmax = (0.0)*3        #item   10-12  3 floats, per animation bounding box max.
    animblock = 0            #item   13     int.    ##### HL1 seqgroup in mdl_sequence_desc I think. #####
    animindex = 0            #item   14     int, non-zero when anim data isn't in sections.
    numikrules = 0           #item   15     int.
    ikruleindex = 0          #item   16     int, non-zero when IK data is stored in the mdl.
    animblockikruleindex = 0 #item   17     int, non-zero when IK data is stored in animblock file.
    unused1 = 0              #item   18     int.
    unused2 = 0              #item   19     int.
    unused3 = 0              #item   20     int.
    unused4 = 0              #item   21     int.
    unused5 = 0              #item   22     int.
    unused6 = 0              #item   23     int.
    unused7 = 0              #item   24     int.
    binary_format="<2if4i3f3f12i"  #little-endian (<), see #item descriptions above.
    data_read_in = 100 # Total binary_format byte value above, used below to set the file offset pointer back.
    ThisOffset = 0 # Need the offset of the structure to get to the anim block later

    def __init__(self):
        self.baseptr = 0
        self.sznameindex = 0
        self.pszName = ""
        self.fps = 0.0
        self.flags = 0
        self.numframes = 0
        self.nummovements = 0
        self.movementindex = 0
        self.bboxmin = (0.0)*3
        self.bboxmax = (0.0)*3
        self.animblock = 0
        self.animindex = 0
        self.numikrules = 0
        self.ikruleindex = 0
        self.animblockikruleindex = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.binary_format="<2if4i3f3f12i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 100 # Total binary_format byte value above, used below to set the file offset pointer back.
        self.ThisOffset = 0

    def load(self, file, ani_file, hl2_file_obj):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.baseptr = data[0]
        # inline studiohdr_t    *pStudiohdr( void ) const { return (studiohdr_t *)(((byte *)this) + baseptr); }
        self.sznameindex = data[1]
        self.pszName = ""
        self.fps = data[2]
        self.flags = data[3]
        self.numframes = data[4]
        self.nummovements = data[5]
        self.movementindex = data[6]
        self.bboxmin = (data[7], data[8], data[9])
        self.bboxmax = (data[10], data[11], data[12])
        self.animblock = data[13]
        self.animindex = data[14]
        self.numikrules = data[15]
        self.ikruleindex = data[16]
        self.animblockikruleindex = data[17]
        self.unused1 = data[18]
        self.unused2 = data[19]
        self.unused3 = data[20]
        self.unused4 = data[21]
        self.unused5 = data[22]
        self.unused6 = data[23]
        self.unused7 = data[24]

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        self.ThisOffset = SaveCurOffset - self.data_read_in
        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            Namedata = struct.unpack(binary_format, temp_data)
            if Namedata[0] == '\x00':
                break
            self.pszName = self.pszName + Namedata[0]
        if logging == 1:
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("fps: " + str(self.fps))
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("numframes: " + str(self.numframes))
            tobj.logcon ("nummovements: " + str(self.nummovements))
            tobj.logcon ("movementindex: " + str(self.movementindex))
            tobj.logcon ("bboxmin: " + str(self.bboxmin))
            tobj.logcon ("bboxmax: " + str(self.bboxmax))
            tobj.logcon ("animblock: " + str(self.animblock))
            tobj.logcon ("animindex: " + str(self.animindex))
            tobj.logcon ("numikrules: " + str(self.numikrules))
            tobj.logcon ("ikruleindex: " + str(self.ikruleindex))
            tobj.logcon ("animblockikruleindex: " + str(self.animblockikruleindex))

        # inline mstudiomovement_t * const pMovement( int i ) const { return (mstudiomovement_t *)(((byte *)this) + movementindex) + i; };
        file.seek(SaveCurOffset - self.data_read_in + self.movementindex, 0) # change the file offset pointer position.
        for i in xrange(self.nummovements, 0):
            std_movement = HL2_StudioMovement()
            std_movement.load(file)
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


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


class HL2_TexturesInfo:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiotexture_t
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int, file offset to this TexturesInfo data.
    pszName = ""           #item (none)   max. 64 char, skin name.
    flags = 0              #item   1      int, skin flags setting for special texture handling ex: None=0 (default), Chrome=2 (cstrike), Chrome=3 (valve), Additive=32, Chrome & Additive=34, Transparent=64.
    used = 0               #item   2      int.
    unknown = 0            #item   3      int.
    material = 0           #item   4      int.
    clientmaterial = 0     #item   5      int.
    unused1 = 0            #item   6      int.
    unused2 = 0            #item   7      int.
    unused3 = 0            #item   8      int.
    unused4 = 0            #item   9      int.
    unused5 = 0            #item   10     int.
    unused6 = 0            #item   11     int.
    unused7 = 0            #item   12     int.
    unused8 = 0            #item   13     int.
    unused9 = 0            #item   14     int.
    unused10 = 0           #item   15     int.
    binary_format="<16i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.sznameindex = 0
        self.pszName = ""
        self.flags = 0
        self.used = 0
        self.unknown = 0
        self.material = 0
        self.clientmaterial = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.unused9 = 0
        self.unused10 = 0
        self.binary_format="<16i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 64 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        if logging == 1:
            tobj.logcon ("======================================")
            tobj.logcon ("HL2_TexturesInfo data")
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("used: " + str(self.used))
            tobj.logcon ("unknown: " + str(self.unknown))
            tobj.logcon ("material: " + str(self.material))
            tobj.logcon ("clientmaterial: " + str(self.clientmaterial))
        self.sznameindex = data[0]
        self.flags = data[1]
        self.used = data[2]
        self.unknown = data[3]
        self.material = data[4]
        self.clientmaterial = data[5]
        self.unused1 = data[6]
        self.unused2 = data[7]
        self.unused3 = data[8]
        self.unused4 = data[9]
        self.unused5 = data[10]
        self.unused6 = data[11]
        self.unused7 = data[12]
        self.unused8 = data[13]
        self.unused9 = data[14]
        self.unused10 = data[15]

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]
        if logging == 1:
            tobj.logcon ("pszName: " + self.pszName)
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.




class HL2_StudioMovement:
    #Header Structure      #item of file, type, description.
    endframe = 0           #item   0      int.
    motionflags = 0        #item   1      int.
    v0 = 0.0               #item   2      float, velocity at start of block.
    v1 = 0.0               #item   3      float, velocity at end of block.
    angle = 0.0            #item   4      float, YAW rotation at end of this blocks movement.
    vector = (0.0)*3       #item   5-7    3 floats, movement vector relative to this blocks initial angle.
    position = (0.0)*3     #item   8-10   3 floats, relative to start of animation???
    binary_format="<2i3f3f3f"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.endframe = 0
        self.motionflags = 0
        self.v0 = 0.0
        self.v1 = 0.0
        self.angle = 0.0
        self.vector = (0.0)*3
        self.position = (0.0)*3
        self.binary_format="<2i3f3f3f"  #little-endian (<), see #item descriptions above.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        if logging == 1:
            tobj.logcon ("========================")
            tobj.logcon ("HL2_StudioMovement data")
            tobj.logcon ("endframe: " + str(self.endframe))
            tobj.logcon ("motionflags: " + str(self.motionflags))
            tobj.logcon ("v0: " + str(self.v0))
            tobj.logcon ("v1: " + str(self.v1))
            tobj.logcon ("angle: " + str(self.angle))
            tobj.logcon ("vector: " + str(self.vector))
            tobj.logcon ("position: " + str(self.position))
        self.endframe = data[0]
        self.motionflags = data[1]
        self.v0 = data[2]
        self.v1 = data[3]
        self.angle = data[4]
        self.vector = (data[5], data[6], data[7])
        self.position = (data[8], data[9], data[10])


class HL2_AnimValuePtr:
    #Header Structure   #item of file, type, description.
    offset = (0)*3     #item   0     3 short, offset.
    binary_format="<3h" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.offset = (0)*3
        self.binary_format="<3h"

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.offset = (data[0], data[1], data[2])


class HL2_LocalSeqDesc:
    #Header Structure        #item of file, type, description.
    baseptr = 0              #item   0      int.
    szlabelindex = 0         #item   1      int.
    pszLabel = ""
    szactivitynameindex = 0  #item   2      int.
    pszActivityName = ""
    flags = 0                #item   3      int, looping/non-looping flags.
    activity = 0             #item   4      int, initialized at loadtime to game DLL values.
    actweight = 0            #item   5      int.
    numevents = 0            #item   6      int.
    eventindex = 0           #item   7      int.
    bboxmin = (0.0)*3        #item   8-10   3 floats, per sequence bounding box min.
    bboxmax = (0.0)*3        #item   11-13  3 floats, per sequence bounding box max.
    numblends = 0            #item   14     int.
    animindexindex = 0       #item   15     int, index into array of shorts which is groupsize[0] x groupsize[1] in length.
    movementindex = 0        #item   16     int, [blend] float array for blended movement.
    groupsize = (0)*2        #item   17-18  2 ints.
    paramindex = (0)*2       #item   19-20  2 ints, X, Y, Z, XR, YR, ZR.
    paramstart = (0.0)*2     #item   21-22  2 floats, local (0..1) starting value.
    paramend = (0.0)*2       #item   23-24  2 floats, local (0..1) ending value.
    paramparent = 0          #item   25     int.
    fadeintime = 0.0         #item   26     float, ideal cross fate in time (0.2 default).
    fadeouttime = 0.0        #item   27     float, ideal cross fade out time (0.2 default).
    localentrynode = 0       #item   28     int, transition node at entry.
    localexitnode = 0        #item   29     int, transition node at exit.
    nodeflags = 0            #item   30     int, transition rules.
    entryphase = 0.0         #item   31     float, used to match entry gait.
    exitphase = 0.0          #item   32     float, used to match exit gait.
    lastframe = 0.0          #item   33     float, frame that should generate EndOfSequence.
    nextseq = 0              #item   34     int, auto advancing sequences.
    pose = 0                 #item   35     int, index of delta animation between end and nextseq.
    numikrules = 0           #item   36     int.
    numautolayers = 0        #item   37     int.
    autolayerindex = 0       #item   38     int.
    weightlistindex = 0      #item   39     int.
    posekeyindex = 0         #item   40     int.
    numiklocks = 0           #item   41     int.
    iklockindex = 0          #item   42     int.
    keyvalueindex = 0        #item   43     int.
    keyvaluesize = 0         #item   44     int.
    unused1 = 0              #item   45     int.
    unused2 = 0              #item   46     int.
    unused3 = 0              #item   47     int.
    unused4 = 0              #item   48     int.
    unused5 = 0              #item   49     int.
    unused6 = 0              #item   50     int.
    unused7 = 0              #item   51     int.
    unused8 = 0              #item   52     int.
    data_read_in = 212 # Total binary_format byte value above, used below to set the file offset pointer back.

    binary_format="<8i3f3f3i2i2i2f2fi2f3i3f19i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.baseptr = 0
        self.szlabelindex = 0
        self.pszLabel = ""
        self.szactivitynameindex = 0
        self.pszActivityName = ""
        self.flags = 0
        self.activity = 0
        self.actweight = 0
        self.numevents = 0
        self.eventindex = 0
        self.bboxmin = (0.0)*3
        self.bboxmax = (0.0)*3
        self.numblends = 0
        self.animindexindex = 0
        self.movementindex = 0
        self.groupsize = (0)*2
        self.paramindex = (0)*2
        self.paramstart = (0.0)*2
        self.paramend = (0.0)*2
        self.paramparent = 0
        self.fadeintime = 0.0
        self.fadeouttime = 0.0
        self.localentrynode = 0
        self.localexitnode = 0
        self.nodeflags = 0
        self.entryphase = 0.0
        self.exitphase = 0.0
        self.lastframe = 0.0
        self.nextseq = 0
        self.pose = 0
        self.numikrules = 0
        self.numautolayers = 0
        self.autolayerindex = 0
        self.weightlistindex = 0
        self.posekeyindex = 0
        self.numiklocks = 0
        self.iklockindex = 0
        self.keyvalueindex = 0
        self.keyvaluesize = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.data_read_in = 212 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.baseptr = data[0]
        # inline studiohdr_t    *pStudiohdr( void ) const { return (studiohdr_t *)(((byte *)this) + baseptr); }
        self.szlabelindex = data[1]
        self.pszLabel = ""
        self.szactivitynameindex = data[2]
        self.pszActivityName = ""
        self.flags = data[3]
        self.activity = data[4]
        self.actweight = data[5]
        self.numevents = data[6]
        self.eventindex = data[7]
        # inline mstudioevent_t *pEvent( int i ) const { assert( i >= 0 && i < numevents); return (mstudioevent_t *)(((byte *)this) + eventindex) + i; };
        self.bboxmin = (data[8], data[9], data[10])
        self.bboxmax = (data[11], data[12], data[13])
        self.numblends = data[14]
        self.animindexindex = data[15]

    #    inline int            anim( int x, int y ) const
    #    {
    #        if ( x >= groupsize[0] )
    #        {
    #            x = groupsize[0] - 1;
    #        }

    #        if ( y >= groupsize[1] )
    #        {
    #            y = groupsize[ 1 ] - 1;
    #        }

    #        int offset = y * groupsize[0] + x;
    #        short *blends = (short *)(((byte *)this) + animindexindex);
    #        int value = (int)blends[ offset ];
    #        return value;
    #    }
    

        self.movementindex = data[16]
        self.groupsize = (data[17], data[18])
        self.paramindex = (data[19], data[20])
        self.paramstart = (data[21], data[22])
        self.paramend = (data[23], data[24])
        self.paramparent = data[25]
        self.fadeintime = data[26]
        self.fadeouttime = data[27]
        self.localentrynode = data[28]
        self.localexitnode = data[29]
        self.nodeflags = data[30]
        self.entryphase = data[31]
        self.exitphase = data[32]
        self.lastframe = data[33]
        self.nextseq = data[34]
        self.pose = data[35]
        self.numikrules = data[36]
        self.numautolayers = data[37]
        self.autolayerindex = data[38]
        # inline mstudioautolayer_t *pAutolayer( int i ) const { assert( i >= 0 && i < numautolayers); return (mstudioautolayer_t *)(((byte *)this) + autolayerindex) + i; };
        self.weightlistindex = data[39]
        # inline float		*pBoneweight( int i ) const { return ((float *)(((byte *)this) + weightlistindex) + i); };
        # inline float		weight( int i ) const { return *(pBoneweight( i)); };

        # FIXME: make this 2D instead of 2x1D arrays
        self.posekeyindex = data[40]
        # float             *pPoseKey( int iParam, int iAnim ) const { return (float *)(((byte *)this) + posekeyindex) + iParam * groupsize[0] + iAnim; }
        # float             poseKey( int iParam, int iAnim ) const { return *(pPoseKey( iParam, iAnim )); }

        self.numiklocks = data[41]
        self.iklockindex = data[42]
        # inline mstudioiklock_t *pIKLock( int i ) const { assert( i >= 0 && i < numiklocks); return (mstudioiklock_t *)(((byte *)this) + iklockindex) + i; };
        self.keyvalueindex = data[43]
        self.keyvaluesize = data[44]
        # inline const char * KeyValueText( void ) const { return keyvaluesize != 0 ? ((char *)this) + keyvalueindex : NULL; }

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.szlabelindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            Labeldata = struct.unpack(binary_format, temp_data)
            if Labeldata[0] == '\x00':
                break
            self.pszLabel = self.pszLabel + Labeldata[0]
        if logging == 1:
            tobj.logcon ("pszLabel: " + self.pszLabel)
            tobj.logcon ("szactivitynameindex: " + str(self.szactivitynameindex))
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("activity: " + str(self.activity))
            tobj.logcon ("actweight: " + str(self.actweight))
            tobj.logcon ("numevents: " + str(self.numevents))
            tobj.logcon ("eventindex: " + str(self.eventindex))
            tobj.logcon ("bboxmin: " + str(self.bboxmin))
            tobj.logcon ("bboxmax: " + str(self.bboxmax))
            tobj.logcon ("animindexindex: " + str(self.animindexindex))
            tobj.logcon ("movementindex: " + str(self.movementindex))
            tobj.logcon ("groupsize: " + str(self.groupsize))
            tobj.logcon ("paramindex: " + str(self.paramindex))
            tobj.logcon ("paramstart: " + str(self.paramstart))
            tobj.logcon ("paramend: " + str(self.paramend))
            tobj.logcon ("paramparent: " + str(self.paramparent))
            tobj.logcon ("fadeintime: " + str(self.fadeintime))
            tobj.logcon ("fadeouttime: " + str(self.fadeouttime))
            tobj.logcon ("localentrynode: " + str(self.localentrynode))
            tobj.logcon ("localexitnode: " + str(self.localexitnode))
            tobj.logcon ("nodeflags: " + str(self.nodeflags))
            tobj.logcon ("entryphase: " + str(self.entryphase))
            tobj.logcon ("exitphase: " + str(self.exitphase))
            tobj.logcon ("lastframe: " + str(self.lastframe))
            tobj.logcon ("nextseq: " + str(self.nextseq))
            tobj.logcon ("pose: " + str(self.pose))
            tobj.logcon ("numikrules: " + str(self.numikrules))
            tobj.logcon ("numautolayers: " + str(self.numautolayers))
            tobj.logcon ("autolayerindex: " + str(self.autolayerindex))
            tobj.logcon ("weightlistindex: " + str(self.weightlistindex))
            tobj.logcon ("posekeyindex: " + str(self.posekeyindex))
            tobj.logcon ("numiklocks: " + str(self.numiklocks))
            tobj.logcon ("iklockindex: " + str(self.iklockindex))
            tobj.logcon ("keyvalueindex: " + str(self.keyvalueindex))
            tobj.logcon ("keyvaluesize: " + str(self.keyvaluesize))
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        # DAN this is not right
        # inline char * const pszActivityName( void ) const { return ((char *)this) + szactivitynameindex; }
        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.szactivitynameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        start = 0
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            Namedata = struct.unpack(binary_format, temp_data)
            if Namedata[0] == '\x00':
                if start != 0:
                    break
                else:
                    start = start + 1
                    continue
            self.pszActivityName = self.pszActivityName + Namedata[0]
        if logging == 1:
            tobj.logcon ("DAN PLEASE FIX THIS pszActivityName: " + self.pszActivityName)
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


class HL2_AnimBlock:
    #Header Structure   #item of file, type, description.
    datastart = 0       #item   0      int.
    dataend = 0         #item   0      int.
    binary_format="<2i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.datastart = 0
        self.dataend = 0
        self.binary_format="<2i"

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.datastart = data[0]
        self.dataend = data[1]


class HL2_EyeBall:
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int.
    pszName = ""
    bone = 0               #item   1      int.
    org = (0.0)*3          #item   2-4    3 floats.
    zoffset = 0.0          #item   5      float.
    radius = 0.0           #item   6      float.
    up = (0.0)*3           #item   7-9    3 floats.
    forward = (0.0)*3      #item   10-12  3 floats.
    texture = 0            #item   13     int.
    iris_material = 0      #item   14     int.
    iris_scale = 0.0       #item   15     float.
    glint_material = 0     #item   16     int.
    upperflexdesc = (0)*3  #item   17-19  3 ints, index of raiser, neutral, and lowerer flexdesc that is set by flex controllers.
    lowerflexdesc = (0)*3  #item   20-22  3 ints.
    uppertarget = (0.0)*3  #item   23-25  3 floats, angle (radians) of raised, neutral, and lowered lid positions.
    lowertarget = (0.0)*3  #item   26-28  3 floats.
    upperlidflexdesc = 0   #item   29     int, index of flex desc that actual lid flexes look to.
    lowerlidflexdesc = 0   #item   30     int.
    unused1 = 0            #item   31     int.
    unused2 = 0            #item   32     int.
    unused3 = 0            #item   33     int.
    unused4 = 0            #item   34     int.
    unused5 = 0            #item   35     int.
    unused6 = 0            #item   36     int.
    unused7 = 0            #item   37     int.
    unused8 = 0            #item   38     int.
    unused9 = 0            #item   39     int.
    unused10 = 0           #item   40     int.
    unused11 = 0           #item   41     int.
    unused12 = 0           #item   42     int.
    binary_format = "<2i3f2f3f3f2ifi3i3i3f3f14i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.sznameindex = 0
        self.pszName = ""
        self.bone = 0
        self.org = (0.0)*3
        self.zoffset = 0.0
        self.radius = 0.0
        self.up = (0.0)*3
        self.forward = (0.0)*3
        self.texture = 0
        self.iris_material = 0
        self.iris_scale = 0.0
        self.glint_material = 0
        self.upperflexdesc = (0)*3
        self.lowerflexdesc = (0)*3
        self.uppertarget = (0.0)*3
        self.lowertarget = (0.0)*3
        self.upperlidflexdesc = 0
        self.lowerlidflexdesc = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.unused9 = 0
        self.unused10 = 0
        self.unused11 = 0
        self.unused12 = 0
        self.binary_format = "<2i3f2f3f3f2ifi3i3i3f3f14i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 172 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        if logging == 1:
            tobj.logcon ("======================================")
            tobj.logcon ("HL2_EyeBall data")
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("bone: " + str(self.bone))
            tobj.logcon ("org: " + str(self.org))
            tobj.logcon ("zoffset: " + str(self.zoffset))
            tobj.logcon ("radius: " + str(self.radius))
            tobj.logcon ("up: " + str(self.up))
            tobj.logcon ("forward: " + str(self.forward))
            tobj.logcon ("texture: " + str(self.texture))
            tobj.logcon ("iris_material: " + str(self.iris_material))
            tobj.logcon ("iris_scale: " + str(self.iris_scale))
            tobj.logcon ("glint_material: " + str(self.glint_material))
            tobj.logcon ("upperflexdesc: " + str(self.upperflexdesc))
            tobj.logcon ("lowerflexdesc: " + str(self.lowerflexdesc))
            tobj.logcon ("uppertarget: " + str(self.uppertarget))
            tobj.logcon ("lowertarget: " + str(self.lowertarget))
            tobj.logcon ("upperlidflexdesc: " + str(self.upperlidflexdesc))
            tobj.logcon ("lowerlidflexdesc: " + str(self.lowerlidflexdesc))
        self.sznameindex = data[0]
        self.bone = data[1]
        self.org = (data[2], data[3], data[4])
        self.zoffset = data[5]
        self.radius = data[6]
        self.up = (data[7], data[8], data[9])
        self.forward = (data[10], data[11], data[12])
        self.texture = data[13] # Value given incorrect, do not use it. Mesh has the correct texture to use.
        self.iris_material = data[14] # Value given IS correct, USE IT when HL2_VTXFileReader "mesh_flags = 2".
        self.iris_scale = data[15]
        self.glint_material = data[16] # Value given IS correct, USE IT when HL2_VTXFileReader "mesh_flags = 2".
        self.upperflexdesc = (data[17], data[18], data[19])
        self.lowerflexdesc = (data[20], data[21], data[22])
        self.uppertarget = (data[23], data[24], data[25])
        self.lowertarget = (data[26], data[27], data[28])
        self.upperlidflexdesc = data[29]
        self.lowerlidflexdesc = data[30]
        self.unused1 = data[31]
        self.unused2 = data[32]
        self.unused3 = data[33]
        self.unused4 = data[34]
        self.unused5 = data[35]
        self.unused6 = data[36]
        self.unused7 = data[37]
        self.unused8 = data[38]
        self.unused9 = data[39]
        self.unused10 = data[40]
        self.unused11 = data[41]
        self.unused12 = data[42]

        SaveCurOffset = file.tell() # Save the file current offset pointer.

        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]
        if logging == 1:
            tobj.logcon ("pszName: " + self.pszName)

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


class HL2_Node:
    #Header Structure      #item of file, type, description.
    bone = 0               #item   0      int, the bone's index.
    group = 0              #item   1      int, intersection group.
    bbmin = (0.0)*3        #item   2-4    3 floats, bounding box min x,y,z Vector.
    bbmax = (0.0)*3        #item   5-7    3 floats, bounding box max x,y,z Vector.
    szhitboxnameindex = 0  #item   8      int, offset to the name of the hitbox.
    unused1 = 0            #item   9      int.
    unused2 = 0            #item   10     int.
    unused3 = 0            #item   11     int.
    unused4 = 0            #item   12     int.
    unused5 = 0            #item   13     int.
    unused6 = 0            #item   14     int.
    unused7 = 0            #item   15     int.
    unused8 = 0            #item   16     int.
    pszLocalNodeName = ""  # returned string of the bbox name, if any.
    binary_format="<64c"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone = 0
        self.group = 0
        self.bbmin = (0.0)*3
        self.bbmax = (0.0)*3
        self.szhitboxnameindex = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.unused5 = 0
        self.unused6 = 0
        self.unused7 = 0
        self.unused8 = 0
        self.pszLocalNodeName = ""
        self.binary_format="<64c"  #little-endian (<), see #item descriptions above.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        """self.bone = data[0]
        self.group = data[1]
        self.bbmin = (data[2], data[3], data[4])
        self.bbmax = (data[5], data[6], data[7])
        self.szhitboxnameindex = data[8]
        self.unused1 = data[9]
        self.unused2 = data[10]
        self.unused3 = data[11]
        self.unused4 = data[12]
        self.unused5 = data[13]
        self.unused6 = data[14]
        self.unused7 = data[15]
        self.unused8 = data[16]
        if self.szhitboxnameindex != 0:
            CurOffset = file.tell() # Save the file current offset pointer.
            file.seek(self.szhitboxnameindex, 0) # change the file offset pointer position.
            binary_format="<64c"
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            self.HitBoxName = data
            file.seek(CurOffset, 0) # Reset the file offset pointer back to where it should be now."""
        self.pszLocalNodeName = data

        if logging == 1:
            tobj.logcon ("--------------HL2_Node----------------")
            tobj.logcon ("pszLocalNodeName: " + str(self.pszLocalNodeName))
            """tobj.logcon ("bone: " + str(self.bone))
            tobj.logcon ("group: " + str(self.group))
            tobj.logcon ("bbmin: " + str(self.bbmin))
            tobj.logcon ("bbmax: " + str(self.bbmax))
            tobj.logcon ("szhitboxnameindex: " + str(self.szhitboxnameindex))"""


class HL2_FlexDesc:
    #Header Structure      #item of file, type, description.
    szFACSindex = 0        #item   0      int.
    pszFACS = ""
    binary_format="<i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.szFACSindex = 0
        self.pszFACS = ""
        self.binary_format="<i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 4 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.szFACSindex = data[0]

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.szFACSindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszFACS = self.pszFACS + data[0]
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        if logging == 1:
            tobj.logcon ("szFACSindex: " + str(self.szFACSindex))
            tobj.logcon ("pszFACS: " + str(self.pszFACS))


class HL2_FlexController:
    #Header Structure      #item of file, type, description.
    sztypeindex = 0        #item   0      int.
    pszType = ""
    sznameindex = 0        #item   1      int.
    pszName = ""
    link = 0               #item   2      int, remapped at load time to master list.
    min = 0.0              #item   3      float.
    max = 0.0              #item   4      float.
    binary_format="<3i2f"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.sztypeindex = 0
        self.pszType = ""
        self.sznameindex = 0
        self.pszName = ""
        self.min = 0.0
        self.max = 0.0
        self.binary_format="<3i2f"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 20 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.sztypeindex = data[0]
        self.sznameindex = data[1]
        self.link = data[2]
        self.min = data[3]
        self.max = data[4]

        SaveCurOffset = file.tell() # Save the file current offset pointer.

        file.seek(SaveCurOffset - self.data_read_in + self.sztypeindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszType = self.pszType + data[0]

        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        if logging == 1:
            tobj.logcon ("sztypeindex: " + str(self.sztypeindex))
            tobj.logcon ("pszType: " + str(self.pszType))
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("link: " + str(self.link))
            tobj.logcon ("min: " + str(self.min))
            tobj.logcon ("max: " + str(self.max))


class HL2_FlexOp: # DAN not sure this is right
    #Header Structure      #item of file, type, description.
    op = 0                 #item   0      int.
    union_value = 0.0      #item   1      float (could be an int=index or float=value) so we just use a float.
    binary_format="<if"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.op = 0
        self.union_value = 0.0
        self.binary_format = "<if"  #little-endian (<), see #item descriptions above.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.op = data[0]
        self.union_value = data[1]

        if logging == 1:
            tobj.logcon ("op: " + str(self.op))
            tobj.logcon ("union_value: " + str(self.union_value))


class HL2_FlexRule:
    #Header Structure      #item of file, type, description.
    flex = 0               #item   0      int.
    numops = 0             #item   1      int.
    opindex = 0            #item   2      int.
    binary_format="<3i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.flex = 0
        self.numops = 0
        self.opindex = 0
        self.binary_format="<3i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 12 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.flex = data[0]
        self.numops = data[1]
        self.opindex = data[2]

        if logging == 1:
            tobj.logcon ("flex: " + str(self.flex))
            tobj.logcon ("numops: " + str(self.numops))
            tobj.logcon ("opindex: " + str(self.opindex))

        SaveCurOffset = file.tell() # Save the file current offset pointer.

        file.seek(SaveCurOffset - self.data_read_in + self.opindex, 0) # change the file offset pointer position.
        for op in xrange(self.numops):
            if logging == 1:
                tobj.logcon ("--------------" + str(op) + " HL2_FlexOp ----------------")
            flexop = HL2_FlexOp()
            flexop.load(file)

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


class HL2_IKLink:
    #Header Structure      #item of file, type, description.
    bone = 0               #item   0      int.
    kneeDir = (0.0)*3      #item   1-3    3 floats, ideal bending direction (per link, if applicable).
    unused0 = (0.0)*3      #item   4-6    3 floats, unused.
    binary_format = "<i3f3f"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone = 0
        self.kneeDir = (0.0)*3
        self.unused0 = (0.0)*3
        self.binary_format = "<i3f3f"  #little-endian (<), see #item descriptions above.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.bone = data[0]
        self.kneeDir = (data[1], data[2], data[3])
        self.unused0 = (data[4], data[5], data[6])

        if logging == 1:
            tobj.logcon ("bone: " + str(self.bone))
            tobj.logcon ("kneeDir: " + str(self.kneeDir))
            tobj.logcon ("unused0: " + str(self.unused0))


class HL2_IKChain:
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int.
    pszName = ""
    linktype = 0           #item   1      int.
    numlinks = 0           #item   2      int.
    linkindex = 0          #item   3      int.
    binary_format="<4i"  #little-endian (<), see #item descriptions above.

    links = []

    def __init__(self):
        self.sznameindex = 0
        self.pszName = ""
        self.linktype = 0
        self.numlinks = 0
        self.linkindex = 0
        self.binary_format="<4i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 16 # Total binary_format byte value above, used below to set the file offset pointer back.
        self.links = []

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.sznameindex = data[0]
        self.linktype = data[1]
        self.numlinks = data[2]
        self.linkindex = data[3]

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        if logging == 1:
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("linktype: " + str(self.linktype))
            tobj.logcon ("numlinks: " + str(self.numlinks))
            tobj.logcon ("linkindex: " + str(self.linkindex))

        SaveCurOffset = file.tell() # Save the file current offset pointer.

        file.seek(SaveCurOffset - self.data_read_in + self.linkindex, 0) # change the file offset pointer position.
        for i in xrange(self.numlinks):
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_IKLink ----------------")
            link = HL2_IKLink()
            link.load(file)
            self.links.append(link)

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.


class HL2_Mouth:
    #Header Structure      #item of file, type, description.
    bone = 0               #item   0      int.
    forward = (0.0)*3      #item   1-3    3 floats.
    flexdesc = 0           #item   4      int.
    binary_format="<i3fi"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone = 0
        self.forward = (0.0)*3
        self.flexdesc = 0
        self.binary_format="<i3fi"  #little-endian (<), see #item descriptions above.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.bone = data[0]
        self.forward = (data[1], data[2], data[3])
        self.flexdesc = data[4]

        if logging == 1:
            tobj.logcon ("-------------HL2_Mouth---------------")
            tobj.logcon ("bone: " + str(self.bone))
            tobj.logcon ("forward: " + str(self.forward))
            tobj.logcon ("flexdesc: " + str(self.flexdesc))


class HL2_LocalPoseParameter:
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int.
    pszName = ""
    flags = 0              #item   1      int, ????.
    start = 0.0            #item   2      float, starting value.
    end = 0.0              #item   3      float, ending value.
    loop = 0.0             #item   4      float, looping range, 0 for no looping, 360 for rotations, etc.
    binary_format="<2i3f"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.sznameindex = 0
        self.flags = 0
        self.pszName = ""
        self.start = 0.0
        self.end = 0.0
        self.loop = 0.0
        self.binary_format="<2i3f"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 20 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.sznameindex = data[0]
        self.flags = data[1]
        self.start = data[4]
        self.end = data[4]
        self.loop = data[4]

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        if logging == 1:
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("pszName: " + self.pszName)
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("start: " + str(self.start))
            tobj.logcon ("end: " + str(self.end))
            tobj.logcon ("loop: " + str(self.loop))


class HL2_SurfaceProp:
    #Header Structure      #item of file, type, description.
    pszName = ""

    def __init__(self):
        self.pszName = ""

    def load(self, file):
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]

        if logging == 1:
            tobj.logcon ("pszName: " + self.pszName)


class HL2_KeyValues(object):
    #Header Structure      #item of file, type, description.
    mdlkeyvalues = ""

    def __init__(self):
        self.mdlkeyvalues = ""
        self.binaryFormat = "<%ds" % 0

    def Load(self, file, keyvaluesize):
        # where are we in the file (for calculating real offsets) just for print test below, remove when done.
        ofsBegin = file.tell()
        self.binaryFormat = "<%ds" % keyvaluesize
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.mdlkeyvalues = data[0].split("\x00")

        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("======HL2_KeyValues======")
            tobj.logcon ("ofsBegin: " + str(ofsBegin))
            tobj.logcon ("keyvaluesize: " + str(keyvaluesize))
            tobj.logcon ("mdlkeyvalues: " + str(self.mdlkeyvalues))

        return self


class HL2_LocalIKAutoplayLock:
    #Header Structure      #item of file, type, description.
    chain = 0              #item   0      int.
    flPosWeight = 0.0      #item   1      float.
    flLocalQWeight = 0.0   #item   2      float.
    flags = 0              #item   3      int.
    unused1 = 0            #item   4      int.
    unused2 = 0            #item   5      int.
    unused3 = 0            #item   6      int.
    unused4 = 0            #item   7      int.
    binary_format="<i2f5i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.chain = 0
        self.flPosWeight = 0.0
        self.flLocalQWeight = 0.0
        self.flags = 0
        self.unused1 = 0
        self.unused2 = 0
        self.unused3 = 0
        self.unused4 = 0
        self.binary_format="<i2f5i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 20 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.chain = data[0]
        self.flPosWeight = data[1]
        self.flLocalQWeight = data[2]
        self.flags = data[3]
        self.unused1 = data[4]
        self.unused2 = data[5]
        self.unused3 = data[6]
        self.unused4 = data[7]

        if logging == 1:
            tobj.logcon ("chain: " + str(self.chain))
            tobj.logcon ("flPosWeight: " + str(self.flPosWeight))
            tobj.logcon ("flLocalQWeight: " + str(self.flLocalQWeight))
            tobj.logcon ("flags: " + str(self.flags))


class HL2_ModelGroup:
    #Header Structure      #item of file, type, description.
    szlabelindex = 0       #item   0      int, textual name.
    pszLabel = ""
    sznameindex = 0        #item   1      int, file name.
    pszName = ""
    binary_format="<2i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.szlabelindex = 0
        self.pszLabel = ""
        self.sznameindex = 0
        self.pszName = ""
        self.binary_format="<2i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 8 # Total binary_format byte value above, used below to set the file offset pointer back.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.szlabelindex = data[0]
        self.sznameindex = data[1]

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.szlabelindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszLabel = self.pszLabel + data[0]
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset - self.data_read_in + self.sznameindex, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]
        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

        if logging == 1:
            tobj.logcon ("----HL2_ModelGroup----")
            tobj.logcon ("szlabelindex: " + str(self.szlabelindex))
            tobj.logcon ("pszLabel: " + self.pszLabel)
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("pszName: " + self.pszName)


######################################################
# ANI Importer Functions and animation data structures
######################################################
class HL2_ANIStudioAnim:
    #Header Structure  #item of file, type, description.
    bone = 0           #item   0      byte
    flags = 0          #item   1      byte, weighing options
    nextoffset = 0     #item   2      short
    binary_format="<2Bh"  #little-endian (<), see #item descriptions above.
    
    def __init__(self):
        self.bone = 0
        self.flags = 0
        self.nextoffset = 0
        self.binary_format="<2Bh"

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.bone = data[0]
        self.flags = data[1]
        self.nextoffset = data[2]


######################################################
# VVD Importer Functions and vertex data structures
######################################################
class HL2_VVDFileReader:
    #Header Structure      #item of file, type, description.
    id = ""                #item   0      4s,  MODEL_VERTEX_FILE_ID.
    version = 0            #item   1      int, MODEL_VERTEX_FILE_VERSION.
    checksum = 0           #item   2      int, same as studiohdr_t, ensures sync.
    numLODs = 0            #item   3      int, num of valid lods.
    numLODVertexes = [0]*8 #item   4-11   8 ints, num verts for desired root lod.
    numFixups = 0          #item   12     int, num of vertexFileFixup_t.
    fixupTableStart = 0    #item   13     int, offset from base to fixup table.
    vertexDataStart = 0    #item   14     int, offset from base to vertex block.
    tangentDataStart = 0   #item   15     int, offset from base to tangent block.
    binary_format="<4s15i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.id = ""
        self.version = 0
        self.checksum = 0
        self.numLODs = 0
        self.numLODVertexes = [0]*8
        self.numFixups = 0
        self.fixupTableStart = 0
        self.vertexDataStart = 0
        self.tangentDataStart = 0
        self.binary_format="<4s15i"  #little-endian (<), see #item descriptions above.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.id = data[0]
        self.version = data[1]
        self.checksum = data[2]
        self.numLODs = data[3]
        self.numLODVertexes = [data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]]
        self.numFixups = data[12]
        self.fixupTableStart = data[13]
        self.vertexDataStart = data[14]
        self.tangentDataStart = data[15]

        if logging == 1:
            tobj.logcon ("id: " + str(self.id))
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("checksum: " + str(self.checksum))
            tobj.logcon ("numLODs: " + str(self.numLODs))
            tobj.logcon ("numLODVertexes: " + str(self.numLODVertexes))
            tobj.logcon ("numFixups: " + str(self.numFixups))
            tobj.logcon ("fixupTableStart: " + str(self.fixupTableStart))
            tobj.logcon ("vertexDataStart: " + str(self.vertexDataStart))
            tobj.logcon ("tangentDataStart: " + str(self.tangentDataStart))

        return self


class HL2_VVDFixup:
    #Header Structure      #item of file, type, description.
    lod = 0                #item   0      int, used to skip culled root lod
    sourceVertexID = 0     #item   1      int, absolute index from start of vertex/tangent blocks
    numVertexes = 0        #item   2      int, ?
    binary_format="<3i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.lod = 0
        self.sourceVertexID = 0
        self.numVertexes = 0
        self.binary_format="<3i"  #little-endian (<), see #item descriptions above.

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.lod = data[0]
        self.sourceVertexID = data[1]
        self.numVertexes = data[2]

      #  if logging == 1:
      #      tobj.logcon ("lod: " + str(self.lod))
      #      tobj.logcon ("sourceVertexID: " + str(self.sourceVertexID))
      #      tobj.logcon ("numVertexes: " + str(self.numVertexes))

        return self


def HL2_GetVertexData(mdl_name):
    file_name = mdl_name.lower() # Make sure all text is lower case.
    file_name = file_name + ".mdl"
    file_name = file_name.replace(".mdl", ".vvd")
    cur_dir = os.getcwd()
    files = os.listdir(cur_dir)
    for item in range(len(files)):
        item_name = files[item].lower() # Make sure all text is lower case.
        if item_name == file_name:
            vvd_file = open(cur_dir + "\\" + files[item], "rb")
            break
        if item == len(files) - 1:
            quarkx.msgbox("Could not find vertex file:\n\n" + file_name + "\n\nImport of model aborted.", MT_ERROR, MB_OK)
            return None

    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("====================")
        tobj.logcon ("      VVD FILE")
        tobj.logcon ("vvd_file: " + str(vvd_file))
        tobj.logcon ("====================")
        tobj.logcon ("--------- HL2_VVDFileReader ---------")

    VVD = HL2_VVDFileReader()
    VVDFileReader = VVD.load(vvd_file)
    return vvd_file, VVDFileReader


######################################################
# VTX Importer Functions and triangle data structures
######################################################
class HL2_VTXFileReader:
    #Header Structure            #item of file, type, description.
    vtx_version = 0              #item   0      int.
    vertex_cache_size = 0        #item   1      int.
    max_bones_per_strip = 0      #item   2      unsigned short.
    max_bones_per_tri = 0        #item   3      unsigned short.
    max_bones_per_vertex = 0     #item   4      int.
    check_sum = 0                #item   5      int.
    num_lods = 0                 #item   6      int.
    mtl_replace_list_offset = 0  #item   7      int.
    num_body_parts = 0           #item   8      int.
    body_part_offset = 0         #item   9      int.
    binary_format="<2i2H6i"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.vtx_version = 0
        self.vertex_cache_size = 0
        self.max_bones_per_strip = 0
        self.max_bones_per_tri = 0
        self.max_bones_per_vertex = 0
        self.check_sum = 0
        self.num_lods = 0
        self.mtl_replace_list_offset = 0
        self.num_body_parts = 0
        self.body_part_offset = 0
        self.binary_format="<2i2H6i"  #little-endian (<), see #item descriptions above.

    def load(self, vtx_file, HL2_Obj, vvd_file, ComponentList):
        # Things we will need.
        QuArKBonesData = HL2_Obj.QuArKBonesData
        ModelComponentList = editor.ModelComponentList

        temp_data = vtx_file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.vtx_version = data[0]
        self.vertex_cache_size = data[1]
        self.max_bones_per_strip = data[2]
        self.max_bones_per_tri = data[3]
        self.max_bones_per_vertex = data[4]
        self.check_sum = data[5]
        self.num_lods = data[6]
        self.mtl_replace_list_offset = data[7]
        self.num_body_parts = data[8]
        self.body_part_offset = data[9]

        if logging == 1:
            tobj.logcon ("vtx_version: " + str(self.vtx_version))
            tobj.logcon ("vertex_cache_size: " + str(self.vertex_cache_size))
            tobj.logcon ("max_bones_per_strip: " + str(self.max_bones_per_strip))
            tobj.logcon ("max_bones_per_tri: " + str(self.max_bones_per_tri))
            tobj.logcon ("max_bones_per_vertex: " + str(self.max_bones_per_vertex))
            tobj.logcon ("check_sum: " + str(self.check_sum))
            tobj.logcon ("num_lods: " + str(self.num_lods))
            tobj.logcon ("mtl_replace_list_offset: " + str(self.mtl_replace_list_offset))
            tobj.logcon ("num_body_parts: " + str(self.num_body_parts))
            tobj.logcon ("body_part_offset: " + str(self.body_part_offset))

        vtx_file.seek(self.body_part_offset, 0)
        new_ComponentList = []
        for i in xrange(self.num_body_parts):
            binary_format="<2i"
            temp_data = vtx_file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            num_models = data[0]
            model_offset = data[1]

            if logging == 1:
                tobj.logcon ("num_models: " + str(num_models))
                tobj.logcon ("model_offset: " + str(model_offset))
                tobj.logcon ("-------------------")

            SaveCurBodyPartOffset = vtx_file.tell() # Save the file current LOD offset pointer.
            vtx_file.seek(self.body_part_offset + (i * 8) + model_offset, 0)

            for j in xrange(num_models):
                binary_format="<2i"
                temp_data = vtx_file.read(struct.calcsize(binary_format))
                data = struct.unpack(binary_format, temp_data)
                num_lods = data[0]
                lod_offset = data[1]

                if logging == 1:
                    tobj.logcon ("num_lods: " + str(num_lods))
                    tobj.logcon ("lod_offset: " + str(lod_offset))
                    tobj.logcon ("-------------------")

                SaveCurModelOffset = vtx_file.tell() # Save the file current LOD offset pointer.
                vtx_file.seek(self.body_part_offset + (i * 8) + model_offset + (j * 8) + lod_offset, 0)

                for k in xrange(num_lods):
                    binary_format="<2if"
                    temp_data = vtx_file.read(struct.calcsize(binary_format))
                    data = struct.unpack(binary_format, temp_data)
                    num_meshes = data[0]
                    mesh_offset = data[1]
                    switch_point = data[2]

                    if logging == 1:
                        tobj.logcon ("num_meshes: " + str(num_meshes))
                        tobj.logcon ("mesh_offset: " + str(mesh_offset))
                        tobj.logcon ("switch_point: " + str(switch_point))
                        tobj.logcon ("-------------------")

                    if k == 0: # If we go beyond the 1st set the data turns to junk!?
                        # Setup things we will need.
                        skins = HL2_Obj.skins_group # A list of the .vtf skin files full paths and names.
                        materials = HL2_Obj.materials_group # A list of the .vmt material files full paths and names to go with skins above.
                        meshes = HL2_Obj.bodyparts[i].models[j].meshes
                        eyeballs = HL2_Obj.bodyparts[i].models[j].eyeballs
                        eyeball_count = 0

                        SaveCurLodOffset = vtx_file.tell() # Save the file current LOD offset pointer.
                        vtx_file.seek(self.body_part_offset + (i * 8) + model_offset + (j * 8) + lod_offset + (k * 12) + mesh_offset, 0)

                        for l in xrange(num_meshes):
                            mesh = meshes[l] # Original set of mdl_mesh es.
                            # Original set of mesh vertex data.
                            # dict. list [vtx_index] = [[ 3 weight values ], [ 3 weight bone indexes ], # of bones, ( vertex position ), ( vertex normal ), [ vertex U,V values ]]
                            mesh_pointer = vtx_file.tell()
                            binary_format="<2iB"
                            temp_data = vtx_file.read(struct.calcsize(binary_format))
                            data = struct.unpack(binary_format, temp_data)
                            num_strip_groups = data[0]
                            strip_group_offset = data[1]
                            mesh_flags = data[2] # 1 = teeth, 2 = eyes, 0 = other.

                            if logging == 1:
                                tobj.logcon ("========VTXMesh=======")
                                tobj.logcon ("num_strip_groups: " + str(num_strip_groups))
                                tobj.logcon ("strip_group_offset: " + str(strip_group_offset))
                                tobj.logcon ("mesh_flags: " + str(mesh_flags))
                                tobj.logcon ("===================")

                            SaveCurMeshOffset = vtx_file.tell() # Save the file current Mesh offset pointer.
                            vtx_file.seek(mesh_pointer + strip_group_offset, 0)
                            for m in xrange(num_strip_groups): # Make QuArK additional components here.
                                new_comp = ComponentList[i+l].copy()
                                if m > 0:
                                    new_comp.shortname = new_comp.shortname + str(m)
                                if mesh_flags != 2:
                                    skin_path = skins[mesh.material][0]
                                    material_path = materials[mesh.material][0]
                                    if skin_path != "None":
                                        skinname = 'models' + skin_path.split('/models')[1]
                                        skin = quarkx.newobj(skinname)
                                        image = quarkx.openfileobj(skin_path)
                                        skin['Image1'] = image.dictspec['Image1']
                                        skin['Size'] = image.dictspec['Size']
                                        skin['HL_skin_flags'] = skins[mesh.material][1]
                                        if material_path != "None":
                                            shader_keyword, shader_file, shader_name, mesh_shader = ReadMaterialFile(material_path)
                                            new_comp['shader_keyword'] = skin['shader_keyword'] = shader_keyword
                                            new_comp['shader_file'] = skin['shader_file'] = shader_file
                                            new_comp['shader_name'] = skin['shader_name'] = shader_name
                                            new_comp['mesh_shader'] = skin['mesh_shader'] = mesh_shader
                                            new_comp['skin_name'] = skin.name
                                        else:
                                            new_comp['shader_keyword'] = skin['shader_keyword'] = material_path
                                        new_comp.dictitems['Skins:sg'].appenditem(skin)
                                        new_comp['skinsize'] = skin['Size']
                                else:
                                    if eyeball_count < len(eyeballs):
                                        eyeball = eyeballs[eyeball_count]
                                        skin_path = skins[eyeball.iris_material][0]
                                        material_path = materials[eyeball.iris_material][0]
                                    if skin_path != "None":
                                        skinname = 'models' + skin_path.split('/models')[1]
                                        skin = quarkx.newobj(skinname)
                                        image = quarkx.openfileobj(skin_path)
                                        skin['Image1'] = image.dictspec['Image1']
                                        skin['Size'] = image.dictspec['Size']
                                        skin['HL_skin_flags'] = skins[eyeball.iris_material][1]
                                        if material_path != "None":
                                            shader_keyword, shader_file, shader_name, mesh_shader = ReadMaterialFile(material_path)
                                            new_comp['shader_keyword'] = skin['shader_keyword'] = shader_keyword
                                            new_comp['shader_file'] = skin['shader_file'] = shader_file
                                            new_comp['shader_name'] = skin['shader_name'] = shader_name
                                            new_comp['mesh_shader'] = skin['mesh_shader'] = mesh_shader
                                            new_comp['skin_name'] = skin.name
                                        else:
                                            new_comp['shader_keyword'] = skin['shader_keyword'] = material_path
                                        new_comp.dictitems['Skins:sg'].appenditem(skin)
                                        new_comp['skinsize'] = skin['Size']
                                    if eyeball_count < len(eyeballs):
                                        skin_path = skins[eyeball.glint_material][0]
                                        material_path = materials[eyeball.glint_material][0]
                                    if skin_path != "None":
                                        skinname = 'models' + skin_path.split('/models')[1]
                                        skin = quarkx.newobj(skinname)
                                        image = quarkx.openfileobj(skin_path)
                                        skin['Image1'] = image.dictspec['Image1']
                                        skin['Size'] = image.dictspec['Size']
                                        skin['HL_skin_flags'] = skins[eyeball.glint_material][1]
                                        if material_path != "None":
                                            shader_keyword, shader_file, shader_name, mesh_shader = ReadMaterialFile(material_path)
                                            skin['shader_keyword'] = shader_keyword
                                            skin['shader_file'] = shader_file
                                            skin['shader_name'] = shader_name
                                            skin['mesh_shader'] = mesh_shader
                                            if not new_comp.dictspec.has_key('skin_name'):
                                                new_comp['shader_keyword'] = shader_keyword
                                                new_comp['shader_file'] = shader_file
                                                new_comp['shader_name'] = shader_name
                                                new_comp['mesh_shader'] = mesh_shader
                                                new_comp['skin_name'] = skin.name
                                        else:
                                            new_comp['shader_keyword'] = skin['shader_keyword'] = material_path
                                        skingroup = new_comp.dictitems['Skins:sg']
                                        skingroup.appenditem(skin)
                                        if len(skingroup.subitems) == 1:
                                            new_comp['skinsize'] = skin['Size']
                                    eyeball_count += 1
                                strip_group_pointer = vtx_file.tell()
                                binary_format="<6iB"
                                temp_data = vtx_file.read(struct.calcsize(binary_format))
                                data = struct.unpack(binary_format, temp_data)
                                num_vertices = data[0]
                                vertex_offset = data[1]
                                num_indices = data[2]
                                index_offset = data[3]
                                num_strips = data[4]
                                strip_offset = data[5]
                                strip_group_flags = data[6]

                                if logging == 1:
                                    tobj.logcon ("------VTXStripGroup------")
                                    tobj.logcon ("num_vertices: " + str(num_vertices))
                                    tobj.logcon ("vertex_offset: " + str(vertex_offset))
                                    tobj.logcon ("num_indices: " + str(num_indices))
                                    tobj.logcon ("index_offset: " + str(index_offset))
                                    tobj.logcon ("num_strips: " + str(num_strips))
                                    tobj.logcon ("strip_offset: " + str(strip_offset))
                                    tobj.logcon ("strip_group_flags: " + str(strip_group_flags))
                                    tobj.logcon ("------VTXVertex------")

                                SaveCurGroupOffset =  vtx_file.tell() # Save the file current Group offset pointer.

                                vtx_file.seek(strip_group_pointer + vertex_offset, 0)
                                binary_format="<3BBh3b"
                                comp_mesh = ()
                                UVs = []
                                TexWidth, TexHeigth = new_comp['skinsize']
                                # QuArKBonesData
                                bonevtxlist = {}
                                weightvtxlist = {}
                                for n in xrange(num_vertices): # Need to make a HL2_VTXVertex class for this, cdunde.
                                    temp_data = vtx_file.read(struct.calcsize(binary_format))
                                    data = struct.unpack(binary_format, temp_data)
                                    bone_weight_index = [data[0], data[1], data[2]]
                                    num_bones = data[3]
                                    orig_mesh_vertex_id = data[4]
                                    bone_id = [data[5], data[6], data[7]]
                                    vert_data = mesh.vertex_weights[orig_mesh_vertex_id]

                                    # Add to bonevtxlist, weightvtxlist and build bone vtxlist.
                                    bone_weight_values = vert_data[0]
                                    weight_bones = vert_data[1]
                                    num_bones = vert_data[2]
                                    for bone_index in xrange(num_bones):
                                        bi = weight_bones[bone_index]
                                        wv = bone_weight_values[bone_index]
                                        if not bonevtxlist.has_key(QuArKBonesData[bi][0]):
                                            bonevtxlist[QuArKBonesData[bi][0]] = {}
                                        bonevtxlist[QuArKBonesData[bi][0]][n] = {'color': '\x00\x00\xff'}
                                        if not weightvtxlist.has_key(n):
                                            weightvtxlist[n] = {}
                                        weightvtxlist[n][QuArKBonesData[bi][0]] = {'weight_value': wv, 'color': quarkpy.mdlutils.weights_color(editor, wv)}
                                        if not QuArKBonesData[bi][1].has_key(new_comp.name):
                                            QuArKBonesData[bi][1][new_comp.name] = []
                                        QuArKBonesData[bi][1][new_comp.name].append(n)
                                    # Make baseframe Vertices here.
                                    vert_pos = vert_data[3]
                                    comp_mesh = comp_mesh + vert_pos
                                    # Build UVs list here for Tris use below.
                                    vert_UV = vert_data[5]
                                    vert_UV = [int(vert_UV[0]*TexWidth), int(vert_UV[1]*TexHeigth)]
                                    UVs = UVs + [vert_UV]

                                ModelComponentList[new_comp.name] = {'colorvtxlist': {}}
                                ModelComponentList[new_comp.name]['bonevtxlist'] = bonevtxlist
                                ModelComponentList[new_comp.name]['weightvtxlist'] = weightvtxlist

                                baseframe = new_comp.dictitems['Frames:fg'].subitems[0]
                                baseframe['Vertices'] = comp_mesh

                                vtx_file.seek(strip_group_pointer + index_offset, 0)
                                vtx_indexes = []
                                binary_format="<H"
                                for n in xrange(num_indices):
                                    temp_data = vtx_file.read(struct.calcsize(binary_format))
                                    data = struct.unpack(binary_format, temp_data)
                                    vtx_indexes.append(data[0])

                                if logging == 1:
                                    tobj.logcon ("------VTXStrip------")

                                vtx_file.seek(strip_group_pointer + strip_offset, 0)
                                binary_format="<4ihB2i"
                                Tris = ''
                                for n in xrange(num_strips):
                                    temp_data = vtx_file.read(struct.calcsize(binary_format))
                                    data = struct.unpack(binary_format, temp_data)
                                    num_indices = data[0]
                                    index_offset = data[1]
                                    num_vertices = data[2]
                                    vertex_offset = data[3]
                                    num_bones = data[4]
                                    strip_flags = data[5]
                                    num_bone_state_changes = data[6]
                                    bone_state_change_offset = data[7]

                                    if logging == 1:
                                        tobj.logcon ("num_indices: " + str(num_indices))
                                        tobj.logcon ("index_offset: " + str(index_offset))
                                        tobj.logcon ("num_vertices: " + str(num_vertices))
                                        tobj.logcon ("vertex_offset: " + str(vertex_offset))
                                        tobj.logcon ("num_bones: " + str(num_bones))
                                        tobj.logcon ("strip_flags: " + str(strip_flags))
                                        tobj.logcon ("num_bone_state_changes: " + str(num_bone_state_changes))
                                        tobj.logcon ("bone_state_change_offset: " + str(bone_state_change_offset))

                                    if strip_flags == 1:
                                        #This is a triangle list
                                        # QuArK Tris made here.
                                        for triX in range(num_indices / 3):
                                            index_0 = index_offset + 3 * triX + 0
                                            index_1 = index_offset + 3 * triX + 1
                                            index_2 = index_offset + 3 * triX + 2
                                            if index_2 >= index_offset + num_indices:

                                                #Not a complete triangle?
                                                continue
                                            tri = (vtx_indexes[index_0], vtx_indexes[index_1], vtx_indexes[index_2])
                                            try:
                                                Tris = Tris + struct.pack("Hhh", tri[0], UVs[tri[0]][0], UVs[tri[0]][1])
                                                Tris = Tris + struct.pack("Hhh", tri[1], UVs[tri[1]][0], UVs[tri[1]][1])
                                                Tris = Tris + struct.pack("Hhh", tri[2], UVs[tri[2]][0], UVs[tri[2]][1])
                                            except:
                                                pass
                                    elif strip_flags == 2:
                                        #This is a triangle strip
                                      #  print "body_parts, model, mesh, strip_group, strip ->", i, j, l, m, n
                                      #  quarkx.beep()
                                        pass
                                    else:
                                        #Dunno
                                      #  print "body_parts, model, mesh, strip_group, strip ->", i, j, l, m, n
                                      #  print "STRIP_FLAGS IS ", strip_flags
                                      #  quarkx.beep()
                                        pass

                                new_comp['Tris'] = Tris #FIXME: Overwrites previous one...! Did fix, all strips should make ONE Tris...I think. 8-| (Valve sucks!)

                                vtx_file.seek(SaveCurGroupOffset, 0) # Reset the file current Group offset pointer back to where it should be now.

                                new_ComponentList.append(new_comp)
                                
                            vtx_file.seek(SaveCurMeshOffset) # Reset the file current Mesh offset pointer back to where it should be now.
                        vtx_file.seek(SaveCurLodOffset) # Reset the file current LOD offset pointer back to where it should be now.
                vtx_file.seek(SaveCurModelOffset)
            vtx_file.seek(SaveCurBodyPartOffset)
        ComponentList = new_ComponentList
        return ComponentList


def HL2_GetTriangleData(mdl_name):
    file_name = mdl_name.lower() # Make sure all text is lower case.
    file_name = file_name + ".mdl"
    file_name = file_name.replace(".mdl", ".dx90.vtx")
    cur_dir = os.getcwd()
    files = os.listdir(cur_dir)
    for item in range(len(files)):
        item_name = files[item].lower() # Make sure all text is lower case.
        if item_name == file_name:
            vtx_file = open(cur_dir + "\\" + files[item], "rb")
            break
        if item == len(files) - 1:
            quarkx.msgbox("Could not find triangle file:\n\n" + file_name + "\n\nImport of model aborted.", MT_ERROR, MB_OK)
            return None

    return vtx_file


class Tags(object):
    mdltagvalues = ""
    origin = [0.0, 0.0, 0.0]
    axis = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    binaryFormat = "<%ds" % 0

    def __init__(self):
        self.mdltagvalues = ""
        self.origin = [0.0, 0.0, 0.0]
        self.axis = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        self.binaryFormat = "<%ds" % 0

    def Load(self, file, tagvaluesize):
        self.binaryFormat = "<%ds" % tagvaluesize
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        self.mdltagvalues = data[0].split("\x00")

        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("mdltagvalues: " + str(self.mdltagvalues))

        return self


######################################################
# HL2 data structures (vectors and quaternions)
######################################################
class HL2_HitBoxSet:
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int, the bone's index.
    pszName = ""           #item   1      32 char, the bone's name.
    numhitboxes = 0        #item   2      int, number of hit boxes in the set.
    hitboxindex = 0        #item   3      int, hit boxes data index offset.
    bboxgroup = None

    def __init__(self):
        self.sznameindex = 0
        self.pszName = ""
        self.numhitboxes = 0
        self.hitboxindex = 0
        self.bboxgroup = None

    def load(self, file, QuArK_bones, bboxlist):
        if logging == 1:
            tobj.logcon ("==============HL2_HITBOXSET==============")
            tobj.logcon ("Offset at start: " + str(file.tell()))

        binary_format="<3i" # data_read_in = 3i = 3*4 = 12
        data_read_in = 12   # Total binary_format byte value above, used below to set the file offset pointer back.
        temp_data = file.read(struct.calcsize(binary_format))
        data = struct.unpack(binary_format, temp_data)
        self.sznameindex = data[0]
        self.numhitboxes = data[1]
        self.hitboxindex = data[2]
        SaveCurOffset = file.tell() # Save the file current offset pointer.

        if logging == 1:
            tobj.logcon ("sznameindex: " + str(self.sznameindex))
            tobj.logcon ("numhitboxes: " + str(self.numhitboxes))
            tobj.logcon ("hitboxindex: " + str(self.hitboxindex))
            tobj.logcon ("SaveCurOffset: " + str(SaveCurOffset))

        file.seek(SaveCurOffset + self.sznameindex - data_read_in, 0) # change the file offset pointer position.
        binary_format="<c"
        while 1:
            temp_data = file.read(struct.calcsize(binary_format))
            data = struct.unpack(binary_format, temp_data)
            if data[0] == '\x00':
                break
            self.pszName = self.pszName + data[0]
        if logging == 1:
            tobj.logcon ("pszName: " + self.pszName)

        # Makes QuArK bbox group folder.
        bbg_name = file.name.split("\\")
        folder = bbg_name[len(bbg_name)-2]
        file_name = bbg_name[len(bbg_name)-1]
        file_name = file_name.split(".")[0]
        bbg_name = folder + "_" + file_name
        self.bboxgroup = quarkx.newobj("BBoxes " + bbg_name + "_" + self.pszName + ":bbg")
        self.bboxgroup['show'] = (1.0,)

        file.seek(SaveCurOffset - data_read_in + self.hitboxindex, 0) # change the file offset pointer position to get the bboxes.
        for count in xrange(self.numhitboxes):
            bbox = mdl_hitbox()
            bbox.load(file, self.bboxgroup, count, QuArK_bones, bboxlist)

        file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.
        if logging == 1:
            tobj.logcon ("------------------------")
            tobj.logcon ("Offset at end: " + str(file.tell()))
            tobj.logcon ("========================")
            tobj.logcon ("")


class Quaternion48:
    x = 0    #item   0    unsigned short
    y = 0    #item   1    unsigned short
    z = 0    #item   2    unsigned short (also contains 1 bit for w-neg (highest bit))
    wneg = 0 #item   2    (see above)
    binary_format="<3H"  #little-endian (<), see #item descriptions above.
    qx = 0.0
    qy = 0.0
    qz = 0.0
    qw = 0.0

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.wneg = 0
        self.binary_format="<3H"
        self.qx = 0.0
        self.qy = 0.0
        self.qz = 0.0
        self.qw = 0.0

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.x = data[0]
        self.y = data[1]
        self.z = data[2]
        self.wneg = (self.z >> 15)
        self.z = self.z & 0x8000 #Cut off the wneg bit
    
        self.qx = (self.x - 32768) * (1 / 32768.0)
        self.qy = (self.y - 32768) * (1 / 32768.0)
        self.qz = (self.z - 16384) * (1 / 16384.0)
        self.qw = 1.0 - self.qx * self.qx - self.qy * self.qy - self.qz * self.qz
        if self.qw < 0:
            self.qw = 0.0
        else:
            self.qw = math.sqrt(self.qw)
        if (self.wneg):
            self.qw = -self.qw

class Vector48:
    #Header Structure   #item of file, type, description.
    x = 0.0    #item   0    float
    y = 0.0    #item   1    float
    z = 0.0    #item   2    float
    binary_format="<3f"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.binary_format="<3f"

    def load(self, file):
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.x = data[0]
        self.y = data[1]
        self.z = data[2]


####################################
# Starts By Using the Model Object
####################################
class mdl_obj(object):
    #Header Structure            #item of file, type, description.
    ident = ""                   #item   0      4s.
    version = 0                  #item   1      int.
    checksum = 0                 #item   2      int.this has to be the same in the phy and vtx files to load!
    name = ""                    #item   3      64s.
    length = 0                   #item   4      int.
    eyeposition = [0.0]*3        #item   5-7    3 floats, ideal eye position.
    illumposition = [0.0]*3      #item   8-10   3 floats, illumination center.
    hull_min = [0.0]*3           #item   11-13  3 floats, ideal movement hull size.
    hull_max = [0.0]*3           #item   14-16  3 floats.
    view_bbmin = [0.0]*3         #item   17-19  3 floats, clipping bounding box.
    view_bbmax = [0.0]*3         #item   20-22  3 floats.
    flags = 0                    #item   23     int.
    numbones = 0                 #item   24     int.
    boneindex = 0                #item   25     int.
    numbonecontrollers = 0       #item   26     int, bone controllers
    bonecontrollerindex = 0      #item   27     int.
    numhitboxsets = 0            #item   28     int.
    hitboxsetindex = 0           #item   29     int.
    numlocalanim = 0             #item   30     int, animations/poses.
    localanimindex = 0           #item   31     int, animation descriptions.
    numlocalseq = 0              #item   32     int, sequences
    localseqindex = 0            #item   33     int.
    activitylistversion = 0      #item   34     int, initialization flag - have the sequences been indexed?
    eventsindexed = 0            #item   35     int.
    numtextures = 0              #item   36     int.
    textureindex = 0             #item   37     int.
    numcdtextures = 0            #item   38     int.
    cdtextureindex = 0           #item   39     int.
    numskinref = 0               #item   40     int.
    numskinfamilies = 0          #item   41     int.
    skinindex = 0                #item   42     int.
    num_bodyparts = 0            #item   43     int.
    bodypartindex = 0            #item   44     int.
    numlocalattachments = 0      #item   45     int.
    localattachmentindex = 0     #item   46     int.
    numlocalnodes = 0            #item   47     int.
    localnodeindex = 0           #item   48     int.
    localnodenameindex = 0       #item   49     int.
    numflexdesc = 0              #item   50     int.
    flexdescindex = 0            #item   51     int.
    numflexcontrollers = 0       #item   52     int.
    flexcontrollerindex = 0      #item   53     int.
    numflexrules = 0             #item   54     int.
    flexruleindex = 0            #item   55     int.
    numikchains = 0              #item   56     int.
    ikchainindex = 0             #item   57     int.
    nummouths = 0                #item   58     int.
    mouthindex = 0               #item   59     int.
    numlocalposeparameters = 0   #item   60     int.
    localposeparamindex = 0      #item   61     int.
    surfacepropindex = 0         #item   62     int, think this is the offset for the surface data, triangles.
    keyvalueindex = 0            #item   63     int.
    keyvaluesize = 0             #item   64     int.
    numlocalikautoplaylocks = 0  #item   65     int.
    localikautoplaylockindex = 0 #item   66     int.
    mass = 0.0                   #item   67     float.
    contents = 0                 #item   68     int.
    numincludemodels = 0         #item   69     int.
    includemodelindex = 0        #item   70     int.
    virtualModel = 0             #item   71     int.
    szanimblocknameindex = 0     #item   72     int.
    numanimblocks = 0            #item   73     int.
    animblockindex = 0           #item   74     int.
    animblockModel = 0           #item   75     int.
    bonetablebynameindex = 0     #item   76     int.
    pVertexBase = 0              #item   77     int.
    pIndexBase = 0               #item   78     int.
    rootLOD = 0                  #item   79     byte.
    unused1 = 0                  #item   80     byte.
    unused2 = 0                  #item   81     byte.
    zeroframecacheindex = 0      #item   82     int.
    array1 = 0                   #item   83     int.
    array2 = 0                   #item   84     int.
    array3 = 0                   #item   85     int.
    array4 = 0                   #item   86     int.
    array5 = 0                   #item   87     int.
    array6 = 0                   #item   88     int.

    binaryFormat = ("<4sii%dsi3f3f3f3f3f3f44if11i3B7i" % (MAX_QPATH))  # little-endian (<).

    hitboxsets = []
    keys = []
    tags = []
    surfaces = []
    ikchains = []
    origin = quarkx.vect(0.0, 0.0, 0.0)

    #mdl data objects
    bones = []
    QuArKBonesData = []
    skins_group = []
    materials_group = []
    demand_seq_groups = []
    anim_blocks = []
    bone_controls = []
    animation_descs = []
    sequence_descs = []
    attachments = {}
    bodyparts = []

    tex_coords = []
    faces = []
    vertices = []
    tagsgroup = []
    num_anim = 0
    main_mdl_comps = []
    main_mdl_bones = []
    bones_names = []
    new_mdl_comps = []

    def __init__(self):
        self.ident = 0
        self.version = 0
        self.checksum = 0 # this has to be the same in the phy and vtx files to load!
        self.name = ""
        self.length = 0
        self.eyeposition = [0.0,0.0,0.0] # ideal eye position
        self.illumposition = [0.0,0.0,0.0] # illumination center
        self.hull_min = [0.0,0.0,0.0] # ideal movement hull size
        self.hull_max = [0.0,0.0,0.0]
        self.view_bbmin = [0.0,0.0,0.0] # clipping bounding box
        self.view_bbmax = [0.0,0.0,0.0]
        self.flags = 0
        self.numbones = 0 # bones
        self.boneindex = 0
        self.numbonecontrollers = 0 # bone controllers
        self.bonecontrollerindex = 0
        self.numhitboxsets = 0
        self.hitboxsetindex = 0
        # file local animations? and sequences
        self.numlocalanim = 0 # animations/poses
        self.localanimindex = 0 # animation descriptions
        self.numlocalseq = 0 # sequences
        self.localseqindex = 0
        self.activitylistversion = 0 # initialization flag - have the sequences been indexed?
        self.eventsindexed = 0
        # raw textures
        self.numtextures = 0
        self.textureindex = 0
        # raw textures search paths
        self.numcdtextures = 0
        self.cdtextureindex = 0
        # replaceable textures tables
        self.numskinref = 0
        self.numskinfamilies = 0
        self.skinindex = 0
        self.num_bodyparts = 0
        self.bodypartindex = 0
        # queryable attachable points
        self.numlocalattachments = 0
        self.localattachmentindex = 0
        # animation node to animation node transition graph
        self.numlocalnodes = 0
        self.localnodeindex = 0
        self.localnodenameindex = 0
        self.numflexdesc = 0
        self.flexdescindex = 0
        self.numflexcontrollers = 0
        self.flexcontrollerindex = 0
        self.numflexrules = 0
        self.flexruleindex = 0
        self.numikchains = 0
        self.ikchainindex = 0
        self.nummouths = 0
        self.mouthindex = 0
        self.numlocalposeparameters = 0
        self.localposeparamindex = 0
        self.surfacepropindex = 0 # think this is the offset for the surface data, triangles.
        # Key values
        self.keyvalueindex = 0
        self.keyvaluesize = 0
        self.numlocalikautoplaylocks = 0
        self.localikautoplaylockindex = 0
        # The collision model mass that jay wanted
        self.mass = 0.0
        self.contents = 0
        # external animations, models, etc.
        self.numincludemodels = 0
        self.includemodelindex = 0
        # implementation specific back pointer to virtual data
        self.virtualModel = 0
        # for demand loaded animation blocks
        self.szanimblocknameindex = 0
        self.numanimblocks = 0
        self.animblockindex = 0
        self.animblockModel = 0
        self.bonetablebynameindex = 0
        # used by tools only that don't cache, but persist mdl's peer data
        # engine uses virtualModel to back link to cache pointers
        self.pVertexBase = 0
        self.pIndexBase = 0
        self.rootLOD = 0
        self.unused1 = 0
        self.unused2 = 0
        self.zeroframecacheindex = 0
        self.array1 = 0
        self.array2 = 0
        self.array3 = 0
        self.array4 = 0
        self.array5 = 0
        self.array6 = 0

        self.hitboxsets = []        # A list of QuArK :bbg bbox groups with QuArK :p hitbox polys.
        self.keys = []
        self.tags = []
        self.surfaces = []
        self.ikchains = []
        self.origin = quarkx.vect(0.0, 0.0, 0.0)
        self.bones = []             # A list of the bones being read in from the file, if any.
        self.QuArKBonesData = []    # A list matching above with [[OurFullName, vtxlist as {dictionary}],...]
        self.skins_group = []       # A list of the .vtf skin files full paths and names.
        self.materials_group = []   # A list of the .vmt material files full paths and names to go with skins above.
        self.demand_seq_groups = [] # A list of the demand sequence groups.
        self.anim_blocks = []       # A list of the animation blocks.
        self.bone_controls = []     # A list of the bone controllers.
        self.animation_descs = []   # A list of the animation descriptions (leads into grouped frames).

    #### SEE OTHER HL IMPORTER USE THIS AS WORD SEARCH
        self.sequence_descs = []    # A list of the sequence descriptions (in the file but never gets used??? uses animation_descs above instead!!!).
        self.attachments = {}       # A dictionary list of  attachments, the key being the bone number it is attached to.
        self.bodyparts = []         # A list of the bodyparts.

        self.tex_coords = []        # A list of integers, 1 for "onseam" and 2 for the s,t or u,v texture coordinates.
        self.faces = []             # A list of the triangles.
        self.vertices = []          # A list of the vertexes.
        self.tagsgroup = []         # A list of tag (attachment) groups to store tag frames into for each tag.
        self.num_anim = 0           # We half to set this because the MORONS at VALVE can't do it.
        self.main_mdl_comps = []    # A list of main model components already loaded into QuArK.
        self.main_mdl_bones = []    # A list of main model components bones already loaded into QuArK.
        self.bones_names = []       # A conversion list of self.main_mdl_bones name converted to importer self.bone names.
        self.new_mdl_comps = []     # A list of main model components updated copies in the main_mdl_comps list above.


    def load(self, file, editor, folder_name, mdl_name, message):
        global progressbar, SpecsList
        SpecsList = """ """
        # file = the actual .mdl model file being read in, imported.
        # folder_name = name of the folder the .mdl model file is in.
        # mdl_name = just the basic name of the .mdl file, ex: barney
        # message = "" and empty string to add needed messages to.
        folder_name = folder_name.lower() # Make sure all text is lower case.
        tmpData = file.read(struct.calcsize(self.binaryFormat))
        data = struct.unpack(self.binaryFormat, tmpData)
        possible_files = ["_animations.mdl", "_animations.ani", "_anims.mdl", "_anims.ani", "_gestures.mdl", "_gestures.ani", "_postures.mdl", "_postures.ani"]

        self.ident = data[0]
        self.version = data[1]
        self.checksum = data[2] # this has to be the same in the phy and vtx files to load!
        self.name = asciiz(data[3])

        # Check for correct file versions.
        if self.version != 44 and self.version != 49:
            return file, None, None, None, message, None, self.version, self.main_mdl_comps, self.new_mdl_comps, None, None, None, None

        # Check if Main .mdl file or not and set our flag 'main_mdl_file' to use in loading the file.
        file_name = self.name.lower() # Make sure all text is lower case.
        main_mdl_file = 1
        main_mdl_name = None
        self.ani_file = None
        for i in range(len(possible_files)):
            if file_name.find(possible_files[i]) != -1:
                main_mdl_file = None
                ani_file_name = file_name.replace(".mdl", ".ani")
                # If related .ani for .mdl file exist, open it for data read in later.
                if os.path.isfile(ani_file_name):
                    main_mdl_name = file_name.split(possible_files[i])[0]
                    full_main_mdl_name = folder_name + "_" + main_mdl_name # + "_" + main_mdl_name
                    for item in editor.Root.subitems:
                        if item.type == ":mc":
                            name = item.shortname.lower() # Make sure all text is lower case.
                            if name.startswith(full_main_mdl_name + "_" + main_mdl_name) or name.startswith(full_main_mdl_name):
                                self.main_mdl_comps = self.main_mdl_comps + [item]
                    if len(self.main_mdl_comps) == 0:
                        quarkx.msgbox("Main Half-Life 2 .mdl model\nfor this animation .mdl file not loaded.\n\nImport the main file first\nthen reload this .mdl file:\n\n" + file_name, quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                        return file, None, None, None, message, None, None, self.main_mdl_comps, self.new_mdl_comps, None, None, None, None
                    self.ani_file = os.getcwd() + "/" + ani_file_name
                    self.ani_file = open(self.ani_file, "rb")
                    break
                else:
                    return file, None, None, None, message, None, self.version, self.main_mdl_comps, self.new_mdl_comps, None, None, None, None
        if main_mdl_file is not None:
            ## Check for and load the .vvd vertex and weights data file for model being imported.
            vvd_file, VVDFileReader = HL2_GetVertexData(mdl_name)
            ## Check for and load the .vtx triangle Tris data file for model being imported.
            vtx_file = HL2_GetTriangleData(mdl_name)
            if vvd_file is None or vtx_file is None:
                return file, None, None, None, message, None, self.version, self.main_mdl_comps, self.new_mdl_comps, None, None, None, None

        self.length = data[4]
        self.eyeposition = [data[5], data[6], data[7]] # ideal eye position
        self.illumposition = [data[8], data[9], data[10]] # illumination center
        self.hull_min = [data[11], data[12], data[13]] # ideal movement hull size
        self.hull_max = [data[14], data[15], data[16]]
        self.view_bbmin = [data[17], data[18], data[19]] # clipping bounding box
        self.view_bbmax = [data[20], data[21], data[22]]
        self.flags = data[23]
        self.numbones = data[24] # bones
        self.boneindex = data[25]
        self.numbonecontrollers = data[26] # bone controllers
        self.bonecontrollerindex = data[27]
        self.numhitboxsets = data[28]
        self.hitboxsetindex = data[29]
        # file local animations? and sequences
        self.numlocalanim = data[30] # animations/poses
        self.localanimindex = data[31] # animation descriptions
        self.numlocalseq = data[32] # sequences
        self.localseqindex = data[33]
        self.activitylistversion = data[34] # initialization flag - have the sequences been indexed?
        self.eventsindexed = data[35]
        # raw textures
        self.numtextures = data[36]
        self.textureindex = data[37]
        # raw textures search paths
        self.numcdtextures = data[38]
        self.cdtextureindex = data[39]
        # replaceable textures tables
        self.numskinref = data[40]
        self.numskinfamilies = data[41]
        self.skinindex = data[42]
        self.num_bodyparts = data[43]
        self.bodypartindex = data[44]
        # queryable attachable points
        self.numlocalattachments = data[45]
        self.localattachmentindex = data[46]
        # animation node to animation node transition graph
        self.numlocalnodes = data[47]
        self.localnodeindex = data[48]
        self.localnodenameindex = data[49]
        self.numflexdesc = data[50]
        self.flexdescindex = data[51]
        self.numflexcontrollers = data[52]
        self.flexcontrollerindex = data[53]
        self.numflexrules = data[54]
        self.flexruleindex = data[55]
        self.numikchains = data[56]
        self.ikchainindex = data[57]
        self.nummouths = data[58]
        self.mouthindex = data[59]
        self.numlocalposeparameters = data[60]
        self.localposeparamindex = data[61]
        self.surfacepropindex = data[62]
        # Key values
        self.keyvalueindex = data[63]
        self.keyvaluesize = data[64]
        self.numlocalikautoplaylocks = data[65]
        self.localikautoplaylockindex = data[66]
        # The collision model mass that jay wanted
        self.mass = data[67]
        self.contents = data[68]
        # external animations, models, etc.
        self.numincludemodels = data[69]
        self.includemodelindex = data[70]
        # implementation specific back pointer to virtual data
        self.virtualModel = data[71]
        # for demand loaded animation blocks
        self.szanimblocknameindex = data[72]
        self.numanimblocks = data[73]
        self.animblockindex = data[74]
        self.animblockModel = data[75]
        self.bonetablebynameindex = data[76]
        # used by tools only that don't cache, but persist mdl's peer data
        # engine uses virtualModel to back link to cache pointers
        self.pVertexBase = data[77]
        self.pIndexBase = data[78]
        self.rootLOD = data[79]
        self.unused1 = data[80]
        self.unused2 = data[81]
        self.zeroframecacheindex = data[82]
        self.array1 = data[83]
        self.array2 = data[84]
        self.array3 = data[85]
        self.array4 = data[86]
        self.array5 = data[87]
        self.array6 = data[88]

        if self.numlocalanim < self.numlocalseq:
            self.num_anim = self.numlocalanim
        else:
            self.num_anim = self.numlocalseq
        # where are we in the file (for calculating real offsets)
        ofsBegin = file.tell()
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Data Size in bytes: " + str(ofsBegin))
            tobj.logcon ("#####################################################################")

        ## To get bonetablebynameindex BYTE?
        SaveCurOffset = file.tell() # Save the file current offset pointer.
        file.seek(SaveCurOffset + self.bonetablebynameindex, 0)
        binaryFormat="<B"
        tmpData = file.read(struct.calcsize(binaryFormat))
        data = struct.unpack(binaryFormat, tmpData)
        if logging == 1:
            tobj.logcon ("bonetablebynameindex: " + str(data))
        # Just get garbage from file read below? Have DAN check this out.
    #    bonetablebyname = data[0]
    #    file.seek(SaveCurOffset + bonetablebyname, 0)
    #    binaryFormat="<64s"
    #    for i in xrange(self.numbones):
    #        tmpData = file.read(struct.calcsize(binaryFormat))
    #        data = struct.unpack(binaryFormat, tmpData)
    #        print "line 3139 bonetablebyname", data

        ## Load the bones data.
        file.seek(self.boneindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numbones: " + str(self.numbones))
        for i in xrange(self.numbones):
            bone = mdl_bone()
            bone.bone_index = i
            bone.load(file)
            if logging == 1:
                tobj.logcon ("----------------------------")
                tobj.logcon ("mdl_bone data index: " + str(i))
            self.bones.append(bone)
            self.QuArKBonesData = self.QuArKBonesData + [[folder_name + '_' + mdl_name + '_' + bone.pszName + ':bone', {}]]

        ## Load the bone controllers data.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numbonecontrollers: " + str(self.numbonecontrollers))
        file.seek(self.bonecontrollerindex, 0)
        for i in xrange(self.numbonecontrollers):
            bone_controller = mdl_bone_control()
            bone_controller.load(file)
            self.bone_controls.append(bone_controller)


        ## Load the animblocks.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numanimblocks: " + str(self.numanimblocks))
        file.seek(self.animblockindex, 0)
        for i in xrange(self.numanimblocks):
            anim_block = HL2_AnimBlock()
            anim_block.load(file)
            #Please note: Block 0 is invalid, so the first AnimBlock is filled with rubbish numbers!
            if logging == 1:
                tobj.logcon ("========================")
                tobj.logcon ("HL2_AnimBlock data index: " + str(i))
                tobj.logcon ("anim_block.datastart: " + str(anim_block.datastart))
                tobj.logcon ("anim_block.dataend: " + str(anim_block.dataend))
                tobj.logcon ("----------------------------")
            self.anim_blocks.append(anim_block)

        ## Load the file local animations.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numlocalanim: " + str(self.numlocalanim))
        file.seek(self.localanimindex, 0)
        total_frames = 0
        if main_mdl_name is not None:
            self.SRCsList = []
            temp = """ """
        for i in xrange(self.numlocalanim):
            local_animation_desc = mdl_sequence_desc()
            local_animation_desc.load(file, self.ani_file, self)
            if logging == 1:
                tobj.logcon ("========================")
                tobj.logcon ("mdl_sequence_desc data index: " + str(i))
                tobj.logcon ("pszName: " + local_animation_desc.pszName)
                tobj.logcon ("numframes: " + str(local_animation_desc.numframes))
                tobj.logcon ("----------------------------")
            if main_mdl_name is not None:
                name = local_animation_desc.pszName.replace("@", "")
                frames = local_animation_desc.numframes
                self.SRCsList = self.SRCsList + [name]
                temp = temp + name + """: = {Txt = """
                temp = temp + '"' + name + ' / ' + str(frames) + '"'
                temp = temp + """Typ = "X" Hint = "Check this box to import these frames."}"""
                total_frames = total_frames + frames
            self.animation_descs.append(local_animation_desc)
        if main_mdl_name is not None:
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("total_frames: " + str(total_frames))
            SpecsList = SpecsList + """sep: = { Typ="S" Txt="Sequence / nbr of frames"}"""
            SpecsList = SpecsList + """all: = {Txt = """
            SpecsList = SpecsList + '"Import All / ' + str(total_frames) + '"'
            SpecsList = SpecsList + """Typ = "X" Hint = "Check this box ONLY to import all frames."}"""
            SpecsList = SpecsList + """sep: = { Typ="S" Txt=""}"""
            SpecsList = SpecsList + temp

        ## Load the file local sequences.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numlocalseq: " + str(self.numlocalseq))
        file.seek(self.localseqindex, 0)
        for i in xrange(self.numlocalseq):
            local_sequence_desc = HL2_LocalSeqDesc()
            local_sequence_desc.load(file)
            self.sequence_descs.append(local_sequence_desc)
            if logging == 1:
                tobj.logcon ("========================")
                tobj.logcon ("HL2_LocalSeqDesc data index: " + str(i))


        ## Setup items needed for QuArK.
        ComponentList = []
        message = ""


        ## Load the file textures info data.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("=====file textures=====")
        file.seek(self.textureindex, 0)
        skin_names = []
        for i in xrange(self.numtextures):
            textures_info = HL2_TexturesInfo()
            textures_info.load(file)
            skin_name = textures_info.pszName.lower() # Make sure all text is lower case.
            skin_flags = str(textures_info.flags) # Keep each skin textures flags setting with its skin.
            skin_names.append([skin_name, skin_flags])
            if logging == 1:
                tobj.logcon ("========================")
                tobj.logcon ("HL2_TexturesInfo data index: " + str(i))
        self.skins_group, self.materials_group = LookForSkins(skin_names, self.skins_group, self.materials_group, folder_name, mdl_name, message)


        ## Load the bodyparts data.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("num_bodyparts: " + str(self.num_bodyparts))
        file.seek(self.bodypartindex, 0)
        for i in xrange(self.num_bodyparts):
            body_part_index = mdl_bodypart()
            body_part_index.load(file)
            self.bodyparts.append(body_part_index)
            if logging == 1:
                tobj.logcon ("========================")
                tobj.logcon ("bodypartindex: " + str(self.bodypartindex))

        QuArK_bones = [] # A list to store all QuArK bones created.
        if main_mdl_file is not None:
            # Read in the fix-up table from the vvd file
            vvd_file.seek(VVDFileReader.fixupTableStart)
            VVDFixups = []
            for i in xrange(VVDFileReader.numFixups):
                Fixup = HL2_VVDFixup()
                Fixup.load(vvd_file)
                VVDFixups += [Fixup]


        ## Load the bodyparts models meshes data
            mesh_vertex_count = 0
            for i in xrange(self.num_bodyparts):
                for j in xrange(self.bodyparts[i].nummodels):
                    name = self.bodyparts[i].models[j].pszName
                    name = name.split(".")[0]
                    nummesh = self.bodyparts[i].models[j].nummeshes
                    vvd_file.seek(VVDFileReader.vertexDataStart)
                    if VVDFileReader.numFixups != 0:
                        vertex_weights_TMP = []
                        binary_format="<3f3bB3f3f2f"
                        for l in xrange(VVDFileReader.numLODVertexes[0]):
                            temp_data = vvd_file.read(struct.calcsize(binary_format))
                            data = struct.unpack(binary_format, temp_data)
                            # dict. list [key]= [   [ 3 weight values ]     ,  [ 3 weight bone indexes ] , # of bones, ( vertex position )     ,        ( vertex normal )      , [ vertex UV values ]]
                            vertex_weights_TMP += [([data[0], data[1], data[2]], [data[3], data[4], data[5]], data[6], (data[7], data[8], data[9]), (data[10], data[11], data[12]), [data[13], data[14]])]

                          #  if logging == 1:
                          #      print "vertex", l, "data->"
                          #      print "weights->", data[0], data[1], data[2]
                          #      print "w-bones->", data[3], data[4], data[5]
                          #      print "nbr of w-bones->", data[6]
                          #      print "vtx pos->", data[7], data[8], data[9]
                          #      print "vtx nor->", data[10], data[11], data[12]
                          #      print "vtx UV->", data[13], data[14]
                          #      print "--------------------------------------"

                        #Apply fixups
                        vertex_weights = []
                        for l in xrange(VVDFileReader.numFixups):
                            Fixup = VVDFixups[l]
                            vertex_weights += vertex_weights_TMP[Fixup.sourceVertexID:Fixup.sourceVertexID+Fixup.numVertexes]
                    else:
                        #No fixup required
                        pass


                ## Load the meshes data
                    for k in xrange(nummesh):


                    ## Now we start creating our Import Component and name it.
                        Component = quarkx.newobj(folder_name + '_' + mdl_name + '_' + name + ' ' + str(k) + ':mc')
                        sdogroup = quarkx.newobj('SDO:sdo')
                        # Create the "Skins:sg" group.
                        try:
                            skinref = self.bodyparts[i].models[j].meshes[k].skinref
                            skinsize = (self.skins_group[skinref].width, self.skins_group[skinref].height)
                        except:
                            skinsize = (256, 256)
                        skingroup = quarkx.newobj('Skins:sg')
                        skingroup['type'] = chr(2)
                        # Create the "Frames:fg" group.
                        framesgroup = quarkx.newobj('Frames:fg')
                        framesgroup['type'] = chr(1)

                        # Create an empty dummy baseframe & comp Tris for now while getting this importer working.
                        Tris = ''
                        Component['Tris'] = Tris
                        frame = quarkx.newobj('baseframe:mf')
                        frame['Vertices'] = ''
                        framesgroup.appenditem(frame)

                        Component['skinsize'] = skinsize
                        Component['show'] = chr(1)
                        Component.appenditem(sdogroup)
                        Component.appenditem(skingroup)
                        Component.appenditem(framesgroup)

                    ## Add bone controls if any.
                        for control in self.bone_controls:
                            bone = self.bones[control.bone]
                            Component['bone_control_'+ str(control.inputfield)] = self.QuArKBonesData[control.bone][0]
                        ComponentList = ComponentList + [Component]

                        mesh = self.bodyparts[i].models[j].meshes[k]
                        if VVDFileReader.numFixups == 0:
                            vertex_weights = mesh.vertex_weights
                            binary_format="<3f3bB3f3f2f"
                            if logging == 1:
                                tobj.logcon ("======================================")
                                tobj.logcon ("HL2import mdl_mesh")
                                tobj.logcon ("mesh-> meshid, numvertices, vertexoffset, VVDFileReader-> vertexDataStart")
                                tobj.logcon ("         " + str(mesh.meshid) + "        " + str(mesh.numvertices) + "         " + str(mesh.vertexoffset) + "             " + str(VVDFileReader.vertexDataStart))
                                tobj.logcon ("======================================")
                            for l in xrange(mesh.numvertices):
                                temp_data = vvd_file.read(struct.calcsize(binary_format))
                                data = struct.unpack(binary_format, temp_data)
                                # dict. list [key]= [   [ 3 weight values ]     ,  [ 3 weight bone indexes ] , # of bones, ( vertex position )     ,        ( vertex normal )      , [ vertex UV values ]]
                                vertex_weights.append([[data[0], data[1], data[2]], [data[3], data[4], data[5]], data[6], (data[7], data[8], data[9]), (data[10], data[11], data[12]), [data[13], data[14]]])

                                if logging == 1:
                                    tobj.logcon ("vertex" + str(l) + "data:")
                                    tobj.logcon ("weights: " + str(data[0]) + str(data[1]) + str(data[2]))
                                    tobj.logcon ("w-bones: " + str(data[3]) + str(data[4]) + str(data[5]))
                                    tobj.logcon ("nbr of w-bones: " + str(data[6]))
                                    tobj.logcon ("vtx pos: " + str(data[7]) + str(data[8]) + str(data[9]))
                                    tobj.logcon ("vtx nor: " + str(data[10]) + str(data[11]) + str(data[12]))
                                    tobj.logcon ("vtx UV: " + str(data[13]) + str(data[14]))
                                    tobj.logcon ("--------------------------------------")
                        else:
                            mesh_weights = []
                            for vtx in xrange(mesh_vertex_count, mesh.numvertices+mesh_vertex_count):
                                mesh_weights.append(vertex_weights[vtx])
                            mesh_vertex_count = mesh_vertex_count + mesh.numvertices
                            mesh.vertex_weights = mesh_weights


            ## Load the vtx file data and send the Components to make the rest of the meshes.
            if len(self.bones) != 0 and len(ComponentList) != 0:
                VTX = HL2_VTXFileReader()
                ComponentList = VTX.load(vtx_file, self, vvd_file, ComponentList)
                if logging == 1:
                    tobj.logcon ("")
                    tobj.logcon ("========================")
                    tobj.logcon ("vtx_file: " + str(vtx_file))
                    tobj.logcon ("========================")
                    tobj.logcon ("--------- HL2_VTXFileReader ---------")


            ## Load the attachments data, for position processing with bones they belong to.
            if len(self.bones) != 0 and len(ComponentList) != 0 and self.numlocalattachments != 0:
                if logging == 1:
                    tobj.logcon ("")
                    tobj.logcon ("========================")
                    tobj.logcon ("     attachments data")
                    tobj.logcon ("------------------------")
                file.seek(self.localattachmentindex, 0)
                tag_comp = ComponentList[0] # Reset this if needed later.
                for i in xrange(self.numlocalattachments):
                    attachment = mdl_attachment()
                    attachment.load(file)
                    if not self.attachments.has_key(attachment.localbone):
                        self.attachments[attachment.localbone] = {}
                        self.attachments[attachment.localbone]['bone_name'] = self.QuArKBonesData[attachment.localbone][0]
                        self.attachments[attachment.localbone]['tag_pos'] = {}
                    local = attachment.local
                    org = [local[0][3], local[1][3], local[2][3]]
                    self.attachments[attachment.localbone]['tag_pos'][i] = org


                ## Create tags (attachments) groups if any. We need to keep these separate for each complete model loaded.
                    tag_name = 'tag_' + attachment.pszName
                    newtag = quarkx.newobj(folder_name + '_' + mdl_name + '_' + tag_name + ':tag')
                    newtag['Component'] = tag_comp.name
                    newtag['bone'] = self.attachments[attachment.localbone]['bone_name']
                    self.tagsgroup = self.tagsgroup + [newtag]
                    if i == 0:
                        tag_comp['Tags'] = tag_name
                    else:
                        tag_comp['Tags'] = tag_comp.dictspec['Tags'] + ", " + tag_name

                    if logging == 1:
                        tobj.logcon ("tag_comp: " + str(tag_comp))
                        tobj.logcon ("Tags: " + str(tag_comp.dictspec['Tags']))

        ## Create the bones, if any.
            if len(self.bones) != 0 and len(ComponentList) != 0:
                for mdlbone in xrange(len(self.bones)):
                    bone = self.bones[mdlbone]
                    new_bone = quarkx.newobj(self.QuArKBonesData[mdlbone][0])
                    new_bone['type'] = 'HL2' # Set our bone type.
                    new_bone['flags'] = (0,0,0,0,0,0)
                    new_bone['show'] = (1.0,)
                    bone_pos = quarkx.vect(bone.pos[0], bone.pos[1], bone.pos[2])
                    quat = EulerAngle2Quaternion([bone.rot[0], bone.rot[1], bone.rot[2]])
                #    quat = [bone.quat[0], bone.quat[1], bone.quat[2], bone.quat[3]]
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

                    if self.numlocalattachments != 0 and self.attachments.has_key(mdlbone):
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
                            self.tagsgroup[tag].appenditem(tagframe)

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
                    new_bone['draw_offset'] = (0.0, 0.0, 0.0)
                    new_bone['_color'] = MapColor("BoneHandles", 3)
                    vtxlist = self.QuArKBonesData[mdlbone][1]
                    new_bone.vtxlist = vtxlist
                    keys = vtxlist.keys()
                    vtx_pos = {}
                    use_key = ComponentList[0].name
                    if len(keys) != 0:
                        key = keys[0]
                        vtx_count = len(vtxlist[key])
                        vtx_pos = {key: vtxlist[key]}
                        use_key = key
                    for key in keys:
                        if len(vtxlist[key]) > vtx_count:
                            vtx_pos = {key: vtxlist[key]}
                            use_key = key
                    new_bone.vtx_pos = vtx_pos
                    new_bone['component'] = use_key
                    new_bone['scale'] = (1.0,) # Written this way to store it as a tuple.
                    new_bone['org_scale'] = new_bone.dictspec['scale']
                    # Add bone control if any.
                    for control in self.bone_controls:
                        if control.bone == mdlbone:
                            new_bone['control_type'] = str(control.type)
                            new_bone['control_start'] = str(control.start)
                            new_bone['control_end'] = str(control.end)
                            new_bone['control_rest'] = str(control.rest)
                            new_bone['control_index'] = str(control.inputfield)
                    QuArK_bones = QuArK_bones + [new_bone]

                    # Sets up the 'bonelist' entry of editor.ModelComponentList for the 'baseframe' of all importing bones
                    bonedata = {}
                    bonedata['frames'] = {}
                    bonedata['frames']['baseframe:mf'] = {}
                    bonedata['frames']['baseframe:mf']['position'] = new_bone.dictspec['position']
                    bonedata['frames']['baseframe:mf']['rotmatrix'] = new_bone.rotmatrix.tuple
                    editor.ModelComponentList['bonelist'][new_bone.name] = bonedata

            # int     RemapSeqBone( int iSequence, int iLocalBone ) const;    // maps local sequence bone to global bone
            # int     RemapAnimBone( int iAnim, int iLocalBone ) const;       // maps local animations bone to global bone

            ## Load the hitboxes data, can only have one per bone and visa versa.
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("========================")
                tobj.logcon ("numhitboxsets: " + str(self.numhitboxsets))
            file.seek(self.hitboxsetindex, 0)
            bboxlist = editor.ModelComponentList['bboxlist']
            for i in xrange(self.numhitboxsets):
                hitboxset = HL2_HitBoxSet()
                hitboxset.load(file, QuArK_bones, bboxlist)
                self.hitboxsets.append(hitboxset.bboxgroup)

        ## Test to try and get nodes data
        if self.numlocalnodes != 0:
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("========================")
                tobj.logcon ("numlocalnodes: " + str(self.numlocalnodes))
            file.seek(self.localnodenameindex, 0)
            NodeName = ""
            binary_format="<c"
            while 1:
                temp_data = file.read(struct.calcsize(binary_format))
                data = struct.unpack(binary_format, temp_data)
                if data[0] == '\x00':
                    break
                NodeName = NodeName + data[0]
            if logging == 1:
                tobj.logcon ("------------------------")
                tobj.logcon ("NodeName: " + str(NodeName))
                tobj.logcon ("------------------------")
            file.seek(self.localnodeindex, 0)
            for i in xrange(self.numlocalnodes):
                node = HL2_Node()
                node.load(file)

        ## Load the flex desc data.
        file.seek(self.flexdescindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numflexdesc: " + str(self.numflexdesc))
        for i in xrange(self.numflexdesc):
            flex_desc = HL2_FlexDesc()
            flex_desc.load(file)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_FlexDesc ----------------")

        ## Load the flex controller data.
        file.seek(self.flexcontrollerindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numflexcontrollers: " + str(self.numflexcontrollers))
        for i in xrange(self.numflexcontrollers):
            flex_cont = HL2_FlexController()
            flex_cont.load(file)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_FlexController ----------------")

        ## Load the flex rules data.
        file.seek(self.flexruleindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numflexrules: " + str(self.numflexrules))
        for i in xrange(self.numflexrules):
            flex_rule = HL2_FlexRule()
            flex_rule.load(file)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_FlexRule ----------------")

        ## Load the ikchains data.
        file.seek(self.ikchainindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numikchains: " + str(self.numikchains))
        for i in xrange(self.numikchains):
            IKChain = HL2_IKChain()
            IKChain.load(file)
            self.ikchains.append(IKChain)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_IKChain ----------------")

        ## Load the mouths data.
        file.seek(self.mouthindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("nummouths: " + str(self.nummouths))
        for i in xrange(self.nummouths):
            mouth = HL2_Mouth()
            mouth.load(file)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_Mouth ----------------")

        ## Load the local pose parameters data.
        file.seek(self.localposeparamindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("numlocalposeparameters: " + str(self.numlocalposeparameters))
        for i in xrange(self.numlocalposeparameters):
            localposeparameter = HL2_LocalPoseParameter()
            localposeparameter.load(file)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_LocalPoseParameter ----------------")

        ## Load the surface prop data.
        file.seek(self.surfacepropindex, 0)
        flex_rule = HL2_SurfaceProp()
        flex_rule.load(file)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("surface prop data")

        ## Load the keyvalues data.
        if self.keyvaluesize != 0:
            file.seek(self.keyvalueindex, 0)
            keyvalues = HL2_KeyValues()
            self.keys.append(keyvalues)
            keyvalues.Load(file, self.keyvaluesize)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("keyvalues data")

        ## Load the local ik autoplay locks data.
        file.seek(self.localikautoplaylockindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("local ik autoplay locks")
        for i in xrange(self.numlocalikautoplaylocks):
            localikautoplaylock = HL2_LocalIKAutoplayLock()
            localikautoplaylock.load(file)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_LocalIKAutoplayLock ----------------")

        ## Load the include models data.
        file.seek(self.includemodelindex, 0)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("========================")
            tobj.logcon ("include models data")
        for i in xrange(self.numincludemodels):
            localikautoplaylock = HL2_ModelGroup()
            localikautoplaylock.load(file)
            if logging == 1:
                tobj.logcon ("--------------" + str(i) + " HL2_ModelGroup ----------------")

        # load the tag info
        file.seek(self.surfacepropindex, 0)
        tagvaluesize = self.length - self.surfacepropindex
        tagvalues = Tags()
        self.tags.append(tagvalues)
        tagvalues.Load(file, tagvaluesize)

        return self, ComponentList, QuArK_bones, message, self.tagsgroup, self.version, self.main_mdl_comps, self.new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name, SpecsList

    # Process animation data
    def load_Animation(self, ComponentList, QuArK_bones, message, file, editor, folder_name, mdl_name, main_mdl_name, LoadAnim):
        global progressbar
        control_name = folder_name + "_" + main_mdl_name + "_"
        ani_file = self.ani_file
        #
        # Get all the moving bones
        #
        tmp_start_bones = [] # A list of 'topmost' bones that belong to the model
        for bone in editor.Root.dictitems['Skeleton:bg'].subitems:
            name = bone.shortname.lower() # Make sure all text is lower case.
            if name.startswith(control_name):
                tmp_start_bones += [bone]

        # Determines if this bone is part of the animation?
        def IsBoneMoving(self, bone, control_name=control_name):
            cont_name = control_name.lower()
            test_name = bone.shortname.lower()
            test_name = test_name.split(cont_name)[1]
            for b in self.bones:
                name = b.pszName.lower()
                if name == test_name:
                    return 1
            return 0

        def CheckBone(self, bone, AutoSelect):
            BoneList = []
            if not AutoSelect:
                if IsBoneMoving(self, bone):
                    # Bone is moving! Auto-select all children, as they need to be re-positioned anyway
                    AutoSelect = 1
            if AutoSelect:
                # If this bone needs to be selected, do that
                BoneList += [bone]
            # Loop over all children bones, and select them if needed
            for ChildBone in bone.subitems:
                if ChildBone.type == ":bone":
                    BoneList += CheckBone(self, ChildBone, AutoSelect)
            return BoneList

        # Now start the work:
        for bone in tmp_start_bones:
            AutoSelect = 0
            self.main_mdl_bones += CheckBone(self, bone, AutoSelect)

        # At this point we can check if control_name matches component or if upper and lower case cause a problem.
        if not self.main_mdl_comps[0].name.startswith(control_name):
            control_name = self.main_mdl_comps[0].name.split("_")
            main_mdl_name = control_name[1]
            control_name = control_name[0] + "_" + control_name[1] + "_"

        # Fill the bone names conversion list.
        for bone in self.main_mdl_bones:
            name = bone.shortname.split(control_name)[1]
            self.bones_names = self.bones_names + [name]
        bones_names_count = len(self.bones_names)
        self_bone_count = len(self.bones)

        #List of all the bones that are NOT moving
        all_bones = editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone')
        bones_not_moving = []
        for bone in all_bones:
            if bone not in self.main_mdl_bones and bone.name.startswith(control_name):
                bones_not_moving += [bone]

        # Find any bones in the animation that were not present in the bones we already got
        for j in xrange(self_bone_count):
            FoundIt = 0
            for i in xrange(bones_names_count):
                if self.bones_names[i] == self.bones[j].pszName:
                    FoundIt = 1
                    break
            if not FoundIt:
                print "Warning: Bone %s found in animation that is not present in main mdl file!" % (self.bones[j].pszName)
                #FIXME: Add these to the model?

        bonelist = editor.ModelComponentList['bonelist']
        def GetParentPosAndRot(ParentName, FrameName):
            ParentName = control_name + ParentName + ":bone"
            if not bonelist.has_key(ParentName):
                #Parent bone not found? Return default values
                return quarkx.vect((0.0, 0.0, 0.0)), quarkx.matrix((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
            if bonelist[ParentName]['frames'].has_key(FrameName):
                parent = bonelist[ParentName]['frames'][FrameName]
            else:
                parent = bonelist[ParentName]['frames']['baseframe:mf']
            return quarkx.vect(parent['position']), quarkx.matrix(parent['rotmatrix'])

        # Add to the editor.ModelComponentList 'bonelist' for the importing animation baseframe.
        for i in xrange(bones_names_count):
            FoundIt = 0
            for j in xrange(self_bone_count):
                if self.bones_names[i] == self.bones[j].pszName:
                    bone = self.bones[j]
                    if bone.flags & BONE_ALWAYS_PROCEDURAL:
                        #Procedural bone; don't move with animation data!
                        break
                    
                    BoneIKChain = 0
                    for ikchain in self.ikchains:
                        for link in ikchain.links:
                            if link.bone == bone.bone_index:
                                BoneIKChain = 1
                                break
                    if BoneIKChain:
                        #Bone moved by IKChain
                        continue
                    
                    #bone_pos = quarkx.vect(bone.pos[0] * bone.posscale[0], bone.pos[1] * bone.posscale[1], bone.pos[2] * bone.posscale[2])
                    #quat = EulerAngle2Quaternion([bone.rot[0] * bone.rotscale[0], bone.rot[1] * bone.rotscale[1], bone.rot[2] * bone.rotscale[2]])
                    bone_pos = quarkx.vect(bone.pos[0], bone.pos[1], bone.pos[2])
                    quat = EulerAngle2Quaternion([bone.rot[0], bone.rot[1], bone.rot[2]])
                    tempmatrix = quaternion2matrix(quat)
                    bone_matrix = quarkx.matrix((tempmatrix[0][0], tempmatrix[0][1], tempmatrix[0][2]), (tempmatrix[1][0], tempmatrix[1][1], tempmatrix[1][2]), (tempmatrix[2][0], tempmatrix[2][1], tempmatrix[2][2]))
                    if bone.parent != -1:
                        parent_bone_name = self.bones[bone.parent].pszName
                        parent_pos, parent_matrix = GetParentPosAndRot(parent_bone_name, "BaseFrame " + mdl_name + ":mf")
                        bone_pos = parent_pos + (parent_matrix * bone_pos)
                        bone_matrix = parent_matrix * bone_matrix
                    bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"] = {}
                    bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"]['position'] = bone_pos.tuple
                    bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"]['rotmatrix'] = bone_matrix.tuple
                    FoundIt = 1
                    break
            if not FoundIt:
                #Bone not in animation; use 'old' position and rotmatrix
                baseframe = bonelist[self.main_mdl_bones[i].name]['frames']['baseframe:mf']
                bone_pos = quarkx.vect(baseframe['position'])
                bone_matrix = quarkx.matrix(baseframe['rotmatrix'])
                if bone.parent != -1:
                    parent_bone_name = self.bones[bone.parent].pszName
                    #First, undo 'old' parent stuff
                    parent_pos, parent_matrix = GetParentPosAndRot(parent_bone_name, 'baseframe:mf')
                    bone_pos = (~parent_matrix) * (bone_pos - parent_pos)
                    bone_matrix = (~parent_matrix) * bone_matrix
                    #Now, apply 'new' parent stuff
                    parent_pos, parent_matrix = GetParentPosAndRot(parent_bone_name, "BaseFrame " + mdl_name + ":mf")
                    bone_pos = parent_pos + (parent_matrix * bone_pos)
                    bone_matrix = parent_matrix * bone_matrix
                bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"] = {}
                bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"]['position'] = bone_pos.tuple
                bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"]['rotmatrix'] = bone_matrix.tuple

        for bone in bones_not_moving:
            #Bone not moving; use 'old' position and rotmatrix
            baseframe = bonelist[bone.name]['frames']['baseframe:mf']
            bone_pos = quarkx.vect(baseframe['position'])
            bone_matrix = quarkx.matrix(baseframe['rotmatrix'])
            #FIXME: Fix this!
            #if bone.parent != -1:
            #    parent_bone_name = self.bones[bone.parent].pszName
            #    #First, undo 'old' parent stuff
            #    parent_pos, parent_matrix = GetParentPosAndRot(parent_bone_name, 'baseframe:mf')
            #    bone_pos = (~parent_matrix) * (bone_pos - parent_pos)
            #    bone_matrix = (~parent_matrix) * bone_matrix
            #    #Now, apply 'new' parent stuff
            #    parent_pos, parent_matrix = GetParentPosAndRot(parent_bone_name, "BaseFrame " + mdl_name + ":mf"
            #    bone_pos = parent_pos + (parent_matrix * bone_pos)
            #    bone_matrix = parent_matrix * bone_matrix
            bonelist[bone.name]['frames']["BaseFrame " + mdl_name + ":mf"] = {}
            bonelist[bone.name]['frames']["BaseFrame " + mdl_name + ":mf"]['position'] = bone_pos.tuple
            bonelist[bone.name]['frames']["BaseFrame " + mdl_name + ":mf"]['rotmatrix'] = bone_matrix.tuple

        # Load the animation data for the frames
        for m_localanim in xrange(self.numlocalanim):
            if not LoadAnim[m_localanim]: continue
            anim = self.animation_descs[m_localanim]
            anim_block = self.anim_blocks[anim.animblock]

            SaveCurOffset = file.tell()
            #Read in the zero frame data first
            file.seek(anim.ThisOffset + self.zeroframecacheindex, 0) # change the file offset pointer position.
            ZeroFrame = {}
            for i in xrange(self.numbones):
                bone = self.bones[i]
                if bone.flags & BONE_HAS_SAVEFRAME_POS:
                    #Read in a Vector48
                    pos = Vector48()
                    pos.load(file)
                    #print "line 1082: pos: ",pos
                    if not ZeroFrame.has_key(i):
                        ZeroFrame[i] = {}
                    ZeroFrame[i]['pos'] = pos #FIXME: Probably want to parse this first!
                if bone.flags & BONE_HAS_SAVEFRAME_ROT:
                    #Read in a Quaterion32, but advance a Quaternion48
                    #rot = Quaterion32()
                    #rot.load(file)
                    #FIXME: advance file by 1 byte...!
                    #print "line 1088: rot: ",rot
                    #if not ZeroFrame.has_key(i):
                    #    ZeroFrame[i] = {}
                    #ZeroFrame[i]['rot'] = rot #FIXME: Probably want to parse this first!
                    pass
            file.seek(SaveCurOffset, 0) # Reset the file offset pointer back to where it should be now.

            if ani_file is not None:
                #Read in the animation data
                ani_file.seek(anim_block.datastart + anim.animindex,0)
                #print "pszName, numframes:", anim.pszName, anim.numframes

                # Read in bone animation data from anim blocks
                all_rot_anim_data = {}
                all_pos_anim_data = {}
                while 1:
                    SaveCurAniOffset = ani_file.tell()
                    StudioAnim = HL2_ANIStudioAnim()
                    StudioAnim.load(ani_file)
                    if StudioAnim.bone == 255:
                        #End of anim block
                        break
                    #print
                    #print "bone:", StudioAnim.bone
                    #print "flags:", StudioAnim.flags
                    #print "nextoffset:", StudioAnim.nextoffset
    
                    rot_anim_data = [None, None, None]
                    pos_anim_data = [None, None, None]
                    if anim.numframes == 1:
                        if (StudioAnim.flags & STUDIO_ANIM_RAWROT):
                            #Read in a Quaternion48
                            rot = Quaternion48()
                            rot.load(ani_file)
                            #print "line 4446: rot:", rot
                            #print rot.qx
                            #print rot.qy
                            #print rot.qz
                            #print rot.qw
                            rot_anim_data = [[rot.qx], [rot.qy], [rot.qz]] #Not storing qw
                        if (StudioAnim.flags & STUDIO_ANIM_RAWPOS):
                            #Read in a Vector48
                            pos = Vector48()
                            pos.load(ani_file)
                            #print "line 4456: pos:", pos
                            #print pos.x
                            #print pos.y
                            #print pos.z
                            pos_anim_data = [[pos.x], [pos.y], [pos.z]]
                    else:
                        AnimValuePtrRot = None
                        AnimValuePtrPos = None
                        if (StudioAnim.flags & STUDIO_ANIM_ANIMROT):
                            SaveCurAniValuePtrRotOffset = ani_file.tell()
                            AnimValuePtrRot = HL2_AnimValuePtr()
                            AnimValuePtrRot.load(ani_file)
                            #print "AnimValuePtr Rot.offset", AnimValuePtrRot.offset
                        if (StudioAnim.flags & STUDIO_ANIM_ANIMPOS):
                            SaveCurAniValuePtrPosOffset = ani_file.tell()
                            AnimValuePtrPos = HL2_AnimValuePtr()
                            AnimValuePtrPos.load(ani_file)
                            #print "AnimValuePtr Pos.offset", AnimValuePtrPos.offset
                        if AnimValuePtrRot is not None:
                            for i in xrange(0, 3): #XR, YR, ZR
                                if AnimValuePtrRot.offset[i] == 0:
                                    #No data
                                    continue
                                rot_anim_data[i] = []
                                ani_file.seek(SaveCurAniValuePtrRotOffset+AnimValuePtrRot.offset[i],0)
                                j = 0
                                while j < anim.numframes:
                                    AnimValue = mdl_bone_anim_value()
                                    AnimValue.load(ani_file)
                                    #print "AnimValue.valid", AnimValue.valid
                                    #print "AnimValue.total", AnimValue.total
                                    #print "AnimValue.value", AnimValue.value
                                    for k in xrange(AnimValue.valid):
                                        AnimValue2 = mdl_bone_anim_value()
                                        AnimValue2.load(ani_file)
                                        rot_anim_data[i] += [AnimValue2.value]
                                        j += 1
                                    for k in xrange(AnimValue.valid, AnimValue.total):
                                        rot_anim_data[i] += [AnimValue2.value] #Repeat last entry
                                        j += 1
                            #print "line 4496: rot_anim_data for X:", rot_anim_data[0]
                            #print "line 4497: rot_anim_data for Y:", rot_anim_data[1]
                            #print "line 4498: rot_anim_data for Z:", rot_anim_data[2]
                        if AnimValuePtrPos is not None:
                            for i in xrange(0, 3): #X, Y, Z
                                if AnimValuePtrPos.offset[i] == 0:
                                    #No data
                                    continue
                                pos_anim_data[i] = []
                                ani_file.seek(SaveCurAniValuePtrPosOffset+AnimValuePtrPos.offset[i],0)
                                j = 0
                                while j < anim.numframes:
                                    AnimValue = mdl_bone_anim_value()
                                    AnimValue.load(ani_file)
                                    #print "AnimValue.valid", AnimValue.valid
                                    #print "AnimValue.total", AnimValue.total
                                    #print "AnimValue.value", AnimValue.value
                                    for k in xrange(AnimValue.valid):
                                        AnimValue2 = mdl_bone_anim_value()
                                        AnimValue2.load(ani_file)
                                        pos_anim_data[i] += [AnimValue2.value]
                                        j += 1
                                    for k in xrange(AnimValue.valid, AnimValue.total):
                                        pos_anim_data[i] += [AnimValue2.value] #Repeat last entry
                                        j += 1
                            #print "line 4521: pos_anim_data for X:", pos_anim_data[0]
                            #print "line 4522: pos_anim_data for Y:", pos_anim_data[1]
                            #print "line 4523: pos_anim_data for Z:", pos_anim_data[2]
                        all_pos_anim_data[StudioAnim.bone] = pos_anim_data
                        all_rot_anim_data[StudioAnim.bone] = rot_anim_data
                    if StudioAnim.nextoffset == 0:
                        break
                    else:
                        ani_file.seek(SaveCurAniOffset+StudioAnim.nextoffset,0)

                for i in xrange(bones_names_count):
                    FoundIt = 0
                    for j in xrange(self_bone_count):
                        if self.bones_names[i] == self.bones[j].pszName:
                            bone = self.bones[j]
                            for m_frame in xrange(anim.numframes):
                                pos = [0.0, 0.0, 0.0]
                                if all_pos_anim_data.has_key(j):
                                    pos_anim_data = all_pos_anim_data[j]
                                else:
                                    pos_anim_data = [None, None, None]
                                for k in xrange(3):
                                    if pos_anim_data[k] is not None:
                                        pos[k] = (pos_anim_data[k][m_frame] * self.bones[j].posscale[k]) + self.bones[j].pos[k]
                                    else:
                                        if ZeroFrame.has_key(j):
                                            pos[k] = ZeroFrame[j]['pos'][k]
                                        else:
                                            pos[k] = self.bones[j].pos[k]
                                rot = [0.0, 0.0, 0.0]
                                if all_rot_anim_data.has_key(j):
                                    rot_anim_data = all_rot_anim_data[j]
                                else:
                                    rot_anim_data = [None, None, None]
                                for k in xrange(3):
                                    if rot_anim_data[k] is not None:
                                        rot[k] = (rot_anim_data[k][m_frame] * self.bones[j].rotscale[k]) + self.bones[j].rot[k]
                                    else:
                                        if ZeroFrame.has_key(j):
                                            rot[k] = ZeroFrame[j]['rot'][k]
                                        else:
                                            rot[k] = self.bones[j].rot[k]
                                frame_name = anim.pszName.replace("@", "") + " frame " + str(m_frame+1)
                                bone_pos = quarkx.vect(pos[0], pos[1], pos[2])
                                quat = EulerAngle2Quaternion(rot)
                                tempmatrix = quaternion2matrix(quat)
                                bone_matrix = quarkx.matrix((tempmatrix[0][0], tempmatrix[0][1], tempmatrix[0][2]), (tempmatrix[1][0], tempmatrix[1][1], tempmatrix[1][2]), (tempmatrix[2][0], tempmatrix[2][1], tempmatrix[2][2]))
                                if bone.parent != -1:
                                    parent_bone_name = self.bones[bone.parent].pszName
                                    parent_pos, parent_matrix = GetParentPosAndRot(parent_bone_name, frame_name + ":mf")
                                    bone_pos = parent_pos + (parent_matrix * bone_pos)
                                    bone_matrix = parent_matrix * bone_matrix
                                bonelist[self.main_mdl_bones[i].name]['frames'][frame_name + ":mf"] = {}
                                bonelist[self.main_mdl_bones[i].name]['frames'][frame_name + ":mf"]['position'] = bone_pos.tuple
                                bonelist[self.main_mdl_bones[i].name]['frames'][frame_name + ":mf"]['rotmatrix'] = bone_matrix.tuple
                            FoundIt = 1
                            break
                    if not FoundIt:
                        #Bone not found; apply BaseFrame data
                        for m_frame in xrange(anim.numframes):
                            frame_name = anim.pszName.replace("@", "") + " frame " + str(m_frame+1)
                            QuArK_bone = self.main_mdl_bones[i]
                            bone_pos = quarkx.vect(bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"]['position'])
                            bone_matrix = quarkx.matrix(bonelist[self.main_mdl_bones[i].name]['frames']["BaseFrame " + mdl_name + ":mf"]['rotmatrix'])
                            if QuArK_bone['parent_name'] != "None":
                                old_parent_pos = quarkx.vect(bonelist[QuArK_bone['parent_name']]['frames']["BaseFrame " + mdl_name + ":mf"]['position'])
                                old_parent_matrix = quarkx.matrix(bonelist[QuArK_bone['parent_name']]['frames']["BaseFrame " + mdl_name + ":mf"]['rotmatrix'])
                                new_parent_pos = quarkx.vect(bonelist[QuArK_bone['parent_name']]['frames'][frame_name + ":mf"]['position'])
                                new_parent_matrix = quarkx.matrix(bonelist[QuArK_bone['parent_name']]['frames'][frame_name + ":mf"]['rotmatrix'])
                                #First, undo 'old' parent stuff
                                bone_pos = (~old_parent_matrix) * (bone_pos - old_parent_pos)
                                bone_matrix = (~old_parent_matrix) * bone_matrix
                                #Now, apply 'new' parent stuff
                                bone_pos = new_parent_pos + (new_parent_matrix * bone_pos)
                                bone_matrix = new_parent_matrix * bone_matrix
                            bonelist[self.main_mdl_bones[i].name]['frames'][frame_name + ":mf"] = {}
                            bonelist[self.main_mdl_bones[i].name]['frames'][frame_name + ":mf"]['position'] = bone_pos.tuple
                            bonelist[self.main_mdl_bones[i].name]['frames'][frame_name + ":mf"]['rotmatrix'] = bone_matrix.tuple
                for bone in bones_not_moving:
                    #Bone not moving; copy BaseFrame data
                    for m_frame in xrange(anim.numframes):
                        frame_name = anim.pszName.replace("@", "") + " frame " + str(m_frame+1)
                        bonelist[bone.name]['frames'][frame_name + ":mf"] = {}
                        bonelist[bone.name]['frames'][frame_name + ":mf"]['position'] = bonelist[bone.name]['frames']["BaseFrame " + mdl_name + ":mf"]['position']
                        bonelist[bone.name]['frames'][frame_name + ":mf"]['rotmatrix'] = bonelist[bone.name]['frames']["BaseFrame " + mdl_name + ":mf"]['rotmatrix']

        # Adds the animation baseframe to each component.
        NumberOfAnimsToLoad = 0
        for m_localanim in xrange(self.numlocalanim):
            if LoadAnim[m_localanim]:
                NumberOfAnimsToLoad += 1
        Strings[2462] = main_mdl_name + "\n" + Strings[2462] #FIXME: Probably wrong...
        progressbar = quarkx.progressbar(2462, len(self.main_mdl_comps)*NumberOfAnimsToLoad)
        alltags = editor.Root.dictitems['Misc:mg'].findallsubitems("", ":tag")
        model_tag_bone_names = []
        test_tag_name = folder_name + "_" + main_mdl_name + "_tag_"
        for tag in alltags:
            if tag.name.startswith(test_tag_name):
                self.tagsgroup.append(tag.copy())
                model_tag_bone_names = model_tag_bone_names + [tag.dictspec['bone']]
        for comp in range(len(self.main_mdl_comps)):
            comp_name = self.main_mdl_comps[comp].name
            new_comp = self.main_mdl_comps[comp].copy()
            framesgroup = new_comp.dictitems['Frames:fg']
            baseframe = framesgroup.dictitems['baseframe:mf']

            #Update baseframe vertices
            dupeframe = None
            baseframe_name = "BaseFrame " + mdl_name
            if baseframe_name + ":mf" in framesgroup.dictitems.keys():
                dupeframe = 1
            new_frame = baseframe.copy()
            new_frame.shortname = baseframe_name
            meshverts = baseframe.vertices
            newverts = [quarkx.vect(0.0, 0.0, 0.0)] * len(meshverts)
            for bone_index in xrange(bones_names_count):
                pbone = self.main_mdl_bones[bone_index]
                Bpos_old = quarkx.vect(bonelist[pbone.name]['frames']['baseframe:mf']['position'])
                Brot_old = quarkx.matrix(bonelist[pbone.name]['frames']['baseframe:mf']['rotmatrix'])
                Bpos_new = quarkx.vect(bonelist[pbone.name]['frames'][baseframe_name+':mf']['position'])
                Brot_new = quarkx.matrix(bonelist[pbone.name]['frames'][baseframe_name+':mf']['rotmatrix'])
                # Updates all the tags adding their 'BaseFrame' for this model's imported animation.
                if comp == 0 and pbone.name in model_tag_bone_names and dupeframe is None:
                    for tag in self.tagsgroup:
                        if tag.dictspec['bone'] == pbone.name:
                            tagframe = tag.subitems[0].copy()
                            tagframe.shortname = "Tag " + "BaseFrame " + mdl_name
                            Tpos = quarkx.vect(tagframe.dictspec['origin'])
                            Tpos = (~Brot_old) * (Tpos - Bpos_old)
                            Tpos = Bpos_new + (Brot_new * Tpos)
                            tagframe['origin'] = Tpos.tuple
                            m = Brot_new.tuple
                            tagframe['rotmatrix'] = (m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2], m[2][0], m[2][1], m[2][2])
                            tag.appenditem(tagframe)
                if pbone.vtxlist.has_key(comp_name):
                    vtxs = pbone.vtxlist[comp_name]
                    for vert_index in vtxs:
                        if editor.ModelComponentList[comp_name]['weightvtxlist'].has_key(vert_index):
                            weight_value = editor.ModelComponentList[comp_name]['weightvtxlist'][vert_index][pbone.name]['weight_value']
                        else:
                            weight_value = 1.0
                        vert_pos = meshverts[vert_index]
                        vert_pos = (~Brot_old) * (vert_pos - Bpos_old)
                        newverts[vert_index] += weight_value * (Bpos_new + (Brot_new * vert_pos))
            new_frame.vertices = newverts
            if dupeframe is None:
                framesgroup.appenditem(new_frame)
            baseframe = new_frame   #This is now our new baseframe
            meshverts = baseframe.vertices

            #Update frame vertices
            for m_localanim in xrange(self.numlocalanim):
                if not LoadAnim[m_localanim]: continue
                progressbar.progress()
                anim = self.animation_descs[m_localanim]
                for m_frame in xrange(anim.numframes):
                    frame_name = anim.pszName.replace("@", "") + " frame " + str(m_frame+1)
                    new_frame = baseframe.copy()
                    new_frame.shortname = frame_name
                    new_frame['frame_flags'] = str(anim.flags)
                    newverts = [quarkx.vect(0.0, 0.0, 0.0)] * len(meshverts)
                    for bone_index in xrange(bones_names_count):
                        pbone = self.main_mdl_bones[bone_index]
                        Bpos_old = quarkx.vect(bonelist[pbone.name]['frames'][baseframe_name+':mf']['position'])
                        Brot_old = quarkx.matrix(bonelist[pbone.name]['frames'][baseframe_name+':mf']['rotmatrix'])
                        Bpos_new = quarkx.vect(bonelist[pbone.name]['frames'][frame_name+':mf']['position'])
                        Brot_new = quarkx.matrix(bonelist[pbone.name]['frames'][frame_name+':mf']['rotmatrix'])
                        # Updates all the tags adding their animation frames for this model's imported animation.
                        if comp == 0 and pbone.name in model_tag_bone_names:
                            for tag in self.tagsgroup:
                                if tag.dictspec['bone'] == pbone.name:
                                    tagframe = tag.dictitems["Tag " + baseframe_name + ":tagframe"].copy()
                                    tagframe.shortname = "Tag " + frame_name
                                    Tpos = quarkx.vect(tagframe.dictspec['origin'])
                                    Tpos = (~Brot_old) * (Tpos - Bpos_old)
                                    Tpos = Bpos_new + (Brot_new * Tpos)
                                    tagframe['origin'] = Tpos.tuple
                                    m = Brot_new.tuple
                                    tagframe['rotmatrix'] = (m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2], m[2][0], m[2][1], m[2][2])
                                    tag.appenditem(tagframe)
                        if pbone.vtxlist.has_key(comp_name):
                            vtxs = pbone.vtxlist[comp_name]
                            for vert_index in vtxs:
                                if editor.ModelComponentList[comp_name]['weightvtxlist'].has_key(vert_index):
                                    weight_value = editor.ModelComponentList[comp_name]['weightvtxlist'][vert_index][pbone.name]['weight_value']
                                else:
                                    weight_value = 1.0
                                vert_pos = meshverts[vert_index]
                                vert_pos = (~Brot_old) * (vert_pos - Bpos_old)
                                newverts[vert_index] += weight_value * (Bpos_new + (Brot_new * vert_pos))
                    new_frame.vertices = newverts
                    framesgroup.appenditem(new_frame)

            self.new_mdl_comps.append(new_comp)

        Strings[2462] = Strings[2462].replace(main_mdl_name + "\n", "")
        progressbar.close()
            
        return self, ComponentList, QuArK_bones, message, self.tagsgroup, self.version, self.main_mdl_comps, self.new_mdl_comps

    def dump(self):
        tobj.logcon ("")
        tobj.logcon ("========================")
        tobj.logcon ("Object file: " + str(file))
        tobj.logcon ("")
        tobj.logcon ("ident: " + str(self.ident))
        tobj.logcon ("version: " + str(self.version))
        tobj.logcon ("-----has to be the same in the phy and vtx files to load----")
        tobj.logcon ("checksum: " + str(self.checksum))
        tobj.logcon ("name: " + self.name)
        tobj.logcon ("length: " + str(self.length))
        tobj.logcon ("-----ideal eye position----")
        tobj.logcon ("eyeposition: " + str(self.eyeposition))
        tobj.logcon ("-----illumination center----")
        tobj.logcon ("illumposition: " + str(self.illumposition))
        tobj.logcon ("-----ideal movement hull size----")
        tobj.logcon ("hull_min: " + str(self.hull_min))
        tobj.logcon ("hull_max: " + str(self.hull_max))
        tobj.logcon ("-----clipping bounding box----")
        tobj.logcon ("view_bbmin: " + str(self.view_bbmin))
        tobj.logcon ("view_bbmax: " + str(self.view_bbmax))
        tobj.logcon ("-----flags----")
        tobj.logcon ("flags: " + str(self.flags))
        tobj.logcon ("-----bones----")
        tobj.logcon ("numbones: " + str(self.numbones))
        tobj.logcon ("boneindex: " + str(self.boneindex))
        tobj.logcon ("-----bone controllers----")
        tobj.logcon ("numbonecontrollers: " + str(self.numbonecontrollers))
        tobj.logcon ("bonecontrollerindex: " + str(self.bonecontrollerindex))
        tobj.logcon ("-----hitboxes----")
        tobj.logcon ("numhitboxsets: " + str(self.numhitboxsets))
        tobj.logcon ("hitboxsetindex: " + str(self.hitboxsetindex))
        tobj.logcon ("-----animations----")
        tobj.logcon ("numlocalanim: " + str(self.numlocalanim))
        tobj.logcon ("localanimindex: " + str(self.localanimindex))
        tobj.logcon ("-----sequences----")
        tobj.logcon ("numlocalseq: " + str(self.numlocalseq))
        tobj.logcon ("localseqindex: " + str(self.localseqindex))
        tobj.logcon ("---initialization flags---")
        tobj.logcon ("activitylistversion: " + str(self.activitylistversion))
        tobj.logcon ("eventsindexed: " + str(self.eventsindexed))
        tobj.logcon ("-----raw textures----")
        tobj.logcon ("numtextures: " + str(self.numtextures))
        tobj.logcon ("textureindex: " + str(self.textureindex))
        tobj.logcon ("-----cd textures----")
        tobj.logcon ("numcdtextures: " + str(self.numcdtextures))
        tobj.logcon ("cdtextureindex: " + str(self.cdtextureindex))
        tobj.logcon ("-----replaceable textures tables----")
        tobj.logcon ("numskinref: " + str(self.numskinref))
        tobj.logcon ("numskinfamilies: " + str(self.numskinfamilies))
        tobj.logcon ("skinindex: " + str(self.skinindex))
        tobj.logcon ("num_bodyparts: " + str(self.num_bodyparts))
        tobj.logcon ("bodypartindex: " + str(self.bodypartindex))
        tobj.logcon ("-----queryable attachable points----")
        tobj.logcon ("numlocalattachments: " + str(self.numlocalattachments))
        tobj.logcon ("localattachmentindex: " + str(self.localattachmentindex))
        tobj.logcon ("-----animation node to animation node transition graph----")
        tobj.logcon ("numlocalnodes: " + str(self.numlocalnodes))
        tobj.logcon ("localnodeindex: " + str(self.localnodeindex))
        tobj.logcon ("localnodenameindex: " + str(self.localnodenameindex))
        tobj.logcon ("numflexdesc: " + str(self.numflexdesc))
        tobj.logcon ("flexdescindex: " + str(self.flexdescindex))
        tobj.logcon ("numflexcontrollers: " + str(self.numflexcontrollers))
        tobj.logcon ("flexcontrollerindex: " + str(self.flexcontrollerindex))
        tobj.logcon ("numflexrules: " + str(self.numflexrules))
        tobj.logcon ("flexruleindex: " + str(self.flexruleindex))
        tobj.logcon ("numikchains: " + str(self.numikchains))
        tobj.logcon ("ikchainindex: " + str(self.ikchainindex))
        tobj.logcon ("nummouths: " + str(self.nummouths))
        tobj.logcon ("mouthindex: " + str(self.mouthindex))
        tobj.logcon ("numlocalposeparameters: " + str(self.numlocalposeparameters))
        tobj.logcon ("localposeparamindex: " + str(self.localposeparamindex))
        tobj.logcon ("surfacepropindex: " + str(self.surfacepropindex))
        tobj.logcon ("-----Key values----")
        tobj.logcon ("keyvalueindex: " + str(self.keyvalueindex))
        tobj.logcon ("keyvaluesize: " + str(self.keyvaluesize))
        tobj.logcon ("numlocalikautoplaylocks: " + str(self.numlocalikautoplaylocks))
        tobj.logcon ("localikautoplaylockindex: " + str(self.localikautoplaylockindex))
        tobj.logcon ("-----collision model mass----")
        tobj.logcon ("mass: " + str(self.mass))
        tobj.logcon ("contents: " + str(self.contents))
        tobj.logcon ("-----external animations, models, etc.----")
        tobj.logcon ("numincludemodels: " + str(self.numincludemodels))
        tobj.logcon ("includemodelindex: " + str(self.includemodelindex))
        tobj.logcon ("-----implementation specific back pointer to virtual data----")
        tobj.logcon ("virtualModel: " + str(self.virtualModel))
        tobj.logcon ("-----for demand loaded animation blocks----")
        tobj.logcon ("szanimblocknameindex: " + str(self.szanimblocknameindex))
        tobj.logcon ("numanimblocks: " + str(self.numanimblocks))
        tobj.logcon ("animblockindex: " + str(self.animblockindex))
        tobj.logcon ("animblockModel: " + str(self.animblockModel))
        tobj.logcon ("bonetablebynameindex: " + str(self.bonetablebynameindex))
        tobj.logcon ("-----used by tools only that don't cache, but persist mdl's peer data----")
        tobj.logcon ("-----engine uses virtualModel to back link to cache pointers----")
        tobj.logcon ("pVertexBase: " + str(self.pVertexBase))
        tobj.logcon ("pIndexBase: " + str(self.pIndexBase))
        tobj.logcon ("rootLOD: " + str(self.rootLOD))
        tobj.logcon ("unused1: " + str(self.unused1))
        tobj.logcon ("unused2: " + str(self.unused2))
        tobj.logcon ("zeroframecacheindex: " + str(self.zeroframecacheindex))
        tobj.logcon ("array1: " + str(self.array1))
        tobj.logcon ("array2: " + str(self.array2))
        tobj.logcon ("array3: " + str(self.array3))
        tobj.logcon ("array4: " + str(self.array4))
        tobj.logcon ("array5: " + str(self.array5))
        tobj.logcon ("array6: " + str(self.array6))
        tobj.logcon ("")
        tobj.logcon ("========================")



########################
# To run this file
########################
def load_mdl(basepath, filename):
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

    # FullPathName is the full path and the full file name being imported with forward slashes.
    FullPathName = filename.replace("\\", "/")
    # FolderPath is the full path to the model's folder w/o slash at end.
    FolderPath = FullPathName.rsplit("/", 1)
    FolderPath, ModelName = FolderPath[0], FolderPath[1]
    # ModelFolder is just the .HL2 model file's FOLDER name without any path, slashes or the ".HL2" file name.
    # Probably best to use ModelFolder to keep all the tags and bones (if any) together for a particular modle.
    ModelFolder = FolderPath.rsplit("/", 1)[1]
    # BasePath is the full path to and the name of the game folder or any folder that has the "models" and "scripts" (shader or material) folders in it, w/o slash at end.
    BasePath = FolderPath.rsplit("/models/", 1)[0]
    # ModelsPath is just the path starting with the "models/" FOLDER on without the ".HL2" file name or slash at the end of the path.
    ModelsPath = FolderPath.replace(BasePath+"/", "")
    # ModelName is just the .HL2 model file name without any path or the ".HL2" type.
    ModelName = ModelName.rsplit(".", 1)[0]

    # read the file in
    file = open(filename,"rb")
    mdl = mdl_obj()
    message = ""
    MODEL, ComponentList, QuArK_bones, message, tagsgroup, version, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name, SpecsList = mdl.load(file, editor, ModelFolder, ModelName, message)

    if logging == 1:
        mdl.dump() # Writes the file Header last to the log for comparison reasons.

    if MODEL is None:
        return MODEL, file, None, None, None, message, tagsgroup, version, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name, SpecsList

    return MODEL, file, ComponentList, QuArK_bones, mdl.hitboxsets, message, tagsgroup, version, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name, SpecsList


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
    "filename is the full path and name of the .HL2 file selected."
    "gamename is None."
    "For example:  C:\Valve\Steam\...\models\airboat.mdl"

    global editor, logging, tobj, starttime, importername, textlog, Strings, basepath
    import quarkpy.mdleditor
    editor = quarkpy.mdleditor.mdleditor

    ### First we test for a valid (proper) model path.
    basepath = ie_utils.validpath(filename)
    try:
        basepath = basepath.replace("\\", "/")
    except:
        editor = None # Reset the global again.
        quarkx.msgbox("Can not open the file.\n" + filename + "\n\nCopy file to\na folder called 'models'\nsomeplace and try again.", MT_ERROR, MB_OK)
        return
    if basepath is None:
        editor = None # Reset the global again.
        quarkx.msgbox("Can not open the file.\n" + filename + "\n\nCopy file to\na folder called 'models'\nsomeplace and try again.", MT_ERROR, MB_OK)
        return

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
    self, file, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, version, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name, SpecsList = load_mdl(basepath, filename)

    if version is None or (version != 44 and version != 49):
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        if version == 6:
            quarkx.msgbox("Invalid Half-Life 2 .mdl model.\nVersion number is " + str(version) + "\nThis is a Quake .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        elif version == 10:
            quarkx.msgbox("Invalid Half-Life 2 .mdl model.\nVersion number is " + str(version) + "\nThis is a Half-Life 1 .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        elif version is not None:
            quarkx.msgbox("Invalid Half-Life 2 .mdl model.\nID, Version number is " + str(message) + ", " + str(version) + "\nThis is another type .mdl model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        else:
            pass
        try:
            progressbar.close()
        except:
            pass
        return
    if main_mdl_name is None:
        FinishImport(file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps)
    else:
        # Calls the dialog to limit large animation importing.
        UIImportDialog(self, file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name, SpecsList)

def FinishImport(file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps):
    file.close()
    if editor.form is not None:
        undo = quarkx.action()
    editor_dictitems = editor.Root.dictitems

    # Import the tags (attachments) if any.
    if editor.form is not None:
        alltags = editor.Root.dictitems['Misc:mg'].findallsubitems("", ":tag")
    for i in range(len(tagsgroup)):
        if editor.form is not None:
            existing_tag = None
            for tag in alltags:
                if tag.name == tagsgroup[i].name:
                    undo.exchange(tag, tagsgroup[i])
                    existing_tag = 1
                    break
            if existing_tag is None:
                undo.put(editor_dictitems['Misc:mg'], tagsgroup[i])
        else:
            editor_dictitems['Misc:mg'].appenditem(tagsgroup[i])

    # Import the bboxes (hit boxes) if any.
    if editor.form is not None:
        for bboxgroup in hitboxsets:
            undo.put(editor_dictitems['Misc:mg'], bboxgroup)
    else:
        for bboxgroup in hitboxsets:
            editor_dictitems['Misc:mg'].appenditem(bboxgroup)

    # Section below sets up the QuArK editor.ModelComponentList for each mesh.
    for comp in ComponentList:
        if not editor.ModelComponentList.has_key(comp.name):
            editor.ModelComponentList[comp.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}

    # Process the bones, if any.
    newbones = []
    for bone_index in range(len(QuArK_bones)): # Using list of ALL bones.
        boneobj = QuArK_bones[bone_index]
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

        if len(main_mdl_comps) != 0:
            for i in range(len(main_mdl_comps)):
                undo.exchange(main_mdl_comps[i], new_mdl_comps[i])
            name = filename.rsplit("\\", 1)[1]
            editor.ok(undo, name + " animation imported")
        else:
            editor.ok(undo, str(len(ComponentList)) + " .mdl Components imported")

        editor = None   #Reset the global again
        if message != "":
            message = message + "================================\r\n\r\n"
            message = message + "You need to find and supply the proper texture(s) and folder(s) above.\r\n"
            message = message + "Extract the folder(s) and file(s) to the 'game' folder.\r\n\r\n"
            message = message + "If a texture does not exist it may need a .vmt material file or some other type of image file.\r\n"
            message = message + "If so then you need to make a .tga file copy of that texture, perhaps in PaintShop Pro.\r\n\r\n"
            message = message + "You may also need to rename it to match the exact name above.\r\n"
            message = message + "Either case, it would be for editing purposes only and should be placed in the model's folder.\r\n\r\n"
            message = message + "Once this is done, then delete the imported components and re-import the model."
            quarkx.textbox("WARNING", "Missing Skin Textures:\r\n\r\n================================\r\n" + message, MT_WARNING)

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
import ie_md0_HL2_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".mdl Half-Life2 Importer", ".mdl file", "*.mdl", loadmodel, ie_md0_HL2_import)


######################################################
# DIALOG SECTION (for Editor's Specifics/Args page)
######################################################
def dataformname(o):
    "Returns the data form for this type of object 'o' (a model's skin texture) to use for the Specific/Args page."
    import quarkpy.mdlentities # Used further down in a couple of places.

    # Next line calls for the External Skin Editor Module in mdlentities.py to be used.
    external_skin_editor_dialog_plugin = quarkpy.mdlentities.UseExternalSkinEditor()

    # Next lines create the spacific items for a skin's flags if the o object is a selected skin.
    if o.dictspec.has_key('Image1'):
        flag_items = []
        flag__values = []
        flag_items = flag_items + ['"None"$0D']
        flag_items = flag_items + ['"Chrome (cstrike)"$0D']
        flag_items = flag_items + ['"Chrome (valve)"$0D']
        flag_items = flag_items + ['"Additive"$0D']
        flag_items = flag_items + ['"Chrome & Additive"$0D']
        flag_items = flag_items + ['"Transparent"']
        flag__values = flag__values + ['"0"$0D']
        flag__values = flag__values + ['"2"$0D']
        flag__values = flag__values + ['"3"$0D']
        flag__values = flag__values + ['"32"$0D']
        flag__values = flag__values + ['"34"$0D']
        flag__values = flag__values + ['"64"']

        skin_items = """sep: = { Typ="S" Txt="" } HL_skin_flags: = {Typ = "CL" Txt = "skin flags" items = """
        for item in flag_items:
            skin_items = skin_items + item

        skin_items = skin_items + """ values = """
        for item in flag__values:
            skin_items = skin_items + item

        skin_items = skin_items + """ Hint="List of available skin flags."$0D"Will be applied to current skin only."$0D"None = 0 (default), Chrome = 2, Additive = 32"$0D"Chrome & Additive = 34, Transparent = 64"}"""

    # Next lines create the spacific items for a frame if the o object is a selected frame.
    if o.type == ":mf":
        flag_items = []
        flag__values = []
        flag_items = flag_items + ['"None"$0D']
        flag_items = flag_items + ['"non-looping"$0D']
        flag_items = flag_items + ['"looping"']
        flag__values = flag__values + ['"None"$0D']
        flag__values = flag__values + ['"0"$0D']
        flag__values = flag__values + ['"1"']

        frame_items = """sep: = { Typ="S" Txt="" } frame_flags: = {Typ = "CL" Txt = "frame flags" items = """
        for item in flag_items:
            frame_items = frame_items + item

        frame_items = frame_items + """ values = """
        for item in flag__values:
            frame_items = frame_items + item

        frame_items = frame_items + """ Hint="List of available frame flags."$0D"Will be applied to all 'group' frames (starting with the same name)."$0D"non-looping = 0 (default), looping = 1"}"""

    # Next line calls for the Vertex Weights Specifics Module in mdlentities.py to be used.
    vertex_weights_specifics_plugin = quarkpy.mdlentities.UseVertexWeightsSpecifics()

    # Next line calls for the Shader Module in mdlentities.py to be used.
    Shader_dialog_plugin = quarkpy.mdlentities.UseShaders()

    dlgdef = """
    {
      Help = "These are the Specific settings for Half-Life 1 & 2 (.mdl) model types."$0D
             "mdl models use 'meshes' the same way that QuArK uses 'components'."$0D
             "Each can have its own special Surface or skin texture settings."$0D
             "These textures have a 'material' (or shader) .vmf file that they use for special effects."$0D0D22
             "skin name"$22" - The currently selected skin texture name."$0D22
             "edit skin"$22" - Opens this skin texture in an external editor (can not open .vtf files)."$0D22
             "HL_skin_flags"$22" - (Appears when a skin is selected) List of available skin flags."$0D
             "        Will be applied to the current skin only."$0D
             "        None = 0 (default), Chrome (cstrike) = 2, Chrome (valve) = 3,"$0D
             "        Additive = 32, Chrome & Additive = 34, Transparent = 64"$0D22
             "frame_flags"$22" - (Appears when frame is selected) List of available frame flags."$0D
             "        Will be applied to all 'group' frames (starting with the same name)."$0D
             "        non-looping = 0 (default), looping = 1"$0D22
             "shader file"$22" - Gives the full path and name of the .vmf material"$0D
             "           shader file that the selected skin texture uses, if any."$0D22
             "shader name"$22" - Gives the name of the shader located in the above file"$0D
             "           that the selected skin texture uses, if any."$0D22
             "shader keyword"$22" - Gives the above shader 'keyword' that is used to identify"$0D
             "          the currently selected skin texture used in the shader, if any."$0D22
             "shader lines"$22" - Number of lines to display in window below, max. = 35."$0D22
             "edit shader"$22" - Opens shader below in a text editor."$0D22
             "mesh shader"$22" - Contains the full text of this skin texture's shader, if any."$0D22
             "          This can be copied to a text file, changed and saved."
      skin_name:      = {t_ModelEditor_texturebrowser = ! Txt="skin name"    Hint="The currently selected skin texture name."}
      """ + external_skin_editor_dialog_plugin + """
    """
    if o.dictspec.has_key('Image1'):
        dlgdef = dlgdef + """""" + skin_items + """"""
    if o.type == ":mf":
        dlgdef = dlgdef + """""" + frame_items + """"""
    dlgdef = dlgdef + """""" + vertex_weights_specifics_plugin + """
    """ + Shader_dialog_plugin + """}"""

    editor = quarkpy.mdleditor.mdleditor # Get the editor.
    ico_mdlskv = ico_dict['ico_mdlskv']  # Just to shorten our call later.
    icon_btns = {}                       # Setup our button list, as a dictionary list, to return at the end.
    # Next line calls for the Vertex Weights system in mdlentities.py to be used.
    vtxweightsbtn = quarkpy.qtoolbar.button(quarkpy.mdlentities.UseVertexWeights, "Open or Update\nVertex Weights Dialog||When clicked, this button opens the dialog to allow the 'weight' movement setting of single vertexes that have been assigned to more then one bone handle.\n\nClick the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
    vtxweightsbtn.state = quarkpy.qtoolbar.normal
    vtxweightsbtn.caption = "" # Texts shows next to button and keeps the width of this button so it doesn't change.
    icon_btns['vtxweights'] = vtxweightsbtn # Put our button in the above list to return.

    if (editor.Root.currentcomponent.currentskin is not None) and (o.name == editor.Root.currentcomponent.currentskin.name): # If this is not done it will cause looping through multiple times.
        if o.parent.parent.dictspec.has_key("shader_keyword") and o.dictspec.has_key("shader_keyword"):
            if o.parent.parent.dictspec['shader_keyword'] != o.dictspec['shader_keyword']:
                if o.parent.parent.dictspec['shader_file'] == o.dictspec['shader_file']:
                    o['shader_keyword'] = o.parent.parent.dictspec['shader_keyword']
        if (o.parent.parent.dictspec.has_key("skin_name")) and (o.parent.parent.dictspec['skin_name'] != o.name) and (not o.parent.parent.dictspec['skin_name'] in o.parent.parent.dictitems['Skins:sg'].dictitems.keys()):
            # Gives the newly selected skin texture's game folders path and file name, for example:
            #     models/monsters/cacodemon/cacoeye.tga
            skinname = o.parent.parent.dictspec['skin_name']
            skin = quarkx.newobj(skinname)
            # Gives the full current work directory (cwd) path up to the file name, need to add "\\" + filename, for example:
            #     E:\Program Files\Doom 3\base\models\monsters\cacodemon
            cur_folder = os.getcwd()
            # Gives just the actual file name, for example: cacoeye.tga
            tex_file = skinname.split("/")[-1]
            # Puts the full path and file name together to get the file, for example:
            # E:\Program Files\Doom 3\base\models\monsters\cacodemon\cacoeye.tga
            file = cur_folder + "\\" + tex_file
            image = quarkx.openfileobj(file)
            skin['Image1'] = image.dictspec['Image1']
            skin['Size'] = image.dictspec['Size']
            skin['shader_keyword'] = o.parent.parent.dictspec['shader_keyword']
            skingroup = o.parent.parent.dictitems['Skins:sg']
            undo = quarkx.action()
            undo.put(skingroup, skin)
            editor.ok(undo, o.parent.parent.shortname + " - " + "new skin added")
            editor.Root.currentcomponent.currentskin = skin
            editor.layout.explorer.sellist = [editor.Root.currentcomponent.currentskin]
            quarkpy.mdlutils.Update_Skin_View(editor, 2)

    DummyItem = o
    while (DummyItem.type != ":mc"): # Gets the object's model component.
        DummyItem = DummyItem.parent
    comp = DummyItem

    # This sections handles the data for this model type skin page form.
    if o.dictspec.has_key('Image1'):
        if not o.dictspec.has_key('HL_skin_flags'):
            o['HL_skin_flags'] = "0"
            comp['HL_skin_flags'] = "0"
            comp.currentskin = o
        elif comp.name == editor.Root.currentcomponent.name and o.name != comp.currentskin.name:
            comp['HL_skin_flags'] = o.dictspec['HL_skin_flags']
        elif comp.name == editor.Root.currentcomponent.name and comp.dictspec.has_key('HL_skin_flags') and comp.dictspec['HL_skin_flags'] != o.dictspec['HL_skin_flags']: # When setting is changed
            o['HL_skin_flags'] = comp.dictspec['HL_skin_flags']
            for item in editor.Root.subitems:
                if item.type == ":mc":
                    for skin in item.dictitems['Skins:sg'].subitems:
                        if skin.name == o.name:
                            skin['HL_skin_flags'] = o.dictspec['HL_skin_flags']
                            item['HL_skin_flags'] = o.dictspec['HL_skin_flags']
                            break
        elif comp.name == editor.Root.currentcomponent.name:
            comp['HL_skin_flags'] = o.dictspec['HL_skin_flags']
        elif comp.name != editor.Root.currentcomponent.name:
            if o.name != comp.currentskin.name:
                comp['HL_skin_flags'] = o.dictspec['HL_skin_flags']

    # This sections handles the data for this model type frame page form.
    if o.type == ":mf":
        global framename
        if comp.dictspec.has_key('frame_flags'):
            if o.dictspec.has_key('frame_flags'):
                if framename is not None and o.name.startswith(framename):
                    if comp.dictspec['frame_flags'] == "None":
                        frame_flags = "" # Update group frames here.
                        frames = o.parent.subitems
                        group = None
                        for frame in frames:
                            if frame.name.startswith(framename):
                                frame['frame_flags'] = frame_flags
                                group = 1
                            elif group is not None:
                                break
                    elif comp.dictspec['frame_flags'] != o.dictspec['frame_flags']:
                        frame_flags = comp.dictspec['frame_flags'] # Update group frames here.
                        frames = o.parent.subitems
                        group = None
                        for frame in frames:
                            if frame.name.startswith(framename):
                                frame['frame_flags'] = frame_flags
                                group = 1
                            elif group is not None:
                                break
            else:
                if comp.dictspec['frame_flags'] != "None" and (framename is not None and o.name.startswith(framename)):
                    frame_flags = comp.dictspec['frame_flags'] # Update group frames here.
                    frames = o.parent.subitems
                    group = None
                    for frame in frames:
                        if frame.name.startswith(framename):
                            frame['frame_flags'] = frame_flags
                            group = 1
                        elif group is not None:
                            break
        else:
            comp['frame_flags'] = "None"
        framename = o.shortname.split(" ")[0]
        if framename[len(framename)-1].isdigit():
            list = []
            for i in framename:
                list.append(i)
            list.reverse()
            for i in list:
                if i.isdigit():
                    list.remove(i)
                    continue
                if not i.isdigit():
                    break
            list.reverse()
            framename = ""
            for i in list:
                framename += i

    if comp.type == ":mc": # Just makes sure what we have is a model component.
        if comp.dictspec.has_key('shader_file') and o.dictspec.has_key('shader_file') and comp.dictspec.has_key('mesh_shader') and o.dictspec.has_key('mesh_shader'):
            if comp.dictspec['shader_file'] == o.dictspec['shader_file'] and comp.dictspec['mesh_shader'] != o.dictspec['mesh_shader']:
                o['mesh_shader'] = comp.dictspec['mesh_shader']
            else:
                comp['mesh_shader'] = o.dictspec['mesh_shader']

        formobj = quarkx.newobj("mdl_mc:form")
        formobj.loadtext(dlgdef)
        return formobj, icon_btns
    else:
        return None, None

def dataforminput(o):
    "Returns the default settings or input data for this type of object 'o' (a model's skin texture) to use for the Specific/Args page."

    DummyItem = o
    while (DummyItem.type != ":mc"): # Gets the object's model component.
        DummyItem = DummyItem.parent
    if DummyItem.type == ":mc":
        comp = DummyItem

        # This sections handles the data for this model type skin page form.
        if o.dictspec.has_key('Image1'):
            if o.dictspec.has_key('HL_skin_flags'):
                comp['HL_skin_flags'] = o.dictspec['HL_skin_flags']
            else:
                comp['HL_skin_flags'] = "0"

        # This sections handles the data for this model type frame page form.
        if o.type == ":mf":
            if o.dictspec.has_key('frame_flags'):
                comp['frame_flags'] = o.dictspec['frame_flags']
            else:
                comp['frame_flags'] = "None"

        # This sections handles the data for this model type skin page form.
        # This makes sure what is selected is a model skin, if so it fills the Skin page data and adds the items to the component.
        # It also handles the shader file which its name is the full path and name of the skin texture.
        if len(comp.dictitems['Skins:sg'].subitems) == 0 or o in comp.dictitems['Skins:sg'].subitems:
            if not comp.dictspec.has_key('shader_file'):
                if o.dictspec.has_key('shader_file'):
                    comp['shader_file'] = o.dictspec['shader_file']
                else:
                    comp['shader_file'] = "None"
            else:
                if o.dictspec.has_key('shader_file'):
                    comp['shader_file'] = o.dictspec['shader_file']
                else:
                    comp['shader_file'] = "None"
            if not comp.dictspec.has_key('shader_name'):
                if o.dictspec.has_key('shader_name'):
                    comp['shader_name'] = o.dictspec['shader_name']
                else:
                    comp['shader_name'] = "None"
            else:
                if o.dictspec.has_key('shader_name'):
                    comp['shader_name'] = o.dictspec['shader_name']
                else:
                    comp['shader_name'] = "None"
            if not comp.dictspec.has_key('skin_name'):
                if len(comp.dictitems['Skins:sg'].subitems) != 0:
                   comp['skin_name'] = o.name
                else:
                   comp['skin_name'] = "no skins exist"
            else:
                if len(comp.dictitems['Skins:sg'].subitems) != 0:
                   comp['skin_name'] = o.name
                else:
                   comp['skin_name'] = "no skins exist"
            if not comp.dictspec.has_key('shader_keyword'):
                if o.dictspec.has_key("shader_keyword"):
                    comp['shader_keyword'] = o.dictspec['shader_keyword']
                else:
                    comp['shader_keyword'] = o['shader_keyword'] = "None"
            else:
                if o.dictspec.has_key("shader_keyword"):
                    comp['shader_keyword'] = o.dictspec['shader_keyword']
                else:
                    comp['shader_keyword'] = o['shader_keyword'] = "None"
            if not comp.dictspec.has_key('shader_lines'):
                if quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] is not None:
                    comp['shader_lines'] = quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"]
                else:
                    comp['shader_lines'] = "8"
                    quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = comp.dictspec['shader_lines']
            else:
                quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = comp.dictspec['shader_lines']
            if not comp.dictspec.has_key('mesh_shader'):
                if o.dictspec.has_key('mesh_shader'):
                    comp['mesh_shader'] = o.dictspec['mesh_shader']
                else:
                    comp['mesh_shader'] = "None"


##########################################################
# DIALOG SECTION (for limiting large .mdl animation files)
##########################################################
class ImportDlg(quarkpy.dlgclasses.LiveEditDlg):
    size = (250, 500)
    dlgflags = FWF_KEEPFOCUS
    dfsep = 0.8      # sets 80% for labels and the rest for a check box.
    dlgdef = """ """ # The dialog is created in the setup function to allow self generated items.

    def cancel(self, dlg):
        # Modified from dlgclasses.py
        quarkpy.qmacro.dialogbox.close(self, dlg)
        self.src = None


def DialogClick(MDL, file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name):
    if editor is None: return

    def setup(self, editor=editor, total_frames=total_frames):
        editor.importdlg = self
        self.dlgdef = """
            {
            Style = "13"
            Caption = "mdl Import Items"
            sep: = {
                Typ="S"
                Txt="Instructions: place cursor here"
                Hint = "Place your cursor over each item"$0D
                       "below for a description of what it does."$0D$0D
                       "The more frames = the longer to import (could be minutes)"$0D$0D
                       "To import, check boxes then click the 'Close dialog' button at the very bottom."$0D$0D
                       "You can cancel the entire import process at any time by clearing all"$0D
                       "checked boxes and clicking the 'Close dialog' button at the very bottom."
                   }
            sep: = { Typ="S" Txt="" }

            """ + SpecsList + """

            sep: = { Typ="S" Txt="" }
            exit:py = {Txt="Import selections / Close dialog"}
            }
            """

        src = self.src
        self.all = src['all']

    def action(self, editor=editor, MDL=MDL):
        src = self.src
        if src['all'] is not None and self.all is None:
            for name in MDL.SRCsList:
                if src[name] is not None:
                    src[name] = None
        else:
            src['all'] = None

    def onclosing(self, MDL=MDL, file=file, editor=editor, filename=filename, ComponentList=ComponentList, QuArK_bones=QuArK_bones, hitboxsets=hitboxsets, message=message, tagsgroup=tagsgroup, main_mdl_comps=main_mdl_comps, new_mdl_comps=new_mdl_comps, main_mdl_name=main_mdl_name, total_frames=total_frames, folder_name=folder_name, mdl_name=mdl_name):
        LoadAnim = [] # List for which animation sequences to load.
        src = self.src
        cancel = 0
        if src['all'] is not None:
            for name in MDL.SRCsList:
                LoadAnim += [1]
                cancel += 1
        else:
            for name in MDL.SRCsList:
                if src[name] is not None:
                    LoadAnim += [1]
                    cancel += 1
                else:
                    LoadAnim += [0]
        if cancel != 0:
            MDL, ComponentList, QuArK_bones, message, MDL.tagsgroup, MDL.version, MDL.main_mdl_comps, MDL.new_mdl_comps = MDL.load_Animation(ComponentList, QuArK_bones, message, file, editor, folder_name, mdl_name, main_mdl_name, LoadAnim)
            FinishImport(file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps)

    ImportDlg(quarkx.clickform, 'importdlg', editor, setup, action, onclosing)


def UIImportDialog(MDL, file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name, SpecsList):
    if total_frames > 200:
        # Sets up the new window form for the importers dialog for user selection settings and calls its class.
        DialogClick(MDL, file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps, main_mdl_name, total_frames, folder_name, mdl_name)
    else:
        LoadAnim = [] # List for which animation sequences to load.
        for name in MDL.SRCsList:
            LoadAnim += [1]
        MDL, ComponentList, QuArK_bones, message, MDL.tagsgroup, MDL.version, MDL.main_mdl_comps, MDL.new_mdl_comps = MDL.load_Animation(ComponentList, QuArK_bones, message, file, editor, folder_name, mdl_name, main_mdl_name, LoadAnim)
        FinishImport(file, editor, filename, ComponentList, QuArK_bones, hitboxsets, message, tagsgroup, main_mdl_comps, new_mdl_comps)


# ----------- REVISION HISTORY ------------
#
# $Log: ie_md0_HL2_import.py,v $
# Revision 1.20  2012/11/11 03:54:40  cdunde
# Minor correction.
#
# Revision 1.19  2012/08/31 22:59:40  cdunde
# Minor logging label correction.
#
# Revision 1.18  2012/08/01 01:34:49  cdunde
# File cleanup and added animation file name possibilities.
#
# Revision 1.17  2012/03/10 20:30:32  cdunde
# Fix for skin flag and its comp proper setting handling.
#
# Revision 1.16  2012/03/10 08:10:12  cdunde
# Added texture skin flag support.
#
# Revision 1.15  2012/03/03 07:26:35  cdunde
# Sync 2. Rearranged files and names to coincide better.
#
# Revision 1.14  2012/02/25 18:55:59  cdunde
# Rearranged files and names to coincide better.
#
# Revision 1.13  2011/12/28 08:28:22  cdunde
# Setup importer bone['type'] not done yet.
#
# Revision 1.12  2011/12/23 03:15:17  cdunde
# To remove all importers bone ['type'] from ModelComponentList['bonelist'].
# Those should be kept with the individual bones if we decide it is needed.
#
# Revision 1.11  2011/11/19 06:28:18  cdunde
# Added frame flags importing and Specifics page setting support.
#
# Revision 1.10  2011/05/25 20:55:03  cdunde
# Revamped Bounding Box system for more flexibility with model formats that do not have bones, only single or multi components.
#
# Revision 1.9  2011/04/07 19:07:37  cdunde
# Update to change all print statements over to logging system.
#
# Revision 1.8  2011/04/03 08:40:15  cdunde
# Added code for misuse of upper and lower case item name changing.
#
# Revision 1.7  2011/04/02 04:18:23  cdunde
# To stop dupe BaseFrames when importing animations.
#
# Revision 1.6  2011/04/02 03:17:58  cdunde
# Minor update to cancel animation importing..
#
# Revision 1.5  2011/04/02 01:08:10  cdunde
# Added Half-Life 2 importer animation support with bone, attachment and bbox movement.
#
# Revision 1.4  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.3  2011/03/10 20:57:53  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
# Added HL2 animation support.
#
# Revision 1.2  2011/01/14 02:54:30  cdunde
# Increased material and texture locating abilities,
# added multi material editing and dialog support
# and removed unneeded code from this importer.
#
# Revision 1.1  2011/01/12 01:59:08  cdunde
# Setup importer for Half-Life 2 mesh (animation to follow) with bone, attachment, bbox and skin support.
#
#
#