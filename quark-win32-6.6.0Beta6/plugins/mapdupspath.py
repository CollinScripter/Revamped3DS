# QuArK  -  Quake Army Knife
#
# Copyright (C) 1996-2000 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/mapdupspath.py,v 1.50 2005/10/15 00:49:51 cdunde Exp $


Info = {
   "plug-in":       "Path Duplicator",
   "desc":          "Path Duplicator",
   "date":          "3 feb 01",
   "author":        "Decker, also tiglari",
   "author e-mail": "decker@planetquake.com, tiglari@planetquake.com",
   "quark":         "Version 6.2"
}

import quarkx
from quarkpy.maputils import *
import plugins.deckerutils
import quarkpy.mapduplicator
import quarkpy.maphandles
import quarkpy.mapentities
import quarkpy.qhandles
import quarkpy.mapbtns
import quarkpy.dlgclasses
import math
StandardDuplicator = quarkpy.mapduplicator.StandardDuplicator
DuplicatorManager = quarkpy.mapduplicator.DuplicatorManager
DupOffsetHandle = quarkpy.mapduplicator.DupOffsetHandle

from quarkpy.mapentities import ObjectOrigin
from quarkpy.maphandles import GetUserCenter
from quarkpy.maphandles import UserCenterHandle


#
# destructive, do to copies
#
def evaluateDuplicators(group):
    for obj in group.subitems:
       if obj.type==":b" or obj.type==":g":
           evaluateDuplicators(obj)
    getmgr = quarkpy.mapduplicator.DupManager
    for obj in group.subitems:
       if obj.type==":d":
            index=group.subitems.index(obj)
            mgr = getmgr(obj)
            image = 0
            while 1:
                objlist = mgr.buildimages(image)
                if len(objlist)==0:
                    break
                image = image + 1
                new = quarkx.newobj("%s (%d):g" % (obj.shortname, image))
                for o in objlist:
                    new.appenditem(o)
                group.removeitem(index)
                group.insertitem(index, new)

#
#  Two ways of making axes that don't `twist'.  This leads to the
#    section not joining properly, but maybe something can be done
#    about this someday (with curved `elbows', for example)
#
def MakeAxes2(x):
    xn=x.normalized
    if abs(xn*quarkx.vect(0,1,0))<.1:
        z=(xn^quarkx.vect(-1,0,0)).normalized
    else:
        z=(xn^quarkx.vect(0,1,0)).normalized
    y = (z^x).normalized
    return xn, y, z

def Vertical(x):
    x=x.normalized
    return abs(x*quarkx.vect(0,0,1))>.99999

def MakeLevelAxes(x):
    x=x.normalized
    mapx, mapy, mapz = quarkx.vect(1,0,0),quarkx.vect(0,1,0),quarkx.vect(0,0,1)
    dot = x*mapz
    #
    # project onto the xy plane
    #
    xp = quarkx.vect(x*mapx,x*mapy,0).normalized
    y = matrix_rot_z(math.pi/2)*xp
    return x, y, (x^y).normalized

def NewAxes(prevaxes, newx):
    try:
        mat=matrix_rot_u2v(prevaxes[0],newx)
        return newx, mat*prevaxes[1], mat*prevaxes[2]
    except:  # no angle
        return prevaxes

def MakeUniqueTargetname():
    import time
    return "t" + time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))


SMALL=0.001

def getNormalFaces(faces, axis):
    def normalFace(face,axis=axis):
        return abs(face.normal*axis-1)<SMALL
    return filter(normalFace,faces)

def getends(group,x_axis):
    list = group.findallsubitems("",":f")
    return getNormalFaces(list,-x_axis), getNormalFaces(list,x_axis)

#
# Position following path points
#
class PositionFollowingDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (210,250)
    dfsep = 0.50

    dlgdef = """
        {
        Style = "9"
        Caption = "Position Following"

        sep: = {Typ="S" Txt=" "}

        number: =
        {
        Txt = "Number"
        Typ = "EF1"
        Hint = "How many of the following path points to position" $0D " (new ones will be made if needed)"
        }

        sep: = {Typ="S" Txt=" "}

        angles: =
        {
        Txt = "First Pitch Yaw"
        Typ = "EQ"
        Hint = "Pitch Yaw angles to next, in degrees, map space"
        }

        sep: = {Typ="S" Txt=" "}

        more_angles: =
        {
        Txt = "More Pitch Yaw"
        Typ = "EQ"
        Hint = "Pitch Yaw angles for remaining, in degrees, relative to previous"
        }

        sep: = {Typ="S" Txt=" "}

        distance: =
         {
         Txt = "Distance"
         Typ = "EU"
         Hint = "Distance to next, in units"
         }


         sep: = {Typ="S" Txt=" "}

        shifttail: =
         {
         Txt = "Shift Tail"
         Typ = "X"
         Hint = "If checked, remaining points are moved to retain distance w.r.t last in moved series"
         }

         sep: = {Typ="S" Txt=" "}

         exit:py = { Txt=""}
    }
    """


