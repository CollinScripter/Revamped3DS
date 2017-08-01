"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Quake 2 .md2 model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_ASE_export.py,v 1.6 2009/08/09 23:41:40 cdunde Exp $


Info = {
   "plug-in":       "ie_ASE_exporter",
   "desc":          "Export selected components to an ASE file and create its collition .cm file. Based on code from Blender, ASE_exporters, author - Goofos.",
   "date":          "June 9 2009",
   "author":        "cdunde/DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 2" }

import time, math, os, os.path, struct, operator, sys as osSys, chunk
import quarkx
import quarkpy.qmacro
from quarkpy.qutils import *
import quarkpy.mdleditor
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

#Globals
logging = 0
exportername = "ie_ASE_export.py"
textlog = "ase_ie_log.txt"
progressbar = None
user_frame_list=[]
g_scale = 1.0
ColTab = "\t"
Colidnt = 1

#============================================
#                   Setup Section
#============================================

def set_lists(self, component, exp_list, objects, matTable, worldTable):
    global mat_cnt
    mat_cnt = 0
    mat_index = 0
    #exp_list = [container1 = [ component, material_ref, refmat],...]

    for current_obj in objects:
        container = []
        if current_obj.type == ':mc':
            container.append(current_obj)
            refmat = 0
            objmatref = current_obj.dictspec['MATERIAL_REF'].split("/")[0]

            # Sets the flag to export this component's shader file is there is one.
            if current_obj.dictspec.has_key('shader_file') and current_obj.dictspec['shader_file'] != "None":
                worldTable['mat_type'] = 1
            mat_ref = []
            mats_me = None
            mats_ob = None
            if current_obj.dictitems.has_key('Skins:sg') and len(current_obj.dictitems['Skins:sg'].subitems) != 0:
                me_mats = mats_me = current_obj.dictitems['Skins:sg'].subitems
                mats_ob = current_obj.dictitems['Skins:sg'].subitems[0]
            #Find used Materials by Meshes or Objects
            if self.src['MTL'] is not None and mats_me is not None: #Materials
                if len(mats_me) > 1:
                    matTable[mat_index] = []
                    for mat in mats_me:
                        if mat.name.find("MAT") != -1 and not mat.name.find("SUB") != -1:
                            matkey = mat.name.split("/")[0]
                            if objmatref == matkey:
                                refmat = mat_index
                            matTable[mat_index] = matTable[mat_index] + [mat]
                            for mat2 in mats_me:
                                if mat2.name.split("_")[0] == matkey:
                                    if mat2.name.find("SUB") != -1:
                                        matTable[mat_index] = matTable[mat_index] + [mat2]
                            mat_index+=1
                            matTable[mat_index] = []
                elif mats_ob:
                    me_mats = [mats_ob]
                    matTable[mat_index] = []
                    for mat in me_mats:
                        if mat.name.find("MAT") != -1 and not mat.name.find("SUB") != -1:
                            matkey = mat.name.split("/")[0]
                            if objmatref == matkey:
                                refmat = mat_index
                            matTable[mat_index] = matTable[mat_index] + [mat]
                            for mat2 in me_mats:
                                if mat2.name.split("_")[0] == matkey:
                                    if mat2.name.find("SUB") != -1:
                                        matTable[mat_index] = matTable[mat_index] + [mat2]
                mat_ref = -1

                if mat_ref < 0:
                    mat_ref = mat_index
                    mat_index+=1
                if len(me_mats) > 1:
                    mat_cnt = len(matTable.keys())-1
            container.append(mat_ref)
            container.append(refmat)
            exp_list.append(container)

    # General Editor Scene settings.
    color = quarkx.setupsubset(SS_GENERAL, "3D view").getint("FogColor")
    R, G, B = quarkpy.qutils.ColorToRGB(color)
    if color != None:
        worldTable['scene_bkgR'] = R
        worldTable['scene_bkgG'] = G
        worldTable['scene_bkgB'] = B
    if component.dictspec.has_key('SCENE_AMBIENT_STATIC'):
        color = component.dictspec['SCENE_AMBIENT_STATIC']
        quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
        color = quarkpy.qeditor.MapColor("color", SS_MODEL)
        R, G, B = quarkpy.qutils.ColorToRGB(color)
        worldTable['scene_ambR'] = R
        worldTable['scene_ambG'] = G
        worldTable['scene_ambB'] = B

#============================================
#                Header/Scene
#============================================

def write_header(file, filename, component, worldTable):
    global user_frame_list, progressbar, tobj, Strings

    # Get the component's Mesh.
    mesh = component.triangles
    Strings[2455] = component.shortname + "\n" + Strings[2455]
    progressbar = quarkx.progressbar(2455, len(mesh)*6)

    file.write("*3DSMAX_ASCIIEXPORT%s200\n" % (Tab))
    file.write("*COMMENT \"Exported from %s - %s\"\n" % (quarkx.version, time.asctime(time.localtime())))
    file.write("*SCENE {\n")

    name = filename.split('/')[-1].split('\\')[-1]
    file.write("%s*SCENE_FILENAME \"%s\"\n" % (Tab, name))

    file.write("%s*SCENE_FIRSTFRAME %d\n" % (Tab, 0))
    if len(component.dictitems['Frames:fg'].subitems)-1 == 0:
        file.write("%s*SCENE_LASTFRAME %d\n" % (Tab, 1))
    else:
        file.write("%s*SCENE_LASTFRAME %d\n" % (Tab, len(component.dictitems['Frames:fg'].subitems)-1))
    file.write("%s*SCENE_FRAMESPEED %d\n" % (Tab, 32))
    file.write("%s*SCENE_TICKSPERFRAME 160\n" % (Tab)) # QuArK has no Ticks?...What are those?

    file.write("%s*SCENE_BACKGROUND_STATIC %.4f %.4f %.4f\n" % (Tab, worldTable['scene_bkgB']/256., worldTable['scene_bkgG']/256., worldTable['scene_bkgR']/256.))
    file.write("%s*SCENE_AMBIENT_STATIC %.4f %.4f %.4f\n" % (Tab, worldTable['scene_ambB']/256., worldTable['scene_ambG']/256., worldTable['scene_ambR']/256.))
    file.write("}\n")


#============================================
#                 Materials Section
#============================================

def write_materials(file, exp_list, worldTable, matTable):
    file.write("*MATERIAL_LIST {\n")
    file.write("%s*MATERIAL_COUNT %s\n" % (Tab, mat_cnt))

    for i,m in matTable.iteritems():
        if len(m) == 1: # single material (skin texture).
            mat_class = 'Standard'

            material = m[0]
            mat_name = material.name

            file.write("%s*MATERIAL %d {\n" % ((Tab), i))

            idnt = 2
            subnbr = mat_para(file, idnt, material, mat_name, mat_class, worldTable)
            mat_dummy(file, idnt, material, subnbr)
           # mat_map(file, idnt, mat_name) # QuArK do we need this part? YES, writes a single MATERIAL's (has no submaterials) "MAP_DIFFUSE" section.
            quark_mat_map(file, idnt, material, subnbr) # QuArK's way of doing the above function, see the "mat_map" function for more possible detail we may need.

            file.write("%s}\n" % (Tab))

        elif len(m) > 1: # multiple materials (skin textures).
            mat_class = 'Multi/Sub-Object'

            mats = m
            material = mats[0]
            mat_name = 'Multi # ' + material.name
            submat_no = len(mats) - 1

            idnt = 2
            file.write("%s*MATERIAL %d {\n" % ((Tab), i))

            mat_para(file, idnt, material, mat_name, mat_class, worldTable)

            file.write("%s*NUMSUBMTLS %d\n" % ((Tab*idnt), submat_no))

            for submat_cnt,current_mat in enumerate(mats):
                if submat_cnt == 0:
                    continue
                material = current_mat
                mat_class = 'Standard'
                mat_name = material.name

                idnt = 2
                file.write("%s*SUBMATERIAL %d {\n" % ((Tab*idnt), submat_cnt-1))
                submat_cnt += 1

                idnt = 3
                subnbr = mat_para(file, idnt, material, mat_name, mat_class, worldTable)
                mat_dummy(file, idnt, material, subnbr)
               # mat_map(file, idnt, mat_name) # QuArK do we need this part? YES, writes each SUBMATERIAL's "MAP_DIFFUSE" section.
                quark_mat_map(file, idnt, material, subnbr) # QuArK's way of doing the above function, see the "mat_map" function for more possible detail we may need.

                idnt = 2
                file.write("%s}\n" % (Tab*idnt))

            file.write("%s}\n" % (Tab))

    file.write("}\n")


