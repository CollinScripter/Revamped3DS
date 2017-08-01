#-------------------------------------------------------------------------------
#      Module:         mapmakeprism.py
#      Subsystem:      mapmakeprism
#      Program:        mapmakeprism
#      Copyright (c) 1998 - Descartes Systems Sciences
#
# Code review:
#
# tiglari's remarks on some suggested code changes, prefaced by tig:
#
#
#-------------------------------------------------------------------------------
# $Header: /cvsroot/quark/runtime/plugins/mapmakeprism.py,v 1.14 2005/10/15 00:49:51 cdunde Exp $

Info = {
   "plug-in":       "Make n sided prism",
   "desc":          "Make an n sided prism from user supplied specs",
   "date":          "2000.06.??",
   "author":        "ax2grind",
   "author e-mail": "ax2grind@altavista.com",
   "original author":        "Tim Smith",
   "original author e-mail": "etsmith@mindspring.com",
   "quark":         "Version 6.x"
}


import quarkpy.qmenu
import math
import quarkx
import quarkpy.qmacro
import quarkpy.qtoolbar
import quarkpy.mapsearch
import quarkpy.mapbtns
from quarkpy.maputils import *
import mapsearch1


class MakePrismDlg(quarkpy.qmacro.dialogbox):
    # Dialog layout
    size = (290, 322)
    dfsep = 0.4     # separation at 40% between labels and edit boxes
    dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE

    dlgdef = """
        {
            Style = "15"
            Caption = "Make an N-Sided Prism"

            tex: =
            {
                Txt = "Prism texture:"
                Typ = "ET"
                SelectMe = "1"
            }

            vertex: =
            {
                Typ = "X"
                Txt = "Start prism..."
                Cap = "on a vertex"
            }

            sides: =
            {
                Txt = "Number of sides"
                Typ = "EF1"
                Min = '5'
            }

            radius: =
            {
                Txt = "Radius of prism"
                Typ = "EF"
                Hint = "Distance(s) from center to outside edge."
                 $0D$0D"There are four ways of specifying the radius:"
                    $0D"'<r>' - The same radius all over"
                    $0D"'<x> <y>' - X-axis and Y-axis radiuses"
                    $0D"'<lx> <ly> <ur>' - Lower X/Y-axis radiuses, and Upper radius"
                    $0D"'<lx> <ly> <ux> <uy>' - Lower X/Y-axis radiuses, and Upper X/Y-axis radiuses"
                 $0D$0D"Examples:"
                    $0D"'128' - Will give a uniform cylinder, 128 units in radius"
                    $0D"'128 64' - Will give an oval cylinder, 128 X-radius and 64 Y-radius"
                    $0D"'128 64 96' - Will give an oval cylinder at the bottom, and a uniform cylinder at the top"
                    $0D"'128 64 64 128' - Will give an oval cylinder at the bottom, and the same at top but twisted"
            }

            hollow: =
            {
                Txt = "Hollow of prism"
                Typ = "EF"
                Hint = "Distance(s) from center to inside edge."
                    $0D"Must be zero or lower than the 'Radius of prism' values,"
                    $0D"and 'Pie-slices' must be marked for hollow to have any effect."
                 $0D$0D"If any of the values are negative, they will be subtracted"
                    $0D"from the 'Radius', and used as inner-radius."
                 $0D$0D"The same four ways of specifying the radius, apply to"
                    $0D"this, as with 'Radius of prism'."
            }

            height: =
            {
                Txt = "Height of prism"
                Typ = "EF1"
            }

            offset: =
            {
                Txt = "Slant of prism"
                Typ = "EF"
                Hint = "X- and Y-offset between the lower- and upper-centerpart of the cylinder"
                 $0D$0D"Examples:"
                    $0D"'0' - No slant/skew/offset of the prism"
                    $0D"'+64' - Offset the upper-centerpart of the cylinder by; (64,64)"
                    $0D"'+32 -16' - Offset the upper-centerpart of the cylinder by; (32,-16)"
            }

            gridsize: =
            {
                Txt = "Size of grid"
                Typ = "EF1"
                Hint = "Vertices aligned to this grid."
            }

            slice: =
            {
                Typ = "X"
                Txt = "Pie-slices"
                Cap = "Yes, make me some slices"
            }

            shareface: =
            {
                Typ = "X"
                Txt = "Share Faces"
                Cap = "Yes, Top and Bottom"
            }

            stair: =
            {
                Typ = "X"
                Txt = "Staircase:"
                Cap = "Yes, make me some stairs."
            }

            ramp: =
            {
                Typ = "X"
                Txt = "Ramp:"
                Cap = "Yes, make me a ramp."
            }



            sep: = { Typ ="S" Txt=""}

            MakePrism:py = {Txt="" }

            close:py = {Txt="" }
        }
    """

    def __init__(self, form, editor):
        # General initialization of some local values
        self.editor = editor
        self.sellist = self.editor.visualselection()

        # Create the data source
        src = quarkx.newobj(":")

        # Based on the textures in the selections, initialize the from and to textures
        texlist = quarkx.texturesof(editor.layout.explorer.sellist)
        if len(texlist) == 1:
            src["tex"] = texlist[0]
        else:
            src["tex"] = quarkx.setupsubset()["DefaultTexture"]

        # Populate the other values
        if (quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Sides"] is None):
            src["vertex"]      = ""
            src["sides"]       = 6,
            src["radius"]      = 64, 64, 64, 64,
            src["hollow"]      = 0, 0, 0, 0,
            src["height"]      = 128,
            src["offset"]      = 0, 0,
            src["gridsize"]    = 0,
            src["slice"]       = ""
            src["shareface"]   = ""
            src["stair"]       = ""
            src["ramp"]        = ""
        else:
            src["vertex"]      = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Vertex"]
            src["sides"]       = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Sides"]
            src["radius"]      = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Radius"]
            src["hollow"]      = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Hollow"]
            src["height"]      = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Height"]
            src["offset"]      = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Offset"]
            src["gridsize"]    = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Gridsize"]
            src["slice"]       = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Slice"]
            src["shareface"]   = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Shareface"]
            src["stair"]       = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Stair"]
            src["ramp"]        = quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Ramp"]

        # Create the dialog form and the buttons
        quarkpy.qmacro.dialogbox.__init__(self, form, src,
            close = quarkpy.qtoolbar.button(
                self.close,
                "close this box",
                ico_editor, 0,
                "Close"),
            MakePrism = quarkpy.qtoolbar.button(
                self.MakePrism,
                "make prism",
                ico_editor, 3,
                "Make Prism"))



    def MakePrism(self, btn):
        # Commit any pending changes in the dialog box
        quarkx.globalaccept()

        # Gather information about what is to be created
        tex     = self.src["tex"]
        sides   =(self.src["sides"])[0]

        try:
            # Set; Down-Outer-Radius-X, Down-Outer-Radius-Y, Up-Outer-Radius-X, Up-Outer-Radius-Y
            value = self.src["radius"]
            dorx = dory = uorx = uory = value[0]
            if len(value) > 1:
                dory = uory = value[1]
            if len(value) > 2:
                uorx = uory = value[2]
            if len(value) > 3:
                uory = value[3]
        except:
            raise "Failure in 'Radius of prism' values"
        if (dorx < 0 or dory < 0 or uorx < 0 or uory < 0):
            raise "Negative values in 'Radius of prism' not allowed"

        try:
            # Set; Down-Inner-Radius-X, Down-Inner-Radius-Y, Up-Inner-Radius-X, Up-Inner-Radius-Y
            value = self.src["hollow"]
            dirx = diry = uirx = uiry = value[0]
            if len(value) > 1:
                diry = uiry = value[1]
            if len(value) > 2:
                uirx = uiry = value[2]
            if len(value) > 3:
                uiry = value[3]
            # If negative values, compute real radius from center
            if (dirx < 0):
                dirx = dorx + dirx
            if (diry < 0):
                diry = dory + diry
            if (uirx < 0):
                uirx = uorx + uirx
            if (uiry < 0):
                uiry = uory + uiry
        except:
            raise "Failure in 'Hollow of prism' values"
        if (dirx < 0 or diry < 0 or uirx < 0 or uiry < 0):
            raise "Negative values in 'Hollow of prism' will result in illegal brushes"

        value   = self.src["height"]
        height  = value[0] / 2

        try:
            value = self.src["offset"]
            offsetX = offsetY = value[0]
            if len(value) > 1:
                offsetY = value[1]
        except:
            raise "Failure in 'Offset of prism' values"

        gridsize    = (self.src["gridsize"])[0]
        slice       = self.src["slice"] is not None
        shareface   = self.src["shareface"] is not None
        stair       = self.src["stair"] is not None
        ramp        = self.src["ramp"] is not None

        # Save the settings...
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Vertex"]       = self.src["vertex"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Sides"]        = self.src["sides"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Radius"]       = self.src["radius"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Hollow"]       = self.src["hollow"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Height"]       = self.src["height"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Offset"]       = self.src["offset"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Gridsize"]     = self.src["gridsize"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Slice"]        = self.src["slice"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Shareface"]    = self.src["shareface"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Stair"]        = self.src["stair"]
        quarkx.setupsubset(SS_MAP, "Options")["MakePrism_Ramp"]         = self.src["ramp"]

        z_axis = quarkx.vect(0,0,1)
        
        # Create the prism
        if slice:
            p = quarkx.newobj("n-prism:g");
        else:
            p = quarkx.newobj("n-prism:p");

        # Create the top and bottom face
        up = quarkx.newobj("up:f")
        up["v"] = (-uorx+offsetX,-uory+offsetY,height, 128-uorx+offsetX,-uory+offsetY,height, -uorx+offsetX,128-uory+offsetY,height)
        up["tex"] = tex
        down = quarkx.newobj("down:f")
        down["v"] = (-dorx,128-dory,-height, 128-dorx,128-dory,-height, -dorx,-dory,-height)
        down["tex"] = tex
        # attach in simplest case
        if (slice and shareface and not stair) or not slice:
                p.appenditem(up)
                p.appenditem(down)

        # Create the sides
        angle = math.pi/2
        step = math.pi*2/sides
        if (self.src["vertex"] is None):
            angle = angle-step/2
        caseup = casedown = slantup = slantdown = i = 0

        while i < sides:
            # Compute the information about the side
            v1 = self.ComputePoint(angle-step,  dorx, dory, gridsize, -height)
            v2 = self.ComputePoint(angle,       dorx, dory, gridsize, -height)
            v3 = self.ComputePoint(angle-step,  uorx, uory, gridsize,  height)
            v4 = self.ComputePoint(angle,       uorx, uory, gridsize,  height)

            # Create the face
            f = quarkx.newobj("outside:f")
            f["v"] = (v1.x,v1.y,v1.z, v2.x,v2.y,v2.z, v3.x+offsetX,v3.y+offsetY,v3.z)
            f["tex"] = tex

            if not slice:
                p.appenditem(f)
            else:
                p1 = quarkx.newobj("prism-slice:p");
                p1.appenditem(f)

                v5 = self.ComputePoint(angle,       dirx, diry, gridsize, -height)
                v6 = self.ComputePoint(angle-step,  dirx, diry, gridsize, -height)
                v7 = self.ComputePoint(angle,       uirx, uiry, gridsize,  height)
                v8 = self.ComputePoint(angle-step,  uirx, uiry, gridsize,  height)

                f = quarkx.newobj("clockside:f")
                f["v"] = (v6.x,v6.y,v6.z, v1.x,v1.y,v1.z, v8.x+offsetX,v8.y+offsetY,v8.z)
                f["tex"] = tex
                p1.appenditem(f)

                if stair:
                    caseup = height*2/sides*i
                    if shareface:
                        casedown = height*2/sides*(sides-i-1)

                if ramp:
                    slantup = height*2/sides
                    if shareface:
                        slantdown = slantup

                    f = quarkx.newobj("farside:f")
                    f["v"] = (v2.x,v2.y,v2.z, v6.x,v6.y,v6.z, v4.x+offsetX,v4.y+offsetY,v4.z)
                    f["tex"] = tex
                    p1.appenditem(f)

                    f = quarkx.newobj("up:f")
                    f["v"] = (v3.x+offsetX,v3.y+offsetY,v3.z-caseup-slantup, v4.x+offsetX,v4.y+offsetY,v4.z-caseup, v8.x+offsetX,v8.y+offsetY,v8.z-caseup-slantup)
                    f["tex"] = tex
                    p1.appenditem(f)

                    f = quarkx.newobj("down:f")
                    f["v"] = (v1.x,v1.y,v1.z+casedown-slantdown, v6.x,v6.y,v6.z+casedown-slantdown, v2.x,v2.y,v2.z+casedown)
                    f["tex"] = tex
                    p1.appenditem(f)

                    p.appenditem(p1);
                    p1 = quarkx.newobj("prism-slice:p");

                    f = quarkx.newobj("nearside:f")
                    f["v"] = (v6.x,v6.y,v6.z, v2.x,v2.y,v2.z, v8.x+offsetX,v8.y+offsetY,v8.z)
                    f["tex"] = tex
                    p1.appenditem(f)

                f = quarkx.newobj("counterside:f")
                f["v"] = (v2.x,v2.y,v2.z, v5.x,v5.y,v5.z, v4.x+offsetX,v4.y+offsetY,v4.z)
                f["tex"] = tex
                p1.appenditem(f)

                if (dirx or diry or uirx or uiry) != 0:
                    f = quarkx.newobj("inside:f")
                    f["v"] = (v5.x,v5.y,v5.z, v6.x,v6.y,v6.z, v7.x,v7.y,v7.z)
                    f["tex"] = tex
                    p1.appenditem(f)

                if (not shareface and not stair) or stair:
