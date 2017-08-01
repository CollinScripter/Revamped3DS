# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for Alice, EF2 and FAKK2 .ska and .skb model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_skb_export.py,v 1.22 2013/02/20 05:19:41 cdunde Exp $


Info = {
   "plug-in":       "ie_skb_exporter",
   "desc":          "This script exports a Alice, EF2 and FAKK2 file (.ska and .skb) and animations.",
   "date":          "Aug. 3 2010",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import struct, sys, os, operator, math
from math import *
import quarkx
import quarkpy.mdleditor
from quarkpy.qutils import *
from types import *
import quarkpy.mdlutils
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
SS_MODEL = 3
logging = 0
exportername = "ie_skb_export.py"
textlog = "ska-skb_ie_log.txt"
editor = None
progressbar = None
file_version = 0
ModelFolder = None


######################################################
# SKB Model Constants
######################################################
MAX_PATH = 64
SKB_MAX_BONES = 256
SKB_MAX_FRAMES = 2048
SKB_MAX_SURFACES = 32
SKB_MAX_TRIANGLES = 8192
SKB_MAX_VERTICES = 4096

######################################################
# SKB data structures
######################################################
class SKB_Bone:
    #Header Structure      #item of data file, size & type,   description.
    parent = 0             #item   0     int, gives the index to the parent bone in the bones list.
    flags = 0              #item   1     int, holds any of the bone flags MD4_BONE_FLAG_H (head), MD4_BONE_FLAG_U (upper), MD4_BONE_FLAG_L (lower), or MD4_BONE_FLAG_T (tag).
    name = ""              #item   2-65  64 char, the bone name.
    if file_version == 4:  #(EF2), these items are read in from the file later.
        basequat = (0)*4   #item   66    66-69   4 signed short ints, the bone's baseframe quat values.
        baseoffset = (0)*3 #item   70    70-72   3 signed short ints, the bone's baseframe offset.
        basejunk1 = 0      #item   73    73      1 signed short int, written to keep pointer count correct, but DO NOT USE.

    binary_format="<2i%ds" % MAX_PATH #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.parent = 0
        self.flags = 0
        self.name = ""
        if file_version == 4:  #(EF2), these items are saved in the file later.
            self.basequat = (0)*4
            self.baseoffset = (0)*3
            self.basejunk1 = 0

    def fill(self, bone, ConvertBoneNameToIndex, ModelFolder):
        self.name = bone.shortname.replace(ModelFolder + "_", "", 1)
        if bone.dictspec['parent_name'] == "None":
            self.parent = -1
        else:
            self.parent = ConvertBoneNameToIndex[bone.dictspec['parent_name']]
        self.flags = 0


    def save(self, file):
        tmpData = [0]*3
        tmpData[0] = self.parent
        tmpData[1] = self.flags
        tmpData[2] = self.name
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2])
        file.write(data)

    def save_baseframe(self, file): # file_version = 4 (EF2) only
        binary_format="<8h"  #little-endian (<), see #item descriptions above.
        tmpData = [0]*8
        tmpData[0] = self.basequat[0]
        tmpData[1] = self.basequat[1]
        tmpData[2] = self.basequat[2]
        tmpData[3] = self.basequat[3]
        tmpData[4] = self.baseoffset[0]
        tmpData[5] = self.baseoffset[1]
        tmpData[6] = self.baseoffset[2]
        tmpData[7] = self.basejunk1
        data = struct.pack(binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7])
        file.write(data)

    def dump(self):
        tobj.logcon ("bone parent: " + str(self.parent))
        tobj.logcon ("bone flags: " + str(self.flags))
        tobj.logcon ("bone name: " + str(self.name))
        tobj.logcon ("")

    def dump_baseframe(self):
        tobj.logcon ("bone name: " + str(self.name))
        tobj.logcon ("bone basequat: " + str(self.basequat))
        tobj.logcon ("bone baseoffset: " + str(self.baseoffset))
        tobj.logcon ("")