class PathDuplicatorPointHandle(quarkpy.qhandles.IconHandle):

    def __init__(self, origin, centerof, pathdupmaster=0):
        quarkpy.qhandles.IconHandle.__init__(self, origin, centerof)
        self.pathdupmaster = pathdupmaster
        self.mainpathdup=self.centerof.parent.findname("Path Duplicator:d")


    def findpathdupcornerwith(self, list, entitykey, entitykeydata):
        for e in list:
            if e.type == ':d':
                if e[entitykey] == entitykeydata:
                    return e
        return None

    def makecopy(self, original):
        new = original.copy()
        # Erase all subitems from object.
        while (new.itemcount > 0):
            new.removeitem(new.itemcount-1)
        # Erase all key/keydata in object.
        for key in original.dictspec.keys():
            new[key] = ""
        # Copy only those key/keydata's we're interested in.
        new.shortname = "PathDup.Point"
        new["macro"] = "dup path_point"
        new["origin"] = original["origin"]
        new["target"] = original["target"]
        new["targetname"] = original["targetname"]
        return new

    #
    # For decent org., I wanted this to be a method of
    #  PathPointDuplicator, but couldn't get it to
    #  work.
    #
    def sourcelist2(self):
        myself = self.centerof
        list = []
        if (myself.parent is not None):
            for item in myself.parent.subitems:
                if item!=myself and (item.type!=':d' or quarkpy.mapduplicator.DupManager(item).siblingincluded(myself)):
                    list.append(item)
        return list

    def menu(self, editor, view):

        def after1click(m, self=self, editor=editor, view=view):
            # Insert a copy of me, between me and whoever I point to, and give this
            # new copy a unique targetname, which I should now point to instead.
            # Try also to put the new copy, into the tree-view in targeting-order.
            undo = quarkx.action()
            new = self.makecopy(self.centerof)
            new["targetname"] = MakeUniqueTargetname()
            undo.setspec(self.centerof, "target", new["targetname"])
            who_do_i_target = self.findpathdupcornerwith(self.centerof.parent.subitems, "targetname", new["target"])
            if (who_do_i_target is not None):
                newtranslate = (who_do_i_target.origin - self.centerof.origin) / 2
            else:
                prev_prev = self.findpathdupcornerwith(self.centerof.parent.subitems, "target", self.centerof["targetname"])
                if (prev_prev is not None) and (prev_prev["macro"] == "dup path_point"):
                    newtranslate = (self.centerof.origin - prev_prev.origin)
                else:
                    newtranslate = quarkx.vect(64,0,0)
            new.translate(newtranslate)
            newtranslate = new.origin - quarkpy.qhandles.aligntogrid(new.origin, 1)
            new.translate(newtranslate)
            if ((who_do_i_target is not None) and (who_do_i_target.parent == self.centerof.parent)):
                undo.put(self.centerof.parent, new, who_do_i_target)
            else:
                undo.put(self.centerof.parent, new)
            editor.ok(undo, "Insert after PathDuplicator corner")
            editor.layout.explorer.sellist = [new]

        def before1click(m, self=self, editor=editor, view=view):
            # Insert a copy of me, between me and whoever points to ne, and give this
            # new copy a unique targetname, which my previous should point to instead.
            # Try also to put the new copy, into the tree-view in targeting-order.
            undo = quarkx.action()
            who_targets_me = self.findpathdupcornerwith(self.centerof.parent.subitems, "target", self.centerof["targetname"])
            new = self.makecopy(self.centerof)
            new["targetname"] = MakeUniqueTargetname()
            new["target"] = self.centerof["targetname"]
            if (who_targets_me is not None) and (who_targets_me["macro"] == "dup path_point"):
                newtranslate = (who_targets_me.origin - self.centerof.origin) / 2
            else:
                next_next = self.findpathdupcornerwith(self.centerof.parent.subitems, "targetname", self.centerof["target"])
                if (next_next is not None) and (next_next["macro"] == "dup path_point"):
                    newtranslate = (self.centerof.origin - next_next.origin)
                else:
                    newtranslate = quarkx.vect(-64,0,0)
            new.translate(newtranslate)
            newtranslate = new.origin - quarkpy.qhandles.aligntogrid(new.origin, 1)
            new.translate(newtranslate)
            undo.put(self.centerof.parent, new, self.centerof)
            if (who_targets_me is not None):
                undo.setspec(who_targets_me, "target", new["targetname"])
            editor.ok(undo, "Insert before PathDuplicator corner")
            editor.layout.explorer.sellist = [new]

        def remove1click(m, self=self, editor=editor, view=view):
            # Tell whoever points to me, that it should now point to my target instead, as I am going to be removed now.
            undo = quarkx.action()
            what_is_my_target = self.centerof["target"]
            who_targets_me = self.findpathdupcornerwith(self.centerof.parent.subitems, "target", self.centerof["targetname"])
            if who_targets_me is not None:
                undo.setspec(who_targets_me, "target", what_is_my_target)
            undo.exchange(self.centerof, None);
            editor.ok(undo, "Remove PathDuplicator corner");

        def speeddraw1click(m, self=self, editor=editor, view=view):
            #
            walker = self.centerof
            who_targets_me = self.findpathdupcornerwith(self.centerof.parent.subitems, "target", walker["targetname"])
            while (who_targets_me is not None) and (who_targets_me["target"] is not None):
                walker = who_targets_me
                who_targets_me = self.findpathdupcornerwith(self.centerof.parent.subitems, "target", walker["targetname"])
            if (walker["speeddraw"] is not None):
                if (walker["speeddraw"] == "1"):
                    walker["speeddraw"] = "0"
                else:
                    walker["speeddraw"] = "1"
            #FIXME - How to redraw the duplicator, to reflect the change?!?


        def selectdup1click(m, self=self, editor=editor):
            editor.layout.explorer.uniquesel = self.mainpathdup
            editor.invalidateviews()

        def selecttail1click(m, self=self, editor=editor):
            center = self.centerof
            list = self.sourcelist2()
            pathlist = plugins.deckerutils.GetEntityChain(self.centerof["target"], list)
            editor.layout.explorer.sellist = [center] + pathlist
            editor.invalidateviews()

        def retarget1click(m, self=self, editor=editor):
            group = self.centerof.parent
            previous = self.centerof
            i=1
            undo = quarkx.action()
            for item in group.subitems:
                if item["macro"]=='dup path_point':
                    targetname = MakeUniqueTargetname()+'.'+`i`
                    i=i+1
                    undo.setspec(previous,"target",targetname)
                    undo.setspec(item,"targetname",targetname)
                    previous=item
            undo.setspec(previous,"target","dpathX")
            editor.ok(undo, 'retarget path corners')
            editor.layout.explorer.uniquesel=self.centerof
            editor.invalidateviews()

        def positionfollowing1click(m, self=self, editor=editor):
            class pack:
                  "stick stuff here"

            def setup(self,handle=self, pack=pack):
                list = handle.sourcelist2()
                if self.src["number"] is None:
                    self.src["number"] = 1,
                pathlist = plugins.deckerutils.GetEntityChain(handle.centerof["target"], list)
                thisorigin = handle.centerof.origin
                if pathlist:
                    nextorigin = pathlist[0].origin
                    dist = nextorigin-thisorigin
                    normdist = dist.normalized
                    self.src["distance"] = "%.2f"%abs(dist)
                    xax, yax, zax = (quarkx.vect(1,0,0),
                                    quarkx.vect(0,1,0),
                                    quarkx.vect(0,0,1))
                    pitch = "%.1f"%(math.asin(normdist*zax)/deg2rad)
                    yaw = "%.1f"%(math.atan2(normdist*yax, normdist*xax)/deg2rad)
                    self.src["angles"] = pitch+' '+yaw
                pack.list=pathlist
                pack.thisorigin=thisorigin

            def action(self, handle=self, editor=editor, pack=pack):
                if self.src["distance"]:
                    distance = eval(self.src["distance"])
                else:
                    distance = 0
                pitch, yaw = read2vec(self.src["angles"])
                if not distance or pitch is None:
                    return
                list = pack.list
                vangle = quarkx.vect(1,0,math.sin(pitch*deg2rad)).normalized
                normdist = matrix_rot_z(yaw*deg2rad)*vangle
                undo=quarkx.action()
                if list:
                    next = list[0]
                    new = next.copy()
                else:
                    new = handle.centerof.copy()
                    new["targetname"] = MakeUniqueTargetname()+'.0'
                    undo.setspec(handle.centerof,"target",new["targetname"])
                shift = pack.thisorigin+distance*normdist-new.origin
                new.translate(shift)
                if list:
                    undo.exchange(next, new)
                else:
                    undo.put(handle.centerof.parent,new)
                number, = self.src["number"]
                pitch2, yaw2 = read2vec(self.src["more_angles"])
                for i in range(1, number):
                    shift = None
                    if pitch2 is None:
                        continue
                    pitch = pitch+pitch2
                    yaw = yaw+yaw2
                    vangle=quarkx.vect(1,0,math.sin(pitch*deg2rad)).normalized
                    normdist = matrix_rot_z(yaw*deg2rad)*vangle
                    if i>=len(list):
                        new2 = new.copy()
                        #
                        # clock doesn't tick fast enough to give unique names
                        #
                        new2["targetname"] = MakeUniqueTargetname()+'.'+`i`
                        undo.setspec(new,"target",new2["targetname"])
                    else:
                        new2 = list[i].copy()
                    shift=new.origin+distance*normdist-new2.origin
                    new2.translate(shift)
                    if i>=len(list):
                        list.append(new2)
                        undo.put(new.parent, new2)
                    else:
                        undo.exchange(list[i],new2)
                    new = new2

                if self.src["shifttail"] and shift is not None:
                   for i in range(number,len(list)):
                       new = list[i].copy()
                       new.translate(shift)
                       undo.exchange(list[i], new)


                editor.ok(undo, "Move following path point(s)")
                editor.layout.explorer.uniquesel=handle.centerof

            PositionFollowingDlg(quarkx.clickform, 'positionfollowing', editor, setup, action)



        menulist = [qmenu.item("Insert after",  after1click)]
        if (self.pathdupmaster == 0):

            # if it is not the PathDup, then it must be a PathDupCorner, and several more menuitems are available
            menulist.append(qmenu.item("Insert before", before1click))
            menulist.append(qmenu.item("Remove",        remove1click))
            menulist.append(qmenu.item("Select main dup",   selectdup1click, "|Select main duplicator (making all path points visible)"))
            menulist.append(qmenu.item("Select tail", selecttail1click, "Multi-select this & the following path points"))
            menulist.append(qmenu.item("Position following", positionfollowing1click, "|Position following path points relative to this one, making new ones if necessary"))

        else:
            menulist.append(qmenu.item("Retarget Path", retarget1click, "Set target/targetname specifics, following subitem order"))
        menulist.append(qmenu.item("Toggle speeddraw",  speeddraw1click))

        return menulist


