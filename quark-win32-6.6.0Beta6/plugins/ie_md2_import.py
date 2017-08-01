# Two lines below to stop encoding errors in the console.
#!/usr/bin/python
# -*- coding: ascii -*-

"""   QuArK  -  Quake Army Knife

QuArK Model Editor importer for Quake 2 .md2 model files.
"""
#
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/ie_md2_import.py,v 1.15 2012/12/25 06:01:57 cdunde Exp $


Info = {
   "plug-in":       "ie_md2_importer",
   "desc":          "This script imports a Quake 2 file (MD2), textures, and animations into QuArK for editing. Original code from Blender, md2_import.py, author - Bob Holcomb.",
   "date":          "June 3 2008",
   "author":        "cdunde & DanielPharos",
   "author e-mail": "cdunde@sbcglobal.net",
   "quark":         "Version 6.6.0 Beta 2" }

import struct, sys, os, time, operator
import quarkx
from types import *
import ie_utils
from ie_utils import tobj
from quarkpy.qdictionnary import Strings

# Globals
logging = 0
importername = "ie_md2_import.py"
textlog = "md2_ie_log.txt"
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
# MD2 Model Constants
######################################################
MD2_MAX_TRIANGLES=4096
MD2_MAX_VERTICES=2048
MD2_MAX_TEXCOORDS=2048
MD2_MAX_FRAMES=512
MD2_MAX_SKINS=32
MD2_MAX_FRAMESIZE=(MD2_MAX_VERTICES * 4 + 128)

######################################################
# MD2 data structures
######################################################
class md2_alias_triangle:
    vertices=[]
    lightnormalindex=0

    binary_format="<3BB" #little-endian (<), 3 Unsigned char
    
    def __init__(self):
        self.vertices=[0]*3
        self.lightnormalindex=0

    def load(self, file):
        # file is the model file & full path, ex: C:\Quake2\baseq2\models\chastity\tris.md2
        # data[0] through data[3] ex: (178, 143, 180, 63), 3 texture coords and normal (normal not needed).
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)
        self.vertices[0]=data[0]
        self.vertices[1]=data[1]
        self.vertices[2]=data[2]
        self.lightnormalindex=data[3]
        return self

    def dump(self):
        print "MD2 Alias_Triangle Structure"
        print "vertex: ", self.vertices[0]
        print "vertex: ", self.vertices[1]
        print "vertex: ", self.vertices[2]
        print "lightnormalindex: ",self.lightnormalindex
        print ""

class md2_face:
    vertex_index=[]
    texture_index=[]

    binary_format="<3h3h" #little-endian (<), 3 short, 3 short
    
    def __init__(self):
        self.vertex_index = [ 0, 0, 0 ]
        self.texture_index = [ 0, 0, 0]

    def load (self, file):
        # file is the model file & full path, ex: C:\Quake2\baseq2\models\chastity\tris.md2
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
        print "MD2 Face Structure"
        print "vertex index: ", self.vertex_index[0]
        print "vertex index: ", self.vertex_index[1]
        print "vertex index: ", self.vertex_index[2]
        print "texture index: ", self.texture_index[0]
        print "texture index: ", self.texture_index[1]
        print "texture index: ", self.texture_index[2]
        print ""

class md2_tex_coord:
    u=0
    v=0

    binary_format="<2h" #little-endian (<), 2 unsigned short

    def __init__(self):
        self.u=0
        self.v=0

    def load (self, file):
        # file is the model file & full path, ex: C:\Quake2\baseq2\models\chastity\tris.md2
        # data[0] and data[1] ex: (169, 213), are 2D skin texture coords as integers.
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.u=data[0]
        self.v=data[1]
        return self

    def dump (self):
        print "MD2 Texture Coordinate Structure"
        print "texture coordinate u: ",self.u
        print "texture coordinate v: ",self.v
        print ""


