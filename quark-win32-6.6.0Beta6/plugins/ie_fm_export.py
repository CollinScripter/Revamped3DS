# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for Heretic II .fm model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_fm_export.py,v 1.8 2013/02/20 05:19:41 cdunde Exp $


Info = {
   "plug-in":       "ie_fm_exporter",
   "desc":          "Export a single selected component to a Heretic II file (FM).",
   "date":          "September 24 2011",
   "author":        "cdunde/DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 5" }

import struct, chunk, os, time, operator
import quarkx
import quarkpy.mdleditor
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

#Globals
editor = None
logging = 0
exportername = "ie_fm_export.py"
textlog = "fm_ie_log.txt"
progressbar = None
user_frame_list=[]
user_skins_list=[]
g_scale = 1.0


######################################################
# FM Model Constants
######################################################
FM_MAX_TRIANGLES=4096
FM_MAX_VERTICES=2048
FM_MAX_TEXCOORDS=2048
FM_MAX_FRAMES=512
FM_MAX_SKINS=32
FM_MAX_FRAMESIZE=(FM_MAX_VERTICES * 4 + 128)

# The default animation frames list (needs to be changed for .fm file type, this is for Quake2).
FM_FRAME_NAME_LIST=(("stand",1,40),
                    ("run",41,46),
                    ("attack",47,54),
                    ("pain1",55,58),
                    ("pain2",59,62),
                    ("pain3",63,66),
                    ("jump",67,72),
                    ("flip",73,84),
                    ("salute", 85,95),
                    ("taunt",96,112),
                    ("wave",113,123),
                    ("point",124,135),
                    ("crstnd",136,154),
                    ("crwalk",155,160),
                    ("crattack",161,169),
                    ("crpain",170,173),
                    ("crdeath",174,178),
                    ("death1",179,184),
                    ("death2",185,190),
                    ("death3",191,198))
                    #198 frames

######################################################
# FM data structures
######################################################
class fm_alias_triangle: # See .md2 format doc "Vertices". A QuArK's "frame" ['Vertices'].
    vertices = []
    lightnormalindex = 0
    binary_format = "<3BB"
    def __init__(self):
        self.vertices = [0] * 3
        self.lightnormalindex = 0
    def save(self, file):
        temp_data = [0] * 4
        temp_data[0] = self.vertices[0]
        temp_data[1] = self.vertices[1]
        temp_data[2] = self.vertices[2]
        temp_data[3] = self.lightnormalindex
        data = struct.pack(self.binary_format, temp_data[0], temp_data[1], temp_data[2], temp_data[3])
        file.write(data)
        progressbar.progress()
    def dump(self):
        global tobj, logging
        tobj.logcon ("vertex 0,1,2, lightnormalindex: " + str(self.vertices[0]) + ", " + str(self.vertices[1]) + ", " + str(self.vertices[2]) + ", " + str(self.lightnormalindex))
        tobj.logcon ("----------------------------------------")
        
class fm_face: # See .md2 format doc "Triangles". QuArK's "component.triangles".
    vertex_index=[]
    texture_index=[]
    binary_format="<3h3h"
    def __init__(self):
        self.vertex_index = [ 0, 0, 0 ]
        self.texture_index = [ 0, 0, 0]
    def save(self, file):
        temp_data=[0]*6
        temp_data[0]=self.vertex_index[0]
        temp_data[1]=self.vertex_index[1]
        temp_data[2]=self.vertex_index[2]
        temp_data[3]=self.texture_index[0]
        temp_data[4]=self.texture_index[1]
        temp_data[5]=self.texture_index[2]
        data=struct.pack(self.binary_format,temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4],temp_data[5])
        file.write(data)
        progressbar.progress()
    def dump (self):
        global tobj, logging
        tobj.logcon ("vertex indexes: " + str(self.vertex_index[0]) + ", " + str(self.vertex_index[1]) + ", " + str(self.vertex_index[2]))
        tobj.logcon ("texture indexes: " + str(self.texture_index[0]) + ", " + str(self.texture_index[1]) + ", " + str(self.texture_index[2]))
        tobj.logcon ("----------------------------------------")
        
class fm_tex_coord: # See .md2 format doc "Texture coordinates". QuArK's "component.triangles".
    u=0
    v=0
    binary_format="<2h"
    def __init__(self):
        self.u=0
        self.v=0
    def save(self, file, st_coord):
        temp_data=[0]*2
      #  temp_data[0]=self.u
      #  temp_data[1]=self.v
        temp_data[0]=self.u=st_coord[0]
        temp_data[1]=self.v=st_coord[1]
        data=struct.pack(self.binary_format, temp_data[0], temp_data[1])
        file.write(data)
        progressbar.progress()
    def dump (self):
        global tobj, logging
        tobj.logcon ("texture coordinate u, v: " + str(self.u) + ", " + str(self.v))
        tobj.logcon ("----------------------------------------")

