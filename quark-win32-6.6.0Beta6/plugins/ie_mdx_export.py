# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor exporter for Kingpin .mdx model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_mdx_export.py,v 1.3 2013/02/20 05:19:41 cdunde Exp $


Info = {
   "plug-in":       "ie_mdx_exporter",
   "desc":          "Exports selected components to a Kingpin file (MDX). Original code from QuArK ie_fm_export.py file and other QuArK .py exporters.",
   "date":          "October 14 2011",
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
exportername = "ie_mdx_export.py"
textlog = "mdx_ie_log.txt"
progressbar = None
user_frame_list=[]
user_skins_list=[]
g_scale = 1.0


######################################################
# MDX Model Constants
######################################################
MDX_MAX_TRIANGLES=4096
MDX_MAX_VERTICES=2048
MDX_MAX_TEXCOORDS=2048
MDX_MAX_FRAMES=1024
MDX_MAX_SKINS=32
MDX_MAX_FRAMESIZE=(MDX_MAX_VERTICES * 4 + 128)

# The default animation frames list. (This info, from player model tutorial, found at http://kingpinforever.com/fredz/modelq2tokp.html)
                                                # frames
MDX_FRAME_NAME_LIST=(("tgun_rdy_",1,32),        #1  32  Standing with tommygun ready(all 2 handed weaps)
                    ("tgun_shoot_",1,5),        #2   5  Standing while shooting tommygun (as above)
                    ("tg_bird_",1,10),          #3  10  Taunt - Givin the Slim Shady :)
                    ("tg_crch_grab_",1,16),     #4  16  Taunt - Grabbing Crotch
                    ("tg_chin_flip_",1,15),     #5  15  Taunt - Flick Chin
                    ("1pstl_rdy_",1,23),        #6  23  Standing with one pistol ready
                    ("p_std_shoot_",1,4),       #7   4  Standing and shooting pistol
                    ("walk_gdown_",1,10),       #8  10  Walking with gun down
                    ("walk_tg_sht_", 1,10),     #9  10  Walking whilst shooting 2 handed weapons
                    ("run_tg_sht_",1,6),        #10  6  Running whilst shooting 2 handed weapons
                    ("rsd_tg_run_",1,6),        #11  6  Running right sidestep whilst shooting 2hw
                    ("lsd_tg_run_",1,6),        #12  6  Running left sidestep whilst shooting 2hw
                    ("p_walk_sht_",1,10),       #13 10  Walking whilst shooting pistol
                    ("p_run_shoot_",1,6),       #14  6  Running whilst shooting pistol
                    ("p_rside_run_",1,6),       #15  6  Running right sidestep whilst shooting pistol
                    ("p_lside_run_",1,6),       #16  6  Running left sidestep whilst shooting pistol
                    ("melee_rdy_",1,19),        #17 19  Standing with pipe ready
                    ("melee1_",1,7),            #18  7  Pipe attack sequence 1
                    ("melee2_",1,6),            #19  6  Pipe attack sequence 2
                    ("run_melee_",1,6),         #20  6  Running whilst attacking with pipe
                    ("run_guns_dn_",1,6),       #21  6  Running with gun down
                    ("jump_",1,7),              #22  7  Jump sequence
                    ("clmb_loop_",1,9),         #23  9  Climb sequence
                    ("death1_",1,19),           #24 19  Standing death sequence 1
                    ("death2_",1,16),           #25 16  Standing death sequence 2
                    ("death3_",1,28),           #26 28  Standing death sequence 3
                    ("death4_",1,13),           #27 13  Standing death sequence 4
                    ("tg_crch_rdy_",1,27),      #28 27  Crouching with tommygun ready
                    ("crouch_shoot_",1,6),      #29  6  Crouching whilst shooting  2 handed weapon
                    ("crouch_walk_",1,5),       #30  5  Crouching whilst moving
                    ("1p_crch_rdy_",1,18),      #31 18  Crouching with 1 pistol ready
                    ("p_crch_sht_",1,5),        #32  5  Crouching whilst shooting pistol
                    ("p_crch_walk_",1,6),       #33  6  Crouching and moving with pistol
                    ("crouch_death_",1,12))     #31 12  Crouching death sequence
                                                #  386  total number of frames

######################################################
# MDX data structures
######################################################
class mdx_alias_triangle: # See .md2 format doc "Vertices". A QuArK's "frame" ['Vertices'].
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

class mdx_face: # See .md2 format doc "Triangles". QuArK's "component.triangles".
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

class mdx_tex_coord: # See .md2 format doc "Texture coordinates". QuArK's "component.triangles".
    u=0
    v=0
    binary_format="<2h"
    def __init__(self):
        self.u=0
        self.v=0
    def save(self, file, st_coord):
        temp_data=[0]*2
        self.u=st_coord[0]
        self.v=st_coord[1]
    def dump (self):
        global tobj, logging
        tobj.logcon ("texture coordinate u, v: " + str(self.u) + ", " + str(self.v))
        tobj.logcon ("----------------------------------------")

class glGLCommands_t:
    TrisTypeNum=0
    SubObjectID=0
    cmd_list=[]
    binary_format="<2i" #little-endian (<), 2 ints

    def __init__(self):
        self.TrisTypeNum=0
        self.SubObjectID=0
        self.cmd_list=[]

    def save(self,file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # data[0] ex: (4) or (-7), positive int = a triangle strip, negative int = a triangle fan, 0 = end of valid GL_commands data.
        # data[1] ex: (3), positive int, the model component (section) this data applies to.
        data=struct.pack(self.binary_format, self.TrisTypeNum, self.SubObjectID)
        file.write(data)
        for cmd in self.cmd_list:
            cmd.save(file)
            progressbar.progress()
    def dump(self):
        global tobj, logging
        tobj.logcon ("-------------------")
        tobj.logcon ("MDX OpenGL Command Structure")
        tobj.logcon ("TrisTypeNum: " + str(self.TrisTypeNum))
        tobj.logcon ("SubObjectID: " + str(self.SubObjectID))
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
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # temp_data[0] and temp_data[1] ex: (0.1397, 0.6093), are 2D skin texture coords as floats, percentage of skin size.
        # temp_data[2] the face vertex index the s,t belong to.
        temp_data=[0]*3
        temp_data[0]=float(self.s)
        temp_data[1]=float(self.t)
        temp_data[2]=self.vert_index
        data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2])
        file.write(data)
        progressbar.progress()
    def dump (self):
        global tobj, logging
        tobj.logcon ("MDX OpenGL Command Vertex")
        tobj.logcon ("s: " + str(self.s))
        tobj.logcon ("t: " + str(self.t))
        tobj.logcon ("vertexIndex: " + str(self.vert_index))
        tobj.logcon ("")