def mat_para(file, idnt, material, mat_name, mat_class, worldTable):
    # Skin Texture Material settings.
    subnbr = ""
    if material.name.find("SUB") != -1:
        subnbr = material.name.split("/")[0]
        subnbr = subnbr.split("SUB")
        if len(subnbr) > 1:
            subnbr = "SUB" + subnbr[1] + "_"
        else:
            subnbr = "SUB" + subnbr[0] + "_"
    elif material.name.startswith("MAT"):
        subnbr = material.name.split("/")[0] + "_"
    if material.dictspec.has_key(subnbr + 'MATERIAL_NAME'):
        mat_name = material.dictspec[subnbr + 'MATERIAL_NAME']
    if material.dictspec.has_key(subnbr + 'MATERIAL_CLASS'):
        mat_class = material.dictspec[subnbr + 'MATERIAL_CLASS']
    if material.dictspec.has_key(subnbr + 'MATERIAL_AMBIENT'):
        color = material.dictspec[subnbr + 'MATERIAL_AMBIENT']
        quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
        color = quarkpy.qeditor.MapColor("color", SS_MODEL)
        ambR, ambG, ambB = quarkpy.qutils.ColorToRGB(color)
    else:
        ambR = ambG = ambB = 0.0
    if material.dictspec.has_key(subnbr + 'MATERIAL_DIFFUSE'):
        color = material.dictspec[subnbr + 'MATERIAL_DIFFUSE']
        quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
        color = quarkpy.qeditor.MapColor("color", SS_MODEL)
        difR, difG, difB = quarkpy.qutils.ColorToRGB(color)
    else:
        difR = difG = difB = 0.0
    if material.dictspec.has_key(subnbr + 'MATERIAL_SPECULAR'):
        color = material.dictspec[subnbr + 'MATERIAL_SPECULAR']
        quarkx.setupsubset(SS_MODEL, "Colors")["color"] = color
        color = quarkpy.qeditor.MapColor("color", SS_MODEL)
        specR, specG, specB = quarkpy.qutils.ColorToRGB(color)
    else:
        specR = specG = specB = 0.0
    if material.dictspec.has_key(subnbr + 'MATERIAL_SHINE'):
        mat_spec = float(material.dictspec[subnbr + 'MATERIAL_SHINE'])
    else:
        mat_spec = 0.0
    if material.dictspec.has_key(subnbr + 'MATERIAL_SHINESTRENGTH'):
        mat_hard = float(material.dictspec[subnbr + 'MATERIAL_SHINESTRENGTH'])
    else:
        mat_hard = 0.0
    if material.dictspec.has_key(subnbr + 'MATERIAL_TRANSPARENCY'):
        mat_alpha = float(material.dictspec[subnbr + 'MATERIAL_TRANSPARENCY'])
    else:
        mat_alpha = 1.0000
    if material.dictspec.has_key(subnbr + 'MATERIAL_WIRESIZE'):
        mat_wiresize = float(material.dictspec[subnbr + 'MATERIAL_WIRESIZE'])
    else:
        mat_wiresize = 1.0000

    file.write("%s*MATERIAL_NAME \"%s\"\n" % ((Tab*idnt), mat_name))
    file.write("%s*MATERIAL_CLASS \"%s\"\n" % ((Tab*idnt), mat_class))
    file.write("%s*MATERIAL_AMBIENT %.4f   %.4f   %.4f\n" % ((Tab*idnt), ambB/256., ambG/256., ambR/256.))
    file.write("%s*MATERIAL_DIFFUSE %.4f   %.4f   %.4f\n" % ((Tab*idnt), difB/256., difG/256., difR/256.))
    file.write("%s*MATERIAL_SPECULAR %.4f   %.4f   %.4f\n" % ((Tab*idnt), specB/256., specG/256., specR/256.))
    file.write("%s*MATERIAL_SHINE %.4f\n" % ((Tab*idnt), mat_spec))
    file.write("%s*MATERIAL_SHINESTRENGTH %.4f\n" % ((Tab*idnt), (mat_hard)))
    file.write("%s*MATERIAL_TRANSPARENCY %.4f\n" % ((Tab*idnt), mat_alpha))
    file.write("%s*MATERIAL_WIRESIZE %.4f\n" % (Tab*idnt, mat_wiresize))
    return subnbr


def mat_dummy(file, idnt, material, subnbr):
    if material.dictspec.has_key(subnbr + 'MATERIAL_SHADING') and material.dictspec[subnbr + 'MATERIAL_SHADING'] != "None":
        mat_shading = material.dictspec[subnbr + 'MATERIAL_SHADING']
    else:
        mat_shading = "Blinn"
    if material.dictspec.has_key(subnbr + 'MATERIAL_XP_FALLOFF'):
        mat_xp_falloff = float(material.dictspec[subnbr + 'MATERIAL_XP_FALLOFF'])
    else:
        mat_xp_falloff = 0.0000
    if material.dictspec.has_key(subnbr + 'MATERIAL_SELFILLUM'):
        mat_selfillum = float(material.dictspec[subnbr + 'MATERIAL_SELFILLUM'])
    else:
        mat_selfillum = 0.0000
    if material.dictspec.has_key(subnbr + 'MATERIAL_FALLOFF') and material.dictspec[subnbr + 'MATERIAL_FALLOFF'] != "None":
        mat_falloff = material.dictspec[subnbr + 'MATERIAL_FALLOFF']
    else:
        mat_falloff = "In"
    if material.dictspec.has_key(subnbr + 'MATERIAL_XP_TYPE') and material.dictspec[subnbr + 'MATERIAL_XP_TYPE'] != "None":
        mat_xp_type = material.dictspec[subnbr + 'MATERIAL_XP_TYPE']
    else:
        mat_xp_type = "Filter"
    file.write("%s*MATERIAL_SHADING %s\n" % (Tab*idnt, mat_shading))
    file.write("%s*MATERIAL_XP_FALLOFF %.4f\n" % (Tab*idnt, mat_xp_falloff))
    file.write("%s*MATERIAL_SELFILLUM %.4f\n" % (Tab*idnt, mat_selfillum))
    file.write("%s*MATERIAL_FALLOFF %s\n" % (Tab*idnt, mat_falloff))
    file.write("%s*MATERIAL_XP_TYPE %s\n" % (Tab*idnt, mat_xp_type))


def quark_mat_map(file, idnt, material, subnbr):
    file.write("%s%s {\n" % ((Tab*idnt), "*MAP_DIFFUSE"))
    idnt += 1

    tex_map_name = material.dictspec[subnbr + 'MAP_NAME']
    tex_map_class = material.dictspec[subnbr + 'MAP_CLASS']
    tex_map_subno = material.dictspec[subnbr + 'MAP_SUBNO']
    tex_map_amount = float(material.dictspec[subnbr + 'MAP_AMOUNT'])
    tex_map_bitmap = material.dictspec[subnbr + 'BITMAP']
    tex_map_bitmap = tex_map_bitmap.split(".")[0] + ".tga"
    tex_map_type = material.dictspec[subnbr + 'MAP_TYPE']
    tex_map_uvw_u_offset = float(material.dictspec[subnbr + 'UVW_U_OFFSET'])
    tex_map_uvw_v_offset = float(material.dictspec[subnbr + 'UVW_V_OFFSET'])
    tex_map_uvw_u_tiling = float(material.dictspec[subnbr + 'UVW_U_TILING'])
    tex_map_uvw_v_tiling = float(material.dictspec[subnbr + 'UVW_V_TILING'])
    tex_map_uvw_angle = float(material.dictspec[subnbr + 'UVW_ANGLE'])
    tex_map_uvw_blur = float(material.dictspec[subnbr + 'UVW_BLUR'])
    tex_map_uvw_blur_offset = float(material.dictspec[subnbr + 'UVW_BLUR_OFFSET'])
    tex_map_uvw_nouse_amt = float(material.dictspec[subnbr + 'UVW_NOUSE_AMT'])
    tex_map_uvw_noise_size = float(material.dictspec[subnbr + 'UVW_NOISE_SIZE'])
    tex_map_uvw_noise_level = int(material.dictspec[subnbr + 'UVW_NOISE_LEVEL'])
    tex_map_uvw_noise_phase = float(material.dictspec[subnbr + 'UVW_NOISE_PHASE'])
    tex_map_bitmap_filter = material.dictspec[subnbr + 'BITMAP_FILTER']

    file.write("%s*MAP_NAME \"%s\"\n" % ((Tab*idnt), tex_map_name))
    file.write("%s*MAP_CLASS \"%s\"\n" % ((Tab*idnt), tex_map_class))
    file.write("%s*MAP_SUBNO %s\n" % ((Tab*idnt), tex_map_subno))
    file.write("%s*MAP_AMOUNT %.4f\n" % ((Tab*idnt), tex_map_amount))
    file.write("%s*BITMAP \"%s\"\n" % ((Tab*idnt), tex_map_bitmap))
    file.write("%s*MAP_TYPE %s\n" % ((Tab*idnt), tex_map_type))
    file.write("%s*UVW_U_OFFSET %.4f\n" % ((Tab*idnt), tex_map_uvw_u_offset))
    file.write("%s*UVW_V_OFFSET %.4f\n" % ((Tab*idnt), tex_map_uvw_v_offset))
    file.write("%s*UVW_U_TILING %.4f\n" % ((Tab*idnt), tex_map_uvw_u_tiling))
    file.write("%s*UVW_V_TILING %.4f\n" % ((Tab*idnt), tex_map_uvw_v_tiling))
    file.write("%s*UVW_ANGLE %.4f\n" % ((Tab*idnt), tex_map_uvw_angle))
    file.write("%s*UVW_BLUR %.4f\n" % ((Tab*idnt), tex_map_uvw_blur))
    file.write("%s*UVW_BLUR_OFFSET %.4f\n" % ((Tab*idnt), tex_map_uvw_blur_offset))
    file.write("%s*UVW_NOUSE_AMT %.4f\n" % ((Tab*idnt), tex_map_uvw_nouse_amt))
    file.write("%s*UVW_NOISE_SIZE %.4f\n" % ((Tab*idnt), tex_map_uvw_noise_size))
    file.write("%s*UVW_NOISE_LEVEL %i\n" % ((Tab*idnt), tex_map_uvw_noise_level))
    file.write("%s*UVW_NOISE_PHASE %.4f\n" % ((Tab*idnt), tex_map_uvw_noise_phase))
    file.write("%s*BITMAP_FILTER %s\n" % ((Tab*idnt), tex_map_bitmap_filter))

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mat_map(file, idnt, mat_name):
    mapTable = {0:'*MAP_AMBIENT',1:'*MAP_DIFFUSE',2:'*MAP_SPECULAR',3:'*MAP_SHINE',4:'*MAP_SHINESTRENGTH',5:'*MAP_SELFILLUM',6:'*MAP_OPACITY',7:'*MAP_FILTERCOLOR',8:'*MAP_BUMP',9:'*MAP_REFLECT',10:'*MAP_REFRACT',11:'*MAP_REFRACT'}
    tex_list = [[],[],[],[],[],[],[],[],[],[],[],[]]

    mat = Material.Get(mat_name)
    MTexes = mat.getTextures()

    for current_MTex in MTexes:
        if current_MTex is not None:
            # MAP_SUBNO 0 = *MAP_AMBIENT
            if current_MTex.mapto & Texture.MapTo.AMB:
                map_getTex(current_MTex, 0, (current_MTex.dvar*current_MTex.varfac), tex_list)
            # MAP_SUBNO 1 = *MAP_DIFFUSE = COL = 1
            elif current_MTex.mapto & Texture.MapTo.COL:
                map_getTex(current_MTex, 1, current_MTex.colfac, tex_list)
            # MAP_SUBNO 2 = *MAP_SPECULAR (Color)= CSP or SPEC? = 4
            elif current_MTex.mapto & Texture.MapTo.CSP:
                map_getTex(current_MTex, 2, current_MTex.colfac, tex_list)
            # MAP_SUBNO 3 = *MAP_SHINE (Spec Level) = SPEC or CSP? = 32
            elif current_MTex.mapto & Texture.MapTo.SPEC:
                map_getTex(current_MTex, 3, (current_MTex.dvar*current_MTex.varfac), tex_list)
            # MAP_SUBNO 4 = *MAP_SHINESTRENGTH (Gloss) = HARD = 256
            elif current_MTex.mapto & Texture.MapTo.HARD:
                map_getTex(current_MTex, 4, (current_MTex.dvar*current_MTex.varfac), tex_list)
            # MAP_SUBNO 5 = *MAP_SELFILLUM
            # MAP_SUBNO 6 = *MAP_OPACITY = ALPHA = 128
            elif current_MTex.mapto & Texture.MapTo.ALPHA:
                map_getTex(current_MTex, 6, (current_MTex.dvar*current_MTex.varfac), tex_list)
            # MAP_SUBNO 7 = *MAP_FILTERCOLOR
            # MAP_SUBNO 8 = *MAP_BUMP = NOR = 2
            elif current_MTex.mapto & Texture.MapTo.NOR:
                map_getTex(current_MTex, 8, (current_MTex.norfac/25), tex_list)
            # MAP_SUBNO 9 = *MAP_REFLECT
            elif current_MTex.mapto & Texture.MapTo.REF:
                map_getTex(current_MTex, 9, (current_MTex.norfac/25), tex_list)
            # MAP_SUBNO 10 = *MAP_REFRACT (refraction)
            # MAP_SUBNO 11 = *MAP_REFRACT (displacement)
            elif current_MTex.mapto & Texture.MapTo.DISP:
                map_getTex(current_MTex, 11, (current_MTex.norfac/25), tex_list)

    # Write maps
    for current_LI in tex_list:
        subNo = tex_list.index(current_LI)
        for current_MTex in current_LI:
            tex = current_MTex[0].tex
            if tex.type == Texture.Types.IMAGE:
                map_image(file, idnt, current_MTex, subNo, tex, mapTable[subNo])


