# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for original Half-Life .mdl model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md0_HL1_export.py,v 1.10 2012/07/21 04:19:54 cdunde Exp $


Info = {
   "plug-in":       "ie_md0_HL1_export",
   "desc":          "This script exports a Half-Life file (MDL), textures, and animations from QuArK.",
   "date":          "September 28, 2011",
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
exportername = "ie_md0_HL1_export.py"
textlog = "HL1mdl_ie_log.txt"
progressbar = None
mdl = None
MAX_QPATH = 64

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

    def save(self, file):
        tmpData = [0]*15
        tmpData[0] = self.bone
        tmpData[1] = self.group
        tmpData[2] = self.bbmin[0]
        tmpData[3] = self.bbmin[1]
        tmpData[4] = self.bbmin[2]
        tmpData[5] = self.bbmax[0]
        tmpData[6] = self.bbmax[1]
        tmpData[7] = self.bbmax[2]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7])
        file.write(data)

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


class mdl_skin_info:
# Done cdunde from -> hlmviewer source file -> studio.h -> mstudiotexture_t
    #Header Structure       #item of file, type, description.
    name = ""               #item  0-63   64 char, skin name.
    flags = 0               #item  64     int, skin flags setting for special texture handling ex: None=0 (default), Chrome=2 (cstrike), Chrome=3 (valve), Additive=32, Chrome & Additive=34, Transparent=64.
    width = 0               #item  65     int, skinwidth in pixels.
    height = 0              #item  66     int, skinheight in pixels.
    skin_offset = 0         #item  67     int, index (Offset) to skin data.
    binary_format = "<64s4i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.name = ""
        self.flags = 0
        self.width = 0
        self.height = 0
        self.skin_offset = 0

    def save(self, file):
        tmpData = [0]*5
        tmpData[0] = self.name
        tmpData[1] = self.flags
        tmpData[2] = self.width
        tmpData[3] = self.height
        tmpData[4] = self.skin_offset
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4])
        file.write(data)

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
    mdl.name = dlg.mdlfile.name
    mdl.length = 244 # class mdl_obj binary_format, the .mdl file header.

    if dlg.src['SkinsOnly'] is None:
        ### OFFSET FOR BONES SECTION.
        mdl.bones_offset = mdl.length

        for bone in dlg.bones:
            mdl.QuArK_bones.append(bone.copy())
        mdl.num_bones = len(mdl.QuArK_bones)

        ### OFFSET FOR BONES_CONTROLS SECTION.
        mdl.bone_controls_offset = mdl.bones_offset + (mdl.num_bones * 112) # 112 = class mdl_bone binary_format.

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
        mdl.attachments_offset = mdl.bone_controls_offset + (mdl.num_bone_controls * 24) # 24 = class mdl_bone_control binary_format.

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
        mdl.num_attachments = len(mdl.attachments)

        ### OFFSET FOR HITBOXES SECTION.
        mdl.hitboxes_offset = mdl.attachments_offset + (mdl.num_attachments * 88) # 88 = class mdl_attachment binary_format.

        bone_to_hitbox_data = {} #Store the hitbox data; we need it for bbox calc for the animation sequence later
        if dlg.src['BBoxes'] is not None:
            for key in dlg.bboxlist.keys():
                name = key.split(":p")[0]
                for i in xrange(0, mdl.num_bones):
                    if mdl.QuArK_bones[i].shortname == name:
                        size = dlg.bboxlist[key]['size']
                        hitbox = mdl_hitbox()
                        hitbox.bone = i
                        hitbox.bbmin = size[0]
                        hitbox.bbmax = size[1]
                        mdl.hitboxes.append(hitbox)
                        bone_to_hitbox_data[i] = (quarkx.vect(size[0]), quarkx.vect(size[1]))
                        break
        mdl.num_hitboxes = len(mdl.hitboxes)

        ### OFFSET FOR ANIMATION SEQUENCE_DESC SECTION. (SetUpBones Section in the IMPORTER)
        mdl.anim_seq_offset = mdl.hitboxes_offset + (mdl.num_hitboxes * 32) # 32 = class mdl_hitbox binary_format.

        comp = dlg.comp_list[0]
        comp_framesgroup = comp.dictitems['Frames:fg'].subitems

        #Sort the frames per sequence
        mdl.num_anim_seq = 0
        for i in xrange(0, len(comp_framesgroup)):
            frame_name = comp_framesgroup[i].name
            if frame_name.find("baseframe") != -1:
                continue
            name = frame_name.split(" ")[0]
            if not mdl.QuArK_anim_seq_frames.has_key(name):
                mdl.num_anim_seq += 1
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
            if bbmax is not None:
                anim_seq.bbmax = bbmax

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
        mdl_bone_anim_offset = mdl.anim_seq_offset + (mdl.num_anim_seq * 176) # 176 = class mdl_sequence_desc binary_format.

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
        mdl.demand_hdr_offset = mdl_bone_anim_offset
        mdl.num_demand_hdr_groups = 1
        for i in xrange(mdl.num_demand_hdr_groups):
            mdl.demand_seq_groups.append(mdl_demand_group())

        ### OFFSET FOR BODYPARTS SECTION.
        mdl.transitions_offset = mdl.demand_hdr_offset + (mdl.num_demand_hdr_groups * 104) # 104 = class mdl_demand_group binary_format.
        mdl.bodyparts_offset = mdl.transitions_offset

        mdl.num_bodyparts = 1
        QuArK_models = {}
        QuArK_models['highcount'] = []
        QuArK_models['lowcount'] = []
        for i in xrange(mdl.num_bodyparts):
            bodypart = mdl_bodypart()
            bodypart.model_offset = mdl.bodyparts_offset + (mdl.num_bodyparts * 76) # 76 = class mdl_bodypart binary_format.
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

    if dlg.src['SkinsOnly'] is not None or dlg.src['EmbedSkins'] is not None:
        mdl.num_textures = len(dlg.skins)
        mdl.num_skin_groups = 1
        mdl.num_skin_refs = mdl.num_textures

        ### OFFSETS FOR TEXTURE AND SKIN SECTIONS.
        mdl.texture_index_offset = mdl.length
        mdl.texture_data_offset = mdl.texture_index_offset + (mdl.num_textures * 80) # 80 = class mdl_skin_info binary_format.
        next_skin_offset = 0
        for i in xrange(mdl.num_textures):
            skin_info = mdl_skin_info()
            skin_info.name = dlg.skins[i].name
            if dlg.skins[i].dictspec.has_key('HL_skin_flags'):
                skin_info.flags = int(dlg.skins[i].dictspec['HL_skin_flags'])
            skin_info.name = dlg.skins[i].name
            size = dlg.skins[i].dictspec['Size']
            skin_info.width = int(size[0])
            skin_info.height = int(size[1])
            skin_info.skin_offset = mdl.texture_data_offset + next_skin_offset
          #  skin_info.dump()
            if dlg.skins[i].dictspec.has_key('Pal'): # in 8 bit format
                next_skin_offset += skin_info.width * skin_info.height # Each pixel = 1 type "B" = 1 byte.
                next_skin_offset += 256 * 3 # The skin's Palette data = 256 pixels * 3 type "B" at 1 byte\ea. for a RGB value.
            else: # in 24 bit format (needs fixing)
                next_skin_offset += ((skin_info.width * skin_info.height) * 3) + 54 # Each pixel = 3 type "B" = 1 bytes\ea + bmp_header size.
                
            mdl.skins_group.append(skin_info)
        mdl.skin_refs_offset = mdl.texture_data_offset + next_skin_offset
        mdl.length = mdl.texture_data_offset + (mdl.num_skin_groups * mdl.num_skin_refs * 2) # 2 = 1 short, NO mdl_skin class.
    mdl.dump()


