"""   QuArK  -  Quake Army Knife

Python code to implement the various Duplicator styles.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapdups.py,v 1.16 2007/12/21 20:39:23 cdunde Exp $


#
# Feel free to add your own styles here, or better
# in a new plug-in that looks like this one.
#

Info = {
   "plug-in":       "Basic Duplicators",
   "desc":          "Standard Duplicator styles.",
   "date":          "31 oct 98",
   "author":        "Armin Rigo",
   "author e-mail": "arigo@planetquake.com",
   "quark":         "Version 5.1" }


from quarkpy.maputils import *
import quarkpy.mapduplicator
import quarkpy.maphandles
import quarkpy.mapcommands
StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator



class BasicDuplicator(StandardDuplicator):
    "Classic basic duplicators (count, offset, angle)."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        s = self.dup["angle"]
        if s:
            self.matrix = matrix_rot_z(float(s)*deg2rad)

   # def applylinear(self, matrix, direct=0):
   #     StandardDuplicator.applylinear(self, matrix, direct)
   #     s = self.dup["angle"]
   #     if s:
   #         angle = float(s)*deg2rad
   #         v = quarkx.vect(math.cos(angle), math.sin(angle), 0)
   #         v = matrix * v
   #         if v.x or v.y:
   #             angle = math.atan2(v.y, v.x)*rad2deg
   #             self.dup["angle"] = str(int(angle))


class LinearDuplicator(StandardDuplicator):
    "Linear (matrix) duplicators (count, offset, linear)."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        #
        # old matrix for backward compatibility
        #
        s = self.dup["linear"]
        if s:
            self.matrix = quarkx.matrix(s)

    def applylinear(self, matrix, direct=0):
        s = self.dup["linear"]
        if direct and s:
            m1 = quarkx.matrix(s)
            self.dup["linear"] = str(matrix * m1)
        else:
            StandardDuplicator.applylinear(self, matrix, direct)
            if s:
                m1 = quarkx.matrix(s)
                m1 = matrix * m1 * (~matrix)
                self.dup["linear"] = str(m1)


class SymXDuplicator(StandardDuplicator):
    "X-Axis Symmetry."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        self.matrix = quarkx.matrix((-1,0,0),(0,1,0),(0,0,1))


class SymYDuplicator(StandardDuplicator):
    "Y-Axis Symmetry."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        self.matrix = quarkx.matrix((1,0,0),(0,-1,0),(0,0,1))


class SymZDuplicator(StandardDuplicator):
    "Z-Axis Symmetry."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        self.matrix = quarkx.matrix((1,0,0),(0,1,0),(0,0,-1))


class SymXYDuplicator(StandardDuplicator):
    "X- and Y-Axis Symmetry (makes 3 images)."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        self.mx = quarkx.matrix((-1,0,0),(0,1,0),(0,0,1))
        self.my = quarkx.matrix((1,0,0),(0,-1,0),(0,0,1))
        self.mxy = quarkx.matrix((-1,0,0),(0,-1,0),(0,0,1))

    def do(self, item):
        item2 = item.copy()
        item3 = item.copy()
        item.linear(self.origin, self.mx)
        item2.linear(self.origin, self.my)
        item3.linear(self.origin, self.mxy)
        return [item, item2, item3]

class SymXYZDuplicator(StandardDuplicator):
    "XYZ-Axis Symmetry."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        x = 1
        y = 1
        z = 1
        if self.dup["x"]:
            x = -1
        if self.dup["y"]:
            y = -1
        if self.dup["z"]:
            z = -1
        self.matrix = quarkx.matrix((x,0,0),(0,y,0),(0,0,z))

class MirrorEnhanced(StandardDuplicator):
    "Enhanced Mirror."

    def readvalues(self):
        StandardDuplicator.readvalues(self)
        self.matrix = quarkx.matrix((-1,0,0),(0,1,0),(0,0,1))

        szmangle = self.dup["mangle"]
        angles = quarkx.vect(szmangle)
        pitch = -angles.x*deg2rad
        yaw = angles.y*deg2rad
        roll = angles.z*deg2rad

        mat = matrix_rot_z(yaw)*matrix_rot_y(pitch)*matrix_rot_x(roll)
        self.matrix = mat * self.matrix * (~mat)

    def applylinear(self, matrix, direct=0):
        StandardDuplicator.applylinear(self, matrix, direct)

        szmangle = self.dup["mangle"]
        angles = quarkx.vect(szmangle)
        pitch = -angles.x*deg2rad
        yaw = angles.y*deg2rad
        roll = angles.z*deg2rad

        mat = matrix_rot_z(yaw)*matrix_rot_y(pitch)*matrix_rot_x(roll)
        linear = matrix*mat
        cols = linear.cols
        #
        # get scale
        #
        scale=tuple(map(lambda v:abs(v), cols))
        cols = tuple(map(lambda v:v.normalized, cols))
        #
        # get rotations, cols[0] is 'rotated X axis, compute the others
        #
        axes = quarkx.matrix('1 0 0 0 1 0 0 0 1').cols
        yrot = cols[2]^cols[0]
        zrot = cols[0]^yrot
        pitch = math.asin(cols[0]*axes[2])
        if abs(pitch)<89.99:
            p = projectpointtoplane(cols[0],axes[2],
                quarkx.vect(0,0,0), axes[2]).normalized
            yaw = math.atan2(p.y, p.x)
        else:
            yaw = 0
        y2 = matrix_rot_y(-pitch)*matrix_rot_z(-yaw)*yrot
        roll = math.atan2(y2*axes[2], y2*axes[1])
        self.dup["mangle"] = str(-pitch/deg2rad) + " " + str(yaw/deg2rad) + " " + str(roll/deg2rad)


class DiggingDuplicator(StandardDuplicator):
    "For what is a Digger rather than a Duplicator. (abstract)"

    Icon = (ico_dict['ico_mapdups'], 1)

    def readvalues(self):
        pass

    def makeneg(self, item):
        if not (item.type in (':e', ':b')):
            if self.dup["global"]:
                item["neg"]="g"
            else:
                item["neg"]="1"



class Digger(DiggingDuplicator):
    "Makes everything in the group negative."

    def do(self, item):
        self.makeneg(item)
        return [item]



class DepthDuplicator(DiggingDuplicator):
    "Digger with a 'depth' parameter. (abstract)"

    def readvalues(self):
        self.depth = float(self.dup["depth"])
        if self.depth<=0:
            raise "depth<=0"

    def applylinear(self, matrix, direct=0):
        depth = float(self.dup["depth"])
        factor = math.exp(math.log(abs(matrix))/3)
        self.dup["depth"] = quarkx.ftos(depth*factor)


class HollowMaker(DepthDuplicator):
    "Makes the polyhedrons in the group hollow."

    def do(self, item):
        item2 = item.copy()
        item2.inflate(-self.depth)
        self.makeneg(item2)
        return [item, item2]



#
# a buildimages method for this is supplied in
#  mapmiteredges.py, for mitered edges.
#
class WallMaker(DepthDuplicator):
    "Extrude the polyhedrons in the group."

    def do(self, item):
        item2 = item.copy()
        item.inflate(self.depth)
        self.makeneg(item2)
        return [item, item2]


#
# This plug-in introduces a new menu item for Duplicators : "Dissociate Duplicator images".
#

def dissociate1click(m):
    editor = mapeditor()
    if editor is None: return
    getmgr = quarkpy.mapduplicator.DupManager
    undo = quarkx.action()
    list = editor.layout.explorer.sellist
    list2=[]
    for obj in list:
        if obj.type == ':d':
           list2.append(obj)
           if obj["out"] and obj.parent is not None:
               for item in obj.parent.subitems:
                   if item!=obj and item.type==':d' and item["out"]:
                       list2.append(item)

    for obj in list2:
        if obj.type == ':d':
            mgr = getmgr(obj)
            image = 0
            insertbefore = obj.nextingroup()
            while 1:
                objlist = mgr.buildimages(image)
                if len(objlist)==0:
                    break
                image = image + 1
                new = quarkx.newobj("%s (%d):g" % (obj.shortname, image))
                for o in objlist:
                    new.appenditem(o)
                undo.put(obj.parent, new, insertbefore)
            undo.exchange(obj, None)    # removes the duplicator
    editor.ok(undo, "dissociate images")


dissociate = quarkpy.qmenu.item("Dissociate Duplicator images", dissociate1click,"|Dissociate Duplicator images:\n\nOnly active when you have selected a duplicator. This will create actural copies of the duplicator-object(s), and remove the duplicator itself.\n\nIf the duplicator is an 'out' duplicator, and there are others (immediately) in the group, they will all be dissociated together.|intro.mapeditor.menu.html#disdupimages")

def dissociateGroupClick(m):
    editor = mapeditor()
    if editor is None: return
    getmgr = quarkpy.mapduplicator.DupManager
    list = editor.layout.explorer.sellist
    grouplist = []
    for group in list:
        if group.type == ":g":
            while 1:
                undo = quarkx.action()

                objlist1 = group.findallsubitems("", ":d")
                if len(objlist1) == 0:
                    break
                obj = objlist1[-1]

                list2=[obj]
                if obj["out"] and obj.parent is not None:
                    for item in obj.parent.subitems:
                        if item!=obj and item.type==':d' and item["out"]:
                            list2.append(item)

                for obj in list2:
                    mgr = getmgr(obj)
                    image = 0
                    insertbefore = obj.nextingroup()
                    while 1:
                        objlist = mgr.buildimages(image)
                        if len(objlist)==0:
                            break
                        image = image + 1
                        new = quarkx.newobj("%s (%d):g" % (obj.shortname, image))
                        for o in objlist:
                            new.appenditem(o)
                        undo.put(obj.parent, new, insertbefore)
                    undo.exchange(obj, None)    # removes the duplicator
                editor.ok(undo, "dissociate images in group")


DissociateGroupItem = quarkpy.qmenu.item("Dissociate Duplicator images", dissociateGroupClick,"|Dissociate Duplicator images:\n\nOnly active when you have selected a duplicator. This will create actural copies of the duplicator-object(s), and remove the duplicator itself.\n\nIf the duplicator is an 'out' duplicator, and there are others (immediately) in the group, they will all be dissociated together.|intro.mapeditor.menu.html#disdupimages")


#
# Add item to the Commands menu.
#

import quarkpy.qmenu
import quarkpy.mapcommands
import quarkpy.mapentities


def commands1click(menu, oldclick = quarkpy.mapcommands.onclick):
    oldclick(menu)
    editor = mapeditor()
    if editor is None: return
    if ":d" in map(lambda obj: obj.type, editor.layout.explorer.sellist):   # any Duplicator selected ?
        dissociate.state = 0
    else:
        dissociate.state = qmenu.disabled

quarkpy.mapcommands.items.append(quarkpy.qmenu.sep)   # separator
quarkpy.mapcommands.items.append(dissociate)
quarkpy.mapcommands.onclick = commands1click


#
# Add item to the Duplicators pop-up menu.
#

def DuplicatorMenu(o, editor, oldmenu = quarkpy.mapentities.DuplicatorType.menubegin.im_func):
    dissociate.state = 0
    return oldmenu(o, editor) + [dissociate, quarkpy.qmenu.sep]

quarkpy.mapentities.DuplicatorType.menubegin = DuplicatorMenu

def DupGroupMenu(o, editor, oldmenu = quarkpy.mapentities.GroupType.menubegin.im_func):	
    return oldmenu(o, editor) + [DissociateGroupItem, quarkpy.qmenu.sep]

quarkpy.mapentities.GroupType.menubegin = DupGroupMenu



#
# Register the duplicator types from this plug-in.
#

quarkpy.mapduplicator.DupCodes.update({
  "dup basic":           BasicDuplicator,
  "dup lin":             LinearDuplicator,
  "dup symx":            SymXDuplicator,
  "dup symy":            SymYDuplicator,
  "dup symz":            SymZDuplicator,
  "dup symxy":           SymXYDuplicator,
  "dup symxyz":          SymXYZDuplicator,
  "dup enhancedmirror":  MirrorEnhanced,
  "digger":              Digger,
  "hollow maker":        HollowMaker,
  "wall maker":          WallMaker,
})

#
# Clear texture cycle files cache (so that edits will
#   be reloaded)
#

def resetTextureCycleClick(m):
    quarkpy.mapduplicator.Dup_Tex_Dicts={}

quarkpy.mapcommands.items.append(qmenu.item("Reset Texture Cycle",resetTextureCycleClick,"|Reset Texture Cycle:\n\nReload files specifying texture cycles for duplicators.|intro.mapeditor.menu.html#disdupimages"))

# ----------- REVISION HISTORY ------------
#
#
# $Log: mapdups.py,v $
# Revision 1.16  2007/12/21 20:39:23  cdunde
# Added new Templates functions and Templates.
#
# Revision 1.15  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.12  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.11  2001/10/22 10:15:48  tiglari
# live pointer hunt, revise icon loading
#
# Revision 1.10  2001/09/23 07:00:34  tiglari
# mitered edges for wall maker duplicator
#
# Revision 1.9  2001/08/15 17:49:55  decker_dk
# Added a 'dup symxyz' with toggleable axes.
#
# Revision 1.8  2001/08/07 23:33:43  tiglari
# reset texture cycle command
#
# Revision 1.7  2001/05/19 03:55:42  tiglari
# dissociate one, dissociate all, for 'out' duplicators
#
# Revision 1.6  2001/05/12 10:15:56  tiglari
# remove matrix2 (buildLinearMatrix) support from linear duplicator
#
# Revision 1.5  2001/04/08 02:44:15  tiglari
# fix conflict
#
# Revision 1.4  2001/04/06 06:00:35  tiglari
# fixed a messed up change to Linear Duplicator readavalues
#
# Revision 1.3  2001/03/29 09:28:55  tiglari
# scale and rotate specifics for duplicators
#
# Revision 1.2  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#
