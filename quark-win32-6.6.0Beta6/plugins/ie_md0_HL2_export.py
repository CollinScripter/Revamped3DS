# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for original Half-Life 2 .mdl model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md0_HL2_export.py,v 1.1 2013/05/30 07:58:11 cdunde Exp $

"""
I started the HL2 Exporter by simply coping the HL1 Exporter so there is a lot of HL1 stuff
in this that does not apply to HL2. I then worked on one class at a time leaving off with the bones classes.
Right now the HL2 Exporter DOES write to the .mdl file but remember there are also two or three other files
that it must create, the .vtx, .vvd and ani (if there is any animation for the model) and the .mdl file will not re-import.
By comparing the classes in both the HL1 and HL2 Exporters someone should be able to see
which ones still need to be done.

This section gives the class names differences between HL1 and HL2.
I think I did these match ups when we were working on the HL2 Importer
because Valve had changed some of those names.
HL1 Classes                                                     HL2 Classes
============                                                    ============
HL1 Matches                 STORED IN               --DONE->    HL2 Matches                     STORED IN
                            class, list                                                         class, list
-----------                 ---------               --------    -----------                     ---------
class mdl_bone              mdl_obj, bones          X           class HL2_Bone                  Object, bones
class mdl_bone_control      mdl_obj, bone_controls  X           class HL2_BoneController        Object, bone_controls
class mdl_hitbox            mdl_obj, hitboxes       X           class HL2_HitBox                HL2_HitBoxSet, bboxgroup
class mdl_attachment        mdl_obj, attachments    X           class HL2_LocalAttachment       Object, attachments
class mdl_bodypart          mdl_obj, bodyparts      X           class HL2_BodyPartIndex         Object, bodyparts
class mdl_model             bodyparts, models       X           class HL2_Model                 bodyparts, models
class mdl_mesh              models, meshes          X           class HL2_Mesh                  models, meshes
class mdl_sequence_desc     mdl_obj, sequence_descs X           class HL2_LocalAnimDesc         Object, animation_descs
class mdl_bone_anim_value                           X           class HL2_AnimValue     used by HL2_AnimValuePtr

class mdl_obj                                       X           class Object    #### SEE OTHER HL IMPORTER USE THIS AS WORD SEARCH
                                               
No Match Yet
------------
                                        class HL2_ANIStudioAnim (called from our anim dialog in class Object, def load_Animation), if ani_file is not None:
                                        class HL2_AnimValuePtr (pointers for Rot & Pos using 'class HL2_AnimValue' below).

class mdl_skin_info                     class HL2_TexturesInfo          LOADED AND USED
class mdl_bone_anim
                                        class HL2_StudioMovement        LOADED BUT NOT USED
class mdl_demand_hdr_group NOT USED
                                        class HL2_LocalSeqDesc          LOADED BUT NOT USED
class mdl_demand_group                  class HL2_AnimBlock             LOADED AND USED
class mdl_events                        class HL2_EyeBall               LOADED AND USED
class mdl_pivots
                                        class HL2_Node                  LOADED BUT NOT USED
                                        class HL2_FlexDesc              LOADED BUT NOT USED
                                        class HL2_FlexController        LOADED BUT NOT USED
                                        class HL2_FlexOp                LOADED BUT NOT USED
                                        class HL2_FlexRule              LOADED BUT NOT USED
                                        class HL2_IKLink                LOADED AND USED
                                        class HL2_IKChain               LOADED AND USED
                                        class HL2_Mouth                 LOADED BUT NOT USED
                                        class HL2_LocalPoseParameter    LOADED BUT NOT USED
                                        class HL2_SurfaceProp           LOADED BUT NOT USED
                                        class HL2_KeyValues             LOADED BUT NOT USED

                                        class HL2_LocalIKAutoplayLock   LOADED BUT NOT USED
                                        class HL2_ModelGroup            LOADED BUT NOT USED

class mdl_triangle                      class HL2_VVDFileReader         LOADED AND USED
class mdl_vert_info                     class HL2_VVDFixup              LOADED AND USED
class mdl_vertex                        class HL2_VTXFileReader         LOADED AND USED

                                        class Tags # load the tag info  LOADED BUT NOT USED, attributes origin & axis don't exist...not in binaryFormat or read in???

IN HL1 ONLY                             IN HL2 ONLY (ALL USED)
-----------                             -----------
                                        class HL2_HitBoxSet (CONTAINS class HL2_HitBox)         mdl_obj, hitboxsets
                                        class Quaternion48
                                        class Vector48
"""


Info = {
   "plug-in":       "ie_md0_HL2_export",
   "desc":          "This script exports a Half-Life 2 file (MDL), textures, and animations from QuArK.",
   "date":          "March 24, 2012",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 5" }

import struct, sys, os, time, operator, math
import quarkx
from quarkpy.qutils import *
import quarkpy.mdleditor
from types import *
import quarkpy.mdlutils
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings
from quarkpy.qeditor import MapColor # Strictly needed for QuArK bones MapColor call.

# Globals
logging = 0
exportername = "ie_md0_HL2_export.py"
textlog = "HL2mdl_ie_log.txt"
progressbar = None
mdl = None
MAX_QPATH = 64
SpecsList = """ """
SpecsList2 = """ """
ani_dlg = None
possible_files = ["_animations", "_anims", "_gestures", "_postures"]
QuArK_bones = []

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
def matrix2euler(matrix):
    # Return Euler angles from rotation matrix for specified axis sequence.
    M = matrix
    cy = math.sqrt(M[0][0]*M[0][0] + M[1][0]*M[1][0])
    if cy < 0.001:
        ax = math.atan2(-M[1][2], M[1][1])
        ay = math.atan2(-M[2][0], cy)
        az = 0.0
    else:
        ax = math.atan2( M[2][1], M[2][2])
        ay = math.atan2(-M[2][0], cy)
        az = math.atan2( M[1][0], M[0][0])

    return [ax, ay, az]


def ConvertToHL1AnimData(data):
    #Special case: if all zeroes, there's no data to store!
    AllZeroes = 1
    for number in data:
        if number != 0:
            AllZeroes = 0
            break
    if AllZeroes:
        return ""

    result = []
    valid = 0
    total = 0
    value = 40000 #Note: Make sure this number is out-of-range of a 'signed short integer'
    chain = []
    repeating = 0
    for i in xrange(len(data)):
        if data[i] != value:
            if repeating:
                x = mdl_bone_anim_value()
                x.set_valid_total(valid, total)
                result += [x]
                result += chain
                chain = []
                valid = 0
                total = 0
                repeating = 0
            x = mdl_bone_anim_value()
            x.set_value(data[i])
            value = data[i]
            chain += [x]
            valid += 1
            total += 1
        else:
            repeating = 1
            total += 1
        if total == 255: #Max length
            x = mdl_bone_anim_value()
            x.set_valid_total(valid, total)
            result += [x]
            result += chain
            chain = []
            valid = 0
            total = 0
            repeating = 0

    if total != 0: #Save last bit of data
        x = mdl_bone_anim_value()
        x.set_valid_total(valid, total)
        result += [x]
        result += chain
        chain = []
        valid = 0
        total = 0
        repeating = 0

    # Convert to struct.pack-ed data
    final_result = ""
    for x in result:
        final_result += x.data
    return final_result


def mesh_normals(comp_name, faces, verts, bones, num_bones):
    norms = []
    norms_infos = []
    vec_null = quarkx.vect(0.0, 0.0, 0.0)
   # v_normals = dict([(verts[index], vec_null) for index in range(len(verts))])
    dict = {}
    for index in range(len(verts)):
        dict[index] = vec_null
    v_normals = dict
   # f_normals = dict([(f.index, vec_null) for f in faces])
    dict = {}
    for index in range(len(faces)):
        dict[index] = vec_null
    f_normals = dict

    for i,f in enumerate(faces):
        f_index = i
        smooth = 1
        f_dic = f_normals[i]
        f_verts = f

        if len(f_verts) is 3: # Triangle
            v0,v1,v2 = f_verts[:]
            facevtx0, facevtx1, facevtx2 = verts[f_verts[0][0]], verts[f_verts[1][0]], verts[f_verts[2][0]]
            facenormal = ((facevtx1 - facevtx0) ^ (facevtx2 - facevtx0)).normalized * -1
            v0_i,v1_i,v2_i = f_verts[0][0], f_verts[1][0], f_verts[2][0]
            f_no = facenormal
            f_normals[f_index] = f_no
            if smooth:
                v_normals[v0_i] = v_normals[v0_i] + f_no
                v_normals[v1_i] = v_normals[v1_i] + f_no
                v_normals[v2_i] = v_normals[v2_i] + f_no

    #-- Normalize vectors
    for vec in v_normals.itervalues():
        vec = vec.normalized
        normal = vec.tuple
        norm = mdl_norm()
        norm.v = [normal[0], normal[1], normal[2]]
        norms.append(norm)

    for i in xrange(0, len(norms)):
        norm_info = mdl_norm_info()
        for j in xrange(0, num_bones):
            if bones[j].vtxlist.has_key(comp_name):
                if i in bones[j].vtxlist[comp_name]:
                    norm_info.bone_index = j
                    break
        norms_infos.append(norm_info)

    return norms, norms_infos


# important values: offset, headerlength, width, height and colordepth
# This is for a Windows Version 3 DIB header
bmp_header = {'mn1':66,
              'mn2':77,
              'filesize':0,
              'undef1':0,
              'undef2':0,
              'offset':54,
              'headerlength':40,
              'width':0,
              'height':0,
              'colorplanes':0,
              'colordepth':24,
              'compression':0,
              'imagesize':0,
              'res_hor':0,
              'res_vert':0,
              'palette':0,
              'importantcolors':0}


# It takes a header (based on bmp_header), 
# the pixel data (from structs, as produced by get_color and row_padding),
# and writes it to filename
def make_bmp_header(header):
    header_str = ""
    header_str += struct.pack('<B', header['mn1'])
    header_str += struct.pack('<B', header['mn2'])
    header_str += struct.pack('<L', header['filesize'])
    header_str += struct.pack('<H', header['undef1'])
    header_str += struct.pack('<H', header['undef2'])
    header_str += struct.pack('<L', header['offset'])
    header_str += struct.pack('<L', header['headerlength'])
    header_str += struct.pack('<L', header['width'])
    header_str += struct.pack('<L', header['height'])
    header_str += struct.pack('<H', header['colorplanes'])
    header_str += struct.pack('<H', header['colordepth'])
    header_str += struct.pack('<L', header['compression'])
    header_str += struct.pack('<L', header['imagesize'])
    header_str += struct.pack('<L', header['res_hor'])
    header_str += struct.pack('<L', header['res_vert'])
    header_str += struct.pack('<L', header['palette'])
    header_str += struct.pack('<L', header['importantcolors'])
    return header_str


######################################################
# Tri-Strip/Tri-Fan functions
######################################################
class mdl_face:
    vertex_index = []
    texture_uv = [[0,0], [0,0], [0,0]]

    def __init__(self):
        self.vertex_index = [0, 0, 0]
        self.texture_uv = [[0,0], [0,0], [0,0]]

    def dump (self):
        global tobj, logging
        tobj.logcon ("vertex indexes: " + str(self.vertex_index[0]) + ", " + str(self.vertex_index[1]) + ", " + str(self.vertex_index[2]))
        tobj.logcon ("texture indexes: " + str(self.texture_uv[0]) + ", " + str(self.texture_uv[1]) + ", " + str(self.texture_uv[2]))
        tobj.logcon ("----------------------------------------")


def find_strip_length(mesh, start_tri, start_vert):
    #variables shared between fan and strip functions
    global used
    global strip_vert
    global strip_st
    global strip_tris
    global strip_count

    m1=m2=0
    st1=st2=0
    
    used[start_tri]=2

    last=start_tri

    strip_vert[0]=mesh.faces[last].vertex_index[start_vert%3]
    strip_vert[1]=mesh.faces[last].vertex_index[(start_vert+1)%3]
    strip_vert[2]=mesh.faces[last].vertex_index[(start_vert+2)%3]

    strip_st[0]=mesh.faces[last].texture_uv[start_vert%3]
    strip_st[1]=mesh.faces[last].texture_uv[(start_vert+1)%3]
    strip_st[2]=mesh.faces[last].texture_uv[(start_vert+2)%3]

    strip_tris[0]=start_tri
    strip_count=1

    m1=mesh.faces[last].vertex_index[(start_vert+2)%3]
    st1=mesh.faces[last].texture_uv[(start_vert+2)%3]
    m2=mesh.faces[last].vertex_index[(start_vert+1)%3]
    st2=mesh.faces[last].texture_uv[(start_vert+1)%3]
    
    #look for matching triangle
    check=start_tri+1
    
    for tri_counter in range(start_tri+1, mesh.numtris):
        
        for k in range(0,3):
            if mesh.faces[check].vertex_index[k]!=m1:
                continue
            if str(mesh.faces[check].texture_uv[k])!=str(st1):
                continue
            if mesh.faces[check].vertex_index[(k+1)%3]!=m2:
                continue
            if str(mesh.faces[check].texture_uv[(k+1)%3])!=str(st2):
                continue
            
            #if we can't use this triangle, this tri_strip is done
            if (used[tri_counter]!=0):
                for clear_counter in range(start_tri+1, mesh.numtris):
                    if used[clear_counter]==2:
                        used[clear_counter]=0
                return strip_count

            #new edge
            if (strip_count & 1):
                m2=mesh.faces[check].vertex_index[(k+2)%3]
                st2=mesh.faces[check].texture_uv[(k+2)%3]
            else:
                m1=mesh.faces[check].vertex_index[(k+2)%3]
                st1=mesh.faces[check].texture_uv[(k+2)%3]

            strip_vert[strip_count+2]=mesh.faces[tri_counter].vertex_index[(k+2)%3]
            strip_st[strip_count+2]=mesh.faces[tri_counter].texture_uv[(k+2)%3]
            strip_tris[strip_count]=tri_counter
            strip_count+=1
    
            used[tri_counter]=2
        check+=1
    return strip_count


def find_fan_length(mesh, start_tri, start_vert):
    #variables shared between fan and strip functions
    global used
    global strip_vert
    global strip_st
    global strip_tris
    global strip_count

    m1=m2=0
    st1=st2=0
    
    used[start_tri]=2

    last=start_tri

    strip_vert[0]=mesh.faces[last].vertex_index[start_vert%3]
    strip_vert[1]=mesh.faces[last].vertex_index[(start_vert+1)%3]
    strip_vert[2]=mesh.faces[last].vertex_index[(start_vert+2)%3]
    
    strip_st[0]=mesh.faces[last].texture_uv[start_vert%3]
    strip_st[1]=mesh.faces[last].texture_uv[(start_vert+1)%3]
    strip_st[2]=mesh.faces[last].texture_uv[(start_vert+2)%3]

    strip_tris[0]=start_tri
    strip_count=1

    m1=mesh.faces[last].vertex_index[(start_vert+0)%3]
    st1=mesh.faces[last].texture_uv[(start_vert+0)%3]
    m2=mesh.faces[last].vertex_index[(start_vert+2)%3]
    st2=mesh.faces[last].texture_uv[(start_vert+2)%3]

    #look for matching triangle    
    check=start_tri+1
    for tri_counter in range(start_tri+1, mesh.numtris):
        for k in range(0,3):
            if mesh.faces[check].vertex_index[k]!=m1:
                continue
            if str(mesh.faces[check].texture_uv[k])!=str(st1):
                continue
            if mesh.faces[check].vertex_index[(k+1)%3]!=m2:
                continue
            if str(mesh.faces[check].texture_uv[(k+1)%3])!=str(st2):
                continue
            
            #if we can't use this triangle, this tri_strip is done
            if (used[tri_counter]!=0):
                for clear_counter in range(start_tri+1, mesh.numtris):
                    if used[clear_counter]==2:
                        used[clear_counter]=0
                return strip_count

            #new edge
            m2=mesh.faces[check].vertex_index[(k+2)%3]
            st2=mesh.faces[check].texture_uv[(k+2)%3]
            
            strip_vert[strip_count+2]=m2
            strip_st[strip_count+2]=st2
            strip_tris[strip_count]=tri_counter
            strip_count+=1
    
            used[tri_counter]=2
        check+=1
    return strip_count


######################################################
# Globals & classes for GL command list calculations
######################################################
used=[]
strip_vert=0
strip_st=0
strip_tris=0
strip_count=0

class glGLCommands_t:
                            #item of data file, size & type,   description
    TrisTypeNum=0           #item  0   short, fan or strip indicator & number of mesh mdl_triangle vertexes.
    cmd_list=[]
    binary_format="<h" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.TrisTypeNum=0
        self.cmd_list=[]

    def save(self, file):
        # data[0] ex: (4) or (-7), positive int = a triangle strip, negative int = a triangle fan, 0 = end of valid GL_commands data.
        #             The value gives the number of mesh mdl_triangle vertexes that make up the strip or fan.
        data=struct.pack(self.binary_format, self.TrisTypeNum)
        file.write(data)
        for cmd in self.cmd_list: # This is a list of mesh mdl_triangle vertexes.
            cmd.save(file)

    def dump(self):
        print "-------------------"
        print "MDL OpenGL Command Structure"
        print "tris_group: ", self.TrisTypeNum
        print "-------------------"
        for cmd in self.cmd_list:
            cmd.dump()


######################################################
# Build GL command List
######################################################
def build_GL_commands(mesh, mesh_bytes_count):
    #variables shared between fan and strip functions
    global used
    used=[0]*mesh.numtris
    global strip_vert
    strip_vert=[0]*128
    global strip_st
    strip_st=[[0,0]]*128
    global strip_tris
    strip_tris=[0]*128
    global strip_count
    strip_count=0

    #variables
    start_vert=0
    fan_length=strip_length=0
    length=best_length=0
    best_type=0
    best_vert=[0]*1024
    best_st=[[0,0]]*1024
    best_tris=[0]*1024

    for face_counter in range(0,mesh.numtris):
        if used[face_counter]==1: #don't evaluate a tri that's been used
            pass
        else:
            best_length=0 #restart the counter
            #for each vertex index in this face
            for start_vert in range(0,3):
                strip_length=find_strip_length(mesh, face_counter, start_vert)
                if (strip_length>best_length): 
                    best_type=0
                    best_length=strip_length
                    for index in range (0, best_length+2):
                        best_st[index]=strip_st[index]
                        best_vert[index]=strip_vert[index]
                    for index in range(0, best_length):
                        best_tris[index]=strip_tris[index]

                fan_length=find_fan_length(mesh, face_counter, start_vert)
                if (fan_length>best_length):
                    best_type=1
                    best_length=fan_length
                    for index in range (0, best_length+2):
                        best_st[index]=strip_st[index]
                        best_vert[index]=strip_vert[index]
                    for index in range(0, best_length):
                        best_tris[index]=strip_tris[index]

            #mark the tris on the best strip/fan as used
            for used_counter in range (0, best_length):
                used[best_tris[used_counter]]=1

            temp_cmdlist=glGLCommands_t()
            mesh_bytes_count += 2 # 2 = class glGLCommands_t binary_format.
            #push the number of commands into the command stream
            if best_type==1:
                temp_cmdlist.TrisTypeNum=(-(best_length+2))
            else:
                temp_cmdlist.TrisTypeNum=best_length+2
            for command_counter in range (0, best_length+2):
                #emit a vertex into the reorder buffer
                cmd=mdl_triangle()
                mesh_bytes_count += 8 # 8 = class mdl_triangle binary_format.
                #put S/T (also known as U/V) coords in the structure
                st=best_st[command_counter]
                cmd.index2u=st[0]
                cmd.index3v=st[1]
                cmd.index0vert=best_vert[command_counter]
                cmd.index1uv=cmd.index0vert
                temp_cmdlist.cmd_list.append(cmd)
            mesh.triangles.append(temp_cmdlist)

    #end of list
    temp_cmdlist=glGLCommands_t()
    mesh_bytes_count += 2 # 2 = class glGLCommands_t binary_format.
    temp_cmdlist.TrisTypeNum=0
    mesh.triangles.append(temp_cmdlist)

    #cleanup and return
    used=best_vert=best_st=best_tris=strip_vert=strip_st=strip_tris=0
    return mesh_bytes_count


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
    bonecontroller = [-1]*6 #item  34-39  6 int, bone controller index, -1 == none
    value = [0.0]*6        #item  40-45  6 floats, default DoF values
    scale = [0.0]*6        #item  46-51  6 floats, scale for delta DoF values

    binary_format = "<32sii6i6f6f" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bone_index = 0
        self.name = ""
        self.parent = 0
        self.flags = 0
        self.bonecontroller = [-1]*6
        self.value = [0.0]*6
        self.scale = [0.0]*6

    def save(self, file):
        tD = [0]*21
        tD[0] = self.name
        tD[1] = self.parent
        tD[2] = self.flags
        tD[3] = self.bonecontroller[0]
        tD[4] = self.bonecontroller[1]
        tD[5] = self.bonecontroller[2]
        tD[6] = self.bonecontroller[3]
        tD[7] = self.bonecontroller[4]
        tD[8] = self.bonecontroller[5]
        tD[9] = self.value[0]
        tD[10] = self.value[1]
        tD[11] = self.value[2]
        tD[12] = self.value[3]
        tD[13] = self.value[4]
        tD[14] = self.value[5]
        tD[15] = self.scale[0]
        tD[16] = self.scale[1]
        tD[17] = self.scale[2]
        tD[18] = self.scale[3]
        tD[19] = self.scale[4]
        tD[20] = self.scale[5]
        data = struct.pack(self.binary_format, tD[0], tD[1], tD[2], tD[3], tD[4], tD[5], tD[6], tD[7], tD[8], tD[9], tD[10], tD[11], tD[12], tD[13], tD[14], tD[15], tD[16], tD[17], tD[18], tD[19], tD[20])
        file.write(data)

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

    def save(self, file):
        tmpData = [0]*6
        tmpData[0] = self.bone
        tmpData[1] = self.type
        tmpData[2] = self.start
        tmpData[3] = self.end
        tmpData[4] = self.rest
        tmpData[5] = self.index
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5])
        file.write(data)

    def dump(self):
        print "MDL Bone Control"
        print "bone: ", self.bone
        print "type: ", self.type
        print "start: ", self.start
        print "end: ", self.end
        print "rest: ", self.rest
        print "index: ", self.index
        print "===================="


