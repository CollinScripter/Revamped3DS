# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Doom3\Quake4 .md5mesh and .md5anim model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md5_import.py,v 1.49 2012/01/15 07:08:00 cdunde Exp $


Info = {
   "plug-in":       "ie_md5_importer",
   "desc":          "This script imports a Doom3\Quake4 .md5mesh and .md5anim model file, textures, and animations into QuArK for editing. Original code from Blender, md5Import_0.5.py, author - Bob Holcomb.",
   "date":          "Dec 5 2008",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 2" }

import sys, struct, os
from types import *
import quarkx
import quarkpy.qutils
import quarkpy.qhandles
import quarkpy.qtoolbar
import quarkpy.mdlhandles
import quarkpy.mdlutils
import ie_utils
from os import path
from ie_utils import tobj
import math
from math import *
from quarkpy.qdictionnary import Strings
from quarkpy.qeditor import ico_dict # Get the dictionary list of all icon image files available.
from quarkpy.qeditor import MapColor # Strictly needed for QuArK bones MapColor call.

# Globals
SS_MODEL = 3
md5_mesh_path = None
md5_anim_path = None
md5_model = None
md5_bones = None
md5_model_comps = []
logging = 0
importername = "ie_md5_import.py"
textlog = "md5_ie_log.txt"
editor = None
progressbar = None


######################################################
# Vector, Quaterion, Matrix math stuff - some taken from
# Jiba's blender2cal3d script
######################################################
def quaternion2matrix(q):
    xx = q[0] * q[0]
    yy = q[1] * q[1]
    zz = q[2] * q[2]
    xy = q[0] * q[1]
    xz = q[0] * q[2]
    yz = q[1] * q[2]
    wx = q[3] * q[0]
    wy = q[3] * q[1]
    wz = q[3] * q[2]
    return [[1.0 - 2.0 * (yy + zz),       2.0 * (xy + wz),       2.0 * (xz - wy), 0.0],
            [      2.0 * (xy - wz), 1.0 - 2.0 * (xx + zz),       2.0 * (yz + wx), 0.0],
            [      2.0 * (xz + wy),       2.0 * (yz - wx), 1.0 - 2.0 * (xx + yy), 0.0],
            [0.0                  , 0.0                  , 0.0                  , 1.0]]

def matrix2quaternion(m):
    s = math.sqrt(abs(m[0][0] + m[1][1] + m[2][2] + m[3][3]))
    if s == 0.0:
        x = abs(m[2][1] - m[1][2])
        y = abs(m[0][2] - m[2][0])
        z = abs(m[1][0] - m[0][1])
        if   (x >= y) and (x >= z):
            return 1.0, 0.0, 0.0, 0.0
        elif (y >= x) and (y >= z):
            return 0.0, 1.0, 0.0, 0.0
        else:
            return 0.0, 0.0, 1.0, 0.0
    return quaternion_normalize([
        -(m[2][1] - m[1][2]) / (2.0 * s),
        -(m[0][2] - m[2][0]) / (2.0 * s),
        -(m[1][0] - m[0][1]) / (2.0 * s),
        0.5 * s,
        ])

def quaternion_normalize(q):
    l = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
    return q[0] / l, q[1] / l, q[2] / l, q[3] / l

def quaternion_multiply(q1, q2):
    r = [
            q2[3] * q1[0] + q2[0] * q1[3] + q2[1] * q1[2] - q2[2] * q1[1],
            q2[3] * q1[1] + q2[1] * q1[3] + q2[2] * q1[0] - q2[0] * q1[2],
            q2[3] * q1[2] + q2[2] * q1[3] + q2[0] * q1[1] - q2[1] * q1[0],
            q2[3] * q1[3] - q2[0] * q1[0] - q2[1] * q1[1] - q2[2] * q1[2],
        ]
    d = math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2] + r[3] * r[3])
    r[0] /= d
    r[1] /= d
    r[2] /= d
    r[3] /= d
    return r

def matrix_translate(m, v):
    v = v.tuple
    m[3][0] += v[0]
    m[3][1] += v[1]
    m[3][2] += v[2]
    return m

def matrix_multiply(b, a):
    return [ [
        a[0][0] * b[0][0] + a[0][1] * b[1][0] + a[0][2] * b[2][0],
        a[0][0] * b[0][1] + a[0][1] * b[1][1] + a[0][2] * b[2][1],
        a[0][0] * b[0][2] + a[0][1] * b[1][2] + a[0][2] * b[2][2],
        0.0,
        ], [
        a[1][0] * b[0][0] + a[1][1] * b[1][0] + a[1][2] * b[2][0],
        a[1][0] * b[0][1] + a[1][1] * b[1][1] + a[1][2] * b[2][1],
        a[1][0] * b[0][2] + a[1][1] * b[1][2] + a[1][2] * b[2][2],
        0.0,
        ], [
        a[2][0] * b[0][0] + a[2][1] * b[1][0] + a[2][2] * b[2][0],
        a[2][0] * b[0][1] + a[2][1] * b[1][1] + a[2][2] * b[2][1],
        a[2][0] * b[0][2] + a[2][1] * b[1][2] + a[2][2] * b[2][2],
         0.0,
        ], [
        a[3][0] * b[0][0] + a[3][1] * b[1][0] + a[3][2] * b[2][0] + b[3][0],
        a[3][0] * b[0][1] + a[3][1] * b[1][1] + a[3][2] * b[2][1] + b[3][1],
        a[3][0] * b[0][2] + a[3][1] * b[1][2] + a[3][2] * b[2][2] + b[3][2],
        1.0,
        ] ]

def matrix_invert(m):
    det = (m[0][0] * (m[1][1] * m[2][2] - m[2][1] * m[1][2])
         - m[1][0] * (m[0][1] * m[2][2] - m[2][1] * m[0][2])
         + m[2][0] * (m[0][1] * m[1][2] - m[1][1] * m[0][2]))
    if det == 0.0:
        return None
    det = 1.0 / det
    r = [ [
        det * (m[1][1] * m[2][2] - m[2][1] * m[1][2]),
      - det * (m[0][1] * m[2][2] - m[2][1] * m[0][2]),
        det * (m[0][1] * m[1][2] - m[1][1] * m[0][2]),
        0.0,
      ], [
      - det * (m[1][0] * m[2][2] - m[2][0] * m[1][2]),
        det * (m[0][0] * m[2][2] - m[2][0] * m[0][2]),
      - det * (m[0][0] * m[1][2] - m[1][0] * m[0][2]),
        0.0
      ], [
        det * (m[1][0] * m[2][1] - m[2][0] * m[1][1]),
      - det * (m[0][0] * m[2][1] - m[2][0] * m[0][1]),
        det * (m[0][0] * m[1][1] - m[1][0] * m[0][1]),
        0.0,
      ] ]
    r.append([
      -(m[3][0] * r[0][0] + m[3][1] * r[1][0] + m[3][2] * r[2][0]),
      -(m[3][0] * r[0][1] + m[3][1] * r[1][1] + m[3][2] * r[2][1]),
      -(m[3][0] * r[0][2] + m[3][1] * r[1][2] + m[3][2] * r[2][2]),
      1.0,
      ])
    return r

def matrix_rotate_x(angle):
    cos = math.cos(angle)
    sin = math.sin(angle)
    return [
        [1.0,  0.0, 0.0, 0.0],
        [0.0,  cos, sin, 0.0],
        [0.0, -sin, cos, 0.0],
        [0.0,  0.0, 0.0, 1.0],
    ]

def matrix_rotate_y(angle):
    cos = math.cos(angle)
    sin = math.sin(angle)
    return [
        [cos, 0.0, -sin, 0.0],
        [0.0, 1.0,  0.0, 0.0],
        [sin, 0.0,  cos, 0.0],
        [0.0, 0.0,  0.0, 1.0],
    ]

def matrix_rotate_z(angle):
    cos = math.cos(angle)
    sin = math.sin(angle)
    return [
        [ cos, sin, 0.0, 0.0],
        [-sin, cos, 0.0, 0.0],
        [ 0.0, 0.0, 1.0, 0.0],
        [ 0.0, 0.0, 0.0, 1.0],
    ]

def matrix_rotate(axis, angle):
    vx  = axis[0]
    vy  = axis[1]
    vz  = axis[2]
    vx2 = vx * vx
    vy2 = vy * vy
    vz2 = vz * vz
    cos = math.cos(angle)
    sin = math.sin(angle)
    co1 = 1.0 - cos
    return [
        [vx2 * co1 + cos,          vx * vy * co1 + vz * sin, vz * vx * co1 - vy * sin, 0.0],
        [vx * vy * co1 - vz * sin, vy2 * co1 + cos,          vy * vz * co1 + vx * sin, 0.0],
        [vz * vx * co1 + vy * sin, vy * vz * co1 - vx * sin, vz2 * co1 + cos,          0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
  # return [
  #     [vx2 * co1 + cos,          vx * vy * co1 + vz * sin, vz * vx * co1 - vy * sin, 0.0],
  #     [vz * vx * co1 + vy * sin, vy * vz * co1 - vx * sin, vz2 * co1 + cos,          0.0],
  #     [vx * vy * co1 - vz * sin, vy2 * co1 + cos,          vy * vz * co1 + vx * sin, 0.0],
  #     [0.0, 0.0, 0.0, 1.0],
  # ]
  
def matrix_scale(fx, fy, fz):
  return [
        [ fx, 0.0, 0.0, 0.0],
        [0.0,  fy, 0.0, 0.0],
        [0.0, 0.0,  fz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]

def point_by_matrix(p, m):
  return [
        p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + m[3][0],
        p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + m[3][1],
        p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + m[3][2]
    ]

def point_distance(p1, p2):
  return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)

def vector_by_matrix(p, m):
  return [
        p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0],
        p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1],
        p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2]
    ]

def vector_length(v):
    v = v.tuple
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length == 0.0:
        length = 1.0
    return length

def vector_normalize(v):
    v = v.tuple
    l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    try:
        return v[0] / l, v[1] / l, v[2] / l
    except:
        return 1, 0, 0

def vector_dotproduct(v1, v2):
    v1 = v1.tuple
    v2 = v2.tuple
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def vector_crossproduct(v1, v2):
    v1 = v1.tuple
    v2 = v2.tuple
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    ]

