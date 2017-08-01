"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for Doom 3 and Quake 4 .md5mesh and .md5anim model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md5_export.py,v 1.20 2012/01/30 03:37:25 cdunde Exp $

Info = {
   "plug-in":       "ie_md5_exporter",
   "desc":          "Export selected components to an .md5mesh (with bones) or .md5anim file.",
   "date":          "August 2 2009",
   "author":        "cdunde/DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 3" }

import time, math, os, os.path, struct, operator, sys as osSys, chunk
from math import *
import quarkx
import quarkpy.qmacro
from quarkpy.qutils import *
import quarkpy.mdleditor
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
logging = 0
exportername = "ie_md5_export.py"
textlog = "md5_ie_log.txt"


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
    #See: http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/index.htm
    s = math.sqrt(abs(m[0][0] + m[1][1] + m[2][2] + m[3][3]))
    if s < 0.001:
        if ((m[0][0] > m[1][1]) and (m[0][0] > m[2][2])):
            s = math.sqrt(m[3][3] + m[0][0] - m[1][1] - m[2][2]) * 2.0
            return quaternion_normalize([
            -0.25 * s,
            -(m[0][1] + m[1][0]) / s,
            -(m[0][2] + m[2][0]) / s,
            (m[2][1] - m[1][2]) / s,
            ])
        elif (m[1][1] > m[2][2]):
            s = math.sqrt(m[3][3] + m[1][1] - m[0][0] - m[2][2]) * 2.0
            return quaternion_normalize([
            -(m[0][1] + m[1][0]) / s,
            -0.25 * s,
            -(m[1][2] + m[2][1]) / s,
            (m[0][2] - m[2][0]) / s,
            ])
        else:
            s = math.sqrt(m[3][3] + m[2][2] - m[0][0] - m[1][1]) * 2.0
            return quaternion_normalize([
            -(m[0][2] + m[2][0]) / s,
            -(m[1][2] + m[2][1]) / s,
            -0.25 * s,
            (m[1][0] - m[0][1]) / s,
            ])
    return quaternion_normalize([
        -(m[2][1] - m[1][2]) / (2.0 * s),
        -(m[0][2] - m[2][0]) / (2.0 * s),
        -(m[1][0] - m[0][1]) / (2.0 * s),
        0.5 * s,
        ])

def quaternion_normalize(q):
    l = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
    return q[0] / l, q[1] / l, q[2] / l, q[3] / l

# This function takes a bone's matrix and inverses it
# for exportation of data that uses the matrix, such as weights, bm = bone matrix.
# Not being used in this file any more but should be saved and changed for individual bone call.
def inverse_matrix(self):
    self.bone_matrix_list = {}
    for bone in range(len(self.bones)):
        bm = []
        worklist = [[0,0,0],[0,0,0],[0,0,0]]
        try:
            bonematrix = self.editor.ModelComponentList['bonelist'][self.bones[bone].name]['bonematrix']
        except:
            bonematrix = self.bones[bone].rotmatrix.tuple
        bm = bonematrix
        worklist[0][0] = ((bm[1][1]*bm[2][2]) - (bm[1][2]*bm[2][1])) * 1
        worklist[0][1] = ((bm[1][0]*bm[2][2]) - (bm[1][2]*bm[2][0])) * -1
        worklist[0][2] = ((bm[1][0]*bm[2][1]) - (bm[1][1]*bm[2][0])) * 1

        worklist[1][0] = ((bm[0][1]*bm[2][2]) - (bm[0][2]*bm[2][1])) * -1
        worklist[1][1] = ((bm[0][0]*bm[2][2]) - (bm[0][2]*bm[2][0])) * 1
        worklist[1][2] = ((bm[0][0]*bm[2][1]) - (bm[0][1]*bm[2][0])) * -1

        worklist[2][0] = ((bm[0][1]*bm[1][2]) - (bm[0][2]*bm[1][1])) * 1
        worklist[2][1] = ((bm[0][0]*bm[1][2]) - (bm[0][2]*bm[1][0])) * -1
        worklist[2][2] = ((bm[0][0]*bm[1][1]) - (bm[0][1]*bm[1][0])) * 1

        bm[0][0] = worklist[0][0]
        bm[1][0] = worklist[0][1]
        bm[2][0] = worklist[0][2]

        bm[0][1] = worklist[1][0]
        bm[1][1] = worklist[1][1]
        bm[2][1] = worklist[1][2]

        bm[0][2] = worklist[2][0]
        bm[1][2] = worklist[2][1]
        bm[2][2] = worklist[2][2]

        self.bone_matrix_list[self.bones[bone].name] = bm

def vector_by_matrix(p, m):
    return [
        p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0],
        p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1],
        p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2]
       ]

def reverse_vector_by_matrix(p, m):
    return [
        p[0] / m[0][0] - p[1] / m[1][0] - p[2] / m[2][0],
        p[0] / m[0][1] - p[1] / m[1][1] - p[2] / m[2][1],
        p[0] / m[0][2] - p[1] / m[1][2] - p[2] / m[2][2]
       ]


######################################################
# WRITES MESH & ANIMATION SHADERS SECTION
######################################################
def write_shaders(filename, exp_list):
    shaders = []
    for comp in exp_list:
        if comp[0].dictspec.has_key('shader_name') and comp[0].dictspec['shader_name'] != "None" and not comp[0].dictspec['shader_name'] in shaders:
            if len(shaders) == 0:
                if filename.endswith(".md5mesh"):
                    shadername = filename.replace(".md5mesh", ".mtr")
                else:
                    shadername = filename.replace(".md5anim", ".mtr")
                shaderfile = open(shadername, "w")
            shaders = shaders + [comp[0].dictspec['shader_name']]
            shader = comp[0].dictspec['mesh_shader']
            shader = shader.replace("\r\n", "\n")
            shaderfile.write(shader)
    try:
        shaderfile.close()
    except:
        pass


######################################################
# SETUP SECTION
######################################################
def set_lists(exp_list, objects, worldTable):
    #exp_list = [component1, component2,...]
    for current_obj in objects:
        if current_obj.type == ':mc':
            exp_list.append(current_obj)

            # Sets the flag to export this component's shader file if there is one.
            if current_obj.dictspec.has_key('shader_file') and current_obj.dictspec['shader_file'] != "None":
                worldTable['mat_type'] = 1