class HL2_HitBoxSet:
    #Header Structure      #item of file, type, description.
    sznameindex = 0        #item   0      int, the bone's index.
    numhitboxes = 0        #item   1      int, number of hit boxes in the set.
    hitboxindex = 0        #item   2      int, hit boxes data index offset.
    pszName = "Default"    #item   3      32 char, the bone's name.

    binary_format="<3i" # data_read_in = 3i = 3*4 = 12

    def __init__(self):
        self.sznameindex = 0
        self.numhitboxes = 0
        self.hitboxindex = 0
        self.pszName = "default"

    def save(self, file, QuArK_bones, hitboxes):
        self.sznameindex = file.tell() + 12 + (len(hitboxes) * 68) + 32
        self.numhitboxes = len(hitboxes)
        self.hitboxindex = 12
        tmpData = [0]*3
        tmpData[0] = self.sznameindex
        tmpData[1] = self.numhitboxes
        tmpData[2] = self.hitboxindex
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2])
        file.write(data)

        for i in xrange(self.numhitboxes):
            bbox = hitboxes[i]
            bbox.save(file)
            # bbox.dump()

        binary_format="<32s"
        # Write the bbox name (same for all of them).
        data = struct.pack(binary_format, bbox.HitBoxName)
        file.write(data)

        # Write the HL2_HitBoxSet name.
        data = struct.pack(binary_format, self.pszName)
        file.write(data)

    def dump(self):
        print "==============HL2_HITBOXSET=============="
        print "sznameindex: ", self.sznameindex
        print "numhitboxes: ", self.numhitboxes
        print "hitboxindex: ", self.hitboxindex
        print "pszName: ", self.pszName


class mdl_hitbox:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiobbox_t
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

    binary_format = "<2i3f3fi8i" #little-endian (<), see #item descriptions above.

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

    def save(self, file):
        tmpData = [0]*17
        tmpData[0] = self.bone
        tmpData[1] = self.group
        tmpData[2] = self.bbmin[0]
        tmpData[3] = self.bbmin[1]
        tmpData[4] = self.bbmin[2]
        tmpData[5] = self.bbmax[0]
        tmpData[6] = self.bbmax[1]
        tmpData[7] = self.bbmax[2]
        tmpData[8] = self.szhitboxnameindex
        tmpData[9] = self.unused1
        tmpData[10] = self.unused2
        tmpData[11] = self.unused3
        tmpData[12] = self.unused4
        tmpData[13] = self.unused5
        tmpData[14] = self.unused6
        tmpData[15] = self.unused7
        tmpData[16] = self.unused8
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12], tmpData[13], tmpData[14], tmpData[15], tmpData[16])
        file.write(data)

    def dump(self):
        print "MDL Hitbox"
        print "bone: ", self.bone
        print "group: ", self.group
        print "bbmin: ", self.bbmin
        print "bbmax: ", self.bbmax
        print "szhitboxnameindex: ", self.szhitboxnameindex
        print "unused1: ", self.unused1
        print "unused2: ", self.unused2
        print "unused3: ", self.unused3
        print "unused4: ", self.unused4
        print "unused5: ", self.unused5
        print "unused6: ", self.unused6
        print "unused7: ", self.unused7
        print "unused8: ", self.unused8
        print "HitBoxName: ", self.HitBoxName
        print "===================="