####################################
# Starts By Using the Model Object
####################################
class mdl_obj: # Done cdunde from -> hlmviewer source file -> studio.h -> studiohdr_t
    origin = quarkx.vect(0.0, 0.0, 0.0) ### For QuArK's model placement in the editor.
    #Header Structure          #item of data file, size & type,   description
    ident = "IDST"             #item  0-3   4 char[] string, The version of the file (Must be IDST)
    version = 10               #item  4     int, This is used to identify the file
    name = ""                  #item  5-68  64 char[] string, the models path and full name.
    length = 0                 #item  69    int, length of the file in bytes to EOF.
    eyeposition = [0.0]*3      #item  70-72 3 floats, ideal eye position.
    min = [0.0]*3              #item  73-75 3 floats, ideal movement hull size, min.
    max = [0.0]*3              #item  76-78 3 floats, ideal movement hull size, max.
    bbmin = [0.0]*3            #item  79-81 3 floats, clipping bounding box size, min.
    bbmax = [0.0]*3            #item  82-84 3 floats, clipping bounding box size, max.
    flags = 0                  #item  85    int, unknown item.
    num_bones = 0              #item  86    int, The number of bone for the model.
    bones_offset = 0           #item  87    int, The bones data starting point in the file, in bytes.
    num_bone_controls = 0      #item  88    int, The number of bone controllers.
    bone_controls_offset = 0   #item  89    int, The bones controllers data starting point in the file, in bytes.
    num_hitboxes = 0           #item  90    int, The number of complex bounding boxes.
    hitboxes_offset = 0        #item  91    int, The hitboxes data starting point in the file, in bytes.
    num_anim_seq = 0           #item  92    int, The number of animation sequences for the model.
    anim_seq_offset = 0        #item  93    int, The animation sequences data starting point in the file, in bytes.
    num_demand_hdr_groups = 0  #item  94    int, The number of demand seq groups for the model, demand loaded sequences.
    demand_hdr_offset = 0      #item  95    int, The demand seq groups data starting point in the file, in bytes.
    num_textures = 0           #item  96    int, The number of raw textures.
    texture_index_offset = 0   #item  97    int, The textures data index starting point in the file, in bytes.
    texture_data_offset = 0    #item  98    int, The textures data starting point in the file, in bytes.
    num_skin_refs = 0          #item  99    int, The number of replaceable textures for the model.
    num_skin_groups = 0        #item  100   int, The number of texture groups for the model.
    skin_refs_offset = 0       #item  101   int, The skin ref data starting point in the file, in bytes.
    num_bodyparts = 0          #item  102   int, The number of body parts for the model.
    bodyparts_offset = 0       #item  103   int, The body parts data starting point in the file, in bytes.
    num_attachments = 0        #item  104   int, The number of queryable attachable points for the model.
    attachments_offset = 0     #item  105   int, The queryable attachable points data starting point in the file, in bytes.
    sound_table = 0            #item  106   int, unknown item.
    sound_table_offset = 0     #item  107   int, The sound table data starting point in the file, in bytes.
    sound_groups = 0           #item  108   int, unknown item.
    sound_groups_offset = 0    #item  109   int, The sound groups data starting point in the file, in bytes.
    num_transitions = 0        #item  110   int, The number of animation node to animation node transition graph.
    transitions_offset = 0     #item  111   int, The transitions data starting point in the file, in bytes.

    binary_format = "<4si64si3f3f3f3f3f27i" #little-endian (<), see #item descriptions above.

    #mdl data objects
    bones = []
    QuArK_bones = []
    skins_group = []
    skinrefs = []
    demand_seq_groups = []
    bone_controls = []
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

    def __init__ (self):
        self.bones = []             # A list of the bones.
        self.QuArK_bones = []       # A list of the QuArK bones, for our use only.
        self.skins_group = []       # A list of the skins.
        self.skinrefs = []          # A list of the skinref data.
        self.demand_seq_groups = [] # A list of the demand sequence groups.
        self.bone_controls = []     # A list of the bone controllers.
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

    def save(self, dlg):
        global progressbar
        # file = the actual .mdl model file being written to, exported.
        file = dlg.mdlfile

        # Write the header
        data = struct.pack(self.binary_format,
        self.ident,
        self.version,
        self.name,
        self.length,
        self.eyeposition[0], self.eyeposition[1], self.eyeposition[2],
        self.min[0], self.min[1], self.min[2],
        self.max[0], self.max[1], self.max[2],
        self.bbmin[0], self.bbmin[1], self.bbmin[2],
        self.bbmax[0], self.bbmax[1], self.bbmax[2],
        self.flags,
        self.num_bones,
        self.bones_offset,
        self.num_bone_controls,
        self.bone_controls_offset,
        self.num_hitboxes,
        self.hitboxes_offset,
        self.num_anim_seq,
        self.anim_seq_offset,
        self.num_demand_hdr_groups,
        self.demand_hdr_offset,
        self.num_textures,
        self.texture_index_offset,
        self.texture_data_offset,
        self.num_skin_refs,
        self.num_skin_groups,
        self.skin_refs_offset,
        self.num_bodyparts,
        self.bodyparts_offset,
        self.num_attachments,
        self.attachments_offset,
        self.sound_table,
        self.sound_table_offset,
        self.sound_groups,
        self.sound_groups_offset,
        self.num_transitions,
        self.transitions_offset)
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
        for i in xrange(self.num_attachments):
            self.attachments[i].save(file)
          #  self.attachments[i].dump()

        # write the hitboxes data, can only have one per bone and visa versa.
        for i in xrange(self.num_hitboxes):
            self.hitboxes[i].save(file)
          #  self.hitboxes[i].dump()

        # write the animation sequence descriptions data.
        for i in xrange(self.num_anim_seq):
            self.sequence_descs[i].save(file)
          #  self.sequence_descs[i].dump()

        # write the animation sequence data.
        for i in xrange(self.num_anim_seq):
            # write the bone anim data.
            for j in xrange(len(self.sequence_descs[i].anim_bones)):
                self.sequence_descs[i].anim_bones[j].save(file)
                #  self.sequence_descs[i].anim_bones[j].dump()
            # write the bone anim value data.
            for j in xrange(len(self.sequence_descs[i].anim_bones)):
                for k in xrange(6):
                    file.write(self.QuArK_anim_data[i][j][k])

        # write the header for demand sequence group data
        for i in xrange(self.num_demand_hdr_groups):
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

        # write the skin image data for each skin, texture_data_offset
        for i in xrange(self.num_textures):
            skin = self.skins_group[i]
            skin_width = skin.width
            skin_height = skin.height
            if dlg.skins[i].dictspec.has_key('Pal'):
                #Pixel data first in 8 bit format
                ImageData = dlg.skins[i]['Image1']
                MdlSkinData = ''
                for y in range(skin_height):
                    for x in range(skin_width):
                        MdlSkinData += struct.pack("B", ord(ImageData[(skin_height-y-1) * skin_width+x]))
                file.write(MdlSkinData)
                #Palette data is next in 8 bit format
                ImageData = dlg.skins[i]['Pal']
                MdlSkinData = ''
                for k in xrange(0, 256*3):
                    MdlSkinData += struct.pack("B", ord(ImageData[k]))
                file.write(MdlSkinData)
            else:
                #Pixel data in 24 bit format, NEEDS FIXING
                header = bmp_header
                header["width"] = skin_width
                header["height"] = skin_height
                ImageData = dlg.skins[i]['Image1']
                MdlSkinData = make_bmp_header(header)
                for k in xrange(54, ((skin_width*skin_height)*3)+54):
                    try:
                        MdlSkinData += struct.pack("B", ord(ImageData[k]))
                    except:
                        break
                file.write(MdlSkinData)

        # Loop over the number of num_skin_groups, always 1 (no class was given)
        for i in xrange(self.num_skin_groups):
            # Write the skin ref data (no class was given), skin_refs_offset
            binary_format = "<h"
            for j in xrange(self.num_skin_refs):
                data = struct.pack(binary_format, j)
                file.write(data)

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
# filename = the model file & full path being writen to, ex: C:\Half-Life\valve\models\player\barney\barney.mdl
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
# For example:  C:\Half-Life\valve\models\player\barney\barney.mdl
# gamename is None.
def savemodel(root, filename, gamename, nomessage=0):
    global editor
    editor = quarkpy.mdleditor.mdleditor
    if editor is None:
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
quarkpy.qmdlbase.RegisterMdlExporter(".mdl Half-Life1 Exporter", ".mdl file", "*.mdl", savemodel)