class VertexInfo_t:
    # See http://web.archive.org/web/20020404103848/http://members.cheapnet.co.uk/~tical/misc/mdx.htm#VERTEXINFO
    # There is the vertex_info_list, which is made up of a series of numVertices int's,
    # all of which are grouped by the sub-object (component) they belong to.
    # If a vertex is in sub-object 1 then its marked as 1, if its in sub-object 2 then its marked as 2 etc etc.
    # First all the vertices from the first sub-object are marked then the rest of the vertices from other sub-objects follow.
    # For example if the first sub-object has 4 vertices and the second sub-object has 2 vertices the HEX code in the mdx would look like this:
    #     0100 0000 0100 0000 0100 0000 0100 0000 0200 0000 0200 0000
    # in the vertex_info_list it would look like this:
    #     (1,1,1,1,2,2)
    sub_obj_index=0
    binary_format="<i"
    def __init__(self):
        self.sub_obj_index=0
    def save(self, file):
        data=struct.pack(self.binary_format, self.sub_obj_index)
        file.write(data)
        progressbar.progress()
    def dump (self):
        global tobj, logging
        tobj.logcon ("VertexInfo sub_obj_index: " + str(self.sub_obj_index))
        tobj.logcon ("----------------------------------------")

class BBox_t:
    min=(0.,0.,0.)
    max=(0.,0.,0.)
    binary_format="<6f" #little-endian (<), 6 floats

    def __init__(self):
        self.min=(0.,0.,0.)
        self.max=(0.,0.,0.)
    def save(self,file):
        # file is the model file & full path, ex: C:\Kingpin\main\models\weapons\crowbar.mdx
        # temp_data[0] through temp_data[5] are coords as floats.
        temp_data=[0]*6
        temp_data[0]=self.min[0]
        temp_data[1]=self.min[1]
        temp_data[2]=self.min[2]
        temp_data[3]=self.max[0]
        temp_data[4]=self.max[1]
        temp_data[5]=self.max[2]
        data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4],temp_data[5])
        file.write(data)
        progressbar.progress()
    def dump (self):
        global tobj, logging
        tobj.logcon ("MDX BBox Frames Structure")
        tobj.logcon ("min: " + str(self.min))
        tobj.logcon ("max: " + str(self.max))
        tobj.logcon ("")