class SKB_Surface:
    # ident = 541870931 = "SKL "
    #Header Structure    #item of data file, size & type,   description.
    ident = "SKL "       #item   0    int but written as 4s string to convert to alpha, used to identify the file (see above).
    name = ""            #item   1    1-64 64 char, the surface (mesh) name.
    numTriangles = 0     #item  65    int, number of triangles.
    numVerts = 0         #item  66    int, number of verts.
    minLod = 0           #item  67    int, unknown.
    ofsTriangles = 0     #item  68    int, offset for triangle 3 vert_index data.
    ofsVerts = 0         #item  69    int, offset for VERTICES data.
    ofsCollapseMap = 0   #item  70    int, offset where Collapse Map begins, NumVerts * int.
    ofsEnd = 0           #item  71    int, next Surface data follows ex: (header) ofsSurfaces + (1st surf) ofsEnd = 2nd surface offset.

    Triangles = []
    Vert_coords = {}
    CollapseMapVerts = []

    binary_format="<4s%ds7i" % MAX_PATH #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.ident = "SKL "
        self.name = ""
        self.numTriangles = 0
        self.numVerts = 0
        self.minLod = 0
        self.ofsTriangles = 0
        self.ofsVerts = 0
        self.ofsCollapseMap = 0
        self.ofsEnd = 0

        self.Triangles = []
        self.Vert_coords = []
        self.CollapseMapVerts = []

    def fill(self, Component, QuArK_bones, ConvertBoneNameToIndex):
        #Get the QuArK's ModelComponentList['bonelist'].
        bonelist = editor.ModelComponentList['bonelist']

        surf_offset_pointer = struct.calcsize(self.binary_format) # Add its header size in bytes (see above).

        # Get this Component's baseframe vertices and Component's name.
        baseframe = Component.dictitems['Frames:fg'].dictitems['baseframe:mf']
        vertices = baseframe.vertices
        comp_name = Component.name
        Tris = Component.triangles
        user_skins_list = Component.dictitems['Skins:sg']
        if str(Component.dictspec['skinsize']) != str(user_skins_list.subitems[0].dictspec['Size']):
            Component['skinsize'] = user_skins_list.subitems[0].dictspec['Size']
        skinsize = Component.dictspec['skinsize']

        UVs_of_vert = {}
        old_verts = [] #For quick saving of duplicate x,y,z + weights

        # Fill the Triangles and UVs vert_coord data.
        self.ofsTriangles = surf_offset_pointer
        if logging == 1:
            tobj.logcon ("-----------------------------------")
            tobj.logcon ("Triangle vert_indexes, numTriangles: " + str(self.numTriangles))
            tobj.logcon ("-----------------------------------")
        for i in xrange(0, len(Tris)):
            tri = SKB_Triangle()
            Ctri = Tris[i]
            new_Ctri = []
            if logging == 1:
                tobj.logcon ("tri " + str(i) + " " + str(tri.indices))
            for j in xrange(3):
                vert_index = Ctri[j][0]
                vert_coord = SKB_VertCoord()
                vert_coord.fill(Ctri[j], skinsize)
                if UVs_of_vert.has_key(vert_index):
                    #We've seen this vert_index before
                    FoundAVert = 0
                    for k in xrange(len(UVs_of_vert[vert_index])):
                        UV = UVs_of_vert[vert_index][k]
                        if (abs(UV[0] - vert_coord.uv[0]) < 0.001) and (abs(UV[1] - vert_coord.uv[1]) < 0.001):
                            #Same UV; recycle vert
                            new_vert_index = UV[2]
                            FoundAVert = 1
                            break
                    if not FoundAVert:
                        #Same vert_index, but different UV: split it!
                        new_vert_index = len(old_verts)
                        old_verts += [vert_index]
                        self.Vert_coords.append(vert_coord)
                        UVs_of_vert[vert_index] += [(vert_coord.uv[0], vert_coord.uv[1], new_vert_index)]
                else:
                    #Totally new vert_index
                    new_vert_index = len(old_verts)
                    old_verts += [vert_index]
                    self.Vert_coords.append(vert_coord)
                    UVs_of_vert[vert_index] = [(vert_coord.uv[0], vert_coord.uv[1], new_vert_index)]
                new_Ctri += [(new_vert_index, vert_coord.uv[0], vert_coord.uv[1])]
            tri.fill(new_Ctri)
            self.Triangles.append(tri)
        if logging == 1:
            tobj.logcon ("")

        self.numTriangles = len(self.Triangles)
        self.numVerts = len(old_verts)
        self.minLod = self.numVerts

        surf_offset_pointer = surf_offset_pointer + (self.numTriangles * (3 * 4))

        # Fill the Tex Coords normal and weights data.
        self.ofsVerts = surf_offset_pointer
        verts_pointer = 0

        if logging == 1:
            tobj.logcon ("-----------------------------")
            tobj.logcon ("Vert UV's & Weights, numVerts: " + str(self.numVerts))
            tobj.logcon ("-----------------------------")

        # Get this Component's ModelComponentList 'weightvtxlist'.
        weightvtxlist = editor.ModelComponentList[comp_name]['weightvtxlist']
        #Data Structure    #item of data file, size & type,   description.
        # normal            item   0-11    3 floats * 4 bytes ea.
        # uv                item   12-17   2 floats * 4 bytes ea., the UV values for the skin texture(read in the SKB_VertCoord class section).
        # num_weights       item   18      1 int    * 4 bytes, number of weights the current vertex has, 1 weight = assigned amount to a single bone.
        for i in xrange(0, self.numVerts):
            verts_pointer = verts_pointer + (6 * 4) # Count for (see above).
            vert = self.Vert_coords[i]
            old_vert_index = old_verts[i]
            vert_weights = weightvtxlist[old_vert_index]
            bonenames = vert_weights.keys()
            vert.num_weights = len(bonenames)
            if logging == 1:
                tobj.logcon ("vert " + str(i) + " U,V: " + str(vert.uv))
                tobj.logcon ("  num_weights " + str(vert.num_weights))
                tobj.logcon ("  =============")
            #Data Structure    #item of data file, size & type,   description.
            # boneIndex         item   0    int, the bone index number in list order.
            # weight_value      item   1    float, this is the QuArK ModelComponentList['weightvtxlist'][vertex]['weight_value']
            # vtx_offset        item   2-4  3 floats, offset between the bone position and a vertex's position.
            verts_pointer = verts_pointer + (vert.num_weights * (5 * 4)) # binary_format = "<if3f" or 5 items/4 bytes each.

            vtx_pos = vertices[old_vert_index]
            fix_offsets = None
            for j in xrange(0, vert.num_weights):
                boneIndex = ConvertBoneNameToIndex[bonenames[j]]
                weight_value = vert_weights[bonenames[j]]['weight_value']
                try: # Alice, FAKK2 or EF2 model being exported. Could also be for MOHAA, uses vtx_offset as well with changes.
                    vtx_offset = vert_weights[bonenames[j]]['vtx_offset']
                    QuArK_bone = QuArK_bones[boneIndex]
                    if QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'].startswith('skb-'):
                        if weight_value == 1.0:
                            check_pos = vtx_pos.tuple
                            if str(check_pos) != str(vtx_offset):
                                vtx_offset = check_pos
                        else:
                            vtx_offsets = quarkx.vect(0.0, 0.0, 0.0)
                            for k in xrange(0, vert.num_weights):
                                vtx_offsets += quarkx.vect(vert_weights[bonenames[k]]['vtx_offset'])
                            ovp = (vtx_offsets / vert.num_weights).tuple             # ovp = original vtx_pos (computed)
                            cp = (round(ovp[0],6), round(ovp[1],6), round(ovp[2],6)) # cp = compare vtx pos
                            vp = vtx_pos.tuple
                            if (fix_offsets is None) and ((abs(cp[0]) > abs(vp[0])+0.1) or (abs(cp[0]) < abs(vp[0])-0.1) or (abs(cp[1]) > abs(vp[1])+0.1) or (abs(cp[1]) < abs(vp[1])-0.1) or (abs(cp[2]) > abs(vp[2])+0.1) or (abs(cp[2]) < abs(vp[2])-0.1)):
                                fix_offsets = 1
                        if fix_offsets is not None:
                            temp = [0.0, 0.0, 0.0]
                            vo = vert_weights[bonenames[j]]['vtx_offset']
                            for k in xrange(3):
                                temp[k] = (vp[k] * (vo[k] / ovp[k]))
                            vtx_offset = (temp[0], temp[1], temp[2])
                except: # Handles other model formats, HL1 here, exporting as skb models (mesh only).
                    try: # only handles a weight_value of 1.0, need to add for more then 1 weight, see how just above here.
                        Bpos = bonelist[bonenames[j]]['frames']['baseframe:mf']['position']
                        Brot = quarkx.matrix(bonelist[bonenames[j]]['frames']['baseframe:mf']['rotmatrix'])
                        vtx_offset = (~Brot * (vtx_pos - quarkx.vect(Bpos))).tuple
                    except: # Should NEVER happen, no bones? Get rid of the try statement.
                        vtx_offset = vtx_pos.tuple

                if logging == 1:
                    tobj.logcon ("  weight " + str(j))
                    tobj.logcon ("    boneIndex " + str(boneIndex))
                    tobj.logcon ("    weight_value " + str(weight_value))
                    tobj.logcon ("    vtx_offset " + str(vtx_offset))

                vert.weights[j] = [boneIndex, weight_value, vtx_offset]

            if logging == 1:
        #        tobj.logcon ("    vtxweight " + str(weightvtxlist[old_vert_index]))
                tobj.logcon ("    -------------")

        # CollapseMap data here - the reduction of number of model mesh faces when viewed further away.
        surf_offset_pointer = surf_offset_pointer + verts_pointer
        self.ofsCollapseMap = surf_offset_pointer
        surf_offset_pointer = surf_offset_pointer + (self.numVerts * 4)
        self.ofsEnd = surf_offset_pointer

    def save(self, file):
        # Write this surface (Component's) header.
        tmpData = [0]*9
        tmpData[0] = self.ident
        tmpData[1] = self.name
        tmpData[2] = self.numTriangles
        tmpData[3] = self.minLod
        tmpData[4] = self.numVerts
        tmpData[5] = self.ofsTriangles
        tmpData[6] = self.ofsVerts
        tmpData[7] = self.ofsCollapseMap
        tmpData[8] = self.ofsEnd
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8])
        file.write(data)

        # Write this surface (Component's) Triangles.
        for tri in self.Triangles:
            tri.save(file)

        # Write this surface (Component's) Vert_coords.
        for i in xrange(0, self.numVerts):
            vert = self.Vert_coords[i]
            vert.save_vert(file)
            vert.save_weights(file)

        # Write this surface (Component's) CollapseMap.
        binary_format = "<i"
        for i in xrange(0, self.numVerts):
            data = struct.pack(binary_format, i)
            file.write(data)

    def dump(self):
        tobj.logcon ("ident: " + self.ident)
        tobj.logcon ("name: " + str(self.name))
        tobj.logcon ("numTriangles: " + str(self.numTriangles))
        tobj.logcon ("minLod: " + str(self.minLod))
        tobj.logcon ("numVerts: " + str(self.numVerts))
        tobj.logcon ("ofsTriangles: " + str(self.ofsTriangles))
        tobj.logcon ("ofsVerts: " + str(self.ofsVerts))
        tobj.logcon ("ofsCollapseMap: " + str(self.ofsCollapseMap))
        tobj.logcon ("ofsEnd: " + str(self.ofsEnd))