def map_getTex(MTex, map_subNo, map_amount, texes):
    # container = [[[MTex], [map_amount]], ...]
    container = []
    container.append(MTex)
    container.append(map_amount)
    texes[map_subNo].append(container)


def map_image(file, idnt, MTexCon, subNo, tex, mapType):
    img = tex.getImage()
    #path = sys.expandpath(img.getFilename()).replace('/', '\\')
    path = img.filename #or img.getFilename()
    path = path.split(".")[0] + ".tga"
    tex_class = 'Bitmap'
    tex_mapType = 'Screen'
    tex_filter = 'Pyramidal'

    file.write("%s%s {\n" % ((Tab*idnt), mapType))

    idnt += 1
    file.write("%s*MAP_NAME \"%s\"\n" % ((Tab*idnt), tex.getName()))
    file.write("%s*MAP_CLASS \"%s\"\n" % ((Tab*idnt), tex_class))
    file.write("%s*MAP_SUBNO %s\n" % ((Tab*idnt), subNo))
    file.write("%s*MAP_AMOUNT %.4f\n" % ((Tab*idnt), MTexCon[1]))
    file.write("%s*BITMAP \"%s\"\n" % ((Tab*idnt), path))
    file.write("%s*MAP_TYPE %s\n" % ((Tab*idnt), tex_mapType))

    # hope this part is right!
    u_tiling = tex.repeat[0]*tex.crop[2]
    v_tiling = tex.repeat[1]*tex.crop[3]
    file.write("%s*UVW_U_OFFSET %.4f\n" % ((Tab*idnt), tex.crop[0]))
    file.write("%s*UVW_V_OFFSET %.4f\n" % ((Tab*idnt), tex.crop[1]))
    file.write("%s*UVW_U_TILING %.4f\n" % ((Tab*idnt), u_tiling))
    file.write("%s*UVW_V_TILING %.4f\n" % ((Tab*idnt), v_tiling))

    map_uvw(file, idnt) #hardcoded

    file.write("%s*BITMAP_FILTER %s\n" % ((Tab*idnt), tex_filter))

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mat_uv(file, idnt, uv_image, uv_name, mat_class, worldTable):
    fake_val0 = '0.0000'
    fake_val1 = '0.1000'
    fake_val2 = '0.5882'
    fake_val3 = '0.9000'
    fake_val4 = '1.0000'

    file.write("%s*MATERIAL_NAME \"%s\"\n" % ((Tab*idnt), uv_name))
    file.write("%s*MATERIAL_CLASS \"%s\"\n" % ((Tab*idnt), mat_class))
    file.write("%s*MATERIAL_AMBIENT %.4f   %.4f   %.4f\n" % ((Tab*idnt), worldTable['ambR']/256., worldTable['ambG']/256., worldTable['ambB']/256.)) #------------Usefull?
    file.write("%s*MATERIAL_DIFFUSE %s   %s   %s\n" % ((Tab*idnt), fake_val2, fake_val2, fake_val2))
    file.write("%s*MATERIAL_SPECULAR %s   %s   %s\n" % ((Tab*idnt), fake_val3, fake_val3, fake_val3))
    file.write("%s*MATERIAL_SHINE %s\n" % ((Tab*idnt), fake_val1))
    file.write("%s*MATERIAL_SHINESTRENGTH %s\n" % ((Tab*idnt), fake_val0))
    file.write("%s*MATERIAL_TRANSPARENCY %s\n" % ((Tab*idnt), fake_val0))
    file.write("%s*MATERIAL_WIRESIZE %s\n" % ((Tab*idnt), fake_val4))


def map_uv(file, idnt, uv_image, uv_name):
    map_type = '*MAP_DIFFUSE'
    map_subNo = '1'
    tex_class = 'Bitmap'
    tex_mapType = 'Screen'
    tex_filter = 'Pyramidal'

    fake_val0 = '0.0000'
    fake_val1 = '0.1000'
    fake_val2 = '0.5882'
    fake_val3 = '0.9000'
    fake_val4 = '1.0000'

    #replace "/" with "\" in image path
    uv_filename = uv_image.getFilename().replace('/', '\\')
    uv_filename = uv_filename.split(".")[0] + ".tga"

    file.write("%s%s {\n" % ((Tab*idnt), map_type))

    idnt += 1
    file.write("%s*MAP_NAME \"%s\"\n" % ((Tab*idnt), uv_name))
    file.write("%s*MAP_CLASS \"%s\"\n" % ((Tab*idnt), tex_class))
    file.write("%s*MAP_SUBNO %s\n" % ((Tab*idnt), map_subNo))
    file.write("%s*MAP_AMOUNT %s\n" % ((Tab*idnt), fake_val4))
    file.write("%s*BITMAP \"%s\"\n" % ((Tab*idnt), uv_filename))
    file.write("%s*MAP_TYPE %s\n" % ((Tab*idnt), tex_mapType))
    file.write("%s*UVW_U_OFFSET %s\n" % ((Tab*idnt), fake_val0))
    file.write("%s*UVW_V_OFFSET %s\n" % ((Tab*idnt), fake_val0))
    file.write("%s*UVW_U_TILING %s\n" % ((Tab*idnt), fake_val4))
    file.write("%s*UVW_V_TILING %s\n" % ((Tab*idnt), fake_val4))

    map_uvw(file, idnt) #hardcoded

    file.write("%s*BITMAP_FILTER %s\n" % ((Tab*idnt), tex_filter))

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def map_uvw(file, idnt):
    fake_val0 = '0.0000'
    fake_val1 = '1.0000'

    file.write("%s*UVW_ANGLE %s\n" % ((Tab*idnt), fake_val0))
    file.write("%s*UVW_BLUR %s\n" % ((Tab*idnt), fake_val1))
    file.write("%s*UVW_BLUR_OFFSET %s\n" % ((Tab*idnt), fake_val0))
    file.write("%s*UVW_NOUSE_AMT %s\n" % ((Tab*idnt), fake_val1))
    file.write("%s*UVW_NOISE_SIZE %s\n" % ((Tab*idnt), fake_val1))
    file.write("%s*UVW_NOISE_LEVEL 1\n" % (Tab*idnt))
    file.write("%s*UVW_NOISE_PHASE %s\n" % ((Tab*idnt), fake_val0))


#============================================
#                   Mesh Section
#============================================