class glGLCommands_t:
    TrisTypeNum=0
    cmd_list=[]
    binary_format="<i" #little-endian (<), 1 int
    
    def __init__(self):
        self.TrisTypeNum=0
        self.cmd_list=[]
    
    def save(self,file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # data[0] ex: (4) or (-7), positive int = a triangle strip, negative int = a triangle fan, 0 = end of valid GL_commands data.
        data=struct.pack(self.binary_format, self.TrisTypeNum)
        file.write(data)
        for cmd in self.cmd_list:
            cmd.save(file)
    def dump(self):
        global tobj, logging
        tobj.logcon ("-------------------")
        tobj.logcon ("FM OpenGL Command Structure")
        tobj.logcon ("TrisTypeNum: " + str(self.TrisTypeNum))
        tobj.logcon ("-------------------")
        for cmd in self.cmd_list:
            cmd.dump()
        
class glCommandVertex_t:
    s=0.0
    t=0.0
    vert_index=0
    binary_format="<2fi" #little-endian (<), 2 floats + 1 int
    
    def __init__(self):
        self.s=0.0
        self.t=0.0
        vert_index=0
    def save(self,file):
        # file is the model file & full path, ex: C:\Heretic II\base\models\monsters\chicken2\tris.fm
        # temp_data[0] and temp_data[1] ex: (0.1397, 0.6093), are 2D skin texture coords as floats, percentage of skin size.
        # temp_data[2] the face vertex index the s,t belong to.
        temp_data=[0]*3
        temp_data[0]=float(self.s)
        temp_data[1]=float(self.t)
        temp_data[2]=self.vert_index
        data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2])
        file.write(data)
    def dump (self):
        global tobj, logging
        tobj.logcon ("FM OpenGL Command Vertex")
        tobj.logcon ("s: " + str(self.s))
        tobj.logcon ("t: " + str(self.t))
        tobj.logcon ("vertexIndex: " + str(self.vert_index))
        tobj.logcon ("")

class fm_skin: # See .md2 format doc "Texture information".
    name=""
    binary_format="<64s"
    def __init__(self):
        self.name=""
    def save(self, file):
        if not self.name.endswith(".m8") and not self.name.endswith(".m32"):
            fixname=self.name.split(".")[0]
            fixname=fixname + ".m8"
            temp_data=fixname
        else:
            temp_data=self.name
        data=struct.pack(self.binary_format, temp_data)
        file.write(data)
    def dump (self):
        print "FM Skin"
        print "skin name: ",self.name
        print ""
        
class fm_alias_frame: # See .md2 format doc "Vector", "Vertices" and "Frames". QuArK's "component.dictitems['Frames']".
    scale=[]
    translate=[]
    name=[]
    vertices=[]
 #   binary_format="<3f3f16s"
    binary_format="<3f3f"

    def __init__(self):
        self.scale=[0.0]*3
        self.translate=[0.0]*3
        self.name=""
        self.vertices=[]
    def save(self, file):
        temp_data=[0]*7
        temp_data[0]=float(self.scale[0])
        temp_data[1]=float(self.scale[1])
        temp_data[2]=float(self.scale[2])
        temp_data[3]=float(self.translate[0])
        temp_data[4]=float(self.translate[1])
        temp_data[5]=float(self.translate[2])
      #  temp_data[6]=self.name
      #  data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4],temp_data[5],temp_data[6])
        data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4],temp_data[5])
        file.write(data)

        binary_format="<c"
        name=self.name
        for i in xrange(16):
            temp_data=[0]
            if i >= len(self.name):
                temp_data[0]='\x00'
            else:
                temp_data[0]=name[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)

        progressbar.progress()

    def dump (self):
        global tobj, logging
        tobj.logcon ("scale x,y,z: " + str(self.scale[0]) + ", " + str(self.scale[1]) + ", " + str(self.scale[2]))
        tobj.logcon ("translate x,y,z: " + str(self.translate[0]) + ", " + str(self.translate[1]) + ", " + str(self.translate[2]))
        tobj.logcon ("name: " + self.name)
        tobj.logcon ("----------------------------------------")
        