class SKB_VertCoord:
    #Header Structure    #item of data file, size & type,   description.
    normal = [0]*3  # item   0-2    3 floats, a vertex's x,y,z normal values.
    uv = [0]*2      # item   3-4    2 floats, a vertex's U,V values.
    num_weights = 1 # item   5      1 int, number of weights the current vertex has, 1 weight = assigned amount to a single bone.

    binary_format="<5fi" #little-endian (<), (see above)
    
    weights = {}

    def __init__(self):
        self.normal = [0]*3
        self.uv = [0]*2
        self.num_weights = 1

        self.weights = {}

    def fill(self, Ctri, skinsize):
        self.uv = [float(Ctri[1]/skinsize[0]), float(Ctri[2]/skinsize[1])]

    def save_vert(self, file):
        tmpData = [0]*6
        tmpData[0] = self.normal[0]
        tmpData[1] = self.normal[1]
        tmpData[2] = self.normal[2]
        tmpData[3] = self.uv[0]
        tmpData[4] = self.uv[1]
        tmpData[5] = self.num_weights
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5])
        file.write(data)

    def save_weights(self, file):
        binary_format = "<if3f"
        for j in xrange(0, self.num_weights):
            boneIndex, weight_value, vtx_offset = self.weights[j]
            tmpData = [0]*5
            tmpData[0] = boneIndex
            tmpData[1] = weight_value
            tmpData[2] = vtx_offset[0]
            tmpData[3] = vtx_offset[1]
            tmpData[4] = vtx_offset[2]
            data = struct.pack(binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4])
            file.write(data)


class SKB_Triangle:
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


class skb_obj:
    file_pointer = 0
    header_size = 0

    # SKB ident = 541870931 or "SKL " version = 3 Alice and  FAKK2, EF2 uses version 4.
    #Header Structure    #item of data file, size & type,   description.
    ident = "SKL "       #item   0    int but written as 4s string to convert to alpha, used to identify the file (see above).
    version = 0          #item   1    int, version number of the file (see above).
                         #### Items below filled in after version is determined.
    name = ""            #item   0    0-63 64 char, the models path and full name.
    numSurfaces = 0      #item  64    int, number of mesh surfaces.
    numBones = 0         #item  65    int, number of bones.
    ofsBones = 0         #item  66    int, the file offset for the bone names data.
    ofsSurfaces = 0      #item  67    int, the file offset for the surface (mesh) data (for the 1st surface).
    # If file_version = 4 Added EF2 data.
    ofsBaseFrame = 0     #item v4=68  int,  end (or length) of the file.
    ofsEnd = 0           #item v3=68, v4=69 int, end (or length) of the file.

    binary_format="<4si%ds5i" % MAX_PATH  #little-endian (<), see #item descriptions above.

    #skb data objects
    surfaceList = []
    bones = [] # To put our exporting bones into.

    def __init__(self):
        self.file_pointer = 0
        self.header_size = (7 * 4) + 64

        self.ident = "SKL "
        self.version = file_version
        self.name = ""
        self.numSurfaces = 0
        self.numBones = 0
        self.ofsBones = 0
        self.ofsSurfaces = 0
        if self.version == 4: # Added EF2 data.
            self.header_size = self.header_size + 4
            self.ofsBaseFrame = 0
        self.ofsEnd = 0

        if file_version == 4:
            self.binary_format="<4si%ds6i" % MAX_PATH  #little-endian (<), see #item descriptions above.

        self.surfaceList = []
        self.bones = []

    def save(self, file):
        # Write the header.
        if file_version == 4: # Added EF2 data.
            tmpData = [0]*9
        else:
            tmpData = [0]*8
        tmpData[0] = self.ident
        tmpData[1] = self.version
        tmpData[2] = self.name
        tmpData[3] = self.numSurfaces
        tmpData[4] = self.numBones
        tmpData[5] = self.ofsBones
        tmpData[6] = self.ofsSurfaces
        if self.version == 4:
            tmpData[7] = self.ofsBaseFrame
            tmpData[8] = self.ofsEnd
            data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8])
        else:
            tmpData[7] = self.ofsEnd
            data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7])
        file.write(data)

        # Write the bones.
        for bone in self.bones:
            bone.save(file)

        # Write the surfaces.
        for surface in self.surfaceList:
            surface.save(file)

        # If an EF2 export, Fill the BaseFrame Bone data.
        if file_version == 4: # Added EF2 data.
            for bone in self.bones:
                bone.save_baseframe(file)

    def dump(self):
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + self.ident)
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("name: " + self.name)
            tobj.logcon ("number of surfaces: " + str(self.numSurfaces))
            tobj.logcon ("number of bones: " + str(self.numBones))
            tobj.logcon ("offset for bone data: " + str(self.ofsBones))
            tobj.logcon ("offset for surface mesh data: " + str(self.ofsSurfaces))
            if self.version == 4: # Added EF2 data.
                tobj.logcon ("offset for BaseFrame (EF2) data: " + str(self.ofsBaseFrame))
            tobj.logcon ("offset for end (or length) of file: " + str(self.ofsEnd))
            tobj.logcon ("")


