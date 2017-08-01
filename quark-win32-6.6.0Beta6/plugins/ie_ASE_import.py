"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Doom 3 .ase model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_ASE_import.py,v 1.22 2011/06/03 20:29:26 danielpharos Exp $

Info = {
   "plug-in":       "ie_ASE_importer",
   "desc":          "This script imports a .ase Doom 3 model file and textures into QuArK for editing. Original code from Blender, ASEimport_31May06.py, author - Goofos, version 0.1",
   "date":          "March 13 2009",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 2" }


# goofos at epruegel.de
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

import time, os, struct, operator, sys as osSys
import quarkx
import quarkpy.qmacro
from quarkpy.qutils import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings
import quarkpy.dlgclasses

# Globals
SS_MODEL = 3
logging = 0
importername = "ie_ASE_import.py"
textlog = "ase_ie_log.txt"
editor = None
image_type_list = ['.tga', '.dds', '.png', '.jpg', '.bmp']  # Order from best to worst (personal judgement).

# Globals for this file only
material_count = 0
materials_list = {}
scene_specifics = {}
comp_specifics = {}


def makeRGB(words1, words2, words3):
    return (int(round(float(words1)*255)), int(round(float(words2)*255)), int(round(float(words3)*255)))


# =====================
# === Load an image ===
# =====================
#extensively search for image name
def load_image(dir_part, name):
    dir_part = dir_part.replace("\\", "/")
    name = name.replace("\\", "/")
    name_list = []
    # QuArK is not case sensitive for paths or file names, so we don't need to correct for that.
    for ext in image_type_list:
        name_list = name_list + [dir_part + name + ext]
    return name_list


def read_main(file, basepath, filename):

    global counts, tobj, logging
    counts = {'verts': 0, 'tris': 0}
    start = time.clock()
    file = open(filename, "r")

    if logging == 1:
        tobj.logcon("----------------start-----------------\nImport Patch: " + filename)

    lines= file.readlines()
    ComponentList, message = read_file(file, lines, basepath, filename)

 #   Blender.Window.DrawProgressBar(1.0, '')  # clear progressbar
    file.close()
    end = time.clock()
    seconds = " in %.2f %s" % (end-start, "seconds")
    log_message = "Successfully imported " + filename + seconds
    if logging == 1:
        tobj.logcon("----------------end-----------------")
        totals = "Verts: %i Tris: %i " % (counts['verts'], counts['tris'])
        tobj.logcon(totals)
        tobj.logcon(log_message)

    return ComponentList, message

# QuArK note: we can take this out if log prints out ok.
def print_boxed(text): #Copy/Paste from meshtools, only to remove the beep :)
    lines = text.splitlines()
    maxlinelen = max(map(len, lines))
    if osSys.platform[:3] == "win":
        print chr(218)+chr(196) + chr(196)*maxlinelen + chr(196)+chr(191)
        for line in lines:
            print chr(179) + ' ' + line.ljust(maxlinelen) + ' ' + chr(179)
        print chr(192)+chr(196) + chr(196)*maxlinelen + chr(196)+chr(217)
    else:
        print '+-' + '-'*maxlinelen + '-+'
        for line in lines: print '| ' + line.ljust(maxlinelen) + ' |'
        print '+-' + '-'*maxlinelen + '-+'
    #print '\a\r', # beep when done


class ase_obj: # Equivalent to a QuArK component.

    def __init__(self):
        self.name = 'Name'
        self.objType = None
        self.row0x = None
        self.row0y = None
        self.row0z = None
        self.row1x = None
        self.row1y = None
        self.row1z = None
        self.row2x = None
        self.row2y = None
        self.row2z = None
        self.row3x = None
        self.row3y = None
        self.row3z = None
        self.parent = None
        self.obj = None
        self.objName = 'Name'
        self.material_ref = None

class ase_mesh:

    def __init__(self):
        self.name = ''
        self.vCount = 0
        self.fCount = 0
        self.uvVCount = 0
        self.uvFCount = 0
        self.vcVCount = 0
        self.vcFCount = 0
        self.meVerts = []
        self.meFaces = []
        self.uvVerts = []
        self.uvFaces = []
        self.vcVerts = []
        self.vcFaces = []
        self.hasFUV = 0
        self.hasVC = 0

class mesh_face:

    def __init__(self):
        self.v1 = 0
        self.v2 = 0
        self.v3 = 0
        self.mat = None # QuArK note: this is not even being used anywhere, confirm and remove.

class mesh_vert:

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

class mesh_uvVert:

    def __init__(self):
        self.index = 0
        self.u = 0.0
        self.v = 0.0
        self.vec = quarkx.vect(self.u, self.v, 0.0)

class mesh_uvFace:

    def __init__(self):
        self.index = 0
        self.uv1 = 0
        self.uv2 = 0
        self.uv3 = 0

class mesh_vcVert:

    def __init__(self):
        self.index = 0
        self.r = 0
        self.g = 0
        self.b = 0
        self.a = 255

class mesh_vcFace:

    def __init__(self):
        self.index = 0
        self.c1 = 0
        self.c2 = 0
        self.c3 = 0


def read_file(file, lines, basepath, filename):
    global material_count, materials_list, material_0, scene_specifics, comp_specifics
    material_count = 0
    materials_list = {}
    material_sections_found = 0
    material_section = None
    objects = []
    objIdx = 0
    objCheck = -1 #needed to skip helper objects
    PBidx = 0.0
    lineCount = float(len(lines))
    material_0 = None


 #   Blender.Window.DrawProgressBar(0.0, "Read File...") 
    submat_flag = 0
    submat_nbr = ""
    for line in lines:
        words = line.split()
        if line.find("*MATERIAL_COUNT ") != -1: # Finds this text in the current line.
            material_count = int(words[1])

 #       if (PBidx % 10000) == 0.0:
 #           Blender.Window.DrawProgressBar(PBidx / lineCount, "Read File...")

        if not words:
            continue 
        elif words[0] == '*SCENE_BACKGROUND_STATIC':
            scene_specifics['SCENE_BACKGROUND_STATIC'] = RGBToColor(makeRGB(words[1], words[2], words[3]))
        elif words[0] == '*SCENE_AMBIENT_STATIC':
            scene_specifics['SCENE_AMBIENT_STATIC'] = RGBToColor(makeRGB(words[1], words[2], words[3]))
        elif words[0] == '*MATERIAL_COUNT':
            material_count = int(words[1])
        elif words[0] == '*SUBMATERIAL':
            submat_flag = 1
            submat_nbr = "SUB" + words[1] + "_"
            materials_list[material_section][submat_nbr+'PARENT'] = material_section
            materials_list[material_section][submat_nbr+'BITMAP'] = None
        elif submat_flag == 1 and words[0] == '*MAP_DIFFUSE':
            submat_flag = 2
        elif submat_flag == 1 and words[0] == "}":
            submat_flag = 0
            submat_nbr = ""
        elif submat_flag == 2 and words[0] == "}":
            submat_flag = 1
        elif words[0] == '*MATERIAL':
            material_section = int(words[1])
            materials_list[material_section] = {}
            submat_nbr = "MAT" + words[1] + "_"
            materials_list[material_section][submat_nbr + 'BITMAP'] = None
        elif words[0] == '*MATERIAL_NAME':
            material_temp = ' '.join(words[1:])
            material_temp = material_temp.replace('"', "")
            materials_list[material_section][submat_nbr+'MATERIAL_NAME'] = material_temp
            if material_0 is None:
                material_0 = material_temp.split(" ")
                material_0 = material_0[len(material_0)-1]
                material_0 = material_0.replace("\\", "/")
                material_0 = material_0.split("/")
                material_0 = material_0[len(material_0)-1]
        elif words[0] == '*MATERIAL_CLASS':
            material_temp = words[1].replace('"', "")
            materials_list[material_section][submat_nbr+'MATERIAL_CLASS'] = material_temp
        elif words[0] == '*MATERIAL_AMBIENT':
            materials_list[material_section][submat_nbr+'MATERIAL_AMBIENT'] = RGBToColor(makeRGB(words[1], words[2], words[3]))
        elif words[0] == '*MATERIAL_DIFFUSE':
            materials_list[material_section][submat_nbr+'MATERIAL_DIFFUSE'] = RGBToColor(makeRGB(words[1], words[2], words[3]))
        elif words[0] == '*MATERIAL_SPECULAR':
            materials_list[material_section][submat_nbr+'MATERIAL_SPECULAR'] = RGBToColor(makeRGB(words[1], words[2], words[3]))
        elif words[0] == '*MATERIAL_SHINE':
            materials_list[material_section][submat_nbr+'MATERIAL_SHINE'] = words[1]
        elif words[0] == '*MATERIAL_SHINESTRENGTH':
            materials_list[material_section][submat_nbr+'MATERIAL_SHINESTRENGTH'] = words[1]
        elif words[0] == '*MATERIAL_TRANSPARENCY':
            materials_list[material_section][submat_nbr+'MATERIAL_TRANSPARENCY'] = words[1]
        elif words[0] == '*MATERIAL_WIRESIZE':
            materials_list[material_section][submat_nbr+'MATERIAL_WIRESIZE'] = words[1]
        elif words[0] == '*MATERIAL_SHADING':
            materials_list[material_section][submat_nbr+'MATERIAL_SHADING'] = words[1]
        elif words[0] == '*MATERIAL_XP_FALLOFF':
            materials_list[material_section][submat_nbr+'MATERIAL_XP_FALLOFF'] = words[1]
        elif words[0] == '*MATERIAL_SELFILLUM':
            materials_list[material_section][submat_nbr+'MATERIAL_SELFILLUM'] = words[1]
        elif words[0] == '*MATERIAL_FALLOFF':
            materials_list[material_section][submat_nbr+'MATERIAL_FALLOFF'] = words[1]
        elif words[0] == '*MATERIAL_XP_TYPE':
            materials_list[material_section][submat_nbr+'MATERIAL_XP_TYPE'] = words[1]
        elif words[0] == '*MAP_NAME':
            material_temp = ' '.join(words[1:])
            material_temp = material_temp.replace('"', "")
            materials_list[material_section][submat_nbr+'MAP_NAME'] = material_temp
        elif words[0] == '*MAP_CLASS':
            material_temp = words[1].replace('"', "")
            materials_list[material_section][submat_nbr+'MAP_CLASS'] = material_temp
        elif words[0] == '*MAP_SUBNO':
            words1 = float(words[1])
            words1 = int(words1)
            materials_list[material_section][submat_nbr+'MAP_SUBNO'] = str(words1)
        elif words[0] == '*MAP_AMOUNT':
            word1 = float(words[1])
            word1 = "%.4f" % (word1)
            materials_list[material_section][submat_nbr+'MAP_AMOUNT'] = word1
        elif words[0] == '*BITMAP':
            words1 = ' '.join(words[1:])
            words1 = words1.replace('"', "")
            words1 = words1.replace('\\', "/")
            materials_list[material_section][submat_nbr+'BITMAP'] = words1
        elif words[0] == '*MAP_TYPE':
            materials_list[material_section][submat_nbr+'MAP_TYPE'] = words[1]
        elif words[0] == '*UVW_U_OFFSET':
            materials_list[material_section][submat_nbr+'UVW_U_OFFSET'] = words[1]
        elif words[0] == '*UVW_V_OFFSET':
            materials_list[material_section][submat_nbr+'UVW_V_OFFSET'] = words[1]
        elif words[0] == '*UVW_U_TILING':
            materials_list[material_section][submat_nbr+'UVW_U_TILING'] = words[1]
        elif words[0] == '*UVW_V_TILING':
            materials_list[material_section][submat_nbr+'UVW_V_TILING'] = words[1]
        elif words[0] == '*UVW_ANGLE':
            materials_list[material_section][submat_nbr+'UVW_ANGLE'] = words[1]
        elif words[0] == '*UVW_BLUR':
            materials_list[material_section][submat_nbr+'UVW_BLUR'] = words[1]
        elif words[0] == '*UVW_BLUR_OFFSET':
            materials_list[material_section][submat_nbr+'UVW_BLUR_OFFSET'] = words[1]
        elif words[0] == '*UVW_NOUSE_AMT':
            materials_list[material_section][submat_nbr+'UVW_NOUSE_AMT'] = words[1]
        elif words[0] == '*UVW_NOISE_SIZE':
            materials_list[material_section][submat_nbr+'UVW_NOISE_SIZE'] = words[1]
        elif words[0] == '*UVW_NOISE_LEVEL':
            words1 = float(words[1])
            words1 = int(words1)
            materials_list[material_section][submat_nbr+'UVW_NOISE_LEVEL'] = str(words1)
        elif words[0] == '*UVW_NOISE_PHASE':
            materials_list[material_section][submat_nbr+'UVW_NOISE_PHASE'] = words[1]
        elif words[0] == '*BITMAP_FILTER':
            materials_list[material_section][submat_nbr+'BITMAP_FILTER'] = words[1]
        elif words[0] == '*MATERIAL_REF':
            newObj.material_ref = int(words[1])
            comp_specifics[newObj.name]['MATERIAL_REF'] = words[1]
        elif words[0] == '*GEOMOBJECT':
            objCheck = 0
            newObj = ase_obj() # Equivalent to a QuArK component.
            objects.append(newObj)
            obj = objects[objIdx]
            objIdx += 1
        elif words[0] == '*NODE_NAME' and objCheck != -1:
            if objCheck == 0:
                obj.name = words[1].replace('"', "")
                objCheck = 1
            elif objCheck == 1:
                obj.objName = words[1].replace('"', "")
                comp_specifics[newObj.name] = {}
                for key in scene_specifics.keys():
                    comp_specifics[newObj.name][key] = scene_specifics[key]
        elif words[0] == '*TM_ROW0' and objCheck != -1:
            obj.row0x = float(words[1])
            obj.row0y = float(words[2])
            obj.row0z = float(words[3])
        elif words[0] == '*TM_ROW1' and objCheck != -1:
            obj.row1x = float(words[1])
            obj.row1y = float(words[2])
            obj.row1z = float(words[3])
        elif words[0] == '*TM_ROW2' and objCheck != -1:
            obj.row2x = float(words[1])
            obj.row2y = float(words[2])
            obj.row2z = float(words[3])
        elif words[0] == '*TM_ROW3' and objCheck != -1:
            obj.row3x = float(words[1])
            obj.row3y = float(words[2])
            obj.row3z = float(words[3])
            objCheck = -1
        elif words[0] == '*MESH': # Each mesh is a component.
            obj.objType = 'Mesh'
            obj.obj = ase_mesh()
            me = obj.obj
        elif words[0] == '*MESH_NUMVERTEX': # Number of a mesh's vertexes.
            me.vCount = int(words[1])
        elif words[0] == '*MESH_NUMFACES': # Number of a mesh's faces\triangles.
            me.fCount = int(words[1])
        elif words[0] == '*MESH_VERTEX': # Each line is a frame's vertices x,y,z positions.
            v = mesh_vert()
            v.x = float(words[2])
            v.y = float(words[3])
            v.z = float(words[4])
            me.meVerts.append(v)
        elif words[0] == '*MESH_FACE': # Each line is a triangle's 3 vertex (MESH_VERTEX) indexes.
            f = mesh_face()
            f.v1 = int(words[3])
            f.v2 = int(words[5])
            f.v3 = int(words[7])
            me.meFaces.append(f)
        elif words[0] == '*MESH_NUMTVERTEX': # Number of a mesh's vertex's texture u,v values.
            me.uvVCount = int(words[1])
            if me.uvVCount > 0:
                me.hasFUV = 1
        elif words[0] == '*MESH_TVERT': # Each line is a vertex's texture u,v values as percentage of texture width and height.
            uv = mesh_uvVert()
            uv.index = int(words[1])
            uv.u = float(words[2])
            uv.v = float(words[3])
            me.uvVerts.append(uv)
        elif words[0] == '*MESH_NUMTVFACES': # Number of a mesh's triangles with vertex texture u,v indexes.
            me.uvFCount = int(words[1])
        elif words[0] == '*MESH_TFACE': # Each line is a triangle's 3 vertex texture u,v (MESH_TVERT) indexes.
            fUv = mesh_uvFace()
            fUv.index = int(words[1])
            fUv.uv1 = int(words[2])
            fUv.uv2 = int(words[3])
            fUv.uv3 = int(words[4])
            me.uvFaces.append(fUv)
        elif words[0] == '*MESH_NUMCVERTEX':
            me.vcVCount = int(words[1])
            if me.uvVCount > 0:
                me.hasVC = 1
        elif words[0] == '*MESH_VERTCOL':
            c = mesh_vcVert()
            c.index = int(words[1])
            c.r = round(float(words[2])*255)
            c.g = round(float(words[3])*255)
            c.b = round(float(words[4])*255)
            me.vcVerts.append(c)
        elif words[0] == '*MESH_CFACE':
            fc = mesh_vcFace()
            fc.index = int(words[1])
            fc.c1 = int(words[2])
            fc.c2 = int(words[3])
            fc.c3 = int(words[4])
            me.vcFaces.append(fc)
        elif words[0] == '*PROP_MOTIONBLUR':
            comp_specifics[newObj.name]['PROP_MOTIONBLUR'] = words[1]
        elif words[0] == '*PROP_CASTSHADOW':
            comp_specifics[newObj.name]['PROP_CASTSHADOW'] = words[1]
        elif words[0] == '*PROP_RECVSHADOW':
            comp_specifics[newObj.name]['PROP_RECVSHADOW'] = words[1]

        PBidx += 1.0
    ComponentList, message = spawn_main(objects, basepath, filename)

    return ComponentList, message

def spawn_main(objects, basepath, filename):

    PBidx = 0.0
    objCount = float(len(objects))


 #   Blender.Window.DrawProgressBar(0.0, "Importing Objects...")

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

    for obj in objects:

 #       Blender.Window.DrawProgressBar(PBidx / objCount, "Importing Objects...")

        if obj.objType == 'Mesh':
            ComponentList, message, CompNbr = spawn_mesh(obj, basepath, filename, ComponentList, message, CompNbr)

        PBidx += 1.0

    return ComponentList, message


def spawn_mesh(obj, basepath, filename, ComponentList, message, CompNbr):
    # obj = Equivalent to a QuArK component, a mesh.
    # basepath = The full path of the .ase file's location, up to and including the game folder with a forward slash,  / , at the end.
    # filename = The full path and name of the .ase file.

    # Sets up to look for the material shader to get all skin textures from.
    # The material shader name is the same as the location path and name of the file being imported (without .ase).
    material = filename.replace("\\", "/")
    material = material.replace(basepath, "")
    material = material.rsplit(".")[0]

    ### For the Skins:sg group.
    skinsize = (256, 256)
    skingroup = quarkx.newobj('Skins:sg')
    skingroup['type'] = chr(2)
    skinname = (material + '.tga')
    skin = quarkx.newobj(skinname)
    skinname = skinname.split('/')
    # First trys to find and load the primary texture (material) by name given in the .ase file
    # and in the materials_list by each component's ['MATERIAL_REF'] number and ['BITMAP'] key
    # along with all of that texture's dictspec specifics items for the skin dialog to use.
    if len(materials_list.keys()) != 0:
        gamefolder = basepath.split("/")
        gamefolder = gamefolder[len(gamefolder)-2]
        filefolder = filename.replace("\\", "/")
        filefolder = filefolder.split("/" + gamefolder + "/", 1)
        filefolder = filefolder[1]
        filefolder = filefolder.rsplit("/", 1)[0] + "/"
        possible_names = filename.rsplit("\\", 1)[1]
        possible_names = possible_names.split(".")[0]
        possible_names = possible_names.split("_")

        # Tries to find main one to load first based on model materials.
        # If not then goes through all the keys to find a texture material.
        if (materials_list[obj.material_ref]['MAT' + str(obj.material_ref) + '_' + 'BITMAP'] is not None) or (materials_list[obj.material_ref].has_key().startswith("SUB") and materials_list[obj.material_ref].has_key().endswith("BITMAP")):
            submat_key = None
            look4file = ""
            if (materials_list[obj.material_ref]['MAT' + str(obj.material_ref) + '_' + 'BITMAP'] is not None):
                try:
                    look4file = materials_list[obj.material_ref]['MAT' + str(obj.material_ref) + '_' + 'BITMAP'].split(gamefolder + "/", 1)[1]
                except:
                    try:
                        look4file = materials_list[obj.material_ref]['MAT' + str(obj.material_ref) + '_' + 'BITMAP'].split("../", 1)[1]
                    except:
                        pass
            else:
                for key in materials_list[obj.material_ref].keys():
                    if key.startswith("SUB") and key.endswith("BITMAP"):
                        look4file = materials_list[obj.material_ref][key].split(gamefolder + "/", 1)[1]
                        submat_key = key.split("_")[0]
                        materials_list[obj.material_ref][submat_key + "_PARENT"] = look4file
                        break
            file_type = "." + materials_list[obj.material_ref]['MAT' + str(obj.material_ref) + '_' + 'BITMAP'].rsplit(".", 1)[1]
            if (os.path.exists(basepath + look4file)) and (file_type in image_type_list):
                if not 'MAT' + str(obj.material_ref) + "/" + look4file in skingroup.dictitems.keys():
                    skin = quarkx.newobj('MAT' + str(obj.material_ref) + "/" + look4file)
                    image = quarkx.openfileobj(basepath + look4file)
                    skin['Image1'] = image.dictspec['Image1']
                    skin['Size'] = image.dictspec['Size']
                    if submat_key is not None:
                        subskin = skin.copy()
                        subskin.name = submat_key + "/" + subskin.name
                        for key in materials_list[obj.material_ref].keys():
                            if key.startswith(submat_key + "_"):
                                subskin[key] = materials_list[obj.material_ref][key]
                    for key in materials_list[obj.material_ref].keys():
                        if not key.startswith("SUB"):
                            skin[key] = materials_list[obj.material_ref][key]
                    skingroup.appenditem(skin)
                    skinsize = skin['Size']
                    if submat_key is not None:
                        skingroup.appenditem(subskin)
                        submat_key = None
                elif submat_key is not None:
                    subskin = quarkx.newobj(submat_key + "/" + look4file)
                    image = quarkx.openfileobj(basepath + look4file)
                    subskin['Image1'] = image.dictspec['Image1']
                    subskin['Size'] = image.dictspec['Size']
                    for key in materials_list[obj.material_ref].keys():
                        if key.startswith(submat_key + "_"):
                            subskin[key] = materials_list[obj.material_ref][key]
                    skingroup.appenditem(subskin)
                    submat_key = None
            else:
                if message == "":
                    message = message + "Trying to load skins in models material groups.\r\n"
                    if obj.objName != 'Name':
                        name = obj.objName.replace('"', "")
                        message = message + name + " needs the following skin textures\r\n"
                    else:
                        message = message + "Import Component " + str(CompNbr) + " needs the following skin textures\r\n"
                temppath = basepath
                message = message + (temppath.replace("\\", "/") + look4file + '\r\n')
        else:
            for key in materials_list.keys():
                if (materials_list[key]['MAT' + str(key) + '_' + 'BITMAP'] is not None) and (materials_list[key]['MAT' + str(key) + '_' + 'BITMAP'].find(filefolder) != -1):
                    look4file = materials_list[key]['MAT' + str(key) + '_' + 'BITMAP'].split(filefolder)[1]
                    for name in possible_names:
                        if not 'MAT' + str(key) + "/" + filefolder + look4file in skingroup.dictitems.keys() and look4file.find(name) != -1:
                            file_type = look4file.split(".")[1]
                            file_type = "." + file_type
                            if (os.path.exists(os.getcwd().replace("\\", "/") + "/" + look4file)) and (file_type in image_type_list):
                                skin = quarkx.newobj('MAT' + str(key) + "/" + filefolder + look4file)
                                image = quarkx.openfileobj(os.getcwd() + "\\" + look4file)
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                for key in materials_list[obj.material_ref].keys():
                                    skin[key] = materials_list[obj.material_ref][key]
                                skingroup.appenditem(skin)
                                skinsize = skin['Size']
                                break
                else: ### No material BITMAP AND no submaterial BITMAP...need to do something here for those ! ! !
                    pass
        # Now it loads all other textures that have a  ['BITMAP'] key that is not 'None'
        # along with all of that texture's dictspec specifics items for the skin dialog to use.
        for matkey in materials_list.keys():
            if (materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'] is not None):
                look4file = ""
                try:
                    look4file = materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'].split(gamefolder + "/", 1)[1]
                except:
                    try:
                        look4file = materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'].split("../", 1)[1]
                    except:
                        pass
                file_type = "." + materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'].rsplit(".", 1)[1]
                if (os.path.exists(basepath + look4file)) and (file_type in image_type_list):
                    if not 'MAT' + str(matkey) + "/" + look4file in skingroup.dictitems.keys():
                        skin = quarkx.newobj('MAT' + str(matkey) + "/" + look4file)
                        image = quarkx.openfileobj(basepath + look4file)
                        skin['Image1'] = image.dictspec['Image1']
                        skin['Size'] = image.dictspec['Size']
                        for key in materials_list[matkey].keys():
                            if not key.startswith("SUB"):
                                skin[key] = materials_list[matkey][key]
                        skingroup.appenditem(skin)
                        if len(skingroup.subitems) == 0:
                            for name in possible_names:
                                if look4file.find(name) != -1:
                                    skinsize = skin['Size']
                else:
                    if message == "":
                        message = message + "Trying to load skins in models material groups.\r\n"
                        if obj.objName != 'Name':
                            name = obj.objName.replace('"', "")
                            message = message + name + " needs the following skin textures\r\n"
                        else:
                            message = message + "Import Component " + str(CompNbr) + " needs the following skin textures\r\n"
                    temppath = basepath
                    message = message + (temppath.replace("\\", "/") + look4file + '\r\n')
            else:
                textures = []
                matkeys = materials_list[matkey].keys()
                matkeys.sort()
                for key in matkeys:
                    if key.startswith("SUB"):
                        submat_key = key.split("_")[0]
                        if materials_list[matkey][submat_key + '_BITMAP'] is not None:
                            look4file = materials_list[matkey][submat_key + '_BITMAP'].split(gamefolder + "/", 1)[1]
                            if materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'] is None:
                                materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'] = "MAT" + str(matkey) + "/" + look4file
                            if (os.path.exists(basepath + look4file)) and (file_type in image_type_list):
                                image = quarkx.openfileobj(basepath + look4file)
                                if not materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'] in skingroup.dictitems.keys():
                                    matskin = quarkx.newobj(materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP'])
                                    matskin['Image1'] = image.dictspec['Image1']
                                    matskin['Size'] = image.dictspec['Size']
                                    for mkey in materials_list[matkey].keys():
                                        if not mkey.startswith("SUB"):
                                            matskin[mkey] = materials_list[matkey][mkey]
                                    skingroup.appenditem(matskin)
                                    skinsize = matskin['Size']

                                subskinname = "MAT" + str(matkey) + "_" + submat_key + "/" + look4file
                                if not subskinname in skingroup.dictitems.keys():
                                    subskin = quarkx.newobj(subskinname)
                                    subimage = image.copy()
                                    subskin['Image1'] = subimage.dictspec['Image1']
                                    subskin['Size'] = subimage.dictspec['Size']
                                    materials_list[matkey][submat_key + '_PARENT'] = materials_list[matkey]['MAT' + str(matkey) + '_' + 'BITMAP']
                                    for skey in materials_list[matkey].keys():
                                        if skey.startswith(submat_key + "_"):
                                            subskin[skey] = materials_list[matkey][skey]
                                    skingroup.appenditem(subskin)
                            elif not look4file in textures: ### Can't find the skin file.
                                if message == "":
                                    message = message + "Trying to load skins in models material groups.\r\n"
                                    if obj.objName != 'Name':
                                        name = obj.objName.replace('"', "")
                                        message = message + name + " needs the following skin textures\r\n"
                                    else:
                                        message = message + "Import Component " + str(CompNbr) + " needs the following skin textures\r\n"
                                temppath = basepath
                                message = message + (temppath.replace("\\", "/") + look4file + '\r\n')
                                textures = textures + [look4file]
                        else: ### No material BITMAP AND no submaterial BITMAP...need to do something here for those ! ! !
                            pass

    if message != "":
        message = message + "================================\r\n"
    
    # Now it checks if the model has any shader textures specified with it
    # or any other textures if it does not use a shader file and trys to load those.
    foundshader = foundtexture = foundimage = imagefile = None
    mesh_shader = shader_file = shader_name = shader_keyword = qer_editorimage = diffusemap = map = bumpmap = addnormals = heightmap = specularmap = None
    if os.path.exists(basepath + "materials") == 1:
        shaderspath = basepath + "materials"
        shaderfiles = os.listdir(shaderspath)
        noimage = "No Shader Files Found."
        for shaderfile in shaderfiles:
            noimage = ""
            #read the file in
            try: # To by pass sub-folders, should make this to check those also.
                read_shader_file=open(shaderspath+"/"+shaderfile,"r")
            except:
                continue
            shaderlines=read_shader_file.readlines()
            read_shader_file.close()
            left_cur_braket = 0
            for line in range(len(shaderlines)):
                if foundshader is None and shaderlines[line].startswith(material+"\n"):
                    shaderline = shaderlines[line].replace(chr(9), "    ")
                    shaderline = shaderline.rstrip()
                    mesh_shader = "\r\n" + shaderline + "\r\n"
                    shader_file = shaderspath + "/" + shaderfile
                    shader_name = material
                    foundshader = material
                    left_cur_braket = 0
                    continue
                if foundshader is not None and shaderlines[line].find("{") != -1:
                    left_cur_braket = left_cur_braket + 1
                if foundshader is not None and shaderlines[line].find("}") != -1:
                    left_cur_braket = left_cur_braket - 1
                if foundshader is not None:
                    testline = shaderlines[line].strip()
                    if testline.startswith("//"):
                        continue
                    if shaderlines[line].find("qer_editorimage") != -1 or shaderlines[line].find("diffusemap") != -1:
                        words = shaderlines[line].split()
                        for word in words:
                            if word.endswith(".tga"):
                                foundtexture = word
                                if shaderlines[line].find("qer_editorimage") != -1:
                                    shader_keyword = "qer_editorimage"
                                else:
                                    shader_keyword = "diffusemap"
                                skinname = foundtexture
                                skin = quarkx.newobj(skinname)
                                break
                            elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")):
                                foundtexture = word + ".tga"
                                if shaderlines[line].find("qer_editorimage") != -1:
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
                                if (not skin.name in skingroup.dictitems.keys()) and (not skin.shortname in skingroup.dictitems.keys()):
                                    skin['Image1'] = image.dictspec['Image1']
                                    skin['Size'] = image.dictspec['Size']
                                    skin['shader_keyword'] = shader_keyword
                                    skingroup.appenditem(skin)
                                    if skinsize == (256, 256):
                                        skinsize = skin['Size']
                                    foundtexture = None
                                else:
                                    skingroup.dictitems[skin.name]['shader_keyword'] = shader_keyword
                                    foundtexture = None
                            else: # Keep looking in the shader files, the shader may be in another one.
                                imagefile = basepath + foundtexture
                                if obj.objName != 'Name':
                                    name = obj.objName.replace('"', "")
                                    noimage = noimage + "\r\nFound needed shader for " + name + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "and the 'diffusemap' image to display.\r\n    " + foundtexture + "\r\n" + "But that image file does not exist.\r\n"
                                else:
                                    noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "and the 'diffusemap' image to display.\r\n    " + foundtexture + "\r\n" + "But that image file does not exist.\r\n"
                    if shaderlines[line].find("bumpmap") != -1 and (not shaderlines[line].find("addnormals") != -1 and not shaderlines[line].find("heightmap") != -1):
                        words = shaderlines[line].replace("("," ")
                        words = words.replace(")"," ")
                        words = words.replace(","," ")
                        words = words.split()
                        for word in words:
                            if word.endswith(".tga"):
                                bumpmap = word
                            elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")):
                                bumpmap = word + ".tga"
                    if shaderlines[line].find("addnormals") != -1 or shaderlines[line].find("heightmap") != -1:
                        words = shaderlines[line].replace("("," ")
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
                    elif shaderlines[line].find("specularmap") != -1:
                        words = shaderlines[line].split()
                        for word in words:
                            if word.endswith(".tga"):
                                specularmap = word
                            elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")):
                                specularmap = word + ".tga"
                    # Dec character code for space = chr(32), for tab = chr(9)
                    elif shaderlines[line].find(chr(32)+"map") != -1 or shaderlines[line].find(chr(9)+"map") != -1:
                        words = shaderlines[line].split()
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
                                if obj.objName != 'Name':
                                    name = obj.objName.replace('"', "")
                                    noimage = noimage + "\r\nFound needed shader for " + name + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                                else:
                                    noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                        elif map is not None:
                            shader_keyword = "map"
                            skingroup.dictitems[map]['shader_keyword'] = shader_keyword
                    else:
                        if shaderlines[line].find("/") != -1:
                            if shaderlines[line-1].find("qer_editorimage") != -1 or shaderlines[line-1].find("diffusemap") != -1 or shaderlines[line-1].find("bumpmap") != -1 or shaderlines[line-1].find("addnormals") != -1 or shaderlines[line-1].find("heightmap") != -1 or shaderlines[line-1].find("specularmap") != -1 or shaderlines[line].find(chr(32)+"map") != -1 or shaderlines[line].find(chr(9)+"map") != -1:
                                words = shaderlines[line].replace("("," ")
                                words = words.replace(")"," ")
                                words = words.replace(","," ")
                                words = words.split()
                                image = imagename = None
                                for word in words:
                                    if word.endswith(".tga") and (word.startswith("models") or word.startswith("textures")) and ((not word.endswith("_dis.tga") and not word.endswith("_dis")) and (not word.endswith("dis2.tga") and not word.endswith("dis2"))):
                                        image = imagename = word
                                    elif word.find("/") != -1 and (word.startswith("models") or word.startswith("textures")) and ((not word.endswith("_dis.tga") and not word.endswith("_dis")) and (not word.endswith("dis2.tga") and not word.endswith("dis2"))):
                                        imagename = word
                                        image = word + ".tga"
                                if image is not None:
                                    words = shaderlines[line-1].replace("("," ")
                                    words = words.replace(")"," ")
                                    words = words.replace(","," ")
                                    words = words.split()
                                    keys = [qer_editorimage, diffusemap, bumpmap, addnormals, heightmap, specularmap, map]
                                    words.reverse() # Work our way backwards to get the last key name first.
                                    for word in range(len(words)):
                                        if words[word] in keys:
                                            shader_keyword = words[word]
                                            if (not skin.name in skingroup.dictitems.keys()) and (not skin.shortname in skingroup.dictitems.keys()):
                                                imagefile = basepath + image
                                                if os.path.isfile(basepath + image):
                                                    skinname = image
                                                    foundimage = basepath + skinname
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
                                                    if obj.objName != 'Name':
                                                        name = obj.objName.replace('"', "")
                                                        noimage = noimage + "\r\nFound needed shader for " + name + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                                                    else:
                                                        noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                                            else:
                                                if not skingroup.dictitems[skin.name].dictspec.has_key('shader_keyword') and skin.name == words[0]:
                                                    skingroup.dictitems[skin.name]['shader_keyword'] = shader_keyword
                                    
                    shaderline = shaderlines[line].replace(chr(9), "    ")
                    shaderline = shaderline.rstrip()
                    if mesh_shader is not None:
                        mesh_shader = mesh_shader + shaderline + "\r\n"
                    if shaderlines[line].find("}") != -1 and left_cur_braket == 0: # Done reading shader so break out of reading this file.
                        break
            if mesh_shader is not None:
                if bumpmap is not None:
                    shader_keyword = "bumpmap"
                    if not bumpmap in skingroup.dictitems.keys():
                        imagefile = basepath + bumpmap
                        if os.path.isfile(basepath + bumpmap):
                            skinname = bumpmap
                            foundimage = basepath + skinname
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
                            if obj.objName != 'Name':
                                name = obj.objName.replace('"', "")
                                noimage = noimage + "\r\nFound needed shader for " + name + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                    else:
                        skingroup.dictitems[bumpmap]['shader_keyword'] = shader_keyword
                if addnormals is not None:
                    shader_keyword = "addnormals"
                    if not addnormals in skingroup.dictitems.keys():
                        imagefile = basepath + addnormals
                        if os.path.isfile(basepath + addnormals):
                            skinname = addnormals
                            foundimage = basepath + skinname
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
                            if obj.objName != 'Name':
                                name = obj.objName.replace('"', "")
                                noimage = noimage + "\r\nFound needed shader for " + name + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                    else:
                        skingroup.dictitems[addnormals]['shader_keyword'] = shader_keyword
                if heightmap is not None:
                    shader_keyword = "heightmap"
                    if not heightmap in skingroup.dictitems.keys():
                        imagefile = basepath + heightmap
                        if os.path.isfile(basepath + heightmap):
                            skinname = heightmap
                            foundimage = basepath + skinname
                            # Make the skin and add it.
                            skin = quarkx.newobj(skinname)
                            image = quarkx.openfileobj(foundimage)
                            skin['Image1'] = image.dictspec['Image1']
                            skin['Size'] = image.dictspec['Size']
                            skin['shader_keyword'] = shader_keyword
                            if (not skin.name in skingroup.dictitems.keys()) and (not skin.shortname in skingroup.dictitems.keys()):
                                skingroup.appenditem(skin)
                                if skinsize == (256, 256):
                                    skinsize = skin['Size']
                        else:
                            if obj.objName != 'Name':
                                name = obj.objName.replace('"', "")
                                noimage = noimage + "\r\nFound needed shader for " + name + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                    else:
                        skingroup.dictitems[heightmap]['shader_keyword'] = shader_keyword
                if specularmap is not None:
                    shader_keyword = "specularmap"
                    if not specularmap in skingroup.dictitems.keys():
                        imagefile = basepath + specularmap
                        if os.path.isfile(basepath + specularmap):
                            skinname = specularmap
                            foundimage = basepath + skinname
                            # Make the skin and add it.
                            skin = quarkx.newobj(skinname)
                            if (not skin.name in skingroup.dictitems.keys()) and (not skin.shortname in skingroup.dictitems.keys()):
                                image = quarkx.openfileobj(foundimage)
                                skin['Image1'] = image.dictspec['Image1']
                                skin['Size'] = image.dictspec['Size']
                                skin['shader_keyword'] = shader_keyword
                                skingroup.appenditem(skin)
                                if skinsize == (256, 256):
                                    skinsize = skin['Size']
                        else:
                            if obj.objName != 'Name':
                                name = obj.objName.replace('"', "")
                                noimage = noimage + "\r\nFound needed shader for " + name + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + material + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                    else:
                        skingroup.dictitems[specularmap]['shader_keyword'] = shader_keyword
                if imagefile is None:
                    imagefile = "NO IMAGE FILE FOUND AT ALL, CHECK THE SHADER."
                break
            if foundshader is not None: # Found the shader so break out of the shader files loop.
                break
        if len(noimage) > 0:
            message = message + noimage
        if material is not None and foundshader is None: # This component has an image but no shader was found, so...
            texturepath = basepath + material + ".tga"
            if os.path.exists(texturepath) == 1: # May not be a shader so we look for a texture with the same image name.
                skinname = material + ".tga"
                if not skinname in skingroup.dictitems.keys():
                    skin = quarkx.newobj(skinname)
                    image = quarkx.openfileobj(texturepath)
                    skin['Image1'] = image.dictspec['Image1']
                    skin['Size'] = image.dictspec['Size']
                    for key in materials_list[obj.material_ref].keys():
                        skin[key] = materials_list[obj.material_ref][key]
                    skingroup.appenditem(skin)
                    if skinsize == (256, 256):
                        skinsize = skin['Size']
            elif material_0 is not None:
                trythis = material.rsplit("/", 1)
                trythis = trythis[0]
                texturepath = basepath + trythis + "/" + material_0
                if os.path.exists(texturepath) == 1: # May not be a shader so we look for a texture with the same image name.
                    skinname = trythis + "/" + material_0
                    if not skinname in skingroup.dictitems.keys():
                        skin = quarkx.newobj(skinname)
                        image = quarkx.openfileobj(texturepath)
                        skin['Image1'] = image.dictspec['Image1']
                        skin['Size'] = image.dictspec['Size']
                        for key in materials_list[obj.material_ref].keys():
                            skin[key] = materials_list[obj.material_ref][key]
                        skingroup.appenditem(skin)
                        if skinsize == (256, 256):
                            skinsize = skin['Size']
                        if obj.objName != 'Name':
                            name = obj.objName.replace('"', "")
                            message = message + "\r\n" + name + " calls for the shader:\r\n    " + material + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder if it exist\r\nor create a shader file if needed.\r\nSome textures were found and imported.\r\n"
                        else:
                            message = message + "\r\nImport Component " + str(CompNbr) + " calls for the shader:\r\n    " + material + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder if it exist\r\nor create a shader file if needed.\r\nSome textures were found and imported.\r\n"
                else: # If no texture is found then we are missing the shader.
                    if obj.objName != 'Name':
                        name = obj.objName.replace('"', "")
                        message = message + "\r\n" + name + " calls for the shader:\r\n    " + material + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder\r\nor create a shader file if needed.\r\n"
                    else:
                        message = message + "\r\nImport Component " + str(CompNbr) + " calls for the shader:\r\n    " + material + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder\r\nor create a shader file if needed.\r\n"
            else: # If no texture is found then we are missing the shader.
                if obj.objName != 'Name':
                    name = obj.objName.replace('"', "")
                    message = message + "\r\n" + name + " calls for the shader:\r\n    " + material + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder\r\nor create a shader file if needed.\r\n"
                else:
                    message = message + "\r\nImport Component " + str(CompNbr) + " calls for the shader:\r\n    " + material + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder\r\nor create a shader file if needed.\r\n"
        try:
            skinsize = skingroup.subitems[0].dictspec['Size']
        except:
            pass
    elif not skinname in skingroup.dictitems.keys():
        name_list = load_image(basepath, material)
        for file in range(len(name_list)):
            if os.path.exists(name_list[file]) == 1:
                image = quarkx.openfileobj(name_list[file])
                skin['Image1'] = image.dictspec['Image1']
                skin['Size'] = image.dictspec['Size']
                skingroup.appenditem(skin)
                skinsize = skin['Size']
                break

            if file == len(name_list)-1:
                if not os.path.exists(os.getcwd().replace("\\", "/") + "/" + skinname[len(skinname)-1]):
                    if message != "":
                        message = message + "================================\r\n"
                    temppath = basepath
                    if obj.objName != 'Name':
                        name = obj.objName.replace('"', "")
                        message = message + name + " needs the skin texture\r\n"
                    else:
                        message = message + "Import Component " + str(CompNbr) + " needs the skin texture\r\n"
                    message = message + (temppath.replace("\\", "/") + material + '\r\n')
                    message = message + "But the texture is not in that location.\r\n"
                    message = message + "Look for:\r\n"
                    message = message + ('    ' + material + '\r\n')
                else:
                    temppath = filename
                    temppath = temppath.replace(basepath, "")
                    temppath = temppath.split("\\")
                    curfolder = ""
                    for item in range(len(temppath)-1):
                        curfolder = curfolder + temppath[item] + "/"
                    skin = quarkx.newobj(curfolder + skinname[len(skinname)-1])
                    image = quarkx.openfileobj(os.getcwd() + "\\" + skinname[len(skinname)-1])
                    skin['Image1'] = image.dictspec['Image1']
                    skin['Size'] = image.dictspec['Size']
                    skingroup.appenditem(skin)
                    skinsize = skin['Size']

    ### For the Frames:fg group and each "name:mf" frame.
    framesgroup = quarkx.newobj('Frames:fg') # QuArK Frames group made here.

    # Because .ase models are "stagnat" models, (no animation), we only make 1 frame
    # which is used to draw the model's 'mesh' (shape) in the editor's views.
    # The Skin-view uses the model's 'Tris' to draw its lines. 
    frame = quarkx.newobj('baseframe:mf') # QuArK frame made here.
    comp_mesh = () # QuArK code

    objMe = obj.obj
    #normal_flag = 1

    row0 = obj.row0x, obj.row0y, obj.row0z
    row1 = obj.row1x, obj.row1y, obj.row1z
    row2 = obj.row2x, obj.row2y, obj.row2z
    row3 = obj.row3x, obj.row3y, obj.row3z 

 #   newMatrix = Blender.Mathutils.Matrix(row0, row1, row2, row3)

 #   newObj = Blender.Object.New(obj.objType, obj.name)
 #   newObj.setMatrix(newMatrix)
 #   Blender.Scene.getCurrent().link(newObj)


 #   newMesh = Blender.Mesh.New(obj.objName)
 #   newMesh.getFromObject(newObj.name)
    newMesh = quarkx.newobj(obj.objName + ':mf')


    # Verts
    for v in objMe.meVerts: # QuArK frame Vertices made here.
        comp_mesh = comp_mesh + (float(v.x), float(v.y), float(v.z))
    frame['Vertices'] = comp_mesh
    framesgroup.appenditem(frame)

    # Faces
    Tris = ''
    TexWidth, TexHeight = skinsize
    if objMe.hasVC == 1:
        if obj.objName != 'Name':
            comp_name = obj.objName.replace('"', "")
        else:
            comp_name = "Import Component " + str(CompNbr)
        comp_name = comp_name + ':mc'
        if not editor.ModelComponentList.has_key(comp_name):
            editor.ModelComponentList[comp_name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
            
    for f in range(len(objMe.meFaces)): # QuArK Tris made here.
        uv1 = (int(float(objMe.uvVerts[objMe.uvFaces[f].uv1].u)*TexWidth), TexHeight-(int(float(objMe.uvVerts[objMe.uvFaces[f].uv1].v)*TexHeight)))
        uv2 = (int(float(objMe.uvVerts[objMe.uvFaces[f].uv2].u)*TexWidth), TexHeight-(int(float(objMe.uvVerts[objMe.uvFaces[f].uv2].v)*TexHeight)))
        uv3 = (int(float(objMe.uvVerts[objMe.uvFaces[f].uv3].u)*TexWidth), TexHeight-(int(float(objMe.uvVerts[objMe.uvFaces[f].uv3].v)*TexHeight)))

        if objMe.hasVC == 1: # QuArK note: Makes up the editor.ModelComponentList[mesh.name]['colorvtxlist'] section for ['vtx_color'].
            try:
                c = objMe.vcFaces[f]
                v1r = int(objMe.vcVerts[c.c1].r)
                v1g = int(objMe.vcVerts[c.c1].g)
                v1b = int(objMe.vcVerts[c.c1].b)
                rgb1 = struct.pack('i', RGBToColor([v1r, v1g, v1b]))
                v2r = int(objMe.vcVerts[c.c2].r)
                v2g = int(objMe.vcVerts[c.c2].g)
                v2b = int(objMe.vcVerts[c.c2].b)
                rgb2 = struct.pack('i', RGBToColor([v2r, v2g, v2b]))
                v3r = int(objMe.vcVerts[c.c3].r)
                v3g = int(objMe.vcVerts[c.c3].g)
                v3b = int(objMe.vcVerts[c.c3].b)
                rgb3 = struct.pack('i', RGBToColor([v3r, v3g, v3b]))
                editor.ModelComponentList[comp_name]['colorvtxlist'][objMe.meFaces[f].v3] = {}
                editor.ModelComponentList[comp_name]['colorvtxlist'][objMe.meFaces[f].v3]['vtx_color'] = rgb3
                editor.ModelComponentList[comp_name]['colorvtxlist'][objMe.meFaces[f].v2] = {}
                editor.ModelComponentList[comp_name]['colorvtxlist'][objMe.meFaces[f].v2]['vtx_color'] = rgb2
                editor.ModelComponentList[comp_name]['colorvtxlist'][objMe.meFaces[f].v1] = {}
                editor.ModelComponentList[comp_name]['colorvtxlist'][objMe.meFaces[f].v1]['vtx_color'] = rgb1
            except:
                pass

        Tris = Tris + struct.pack("Hhh", objMe.meFaces[f].v3,uv3[0],uv3[1])
        Tris = Tris + struct.pack("Hhh", objMe.meFaces[f].v2,uv2[0],uv2[1])
        Tris = Tris + struct.pack("Hhh", objMe.meFaces[f].v1,uv1[0],uv1[1])
  #      newMesh.faces.extend(newMesh.verts[objMe.meFaces[f].v1], newMesh.verts[objMe.meFaces[f].v2], newMesh.verts[objMe.meFaces[f].v3])

    #VertCol
  #  if guiTable['VC'] == 1 and objMe.hasVC == 1: # QuArK note: Make up the editor.ModelComponentList[mesh.name]['boneobjlist'] section for ['color'].
      #  newMesh.vertexColors = 1
      #  for c in objMe.vcFaces:

        #    FCol0 = newMesh.faces[c.index].col[0]
        #    FCol1 = newMesh.faces[c.index].col[1]
        #    FCol2 = newMesh.faces[c.index].col[2]

        #    FCol0.r = int(objMe.vcVerts[c.c1].r)
        #    FCol0.g = int(objMe.vcVerts[c.c1].g)
        #    FCol0.b = int(objMe.vcVerts[c.c1].b)

        #    FCol1.r = int(objMe.vcVerts[c.c2].r)
        #    FCol1.g = int(objMe.vcVerts[c.c2].g)
        #    FCol1.b = int(objMe.vcVerts[c.c2].b)

        #    FCol2.r = int(objMe.vcVerts[c.c3].r)
        #    FCol2.g = int(objMe.vcVerts[c.c3].g)
        #    FCol2.b = int(objMe.vcVerts[c.c3].b)

    # UV
   # for f in objMe.uvFaces: # QuArK does NOT need this section, it is handled above, can be removed.
   #     uv1 = (float(objMe.uvVerts[f.uv1].u), float(objMe.uvVerts[f.uv1].v))
   #     uv2 = (float(objMe.uvVerts[f.uv2].u), float(objMe.uvVerts[f.uv2].v))
   #     uv3 = (float(objMe.uvVerts[f.uv3].u), float(objMe.uvVerts[f.uv3].v))
   #     print "line 757 uv1",uv1
   #     print "line 758 uv2",uv2
   #     print "line 759 uv3",uv3
 #   if guiTable['UV'] == 1 and objMe.hasFUV == 1:
 #       newMesh.faceUV = 1
 #       for f in objMe.uvFaces:
 #           uv1 = Blender.Mathutils.Vector(float(objMe.uvVerts[f.uv1].u), float(objMe.uvVerts[f.uv1].v))
 #           uv2 = Blender.Mathutils.Vector(float(objMe.uvVerts[f.uv2].u), float(objMe.uvVerts[f.uv2].v))
 #           uv3 = Blender.Mathutils.Vector(float(objMe.uvVerts[f.uv3].u), float(objMe.uvVerts[f.uv3].v))
 #           newMesh.faces[f.index].uv = [uv1, uv2, uv3]

 #   newMesh.transform((newObj.getMatrix('worldspace').invert()), 1)
 #   newObj.link(newMesh)

    counts['verts'] += objMe.vCount
    counts['tris'] += objMe.fCount

    # Sort the skingroup to group the sub-materials together (in correct order)
    sort_list = {}
    for skin in skingroup.subitems:
        if skin.name.startswith("MAT"):
            splitted_name = skin.name.split("/")[0].split("_SUB")
            mat_index = int(splitted_name[0].split("MAT")[1])
            if len(splitted_name) == 1:
                # Material itself
                if not sort_list.has_key(mat_index):
                    sort_list[mat_index] = {}
            else:
                sub_index = int(splitted_name[1])
                sort_list[mat_index][sub_index] = skin
    item_index = 0
    while (item_index < len(skingroup.subitems)):
        skin = skingroup.subitems[item_index]
        if skin.name.startswith("MAT"):
            item_index = item_index + 1 # Jump over the material itself
            mat_index = int(skin.name.split("/")[0].split("_SUB")[0].split("MAT")[1])
            sorted_sub_list = sort_list[mat_index].keys()
            sorted_sub_list.sort()
            for sub_item in sorted_sub_list:
                skingroup.removeitem(skingroup.subitems[item_index])
                skingroup.insertitem(item_index, sort_list[mat_index][sub_item].copy())
                item_index = item_index + 1
        else:
            item_index = item_index + 1

    # Now we start creating our Import Component and name it.
    if obj.objName != 'Name':
        name = obj.objName.replace('"', "")
        Component = quarkx.newobj(name + ':mc')
    else:
        Component = quarkx.newobj("Import Component " + str(CompNbr) + ':mc')
        CompNbr = CompNbr + 1
    if not editor.ModelComponentList.has_key(Component.name):
        editor.ModelComponentList[Component.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
    if shader_file is not None: # The path and name of the shader file.
        Component['shader_file'] = shader_file
    if shader_name is not None: # The name of the shader in the shader file.
        Component['shader_name'] = shader_name
    if mesh_shader is not None: # The actual text, to display, of the shader itself.
        Component['mesh_shader'] = mesh_shader
    Component['skinsize'] = skinsize
    Component['Tris'] = Tris
    Component['show'] = chr(1)
    # Adds all of the Component's Specifics page items to the Component.
    for key in comp_specifics[name].keys():
        Component[key] = comp_specifics[name][key]
    # Resets all submaterials ' PARENT'  to the parent's actual skin texture name.
  #  for objkey in materials_list.keys():
  #      for key in materials_list[objkey].keys():
  #          if key.startswith("SUB") and key.endswith("_PARENT"):
  #              skinnbr = materials_list[objkey][key]
  #              materials_list[objkey][key] = skingroup.subitems[skinnbr].name
    sdogroup = quarkx.newobj('SDO:sdo')
    Component.appenditem(sdogroup)
    Component.appenditem(skingroup)
    Component.appenditem(framesgroup)
    ComponentList = ComponentList + [Component]
 #   progressbar.close()
 #   if len(polynames) > 1:
 #       Strings[2454] = Strings[2454].replace("Processing Components " + firstcomp + " to " + lastcomp + "\n" + "Import Component " + str(CompNbr) + "\n\n", "")
 #   else:
 #       Strings[2454] = Strings[2454].replace("Import Component " + str(CompNbr) + "\n", "")

    return ComponentList, message, CompNbr



def read_ui(basepath, filename):
    global tobj, logging, importername, textlog

 #   global guiTable, IMPORT_VC, IMPORT_UV
 #   guiTable = {'VC': 1, 'UV': 1}

    logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

 #   for s in Window.GetScreenInfo():
 #       Window.QHandle(s['id'])

 #   IMPORT_VC = Draw.Create(guiTable['VC'])
 #   IMPORT_UV = Draw.Create(guiTable['UV'])

    # Get USER Options
 #   pup_block = [('Import Options'),('Vertex Color', IMPORT_VC, 'Import Vertex Colors if exist'),('UV', IMPORT_UV, 'Import UV if exist'),]

 #   if not Draw.PupBlock('Import...', pup_block):
 #       return

 #   Window.WaitCursor(1)

 #   guiTable['VC'] = IMPORT_VC.val
 #   guiTable['UV'] = IMPORT_UV.val

    ComponentList, message = read_main(file, basepath, filename)

    if ComponentList == []:
        if logging == 1:
            tobj.logcon ("Can't read file %s" %filename)
        return [None, None, ""]

    ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.

    ### Use the 'ModelRoot' below to test opening the QuArK's Model Editor with, needs to be qualified with main menu item.
    ModelRoot = quarkx.newobj('Model:mr')
  #  ModelRoot.appenditem(Component)

    return ModelRoot, ComponentList, message


def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename is the full path and name of the .ase file selected."
    "gamename is None."
    "For example:  C:\Doom 3\base\models\mapobjects\washroom\toilet.ase"

    global editor, basepath
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
    try:
        basepath = basepath.replace("\\", "/")
    except:
        return
    if basepath is None:
        return

    ### Line below just runs the importer without the editor being open.
    ### Need to figure out how to open the editor with it & complete the ModelRoot.
  #  import_md2_model(editor, filename)

    ### Lines below here loads the model into the opened editor's current model.
    ModelRoot, ComponentList, message = read_ui(basepath, filename)

    if ModelRoot is None or ComponentList is None or ComponentList == []:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        quarkx.msgbox("Invalid .ase model.\nEditor can not import it.", MT_ERROR, MB_OK)
        return

    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        md2fileobj = quarkx.newfileobj("New model.md2")
        md2fileobj['FileName'] = 'New model.qkl'
        for Component in ComponentList:
            editor.Root.appenditem(Component)
        md2fileobj['Root'] = editor.Root.name
        md2fileobj.appenditem(editor.Root)
        md2fileobj.openinnewwindow()
    else: # Imports a model properly from within the editor.
        undo = quarkx.action()
        for Component in ComponentList:
            undo.put(editor.Root, Component)
            editor.Root.currentcomponent = Component
            if len(Component.dictitems['Skins:sg'].subitems) != 0:
                editor.Root.currentcomponent.currentskin = Component.dictitems['Skins:sg'].subitems[0] # To try and set to the correct skin.
                quarkpy.mdlutils.Update_Skin_View(editor, 2) # Sends the Skin-view for updating and center the texture in the view.
            else:
                editor.Root.currentcomponent.currentskin = None
                
            compframes = editor.Root.currentcomponent.findallsubitems("", ':mf')   # get all frames
            for compframe in compframes:
                compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.

            # This needs to be done for each component or bones will not work if used in the editor.
            quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
        editor.ok(undo, str(len(ComponentList)) + " .ase Components imported")

        editor = None   #Reset the global again
        if message != "":
            message = message + "================================\r\n\r\n"
            message = message + "You need to find and supply the proper texture(s) and folder(s) above.\r\n"
            message = message + "Extract the folder(s) and file(s) to the 'game' folder.\r\n\r\n"
            message = message + "If a texture does not exist it may be a .dds or some other type of image file.\r\n"
            message = message + "If so then you need to make a .tga file copy of that texture, perhaps in PaintShop Pro.\r\n\r\n"
            message = message + "You may also need to rename it to match the exact name above.\r\n"
            message = message + "Either case, it would be for editing purposes only and should be placed in the model's folder.\r\n\r\n"
            message = message + "Once this is done, then delete the imported components and re-import the model."
            quarkx.textbox("WARNING", "Missing Skin Textures:\r\n\r\n================================\r\n" + message, MT_WARNING)

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_ASE_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".ase Importer", ".ase file", "*.ase", loadmodel, ie_ASE_import)



def dataformname(o):
    "Returns the data form for this type of object 'o' (a model component & others) to use for the Specific/Args page."
    import quarkpy.mdlentities # Used further down in a couple of places.

    DummyItem = o
    while (DummyItem.type != ":mc"): # Gets the object's model component.
        DummyItem = DummyItem.parent
    comp = DummyItem

    # Next line calls for the Shader Module in mdlentities.py to be used.
    external_skin_editor_dialog_plugin = quarkpy.mdlentities.UseExternalSkinEditor()

    # Next line calls for the Vertex U,V Color Module in mdlentities.py to be used.
    vtx_UVcolor_dialog_plugin = quarkpy.mdlentities.UseVertexUVColors()

    # Next line calls for the Vertex Weights Specifics Module in mdlentities.py to be used.
    vertex_weights_specifics_plugin = quarkpy.mdlentities.UseVertexWeightsSpecifics()

    # Next line calls for the Shader Module in mdlentities.py to be used.
    Shader_dialog_plugin = quarkpy.mdlentities.UseShaders()

    from quarkpy.qeditor import ico_dict # Get the dictionary list of all icon image files available.
    import quarkpy.qtoolbar              # Get the toolbar functions to make the button with.
    editor = quarkpy.mdleditor.mdleditor # Get the editor.
    ico_mdlskv = ico_dict['ico_mdlskv']  # Just to shorten our call later.
    icon_btns = {}                       # Setup our button list, as a dictionary list, to return at the end.
    # Next line calls for the Vertex Weights system in mdlentities.py to be used.
    vtxweightsbtn = quarkpy.qtoolbar.button(quarkpy.mdlentities.UseVertexWeights, "Open or Update\nVertex Weights Dialog||When clicked, this button opens the dialog to allow the 'weight' movement setting of single vertexes that have been assigned to more then one bone handle.\n\nClick the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
    vtxweightsbtn.state = quarkpy.qtoolbar.normal
    vtxweightsbtn.caption = "" # Texts shows next to button and keeps the width of this button so it doesn't change.
    icon_btns['vtxweights'] = vtxweightsbtn   # Put our button in the above list to return.

    if (editor.Root.currentcomponent.currentskin is not None) and (o.name == editor.Root.currentcomponent.currentskin.name): # If this is not done it will cause looping through multiple times.
        if o.parent.parent.dictspec.has_key("shader_keyword") and o.dictspec.has_key("shader_keyword"):
            if o.parent.parent.dictspec['shader_keyword'] != o.dictspec['shader_keyword']:
                o.parent.parent['shader_keyword'] = o.dictspec['shader_keyword']

    # This section just for o objects that are skin textures.
    if o.type.startswith("."):

        subnbr = ""
        if o.name.find("SUB") != -1:
            subnbr = o.name.split("/")[0]
            subnbr = subnbr.split("SUB")
            if len(subnbr) > 1:
                subnbr = "SUB" + subnbr[1] + "_"
            else:
                subnbr = "SUB" + subnbr[0] + "_"
        elif o.name.startswith("MAT"):
            subnbr = o.name.split("/")[0] + "_"

        if not comp.dictspec.has_key('mesh_shader'):
            o['mesh_shader'] = "None"
        else:
            o['mesh_shader'] = comp.dictspec['mesh_shader']
        # Material Identifiers section.
        if not o.dictspec.has_key(subnbr + 'MATERIAL_NAME'):
            o[subnbr + 'MATERIAL_NAME'] = "None"
        if not o.dictspec.has_key(subnbr + 'MATERIAL_CLASS'):
            o[subnbr + 'MATERIAL_CLASS'] = "Standard"
        if not o.dictspec.has_key(subnbr + 'MATERIAL_SHINE'):
            o[subnbr + 'MATERIAL_SHINE'] = str(0.00)
        if o.dictspec.has_key(subnbr + 'MATERIAL_SHINE'):
            vtxkey =  float(o.dictspec[subnbr + 'MATERIAL_SHINE'])
            if vtxkey > 1:
                vtxkey = round(vtxkey,2) - 0.95
            elif vtxkey == 1:
                vtxkey = 0.05
            elif vtxkey == 0:
                vtxkey = 0.00
            elif vtxkey == -1.0:
                vtxkey = 0.00
            elif vtxkey < 0:
                vtxkey = round(vtxkey,2) + 0.95
            if vtxkey >= 0.95:
                vtxkey = 0.95
            elif vtxkey <= 0.00:
                vtxkey = 0.00
            o[subnbr + 'MATERIAL_SHINE'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'MATERIAL_SHINESTRENGTH'):
            o[subnbr + 'MATERIAL_SHINESTRENGTH'] = str(0.00)
        if o.dictspec.has_key(subnbr + 'MATERIAL_SHINESTRENGTH'):
            vtxkey =  float(o.dictspec[subnbr + 'MATERIAL_SHINESTRENGTH'])
            if vtxkey > 1:
                vtxkey = round(vtxkey,2) - 0.95
            elif vtxkey == 1:
                vtxkey = 0.05
            elif vtxkey == 0:
                vtxkey = 0.00
            elif vtxkey == -1.0:
                vtxkey = 0.00
            elif vtxkey < 0:
                vtxkey = round(vtxkey,2) + 0.95
            if vtxkey >= 0.95:
                vtxkey = 0.95
            elif vtxkey <= 0.00:
                vtxkey = 0.00
            o[subnbr + 'MATERIAL_SHINESTRENGTH'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'MATERIAL_TRANSPARENCY'):
            o[subnbr + 'MATERIAL_TRANSPARENCY'] = str(0.00)
        if o.dictspec.has_key(subnbr + 'MATERIAL_TRANSPARENCY'):
            vtxkey =  float(o.dictspec[subnbr + 'MATERIAL_TRANSPARENCY'])
            if vtxkey > 1:
                vtxkey = round(vtxkey,2) - 0.95
            elif vtxkey == 1:
                vtxkey = 0.05
            elif vtxkey == 0:
                vtxkey = 0.00
            elif vtxkey == -1.0:
                vtxkey = 0.00
            elif vtxkey < 0:
                vtxkey = round(vtxkey,2) + 0.95
            if vtxkey >= 0.95:
                vtxkey = 0.95
            elif vtxkey <= 0.00:
                vtxkey = 0.00
            o[subnbr + 'MATERIAL_TRANSPARENCY'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'MATERIAL_WIRESIZE'):
            o[subnbr + 'MATERIAL_WIRESIZE'] = str(1.00)
        if o.dictspec.has_key(subnbr + 'MATERIAL_WIRESIZE'):
            vtxkey =  float(o.dictspec[subnbr + 'MATERIAL_WIRESIZE'])
            if vtxkey <= 1.00:
                vtxkey = 1.00
            o[subnbr + 'MATERIAL_WIRESIZE'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'MATERIAL_SHADING'):
            o[subnbr + 'MATERIAL_SHADING'] = "None"
        if not o.dictspec.has_key(subnbr + 'MATERIAL_XP_FALLOFF'):
            o[subnbr + 'MATERIAL_XP_FALLOFF'] = str(0.00)
        if o.dictspec.has_key(subnbr + 'MATERIAL_XP_FALLOFF'):
            vtxkey =  float(o.dictspec[subnbr + 'MATERIAL_XP_FALLOFF'])
            if vtxkey > 1:
                vtxkey = round(vtxkey,2) - 0.95
            elif vtxkey == 1:
                vtxkey = 0.05
            elif vtxkey == 0:
                vtxkey = 0.00
            elif vtxkey == -1.0:
                vtxkey = 0.00
            elif vtxkey < 0:
                vtxkey = round(vtxkey,2) + 0.95
            if vtxkey >= 0.95:
                vtxkey = 0.95
            elif vtxkey <= 0.00:
                vtxkey = 0.00
            o[subnbr + 'MATERIAL_XP_FALLOFF'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'MATERIAL_XP_TYPE'):
            o[subnbr + 'MATERIAL_XP_TYPE'] = "None"
        if not o.dictspec.has_key(subnbr + 'MATERIAL_SELFILLUM'):
            o[subnbr + 'MATERIAL_SELFILLUM'] = str(0.00)
        if o.dictspec.has_key(subnbr + 'MATERIAL_SELFILLUM'):
            vtxkey =  float(o.dictspec[subnbr + 'MATERIAL_SELFILLUM'])
            if vtxkey > 1:
                vtxkey = round(vtxkey,2) - 0.95
            elif vtxkey == 1:
                vtxkey = 0.05
            elif vtxkey == 0:
                vtxkey = 0.00
            elif vtxkey == -1.0:
                vtxkey = 0.00
            elif vtxkey < 0:
                vtxkey = round(vtxkey,2) + 0.95
            if vtxkey >= 0.95:
                vtxkey = 0.95
            elif vtxkey <= 0.00:
                vtxkey = 0.00
            o[subnbr + 'MATERIAL_SELFILLUM'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'MATERIAL_FALLOFF'):
            o[subnbr + 'MATERIAL_FALLOFF'] = "None"
        # Map Identifiers section.
        if not o.dictspec.has_key(subnbr + 'MAP_NAME'):
            o[subnbr + 'MAP_NAME'] = "None"
        if not o.dictspec.has_key(subnbr + 'MAP_CLASS'):
            o[subnbr + 'MAP_CLASS'] = "Bitmap"
        if not o.dictspec.has_key(subnbr + 'MAP_SUBNO'):
            o[subnbr + 'MAP_SUBNO'] = "1"
        if not o.dictspec.has_key(subnbr + 'MAP_AMOUNT'):
            o[subnbr + 'MAP_AMOUNT'] = "1.0000"
        try:
            gamefolder = basepath.split("/")
            gamefolder = gamefolder[len(gamefolder)-2]
            if o.name.startswith("MAT"):
                o[subnbr + 'BITMAP'] = '/' + gamefolder + '/' + o.name.split("/", 1)[1]
            else:
                o[subnbr + 'BITMAP'] = '/' + gamefolder + '/' + o.name
        except:
            if o.name.startswith("MAT"):
                o[subnbr + 'BITMAP'] = '/base/' + o.name.split("/", 1)[1]
            else:
                o[subnbr + 'BITMAP'] = '/base/' + o.name
        if not o.dictspec.has_key(subnbr + 'MAP_TYPE'):
            o[subnbr + 'MAP_TYPE'] = "Screen"
        if not o.dictspec.has_key(subnbr + 'UVW_U_OFFSET'):
            o[subnbr + 'UVW_U_OFFSET'] = str(0.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_U_OFFSET'])
            o[subnbr + 'UVW_U_OFFSET'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_V_OFFSET'):
            o[subnbr + 'UVW_V_OFFSET'] = str(0.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_V_OFFSET'])
            o[subnbr + 'UVW_V_OFFSET'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_U_TILING'):
            o[subnbr + 'UVW_U_TILING'] = str(1.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_U_TILING'])
            o[subnbr + 'UVW_U_TILING'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_V_TILING'):
            o[subnbr + 'UVW_V_TILING'] = str(1.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_V_TILING'])
            o[subnbr + 'UVW_V_TILING'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_ANGLE'):
            o[subnbr + 'UVW_ANGLE'] = str(0.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_ANGLE'])
            o[subnbr + 'UVW_ANGLE'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_BLUR'):
            o[subnbr + 'UVW_BLUR'] = str(1.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_BLUR'])
            o[subnbr + 'UVW_BLUR'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_BLUR_OFFSET'):
            o[subnbr + 'UVW_BLUR_OFFSET'] = str(0.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_BLUR_OFFSET'])
            o[subnbr + 'UVW_BLUR_OFFSET'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_NOUSE_AMT'):
            o[subnbr + 'UVW_NOUSE_AMT'] = str(1.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_NOUSE_AMT'])
            o[subnbr + 'UVW_NOUSE_AMT'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_NOISE_SIZE'):
            o[subnbr + 'UVW_NOISE_SIZE'] = str(1.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_NOISE_SIZE'])
            o[subnbr + 'UVW_NOISE_SIZE'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'UVW_NOISE_LEVEL'):
            o[subnbr + 'UVW_NOISE_LEVEL'] = "1"
        if not o.dictspec.has_key(subnbr + 'UVW_NOISE_PHASE'):
            o[subnbr + 'UVW_NOISE_PHASE'] = str(0.00)
        else:
            vtxkey =  float(o.dictspec[subnbr + 'UVW_NOISE_PHASE'])
            o[subnbr + 'UVW_NOISE_PHASE'] = str(vtxkey)
        if not o.dictspec.has_key(subnbr + 'BITMAP_FILTER'):
            o[subnbr + 'BITMAP_FILTER'] = "Pyramidal"

        # This section just for o objects that are skin textures.
        def usesubmaterial(o=o, editor=editor, subnbr=subnbr):
            if not o.type.startswith("."):
                return """ """

            submatial = subnbr + """MATERIAL_CLASS: = {Typ="E R"   Txt="MATERIAL CLASS"   Hint="Type of the material."$0D"'Standard' denotes a material with no submaterials,"$0D"and a submaterial can not have other submaterials."$0D"'Multi/Sub-Object' is available for use when submaterials can be assigned to a material."$0D"Ignored by UnrealEd."}"""
            insertbefore = None
            for skin in range(len(editor.Root.currentcomponent.dictitems['Skins:sg'].subitems)):
                if skin == len(editor.Root.currentcomponent.dictitems['Skins:sg'].subitems)-1:
                    break
                if editor.Root.currentcomponent.dictitems['Skins:sg'].subitems[skin].name == o.name:
                    insertbefore = editor.Root.currentcomponent.dictitems['Skins:sg'].subitems[skin + 1]
                    break
            if not o.name.find("SUB") != -1:
                nbr = -1
                name = o.name
                matnbr = ""
                if o.name.startswith("MAT"):
                    matnbr = o.name.split("/")[0]
                for key in editor.Root.currentcomponent.dictitems['Skins:sg'].dictitems.keys():
                    if key.find("SUB") != -1:
                        if key.find(matnbr) != -1:
                            skin_name = key.split("/")[0]
                            skin_name = skin_name.split("SUB")
                            if len(skin_name) == 1:
                                skin_name = int(skin_name)
                            else:
                                skin_name = int(skin_name[1])
                            if skin_name > nbr:
                                nbr = skin_name
                                name = key
                for skin in range(len(editor.Root.currentcomponent.dictitems['Skins:sg'].subitems)):
                    if skin == len(editor.Root.currentcomponent.dictitems['Skins:sg'].subitems)-1:
                        break
                    if editor.Root.currentcomponent.dictitems['Skins:sg'].subitems[skin].name == name:
                        name = editor.Root.currentcomponent.dictitems['Skins:sg'].subitems[skin + 1].name
                        insertbefore = editor.Root.currentcomponent.dictitems['Skins:sg'].dictitems[name]
                        break
                nbr = nbr + 1

                if o.dictspec.has_key(subnbr + "MATERIAL_CLASS") and o.dictspec[subnbr + 'MATERIAL_CLASS'] == "Standard":
                    submatial = subnbr + """MATERIAL_CLASS: = {Typ="CL"   Txt="MATERIAL CLASS"   Hint="Type of the material."$0D"'Standard' denotes a material with no submaterials,"$0D"'Multi/Sub-Object' is set to enable a button to assign submaterials to a material."$0D"Ignored by UnrealEd."   items = "Standard"$0D "Multi/Sub-Object"   values = "Standard"$0D "Multi/Sub-Object"}"""
                elif o.dictspec.has_key(subnbr + "MATERIAL_CLASS"):
                    submatial = subnbr + """MATERIAL_CLASS: = {Typ="CL"   Txt="MATERIAL CLASS"   Hint="Type of the material."$0D"'Standard' denotes a material with no submaterials,"$0D"'Multi/Sub-Object' is set to enable a button to assign submaterials to a material."$0D"Ignored by UnrealEd."   items = "Standard"$0D "Multi/Sub-Object"   values = "Standard"$0D "Multi/Sub-Object"}
                      NEWSUBMATERIAL: = {t_ModelEditor_texturebrowser = ! Txt = "new submaterial """ + str(nbr) + '"' + """    Hint="Select a skin texture image file"$0D"to import and add to this group."$0D"Will not add a skin with duplicate names."$0D"UnrealEd looks for a texture by this name."}
                      """

                if (editor.Root.currentcomponent.currentskin is not None) and (o.name == editor.Root.currentcomponent.currentskin.name): # If this is not done it will cause looping through multiple times.
                    if (o.dictspec.has_key("NEWSUBMATERIAL")) and (o.dictspec['NEWSUBMATERIAL'] != o.name) and (not subnbr + o.dictspec['NEWSUBMATERIAL'] in o.parent.parent.dictitems['Skins:sg'].dictitems.keys()):
                        subnbr = "SUB" + str(nbr)
                        submatnbr = subnbr
                        if o.name.startswith("MAT"):
                            matname = o.name.split("/")[0] + "_"
                            subnbr = matname + subnbr
                        # Gives the newly selected skin texture's game folders path and file name, for example:
                        #     models/monsters/cacodemon/cacoeye.tga
                        skinname = subnbr + "/" + o.dictspec['NEWSUBMATERIAL']
                        o['NEWSUBMATERIAL'] = ""
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
                        skin[submatnbr + '_PARENT'] = o.name
                        skingroup = o.parent.parent.dictitems['Skins:sg']
                        undo = quarkx.action()
                        undo.put(skingroup, skin, insertbefore)
                        editor.ok(undo, o.parent.parent.shortname + " - " + "new skin added")
                        editor.Root.currentcomponent.currentskin = skin
                        editor.layout.explorer.sellist = [editor.Root.currentcomponent.currentskin]
                        quarkpy.mdlutils.Update_Skin_View(editor, 2)
            return submatial

        def_skin_dlgdef = """
        {
          Help = "These are the Specific settings for .ase model's skins (materials)."$0D
                 "ASE uses 'meshes' the same way that QuArK uses 'components'."$0D
                 "Each has its own special MATERIAL (or skin texture) settings."$0D0D
                 "NOTE: Some games do NOT allow 'TEXTURE TILING' for MODELS, only for SCENES."$0D
                 "            Meaning spreading the model faces over repeated image areas of a texture."$0D0D22
                 "edit skin"$22" - Opens this skin texture in an external editor."$0D0D
                 "Material Identifiers - (Settings for the exported model file)"$0D
                 "           Settings that effect the actual skin texture, material, of objects in the file."$0D22
                 "MATERIAL NAME"$22" - Name of the material."$0D22
                 "MATERIAL CLASS"$22" - Type of the material."$0D
                 "          'Standard' denotes a material with no submaterials,"$0D
                 "           and a submaterial and not have other submaterials."$0D
                 "          'Multi/Sub-Object' is set when there are submaterials assigned to a material."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "ambient color"$22" - Ambient glow of this material."$0D
                 "          This is not shown in QuArK at this time."$0D22
                 "diffuse color"$22" - Diffuse color of this material."$0D
                 "          This is not shown in QuArK at this time."$0D22
                 "specular color"$22" - Specular highlight color of this material."$0D
                 "          This is not shown in QuArK at this time."$0D22
                 "specular shine"$22" - Defines how focused the specular shine is."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "shine strength"$22" - Defines the strength of the specular shine is."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "transparency"$22" - The transparency of the material represented as a float from 0 to 1."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "wire size"$22" - The pixel width that wires should draw when viewed as wire frame mode."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "shading"$22" - Shading algorithm to use. Observed values are Blinn and Phong (without quotes)."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "expon. falloff"$22" - The exponential falloff of lighting."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "expon. type"$22" - Unknown. Only observed exponential value is 'Filter' (whout quotes)."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "selfillum"$22" - Unknown, presumed to be some sort of ambient glow."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "mat. falloff"$22" - Unknown. Only observed value is 'In' (without quotes)."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D0D
                 "Map Identifiers - (Settings for the exported model file)"$0D
                 "           Settings that effect the actual map of objects in the file."$0D22
                 "map name"$22" - Unknown. The name of this texture map for display in the editor."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "map class"$22" - Unknown, Observed value is 'Bitmap' (with the quotes)."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "map subno"$22" - Unknown. Observed value is 1."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "map amount"$22" - Unknown."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "bitmap"$22" - Name and path of the material. UnrealEd looks for a texture by this name."$0D
                 "           This is not shown in QuArK at this time."$0D22
                 "map type"$22" - Unknown, Observed value is 'Screen' (without quotes)."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw u offset"$22" - Offset value for texture horizontal position."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw v offset"$22" - Offset value for texture vertical position."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw u tiling"$22" - Texture tiling horizontal position."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw v tiling"$22" - Texture tiling vertical position."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw angle"$22" - Texture angle position."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw blur"$22" - Texture blurring value."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw blur offset"$22" - Texture blurring offset."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw nouse amount"$22" - Texture no use amount."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw noise size"$22" - Texture noise size."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw noise level"$22" - Unknown. Observed value is 1."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "uvw noise phase"$22" - Texture noise phase."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
                 "bitmap filter"$22" - Unknown, presumed to be filter for generating MIP Maps."$0D
                 "           Only observed value is 'Pyramidal' (without the quotes)."$0D
                 "           Ignored by UnrealEd. This is not shown in QuArK at this time."
          """ + external_skin_editor_dialog_plugin + """
          """ + Shader_dialog_plugin + """
          sep: = {Typ = "S"   Txt = "" }
          Sep: = {Typ = "S"   Txt = "Material Identifiers"  Hint="(Settings for the exported model file)"$0D"Settings that effect the actual skin texture, material, of objects in the file."}
          """ + subnbr + """MATERIAL_NAME:         = {Typ="E"    Txt="MATERIAL NAME"    Hint="Name of the material."$0D"UnrealEd may look for a texture by this name,"$0D"but it has not been tested."$0D0D"NOTE: Some games do NOT allow 'TEXTURE TILING'"$0D"for MODELS, only for SCENES."$0D"Meaning spreading the model faces over"$0D"repeated image areas of a texture."}
          """ + usesubmaterial() + """
          """ + subnbr + """MATERIAL_AMBIENT:      = {Typ="LI"   Txt="ambient color"    Hint="Ambient glow of this material."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_DIFFUSE:      = {Typ="LI"   Txt="diffuse color"    Hint="Diffuse color of this material."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_SPECULAR:     = {Typ="LI"   Txt="specular color"   Hint="Specular highlight color of this material."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_SHINE:        = {Typ="EU"   Txt="specular shine"   Hint="Defines how focused the specular shine is."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_SHINESTRENGTH:= {Typ="EU"   Txt="shine strength"   Hint="Defines the strength of the specular shine is."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_TRANSPARENCY: = {Typ="EU"   Txt="transparency"     Hint="The transparency of the material represented as a float from 0 to 1."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_WIRESIZE:     = {Typ="EU"   Txt="wire size"        Hint="The pixel width that wires should draw when viewed as wire frame mode."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_SHADING:      = {Typ="CL"   Txt="shading"          Hint="Shading algorithm to use. Observed values are Blinn and Phong (without quotes)."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."    items = "None"$0D "Blinn"$0D "Phong"    values = "None"$0D "Blinn"$0D "Phong"}
          """ + subnbr + """MATERIAL_XP_FALLOFF:   = {Typ="EU"   Txt="expon. falloff"   Hint="The exponential falloff of lighting."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_XP_TYPE:      = {Typ="CL"   Txt="expon. type"      Hint="Unknown. Only observed exponential value is 'Filter' (whout quotes)."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."   items = "None"$0D "Filter"   values = "None"$0D "Filter"}
          """ + subnbr + """MATERIAL_SELFILLUM:    = {Typ="EU"   Txt="selfillum"        Hint="Unknown, presumed to be some sort of ambient glow."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MATERIAL_FALLOFF:      = {Typ="CL"   Txt="mat. falloff"     Hint="Unknown. Only observed value is 'In' (without quotes)."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "None"$0D "In"       values = "None"$0D "In"}
          sep: = {Typ = "S"   Txt = "" }
          Sep: = {Typ = "S"   Txt = "Map Identifiers"  Hint="(Settings for the exported model file)"$0D"Settings that effect the actual map of objects in the file."}
          """ + subnbr + """MAP_NAME:              = {Typ="E"    Txt="map name"         Hint="The name of this texture map for display in the editor."$0D"UnrealEd looks for a texture by this name."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MAP_CLASS:             = {Typ="CL"   Txt="map class"        Hint="Unknown, Observed value is 'Bitmap' (with the quotes)."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "None"$0D "Bitmap"       values = "None"$0D "Bitmap"}
          """ + subnbr + """MAP_SUBNO:             = {Typ="CL"   Txt="map subno"        Hint="Unknown. Observed value is 1."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "0"$0D "1"       values = "0"$0D "1"}
          """ + subnbr + """MAP_AMOUNT:            = {Typ="CL"   Txt="map amount"       Hint="Unknown. Observed value is 1.0."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "0.0000"$0D "1.0000"       values = "0.0000"$0D "1.0000"}
          """ + subnbr + """BITMAP:                = {Typ="E R"  Txt="bitmap"           Hint="Name and path of the material."$0D"UnrealEd looks for a texture by this name."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """MAP_TYPE:              = {Typ="CL"   Txt="map type"         Hint="Unknown, Observed value is 'Screen' (without quotes)."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "None"$0D "Screen"       values = "None"$0D "Screen"}
          """ + subnbr + """UVW_U_OFFSET:          = {Typ="EU"   Txt="uvw u offset"     Hint="Offset value for texture horizontal position."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_V_OFFSET:          = {Typ="EU"   Txt="uvw v offset"     Hint="Offset value for texture vertical position."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_U_TILING:          = {Typ="EU"   Txt="uvw u tiling"     Hint="Texture tiling horizontal position."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_V_TILING:          = {Typ="EU"   Txt="uvw v tiling"     Hint="Texture tiling vertical position."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_ANGLE:             = {Typ="EU"   Txt="uvw angle"        Hint="Texture angle position."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_BLUR:              = {Typ="EU"   Txt="uvw blur"         Hint="Texture blurring value."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_BLUR_OFFSET:       = {Typ="EU"   Txt="uvw blur offset"  Hint="Texture blurring offset."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_NOUSE_AMT:         = {Typ="EU"   Txt="uvw nouse amount" Hint="Texture no use amount."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_NOISE_SIZE:        = {Typ="EU"   Txt="uvw noise size"   Hint="Texture noise size."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """UVW_NOISE_LEVEL:       = {Typ="CL"   Txt="uvw noise level"  Hint="Unknown. Observed value is 1."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "0"$0D "1"       values = "0"$0D "1"}
          """ + subnbr + """UVW_NOISE_PHASE:       = {Typ="EU"   Txt="uvw noise phase"  Hint="Texture noise phase."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."}
          """ + subnbr + """BITMAP_FILTER:         = {Typ="CL"   Txt="bitmap filter"    Hint="Unknown, presumed to be filter for generating MIP Maps."$0D"Only observed value is 'Pyramidal' (without the quotes)."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "None"$0D "Pyramidal"       values = "None"$0D "Pyramidal"}
        }
        """

        formobj = quarkx.newobj("skin:form")
        formobj.loadtext(def_skin_dlgdef)
        return formobj, None


    # This section for component stored specific settings.
    # Scene Identifiers section.
    if comp.dictspec.has_key('SCENE_BACKGROUND_STATIC') and quarkx.setupsubset(SS_GENERAL, "3D view")["FogColor"] != comp.dictspec['SCENE_BACKGROUND_STATIC']:
        quarkx.setupsubset(SS_GENERAL, "3D view")["FogColor"] = comp.dictspec['SCENE_BACKGROUND_STATIC']
        quarkx.reloadsetup()
    if not comp.dictspec.has_key('SCENE_BACKGROUND_STATIC'):
        comp['SCENE_BACKGROUND_STATIC'] = quarkx.setupsubset(SS_GENERAL, "3D view")["FogColor"]
    # Geometry Object Identifiers
    if not comp.dictspec.has_key('PROP_MOTIONBLUR'):
        comp['PROP_MOTIONBLUR'] = "0"
    if not comp.dictspec.has_key('PROP_CASTSHADOW'):
        comp['PROP_CASTSHADOW'] = "0"
    if not comp.dictspec.has_key('PROP_RECVSHADOW'):
        comp['PROP_RECVSHADOW'] = "0"

    try:
        matnbr = int(comp.dictspec['MATERIAL_REF'])
        for skin in comp.dictitems['Skins:sg'].subitems:
            if skin.name.find("MAT" + str(matnbr)) != -1 and not skin.name.find("SUB") != -1 and skin.name.startswith("MAT"+str(matnbr)+"/"):
                comp['MATERIAL_REF'] = skin.name # Sets this to the current "VALUE".
    except:
        pass

    if not comp.dictspec.has_key('MATERIAL_REF'):
        comp['MATERIAL_REF'] = "None"

    items = ['"None"' + "$0D"]
    values = ['"None"' + "$0D"]

    for skin in comp.dictitems['Skins:sg'].subitems:
        if skin.name.startswith("MAT") and not skin.name.find("SUB") != -1:
            matnbr = skin.name.split("/")[0]
            matnbr = matnbr.replace("MAT", "")
            items = items + ['"' + matnbr + " - " + skin.name.split(".")[0] + '"' + "$0D"]
            values = values + ['"' + skin.name + '"' + "$0D"]

    MATList = """MATERIAL_REF: = {Typ="CL" Txt="material ref." items = """

    for item in items:
        MATList = MATList + item 

    MATList = MATList + """ values = """

    for value in values:
        MATList = MATList + value

    MATList = MATList + """ Hint="List of materials that this"$0D"component can reference"$0D"as its currently active material."$0D0D"To add a new texture to this list"$0D"you must add MAT(next number)/"$0D"to be beginning of its name."}"""


    dlgdef = """
    {
      Help = "These are the Specific settings for .ase model types."$0D
             "ASE uses 'meshes' the same way that QuArK uses 'components'."$0D
             "Each has its own special MATERIAL (or skin texture) settings."$0D0D
             "NOTE: Some games do NOT allow 'TEXTURE TILING' for MODELS, only for SCENES."$0D
             "            Meaning spreading the model faces over repeated image areas of a texture."$0D0D22
             "MATERIAL NAME"$22" - Name of the material."$0D22
             "edit skin"$22" - Opens this skin texture in an external editor."$0D0D
             "UV Vertex Colors - Texture lighting characteristics of a model."$0D22
             "vertex color"$22" - Color to use for this component's u,v vertex color mapping."$0D
             "          Click the color display button to select a color."$0D22
             "show vertex color"$22" - When checked, if component has vertex coloring they will show."$0D
             "          If NOT checked and it has bones with vetexes, those will show."$0D22
             "apply vertex color"$22" - Applies the selected 'Vertex Color'"$0D
             "          to the currently selected vertexes."$0D22
             "remove vertex color"$22" - Removes all of the vertex color"$0D
             "          from the currently selected vertexes."$0D0D
             "Vertex Weight Colors - Bone's weighted vertex movement by color."$0D22
             "use weight bone sel"$22" - When checked, it puts bone selection into a special mode allowing you to"$0D
             "          add or remove bones to the selection without having to use the 'Ctrl' key."$0D22
             "show weight colors"$22" - When checked, if component has vertex weight coloring they will show."$0D
             "          If NOT checked and it has bones with vetexes, those will show."$0D22
             "auto apply changes"$22" - When checked, applies all bone weight settings for any currently or"$0D
             "          additional selected vertexes using the linear handle or applied by the paint brush."$0D0D
             "Shader File - Special effects code by use of textures."$0D22
             "shader file"$22" - Gives the full path and name of the .mtr material"$0D
             "           shader file that the selected skin texture uses, if any."$0D22
             "shader name"$22" - Gives the name of the shader located in the above file"$0D
             "           that the selected skin texture uses, if any."$0D22
             "shader keyword"$22" - Gives the above shader 'keyword' that is used to identify"$0D
             "          the currently selected skin texture used in the shader, if any."$0D22
             "shader lines"$22" - Number of lines to display in window below, max. = 35."$0D22
             "edit shader"$22" - Opens shader below in a text editor."$0D22
             "mesh shader"$22" - Contains the full text of this skin texture's shader, if any."$0D
             "          This can be copied to a text file, changed and saved."$0D0D
             "Scene Identifiers - (Settings for the exported model file)"$0D
             "           Settings for the scene's, ambient light and background color."$0D22
             "background color"$22" - Color for the scene background. Ignored by UnrealEd."$0D
             "           This is the same as QuArK's 'Fog Color' in its Config's 3D view setting."$0D22
             "ambient color"$22" - Color for the scene ambient lighting and brightness."$0D
             "           Ignored by UnrealEd. This light is not shown in QuArK at this time."$0D0D
             "Geometry Object Identifiers - (Settings for the exported model file)"$0D
             "           Settings that effect the actual geometry of objects in the file."$0D22
             "motion blur"$22" - Indicates that this object should be motion blurred if 1, and not if 0."$0D
             "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
             "cast shadows"$22" - Indicates that this object should cast shadows if 1, and not if 0."$0D
             "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
             "receive shadows"$22" - Indicates that this object should receive shadows if 1, and not if 0."$0D
             "           Ignored by UnrealEd. This is not shown in QuArK at this time."$0D22
             "material ref."$22" - List of materials that this component can"$0D
             "           reference as its currently active material."$0D
             "           To add a new texture to this list"$0D
             "           you must add MAT(next number)/"$0D
             "           to be beginning of its name."
      ase_NAME:                = {Typ="E R"  Txt="current skin"      Hint="Name of the skin texture material"$0D"that is currently selected and active."$0D0D"NOTE: Some games do NOT allow 'TEXTURE TILING'"$0D"for MODELS, only for SCENES."$0D"Meaning spreading the model faces over"$0D"repeated image areas of a texture."}
      """ + external_skin_editor_dialog_plugin + """
      """ + vtx_UVcolor_dialog_plugin + """
      """ + vertex_weights_specifics_plugin + """
      """ + Shader_dialog_plugin + """
      sep: = {Typ = "S"   Txt = "" }
      Sep: = {Typ = "S"   Txt = "Scene Identifiers"  Hint="(Settings for the exported model file)"$0D"Settings for the scene's, ambient light and background color."}
      SCENE_BACKGROUND_STATIC: = {Typ="LI"   Txt="background color"  Hint="Color for the scene background."$0D"Ignored by UnrealEd."$0D"This is the same as QuArK's 'Fog Color' in its Config's 3D view setting."}
      SCENE_AMBIENT_STATIC:    = {Typ="LI"   Txt="ambient color"     Hint="Color for the scene ambient lighting and brightness."$0D"Ignored by UnrealEd."$0D"This light is not shown in QuArK at this time."}
      sep: = {Typ = "S"   Txt = "" }
      Sep: = {Typ = "S"   Txt = "Geometry Object Identifiers"  Hint="(Settings for the exported model file)"$0D"Settings that effect the actual geometry of objects in the file."}
      PROP_MOTIONBLUR:         = {Typ="CL"   Txt="motion blur"       Hint="Indicates that this object should be motion blurred if 1, and not if 0."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."   items = "0"$0D "1"       values = "0"$0D "1"}
      PROP_CASTSHADOW:         = {Typ="CL"   Txt="cast shadows"      Hint="Indicates that this object should cast shadows if 1, and not if 0."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."        items = "0"$0D "1"       values = "0"$0D "1"}
      PROP_RECVSHADOW:         = {Typ="CL"   Txt="receive shadows"   Hint="Indicates that this object should receive shadows if 1, and not if 0."$0D"Ignored by UnrealEd."$0D"This is not shown in QuArK at this time."     items = "0"$0D "1"       values = "0"$0D "1"}
      """ + MATList + """
    }
    """

    if comp.type == ":mc": # Just makes sure what we have is a model component.
        formobj = quarkx.newobj("ase_mc:form")
        formobj.loadtext(dlgdef)
        return formobj, icon_btns
    else:
        return None, None

def dataforminput(o):
    "Returns the default settings or input data for this type of object 'o' (a model component & others) to use for the Specific/Args page."

    editor = quarkpy.mdleditor.mdleditor # Get the editor.

    # This section just for o objects that are skin textures.
    if o.type.startswith("."):
        DummyItem = o
        while (DummyItem.type != ":mc"): # Gets the object's model component.
            DummyItem = DummyItem.parent
        comp = DummyItem

        if not comp.dictspec.has_key('shader_file'):
            o['shader_file'] = "None"
        else:
            o['shader_file'] = comp.dictspec['shader_file']
        if not comp.dictspec.has_key('shader_name'):
            o['shader_name'] = "None"
        else:
            o['shader_name'] = comp.dictspec['shader_name']
        if not o.dictspec.has_key('shader_keyword'):
            o['shader_keyword'] = "None"
        else:
            comp['shader_keyword'] = o.dictspec['shader_keyword']
        if not comp.dictspec.has_key('mesh_shader'):
            o['mesh_shader'] = comp['mesh_shader'] = "None"
        else:
            o['mesh_shader'] = comp.dictspec['mesh_shader']

    else:
        DummyItem = Item = o
        while (DummyItem.type != ":mc"): # Gets the object's model component.
            DummyItem = DummyItem.parent
        o = DummyItem
        if o.type == ":mc": # Just makes sure what we have is a model component.
            if not o.dictspec.has_key('ase_NAME'):
                if len(o.dictitems['Skins:sg'].subitems) != 0:
                    o['ase_NAME'] = o.dictitems['Skins:sg'].subitems[0].name
                else:
                    o['ase_NAME'] = "no skins exist"
            if o.currentskin is None:
                if len(o.dictitems['Skins:sg'].subitems) != 0:
                    o.currentskin = o.dictitems['Skins:sg'].subitems[0]
                else:
                    o['ase_NAME'] = "no skins exist"
            if o.dictspec['ase_NAME'] != "no skins exist" and o.dictspec['ase_NAME'] != o.currentskin.name:
                o['ase_NAME'] = o.currentskin.name
            if not o.dictspec.has_key('vtx_color'):
                o['vtx_color'] = "0.75 0.75 0.75"
            if not o.dictspec.has_key('shader_file'):
                o['shader_file'] = "None"
            if not o.dictspec.has_key('shader_name'):
                o['shader_name'] = "None"
            if (editor.Root.currentcomponent.currentskin is not None) and (Item.name == editor.Root.currentcomponent.currentskin.name):
                if Item.dictspec.has_key("shader_keyword"):
                    o['shader_keyword'] = Item.dictspec['shader_keyword']
            else:
                o['shader_keyword'] = "None"
            if not o.dictspec.has_key('mesh_shader'):
                o['mesh_shader'] = "None"
            if o.dictspec.has_key('SCENE_BACKGROUND_STATIC') and quarkx.setupsubset(SS_GENERAL, "3D view")["FogColor"] != o.dictspec['SCENE_BACKGROUND_STATIC']:
                quarkx.setupsubset(SS_GENERAL, "3D view")["FogColor"] = o.dictspec['SCENE_BACKGROUND_STATIC']
                quarkx.reloadsetup()


# ----------- REVISION HISTORY ------------
#
# $Log: ie_ASE_import.py,v $
# Revision 1.22  2011/06/03 20:29:26  danielpharos
# Removed some bad characters from comments.
#
# Revision 1.21  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.20  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.19  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.18  2010/11/06 15:00:47  danielpharos
# Replaced some non-ASCII characters.
#
# Revision 1.17  2010/11/06 13:29:36  danielpharos
# Removed unneeded variable.
#
# Revision 1.16  2010/10/10 03:24:59  cdunde
# Added support for player models attachment tags.
# To make baseframe name uniform with other files.
#
# Revision 1.15  2010/06/13 15:37:55  cdunde
# Setup Model Editor to allow importing of model from main explorer File menu.
#
# Revision 1.14  2010/05/01 04:25:37  cdunde
# Updated files to help increase editor speed by including necessary ModelComponentList items
# and removing redundant checks and calls to the list.
#
# Revision 1.13  2010/01/01 05:55:41  cdunde
# Update to try and import ase files from other games.
#
# Revision 1.12  2009/08/28 07:21:34  cdunde
# Minor comment addition.
#
# Revision 1.11  2009/08/01 05:31:13  cdunde
# Update.
#
# Revision 1.10  2009/07/27 08:46:41  cdunde
# Fix for error if no currentskin exist.
#
# Revision 1.9  2009/07/08 18:53:38  cdunde
# Added ASE model exporter and completely revamped the ASE importer.
#
# Revision 1.8  2009/06/03 05:16:22  cdunde
# Over all updating of Model Editor improvements, bones and model importers.
#
# Revision 1.7  2009/05/01 20:39:34  cdunde
# Moved additional Specific page systems to mdlentities.py as modules.
#
# Revision 1.6  2009/04/28 21:30:56  cdunde
# Model Editor Bone Rebuild merge to HEAD.
# Complete change of bone system.
#
# Revision 1.5  2009/03/26 07:17:17  cdunde
# Update for editing vertex color support.
#
# Revision 1.4  2009/03/25 19:46:00  cdunde
# Changed dictionary list keyword to be more specific.
#
# Revision 1.3  2009/03/25 05:30:19  cdunde
# Added vertex color support.
#
# Revision 1.2  2009/03/19 06:43:48  cdunde
# Minor improvement to avoid improper path splitting.
#
# Revision 1.1  2009/03/18 00:04:21  cdunde
# Added asi model format importing plugin.
#
#