class mdx_skin: # See .md2 format doc "Texture information".
    name=""
    binary_format="<64s"
    def __init__(self):
        self.name=""
    def save(self, file):
        if not self.name.endswith(".tga"):
            fixname=self.name.split(".")[0]
            self.name=fixname + ".tga"
        data=struct.pack(self.binary_format, self.name)
        file.write(data)
    def dump (self):
        print "MDX Skin"
        print "skin name: ",self.name
        print ""

class mdx_alias_frame: # See .md2 format doc "Vector", "Vertices" and "Frames". QuArK's "component.dictitems['Frames']".
    scale=[]
    translate=[]
    name=[]
    vertices=[]
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

    def dump (self):
        global tobj, logging
        tobj.logcon ("scale x,y,z: " + str(self.scale[0]) + ", " + str(self.scale[1]) + ", " + str(self.scale[2]))
        tobj.logcon ("translate x,y,z: " + str(self.translate[0]) + ", " + str(self.translate[1]) + ", " + str(self.translate[2]))
        tobj.logcon ("name: " + self.name)
        tobj.logcon ("----------------------------------------")
        
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
    num_SfxDefines=0     #int 10   The number of sfx definitions, seem to always be zero
    num_SfxEntries=0     #int 11   The number of sfx entries, seem to always be zero
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
    num_tex_coords=0     #The number of texture coordinates, for QuArK's exporter use only.
    tex_coords=[]
    st_coord={}
    faces=[]
    frames=[]
    skins=[]
    GL_commands=[]
    facelist=[]
    vertex_info_list=[]
    bbox_frames=[]

    def __init__ (self):
        self.num_tex_coords=0
        self.tex_coords=[]
        self.st_coord={}
        self.faces=[]
        self.frames=[]
        self.skins=[]
        self.GL_commands=[]
        self.facelist=[]
        self.vertex_info_list=[]
        self.bbox_frames=[]

    def save(self, file):
        global tobj, logging
        #write the header data
        temp_data=[0]*23
        temp_data[0]=self.ident
        temp_data[1]=self.version
        temp_data[2]=int(self.skin_width)
        temp_data[3]=int(self.skin_height)
        temp_data[4]=self.frame_size
        temp_data[5]=self.num_skins
        temp_data[6]=self.num_vertices
        temp_data[7]=self.num_faces
        temp_data[8]=self.num_GL_commands
        temp_data[9]=self.num_frames
        temp_data[10]=self.num_SfxDefines
        temp_data[11]=self.num_SfxEntries
        temp_data[12]=self.num_SubObjects
        temp_data[13]=self.offset_skins
        temp_data[14]=self.offset_faces
        temp_data[15]=self.offset_frames
        temp_data[16]=self.offset_GL_commands
        temp_data[17]=self.offset_VertexInfo
        temp_data[18]=self.offset_SfxDefines
        temp_data[19]=self.offset_SfxEntries
        temp_data[20]=self.offset_BBoxFrames
        temp_data[21]=self.offset_DummyEnd
        temp_data[22]=self.offset_end
        data=struct.pack(self.binary_format, temp_data[0],temp_data[1],temp_data[2],temp_data[3],temp_data[4],temp_data[5],temp_data[6],temp_data[7],temp_data[8],temp_data[9],temp_data[10],temp_data[11],temp_data[12],temp_data[13],temp_data[14],temp_data[15],temp_data[16],temp_data[17],temp_data[18],temp_data[19],temp_data[20],temp_data[21],temp_data[22])
        file.write(data)

        #save the skin data
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: skin")
            tobj.logcon ("#####################################################################")
        for skin in self.skins:
            skin.save(file)

        #process the "st coord" (texture coordinates) data
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: st coord")
            tobj.logcon ("#####################################################################")
        for i in xrange(0, self.num_tex_coords):
            self.tex_coords[i].save(file, self.st_coord[i])
            progressbar.progress()
            if logging == 1:
                tobj.logcon ("mdx_tex_coord " + str(i))
                self.tex_coords[i].dump()

        #save the face data
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: face")
            tobj.logcon ("#####################################################################")
        count=-1
        for face in self.faces:
            face.save(file)
            progressbar.progress()
            if logging == 1:
                count+=1
                tobj.logcon ("mdx_face " + str(count))
                face.dump()

        #save the frames data
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: frames")
            tobj.logcon ("#####################################################################")
        count=-1
        for frame in self.frames:
            frame.save(file)
            if logging == 1:
                count+=1
                tobj.logcon ("mdx_alias_frame " + str(count))
                frame.dump()
                count2=-1
            for vert in frame.vertices:
                vert.save(file)
                if logging == 1:
                    count2+=1
                    tobj.logcon ("mdx_alias_triangle " + str(count2))
                    vert.dump()
            progressbar.progress()

        #save the GL command List data, see models.c BuildGlCmds for GL_commands list creation code.
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: GL_commands")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("START OF GLCMDS at, num_GL_commands: " + str(file.tell()) + ", " + str(self.num_GL_commands))
        for cmd in self.GL_commands:
            cmd.save(file)
            if logging == 1:
                cmd.dump()
            progressbar.progress()

        #save the VertexInfo data
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: VertexInfo")
            tobj.logcon ("#####################################################################")
        for i in xrange(0, self.num_vertices):
            self.vertex_info_list[i].save(file)
            if logging == 1:
                self.vertex_info_list[i].dump()
            progressbar.progress()

        #save the BBoxFrames data
        if logging == 1:
            tobj.logcon ("")
            tobj.logcon ("#####################################################################")
            tobj.logcon ("SectionName: BBoxFrames")
            tobj.logcon ("#####################################################################")
        for i in xrange(0, len(self.bbox_frames)):
            self.bbox_frames[i].save(file)
            if logging == 1:
                self.bbox_frames[i].dump()
            progressbar.progress()

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
# Fill MDX data structure
######################################################
def fill_mdx(mdx, component):
    global user_frame_list, user_skins_list, progressbar, tobj, Strings
    
    mdx.num_SubObjects=len(component)

    # Header information data.
    mdx.ident = 1481655369   # Must be this number.
    mdx.version = 4          # Must be this number.

    # Get the skin information.
    user_skins_list = component[0].dictitems['Skins:sg']
    try:
        if str(component[0].dictspec['skinsize']) != str(user_skins_list.subitems[0].dictspec['Size']):
            component[0]['skinsize'] = user_skins_list.subitems[0].dictspec['Size']
        size = component[0].dictspec['skinsize']
        mdx.skin_width = size[0]
        mdx.skin_height = size[1]
    except:
        size = user_skins_list.subitems[0].dictspec['Size']
        mdx.skin_width = size[0]
        mdx.skin_height = size[1]
    mdx.num_skins = 1
    #add a skin node to the mdx data structure
    mdx.skins.append(mdx_skin())
    name = user_skins_list.subitems[0].name
    if name.find("skin_head") != -1 or name.find("skin_upper") != -1 or name.find("skin_lower") != -1:
        name = name.rsplit("_", 1)[0] + ".tga"
    mdx.skins[0].name = name

    mdx.num_frames = len(component[0].dictitems['Frames:fg'].dictitems) # Number of frames in the Frames group, 'Frames:fg'.

    #load up some intermediate data structures
    tex_list={}
    tex_count=0
    face_count=0
    vertices_count=0

    # Setup our progressbar
    for i in xrange(0, mdx.num_SubObjects):
        mdx.num_faces = mdx.num_faces + len(component[i].triangles) # Number of triangles.
        mdx.num_vertices = mdx.num_vertices + len(component[i].dictitems['Frames:fg'].subitems[0].dictspec['Vertices'])/3
    progressbar = quarkx.progressbar(2455, (mdx.num_faces+mdx.num_vertices)*6)

    for i in xrange(0, mdx.num_SubObjects):

        # Get the current (i) component Mesh.
        mesh = component[i].triangles
        user_frame_list = component[i].dictitems['Frames:fg']

        comp_num_of_vertices = len(user_frame_list.dictitems[user_frame_list.subitems[0].name].dictspec['Vertices'])/3 # Number of vertices per frame.
        comp_num_of_faces = len(mesh)

        #build the VertexInfo list
        for j in xrange(0, comp_num_of_vertices):
            #add a VertexInfo_t
            mdx.vertex_info_list.append(VertexInfo_t())
            mdx.vertex_info_list[j].sub_obj_index=i # Identifies which vertexes belong to which component (SubObject).
            progressbar.progress()

        # Put texture information in the mdx structure.
        # Build UV coords dictionary (prevents double entries-saves space).
        for face in range(0, len(mesh)):
            mdx.faces.append(mdx_face())
            for j in range(0, len(mesh[face])):
                # A list of sub-lists of the u, v coords. Each vert has its own UV coords.
                mdx.tex_coords.append(mdx_tex_coord())
                t=(mesh[face][j][1], mesh[face][j][2])
                tex_key=(t[0],t[1])
                mdx.faces[face+face_count].vertex_index[j] = mesh[face][j][0] + vertices_count
                mdx.tex_coords[(face*3)+j].u = mesh[face][j][1] # tex_coords is screwed up here.
                mdx.tex_coords[(face*3)+j].v = mesh[face][j][2] # tex_coords is screwed up here.
                if logging == 1:
                    mdx.facelist = mdx.facelist + [(mesh[face][j][0] + vertices_count, mesh[face][j][1], mesh[face][j][2])]
                if not tex_list.has_key(tex_key):
                    tex_list[tex_key] = tex_count
                    mdx.st_coord[tex_count] = tex_key
                    tex_count+=1
                mdx.faces[face+face_count].texture_index[j] = tex_list[tex_key]
            progressbar.progress()

        #get the frame list
        user_frame_list = component[i].dictitems['Frames:fg']

        #fill in each frame with frame info and all the vertex data for that frame
        #fill in each bbox_frame with the min and max data for that bbox_frame
        for frame in range(0, mdx.num_frames):
            if i == 0:
                #add a frame
                mdx.frames.append(mdx_alias_frame())
            #add a bbox_frame
            mdx.bbox_frames.append(BBox_t())
            
            # Each frame has a scale and transform value that gets the vertex value between 0-255.
            # Since the scale and transform are the same for all the verts in the frame,
            # we only need to figure this out once per frame

            #we need to start with the bounding box
            vertices = []
            framename = component[0].dictitems['Frames:fg'].subitems[frame].name
            frameVertices = user_frame_list.dictitems[framename].dictspec['Vertices']
            for vert_counter in range(0, comp_num_of_vertices):
                x= frameVertices[(vert_counter*3)]
                y= frameVertices[(vert_counter*3)+1]
                z= frameVertices[(vert_counter*3)+2]
                vertices = vertices + [quarkx.vect(x, y, z)]
            bounding_box = quarkx.boundingboxof(vertices) # Uses the component's frame.vertices

            #fill in the bbox_frame data WE REALLY NEED THE MAX AND MIN OF THE ABOVE x,y,z VALUES FOR A PROPPER BBOX SHAPE.
            mdx.bbox_frames[frame+i].min = bounding_box[0].tuple
            mdx.bbox_frames[frame+i].max = bounding_box[1].tuple

            #the scale is the difference between the min and max OF ALL SubObjects COMBINED (on that axis) / 255
            #we need to start with the bounding box OF ALL SubObjects COMBINED
            vertices = []
            for j in xrange(0, mdx.num_SubObjects):
                CompVertices = component[j].dictitems['Frames:fg'].dictitems[framename].dictspec['Vertices']
                for vert_counter in range(0, len(CompVertices)/3):
                    x= CompVertices[(vert_counter*3)]
                    y= CompVertices[(vert_counter*3)+1]
                    z= CompVertices[(vert_counter*3)+2]
                    vertices = vertices + [quarkx.vect(x, y, z)]
            bounding_box = quarkx.boundingboxof(vertices) # Uses the COMBINED component's frame.vertices

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
            if i == 0:
                mdx.frames[frame].scale = scale
                mdx.frames[frame].translate = translate

            # Now for the frame vertices.
            for vert_counter in range(0, comp_num_of_vertices):
                # Add a vertex to the mdx structure.
                mdx.frames[frame].vertices.append(mdx_alias_triangle())

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
                mdx.frames[frame].vertices[vert_counter+vertices_count].vertices = (new_x, new_y, new_z)

                # We need to add the lookup table check here.
                mdx.frames[frame].vertices[vert_counter+vertices_count].lightnormalindex = 0

            # Output all the frame names in the user_frame_list.
            mdx.frames[frame].name = framename.split(":")[0]

        vertices_count = vertices_count + comp_num_of_vertices
        face_count = face_count + comp_num_of_faces

    mdx.num_tex_coords = len(tex_list) # Number of non-duplicated UV coords in Skin-view.

    #compute GL commands
    mdx.num_GL_commands=build_GL_commands(mdx, component)

    #get the frame data
    #calculate 1 frame size  + (1 vert size*num_verts)
    mdx.frame_size=40+(4*mdx.num_vertices) #in bytes

    # Compute these after everthing is loaded into a mdx structure.
    header_size = 23 * 4 # 23 integers, each integer is 4 bytes.
    skin_size = 64 * mdx.num_skins # 64 char per skin * number of skins.
    face_size = 12 * mdx.num_faces # 3 shorts for vertex index, 3 shorts for tex index.
    vertex_info_size = 4 * mdx.num_vertices # 1 int, gives component (SubObject) number a vertex belongs to.
    frames_size = ((12+12+16) + (4 * mdx.num_vertices)) * mdx.num_frames # (Frame info + num_vertices per frame) * num_frames.
    GL_command_size = mdx.num_GL_commands * 4 # Each is an integer or float, so 4 bytes per.
    bbox_frames_size = (6 * 4) * mdx.num_frames * mdx.num_SubObjects # 6 floats per BBox * num_frames * num_SubObjects.

    mdx.offset_skins=header_size
    mdx.offset_faces=mdx.offset_skins + skin_size
    mdx.offset_frames=mdx.offset_faces + face_size
    mdx.offset_GL_commands=mdx.offset_frames + frames_size
    mdx.offset_VertexInfo=mdx.offset_GL_commands + GL_command_size
    mdx.offset_SfxDefines=mdx.offset_VertexInfo + vertex_info_size
    mdx.offset_SfxEntries=mdx.offset_SfxDefines
    mdx.offset_BBoxFrames=mdx.offset_SfxEntries
    mdx.offset_DummyEnd=mdx.offset_BBoxFrames + bbox_frames_size
    mdx.offset_end=mdx.offset_DummyEnd