######################################################
# WRITE EXPORT FILE HEADER SECTION
######################################################
def write_header(self, file, filename, component, worldTable):
    global user_frame_list, tobj

    # Get the component's Mesh.
    mesh = component.triangles

    file.write('MD5Version 10\n')
    path_name = filename.replace("\\", "/")
    path_name = "models/" + path_name.split("/models/")[1]
    path_shortname = path_name.rsplit("/", 1)
    path, shortname = path_shortname[0], path_shortname[1]
    shortname = shortname.split(".")[0]
    if self.src["makefolder"] is not None:
        path = path.rsplit("/", 1)[0]
    typepath = path.replace("/md5/", "/")
    if self.src['Doom3'] is not None:
        folder = "/cycles/"
        type = ".mb"
        game = "Doom"
    else:
        folder = "/anims/"
        type = ".ma"
        game = "Quake4"
    if filename.endswith(".md5mesh"):
        file.write('commandline "mesh %s%s%s%s -dest %s/%s.md5mesh -game %s"\n' % (typepath, folder, shortname, type, path, shortname, game))
    else:
        file.write('commandline "anim %s%s%s%s -dest %s/%s.md5anim -game %s"\n' % (typepath, folder, shortname, type, path, shortname, game))

    file.write('\n')


######################################################
# EXPORT MESH ONLY SECTION
######################################################
    # "exp_list" is a list of one or more selected model components for exporting.