class PathPointHandle(PathDuplicatorPointHandle):

    def __init__(self, origin, centerof, mainpathdup):
        quarkpy.qhandles.IconHandle.__init__(self, origin, centerof)
        self.pathdupmaster = 0
        self.mainpathdup = mainpathdup


    #
    # called at end of drag, resets selection
    #
    def ok(self, editor, undo, old, new):
        PathDuplicatorPointHandle.ok(self,editor,undo,old,new)
        editor.layout.explorer.sellist=[self.mainpathdup.dup]

    def menu(self, editor, view):
        return PathDuplicatorPointHandle.menu(self, editor, view)

        def seldup1click(m,self=self,editor=editor):
            editor.layout.explorer.uniqusel=self.mainpathdup

        seldup = qmenu.item("Select duplicator",seldup1click,"select main duplicator (so that all path handles become visible)")
        pointhandles = pointhandles = [seldup]
        return pointhandles

class PathDuplicatorPoint(DuplicatorManager):

    Icon = (ico_dict['ico_mapdups'], 2)

    def buildimages(self, singleimage=None):
        pass

    def handles(self, editor, view):
        hndl = PathDuplicatorPointHandle(self.dup.origin, self.dup)
        return [hndl]

    def sourcelist2(self):
        myself = self.dup
        list = []
        if (myself.parent is not None):
            for item in myself.parent.subitems:
                if item!=myself and (item.type!=':d' or quarkpy.mapduplicator.DupManager(item).siblingincluded(myself)):
                    list.append(item)
        return list

