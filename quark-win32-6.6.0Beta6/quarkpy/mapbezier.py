"""   QuArK  -  Quake Army Knife

Management of Bezier patches
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/mapbezier.py,v 1.45 2008/05/25 21:02:46 cdunde Exp $

#py2.4 indicates upgrade change for python 2.4

import quarkx
from maputils import *
import qhandles
import maphandles
import mapentities
import dlgclasses

from plugins.tagging import *
import plugins.maptagpoint
from b2utils import *

class CornerTexPos(dlgclasses.LiveEditDlg):
    endcolor = AQUA
    size = (170,190)
    dfsep = 0.4

    dlgdef = """
        {
        Style = "9"
        Caption = "Texture Corner Dialog"


        Corners: =
        {
         Txt = "texrect" Typ = "EF004"
         Hint = "(0,0).s (0,0).t, (m,n).s, (m,n).t, when tex placement is rectangular." $0D "Set these numbers to enforce a rectangular texture scale." $0D "If this is blank, the scale is not rectangular"
        }
        Corner1: =
        {
         Txt = "(0,0)"  Typ = "EF002"
         Hint = "s t texture coordinates for 0,0 corner"
        }
        Corner2: =
        {
         Txt = "(0,n)"  Typ = "EF002"
         Hint = "s t texture coordinates for 0,n corner"
        }
        Corner3: =
        {
         Txt = "(m,0)"  Typ = "EF002"
         Hint = "s t texture coordinates for m,0 corner"
        }
        Corner4: =
        {
         Txt = "(m,n)"  Typ = "EF002"
         Hint = "s t texture coordinates for m,n corner"
        }

        sep: = { Typ="S" Txt=""}

        fixed: ={Txt="fixed int." Typ="X"
                }

        sep: = { Typ="S" Txt=""}



        exit:py = { Txt="" }
    }
    """

class CPTexPos(dlgclasses.LiveEditDlg):
    endcolor = AQUA
    size = (100,100)
    dfsep = 0.5

    dlgdef = """
        {
        Style = "9"
        Caption = "Positioning Dialog"

        Coords: = 
        {
        Txt = "&"
        Typ = "EF002"
        Hint = "s t texture coordinates.  Enter new ones here." $0D "The difference between new and old can be propagated to row, column or all with checkboxes below."
        }

        sep: = {Typ="S" Txt=" "} 
        moverow: ={Txt="move row" Typ="X"
                   Hint = "If this is checked, texture movement applies to whole row (same color)."}
        movecol: ={Txt="move col" Typ="X"
                   Hint = "If this is checked, texture movement applies to whole column (different colors)."}
        moveall: ={Txt="move all" Typ="X"
                   Hint = "If this is checked, whole texture is shifted"}

        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

def pointsToMove(moverow, movecol, i, j, h, w):
    "returns list of (i,j) indexes of points to move"
    "if moverow==1 and movecol==1, move everything"
    if moverow and movecol:
        def row(i,w=w):
             return map(lambda j,i=i:(i,j),range(w))
        return reduce(lambda x,y:x+y, map(row,range(h))) 
    if movecol:
        return map(lambda i,j=j:(i, j),range(h))
    if moverow:
        return map(lambda j,i=i:(i, j), range(w))
    return (i, j),  # Newbie Pythonistas: the comma is not a typo,
                    # but means that the function returns a 
                    # 1-element tuple whose sole element is a 2-tuple.


def texcpclick(m):
    h, editor = m.h, m.editor
          
    class pack:
        "place to stick stuff"
    pack.ij, pack.b2 = h.ij, h.b2

    def setup(self, pack=pack):
        cp, (i, j), b2 = map(list, pack.b2.cp), pack.ij, pack.b2
        src = self.src
        p = cp[i][j]
        src["Coords"] = cp[i][j].s, cp[i][j].t

    def action(self, pack=pack):
        cp, (i, j), b2 = copyCp(pack.b2.cp),   pack.ij, pack.b2
        s, t = self.src["Coords"]
        os, ot = cp[i][j].st
        ds, dt = s-os, t-ot
        delta = quarkx.vect(0, 0, 0, ds, dt)
        moverow, movecol, moveall = self.src["moverow"], self.src["movecol"], self.src["moveall"]
        if moveall:
            moverow=movecol=1
        for (m, n) in pointsToMove(moverow, movecol, i, j, b2.H, b2.W):
            cp[m][n] = cp[m][n]+delta
        new = b2.copy()
        new.cp = cp
        undo=quarkx.action()
        undo.exchange(b2, new)
        self.editor.ok(undo,"move texture")
        pack.b2 = new
        self.editor.invalidateviews()

    CPTexPos(quarkx.clickform, 'beztexpos', editor, setup, action)


#
# The idea here is to use the bezier formulas (see comments to bezier.pas)
#  to compute the 1/4, 1/2, 3/4 points on the bezier curve segment
#  whose midpoint is at i (in each column), the 1/2 point becomes
#  the new even coordinate cp, & the new odd coordinate cp's are
#  chosen to get the line to pass thru the 1/4 and 3/4 points.
#
# The structure of this code should be revamped to operate on
#  ranges of rows, columns or both at once, then thinning should
#  be added.
#
def quilt_addrow(cp,(i,j)):
    "alters cp so that two patch-rows replace the ith one"
    md, q1, q3 = [], [], []
    #
    # Should try to do this with maplist 
    #
    # & We'll probably want a variant to do this to a whole list
    #
    fFactor = 0.41421356
    for c in range(len(cp[0])):
        arc = cp[i-1][c],cp[i][c],cp[i+1][c]
        mid = apply(b2midpoint, arc)
        qt1 = apply(b2qtpoint, arc)
        qt3 = apply(b2qt3point, arc)

        qt11 = b2midcp(cp[i-1][c],qt1, mid)
        qt22 = b2midcp(mid,qt3,cp[i+1][c])

        p0 = cp[i-1][c]
        p1 = cp[i][c]
        p2 = cp[i+1][c]

        qt11x = p0.x*(1-fFactor)+p1.x*fFactor
        qt11y = p0.y*(1-fFactor)+p1.y*fFactor
        qt11z = p0.z*(1-fFactor)+p1.z*fFactor
        qt11 = quarkx.vect((qt11x, qt11y, qt11z) + qt11.st)

        qt22x = p2.x*(1-fFactor)+p1.x*fFactor
        qt22y = p2.y*(1-fFactor)+p1.y*fFactor
        qt22z = p2.z*(1-fFactor)+p1.z*fFactor
        qt22 = quarkx.vect((qt22x, qt22y, qt22z) + qt22.st)

        midx = (qt11x+qt22x)/2
        midy = (qt11y+qt22y)/2
        midz = (qt11z+qt22z)/2
        mid = quarkx.vect((midx, midy, midz) + mid.st)
        md.append(mid)
        q1.append(qt11)
        q3.append(qt22)
    cp[i:i+1] = [q1, md, q3]


def doubleRowsOfQuilt(cp):
    newcp = copyCp(cp)
    for i in range(len(cp)-2,0,-2):
        quilt_addrow(newcp,(i,0))
    return newcp

def quilt_addcol(cp,(i,j)):
    "alters cp so that two patch-rows replace the ith one"
    fFactor = 0.41421356
    for row in cp:
        arc = row[j-1],row[j],row[j+1]

        mid = apply(b2midpoint, arc)
        qt1 = apply(b2qtpoint, arc)
        qt3 = apply(b2qt3point, arc)

        qt11 = b2midcp(arc[0],qt1, mid)
        qt22 = b2midcp(mid,qt3,arc[2])


        p0 = row[j-1]
        p1 = row[j]
        p2 = row[j+1]

        qt11x = p0.x*(1-fFactor)+p1.x*fFactor
        qt11y = p0.y*(1-fFactor)+p1.y*fFactor
        qt11z = p0.z*(1-fFactor)+p1.z*fFactor
        qt11 = quarkx.vect((qt11x, qt11y, qt11z) + qt11.st)

        qt22x = p2.x*(1-fFactor)+p1.x*fFactor
        qt22y = p2.y*(1-fFactor)+p1.y*fFactor
        qt22z = p2.z*(1-fFactor)+p1.z*fFactor
        qt22 = quarkx.vect((qt22x, qt22y, qt22z) + qt22.st)

        midx = (qt11x+qt22x)/2
        midy = (qt11y+qt22y)/2
        midz = (qt11z+qt22z)/2
        mid = quarkx.vect((midx, midy, midz) + mid.st)

        row[j:j+1]=[qt11,mid,qt22]

def doubleColsOfQuilt(cp):
    newcp = copyCp(cp)
    for j in range(len(cp[0])-2,0,-2):
        quilt_addcol(newcp,(0,j))
    return newcp

def quilt_delrow(b2, cp,(i,j)):
    md = []
    for c in range(len(cp[0])):
        arc = cp[i-2][c],cp[i][c],cp[i+2][c]
        mid = apply(b2midcp,arc)
        md.append(mid)
    cp[i-1:i+2]=[md]


def quilt_delcol(b2, cp, (i,j)):
    for row in cp:
        arc=row[j-2],row[j],row[j+2]
        mid = apply(b2midcp,arc)
        row[j-1:j+2]=[mid]


def quilt_cutcol(b2, cp, (i,j)):
    newcp = copyCp(cp)
    for row in newcp:
        row[j+1:] = []

    newb2 = b2.copy()
    newb2.cp = newcp

    for row in cp:
        row[0:j] = []

    return newb2



def quilt_cutrow(b2, cp, (i,j)):
    newcp = copyCp(cp)

    newcp[i+1:] = []

    newb2 = b2.copy()
    newb2.cp = newcp

    cp[0:i] = []

    return newb2


#
# Handles for control points.
#


class CPHandle(qhandles.GenericHandle):
    "Bezier Control point."

    undomsg = Strings[627]
    hint = "reshape bezier patch (Ctrl key: force control point to grid)\n  Alt: move whole row (same hue)\n  Shift: move whole column.\n  Shift+Alt key: move everything.  \n S: shift texture instead.||This is one of the control points of the selected Bezier patch. Moving this control points allows you to distort the shape of the patch. Control points can be seen as 'attractors' for the 'sheet of paper' Bezier patch."

    def __init__(self, pos, b2, ij, color): #DECKER
        qhandles.GenericHandle.__init__(self, pos)
        self.b2 = b2
        self.ij = ij
        self.hint = "(%s,%s)--"%ij+self.hint
        self.color = color #DECKER
        self.cursor = CR_CROSSH
        self.h = len(b2.cp) 
        self.w =  len(b2.cp[0])

    def draw(self, view, cv, draghandle=None):
        if self.ij == (0,0):
            # draw the control point net but only once
            cv.reset()
            self.drawcpnet(view, cv)
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = self.color #DECKER
 #py2.4            cv.rectangle(p.x-3, p.y-3, p.x+4, p.y+4)
            cv.rectangle(int(p.x-3), int(p.y-3), int(p.x+4), int(p.y+4)) #py2.4

            picked=self.b2["picked"]
            if picked is not None:
                i, j = self.ij
                index = i*(self.b2.W)+j
                for test in picked:
                    if test == index:
                        brushstyle = cv.brushstyle
                        cv.pencolor = BLUE
                        cv.brushstyle = BS_CLEAR
 #py2.4                        cv.rectangle(p.x-5, p.y-5, p.x+6, p.y+6)
                        cv.rectangle(int(p.x-5), int(p.y-5), int(p.x+6), int(p.y+6)) #py2.4
                        #cv.brushstyle = brushstyle


    #
    # This is important because in general the derivative
    #  will only be well-defined at corners
    #
    def iscorner(self):
        i, j = self.ij
        if not (i==0 or i==self.b2.H-1):
            return 0
        if not (j==0 or j==self.b2.W-1):
            return 0
        return 1

    def edgeType(self):
        "(type, dim); type=P_FRONT etc"
        "None; not an edge"
        i, j = self.ij
        cp = self.b2.cp
        h = len(cp)
        w = len(cp[0])
        if 0<i<h-1:
            if j==0:
                return P_FRONT, h
            if j==w-1:
                return P_BACK, h 
        if 0<j<w-1:
            if i==0:
                return P_BOTTOM, w
            if i==h-1:
                return P_TOP, w


    #
    # Things that are only sensible for particular control points
    #  should go here, things that are sensible for the whole patch
    #  should go on the BezierType menu update below.
    #

    def menu(self, editor, view):

        i, j = self.ij
        cp = self.b2.cp

        patchmenu = mapentities.CallManager("menu", self.b2, editor)+self.OriginItems(editor, view)

        texcp = qmenu.item("Texture Coordinates",texcpclick, "|Gives the position of the texture on the selected beizer patch.|maped.curves.html#texmanag")
        texcp.h, texcp.editor = self, editor
        texpop = findlabelled(patchmenu,'texpop')
        texpop.items[:0] = [texcp, qmenu.sep]

        def thickenclick(m,self=self,editor=editor):
          new = self.b2.copy()
          #
          # Operating on cp's `in situ' doesn't seem to work.
          #

          ncp = copyCp(new.cp)
          m.thicken(ncp, self.ij)
          #
          # this setting of the cp attribute triggers a lot of stuff
          #   in the delphi
          #
          new.cp = ncp
          undo = quarkx.action()
          undo.exchange(self.b2, new)
          editor.ok(undo,"thicken mesh")

        def thinclick(m,self=self,editor=editor):
          new = self.b2.copy()
          #
          # Operating on cp's `in situ' doesn't seem to work.
          #

          ncp = copyCp(new.cp)
          otherb2 = m.thin(self.b2, ncp, self.ij)
          #
          # this setting of the cp attribute triggers a lot of stuff
          #   in the delphi
          #
          new.cp = ncp
          undo = quarkx.action()
          undo.exchange(self.b2, new)
          if (otherb2 is not None and self.b2.parent is not None):
            undo.put(self.b2.parent, otherb2)
          editor.ok(undo,"thin mesh")


        #
        # We have both add row & column because sometimes an edge
        #  point is hard to find, and for interior points either
        #  would be possible
        #
        addrow = qmenu.item("Add Row",thickenclick,"|Adds a row to the mesh.|maped.curves.html")
        delrow = qmenu.item("Delete Row", thinclick,"|Removes a row from the mesh.|maped.curves.html")
        cutrow = qmenu.item("Cut Bezier By Row", thinclick,"|Cut bezier and create two its parts.|maped.curves.html")
        if iseven(i):
            addrow.state=qmenu.disabled
            delrow.thin=quilt_delrow
            cutrow.thin=quilt_cutrow
        else:
            addrow.thicken=quilt_addrow
            delrow.state=qmenu.disabled
            cutrow.state=qmenu.disabled

        if len(cp)<4 or i==0 or i==len(cp)-1:
            delrow.state=qmenu.disabled
            cutrow.state=qmenu.disabled

        addcol = qmenu.item("Add Column",thickenclick,"|Adds a column to the mesh.|maped.curves.html")
        delcol = qmenu.item("Delete Column",thinclick,"|Removes a column from the mesh.|maped.curves.html")
        cutcol = qmenu.item("Cut Bezier By Column", thinclick,"|Cut bezier and create two its parts.|maped.curves.html")
        if iseven(j):
          addcol.state=qmenu.disabled
          delcol.thin=quilt_delcol
          cutcol.thin=quilt_cutcol
        else:
          addcol.thicken=quilt_addcol
          delcol.state=qmenu.disabled
          cutcol.state=qmenu.disabled
        if len(cp[0])<4 or j==0 or j==len(cp[0])-1:
          delcol.state=qmenu.disabled
          cutcol.state=qmenu.disabled

        def meshclick(m, self=self, editor=editor):
            b2 = self.b2
            new = b2.copy()
            new.cp = m.action(new.cp)
            undo = quarkx.action()
            undo.exchange(b2, new)
            editor.ok(undo, "change mesh")


        doublerow = qmenu.item("Double Rows", meshclick, "|Double the number of rows in the mesh.|maped.curves.html")
        doublerow.action = doubleRowsOfQuilt

        doublecol = qmenu.item("Double Columns", meshclick, "|Double the number of columns in the mesh.|maped.curves.html")
        doublecol.action = doubleColsOfQuilt

        mesh = qmenu.popup("Mesh",[addrow, addcol, delrow, delcol, cutrow, cutcol,
                qmenu.sep, doublerow, doublecol])


        tagpt = gettaggedpt(editor)

        #
        # This should be slated for removal because `glue to tagged'
        # defined in plugins.maptagpoint already does the job (a bit
        # of that ol' Armin magic...
        #
        def glueclick(m, editor=editor,tagpt=tagpt,b2=self.b2,(i,j)=self.ij):
            cp=copyCp(b2.cp)
            if quarkx.keydown('S'):
              cp[i][j]=tagpt
            else:
              cp[i][j] = quarkx.vect(tagpt.xyz+(cp[i][j]).st)
            new = b2.copy()
            new.cp = cp
            undo=quarkx.action()
            undo.exchange(b2, new)
            editor.ok(undo,"glue to tagged")
            editor.invalidateviews()

        glue = qmenu.item("&Glue to tagged point", glueclick,"|Glues the edge of the selected bezier patch to the tagged patch edge and these one into one quilt.|maped.curves.html")
        if tagpt is None:
            glue.state=qmenu.disabled

        def JoinClick(m,self=self, editor=editor):
            b2 = self.b2
            tb2 = m.tagged.b2
    #            ncp = map(lambda row1, row2,b2=b2,tb2=tb2:row1+row2[1:],tb2.cp,b2.cp)
            ncp = joinCp(m.tagtype,tb2.cp,m.selftype,b2.cp)
            new =tb2.copy()
            new.cp = ncp
            undo = quarkx.action()
            undo.exchange(tb2, new)
            undo.exchange(b2,None)
            editor.ok(undo,'Join Patches')
            editor.invalidateviews()

        def KnitClick(m,self=self, editor=editor):
            b2 = self.b2
            tb2 = m.tagged.b2
            ncp = knitCp(m.selftype,b2.cp,m.tagtype,tb2.cp)
            new = b2.copy()
            new.cp = ncp
            undo = quarkx.action()
            undo.exchange(b2, new)
            editor.ok(undo,'Knit edges')
            editor.invalidateviews()

        joinitem = qmenu.item("&Join patch to tagged",JoinClick,"|Combine tagged patch and this one into one quilt.|maped.curves.html")
        knititem = qmenu.item("&Knit edge to tagged",KnitClick,"|Attach this edge to tagged edge.|maped.curves.html")
        joinitem.state=knititem.state=qmenu.disabled
        tagged = gettaggedb2cp(editor)
        for item in joinitem, knititem:
          if tagged is not None:
            tagtype = tagged.edgeType() # orientation, dimension of edge
            selftype = self.edgeType()
            if tagtype is not None and selftype is not None:
                if tagtype[1]==selftype[1]:  # same dim
                    item.state=qmenu.normal
                    item.tagtype, item.selftype = tagtype, selftype
                    item.tagged = tagged
          if item.state==qmenu.disabled:
             morehint = "\n\nTo enable this menu item, tag a non-corner edge point of one patch, and RMB on a non-corner edge point of another"
             item.hint=item.hint+morehint

        tagged = gettaggededge(editor)

        def alignclick(m,self=self,tagged=tagged,editor=editor):
            b2 = self.b2.copy()
            cp = b2.cp
            i, j = self.ij
            norm = (tagged[1]-tagged[0]).normalized
            p = cp[i][j]
            #
            # operating on cp's of b2's tends not to work; make a copy
            #
            cp2 = copyCp(cp)
            if m.col:
                for k in range(len(cp)):
                    delta = perptonormthru(cp[k][j], p, norm)
                    delta = quarkx.vect(delta.xyz+(0.0, 0.0))
                    cp2[k][j] = cp2[k][j]-delta
                    mess = "align column"
            else:
                for k in range(len(cp[0])):
                    delta = perptonormthru(cp[i][k], p, norm)
                    delta = quarkx.vect(delta.xyz+(0.0, 0.0))
                    cp2[i][k] = cp2[i][k]-delta
                    mess = "align row"
            b2.cp = cp2
            undo_exchange(editor,self.b2,b2,mess)

        alignrow = qmenu.item('Align Row to tagged edge',alignclick,"|Aligns the row to paralell to tagged edge, passing thru this point.|maped.curves.html")
        aligncol = qmenu.item('Align Col to tagged edge',alignclick,"|Aligns the column to paralell to tagged edge, passing thru this point.|maped.curves.html")
        if tagged is None:
            alignrow.state=qmenu.disabled
            aligncol.state=qmenu.disabled
        else:
            alignrow.col=0
            aligncol.col=1

    #
    # not sure why this was here, testing perhaps?
    #
    #        def subdivide(m,self=self,editor=editor):
    #            cp = copyCp(self.b2.cp)
    #            new = self.b2.copy()
    #            newcp = subdivideColumns(3,cp)
    #            new.cp = newcp
    #            undo=quarkx.action()
    #            undo.exchange(self.b2, new)
    #            editor.ok(undo,"subdivide")
    #
    #        subdiv = qmenu.item("subdivide",subdivide,"|Splits up the bezier mesh.|maped.curves.html")
    #        return [texcp, thicken] + [qmenu.sep] + mapentities.CallManager("menu", self.b2, editor)+self.OriginItems(editor, view)

        index = i*(self.b2.W)+j
        picked=self.b2["picked"] 

        def pickClick(m,editor=editor,b2=self.b2,index=index, picked=picked):
            if picked is None:
                picked = index,
            else:
                picked = picked + (index,)
            undo=quarkx.action()
            undo.setspec(b2,"picked",picked)
            editor.ok(undo,"Pick CP")

        def unPickClick(m,editor=editor,b2=self.b2,index=index, picked=picked):
            if len(picked)==1:
                picked=None
            else:
                loc = list(picked).index(index)
                picked = picked[:loc]+picked[loc+1:]
            undo=quarkx.action()
            undo.setspec(b2,"picked",picked)
            editor.ok(undo,"Unpick CP")

        def pickRowClick(m,editor=editor,b2=self.b2,index=index, picked=picked):
            for iRow in range(b2.W):
                newindex = i*(self.b2.W)+iRow
                if picked is None:
                    picked = newindex,
                else:
                    bFound = 0
                    for ind in picked:
                        if ind==newindex:
                            bFound = 1
                            break
                    if bFound == 0:
                        picked = picked + (newindex,)
            undo=quarkx.action()
            undo.setspec(b2,"picked",picked)
            editor.ok(undo,"Pick Row")

        def unPickRowClick(m,editor=editor,b2=self.b2,index=index, picked=picked):
            newpicked = None
            for ind in picked:
                found = 0
                for iRow in range(b2.W):
                    newindex = i*(self.b2.W)+iRow
                    if ind==newindex:
                        found = 1
                        break
                if found == 0:
                    if newpicked is None:
                        newpicked = (int(ind),)
                    else:
                        newpicked = newpicked + (int(ind),)
            undo=quarkx.action()
            undo.setspec(b2,"picked", newpicked)
            editor.ok(undo,"Unpick Row")

        def pickColClick(m,editor=editor,b2=self.b2,index=index, picked=picked):
            for iCol in range(b2.H):
                newindex = iCol*(self.b2.W)+j
                if picked is None:
                    picked = newindex,
                else:
                    bFound = 0
                    for ind in picked:
                        if ind==newindex:
                            bFound = 1
                            break
                    if bFound == 0:
                        picked = picked + (newindex,)
            undo=quarkx.action()
            undo.setspec(b2,"picked",picked)
            editor.ok(undo,"Pick Col")

        def unPickColClick(m,editor=editor,b2=self.b2,index=index, picked=picked):
            newpicked = None
            for ind in picked:
                found = 0
                for iCol in range(b2.W):
                    newindex = iCol*(self.b2.W)+j
                    if ind==newindex:
                        found = 1
                        break
                if found == 0:
                    if newpicked is None:
                        newpicked = (int(ind),)
                    else:
                        newpicked = newpicked + (int(ind),)
            undo=quarkx.action()
            undo.setspec(b2,"picked", newpicked)
            editor.ok(undo,"Unpick Col")

        def pickAllClick(m,editor=editor,b2=self.b2):
            picked = None
            for index in range(b2.W*b2.H):
                if picked is None:
                    picked = index,
                else:
                    picked = picked + (index, )

            undo=quarkx.action()
            undo.setspec(b2,"picked", picked)
            editor.ok(undo,"Pick All")
            editor.invalidateviews()

        def unPickAllClick(m,editor=editor,b2=self.b2):
            undo=quarkx.action()
            undo.setspec(b2,"picked",None)
            editor.ok(undo,"Unpick All")
            editor.invalidateviews()

        pickItem = qmenu.item("Pick CP", pickClick,"|When one or more CPs are picked `picked', dragging one of them drags all, and movement palette operations applied to a patch are applied only to the picked CPs.\n\nPatches remember which of their CPs are picked.|maped.curves.html")
        unPickItem = qmenu.item("Unpick CP", unPickClick, "|Unselects a specific selected bezier control point.|maped.curves.html")

        pickRowItem = qmenu.item("Pick Ro&w", pickRowClick, "|Selects the entire row that the control point is in.|maped.curves.html")
        unPickRowItem = qmenu.item("Unpick Ro&w", unPickRowClick, "|Unselects the entire row that the control point is in.|maped.curves.html")

        pickColItem = qmenu.item("Pick Col&umns", pickColClick, "|Selects the entire column that the control point is in.|maped.curves.html")
        unPickColItem = qmenu.item("Unpick Col&umns", unPickColClick, "|Unselects the entire column that the control point is in.|maped.curves.html")

        pickAllItem = qmenu.item("Pick All", pickAllClick, "|Selects all control points.|maped.curves.html")
        unPickAllItem = qmenu.item("Unpick All", unPickAllClick, "|Unselects all control points.|maped.curves.html")

        picklist = [qmenu.sep]
        found = 0
        if picked is not None:
            for ind in picked:
                if ind==index:
                    picklist = picklist + [unPickItem]
                    found = 1
                    break
        if found == 0:
            picklist = picklist + [pickItem]

        found = 0
        if picked is not None:
            for iRow in range(self.b2.W):
                newindex = i*(self.b2.W)+iRow
                for ind in picked:
                    if ind==newindex:
                        found = found + 1
                        break

        if found < self.b2.W:
            picklist = picklist + [pickRowItem]

        if found > 0:
            picklist = picklist + [unPickRowItem]

        found = 0
        if picked is not None:
            for iCol in range(self.b2.H):
                newindex = iCol*(self.b2.W)+j
                for ind in picked:
                    if ind==newindex:
                        found = found + 1
                        break

        if found < self.b2.H:
            picklist = picklist + [pickColItem]

        if found > 0:
            picklist = picklist + [unPickColItem]


        if picked is None or len(picked) < self.b2.W*self.b2.H:
            picklist = picklist + [pickAllItem]

        if picked is not None:
            picklist = picklist + [unPickAllItem]

        #picklist = [qmenu.sep, pickItem, unPickItem, unPickAllItem]

        return [mesh, joinitem, knititem, alignrow, aligncol] + picklist+[qmenu.sep] + patchmenu

    def drawcpnet(self, view, cv, cp=None):
        #
        # This function draws the net joining the control points in a selected patch
        #
        if cp is None:
            cp = self.b2.cp
        #
        # Project all control points using view.proj
        #
        cp = map(lambda cpline, proj=view.proj: map(proj, cpline), cp)
        #
        # Draw the horizontal lines
        #
        for cpline in cp:
            for j in range(len(cpline)-1):
                cv.line(cpline[j], cpline[j+1])
        #
        # Transpose the "cp" matrix and draw the vertical lines
        #
        cp = apply(map, (None,)+tuple(cp))
        for cpline in cp:
            for i in range(len(cpline)-1):
                cv.line(cpline[i], cpline[i+1])

    def drawred(self, redimages, view, redcolor, oldcp=None):
        #
        # Draw a rough net joining all control points while dragging one of them.
        #
        if oldcp is None:
            try:
                oldcp = self.newcp
            except AttributeError:
                return
            if oldcp is None:
                return
        cv = view.canvas()
        cv.pencolor = redcolor
        #
        # Draw the net
        #
        self.drawcpnet(view, cv, oldcp)
        return oldcp

    # converting to standard ij
    def drag(self, v1, v2, flags, view):
        delta = v2-v1
        if not (flags&MB_CTRL):
            delta = qhandles.aligntogrid(delta, 0)
        if delta or (flags&MB_REDIMAGE):
            new = self.b2.copy()
            cp = map(list, self.b2.cp)
            i, j = self.ij
            moverow = (quarkx.keydown('\022')==1)  # ALT
            movecol = (quarkx.keydown('\020')==1)  # SHIFT
            picked = self.b2["picked"]
            if picked:
                indexes = map(lambda p,b2=self.b2:cpPos(p,b2),picked)
            else:
                indexes = pointsToMove(moverow, movecol, i, j, self.h, self.w)        # tiglari, need to unswap 
    #            squawk(`indexes`)
            td = (v2-v1)/128
            for m,n in indexes:
                p = cp[m][n] + delta
                if flags&MB_CTRL:
                    p = qhandles.aligntogrid(p, 0)
                if quarkx.keydown('S')==1: # RMB
                    xaxis, yaxis = tanAxes(cp,i,j)
                    xaxis, yaxis = -xaxis, -yaxis
                    q = cp[m][n]
                    cp[m][n]=quarkx.vect(q.x, q.y, q.z,
                              q.s+td*yaxis, q.t+td*xaxis)
                else:
                   cp[m][n] = quarkx.vect(p.x, p.y, p.z)  # discards texture coords
    #            if 0:
            if quarkx.keydown('S')==1:
                    self.draghint="tex coords: %.2f, %.2f"%(cp[i][j].s, cp[i][j].t)
            else:
                    self.draghint = vtohint(delta)
            if self.b2["smooth"]:
                # keep the patch smoothness
                def makesmooth(di,dj,i=i,j=j,cp=cp):
                    p = 2*cp[i+di][j+dj] - cp[i][j]
                    cp[i+di+di][j+dj+dj] = quarkx.vect(p.x, p.y, p.z)  # discards texture coords
                if j&1:
                    if j>2: makesmooth(0,-1)
                    if j+2<len(cp[0]): makesmooth(0, 1)
                if i&1:
                    if i>2: makesmooth(-1,0)
                    if i+2<len(cp): makesmooth(1,0)
            new.cp = self.newcp = cp
            new = [new]
        else:
            self.newcp = None
            new = None
        return [self.b2], new

class CPTextureHandle(qhandles.GenericHandle):
    "Bezier Control point (Texture Handle)."

    undomsg = Strings[627]
    hint = "re-position texture vertexes (Ctrl key: force control point to grid)\n  Alt: move whole row (same hue)\n  Shift: move whole column.\n  Shift+Alt key: move everything.  \n S: shift texture instead.||This is one of the control points of the selected Bezier patch. Moving this control points allows you to distort the shape of the patch. Control points can be seen as 'attractors' for the 'sheet of paper' Bezier patch."

    def __init__(self, pos, b2, ij, color): #DECKER
        qhandles.GenericHandle.__init__(self, pos)
        self.b2 = b2
        self.ij = ij
        self.hint = "(%s,%s)--"%ij+self.hint
        self.color = color #DECKER
        self.cursor = CR_CROSSH
        self.h = len(b2.cp) 
        self.w =  len(b2.cp[0])

    def draw(self, view, cv, draghandle=None):
        if self.ij == (0,0):
            cv.reset()
            #self.drawcpnet(view, cv)
        p = view.proj(self.pos)
        if p.visible:
            cv.reset()
            cv.brushcolor = self.color #DECKER
 #py2.4            cv.rectangle(p.x-3, p.y-3, p.x+4, p.y+4)
            cv.rectangle(int(p.x-3), int(p.y-3), int(p.x+4), int(p.y+4)) #py2.4

    #
    # This is important because in general the derivative
    #  will only be well-defined at corners
    #
    def iscorner(self):
        i, j = self.ij
        if not (i==0 or i==self.b2.H-1):
            return 0
        if not (j==0 or j==self.b2.W-1):
            return 0
        return 1

    def edgeType(self):
        "(type, dim); type=P_FRONT etc"
        "None; not an edge"
        i, j = self.ij
        cp = self.b2.cp
        h = len(cp)
        w = len(cp[0])
        if 0<i<h-1:
            if j==0:
                return P_FRONT, h
            if j==w-1:
                return P_BACK, h 
        if 0<j<w-1:
            if i==0:
                return P_BOTTOM, w
            if i==h-1:
                return P_TOP, w            

    # converting to standard ij
    def drag(self, v1, v2, flags, view):
        delta = v2-v1
        if not (flags&MB_CTRL):
            delta = qhandles.aligntogrid(delta, 0)
        if delta or (flags&MB_REDIMAGE):
            new = self.b2.copy()
            cp = map(list, self.b2.cp)
            i, j = self.ij
            moverow = (quarkx.keydown('\022')==1)  # ALT
            movecol = (quarkx.keydown('\020')==1)  # SHIFT
            picked = self.b2["picked"]
            if picked:
                indexes = map(lambda p,b2=self.b2:cpPos(p,b2),picked)
            else:
                indexes = pointsToMove(moverow, movecol, i, j, self.h, self.w)        # tiglari, need to unswap 
            td = (v2-v1)/128
            for m,n in indexes:
                 q = cp[m][n]
                 cp[m][n]=quarkx.vect(q.x, q.y, q.z, q.s + delta.x, q.t + delta.y)
            self.draghint = vtohint(delta)
            new.cp = self.newcp = cp
            new = [new]
        else:
            self.newcp = None
            new = None
        return [self.b2], new

#
# getting tag point to actually tag the bezier control point.
#
def tagB2CpClick(m):
    import qeditor
    editor = qeditor.mapeditor()
    if editor is None: return
    tagb2cp(m.o, editor)

def originmenu(self, editor, view, oldoriginmenu = quarkpy.qhandles.GenericHandle.OriginItems.im_func):
  menu = oldoriginmenu(self, editor, view)
  if isinstance(self, CPHandle):
      for item in menu:
          try:
              if item.tagger:
                  item.onclick = tagB2CpClick
                  item.o = self
          except (AttributeError):
              pass
  return menu

quarkpy.qhandles.GenericHandle.OriginItems = originmenu

#
# Stuff that's meaningful for the whole patch should go here
#
def newb2menu(o, editor, oldmenu=mapentities.BezierType.menubegin.im_func):
    "update for RMB menu for beziers"


    def projtexclick(m, o=o, editor=editor):
        new = o.copy()
        texFromFaceToB2(new, m.tagged, editor)
        undo = quarkx.action()
        undo.exchange(o, new)
        editor.ok(undo,"project texture from tagged")

    projtex = qmenu.item("&Project from tagged", projtexclick, "|Texture of a tagged face is projected onto the patch in a `flat' way (just like project texture from tagged face onto faces).|maped.curves.html#texmanag")
    tagged = gettaggedface(editor)
    if tagged is None:
       projtex.state=qmenu.disabled
    else:
       projtex.tagged = tagged

    def rotclick(m, o=o, editor=editor):
        ncp = RotateCpCounter(1,o.cp)
        new = o.copy()
        new.cp = ncp
        undo=quarkx.action()
        undo.exchange(o, new)
        editor.ok(undo,"Spin")
        editor.invalidateviews()

    rotate = qmenu.item("Rotate",rotclick,"|`Rotates' control points without changeing patch shape\n(I'm not sure if it's useful on its own but it helps in the implementation of some things so here it is anyway.)|maped.curves.html")

    def unwarpclick(m,o=o,editor=editor):
        new=o.copy()
        new.cp = undistortColumns(undistortRows(o.cp))
        undo=quarkx.action()
        undo.exchange(o, new)
        editor.ok(undo,"unwarp")

    def unwarpclickB(m,o=o,editor=editor):
        new=o.copy()
        new.cp = undistortColumnsCaseB(undistortRowsCaseB(o.cp))
        undo=quarkx.action()
        undo.exchange(o, new)
        editor.ok(undo,"unwarpEx")

    def UniformWrapClick(m,o=o,editor=editor):
        new=o.copy()
        new.cp = UniformWrapCollumns(UniformWrapRows(o.cp))
        undo=quarkx.action()
        undo.exchange(o, new)
        editor.ok(undo,"UniformWrap")

    unwarp = qmenu.item("Unwarp", unwarpclick, "|Tries to reduce texture scale changes within the selected bezier patch, keeping corner points the same.|maped.curves.html#texmanag")
    unwarpEx = qmenu.item("UnwarpEx", unwarpclickB, "|Unwraps the texture shown on the selected bezier patch.|maped.curves.html#texmanag")
    UniformWrap = qmenu.item("UniformWrap", UniformWrapClick, "|Uniformly wraps the texture on the selected bezier patch.|maped.curves.html#texmanag")

    def cornertexclick(m,o=o,editor=editor):

        class pack:
            "a place to stick stuff"
        pack.o=o
        pack.fixed=""

        def reset(self, pack=pack):
            cp = pack.o.cp
            m = len(cp)-1
            n = len(cp[0])-1

            one = cp[0][0].s, cp[0][0].t, cp[m][n].s, cp[m][n].t
            two = cp[m][0].s, cp[0][n].t, cp[0][n].s ,cp[m][0].t
#            squawk("1: %s; 2: %s"%(one, two))
            if one==two:
                self.src["Corners"] = cp[0][0].s, cp[0][0].t, cp[m][n].s, cp[m][n].t,
            else:
                self.src["Corners"] = None
            pack.oldcnr = self.src["Corners"]

        def setup(self, pack=pack, reset=reset):
            src=self.src
            cp = pack.o.cp
            m = len(cp)-1
            n = len(cp[0])-1
            src["Corner1"]=cp[0][0].s, cp[0][0].t
            src["Corner2"]=cp[0][n].s, cp[0][n].t
            src["Corner3"]=cp[m][0].s, cp[m][0].t
            src["Corner4"]=cp[m][n].s, cp[m][n].t
            reset(self)

        def action(self, pack=pack, reset=reset):
            src = self.src
            new = pack.o.copy()
            cp = listCp(new.cp)
            m = len(cp)-1
            n = len(cp[0])-1
            st = range(4)
            if src["Corners"]!=pack.oldcnr:
                cnr = src["Corners"]
                src["Corner1"] = cnr[0], cnr[1]
                src["Corner2"] = cnr[2], cnr[1]
                src["Corner3"] = cnr[0], cnr[3]
                src["Corner4"] = cnr[2], cnr[3]
            st[0]= src["Corner1"]
            st[1]= src["Corner2"]
            st[2]= src["Corner3"]
            st[3]= src["Corner4"]
            cnrs = range(4)
            for (i, j, k) in ((0,0,0),(0,n,1),(m,0,2),(m,n,3)):
                cp[i][j]=quarkx.vect(cp[i][j].xyz+st[k])
                cnrs[k] = cp[i][j]
#            if src["fixed"]:
            if 0:
                cp2 = apply(interpolateGrid,cnrs+[len(cp),len(cp[0])])
                cp = texcpFromCp(cp, cp2)
            else:
                cp = undistortColumns(undistortRows(cp))
            new.cp=cp
            undo=quarkx.action()
            undo.exchange(pack.o, new)
            self.editor.ok(undo,"corners")
            pack.o = new
            reset(self)

        CornerTexPos(quarkx.clickform,'cornertexpos',editor,setup,action)

    cornertex = qmenu.item("Position by &corners",cornertexclick,"|A dialog for positioning textures by specifying the texture coordinates of the corners of the selected bezier patch.|maped.curves.html#texmanag")


    old = oldmenu(o, editor)
    texpop = findlabelled(old,'texpop')

    texpop.items = texpop.items + [projtex, cornertex, unwarp, unwarpEx, UniformWrap]

    return old+[rotate]

mapentities.BezierType.menubegin = newb2menu

#
# Handle for the center of a Bezier patch.
#

class CenterHandle(maphandles.CenterHandle):
    "Bezier center."

    def __init__(self, pos, centerof):
        ##c_x = quarkx.setupsubset(SS_MAP, "Building")["BezierCenterX"][0]
        ##c_y = quarkx.setupsubset(SS_MAP, "Building")["BezierCenterY"][0]
        ##pos = quarkx.vect(pos.x + c_x, pos.y+c_y, pos.z)
        maphandles.CenterHandle.__init__(self, pos, centerof, 0x202020, 1)

    # tiglari
    def menu(self, editor, view):

        return mapentities.CallManager("menu", self.centerof, editor)
    # /tiglari

import mapeditor
from plugins.tagging import drawsquare
def pickfinishdrawing(editor, view, oldmore=mapeditor.MapEditor.finishdrawing):
    cv = view.canvas()
    cv.pencolor = MapColor("Duplicator")
    for item in editor.layout.explorer.sellist:
        if item.type==":b2" and item["picked"] is not None:
            cp = item.cp
            for p in item["picked"]:
                i, j = cpPos(p, item)
                p1 = view.proj(cp[i][j])
                drawsquare(cv,p1,10)
    oldmore(editor,view)

mapeditor.MapEditor.finishdrawing = pickfinishdrawing


# ----------- REVISION HISTORY ------------
#$Log: mapbezier.py,v $
#Revision 1.45  2008/05/25 21:02:46  cdunde
#Dans fix for the tagging.
#
#Revision 1.44  2008/02/22 09:52:24  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.43  2007/12/14 22:30:53  cdunde
#Minor corrections of new Infobase links.
#
#Revision 1.42  2007/12/14 21:48:00  cdunde
#Added many new beizer shapes and functions developed by our friends in Russia,
#the Shine team, Nazar and vodkins.
#
#Revision 1.41  2006/11/30 01:19:34  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.40  2006/11/29 07:00:29  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.39.2.2  2006/11/23 20:04:06  danielpharos
#Very small clean-up of the header
#
#Revision 1.39.2.1  2006/11/03 23:38:09  cdunde
#Updates to accept Python 2.4.4 by eliminating the
#Depreciation warning messages in the console.
#
#Revision 1.39  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.36  2001/06/17 21:05:27  tiglari
#fix button captions
#
#Revision 1.35  2001/06/16 03:20:48  tiglari
#add Txt="" to separators that need it
#
#Revision 1.34  2001/02/07 18:40:47  aiv
#bezier texture vertice page started.
#
#Revision 1.33  2001/01/15 21:56:29  tiglari
#remove useless `subdiv' menu item (old test code, methinks).
#`picking' extended to drag (drag one picked CP now drags all)
#
#Revision 1.32  2000/12/30 05:28:19  tiglari
#`pick' functions for acting on selected bezier cp's
#
#Revision 1.31  2000/08/23 12:13:53  tiglari
#added knit edge RMB for patches; also double rows/columns
#
#Revision 1.30  2000/07/30 23:03:51  tiglari
#align row/column to tagged edge added; glue to tagged removed,
#since the one in plugins.maptagpoint already does the job.
#
#Revision 1.29  2000/07/29 01:12:14  alexander
#fixed: copycp ->copyCp (texture coordinate pyton crash AGAIN :)
#
#Revision 1.28  2000/07/26 11:36:01  tiglari
#menu reorganization (one texture popup)
#
#Revision 1.26  2000/07/24 13:00:02  tiglari
#reorganization of bezier texture menu, added a new positioning item, `texture at corners'.  Also a sort of `rotation' of control points.
#
#Revision 1.25  2000/07/23 08:43:17  tiglari
#project texture to tagged plane removed from bezier cp menu
#(functionality now in project tex. from tagged for faces)
#
#Revision 1.24  2000/07/16 07:58:11  tiglari
#bezier menu -> menubegin; mesh thinning
#
#Revision 1.23  2000/07/04 11:04:23  tiglari
#fixed patch thicken bug (copycp->copyCp)
#
#Revision 1.22  2000/06/26 22:51:55  tiglari
#renaming: antidistort_rows/columns->undistortRows/Colunmns,
#tanaxes->tanAxes, copy/map/transposecp->copy/map/transposeCP
#
#Revision 1.21  2000/06/25 23:48:02  tiglari
#Function Renaming & Reorganization, hope no breakage
#
#Revision 1.20  2000/06/14 21:19:39  tiglari
#texture coord entry dialog fixes, drag hint shows texture coords when texture is dragged
#
#Revision 1.19  2000/05/29 21:43:08  tiglari
#Project texture to tagged added
#
#Revision 1.18  2000/05/26 23:12:34  tiglari
#More patch manipulation facilities
#
#Revision 1.17  2000/05/19 10:08:09  tiglari
#Added texture projection, redid some bezier utilties
#
#Revision 1.16  2000/05/08 11:12:19  tiglari
#fixed problems with keys for bezier cp movement
#