class mdl_attachment:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioattachment_t
    #Header Structure      #item of file, type, description.
    name = ""              #item   0-31   32 char, attachment name.
    type = 0               #item   32     int, type of attachment.
    bone = 0               #item   33     int, bone index.
    org = [0.0]*3          #item   34-36  3 floats, attachment point.
    vectors = [[0.0]*3]*3  #item   37-45  3 floats each for 3 vectors.

    binary_format = "<32s2i3f9f" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.name = ""
        self.type = 0
        self.bone = 0
        self.org = [0.0]*3
        self.vectors = [[0.0]*3]*3

    def save(self, file):
        tmpData = [0]*15
        tmpData[0] = self.name
        tmpData[1] = self.type
        tmpData[2] = self.bone
        tmpData[3] = self.org[0]
        tmpData[4] = self.org[1]
        tmpData[5] = self.org[2]
        tmpData[6] = self.vectors[0][0]
        tmpData[7] = self.vectors[0][1]
        tmpData[8] = self.vectors[0][2]
        tmpData[9] = self.vectors[1][0]
        tmpData[10] = self.vectors[1][1]
        tmpData[11] = self.vectors[1][2]
        tmpData[12] = self.vectors[2][0]
        tmpData[13] = self.vectors[2][1]
        tmpData[14] = self.vectors[2][2]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12], tmpData[13], tmpData[14])
        file.write(data)

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
    name = "body"           #item  0-63   64 char, bodypart name.
    nummodels = 0           #item  64     int, number of bodypart models.
    base = 1                #item  65     int, unknown item.
    model_offset = 0        #item  66     int, index (Offset) into models array (data).
    models = []                           # A list containing its models.

    binary_format = "<64s3i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.name = "body"
        self.nummodels = 0
        self.base = 1
        self.model_offset = 0
        self.models = []

    def save(self, file):
        tmpData = [0]*4
        tmpData[0] = self.name
        tmpData[1] = self.nummodels
        tmpData[2] = self.base
        tmpData[3] = self.model_offset
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
        file.write(data)

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

    binary_format = "<64sif10i" #little-endian (<), see #item descriptions above.

    meshes = []                           # List of meshes.
    verts = []                            # List of vertex vector poistions.
    verts_info = []                       # List of vertex bone indexes.
    normals = []                          # List of normal vector poistions.
    groups = []                           # List of groups, unknown items.
    normals_info = []                     # List of normal bone index.

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
        self.normals_info = []

    def save(self, file):
        tmpData = [0]*13
        tmpData[0] = self.name
        tmpData[1] = self.type
        tmpData[2] = self.boundingradius
        tmpData[3] = self.nummesh
        tmpData[4] = self.mesh_offset
        tmpData[5] = self.numverts
        tmpData[6] = self.vert_info_offset
        tmpData[7] = self.vert_offset
        tmpData[8] = self.numnorms
        tmpData[9] = self.norm_info_offset
        tmpData[10] = self.norm_offset
        tmpData[11] = self.numgroups
        tmpData[12] = self.group_offset
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12])
        file.write(data)

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
    faces = []                         # List of mesh_faces, true triangles.

    binary_format = "<5i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.numtris = 0
        self.tri_offset = 0
        self.skinref = 0
        self.numnorms = 0
        self.normindex = 0

        self.triangles = []
        self.normals = []
        self.faces = []

    def save(self, file):
        tmpData = [0]*5
        tmpData[0] = self.numtris
        tmpData[1] = self.tri_offset
        tmpData[2] = self.skinref
        tmpData[3] = self.numnorms
        tmpData[4] = self.normindex
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4])
        file.write(data)

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
    numblends = 1            #item   54     int, unknown item.
    anim_offset = 0          #item   55     int, start (Offset) to the sequence group data ex: [blend][bone][X, Y, Z, XR, YR, ZR].
    blendtype = [0]*2        #item   56-57  2 ints, X, Y or Z and XR, YR or ZR.
    blendstart = [0.0]*2     #item   58-59  2 floats, starting values.
    blendend = [1.0, 0.0]    #item   60-61  2 floats, ending values.
    blendparent = 0          #item   62     int, unknown item.
    seqgroup = 0             #item   63     int, sequence group for demand loading.
    entrynode = 0            #item   64     int, transition node at entry.
    exitnode = 0             #item   65     int, transition node at exit.
    nodeflags = 0            #item   66     int, transition rules.
    nextseq = 0              #item   67     int, auto advancing sequences.
    anim_bones = []                           # A list containing this seq's mdl_bone_anim.

    binary_format = "<32sf10i3f2i6f4i4f6i" #little-endian (<), see #item descriptions above.

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
        self.numblends = 1
        self.anim_offset = 0
        self.blendtype = [0]*2
        self.blendstart = [0.0]*2
        self.blendend = [1.0, 0.0]
        self.blendparent = 0
        self.seqgroup = 0
        self.entrynode = 0
        self.exitnode = 0
        self.nodeflags = 0
        self.nextseq = 0
        self.anim_bones = []

    def save(self, file):
        tD = [0]*37
        tD[0] = self.label
        tD[1] = self.fps
        tD[2] = self.flags
        tD[3] = self.activity
        tD[4] = self.actweight
        tD[5] = self.numevents
        tD[6] = self.event_offset
        tD[7] = self.numframes
        tD[8] = self.numpivots
        tD[9] = self.pivot_offset
        tD[10] = self.motiontype
        tD[11] = self.motionbone
        tD[12] = self.linearmovement[0]
        tD[13] = self.linearmovement[1]
        tD[14] = self.linearmovement[2]
        tD[15] = self.automoveposindex
        tD[16] = self.automoveangleindex
        tD[17] = self.bbmin[0]
        tD[18] = self.bbmin[1]
        tD[19] = self.bbmin[2]
        tD[20] = self.bbmax[0]
        tD[21] = self.bbmax[1]
        tD[22] = self.bbmax[2]
        tD[23] = self.numblends
        tD[24] = self.anim_offset
        tD[25] = self.blendtype[0]
        tD[26] = self.blendtype[1]
        tD[27] = self.blendstart[0]
        tD[28] = self.blendstart[1]
        tD[29] = self.blendend[0]
        tD[30] = self.blendend[1]
        tD[31] = self.blendparent
        tD[32] = self.seqgroup
        tD[33] = self.entrynode
        tD[34] = self.exitnode
        tD[35] = self.nodeflags
        tD[36] = self.nextseq
        data = struct.pack(self.binary_format, tD[0], tD[1], tD[2], tD[3], tD[4], tD[5], tD[6], tD[7], tD[8], tD[9], tD[10], tD[11], tD[12], tD[13], tD[14], tD[15], tD[16], tD[17], tD[18], tD[19], tD[20], tD[21], tD[22], tD[23], tD[24], tD[25], tD[26], tD[27], tD[28], tD[29], tD[30], tD[31], tD[32], tD[33], tD[34], tD[35], tD[36])
        file.write(data)

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
    #valid = 0               #item  0     unsigned char int, 1 byte.
    #total = 0               #item  1     unsigned char int, 1 byte.
    #value = 0               #item  0+1   signed short int, 2 bytes.

    #Please use the set_valid_total and set_value functions!
    data = ""

    #This is a C++ union (two different ways to read the same bitstream); we'll do both at the same time
    binary_format1 = "<2B" #little-endian (<), see #item descriptions above.
    binary_format2 = "<h" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.data = ""

    def set_valid_total(self, valid, total):
        self.data = struct.pack(self.binary_format1, valid, total)

    def set_value(self, value):
        self.data = struct.pack(self.binary_format2, value)

    def save(self, file):
        #Note: This function is actually not used; see ConvertToHL1AnimData
        file.write(self.data)

    def dump(self):
        print "MDL Anim Frames"
        print "data: ", self.data
        print "===================="


class HL2_TexturesInfo: # Was mdl_skin_info in HL1.
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
    binary_format="<i64s15i"  #little-endian (<), see #item descriptions above.

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
        self.binary_format="<i64s15i"  #little-endian (<), see #item descriptions above.
        self.data_read_in = 64 # Total binary_format byte value above, used below to set the file offset pointer back.

    def save(self, file):
        tmpData = [0]*17
        tmpData[0] = self.sznameindex
        tmpData[1] = self.pszName
        tmpData[2] = self.flags
        tmpData[3] = self.used
        tmpData[4] = self.unknown
        tmpData[5] = self.material
        tmpData[6] = self.clientmaterial
        tmpData[7] = self.unused1
        tmpData[8] = self.unused2
        tmpData[9] = self.unused3
        tmpData[10]= self.unused4
        tmpData[11]= self.unused5
        tmpData[12]= self.unused6
        tmpData[13]= self.unused7
        tmpData[14]= self.unused8
        tmpData[15]= self.unused9
        tmpData[16]= self.unused10
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12], tmpData[13], tmpData[14], tmpData[15], tmpData[16])
        file.write(data)

    def dump(self):
        print "MDL Skin"
        print "sznameindex: ", self.sznameindex
        print "pszName: ", self.pszName
        print "flags: ", self.flags
        print "used: ", self.used
        print "unknown: ", self.unknown
        print "material: ", self.material
        print "clientmaterial: ", self.clientmaterial
        print "unused1: ", self.unused1
        print "unused2: ", self.unused2
        print "unused3: ", self.unused3
        print "unused4: ", self.unused4
        print "unused5: ", self.unused5
        print "unused6: ", self.unused6
        print "unused7: ", self.unused7
        print "unused8: ", self.unused8
        print "unused9: ", self.unused9
        print "unused10: ", self.unused10
        print "--------------------"


class mdl_bone_anim:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudioanim_t
                            #item of data file, size & type,   description
    offset = [0]*6          #item  0-5   6 unsigned short ints, file offsets to read animation data for bone(s) for EACH SET of ANIMATION FRAMES sequences.

    binary_format = "<6H" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.offset = [0]*6

    def save(self, file):
        tmpData = [0]*6
        tmpData[0] = self.offset[0]
        tmpData[1] = self.offset[1]
        tmpData[2] = self.offset[2]
        tmpData[3] = self.offset[3]
        tmpData[4] = self.offset[4]
        tmpData[5] = self.offset[5]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5])
        file.write(data)

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

    def save(self, file):
        tmpData = [0]*4
        tmpData[0] = self.index0vert
        tmpData[1] = self.index1uv
        tmpData[2] = self.index2u
        tmpData[3] = self.index3v
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
        file.write(data)

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

    def save(self, file):
        tmpData = [0]
        tmpData[0] = self.bone_index
        data = struct.pack(self.binary_format, tmpData[0])
        file.write(data)

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

    def save(self, file):
        tmpData = [0]*3
        tmpData[0] = self.v[0]
        tmpData[1] = self.v[1]
        tmpData[2] = self.v[2]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2])
        file.write(data)
                        
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
    label = "default"       #item  0-31   32 char, group label
    name = ""               #item  32-95  64 char, group name
    cache = 0               #item  96     int, cache index pointer
    data = 0                #item  97     int, hack for group 0

    binary_format = "<32s64s2i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.label = "default"
        self.name = ""
        self.cache = 0
        self.data = 0

    def save(self, file):
        tmpData = [0]*4
        tmpData[0] = self.label
        tmpData[1] = self.name
        tmpData[2] = self.cache
        tmpData[3] = self.data
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
        file.write(data)

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


class mdl_norm_info: # Gives a bone_index for each Component's normal that is assigned to that bone.
    bone_index = 0
    binary_format = "<B" #little-endian (<), 1 single byte (unsigned int).

    def __init__(self):
        self.bone_index = 0

    def save(self, file):
        tmpData = [0]
        tmpData[0] = self.bone_index
        data = struct.pack(self.binary_format, tmpData[0])
        file.write(data)

    def dump(self, bodypart, model, norm):
        print "MDL Normal Info for, bodypart, model, norm:", bodypart, model, norm
        print "bone_index: ",self.bone_index
        print "===================="

class mdl_norm: # Gives each normal's x,y,z position.
    v = [0.0]*3
    binary_format = "<3f" #little-endian (<), 3 floats.

    def __init__(self):
        self.v = [0.0]*3

    def save(self, file):
        tmpData = [0]*3
        tmpData[0] = self.v[0]
        tmpData[1] = self.v[1]
        tmpData[2] = self.v[2]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2])
        file.write(data)
                        
    def dump(self):
        print "MDL Normal"
        print "v: ",self.v[0], self.v[1], self.v[2]
        print "===================="


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
              #  value = m_controller[i] / 255.0
                value = m_controller[i]
                if (value < 0):
                    value = 0.0
                elif (value > 1.0):
                    value = 1.0
              #  value = (1.0 - value) * pbonecontroller.start + value * pbonecontroller.end
        else:
            value = m_mouth / 64.0
            if (value > 1.0):
                value = 1.0
            value = (1.0 - value) * pbonecontroller.start + value * pbonecontroller.end

        if ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_XR) \
        or ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_YR) \
        or ((pbonecontroller.type & STUDIO_TYPES) == STUDIO_ZR):
            if i == 0:
                m_adj += [value * (math.pi / 180.0)]
            else:
                m_adj += [value]
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
                    animvalue = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    panimvalueX = panimvalue + (k+2) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue2 = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += (animvalue.value * (1.0 - s) + s * animvalue2.value) * bone.scale[i]
                else:
                    panimvalueX = panimvalue + (k+1) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += animvalue.value * bone.scale[i]
            else:
                # are we at the end of the repeating values section and there's another section with data?
                if (animvalue.total <= k + 1):
                    panimvalueX = panimvalue + (animvalue.valid) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    panimvalueX = panimvalue + (animvalue.valid+2) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue2 = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += (animvalue.value * (1.0 - s) + s * animvalue2.value) * bone.scale[i]
                else:
                    panimvalueX = panimvalue + (animvalue.valid) * struct.calcsize(mdl_bone_anim_value.binary_format1)
                    animvalue = Read_mdl_bone_anim_value(self, file, panimvalueX)
                    pos[i] += animvalue.value * bone.scale[i]
        if (bone.bonecontroller[i] != -1):
            pos[i] += m_adj[bone.bonecontroller[i]]

    return pos


######################################################
# FILL MDL DATA STRUCTURE
######################################################