######################################################
# DIALOG SECTION (which calls to export an .mdl file)
######################################################
class ExportSettingsDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (200, 300)
    dfsep = 0.65     # sets 65% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """
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

        EmbedSkins: =
            {
            Txt = "Embed Skin Textures:"
            Typ = "X"
            Hint = "Check this box to embed the component's skins into the model file."$0D
                   "Most HL1 models contain their actual skin(s) texture within the file."
            }

        Skins: =
            {
            Txt = "Export Skin Textures:"
            Typ = "X"
            Hint = "Check this box to export the component's skins as bmp files."$0D
                   "These files may need to be moved to other folders."
            }

        SkinsOnly: =
            {
            Txt = "Make Skins Only Model:"
            Typ = "X"
            Hint = "Check this box to make a model with skin names only."$0D
                   "Some HL1 models do use this kind of model,"$0D
                   "with the same name but ends with 'T' added to it."
            }

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

    def __init__(self, form1, root, filename, editor, newfiles_folder, comp_group): # Creates the dialogbox.
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
        src['EmbedSkins'] = "1"
        src['Skins'] = None
        src['SkinsOnly'] = None
        src['makefolder'] = None
        self.src = src

        # Create the dialog form and the buttons.
        quarkpy.qmacro.dialogbox.__init__(self, form1, src,
            MakeFiles = quarkpy.qtoolbar.button(self.MakeFiles,"DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.",ico_editor, 3, "Export Model"),
            close = quarkpy.qtoolbar.button(self.close, "DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.", ico_editor, 0, "Cancel Export")
            )

    def datachange(self, df):
        if self.src['SkinsOnly'] == "1" and not (self.src['dummy'] is None):
            self.src['Tags'] = None
            self.src['BBoxes'] = None
            self.src['dummy'] = None
        elif self.src['Tags'] == "1" and self.src['SkinsOnly'] == "1":
            self.src['SkinsOnly'] = None
            self.src['dummy'] = "1"
        elif self.src['BBoxes'] == "1" and self.src['SkinsOnly'] == "1":
            self.src['SkinsOnly'] = None
            self.src['dummy'] = "1"
        elif (self.src['Tags'] == "1" or self.src['BBoxes'] == "1") and self.src['dummy'] is None:
            self.src['dummy'] = "1"
            
        df.setdata(self.src, self.f) # This line updates the dialog.

    def MakeFiles(self, btn):
        # Accepts all entries then starts making the processing function calls.
        quarkx.globalaccept()
        root = self.root

        self.tags = []
        self.bboxlist = {}
        self.skins = []
        self.bones = []

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

        if self.src['EmbedSkins'] is not None or self.src['SkinsOnly'] is not None:
            skin_names = []
            for comp in self.comp_list:
                for skin in comp.dictitems['Skins:sg'].subitems:
                    if not skin.name in skin_names:
                        self.skins.append(skin)
                        skin_names.append(skin.name)

        if self.src['Skins'] is not None:
            skin_names = []
            for comp in self.comp_list:
                for skin in comp.dictitems['Skins:sg'].subitems:
                    if not skin.name in skin_names:
                        skin_names.append(skin.name)
                    else:
                        continue
                    tempfilename = self.filename.replace("\\", "/")
                    tempfilename = tempfilename.rsplit("/", 1)[0]
                    tempskinname = skin.name.replace("\\", "/")
                    tempskinname = tempskinname.rsplit("/", 1)[1]
                    skin.filename = tempfilename + '/' + tempskinname
                    quarkx.savefileobj(skin, FM_Save, 4)

        if self.src['SkinsOnly'] is None:
            skeletongroup = self.editor.Root.dictitems['Skeleton:bg']  # get the bones group
            bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
            for bone in bones:
                if bone.name.startswith(self.comp_group):
                    self.bones.append(bone)
            if len(self.bones) == 0:
                quarkx.msgbox("No Bones exist for exporting.\n\nAt least one bone is needed to position the model.\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
        else:
            if not self.filename.endswith("T.mdl"):
                self.filename = self.filename.rsplit('.', 1)[0]
                self.filename = self.filename + "T.mdl"

        # Opens the output file for writing the .mdl file to disk.
        self.mdlfile = open(self.filename,"wb")
        save_mdl(self) # This is the funciton above called to start exporting the model file.
        self.mdlfile.close()


def UIExportDialog(root, filename, editor, comp_group):
    # Sets up the new window form for the exporters dialog for user selection settings and calls its class.
    form1 = quarkx.newform("masterform")
    if filename.endswith(".mdl"):
        newfiles_folder = filename.replace(".mdl", "")
    ExportSettingsDlg(form1, root, filename, editor, newfiles_folder, comp_group)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_md0_HL1_export.py,v $
# Revision 1.10  2012/07/21 04:19:54  cdunde
# File cleanup.
#
# Revision 1.9  2012/03/10 10:00:39  cdunde
# Added texture skin flag support.
#
# Revision 1.8  2012/03/04 00:02:32  cdunde
# DanielPharos code for normals and dialog settings.
#
# Revision 1.7  2012/03/03 07:26:35  cdunde
# Sync 2. Rearranged files and names to coincide better.
#
# Revision 1.6  2012/02/25 23:52:08  cdunde
# Fixes by DanielPharos for correct skin texture matching to components.
#
# Revision 1.5  2012/02/18 23:11:19  cdunde
# Code by DanielPharos, final fix for correct exported animations.
#
# Revision 1.4  2012/02/12 03:40:56  cdunde
# Code by DanielPharos to export animations.
#
# Revision 1.3  2012/01/30 03:15:06  cdunde
# Fix by DanielPharos to correctly position vertexes of the meshes with their 'baseframe' bones.
#
# Revision 1.2  2012/01/11 19:25:45  cdunde
# To remove underscore lines from folder and model names then combine them with one
# underscore line at the end for proper editor functions separation capabilities later.
#
# Revision 1.1  2011/12/23 22:33:43  cdunde
# Added export support for Half-Life 1 static and animation models with bones .mdl file types.
# Still needs work, see TODO NOTES at top of file.
#
#
