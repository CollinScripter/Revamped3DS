######################################################
#
# Utilities for working with faces
#
#     tiglari@planetquake.com
#
######################################################

#$Header: /cvsroot/quark/runtime/plugins/faceutils.py,v 1.14 2005/11/06 23:42:39 cdunde Exp $

from quarkpy.qutils import *
import quarkpy.qhandles

# globals
set_error = None

def cyclenext(i, len):
  j = i+1
  if j == len:
    return 0
  else:
    return j

def cycleprev(i, len):
  j = i-1
  if j == 0:
    return len
  else:
    return j

def vtx_index(vtxes, pos):
  for i in range(len(vtxes)):
    if not(vtxes[i]-pos):
      return i

def abutting_vtx(l1, l2):
  "gets the two vtx shared between l1 & l2, which are"
  "supposed to be vertex-cyles of abutting faces"
  "returns list of (el,ind) tuples, where el is from l1,"
  "and ind is its index"
  intx = []
  pozzies = []
  i = -1
  for el1 in l1:
    i = i+1
    for el2 in l2 :
      if not (el1-el2):
        pozzies.append(i)
        intx.append((el1,i))
        break
  if len(intx) != 2:
    return []
  if pozzies[0]==0 and pozzies[1]>1:
    intx.reverse()
  return intx


def non_abutting_vtx(l1, l2):
  "gets the two vertexes shared between vertex list 1 (l1) & 2 (l2),"
  " which are supposed to be vertex-cyles of abutting faces."
  "This funciton returns two sets of lists."
  "The first list is of (el,ind) tuples, where el is from l1, and ind is its index."
  "The second list returns the index of the two vertex points that make up the shared edge."
  intx = []
  pozzies = []
  i = -1
  for el1 in l1:
    i = i+1
    for el2 in l2 :
      if not (el1-el2):
        pozzies.append(i)
        intx.append((el1,i))
        break
  if len(intx) != 2:
    return [],[]
  if pozzies[0]==0 and pozzies[1]>1:
    intx.reverse()
  return intx,pozzies



def intersection_vect(l1, l2):
  "for points/vectors only"
  "note that the points come out in the same order they have in l1"
  shared = []
  for el1 in l1:
    for el2 in l2 :
      if not (el1-el2):
        shared.append(el1)
        break
  return shared

def shares_edge(face, poly, vtx1, vtx2):
   vtxes = face.verticesof(poly)
   list = intersection_vect([vtx1, vtx2], vtxes)
   return len(list)==2


def coplanar(f1, f2, opp=1):
    "if opp==0, face normals must point in same direction"
    o1 = f1.dist*f1.normal
    o2 = f2.dist*f2.normal
    #debug('coplanar')
    if not f1.normal*(o2-o1):
        if not f1.normal-f2.normal:
            return 1
        if opp and not f1.normal+f2.normal:
            return 1
    return 0

def nearly_equals(value1, value2):
    """Return 1 if the two passed values are almost the same.  This works around
       rountind errors preventing vertex_in_vertices from working absolutely
       precisely."""
    if abs(value1 - value2) < 0.0001:
        return 1
    else:
        return 0

def vertex_in_vertices(v1, vertex_list):
    """Return 1 if the first vertex is in the list of vertices."""
    result = 0
    for vertex in vertex_list:
        if nearly_equals(v1.x, vertex.x) and \
           nearly_equals(v1.y, vertex.y) and \
           nearly_equals(v1.z, vertex.z):
            result = 1
    return result

def shared_vertices(selected_faces, all_faces):
    """searches thru the list of selected_faces and finds each vertex
       that is shared between a selected face and another face that is
       not selected, and returns a list of all faces thus detected"""

    result = []

    for selected_face in selected_faces:
        # TODO: iterate thru all objects that use this face instead of processing
        #       just the first one
        selected_polys = selected_face.faceof
        selected_poly = selected_polys[0]
        if selected_poly == selected_face:
            continue # this selected face is not used

        selected_vertices = selected_face.verticesof(selected_poly)

        if not(selected_face in result):
            result.append(selected_face)

            for a_face in all_faces:
                if (a_face in selected_faces) or (a_face in result):
                    continue

                # selected_face is a face that has already been selected
                # a_face is a face that has not been selected
                # if these two share at least one vertex, add the unselected
                #   face to the result list

                found = 0

                # a_face.faceof should return a list of objects that have a_face as one of
                # their faces.  This is usually just a single poly.  If nothing has a_face as
                # one of it's faces, then the list contains a_face itself
                # TODO: iterate thru all objects that use this face instead of processing
                #       just the first one
                a_polys = a_face.faceof
                a_poly = a_polys[0]
                if a_poly == a_face:
                    continue # this face is not used

                a_face_vertices = a_face.verticesof(a_poly)

                for selected_vertex in selected_vertices:
                    if vertex_in_vertices(selected_vertex, a_face_vertices):
                        found = 1
                if found:
                    result.append(a_face)

    return result


