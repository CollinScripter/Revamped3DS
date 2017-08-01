"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Quake 2 .md2 model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_lightwave_import.py,v 1.43 2011/06/03 20:29:26 danielpharos Exp $

Info = {
   "plug-in":       "ie_md2_importer",
   "desc":          "This script imports a .lwo Lightwave type LWOB and LWO2 (Doom 3) model file and textures into QuArK for editing. Original code from Blender, lightwave_import.py, authors - Alessandro Pirovano, Anthony D'Agostino (Scorpius).",
   "date":          "June 3 2008",
   "author":        "cdunde/DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 2" }

# +---------------------------------------------------------+
# | Previous Release log:                                   |
# | 0.2.2b: This version.                                   |
# | 0.2.1 : Modified material mode assignment to deal with  |
# |         Python API modification                         |
# |         Changed script license to GNU GPL               |
# | 0.2.0:  Major rewrite to deal with large meshes         |
# |         - 2 pass file parsing                           |
# |         - lower memory footprint                        |
# |           (as long as python gc allows)                 |
# |         2.40a2 - Removed subsurf settings patches=poly  |
# |         2.40a2 - Edge generation instead of 2vert faces |
# | 0.1.16: fixed (try 2) texture offset calculations       |
# |         added hint on axis mapping                      |
# |         added hint on texture blending mode             |
# |         added hint on texture transparency setting      |
# |         search images in original directory first       |
# |         fixed texture order application                 |
# | 0.1.15: added release log                               |
# |         fixed texture offset calculations (non-UV)      |
# |         fixed reverting vertex order in face generation |
# |         associate texture on game-engine settings       |
# |         vector math definitely based on mathutils       |
# |         search images in "Images" and "../Images" dir   |
# |         revised logging facility                        |
# |         fixed subsurf texture and material mappings     |
# | 0.1.14: patched missing mod_vector (not definitive)     |
# | 0.1.13: first public release                            |
# +---------------------------------------------------------+

#iosuite related import
### QuArK note: may need later, file in C:\Program Files\Blender Foundation\Blender 2.40\.blender\scripts\bpymodules
#try: #new naming
#    import meshtools as my_meshtools
#except ImportError: #fallback to the old one
#    print "using old mod_meshtools"
#    import mod_meshtools as my_meshtools

#python specific modules import
import struct, chunk, os, cStringIO, time, operator
import quarkx
import quarkpy.qtoolbar
import ie_utils
import quarkpy.mdlentities
import quarkpy.mdlutils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings
from quarkpy.qeditor import ico_dict # Get the dictionary list of all icon image files available.

# ===========================================================
# === Utility Preamble ======================================
# ===========================================================

# Globals
SS_MODEL = 3
logging = 0
importername = "ie_lightwave_import.py"
textlog = "lwo_ie_log.txt"
editor = None

def rlcopy(ll):
    if type(ll) != type ([]):
        return ll
    if ll == []:
        return []
    cpy = [rlcopy(ii) for ii in ll]
    return cpy

# ===========================================================
# === Main read functions ===================================
# ===========================================================