######################################################
# FILL SKB OBJ DATA STRUCTURE
######################################################
    def fill_skb_obj(self, file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
        message = ""
        self.file_pointer = self.header_size # Update our pointer for the file header that will be written first in the "save" call.

        # Fill the Bones data.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("==========================")
            tobj.logcon ("PROCESSING BONES, numBones: " + str(self.numBones))
            tobj.logcon ("==========================")
            tobj.logcon ("")
        self.ofsBones = self.file_pointer
        for i in xrange(0, self.numBones):
            bone = SKB_Bone()
            QuArK_bone = QuArK_bones[i]
            bone.fill(QuArK_bone, ConvertBoneNameToIndex, ModelFolder)
            self.bones.append(bone)
            if logging == 1:
                tobj.logcon ("Bone " + str(i))
                bone.dump()
        self.file_pointer = self.ofsBones + (self.numBones * ((2 * 4)+64))

        # Fill the surfaces (meshes) data.
        self.ofsEnd = self.ofsSurfaces = self.file_pointer
        for i in xrange(0, self.numSurfaces):
            if logging == 1:
                tobj.logcon ("=====================")
                tobj.logcon ("PROCESSING SURFACE: " + str(i))
                tobj.logcon ("=====================")
                tobj.logcon ("")
            surface = SKB_Surface()
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
            surface.fill(Component, QuArK_bones, ConvertBoneNameToIndex)
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("----------------")
                tobj.logcon ("Surface " + str(i) + " Header")
                tobj.logcon ("----------------")
                surface.dump()
                tobj.logcon ("")
            self.surfaceList.append(surface)
            self.file_pointer = self.file_pointer + surface.ofsEnd

        # If an EF2 export, Fill the BaseFrame Bone data.
        if file_version == 4: # Added EF2 data.
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("==========================")
                tobj.logcon ("PROCESSING BASEFRAME BONES, numBones: " + str(self.numBones))
                tobj.logcon ("==========================")
                tobj.logcon ("")
            self.ofsBaseFrame = self.file_pointer
            bonelist = editor.ModelComponentList['bonelist']
            factor = 64.0
            scale = 32767.0 # To convert quaternion-units into rotation values.
            # Use bonelist for mesh baseframe exporting and NOT the bones themselves.
            # If another frame is current the bones contain those positions and matrixes.
            for i in xrange(0, self.numBones):
                QuArK_bone = QuArK_bones[i]
                QuArK_Bone_name = QuArK_bone.name
                if bonelist.has_key(QuArK_Bone_name):
                    bone_pos = bonelist[QuArK_Bone_name]['frames']['baseframe:mf']['position']
                    bone_rot = bonelist[QuArK_Bone_name]['frames']['baseframe:mf']['rotmatrix']
                    bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                    bone_rot = matrix2quaternion(bone_rot)

                    bone = self.bones[i]
                    bone.basequat = (int(bone_rot[0] * scale), int(bone_rot[1] * scale), int(bone_rot[2] * scale), int(bone_rot[3] * scale))
                    # For Half-Life 1 model being exported.
                    if QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'HL1':
                        bone.baseoffset = (int(bone_pos[1] * -factor), int(bone_pos[0] * factor), int(bone_pos[2] * factor))
                    else: # For Alice, FAKK2, EF2 or other model being exported.
                        bone.baseoffset = (int(bone_pos[0] * factor), int(bone_pos[1] * factor), int(bone_pos[2] * factor))

                    if logging == 1:
                        tobj.logcon ("Bone " + str(i))
                        bone.dump_baseframe()
                else:
                    if logging == 1:
                        tobj.logcon ("UNUSED Bone: " + QuArK_Bone_name.replace(":bone", ""))

            self.file_pointer = self.ofsBaseFrame + (self.numBones * (8 * 2))

        self.ofsEnd = self.file_pointer

        return message


######################################################
# SKA data structures
######################################################
class SKA_BoneName_EF2:
    #Header Structure       #item of data file, size & type,   description.
    ID = 0          #item   0       0     1 int, the bone's ID.
    name = ""       #item   1-31    1-31  32 char, the bone's name.

    binary_format="<f%ds" % (MAX_PATH * .5)  #little-endian (<), see items above.

    def __init__(self):
        self.ID = 0
        self.name = ""

    def save(self, file):
        tmpData = [0]*2
        tmpData[0] = self.ID
        tmpData[1] = self.name
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1])
        file.write(data)

    def dump(self):
        tobj.logcon ("ID: " + str(self.ID))
        tobj.logcon ("name: " + str(self.name))

class SKA_Bone:
    #Header Structure       #item of data file, size & type,   description.
    matrix = [0]*4          #item   0    0-3   4 ints, the bone's quat values.
    offset = [0]*3          #item   4    4-6   3 ints, the bone's offset.
    junk1 = 0               #item   7    7     1 int, read in to keep pointer count correct, but DO NOT USE.

    binary_format="<4h3hh"  #little-endian (<), see items above.

    def __init__(self):
        self.matrix = [0]*4
        self.offset = [0]*3
        self.junk1 = 0

    def save(self, file):
        tmpData = [0]*8
        tmpData[0] = self.matrix[0]
        tmpData[1] = self.matrix[1]
        tmpData[2] = self.matrix[2]
        tmpData[3] = self.matrix[3]
        tmpData[4] = self.offset[0]
        tmpData[5] = self.offset[1]
        tmpData[6] = self.offset[2]
        tmpData[7] = self.junk1
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7])
        file.write(data)

    def dump(self):
        tobj.logcon ("quat pos: " + str(self.matrix))
        tobj.logcon ("offset pos: " + str(self.offset))
        tobj.logcon ("junk1: " + str(self.junk1))
        tobj.logcon ("")

