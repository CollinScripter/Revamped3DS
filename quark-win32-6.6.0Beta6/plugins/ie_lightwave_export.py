"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Quake 2 .md2 model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_lightwave_export.py,v 1.15 2010/11/09 05:48:10 cdunde Exp $

Info = {
   "plug-in":       "ie_md2_exporter",
   "desc":          "Export selected meshes to LightWave File Format (.lwo). Original code from Blender, lightwave_import.py, author - Anthony D'Agostino (Scorpius)",
   "date":          "June 21 2008",
   "author":        "cdunde/DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 2" }

# +---------------------------------------------------------+
# | Copyright (c) 2002 Anthony D'Agostino                   |
# | http://www.redrival.com/scorpius                        |
# | scorpius@netzero.com                                    |
# | April 21, 2002                                          |
# | Read and write LightWave Object File Format (*.lwo)     |
# +---------------------------------------------------------+

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

import struct, chunk, os, cStringIO, time, operator
import quarkx
import quarkpy.mdleditor
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
logging = 0
exportername = "ie_lightwave_export.py"
textlog = "lwo_ie_log.txt"
progressbar = None
MeshValid = 0
oldminX = 1000000
oldminY = 1000000
oldminZ = 1000000
oldmaxX = -1000000
oldmaxY = -1000000
oldmaxZ = -1000000

months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December']

