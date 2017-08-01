# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for Quake3 .md3 model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md3_export.py,v 1.3 2011/03/31 16:13:17 cdunde Exp $


Info = {
   "plug-in":       "ie_md3_exporter",
   "desc":          "This script exports .md3 model files, textures, and animations from QuArK.",
   "date":          "March 11 2010",
   "author":        "cdunde",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import time, os, struct, math
import quarkx
from quarkpy.qutils import *
import quarkpy.mdleditor
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
SS_MODEL = 3
logging = 0
exportername = "ie_md3_export.py"
textlog = "md3_ie_log.txt"
editor = None

# Global .md3 file limits and values.
MAX_QPATH = 64
MD3_XYZ_SCALE = (1.0 / 64.0)


######################################################
# Exporter Functions section
######################################################
# copied from PhaethonH <phaethon@linux.ucla.edu> md3.py
def Encode(normal):
    x, y, z = normal

    # normalise
    l = math.sqrt((x*x) + (y*y) + (z*z))
    if l == 0:
        return 0
    x = x/l
    y = y/l
    z = z/l

    if (x == 0.0) & (y == 0.0) :
        if z > 0.0:
            return 0
        else:
            return (128 << 8)

    # Encode a normal vector into a 16-bit latitude-longitude value
    #lng = math.acos(z)
    #lat = math.acos(x / math.sin(lng))
    #retval = ((lat & 0xFF) << 8) | (lng & 0xFF)
    lng = math.acos(z) * 255 / (2 * math.pi)
    lat = math.atan2(y, x) * 255 / (2 * math.pi)
    retval = ((int(lat) & 0xFF) << 8) | (int(lng) & 0xFF)
    return retval


#q_math
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
# WRITES MESH SHADERS SECTION
######################################################
def write_shaders(filename, comp_list):
    shaders = []
    for comp in comp_list:
        if comp.dictspec.has_key('shader_name') and comp.dictspec['shader_name'] != "None" and not comp.dictspec['shader_name'] in shaders:
            if len(shaders) == 0:
                shadername = filename.replace(".md3", ".shader")
                shaderfile = open(shadername, "w")
            shaders = shaders + [comp.dictspec['shader_name']]
            shader = comp.dictspec['mesh_shader']
            shader = shader.replace("\r\n", "\n")
            shaderfile.write(shader)
    try:
        shaderfile.close()
    except:
        pass


######################################################
# EXPORTER CLASS SECTION
######################################################
class md3Vert:
    xyz = [0, 0, 0]
    normal = 0
    binaryFormat = "<3hh" # Each h = 2 bytes.

    def __init__(self):
        self.xyz = [0, 0, 0]
        self.normal = 0

    def save(self, file):
        tmpData = [0]*4
        tmpData[0] = int(self.xyz[0] / MD3_XYZ_SCALE)
        tmpData[1] = int(self.xyz[1] / MD3_XYZ_SCALE)
        tmpData[2] = int(self.xyz[2] / MD3_XYZ_SCALE)
        tmpData[3] = int(self.normal)
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
        file.write(data)


class md3TexCoord:
    u = 0.0
    v = 0.0
    binaryFormat = "<2f" # Each f = 4 bytes.

    def __init__(self):
        self.u = 0.0
        self.v = 0.0

    def save(self, file):
        tmpData = [0]*2
        tmpData[0] = self.u
        tmpData[1] = self.v
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1])
        file.write(data)


class md3Triangle:
    indexes = [ 0, 0, 0 ]
    binaryFormat = "<3i" # Each i = 4 bytes.

    def __init__(self):
        self.indexes = [ 0, 0, 0 ]

    def save(self, file):
        tmpData = [0]*3
        tmpData[0] = self.indexes[0]
        tmpData[1] = self.indexes[1]
        tmpData[2] = self.indexes[2]
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1], tmpData[2])
        file.write(data)


