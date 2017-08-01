# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for MoHAA (.skc and .skd) animations and mesh model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_skd_export.py,v 1.14 2013/02/20 05:19:41 cdunde Exp $


Info = {
   "plug-in":       "ie_skd_exporter",
   "desc":          "This script exports MoHAA (.skc and .skd) animations and mesh model files.",
   "date":          "Nov. 19 2011",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 5" }

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
from quarkpy.qeditor import matrix_rot_x

# Globals
SS_MODEL = 3
logging = 0
exportername = "ie_skd_export.py"
textlog = "skc-skd_ie_log.txt"
editor = None
bonelist = None
progressbar = None
ModelFolder = None


######################################################
# SKC\SKD Model Constants
######################################################
SKC_MAX_CHANNEL_CHARS = 32
MAX_NAME = 32
MAX_PATH = 64
SKD_MAX_BONES = 128
SKD_MAX_FRAMES = 2048
SKD_MAX_SURFACES = 32
SKD_MAX_TRIANGLES = 8192
SKD_MAX_VERTICES = 4096

######################################################
# SKD data structures
######################################################
# A list of binary_formats to use based on a bone's jointType.
# Examples for type 0-4 from MOHAA models\animal\dog\german_shepherd.skd
# Examples for type 5-6 from MOHAA models\human\allied_airborne\airborne.skd
# typedef enum {   x = looks right         84 = number of SKD_Bone header in bytes.
# 0  JT_24BYTES1     = (ofsChannels) 108 - 84 (ofsValues) = 24/4bytes =  6f values, 3 = pos x,y,z, 3 = quat qx,qy,qz (see if bone.jointType == 0: section below for usage)
#                      bone values: (13.266192436218262, -0.0060352231375873089, 6.4365340222138911e-005, 1.0, 1.0, 1.0)
#                      bone channels: ('Bip01 Neck rot\x00',)
#                      bone refs: None
# 1  JT_POSROT_SKC   = (ofsChannels)  96 - 84 (ofsValues) = 12/4bytes =  3f values, 3 = quat qx,qy,qz (see elif bone.jointType == 1: section below for usage)
#                      bone values: (1.0, 1.0, 1.0)
#                      bone channels: ('Bip01 rot\x00Bip01 pos\x00',)
#                      bone refs: None
# 2? JT_40BYTES1     = (ofsChannels) 124 - 84 (ofsValues) = 40/4bytes = 10f values, 4 = quat qx,qy,qz,qw, 3 = pos x,y,z, 3 = quat qx,qy,qz (see elif bone.jointType == 2: section below for usage)
#                      bone values: (0.81796324253082275, 0.56404381990432739, -0.10230085998773575, -0.048220913857221603,
#                                    8.0932804848998785e-006, -3.153935722366441e-006, -5.1458311080932617, 1.0, 1.0, 1.0)
#                      bone channels: None
#                      bone refs: None
# 3  JT_24BYTES2     = (ofsChannels) 108 - 84 (ofsValues) = 24/4bytes =  6f values, + ofsRefs has another bone's name (not used at this time), channel has None, see example below:
#                      3 = pos x,y,z, 3 = quat qx,qy,qz (see elif bone.jointType == 3: section below for usage)
#                      bone values: (27.260543823242187, -1.0524528079258744e-005, -1.1960052688664291e-005, 1.0, 1.0, 1.0)
#                      bone channels: None
#                      bone refs: ('Bip01 R Thigh\x00',)
# 4  JT_24BYTES3   x = (ofsChannels) 108 - 84 (ofsValues) = 24/4bytes = 6f values, + ofsRefs has another bone's name (not used at this time)
#                      3 = pos x,y,z, 3 = quat qx,qy,qz (see elif bone.jointType == 4: section below for usage)
#                      bone values: (16.437829971313477, -2.24210293708893e-006, 1.8269793145009317e-006, 1.0, 1.0, 1.0)
#                      bone channels: ('Bip01 R Foot rot\x00Bip01 R Foot pos\x00',)
#                      bone refs: ('Bip01 R Thigh\x00',)
# 5 JT_40BYTES2     = (ofsChannels) 124 - 84 (ofsValues) = 40/4bytes = 10f values,, + ofsRefs has another bone's name (used to replace bone's rotmatrix)
#                      3 = jointWeight, Degrees?, unknown, 3 = pos x,y,z, 3 = quat qx,qy,qz, 1 = believe qw (see elif bone.jointType == 5: section below for usage)
#                      bone values: (1.0, 180.0, 0.54000002145767212, 14.681717872619629, -1.238970810391038e-007, -1.0011821359512396e-005,
#                                    1.0, 1.0, 1.0, 0.0)
#                      bone channels: None
#                      bone refs: ('Bip01 L UpperArm\x00',)
# 6  JT_28BYTES      = (ofsChannels) 112 - 84 (ofsValues) = 28/4bytes =  7f values, 1 = jointWeight, 3 = pos x,y,z, 3 = quat qx,qy,qz (see elif bone.jointType == 6: section below for usage)
#                      bone values: (0.5, 8.7047643661499023, -0.76852285861968994, -0.13475938141345978, 1.0, 1.0, 1.0)
#                      bone channels: None
#                      bone refs: ('helper Lshoulder\x00Bip01 L UpperArm\x00',) 1st & 2nd bone rot values appear to be the same, but if 1st does not exist use 2nd, we do anyway.
# } skdJointType_t;
skdJointType = [
    "<3f3f",
    "<3f",
    "<4f3f3f",
    "<3f3f",
    "<3f3f",
    "<3f3f3ff",
    "<1f3f3f"
]


class SKD_Bone:
    #Header Structure      #item of data file, size & type,   description.
    name = ""              #item   0-31   32 char, the bone's name.
    parent = ""            #item   32-63  32 char, the bone's parent name.
    jointType = 0          #item   64     1 signed short int, see skdJointType list description above.
    ofsValues = 0          #item   65     1 signed short int, constant = number of SKD_Bone header in bytes.
    ofsChannels = 0        #item   66     1 signed short int, ofsValues + skdJointType in bytes (6 floats for type 0).
    ofsRefs = 0            #item   67     1 signed short int, ofsChannels + the bone's name, 1 byte per letter + 5 bytes for ' rot\x00' including the blank space for type 0.
    ofsEnd = 0             #item   68     1 signed short int. usually the same as ofsRefs for type 0.

    basepos = [0.0]*3      # For QuArK Exporter use only.
    basequat = [1.0]*4     # For QuArK Exporter use only.
    channels = "None"      # For QuArK Exporter use only.
    refs = "None"          # For QuArK Exporter use only.
    parent_index = -1      # For QuArK Exporter use only.
    jointWeight = [1.,180.,1.]  # For QuArK Exporter use only.

    binary_format="<%ds%ds5i" % (MAX_NAME, MAX_NAME) #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.name = ""
        self.parent = ""
        self.jointType = 0
        self.ofsValues = 84
        self.ofsChannels = 108
        self.ofsRefs = 0
        self.ofsEnd = 0

        self.basepos = [0.0]*3
        self.basequat = [1.0]*4
        self.channels = "None"
        self.refs = "None"
        self.parent_index = -1
        self.jointWeight = [1.,180.,1.]

    def fill(self, bone, ConvertBoneNameToIndex, ModelFolder):
        self.name = bone.shortname.replace(ModelFolder + "_", "", 1)
        if bone.dictspec['parent_name'] == "None":
            self.parent = "worldbone"
        else:
            parent_name = bone.dictspec['parent_name']
            self.parent_index = ConvertBoneNameToIndex[parent_name]
            parent_name = parent_name.split(":bone")[0]
            parent_name = parent_name.replace(ModelFolder + "_", "", 1)
            self.parent = parent_name

        if bonelist.has_key(bone.name) and bonelist[bone.name]['frames'].has_key('baseframe:mf') and bonelist[bone.name]['frames']['baseframe:mf'].has_key('SKD_JointType'):
            self.jointType = bonelist[bone.name]['frames']['baseframe:mf']['SKD_JointType']
            if bonelist[bone.name]['frames']['baseframe:mf'].has_key('SKD_jointWeight'):
                self.jointWeight[0] = bonelist[bone.name]['frames']['baseframe:mf']['SKD_jointWeight']
            if bonelist[bone.name]['frames']['baseframe:mf'].has_key('SKD_JointChannels'):
                if bonelist[bone.name]['frames']['baseframe:mf']['SKD_JointChannels'] != "None":
                    self.channels = bonelist[bone.name]['frames']['baseframe:mf']['SKD_JointChannels'][0]
            if bonelist[bone.name]['frames']['baseframe:mf'].has_key('SKD_JointRefs'):
                self.refs = ""
                for bone_ref in bonelist[bone.name]['frames']['baseframe:mf']['SKD_JointRefs']:
                    bone_ref = bone_ref.replace(ModelFolder + "_", "", 1)
                    bone_ref = bone_ref.replace(":bone", "") + "\x00"
                    self.refs += bone_ref
        else:
            self.channels = self.name + ' rot\x00'

        self.ofsChannels = self.ofsValues + struct.calcsize(skdJointType[self.jointType])
        countfix = self.channels.replace('\x00', ',')
        self.ofsEnd = self.ofsRefs = self.ofsChannels + len(countfix)

        if self.refs != "None":
            countfix = self.refs.replace('\x00', ',')
            self.ofsEnd = self.ofsRefs + len(countfix)

    def save(self, file):
        tmpData = [0]*7
        tmpData[0] = self.name
        tmpData[1] = self.parent
        tmpData[2] = self.jointType
        tmpData[3] = self.ofsValues
        tmpData[4] = self.ofsChannels
        tmpData[5] = self.ofsRefs
        tmpData[6] = self.ofsEnd
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6])
        file.write(data)

        tmpData = [0]*10
        tmpData[0] = self.basepos[0]
        tmpData[1] = self.basepos[1]
        tmpData[2] = self.basepos[2]
        tmpData[3] = self.basequat[0]
        tmpData[4] = self.basequat[1]
        tmpData[5] = self.basequat[2]
        tmpData[6] = self.basequat[3]
        tmpData[7] = self.jointWeight[0]
        tmpData[8] = self.jointWeight[1]
        tmpData[9] = self.jointWeight[2]
        binary_format = skdJointType[self.jointType]
        if self.jointType == 0 or self.jointType == 3 or self.jointType == 4:
            data = struct.pack(binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5])
        elif self.jointType == 1:
            data = struct.pack(binary_format, tmpData[3], tmpData[4], tmpData[5])
        elif self.jointType == 2:
            data = struct.pack(binary_format, tmpData[3], tmpData[4], tmpData[5], -tmpData[6], tmpData[0], tmpData[1], tmpData[2], 1.0, 1.0, 1.0)
        elif self.jointType == 5:
            data = struct.pack(binary_format, tmpData[7], tmpData[8], tmpData[9], tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6])
        elif self.jointType == 6:
            data = struct.pack(binary_format, tmpData[7], tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5])
        file.write(data)

        tmpData = [0]
        tmpData[0] = self.channels
        countfix = self.channels.replace('\x00', ',')
        binary_format="<%ds" % (len(countfix))
        data = struct.pack(binary_format, tmpData[0])
        file.write(data)

        if self.refs != "None":
            tmpData = [0]
            tmpData[0] = self.refs
            countfix = self.refs.replace('\x00', ',')
            binary_format="<%ds" % (len(countfix))
            data = struct.pack(binary_format, tmpData[0])
            file.write(data)

    def dump(self):
        tobj.logcon ("bone name: " + str(self.name))
        tobj.logcon ("bone parent: " + str(self.parent))
        tobj.logcon ("bone jointType: " + str(self.jointType))
        tobj.logcon ("bone ofsValues: " + str(self.ofsValues))
        tobj.logcon ("bone ofsChannels: " + str(self.ofsChannels))
        tobj.logcon ("bone ofsRefs: " + str(self.ofsRefs))
        tobj.logcon ("bone ofsEnd: " + str(self.ofsEnd))
        tobj.logcon ("bone basepos: " + str(self.basepos))
        tobj.logcon ("bone basequat: " + str(self.basequat))
        tobj.logcon ("bone channels: " + str(self.channels))
        if self.refs != "None":
            tobj.logcon ("bone refs: " + str(self.refs))
        tobj.logcon ("bone jointWeight: " + str(self.jointWeight))
        tobj.logcon ("")


