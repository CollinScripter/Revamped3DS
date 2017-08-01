"""   QuArK  -  Quake Army Knife

Display axis icons in Model editor
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mdlaxisicons.py,v 1.19 2010/05/05 15:46:39 cdunde Exp $


Info = {
   "plug-in":       "Display axis icons in Model editor",
   "desc":          "Displays the axis icons in Model editor viewing windows",
   "date":          "March 6 2006",
   "author":        "cdunde",
   "author e-mail": "cdunde1@comcast.net",
   "quark":         "Version 6" }


import quarkx
import quarkpy.mdloptions
from quarkpy.mdlutils import *
from quarkpy.qhandles import *
from quarkpy.qutils import *

#
# <tiglari>
#
# This snippet redefines the MakeScroller function in the qhandles
#  module, eliminating the need for a new qhandles.py file.
#

#
# This attaches the item to the options menu; it's best for new
#  facilities to redefine menus etc in the quarkpy modules rather
#  than modify the files themselves because then if people don't
#  like the effects of your plugin they can remove all of them by
#  deleting one file.  The toggle-item itself works fine.
# The prolixity of `quarkpy.mapoptions' could be reduced by using
#  `import X from mapoptions' statements (without ""'s & #)as follows:
#""from quarkpy.mapoptions import *"" and
#""items.append(toggleitem("&Axis XYZ letter indicator in view windows",
#"AxisXYZ", (1,1),
#      hint="|Display the X Y or Z indicator letter per view to associate #the rotation menu buttons. These are for reference only and are not #selectable with the mouse."))""

# But I don't think that would be worthwhile, 
#  so we'll just use the long version below insted:
#


XYZitem = quarkpy.mdloptions.toggleitem("&Axis XYZ letter indicator in view windows", "AxisXYZ", (1,1),
      hint="|Axis XYZ letter indicator in view windows:\n\nThis display s the X Y or Z indicator letter per view to associate the rotation menu buttons. These are for reference only and are not selectable with the mouse.|intro.modeleditor.menu.html#optionsmenu")


quarkpy.mdloptions.items.append(XYZitem)
for menitem, keytag in [(XYZitem, "AxisXYZ")]:
    MapHotKey(keytag,menitem,quarkpy.mdloptions)


#
# Get the actual icons, no reason to do this more than once.
# Done by the loadimages function and the required augments.
#  img = quarkx.loadimages(filename + ext, width, transparencypt)
#

axisicons = quarkx.loadimages("images\\axisicons.bmp",32,(0,0))

#
# This part is a magical incantation.
# First the normal arguments for
#  finishdrawing, then the oldfinish=... stuff,
#  which has the effect of storing the current
#  finishdrawing method inside this function as
#  the value of the oldfinish variable.
# These def statements are executed as the plugins are being
#  loaded, but not reexecuted in later operations
#  of the map editor, only the functions they define are.
#


def newfinishdrawing(editor, view, oldfinish=quarkpy.mdleditor.ModelEditor.finishdrawing):
    #
    # execute the old method
    #

    oldfinish(editor, view)

    # Stops jerky movement during panning in 2D views.
    from quarkpy.qbaseeditor import flagsmouse
    if (flagsmouse == 528 or flagsmouse == 1040):
        view.handles = []

    #
    # Why not see what the clientarea produces.
    # Look at the console to find out.
    #
#    debug('area: '+`view.clientarea`)

    #
    # Below ties this function to the toggel button
    #  in the Option menu.
    #



    def MakeScroller(layout, view):
        sbviews = [None, None]
        for ifrom, linkfrom, ito, linkto in layout.sblinks:
            if linkto is view:
                sbviews[ito] = (ifrom, linkfrom)
        def scroller(x, y, view=view, hlink=sbviews[0], vlink=sbviews[1]):
            import quarkpy.mdleditor
            editor = quarkpy.mdleditor.mdleditor
            view.scrollto(x, y)
            try:
                if (view.info["viewname"] == "skinview" or view.info["viewname"] == "editors3Dview" or view.info["viewname"] == "3Dwindow"):
                    if view.info["viewname"] == "editors3Dview":
                        comp = editor.Root.currentcomponent
                        fillcolor = MapColor("Options3Dviews_fillColor1", SS_MODEL)
                        backfacecolor1 = MapColor("BackFaceColor1", SS_MODEL)
                        backfacecolor2 = MapColor("BackFaceColor2", SS_MODEL)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh1"] == "1":
     # The line below can be used later if we want an option to draw the back faces as well.
     #2                       comp.filltris = [(fillcolor,(backfacecolor1,backfacecolor2))]*len(comp.triangles)
                            comp.filltris = [(fillcolor,None)]*len(comp.triangles)
                        else:
                            if quarkx.setupsubset(SS_MODEL, "Options")["DBF"] == "1":
                                comp.filltris = [(None,(backfacecolor1,backfacecolor2))]*len(comp.triangles)             
                            else:
                                if editor.ModelFaceSelList != []:
                                    comp.filltris = quarkpy.mdleditor.faceselfilllist(view)

                    if view.info["viewname"] == "3Dwindow":
                        comp = editor.Root.currentcomponent
                        fillcolor = MapColor("Options3Dviews_fillColor5", SS_MODEL)
                        backfacecolor1 = MapColor("BackFaceColor1", SS_MODEL)
                        backfacecolor2 = MapColor("BackFaceColor2", SS_MODEL)
                        if quarkx.setupsubset(SS_MODEL, "Options")["Options3Dviews_fillmesh5"] == "1":
     # The line below can be used later if we want an option to draw the back faces as well.
     #2                       comp.filltris = [(fillcolor,(backfacecolor1,backfacecolor2))]*len(comp.triangles)
                            comp.filltris = [(fillcolor,None)]*len(comp.triangles)
                        else:
                            if quarkx.setupsubset(SS_MODEL, "Options")["DBF"] == "1":
                                comp.filltris = [(None,(backfacecolor1,backfacecolor2))]*len(comp.triangles)            
                            else:
                                if editor.ModelFaceSelList != []:
                                    comp.filltris = quarkpy.mdleditor.faceselfilllist(view)
                    view.repaint()
                    return scroller
            except:
                pass

            if hlink is not None:
                if hlink[0]:
                    hlink[1].scrollto(None, x)
                else:
                    hlink[1].scrollto(x, None)
            if vlink is not None:
                if vlink[0]:
                    vlink[1].scrollto(None, y)
                else:
                    vlink[1].scrollto(y, None)
            if not MdlOption("AxisXYZ"):
                view.update()
            ### This is the 2D views Textured mode scroller section
            if (flagsmouse == 1040 or flagsmouse == 1048 or flagsmouse == 1056) and view.viewmode == "tex":
                if (view.info["viewname"] == "XY" or view.info["viewname"] == "XZ" or view.info["viewname"] == "YZ"):
                    quarkpy.mdleditor.paintframefill(editor, view)
             #   view.repaint() # If uncommented, causes gridscale to jitter.
            ### This is the 2D views WireFrame mode scroller section
            else:
                if (view.info["viewname"] == "XY" or view.info["viewname"] == "XZ" or view.info["viewname"] == "YZ"):
                    quarkpy.mdleditor.paintframefill(editor, view)
        return scroller
    quarkpy.qhandles.MakeScroller = MakeScroller

    if not MdlOption("AxisXYZ"):return



    # The following sets the canvas function to draw the images.
    cv = view.canvas()
    type = view.info["type"]  # These type values are set
                              #  in the layout-defining plugins.
    if type == "YZ":
       index = 0
    elif type == "XZ":
       index = 1
    elif type == "XY":
       index = 2
    else:
       return

    #
    # ahah, the canvas has absolute coordinates with relation
    #  to the window it appears in.
    #

    if (flagsmouse == 528 or flagsmouse == 1040 or flagsmouse == 1048 or flagsmouse == 1056):
        pass
    else:
        cv.draw(axisicons[index],14,1)

#
# Now set our new function as the finishdrawing method.
#


quarkpy.mdleditor.ModelEditor.finishdrawing = newfinishdrawing


#
# There is still the problem that when the view is panned, the old image is not erased, we
#   need to find out how the red lines are drawn, and how grey-out-of-view really works,
#   to learn how to stop this.  The images persist only in the view that's actually being
#   dragged on, but flicker in the others, which looks unprofessional, whereas the
#   red line is rock solid.
#


# ----------- REVISION HISTORY ------------
#
#$Log: mdlaxisicons.py,v $
#Revision 1.19  2010/05/05 15:46:39  cdunde
#To stop jerky movement in Model Editor when scrolling, panning.
#
#Revision 1.18  2008/07/15 23:16:27  cdunde
#To correct typo error from MldOption to MdlOption in all files.
#
#Revision 1.17  2008/05/01 15:38:54  danielpharos
#Got rid of global saveeditor
#
#Revision 1.16  2008/02/22 09:52:22  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.15  2007/10/30 20:24:01  danielpharos
#Change a wrong currentview into view
#
#Revision 1.14  2007/07/20 01:41:04  cdunde
#To setup selected model mesh faces so they will draw correctly in all views.
#
#Revision 1.13  2007/06/19 06:16:07  cdunde
#Added a model axis indicator with direction letters for X, Y and Z with color selection ability.
#Added model mesh face selection using RMB and LMB together along with various options
#for selected face outlining, color selections and face color filltris but this will not fill the triangles
#correctly until needed corrections are made to either the QkComponent.pas or the PyMath.pas
#file (for the TCoordinates.Polyline95f procedure).
#Also setup passing selected faces from the editors views to the Skin-view on Options menu.
#
#Revision 1.12  2007/06/07 04:23:21  cdunde
#To setup selected model mesh face colors, remove unneeded globals
#and correct code for model colors.
#
#Revision 1.11  2007/05/17 23:56:54  cdunde
#Fixed model mesh drag guide lines not always displaying during a drag.
#Fixed gridscale to display in all 2D view(s) during pan (scroll) or drag.
#General code proper rearrangement and cleanup.
#
#Revision 1.10  2007/05/16 23:28:22  cdunde
#Fixed panning function that stopped model mesh from being drawn
#during panning (scrolling) action and removed unnecessary code.
#
#Revision 1.9  2007/05/16 20:59:02  cdunde
#To remove unused argument for the mdleditor paintframefill function.
#
#Revision 1.8  2007/04/13 19:41:48  cdunde
#Minor improvement in the multi meshfill coloring when scrolling or zooming.
#
#Revision 1.7  2007/04/04 21:34:17  cdunde
#Completed the initial setup of the Model Editors Multi-fillmesh and color selection function.
#
#Revision 1.6  2007/03/04 19:37:03  cdunde
#To stop unneeded redrawing of handles in other views
#when scrolling in a Model Editor's 3D view.
#
#Revision 1.5  2007/01/30 06:37:37  cdunde
#To get the Skin-view to scroll without having to redraw all the handles in every view.
#Increases response time and drawing speed.
#
#Revision 1.4  2006/11/30 01:17:48  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.3  2006/11/29 06:58:36  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.2.2.1  2006/11/28 00:55:35  cdunde
#Started a new Model Editor Infobase section and their direct function links from the Model Editor.
#
#Revision 1.2  2006/03/07 07:51:19  cdunde
#To put in safeguard fix for occasional error of not getting editor.
#
#Revision 1.1  2006/03/07 06:11:21  cdunde
#To add view axis icons to Model editor Options menu.
#
#
#