class md2_skin:
    name=""

    binary_format="<64s" #little-endian (<), char[64]

    def __init__(self):
        self.name=""

    def load (self, file):
        # file is the model file & full path, ex: C:\Quake2\baseq2\models\chastity\tris.md2
        # self.name is just the skin texture path and name, ex: models/chastity/anarchy.pcx
        temp_data=file.read(struct.calcsize(self.binary_format))
        data=struct.unpack(self.binary_format, temp_data)
        self.name=asciiz(data[0])
        return self

    def dump (self):
        print "MD2 Skin"
        print "skin name: ",self.name
        print ""

class md2_alias_frame:
    scale=[]
    translate=[]
    name=[]
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
        # file is the model file & full path, ex: C:\Quake2\baseq2\models\chastity\tris.md2
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
        self.name=asciiz(data[6])
        return self

    def dump (self):
        print "MD2 Alias Frame"
        print "scale x: ",self.scale[0]
        print "scale y: ",self.scale[1]
        print "scale z: ",self.scale[2]
        print "translate x: ",self.translate[0]
        print "translate y: ",self.translate[1]
        print "translate z: ",self.translate[2]
        print "name: ",self.name
        print ""

class md2_obj:
    #Header Structure
    ident=0              #int  0   This is used to identify the file
    version=0            #int  1   The version number of the file (Must be 8)
    skin_width=0         #int  2   The skin width in pixels
    skin_height=0        #int  3   The skin height in pixels
    frame_size=0         #int  4   The size in bytes the frames are
    num_skins=0          #int  5   The number of skins associated with the model
    num_vertices=0       #int  6   The number of vertices (constant for each frame)
    num_tex_coords=0     #int  7   The number of texture coordinates
    num_faces=0          #int  8   The number of faces (polygons)
    num_GL_commands=0    #int  9   The number of gl commands
    num_frames=0         #int 10   The number of animation frames
    offset_skins=0       #int 11   The offset in the file for the skin data
    offset_tex_coords=0  #int 12   The offset in the file for the texture data
    offset_faces=0       #int 13   The offset in the file for the face data
    offset_frames=0      #int 14   The offset in the file for the frames data
    offset_GL_commands=0 #int 15   The offset in the file for the gl commands data
    offset_end=0         #int 16   The end of the file offset

    binary_format="<17i"  #little-endian (<), 17 integers (17i)

    #md2 data objects
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
        # file is the model file & full path, ex: C:\Quake2\baseq2\models\chastity\tris.md2
        # data is all of the header data amounts.
        temp_data = file.read(struct.calcsize(self.binary_format))
        data = struct.unpack(self.binary_format, temp_data)

        self.ident=data[0]
        self.version=data[1]

        if (self.ident!=844121161 or self.version!=8): # Not a valid MD2 file.
            return None

        self.skin_width=data[2]
        self.skin_height=data[3]
        self.frame_size=data[4]

        #make the # of skin objects for model
        self.num_skins=data[5]
        for i in xrange(0,self.num_skins):
            self.skins.append(md2_skin())

        self.num_vertices=data[6]

        #make the # of texture coordinates for model
        self.num_tex_coords=data[7]
        for i in xrange(0,self.num_tex_coords):
            self.tex_coords.append(md2_tex_coord())

        #make the # of triangle faces for model
        self.num_faces=data[8]
        for i in xrange(0,self.num_faces):
            self.faces.append(md2_face())

        self.num_GL_commands=data[9]

        #make the # of frames for the model
        self.num_frames=data[10]
        for i in xrange(0,self.num_frames):
            self.frames.append(md2_alias_frame())
            #make the # of vertices for each frame
            for j in xrange(0,self.num_vertices):
                self.frames[i].vertices.append(md2_alias_triangle())

        self.offset_skins=data[11]
        self.offset_tex_coords=data[12]
        self.offset_faces=data[13]
        self.offset_frames=data[14]
        self.offset_GL_commands=data[15]
        self.offset_end=data[16]

        #load the skin info
        file.seek(self.offset_skins,0)
        for i in xrange(0, self.num_skins):
            self.skins[i].load(file)
            #self.skins[i].dump()

        #load the texture coordinates
        file.seek(self.offset_tex_coords,0)
        for i in xrange(0, self.num_tex_coords):
            self.tex_coords[i].load(file)
            #self.tex_coords[i].dump()

        #load the face info
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
        return self

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
            tobj.logcon ("number of texture coordinates: " + str(self.num_tex_coords))
            tobj.logcon ("number of faces: " + str(self.num_faces))
            tobj.logcon ("number of GL commands: " + str(self.num_GL_commands))
            tobj.logcon ("number of frames: " + str(self.num_frames))
            tobj.logcon ("offset skins: " + str(self.offset_skins))
            tobj.logcon ("offset texture coordinates: " + str(self.offset_tex_coords))
            tobj.logcon ("offset faces: " + str(self.offset_faces))
            tobj.logcon ("offset frames: " + str(self.offset_frames))
            tobj.logcon ("offset GL Commands: " + str(self.offset_GL_commands))
            tobj.logcon ("offset end: " + str(self.offset_end))
            tobj.logcon ("")