class SKD_Surface:
    # ident = 541870931 = "SKL "
    #Header Structure    #item of data file, size & type,   description.
    ident = "SKL "       #item   0    int but written as 4s string to convert to alpha, used to identify the file (see above).
    name = ""            #item   1    1-64 64 char, the surface (mesh) name.
    numTriangles = 0     #item  65    int, number of triangles.
    numVerts = 0         #item  66    int, number of verts.
    StaticSurfProc = 0   #item  67    int, unknown.
    ofsTriangles = 0     #item  68    int, offset for triangle 3 vert_index data.
    ofsVerts = 0         #item  69    int, offset for VERTICES data.
    ofsCollapseMap = 0   #item  70    int, offset where Collapse Map begins, NumVerts * int.
    ofsEnd = 0           #item  71    int, next Surface data follows ex: (header) ofsSurfaces + (1st surf) ofsEnd = 2nd surface offset.
    ofsCollapseIndex = 0 #item  72    int, unknown.llows ex: (header) ofsSurfaces + (1st surf) ofsEnd = 2nd surface offset.

    Triangles = []
    Vert_coords = {}
    CollapseMapVerts = []

    binary_format="<4s%ds8i" % MAX_PATH #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.ident = "SKL "
        self.name = ""
        self.numTriangles = 0
        self.numVerts = 0
        self.StaticSurfProc = 0
        self.ofsTriangles = 0
        self.ofsVerts = 0
        self.ofsCollapseMap = 0
        self.ofsEnd = 0
        self.ofsCollapseIndex = 0

        self.Triangles = []
        self.Vert_coords = []
        self.CollapseMapVerts = []

    def fill(self, Component, skd_bones, QuArK_bones, ConvertBoneNameToIndex):
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
            tri = SKD_Triangle()
            Ctri = Tris[i]
            new_Ctri = []
            if logging == 1:
                tobj.logcon ("tri " + str(i) + " " + str(tri.indices))
            for j in xrange(3):
                vert_index = Ctri[j][0]
                vert_coord = SKD_Vertex()
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
        for i in xrange(0, self.numVerts):
            verts_pointer = verts_pointer + (7 * 4) # Count for (see class SKD_Vertex).
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
            verts_pointer = verts_pointer + (vert.num_weights * (5 * 4)) # binary_format = "<if3f" or 5 items @ 4 bytes ea.

            vtx_pos = vertices[old_vert_index]

            for j in xrange(0, vert.num_weights):
                boneIndex = ConvertBoneNameToIndex[bonenames[j]]
                weight_value = vert_weights[bonenames[j]]['weight_value']
                Bpos = quarkx.vect(bonelist[bonenames[j]]['frames']['baseframe:mf']['position'])
                Brot = quarkx.matrix(bonelist[bonenames[j]]['frames']['baseframe:mf']['rotmatrix'])
                try:
                    vtx_offset = vert_weights[bonenames[j]]['vtx_offset']
                except:
                    QuArK_bone = QuArK_bones[boneIndex]
                    if vert.num_weights == 1:
                        # For HL1
                        if QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'HL1':
                            vtx_offset = (~Brot * (vtx_pos-Bpos)).tuple
                        # For MD5
                        elif QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'md5':
                            vtx_offset = (~Brot * (vtx_pos-Bpos)).tuple
                        else:
                            vtx_offset = (vtx_pos - Bpos).tuple
                    else:
                        try:
                            bone = skd_bones[boneIndex]
                            bone_jointType = bonelist[bonenames[j]]['frames']['baseframe:mf']['SKD_JointType']
                            parent_bone_jointType = bonelist[QuArK_bones[bone.parent_index].name]['frames']['baseframe:mf']['SKD_JointType']
                            if (bone_jointType == 2) or (bone_jointType == 3) or (bone_jointType == 4) or (parent_bone_jointType == 2) or (parent_bone_jointType == 3) or (parent_bone_jointType == 4):
                                vtx_offset = (~Brot * (vtx_pos-Bpos)).tuple
                            else:
                                vtx_offset = (vtx_pos - Bpos).tuple
                        except:
                            # For HL1, but never uses this because it does not split weights.
                            if QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'HL1':
                                vtx_offset = (~Brot * (vtx_pos-Bpos)).tuple
                            # For MD5
                            elif QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'md5':
                                vtx_offset = (~Brot * (vtx_pos-Bpos)).tuple
                            else:
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
        self.ofsCollapseMap = self.ofsVerts + verts_pointer
        self.ofsCollapseIndex = self.ofsCollapseMap + (self.numVerts * 4)
      #  self.ofsEnd = self.ofsCollapseIndex + (self.numVerts * 4) # NOT being exported at this time.
        self.ofsEnd = self.ofsCollapseIndex

    def save(self, file):
        # Write this surface (Component's) header.
        tmpData = [0]*10
        tmpData[0] = self.ident
        tmpData[1] = self.name
        tmpData[2] = self.numTriangles
        tmpData[3] = self.numVerts
        tmpData[4] = self.StaticSurfProc
        tmpData[5] = self.ofsTriangles
        tmpData[6] = self.ofsVerts
        tmpData[7] = self.ofsCollapseMap
        tmpData[8] = self.ofsEnd
        tmpData[9] = self.ofsCollapseIndex
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9])
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
        tobj.logcon ("numVerts: " + str(self.numVerts))
        tobj.logcon ("StaticSurfProc: " + str(self.StaticSurfProc))
        tobj.logcon ("ofsTriangles: " + str(self.ofsTriangles))
        tobj.logcon ("ofsVerts: " + str(self.ofsVerts))
        tobj.logcon ("ofsCollapseMap: " + str(self.ofsCollapseMap))
        tobj.logcon ("ofsEnd: " + str(self.ofsEnd))
        tobj.logcon ("ofsCollapseIndex: " + str(self.ofsCollapseIndex))