def write_mesh(self, file, component, exp_list, matTable, total):
    global Colidnt

    for current_container in exp_list:
        TransTable = {'SizeX': 1, 'SizeY': 1, 'SizeZ': 1}
        nameMe = {'objName': 'obj', 'meName': 'me'}
        sGroups = {}
        hasTable = {'hasMat': 0, 'hasSG': 0, 'hasUV': 0, 'hasVC': 0, 'matRef': 0}
        count = {'face': 0, 'vert': 0, 'UVs': 0, 'cVert': 0}

        obj = current_container[0]
        mat_ref = current_container[2]
        data = obj.dictitems['Skins:sg']
        nameMe['objName'] = obj.shortname
        nameMe['meName'] = obj.shortname

        mats_me = [mat for mat in data.subitems if mat]
        mats_ob = obj.dictitems['Skins:sg'].subitems
        materials = False

        if mats_me:
            materials = mats_me
        elif mats_ob:
            materials = mats_ob

        if materials:
            hasTable['hasMat'] = 1
            hasTable['matRef'] = current_container[1]
       # This would require a component inside another component, QuArK does not do that.
       # if obj.getParent():
       #     nameMe['parent'] = obj.getParent().name

    #    me = Mesh.New()      # Create a new mesh
        me = obj      # QuArK uses the component (obj) here.

    #    if self.src['MOD'] is not None:   # Use modified mesh
    #        me.getFromObject(obj.name, 0) # Get the object's mesh data, cage 0 = apply mod
    #    else:
    #        me.getFromObject(obj.name, 1)

    #    me.transform(obj.matrix)   #ASE stores transformed mesh data
    #    tempObj = Blender.Object.New('Mesh', 'ASE_export_temp_obj')
    #    tempObj.setMatrix(obj.matrix)
    #    tempObj.link(me)

    #    if self.src['VG2SG'] is not None:
    #        VGNames = data.getVertGroupNames()
    #        for vg in VGNames:
    #            me.addVertGroup(vg)
    #            gverts = data.getVertsFromGroup(vg, 1)
    #            gverts_copy = []
    #            for gv in gverts:
    #                gverts_copy.append(gv[0])
    #            me.assignVertsToGroup(vg, gverts_copy, 1, 1)

    #    obj = tempObj
    #    faces = me.faces
    #    verts = me.verts
        faces = obj.triangles
        verts = obj.dictitems['Frames:fg'].subitems[0].vertices

        count['vert'] = len(verts)
        total['Verts'] += count['vert']
      ### May need this for future QuArK function to group vertexes by selection and vert_index list.
      #  vGroups = me.getVertGroupNames()
      #  if self.src['VG2SG'] is not None and len(vGroups) > 0:
      #      for current_VG in vGroups:
      #          if current_VG.lower().count("smooth."):
      #              hasTable['hasSG'] = 1
      #              gWeight = current_VG.lower().replace("smooth.", "")
      #              sGroups[current_VG] = gWeight

        if self.src['UV'] is not None:
            hasTable['hasUV'] = 1

        if self.src['VC'] is not None:
            if self.editor.ModelComponentList.has_key(obj.name) and self.editor.ModelComponentList[obj.name].has_key('colorvtxlist'):
                hasTable['hasVC'] = 1

        count['face'] = len(obj.triangles)
        total['Tris'] += count['face']
        total['Faces'] = total['Tris']

        #Open Geomobject
        file.write("*GEOMOBJECT {\n")
        file.write("%s*NODE_NAME \"%s\"\n" % (Tab, nameMe['objName']))

        if nameMe.has_key('parent'):
            file.write("%s*NODE_PARENT \"%s\"\n" % (Tab, nameMe['parent']))

        idnt = 1
        mesh_matrix(file, idnt, obj, nameMe, TransTable)

        #Open Mesh
        file.write("%s*MESH {\n" % (Tab))

        idnt = 2
        file.write("%s*TIMEVALUE 0\n" % (Tab*idnt))
        file.write("%s*MESH_NUMVERTEX %i\n" % ((Tab*idnt), count['vert']))
        file.write("%s*MESH_NUMFACES %i\n" % ((Tab*idnt), count['face']))

        idnt = 2
        mesh_vertexList(self, file, idnt, verts, count)
        idnt = 2
        mesh_faceList(self, file, idnt, me, materials, sGroups, faces, matTable, hasTable, count, mat_ref)

        if hasTable['hasUV'] == 1:
            UVTable = {}

            active_map_channel = obj.dictitems['Skins:sg'].subitems[0]
            map_channels = obj.dictitems['Skins:sg'].subitems

            idnt = 2
            mesh_tVertList(file, component, idnt, faces, UVTable, count, active_map_channel)
            mesh_tFaceList(file, idnt, faces, UVTable, count)
            UVTable = {}

            if self.src['MAPPING'] is not None:
                if len(map_channels) > 1:
                    chan_index = 2
                    for map_chan in map_channels:
                        if map_chan != active_map_channel:
                            activeUVLayer = map_chan
                            idnt = 2
                            file.write("%s*MESH_MAPPINGCHANNEL %i {\n" % ((Tab*idnt), chan_index))
                            idnt = 3
                            mesh_tVertList(file, component, idnt, faces, UVTable, count, activeUVLayer)
                            mesh_tFaceList(file, idnt, faces, UVTable, count)
                            UVTable = {}
                            chan_index += 1
                            idnt = 2
                            file.write("%s}\n" % (Tab*idnt))

            activeUVLayer = active_map_channel

        else:
            # dirty fix
            file.write("%s*MESH_NUMTVERTEX %i\n" % ((Tab*idnt), count['UVs']))

        if hasTable['hasVC'] == 1:
            idnt = 2
            if self.editor.ModelComponentList.has_key(component.name) and self.editor.ModelComponentList[component.name].has_key('colorvtxlist'):
                colorvtxlist = self.editor.ModelComponentList[component.name]['colorvtxlist']
                mesh_cVertList(file, colorvtxlist, idnt, verts)
                mesh_cFaceList(file, idnt, faces)

        if self.src['NORMALS'] is not None:
            idnt = 2
            mesh_normals(file, component, idnt, faces, verts, count)

        # Close *MESH
        idnt = 1
        file.write("%s}\n" % (Tab*idnt))

        idnt = 1
        mesh_footer(file, idnt, obj, hasTable, mat_ref)

        # Close *GEOMOBJECT
        file.write("}\n")

    # Section below writes the .cm collision model file if set to do so.
    if self.colfile is not None:
        # Collision file header section.
        self.colfile.write('CM "1.00"\n\n')
        self.colfile.write('0\n\n')
        name = self.filename.replace("\\", "/").split("/models/", 1)[1]
        name = "models/" + name
        if self.src["makefolder"] is not None:
            remove = self.newfiles_folder.rsplit('\\', 1)[1]
            remove = "/" + remove + "/"
            name = name.replace(remove, "/")
        self.colfile.write('collisionModel "%s" {\n' % (name))
        # Collision file vertices section.
        vertices_count = 0
        for group in self.colvertices:
            vertices_count = vertices_count + len(group)
        self.colfile.write('%svertices { /* numVertices = */ %d\n' % ((ColTab*Colidnt), vertices_count))
        # Put for loop here to write the vertices section.
        vertex_counter = 0
        output_vertices = []
        for group in range(len(self.colvertices)):
            for vertex in range(len(self.colvertices[group])):
                vtx = self.colvertices[group][vertex]
                X, Y, Z = vtx[0], vtx[1], vtx[2]
                X =int(round(X))
                Y =int(round(Y))
                Z =int(round(Z))
                output_vertices = output_vertices + [[X, Y, Z]]
                self.colfile.write('%s/* %d */ ( %d %d %d )\n' % ((ColTab*Colidnt), (vertex_counter), X, Y, Z))
                vertex_counter = vertex_counter + 1
        self.colfile.write('%s}\n' % ((ColTab*Colidnt)))
        # Collision file edges section.
        edges_count = len(self.edges)
        self.colfile.write('%sedges { /* numEdges = */ %d\n' % ((ColTab*Colidnt), edges_count))
        for edge in range(len(self.edges)):
            if edge == 0:
                self.colfile.write('%s/* %d */ ( %d %d ) 0 0\n' % ((ColTab*Colidnt), edge, self.edges[edge][0], self.edges[edge][1]))
            else:
                self.colfile.write('%s/* %d */ ( %d %d ) 0 2\n' % ((ColTab*Colidnt), edge, self.edges[edge][0], self.edges[edge][1]))
        self.colfile.write('%s}\n' % ((ColTab*Colidnt)))
        # Collision file nodes section.
        self.colfile.write('%snodes {\n' % ((ColTab*Colidnt)))
        self.colfile.write('%s( -1 0 )\n' % ((ColTab*Colidnt)))
        self.colfile.write('%s}\n' % ((ColTab*Colidnt)))
        # Collision file polygons section.
        self.colfile.write('%spolygons {\n' % ((ColTab*Colidnt)))
        for face in range(len(self.polygons)):
            poly = self.polygons[face]
            edges = len(poly[0])
            face_verts = [[], [], []]
            face_vert_nr = 0
            min = [10000, 10000, 10000]
            max = [-10000, -10000, -10000]
            for edge in range(edges):
                # Only check first vertex of edge, since other vertex will come through with next edge
                if poly[0][edge] < 0:
                    vertex_to_check = self.edges[abs(poly[0][edge])][1]
                else:
                    vertex_to_check = self.edges[poly[0][edge]][0]
                if face_vert_nr < 2:
                    face_verts[face_vert_nr] = output_vertices[vertex_to_check]
                    face_vert_nr += 1
                else:
                    face_verts[face_vert_nr] = output_vertices[vertex_to_check]
                for i in [0, 1, 2]:
                    if output_vertices[vertex_to_check][i] < min[i]:
                        min[i] = output_vertices[vertex_to_check][i]
                    if output_vertices[vertex_to_check][i] > max[i]:
                        max[i] = output_vertices[vertex_to_check][i]
            for i in [0, 1, 2]:
                face_verts[i] = quarkx.vect(face_verts[i][0], face_verts[i][1], face_verts[i][2])
            face_normal = (face_verts[1] - face_verts[0]) ^ (face_verts[2] - face_verts[0])
            face_normal = face_normal.normalized
            face_normal = face_normal.tuple
            dist_to_origin = 0
            for i in [0, 1, 2]:
                dist_to_origin = dist_to_origin + ((((face_normal[i] * min[i]) + (face_normal[i] * max[i])) / 2) ** 2)
            dist_to_origin = math.sqrt(dist_to_origin)
            self.colfile.write('%s%d ( %d %d %d %d ) ( %f %f %f ) %f ( %f %f %f ) ( %f %f %f ) "textures/common/moveableclipmodel"\n' % ((ColTab*Colidnt), edges, poly[0][0], poly[0][1], poly[0][2], poly[0][3], face_normal[0], face_normal[1], face_normal[2], dist_to_origin, min[0], min[1], min[2], max[0], max[1], max[2]))
            self.polygons[face] = self.polygons[face] + [[face_normal[0], face_normal[1], face_normal[2]]] + [[dist_to_origin]] + [[[min[0], min[1], min[2]], [max[0], max[1], max[2]]]]
        self.colfile.write('%s}\n' % ((ColTab*Colidnt)))
        # Collision file brushes section.
        self.colfile.write('%sbrushes {\n' % ((ColTab*Colidnt)))
        def startpoly(face, pmin, pmax):
            global Colidnt
            brushes_count = 6 # Hard coded variable since this code for QuArK only makes cube polys.
            self.colfile.write('%s%d {\n' % ((ColTab*Colidnt), brushes_count))
            Colidnt = Colidnt + 1
            self.colfile.write('%s( 0 0 1 ) %f\n' % ((ColTab*Colidnt), pmax[2]))
        def finishpoly(face, pmin, pmax):
            global Colidnt
            if face > 5:
                self.colfile.write('%s( 0 0 -1 ) %f\n' % ((ColTab*Colidnt), pmin[2]))
            Colidnt = Colidnt - 1
            self.colfile.write('%s} ( %f %f %f ) ( %f %f %f ) "solid"\n' % ((ColTab*Colidnt), pmin[0], pmin[1], pmin[2], pmax[0], pmax[1], pmax[2]))
        polycount = 0
        prevpoly = -1
        facecount = 4
        for face in range(len(self.polygons)-1):
            poly = self.polygons[face]
            if polycount != prevpoly:
                pmin = [10000., 10000., 10000.]
                pmax = [-10000., -10000., -10000.]
                for face2 in range(face, face+4):
                    poly2 = self.polygons[face2]
                    for i in [0, 1, 2]:
                        if poly2[3][0][i] < pmin[i]:
                            pmin[i] = poly2[3][0][i]
                        if poly2[3][1][i] > pmax[i]:
                            pmax[i] = poly2[3][1][i]
                prevpoly = polycount
                startpoly(face, pmin, pmax)
            self.colfile.write('%s( %f %f %f ) %f\n' % ((ColTab*Colidnt), poly[1][0], poly[1][1], poly[1][2], poly[2][0]))
            if face == facecount:
                # write the last face of this poly here
                finishpoly(face, pmin, pmax)
                if face != len(self.polygons)-2:
                    facecount = facecount + 4
                    polycount = polycount + 1
        self.colfile.write('%s}\n' % ((ColTab*Colidnt)))
        self.colfile.write('}\n') # End of Collision file.