######################################################
# Import functions
######################################################
def load_textures(md2):
    global tobj, logging
    # Checks if the model has textures specified with it.
    skinsize = (256, 256)
    skingroup = quarkx.newobj('Skins:sg')
    skingroup['type'] = chr(2)
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Skins group data: " + str(md2.num_skins) + " skins")
        tobj.logcon ("#####################################################################")
    if int(md2.num_skins) > 0:
        for i in xrange(0,md2.num_skins):
            if logging == 1:
                tobj.logcon (md2.skins[i].name)
            skinname = md2.skins[i].name.split('/')
            skin = quarkx.newobj(md2.skins[i].name)
            try:
                image = quarkx.openfileobj(os.getcwd() + "\\" + skinname[len(skinname)-1])
                skin['Image1'] = image.dictspec['Image1']
            except:
                try:
                    skinsize = (md2.skin_width, md2.skin_height) # Used for QuArK.
                    continue
                except:
                    continue
            try:
                skin['Pal'] = image.dictspec['Pal']
            except:
                pass
            skin['Size'] = image.dictspec['Size']
            skingroup.appenditem(skin)
            skinsize = (md2.skin_width, md2.skin_height) # Used for QuArK.
            # Only writes to the console here.
          #  md2.skins[i].dump() # Comment out later, just prints to the console what the skin(s) are.

        return skinsize, skingroup # Used for QuArK.
    else:
        return skinsize, skingroup # Used for QuArK.
	

def animate_md2(md2): # The Frames Group is made here & returned to be added to the Component.
    global progressbar, tobj, logging
	######### Animate the verts through the QuArK Frames lists.
    framesgroup = quarkx.newobj('Frames:fg')

    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Frame group data: " + str(md2.num_frames) + " frames")
        tobj.logcon ("frame: frame name")
        tobj.logcon ("#####################################################################")

    for i in xrange(0, md2.num_frames):
        ### md2.frames[i].name is the frame name, ex: attack1
        if logging == 1:
            tobj.logcon (str(i) + ": " + md2.frames[i].name)

        frame = quarkx.newobj(md2.frames[i].name + ':mf')
        mesh = ()
        #update the vertices
        for j in xrange(0,md2.num_vertices):
            x=(md2.frames[i].scale[0]*md2.frames[i].vertices[j].vertices[0]+md2.frames[i].translate[0])*g_scale
            y=(md2.frames[i].scale[1]*md2.frames[i].vertices[j].vertices[1]+md2.frames[i].translate[1])*g_scale
            z=(md2.frames[i].scale[2]*md2.frames[i].vertices[j].vertices[2]+md2.frames[i].translate[2])*g_scale

            #put the vertex in the right spot
            mesh = mesh + (x,)
            mesh = mesh + (y,)
            mesh = mesh + (z,)

        frame['Vertices'] = mesh
        framesgroup.appenditem(frame)
        progressbar.progress()
    return framesgroup