#                    f = quarkx.newobj("up:f")
#                    f["v"] = (v7.x+offsetX,v7.y+offsetY,v7.z, v8.x+offsetX,v8.y+offsetY,v8.z, v4.x+offsetX,v4.y+offsetY,v4.z)
#                    f["tex"] = tex
                    f = up.copy()
                    if stair:
                       f.translate(-caseup*z_axis)
                    p1.appenditem(f)


#                    f = quarkx.newobj("down:f")
#                    f["v"] = (v5.x,v5.y,v5.z+casedown, v2.x,v2.y,v2.z+casedown, v6.x,v6.y,v6.z+casedown-slantdown)
#                    f["tex"] = tex
                    f = down.copy()
                    p1.appenditem(f)


                p.appenditem(p1);


            # Next point
            angle = angle - step
            i = i + 1



        # Remove borken polys and faces then Drop the items

        p.rebuildall()
        list = p.findallsubitems("", ':p')+p.findallsubitems("", ':f')
        list = filter(lambda p: p.broken, list)
        faces = list
        for face in faces:
            if face.broken:
                face.parent.removeitem(face)


        quarkpy.mapbtns.dropitemsnow(self.editor, [p], "make n sided prism")
        return


    def ComputePoint(self, angle, radiusX, radiusY, gridsize, z):
        # Compute the vertex
        if radiusX > 0:
            x = math.cos(angle) * radiusX
        elif radiusX < 0:
            x = math.cos(angle) ** 3 * math.fabs(radiusX)
        else:
            x = 0
        if radiusY > 0:
            y = math.sin(angle) * radiusY
        elif radiusY < 0:
            y = math.sin(angle) ** 3 * math.fabs(radiusY)
        else:
            y = 0
        if gridsize != 0:
            x = quarkx.rnd(x / gridsize) * gridsize
            y = quarkx.rnd(y / gridsize) * gridsize
        return quarkx.vect(x, y, z)