def mesh_matrix(file, idnt, obj, nameMe, TransTable):
    bbox = quarkx.boundingboxof(obj.dictitems['Frames:fg'].subitems[0].vertices)
    location = ((bbox[0]+bbox[1])*0.5).tuple
    rota = quarkx.vect(0, 0, 0)
    angle = math.radians(0.0)

  #  Blender.Window.DrawProgressBar(0.0, "Writing Transform Node")

    file.write("%s*NODE_TM {\n" % (Tab*idnt))

    idnt += 1
    file.write("%s*NODE_NAME \"%s\"\n" % ((Tab*idnt), nameMe['meName']))
    # Inherit from what?..
    file.write("%s*INHERIT_POS 0 0 0\n" % (Tab*idnt))
    file.write("%s*INHERIT_ROT 0 0 0\n" % (Tab*idnt))
    file.write("%s*INHERIT_SCL 0 0 0\n" % (Tab*idnt))

    file.write("%s*TM_ROW0 %.4f %.4f %.4f\n" % ((Tab*idnt), 1.0000, 0.0000, 0.0000))
    file.write("%s*TM_ROW1 %.4f %.4f %.4f\n" % ((Tab*idnt), 0.0000, 1.0000, 0.0000))
    file.write("%s*TM_ROW2 %.4f %.4f %.4f\n" % ((Tab*idnt), 0.0000, 0.0000, 1.0000))
    file.write("%s*TM_ROW3 %.4f %.4f %.4f\n" % ((Tab*idnt), 0.0000, 0.0000, 0.0000))

    file.write("%s*TM_POS %.4f %.4f %.4f\n" % ((Tab*idnt), location[0], location[1], location[2]))

    file.write("%s*TM_ROTAXIS %.4f %.4f %.4f\n" % ((Tab*idnt), rota.x, rota.y, rota.z))
    file.write("%s*TM_ROTANGLE %.4f\n" % ((Tab*idnt), angle))

    file.write("%s*TM_SCALE %.4f %.4f %.4f\n" % ((Tab*idnt), TransTable['SizeX'], TransTable['SizeY'], TransTable['SizeZ']))
    #file.write("%s*TM_SCALEAXIS 0.0000 0.0000 0.0000\n" % (Tab*idnt))
    # Looks more logical, because QuArK uses the rotaxis for rot and scale:
    file.write("%s*TM_SCALEAXIS %.4f %.4f %.4f\n" % ((Tab*idnt), rota.x, rota.y, rota.z))
    file.write("%s*TM_SCALEAXISANG %.4f\n" % ((Tab*idnt), angle))

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mesh_vertexList(self, file, idnt, verts, count):
    file.write("%s*MESH_VERTEX_LIST {\n" % (Tab*idnt))

    idnt += 1

   # Blender.Window.DrawProgressBar(0.0, "Writing vertices")

    # Setup for collision file data.
    Zminmax = [10000., -10000.]
    ZmaxXminmax = [10000., -10000.]
    ZmaxYminmax = [10000., -10000.]
    ZminXminmax = [10000., -10000.]
    ZminYminmax = [10000., -10000.]

    for current_vert in range(len(verts)):
        vertex = verts[current_vert].tuple

       # if (current_vert % 1000) == 0:
       #     Blender.Window.DrawProgressBar((current_vert+1.0) / count['vert'], "Writing vertices")

        file.write("%s*MESH_VERTEX %d\t%.4f\t%.4f\t%.4f\n" % ((Tab*idnt), current_vert, vertex[0], vertex[1], vertex[2]))
        # Section below collects max & min Z data for the collision model .cm file if selected to write one.
        if self.colfile is not None:
            if vertex[2] >= Zminmax[1]:
                Zminmax[1] = vertex[2]
            if vertex[2] <= Zminmax[0]:
                Zminmax[0] = vertex[2]

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))

    # Section below builds the data for the collision model .cm file if selected to write one.
    if self.colfile is not None:
        # Creates the "vertices" data section of the collision file.
        for vert in verts:
            vertex = vert.tuple
            if vertex[2] <= Zminmax[0] + 4.0:
                if vertex[0] < ZminXminmax[0]:
                    ZminXminmax[0] = vertex[0]
                if vertex[0] > ZminXminmax[1]:
                    ZminXminmax[1] = vertex[0]
                if vertex[1] < ZminYminmax[0]:
                    ZminYminmax[0] = vertex[1]
                if vertex[1] > ZminYminmax[1]:
                    ZminYminmax[1] = vertex[1]
            if vertex[2] >= Zminmax[1] - 4.0:
                if vertex[0] < ZmaxXminmax[0]:
                    ZmaxXminmax[0] = vertex[0]
                if vertex[0] > ZmaxXminmax[1]:
                    ZmaxXminmax[1] = vertex[0]
                if vertex[1] < ZmaxYminmax[0]:
                    ZmaxYminmax[0] = vertex[1]
                if vertex[1] > ZmaxYminmax[1]:
                    ZmaxYminmax[1] = vertex[1]
        Zsection = (Zminmax[1] - Zminmax[0]) / int(float(self.src['ColSections']))
        Zblocks = {}
        Zblocks["Zblock0"] = []
        # Zblock 0 is a list that contain that "groups" or "sections" [heigth value, [list of its vertexes], [Xminmax values], [XminYminmax values], [XmaxYminmax values]]
        Zblocks["Zblock0"] = Zblocks["Zblock0"] + [round(Zminmax[0])] + [[]] + [[10000., -10000.]] + [[10000., -10000.]] + [[10000., -10000.]]
        # Each Zblock is a list that contain that "groups" or "sections" [heigth value, [list of its vertexes], [Xminmax values], [Yminmax values]]
        for section in range(1, int(float(self.src['ColSections']))):
            name = "Zblock" + str(section)
            Zblocks[name] = []
            Zblocks[name] = Zblocks[name] + [Zminmax[0] + (Zsection*section)] + [[]] + [[10000., -10000.]] + [[10000., -10000.]]
        Zblock0 = round(Zminmax[0]) # remove
        Zblock1 = Zminmax[0] + Zsection # remove
        Zblock2 = Zminmax[0] + (Zsection*2) # remove
        Zblock3 = round(Zminmax[1]) # remove
        name = "Zblock" + str(int(float(self.src['ColSections'])))
        Zblocks[name] = []
        # Last Zblock is a list that contain that "groups" or "sections" [heigth value, [list of its vertexes], [Xminmax values], [Yminmax values]]
        Zblocks[name] = Zblocks[name] + [round(Zminmax[1])]
        Zblocks[name] = Zblocks[name] + [[]] + [[10000., -10000.]] + [[10000., -10000.]]
        Zblockkeys = Zblocks.keys()
        Zblockkeys.sort()
        for vert in verts:
            vertex = vert.tuple
            for key in range(len(Zblockkeys)):
                if (key == 0) and (vertex[2] <= Zblocks[Zblockkeys[key]][0]):
                    Zblocks[Zblockkeys[key]][1] = Zblocks[Zblockkeys[key]][1] + [vert]
                    continue
                if (vertex[2] > Zblocks[Zblockkeys[key-1]][0]) and (vertex[2] <= Zblocks[Zblockkeys[key]][0]):
                    Zblocks[Zblockkeys[key]][1] = Zblocks[Zblockkeys[key]][1] + [vert]
        for vert in Zblocks[Zblockkeys[0]][1]:
            vertex = vert.tuple
            if vertex[0] <= Zblocks[Zblockkeys[0]][2][0]:
                Zblocks[Zblockkeys[0]][2][0] = vertex[0]
                if vertex[1] < Zblocks[Zblockkeys[0]][3][0]:
                    Zblocks[Zblockkeys[0]][3][0] = vertex[1]
                if vertex[1] > Zblocks[Zblockkeys[0]][3][1]:
                    Zblocks[Zblockkeys[0]][3][1] = vertex[1]
            if vertex[0] >= Zblocks[Zblockkeys[0]][2][1]:
                Zblocks[Zblockkeys[0]][2][1] = vertex[0]
                if vertex[1] < Zblocks[Zblockkeys[0]][4][0]:
                    Zblocks[Zblockkeys[0]][4][0] = vertex[1]
                if vertex[1] > Zblocks[Zblockkeys[0]][4][1]:
                    Zblocks[Zblockkeys[0]][4][1] = vertex[1]
        if Zblocks[Zblockkeys[0]][2][0] > ZminXminmax[0]:
            Zblocks[Zblockkeys[0]][2][0] = ZminXminmax[0]
        if Zblocks[Zblockkeys[0]][2][1] < ZminXminmax[1]:
            Zblocks[Zblockkeys[0]][2][1] = ZminXminmax[1]
        if Zblocks[Zblockkeys[0]][3][0] > ZminYminmax[0]:
            Zblocks[Zblockkeys[0]][3][0] = ZminYminmax[0]
        if Zblocks[Zblockkeys[0]][3][1] < ZminYminmax[1]:
            Zblocks[Zblockkeys[0]][3][1] = ZminYminmax[1]
        if Zblocks[Zblockkeys[0]][4][0] > ZminYminmax[0]:
            Zblocks[Zblockkeys[0]][4][0] = ZminYminmax[0]
        if Zblocks[Zblockkeys[0]][4][1] < ZminYminmax[1]:
            Zblocks[Zblockkeys[0]][4][1] = ZminYminmax[1]
        for section in range(1, len(Zblockkeys)):
            name = "Zblock" + str(section)
            for vert in Zblocks[name][1]:
                vertex = vert.tuple
                if vertex[0] <= Zblocks[name][2][0]:
                    Zblocks[name][2][0] = vertex[0]
                if vertex[0] >= Zblocks[name][2][1]:
                    Zblocks[name][2][1] = vertex[0]
                if vertex[1] < Zblocks[name][3][0]:
                    Zblocks[name][3][0] = vertex[1]
                if vertex[1] > Zblocks[name][3][1]:
                    Zblocks[name][3][1] = vertex[1]
        self.colvertices = self.colvertices + [[[Zblocks[Zblockkeys[0]][2][0],Zblocks[Zblockkeys[0]][3][0],Zblock0], [Zblocks[Zblockkeys[0]][2][0],Zblocks[Zblockkeys[0]][3][1],Zblock0], [Zblocks[Zblockkeys[0]][2][1],Zblocks[Zblockkeys[0]][4][1],Zblock0], [Zblocks[Zblockkeys[0]][2][1],Zblocks[Zblockkeys[0]][4][0],Zblock0]]]

        Zblockkeys.reverse()
        for section in range(1, len(Zblockkeys)-1):
            name = Zblockkeys[section]
            if Zblocks[name][2][0] == 10000.:
                Zblocks[name][2][0] = Zblocks[Zblockkeys[section-1]][2][0]
            if Zblocks[name][2][1] == -10000.:
                Zblocks[name][2][1] = Zblocks[Zblockkeys[section-1]][2][1]
            if Zblocks[name][3][0] == 10000.:
                Zblocks[name][3][0] = Zblocks[Zblockkeys[section-1]][3][0]
            if Zblocks[name][3][1] == -10000.:
                Zblocks[name][3][1] = Zblocks[Zblockkeys[section-1]][3][1]

        Zblockkeys.reverse()
        for section in range(1, len(Zblockkeys)):
            name = "Zblock" + str(section)
            self.colvertices = self.colvertices + [[[Zblocks[name][2][0],Zblocks[name][3][0],Zblocks[name][0]], [Zblocks[name][2][0],Zblocks[name][3][1],Zblocks[name][0]], [Zblocks[name][2][1],Zblocks[name][3][1],Zblocks[name][0]], [Zblocks[name][2][1],Zblocks[name][3][0],Zblocks[name][0]]]]

        # Stores the "edges" data section of the collision file.
        def record(self, group, edgelist, add1, add2, vtx=None):
            if (not [add1, add2] in self.edges) and (not [add2, add1] in self.edges):
                self.edges = self.edges + [[add1, add2]]
                edgelist = edgelist + [len(self.edges)-1]
            else:
                for edge in range(len(self.edges)):
                    if [add1, add2] == self.edges[edge]:
                        edgelist = edgelist + [edge]
                        break
                    if [add2, add1] == self.edges[edge]:
                        edgelist = edgelist + [-edge]
                        break
            if len(edgelist) == 4:
                self.polygons = self.polygons + [[edgelist]]
                edgelist.reverse()
                temp = [[]]
                for edge in edgelist:
                    if edge < 0:
                        edge = edge*-1
                        edge = self.edges[edge]
                        edge.reverse()
                        temp[0] = temp[0] + [self.polytemplist[edge[0]]]
                        edge.reverse()
                    else:
                        edge = self.edges[edge]
                        temp[0] = temp[0] + [self.polytemplist[edge[0]]]
                if len(temp[0]) != 0:
                    self.polydata[group-1] = self.polydata[group-1] + temp
                edgelist.reverse()
                edgelist = []
                if (group == len(self.colvertices)-1) and (vtx is not None):
                    edgelist = [-(len(self.edges)-1), -(len(self.edges)-3), -(len(self.edges)-5), -(len(self.edges)-7)]
                    self.polygons = self.polygons + [[edgelist]]
                    edgelist.reverse()
                    temp = [[]]
                    for edge in edgelist:
                        if edge < 0:
                            edge = edge*-1
                            edge = self.edges[edge]
                            edge.reverse()
                            temp[0] = temp[0] + [self.polytemplist[edge[0]]]
                            edge.reverse()
                        else:
                            edge = self.edges[edge]
                            temp[0] = temp[0] + [self.polytemplist[edge[0]]]
                    if len(temp[0]) != 0:
                        self.polydata = self.polydata + [[]]
                        self.polydata[group] = self.polydata[group] + temp
                    edgelist.reverse()
                    edgelist = []
            return edgelist
        for group in range(len(self.colvertices)):
            for vtx in self.colvertices[group]:
                self.polytemplist = self.polytemplist + [vtx]
        for group in range(len(self.colvertices)):
            # Creates the "edges" data section of the collision file.
            if group == 0:
                self.edges = self.edges + [[0, 0], [0, 1], [1, 2], [2, 3], [3, 0]]
                self.polygons = self.polygons + [[[1,2,3,4]]]
                self.polydata = self.polydata + [[[self.colvertices[group][3],self.colvertices[group][2],self.colvertices[group][1],self.colvertices[group][0]]]]
                continue
            edgelist = []
            for vtx in range(len(self.colvertices[group])):
                if vtx == 3:
                    add1 = vtx + 4*(group-1) #          3 :             7  :                11
                    add2 = vtx + 4*group     #          7 :             11 :                15
                    edgelist = record(self, group, edgelist, add1, add2)
                    add1 = add2              #          7 :             11 :                15
                    add2 = add1 - 3          #          4 :             8  :                12
                    edgelist = record(self, group, edgelist, add1, add2)
                    add1 = add2              #          4 :             8  :                12
                    add2 = add1 - 4          #          0 :             4  :                8
                    edgelist = record(self, group, edgelist, add1, add2)
                    add1 = add2              #          0 :             4  :                8
                    add2 = add1 + 3          #          3 :             7  :                11
                    edgelist = record(self, group, edgelist, add1, add2, vtx)
                else:
                    add1 = vtx + 4*(group-1) # 0, 1, 2,  :  4, 5, 6    :   8,   9, 10
                    add2 = vtx + 4*group     # 4, 5, 6,  :  8, 9, 10  :  12, 13, 14
                    edgelist = record(self, group, edgelist, add1, add2)
                    add1 = add2              # 4, 5, 6,  :  8, 9, 10  :  12, 13, 14
                    add2 = add1 + 1          # 5, 6, 7,  :  9, 10, 11 :  13, 14, 15
                    edgelist = record(self, group, edgelist, add1, add2)
                    add1 = add2              # 5, 6, 7,  :  9, 10, 11 :  13, 14, 15
                    add2 = add1 - 4          # 1, 2, 3,  :  5,  6,  7  :   9, 10,  11
                    edgelist = record(self, group, edgelist, add1, add2)
                    add1 = add2              # 1, 2, 3,  :  5,  6,  7  :   9, 10,  11
                    add2 = add1 - 1          # 0, 1, 2,  :  4,  5,  6  :   8,   9, 10
                    edgelist = record(self, group, edgelist, add1, add2)
            if group != len(self.colvertices)-1:
                self.polydata = self.polydata + [[]]
                    