def load_md2(md2_filename, name):
    global progressbar, tobj, logging, Strings
    #read the file in
    file=open(md2_filename,"rb")
    md2=md2_obj()
    MODEL = md2.load(file)

    file.close()
    if MODEL is None:
        return None, None, None, None

    Strings[2454] = name + "\n" + Strings[2454]
    progressbar = quarkx.progressbar(2454, md2.num_faces + (md2.num_frames * 2))
    skinsize, skingroup = load_textures(md2) # Calls here to make the Skins Group.

    ######### Make the faces for QuArK, the 'component.triangles', which is also the 'Tris'.
    if logging == 1:
        tobj.logcon ("")
        tobj.logcon ("#####################################################################")
        tobj.logcon ("Face group data: " + str(md2.num_faces) + " faces")
        tobj.logcon ("face: (vert_index, U, V)")
        tobj.logcon ("#####################################################################")

    Tris = ''
    for i in xrange(0, md2.num_faces):
        if logging == 1:
            facelist = []
            facelist = facelist + [(md2.faces[i].vertex_index[0], md2.tex_coords[md2.faces[i].texture_index[0]].u, md2.tex_coords[md2.faces[i].texture_index[0]].v)]
            facelist = facelist + [(md2.faces[i].vertex_index[1], md2.tex_coords[md2.faces[i].texture_index[1]].u, md2.tex_coords[md2.faces[i].texture_index[1]].v)]
            facelist = facelist + [(md2.faces[i].vertex_index[2], md2.tex_coords[md2.faces[i].texture_index[2]].u, md2.tex_coords[md2.faces[i].texture_index[2]].v)]
            tobj.logcon (str(i) + ": " + str(facelist))
        Tris = Tris + struct.pack("Hhh", md2.faces[i].vertex_index[0], md2.tex_coords[md2.faces[i].texture_index[0]].u, md2.tex_coords[md2.faces[i].texture_index[0]].v)
        Tris = Tris + struct.pack("Hhh", md2.faces[i].vertex_index[1], md2.tex_coords[md2.faces[i].texture_index[1]].u, md2.tex_coords[md2.faces[i].texture_index[1]].v)
        Tris = Tris + struct.pack("Hhh", md2.faces[i].vertex_index[2], md2.tex_coords[md2.faces[i].texture_index[2]].u, md2.tex_coords[md2.faces[i].texture_index[2]].v)
        progressbar.progress()

    framesgroup = animate_md2(md2) # Calls here to make the Frames Group.

    if logging == 1:
        md2.dump() # Writes the file Header last to the log for comparison reasons.

    return Tris, skinsize, skingroup, framesgroup


########################
# To run this file
########################

def import_md2_model(editor, md2_filename):


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

    Tris, skinsize, skingroup, framesgroup = load_md2(md2_filename, name) # Loads the model.
    if Tris is None:
        return None, None

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

    ### Use the 'ModelRoot' below to test opening the QuArK's Model Editor with, needs to be qualified with main menu item.
    ModelRoot = quarkx.newobj('Model:mr')
  #  ModelRoot.appenditem(Component)

    return ModelRoot, Component


def loadmodel(root, filename, gamename, nomessage=0):
    "Loads the model file: root is the actual file,"
    "filename and gamename is the full path to"
    "and name of the .md2 file selected."
    "For example:  C:\Quake2\baseq2\models\monkey\tris.md2"

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

    ### First we test for a valid (proper) model path.
    basepath = ie_utils.validpath(filename)
    if basepath is None:
        return

    logging, tobj, starttime = ie_utils.default_start_logging(importername, textlog, filename, "IM") ### Use "EX" for exporter text, "IM" for importer text.

    ### Lines below here loads the model into the opened editor's current model.
    ModelRoot, Component = import_md2_model(editor, filename)

    if ModelRoot is None and Component is None:
        quarkx.beep() # Makes the computer "Beep" once if a file is not valid. Add more info to message.
        quarkx.msgbox("Invalid .md2 model.\nEditor can not import it.", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_OK)
        progressbar.close()
        return

    if editor.form is None: # Step 2 to import model from QuArK's Explorer.
        md2fileobj = quarkx.newfileobj("New model.md2")
        md2fileobj['FileName'] = 'New model.qkl'
        editor.Root.appenditem(Component)
        md2fileobj['Root'] = editor.Root.name
        md2fileobj.appenditem(editor.Root)
        md2fileobj.openinnewwindow()
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

    # Updates the Texture Browser's "Used Skin Textures" for all imported skins.
    tbx_list = quarkx.findtoolboxes("Texture Browser...");
    ToolBoxName, ToolBox, flag = tbx_list[0]
    if flag == 2:
        quarkpy.mdlbtns.texturebrowser() # If already open, reopens it after the update.
    else:
        quarkpy.mdlbtns.updateUsedTextures()