class SKD_Vertex:
    #Data Structure    # item of data file, size & type,   description.
    normal = [0]*3     # item   0-2    3 floats, a vertex's x,y,z normal values.
    uv = [0]*2         # item   3-4    2 floats, a vertex's U,V values.
    num_weights = 1    # item   5      1 int, number of weights the current vertex has, 1 weight = assigned amount to a single bone.
                       #                    numWeights[i] = SKD_Weight()
    numMorphs = 0      # item   6      int, number of morphs the current vertex has, these control mouth movement for speech.
                       #                    numMorphs[i] = SKD_Morph()

    binary_format="<3f2f2i" #little-endian (<), (see above)
    
    weights = {}

    def __init__(self):
        self.normal = [0]*3
        self.uv = [0]*2
        self.num_weights = 1
        self.numMorphs = 0

        self.weights = {}

    def fill(self, Ctri, skinsize):
        self.uv = [float(Ctri[1]/skinsize[0]), float(Ctri[2]/skinsize[1])]

    def save_vert(self, file):
        tmpData = [0]*7
        tmpData[0] = self.normal[0]
        tmpData[1] = self.normal[1]
        tmpData[2] = self.normal[2]
        tmpData[3] = self.uv[0]
        tmpData[4] = self.uv[1]
        tmpData[5] = self.num_weights
        tmpData[6] = self.numMorphs
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6])
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


class SKD_Morph:
    #Data Structure    # item of data file, size & type,   description.
    index = 0          # item   0    int.
    pos = (0)*3        # item   1-3  3 floats, morph's position.

    binary_format="<i3f" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.index = 0
        self.pos = (0.0)*3

    def fill(self, index, pos):
        self.index = index
        self.pos = (pos[0], pos[1], pos[2])

    def save(self, file):
        tmpData = [0]*4
        tmpData[0] = self.index
        tmpData[1] = self.pos[0]
        tmpData[2] = self.pos[1]
        tmpData[3] = self.pos[2]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
        file.write(data)


class SKD_HitBox:
    #Data Structure    # item of data file, size & type,   description.
    boneIndex = 0      # item   0    int.

    binary_format="<i" #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.boneIndex = 0

    def fill(self, bone_index):
        self.boneIndex = bone_index

    def save(self, file):
        tmpData = [0]
        tmpData[0] = self.boneIndex
        data = struct.pack(self.binary_format, tmpData[0])
        file.write(data)