# ==============================
# === Write LightWave Format ===
# ==============================
def writefile(filename):
    global progressbar, tobj, Strings, MeshValid
    editor = quarkpy.mdleditor.mdleditor
    if editor is None:
        MeshValid = 0
        return
    # "objects" is a list of one or more selected model components for exporting.
    objects = editor.layout.explorer.sellist

    if not objects:
        quarkx.msgbox("No Components have been selected for exporting.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        MeshValid = 0
        return
    for object in objects:
        if not object.name.endswith(":mc"):
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select\ncomponent folders for exporting.\n\nAn item that is not\na component folder\nis in your selections.\nDeselect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            MeshValid = 0
            return

    file = open(filename, "wb")

    text = generate_text() # General comment text that is written to the model file, not really necessary.
    desc = generate_desc() # Just Copyright text that is written to the model file, not really necessary.

    # If you want to write an icon image to the model file you need to un-comment all lines with #1 in front of them,
    # make a 60x60 pixel, 24-Bit Uncompressed, 16 Million color .tga icon image and put it in the QuArK\images folder.
#1    icon = generate_icon() # Just writes the QuArK icon .tga image into the file, not really necessary.

    # "material_names" is a dictionary list of surface indexes (as the 'key') and their related skin texture names.
    material_names = get_used_material_names(objects)

    tags = generate_tags(material_names) # "tags" is just a regular list of the skin names only.
    surfs = generate_surfs(material_names, objects) # Just 'SURF' keys list. Writes the "Surface data for TAG (Model Component\Texture)"

    # Used later to write the above items to the model file.
#1    chunks = [text, desc, icon, tags]
    chunks = [text, desc, tags]

    meshdata = cStringIO.StringIO() # Creates this to write chunks of data in memory then written to the model file later for each component.

    meshes = []
    mesh_names = []
    MeshValid = 0
    for obj_index in range(len(objects)):
        if len(objects[obj_index].dictitems['Frames:fg'].dictitems) == 0:
            quarkx.msgbox("Invalid Component !\n\nThe component '" + objects[obj_index].shortname + "'\ndoes not have a frame in its 'Frames' group\nand will not be included in the model file.\n\nClick 'OK' to continue exporting.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
            continue

        MeshValid = 1

        # "meshname" is the component's single frame's name, its 'key' which is used next.
        meshname = objects[obj_index].dictitems['Frames:fg'].subitems[0].name

        # "obj_index" is the index to a single model component being processed,
        # The obj_index corresponds with its surf_index in the material_names dictionary control list.
        # "mesh" is the component's single frame's actual data 'dictspec' item ['Vertices'].
        # So mesh.dictspec['Vertices'] will return one CONTINIOUS list of all the vertexes x,y,z 3D positions
        # that make up that component's shape (mesh). They are NOT grouped into smaller lists, QuArK does that.
        meshes = meshes + [objects[obj_index].dictitems['Frames:fg'].dictitems[meshname]]
        mesh_names = mesh_names + [objects[obj_index].shortname]

    if MeshValid == 0:
        # No valid mesh found to export!
        return

    # The Surface layer data for each component's skin texture and its related Specifics and Arguments.
    layr = generate_layr(0)

    # 'SURF' specifics and their settings, by texture name as key, the "surf_list" ALSO
    # Makes the list of "tri_index numbers", by texture name as key, objspec_list[5]
    ptag = generate_ptag(objects, material_names)

    # pnts is the "frame.vertices" x,y,z position of each vertex, objspec_list[2]
    # meshvectors are the "Bounding Box" minimum and maximum x,y,z coords for all selected components combined.
    pnts, meshvectors = generate_pnts(meshes, mesh_names)

    # Creation of the bounding box.
    bbox = generate_bbox(meshvectors)

    # pols is a list of the three vertex_index numbers for each face for all Components combined, objspec_list[3]
    # my_uv_dict and my_facesuv_list are dictionary lists with the vertex_index as the 'key' and its related u,v values, used further below.
    pols, full_uv_dict, full_facesuv_list = generate_pols(objects, mesh_names)

    # Creation of the clip data, not active in QuArK right now.
    clip = generate_clip(meshes, material_names)

    write_chunk(meshdata, "LAYR", layr); chunks.append(layr) # The Surface layer data for each component's skin texture and its related Specifics and Arguments.
    write_chunk(meshdata, "PNTS", pnts); chunks.append(pnts) # The "frame.vertices" x,y,z position of each vertex, objspec_list[2]
    write_chunk(meshdata, "BBOX", bbox); chunks.append(bbox) # The "Bounding Box" minimum and maximum x,y,z coords for all selected components combined.
    write_chunk(meshdata, "POLS", pols); chunks.append(pols) # List of the three vertex_index numbers for each face for all Components combined, objspec_list[3]
    write_chunk(meshdata, "PTAG", ptag); chunks.append(ptag) # Makes the list of "tri_index numbers", by texture name as key, objspec_list[5]

    vmap_uv_list = []
    vmad_uv_list = []
    for object_nr in range(len(objects)):
        object = objects[object_nr]
        name = mesh_names[object_nr]
        # Creation of the UVMAP u,v data, using the my_uv_dict (objspec_list[7]) list from above.
        vmap_uv_list = vmap_uv_list + [generate_vmap_uv(object, full_uv_dict[object_nr], name)]

        # Creation of the UVMAD u,v data, using the my_uv_dict (objspec_list[8]) lists from above and my_facesuv_list.
        vmad_uv_list = vmad_uv_list + [generate_vmad_uv(object, full_uv_dict[object_nr], full_facesuv_list[object_nr], name)]

    # Sense QuArK does not have these things right now
    # we are commenting them out until it does.
    # if meshtools.has_vertex_colors(mesh):
    #     if meshtools.average_vcols:
    #         vmap_vc = generate_vmap_vc(mesh)  # per vert
    #     else:
    #         vmad_vc = generate_vmad_vc(mesh)  # per face

    # Original code but not being qualified right now, for future reference only.
    # if meshtools.has_vertex_colors(mesh):
    #     if meshtools.average_vcols:
    #         write_chunk(meshdata, "VMAP", vmap_vc)
    #         chunks.append(vmap_vc)
    #     else:
    #         write_chunk(meshdata, "VMAD", vmad_vc)
    #         chunks.append(vmad_vc)

    # if mesh.hasFaceUV():
    #     write_chunk(meshdata, "VMAD", vmad_uv)
    #     chunks.append(vmad_uv)
    #     write_chunk(meshdata, "CLIP", clip)
    #     chunks.append(clip)

    # Writes the vert_index, u,v data to the model file.
    for vmap_uv in vmap_uv_list:
        write_chunk(meshdata, "VMAP", vmap_uv)
        chunks.append(vmap_uv)
    for vmad_uv in vmad_uv_list:
        write_chunk(meshdata, "VMAD", vmad_uv)
        chunks.append(vmad_uv)

    # Writes the surface data, for each components texture, to the model file.
    for surf in surfs:
        chunks.append(surf)

    date = time.localtime()
    date_chunk = generate_nstring(str(months[date[1]-1]) + " " + str(date[2]) + ", " + str(date[0]))
    chunks.append(date_chunk)

    # Writes the header and previous defined chunks of data (see by name above) to the model file.
    write_header(file, chunks)
#1    write_chunk(file, "ICON", icon) # see notes above for the #1 commented items.
    write_chunk(file, "TEXT", text)
    write_chunk(file, "DESC", desc)
    write_chunk(file, "TAGS", tags)
    file.write(meshdata.getvalue()); meshdata.close()
    for surf in surfs:
        write_chunk(file, "SURF", surf)
    write_chunk(file, "DATE", date_chunk)

    file.close()


# =======================================
# === Generate Null-Terminated String ===
# =======================================
def generate_nstring(string):
    if len(string)%2 == 0:   # even
        string += "\0\0"
    else:                    # odd
        string += "\0"
    return string

# ===============================
# === Get Used Material Names ===
# ===============================
def get_used_material_names(objects):
    # "objects" is a list of model components selected to export.
    # "object" is one of those in the list.
    matnames = {}
    surf_index = 0
    for object in objects:
        skinname = object.dictitems['Skins:sg'].subitems[0].name
        skinname = skinname.split(".")[0]
        matnames[surf_index] = skinname
        surf_index = surf_index + 1

        # We will want to rework this area once we figure out this Vertex Color Map stuff for .lwo files.
	#	objname = object.name
	#	meshname = object.data.name
	#	mesh = Blender.NMesh.GetRaw(meshname)
    #    if not mesh: continue
    #    if (not mesh.materials) and (meshtools.has_vertex_colors(mesh)):
            # vcols only
    #        if meshtools.average_vcols:
    #            matnames["\251 Per-Vert Vertex Colors"] = None
    #        else:
    #            matnames["\251 Per-Face Vertex Colors"] = None
    #    elif (mesh.materials) and (not meshtools.has_vertex_colors(mesh)):
            # materials only
    #        for material in mesh.materials:
    #            matnames[material.name] = None
    #    elif (not mesh.materials) and (not meshtools.has_vertex_colors(mesh)):
            # neither
    #        matnames["\251 Blender Default"] = None
    #    else:
            # both
    #        for material in mesh.materials:
    #            matnames[material.name] = None
    return matnames

# =========================================
# === Generate Tag Strings (TAGS Chunk) ===
# =========================================
def generate_tags(material_names):
    tag_names = []
    for name in range(len(material_names)):
        tag_names = tag_names + [material_names[name]]
    tag_names = map(generate_nstring, tag_names)
    tags_data = reduce(operator.add, tag_names)
    return tags_data

# ========================
# === Generate Surface ===
# ========================
def generate_surface(surf_index, texture_name, object):
    if texture_name.find("\251 Per-") == 0:
        return generate_vcol_surf(surf_index)
    elif texture_name == "\251 QuArK Default":
        return generate_default_surf()
    else:
        return generate_surf(texture_name, object)

# =================================================================
# ======================== Generate Surfs =========================
# ===================== Just 'SURF' keys list. ====================
# == Writes the "Surface data for TAG (Model Component\Texture)" ==
# =================================================================
def generate_surfs(material_names, objects):
    surfaces = []
    for index in range(len(material_names)):
        surfaces = surfaces + [generate_surface(index, material_names[index], objects[index])]
    return surfaces

# ===================================
# === Generate Layer (LAYR Chunk) ===
# ===================================
def generate_layr(layer_index): # Here the surf_index and the obj_index are one in the same.
    data = cStringIO.StringIO()
    data.write(struct.pack(">h", layer_index))   # layer index number
    data.write(struct.pack(">h", 0))            # flags (not being used right now)
    data.write(struct.pack(">fff", 0, 0, 0))    # model origin (could be set by the bbox averaged)
    data.write(generate_nstring("layer "+str(layer_index)))      # skin texture name
    return data.getvalue()

# ==========================================================================
# ====================== Generate Verts (PNTS Chunk) =======================
# == The "frame.vertices" x,y,z position of each vertex, objspec_list[2] ===
# ==========================================================================
# These are a single component's 'Frames:fg' 'baseframe:mf' (there's only one) 'Vertices'.
def generate_pnts(meshes, mesh_names):
    global Strings
    data = cStringIO.StringIO()
    meshvectors = []
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("---- PNTS, objspec_list[2]")
        tobj.logcon ("('verts' SINGLE list of items of all vertex positions.)")
        tobj.logcon ("(Each item is a list of 3 positions (x, y, z) of one vertex.)")
        tobj.logcon ("(Each items position in the list corresponds with their)")
        tobj.logcon ("(vertex_index in the 'faces' list, objspec_list[3].)")
        #tobj.logcon ("read " + str(verts/3) + " total 'frame' vertexes.")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("list:[")
        count = 0
    for mesh_nr in range(len(meshes)):
        mesh = meshes[mesh_nr]
        vertices = mesh.dictspec['Vertices']
        verts = int(len(vertices) / 3)
        # setup a progress-indicator
        Strings[2452] = mesh_names[mesh_nr] + "\n" + Strings[2452]
        progressbar = quarkx.progressbar(2452, verts)
        for i in xrange(verts):
            x, y, z = (vertices[i*3], vertices[i*3+1], vertices[i*3+2])
            if logging == 1:
                tobj.logcon (str(count) + ": (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
                count = count + 1

            meshvectors = meshvectors + [[x, y, z]]
            data.write(struct.pack(">fff", x, z, y))
            progressbar.progress()
        progressbar.close()
        Strings[2452] = Strings[2452].replace(mesh_names[mesh_nr] + "\n", "")
    if logging == 1:
        tobj.logcon ("]")
    return data.getvalue(), meshvectors

# ==========================================
# === Generate Bounding Box (BBOX Chunk) ===
# ==========================================
def generate_bbox(meshvectors):
    data = cStringIO.StringIO()
    def getbbox(meshvector):
        global oldminX, oldminY, oldminZ, oldmaxX, oldmaxY, oldmaxZ
        if oldminX > meshvector[0]:
            oldminX = meshvector[0]
        if oldminY > meshvector[1]:
            oldminY = meshvector[1]
        if oldminZ > meshvector[2]:
            oldminZ = meshvector[2]
        if oldmaxX < meshvector[0]:
            oldmaxX = meshvector[0]
        if oldmaxY < meshvector[1]:
            oldmaxY = meshvector[1]
        if oldmaxZ < meshvector[2]:
            oldmaxZ = meshvector[2]
    map(getbbox, meshvectors)
    data.write(struct.pack(">6f", oldminX, oldminY, oldminZ, oldmaxX, oldmaxY, oldmaxZ))
    return data.getvalue()

# =====================================================
# ========= Average All Vertex Colors (Fast) ==========
# == Original code not being used by QuArK right now ==
# =====================================================
def average_vertexcolors(mesh):
    vertexcolors = {}
    vcolor_add = lambda u, v: [u[0]+v[0], u[1]+v[1], u[2]+v[2], u[3]+v[3]]
    vcolor_div = lambda u, s: [u[0]/s, u[1]/s, u[2]/s, u[3]/s]
    for i in range(len(mesh.faces)):    # get all vcolors that share this vertex
        if not i%100 and meshtools.show_progress:
            Blender.Window.DrawProgressBar(float(i)/len(mesh.verts), "Finding Shared VColors")
        for j in range(len(mesh.faces[i].v)):
            index = mesh.faces[i].v[j].index
            color = mesh.faces[i].col[j]
            r,g,b,a = color.r, color.g, color.b, color.a
            vertexcolors.setdefault(index, []).append([r,g,b,a])
    for i in range(len(vertexcolors)):    # average them
        if not i%100 and meshtools.show_progress:
            Blender.Window.DrawProgressBar(float(i)/len(mesh.verts), "Averaging Vertex Colors")
        vcolor = [0,0,0,0]    # rgba
        for j in range(len(vertexcolors[i])):
            vcolor = vcolor_add(vcolor, vertexcolors[i][j])
        shared = len(vertexcolors[i])
        vertexcolors[i] = vcolor_div(vcolor, shared)
    return vertexcolors

# =====================================================
# === Generate Per-Vert Vertex Colors (VMAP Chunk) ====
# == Original code not being used by QuArK right now ==
# =====================================================
def generate_vmap_vc(mesh):
    data = cStringIO.StringIO()
    data.write("RGB ")                                      # type
    data.write(struct.pack(">H", 3))                        # dimension
    data.write(generate_nstring("QuArK's Vertex Colors"))   # name (replace with texture or component name later)
    vertexcolors = average_vertexcolors(mesh)
    for i in range(len(vertexcolors)):
        r, g, b, a = vertexcolors[i]
        data.write(struct.pack(">H", i)) # vertex index
        data.write(struct.pack(">fff", r/255.0, g/255.0, b/255.0))
    return data.getvalue()

# =====================================================
# === Generate Per-Face Vertex Colors (VMAD Chunk) ====
# == Original code not being used by QuArK right now ==
# =====================================================
def generate_vmad_vc(mesh):
    data = cStringIO.StringIO()
    data.write("RGB ")                                      # type
    data.write(struct.pack(">H", 3))                        # dimension
    data.write(generate_nstring("QuArK's Vertex Colors"))   # name (replace with texture or component name later)
    for i in range(len(mesh.faces)):
        if not i%100 and meshtools.show_progress:
            Blender.Window.DrawProgressBar(float(i)/len(mesh.faces), "Writing Vertex Colors")
        numfaceverts = len(mesh.faces[i].v)
        for j in range(numfaceverts-1, -1, -1):             # Reverse order
            r = mesh.faces[i].col[j].r
            g = mesh.faces[i].col[j].g
            b = mesh.faces[i].col[j].b
            v = mesh.faces[i].v[j].index
            data.write(struct.pack(">H", v)) # vertex index
            data.write(struct.pack(">H", i)) # face index
            data.write(struct.pack(">fff", r/255.0, g/255.0, b/255.0))
    return data.getvalue()

# ================================================
# === Generate Per-Face UV Coords (VMAP Chunk) ===
# ================================================
def generate_vmap_uv(object, my_uv_dict, name): # "object" is one of the selected components being exported.
    global Strings
    # setup a progress-indicator
    Strings[2451] = name + "\nUVMAP " + Strings[2451]
    progressbar = quarkx.progressbar(2451, len(my_uv_dict))
    data = cStringIO.StringIO()
    data.write("TXUV")                                       # type
    data.write(struct.pack(">H", 2))                         # dimension
    skinname = object.dictitems['Skins:sg'].subitems[0].name # texture skin name, Should be the "UVNAME"
    skinname = skinname.split(".")[0]
    data.write(generate_nstring(skinname)) # texture skin name
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("in generate_vmap_uv function, objspec_list[7] (uvcoords_dict)")
        tobj.logcon ("(dict list (uses ['UVNAME'] as key) of dict lists which use uv_index as keys.)")
        tobj.logcon ("(u,v 2D texture positions, both VMAD & VMAP use this.)")
        tobj.logcon ("read " + str(len(my_uv_dict)) + " total uv's")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("dict:{")
        uvlist = {}
    for key in my_uv_dict:
        U, V = my_uv_dict[key]
        if logging == 1:
            uvlist[key] = (U, V)
        data.write(struct.pack(">H", key)) # vertex index
        data.write(struct.pack(">ff", U, V))
        progressbar.progress()
    if logging == 1:
        tobj.logcon (skinname + " : " + str(uvlist))
        tobj.logcon ("}")
    progressbar.close()
    Strings[2451] = Strings[2451].replace(name + "\nUVMAP ", "")
    return data.getvalue()

# ================================================
# === Generate Per-Face UV Coords (VMAD Chunk) ===
# ================================================
def generate_vmad_uv(object, my_uv_dict, my_facesuv_list, name): # "object" is one of the selected components being exported.
    global Strings
    # setup a progress-indicator
    Strings[2451] = name + "\nUVMAD " + Strings[2451]
    progressbar = quarkx.progressbar(2451, len(my_facesuv_list))
    data = cStringIO.StringIO()
    data.write("TXUV")                                       # type
    data.write(struct.pack(">H", 2))                         # dimension
    skinname = object.dictitems['Skins:sg'].subitems[0].name # texture skin name
    skinname = skinname.split(".")[0]
    data.write(generate_nstring(skinname)) # texture skin name, Should be the "UVNAME"
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("in generate_vmad_uv function, objspec_list[8] (facesuv_dict)")
        tobj.logcon ("(dict list (uses ['UVNAME'] as key) of standard lists of [tri, vert, uv] indexes.)")
        tobj.logcon ("(VMAD only uses this. No sub-keys, iterate using:)")
        tobj.logcon ("(if tri_index = [0] and vert_index = [1]: uv_index = [2] -> for objspec_list[7])")
        tobj.logcon ("read " + str(len(my_facesuv_list)) + " total index lists.")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("dict:{")
        uvlist = []
    for item in range(len(my_facesuv_list)):
        i, v, newUV = my_facesuv_list[item]
        U, V = newUV
        if logging == 1:
            uvlist = uvlist + [[i, v, newUV]]
        data.write(struct.pack(">H", v)) # vertex index
        data.write(struct.pack(">H", i)) # face index
        data.write(struct.pack(">ff", U, V))
        progressbar.progress()
    if logging == 1:
        tobj.logcon (skinname + " : " + str(uvlist))
        tobj.logcon ("}")
    progressbar.close()
    Strings[2451] = Strings[2451].replace(name + "\nUVMAD ", "")
    return data.getvalue()

# ======================================
# === Generate Variable-Length Index ===
# ======================================
def generate_vx(index):
    if index < 0xFF00:
        value = struct.pack(">H", index)                 # 2-byte index
    else:
        value = struct.pack(">L", index | 0xFF000000)    # 4-byte index
    return value

# =======================================================================================================
# ============================== Generate Face vert_index list (POLS Chunk) =============================
# == List of the three vertex_index numbers for each face for all Components combined, objspec_list[3] ==
# === And makes the uv_dict of each triangles vertex u,v position values for all Components combined. ===
# =======================================================================================================
def generate_pols(object_list, mesh_names): # "object_list" are all of the selected components being exported.
    global Strings
    data = cStringIO.StringIO()
    data.write("FACE")
    full_uv_dict = []      # start a brand new  objspec_list[7]
    full_facesuv_list = [] # start a brand new  objspec_list[8]
    maxverts_list = []
    count = 0
    for object_nr in range(len(object_list)):
        full_uv_dict = full_uv_dict + [{}]
        my_uv_dict = full_uv_dict[object_nr]
        full_facesuv_list = full_facesuv_list + [[]]
        my_facesuv_list = full_facesuv_list[object_nr]
        object = object_list[object_nr]
        # setup a progress-indicator
        Strings[2450] = mesh_names[object_nr] + "\n" + Strings[2450]
        progressbar = quarkx.progressbar(2450, len(object.triangles))
        tris = object.triangles
        frame = object.dictitems['Frames:fg'].subitems[0].name
        maxverts = len(object.dictitems['Frames:fg'].dictitems[frame].vertices)
        if object_nr == 0:
            maxverts_list = maxverts_list + [maxverts]
            start_index = 0
        else:
            maxverts_list = maxverts_list + [maxverts_list[object_nr-1] + maxverts]
            start_index = maxverts_list[object_nr-1]

        skinname = object.dictitems['Skins:sg'].subitems[0].name
        TexWidth, TexHeight = object.dictitems['Skins:sg'].dictitems[skinname].dictspec['Size']
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("objspec_list[3] ('faces' list)")
            tobj.logcon ("Gives the three vertex_index numbers for each face.")
            tobj.logcon ("Use tri_index to get one set.")
            tobj.logcon ("read " + str(len(tris)) + " total faces for " + skinname.split(".")[0])
            tobj.logcon ("#####################################################################")
            tobj.logcon ("list:[")
        for i in range(len(tris)):
            face = tris[i]
            data.write(struct.pack(">H", len(face))) # Number of vertexes per face.
            if logging == 1:
                facelist = []
            for j in xrange(len(face)):
                index = start_index + face[j][0]
                if logging == 1:
                    facelist = facelist + [index]
                u = face[j][1] / TexWidth
                v = -face[j][2]
                v = (v / TexHeight) + 1
                if my_uv_dict.has_key(index):
                    if (u != my_uv_dict[index][0]) or (v != my_uv_dict[index][1]):
                        my_facesuv_list.append([count, index, (u, v)])
                else:
                    my_uv_dict[index] = (u, v)
                data.write(generate_vx(index))
            if logging == 1:
                tobj.logcon (str(i) + ": " + str(facelist))
            count = count + 1
            progressbar.progress()
        if logging == 1:
            tobj.logcon ("]")
        progressbar.close()
        Strings[2450] = Strings[2450].replace(mesh_names[object_nr] + "\n", "")
    return data.getvalue(), full_uv_dict, full_facesuv_list

# =============================================================================================
# ========================= Generate Polygon Tag Mapping (PTAG Chunk) =========================
# ======== 'SURF' specifics and their settings, by texture name as key, the "surf_list" =======
# == The "polytag_dict" list of "tri_index numbers", by texture name as key, objspec_list[5] ==
# =============================================================================================
def generate_ptag(object_list, material_names): # "object_list" is a list of the selected components being exported.
    global Strings
    data = cStringIO.StringIO()
    data.write("SURF")
    count = 0
    for obj_index in range(len(object_list)):
        object = object_list[obj_index]
        # setup a progress-indicator
        Strings[2453] = object_list[obj_index].shortname + "\n" + Strings[2453]
        progressbar = quarkx.progressbar(2453, len(object.triangles))
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("---- PTAG, objspec_list[5] (polytag_dict) tri_index list")
            tobj.logcon ("(dict list, uses Component\Texture name as 'key'.)")
            tobj.logcon ("read " + str(len(object.triangles)) + " tri_indexes.")
            tobj.logcon ("#####################################################################")
            facelist = []
        for i in range(len(object.triangles)):
            if logging == 1:
                facelist = facelist + [count]
            data.write(generate_vx(count)) # Makes the list of "tri_index numbers", by texture name as key.
    # Sence QuArK does not have this type of face material support, we comment it out until it does.
      #  if (not mesh.materials) and (meshtools.has_vertex_colors(mesh)):        # vcols only
      #      if meshtools.average_vcols:
      #          name = "\251 Per-Vert Vertex Colors"
      #      else:
      #          name = "\251 Per-Face Vertex Colors"
      #  elif (mesh.materials) and (not meshtools.has_vertex_colors(mesh)):        # materials only
      #      idx = mesh.faces[i].mat    #erialIndex
      #      name = mesh.materials[idx].name
      #  elif (not mesh.materials) and (not meshtools.has_vertex_colors(mesh)):    # neither
      #      name = "\251 Blender Default"
      #  else:                                                                        # both
      #      idx = mesh.faces[i].mat
      #      name = mesh.materials[idx].name
      #  names = material_names.keys()
      #  surfidx = names.index(name)

            data.write(struct.pack(">H", obj_index)) # obj_index and surf_index are one in the same.
            count = count + 1
            progressbar.progress()
        if logging == 1:
            tobj.logcon ("dict:{")
            tobj.logcon ("[" + material_names[obj_index] + "] -> " + str(facelist))
            tobj.logcon ("}")
        progressbar.close()
        Strings[2453] = Strings[2453].replace(object_list[obj_index].shortname + "\n", "")
    return data.getvalue()

# ===================================================
# === Generate VC Surface Definition (SURF Chunk) ===
# ===================================================
def generate_vcol_surf(mesh):
    data = cStringIO.StringIO()
    if meshtools.average_vcols and meshtools.has_vertex_colors(mesh):
        surface_name = generate_nstring("\251 Per-Vert Vertex Colors")
    else:
        surface_name = generate_nstring("\251 Per-Face Vertex Colors")
    data.write(surface_name)
    data.write("\0\0")

    data.write("COLR")
    data.write(struct.pack(">H", 14))
    data.write(struct.pack(">fffH", 1, 1, 1, 0))

    data.write("DIFF")
    data.write(struct.pack(">H", 6))
    data.write(struct.pack(">fH", 0.0, 0))

    data.write("LUMI")
    data.write(struct.pack(">H", 6))
    data.write(struct.pack(">fH", 1.0, 0))

    data.write("VCOL")
    data.write(struct.pack(">H", 34))
    data.write(struct.pack(">fH4s", 1.0, 0, "RGB "))  # intensity, envelope, type
    data.write(generate_nstring("QuArK's Vertex Colors")) # name

    data.write("CMNT")  # material comment
    comment = "Vertex Colors: Exported from QuArk Model Editor"
    comment = generate_nstring(comment)
    data.write(struct.pack(">H", len(comment)))
    data.write(comment)
    return data.getvalue()

# ================================================
# === Generate Surface Definition (SURF Chunk) ===
# ======= Makes up the 'SURF' detatil data =======
# ================================================
def generate_surf(material_name, object):
    data = cStringIO.StringIO()
    data.write(generate_nstring(material_name))
    data.write("\0\0")

 #   R,G,B = material.R, material.G, material.B
    if object.dictspec.has_key('lwo_COLR'):
        color = object['lwo_COLR'].split(" ")
        R, G, B = float(color[0]), float(color[1]), float(color[2])
    else:
        R = G = B = 0.78431373834609985
    data.write("COLR")
    data.write(struct.pack(">H", 14))
    data.write(struct.pack(">fffH", R, G, B, 0))

    data.write("LUMI")
    data.write(struct.pack(">H", 6))
  #  data.write(struct.pack(">fH", material.emit, 0))
    data.write(struct.pack(">fH", 0.0, 0))

    data.write("DIFF")
    data.write(struct.pack(">H", 6))
 #   data.write(struct.pack(">fH", material.ref, 0))
    data.write(struct.pack(">fH", 1.0, 0))

    data.write("SPEC")
    data.write(struct.pack(">H", 6))
  #  data.write(struct.pack(">fH", material.spec, 0))
    data.write(struct.pack(">fH", 0.0, 0))

    data.write("GLOS")
    data.write(struct.pack(">H", 6))
  #  gloss = material.hard / (255/2.0)
    gloss = 50 / (255/2.0)
    gloss = round(gloss, 1)
    data.write(struct.pack(">fH", gloss, 0))

    data.write("CMNT")  # material comment
    comment = material_name + ": Exported from QuArk Model Editor"
    comment = generate_nstring(comment)
    data.write(struct.pack(">H", len(comment)))
    data.write(comment)

    # Check if the material contains any image maps
    #mtextures = material.getTextures()                                   # Get a list of textures linked to the material
    mtextures = [material_name]
    for mtex in mtextures:
      #  if (mtex) and (mtex.tex.type == Blender.Texture.Types.IMAGE):    # Check if the texture is of type "IMAGE"
        if mtex:
            data.write("BLOK")                  # Surface BLOK header
            data.write(struct.pack(">H", 104))  # Hardcoded and ugly! Will only handle 1 image per material

            # IMAP subchunk (image map sub header)
            data.write("IMAP")
            data_tmp = cStringIO.StringIO()
            data_tmp.write(struct.pack(">H", 0))  # Hardcoded - not sure what it represents
            data_tmp.write("CHAN")
            data_tmp.write(struct.pack(">H", 4))
            data_tmp.write("COLR")
            data_tmp.write("OPAC")                # Hardcoded texture layer opacity
            data_tmp.write(struct.pack(">H", 8))
            data_tmp.write(struct.pack(">H", 0))
            data_tmp.write(struct.pack(">f", 1.0))
            data_tmp.write(struct.pack(">H", 0))
            data_tmp.write("ENAB")
            data_tmp.write(struct.pack(">HH", 2, 1))  # 1 = texture layer enabled
            data_tmp.write("NEGA")
            data_tmp.write(struct.pack(">HH", 2, 0))  # Disable negative image (1 = invert RGB values)
            data_tmp.write("AXIS")
            data_tmp.write(struct.pack(">HH", 2, 1))
            data.write(struct.pack(">H", len(data_tmp.getvalue())))
            data.write(data_tmp.getvalue())

            ### For some reason this will not allow another model type, like .md3, to be exported.
            # IMAG subchunk
        #    data.write("IMAG")
        #    data.write(struct.pack(">HH", 2, 1))
        #    data.write("PROJ")
        #    data.write(struct.pack(">HH", 2, 5)) # UV projection

            data.write("VMAP")
            uvname = generate_nstring(material_name)
            data.write(struct.pack(">H", len(uvname)))
            data.write(uvname)

    return data.getvalue()

# =============================================
# === Generate Default Surface (SURF Chunk) ===
# =============================================
def generate_default_surf():
    data = cStringIO.StringIO()
    material_name = "\251 QuArK Default"
    data.write(generate_nstring(material_name))
    data.write("\0\0")

    data.write("COLR")
    data.write(struct.pack(">H", 14))
    data.write(struct.pack(">fffH", 1, 1, 1, 0))

    data.write("DIFF")
    data.write(struct.pack(">H", 6))
    data.write(struct.pack(">fH", 0.8, 0))

    data.write("LUMI")
    data.write(struct.pack(">H", 6))
    data.write(struct.pack(">fH", 0, 0))

    data.write("SPEC")
    data.write(struct.pack(">H", 6))
    data.write(struct.pack(">fH", 0.5, 0))

    data.write("GLOS")
    data.write(struct.pack(">H", 6))
    gloss = 50 / (255/2.0)
    gloss = round(gloss, 1)
    data.write(struct.pack(">fH", gloss, 0))

    data.write("CMNT")  # material comment
    comment = material_name + ": Exported from QuArk Model Editor"

    # vals = map(chr, range(164,255,1))
    # keys = range(164,255,1)
    # keys = map(lambda x: `x`, keys)
    # comment = map(None, keys, vals)
    # comment = reduce(operator.add, comment)
    # comment = reduce(operator.add, comment)

    comment = generate_nstring(comment)
    data.write(struct.pack(">H", len(comment)))
    data.write(comment)
    return data.getvalue()

# ============================================
# === Generate Object Comment (TEXT Chunk) ===
# ============================================
def generate_text():
    comment  = "Lightwave Export Script for QuArK\n"
    comment += "by cdunde\n"
    comment += "http://quark.planetquake.gamespy.com/\n"
    return generate_nstring(comment)

# ==============================================
# === Generate Description Line (DESC Chunk) ===
# ==============================================
def generate_desc():
    comment = "Copyright 2008 QuArK Developers"
    return generate_nstring(comment)

# ==================================================
# === Generate Thumbnail Icon Image (ICON Chunk) ===
# ==================================================
def generate_icon():
    data = cStringIO.StringIO()
    file = open(quarkx.exepath + "images/quark.tga", "rb") # 60x60 uncompressed TGA
    file.read(18)
    icon_data = file.read(3600) # ?
    file.close()
    data.write(struct.pack(">HH", 0, 60))
    data.write(icon_data)
    return data.getvalue()

# ===============================================
# === Generate CLIP chunk with STIL subchunks ===
# ===============================================
def generate_clip(mesh, material_names):
    data = cStringIO.StringIO()
    clipid = 1
    # QuArK does not have any of this so we pass it until it does.
  #  for i in range(len(mesh.materials)):                                    # Run through list of materials used by mesh
  #      material = Blender.Material.Get(mesh.materials[i].name)
  #      mtextures = material.getTextures()                                    # Get a list of textures linked to the material
  #      for mtex in mtextures:
  #          if (mtex) and (mtex.tex.type == Blender.Texture.Types.IMAGE):    # Check if the texture is of type "IMAGE"
  #              pathname = mtex.tex.image.filename                            # If full path is needed use filename in place of name
  #              pathname = pathname[0:2] + pathname.replace("\\", "/")[3:]  # Convert to Modo standard path
  #              imagename = generate_nstring(pathname)
  #              data.write(struct.pack(">L", clipid))                       # CLIP sequence/id
  #              data.write("STIL")                                          # STIL image
  #              data.write(struct.pack(">H", len(imagename)))               # Size of image name
  #              data.write(imagename)
  #              clipid += 1
    return data.getvalue()

# ===================
# === Write Chunk ===
# ===================
def write_chunk(file, name, data):
    file.write(name)
    file.write(struct.pack(">L", len(data)))
    file.write(data)

# =============================
# === Write LWO File Header ===
# =============================
def write_header(file, chunks):
    chunk_sizes = map(len, chunks)
    chunk_sizes = reduce(operator.add, chunk_sizes)
    form_size = chunk_sizes + len(chunks)*8 + len("FORM")
    file.write("FORM")
    file.write(struct.pack(">L", form_size))
    file.write("LWO2")

# Saves the model file: root is the actual file,
# filename is the full path and name of the .lwo file to create.
# gamename is None."
# For example:  C:\Doom 3\base\models\mapobjects\chairs\kitchenchair\kitchenchair.lwo
def savemodel(root, filename, gamename, nomessage=0):
    global tobj, logging, exportername, textlog, MeshValid
    import quarkpy.qutils
    editor = quarkpy.mdleditor.mdleditor
    if editor is None:
        return
    if len(editor.layout.explorer.sellist) > 1 and quarkx.setupsubset(3, "Options")["ExpComponentChecks"] == "1":
        frame_count = []
        for item in editor.layout.explorer.sellist:
            if item.type == ":mc":
                frame_count = frame_count + [len(item.dictitems['Frames:fg'].dictitems)]
        if len(frame_count) > 1:
            for item in range(len(frame_count)):
                if item >= len(frame_count)-1:
                    break
                if frame_count[item] != frame_count[item+1]:
                    results = quarkx.msgbox("Number of selected component's frames do not match\nor some frames have identical names.\n\nDo you wish to continue with this export?", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_YES|quarkpy.qutils.MB_NO)
                    if results != 6:
                        return
                    else:
                        break

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    writefile(filename)
    if MeshValid != 0:
        add_to_message = "Any used skin textures that are not a\n.tga, .dds, .png, .jpg or .bmp\nwill need to be created to go with the model"
        ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.


### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".lwo LightWave Exporter", ".lwo file", "*.lwo", savemodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_lightwave_export.py,v $
# Revision 1.15  2010/11/09 05:48:10  cdunde
# To reverse previous changes, some to be reinstated after next release.
#
# Revision 1.14  2010/11/06 13:31:04  danielpharos
# Moved a lot of math-code to ie_utils, and replaced magic constant 3 with variable SS_MODEL.
#
# Revision 1.13  2010/10/10 03:24:59  cdunde
# Added support for player models attachment tags.
# To make baseframe name uniform with other files.
#
# Revision 1.12  2009/03/10 08:00:39  cdunde
# Updates by DanielPharos to fix multiple component models
# to work correctly in game and uv positioning.
#
# Revision 1.11  2009/03/08 04:48:52  cdunde
# To reinstate functions previously removed to get models to show in games.
#
# Revision 1.10  2009/03/07 08:22:13  cdunde
# Update for models to show up in games.
# UVs are not correct and Doom3 requires a .cm collision model file to work.
# Also, only shows one component in games but all components in QuArK.
#
# Revision 1.9  2009/01/29 02:13:51  cdunde
# To reverse frame indexing and fix it a better way by DanielPharos.
#
# Revision 1.8  2008/07/21 18:06:13  cdunde
# Moved all the start and end logging code to ie_utils.py in two functions,
# "default_start_logging" and "default_end_logging" for easer use and consistency.
# Also added logging and progress bars where needed and cleaned up files.
#
# Revision 1.7  2008/07/17 00:28:15  cdunde
# Added option for error checking of selected components before exporting.
#
# Revision 1.6  2008/07/11 04:40:20  cdunde
# Minor correction.
#
# Revision 1.5  2008/07/11 04:38:47  cdunde
# Clean out blank spaces.
#
# Revision 1.4  2008/07/11 04:34:32  cdunde
# Setup of Specifics\Arg page for model types data and settings.
#
# Revision 1.3  2008/06/29 05:29:08  cdunde
# Minor correction.
#
# Revision 1.2  2008/06/28 15:12:06  cdunde
# Minor correction.
#
# Revision 1.1  2008/06/28 14:52:35  cdunde
# Added .lwo lightwave model export support and improved the importer.
#
#