def export_mesh(self, file, filename, exp_list):
    global tobj, Strings

    joints = self.bones
    fixed_comp_name = []
    for comp in exp_list:
        compname = comp.shortname.split("_", 1)
        foldername = compname[0]
        compname = compname[1]
        fixed_comp_name = fixed_comp_name + [(foldername, compname)]

    file.write('numJoints %i\n' % len(joints))
    file.write('numMeshes %i\n' % len(exp_list))
    file.write('\n')

    #Write the joints section
    file.write('joints {\n')
    joint_data = []
    temp_joint_data = None
    for current_joint in joints:
        if current_joint.dictspec.has_key('type') and current_joint.dictspec['type'] == 'skb-EF2' and temp_joint_data is None:
            temp_joint_data = {}
            bonelist = self.editor.ModelComponentList['bonelist']
            for joint in joints:
                bone_name = joint.name
                if joint.dictspec['parent_name'] == "None":
                    bone_data = bonelist[bone_name]['frames']['baseframe:mf']
                    temp_joint_data[bone_name] = [bone_data['position'], bone_data['rotmatrix']]
                else:
                    parent_name = joint.dictspec['parent_name']
                    bone_data = bonelist[bone_name]['frames']['baseframe:mf']
                    bone_pos = quarkx.vect(bone_data['position'])
                    tempmatrix = bone_data['rotmatrix']
                    bone_rot = quarkx.matrix((tempmatrix[0][0], tempmatrix[0][1], tempmatrix[0][2]), (tempmatrix[1][0], tempmatrix[1][1], tempmatrix[1][2]), (tempmatrix[2][0], tempmatrix[2][1], tempmatrix[2][2]))
                    parent_data = temp_joint_data[parent_name]
                    parent_pos = quarkx.vect(parent_data[0])
                    parent_rot = quarkx.matrix(parent_data[1])
                    bone_pos = ((parent_rot * bone_pos) + parent_pos).tuple
                    bone_rot = (parent_rot * bone_rot).tuple
                    temp_joint_data[bone_name] = [bone_pos, bone_rot]
        joint_name = current_joint.shortname.split("_", 1)[1]
        joint_name = joint_name.replace(" ", "_")
        parent_index = -1
        parent_bone_name = ""
        if current_joint.dictspec['parent_name'] != "None":
            for parent_bone in range(len(joints)):
                if current_joint.dictspec['parent_name'] == joints[parent_bone].name:
                    parent_index = parent_bone
                    parent_bone_name = joints[parent_bone].shortname.split("_", 1)[1]
                    break
        comp_name = current_joint['component']
        comp = None
        for test_comp in exp_list:
            if test_comp.name == comp_name:
                comp = test_comp
                break
        if comp is None:
            #Can't use this component; defaulting!
            comp = exp_list[0]
        baseframe = comp.dictitems['Frames:fg'].dictitems['baseframe:mf']
        if not self.editor.ModelComponentList['bonelist'].has_key(current_joint.name):
            # This bone has no vertexes assigned to it but could have a child bone for editing the model only.
            bone_pos = current_joint.position.tuple
            bone_rot = current_joint.rotmatrix.tuple
        else:
            bone_data = self.editor.ModelComponentList['bonelist'][current_joint.name]['frames'][baseframe.name]
            bone_pos = bone_data['position']
            bone_rot = bone_data['rotmatrix']
            if current_joint.dictspec.has_key('type') and current_joint.dictspec['type'] == 'skb-EF2':
                bone_data = temp_joint_data[current_joint.name]
                bone_pos = bone_data[0]
                bone_rot = bone_data[1]
        joint_data = joint_data + [(bone_pos, bone_rot)]
        bone_rot = ((bone_rot[0][0], bone_rot[0][1], bone_rot[0][2], 0.0), (bone_rot[1][0], bone_rot[1][1], bone_rot[1][2], 0.0), (bone_rot[2][0], bone_rot[2][1], bone_rot[2][2], 0.0), (0.0, 0.0, 0.0, 1.0))
        bone_rot = matrix2quaternion(bone_rot)
        bone_pos0 = ie_utils.NicePrintableFloat(bone_pos[0])
        bone_pos1 =  ie_utils.NicePrintableFloat(bone_pos[1])
        bone_pos2 =  ie_utils.NicePrintableFloat(bone_pos[2])
        bone_rot0 =  ie_utils.NicePrintableFloat(bone_rot[0])
        bone_rot1 =  ie_utils.NicePrintableFloat(bone_rot[1])
        bone_rot2 =  ie_utils.NicePrintableFloat(bone_rot[2])
        file.write('\t"%s"\t%i ( %s %s %s ) ( %s %s %s )\t\t// %s\n' % (joint_name, parent_index, bone_pos0, bone_pos1, bone_pos2, bone_rot0, bone_rot1, bone_rot2, parent_bone_name))
    file.write('}\n')
    file.write('\n')

    #Preparation: set-up a bone-name to bone-index convertion dict
    bone_name_to_index = {}
    for bone_index in range(len(joints)):
        bone_name_to_index[joints[bone_index].name] = bone_index


    for comp_index in range(len(exp_list)):
        comp = exp_list[comp_index]
        triangles = comp.triangles
        vertices = comp.dictitems['Frames:fg'].subitems[0].vertices
        texWidth, texHeight = comp.dictitems['Skins:sg'].subitems[0].dictspec['Size']

        #Split any vertex having multiple U,V coordinates into separate vertices
        UVs_of_vert = {}
        old_verts = [] #For quick saving of duplicate x,y,z + weights
        new_triangles = []
        new_vertices = []
        for i in xrange(0, len(triangles)):
            new_triangle = []
            for j in xrange(3):
                vert_index = triangles[i][j][0]
                vert_coord = [triangles[i][j][1] / texWidth, triangles[i][j][2] / texHeight]
                if UVs_of_vert.has_key(vert_index):
                    #We've seen this vert_index before
                    FoundAVert = 0
                    for k in xrange(len(UVs_of_vert[vert_index])):
                        UV = UVs_of_vert[vert_index][k]
                        if (abs(UV[0] - vert_coord[0]) < 0.001) and (abs(UV[1] - vert_coord[1]) < 0.001):
                            #Same UV; recycle vert
                            new_vert_index = UV[2]
                            FoundAVert = 1
                            break
                    if not FoundAVert:
                        #Same vert_index, but different UV: split it!
                        new_vert_index = len(old_verts)
                        old_verts += [vert_index]
                        UVs_of_vert[vert_index] += [(vert_coord[0], vert_coord[1], new_vert_index)]
                        new_vertices += [vertices[vert_index]]
                else:
                    #Totally new vert_index
                    new_vert_index = len(old_verts)
                    old_verts += [vert_index]
                    UVs_of_vert[vert_index] = [(vert_coord[0], vert_coord[1], new_vert_index)]
                    new_vertices += [vertices[vert_index]]
                new_triangle += [(new_vert_index, vert_coord[0], vert_coord[1])]
            new_triangles += [new_triangle]
        vertices = new_vertices
        triangles = new_triangles

        weightvtxlist = None
        if self.editor.ModelComponentList.has_key(comp.name) and self.editor.ModelComponentList[comp.name].has_key('weightvtxlist'):
            weightvtxlist = self.editor.ModelComponentList[comp.name]['weightvtxlist']

        # Starts the "mesh" section.
        file.write('mesh {\n')
        file.write('\t// meshes: %s\n' % fixed_comp_name[comp_index][1])

        if comp.dictspec.has_key('shader_name') and comp.dictspec['shader_name'] != "None":
            shader = comp.dictspec['shader_name']
        elif comp.dictitems['Skins:sg'].subitems[0].shortname.startswith("models/"):
            shader = comp.dictitems['Skins:sg'].subitems[0].shortname.rsplit("/", 1)[0] + "/" + comp.shortname
        elif self.exportpath.find("\\models\\") != -1:
            shader = self.exportpath.replace("\\", "/")
            if shader.find("/md5/") != -1:
                shader = shader.replace("/md5/", "/")
            if self.src["makefolder"] is not None:
                shader = shader.rsplit("/", 1)[0]
            shader = "models/" + shader.split("/models/")[1] + "/" + comp.shortname
        else:
            shader = comp.dictitems['Skins:sg'].subitems[0].shortname.rsplit("/", 1)[0] + "/" + comp.shortname
        file.write('\tshader "%s"\n' % shader)
        file.write('\n')

        self.mesh_vtx_errors = [] # For self.mesh_errors data output below.

        # Build the weights, and compute their proper index numbers
        #Note: The vert_index stored in weight_sets is only used in position calculations,
        #so even when that set of weights is being shared by multiple vertices,
        #all shared verts have the same position, it doesn't matter.
        HighestWeightIndex = -1
        weight_sets = []
        weights = []
        vert_blends = []
        for vert_index in range(len(vertices)):
            # Creates weight data for the "weight" section below.
            current_vertex = vertices[vert_index]
            old_vert_index = old_verts[vert_index]
            if weightvtxlist is not None and weightvtxlist.has_key(old_vert_index):
                blend_index = -1 #Calculated later
                blend_count = len(weightvtxlist[old_vert_index])
                
                #Create the weight_set for this vertex
                weight_set = []
                sorted_keys = weightvtxlist[old_vert_index].keys()
                #Sort on bone_index: (although not strictly speaking needed, it is nicer)
                sorted_keys = sorted(sorted_keys, key=lambda sort_me: bone_name_to_index[sort_me])
                for key in sorted_keys:
                    bone_index = bone_name_to_index[key]
                    weight_value = weightvtxlist[old_vert_index][key]['weight_value']
                    bone_pos = joint_data[bone_index][0]
                    bone_pos = quarkx.vect(bone_pos)
                    bone_rot = joint_data[bone_index][1]
                    bone_rot = quarkx.matrix(bone_rot)
                    # For Alice, FAKK2 or EF2 model being exported.
                    if joints[bone_index].dictspec.has_key('type') and joints[bone_index].dictspec['type'].startswith('skb-'):
                        weight_pos = quarkx.vect(weightvtxlist[old_vert_index][key]['vtx_offset'])
                     #1   vo = weightvtxlist[old_vert_index][key]['vtx_offset']
                     #1   br = bone_rot.tuple
                     #1   m = [[1,1,1]]*3
                     #1   for i in range(3):
                     #1       for j in range(3):
                     #1           if br[i][j] == 0:
                     #1               continue
                     #1           m[i][j] = br[i][j]
                     #1   pos = reverse_vector_by_matrix(vo, m)
                     #1   wv = weight_value
                     #1   weight_pos = quarkx.vect((pos[0]-vo[0])/wv, (pos[1]-vo[1])/wv, (pos[2]-vo[2])/wv)
                #2        fix_offsets = None
                #2        vtx_offset = weightvtxlist[old_vert_index][key]['vtx_offset']
                #2        if weight_value == 1.0:
                #2            check_pos = current_vertex.tuple
                #2            if str(check_pos) != str(vtx_offset):
                #2                weight_pos = quarkx.vect(check_pos)
                #2        else:
                #2            vtx_offsets = quarkx.vect(0.0, 0.0, 0.0)
                #2            for k in xrange(0, len(sorted_keys)):
                #2                vtx_offsets += quarkx.vect(weightvtxlist[old_vert_index][key]['vtx_offset'])
                #2            ovp = (vtx_offsets / len(sorted_keys)).tuple             # ovp = original current_vertex (computed)
                #2            cp = (round(ovp[0],6), round(ovp[1],6), round(ovp[2],6)) # cp = compare vtx pos
                #2            vp = current_vertex.tuple
                #2            if (fix_offsets is None) and ((abs(cp[0]) > abs(vp[0])+0.1) or (abs(cp[0]) < abs(vp[0])-0.1) or (abs(cp[1]) > abs(vp[1])+0.1) or (abs(cp[1]) < abs(vp[1])-0.1) or (abs(cp[2]) > abs(vp[2])+0.1) or (abs(cp[2]) < abs(vp[2])-0.1)):
                #2                fix_offsets = 1
                #2        if fix_offsets is not None:
                #2            temp = [0.0, 0.0, 0.0]
                #2            vo = weightvtxlist[old_vert_index][key]['vtx_offset']
                #2            for k in xrange(3):
                #2                temp[k] = (vp[k] * (vo[k] / ovp[k]))
                #2            weight_pos = quarkx.vect(temp[0], temp[1], temp[2])
                    elif joints[bone_index].dictspec.has_key('type') and joints[bone_index].dictspec['type'].startswith('skd-MOHAA'):
                        weight_pos = quarkx.vect(weightvtxlist[old_vert_index][key]['vtx_offset'])
                        bonelist = self.editor.ModelComponentList['bonelist']
                        bone_jointType = bonelist[key]['frames']['baseframe:mf']['SKD_JointType']
                        if bone_jointType == 1:
                            weight_pos = weight_pos
                    else:
                        weight_pos = (~bone_rot) * (current_vertex - bone_pos)
                    pos_x, pos_y, pos_z = weight_pos.tuple
                    weight_set += [(bone_index, weight_value, pos_x, pos_y, pos_z)]
                
                #Find shared sets of weights
                SameSet = None
                for tmp_weight_set in weight_sets:
                    SameSet = tmp_weight_set
                    if len(weight_set) != SameSet[1]:
                        #Different amount of weights; this can't be an identical set!
                        SameSet = None
                        continue
                    for weight_nr in range(SameSet[1]):
                        set_bone_index, set_weight_value, set_pos_x, set_pos_y, set_pos_z = weights[SameSet[0]+weight_nr]
                        bone_index, weight_value, pos_x, pos_y, pos_z = weight_set[weight_nr]
                        if (set_bone_index != bone_index) or (set_weight_value != weight_value) \
                        or (abs(set_pos_x - pos_x) > 0.0001) \
                        or (abs(set_pos_y - pos_y) > 0.0001) \
                        or (abs(set_pos_z - pos_z) > 0.0001):
                            #Different set
                            SameSet = None
                            break
                    if SameSet is not None:
                        break
                
                #Now save it all
                if SameSet is not None:
                    #Shared set of weights; use old one to avoid duplication
                    blend_index = SameSet[0]
                else:
                    #New set; add to the end of weights
                    blend_index = len(weights)
                    for weight in weight_set:
                        weights += [weight]
                    weight_sets += [(blend_index, blend_count)]
                vert_blends += [(blend_index, blend_count)]
            else: # Handles un-assigned vertexes and writes them to the mesh_error report for viewing by the user.
                #(Similar code as above here)
                #Create the weight_set for this vertex
                #New set; add to the end of weights
                blend_index = len(weights)
                blend_count = 1
                bone_index = 0 #0 = origin bone
                weight_value = 1.0
                
                bone_pos = joint_data[bone_index][0]
                bone_pos = quarkx.vect(bone_pos)
                bone_rot = joint_data[bone_index][1]
                bone_rot = quarkx.matrix(bone_rot)
                # For EF2 model being exported.
                if joints[bone_index].dictspec.has_key('type') and joints[bone_index].dictspec['type'] == 'skb-EF2':
                    weight_pos = ((bone_rot * current_vertex) + bone_pos) * weight_value
                else:
                    weight_pos = (~bone_rot) * (current_vertex - bone_pos)
                pos_x, pos_y, pos_z = weight_pos.tuple
                
                weights += [(bone_index, weight_value, pos_x, pos_y, pos_z)]
                weight_sets += [(blend_index, blend_count)]
                vert_blends += [(blend_index, blend_count)]
                # For vertex error report output.
                self.mesh_vtx_errors = self.mesh_vtx_errors + [old_vert_index]

        # Writes the "vert" section.
        Strings[2452] = comp.shortname + "\n" + Strings[2452]
        progressbar = quarkx.progressbar(2452, len(vertices))
        file.write('\tnumverts %i\n' % len(vertices))

        for vert_index in range(len(vertices)):
            progressbar.progress()
            for tri in range(len(triangles)):
                if triangles[tri][0][0] == vert_index:
                    U = triangles[tri][0][1]
                    V = triangles[tri][0][2]
                    break
                elif triangles[tri][1][0] == vert_index:
                    U = triangles[tri][1][1]
                    V = triangles[tri][1][2]
                    break
                elif triangles[tri][2][0] == vert_index:
                    U = triangles[tri][2][1]
                    V = triangles[tri][2][2]
                    break
            U = ie_utils.NicePrintableFloat(U)
            V = ie_utils.NicePrintableFloat(V)
            blend_index = vert_blends[vert_index][0]
            blend_count = vert_blends[vert_index][1]
            file.write('\tvert %i ( %s %s ) %i %i\n' % (vert_index, U, V, blend_index, blend_count))
        file.write('\n')
        Strings[2452] = Strings[2452].replace(comp.shortname + "\n", "")
        progressbar.close()

        # Writes the mesh_errors report.
        if len(self.mesh_vtx_errors) != 0:
            self.mesh_errors = self.mesh_errors + "\nVertexes not assigned to a bone and weight value applied\nfor component: " + comp.shortname + "\n\n"
            vtxcount = 0
            for vtx in range(len(self.mesh_vtx_errors)):
                if vtx == len(self.mesh_vtx_errors)-1:
                    self.mesh_errors = self.mesh_errors + str(self.mesh_vtx_errors[vtx]) + "\n============================================\n"
                    break
                if vtxcount == 10:
                    self.mesh_errors = self.mesh_errors + str(self.mesh_vtx_errors[vtx]) + ",\n"
                    vtxcount = 0
                    continue
                self.mesh_errors = self.mesh_errors + str(self.mesh_vtx_errors[vtx]) + ", "
                vtxcount = vtxcount + 1


        # Writes the "tri" section.
        Strings[2453] = comp.shortname + "\n" + Strings[2453]
        progressbar = quarkx.progressbar(2453, len(triangles))
        file.write('\tnumtris %i\n' % len(triangles))
        for tri in range(len(triangles)):
            progressbar.progress()
            file.write('\ttri %i %i %i %i\n' % (tri, triangles[tri][0][0], triangles[tri][1][0], triangles[tri][2][0]))
        file.write('\n')
        Strings[2453] = Strings[2453].replace(comp.shortname + "\n", "")
        progressbar.close()

        # Writes the "weight" section.
        Strings[2450] = comp.shortname + "\n" + Strings[2450]
        progressbar = quarkx.progressbar(2450, len(weights))
        file.write('\tnumweights %i\n' % (len(weights)))

        for weight_index in range(len(weights)):
            progressbar.progress()
            weight = weights[weight_index]
            bone_index = weight[0]
            weight_value = ie_utils.NicePrintableFloat(weight[1])
            current_vertex0 = ie_utils.NicePrintableFloat(weight[2])
            current_vertex1 = ie_utils.NicePrintableFloat(weight[3])
            current_vertex2 = ie_utils.NicePrintableFloat(weight[4])
            file.write('\tweight %i %i %s ( %s %s %s )\n' % (weight_index, bone_index, weight_value, current_vertex0, current_vertex1, current_vertex2))

        file.write('}\n')
        file.write('\n')
        Strings[2450] = Strings[2450].replace(comp.shortname + "\n", "")
        progressbar.close()