def mesh_faceList(self, file, idnt, me, materials, sGroups, faces, matTable, hasTable, count, mat_ref):
    file.write("%s*MESH_FACE_LIST {\n" % (Tab*idnt))
    idnt += 1
    faceNo = 0

   # Blender.Window.DrawProgressBar(0.0, "Writing faces")
    if hasTable['hasMat'] == 1 and matTable:
        mats = matTable[hasTable['matRef']]
   # fgon_eds = [(ed.key) for ed in me.edges if ed.flag & Mesh.EdgeFlags.FGON]
    for current_face in faces:
        face_verts = current_face
        smooth = '*MESH_SMOOTHING'
        matID = '*MESH_MTLID 0'

       # if (faceNo % 500) == 0:
       #     Blender.Window.DrawProgressBar((faceNo+1.0) / count['face'], "Writing faces")

        if hasTable['hasMat'] == 1:
            if self.src['MTL'] is not None:
                matID = '*MESH_MTLID %i' % (mat_ref)
            else:
                matID = '*MESH_MTLID %i' % (0)

        if len(face_verts) is 3:
            vert0 = face_verts[0][0]
            vert1 = face_verts[1][0]
            vert2 = face_verts[2][0]

            #Find hidden (fgon) edges
           # edge_keys = current_face.edge_keys
            eds_fgon = [1,1,1]
           # for i,ed_key in enumerate(edge_keys):
           #     if ed_key in fgon_eds:
           #         eds_fgon[i] = 0

            #Find Smoothgroups for this face:
            if self.src['VG2SG'] is not None and hasTable['hasSG'] == 1: # and current_face.smooth:
                firstSmooth = 1
                for current_SG in sGroups:
                    sGroup = me.getVertsFromGroup(current_SG)
                    if vert0 in sGroup and vert1 in sGroup and vert2 in sGroup:
                        if firstSmooth == 1:
                            smooth += ' %s' % (sGroups[current_SG])
                            firstSmooth = 0
                        else:
                            smooth += ', %s' % (sGroups[current_SG])
           # elif current_face.smooth:
            elif current_face:
                if self.src['VG2SG'] is not None:
                    smooth += ' 1'
                else:
                    smooth += ' 0'

            file.write("%s*MESH_FACE %i: A: %i B: %i C: %i AB: %i BC: %i CA: %i %s \t%s\n" % ((Tab*idnt), faceNo, vert2, vert1, vert0, eds_fgon[0], eds_fgon[1], eds_fgon[2], smooth, matID))
            faceNo+=1

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mesh_tVertList(file, component, idnt, faces, UVTable, count, activeUVLayer):
    TexWidth, TexHeight = activeUVLayer.dictspec['Size']

   # Blender.Window.DrawProgressBar(0.0, "Setup UV index")

    for current_face in faces:
        faceuv = current_face
        for current_uv in faceuv:
            uv = (current_uv[1], current_uv[2])
            if not UVTable.has_key(uv):
                UVTable[uv] = 0
                count['UVs'] += 1

    #count['UVs'] = len(UVTable)
    file.write("%s*MESH_NUMTVERTEX %d\n" % ((Tab*idnt), count['UVs']))
    file.write("%s*MESH_TVERTLIST {\n" % (Tab*idnt))

    idnt += 1
   # Blender.Window.DrawProgressBar(0.0, "Writing UV index")

    for index,current_UV in enumerate(UVTable.iterkeys()):
      # if (index % 1000) == 0:
      #    Blender.Window.DrawProgressBar((index+1.0) / count['face'], "Writing UV index")

       U = current_UV[0]/TexWidth
       V = -current_UV[1]/TexHeight

       file.write("%s*MESH_TVERT %i %.4f\t%.4f\t0.0000\n" % ((Tab*idnt), index, U, V))
       UVTable[current_UV] = index

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mesh_tFaceList(file, idnt, faces, UVTable, count):
    tfaceNo = 0

   # Blender.Window.DrawProgressBar(0.0, "Writing Face UV")

    file.write("%s*MESH_NUMTVFACES %i\n" % ((Tab*idnt), count['face']))
    file.write("%s*MESH_TFACELIST {\n" % (Tab*idnt))

    idnt += 1

    for current_face in faces:
        faceUV = current_face

       # if (tfaceNo % 1000) == 0:
       #     Blender.Window.DrawProgressBar((tfaceNo+1.0) / count['face'], "Writing Face UV")

        if len(faceUV) is 3: # Triangle
            UV0 = UVTable[(faceUV[0][1], faceUV[0][2])]
            UV1 = UVTable[(faceUV[1][1], faceUV[1][2])]
            UV2 = UVTable[(faceUV[2][1], faceUV[2][2])]
            file.write("%s*MESH_TFACE %i\t%i\t%i\t%d\n" % ((Tab*idnt), tfaceNo, UV2, UV1, UV0))
            tfaceNo+=1

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mesh_cVertList(file, colorvtxlist, idnt, verts):
   # Blender.Window.DrawProgressBar(0.0, "Setup VCol index")

    keys = colorvtxlist.keys()

    file.write("%s*MESH_NUMCVERTEX %i\n" % ((Tab*idnt), len(verts)))
    file.write("%s*MESH_CVERTLIST {\n" % (Tab*idnt))

    idnt += 1

   # Blender.Window.DrawProgressBar(0.0, "Writing VCol index")

    for colorvtxindex in range(len(verts)):
        R, G, B = (256., 256., 256.)
        if colorvtxlist.has_key(colorvtxindex):
            vtx_color = colorvtxlist[colorvtxindex]['vtx_color']
            quarkx.setupsubset(SS_MODEL, "Colors")["color"] = vtx_color
            vtx_color = quarkpy.qeditor.MapColor("color", SS_MODEL)
            R, G, B = quarkpy.qutils.ColorToRGB(vtx_color)
       # if (colorvtxindex % 1000) == 0:
       #     Blender.Window.DrawProgressBar((colorvtxindex+1.0) / len(keys), "Writing VCol index")

        file.write("%s*MESH_VERTCOL %i\t%.4f\t%.4f\t%.4f\n" % ((Tab*idnt), colorvtxindex, (B/256.), (G/256.), (R/256.)))

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mesh_cFaceList(file, idnt, faces):
    cFaceNo = 0

   # Blender.Window.DrawProgressBar(0.0, "Writing Face Colors")
    file.write("%s*MESH_NUMCVFACES %i\n" % ((Tab*idnt), len(faces)))
    file.write("%s*MESH_CFACELIST {\n" % (Tab*idnt))

    idnt += 1
    for current_face in range(len(faces)):

       # if (cFaceNo % 500) == 0:
       #     Blender.Window.DrawProgressBar((cFaceNo+1.0) / len(colfaces), "Writing Face Colors")

        color0 = faces[current_face][0][0]
        color1 = faces[current_face][1][0]
        color2 = faces[current_face][2][0]

        file.write("%s*MESH_CFACE %i\t%i\t%i\t%i\n" % ((Tab*idnt), cFaceNo, color2, color1, color0))
        cFaceNo+= 1

    idnt -= 1
    file.write("%s}\n" % (Tab*idnt))