def vector_angle(v1, v2):
    s = vector_length(v1) * vector_length(v2)
    f = vector_dotproduct(v1, v2) / s
    if f >=  1.0:
        return 0.0
    if f <= -1.0:
        return math.pi / 2.0
    return math.atan(-f / math.sqrt(1.0 - f * f)) + math.pi / 2.0


######################################################
# MD5 DATA STRUCTURES
######################################################
class md5_vert:
    vert_index=0
    co=[]
    uvco=[]
    blend_index=0
    blend_count=0

    def __init__(self):
        self.vert_index=0
        self.co=[0.0]*3
        self.uvco=[0.0]*2
        self.blend_index=0
        self.blend_count=0

    def dump(self):
        print "vert index: ", self.vert_index
        print "co: ", self.co
        print "uvco: ", self.uvco
        print "blend index: ", self.blend_index
        print "belnd count: ", self.blend_count

class md5_weight:
    weight_index=0
    bone_index=0
    bias=0.0
    weights=()

    def __init__(self):
        self.weight_index=0
        self.bone_index=0
        self.bias=0.0
        self.weights=(0.0)*3

    def dump(self):
        print "weight index: ", self.weight_index
        print "bone index: ", self.bone_index
        print "bias: ", self.bias
        print "weighst: ", self.weights

class md5_bone:
    bone_index=0
    name=""
    bindpos=[]
    bindmat=[]
    parent=""
    parent_index=0
    blenderbone=None
    roll=0

    def __init__(self):
        self.bone_index=0
        self.name=""
        self.bindpos=[0.0]*3
        self.bindmat=[None]*3 # This how you initilize a 2d-array.
        for i in range(3):
            self.bindmat[i] = [0.0]*3
        self.parent=""
        self.parent_index=0
        self.blenderbone=None

    def dump(self):
        print "bone index: ", self.bone_index
        print "name: ", self.name
        print "bind position: ", self.bindpos
        print "bind translation matrix (mat): ", self.bindmat
        print "parent: ", self.parent
        print "parent index: ", self.parent_index
        print "blenderbone: ", self.blenderbone


class md5_tri:
    tri_index=0
    vert_index=[]

    def __init__(self):
        self.tri_index=0;
        self.vert_index=[0]*3

    def dump(self):
        print "tri index: ", self.tri_index
        print "vert index: ", self.vert_index

class md5_mesh:
    mesh_index=0
    verts=[]
    tris=[]
    weights=[]
    shader=""

    def __init__(self):
        self.mesh_index=0
        self.verts=[]
        self.tris=[]
        self.weights=[]
        self.shader=""

    def dump(self):
        print "mesh index: ", self.mesh_index
        print "verts: ", self.verts
        print "tris: ", self.tris
        print "weights: ", self.weights
        print "shader: ", self.shader