######################################################
# EXPORT ANIMATION ONLY SECTION
######################################################
    # "exp_list" is a list of one or more selected model components for exporting.
def export_anim(self, file, filename, exp_list):
    global tobj, Strings

    NumberOfFrames = -1
    for object in exp_list:
        CurNumberOfFrames = len(object.dictitems['Frames:fg'].subitems)
        if NumberOfFrames == -1:
            NumberOfFrames = CurNumberOfFrames
        elif (CurNumberOfFrames != NumberOfFrames):
            quarkx.msgbox("The selected component folders do not have the same number of frames !\n\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        else:
            NumberOfFrames = CurNumberOfFrames
    frames = exp_list[0].dictitems['Frames:fg'].subitems

    #Filter out all the baseframes, since we don't need them for MD5
    UseOnlyTheseFrames = []
    for frame_counter in range(0,NumberOfFrames):
        if not frames[frame_counter].shortname.endswith("baseframe"):
            UseOnlyTheseFrames += [frame_counter]
    NumberOfFrames = len(UseOnlyTheseFrames)

    joints = self.bones
    NumberOfBones = len(joints)
    joints_parent_index = [[]]*NumberOfBones
    for joint_counter in range(0,NumberOfBones):
        current_joint = joints[joint_counter]
        joints_parent_index[joint_counter] = -1
        if current_joint.dictspec['parent_name'] != "None":
            for parent_bone in range(len(joints)):
                if current_joint.dictspec['parent_name'] == joints[parent_bone].name:
                    joints_parent_index[joint_counter] = parent_bone
                    break

    # Get all the animation data
    QuArK_frame_position = [[]]*NumberOfFrames
    QuArK_frame_matrix = [[]]*NumberOfFrames
    progressbar = quarkx.progressbar(2455, NumberOfFrames*2)
    for frame_counter in range(0,NumberOfFrames):
        progressbar.progress()
        QuArK_frame_position[frame_counter] = [[]]*NumberOfBones
        QuArK_frame_matrix[frame_counter] = [[]]*NumberOfBones
        for joint_counter in range(0,NumberOfBones):
            current_joint = joints[joint_counter]
            if not self.editor.ModelComponentList['bonelist'].has_key(current_joint.name):
                # This bone has no vertexes assigned to it but could have a child bone for editing the model only.
                bone_pos = current_joint.position.tuple
                bone_rot = current_joint.rotmatrix.tuple
            else:
                bone_data = self.editor.ModelComponentList['bonelist'][current_joint.name]['frames'][frames[UseOnlyTheseFrames[frame_counter]].name]
                bone_pos = bone_data['position']
                bone_rot = bone_data['rotmatrix']
            QuArK_frame_position[frame_counter][joint_counter] = quarkx.vect(bone_pos)
            QuArK_frame_matrix[frame_counter][joint_counter] = quarkx.matrix(bone_rot)

    # Calculate all the MD5 animation data
    QuArK_frame_position_raw = [[]]*NumberOfFrames
    QuArK_frame_matrix_raw = [[]]*NumberOfFrames
    for frame_counter in range(0,NumberOfFrames):
        progressbar.progress()
        QuArK_frame_position_raw[frame_counter] = [[]]*NumberOfBones
        QuArK_frame_matrix_raw[frame_counter] = [[]]*NumberOfBones
        BonesToDo = range(0,NumberOfBones)
        BoneDone = []
        for joint_counter in range(0,NumberOfBones):
            BoneDone += [0]
        while len(BonesToDo) != 0:
            DelayBones = []
            for joint_counter in BonesToDo:
                current_joint = joints[joint_counter]
                parent_index = joints_parent_index[joint_counter]
                if parent_index != -1:
                    if BoneDone[parent_index] == 0:
                        #This bone is being processed before its parent! This is BAD!
                        DelayBones += [joint_counter]
                        continue
                    #parent_bone = joints[parent_index]
                    ParentMatrix = QuArK_frame_matrix[frame_counter][parent_index]
                    temppos = QuArK_frame_position[frame_counter][joint_counter] - QuArK_frame_position[frame_counter][parent_index]
                    QuArK_frame_position_raw[frame_counter][joint_counter] = (~ParentMatrix) * temppos
                    QuArK_frame_matrix_raw[frame_counter][joint_counter] = (~ParentMatrix) * QuArK_frame_matrix[frame_counter][joint_counter]
                else:
                    QuArK_frame_position_raw[frame_counter][joint_counter] = QuArK_frame_position[frame_counter][joint_counter]
                    QuArK_frame_matrix_raw[frame_counter][joint_counter] = QuArK_frame_matrix[frame_counter][joint_counter]
                BoneDone[joint_counter] = 1
            BonesToDo = DelayBones
    progressbar.close()

    hierarchy = []
    numAnimatedComponents = 0
    progressbar = quarkx.progressbar(2448, NumberOfBones * NumberOfFrames)
    for joint_counter in range(0,NumberOfBones):
        progressbar.progress()
        Flags = [0, 0, 0, 0, 0, 0]   #Tx, Ty, Tz, Qx, Qy, Qz
        Values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]   #Tx, Ty, Tz, Qx, Qy, Qz
        for frame_counter in range(0,NumberOfFrames):
            progressbar.progress()
            # Convert the position to a tuple and rotmatrix to quaternions:
            QuArK_frame_position_raw[frame_counter][joint_counter] = (QuArK_frame_position_raw[frame_counter][joint_counter]).tuple
            rotmatrix = (QuArK_frame_matrix_raw[frame_counter][joint_counter]).tuple
            rotmatrix = ((rotmatrix[0][0], rotmatrix[0][1], rotmatrix[0][2], 0.0)
                        ,(rotmatrix[1][0], rotmatrix[1][1], rotmatrix[1][2], 0.0)
                        ,(rotmatrix[2][0], rotmatrix[2][1], rotmatrix[2][2], 0.0)
                        ,(            0.0,             0.0,             0.0, 1.0))
            rotmatrix = matrix2quaternion(rotmatrix)
            #if rotmatrix[3] > 0.0:
            #    rotmatrix = (-rotmatrix[0], -rotmatrix[1], -rotmatrix[2])
            QuArK_frame_matrix_raw[frame_counter][joint_counter] = rotmatrix

            bone_pos = QuArK_frame_position_raw[frame_counter][joint_counter]
            bone_rot = QuArK_frame_matrix_raw[frame_counter][joint_counter]
            if (frame_counter == 0):
                Values[0] = bone_pos[0]
                Values[1] = bone_pos[1]
                Values[2] = bone_pos[2]
                Values[3] = bone_rot[0]
                Values[4] = bone_rot[1]
                Values[5] = bone_rot[2]
            else:
                if ((Flags[0] == 0) and (abs(Values[0] - bone_pos[0]) > 0.0001)):
                    numAnimatedComponents += 1
                    Flags[0] = 1
                if ((Flags[1] == 0) and (abs(Values[1] - bone_pos[1]) > 0.0001)):
                    numAnimatedComponents += 1
                    Flags[1] = 1
                if ((Flags[2] == 0) and (abs(Values[2] - bone_pos[2]) > 0.0001)):
                    numAnimatedComponents += 1
                    Flags[2] = 1
                if ((Flags[3] == 0) and (abs(Values[3] - bone_rot[0]) > 0.0001)):
                    numAnimatedComponents += 1
                    Flags[3] = 1
                if ((Flags[4] == 0) and (abs(Values[4] - bone_rot[1]) > 0.0001)):
                    numAnimatedComponents += 1
                    Flags[4] = 1
                if ((Flags[5] == 0) and (abs(Values[5] - bone_rot[2]) > 0.0001)):
                    numAnimatedComponents += 1
                    Flags[5] = 1
        hierarchy += [(Flags, Values)]
    progressbar.close()

    bounds = [[]]*NumberOfFrames
    for frame_counter in range(0,NumberOfFrames):
        current_min = [None, None, None]
        current_max = [None, None, None]
        for object in exp_list:
            vertices = object.dictitems['Frames:fg'].subitems[UseOnlyTheseFrames[frame_counter]].vertices
            for vert in vertices:
                vert = vert.tuple
                for i in range(0,3):
                    if ((current_min[i] is None) or (vert[i] < current_min[i])):
                        current_min[i] = vert[i]
                    if ((current_max[i] is None) or (vert[i] > current_max[i])):
                        current_max[i] = vert[i]
        bounds[frame_counter] = (current_min, current_max)

    FlagName = ('Tx', 'Ty', 'Tz', 'Qx', 'Qy', 'Qz')

    file.write('numFrames %i\n' % NumberOfFrames)
    file.write('numJoints %i\n' % len(joints))
    file.write('frameRate 24\n')
    file.write('numAnimatedComponents %i\n' % numAnimatedComponents)
    file.write('\n')

    file.write('hierarchy {\n')
    FlagStartIndex = [[]]*NumberOfBones
    for joint_counter in range(0,NumberOfBones):
        if (joint_counter == 0):
            FlagStartIndex[joint_counter] = 0
        else:
            FlagStartIndex[joint_counter] = FlagStartIndex[joint_counter-1] + NumberOfFlags
        current_joint = joints[joint_counter]
        joint_name = current_joint.shortname.split("_", 1)[1]
        joint_name = joint_name.replace(" ", "_")
        parent_index = joints_parent_index[joint_counter]
        if parent_index == -1:
            parent_bone_name = ""
        else:
            parent_bone_name = joints[parent_index].shortname.split("_", 1)[1]
        hierarchy_item = hierarchy[joint_counter]
        Flags = hierarchy_item[0]
        Values = hierarchy_item[1]
        FlagValue = 0
        FlagText = ''
        NumberOfFlags = 0
        for i in range(0,6):
            if (Flags[i] != 0):
                FlagValue += 2 ** i
                FlagText += ' ' + FlagName[i]
                NumberOfFlags += 1
        comment_part = ''
        if len(parent_bone_name) != 0:
            comment_part += ' ' + parent_bone_name
        if FlagValue != 0:
            comment_part += ' (' + FlagText + ' )'
        if NumberOfFlags == 0:
            OutputFlagStartIndex = 0
        else:
            OutputFlagStartIndex = FlagStartIndex[joint_counter]
        file.write('\t"%s"\t%i %i %i\t//%s\n' % (joint_name, parent_index, FlagValue, OutputFlagStartIndex, comment_part))
    file.write('}\n')
    file.write('\n')

    file.write('bounds {\n')
    for frame_counter in range(0,NumberOfFrames):
        current_bound = bounds[frame_counter]
        current_min = current_bound[0]
        current_max = current_bound[1]
        file.write('\t(')
        for amt in current_min:
            amt = ie_utils.NicePrintableFloat(amt)
            file.write(' %s' % (amt))
        file.write(' ) (')
        for amt in current_max:
            amt = ie_utils.NicePrintableFloat(amt)
            file.write(' %s' % (amt))
        file.write(' )\n')
    file.write('}\n')
    file.write('\n')

    file.write('baseframe {\n')
    for joint_counter in range(0,NumberOfBones):
        hierarchy_item = hierarchy[joint_counter]
        Values = hierarchy_item[1]
        file.write('\t( ')
        for value in range(len(Values)):
            amt = ie_utils.NicePrintableFloat(Values[value])
            if value == len(Values)-4:
                file.write('%s ) ( ' % (amt))
                continue
            if value == len(Values)-1:
                file.write('%s )\n' % (amt))
                break
            file.write('%s ' % (amt))
    file.write('}\n')
    file.write('\n')

    progressbar = quarkx.progressbar(2452, NumberOfFrames * NumberOfBones)
    for frame_counter in range(0,NumberOfFrames):
        progressbar.progress()
        file.write('frame %i {\n' % frame_counter)
        for joint_counter in range(0,NumberOfBones):
            progressbar.progress()
            hierarchy_item = hierarchy[joint_counter]
            Flags = hierarchy_item[0]
            bone_pos = QuArK_frame_position_raw[frame_counter][joint_counter]
            bone_rot = QuArK_frame_matrix_raw[frame_counter][joint_counter]
            FirstItem = 1
            for i in range(0,3):
                if (Flags[i] != 0):
                    if (FirstItem):
                        file.write('\t')
                        FirstItem = 0
                    amt = ie_utils.NicePrintableFloat(bone_pos[i])
                    file.write(' %s' % amt)
            for i in range(0,3):
                if (Flags[i+3] != 0):
                    if (FirstItem):
                        file.write('\t')
                        FirstItem = 0
                    amt = ie_utils.NicePrintableFloat(bone_rot[i])
                    file.write(' %s' % amt)
            if (FirstItem == 0):
                file.write('\n')
        file.write('}\n')
        file.write('\n')
    progressbar.close()