class SKD_Triangle:
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


class skd_obj:
    file_pointer = 0
    header_size = 0

    # SKD ident = "SKMD" version = 5 MOHAA.
    #Header Structure    #item of data file, size & type,   description.
    ident = "SKMD"       #item   0    int but written as 4s string to convert to alpha, used to identify the file (see above).
    version = 5          #item   1    int, version number of the file (see above).
                         #### Items below filled in after version is determined.
    name = ""            #item   0    0-63 64 char, the models full name without its path.
    numSurfaces = 0      #item  64    int, number of mesh surfaces.
    numBones = 0         #item  65    int, number of bones.
    ofsBones = 0         #item  66    int, the file offset for the bone names data.
    ofsSurfaces = 0      #item  67    int, the file offset for the surface (mesh) data (for the 1st surface).
    ofsEnd = 0           #item  68    int, end (or length) of the file.
                         #                 Each level of detail (LODs) has completely separate sets of surfaces.
    numLODs = 0          #item  69    int, number of LODs (Low Object Display), low poly model viewed at distance.
    ofsLODs = 0          #item  70    int, offset to LOD data.
    lodIndex = 0         #item  71    int, LOD Index. [8]?
    numBoxes = 0         #item  72    int, number of Hit Boxes.
    ofsBoxes = 0         #item  73    int, number of Morphs.
    numMorphTargets = 0  #item  74    int, number of Morphs.
    ofsMorphTargets = 0  #item  75    int, offset to Morph data.

    binary_format="<4si%ds12i" % MAX_PATH  #little-endian (<), see #item descriptions above.

    #skd data objects
    surfaceList = []
    bones = [] # To put our exporting bones into.

    def __init__(self):
        self.file_pointer = 0
        self.header_size = (14 * 4) + 64

        self.ident = "SKMD"
        self.version = 5
        self.name = ""
        self.numSurfaces = 0
        self.numBones = 0
        self.ofsBones = 0
        self.ofsSurfaces = 0
        self.ofsEnd = 0
        self.numLODs = 0
        self.ofsLODs = 0
        self.lodIndex = 0 # lodIndex[8]
        self.numBoxes = 0
        self.ofsBoxes = 0
        self.numMorphTargets = 0
        self.ofsMorphTargets = 0

        self.surfaceList = []
        self.bones = []

    def save(self, file):
        # Write the header.
        tmpData = [0]*15
        tmpData[0] = self.ident
        tmpData[1] = self.version
        tmpData[2] = self.name
        tmpData[3] = self.numSurfaces
        tmpData[4] = self.numBones
        tmpData[5] = self.ofsBones
        tmpData[6] = self.ofsSurfaces
        tmpData[7] = self.ofsEnd
        tmpData[8] = self.numLODs
        tmpData[9] = self.ofsLODs
        tmpData[10] = self.lodIndex
        tmpData[11] = self.numBoxes
        tmpData[12] = self.ofsBoxes
        tmpData[13] = self.numMorphTargets
        tmpData[14] = self.ofsMorphTargets
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12], tmpData[13], tmpData[14])
        file.write(data)

        # Write the bones.
        for bone in self.bones:
            bone.save(file)

        # Write the surfaces.
        for surface in self.surfaceList:
            surface.save(file)

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
            tobj.logcon ("offset for end (or length) of file: " + str(self.ofsEnd))
            tobj.logcon ("number of LODs: " + str(self.numLODs))
            tobj.logcon ("offset for LODs: " + str(self.ofsLODs))
            tobj.logcon ("lodIndex: " + str(self.lodIndex))
            tobj.logcon ("number of Boxes: " + str(self.numBoxes))
            tobj.logcon ("offset for Box data: " + str(self.ofsBoxes))
            tobj.logcon ("number of Morph Targets: " + str(self.numMorphTargets))
            tobj.logcon ("offset for Morph Targets data: " + str(self.ofsMorphTargets))
            tobj.logcon ("")