def MakePrismClick(m):
    # Function to start the dialog
    editor = mapeditor()
    if editor is None:
        return
    MakePrismDlg(quarkx.clickform, editor)


# Register the replace texture menu item
quarkpy.mapcommands.items.append(quarkpy.qmenu.sep) # separator
quarkpy.mapcommands.items.append(quarkpy.qmenu.item("&Make Prism", MakePrismClick, "|Make Prism:\n\nThis opens a dialog window for your input to create a prism of various types as well as texture selection.|intro.mapeditor.menu.html#makeprism"))

#----------- REVISION HISTORY ------------
#
# $Log: mapmakeprism.py,v $
# Revision 1.14  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.11  2003/03/24 08:57:15  cdunde
# To update info and link to infobase
#
# Revision 1.10  2003/02/01 01:04:41  cdunde
# Reactivate ramp selection and add script
# to remove newly created broken polys and faces.
#
# Revision 1.8  2001/06/17 21:10:57  tiglari
# fix button captions
#
# Revision 1.7  2001/03/07 20:16:16  tiglari
# removed ramp checkbox (for now, till it works)
#
# Revision 1.6  2001/02/28 09:45:18  tiglari
# fixed `stairs' option bug (ramp still has problems)
#
# Revision 1.5  2001/01/27 18:25:29  decker_dk
# Renamed 'TextureDef' -> 'DefaultTexture'
#
# Revision 1.4  2000/12/19 21:07:42  decker_dk
# Ax2Grind's MapMakePrism.py changes
#
# Revision 1.3  2000/06/03 10:25:30  alexander
# added cvs headers
#
# 2000-04-29 Decker; Added functionality to create cylinder-walls, with indent.
#            Loads/Saves used settings in SETUP.QRK
# 1999-04-15 Decker; Added functionality to create pie-slices, and face-sharing
#            of top and bottom face, if pie-slices are choosen.