class PathDuplicator(StandardDuplicator):

    cuberadius = 3096

    def readvalues(self):
        self.origin = self.dup.origin
        if self.origin is None:
            self.origin = quarkx.vect(0,0,0)
        self.matrix = None
        self.target = self.dup["target"]
        try:
           self.speed = int(self.dup["speeddraw"])
        except:
           self.speed = 0
        try:
           self.scaletex = int(self.dup["scaletexture"])
        except:
           self.scaletex = 0

    def applylinear(self, matrix, direct=0):
        pass

    def do(self, item):
        pass

    def sourcelist(self):
        list = StandardDuplicator.sourcelist(self)
        group = quarkx.newobj("group:g");
        for item in list:
           group.appenditem(item.copy())
        evaluateDuplicators(group)
        return group

    def sourcelist2(self):
        myself = self.dup
        list = []
        if (myself.parent is not None):
            for item in myself.parent.subitems:
                if item!=myself and (item.type!=':d' or quarkpy.mapduplicator.DupManager(item).siblingincluded(myself)):
                    list.append(item)
        return list

    def buildimages(self, singleimage=None):
        try:
            self.readvalues()
        except:
            print "Note: Invalid Duplicator Specific/Args."
            return

        pathlist = plugins.deckerutils.GetEntityChain(self.target, self.sourcelist2())
        #pathlist.insert(0, self.dup)

        templategroup = self.sourcelist()
        templatebbox = quarkx.boundingboxof([templategroup])
        templatesize = templatebbox[1] - templatebbox[0]

        # If SPEEDDRAW specific is set to one, we'll only use a single cube to make the path.
        if self.speed == 1:
           del templategroup
           templategroup = quarkx.newobj("group:g")
           templategroup.appenditem(plugins.deckerutils.NewXYZCube(templatesize.x, templatesize.y, templatesize.z, quarkx.setupsubset()["DefaultTexture"]))

        if (singleimage is None and self.speed != 1):
           viewabletemplategroup = templategroup.copy()
           viewabletemplategroup[";view"] = str(VF_IGNORETOBUILDMAP)  # Do not send this to .MAP file
           newobjs = [viewabletemplategroup]
        else:
           newobjs = []
        templatescale = min(templatesize.x, templatesize.y)/3
        OriginShift = -ObjectOrigin(templategroup)
        templategroup.translate(OriginShift, 0)    # Move it to (0,0,0)

        tile = templategroup.findname("Tile:g")
        if tile is not None:
            templategroup.removeitem(tile)

        templatefront=getNormalFaces(templategroup.findallsubitems("",":f"),
                                     quarkx.vect(1,0,0))
        rimvtxes=[]
        for face in templatefront:
            for vtxes in face.vertices:
                for vtx in vtxes:
                    rimvtxes.append(vtx)

