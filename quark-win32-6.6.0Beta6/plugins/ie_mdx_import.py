# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Kingpin .mdx model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_mdx_import.py,v 1.9 2011/10/21 06:22:20 cdunde Exp $


Info = {
   "plug-in":       "ie_mdx_importer",
   "desc":          "This script imports a Kingpin file (MDX), textures, and animations into QuArK for editing.",
   "date":          "May 12 2011",
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
importername = "ie_mdx_importer.py"
textlog = "mdx_ie_log.txt"
progressbar = None
g_scale = 1.0

######################################################
# Main Body
######################################################

#returns the string from a null terminated string
def asciiz (s):
  n = 0
  while (ord(s[n]) != 0):
    n = n + 1
  return s[0:n]


######################################################
# MDX Model Constants
######################################################
MDX_MAX_TRIANGLES=4096
MDX_MAX_VERTICES=2048
MDX_MAX_TEXCOORDS=2048
MDX_MAX_FRAMES=1024
MDX_MAX_SKINS=32
MDX_MAX_FRAMESIZE=(MDX_MAX_VERTICES * 4 + 128)

######################################################
# MDX data structures
######################################################
class mdx_alias_triangle:
    vertices=[]
    lightnormalindex=0

    binary_format="<3BB" #little-endian (<), 3 Unsigned char
    
    def __init__(self):
        self.vertices=[0]*3
        self.lightnormalindex=0

    def load(self, file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # data[0] through data[3] ex: (178, 143, 180, 63), 3 texture coords and normal (normal not needed).
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.vertices[0]=data[0]
        self.vertices[1]=data[1]
        self.vertices[2]=data[2]
        self.lightnormalindex=data[3]
        return self

    def dump(self):
        print "MDX Alias_Triangle Structure"
        print "vertex: ", self.vertices[0]
        print "vertex: ", self.vertices[1]
        print "vertex: ", self.vertices[2]
        print "lightnormalindex: ",self.lightnormalindex
        print ""

class mdx_face:
    vertex_index=[]
    texture_index=[] # only has zeros so not being used, see "class glCommandVertex_t" below

    binary_format="<3h3h" #little-endian (<), 3 short, 3 short
    
    def __init__(self):
        self.vertex_index = [ 0, 0, 0 ]
        self.texture_index = [ 0, 0, 0]

    def load (self, file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
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
        print "MDX Face Structure"
        print "vertex index: ", self.vertex_index[0]
        print "vertex index: ", self.vertex_index[1]
        print "vertex index: ", self.vertex_index[2]
        print "texture index: ", self.texture_index[0]
        print "texture index: ", self.texture_index[1]
        print "texture index: ", self.texture_index[2]
        print ""

class glGLCommands_t:
    TrisTypeNum=None
    SubObjectID=None

    binary_format="<2i" #little-endian (<), 2 ints

    def __init__(self):
        self.TrisTypeNum=None
        self.SubObjectID=None

    def load (self, file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # data[0] ex: (4) or (-7), positive int = a triangle strip, negative int = a triangle fan, 0 = end of valid GL_commands data.
        # data[1] ex: (3), positive int, the model component (section) this data applies to.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.TrisTypeNum=data[0]
        self.SubObjectID=data[1]
        return self

    def dump (self):
        print "MDX GL Command Structure"
        print "TrisTypeNum: ",self.TrisTypeNum
        print "SubObjectID: ",self.SubObjectID
        print ""

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
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # data[0] and data[1] ex: (0.1397, 0.6093), are 2D skin texture coords as floats, percentage of skin size.
        # data[3] the face vertex index the u,v belong to.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.u=data[0]
        self.v=data[1]
        self.vertexIndex=data[2]
        return self

    def dump (self):
        print "MDX GL Command Vertex"
        print "u: ",self.u
        print "v: ",self.v
        print "vertexIndex: ",self.vertexIndex
        print ""

class BBox_t:
    min=(0.,0.,0.)
    max=(0.,0.,0.)

    binary_format="<6f" #little-endian (<), 6 floats

    def __init__(self):
        self.min=(0.,0.,0.)
        self.max=(0.,0.,0.)

    def load (self, file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # data[0] through data[5] are coords as floats.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.min=(data[0], data[1], data[2])
        self.max=(data[3], data[4], data[5])
        return self

    def dump (self):
        print "MDX BBox Frames Structure"
        print "min: ",self.min
        print "max: ",self.max
        print ""


class mdx_skin:
    name=""

    binary_format="<64s" #little-endian (<), char[64]

    def __init__(self):
        self.name=""

    def load (self, file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # self.name is just the skin texture path and name, ex: models/weapons/crowbar.tga
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.name=asciiz(data[0])
        return self

    def dump (self):
        print "MDX Skin"
        print "skin name: ",self.name
        print ""

class mdx_alias_frame:
    scale=[0.0]*3
    translate=[0.0]*3
    name=""
    vertices=[]

    binary_format="<3f3f16s" #little-endian (<), 3 float, 3 float char[16]
    #did not add the "3bb" to the end of the binary format
    #because the alias_vertices will be read in through
    #thier own loader

    def __init__(self):
        self.scale=[0.0]*3
        self.translate=[0.0]*3
        self.name=""
        self.vertices=[]


    def load (self, file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # self.scale[0] through self.scale[2] ex: 0.12633632123470306, 0.077566042542457581, 0.21140974760055542,
        # self.translate[0] through self.translate[2] ex: -16.496400833129883, -9.5092992782592773, -24.108100891113281,
        # self.name is the frame name ex: active_01
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.scale[0]=data[0]
        self.scale[1]=data[1]
        self.scale[2]=data[2]
        self.translate[0]=data[3]
        self.translate[1]=data[4]
        self.translate[2]=data[5]
        self.name=asciiz(data[6])
        return self

    def dump (self):
        print "MDX Alias Frame"
        print "scale x: ",self.scale[0]
        print "scale y: ",self.scale[1]
        print "scale z: ",self.scale[2]
        print "translate x: ",self.translate[0]
        print "translate y: ",self.translate[1]
        print "translate z: ",self.translate[2]
        print "name: ",self.name
        print ""

class mdx_obj:
    #Header Structure
    ident=0              #int  0   This is used to identify the file
    version=0            #int  1   The version number of the file (Must be 8)
    skin_width=0         #int  2   The skin width in pixels
    skin_height=0        #int  3   The skin height in pixels
    frame_size=0         #int  4   The size in bytes the frames are
    num_skins=0          #int  5   The number of skins associated with the model
    num_vertices=0       #int  6   The number of vertices (constant for each frame)
    num_faces=0          #int  7   The number of faces, triangles (polygons)
    num_GL_commands=0    #int  8   The number of gl commands
    num_frames=0         #int  9   The number of animation frames
    num_SfxDefines=0     #int 10   The number of sfx definitions
    num_SfxEntries=0     #int 11   The number of sfx entries
    num_SubObjects=0     #int 12   The number of subobjects in mdx file
    offset_skins=0       #int 13   The offset in the file for the skin data
    offset_faces=0       #int 14   The offset in the file for the face data
    offset_frames=0      #int 15   The offset in the file for the frames data
    offset_GL_commands=0 #int 16   The offset in the file for the gl commands data
    offset_VertexInfo=0  #int 17   The offset in the file for the vertex info data
    offset_SfxDefines=0  #int 18   The offset in the file for the sfx definitions data
    offset_SfxEntries=0  #int 19   The offset in the file for the sfx entries data
    offset_BBoxFrames=0  #int 20   The offset in the file for the bbox frames data
    offset_DummyEnd=0    #int 21   Same as offset_end below
    offset_end=0         #int 22   The end of the file offset

    binary_format="<23i"  #little-endian (<), 23 integers

    #mdx data objects
    faces=[]
    frames=[]
    skins=[]

    def __init__ (self):
        self.faces=[]
        self.frames=[]
        self.skins=[]


    def load (self, file, name):
        global progressbar

        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # data is all of the header data amounts.
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.ident=data[0]
        self.version=data[1]

        if (self.ident!=1481655369 or self.version!=4): # Not a valid MDX file.
            return None, None

        self.skin_width=data[2]
        self.skin_height=data[3]
        self.frame_size=data[4]

        #make the # of skin objects for model
        self.num_skins=data[5]
        for i in xrange(0,self.num_skins):
            self.skins.append(mdx_skin())

        self.num_vertices=data[6]

        #make the # of triangle faces for model
        self.num_faces=data[7]
        for i in xrange(0,self.num_faces):
            self.faces.append(mdx_face())

        self.num_GL_commands=data[8]

        #make the # of frames for the model
        self.num_frames=data[9]
        for i in xrange(0,self.num_frames):
            self.frames.append(mdx_alias_frame())
            #make the # of vertices for each frame
            for j in xrange(0,self.num_vertices):
                self.frames[i].vertices.append(mdx_alias_triangle())

        self.num_SfxDefines=data[10]

        self.num_SfxEntries=data[11]

        self.num_SubObjects=data[12]

        self.offset_skins=data[13]
        self.offset_faces=data[14]
        self.offset_frames=data[15]
        self.offset_GL_commands=data[16]
        self.offset_VertexInfo=data[17]
        self.offset_SfxDefines=data[18]
        self.offset_SfxEntries=data[19]
        self.offset_BBoxFrames=data[20]
        self.offset_DummyEnd=data[21]
        self.offset_end=data[22]

        #load the skin data
        file.seek(self.offset_skins,0)
        for i in xrange(0, self.num_skins):
            self.skins[i].load(file)
            #self.skins[i].dump()

        #load the face data
        file.seek(self.offset_faces,0)
        for i in xrange(0, self.num_faces):
            self.faces[i].load(file)
            #self.faces[i].dump()

        #load the frames
        file.seek(self.offset_frames,0)
        for i in xrange(0, self.num_frames):
            self.frames[i].load(file)
            #self.frames[i].dump()
            for j in xrange(0,self.num_vertices):
                self.frames[i].vertices[j].load(file)
                #self.frames[i].vertices[j].dump()

        Strings[2454] = name + "\n" + Strings[2454]
        progressbar = quarkx.progressbar(2454, (self.num_faces * self.num_SubObjects) + self.num_frames)

        message = "" # An empty string to add needed messages to.
        skinsize, skingroup, message = load_textures(self, message) # Calls here to make the Skins Group.

        # Now we can name our component that will be imported.
        ComponentList = []
        if self.num_SubObjects < 2:
            Component = quarkx.newobj(name + ':mc')
            ComponentList = ComponentList + [Component]
        else:
            for i in xrange(0, self.num_SubObjects):
                Component = quarkx.newobj(name + '_' + str(i+1) + ':mc')
                ComponentList = ComponentList + [Component]

        ######### Make the faces for QuArK, the 'component.triangles', which is also the 'Tris'.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Face group data: " + str(self.num_faces) + " faces")
            tobj.logcon ("face: (vert_index, U, V)")
            tobj.logcon ("#####################################################################")

        faces = []
        for i in xrange(0, self.num_SubObjects):
            faces += [[]]

        #load the GL_commands to get the skin U,V values
        file.seek(self.offset_GL_commands,0)
        for i in xrange(0, self.num_GL_commands):
            gl_command = glGLCommands_t()
            gl_command.load(file)
            #gl_command.dump()
            if gl_command.TrisTypeNum is not None:
                if gl_command.TrisTypeNum == 0: # end of valid GL_commands data section
                    break
                if gl_command.TrisTypeNum > -1: # a triangle strip
                    for j in xrange(0, gl_command.TrisTypeNum):
                        gl_vertex = glCommandVertex_t()
                        gl_vertex.load(file)
                        #gl_vertex.dump()

                        if j == 0:
                            vertex_info0 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                        elif j == 1:
                            vertex_info1 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                        else:
                            vertex_info2 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                            faces[gl_command.SubObjectID] += [(vertex_info0, vertex_info1, vertex_info2)]
                            if not j&1: # This test if a number is even.
                                vertex_info0 = vertex_info2
                            else: # else it is odd.
                                vertex_info1 = vertex_info2
                else: # a triangle fan
                    for j in xrange(0, gl_command.TrisTypeNum * -1):
                        gl_vertex = glCommandVertex_t()
                        gl_vertex.load(file)
                        #gl_vertex.dump()

                        if j == 0:
                            vertex_info0 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                        elif j == 1:
                            vertex_info1 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                        else:
                            vertex_info2 = (gl_vertex.vertexIndex, gl_vertex.u, gl_vertex.v)
                            faces[gl_command.SubObjectID] += [(vertex_info0, vertex_info1, vertex_info2)]
                            vertex_info1 = vertex_info2

        #load the BBoxFrames data
        file.seek(self.offset_BBoxFrames,0)
        self.BBoxes = []
        bboxgroup = quarkx.newobj("BBoxes "+name+":bbg")
        bboxgroup['show'] = (1.0,)
      #  print "BBoxes"
        for i in xrange(0, self.num_SubObjects):
            Component = ComponentList[i]
      #      print "==============="
      #      print "Component.name", Component.name
      #      print "==============="
            bboxSubObj = []
            for j in xrange(0, self.num_frames):
      #          print "-------"
      #          print "frame name:", self.frames[j].name
                BBox = BBox_t()
                BBox.load(file)
                bboxSubObj.append(BBox)
      #          BBox.dump()
                if j == 0: # Temp code until we figure out what to do with these, ref melutils.py DrawBBoxes function.
                    bboxname = Component.name.replace(":mc", ":p")
                    bbox = [BBox.min, BBox.max]
                    editor.ModelComponentList['bboxlist'][bboxname] = {}
                    editor.ModelComponentList['bboxlist'][bboxname]['size'] = bbox
                    p = MakePoly(Component.name, bbox)
                    bboxgroup.appenditem(p)
            self.BBoxes.append(bboxSubObj)

        # make up vertex index conversion lists.
        self.fvc = {} # fvc = frames vertex index conversion.
        for i in xrange(0, self.num_SubObjects):
            self.fvc[i] = []
            for j in xrange(0, len(faces[i])):
                current_face = faces[i][j]
                if not current_face[0][0] in self.fvc[i]:
                    self.fvc[i].append(current_face[0][0])
                if not current_face[1][0] in self.fvc[i]:
                    self.fvc[i].append(current_face[1][0])
                if not current_face[2][0] in self.fvc[i]:
                    self.fvc[i].append(current_face[2][0])
        tvc = {} # tvc = Tris vertex index conversion.
        for i in xrange(0, self.num_SubObjects):
            tvc[i] = {}
            for j in range(len(self.fvc[i])):
                tvc[i][self.fvc[i][j]] = j

        for i in xrange(0, self.num_SubObjects):
            Component = ComponentList[i]
            Tris = ''
            # Don't use these, sometimes they are wrong. Use the actual imported texture skinsize instead.
            #TexWidth = self.skin_width
            #TexHeight = self.skin_height
            TexWidth = skinsize[0]
            TexHeight = skinsize[1]
            for j in xrange(0, len(faces[i])):
                current_face = faces[i][j]
                if logging == 1:
                    facelist = []
                    facelist = facelist + [(tvc[i][current_face[0][0]], int(TexWidth * current_face[0][1]), int(TexHeight * current_face[0][2]))]
                    facelist = facelist + [(tvc[i][current_face[1][0]], int(TexWidth * current_face[1][1]), int(TexHeight * current_face[1][2]))]
                    facelist = facelist + [(tvc[i][current_face[2][0]], int(TexWidth * current_face[2][1]), int(TexHeight * current_face[2][2]))]
                    tobj.logcon (str(j) + ": " + str(facelist))
                Tris = Tris + struct.pack("Hhh", tvc[i][current_face[0][0]], int(TexWidth * current_face[0][1]), int(TexHeight * current_face[0][2]))
                Tris = Tris + struct.pack("Hhh", tvc[i][current_face[1][0]], int(TexWidth * current_face[1][1]), int(TexHeight * current_face[1][2]))
                Tris = Tris + struct.pack("Hhh", tvc[i][current_face[2][0]], int(TexWidth * current_face[2][1]), int(TexHeight * current_face[2][2]))
                progressbar.progress()
            Component['Tris'] = Tris

        return self, ComponentList, skinsize, skingroup, message, bboxgroup

    def dump (self):
        global tobj, logging
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Header Information")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("ident: " + str(self.ident))
            tobj.logcon ("version: " + str(self.version))
            tobj.logcon ("skin width: " + str(self.skin_width))
            tobj.logcon ("skin height: " + str(self.skin_height))
            tobj.logcon ("frames byte size: " + str(self.frame_size))
            tobj.logcon ("number of skins: " + str(self.num_skins))
            tobj.logcon ("number of vertices per frame: " + str(self.num_vertices))
            tobj.logcon ("number of faces: " + str(self.num_faces))
            tobj.logcon ("number of GL commands: " + str(self.num_GL_commands))
            tobj.logcon ("number of frames: " + str(self.num_frames))
            tobj.logcon ("number of SfxDefines: " + str(self.num_SfxDefines))
            tobj.logcon ("number of SfxEntries: " + str(self.num_SfxEntries))
            tobj.logcon ("number of SubObjects: " + str(self.num_SubObjects))
            tobj.logcon ("offset skins: " + str(self.offset_skins))
            tobj.logcon ("offset faces: " + str(self.offset_faces))
            tobj.logcon ("offset frames: " + str(self.offset_frames))
            tobj.logcon ("offset GL Commands: " + str(self.offset_GL_commands))
            tobj.logcon ("offset VertexInfo: " + str(self.offset_VertexInfo))
            tobj.logcon ("offset SfxDefines: " + str(self.offset_SfxDefines))
            tobj.logcon ("offset SfxEntries: " + str(self.offset_SfxEntries))
            tobj.logcon ("offset BBoxFrames: " + str(self.offset_BBoxFrames))
            tobj.logcon ("offset DummyEnd: " + str(self.offset_DummyEnd))
            tobj.logcon ("offset end: " + str(self.offset_end))
            tobj.logcon ("")

######################################################
# QuArK Import functions
######################################################
# Create the bboxes (hit boxes).
def MakePoly(compname, bbox):
    m = bbox[0]
    M = bbox[1]
    shortname = compname.split(":")[0]
    p = quarkx.newobj(shortname + ":p");
    p["assigned2"] = compname
    p['show'] = (1.0,)
    face = quarkx.newobj("north:f") # BACK FACE
    vtx0X, vtx0Y, vtx0Z = m[0],M[1],M[2]
    vtx1X, vtx1Y, vtx1Z = M[0],M[1],M[2]
    vtx2X, vtx2Y, vtx2Z = m[0],M[1],m[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("east:f") # RIGHT FACE
    vtx0X, vtx0Y, vtx0Z = M[0],M[1],M[2]
    vtx1X, vtx1Y, vtx1Z = M[0],m[1],M[2]
    vtx2X, vtx2Y, vtx2Z = M[0],M[1],m[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("south:f") # FRONT FACE
    vtx0X, vtx0Y, vtx0Z = M[0],m[1],M[2]
    vtx1X, vtx1Y, vtx1Z = m[0],m[1],M[2]
    vtx2X, vtx2Y, vtx2Z = M[0],m[1],m[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("west:f") # LEFT FACE
    vtx0X, vtx0Y, vtx0Z = m[0],m[1],M[2]
    vtx1X, vtx1Y, vtx1Z = m[0],M[1],M[2]
    vtx2X, vtx2Y, vtx2Z = m[0],m[1],m[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("up:f") # TOP FACE
    vtx0X, vtx0Y, vtx0Z = m[0],M[1],M[2]
    vtx1X, vtx1Y, vtx1Z = m[0],m[1],M[2]
    vtx2X, vtx2Y, vtx2Z = M[0],M[1],M[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)
    face = quarkx.newobj("down:f") # BOTTOM FACE
    vtx0X, vtx0Y, vtx0Z = m[0],M[1],m[2]
    vtx1X, vtx1Y, vtx1Z = M[0],M[1],m[2]
    vtx2X, vtx2Y, vtx2Z = m[0],m[1],m[2]
    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
    face["tex"] = None
    p.appenditem(face)

    return p

def load_textures(mdx, message):
    global tobj, logging
    # Checks if the model has textures specified with it.
    skinsize = (256, 256)
    skingroup = quarkx.newobj('Skins:sg')
    skingroup['type'] = chr(2)
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Skins group data: " + str(mdx.num_skins) + " skins")
        tobj.logcon ("#####################################################################")
    if int(mdx.num_skins) > 0:
        for i in xrange(0,mdx.num_skins):
            # Only writes to the console here.
           # mdx.skins[i].dump() # Comment out later, just prints to the console what the skin(s) are.
            if logging == 1:
                tobj.logcon (mdx.skins[i].name)
            skinname = mdx.skins[i].name.split('/')
            images = []
            # First try to find the skin in the current model's folder.
            if os.path.exists(os.getcwd() + "\\" + skinname[len(skinname)-1]):
                images = [os.getcwd() + "\\" + skinname[len(skinname)-1]]
        if len(images) == 0:
            # Probably skin not found; let's try the player-model variations
            if skinname[-1].find("skin_upper") != -1:
                for filename in os.listdir(os.getcwd()):
                    if filename.startswith("body") and (filename.endswith(".tga") or filename.endswith(".TGA")):
                        images += [os.getcwd() + "\\" + filename]
            elif skinname[-1].find("skin_head") != -1:
                for filename in os.listdir(os.getcwd()):
                    if filename.startswith("head") and (filename.endswith(".tga") or filename.endswith(".TGA")):
                        images += [os.getcwd() + "\\" + filename]
            elif skinname[-1].find("skin_lower") != -1:
                for filename in os.listdir(os.getcwd()):
                    if filename.startswith("legs") and (filename.endswith(".tga") or filename.endswith(".TGA")):
                        images += [os.getcwd() + "\\" + filename]

        if len(images) == 0: # Skin maybe in another folder, try to find it.
            dir = os.getcwd()
            skinname = mdx.skins[0].name
            if dir.find("\\main") != -1:
                dir = dir.split("main")[0]
                if skinname.startswith("/") or skinname.startswith("\\"):
                    fullpath = dir + "main" + skinname
                else:
                    fullpath = dir + "main/" + skinname
                # let's try the player-model variations first
                if skinname.find("skin_upper") != -1:
                    path = fullpath.rsplit("/", 1)[0]
                    for filename in os.listdir(path):
                        if filename.startswith("body") and (filename.endswith(".tga") or filename.endswith(".TGA")):
                            images += [path + "\\" + filename]
                elif skinname.find("skin_head") != -1:
                    path = fullpath.rsplit("/", 1)[0]
                    for filename in os.listdir(path):
                        if filename.startswith("head") and (filename.endswith(".tga") or filename.endswith(".TGA")):
                            images += [path + "\\" + filename]
                elif skinname.find("skin_lower") != -1:
                    path = fullpath.rsplit("/", 1)[0]
                    for filename in os.listdir(path):
                        if filename.startswith("legs") and (filename.endswith(".tga") or filename.endswith(".TGA")):
                            images += [path + "\\" + filename]
                else:
                    images += [fullpath]

        if len(images) == 0:
            for i in xrange(0,mdx.num_skins):
                message = message + "Missing skin name: " + mdx.skins[i].name + "\r\n"

        for j in range(len(images)):
            try:
                image = quarkx.openfileobj(images[j])
            except:
                message = message + "Missing skin name: " + mdx.skins[i].name + "\r\n"
                continue
            if len(images) > 1:
                skinname_temp = mdx.skins[i].name.rsplit(".",1)
                skinname_temp = skinname_temp[0] + "_" + str(j+1) + "." + skinname_temp[1]
                skin = quarkx.newobj(skinname_temp)
            else:
                skin = quarkx.newobj(mdx.skins[i].name)
            skin['Image1'] = image.dictspec['Image1']
            try:
                skin['Pal'] = image.dictspec['Pal']
            except:
                pass
            skin['Size'] = image.dictspec['Size']
            skingroup.appenditem(skin)
            if j == 0: # Only use the 1st one to set this.
                skinsize = image.dictspec['Size'] # Used for QuArK.

        return skinsize, skingroup, message
    else:
        return skinsize, skingroup, message

def animate_mdx(mdx, ComponentList, skingroup): # The Frames Group is made here & returned to be added to the Component.
    global progressbar, tobj, logging
    ######### Animate the verts through the QuArK Frames lists.
    sdogroup = quarkx.newobj('SDO:sdo')
    for c in range(len(ComponentList)):
        ComponentList[c].appenditem(sdogroup.copy())
        ComponentList[c].appenditem(skingroup.copy())
        framesgroup = quarkx.newobj('Frames:fg')

        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("Frame group data: " + str(mdx.num_frames) + " frames")
            tobj.logcon ("frame: frame name")
            tobj.logcon ("#####################################################################")

        fvc = mdx.fvc[c]
        for i in xrange(0, mdx.num_frames):
            ### mdx.frames[i].name is the frame name, ex: active_01
            if logging == 1:
                tobj.logcon (str(i) + ": " + mdx.frames[i].name)

            frame = quarkx.newobj(mdx.frames[i].name + ':mf')
            mesh = ()
            #update the vertices
            for j in range(len(fvc)):
                x=(mdx.frames[i].scale[0]*mdx.frames[i].vertices[fvc[j]].vertices[0]+mdx.frames[i].translate[0])*g_scale
                y=(mdx.frames[i].scale[1]*mdx.frames[i].vertices[fvc[j]].vertices[1]+mdx.frames[i].translate[1])*g_scale
                z=(mdx.frames[i].scale[2]*mdx.frames[i].vertices[fvc[j]].vertices[2]+mdx.frames[i].translate[2])*g_scale

                #put the vertex in the right spot
                mesh = mesh + (x,)
                mesh = mesh + (y,)
                mesh = mesh + (z,)

            frame['Vertices'] = mesh
            framesgroup.appenditem(frame)
            progressbar.progress()
        ComponentList[c].appenditem(framesgroup)


def load_mdx(mdx_filename):
    global progressbar, tobj, logging, Strings
    #read the file in
    file = open(mdx_filename,"rb")
    mdx = mdx_obj()
    name = mdx_filename.replace("\\", "/")
    name = name.split(".")[0]
    name = name.split("/")
    name = name[len(name)-2] + "_" + name[len(name)-1]
    MODEL, ComponentList, skinsize, skingroup, message, bboxgroup = mdx.load(file, name)

    file.close()
    if MODEL is None:
        return None, None, None, None, message

    animate_mdx(mdx, ComponentList, skingroup) # Calls here to make the Frames Group.
    
    progressbar.close()
    Strings[2454] = Strings[2454].replace(name + "\n", "")

    if logging == 1:
        mdx.dump() # Writes the file Header last to the log for comparison reasons.

    return ComponentList, skinsize, message, bboxgroup


########################
# To run this file
########################

def import_mdx_model(editor, mdx_filename):
    # Now we call to Import our Component(s).

    ComponentList, skinsize, message, bboxgroup = load_mdx(mdx_filename) # Loads the model.
    if ComponentList is None:
        return None, message

    for Component in ComponentList:
        # Set it up in the ModelComponentList.
        editor.ModelComponentList[Component.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
        Component['skinsize'] = skinsize
        Component['show'] = chr(1)

    return ComponentList, message, bboxgroup


def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename and gamename is the full path to"
    "and name of the .mdx file selected."
    "For example:  C:\Kingpin\main\models\weapons\crowbar.mdx"

    global editor, progressbar, tobj, logging, importername, textlog, Strings
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
    ComponentList, message, bboxgroup = import_mdx_model(editor, filename)

    if ComponentList is None:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        quarkx.msgbox("Invalid .mdx model.\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        progressbar.close()
        return

    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        md2fileobj = quarkx.newfileobj("New model.md2")
        md2fileobj['FileName'] = 'New model.qkl'
        editor.Root.dictitems['Misc:mg'].appenditem(bboxgroup)
        for Component in ComponentList:
            editor.Root.appenditem(Component)
        md2fileobj['Root'] = editor.Root.name
        md2fileobj.appenditem(editor.Root)
        md2fileobj.openinnewwindow()
    else: # Imports a model properly from within the editor.
        undo = quarkx.action()
        undo.put(editor.Root.dictitems['Misc:mg'], bboxgroup)
        for Component in ComponentList:
            undo.put(editor.Root, Component)
            # This needs to be done for each component or bones will not work if used in the editor.
            quarkpy.mdlutils.make_tristodraw_dict(editor, Component)
            editor.Root.currentcomponent = Component
        compframes = editor.Root.currentcomponent.findallsubitems("", ':mf') # get all frames
        for compframe in compframes:
            compframe.compparent = editor.Root.currentcomponent # To allow frame relocation after editing.

        ie_utils.default_end_logging(filename, "IM", starttime) ### Use "EX" for exporter text, "IM" for importer text.

        if len(ComponentList) == 1:
            editor.ok(undo, Component.shortname + " created")
        else:
            editor.ok(undo, str(len(ComponentList)) + " components created")

        comp = editor.Root.currentcomponent
        skins = comp.findallsubitems("", ':sg')      # Gets the skin group.
        if len(skins[0].subitems) != 0:
            comp.currentskin = skins[0].subitems[0]      # To try and set to the correct skin.
            quarkpy.mdlutils.Update_Skin_View(editor, 2) # Sends the Skin-view for updating and center the texture in the view.
        else:
            comp.currentskin = None

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

    if message != "":
        message = message + "================================\r\n"
        message = message + "You need to find and supply the proper texture for the\r\n"
        message = message + "imported components, see missing textures above.\r\n"
        message = message + "It may be a texture in another model's folder.\r\n"
        message = message + "You can import it by selecting one of the component 'Skins' folder,\r\n"
        message = message + "open it's 'Specifics/Args' page and click on the 'import skin' icon button.\r\n"
        message = message + "Once imported copy that skin to all the other imported component 'Skins' folders."
        quarkx.textbox("WARNING", message, quarkpy.qutils.MT_WARNING)

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_mdx_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".mdx Kingpin Importer", ".mdx file", "*.mdx", loadmodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_mdx_import.py,v $
# Revision 1.9  2011/10/21 06:22:20  cdunde
# Correction for creating the tristodraw list for multiple components.
#
# Revision 1.8  2011/10/16 20:57:27  cdunde
# Updated importer for better skin texture file locating and loading.
#
# Revision 1.7  2011/09/29 22:35:39  cdunde
# Removed folder restriction call because not all model folders are in the models folder.
#
# Revision 1.6  2011/05/25 20:55:03  cdunde
# Revamped Bounding Box system for more flexibility with model formats that do not have bones, only single or multi components.
#
# Revision 1.5  2011/05/19 07:38:11  cdunde
# Fix, sometimes imported file read in skin size is incorrect.
#
# Revision 1.4  2011/05/19 06:47:54  cdunde
# To stop duplicate skin textures importing under another name.
#
# Revision 1.3  2011/05/19 01:35:16  cdunde
# Update to import model by folder and file name
# and add instructional message for missing textures.
#
# Revision 1.2  2011/05/16 00:10:06  cdunde
# Update by Daniel Pharos to import separate model sections as multi components.
#
# Revision 1.1  2011/05/15 18:15:48  danielpharos
# Started support for Kingpin MDX model format with animation and skin support. Credit for this goes to cdunde.
#
#