def fill_mdl(dlg):
    # Fill the mdl_obj header values.
    print "line 1705 dlg", dlg
    name = dlg.mdlfile.name.replace("\\", "/")
    name = name.split("/")
    name = name[len(name)-1]
    mdl.name = name
    mdl.length = 407 # class mdl_obj binary_format, the .mdl file header.

    if dlg.src['MakeMainMDL'] is not None or ani_dlg is not None:
        if ani_dlg is None:
            mdl.eyeposition[2] = 65.0
        mdl.illumposition = [4.0, .64, 32]
        # mdl.hull_min and mdl.hull_max computed in "Sort the frames per sequence" or "export all the animation data" section below.

        ### OFFSET FOR BONES SECTION.
        mdl.boneindex = mdl.length

        mdl.QuArK_bones = QuArK_bones
        mdl.num_bones = len(mdl.QuArK_bones)

        ### OFFSET FOR BONES_CONTROLS SECTION.
        mdl.bone_controls_offset = mdl.boneindex + (mdl.num_bones * 112) # 112 = class mdl_bone binary_format.

        # Setup quick cross reference dictionary lists.
        QuArK_bone_name2bone_index = {}
        for i in xrange(0, mdl.num_bones):
            QuArK_bone = mdl.QuArK_bones[i]
            QuArK_bone_name2bone_index[QuArK_bone.name] = i # Fill this quick cross reference dictionary list.

        for i in xrange(0, mdl.num_bones):
            bone = mdl_bone()
            bone.bone_index = i
            QuArK_bone = mdl.QuArK_bones[i]
            bone.name = QuArK_bone.shortname.replace(dlg.comp_group, "")
            bone.parent = -1
            parent = QuArK_bone.dictspec['parent_name']
            parent_matrix = None
            if QuArK_bone_name2bone_index.has_key(parent):
                bone.parent = QuArK_bone_name2bone_index[parent]
                parent_bone = mdl.QuArK_bones[bone.parent]
                parent_pos = parent_bone.position
                parent_matrix = parent_bone.rotmatrix
            if QuArK_bone.dictspec.has_key('control_type'):
                bone_conttrol = mdl_bone_control()
                bone_conttrol.bone = i
                bone_conttrol.type = int(QuArK_bone.dictspec['control_type'])
                bone_conttrol.start = float(QuArK_bone.dictspec['control_start'])
                bone_conttrol.end = float(QuArK_bone.dictspec['control_end'])
                bone_conttrol.rest = int(QuArK_bone.dictspec['control_rest'])
                bone_conttrol.index = int(QuArK_bone.dictspec['control_index'])
                bone.bonecontroller[3] = bone_conttrol.index
                mdl.bone_controls.append(bone_conttrol)
            mdl.num_bone_controls = len(mdl.bone_controls)

            if parent != "None":
                pos = (~parent_matrix * (QuArK_bone.position - parent_pos)).tuple
                m = ~parent_matrix * QuArK_bone.rotmatrix
                m = m.tuple
            else:
                pos = QuArK_bone.position.tuple
                m = QuArK_bone.rotmatrix
                m = m.tuple
            m = [[m[0][0],m[0][1],m[0][2],0], [m[1][0],m[1][1],m[1][2],0], [m[2][0],m[2][1],m[2][2],0], [0,0,0,1]]
            ang = matrix2euler(m)
            bone.value = [pos[0], pos[1], pos[2], ang[0], ang[1], ang[2]]
            scale = 0.0039063692092895508
            bone.scale = [scale, scale, scale, 0.00001, 0.00001, 0.00001]
            mdl.bones.append(bone)

        ### OFFSET FOR ATTACHMENTS SECTION.
        mdl.localattachmentindex = mdl.bone_controls_offset + (mdl.num_bone_controls * 24) # 24 = class mdl_bone_control binary_format.

        if dlg.src['Tags'] is not None:
            for tag in dlg.tags:
                bone_name = tag.dictspec['bone']
                Tpos = None
                for tagframe in tag.subitems:
                    if tagframe.name.find("baseframe") != -1:
                        Tpos = quarkx.vect(tagframe.dictspec['origin'])
                        break
                if Tpos is not None:
                    for i in xrange(0, mdl.num_bones):
                        if mdl.QuArK_bones[i].name == bone_name:
                            bone_pos = mdl.QuArK_bones[i].position
                            bone_matrix = mdl.QuArK_bones[i].rotmatrix
                            attachment = mdl_attachment()
                            attachment.bone = i
                            attachment.org = (~bone_matrix * (Tpos - bone_pos)).tuple
                            mdl.attachments.append(attachment)
                            break
        mdl.numlocalattachments = len(mdl.attachments)

        ### OFFSET FOR HITBOXES SECTION.
        mdl.hitboxsetindex = mdl.localattachmentindex + (mdl.numlocalattachments * 88) # 88 = class mdl_attachment binary_format.

        bone_to_hitbox_data = {} #Store the hitbox data; we need it for bbox calc for the animation sequence later
        szhitboxnameindex = mdl.hitboxsetindex + 12 + (len(mdl.hitboxes) * 68)
        if dlg.src['BBoxes'] is not None:
            count = 0
            for key in dlg.bboxlist.keys():
                name = key.split(":p")[0]
                for i in xrange(0, mdl.num_bones):
                    if mdl.QuArK_bones[i].shortname == name:
                        size = dlg.bboxlist[key]['size']
                        hitbox = mdl_hitbox()
                        hitbox.bone = i
                        hitbox.bbmin = size[0]
                        hitbox.bbmax = size[1]
                        hitbox.szhitboxnameindex = szhitboxnameindex
                        if count == 0:
                            temp = name.split("_")
                            if len(temp) > 1:
                                hitbox.HitBoxName = temp[len(temp)-2]
                            else:
                                hitbox.HitBoxName = temp[0]
                            count += 1
                        mdl.hitboxes.append(hitbox)
                        bone_to_hitbox_data[i] = (quarkx.vect(size[0]), quarkx.vect(size[1]))
                        break

        mdl.hitboxsetindex = mdl.hitboxsetindex + 12 + 32 # class HL2_HitBoxSet binary_format.

        ### OFFSET FOR ANIMATION SEQUENCE_DESC SECTION. (SetUpBones Section in the IMPORTER)
        mdl.localanimindex = mdl.hitboxsetindex + (len(mdl.hitboxes) * 68) + 32 # 68 = class mdl_hitbox binary_format + name at end of them all.

        comp = dlg.comp_list[0]
        comp_framesgroup = comp.dictitems['Frames:fg'].subitems

        #Sort the frames per sequence
        if ani_dlg is None:
            frame_name = comp_framesgroup[0].name
            name = frame_name.split(" ")[0]
            if not mdl.QuArK_anim_seq_frames.has_key(name):
                mdl.numlocalanim = 1
                mdl.QuArK_anim_seq += [name]
                mdl.QuArK_anim_seq_frames[name] = []
            mdl.QuArK_anim_seq_frames[name].append(comp_framesgroup[0])
            bone_min_max = [[]] * mdl.num_bones
            bbmin = None
            bbmax = None
            for j in xrange(0, mdl.num_bones):
                QuArK_bone = mdl.QuArK_bones[j]
                parent = QuArK_bone.dictspec['parent_name']
                if QuArK_bone_name2bone_index.has_key(parent):
                    parent_bone = mdl.QuArK_bones[QuArK_bone_name2bone_index[parent]]
                else:
                    parent_bone = None

                data = [[], [], [], [], [], []]   # X, Y, Z, quatX, quatY, quatZ
                bone_data = editor.ModelComponentList['bonelist'][QuArK_bone.name]['frames']["baseframe:mf"]
                bone_pos = quarkx.vect(bone_data['position'])
                bone_rot = quarkx.matrix(bone_data['rotmatrix'])
                if bone_to_hitbox_data.has_key(j):
                    bmin, bmax = bone_to_hitbox_data[j]
                    bmin = (bone_rot * bmin) + bone_pos
                    bmax = (bone_rot * bmax) + bone_pos
                    bmin = bmin.tuple
                    bmax = bmax.tuple
                    if bbmin is None:
                        bbmin = [bmin[0], bmin[1], bmin[2]]
                    else:
                        if bmin[0] < bbmin[0]:
                            bbmin[0] = bmin[0]
                        if bmin[1] < bbmin[1]:
                            bbmin[1] = bmin[1]
                        if bmin[2] < bbmin[2]:
                            bbmin[2] = bmin[2]
                        if bmin[0] > bbmax[0]:
                            bbmax[0] = bmin[0]
                        if bmin[1] > bbmax[1]:
                            bbmax[1] = bmin[1]
                        if bmin[2] > bbmax[2]:
                            bbmax[2] = bmin[2]
                    if bbmax is None:
                        bbmax = [bmax[0], bmax[1], bmax[2]]
                    else:
                        if bmax[0] < bbmin[0]:
                            bbmin[0] = bmax[0]
                        if bmax[1] < bbmin[1]:
                            bbmin[1] = bmax[1]
                        if bmax[2] < bbmin[2]:
                            bbmin[2] = bmax[2]
                        if bmax[0] > bbmax[0]:
                            bbmax[0] = bmax[0]
                        if bmax[1] > bbmax[1]:
                            bbmax[1] = bmax[1]
                        if bmax[2] > bbmax[2]:
                            bbmax[2] = bmax[2]
                if parent_bone:
                    parent_bone_data = editor.ModelComponentList['bonelist'][parent_bone.name]['frames']["baseframe:mf"]
                    parent_pos = quarkx.vect(parent_bone_data['position'])
                    parent_rot = quarkx.matrix(parent_bone_data['rotmatrix'])

                    bone_pos = ~parent_rot * (bone_pos - parent_pos)
                    bone_rot = ~parent_rot * bone_rot

                bone_pos = bone_pos.tuple
                bone_rot = bone_rot.tuple
                m = matrix2euler(bone_rot)

                data[0] += [bone_pos[0]]
                data[1] += [bone_pos[1]]
                data[2] += [bone_pos[2]]
                data[3] += [m[0]]
                data[4] += [m[1]]
                data[5] += [m[2]]

                #Update the min,max, if needed
                for k in xrange(6):
                    if len(bone_min_max[j]) <= k:
                        #Not yet stored
                        min = data[k][0]
                        max = data[k][0]
                    else:
                        min, max = bone_min_max[j][k]
                    for l in xrange(len(data[k])):
                        if data[k][l] < min:
                            min = data[k][l]
                        if data[k][l] > max:
                            max = data[k][l]
                    if len(bone_min_max[j]) <= k:
                        bone_min_max[j] += [(min, max)]
                    else:
                        bone_min_max[j][k] = (min, max)
            if bbmin is not None:
                if mdl.hull_min[0] == 0 and mdl.hull_min[1] == 0 and mdl.hull_min[2] == 0:
                    mdl.hull_min = bbmin
                print "line 1914 hull_min", mdl.hull_min
            if bbmax is not None:
                if mdl.hull_max[0] == 0 and mdl.hull_max[1] == 0 and mdl.hull_max[2] == 0:
                    mdl.hull_max = bbmax
                print "line 1918 hull_max", mdl.hull_max
        else:
            print "line 1920 SRCsList", len(ani_dlg.SRCsList)
            print ani_dlg.SRCsList
            mdl.numlocalanim = 0
            for i in xrange(0, len(comp_framesgroup)):
                frame_name = comp_framesgroup[i].name
                name = frame_name.split(" ")[0]
                if frame_name.find("baseframe") != -1 or frame_name.find("BaseFrame") != -1 or ani_dlg.src[name] is None:
                    continue
                if not mdl.QuArK_anim_seq_frames.has_key(name):
                    mdl.numlocalanim += 1
                    mdl.QuArK_anim_seq += [name]
                    mdl.QuArK_anim_seq_frames[name] = []
                mdl.QuArK_anim_seq_frames[name].append(comp_framesgroup[i])

        #Now loop over the sequences, and store the animation data
        for name in mdl.QuArK_anim_seq:
            sequence_desc = mdl_sequence_desc()
            sequence_desc.label = name
            #The frame_flags are supposed to be the same for all frames of a single animation sequence; so just take the first frame and use its frame_flags
            frame = mdl.QuArK_anim_seq_frames[name][0]
            if frame.dictspec.has_key('frame_flags') and frame.dictspec['frame_flags'] != "None":
                sequence_desc.flags = int(frame.dictspec['frame_flags'])
            sequence_desc.numframes = len(mdl.QuArK_anim_seq_frames[name])
            for j in xrange(0, mdl.num_bones):
                anim_bone = mdl_bone_anim()
                sequence_desc.anim_bones.append(anim_bone)
            mdl.sequence_descs.append(sequence_desc)

        #Now export all the animation data
        all_data = []
        bone_min_max = [[]] * mdl.num_bones
        for anim_seq in mdl.sequence_descs:
            frames = mdl.QuArK_anim_seq_frames[anim_seq.label]
            print "line 1953 anim_seq.label", anim_seq.label
            bbmin = None
            bbmax = None
            all_bone_data = []
            for j in xrange(0, mdl.num_bones):
                QuArK_bone = mdl.QuArK_bones[j]
                parent = QuArK_bone.dictspec['parent_name']
                if QuArK_bone_name2bone_index.has_key(parent):
                    parent_bone = mdl.QuArK_bones[QuArK_bone_name2bone_index[parent]]
                else:
                    parent_bone = None

                data = [[], [], [], [], [], []]   # X, Y, Z, quatX, quatY, quatZ
                for m_frame in xrange(anim_seq.numframes):
                    bone_data = editor.ModelComponentList['bonelist'][QuArK_bone.name]['frames'][frames[m_frame].name]
                    bone_pos = quarkx.vect(bone_data['position'])
                    bone_rot = quarkx.matrix(bone_data['rotmatrix'])
                    if bone_to_hitbox_data.has_key(j):
                        bmin, bmax = bone_to_hitbox_data[j]
                        bmin = (bone_rot * bmin) + bone_pos
                        bmax = (bone_rot * bmax) + bone_pos
                        bmin = bmin.tuple
                        bmax = bmax.tuple
                        if bbmin is None:
                            bbmin = [bmin[0], bmin[1], bmin[2]]
                        else:
                            if bmin[0] < bbmin[0]:
                                bbmin[0] = bmin[0]
                            if bmin[1] < bbmin[1]:
                                bbmin[1] = bmin[1]
                            if bmin[2] < bbmin[2]:
                                bbmin[2] = bmin[2]
                            if bmin[0] > bbmax[0]:
                                bbmax[0] = bmin[0]
                            if bmin[1] > bbmax[1]:
                                bbmax[1] = bmin[1]
                            if bmin[2] > bbmax[2]:
                                bbmax[2] = bmin[2]
                        if bbmax is None:
                            bbmax = [bmax[0], bmax[1], bmax[2]]
                        else:
                            if bmax[0] < bbmin[0]:
                                bbmin[0] = bmax[0]
                            if bmax[1] < bbmin[1]:
                                bbmin[1] = bmax[1]
                            if bmax[2] < bbmin[2]:
                                bbmin[2] = bmax[2]
                            if bmax[0] > bbmax[0]:
                                bbmax[0] = bmax[0]
                            if bmax[1] > bbmax[1]:
                                bbmax[1] = bmax[1]
                            if bmax[2] > bbmax[2]:
                                bbmax[2] = bmax[2]
                    if parent_bone:
                        parent_bone_data = editor.ModelComponentList['bonelist'][parent_bone.name]['frames'][frames[m_frame].name]
                        parent_pos = quarkx.vect(parent_bone_data['position'])
                        parent_rot = quarkx.matrix(parent_bone_data['rotmatrix'])

                        bone_pos = ~parent_rot * (bone_pos - parent_pos)
                        bone_rot = ~parent_rot * bone_rot

                    bone_pos = bone_pos.tuple
                    bone_rot = bone_rot.tuple
                    m = matrix2euler(bone_rot)

                    data[0] += [bone_pos[0]]
                    data[1] += [bone_pos[1]]
                    data[2] += [bone_pos[2]]
                    data[3] += [m[0]]
                    data[4] += [m[1]]
                    data[5] += [m[2]]

                #Update the min,max, if needed
                for k in xrange(6):
                    if len(bone_min_max[j]) <= k:
                        #Not yet stored
                        min = data[k][0]
                        max = data[k][0]
                    else:
                        min, max = bone_min_max[j][k]
                    for l in xrange(len(data[k])):
                        if data[k][l] < min:
                            min = data[k][l]
                        if data[k][l] > max:
                            max = data[k][l]
                    if len(bone_min_max[j]) <= k:
                        bone_min_max[j] += [(min, max)]
                    else:
                        bone_min_max[j][k] = (min, max)

                all_bone_data += [data]
            all_data += [all_bone_data]

            if bbmin is not None:
                anim_seq.bbmin = bbmin
                if mdl.hull_min[0] == 0 and mdl.hull_min[1] == 0 and mdl.hull_min[2] == 0:
                    mdl.hull_min = anim_seq.bbmin
                print "line 2050 hull_min", mdl.hull_min
            if bbmax is not None:
                anim_seq.bbmax = bbmax
                if mdl.hull_max[0] == 0 and mdl.hull_max[1] == 0 and mdl.hull_max[2] == 0:
                    mdl.hull_max = anim_seq.bbmax
                print "line 2055 hull_max", mdl.hull_max

        mdl.QuArK_anim_data = []
        for i in xrange(len(mdl.sequence_descs)):
            anim_seq = mdl.sequence_descs[i]
            all_bone_data = all_data[i]
            mdl.QuArK_anim_data += [[]]
            for j in xrange(0, mdl.num_bones):
                data = all_bone_data[j]
                mdl.QuArK_anim_data[i] += [[]]

                # Calculate the final bone.scale, apply them and then save the data
                for k in xrange(6):
                    # Get the largest deviation from value, and set that as the scale
                    min, max = bone_min_max[j][k]
                    max = abs((max - mdl.bones[j].value[k]) / 32767)
                    min = abs((mdl.bones[j].value[k] - min) / -32768)
                    if min > max:
                        mdl.bones[j].scale[k] = min
                    else:
                        mdl.bones[j].scale[k] = max
                    if mdl.bones[j].scale[k] == 0.0:
                        #To prevent division by zero error
                        mdl.bones[j].scale[k] = 1.0

                    raw_data = []
                    for l in xrange(len(data[k])):
                        number = int((data[k][l] - mdl.bones[j].value[k]) / mdl.bones[j].scale[k])
                        if number < -32768:
                            number = -32768
                        if number > 32767:
                            number = 32767
                        raw_data += [number]

                    mdl.QuArK_anim_data[i][j] += [ConvertToHL1AnimData(raw_data)]

        #Try to be nice; delete big memory hog
        del all_data
        del bone_min_max

        ### OFFSET FOR BONE_ANIM SECTION.
        mdl_bone_anim_offset = mdl.localanimindex + (mdl.numlocalanim * 176) # 176 = class mdl_sequence_desc binary_format.

        for i in xrange(len(mdl.sequence_descs)):
            anim_seq = mdl.sequence_descs[i]
            anim_seq.anim_offset = mdl_bone_anim_offset

            mdl_bone_anim_offset += 12 * mdl.num_bones # 12 = class mdl_bone_anim binary_format.

            mdl_bone_anim_value_offset = 0 #This is the total number of bytes of animation data stores for this mdl_bone_anim so far.
            for j in xrange(0, mdl.num_bones):
                for k in xrange(6):
                    raw_data = mdl.QuArK_anim_data[i][j][k]
                    if len(raw_data) == 0:
                        #No data to store
                        anim_seq.anim_bones[j].offset[k] = 0
                    else:
                        anim_seq.anim_bones[j].offset[k] = mdl_bone_anim_value_offset + (12 * (mdl.num_bones - j)) # 12 = class mdl_bone_anim binary_format.
                        mdl_bone_anim_value_offset += len(raw_data)
            mdl_bone_anim_offset += mdl_bone_anim_value_offset

        ### OFFSET FOR DEMAND_HDR SECTION.
        mdl.localseqindex = mdl_bone_anim_offset
        mdl.numlocalseq = 1
        for i in xrange(mdl.numlocalseq):
            mdl.demand_seq_groups.append(mdl_demand_group())

        ### OFFSET FOR BODYPARTS SECTION.
        mdl.bodypartindex = mdl.localseqindex + (mdl.numlocalseq * 104) # 104 = class mdl_demand_group binary_format.

        mdl.num_bodyparts = 1
        QuArK_models = {}
        QuArK_models['highcount'] = []
        QuArK_models['lowcount'] = []
        for i in xrange(mdl.num_bodyparts):
            bodypart = mdl_bodypart()
            bodypart.model_offset = mdl.bodypartindex + (mdl.num_bodyparts * 76) # 76 = class mdl_bodypart binary_format.
            bodyparts_section_in_bytes = 0
            nummodels = 1
            for j in xrange(0, len(dlg.comp_list)):
                test_name = dlg.comp_list[j].name.replace(dlg.comp_group, "")
                if not test_name.startswith("l"):
                    mesh = dlg.comp_list[j].copy()
                    mesh.shortname = mesh.shortname.replace(dlg.comp_group, "")
                    QuArK_models['highcount'].append(mesh)
                    for k in xrange(0, len(dlg.comp_list)):
                        comp_name = dlg.comp_list[k].name.replace(dlg.comp_group, "")
                        if comp_name.startswith("l") and comp_name.find(test_name) != -1:
                            nummodels = 2
                            mesh = dlg.comp_list[k].copy()
                            mesh.shortname = mesh.shortname.replace(dlg.comp_group, "")
                            QuArK_models['lowcount'].append(mesh)
            bodypart.nummodels = nummodels
            bodyparts_section_in_bytes += bodypart.nummodels * 112 # 112 = class mdl_model binary_format.
            mdl.bodyparts.append(bodypart)
            for j in xrange(mdl.bodyparts[i].nummodels):
                model = mdl_model()
                QuArK_mesh_verts = []
                model.numverts = 0
                model.vert_info_offset = bodypart.model_offset + bodyparts_section_in_bytes
                if j == 0 and len(QuArK_models['lowcount']) != 0:
                    QuArK_list = QuArK_models['lowcount']
                else:
                    QuArK_list = QuArK_models['highcount']
                model.name = QuArK_list[0].shortname.split(" ")[0]
                weightvtxlist = None
                for comp in QuArK_list:
                    if comp.name.find(model.name) != -1:
                        model.nummesh += 1
                        mesh_verts = {}
                        verts = []
                        vert_infos = []
                        if editor.ModelComponentList.has_key(dlg.comp_group + comp.name) and editor.ModelComponentList[dlg.comp_group + comp.name]['weightvtxlist'] != {}:
                            weightvtxlist = editor.ModelComponentList[dlg.comp_group + comp.name]['weightvtxlist']
                        framesgroup = comp.dictitems['Frames:fg'].subitems
                        for frame in framesgroup:
                            if frame.name.find("baseframe:mf") != -1:
                                break
                        faces = comp.triangles
                        fv = frame.vertices
                        norms, norms_infos = mesh_normals(comp.name, faces, fv, mdl.QuArK_bones, mdl.num_bones)
                        vert_index = -1
                        for k in xrange(0, len(fv)):
                            key = str(fv[k])
                            if not key in mesh_verts.keys():
                                vert_index += 1
                                mesh_verts[key] = k

                                verts_info = mdl_vert_info()
                                ## NOTE 1 of HL1 EXPORTER NOTES at top of this file.
                                if weightvtxlist is not None:
                                    try:
                                        vert_weights = weightvtxlist[vert_index]
                                    except:
                                        quarkx.msgbox("Unassigned Vertex !\nCan not export model.\n\nComponent: " + dlg.comp_group + comp.shortname + ".\n  vertex nbr: " + str(vert_index) + "\nhas not been assigned to a bone.\n\nDo a vertex search to select it for assignment.\nAll vertices must be assigned before exporting.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                                        quarkx.beep()
                                        return
                                    bone_name = vert_weights.keys()[0]
                                    if len(vert_weights) > 1:
                                        weight_value = 0.0
                                        for name in vert_weights.keys():
                                            if vert_weights[name]['weight_value'] > weight_value:
                                                weight_value = vert_weights[name]['weight_value']
                                                bone_name = name
                                    verts_info.bone_index = QuArK_bone_name2bone_index[bone_name]

                                else:
                                    for l in xrange(0, mdl.num_bones):
                                        if mdl.QuArK_bones[l].vtxlist.has_key(dlg.comp_group + comp.name):
                                            if k in mdl.QuArK_bones[l].vtxlist[dlg.comp_group + comp.name]:
                                                verts_info.bone_index = l
                                                break

                                vert_infos.append(verts_info)

                                # Calculate vertex position to store
                                vert_pos = fv[k].tuple
                                bone = mdl.QuArK_bones[verts_info.bone_index]
                                bp = bone.position
                                br = bone.rotmatrix
                                vert_pos = quarkx.vect(vert_pos[0], vert_pos[1], vert_pos[2])
                                vert_pos = (~br) * (vert_pos - bp)
                                vert_pos = vert_pos.tuple

                                vertex = mdl_vertex()
                                vertex.v = vert_pos
                                verts.append(vertex)

                        QuArK_mesh_verts.append(mesh_verts)
                        model.numverts += len(verts)
                        model.verts.append(verts)
                        model.verts_info.append(vert_infos)
                        model.numnorms += len(norms)
                        model.normals.append(norms)
                        model.normals_info.append(norms_infos)
                bodyparts_section_in_bytes += model.numverts # 1 bytes each = class mdl_vert_info binary_format, 1 per vert.

                model.norm_info_offset = bodypart.model_offset + bodyparts_section_in_bytes
                bodyparts_section_in_bytes += model.numnorms # 1 bytes each = class mdl_norm_info binary_format, 1 per vert.

                model.vert_offset = bodypart.model_offset + bodyparts_section_in_bytes
                bodyparts_section_in_bytes += model.numverts * 12 # 12 = class mdl_vertex binary_format.

                model.norm_offset = bodypart.model_offset + bodyparts_section_in_bytes
                bodyparts_section_in_bytes += model.numnorms * 12 # 12 = class mdl_norm binary_format, just use above mdl_vertex.

                model.mesh_offset = bodypart.model_offset + bodyparts_section_in_bytes
                bodyparts_section_in_bytes += model.nummesh * 20 # 20 = class mdl_mesh binary_format.
                # each mesh = 5 ints = numtris, tri_offset, skinref, numnorms, normindex (has lists = triangles & normals)
                mesh_index = -1
                keys_count = 0
                for k in xrange(0, len(QuArK_list)):
                    comp = QuArK_list[k]
                    if comp.name.find(model.name) != -1:
                        mesh_index += 1
                        framesgroup = comp.dictitems['Frames:fg'].subitems
                        for frame in framesgroup:
                            if frame.name.find("baseframe") != -1:
                                break
                        fv = frame.vertices
                        mesh_verts = QuArK_mesh_verts[mesh_index]
                        QuArK_tris = comp.triangles
                        mesh = mdl_mesh()
                        mesh.numtris = len(QuArK_tris)
                        mesh.tri_offset = bodypart.model_offset + bodyparts_section_in_bytes
                        mesh.skinref = mesh_index
                        mesh.numnorms = len(model.normals[mesh_index])
                      #  mesh.dump()
                        for l in xrange(0, mesh.numtris):
                            tri = QuArK_tris[l]
                            face = mdl_face()
                            for m in xrange(0, 3):
                                key = str(fv[tri[m][0]])
                                face.vertex_index[m] = mesh_verts[key] + keys_count
                                face.texture_uv[m][0] = tri[m][1]
                                face.texture_uv[m][1] = tri[m][2]
                            mesh.faces.append(face)
                        mesh_bytes_count = 0
                        mesh_bytes_count = build_GL_commands(mesh, mesh_bytes_count)
                        bodyparts_section_in_bytes += mesh_bytes_count
                        model.meshes.append(mesh)
                        keys_count += len(mesh_verts.keys())
                      #  for GL_com in mesh.triangles:
                      #      GL_com.dump()

                mdl.bodyparts[i].models.append(model)

          #  mdl.bodyparts[i].dump()
          #  for model in mdl.bodyparts[i].models:
          #      model.dump()
          #      for mesh in model.meshes:
          #          mesh.dump()

        mdl.length = bodypart.model_offset + bodyparts_section_in_bytes

    if dlg.src['MakeMainMDL'] is not None:
        mdl.num_textures = len(dlg.skins)
        mdl.numskinref = mdl.num_textures

        ### OFFSETS FOR TEXTURE AND SKIN SECTIONS.
        mdl.textureindex = mdl.length
        next_skin_offset = 0
        for i in xrange(mdl.num_textures):
            skin_info = HL2_TexturesInfo()
            skin_info.sznameindex = mdl.textureindex + 4 + next_skin_offset
            skin_info.pszName = dlg.skin_shortnames[i]
            if dlg.skins[i].dictspec.has_key('HL_skin_flags'):
                skin_info.flags = int(dlg.skins[i].dictspec['HL_skin_flags'])
            next_skin_offset = next_skin_offset + 124
          #  skin_info.dump()
                
            mdl.skins_group.append(skin_info)
        mdl.length = mdl.textureindex + (mdl.num_textures * 128) # 128 = class HL2_TexturesInfo binary_format.
    mdl.dump()


####################################
# Starts By Using the Model Object
#################################### #NEED = need to add to writing to file code.
class mdl_obj: # Done cdunde from -> hlmviewer source file -> studio.h -> studiohdr_t
    origin = quarkx.vect(0.0, 0.0, 0.0) ### For QuArK's model placement in the editor.
    #Header Structure          #item of data file, size & type,   description
    ident = "IDST"             #item  0     4s string, The version of the file (Must be IDST)
    version = 44               #item  1     int, This is used to identify the file, 44=HL2 mesh file.
    checksum = 0    #NEED      #item  2     int.this has to be the same in the phy and vtx files to be created.
    name = ""                  #item  3     64s string, the models path and full name.
    length = 0                 #item  4     int, length of the file in bytes to EOF.
    eyeposition = [0.0]*3      #item  5-7   3 floats, ideal eye position.
    illumposition = [0.0]*3    #item  8-10  3 floats, illumination center.
    hull_min = [0.0]*3         #item  11-13 3 floats, ideal movement hull size, min.
    hull_max = [0.0]*3         #item  14-16 3 floats, ideal movement hull size, max.
    view_bbmin = [0.0]*3       #item  17-19 3 floats, clipping bounding box size, min.
    view_bbmax = [0.0]*3       #item  20-22 3 floats, clipping bounding box size, max.
    flags = 0                  #item  23    int, unknown item.
    num_bones = 0              #item  24    int, The number of bone for the model.
    boneindex = 0              #item  25    int, The bones data starting point in the file, in bytes.
    num_bone_controls = 0      #item  26    int, The number of bone controllers.
    bone_controls_offset = 0   #item  27    int, The bones controllers data starting point in the file, in bytes.
    numhitboxsets = 1          #item  28    int, The number of complex bounding boxe sets (always 1).
    hitboxsetindex = 0         #item  29    int, The hitboxesets data starting point in the file, in bytes.
    numlocalanim = 0           #item  30    int, The number of animation sequences for the model (num_anim_seq in HL1).
    localanimindex = 0         #item  31    int, The animation sequences data starting point in the file, in bytes (anim_seq_offset in HL1).
    numlocalseq = 0            #item  32    int, The number of demand seq groups for the model, demand loaded sequences (num_demand_hdr_groups in HL1).
    localseqindex = 0          #item  33    int, The demand seq groups data starting point in the file, in bytes (demand_hdr_offset in HL1).
    activitylistversion = 0 #NEED #item  34    int, initialization flag - have the sequences been indexed?
    eventsindexed = 0  #NEED   #item  35    int.
    num_textures = 0           #item  36    int, The number of raw textures.
    textureindex = 0           #item  37    int, The "HL2_TexturesInfo" data index starting point in the file, in bytes (texture_index_offset in HL1).
    numcdtextures = 1  #NEED   #item  38    int, We don't use this, always 1.
    cdtextureindex = 0 #NEED   #item  39    int, We don't use this.
    numskinref = 0     #NEED   #item  40    int, Same as "num_textures" (num_skin_refs in HL1).
    numskinfamilies = 1        #item  41    int, The number of texture groups for the model, always 1 (num_skin_groups in HL1).
    skinindex = 0              #item  42    int, Not used anymore (skin_refs_offset in HL1).
    num_bodyparts = 0          #item  43    int, The number of body parts for the model.
    bodypartindex = 0  #NEED   #item  44    int, The body parts data starting point in the file, in bytes (bodyparts_offset in HL1).
    numlocalattachments = 0  #NEED #item  45    int, The number of queryable attachable points for the model (num_attachments in HL1).
    localattachmentindex = 0 #NEED #item  46    int, The queryable attachable points data starting point in the file, in bytes (attachments_offset in HL1).
    numlocalnodes = 0  #NEED   #item  47    int, unknown item.
    localnodeindex = 0 #NEED   #item  48    int, unknown item.
    localnodenameindex = 0 #NEED #item  49    int, unknown item.
    numflexdesc = 0 #NEED #item  50    int, unknown item.
    flexdescindex = 0  #NEED   #item  51    int, unknown item.
    numflexcontrollers = 0 #NEED #item  52    int, unknown item.
    # NEED ALL BELOW
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

    binary_format = ("<4sii%dsi3f3f3f3f3f3f44if11i3B7i" % (MAX_QPATH)) #little-endian (<), see #item descriptions above.

    hitboxsets = [] # NEW
    keys = [] # NEW
    tags = [] # NEW
    surfaces = [] # NEW
    ikchains = [] # NEW
    origin = quarkx.vect(0.0, 0.0, 0.0) # NEW

    #mdl data objects
    bones = []
    QuArK_bones = []
    skins_group = []
    QuArKBonesData = [] # NEW
    materials_group = [] # NEW
    demand_seq_groups = []
    anim_blocks = [] # NEW
    bone_controls = []
    animation_descs = [] # NEW
    QuArK_anim_seq = []
    QuArK_anim_seq_frames = {}
    QuArK_anim_data = []
    sequence_descs = []
    hitboxes = []
    attachments = []
    bodyparts = []

    tex_coords = []
    faces = []
    vertices = []
    tagsgroup = [] # NEW
    num_anim = 0 # NEW
    main_mdl_comps = [] # NEW
    main_mdl_bones = [] # NEW
    bones_names = [] # NEW
    new_mdl_comps = [] # NEW

    def __init__ (self):
        self.hitboxsets = []        # A list of QuArK :bbg bbox groups with QuArK :p hitbox polys.
        self.keys = []              # NEW
        self.tags = []              # NEW
        self.surfaces = []          # NEW
        self.ikchains = []          # NEW
        self.origin = quarkx.vect(0.0, 0.0, 0.0) # NEW
        self.bones = []             # A list of the bones.
        self.QuArK_bones = []       # A list of the QuArK bones, for our use only.
        self.skins_group = []       # A list of the skins.
        self.QuArKBonesData = []    # NEW A list matching above with [[OurFullName, vtxlist as {dictionary}],...]
        self.materials_group = []   # NEW A list of the .vmt material files full paths and names to go with skins above.
        self.demand_seq_groups = [] # A list of the demand sequence groups.
        self.anim_blocks = []       # NEW A list of the animation blocks.
        self.bone_controls = []     # A list of the bone controllers.
        self.animation_descs = []   # NEW A list of the animation descriptions (leads into grouped frames).
        self.QuArK_anim_seq = []    # A list of the QuArK frame groups in their proper tree-view order.
        self.QuArK_anim_seq_frames = {} # A dictionary of the QuArK frames, for our use only. Key = sequence name, value = list of frames
        self.QuArK_anim_data = []   # A list of the raw bone_anim_value data.
        self.sequence_descs = []    # A list of the sequence descriptions (leads into grouped frames).
        self.hitboxes = []          # A list of the hitboxes.
        self.attachments = []       # A list of the attachments, our QuArK tags and their tag frames.
        self.bodyparts = []         # A list of the bodyparts.

        self.tex_coords = []        # A list of integers, 1 for "onseam" and 2 for the s,t or u,v texture coordinates.
        self.faces = []             # A list of the triangles.
        self.vertices = []          # A list of the vertexes.
        self.tagsgroup = []         # NEW A list of tag (attachment) groups to store tag frames into for each tag.
        self.num_anim = 0           # NEW We half to set this because the MORONS at VALVE can't do it.
        self.main_mdl_comps = []    # NEW A list of main model components already loaded into QuArK.
        self.main_mdl_bones = []    # NEW A list of main model components bones already loaded into QuArK.
        self.bones_names = []       # NEW A conversion list of self.main_mdl_bones name converted to importer self.bone names.
        self.new_mdl_comps = []     # NEW A list of main model components updated copies in the main_mdl_comps list above.

    def save(self, dlg):
        global progressbar
        # file = the actual .mdl model file being written to, exported.
        file = dlg.mdlfile

        # Write the header
        data = struct.pack(self.binary_format,
        self.ident,
        self.version,
        self.checksum,
        self.name,
        self.length,
        self.eyeposition[0], self.eyeposition[1], self.eyeposition[2],
        self.illumposition[0], self.illumposition[1], self.illumposition[2],
        self.hull_min[0], self.hull_min[1], self.hull_min[2],
        self.hull_max[0], self.hull_max[1], self.hull_max[2],
        self.view_bbmin[0], self.view_bbmin[1], self.view_bbmin[2],
        self.view_bbmax[0], self.view_bbmax[1], self.view_bbmax[2],
        self.flags,
        self.num_bones,
        self.boneindex,
        self.num_bone_controls,
        self.bone_controls_offset,
        self.numhitboxsets,
        self.hitboxsetindex,
        self.numlocalanim,
        self.localanimindex,
        self.numlocalseq,
        self.localseqindex,
        self.activitylistversion,
        self.eventsindexed,
        self.num_textures,
        self.textureindex,
        self.numcdtextures,
        self.cdtextureindex,
        self.numskinref,
        self.numskinfamilies,
        self.skinindex,
        self.num_bodyparts,
        self.bodypartindex,
        self.numlocalattachments,
        self.localattachmentindex,
        self.numlocalnodes,
        self.localnodeindex,
        self.localnodenameindex,
        self.numflexdesc,
        self.flexdescindex,
        self.numflexcontrollers,
        self.flexcontrollerindex,
        self.numflexrules,
        self.flexruleindex,
        self.numikchains,
        self.ikchainindex,
        self.nummouths,
        self.mouthindex,
        self.numlocalposeparameters,
        self.localposeparamindex,
        self.surfacepropindex,
        self.keyvalueindex,
        self.keyvaluesize,
        self.numlocalikautoplaylocks,
        self.localikautoplaylockindex,
        self.mass,
        self.contents,
        self.numincludemodels,
        self.includemodelindex,
        self.virtualModel,
        self.szanimblocknameindex,
        self.numanimblocks,
        self.animblockindex,
        self.animblockModel,
        self.bonetablebynameindex,
        self.pVertexBase,
        self.pIndexBase,
        self.rootLOD,
        self.unused1,
        self.unused2,
        self.zeroframecacheindex,
        self.array1,
        self.array2,
        self.array3,
        self.array4,
        self.array5,
        self.array6)
        file.write(data)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Data Size in bytes: " + str(file.tell()))
            tobj.logcon ("#####################################################################")

        # write the bones data
        for i in xrange(self.num_bones):
            self.bones[i].save(file)
          #  self.bones[i].dump()

        # write the bone controllers data
        for i in xrange(self.num_bone_controls):
            self.bone_controls[i].save(file)
          #  self.bone_controls[i].dump()

        # write the bone attachments data
        for i in xrange(self.numlocalattachments):
            self.attachments[i].save(file)
          #  self.attachments[i].dump()

        # write the hitboxsets and hitboxes data, can only have one per bone and visa versa.
        hitboxset = HL2_HitBoxSet()
        hitboxset.save(file, QuArK_bones, self.hitboxes)
          #  hitboxset.dump()

        # write the animation sequence descriptions data.
        for i in xrange(self.numlocalanim):
            self.sequence_descs[i].save(file)
          #  self.sequence_descs[i].dump()

        # write the animation sequence data.
        for i in xrange(self.numlocalanim):
            # write the bone anim data.
            for j in xrange(len(self.sequence_descs[i].anim_bones)):
                self.sequence_descs[i].anim_bones[j].save(file)
                #  self.sequence_descs[i].anim_bones[j].dump()
            # write the bone anim value data.
            for j in xrange(len(self.sequence_descs[i].anim_bones)):
                for k in xrange(6):
                    file.write(self.QuArK_anim_data[i][j][k])

        # write the header for demand sequence group data
        for i in xrange(self.numlocalseq):
            self.demand_seq_groups[i].save(file)
          #  self.demand_seq_groups[i].dump()

        # write the bodyparts data
        for bodypart in self.bodyparts:
            bodypart.save(file)
          #  bodypart.dump()
            for model in bodypart.models:
                model.save(file)
                #  model.dump()
            for model in bodypart.models:
                for vert_info in model.verts_info:
                    for info in vert_info:
                        info.save(file)
                        #  info.dump()
                for norm_info in model.normals_info:
                    for info in norm_info:
                        info.save(file)
                        #  info.dump()
                for verts in model.verts:
                    for vert in verts:
                        vert.save(file)
                        #  vert.dump()
                for norms in model.normals:
                    for norm in norms:
                        norm.save(file)
                        #  norm.dump()
                for mesh in model.meshes:
                    mesh.save(file)
                    #  mesh.dump()
                for mesh in model.meshes:
                    for tri in mesh.triangles:
                        tri.save(file)
                        #  tri.dump()

        # write the skins group data, texture_index_offset
        for i in xrange(self.num_textures):
            self.skins_group[i].save(file)
          #  self.skins_group[i].dump()

    def dump(self):
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + str(self.ident))
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("checksum: " + str(self.checksum))
            tobj.logcon ("name: " + str(self.name))
            tobj.logcon ("length: " + str(self.length))
            tobj.logcon ("eyeposition: " + str(self.eyeposition))
            tobj.logcon ("hull_min: " + str(self.hull_min))
            tobj.logcon ("hull_max: " + str(self.hull_max))
            tobj.logcon ("view_bbmin: " + str(self.view_bbmin))
            tobj.logcon ("view_bbmax: " + str(self.view_bbmax))
            tobj.logcon ("flags: " + str(self.flags))
            tobj.logcon ("num_bones: " + str(self.num_bones))
            tobj.logcon ("boneindex: " + str(self.boneindex))
            tobj.logcon ("num_bone_controls: " + str(self.num_bone_controls))
            tobj.logcon ("bone_controls_offset: " + str(self.bone_controls_offset))
            tobj.logcon ("numhitboxsets: " + str(self.numhitboxsets))
            tobj.logcon ("hitboxsetindex: " + str(self.hitboxsetindex))
            tobj.logcon ("numlocalanim: " + str(self.numlocalanim))
            tobj.logcon ("localanimindex: " + str(self.localanimindex))
            tobj.logcon ("numlocalseq: " + str(self.numlocalseq))
            tobj.logcon ("localseqindex: " + str(self.localseqindex))
            tobj.logcon ("activitylistversion: " + str(self.activitylistversion))
            tobj.logcon ("eventsindexed: " + str(self.eventsindexed))
            tobj.logcon ("num_textures: " + str(self.num_textures))
            tobj.logcon ("textureindex: " + str(self.textureindex))
            tobj.logcon ("numcdtextures: " + str(self.numcdtextures))
            tobj.logcon ("cdtextureindex: " + str(self.cdtextureindex))
            tobj.logcon ("numskinref: " + str(self.numskinref))
            tobj.logcon ("numskinfamilies: " + str(self.numskinfamilies))
            tobj.logcon ("skinindex: " + str(self.skinindex))
            tobj.logcon ("num_bodyparts: " + str(self.num_bodyparts))
            tobj.logcon ("bodypartindex: " + str(self.bodypartindex))
            tobj.logcon ("numlocalattachments: " + str(self.numlocalattachments))
            tobj.logcon ("localattachmentindex: " + str(self.localattachmentindex))
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
            tobj.logcon ("keyvalueindex: " + str(self.keyvalueindex))
            tobj.logcon ("keyvaluesize: " + str(self.keyvaluesize))
            tobj.logcon ("numlocalikautoplaylocks: " + str(self.numlocalikautoplaylocks))
            tobj.logcon ("localikautoplaylockindex: " + str(self.localikautoplaylockindex))
            tobj.logcon ("mass: " + str(self.mass))
            tobj.logcon ("contents: " + str(self.contents))
            tobj.logcon ("numincludemodels: " + str(self.numincludemodels))
            tobj.logcon ("includemodelindex: " + str(self.includemodelindex))
            tobj.logcon ("virtualModel: " + str(self.virtualModel))
            tobj.logcon ("szanimblocknameindex: " + str(self.szanimblocknameindex))
            tobj.logcon ("numanimblocks: " + str(self.numanimblocks))
            tobj.logcon ("animblockindex: " + str(self.animblockindex))
            tobj.logcon ("animblockModel: " + str(self.animblockModel))
            tobj.logcon ("bonetablebynameindex: " + str(self.bonetablebynameindex))
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


