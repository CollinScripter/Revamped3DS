# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Heretic II .fm model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_fm_import.py,v 1.8 2011/10/14 05:28:16 cdunde Exp $


Info = {
   "plug-in":       "ie_fm_importer",
   "desc":          "This script imports a Heretic II file (FM), .m8 textures, and animations into QuArK for editing. Original code from QuArK, ie_md2_import.py file.",
   "date":          "Feb. 6 2011",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 4" }

import struct, sys, os, time, operator
import quarkx
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
logging = 0
importername = "ie_fm_import.py"
textlog = "fm_ie_log.txt"
progressbar = None
g_scale = 1.0

######################################################
# FM Model Constants
######################################################
MAX_FM_TRIANGLES=2048
MAX_FM_VERTS=2048
MAX_FM_FRAMES=2048
MAX_FM_SKINS=64
MAX_FM_SKINNAME=64
MAX_FM_MESH_NODES=16
SCALE_ADJUST_FACTOR=0.95 # Used only on U texture value, some look better, some don't. Game code sets to 0.96.
MAX_MODELJOINTS=256
MAX_MODELJOINTNODES=255

######################################################
# FM data structures
######################################################
class fm_alias_triangle:
    vertices=[]
    lightnormalindex=0

    binary_format="<3BB" #little-endian (<), 3 Unsigned char
    
    def __init__(self):
        self.vertices=[0]*3
        self.lightnormalindex=0

    def load(self, file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # data[0] through data[3] ex: (178, 143, 180, 63), 3 texture coords and normal (normal not needed).
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.vertices[0]=data[0]
        self.vertices[1]=data[1]
        self.vertices[2]=data[2]
        self.lightnormalindex=data[3]
        return self

    def dump(self):
        global tobj, logging
        tobj.logcon ("vertex 0,1,2, lightnormalindex: " + str(self.vertices[0]) + ", " + str(self.vertices[1]) + ", " + str(self.vertices[2]) + ", " + str(self.lightnormalindex))
        tobj.logcon ("----------------------------------------")

class fm_face:
    vertex_index=[]
    texture_index=[]

    binary_format="<3h3h" #little-endian (<), 3 short, 3 short
    
    def __init__(self):
        self.vertex_index = [ 0, 0, 0 ]
        self.texture_index = [ 0, 0, 0]

    def load (self, file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # data[0] through data[5] ex: (62, 38, 71, 49, 69, 77), are 3 vertex and 3 texture indexes as integers.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.vertex_index[0]=data[0]
        self.vertex_index[1]=data[1]
        self.vertex_index[2]=data[2]
        self.texture_index[0]=data[3]
        self.texture_index[1]=data[4]
        self.texture_index[2]=data[5]
        return self

    def dump (self):
        global tobj, logging
        tobj.logcon ("vertex indexes: " + str(self.vertex_index[0]) + ", " + str(self.vertex_index[1]) + ", " + str(self.vertex_index[2]))
        tobj.logcon ("texture indexes: " + str(self.texture_index[0]) + ", " + str(self.texture_index[1]) + ", " + str(self.texture_index[2]))
        tobj.logcon ("----------------------------------------")

class glGLCommands_t:
    TrisTypeNum=None

    binary_format="<i" #little-endian (<), 1 int

    def __init__(self):
        self.TrisTypeNum=None

    def load (self, file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # data[0] ex: (4) or (-7), positive int = a triangle strip, negative int = a triangle fan, 0 = end of valid GL_commands data.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.TrisTypeNum=data[0]
        return self

    def dump (self):
        global tobj, logging
        tobj.logcon ("-------------------")
        tobj.logcon ("FM OpenGL Command Structure")
        tobj.logcon ("TrisTypeNum: " + str(self.TrisTypeNum))
        tobj.logcon ("-------------------")

class glCommandVertex_t:
    u=0.0
    v=0.0
    vertexIndex=0

    binary_format="<2fi" #little-endian (<), 2 floats + 1 int

    def __init__(self):
        self.u=0.0
        self.v=0.0
        self.vertexIndex=0

    def load (self, file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # data[0] and data[1] ex: (0.1397, 0.6093), are 2D skin texture coords as floats, percentage of skin size.
        # data[2] the face vertex index the u,v belong to.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.u=data[0]
        self.v=data[1]
        self.vertexIndex=data[2]
        return self

    def dump (self):
        global tobj, logging
        tobj.logcon ("FM OpenGL Command Vertex")
        tobj.logcon ("u: " + str(self.u))
        tobj.logcon ("v: " + str(self.v))
        tobj.logcon ("vertexIndex: " + str(self.vertexIndex))
        tobj.logcon ("")

class fm_tex_coord:
    u=0
    v=0

    binary_format="<2h" #little-endian (<), 2 unsigned short

    def __init__(self):
        self.u=0
        self.v=0

    def load (self, file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # data[0] and data[1] ex: (169, 213), are 2D skin texture coords as integers.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
      #  self.u=int(data[0]*SCALE_ADJUST_FACTOR) # See notation for this at top of this file.
        self.u=data[0]
        self.v=data[1]
        return self

    def dump (self):
        global tobj, logging
        tobj.logcon ("texture coordinate u, v: " + str(self.u) + ", " + str(self.v))
        tobj.logcon ("----------------------------------------")


class fm_skin:
    name=""

    binary_format="<64c" #little-endian (<), char[64]

    def __init__(self):
        self.name=""

    def load (self, file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # self.name is just the skin texture path and name, ex: C:\Heretic II\base\models\monsters\chicken2/!skin.m8
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        for i in xrange(64):
            if not str(data[i]).isalnum() and str(data[i]) != "\\" and str(data[i]) != "/" and str(data[i]) != "!" and str(data[i]) != "." and str(data[i]) != "_" and str(data[i]) != "-":
                continue
            self.name = self.name + str(data[i])
        return self

    def dump (self):
        print "================="
        print "FM Skin"
        print "-----------------"
        print "skin name: ",self.name
        print "-----------------"
        print ""

class fm_alias_frame:
    scale=[]
    translate=[]
    name=[]
    vertices=[]

    binary_format="<3f3f" #little-endian (<), 3 float, 3 float char[16]
    #did not add the "3bb" to the end of the binary format
    #because the alias_vertices will be read in through
    #thier own loader

    def __init__(self):
        self.scale=[0.0]*3
        self.translate=[0.0]*3
        self.name=""
        self.vertices=[]


    def load (self, file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # self.scale[0] through self.scale[2] ex: 0.12633632123470306, 0.077566042542457581, 0.21140974760055542,
        # self.translate[0] through self.translate[2] ex: -16.496400833129883, -9.5092992782592773, -24.108100891113281,
        # self.name is the frame name ex: attack1
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.scale[0]=data[0]
        self.scale[1]=data[1]
        self.scale[2]=data[2]
        self.translate[0]=data[3]
        self.translate[1]=data[4]
        self.translate[2]=data[5]

        binary_format="<16c"
        temp_data=file.read(struct.calcsize(binary_format))
        data=struct.unpack(binary_format, temp_data)
        for i in xrange(16):
            if str(data[i]) == "\x00":
                break
            self.name = self.name + str(data[i])
        return self

    def dump (self):
        global tobj, logging
        tobj.logcon ("scale x,y,z: " + str(self.scale[0]) + ", " + str(self.scale[1]) + ", " + str(self.scale[2]))
        tobj.logcon ("translate x,y,z: " + str(self.translate[0]) + ", " + str(self.translate[1]) + ", " + str(self.translate[2]))
        tobj.logcon ("name: " + self.name)
        tobj.logcon ("----------------------------------------")

class fm_obj:
    #Header Structure
    SectionName=""       #char 0-31 This is used to identify each file Section, (offsets are not given).
                         # (in this order) SectionName = 'header', 'skin', 'st coord', 'tris', 'frames'.
                         # (may also have) SectionName = 'short frames', 'normals', 'comp data', 'glcmds', 'mesh nodes', 'skeleton' and\or 'references'.
    section_version=0    #int  32   The version number of each section.
    section_byte_size=0  #int  33   The size in bytes of each section.
    skin_width=0         #int  34   The skin width in pixels
    skin_height=0        #int  35   The skin height in pixels
    frame_size=0         #int  36   The size in bytes the frames are
    num_skins=0          #int  37   The number of skins associated with the model
    num_vertices=0       #int  38   The number of vertices (constant for each frame)
    num_tex_coords=0     #int  39   The number of texture coordinates
    num_faces=0          #int  40   The number of faces (polygons)
    num_GL_commands=0    #int  41   The number of gl commands
    num_frames=0         #int  42   The number of animation frames
    num_mesh_nodes=0     #int  43   The number of nodes, believe these are bones.

    binary_format="<32c12i"  #little-endian (<), see above.

    #fm data objects
    tex_coords=[]
    faces=[]
    frames=[]
    skins=[]

    def __init__ (self):
        self.tex_coords=[]
        self.faces=[]
        self.frames=[]
        self.skins=[]


    def load (self, file):
        global tobj, logging
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # data is all of the header data amounts.
        filesize = os.path.getsize(file.name) # The full size in Bytes of this file for checking later on.
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.SectionName=""
        for i in xrange(32):
            if str(data[i]) == "\x00":
                continue
            self.SectionName = self.SectionName + str(data[i])
        self.section_version=data[32]
        self.section_byte_size=data[33]
        if (self.SectionName!="header"): # Not a valid .fm file.
            return None

        self.skin_width=data[34]
        self.skin_height=data[35]
        self.frame_size=data[36]

        #make the # of skin objects for model
        self.num_skins=data[37]
        for i in xrange(0,self.num_skins):
            self.skins.append(fm_skin())

        self.num_vertices=data[38]

        #make the # of texture coordinates for model
        self.num_tex_coords=data[39]
        for i in xrange(0,self.num_tex_coords):
            self.tex_coords.append(fm_tex_coord())

        #make the # of triangle faces for model
        self.num_faces=data[40]
        for i in xrange(0,self.num_faces):
            self.faces.append(fm_face())

        self.num_GL_commands=data[41]

        #make the # of frames for the model
        self.num_frames=data[42]
        for i in xrange(0,self.num_frames):
            self.frames.append(fm_alias_frame())
            #make the # of vertices for each frame
            for j in xrange(0,self.num_vertices):
                self.frames[i].vertices.append(fm_alias_triangle())

        #make the # of nodes for the model, each is a section of the mesh.
        self.num_mesh_nodes=data[43]

        ### Start reading and loading all the file data.

        #load the "skin" section.
        binary_format="<32c2i"
        temp_data=file.read(struct.calcsize(binary_format))
        data=struct.unpack(binary_format, temp_data)
        SectionName=""
        for i in xrange(32):
            if str(data[i]) == "\x00":
                continue
            SectionName = SectionName + str(data[i])
        section_version=data[32]
        section_byte_size=data[33]
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: " + SectionName)
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        for i in xrange(0, self.num_skins):
            self.skins[i].load(file)
            #self.skins[i].dump()

        #load the "st coord" (texture coordinates) section.
        binary_format="<32c2i"
        temp_data=file.read(struct.calcsize(binary_format))
        data=struct.unpack(binary_format, temp_data)
        SectionName=""
        for i in xrange(32):
            if str(data[i]) == "\x00":
                continue
            SectionName = SectionName + str(data[i])
        section_version=data[32]
        section_byte_size=data[33]
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: " + SectionName)
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        for i in xrange(0, self.num_tex_coords):
            self.tex_coords[i].load(file)
            if logging == 1:
                tobj.logcon ("fm_tex_coord " + str(i))
                self.tex_coords[i].dump()

        #load the "tris" section.
        binary_format="<32c2i"
        temp_data=file.read(struct.calcsize(binary_format))
        data=struct.unpack(binary_format, temp_data)
        SectionName=""
        for i in xrange(32):
            if str(data[i]) == "\x00":
                continue
            SectionName = SectionName + str(data[i])
        section_version=data[32]
        section_byte_size=data[33]
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: " + SectionName)
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        for i in xrange(0, self.num_faces):
            self.faces[i].load(file)
            if logging == 1:
                tobj.logcon ("fm_face " + str(i))
                self.faces[i].dump()

        #load the "frames" section.
        binary_format="<32c2i"
        temp_data=file.read(struct.calcsize(binary_format))
        data=struct.unpack(binary_format, temp_data)
        SectionName=""
        for i in xrange(32):
            if str(data[i]) == "\x00":
                continue
            SectionName = SectionName + str(data[i])
        section_version=data[32]
        section_byte_size=data[33]
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: " + SectionName)
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        for i in xrange(0, self.num_frames):
            self.frames[i].load(file)
            if logging == 1:
                tobj.logcon ("fm_alias_frame " + str(i))
                self.frames[i].dump()
            for j in xrange(0,self.num_vertices):
                self.frames[i].vertices[j].load(file)
                if logging == 1:
                    tobj.logcon ("fm_alias_triangle " + str(j))
                    self.frames[i].vertices[j].dump()

        if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
            return self

        #read the next section header data.
        binary_format="<32c2i"
        temp_data=file.read(struct.calcsize(binary_format))
        data=struct.unpack(binary_format, temp_data)
        SectionName=""
        for i in xrange(32):
            if str(data[i]) == "\x00":
                continue
            SectionName = SectionName + str(data[i])
        section_version=data[32]
        section_byte_size=data[33]
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: " + SectionName)
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")

        #load the "short frames" section if any.
        if SectionName == "short frames":
            file.seek(file.tell()+section_byte_size,0) # To skip over reading in "short frames" section data, don't know how.
            if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
                return self
            #read the next section header data.
            binary_format="<32c2i"
            temp_data=file.read(struct.calcsize(binary_format))
            data=struct.unpack(binary_format, temp_data)
            SectionName=""
            for i in xrange(32):
                if str(data[i]) == "\x00":
                    continue
                SectionName = SectionName + str(data[i])
            section_version=data[32]
            section_byte_size=data[33]
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("#####################################################################")
                tobj.logcon ("SectionName: " + SectionName)
                tobj.logcon ("section_version: " + str(section_version))
                tobj.logcon ("section_byte_size: " + str(section_byte_size))
                tobj.logcon ("#####################################################################")

        #load the "normals" section if any.
        if SectionName == "normals":
            file.seek(file.tell()+section_byte_size,0) # To skip over reading in "normals" section data, don't know how.
            if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
                return self
            #read the next section header data.
            binary_format="<32c2i"
            temp_data=file.read(struct.calcsize(binary_format))
            data=struct.unpack(binary_format, temp_data)
            SectionName=""
            for i in xrange(32):
                if str(data[i]) == "\x00":
                    continue
                SectionName = SectionName + str(data[i])
            section_version=data[32]
            section_byte_size=data[33]
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("#####################################################################")
                tobj.logcon ("SectionName: " + SectionName)
                tobj.logcon ("section_version: " + str(section_version))
                tobj.logcon ("section_byte_size: " + str(section_byte_size))
                tobj.logcon ("#####################################################################")

        #load the "comp data" section if any.
        if SectionName == "comp data":
            file.seek(file.tell()+section_byte_size,0) # To skip over reading in "comp data" section data, don't know how.
            if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
                return self
            #read the next section header data.
            binary_format="<32c2i"
            temp_data=file.read(struct.calcsize(binary_format))
            data=struct.unpack(binary_format, temp_data)
            SectionName=""
            for i in xrange(32):
                if str(data[i]) == "\x00":
                    continue
                SectionName = SectionName + str(data[i])
            section_version=data[32]
            section_byte_size=data[33]
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("#####################################################################")
                tobj.logcon ("SectionName: " + SectionName)
                tobj.logcon ("section_version: " + str(section_version))
                tobj.logcon ("section_byte_size: " + str(section_byte_size))
                tobj.logcon ("#####################################################################")

        #load the "glcmds" section if any (ex: num_GL_commands-> 1135 ints * 4bytes = 4540).
        if SectionName == "glcmds" and self.num_GL_commands > 0:
            if logging == 1:
                tobj.logcon ("START OF GLCMDS at, num_GL_commands: " + str(file.tell()) + ", " + str(self.num_GL_commands))
            for i in xrange(0, self.num_GL_commands):
                gl_command = glGLCommands_t()
                gl_command.load(file)
                if logging == 1:
                    gl_command.dump()
                if gl_command.TrisTypeNum is not None:
                    if gl_command.TrisTypeNum == 0: # end of valid GL_commands data section
                        break
                    if gl_command.TrisTypeNum > -1: # a triangle strip
                        for j in xrange(0, gl_command.TrisTypeNum):
                            gl_vertex = glCommandVertex_t()
                            gl_vertex.load(file)
                            if logging == 1:
                                gl_vertex.dump()

                            if j == 0:
                                vertex_info0 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                            elif j == 1:
                                vertex_info1 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                            else:
                                vertex_info2 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                              #  faces[gl_command.SubObjectID] += [(vertex_info0, vertex_info1, vertex_info2)]
                                if not j&1: # This test if a number is even.
                                    vertex_info0 = vertex_info2
                                else: # else it is odd.
                                    vertex_info1 = vertex_info2
                    else: # a triangle fan
                        for j in xrange(0, gl_command.TrisTypeNum * -1):
                            gl_vertex = glCommandVertex_t()
                            gl_vertex.load(file)
                            if logging == 1:
                                gl_vertex.dump()

                            if j == 0:
                                vertex_info0 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                            elif j == 1:
                                vertex_info1 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                            else:
                                vertex_info2 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                              #  faces[gl_command.SubObjectID] += [(vertex_info0, vertex_info1, vertex_info2)]
                                vertex_info1 = vertex_info2

            if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
                return self
            #read the next section header data.
            binary_format="<32c2i"
            temp_data=file.read(struct.calcsize(binary_format))
            data=struct.unpack(binary_format, temp_data)
            SectionName=""
            for i in xrange(32):
                if str(data[i]) == "\x00":
                    continue
                SectionName = SectionName + str(data[i])
            section_version=data[32]
            section_byte_size=data[33]
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("#####################################################################")
                tobj.logcon ("SectionName: " + SectionName)
                tobj.logcon ("section_version: " + str(section_version))
                tobj.logcon ("section_byte_size: " + str(section_byte_size))
                tobj.logcon ("#####################################################################")

        #load the "mesh nodes" (nodes = bone joints)
        if SectionName == "mesh nodes" and self.num_mesh_nodes > 0:
            holdpointer = file.tell()

            if logging == 1:
                tobj.logcon ("num_mesh_nodes: " + str(self.num_mesh_nodes))
                tobj.logcon ("============================")
                tobj.logcon ("pointer location at start: " + str(holdpointer))
                binary_format="<b"
                count=256
                while count > 0:
                    temp_data=file.read(struct.calcsize(binary_format))
                    data=struct.unpack(binary_format, temp_data)
                    count-=1
                    if data[0] == 0:
                        continue
                    tobj.logcon ("tri data: " + str(data))
                tobj.logcon ("pointer at end of tri data: " + str(file.tell()))
                count=256
                while count > 0:
                    temp_data=file.read(struct.calcsize(binary_format))
                    data=struct.unpack(binary_format, temp_data)
                    count-=1
                    if data[0] == 0:
                        continue
                    tobj.logcon ("vert data: " + str(data))
                tobj.logcon ("pointer at end of vert data: " + str(file.tell()))
                file.seek(filesize-4,0)
                tobj.logcon ("pointer 2h data: " + str(file.tell()))
                binary_format="<2h"
                temp_data=file.read(struct.calcsize(binary_format))
                data=struct.unpack(binary_format, temp_data)
                tobj.logcon ("pointer after, glstart, nbrglcmds: " + str(file.tell()) + ", " + str(data[0]) + ", " + str(data[1]))

            file.seek(holdpointer,0)
            file.seek(file.tell()+section_byte_size,0) # To skip over reading in "mesh nodes" section data, don't know how.
            if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
                return self
            #read the next section header data.
            binary_format="<32c2i"
            temp_data=file.read(struct.calcsize(binary_format))
            data=struct.unpack(binary_format, temp_data)
            SectionName=""
            for i in xrange(32):
                if str(data[i]) == "\x00":
                    continue
                SectionName = SectionName + str(data[i])
            section_version=data[32]
            section_byte_size=data[33]
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("#####################################################################")
                tobj.logcon ("SectionName: " + SectionName)
                tobj.logcon ("section_version: " + str(section_version))
                tobj.logcon ("section_byte_size: " + str(section_byte_size))
                tobj.logcon ("#####################################################################")

        #load the "skeleton" (nodes = bone joints).
        if SectionName == "skeleton":
            file.seek(file.tell()+section_byte_size,0) # To skip over reading in "skeleton" section data, don't know how.
            if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
                return self
            #read the next section header data.
            binary_format="<32c2i"
            temp_data=file.read(struct.calcsize(binary_format))
            data=struct.unpack(binary_format, temp_data)
            SectionName=""
            for i in xrange(32):
                if str(data[i]) == "\x00":
                    continue
                SectionName = SectionName + str(data[i])
            section_version=data[32]
            section_byte_size=data[33]
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("#####################################################################")
                tobj.logcon ("SectionName: " + SectionName)
                tobj.logcon ("section_version: " + str(section_version))
                tobj.logcon ("section_byte_size: " + str(section_byte_size))
                tobj.logcon ("#####################################################################")

        #load the "references".
        if SectionName == "references":
            file.seek(file.tell()+section_byte_size,0) # To skip over reading in "references" section data, don't know how.
            if file.tell() >= filesize: # Check if end of file. If so, stop here and return.
                return self
            #read the next section header data.
            binary_format="<32c2i"
            temp_data=file.read(struct.calcsize(binary_format))
            data=struct.unpack(binary_format, temp_data)
            SectionName=""
            for i in xrange(32):
                if str(data[i]) == "\x00":
                    continue
                SectionName = SectionName + str(data[i])
            section_version=data[32]
            section_byte_size=data[33]
            if logging == 1:
                tobj.logcon ("")
                tobj.logcon ("#####################################################################")
                tobj.logcon ("SectionName: " + SectionName)
                tobj.logcon ("section_version: " + str(section_version))
                tobj.logcon ("section_byte_size: " + str(section_byte_size))
                tobj.logcon ("#####################################################################")

        return self

    def dump (self):
        global tobj, logging
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Section Name: " + str(self.SectionName))
            tobj.logcon ("section version: " + str(self.section_version))
            tobj.logcon ("section byte size: " + str(self.section_byte_size))
            tobj.logcon ("skin width: " + str(self.skin_width))
            tobj.logcon ("skin height: " + str(self.skin_height))
            tobj.logcon ("frames byte size: " + str(self.frame_size))
            tobj.logcon ("number of skins: " + str(self.num_skins))
            tobj.logcon ("number of vertices per frame: " + str(self.num_vertices))
            tobj.logcon ("number of texture coordinates: " + str(self.num_tex_coords))
            tobj.logcon ("number of faces: " + str(self.num_faces))
            tobj.logcon ("number of GL commands: " + str(self.num_GL_commands))
            tobj.logcon ("number of frames: " + str(self.num_frames))
            tobj.logcon ("number of mesh nodes: " + str(self.num_mesh_nodes))
            tobj.logcon ("")

######################################################
# Import functions
######################################################
def load_textures(fm, message):
    global tobj, logging
    # Checks if the model has textures specified with it,
    # if not trys to load some from the model's folder.
    skinsize = (256, 256)
    skingroup = quarkx.newobj('Skins:sg')
    skingroup['type'] = chr(2)
    cur_dir = os.getcwd()
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Skins group data: " + str(fm.num_skins) + " skins")
        tobj.logcon ("#####################################################################")
    if int(fm.num_skins) > 0:
        for i in xrange(0,fm.num_skins):
            if logging == 1:
                tobj.logcon (fm.skins[i].name)
            skinname = fm.skins[i].name.split('/')
            try:
                image = quarkx.openfileobj(cur_dir + "\\" + skinname[len(skinname)-1])
            except:
                message = message + fm.skins[i].name + "\r\n"
                continue
            skin = quarkx.newobj(fm.skins[i].name)
            skin['Image1'] = image.dictspec['Image1']
            try:
                skin['Pal'] = image.dictspec['Pal']
            except:
                pass
            skin['Size'] = image.dictspec['Size']
            skingroup.appenditem(skin)
            skinsize = (fm.skin_width, fm.skin_height) # Used for QuArK.
            # Only writes to the console here.
          #  fm.skins[i].dump() # Comment out later, just prints to the console what the skin(s) are.

        if len(skingroup.subitems) == 0:
            files = os.listdir(cur_dir)
            folder = cur_dir.replace("\\", "/")
            folder = folder.rsplit("/", 1)[1]
            for name in files:
                if name.endswith(".m8") and not name.endswith("_i.m8"):
                    image = quarkx.openfileobj(cur_dir + "\\" + name)
                    skin = quarkx.newobj(folder + "/" + name)
                    skin['Image1'] = image.dictspec['Image1']
                    try:
                        skin['Pal'] = image.dictspec['Pal']
                    except:
                        pass
                    skin['Size'] = image.dictspec['Size']
                    skingroup.appenditem(skin)
                    if len(skingroup.subitems) == 1:
                        skinsize = (fm.skin_width, fm.skin_height) # Used for QuArK.

        return skinsize, skingroup, message # Used for QuArK.
    else:
        message = message + "No skins were specified with the model.\r\nAttempting to import skin(s) from work folder.\r\n"
        files = os.listdir(cur_dir)
        folder = cur_dir.replace("\\", "/")
        folder = folder.rsplit("/", 1)[1]
        for name in files:
            if name.endswith(".m8") and not name.endswith("_i.m8"):
                image = quarkx.openfileobj(cur_dir + "\\" + name)
                skin = quarkx.newobj(folder + "/" + name)
                skin['Image1'] = image.dictspec['Image1']
                try:
                    skin['Pal'] = image.dictspec['Pal']
                except:
                    pass
                skin['Size'] = image.dictspec['Size']
                skingroup.appenditem(skin)
                if len(skingroup.subitems) == 1:
                    skinsize = (fm.skin_width, fm.skin_height) # Used for QuArK.

        return skinsize, skingroup, message # Used for QuArK.
	

def animate_fm(fm): # The Frames Group is made here & returned to be added to the Component.
    global progressbar, tobj, logging
	######### Animate the verts through the QuArK Frames lists.
    framesgroup = quarkx.newobj('Frames:fg')

    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Frame group data: " + str(fm.num_frames) + " frames")
        tobj.logcon ("frame: frame name")
        tobj.logcon ("#####################################################################")

    for i in xrange(0, fm.num_frames):
        ### fm.frames[i].name is the frame name, ex: attack1
        if logging == 1:
            tobj.logcon (str(i) + ": " + fm.frames[i].name)

        frame = quarkx.newobj(fm.frames[i].name + ':mf')
        mesh = ()
        #update the vertices
    #    print "======================="
    #    print "line 616 frame", i, frame.name
    #    print "line 617 scale", fm.frames[i].scale
    #    print "line 618 g_scale", g_scale
    #    print "line 619 translate", fm.frames[i].translate
        for j in xrange(0,fm.num_vertices):
    #        print "-----------------------"
    #        print "line 622 vertices", fm.frames[i].vertices[j].vertices
            x=(fm.frames[i].scale[0]*fm.frames[i].vertices[j].vertices[0]+fm.frames[i].translate[0])*g_scale
            y=(fm.frames[i].scale[1]*fm.frames[i].vertices[j].vertices[1]+fm.frames[i].translate[1])*g_scale
            z=(fm.frames[i].scale[2]*fm.frames[i].vertices[j].vertices[2]+fm.frames[i].translate[2])*g_scale
    #        print "line 626 x,y,z", x,y,z

            #put the vertex in the right spot
            mesh = mesh + (x,)
            mesh = mesh + (y,)
            mesh = mesh + (z,)

        frame['Vertices'] = mesh
        framesgroup.appenditem(frame)
        progressbar.progress()
    return framesgroup


def load_fm(fm_filename, name):
    global progressbar, tobj, logging, Strings
    message = ""
    #read the file in
    file=open(fm_filename,"rb")
    fm=fm_obj()
    MODEL = fm.load(file)

    file.close()
    if MODEL is None:
        return None, None, None, None

    Strings[2454] = name + "\n" + Strings[2454]
    progressbar = quarkx.progressbar(2454, fm.num_faces + (fm.num_frames * 2))
    skinsize, skingroup, message = load_textures(fm, message) # Calls here to make the Skins Group.

    ######### Make the faces for QuArK, the 'component.triangles', which is also the 'Tris'.
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Face group data: " + str(fm.num_faces) + " faces")
        tobj.logcon ("face: (vert_index, U, V)")
        tobj.logcon ("#####################################################################")

    Tris = ''
    for i in xrange(0, fm.num_faces):
        if logging == 1:
            facelist = []
            facelist = facelist + [(fm.faces[i].vertex_index[0], fm.tex_coords[fm.faces[i].texture_index[0]].u, fm.tex_coords[fm.faces[i].texture_index[0]].v)]
            facelist = facelist + [(fm.faces[i].vertex_index[1], fm.tex_coords[fm.faces[i].texture_index[1]].u, fm.tex_coords[fm.faces[i].texture_index[1]].v)]
            facelist = facelist + [(fm.faces[i].vertex_index[2], fm.tex_coords[fm.faces[i].texture_index[2]].u, fm.tex_coords[fm.faces[i].texture_index[2]].v)]
            tobj.logcon (str(i) + ": " + str(facelist))
        Tris = Tris + struct.pack("Hhh", fm.faces[i].vertex_index[0], fm.tex_coords[fm.faces[i].texture_index[0]].u, fm.tex_coords[fm.faces[i].texture_index[0]].v)
        Tris = Tris + struct.pack("Hhh", fm.faces[i].vertex_index[1], fm.tex_coords[fm.faces[i].texture_index[1]].u, fm.tex_coords[fm.faces[i].texture_index[1]].v)
        Tris = Tris + struct.pack("Hhh", fm.faces[i].vertex_index[2], fm.tex_coords[fm.faces[i].texture_index[2]].u, fm.tex_coords[fm.faces[i].texture_index[2]].v)
        progressbar.progress()

    framesgroup = animate_fm(fm) # Calls here to make the Frames Group.

    if logging == 1:
        fm.dump() # Writes the file Header last to the log for comparison reasons.

    return Tris, skinsize, skingroup, framesgroup, message


########################
# To run this file
########################

def import_fm_model(editor, fm_filename):


    # Now we start creating our Import Component.
    # But first we check for any other "Import Component"s,
    # if so we name this one 1 more then the largest number.
    name = "None"
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
            name = "Import Component " + str(nbr)
    if name != "None":
        pass
    else:
        name = "Import Component 1"

    Tris, skinsize, skingroup, framesgroup, message = load_fm(fm_filename, name) # Loads the model.
    if Tris is None:
        message = ""
        return None, None, message

    # Now we can name our component that will be imported.
    Component = quarkx.newobj(name + ':mc')
    # Set it up in the ModelComponentList.
    editor.ModelComponentList[Component.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
    Component['skinsize'] = skinsize
    Component['Tris'] = Tris
    Component['show'] = chr(1)
    sdogroup = quarkx.newobj('SDO:sdo')
    Component.appenditem(sdogroup)
    Component.appenditem(skingroup)
    Component.appenditem(framesgroup)

    return Component, message


def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename and gamename is the full path to"
    "and name of the .fm file selected."
    "For example:  C:\Heretic II\base\models\monsters\chicken2\tris.fm"

    global progressbar, tobj, logging, importername, textlog, Strings
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

    logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

    ### Lines below here loads the model into the opened editor's current model.
    Component, message = import_fm_model(editor, filename)

    if Component is None:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        quarkx.msgbox("Invalid .fm model.\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        progressbar.close()
        return

    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        fmfileobj = quarkx.newfileobj("New model.md2")
        fmfileobj['FileName'] = 'New model.qkl'
        editor.Root.appenditem(Component)
        fmfileobj['Root'] = editor.Root.name
        fmfileobj.appenditem(editor.Root)
        fmfileobj.openinnewwindow()
    else: # Imports a model properly from within the editor.
        undo = quarkx.action()
        undo.put(editor.Root, Component)
        editor.Root.currentcomponent = Component
        compframes = editor.Root.currentcomponent.findallsubitems("", ':mf') # get all frames
        for compframe in compframes:
            compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.
            progressbar.progress()

        progressbar.close()
        Strings[2454] = Strings[2454].replace(Component.shortname + "\n", "")
        ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.

        # This needs to be done for each component or bones will not work if used in the editor.
        quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
        editor.ok(undo, Component.shortname + " created")

        comp = editor.Root.currentcomponent
        skins = comp.findallsubitems("", ':sg')      # Gets the skin group.
        if len(skins[0].subitems) != 0:
            comp.currentskin = skins[0].subitems[0]      # To try and set to the correct skin.
            quarkpy.mdlutils.Update_Skin_View(editor, 2) # Sends the Skin-view for updating and center the texture in the view.
        else:
            comp.currentskin = None

        if message != "":
            message = message + "================================\r\n\r\n"
            message = message + "The model you just imported calls for a specific texture(s) and location.\r\n"
            message = message + "You need to find and supply the proper texture(s) and folder(s) above\r\n"
            message = message + "which may not be the current directory and folder you are importing from.\r\n"
            message = message + "If you wish to add this texture you must do so through the Texture Browser.\r\n\r\n"
            message = message + "To do so extract the folder(s) and file(s) to your working directory.\r\n"
            message = message + "Click on 'Toolboxes' > 'Texture Browser...'\r\n"
            message = message + "From its menu click on 'Edit' > 'Import files' > 'Import (copy) files...'\r\n"
            message = message + "Once it is imported double click on it to add it to the Skins group of your current component.\r\n"
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
import ie_fm_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".fm HereticII Importer", ".fm file", "*.fm", loadmodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_fm_import.py,v $
# Revision 1.8  2011/10/14 05:28:16  cdunde
# Final, reading in the GLcommands properly.
#
# Revision 1.7  2011/10/13 19:35:29  cdunde
# Update for logging to match exporter logging.
#
# Revision 1.6  2011/10/06 08:59:52  cdunde
# Logging correction to stop header data from being over written.
#
# Revision 1.5  2011/09/28 06:56:54  cdunde
# Texture naming update.
#
# Revision 1.4  2011/04/05 20:51:42  cdunde
# Comment update.
#
# Revision 1.3  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.2  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.1  2011/02/11 19:52:56  cdunde
# Added import support for Heretic II and .m8 as supported texture file type.
#
#