######################################################
# Tri-Strip/Tri-Fan functions
######################################################
def find_strip_length(mdx, start_tri, start_vert, num_faces, face_count):
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

    strip_vert[0]=mdx.faces[last+face_count].vertex_index[start_vert%3]
    strip_vert[1]=mdx.faces[last+face_count].vertex_index[(start_vert+1)%3]
    strip_vert[2]=mdx.faces[last+face_count].vertex_index[(start_vert+2)%3]

    strip_st[0]=mdx.faces[last+face_count].texture_index[start_vert%3]
    strip_st[1]=mdx.faces[last+face_count].texture_index[(start_vert+1)%3]
    strip_st[2]=mdx.faces[last+face_count].texture_index[(start_vert+2)%3]

    strip_tris[0]=start_tri
    strip_count=1

    m1=mdx.faces[last+face_count].vertex_index[(start_vert+2)%3]
    st1=mdx.faces[last+face_count].texture_index[(start_vert+2)%3]
    m2=mdx.faces[last+face_count].vertex_index[(start_vert+1)%3]
    st2=mdx.faces[last+face_count].texture_index[(start_vert+1)%3]

    #look for matching triangle
    check=start_tri+1

    for tri_counter in range(start_tri+1, num_faces):

        for k in range(0,3):
            if mdx.faces[check+face_count].vertex_index[k]!=m1:
                continue
            if mdx.faces[check+face_count].texture_index[k]!=st1:
                continue
            if mdx.faces[check+face_count].vertex_index[(k+1)%3]!=m2:
                continue
            if mdx.faces[check+face_count].texture_index[(k+1)%3]!=st2:
                continue

            #if we can't use this triangle, this tri_strip is done
            if (used[tri_counter]!=0):
                for clear_counter in range(start_tri+1, num_faces):
                    if used[clear_counter]==2:
                        used[clear_counter]=0
                return strip_count

            #new edge
            if (strip_count & 1):
                m2=mdx.faces[check+face_count].vertex_index[(k+2)%3]
                st2=mdx.faces[check+face_count].texture_index[(k+2)%3]
            else:
                m1=mdx.faces[check+face_count].vertex_index[(k+2)%3]
                st1=mdx.faces[check+face_count].texture_index[(k+2)%3]

            strip_vert[strip_count+2]=mdx.faces[tri_counter+face_count].vertex_index[(k+2)%3]
            strip_st[strip_count+2]=mdx.faces[tri_counter+face_count].texture_index[(k+2)%3]
            strip_tris[strip_count]=tri_counter
            strip_count+=1

            used[tri_counter]=2
        check+=1
    return strip_count

