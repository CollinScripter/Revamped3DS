
########################################################
#
#               Side Tagging and Glueing Plugin
#                      v1.6, Aug 30, 1999
#                     works with Quark5.11
#
#
#        by tiglari@hexenworld.com, with lots of advice
#          code snippets and additions from Armin Rigo
#     
#
#   Possible extensions:
#    - button & floating toolbar as well as menu commands
#    - tracking of tagged sides that move
#   I'm not sure how useful either of these would really be, and
#   think there's other stuff that's a higher priority now.
#
#   You may freely distribute modified & extended versions of
#   this plugin as long as you give due credit to tiglari &
#   Armin Rigo. (It's free software, just like Quark itself.)
#
#   Please notify bugs & possible improvements to
#   tiglari@hexenworld.com
#  
#
##########################################################


#$Header: /cvsroot/quark/runtime/plugins/maptagside.py,v 1.44 2013/03/17 14:15:09 danielpharos Exp $


Info = {
   "plug-in":       "Side Tag & Glue",
   "desc":          "Side tagging and gluing to tagged side",
   "date":          "Aug 30, 1999",
   "author":        "tiglari",
   "author e-mail": "tiglari@hexenworld.com",
   "quark":         "Version 5.11" }

import quarkx
import quarkpy.mapmenus
import quarkpy.mapentities
import quarkpy.qmenu
import quarkpy.mapeditor
import quarkpy.qbaseeditor
import quarkpy.mapcommands
import quarkpy.mapoptions
import quarkpy.qhandles
import quarkpy.mapbtns
import mapsnapobject
import mergepolys
from quarkpy.maputils import *
from tagging import *
from faceutils import *

import maptagpoint

# A lot of recent code is piled up at the front.
#  All this needs to be broken up into separate files!!
#


def ToggleCheck(m):
  if m.state == qmenu.checked:
    m.state = qmenu.normal
  else:
    m.state = qmenu.checked

def toggleitem(text,hint):
  item = qmenu.item(text,ToggleCheck,hint)
  return item

#
# Texture multiple support (juggernaut's idea)
#