#        # -- If SCALETEXTURES is on, use the linear() operation
#        if (self.scaletex != 0):
#           scalematrix = quarkx.matrix((2048/templatescale,0,0), (0,1,0), (0,0,1))
#        else:
#           # -- User does not want to scale textures (who wants), but then we must scale the polys in another way
#           flist = templategroup.findallsubitems("", ":f")
#           for f in flist:
#              f.translate(quarkx.vect(2048 - f.dist,0,0) * f.normal.x)

        count = len(pathlist)-1
        if (singleimage is not None) and (singleimage >= count): # Speed up Dissociate images processing
            return [] # Nothing more to send back!
        prevaxes = quarkx.vect(1,0,0),quarkx.vect(0,1,0),quarkx.vect(0,0,1)
        for i in range(count):
            #DECKER 2002-08-04 part-2: Moved this if-structure above the for-loop
            #if (singleimage is not None): # Speed up Dissociate images processing
            #   if (singleimage >= count):
            #      return [] # Nothing more to send back!
            #   #DECKER 2002-08-04: Removed this else, as it would cause dissociate images to produce an incorrect result.
            #   #                   Found by quantum_red in QuArK forum date: 2002-07-30 subject: "Texture Alignment Problem".
            #   #else:
            #   #   i = singleimage
            thisorigin = pathlist[i].origin
            nextorigin = pathlist[i+1].origin
            #print "Image#", i, "this", thisorigin, "next", nextorigin

            list = templategroup.copy()

            pathdist = nextorigin - thisorigin