def mesh_normals(file, component, idnt, faces, verts, count):
    # To export quads it is needed to calculate all face and vertex normals new!
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

    file.write("%s*MESH_NORMALS {\n" % (Tab*idnt))

   # Blender.Window.DrawProgressBar(0.0, "Setup Normals")

    #-- Calculate new face and vertex normals

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
       vec.normalized

    #-- Finally write normals
    normNo = 0
    idnt += 2

   # Blender.Window.DrawProgressBar(0.0, "Writing Normals")

    for f_index in range(len(faces)):

       # if (normNo % 500) == 0:
       #     Blender.Window.DrawProgressBar((normNo+1.0) / count['face'], "Writing Normals")

        f_verts = faces[f_index]
       # smooth = faces[f_index].smooth
        smooth = 1

        if len(f_verts) is 3: # Triangle
            v0_i = f_verts[0][0]
            v1_i = f_verts[1][0]
            v2_i = f_verts[2][0]

            idnt -= 1
            f_no = f_normals[f_index]
            file.write("%s*MESH_FACENORMAL %i\t%.4f\t%.4f\t%.4f\n" % ((Tab*idnt), normNo, f_no.x, f_no.y, f_no.z))
            normNo += 1

            idnt += 1
            mesh_vertNorm(file, idnt, v0_i, v1_i, v2_i, v_normals, smooth, f_no)


    idnt -= 2
    file.write("%s}\n" % (Tab*idnt))


def mesh_vertNorm(file, idnt, v0_i, v1_i, v2_i, v_normals, smooth, f_no):
    if smooth:
        v_no0 = v_normals[v0_i]
        v_no1 = v_normals[v1_i]
        v_no2 = v_normals[v2_i]
    else: #If solid use the face normal
        v_no0 = v_no1 = v_no2 = f_no

    file.write("%s*MESH_VERTEXNORMAL %i\t%.4f\t%.4f\t%.4f\n" % ((Tab*idnt), v2_i, v_no2.x, v_no2.y, v_no2.z))
    file.write("%s*MESH_VERTEXNORMAL %i\t%.4f\t%.4f\t%.4f\n" % ((Tab*idnt), v1_i, v_no1.x, v_no1.y, v_no1.z))
    file.write("%s*MESH_VERTEXNORMAL %i\t%.4f\t%.4f\t%.4f\n" % ((Tab*idnt), v0_i, v_no0.x, v_no0.y, v_no0.z))


def mesh_footer(file, idnt, obj, hasTable, mat_ref):
    if obj.dictspec.has_key('PROP_MOTIONBLUR'):
        comp_prop_motionblur = int(obj.dictspec['PROP_MOTIONBLUR'])
    else:
        comp_prop_motionblur = 0
    if obj.dictspec.has_key('PROP_CASTSHADOW'):
        comp_prop_castshadow = int(obj.dictspec['PROP_CASTSHADOW'])
    else:
        comp_prop_castshadow = 1
    if obj.dictspec.has_key('PROP_RECVSHADOW'):
        comp_prop_recvshadow = int(obj.dictspec['PROP_RECVSHADOW'])
    else:
        comp_prop_recvshadow = 1

    file.write("%s*PROP_MOTIONBLUR %i\n" % ((Tab*idnt), comp_prop_motionblur))
    file.write("%s*PROP_CASTSHADOW %i\n" % ((Tab*idnt), comp_prop_castshadow))
    file.write("%s*PROP_RECVSHADOW %i\n" % ((Tab*idnt), comp_prop_recvshadow))

    if hasTable['hasMat'] != 0:
        file.write("%s*MATERIAL_REF %i\n" % ((Tab*idnt), mat_ref))