class fm_obj:
    #Header Structure
    SectionName=[]       #char 32  This is used to identify the file (Must be 'header')
    section_version=0    #int 0    The version number of each section.
    section_byte_size=0  #int 1    The size in bytes of each section.
    skin_width=0         #int 2    The skin width in pixels
    skin_height=0        #int 3    The skin height in pixels
    frame_size=0         #int 4    The size in bytes the frames are
    num_skins=0          #int 5    The number of skins associated with the model
    num_vertices=0       #int 6    The number of vertices (constant for each frame)
    num_tex_coords=0     #int 7    The number of texture coordinates
    num_faces=0          #int 8    The number of faces (polygons)
    num_GL_commands=0    #int 9    The number of gl commands
    num_frames=0         #int 10   The number of animation frames
    num_mesh_nodes=1     #int 11   The number of nodes, believe these are bones.
    binary_format="<12i" #little-endian (<), 12 integers (12i)
    #fm data objects
    tex_coords=[]
    st_coord={}
    faces=[]
    frames=[]
    skins=[]
    GL_commands=[]
    facelist=[]

    def __init__ (self):
        self.tex_coords=[]
        self.st_coord={}
        self.faces=[]
        self.frames=[]
        self.skins=[]
        self.facelist=[]

    def save(self, file):
        global tobj, logging
        #write the "header" data
        binary_format="<c"
        for i in xrange(len(self.SectionName)):
            temp_data=[0]
            temp_data[0]=self.SectionName[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
        temp_data=[0]*12
        temp_data[0]=self.section_version
        temp_data[1]=self.section_byte_size
        temp_data[2]=self.skin_width
        temp_data[3]=self.skin_height
        temp_data[4]=self.frame_size
        temp_data[5]=self.num_skins
        temp_data[6]=self.num_vertices
        temp_data[7]=self.num_tex_coords
        temp_data[8]=self.num_faces
        temp_data[9]=self.num_GL_commands
        temp_data[10]=self.num_frames
        temp_data[11]=self.num_mesh_nodes
        data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4],temp_data[5],temp_data[6],temp_data[7],temp_data[8],temp_data[9],temp_data[10],temp_data[11])
        file.write(data)

        #write the "skin" header
        binary_format="<c"
        skin = "skin"
        for i in xrange(32):
            temp_data=[0]
            if i > 3:
                temp_data[0]='\x00'
            else:
                temp_data[0]=skin[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
        binary_format="<2i"
        section_version = 1
        section_byte_size = self.num_skins * 64 # The binary_format for a fm_skin
        temp_data=[0]*2
        temp_data[0]=section_version
        temp_data[1]=section_byte_size
        data=struct.pack(binary_format, temp_data[0],temp_data[1])
        file.write(data)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: skin")
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        #save the "skin" data
        for skin in self.skins:
            skin.save(file)
            progressbar.progress()

        #write the "st coord" (texture coordinates) header
        binary_format="<c"
        stcoord = "st coord"
        for i in xrange(32):
            temp_data=[0]
            if i > 7:
                temp_data[0]='\x00'
            else:
                temp_data[0]=stcoord[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
        binary_format="<2i"
        section_version = 1
        section_byte_size = self.num_tex_coords * 4 # The binary_format for a fm_tex_coord
        temp_data=[0]*2
        temp_data[0]=section_version
        temp_data[1]=section_byte_size
        data=struct.pack(binary_format, temp_data[0],temp_data[1])
        file.write(data)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: st coord")
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        #save the "st coord" (texture coordinates) data
        for i in xrange(0, self.num_tex_coords):
            self.tex_coords[i].save(file, self.st_coord[i])
            progressbar.progress()
            if logging == 1:
                tobj.logcon ("fm_tex_coord " + str(i))
                self.tex_coords[i].dump()

        #write the "tris" header
        binary_format="<c"
        tris = "tris"
        for i in xrange(32):
            temp_data=[0]
            if i > 3:
                temp_data[0]='\x00'
            else:
                temp_data[0]=tris[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
        binary_format="<2i"
        section_version = 1
        section_byte_size = self.num_faces * 12 # The binary_format for a fm_face
        temp_data=[0]*2
        temp_data[0]=section_version
        temp_data[1]=section_byte_size
        data=struct.pack(binary_format, temp_data[0],temp_data[1])
        file.write(data)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: tris")
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        #save the "tris" data
        count=-1
        for face in self.faces:
            face.save(file)
            progressbar.progress()
            if logging == 1:
                count+=1
                tobj.logcon ("fm_face " + str(count))
                face.dump()

        #write the "frames" header
        binary_format="<c"
        frames = "frames"
        for i in xrange(32):
            temp_data=[0]
            if i > 5:
                temp_data[0]='\x00'
            else:
                temp_data[0]=frames[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
        binary_format="<2i"
        section_version = 1
        section_byte_size = self.frame_size * self.num_frames
        temp_data=[0]*2
        temp_data[0]=section_version
        temp_data[1]=section_byte_size
        data=struct.pack(binary_format, temp_data[0],temp_data[1])
        file.write(data)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: frames")
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        #save the "frames" data
        count=-1
        for frame in self.frames:
            frame.save(file)
            if logging == 1:
                count+=1
                tobj.logcon ("fm_alias_frame " + str(count))
                frame.dump()
                count2=-1
            for vert in frame.vertices:
                vert.save(file)
                if logging == 1:
                    count2+=1
                    tobj.logcon ("fm_alias_triangle " + str(count2))
                    vert.dump()
            progressbar.progress()

        #write the "glcmds" header, see models.c BuildGlCmds for GL_commands list creation code.
        binary_format="<c"
        glcmds = "glcmds"
        for i in xrange(32):
            temp_data=[0]
            if i > 5:
                temp_data[0]='\x00'
            else:
                temp_data[0]=glcmds[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
        binary_format="<2i"
        section_version = 1
        section_byte_size = self.num_GL_commands * 4 # The binary_format for a glCommandVertex_t
        temp_data=[0]*2
        temp_data[0]=section_version
        temp_data[1]=section_byte_size
        data=struct.pack(binary_format, temp_data[0],temp_data[1])
        file.write(data)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: glcmds")
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        if logging == 1:
            tobj.logcon ("START OF GLCMDS at, num_GL_commands: " + str(file.tell()) + ", " + str(self.num_GL_commands))
        #save the "glcmds" GL command List data, see models.c BuildGlCmds for GL_commands list creation code.
        for cmd in self.GL_commands:
            cmd.save(file)
            if logging == 1:
                cmd.dump()
            progressbar.progress()

        #write the "mesh nodes" header
        binary_format="<c"
        meshnodes = "mesh nodes"
        for i in xrange(32):
            temp_data=[0]
            if i > 9:
                temp_data[0]='\x00'
            else:
                temp_data[0]=meshnodes[i]
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
        binary_format="<2i"
        section_version=3
        section_byte_size=516
        temp_data=[0]*2
        temp_data[0]=section_version
        temp_data[1]=section_byte_size
        data=struct.pack(binary_format, temp_data[0],temp_data[1])
        file.write(data)
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: mesh nodes")
            tobj.logcon ("section_version: " + str(section_version))
            tobj.logcon ("section_byte_size: " + str(section_byte_size))
            tobj.logcon ("#####################################################################")
        #save the "mesh nodes" data
        if logging == 1:
            tobj.logcon ("num_mesh_nodes: " + str(self.num_mesh_nodes))
            tobj.logcon ("============================")
            tobj.logcon ("pointer location at start: " + str(file.tell()))
        binary_format="<5b"
        temp_data=[0]*5
        temp_data[0]=temp_data[1]=temp_data[2]=temp_data[3]=-1
        temp_data[4]=1
        data=struct.pack(binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4])
        file.write(data)
        if logging == 1:
            for item in temp_data:
                tobj.logcon ("tri data: (" + str(item) + ",)")
            tobj.logcon ("pointer at end of tri data: " + str(file.tell()))
        binary_format="<b"
        count=256-5
        while count > 0:
            temp_data=[0]
            temp_data[0]=0
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
            count-=1
        binary_format="<3b"
        temp_data=[0]*3
        temp_data[0]=temp_data[1]=-1
        temp_data[2]=127
        data=struct.pack(binary_format, temp_data[0],temp_data[1],temp_data[2])
        file.write(data)
        if logging == 1:
            for item in temp_data:
                tobj.logcon ("vert data: (" + str(item) + ",)")
            tobj.logcon ("pointer at end of vert data: " + str(file.tell()))
            tobj.logcon ("")
        binary_format="<b"
        count=256-3
        while count > 0:
            temp_data=[0]
            temp_data[0]=0
            data = struct.pack(binary_format, temp_data[0])
            file.write(data)
            count-=1
        binary_format="<2h"
        temp_data=[0]*2
        temp_data[0]=0
        temp_data[1]=self.num_GL_commands
        data=struct.pack(binary_format, temp_data[0],temp_data[1])
        file.write(data)
        if logging == 1:
            tobj.logcon ("pointer after, glstart, nbrglcmds: " + str(file.tell()) + ", " + str(temp_data[0]) + ", " + str(temp_data[1]))

        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Skins group data: " + str(self.num_skins) + " skins")
            tobj.logcon ("#####################################################################")
            for skin_counter in range(0, self.num_skins):
                tobj.logcon (user_skins_list.subitems[skin_counter].name)

        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Face group data: " + str(len(self.facelist)/3) + " faces")
            tobj.logcon ("face: (vert_index, U, V)")
            tobj.logcon ("#####################################################################")
            for i in xrange(0, len(self.facelist)/3):
                set=i*3
                tobj.logcon (str(i) + ": [" + str(self.facelist[set]) + ", " + str(self.facelist[set+1]) + ", " + str(self.facelist[set+2]) + "]")

        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Frame group data: " + str(self.num_frames) + " frames")
            tobj.logcon ("frame: frame name")
            tobj.logcon ("#####################################################################")
            for frame in range(0,self.num_frames):
                tobj.logcon (str(frame) + ": " + user_frame_list.subitems[frame].shortname)

    def dump (self):
        global tobj, logging
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Section Name: header")
            tobj.logcon ("section version: " + str(self.section_version))
            tobj.logcon ("section byte size: " + str(self.section_byte_size))
            tobj.logcon ("skin width: " + str(int(self.skin_width)))
            tobj.logcon ("skin height: " + str(int(self.skin_height)))
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
# Fill FM data structure
######################################################
def fill_fm(fm, component):
    global user_frame_list, user_skins_list, progressbar, tobj, Strings

    # Get the component Mesh.
    mesh = component.triangles
    Strings[2455] = component.shortname + "\n" + Strings[2455]
    progressbar = quarkx.progressbar(2455, len(mesh)*6)
    
    #load up some intermediate data structures
    tex_list={}
    tex_count=0
    user_frame_list = component.dictitems['Frames:fg']

    # Header information data.
    header = "header"
    for i in xrange(32):
        if i > 5:
            fm.SectionName.append('\x00')
        else:
            fm.SectionName.append(header[i])
    fm.section_version = 2     # Must be this number.
    fm.section_byte_size = 40  # Always this, the binary size up to and including this point = 32 char + 2 ints (at 4 bytes each)
    fm.num_vertices = len(user_frame_list.dictitems[user_frame_list.subitems[0].name].dictspec['Vertices'])/3 # Number of vertices per frame.
    fm.num_faces = len(component.triangles) # Number of triangles.

    # Get the skin information.
    user_skins_list = component.dictitems['Skins:sg']
    try:
        if str(component.dictspec['skinsize']) != str(user_skins_list.subitems[0].dictspec['Size']):
            component['skinsize'] = user_skins_list.subitems[0].dictspec['Size']
        size = component.dictspec['skinsize']
        fm.skin_width = size[0]
        fm.skin_height = size[1]
        # Use line below as option, embeds skin names into model, none if left out.
        fm.num_skins = len(user_skins_list.subitems) # Number of skins.
    except:
        if len(user_skins_list.subitems) == 0:
            fm.num_skins = 0 # If no skins exist.
        else:
            # Use line below as option, embeds skin names into model, none if left out.
            fm.num_skins = len(user_skins_list.subitems) # Number of skins.
            size = user_skins_list.subitems[0].dictspec['Size']
            fm.skin_width = size[0]
            fm.skin_height = size[1]
    for skin_counter in range(0, fm.num_skins):
        #add a skin node to the fm data structure
        fm.skins.append(fm_skin())
        fm.skins[skin_counter].name = user_skins_list.subitems[skin_counter].name

    # Put texture information in the fm structure.
    # Build UV coords dictionary (prevents double entries-saves space).
    for face in range(0, len(mesh)):
        for i in range(0, len(mesh[face])):
            # A list of sub-lists of the u, v coords. Each vert has its own UV coords.
            fm.tex_coords.append(fm_tex_coord())
        progressbar.progress()
    for face in range(0, len(mesh)):
        fm.faces.append(fm_face())

        for i in range(0, len(mesh[face])):
            t=(mesh[face][i][1], mesh[face][i][2])
            tex_key=(t[0],t[1])
            fm.tex_coords[(face*3)+i].u = mesh[face][i][1] # tex_coords is screwed up here.
            fm.tex_coords[(face*3)+i].v = mesh[face][i][2] # tex_coords is screwed up here.
            fm.faces[face].vertex_index[i] = mesh[face][i][0]
            if logging == 1:
                fm.facelist = fm.facelist + [(mesh[face][i][0], mesh[face][i][1], mesh[face][i][2])]
            if not tex_list.has_key(tex_key):
                tex_list[tex_key] = tex_count
                fm.st_coord[tex_count] = tex_key
                tex_count+=1
            fm.faces[face].texture_index[i] = tex_list[tex_key]
        progressbar.progress()

    fm.num_tex_coords = len(tex_list) # Number of non-duplicated UV coords in Skin-view.

    #compute GL commands
    fm.num_GL_commands=build_GL_commands(fm)

    #get the frame data
    #calculate 1 frame size  + (1 vert size*num_verts)
    fm.frame_size=40+(fm.num_vertices*4) #in bytes
    
    #get the frame list
    user_frame_list = component.dictitems['Frames:fg']
    if user_frame_list=="default":
        fm.num_frames=198
    else:
        fm.num_frames = len(user_frame_list.dictitems) # Number of frames in the Frames group, 'Frames:fg'.

    #fill in each frame with frame info and all the vertex data for that frame
    for frame in range(0,fm.num_frames):
        #add a frame
        fm.frames.append(fm_alias_frame())
        
# Each frame has a scale and transform value that gets the vertex value between 0-255.
# Since the scale and transform are the same for all the verts in the frame,
# we only need to figure this out once per frame

        #we need to start with the bounding box
        vertices = []
        framename = user_frame_list.subitems[frame].name
        frameVertices = user_frame_list.dictitems[framename].dictspec['Vertices']
        for vert_counter in range(0, fm.num_vertices):
            x= frameVertices[(vert_counter*3)]
            y= frameVertices[(vert_counter*3)+1]
            z= frameVertices[(vert_counter*3)+2]
            vertices = vertices + [quarkx.vect(x, y, z)]
        bounding_box = quarkx.boundingboxof(vertices) # Uses the component's frame.vertices

        #the scale is the difference between the min and max (on that axis) / 255
        frame_scale_x=(bounding_box[1].x-bounding_box[0].x)/255
        frame_scale_y=(bounding_box[1].y-bounding_box[0].y)/255
        frame_scale_z=(bounding_box[1].z-bounding_box[0].z)/255
        scale = (frame_scale_x, frame_scale_y, frame_scale_z)
        
        #translate value of the mesh to center it on the origin
        frame_trans_x=bounding_box[0].x
        frame_trans_y=bounding_box[0].y
        frame_trans_z=bounding_box[0].z
        translate = (frame_trans_x, frame_trans_y, frame_trans_z)

        #fill in the data
        fm.frames[frame].scale = scale
        fm.frames[frame].translate = translate
        
        # Now for the frame vertices.
        for vert_counter in range(0, fm.num_vertices):
            # Add a vertex to the fm structure.
            fm.frames[frame].vertices.append(fm_alias_triangle())

            #figure out the new coords based on scale and transform
            #then translates the point so it's not less than 0
            #then scale it so it's between 0..255
            new_x=round(float((frameVertices[(vert_counter*3)]-translate[0])/scale[0]), 0)
            new_y=round(float((frameVertices[(vert_counter*3)+1]-translate[1])/scale[1]), 0)
            new_z=round(float((frameVertices[(vert_counter*3)+2]-translate[2])/scale[2]), 0)
            new_x=int(new_x)
            new_y=int(new_y)
            new_z=int(new_z)
            # Put them in the structure.
            fm.frames[frame].vertices[vert_counter].vertices = (new_x, new_y, new_z)

            # We need to add the lookup table check here.
            fm.frames[frame].vertices[vert_counter].lightnormalindex = 0
            
    # Output all the frame names in the user_frame_list.
        fm.frames[frame].name = framename.split(":")[0]
        progressbar.progress()

    # Compute these after everthing is loaded into a fm structure.
    header_size = 17 * 4 # 17 integers, each integer is 4 bytes.
    skin_size = 64 * fm.num_skins # 64 char per skin * number of skins.
    tex_coord_size = 4 * fm.num_tex_coords # 2 short * number of texture coords.
    face_size = 12 * fm.num_faces # 3 shorts for vertex index, 3 shorts for tex index.
    frames_size = (((12+12+16) + (4 * fm.num_vertices)) * fm.num_frames) # Frame info + verts per frame * num frames.
    GL_command_size = fm.num_GL_commands * 4 # Each is an integer or float, so 4 bytes per.

######################################################
# Tri-Strip/Tri-Fan functions
######################################################
def find_strip_length(fm, start_tri, start_vert):
    #variables shared between fan and strip functions
    global used
    global strip_vert
    global strip_st
    global strip_tris
    global strip_count

    m1=m2=0
    st1=st2=0
    
    used[start_tri]=2

    last=start_tri

    strip_vert[0]=fm.faces[last].vertex_index[start_vert%3]
    strip_vert[1]=fm.faces[last].vertex_index[(start_vert+1)%3]
    strip_vert[2]=fm.faces[last].vertex_index[(start_vert+2)%3]

    strip_st[0]=fm.faces[last].texture_index[start_vert%3]
    strip_st[1]=fm.faces[last].texture_index[(start_vert+1)%3]
    strip_st[2]=fm.faces[last].texture_index[(start_vert+2)%3]

    strip_tris[0]=start_tri
    strip_count=1

    m1=fm.faces[last].vertex_index[(start_vert+2)%3]
    st1=fm.faces[last].texture_index[(start_vert+2)%3]
    m2=fm.faces[last].vertex_index[(start_vert+1)%3]
    st2=fm.faces[last].texture_index[(start_vert+1)%3]
    
    #look for matching triangle
    check=start_tri+1
    
    for tri_counter in range(start_tri+1, fm.num_faces):
        
        for k in range(0,3):
            if fm.faces[check].vertex_index[k]!=m1:
                continue
            if fm.faces[check].texture_index[k]!=st1:
                continue
            if fm.faces[check].vertex_index[(k+1)%3]!=m2:
                continue
            if fm.faces[check].texture_index[(k+1)%3]!=st2:
                continue
            
            #if we can't use this triangle, this tri_strip is done
            if (used[tri_counter]!=0):
                for clear_counter in range(start_tri+1, fm.num_faces):
                    if used[clear_counter]==2:
                        used[clear_counter]=0
                return strip_count

            #new edge
            if (strip_count & 1):
                m2=fm.faces[check].vertex_index[(k+2)%3]
                st2=fm.faces[check].texture_index[(k+2)%3]
            else:
                m1=fm.faces[check].vertex_index[(k+2)%3]
                st1=fm.faces[check].texture_index[(k+2)%3]

            strip_vert[strip_count+2]=fm.faces[tri_counter].vertex_index[(k+2)%3]
            strip_st[strip_count+2]=fm.faces[tri_counter].texture_index[(k+2)%3]
            strip_tris[strip_count]=tri_counter
            strip_count+=1
    
            used[tri_counter]=2
        check+=1
    return strip_count

def find_fan_length(fm, start_tri, start_vert):
    #variables shared between fan and strip functions
    global used
    global strip_vert
    global strip_st
    global strip_tris
    global strip_count

    m1=m2=0
    st1=st2=0
    
    used[start_tri]=2

    last=start_tri

    strip_vert[0]=fm.faces[last].vertex_index[start_vert%3]
    strip_vert[1]=fm.faces[last].vertex_index[(start_vert+1)%3]
    strip_vert[2]=fm.faces[last].vertex_index[(start_vert+2)%3]
    
    strip_st[0]=fm.faces[last].texture_index[start_vert%3]
    strip_st[1]=fm.faces[last].texture_index[(start_vert+1)%3]
    strip_st[2]=fm.faces[last].texture_index[(start_vert+2)%3]

    strip_tris[0]=start_tri
    strip_count=1

    m1=fm.faces[last].vertex_index[(start_vert+0)%3]
    st1=fm.faces[last].texture_index[(start_vert+0)%3]
    m2=fm.faces[last].vertex_index[(start_vert+2)%3]
    st2=fm.faces[last].texture_index[(start_vert+2)%3]

    #look for matching triangle    
    check=start_tri+1
    for tri_counter in range(start_tri+1, fm.num_faces):
        for k in range(0,3):
            if fm.faces[check].vertex_index[k]!=m1:
                continue
            if fm.faces[check].texture_index[k]!=st1:
                continue
            if fm.faces[check].vertex_index[(k+1)%3]!=m2:
                continue
            if fm.faces[check].texture_index[(k+1)%3]!=st2:
                continue
            
            #if we can't use this triangle, this tri_strip is done
            if (used[tri_counter]!=0):
                for clear_counter in range(start_tri+1, fm.num_faces):
                    if used[clear_counter]==2:
                        used[clear_counter]=0
                return strip_count

            #new edge
            m2=fm.faces[check].vertex_index[(k+2)%3]
            st2=fm.faces[check].texture_index[(k+2)%3]
            
            strip_vert[strip_count+2]=m2
            strip_st[strip_count+2]=st2
            strip_tris[strip_count]=tri_counter
            strip_count+=1
    
            used[tri_counter]=2
        check+=1
    return strip_count


######################################################
# Globals for GL command list calculations
######################################################
used=[]
strip_vert=0
strip_st=0
strip_tris=0
strip_count=0

######################################################
# Build GL command List
######################################################
def build_GL_commands(fm):
    #variables shared between fan and strip functions
    global used
    used=[0]*fm.num_faces
    global strip_vert
    strip_vert=[0]*128
    global strip_st
    strip_st=[0]*128
    global strip_tris
    strip_tris=[0]*128
    global strip_count
    strip_count=0
    
    #variables
    num_commands=0
    start_vert=0
    fan_length=strip_length=0
    length=best_length=0
    best_type=0
    best_vert=[0]*1024
    best_st=[0]*1024
    best_tris=[0]*1024
    s=0.0
    t=0.0
    
    for face_counter in range(0,fm.num_faces):
        if used[face_counter]==1: #don't evaluate a tri that's been used
            pass
        else:
            best_length=0 #restart the counter
            #for each vertex index in this face
            for start_vert in range(0,3):
                strip_length=find_strip_length(fm, face_counter, start_vert)
                if (strip_length>best_length): 
                    best_type=0
                    best_length=strip_length
                    for index in range (0, best_length+2):
                        best_st[index]=strip_st[index]
                        best_vert[index]=strip_vert[index]
                    for index in range(0, best_length):
                        best_tris[index]=strip_tris[index]

                fan_length=find_fan_length(fm, face_counter, start_vert)
                if (fan_length>best_length):
                    best_type=1
                    best_length=fan_length
                    for index in range (0, best_length+2):
                        best_st[index]=strip_st[index]
                        best_vert[index]=strip_vert[index]
                    for index in range(0, best_length):
                        best_tris[index]=strip_tris[index]

            #mark the tris on the best strip/fan as used
            for used_counter in range (0, best_length):
                used[best_tris[used_counter]]=1

            temp_cmdlist=glGLCommands_t()
            #push the number of commands into the command stream
            if best_type==1:
                temp_cmdlist.TrisTypeNum=(-(best_length+2))
                num_commands+=1
            else:
                temp_cmdlist.TrisTypeNum=best_length+2
                num_commands+=1
            for command_counter in range (0, best_length+2):
                #emit a vertex into the reorder buffer
                cmd=glCommandVertex_t()
                index=best_st[command_counter]
                #calc and put S/T coords in the structure
            #    s=fm.tex_coords[index].u # tex_coords is screwed up here.
            #    t=fm.tex_coords[index].v # tex_coords is screwed up here.
                s=fm.st_coord[index][0]
                t=fm.st_coord[index][1]
                try:
                    s=(s+0.5)/fm.skin_width
                    t=(t+0.5)/fm.skin_height
                except:
                    s=(s+0.5)/1
                    t=(t+0.5)/1
                cmd.s=s
                cmd.t=t
                cmd.vert_index=best_vert[command_counter]
                temp_cmdlist.cmd_list.append(cmd)
                num_commands+=3
            fm.GL_commands.append(temp_cmdlist)
    
    #end of list
    temp_cmdlist=glGLCommands_t()    
    temp_cmdlist.TrisTypeNum=0
    fm.GL_commands.append(temp_cmdlist)  
    num_commands+=1
    
    #cleanup and return
    used=best_vert=best_st=best_tris=strip_vert=strip_st=strip_tris=0
    return num_commands

######################################################
# Save FM Format
######################################################
def save_fm(filename):
    global editor, tobj, logging, exportername, textlog, Strings
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
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select one component\nfolder at a time for exporting.\n\nAn item that is not a component folder\nis in your selections.\n\nDeselect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
    if len(objects) > 1:
        quarkx.msgbox(str(len(objects)) + " Components have been selected for exporting.\nYou can ONLY select one component folder at a time for exporting.\n\nComponents can be combined or copied into one,\nbut only one skin can be used at a time.\n\nCorrect and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        return
    else:
        if not objects[0].dictitems['Frames:fg'] or len(objects[0].dictitems['Frames:fg'].subitems) == 0:
            quarkx.msgbox("No frames exist for exporting.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if len(objects[0].dictitems['Frames:fg'].subitems[0].dictspec['Vertices']) == 0:
            quarkx.msgbox("Nothing exist for exporting.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    fm = fm_obj()  #blank fm object to save

    #get the component
    component = editor.layout.explorer.sellist[0] #this gets the first component (should be only one)

    fill_fm(fm, component)

    #actually write it to disk
    file = open(filename,"wb")
    fm.save(file)
    if logging == 1:
        fm.dump() # Writes the file Header last to the log for comparison reasons.
    file.close()
    progressbar.close()
    Strings[2455] = Strings[2455].replace(component.shortname + "\n", "")

    #cleanup
    fm = 0

    add_to_message = "Any used skin textures that are not a .m8 or .m32\nwill need to be created by saving it as a .m8 to go with the model"
    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

# Saves the model file: root is the actual file,
# filename is the full path and name of the .fm file to create.
# gamename is None.
# For example:  C:\Heretic II\base\models\monsters\assassin\tris.fm
def savemodel(root, filename, gamename, nomessage=0):
    save_fm(filename)

### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".fm Heretic II Exporter", ".fm file", "*.fm", savemodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_fm_export.py,v $
# Revision 1.8  2013/02/20 05:19:41  cdunde
# Fix for sometimes incorrect skinsize being used.
#
# Revision 1.7  2011/10/21 19:29:11  cdunde
# Update for proper GLcommands code processing.
#
# Revision 1.6  2011/10/14 05:27:10  cdunde
# Final, fixed the GLcommands properly.
#
# Revision 1.5  2011/10/11 07:19:36  cdunde
# Update to display full model in game without blowing it up.
# build_GL_commands section and related functions still not correct, needs work.
#
# Revision 1.4  2011/10/02 06:18:31  cdunde
# To match class names with importer and fix cause of blowing up the game.
# Model does NOT show up in game but its bounding box works. Need someone to fix this.
#
# Revision 1.3  2011/09/28 06:56:54  cdunde
# Texture naming update.
#
# Revision 1.2  2011/09/28 05:29:23  cdunde
# Comment update.
#
# Revision 1.1  2011/09/28 105:15:46  cdunde
# Added export support for Heretic II static and animation models .fm file type.
#