######################################################
# END OF EXPORT ANIMATION ONLY SECTION
######################################################


######################################################
# CALL TO SAVE MESH (.md5mesh) FILE (called from dialog section below)
######################################################
def save_md5(self):
    global tobj, logging, exportername, textlog, Strings, exp_list, Tab, worldTable
    editor = self.editor
    if editor is None:
        return
    filename = self.filename

    objects = editor.layout.explorer.sellist
    exp_list = []
    Tab = "\t"
    worldTable = {'mat_type': 0} #default

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    file = self.md5file

    #get the component
    component = editor.Root.currentcomponent # This gets the first component (should be only one).

    # This section calls common file writing functions then to export either an .md5 mesh or animation file.
    set_lists(exp_list, objects, worldTable)
    write_header(self, file, filename, component, worldTable)
    if filename.endswith(".md5mesh"): # Calls to write a mesh file.
        export_mesh(self, file, filename, exp_list)
    else: # Calls to write an animation file.
        export_anim(self, file, filename, exp_list)

    file.close()

    if self.src['Shaders'] is not None and worldTable['mat_type'] == 1:
        write_shaders(filename, exp_list)
    if self.src['Skins'] is not None:
        for comp in exp_list:
            comp = comp[0]
            for skin in comp.dictitems['Skins:sg'].subitems:
                tempfilename = filename.replace("\\", "/")
                tempfilename = tempfilename.rsplit("/", 1)[0]
                tempskinname = skin.name.replace("\\", "/")
                tempskinname = tempskinname.rsplit("/", 1)[1]
                skin.filename = tempfilename + '/' + tempskinname
                quarkx.savefileobj(skin, FM_Save, 0)

    add_to_message = "Any skin textures used as a material\nwill need to be converted to a .tga file.\n\nThis can be done in an image editor\nsuch as 'PaintShopPro' or 'PhotoShop'."

    if self.mesh_errors != "":
        quarkx.beep()
        add_to_message = add_to_message + "\n\nUNASSIGNED VERTEXES !\n\nA text file named 'MD5_unassigned_vertex_log' has been written to your main QuArK folder.\nRead that file for a listing of unassigned vertexes by component."
        MD5_errorlog = open(quarkx.exepath + '\MD5_unassigned_vertex_log.txt',"w")
        MD5_errorlog.write(self.mesh_errors)
        MD5_errorlog.close()

    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.