######################################################
# IMPORT A MESH FILE ONLY SECTION
######################################################
def load_md5(md5_filename, basepath, actionname):
    global md5_model, md5_model_comps, md5_bones, progressbar, tobj, logging, Strings

    md5_model_comps = []
    filename = actionname.replace(".md5mesh", "")
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
    QuArK_bones = []         # A list to store all QuArK bones created from the .md5mesh file "joints" section.
                             # [ bone1, bone2,...]
    QuArK_weights_list = {}  # A list to store all QuArK  "weights" created from the .md5mesh "verts" section for each mesh.
                             # {mesh_index : vert_index :[weight_index, nbr_of_weights]}

    #read the file in
    # md5_filename = the full path and file name of the .md5mesh file being imported, ex.
    # "C:\Program Files\Doom 3\base\models\md5\monsters\pinky\pinky.md5mesh"
    file=open(md5_filename,"r")
    lines=file.readlines()
    file.close()

    md5_model=[]
    md5_bones=[]

    num_lines=len(lines)

    for line_counter in range(0,num_lines):
        current_line=lines[line_counter]
        words=current_line.split()

    mesh_counter=0
    progressbar = quarkx.progressbar(2454, num_lines)
    for line_counter in range(0,num_lines):
        progressbar.progress()
        current_line=lines[line_counter]
        words=current_line.split()
        ### BONES start here., see class md5_bone above.
        if words and words[0]=="numJoints":
            num_bones=int(words[1])
        elif words and words[0]=="joints":
            # Go to next line.
            line_counter+=1
            for bone_counter in range(0,num_bones): # num_bones = "numJoints" in md5mesh file (including "origin") as an integer.
                current_line=lines[line_counter]
                #skip over blank lines
                while len(current_line) == 0:
                    line_counter+=1
                    current_line=lines[line_counter]
                #make a new bone
                md5_bones.append(md5_bone())
                # Change in case name has blank spaces in it.
                words=current_line.rsplit('\"', 1)
                words[0] = words[0].replace('\"', "").strip()
                words[1] = words[1].split()
                line = [words[0]]
                for word in words[1]:
                    line = line + [word]
                words = line
                md5_bones[bone_counter].bone_index=bone_counter
                #get rid of the quotes on either side
                temp_name=words[0]
                ### QuArK note: this is where we start making our bones.
                new_bone = quarkx.newobj(filename + "_" + temp_name + ":bone")
                new_bone['type'] = 'md5' # Set our bone type.
                new_bone['flags'] = (0,0,0,0,0,0)
                new_bone['show'] = (1.0,)
                new_bone['position'] = (float(words[3]), float(words[4]), float(words[5]))
                new_bone.position = quarkx.vect(new_bone.dictspec['position'])
                new_bone['parent_index'] = words[1] # QuArK code, this is NOT an integer but a string of its integer value.
                if int(new_bone.dictspec['parent_index']) == -1:
                    new_bone['parent_name'] = "None"
                    new_bone['bone_length'] = (0.0, 0.0, 0.0)
                else:
                    new_bone['parent_name'] = QuArK_bones[int(new_bone.dictspec['parent_index'])].name
                    new_bone['bone_length'] = (-quarkx.vect(QuArK_bones[int(new_bone.dictspec['parent_index'])].dictspec['position']) + quarkx.vect(new_bone.dictspec['position'])).tuple
                new_bone['rotmatrix'] = (1., 0., 0., 0., 1., 0., 0., 0., 1.)
                new_bone['scale'] = (1.0,)
                new_bone['component'] = "None" # None for now and get the component name later.
                new_bone['draw_offset'] = (0.0, 0.0, 0.0)
                new_bone['_color'] = MapColor("BoneHandles", 3)
                new_bone['bindmat'] = (float(words[8]), float(words[9]), float(words[10])) # QuArK code, use these values to build this bones matrix (see "quaternion2matrix" code below).
                new_bone.rotmatrix = quarkx.matrix((1, 0, 0), (0, 1, 0), (0, 0, 1))
                new_bone.vtxlist = {}
                new_bone.vtx_pos = {}

                # QuArK code below, adjust to handles jointscale for other bones connecting to this one and so on.
                jointscale = 1.0
                if bone_counter == 0:
                    parent_bone_scale = jointscale
                else:
                    parent_bone_scale = QuArK_bones[int(new_bone.dictspec['parent_index'])].dictspec['scale'][0]
                if abs(new_bone.dictspec['bone_length'][0]) > abs(new_bone.dictspec['bone_length'][1]):
                    if  abs(new_bone.dictspec['bone_length'][0]) > abs(new_bone.dictspec['bone_length'][2]):
                        testscale = abs(new_bone.dictspec['bone_length'][0])
                    else:
                        testscale = abs(new_bone.dictspec['bone_length'][2])
                else:
                    if  abs(new_bone.dictspec['bone_length'][1]) > abs(new_bone.dictspec['bone_length'][2]):
                        testscale = abs(new_bone.dictspec['bone_length'][1])
                    else:
                        testscale = abs(new_bone.dictspec['bone_length'][2])
                if testscale < 8:
                    jointscale = jointscale - (testscale * .08)

                if jointscale < 0.1:
                    jointscale = 0.1
                elif jointscale > parent_bone_scale:
                    jointscale = parent_bone_scale

                new_bone['scale'] = (jointscale,) # Written this way to store it as a tuple.

                md5_bones[bone_counter].name=temp_name
                md5_bones[bone_counter].parent_index = int(words[1])
                if md5_bones[bone_counter].parent_index>=0:
                    md5_bones[bone_counter].parent = md5_bones[md5_bones[bone_counter].parent_index].name
                md5_bones[bone_counter].bindpos[0]=float(words[3])
                md5_bones[bone_counter].bindpos[1]=float(words[4])
                md5_bones[bone_counter].bindpos[2]=float(words[5])
                qx = float(words[8])
                qy = float(words[9])
                qz = float(words[10])
                qw = 1 - qx*qx - qy*qy - qz*qz
                if qw<0:
                    qw=0
                else:
                    qw = -sqrt(qw)
                md5_bones[bone_counter].bindmat = quaternion2matrix([qx,qy,qz,qw])

                tempmatrix = md5_bones[bone_counter].bindmat
                new_bone['rotmatrix'] = (tempmatrix[0][0], tempmatrix[1][0], tempmatrix[2][0], tempmatrix[0][1], tempmatrix[1][1], tempmatrix[2][1], tempmatrix[0][2], tempmatrix[1][2], tempmatrix[2][2])
                new_bone.rotmatrix = quarkx.matrix((tempmatrix[0][0], tempmatrix[1][0], tempmatrix[2][0]), (tempmatrix[0][1], tempmatrix[1][1], tempmatrix[2][1]), (tempmatrix[0][2], tempmatrix[1][2], tempmatrix[2][2]))
                QuArK_bones = QuArK_bones + [new_bone]
                #next line
                line_counter+=1

           # for bone in md5_bones:
           #     bone.dump()

        elif words and words[0]=="numMeshes":
            num_meshes=int(words[1])

        elif words and words[0]=="mesh":
            # Create a new mesh and name it.
            md5_model.append(md5_mesh())
            md5_model[mesh_counter].mesh_index = mesh_counter
            while (not words or (words and words[0]!="}")):
                line_counter+=1
                current_line=lines[line_counter]
                words=current_line.split()
                if words and words[0]=="shader":
                    temp_name=str(" ".join(words[1:]))
                    temp_name=temp_name[1:-1]
                    md5_model[mesh_counter].shader=temp_name
                if words and words[0]=="vert":
                    md5_model[mesh_counter].verts.append(md5_vert())
                    vert_counter=len(md5_model[mesh_counter].verts)-1
                    #load it with the raw data
                    md5_model[mesh_counter].verts[vert_counter].vert_index=int(words[1])
                    md5_model[mesh_counter].verts[vert_counter].uvco[0]=float(words[3])
                    md5_model[mesh_counter].verts[vert_counter].uvco[1]=(1-float(words[4]))
                    md5_model[mesh_counter].verts[vert_counter].blend_index=int(words[6])
                    md5_model[mesh_counter].verts[vert_counter].blend_count=int(words[7])
                if words and words[0]=="tri":
                    md5_model[mesh_counter].tris.append(md5_tri())
                    tri_counter=len(md5_model[mesh_counter].tris)-1
                    #load it with raw data
                    md5_model[mesh_counter].tris[tri_counter].tri_index=int(words[1])
                    md5_model[mesh_counter].tris[tri_counter].vert_index[0]=int(words[2])
                    md5_model[mesh_counter].tris[tri_counter].vert_index[1]=int(words[3])
                    md5_model[mesh_counter].tris[tri_counter].vert_index[2]=int(words[4])
                if words and words[0]=="weight":
                    md5_model[mesh_counter].weights.append(md5_weight())
                    weight_counter=len(md5_model[mesh_counter].weights)-1
                    #load it with raw data
                    md5_model[mesh_counter].weights[weight_counter].weight_index=int(words[1])
                    md5_model[mesh_counter].weights[weight_counter].bone_index=int(words[2])
                    md5_model[mesh_counter].weights[weight_counter].bias=float(words[3])
                    md5_model[mesh_counter].weights[weight_counter].weights = (float(words[5]), float(words[6]), float(words[7]))
                    #md5_model[mesh_counter].weights[weight_counter].dump()

            mesh_counter += 1
    progressbar.close()

    #figure out the base pose for each vertex from the weights
    bone_vtx_list = {} # { bone_index : { mesh_index : [ vtx, vtx, vtx ...] } }
    ModelComponentList = {} # { mesh_index : { bone_index : {vtx_index : {'color': '\x00\x00\xff', weight: 1.0} } } }
    mesh_count = 0
    for mesh in md5_model:
       # mesh.dump()
        mesh_count += 1
        Strings[2458] = "md5 mesh " + str(mesh_count) + "\n" + Strings[2458]
        progressbar = quarkx.progressbar(2458, len(mesh.verts))
        for vert_counter in range(0, len(mesh.verts)):
            progressbar.progress()
            blend_index=mesh.verts[vert_counter].blend_index
            for blend_counter in range(0, mesh.verts[vert_counter].blend_count):
                #get the current weight info
                w=mesh.weights[blend_index+blend_counter]
                #w.dump()
                #the bone that the current weight is refering to
                b=md5_bones[w.bone_index]
                weight_index = blend_index+blend_counter
                weight_value = md5_model[mesh.mesh_index].weights[weight_index].bias
                bonename = filename + "_" + b.name + ":bone"
                # QuArK code.
                if not QuArK_weights_list.has_key(mesh.mesh_index):
                    QuArK_weights_list[mesh.mesh_index] = {}
                if not QuArK_weights_list[mesh.mesh_index].has_key(vert_counter):
                    QuArK_weights_list[mesh.mesh_index][vert_counter] = {}
                weight_data = {}
                weight_data['weight_value'] = weight_value
                weight_data['color'] = quarkpy.mdlutils.weights_color(editor, weight_value)
                QuArK_weights_list[mesh.mesh_index][vert_counter][bonename] = weight_data

                if not mesh.mesh_index in ModelComponentList.keys():
                    ModelComponentList[mesh.mesh_index] = {}
                if not w.bone_index in ModelComponentList[mesh.mesh_index].keys():
                    ModelComponentList[mesh.mesh_index][w.bone_index] = {}
                if not vert_counter in ModelComponentList[mesh.mesh_index][w.bone_index].keys():
                    ModelComponentList[mesh.mesh_index][w.bone_index][vert_counter] = {}
                if not w.bone_index in bone_vtx_list.keys():
                    bone_vtx_list[w.bone_index] = {}
                if not mesh.mesh_index in bone_vtx_list[w.bone_index].keys():
                    bone_vtx_list[w.bone_index][mesh.mesh_index] = []
                if not vert_counter in bone_vtx_list[w.bone_index][mesh.mesh_index]:
                    bone_vtx_list[w.bone_index][mesh.mesh_index] = bone_vtx_list[w.bone_index][mesh.mesh_index] + [vert_counter]
                #print "b: "
                #b.dump()
                pos=[0.0]*3
                #print "pos: ", pos
                # First, pos = the (w.weights) weight's vector x,y,z position * the (b.bindmat) bone's matrix (read in earlier from the "joints" section).
                pos = vector_by_matrix(w.weights, b.bindmat)
                # b.bindpos = the bone's x,y,z position (read in earlier from the "joints" section).
                # w.bias = the weight's "weight percentage value".
                pos =((pos[0]+b.bindpos[0])*w.bias, (pos[1]+b.bindpos[1])*w.bias, (pos[2]+b.bindpos[2])*w.bias)
                #vertex position is sum of all weight info adjusted for bias
                mesh.verts[vert_counter].co[0]+=pos[0]
                mesh.verts[vert_counter].co[1]+=pos[1]
                mesh.verts[vert_counter].co[2]+=pos[2]
        Strings[2458] = Strings[2458].replace("md5 mesh " + str(mesh_count) + "\n", "")
        progressbar.close()

    # Used for QuArK progressbar.
    firstcomp = str(CompNbr)
    lastcomp = str(CompNbr + len(md5_model)-1)

    # basepath = The full path to the game folder, ex: "C:\Program Files\Doom 3\base\"
    mesh_count = 0
    progressbar = quarkx.progressbar(2454, len(md5_model))
    for mesh in md5_model: # A new QuArK component needs to be made for each mesh.
        mesh_count += 1
        if len(md5_model) > 1:
            Strings[2454] = "Processing Components " + firstcomp + " to " + lastcomp + "\n" + "Importing Component " + str(mesh_count) + "\n\n"
        else:
            Strings[2454] = "Importing Component " + str(mesh_count) + "\n"
        progressbar.progress()
        ### Creates this component's Skins:sg group.
        # Checks if the model has textures specified with it.
        skinsize = (256, 256)
        skingroup = quarkx.newobj('Skins:sg')
        skingroup['type'] = chr(2)
        noimage = "\r\nNo shader or image found.\r\n"
        foundshader = mesh_shader = shader_file = shader_name = None
        if(mesh.shader!=""): # Make the QuArK Skins here
            path = mesh.shader.split("\\")
            path = path[len(path)-1] # This is the full shader we are looking for, ex: "models/monsters/pinky/pinky_metal"
            shaderspath = basepath + "materials"
            try:
                shaderfiles = os.listdir(shaderspath)
                for shaderfile in shaderfiles:
                    noimage = ""
                    foundshader = foundtexture = foundimage = imagefile = None
                    mesh_shader = shader_file = shader_name = shader_keyword = qer_editorimage = diffusemap = map = bumpmap = addnormals = heightmap = specularmap = None
                    #read the file in
                    try: # To by pass sub-folders, should make this to check those also.
                        file=open(shaderspath+"/"+shaderfile,"r")
                    except:
                        continue
                    lines=file.readlines()
                    file.close()
                    left_cur_braket = 0
                    for line in range(len(lines)):
                        if foundshader is None and lines[line].startswith(mesh.shader+"\n"):
                            shaderline = lines[line].replace(chr(9), "    ")
                            shaderline = shaderline.rstrip()
                            mesh_shader = "\r\n" + shaderline + "\r\n"
                            shader_file = shaderspath + "/" + shaderfile
                            shader_name = mesh.shader
                            foundshader = mesh.shader
                            left_cur_braket = 0
                            continue
                        if foundshader is not None and lines[line].find("{") != -1:
                            left_cur_braket = left_cur_braket + 1
                        if foundshader is not None and lines[line].find("}") != -1:
                            left_cur_braket = left_cur_braket - 1
                        if foundshader is not None:
                            if lines[line].find("qer_editorimage") != -1 or lines[line].find("diffusemap") != -1:
                                words = lines[line].split()
                                for word in words:
                                    if word.endswith(".tga"):
                                        foundtexture = word
                                        if lines[line].find("qer_editorimage") != -1:
                                            shader_keyword = "qer_editorimage"
                                        else:
                                            shader_keyword = "diffusemap"
                                        skinname = foundtexture
                                        skin = quarkx.newobj(skinname)
                                        break
                                    elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")):
                                        foundtexture = word + ".tga"
                                        if lines[line].find("qer_editorimage") != -1:
                                            shader_keyword = "qer_editorimage"
                                        else:
                                            shader_keyword = "diffusemap"
                                        skinname = foundtexture
                                        skin = quarkx.newobj(skinname)
                                        break
                                if foundtexture is not None:
                                    if os.path.isfile(basepath + foundtexture):
                                        foundimage = basepath + foundtexture
                                        image = quarkx.openfileobj(foundimage)
                                        skin['Image1'] = image.dictspec['Image1']
                                        skin['Size'] = image.dictspec['Size']
                                        skin['shader_keyword'] = shader_keyword
                                        skingroup.appenditem(skin)
                                        if skinsize == (256, 256):
                                            skinsize = skin['Size']
                                        foundtexture = None
                                    else: # Keep looking in the shader files, the shader may be in another one.
                                        imagefile = basepath + foundtexture
                                        noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + mesh.shader + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "and the 'diffusemap' image to display.\r\n    " + foundtexture + "\r\n" + "But that image file does not exist.\r\n"
                            if lines[line].find("bumpmap") != -1 and (not lines[line].find("addnormals") != -1 and not lines[line].find("heightmap") != -1):
                                words = lines[line].replace("("," ")
                                words = words.replace(")"," ")
                                words = words.replace(","," ")
                                words = words.split()
                                for word in words:
                                    if word.endswith(".tga"):
                                        bumpmap = word
                                    elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")):
                                        bumpmap = word + ".tga"
                            if lines[line].find("addnormals") != -1 or lines[line].find("heightmap") != -1:
                                words = lines[line].replace("("," ")
                                words = words.replace(")"," ")
                                words = words.replace(","," ")
                                words = words.split()
                                for word in range(len(words)):
                                    if words[word].find("addnormals") != -1 and words[word+1].find("/") != -1 and (words[word+1].startswith("models") or words[word+1].startswith("textures")):
                                        addnormals = words[word+1]
                                        if not addnormals.endswith(".tga"):
                                            addnormals = addnormals + ".tga"
                                    if words[word].find("heightmap") != -1 and words[word+1].find("/") != -1 and (words[word+1].startswith("models") or words[word+1].startswith("textures")):
                                        heightmap = words[word+1]
                                        if not heightmap.endswith(".tga"):
                                            heightmap = heightmap + ".tga"
                            elif lines[line].find("specularmap") != -1:
                                words = lines[line].split()
                                for word in words:
                                    if word.endswith(".tga"):
                                        specularmap = word
                                    elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")):
                                        specularmap = word + ".tga"
                            # Dec character code for space = chr(32), for tab = chr(9)
                            elif lines[line].find(chr(32)+"map") != -1 or lines[line].find(chr(9)+"map") != -1:
                                words = lines[line].split()
                                for word in words:
                                    if word.endswith(".tga") and (word.startswith("models") or word.startswith("textures")) and ((not word.endswith("_dis.tga") and not word.endswith("_dis")) and (not word.endswith("dis2.tga") and not word.endswith("dis2"))):
                                        map = word
                                    elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")) and ((not word.endswith("_dis.tga") and not word.endswith("_dis")) and (not word.endswith("dis2.tga") and not word.endswith("dis2"))):
                                        map = word + ".tga"
                                if map is not None and not map in skingroup.dictitems.keys():
                                    imagefile = basepath + map
                                    if os.path.isfile(basepath + map):
                                        skinname = map
                                        foundimage = basepath + skinname
                                        shader_keyword = "map"
                                        # Make the skin and add it.
                                        skin = quarkx.newobj(skinname)
                                        image = quarkx.openfileobj(foundimage)
                                        skin['Image1'] = image.dictspec['Image1']
                                        skin['Size'] = image.dictspec['Size']
                                        skin['shader_keyword'] = shader_keyword
                                        skingroup.appenditem(skin)
                                        if skinsize == (256, 256):
                                            skinsize = skin['Size']
                                    else:
                                        noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + mesh.shader + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                            else:
                                if lines[line].find("/") != -1:
                                    if lines[line-1].find("qer_editorimage") != -1 or lines[line-1].find("diffusemap") != -1 or lines[line-1].find("bumpmap") != -1 or lines[line-1].find("addnormals") != -1 or lines[line-1].find("heightmap") != -1 or lines[line-1].find("specularmap") != -1 or lines[line].find(chr(32)+"map") != -1 or lines[line].find(chr(9)+"map") != -1:
                                        words = lines[line].replace("("," ")
                                        words = words.replace(")"," ")
                                        words = words.replace(","," ")
                                        words = words.split()
                                        image = None
                                        for word in words:
                                            if word.endswith(".tga") and (word.startswith("models") or word.startswith("textures")) and ((not word.endswith("_dis.tga") and not word.endswith("_dis")) and (not word.endswith("dis2.tga") and not word.endswith("dis2"))):
                                                image = word
                                            elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")) and ((not word.endswith("_dis.tga") and not word.endswith("_dis")) and (not word.endswith("dis2.tga") and not word.endswith("dis2"))):
                                                image = word + ".tga"
                                        if (image is not None) and (not image in skingroup.dictitems.keys()):
                                            words = lines[line-1].replace("("," ")
                                            words = words.replace(")"," ")
                                            words = words.replace(","," ")
                                            words = words.split()
                                            keys = [qer_editorimage, diffusemap, bumpmap, addnormals, heightmap, specularmap, map]
                                            words.reverse() # Work our way backwards to get the last key name first.
                                            for word in range(len(words)):
                                                if words[word] in keys:
                                                    imagefile = basepath + image
                                                    if os.path.isfile(basepath + image):
                                                        skinname = image
                                                        foundimage = basepath + skinname
                                                        shader_keyword = words[word]
                                                        # Make the skin and add it.
                                                        skin = quarkx.newobj(skinname)
                                                        image = quarkx.openfileobj(foundimage)
                                                        skin['Image1'] = image.dictspec['Image1']
                                                        skin['Size'] = image.dictspec['Size']
                                                        skin['shader_keyword'] = shader_keyword
                                                        skingroup.appenditem(skin)
                                                        if skinsize == (256, 256):
                                                            skinsize = skin['Size']
                                                    else:
                                                        noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + mesh.shader + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                            shaderline = lines[line].replace(chr(9), "    ")
                            shaderline = shaderline.rstrip()
                            if mesh_shader is not None:
                                mesh_shader = mesh_shader + shaderline + "\r\n"
                            if lines[line].find("}") != -1 and left_cur_braket == 0: # Done reading shader so break out of reading this file.
                                break
                    if mesh_shader is not None:
                        if bumpmap is not None:
                            imagefile = basepath + bumpmap
                            if os.path.isfile(basepath + bumpmap):
                                skinname = bumpmap
                                foundimage = basepath + skinname
                                shader_keyword = "bumpmap"
                                # Make the skin and add it.
                                skin = quarkx.newobj(skinname)
                                image = quarkx.openfileobj(foundimage)
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                skin['shader_keyword'] = shader_keyword
                                skingroup.appenditem(skin)
                                if skinsize == (256, 256):
                                    skinsize = skin['Size']
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + mesh.shader + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                        if addnormals is not None:
                            imagefile = basepath + addnormals
                            if os.path.isfile(basepath + addnormals):
                                skinname = addnormals
                                foundimage = basepath + skinname
                                shader_keyword = "addnormals"
                                # Make the skin and add it.
                                skin = quarkx.newobj(skinname)
                                image = quarkx.openfileobj(foundimage)
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                skin['shader_keyword'] = shader_keyword
                                skingroup.appenditem(skin)
                                if skinsize == (256, 256):
                                    skinsize = skin['Size']
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + mesh.shader + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                        if heightmap is not None:
                            imagefile = basepath + heightmap
                            if os.path.isfile(basepath + heightmap):
                                skinname = heightmap
                                foundimage = basepath + skinname
                                shader_keyword = "heightmap"
                                # Make the skin and add it.
                                skin = quarkx.newobj(skinname)
                                image = quarkx.openfileobj(foundimage)
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                skin['shader_keyword'] = shader_keyword
                                skingroup.appenditem(skin)
                                if skinsize == (256, 256):
                                    skinsize = skin['Size']
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + mesh.shader + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                        if specularmap is not None:
                            imagefile = basepath + specularmap
                            if os.path.isfile(basepath + specularmap):
                                skinname = specularmap
                                foundimage = basepath + skinname
                                shader_keyword = "specularmap"
                                # Make the skin and add it.
                                skin = quarkx.newobj(skinname)
                                image = quarkx.openfileobj(foundimage)
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                skin['shader_keyword'] = shader_keyword
                                skingroup.appenditem(skin)
                                if skinsize == (256, 256):
                                    skinsize = skin['Size']
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + mesh.shader + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                        if imagefile is None:
                            imagefile = "NO IMAGE FILE FOUND AT ALL, CHECK THE SHADER."
                        break
                    if foundshader is not None: # Found the shader so break out of the shader files loop.
                        break
            except:
                noimage = noimage + "\r\nThe needed file folder\r\n    " + shaderspath + "\r\ncould not be located.\r\nCorrect and retry importing the model.\r\n"

            message = message + noimage

            if mesh.shader is not None and foundshader is None: # This component has an image but no shader was found, so...
                texturepath = basepath + "/" + mesh.shader + ".tga"
                if os.path.isfile(texturepath): # May not be a shader so we look for a texture with the same image name.
                    skinname = mesh.shader + ".tga"
                    skin = quarkx.newobj(skinname)
                    foundimage = basepath + skinname
                    image = quarkx.openfileobj(foundimage)
                    skin['Image1'] = image.dictspec['Image1']
                    skin['Size'] = image.dictspec['Size']
                    skingroup.appenditem(skin)
                    if skinsize == (256, 256):
                        skinsize = skin['Size']
                else: # If no texture is found then we are missing the shader.
                    message = message + "\r\nImport Component " + str(CompNbr) + " calls for the shader:\r\n    " + mesh.shader + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder\r\nor create a shader file if needed.\r\n    texturepath = " + mesh.shader + "\r\n"

        # QuArK Frames group, frames and frame vertices section.
        framesgroup = quarkx.newobj('Frames:fg') # QuArK Frames group made here.
        frame = quarkx.newobj('baseframe:mf') # QuArK frame made here.
        comp_mesh = ()
        comp_verts = []
        for vert in mesh.verts: # QuArK frame Vertices made here.
                comp_mesh = comp_mesh + (vert.co[0], vert.co[1], vert.co[2])
                #add the uv coords to the vertex
                # As a percentage of the QuArK Skinview1.clientarea for X and Y.
                U = int(skinsize[0] * vert.uvco[0])
                V = int(skinsize[1] * vert.uvco[1])
                V = -V + skinsize[1]
                v = (U, V)
                #add the vertex to the mesh
                comp_verts = comp_verts + [v]
        frame['Vertices'] = comp_mesh
        framesgroup.appenditem(frame)
        # QuArK Tris made here.
        Tris = ''
        for tri in mesh.tris:
                Tris = Tris + struct.pack("Hhh", tri.vert_index[0],comp_verts[tri.vert_index[0]][0],comp_verts[tri.vert_index[0]][1])
                Tris = Tris + struct.pack("Hhh", tri.vert_index[1],comp_verts[tri.vert_index[1]][0],comp_verts[tri.vert_index[1]][1])
                Tris = Tris + struct.pack("Hhh", tri.vert_index[2],comp_verts[tri.vert_index[2]][0],comp_verts[tri.vert_index[2]][1])

        # Now we start creating our Import Component and name it.
        if mesh.shader != "":
            Comp_name = mesh.shader.split("/")
            Comp_name = Comp_name[len(Comp_name)-1]
            Component = quarkx.newobj(filename + "_" + Comp_name + ':mc')
        elif shader_name is not None:
            Comp_name = shader_name.split("/")
            Comp_name = Comp_name[len(Comp_name)-1]
            Component = quarkx.newobj(filename + "_" + Comp_name + ':mc')
        else:
            Component = quarkx.newobj(filename + "_" + "Import Component " + str(CompNbr) + ':mc')
            CompNbr = CompNbr + 1
        md5_model_comps = md5_model_comps + [Component.name]
        if mesh.mesh_index == 0:
            for bone in QuArK_bones:
                bone['component'] = Component.name
                # This next line preserves origianl handle scale setting for each bone.
                bone['org_scale'] = bone.dictspec['scale']
        if shader_file is not None: # The path and name of the shader file.
            Component['shader_file'] = shader_file
        if shader_name is not None: # The name of the shader in the shader file.
            Component['shader_name'] = shader_name
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
    if len(md5_model) > 1:
        Strings[2454] = Strings[2454].replace("Processing Components " + firstcomp + " to " + lastcomp + "\n" + "Importing Component " + str(mesh_count) + "\n\n", "")
    else:
        Strings[2454] = Strings[2454].replace("Importing Component " + str(mesh_count) + "\n", "")
    progressbar.close()

    # Section below gives all the bones their bone.vtxlist and bone.vtx_pos is set to an empty dictionary to keep from pulling the bone off of its set position.
    for bone_index in range(len(QuArK_bones)):
        if bone_vtx_list.has_key(bone_index):
            temp_vtxlist = {}
            for mesh_index in bone_vtx_list[bone_index].keys():
                compkey = ComponentList[mesh_index].name
                temp_vtxlist[compkey] = bone_vtx_list[bone_index][mesh_index]
            QuArK_bones[bone_index].vtxlist = temp_vtxlist
            vtxcount = 0
            usekey = None
            for key in QuArK_bones[bone_index].vtxlist.keys():
                if len(QuArK_bones[bone_index].vtxlist[key]) > vtxcount:
                    usekey = key
                    vtxcount = len(QuArK_bones[bone_index].vtxlist[key])
            if usekey is not None:
                temp = {}
                temp[usekey] = QuArK_bones[bone_index].vtxlist[usekey]
                QuArK_bones[bone_index].vtx_pos = temp
                QuArK_bones[bone_index]['component'] = usekey

    # Section below fills the editor.ModelComponentList 'bonelist' for all importing bones and fills the 'baseframe' data.
    for bone_index in range(len(QuArK_bones)):
        current_bone = QuArK_bones[bone_index]
        if not editor.ModelComponentList['bonelist'].has_key(current_bone.name):
            editor.ModelComponentList['bonelist'][current_bone.name] = {}
        editor.ModelComponentList['bonelist'][current_bone.name]['frames'] = {}
        bone_data = {}
        bone_data['position'] = current_bone.position.tuple
        bone_data['rotmatrix'] = current_bone.rotmatrix.tuple
        editor.ModelComponentList['bonelist'][current_bone.name]['frames']['baseframe:mf'] = bone_data

    # Section below sets up the QuArK editor.ModelComponentList for each mesh.
    for mesh_index in ModelComponentList.keys():
        compname = ComponentList[mesh_index].name
        if not editor.ModelComponentList.has_key(compname):
            editor.ModelComponentList[compname] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
        for bone_index in ModelComponentList[mesh_index].keys():
            bonename = QuArK_bones[bone_index].name
            if not editor.ModelComponentList[compname]['bonevtxlist'].has_key(bonename):
                editor.ModelComponentList[compname]['bonevtxlist'][bonename] = {}
            for vtx_index in ModelComponentList[mesh_index][bone_index].keys():
                editor.ModelComponentList[compname]['bonevtxlist'][bonename][vtx_index] = ModelComponentList[mesh_index][bone_index][vtx_index]
                editor.ModelComponentList[compname]['bonevtxlist'][bonename][vtx_index]['color'] = QuArK_bones[bone_index].dictspec['_color']
        if QuArK_weights_list.has_key(mesh_index) and len(QuArK_weights_list[mesh_index].keys()) != 0:
            for vertex in QuArK_weights_list[mesh_index].keys():
                if not editor.ModelComponentList[compname]['weightvtxlist'].has_key(vertex):
                    editor.ModelComponentList[compname]['weightvtxlist'][vertex] = QuArK_weights_list[mesh_index][vertex]

    return ComponentList, QuArK_bones, message # Gives a list of ALL bone as they are created, same as in the .md5mesh file.