class SKA_Frame:
    #Header Structure            #item of data file, size & type,   description.
    bounds = [[0.0]*3, [0.0]*3]  #item   0    0-5 6 floats, the frame's bboxMin and bboxMax.
    radius = 0.0                 #item   6    float, dist from origin to corner.
    delta = [0.0]*3              #item   7    7-9 3 floats.

    bones = [] # To store the animation bones in for processing the file.

    binary_format="<6ff3f"  #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.bounds = [[0.0]*3, [0.0]*3]
        self.radius = 0.0
        self.delta = [0.0]*3
        self.bones = []

    def fill(self, frame_name, frame_maxs, frame_offset, frame_scale, bonelist, numBones, QuArK_bones, ConvertBoneNameToIndex): # parent_indexes, real_bone_index, index_to_ska
        for i in xrange(0, numBones):
            bone = SKA_Bone()
            QuArK_bone = QuArK_bones[i]
            offset = [0]*3
            scale = 32767.0 # To convert quaternion-units into rotation values.

            if QuArK_bone.dictspec['parent_name'] != "None":
                parent_bone = QuArK_bones[ConvertBoneNameToIndex[QuArK_bones[i].dictspec['parent_name']]]
                parent_pos = quarkx.vect(bonelist[parent_bone.name]['frames'][frame_name]['position']) # SetPosition
                parent_rot = quarkx.matrix(bonelist[parent_bone.name]['frames'][frame_name]['rotmatrix']) # SetRotation
                bone_pos = quarkx.vect(bonelist[QuArK_bone.name]['frames'][frame_name]['position'])
                bone_pos = (~parent_rot * (bone_pos - parent_pos)).tuple
                parent_pos = parent_pos.tuple
                for j in xrange(0, 3):
                    if bone_pos[j] == frame_maxs[j]:
                        offset[j] = 32767
                    else:
                        offset[j] = int(bone_pos[j] * 64.0)
                bone_rot = quarkx.matrix(bonelist[QuArK_bone.name]['frames'][frame_name]['rotmatrix'])
                bone_rot = (~parent_rot * bone_rot).tuple
                bone_rot = ((bone_rot[0][0], bone_rot[1][0], bone_rot[2][0], 0.0), (bone_rot[0][1], bone_rot[1][1], bone_rot[2][1], 0.0), (bone_rot[0][2], bone_rot[1][2], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                bone_rot = matrix2quaternion(bone_rot)
                bone.matrix = (int(bone_rot[0] * scale), int(bone_rot[1] * scale), int(bone_rot[2] * scale), int(bone_rot[3] * scale))
            else:
                bone_pos = bonelist[QuArK_bone.name]['frames'][frame_name]['position'] # bone.SetPosition
                bone_rot = bonelist[QuArK_bone.name]['frames'][frame_name]['rotmatrix'] # bone.SetRotation
                bone_rot = ((bone_rot[0][0], bone_rot[1][0], bone_rot[2][0], 0.0), (bone_rot[0][1], bone_rot[1][1], bone_rot[2][1], 0.0), (bone_rot[0][2], bone_rot[1][2], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                bone_rot = matrix2quaternion(bone_rot)
                bone.matrix = [int(bone_rot[0] * scale), int(bone_rot[1] * scale), int(bone_rot[2] * scale), int(bone_rot[3] * scale)]
                for j in xrange(0, 3):
                    if bone_pos[j] == frame_maxs[j]:
                        offset[j] = 32767
                    else:
                        offset[j] = int(bone_pos[j] * 64.0)

            bone.offset = [offset[0], offset[1], offset[2]]
            self.bones.append(bone)

            if logging == 1:
                tobj.logcon ("bone " + str(i))
                bone.dump()

    def save(self, file):
        tmpData = [0]*10
        tmpData[0] = self.bounds[0][0]
        tmpData[1] = self.bounds[0][1]
        tmpData[2] = self.bounds[0][2]
        tmpData[3] = self.bounds[1][0]
        tmpData[4] = self.bounds[1][1]
        tmpData[5] = self.bounds[1][2]
        tmpData[6] = self.radius
        tmpData[7] = self.delta[0]
        tmpData[8] = self.delta[1]
        tmpData[9] = self.delta[2]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9])
        file.write(data)

    def dump(self):
        tobj.logcon ("bounds: " + str(self.bounds))
        tobj.logcon ("radius: " + str(self.radius))
        tobj.logcon ("delta: " + str(self.delta))


class ska_obj:
    file_pointer = 0
    header_size = 0

    # SKA ident = 1312901971 or "SKAN" version = 3 Alice and  FAKK2, EF2 uses version 4.
    #Header Structure    #item of data file, size & type,   description.
    ident = "SKAN"       #item   0    int but written as 4s string to convert to alpha, used to identify the file (see above).
    version = 0          #item   1    int, version number of the file (see above).
                         #### Items below filled in after version is determined.
    name = ""            #item   2    2-65 64 char, the models path and full name.
    type = 0             #item  66    int, unknown.
    numFrames = 0        #item  67    int, number of mesh animation frames.
    numBones = 0         #item  68    int, number of bones.
    totaltime = 0        #item  69    float, the time duration for the complete animation sequence.
    frametime = 0        #item  70    float, the time duration for a single frame, FPS (frames per second).
    totaldelta = [0.0]*3 #item  71    71-73 3 floats, the file offset for the surface (mesh) data (for the 1st surface).
    ofsBones = 0         #item  74    int, only used for EF2 file.
    ofsFrames = 0        #item  74\75 int, offset for the frames data.

    binary_format="<4si%ds3i2f3fi" % MAX_PATH #little-endian (<), see #item descriptions above.

    #ska data objects
    bone_names = []
    frames = []

    def __init__(self):
        self.file_pointer = 0
        self.header_size = (11 * 4) + 64

        self.ident = "SKAN"
        self.version = file_version
        self.name = ""
        self.type = 0
        self.numFrames = 0
        self.numBones = 0
        self.totaltime = 0
        self.frametime = 0.0500000007451
        self.totaldelta = [0.0]*3
        if self.version == 4: # Added EF2 data.
            self.header_size = self.header_size + 4
            self.ofsBones = 0
        self.ofsFrames = 0

        if file_version == 4:
            self.binary_format="<4si%ds3i2f3f2i" % MAX_PATH  #little-endian (<), see #item descriptions above.
        
        self.bone_names = []
        self.frames = []

    def save(self, file):
        # Write the header.
        if file_version == 4: # Added EF2 data.
            tmpData = [0]*13
        else:
            tmpData = [0]*12
        tmpData[0] = self.ident
        tmpData[1] = self.version
        tmpData[2] = self.name
        tmpData[3] = self.type
        tmpData[4] = self.numFrames
        tmpData[5] = self.numBones
        tmpData[6] = self.totaltime
        tmpData[7] = self.frametime
        tmpData[8] = self.totaldelta[0]
        tmpData[9] = self.totaldelta[1]
        tmpData[10] = self.totaldelta[2]
        if self.version == 4:
            tmpData[11] = self.ofsBones
            tmpData[12] = self.ofsFrames
            data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12])
        else:
            tmpData[11] = self.ofsFrames
            data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11])
        file.write(data)

        # If an EF2 export, Write the BoneNames data.
        if file_version == 4: # Added EF2 data.
            for i in xrange(0, self.numBones):
                bone_name = self.bone_names[i]
                bone_name.save(file)

        # Write the Frames.
        for frame in self.frames:
            frame.save(file)
            for bone in frame.bones:
                bone.save(file)

    def fill_ska_obj(self, file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
        message = ""
        self.file_pointer = self.header_size # Update our pointer for the file header that will be written first in the "save" call.

        if self.version == 3:
            self.ofsFrames = self.file_pointer
        else:
            # EF2 has ofsBones in there
            self.ofsBones = self.file_pointer
            self.file_pointer = self.file_pointer + (self.numBones * (4 + 32))
            self.ofsFrames = self.file_pointer

        if self.version == 4:
            #EF2 has bone_names
            for i in xrange(0, self.numBones):
                QuArK_bone = QuArK_bones[i]
                if QuArK_bone.dictspec['parent_name'] != "None":
                    parent_bone = QuArK_bones[ConvertBoneNameToIndex[QuArK_bone.dictspec['parent_name']]]
                    vect_diff = QuArK_bone.position - parent_bone.position
                    vect_diff = vect_diff.tuple
                    ID = math.sqrt((vect_diff[0] * vect_diff[0]) + (vect_diff[1] * vect_diff[1]) + (vect_diff[2] * vect_diff[2]))
                else:
                    ID = 0.0
                
                bone_name = SKA_BoneName_EF2()
                bone_name.ID = ID
                try:
                    bone_name.name = QuArK_bone.shortname.replace(ModelFolder + "_", "", 1)
                except:
                    bone_name.name = QuArK_bone.shortname.split("_", 1)[1]
                self.bone_names.append(bone_name)
                if logging == 1:
                    tobj.logcon ("BoneName " + str(i))
                    bone_name.dump()

        #Setup some lists we will need.
        framesgroups = []
        baseframes = []
        comp_names = []
        numComponents = len(QuArK_comps)
        for i in xrange(0, numComponents):
            comp_names = comp_names + [QuArK_comps[i].name]
            framesgroup = QuArK_comps[i].dictitems['Frames:fg']
            baseframes = baseframes + [framesgroup.dictitems['baseframe:mf']]
            framesgroups = framesgroups + [framesgroup]

        #Get the QuArK's ModelComponentList['bonelist'].
        bonelist = editor.ModelComponentList['bonelist']

        #fill the Frames
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("============================")
            tobj.logcon ("PROCESSING FRAMES: ")
            tobj.logcon ("============================")
            tobj.logcon ("")
        frame_count = self.numFrames
        for i in xrange(0, frame_count):
            frame = SKA_Frame()
            # We need to start with the bounding box of all the components being exported combined.
            mins = [10000.0, 10000.0, 10000.0]
            maxs = [-10000.0, -10000.0, -10000.0]
            for j in xrange(0, numComponents):
                vertices = framesgroups[j].subitems[i].vertices
                bounding_box = quarkx.boundingboxof(vertices) # Uses each component's frame.vertices
                bboxMin = bounding_box[0].tuple
                bboxMax = bounding_box[1].tuple
                for k in xrange(3):
                    if bboxMin[k] < mins[k]:
                        mins[k] = bboxMin[k]
                    if bboxMax[k] > maxs[k]:
                        maxs[k] = bboxMax[k]
            frame.bounds = [[mins[0], mins[1], mins[2]], [maxs[0], maxs[1], maxs[2]]]
            frame.radius = RadiusFromBounds(mins, maxs)

            frame_name = framesgroups[0].subitems[i].name
            frame_maxs = [maxs[0], maxs[1], maxs[2]]
            frame_offset = ((quarkx.vect(mins[0], mins[1], mins[2]) + quarkx.vect(maxs[0], maxs[1], maxs[2])) / 2).tuple
            frame_scale = [0.0, 0.0, 0.0]
            for j in xrange(0, 3):
                frame_scale[j] = (maxs[j] - mins[j]) / 65536
            if frame_name.find("baseframe") != -1:
                self.numFrames -= 1
                continue
            self.frames.append(frame)

            frame.fill(frame_name, frame_maxs, frame_offset, frame_scale, bonelist, self.numBones, QuArK_bones, ConvertBoneNameToIndex)
            if logging == 1:
                tobj.logcon ("---------------------")
                tobj.logcon ("frame " + str(i))
                tobj.logcon ("---------------------")
                frame.dump()
                tobj.logcon ("=====================")
                tobj.logcon ("")

        self.totaltime = self.numFrames * self.frametime
        return message

    def dump(self):
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + self.ident)
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("name: " + self.name)
            tobj.logcon ("type: " + str(self.type))
            tobj.logcon ("number of frames: " + str(self.numFrames))
            tobj.logcon ("number of bones: " + str(self.numBones))
            tobj.logcon ("anim. duration: " + str(self.totaltime))
            tobj.logcon ("anim. FPS: " + str(self.frametime))
            tobj.logcon ("total delta: " + str(self.totaldelta))
            if self.version == 4:
                tobj.logcon ("bonenames offset: " + str(self.ofsBones))
            tobj.logcon ("frames data offset: " + str(self.ofsFrames))
            tobj.logcon ("")