#            # -- Place center between the two paths
#            neworigin = pathdist*0.5 + thisorigin

            #
            # place center so textures will tile from start
            #
            neworigin = pathdist.normalized*0.5*templatesize.z + thisorigin

            if (pathlist[i]["level"] or self.dup["level"]) and not Vertical(pathdist):
               prevaxes = MakeLevelAxes(pathdist.normalized)
            else:
               prevaxes = NewAxes(prevaxes,pathdist.normalized)
            xax, yax, zax = prevaxes
            #
            # N.B. when the three args are vectors they are indeed
            #  input as columns.  Tuples otoh will go in as rows.
            #
            mat = quarkx.matrix(xax,yax,zax)
            list.translate(neworigin, 0)
            list.linear(neworigin, mat)
            front, back = getends(list,xax)

            for face in front:
               center = projectpointtoplane(thisorigin,face.normal,face.dist*face.normal,face.normal)
               face.translate(thisorigin-center,0)
               if i>0:
                   if singleimage is not None:
                       lastx = (thisorigin-pathlist[i-1].origin).normalized
                       joinnorm=((xax+lastx)/2).normalized
                   face.distortion(-joinnorm,thisorigin)
            for face in back:
               center = projectpointtoplane(thisorigin,face.normal,face.dist*face.normal,face.normal)
               face.translate(nextorigin-center,0)
               if i<count-1:
                   nextx=(pathlist[i+2].origin-nextorigin).normalized
                   joinnorm=((xax+nextx)/2).normalized
                   face.distortion(joinnorm,nextorigin)

            #
            # find out where flat-ended segments would end if they
            #   are to just touch at the corners
            #
            def vtxshift(vtx,mat=mat,orig=thisorigin, shift=OriginShift):
                return mat*(vtx+shift)+orig
            if (tile is not None) or self.dup["squarend"]:
                startseg=endseg=0
                for vtx in map(vtxshift,rimvtxes):
                    frontpoint=projectpointtoplane(vtx,xax,thisorigin,front[0].normal)
                    frontproj = (frontpoint-thisorigin)*xax
                    startseg=max(startseg,frontproj)
                    backpoint=projectpointtoplane(vtx,-xax,nextorigin,back[0].normal)
                    backproj = -(backpoint-nextorigin)*xax
                    endseg=min(endseg,backproj)

            if tile is not None:
                tileableLength=abs(pathdist)-startseg+endseg
                tileOffset = (tileableLength%templatesize.x)/2
                tileTimes=int(tileableLength/templatesize.x)
                for i in range(tileTimes):
                    if i==0:
                        newTile=tile.copy()
                        newTile.linear(quarkx.vect(0,0,0),mat)
                        newTile.translate(thisorigin+(startseg+templatesize.x*0.5+tileOffset)*xax)
                    else:
                        newTile=newTile.copy()
                        newTile.translate(xax*templatesize.x)
                    list.appenditem(newTile)
            #
            #  Code below creates `box' shaped sections that just touch at the
            #   edges, or are set back.  Can't do it by taking vertices of actual
            #   front and back faces above because these don't seem to be
            #   computed yet.
            #
            if self.dup["squarend"]:
                 setback = self.dup["setback"]
                 if setback is None:
                     setback=0
                 else:
                     setback,=setback
                 if startseg:
                     start=xax*(startseg+setback)
                     for face in front:
                         face.translate(start)
                         face.distortion(-xax,thisorigin+start)
                 if endseg:
                     end=xax*(endseg-setback)
                     for face in back:
                         face.translate(end)
                         face.distortion(xax,nextorigin+end)

            if (singleimage is None) or (i==singleimage):
                newobjs = newobjs + [list]
            del list
            if (i==singleimage): # Speed up Dissociate images processing
                break
        return newobjs


    def handles(self, editor, view):
        try:
            self.readvalues()
        except:
            print "Note: Invalid Duplicator Specific/Args."
            return
        def makehandle(item,self=self):
            return PathPointHandle(item.origin, item, self)
        pathHandles=map(makehandle,plugins.deckerutils.GetEntityChain(self.target, self.sourcelist2()))

        return DuplicatorManager.handles(self, editor, view) + [PathDuplicatorPointHandle(self.dup.origin, self.dup, 1)]+pathHandles




class InstanceDuplicator(PathDuplicator):

    def handles(self, editor, view):
        h = StandardDuplicator.handles(self, editor, view)
        h[0].hint = "Copies of my contents are placed at the path points\n"
        if self.dup["usercenter"] is not None:
            h.append(UserCenterHandle(self.dup))
        return h


    def buildimages(self, singleimage=None):

        if len(self.dup.subitems)==0:
            return


        try:
            self.readvalues()
        except:
            print "Note: Invalid Duplicator Specific/Args."
            return

        pathlist = plugins.deckerutils.GetEntityChain(self.target, self.sourcelist2())
        #pathlist.insert(0, self.dup)


        templategroup = self.sourcelist()
        templatebbox = quarkx.boundingboxof([templategroup])
        templatesize = templatebbox[1] - templatebbox[0]

        newobjs = []
        if (singleimage is None and self.speed != 1):
           viewabletemplategroup = templategroup.copy()
           viewabletemplategroup[";view"] = str(VF_IGNORETOBUILDMAP)  # Do not send this to .MAP file
           newobjs = [viewabletemplategroup]
        else:
           newobjs = []
        templatescale = min(templatesize.x, templatesize.y)/3