def write_shaders(filename, exp_list):
    shaders = []
    for comp in exp_list:
        if comp[0].dictspec.has_key('shader_name') and comp[0].dictspec['shader_name'] != "None" and not comp[0].dictspec['shader_name'] in shaders:
            if len(shaders) == 0:
                shadername = filename.replace(".ase", ".mtr")
                shaderfile = open(shadername, "w")
            shaders = shaders + [comp[0].dictspec['shader_name']]
            shader = comp[0].dictspec['mesh_shader']
            shader = shader.replace("\r\n", "\n")
            shaderfile.write(shader)
    try:
        shaderfile.close()
    except:
        pass

   #-------------------------End----------------------

######################################################
# Save ASE Format
######################################################
def save_ASE(self):
    global tobj, logging, exportername, textlog, Strings, exp_list, Tab, idnt, imgTable, worldTable
    editor = self.editor
    if editor is None:
        return
    filename = self.filename

    objects = editor.layout.explorer.sellist
    exp_list = []
    Tab = "\t"
    idnt = 1
    matTable = {}
    worldTable = {'scene_bkgR': 0.0, 'scene_bkgG': 0.0, 'scene_bkgB': 0.0, 'scene_ambR': 0.0, 'scene_ambG': 0.0, 'scene_ambB': 0.0, 'ambR': 0.0, 'ambG': 0.0, 'ambB': 0.0, 'difR': 0.0, 'difG': 0.0, 'difB': 0.0, 'specR': 0.0, 'specG': 0.0, 'specB': 0.0, 'mat_type': 0} #default
    total = {'Verts': 0, 'Tris': 0, 'Faces': 0}

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    file = self.asefile

    #get the component
    component = editor.Root.currentcomponent # This gets the first component (should be only one).

    if logging == 1:
        ase.dump() # Writes the file Header last to the log for comparison reasons.

    # This section writes the various sections to the exporter .ase file.
    # Some items are commented out because we are not storing this data yet.
    set_lists(self, component, exp_list, objects, matTable, worldTable)
    write_header(file, filename, component, worldTable)
    write_materials(file, exp_list, worldTable, matTable)
    write_mesh(self, file, component, exp_list, matTable, total)

    file.close()
    if self.colfile is not None:
        self.colfile.close()

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
        
    progressbar.close()
    Strings[2455] = Strings[2455].replace(component.shortname + "\n", "")

    #cleanup
    ase = 0

    add_to_message = "Any skin textures used as a material\nwill need to be converted to a .tga file.\n\nThis can be done in an image editor\nsuch as 'PaintShopPro' or 'PhotoShop'."
    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

# Saves the model file: root is the actual file,
# filename is the full path and name of the .ase to create.
# For example:  C:Program Files\Doom 3\base\models\mapobjects\washroom\toilet.ase
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
    for object in objects:
        if not object.dictitems['Frames:fg'] or len(object.dictitems['Frames:fg'].subitems) == 0:
            quarkx.msgbox("Component " + object.shortname + "\nhas no frames to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if len(object.dictitems['Frames:fg'].subitems[0].dictspec['Vertices']) == 0:
            quarkx.msgbox("Component " + object.shortname + "\nhas no frame vertices to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

    UIExportDialog(root, filename, editor)
    return

### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".ase Exporter", ".ase file", "*.ase", savemodel)


class ExportSettingsDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (200, 300)
    dfsep = 0.6     # sets 80% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """
        {
        Style = "13"
        Caption = "ASE Export Items"
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

        MTL: =
            {
            Txt = "Export MTL Data:"
            Typ = "X"
            Hint = "When checked all material (skin texture)"$0D
                   "data will be exported into the ase model file."$0D
                   "Default setting is checked."
            }

        UV: =
            {
            Txt = "Export UV Data:"
            Typ = "X"
            Hint = "When checked all vertices and face texture UV"$0D
                   "data will be exported into the ase model file."$0D
                   "Default setting is checked."
            }

        VC: =
            {
            Txt = "Export VC Data:"
            Typ = "X"
            Hint = "When checked all vertices and face vertex color (paint)"$0D
                   "data will be exported into the ase model file."$0D
                   "Default setting is un-checked to reduce file size."
            }

        MAPPING: =
            {
            Txt = "Export MAP Data:"
            Typ = "X"
            Hint = "When checked all material channel mapping"$0D
                   "data will be exported into the ase model file."$0D
                   "Default setting is un-checked to reduce file size."
            }

        NORMALS: =
            {
            Txt = "Export NORM Data:"
            Typ = "X"
            Hint = "When checked all faces normals are calculated and the"$0D
                   "data will be exported into the ase model file."$0D
                   "Default setting is un-checked to reduce file size."
            }

        VG2SG: =
            {
            Txt = "Export VG2SG Data:"
            Typ = "X"
            Hint = "When checked all mesh faces are set for 'MESH_SMOOTHING'"$0D
                   "data to be exported into the ase model file."$0D
                   "Default setting is un-checked."
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

        Collision: =
            {
            Txt = "Make Collision file:"
            Typ = "X"
            Hint = "Check this box to make and export a .cm collision"$0D
                   "model file to go along with the exported .ase file."$0D0D
                   "For Doom3, to see the collision model bring down the game console,"$0D
                   "type in g_showCollisionModels 1"$0D
                   "press Enter, close the game console and move toward the model."
            }

        ColSections: =
            {
            Txt = "   Collision sections:"
            Typ = "EU"
            Hint = "Number of collision sections to create."$0D
                   "Greater the number, the more detailed the collision."$0D
                   "Min = 1, Max = 3, Default = 3"
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
                   "that you chose for the .ase model file to be placed."
            }

        sep: = { Typ="S" Txt="" }
        MakeFiles:py = {Txt="Export Model"}
        close:py = {Txt="Close dialog"}
        }
        """

    def __init__(self, form1, root, filename, editor, newfiles_folder): # Creates the dialogbox.
        self.filename = filename
        self.newfiles_folder = newfiles_folder
        self.editor = editor
        self.asefile = None
        self.colfile = None
        self.colfilename = None
        self.colvertices = []
        self.edges = []
        self.polygons = []
        self.polydata = []
        self.polytemplist = []
        self.exportpath = filename.replace('\\', '/')
        self.exportpath = self.exportpath.rsplit('/', 1)[0]
        src = quarkx.newobj(":")
        src['MTL'] = "1"
        src['UV'] = "1"
        src['MAPPING'] = None
        src['VC'] = None
        src['NORMALS'] = None
        src['VG2SG'] = None
        src['Skins'] = None
        src['Shaders'] = None
        src['Collision'] = None
        src['ColSections'] = "3"
        src['makefolder'] = None
        self.src = src
        self.root = root

        # Create the dialog form and the buttons.
        quarkpy.qmacro.dialogbox.__init__(self, form1, src,
            MakeFiles = quarkpy.qtoolbar.button(self.MakeFiles,"DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.",ico_editor, 3, "Export Model"),
            close = quarkpy.qtoolbar.button(self.close, "DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.", ico_editor, 0, "Cancel Export")
            )

    def datachange(self, df):
        self.src['ColSections'] = str(int(float(self.src['ColSections'])))
        if int(self.src['ColSections']) < 1:
            self.src['ColSections'] = "1"
        if int(self.src['ColSections']) > 3:
            self.src['ColSections'] = "3"
        self.colvertices = []
        self.edges = []
        self.polygons = []
        self.polydata = []
        self.polytemplist = []
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

        if self.src["Collision"] is not None:
            self.colfilename = self.filename.rsplit('.', 1)[0] + ".cm"
            if not os.path.exists(self.colfilename):
                pass
            else:
                result = quarkx.msgbox("A Collision file of the same name\n    " + self.colfilename + "\nalready exist at that location.\n\nCAUTION:\nIf you click 'YES' the current file will be overwritten.\nIf you click 'NO' the current file will remain as is.\n\nDo you wish to rewrite this file?", quarkpy.qutils.MT_WARNING, quarkpy.qutils.MB_YES | quarkpy.qutils.MB_NO)
                if result == MR_YES:
                    pass
                else:
                    self.colfilename = None

        # Open the output file for writing the .ase file to disk.
        self.asefile = open(self.filename,"w")
        if self.colfilename is not None:
            self.colfile = open(self.colfilename,"w")
        save_ASE(self)


def UIExportDialog(root, filename, editor):
    # Sets up the new window form for the exporters dialog for user selection settings and calls its class.
    form1 = quarkx.newform("masterform")
    newfiles_folder = filename.replace(".ase", "")
    ExportSettingsDlg(form1, root, filename, editor, newfiles_folder)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_ASE_export.py,v $
# Revision 1.6  2009/08/09 23:41:40  cdunde
# Fix to remove work folder name from collision model.
#
# Revision 1.5  2009/08/01 05:31:13  cdunde
# Update.
#
# Revision 1.4  2009/07/25 10:24:29  cdunde
# Improved .cm collision model code for simple to more detail model setting capability.
#
# Revision 1.3  2009/07/24 00:50:16  cdunde
# ASE model exporter can now export .cm collision model files.
#
# Revision 1.2  2009/07/13 23:55:03  cdunde
# Start of collision model file creation support.
#
# Revision 1.1  2009/07/08 18:53:39  cdunde
# Added ASE model exporter and completely revamped the ASE importer.
#
#
#