### To register this Python plugin and put it on the importers menu.
import quarkpy.qmdlbase
import ie_md2_import # This imports itself to be passed along so it can be used in mdlmgr.py later.
quarkpy.qmdlbase.RegisterMdlImporter(".md2 Quake2 Importer", ".md2 file", "*.md2", loadmodel)

# ----------- REVISION HISTORY ------------
#
# $Log: ie_md2_import.py,v $
# Revision 1.15  2012/12/25 06:01:57  cdunde
# Minor texture update.
#
# Revision 1.14  2011/03/13 00:41:47  cdunde
# Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
# Revision 1.13  2011/03/10 20:56:39  cdunde
# Updating of Used Textures in the Model Editor Texture Browser for all imported skin textures
# and allow bones and Skeleton folder to be placed in Userdata panel for reuse with other models.
#
# Revision 1.12  2010/06/13 15:37:55  cdunde
# Setup Model Editor to allow importing of model from main explorer File menu.
#
# Revision 1.11  2010/05/01 22:54:49  cdunde
# Fix for importing models without any skins.
# Set default skinsize to match all other importers.
#
# Revision 1.10  2010/05/01 04:25:37  cdunde
# Updated files to help increase editor speed by including necessary ModelComponentList items
# and removing redundant checks and calls to the list.
#
# Revision 1.9  2009/04/28 21:30:56  cdunde
# Model Editor Bone Rebuild merge to HEAD.
# Complete change of bone system.
#
# Revision 1.8  2009/01/29 02:13:51  cdunde
# To reverse frame indexing and fix it a better way by DanielPharos.
#
# Revision 1.7  2009/01/26 18:29:12  cdunde
# Update for correct frame index setting.
#
# Revision 1.6  2008/12/10 20:21:25  cdunde
# To display proper skin once model is imported.
#
# Revision 1.5  2008/11/19 06:16:22  cdunde
# Bones system moved to outside of components for Model Editor completed.
#
# Revision 1.4  2008/10/29 04:25:34  cdunde
# Minor correction.
#
# Revision 1.3  2008/10/26 00:42:21  cdunde
# Opps! Forgot md2 files don't have any Specifics, to remove test code.
#
# Revision 1.2  2008/10/26 00:07:09  cdunde
# Moved all of the Specifics/Args page code for the Python importers\exports to the importer files.
#
# Revision 1.1  2008/07/21 18:06:08  cdunde
# Moved all the start and end logging code to ie_utils.py in two functions,
# "default_start_logging" and "default_end_logging" for easer use and consistency.
# Also added logging and progress bars where needed and cleaned up files.
#
# Revision 1.5  2008/06/17 20:39:13  cdunde
# To add lwo model importer, uv's still not correct though.
# Also added model import\export logging options for file types.
#
# Revision 1.4  2008/06/16 00:11:46  cdunde
# Made importer\exporter logging corrections to work with others
# and started logging function for md2 model importer.
#
# Revision 1.3  2008/06/14 08:17:29  cdunde
# Added valid model path check.
#
# Revision 1.2  2008/06/07 05:46:50  cdunde
# Removed a lot of unused dead code.
#
# Revision 1.1  2008/06/04 03:56:40  cdunde
# Setup new QuArK Model Editor Python model import export system.
#
#
