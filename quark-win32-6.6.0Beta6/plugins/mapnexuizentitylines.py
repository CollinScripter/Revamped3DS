"""   QuArK  -  Quake Army Knife
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/mapnexuizentitylines.py,v 1.1 2008/07/14 16:34:44 cdunde Exp $


Info = {
   "plug-in":       "NEXUIZ Arrow Extensions",
   "desc":          "Displays axis for rotating entities and jump-archs for push-entities. Note: RED-colored jump-archs indicates that the jump isn't correctly calculated, due to either non-default gravity or too low an arch.",
   "date":          "03 June 2008",
   "author":        "X7",
   "author e-mail": "wplews@gmail.com",
   "quark":         "Version 6.0 Beta 1" }


import math
from quarkpy.maputils import *
import quarkpy.mapentities
import quarkpy.qeditor
import quarkpy.qhandles

DefaultDrawEntityLines = quarkpy.mapentities.DefaultDrawEntityLines
ObjectOrigin = quarkpy.mapentities.ObjectOrigin

import plugins.deckerutils
FindOriginFlagPolyPos = plugins.deckerutils.FindOriginTexPolyPos2

class NEXUIZDrawEntityLines(DefaultDrawEntityLines):

   # - Decker. Trying to calculate a more correct jump-arch, using the math from Q3's GameSource,
   #   but I simply can't figure out how to do that.
   #
   #def CalculateTrajectory2(self, start_vec, apex_vec, speed_angles, gravity=800.0, multiplier=2, points=16):
   #    path_vecs = []
   #    try:
   #        if (apex_vec is not None):
   #            height = apex_vec.z - start_vec.z
   #            if (height <= 0 or gravity <= 0):
   #                raise "Problem!"
   #            time = math.sqrt( height / ( 0.5 * gravity ) );
   #            if (time <= 0):
   #                raise "Problem!"
   #            direction_vec = apex_vec - start_vec
   #            direction_vec = quarkx.vect(direction_vec.x, direction_vec.y, 0)
   #            direction_vec = direction_vec.normalized
   #            forward = abs(direction_vec) / time
   #            velocity_vec = direction_vec * forward
   #            velocity_vec = quarkx.vect(velocity_vec.x, velocity_vec.y, time * gravity)
   #        else:
   #            speed_z, angles = speed_angles
   #            direction_vec = quarkpy.qhandles.angles2vec(angles)
   #            direction_vec = quarkx.vect(direction_vec.x, direction_vec.y, 0)
   #            direction_vec = direction_vec.normalized
   #            velocity_vec = direction_vec * speed_z
   #            velocity_vec = quarkx.vect(velocity_vec.x, velocity_vec.y, speed_z)
   #        print "direction:", direction_vec, "velocity:", velocity_vec
   #    except:
   #        print "Exception:"
   #    return path_vecs, color

    def CalculateTrajectory(self, start_vec, apex_vec, speed_angles, gravity=800.0, multiplier=2, points=16):
        # Credits to "http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/bobtoolz/bobtoolz/DBobView.cpp"
        path_vecs = []
        color = 0x000000
        etext = None
        try:
            dist_vec = None
            speed_z = 0

            if (apex_vec is not None):
                # Calculate a distance-vector between the start-vector and the apex-vector
                dist_vec = apex_vec - start_vec

                # If the distance-vector's z-axis is zero or negative, then we can't calculate a proper flight-arch
                if (dist_vec.z <= 0):
                    etext = "Can't calculate with zero/negative z-distance"
                    raise etext

                # Calculate the z-axis speed at normal gravity (800.0)
                speed_z = math.sqrt(2 * gravity * dist_vec.z)
            else:
                if (gravity != 800):
                    # This calculation won't work with another gravity setting.
                    color = 0x0000FF
                    print "Trigger_push/Target_push: Gravity isn't 800.0, so jump-arch is not calculated correctly"

                speed_z, angles = speed_angles
                speed_z = math.sqrt(gravity * speed_z)
                dist_vec = quarkpy.qhandles.angles2vec(angles)

                if (dist_vec.z < 0.7):
                    # This calculation won't work with a pitch lower than ~45
                    color = 0x0000FF
                    print "Trigger_push/Target_push: pitch-angle is less than 45, so jump-arch is not calculated correctly"

                dist_vec = dist_vec.normalized * speed_z

            # Calculate the time it will take to make the "flight" at normal gravity (800.0)
            flight_time = speed_z / gravity

            # Calculate the speed-distance-vector of one unit of flight_time
            speed_vec = dist_vec * (1 / flight_time)

            # Adjust the z-axis of the speed-distance-vector
            speed_vec = quarkx.vect(speed_vec.x, speed_vec.y, speed_z)

            # Determine the flighttime-interval between each point
            interval = (multiplier * flight_time) / points

            # Calculate each point in the flight-path
            for i in range(points+1):
                # Compute the flighttime for this point
                ltime = interval * i

                # Calculate a point in the linear(straight) line from start-vector to end-vector
                path_vec = speed_vec * ltime
                path_vec = path_vec + start_vec

                # Adjust the z-axis
                z = start_vec.z + (speed_z * ltime) - (gravity * 0.5 * ltime * ltime)
                path_vec = quarkx.vect(path_vec.x, path_vec.y, z)

                # Put this point in the list
                path_vecs.append(path_vec)
        except etext:
            print "exception:", etext

        return path_vecs, color

    def showjumparch(self, start_entity, view, entities):
        apex_vec = None
        speed_angles = None
        if (start_entity["target"] is not None \
        and start_entity["target"] != ""):
            apex_entity = None
            for e in entities:
                if (e["targetname"] == start_entity["target"]):
                    apex_vec = ObjectOrigin(e)
                    break
            else:
                return
        else:
            speed = 1000 # Default value according to [DataQ3.QRK] target_push:form
            if (start_entity["speed"] is not None \
            and start_entity["speed"] != ""):
                speed = int(start_entity["speed"])
            angles = None
            if (start_entity["angles"] is not None):
                angles = start_entity["angles"]
            if (angles is None):
                return
            speed_angles = (speed, angles)
        start_vec = ObjectOrigin(start_entity)

        editor = quarkpy.qeditor.mapeditor()
        if editor is None:
            return
        worldspawn = editor.Root
        gravity = 800.0
        if (worldspawn["gravity"] is not None \
        and worldspawn["gravity"] != ""):
            gravity = int(worldspawn["gravity"])

        path, color = self.CalculateTrajectory(start_vec, apex_vec, speed_angles, gravity)
        if len(path) > 0:
            cv = view.canvas()
            cv.pencolor = color
            cv.penwidth = 3
            prevpath = None
            for p in path:
                thispath = view.proj(p)
                if prevpath is not None:
                    cv.line(prevpath, thispath)
                prevpath = thispath

    def showoriginline(self, entity, xaxisbitvalue, yaxisbitvalue, view, color):
        orgpos = FindOriginFlagPolyPos(entity)
        if orgpos is not None:
            try:
                axisflags = int(entity["spawnflags"])
            except:
                axisflags = 0
            axisdist = quarkx.vect(0, 0, 0)
            if axisflags & xaxisbitvalue:
                axisdist = quarkx.vect(16, 0, 0) # 16 is just some appropriate value I choosed
            elif axisflags & yaxisbitvalue:
                axisdist = quarkx.vect(0, 16, 0)
            else:
                axisdist = quarkx.vect(0, 0, 16)
            cv = view.canvas()
            cv.pencolor = color
            cv.penwidth = 3 # So it the axis gets more visual
            pos1, pos2 = (orgpos + axisdist), (orgpos - axisdist)
            vpos1, vpos2 = view.proj(pos1), view.proj(pos2)
            cv.line(vpos1, vpos2)

    def drawentitylines(self, entity, org, view, entities, processentities):
        # Draw the default target/targetname/killtarget/light/_light arrows/ellipse
        DefaultDrawEntityLines.drawentitylines(self, entity, org, view, entities, processentities)
        # From here its Quake-3 special
        axiscolor = quarkpy.qeditor.MapColor("Axis")
        rotcolor = 0xff00ff     # (magenta) rotation axis
        org1 = view.proj(org)
        if org1.visible:
            if entity.name == "func_bobbing:b":
                self.showoriginline(entity, 1, 2, view, rotcolor)
            elif entity.name == "func_rotating:b":
                self.showoriginline(entity, 4, 8, view, rotcolor) # func_rotating has different bitvalues for X-axis and Y-axis
            elif entity.name == "trigger_push:b":
                self.showjumparch(entity, view, entities)
            elif entity.name == "target_push:e":
                self.showjumparch(entity, view, entities)

#
# Register this class with its gamename
#
quarkpy.mapentities.EntityLinesMapping.update({
  "NEXUIZ": NEXUIZDrawEntityLines()
})


# ----------- REVISION HISTORY ------------
#
# $Log: mapnexuizentitylines.py,v $
# Revision 1.1  2008/07/14 16:34:44  cdunde
# More new entity line drawing features by X7.
#
#