class md3Shader:
    name = ""
    index = 0
    binaryFormat = "<%dsi" % MAX_QPATH  # name, then 1 int

    def __init__(self):
        self.name = ""
        self.index = 0

    def save(self, file):
        tmpData = [0]*2
        tmpData[0] = self.name
        tmpData[1] = self.index
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1])
        file.write(data)


class md3Surface:
    ofsBegin = 0
    ident = ""
    name = ""
    flags = 0
    numFrames = 0
    numShaders = 0
    numVerts = 0
    numTriangles = 0
    ofsTriangles = 0
    ofsShaders = 0
    ofsUV = 0
    ofsVerts = 0
    ofsEnd = 0
    triangles = []
    shaders = []
    uv = []
    verts = []
    binaryFormat = "<4s%ds10i" % MAX_QPATH  # ident, name, then 10 ints * 4 bytes per int

    def __init__(self):
        self.ofsBegin = 4 + MAX_QPATH + (10 * 4) # For calculating real offsets, starts with its own Surface header count.
        self.ident = "IDP3"
        self.name = ""
        self.flags = 0
        self.numFrames = 0
        self.numShaders = 0
        self.numVerts = 0
        self.numTriangles = 0
        self.ofsTriangles = 0
        self.ofsShaders = 0
        self.ofsUV = 0
        self.ofsVerts = 0
        self.ofsEnd = 0
        self.triangles = []
        self.shaders = []
        self.uv = []
        self.verts = []

    def save(self, file):
        tmpData = [0]*12
        tmpData[0] = self.ident
        tmpData[1] = self.name
        tmpData[2] = self.flags
        tmpData[3] = self.numFrames
        tmpData[4] = self.numShaders
        tmpData[5] = self.numVerts
        tmpData[6] = self.numTriangles
        tmpData[7] = self.ofsTriangles
        tmpData[8] = self.ofsShaders
        tmpData[9] = self.ofsUV
        tmpData[10] = self.ofsVerts
        tmpData[11] = self.ofsEnd
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11])
        file.write(data)

        # Write the shader info.
        for shader in self.shaders:
            shader.save(file)

        # Write the tri info.
        for tri in self.triangles:
            tri.save(file)

        # Write the uv info.
        for uv in self.uv:
            uv.save(file)

        # Write the verts info.
        for i in xrange(self.numFrames):
            for j in xrange(self.numVerts):
                self.verts[(i * self.numVerts) + j].save(file)


class md3Tag:
    name = ""
    origin = [0.0, 0.0, 0.0]
    axis = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    binaryFormat = "<%ds3f9f" % MAX_QPATH  # name, then 12 ints * 4 bytes per int

    def __init__(self):
        self.name = ""
        self.origin = [0.0, 0.0, 0.0]
        self.axis = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]

    def save(self, file):
        tmpData = [0]*13
        tmpData[0] = self.name
        tmpData[1] = self.origin[0]
        tmpData[2] = self.origin[1]
        tmpData[3] = self.origin[2]
        tmpData[4] = self.axis[0]
        tmpData[5] = self.axis[1]
        tmpData[6] = self.axis[2]
        tmpData[7] = self.axis[3]
        tmpData[8] = self.axis[4]
        tmpData[9] = self.axis[5]
        tmpData[10] = self.axis[6]
        tmpData[11] = self.axis[7]
        tmpData[12] = self.axis[8]
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12])
        file.write(data)