######################################################
# IMPORT ANIMATION ONLY STARTS HERE
######################################################

class md5anim_bone:
    name = ""
    parent_index = 0
    flags = 0
    frameDataIndex = 0
    bindpos = []
    bindquat = []
    
    def __init__(self):
        name = ""
        self.bindpos=[0.0]*3
        self.bindquat=[0.0]*4
        self.parent_index = 0
        self.flags = 0
        self.frameDataIndex = 0


######################################################
# IMPORTS ANIMATION FRAMES SECTION
######################################################
class md5anim:
    num_bones = 0
    md5anim_bones = []
    frameRate = 24
    numFrames = 0
    numAnimatedComponents = 0
    baseframe = []
    framedata = []

    def __init__(self):
        num_bones = 0
        md5anim_bones = []
        baseframe = []
        framedata = []
        
    def load_md5anim(self, md5_filename, bones, actionname): # bones = A list of all the  bones in the QuArK's "Skeleton:bg" folder, in their proper tree-view order, to get our current bones from.
        file=open(md5_filename,"r")
        lines=file.readlines()
        file.close()

        num_lines=len(lines)

        for line_counter in range(0,num_lines):
            current_line=lines[line_counter]
            words=current_line.split()

            if words and words[0]=="numJoints":
                self.num_bones=int(words[1])

            elif words and words[0]=="numFrames":
                self.numFrames=int(words[1])
                self.framedata = [[]]*self.numFrames

            elif words and words[0]=="frameRate":
                self.frameRate=int(words[1])

            elif words and words[0]=="numAnimatedComponents":
                self.numAnimatedComponents=int(words[1])

            elif words and words[0]=="hierarchy":
                for bone_counter in range(0,self.num_bones):
                    #make a new bone
                    self.md5anim_bones.append(md5anim_bone())
                    #next line
                    line_counter+=1
                    current_line=lines[line_counter]
                    words=current_line.split()
                    #skip over blank lines
                    while not words:
                        line_counter+=1
                        current_line=lines[line_counter]
                        words=current_line.split()

                    #get rid of the quotes on either side
                    temp_name=str(words[0])
                    temp_name=temp_name[1:-1]
                    self.md5anim_bones[bone_counter].name=temp_name
                    self.md5anim_bones[bone_counter].parent_index = int(words[1])
                    flags = self.md5anim_bones[bone_counter].flags = int(words[2])
                    if flags >= 32:
                        flag = bones[bone_counter].dictspec['flags'][:5] + (32,)
                        bones[bone_counter]['flags'] = flag
                        flags = flags - 32
                    if flags >= 16:
                        flag = bones[bone_counter].dictspec['flags'][:4] + (16,) + bones[bone_counter].dictspec['flags'][5:]
                        bones[bone_counter]['flags'] = flag
                        flags = flags - 16
                    if flags >= 8:
                        flag = bones[bone_counter].dictspec['flags'][:3] + (8,) + bones[bone_counter].dictspec['flags'][4:]
                        bones[bone_counter]['flags'] = flag
                        flags = flags - 8
                    if flags >= 4:
                        flag = bones[bone_counter].dictspec['flags'][:2] + (4,) + bones[bone_counter].dictspec['flags'][3:]
                        bones[bone_counter]['flags'] = flag
                        flags = flags - 4
                    if flags >= 2:
                        flag = bones[bone_counter].dictspec['flags'][:1] + (2,) + bones[bone_counter].dictspec['flags'][2:]
                        bones[bone_counter]['flags'] = flag
                        flags = flags - 2
                    if flags >= 1:
                        flag = (1,) + bones[bone_counter].dictspec['flags'][1:]
                        bones[bone_counter]['flags'] = flag

                    self.md5anim_bones[bone_counter].frameDataIndex=int(words[3])

            elif words and words[0]=="baseframe":
                filename = actionname.replace(".md5anim", "")
                for bone_counter in range(0,self.num_bones):
                    line_counter+=1
                    current_line=lines[line_counter]
                    words=current_line.split()
                    #skip over blank lines
                    while not words:
                        line_counter+=1
                        current_line=lines[line_counter]
                        words=current_line.split()
                    self.md5anim_bones[bone_counter].bindpos[0] = float(words[1])
                    self.md5anim_bones[bone_counter].bindpos[1] = float(words[2])
                    self.md5anim_bones[bone_counter].bindpos[2] = float(words[3])
                    qx = float(words[6])
                    qy = float(words[7])
                    qz = float(words[8])
                    bones[bone_counter][filename] = self.md5anim_bones[bone_counter].bindpos[0], self.md5anim_bones[bone_counter].bindpos[1], self.md5anim_bones[bone_counter].bindpos[2], qx,qy,qz
                    qw = 1 - qx*qx - qy*qy - qz*qz
                    if qw<0:
                        qw=0
                    else:
                        qw = -sqrt(qw)
                    self.md5anim_bones[bone_counter].bindquat = [qx,qy,qz,qw]

            elif words and words[0]=="frame":
                framenumber = int(words[1])
                self.framedata[framenumber]=[]
                line_counter+=1
                current_line=lines[line_counter]
                words=current_line.split()
                while words and not(words[0]=="frame" or words[0]=="}"):
                    for i in range(0, len(words)):
                        self.framedata[framenumber].append(float(words[i]))
                    line_counter+=1
                    current_line=lines[line_counter]
                    words=current_line.split()

    def apply(self, bones, actionname):
        #A list of bones.name -> bone_index, to speed things up
        ConvertBoneNameToIndex = {}
        for bone_index in range(len(bones)):
            ConvertBoneNameToIndex[bones[bone_index].name] = bone_index

        global editor
        filename = actionname.replace(".md5anim", "")
        Strings[2462] = Strings[2462] + "\n" + filename
        progressbar = quarkx.progressbar(2462, self.numFrames * len(md5_model_comps))
        undo = quarkx.action()

        #Construct baseframe data
        QuArK_baseframe_position_raw = [[]]*self.num_bones
        QuArK_baseframe_matrix_raw = [[]]*self.num_bones
        for bone_counter in range(0,self.num_bones):
            QuArK_baseframe_position_raw[bone_counter] = quarkx.vect(self.md5anim_bones[bone_counter].bindpos[0], self.md5anim_bones[bone_counter].bindpos[1], self.md5anim_bones[bone_counter].bindpos[2])
            tempmatrix = quaternion2matrix(self.md5anim_bones[bone_counter].bindquat)
            QuArK_baseframe_matrix_raw[bone_counter] = quarkx.matrix((tempmatrix[0][0], tempmatrix[1][0], tempmatrix[2][0]), (tempmatrix[0][1], tempmatrix[1][1], tempmatrix[2][1]), (tempmatrix[0][2], tempmatrix[1][2], tempmatrix[2][2]))

        #Construct animation frame data
        QuArK_frame_position_raw = [[]]*self.numFrames
        QuArK_frame_matrix_raw = [[]]*self.numFrames
        for frame_counter in range(0,self.numFrames):
            QuArK_frame_position_raw[frame_counter] = [[]]*self.num_bones
            QuArK_frame_matrix_raw[frame_counter] = [[]]*self.num_bones
            for bone_counter in range(0,self.num_bones):
                currentbone = self.md5anim_bones[bone_counter]
                lx, ly, lz = currentbone.bindpos # These are originally set when the "baseframe" is read in and creates the bones.
                (qx, qy, qz, qw) = currentbone.bindquat # These are originally set when the "baseframe" is read in and creates the bones.
                frameDataIndex = currentbone.frameDataIndex # These are originally set when the "baseframe" is read in and creates the bones.
                if (currentbone.flags & 1):
                    lx = self.framedata[frame_counter][frameDataIndex]
                    frameDataIndex+=1
                if (currentbone.flags & 2):
                    ly = self.framedata[frame_counter][frameDataIndex]
                    frameDataIndex+=1
                if (currentbone.flags & 4):
                    lz = self.framedata[frame_counter][frameDataIndex]
                    frameDataIndex+=1
                if (currentbone.flags & 8):
                    qx = self.framedata[frame_counter][frameDataIndex]
                    frameDataIndex+=1
                if (currentbone.flags & 16):
                    qy = self.framedata[frame_counter][frameDataIndex]
                    frameDataIndex+=1
                if (currentbone.flags & 32):
                    qz = self.framedata[frame_counter][frameDataIndex]
                qw = 1 - qx*qx - qy*qy - qz*qz
                if qw<0:
                    qw=0
                else:
                    qw = -sqrt(qw)
                QuArK_frame_position_raw[frame_counter][bone_counter] = quarkx.vect(lx, ly, lz)
                tempmatrix = quaternion2matrix([qx, qy, qz, qw])
                QuArK_frame_matrix_raw[frame_counter][bone_counter] = quarkx.matrix((tempmatrix[0][0], tempmatrix[1][0], tempmatrix[2][0]), (tempmatrix[0][1], tempmatrix[1][1], tempmatrix[2][1]), (tempmatrix[0][2], tempmatrix[1][2], tempmatrix[2][2]))

        #Prepare baseframe data
        QuArK_baseframe_position = [[]]*self.num_bones
        QuArK_baseframe_matrix = [[]]*self.num_bones
        for bone_counter in range(0,self.num_bones):
            currentbone = self.md5anim_bones[bone_counter]
            if currentbone.parent_index < 0:
                QuArK_baseframe_position[bone_counter] = QuArK_baseframe_position_raw[bone_counter]
                QuArK_baseframe_matrix[bone_counter] = QuArK_baseframe_matrix_raw[bone_counter]
            else:
                ParentMatrix = QuArK_baseframe_matrix[currentbone.parent_index]
                temppos = ParentMatrix * QuArK_baseframe_position_raw[bone_counter]
                QuArK_baseframe_position[bone_counter] = QuArK_baseframe_position[currentbone.parent_index] + temppos
                QuArK_baseframe_matrix[bone_counter] = ParentMatrix * QuArK_baseframe_matrix_raw[bone_counter]

        #Prepare animation frame data
        QuArK_frame_position = [[]]*self.numFrames
        QuArK_frame_matrix = [[]]*self.numFrames
        for frame_counter in range(0,self.numFrames):
            QuArK_frame_position[frame_counter] = [[]]*self.num_bones
            QuArK_frame_matrix[frame_counter] = [[]]*self.num_bones
            for bone_counter in range(0,self.num_bones):
                currentbone = self.md5anim_bones[bone_counter]
                if currentbone.parent_index < 0:
                    QuArK_frame_position[frame_counter][bone_counter] = QuArK_frame_position_raw[frame_counter][bone_counter]
                    QuArK_frame_matrix[frame_counter][bone_counter] = QuArK_frame_matrix_raw[frame_counter][bone_counter]
                else:
                    ParentMatrix = QuArK_frame_matrix[frame_counter][currentbone.parent_index]
                    temppos = ParentMatrix * QuArK_frame_position_raw[frame_counter][bone_counter]
                    QuArK_frame_position[frame_counter][bone_counter] = QuArK_frame_position[frame_counter][currentbone.parent_index] + temppos
                    QuArK_frame_matrix[frame_counter][bone_counter] = ParentMatrix * QuArK_frame_matrix_raw[frame_counter][bone_counter]

        # Create baseframe
        baseframes_list = []
        most_vtxs = 0
        for mesh_counter in range(len(md5_model_comps)):
            oldframe = editor.Root.dictitems[md5_model_comps[mesh_counter]].dictitems['Frames:fg'].dictitems['baseframe:mf']
            comp_name = oldframe.parent.parent.name
            baseframe = oldframe.copy()
            baseframe.shortname = filename + " baseframe"
            baseframes_list = baseframes_list + [baseframe]
            newverts = baseframe.vertices
            for vert_counter in range(len(newverts)):
                if editor.ModelComponentList[comp_name]['weightvtxlist'].has_key(vert_counter):
                    oldpos = newverts[vert_counter] #This is the old position
                    newpos = quarkx.vect(0.0, 0.0, 0.0)
                    for key in editor.ModelComponentList[comp_name]['weightvtxlist'][vert_counter].keys():
                        bone_index = ConvertBoneNameToIndex[key]
                        if bone_index == -1:
                            continue
                        our_bone_name = bones[bone_index].name
                        our_weight_value = editor.ModelComponentList[comp_name]['weightvtxlist'][vert_counter][our_bone_name]['weight_value']
                        our_bone_data = editor.ModelComponentList['bonelist'][our_bone_name]['frames']['baseframe:mf']
                        our_bone_pos = quarkx.vect(our_bone_data['position'])
                        our_bone_rot = quarkx.matrix(our_bone_data['rotmatrix'])
                        our_weight_pos = (~our_bone_rot) * (oldpos - our_bone_pos)
                        temppos = QuArK_baseframe_matrix[bone_index] * our_weight_pos
                        newpos = newpos + ((QuArK_baseframe_position[bone_index] + temppos) * our_weight_value)
                    newverts[vert_counter] = newpos
            baseframe.vertices = newverts
            FramesGroup = oldframe.parent
            undo.put(FramesGroup, baseframe)

        for bone_counter in range(0,self.num_bones):
            for current_bone in bones:
                bone_name = current_bone.shortname
                bone_name = bone_name.split("_", 1)[1]
                if bone_name == self.md5anim_bones[bone_counter].name:
                    break
            if not editor.ModelComponentList['bonelist'].has_key(current_bone.name):
                raise "editor.ModelComponentList corrupt!"
            if not editor.ModelComponentList['bonelist'][current_bone.name].has_key('frames'):
                raise "editor.ModelComponentList corrupt!"
            framename = filename + " baseframe"
            bone_data = {}
            bone_data['position'] = QuArK_baseframe_position[bone_counter].tuple
            bone_data['rotmatrix'] = QuArK_baseframe_matrix[bone_counter].tuple
            editor.ModelComponentList['bonelist'][current_bone.name]['frames'][framename + ':mf'] = bone_data

        #Create animation frames
        for frame_counter in range(0,self.numFrames):
            most_vtxs = 0
            for mesh_counter in range(len(md5_model_comps)):
                progressbar.progress()
                baseframe = editor.Root.dictitems[md5_model_comps[mesh_counter]].dictitems['Frames:fg'].dictitems['baseframe:mf']
                newframe = baseframes_list[mesh_counter].copy()
                comp_name = baseframes_list[mesh_counter].parent.parent.name
                newframe.shortname = filename + " frame "+str(frame_counter+1)
                meshverts = baseframe.vertices
                newverts = newframe.vertices
                for vert_counter in range(len(newverts)):
                    if editor.ModelComponentList[comp_name]['weightvtxlist'].has_key(vert_counter):
                        oldpos = meshverts[vert_counter] #This is the old position
                        newpos = quarkx.vect(0.0, 0.0, 0.0)
                        for key in editor.ModelComponentList[comp_name]['weightvtxlist'][vert_counter].keys():
                            bone_index = ConvertBoneNameToIndex[key]
                            if bone_index == -1:
                                continue
                            our_bone_name = bones[bone_index].name
                            our_weight_value = editor.ModelComponentList[comp_name]['weightvtxlist'][vert_counter][our_bone_name]['weight_value']
                            our_bone_data = editor.ModelComponentList['bonelist'][our_bone_name]['frames']['baseframe:mf']
                            our_bone_pos = quarkx.vect(our_bone_data['position'])
                            our_bone_rot = quarkx.matrix(our_bone_data['rotmatrix'])
                            our_weight_pos = (~our_bone_rot) * (oldpos - our_bone_pos)
                            temppos = QuArK_frame_matrix[frame_counter][bone_index] * our_weight_pos
                            newpos = newpos + ((QuArK_frame_position[frame_counter][bone_index] + temppos) * our_weight_value)
                        newverts[vert_counter] = newpos
                newframe.vertices = newverts
                FramesGroup = baseframes_list[mesh_counter].parent
                undo.put(FramesGroup, newframe)

        # Section below fills the 'bonelist' entry of editor.ModelComponentList for all the importing 'baseframe' and animation frames.
        for bone_counter in range(0,self.num_bones):
            for current_bone in bones:
                bone_name = current_bone.shortname
                bone_name = bone_name.split("_", 1)[1]
                if bone_name == self.md5anim_bones[bone_counter].name:
                    break
            if not editor.ModelComponentList['bonelist'].has_key(current_bone.name):
                raise "editor.ModelComponentList corrupt!"
            if not editor.ModelComponentList['bonelist'][current_bone.name].has_key('frames'):
                raise "editor.ModelComponentList corrupt!"
            for frame_counter in range(0,self.numFrames):
                framename = filename + " frame "+str(frame_counter+1)
                bone_data = {}
                bone_data['position'] = QuArK_frame_position[frame_counter][bone_counter].tuple
                bone_data['rotmatrix'] = QuArK_frame_matrix[frame_counter][bone_counter].tuple
                editor.ModelComponentList['bonelist'][current_bone.name]['frames'][framename + ':mf'] = bone_data

        editor.ok(undo, "ANIM " + filename + " loaded")
        Strings[2462] = Strings[2462].replace("\n" + filename, "")
        progressbar.close()