#        templategroup.translate(-ObjectCustomOrigin(templategroup), 0)    # Move it to (0,0,0)
        if self.dup["usercenter"] is not None:
            templategroup.translate(-GetUserCenter(self.dup), 0)    # Move it to (0,0,0)
        elif self.dup["elbow"] is not None:
            templategroup.translate(-pathlist[1].origin, 0)
        else:
            templategroup.translate(-ObjectOrigin(templategroup), 0)    # Move it to (0,0,0)
        for item in templategroup.subitems[:]:
            if item.type==":d" and item["macro"]=="dup origin":
                templategroup.removeitem(item)

        count = len(pathlist)
        prevaxes = quarkx.vect(1,0,0),quarkx.vect(0,1,0),quarkx.vect(0,0,1)
        if self.dup["elbow"] == 1:
            retromat = ~(matrix_rot_u2v(prevaxes[0],(pathdist[1]-pathdist[0]).normalized))
            prevaxes = retromat*prevaxes[0],retromat*prevaxes[2],retromat*prevaxes[2],


#        debug('count '+`count`+' image '+`singleimage`)
        for i in range(count):

            if (singleimage is not None): # Speed up Dissociate images processing
               if (singleimage >= count):
                  return [] # Nothing more to send back!
               else:
                  i = singleimage

            thisorigin = pathlist[i].origin

            if (self.dup["track"] or self.dup["elbow"]) and count>1:
                if i<count-1:
                    nextorigin = pathlist[i+1].origin
                    pathdist = nextorigin-thisorigin
                    #
                    # otherwise just use last pathdist
                    #
#                if self.dup["elbow"] and i==count-1:
#                   pathdist=pathlist[count-2].origin-pathlist[count-1].origin
                if self.dup["elbow"]:
                   pathdist = thisorigin-pathlist[i-1].origin
                if (pathlist[i]["level"] or self.dup["level"]) and not Vertical(pathdist):
                   prevaxes = MakeLevelAxes(pathdist.normalized)
                else:
                   prevaxes = NewAxes(prevaxes,pathdist.normalized)
                xax, yax, zax = prevaxes
                #
                # N.B. when the three args are vectors they are indeed
                #  input as columns.  Tuples otoh will go in as rows.
                #
                matrix = quarkx.matrix(xax,yax,zax)
            else:
                matrix=quarkx.matrix('1 0 0 0 1 0 0 0 1')

#                debug("  image %d; i %d"%(singleimage, i))

            list = templategroup.subitems[0].copy()
            if not (pathlist[i]["no instance"] or (self.dup["elbow"] and (i==0 or i==count-1))):
                list.translate(thisorigin)
                list.linear(thisorigin,matrix)
                if (singleimage is None) or (i==singleimage):
                    newobjs = newobjs + [list]
            else:
                #
                # This cruft is necessary because dissociate1click
                #  stops the image-generation process when an empty
                #  image is returned
                #
                dummy = quarkx.newobj('dummy:g')
                newobjs = newobjs + [dummy]
            del list
            if (i==singleimage): # Speed up Dissociate images processing
                break

        return newobjs


def macro_instances(self):
    editor=mapeditor()
    if editor is None: return
    dup = editor.layout.explorer.uniquesel
    if dup is None: return
    undo = quarkx.action()
    new=dup.copy()
    new.shortname = 'Elbow duplicator'
    new["macro"] = 'dup instance'
    new["elbow"] = "1"
    for item in new.subitems[:]:
        new.removeitem(item)
    new.translate(quarkx.vect(64, -64, 0))
    undo.put(dup.parent, new, dup)
    editor.ok(undo,"add elbows")
    editor.layout.explorer.uniquesel=new

quarkpy.qmacro.MACRO_instances = macro_instances



quarkpy.mapduplicator.DupCodes.update({
  "dup path":       PathDuplicator,
  "dup path_point": PathDuplicatorPoint,
  "dup instance":   InstanceDuplicator,
})