class md3Frame:
    mins = [0.0, 0.0, 0.0]
    maxs = [0.0, 0.0, 0.0]
    localOrigin = [0.0, 0.0, 0.0]
    radius = 0.0
    name = ""
    binaryFormat = "<3f3f3ff16s" # 10 f * 4 bytes per f + 16 s * 1 byte per s

    def __init__(self):
        self.mins = [0.0, 0.0, 0.0]
        self.maxs = [0.0, 0.0, 0.0]
        self.localOrigin = [0.0, 0.0, 0.0]
        self.radius = 0.0
        self.name = ""

    def save(self, file):
        tmpData = [0]*11
        tmpData[0] = self.mins[0]
        tmpData[1] = self.mins[1]
        tmpData[2] = self.mins[2]
        tmpData[3] = self.maxs[0]
        tmpData[4] = self.maxs[1]
        tmpData[5] = self.maxs[2]
        tmpData[6] = self.localOrigin[0]
        tmpData[7] = self.localOrigin[1]
        tmpData[8] = self.localOrigin[2]
        tmpData[9] = self.radius
        tmpData[10] = self.name
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10])
        file.write(data)


######################################################
# FILL MD3 DATA STRUCTURE
######################################################
def fill_md3(md3, QuArK_objects):
    # Fill the md3Object header values.
    frames = QuArK_objects.comp_list[0].dictitems['Frames:fg'].subitems
    if len(frames) > 1:
        md3.numFrames = len(frames)-1
    else:
        md3.numFrames = len(frames)
    md3.numTags = len(QuArK_objects.tags)
    md3.numSurfaces = len(QuArK_objects.comp_list)

    # load the frame info
    md3.ofsFrames = md3.header_size
    for frame in xrange(md3.numFrames):
        md3.frames.append(md3Frame())
        # We need to start with the bounding box.
        bounding_box = quarkx.boundingboxof(frames[frame].vertices) # Uses the component's frame.vertices
        # Fill in the frame data.
        mins = bounding_box[0].tuple
        maxs = bounding_box[1].tuple
        md3.frames[frame].mins = mins
        md3.frames[frame].maxs = maxs
        md3.frames[frame].radius = RadiusFromBounds(mins, maxs)
        md3.frames[frame].name = frames[frame].name.split(":")[0]
    md3.header_size = md3.ofsFrames + md3.numFrames * ((10 * 4) + 16)

    # load the tags info
    md3.ofsTags = md3.header_size
    for frame in xrange(md3.numFrames):
        for tag_count in xrange(md3.numTags):
            md3.tags.append(md3Tag())
            tag = QuArK_objects.tags[tag_count]
            tagframe = tag.subitems[frame]
            tag_name = tag.name.split(":")[0]
            tag_name = tag_name.split("_", 1)
            tag_name = tag_name[len(tag_name)-1]
            md3.tags[(frame * md3.numTags) + tag_count].name = tag_name
            md3.tags[(frame * md3.numTags) + tag_count].origin = tagframe.dictspec['origin']
            md3.tags[(frame * md3.numTags) + tag_count].axis = tagframe.dictspec['rotmatrix']
    md3.header_size = md3.ofsTags + (md3.numFrames * md3.numTags * (MAX_QPATH + (12 * 4)))

    # load the surfaces info
    offset_point = md3.ofsSurfaces = md3.header_size
    for surface_count in xrange(md3.numSurfaces):
        md3.surfaces.append(md3Surface())
        cur_md3surface = md3.surfaces[surface_count]
        comp = QuArK_objects.comp_list[surface_count]
        skin = comp.dictitems['Skins:sg'].subitems[0]
        TexWidth, TexHeight = skin.dictspec['Size']
        comp_name = comp.shortname.split("_", 1)
        comp_name = comp_name[len(comp_name)-1]
        cur_md3surface.name = comp_name
        cur_md3surface.numFrames = md3.numFrames

        # load the shader(s) info
        cur_md3surface.ofsShaders = cur_md3surface.ofsBegin
        shader_bytes = 0
        cur_md3surface.shaders.append(md3Shader())
        shader_bytes = shader_bytes + MAX_QPATH + 4
        cur_md3surface.shaders[cur_md3surface.numShaders].name = skin.name
        cur_md3surface.shaders[cur_md3surface.numShaders].index = cur_md3surface.numShaders
        cur_md3surface.numShaders = cur_md3surface.numShaders + 1

        # load the triangles info
        cur_md3surface.ofsTriangles = cur_md3surface.ofsShaders + shader_bytes
        # Get the component's frames and mesh triangles.
        frames = comp.dictitems['Frames:fg'].subitems
        cur_md3surface.numFrames = md3.numFrames
        cur_md3surface.numVerts = len(frames[0].vertices)
        tris = comp.triangles
        cur_md3surface.numTriangles = len(tris)
        for vtx in xrange(cur_md3surface.numVerts):
            cur_md3surface.uv.append(md3TexCoord())
        for tri_count in xrange(cur_md3surface.numTriangles):
            tri = md3Triangle()
            cur_md3surface.triangles.append(tri)
            face = tris[tri_count]
            for vtx in xrange(len(face)):
                tri.indexes[vtx] = face[vtx][0]
                vtx_uvs = cur_md3surface.uv[tri.indexes[vtx]]
                vtx_uvs.u = float(face[vtx][1] / TexWidth)
                vtx_uvs.v = float(face[vtx][2] / TexHeight)
        triangle_bytes = cur_md3surface.numTriangles * 12 # Updates for each triangle's 3 integer vtx_index values (4 bytes per int), uvs & verts update the offset_point in their own sections below.

        # uv info loaded above with triangles info, just update the offset_point.
        cur_md3surface.ofsUV = cur_md3surface.ofsTriangles + triangle_bytes
        uv_bytes = cur_md3surface.numVerts * 2 * 4 # vertices per frame * (2f (u & v) * 4 bytes per f)

        # load the verts info.
        cur_md3surface.ofsVerts = cur_md3surface.ofsUV + uv_bytes
        for frame_count in xrange(cur_md3surface.numFrames):
            frame_verts = frames[frame_count].vertices
            for vtx_count in xrange(cur_md3surface.numVerts):
                vert = md3Vert()
                cur_md3surface.verts.append(vert)
                vtx = frame_verts[vtx_count]
                vert.xyz = vtx.tuple
                vtx_normal = vtx.normalized.tuple
                vert.normal = Encode(vtx_normal[0:3])
        vert_bytes = cur_md3surface.numFrames * (cur_md3surface.numVerts * 8)

        # set the end of this surface and update the end of the md3.
        cur_md3surface.ofsEnd = cur_md3surface.ofsVerts + vert_bytes
        offset_point = offset_point + cur_md3surface.ofsEnd
        md3.ofsEnd = offset_point


