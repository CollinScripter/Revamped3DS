# QuArK  -  Quake Army Knife
#
# Copyright (C) 2001 The Quark Community
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/maplinedit.py,v 1.8 2005/10/15 00:49:51 cdunde Exp $
 
Info = {
   "plug-in":       "Linear Matrix Editor",
   "desc":          "Edit matrix in linear specific",
   "date":          "10 May 2001",
   "author":        "tiglari",
   "author e-mail": "tiglari@planetquake.com",
   "quark":         "Quark 6.2" }


import quarkx
from quarkpy.maputils import *
import quarkpy.qmacro
import quarkpy.dlgclasses
from quarkpy.qdictionnary import Strings
from quarkpy.qeditor import matrix_rot_x
from quarkpy.qeditor import matrix_rot_y
from quarkpy.qeditor import matrix_rot_z


class LinEditDlg (quarkpy.dlgclasses.LiveEditDlg):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (180,200)
    dfsep = 0.45

    dlgdef = """
        {
            Style = "9"
        Caption = "Linear Mapping Edit Dialog"

        scale: = 
        {
        Txt = "Scale"
        Typ = "EF003"
        Hint = "Scale X, Y, Z dimensions"
        }

        sep: = {Typ="S" Txt=" "} 

        angles: =
        {
        Txt = "Angles"
        Typ = "EF003"
        Hint = "Pitch, Yaw, Roll angles (rotations around Y, Z, X" $0D " axes, in order"
        }

        sep: = {Typ="S" Txt=" "}
        
        mirror: = {
        Txt = "Mirror"
        Typ = "X"
        Hint = "Mirror in XZ plane.  Mirror effects can also be produced" $0D " with negative scale values"
        }
       
        sep: = {Typ="S" Txt=" "} 
        
        shear: = {
        Txt = "Shear"
        Typ = "EF003"
        Hint = "Shear angles: Z crunch (toward X axis),"$0D " Y-lift (out of XY plane), Y-twist (from Y-axis orientation)" $0D " For mirror-image, set Y-twist to 180"
        }
      
        sep: = { Typ="S" Txt=""}

        exit:py = {Txt="" }
    }
    """

def macro_linedit(self):
    editor = mapeditor()
    if editor is None:
        quarkx.msgbox('Unfortunately, you need to reselect me in the tree-view',
           MT_INFORMATION,MB_OK)
        return

    sel = editor.layout.explorer.uniquesel
    if sel is None:
        squawk("very wierd, no selection")
        return

    class pack:
        "just a place to stick stuff"
    pack.sel = sel

    axes = quarkx.matrix('1 0 0 0 1 0 0 0 1').cols

    def setup(self, pack=pack, axes=axes):
        pass
        src = self.src
        sel = pack.sel
        linear = sel["linear"]
        if linear is None:
            linear = '1 0 0 0 1 0 0 0 1'
        linear = quarkx.matrix(linear)
        pack.linear = linear
        cols = linear.cols
        #
        # get scale
        #
        src["scale"]=tuple(map(lambda v:abs(v), cols))
        cols = tuple(map(lambda v:v.normalized, cols))    
        #
        # get rotations, cols[0] is 'rotated X axis, compute the others
        #
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
        src["angles"] = pitch/deg2rad, yaw/deg2rad, roll/deg2rad

        mat = matrix_rot_z(yaw)*matrix_rot_y(pitch)*matrix_rot_x(roll)

        cols = map(lambda v, mat=mat:~mat*v,cols)
        
#        cols = quarkx.matrix('1 0 0 0 1 0 0 0 1').cols
        #
        # Now get shear info (the cols have been rotated into
        #   'canonical' position)
        #
        zxshear = math.asin(cols[0]*cols[2])
        ylift = math.asin(axes[2]*cols[1])
        p = projectpointtoplane(cols[1],axes[2],quarkx.vect(0,0,0),axes[2]).normalized
        ytwist = math.atan2(p*axes[0], p*axes[1])
        if ytwist > math.pi/2:
            src["mirror"] = 1
            ytwist = math.pi-ytwist
        src["shear"] = zxshear/deg2rad, ylift/deg2rad, ytwist/deg2rad
        

    def action(self, pack=pack, editor=editor):
        src = self.src
        zxshear, ylift, ytwist = tuple(map(lambda x:x*deg2rad, src["shear"]))
        if src["mirror"]:
            ytwist = math.pi-ytwist
#        debug('yt '+`ytwist/deg2rad`)
        colz = matrix_rot_y(-zxshear)*quarkx.vect(0,0,1)
        coly = matrix_rot_x(ylift)*matrix_rot_z(-ytwist)*quarkx.vect(0,1,0)
        cols = quarkx.vect(1,0,0), coly, colz
        scale = src["scale"]
        cols = map(lambda v,s:s*v, cols, scale)
        angles = src["angles"]
        pitch, yaw, roll = tuple(map(lambda a:a*deg2rad, angles))

        mat = matrix_rot_z(yaw)*matrix_rot_y(pitch)*matrix_rot_x(roll)
                
        cols = map(lambda v,mat=mat:mat*v, cols)


        #
        # apply change  
        #
        linear = str(quarkx.matrix(cols[0],cols[1],cols[2]))
        undo = quarkx.action()
        if linear == '1 0 0 0 1 0 0 0 1':
            linear = None
        undo.setspec(pack.sel, 'linear', linear)
        editor.ok(undo,"Set matrix scale")
        

    LinEditDlg(quarkx.clickform, 'linedit', editor, setup, action)
        
    
    
quarkpy.qmacro.MACRO_linedit = macro_linedit

#$Log: maplinedit.py,v $
#Revision 1.8  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.5  2001/06/17 21:10:57  tiglari
#fix button captions
#
#Revision 1.4  2001/06/16 03:29:36  tiglari
#add Txt="" to separators that need it
#
#Revision 1.3  2001/05/12 18:57:36  tiglari
#add Mirror checkbox
#
#Revision 1.2  2001/05/12 12:24:23  tiglari
#add rotate & shear
#
#Revision 1.1  2001/05/11 09:39:41  tiglari
#kickoff with scale
#

    