class MakeTexMultDlg(quarkpy.qmacro.dialogbox):

    #
    # dialog layout
    #

    size = (160, 75)
    dfsep = 0.6       # separation at 40% between labels and edit boxes
    dlgflags = FWF_KEEPFOCUS

    dlgdef = """
        {
        Style = "9"
        Caption = "Texture Wrapping Multiplier"

        mult: =
        {
        Txt = "Multiplier:"
        Typ = "EF1"
        Hint = "Enter how many times you want the"$0D" texture pattern repeated as it is wrapped."$0D"You can also use decimals like .5 for half."$0D"If you enter 0, the multiplier is not set"$0D" and will have no effect."
        }
        close:py = {Txt="" }
    }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, editor):

    #
    # General initialization of some local values
    #

        self.editor = editor
        self.sellist = self .editor .visualselection ()
        
        src = quarkx.newobj(":")
        src["mult"] = 0,
        editor.texmult = self
        self.src = src

    #
    # Create the dialog form and the buttons
    #

        quarkpy.qmacro.dialogbox.__init__(self, form, src,
        close = quarkpy.qtoolbar.button(
            self.close,
            "close this box",
            ico_editor, 0,
            "Close"))

    def onclose(self, dlg):
      requestmultiplier.state=qmenu.normal
      self.editor.texmult = None
      quarkpy.qmacro.dialogbox.onclose(self,dlg)
    

def WrapMultClick(m):
  editor = mapeditor()
  if editor is None: return
  if requestmultiplier.state==qmenu.checked:
 #    requestmultiplier.state=qmenu.normal
     editor.texmult.close()
  else:
    requestmultiplier.state=qmenu.checked
    MakeTexMultDlg(quarkx.clickform,editor)

requestmultiplier=qmenu.item("Texture Wrap Multiplier",WrapMultClick,"|When this item is checked, if you wrap a texture across a set of faces (around pillar or across tagged faces), the texture is scaled in the direction of fitting so as to fit as many times as specified in the dialog box.\n\nThe multiplier stays active until the dialog box is closed.  The 'preserve aspect ration' menu item controls whether the texture scales correspondingly in the other direction.")


#
#  snap object stuff, need to know how to get bbox info for this
#

def objectmenu(o, editor, oldmenu=quarkpy.mapentities.EntityManager.menu.im_func):
  menu = oldmenu(o,editor)
  menu [:0] = [snapobj(editor,o)]
  return menu

#quarkpy.mapentities.EntityManager.menu = objectmenu

def snapobj(editor,o):
  tagged=gettagged(editor)
  item=qmenu.item("Snap to tagged",SnapClick)
  if tagged is None:
    item.state=qmenu.disabled
  else:
    item.o = o   
  return item
  
def SnapClick(m):
   editor=mapeditor()
   if editor is None: return
   (vmin,vmax)=quarkx.boundingboxof([m.o])
   squawk("min: "+`vmin`+"  max: "+`vmax`)
   

#
# projecting textures onto faces
#

def projectpointtoplane2(point,along,origin,normal):
  "standard vector, normalized vector, origin v of plane, normal v to plane"  
  p1 = origin-point
  p1 = p1*normal
  p2 = along*normal
  p3 = p1/p2
  p4 = p3*along
  return point+p4
  
def projectpointtoplane(p,n1,o2,n2):
  "project point to plane at o2 with normal n2 along normal n1"
  v1 = o2-p
  v2 = v1*n2
  v3 = n1*n2

#  inserted this test to avoid error when trying to divide by 0.
  if v3 == 0:
      v4 = v2/1
  else:
      v4 = v2/v3

  v5 = v4*n1
  return p + v5

#  return p + (((o2-p)*n2)/n1*n2)*n1

#  return point+((origin-point)*normal/along*normal)*along
   

def projecttex(editor,o):
  item=qmenu.item("&Project tex. from tagged",ProjTexClick,"|Projects the texture of the tagged face onto the selected one, or those in the selected item, so that a texture can be wrapped without seams over an irregular assortment of faces.\n\nTextures aren't projected onto faces that are too close to perpendicular to the projecting face.")
  tagged=gettaggedtexplane(editor)
#  item.single = 0 # overrideable below, controls same-name check
  if tagged is None:
    item.state = qmenu.disabled
  elif o.type==":f" and math.fabs(tagged.normal*o.normal)<.001:
    item.state=qmenu.disabled
#    item.single = 1
  else:
    item.olist = [o]
    item.tagged=tagged
  return item
  
def ProjTexClick(m):
  editor = mapeditor()
  if editor is None: return
  undo = quarkx.action()
  bad = projectface(undo, m.tagged, m.olist)
  editor.ok(undo,"Project Texture")
  if bad:
    quarkx.msgbox("Some faces could not have the texture projected onto them",
      MT_WARNING,MB_OK)
  
def projectface(undo, tagged, olist):  
  list = []
  for o in olist:
    if o.type==":f":
      list.append(o)
    else:
      list = list + o.findallsubitems("",":f")
  undo = quarkx.action()
  normal = tagged.normal
  bad = 0
  for o in list:
    if math.fabs(tagged.normal*o.normal)<.001:
      bad = 1
    else:
     newface = projecttexfrom(tagged, o)
     undo.exchange(o, newface)


def projecttexfrom(source, goal):
  (o, t1, t2) = source.threepoints(1)
  along = source.normal
  (org, t3, t4) = goal.threepoints(1)
  norm = goal.normal
  (p, pt1, pt2) = (projectpointtoplane(o,along,org,norm),
                   projectpointtoplane(t1,along,org,norm),
                   projectpointtoplane(t2,along,org,norm))
  newface=goal.copy()
  newface.setthreepoints((p,pt1,pt2),1)
  newface.texturename=source.texturename
  if newface.normal*goal.normal<0:
     newface.swapsides()
#    (p1, p2, p3) = newface.threepoints(1)
#    squawk("swapping")
#    newface.setthreepoints((p1,-p2,-p3),1)
#  else: squawk("noswap")
  return newface

#
# experiment
#

def prepareobjecttodrop(editor,obj,oldprep=quarkpy.mapbtns.prepareobjecttodrop):
  objdict=getspecdict("_tag",obj)
  mapdict=getspecdict("_tag",editor.Root)
  if not (objdict=={} or mapdict=={}):
    objkeys=objdict.keys()
    mapkeys=mapdict.keys()
    objkeys.sort()
    mapkeys.sort()
    maxkey=mapkeys[-1]
    if objkeys[-1]>maxkey:
      maxkey=objkeys[-1]
    newkey=maxkey+1
    for tag in objdict.keys():
      if mapdict.has_key(tag):
        for thing in objdict[tag]:
          thing.setint("_tag",newkey)
      newkey=newkey+1
    objkeys = getspecdict("_tag",obj)
  oldprep(editor,obj)
 
quarkpy.mapbtns.prepareobjecttodrop = prepareobjecttodrop 

def new_ok(self, editor,undo,old,new,oldok=quarkpy.qhandles.GenericHandle.ok.im_func):
  codrug = codrag(editor,undo,old,new)
  if codrug >= 0:
    oldok(self,editor,undo,old,new)
  if codrug==1 and menmultisellinkdrag.state==qmenu.normal:
    editor.layout.explorer.sellist=new

quarkpy.qhandles.GenericHandle.ok = new_ok


def glueface(undo, face, target, exch=1):
    "moves face to the target position"
    if exch:
      newface = face.copy()
    else:
      newface = face
    if newface.normal*target.normal < 0:
      newface.distortion(-target.normal, face.origin)
    else:
      newface.distortion(target.normal, face.origin)
    newface.translate(newface.normal * \
        (newface.normal*target.origin - newface.dist))
    if exch:
      undo.exchange(face, newface)

def checkglue(dict):
  for key in dict.keys():
      face1 = dict[key][0]
      for face in dict[key][1:]:
        if not coplanar(face,face1):
          return 0
  return 1

def gluefaces(editor,undo,movee,tagdict):
  mapdict = getspecdict("_tag",editor.Root)
  for key in tagdict.keys():
    face1 = tagdict[key][0]
    faces = mapdict[key]
    for face in faces:
      if checktree(movee,face) or coplanar(face,face1):
        continue
      glueface(undo,face,face1)
 
def number(num,sing,pl):
  if (num==1):
    return sing
  else:
    return pl

def codrag(editor,undo,old,new):
  if len(old)>1: return 0
  old = old[0]
  new = new[0]
  type = old.type
  if not (type==":f" or type==":p" or type==":b" or type==":g"):
     return 0
  dragdict=getspecdict("_tag",new)
  if dragdict=={}: return 0
  if not checkglue(dragdict):
    quarkx.msgbox("The dragged "+typenames[type]+" contains linked faces that are not coplanar.\n\nYou should fix this and then use the 'Glue linked faces' speedmenu item to align the linked faces elsewhere in the map",
       MT_WARNING,MB_OK)
    return 0
  if mengluelinkedondrag.state==qmenu.normal:
    size = len(dragdict.keys())
    response = quarkx.msgbox("This object is linked to other faces.  Do you want to drag them too?",MT_INFORMATION,MB_YES_NO_CANCEL)
    if response == MR_NO:
      return 0
    if response == MR_CANCEL:
      return -1
  gluefaces(editor,undo,old,dragdict)
  return 1

  
menlinkonglue=toggleitem("Link on Glue","|Link on Glue:\n\nWhen this option is checked, the `Glue-to-tagged' command links the glued side to the tagged one, making it easy to keep them copanar.|intro.mapeditor.menu.html#optionsmenu")

menmultisellinkdrag=toggleitem("MultiSelect on Linked Drag","|MultiSelect on Linked Drag:\n\nWhen this option is checked, when a face is dragged that is linked to others, they all become the multi-selection after the drag.\n\nWhen it is unchecked, the selection remains unchanged.|intro.mapeditor.menu.html#optionsmenu")

#menmultisellinkdrag.state=qmenu.checked

mengluelinkedondrag=toggleitem("Silent Glue Linked on Drag","|Silent Glue Linked on Drag:\n\nWhen this option is checked, when something is dragged, faces linked to its faces will be dragged along too.|intro.mapeditor.menu.html#optionsmenu")

#mengluelinkedondrag.state=qmenu.checked

quarkpy.mapoptions.items.append(qmenu.sep)
quarkpy.mapoptions.items.append(menmultisellinkdrag)
quarkpy.mapoptions.items.append(menlinkonglue)
quarkpy.mapoptions.items.append(mengluelinkedondrag)


#
#---------------- An important exception -------------
#

bail = 'bail'

def check_true(whatever):
  "this device is used to exit from complicated sequences of tests"
  "  when one fails"
  if not whatever:
     raise bail, 0
  return whatever

#
# --------------- Some Geometry Utilities ---------
#

def intersection(l1, l2):
  "but not for points/vectors"
  return filter(lambda el, list=l2: list.count(el)>0, l1)

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
    
def colinear(list):
 "first 2 should not be coincident"
 if len(list) < 3:
   return 1
 norm = (list[1]-list[0]).normalized
 v0 = list[0]
 for v in list[2:]:
   if v0 - v:
 #    if not samelinenorm(line, (v0-v).normalized):
#     if norm-(v-v0).normalized:
     if abs(norm-(v-v0).normalized)>0.0001:
        return 0
 return 1

def abutting_vtx2(l1, l2):
  "gets the 2 vtx of l1 that are on the same line as 2 of l2, which are"
  "supposed to be vertex-cyles of abutting faces"
  "returns [i1, i2] list, index positions in l1, in cycle-order"
  "and ind is its index"
  (len1, len2) = (len(l1), len(l2))
  i1 = 0
  for v1 in l1:
    i = i1
    i1 = cyclenext(i1, len1)
    v1n = l1[i1]
    i2 = 0
    for v2 in l2:
      i2 = cyclenext(i2, len2)
      v2n = l2[i2]
      if colinear([v1, v1n, v2, v2n]):
        return [i, i1]
  return []
    
def samelinenorm(v1, v2):
  "v1 and v2 must be normalized"
  if math.fabs(v1* v2) == 1:
    return 1
  else:
    return 0

def abutting_face_vtx(vtxes1, vtxes2):
  "gets the 2 vertices shared by abutting faces, specified as lists"
  "of vertex-cyles, returns (vi1, vi2, ci), indN the indexes of"
  "vertices and then the cycle, in vtxes1"
  index = 0
  for vtx1 in vtxes1:
    for vtx2 in vtxes2:
      result = abutting_vtx2(vtx1, vtx2)
      if result:
        result.append(index)
        return result
    index = index+1
  return []
      
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
       
  
def oppositeedge(vtx, i, b):
  "returns (op1, op2, width) tuple, or 0, indexes of opposite vertices"
  "in cycle order, and a vector from first to the opposite edge's line."
  "i is the index of first vertex, b the normalized separation vector"
  "separation vector is second vertex minus first, in cycle-order"
  length = len(vtx)
#  squawk("i: "+`i`+"vtxes: "+`vtx`)
  first = cyclenext(i, length)
  start = vtx[i]
  while (first != i):
    second = cyclenext(first, length)
#    squawk("trying "+`vtx[first]`+":"+`vtx[second]`)
    sep = (vtx[second]-vtx[first]).normalized
#    squawk("normals: "+`b`+":"+`sep`)
    if not (sep + b):      # note that signs are opposite cuz of cycling
      return (first, second, perptonormthru(start,vtx[first],b))
    first = second
  return 0

  
def oppositeedge_vtxes(vtxes, abuttment):
  "does the work of oppositeedge, but taking a list of vertex-cycles"
  "and the output of abutting_face_vtx as inputs"
  cycle = vtxes[abuttment[2]]
  separ = (cycle[abuttment[1]]-cycle[abuttment[0]]).normalized
  return oppositeedge(cycle,abuttment[1],separ)
     

def index_vect(list, vect):
  "finds the index-position of a vector on a list of vectors"
  ind = 0
  for el  in list:
    if not (el-vect):
      return ind;
    ind = ind + 1
   
def coplanar_adjacent_sides(side1,side2):
  list = [side1]
  quarkx.extendcoplanar(list,[side2])
  if len(list) == 2:
    return 1
  else: return 0

def intersecting_sides(side1, side2):
  if math.fabs(side1.normal*side2.normal) < .99999:
     return 1
  else: return 0


#
# ----------- menu-management utilties ----------------
#

def gluemenuitem(String, ClickFunction,o, helptext='', infobaselink=''):
  "make a menu-item with a side attached"
  item = qmenu.item(String, ClickFunction, helptext,infobaselink=infobaselink)
  item.side = o
  return item



#
# ---------  misc utilities -----------
#

def squawk(msg):
  quarkx.msgbox(msg, MT_INFORMATION, MB_OK)

def isoneface(selections):
  return len(selections) == 1 and selections[0].type == ':f'

def sideof (m, editor):
  try:
    return m.side
  except (AttributeError) :
    tagged = editor.layout.explorer.sellist
    if not isoneface(tagged):
      return None
    #editor.visualselection()       #clears handle on tagged side(s)
    return tagged[0]



#
# old, zap this a few months after 041501
#
#def coplanar2(f1, f2):
#  (p1, p2, p3) = f1.threepoints(0)
#  (q1, q2, q3) = f2.threepoints(0)
#  n = f1.normal
#  if n*(q1-p1) == 0:
#    return 1
#  return 0
  
def drawlinks2(editor, view):
  "separated linked faces drawn dotted, in blue if selected otherwise red"
  dict = getspecdict("_tag", editor.Root)
  if dict is None: return
  keys = dict.keys()
#  quarkx.msgbox(`keys`,MT_INFORMATION,MB_OK)
  for key in keys:
    faces = dict[key]
    planes = [faces[0]]
    for face in faces[1:len(faces)]:
      for plane in planes:
        if coplanar(face,plane):
          break;
      else:
        planes.append(face)
    if len(planes)>1:
      cv = view.canvas()
      sellist = editor.layout.explorer.sellist
      if len(sellist) == 1 and sellist[0] in planes:
        cv.pencolor = MapColor("Duplicator")
      else:
        cv.pencolor = MapColor("Tag")
      cv.penstyle = PS_DOT
      #
      #  something's screwy here
      #
      for face in faces:
        drawredface(view,cv,face)
        
def getlinkedfaces(tag, allfaces):
  result = []
  for face in allfaces:
    if face.getint("_tag")==tag:
      result.append(face)
  return result


#
# makes a dict pairing the values of the tags on the faces
#  with 1 (meaning that they're relevant tags)
#
def startdict(faces):
  dict = {}
  for face in faces:
    if face.type==":f" and face.getint("_tag"):
      dict[face.getint("_tag")] = 1
  return dict

def drawlinks(editor, view):
  "if a linked face is selected, and some of the faces linked to it"
  "  are not coplanar, all are drawn in dotted red"

  dict =  startdict(editor.layout.explorer.sellist)
  if dict:
    #
    # We only want to do this once, and only if there is a
    #  tagged thing in the selection
    #
    allfaces = editor.Root.findallsubitems("",":f")
  cv = view.canvas()
  cv.pencolor = MapColor("Tag")
  cv.penstyle = PS_DOT
  for tag in dict.keys():
    faces = getlinkedfaces(tag, allfaces)
    planes = [faces[0]]
    for face in faces[1:len(faces)]:
      for plane in planes:
        if coplanar(face,plane):
          break;
      else:
        planes.append(face)
    if len(planes)>1:
      for face in faces:
        drawredface(view,cv,face)
    

def linkfinishdrawing(editor, view, oldmore=quarkpy.mapeditor.MapEditor.finishdrawing):
  "the new finishdrawning routine"
  drawlinks(editor, view)
  oldmore(editor, view)

quarkpy.mapeditor.MapEditor.finishdrawing = linkfinishdrawing


# -----------------------------------------------------
# ------------- tagging menu items --------------------
# -----------------------------------------------------

#
# ----------- tag & clear side & point  --------------------
#


def TagSideClick (m):
    "tags a face on mouse-click"
    editor = mapeditor()
    if editor is None: return
    try:
        sides = [m.side]
    except (AttributeError):
        sides = editor.layout.explorer.sellist
    if (len(sides) < 1):
        quarkx.msgbox("No selection has been made\n\nYou must first select\na face or vertex point to tag", MT_ERROR, MB_OK)
        return
    for side in sides:
        if (side.type != ":f"):
            quarkx.msgbox("Nothing has been done\n\nYou have selected a brush or multiple brushes\n\nYou need to select the face or vertex point\nof a single brush to be able to tag it", MT_ERROR, MB_OK)
            return
    tagface(sideof(m, editor), editor)


def ClearTagClick (m):
    "clears tag on menu-click"
    editor = mapeditor()
    if editor is None: return
    cleartag(editor)


#
# ------------- glueing & aligning sides & points ----------------
#


def GlueSideClick(m):
    "glues selection or current side handle to tagged side or point"
    editor = mapeditor()
    if editor is None: return
    try:
        sides = [m.side]
    except (AttributeError):
        sides = editor.layout.explorer.sellist
    if (len(sides) < 1):
        quarkx.msgbox("No selection has been made.\n\nYou must select and tag only one face or vertex point\nand then select another one to glue to the first one", MT_ERROR, MB_OK)
        return
    for side in sides:
        if (side.type != ":f"):
            quarkx.msgbox("The selected object is not\na face or vertex point", MT_ERROR, MB_OK)
            return
    tagged = gettaggedplane(editor)
    if tagged is None:
        tagpt = gettaggedpt(editor)
        if tagpt is None:
            quarkx.msgbox("Nothing done\n\nEither you have not tagged a face or vertex point\nor you have tagged more than one\n\nYou must first select and tag only one face or vertex point\nand then select another one to glue to the first one", MT_ERROR, MB_OK)
            return
    else:
        tagpt = tagged.origin
    editor.invalidateviews()
    gluit = 1
    ActionString = "glue to tagged"
    undo = quarkx.action()
    for side in sides:
        fulcrum = side.origin
        try:
            fulcrum = m.fulcrum
            gluit = 0
            ActionString = "Align to tagged"
        except (AttributeError) : pass
        new=side.copy()
        if tagged is not None:
            #
            # if necessary (it usually is), flip normal of new side
            #
            if new.normal*tagged.normal < 0:
              new.distortion(-tagged.normal, fulcrum)
            else: new.distortion(tagged.normal,side.origin)
        if gluit:
            #
            # force the translation vector to be parallel to the normal vector to avoid texture translation
            #
            new.translate(new.normal * (new.normal*tagpt - new.dist))
    undo.exchange(side, new)
    editor.layout.explorer.sellist = []
    editor.ok(undo, ActionString)
    if gluit and menlinkonglue.state==qmenu.checked:
        if quarkx.msgbox("Link glued face?",MT_CONFIRMATION,MB_YES|MB_NO)==MR_YES:
            m.side=new
            LinkFaceClick(m,0)

#
# -------------- Managing Tagged List --------------
#


def removefromtaggedstate(menuitem, editor, o):
  "in charge of disabling remove from tagged menu item"
  tagged = gettagged(editor)
  if not tagged is None:
    if tagged == o:
       return
  else:
    taglist = gettaggedlist(editor)
    if not taglist is None:
      count = taglist.count(o)
      if count:
        return
  menuitem.state = qmenu.disabled

def AddtoTaggedClick(m):
  "expects the selected face to be attached to m as .side"
  editor = mapeditor()
  if editor is None: return
  taglist = gettaggedlist(editor)
  side = editor.layout.explorer.uniquesel
  if side is not None:
    addtotaggedfaces(side, editor)

def RemovefromTaggedClick(m):
  "expects the selected face to be attached to m as .side"
  editor = mapeditor()
  if editor is None: return
  removefromtaggedfaces(m.side, editor)

def SelectTaggedClick(m):
  "expects .taglist to be attached to m"
  editor = mapeditor()
  if editor is None:
    return
  ClearTagClick(None)
  try:
    editor.layout.explorer.sellist = m.taglist
  except (AttributeError):
    pass


#
# ------ Wrapping texture from one face to another
#  (no fitting, this one also works in lots of cases where it's
#   probably useless, such as faces that don't abutt, but whose
#   planes intersect)
#

def aligntexstate(aligntex, tagged, o):
  "sorts out what kind of abuttment, if any for tagged side and this one"
  if tagged is None or o is tagged or tagged.treeparent is None:
     aligntex.state = qmenu.disabled
     return
#  if coplanar_adjacent_sides(tagged, o):
  if abs(tagged.normal*o.normal)>.999999:  # they are almost parallel
    aligntex.abuttype = 0
  elif intersecting_sides(tagged, o):
    aligntex.abuttype = 1
  else:
    aligntex.state = qmenu.disabled


def wraptex(orig, side):
    "actually wraps the texture from orig to side"
    "assumes aligntexstate has checked the preconditions"
    #
    # Find a point where the two sides intersect.
    #
    (o, t1, t2) = orig.threepoints(0)
    (r, s1, s2) = side.threepoints(0)
    n = side.normal
    if n*(t1-o) != 0:
#      quarkx.msgbox("t1 is OK",MT_INFORMATION, MB_OK)
      t = t1
    else:
#      quarkx.msgbox("t2 is hopefully OK",MT_INFORMATION, MB_OK)
      t = t2

#  inserted this test to avoid error when trying to divide by 0.
    if (n*(t-o)) == 0:
        l = -(n*(o-r))/1
    else:
        l = -(n*(o-r))/(n*(t-o))

    p = l*(t-o)+o
    if n*(p-r) > .000001:
      squawk("Sorry, something's not right here, I can't do this")
      return
    #
    # Now make the new side
    #
    newside = side.copy()
    newside.texturename = orig.texturename
    #
    # Orient the new side paralell to the original
    #
    newside.setthreepoints((o, t1, t2,), 0)
    #
    # Now make sure texture orientation is right
    #
    newside.setthreepoints(orig.threepoints(1),3) 
    #
    #  Swing the new side into position
    #
    newside.distortion(side.normal,p)
    #
    # check orientation
    #
    return newside


def MirrorFlipTexClick(m):
    editor = mapeditor()
    if editor is None: return
    side = editor.layout.explorer.uniquesel
    try:
        sides = [m.side]
    except (AttributeError):
        sides = editor.layout.explorer.sellist
    if (len(sides) < 1):
        quarkx.msgbox("No selection has been made\n\nYou must first select a single face\nof a single brush to flip its texture", MT_ERROR, MB_OK)
        return
    for side in sides:
        if (side.type != ":f"):
            quarkx.msgbox("You have selected a brush or multiple brushes\n\nYou need to select a single face of a\nsingle brush to be able to flip its texture", MT_ERROR, MB_OK)
            return
    #
    # this seems like an awkward technique, & I'd sort of
    #  like to dispense with the swapsides_leavetex() method,
    #  but I can't get anything else to work, and maybe
    #  this method is a slight speed optimization anyway,
    #  for invisible walls of some of the duplicators.
    #
    newside=side.copy()
    newside.swapsides_leavetex()
    newside=projecttexfrom(side,newside)
    newside.swapsides_leavetex()
    undo=quarkx.action()
    undo.exchange(side, newside)
    editor.ok(undo,"mirror flip texture")


def AlignTexClick(m):
  "wraps texture from tagged to selected side"
  "uses wraptex to do the real work"
  editor = mapeditor()
  if editor is None: return
  side = editor.layout.explorer.uniquesel
  tagged = gettaggedplane(editor)

  if side is None:
    quarkx.msgbox("Either no selection has been made or\nyou have selected more than one face\n\nYou must select and tag only one face of a\nbrush and then select another one to wrap to", MT_ERROR, MB_OK)
    return
  if tagged is None:
    quarkx.msgbox("Nothing done\n\nEither you have not tagged a face\nor you have tagged more than one\n(if so, all tags will be removed)\n\nYou must first select and tag only one face\nand then select another one to wrap to", MT_ERROR, MB_OK)
    cleartag(editor)
    return
  if side == tagged:
    quarkx.msgbox("Nothing done\n\nYou have selected the tagged face\nSelect another face to wrap to", MT_ERROR, MB_OK)
    return

  tagged = gettagged(editor)
  try:
      if m.mirror:
          tagged=tagged.copy()
          tagged.swapsides()
# version needed with wrong swapsides (not equiv to 63c)
#          tagged2=tagged.copy()
#          tagged2.swapsides()
#          tagged = projecttexfrom(tagged, tagged2)
  except:  pass
  try:
      abutt = m.abuttype
  except (AttributeError):
      aligntexstate(m, tagged, side)
  
  editor.invalidateviews()
  ActionString = "wrap texture from tagged"
  undo = quarkx.action()
#  debug('what abut')
  if m.abuttype == 1:
    side2=side.copy()
    if tomirroritem.state==qmenu.checked:
       side2.swapsides()   
    newside = wraptex(tagged, side2)
    if tomirroritem.state==qmenu.checked:
       newside.swapsides()   
  else:
#    debug('abut 0')
    newside=side.copy()
    if tomirroritem.state==qmenu.checked:
       newside.swapsides()   
    newside = projecttexfrom(tagged, newside)
    if tomirroritem.state==qmenu.checked:
       newside.swapsides()   
      
  undo.exchange(side, newside)
  editor.ok(undo, ActionString)
  if checkshifttagged.state == qmenu.checked:
    m.side = newside
    TagSideClick(m)


#
# ---------- wrapping & fitting texture around pillar
#

def pillarwrapdisabler(menuitem, tagged, o):
  "figures out if wrapping can procede from tagged to selected and"
  "so-on around poly, attaching useful info to m on successful return"
  #
  # the faces belong to polys
  #
  selpolys = o.faceof
  tagpolys = tagged.faceof
  #
  # using a defined exception as a bailout go-to
  #
  bail = 'bail'
  try:
    if tagpolys[0].type != ":p" or selpolys[0].type != ":p":
      raise bail, 0
    #
    # and indeed to the same poly
    #
    thepolys = intersection(tagpolys, selpolys)
    if thepolys == []:
      raise bail, 0
    thepoly = thepolys[0]  # I hope this assumption isn't unsound
    #
    # and indeed that these faces furthermore abutt
    #
    ovx = o.verticesof(thepoly)
    tvx = tagged.verticesof(thepoly)
    #
    # the order to abutting vtx matters, since returned list of tuples
    #  provides index in first arg as second member of the tuples
    #
    shared = abutting_vtx(ovx, tvx)
    if not shared:
      raise bail, 0
    sep = (shared[1][0]-shared[0][0]).normalized
    result = oppositeedge(ovx, shared[0][1], sep)
    if not result:
      raise bail, 0
    (first, second, gap) = result
    #
    # Now we embark on a voyage of discovery around the poly,
    # looking for a face that shares 2 vertices with our selected
    # face, such that these 2 vertices make an edge paralell to sep,
    # and so on around, till we get back to the originally selected
    # tagged face.  If at any prior time we fail, we bail, but if
    # we emerge successful, we attach to the menu-item a list of faces
    # for wrapping, the length of the path around, and the `gap' vector
    # of the tagged side (for figuring out how to rescale the texture)
    #
    polyfaces = thepoly.faces
#    squawk(`len(polyfaces)`)
    polyfaces.remove(tagged)
    polyfaces.remove(o)
#    squawk(`len(polyfaces)`)
    facelist = [tagged, o]
    circuitlength = abs(gap)
    ovtxes = [ovx[first], ovx[second]]
    def findnextface(polyfaces, thepoly, ovtxes):
        "defined here to reduce variable binding"
        for face in polyfaces:
          vtxes = face.verticesof(thepoly)
          int = abutting_vtx(vtxes, ovtxes)
          if len(int) == 2:
            polyfaces.remove(face)
            return (face, vtxes, int)
        return 0
    while 1:
      facial = findnextface(polyfaces, thepoly, ovtxes)
      #
      #  mebbe we found a next face
      #
      if facial:
         (face, nvtxes, shared) = facial
         result = oppositeedge(nvtxes, shared[0][1], sep)
         if not result:
           raise bail, 0
         (first, second, gap) = result
         facelist.append(face)
         circuitlength = circuitlength + abs(gap)
         ovtxes = [nvtxes[first], nvtxes[second]]     
         continue
      #
      # but if we didn't, mebbe that's cuz we're all the way around!
      #
      else:
        int = abutting_vtx(tvx, ovtxes)
        if len(int) == 2:
          result = oppositeedge(tvx, int[0][1], sep)
          if result:
            (first, second, gap) = result
            circuitlength = circuitlength + abs(gap)
            menuitem.wraplist = facelist
            menuitem.circuit = circuitlength
            menuitem.horiz = gap
#            squawk("faces: "+`len(facelist)`)
            return
      raise bail, 0
  #
  # and the final bailout go-to
  #

  except bail, dummy:
    menuitem.state = qmenu.disabled
    return 0
  
def PillarWrapClick(m):
  "expects m to have fields:"
  "  .wraplist - sequential list of faces for wraparound"
  "  .circuit - total circuitlength"
  "  .horiz - vector from one side of tagged face to the other"
  "all preconditions should be satisfied if menuitem enabled"
  
  (faces, circuit, gap) = (m.wraplist, m.circuit, m.horiz)
  editor = mapeditor()
  if requestmultiplier.state == qmenu.checked:
    multiplier, = editor.texmult.src["mult"]
  else:
    multiplier = 0

  firstface = faces[0]
  #
  # First figure out how to scale the texture
  #
  txsrc=editor.TexSource
  tp = firstface.threepoints(2, txsrc)
  gapn = gap.normalized
  # projection of texture scale vectors onto prism cap
  axlengths = (abs(tp[1]-tp[0]), abs(tp[2]-tp[0]))
  normal = ((tp[1]-tp[0]).normalized, (tp[2]-tp[0]).normalized)
  proj = (math.fabs((tp[1]-tp[0]).normalized*gapn), math.fabs((tp[2]-tp[0]).normalized*gapn))
  if proj[0] > proj[1]:
    primaxis = 0
  else:
    primaxis = 1
  projlength = axlengths[primaxis]*proj[primaxis]
  if multiplier:
    times = multiplier
  else:
    times = circuit/projlength
  repeat = math.floor(times)
  if times - repeat > .5:
    repeat = repeat + 1
  #squawk("t="+`times`+"; r="+`repeat`)
  #
  # replength is the desired length of projection of the
  #  chosen texture axis onto the capping face
  #
  replength = circuit/repeat
  stretch = replength/axlengths[primaxis]
#  squawk("stretch = "+`stretch`)
  stretched = ((tp[1]-tp[0])*stretch, (tp[2]-tp[0])*stretch)
  newaxes = [tp[1], tp[2]]
  secaxis = 1 - primaxis
  newaxes[primaxis] = tp[0]+stretched[primaxis]
  if checkaspectratio.state == qmenu.checked:
#    squawk("preserving aspect")
    newaxes[secaxis] = tp[0]+stretched[secaxis]
#  newaxes = (tp[0]+stretched[0], tp[0]+stretched[1])
  newface = firstface.copy()
  newface.setthreepoints((tp[0], newaxes[0], newaxes[1]),2,txsrc)
  ActionString = "pillar wrap"
  undo = quarkx.action()
  #
  # swap in the resized texture  
  #
  undo.exchange(firstface, newface)
  startface = newface
  #
  # and now at last for the big wrap
  #
  faces.remove(firstface)
  for face in faces:
    currface = newface  
    newface = wraptex(currface, face)
    undo.exchange(face, newface)
  editor.ok(undo, ActionString)
  editor.layout.explorer.sellist = [startface]

#
#  --- wrapping and fitting across chain of tagged sides
#

def wraptaggedstate(menuitem, o):
   "figures out if wrap & fit can happen across the tagged list of sides,"
   "starting from the current one, and proceding either from edge, or if"
   "the current one is in a cycle, in the direction the list was formed."
   "attaching useful info to menuitem on successful return, including"
   "list of faces in wrap order, & total length to fit"

   editor = mapeditor()
   if editor is None:
      return
   taglist = gettaggedlist(editor)
#   bail = 'bail'
   try:  # raise the bail exception to quit the sequence tests
     if taglist is None:
        raise bail, 0
     #
     # the current side must be in the tagged list
     #  (actaully, on an end or in a cycle!) 
     #
     taglist = taglist[:]      #make a copy
     if taglist.count(o) == 0:
        raise bail, 0
     pozzie = taglist.index(o)
     #
     #  Figure out which direction to go in building the wrap list.
     #  At an edge, go in the only possible direction.  In the middle,
     #  it's only possible if there's a circuit.  In this case, go in
     #  the direction of the abutting (tagged) face with the higher
     #  index, or with a zero index, or who cares.  If you can't use
     #  everything on the taglist, then the menu-item shouldn't get
     #  enabled.
     #
     #  So first find the face(s) that abutt with o.
     #
     tagind = taglist.index(o) # we'll need this shortly
     taglist.remove(o)
     ovtxes = o.vertices  # this is a vertex list, no info about polys
     faces = []
     abuttments = []
     for face in taglist:
        abuttment = abutting_face_vtx(ovtxes, face.vertices)
#        squawk("abuttment = "+`abuttment`)
        #
        # If successful, abuttment[0] will be a list [v1i, v2i, ci]
        #  the indexes from ovtexes that are shared with face.vertices,
        #  ci the index of vertex-cycle they're from
        #
        if abuttment:
          faces.append(face)
          abuttments.append(abuttment)
     if len(faces) > 2 or len(faces) == 0:
       raise bail, 0  #  wrong number, no proper abuttment
     if len(faces) == 2:
       #
       # Now we pick one, hopefully one that was tagged after o
       #
       (ind1, ind2) = (taglist.index(faces[0]), taglist.index(faces[1]))
#       squawk("index: "+`index`)
       if ind1 >= tagind:
         index = 0
       elif ind2 >= tagind:
         index = 1
       elif ind1 == 0:
         index = 0
       else:
         index = 1
     else:
       index = 0
     nextface = faces[index]
     (vi1, vi2, ci) = abuttments[index]
     #
     # Now we check that both o and nextface have an edge parellel
     #  to their shared edge, and get the distance between these
     #  edges.
     #
#    squawk("banzai")     
     vertical = (ovtxes[ci][vi2]-ovtxes[ci][vi1]).normalized
     (opi1, opi2, width) =  check_true(oppositeedge(ovtxes[ci], vi1, vertical)) 
     #
     # record the `horizontal' vector going from one side of the face
     #  to the other
     #
     horiz = width
     #
     # Now find out how to shift the origin of the texture threepoints
     #
     (p0, p1, p2) = o.threepoints(2)
     texorigshift = perptonormthru(p0, ovtxes[ci][vi1], vertical)
     #
#     squawk("passed 1")
     #
     # annoying to have to do this again, but such is life
     #   or perhaps I'm a moron
     #
     circuit = abs(width)
     current = faces[index]
     nvtxes = current.vertices
     (vi1, vi2, ci) = abutting_face_vtx(nvtxes, ovtxes)
#     squawk("passed 2")
     #
     # Note the sign-switch, cuz oppositeedge is very lazy
     #
     vertical = -vertical
     (opi1, opi2, width) = check_true(oppositeedge(nvtxes[ci], vi1, vertical))
#     squawk("passed 3")
     circuit = circuit + abs(width)   
     taglist.remove(current)
     wraplist = [o, current]
     #
     # Now repeat finding one face that extends the wall we've got
     #   so far. If every face gets used, sucess, otherwise bail.
     #
     while taglist:
#       squawk("taglen: "+`len(taglist)`)
       for face in taglist[:]:
         abuttment = abutting_face_vtx(face.vertices, nvtxes)
         if abuttment:
#           squawk("abutted")
           nvtxes = face.vertices
           (vi1, vi2, ci) = abuttment
           (opi1, opi2, width) = check_true(oppositeedge(nvtxes[ci], vi1, vertical))
#           squawk("checked out")
           circuit = circuit + abs(width)
           taglist.remove(face)
           wraplist.append(face)
           break
       #
       # OK we've looked at every that's left, & none of them
       #  latch onto what we've got, so bail
       #
       else:
         raise bail, 0    
#     squawk("length: "+`len(wraplist)`)
     menuitem.wraplist = wraplist
     menuitem.circuit = circuit
     menuitem.horiz = horiz
     menuitem.texorigshift = texorigshift
   except bail, dummy:
     menuitem.state = qmenu.disabled
     return


def nextface(v1, v2, faces):
       "test routine"
       for face in faces:
         vtxes = face.vertices
         vxi=0
         for vtx in vtxes:
           vi = 0
           for v in vtx:
             if not v-v1:
               vni = cyclenext(vi, len(vtx))
               if not vtx[vni]-v2:
                 return (vi, vni,vxi, face)
             vi = vi+1
           xvi = vxi+1
         squawk("bailing")
         return None

def TaggedWrapClick(m):
  editor = mapeditor()
  side = m.wraplist[0]
  (p1, p2, p3) = side.threepoints(2)
  shift = m.texorigshift
  side.setthreepoints((p1+shift, p2+shift, p3+shift), 2)
  PillarWrapClick(m)




# -----------------------------------------------------
# --------------  Set up Menus  -----------------------
#
#  (no real organization here yet!)
#
# Right Mouse menus are built `on the click' so that their items can
#  contain info about the object they are clicked over, and also
#  info prepared by their disablers (which do quite a lot of the work
#  for the texture-fitting operations)
#

tagtext = "|Tag side:\n\n`Tags' a side for reference in later operations of positioning and alignment.\n\nThe tagged side then appears in red.|intro.mapeditor.menu.html#commandsmenu"

gluetext = "Moves & aligns this side to the tagged one"
gluepttext = "Moves this side to the tagged point"

aligntext = "|Wrap texture from tagged:\n\nCopies the texture from the tagged face to this one, wrapping around a shared edge with proper alignment.\n\nThis is only really supposed work when the faces abutt at an edge, although it sometimes works more generally.|intro.mapeditor.menu.html#commandsmenu"
mirroraligntext = "|Like aligntex, but wraps from a mirror-image of the face.\n\nUseful for aligning textures with bezier curves from the shape-generators|intro.mapeditor.menu.html#commandsmenu"
wraptext = "|Wraps from the tagged face, around pillar in direction of selected, scaling to eliminate seams.\n\nWon't work if the edges to be wrapped around aren't all paralell, and scales texture minimally to fit.  `preserve aspect ratio' option controls whether one or both texture dimensions are scaled.|maped.plugins.tagside.html#texture"

aspecttext = "|If checked, aspect ratio of textures is preserved when texture is scaled wrapping around multiple sides (pillar and multi-wrap).\n\n Click to toggle check."
checkaspectratio = qmenu.item("Preserve aspect ratio", ToggleCheck, aspecttext)

tomirrortext = "|If checked, texture is mirrored so as to look good when wrapped/projected to a wall-maker brush-face, etc."
tomirroritem = qmenu.item("To mirror", ToggleCheck,tomirrortext)

selecttaggedtext = "Tagged items become multi-selection"

shifttagtext = "|If checked, selected side becomes tagged side after `wrap texture from tagged' operation.\n\n  Click to toggle check."
checkshifttagged = qmenu.item("Shift tagged to selected", ToggleCheck, shifttagtext)

def tagpopup(editor, o):
  addtotagged = gluemenuitem("&Add to tagged", AddtoTaggedClick, o, "Adds side to tagged list")
  removefromtagged = gluemenuitem("&Remove from tagged", RemovefromTaggedClick, o, "Takes side off tagged list")
  removefromtaggedstate(removefromtagged, editor,o)
  selecttagged = qmenu.item("&Select tagged list", SelectTaggedClick,selecttaggedtext)
  if gettaggedlist(editor) is None:
    selecttagged.state = qmenu.disabled
  else:
    selecttagged.taglist = gettaggedlist(editor)
  if gettaggedlist(editor) is None and gettagged(editor) is None:
        addtotagged.state = qmenu.disabled
  
  list = [addtotagged,
          removefromtagged,
          selecttagged,
          mencleartag]
  tagpop = qmenu.popup("&More Tagging", list, None, "More commands for managing tags")
  tagpop.label = 'tagpop'
  return tagpop

wrappoptext = "More commands and options"
wraptaggedtext = "|Wraps texture from selected side, which is in a chain of tagged sides, across the rest of the chain, scaling the texture to eliminate seams.\n\nIf side is flanked by two on the tagged list, wrapping goes in direction of whichever was first pushed onto the tagged list.\n\nSomewhat limited, since it requires each side to share two vertices with the next, and tends to fail for complicated multi-brush wraps, probably because tests for vertex-sharing are unduly stringent.  I will be working on making them less restrictive."

def wrappopup(o, tagged):
  editor = mapeditor()
  aligntex = gluemenuitem("&From tagged", AlignTexClick, o, aligntext)
  mirrortex = gluemenuitem("From tagged &mirror", AlignTexClick, o, mirroraligntext)
  pillarwrap = gluemenuitem("&Around pillar", PillarWrapClick, o, wraptext)
  wraptagged = gluemenuitem("A&cross tagged", TaggedWrapClick, o, wraptaggedtext)
  if tagged != None:
    pillarwrapdisabler(pillarwrap, tagged, o)
  else:
    pillarwrap.state = qmenu.disabled
  aligntexstate(aligntex, tagged, o)
  aligntexstate(mirrortex, tagged, o)
  if aligntex.state == qmenu.normal:
    aligntex.state = qmenu.default
  if mirrortex.state == qmenu.normal:
    mirrortex.mirror=1
  wraptaggedstate(wraptagged, o)
  list = [aligntex,
          mirrortex,
#          projexttex(editor,o),
          pillarwrap,
          wraptagged,
          qmenu.sep,
          checkaspectratio,
#          tomirroritem,
          requestmultiplier,
          checkshifttagged
         ]
  popup = qmenu.popup("&Wrapping", list, None, wrappoptext)
  popup.label = 'wrappopup'
  return popup



def getspecdict(spec, root):
  faces = root.findallsubitems("",":f")
  dict = {}
  for face in faces:
    val = face.getint(spec)
    if val!=0:
#      squawk("key "+`val`)
      if dict.has_key(val):
        dict[val].append(face)
      else:
        dict[val] = [face]
  return dict

def findfreetag(dict):
  keys = dict.keys()
#  squawk(`keys`)
  keys.sort()
  i = 1
  for j in keys:
    if i != j:
      return i;
    i = i+1
  return i;

def LinkFaceClick(m, glue=1):
  editor = mapeditor()
  if editor is None: return
  tagged = gettagged(editor)
  tag = tagged.getint("_tag")
  undo = quarkx.action()
  if tag == 0:
    dict = getspecdict("_tag",editor.Root)
#  squawk(`dict`)
    tag = findfreetag(dict)
#    squawk(`tag`)
    newtagged = tagged.copy()
    newtagged.setint("_tag",tag)
#    squawk("new: "+`newtagged.getint("_tag")`)
    undo.exchange(tagged, newtagged)

   # To fix this function. Old way never replaced with new keyword.
#    editor.tagging.tagged = newtagged  
    tagface(newtagged, editor)
  
  newside = m.side.copy()
  newside.setint("_tag",tag)
  oldtag = m.side.getint("_tag")
  if oldtag:
    if quarkx.msgbox("There are faces already linked to this one.\nDo you want to link them to the tagged face also?",
      MT_INFORMATION, MB_YES | MB_NO) == MR_YES:
      faces = dict[oldtag]
      for face in faces:
        if face == m.side:
          continue
        newface = face.copy()
        newface.setint("_tag",tag)
#        if glue: glueface(undo,newface,tagged,0)
        undo.exchange(face,newface)
#  if glue: glueface(undo, newside, tagged, 0)
  undo.exchange(m.side, newside)
  editor.ok(undo, "Link Sides")
  editor.layout.explorer.sellist = [newside]

def gluelinked(o):
  tag = o.getint("_tag")
  item =  qmenu.item("&Glue linked",GlueLinkedClick,"Glue linked items to this")
  if tag == 0:
    item.state = qmenu.disabled
  else:
     item.tag = tag
     item.object = o
  return item

def GlueLinkedClick(m):
#  squawk(`m.tag`)
  editor = mapeditor()
  dict = getspecdict("_tag",editor.Root)
  faces = dict[m.tag]
  glueto = m.object
  undo = quarkx.action()
  for face in faces:
    if face.getint("_tag") == 0 or face is glueto:
      continue
    glueface(undo, face, glueto)
  editor.ok(undo,"Glue Linked Faces")
  editor.layout.explorer.sellist = [glueto]

def UnlinkFaceClick(m):
  editor = mapeditor()
  if editor is None: return
  undo = quarkx.action()
  dict = getspecdict("_tag",editor.Root)
  cofaces = dict[m.tag]
  if len(cofaces) == 2:
    (face0, face1) = (cofaces[0].copy(), cofaces[1].copy())
    face0["_tag"] = face1["_tag"] = ""
    undo.exchange(cofaces[0], face0)
    undo.exchange(cofaces[1], face1) 
  else:
    face = m.object.copy()
    face["_tag"] = ""
    undo.exchange(m.object, face)
  editor.ok(undo,"Unlink Face")  
  editor.layout.sellist = [m.object]

def UnlinkAllClick(m):
  editor = mapeditor()
  if editor is None: return
  undo = quarkx.action()
  dict = getspecdict("_tag",editor.Root)
  cofaces = dict[m.tag]
  for face in cofaces:
    newface = face.copy()
    newface["_tag"] = ""
    undo.exchange(face, newface)
  editor.ok(undo,"Unlink All")  
  editor.layout.sellist = [m.object]
  
def selectmenuitem(o,text,command,help):
  tag = o.getint("_tag")
  item =  qmenu.item(text,command,help)
  if tag == 0:
    item.state = qmenu.disabled
  else:
     item.tag = tag
     item.object = o
  return item

def SelectClick(m):
  editor = mapeditor()
  if editor is None: return
  dict = getspecdict("_tag",editor.Root)
  cofaces = dict[m.tag]
  list = []
  for face in cofaces:
    list.append(face)
  editor.layout.explorer.sellist = list

def isfaces(list):
  if len(list) >1 and list[0].type == ':f':
    return 1
  else:
    return 0

def LinkSelClick(m):
  editor = mapeditor()
  if editor is None: return
  dict = getspecdict("_tag",editor.Root)
  tag =  findfreetag(dict)
  #
  # disabler is supposed to assure that faces is made of faces
  #
  faces = mapeditor().layout.explorer.sellist
  for face in faces:
    face.setint("_tag",tag)
    quarkx.msgbox("Selected items are now linked.", MT_CONFIRMATION, MB_OK)


def breaksharedface(e,o):
  faceitem = qmenu.item("&Break shared face",BreakFaceClick,"|Breaks a shared face into independent faces that are linked. (So that for example they can have different textures, or the same texture differently aligned)")
  faceitem.object = o
  faceitem.editor = e
  faceitem.polys = o.faceof
  if len(faceitem.polys) < 2:
    faceitem.state = qmenu.disabled
  return faceitem
  
def BreakFaceClick(m):
  undo = quarkx.action()
  polys = m.polys
  face = m.object
  editor = m.editor
  dict = getspecdict("_tag",editor.Root)
  tag = findfreetag(dict)
  for poly in polys:
    newpoly = poly.copy()
    newface = face.copy()
    newpoly.appenditem(newface)
    newface.setint("_tag",tag)
    undo.exchange(poly, newpoly)
  undo.exchange(face, None)
  editor.ok(undo, "Break Shared Face")
  editor.layout.explorer.sellist = []


#
#  --------------------  face menu ------------------------
#  stash the old function in the new function's last parameter
#  the disabling + menu logic here has completely lost the plot ...
#

linktext = "|Linking is a device for making it easier to keep certain sets of faces coplanar, such as the components of a chair or a window-frame, or a floor and the bottom of something that's supposed to sit on it.\n\nTo link two faces, tag one, and then select `Link face to tagged' from the Linking submenu for the face you want to link to it.\n\nFurther commands from the Linking submenu then become enabled, for gluing to a side others that are linked to it, unlinking, etc.\n\nSince linked faces are supposed to be coplanar, if two aren't then they are both drawn in dotted red."

def tagmenu(o, editor, oldfacemenu = quarkpy.mapentities.FaceType.menu.im_func):
  "the new right-mouse for sides"
  menu = oldfacemenu(o, editor)
  tagged = gettaggedplane(editor)
  glueitem = gluemenuitem("&Glue to tagged", GlueSideClick, o, gluetext)
  glueitem.label = 'glue'
  snapitem = mapsnapobject.parentSnapPopup(o,editor)
  mirrorflipitem = gluemenuitem("Mirror flip &tex", MirrorFlipTexClick, o, "Flip tex to mirror-image")
  linktotagged = gluemenuitem("&Link face to tagged", LinkFaceClick, o, "|Links face to tagged for the `glue to linked' command.\n\nNormally the `Glue to tagged' command with the `link on glue' option set should be used instead of this command, because this command doesn't move the face to what it gets linked to, and so doesn't test for broken polys.")
#  aligntex = gluemenuitem("&Wrap texture from tagged", AlignTexClick, o, aligntext)
  tagpop = tagpopup(editor, o)
  wrappop = wrappopup(o, tagged)
  linkpopup = qmenu.popup("&Linking",
     [      selectmenuitem(o,"&Glue linked",GlueLinkedClick,"|Glue to this face all faces that are linked to it.\n\n (This one stays still; the others move.)\n\nSince linked sides are supposed to be coplanar, if they aren't they're drawn in dotted red lines."),
      selectmenuitem(o,"&Select linked faces",SelectClick,"|Select all faces linked to this face.\n\nSo that you can for example select all the faces linked this one, and drag or shear them as a multiselection, rather than first move one and then glue the others to it."),
      selectmenuitem(o,"&Unlink face",UnlinkFaceClick,"|Unlink this face from the ones it's linked to"),
      selectmenuitem(o,"Unlink &all",UnlinkAllClick,"|Unlink all the faces linked to this from each other"),
      linktotagged
     ], None, linktext)
  if o is tagged:
    glueitem.state = qmenu.disabled
    linktotagged.state = qmenu.disabled
    wrappop.state = qmenu.disabled
    tagpop.state = qmenu.disabled
    if o.getint("_tag") == 0:
      linkpopup.state = qmenu.disabled
  if tagged is None:
      if o.getint("_tag") == 0:
        linkpopup.state = qmenu.disabled
      if gettaggedpt(editor) is None:
        glueitem.state = qmenu.disabled
      else:
        glueitem.hint = gluepttext
      linktotagged.state = qmenu.disabled
#      if not gettaggedlist(editor):
#        wrappop.state = qmenu.disabled
#        tagpop.state = qmenu.disabled
  
  texpop = findlabelled(menu,'texpop')
  projtex = projecttex(editor,o)
  projtex.text = "Project from tagged"
  texpop.items = texpop.items + [projtex,mirrorflipitem,wrappop]
  menu[:0] = [#extendtolinked(editor, o),
              gluemenuitem("&Tag face",TagSideClick,o,"|Tag face:\n\n`Tags' a face for reference in later operations of positioning and alignment.\n\nThe tagged face then appears in red.\n\nFor more detail on the use of this fuction, click on the InfoBase button below.|maped.plugins.tagside.html#basic"),
#              addtotagged,
              glueitem,
              snapitem,
              tagpop,
              linkpopup,
#              projecttex(editor,o),
#              wrappop,
              breaksharedface(editor,o),
              qmenu.sep]
  return menu


#
# now bung in the new one.
#
quarkpy.mapentities.FaceType.menu = tagmenu



verttext = "|To use this, you need to have one side tagged and another selected.\n\nThe selected side will then be aligned parallel to the tagged side, rotating around this vertex as a fulcrum."
def tagvertmenu(self, editor, view, oldvertmenu = quarkpy.maphandles.VertexHandle.menu.im_func):
  menu = oldvertmenu(self,editor,view)
  face = None
  tagged = gettagged(editor)
  if not tagged is None:
    selection = editor.layout.explorer.sellist
    if isoneface(selection) and not selection[0] is tagged:
      face = selection[0]
  item = gluemenuitem("&Align face to tagged", GlueSideClick, face, verttext)
  item.fulcrum = self.pos
  if face is None:
    item.state = qmenu.disabled
  menu[:0] = [item]
  return menu

quarkpy.maphandles.VertexHandle.menu = tagvertmenu


#
#  Ditto for the menu that appears when we click on the background
#

def backmenu(editor, view=None, origin=None, oldbackmenu = quarkpy.mapmenus.BackgroundMenu):
  menu = oldbackmenu(editor, view, origin)
  if origin is not None:
    item = maptagpoint.tagpointitem(editor, editor.aligntogrid(origin))
    for test in menu:
      if hasattr(test, "origin"):
        i = menu.index(test)+1
        break
    else:
      i = 0
    menu[i:i] = [item]
  return menu

quarkpy.mapmenus.BackgroundMenu = backmenu


#
#  menus for entities containing faces.
#

typenames = {
  ":p" : "poly",
  ":b" : "entity",
  ":g" : "group"
}



def cutpoly(editor, o):
  item = qmenu.item("Cut poly &along tagged",CutPolyClick,"|Cuts this poly along the plane of the tagged face.")
  item.state = qmenu.disabled
  tagged = gettaggedplane(editor)
  if tagged is None:
    return item
  cutter1 = tagged.copy()
  piece1 = o.copy()
  piece1.appenditem(cutter1)
  if piece1.broken:
    return item
  piece2 = o.copy()
  cutter2 = tagged.copy()
  cutter2.swapsides()
  piece2.appenditem(cutter2)
  if piece2.broken:
    return item
  for piece in [piece1, piece2]:
    for face in piece.subitems:
      if not face in piece.faces:
#        squawk("hacking")
        piece.removeitem(face)
  item.pieces = (piece1,piece2)
  item.o = o
  item.state=qmenu.normal
  return item

def CutPolyClick(m):
  editor = mapeditor()
  if editor is None: return
  undo = quarkx.action()
  undo.put(m.o.parent,m.pieces[0],m.o)
  undo.exchange(m.o, m.pieces[1])
  editor.ok(undo,"Cut poly along tagged")
  

def gluepoly(editor, o):
  typename = typenames[o.type]
  item = qmenu.item("Glue &linked faces",GluePolyClick,"|Faces that are linked to faces in this "+typename+" get glued to them")
  tagdict = getspecdict("_tag",o)
  if tagdict == {}:
    item.state=qmenu.disabled
    return item
  item.dict = tagdict
  item.o = o
  return item


def GluePolyClick(m):
  editor=mapeditor()
  if editor is None: return
  tagdict = m.dict
  if not checkglue(tagdict):
     quarkx.msgbox("The selection contains linked faces that aren't coplanar.  Fix this and then try again",MT_WARNING,MB_OK)
     return
  undo = quarkx.action()
  mapdict = getspecdict("_tag",editor.Root)
  gluefaces(editor,undo,m.o,tagdict)
  editor.ok(undo,"Glue linked faces")    
  editor.layout.explorer.sellist=[m.o]



def tagpolymenu(o, editor, oldmenu=quarkpy.mapentities.PolyhedronType.menu.im_func):
  "the new right-mouse menu for polys"
  menu = oldmenu(o, editor)
  menu[:0] = [gluepoly(editor,o),
              projecttex(editor,o),
              mergepolys.mergepoly(editor,o), # now in mapmergepoly
              cutpoly(editor,o),
              qmenu.sep]
  return menu
  
quarkpy.mapentities.PolyhedronType.menu = tagpolymenu

def taggroupmenu(o, editor,oldmenu=quarkpy.mapentities.GroupType.menu.im_func):
  "the new right-mouse menu for groups"
  menu = oldmenu(o, editor)
  menu[:0] = [gluepoly(editor,o),
              mergepolys.groupmergepoly(editor,o),
              projecttex(editor,o),
              qmenu.sep]
  return menu
  
quarkpy.mapentities.GroupType.menu = taggroupmenu

def tagbrushmenu(o, editor,oldmenu=quarkpy.mapentities.BrushEntityType.menu.im_func):
  "the new right-mouse menu for groups"
  menu = oldmenu(o, editor)
  menu[:0] = [gluepoly(editor,o),
              projecttex(editor,o),
              qmenu.sep]
  return menu
  
quarkpy.mapentities.BrushEntityType.menu = tagbrushmenu



#
#  Set up command menus.  Maybe junk these for buttons, or only
#   use right-mouse click?
#

def commandsclick(menu, oldcommand=quarkpy.mapcommands.onclick):
  oldcommand(menu)
  editor = mapeditor()
  if editor is None: return
  menaddtotagged.state=qmenu.disabled
  selection = editor.layout.explorer.sellist
  if isfaces(selection):
     menlinksel.state = qmenu.normal
  else:
     menlinksel.state = qmenu.disabled
  if isoneface(selection):
    face = selection[0]
    mentagside.state = qmenu.normal
    tag =face.getint("_tag")
#
# This below overloads the menu, I think.
#    if tag==0:
#      mengluelinked.state = qmenu.disabled
#    else:
#      mengluelinked.state = qmenu.normal
#      mengluelinked.object = face
#      mengluelinked.tag = tag
  else:
    face = None
    mentagside.state = qmenu.disabled
#    mengluelinked.state = qmenu.disabled
  tagged = gettaggedplane(editor)
  if tagged is None:
    if gettaggedpt(editor):
      mencleartag.state = qmenu.normal
      menglueside.state = qmenu.normal
    else:
      if not gettaggedlist(editor):
        mencleartag.state = qmenu.disabled
      menglueside.state = qmenu.disabled
    menaligntex.state = qmenu.disabled
  else:
    if isoneface(selection) and selection[0] is not tagged:
       menaddtotagged.state=qmenu.normal
    mencleartag.state = qmenu.normal
    menglueside.state = len(selection)==0 and qmenu.disabled
    if face is None or tagged is face:
      menaligntex.state = qmenu.disabled
    else:
      menaligntex.state = qmenu.normal
      aligntexstate(menaligntex, tagged, face)
  try:
    if not editor.tagging is None:
       mencleartag.state = qmenu.normal
  except AttributeError: pass

mentagside  = qmenu.item("&Tag side", TagSideClick, tagtext)
mencleartag = qmenu.item("&Clear Tag", ClearTagClick, "|Clear Tag:\n\nClears (cancels) all the tags that have been set.|intro.mapeditor.menu.html#commandsmenu")
menglueside = qmenu.item("&Glue to Tagged", GlueSideClick, "|Glue to Tagged:\n\nMoves & aligns the selected side to tagged side.|intro.mapeditor.menu.html#commandsmenu")
menaddtotagged = qmenu.item("&Add to tagged", AddtoTaggedClick, "|Add to tagged:\n\nAdds side to tagged list.|intro.mapeditor.menu.html#commandsmenu")
menaligntex = qmenu.item("&Wrap texture from tagged", AlignTexClick, aligntext)
menlinksel  = qmenu.item("&Link selected",LinkSelClick,"|Link selected:\n\nLink the selected faces.\n\nWhat the Link selection command then does is 'link' all of the selected faces so that if one is moved, you will be invited to move all the others with it.\n\nSee the infobase for more on how to select items and activate this function.|intro.mapeditor.menu.html#commandsmenu")
#mengluelinked = qmenu.item("Gl&ue linked",GlueLinkedClick,"|Glue linked:\n\nGlue linked faces to the selected one.|intro.mapeditor.menu.html#commandsmenu")

quarkpy.mapcommands.items.append(qmenu.sep)   # separator
quarkpy.mapcommands.items.append(mentagside)
quarkpy.mapcommands.items.append(mencleartag)
quarkpy.mapcommands.items.append(menglueside)
quarkpy.mapcommands.items.append(menaligntex)
quarkpy.mapcommands.items.append(menaddtotagged)
quarkpy.mapcommands.items.append(menlinksel)
#
# de trop on the menu, methinks
#quarkpy.mapcommands.items.append(mengluelinked)
#quarkpy.mapcommands.shortcuts["Alt+L"] = mengluelinked

quarkpy.mapcommands.onclick = commandsclick


for menitem, keytag in [(mentagside, "Tag Side"),
                        (mencleartag, "Clear Tags"),
                        (menglueside, "Glue Side"),
                        (menaligntex, "Align Texture"),
                        (menaddtotagged, "Add to Tagged"),
                        (menlinksel, "Link Selection")]:

    MapHotKey(keytag,menitem,quarkpy.mapcommands)


menselecttagged = quarkpy.qmenu.item("Select Tagged Face(s)",SelectTaggedClick,"|Select Tagged Face(s):\n\nThe things now tagged will become a multiple selection.|intro.mapeditor.menu.html#selectionmenu")

def selectionclick(menu, oldselect=quarkpy.mapselection.onclick):
    oldselect(menu)
    editor = mapeditor()
    if editor is None: return
    list = gettaggedlist(editor)
    if list is None:
        list = gettagged(editor)
        if list is not None:
            list = [list]
    if list is None:
        menselecttagged.state=qmenu.disabled
    else:
        menselecttagged.state=qmenu.normal
        menselecttagged.taglist = list

quarkpy.mapselection.onclick = selectionclick
quarkpy.mapselection.items.append(menselecttagged)

for menitem, keytag in [(menselecttagged, "Select Tagged Faces")]:

    MapHotKey(keytag,menitem,quarkpy.mapselection)

# ----------- REVISION HISTORY ------------
#$Log: maptagside.py,v $
#Revision 1.44  2013/03/17 14:15:09  danielpharos
#Fixed a typo.
#
#Revision 1.43  2008/08/21 12:40:38  danielpharos
#Fixed cut poly menu item disappearing from menu when having a face tagged that can't be cut.
#
#Revision 1.42  2008/08/18 20:36:25  danielpharos
#Removed redundant variable
#
#Revision 1.41  2008/02/22 09:52:21  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.40  2006/11/30 01:17:47  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.39  2006/11/29 06:58:35  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.37.2.2  2006/11/07 17:34:45  cdunde
#To stop console error when Alt+S is pressed with cursor outside of any view.
#
#Revision 1.37.2.1  2006/11/03 23:48:46  cdunde
#To fix this function. Old way never replaced with new keyword.
#
#Revision 1.37  2006/07/11 14:18:31  cdunde
#Added 0 division testing to stop console errors
#
#Revision 1.36  2005/10/15 00:51:56  cdunde
#To reinstate headers and history
#
#Revision 1.32  2003/10/07 21:37:31  cdunde
#Update for Tagside Infobase detail link
#
#Revision 1.31  2003/05/21 06:39:35  cdunde
#To remove error message box causing cleartag for tagged point not to work properly
#
#Revision 1.30  2003/05/09 01:01:08  cdunde
#Added function buttons for tagtoolbar
#
#Revision 1.29  2003/03/28 02:54:40  cdunde
#To update info and add infobase links.
#
#Revision 1.28  2003/03/26 03:31:43  cdunde
#To update info and make infobase link
#
#Revision 1.27  2003/03/25 08:30:56  tiglari
#more fix of select tagged logic (the de-tagging effect is for now taken to
# be the intended behavior)
#
#Revision 1.26  2003/03/24 22:58:08  tiglari
#fix selected tag faces enable bug (noted by cdunde)
#
#Revision 1.25  2003/03/24 08:57:15  cdunde
#To update info and link to infobase
#
#Revision 1.24  2003/03/15 06:56:56  cdunde
#To add hint updates and infobaselinks
#
#Revision 1.23  2003/01/03 07:50:42  tiglari
#transfer texture-mirror, swapsides_leavetex from rel-63a brancy
#
#Revision 1.20.2.4  2003/01/01 05:08:33  tiglari
#remove debug comments
#
#Revision 1.20.2.3  2002/12/30 05:04:13  tiglari
#remove 'to mirror' option - doesn't seem to be necessary
#
#Revision 1.20.2.2  2002/05/19 05:06:12  tiglari
#Put Select tagged faces command on selection menu
#

#Revision 1.21  2002/05/18 22:38:31  tiglari
#remove debug statement
#
#Revision 1.20  2002/03/30 06:33:33  tiglari
#improve F1 help for texture wrap multiplier (face RMB|Textures menu)
#
#Revision 1.19  2001/10/07 22:33:58  tiglari
#None-returning function call fixed
#
#Revision 1.18  2001/08/07 23:35:37  tiglari
#snap map object to tagged face command
#
#Revision 1.17  2001/06/17 21:10:56  tiglari
#fix button captions
#
#Revision 1.16  2001/05/25 12:26:01  tiglari
#tagged plane support
#
#Revision 1.15  2001/05/03 06:47:06  tiglari
#Fixed no wrap to paralell faces and failure of wrap hotkey bugs
#
#Revision 1.14  2001/04/15 08:53:44  tiglari
#move merge poly code to mergepolys.py; add merge polys in group functionality
#
#Revision 1.13  2001/04/15 06:08:47  tiglari
#merge polys improved (new coplanar from faceutils)
#
#Revision 1.12  2001/03/20 08:02:16  tiglari
#customizable hot key support
#
#Revision 1.11.2.1  2001/03/11 22:08:15  tiglari
#customizable hot keys
#
#Revision 1.11  2001/02/25 23:32:25  tiglari
#attempt to make wrap across tagged faces more robust
#
#Revision 1.10  2000/07/30 03:29:10  tiglari
#`wrap from tagged mirror' added to texture|wrapping, for easier texturing
#with arches & bevels
#
#Revision 1.9  2000/07/29 02:07:57  tiglari
#minor internal fiddles
#
#Revision 1.8  2000/07/25 15:55:24  alexander
#fixed: right clicking in the background python crash
#
#Revision 1.7  2000/07/24 09:12:49  tiglari
#Put texture-wrap & projection into a submenu labelled 'texpop', for texture menu cleanup as suggested by Brian Audette
#
#Revision 1.6  2000/07/23 08:35:12  tiglari
#tag point functions removed, projection of texture from tagged corner bezier point added (to projecttex(editor, o))
#
#Revision 1.5  2000/06/12 11:22:48  tiglari
#fixed problem with texture-wrapping from paralell faces (WrapTexClick)
#
#Revision 1.4  2000/06/03 10:25:30  alexander
#added cvs headers
#
#Revision 1.3  2000/05/27 05:37:08  tiglari
#hopefully fixed texture scale transpose problem in wrapping (wraptex).
#
#