class md3Object:
    header_size = 0
    #Header Structure
    ident = ""        #item 0    This is used to identify the file.
    version = 0       #item 1    The version number of the file (Must be 15).
    name = ""         #item 2    Full file path & name to save, can not exceed 64 characters & spaces.
    flags = 0         #item 3    Model flag setting, if any.
    numFrames = 0     #item 4    The number of animation frames, if any, including the 'baseframe'.
    numTags = 0       #item 5    The number of tags in this model.
    numSurfaces = 0   #item 6    The number of components, meshes, being exported for this model.
    numSkins = 0      #item 7    The number of skins associated with the model.
    ofsFrames = 0     #item 8    The offset in the file for the starting point for the frames data.
    ofsTags = 0       #item 9    The offset in the file for the starting point for the tags data.
    ofsSurfaces = 0   #item 10   The offset in the file for the starting point for the Surface data.
    ofsEnd = 0        #item 11   The end of the file offset.
    binaryFormat = "<4si%ds9i" % MAX_QPATH  # little-endian (<), 4 char[] string, 1 int, size of string 'name' max 64 char[], integers (9i)
    # md3 data objects
    frames = []
    tags = []
    surfaces = []

    def __init__(self):
        self.header_size = (11 * 4) + MAX_QPATH # length of ident string, 1 byte per character + 10 integer items below, 4 bytes per integer + MAX_QPATH (64).
        self.ident = "IDP3" # ident.
        self.version = 15 # version.
        self.name = ""
        self.flags = 0
        self.numFrames = 0
        self.numTags = 0
        self.numSurfaces = 0
        self.numSkins = 0
        self.ofsFrames = 0
        self.ofsTags = 0
        self.ofsSurfaces = 0
        self.ofsEnd = 0
        self.frames = []
        self.tags = []
        self.surfaces = []

    def save(self, file):
        # Write the header.
        tmpData = [0]*12
        tmpData[0] = self.ident
        tmpData[1] = self.version
        tmpData[2] = self.name
        tmpData[3] = self.flags
        tmpData[4] = self.numFrames
        tmpData[5] = self.numTags
        tmpData[6] = self.numSurfaces
        tmpData[7] = self.numSkins
        tmpData[8] = self.ofsFrames
        tmpData[9] = self.ofsTags
        tmpData[10] = self.ofsSurfaces
        tmpData[11] = self.ofsEnd
        data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1], tmpData[2], tmpData[3], tmpData[4], tmpData[5], tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11])
        file.write(data)

        # Write the frames.
        for frame in self.frames:
            frame.save(file)

        # Write the tags.
        for frame in xrange(self.numFrames):
            for tag in xrange(self.numTags):
                self.tags[(frame * self.numTags) + tag].save(file)

        # Write the surfaces.
        for surface in self.surfaces:
            surface.save(file)


