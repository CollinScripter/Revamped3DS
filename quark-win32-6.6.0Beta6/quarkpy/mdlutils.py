"""   QuArK  -  Quake Army Knife

Various Model editor utility functions.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mdlutils.py,v 1.173 2013/02/13 03:28:42 cdunde Exp $

import quarkx
import qutils
import qhandles
from qeditor import *
from math import *

### Globals
keyframesrotation = 0

###############################
#
# Color functions
#
###############################


#
# Takes a float value from 0.0 to 1.0 and returns the Hex value (as a string)
# for its color to be stored and used for drawing the item in that color.
# These are only color going across the top of the custom color chart from yellow to red.
#
def weights_color(editor, weight_value):
    if weight_value <= .2:
        R = round(255-(weight_value*100*10.2))
        G = 255
        B = 51
    elif weight_value <= .4:
        R = 51
        G = 255
        B = round(51+((weight_value-.2)*100*10.2))
    elif weight_value <= .6:
        R = 51
        G = round(255-((weight_value-.4)*100*10.2))
        B = 255
    elif weight_value <= .8:
        R = round(51+((weight_value-.6)*100*10.2))
        G = 51
        B = 255
    elif weight_value <= 1.0:
        R = 255
        G = 51
        B = round(255-((weight_value-.8)*100*10.2))
    else:
        R = 255
        G = 51
        B = 255
    quarkx.setupsubset(SS_MODEL, "Colors")["temp_color"] = int(qutils.RGBToColor([R,G,B]))
    color = quarkx.setupsubset(SS_MODEL, "Colors")["temp_color"]
    return color



###############################
#
# ModelComponentList functions
#
###############################


#
# Creates the editor.ModelComponentList 'tristodraw' dictionary list for the "component" sent to this function.
#
def make_tristodraw_dict(editor, comp):
    if comp.dictitems.has_key("Frames:fg") and len(comp.dictitems['Frames:fg'].subitems) != 0:
        if (len(comp.dictitems['Frames:fg'].subitems[0].vertices) == 0) and (editor.ModelComponentList['tristodraw'].has_key(comp.name)):
            del editor.ModelComponentList['tristodraw'][comp.name]
            if editor.SkinViewList['tristodraw'].has_key(comp.name):
                del editor.SkinViewList['tristodraw'][comp.name]
            if editor.SkinViewList['handlepos'].has_key(comp.name):
                del editor.SkinViewList['handlepos'][comp.name]
        else:
            if not editor.ModelComponentList['tristodraw'].has_key(comp.name):
                editor.ModelComponentList['tristodraw'][comp.name] = {}
            if not editor.SkinViewList['tristodraw'].has_key(comp.name):
                editor.SkinViewList['tristodraw'][comp.name] = {}
            if not editor.SkinViewList['handlepos'].has_key(comp.name):
                editor.SkinViewList['handlepos'][comp.name] = []
            tristodraw = {}
            skin_tristodraw = {}
            tris = comp.triangles
            for vtx in range(len(comp.dictitems['Frames:fg'].subitems[0].vertices)):
                tristodraw[vtx] = []
            for i in range(len(tris)):
                for j in range(len(tris[i])):
                    vtx = tris[i][j][0]
                    svtx = (i*3) + j
                    skin_tristodraw[svtx] = []
                    for k in range(len(tris[i])):
                        vtx2 = tris[i][k][0]
                        svtx2 = (i*3) + k
                        if vtx == vtx2:
                            continue
                        if not vtx2 in tristodraw[vtx]:
                            tristodraw[vtx] = tristodraw[vtx] + [vtx2]
                        if not svtx2 in skin_tristodraw[svtx]:
                            skin_tristodraw[svtx] = skin_tristodraw[svtx] + [svtx2]
            for vtx in range(len(comp.dictitems['Frames:fg'].subitems[0].vertices)):
                if len(tristodraw[vtx]) == 0:
                    del tristodraw[vtx]
                    continue
                tristodraw[vtx].sort()
                tristodraw[vtx].reverse()
            if len(tristodraw) == 0:
                del editor.ModelComponentList['tristodraw'][comp.name]
                if len(skin_tristodraw) == 0:
                    del editor.SkinViewList['tristodraw'][comp.name]
                    del editor.SkinViewList['handlepos'][comp.name]
            else:
                editor.ModelComponentList['tristodraw'][comp.name] = tristodraw
                keys = skin_tristodraw.keys()
                for vtx in range(len(keys)):
                    if len(skin_tristodraw[keys[vtx]]) == 0:
                        del skin_tristodraw[keys[vtx]]
                        continue
                    skin_tristodraw[keys[vtx]].sort()
                    skin_tristodraw[keys[vtx]].reverse()
                editor.SkinViewList['tristodraw'][comp.name] = skin_tristodraw
    else:
        if editor.ModelComponentList['tristodraw'].has_key(comp.name):
            del editor.ModelComponentList['tristodraw'][comp.name]
            if editor.SkinViewList['tristodraw'].has_key(comp.name):
                del editor.SkinViewList['tristodraw'][comp.name]
                del editor.SkinViewList['handlepos'][comp.name]

#
# Updates the editor.ModelComponentList for a component's bonevtxlist when any vertex is removed,
# and it needs an undo action sent to it as well for updating the bones needed.
#
def update_bonevtxlist(editor, comp, vertices_to_remove):
    Old_dictionary_list = editor.ModelComponentList[comp.name]['bonevtxlist'].copy()
    old = []
    new = []
    for bone in editor.ModelComponentList[comp.name]['bonevtxlist']:
        old_bone = findbone(editor, bone)
        old = old +[old_bone]
        new_bone = old_bone.copy()
        new = new + [new_bone]
        old_vertices = new_bone.vtxlist.copy()
        for mesh in new_bone.vtxlist:
            Old_vtxlist = old_vertices[mesh]
            old_vertices[mesh] = update_vertex_list(Old_vtxlist, vertices_to_remove)
            if old_vertices[mesh] is None:
                del old_vertices[mesh]
        new_bone.vtxlist = old_vertices
        old_vertices = new_bone.vtx_pos.copy()
        for mesh in new_bone.vtx_pos:
            Old_vtxlist = old_vertices[mesh]
            old_vertices[mesh] = update_vertex_list(Old_vtxlist, vertices_to_remove)
            if old_vertices[mesh] is None:
                del old_vertices[mesh]
        new_bone.vtx_pos = old_vertices
        Old_dictionary_list[bone] = update_vertex_keys(Old_dictionary_list[bone], vertices_to_remove)
        if len(Old_dictionary_list[bone]) == 0:
            del Old_dictionary_list[bone]
    undo = quarkx.action()
    oldskelgroup = editor.Root.dictitems['Skeleton:bg']
    newskelgroup = boneundo(editor, old, new)
    editor.ModelComponentList[comp.name]['bonevtxlist'] = Old_dictionary_list
    undo.exchange(oldskelgroup, newskelgroup)
    editor.ok(undo, "")
    # This section updates the "Vertex Weights Dialog" if it is opened and needs to update.
    formlist = quarkx.forms(1)
    for f in formlist:
        try:
            if f.caption == "Vertex Weights Dialog":
                import mdlentities # Import needs to be here to avoid error.
                mdlentities.WeightsClick(editor)
        except:
            pass

#
# Updates the editor.ModelComponentList for a component's colorvtxlist when any vertex is removed.
#
def update_colorvtxlist(editor, comp, vertices_to_remove):
    Old_dictionary_list = editor.ModelComponentList[comp.name]['colorvtxlist']
    editor.ModelComponentList[comp.name]['colorvtxlist'] = update_vertex_keys(Old_dictionary_list, vertices_to_remove)

#
# Updates the editor.ModelComponentList for a component's weightvtxlist.
#
def update_weightvtxlist(editor, vertex_index, bone=None, comp=None, option=1):
    def update_weightlist(Old_dictionary_list, bone_item, vertex_index=vertex_index):
        if not Old_dictionary_list.has_key(bone_item.name):
            Old_dictionary_list[bone_item.name] = {}
        Old_dictionary_list[bone_item.name]['color'] = bone_item.dictspec[bone_item.shortname + "_weight_color"]
        Old_dictionary_list[bone_item.name]['weight_value'] = float(bone_item.dictspec[bone_item.shortname + "_weight_value"])
    if comp is None:
        comp = editor.Root.currentcomponent
    if option == 1:
        if not editor.ModelComponentList[comp.name]['weightvtxlist'].has_key(vertex_index):
            editor.ModelComponentList[comp.name]['weightvtxlist'][vertex_index] = {}
            Old_dictionary_list = editor.ModelComponentList[comp.name]['weightvtxlist'][vertex_index]
        else:
            Old_dictionary_list = editor.ModelComponentList[comp.name]['weightvtxlist'][vertex_index]
    found_bone = None
    for item in editor.layout.explorer.sellist:
        if item.type == ":bone":
            if item.dictspec.has_key(item.shortname + "_weight_value"):
                if bone is not None and found_bone is None and item.name == bone.name:
                    found_bone = 1
                update_weightlist(Old_dictionary_list, item)
    if bone is not None and found_bone is None:
        if not bone.dictspec.has_key(bone.shortname + "_weight_value"):
            bone[bone.shortname + "_weight_value"] = "1.0"
            bone[bone.shortname + "_weight_color"] = weights_color(editor, 1.0)
        update_weightlist(Old_dictionary_list, bone)



###############################
#
# Operational functions
#
##############################################################


#
# Saves the tree-view selections and expanded folders structure.
#
def SaveTreeView(editor):
    sub_types = [':mg', ':tag', ':bg', ':bone', ':mc', ':sg', ':fg']
    skip_types = [':sdo']
    sellist = editor.layout.explorer.sellist
    editor.ObjSelectList = []
    for obj in sellist:
        sel = [obj.name]
        par = obj.parent
        if par.name == "New model.qkl":
            par = editor.Root
        while par.type != ":mr":
            sel = sel + [par.name]
            par = par.parent
        sel.reverse()
        editor.ObjSelectList = editor.ObjSelectList + [sel]

    editor.ObjExpandList = []
    def storestate(parent, list):
        if (len(parent.subitems) != 0) and parent.type in sub_types:
            if (parent.flags & qutils.OF_TVEXPANDED) and not parent.name in list:
                list += [parent.name]
            for Object in parent.subitems:
                if (len(Object.subitems) != 0) and Object.type in sub_types:
                    if (Object.flags & qutils.OF_TVEXPANDED):
                        list += [Object.name]
                        list = storestate(Object, list)
                elif Object.type in skip_types or Object.type == ":bone":
                    continue
                else:
                    break
        return list
    for Object in editor.Root.subitems:
        editor.ObjExpandList = storestate(Object, editor.ObjExpandList)

#
# Restores the tree-view selections and expanded folders structure.
#
def RestoreTreeView(editor):
    NewSellist = []
    for item in editor.ObjSelectList:
        get = editor.Root
        try:
            for name in range(len(item)):
                get = get.dictitems[item[name]]
            NewSellist = NewSellist + [get]
        except:
            continue

    getbones = 0
    for ObjectName in editor.ObjExpandList:
        try:
            if ObjectName.endswith(":bg"):
                bonesgroup = editor.Root.dictitems[ObjectName]
                bonesgroup.flags = bonesgroup.flags | qutils.OF_TVEXPANDED
            elif ObjectName.endswith(":bone"):
                if getbones == 0:
                	bones = bonesgroup.findallsubitems("", ':bone')
                	getbones = 1
                for bone in bones:
                    if bone.name == ObjectName:
                        bone.flags = bone.flags | qutils.OF_TVEXPANDED
                        break
            elif ObjectName.endswith(":mc"):
                comp = editor.Root.dictitems[ObjectName]
                comp.flags = comp.flags | qutils.OF_TVEXPANDED
            elif ObjectName.endswith(":sg") or ObjectName.endswith(":fg"):
                group = editor.Root.dictitems[comp.name].dictitems[ObjectName]
                group.flags = group.flags | qutils.OF_TVEXPANDED
        except:
            continue

    editor.layout.explorer.sellist = NewSellist

#
# Saves the ModelComponentList into cPickle as a single string.
#
def FlattenModelComponentList(editor):
    # Based on http://docs.python.org/library/pickle.html
    import cPickle
    from cStringIO import StringIO
    src = StringIO()
    p = cPickle.Pickler(src)
    p.dump(editor.ModelComponentList)
    return src.getvalue()

#
# Extracts the stored ModelComponentList from cPickle as a single string.
#
def UnflattenModelComponentList(editor, datastream):
    # Based on http://docs.python.org/library/pickle.html
    import cPickle
    from cStringIO import StringIO
    dst = StringIO(datastream)
    up = cPickle.Unpickler(dst)
    editor.ModelComponentList = up.load()

#
# Checks a triangle index to see if it is in the list of triangles to be removed, 0 = no, 1= yes.
#
def checkinlist(tri, toberemoved):
  for tbr in toberemoved:
    if (tri == tbr):
      return 1
  return 0


#
# Is a given object still in the tree view = 1, or was it removed = 0 ?
#
def checktree(root, obj):
    while obj is not root:
        t = obj.parent
        if t is None or not (obj in t.subitems):
            return 0
        obj = t
    return 1


#
# This function sets black colors on components that don't have any colors set
#
def fixColorComps(editor):
    for comp in editor.Root.subitems:
        if comp.type != ":mc":
            continue
        if not comp.dictspec.has_key('comp_color1'):
            comp['comp_color1'] = '\x00'
        if not comp.dictspec.has_key('comp_color2'):
            comp['comp_color2'] = '\x00'
    if editor.layout is not None:
        editor.layout.explorer.invalidate()


#
# The UserDataPanel class, overridden to be model-specific.
#
class MdlUserDataPanel(UserDataPanel):

    def btnclick(self, btn):
        #
        # Send the click message to the module mdlbtns.
        #
        import mdlbtns
        mdlbtns.mdlbuttonclick(btn)


    #def drop(self, btnpanel, list, i, source):
        #if len(list)==1 and list[0].type == ':g':
        #    quarkx.clickform = btnpanel.owner
        #    editor = mapeditor()
        #    if editor is not None and source is editor.layout.explorer:
        #        choice = quarkx.msgbox("You are about to create a new button from this group. Do you want the button to display a menu with the items in this group ?\n\nYES: you can pick up individual items when you click on this button.\nNO: you can insert the whole group in your map by clicking on this button.", MT_CONFIRMATION, MB_YES_NO_CANCEL)
        #        if choice == MR_CANCEL:
        #            return
        #        if choice == MR_YES:
        #            list = [group2folder(list[0])]
        #UserDataPanel.drop(self, btnpanel, list, i, source)



def find2DTriangles(comp, tri_index, ver_index):
    "This function returns triangles and their index of a component's"
    "mesh that have a common vertex position of the 2D drag view."
    "This is primarily used for the Skin-view mesh drag option."
    "See the mdlhandles.py file class SkinHandle, drag function for its use."
    tris = comp.triangles
    tris_out = {}
    i = 0
    for tri in tris:
        for vtx in tri:
            if str(vtx) == str(tris[tri_index][ver_index]):
              if i == tri_index:
                  break
              else:
                  tris_out[i] = tri
                  break
        i = i + 1
    return tris_out


#
# Checks all values, in the same list position, of two tuples
# and returns 1 if they are all nearly the same.
# Used for comparing vectors for possible dragging together.
#
def checktuplepos(tuple1, tuple2):
    for i in range(len(tuple1)):
        if abs(tuple1[i] - tuple2[i]) < 0.0001:
            if i == len(tuple1)-1:
                return 1
            continue
        else:
            return 0



#
# Calculate Position of a Point along the vector AC, Keeping L (Length)
# This function is used to calculate the new position of a "Bone" drag handle
# to keep a bone the same length during and after a drag movement.
#
def ProjectKeepingLength(A,C,L):
    def NormaliseVect(v1, v2):
        le = sqrt( pow(v2.x - v1.x, 2) + 
                   pow(v2.y - v1.y, 2) + 
                   pow(v2.z - v1.z, 2) )
        if (le <> 0):
            v = quarkx.vect( \
                (v2.x - v1.x) / le, \
                (v2.y - v1.y) / le, \
                (v2.z - v1.z) / le  )
        else:
            v = quarkx.vect(0,0,0)
        return v
    n = NormaliseVect(A, C)
    xxx = quarkx.vect(
        A.x + (L * n.x),
        A.y + (L * n.y),
        A.z + (L * n.z)
        )
    return xxx


#
# Checks triangle for vertex [index]
#
def checkTriangle(tri, index):
    for c in tri:
        if (c[0] == index): # c[0] is the 'vertexno'
            return 1
    return 0


#
#  Find a triangle based on the 3 vertex indexs that are given.
#  DanielPharos: Make sure v1, v2 and v3 are different!
#
def findTriangle(comp, v1, v2, v3):
    tris = comp.triangles
    index = -1
    for tri in tris:
        index = index + 1
        b = 0
        v1found = 0
        v2found = 0
        v3found = 0
        for c in tri:
            if v1found == 0:
                if (v1 == c[0]):
                    v1found = 1
                    b = b + 1
            if v2found == 0:
                if (v2 == c[0]):
                    v2found = 1
                    b = b + 1
            if v3found == 0:
                if (v3 == c[0]):
                    v3found = 1
                    b = b + 1
            if b == 3:
                return index
    return None


#
# Find other triangles containing a vertex at the same location
# as the one selected creating a VertexHandle instance.
# ONLY returns the triangle objects themselves, but NOT their tri_index numbers.
# To get both use the findTrianglesAndIndex function below this one.
# For example call this function like this (for clarity):
#    component = editor.layout.explorer.uniquesel
#    handlevertex = self.index
#    if component.name.endswith(":mc"):
#        tris = findTriangles(component, handlevertex)
# or like this (to be brief):
#    comp = editor.layout.explorer.uniquesel
#    if comp.name.endswith(":mc"):
#        tris = findTriangles(comp, self.index)
#
def findTriangles(comp, index):
    tris = comp.triangles
    tris_out = [ ]
    for tri in tris:
        found_com_vtx_pos_tri = checkTriangle(tri, index)
        if (found_com_vtx_pos_tri == 1):
            tris_out = tris_out + [ tri ]
    return tris_out


#
# Find and return other triangles (AND their tri_index and ver_index_order_pos numbers)
# containing a vertex at the same location as the one selected creating a VertexHandle instance.
# Also returns each triangles vertex, vert_index and vert_pos for the following complete list items.
###|--- contence ---|-------- format -------|----------------------- discription -----------------------|
#   Editor vertexes  (frame_vertices_index, view.proj(pos), tri_index, ver_index_order_pos, (tri_vert0,tri_vert1,tri_vert2))
#                    Created using:    editor.Root.currentcomponent.currentframe.vertices
#                                         (see Infobase docs help/src.quarkx.html#objectsmodeleditor)
#                               item 0: Its "Frame" "vertices" number, which is the same number as a triangles "ver_index" number.
#                               item 1: Its 3D grid pos "projected" to a x,y 2D view position.
#                                       The "pos" needs to be a projected position for a decent size application
#                                       to the "Skin-view" when a new triangle is made in the editor.
#                               item 2: The Model component mesh triangle number this vertex is used in (usually more then one triangle).
#                               item 3: The ver_index_order_pos number is its order number position of the triangle points, either 0, 1 or 2.
#                               item 4: All 3 of the triangles vertexes data (ver_index, u and v (or x,y) projected texture 2D Skin-view positions)
#
def findTrianglesAndIndexes(comp, vert_index, vert_pos):
    tris = comp.triangles
    tris_out = [ ]
    for tri_index in range(len(tris)):
        found_com_vtx_pos_tri = checkTriangle(tris[tri_index], vert_index)
        if (found_com_vtx_pos_tri == 1):
            if vert_index == tris[tri_index][0][0]:
                tris_out = tris_out + [[vert_index, vert_pos, tri_index, 0, tris[tri_index]]]
            elif vert_index == tris[tri_index][1][0]:
                tris_out = tris_out + [[vert_index, vert_pos, tri_index, 1, tris[tri_index]]]
            else:
                tris_out = tris_out + [[vert_index, vert_pos, tri_index, 2, tris[tri_index]]]
    return tris_out



# 'index' the vertex index number that is being deleted and is used in the triangle 'tri'.
# This funciton fixes the vert_index number for one particular triangle.
def fixTri(tri, index):
    new_tri = [ ]
    for c in tri:
        v = 0
        if ( c[0] > index):
            v = c[0]-1
        else:
            v = c[0]
        s = c[1]
        t = c[2]
        new_tri = new_tri + [(v,s,t)]
    return (new_tri[0], new_tri[1], new_tri[2])


#
# 'index' is a vertex index number that is being deleted and is used in the triangle 'tri'.
# This funciton fixes the vert_index numbers for all triangles in the list 'tris'.
# Goes through tri list: if greaterthan index then takes 1 away from vertexno.
#
def fixUpVertexNos(tris, index):
    new_tris = [ ]
    for tri in tris:
         x = fixTri(tri, index)
         new_tris = new_tris + [x]
    return new_tris



###############################
#
# Animation functions
#
###############################

def KeyframeLinearInterpolation(editor, sellistPerComp, IPF, keyframenbr1, keyframenbr2):
    undo = quarkx.action()
    msg = str(int(round(1/IPF)-2)) + " key frames added"
    # To handle models that have bones and multiple components.
    if len(sellistPerComp) == 1 and len(editor.Root.dictitems['Skeleton:bg'].subitems) != 0:
        framecomp = sellistPerComp[0][0]
        group = framecomp.name.split("_")[0]
        for item in editor.Root.subitems:
            if item.type == ":mc" and item.name != framecomp.name and item.name.startswith(group):
                    FrameGroup = item.dictitems['Frames:fg'].subitems # Get all the frames for this component.
                    sellistPerComp = sellistPerComp + [[item, [FrameGroup[keyframenbr1], FrameGroup[keyframenbr2]]]]
    for comp in sellistPerComp:
        includebones = check4bones = allbones = bones2move = None
        if comp[0].type == ":tag":
            parent = comp[0]
        else:
            parent = comp[0].dictitems['Frames:fg']
            if allbones is None:
                allbones = editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone')
        frames = parent.subitems
        if check4bones is None and allbones is not None and len(allbones) != 0:
            check4bones = 1
            includebones = []
            bones2move = []
            bonelist = editor.ModelComponentList['bonelist']
            keys = bonelist.keys()
            bones_parent_list = []
            group_count = -1
            group_list = []
            for bone in allbones:
                if not bone.name in keys:
                    bone_comp = bone.dictspec['component']
                    bone_frames = editor.Root.dictitems[bone_comp].dictitems['Frames:fg'].subitems
                    bonelist[bone.name] = {}
                    bonelist[bone.name]['frames'] = {}
                    for frame in bone_frames:
                        bonelist[bone.name]['frames'][frame.name] = {}
                        vertices = frame.vertices
                        vtxlist = bone.vtx_pos[bone_comp]
                        vtxpos = quarkx.vect(0.0, 0.0, 0.0)
                        for vtx in vtxlist:
                            vtxpos = vtxpos + vertices[vtx]
                        vtxpos = vtxpos/ float(len(vtxlist))
                        pos = vtxpos + quarkx.vect(bone.dictspec['draw_offset'])
                        bonelist[bone.name]['frames'][frame.name]['position'] = pos.tuple
                        bonelist[bone.name]['frames'][frame.name]['rotmatrix'] = bone.rotmatrix.tuple
                if (bonelist[bone.name]['frames'].has_key(frames[keyframenbr1].name) and bonelist[bone.name]['frames'].has_key(frames[keyframenbr2].name)) or (bone.dictspec['parent_name'] in bones_parent_list):
                    if (bone.dictspec['parent_name'] in bones_parent_list) or (str(bonelist[bone.name]['frames'][frames[keyframenbr1].name]['position']) != str(bonelist[bone.name]['frames'][frames[keyframenbr2].name]['position'])) or (str(bonelist[bone.name]['frames'][frames[keyframenbr1].name]['rotmatrix']) != str(bonelist[bone.name]['frames'][frames[keyframenbr2].name]['rotmatrix'])):
                        if not bone.name in bones_parent_list:
                            if not bone.dictspec['parent_name'] in bones_parent_list and ((str(bonelist[bone.name]['frames'][frames[keyframenbr1].name]['position']) != str(bonelist[bone.name]['frames'][frames[keyframenbr2].name]['position'])) or (str(bonelist[bone.name]['frames'][frames[keyframenbr1].name]['rotmatrix']) != str(bonelist[bone.name]['frames'][frames[keyframenbr2].name]['rotmatrix']))):
                                group_count += 1
                                group_list = []
                                bones2move.append(group_list)
                            bones_parent_list.append(bone.name)
                                
                        bones2move[group_count].append(bone.name)
                    else:
                        includebones = includebones + [bone.name]
        insertbefore = comp[1][1]
        PrevFrame = comp[1][0].copy()
        NextFrame = comp[1][1].copy()
        for framenbr in range(keyframenbr1+1, keyframenbr2):
            old = frames[framenbr]
            undo.exchange(old, None)
        if bones2move is None:
            count = 1
        else:
            count = len(bones2move)
        for framenbr in range(1, int(round(1/IPF))-1):
            Factor = IPF * framenbr
            ReducedFactor = Factor - floor(Factor)
            newframe = PrevFrame.copy()
            newframe.shortname = PrevFrame.shortname + "-" + str(framenbr)

            PrevVertices = PrevFrame.vertices
            NextVertices = NextFrame.vertices
            if bones2move is not None:
                vtxcount = len(PrevVertices)
                oldverticespos = {}
                newverticespos = {}
                verticesweight = {}
                oldverticespos[comp[0].name] = PrevVertices
                newverticespos[comp[0].name] = [[]] * vtxcount
                verticesweight[comp[0].name] = [[]] * vtxcount
                for vtx in range(vtxcount):
                    newverticespos[comp[0].name][vtx] = None
                    verticesweight[comp[0].name][vtx] = 0.0

            for c in range(count):
                if includebones is not None:
                    rotbone = bones2move[c][0]
                    dragbone = bones2move[c][1]
                    rotationorigin = quarkx.vect(bonelist[rotbone]['frames'][PrevFrame.name]['position'])
                    rotationorigin_start = quarkx.vect(bonelist[dragbone]['frames'][PrevFrame.name]['position']) - quarkx.vect(bonelist[rotbone]['frames'][PrevFrame.name]['position'])
                    rotationorigin_end = quarkx.vect(bonelist[dragbone]['frames'][NextFrame.name]['position']) - quarkx.vect(bonelist[rotbone]['frames'][NextFrame.name]['position'])
                    delta_diff = rotationorigin_end - rotationorigin_start
                    mOld = quarkx.matrix(bonelist[rotbone]['frames'][PrevFrame.name]['rotmatrix'])
                    mNew = quarkx.matrix(bonelist[rotbone]['frames'][NextFrame.name]['rotmatrix'])
                    mDIFF = mNew - mOld # Tells us which axes we rotated on.
                    mCHECK = mDIFF.tuple # Tells us which axes we rotated on.
                    if mCHECK[0][0]==0 and mCHECK[0][1]==0 and mCHECK[0][2]==0:
                        #Get the X-view
                        for view in editor.layout.views:
                            if view.info["type"] == "YZ":
                                break
                        rotationorigin_end = rotationorigin_start + ReducedFactor * delta_diff
                        normal = view.vector("Z").normalized
                        oldpos = rotationorigin_start - normal*(normal*rotationorigin_start)
                        newpos = rotationorigin_end - normal*(normal*rotationorigin_end)
                        m = qhandles.UserRotationMatrix(normal, newpos, oldpos, 0)
                        mDIFF = m
                    elif mCHECK[1][0]==0 and mCHECK[1][1]==0 and mCHECK[1][2]==0:
                        #Get the Y-view
                        for view in editor.layout.views:
                            if view.info["type"] == "XZ":
                                break
                        rotationorigin_end = rotationorigin_start + ReducedFactor * delta_diff
                        normal = view.vector("Z").normalized
                        oldpos = rotationorigin_start - normal*(normal*rotationorigin_start)
                        newpos = rotationorigin_end - normal*(normal*rotationorigin_end)
                        m = qhandles.UserRotationMatrix(normal, newpos, oldpos, 0)
                        mDIFF = m
                    elif mCHECK[2][0]==0 and mCHECK[2][1]==0 and mCHECK[2][2]==0:
                        #Get the Z-view
                        for view in editor.layout.views:
                            if view.info["type"] == "XY":
                                break
                        rotationorigin_end = rotationorigin_start + ReducedFactor * delta_diff
                        normal = view.vector("Z").normalized
                        oldpos = rotationorigin_start - normal*(normal*rotationorigin_start)
                        newpos = rotationorigin_end - normal*(normal*rotationorigin_end)
                        m = qhandles.UserRotationMatrix(normal, newpos, oldpos, 0)
                        mDIFF = m
                    else:
                        #Get the editor's view
                        for view in editor.layout.views:
                            if view.info["type"] == "2D":
                                break
                        rotationorigin_end = rotationorigin_start + ReducedFactor * delta_diff
                        normal = view.vector("Z").normalized
                        oldpos = rotationorigin_start - normal*(normal*rotationorigin_start)
                        newpos = rotationorigin_end - normal*(normal*rotationorigin_end)
                        m = qhandles.UserRotationMatrix(normal, newpos, oldpos, 0)
                        mDIFF = m
                    if m is None:
                        m = quarkx.matrix(quarkx.vect(1.0, 0.0, 0.0), quarkx.vect(0.0, 1.0, 0.0), quarkx.vect(0.0, 0.0, 1.0))
                if comp[0].type == ":tag":
                    OldPos = quarkx.vect(PrevFrame.dictspec['origin'])
                    NewPos = quarkx.vect(NextFrame.dictspec['origin'])
                    pos = (OldPos * (1.0 - ReducedFactor)) + (NewPos * ReducedFactor)
                    newframe['origin'] = pos.tuple
                    msg = str(int(round(1/IPF)-2)) + " key and tag frames added"
                else:
                    if includebones is not None: # Stores the bone position (that did NOT move) for the newly created frame.
                        for bone in includebones:
                            OldPos = bonelist[bone]['frames'][PrevFrame.name]['position']
                            OldRot = bonelist[bone]['frames'][PrevFrame.name]['rotmatrix']
                            bonelist[bone]['frames'][newframe.name] = {}
                            bonelist[bone]['frames'][newframe.name]['position'] = OldPos
                            bonelist[bone]['frames'][newframe.name]['rotmatrix'] = OldRot

                    if bones2move is not None: # Stores the bone position (that DID move) for the newly created frame.
                        bones = []
                        for bone in bones2move[c]:
                            for bone2 in allbones:
                                if bone2.name == bone:
                                    bones.append(bone2)
                                    break
                            OldPos = bonelist[bone]['frames'][PrevFrame.name]['position']
                            OldRot = quarkx.matrix(bonelist[bone]['frames'][PrevFrame.name]['rotmatrix'])
                            try:
                                NewPos = bonelist[bone]['frames'][NextFrame.name]['position']
                                NewRot = quarkx.matrix(bonelist[bone]['frames'][NextFrame.name]['rotmatrix'])
                                rot = (OldRot * (1.0 - ReducedFactor)) + (NewRot * ReducedFactor)
                                if bone == bones2move[c][0]:
                                    pos = (quarkx.vect(OldPos) * (1.0 - ReducedFactor)) + (quarkx.vect(NewPos) * ReducedFactor)
                                    rot = m * OldRot
                                else:
                                    changedpos = quarkx.vect(OldPos) - rotationorigin
                                    changedpos = m * changedpos
                                    pos = changedpos + rotationorigin
                                    ParNewRot = quarkx.matrix(bonelist[bone2.dictspec['parent_name']]['frames'][newframe.name]['rotmatrix'])
                                    rot = ParNewRot * OldRot
                            except:
                                ParOldPos = quarkx.vect(bonelist[bone2.dictspec['parent_name']]['frames'][PrevFrame.name]['position'])
                                ParNewPos = quarkx.vect(bonelist[bone2.dictspec['parent_name']]['frames'][newframe.name]['position'])
                                ParNewRot = quarkx.matrix(bonelist[bone2.dictspec['parent_name']]['frames'][newframe.name]['rotmatrix'])
                                changedpos = quarkx.vect(OldPos) - rotationorigin
                                changedpos = m * changedpos
                                pos = changedpos + rotationorigin
                                rot = ParNewRot * OldRot
                            bonelist[bone]['frames'][newframe.name] = {}
                            bonelist[bone]['frames'][newframe.name]['position'] = pos.tuple
                            bonelist[bone]['frames'][newframe.name]['rotmatrix'] = rot.tuple
                    # Positions the newly created frame's vertices.
                    newvertices = []
                    if bones2move is not None: # For models with bones, fills the 3 dictionary list below.
                        for bone in bones:
                            vertices = bone.vtxlist
                            for compname in vertices:
                                for vtx in vertices[compname]:
                                    if editor.ModelComponentList[compname]['weightvtxlist'].has_key(vtx) and editor.ModelComponentList[compname]['weightvtxlist'][vtx].has_key(bone.name):
                                        weight_value = editor.ModelComponentList[compname]['weightvtxlist'][vtx][bone.name]['weight_value']
                                    else:
                                        weight_value = 1.0
                                    try:
                                      #  changedpos = oldverticespos[compname][vtx] - rotationorigin
                                        changedpos = PrevVertices[vtx] - rotationorigin
                                        changedpos = m * changedpos
                                        if newverticespos[compname][vtx] is None:
                                            newverticespos[compname][vtx] = quarkx.vect(0, 0, 0)
                                        newverticespos[compname][vtx] = newverticespos[compname][vtx] + (changedpos + rotationorigin) * weight_value
                                        verticesweight[compname][vtx] = verticesweight[compname][vtx] + weight_value
                                    except:
                                        break
            if bones2move is not None: # For models with bones.
                for compname in newverticespos.keys():
                    for vtx in range(len(newverticespos[compname])):
                        if newverticespos[compname][vtx] is None:
                            newverticespos[compname][vtx] = oldverticespos[compname][vtx]
                            verticesweight[compname][vtx] = 1.0
                        if abs(verticesweight[compname][vtx] - 1.0) > 0.001:
                            oldpartpos = oldverticespos[compname][vtx] * (1.0 - verticesweight[compname][vtx])
                            newverticespos[compname][vtx] = newverticespos[compname][vtx] + oldpartpos
                newvertices = newverticespos[compname]
            else: # For models with NO bones.
                for i in range(len(PrevVertices)):
                    OldPos = PrevVertices[i]
                    NewPos = NextVertices[i]
                    pos = (OldPos * (1.0 - ReducedFactor)) + (NewPos * ReducedFactor)
                    newvertices = newvertices + [pos]
            newframe.vertices = newvertices

            undo.put(parent, newframe, insertbefore)
    editor.ok(undo, msg)

def LinearInterpolation(editor, AnimFrames, Factor=0.0):
    FrameIndex = int(floor(Factor))
    if (Factor < 0.0) or (FrameIndex > len(AnimFrames)-1):
        # Somebody send me a bad Factor! Bad programmer! Bad!
        raise "LinearInterpolation: Factor out of range! (%f)" % Factor
    PrevFrame = AnimFrames[FrameIndex]
    if FrameIndex < len(AnimFrames)-1:
        NextFrame = AnimFrames[FrameIndex+1]
    else:
        NextFrame = AnimFrames[0]
    PrevVertices = PrevFrame.vertices
    NextVertices = NextFrame.vertices
    if len(PrevVertices) != len(NextVertices):
        # Somebody send me frames with different numbers of vertices! Bad programmer! Bad!
        raise "LinearInterpolation: Incompatible frames!"
    ReducedFactor = Factor - floor(Factor)
    newframe = PrevFrame.copy()
    newframe.shortname = "AnimFrame"
    newvertices = []
    for i in range(len(PrevVertices)):
        OldPos = PrevVertices[i]
        NewPos = NextVertices[i]
        pos = (OldPos * (1.0 - ReducedFactor)) + (NewPos * ReducedFactor)
        newvertices = newvertices + [pos]
    newframe.vertices = newvertices
    return newframe

def gauss_jordan(m, eps = 1.0/(10**10)):
  #From: http://elonen.iki.fi/code/misc-notes/python-gaussj/
  """Puts given matrix (2D array) into the Reduced Row Echelon Form.
     Returns 1 if successful, 0 if 'm' is singular.
     NOTE: make sure all the matrix items support fractions! Int matrix will NOT work!
     Written by Jarno Elonen in April 2005, released into Public Domain"""
  (h, w) = (len(m), len(m[0]))
  for y in range(0,h):
    maxrow = y
    for y2 in range(y+1, h):    # Find max pivot
      if abs(m[y2][y]) > abs(m[maxrow][y]):
        maxrow = y2
    (m[y], m[maxrow]) = (m[maxrow], m[y])
    if abs(m[y][y]) <= eps:     # Singular?
      return 0
    for y2 in range(y+1, h):    # Eliminate column y
      c = m[y2][y] / m[y][y]
      for x in range(y, w):
        m[y2][x] -= m[y][x] * c
  for y in range(h-1, 0-1, -1): # Backsubstitute
    c  = m[y][y]
    for y2 in range(0,y):
      for x in range(w-1, y-1, -1):
        m[y2][x] -=  m[y][x] * m[y2][y] / c
    m[y][y] /= c
    for x in range(h, w):       # Normalize row y
      m[y][x] /= c
  return 1

def PolynomialInterpolation(editor, AnimFrames, Factor=0.0):
    FrameIndex = int(floor(Factor))
    if (Factor < 0.0) or (FrameIndex > len(AnimFrames)-1):
        # Somebody send me a bad Factor! Bad programmer! Bad!
        raise "PolynomialInterpolation: Factor out of range! (%f)" % Factor
    # Uses gaussian elimination: [A]*{x}={B}
    NumberFrames = len(AnimFrames)
    if NumberFrames > 1000:
        # Can't have the float-cast loose precision
        raise "PolynomialInterpolation: Too many frames!"
    newframe = AnimFrames[0].copy()
    newframe.shortname = "AnimFrame"
    newvertices = []
    for vtx in range(len(AnimFrames[0].vertices)):
        mtx = []
        for n in range(NumberFrames):
            NewLine = []
            for m in range(NumberFrames):
                NewLine = NewLine + [float(n**(NumberFrames-1-m))]
            NewLine = NewLine + [AnimFrames[n].vertices[vtx]]
            mtx = mtx + [NewLine]
        pos = quarkx.vect((0.0, 0.0, 0.0))
        if gauss_jordan(mtx):
            for n in range(NumberFrames):
                pos = pos + (mtx[n][NumberFrames] * (Factor ** (NumberFrames-1-n)))
        newvertices = newvertices + [pos]
    newframe.vertices = newvertices
    return newframe


###############################
#
# Vertex functions
#
###############################


#
# Add a vertex to the currently selected model component or frame(s)
# at the position where the cursor was when the RMB was clicked.
#
def addvertex(editor, comp, pos):
    new_comp = comp.copy()
    compframes = new_comp.findallsubitems("", ':mf')   # find all frames
    for compframe in compframes:
        vtxs = compframe.vertices
        vtxs = vtxs + [pos]
        compframe.vertices = vtxs
        compframe.compparent = new_comp # To allow frame relocation after editing.
    undo = quarkx.action()
    undo.exchange(comp, new_comp)
    editor.ok(undo, "add vertex")


#
# Updates (drags) a vertex or vertexes in the 'editor.SkinVertexSelList' list, or similar list,
#    of the currently selected model component or frame(s),
#    to the same position of the 1st item in the 'editor.SkinVertexSelList' list.
# The 'editor.SkinVertexSelList' list is a group of lists within a list.
# If 'option 1' is used for the Skin-view then
# each group list must be created in the manner below then added to the 'editor.SkinVertexSelList' list:
#    editor.SkinVertexSelList + [[self.pos, self, self.tri_index, self.ver_index]]
# if 'option 0' is used for the Model Editor then
# each group list must be created in the manner below then added to the 'editor.ModelVertexSelList' list:
#    editor.ModelVertexSelList + [[frame_vertices_index, view.proj(pos)]]
#
def replacevertexes(editor, comp, vertexlist, flags, view, undomsg, option=1, method=1):
    "option=0 uses the ModelVertexSelList for the editor to align vertexes."
    "option=1 uses the SkinVertexSelList for the Skin-view to align vertexes."
    "option=2 uses the ModelVertexSelList for the editor and merges two, or more, selected vertexes."
    "method=1 other selected vertexes move to the 'Base' vertex position of each tree-view selected 'frame', only applies to option=0."
    "method=2 other selected vertexes move to the 'Base' vertex position of the 1st tree-view selected 'frame', only applies to option=0."
    for item in editor.layout.explorer.sellist:
        if item.type == ':mf':
            compairframe = item
            break
    new_comp = comp.copy()

    if option == 0:
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        for compframe in compframes:
            for listframe in editor.layout.explorer.sellist:
                if compframe.name == listframe.name:
                    old_vtxs = compframe.vertices
                    if quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method1'] == "1":
                        newpos = old_vtxs[vertexlist[0]]
                    elif quarkx.setupsubset(SS_MODEL, "Options")['APVexs_Method2'] == "1":
                        newpos = compairframe.vertices[vertexlist[0]]
                    else:
                        newpos = old_vtxs[vertexlist[0]]
                    for vtx in vertexlist:
                        if vtx == vertexlist[0]:
                            continue
                        old_vtxs[vtx] = newpos
                        compframe.vertices = old_vtxs
            compframe.compparent = new_comp # To allow frame relocation after editing.
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        editor.ok(undo, undomsg)

    elif option == 1:
        tris = new_comp.triangles
        try:
            tex = comp.currentskin
            texWidth,texHeight = tex["Size"]
        except:
            texWidth,texHeight = view.clientarea

        if comp.currentskin is not None:
            newpos = vertexlist[0][0] + quarkx.vect(texWidth*.5, texHeight*.5, 0)
        else:
            newpos = vertexlist[0][0] + quarkx.vect(int((texWidth*.5) +.5), int((texHeight*.5) -.5), 0)

        for triindex in range(len(tris)):
            tri = tris[triindex]
            for item in vertexlist:
                if triindex == item[2]:
                    for j in range(len(tri)):
                        if j == item[3]:
                            if j == 0:
                                newtriangle = ((tri[j][0], int(newpos.tuple[0]), int(newpos.tuple[1])), tri[1], tri[2])
                            elif j == 1:
                                newtriangle = (tri[0], (tri[j][0], int(newpos.tuple[0]), int(newpos.tuple[1])), tri[2])
                            else:
                                newtriangle = (tri[0], tri[1], (tri[j][0], int(newpos.tuple[0]), int(newpos.tuple[1])))
                            tris[triindex] = newtriangle
        new_comp.triangles = tris
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        for compframe in compframes:
            compframe.compparent = new_comp # To allow frame relocation after editing.
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        editor.ok(undo, undomsg)

    elif option == 2:
        tris = new_comp.triangles
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        unusedvtxs = []
        for vtx in range(len(vertexlist)):
            if vtx == 0:
                continue
            unusedvtxs = unusedvtxs + [vertexlist[vtx]]
        newvertnumbers = []
        newvertoffset = 0
        old_vtxs = comp.currentframe.vertices
        for v in range(len(old_vtxs)):
            if v == vertexlist[0]:
                newindex = v + newvertoffset
            if v in unusedvtxs:
                newvertoffset = newvertoffset - 1
            newvertnumbers = newvertnumbers + [v + newvertoffset]
        for v in range(len(vertexlist)):
            newvertnumbers[vertexlist[v]] = newindex
        for triindex in range(len(tris)):
            tri = tris[triindex]
            newtriangle = ((newvertnumbers[tri[0][0]], tri[0][1], tri[0][2]), (newvertnumbers[tri[1][0]], tri[1][1], tri[1][2]), (newvertnumbers[tri[2][0]], tri[2][1], tri[2][2]))
            if newtriangle[0][0] == newtriangle[1][0] or newtriangle[1][0] == newtriangle[2][0] or newtriangle[2][0] == newtriangle[0][0]:
                quarkx.msgbox("Improper Selection!\n\nYou can not merge two\nvertexes of the same triangle.", MT_ERROR, MB_OK)
                return None, None
            tris[triindex] = newtriangle
        unusedvtxs.sort()
        unusedvtxs.reverse()
        vtxs = []
        for compframe in compframes:
            old_vtxs = compframe.vertices
            for index in range(len(unusedvtxs)):
                vtxs = old_vtxs[:unusedvtxs[index]] + old_vtxs[unusedvtxs[index]+1:]
                old_vtxs = vtxs

            compframe.vertices = vtxs
            compframe.compparent = new_comp # To allow frame relocation after editing.

        new_comp.triangles = tris
        if len(editor.ModelVertexSelList) > 2:
            undomsg = "merged " + str(len(editor.ModelVertexSelList)) + " vertexes"
        editor.ModelVertexSelList = []
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        make_tristodraw_dict(editor, new_comp)
        editor.ok(undo, undomsg)


#
# remove a vertex from a component
#
def removevertex(comp, index, all3=0):
    editor = mapeditor()
    if editor is None:
        return

    new_comp = comp.copy() # create a copy to edit (we store the old one in the undo list)
    tris = new_comp.triangles
    #### 1) find all triangles that use vertex 'index' and delete them.
    if all3 == 1:
        index = editor.ModelVertexSelList[0]
    toBeRemoved = findTriangles(comp, index)
    new_tris = []
    for tri in tris:
        p = checkinlist(tri, toBeRemoved)
        if (p==0):
            new_tris = new_tris + [ tri ]
    
    if all3 == 1:
        new_tris = []
        for tri in tris:
            if (editor.ModelVertexSelList[0] == tri[0][0]) and (editor.ModelVertexSelList[1] == tri[1][0]) and (editor.ModelVertexSelList[2] == tri[2][0]):
                index = editor.ModelVertexSelList[0]
                continue
            elif (editor.ModelVertexSelList[0] == tri[0][0]) and (editor.ModelVertexSelList[2] == tri[1][0]) and (editor.ModelVertexSelList[1] == tri[2][0]):
                index = editor.ModelVertexSelList[0]
                continue
            elif (editor.ModelVertexSelList[1] == tri[0][0]) and (editor.ModelVertexSelList[2] == tri[1][0]) and (editor.ModelVertexSelList[0] == tri[2][0]):
                index = editor.ModelVertexSelList[1]
                continue
            elif (editor.ModelVertexSelList[1] == tri[0][0]) and (editor.ModelVertexSelList[0] == tri[1][0]) and (editor.ModelVertexSelList[2] == tri[2][0]):
                index = editor.ModelVertexSelList[1]
                continue
            elif (editor.ModelVertexSelList[2] == tri[0][0]) and (editor.ModelVertexSelList[1] == tri[1][0]) and (editor.ModelVertexSelList[0] == tri[2][0]):
                index = editor.ModelVertexSelList[2]
                continue
            elif (editor.ModelVertexSelList[2] == tri[0][0]) and (editor.ModelVertexSelList[0] == tri[1][0]) and (editor.ModelVertexSelList[1] == tri[2][0]):
                index = editor.ModelVertexSelList[2]
                continue
            else:
                new_tris = new_tris + [ tri ]

    #### 2) loop through all frames and delete unused vertex(s).
    if all3 == 1:
        vertexestoremove = []
        for vertex in editor.ModelVertexSelList:
            vtxcount = 0
            for tri in tris:
                for vtx in tri:
                    if vtx[0] == vertex:
                        vtxcount = vtxcount + 1
            if vtxcount > 1:
                pass
            else:
                vertexestoremove = vertexestoremove + [vertex]
        compframes = new_comp.findallsubitems("", ':mf')   # find all frames
        for unusedvertex in vertexestoremove:
            unusedindex = unusedvertex
            for compframe in compframes: 
                old_vtxs = compframe.vertices
                vtxs = old_vtxs[:unusedindex]
                compframe.vertices = vtxs
                compframe.compparent = new_comp # To allow frame relocation after editing.
        new_tris = fixUpVertexNos(new_tris, index)
        new_comp.triangles = new_tris
    else:
        enew_tris = fixUpVertexNos(new_tris, index)
        new_comp.triangles = enew_tris
        compframes = new_comp.findallsubitems("", ':mf')   # find all frames
        for compframe in compframes: 
            old_vtxs = compframe.vertices
            vtxs = old_vtxs[:index] + old_vtxs[index+1:]
            compframe.vertices = vtxs
            compframe.compparent = new_comp # To allow frame relocation after editing.

    #### 3) re-build all views
    undo = quarkx.action()
    undo.exchange(comp, new_comp)
    if all3 == 1:
        make_tristodraw_dict(editor, new_comp)
        editor.ok(undo, "remove triangle")
        editor.ModelVertexSelList = []
    else:
        make_tristodraw_dict(editor, new_comp)
        editor.ok(undo, "remove vertex")
        editor.ModelVertexSelList = []


#
# Creates a new dictionary of vertex index keys with deleted ones removed
# and the old vertex key numbers corrected (updated).
#
def update_vertex_keys(Old_dictionary_list, vertices_to_remove):
    old_keys = Old_dictionary_list.keys() # List of 'bonevtxlist' keys as vertex_index integer items.
    NewVertexNumbers = []
    for vtx in range(len(old_keys)):
        if old_keys[vtx] in vertices_to_remove:
            # This vertex index is completely removed because it was combined with another, moved to another component or deleted.
            NewVertexNumbers = NewVertexNumbers + [-1]
        else:
            for remove in range(len(vertices_to_remove)):
                if vertices_to_remove[remove] > old_keys[vtx]:
                    NewVertexNumbers = NewVertexNumbers + [old_keys[vtx] - (remove)]
                    break
                if remove == len(vertices_to_remove)-1:
                    NewVertexNumbers = NewVertexNumbers + [old_keys[vtx] - len(vertices_to_remove)]
    # Now create the new dictionary list
    New_dictionary_list = {}
    for vtx in range(len(Old_dictionary_list)):
        if NewVertexNumbers[vtx] <> -1:
            New_dictionary_list[NewVertexNumbers[vtx]] = Old_dictionary_list[Old_dictionary_list.keys()[vtx]]
    return New_dictionary_list


#
# Creates a new list of vertex indexes with deleted ones removed
# and the old vertex numbers corrected (updated).
#
def update_vertex_list(Old_vtxlist, vertices_to_remove):
    New_vtxlist = []
    for vtx in range(len(Old_vtxlist)):
        if Old_vtxlist[vtx] in vertices_to_remove:
            continue
        else:
            for remove in range(len(vertices_to_remove)):
                if vertices_to_remove[remove] > Old_vtxlist[vtx]:
                    New_vtxlist = New_vtxlist + [Old_vtxlist[vtx] - remove]
                    break
                if remove == len(vertices_to_remove)-1:
                    New_vtxlist = New_vtxlist + [Old_vtxlist[vtx] - len(vertices_to_remove)]
    if New_vtxlist == []:
        return None
    return New_vtxlist


    
###############################
#
# Triangle & Face functions
#
###############################


#
# Add a triangle to a given component
#
def addtriangle(editor):
    comp = editor.Root.currentcomponent
    if (comp is None):
        return

    v1 = editor.ModelVertexSelList[0]
    v2 = editor.ModelVertexSelList[1]
    v3 = editor.ModelVertexSelList[2]

    from mdlhandles import SkinView1
    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
        for v in editor.layout.views:
            if v.info["viewname"] == "editors3Dview":
                cordsview = v
    else:

        try:
            tex = comp.currentskin
            texWidth,texHeight = tex["Size"]
            if quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] == "1":
                SkinViewScale = SkinView1.info["scale"]
            else:
                SkinViewScale = 1
        except:
            texWidth,texHeight = SkinView1.clientarea
            SkinViewScale = 1
    vertices = comp.currentframe.vertices
    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
        s1 = int(cordsview.proj(vertices[editor.ModelVertexSelList[0]]).tuple[0]*.025)
        t1 = -int(cordsview.proj(vertices[editor.ModelVertexSelList[0]]).tuple[1]*.025)
        s2 = int(cordsview.proj(vertices[editor.ModelVertexSelList[1]]).tuple[0]*.025)
        t2 = -int(cordsview.proj(vertices[editor.ModelVertexSelList[1]]).tuple[1]*.025)
        s3 = int(cordsview.proj(vertices[editor.ModelVertexSelList[2]]).tuple[0]*.025)
        t3 = -int(cordsview.proj(vertices[editor.ModelVertexSelList[2]]).tuple[1]*.025)
    else:
        s1 = int(vertices[editor.ModelVertexSelList[0]].tuple[0]+int(texWidth*.5)*SkinViewScale)
        t1 = int(vertices[editor.ModelVertexSelList[0]].tuple[1]-int(texHeight*.5)*SkinViewScale)
        s2 = int(vertices[editor.ModelVertexSelList[1]].tuple[0]+int(texWidth*.5)*SkinViewScale)
        t2 = int(vertices[editor.ModelVertexSelList[1]].tuple[1]-int(texHeight*.5)*SkinViewScale)
        s3 = int(vertices[editor.ModelVertexSelList[2]].tuple[0]+int(texWidth*.5)*SkinViewScale)
        t3 = int(vertices[editor.ModelVertexSelList[2]].tuple[1]-int(texHeight*.5)*SkinViewScale)

    if findTriangle(comp, v1, v2, v3) is not None:
        quarkx.msgbox("Improper Selection!\n\nA triangle using these 3 vertexes already exist.\n\nSelect at least one different vertex\nto make a new triangle with.\n\nTo 'Un-pick' a vertex from the 'Pick' list\nplace your cursor over that vertex,\nRMB click and select 'Pick Vertex'.\nThen you can pick another vertex to replace it.", MT_ERROR, MB_OK)
        return

    tris = comp.triangles

    tris = tris + [((v1,s1,t1),(v2,s2,t2),(v3,s3,t3))] # This is where the 'actual' texture positions s and t are needed to add to the triangles vertexes.

    new_comp = comp.copy()
    new_comp.triangles = tris
    new_comp.currentskin = editor.Root.currentcomponent.currentskin
    new_comp.currentframe = editor.Root.currentcomponent.currentframe
    compframes = new_comp.findallsubitems("", ':mf')   # get all frames
    for compframe in compframes:
        compframe.compparent = new_comp # To allow frame relocation after editing.
    undo = quarkx.action()
    undo.exchange(comp, new_comp)
    make_tristodraw_dict(editor, new_comp)
    editor.Root.currentcomponent = new_comp
    editor.ok(undo, "add triangle")
    if SkinView1 is not None:
        SkinView1.invalidate()


#
# Remove a triangle ,using its triangle index, from the current component
#
def removeTriangle(editor, comp, index):
    if (index is None):
        return
    todo = quarkx.msgbox("Do you also want to\nremove the 3 vertexes?",MT_CONFIRMATION, MB_YES_NO_CANCEL)
    if todo == MR_CANCEL:
        return
    if todo == MR_YES:
        vertexestoremove = []
        for vertex in editor.ModelVertexSelList:
            vtxcount = 0
            tris = comp.triangles
            for tri in tris:
                for vtx in tri:
                    if vtx[0] == vertex:
                        vtxcount = vtxcount + 1
            if vtxcount > 1:
                pass
            else:
                vertexestoremove = vertexestoremove + [vertex]
        if len(vertexestoremove) == 0:
            pass
        else:
            removevertex(comp, index, 1)
            return
    new_comp = comp.copy()
    old_tris = new_comp.triangles
    tris = old_tris[:index] + old_tris[index+1:]
    new_comp.triangles = tris
    compframes = new_comp.findallsubitems("", ':mf')   # get all frames
    for compframe in compframes:
        compframe.compparent = new_comp # To allow frame relocation after editing.
    undo = quarkx.action()
    undo.exchange(comp, new_comp)
    make_tristodraw_dict(editor, new_comp)
    editor.ok(undo, "remove triangle")


#
# Remove a triangle ,using its vertexes, from the current component
#
def removeTriangle_v3(editor):
    comp = editor.Root.currentcomponent
    v1 = editor.ModelVertexSelList[0]
    v2 = editor.ModelVertexSelList[1]
    v3 = editor.ModelVertexSelList[2]
    removeTriangle(editor, comp, findTriangle(comp, v1,v2,v3))


#
# The 'option' value of 1 COPIES the currently selected faces of a component to another component (that is not Hidden).
# The 'option' value of 2 MOVES the currently selected faces of a component to another component (that is not Hidden).
# This function will also remove the selected faces and unused vertexes from the original component.
# The 'option' value of 3 DELETES the currently selected faces of a component.
# This function will also remove any unused vertexes of those faces from that component.
#
def movefaces(editor, movetocomponent, option=2):
    comp = editor.Root.currentcomponent

    # This section does a selection test and gives an error message box if needed.
    for item in editor.layout.explorer.sellist:
        if item.parent.parent.name != comp.name:
            quarkx.msgbox("IMPROPER SELECTION !\n\nYou need to select a frame && faces from\none component to move them to another component.\n\nYou have selected items that are not\npart of the ''"+editor.Root.currentcomponent.shortname+"'' Frames group.\nPlease un-select these items.\n\nAction Canceled.", MT_ERROR, MB_OK)
            return

    # These are things that we need to setup first for use later on.
    temp_list = []
    remove_triangle_list = []
    vertices_to_remove = []

    # Now we start creating our data copies to work with and the final "ok" swapping function at the end.
    tris = comp.triangles
    change_comp = comp.copy()
    if option < 3:
        new_comp = editor.Root.dictitems[movetocomponent + ':mc'].copy()
        # Component copy's still need to have their currentskin set.
        new_comp.currentskin = editor.Root.dictitems[movetocomponent + ':mc'].currentskin

    # This section creates the "remove_triangle_list" from the ModelFaceSelList which is already
    #    in ascending numerical order but may have duplicate tri_index numbers that need to be removed.
    # The order also needs to be descending so when triangles are removed from another list it
    #    does not select an improper triangle due to list items shifting forward numerically.
    # The "remove_triangle_list" is used to re-create the current component.triangles and new_comp.triangles.
    for tri_index in reversed(editor.ModelFaceSelList):
        if tri_index in remove_triangle_list:
            pass
        else:
            remove_triangle_list = remove_triangle_list + [tri_index]

    # This section creates the "vertices_to_remove" to be used
    #    to re-create the current component's frame.vertices.
    # It also skips over any duplicated vertex_index numbers of the triangles to be moved
    #    to the new_comp and\or removed from the original component if 'option' calls to.
    for tri_index in remove_triangle_list:
        for vtx in range(len(tris[tri_index])):
            if tris[tri_index][vtx][0] in temp_list:
                pass
            else:
                temp_list.append(tris[tri_index][vtx][0])

    # This section sorts the "vertices_to_remove" numerically in ascending order then
    # recreates it in descending order for the same reason that the triangles above were done.
    temp_list.sort()
    for item in reversed(temp_list):
        vertices_to_remove.append(item)

    ###### NEW COMPONENT SECTION ######
    if option < 3:

    # This first part adds the new triangles, which are the ones that have been selected,
    #    to the "moveto" new_comp.triangles using the "remove_triangle_list" which are also
    #    the same ones to be removed from the original component if 'option' calls to.
        newtris = []
        for tri_index in range(len(remove_triangle_list)):
            newtris = newtris + [comp.triangles[remove_triangle_list[tri_index]]]

    # This second part adds the NEW vertices to end of each frames "frame.vertices"
    #    to construct the new triangles that are being added just below this section.
        nbr_of_new_comp_vtxs_before_adding = len(new_comp.dictitems['Frames:fg'].subitems[0].vertices)
        for frame in range(len(comp.dictitems['Frames:fg'].subitems)):
            try: # To avoid error in case one component has more frames then the other.
                newframe_vertices = new_comp.dictitems['Frames:fg'].subitems[frame].vertices
                for vert_index in range(len(vertices_to_remove)):
                    newframe_vertices = newframe_vertices + [comp.dictitems['Frames:fg'].subitems[frame].vertices[vertices_to_remove[vert_index]]]
                new_comp.dictitems['Frames:fg'].subitems[frame].vertices = newframe_vertices
            except:
                break

    # This third part fixes up the 'new_comp.triangles', NEW triangles vertex index numbers
    #    to coordinate with those frame.vertices lists updated above.
        temptris = []
        for tri in range(len(newtris)):
            for index in range(len(newtris[tri])):
                for vert_index in range(len(vertices_to_remove)):
                    if newtris[tri][index][0] == vertices_to_remove[vert_index]:
                        if index == 0:
                            tri0 = (nbr_of_new_comp_vtxs_before_adding + vert_index, newtris[tri][index][1], newtris[tri][index][2])
                            break
                        elif index == 1:
                            tri1 = (nbr_of_new_comp_vtxs_before_adding + vert_index, newtris[tri][index][1], newtris[tri][index][2])
                            break
                        else:
                            tri2 = (nbr_of_new_comp_vtxs_before_adding + vert_index, newtris[tri][index][1], newtris[tri][index][2])
                            temptris = temptris + [(tri0, tri1, tri2)]
                            break
        new_comp.triangles = new_comp.triangles + temptris

    # This last part updates the "moveto" component finishing the process for that.
        undo = quarkx.action()
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        for compframe in compframes:
            compframe.compparent = new_comp # To allow frame relocation after editing.
        undo = quarkx.action()
        # Clear these list to avoid errors.
        editor.ModelFaceSelList = []
        editor.EditorObjectList = []
        editor.Root.currentcomponent = new_comp
        undo.exchange(editor.Root.dictitems[movetocomponent + ':mc'], None)
        undo.put(editor.Root, new_comp)
        # Updates the editor.ModelComponentList 'tristodraw', for this component. This needs to be done for each component or bones will not work if used in the editor.
        make_tristodraw_dict(editor, new_comp)
        if option == 1:
            editor.ok(undo, "faces copied to " + new_comp.shortname)
        else:
            editor.ok(undo, "faces moved to " + new_comp.shortname)

    ###### ORIGINAL COMPONENT SECTION ######
    if option > 1:

    # This section checks and takes out, from the vertices_to_remove, any vert_index that is being used by a
    #    triangle that is not being removed, in the remove_triangle_list, to avoid any invalid triangle errors.
        dumylist = vertices_to_remove
        for tri in range(len(change_comp.triangles)):
            if tri in remove_triangle_list:
                continue
            else:
                for vtx in range(len(change_comp.triangles[tri])):
                    if change_comp.triangles[tri][vtx][0] in dumylist:
                        dumylist.remove(change_comp.triangles[tri][vtx][0])
        vertices_to_remove = dumylist

    # This section uses the "remove_triangle_list" to recreate the original
    #    component.triangles without the selected faces.
        old_tris = change_comp.triangles
        remove_triangle_list.sort()
        remove_triangle_list = reversed(remove_triangle_list)
        for index in remove_triangle_list:
            old_tris = old_tris[:index] + old_tris[index+1:]
        change_comp.triangles = old_tris

    # This section uses the "vertices_to_remove" to recreate the
    #    original component's frames without any unused vertexes.
        new_tris = change_comp.triangles
        compframes = change_comp.findallsubitems("", ':mf')   # find all frames
        for index in vertices_to_remove:
            enew_tris = fixUpVertexNos(new_tris, index)
            new_tris = enew_tris
            for compframe in compframes: 
                old_vtxs = compframe.vertices
                vtxs = old_vtxs[:index] + old_vtxs[index+1:]
                compframe.vertices = vtxs
        change_comp.triangles = new_tris

    # This updates the original component finishing the process for that.
        vertices_to_remove.sort()
        compframes = change_comp.findallsubitems("", ':mf')   # get all frames
        for compframe in compframes:
            compframe.compparent = change_comp # To allow frame relocation after editing.
        editor.Root.currentcomponent = change_comp
        editor.Root.currentcomponent.currentskin = comp.currentskin
        undo = quarkx.action()
        undo.exchange(comp, None)
        undo.put(editor.Root, change_comp)
        # Updates the editor.ModelComponentList 'tristodraw', for this component. This needs to be done for each component or bones will not work if used in the editor.
        make_tristodraw_dict(editor, change_comp)
        if option == 2:
            editor.ok(undo, "faces moved from " + change_comp.shortname)
        else:
            editor.ok(undo, "faces deleted from " + change_comp.shortname)
        # Updates the editor.ModelComponentList, for this component, 'bonevtxlist' and 'colorvtxlist' if one or both exist. 
        if len(vertices_to_remove) != 0:
            if editor.ModelComponentList[change_comp.name]['bonevtxlist'] != {}:
                update_bonevtxlist(editor, change_comp, vertices_to_remove)
            if editor.ModelComponentList[change_comp.name]['colorvtxlist'] != {}:
                update_colorvtxlist(editor, change_comp, vertices_to_remove)



###############################
#
# Conversion and Poly functions
#
###############################


#
# Returns the correct frame_name needed.
#
def GetFrameName(editor):
    Root = editor.Root
    explorer = editor.layout.explorer
    try:
        frame_name = editor.Root.currentcomponent.currentframe.name
    except:
        frame_name = editor.Root.currentcomponent.dictitems['Frames:fg'].subitems[0].name
    if explorer.uniquesel is not None:
        if explorer.uniquesel.type == ":mf":
            frame_name = explorer.uniquesel.name
        elif explorer.uniquesel.type == ":mc":
            if explorer.uniquesel.currentframe is None:
                frame = explorer.uniquesel.dictitems['Frames:fg'].subitems[0]
                explorer.uniquesel.currentframe = frame
                frame_name = frame.name
            else:
                frame_name = explorer.uniquesel.currentframe.name
    elif len(explorer.sellist) > 1:
        if explorer.sellist[0].type == ":mf":
            frame_name = explorer.sellist[0].name
        elif explorer.sellist[1].type == ":mf":
            frame_name = explorer.sellist[1].name

    return frame_name


#
# Returns the correct frame_name needed for the editor.ModelComponentList['bonelist'].
#
def GetBonelistFrameName(editor, frame_name, bones, bonename, comp):
    bonelist_frame_name = None

    for bone in bones:
        if bonename == bone.name:
            comp_name = bone.dictspec['component']
            try:
                comp2 = editor.Root.dictitems[comp_name]
                comp_frames = comp2.dictitems['Frames:fg'].subitems
                c_frames = comp.dictitems['Frames:fg'].subitems
                frame_index = None
                for f in range(len(c_frames)):
                    if frame_name == c_frames[f].name:
                        frame_index = f
                        break
                if frame_index is not None and frame_index < len(comp_frames):
                    bonelist_frame_name = comp_frames[frame_index].name
                    break
            except:
                break

    return bonelist_frame_name


#
# Update the editor.ModelComponentList['bboxlist'] for a poly bbox (hit box) at the end of a drag,
# depending on what they are assigned to like a bone or a component's vertexes or something else.
#
def UpdateBBoxList(editor, newpoly, count=None):
    Root = editor.Root
    frame_name = GetFrameName(editor)
    assigned2 = newpoly.dictspec["assigned2"]
    bboxlist = editor.ModelComponentList['bboxlist']
    if assigned2 == "None": # MIGHT want to save this anyway to
        pass                # editor.ModelComponentList['bboxlist'][poly.name]
                            # to be stored in our .qkl model work files.
    elif assigned2.endswith(":bone"):
        # Set things up that we'll need.
        comp = Root.currentcomponent
        skelgroup = Root.dictitems['Skeleton:bg']
        bones = skelgroup.findallsubitems("", ':bone')
        bonelist = editor.ModelComponentList['bonelist']

        if bonelist.has_key(assigned2):
            bonename = assigned2
        else:
            quarkx.msgbox("Bounding Box " + newpoly.shortname + "\nassigned to " + assigned2 + "\n\nBut a data conflict exist causing this error.\nDelete, remake and assign the Bounding Box.", MT_ERROR, MB_OK)
            return
        keys = bonelist[bonename]['frames'].keys()
        if not frame_name in keys:
            bonelist_frame_name = GetBonelistFrameName(editor, frame_name, bones, bonename, comp)
        else:
            bonelist_frame_name = frame_name

        # Updates the bboxlist.
        poly = quarkx.newobj("dummy:p");
        poly['show'] = (1.0,)
        bone_data = bonelist[bonename]
        if not bboxlist.has_key(newpoly.name):
            bpos = quarkx.vect(bone_data['frames'][bonelist_frame_name]['position'])
            brot = quarkx.matrix(bone_data['frames'][bonelist_frame_name]['rotmatrix'])
            poly.shortname = newpoly.shortname
            poly['assigned2'] = bonename
        else:
            bpos = quarkx.vect(bone_data['frames'][bonelist_frame_name]['position'])
            brot = ~quarkx.matrix(bone_data['frames'][bonelist_frame_name]['rotmatrix'])
            if count is None:
                parent = editor.Root.dictitems['Misc:mg']
                polys = parent.findallsubitems("", ':p')
                poly_names = []
                for p in polys:
                    if p.shortname.startswith("bbox "):
                        poly_names = poly_names + [p.shortname]
                count = 1
                while 1:
                    name = "bbox " + str(count)
                    if name in poly_names:
                        count = count + 1
                    else:
                        break
            poly.shortname = "bbox " + str(count)

        polykeys = []
        for f in newpoly.subitems:
            polykeys = polykeys + [f.name]
        for f in polykeys:
            face = quarkx.newobj(f)
            vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z = newpoly.dictitems[f].dictspec["v"]
            if not bboxlist.has_key(newpoly.name):
                vtx0 = quarkx.vect(vtx0X, vtx0Y, vtx0Z).tuple
                vtx1 = quarkx.vect(vtx1X, vtx1Y, vtx1Z).tuple
                vtx2 = quarkx.vect(vtx2X, vtx2Y, vtx2Z).tuple
            else:
                vtx0 = (brot * (quarkx.vect(vtx0X, vtx0Y, vtx0Z) - bpos)).tuple
                vtx1 = (brot * (quarkx.vect(vtx1X, vtx1Y, vtx1Z) - bpos)).tuple
                vtx2 = (brot * (quarkx.vect(vtx2X, vtx2Y, vtx2Z) - bpos)).tuple
            vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
            vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
            vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
            face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
            face["tex"] = None
            poly.appenditem(face)

        bbox = quarkx.boundingboxof([poly])
        if not bboxlist.has_key(newpoly.name):
            bboxlist[newpoly.name] = {}
        bboxlist[newpoly.name]['size'] = [bbox[0].tuple, bbox[1].tuple]

        return poly # DO NOT move outside to combine calls, will break dragging of poly in editor.

    elif assigned2.endswith(":mc"):
        # Set things up that we'll need.
        bboxlist = editor.ModelComponentList['bboxlist']

        # Updates the bboxlist.
        poly = newpoly
        bbox = quarkx.boundingboxof([poly])
        if not bboxlist.has_key(poly.name):
            bboxlist[poly.name] = {}
            bboxlist[poly.name]['size'] = []
        if bboxlist[poly.name].has_key('size'):
            bboxlist[poly.name]['size'] = [bbox[0].tuple, bbox[1].tuple]
        elif bboxlist[poly.name].has_key('vtx_list'):
            pass # bbox drag can not change the bboxlist for this key. Just here for ref.
        elif bboxlist[poly.name].has_key('frames'):
            pass # bbox drag can not change the bboxlist for this key. Just here for ref.

        return poly # DO NOT move outside to combine calls, will break dragging of poly in editor.


#
# Update the poly bboxes (hit boxes if any) when switching frames, like during animation.
#
def UpdateBBoxPoly(poly, bpos, brot, bbox):
    m = bbox[0]
    M = bbox[1]
    polykeys = []
    for p in poly.subitems:
        polykeys = polykeys + [p.name]
    for f in polykeys:
        if f == "north:f": # BACK FACE
            poly.removeitem(poly.dictitems[f])
            face = quarkx.newobj("north:f")
            vtx0 = (bpos + (brot * quarkx.vect(m[0],M[1],M[2]))).tuple
            vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
            vtx1 = (bpos + (brot * quarkx.vect(M[0],M[1],M[2]))).tuple
            vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
            vtx2 = (bpos + (brot * quarkx.vect(m[0],M[1],m[2]))).tuple
            vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
            face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
            face["tex"] = None
            poly.appenditem(face)

        elif f == "east:f": # RIGHT FACE
            poly.removeitem(poly.dictitems[f])
            face = quarkx.newobj("east:f")
            vtx0 = (bpos + (brot * quarkx.vect(M[0],M[1],M[2]))).tuple
            vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
            vtx1 = (bpos + (brot * quarkx.vect(M[0],m[1],M[2]))).tuple
            vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
            vtx2 = (bpos + (brot * quarkx.vect(M[0],M[1],m[2]))).tuple
            vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
            face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
            face["tex"] = None
            poly.appenditem(face)

        elif f == "south:f": # FRONT FACE
            poly.removeitem(poly.dictitems[f])
            face = quarkx.newobj("south:f")
            vtx0 = (bpos + (brot * quarkx.vect(M[0],m[1],M[2]))).tuple
            vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
            vtx1 = (bpos + (brot * quarkx.vect(m[0],m[1],M[2]))).tuple
            vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
            vtx2 = (bpos + (brot * quarkx.vect(M[0],m[1],m[2]))).tuple
            vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
            face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
            face["tex"] = None
            poly.appenditem(face)

        elif f == "west:f": # LEFT FACE
            poly.removeitem(poly.dictitems[f])
            face = quarkx.newobj("west:f")
            vtx0 = (bpos + (brot * quarkx.vect(m[0],m[1],M[2]))).tuple
            vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
            vtx1 = (bpos + (brot * quarkx.vect(m[0],M[1],M[2]))).tuple
            vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
            vtx2 = (bpos + (brot * quarkx.vect(m[0],m[1],m[2]))).tuple
            vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
            face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
            face["tex"] = None
            poly.appenditem(face)

        elif f == "up:f": # TOP FACE
            poly.removeitem(poly.dictitems[f])
            face = quarkx.newobj("up:f")
            vtx0 = (bpos + (brot * quarkx.vect(m[0],M[1],M[2]))).tuple
            vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
            vtx1 = (bpos + (brot * quarkx.vect(m[0],m[1],M[2]))).tuple
            vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
            vtx2 = (bpos + (brot * quarkx.vect(M[0],M[1],M[2]))).tuple
            vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
            face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
            face["tex"] = None
            poly.appenditem(face)

        elif f == "down:f": # BOTTOM FACE
            poly.removeitem(poly.dictitems[f])
            face = quarkx.newobj("down:f")
            vtx0 = (bpos + (brot * quarkx.vect(m[0],M[1],m[2]))).tuple
            vtx0X, vtx0Y, vtx0Z = vtx0[0], vtx0[1], vtx0[2]
            vtx1 = (bpos + (brot * quarkx.vect(M[0],M[1],m[2]))).tuple
            vtx1X, vtx1Y, vtx1Z = vtx1[0], vtx1[1], vtx1[2]
            vtx2 = (bpos + (brot * quarkx.vect(m[0],m[1],m[2]))).tuple
            vtx2X, vtx2Y, vtx2Z = vtx2[0], vtx2[1], vtx2[2]
            face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
            face["tex"] = None
            poly.appenditem(face)

    try: # In case a previous QuArK.exe is used before adding the function call below.
        poly.changedfaces() # Makes the Delphi code add + sign to poly without going through undo code.
    except:
        pass

#
# Updates the poly bboxes (hit boxes if any) and editor explorer.
#
def DrawBBoxes(editor, explorer, comp):
            Root = editor.Root
            miscgroup = Root.dictitems['Misc:mg']
            polys = miscgroup.findallsubitems("", ':p')
            if len(polys) != 0:
                frame_name = GetFrameName(editor)

                # Set things up that we'll probably need.
                skelgroup = Root.dictitems['Skeleton:bg']
                bones = skelgroup.findallsubitems("", ':bone')
                bonelist = editor.ModelComponentList['bonelist']
                bboxlist = editor.ModelComponentList['bboxlist']
                bone_names = bonelist.keys()
                found_frame = None

                # Process all polys, first see what they are assigned to, if anything.
                for poly in polys:
                    assigned2 = poly.dictspec["assigned2"]
                    if assigned2 == "None": # MIGHT want to save these anyway to
                        continue            # editor.ModelComponentList['bboxlist'][poly.name]
                                            # to be stored in our .qkl model work files.
                    elif assigned2.endswith(":bone"):
                        bonename = assigned2
                        if bonelist.has_key(bonename) and bboxlist.has_key(poly.name):
                            pass
                        else:
                            continue
                        keys = bonelist[bonename]['frames'].keys()
                        if not frame_name in keys:
                            bonelist_frame_name = GetBonelistFrameName(editor, frame_name, bones, bonename, comp)
                        else:
                            bonelist_frame_name = frame_name

                        # Updates the poly as needed.
                        if bonelist_frame_name is not None:
                            bone_data = bonelist[bonename]
                            try:
                                bpos = quarkx.vect(bone_data['frames'][bonelist_frame_name]['position'])
                            except:
                                continue
                            brot = quarkx.matrix(bone_data['frames'][bonelist_frame_name]['rotmatrix'])
                            bbox = bboxlist[poly.name]['size']
                            UpdateBBoxPoly(poly, bpos, brot, bbox)
                            found_frame = 1
                    elif assigned2.endswith(":mc"):
                        if bboxlist.has_key(poly.name):
                            pass
                        else:
                            continue
                        found_dict = None
                        if bboxlist[poly.name].has_key('size'):
                            bpos = quarkx.vect(0.,0.,0.)
                            brot = quarkx.matrix((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
                            frame_index = Root.currentcomponent.dictitems['Frames:fg'].dictitems[frame_name].index
                            try:
                                frame_verts = Root.dictitems[assigned2].dictitems['Frames:fg'].subitems[frame_index].vertices
                            except:
                                continue
                            bbox = quarkx.boundingboxof(frame_verts)
                            bbox = [bbox[0].tuple, bbox[1].tuple]
                            UpdateBBoxPoly(poly, bpos, brot, bbox)
                        elif bboxlist[poly.name].has_key('vtx_list'):
                            bpos = quarkx.vect(0.,0.,0.)
                            brot = quarkx.matrix((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
                            frame_verts = []
                            frame_index = Root.currentcomponent.dictitems['Frames:fg'].dictitems[frame_name].index
                            try:
                                vertices = Root.dictitems[assigned2].dictitems['Frames:fg'].subitems[frame_index].vertices
                            except:
                                continue
                            for vtx_index in bboxlist[poly.name]['vtx_list']:
                                frame_verts = frame_verts + [vertices[vtx_index]]
                            bbox = quarkx.boundingboxof(frame_verts)
                            bbox = [bbox[0].tuple, bbox[1].tuple]
                            UpdateBBoxPoly(poly, bpos, brot, bbox)
                        elif bboxlist[poly.name].has_key('frames'):
                            pass # still needs to be setup

#
# Creates a QuArK Internal Group Object which consist of QuArK internal Poly Objects
# created from each selected vertex in the
# option=0 uses the ModelVertexSelList for the editor and
# option=1 uses the SkinVertexSelList for the Skin-view
# that can be manipulated by some function using QuArK Internal Poly Objects
# such as the Linear Handle functions.
# "otherlist" does NOT apply for the Skin-view, only the editor and it will
# use the list supplied and not the default ModelVertexSelList list above.
#
def MakeEditorVertexPolyObject(editor, option=0, otherlist=None, name=None):
    "Creates a QuArK Internal Group Object of Poly Objects for vertex drags."
    from qbaseeditor import currentview

    if editor.Root.currentcomponent is None:
        componentnames = []
        for item in editor.Root.dictitems:
            if item.endswith(":mc"):
                componentnames.append(item)
        componentnames.sort()
        comp = editor.Root.dictitems[componentnames[0]]
    else:
        comp = editor.Root.currentcomponent

    currentskin = comp.currentskin
    if currentskin is not None:
        skinname = currentskin.shortname
    else:
        skinname = "None"
        
    if option == 0:
        if editor.ModelVertexSelList == [] and otherlist is None:
            return []
        elif otherlist is not None:
            VertexList = otherlist
        else:
            VertexList = editor.ModelVertexSelList

        scale = currentview.info["scale"]*2
        polylist = []
        if name is None:
            group = quarkx.newobj("selected:g");
        else:
            if name.find(":mc-b-") != -1:
                thiscomp = name.split("-b-")[0]
                comp = editor.Root.dictitems[thiscomp]
            group = quarkx.newobj(name + ":g");
        if comp.currentframe is None:
            return []
        else:
            vertices = comp.currentframe.vertices
        for vtx in range (len(vertices)):
            for ver_index in range (len(VertexList)):
                if vtx == VertexList[ver_index]:
                    vertex = vertices[vtx]
                    p = quarkx.newobj(str(vtx)+":p");
                    face = quarkx.newobj("east:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(1.0,0.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(1.0,0.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("west:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(-1.0,0.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(-1.0,-1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(-1.0,0.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("north:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,1.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(-1.0,1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,1.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("south:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,-1.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,-1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,-1.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("up:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,0.0,1.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,0.0,1.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,1.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("down:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,0.0,-1.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,0.0,-1.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,-1.0,-1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    group.appenditem(p)

        polylist = polylist + [group]
        return polylist
    
    if option == 1:
        from mdlhandles import SkinView1
        import mdlhandles
        scale = SkinView1.info["scale"]*2
        VertexList = editor.SkinVertexSelList
        polylist = []
        group = quarkx.newobj("selected:g");
        for vtx in range (len(SkinView1.handles)):
            if (isinstance(SkinView1.handles[vtx], mdlhandles.LinRedHandle)) or (isinstance(SkinView1.handles[vtx], mdlhandles.LinSideHandle)) or (isinstance(SkinView1.handles[vtx], mdlhandles.LinCornerHandle)):
                continue
            for handle in range (len(VertexList)):
                tri_index = int(VertexList[handle][2])
                ver_index = int(VertexList[handle][3])
                handlevtx = (tri_index * 3) + ver_index
                if vtx == handlevtx:
                    vertex = SkinView1.handles[vtx].pos
                    p = quarkx.newobj(str(tri_index)+","+str(ver_index)+":p");
                    face = quarkx.newobj("east:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(1.0,0.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(1.0,0.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("west:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(-1.0,0.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(-1.0,-1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(-1.0,0.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("north:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,1.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(-1.0,1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,1.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("south:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,-1.0,0.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,-1.0,0.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,-1.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("up:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,0.0,1.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,0.0,1.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,1.0,1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    face = quarkx.newobj("down:f")
                    vtx0X, vtx0Y, vtx0Z = (vertex + quarkx.vect(0.0,0.0,-1.0)/scale).tuple
                    vtx1X, vtx1Y, vtx1Z = (vertex + quarkx.vect(1.0,0.0,-1.0)/scale).tuple
                    vtx2X, vtx2Y, vtx2Z = (vertex + quarkx.vect(0.0,-1.0,-1.0)/scale).tuple
                    face["v"] = (vtx0X, vtx0Y, vtx0Z, vtx1X, vtx1Y, vtx1Z, vtx2X, vtx2Y, vtx2Z)
                    face["tex"] = skinname
                    p.appenditem(face)
                    group.appenditem(p)

        polylist = polylist + [group]
        return polylist

# For the Linear Handles New Method of drag lines and movement.
# option=0 for the Editor, called from mdlhandles.py class LinRedHandle, ok function.
# option=1 for the Skin-view.
# option=2 for the Editor, called from mdlhandles.py class LinRedHandle, ok function
#   and is for the editor's selected vertexes extrusion functions of that handle.
# option=3 for the Editor, called from mdlhandles.py class LinCornerHandle and LinSideHandle, ok functions.
#
def UpdateFramesVertexes(editor, delta, view, undomsg, option=0):
    if option == 0:
        undo = quarkx.action()
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        for item in editor.layout.explorer.sellist:
            if item.type == ":mf":
                compframe = new_comp.dictitems['Frames:fg'].dictitems[item.name]
                old_vtxs = compframe.vertices
                for vtx_index in editor.ModelVertexSelList:
                    vertex = old_vtxs[vtx_index]
                    old_vtxs[vtx_index] = vertex + delta
                compframe.vertices = old_vtxs
                compframe.compparent = new_comp # To allow frame relocation after editing.
        undo.exchange(comp, new_comp)
        editor.ok(undo, undomsg)

    if option == 2:
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        newtris = new_comp.triangles
        newtri_index = len(comp.triangles)
        newvertexselection = []
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        currentvertices = len(compframes[0].vertices)
        for compframe in range(len(compframes)):
            if compframes[compframe].name == comp.currentframe.name:
                current = compframe
                break
        for vtx_index in range(len(editor.ModelVertexSelList)):
            old_vtxs = compframes[current].vertices
            vtxnbr = editor.ModelVertexSelList[vtx_index]
            newver_index = currentvertices + vtx_index
            newvertexselection = newvertexselection + [newver_index]
            for compframe in compframes:
                old_vtxs = compframe.vertices
                newvertex = old_vtxs[vtxnbr] + delta
                old_vtxs = old_vtxs + [newvertex]
                compframe.vertices = old_vtxs
                compframe.compparent = new_comp # To allow frame relocation after editing.

        from mdlhandles import SkinView1
        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
            for v in editor.layout.views:
                if v.info["viewname"] == "editors3Dview":
                    cordsview = v
        else:
            try:
                tex = comp.currentskin
                texWidth,texHeight = tex["Size"]
                if quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] == "1":
                    SkinViewScale = SkinView1.info["scale"]
                else:
                    SkinViewScale = 1
            except:
                texWidth,texHeight = SkinView1.clientarea
                SkinViewScale = 1
        for tri in editor.SelCommonTriangles:
            if len(tri) == 3:
                oldtri, oldver1 ,oldver0 = tri
            else:
                oldtri, oldver1 ,oldver0 ,oldver2 = tri
            for vtx_index in range(len(editor.ModelVertexSelList)):
                if editor.ModelVertexSelList[vtx_index] == oldver1:
                    newver_index0 = currentvertices + vtx_index
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        newuv0u = int(cordsview.proj(compframes[current].vertices[newver_index0]).tuple[0])
                        newuv0v = int(cordsview.proj(compframes[current].vertices[newver_index0]).tuple[1])
                        olduv0u = int(cordsview.proj(compframes[current].vertices[oldver0]).tuple[0])
                        olduv0v = int(cordsview.proj(compframes[current].vertices[oldver0]).tuple[1])
                    else:
                        newuv0u = int(compframes[current].vertices[newver_index0].tuple[0]-int(texWidth*.5))*SkinViewScale
                        newuv0v = int(compframes[current].vertices[newver_index0].tuple[1]-int(texHeight*.5))*SkinViewScale
                        olduv0u = int(compframes[current].vertices[oldver0].tuple[0]+int(texWidth*.5))*SkinViewScale
                        olduv0v = int(compframes[current].vertices[oldver0].tuple[1]+int(texHeight*.5))*SkinViewScale
                if editor.ModelVertexSelList[vtx_index] == oldver0:
                    newver_index1 = currentvertices + vtx_index
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        newuv1u = int(cordsview.proj(compframes[current].vertices[newver_index1]).tuple[0])
                        newuv1v = int(cordsview.proj(compframes[current].vertices[newver_index1]).tuple[1])
                        olduv1u = int(cordsview.proj(compframes[current].vertices[oldver1]).tuple[0])
                        olduv1v = int(cordsview.proj(compframes[current].vertices[oldver1]).tuple[1])
                    else:
                        newuv1u = int(compframes[current].vertices[newver_index1].tuple[0]+int(texWidth*.5))*SkinViewScale
                        newuv1v = int(compframes[current].vertices[newver_index1].tuple[1]-int(texHeight*.5))*SkinViewScale
                        olduv1u = int(compframes[current].vertices[oldver1].tuple[0]-int(texWidth*.5))*SkinViewScale
                        olduv1v = int(compframes[current].vertices[oldver1].tuple[1]+int(texHeight*.5))*SkinViewScale
                if len(tri) == 4:
                    if editor.ModelVertexSelList[vtx_index] == oldver2:
                        newver_index2 = currentvertices + vtx_index
                        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                            newuv2u = int(cordsview.proj(compframes[current].vertices[newver_index2]).tuple[0])
                            newuv2v = int(cordsview.proj(compframes[current].vertices[newver_index2]).tuple[1])
                            olduv2u = int(cordsview.proj(compframes[current].vertices[oldver2]).tuple[0])
                            olduv2v = int(cordsview.proj(compframes[current].vertices[oldver2]).tuple[1])
                        else:
                            newuv2u = int(compframes[current].vertices[newver_index2].tuple[0]+int(texWidth*.5))*SkinViewScale
                            newuv2v = int(compframes[current].vertices[newver_index2].tuple[1]-int(texHeight*.5))*SkinViewScale
                            olduv2u = int(compframes[current].vertices[oldver2].tuple[0]-int(texWidth*.5))*SkinViewScale
                            olduv2v = int(compframes[current].vertices[oldver2].tuple[1]+int(texHeight*.5))*SkinViewScale

            newtris = newtris + [((newver_index0, newuv0u, newuv0v), (newver_index1, newuv1u, newuv1v), (oldver0, olduv0u, olduv0v))]
            newtris = newtris + [((newver_index0, newuv0u, newuv0v), (oldver0, olduv0u, olduv0v), (oldver1, olduv1u, olduv1v))]
        new_comp.triangles = newtris

        if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
            undomsg = "editor-linear all edges extrusion"
        else:
            undomsg = "editor-linear outside edges extrusion"

        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        make_tristodraw_dict(editor, new_comp)
        editor.ok(undo, undomsg)
        editor.ModelVertexSelList = newvertexselection

    if option == 3:
        undo = quarkx.action()
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        for item in editor.layout.explorer.sellist:
            if item.type == ":mf":
                compframe = new_comp.dictitems['Frames:fg'].dictitems[item.name]
                old_vtxs = compframe.vertices
                for vtx_index in editor.ModelVertexSelList:
                    old_vtxs[vtx_index] = delta[vtx_index]
                compframe.vertices = old_vtxs
                compframe.compparent = new_comp # To allow frame relocation after editing.
        undo.exchange(comp, new_comp)
        editor.ok(undo, undomsg)
                

#
# Does the opposite of the 'MakeEditorVertexPolyObject' (just above this function) to convert a list
#   of a group of polys that have been manipulated by some function using QuArK Internal Poly Objects.
# The 'new' objects list in the functions 'ok' section is passed to here where it is converted back to
# usable model component mesh vertexes and the final 'ok' function is performed.
# option=0 does the conversion for the Editor.
# option=1 does the conversion for the Skin-view.
# option=2, called from mdlhandles.py class LinRedHandle, ok function
#   is for the editor's selected edges vertexes extrusion function.
#
def ConvertVertexPolyObject(editor, newobjectslist, flags, view, undomsg, option=0):
    "Does the opposite of the 'MakeEditorVertexPolyObject' (just above this function) to convert a list"
    "of a group of polys that have been manipulated by some function using QuArK Internal Poly Objects."

    for item in editor.layout.explorer.sellist:
        if item.type == ':mf':
            compairframe = item
            break
    if option == 0:
        bones = None
        undo = quarkx.action()
        if len(newobjectslist) > 1:
            comp_list = []
            if newobjectslist[0].name.find(":mc-b-") != -1:
                for obj in newobjectslist:
                    if obj.name.find(":mc-b-") != -1:
                        thiscomp = obj.name.split("-b-")[0]
                        if thiscomp in comp_list:
                            continue
                        comp_list = comp_list + [thiscomp]
                bones = 1
            else:
                comp = editor.Root.currentcomponent
                comp_list = [comp.name]
                new_comp = comp.copy()
                compframes = new_comp.findallsubitems("", ':mf')   # get all frames
            comp_count = len(comp_list)
            count = 0
            while 1:
                comp = editor.Root.currentcomponent # Don't need this line unless we do an option setting & maybe not then either.
                if comp.name != comp_list[count]: # Don't need this line unless we do an option setting & maybe not then either.
                    comp = editor.Root.dictitems[comp_list[count]]
                new_comp = comp.copy()
                compframes = new_comp.findallsubitems("", ':mf')   # get all frames
                compframe = compframes[editor.bone_frame]
                for newobject in range(len(newobjectslist)):
                    if bones is not None:
                        obj_name = newobjectslist[newobject].name.split("-b-")[0]
                        if obj_name != comp_list[count]:
                            continue
                    for poly in range(len(newobjectslist[newobject].subitems)):
                        for listframe in editor.layout.explorer.sellist:
                            if listframe.type != ':mf':
                                continue
                            old_vtxs = compframe.vertices
                            if listframe == compairframe:
                                vtxnbr = int(newobjectslist[newobject].subitems[poly].shortname)
                                face = newobjectslist[newobject].subitems[poly].subitems[0]
                                vertex = quarkx.vect(face["v"][0] , face["v"][1], face["v"][2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
                                delta = vertex - old_vtxs[vtxnbr]
                                old_vtxs[vtxnbr] = vertex
                            compframe.vertices = old_vtxs
                    compframe.compparent = new_comp # To allow frame relocation after editing.
                if count == comp_count-1:
                    break
                undo.exchange(comp, new_comp)
                count = count + 1
        else:
            if newobjectslist[0].name.find(":mc-b-") != -1:
                thiscomp = newobjectslist[0].name.split("-b-")[0]
                comp = editor.Root.dictitems[thiscomp]
                bones = 1
            else:
                comp = editor.Root.currentcomponent
            new_comp = comp.copy()
            compframes = new_comp.findallsubitems("", ':mf')   # get all frames
            for poly in range(len(newobjectslist[0].subitems)):
                for compframe in range(len(compframes)):
                    for listframe in editor.layout.explorer.sellist:
                        if listframe.type != ":mf":
                            continue
                        if (bones is None and compframes[compframe].name == listframe.name) or (bones is not None and compframe == editor.bone_frame):
                            old_vtxs = compframes[compframe].vertices
                            if listframe == compairframe:
                                vtxnbr = int(newobjectslist[0].subitems[poly].shortname)
                                face = newobjectslist[0].subitems[poly].subitems[0]
                                vertex = quarkx.vect(face["v"][0] , face["v"][1], face["v"][2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
                                delta = vertex - old_vtxs[vtxnbr]
                                old_vtxs[vtxnbr] = vertex
                            else:
                                vtxnbr = int(newobjectslist[0].subitems[poly].shortname)
                                old_vtxs[vtxnbr] = old_vtxs[vtxnbr] + delta
                            compframes[compframe].vertices = old_vtxs
                    compframes[compframe].compparent = new_comp # To allow frame relocation after editing.
        # This does the undo.exchange or final undo.exchange when needed.
        undo.exchange(comp, new_comp)
        editor.ok(undo, undomsg)

    if option == 1:
        from qbaseeditor import currentview
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        tris = new_comp.triangles
        try:
            tex = comp.currentskin
            texWidth,texHeight = tex["Size"]
        except:
            texWidth,texHeight = currentview.clientarea
        for poly in range(len(newobjectslist[0].subitems)):
            polygon = newobjectslist[0].subitems[poly]
            face = polygon.subitems[0]
            if comp.currentskin is not None:
                newpos = quarkx.vect(face["v"][0] , face["v"][1], face["v"][2]) + quarkx.vect(texWidth*.5, texHeight*.5, 0)
            else:
                newpos = quarkx.vect(face["v"][0] , face["v"][1], face["v"][2]) + quarkx.vect(int((texWidth*.5) +.5), int((texHeight*.5) -.5), 0)    
            tuplename = tuple(str(s) for s in polygon.shortname.split(','))
            tri_index, ver_index = tuplename
            tri_index = int(tri_index)
            ver_index = int(ver_index)
            tri = tris[tri_index]
            for j in range(len(tri)):
                if j == ver_index:
                    if j == 0:
                        newtriangle = ((tri[j][0], int(newpos.tuple[0]), int(newpos.tuple[1])), tri[1], tri[2])
                    elif j == 1:
                        newtriangle = (tri[0], (tri[j][0], int(newpos.tuple[0]), int(newpos.tuple[1])), tri[2])
                    else:
                        newtriangle = (tri[0], tri[1], (tri[j][0], int(newpos.tuple[0]), int(newpos.tuple[1])))
                    tris[tri_index] = newtriangle
        new_comp.triangles = tris
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        for compframe in compframes:
            compframe.compparent = new_comp # To allow frame relocation after editing.
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        editor.ok(undo, undomsg)
    
    if option == 2:
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        newtris = new_comp.triangles
        newtri_index = len(comp.triangles)
        newvertexselection = []
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        currentvertices = len(compframes[0].vertices)
        for compframe in range(len(compframes)):
            if compframes[compframe].name == comp.currentframe.name:
                current = compframe
                break
        for poly in range(len(newobjectslist[0].subitems)):
            old_vtxs = compframes[current].vertices
            vtxnbr = int(newobjectslist[0].subitems[poly].shortname)
            newver_index = currentvertices + poly
            face = newobjectslist[0].subitems[poly].subitems[0]
            newvertex = quarkx.vect(face["v"][0] , face["v"][1], face["v"][2]) - quarkx.vect(1.0,0.0,0.0)/view.info["scale"]*2
            delta = newvertex - old_vtxs[vtxnbr]
            newvertexselection = newvertexselection + [newver_index]
            for compframe in compframes:
                old_vtxs = compframe.vertices
                newvertex = old_vtxs[vtxnbr] + delta
                old_vtxs = old_vtxs + [newvertex]
                compframe.vertices = old_vtxs
                compframe.compparent = new_comp # To allow frame relocation after editing.

        from mdlhandles import SkinView1
        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
            for v in editor.layout.views:
                if v.info["viewname"] == "editors3Dview":
                    cordsview = v
        else:
            try:
                tex = comp.currentskin
                texWidth,texHeight = tex["Size"]
                if quarkx.setupsubset(SS_MODEL, "Options")['UseSkinViewScale'] == "1":
                    SkinViewScale = SkinView1.info["scale"]
                else:
                    SkinViewScale = 1
            except:
                texWidth,texHeight = SkinView1.clientarea
                SkinViewScale = 1
        for tri in editor.SelCommonTriangles:
            if len(tri) == 3:
                oldtri, oldver1 ,oldver0 = tri
            else:
                oldtri, oldver1 ,oldver0 ,oldver2 = tri
            for poly in range(len(newobjectslist[0].subitems)):
                if int(newobjectslist[0].subitems[poly].shortname) == oldver1:
                    newver_index0 = currentvertices + poly
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        newuv0u = int(cordsview.proj(compframes[current].vertices[newver_index0]).tuple[0])
                        newuv0v = int(cordsview.proj(compframes[current].vertices[newver_index0]).tuple[1])
                        olduv0u = int(cordsview.proj(compframes[current].vertices[oldver0]).tuple[0])
                        olduv0v = int(cordsview.proj(compframes[current].vertices[oldver0]).tuple[1])
                    else:
                        newuv0u = int(compframes[current].vertices[newver_index0].tuple[0]-int(texWidth*.5))*SkinViewScale
                        newuv0v = int(compframes[current].vertices[newver_index0].tuple[1]-int(texHeight*.5))*SkinViewScale
                        olduv0u = int(compframes[current].vertices[oldver0].tuple[0]+int(texWidth*.5))*SkinViewScale
                        olduv0v = int(compframes[current].vertices[oldver0].tuple[1]+int(texHeight*.5))*SkinViewScale
                if int(newobjectslist[0].subitems[poly].shortname) == oldver0:
                    newver_index1 = currentvertices + poly
                    if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                        newuv1u = int(cordsview.proj(compframes[current].vertices[newver_index1]).tuple[0])
                        newuv1v = int(cordsview.proj(compframes[current].vertices[newver_index1]).tuple[1])
                        olduv1u = int(cordsview.proj(compframes[current].vertices[oldver1]).tuple[0])
                        olduv1v = int(cordsview.proj(compframes[current].vertices[oldver1]).tuple[1])
                    else:
                        newuv1u = int(compframes[current].vertices[newver_index1].tuple[0]+int(texWidth*.5))*SkinViewScale
                        newuv1v = int(compframes[current].vertices[newver_index1].tuple[1]-int(texHeight*.5))*SkinViewScale
                        olduv1u = int(compframes[current].vertices[oldver1].tuple[0]-int(texWidth*.5))*SkinViewScale
                        olduv1v = int(compframes[current].vertices[oldver1].tuple[1]+int(texHeight*.5))*SkinViewScale
                if len(tri) == 4:
                    if int(newobjectslist[0].subitems[poly].shortname) == oldver2:
                        newver_index2 = currentvertices + poly
                        if quarkx.setupsubset(SS_MODEL, "Options")['SkinFrom3Dview'] == "1" or SkinView1 is None:
                            newuv2u = int(cordsview.proj(compframes[current].vertices[newver_index2]).tuple[0])
                            newuv2v = int(cordsview.proj(compframes[current].vertices[newver_index2]).tuple[1])
                            olduv2u = int(cordsview.proj(compframes[current].vertices[oldver2]).tuple[0])
                            olduv2v = int(cordsview.proj(compframes[current].vertices[oldver2]).tuple[1])
                        else:
                            newuv2u = int(compframes[current].vertices[newver_index2].tuple[0]+int(texWidth*.5))*SkinViewScale
                            newuv2v = int(compframes[current].vertices[newver_index2].tuple[1]-int(texHeight*.5))*SkinViewScale
                            olduv2u = int(compframes[current].vertices[oldver2].tuple[0]-int(texWidth*.5))*SkinViewScale
                            olduv2v = int(compframes[current].vertices[oldver2].tuple[1]+int(texHeight*.5))*SkinViewScale

            newtris = newtris + [((newver_index0, newuv0u, newuv0v), (newver_index1, newuv1u, newuv1v), (oldver0, olduv0u, olduv0v))]
            newtris = newtris + [((newver_index0, newuv0u, newuv0v), (oldver0, olduv0u, olduv0v), (oldver1, olduv1u, olduv1v))]
        new_comp.triangles = newtris

        if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
            undomsg = "editor-linear all edges extrusion"
        else:
            undomsg = "editor-linear outside edges extrusion"

        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        make_tristodraw_dict(editor, new_comp)
        editor.ok(undo, undomsg)
        editor.ModelVertexSelList = newvertexselection



def MakeEditorFaceObject(editor, option=0):
    "Creates a single QuArK Internal Face Object from 3 selected vertexes in the ModelVertexSelList"
    "or list of Face Objects by using the ModelFaceSelList 'tri_index' items in the list directly."

    editor.EditorObjectList = []
    comp = editor.Root.currentcomponent
    tris = comp.triangles  # A list of all the triangles of the current component if there is more than one.
                           # If NONE of the sub-items of a models component(s) have been selected,
                           # then it uses the 1st item of each sub-item, of the 1st component of the model.
                           # For example, the 1st skin, the 1st frame and so on, of the 1st component.
    if option == 0: # Returns one QuArK Internal Object (a face), identified by the currentcomponent's 'shortname' and tri_index,
                    # for each tri_index item in the ModelFaceSelList.
                    # These Objects can then be used with other Map Editor and Quarkx functions.
                    # They can also be easily converted back to the Model Editor's needed format using the Object's shortname and tri_index.
        for trinbr in range(len(tris)):  # Iterates, goes through, the above list, starting with a count number of zero, 0, NOT 1.
            for tri_index in range(len(editor.ModelFaceSelList)):
                if trinbr == editor.ModelFaceSelList[tri_index]:
                    face = quarkx.newobj(comp.shortname+","+str(trinbr)+","+str(tris[trinbr][0][0])+","+str(tris[trinbr][1][0])+","+str(tris[trinbr][2][0])+":f")
                    if editor.Root.currentcomponent.currentskin is not None:
                        face["tex"] = editor.Root.currentcomponent.currentskin.shortname
                    else:
                        face["tex"] = "None"
                    # Here we need to use the triangles 3 vertex_index numbers to maintain their proper order to create the face Object.
                    # The last 3 amount are usually for texture positioning on a face, but can not be used for the Model Editor's format.
                    vtxindexes = (float(tris[trinbr][0][0]), float(tris[trinbr][1][0]), float(tris[trinbr][2][0]), 0.0, 0.0, 0.0)
                    face["tv"] = (vtxindexes)                                  # They don't really give usable values for texture positioning.
                    verts = editor.Root.currentcomponent.currentframe.vertices # The list of vertex positions of the current component's
                                                                               # current animation frame selected, if any, if not then its 1st frame.
                    vect0X ,vect0Y, vect0Z = verts[tris[trinbr][0][0]].tuple # Gives the actual 3D vector x,y and z positions of the triangle's 1st vertex.
                    vect1X ,vect1Y, vect1Z = verts[tris[trinbr][1][0]].tuple # Gives the actual 3D vector x,y and z positions of the triangle's 2nd vertex.
                    vect2X ,vect2Y, vect2Z = verts[tris[trinbr][2][0]].tuple # Gives the actual 3D vector x,y and z positions of the triangle's 3rd vertex.
                    vertexlist = (vect0X ,vect0Y, vect0Z, vect1X ,vect1Y, vect1Z, vect2X ,vect2Y, vect2Z)
                    face["v"] = vertexlist
                    editor.EditorObjectList = editor.EditorObjectList + [face]
        return editor.EditorObjectList
    if option != 2:
        editor.ModelFaceSelList = []
        editor.SelCommonTriangles = []
        editor.SelVertexes = []
    v0 = editor.ModelVertexSelList[0] # Gives the index number of the 1st vertex in the list.
    v1 = editor.ModelVertexSelList[1] # Gives the index number of the 2nd vertex in the list.
    v2 = editor.ModelVertexSelList[2] # Gives the index number of the 3rd vertex in the list.
    
    if option == 1: # Returns only one object (face) & tri_index for the 3 selected vertexes used by the same triangle.
                    # This object can then be used with other Map Editor and Quarkx functions.
        for trinbr in range(len(tris)):  # Iterates, goes through, the above list, starting with a count number of zero, 0, NOT 1.

            # Compares all of the triangle's vertex index numbers, in their proper order, to the above 3 items.
            # Thus insuring it will return the actual single triangle that we want.
            if (tris[trinbr][0][0] == v0 or tris[trinbr][0][0] == v1 or tris[trinbr][0][0] == v2) and (tris[trinbr][1][0] == v0 or tris[trinbr][1][0] == v1 or tris[trinbr][1][0] == v2) and (tris[trinbr][2][0] == v0 or tris[trinbr][2][0] == v1 or tris[trinbr][2][0] == v2):
                tri_index = trinbr  # The iterating count number (trinbr) IS the tri_index number.
                face = quarkx.newobj(comp.shortname+" face\\tri "+str(tri_index)+":f")
                if editor.Root.currentcomponent.currentskin is not None:
                    face["tex"] = editor.Root.currentcomponent.currentskin.shortname
                else:
                    face["tex"] = "None"
                # Here we need to use the triangles vertexes to maintain their proper order.
                vtxindexes = (float(tris[trinbr][0][0]), float(tris[trinbr][1][0]), float(tris[trinbr][2][0]), 0.0, 0.0, 0.0) # We use this triangle's 3 vertex_index numbers here just to create the face object.
                face["tv"] = (vtxindexes)                                  # They don't really give usable values for texture positioning.
                verts = editor.Root.currentcomponent.currentframe.vertices # The list of vertex positions of the current component's
                                                                           # current animation frame selected, if any, if not then its 1st frame.
                vect00 ,vect01, vect02 = verts[tris[trinbr][0][0]].tuple # Gives the actual 3D vector x,y and z positions of the triangle's 1st vertex.
                vect10 ,vect11, vect12 = verts[tris[trinbr][1][0]].tuple # Gives the actual 3D vector x,y and z positions of the triangle's 2nd vertex.
                vect20 ,vect21, vect22 = verts[tris[trinbr][2][0]].tuple # Gives the actual 3D vector x,y and z positions of the triangle's 3rd vertex.
                vertexlist = (vect00 ,vect01, vect02, vect10 ,vect11, vect12, vect20 ,vect21, vect22)
                face["v"] = vertexlist
                editor.EditorObjectList = editor.EditorObjectList + [[face, tri_index]]
                editor.ModelFaceSelList = editor.ModelFaceSelList + [tri_index]
                return editor.EditorObjectList

    elif option == 2: # Returns an object (face) & tri_index for each triangle that shares the 1st vertex of the 3 selected vertexes used by the same triangle.
                      # Meaning, any triangle (face) using this 'common' vertex will be returned.
                      # Its 1st vertex must be selected by itself first, then its other 2 vertexes in any order.
                      # These objects can then be used with other Map Editor and Quarkx functions.
        for trinbr in range(len(tris)):  # Iterates, goes through, the above list, starting with a count number of zero, 0, NOT 1.
            if (tris[trinbr][0][0] == v0 or tris[trinbr][0][0] == v1 or tris[trinbr][0][0] == v2) and (tris[trinbr][1][0] == v0 or tris[trinbr][1][0] == v1 or tris[trinbr][1][0] == v2) and (tris[trinbr][2][0] == v0 or tris[trinbr][2][0] == v1 or tris[trinbr][2][0] == v2):
                tri_index = trinbr
                break

        for trinbr in range(len(tris)):  # Iterates, goes through, the above list, starting with a count number of zero, 0, NOT 1.
            if tris[trinbr][0][0] == v0 or tris[trinbr][1][0] == v0 or tris[trinbr][2][0] == v0:
                face = quarkx.newobj(comp.shortname+" face\\tri "+str(trinbr)+":f")
                if editor.Root.currentcomponent.currentskin is not None:
                    face["tex"] = editor.Root.currentcomponent.currentskin.shortname
                else:
                    face["tex"] = "None"
                vtxindexes = (float(tris[trinbr][0][0]), float(tris[trinbr][1][0]), float(tris[trinbr][2][0]), 0.0, 0.0, 0.0) # We use each triangle's 3 vertex_index numbers here just to create it's face object.
                face["tv"] = (vtxindexes)                                                                                     # They don't really give usable values for texture positioning.
                verts = editor.Root.currentcomponent.currentframe.vertices # The list of vertex positions of the current component's
                                                                           # current animation frame selected, if any, if not then its 1st frame.
                vect00 ,vect01, vect02 = verts[tris[trinbr][0][0]].tuple # Gives the actual 3D vector x,y and z positions of this triangle's 1st vertex.
                vect10 ,vect11, vect12 = verts[tris[trinbr][1][0]].tuple # Gives the actual 3D vector x,y and z positions of this triangle's 2nd vertex.
                vect20 ,vect21, vect22 = verts[tris[trinbr][2][0]].tuple # Gives the actual 3D vector x,y and z positions of this triangle's 3rd vertex.
                vertexlist = (vect00 ,vect01, vect02, vect10 ,vect11, vect12, vect20 ,vect21, vect22)
                face["v"] = vertexlist
                editor.EditorObjectList = editor.EditorObjectList + [[face, tri_index]]
        return editor.EditorObjectList
        
    elif option == 3: # Returns an object & tri_index for each triangle that shares the 1st and one other vertex of our selected triangle's vertexes.
                      # These objects can then be used with other Map Editor and Quarkx functions.
        for trinbr in range(len(tris)):  # Iterates, goes through, the above list, starting with a count number of zero, 0, NOT 1.
            if (tris[trinbr][0][0] == v0 or tris[trinbr][0][0] == v1 or tris[trinbr][0][0] == v2) and (tris[trinbr][1][0] == v0 or tris[trinbr][1][0] == v1 or tris[trinbr][1][0] == v2) and (tris[trinbr][2][0] == v0 or tris[trinbr][2][0] == v1 or tris[trinbr][2][0] == v2):
                tri_index = trinbr
                break

        for trinbr in range(len(tris)):  # Iterates, goes through, the above list, starting with a count number of zero, 0, NOT 1.
            if (tris[trinbr][0][0] is v0 or tris[trinbr][0][0] is v1 or tris[trinbr][0][0] is v2) and ((tris[trinbr][1][0] is v0 or tris[trinbr][1][0] is v1 or tris[trinbr][1][0] is v2) or (tris[trinbr][2][0] is v0 or tris[trinbr][2][0] is v1 or tris[trinbr][2][0] is v2)):
                face = quarkx.newobj(comp.shortname+" face\\tri "+str(trinbr)+":f")
                if editor.Root.currentcomponent.currentskin is not None:
                    face["tex"] = editor.Root.currentcomponent.currentskin.shortname
                else:
                    face["tex"] = "None"
                vtxindexes = (float(tris[trinbr][0][0]), float(tris[trinbr][1][0]), float(tris[trinbr][2][0]), 0.0, 0.0, 0.0) # We use each triangle's 3 vertex_index numbers here just to create it's face object.
                face["tv"] = (vtxindexes)                                                                                     # They don't really give usable values for texture positioning.
                verts = editor.Root.currentcomponent.currentframe.vertices # The list of vertex positions of the current component's
                                                                           # current animation frame selected, if any, if not then its 1st frame.
                vect00 ,vect01, vect02 = verts[tris[trinbr][0][0]].tuple # Gives the actual 3D vector x,y and z positions of this triangle's 1st vertex.
                vect10 ,vect11, vect12 = verts[tris[trinbr][1][0]].tuple # Gives the actual 3D vector x,y and z positions of this triangle's 2nd vertex.
                vect20 ,vect21, vect22 = verts[tris[trinbr][2][0]].tuple # Gives the actual 3D vector x,y and z positions of this triangle's 3rd vertex.
                vertexlist = (vect00, vect01, vect02, vect10, vect11, vect12, vect20, vect21, vect22)
                face["v"] = vertexlist
                editor.EditorObjectList = editor.EditorObjectList + [[face, trinbr]]
                editor.ModelFaceSelList = editor.ModelFaceSelList + [trinbr]
        return editor.EditorObjectList


#
# Does the opposite of the 'MakeEditorFaceObject' (just above this function) to convert
#   a list of faces that have been manipulated by some function using QuArK Internal Face Objects.
# The 'new' objects list in the functions 'ok' section is passed to here where it is converted back
#   to usable model component mesh vertexes of those faces and the final 'ok' function is performed.
# option=0 is the function for the Model Editor.
# option=1 is the function for the Skin-view.
# option=2, called from mdlhandles.py class LinRedHandle, ok function
#   is for the editor's selected faces extrusion function.
#
def ConvertEditorFaceObject(editor, newobjectslist, flags, view, undomsg, option=0):
    "Does the opposite of the 'MakeEditorFaceObject' (just above this function) to convert"
    "a list of faces that have been manipulated by some function using QuArK Internal Face Objects."
    for item in editor.layout.explorer.sellist:
        if item.type == ':mf':
            compairframe = item
            break
    if option == 0:
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        for face in newobjectslist:
            VertToMove = []
            tuplename = tuple(str(s) for s in face.shortname.split(','))
            compname, tri_index, ver_index0, ver_index1, ver_index2 = tuplename
            VertToCheck0 = [int(ver_index0), quarkx.vect(face["v"][0], face["v"][1], face["v"][2])]
            VertToCheck1 = [int(ver_index1), quarkx.vect(face["v"][3], face["v"][4], face["v"][5])]
            VertToCheck2 = [int(ver_index2), quarkx.vect(face["v"][6], face["v"][7], face["v"][8])]
            if not (VertToCheck0 in VertToMove):
                VertToMove = VertToMove + [VertToCheck0]
            if not (VertToCheck1 in VertToMove):
                VertToMove = VertToMove + [VertToCheck1]
            if not (VertToCheck2 in VertToMove):
                VertToMove = VertToMove + [VertToCheck2]
            for Vert in VertToMove:
                for compframe in compframes:
                    for listframe in editor.layout.explorer.sellist:
                        if compframe.name == listframe.name:
                            old_vtxs = compframe.vertices
                            if listframe == compairframe:
                                delta = Vert[1] - old_vtxs[Vert[0]]
                                old_vtxs[Vert[0]] = Vert[1]
                            else:
                                old_vtxs[Vert[0]] = old_vtxs[Vert[0]] + delta
                            compframe.vertices = old_vtxs
                    compframe.compparent = new_comp # To allow frame relocation after editing.
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        editor.ok(undo, undomsg)

    # for test reference only - def replacevertexes(editor, comp, vertexlist, flags, view, undomsg):
    if option == 1:
        comp = editor.Root.currentcomponent
        vertexlist = []
        for face in newobjectslist:
            tuplename = tuple(str(s) for s in face.shortname.split(','))
            vtxpos0 = quarkx.vect(face["v"][0] , face["v"][1], face["v"][2])
            vtxpos1 = quarkx.vect(face["v"][3] , face["v"][4], face["v"][5])
            vtxpos2 = quarkx.vect(face["v"][6] , face["v"][7], face["v"][8])
            pos0X, pos0Y, pos0Z = view.proj(vtxpos0).tuple
            pos1X, pos1Y, pos1Z = view.proj(vtxpos1).tuple
            pos2X, pos2Y, pos2Z = view.proj(vtxpos2).tuple
            pos0 = quarkx.vect(pos0Y, pos0Z, 0)
            pos1 = quarkx.vect(pos1Y, pos1Z, 0)
            pos2 = quarkx.vect(pos2Y, pos2Z, 0)
            compname, tri_index, ver_index0, ver_index1, ver_index2 = tuplename
            tri_index = int(tri_index)
            ver_index0 = int(ver_index0)
            ver_index1 = int(ver_index1)
            ver_index2 = int(ver_index2)
            vertex0 = editor.Root.currentcomponent.currentframe.vertices[ver_index0]
            vertex1 = editor.Root.currentcomponent.currentframe.vertices[ver_index1]
            vertex2 = editor.Root.currentcomponent.currentframe.vertices[ver_index2]
            if vertexlist == []:
                vertexlist = vertexlist + [[pos0, vertex0, tri_index, ver_index0]] + [[pos1, vertex1, tri_index, ver_index1]] + [[pos2, vertex2, tri_index, ver_index2]]
            else:
                for item in range(len(vertexlist)):
                    if vertexlist[item][2] == int(tuplename[1]):
                        break
                    if item == len(vertexlist)-1:
                        vertexlist = vertexlist + [[pos0, vertex0, tri_index, ver_index0]] + [[pos1, vertex1, tri_index, ver_index1]] + [[pos2, vertex2, tri_index, ver_index2]]

        replacevertexes(editor, comp, vertexlist, flags, view, undomsg, option=option)

    if option == 2:
        comp = editor.Root.currentcomponent
        new_comp = comp.copy()
        newtris = new_comp.triangles
        newtri_index = len(comp.triangles)
        newfaceselection = []
        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        currentvertices = len(compframes[0].vertices)

        for selface in editor.ModelFaceSelList:
            netvtxs = []
            for vtx in comp.triangles[selface]:
                if vtx in netvtxs:
                    pass
                else:
                    netvtxs = netvtxs + [vtx[0]]
        newvtxsneeded = len(netvtxs)

        old_vtxs = []
        old_vtx_nbrs = []
        editor.ModelFaceSelList.sort()

        # This section computes the net delta vertex movement for the extrusion drag.
        face = newobjectslist[0]
        tuplename = tuple(str(s) for s in face.shortname.split(','))
        compname, tri_index, ver_index0, ver_index1, ver_index2 = tuplename
        old_ver0 = comp.currentframe.vertices[int(ver_index0)]
        new_ver0 = quarkx.vect(face["v"][0], face["v"][1], face["v"][2])
        delta = new_ver0 - old_ver0

        for face in newobjectslist:
            tuplename = tuple(str(s) for s in face.shortname.split(','))
            compname, tri_index, ver_index0, ver_index1, ver_index2 = tuplename
            tri_index = int(tri_index)
            ver_index0 = int(ver_index0)
            ver_index1 = int(ver_index1)
            ver_index2 = int(ver_index2)

            # This section makes the new vertexes of the editor's selected faces extrusion function.
            if ver_index0 in old_vtx_nbrs:
                pass
            else:
                old_vtxs = old_vtxs + [quarkx.vect(face["v"][0], face["v"][1], face["v"][2])]
                old_vtx_nbrs = old_vtx_nbrs + [ver_index0]
            if ver_index1 in old_vtx_nbrs:
                pass
            else:
                old_vtxs = old_vtxs + [quarkx.vect(face["v"][3], face["v"][4], face["v"][5])]
                old_vtx_nbrs = old_vtx_nbrs + [ver_index1]
            if ver_index2 in old_vtx_nbrs:
                pass
            else:
                old_vtxs = old_vtxs + [quarkx.vect(face["v"][6], face["v"][7], face["v"][8])]
                old_vtx_nbrs = old_vtx_nbrs + [ver_index2]

            # This section calculates the new selected triangle's (face) vertex index numbers.
            vtx0,u0,v0 = comp.triangles[tri_index][0]
            vtx1,u1,v1 = comp.triangles[tri_index][1]
            vtx2,u2,v2 = comp.triangles[tri_index][2]
            for oldnbr in range(len(old_vtx_nbrs)):
                if vtx0 == old_vtx_nbrs[oldnbr]:
                    newvtx0 = currentvertices + oldnbr
                if vtx1 == old_vtx_nbrs[oldnbr]:
                    newvtx1 = currentvertices + oldnbr
                if vtx2 == old_vtx_nbrs[oldnbr]:
                    newvtx2 = currentvertices + oldnbr

            # This section makes the new 'side' triangles for the extruded faces.
            vtx01 = vtx12 = vtx20 = 1
            for selface in editor.ModelFaceSelList:
                vtxs = []
                for vtx in comp.triangles[selface]:
                    vtxs = vtxs + [vtx[0]]
                if selface == tri_index or len(editor.ModelFaceSelList) == 1:
                    pass
                else:
                    if (vtx0 in vtxs and vtx1 in vtxs):
                        vtx01 = 0
                    if (vtx1 in vtxs and vtx2 in vtxs):
                        vtx12 = 0
                    if (vtx2 in vtxs and vtx0 in vtxs):
                        vtx20 = 0

            if vtx01 == 1:
                newtris = newtris + [((newvtx0,u0,v0), (comp.triangles[tri_index][0][0],u0,v0), (newvtx1,u1,v1))]
                newtris = newtris + [((newvtx1,u1,v1), (comp.triangles[tri_index][0][0],u0,v0), (comp.triangles[tri_index][1][0],u1,v1))]
                newtri_index = newtri_index + 2
            if vtx12 == 1:
                newtris = newtris + [((newvtx2,u2,v2), (newvtx1,u1,v1), (comp.triangles[tri_index][1][0],u1,v1))]
                newtris = newtris + [((newvtx2,u2,v2), (comp.triangles[tri_index][1][0],u1,v1), (comp.triangles[tri_index][2][0],u2,v2))]
                newtri_index = newtri_index + 2
            if vtx20 == 1:
                newtris = newtris + [((newvtx2,u2,v2), (comp.triangles[tri_index][0][0],u0,v0), (newvtx0,u0,v0))]
                newtris = newtris + [((newvtx2,u2,v2), (comp.triangles[tri_index][2][0],u2,v2), (comp.triangles[tri_index][0][0],u0,v0))]
                newtri_index = newtri_index + 2
            # This section makes the new selected faces being dragged.
            newtris = newtris + [((newvtx0,u0,v0), (newvtx1,u1,v1), (newvtx2,u2,v2))]

            if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
                # This line leaves the 'bulkheads' in between extrusion drags.
                newfaceselection = newfaceselection + [newtri_index]
            else:
                # This line, and the two noted below, remove the 'bulkheads' between extrusion drags.
                newfaceselection = newfaceselection + [newtri_index-len(editor.ModelFaceSelList)]

            newtri_index = newtri_index + 1

        if quarkx.setupsubset(SS_MODEL, "Options")["ExtrudeBulkHeads"] is not None:
            undomsg = "editor-linear face extrusion w/bulkheads"
        else:
            # These lines, and the one noted above, remove the 'bulkheads' between extrusion drags.
            undomsg = "editor-linear face extrusion"
            for tri_index in reversed(editor.ModelFaceSelList):
                newtris = newtris[:tri_index] + newtris[tri_index+1:]

        # This updates (adds) the new vertices to each frame.
        for compframe in compframes:
            if compframe.name == comp.currentframe.name:
                compframe.vertices = compframe.vertices + old_vtxs
            else:
                new_vtxs = []
                for old_nbr in old_vtx_nbrs:
                    new_vtxs = new_vtxs + [compframe.vertices[old_nbr] + delta]
                compframe.vertices = compframe.vertices + new_vtxs
            compframe.compparent = new_comp # To allow frame relocation after editing.

        # This updates (adds) the new triangles to the component.
        new_comp.triangles = newtris

        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        make_tristodraw_dict(editor, new_comp)
        editor.ok(undo, undomsg)
        editor.ModelFaceSelList = newfaceselection

        # Sets these lists up for the Linear Handle drag lines to be drawn.
        editor.SelCommonTriangles = []
        editor.SelVertexes = []
        if quarkx.setupsubset(SS_MODEL, "Options")['NFDL'] is None:
            for tri in editor.ModelFaceSelList:
                for vtx in range(len(comp.triangles[tri])):
                    if comp.triangles[tri][vtx][0] in editor.SelVertexes:
                        pass
                    else:
                        editor.SelVertexes = editor.SelVertexes + [comp.triangles[tri][vtx][0]] 
                    editor.SelCommonTriangles = editor.SelCommonTriangles + findTrianglesAndIndexes(comp, comp.triangles[tri][vtx][0], None)

        MakeEditorFaceObject(editor)



###############################
#
# Component & Sub-item Creation functions
#
###############################


#
# Actually done through the Delete and Cut functions on a menu.
# This function removes all data that may exist for the removed
# component from the editor's ModelComponentList and Bones, if any.
#
def removecomp(editor, compname, undo, multi_comps=0):
    components = editor.Root.findallsubitems("", ':mc')
    if len(components) == 1:
        editor.ModelComponentList = {'bboxlist': {}, 'bonelist': {}, 'tristodraw': {}}
    else:
        if editor.ModelComponentList.has_key(compname):
            try:
                del editor.ModelComponentList['tristodraw'][compname]
            except:
                pass
            del editor.ModelComponentList[compname]
        for comp in components:
            if comp.name != compname:
                newbonecomp = comp.name
                editor.Root.currentcomponent = comp
                break
        oldskelgroup = editor.Root.dictitems['Skeleton:bg']
        old = oldskelgroup.findallsubitems("", ':bone') # Get all bones in the old group.
        new = []
        for bone in old:
            new = new + [bone.copy()]
        for bone in new:
            if bone.dictspec['component'] == compname:
                bone['component'] = newbonecomp
                bone['comp_list'] = newbonecomp
            tempdata = {}
            for component in bone.vtxlist.keys():
                if component == compname:
                    continue
                else:
                    tempdata[component] = bone.vtxlist[component]
            bone.vtxlist = {}
            bone.vtxlist = tempdata
            tempdata = {}
            for component in bone.vtx_pos.keys():
                if component == compname:
                    continue
                else:
                    tempdata[component] = bone.vtx_pos[component]
            bone.vtx_pos = {}
            bone.vtx_pos = tempdata
        if multi_comps == 0:
            newskelgroup = boneundo(editor, old, new)
            undo.exchange(oldskelgroup, newskelgroup)
        else:
            for bone in new:
                oldskelgroup.dictitems[bone.name]['component'] = bone.dictspec['component']
                oldskelgroup.dictitems[bone.name]['comp_list'] = bone.dictspec['component']

#
# The 'option' value of 1 MAKES a "clean" brand new component with NO triangles, frame.vertecies (only frames) or bones.
# The 'option' value of 2 ADDS a new component to the model using currently selected faces of another component.
#    This function will also remove the selected faces and unused vertexes from the original component.
#
def addcomponent(editor, option=2):
    comp = editor.Root.currentcomponent

    # This section does a few selection test and gives an error message box if needed.
    if option == 2:
        for item in editor.layout.explorer.sellist:
            if item.parent.parent.name != comp.name:
                quarkx.msgbox("IMPROPER SELECTION !\n\nYou need to select a frame && faces from\none component to make a new component.\n\nYou have selected items that are not\npart of the ''"+editor.Root.currentcomponent.shortname+"'' Frames group.\nPlease un-select these items.\nYou can add other component faces\nafter the new component is created.\n\nAction Canceled.", MT_ERROR, MB_OK)
                return
        if editor.ModelFaceSelList == []:
            quarkx.msgbox("You need to select a group of faces\nto make a new component from.", MT_ERROR, MB_OK)
            return
    else:
        for item in editor.layout.explorer.sellist:
            if item.parent.parent.name != comp.name:
                quarkx.msgbox("IMPROPER SELECTION !\n\nYou need to select a frame from\none component to make a new clean component.\n\nYou have selected items that are not\npart of the ''"+editor.Root.currentcomponent.shortname+"'' Frames group.\nPlease un-select these items.\nYou can add other component faces\nafter the new clean component is created.\n\nAction Canceled.", MT_ERROR, MB_OK)
                return

    # These are things that we need to setup first for use later on.
    if option == 2:
        temp_list = []
        remove_triangle_list = []
        vertices_to_remove = []

    # Now we start creating our data copies to work with and the final "ok" swapping function at the end.
    # But first we check for any other "new component"s, if so we name this one 1 more then the largest number.
    if option == 2:
        tris = comp.triangles
        change_comp = comp.copy()
    new_comp = comp.copy()
    new_comp.shortname = "None"
    comparenbr = 0
    if option == 2:
        for item in editor.Root.dictitems:
            if editor.Root.dictitems[item].shortname.startswith('new component'):
                getnbr = editor.Root.dictitems[item].shortname
                getnbr = getnbr.replace('new component', '')
                if getnbr == "":
                   nbr = 0
                else:
                    nbr = int(getnbr)
                if nbr > comparenbr:
                    comparenbr = nbr
                nbr = comparenbr + 1
                new_comp.shortname = "new component " + str(nbr)
        if new_comp.shortname != "None":
            pass
        else:
            new_comp.shortname = "new component 1"
        # Component copy's still need to have their currentskin set.
        new_comp.currentskin = comp.currentskin
        # Set it up in the ModelComponentList.
        editor.ModelComponentList[new_comp.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}
    else:
        for item in editor.Root.dictitems:
            if editor.Root.dictitems[item].shortname.startswith('new clean component'):
                getnbr = editor.Root.dictitems[item].shortname
                getnbr = getnbr.replace('new clean component', '')
                if getnbr == "":
                   nbr = 0
                else:
                    nbr = int(getnbr)
                if nbr > comparenbr:
                    comparenbr = nbr
                nbr = comparenbr + 1
                new_comp.shortname = "new clean component " + str(nbr)
        if new_comp.shortname != "None":
            pass
        else:
            new_comp.shortname = "new clean component 1"
        editor.ModelComponentList[new_comp.name] = {'bonevtxlist': {}, 'colorvtxlist': {}, 'weightvtxlist': {}}

    ###### NEW COMPONENT SECTION ######

    # This section creates the "remove_triangle_list" from the ModelFaceSelList which is already
    #    in ascending numerical order but may have duplicate tri_index numbers that need to be removed.
    # The order also needs to be descending so when triangles are removed from another list it
    #    does not select an improper triangle due to list items shifting forward numerically.
    # The "remove_triangle_list" is used to re-create the current component.triangles and new_comp.triangles.
    if option == 2:
        for tri_index in reversed(editor.ModelFaceSelList):
            if tri_index in remove_triangle_list:
                pass
            else:
                remove_triangle_list = remove_triangle_list + [tri_index]

    # This section creates the "vertices_to_remove" to be used
    #    to re-create the current component's frame.vertices.
    # It also skips over any vertexes of the triangles to be removed but should not be included
    #    because they are "common" vertexes and still being used by other remaining triangles.
        for tri_index in remove_triangle_list:
            for vtx in range(len(tris[tri_index])):
                if tris[tri_index][vtx][0] in temp_list:
                    pass
                else:
                    temp_list.append(tris[tri_index][vtx][0])
        temp_list.sort()
        for item in reversed(temp_list):
            vertices_to_remove.append(item)

    # This creates the new component and places it under the main Model Root with the other components.
    ## This first part sets up the new_comp.triangles, which are the ones that have been selected, using the
    ##    "remove_triangle_list" which are also the same ones to be removed from the original component.
        newtris = []
        for tri_index in range(len(remove_triangle_list)):
            newtris = newtris + [comp.triangles[remove_triangle_list[tri_index]]]
        new_comp.triangles = newtris

    ## This second part reconstructs each frames "frame.vertices" to consist
    ##    of only those that are needed, removing any that are unused.
    ## Then it fixes up the new_comp.triangles vertex index numbers
    ##    to coordinate with those frame.vertices lists.
        for compframe in range(len(comp.dictitems['Frames:fg'].subitems)):
            newframe_vertices = []
            for vert_index in range(len(vertices_to_remove)):
                newframe_vertices = newframe_vertices + [comp.dictitems['Frames:fg'].subitems[compframe].vertices[vertices_to_remove[vert_index]]]
            new_comp.dictitems['Frames:fg'].subitems[compframe].vertices = newframe_vertices

        newtris = []
        for tri in range(len(new_comp.triangles)):
            for index in range(len(new_comp.triangles[tri])):
                for vert_index in range(len(vertices_to_remove)):
                    if new_comp.triangles[tri][index][0] == vertices_to_remove[vert_index]:
                        if index == 0:
                            tri0 = (vert_index, new_comp.triangles[tri][index][1], new_comp.triangles[tri][index][2])
                            break
                        elif index == 1:
                            tri1 = (vert_index, new_comp.triangles[tri][index][1], new_comp.triangles[tri][index][2])
                            break
                        else:
                            tri2 = (vert_index, new_comp.triangles[tri][index][1], new_comp.triangles[tri][index][2])
                            newtris = newtris + [(tri0, tri1, tri2)]
                            break
        new_comp.triangles = newtris
    else:
        new_comp.triangles = []
        for compframe in range(len(new_comp.dictitems['Frames:fg'].subitems)):
            new_comp.dictitems['Frames:fg'].subitems[compframe].vertices = []

    ## This last part places the new component into the editor and the model.
    compframes = new_comp.findallsubitems("", ':mf')   # get all frames
    for compframe in compframes:
        compframe.compparent = new_comp # To allow frame relocation after editing.
    undo = quarkx.action()
    # Clear these list to avoid errors, only needed for option 2.
    if option == 2:
        editor.ModelFaceSelList = []
        editor.EditorObjectList = []
    undo.put(editor.Root, new_comp)
    # Updates the editor.ModelComponentList 'tristodraw', for this component. This needs to be done for each component or bones will not work if used in the editor.
    make_tristodraw_dict(editor, new_comp)
    editor.ok(undo, new_comp.shortname + " created")
    if option == 1:
        return


    ###### ORIGINAL COMPONENT SECTION ######

    # This section checks and takes out, from the vertices_to_remove, any vert_index that is being used by a
    # triangle that is not being removed, in the remove_triangle_list, to avoid any invalid triangle errors.
    dumylist = vertices_to_remove
    for tri in range(len(change_comp.triangles)):
        if tri in remove_triangle_list:
            continue
        else:
            for vtx in range(len(change_comp.triangles[tri])):
                if change_comp.triangles[tri][vtx][0] in dumylist:
                    dumylist.remove(change_comp.triangles[tri][vtx][0])
    vertices_to_remove = dumylist
    
    # This section uses the "remove_triangle_list" to recreate the original
    # component.triangles without the selected faces.
    old_tris = change_comp.triangles
    remove_triangle_list.sort()
    remove_triangle_list = reversed(remove_triangle_list)
    for index in remove_triangle_list:
        old_tris = old_tris[:index] + old_tris[index+1:]
    change_comp.triangles = old_tris

    # This section uses the "vertices_to_remove" to recreate the
    # original component's frames without any unused vertexes.
    new_tris = change_comp.triangles
    compframes = change_comp.findallsubitems("", ':mf')   # find all frames
    for index in vertices_to_remove:
        enew_tris = fixUpVertexNos(new_tris, index)
        new_tris = enew_tris
        for compframe in compframes: 
            old_vtxs = compframe.vertices
            vtxs = old_vtxs[:index] + old_vtxs[index+1:]
            compframe.vertices = vtxs
    change_comp.triangles = new_tris

    # This section updates any bones in the original component and the editor.ModelComponentList,
    # if any vertexes that are being removed have been assigned to a bone's handle.
    vertices_to_remove.sort()

    # This last section updates the original component finishing the process for it.
    compframes = change_comp.findallsubitems("", ':mf')   # get all frames
    for compframe in compframes:
        compframe.compparent = change_comp # To allow frame relocation after editing.
    editor.Root.currentcomponent = change_comp
    editor.Root.currentcomponent.currentskin = comp.currentskin
    undo = quarkx.action()
    undo.exchange(comp, None)
    undo.put(editor.Root, change_comp)
    # Updates the editor.ModelComponentList 'tristodraw', for this component.  This needs to be done for each component or bones will not work if used in the editor.
    make_tristodraw_dict(editor, change_comp)
    editor.ok(undo, change_comp.shortname + " updated")
    # Updates the editor.ModelComponentList, for this component, 'bonevtxlist' and 'colorvtxlist' if one or both exist. 
    if len(vertices_to_remove) != 0:
        if editor.ModelComponentList[change_comp.name]['bonevtxlist'] != {}:
            update_bonevtxlist(editor, change_comp, vertices_to_remove)
        if editor.ModelComponentList[change_comp.name]['colorvtxlist'] != {}:
            update_colorvtxlist(editor, change_comp, vertices_to_remove)
    Update_Editor_Views(editor)

#
# Add a frame to a given component (ie duplicate last one)
#
def addframe(editor):
    comp = editor.Root.currentcomponent
    if (editor.layout.explorer.uniquesel is None) or (editor.layout.explorer.uniquesel.type != ":mf"):
        quarkx.msgbox("You need to select a single frame to duplicate.\n\nFor multiple frames use 'Duplicate' on the 'Edit' menu.", MT_ERROR, MB_OK)
        return

    newframe = editor.layout.explorer.uniquesel.copy()
    new_comp = comp.copy()
    compframes = new_comp.dictitems['Frames:fg'].subitems   # all frames
    itemdigit = None

    if newframe.shortname[len(newframe.shortname)-1].isdigit():
        itemdigit = ""
        count = len(newframe.shortname)-1
        while count >= 0:
            if newframe.shortname[count] == " ":
                count = count - 1
            elif newframe.shortname[count].isdigit():
                itemdigit = str(newframe.shortname[count]) + itemdigit
                count = count - 1
            else:
                break
        itembasename = newframe.shortname.split(itemdigit)[0]
    else:
        itembasename = newframe.shortname

    name = None
    comparenbr = 0
    count = 0
    stopcount = 0
    for compframe in compframes:
        if not itembasename.endswith(" ") and compframe.shortname.startswith(itembasename + " "):
            if stopcount == 0:
                count = count + 1
            continue
        if compframe.shortname.startswith(itembasename):
            stopcount = 1
            getnbr = compframe.shortname.replace(itembasename, '')
            if getnbr == "":
                nbr = 0
            else:
                nbr = int(getnbr)
            if nbr > comparenbr:
                comparenbr = nbr
                count = count + 1
            nbr = comparenbr + 1
            name = itembasename + str(nbr)
        if stopcount == 0:
            count = count + 1
    if name is not None:
        pass
    else:
        name = newframe.shortname
    newframe.shortname = name
    for frame in range(len(new_comp.dictitems['Frames:fg'].subitems)):
        if frame == len(new_comp.dictitems['Frames:fg'].subitems)-1 and count == 0:
            count = frame + 1
        if new_comp.dictitems['Frames:fg'].subitems[frame].shortname.startswith(itembasename):
            count = frame + 1
    # Places the new frame at the end of its group of frames of the same name.
    new_comp.dictitems['Frames:fg'].insertitem(count, newframe)
    compframes = new_comp.dictitems['Frames:fg'].subitems   # all frames
    # To allow frame relocation after editing.
    for compframe in compframes:
        compframe.compparent = new_comp
    undo = quarkx.action()
    undo.exchange(comp, None)
    undo.put(editor.Root, new_comp)
    editor.ok(undo, "add frame")



###############################
#
# Skeleton & Bone functions
#
###############################


#
# Actually done through the "Delete" and "Cut" functions on a menu.
# This function removes all data that may exist for the removed
# bonename from the editor's ModelComponentList and other bones, if any.
# If bonename is the "parent" of any other bones then their dictspec['parent_name']
# is set to "None" and they are moved outside of that parent bone so they are NOT
# removed or deleted. But if they are also in the "list" to be removed then nothing is done
# which allows them to be removed and deleted properly when the time comes.
#
def removebone(editor, bonename, undo, list, bonelist):
    def UpdateSubBones(bone, newbone, list):
        import operator
        try:
            bone_index = operator.indexOf(list, bone)
        except:
            pass
        else:
            list[bone_index] = newbone
        for sub_bone in range(len(bone.subitems)):
            list = UpdateSubBones(bone.subitems[sub_bone], newbone.subitems[sub_bone], list)
        return list

    for comp in editor.ModelComponentList.keys():
        if not comp.endswith(":mc"):
            continue
        if editor.ModelComponentList[comp]['bonevtxlist'].has_key(bonename):
            del editor.ModelComponentList[comp]['bonevtxlist'][bonename]
    group = editor.Root.dictitems['Skeleton:bg']
    for bone in bonelist:
        if bone.dictspec['parent_name'] == "None":
            change_parent_name = 0
        else:
            if bone.dictspec['parent_name'] == bonename:
                # "parent_name" bone is going to be removed
                change_parent_name = 1
            else:
                change_parent_name = 0
        if bone.parent.name == bonename:
            # bone.parent is going to be removed
            move_to_root = 1
        else:
            move_to_root = 0
        if change_parent_name or move_to_root:
            if move_to_root:
                newbone = bone.copy(group)
            else:
                newbone = bone.copy()
            if change_parent_name:
                newbone['parent_name'] = "None"
            if move_to_root:
                undo.exchange(bone, None)
                undo.put(group, newbone) # Move newbone to root.
            else:
                undo.exchange(bone, newbone) # Move newbone to root.
            list = UpdateSubBones(bone, newbone, list) # Updates the list and makes it our Current list.
            bonelist = UpdateSubBones(bone, newbone, bonelist) # Updates the list and makes a New list.

    return list, bonelist


#
# Finds and gets all bones within another bone in the explorer.sellist.
# "bonelist" is an empty list to start with for ex.: bonelist = []
# "bone" is each bone within the explorer.sellist from a "for" loop, calling this function for each bone.
# If "option" is "0" the original "bone" is added to the "bonelist", if set to another value then it is NOT included.
#
def addtolist(bonelist, bone, option=0):
    if ((not MdlOption("IndividualBonesSel")) or (bone.selected != 0)) and option == 0:
        bonelist = bonelist + [bone]
    for subbone in bone.subitems:
        if subbone.type == ":bone" and not subbone in bonelist:
            bonelist = addtolist(bonelist, subbone)
    return bonelist

#
# Finds and returns the bone name sent to this function.
#
def findbone(editor, bone_name):
    bones = editor.Root.dictitems['Skeleton:bg'].findallsubitems("", ':bone') # Get all bones.
    for this_bone in bones:
        if this_bone.name == bone_name:
            return this_bone
    return None

#
# This function removes all bones, CLEARS ALL selection lists and the editor.ModelComponentList
# to avoid errors in case there are bones that exist but all components have been deleted.
# It will also replace the 'Skeleton:bg' if it has been deleted by the user.
#
def clearbones(editor, undomsg):
    import mdlmgr
    from mdlmgr import treeviewselchanged
    mdlmgr.treeviewselchanged = 1
    editor.layout.explorer.sellist = []
    editor.layout.explorer.uniquesel = None
    editor.ModelComponentList['bonelist'] = {}
    undo = quarkx.action()
    skeletongroup = quarkx.newobj('Skeleton:bg')
    skeletongroup['type'] = chr(5)
    # If all components have been deleted.
    if editor.Root.dictitems.has_key("Skeleton:bg"):
        editor.ModelComponentList['tristodraw'] = {}
        undo.exchange(editor.Root.dictitems['Skeleton:bg'], skeletongroup)
    else:
        # If the 'Skeleton:bg' has been deleted.
        insertbefore = None
        for item in editor.Root.subitems:
            if item.type == ":mc":
                insertbefore = item
                break
        for item in editor.Root.subitems:
            if item.type == ":mc":
                editor.ModelComponentList[item.name]['bonevtxlist'] = {}
                editor.ModelComponentList[item.name]['weightvtxlist'] = {}
        if insertbefore is not None:
            undo.put(editor.Root, skeletongroup, insertbefore)
        else:
            undo.put(editor.Root, skeletongroup)
    editor.ok(undo, undomsg)
    formlist = quarkx.forms(1)
    for f in formlist:
        try:
            # This section updates the "Vertex Weights Dialog" if it is opened and needs to update.
            if f.caption == "Vertex Weights Dialog":
                import mdlentities
                mdlentities.WeightsClick(editor)
        except:
            pass

#
# Creates and returns a new Skeleton group to undo.exchange the old Skeleton group with.
# The 'old' is a standard list containing the old bones
# and the 'new' is a standard list containing the new bones in the same order.
# The 'new' is used to put them inside the 'newskelgroup'.
#
def boneundo(editor, old, new):
    def replacebone(oldskelgroup, newskelgroup, old, new):
        import operator
        for checkbone in range(len(oldskelgroup.subitems)):
            try:
                itemindex = operator.indexOf(old, oldskelgroup.subitems[checkbone])
            except:
                pass
            else:
                newskelgroup.removeitem(checkbone)
                copybone = new[itemindex].copy()
                newskelgroup.insertitem(checkbone, copybone)
            replacebone(oldskelgroup.subitems[checkbone], newskelgroup.subitems[checkbone], old, new)
    oldskelgroup = editor.Root.dictitems['Skeleton:bg']
    newskelgroup = oldskelgroup.copy()
    replacebone(oldskelgroup, newskelgroup, old, new)
    return newskelgroup

#
# This function adds a :bone-object to the skeleton-group of comp at position pos
#
def addbone(editor, comp, pos):
    name = None
    comparenbr = 0
    skeletongroup = editor.Root.dictitems['Skeleton:bg']    # get the bones group
    bones = skeletongroup.findallsubitems("", ':bone')      # get all bones
    for item in bones:
        if item.shortname.startswith('NewBone'):
            getnbr = item.shortname
            getnbr = getnbr.replace('NewBone', '')
            if getnbr == "":
                nbr = 0
            else:
                nbr = int(getnbr)
            if nbr > comparenbr:
                comparenbr = nbr
            nbr = comparenbr + 1
            name = "NewBone" + str(nbr)
    if name is None:
        name = "NewBone1"
    new_bone = quarkx.newobj(name + ":bone")
    new_bone['type'] = "qrk" # A QuArK default bone.
    new_bone['flags'] = (0,0,0,0,0,0)
    new_bone['show'] = (1.0,)
    new_bone['component'] = editor.Root.currentcomponent.name
    new_bone['parent_name'] = "None"
    new_bone.position = pos
    new_bone['position'] = pos.tuple
    from math import sqrt
    new_bone.rotmatrix = quarkx.matrix((sqrt(2)/2, -sqrt(2)/2, 0), (sqrt(2)/2, sqrt(2)/2, 0), (0, 0, 1))
    new_bone['draw_offset'] = (0.0,0.0,0.0)
    new_bone['scale'] = (1.0,)
    new_bone['_color'] = MapColor("BoneHandles", SS_MODEL)
    new_bone['bone_length'] = (0.0,0.0,0.0)
    undo = quarkx.action()
    undo.put(skeletongroup, new_bone)
    editor.ok(undo, "add bone")
 ### Code below if we just want to draw new bones without redrawing all handles.
 #   import mdlentities # Import needs to be here to avoid error.
 #   handle = mdlentities.CallManager("handlesopt", new_bone, editor)
 #   for v in editor.layout.views:
 #       cv = v.canvas()
 #       v.handles = v.handles + handle
 #       for h in handle:
 #           h.draw(v, cv, h)

#
# This function creates a new bone at position pos attached to bone.
#
def continue_bone(editor, bone, pos):
    skeletongroup = editor.Root.dictitems['Skeleton:bg']  # get the bones group
    name = None
    comparenbr = 0
    bones = skeletongroup.findallsubitems("", ':bone')      # get all bones
    for item in bones:
        if item.shortname.startswith('NewBone'):
            getnbr = item.shortname
            getnbr = getnbr.replace('NewBone', '')
            if getnbr == "":
                nbr = 0
            else:
                nbr = int(getnbr)
            if nbr > comparenbr:
                comparenbr = nbr
            nbr = comparenbr + 1
            name = "NewBone" + str(nbr)
    if name is None:
        name = "NewBone1"
    new_bone = quarkx.newobj(name + ":bone")
    new_bone['type'] = "qrk" # A QuArK default bone.
    new_bone['flags'] = (0,0,0,0,0,0)
    new_bone['show'] = (1.0,)
    new_bone['component'] = editor.Root.currentcomponent.name
    new_bone['parent_name'] = bone.name
    pos = quarkx.vect(bone.dictspec['position']) + quarkx.vect(8.0,2.0,2.0)
    new_bone.position = pos
    new_bone['position'] = pos.tuple
    new_bone.rotmatrix = bone.rotmatrix
    new_bone['draw_offset'] = (0, 0, 0)
    new_bone['scale'] = (1.0,)
    new_bone['_color'] = MapColor("BoneHandles", SS_MODEL)
    new_bone['bone_length'] = (8.0,2.0,2.0)
    undo = quarkx.action()
    undo.put(skeletongroup, new_bone)
    editor.ok(undo, "add bone")
 ### Code below if we just want to draw new bones without redrawing all handles.
 #   import mdlentities # Import needs to be here to avoid error.
 #   handle = mdlentities.CallManager("handlesopt", new_bone, editor)
 #   for v in editor.layout.views:
 #       cv = v.canvas()
 #       v.handles = v.handles + handle
 #       for h in handle:
 #           h.draw(v, cv, h)

#
# This function creates a bone control to the specified bone and all its components.
#
def add_bone_control(editor, spec_bone):
    folder_name = spec_bone.name.split("_")[0]
    nbr = -1
    for item in editor.Root.subitems:
        if item.type == ":mc" and item.name.startswith(folder_name):
            keys = item.dictspec.keys()
            keys.sort()
            for key in keys:
                if key.startswith("bone_control_"):
                    chk_nbr = int(key.split("_")[2])
                    if chk_nbr != nbr+1:
                        break
                    nbr = int(key.split("_")[2])
            break
    undo = quarkx.action()
    new_bone = spec_bone.copy()
    new_bone['control_type'] = "8"
    new_bone['control_start'] = "-30.0"
    new_bone['control_end'] = "30.0"
    new_bone['control_rest'] = "0"
    new_bone['control_index'] = str(nbr+1)
    undo.exchange(spec_bone, new_bone)
    for item in editor.Root.subitems:
        if item.type == ":mc" and item.name.startswith(folder_name):
            new_comp = item.copy()
            new_comp["bone_control_" + str(nbr+1)] = spec_bone.name
            undo.exchange(item, new_comp)
    editor.ok(undo, "add bone control")

#
# This function removes a bone control from the specified bone and all its components.
#
def remove_bone_control(editor, spec_bone):
    folder_name = spec_bone.name.split("_")[0]
    undo = quarkx.action()
    new_bone = spec_bone.copy()
    new_bone['control_type'] = ""
    new_bone['control_start'] = ""
    new_bone['control_end'] = ""
    new_bone['control_rest'] = ""
    new_bone['control_index'] = ""
    undo.exchange(spec_bone, new_bone)
    for item in editor.Root.subitems:
        if item.type == ":mc" and item.name.startswith(folder_name):
            new_comp = item.copy()
            keys = new_comp.dictspec.keys()
            for key in keys:
                if key.startswith("bone_control_") and (new_comp.dictspec[key] == spec_bone.name):
                    new_comp[key] = ""
                    break
            undo.exchange(item, new_comp)
    editor.ok(undo, "remove bone control")

#
# This function attaches 1st bone selected (based on tree-view order) to 2nd bone selected as its parent.
#
def attach_bone1to2(editor, bone1, bone2):
    new_bone = bone1.copy()
    new_bone['parent_name'] = bone2.name
    bone_length = (bone1.position - bone2.position)
    new_bone['bone_length'] = bone_length.tuple
    undo = quarkx.action()
    undo.exchange(bone1, new_bone)
    if bone2['parent_name'] == bone1.name:
        new_bone = bone2.copy()
        new_bone['parent_name'] = "None"
        new_bone['bone_length'] = (0.0,0.0,0.0)
        undo.exchange(bone2, new_bone)
    editor.ok(undo, "attach bone 1 to 2")

#
# This function attaches 2nd bone selected (based on tree-view order) to 1st bone selected as its parent.
#
def attach_bone2to1(editor, bone1, bone2):
    new_bone = bone2.copy()
    new_bone['parent_name'] = bone1.name
    bone_length = (bone2.position - bone1.position)
    new_bone['bone_length'] = bone_length.tuple
    undo = quarkx.action()
    undo.exchange(bone2, new_bone)
    if bone1['parent_name'] == bone2.name:
        new_bone = bone1.copy()
        new_bone['parent_name'] = "None"
        new_bone['bone_length'] = (0.0,0.0,0.0)
        undo.exchange(bone1, new_bone)
    editor.ok(undo, "attach bone 2 to 1")

#
# This function detaches bone from its parent bone.
#
def detach_bone(editor, bone):
    new_bone = bone.copy()
    new_bone['parent_name'] = "None"
    new_bone['bone_length'] = (0.0,0.0,0.0)
    undo = quarkx.action()
    undo.exchange(bone, new_bone)
    editor.ok(undo, "detach bones")

#
# This function aligns 1st bone selected (based on tree-view order) to 2nd selected bones position.
#
def align__bone1to2(editor, bone1, bone2):
    undo = quarkx.action()
    skeletongroup = editor.Root.dictitems['Skeleton:bg']  # get the bones group
    bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
    new_bone = bone1.copy()
    newpoint = bone2.position
    new_bone['position'] = newpoint.tuple
    new_bone['draw_offset'] = bone2.dictspec['draw_offset']
    if new_bone.dictspec.has_key("parent_name") and new_bone.dictspec['parent_name'] != "None":
        for bone in bones:
            if bone.name == new_bone.dictspec['parent_name']:
                new_bone['bone_length'] = (new_bone.position - bone.position).tuple
    undo.exchange(bone1, new_bone)
    for bone in bones:
        if bone.dictspec.has_key("parent_name") and bone.dictspec['parent_name'] == bone1.name:
            new_bone = bone.copy()
            new_bone['bone_length'] = (new_bone.position - bone2.position).tuple
            undo.exchange(bone, new_bone)
    try:
        bone1_frames = self.editor.ModelComponentList['bonelist'][bone1.name]['frames']
        bone2_frames = self.editor.ModelComponentList['bonelist'][bone2.name]['frames']
        bone1_keys = bone1_frames.keys()
        bone2_keys = bone2_frames.keys()
        if len(bone1_frames) <= len(bone2_frames):
            for i in range(len(bone1_keys)):
                bone1_frames[bone1_keys[i]]['position'] = bone2_frames[bone2_keys[i]]['position']
        else:
            for i in range(len(bone2_keys)):
                bone1_frames[bone1_keys[i]]['position'] = bone2_frames[bone2_keys[i]]['position']
    except:
        pass
    editor.ok(undo, "align bone 1 to 2")

#
# This function aligns 2nd bone selected (based on tree-view order) to 1st selected bones position.
#
def align__bone2to1(editor, bone1, bone2):
    undo = quarkx.action()
    skeletongroup = editor.Root.dictitems['Skeleton:bg']  # get the bones group
    bones = skeletongroup.findallsubitems("", ':bone')    # get all bones
    new_bone = bone2.copy()
    newpoint = bone1.position
    new_bone['position'] = newpoint.tuple
    new_bone['draw_offset'] = bone1.dictspec['draw_offset']
    if new_bone.dictspec.has_key("parent_name"):
        for bone in bones:
            if bone.name == new_bone.dictspec['parent_name']:
                new_bone['bone_length'] = (new_bone.position - bone.position).tuple
    undo.exchange(bone2, new_bone)
    for bone in bones:
        if bone.dictspec.has_key("parent_name") and bone.dictspec['parent_name'] == bone2.name:
            new_bone = bone.copy()
            new_bone['bone_length'] = (new_bone.position - bone1.position).tuple
            undo.exchange(bone, new_bone)
    try:
        bone1_frames = self.editor.ModelComponentList['bonelist'][bone1.name]['frames']
        bone2_frames = self.editor.ModelComponentList['bonelist'][bone2.name]['frames']
        bone1_keys = bone1_frames.keys()
        bone2_keys = bone2_frames.keys()
        if len(bone2_frames) <= len(bone1_frames):
            for i in range(len(bone2_keys)):
                bone2_frames[bone2_keys[i]]['position'] = bone1_frames[bone1_keys[i]]['position']
        else:
            for i in range(len(bone1_keys)):
                bone2_frames[bone2_keys[i]]['position'] = bone1_frames[bone1_keys[i]]['position']
    except:
        pass
    editor.ok(undo, "align bone 2 to 1")

#
# This function assigns\releases vertices of the currently seledted comp for the bone RMB clicked on.
#
def assign_release_vertices(editor, bone, comp, vtxsellist):
    new_bone = bone.copy()
    old_vertices = new_bone.vtxlist
    if old_vertices.has_key(comp.name):
        old_vertices_comp = old_vertices[comp.name]
    else:
        old_vertices_comp = []
    for vtx in vtxsellist:
        if (vtx in old_vertices_comp) and (editor.ModelComponentList[comp.name]['bonevtxlist'].has_key(bone.name)) and (vtx in editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name].keys()):
            old_vertices_comp.remove(vtx)
            del editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name][vtx]
            continue
        else:
            if not editor.ModelComponentList[comp.name]['bonevtxlist'].has_key(bone.name):
                editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name] = {}
            if not editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name].has_key(vtx):
                editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name][vtx] = {}
            editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name][vtx]['color'] = new_bone["_color"]
            old_vertices_comp = old_vertices_comp + [vtx]
    if len(editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name]) == 0:
        del editor.ModelComponentList[comp.name]['bonevtxlist'][bone.name]
    old_vertices_comp.sort()
    old_vertices[comp.name] = old_vertices_comp
    if len(old_vertices[comp.name]) == 0:
        if new_bone.vtx_pos.has_key(comp.name):
            new_bone.vtx_pos ={}
        del old_vertices[comp.name]
    new_bone.vtxlist = old_vertices
    if len(new_bone.vtx_pos) == 0:
        new_bone.vtx_pos = old_vertices
        new_bone['component'] = comp.name
        # Dupe call but needs to be here to update the bone in case it is not selected in the tree-view.
        Rebuild_Bone(editor, new_bone, editor.Root.currentcomponent.currentframe)

    # Updates the ModelComponentList weightvtxlist.
    Old_dictionary_list = None
    if editor.ModelComponentList[comp.name]['weightvtxlist'] != {}:
        Old_dictionary_list = editor.ModelComponentList[comp.name]['weightvtxlist']
    for vertex_index in vtxsellist:
        if Old_dictionary_list is not None and Old_dictionary_list.has_key(vertex_index):
            vertex_list = Old_dictionary_list[vertex_index]
            vertex_list_keys = vertex_list.keys()
            if new_bone.name in vertex_list_keys:
                for key in vertex_list_keys:
                    if key == new_bone.name:
                        del vertex_list[key]
                if len(vertex_list) == 0:
                    del Old_dictionary_list[vertex_index]
                import mdlmgr # Import needs to be here to avoid error.
                from mdlmgr import treeviewselchanged
                mdlmgr.treeviewselchanged = 1
            else:
                update_weightvtxlist(editor, vertex_index, new_bone)
        else:
            update_weightvtxlist(editor, vertex_index, new_bone)
    undo = quarkx.action()
    undo.exchange(bone, new_bone)
    editor.ok(undo, "assign-release vertices")
    # This section updates the "Vertex Weights Dialog" if it is opened and needs to update.
    formlist = quarkx.forms(1)
    for f in formlist:
        try:
            if f.caption == "Vertex Weights Dialog":
                import mdlentities # Import needs to be here to avoid error.
                mdlentities.macro_updatedialog(None)
        except:
            pass

#
# This recreates the bone's drag handle, o being the bone object (the bone).
# frame = editor.Root.dictitems[o.dictspec['component']].dictitems['Frames:fg'].subitems[editor.bone_frame]
# This does not need to be returned since it is changing the object itself.
def Rebuild_Bone(editor, o, frame):
    try:
        o.position = quarkx.vect(editor.ModelComponentList['bonelist'][o.name]['frames'][frame.name]['position'])
        o['position'] = o.position.tuple
    except:
        if len(o.vtx_pos) != 0:
            if not o.name in editor.ModelComponentList['bonelist'].keys():
                editor.ModelComponentList['bonelist'][o.name] = {}
                editor.ModelComponentList['bonelist'][o.name]['frames'] = {}
                editor.ModelComponentList['bonelist'][o.name]['type'] = 'default'
            frames = editor.Root.dictitems[o.dictspec['component']].dictitems['Frames:fg'].subitems
            for frame2 in frames:
                vertices = frame2.vertices
                vtxlist = o.vtx_pos[o.dictspec['component']]
                vtxpos = quarkx.vect(0.0, 0.0, 0.0)
                for vtx in vtxlist:
                    try:
                        vtxpos = vtxpos + vertices[vtx]
                    except:
                        return
                vtxpos = vtxpos/ float(len(vtxlist))
                editor.ModelComponentList['bonelist'][o.name]['frames'][frame2.name] = {}
                editor.ModelComponentList['bonelist'][o.name]['frames'][frame2.name]['position'] = (vtxpos + quarkx.vect(o.dictspec['draw_offset'])).tuple
                editor.ModelComponentList['bonelist'][o.name]['frames'][frame2.name]['rotmatrix'] = o.rotmatrix.tuple
                if frame2.name == frame.name:
                    o.position = vtxpos + quarkx.vect(o.dictspec['draw_offset'])
                    o['position'] = o.position.tuple



###############################
#
# Selection functions
#
###############################


def SkinVertexSel(editor, sellist):
    "Used when a single or multiple vertexes are selected in the Skin-view"
    "by 'picking' them individually or by using the Red Rectangle Selector."
    "The selected Skin vertexes will be added, if not already selected, to the SkinVertexSelList."
    "The first Skin vertex in the SkinVertexSelList will always be used as the Skin-view's 'base' vertex."
    "You will need to call to redraw the Skin-view for this list once it is updated to display the selections."

    # Equivalent of skinpick_cleared in mdlhandles.py file.
    if sellist == []:
        editor.SkinVertexSelList = []
        return

    if len(sellist) > 1:
        setup = quarkx.setupsubset(SS_MODEL, "Options")
        if not setup["SingleVertexDrag"]:
    # Compares the 1st Skin-view vertex position in the sellist to all others 3D position (pos) and places the
    #    last one that matches at the front of the sellist as the 'base vertex' to be drawn so it can be seen.
            holditem = sellist[0]
            for item in range (len(sellist)):
                if item == 0:
                    pass
                else:
                    if holditem[0] == sellist[item][0]:
                        holditem = sellist[item]
            dupe = holditem
            sellist.remove(dupe)
            sellist = [holditem] + sellist
        else:
            newlist = []
            for item in range (len(sellist)):
                holditem = sellist[item]
                if newlist == []:
                    newlist = newlist + [holditem]
                    continue
                compaircount = -1
                for compairitem in newlist:
                    compaircount = compaircount + 1
                    if str(holditem[0]) == str(compairitem[0]):
                        break
                if compaircount == len(newlist)-1:
                    newlist = newlist + [holditem]
            sellist = newlist
    # Compares the 1st Skin-view vertex position in the sellist to all others 3D position (pos) and places the
    #    last one that matches at the front of the sellist as the 'base vertex' to be drawn so it can be seen.
            holditem = sellist[0]
            for item in range (len(sellist)):
                if item == 0:
                    pass
                else:
                    if holditem[0] == sellist[item][0]:
                        holditem = sellist[item]
            dupe = holditem
            sellist.remove(dupe)
            sellist = [holditem] + sellist

  # Checks for and removes any duplications of items in the list.
    for vertex in sellist:
        itemcount = 0
        if editor.SkinVertexSelList == []:
            editor.SkinVertexSelList = editor.SkinVertexSelList + [vertex]
            if len(sellist) == 1:
                return
        else:
            for item in editor.SkinVertexSelList:
                itemcount = itemcount + 1
                if vertex[2] == item[2] and  vertex[3] == item[3]:
                    editor.SkinVertexSelList.remove(item)
                    break
                elif itemcount == len(editor.SkinVertexSelList):
                    editor.SkinVertexSelList = editor.SkinVertexSelList + [vertex]



def PassSkinSel2Editor(editor):
    "For passing selected vertexes(faces) from the Skin-view to the Editor's views."
    "After you call this function you will need to also call to draw the handels in the views."
    "This uses the SkinVertexSelList for passing to the ModelVertexSelList."
    "How to convert from the SkinVertexSelList to the ModelVertexSelList using tri_index and ver_index."
    " tri_index = tris[vtx[2]] this is the 3rd item in a SkinVertexSelList item."
    " ver_index = tris[vtx[2]][vtx[3]][0] this is the 4th item in a SkinVertexSelList item."
    "The above indexes are used to find the corresponding triangle vertex index in the model meshes triangles."
    "Also see the explanation of 'PassEditorSel2Skin' below for further detail."

    tris = editor.Root.currentcomponent.triangles
    for vtx in editor.SkinVertexSelList:
        try: # Needs to be in this try statement in case the component has no vertexes.
            if editor.ModelVertexSelList == []:
                editor.ModelVertexSelList = editor.ModelVertexSelList + [tris[vtx[2]][vtx[3]][0]]
            else:
                for vertex in range(len(editor.ModelVertexSelList)):
                    if tris[vtx[2]][vtx[3]][0] == editor.ModelVertexSelList[vertex]:
                        break
                    if vertex == len(editor.ModelVertexSelList)-1:
                        editor.ModelVertexSelList = editor.ModelVertexSelList + [tris[vtx[2]][vtx[3]][0]]
        except:
            continue



def PassEditorSel2Skin(editor, option=1):
    "For passing selected vertexes(faces) from the Editor's views to the Skin-view."
    "After you call this function you will need to also call to draw the handels in the Skin-view."
    "The 'option' value of 1 uses the ModelVertexSelList for passing individual selected vertexes to the Skin-view."
    "The 'option' value of 2 uses the ModelFaceSelList for passing selected 'faces' vertexes to the Skin-view."
    "The 'option' value of 3 uses the SkinFaceSelList for passing selected 'faces' vertexes but retains its own data"
    "which is used to draw the highlighted outlines of the Skin-view selected faces in the qbaseeditor.py 'finishdrawing' function."
    "All three will be applied to the Skin-view's SkinVertexSelList of 'existing' vertex selection, if any."
    " See the mdleditor.py file (very beginning) for each individual item's, list of items-their format."
    "     tri_index (or editor_tri_index in the case below) = tris[tri]"
    "     tri being the sequential number (starting with zero) as it iterates (counts)"
    "     through the list of 'component triangles'."

    "     ver_index = tris[tri][vertex][0]"
    "     [vertex] being each vertex 'item' of the triangle as we iterate through all 3 of them"
    "     and [0] being the 1st item in each of the triangles vertex 'items'. That is ...(see below)"

    "     Each triangle vertex 'item' is another list of items, the 1st item being its ver_index,"
    "     where this vertex lies in a 'frames vertices' list of vertexes."
    "     Each 'frame' has its own list that gives every vertex point of the models mesh for that frame."
    "     Or, each of the 'frame vertices' is the actual 3D position of that triangles vertex 'x,y,z point'."

    "     (see skinvtx_index below, the models mesh and skin mesh vertex formats are not the same.)"
    "     The Skin-view has no triangles, it only uses a list of vertices."
    "     That list of vertices is made up in the same order that the 'frame vertices' lists are."
    "     Which is starting with the 1st vertex of the 1st triangle"
    "     and ending with the last vertex of the last triangle. This list make up the Skin-view view.handles."
    "     Therefore, you can call for a specific triangles Skin-view vertex"
    "     by using that triangles 'item' ver_index number."
    "     The 1st item in the models mesh ver_index is that vertexe's position in the 'Frame objects vertices' list"
    "     AND the Skin-view's view.handles list."

    "     All 3 of the items in the models 'skin mesh' (or view.handles)"
    "     are in the same 'order' of the triangle (0, 1, 2) vertexes."
    "     So for each model components mesh triangle in the Editor,"
    "     there are 3 vertex view.handles in the Skin-view mesh"
    "     and why we need to iterate through the Skin-view view.handles"
    "     to match up its corresponding triangle vertex."

    "     Another way to call a triangles Skin-view 'view.handles' would be with the following formula:"
    "     (tri_index * 3) + its vertex position number, either 0, 1 or 2. For example to get the 3 view.handles of tri_index 5:"
    "         from mdlhandles import SkinView1                   "
    "         if SkinView1 is not None:                          "
    "             vertex0 = SkinView1.handles[(tri_index*3)+0]   "
    "             vertex1 = SkinView1.handles[(tri_index*3)+1]   "
    "             vertex2 = SkinView1.handles[(tri_index*3)+2]   "

    tris = editor.Root.currentcomponent.triangles
    from mdlhandles import SkinView1
    import mdlhandles
    skinhandle = None

    if option == 1:
        vertexlist = editor.ModelVertexSelList
        if editor.Root.currentcomponent is None:
            componentnames = []
            for item in editor.Root.dictitems:
                if item.endswith(":mc"):
                    componentnames.append(item)
            componentnames.sort()
            editor.Root.currentcomponent = editor.Root.dictitems[componentnames[0]]
        comp = editor.Root.currentcomponent
        commontris = []
        vertices = comp.currentframe.vertices
        for vert in vertexlist:
            commontris = commontris + findTrianglesAndIndexes(comp, vert, vertices[vert])

    if option == 2:
        vertexlist = []
        for tri_index in editor.ModelFaceSelList:
            for vertex in range(len(tris[tri_index])):
                vtx = tris[tri_index][vertex][0]
                vertexlist = vertexlist + [[vtx, tri_index]]

    if option == 3:
        vertexlist = []
        for tri_index in editor.SkinFaceSelList:
            for vertex in range(len(tris[tri_index])):
                vtx = tris[tri_index][vertex][0]
                vertexlist = vertexlist + [[vtx, tri_index]]

    if option == 1:
        for vert in commontris:
            editor_tri_index = vert[2]
            skinvtx_index = vert[3]
            if SkinView1 is not None:
                if editor.SkinVertexSelList == []:
                    for handle in SkinView1.handles:
                        if (isinstance(handle, mdlhandles.LinRedHandle)) or (isinstance(handle, mdlhandles.LinSideHandle)) or (isinstance(handle, mdlhandles.LinCornerHandle)):
                            continue
                        # Here we compair the Skin-view handle (in its handles list) tri_index item
                        #    to the editor_tri_index we got above to see if they match.
                        # The same applies to the comparison of the Skin-view handel ver_index and skinvtx_index.
                        try:
                            if handle.tri_index == editor_tri_index and handle.ver_index == skinvtx_index:
                                skinhandle = handle
                                break
                        except:
                            return
                    if skinhandle is not None:
                        editor.SkinVertexSelList = editor.SkinVertexSelList + [[skinhandle.pos, skinhandle, skinhandle.tri_index, skinhandle.ver_index]]
                else:
                    for handle in SkinView1.handles:
                        if (isinstance(handle, mdlhandles.LinRedHandle)) or (isinstance(handle, mdlhandles.LinSideHandle)) or (isinstance(handle, mdlhandles.LinCornerHandle)):
                            continue
                        if handle.tri_index == editor_tri_index and handle.ver_index == skinvtx_index:
                            skinhandle = handle
                            break
                    if skinhandle is not None:
                        for vertex in range(len(editor.SkinVertexSelList)):
                            if editor.SkinVertexSelList[vertex][2] == skinhandle.tri_index and editor.SkinVertexSelList[vertex][3] == skinhandle.ver_index:
                               break
                            if vertex == len(editor.SkinVertexSelList)-1:
                                editor.SkinVertexSelList = editor.SkinVertexSelList + [[skinhandle.pos, skinhandle, skinhandle.tri_index, skinhandle.ver_index]]

    if option == 2 or option == 3:
        editor_tri_index = None
        for vtx in vertexlist:
            ver_index = vtx[0]
            if editor.SkinVertexSelList == []:
                for vertex in range(len(tris[vtx[1]])):
                    if ver_index == tris[vtx[1]][vertex][0]:
                        editor_tri_index = vtx[1]
                        skinvtx_index = vertex
                        break
                if editor_tri_index is None:
                    continue
                if SkinView1 is None:
                    pass
                else:
                    for handle in SkinView1.handles:
                        if (isinstance(handle, mdlhandles.LinRedHandle)) or (isinstance(handle, mdlhandles.LinSideHandle)) or (isinstance(handle, mdlhandles.LinCornerHandle)):
                            continue
                        # Here we compair the Skin-view handle (in its handles list) tri_index item
                        #    to the editor_tri_index we got above to see if they match.
                        # The same applies to the comparison of the Skin-view handel ver_index and skinvtx_index.
                        try:
                            if handle.tri_index == editor_tri_index and handle.ver_index == skinvtx_index:
                                skinhandle = handle
                                break
                        except:
                            return
                    if skinhandle is not None:
                        editor.SkinVertexSelList = editor.SkinVertexSelList + [[skinhandle.pos, skinhandle, skinhandle.tri_index, skinhandle.ver_index]]
            else:
                for vertex in range(len(tris[vtx[1]])):
                    if ver_index == tris[vtx[1]][vertex][0]:
                        editor_tri_index = vtx[1]
                        skinvtx_index = vertex
                        break
                if editor_tri_index is None: continue
                for handle in SkinView1.handles:
                    if (isinstance(handle, mdlhandles.LinRedHandle)) or (isinstance(handle, mdlhandles.LinSideHandle)) or (isinstance(handle, mdlhandles.LinCornerHandle)):
                        continue
                    if handle.tri_index == editor_tri_index and handle.ver_index == skinvtx_index:
                        skinhandle = handle
                        break
                if skinhandle is not None:
                    for vertex in range(len(editor.SkinVertexSelList)):
                        if editor.SkinVertexSelList[vertex][2] == skinhandle.tri_index and editor.SkinVertexSelList[vertex][3] == skinhandle.ver_index:
                            break
                        if vertex == len(editor.SkinVertexSelList)-1:
                            editor.SkinVertexSelList = editor.SkinVertexSelList + [[skinhandle.pos, skinhandle, skinhandle.tri_index, skinhandle.ver_index]]

    # Compares the 1st Skin-view vertex position in the sellist to all others 3D position (pos) and places the
    #    last one that matches at the front of the sellist as the 'base vertex' to be drawn so it can be seen.
    if len(editor.SkinVertexSelList) > 1:
        holditem = editor.SkinVertexSelList[0]
        for item in range (len(editor.SkinVertexSelList)):
            if item == 0:
                pass
            else:
                if holditem[0] == editor.SkinVertexSelList[item][0]:
                    holditem = editor.SkinVertexSelList[item]
        dupe = holditem
        editor.SkinVertexSelList.remove(dupe)
        editor.SkinVertexSelList = [holditem] + editor.SkinVertexSelList



###############################
#
# Misc Group functions
#
###############################

#
# This function removes all tagss and CLEARS ALL selection lists
# to avoid errors in case there are tagss that exist but all components have been deleted.
# It will also replace the 'Misc:mg' if it has been deleted by the user.
#
def clearMiscGroup(editor, undomsg, undo=None):
    import mdlmgr
    from mdlmgr import treeviewselchanged
    mdlmgr.treeviewselchanged = 1
    editor.layout.explorer.sellist = []
    editor.layout.explorer.uniquesel = None
    if undo is None:
        undo = quarkx.action()
    miscgroup = quarkx.newobj('Misc:mg')
    miscgroup['type'] = chr(6)
    # If all components have been deleted.
    if editor.Root.dictitems.has_key("Misc:mg"):
        undo.exchange(editor.Root.dictitems['Misc:mg'], miscgroup)
    else:
        # If the 'Misc:mg' has been deleted.
        insertbefore = None
        for item in editor.Root.subitems:
            if item.type == ":bg" or item.type == ":mc":
                insertbefore = item
                break
        if insertbefore is not None:
            undo.put(editor.Root, miscgroup, insertbefore)
        else:
            undo.put(editor.Root, miscgroup)
    editor.ok(undo, undomsg)



###############################
#
# Tag & Tag Frame functions
#
###############################


#
# This function adds a :tag object to the Misc group at position pos for each selected component in the complist.
#
def addtag(editor, complist, pos):
    comp_FramesGroup = complist[len(complist)-1].dictitems['Frames:fg']
    comp_frames = comp_FramesGroup.subitems
    if len(complist) > 1:
        for comp in complist:
            if len(comp.dictitems['Frames:fg'].subitems) != len(comp_frames):
                quarkx.beep() # Makes the computer "Beep" once .
                quarkx.msgbox("FRAME COUNT ERROR !\n\nNot all components selected for this\ntag have the same number of frames.\n\nCorrect and try again.", MT_ERROR, MB_OK)
                return
    keys = comp_FramesGroup.dictitems.keys()
    for key in range(len(keys)):
        if keys[key] == "baseframe:mf":
            break
        if key == len(keys)-1:
            quarkx.beep() # Makes the computer "Beep" once .
            quarkx.msgbox("No 'baseframe' !\n\nTo use tags you must have a frame named:\n    baseframe\nthat is the base position of each selected component.\n\nIt is best to have them as the last frame\nand each selected component\nmust have the same number of frames.\n\nCorrect and try again.", MT_ERROR, MB_OK)
            return
    name = None
    comparenbr = 0
    miscgroup = editor.Root.dictitems['Misc:mg']   # get the misc group
    tags = miscgroup.findallsubitems("", ':tag')   # get all tags
    compname = complist[len(complist)-1].name
    compbasename = complist[len(complist)-1].shortname
    compbasename = compbasename.split("_")[0]
    for item in tags:
        if item.shortname.startswith(compbasename + '_tag_NewTag'):
            getnbr = item.shortname
            getnbr = getnbr.split('_tag_NewTag')[1]
            if getnbr == "":
                nbr = 0
            else:
                nbr = int(getnbr)
            if nbr > comparenbr:
                comparenbr = nbr
            nbr = comparenbr + 1
            name = compbasename + "_tag_NewTag" + str(nbr)
    if name is None:
        name = compbasename + "_tag_NewTag1"
    # First we make the tag.
    new_tag = quarkx.newobj(name + ":tag")
    new_tag['Component'] = compname
    new_tag['show'] = (1.0,)
    # Now we make its tag_frames.
    baseframe = comp_FramesGroup.dictitems['baseframe:mf']
    if len(comp_frames) == 1:
        tagframe = quarkx.newobj('Tag baseframe:tagframe')
        tagframe['origin'] = pos.tuple
        if baseframe.dictspec.has_key('rotmatrix'):
            tagframe['rotmatrix'] = baseframe.dictspec['rotmatrix']
        else:
            tagframe['rotmatrix'] = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        tagframe['show'] = (1.0,)
        new_tag.appenditem(tagframe)
    else:
        vertices = baseframe.vertices
        vtxpos = quarkx.vect(0, 0, 0)
        for vtx in range(len(vertices)):
            vtxpos = vtxpos + vertices[vtx]
        vtx_center_pos = vtxpos/ float(len(vertices))
        offset = pos - vtx_center_pos
        for frame in range(len(comp_frames)):
            vertices = comp_frames[frame].vertices
            vtxpos = quarkx.vect(0, 0, 0)
            for vtx in range(len(vertices)):
                vtxpos = vtxpos + vertices[vtx]
            vtx_center_pos = vtxpos/ float(len(vertices))
            if frame == len(comp_frames)-1:
                tagframe = quarkx.newobj('Tag baseframe:tagframe')
            else:
                tagframe = quarkx.newobj('Tag Frame ' + str(frame+1) + ':tagframe')
            tagframe['origin'] = (vtx_center_pos + offset).tuple
            if comp_frames[frame].dictspec.has_key('rotmatrix'):
                tagframe['rotmatrix'] = comp_frames[frame].dictspec['rotmatrix']
            else:
                tagframe['rotmatrix'] = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
            tagframe['show'] = (1.0,)
            new_tag.appenditem(tagframe)

    # Now we update the components.
    undo = quarkx.action()
    for comp in complist:
        new_comp = comp.copy()
        if new_comp.dictspec.has_key("tag_components"):
            tag_comps_list = new_comp.dictspec['tag_components'].split(", ")
            for comp2 in complist:
                if comp2.name in tag_comps_list:
                    continue
                else:
                    tag_comps_list = tag_comps_list + [comp2.name]
            for comp2 in range(len(tag_comps_list)):
                if comp2 == 0:
                    new_comp['tag_components'] = tag_comps_list[comp2]
                else:
                    new_comp['tag_components'] = new_comp.dictspec['tag_components'] + ", " + tag_comps_list[comp2]
        else:
            for comp2 in range(len(complist)):
                if comp2 == 0:
                    new_comp['tag_components'] = complist[comp2].name
                else:
                    new_comp['tag_components'] = new_comp.dictspec['tag_components'] + ", " + complist[comp2].name
        if new_comp.name == complist[len(complist)-1].name:
            new_tagname = new_tag.shortname.split(compbasename + "_")[1]
            if new_comp.dictspec.has_key("Tags"):
                Tags_list = new_comp.dictspec['Tags'].split(", ")
                if new_tagname in Tags_list:
                    pass
                else:
                    Tags_list = Tags_list + [new_tagname]
                    for Tag in range(len(Tags_list)):
                        if Tag == 0:
                            new_comp['Tags'] = Tags_list[Tag]
                        else:
                            new_comp['Tags'] = new_comp.dictspec['Tags'] + ", " + Tags_list[Tag]
            else:
                new_comp['Tags'] = new_tagname
        undo.exchange(comp, new_comp)

    undo.put(miscgroup, new_tag)
    editor.ok(undo, "added tag - " + new_tag.shortname)


#
# This function will delete a single tag and its tag frames from the 'Misc' group, all components it belongs to will remain.
#
def deletetag(editor, tag_to_del):
    undo = quarkx.action()
    deltag = tag_to_del.name.replace(":tag", "")
    deltag = deltag.split("_tag_")
    deltagfile = deltag[0]
    deltagname = "tag_" + deltag[1]
    comps = editor.Root.findallsubitems("", ':mc')   # find all components
    for comp in comps:
        if comp.dictspec.has_key('Tags') and comp.name.startswith(deltagfile):
            checktags = comp.dictspec['Tags'].split(", ")
            if deltagname in checktags:
                newcomp = comp.copy()
                oldtags = newcomp.dictspec['Tags'].split(", ")
                newtags = ""
                count = 0
                for tag in oldtags:
                    if count == 0 and tag != deltagname:
                        newtags = tag
                        count = 1
                    elif tag != deltagname:
                        newtags = newtags + ", " + tag
                newcomp['Tags'] = newtags
                if len(newtags) == 0:
                    tag_components = comp.dictspec['tag_components'].split(", ")
                    for comp2 in tag_components:
                        if comp2 == comp.name:
                            continue
                        old_comp2 = editor.Root.dictitems[comp2]
                        new_comp2 = old_comp2.copy()
                        tag_components2 = new_comp2.dictspec['tag_components'].split(", ")
                        new_tag_components2 = ""
                        count = 0
                        for comp_name2 in tag_components2:
                            if comp_name2 in tag_components:
                                continue
                            else:
                                if count == 0:
                                    new_tag_components2 = comp_name2
                                    count = 1
                                else:
                                    new_tag_components2 = new_tag_components2 + ", " + comp_name2
                        new_comp2['tag_components'] = new_tag_components2
                        undo.exchange(old_comp2, new_comp2)
                    newcomp['tag_components'] = ""
                undo.exchange(comp, newcomp)
    undo.exchange(tag_to_del, None)
    editor.ok(undo, "tag deleted - " + tag_to_del.shortname)



###############################
#
# Texture handling functions
#
###############################


#
# Changes the u and v skinning coords in the Skin-view for all faces (triangles)
# of the currentcomponent and updates its "Tris" u, v values based on the
# size of the currentskin in the Skin-view at the time this function is called.
#
def skinrescale(editor):
    import mdlhandles
    from mdlhandles import SkinView1
    comp = editor.Root.currentcomponent
    skin = comp.currentskin
    if comp is None:
        quarkx.msgbox("No Current Component Selected !\n\nYou need to select a component\nto activate this function.\n\nPress 'F1' for InfoBase help\nof this function for details.\n\nAction Canceled.", MT_ERROR, MB_OK)
        return
    if skin is None:
        quarkx.msgbox("No Skin Texture Exist !\n\nYou need to import a skin texture\nfrom the 'Texture Browser' to activate this function.\n\nPress 'F1' for InfoBase help\nof this function for details.\n\nAction Canceled.", MT_ERROR, MB_OK)
        return
    if SkinView1 is None:
        quarkx.msgbox("No Skin Handles Exist !\n\nPress 'F1' for InfoBase help\nof this function for details.\n\nAction Canceled.", MT_ERROR, MB_OK)
        return
    new_texWidth, new_texHeight = skin["Size"]
    old_texWidth, old_texHeight = comp.dictspec['skinsize']
    if new_texWidth == old_texWidth and new_texHeight == old_texHeight:
        return
    new_comp = comp.copy()
    new_comp['skinsize'] = skin["Size"]
    texWidth_scale = new_texWidth / old_texWidth
    texHeight_scale = new_texHeight / old_texHeight

    # Because the original list can not be changed, we use a dummy list copy
    # then pass the updated values back to the original list, and so on, in a loop.
    newtris = tris = comp.triangles
    for i in range(len(tris)): # i is the tri_index based on its position in the 'Tris' frame list.
        tri = tris[i]
        for j in range(len(tri)): # j is the vert_index, either 0, 1 or 2 vertex of the triangle.
                                    # To calculate a triangle's vert_index number = (i * 3) + j
            u = int(round(tri[j][1] * texWidth_scale))
            v = int(round(tri[j][2] * texHeight_scale))
            if j == 0:
                vtx0 = (tri[j][0], u, v)
            elif j == 1:
                vtx1 = (tri[j][0], u, v)
            else:
                vtx2 = (tri[j][0], u, v)
        tri = (vtx0, vtx1, vtx2)
        newtris[i:i+1] = [tri]
    new_comp.triangles = newtris

    # Now we need to rebuilt the Skin-view handles.
    mdlhandles.buildskinvertices(editor, SkinView1, editor.layout, new_comp, skin)

    # Finally the undo exchange is made and ok called to finish the function.
    undo = quarkx.action()
    undo.exchange(comp, new_comp)
    editor.ok(undo, "Skin-view rescaled")


#
# Changes the selected faces (triangles), in the ModelFaceSelList of the editor,
# u and v skinning coords based on the editor3Dview positions
# which also changes their layout in the Skin-view causing a
# "re-mapping" of those selected faces skin positions.
#
def skinremap(editor):
    comp = editor.Root.currentcomponent
    if (comp is None) or (comp.currentframe is None) or (editor.ModelFaceSelList == []):
        quarkx.msgbox("Improper Action !\n\nYou need to select at least one\nface of a component to be re-skinned\nto activate this function.\n\nPress 'F1' for InfoBase help\nof this function for details.\n\nAction Canceled.", MT_ERROR, MB_OK)
        return
    new_comp = comp.copy()
    framevtxs = comp.currentframe.vertices

    # Sets the editors 3D view to get the new u,v co-ordinances from.
    for v in editor.layout.views:
        if v.info["viewname"] == "editors3Dview":
            cordsview = v

    # Changes the old u,v Skin-view position values for each selected face
    # to the new ones and replaces those old triangles with the updated ones.
    for tri_index in editor.ModelFaceSelList:
        # Because the original list can not be changed, we use a dummy list copy
        # then pass the updated values back to the original list, and so on, in a loop.
        newtris = new_comp.triangles
        for vtx in range(len(comp.triangles[tri_index])):
            u = int(cordsview.proj(framevtxs[comp.triangles[tri_index][vtx][0]]).tuple[0])
            v = int(cordsview.proj(framevtxs[comp.triangles[tri_index][vtx][0]]).tuple[1])
            if vtx == 0:
                vtx0 = (comp.triangles[tri_index][vtx][0], u, v)
            elif vtx == 1:
                vtx1 = (comp.triangles[tri_index][vtx][0], u, v)
            else:
                vtx2 = (comp.triangles[tri_index][vtx][0], u, v)
        tri = (vtx0, vtx1, vtx2)
        newtris[tri_index:tri_index+1] = [tri]
        new_comp.triangles = newtris

        compframes = new_comp.findallsubitems("", ':mf')   # get all frames
        for compframe in compframes:
            compframe.compparent = new_comp # To allow frame relocation after editing.

    # Finally the undo exchange is made and ok called to finish the function.
    undo = quarkx.action()
    undo.exchange(comp, new_comp)
    editor.ok(undo, "Skin-view remap")
    for view in editor.layout.views:
        if view.viewmode != "wire":
            view.invalidate(1)


#
# view = current view that the cursor is in.
# If one of the editor's views:
#    object = triangleface = a single item list containing the triangle face that the cursor is over.
#    Returns TWO lists (of integers) WITHIN another list, of a texture's pixel u, v
#        position on a triangle where the cursor is located at in any of the views.
#    The first sub-list is used for any of the editor's views.
#       It gives the actual pixel location on the skin texture itself.
#       This sub-list is then used for any of the quarkx 'Texture Functions'
#        to locate and\or change a pixel on a texture, or textures palette if one exist.
#    The second sub-list is strictly used, if desired, to pass to and draw something
#        in the Skin-view, using it's 'canvas()' function, at the same time and
#        pixel location when the cursor is in one of the other editor's views, for example:
#            returnedlist = [[pixU, pixV], [skinpixU, skinpixV]]
#            skinpixU, skinpixV = returnedlist[1]
#            if SkinView1 is not None:
#                texWidth, texHeight = modelfacelist[0][1].currentskin["Size"]
#                skinpix = quarkx.vect(skinpixU-int(texWidth*.5), skinpixV-int(texHeight*.5), 0)
#                skinviewX, skinviewY, skinviewZ = SkinView1.proj(skinpix).tuple
#                skincv = SkinView1.canvas()
#                svs = round(SkinView1.info['scale']*.5)
#                brushwidth = float(quarkx.setupsubset(SS_MODEL, "Options")["Paint_BrushWidth"])
#                svs = int(brushwidth * svs)
#                skincv.rectangle(int(skinviewX)-svs,int(skinviewY)-svs,int(skinviewX)+svs,int(skinviewY)+svs)
#      If the cursor is currently in the Skin-view use as described below.
# If the Skin-view:
#    object (not needed)
#    Returns a single list containing two integers, the texture's pixel u, v position in the Skin-view.
# x and y = the position where the cursor is at in the view as a 'projected' 2D screen view.
#
def TexturePixelLocation(editor, view, x, y, object=None):
    if view.info["viewname"] != "skinview":
        triangleface = object
        if triangleface != []:
            trivtx0, trivtx1, trivtx2 = triangleface[0][1].triangles[triangleface[0][2]]

            facevtx0 = triangleface[0][1].currentframe.vertices[triangleface[0][1].triangles[triangleface[0][2]][0][0]]
            facevtx1 = triangleface[0][1].currentframe.vertices[triangleface[0][1].triangles[triangleface[0][2]][1][0]]
            facevtx2 = triangleface[0][1].currentframe.vertices[triangleface[0][1].triangles[triangleface[0][2]][2][0]]
            
            pixpos = view.space(quarkx.vect(x, y, 0)) # Where the cursor is pointing in the view.

            vectorZ = view.vector("z").normalized
            facenormal = ((facevtx1 - facevtx0) ^ (facevtx2 - facevtx0)).normalized
            pixpos = pixpos - ((((pixpos - facevtx0) * facenormal) / (vectorZ * facenormal)) * vectorZ)

            # Adapted from http://www.blackpawn.com/texts/pointinpoly/default.html
            # Formula to compute u and v for a point on a triangle face:
            # ==========================================================
            # We use trivtx0 as our base, for it's U,V values to multiply our two factors by
            # and get the U,V values for pixpos (where our cursor is at in the 3D view).

            P = pixpos
            A = facevtx0
            B = facevtx1
            C = facevtx2
            # (what we are computing to get) u texture position value
            # (what we are computing to get) v texture position value


            v0 = (C - A)
            v1 = (B - A)
            v2 = (P - A)
            
            dot00 = v0 * v0
            dot01 = v0 * v1
            dot02 = v0 * v2
            dot11 = v1 * v1
            dot12 = v1 * v2

            invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
            V = (dot11 * dot02 - dot01 * dot12) * invDenom
            U = (dot00 * dot12 - dot01 * dot02) * invDenom

            # To draw, by pixel location, in Skin-view using it's 'canvase()' function.
            skinpixU = int((1 - U - V) * trivtx0[1] + U * trivtx1[1] + V * trivtx2[1])+.5
            skinpixV = int((1 - U - V) * trivtx0[2] + U * trivtx1[2] + V * trivtx2[2])+.5

            # The actual pixel location on the skin texture itself.
            pixU = int(skinpixU-.5)
            pixV = int(skinpixV-.5)

            # This section corrects for texture tiling in the editor's views.
            texWidth, texHeight = editor.Root.currentcomponent.currentskin["Size"]
            cursorXpos = pixU
            cursorYpos = pixV

            if cursorXpos >= texWidth-1:
                Xstart = int(cursorXpos / texWidth)
                pixU = int(cursorXpos - (texWidth * Xstart))
            elif cursorXpos < -texWidth:
                Xstart = int(abs(cursorXpos / (texWidth+.5)))
                pixU = int(cursorXpos + (texWidth * Xstart) + texWidth)
            else:
                if cursorXpos >= 1:
                    pixU = cursorXpos
                if cursorXpos <= -1:
                    pixU = cursorXpos + texWidth
                if cursorXpos == 0:
                    pixU = 0

            while pixU >= texWidth:
                pixU = pixU - 1
            while pixU <= -1:
                pixU = texWidth - 1
            pixU = int(pixU)

            if cursorYpos >= texHeight-1:
                Ystart = int(cursorYpos / texHeight)
                pixV = int(cursorYpos - (texHeight * Ystart))
            elif cursorYpos < -texHeight:
                Ystart = int(abs(cursorYpos / (texHeight+.5)))
                pixV = int(cursorYpos + (texHeight * Ystart) + texHeight)
            else:
                if cursorYpos >= 1:
                    pixV = cursorYpos
                if cursorYpos <= -1:
                    pixV = cursorYpos + texHeight
                if cursorYpos == 0:
                    pixV = 0

            while pixV >= texHeight:
                pixV = pixV - 1
            while pixV <= -1:
                pixV = texHeight - 1
            pixV = int(pixV)

            return [[pixU, pixV], [skinpixU, skinpixV]]

    else:
        # This section computes the proper pixU, pixV position values for tiling in the Skin-view.
        texWidth, texHeight = editor.Root.currentcomponent.currentskin["Size"]
        list = view.space(quarkx.vect(x, y, 0)).tuple
        cursorXpos = int(list[0])
        cursorYpos = int(list[1])
        if cursorXpos >= (texWidth * .5):
            Xstart = int((cursorXpos / texWidth) -.5)
            Xpos = -texWidth + cursorXpos - (texWidth * Xstart)
        elif cursorXpos <= (-texWidth * .5):
            Xstart = int((cursorXpos / texWidth) +.5)
            Xpos = texWidth + cursorXpos + (texWidth * -Xstart) - 1
        else:
            if cursorXpos > 0:
                Xpos = cursorXpos
            if cursorXpos < 0:
                Xpos = cursorXpos - 1
            if cursorXpos == 0:
                cursorXpos = list[0]
                if cursorXpos < 0:
                    Xpos = -1
                else:
                    Xpos = 0

        pixU = Xpos + (texWidth * .5)
        while pixU >= texWidth:
            pixU = pixU - 1
        while pixU <= -texWidth:
            pixU = pixU + 1
        pixU = int(pixU)

        if cursorYpos >= (texHeight * .5):
            Ystart = int((cursorYpos / texHeight) -.5)
            Ypos = -texHeight + cursorYpos - (texHeight * Ystart)
        elif cursorYpos <= (-texHeight * .5):
            Ystart = int((cursorYpos / texHeight) +.5)
            Ypos = texHeight + cursorYpos + (texHeight * -Ystart) -1
        else:
            if cursorYpos > 0:
                Ypos = cursorYpos
            if cursorYpos < 0:
                Ypos = cursorYpos - 1
            if cursorYpos == 0:
                cursorYpos = list[1]
                if cursorYpos < 0:
                    Ypos = -1
                else:
                    Ypos = 0

        pixV = Ypos + (texHeight * .5)
        while pixV >= texHeight:
            pixV = pixV - 1
        while pixV <= -texHeight:
            pixV = pixV + 1
        pixV = int(pixV)

        return [pixU, pixV]



###############################
#
# General Editor functions
#
###############################

#
# To have any tags, bones or other items, to avoid errors, this checks that at least one model component exist in the editor.
#
def allowitems(editor):
    for item in editor.Root.dictitems:
        if item.endswith(":mc"):
            return 1
    return 0


def Update_Skin_View(editor, option=1):
    "Updates the Skin-view using virous option settings."
    "option = 0 updates just the upper section."
    "option = 1 updates the upper section and redraws the lower section."
    "option = 2 same a 1 and resets the texture positioning in the lower section."

    import mdlhandles
    from mdlhandles import SkinView1
    comp = editor.Root.currentcomponent
    skin = comp.currentskin
    if option == 0:
        # Updates the upper section only.
        q = editor.layout.skinform.linkedobjects[0]
        q["triangles"] = str(len(comp.triangles))
        q["ownedby"] = comp.shortname
        if skin is not None:
            q["texture"] = skin.name
            texWidth,texHeight = skin["Size"]
            q["skinsize"] = (str(int(texWidth)) + " wide by " + str(int(texHeight)) + " high")
        else:
            q["texture"] = "no skins exist for this component"
            q["skinsize"] = "not available"
        editor.layout.skinform.setdata(q, editor.layout.skinform.form)
        if SkinView1 is not None:
            SkinView1.invalidate()
    if option == 1:
        # Updates the upper section.
        editor.layout.selectskin(skin)
        editor.layout.mpp.resetpage()
        # Updates the lower (view) section.
        if SkinView1 is not None:
            mdlhandles.buildskinvertices(editor, SkinView1, editor.layout, comp, skin)
    if option == 2:
        # Updates the upper section.
        editor.layout.selectskin(skin)
        editor.layout.mpp.resetpage()
        # Updates the lower (view) section and centers the texture.
        if SkinView1 is not None and SkinView1.info is not None:
            viewWidth, viewHeight = SkinView1.clientarea
            try:
                texWidth, texHeight = skin["Size"]
            except:
                texWidth, texHeight = SkinView1.clientarea
            if texWidth > texHeight:
                SkinView1.info["scale"] = viewWidth / texWidth
            elif texWidth < texHeight:
                SkinView1.info["scale"] = viewHeight / texHeight
            elif viewWidth > viewHeight:
                SkinView1.info["scale"] = viewHeight / texHeight
            else:
                SkinView1.info["scale"] = viewWidth / texWidth
            SkinView1.info["center"] = SkinView1.screencenter = quarkx.vect(0,0,0)
            setprojmode(SkinView1)


def Update_Editor_Views(editor, option=4):
    "Updates the Editors views once something has chaged in the Skin-view,"
    "such as synchronized or added 'skin mesh' vertex selections."
    "It can also be used to just update all of the Editor's views or just its 2D views."
    "Various 'option' items are shown below in their proper order of sequence."
    "This is done to increase drawing speed, only use what it takes to do the job."

    import mdleditor
    import mdlhandles
    import qhandles
    import mdlmgr
    mdlmgr.treeviewselchanged = 1
    editorview = editor.layout.views[0]
    newhandles = mdlhandles.BuildCommonHandles(editor, editor.layout.explorer)
    True3Dview = None
    if quarkx.setupsubset(SS_MODEL, "Options")['EditorTrue3Dmode'] == "1":
        for v in editor.layout.views:
            if v.info["viewname"] == "editors3Dview":
                True3Dview = v
    FullTrue3Dview = None
    if quarkx.setupsubset(SS_MODEL, "Options")['Full3DTrue3Dmode'] == "1":
        for v in editor.layout.views:
            if v.info["viewname"] == "3Dwindow" and v.info['type'] == "3D":
                FullTrue3Dview = v
    if option == 7:
        import qbaseeditor
        from qbaseeditor import currentview
    for v in editor.layout.views:
        if v.info["viewname"] == "skinview":
            pass
        if (option == 6 and v.info["viewname"] == "editors3Dview") or (option == 6 and v.info["viewname"] == "3Dwindow"):
            pass
        if option == 7 and v.info["viewname"] != currentview.info["viewname"]:
            pass
        else:
            if option == 1:
                v.invalidate(1)
            if option <= 7:
                mdleditor.setsingleframefillcolor(editor, v)
            if option <= 7:
                v.repaint()
            if option <= 7:
                plugins.mdlgridscale.gridfinishdrawing(editor, v)
                plugins.mdlaxisicons.newfinishdrawing(editor, v)
            if option <= 7 or option == 5:
                if v.info["viewname"] == "editors3Dview" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles1"] == "1":
                    v.handles = []
                elif v.info["viewname"] == "XY" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles2"] == "1":
                    v.handles = []
                elif v.info["viewname"] == "YZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles3"] == "1":
                    v.handles = []
                elif v.info["viewname"] == "XZ" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles4"] == "1":
                    v.handles = []
                elif v.info["viewname"] == "3Dwindow" and quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_nohandles5"] == "1":
                    v.handles = []
                else:
                    v.handles = newhandles
                    if True3Dview is not None and v.info["viewname"] != "editors3Dview" and v.info["viewname"] != "3Dwindow":
                        handle = qhandles.EyePosition(v, True3Dview)
                        handle.hint = "camera for the Editor 3D view"
                        v.handles.append(handle)
                        handle = mdlhandles.MdlEyeDirection(v, True3Dview)
                        handle.hint = "Editor 3D view camera direction"
                        v.handles.append(handle)
                    if FullTrue3Dview is not None and v.info["viewname"] != "editors3Dview" and v.info["viewname"] != "3Dwindow":
                        handle = qhandles.EyePosition(v, FullTrue3Dview)
                        handle.hint = "camera for the floating 3D view"
                        v.handles.append(handle)
                        handle = mdlhandles.MdlEyeDirection(v, FullTrue3Dview)
                        handle.hint = "floating 3D view camera direction"
                        v.handles.append(handle)
                if editor.ModelFaceSelList != []:
                    mdlhandles.ModelFaceHandle(qhandles.GenericHandle).draw(editor, v, editor.EditorObjectList)
                if v.handles is None:
                    v.handles = []
                if v.handles == []:
                    pass
                else:
                    cv = v.canvas()
                    for h in v.handles:
                       h.draw(v, cv, h)
                if quarkx.setupsubset(SS_MODEL, "Options")["MAIV"] == "1":
                    mdleditor.modelaxis(v)



def ReverseFaces(editor):
    "Reverses or mirrors the selected faces, in the ModelFaceSelList, vertexes"
    "making turning the face in the opposite direction."
    comp = editor.Root.currentcomponent
    if (len(editor.ModelFaceSelList) < 1) or (comp is None):
        quarkx.msgbox("No selection has been made\n\nYou must first select some faces of a\nmodel component to flip their direction.", MT_ERROR, MB_OK)
        return
    sellist = editor.layout.explorer.sellist
    if len(sellist) == 0:
        quarkx.msgbox("Improper Action - no frame selection.\n\nYou must first select a frame and some faces\nof a model component to flip their direction.", MT_ERROR, MB_OK)
        return
    for item in range(len(sellist)):
        if sellist[item].type == ":mf":
            break
        if item == len(sellist)-1:
            quarkx.msgbox("Improper Action - no frame selection.\n\nYou must first select a frame and some faces\nof a model component to flip their direction.", MT_ERROR, MB_OK)
            return

    new_comp = comp.copy()
    new_tris = comp.triangles
    for tri in editor.ModelFaceSelList:
        vtxs = comp.triangles[tri]
        if vtxs[1][0] > vtxs[2][0]:
            new_tris[tri] = (vtxs[1],vtxs[0],vtxs[2])
        else:
            new_tris[tri] = (vtxs[2],vtxs[1],vtxs[0])
    new_comp.triangles = new_tris
    new_comp.currentskin = editor.Root.currentcomponent.currentskin
    compframes = new_comp.findallsubitems("", ':mf')   # get all frames
    curframe = comp.currentframe
    new_comp.currentframe = compframes[curframe.index]
    undo = quarkx.action()
    undo.exchange(comp, new_comp)
    editor.Root.currentcomponent = new_comp
    editor.ok(undo, "Reversed Faces")



def SubdivideFaces(editor, pieces=None):
    "Splits the selected faces, in the ModelFaceSelList, into the number of new triangles given as 'pieces'."
    comp = editor.Root.currentcomponent
    if (len(editor.ModelFaceSelList) < 1) or (comp is None):
        quarkx.msgbox("No selection has been made\n\nYou must first select a frame and some faces\nof a model component to subdivide those faces.", MT_ERROR, MB_OK)
        return
    sellist = editor.layout.explorer.sellist
    if len(sellist) == 0:
        quarkx.msgbox("Improper Action - no frame selection.\n\nYou must first select a frame and some faces\nof a model component to subdivide those faces.", MT_ERROR, MB_OK)
        return
    for item in range(len(sellist)):
        if sellist[item].type == ":mf":
            break
        if item == len(sellist)-1:
            quarkx.msgbox("Improper Action - no frame selection.\n\nYou must first select a frame and some faces\nof a model component to subdivide those faces.", MT_ERROR, MB_OK)
            return

    new_comp = comp.copy()
    new_tris = new_comp.triangles
    newtri_index = len(comp.triangles)-1
    newfaceselection = []
    new_compframes = new_comp.findallsubitems("", ':mf')   # get all frames
    currentvertices = len(new_compframes[0].vertices)-1
    curframe = comp.currentframe

    if pieces == 2:
        # This updates (adds) the new vertices to each frame.
        commonvtxs = []
        commonvtxnbr = []
        for tri in editor.ModelFaceSelList:
            for vtx in comp.triangles[tri]:
                if not (curframe.vertices[vtx[0]] in commonvtxs):
                    commonvtxs = commonvtxs + [curframe.vertices[vtx[0]]]
                    commonvtxnbr = commonvtxnbr + [vtx[0]]
        for tri in editor.ModelFaceSelList:
            trivtxs = comp.triangles[tri]
            # Line for vertex 0 and vertex 1 will be split because it is the longest side.
            if (abs(curframe.vertices[trivtxs[0][0]] - curframe.vertices[trivtxs[1][0]]) > abs(curframe.vertices[trivtxs[1][0]] - curframe.vertices[trivtxs[2][0]])) and (abs(curframe.vertices[trivtxs[0][0]] - curframe.vertices[trivtxs[1][0]]) > abs(curframe.vertices[trivtxs[2][0]] - curframe.vertices[trivtxs[0][0]])):
                sidecenter = (curframe.vertices[trivtxs[0][0]] + curframe.vertices[trivtxs[1][0]])/2
                for vtx in range(len(commonvtxs)):
                    if str(sidecenter) == str(commonvtxs[vtx]):
                        newvtx_index0 = commonvtxnbr[vtx]
                        newvtx0u = (trivtxs[0][1] + trivtxs[1][1])/2
                        newvtx0v = (trivtxs[0][2] + trivtxs[1][2])/2
                        new_tris[tri] = ((newvtx_index0,newvtx0u,newvtx0v), trivtxs[2], trivtxs[0])
                        new_tris = new_tris + [((newvtx_index0,newvtx0u,newvtx0v), trivtxs[1], trivtxs[2])]
                        newtri_index = newtri_index + 1
                        newfaceselection = newfaceselection + [newtri_index]
                        break
                    if vtx == len(commonvtxs)-1:
                        currentvertices = currentvertices + 1
                        newvtx_index0 = currentvertices
                        newvtx0u = (trivtxs[0][1] + trivtxs[1][1])/2
                        newvtx0v = (trivtxs[0][2] + trivtxs[1][2])/2
                        new_tris[tri] = ((newvtx_index0,newvtx0u,newvtx0v), trivtxs[2], trivtxs[0])
                        new_tris = new_tris + [((newvtx_index0,newvtx0u,newvtx0v), trivtxs[1], trivtxs[2])]
                        newtri_index = newtri_index + 1
                        newfaceselection = newfaceselection + [newtri_index]
                        commonvtxs = commonvtxs + [sidecenter]
                        commonvtxnbr = commonvtxnbr + [newvtx_index0]
                        for frame in new_compframes:
                            old_vtxs = frame.vertices
                            sidecenter = (frame.vertices[trivtxs[0][0]] + frame.vertices[trivtxs[1][0]])/2
                            old_vtxs = old_vtxs + [sidecenter]
                            frame.vertices = old_vtxs
                            frame.compparent = new_comp
            # Line for vertex 1 and vertex 2 will be split because it is the longest side.
            elif (abs(curframe.vertices[trivtxs[1][0]] - curframe.vertices[trivtxs[2][0]]) > abs(curframe.vertices[trivtxs[0][0]] - curframe.vertices[trivtxs[1][0]])) and (abs(curframe.vertices[trivtxs[1][0]] - curframe.vertices[trivtxs[2][0]]) > abs(curframe.vertices[trivtxs[2][0]] - curframe.vertices[trivtxs[0][0]])):
                sidecenter = (curframe.vertices[trivtxs[1][0]] + curframe.vertices[trivtxs[2][0]])/2
                for vtx in range(len(commonvtxs)):
                    if str(sidecenter) == str(commonvtxs[vtx]):
                        newvtx_index0 = commonvtxnbr[vtx]
                        newvtx0u = (trivtxs[1][1] + trivtxs[2][1])/2
                        newvtx0v = (trivtxs[1][2] + trivtxs[2][2])/2
                        new_tris[tri] = ((newvtx_index0,newvtx0u,newvtx0v), trivtxs[2], trivtxs[0])
                        new_tris = new_tris + [((newvtx_index0,newvtx0u,newvtx0v), trivtxs[0], trivtxs[1])]
                        newtri_index = newtri_index + 1
                        newfaceselection = newfaceselection + [newtri_index]
                        break
                    if vtx == len(commonvtxs)-1:
                        currentvertices = currentvertices + 1
                        newvtx_index0 = currentvertices
                        newvtx0u = (trivtxs[1][1] + trivtxs[2][1])/2
                        newvtx0v = (trivtxs[1][2] + trivtxs[2][2])/2
                        new_tris[tri] = ((newvtx_index0,newvtx0u,newvtx0v), trivtxs[2], trivtxs[0])
                        new_tris = new_tris + [((newvtx_index0,newvtx0u,newvtx0v), trivtxs[0], trivtxs[1])]
                        newtri_index = newtri_index + 1
                        newfaceselection = newfaceselection + [newtri_index]
                        commonvtxs = commonvtxs + [sidecenter]
                        commonvtxnbr = commonvtxnbr + [newvtx_index0]
                        for frame in new_compframes:
                            old_vtxs = frame.vertices
                            sidecenter = (frame.vertices[trivtxs[1][0]] + frame.vertices[trivtxs[2][0]])/2
                            old_vtxs = old_vtxs + [sidecenter]
                            frame.vertices = old_vtxs
                            frame.compparent = new_comp
            # Line for vertex 2 and vertex 0 will be split because it is the longest side.
            else:
                sidecenter = (curframe.vertices[trivtxs[2][0]] + curframe.vertices[trivtxs[0][0]])/2
                for vtx in range(len(commonvtxs)):
                    if str(sidecenter) == str(commonvtxs[vtx]):
                        newvtx_index0 = commonvtxnbr[vtx]
                        newvtx0u = (trivtxs[2][1] + trivtxs[0][1])/2
                        newvtx0v = (trivtxs[2][2] + trivtxs[0][2])/2
                        new_tris[tri] = ((newvtx_index0,newvtx0u,newvtx0v), trivtxs[0], trivtxs[1])
                        new_tris = new_tris + [((newvtx_index0,newvtx0u,newvtx0v), trivtxs[1], trivtxs[2])]
                        newtri_index = newtri_index + 1
                        newfaceselection = newfaceselection + [newtri_index]
                        break
                    if vtx == len(commonvtxs)-1:
                        currentvertices = currentvertices + 1
                        newvtx_index0 = currentvertices
                        newvtx0u = (trivtxs[2][1] + trivtxs[0][1])/2
                        newvtx0v = (trivtxs[2][2] + trivtxs[0][2])/2
                        new_tris[tri] = ((newvtx_index0,newvtx0u,newvtx0v), trivtxs[0], trivtxs[1])
                        new_tris = new_tris + [((newvtx_index0,newvtx0u,newvtx0v), trivtxs[1], trivtxs[2])]
                        newtri_index = newtri_index + 1
                        newfaceselection = newfaceselection + [newtri_index]
                        commonvtxs = commonvtxs + [sidecenter]
                        commonvtxnbr = commonvtxnbr + [newvtx_index0]
                        for frame in new_compframes:
                            old_vtxs = frame.vertices
                            sidecenter = (frame.vertices[trivtxs[2][0]] + frame.vertices[trivtxs[0][0]])/2
                            old_vtxs = old_vtxs + [sidecenter]
                            frame.vertices = old_vtxs
                            frame.compparent = new_comp

        # This updates (adds) the new triangles to the component.
        new_comp.triangles = new_tris
        new_comp.currentskin = editor.Root.currentcomponent.currentskin
        new_comp.currentframe = new_compframes[curframe.index]
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        make_tristodraw_dict(editor, new_comp)
        editor.Root.currentcomponent = new_comp
        editor.ok(undo, "face Subdivision 2")
        editor.ModelFaceSelList = editor.ModelFaceSelList + newfaceselection
        newfaceselection = []
        import mdlhandles
        from mdlhandles import SkinView1
        if SkinView1 is not None:
            q = editor.layout.skinform.linkedobjects[0]
            q["triangles"] = str(len(editor.Root.currentcomponent.triangles))
            editor.layout.skinform.setdata(q, editor.layout.skinform.form)
            SkinView1.invalidate()

    elif pieces == 3:
        # This updates (adds) the new vertices to each frame.
        for tri_index in editor.ModelFaceSelList:
            currentvertices = currentvertices + 1
            for frame in new_compframes:
                old_vtxs = frame.vertices
                faceCenter = (old_vtxs[new_tris[tri_index][0][0]] + old_vtxs[new_tris[tri_index][1][0]] + old_vtxs[new_tris[tri_index][2][0]]) / 3
                frame.vertices = old_vtxs + [faceCenter]
                frame.compparent = new_comp
            faceCenterU = int((new_tris[tri_index][0][1] + new_tris[tri_index][1][1] + new_tris[tri_index][2][1]) / 3)
            faceCenterV = int((new_tris[tri_index][0][2] + new_tris[tri_index][1][2] + new_tris[tri_index][2][2]) / 3)
            newtri1 = ((currentvertices, faceCenterU, faceCenterV), (new_tris[tri_index][1][0], new_tris[tri_index][1][1], new_tris[tri_index][1][2]), (new_tris[tri_index][2][0], new_tris[tri_index][2][1], new_tris[tri_index][2][2]))
            newtri2 = ((currentvertices, faceCenterU, faceCenterV), (new_tris[tri_index][2][0], new_tris[tri_index][2][1], new_tris[tri_index][2][2]), (new_tris[tri_index][0][0], new_tris[tri_index][0][1], new_tris[tri_index][0][2]))
            new_tris[tri_index] = ((currentvertices, faceCenterU, faceCenterV), (new_tris[tri_index][0][0], new_tris[tri_index][0][1], new_tris[tri_index][0][2]), (new_tris[tri_index][1][0], new_tris[tri_index][1][1], new_tris[tri_index][1][2]))
            new_tris = new_tris + [newtri1] + [newtri2]
            newfaceselection = newfaceselection + [newtri_index+1] + [newtri_index+2]
            newtri_index = newtri_index+2

        # This updates (adds) the new triangles to the component.
        new_comp.triangles = new_tris
        new_comp.currentskin = editor.Root.currentcomponent.currentskin
        new_comp.currentframe = new_compframes[curframe.index]
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        make_tristodraw_dict(editor, new_comp)
        editor.Root.currentcomponent = new_comp
        editor.ok(undo, "face Subdivision 3")
        editor.ModelFaceSelList = editor.ModelFaceSelList + newfaceselection
        newfaceselection = []
        import mdlhandles
        from mdlhandles import SkinView1
        if SkinView1 is not None:
            q = editor.layout.skinform.linkedobjects[0]
            q["triangles"] = str(len(editor.Root.currentcomponent.triangles))
            editor.layout.skinform.setdata(q, editor.layout.skinform.form)
            SkinView1.invalidate()

    elif pieces == 4:
        # This updates (adds) the new vertices to each frame.
        commonvtxs = []
        commonvtxnbr = []
        for tri in editor.ModelFaceSelList:
            for vtx in comp.triangles[tri]:
                if not (curframe.vertices[vtx[0]] in commonvtxs):
                    commonvtxs = commonvtxs + [curframe.vertices[vtx[0]]]
                    commonvtxnbr = commonvtxnbr + [vtx[0]]
        for tri in editor.ModelFaceSelList:
            newsidecenter = []
            trivtxs = comp.triangles[tri]
            side01center = (curframe.vertices[trivtxs[0][0]] + curframe.vertices[trivtxs[1][0]])/2
            newvtx3u = (trivtxs[0][1] + trivtxs[1][1])/2
            newvtx3v = (trivtxs[0][2] + trivtxs[1][2])/2
            for vtx in range(len(commonvtxs)):
                if str(side01center) == str(commonvtxs[vtx]):
                    newvtx_index3 = commonvtxnbr[vtx]
                    break
                if vtx == len(commonvtxs)-1:
                    currentvertices = currentvertices + 1
                    newvtx_index3 = currentvertices
                    commonvtxs = commonvtxs + [side01center]
                    commonvtxnbr = commonvtxnbr + [newvtx_index3]
                    newsidecenter = newsidecenter + [0]
            newvtx3 = (newvtx_index3,newvtx3u,newvtx3v)
            side12center = (curframe.vertices[trivtxs[1][0]] + curframe.vertices[trivtxs[2][0]])/2
            newvtx4u = (trivtxs[1][1] + trivtxs[2][1])/2
            newvtx4v = (trivtxs[1][2] + trivtxs[2][2])/2
            for vtx in range(len(commonvtxs)):
                if str(side12center) == str(commonvtxs[vtx]):
                    newvtx_index4 = commonvtxnbr[vtx]
                    break
                if vtx == len(commonvtxs)-1:
                    currentvertices = currentvertices + 1
                    newvtx_index4 = currentvertices
                    commonvtxs = commonvtxs + [side12center]
                    commonvtxnbr = commonvtxnbr + [newvtx_index4]
                    newsidecenter = newsidecenter + [1]
            newvtx4 = (newvtx_index4,newvtx4u,newvtx4v)
            side20center = (curframe.vertices[trivtxs[2][0]] + curframe.vertices[trivtxs[0][0]])/2
            newvtx5u = (trivtxs[2][1] + trivtxs[0][1])/2
            newvtx5v = (trivtxs[2][2] + trivtxs[0][2])/2
            for vtx in range(len(commonvtxs)):
                if str(side20center) == str(commonvtxs[vtx]):
                    newvtx_index5 = commonvtxnbr[vtx]
                    break
                if vtx == len(commonvtxs)-1:
                    currentvertices = currentvertices + 1
                    newvtx_index5 = currentvertices
                    commonvtxs = commonvtxs + [side20center]
                    commonvtxnbr = commonvtxnbr + [newvtx_index5]
                    newsidecenter = newsidecenter + [2]
            newvtx5 = (newvtx_index5,newvtx5u,newvtx5v)

            new_tris[tri] = (newvtx5, trivtxs[0], newvtx3)
            new_tri1 = (newvtx4, newvtx3, trivtxs[1])
            new_tri2 = (newvtx5, newvtx3, newvtx4)
            new_tri3 = (newvtx5, newvtx4, trivtxs[2])
            new_tris = new_tris + [new_tri1] + [new_tri2] + [new_tri3]
            newfaceselection = newfaceselection + [newtri_index+1] + [newtri_index+2] + [newtri_index+3]
            newtri_index = newtri_index+3

            for frame in new_compframes:
                old_vtxs = frame.vertices
                if 0 in newsidecenter:
                    side01center = (frame.vertices[trivtxs[0][0]] + frame.vertices[trivtxs[1][0]])/2
                    old_vtxs = old_vtxs + [side01center]
                if 1 in newsidecenter:
                    side12center = (frame.vertices[trivtxs[1][0]] + frame.vertices[trivtxs[2][0]])/2
                    old_vtxs = old_vtxs + [side12center]
                if 2 in newsidecenter:
                    side20center = (frame.vertices[trivtxs[2][0]] + frame.vertices[trivtxs[0][0]])/2
                    old_vtxs = old_vtxs + [side20center]
                frame.vertices = old_vtxs
                frame.compparent = new_comp

        # This updates (adds) the new triangles to the component.
        new_comp.triangles = new_tris
        new_comp.currentskin = editor.Root.currentcomponent.currentskin
        new_comp.currentframe = new_compframes[curframe.index]
        undo = quarkx.action()
        undo.exchange(comp, new_comp)
        make_tristodraw_dict(editor, new_comp)
        editor.Root.currentcomponent = new_comp
        editor.ok(undo, "face Subdivision 4")
        editor.ModelFaceSelList = editor.ModelFaceSelList + newfaceselection
        newfaceselection = []
        import mdlhandles
        from mdlhandles import SkinView1
        if SkinView1 is not None:
            q = editor.layout.skinform.linkedobjects[0]
            q["triangles"] = str(len(editor.Root.currentcomponent.triangles))
            editor.layout.skinform.setdata(q, editor.layout.skinform.form)
            SkinView1.invalidate()



# ----------- REVISION HISTORY ------------
#
#
#$Log: mdlutils.py,v $
#Revision 1.173  2013/02/13 03:28:42  cdunde
#Code cleanup.
#
#Revision 1.172  2013/02/11 21:05:44  cdunde
#To remove 1 unit hard coded offset causing misplacement of dragged faces.
#
#Revision 1.171  2012/10/09 05:27:44  cdunde
#To stop console error.
#
#Revision 1.170  2012/07/15 20:40:47  cdunde
#Fixed KeyFrame rotation function for models with bones.
#
#Revision 1.169  2012/03/25 01:07:49  cdunde
#To fix error in KeyframeLinearInterpolation function for models that do not have any bones.
#
#Revision 1.168  2011/12/28 07:28:51  cdunde
#Setting up system for bone.dictspec['type'] to store what kind of IMPORTER or
#default QuArK new bones ('type' = qrk) a bone is.
#Each importer sets its own 'type' as it creates its bones and these do not change.
#The type is used by EXPORTERS as an indicator as to how they need to be processed
#for EXPORTING them to another model format.
#
#Trying to keep this system simple and centralized, a universal function can be
#setup and called from the quarkpy/mdlutils.py file by any exporter as needed,
#passing two arguments, the exporters name and the bone type, as it loops through them.
#The code that exporter needs to convert that bone type for proper exporting
#would be identified, by the two arguments, used and return the needed values.
#
#The quarkpy/mdlutils.py universal function could then be updated
#as new importers and exporters are created with their own conversion code.
#Then all other exporters, new or existing, would call that function when
#a SINGLE bone was NOT one of its own ['type'].
#
#This keeps all that code centralized in ONE PLACE.
#
#Revision 1.167  2011/11/14 07:26:38  cdunde
#Correction to last changes,
#some imported models have bones without any vertices assigned to them
#so we can not remove them to clean up the boneslist or exporting breaks.
#
#Revision 1.166  2011/11/13 03:15:09  cdunde
#To allow the changing of bonecontrol indexes.
#
#Revision 1.165  2011/11/12 06:01:12  cdunde
#Changed needed functions to affect bonelist.
#
#Revision 1.164  2011/09/25 05:15:09  cdunde
#To fix occasional error message.
#
#Revision 1.163  2011/05/28 00:11:27  cdunde
#Fixes to avoid error from bboxes of multiple models in the editor at the same time.
#
#Revision 1.162  2011/05/26 22:57:48  cdunde
#Removed OLD bones system Keyframe rotation function not used anymore.
#
#Revision 1.161  2011/05/26 09:32:19  cdunde
#Setup component bbox vertex assignment support.
#
#Revision 1.160  2011/05/25 20:55:03  cdunde
#Revamped Bounding Box system for more flexibility with model formats that do not have bones, only single or multi components.
#
#Revision 1.159  2011/05/22 22:39:31  cdunde
#Change to allow new QuArK bones assigned vertexes to use Keyframe function.
#
#Revision 1.158  2011/05/22 09:13:15  cdunde
#Added bone and bounding boxes support to Keyframe Linear Interpolation function.
#
#Revision 1.157  2011/02/21 20:18:29  cdunde
#Removed redundant code and used new frame index dectspec to speed things up and Depreciation Alert fixed.
#Also fixed errors and skins not showing when making new components from others.
#
#Revision 1.156  2011/02/11 19:46:25  cdunde
#Fixed broken mesh vertex merging function.
#
#Revision 1.155  2010/12/28 20:14:36  cdunde
#Fix for occasional currentframe error.
#
#Revision 1.154  2010/12/19 17:24:54  cdunde
#Changes so a bone can have multiple bounding boxes assigned to it.
#
#Revision 1.153  2010/12/07 21:04:49  cdunde
#Removed code that we decided not to use.
#
#Revision 1.152  2010/12/07 11:17:14  cdunde
#More updates for Model Editor bounding box system.
#
#Revision 1.151  2010/12/06 05:43:06  cdunde
#Updates for Model Editor bounding box system.
#
#Revision 1.150  2010/10/20 20:17:54  cdunde
#Added bounding boxes (hit boxes) and bone controls support used by Half-Life, maybe others.
#
#Revision 1.149  2010/10/20 06:40:36  cdunde
#Fixed the loss of selections and expanded items in the Model Editor from UNDO and REDO actions.
#
#Revision 1.148  2010/10/10 03:24:59  cdunde
#Added support for player models attachment tags.
#To make baseframe name uniform with other files.
#
#Revision 1.147  2010/09/16 06:33:33  cdunde
#Model editor, Major change of Skin-view Linear Handle selection and dragging system, massively improving drawing time.
#
#Revision 1.146  2010/09/03 07:19:11  cdunde
#Speedup code changes for the function MakeEditorVertexPolyObject.
#
#Revision 1.145  2010/06/06 23:27:20  cdunde
#Fix for ModelComponentList weightvtxlist not always being updated properly.
#
#Revision 1.144  2010/05/29 04:34:45  cdunde
#Update for Model Editor camera EYE handles for editor and floating 3D view.
#
#Revision 1.143  2010/05/15 07:43:26  cdunde
#Fix for another possible error causer...how many of these do we have?!
#
#Revision 1.142  2010/05/14 06:12:32  cdunde
#Needed fix, in case user deletes Misc group or components with tags, to avoid errors.
#
#Revision 1.141  2010/05/14 00:26:45  cdunde
#Need fix, in case user deletes Skeleton group, to avoid errors and update ModelComponentList.
#
#Revision 1.140  2010/05/12 08:07:13  cdunde
#Added Eye camera handle when in True 3D mode for easier navigation.
#
#Revision 1.139  2010/05/05 15:46:39  cdunde
#To stop jerky movement in Model Editor when scrolling, panning.
#
#Revision 1.138  2010/05/05 04:08:47  cdunde
#Function correction.
#
#Revision 1.137  2010/05/04 05:30:52  cdunde
#Added new function to rescale Skin-view handles to current skin texture size.
#
#Revision 1.136  2010/05/01 07:16:40  cdunde
#Update by DanielPharos to allow removal of weight_index storage in the ModelComponentList related files.
#
#Revision 1.135  2010/05/01 04:49:04  cdunde
#Weights dialog fix by DanielPharos and reset of range from .01 to 1.0.
#
#Revision 1.134  2010/05/01 04:25:37  cdunde
#Updated files to help increase editor speed by including necessary ModelComponentList items
#and removing redundant checks and calls to the list.
#
#Revision 1.133  2010/04/23 10:03:29  cdunde
#Commented function description clarification.
#
#Revision 1.132  2010/04/08 04:50:57  cdunde
#Needed fixes for some broken bone specifics items.
#
#Revision 1.131  2010/04/03 19:56:06  cdunde
#Minor updates.
#
#Revision 1.130  2010/03/20 08:16:59  cdunde
#Needed updates to reactivate bone settings properly.
#
#Revision 1.129  2010/03/20 05:22:20  cdunde
#To allow offsetting of bone handles for imported models.
#
#Revision 1.128  2010/03/19 23:53:57  cdunde
#Update for correct bone positioning when read in from a model file.
#
#Revision 1.126  2010/03/09 19:59:19  cdunde
#Attribute correction.
#
#Revision 1.125  2009/11/16 05:35:49  cdunde
#Comment clarification update.
#
#Revision 1.124  2009/11/09 02:17:31  cdunde
#Fixes for individual bone selection and handle color change.
#
#Revision 1.123  2009/10/29 19:56:33  danielpharos
#Fixed bad error-message text.
#
#Revision 1.122  2009/10/21 06:28:26  cdunde
#Update to keyframes functions for handling tags.
#
#Revision 1.121  2009/10/20 07:03:20  cdunde
#Added keyframe fill-in frames creation support for single and multiple component selections.
#
#Revision 1.120  2009/10/16 21:01:18  cdunde
#Menu update.
#
#Revision 1.119  2009/10/14 00:20:47  cdunde
#Various fixes for CFG Animation and interpolation.
#
#Revision 1.118  2009/10/13 22:02:36  danielpharos
#Removed some redundant code.
#
#Revision 1.117  2009/10/10 04:11:08  cdunde
#Another method of interpolation by DanielPharos. Not being called at this time.
#
#Revision 1.116  2009/10/03 06:16:07  cdunde
#Added support for animation interpolation in the Model Editor.
#(computation of added movement to emulate game action)
#
#Revision 1.115  2009/09/30 19:37:26  cdunde
#Threw out tags dialog, setup tag dragging, commands, and fixed saving of face selection.
#
#Revision 1.114  2009/08/24 23:39:20  cdunde
#Added support for multiple bone sets for imported models and their animations.
#
#Revision 1.113  2009/08/18 23:21:36  cdunde
#To increase Rebuild_Bone function processing speed.
#
#Revision 1.112  2009/08/15 09:37:14  cdunde
#To fix improper bone position on specifics page for different frame selection.
#
#Revision 1.111  2009/07/27 05:57:15  cdunde
#To fix incorrect function description comment.
#
#Revision 1.110  2009/07/14 00:27:33  cdunde
#Completely revamped Model Editor vertex Linear draglines system,
#increasing its reaction and drawing time to twenty times faster.
#
#Revision 1.109  2009/07/04 03:02:40  cdunde
#Fix to stop multiple Skeleton folders from being created when multiple components are deleted.
#
#Revision 1.108  2009/06/09 05:51:48  cdunde
#Updated to better display the Model Editor's Skeleton group and
#individual bones and their sub-bones when they are hidden.
#
#Revision 1.107  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.106  2009/05/01 06:06:15  cdunde
#Moved bones undo function to mdlutils.py for generic use elsewhere.
#
#Revision 1.105  2009/04/29 23:50:03  cdunde
#Added auto saving and updating features for weights dialog data.
#
#Revision 1.104  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.103  2009/03/26 22:32:30  danielpharos
#Fixed the treeview color boxes for components not showing up the first time.
#
#Revision 1.102  2009/02/17 04:57:00  cdunde
#To fix another error situation cause.
#
#Revision 1.101  2009/01/30 20:38:46  cdunde
#Added option for creation of all bone handle draglines when importing.
#
#Revision 1.100  2009/01/30 08:32:58  cdunde
#To put limits on tristodraw function call due to massive slowdown with large models.
#
#Revision 1.99  2009/01/29 02:13:51  cdunde
#To reverse frame indexing and fix it a better way by DanielPharos.
#
#Revision 1.98  2009/01/27 20:56:24  cdunde
#Update for frame indexing.
#Added new bone function 'Attach End to Start'.
#Code reorganization for consistency of items being created.
#
#Revision 1.97  2009/01/27 05:03:00  cdunde
#Full support for .md5mesh bone importing with weight assignment and other improvements.
#
#Revision 1.96  2009/01/09 08:33:26  cdunde
#New function added "allowbones", checks for at least one component to allowing bones.
#New function added "clearbones", remakes "Skeleton" folder with NO bones to clear them.
#
#Revision 1.95  2008/12/22 05:06:00  cdunde
#Added new function to attach bones end handles.
#Corrected the way the Make_BoneVtxList function works to process each bone's handle by its stored component name.
#
#Revision 1.94  2008/12/19 07:14:10  cdunde
#Added new function to add newly imported bones to the editor.ModelComponentList sections properly
#and made a change for the Skin-view updating that stops improper skin selection after a drag.
#
#Revision 1.93  2008/12/10 20:20:58  cdunde
#Setup a utility to deal with the updating of the Skin-view easer.
#
#Revision 1.92  2008/11/24 22:51:10  cdunde
#To update bone and editor.ModelComponentList after new component is created. Additional fix.
#
#Revision 1.91  2008/11/22 05:08:55  cdunde
#To update bone and editor.ModelComponentList after new component is created.
#
#Revision 1.90  2008/11/19 06:16:22  cdunde
#Bones system moved to outside of components for Model Editor completed.
#
#Revision 1.89  2008/11/01 07:53:02  cdunde
#To stop any bones being copied to new components.
#
#Revision 1.88  2008/10/21 04:35:33  cdunde
#Bone corner handle rotation fixed correctly by DanielPharos
#and stop all drawing during Keyframe Rotation function.
#
#Revision 1.87  2008/10/15 00:01:30  cdunde
#Setup of bones individual handle scaling and Keyframe matrix rotation.
#Also removed unneeded code.
#
#Revision 1.86  2008/10/08 20:00:45  cdunde
#Updates for Model Editor Bones system.
#
#Revision 1.85  2008/10/04 05:48:06  cdunde
#Updates for Model Editor Bones system.
#
#Revision 1.84  2008/09/15 04:47:46  cdunde
#Model Editor bones code update.
#
#Revision 1.83  2008/08/08 05:02:11  cdunde
#Rearranged all functions into groups to organize and make locating easer.
#
#Revision 1.82  2008/08/08 04:55:06  cdunde
#To add new functions by DanielPharos and cdunde.
#
#Revision 1.81  2008/07/25 22:57:23  cdunde
#Updated component error checking and added frame matching and\or
#duplicating with independent names to avoid errors with other functions.
#
#Revision 1.80  2008/07/24 23:34:12  cdunde
#To fix non-ASCII character from causing python depreciation errors.
#
#Revision 1.79  2008/05/01 19:15:22  danielpharos
#Fix treeviewselchanged not updating.
#
#Revision 1.78  2008/05/01 13:52:31  danielpharos
#Removed a whole bunch of redundant imports and other small fixes.
#
#Revision 1.77  2008/02/23 04:41:11  cdunde
#Setup new Paint modes toolbar and complete painting functions to allow
#the painting of skin textures in any Model Editor textured and Skin-view.
#
#Revision 1.76  2008/02/13 08:55:24  cdunde
#To replace lost code of last change due to text editor.
#
#Revision 1.75  2008/02/13 08:49:29  cdunde
#Extended the TexturePixelLocation function for special Skin-view needs.
#
#Revision 1.74  2008/02/11 00:47:30  cdunde
#To fix text editor error.
#
#Revision 1.73  2008/02/11 00:39:51  cdunde
#Added new function to get the u, v texture position of any
#triangle where the cursor is pointing in any view.
#
#Revision 1.72  2008/02/07 13:19:48  danielpharos
#Fix findTriangle triggering on invalid triangles
#
#Revision 1.71  2007/12/08 07:40:01  cdunde
#Minor comment update.
#
#Revision 1.70  2007/12/08 07:20:56  cdunde
#To get the face extrusion functions to apply movement based on frame animation positions.
#
#Revision 1.69  2007/12/05 04:45:57  cdunde
#Added two new function methods to Subdivide selected faces into 3 and 4 new triangles each.
#
#Revision 1.68  2007/12/02 06:47:11  cdunde
#Setup linear center handle selected vertexes edge extrusion function.
#
#Revision 1.67  2007/11/24 01:46:01  cdunde
#To get all of the vertex and face Linear Handle movements
#to work properly for selected frames with animation differences.
#
#Revision 1.66  2007/11/22 07:31:04  cdunde
#Setup to allow merging of a base vertex and other multiple selected vertexes.
#
#Revision 1.65  2007/11/20 02:27:55  cdunde
#Added check to stop merging of two vertexes of the same triangle.
#
#Revision 1.64  2007/11/19 20:17:03  cdunde
#To try and stop vertex merging from crashing if last vertex is the base vertex.
#
#Revision 1.63  2007/11/19 07:45:55  cdunde
#Minor corrections for option number and activating menu item.
#
#Revision 1.62  2007/11/19 01:09:17  cdunde
#Added new function "Merge 2 Vertexes" to the "Vertex Commands" menu.
#
#Revision 1.61  2007/11/16 18:48:23  cdunde
#To update all needed files for fix by DanielPharos
#to allow frame relocation after editing.
#
#Revision 1.60  2007/11/15 22:08:24  danielpharos
#Fix the frame-won't-drag problem after a subdivide face action.
#
#Revision 1.59  2007/11/14 04:34:48  cdunde
#To stop duplicate handle redrawing after face subdivision.
#
#Revision 1.58  2007/11/14 00:11:13  cdunde
#Corrections for face subdivision to stop models from drawing broken apart,
#update Skin-view "triangles" amount displayed and proper full redraw
#of the Skin-view when a component is un-hidden.
#
#Revision 1.57  2007/11/13 19:36:09  cdunde
#To fix error if Skin-view has not been opened at least once and
#remove integer u,v conversion plus some file cleanup.
#
#Revision 1.56  2007/11/13 07:20:59  cdunde
#Update to the way Subdivision, face splitting, works to greatly increase speed.
#
#Revision 1.55  2007/11/12 00:53:23  cdunde
#To remove test print statements.
#
#Revision 1.54  2007/11/12 00:29:18  cdunde
#Fixed Linear Handle for selected faces and frames to draw
#face vertexes locations properly for animation movement.
#
#Revision 1.53  2007/11/11 11:41:50  cdunde
#Started a new toolbar for the Model Editor to support "Editing Tools".
#
#Revision 1.52  2007/11/04 00:33:33  cdunde
#To make all of the Linear Handle drag lines draw faster and some selection color changes.
#
#Revision 1.51  2007/10/25 17:25:47  cdunde
#To fix some small typo errors.
#
#Revision 1.50  2007/10/24 14:58:12  cdunde
#To activate all Movement toolbar button functions for the Model Editor.
#
#Revision 1.49  2007/10/22 02:22:08  cdunde
#To speed up conversion code.
#
#Revision 1.48  2007/10/21 04:52:27  cdunde
#Added a "Snap Shot" function and button to the Skin-view to allow the re-skinning
#of selected faces in the editor based on their position in the editor's 3D view.
#
#Revision 1.47  2007/10/08 16:19:42  cdunde
#Missed a change item.
#
#Revision 1.46  2007/10/06 20:14:31  cdunde
#Added function option to just update the editors 2D views.
#
#Revision 1.45  2007/09/15 19:19:15  cdunde
#To fix if sometimes the model component it lost.
#
#Revision 1.44  2007/09/13 01:04:59  cdunde
#Added a new function, to the Faces RMB menu, for a "Empty Component" to start fresh from.
#
#Revision 1.43  2007/09/12 05:25:51  cdunde
#To move Make New Component menu function from Commands menu to RMB Face Commands menu and
#setup new function to move selected faces from one component to another.
#
#Revision 1.42  2007/09/11 00:09:20  cdunde
#Small update.
#
#Revision 1.41  2007/09/10 01:33:19  cdunde
#To speed up "Make new component" function.
#
#Revision 1.40  2007/09/07 23:55:29  cdunde
#1) Created a new function on the Commands menu and RMB editor & tree-view menus to create a new
#     model component from selected Model Mesh faces and remove them from their current component.
#2) Fixed error of "Pass face selection to Skin-view" if a face selection is made in the editor
#     before the Skin-view is opened at least once in that session.
#3) Fixed redrawing of handles in areas that hints show once they are gone.
#
#Revision 1.39  2007/09/01 20:32:06  cdunde
#Setup Model Editor views vertex "Pick and Move" functions with two different movement methods.
#
#Revision 1.38  2007/09/01 19:36:40  cdunde
#Added editor views rectangle selection for model mesh faces when in that Linear handle mode.
#Changed selected face outline drawing method to greatly increase drawing speed.
#
#Revision 1.37  2007/08/24 00:33:08  cdunde
#Additional fixes for the editor vertex selections and the View Options settings.
#
#Revision 1.36  2007/08/20 19:58:23  cdunde
#Added Linear Handle to the Model Editor's Skin-view page
#and setup color selection and drag options for it and other fixes.
#
#Revision 1.35  2007/08/08 21:07:47  cdunde
#To setup red rectangle selection support in the Model Editor for the 3D views using MMB+RMB
#for vertex selection in those views.
#Also setup Linear Handle functions for multiple vertex selection movement using same.
#
#Revision 1.34  2007/08/02 08:33:44  cdunde
#To get the model axis to draw and other things to work corretly with Linear handle toolbar button.
#
#Revision 1.33  2007/08/01 07:36:35  cdunde
#Notation change only.
#
#Revision 1.32  2007/07/28 23:11:26  cdunde
#Needed to fix the MakeEditorFaceObject function to maintain the face vertexes in their proper order.
#Also expanded the function to create a list of QuArK Internal Objects (faces) directly from the
#ModelFaceSelList for use with the newly added ModelEditorLinHandlesManager class and its related classes
#to the mdlhandles.py file to use for editing movement of model faces, vertexes and bones (in the future).
#Also changed those Object face names to include their component name, tri_index and vertex_index(s) for
#extraction to convert the Object face back into usable vertexes and triangles in the models mesh using
#a new function added to this file called 'ConvertEditorFaceObject'.
#
#Revision 1.31  2007/07/16 12:20:24  cdunde
#Commented info update.
#
#Revision 1.30  2007/07/15 21:22:46  cdunde
#Added needed item updates when a new triangle is created.
#
#Revision 1.29  2007/07/15 01:20:49  cdunde
#To fix error for trying to pass selected vertex(es) that do not belong to a triangle
#(new ones or leftovers from any delete triangles) to the Skin-view.
#
#Revision 1.28  2007/07/14 22:42:43  cdunde
#Setup new options to synchronize the Model Editors view and Skin-view vertex selections.
#Can run either way with single pick selection or rectangle drag selection in all views.
#
#Revision 1.27  2007/07/11 20:48:23  cdunde
#Opps, forgot a couple of things with the last change.
#
#Revision 1.26  2007/07/11 20:00:55  cdunde
#Setup Red Rectangle Selector in the Model Editor Skin-view for multiple selections.
#
#Revision 1.25  2007/07/09 18:59:23  cdunde
#Setup RMB menu sub-menu "skin-view Options" and added its "Pass selection to Editor views"
#function. Also added Skin-view Options to editors main Options menu.
#
#Revision 1.24  2007/07/02 22:49:43  cdunde
#To change the old mdleditor "picked" list name to "ModelVertexSelList"
#and "skinviewpicked" to "SkinVertexSelList" to make them more specific.
#Also start of function to pass vertex selection from the Skin-view to the Editor.
#
#Revision 1.23  2007/06/11 19:52:31  cdunde
#To add message box for proper vertex order of selection to add a triangle to the models mesh.
#and changed code for deleting a triangle to stop access violation errors and 3D views graying out.
#
#Revision 1.22  2007/05/28 23:46:26  cdunde
#To remove unneeded view invalidations.
#
#Revision 1.21  2007/05/18 02:16:48  cdunde
#To remove duplicate definition of the qbaseeditor.py files def invalidateviews function called
#for in some functions and not others. Too confusing, unnecessary and causes missed functions.
#Also fixed error message when in the Skin-view after a new triangle is added.
#
#Revision 1.20  2007/04/27 17:27:42  cdunde
#To setup Skin-view RMB menu functions and possable future MdlQuickKeys.
#Added new functions for aligning, single and multi selections, Skin-view vertexes.
#To establish the Model Editors MdlQuickKeys for future use.
#
#Revision 1.19  2007/04/22 23:02:17  cdunde
#Fixed slight error in Duplicate current frame, was coping incorrect frame.
#
#Revision 1.18  2007/04/22 21:06:04  cdunde
#Model Editor, revamp of entire new vertex and triangle creation, picking and removal system
#as well as its code relocation to proper file and elimination of unnecessary code.
#
#Revision 1.17  2007/04/19 03:20:06  cdunde
#To move the selection retention code for the Skin-view vertex drags from the mldhandles.py file
#to the mdleditor.py file so it can be used for many other functions that cause the same problem.
#
#Revision 1.16  2007/04/17 16:01:25  cdunde
#To retain selection of original animation frame when duplicated.
#
#Revision 1.15  2007/04/17 12:55:34  cdunde
#Fixed Duplicate current frame function to stop Model Editor views from crashing
#and updated its popup help and Infobase link description data.
#
#Revision 1.14  2007/04/16 16:55:59  cdunde
#Added Vertex Commands to add, remove or pick a vertex to the open area RMB menu for creating triangles.
#Also added new function to clear the 'Pick List' of vertexes already selected and built in safety limit.
#Added Commands menu to the open area RMB menu for faster and easer selection.
#
#Revision 1.13  2007/04/10 06:00:36  cdunde
#Setup mesh movement using common drag handles
#in the Skin-view for skinning model textures.
#
#Revision 1.12  2007/03/29 15:25:34  danielpharos
#Cleaned up the tabs.
#
#Revision 1.11  2006/12/06 04:05:59  cdunde
#For explanation comment on how to use def findTriangles function.
#
#Revision 1.10  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.7  2001/03/15 21:07:49  aiv
#fixed bugs found by fpbrowser
#
#Revision 1.6  2001/02/01 22:03:15  aiv
#RemoveVertex Code now in Python
#
#Revision 1.5  2000/10/11 19:07:47  aiv
#Bones, and some kinda skin vertice viewer
#
#Revision 1.4  2000/08/21 21:33:04  aiv
#Misc. Changes / bugfixes
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#