# =============================
# === Read LightWave Format ===
# =============================
def read(basepath, filename):
    global tobj, logging, importername, textlog

    logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

    file = open(filename, "rb")

    form_id, form_size, form_type = struct.unpack(">4s1L4s",  file.read(12))
    if (form_type == "LWOB"):
        ComponentList, message = read_lwob(file, basepath, filename)
    elif (form_type == "LWO2"):
        ComponentList, message = read_lwo2(file, basepath, filename)
    else:
        if logging == 1:
            tobj.logcon ("Can't read a file with the form_type: %s" %form_type)
        file.close()
        return [None, None, ""]

    file.close()

    if form_type == "LWO2": add_to_message = "LWO2 (v6.0 Format) file type"
    if form_type == "LWOB": add_to_message = "LWOB (v5.5 Format) file type"

    ie_utils.default_end_logging(filename, "IM", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

    ### Use the 'ModelRoot' below to test opening the QuArK's Model Editor with, needs to be qualified with main menu item.
    ModelRoot = quarkx.newobj('Model:mr')
  #  ModelRoot.appenditem(Component)

    return ModelRoot, ComponentList, message


# =================================
# === Read LightWave 5.5 format ===
# =================================
def read_lwob(file, basepath, filename):
    global tobj, logging

    if logging == 1:
        tobj.logcon("LightWave 5.5 format")
    objname = os.path.splitext(os.path.basename(filename))[0]

    while 1:
        try:
            lwochunk = chunk.Chunk(file)
        except EOFError:
            break
        if lwochunk.chunkname == "LAYR":
            objname = read_layr(lwochunk)
        elif lwochunk.chunkname == "PNTS":                         # Verts
            verts = read_verts(lwochunk)
        elif lwochunk.chunkname == "POLS": # Faces v5.5
            faces = read_faces_5(lwochunk)
            my_meshtools.create_mesh(verts, faces, objname)
        else:                                                       # Misc Chunks
            lwochunk.skip()
    message = ""
    return None, message


# =============================
# === Read LightWave Format ===
# =============================
def read_lwo2(file, basepath, filename, typ="LWO2"):
    global tobj, logging

    if logging == 1:
        tobj.logcon("LightWave 6 (and above) format")

    name = filename.split('\\')
    fname_part = name[len(name)-1]
    dir_part = filename.replace('\\'+ fname_part, '')
    ask_weird = 1

    #first initialization of data structures
    defaultname = os.path.splitext(fname_part)[0]
    tag_list = []              # a list of the textures, without file suffix, that the model uses.
    surf_list = []             # surf specifics and their settings: needs to be saved for export.
    clip_list = []             # usually empty: but should be saved for export anyway just in case.
    object_index = 0           # just a counter for how many components are created for writing to the log.
    object_list = None         # has 9 different subitems, [0] model name or 'NoName', [2] are the frame.vertecies.
    objspec_list = None        # only set here as none: but should be checked at end for export just in case (see next line).
    # init value is: object_list = [[None, {}, [], [], {}, {}, 0, {}, {}]]
    #0 - objname                    #original name
    #1 - obj_dict = {TAG}           #objects created
    #2 - verts = []                 #object vertexes
    #3 - faces = []                 #object faces (associations poly -> vertexes)
    #4 - obj_dim_dict = {TAG}       #tuples size and pos in local object coords - used for NON-UV mappings
    #5 - polytag_dict = {TAG}       #tag to polygons mapping
    #6 - patch_flag                 #0 = surf; 1 = patch (subdivision surface) - it was the image list
    #7 - uvcoords_dict = {name}     #uvmap coordinates (mixed mode per vertex/per face)
    #8 - facesuv_dict = {name}      #vmad only coordinates associations poly & vertex -> uv tuples

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

    #pass 1: look in advance for materials
    if logging == 1:
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Starting Pass 1:")
        tobj.logcon ("#####################################################################")
    while 1:
        try:
            lwochunk = chunk.Chunk(file)
        except EOFError:
            break
        if logging == 1:
            tobj.pprint(" ")
        if lwochunk.chunkname == "TAGS":                           # Tags, a list of skin textures used.
            if logging == 1:
                tobj.pprint("---- TAGS (Model Components\Textures)")
            tag_list.extend(read_tags(lwochunk))
            if logging == 1:
                tobj.pprint("tag_list")
                tobj.pprint(tag_list)
        elif lwochunk.chunkname == "SURF":                         # surfaces
            if logging == 1:
                tobj.pprint("---- SURF")
            surf_list.append(read_surfs(lwochunk, surf_list, tag_list))
            if logging == 1:
                tobj.pprint("surf_list")
                tobj.pprint(surf_list)
        elif lwochunk.chunkname == "CLIP":                         # texture images
            if logging == 1:
                tobj.pprint("---- CLIP")
            clip_list.append(read_clip(lwochunk, dir_part))
            if logging == 1:
                tobj.pprint("read total %s clips up to now" % len(clip_list))
                tobj.pprint("clip_list")
                tobj.pprint(clip_list)
        else:                                                       # Misc Chunks
            if ask_weird:
                ckname = ie_utils.safestring(lwochunk.chunkname)
                if "#" in ckname:
                    choice = quarkx.msgbox("WARNING: file could be corrupted.%t|Import anyway|Give up", quarkpy.qutils.MT_WARNING, quarkpy.qutils.MB_YES_NO_CANCEL)
                    if choice != MR_YES:
                        if logging == 1:
                            tobj.logcon("---- %s: Maybe file corrupted. Terminated by user" % lwochunk.chunkname)
                        return None
                    ask_weird = 0
            if logging == 1:
                tobj.pprint("---- %s: skipping (maybe later)" % lwochunk.chunkname)
            lwochunk.skip()

    #add default material for orphaned faces, if any
    # QuArK note: may need to figure out what this is, was uncommented.
 #   surf_list.append({'NAME': "_Orphans", 'g_MAT': Blender.Material.New("_Orphans")})

    #pass 2: effectively generate objects
    if logging == 1:
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Pass 2: now for the hard part")
        tobj.logcon ("#####################################################################")
    file.seek(0)
    # === LWO header ===
    form_id, form_size, form_type = struct.unpack(">4s1L4s",  file.read(12))
    if (form_type != "LWO2"):
        if logging == 1:
            tobj.logcon ("??? Inconsistent file type: %s" %form_type)
        return None
    while 1:
        try:
            lwochunk = chunk.Chunk(file)
        except EOFError:
            break
        if logging == 1:
            tobj.pprint(" ")
        if lwochunk.chunkname == "LAYR":
            if logging == 1:
                tobj.pprint("---- LAYR")
            objname = read_layr(lwochunk)
            if logging == 1:
                tobj.pprint(objname)
            if objspec_list != None: #create the object
                polynames = polytag_dict.keys()
                ComponentList, message, CompNbr = create_objects(filename, polynames, clip_list, objspec_list, surf_list, basepath, ComponentList, message, CompNbr)
                update_material(clip_list, objspec_list, surf_list) #give it all the object
            objspec_list = [objname, {}, [], [], {}, {}, 0, {}, {}]
            object_index += 1
        elif lwochunk.chunkname == "PNTS":                         # Verts
            if logging == 1:
                tobj.pprint("---- PNTS, objspec_list[2]")
                tobj.pprint("('verts' SINGLE list of items of all vertex positions, used by ALL comps.)")
                tobj.pprint("(Each item is a list of 3 positions (x, y, z) of one vertex.)")
                tobj.pprint("(Each items position in the list corresponds with their)")
                tobj.pprint("(vertex_index in the 'faces' list, objspec_list[3].)")
            verts = read_verts(lwochunk)
            objspec_list[2] = verts
        elif lwochunk.chunkname == "VMAP":                         # MAPS (UV)
            if logging == 1:
                tobj.pprint("---- VMAP")
            uvcoords_dict = read_vmap(objspec_list[7], len(objspec_list[2]), lwochunk)
            if logging == 1:
                tobj.pprint("uvcoords_dict 1st in VMAP")
                tobj.pprint("total uv's")
                for key in objspec_list[7].keys():
                    tobj.pprint(len(objspec_list[7][key]))
                tobj.pprint("")
                tobj.pprint(objspec_list[7])
        elif lwochunk.chunkname == "VMAD":                         # MAPS (UV) per-face
            if logging == 1:
                tobj.pprint("---- VMAD")
            uvcoords_dict, facesuv_dict = read_vmad(objspec_list[7], objspec_list[8], len(objspec_list[3]), len(objspec_list[2]), lwochunk)
            if logging == 1:
                tobj.pprint("total facesuv_dict")
                for key in objspec_list[8].keys():
                    tobj.pprint(len(objspec_list[8][key]))
        elif lwochunk.chunkname == "POLS": # Faces v6.0
            if logging == 1:
                tobj.pprint("-------- POLS(6), objspec_list[3] ('faces' list)")
                tobj.pprint("STANDARD list of sub-lists, for all Components combined.")
                tobj.pprint("Gives the three vertex_index numbers for each face.")
                tobj.pprint("Use tri_index to get one set.")
            faces, flag = read_faces_6(lwochunk)
            if logging == 1:
                tobj.pprint(faces)
            #flag is 0 for regular polygon, 1 for patches (= subsurf), 2 for anything else to be ignored
            if flag<2:
                if objspec_list[3] != []:
                    #create immediately the object
                    polynames = polytag_dict.keys()
                    ComponentList, message, CompNbr = create_objects(filename, polynames, clip_list, objspec_list, surf_list, basepath, ComponentList, message, CompNbr)
                    update_material(clip_list, objspec_list, surf_list) #give it all the object
                    #update with new data
                    objspec_list = [objspec_list[0],                  #update name
                                    {},                               #init
                                    objspec_list[2],                  #same vertexes
                                    faces,                            #give it the new faces
                                    {},                               #no need to copy - filled at runtime
                                    {},                               #polygon tagging will follow
                                    flag,                             #patch flag
                                    objspec_list[7],                  #same uvcoords
                                    {}]                               #no vmad mapping
                    object_index += 1
                #end if already has a face list
                objspec_list[3] = faces
                objname = objspec_list[0]
                if objname == None:
                    objname = defaultname
            #end if processing a valid poly type
        elif lwochunk.chunkname == "PTAG":                         # PTags
            if logging == 1:
                tobj.pprint("---- PTAG, objspec_list[5] (polytag_dict) tri_index list")
                tobj.pprint("(dict list, uses Component\Texture name as 'key'.)")
            polytag_dict = read_ptags(lwochunk, tag_list)
            for key in polytag_dict.keys():
                objspec_list[5][key] = polytag_dict[key]
        else:
            if logging == 1:                             # Misc Chunks
                tobj.pprint("---- %s: skipping (definitely!)" % lwochunk.chunkname)
            lwochunk.skip()
        #uncomment here to log data structure as it is built
        #tobj.pprint(object_list)
    #last object read
    if logging == 1:
        tobj.pprint("in read_vmad function, objspec_list[7] (uvcoords_dict)")
        tobj.pprint("dict list, uses ['UVNAME'] as key, of dict lists, uses uv_index as keys.")
        tobj.pprint("u,v 2D texture positions, both VMAD & VMAP use this.")
        tobj.pprint("total uv's")
        for key in objspec_list[7].keys():
            tobj.pprint(len(objspec_list[7][key]))
        tobj.pprint("")
        tobj.pprint(uvcoords_dict)
        tobj.pprint("")
        tobj.pprint("")
        tobj.pprint("in read_vmad function, objspec_list[8] (facesuv_dict)")
        tobj.pprint("dict list, uses ['UVNAME'] as key, list of [tri, vert, uv] indexes.")
        tobj.pprint("VMAD only uses this.")
        tobj.pprint("No sub-keys, itterate using:")
        tobj.pprint("if tri_index = [0] and vert_index = [1]: uv_index = [2] (for objspec_list[7])")
        tobj.pprint(facesuv_dict)
        tobj.pprint("")
    polynames = polytag_dict.keys()
    ### The next two lines make it load 10 times slower and have no effect on the u,v problem.
    ### But if commented out will NOT allow multiple component model importing.
    ComponentList, message, CompNbr = create_objects(filename, polynames, clip_list, objspec_list, surf_list, basepath, ComponentList, message, CompNbr)
    update_material(clip_list, objspec_list, surf_list) #give it all the object

    objspec_list = None
    surf_list = None
    clip_list = None

    if logging == 1:
        tobj.pprint ("\n#####################################################################")
        tobj.pprint("Created %d Components:" % object_index)
        tobj.pprint ("#####################################################################")

    return ComponentList, message


# ===========================================================
# === File reading routines =================================
# ===========================================================
# ==================
# === Read Verts ===
# ==================
def read_verts(lwochunk):
    global tobj, logging

    data = cStringIO.StringIO(lwochunk.read())
    numverts = lwochunk.chunksize/12
    verts = [None] * numverts
    # Makes QuArK component.currentframe.verteicies here.
    for i in xrange(numverts):
        x, y, z = struct.unpack(">fff", data.read(12))
        verts[i] = (x, z, y)
    if logging == 1:
        tobj.logcon (verts)
        tobj.pprint("read %d vertexes" % (i+1))
    return verts


# =================
# === Read Name ===
# =================
# modified to deal with odd lenght strings
def read_name(file):
    name = ""
    while 1:
        char = file.read(1)
        if char == "\0": break
        else: name += char
    len_name = len(name) + 1 #count the trailing zero
    if len_name%2==1:
        char = file.read(1) #remove zero padding to even lenght
        len_name += 1
    return name, len_name


# ==================
# === Read Layer ===
# ==================
def read_layr(lwochunk):
    data = cStringIO.StringIO(lwochunk.read())
    idx, flags = struct.unpack(">hh", data.read(4))
    pivot = struct.unpack(">fff", data.read(12))
    layer_name, discard = read_name(data)
    if not layer_name: layer_name = "NoName"
    return layer_name


# ======================
# === Read Faces 5.5 ===
# ======================
def read_faces_5(lwochunk):
    global tobj, logging
    data = cStringIO.StringIO(lwochunk.read())
    faces = []
    i = 0
    while i < lwochunk.chunksize:
        facev = []
        numfaceverts, = struct.unpack(">H", data.read(2))
        for j in xrange(numfaceverts):
            index, = struct.unpack(">H", data.read(2))
            facev.append(index)
        facev.reverse()
        faces.append(facev)
        surfaceindex, = struct.unpack(">H", data.read(2))
        if surfaceindex < 0:
            if logging == 1:
                tobj.logcon ("***Error. Referencing uncorrect surface index")
            return
        i += (4+numfaceverts*2)
    return faces


# ==================================
# === Read Variable-Length Index ===
# ==================================
def read_vx(data):
    byte1, = struct.unpack(">B", data.read(1))
    if byte1 != 0xFF:    # 2-byte index
        byte2, = struct.unpack(">B", data.read(1))
        index = byte1*256 + byte2
        index_size = 2
    else:                # 4-byte index
        byte2, byte3, byte4 = struct.unpack(">3B", data.read(3))
        index = byte2*65536 + byte3*256 + byte4
        index_size = 4
    return index, index_size


# ==================================
# ====== Read Color Map Float ======
# ==================================
def read_vcol(surf_list, lwochunk, data):
    global tobj, logging
  #  intensity = struct.unpack(">f", data.read(4))
    if logging == 1:
        tobj.pprint ("WE ARE IN ----- VCOL:")
    '''    tobj.pprint ("intensity:")
        tobj.pprint (intensity)
    VCOL = {}    #start a brand new: this could be made more smart
    i = 0
    my_uv_dict = {}
    while (i < lwochunk.chunksize - 6):      #4+2 header bytes already read
        vertnum, vnum_size = read_vx(data)
        if logging == 1:
            tobj.pprint ("vertnum = %s, vnum_size = %s" % (vertnum, vnum_size))
        u, v = struct.unpack(">ff", data.read(8))
        my_uv_dict[vertnum] = (u, v)
        i += 8 + vnum_size
    #end loop on uv pairs
    surf_list['VCOL'] = my_uv_dict
    map_type = data.read(4)
    name, i = read_name(data) #i initialized with string lenght + zeros
    if logging == 1:
        tobj.pprint ("map type = %s, name = %s" % (map_type, name))
        tobj.pprint ("Now reading uv data below:")'''

    return


# ============================================
# == Read uvmapping (Quake 4 is using this) ==
# ============================================
def read_vmap(uvcoords_dict, maxvertnum, lwochunk): # u,v per vertex point
    global tobj, logging
    if maxvertnum == 0:
        if logging == 1:
            tobj.pprint ("Found VMAP but no vertexes to map!")
        return uvcoords_dict
    data = cStringIO.StringIO(lwochunk.read())
    map_type = data.read(4)
    if map_type != "TXUV":
        if logging == 1:
            tobj.pprint ("Reading VMAP: No Texture UV map Were Found. Map Type: %s" % map_type)
        return uvcoords_dict
    dimension, = struct.unpack(">H", data.read(2))
    name, i = read_name(data) #i initialized with string lenght + zeros
    if logging == 1:
        tobj.pprint ("TXUV %d %s" % (dimension, name))
    #note if there is already a VMAD it will be lost
    #it is assumed that VMAD will follow the corresponding VMAP
    if uvcoords_dict.has_key(name):
        my_uv_dict = uvcoords_dict[name]          #update existing
    else:
        my_uv_dict = {}    #start a brand new: this could be made more smart
    while (i < lwochunk.chunksize - 6):      #4+2 header bytes already read
        vertnum, vnum_size = read_vx(data)
        u, v = struct.unpack(">ff", data.read(8))
        my_uv_dict[vertnum] = (u, v)
        i += 8 + vnum_size
    #end loop on uv pairs
    uvcoords_dict[name] = my_uv_dict
    #this is a per-vertex mapping AND the uv tuple is vertex-ordered, so faces_uv is the same as faces
    return uvcoords_dict # For VMAP

# ========================
# === Read uvmapping 2 ===
# ========================
def read_vmad(uvcoords_dict, facesuv_dict, maxfacenum, maxvertnum, lwochunk):
    global tobj, logging
    if maxvertnum == 0 or maxfacenum == 0:
        if logging == 1:
            tobj.pprint ("Found VMAD but no vertexes to map!")
        return uvcoords_dict, facesuv_dict
    data = cStringIO.StringIO(lwochunk.read())
    map_type = data.read(4)
    if map_type != "TXUV":
        if logging == 1:
            tobj.pprint ("Reading VMAD: No Texture UV map Were Found. Map Type: %s" % map_type)
        return uvcoords_dict, facesuv_dict
    dimension, = struct.unpack(">H", data.read(2))
    name, i = read_name(data) #i initialized with string lenght + zeros
    if logging == 1:
        tobj.pprint ("TXUV %d %s" % (dimension, name))
    if uvcoords_dict.has_key(name):
        my_uv_dict = uvcoords_dict[name] # update existing objspec_list[7]
    else:
        my_uv_dict = {}    # start a brand new  objspec_list[7]: this could be made more smart
    my_facesuv_list = []   # start a brand new  objspec_list[8]
    newindex = maxvertnum + 10 #why +10? Why not?
    #end variable initialization
    while (i < lwochunk.chunksize - 6):  #4+2 header bytes already read
        vertnum, vnum_size = read_vx(data)
        i += vnum_size
        polynum, vnum_size = read_vx(data)
        i += vnum_size
        u, v = struct.unpack(">ff", data.read(8))
        my_uv_dict[newindex] = (u, v)
        my_facesuv_list.append([polynum, vertnum, newindex])
        newindex += 1
        i += 8
    #end loop on uv pairs
    uvcoords_dict[name] = my_uv_dict
    facesuv_dict[name] = my_facesuv_list
    # QuArK Notes: Make each
    if logging == 1:
        tobj.pprint ("updated %d vertexes data (see data below by texture name)" % (newindex-maxvertnum-10))
    return [uvcoords_dict, facesuv_dict] # For VMAD


# ===============================================================================================
# ======================================== Read tags ============================================
# ================== tag_list is a list of textures used in the model, ex: ======================
# == ['models/mapobjects/chairs/kitchenchair/kitchenchair', 'textures/base_trim/bluetex4s_ed'] ==
# ===============================================================================================
def read_tags(lwochunk):
    data = cStringIO.StringIO(lwochunk.read())
    tag_list = []
    current_tag = ""
    i = 0
    while i < lwochunk.chunksize:
        char = data.read(1)
        if char == "\0":
            tag_list.append(current_tag)
            if (len(current_tag) % 2 == 0):
                char = data.read(1)
            current_tag = ""
        else:
            current_tag += char
        i += 1
    if logging == 1:
        tobj.pprint("read %d tags, list follows:" % len(tag_list))
    return tag_list


# ==================
# === Read Ptags ===
# ==================
def read_ptags(lwochunk, tag_list):
    global tobj, logging
    data = cStringIO.StringIO(lwochunk.read())
    polygon_type = data.read(4)
    if polygon_type != "SURF":
        if logging == 1:
            tobj.pprint ("No Surf Were Found. Polygon Type: %s" % polygon_type)
        return {}
    ptag_dict = {}
    i = 0
    while(i < lwochunk.chunksize-4): #4 bytes polygon type already read
        poln, poln_size = read_vx(data)
        i += poln_size
        surface_index, = struct.unpack(">H", data.read(2))
        if surface_index > (len(tag_list)):
            if logging == 1:
                tobj.pprint ("Reading PTAG: Surf belonging to undefined TAG: %d. Skipping" % tag_index)
            return {}
        i += 2
        tag_key = tag_list[surface_index]
        if not(ptag_dict.has_key(tag_key)):
            ptag_dict[tag_list[surface_index]] = [poln]
        else:
            ptag_dict[tag_list[surface_index]].append(poln)
    if logging == 1:
        tobj.logcon (ptag_dict)
        tobj.pprint ("from tag_list (same as 'poly'):")
    facecount = 0
    for i in ptag_dict.keys():
        if logging == 1:
            tobj.pprint ("    read %d faces for Comp.\Tex. %s" % (len(ptag_dict[i]), i))
        facecount = facecount + len(ptag_dict[i])
    if logging == 1:
        tobj.pprint ("        ------")
        tobj.pprint ("   total %d faces" % (facecount))
    return ptag_dict


# ==================
# === Read Clips ===
# ==================
def read_clip(lwochunk, dir_part):
    global tobj, logging
# img, IMG, g_IMG refers to blender image objects
# ima, IMAG, g_IMAG refers to clip dictionary 'ID' entries: refer to blok and surf
    clip_dict = {}
    data = cStringIO.StringIO(lwochunk.read())
    image_index, = struct.unpack(">L", data.read(4))
    clip_dict['ID'] = image_index
    i = 4
    while(i < lwochunk.chunksize):
        subchunkname, = struct.unpack("4s", data.read(4))
        subchunklen, = struct.unpack(">H", data.read(2))
        if subchunkname == "STIL":
            if logging == 1:
                tobj.pprint("-------- STIL")
            clip_name, k = read_name(data)
            #now split text independently from platform
            #depend on the system where image was saved. NOT the one where the script is run
            no_sep = "\\"
            clip_name = clip_name.replace(no_sep, "/")
            short_name = clip_name.split("/")
            short_name = short_name[len(short_name)-1]
            if (clip_name == "") or (short_name == ""):
                if logging == 1:
                    tobj.pprint ("Reading CLIP: Empty clip name not allowed. Skipping")
                discard = data.read(subchunklen-k)
            clip_dict['NAME'] = clip_name
            clip_dict['BASENAME'] = short_name
        elif subchunkname == "XREF":                           #cross reference another image
            if logging == 1:
                tobj.pprint("-------- XREF")
            image_index, = struct.unpack(">L", data.read(4))
            clip_name, k = read_name(data)
            clip_dict['NAME'] = clip_name
            clip_dict['XREF'] = image_index
        elif subchunkname == "NEGA":                           #negate texture effect
            if logging == 1:
                tobj.pprint("-------- NEGA")
            n, = struct.unpack(">H", data.read(2))
            clip_dict['NEGA'] = n
        else:                                                       # Misc Chunks
            if logging == 1:
                tobj.pprint("-------- CLIP:%s: skipping" % subchunkname)
            discard = data.read(subchunklen)
        i = i + 6 + subchunklen
    #end loop on surf chunks
    if logging == 1:
        tobj.pprint("read image:%s" % clip_dict)
    if clip_dict.has_key('XREF'):
        if logging == 1:
            tobj.pprint("Cross-reference: no image pre-allocated.")
        return clip_dict
    """#look for images
    img = load_image("",clip_dict['NAME'])
    if img == None:
        if logging == 1:
            tobj.pprint (  "***No image %s found: trying LWO file subdir" % clip_dict['NAME'])
        img = load_image(dir_part,clip_dict['BASENAME'])
    if img == None:
        if logging == 1:
            tobj.pprint (  "***No image %s found in directory %s: trying Images subdir" % (clip_dict['BASENAME'], dir_part))
        img = load_image(dir_part+Blender.sys.sep+"Images",clip_dict['BASENAME'])
    if img == None:
        if logging == 1:
            tobj.pprint (  "***No image %s found: trying alternate Images subdir" % clip_dict['BASENAME'])
        img = load_image(dir_part+Blender.sys.sep+".."+Blender.sys.sep+"Images",clip_dict['BASENAME'])
    if img == None:
        if logging == 1:
            tobj.pprint (  "***No image %s found: giving up" % clip_dict['BASENAME'])
    #lucky we are: we have an image
    if logging == 1:
        tobj.pprint ("Image pre-allocated.")
    clip_dict['g_IMG'] = img"""
    return clip_dict


# ===========================
# === Read Surfaces Block ===
# ===========================
def read_surfblok(subchunkdata):
    global tobj, logging
    lenght = len(subchunkdata)
    my_dict = {}
    my_uvname = ""
    data = cStringIO.StringIO(subchunkdata)
    ##############################################################
    # blok header sub-chunk
    ##############################################################
    subchunkname, = struct.unpack("4s", data.read(4))
    subchunklen, = struct.unpack(">h", data.read(2))
    accumulate_i = subchunklen + 6
    if subchunkname != 'IMAP':
        if logging == 1:
            tobj.pprint("---------- SURF: BLOK: not IMAP, got %s: block aborting" % subchunkname)
        return {}, ""
    if logging == 1:
        tobj.pprint ("---------- IMAP")
    ordinal, i = read_name(data)
    my_dict['ORD'] = ordinal
    #my_dict['g_ORD'] = -1
    my_dict['ENAB'] = True
    while(i < subchunklen): # ---------left 6------------------------- loop on header parameters
        sub2chunkname, = struct.unpack("4s", data.read(4))
        sub2chunklen, = struct.unpack(">h", data.read(2))
        i = i + 6 + sub2chunklen
        if sub2chunkname == "CHAN":
            if logging == 1:
                tobj.pprint("------------ CHAN")
            sub2chunkname, = struct.unpack("4s", data.read(4))
            my_dict['CHAN'] = sub2chunkname
            sub2chunklen -= 4
        elif sub2chunkname == "ENAB":                             #only present if is to be disabled
            if logging == 1:
                tobj.pprint("------------ ENAB")
            ena, = struct.unpack(">h", data.read(2))
            my_dict['ENAB'] = ena
            sub2chunklen -= 2
        elif sub2chunkname == "NEGA":                             #only present if is to be enabled
            if logging == 1:
                tobj.pprint("------------ NEGA")
            ena, = struct.unpack(">h", data.read(2))
            if ena == 1:
                my_dict['NEGA'] = ena
            sub2chunklen -= 2
        elif sub2chunkname == "OPAC":                             #only present if is to be disabled
            if logging == 1:
                tobj.pprint("------------ OPAC")
            opa, = struct.unpack(">h", data.read(2))
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['OPAC'] = opa
            my_dict['OPACVAL'] = s
            sub2chunklen -= 6
        elif sub2chunkname == "AXIS":
            if logging == 1:
                tobj.pprint("------------ AXIS")
            ena, = struct.unpack(">h", data.read(2))
            my_dict['DISPLAXIS'] = ena
            sub2chunklen -= 2
        else:                                                       # Misc Chunks
            if logging == 1:
                tobj.pprint("------------ SURF: BLOK: IMAP: %s: skipping" % sub2chunkname)
            discard = data.read(sub2chunklen)
    #end loop on blok header subchunks
    ##############################################################
    # blok attributes sub-chunk
    ##############################################################
    subchunkname, = struct.unpack("4s", data.read(4))
    subchunklen, = struct.unpack(">h", data.read(2))
    accumulate_i += subchunklen + 6
    if subchunkname != 'TMAP':
        if logging == 1:
            tobj.pprint("---------- SURF: BLOK: not TMAP, got %s: block aborting" % subchunkname)
        return {}, ""
    if logging == 1:
        tobj.pprint ("---------- TMAP")
    i = 0
    while(i < subchunklen): # -----------left 6----------------------- loop on header parameters
        sub2chunkname, = struct.unpack("4s", data.read(4))
        sub2chunklen, = struct.unpack(">h", data.read(2))
        i = i + 6 + sub2chunklen
        if sub2chunkname == "CNTR":
            if logging == 1:
                tobj.pprint("------------ CNTR")
            x, y, z = struct.unpack(">fff", data.read(12))
            envelope, env_size = read_vx(data)
            my_dict['CNTR'] = [x, y, z]
            sub2chunklen -= (12+env_size)
        elif sub2chunkname == "SIZE":
            if logging == 1:
                tobj.pprint("------------ SIZE")
            x, y, z = struct.unpack(">fff", data.read(12))
            envelope, env_size = read_vx(data)
            my_dict['SIZE'] = [x, y, z]
            sub2chunklen -= (12+env_size)
        elif sub2chunkname == "ROTA":
            if logging == 1:
                tobj.pprint("------------ ROTA")
            x, y, z = struct.unpack(">fff", data.read(12))
            envelope, env_size = read_vx(data)
            my_dict['ROTA'] = [x, y, z]
            sub2chunklen -= (12+env_size)
        elif sub2chunkname == "CSYS":
            if logging == 1:
                tobj.pprint("------------ CSYS")
            ena, = struct.unpack(">h", data.read(2))
            my_dict['CSYS'] = ena
            sub2chunklen -= 2
        else:                                                       # Misc Chunks
            if logging == 1:
                tobj.pprint("------------ SURF: BLOK: TMAP: %s: skipping" % sub2chunkname)
        if  sub2chunklen > 0:
            discard = data.read(sub2chunklen)
    #end loop on blok attributes subchunks
    ##############################################################
    # ok, now other attributes without sub_chunks
    ##############################################################
    while(accumulate_i < lenght): # ---------------------------------- loop on header parameters: lenght has already stripped the 6 bypes header
        subchunkname, = struct.unpack("4s", data.read(4))
        subchunklen, = struct.unpack(">H", data.read(2))
        accumulate_i = accumulate_i + 6 + subchunklen
        if subchunkname == "PROJ":
            if logging == 1:
                tobj.pprint("---------- PROJ")
            p, = struct.unpack(">h", data.read(2))
            my_dict['PROJ'] = p
            subchunklen -= 2
        elif subchunkname == "AXIS":
            if logging == 1:
                tobj.pprint("---------- AXIS")
            a, = struct.unpack(">h", data.read(2))
            my_dict['MAJAXIS'] = a
            subchunklen -= 2
        elif subchunkname == "IMAG":
            if logging == 1:
                tobj.pprint("---------- IMAG")
            i, i_size = read_vx(data)
            my_dict['IMAG'] = i
            subchunklen -= i_size
        elif subchunkname == "WRAP":
            if logging == 1:
                tobj.pprint("---------- WRAP")
            ww, wh = struct.unpack(">hh", data.read(4))
            #reduce width and height to just 1 parameter for both
            my_dict['WRAP'] = max([ww,wh])
            #my_dict['WRAPWIDTH'] = ww
            #my_dict['WRAPHEIGHT'] = wh
            subchunklen -= 4
        elif subchunkname == "WRPW":
            if logging == 1:
                tobj.pprint("---------- WRPW")
            w, = struct.unpack(">f", data.read(4))
            my_dict['WRPW'] = w
            envelope, env_size = read_vx(data)
            subchunklen -= (env_size+4)
        elif subchunkname == "WRPH":
            if logging == 1:
                tobj.pprint("---------- WRPH")
            w, = struct.unpack(">f", data.read(4))
            my_dict['WRPH'] = w
            envelope, env_size = read_vx(data)
            subchunklen -= (env_size+4)
        elif subchunkname == "VMAP":
            if logging == 1:
                tobj.pprint("---------- VMAP")
            vmp, i = read_name(data)
            my_dict['VMAP'] = vmp
            my_uvname = vmp
            subchunklen -= i
        else:                                                    # Misc Chunks
            if logging == 1:
                tobj.pprint("---------- SURF: BLOK: %s: skipping" % subchunkname)
        if  subchunklen > 0:
            discard = data.read(subchunklen)
    #end loop on blok subchunks
    return my_dict, my_uvname


# =====================
# === Read Surfaces ===
# =====================
def read_surfs(lwochunk, surf_list, tag_list):
    global tobj, logging
    my_dict = {}
    data = cStringIO.StringIO(lwochunk.read())
    surf_name, i = read_name(data)
    parent_name, j = read_name(data)
    i += j
    if (surf_name == "") or not(surf_name in tag_list):
        if logging == 1:
            tobj.pprint ("Reading SURF: Actually empty surf name not allowed. Skipping")
        return {}
    if (parent_name != ""):
        parent_index = [x['NAME'] for x in surf_list].count(parent_name)
        if parent_index >0:
            my_dict = surf_list[parent_index-1]
    my_dict['NAME'] = surf_name
    if logging == 1:
        tobj.pprint ("Surface data for TAG (Model Component\Texture)")
        tobj.pprint ("    %s" % surf_name)
    while(i < lwochunk.chunksize):
        subchunkname, = struct.unpack("4s", data.read(4))
        subchunklen, = struct.unpack(">H", data.read(2))
        i = i + 6 + subchunklen #6 bytes subchunk header
        if subchunkname == "COLR":             #color: mapped on color
            if logging == 1:
                tobj.pprint("-------- COLR")
            r, g, b = struct.unpack(">fff", data.read(12))
            envelope, env_size = read_vx(data)
            my_dict['COLR'] = [r, g, b]
            subchunklen -= (12+env_size)
        elif subchunkname == "DIFF":           #diffusion: mapped on reflection (diffuse shader)
            if logging == 1:
                tobj.pprint("-------- DIFF")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['DIFF'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "SPEC":           #specularity: mapped to specularity (spec shader)
            if logging == 1:
                tobj.pprint("-------- SPEC")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['SPEC'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "REFL":           #reflection: mapped on raymirror
            if logging == 1:
                tobj.pprint("-------- REFL")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['REFL'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "TRNL":           #translucency: mapped on same param
            if logging == 1:
                tobj.pprint("-------- TRNL")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['TRNL'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "GLOS":           #glossiness: mapped on specularity hardness (spec shader)
            if logging == 1:
                tobj.pprint("-------- GLOS")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['GLOS'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "TRAN":           #transparency: inverted and mapped on alpha channel
            if logging == 1:
                tobj.pprint("-------- TRAN")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['TRAN'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "LUMI":           #luminosity: mapped on emit channel
            if logging == 1:
                tobj.pprint("-------- LUMI")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['LUMI'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "GVAL":           #glow: mapped on add channel
            if logging == 1:
                tobj.pprint("-------- GVAL")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['GVAL'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "SMAN":           #smoothing angle
            if logging == 1:
                tobj.pprint("-------- SMAN")
            s, = struct.unpack(">f", data.read(4))
            my_dict['SMAN'] = s
            subchunklen -= 4
        elif subchunkname == "SIDE":           #double sided?
            if logging == 1:
                tobj.pprint("-------- SIDE")       #if 1 side do not define key
            s, = struct.unpack(">H", data.read(2))
            if s == 3:
                my_dict['SIDE'] = s
            subchunklen -= 2
        elif subchunkname == "RIND":           #Refraction: mapped on IOR
            if logging == 1:
                tobj.pprint("-------- RIND")
            s, = struct.unpack(">f", data.read(4))
            envelope, env_size = read_vx(data)
            my_dict['RIND'] = s
            subchunklen -= (4+env_size)
        elif subchunkname == "BLOK":           #blocks
            if logging == 1:
                tobj.pprint("-------- BLOK")
            rr, uvname = read_surfblok(data.read(subchunklen))
            #paranoia setting: preventing adding an empty dict
            if rr != {}:
                if not(my_dict.has_key('BLOK')):
                    my_dict['BLOK'] = [rr]
                else:
                    my_dict['BLOK'].append(rr)
            if uvname != "":
                my_dict['UVNAME'] = uvname     #theoretically there could be a number of them: only one used per surf
            if not(my_dict.has_key('g_IMAG')) and (rr.has_key('CHAN')) and (rr.has_key('OPAC')) and (rr.has_key('IMAG')):
                if (rr['CHAN'] == 'COLR') and (rr['OPAC'] == 0):
                    my_dict['g_IMAG'] = rr['IMAG'] #do not set anything, just save image object for later assignment
            subchunklen = 0 #force ending
        else:                                  # Misc Chunks
            if subchunkname == "VCOL":             # MAPS (UV color map)
                if logging == 1:
                    tobj.pprint("---- SURF:VCOL")
                read_vcol(surf_list, lwochunk, data)
            else:
                if logging == 1:
                    tobj.pprint("-------- SURF:%s: skipping" % subchunkname)
        if  subchunklen > 0:
            discard = data.read(subchunklen)
    #end loop on surf chunks
    if my_dict.has_key('BLOK'):
       my_dict['BLOK'].reverse() #texture applied in reverse order with respect to reading from lwo
    #uncomment this if material pre-allocated by read_surf
    # QuArK note: may need to figure out what this is, was uncommented.
    # AW! Looks like it is adding a new Material Texture attached to the 'g_MAT' dictionary key
    # for special texturing like specle mapping or mimp mapping.
 #   my_dict['g_MAT'] = Blender.Material.New(my_dict['NAME'])
    if logging == 1:
        tobj.pprint("-> Material pre-allocated.")
    return my_dict


# ===========================================================
# === Generation Routines ===================================
# ===========================================================
# ==================================================
# === Compute vector distance between two points ===
# ==================================================
def dist_vector (head, tail): #vector from head to tail
    return Blender.Mathutils.Vector([head[0] - tail[0], head[1] - tail[1], head[2] - tail[2]])


# ================
# === Find Ear ===
# ================
def find_ear(normal, list_dict, verts, face):
    global tobj, logging
    nv = len(list_dict['MF'])
    #looping through vertexes trying to find an ear
    #most likely in case of panic
    mlc = 0
    mla = 1
    mlb = 2

    for c in xrange(nv):
        a = (c+1) % nv; b = (a+1) % nv

        if list_dict['P'][a] > 0.0: #we have to start from a convex vertex
        #if (list_dict['P'][a] > 0.0) and (list_dict['P'][b] <= 0.0): #we have to start from a convex vertex
            mlc = c
            mla = a
            mlb = b
            #if logging == 1:
            #    tobj.pprint ("## mmindex: %s, %s, %s  'P': %s, %s, %s" % (c, a, b, list_dict['P'][c],list_dict['P'][a],list_dict['P'][b]))
            #    tobj.pprint ("   ok, this one passed")
            concave = 0
            concave_inside = 0
            for xx in xrange(nv): #looking for concave vertex
                if (list_dict['P'][xx] <= 0.0) and (xx != b) and (xx != c): #cannot be a: it's convex
                    #ok, found concave vertex
                    concave = 1
                    #a, b, c, xx are all meta-meta vertex indexes
                    mva = list_dict['MF'][a] #meta-vertex-index
                    mvb = list_dict['MF'][b]
                    mvc = list_dict['MF'][c]
                    mvxx = list_dict['MF'][xx]
                    va = face[mva] #vertex
                    vb = face[mvb]
                    vc = face[mvc]
                    vxx = face[mvxx]

                    #Distances
                    d_ac_v = list_dict['D'][c]
                    d_ba_v = list_dict['D'][a]
                    d_cb_v = dist_vector(verts[vc], verts[vb])

                    #distance from triangle points
                    d_xxa_v = dist_vector(verts[vxx], verts[va])
                    d_xxb_v = dist_vector(verts[vxx], verts[vb])
                    d_xxc_v = dist_vector(verts[vxx], verts[vc])

                    #normals
                    n_xxa_v = Blender.Mathutils.CrossVecs(d_ba_v, d_xxa_v)
                    n_xxb_v = Blender.Mathutils.CrossVecs(d_cb_v, d_xxb_v)
                    n_xxc_v = Blender.Mathutils.CrossVecs(d_ac_v, d_xxc_v)

                    #how are oriented the normals?
                    p_xxa_v = Blender.Mathutils.DotVecs(normal, n_xxa_v)
                    p_xxb_v = Blender.Mathutils.DotVecs(normal, n_xxb_v)
                    p_xxc_v = Blender.Mathutils.DotVecs(normal, n_xxc_v)

                    #if normals are oriented all to same directions - so it is insida
                    if ((p_xxa_v > 0.0) and (p_xxb_v > 0.0) and (p_xxc_v > 0.0)) or ((p_xxa_v <= 0.0) and (p_xxb_v <= 0.0) and (p_xxc_v <= 0.0)):
                        #print "vertex %d: concave inside" % xx
                        concave_inside = 1
                        break
                #endif found a concave vertex
            #end loop looking for concave vertexes
            if (concave == 0) or (concave_inside == 0):
                #no concave vertexes in polygon (should not be): return immediately
                #looped all concave vertexes and no one inside found
                return [c, a, b]
        #no convex vertex, try another one
    #end loop to find a suitable base vertex for ear
    #looped all candidate ears and find no-one suitable
    if logging == 1:
        tobj.pprint ("Reducing face: no valid ear found to reduce!")
    return [mlc, mla, mlb] #uses most likely




# ====================
# === Reduce Faces ===
# ====================
# http://www-cgrl.cs.mcgill.ca/~godfried/teaching/cg-projects/97/Ian/cutting_ears.html per l'import
def reduce_face(verts, face):
    nv = len (face)
    if nv == 3: return [[0,1,2]] #trivial decomposition list
    list_dict = {}
    #meta-vertex indexes
    list_dict['MF'] = range(nv) # these are meta-vertex-indexes
    list_dict['D'] = [None] * nv
    list_dict['X'] = [None] * nv
    list_dict['P'] = [None] * nv
    #list of distances
    for mvi in list_dict['MF']:
        #vector between two vertexes
        mvi_hiend = (mvi+1) % nv      #last-to-first
        vi_hiend = face[mvi_hiend] #vertex
        vi = face[mvi]
        list_dict['D'][mvi] = dist_vector(verts[vi_hiend], verts[vi])
    #list of cross products - normals evaluated into vertexes
    for vi in xrange(nv):
        list_dict['X'][vi] = Blender.Mathutils.CrossVecs(list_dict['D'][vi], list_dict['D'][vi-1])
    my_face_normal = Blender.Mathutils.Vector([list_dict['X'][0][0], list_dict['X'][0][1], list_dict['X'][0][2]])
    #list of dot products
    list_dict['P'][0] = 1.0
    for vi in xrange(1, nv):
        list_dict['P'][vi] = Blender.Mathutils.DotVecs(my_face_normal, list_dict['X'][vi])
    #is there at least one concave vertex?
    #one_concave = reduce(lambda x, y: (x) or (y<=0.0), list_dict['P'], 0)
    one_concave = reduce(lambda x, y: (x) + (y<0.0), list_dict['P'], 0)
    decomposition_list = []

    while 1:
        if nv == 3: break
        if one_concave:
            #look for triangle
            ct = find_ear(my_face_normal, list_dict, verts, face)
            mv0 = list_dict['MF'][ct[0]] #meta-vertex-index
            mv1 = list_dict['MF'][ct[1]]
            mv2 = list_dict['MF'][ct[2]]
            #add the triangle to output list
            decomposition_list.append([mv0, mv1, mv2])
            #update data structures removing remove middle vertex from list
            #distances
            v0 = face[mv0] #vertex
            v1 = face[mv1]
            v2 = face[mv2]
            list_dict['D'][ct[0]] = dist_vector(verts[v2], verts[v0])
            #cross products
            list_dict['X'][ct[0]] = Blender.Mathutils.CrossVecs(list_dict['D'][ct[0]], list_dict['D'][ct[0]-1])
            list_dict['X'][ct[2]] = Blender.Mathutils.CrossVecs(list_dict['D'][ct[2]], list_dict['D'][ct[0]])
            #list of dot products
            list_dict['P'][ct[0]] = Blender.Mathutils.DotVecs(my_face_normal, list_dict['X'][ct[0]])
            list_dict['P'][ct[2]] = Blender.Mathutils.DotVecs(my_face_normal, list_dict['X'][ct[2]])
            #physical removal
            list_dict['MF'].pop(ct[1])
            list_dict['D'].pop(ct[1])
            list_dict['X'].pop(ct[1])
            list_dict['P'].pop(ct[1])
            one_concave = reduce(lambda x, y: (x) or (y<0.0), list_dict['P'], 0)
            nv -=1
        else: #here if no more concave vertexes
            if nv == 4: break  #quads only if no concave vertexes
            decomposition_list.append([list_dict['MF'][0], list_dict['MF'][1], list_dict['MF'][2]])
            #physical removal
            list_dict['MF'].pop(1)
            nv -=1
    #end while there are more my_face to triangulate
    decomposition_list.append(list_dict['MF'])
    return decomposition_list


# =========================
# === Recalculate Faces ===
# =========================

def get_uvface(complete_list, facenum):
    # extract from the complete list only vertexes of the desired polygon
    my_facelist = []
    for elem in complete_list:
        if elem[0] == facenum:
            my_facelist.append(elem)
    return my_facelist

def get_newindex(polygon_list, vertnum):
    global tobj, logging
    # extract from the polygon list the new index associated to a vertex
    if polygon_list == []:
        return -1
    for elem in polygon_list:
        if elem[1] == vertnum:
            return elem[2]
    #if logging == 1:
    #    tobj.pprint("WARNING: expected vertex %s for polygon %s. Polygon_list dump follows" % (vertnum, polygon_list[0][0]))
    #    tobj.pprint(polygon_list)
    return -1

def get_surf(surf_list, cur_tag):
    for elem in surf_list:
        if elem['NAME'] == cur_tag:
            return elem
    return {}



# ==========================================
# === Revert list (keeping first vertex) ===
# ==========================================
def revert (llist):
    #different flavors: the reverse one is the one that works better
    #rhead = [llist[0]]
    #rtail = llist[1:]
    #rhead.extend(rtail)
    #return rhead
    #--------------
    rhead=rlcopy(llist)
    rhead.reverse()
    return rhead
    #--------------
    #return llist


# ====================================
# === Modified Create Blender Mesh ===
# ====================================
def my_create_mesh(clip_list, surf, objspec_list, current_facelist, objname, not_used_faces):
    global tobj, logging
    #take the needed faces and update the not-used face list
    complete_vertlist = objspec_list[2]
    complete_facelist = objspec_list[3]
    uvcoords_dict = objspec_list[7]
    facesuv_dict = objspec_list[8]
    vertex_map = {} #implementation as dict
    cur_ptag_faces = []
    cur_ptag_faces_indexes = []
    maxface = len(complete_facelist)
    for ff in current_facelist:
        if ff >= maxface:
            if logging == 1:
                tobj.logcon("Non existent face addressed: Giving up with this object")
            return None, not_used_faces              #return the created object
        cur_face = complete_facelist[ff]
        cur_ptag_faces_indexes.append(ff)
        if not_used_faces != []: not_used_faces[ff] = -1
        for vv in cur_face: vertex_map[vv] = 1
    #end loop on faces
    store_edge = 0

    if logging == 10: # Stops repetitive logging of same data making it 3 times faster WITH logging.
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("******************************************************")
        tobj.pprint ("CREATING THE MESH NOW IN my_create_mesh FUNCTION")
        tobj.pprint ("******************************************************")
        tobj.pprint ("")
        tobj.pprint ("clip_list")
        tobj.pprint (clip_list)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("surf")
        tobj.pprint (surf)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("objspec_list")
        tobj.pprint (objspec_list)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("current_facelist")
        tobj.pprint (current_facelist)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("objname")
        tobj.pprint (objname)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("not_used_faces")
        tobj.pprint (not_used_faces)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("******************************************************")
        tobj.pprint ("SPECIFIC ITEMS IN my_create_mesh FUNCTION")
        tobj.pprint ("******************************************************")
        tobj.pprint ("")
        tobj.pprint ("complete_vertlist")
        tobj.pprint (complete_vertlist)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("complete_facelist")
        tobj.pprint (complete_facelist)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("uvcoords_dict")
        tobj.pprint (uvcoords_dict)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("facesuv_dict")
        tobj.pprint (facesuv_dict)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("cur_ptag_faces_indexes")
        tobj.pprint (cur_ptag_faces_indexes)
        tobj.pprint ("")
        tobj.pprint ("")
        tobj.pprint ("maxface")
        tobj.pprint (maxface)
        tobj.pprint ("")
        tobj.pprint ("")

    # cdunde next 2 lines temp, needs more examination to see what we need for QuArK.
    obj = None
    return obj, not_used_faces              #return the created object

    msh = Blender.NMesh.GetRaw()
    # Name the Object
    if not my_meshtools.overwrite_mesh_name:
        objname = my_meshtools.versioned_name(objname)
    Blender.NMesh.PutRaw(msh, objname)    # Name the Mesh
    obj = Blender.Object.GetSelected()[0]
    obj.name=objname
    # Associate material and mesh properties => from create materials
    msh = obj.getData()
    mat_index = len(msh.getMaterials(1))
    mat = None
    if surf.has_key('g_MAT'):
        mat = surf['g_MAT']
        msh.addMaterial(mat)
    msh.mode |= Blender.NMesh.Modes.AUTOSMOOTH #smooth it anyway
    if surf.has_key('SMAN'):
        #not allowed mixed mode mesh (all the mesh is smoothed and all with the same angle)
        #only one smoothing angle will be active! => take the max one
        s = int(surf['SMAN']/3.1415926535897932384626433832795*180.0)     #lwo in radians - blender in degrees
        if msh.getMaxSmoothAngle() < s: msh.setMaxSmoothAngle(s)

    img = None
    if surf.has_key('g_IMAG'):
        ima = lookup_imag(clip_list, surf['g_IMAG'])
        if ima != None:
            img = ima['g_IMG']

    #uv_flag = ((surf.has_key('UVNAME')) and (uvcoords_dict.has_key(surf['UVNAME'])) and (img != None))
    uv_flag = ((surf.has_key('UVNAME')) and (uvcoords_dict.has_key(surf['UVNAME'])))

    if uv_flag:        #assign uv-data; settings at mesh level
        msh.hasFaceUV(1)
    msh.update(1)

    if logging == 1:
        tobj.pprint ("\n#===================================================================#")
        tobj.pprint("Processing Object: %s" % objname)
        tobj.pprint ("#===================================================================#")

    jj = 0
    vertlen = len(vertex_map.keys())
    maxvert = len(complete_vertlist)
    for i in vertex_map.keys():
        if not jj%1000 and my_meshtools.show_progress: Blender.Window.DrawProgressBar(float(i)/vertlen, "Generating Verts")
        if i >= maxvert:
            if logging == 1:
                tobj.logcon("Non existent vertex addressed: Giving up with this object")
            return obj, not_used_faces              #return the created object
        x, y, z = complete_vertlist[i]
        msh.verts.append(Blender.NMesh.Vert(x, y, z))
        vertex_map[i] = jj
        jj += 1
    #end sweep over vertexes

    #append faces
    jj = 0
    for i in cur_ptag_faces_indexes:
        if not jj%1000 and my_meshtools.show_progress: Blender.Window.DrawProgressBar(float(jj)/len(cur_ptag_faces_indexes), "Generating Faces")
        cur_face = complete_facelist[i]
        numfaceverts = len(cur_face)
        vmad_list = []    #empty VMAD in any case
        if uv_flag:    #settings at original face level
            if facesuv_dict.has_key(surf['UVNAME']): #yes = has VMAD; no = has VMAP only
                vmad_list = get_uvface(facesuv_dict[surf['UVNAME']],i)  #this for VMAD

        if numfaceverts == 2:
            #This is not a face is an edge
            store_edge = 1
            if msh.edges == None:  #first run
                msh.addEdgeData()
            #rev_face = revert(cur_face)
            i1 = vertex_map[cur_face[1]]
            i2 = vertex_map[cur_face[0]]
            ee = msh.addEdge(msh.verts[i1],msh.verts[i2])
            ee.flag |= Blender.NMesh.EdgeFlags.EDGEDRAW
            ee.flag |= Blender.NMesh.EdgeFlags.EDGERENDER

        elif numfaceverts == 3:
            #This face is a triangle skip face reduction
            face = Blender.NMesh.Face()
            msh.faces.append(face)
            # Associate face properties => from create materials
            if mat != None: face.materialIndex = mat_index
            face.smooth = 1 #smooth it anyway

            #rev_face = revert(cur_face)
            rev_face = [cur_face[2], cur_face[1], cur_face[0]]

            for vi in rev_face:
                index = vertex_map[vi]
                face.v.append(msh.verts[index])

                if uv_flag:
                    ni = get_newindex(vmad_list, vi)
                    if ni > -1:
                        uv_index = ni
                    else: #VMAP - uses the same criteria as face
                        uv_index = vi
                    if uvcoords_dict[surf['UVNAME']].has_key(uv_index):
                        uv_tuple = uvcoords_dict[surf['UVNAME']][uv_index]
                    else:
                        uv_tuple = (0,0)
                    face.uv.append(uv_tuple)

            if uv_flag and img != None:
                face.mode |= Blender.NMesh.FaceModes['TEX']
                face.image = img
                face.mode |= Blender.NMesh.FaceModes.TWOSIDE                  #set it anyway
                face.transp = Blender.NMesh.FaceTranspModes['SOLID']
                face.flag = Blender.NMesh.FaceTranspModes['SOLID']
                #if surf.has_key('SIDE'):
                #    msh.faces[f].mode |= Blender.NMesh.FaceModes.TWOSIDE             #set it anyway
                if surf.has_key('TRAN') and mat.getAlpha()<1.0:
                    face.transp = Blender.NMesh.FaceTranspModes['ALPHA']

        elif numfaceverts > 3:
            #Reduce all the faces with more than 3 vertexes (& test if the quad is concave .....)

            meta_faces = reduce_face(complete_vertlist, cur_face)        # Indices of triangles.
            for mf in meta_faces:
                face = Blender.NMesh.Face()
                msh.faces.append(face)

                if len(mf) == 3: #triangle
                    #rev_face = revert([cur_face[mf[0]], cur_face[mf[1]], cur_face[mf[2]]])
                    rev_face = [cur_face[mf[2]], cur_face[mf[1]], cur_face[mf[0]]]
                else:        #quads
                    #rev_face = revert([cur_face[mf[0]], cur_face[mf[1]], cur_face[mf[2]], cur_face[mf[3]]])
                    rev_face = [cur_face[mf[3]], cur_face[mf[2]], cur_face[mf[1]], cur_face[mf[0]]]

                # Associate face properties => from create materials
                if mat != None: face.materialIndex = mat_index
                face.smooth = 1 #smooth it anyway

                for vi in rev_face:
                    index = vertex_map[vi]
                    face.v.append(msh.verts[index])

                    if uv_flag:
                        ni = get_newindex(vmad_list, vi)
                        if ni > -1:
                            uv_index = ni
                        else: #VMAP - uses the same criteria as face
                            uv_index = vi
                        if uvcoords_dict[surf['UVNAME']].has_key(uv_index):
                            uv_tuple = uvcoords_dict[surf['UVNAME']][uv_index]
                        else:
                            uv_tuple = (0,0)
                        face.uv.append(uv_tuple)

                if uv_flag and img != None:
                    face.mode |= Blender.NMesh.FaceModes['TEX']
                    face.image = img
                    face.mode |= Blender.NMesh.FaceModes.TWOSIDE                  #set it anyway
                    face.transp = Blender.NMesh.FaceTranspModes['SOLID']
                    face.flag = Blender.NMesh.FaceTranspModes['SOLID']
                    #if surf.has_key('SIDE'):
                    #    msh.faces[f].mode |= Blender.NMesh.FaceModes.TWOSIDE             #set it anyway
                    if surf.has_key('TRAN') and mat.getAlpha()<1.0:
                        face.transp = Blender.NMesh.FaceTranspModes['ALPHA']

        jj += 1

    if not(uv_flag):        #clear eventual UV data
        msh.hasFaceUV(0)
    msh.update(1,store_edge)
  #  Blender.Redraw()
    return obj, not_used_faces              #return the created object


# ============================================
# === Set Subsurf attributes on given mesh ===
# ============================================
def set_subsurf(obj):
    msh = obj.getData()
    msh.setSubDivLevels([2, 2])
    #does not work any more in 2.40 alpha 2
    #msh.mode |= Blender.NMesh.Modes.SUBSURF
    if msh.edges != None:
        msh.update(1,1)
    else:
        msh.update(1)
    obj.makeDisplayList()
    return


# =================================
# === object size and dimension ===
# =================================
def obj_size_pos(obj):
    bbox = obj.getBoundBox()
    bbox_min = map(lambda *row: min(row), *bbox) #transpose & get min
    bbox_max = map(lambda *row: max(row), *bbox) #transpose & get max
    obj_size = (bbox_max[0]-bbox_min[0], bbox_max[1]-bbox_min[1], bbox_max[2]-bbox_min[2])
    obj_pos = ( (bbox_max[0]+bbox_min[0]) / 2, (bbox_max[1]+bbox_min[1]) / 2, (bbox_max[2]+bbox_min[2]) / 2)
    return (obj_size, obj_pos)


# =========================
# === Create the object ===
# =========================
def create_objects(filename, polynames, clip_list, objspec_list, surf_list, basepath, ComponentList, message, CompNbr):
    global Strings
    nf = len(objspec_list[3])
    not_used_faces = range(nf)
    ptag_dict = objspec_list[5]
    uvcoords_dict = objspec_list[7]
    facesuv_dict = objspec_list[8]
    obj_dict = {}  #links tag names to object, used for material assignments
    obj_dim_dict = {}
    obj_list = []  #have it handy for parent association
    middlechar = "+"
    endchar = ""
    if (objspec_list[6] == 1):
        middlechar = endchar = "#"
    for cur_tag in ptag_dict.keys():
        if ptag_dict[cur_tag] != []:
            cur_surf = get_surf(surf_list, cur_tag)
            cur_obj, not_used_faces = my_create_mesh(clip_list, cur_surf, objspec_list, ptag_dict[cur_tag], objspec_list[0][:9]+middlechar+cur_tag[:9], not_used_faces)
            #does not work any more in 2.40 alpha 2
            #if objspec_list[6] == 1:
            #    set_subsurf(cur_obj)
            if cur_obj != None:
                obj_dict[cur_tag] = cur_obj
                obj_dim_dict[cur_tag] = obj_size_pos(cur_obj)
                obj_list.append(cur_obj)
    #end loop on current group
    #and what if some faces not used in any named PTAG? get rid of unused faces
    orphans = []
    for tt in not_used_faces:
        if tt > -1: orphans.append(tt)
    #end sweep on unused face list
    not_used_faces = None
    if orphans != []:
        cur_surf = get_surf(surf_list, "_Orphans")
        cur_obj, not_used_faces = my_create_mesh(clip_list, cur_surf, objspec_list, orphans, objspec_list[0][:9]+middlechar+"Orphans", [])
        if cur_obj != None:
            if objspec_list[6] == 1:
                set_subsurf(cur_obj)
            obj_dict["_Orphans"] = cur_obj
            obj_dim_dict["_Orphans"] = obj_size_pos(cur_obj)
            obj_list.append(cur_obj)
    objspec_list[1] = obj_dict
    objspec_list[4] = obj_dim_dict
 #   scene = Blender.Scene.getCurrent ()                   # get the current scene
 #   ob = Blender.Object.New ('Empty', objspec_list[0]+endchar)    # make empty object
 #   scene.link (ob)                                       # link the object into the scene
 #   ob.makeParent(obj_list, 1, 0)                         # set the root for created objects (no inverse, update scene hyerarchy (slow))
 #   Blender.Redraw()

### This area is where we make the different elements of a QuArK Component, for each Component.
    # Now we start making the elements of each component or "poly".
    polyuvname = None
    UVtype = "VMAP"
    firstcomp = str(CompNbr)
    lastcomp = str(CompNbr + len(polynames)-1)
    for poly in polynames:
        ### For the Skins:sg group.
        # Checks if the model has textures specified with it.
        skinsize = (256, 256)
        skingroup = quarkx.newobj('Skins:sg')
        skingroup['type'] = chr(2)
        skinname = (poly + '.tga')
        skin = quarkx.newobj(skinname)
        skinname = skinname.split('/')

        polyuvlist = None
        for list in surf_list:
            if list['NAME'] == poly and list.has_key('BLOK'):
                for item in list['BLOK']:
                    if item.has_key('VMAP'):
                        UVtype = "VMAP"
            if list['NAME'] == poly and list.has_key('UVNAME'):
                polyuvname = list['UVNAME']
                if uvcoords_dict.has_key(polyuvname):
                    polyuvlist = uvcoords_dict[polyuvname]
                    break
        if polyuvname is None:
            for list in surf_list:
                if list.has_key('UVNAME'):
                    polyuvname = list['UVNAME']
                    break
        if uvcoords_dict != {} and polyuvlist is None:
            testname = skinname[len(skinname)-1].replace('.tga', "")
            if len(uvcoords_dict) == 1:
                if uvcoords_dict.keys()[0].find(testname) != -1:
                    polyuvlist = uvcoords_dict[uvcoords_dict.keys()[0]]
                    polyuvname = uvcoords_dict.keys()[0]
            else:
                for key in uvcoords_dict.keys():
                    if key.find(testname) != -1:
                        polyuvlist = uvcoords_dict[key]
                        polyuvname = key
        if polyuvlist == {}:
            polyuvlist = None

        polyname = poly.rsplit(".")[0]
        name_list = load_image(basepath,polyname)
        foundshader = foundtexture = foundimage = imagefile = None
        mesh_shader = shader_file = shader_name = shader_keyword = qer_editorimage = diffusemap = map = bumpmap = addnormals = heightmap = specularmap = None
        for file in range(len(name_list)):
            if os.path.exists(basepath + "materials") == 1:
                shaderspath = basepath + "materials"
                shaderfiles = os.listdir(shaderspath)
                for shaderfile in shaderfiles:
                    noimage = ""
                    #read the file in
                    try: # To by pass sub-folders, should make this to check those also.
                        read_shader_file=open(shaderspath+"/"+shaderfile,"r")
                    except:
                        continue
                    lines=read_shader_file.readlines()
                    read_shader_file.close()
                    left_cur_braket = 0
                    for line in range(len(lines)):
                        if foundshader is None and lines[line].startswith(polyname+"\n"):
                            shaderline = lines[line].replace(chr(9), "    ")
                            shaderline = shaderline.rstrip()
                            mesh_shader = "\r\n" + shaderline + "\r\n"
                            shader_file = shaderspath + "/" + shaderfile
                            shader_name = polyname
                            foundshader = polyname
                            left_cur_braket = 0
                            continue
                        if foundshader is not None and lines[line].find("{") != -1:
                            left_cur_braket = left_cur_braket + 1
                        if foundshader is not None and lines[line].find("}") != -1:
                            left_cur_braket = left_cur_braket - 1
                        if foundshader is not None:
                            testline = lines[line].strip()
                            if testline.startswith("//"):
                                continue
                            lines[line] = lines[line].replace("\\", "/")
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
                                        if (not skin.name in skingroup.dictitems.keys()) and (not skin.shortname in skingroup.dictitems.keys()):
                                            skin['Image1'] = image.dictspec['Image1']
                                            skin['Size'] = image.dictspec['Size']
                                            skin['shader_keyword'] = shader_keyword
                                            skingroup.appenditem(skin)
                                            if skinsize == (256, 256):
                                                skinsize = skin['Size']
                                            foundtexture = None
                                    else: # Keep looking in the shader files, the shader may be in another one.
                                        imagefile = basepath + foundtexture
                                        noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + polyname + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "and the 'diffusemap' image to display.\r\n    " + foundtexture + "\r\n" + "But that image file does not exist.\r\n"
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
                                        noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + polyname + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                            else:
                                if lines[line].find("/") != -1:
                                    if lines[line-1].find("qer_editorimage") != -1 or lines[line-1].find("diffusemap") != -1 or lines[line-1].find("bumpmap") != -1 or lines[line-1].find("addnormals") != -1 or lines[line-1].find("heightmap") != -1 or lines[line-1].find("specularmap") != -1 or lines[line].find(chr(32)+"map") != -1 or lines[line].find(chr(9)+"map") != -1:
                                        words = lines[line].replace("("," ")
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
                                        if (image is not None) and (not image in skingroup.dictitems.keys()) and (not imagename in skingroup.dictitems.keys()):
                                            words = lines[line-1].replace("("," ")
                                            words = words.replace(")"," ")
                                            words = words.replace(","," ")
                                            words = words.split()
                                            keys = [qer_editorimage, diffusemap, bumpmap, addnormals, heightmap, specularmap, map]
                                            words.reverse() # Work our way backwards to get the last key name first.
                                            for word in range(len(words)):
                                                if (words[word] in keys) and (not skin.name in skingroup.dictitems.keys()) and (not skin.shortname in skingroup.dictitems.keys()):
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
                                                        noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + polyname + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
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
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + polyname + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
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
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + polyname + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
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
                                if (not skin.name in skingroup.dictitems.keys()) and (not skin.shortname in skingroup.dictitems.keys()):
                                    skingroup.appenditem(skin)
                                    if skinsize == (256, 256):
                                        skinsize = skin['Size']
                            else:
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + polyname + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                        if specularmap is not None:
                            imagefile = basepath + specularmap
                            if os.path.isfile(basepath + specularmap):
                                skinname = specularmap
                                foundimage = basepath + skinname
                                shader_keyword = "specularmap"
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
                                noimage = noimage + "\r\nFound needed shader for Import Component " + str(CompNbr) + ":\r\n    " + polyname + "\r\n" + "in\r\n    " + shaderspath+"/"+shaderfile + "\r\n" + "but the texture image file it calls to display\r\n    " + imagefile + "\r\nis not there or has a different name.\r\nMake a copy of the file and rename it or\r\ncheck the shader and make a correction to add it.\r\n"
                        if imagefile is None:
                            imagefile = "NO IMAGE FILE FOUND AT ALL, CHECK THE SHADER."
                        break
                    if foundshader is not None: # Found the shader so break out of the shader files loop.
                        break
                if len(noimage) > 0:
                    message = message + noimage
                if poly is not None and foundshader is None: # This component has an image but no shader was found, so...
                    texturepath = basepath + polyname + ".tga"
                    if os.path.exists(texturepath) == 1: # May not be a shader so we look for a texture with the same image name.
                        skinname = polyname + ".tga"
                        skin = quarkx.newobj(skinname)
                        image = quarkx.openfileobj(texturepath)
                        skin['Image1'] = image.dictspec['Image1']
                        skin['Size'] = image.dictspec['Size']
                        skingroup.appenditem(skin)
                        if skinsize == (256, 256):
                            skinsize = skin['Size']
                    else: # If no texture is found then we are missing the shader.
                        message = message + "\r\nImport Component " + str(CompNbr) + " calls for the shader:\r\n    " + polyname + "\r\n" + "but it could not be located in\r\n    " + shaderspath + "\r\n" + "Extract shader file to this folder\r\nor create a shader file if needed.\r\n"
                try:
                    skinsize = skingroup.subitems[0].dictspec['Size']
                except:
                    pass
                break
            else:
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
                    message = message + "Import Component " + str(CompNbr) + " needs the skin texture\r\n"
                    message = message + (temppath.replace("\\", "/") + polyname + '\r\n')
                    message = message + "But the texture is not in that location.\r\n"
                    message = message + "Look for:\r\n"
                    message = message + ('    ' + polyname + '\r\n')
                    polyuvlist = None
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

        # setup a progress-indicator
        if len(polynames) > 1:
            Strings[2454] = "Processing Components " + firstcomp + " to " + lastcomp + "\n" + "Import Component " + str(CompNbr) + "\n\n" + Strings[2454] # 2nd \n hides original string.
        else:
            Strings[2454] = "Import Component " + str(CompNbr) + "\n" + Strings[2454]
        progressbar = quarkx.progressbar(2454, len(objspec_list[5][poly]))
        ### For the model's 'Tris', this needs to be in binary so we use the 'struct' function.
        Tris = ''
        for key in facesuv_dict.keys():
            if key.find(skinname[len(skinname)-1].replace(".tga", "_0")) != -1: # We half to do it this way because some of these dummy's can't get the path right! 8-\
                keyname = key # Don't change this, we use the keyname again later so we don't have to go through this again.
                uv_list = facesuv_dict[keyname] # Gets the u,v list for this poly using (as a 'key') its name with the _0 added at the end of its name.
                break
            elif key == 'texture':
                keyname = key
                uv_list = facesuv_dict[keyname] # Gets the u,v list for this poly using (as a 'key') its name with the _0 added at the end of its name.
                break
      
        ### For the Frames:fg group and each "name:mf" frame.
        framesgroup = quarkx.newobj('Frames:fg')

        # Because .lwo models are "stagnat" models, (no animation), we only make 1 frame
        # which is used to draw the model's 'mesh' (shape) in the editor's views.
        # The Skin-view uses the model's 'Tris' to draw its nlines. 
        frame = quarkx.newobj('baseframe:mf')
        mesh = ()
        vtxconvert = {}
        count = 0
        TexWidth, TexHeight = skinsize
        for tri in range(len(objspec_list[5][poly])): # tri is the tri_index
            tri_index = objspec_list[5][poly][tri]
            face = objspec_list[3][tri_index] # face is now the tri list of vert_index numbers
            # First make the tri_index (vert_index, u pos, v pos)
            # But since some models have more then one component
            # we need to brake the one long list of vertexes into individual smaller lists,
            # one for each component which means we need to convert the old vertex_index to new ones.
            for i in range(len(face)): # face[i] is the individual vert_index number in this "for" loop.
                u, v = (0, 0)
                if UVtype == "VMAD": # VMAD section
                    for index_group in objspec_list[8][polyuvname]:
                        if tri_index == index_group[0] and face[i] == index_group[1]:
                            uv_index = index_group[2]
                            break
                    u, v = objspec_list[7][polyuvname][uv_index] # VMAD section
                    u = TexWidth * u
                    v = TexHeight * v
                else: # VMAP section
                    if polyuvname is None:
                        pass
                    elif objspec_list[8] == {} or len(objspec_list[8][polyuvname]) == 0:
                        try:
                            u, v = objspec_list[7][polyuvname][face[i]]
                        except:
                            pass
                    else:
                        try:
                            for index_group in range(len(objspec_list[8][polyuvname])): # Original import a few uses this.
                                if tri_index == objspec_list[8][polyuvname][index_group][0] and face[i] == objspec_list[8][polyuvname][index_group][1]:
                                    uv_index = objspec_list[8][polyuvname][index_group][2]
                                    u, v = objspec_list[7][polyuvname][uv_index]
                                    break
                                elif index_group == len(objspec_list[8][polyuvname])-1:
                                    u, v = objspec_list[7][polyuvname][face[i]]
                        except:
                            try:
                                u, v = objspec_list[7][polyuvname][face[i]]
                            except:
                                try:
                                    for index_group in objspec_list[8][polyuvname]:
                                        if tri_index == index_group[0] and face[i] == index_group[1]:
                                            uv_index = index_group[2]
                                            u, v = objspec_list[7][polyuvname][uv_index]
                                            break
                                except:
                                    pass
                try:
                    v = -v
                    u = TexWidth * u
                    v = (TexHeight * v) + TexHeight
                except:
                    u, v = (0, 0)

                if vtxconvert.has_key(face[i]):
                    vert_index = vtxconvert[face[i]]
                    try:
                        Tris = Tris + struct.pack("Hhh", vert_index, u, v)
                    except:
                        u, v = (0, 0)
                        Tris = Tris + struct.pack("Hhh", vert_index, u, v)
                    # Since the vertex is already in the frame Vertices list we don't add them again.
                    # So we use its new vert_index number and just continue.
                else:
                    vert_index = vtxconvert[face[i]] = count
                    count = count + 1
                    try:
                        Tris = Tris + struct.pack("Hhh", vert_index, u, v)
                    except:
                        u, v = (0, 0)
                        Tris = Tris + struct.pack("Hhh", vert_index, u, v)

                    # This is a new vertex, so we add it to the frame['Vertices'] mesh
                    x,y,z = (objspec_list[2][face[i]])
                    mesh = mesh + (x,y,z)
            progressbar.progress()
        frame['Vertices'] = mesh
    #    for list in surf_list:
    #        if list['NAME'] == poly:
    #            if list.has_key("COLR"):
    #                frame['lwo_COLR'] = list['COLR']
        framesgroup.appenditem(frame)

        # Now we start creating our Import Component and name it.
        Component = quarkx.newobj("Import Component " + str(CompNbr) + ':mc')
        # Set it up in the ModelComponentList.
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
        for list in surf_list:
            if list['NAME'] == poly:
                Component['lwo_NAME'] = list['NAME']
                if list.has_key('UVNAME'):
                    Component['lwo_UVNAME'] = list['UVNAME']
                if list.has_key('COLR'):
                    Component['COLR'] = str(quarkx.vect(list['COLR'][0], list['COLR'][1], list['COLR'][2]))
        sdogroup = quarkx.newobj('SDO:sdo')
        Component.appenditem(sdogroup)
        Component.appenditem(skingroup)
        Component.appenditem(framesgroup)
        ComponentList = ComponentList + [Component]
        progressbar.close()
        if len(polynames) > 1:
            Strings[2454] = Strings[2454].replace("Processing Components " + firstcomp + " to " + lastcomp + "\n" + "Import Component " + str(CompNbr) + "\n\n", "")
        else:
            Strings[2454] = Strings[2454].replace("Import Component " + str(CompNbr) + "\n", "")
        CompNbr = CompNbr + 1

    return ComponentList, message, CompNbr


# =====================
# === Load an image ===
# =====================
#extensively search for image name
def load_image(dir_part, name):
    dir_part = dir_part.replace("\\", "/")
    name = name.replace("\\", "/")
    name_list = []
    ext_list = ['.tga', '.dds', '.png', '.jpg', '.bmp']  # Order from best to worst (personal judgement).
    # QuArK is not case sensitive for paths or file names, so we don't need to correct for that.
    for ext in ext_list:
        name_list = name_list + [dir_part + name + ext]
    return name_list


# ===========================================
# === Lookup for image index in clip_list ===
# ===========================================
def lookup_imag(clip_list,ima_id):
    for ii in clip_list:
        if ii['ID'] == ima_id:
            if ii.has_key('XREF'):
                #cross reference - recursively look for images
                return lookup_imag(clip_list, ii['XREF'])
            else:
                return ii
    return None


# ===================================================
# === Create and assign image mapping to material ===
# ===================================================
def create_blok(surf, mat, clip_list, obj_size, obj_pos):
    global tobj, logging

    def output_size_ofs(size, pos, blok):
        global tobj, logging
        #just automate repetitive task
        c_map = [0,1,2]
        c_map_txt = ["    X--", "    -Y-", "    --Z"]
        if blok['MAJAXIS'] == 0:
            c_map = [1,2,0]
        if blok['MAJAXIS'] == 2:
            c_map = [0,2,1]
        if logging == 1:
            tobj.pprint ("!!!axis mapping:")
        for mp in c_map: tobj.pprint (c_map_txt[mp])

        s = ["1.0 (Forced)"] * 3
        o = ["0.0 (Forced)"] * 3
        if blok['SIZE'][0] > 0.0:          #paranoia controls
            s[0] = "%.5f" % (size[0]/blok['SIZE'][0])
            o[0] = "%.5f" % ((blok['CNTR'][0]-pos[0])/blok['SIZE'][0])
        if blok['SIZE'][1] > 0.0:
            s[2] = "%.5f" % (size[2]/blok['SIZE'][1])
            o[2] = "%.5f" % ((blok['CNTR'][1]-pos[2])/blok['SIZE'][1])
        if blok['SIZE'][2] > 0.0:
            s[1] = "%.5f" % (size[1]/blok['SIZE'][2])
            o[1] = "%.5f" % ((blok['CNTR'][2]-pos[1])/blok['SIZE'][2])
        if logging == 1:
            tobj.pprint ("!!!texture size and offsets:")
            tobj.pprint ("    sizeX = %s; sizeY = %s; sizeZ = %s" % (s[c_map[0]], s[c_map[1]], s[c_map[2]]))
            tobj.pprint ("    ofsX = %s; ofsY = %s; ofsZ = %s" % (o[c_map[0]], o[c_map[1]], o[c_map[2]]))
        return

    ti = 0
    for blok in surf['BLOK']:
        if logging == 1:
            tobj.pprint ("#...................................................................#")
            tobj.pprint ("# Processing texture block no.%s for surf %s" % (ti,surf['NAME']))
            tobj.pprint ("#...................................................................#")
            tobj.pdict (blok)
        if ti > 9: break                       #only 8 channels 0..7 allowed for texture mapping
        if not blok['ENAB']:
            if logging == 1:
                tobj.pprint (  "***Image is not ENABled! Quitting this block")
            break
        if not(blok.has_key('IMAG')):
            if logging == 1:
                tobj.pprint (  "***No IMAGe for this block? Quitting")
            break                 #extract out the image index within the clip_list
        if logging == 1:
            tobj.pprint ("looking for image number %d" % blok['IMAG'])
        ima = lookup_imag(clip_list, blok['IMAG'])
        if ima == None:
            if logging == 1:
                tobj.pprint (  "***Block index image not within CLIP list? Quitting Block")
            break                              #safety check (paranoia setting)
        img = ima['g_IMG']
        if img == None:
            if logging == 1:
                tobj.pprint ("***Failed to pre-allocate image %s found: giving up" % ima['BASENAME'])
            break
        tname = str(ima['ID'])
        if blok.has_key('CHAN'):
            tname = tname + "+" + blok['CHAN']
        newtex = Blender.Texture.New(tname)
        newtex.setType('Image')                 # make it an image texture
        newtex.image = img
        #how does it extends beyond borders
        if blok.has_key('WRAP'):
            if (blok['WRAP'] == 3) or (blok['WRAP'] == 2):
                newtex.setExtend('Extend')
            elif (blok['WRAP'] == 1):
                newtex.setExtend('Repeat')
            elif (blok['WRAP'] == 0):
                newtex.setExtend('Clip')
        if logging == 1:
            tobj.pprint ("generated texture %s" % tname)

        blendmode_list = ['Mix',
                         'Subtractive',
                         'Difference',
                         'Multiply',
                         'Divide',
                         'Mix (CalcAlpha already set; try setting Stencil!',
                         'Texture Displacement',
                         'Additive']
        set_blendmode = 7 #default additive
        if blok.has_key('OPAC'):
            set_blendmode = blok['OPAC']
        if set_blendmode == 5: #transparency
            newtex.imageFlags |= Blender.Texture.ImageFlags.CALCALPHA
        if logging == 1:
            tobj.pprint ("!!!Set Texture -> MapTo -> Blending Mode = %s" % blendmode_list[set_blendmode])

        set_dvar = 1.0
        if blok.has_key('OPACVAL'):
            set_dvar = blok['OPACVAL']

        #MapTo is determined by CHAN parameter
        mapflag = Blender.Texture.MapTo.COL  #default to color
        if blok.has_key('CHAN'):
            if blok['CHAN'] == 'COLR':
                if logging == 1:
                    tobj.pprint ("!!!Set Texture -> MapTo -> Col = %.3f" % set_dvar)
            if blok['CHAN'] == 'BUMP':
                mapflag = Blender.Texture.MapTo.NOR
                if logging == 1:
                    tobj.pprint ("!!!Set Texture -> MapTo -> Nor = %.3f" % set_dvar)
            if blok['CHAN'] == 'LUMI':
                mapflag = Blender.Texture.MapTo.EMIT
                if logging == 1:
                    tobj.pprint ("!!!Set Texture -> MapTo -> DVar = %.3f" % set_dvar)
            if blok['CHAN'] == 'DIFF':
                mapflag = Blender.Texture.MapTo.REF
                if logging == 1:
                    tobj.pprint ("!!!Set Texture -> MapTo -> DVar = %.3f" % set_dvar)
            if blok['CHAN'] == 'SPEC':
                mapflag = Blender.Texture.MapTo.SPEC
                if logging == 1:
                    tobj.pprint ("!!!Set Texture -> MapTo -> DVar = %.3f" % set_dvar)
            if blok['CHAN'] == 'TRAN':
                mapflag = Blender.Texture.MapTo.ALPHA
                if logging == 1:
                    tobj.pprint ("!!!Set Texture -> MapTo -> DVar = %.3f" % set_dvar)
        if logging == 1:
            if blok.has_key('NEGA'):
                tobj.pprint ("!!!Watch-out: effect of this texture channel must be INVERTED!")

        #the TexCo flag is determined by PROJ parameter
        if blok.has_key('PROJ'):
            if blok['PROJ'] == 0: #0 - Planar
                if logging == 1:
                    tobj.pprint ("!!!Flat projection")
                coordflag = Blender.Texture.TexCo.ORCO
                output_size_ofs(obj_size, obj_pos, blok)
            elif blok['PROJ'] == 1: #1 - Cylindrical
                if logging == 1:
                    tobj.pprint ("!!!Cylindrical projection")
                coordflag = Blender.Texture.TexCo.ORCO
                output_size_ofs(obj_size, obj_pos, blok)
            elif blok['PROJ'] == 2: #2 - Spherical
                if logging == 1:
                    tobj.pprint ("!!!Spherical projection")
                coordflag = Blender.Texture.TexCo.ORCO
                output_size_ofs(obj_size, obj_pos, blok)
            elif blok['PROJ'] == 3: #3 - Cubic
                if logging == 1:
                    tobj.pprint ("!!!Cubic projection")
                coordflag = Blender.Texture.TexCo.ORCO
                output_size_ofs(obj_size, obj_pos, blok)
            elif blok['PROJ'] == 4: #4 - Front Projection
                if logging == 1:
                    tobj.pprint ("!!!Front projection")
                coordflag = Blender.Texture.TexCo.ORCO
                output_size_ofs(obj_size, obj_pos, blok)
            elif blok['PROJ'] == 5: #5 - UV
                if logging == 1:
                    tobj.pprint ("UVMapped")
                coordflag = Blender.Texture.TexCo.UV
        mat.setTexture(ti, newtex, coordflag, mapflag)
        ti += 1
    #end loop over bloks
    return




# ========================================
# === Create and assign a new material ===
# ========================================
#def update_material(surf_list, ptag_dict, obj, clip_list, uv_dict, dir_part):
def update_material(clip_list, objspec, surf_list):
    global tobj, logging
    if (surf_list == []) or (objspec[5] == {}) or (objspec[1] == {}):
        if logging == 1:
            tobj.pprint( "something getting wrong in update_material: dump follows  ...")
            tobj.pprint( surf_list)
            tobj.pprint( objspec[5])
            tobj.pprint( objspec[1])
        return
    obj_dict = objspec[1]
    all_faces = objspec[3]
    obj_dim_dict = objspec[4]
    ptag_dict = objspec[5]
    uvcoords_dict = objspec[7]
    facesuv_dict = objspec[8]
    for surf in surf_list:
        if (surf['NAME'] in ptag_dict.keys()):
            if logging == 1:
                tobj.pprint ("#-------------------------------------------------------------------#")
                tobj.pprint ("Processing surface (material): %s" % surf['NAME'])
                tobj.pprint ("#-------------------------------------------------------------------#")
            #material set up
            facelist = ptag_dict[surf['NAME']]
            #bounding box and position
            cur_obj = obj_dict[surf['NAME']]
            obj_size = obj_dim_dict[surf['NAME']][0]
            obj_pos = obj_dim_dict[surf['NAME']][1]
            if logging == 1:
                tobj.pprint(surf)
            #uncomment this if material pre-allocated by read_surf
            mat = surf['g_MAT']
            if mat == None:
                if logging == 1:
                    tobj.pprint ("Sorry, no pre-allocated material to update. Giving up for %s." % surf['NAME'])
                break
            #mat = Blender.Material.New(surf['NAME'])
            #surf['g_MAT'] = mat
            if surf.has_key('COLR'):
                mat.rgbCol = surf['COLR']
            if surf.has_key('LUMI'):
                mat.setEmit(surf['LUMI'])
            if surf.has_key('GVAL'):
                mat.setAdd(surf['GVAL'])
            if surf.has_key('SPEC'):
                mat.setSpec(surf['SPEC'])                        #it should be * 2 but seems to be a bit higher lwo [0.0, 1.0] - blender [0.0, 2.0]
            if surf.has_key('DIFF'):
                mat.setRef(surf['DIFF'])                         #lwo [0.0, 1.0] - blender [0.0, 1.0]
            if surf.has_key('REFL'):
                mat.setRayMirr(surf['REFL'])                     #lwo [0.0, 1.0] - blender [0.0, 1.0]
                #mat.setMode('RAYMIRROR') NO! this will reset all the other modes
                #mat.mode |= Blender.Material.Modes.RAYMIRROR No more usable?
                mm = mat.getMode()
                mm |= Blender.Material.Modes.RAYMIRROR
                mm &= 327679 #4FFFF this is implementation dependent
                mat.setMode(mm)
            #WARNING translucency not implemented yet check 2.36 API
            #if surf.has_key('TRNL'):
            #
            if surf.has_key('GLOS'):                             #lwo [0.0, 1.0] - blender [0, 255]
                glo = int(371.67 * surf['GLOS'] - 42.334)        #linear mapping - seems to work better than exp mapping
                if glo <32:  glo = 32                            #clamped to 32-255
                if glo >255: glo = 255
                mat.setHardness(glo)
            if surf.has_key('TRAN'):
                mat.setAlpha(1.0-surf['TRAN'])                                        #lwo [0.0, 1.0] - blender [1.0, 0.0]
                #mat.mode |= Blender.Material.Modes.RAYTRANSP
                mm = mat.getMode()
                mm |= Blender.Material.Modes.RAYTRANSP
                mm &= 327679 #4FFFF this is implementation dependent
                mat.setMode(mm)
            if surf.has_key('RIND'):
                s = surf['RIND']
                if s < 1.0: s = 1.0
                if s > 3.0: s = 3.0
                mat.setIOR(s)                                                         #clipped to blender [1.0, 3.0]
                #mat.mode |= Blender.Material.Modes.RAYTRANSP
                mm = mat.getMode()
                mm |= Blender.Material.Modes.RAYTRANSP
                mm &= 327679 #4FFFF this is implementation dependent
                mat.setMode(mm)
            if surf.has_key('BLOK') and surf['BLOK'] != []:
                #update the material according to texture.
                create_blok(surf, mat, clip_list, obj_size, obj_pos)
            #finished setting up the material
        #end if exist SURF
    #end loop on materials (SURFs)
    return


# ======================
# === Read Faces 6.0 ===
# ======================
def read_faces_6(lwochunk):
    global tobj, logging
    data = cStringIO.StringIO(lwochunk.read())
    faces = []
    polygon_type = data.read(4)
    subsurf = 0
    if polygon_type != "FACE" and polygon_type != "PTCH":
        if logging == 1:
            tobj.pprint("No FACE/PATCH Were Found. Polygon Type: %s" % polygon_type)
        return "", 2
    if polygon_type == 'PTCH': subsurf = 1
    i = 0
    while(i < lwochunk.chunksize-4):
        facev = []
        numfaceverts, = struct.unpack(">H", data.read(2))
        i += 2

        for j in xrange(numfaceverts):
            index, index_size = read_vx(data)
            i += index_size
            facev.append(index)
        faces.append(facev)
    if logging == 1:
        tobj.pprint("read %s total faces for all Components; type of block %d (0=FACE; 1=PATCH)" % (len(faces), subsurf))
    return faces, subsurf



# ===========================================================
# === Start the show and main callback ======================
# ===========================================================

def fs_callback(filename):
    read(filename)

def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename is the full path and name of the .lwo file selected."
    "gamename is None."
    "For example:  C:\Doom 3\base\models\mapobjects\chairs\kitchenchair\kitchenchair.lwo"

    global editor
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
    basepath = basepath.replace("\\", "/")
    if basepath is None:
        return

    ### Line below just runs the importer without the editor being open.
    ### Need to figure out how to open the editor with it & complete the ModelRoot.
  #  import_md2_model(editor, filename)

    ### Lines below here loads the model into the opened editor's current model.
    ModelRoot, ComponentList, message = read(basepath, filename)

    if ModelRoot is None or ComponentList is None or ComponentList == []:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        quarkx.msgbox("Invalid .lwo model.\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
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
            compframes = editor.Root.currentcomponent.findallsubitems("", ':mf')   # get all frames
            for compframe in compframes:
                compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.
            # This needs to be done for each component or bones will not work if used in the editor.
            quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
        editor.ok(undo, str(len(ComponentList)) + " .lwo Components imported")

        editor = None   #Reset the global again
        if message != "":
            message = message + "================================\r\n\r\n"
            message = message + "You need to find and supply the proper texture(s) and folder(s) above.\r\n"
            message = message + "Extract the 'Look for:' folder(s) and file(s) to the 'game' folder.\r\n\r\n"
            message = message + "If a texture does not exist it may be a .dds or some other type of image file.\r\n"
            message = message + "If so then you need to make a .tga file copy of that texture, perhaps in PaintShop Pro.\r\n\r\n"
            message = message + "You may also need to rename it to match the exact name above.\r\n"
            message = message + "Either case, it would be for editing purposes only and should be placed in the model's folder.\r\n\r\n"
            message = message + "Once this is done, then delete the imported components and re-import the model."
            quarkx.textbox("WARNING", "Missing Skin Textures:\r\n\r\n================================\r\n" + message, quarkpy.qutils.MT_WARNING)

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_lightwave_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".lwo LightWave Importer", ".lwo file", "*.lwo", loadmodel, ie_lightwave_import)


def vtxcolorclick(btn):
    if editor is None:
        global editor
        editor = quarkpy.mdleditor.mdleditor # Get the editor.
    if quarkx.setupsubset(3, "Options")["LinearBox"] == "1":
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
    if not quarkx.setupsubset(3, "Options")['VertexUVColor'] or quarkx.setupsubset(3, "Options")['VertexUVColor'] == "0":
        quarkx.setupsubset(3, "Options")['VertexUVColor'] = "1"
        quarkpy.qtoolbar.toggle(btn)
        btn.state = quarkpy.qtoolbar.selected
        quarkx.update(editor.form)
        vtxcolorclick(btn)
    else:
        quarkx.setupsubset(3, "Options")['VertexUVColor'] = "0"
        quarkpy.qtoolbar.toggle(btn)
        btn.state = quarkpy.qtoolbar.normal
        quarkx.update(editor.form)


def dataformname(o):
    "Returns the data form for this type of object 'o' (a model component & others) to use for the Specific/Args page."

    # Next line calls for the Shader Module in mdlentities.py to be used.
    external_skin_editor_dialog_plugin = quarkpy.mdlentities.UseExternalSkinEditor()

    # Next line calls for the Vertex U,V Color Module in mdlentities.py to be used.
    vtx_UVcolor_dialog_plugin = quarkpy.mdlentities.UseVertexUVColors()

    # Next line calls for the Shader Module in mdlentities.py to be used.
    Shader_dialog_plugin = quarkpy.mdlentities.UseShaders()

    dlgdef = """
    {
      Help = "These are the Specific settings for Lightwave (.lwo) model types."$0D
             "Lightwave uses 'levels' the same way that QuArK uses 'components'."$0D
             "Each can have its own special Surface level (or skin texture) settings."$0D0D
             "NOTE: Some games do NOT allow 'TEXTURE TILING' for MODELS, only for SCENES."$0D
             "            Meaning spreading the model faces over repeated image areas of a texture."$0D0D22
             "NAME"$22" - Surface level control name, which is its skin texture name."$0D22
             "edit skin"$22" - Opens this skin texture in an external editor."$0D22
             "UVNAME"$22" - Special UV process control name (over rides 'NAME')."$0D
             "          type in any name you want to use."$0D22
             "COLR"$22" - Color to use for this components 'mapped on color'."$0D
             "          Click the color selector button to the right and pick a color."$0D22
             "IMAG"$22" - Image Map Image. Indicates that this surface is an image map."$0D
             "        Check this if 'CHAN' & 'IMAG' are checked and 'OPAC' is NOT checked."$0D22
             "Vertex Color"$22" - Color to use for this component's u,v vertex color mapping."$0D
             "            Click the color display button to select a color."$0D22
             "shader file"$22" - Gives the full path and name of the .mtr material"$0D
             "           shader file that the selected skin texture uses, if any."$0D22
             "shader name"$22" - Gives the name of the shader located in the above file"$0D
             "           that the selected skin texture uses, if any."$0D22
             "shader keyword"$22" - Gives the above shader 'keyword' that is used to identify"$0D
             "          the currently selected skin texture used in the shader, if any."$0D22
             "shader lines"$22" - Number of lines to display in window below, max. = 35."$0D22
             "edit shader"$22" - Opens shader below in a text editor."$0D22
             "mesh shader"$22" - Contains the full text of this skin texture's shader, if any."$0D
             "          This can be copied to a text file, changed and saved."
      lwo_NAME:   = {t_ModelEditor_texturebrowser = ! Txt="NAME"    Hint="Surface level control name,"$0D"which is its main skin texture name."$0D0D"NOTE: Some games do NOT allow 'TEXTURE TILING'"$0D"for MODELS, only for SCENES."$0D"Meaning spreading the model faces over"$0D"repeated image areas of a texture."}
      """ + external_skin_editor_dialog_plugin + """
      lwo_UVNAME: = {Typ="E"   Txt="UVNAME"  Hint="Special UV process control name (over rides 'NAME'),"$0D"type in any name you want to use."}
      COLR:   = {          Txt="COLR"                                                                          }
      COLR:   = {Typ="L"   Txt="COLR"    Hint="Color to use for this components 'mapped on color'."$0D"Click the color selector button to the right and pick a color."}
      lwo_IMAG:   = {Typ="X"   Txt="IMAG"    Hint="Image Map Image. Indicates that this surface is an image map."$0D"Check this if 'CHAN' & 'IMAG' are checked and 'OPAC' is NOT checked."}
      """ + vtx_UVcolor_dialog_plugin + """
      """ + Shader_dialog_plugin + """
    }
    """

    if editor is None:
        global editor
        editor = quarkpy.mdleditor.mdleditor # Get the editor.
    ico_mdlskv = ico_dict['ico_mdlskv']  # Just to shorten our call later.
    icon_btns = {}                       # Setup our button list, as a dictionary list, to return at the end.
    vtxcolorbtn = quarkpy.qtoolbar.button(colorclick, "Test button for now.||This button is just for testing purposes for right now, does not do anything.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
    # Sets the button to its current status, that might be effected by another importer file, either on or off.
    if quarkx.setupsubset(SS_MODEL, "Options")['VertexUVColor'] == "1":
        vtxcolorbtn.state = quarkpy.qtoolbar.selected
    else:
        vtxcolorbtn.state = quarkpy.qtoolbar.normal
    icon_btns['color'] = vtxcolorbtn     # Put our button in the above list to return.
    # Next line calls for the Vertex Weights system in mdlentities.py to be used.
    vtxweightsbtn = quarkpy.qtoolbar.button(quarkpy.mdlentities.UseVertexWeights, "Open or Update\nVertex Weights Dialog||When clicked, this button opens the dialog to allow the 'weight' movement setting of single vertexes that have been assigned to more then one bone handle.\n\nClick the InfoBase button or press F1 again for more detail.|intro.modeleditor.dataforms.html#specsargsview", ico_mdlskv, 5)
    vtxweightsbtn.state = quarkpy.qtoolbar.normal
    vtxweightsbtn.caption = "" # Texts shows next to button and keeps the width of this button so it doesn't change.
    icon_btns['vtxweights'] = vtxweightsbtn   # Put our button in the above list to return.

    if (editor.Root.currentcomponent.currentskin is not None) and (o.name == editor.Root.currentcomponent.currentskin.name): # If this is not done it will cause looping through multiple times.
        if o.parent.parent.dictspec.has_key("shader_keyword") and o.dictspec.has_key("shader_keyword"):
            if o.parent.parent.dictspec['shader_keyword'] != o.dictspec['shader_keyword']:
                o.parent.parent['shader_keyword'] = o.dictspec['shader_keyword']

    DummyItem = o
    while (DummyItem.type != ":mc"): # Gets the object's model component.
        DummyItem = DummyItem.parent
    o = DummyItem

    if o.type == ":mc": # Just makes sure what we have is a model component.
        formobj = quarkx.newobj("lwo_mc:form")
        formobj.loadtext(dlgdef)
        return formobj, icon_btns
    else:
        return None, None

def dataforminput(o):
    "Returns the default settings or input data for this type of object 'o' (a model component & others) to use for the Specific/Args page."

    if editor is None:
        global editor
        editor = quarkpy.mdleditor.mdleditor # Get the editor.
    DummyItem = Item = o
    while (DummyItem.type != ":mc"): # Gets the object's model component.
        DummyItem = DummyItem.parent
    o = DummyItem
    if o.type == ":mc": # Just makes sure what we have is a model component.
        if not o.dictspec.has_key('lwo_NAME'):
            if len(o.dictitems['Skins:sg'].subitems) != 0:
               o['lwo_NAME'] = o.dictitems['Skins:sg'].subitems[0].name
            else:
               o['lwo_NAME'] = "no skins exist"
      #  if not o.dictspec.has_key('lwo_UVNAME'):
      #      o['lwo_UVNAME'] = o.dictitems['Skins:sg'].subitems[0].name
        if not o.dictspec.has_key('COLR'):
            o['COLR'] = "0.75 0.75 0.75"
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
        if not o.dictspec.has_key('shader_lines'):
            if quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] is not None:
                o['shader_lines'] = quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"]
            else:
                o['shader_lines'] = "8"
                quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = o.dictspec['shader_lines']
        else:
            quarkx.setupsubset(SS_MODEL, "Options")["NbrOfShaderLines"] = o.dictspec['shader_lines']
        if not o.dictspec.has_key('mesh_shader'):
            o['mesh_shader'] = "None"

# ----------- REVISION HISTORY ------------
#
# $Log: ie_lightwave_import.py,v $
# Revision 1.43  2011/06/03 20:29:26  danielpharos
# Removed some bad characters from comments.
#
# Revision 1.42  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.41  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.40  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.39  2010/11/06 15:00:47  danielpharos
# Replaced some non-ASCII characters.
#
# Revision 1.38  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.37  2010/10/10 03:24:59  cdunde
# Added support for player models attachment tags.
# To make baseframe name uniform with other files.
#
# Revision 1.36  2010/06/13 15:37:55  cdunde
# Setup Model Editor to allow importing of model from main explorer File menu.
#
# Revision 1.35  2010/05/01 22:54:57  cdunde
# Set default skinsize to match all other importers.
#
# Revision 1.34  2010/05/01 04:25:37  cdunde
# Updated files to help increase editor speed by including necessary ModelComponentList items
# and removing redundant checks and calls to the list.
#
# Revision 1.33  2010/04/23 22:56:55  cdunde
# File cleanup.
#
# Revision 1.32  2009/08/28 07:21:34  cdunde
# Minor comment addition.
#
# Revision 1.31  2009/06/03 05:16:22  cdunde
# Over all updating of Model Editor improvements, bones and model importers.
#
# Revision 1.30  2009/05/01 20:39:34  cdunde
# Moved additional Specific page systems to mdlentities.py as modules.
#
# Revision 1.29  2009/04/28 21:30:56  cdunde
# Model Editor Bone Rebuild merge to HEAD.
# Complete change of bone system.
#
# Revision 1.28  2009/03/26 19:53:12  danielpharos
# Removed redundant variable.
#
# Revision 1.27  2009/03/24 21:46:56  cdunde
# Minor file cleanup.
#
# Revision 1.26  2009/03/24 19:45:14  cdunde
# Help and Hint updates.
#
# Revision 1.25  2009/03/23 19:52:47  cdunde
# Corrections for obtaining shaders and skins properly.
#
# Revision 1.24  2009/03/22 22:02:25  cdunde
# Small error fix.
#
# Revision 1.23  2009/03/17 23:41:01  cdunde
# To fix possible error for shader keyword if any.
#
# Revision 1.22  2009/03/12 19:39:24  cdunde
# Improvements for multiple skin importing.
#
# Revision 1.21  2009/03/11 15:37:09  cdunde
# Added importing of multiple textures for material shader files.
# Added Specifics page display and editing of skins and shaders.
#
# Revision 1.20  2009/01/29 02:13:51  cdunde
# To reverse frame indexing and fix it a better way by DanielPharos.
#
# Revision 1.19  2009/01/26 18:29:12  cdunde
# Update for correct frame index setting.
#
# Revision 1.18  2008/12/16 21:49:05  cdunde
# Fixed UV color button setting from one import file to another.
#
# Revision 1.17  2008/12/15 01:46:35  cdunde
# Slight correction.
#
# Revision 1.16  2008/12/15 01:28:11  cdunde
# To update all importers needed message boxes to new quarkx.textbox function.
#
# Revision 1.15  2008/12/14 22:11:14  cdunde
# Added skin texture editing ability in external editor.
#
# Revision 1.14  2008/12/12 05:41:44  cdunde
# To move all code for lwo UV Color Selection function into the lwo plugins\ie_lightwave_import.py file.
#
# Revision 1.13  2008/12/11 07:07:16  cdunde
# Added custom icon for UV Color mode function.
#
# Revision 1.12  2008/12/10 20:24:48  cdunde
# To move more code into this importer from main mdl files
# and posted notes on related code and things to do still.
#
# Revision 1.11  2008/12/06 19:29:26  cdunde
# To allow Specific page form creation of various item types.
#
# Revision 1.10  2008/11/19 06:16:22  cdunde
# Bones system moved to outside of components for Model Editor completed.
#
# Revision 1.9  2008/11/17 03:03:53  cdunde
# Minor correction to avoid a Specifics page error if no skin exist.
#
# Revision 1.8  2008/10/26 00:07:09  cdunde
# Moved all of the Specifics/Args page code for the Python importers\exports to the importer files.
#
# Revision 1.7  2008/07/24 23:34:11  cdunde
# To fix non-ASCII character from causing python depreciation errors.
#
# Revision 1.6  2008/07/21 18:06:09  cdunde
# Moved all the start and end logging code to ie_utils.py in two functions,
# "default_start_logging" and "default_end_logging" for easer use and consistency.
# Also added logging and progress bars where needed and cleaned up files.
#
# Revision 1.5  2008/07/11 04:34:32  cdunde
# Setup of Specifics\Arg page for model types data and settings.
#
# Revision 1.4  2008/06/29 05:29:08  cdunde
# Minor correction.
#
# Revision 1.3  2008/06/28 14:52:35  cdunde
# Added .lwo lightwave model export support and improved the importer.
#
# Revision 1.2  2008/06/20 05:54:24  cdunde
# Improvements to uv placements.
#
# Revision 1.1  2008/06/17 20:39:13  cdunde
# To add lwo model importer, uv's still not correct though.
# Also added model import\export logging options for file types.
#
#
