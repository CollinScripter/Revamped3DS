""" QuArK  -  Quake Army Knife
"""
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/bspstudy.py,v 1.13 2005/11/27 05:55:12 cdunde Exp $
#

import quarkx
import quarkpy.qbaseeditor
import quarkpy.mapmenus
import quarkpy.bspcommands
import quarkpy.maphandles
import quarkpy.mapentities
import quarkpy.dlgclasses
import mapmadsel

from quarkpy.maputils import *

#
#  This one is to identify the planes that have some
#   other lying close to them; it takes only the first
#   from each pair.  A 'NearPlanesDlg' below gets the
#   planes that are close to an already given one.
#
class ClosePlanesDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (220,200)
    dfsep = 0.35
    dlgflags = FWF_KEEPFOCUS 

    dlgdef = """
        {
        Style = "9"
        Caption = "Close Plane Finder"

        closeplanes: = {
          Typ = "C"
          Txt = "Planes:"
          Items = "%s"
          Values = "%s"
          Hint = "These are the planes that are too close to others.  Pick one," $0D " then push buttons on row below for action."
        }

        normal: = {
          Typ = "EF00003"
          Txt = "Normal"
          Hint = "The normal of the chosen plane"
        }
        
        dist: = {
          Typ = "EF00001"
          Txt = "dist"
          Hint = "The dist value of the chosen plane"
        }
        
        sep: = { Typ="S" Txt=""}

        buttons: = {
          Typ = "PM"
          Num = "2"
          Macro = "closeplanes"
          Caps = "SN"
          Txt = "Actions:"
          Hint1 = "Show the chosen one (point & normal)"
          Hint2 = "Get the planes near the chosen one"
        }

        num: = {
          Typ = "EF1"
          Txt = "No. found"
        }

        close: = {
          Typ = "EF001"
          Txt = "tolerance: "
          Hint = "Planes whose dist*norm difference is less than this are deemed suspicious."
        }
        
        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

    def inspect(self):
        self.editor.layout.explorer.uniquesel = self.pack.plane
        
    def nearplanes(self):
        index = eval(self.chosen)
        plane = self.pack.closeones[index]
        nearPlanesClickFunc(None,plane,self.editor)


def macro_closeplanes(self, index=0):
    editor = mapeditor()
    if editor is None: return
    if index==1:
        editor.closeplanesdlg.inspect()

    elif index==2:
        editor.closeplanesdlg.nearplanes()
        
quarkpy.qmacro.MACRO_closeplanes = macro_closeplanes


def PlanesClick(m):
    editor=mapeditor()
    root = editor.Root
    planes = editor.Root.parent.planes
    planegroup = quarkx.newobj("Planes (%d):g"%len(planes))
    undo=quarkx.action()
    undo.put(root,planegroup)
    i=0
    for plane in planes:
#       debug('plane '+plane.shortname+': '+`plane['norm']`)
#       debug('  dist: '+"%2f"%plane['dist'])
       undo.put(planegroup,plane)
    editor.ok(undo, 'get planes')
    editor.layout.explorer.uniquesel=planegroup
    editor.planes = planegroup


def getClosePlanes(close, editor):
    closeones=[]
    planes = editor.planes.subitems
    indexes = editor.Root.parent.closeplanes(close)
    for i in indexes:
        closeones.append(planes[i])
    return closeones

def CheckPlanesClick(m):
    editor=mapeditor()
    try:
        planes=editor.planes.subitems
    except (AttributeError):
        PlanesClick(m)
        planes=editor.planes.subitems

    close = quarkx.setupsubset(SS_MAP, "Options")["planestooclose"]
    if close==None:
        close="1.0"
    close=eval(close)
    
    closeones = getClosePlanes(close, editor)
#    editor.layout.explorer.sellist=closeones
#    quarkx.msgbox("%d suspicious planes found"%len(closeones),2,4)

    class pack:
      "stick stuff here"
    pack.close=close
    pack.closeones=closeones

    def setup(self, pack=pack, editor=editor):
        self.pack=pack
        #
        # Part of the convolution for the buttons, to communicate
        #  which objects methods should be called when one pushed.
        # Cleaned up in onclosing below.
        #
        editor.closeplanesdlg=self
        #
        # Names and list-indexes of close planes
        #
        ran = range(len(pack.closeones))
        pack.slist = map(lambda obj,num:"%d) %s"(num+1,obj.shortname), pack.closeones, ran)
        pack.klist = map(lambda d:`d`, ran)
        self.src["closeplanes$Items"] = "\015".join(pack.slist)
        self.src["closeplanes$Values"] = "\015".join(pack.klist)
        #
        # Note the commas, EF..1 controls take 1-tuples as data
        #
        self.src["num"]=len(pack.klist),
        self.src["close"]=pack.close,

    def action(self, pack=pack, editor=editor):
        src = self.src
        #
        # note what's been chosen
        #
        self.chosen = src["closeplanes"]
        plane = self.pack.closeones[eval(self.chosen)]
        self.pack.plane=plane
#        debug('norm '+`plane.normal`+' dist '+`plane.dist`)
        src["normal"]=plane.normal.tuple
        src["dist"]=plane.dist,
        #
        # see if thinness threshold has been changed
        #
        newclose, = self.src["close"]
        if newclose!=pack.close:
            if newclose==1.0:
                quarkx.setupsubset(SS_MAP, "Options")["planestooclose"]=None
            else:
                quarkx.setupsubset(SS_MAP, "Options")["planestooclose"]="%f2"%newclose
 
            pack.close="%.2f"%newclose
            pack.closeones=getClosePlanes(newclose, editor)

    #
    # Cleanup when dialog closes (not needed if no mess has
    #  been created)
    #
    def onclosing(self,editor=editor):
        del editor.closeplanesdlg
    
    ClosePlanesDlg(quarkx.clickform, 'closeplanes', editor, setup, action, onclosing)

    
def NodesClick(m,editor=None):
    if editor is None:
        editor=mapeditor()
    if editor is None:
        return
    try:
        nodes=editor.nodes
        quarkx.msgbox("Nodes already gotten",2,4)
        editor.layout.explorer.uniquesel=nodes
    except:
        root = editor.Root
        nodes = root.parent.nodes
        nodes.shortname='Nodes (%s)'%nodes['children']
        undo=quarkx.action()
        undo.put(root,nodes)
        editor.ok(undo, 'get nodes')
        editor.layout.explorer.uniquesel=nodes
        editor.nodes=nodes
  
planesitem=qmenu.item('Get Planes',PlanesClick)
nodesitem=qmenu.item('Get Nodes',NodesClick)
planecheckitem=qmenu.item('Check Planes',CheckPlanesClick)

quarkpy.bspcommands.items.append(planesitem)
quarkpy.bspcommands.items.append(nodesitem)
quarkpy.bspcommands.items.append(planecheckitem)


#
#  This one is to identify the planes that lie close
#    to a specified one.  ClosePlanesDlg above identifies
#    planes that have others near them.  Uses same
#    tolerance as that one.
#
class NearPlanesDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (220,200)
    dfsep = 0.35
    dlgflags = FWF_KEEPFOCUS 

    dlgdef = """
        {
        Style = "9"
        Caption = "Near Planes"

        nearplanes: = {
          Typ = "C"
          Txt = "Planes:"
          Items = "%s"
          Values = "%s"
          Hint = "These are the planes that are near the given one.  Pick one," $0D " then push buttons on row below for action."
        }

        normal: = {
          Typ = "EF00003"
          Txt = "Normal"
          Hint = "The normal of the chosen plane"
        }
        
        dist: = {
          Typ = "EF00001"
          Txt = "dist"
          Hint = "The dist value of the chosen plane"
        }
        
        sep: = { Typ="S" Txt=""}

        buttons: = {
          Typ = "PM"
          Num = "3"
          Macro = "nearplanes"
          Caps = "SCN"
          Txt = "Actions:"
          Hint1 = "Show the chosen one"
          Hint2 = "Collect faces lying on the chosen one"
          Hint3 = "Find nodes split by the chosen one"
        }

        num: = {
          Typ = "EF1"
          Txt = "No. found"
        }
        
        close: = {
          Typ = "EF001"
          Txt = "tolerance: "
          Hint = "Planes whose dist*norm difference is less than this are deemed suspicious."
        }

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

    def inspect(self):
        self.editor.layout.explorer.uniquesel=self.pack.plane

    def collect(self):
        index = eval(self.chosen)
        plane = self.pack.nearones[index]
        collectFacesClickFunc(None,plane,self.editor)

    def findsplit(self):
        editor=self.editor
#        debug('PLANE '+`self.pack.plane.num`)
        findSplitNodes(self.editor,self.pack.plane)

def macro_nearplanes(self, index=0):
    editor = mapeditor()
    if editor is None: return
    if index==1:
        editor.nearplanesdlg.inspect()
    elif index==2:
        editor.nearplanesdlg.collect()
    elif index==3:
        editor.nearplanesdlg.findsplit()
 
        
quarkpy.qmacro.MACRO_nearplanes = macro_nearplanes

def findSplitNodes(editor, plane):
    try:
        node=editor.nodes
    except (AttributeError):
        NodesClick(None,editor)
        node=editor.nodes
    list=[]
    findsplitnodes2(node, plane, list)
    editor.invalidateviews()
    mapmadsel.browseListFunc(editor,list)

def findsplitnodes2(node, plane, list,n=0):
    if plane.num == node.plane.num:
        list.append(node)
#        debug('append '+`node.plane.num`+'; '+`plane.num`)
    for item in node.subitems:
        if item.type==":bspnode":
            if item.leaf!=1:
                findsplitnodes2(item, plane, list,n+1)


def getNearPlanes(close, plane, editor):
    indexes = plane.nearplanes(close,editor.Root.parent)
    return map(lambda index,planes=editor.planes.subitems:planes[index], indexes)


def nearPlanesClickFunc(m,o,editor):
            #
            # planes must have been collected for this
            #  menu item to be available
            #
            close = quarkx.setupsubset(SS_MAP, "Options")["planestooclose"]
            if close==None:
                close="1.0"
            close=eval(close)

            nearones = getNearPlanes(close,o, editor)
        #   debug('near '+`nearones`)
        #    editor.layout.explorer.sellist=closeones
        #    quarkx.msgbox("%d suspicious planes found"%len(closeones),2,4)

            class pack:
              "stick stuff here"
            pack.close=close
            pack.nearones=nearones

            def setup(self, pack=pack, editor=editor, plane=o):
                self.pack=pack
                self.plane=plane
                #
                # Part of the convolution for the buttons, to communicate
                #  which objects methods should be called when one pushed.
                # Cleaned up in onclosing below.
                #
                editor.nearplanesdlg=self

                #
                # Names and list-indexes of close planes
                #
                ran = range(len(pack.nearones))
                pack.slist = map(lambda obj, num:"%d) %s"%(num, obj.shortname, pack.nearones, ran))
                pack.klist = map(lambda d:`d`, ran)
                self.src["nearplanes$Items"] = "\015".join(pack.slist)
                self.src["nearplanes$Values"] = "\015".join(pack.klist)
                #
                # Note the commas, EF..1 controls take 1-tuples as data
                #
                self.src["num"]=len(pack.klist),
                self.src["close"]=pack.close,

            def action(self, pack=pack, editor=editor):
                src = self.src
                #
                # note what's been chosen
                #
                self.chosen = src["nearplanes"]
                plane = self.pack.nearones[eval(self.chosen)]
                self.pack.plane=plane
#                debug('norm '+`plane.normal`+' dist '+`plane.dist`)
                src["normal"]=plane.normal.tuple
                src["dist"]=plane.dist,
                #
                # see if thinness threshold has been changed
                #
                newclose, = self.src["close"]
                if newclose!=pack.close:
                    if newclose==1.0:
                        quarkx.setupsubset(SS_MAP, "Options")["planestooclose"]=None
                    else:
                        quarkx.setupsubset(SS_MAP, "Options")["planestooclose"]="%f2"%newclose

                    pack.close="%.2f"%newclose
                    pack.nearones=getNearPlanes(newclose, self.plane, editor)
            
            #
            # Cleanup when dialog closes (not needed if no mess has
            #  been created)
            #
            def onclosing(self,editor=editor):
                del editor.nearplanesdlg

            NearPlanesDlg(quarkx.clickform, 'nearplanes', editor, setup, action, onclosing)

def collectFacesClickFunc(m,o,editor):
            faces = editor.Root.findallsubitems("",":f")
            dist, normal = o.dist, o.normal
            planept = dist*normal
            coplanar=[]
            i=0
            for face in faces:
              try:
                #
                # if the normals are equal or opposite
                #
                if math.fabs(normal*face.normal)>.999:
                    #
                    # and the plane points are identical:
                    #
                    if not(planept-face.dist*face.normal):
                        coplanar.append(face)
              except:
                pass
              i=i+1;
#            quarkx.msgbox(`i`+' faces tried',2,4)                    
            quarkx.msgbox(`len(coplanar)`+' coplanar faces',2,4)            
            editor.layout.explorer.sellist = coplanar

class PlaneType(quarkpy.mapentities.EntityManager):
    "Bsp planes"

    def menu(o, editor):

        def collectFacesClick(m,o=o,editor=editor):
            collectFacesClickFunc(m,o,editor)
     
        def nearPlanesClick(m,o=o,editor=editor):
            nearPlanesClickFunc(m,o,editor)

        def splitNodesClick(m,o=o,editor=editor):
            findSplitNodes(editor,o)
            
        collectItem=qmenu.item("Select Faces",collectFacesClick,"|Select the faces lying on this plane")
        nearItem = qmenu.item("Near Planes",nearPlanesClick,"|Find the planes near this one")
        splitItem = qmenu.item("Split Nodes",splitNodesClick,"|Find the nodes split by this plane")
        return [collectItem, nearItem, splitItem]
        
class HullType(quarkpy.mapentities.GroupType):
    "Bsp Hulls (models)"

    def menu(o, editor):

        def showFaces(m,o=o,editor=editor):
            for face in o.subitems:
                face.flags = face.flags & ~2
        
        faceItem = qmenu.item("Show Faces",showFaces)
        return [faceItem]

def nodeBox(o):
    "viewed from positive z"
    result = []
    blb = quarkx.vect(o['mins'])
    trf = quarkx.vect(o['maxs'])
    blf = quarkx.vect(blb.x, trf.y, blb.z)
    tlf = quarkx.vect(blb.x, trf.y, trf.z)
    tlb = quarkx.vect(blb.x, blb.y, trf.z)
    trb = quarkx.vect(trf.x, blb.y, trf.z)
    brb = quarkx.vect(trf.x, blb.y, blb.z)
    brf = quarkx.vect(trf.x, trf.y, blb.z)
    for triple in ((tlb,tlf, blf), (brf, trf, trb),
                   (tlf, tlb, trb), (brb, blb, blf),
                   (tlf, trf, brf), (brb, trb, tlb)):
        face = quarkx.newobj('box face:f')
        face.setthreepoints(triple,0)
        result.append(face)
    return result


def nodePoly(o):
    if o['empty']:
        return None
    poly = quarkx.newobj("poly:p")
    for face in nodeBox(o):
        poly.appenditem(face)
    center=(quarkx.vect(o['mins'])+quarkx.vect(o['maxs']))/2
    parent = o.parent
    current = o
#    while 0:
    while parent is not None and parent.type==":bspnode":
        plane = parent.findallsubitems("",":bspplane")[0]
        face=quarkx.newobj('%s:f'%plane.shortname)
#        debug(' plane: '+plane.name)
        norm = quarkx.vect(plane['norm'])
        dist, = plane['dist']
        orth = orthogonalvect(norm)
        cross = orth^norm
        org = dist*norm
        face.setthreepoints((org, org+orth,org+cross),0)
        if face.normal*norm<0:
            face.swapsides()
        if current.name[:5]=='First':
            face.swapsides()
        poly.appenditem(face)
#        if not face in poly.faces:
#            poly.removeitem(face)
        current = parent
        parent = parent.parent
    return poly

class NodeType(quarkpy.mapentities.GroupType):
    "Bsp Nodes"
     
    def drawback(o, editor, view, mode):
        view.drawmap(nodePoly(o),mode)

    def menu(o, editor):
         
        #
        # For debugging
        #
        def bboxPoly(m, o=o, editor=editor):
            poly = nodePoly(o)
            undo=quarkx.action()
            undo.put(o,poly)
            editor.ok(undo,"Add bbox Poly")

        polyItem=qmenu.item("Add BBox poly", bboxPoly)


#
#  hmm this one doesn't actually seem to be so straightforward
#
#        def showFaceClick(m,o=o,editor=editor):
#            faces=o.faces
#            debug(`faces`)
#            
#        faceItem=qmenu.item("Show Faces",showFaceClick)

        return [polyItem]

quarkpy.mapentities.Mapping[":bspnode"] = NodeType()
quarkpy.mapentities.Mapping[":bspplane"] = PlaneType()
quarkpy.mapentities.Mapping[":bsphull"] = HullType()

def bspfinishdrawing(editor, view, oldmore=quarkpy.qbaseeditor.BaseEditor.finishdrawing):
#    debug('start draw')
    from plugins.tagging import drawsquare
    oldmore(editor, view)
    sel = editor.layout.explorer.uniquesel
    if sel is None:
      return
    cv = view.canvas()
    cv.pencolor = MapColor("Duplicator")
    if sel.type==":bspplane":
#        debug('plane')
        dist, = sel["dist"]
        norm = quarkx.vect(sel["norm"])
        pos = dist*norm         
        p1 = view.proj(pos)
        p2 = view.proj(pos+96*norm)
        drawsquare(cv,p1,10)
        cv.line(p1, p2)    

quarkpy.qbaseeditor.BaseEditor.finishdrawing = bspfinishdrawing

# ----------- REVISION HISTORY ------------
#$Log: bspstudy.py,v $
#Revision 1.13  2005/11/27 05:55:12  cdunde
#To start header and history log
#
#