######################################################
# END OF IMPORT ANIMATION ONLY SECTION
######################################################


######################################################
# CALL TO IMPORT ANIMATION (.md5anim) FILE (called from dialog section below)
######################################################
# md5anim_filename = QuArK's full path and file name.
# bones = A list of all the  bones in the QuArK's "Skeleton:bg" folder, in their proper tree-view order, to get our current bones from.
def load_md5anim(md5anim_filename, bones, actionname):
    theanim = md5anim() # Making an "instance" of this class.
    theanim.load_md5anim(md5anim_filename, bones, actionname) # Calling this class function to open and completely read the .md5_anim file.
    theanim.apply(bones, actionname) # Calling this class function to create the amimation frames,
                                     # "bones" (see above), "actionname" is the full ,md5anim file name only.

    return


######################################################
# CALLS TO IMPORT MESH (.md5mesh) and ANIMATION (.md5anim) FILE
######################################################
def import_md5_model(basepath, md5_filename):
    global md5_model_comps

    # basepath just the path to the "game" folder.
    # md5_filename is the full path and file name.
    editor = quarkpy.mdleditor.mdleditor
    pth, actionname = os.path.split(md5_filename)
    if md5_filename.endswith(".md5mesh"): # Calls to load the .md5_mesh file.
        RetComponentList, RetQuArK_bone_list, message = load_md5(md5_filename, basepath, actionname) # Loads the model using list of ALL bones as they are created.

        return RetComponentList, RetQuArK_bone_list, message # Using list of ALL bones as they are created.
    else: # Calls to load the .md5_anim file.
        skeletongroup = editor.Root.dictitems['Skeleton:bg']  # get the bones group
        bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
        mesh_bones = []
        filename = md5_mesh_path[len(md5_mesh_path)-1]
        filename = filename + "_"
        for bone in bones:
            if bone.name.startswith(filename):
                mesh_bones = mesh_bones + [bone]

        if len(mesh_bones) == 0:
            quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
            quarkx.msgbox("Could not apply animation.\nNo bones for the mesh file exist.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        md5_model_comps = []
        for item in editor.Root.subitems:
            if item.type == ":mc" and item.name.startswith(filename):
                md5_model_comps = md5_model_comps + [item.name]
        if len(md5_model_comps) == 0:
            quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
            quarkx.msgbox("No components exist for this animation.\n\nAnimation import aborted.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        load_md5anim(md5_filename, mesh_bones, actionname)

def loadmodel(root, filename, gamename, nomessage=0):
    #   Loads the model file: root is the actual file,
    #   filename is the full path and name of the .md5mesh or .md5anim file selected,
    #   for example:  C:\Program Files\Doom 3\base\models\md5\monsters\pinky\pinky.md5mesh
    #   gamename is None.

    global md5_mesh_path, md5_anim_path, editor, tobj, logging, importername, textlog, Strings
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
    # basepath = the full path up to and including the game folder with ending forward slash, ex:
    # D:/Program Files/Doom 3/base/
    basepath = basepath.replace("\\", "/")
    if basepath is None:
        editor = None   #Reset the global again
        return

    if filename.endswith(".md5mesh"): # Calls to load the .md5_mesh file.
        logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

    ### Lines below here loads the model into the opened editor's current model.
        RetComponentList, RetQuArK_bone_list, message = import_md5_model(basepath, filename)

        if RetComponentList is None or RetComponentList == []:
            quarkx.beep() # Makes the computer "Beep" once if a file is not valid.
            quarkx.msgbox("Invalid .md5 model.\n\n    " + filename + "\n\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            try:
                progressbar.close()
            except:
                pass
            editor = None   #Reset the global again
            return

        newbones = []
        for bone in range(len(RetQuArK_bone_list)): # Using list of ALL bones.
            boneobj = RetQuArK_bone_list[bone]
            parent_index = int(boneobj.dictspec['parent_index'])
            if parent_index < 0:
                newbones = newbones + [boneobj]
            else:
                RetQuArK_bone_list[parent_index].appenditem(boneobj)

        if editor.form is None: # Step 2 to import model from QuArK's Explorer.
            md2fileobj = quarkx.newfileobj("New model.md2")
            md2fileobj['FileName'] = 'New model.qkl'
            for bone in newbones:
                editor.Root.dictitems['Skeleton:bg'].appenditem(bone)
            for Component in RetComponentList:
                editor.Root.appenditem(Component)
            md2fileobj['Root'] = editor.Root.name
            md2fileobj.appenditem(editor.Root)
            md2fileobj.openinnewwindow()
        else: # Imports a model properly from within the editor.
            QuArK_mesh_counter = 0
            undo = quarkx.action()
            for bone in newbones:
                undo.put(editor.Root.dictitems['Skeleton:bg'], bone)
            for Component in RetComponentList:
                undo.put(editor.Root, Component)
                editor.Root.currentcomponent = Component
                compframes = editor.Root.currentcomponent.findallsubitems("", ':mf')   # get all frames
                for compframe in compframes:
                    compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.

                QuArK_mesh_counter = QuArK_mesh_counter + 1

                try:
                    progressbar.close()
                    ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.
                except:
                    pass

                # This needs to be done for each component or bones will not work if used in the editor.
                quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
            editor.ok(undo, str(len(RetComponentList)) + " .md5 Components imported") # Let the ok finish the new components before going on.

            editor.Root.currentcomponent = RetComponentList[0]  # Sets the current component.
            comp = editor.Root.currentcomponent
            skins = comp.findallsubitems("", ':sg')      # Gets the skin group.
            if len(skins[0].subitems) != 0:
                comp.currentskin = skins[0].subitems[0]      # To try and set to the correct skin.
                quarkpy.mdlutils.Update_Skin_View(editor, 2) # Sends the Skin-view for updating and center the texture in the view.
            else:
                comp.currentskin = None

            editor = None   #Reset the global again
            if message != "":
                message = message + "================================\r\n\r\n"
                message = message + "You need to find and supply the proper texture(s) and folder(s) above.\r\n"
                message = message + "Extract the required folder(s) and file(s) to the 'game' folder.\r\n\r\n"
                message = message + "If a texture does not exist it may be a .dds or some other type of image file.\r\n"
                message = message + "If so then you need to make a .tga file copy of that texture, perhaps in PaintShop Pro.\r\n\r\n"
                message = message + "You may also need to rename it to match the exact name above.\r\n"
                message = message + "Either case, it would be for editing purposes only and should be placed in the proper folder.\r\n\r\n"
                message = message + "Once this is done, then delete the imported components and re-import the model."
                quarkx.textbox("WARNING", "Missing Skin Textures:\r\n\r\n================================\r\n" + message, quarkpy.qutils.MT_WARNING)

            md5_mesh_path = filename.rsplit('\\', 1)

    else: # Calls to load the .md5_anim file.
        # md5_anim_path = two items in a list, the full path to the model folder, and the animation file name, ex:
        # md5_anim_path = ['D:\\Program Files\\Doom 3\\base\\models\\md5\\monsters\\lostsoul', 'pain1.md5anim']
        md5_anim_path = filename.rsplit('\\', 1)
        model_folder = md5_anim_path[0].rsplit('\\', 1)[1]
        md5_mesh_path = None
        for item in editor.Root.subitems:
            if item.type == ":mc":
                test4mesh = item.name.split('_', 1)[0]
                if os.path.isfile(test4mesh + ".md5mesh"):
                    md5_mesh_path = [md5_anim_path[0], test4mesh]
                    break
        if md5_mesh_path is None:
            quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
            quarkx.msgbox(".md5mesh file not loaded\n\nFirst load .md5mesh file in:\n    " + md5_anim_path[0] + "\n\nbefore any .md5anim files from that same folder.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            try:
                progressbar.close()
            except:
                pass
            editor = None   #Reset the global again
            return

        import_md5_model(basepath, filename)

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_md5_import # This imports itself to be passed along so it can be used in mdlmgr.py later for the Specifics page.
quarkpy.qmdlbase.RegisterMdlImporter(".md5mesh Doom3\Quake4 Importer", ".md5mesh file", "*.md5mesh", loadmodel, ie_md5_import)
quarkpy.qmdlbase.RegisterMdlImporter(".md5anim Doom3\Quake4 Importer", ".md5anim file", "*.md5anim", loadmodel, ie_md5_import)


######################################################
# DIALOG SECTION (for Editor's Specifics/Args page)
######################################################
def vtxcolorclick(btn):
    if editor is None:
        global editor
        editor = quarkpy.mdleditor.mdleditor # Get the editor.
    if quarkx.setupsubset(SS_MODEL, "Options")["LinearBox"] == "1":
        editor.ModelVertexSelList = []
        editor.linearbox = "True"
        editor.linear1click(btn)
    else:
        if editor.ModelVertexSelList != []:
            editor.ModelVertexSelList = []
            quarkpy.mdlutils.Update_Editor_Views(editor)


def colorclick(btn):
    if editor is None:
        global editor
        editor = quarkpy.mdleditor.mdleditor # Get the editor.
    if not quarkx.setupsubset(SS_MODEL, "Options")['VertexUVColor'] or quarkx.setupsubset(SS_MODEL, "Options")['VertexUVColor'] == "0":
        quarkx.setupsubset(SS_MODEL, "Options")['VertexUVColor'] = "1"
        quarkpy.qtoolbar.toggle(btn)
        btn.state = quarkpy.qtoolbar.selected
        quarkx.update(editor.form)
        vtxcolorclick(btn)
    else:
        quarkx.setupsubset(SS_MODEL, "Options")['VertexUVColor'] = "0"
        quarkpy.qtoolbar.toggle(btn)
        btn.state = quarkpy.qtoolbar.normal
        quarkx.update(editor.form)

def dataformname(o):
    "Returns the data form for this type of object 'o' (a model's skin texture) to use for the Specific/Args page."
    global editor
    import quarkpy.mdlentities # Used further down in a couple of places.

    # Next line calls for the Shader Module in mdlentities.py to be used.
    external_skin_editor_dialog_plugin = quarkpy.mdlentities.UseExternalSkinEditor()

    # Next line calls for the Vertex U,V Color Module in mdlentities.py to be used.
    vtx_UVcolor_dialog_plugin = quarkpy.mdlentities.UseVertexUVColors()

    # Next line calls for the Vertex Weights Specifics Module in mdlentities.py to be used.
    vertex_weights_specifics_plugin = quarkpy.mdlentities.UseVertexWeightsSpecifics()

    # Next line calls for the Shader Module in mdlentities.py to be used.
    Shader_dialog_plugin = quarkpy.mdlentities.UseShaders()

    dlgdef = """
    {
      Help = "These are the Specific settings for Doom3\Quake4 (.md5mesh) model types."$0D
             "md5 models use 'meshes' the same way that QuArK uses 'components'."$0D
             "Each can have its own special Surface or skin texture settings."$0D
             "These textures may or may not have 'shaders' that they use for special effects."$0D0D22
             "skin name"$22" - The currently selected skin texture name."$0D22
             "edit skin"$22" - Opens this skin texture in an external editor."$0D22
             "Vertex Color"$22" - Color to use for this component's u,v vertex color mapping."$0D
             "            Click the color display button to select a color."$0D22
             "show weight colors"$22" - When checked, if component has vertex weight coloring they will show."$0D
             "          If NOT checked and it has bones with vetexes, those will show."$0D
             "shader file"$22" - Gives the full path and name of the .mtr material"$0D
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
      """ + vtx_UVcolor_dialog_plugin + """
      """ + vertex_weights_specifics_plugin + """
      """ + Shader_dialog_plugin + """
    }
    """

    if editor is None:
        global editor
        editor = quarkpy.mdleditor.mdleditor # Get the editor.
    ico_mdlskv = ico_dict['ico_mdlskv']  # Just to shorten our call later.
    icon_btns = {}                       # Setup our button list, as a dictionary list, to return at the end.
    vtxcolorbtn = quarkpy.qtoolbar.button(colorclick, "Color mode||When active, puts the editor vertex selection into this mode and uses the 'COLR' specific setting as the color to designate these types of vertexes.\n\nIt also places the editor into Vertex Selection mode if not there already and clears any selected vertexes to protect from including unwanted ones by mistake.\n\nAny vertexes selected in this mode will become Color UV Vertexes and added to the component as such. Click the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
    # Sets the button to its current status, that might be effected by another importer file, either on or off.
    if quarkx.setupsubset(SS_MODEL, "Options")['VertexUVColor'] == "1":
        vtxcolorbtn.state = quarkpy.qtoolbar.selected
    else:
        vtxcolorbtn.state = quarkpy.qtoolbar.normal
    vtxcolorbtn.caption = "" # Texts shows next to button and keeps the width of this button so it doesn't change.
    icon_btns['color'] = vtxcolorbtn # Put our button in the above list to return.
    # Next line calls for the Vertex Weights system in mdlentities.py to be used.
    vtxweightsbtn = quarkpy.qtoolbar.button(quarkpy.mdlentities.UseVertexWeights, "Open or Update\nVertex Weights Dialog||When clicked, this button opens the dialog to allow the 'weight' movement setting of single vertexes that have been assigned to more then one bone handle.\n\nClick the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
    vtxweightsbtn.state = quarkpy.qtoolbar.normal
    vtxweightsbtn.caption = "" # Texts shows next to button and keeps the width of this button so it doesn't change.
    icon_btns['vtxweights'] = vtxweightsbtn # Put our button in the above list to return.

    if (editor.Root.currentcomponent.currentskin is not None) and (o.name == editor.Root.currentcomponent.currentskin.name): # If this is not done it will cause looping through multiple times.
        if o.parent.parent.dictspec.has_key("shader_keyword") and o.dictspec.has_key("shader_keyword"):
            if o.parent.parent.dictspec['shader_keyword'] != o.dictspec['shader_keyword']:
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

    if comp.type == ":mc": # Just makes sure what we have is a model component.
        formobj = quarkx.newobj("md5_mc:form")
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
        if not comp.dictspec.has_key('vtx_color'):
            comp['vtx_color'] = "0.75 0.75 0.75"
        # This sections handles the data for this model type skin page form.
        # This makes sure what is selected is a model skin, if so it fills the Skin page data and adds the items to the component.
        # It also handles the shader file which its name is the full path and name of the skin texture.
        if len(comp.dictitems['Skins:sg'].subitems) == 0 or o in comp.dictitems['Skins:sg'].subitems:
            if not comp.dictspec.has_key('shader_file'):
                comp['shader_file'] = "None"
            if not comp.dictspec.has_key('shader_name'):
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
                comp['mesh_shader'] = "None"


# ----------- REVISION HISTORY ------------
#
# $Log: ie_md5_import.py,v $
# Revision 1.49  2012/01/15 07:08:00  cdunde
# Change for proper bone parent setting to avoid invalid bone connections.
#
# Revision 1.48  2012/01/14 22:51:03  cdunde
# Change by DanielPharos to avoid cutting off shader names incorrectly because they have spaces in them.
#
# Revision 1.47  2011/12/28 08:28:22  cdunde
# Setup importer bone['type'] not done yet.
#
# Revision 1.46  2011/12/23 03:15:17  cdunde
# To remove all importers bone ['type'] from ModelComponentList['bonelist'].
# Those should be kept with the individual bones if we decide it is needed.
#
# Revision 1.45  2011/12/16 01:06:21  cdunde
# To co-ordinate better with other model format imports and exports.
# Also file cleanup.
#
# Revision 1.44  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.43  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.42  2010/12/08 21:06:01  cdunde
# Fix to load model even if shader can not be found.
#
# Revision 1.41  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.40  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.39  2010/06/13 15:37:55  cdunde
# Setup Model Editor to allow importing of model from main explorer File menu.
#
# Revision 1.38  2010/05/01 05:01:17  cdunde
# Update by DanielPharos to allow removal of weight_index storage in the ModelComponentList.
#
# Revision 1.37  2010/05/01 04:25:37  cdunde
# Updated files to help increase editor speed by including necessary ModelComponentList items
# and removing redundant checks and calls to the list.
#
# Revision 1.36  2010/04/28 19:23:18  cdunde
# AW CRAP!!!
#
# Revision 1.35  2010/04/28 19:16:52  cdunde
# To add line missed in last change.
#
# Revision 1.34  2010/04/28 19:08:07  cdunde
# To remove ModelComponentList weights_pos correctly by DanielPharos, not needed.
#
# Revision 1.33  2010/04/28 07:17:08  cdunde
# To reverse previous change, causes animation importing to crash.
#
# Revision 1.32  2010/04/27 04:36:54  cdunde
# To remove ModelComponentList weights_pos, not needed.
#
# Revision 1.31  2010/04/23 22:56:00  cdunde
# Proper import changes by DanielPharos and file cleanup.
#
# Revision 1.30  2010/03/20 09:21:47  cdunde
# To add code needed for the baseframe.
#
# Revision 1.29  2010/03/20 05:26:35  cdunde
# Removal of unused code.
#
# Revision 1.28  2010/03/19 22:08:55  cdunde
# Update for correct bone positioning when read in from a model file.
#
# Revision 1.27  2010/03/10 04:24:06  cdunde
# Update to support added ModelComponentList for 'bonelist' updating.
#
# Revision 1.26  2010/03/07 09:43:48  cdunde
# Updates and improvements to both the md5 importer and exporter including animation support.
#
# Revision 1.25  2009/08/28 07:21:34  cdunde
# Minor comment addition.
#
# Revision 1.24  2009/08/27 04:32:20  cdunde
# Update for multiple bone sets for import and export to restrict export of bones for selected components only.
#
# Revision 1.23  2009/08/27 03:59:31  cdunde
# To setup a bone's "flags" dictspec item for model importing and exporting support that use them.
#
# Revision 1.22  2009/08/24 23:39:21  cdunde
# Added support for multiple bone sets for imported models and their animations.
#
# Revision 1.21  2009/08/10 01:08:36  cdunde
# To improve on mesh "shader" name importing to properly naming components.
#
# Revision 1.20  2009/08/09 17:17:24  cdunde
# Added .md5mesh and .md5anim model exporter including bones, skins and shaders.
#
# Revision 1.19  2009/06/09 05:51:48  cdunde
# Updated to better display the Model Editor's Skeleton group and
# individual bones and their sub-bones when they are hidden.
#
# Revision 1.18  2009/06/05 02:24:23  cdunde
# To get bones to move with md5.anim model frames.
#
# Revision 1.17  2009/06/03 05:16:22  cdunde
# Over all updating of Model Editor improvements, bones and model importers.
#
# Revision 1.16  2009/04/28 21:30:56  cdunde
# Model Editor Bone Rebuild merge to HEAD.
# Complete change of bone system.
#
# Revision 1.15  2009/03/04 23:33:14  cdunde
# For proper importer exporter listing one menus, code by DanielPharos.
# Start of code for importing md5anim files.
#
# Revision 1.14  2009/01/29 02:13:51  cdunde
# To reverse frame indexing and fix it a better way by DanielPharos.
#
# Revision 1.13  2009/01/26 18:29:54  cdunde
# Update for correct frame index setting.
# Major update of importing.
#
# Revision 1.12  2008/12/22 05:04:40  cdunde
# Bone vertex assignment update and use of mesh names from imported file.
#
# Revision 1.11  2008/12/20 01:49:49  cdunde
# Update to bones to start assigning vertexes to bone handles,
# only works for single component models with this version.
#
# Revision 1.10  2008/12/19 07:12:42  cdunde
# File updates.
#
# Revision 1.9  2008/12/16 21:50:03  cdunde
# Fixed UV color button setting from one import file to another.
# Added the start for importing bones for this file.
#
# Revision 1.8  2008/12/15 01:46:35  cdunde
# Slight correction.
#
# Revision 1.7  2008/12/15 01:28:11  cdunde
# To update all importers needed message boxes to new quarkx.textbox function.
#
# Revision 1.6  2008/12/14 22:11:29  cdunde
# Needed to fix error causing multiple copies of skins to be made.
#
# Revision 1.5  2008/12/12 05:42:04  cdunde
# To ability to open a component's stored shader file in a text editor.
#
# Revision 1.4  2008/12/11 07:07:00  cdunde
# Added button to change number of lines size of shader text box.
# Added custom icon for UV Color mode function.
#
# Revision 1.3  2008/12/10 20:24:16  cdunde
# To move more code into importers from main mdl files
# and made this importer multi skin per component based on what is used in its shader (materials) file.
#
# Revision 1.2  2008/12/06 19:25:58  cdunde
# Development update.
#
# Revision 1.1  2008/12/05 09:30:14  cdunde
# Added setup file for Doom3 Quake4 .md5mesh and .md5anim model importing.
#
#