def save_md3(self):
    "Calls functions to write the .md3 model file (also skin and shader files, if called for)."
    global tobj, logging, exportername, textlog, Strings

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, self.filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    # self = all the QuArK objects setup as attributes of the export dialog including
    #        the tags (if any) and components we are exporting from our model editor.
    md3 = md3Object()

    # Fill the needed data for exporting.
    fill_md3(md3, self)

    #actually write it to disk
    md3.save(self.md3file)

    add_to_message = ""
    ie_utils.default_end_logging(self.filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.


######################################################
# CALL TO SAVE .md3 FILE (where it all starts off from)
######################################################
# Saves the model file: root is the actual file,
# filename is the full path and name of the .md3 to create.
# For example:  C:\Quake 3 Arena\baseq3\models\players\sarge\head.md3.
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
        if filename.endswith(".md3"): # Calls to save the .md3 file.
            framesgroup = object.dictitems['Frames:fg']
            frames = framesgroup.subitems
            if not framesgroup or len(frames) < 1:
                quarkx.msgbox("Component " + object.shortname + "\nhas no frames to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            if anim_frames == 0:
                anim_frames = len(frames)
            if len(frames) != anim_frames:
                quarkx.msgbox("Component " + object.shortname + "\nnumber of animation frames\ndoes not equal other components.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            if not frames[len(frames)-1].shortname.endswith("baseframe"):
                quarkx.msgbox("Component " + object.shortname + "\nlast frame is not a '(frame name) baseframe'.\nAll components to be exported\nmust have a baseframe.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            if len(frames[0].dictspec['Vertices']) == 0:
                quarkx.msgbox("Component " + object.shortname + "\nhas no frame vertices to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            if len(frames) == 0:
                quarkx.msgbox("Component " + object.shortname + "\nhas no skin textures to export.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return

    UIExportDialog(root, filename, editor) # Calls the dialog below which calls to save a mesh or animaition file.
    return


### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".md3 Quake 3 Exporter", ".md3 file", "*.md3", savemodel)


######################################################
# DIALOG SECTION (which calls to export an .md3 file)
######################################################
class ExportSettingsDlg(quarkpy.qmacro.dialogbox):
    endcolor = AQUA
    size = (200, 300)
    dfsep = 0.6     # sets 60% for labels and the rest for edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
    dlgdef = """
        {
        Style = "13"
        Caption = "md3 Export Items"
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

        Skins: =
            {
            Txt = "Export Skin Textures:"
            Typ = "X"
            Hint = "Check this box to export the component's skins files."$0D
                   "These files may need to be moved to other folders."
            }

        Shaders: =
            {
            Txt = "Export Shaders Files:"
            Typ = "X"
            Hint = "Check this box to export the component's"$0D
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
                   "that you chose for the .md3 model file to be placed."
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
        self.tags = []
        self.comp_list = self.editor.layout.explorer.sellist
        self.newfiles_folder = newfiles_folder
        self.md3file = None
        self.exportpath = filename.replace('\\', '/')
        self.exportpath = self.exportpath.rsplit('/', 1)[0]
        src = quarkx.newobj(":")
        src['Tags'] = "1"
        src['Skins'] = None
        src['Shaders'] = None
        src['makefolder'] = None
        self.src = src

        # Create the dialog form and the buttons.
        quarkpy.qmacro.dialogbox.__init__(self, form1, src,
            MakeFiles = quarkpy.qtoolbar.button(self.MakeFiles,"DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.",ico_editor, 3, "Export Model"),
            close = quarkpy.qtoolbar.button(self.close, "DO NOT close this dialog\n ( to retain your settings )\nuntil you check your new files.", ico_editor, 0, "Cancel Export")
            )

    def MakeFiles(self, btn):
        # Accepts all entries then starts making the processing function calls.
        quarkx.globalaccept()
        root = self.root

        if self.src["makefolder"] is not None:
            if not os.path.exists(self.newfiles_folder):
                os.mkdir(self.newfiles_folder)
            else:
                if len(self.filename) > MAX_QPATH:
                    quarkx.msgbox("EXPORT CANCELED:\n\nFull path and file name exceeded\nMD3 file limit of 64 characters & spaces.\n\nNothing was written to the\n    " + self.filename + "\nfile and it remains unchanged.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
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
            miscgroup = self.editor.Root.dictitems['Misc:mg']  # get the Misc group
            tags = miscgroup.findallsubitems("", ':tag')    # get all tags
            for comp in self.comp_list:
                comp_group = comp.name.split("_", 1)[0] + "_"
                for tag in tags:
                    if not tag in self.tags and tag.name.startswith(comp_group):
                        self.tags = self.tags + [tag]
        if self.src['Skins'] is not None:
            for comp in self.comp_list:
                for skin in comp.dictitems['Skins:sg'].subitems:
                    tempfilename = self.filename.replace("\\", "/")
                    tempfilename = tempfilename.rsplit("/", 1)[0]
                    tempskinname = skin.name.replace("\\", "/")
                    tempskinname = tempskinname.rsplit("/", 1)[1]
                    skin.filename = tempfilename + '/' + tempskinname
                    quarkx.savefileobj(skin, FM_Save, 0)
        if self.src['Shaders'] is not None:
            write_shaders(self.filename, self.comp_list)

        # Opens the output file for writing the .md3 file to disk.
        self.md3file = open(self.filename,"wb")
        save_md3(self) # This is the funciton above called to start exporting the mesh or animation file.
        self.md3file.close()


def UIExportDialog(root, filename, editor):
    # Sets up the new window form for the exporters dialog for user selection settings and calls its class.
    form1 = quarkx.newform("masterform")
    if filename.endswith(".md3"):
        newfiles_folder = filename.replace(".md3", "")
    ExportSettingsDlg(form1, root, filename, editor, newfiles_folder)


# ----------- REVISION HISTORY ------------
#
# $Log: ie_md3_export.py,v $
# Revision 1.3  2011/03/31 16:13:17  cdunde
# Small comments corrections.
#
# Revision 1.2  2010/03/16 19:25:37  cdunde
# Update to activate the rest of the export dialog items.
#
# Revision 1.1  2010/03/16 07:17:13  cdunde
# Added support for .md3 model format exporting with tags, textures and shader files.
#
#