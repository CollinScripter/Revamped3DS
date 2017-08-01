"""   QuArK  -  Quake Army Knife

Map Editor Entities manager
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapentities.py,v 1.62 2011/10/06 20:13:37 danielpharos Exp $


import quarkx,sys,math

from maputils import *
import maphandles
import mapoptions
import qhandles



#py2.4 indicates upgrade change for python 2.4

#
# Classes that implement operations on all types of Map Objects,
# e.g. Quake entities, groups, brush entities, duplicators, etc.
# See the base class, EntityManager, for more information about
# the available methods.
#
# Note: there is a special trick with these classes.
# They are not supposed to be used to build instances from;
# instead, they are merely a convenient way to pack functions.
# These functions are NOT called with a first argument "self"
# which is an instance of the class. They are extracted from
# the class and called directly. The first argument is always
# the QuArK object that the operation applies to.
#
# Call them with CallManager().
#

def ObjectOrigin(o):
    "Returns the origin of the map object o, or the center of its bounding box."
    pos = o.origin
    if pos is None:
        #
        # The object has no "origin", let's compute its bounding box.
        #
        box = quarkx.boundingboxof([o])
        if box is None:
            return None
        pos = 0.5*(box[0]+box[1])
    return pos

#
# Entity Manager base class, followed by subclasses.
#

class EntityManager:
    "Base class for entity managers."

    #
    # All methods below are here to be overridden in subclasses.
    #

    def drawback(o, editor, view, mode):
        "Called to draw a background for the object 'o'."
        view.drawmap(o, mode)  # draw a dark background for "o"

    def drawsel(o, view, mode):
        "Called to draw the object 'o' selected."
        view.drawmap(o, mode)  # draw normally by default

    def handles(o, editor, view):
        "Build a list of handles related to this object."
        pos = ObjectOrigin(o)
        if pos is None:
            return []
        return [maphandles.CenterHandle(pos, o, MapColor("Tag"))]

    def applylinear(entity, matrix):
        "Apply a linear mapping on this object."
        pass

    def dataformname(o):
        "The name of the data form to use for the Specific/Args page."
        return "Default" + o.type

    def menu(o, editor):
        "A pop-up menu related to the object."
        import mapmenus
        return CallManager("menubegin", o, editor) + mapmenus.BaseMenu([o], editor)

    def menubegin(o, editor):
        return []


#
# A function to determine which Specifics in a Quake entity
# are to be considered as 2D or 3D angles.
#

# tbd : this should be configured in the game addon file !
def ListAngleSpecs(entity):
    h2D = maphandles.Angle2DHandle
    h3D = maphandles.Angles3DHandle
    if entity["light"] and entity["target"]:
        h = []    # ignore "angle" in light entities
    else:
        h = [("angle", h2D)]    # "angle" is 2D
    h.append(("angles", h3D))   # "angles" is 3D
    h.append(("mangle", h3D))   # "mangle" is 3D
    h.append(("movedir", h3D))   # HL2
    h.append(("gibdir", h3D))   # HL2 
    return h


#
# A function to determine which Specifics in a Quake entity
# are to be considered additional control points.
#

# tbd : this should be configured in the game addon file !
def ListAddPointSpecs(entity):
    "Called from maphandles CenterEntityHandle funciton"
    "to create extra Specifics setting handles"
    "for Half-Life 2 functions commented below."
    h=[]
    h.append("point0")   # HL2 ladder point
    h.append("point1")   # HL2 ladder point
    h.append("lowerleft")# HL2 breakable glass
    h.append("upperleft")# HL2 breakable glass
    h.append("lowerright")# HL2 breakable glass
    h.append("upperright")# HL2 breakable glass
    return h


def entitylinear(entity, matrix):
    #
    # If we rotate the entity, its angle Specifics must be updated.
    #
    for spec, cls in ListAngleSpecs(entity):
        s = entity[spec]
        if s:
            stov, vtos = cls.map
            try:
                normal = stov(s)
            except:
                continue
            normal = matrix * normal
            entity[spec] = vtos(normal)
            return



class EntityType(EntityManager):
    "Quake non-brush Entities"

    def handles(o, editor, view):
        return maphandles.CenterEntityHandle(o, view)

    applylinear = entitylinear

    def drawback(o, editor, view, mode):
        view.drawmap(o, mode)  # draw a dark background for "o"
        drawentitylines(editor, [o], view)

    def dataformname(o):
        return o.shortname

    def menubegin(o, editor):
        import mapmenus
        return mapmenus.EntityMenuPart([o], editor)



class DuplicatorType(EntityType):
    "Duplicators"

    def applylinear(entity, matrix):
        try:
            import mapduplicator
            mapduplicator.DupManager(entity).applylinear(matrix)
        except:
            pass

    def dataformname(o):
        import mapduplicator
        return mapduplicator.DupManager(o).dataformname()

    def handles(o, editor, view):
        import mapduplicator
        return mapduplicator.DupManager(o).handles(editor, view)


class GroupType(EntityManager):
    "QuArK groups"

    def handles(o, editor, view):
        pos = ObjectOrigin(o)
        if pos is None:
            return []
        h = [maphandles.CenterHandle(pos, o, MapColor("Tag"))]
        if o["usercenter"] is not None:
            h.append(maphandles.UserCenterHandle(o))
        return h

    def drawsel(o, view, mode):
        # draw group selected
        view.drawmap(o, mode | DM_SELECTED, view.setup.getint("SelGroupColor"))

    def menu(o, editor):

        def subspecs(m, group=o, editor=editor):
            editor.layout.explorer.sellist = group.subitems
            editor.layout.mpp.viewpage(1)

        import mapbtns
        Spec1 = qmenu.item("Common &specifics...", subspecs, "Specifics/Args of sub-items")
        Spec1.state = qmenu.default
        edit1 = qmenu.popup("Edit", EntityManager.menu.im_func(o, editor), hint="general editing functions")
        usercenter1 = qmenu.item("Add user center", qmacro.MACRO_usercenter, "User controlled pivot point for the group")
        usercenter1.state = (o["usercenter"] is not None) and qmenu.disabled
        GroupCol1 = qmenu.item("Group &color...", mapbtns.groupcolor, "the color to draw the group")
        GroupCol1.rev = 0
        RevertCol1 = qmenu.item("Back to &default color", mapbtns.groupcolor, "removes the special color")
        RevertCol1.rev = 1
        RevertCol1.state = not o["_color"] and qmenu.disabled
        import mapmenus
        return [Spec1, edit1, usercenter1, qmenu.sep, GroupCol1, RevertCol1, qmenu.sep] + mapmenus.ViewGroupMenu(editor)

    def menubegin(o, editor):
        import mapmenus
        import mapbtns
        Spec1 = qmenu.item("&Specifics of the group...", mapmenus.set_mpp_page, "Specifics/Args for the group")
        Spec1.page = 1
        Tex1 = qmenu.item("&Texture...", mapbtns.texturebrowser, "choose texture of all sub-items")
        return [Spec1, Tex1, qmenu.sep]



class BrushEntityType(EntityManager):
    "Quake Brush Entities"

    def drawsel(o, view, mode):
        # draw group selected
        view.drawmap(o, mode | DM_SELECTED, view.setup.getint("SelGroupColor"))

    def drawback(o, editor, view, mode):
        view.drawmap(o, mode)  # draw a dark background for "o"
        drawentitylines(editor, [o], view)

    applylinear = entitylinear

    def handles(o, editor, view):
        return maphandles.CenterEntityHandle(o, view, pos=ObjectOrigin(o))

    def dataformname(o):
        return o.shortname

    def menubegin(o, editor):
        import mapmenus
        return mapmenus.EntityMenuPart([o], editor)



def PolyHandles(o, exclude):
    "Makes a list of polyhedron handles, excluding the face 'exclude'."
    h = []
    pos = o.origin
    if not (pos is None):
        #
        # Vertex handles.
        #
        for v in o.vertices:
            h.append(maphandles.VertexHandle(v, o))
        #
        # Face handles.
        #
        for f in o.faces:
            if f!=exclude:
                #
                # Compute the center of the face.
                #
                vtx = f.verticesof(o)
                center = reduce(lambda x,y: x+y, vtx)/len(vtx)
                #
                # Create the handle at this point.
                #
                h.append(maphandles.PFaceHandle(center, f))
        #
        # Finally, add the polyhedron center handle.
        #
        h.append(maphandles.PolyHandle(pos, o))

    return h



class PolyhedronType(EntityManager):
    "Polyhedrons"

    def handles(o, editor, view):
        h = PolyHandles(o, None)
        if h:
            return h
        #
        # No handle... Maybe the inherited method has some handles to provide.
        #
        return EntityManager.handles.im_func(o, editor, view)

    def menubegin(o, editor):
        import mapmenus
        import mapbtns
        h = [ ]
        if editor.layout.mpp.n != 2:
            Spec1 = qmenu.item("&Polyhedron page...", mapmenus.set_mpp_page, "display polyhedron information")
            Spec1.page = 2
            Spec1.state = qmenu.default
            h.append(Spec1)
        Tex1 = qmenu.item("&Texture...", mapbtns.texturebrowser, "choose texture of polyhedron")
        return h + [Tex1] + mapmenus.MenuTexFlags(editor) + [qmenu.sep]

def line(u,p0,p1):
    "Used in drawdistnet function below to"
    "draw a face displacement net lines."
    f0=1-u
    res=quarkx.vect( p0.x*f0 + p1.x*u , p0.y*f0 + p1.y*u , p0.z*f0 + p1.z*u)
    return res

def drawdistnet(o,view): # NOTE: this function needs to handle the selected face like a bezier.
  "Makes a face displacement net for Half-Life 2"
  for vtx in o.vertices:
    pass
    #print 'vtx',vtx
  try:
    cp=[]
    if len(o.dists)!=0: # o.dists is causing the "grey views" problem, what is it suppose to be?
      #print "dists"
      delta=1.0/len(o.dists)
      #print delta
      u=delta/2.0
      for dists in o.dists:
        cc=[]
        cp.append(cc)
        pa=line(u,vtx[2],vtx[1])
        pb=line(u,vtx[3],vtx[0])
        #print u,pa,pb
        u=u+delta
        #print dists
        v=delta/2.0
        oldpointpos=pa
        for d in dists:
          p=line(v,pa,pb)
          #print u,v,p,d
          pointpos= d*o.normal+p               
          cc.append(pointpos)
          v=v+delta

      cp = map(lambda cpline, proj=view.proj: map(proj, cpline), cp)
      cv=view.canvas()
      for cpline in cp:
        for j in range(len(cpline)-1):
          cv.line(cpline[j], cpline[j+1])
      
      cp = apply(map, (None,)+tuple(cp))
      
      for cpline in cp:
        for i in range(len(cpline)-1):
            cv.line(cpline[i], cpline[i+1])

  except:
    exctype, value = sys.exc_info()[:2]
  #  print exctype, value
  
class FaceType(EntityManager):
    "Polyhedron Faces"

    def drawback(o, editor, view, mode):
        #
        # To draw the background of a face, we actually draw the whole polyhedron.
        #
        for src in o.faceof:
            view.drawmap(src, mode)
        ### Makes a face displacement net for Half-Life 2
  #      drawdistnet(o,view) # o.dists in this function is causing the problem

    def drawsel(o, view, mode):
        view.drawmap(o, mode | DM_SELECTED, view.setup.getint("SelFaceColor"))
        ### Makes a face displacement net for Half-Life 2
  #      drawdistnet(o,view) # o.dists in this function is causing the problem

    def handles(o, editor, view):
  #      print "mapentities line 344 FaceType o",o.name
  #      print "mapentities line 345 FaceType o.dictspec",o.dictspec
  #      print "mapentities line 346 FaceType o.subitems",o.subitems
  #      print "mapentities line 347 EntityType o.Origin",ObjectOrigin(o)
        #
        # Face handles
        #
        if view.viewmode == "tex":
            #
            # Cyan L handles are useful on textured views only.
            #
            h = maphandles.BuildCyanLHandles(editor, o)
        else:
            h = []
        #
        # Add handles from the polyhedron(s) that owns this face.
        #
        for p in o.faceof:
            if p.type==":p":
                h = h + PolyHandles(p, o)
        #
        # Add handles for the face itself - once per polyhedron that owns this face.
        #
        scale = view.scale()
        for vtx in o.vertices:
            #
            # vtx is a list of vertices. (o.vertices was a list of lists)
            # Compute the center of this face.
            #
            center = reduce(lambda x,y: x+y, vtx)/len(vtx)
            #
            # Make a handle at this point.
            #
            h1 = maphandles.FaceHandle(center, o)
            #
            # Make a "normal vector" handle araising from this point.
            #
            h2 = maphandles.FaceNormalHandle(center, vtx, o, scale)
            #
            # Add these new handles to the list.
            #
            h = h + [h2, h1]
 ### NEW SpecialHandle code start, only for Half-Life2 at this time.
 ### Used to create a Half-Life 2 face displacement. Activate by changing to "Half-Life2" below.
        if quarkx.setupsubset(SS_GAMES)['GameCfg'] == "Maybe Future Half-Life2":
            try:
              print "mapentities line 388 vtx"
              for vtx in o.vertices:
                 print vtx
                 print "mapentities line 391 o.name is ",o.name
                 print "mapentities line 392 took o"
        #1      if len(o.dists)!=0:
              if len(o.vertices)!=0:
                print "mapentities line 395 dists"
         #2       delta=1.0/len(o.dists)
                delta=1.0/len(o.vertices)
                print "mapentities line 398 delta is ",delta
                u=delta/2.0
         #3       for dists in o.dists:
                for dists in o.vertices:
                  pa=line(u,vtx[0],vtx[3])
                  pb=line(u,vtx[1],vtx[2])
                  print "mapentities line 404 u,pa,pb are "
                  print u
                  print pa
                  print pb
                  u=u+delta
                  print "mapentities line 409 u is ",u
                  v=delta/2.0
                  oldpointpos=pa
                  for d in dists:
                    p=line(v,pa,pb)
                    print "mapentities line 414 u,v,p,d are "
                    print u
                    print v
                    print p,type(p)
                    print d,type(d)
                    print "mapentities line 419 o.normal ",o.normal,type(o.normal)
              #4      pointpos= d*o.normal+p # just needs dif. method of doing this.

                    pointpos=o.normal+p
                    print "mapentities line 423 pointpos is ",pointpos
              #5      h=h+ [maphandles.SpecialHandle(pointpos,100)]
         #works           h=h+ [maphandles.SpecialHandle(pointpos,o)] # Use the one below
         # new test area
                    scale1 = 1.0
                    spec = "angles"
                    print "mapentities line 429 o.name",o.name
                    h=h+ [maphandles.SpecialHandle(pointpos,o.normal,scale1,o,spec)] # Use this one

                    v=v+delta
              else:
                  print "mapentities line 434 skipped len section"
            except:
              exctype, value = sys.exc_info()[:2]
              print "mapentities line 437 exctype, value",exctype, value
 ### NEW SpecialHandle code end, only for Half-Life2 at this time.
        return h

    def menu(o, editor):
        import mapmenus
        import mapbtns
        h = [ ]
        if editor.layout.mpp.n != 3:
            Spec1 = qmenu.item("&Face page...", mapmenus.set_mpp_page, "display face information")
            Spec1.page = 3
            Spec1.state = qmenu.default
            h.append(Spec1)
        Tex1 = qmenu.item("&Choose Texture...", mapbtns.texturebrowser, "choose texture for face")
        texpop = qmenu.popup("&Texture",[Tex1]+ mapmenus.MenuTexFlags(editor))
        texpop.label = 'texpop'
        import mapselection
        Cancel1 = qmenu.item("&Cancel Selections", mapselection.EscClick, "cancel all items selected")
        Force1 = qmenu.item("&Force center to grid", editor.ForceEverythingToGrid, "force to grid")
        Force1.state = not editor.gridstep and qmenu.disabled
        return h + [texpop, qmenu.sep, Cancel1, qmenu.sep, Force1]


#
# Maybe these functions should be shifted to mapbezier,
# with an empty menu set up here, and the functions added
# using the technique employed for project texture from
# tagged in mapbezier
#
class BezierType(EntityManager):
    "Bezier Patches"

    # tiglari
    def menubegin(o, editor):
        import mapmenus
        import mapbtns

        def swapclick(m, o=o, editor=editor):
            new = o.copy()
            new.swapsides();
            undo=quarkx.action()
            undo.exchange(o, new)
            editor.ok(undo, "Swap Sides")

        Tex1 = qmenu.item("Choose &Texture...", mapbtns.texturebrowser, "choose texture for patch")

        texpop = qmenu.popup("&Texture",[Tex1])
        texpop.label="texpop"
        swap = qmenu.item("&Swap sides",swapclick,"Flip visible side of patch")

        return [texpop, swap]

    # /tiglari

    def tex_handles(o, editor, view):
        import mapbezier
        #
        # Bezier handles : one per control point
        #
        colors = [[0xF00000, 0xD00000, 0xB00000, 0x900000, 0x700000],   #DECKER
                  [0x00F000, 0x00D000, 0x00B000, 0x009000, 0x007000],
                  [0x0000F0, 0x0000D0, 0x0000B0, 0x000090, 0x000070],
                  [0xF0F000, 0xD0D000, 0xB0B000, 0x909000, 0x707000],
                  [0x00F0F0, 0x00D0D0, 0x00B0B0, 0x009090, 0x007070],
                  [0xF000F0, 0xD000D0, 0xB000B0, 0x900090, 0x700070],
                  [0xF0F0F0, 0xD0D0D0, 0xB0B0B0, 0x909090, 0x707070]]
        coli = 0 #DECKER
        h = []
        cp = o.cp
        for i in range(len(cp)):
            colj = 0 #DECKER
            cpline = cp[i]
            for j in range(len(cpline)):
                c1 = cpline[j]
                # makes a list of couples (projected position, handle object)
                c1 = quarkx.vect(c1.s, c1.t, 0)
                h.append( mapbezier.CPTextureHandle(c1, o, (i,j), colors[coli][colj])) #DECKER
                colj = (colj+1)%4
            coli = (coli+1)%6

        return h


    def handles(o, editor, view):
        import mapbezier
        #
        # Bezier handles : one per control point
        #
        colors = [[0xF00000, 0xD00000, 0xB00000, 0x900000, 0x700000],   #DECKER
                  [0x00F000, 0x00D000, 0x00B000, 0x009000, 0x007000],
                  [0x0000F0, 0x0000D0, 0x0000B0, 0x000090, 0x000070],
                  [0xF0F000, 0xD0D000, 0xB0B000, 0x909000, 0x707000],
                  [0x00F0F0, 0x00D0D0, 0x00B0B0, 0x009090, 0x007070],
                  [0xF000F0, 0xD000D0, 0xB000B0, 0x900090, 0x700070],
                  [0xF0F0F0, 0xD0D0D0, 0xB0B0B0, 0x909090, 0x707070]]
        coli = 0 #DECKER
        h = []
        cp = o.cp
        for i in range(len(cp)):
            colj = 0 #DECKER
            cpline = cp[i]
            for j in range(len(cpline)):
                c1 = cpline[j]
                # makes a list of couples (projected position, handle object)
                h.append((view.proj(c1), mapbezier.CPHandle(c1, o, (i,j), colors[coli][colj]))) #DECKER
                colj = (colj+1)%4
            coli = (coli+1)%6

        h.sort()  # sort on Z-order, nearest first
        h.reverse()  # we have to draw back handles first, so reverse the order
        h = map(lambda x: x[1], h)  # extract the 2nd component of all couples (i.e., keep only handle objects)

        #
        # Add a center handle
        #
        try:
            # put the handle in the middle of the first square of control points
            pos = 0.25 * (cp[0][0]+cp[0][1]+cp[1][0]+cp[1][1])
        except IndexError:
            # there are not enough control points
            pos = o.origin
        if pos is not None:
            h.append(mapbezier.CenterHandle(pos, o))

        return h


#
# Mappings between Internal Objects types and Entity Manager classes.
#

Mapping = {
    ":d": DuplicatorType(),
    ":e": EntityType(),
    ":g": GroupType(),
    ":b": BrushEntityType(),
    ":p": PolyhedronType(),
    ":f": FaceType(),
    ":b2": BezierType() }

#
# Use the function below to call a method of the Entity Manager classes.
# Syntax is : CallManager("method", entity, arguments...)
#

def CallManager(fn, *args):
    "Calls a function suitable for the QuArK object given as second argument."
    try:
        mgr = Mapping[args[0].type]
    except KeyError:
        mgr = EntityManager()    # unknown type
    return apply(getattr(mgr, fn).im_func, args)  # call the function



#
# To Armin:
#   Change the existing 'def drawentitylines()' in quarkpy/mapentities.py, to all this.
#   Notice that there is a new setting; "EntityLinesDispersion". If its enabled, it can really increase the time QuArK/Windows
#    spends drawing graphics. (And it confuses me a bit, when I only wants to see what connections one entity has got).
#   Notice that here Arrow() now sends an extra argument, a text, so the Arrow() function should be modified to take this, but
#    does not need to do anything with it, yet!

def ParseCompoundVolume(CVString):

    nNumSpheres = 0

    iChar = 0
    while iChar < len(CVString) and CVString[iChar] != ' ':
        iChar = iChar + 1

    if iChar == len(CVString):
        return []

    nNumSpheres = int(CVString[:iChar])

    ParseList = []

    for iSphere in range(nNumSpheres):
        while iChar < len(CVString) and CVString[iChar] == ' ':
            iChar = iChar + 1

        if iChar == len(CVString):
            return []

        SphereInfoStart = iChar

        # X
        while iChar < len(CVString) and CVString[iChar] != ' ':
            iChar = iChar + 1

        if iChar == len(CVString):
            return []

        # Space
        while iChar < len(CVString) and CVString[iChar] == ' ':
            iChar = iChar + 1

        if iChar == len(CVString):
            return []

        # Y
        while iChar < len(CVString) and CVString[iChar] != ' ':
            iChar = iChar + 1

        if iChar == len(CVString):
            return []

        # Space
        while iChar < len(CVString) and CVString[iChar] == ' ':
            iChar = iChar + 1

        if iChar == len(CVString):
            return []

        # Z
        while iChar < len(CVString) and CVString[iChar] != ' ':
            iChar = iChar + 1

        if iChar == len(CVString):
            return []

        iSphereOrigin = quarkx.vect(CVString[SphereInfoStart:iChar])

        # Space
        while iChar < len(CVString) and CVString[iChar] == ' ':
            iChar = iChar + 1

        if iChar == len(CVString):
            return []

        # Radius
        SphereInfoStart = iChar
        while iChar < len(CVString) and CVString[iChar] != ' ':
            iChar = iChar + 1

        iSphereRadius = float(CVString[SphereInfoStart:iChar])

        ParseList = ParseList + [(iSphereOrigin, iSphereRadius)]

    return ParseList

class DefaultDrawEntityLines:

    def drawentityarrow(self, entity, org, backarrow, color, view, processentities, text=None):
        org2 = ObjectOrigin(entity)
        if org2 is not None:
            cv = view.canvas()
            cv.penwidth = mapoptions.getThinLineThickness()
            cv.pencolor = color
# DECKER - These font settings are commented out at the moment
#           cv.fontname =               # DECKER - Make this configurable
#           cv.fontcolor = color
#           cv.fontsize =               # DECKER - Make this configurable
            if backarrow:
                Arrow(cv, view, org2, org, text) # DECKER - When the Arrow() function can draw a text with it, we're ready for it
            else:
                Arrow(cv, view, org, org2, text) # DECKER - When the Arrow() function can draw a text with it, we're ready for it
            if MapOption("EntityLinesDispersion"): # DECKER - Make this switchable for the user!!!
                if not (entity in processentities):   # remove this to remove
                    processentities.append(entity)    #  recurrence in entity lines

    def drawentityarrows(self, spec, arg, org, backarrow, color, view, entities, processentities, text=None):
        for e in tuple(entities):
            if e[spec]==arg:
                self.drawentityarrow(e, org, backarrow, color, view, processentities, text)


############## SHINE support code start

    def drawAABB(self, mins, maxs, color, view):
        cv = view.canvas()
        cv.pencolor = color
# calculate aabb points
        aabb_010 = view.proj(quarkx.vect(mins.x, maxs.y, mins.z))
        aabb_110 = view.proj(quarkx.vect(maxs.x, maxs.y, mins.z))
        aabb_100 = view.proj(quarkx.vect(maxs.x, mins.y, mins.z))
        aabb_001 = view.proj(quarkx.vect(mins.x, mins.y, maxs.z))
        aabb_011 = view.proj(quarkx.vect(mins.x, maxs.y, maxs.z))
        aabb_101 = view.proj(quarkx.vect(maxs.x, mins.y, maxs.z))
        aabb_000 = view.proj(mins)
        aabb_111 = view.proj(maxs)

# draw low level
        cv.line(int(aabb_000.x), int(aabb_000.y), int(aabb_010.x), int(aabb_010.y))
        cv.line(int(aabb_110.x), int(aabb_110.y), int(aabb_010.x), int(aabb_010.y))
        cv.line(int(aabb_110.x), int(aabb_110.y), int(aabb_100.x), int(aabb_100.y))
        cv.line(int(aabb_000.x), int(aabb_000.y), int(aabb_100.x), int(aabb_100.y))
# draw high level
        cv.line(int(aabb_001.x), int(aabb_001.y), int(aabb_011.x), int(aabb_011.y))
        cv.line(int(aabb_111.x), int(aabb_111.y), int(aabb_011.x), int(aabb_011.y))
        cv.line(int(aabb_111.x), int(aabb_111.y), int(aabb_101.x), int(aabb_101.y))
        cv.line(int(aabb_001.x), int(aabb_001.y), int(aabb_101.x), int(aabb_101.y))
# draw medium level
        cv.line(int(aabb_000.x), int(aabb_000.y), int(aabb_001.x), int(aabb_001.y))
        cv.line(int(aabb_010.x), int(aabb_010.y), int(aabb_011.x), int(aabb_011.y))
        cv.line(int(aabb_110.x), int(aabb_110.y), int(aabb_111.x), int(aabb_111.y))
        cv.line(int(aabb_100.x), int(aabb_100.y), int(aabb_101.x), int(aabb_101.y))


    def drawonesphere(self, entity, sphereradius, org, OriginalOrigin, color, view):
        try:
            radius = sphereradius * view.scale(OriginalOrigin)
            radius = int(radius)   #py2.4
            cv = view.canvas()
            cv.pencolor = color
            cv.penwidth = 2
            cv.brushstyle = BS_CLEAR
            cv.ellipse(int(org.x)-radius, int(org.y)-radius, int(org.x)+radius, int(org.y)+radius)
        except:
            pass


    def drawentityradius(self, entity, nameradius, org, color, view):
        try:
            if entity[nameradius] is not None:
                radius = float(entity[nameradius]) * view.scale(org)
                radius = int(radius)   #py2.4
                cv = view.canvas()
                cv.pencolor = color
                cv.penwidth = 2
                cv.brushstyle = BS_CLEAR
                cv.ellipse(int(org.x)-radius, int(org.y)-radius, int(org.x)+radius, int(org.y)+radius)
        except:
            pass

############## SHINE support code end


    def drawentitylines(self, entity, org, view, entities, processentities):
        # "entity" and "processentities" is the current selected entity.
        # "entities" is a list of all other entities EXCLUDING the selected entity.

        color = MapColor("Axis")
        org1 = view.proj(org)
        if org1.visible:
            L1 = entity["light"]
            L2 = entity["_light"]
            # Rowdy: cdunde reported that Torque uses falloff1 (minimum radius) and falloff2
            #        (maximum radius) for lights, and does not have a 'light' specific
            L3 = entity["distance2"]
            L4 = entity["falloff2"]
            L5 = entity["spotlightlength"]
            if L1 or L2 or L3 or L4 or L5:
            # Rowdy: cdunde reported that Torque uses falloff1 (minimum radius) and falloff2
            #        (maximum radius) for lights, and does not have a 'light' specific
                try:
                    if L5:
                         radius = float(L5)
                         if entity["rendercolor"]:
                             try:
                                 color = vectorRGBcolor(quarkx.vect(entity["rendercolor"]))
                             except:
                                 pass
                    elif L1:
                        #### SHINE support code start
                        if entity["radius"] and quarkx.setupsubset(SS_GAMES)['GameCfg'] == "Shine":
                            try:
                                radius = float(entity["radius"])
                            except:
                                radius = float(L1)
                        #### SHINE support code end
                        else:
                            radius = float(L1)
                        if entity["_color"]:
                            try:
                                color = quakecolor(quarkx.vect(entity["_color"]))
                            except:
                                pass
                    elif L2:
                        L2 = readfloats(L2)
                        radius = L2[3]
                        color = makeRGBcolor(L2[0], L2[1], L2[2])
                    else:
                        if L3:
                            radius = float(L3)
                            if entity["color"]:
                                try:
                                    color = vectorRGBcolor(quarkx.vect(entity["color"]))
                                except:
                                    pass
                        else:
                            radius = float(L4)
                            if entity["color"]:
                                try:
                                    color = vectorRGBcolor(quarkx.vect(entity["color"]))
                                except:
                                    pass

                        #L3 = readfloats(L3)
                        #radius = L3[3]
                        #color = makeRGBcolor(L3[0], L3[1], L3[2])

                    lightfactor, = quarkx.setupsubset()["LightFactor"]

                    radius = radius * view.scale(org) * lightfactor
                    radius = int(radius)   #py2.4
                    cv = view.canvas()
                    if entity["rendercolor"]:
                        color = vectorRGBcolor(quarkx.vect(entity["rendercolor"]))
                        cv.pencolor = color
                    elif quarkx.setupsubset()["LightingOuterConeKeyword"] != "" and entity[quarkx.setupsubset()["LightingOuterConeKeyword"]]:
                        cv.pencolor = color + (color*.5)
                    else:
                        cv.pencolor = color
                    cv.penwidth = mapoptions.getThinLineThickness()
                    cv.brushstyle = BS_CLEAR

                    ### Section below draws the cone(s) for "light" spot entities.
                    if entity["target"] and entity["angles"] and entity["origin"]:
                        editor = mapeditor()
                        for e in tuple(entities):
                            if e["targetname"] == entity["target"] and e["origin"]:
                                u = 1
                                p0 = entity["origin"].split(" ")
                                p0 = quarkx.vect(float(p0[0]), float(p0[1]), float(p0[2]))
                                p1 = e["origin"].split(" ")
                                p1 = quarkx.vect(float(p1[0]), float(p1[1]), float(p1[2]))
                                # Line below converts single vector to "angles" specific values as a string.
                                netangles = qhandles.vec2angles(p1-p0)

                                if netangles != entity["angles"]:
                                    entity["angles"] = netangles
                                    entityform = editor.layout.dataform.linkedobjects[0] # A list of "dictspec" items, the Specifics and their Arguments.
                                    editor.layout.dataform.setdata(entityform, editor.layout.dataform.form)
                                    editor.buildhandles()

                    if entity["angles"] and ((quarkx.setupsubset()["LightingInnerConeKeyword"] != "" and entity[quarkx.setupsubset()["LightingInnerConeKeyword"]]) or (quarkx.setupsubset()["LightingOuterConeKeyword"] != "" and entity[quarkx.setupsubset()["LightingOuterConeKeyword"]])):
                        direct = quarkx.vect(entity["angles"])
                        # 'pitch' below for HL2 only.
                        if entity['pitch']:
                            entity['pitch'] = '%f' % - direct.x
                        ### Draws the outer cone lines.
                        if quarkx.setupsubset()["LightingOuterConeKeyword"] != "" and entity[quarkx.setupsubset()["LightingOuterConeKeyword"]]:
                            cone = float(entity[quarkx.setupsubset()["LightingOuterConeKeyword"]])
                            if not entity[quarkx.setupsubset()["LightingInnerConeKeyword"]]:
                                cv.pencolor = color
                        elif entity['spotlightwidth']:
                            cone = float(entity['spotlightwidth'])/2.0
                        try:
                            for i in range(18):
                                phi = i*2.0*3.14159/18
                                dirvectn=qhandles.angles2vec1(direct.x+cone*math.cos(phi),direct.y+cone*math.sin(phi),direct.z)
                                cv.line(view.proj(org+dirvectn*radius * lightfactor),org1)
                        except:
                            pass
                        ### Draws the inner cone lines.
                        if quarkx.setupsubset()["LightingInnerConeKeyword"] != "" and entity[quarkx.setupsubset()["LightingInnerConeKeyword"]]:
                            cone = float(entity[quarkx.setupsubset()["LightingInnerConeKeyword"]])
                            cv.pencolor = color
                            for i in range(9):
                                phi = i*2.0*3.14159/9
                                dirvectn = qhandles.angles2vec1(direct.x+cone*math.cos(phi),direct.y+cone*math.sin(phi),direct.z)
                                cv.line(view.proj(org+dirvectn*radius * lightfactor),org1)
                    ### Section above draws the cone(s) for "light" spot entities.
                    else:
                        ### Line below draws normal light full radius.
                        cv.ellipse(int(org1.x)-radius, int(org1.y)-radius, int(org1.x)+radius, int(org1.y)+radius)
                except:
                    pass
############ SHINE support code start
        if entity["pivot"] is not None and quarkx.setupsubset(SS_GAMES)['GameCfg'] == "Shine":
           self.drawentityarrows("pivotname", entity["pivot"], org, 1, RED, view, entities, processentities)
############ SHINE support code end
        if entity["combattarget"] is not None:  # X7: combattarget to targetname
           self.drawentityarrows("targetname", entity["combattarget"], org, 0, color, view, entities, processentities)
        if entity["deathtarget"] is not None:  # X7: deathtarget to targetname, color RED
           self.drawentityarrows("targetname", entity["deathtarget"], org, 0, RED, view, entities, processentities)
        if entity["killtarget"] is not None:
           self.drawentityarrows("targetname", entity["killtarget"], org, 0, RED, view, entities, processentities)
        if entity["name"] is not None:  
           # Rowdy: allow for Doom 3's target -> name instead of (and as well as) target -> targetname
           self.drawentityarrows("target", entity["name"], org, 1, color, view, entities, processentities)
        if entity["movewith"] is not None:  # X7: movewith to targetname, color GREEN
           self.drawentityarrows("targetname", entity["movewith"], org, 0, GREEN, view, entities, processentities)
        if entity["pathtarget"] is not None:  # X7: pathtarget to targetname
           self.drawentityarrows("targetname", entity["pathtarget"], org, 0, color, view, entities, processentities)
        if entity["target"] is not None:
           self.drawentityarrows("targetname", entity["target"], org, 0, color, view, entities, processentities)       
           self.drawentityarrows("name", entity["target"], org, 0, color, view, entities, processentities) # Rowdy: allow for Doom 3's
############ SHINE support code start
        if entity["Activator.Target"] is not None and quarkx.setupsubset(SS_GAMES)['GameCfg'] == "Shine":
           self.drawentityarrows("Trigger.TargetName", entity["Activator.Target"], org, 0, color, view, entities, processentities)
############ SHINE support code end
        if entity["targetname"] is not None:
           self.drawentityarrows("combattarget", entity["targetname"], org, 1, color, view, entities, processentities)
           self.drawentityarrows("deathtarget", entity["targetname"], org, 1, RED, view, entities, processentities)
           self.drawentityarrows("killtarget", entity["targetname"], org, 1, RED, view, entities, processentities)
           self.drawentityarrows("movewith", entity["targetname"], org, 1, GREEN, view, entities, processentities)
           self.drawentityarrows("pathtarget", entity["targetname"], org, 1, color, view, entities, processentities)
           self.drawentityarrows("target", entity["targetname"], org, 1, color, view, entities, processentities)
        if entity["team"] is not None:  #X7: team (Arg) for enities that use Team's, color Blue
           self.drawentityarrows("team", entity["team"], org, 0, BLUE, view, entities, processentities)
        if entity["team"] is not None:  #X7: team (Arg) for enities that use Team's, color Blue
           self.drawentityarrows("team", entity["team"], org, 1, BLUE, view, entities, processentities)
        if entity["dmgteam"] is not None:  #X7: dmgteam (Arg) for Q2 Lazarus Monsters enities, color Blue
           self.drawentityarrows("dmgteam", entity["dmgteam"], org, 0, BLUE, view, entities, processentities)
        if entity["dmgteam"] is not None:  #X7: dmgteam (Arg) for Q2 Lazarus Monsters enities, color Blue
           self.drawentityarrows("dmgteam", entity["dmgteam"], org, 1, BLUE, view, entities, processentities)
############ SHINE support code start
        if quarkx.setupsubset(SS_GAMES)['GameCfg'] == "Shine":
    #    pos = string.find(CVD, " ")
    #    if pos>-1:
    #          NV = CVD[:pos]
    #          debug(NV)
    #          i=0
    #          while i<NV:
    #            debug(i)
    #            i = i+1
            try:
                if entity["CollisionInfo.mins"] is not None:
                    if entity["CollisionInfo.maxs"] is not None:
                        mins = org + quarkx.vect(entity["CollisionInfo.mins"])
                        maxs = org + quarkx.vect(entity["CollisionInfo.maxs"])
                        self.drawAABB(mins, maxs, color, view)
            except:
                pass
                

            try:
                if entity["CollisionInfo.CompoundVolumeData"] is not None:
                    SpheresList = ParseCompoundVolume(entity["CollisionInfo.CompoundVolumeData"])
                    for Sphere in SpheresList:
                        SphereOrigin, SphereRadius = Sphere

                        ItemOrigin = quarkx.vect(entity["origin"])

                        szmangle = "0 0 0"
                        if entity["mangle"] is not None:
                            szmangle = entity["mangle"]

                        angles = quarkx.vect(szmangle)
                        pitch = -angles.x*deg2rad
                        yaw = angles.y*deg2rad
                        roll = angles.z*deg2rad

                        mat = matrix_rot_z(yaw)*matrix_rot_y(pitch)*matrix_rot_x(roll)

                        SphereOrigin = (mat*SphereOrigin)+ItemOrigin
                        self.drawonesphere(entity, SphereRadius, view.proj(SphereOrigin),SphereOrigin, color, view)
                else:
                    EntityForm = quarkx.getqctxlist(":form" , entity.shortname)
                    if EntityForm is not None and len(EntityForm) > 0:
                        EntityForm = EntityForm[-1]
                        for TestItem in EntityForm.subitems:
                            if TestItem.shortname == "CompVolInfo":
                                if TestItem["CVInfo"] is not None:
                                    SpheresList = ParseCompoundVolume(TestItem["CVInfo"])
                                    for Sphere in SpheresList:
                                        SphereOrigin, SphereRadius = Sphere

                                        ItemOrigin = quarkx.vect(entity["origin"])

                                        szmangle = "0 0 0"
                                        if entity["mangle"] is not None:
                                            szmangle = entity["mangle"]

                                        angles = quarkx.vect(szmangle)
                                        pitch = -angles.x*deg2rad
                                        yaw = angles.y*deg2rad
                                        roll = angles.z*deg2rad

                                        mat = matrix_rot_z(yaw)*matrix_rot_y(pitch)*matrix_rot_x(roll)

                                        SphereOrigin = (mat*SphereOrigin)+ItemOrigin
                                        self.drawonesphere(entity, SphereRadius, view.proj(SphereOrigin),SphereOrigin, color, view)
                                break;
            except:
                pass

            self.drawentityradius(entity, "CollisionInfo.radius", org1, color, view)
            self.drawentityradius(entity, "SkinMesh.VisibilityDistance", org1, color, view)
            self.drawentityradius(entity, "Shadow.VisibilityDistance", org1, color, view) 
            self.drawentityradius(entity, "BrushModel.VisibilityDistance", org1, color, view)
            self.drawentityradius(entity, "Shadow.MaxDistance", org1, color, view)

            self.drawentityradius(entity, "Sound.MinDistance", org1, BLUE, view)
            self.drawentityradius(entity, "Sound.MaxDistance", org1, RED, view)

            try:
                if entity.shortname == "NavPoint" and entity.parent is not None:
                    self.drawentityradius(entity, "Location.radius", org1, RED, view)
                    radius = float(entity["Location.radius"])
                    worldspawn = entity.parent
                    while worldspawn.shortname <> "worldspawn" and worldspawn.parent is not None:
                        worldspawn = worldspawn.parent
                    items = worldspawn.findallsubitems("NavPoint", ":e")
                    for item in items:
                        if item <> entity and item["origin"] is not None:
                            ItemOrigin = quarkx.vect(item["origin"])
                            ItemRadius = float(item["Location.radius"])
                            lenItem = abs(org - ItemOrigin)
                            if lenItem < 2*(radius + ItemRadius)+300.0:
                                OrgItem = view.proj(ItemOrigin)
                                drawcolor = color
                                if lenItem <= (radius + ItemRadius):
                                    drawcolor = YELLOW
                                self.drawentityradius(item, "Location.radius", OrgItem, drawcolor, view)
                else:
                    self.drawentityradius(entity, "Location.radius", org1, color, view)
            except:
                pass
############ SHINE support code end

#
# EntityLines Manager list
#
EntityLinesMapping = {
  "Default": DefaultDrawEntityLines()
}

def drawentitylines(editor, processentities, view):
    "According to the choosen game, draw additionnal lines and arrows (e.g. target to targetname)"
    entities = editor.AllEntities()
    try:
        mgr = EntityLinesMapping[quarkx.setupsubset().shortname] # DECKER - Find a drawentitylines-mgr for this game
    except KeyError:
        mgr = EntityLinesMapping["Default"] # DECKER - Hmm? Use the default manager, since there wasn't any plugin for the selected game
    i = 0
    while i<len(processentities):
        entity = processentities[i]
        i=i+1
        if entity in entities:
            entities.remove(entity)
        org = ObjectOrigin(entity)
        if org is None:
            continue
        mgr.drawentitylines(entity, org, view, entities, processentities) # DECKER - Call the manager


#
# Function to load the form corresponding to an entity list.
#

formdict = {}

def lookupPyForm(f1):
    if formdict.has_key(f1):
        return formdict[f1]

def registerPyForm(name, formstring):
    f = quarkx.newobj(name+":form")
    f.loadtext(formstring)
    formdict[name] = f

def LoadEntityForm(sl):  # Let's find all the objects (items) in sl (a list)
    formobj = f1 = None  # This will be our outputs
    if len(sl):  # Are there any objects in sl?
        f1 = CallManager("dataformname", sl[0])  # Gets the entity form-name (if one exist) of the first object
        for obj in sl[1:]:  # For all OTHER objects in sl...
            f2 = CallManager("dataformname", obj) # Get their names
            if f2!=f1: # If another one is found use it instead of the first one found
     #       if f2==f1: # If another one is found use the first one found anyway
                f1 = None  # Don't use f1's item, use f2's instead
                break # Stop checking we've already found a match
        if f1 is not None: # If a name has been found but no form yet, then go do the following
            #bbox = LoadPoolObj("BoundingBoxes", quarkx.getqctxlist, ":form")
            #for f in bbox:
            #    if f.shortname == f1:
            #        formobj = f        # find the LAST form
            flist = quarkx.getqctxlist(':form', f1) # Find the form for the f1 name is there is one
            if len(flist): # If a form is found then do the following
                formobj = flist[-1] # Set that :form data to be returned
        if formobj is None: # If the form data still has not been found then try the method below
            formobj = lookupPyForm(f1) # If found this time then set THAT :form data to be returned
    return formobj, f1 # Return both the formobj (can still be None) and the name for further testing
                       # (see "def filldataform" in mapmgr.py where call originated)


# ----------- REVISION HISTORY ------------
#$Log: mapentities.py,v $
#Revision 1.62  2011/10/06 20:13:37  danielpharos
#Removed a bunch of 'fixes for linux': Wine's fault (and a bit ours); let them fix it.
#
#Revision 1.61  2008/07/08 18:27:48  cdunde
#More new entity line drawing features by X7.
#
#Revision 1.60  2008/07/06 14:07:41  cdunde
#Added new entity line drawing features by X7.
#
#Revision 1.59  2008/05/23 05:26:55  cdunde
#To standardize and make game specific settings for spotlight cone line drawing.
#
#Revision 1.58  2008/05/21 18:14:56  cdunde
#To add and\or activate Half-Life 2 functions: (all original code by Alexander)
#1) to create extra Specifics setting handles for func_useableladder function (point0 & point1)
#      func_breakable_glass and func_breakable_surf functions
#      (lowerleft, upperleft, lowerright and upperright)
#2) to draw special light entity lines for functions like light_spot that have the Specifics
#      (angles, _cone, spotlightwidth and\or _inner_cone)
#3) face displacement. Commented out at this time. believe bezier type code should be used instead.
#
#Revision 1.57  2008/05/12 13:08:13  cdunde
#Fixed light radius not showing for other games due to game support for Shine changes.
#
#Revision 1.56  2007/12/24 21:33:58  cdunde
#Added Special entity cv.canvas() line drawing for Shine engine, may also be useful for other games.
#
#Revision 1.55  2007/12/14 21:48:00  cdunde
#Added many new beizer shapes and functions developed by our friends in Russia,
#the Shine team, Nazar and vodkins.
#
#Revision 1.54  2007/01/31 15:12:16  danielpharos
#Removed bogus OpenGL texture mode
#
#Revision 1.53  2006/12/13 03:17:46  cdunde
#Changed Specifics so multiple selections of the same entity can be set together.
#
#Revision 1.52  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.51  2006/11/29 07:00:27  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.50.2.1  2006/11/03 23:38:09  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.50  2006/08/25 20:20:22  cdunde
#To allow mutual selected items Specific setting changes.
#
#Revision 1.49  2006/08/21 03:14:06  cdunde
#Daniel (d.a.a.) and cdunde finally found fix for Access Violation errors
#with various selections of entities to display their form data.
#
#Revision 1.48  2006/01/30 08:20:00  cdunde
#To commit all files involved in project with Philippe C
#to allow QuArK to work better with Linux using Wine.
#
#Revision 1.47  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.44  2005/08/16 19:37:07  cdunde
#Needed to step back to v1.36 content to remove
#console unknowen entity error message.
#
#Revision 1.43  2005/08/13 04:54:08  cdunde
#Commented out, to reverse v1.42 entries causing views to go gray on poly face drag.
#
#Revision 1.42  2005/08/11 21:24:23  alexander
#displacement display and handles
#
#Revision 1.41  2005/08/04 20:40:27  alexander
#draw distance net for displacements
#
#Revision 1.40  2005/07/31 13:32:51  alexander
#halfed  spotlight beam width
#
#Revision 1.39  2005/07/31 13:20:54  alexander
#fixed spotlight color
#
#Revision 1.38  2005/07/31 13:16:11  alexander
#display also spotlight width and length
#
#Revision 1.37  2005/07/30 23:07:07  alexander
#cone showed for light spots and pitch value automatically set when seleting the entity
#showing height points for displacements
#target links shown for source engine
#
#Revision 1.36  2004/12/29 16:40:22  alexander
#introduced new PointSpecHandle which allows to have additional 3d control points on entities.
#which specifics are used for these points is controlled similar to the angle specific list
#
#Revision 1.35  2004/12/26 21:00:00  cdunde
#To remove file errors and dupe entries.
#
#Revision 1.34  2004/12/26 20:08:38  cdunde
#Added light Color-Picker function for Torque game engine.
#
#Revision 1.33  2004/12/26 02:32:35  rowdy
#modified DefaultDrawEntityLines.drawentitylines to draw trigger->func lines for Doom 3, where the func's 'name' specific is used instead of (or as well as) 'targetname'
#
#Revision 1.32  2004/12/23 11:25:09  rowdy
#Rowdy: added support for specific 'falloff2' which is used in Torque instead of the 'light' specific to indicate the (maximum) radius of a light entity (suggested by cdunde)
#
#Revision 1.31  2004/12/19 09:56:44  alexander
#movedir specific gets angle maphandle
#
#Revision 1.30  2003/03/23 07:31:18  tiglari
#make trigger-target line thickness configurable
#
#Revision 1.29  2003/02/13 15:56:53  cdunde
#To add Cancel Selections function to RMB menu.
#
#Revision 1.28  2001/08/16 20:09:29  decker_dk
#Put 'Add user center' menuitem on Treeview Group's context-menu. Its more visible there.
#
#Revision 1.27  2001/04/10 08:52:57  tiglari
#remove CustomObjectOrigin
#
#Revision 1.26  2001/03/31 13:01:35  tiglari
#usercenter for groups (for rotation)
#
#Revision 1.25  2001/03/22 08:14:31  tiglari
#origin duplicator bugfix
#
#Revision 1.24  2001/03/21 21:19:08  tiglari
#custom origin (center for groups) duplicator support
#
#Revision 1.23  2001/02/07 18:40:47  aiv
#bezier texture vertice page started.
#
#Revision 1.22  2001/01/10 20:25:53  tiglari
#fix bug in registerPyForm
#
#Revision 1.21  2000/12/31 02:46:02  tiglari
#Support for python code to add entity forms
# (for shape-generator development: lookup/registerPyForm)
#
#Revision 1.20  2000/07/29 02:06:35  tiglari
#my idea of how to do `hardcore' color coding
#
#Revision 1.19  2000/07/26 11:34:02  tiglari
#changes for bezier menu reorganizations
#
#Revision 1.18  2000/07/24 12:48:39  tiglari
#reorganization of bezier texture menu
#
#Revision 1.17  2000/07/24 09:09:23  tiglari
#Put Texture.. (choose) and Texture Flags into a submenu labelled 'texpop', for texture menu cleanup as suggested by Brian Audette
#
#Revision 1.16  2000/07/16 07:56:26  tiglari
#bezier menu -> menubegin
#
#Revision 1.15  2000/06/04 03:22:28  tiglari
#texture choice item for b2 menu
#
#Revision 1.14  2000/06/02 16:00:22  alexander
#added cvs headers
#
#Revision 1.13  2000/05/26 23:07:39  tiglari
#fiddled with beziertype entity manager
#
#Revision 1.12  2000/05/19 10:13:39  tiglari
#fixed `snap' in revision history at bottom
#
#Revision 1.11  2000/05/19 10:11:13  tiglari
#added revision history, comments on use of BezierType menu
#
#