######################################################
# Export functions for Alice EF2 and FAKK2
######################################################
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
# Export math functions
######################################################
def matrix2quaternion(m):
    #See: http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/index.htm
    trace = m[0][0] + m[1][1] + m[2][2]
    if trace > 0.0:
        s = math.sqrt(m[3][3] + trace) * 2.0
        return quaternion_normalize([
        (m[2][1] - m[1][2]) / s,
        (m[0][2] - m[2][0]) / s,
        (m[1][0] - m[0][1]) / s,
        0.25 * s,
        ])
    elif ((m[0][0] > m[1][1]) and (m[0][0] > m[2][2])):
        s = math.sqrt(m[3][3] + m[0][0] - m[1][1] - m[2][2]) * 2.0
        return quaternion_normalize([
        0.25 * s,
        (m[0][1] + m[1][0]) / s,
        (m[0][2] + m[2][0]) / s,
        (m[2][1] - m[1][2]) / s,
        ])
    elif (m[1][1] > m[2][2]):
        s = math.sqrt(m[3][3] + m[1][1] - m[0][0] - m[2][2]) * 2.0
        return quaternion_normalize([
        (m[0][1] + m[1][0]) / s,
        0.25 * s,
        (m[1][2] + m[2][1]) / s,
        (m[0][2] - m[2][0]) / s,
        ])
    else:
        s = math.sqrt(m[3][3] + m[2][2] - m[0][0] - m[1][1]) * 2.0
        return quaternion_normalize([
        (m[0][2] + m[2][0]) / s,
        (m[1][2] + m[2][1]) / s,
        0.25 * s,
        (m[1][0] - m[0][1]) / s,
        ])