########################
# To run this file
########################
# filename = the model file & full path being writen to, ex: C:\Program Files\Valve\Steam\QuArKApps\hl2\models\alyx.mdl
def save_mdl(dlg):
    global tobj, logging, exportername, textlog, Strings, mdl

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, dlg.filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    # dlg = all the QuArK objects setup as attributes of the export dialog for example
    #        the tags (if any) and components we are exporting from our model editor.
    mdl = mdl_obj()

    # Fill the needed data for exporting.
    fill_mdl(dlg)

    mdl.save(dlg)

    if logging == 1:
        mdl.dump() # Writes the file Header last to the log for comparison reasons.

    try:
        progressbar.close()
    except:
        pass

    ie_utils.default_end_logging(dlg.filename, "EX", starttime) ### Use "EX" for exporter text, "IM" for importer text.


######################################################
# CALL TO PROCESS .mdl FILE (where it all starts off from)
######################################################
# The model file: root is the actual file,
# filename and gamename is the full path to
# and name of the .mdl file selected.
# For example:  C:\Program Files\Valve\Steam\QuArKApps\hl2\models\alyx.mdl
# gamename is None.
def savemodel(root, filename, gamename, nomessage=0):
    global editor
    editor = quarkpy.mdleditor.mdleditor
    if editor is None:
        return

    # TAKE THIS PART OUT WHEN EXPORTER IS DONE BEING WORKED ON.
    result = quarkx.msgbox("THIS EXPORTER IS NOT FINISHED YET.\n\nOpen your plugins/ie_md0_HL2_export.py file\nwith any text editor and read details at the top.\n\nCAUTION:\nIf YES, any file with the same name will be overwritten.\n\nDo you wish to continue with this export?", quarkpy.qutils.MT_WARNING, quarkpy.qutils.MB_YES | quarkpy.qutils.MB_NO)
    if result == MR_YES:
        pass
    else:
        quarkx.msgbox("EXPORT CANCELED:\n\nNothing was written to any files\nand all files in that folder remain unchanged.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return

    # "ComponentList" is a list of one or more selected model components for exporting.
    ComponentList = editor.layout.explorer.sellist

    if not ComponentList:
        quarkx.msgbox("No Components have been selected for exporting.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return
    for i in range(len(ComponentList)):
        object = ComponentList[i]
        framesgroup = object.dictitems['Frames:fg']
        if not object.name.endswith(":mc"):
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select component folders for exporting.\n\nAn item that is not a component folder\nis in your selections.\n\nDeselect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
            if object.dictitems['Frames:fg'].subitems[0].name != "baseframe:mf":
                quarkx.beep()
                quarkx.msgbox("MISSING or MISSPLACED MESH baseframe(s) !\n\nAll selected component's FIRST frame must be a static pose\nof that model's part and that frame named 'baseframe' !\n\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
        if not framesgroup or len(framesgroup.subitems) == 0:
            quarkx.msgbox("No frames exist for " + object.shortname + ".\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if not object.dictitems['Skins:sg']:
            quarkx.msgbox("No Skins folder exist for " + object.shortname + ".\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if i == 0:
            frame_count = len(framesgroup.subitems)
        if len(framesgroup.subitems) != frame_count:
            quarkx.msgbox("Number of frames of selected components do not match.\nMatch the frames for each component and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
    if editor.Root.currentcomponent.currentframe.name != "baseframe:mf":
        quarkx.msgbox("Baseframe not selected:\n\nYou need to select a components 'baseframe'\nbefore exporting and then try again.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return

    comp_group = ComponentList[0].name.split("_")
    comp_count = len(ComponentList)
    if len(comp_group) == 1:
        if comp_count != 1:
            quarkx.msgbox("No Component Group !\n\nTo export you must add the same GroupName and '_' (no spaces).\nto the begining of each\ncomponent(s) and all related tags, bboxes and bone names\nthat you want included in the model file.\n\nCorrect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        else:
            comp_group = comp_group[0].split(":mc")
    else:
        comp_group = comp_group[0] + "_"
        for comp in ComponentList:
            if not comp.name.startswith(comp_group):
                quarkx.msgbox("No Component Group !\n\nTo export you must add a GroupName and '_'.\nto the begining of each\ncomponent(s) and all related tags, bboxes and bone names\nthat you want included in the model file.\n\nCorrect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return

    UIExportDialog(root, filename, editor, comp_group) # Calls the dialog below which calls to save a model file.



### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".mdl Half-Life2 Exporter", ".mdl file", "*.mdl", savemodel)


######################################################
# DIALOG SECTION (which calls to export an .mdl file)
######################################################
class ExportSettingsDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (200, 300)
    dfsep = 0.65     # sets 65% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """ """ # The dialog is created in the UIExportDialog function to allow self generated items.

    def __init__(self, form1, root, filename, editor, newfiles_folder, comp_group): # Creates the dialogbox.
        self.dlgdef = """
        {
        Style = "13"
        Caption = "mdl Export Items"
        sep: = {
            Typ="S"
            Txt="Instructions: place cursor here"
            Hint = "Place your cursor over each item"$0D
                   "below for a description of what it is."$0D$0D
                   "Their default export settings have already been set."$0D
                   "You can cancel the entire export process at any time"$0D
                   "by clicking the 'Close dialog' button."
               }
        sep: = { Typ="S" Txt="" }

        Tags: =
            {
            Txt = "Export Tags:"
            Typ = "X"
            Hint = "Check this box to export the component's"$0D
                   "tags and tag frames, if any, with the model."
            }

        BBoxes: =
            {
            Txt = "Export BBoxes:"
            Typ = "X"
            Hint = "Check this box to export the component's"$0D
                   "BBoxes, if any, with the model."
            }

        MakeMainMDL: =
            {
            Txt = "Make Main MDL file:"
            Typ = "X"
            Hint = "Check this box to create the model's main mdl file."$0D
                   "This is the base file that the model is made from."
            }

        """ + SpecsList + """

        makefolder: =
            {
            Txt = "Make file folder:"
            Typ = "X"
            Hint = "Check this box to make a new folder to place"$0D
                   "all export files in at the location you chose."$0D
                   "Some of these files may need to be moved to other folders."$0D$0D
                   "If unchecked files will all be placed at the same location"$0D
                   "that you chose for the .mdl model file to be placed."
            }

        sep: = { Typ="S" Txt="" }
        MakeFiles:py = {Txt="Export Model"}
        close:py = {Txt="Close dialog"}
        }
        """
        self.root = root
        self.filename = filename
        self.editor = editor
        self.newfiles_folder = newfiles_folder
        self.comp_group = comp_group
        self.comp_list = self.editor.layout.explorer.sellist
        self.mdlfile = None
        self.exportpath = filename.replace('\\', '/')
        self.exportpath = self.exportpath.rsplit('/', 1)[0]
        src = quarkx.newobj(":")
        src['dummy'] = None
        miscgroup = self.editor.Root.dictitems['Misc:mg']  # get the Misc group
        tags = miscgroup.findallsubitems("", ':tag')    # get all tags
        if len(tags) > 0:
            src['Tags'] = "1"
        else:
            src['Tags'] = None
        bboxlist = self.editor.ModelComponentList['bboxlist']
        if len(bboxlist) > 0:
            src['BBoxes'] = "1"
        else:
            src['BBoxes'] = None
        src['MakeMainMDL'] = "1"
        src['MakeAnimations'] = None
        src['MakeGestures'] = None
        src['MakePostures'] = None
        src['makefolder'] = None
        self.src = src

        # Create the dialog form and the buttons.
        quarkpy.qmacro.dialogbox.__init__(self, form1, src,
            MakeFiles = quarkpy.qtoolbar.button(self.MakeFiles,"DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.",ico_editor, 3, "Export Model"),
            close = quarkpy.qtoolbar.button(self.close, "DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.", ico_editor, 0, "Cancel Export")
            )

    def datachange(self, df):
        if (self.src['MakeAnimations'] is None and self.src['MakeGestures'] is None and self.src['MakePostures'] is None) and not (self.src['dummy'] is None):
            self.src['dummy'] = None
        elif self.src['MakeAnimations'] == "1" and (self.src['dummy'] is None or self.src['dummy'] != "1"):
            self.src['MakeGestures'] = None
            self.src['MakePostures'] = None
            self.src['dummy'] = "1"
        elif self.src['MakeGestures'] == "1" and (self.src['dummy'] is None or self.src['dummy'] != "2"):
            self.src['MakeAnimations'] = None
            self.src['MakePostures'] = None
            self.src['dummy'] = "2"
        elif self.src['MakePostures'] == "1" and (self.src['dummy'] is None or self.src['dummy'] != "3"):
            self.src['MakeAnimations'] = None
            self.src['MakeGestures'] = None
            self.src['dummy'] = "3"
            
        df.setdata(self.src, self.f) # This line updates the dialog.

    def MakeFiles(self, btn):
        global QuArK_bones
        QuArK_bones = []
        # Accepts all entries then starts making the processing function calls.
        quarkx.globalaccept()
        root = self.root

        self.tags = []
        self.bboxlist = {}
        self.skins = []
        self.bones = []
        self.skin_names = []
        self.skin_shortnames = []

        if self.src["makefolder"] is not None:
            if not os.path.exists(self.newfiles_folder):
                os.mkdir(self.newfiles_folder)
            else:
                if len(self.filename) > MAX_QPATH:
                    quarkx.msgbox("EXPORT CANCELED:\n\nFull path and file name exceeded\nMDL file limit of 64 characters & spaces.\n\nNothing was written to the\n    " + self.filename + "\nfile and it remains unchanged.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
                    return
                result = quarkx.msgbox("A folder to store the new files in\n    " + self.newfiles_folder + "\nalready exist at that location.\n\nCAUTION:\nAny files in that folder with the same name\nas a new file will be overwritten.\n\nDo you wish to continue making new files for that folder?", quarkpy.qutils.MT_WARNING, quarkpy.qutils.MB_YES | quarkpy.qutils.MB_NO)
                if result == MR_YES:
                    pass
                else:
                    quarkx.msgbox("PROCESS CANCELED:\n\nNothing was written to the\n    " + self.newfiles_folder + "\nfolder and all files in that folder remain unchanged.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
                    return
            self.exportpath = self.newfiles_folder
            self.filename = self.filename.rsplit('\\', 1)[1]
            self.filename = self.newfiles_folder + "\\" + self.filename
        else:
            if not os.path.exists(self.filename):
                pass
            else:
                result = quarkx.msgbox("A file of the same name\n    " + self.filename + "\nalready exist at that location.\n\nCAUTION:\nIf you continue with this export\nthe current file will be overwritten.\n\nDo you wish to continue with this export?", quarkpy.qutils.MT_WARNING, quarkpy.qutils.MB_YES | quarkpy.qutils.MB_NO)
                if result == MR_YES:
                    pass
                else:
                    quarkx.msgbox("PROCESS CANCELED:\n\nNothing was written to the\n    " + self.filename + "\nfile and it remains unchanged.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
                    return

        if self.src["Tags"] is not None:
            frame_count = len(self.comp_list[0].dictitems['Frames:fg'].subitems)
            miscgroup = self.editor.Root.dictitems['Misc:mg']  # get the Misc group
            tags = miscgroup.findallsubitems("", ':tag')    # get all tags
            for tag in tags:
                if tag.name.startswith(self.comp_group):
                    if len(tag.subitems) != frame_count:
                        quarkx.msgbox("Number of tag frames do not match\nnumber of component frames.\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                        return
                    self.tags.append(tag)

        if self.src["BBoxes"] is not None:
            bboxlist = self.editor.ModelComponentList['bboxlist']
            bbox_keys = bboxlist.keys()
            for bbox_key in bbox_keys:
                if bbox_key.startswith(self.comp_group):
                    self.bboxlist[bbox_key] = bboxlist[bbox_key]

        if self.src['MakeMainMDL'] is not None:
            for comp in self.comp_list:
                for skin in comp.dictitems['Skins:sg'].subitems:
                    if not skin.name in self.skin_names:
                        self.skin_names.append(skin.name)
                        name = skin.name.replace("\\", "/")
                        name = name.rsplit(".", 1)[0]
                        try:
                            name = name.rsplit("/", 1)[1]
                        except:
                            pass
                        self.skin_shortnames.append(name)
                        self.skins.append(skin.copy())
                    else:
                        continue

        skeletongroup = self.editor.Root.dictitems['Skeleton:bg']  # get the bones group
        bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
        for bone in bones:
            if bone.name.startswith(self.comp_group):
                QuArK_bones.append(bone)
        if len(QuArK_bones) == 0:
            quarkx.msgbox("No Bones exist for exporting.\n\nAt least one bone is needed to position the model.\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

        if self.src['MakeMainMDL'] is None and self.src['MakeAnimations'] is None and self.src['MakeGestures'] is None and self.src['MakePostures'] is None:
            quarkx.msgbox("Nothing checked for exporting.\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

        framescount = len(self.comp_list[0].dictitems['Frames:fg'].subitems)
        if framescount > 1 and (self.src['MakeAnimations'] is not None or self.src['MakeGestures'] is not None or self.src['MakePostures'] is not None):
            print "line 3030 self.filename", self.filename
            for i in range(len(possible_files)):
                if self.filename.find(possible_files[i]) != -1:
                    self.filename = self.filename.replace(possible_files[i], "")
            if self.src['MakeAnimations'] is not None:
                self.filename = self.filename.split(".")[0] + "_animations.mdl"
            elif self.src['MakeGestures'] is not None:
                self.filename = self.filename.split(".")[0] + "_gestures.mdl"
            elif self.src['MakePostures'] is not None:
                self.filename = self.filename.split(".")[0] + "_postures.mdl"
            # Opens the output file for writing the .mdl file to disk.
            print "line 3041 self.filename", self.filename
            self.mdlfile = open(self.filename,"wb")
            UIAnimDialog(self, editor, self.filename, self.comp_list, self.newfiles_folder)

        elif self.src['MakeMainMDL'] is not None:
            base_name = self.filename.rsplit(".", 1)[0]
            print "line 3047 self.filename", self.filename, base_name
            # Opens the output files for writing the .mdl, .vtx and .vvd files to disk.
            self.mdlfile = open(self.filename,"wb")
            self.vtxfile = open(base_name + ".dx90.vtx","wb")
            self.vvdfile = open(base_name + ".vvd","wb")
            save_mdl(self) # This is the funciton above called to start exporting the model file.
            self.mdlfile.close()
            self.vtxfile.close()
            self.vvdfile.close()


def UIExportDialog(root, filename, editor, comp_group):
    global SpecsList
    SpecsList = """ """
    comp = editor.layout.explorer.sellist[0]
    if len(comp.dictitems['Frames:fg'].subitems) > 1:
        SpecsList = SpecsList + """MakeAnimations: = {Txt = "Make Animation files:" Typ = "X" Hint = "Check this box to create the model's Animation files."$0D"These consist of _animations.mdl & _animations.ani files."}"""
        SpecsList = SpecsList + """MakeGestures: = {Txt = "Make Gesture files:" Typ = "X" Hint = "Check this box to create the model's Gesture files."$0D"These consist of _gestures.mdl & _gestures.ani files."}"""
        SpecsList = SpecsList + """MakePostures: = {Txt = "Make Posture files:" Typ = "X" Hint = "Check this box to create the model's Posture files."$0D"These consist of _postures.mdl & _postures.ani files."}"""

    # Sets up the new window form for the exporters dialog for user selection settings and calls its class.
    form1 = quarkx.newform("masterform")
    if filename.endswith(".mdl"):
        newfiles_folder = filename.replace(".mdl", "")
    ExportSettingsDlg(form1, root, filename, editor, newfiles_folder, comp_group)


##########################################################
# DIALOG SECTION (for frames to export to animation files)
##########################################################
class AnimDlg(quarkpy.dlgclasses.LiveEditDlg):
    size = (250, 500)
    dlgflags = FWF_KEEPFOCUS
    dfsep = 0.8      # sets 80% for labels and the rest for a check box.
    dlgdef = """ """ # The dialog is created in the setup function to allow self generated items.

    def cancel(self, dlg):
        # Modified from dlgclasses.py
        quarkpy.qmacro.dialogbox.close(self, dlg)
        self.src = None


def DialogClick(MDL_DLG, editor, filename, ComponentList, folder_name):
    if editor is None: return
    # Opens animation files to use.
    file = None
    print "line 3093 filename", filename
    print "line 3094 MDL_DLG", MDL_DLG

    def setup(self, editor=editor, MDL_DLG=MDL_DLG, ComponentList=ComponentList):
        global SpecsList2, ani_dlg

        ani_dlg = self
        cur_name = ""
        total_frames = 0
        frame_count = 0
        self.SRCsList = []
        temp = """ """
        frames = ComponentList[0].dictitems['Frames:fg'].subitems
        for frame in frames:
            name = frame.name
            if name.find("baseframe") != -1 or name.find("BaseFrame") != -1:
                continue
            name = name.split(" ")[0]
            if not name in self.SRCsList:
                self.SRCsList = self.SRCsList + [name]
            if cur_name == "":
                frame_count += 1
                cur_name = name
            elif name != cur_name:
                temp = temp + cur_name + """: = {Txt = """
                temp = temp + '"' + cur_name + ' / ' + str(frame_count) + '"'
                temp = temp + """Typ = "X" Hint = "Check this box to export these frames."}"""
                total_frames += frame_count
                frame_count = 1
                cur_name = name
            else:
                frame_count += 1
                cur_name = name
        temp = temp + cur_name + """: = {Txt = """
        temp = temp + '"' + cur_name + ' / ' + str(frame_count) + '"'
        temp = temp + """Typ = "X" Hint = "Check this box to export these frames."}"""
        total_frames += frame_count

        SpecsList2 = """ """
        SpecsList2 = SpecsList2 + """sep: = { Typ="S" Txt="Sequence / nbr of frames"}"""
        SpecsList2 = SpecsList2 + """all: = {Txt = """
        SpecsList2 = SpecsList2 + '"Export All / ' + str(total_frames) + '"'
        SpecsList2 = SpecsList2 + """Typ = "X" Hint = "Check this box ONLY to export all frames."}"""
        SpecsList2 = SpecsList2 + """sep: = { Typ="S" Txt=""}"""
        SpecsList2 = SpecsList2 + temp
        editor.importdlg = self
        self.dlgdef = """
            {
            Style = "13"
            Caption = "mdl Export Items"
            sep: = {
                Typ="S"
                Txt="Instructions: place cursor here"
                Hint = "Place your cursor over each item"$0D
                       "below for a description of what it does."$0D$0D
                       "The more frames = the longer to export (could be minutes)"$0D$0D
                       "To export, check boxes then click the 'Close dialog' button at the very bottom."$0D$0D
                       "You can cancel the entire export process at any time by clearing all"$0D
                       "checked boxes and clicking the 'Close dialog' button at the very bottom."
                   }
            sep: = { Typ="S" Txt="" }

            """ + SpecsList2 + """

            sep: = { Typ="S" Txt="" }
            exit:py = {Txt="Export selections / Close dialog"}
            }
            """

        src = self.src
        self.all = src['all']

    def action(self, editor=editor, MDL_DLG=MDL_DLG):
        src = self.src
        if src['all'] is not None and self.all is None:
            for name in self.SRCsList:
                if src[name] is not None:
                    src[name] = None
        else:
            src['all'] = None

    def onclosing(self, MDL_DLG=MDL_DLG, file=file, editor=editor, filename=filename, ComponentList=ComponentList, folder_name=folder_name):
        global SpecsList2, ani_dlg
        LoadAnim = [] # List for which animation sequences to load.
        src = self.src
        cancel = 0
        print "line 3179 in onclosing", self, MDL_DLG
        if src['all'] is not None:
            for name in self.SRCsList:
                LoadAnim += [1]
                cancel += 1
        else:
            for name in self.SRCsList:
                if src[name] is not None:
                    LoadAnim += [1]
                    cancel += 1
                else:
                    LoadAnim += [0]
        if cancel != 0:
           # MDL_DLG, ComponentList, QuArK_bones = MDL_DLG.load_Animation(ComponentList, QuArK_bones, file, editor, folder_name, LoadAnim)
           # FinishImport(editor, filename, ComponentList, QuArK_bones)
            print "line 3194 saving ani files animations = ", len(LoadAnim), MDL_DLG.mdlfile.name, MDL_DLG.src['MakeMainMDL']
            ani_name = MDL_DLG.mdlfile.name.rsplit(".", 1)[0] + ".ani"
            self.anifile = open(ani_name,"wb")
            save_mdl(MDL_DLG) # This is the funciton above called to start exporting the model file.
            MDL_DLG.mdlfile.close()
            self.anifile.close()
            ani_dlg = None
            SpecsList2 = """ """
            if MDL_DLG.src['MakeMainMDL'] is not None:
                for i in range(len(possible_files)):
                    if MDL_DLG.filename.find(possible_files[i]) != -1:
                        MDL_DLG.filename = MDL_DLG.filename.replace(possible_files[i], "")
                        print "line 3206 going to break", MDL_DLG.filename
                        break
                base_name = MDL_DLG.filename.rsplit(".", 1)[0]
                print "line 3209 MDL_DLG.filename", MDL_DLG.filename
                # Opens the output files for writing the .mdl, .vtx and .vvd files to disk.
                MDL_DLG.mdlfile = open(MDL_DLG.filename,"wb")
                MDL_DLG.vtxfile = open(base_name + ".dx90.vtx","wb")
                MDL_DLG.vvdfile = open(base_name + ".vvd","wb")
                print "line 3214 saving BASE file", MDL_DLG.mdlfile.name
                save_mdl(MDL_DLG) # This is the funciton above called to start exporting the model file.
                MDL_DLG.mdlfile.close()
                MDL_DLG.vtxfile.close()
                MDL_DLG.vvdfile.close()
        else:
            ani_dlg = None
            SpecsList2 = """ """

    # Sets up the new window form for the exporters dialog for user selection settings and calls its class.
    form2 = quarkx.newform("animmasterform")
    AnimDlg(form2, 'animdlg', editor, setup, action, onclosing)


def UIAnimDialog(MDL_DLG, editor, filename, ComponentList, folder_name):
    # Sets up the new window form for the animation dialog for user selection of frames to export and calls its class.
    DialogClick(MDL_DLG, editor, filename, ComponentList, folder_name)



# ----------- REVISION HISTORY ------------
#
# $Log: ie_md0_HL2_export.py,v $
# Revision 1.1  2013/05/30 07:58:11  cdunde
# To start HL2 model exporter.
#
#