######################################################
# CALL TO SAVE MESH (.md5mesh) OR ANIMATION (.md5anim) FILE (where it all starts off from)
######################################################
# Saves the model file: root is the actual file,
# filename is the full path and name of the .md5 to create.
# For example:  C:Program Files\Doom 3\base\models\md5\monsters\archvile\archvile.md5mesh or attack1.md5anim.
# gamename is None.
def savemodel(root, filename, gamename, nomessage=0):
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
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select component folders for exporting.\n\nAn item that is not a component folder is in your selections.\n\nDeselect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
    anim_frames = 0
    for object in objects:
        if filename.endswith(".md5mesh"): # Calls to save the .md5mesh file.
            if len(object.dictitems['Frames:fg'].subitems[0].dictspec['Vertices']) == 0:
                quarkx.msgbox("Component " + object.shortname + "\nhas no frame vertices to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            if len(object.dictitems['Skins:sg'].subitems) == 0:
                quarkx.msgbox("Component " + object.shortname + "\nhas no skin textures to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            if object.dictitems['Frames:fg'].subitems[0].name != "baseframe:mf":
                quarkx.beep()
                quarkx.msgbox("MISSING or MISSPLACED MESH baseframe(s) !\n\nAll selected component's FIRST frame must be a static pose\nof that model's part and that frame named 'baseframe' !\n\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return

        else: # Calls to save the .md5anim file.
            if not object.dictitems['Frames:fg'] or len(object.dictitems['Frames:fg'].subitems) < 2:
                quarkx.msgbox("Component " + object.shortname + "\nhas no animation frames to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            if anim_frames == 0:
                anim_frames = len(object.dictitems['Frames:fg'].subitems)
            if len(object.dictitems['Frames:fg'].subitems) != anim_frames:
                quarkx.msgbox("Component " + object.shortname + "\nnumber of animation frames\ndoes not equal other components.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return

    UIExportDialog(root, filename, editor) # Calls the dialog below which calls to save a mesh or animaition file.
    return


### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".md5mesh Doom3\Quake4 Exporter", ".md5mesh file", "*.md5mesh", savemodel)
quarkpy.qmdlbase.RegisterMdlExporter(".md5anim Doom3\Quake4 Exporter", ".md5anim file", "*.md5anim", savemodel)


######################################################
# DIALOG SECTION (which calls to export a mesh or animation file)
######################################################
class ExportSettingsDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (200, 300)
    dfsep = 0.6     # sets 60% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """
        {
        Style = "13"
        Caption = "md5 Export Items"
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

        Doom3: =
            {
            Txt = "Export for Doom 3:"
            Typ = "X"
            Hint = "When checked the model will be exported"$0D
                   "for use in the Doom 3 game engine."$0D
                   "Default setting is checked."
            }

        Quake4: =
            {
            Txt = "Export for Quake 4:"
            Typ = "X"
            Hint = "When checked the model will be exported"$0D
                   "for use in the Quake 4 game engine."$0D
                   "Default setting is unchecked."
            }

        Skins: =
            {
            Txt = "Export Skin Textures:"
            Typ = "X"
            Hint = "Check this box to export each components skins files."$0D
                   "These files may need to be moved to other folders."
            }

        Shaders: =
            {
            Txt = "Export Shaders Files:"
            Typ = "X"
            Hint = "Check this box to export each components"$0D
                   "skins shader files, if any exist."$0D
                   "These files may need to be moved to other folders"$0D
                   "or copied into other default game shader files."
            }

        makefolder: =
            {
            Txt = "Make file folder:"
            Typ = "X"
            Hint = "Check this box to make a new folder to place"$0D
                   "all export files in at the location you chose."$0D$0D
                   "Some of these files may need to be moved to other folders"$0D
                   "or copied into other files, such as for the model's shader file."$0D$0D
                   "If unchecked files will all be placed at the same location"$0D
                   "that you chose for the .md5 model file to be placed."
            }

        sep: = { Typ="S" Txt="" }
        MakeFiles:py = {Txt="Export Model"}
        close:py = {Txt="Close dialog"}
        }
        """

    def __init__(self, form1, root, filename, editor, newfiles_folder): # Creates the dialogbox.
        self.root = root
        self.filename = filename
        self.editor = editor
        skeletongroup = self.editor.Root.dictitems['Skeleton:bg']  # get the bones group
        bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
        comp_list = []
        for item in self.editor.layout.explorer.sellist:
            if item.type == ":mc":
                comp_list = comp_list + [item]
        export_bones = []
        for bone in range(len(bones)):
            bonename = bones[bone].shortname
            remove = bonename.split("_")[0]
            remove = remove + "_"
            foundbone = 0
            for comp in range(len(comp_list)):
                if comp_list[comp].name.startswith(remove):
                    break
                if comp == len(comp_list)-1:
                    for item in range(len(self.editor.Root.subitems)):
                        if self.editor.Root.subitems[item].type == ":mc" and self.editor.Root.subitems[item].name.startswith(remove):
                            foundbone = 1
                            break
                        if item == len(self.editor.Root.subitems)-1:
                            break
            if foundbone == 0:
                export_bones = export_bones + [bones[bone]]
        self.bones = export_bones
        self.mesh_vtx_errors = []
        self.mesh_errors = ""
        self.newfiles_folder = newfiles_folder
        self.md5file = None
        self.exportpath = filename.replace('\\', '/')
        self.exportpath = self.exportpath.rsplit('/', 1)[0]
        src = quarkx.newobj(":")
        src['dummy'] = "1"
        src['Doom3'] = "1"
        src['Quake4'] = None
        src['Skins'] = None
        src['Shaders'] = None
        src['makefolder'] = None
        self.src = src

        # Create the dialog form and the buttons.
        quarkpy.qmacro.dialogbox.__init__(self, form1, src,
            MakeFiles = quarkpy.qtoolbar.button(self.MakeFiles,"DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.",ico_editor, 3, "Export Model"),
            close = quarkpy.qtoolbar.button(self.close, "DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.", ico_editor, 0, "Cancel Export")
            )

    def datachange(self, df):
        if self.src['Quake4'] == "1" and self.src['dummy'] == "1":
            self.src['Doom3'] = None
            self.src['dummy'] = None
        elif self.src['Doom3'] == "1" and self.src['dummy'] is None:
            self.src['Quake4'] = None
            self.src['dummy'] = "1"
        elif self.src['Quake4'] is None and self.src['Doom3'] is None:
            self.src['Doom3'] = "1"
            self.src['dummy'] = "1"
        df.setdata(self.src, self.f) # This line updates the dialog.

    def MakeFiles(self, btn):
        # Accepts all entries then starts making the processing function calls.
        quarkx.globalaccept()
        root = self.root

        if self.src["makefolder"] is not None:
            if not os.path.exists(self.newfiles_folder):
                os.mkdir(self.newfiles_folder)
            else:
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

        # Opens the output file for writing the .md5 mesh or animation file to disk.
        self.md5file = open(self.filename,"w")
        save_md5(self) # This is the funciton above called to start exporting the mesh or animation file.


def UIExportDialog(root, filename, editor):
    # Sets up the new window form for the exporters dialog for user selection settings and calls its class.
    form1 = quarkx.newform("masterform")
    if filename.endswith(".md5mesh"):
        newfiles_folder = filename.replace(".md5mesh", "")
    else:
        newfiles_folder = filename.replace(".md5anim", "")
    ExportSettingsDlg(form1, root, filename, editor, newfiles_folder)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_md5_export.py,v $
# Revision 1.20  2012/01/30 03:37:25  cdunde
# To allow MOHAA model format to be exported as MD5 files.
#
# Revision 1.19  2012/01/15 04:39:32  cdunde
# Fix by DanielPharos for handling identical vertex_indexes with different U,V coords.
#
# Revision 1.18  2012/01/14 22:49:08  cdunde
# Change by DanielPharos to skip over baseframes which are not used
# and allow other model formats to be exported as MD5 files.
#
# Revision 1.17  2012/01/13 08:04:27  cdunde
# To get MD5 exporter to work with Alice, FAKK2 & EF2 skb_importer models.
#
# Revision 1.16  2011/12/25 03:57:30  cdunde
# Update to ensure proper mesh baseframe bone position and matrix exporting.
#
# Revision 1.15  2011/12/16 01:06:21  cdunde
# To co-ordinate better with other model format imports and exports.
# Also file cleanup.
#
# Revision 1.14  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.13  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.12  2010/05/01 05:01:17  cdunde
# Update by DanielPharos to allow removal of weight_index storage in the ModelComponentList.
#
# Revision 1.11  2010/04/23 23:36:17  cdunde
# Proper export changes by DanielPharos.
#
# Revision 1.10  2010/04/09 23:03:00  cdunde
# Comment typo correction.
#
# Revision 1.9  2010/03/20 05:25:31  cdunde
# Update by DanielPharos to bring imported models and animations more inline with original file.
#
# Revision 1.8  2010/03/10 04:24:06  cdunde
# Update to support added ModelComponentList for 'bonelist' updating.
#
# Revision 1.7  2010/03/08 02:21:18  cdunde
# Variable name correction.
#
# Revision 1.6  2010/03/07 09:43:48  cdunde
# Updates and improvements to both the md5 importer and exporter including animation support.
#
# Revision 1.5  2009/08/27 04:55:06  cdunde
# To add support for exporting other model types as .md5mesh files.
#
# Revision 1.4  2009/08/27 04:32:20  cdunde
# Update for multiple bone sets for import and export to restrict export of bones for selected components only.
#
# Revision 1.3  2009/08/27 04:00:41  cdunde
# To setup a bone's "flags" dictspec item for model importing and exporting support that use them.
# Start of .md5anim exporting support.
#
# Revision 1.2  2009/08/10 01:31:15  cdunde
# To improve on properly exporting mesh "shader" name.
#
# Revision 1.1  2009/08/09 17:17:24  cdunde
# Added .md5mesh and .md5anim model exporter including bones, skins and shaders.
#
#
#