######################################################
# FILL SKD OBJ DATA STRUCTURE
######################################################
    def fill_skd_obj(self, file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
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
        Bones_size = 0
        for i in xrange(0, self.numBones):
            bone = SKD_Bone()
            QuArK_bone = QuArK_bones[i]
            bone.fill(QuArK_bone, ConvertBoneNameToIndex, ModelFolder)
            QuArK_bone_name = QuArK_bone.name
            # Use bonelist for mesh baseframe exporting and NOT the bones themselves.
            # If another frame is current the bones contain those positions and matrixes.
            if bone.parent_index != -1:
                QuArK_parent_name = QuArK_bones[bone.parent_index].name
                if QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'skd-MOHAA':
                    parent_pos = quarkx.vect(bonelist[QuArK_parent_name]['frames']['baseframe:mf']['position'])
                    bone_pos1 = quarkx.vect(bonelist[QuArK_bone_name]['frames']['baseframe:mf']['position'])
                    bone.basepos = (bone_pos1 - parent_pos).tuple
                    parent_rot = quarkx.matrix(bonelist[QuArK_parent_name]['frames']['baseframe:mf']['rotmatrix'])
                    bone_rot1 = quarkx.matrix(bonelist[QuArK_bone_name]['frames']['baseframe:mf']['rotmatrix'])
                    bone_rot = (~parent_rot * bone_rot1).tuple
                else: # Handles other model format bones.
                    # For HL1
                    if QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'HL1':
                        parent_pos = quarkx.vect(bonelist[QuArK_parent_name]['frames']['baseframe:mf']['position'])
                        bone_pos1 = quarkx.vect(bonelist[QuArK_bone_name]['frames']['baseframe:mf']['position'])
                        parent_rot = quarkx.matrix(bonelist[QuArK_parent_name]['frames']['baseframe:mf']['rotmatrix'])
                        bone.basepos = (~parent_rot * (bone_pos1 - parent_pos)).tuple
                    # For Alice & FAKK2
                    elif QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'skb-Alice':
                        parent_pos = quarkx.vect(bonelist[QuArK_parent_name]['frames']['baseframe:mf']['position'])
                        bone_pos1 = quarkx.vect(bonelist[QuArK_bone_name]['frames']['baseframe:mf']['position'])
                        bone.basepos = (bone_pos1 - parent_pos).tuple
                    # For EF2
                    elif QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'skb-EF2':
                        bone.basepos = bonelist[QuArK_bone_name]['frames']['baseframe:mf']['position']
                    # For MD5
                    elif QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'md5':
                        parent_pos = quarkx.vect(bonelist[QuArK_parent_name]['frames']['baseframe:mf']['position'])
                        bone_pos1 = quarkx.vect(bonelist[QuArK_bone_name]['frames']['baseframe:mf']['position'])
                        parent_rot = quarkx.matrix(bonelist[QuArK_parent_name]['frames']['baseframe:mf']['rotmatrix'])
                        bone.basepos = (~parent_rot * (bone_pos1 - parent_pos)).tuple
                    bone_rot = bonelist[QuArK_bone_name]['frames']['baseframe:mf']['rotmatrix']
                bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                # For HL1
                if QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'HL1':
                   bone_rot = quarkx.matrix(bonelist[QuArK_bone_name]['frames']['baseframe:mf']['rotmatrix'])
                   m = (~bone_rot * parent_rot).tuple
                   bone_rot = ((m[0][0], m[0][1], m[0][2], 0.0) ,(m[1][0], m[1][1], m[1][2], 0.0), (m[2][0], m[2][1], m[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                # For MD5
                elif QuArK_bone.dictspec.has_key('type') and QuArK_bone.dictspec['type'] == 'md5':
                    bone_rot = quarkx.matrix(bonelist[QuArK_bone_name]['frames']['baseframe:mf']['rotmatrix'])
                    m = (~bone_rot * parent_rot).tuple
                    bone_rot = ((m[0][0], m[1][0], m[2][0], 0.0) ,(m[0][1], m[1][1], m[2][1], 0.0), (m[0][2], m[1][2], m[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                bone_quat = matrix2quaternion(bone_rot)

                if bone_quat[0] == 0 and bone_quat[1] == 0 and bone_quat[2] == 0:
                    bone_quat = (1.0, 1.0, 1.0, 1.0)
                if (bone.jointType == 3) or (bone.jointType == 4) or (self.bones[bone.parent_index].jointType == 3) or (self.bones[bone.parent_index].jointType == 4):
                    bone_quat = (1.0, 1.0, 1.0, 1.0)
                    bone.basepos = (~parent_rot * (bone_pos1 - parent_pos)).tuple
                if (bone.jointType == 5) or (bone.jointType == 6):
                    if QuArK_bone_name.find("helper") == -1:
                        if bonelist[QuArK_bone_name]['frames']['baseframe:mf'].has_key('SKD_JointRefs'):
                            bone_refs = bonelist[QuArK_bone_name]['frames']['baseframe:mf']['SKD_JointRefs']
                        else:
                            bone_refs = None
                        if bone_refs is None:
                            bone_rot = parent_rot
                            bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                            bone_quat = matrix2quaternion(bone_rot).tuple
                        else:
                            for bone_ref in bone_refs:
                                bone_rot = bonelist[bone_ref]['frames']['baseframe:mf']['rotmatrix']
                                bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                                bone_quat = matrix2quaternion(bone_rot)
                    else:
                        if bonelist[QuArK_bone_name]['frames']['baseframe:mf'].has_key('SKD_JointRefs'):
                            bone_refs = bonelist[QuArK_bone_name]['frames']['baseframe:mf']['SKD_JointRefs']
                        else:
                            bone_refs = None
                        if bone_refs is not None:
                            for bone_ref in bone_refs:
                                ref_rot = quarkx.matrix(bonelist[bone_ref]['frames']['baseframe:mf']['rotmatrix'])
                                bone_rot = ref_rot * matrix_rot_x(-math.pi/2.0) * quarkx.matrix((-1,0,0), (0,0,1), (0,1,0))
                                bone_rot = bone_rot.tuple
                                bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                                bone_quat = matrix2quaternion(bone_rot)
                if (bone.jointType == 6):
                    bone_quat = (1.0, 1.0, 1.0, 1.0)
                    if (bone.jointType == 6 and QuArK_bone_name.find("Lelbow") == -1):
                        bone.basepos = (-bone.basepos[0], bone.basepos[1], -bone.basepos[2])
            else:
                bone.basepos = bonelist[QuArK_bone_name]['frames']['baseframe:mf']['position']
                bone_rot1 = bonelist[QuArK_bone_name]['frames']['baseframe:mf']['rotmatrix']
                bone_rot = ((bone_rot1[0][0], bone_rot1[0][1], bone_rot1[0][2], 0.0), (bone_rot1[1][0], bone_rot1[1][1], bone_rot1[1][2], 0.0), (bone_rot1[2][0], bone_rot1[2][1], bone_rot1[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                bone_quat = matrix2quaternion(bone_rot)

                if bone_quat[0] == 0 and bone_quat[1] == 0 and bone_quat[2] == 0:
                    bone_quat = (1.0, 1.0, 1.0, 1.0)
                if (bone.jointType == 5) or (bone.jointType == 6):
                    bone_quat = (1.0, 1.0, 1.0, 1.0)
                    if (bone.jointType == 6):
                        bone.basepos = (-bone.basepos[0], bone.basepos[1], -bone.basepos[2])
            bone.basequat = (bone_quat[0], bone_quat[1], bone_quat[2], bone_quat[3])

            Bones_size += bone.ofsEnd
            self.bones.append(bone)
            if logging == 1:
                tobj.logcon ("Bone " + str(i))
                bone.dump()
        self.file_pointer = self.ofsBones + Bones_size

        # Fill the surfaces (meshes) data.
        self.ofsSurfaces = self.file_pointer
        FullPathName = file.name.replace("\\", "/")
        FolderPath = FullPathName.rsplit("/", 1)
        ModelName = FolderPath[1].split(".")[0]
        use_count = None
        for i in xrange(0, self.numSurfaces):
            if logging == 1:
                tobj.logcon ("=====================")
                tobj.logcon ("PROCESSING SURFACE: " + str(i))
                tobj.logcon ("=====================")
                tobj.logcon ("")
            surface = SKD_Surface()
            Component = QuArK_comps[i]
            name = Component.shortname
            surf_name = None
            if name.find(ModelFolder + "_") and name.find(ModelName + "_"):
                surf_name = name.replace(ModelFolder + "_", "", 1)
                surf_name = surf_name.replace(ModelName + "_", "", 1)
            if surf_name is None:
                surf_name = name.split("_")
                surf_name = surf_name[len(surf_name)-1]
                if use_count is not None:
                    surf_name = surf_name + str(i+1)
                else:
                    for surf in self.surfaceList:
                        if surf.name == surf_name:
                            surf.name = surf.name + str(i)
                            surf_name = surf_name + str(i+1)
                            use_count = 1
            surface.name = surf_name
            surface.fill(Component, self.bones, QuArK_bones, ConvertBoneNameToIndex)
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("----------------")
                tobj.logcon ("Surface " + str(i) + " Header")
                tobj.logcon ("----------------")
                surface.dump()
                tobj.logcon ("")
            self.surfaceList.append(surface)
            self.file_pointer = self.file_pointer + surface.ofsEnd

        self.ofsEnd = self.file_pointer

        return message


######################################################
# SKC data structures
######################################################
class SKC_Bone_Channel:
    #Header Structure      #item of data file, size & type,   description.
    channels = ""          #item   0-31   32 char, the bone's channel text discription, if it's a pos or rot.

    binary_format="<%ds" % MAX_NAME #little-endian (<), see #item descriptions above.

    def __init__(self):
        self.channels = ""

    def save(self, file):
        tmpData = [0]
        tmpData[0] = self.channels
        data = struct.pack(self.binary_format, tmpData[0])
        file.write(data)


class SKC_Frame_Channel:
    #Header Structure       #item of data file, size & type,   description.
    values = (1.0)*4        #item   0    0-3   4 floats, a bone's rot, quat or rotFK (rotation Forward Kinematics) values.

    binary_format="<4f"     #little-endian (<), see items above.

    def __init__(self):
        self.values = (1.0)*4

    def save(self, file):
        tmpData = [0]*4
        tmpData[0] = self.values[0]
        tmpData[1] = self.values[1]
        tmpData[2] = self.values[2]
        tmpData[3] = self.values[3]
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
        file.write(data)

    def dump(self):
        tobj.logcon ("values: " + str(self.values))


class SKC_Frame:
    #Header Structure            #item of data file, size & type,   description.
    bounds = [[0.0]*3, [0.0]*3]  #item   0    0-5 6 floats, the frame's bboxMin and bboxMax.
    radius = 0.0                 #item   6    float, dist from origin to corner.
    delta = [0.0]*3              #item   7    7-9 3 floats.
    dummy1 = 0.0                 #item   10   float, unknown item.
    ofsChannelData = 0           #item   11   int.

    binary_format="<6ff3ffi"  #little-endian (<), see #item descriptions above.

    Channels = [] # To store the animation Channels in for processing the file.

    def __init__(self):
        self.bounds = [[0.0]*3, [0.0]*3]
        self.radius = 0.0
        self.delta = [0.0]*3
        self.dummy1 = 0.0
        self.ofsChannelData = 0

        self.Channels = []

    def fill(self, frame_name, bonelist, QuArK_bones, ConvertBoneNameToIndex):
        for i in xrange(0, len(QuArK_bones)):
            QuArK_bone = QuArK_bones[i]
            POSchannel = SKC_Frame_Channel()
            QUATchannel = SKC_Frame_Channel()

            if QuArK_bone.dictspec['parent_name'] != "None":
                parent_bone = QuArK_bones[ConvertBoneNameToIndex[QuArK_bones[i].dictspec['parent_name']]]
                parent_pos = quarkx.vect(bonelist[parent_bone.name]['frames'][frame_name]['position'])
                parent_rot = quarkx.matrix(bonelist[parent_bone.name]['frames'][frame_name]['rotmatrix'])

                bone_pos1 = quarkx.vect(bonelist[QuArK_bone.name]['frames'][frame_name]['position'])
                bone_rot = quarkx.matrix(bonelist[QuArK_bone.name]['frames'][frame_name]['rotmatrix'])
                m = (~bone_rot * parent_rot).tuple
                bone_rot = ((m[0][0], m[1][0], m[2][0], 0.0) ,(m[0][1], m[1][1], m[2][1], 0.0), (m[0][2], m[1][2], m[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                bone_quat = matrix2quaternion(bone_rot)
                bone_quat = (-bone_quat[0], -bone_quat[1], -bone_quat[2], bone_quat[3])

                if bonelist.has_key(QuArK_bone.name) and bonelist[QuArK_bone.name]['frames'].has_key('baseframe:mf') and bonelist[QuArK_bone.name]['frames']['baseframe:mf'].has_key('SKD_JointType'):
                    bone_jointType = bonelist[QuArK_bone.name]['frames']['baseframe:mf']['SKD_JointType']
                    if (bone_jointType == 2) or (bone_jointType == 3) or (bone_jointType == 4):
                        if (bone_jointType != 4):
                            bone_pos = (~parent_rot * (bone_pos1 - parent_pos)).tuple
                        else:
                            bone_pos = bone_pos1.tuple
                    else:
                        bone_pos = (~parent_rot * (bone_pos1 - parent_pos)).tuple

                    if (bone_jointType == 5) or (bone_jointType == 6):
                        if QuArK_bone.name.find("helper") == -1:
                            if bonelist[QuArK_bone.name]['frames']['baseframe:mf'].has_key('SKD_JointRefs'):
                                bone_refs = bonelist[QuArK_bone.name]['frames']['baseframe:mf']['SKD_JointRefs']
                            else:
                                bone_refs = None
                            if bone_refs is None:
                                bone_rot = parent_rot.tuple
                                bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                                bone_quat = matrix2quaternion(bone_rot).tuple
                            else:
                                for bone_ref in bone_refs:
                                    bone_rot = bonelist[bone_ref]['frames'][frame_name]['rotmatrix']
                                    bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                                    bone_quat = matrix2quaternion(bone_rot)
                        else:
                            if bonelist[QuArK_bone.name]['frames']['baseframe:mf'].has_key('SKD_JointRefs'):
                                bone_refs = bonelist[QuArK_bone.name]['frames']['baseframe:mf']['SKD_JointRefs']
                            else:
                                bone_refs = None
                            if bone_refs is not None:
                                for bone_ref in bone_refs:
                                    ref_rot = quarkx.matrix(bonelist[bone_ref]['frames'][frame_name]['rotmatrix'])
                                    bone_rot = ref_rot * matrix_rot_x(-math.pi/2.0) * quarkx.matrix((-1,0,0), (0,0,1), (0,1,0))
                                    bone_rot = bone_rot.tuple
                                    bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                                    bone_quat = matrix2quaternion(bone_rot)
                else: # Handles other model format bones.
                    bone_pos = (~parent_rot * (bone_pos1 - parent_pos)).tuple
            else:
                bone_pos = bonelist[QuArK_bone.name]['frames'][frame_name]['position']
                bone_rot = bonelist[QuArK_bone.name]['frames'][frame_name]['rotmatrix']
                bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
                bone_quat = matrix2quaternion(bone_rot)
                bone_quat = (-bone_quat[0], -bone_quat[1], -bone_quat[2], bone_quat[3])
                if bonelist.has_key(QuArK_bone.name) and bonelist[QuArK_bone.name]['frames'].has_key('baseframe:mf') and bonelist[QuArK_bone.name]['frames']['baseframe:mf'].has_key('SKD_JointType'):
                    bone_jointType = bonelist[QuArK_bone.name]['frames']['baseframe:mf']['SKD_JointType']

            POSchannel.values = (bone_pos[0], bone_pos[1], bone_pos[2], 0.0)
            self.Channels.append(POSchannel)
            QUATchannel.values = bone_quat
            self.Channels.append(QUATchannel)

            if logging == 1:
                tobj.logcon ("channel " + str(i))
                channel.dump()

    def save(self, file):
        tmpData = [0]*12
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
        tmpData[10] = self.dummy1
        tmpData[11] = self.ofsChannelData
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11])
        file.write(data)

    def dump(self):
        tobj.logcon ("bounds: " + str(self.bounds))
        tobj.logcon ("radius: " + str(self.radius))
        tobj.logcon ("delta: " + str(self.delta))
        tobj.logcon ("dummy1: " + str(self.dummy1))
        tobj.logcon ("ofsChannelData: " + str(self.ofsChannelData))


class skc_obj:
    # SKC ident = "SKAN" version = 13 MOHAA.
    #Header Structure    #item of data file, size & type,   description.
    ident = "SKAN"       #item  0    int but written as 4s string to convert to alpha, used to identify the file (see above).
    version = 13         #item  1    int, version number of the file (see above).
                         #### Items below filled in after version is determined.
    type = 0             #item  2    int, unknown.
    ofsEnd = 0           #item  3    int, offset for end of this skc data.
    frametime = 0        #item  4    float, the time duration for a single frame, FPS (frames per second).
    dummy1 = 0           #item  5    float, unknown.
    dummy2 = 0           #item  6    float, unknown.
    dummy3 = 0           #item  7    float, unknown.
    dummy4 = 0           #item  8    float, unknown.
    numChannels = 0      #item  9    int, number of Channels, varies per bone, each bone can have up to 3 channels (pos, rot and rotFK).
                                        # pos = x, y, z and w, w being unused.
                                        # rot = quaternion qx, qy, qz, qw values.
                                        # rotFK = rotation forward kinematics; no idea how this works.
    ofsChannels = 0      #item  10   int, offset of Channels data.
    numFrames = 0        #item  11   int, number of mesh animation frames.

    binary_format="<4s3if4f3i"  #little-endian (<), see #item descriptions above.

    #skc data objects
    frames = []
    Channels = []

    def __init__(self):
        self.ident = "SKAN"
        self.version = 13
        self.type = 0
        self.ofsEnd = 0
        self.frametime = 0.0500000007451
        self.dummy1 = 0
        self.dummy2 = 0
        self.dummy3 = 0
        self.dummy4 = 0
        self.numChannels = 0
        self.ofsChannels = 0
        self.numFrames = 0

        self.frames = []
        self.Channels = []

    def save(self, file):
        # Write the file header.
        tmpData = [0]*12
        tmpData[0] = self.ident
        tmpData[1] = self.version
        tmpData[2] = self.type
        tmpData[3] = self.ofsEnd
        tmpData[4] = self.frametime
        tmpData[5] = self.dummy1
        tmpData[6] = self.dummy2
        tmpData[7] = self.dummy3
        tmpData[8] = self.dummy4
        tmpData[9] = self.numChannels
        tmpData[10] = self.ofsChannels
        tmpData[11] = self.numFrames
        data = struct.pack(self.binary_format, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11])
        file.write(data)

        # Write the Frame's Headers.
        for frame in self.frames:
            frame.save(file)

        # Write the Frame's Channels.
        for frame in self.frames:
            for channel in frame.Channels:
                channel.save(file)

        # Write the Bone's Channels.
        for channel in self.Channels:
            channel.save(file)

    def fill_skc_obj(self, file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, QuArK_frame_names, ModelFolder):
        message = ""
        self.numChannels = len(QuArK_bones) * 2 # 2 for each bone, 1 for pos & 1 for quat values.
        # 48 = skc_obj header size & SKC_Frame size, 16 = SKC_Frame_Channel size.
        self.ofsChannels = 48 + (self.numFrames * 48) + ((self.numChannels * 16) * self.numFrames)
        self.ofsEnd = self.ofsChannels + (self.numChannels * 32) # 32 = MAX_NAME for each SKC_Bone_Channel size.

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

        #fill the Frames
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("============================")
            tobj.logcon ("PROCESSING FRAMES: ")
            tobj.logcon ("============================")
            tobj.logcon ("")
        frame_count = len(framesgroups[0].subitems)
        passed_count = 0
        for i in xrange(0, frame_count):
            frame = SKC_Frame()
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
            if frame_name.find("baseframe") != -1:
                continue
            frame.ofsChannelData = 48 + (self.numFrames * 48) + (passed_count * (self.numChannels * 16))
            passed_count += 1
            self.frames.append(frame)

            frame.fill(frame_name, bonelist, QuArK_bones, ConvertBoneNameToIndex)
            if logging == 1:
                tobj.logcon ("---------------------")
                tobj.logcon ("frame " + str(i))
                tobj.logcon ("---------------------")
                frame.dump()
                tobj.logcon ("=====================")
                tobj.logcon ("")

        for i in xrange(0, len(QuArK_bones)):
            name = QuArK_bones[i].shortname
            try:
                name = name.replace(ModelFolder + "_", "", 1)
            except:
                pass
            channel = SKC_Bone_Channel()
            channel.channels = name + ' pos\x00'
            self.Channels.append(channel)

            channel = SKC_Bone_Channel()
            try:
                bone_jointType = bonelist[QuArK_bones[i].name]['frames']['baseframe:mf']['SKD_JointType']
                if (bone_jointType == 2) or (bone_jointType == 3) or (bone_jointType == 4):
                    channel.channels = name + ' rotFK\x00'
                else:
                    channel.channels = name + ' rot\x00'
            except:
                channel.channels = name + ' rot\x00'
            self.Channels.append(channel)

        return message

    def dump(self):
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + self.ident)
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("type: " + str(self.type))
            tobj.logcon ("end of file: " + str(self.ofsEnd))
            tobj.logcon ("anim. FPS: " + str(self.frametime))
            tobj.logcon ("dummy1: " + str(self.dummy1))
            tobj.logcon ("dummy2: " + str(self.dummy2))
            tobj.logcon ("dummy3: " + str(self.dummy3))
            tobj.logcon ("dummy4: " + str(self.dummy4))
            tobj.logcon ("number of channels: " + str(self.numChannels))
            tobj.logcon ("channels data offset: " + str(self.ofsChannels))
            tobj.logcon ("number of frames: " + str(self.numFrames))
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
# CALL TO EXPORT ANIMATION (.skc) FILE
############################
# QuArK_bones = A list of all the bones in the QuArK's "Skeleton:bg" folder, in their proper tree-view order, to get our bones from.
def save_skc(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
    file = open(filename, "wb")
    skc = skc_obj() # Making an "instance" of this class.
  #  skc.name = filename.rsplit("\\", 1)[1] # Original files do not use this.
    # To filter out all baseframes.
    frames = QuArK_comps[0].dictitems['Frames:fg'].subitems
    QuArK_frame_names = []
    for frame in frames:
        if frame.name.find("baseframe") != -1:
            continue
        QuArK_frame_names.append(frame.name)
    skc.numFrames = len(QuArK_frame_names)

    # Fill the needed data for exporting.
    message = skc.fill_skc_obj(file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, QuArK_frame_names, ModelFolder) # Calling this class function to read the file data and create the animation frames.

    #actually write it to disk
    skc.save(file)
    file.close()
    if logging == 1:
        skc.dump() # Writes the file Header last to the log for comparison reasons.

    return message


############################
# CALL TO EXPORT MESH (.skd) FILE
############################
def save_skd(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
    file = open(filename, "wb")
    skd = skd_obj() # Making an "instance" of this class.
    skd.name = filename.rsplit("\\", 1)[1]
    skd.numSurfaces = len(QuArK_comps)
    skd.numBones = len(QuArK_bones)

    # Fill the needed data for exporting.
    message = skd.fill_skd_obj(file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder)

    #actually write it to disk
    skd.save(file)
    file.close()
    if logging == 1:
        skd.dump() # Writes the file Header last to the log for comparison reasons.

    return message


#########################################
# CALLS TO EXPORT MESH (.skd) and ANIMATION (.skc) FILE
#########################################
def export_SK_model(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder):
    if filename.endswith(".skd"): # Calls to write the .skd base mesh model file.
        message = save_skd(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder)
    else: # Calls to write the .skc animation file.
        message = save_skc(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder)

    return message


def savemodel(root, filename, gamename):
    #   Saves the model file: root is the actual file,
    #   filename is the full path and name of the .skc or .skd file selected,
    #   for example:  MOHAA\main\models\animal\dog\german_shepherd.skd
    #   gamename is None.

    global editor, progressbar, tobj, logging, exportername, textlog, Strings, ModelFolder, bonelist
    import quarkpy.qutils
    editor = quarkpy.mdleditor.mdleditor
    # Step 1 to import model from QuArK's Explorer.
    if editor is None:
        return

    #Get the QuArK's ModelComponentList['bonelist'].
    bonelist = editor.ModelComponentList['bonelist']

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

    base_file = None # The full path and file name of the .skd file if we need to call to save it with.

    # model_path = two items in a list, the full path to the model folder, and the model file name, ex:
    # model_path = ['C:\\MOHAA\\main\\models\\animal\\dog', 'german_shepherd.skd' or 'dog_run.skc']
    model_path = filename.rsplit('\\', 1)
    ModelFolder = model_path[0].rsplit('\\', 1)[1]

    # The bone order in the skc file needs to match the ones in the skd file for MOHAA models.
    QuArK_bones = []
    new_bones = []
    # Try to get needed bones by the folder name the model file is in.
    for group in editor.Root.dictitems['Skeleton:bg'].subitems:
        for comp in QuArK_comps:
            checkname = comp.shortname.split("_", 1)[0]
            if group.name.startswith(checkname + "_"):
                group_bones = group.findallsubitems("", ':bone') # Make a list of all bones in this group.
                skd_bones_indexes = {}
                for bone in group_bones:
                    if bone.dictspec.has_key('_skd_boneindex'):
                        skd_bones_indexes[int(bone.dictspec['_skd_boneindex'])] = bone
                    else:
                        new_bones.append(bone)
                skd_keys = skd_bones_indexes.keys()
                skd_keys.sort()
                for key in skd_keys:
                    QuArK_bones.append(skd_bones_indexes[key])
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
                skd_bones_indexes = {}
                for bone in group_bones:
                    if bone.dictspec.has_key('_skd_boneindex'):
                        skd_bones_indexes[int(bone.dictspec['_skd_boneindex'])] = bone
                    else:
                        new_bones.append(bone)
                skd_keys = skd_bones_indexes.keys()
                skd_keys.sort()
                for key in skd_keys:
                    QuArK_bones.append(skd_bones_indexes[key])
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

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    if filename.endswith(".skc") or filename.endswith(".skd"):
        files = os.listdir(model_path[0])
        for file in files:
            if file.endswith(".skd"):
                base_file = model_path[0] + "\\" + file
                break
        if base_file is None:
            if filename.endswith(".skc"):
                quarkx.beep() # Makes the computer "Beep" once.
                choice = quarkx.msgbox(".skd base mesh file not found !\n\nDo you wish to have one created ?", MT_INFORMATION, MB_YES|MB_NO)
                if choice == 6:
                    base_file = filename.replace(".skc", ".skd")
                    message = export_SK_model(base_file, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder) # Calls to save the .skd mesh file before the .skc animation file.
            message = export_SK_model(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder) # Calls to save a .skd mesh or .skc animation file only.
        else:
            message = export_SK_model(filename, QuArK_comps, QuArK_bones, ConvertBoneNameToIndex, ModelFolder) # Calls to save a .skd mesh or .skc animation file only.

    try:
        progressbar.close()
    except:
        pass

    add_to_message = "Any used skin textures that are a\n.dds, .tga or .jpg\nmay need to be copied to go with the model"
    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

    if message != "":
        quarkx.textbox("WARNING", "Missing Skin Texture Links:\r\n\r\n================================\r\n" + message, MT_WARNING)

### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".skc MOHAA Exporter-anim", ".skc file", "*.skc", savemodel)
quarkpy.qmdlbase.RegisterMdlExporter(".skd MOHAA Exporter-mesh", ".skd file", "*.skd", savemodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_skd_export.py,v $
# Revision 1.14  2013/02/20 05:19:41  cdunde
# Fix for sometimes incorrect skinsize being used.
#
# Revision 1.13  2012/01/13 07:50:21  cdunde
# Change to get away from relying on ModelFolder for exporting models.
#
# Revision 1.12  2012/01/09 07:29:37  cdunde
# To get MoHAA skd_exporter to work with Half-Life 1 HL1_importer models.
#
# Revision 1.11  2012/01/08 23:54:10  cdunde
# Fix by DanielPharos for handling identical vertex_indexes with different U,V coords.
#
# Revision 1.10  2012/01/07 02:09:42  cdunde
# To enhance working with Quake4 md5 models.
#
# Revision 1.9  2012/01/04 21:25:30  cdunde
# Added check for needed baseframe.
#
# Revision 1.8  2012/01/04 04:53:39  cdunde
# To get MoHAA skd_exporter to work with Doom3 & Quake4 md5_importer models.
#
# Revision 1.7  2012/01/03 00:14:09  cdunde
# Update to export mesh and animation files without use of original mesh file
# to setup for model full editing abilities, add & remove bones, faces & vertices
# and also work with original files if no editing is done.
#
# Revision 1.6  2012/01/02 04:00:36  cdunde
# Update to get MoHAA skd_exporter to work with Alice, FAKK2 & EF2 skb_importer models.
#
# Revision 1.5  2011/12/23 22:36:31  cdunde
# To get MoHAA skd_exporter to work with Alice, FAKK2 & EF2 skb_importer models.
#
# Revision 1.4  2011/12/16 08:52:26  cdunde
# To start getting the skb_import and skd_export working together, still needs work.
#
# Revision 1.3  2011/12/11 04:01:57  cdunde
# Completed support for skdJointType 5 & 6 anim.
# Fixed components exported without any skins.
#
# Revision 1.2  2011/12/10 02:43:22  cdunde
# Update & corrections for skdJointType 0-4, mesh & anim work perfect.
# Added support for skdJointType 5 & 6, mesh fine but anim needs work.
#
# Revision 1.1  2011/12/01 06:08:54  cdunde
# Added export support for MoHAA static and animation models .skd and .skc file types.
#
#