def find_fan_length(mdx, start_tri, start_vert, num_faces, face_count):
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

    strip_vert[0]=mdx.faces[last+face_count].vertex_index[start_vert%3]
    strip_vert[1]=mdx.faces[last+face_count].vertex_index[(start_vert+1)%3]
    strip_vert[2]=mdx.faces[last+face_count].vertex_index[(start_vert+2)%3]

    strip_st[0]=mdx.faces[last+face_count].texture_index[start_vert%3]
    strip_st[1]=mdx.faces[last+face_count].texture_index[(start_vert+1)%3]
    strip_st[2]=mdx.faces[last+face_count].texture_index[(start_vert+2)%3]

    strip_tris[0]=start_tri
    strip_count=1

    m1=mdx.faces[last+face_count].vertex_index[(start_vert+0)%3]
    st1=mdx.faces[last+face_count].texture_index[(start_vert+0)%3]
    m2=mdx.faces[last+face_count].vertex_index[(start_vert+2)%3]
    st2=mdx.faces[last+face_count].texture_index[(start_vert+2)%3]

    #look for matching triangle    
    check=start_tri+1
    for tri_counter in range(start_tri+1, num_faces):
        for k in range(0,3):
            if mdx.faces[check+face_count].vertex_index[k]!=m1:
                continue
            if mdx.faces[check+face_count].texture_index[k]!=st1:
                continue
            if mdx.faces[check+face_count].vertex_index[(k+1)%3]!=m2:
                continue
            if mdx.faces[check+face_count].texture_index[(k+1)%3]!=st2:
                continue

            #if we can't use this triangle, this tri_strip is done
            if (used[tri_counter]!=0):
                for clear_counter in range(start_tri+1, num_faces):
                    if used[clear_counter]==2:
                        used[clear_counter]=0
                return strip_count

            #new edge
            m2=mdx.faces[check+face_count].vertex_index[(k+2)%3]
            st2=mdx.faces[check+face_count].texture_index[(k+2)%3]

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
def build_GL_commands(mdx, component):
    #variables
    num_commands=0
    face_count=0
    for i in xrange(0, mdx.num_SubObjects):
        num_faces=len(component[i].triangles)
        #variables shared between fan and strip functions
        global used
        used=[0]*num_faces
        global strip_vert
        strip_vert=[0]*128
        global strip_st
        strip_st=[0]*128
        global strip_tris
        strip_tris=[0]*128
        global strip_count
        strip_count=0

        #variables
        start_vert=0
        fan_length=strip_length=0
        length=best_length=0
        best_type=0
        best_vert=[0]*1024
        best_st=[0]*1024
        best_tris=[0]*1024
        s=0.0
        t=0.0

        for face_counter in range(0, num_faces):
            if used[face_counter]==1: #don't evaluate a tri that's been used
                pass
            else:
                best_length=0 #restart the counter
                #for each vertex index in this face
                for start_vert in range(0,3):
                    strip_length=find_strip_length(mdx, face_counter, start_vert, num_faces, face_count)
                    if (strip_length>best_length): 
                        best_type=0
                        best_length=strip_length
                        for index in range (0, best_length+2):
                            best_st[index]=strip_st[index]
                            best_vert[index]=strip_vert[index]
                        for index in range(0, best_length):
                            best_tris[index]=strip_tris[index]

                    fan_length=find_fan_length(mdx, face_counter, start_vert, num_faces, face_count)
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
                temp_cmdlist.SubObjectID=i # SEND COMP NBR TO SET THIS WITH
                num_commands+=1 # ups count for SubOjectID's int value
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
                #    s=mdx.tex_coords[index].u # tex_coords is screwed up here.
                #    t=mdx.tex_coords[index].v # tex_coords is screwed up here.
                    s=mdx.st_coord[index][0]
                    t=mdx.st_coord[index][1]
                    try:
                        s=(s+0.5)/mdx.skin_width
                        t=(t+0.5)/mdx.skin_height
                    except:
                        s=(s+0.5)/1
                        t=(t+0.5)/1
                    cmd.s=s
                    cmd.t=t
                    cmd.vert_index=best_vert[command_counter]
                    temp_cmdlist.cmd_list.append(cmd)
                    num_commands+=3
                mdx.GL_commands.append(temp_cmdlist)
        face_count = face_count + num_faces

    #end of list
    temp_cmdlist=glGLCommands_t()
    temp_cmdlist.TrisTypeNum=0
    mdx.GL_commands.append(temp_cmdlist)  
    num_commands+=2

    #cleanup and return
    used=best_vert=best_st=best_tris=strip_vert=strip_st=strip_tris=0
    return num_commands

