"""   QuArK  -  Quake Army Knife

Various Map editor utilities.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/maputils.py,v 1.29 2011/03/13 00:41:47 cdunde Exp $


import quarkx
from qeditor import *
from qdictionnary import Strings



#
# Function below removed. Use "view.scale()" instead.
#

#def scaleofview(view):
#    "The scale of the given view, or 1.0 for 3D views."
#    if view.info["type"]!="3D":
#        try:
#            return view.info["scale"]
#        except KeyError:
#            pass
#    return 1.0



#
# Is a given object still in the tree view, or was it removed ?
#
def checktree(root, obj):
    while obj is not root:
        t = obj.parent
        if t is None or not (obj in t.subitems):
            return 0
        obj = t
    return 1     


#
# The UserDataPanel class, overridden to be map-specific.
#

def chooselocaltexture(item):
    editor = mapeditor()
    if editor is None: return
    import mapbtns
    mapbtns.applytexture(editor, item.text)

def loadlocaltextures(item):
    editor = mapeditor()
    if editor is None: return
    items = []
    for tex in quarkx.texturesof([editor.Root]):
        m = qmenu.item(tex, chooselocaltexture)
        m.menuicon = ico_objects[1][iiTexture]
        items.append(m)
    return items


class MapUserDataPanel(UserDataPanel):

    def btnclick(self, btn):
        #
        # Send the click message to the module mapbtns.
        #
        import mapbtns
        mapbtns.mapbuttonclick(btn)

    def buildbuttons(self, btnpanel):
        Btns = []
        ico_maped=ico_dict['ico_maped']
        for tb, icon in (("New map items...", 25), ("Texture Browser...", 26)):
            icons = (ico_maped[0][icon], ico_maped[1][icon])
            toolboxes = quarkx.findtoolboxes(tb)
            for toolbox, root, flag in toolboxes:
                new = quarkx.newobj(root.shortname + '.qtxfolder')
                new.appenditem(root.copy())
                btn = self.newbutton(new, btnpanel, icons)
                btn.toolbox = toolbox
                del btn.ondrop
                Btns.append(btn)
            Btns.append(qtoolbar.smallgap)
        new = quarkx.newobj(Strings[185]+".qtxfolder")
        new.appenditem(quarkx.newobj("local:"))
        btn = self.newbutton(new, btnpanel, icons)
        btn.toolbox = Strings[185]
        del btn.ondrop
        del btn.onclick
        btn.menu = loadlocaltextures
        Btns.append(btn)
        Btns.append(qtoolbar.newline)
        return Btns + UserDataPanel.buildbuttons(self, btnpanel)

    def deletebutton(self, btn):
        if hasattr(btn, "toolbox"):
            quarkx.msgbox(Strings[5670] % btn.toolbox, MT_ERROR, MB_OK)
        else:
            UserDataPanel.deletebutton(self, btn)

    def drop(self, btnpanel, list, i, source):
        if len(list)==1 and list[0].type == ':g':
            quarkx.clickform = btnpanel.owner
            editor = mapeditor()
            if editor is not None and source is editor.layout.explorer:
                choice = quarkx.msgbox("You are about to create a new button from this group. Do you want the button to display a menu with the items in this group ?\n\nYES: you can pick up individual items when you click on this button.\nNO: you can insert the whole group in your map by clicking on this button.",
                  MT_CONFIRMATION, MB_YES_NO_CANCEL)
                if choice == MR_CANCEL:
                    return
                if choice == MR_YES:
                    list = [group2folder(list[0])]

        if list[0].type=='.qtxfolder':
            for item in list[0].subitems:
                item["fixedscale"]="1"
        else:
            for item in list:
                item["fixedscale"]="1"

        UserDataPanel.drop(self, btnpanel, list, i, source)


def group2folder(group):
    new = quarkx.newobj(group.shortname + '.qtxfolder')
    for obj in group.subitems:
        if obj.type == ':g':
            obj = group2folder(obj)
        else:
            obj = obj.copy()
        new.appenditem(obj)
    return new

def degcycle(shear):
    if shear > 180:
      shear = shear-360
    if shear < -180:
      shear = shear+360
    return shear

def undo_exchange(editor, old, new, msg):
  undo = quarkx.action()
  undo.exchange(old, new)
  editor.ok(undo, msg)

def perptonormthru(source, dest, normthru):
  "the line from source to dest that is perpendicular to (normalized) normthru"
  diff = source-dest
  dot = diff*normthru
  return diff - dot*normthru
  
#
# Sets sign of vector so that its dot product is
#  positive w.r.t. the axis it's most closely
#  colinear with
#
def set_sign(vec):
  gap = ind = 0
  tuple = vec.tuple
  for i in range(3):
    if tuple[i]>gap:
      gap = tuple[i]
      ind = i
    if gap < 0:
      return -vec
    else:
      return vec

def ArbRotationMatrix(normal, angle):
     # qhandles.UserRotationMatrix with an angle added
     # normal: normal vector for the view plane
     # texpdest: new position of the reference vector texp4
     # texp4: reference vector (handle position minus rotation center)
     # g1: if True, snap angle to grid
    SNAP = 0.998
    cosangle = math.cos(angle)
    sinangle = math.sin(angle)
#    oldcos = cosangle
#    cosangle = cosangle*cosa-sinangle*sina
#    sinangle = sinangle*cosa+sina*oldcos
 
    m = quarkx.matrix((cosangle,  sinangle, 0),
                      (-sinangle, cosangle, 0),
                      (    0,        0,     1))
    v = orthogonalvect(normal, None)
    base = quarkx.matrix(v, v^normal, -normal)
    return base * m * (~base)

def squawk(text):
  if quarkx.setupsubset(SS_MAP, "Options")["Developer"]:
    quarkx.msgbox(text, MT_INFORMATION, MB_OK)

def findlabelled(list,label):
  for item in list:
    try:
      if item.label==label:
        return item
    except (AttributeError):
      pass

def cyclenext(i, len):
    return (i+1)%len
    
def cycleprev(i, len):
    return (i-1)%len

def projectpointtoplane(p,n1,o2,n2):
  "project point to plane at o2 with normal n2 along normal n1"
  v1 = o2-p
  v2 = v1*n2
  v3 = n1*n2
  v4 = v2/v3
  v5 = v4*n1
  return p + v5

def matrix_u_v(u,v):
    return quarkx.matrix((u.x, v.x, 0),
                         (u.y, v.y, 0),
                         (u.z, v.z, 1))
                         
def intersectionPoint2d(p0, d0, p1, d1):
    "intersection in 2D plane, point, direction"
    for v in p0, d0, p1, d1:
        if v.z != 0.0:
            return None
    det = d0.x*d1.y-d1.x*d0.y
    if det==0.0:
        return 0  # lines parallel
    s = (p0.y*d1.x - p1.y*d1.x - d1.y*p0.x +d1.y*p1.x)/det
    return p0+s*d0
        
#
# The two monstrosities below were derived from solving
#   systems of equations in Maple V.  The idea is to think
#   of the texture plane as being a plane in a 3d texture
#   space, so the texture space<->map space mappings are
#   invertible.  For the cases we're intererested in, the
#   third texture coordinate is always zero, and drops out
#   of the equations.
#
# Gets the s, t (texture) coordinates of a space point
#  from the threepoints info and the point location(v)
#
def texCoords(v, texp, coeff=1):
    p0 = texp[0]
    d1 = texp[1]-p0
    d2 = texp[2]-p0
    c = d1^d2
    denom = d1.x*c.z*d2.y-d1.x*d2.z*c.y-c.x*d1.z*d2.y-d2.x*d1.y*c.z+d1.z*d2.x*c.y+c.x*d1.y*d2.z
    s = (-c.z*d2.y*p0.x+c.z*p0.y*d2.x-c.z*d2.x*v.y+c.z*v.x*d2.y+d2.y*c.x*p0.z-d2.y*c.x*v.z-c.y*p0.z*d2.x+c.y*v.z*d2.x+c.y*d2.z*p0.x-c.y*d2.z*v.x+v.y*c.x*d2.z-p0.y*c.x*d2.z)/denom
    t = -(-d1.x*c.y*p0.z+d1.x*c.y*v.z+d1.x*c.z*p0.y-d1.x*c.z*v.y-d1.z*c.x*p0.y+d1.z*c.x*v.y+c.x*p0.z*d1.y-c.x*v.z*d1.y-p0.x*c.z*d1.y+p0.x*c.y*d1.z+v.x*c.z*d1.y-v.x*c.y*d1.z)/denom
    return s*coeff, t*coeff

def solveForThreepoints((v1, (s1, t1)), (v2, (s2, t2)), (v3, (s3, t3))):
    denom = s1*t2-s1*t3-t1*s2+t1*s3-s3*t2+t3*s2
    p0x = -t2*v1.x*s3+v2.x*t1*s3-t3*s1*v2.x+t3*v1.x*s2+t2*s1*v3.x-v3.x*t1*s2
    p0y = -t2*v1.y*s3+v2.y*t1*s3-t3*s1*v2.y+t3*v1.y*s2+t2*s1*v3.y-v3.y*t1*s2
    p0z = -(t2*v1.z*s3-v2.z*t1*s3+t3*s1*v2.z-t3*v1.z*s2-t2*s1*v3.z+v3.z*t1*s2)
    p0 = quarkx.vect(p0x, p0y, p0z)/denom
    d1x = -(t2*v3.x-t2*v1.x+t3*v1.x-v3.x*t1+v2.x*t1-v2.x*t3)
    d1y = -(t2*v3.y-t2*v1.y+t3*v1.y-v3.y*t1+v2.y*t1-v2.y*t3)
    d1z = -(t2*v3.z-t2*v1.z+t3*v1.z-v3.z*t1+v2.z*t1-v2.z*t3)
    d1 = quarkx.vect(d1x, d1y, d1z)/denom
    d2x = -s1*v3.x+s1*v2.x-s3*v2.x+v3.x*s2-v1.x*s2+v1.x*s3
    d2y = -s1*v3.y+s1*v2.y-s3*v2.y+v3.y*s2-v1.y*s2+v1.y*s3
    d2z = -s1*v3.z+s1*v2.z-s3*v2.z+v3.z*s2-v1.z*s2+v1.z*s3
    d2 = quarkx.vect(d2x, d2y, d2z)/denom
    return p0, d1+p0, d2+p0
    
#
# matrix for rotation taking u onto v
#
def matrix_rot_u2v(u,v):
    axis = u^v
    if axis:
      axis = axis.normalized
      import qhandles
      return qhandles.UserRotationMatrix(axis, v, u, 0)
    else:
      matrix = quarkx.matrix("1 0 0 0 1 0 0 0 1")
      if v*u > 0:
        return matrix
      else:
        return ~matrix

def read2vec(vals):
    if vals is None:
       return None, None
    strings = vals.split()
    if len(strings)<2:
       return None, None
    return eval(strings[0]), eval(strings[1])

def readNvec(vals):
    if vals is None:
       return None
    strings = vals.split()
    return tuple(map(lambda str:eval(str), strings))

#
# This one should be zapped soon, but not quite yet.
#
def buildLinearMatrix(dup):
    linear = dup["matrix"]
    matrix = quarkx.matrix('1 0 0 0 1 0 0 0 1')
    if linear is not None:
        matrix = quarkx.matrix(linear)*matrix
    scale = dup["scale"]
    if scale is not None:
        matrix = quarkx.matrix('%.2f 0 0 0 %.2f 0 0 0 %.2f'%scale)*matrix
    angles = dup["angles"]
    if type(angles)==type(""):
        angles = angles.split()
        angles = eval(angles[0]), eval(angles[1]), eval(angles[2])

    if angles is not None:
        angles = map(lambda a:a*deg2rad, angles)
        matrix = matrix_rot_y(angles[0])*matrix_rot_x(angles[1])*matrix_rot_z(angles[2])*matrix
    return matrix

def CaulkTexture():
    tex = quarkx.setupsubset()["DefaultTextureCaulk"]
    if tex is not None:
        return tex
    else:
        return quarkx.setupsubset()["DefaultTexture"]

#
# Checks if the file loaded in the editor is a bsp file.
#
def IsBsp(editor):
    return ("QBsp" in editor.fileobject.classes)

#
# returns n points, lying on the warped circle inscribed
#  in the quadrilateral defined by the four points
#  (tangent at the midpoints of the edges)
#
def warpedCircleFrom4Points(n, points):
    #
    # get the corners
    #
    corners=[]
    for i in range(4):
        corner=points[i]
        corners.append((corner, (points[i-1]-corner)/2, (points[(i+1)%4]-corner)/2))
    #
    # make angle & corner from angle (degrees)
    #
    def angle_corner(angle, corners=corners):
        if angle<90:
            return angle, corners[0]
        elif angle<180:
            return angle-90, corners[1]
        elif angle<270:
            return angle-180, corners[2]
        else:
            return angle-270, corners[3]
    #
    # get angles
    #
    angle_incr=360/n
    circle=[corners[0][0]+corners[0][1]]
    cum_angle=0.0
    for i in range(1,n):
        cum_angle=cum_angle+angle_incr
        angle, corner = angle_corner(cum_angle)
        #
        # get point in quarter-circle resting in
        #   the axes
        #
        point = quarkx.vect(1.0-math.sin(angle*deg2rad), 1.0-math.cos(angle*deg2rad), 0)
        #
        # get linear matrix for mapping
        #
        mat = matrix_u_v(corner[1], corner[2])
        circle.append(corner[0]+mat*point)
    return circle    
    
# ----------- REVISION HISTORY ------------
#
#
#$Log: maputils.py,v $
#Revision 1.29  2011/03/13 00:41:47  cdunde
#Updating fixed for the Model Editor of the Texture Browser's Used Textures folder.
#
#Revision 1.28  2008/11/17 19:10:23  danielpharos
#Centralized and fixed BSP file detection.
#
#Revision 1.27  2008/05/27 19:35:02  danielpharos
#Fix typo
#
#Revision 1.26  2008/02/07 13:19:07  danielpharos
#Fix typo in comment
#
#Revision 1.25  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.22  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.21  2001/10/22 10:24:32  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.19  2001/06/09 22:35:12  tiglari
#add warpec circle routine
#
#Revision 1.18  2001/05/13 01:07:58  tiglari
#disable buildLinearMapping, add CaulkTexture()
#
#Revision 1.17  2001/05/12 18:59:56  tiglari
#remove buildLinearMatrix
#
#Revision 1.16  2001/05/06 10:15:32  tiglari
#readNvec function, for arbitrary lenth string to tuple
#
#Revision 1.15  2001/05/06 06:02:19  tiglari
#Support angles Typ E in buildLinearMatrix (so that angles handle will work)
#
#Revision 1.14  2001/04/17 23:29:07  tiglari
#texture-rescaling bug fix (fixedscale="1" added to objects when they're
#dragged to the panel, removed when inserted to the map, blocks
#rescaling of textures on insert-by-pressing-panel-button
#
#Revision 1.13  2001/04/05 22:31:12  tiglari
#buildLinearMatrix now checks matrix not linear
#
#Revision 1.12  2001/03/29 09:27:58  tiglari
#scale & rotate specifics for duplicators
#
#Revision 1.11  2001/03/20 07:58:40  tiglari
#customizable hot key support
#
#Revision 1.10  2001/03/18 23:59:44  tiglari
#experimental merge
#
#
#Revision 1.9  2001/03/12 23:08:57  tiglari
#read2vec for path dup enhancements
#
#Revision 1.8  2001/03/04 06:41:15  tiglari
#arbitrary axis rot matrix-producer added
#
#Revision 1.7  2001/02/14 11:04:36  tiglari
#shifted some texture positioning utils in from maptexpin
#
#Revision 1.6  2000/09/04 21:27:56  tiglari
#added 2d line intersection finder, vectors->matrix utility
#
#Revision 1.5  2000/08/21 11:25:16  tiglari
#added projectpointtoplane (from plugins.maptagside)
#
#Revision 1.4  2000/07/29 02:04:54  tiglari
#added cyclenext, cycleprev
#
#Revision 1.3  2000/07/24 09:06:56  tiglari
#findlabelled added for finding items on menus (for face/texture revamp)
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#