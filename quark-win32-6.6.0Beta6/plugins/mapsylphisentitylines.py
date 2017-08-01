"""   QuArK  -  Quake Army Knife
"""
#
# Copyright (C) 2003 Harry Kalogirou
#

#$Header: /cvsroot/quark/runtime/plugins/mapsylphisentitylines.py,v 1.5 2011/10/06 20:13:37 danielpharos Exp $

Info = {
   "plug-in":       "Sylphis entities line support",
   "desc":          "Displays varius lines assosiated with Sylphis.",
   "date":          "23 Feb 2003",
   "author":        "Harry Kalogirou",
   "author e-mail": "harkal@gmx.net",
   "quark":         "Version 6.4" }


import math
from quarkpy.maputils import *
import quarkpy.mapentities
import quarkpy.qeditor
import quarkpy.qhandles

DefaultDrawEntityLines = quarkpy.mapentities.DefaultDrawEntityLines
ObjectOrigin = quarkpy.mapentities.ObjectOrigin

import plugins.deckerutils
FindOriginFlagPolyPos = plugins.deckerutils.FindOriginFlagPolyPos

class SylphisDrawEntityLines(DefaultDrawEntityLines):
    def drawentitylines(self, entity, org, view, entities, processentities):
        # Draw the default target/targetname/killtarget/light/_light arrows/ellipse
        DefaultDrawEntityLines.drawentitylines(self, entity, org, view, entities, processentities)
        rad = entity['radius']
        
        if rad:
            o = entity['radius'].split()
            if len(o) == 1: o = (o[0], o[0], o[0])
            elif len(o) == 2: o = (o[0], o[1], (o[0] + o[1]) / 2)
            try:
                radius = quarkx.vect(float(o[0]), float(o[1]), float(o[2]))
            except:
                radius = quarkx.vect(10.0, 10.0, 10.0)
            cx, cy = [], []
            up = view.proj(quarkx.vect(org.x, org.y, org.z + radius.z))
            down = view.proj(quarkx.vect(org.x, org.y, org.z - radius.z))
            right = view.proj(quarkx.vect(org.x, org.y + radius.y, org.z))
            left = view.proj(quarkx.vect(org.x, org.y - radius.y, org.z))
            front = view.proj(quarkx.vect(org.x + radius.x, org.y, org.z))
            back = view.proj(quarkx.vect(org.x - radius.x, org.y, org.z))

            cx.append(up.x); cx.append(down.x); cx.append(left.x); cx.append(right.x)
            cx.append(front.x); cx.append(back.x);
            maxX = max(cx)
            minX = min(cx)

            cy.append(up.y); cy.append(down.y); cy.append(left.y); cy.append(right.y)
            cy.append(front.y); cy.append(back.y);
            maxY = max(cy)
            minY = min(cy)

            lightfactor, = quarkx.setupsubset()['LightFactor']

            radius = 100
            try:
                color = quakecolor(quarkx.vect(entity["color"]))
            except:
                color = makeRGBcolor(255,255,255)
            cv = view.canvas()
            cv.pencolor = color
            cv.penwidth = 2
            cv.brushstyle = BS_CLEAR
            # This is not so "correct" but works most of the times
            cv.ellipse(minX, minY, maxX, maxY)
            cv.penwidth = 1
            cv.line(down.x, down.y, up.x, up.y)
            cv.line(left.x, left.y, right.x, right.y)
            cv.line(back.x, back.y, front.x, front.y)

        parent = entity['parent']
        if parent:
            o = parent.split('.')
            parent = o[0]
            cv = view.canvas()
            for i in entities:
                if i['name'] == parent:
                    cv.pencolor = 0x0080ff
                    cv.penwidth = 2
                    cv.brushstyle = BS_CLEAR
                    o = ObjectOrigin(i)
                    if o is None:return
                    Arrow(cv, view, o, org)
            

#
# Register this class with its gamename
#
quarkpy.mapentities.EntityLinesMapping.update({
  "Sylphis": SylphisDrawEntityLines()
})


# ----------- REVISION HISTORY ------------
#$Log: mapsylphisentitylines.py,v $
#Revision 1.5  2011/10/06 20:13:37  danielpharos
#Removed a bunch of 'fixes for linux': Wine's fault (and a bit ours); let them fix it.
#
#Revision 1.4  2006/01/30 08:20:00  cdunde
#To commit all files involved in project with Philippe C
#to allow QuArK to work better with Linux using Wine.
#
#Revision 1.3  2005/10/15 00:51:24  cdunde
#To reinstate headers and history
#
#Revision 1.1  2004/05/21 01:04:14  cdunde
#To add support for Sylphis game engine. Code by Harry Kalogirou.
#
#