######################################################
# Save MDX Format
######################################################
def save_mdx(filename):
    global editor, tobj, logging, exportername, textlog, Strings
    editor = quarkpy.mdleditor.mdleditor
    if editor is None:
        return
    # "objects" is a list of one or more selected model components for exporting.
    objects = editor.layout.explorer.sellist

    if not objects:
        quarkx.msgbox("No Components have been selected for exporting.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
        return
    for i in range(len(objects)):
        object = objects[i]
        if not object.name.endswith(":mc"):
            quarkx.msgbox("Improper Selection !\n\nYou can ONLY select component folders for exporting.\n\nAn item that is not a component folder\nis in your selections.\n\nDeselect it and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if not object.dictitems['Frames:fg'] or len(object.dictitems['Frames:fg'].subitems) == 0:
            quarkx.msgbox("No frames exist for " + object.shortname + ".\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if not object.dictitems['Skins:sg'] or len(object.dictitems['Skins:sg'].subitems) == 0:
            quarkx.msgbox("No skin exist for " + object.shortname + ".\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if i == 0:
            frame_count = len(object.dictitems['Frames:fg'].subitems)
            name = object.dictitems['Skins:sg'].subitems[0].name
            if not name.startswith("models") and not name.startswith("/models") and not name.startswith("\\models") and not name.startswith("textures") and not name.startswith("/textures") and not name.startswith("//textures"):
                quarkx.msgbox("Skin name for " + object.shortname + "\ndoes not start with either models/ or textures/ folder name.\n\nThe first skin name of each component must start\nwith the name of the upper folder the skin is in. Correct and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
                return
            skin_size = object.dictitems['Skins:sg'].subitems[0].dictspec['Size']
        object_skin_size = object.dictitems['Skins:sg'].subitems[0].dictspec['Size']
        if int(object_skin_size[0]) != int(skin_size[0]) or int(object_skin_size[1]) != int(skin_size[1]) or object.dictitems['Skins:sg'].subitems[0].name != name:
            quarkx.msgbox("Component skins are not the same.\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if len(object.dictitems['Frames:fg'].subitems[0].dictspec['Vertices']) == 0:
            quarkx.msgbox("Nothing exist for " + object.shortname + ".\nCan not create model.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return
        if len(object.dictitems['Frames:fg'].subitems) != frame_count:
            quarkx.msgbox("Number of frames of selected components do not match.\nMatch the frames for each component and try again.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
            return

    logging, tobj, starttime = ie_utils.default_start_logging(exportername, textlog, filename, "EX") ### Use "EX" for exporter text, "IM" for importer text.

    mdx = mdx_obj()  #blank mdx object to save

    fill_mdx(mdx, objects)# To build and fill the values for the file header.

    #actually write it to disk
    file = open(filename,"wb")
    mdx.save(file)
    if logging == 1:
        mdx.dump() # Writes the file Header last to the log for comparison reasons.
    file.close()
    progressbar.close()

    #cleanup
    mdx = 0

    add_to_message = "Any used skin textures that are not a .tga\nwill need to be created to go with the model"
    ie_utils.default_end_logging(filename, "EX", starttime, add_to_message) ### Use "EX" for exporter text, "IM" for importer text.

# Saves the model file: root is the actual file,
# filename is the full path and name of the .mdx file to create.
# For example:  C:\Kingpin\main\models\weapons\crowbar.mdx
# gamename is None.
def savemodel(root, filename, gamename, nomessage=0):
    save_mdx(filename)

### To register this Python plugin and put it on the exporters menu.
import quarkpy.qmdlbase
quarkpy.qmdlbase.RegisterMdlExporter(".mdx Kingpin Exporter", ".mdx file", "*.mdx", savemodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_mdx_export.py,v $
# Revision 1.3  2013/02/20 05:19:41  cdunde
# Fix for sometimes incorrect skinsize being used.
#
# Revision 1.2  2011/10/21 06:23:26  cdunde
# Final update to handle multiple component models.
#
# Revision 1.1  2011/10/16 20:57:11  cdunde
# Added export support for Kingpin static and animation models .mdx file type.
#
#