# ----------- REVISION HISTORY ------------
#$Log: mapdupspath.py,v $
#Revision 1.50  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.47  2002/08/04 11:49:24  decker_dk
#Fixed some code that would cause dissociate images to produce an incorrect result.
#Found by quantum_red in QuArK-forum date: 2002-07-30 subject: "Texture Alignment Problem".
#
#Revision 1.46  2001/10/22 10:15:48  tiglari
#live pointer hunt, revise icon loading
#
#Revision 1.45  2001/07/08 20:57:56  tiglari
#change treatment of vertical 'level' segments
#
#Revision 1.44  2001/07/08 08:34:31  tiglari
#reinstated elbow button for path dup; added 'level' spec for path dup and
#  instance (elbow) dup, fixed orientation bugs
#
#Revision 1.43  2001/06/17 21:10:57  tiglari
#fix button captions
#
#Revision 1.42  2001/06/13 22:27:19  tiglari
#fix instance dup bug
#
#Revision 1.41  2001/06/09 01:21:17  tiglari
#fix due north bug (noted by greeze)
#
#Revision 1.40  2001/05/12 23:04:38  tiglari
#make new linear fixpoint behavior contingent on 'item center' flag
#
#Revision 1.39  2001/05/06 10:22:10  tiglari
#remove buildLinearMatrix stuff from instance duplicator buildimages
#
#Revision 1.38  2001/04/08 02:43:10  tiglari
#if a group inside the instance duplicator has a usercenter, then the
# matrix/scale/rotate attributes of a path point will apply the transformations
# to that group, around the center.  'track rotations' otoh apply w.r.t. the
# usercenter attribute of the instance duplicator itself, to all of the
# subitems of the instance duplicator collectively.
#
#Revision 1.37  2001/04/02 21:11:27  tiglari
#added is None to conditional
#
#Revision 1.36  2001/04/01 00:09:36  tiglari
#usercenter for matrices on path points for instance duplicator
#
#Revision 1.35  2001/03/31 10:18:16  tiglari
#revise instance duplicator to use usercenter specific
#
#Revision 1.34  2001/03/29 09:28:55  tiglari
#scale and rotate specifics for duplicators
#
#Revision 1.33  2001/03/28 23:21:03  tiglari
#re-integrate instance dup stuff from  1.31, which somehow got dropped
#
#Revision 1.32  2001/03/28 12:22:49  tiglari
#fix square end problem (vertex shift function wrong)
#
#Revision 1.25  2001/03/18 23:54:09  tiglari
#experimental merge
#
#
#Revision 1.24  2001/03/17 22:04:53  tiglari
#dissociate images fix
#
#Revision 1.23  2001/03/12 23:10:27  tiglari
#path dup adding/positioning enhancements (does the work of the
# 'torus generator' suggested plugin, inter alia)
#
#Revision 1.22.2.2  2001/03/12 09:21:23  tiglari
#retarget of path points (basically for if a duplicator is used to produce
#a complex pattern such as a spiral))
#
#Revision 1.22.2.1  2001/03/11 22:09:48  tiglari
#position/add path points with set angles
#
#Revision 1.22  2001/03/08 06:23:26  tiglari
#menu item to select duplicator on path point handles
#
#Revision 1.21  2001/03/07 20:00:13  tiglari
#specific for rotation suppression
#
#Revision 1.20  2001/03/04 06:40:13  tiglari
#changed to use arbitrary axis matrix rot from maputils
#
#Revision 1.19  2001/02/27 07:08:02  tiglari
#center tiles along path segments
#
#Revision 1.18  2001/02/27 05:33:07  tiglari
#fixed storage problem (map object created in class definition)
#
#Revision 1.17  2001/02/26 03:26:40  tiglari
#handle ok method fix
#
#Revision 1.16  2001/02/26 02:07:21  tiglari
#all path point handles appear when main dup is selected
#
#Revision 1.15  2001/02/25 16:32:54  decker_dk
#Fix for objects that are supposed to be checked for None/Nil/Null pointer.
#
#Revision 1.14  2001/02/23 03:41:51  tiglari
#square end and setback
#
#Revision 1.13  2001/02/22 21:47:57  tiglari
#stuff in a Tile subitem of the duplicator (top level) will now be tiled
#
#Revision 1.12  2001/02/22 03:37:37  tiglari
#more spiffup, also code for calculating start and end of maximal nonoverlapping
#flat-end path segments
#
#Revision 1.10  2001/02/21 06:34:22  tiglari
#a bit of cleanup, some preliminaries for elbows and tiling
#
#Revision 1.9  2001/02/20 21:31:38  tiglari
#textures tile from start of path (still messes at elbows, this probably
# needs fullon elbow segments to deal with)
#
#Revision 1.8  2001/02/19 19:15:57  decker_dk
#Insert before/after actions now places new 'handle' at more intutive position, and aligned-to-grid.
#
#Revision 1.7  2001/02/11 09:46:52  tiglari
#evaluation of duplicators within template
#
#Revision 1.6  2001/02/09 10:49:07  tiglari
#fixed bug with no-angle path joints
#
#Revision 1.5  2001/02/08 10:44:27  tiglari
#Fixed problems with paths going up & down.
# Replaced subtraction code with end-face movement/distortion.
#
#Revision 1.4  2001/02/04 11:51:45  decker_dk
#Some cleanup
#
#Revision 1.3  2001/02/03 19:08:30  decker_dk
#Changed path-handles to ':d'-macros, so functions can be performed on them. Like adding new path-handles.
#
#Revision 1.2  2001/01/27 18:25:29  decker_dk
#Renamed 'TextureDef' -> 'DefaultTexture'
#
#Revision 1.1  2000/12/19 21:07:19  decker_dk
#Still a buggy Path Duplicator
#
#2000-??-?? Using point-entities as path-handles
#1999-02-10 First public beta.
#1999-01-23 Created.