def quaternion_normalize(q):
    l = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
    return q[0] / l, q[1] / l, q[2] / l, q[3] / l


############################
# CALL TO EXPORT ANIMATION (.ska) FILE
############################
# QuArK_bones = A list of all the bones in the QuArK's "Skeleton:bg" folder, in their proper tree-view order, to get our bones from.
def save_ska(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
    file = open(filename, "wb")
    ska = ska_obj() # Making an "instance" of this class.
    ska.name = filename.rsplit("\\", 1)[1]
    ska.numFrames = len(QuArK_comps[0].dictitems['Frames:fg'].subitems)
    ska.numBones = len(QuArK_bones)

    # Fill the needed data for exporting.
    message = ska.fill_ska_obj(file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder) # Calling this class function to read the file data and create the animation frames.

    #actually write it to disk
    ska.save(file)
    file.close()
    if logging == 1:
        ska.dump() # Writes the file Header last to the log for comparison reasons.

    return message


############################
# CALL TO EXPORT MESH (.skb) FILE
############################
def save_skb(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
    file = open(filename, "wb")
    skb = skb_obj() # Making an "instance" of this class.
    skb.name = filename.rsplit("\\", 1)[1]
    skb.numSurfaces = len(QuArK_comps)
    skb.numBones = len(QuArK_bones)

    # Fill the needed data for exporting.
    message = skb.fill_skb_obj(file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder)

    #actually write it to disk
    skb.save(file)
    file.close()
    if logging == 1:
        skb.dump() # Writes the file Header last to the log for comparison reasons.

    return message


#########################################
# CALLS TO EXPORT MESH (.skb) and ANIMATION (.ska) FILE
#########################################
def export_SK_model(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
    if filename.endswith(".skb"): # Calls to write the .skb base mesh model file.
        message = save_skb(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder)
    else: # Calls to write the .ska animation file.
        message = save_ska(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder)

    return message


def savemodel(root, filename, gamename):
    #   Saves the model file: root is the actual file,
    #   filename is the full path and name of the .ska or .skb file selected,
    #   for example:  C:\FAKK2\fakk\models\animal\edencow\edencow_base.skb
    #   gamename is None.

    global editor, progressbar, tobj, logging, exportername, textlog, Strings, file_version, ModelFolder
    import quarkpy.qutils
    editor = quarkpy.mdleditor.mdleditor
    # Step 1 to import model from QuArK's Explorer.
    if editor is None:
        return

    # "sellist" is a list of one or more selected model components for exporting.
    sellist = editor.layout.explorer.sellist
    if not sellist:
        quarkx.msgbox("No Components have been selected for exporting.", MT_INFORMATION, MB_OK)
        return
    for item in sellist:
        if not item.name.endswith(":mc"):
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select\ncomponent folders for exporting.\n\nAn item that is not\na component folder\nis in your selections.\nDeselect it and try again.", MT_ERROR, MB_OK)
            return
        if item.dictitems['Frames:fg'].subitems[0].name != "baseframe:mf":
            quarkx.beep()
            quarkx.msgbox("MISSING or MISSPLACED MESH baseframe(s) !\n\nAll selected component's FIRST frame must be a static pose\nof that model's part and that frame named 'baseframe' !\n\nCorrect and try again.", MT_ERROR, MB_OK)
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
                    results = quarkx.msgbox("Number of selected component's frames do not match\nor some frames have identical names.\n\nDo you wish to continue with this export?", MT_INFORMATION, MB_YES|MB_NO)
                    if results != 6:
                        return
                    else:
                        break

    base_file = None # The full path and file name of the .skb file if we need to call to save it with.

    # model_path = two items in a list, the full path to the model folder, and the model file name, ex:
    # model_path = ['C:\\FAKK2\\fakk\\models\\animal\\edencow', 'base_cow.skb' or 'idle_moo.ska']
    model_path = filename.rsplit('\\', 1)
    ModelFolder = model_path[0].rsplit('\\', 1)[1]

    # The bone order in the ska file needs to match the ones in the skb file for Alice & FAKK2 models, EF2 uses bone names.
    QuArK_bones = []
    new_bones = []
    # Try to get needed bones by the folder name the model file is in.
    for group in editor.Root.dictitems['Skeleton:bg'].subitems:
        for comp in QuArK_comps:
            checkname = comp.shortname.split("_", 1)[0]
            if group.name.startswith(checkname + "_"):
                group_bones = group.findallsubitems("", ':bone') # Make a list of all bones in this group.
                skb_bones_indexes = {}
                for bone in group_bones:
                    if bone.dictspec.has_key('_skb_boneindex'):
                        skb_bones_indexes[int(bone.dictspec['_skb_boneindex'])] = bone
                    else:
                        new_bones.append(bone)
                skb_keys = skb_bones_indexes.keys()
                skb_keys.sort()
                for key in skb_keys:
                    QuArK_bones.append(skb_bones_indexes[key])
                ModelFolder = checkname
                break
    QuArK_bones = QuArK_bones + new_bones

    # Try to get needed bones by the model file name.
    if len(QuArK_bones) == 0:
        files = os.listdir(model_path[0])
        foundbones = 0
        for file in files:
            name = file.rsplit(".", 1)[0]
            for comp in QuArK_comps:
                if comp.shortname.startswith(name):
                    for group in editor.Root.dictitems['Skeleton:bg'].subitems:
                        if group.shortname.startswith(name):
                            ModelFolder = name
                            foundbones = 1
                            break
                if foundbones == 1:
                    break
            if foundbones == 1:
                break
        for group in editor.Root.dictitems['Skeleton:bg'].subitems:
            if group.name.startswith(ModelFolder + "_"):
                group_bones = group.findallsubitems("", ':bone') # Make a list of all bones in this group.
                skb_bones_indexes = {}
                for bone in group_bones:
                    if bone.dictspec.has_key('_skb_boneindex'):
                        skb_bones_indexes[int(bone.dictspec['_skb_boneindex'])] = bone
                    else:
                        new_bones.append(bone)
                skb_keys = skb_bones_indexes.keys()
                skb_keys.sort()
                for key in skb_keys:
                    QuArK_bones.append(skb_bones_indexes[key])
        QuArK_bones = QuArK_bones + new_bones

    if len(QuArK_bones) == 0:
        quarkx.beep() # Makes the computer "Beep" once.
        quarkx.msgbox("Could not export model.\nNo bones for a selected component exist.", MT_ERROR, MB_OK)
        return

    # A dictionary list by bones.name = (QuArK_bones)list_index to speed things up.
    ConvertBoneNameToIndex = {}
    for QuArK_bone_index in range(len(QuArK_bones)):
        QuArK_bone = QuArK_bones[QuArK_bone_index]
        ConvertBoneNameToIndex[QuArK_bone.name] = QuArK_bone_index

    choice = quarkx.msgbox("The file can be exported as either a\n    version 3 = for Alice or FAKK2 = Yes\nor\n    version 4 = for EF2 = No\n\nDo you wish version 3 for Alice or FAKK2 ?", MT_CONFIRMATION, MB_YES|MB_NO)
    if choice == 6:
        file_version = 3
    else:
        file_version = 4

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    if filename.endswith(".ska") or filename.endswith(".skb"):
        files = os.listdir(model_path[0])
        for file in files:
            if file.endswith(".skb"):
                base_file = model_path[0] + "\\" + file
                break
        if base_file is None:
            if filename.endswith(".ska"):
                quarkx.beep() # Makes the computer "Beep" once.
                choice = quarkx.msgbox(".skb base mesh file not found !\n\nDo you wish to have one created ?", MT_INFORMATION, MB_YES|MB_NO)
                if choice == 6:
                    base_file = filename.replace(".ska", ".skb")
                    message = export_SK_model(base_file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder) # Calls to save an .skb mesh file before the .ska animation file.
            message = export_SK_model(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder) # Calls to save a .skb mesh or .ska animation file only.
        else:
            message = export_SK_model(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder) # Calls to save a .skb mesh or .ska animation file only.

    try:
        progressbar.close()
    except:
        pass

    add_to_message = "Any used skin textures that are a\n.dds, .ftx, .tga, .png, .jpg or .bmp\nmay need to be copied to go with the model"
    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

    if message != "":
        quarkx.textbox("WARNING", "Missing Skin Texture Links:\r\n\r\n================================\r\n" + message, MT_WARNING)

### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".ska Alice\EF2\FAKK2 Exporter-anim", ".ska file", "*.ska", savemodel)
quarkpy.qmdlbase.RegisterMdlExporter(".skb Alice\EF2\FAKK2 Exporter-mesh", ".skb file", "*.skb", savemodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_skb_export.py,v $
# Revision 1.22  2013/02/20 05:19:41  cdunde
# Fix for sometimes incorrect skinsize being used.
#
# Revision 1.21  2012/01/13 07:50:21  cdunde
# Change to get away from relying on ModelFolder for exporting models.
#
# Revision 1.20  2012/01/09 23:09:54  cdunde
# Not all model formats process their vtx_offset the same.
#
# Revision 1.19  2012/01/08 21:55:52  cdunde
# Fix by DanielPharos for handling identical vertex_indexes with different U,V coords.
#
# Revision 1.18  2012/01/08 21:49:04  cdunde
# To enhance working with Quake4 md5 models.
#
# Revision 1.17  2012/01/06 05:35:44  cdunde
# Change for proper way to remove folder name from bones being exported.
#
# Revision 1.16  2012/01/04 21:25:30  cdunde
# Added check for needed baseframe.
#
# Revision 1.15  2012/01/03 00:24:16  cdunde
# To get Alice, FAKK2 & EF2 skb_exporter to work with Half-Life 1 HL1_importer models.
#
# Revision 1.14  2012/01/03 00:10:02  cdunde
# Rearranged export calls for better organization of code.
#
# Revision 1.13  2012/01/02 08:56:06  cdunde
# To stop writing skb file twice and speed up exporting of it.
#
# Revision 1.12  2011/12/26 21:55:34  cdunde
# To ensure proper 'baseframe:mf' selection.
#
# Revision 1.11  2011/12/25 02:29:16  cdunde
# Correction to avoid exporting bone baseframe data that is incorrect.
#
# Revision 1.10  2011/12/15 05:59:11  cdunde
# File cleanup and export vertex offsets for new bones and vertices.
#
# Revision 1.9  2011/12/12 23:05:31  cdunde
# Update to export mesh and animation files without use of original mesh file
# to setup for model full editing abilities, add & remove bones, faces & vertices
# and also work with original files if no editing is done.
#
# Revision 1.8  2011/11/15 05:07:07  cdunde
# Code added to enable adding bones & assigning existing vertices to it.
# Sill can not delete bones, vertices or triangles or
# add new vertices and triangles. Theses things need to be enabled
# to allow true editing of the models.
#
# Revision 1.7  2011/11/14 07:33:37  cdunde
# Removed unused code and fixed baseframe exporting error.
# Still needs more work, exporting mesh does not match original causing model to distort
# and can not add new bones or assign them vertices without causing export blowup.
#
# Revision 1.6  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.5  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.4  2010/08/27 19:36:15  cdunde
# To clarify menu item listing.
#
# Revision 1.3  2010/08/25 18:47:24  cdunde
# Small fix.
#
# Revision 1.2  2010/08/24 21:58:49  cdunde
# Final bone position fix for both skb and ska files, everything working correctly now.
#
# Revision 1.1  2010/08/22 05:11:16  cdunde
# Setup exporter for Alice, EF2 and FAKK2 .skb mesh and .ska animated models with bone and skin support.
#
#