def perimeter_edges(editor):
    """Returns the original selected faces list as 2 new lists of faces,
       perimeter and non-perimeter faces,
       meaning that at least one edge (2 vertexs) is on the perimeter.
       Also, it returns 2 other list of all the vertex points that are
       on the perimeter only that make up the perimeter face edges
       and the non-perimeter points that are inside of that."""

    global set_error
    from plugins.mapterrainmodes import set_error_reset
    if set_error_reset is None:
        set_error = None

    selectedfacelist = editor.layout.explorer.sellist

    perimfaces = []
    non_perimfaces = []
    strperimedges = []
    for baseface in selectedfacelist:
        if baseface.type == ':p' and set_error is None:
            selectedfacelist = []
            quarkx.msgbox("You can not use this handle\nto drag these objects.\n\nIt is only a marker for items involved\nin the 'undo' level you just clicked.\n\nYou must reselect the items to move them.", MT_ERROR, MB_OK)
            set_error = 1
            break
        if set_error == 1:
            break

        baseedges = []
        baseedge0 = 0
        baseedge1 = 0
        baseedge2 = 0
        basepoly = baseface.parent
        if len(baseface.verticesof(basepoly)) != 3:
            editor.layout.explorer.sellist = [baseface]
            selectedfacelist = []
            quarkx.msgbox("You have made an\nimproper selection", MT_ERROR, MB_OK)
            break
        else:
            bfp0, bfp1, bfp2 = baseface.verticesof(basepoly)
        basevertices = baseface.verticesof(basepoly)
        for compface in selectedfacelist:
            comppoly = compface.parent
            if basepoly == comppoly:
                continue # we don't want to compair it to itself.
            else:
                compvertices = compface.verticesof(comppoly)
                intx,pozzie = non_abutting_vtx(basevertices, compvertices)

                if pozzie == [0, 1]:
                    baseedge0 = baseedge0 + 1
                if pozzie == [1, 2]:
                    baseedge1 = baseedge1 + 1
                if pozzie == [0, 2]:
                    baseedge2 = baseedge2 + 1

        if baseedge0 == 0:
            strperimedges.append(str(bfp0))
            strperimedges.append(str(bfp1))

        if baseedge1 == 0:
            strperimedges.append(str(bfp1))
            strperimedges.append(str(bfp2))

        if baseedge2 == 0:
            strperimedges.append(str(bfp0))
            strperimedges.append(str(bfp2))

        if baseedge0 and baseedge1 and baseedge2 != 0:
            non_perimfaces.append(baseface)
        else:
            perimfaces.append(baseface)

    if set_error == 1:
        selectedfacelist = []
        return None, None, None, None

    perimvertexs = []
    strperimvertexs = []
    movablevertexes = []
    strmovablevertexes = []

    for face in selectedfacelist:
        polyofface = face.parent
        for vertex in face.verticesof(polyofface):
            if not(str(vertex) in strperimedges):
                if not(str(vertex) in strmovablevertexes):
                    movablevertexes.append(vertex)
                    strmovablevertexes.append(str(vertex))
            else:
                if not(str(vertex) in strperimvertexs):
                    perimvertexs.append(vertex)
                    strperimvertexs.append(str(vertex))


    return perimfaces, non_perimfaces, perimvertexs, movablevertexes


def close_to(vector1, vector2):
    """Returns 1 if the two passed vectors are within 6 view pixels of each other.
       This avoids two locations from having to be absolutely the same to work."""

    if abs(vector1.tuple[0] - vector2.tuple[0]) < 6 and abs(vector1.tuple[1] - vector2.tuple[1]) < 6:
        return 1
    else:
        return 0


def cursor2vertex(view, face, poly, curpos):
    """Returns the vertex that the cursor is near
       for other processes like canvas painting of it."""

    vertices = face.verticesof(poly)
    for v in vertices:
        vpos = view.proj(v)
        if close_to(vpos, curpos) == 1:
            return vpos, v
    else:
        return None, None

def common_vertexes(fixedvtx, compface, comppoly, variance):
    """Returns compared vertex if two are within the given variance grid units of each other.
       This avoids two locations from having to be absolutely the same to work."""

    compvertices = compface.verticesof(comppoly)
    for compvtx in compvertices:
        if abs(fixedvtx.tuple[0] - compvtx.tuple[0]) < variance and abs(fixedvtx.tuple[1] - compvtx.tuple[1]) < variance and abs(fixedvtx.tuple[2] - compvtx.tuple[2]) < variance:
            return compvtx
    else:
        return None

#$Log: faceutils.py,v $
#Revision 1.14  2005/11/06 23:42:39  cdunde
#Added three new functions, close_to, cursor2vertex and common_vertexes.
#See them for description, last one allows a grid variance setting.
#
#Revision 1.13  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.10  2005/07/01 19:51:31  cdunde
#Added error message to avoid breaking
#
#Revision 1.9  2005/06/30 21:16:04  cdunde
#Minor update
#
#Revision 1.8  2005/06/17 05:48:40  cdunde
#To change the perimeter_edges function method to get clean lists returns without
#dupe vertexes and add an additional list of non-perimeter vertexes
#
#Revision 1.7  2005/06/02 00:42:29  cdunde
#Changes by Rowdy to help min. dup items in list
#
#Revision 1.6  2005/05/30 20:06:25  cdunde
#Added new functions to return 2 lists, perim and non-perim faces,
#and 1 list of the perimeter vertex only.
#
#Revision 1.5  2005/04/20 19:00:24  cdunde
#To fix typo error for continue
#
#Revision 1.4  2005/04/20 12:31:47  rowdy
#added a couple of functions nearly_equals, vertex_in_vertices and shared_vertices
#to check for vertices shared  by adjacent faces to help with the terrain plugin
#Revision 1.3  2001/08/11 04:14:51  tiglari
#remove debug
#
#Revision 1.2  2001/04/15 06:05:52  tiglari
#add coplanar function
#
#Revision 1.1  2001/04/01 04:43:48  tiglari
#initial commit
#
