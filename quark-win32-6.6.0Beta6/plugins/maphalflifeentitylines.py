"""   QuArK  -  Quake Army Knife

History:
1999-12-23  Added func_tracktrain wheeldistance, but only X-axis
1999-12-21  Added func_tank* barrel-position-lines (BTW: I hate Python's way of indenting, without the need for begin/end's)
1999-??-??  Added Team Fortress Classic stuff..
1999-02-20  Added <entity>:TriggerTarget -> <entity>:targetname
1999-02-12  Added scripted_sequence:m_iszEntity -> <entity>:targetname
1999-01-24  Added trigger_changelevel -> info_landmark
1999-01-16  Added axis-rotating lines to rotating entities, so its a little easier to visualize around what the entity will rotate.
"""


#$Header: /cvsroot/quark/runtime/plugins/maphalflifeentitylines.py,v 1.7 2005/10/15 00:49:51 cdunde Exp $


Info = {
   "plug-in":       "Half-Life Arrow Extensions",
   "desc":          "Arrows/Axis for specifics like: 'master', 'multi_manager' and more...",
   "date":          "23 dec 99",
   "author":        "Decker",
   "author e-mail": "decker@post1.tele.dk",
   "quark":         "Version 5.10" }


from quarkpy.maputils import *
import quarkpy.mapentities
from quarkpy.qeditor import MapColor

DefaultDrawEntityLines = quarkpy.mapentities.DefaultDrawEntityLines
quakecolor = quarkpy.mapentities.quakecolor
makeRGBcolor = quarkpy.mapentities.makeRGBcolor
ObjectOrigin = quarkpy.mapentities.ObjectOrigin

import plugins.deckerutils
FindOriginTexPolyPos = plugins.deckerutils.FindOriginTexPolyPos

class HalfLifeDrawEntityLines(DefaultDrawEntityLines):

    def showoriginline(self, entity, xaxisbitvalue, yaxisbitvalue, view, color):
        orgpos = FindOriginTexPolyPos(entity)
        if orgpos is not None:
            try:
                axisflags = int(entity["spawnflags"])
            except:
                axisflags = 0
            axisdist = quarkx.vect(0,0,0)
            if axisflags & xaxisbitvalue:
                axisdist = quarkx.vect(16,0,0) # 16 is just some appropriate value I choosed
            elif axisflags & yaxisbitvalue:
                axisdist = quarkx.vect(0,16,0)
            else:
                axisdist = quarkx.vect(0,0,16)
            cv = view.canvas()
            cv.pencolor = color
            cv.penwidth = 3 # So it the axis gets more visual
            pos1, pos2 = (orgpos + axisdist), (orgpos - axisdist)
            vpos1, vpos2 = view.proj(pos1), view.proj(pos2)
            cv.line(vpos1, vpos2)
        return orgpos

    def drawentitylines(self, entity, org, view, entities, processentities):
        # Draw the default target/targetname/killtarget/light/_light arrows/ellipse
        DefaultDrawEntityLines.drawentitylines(self, entity, org, view, entities, processentities)
        # From here its Half-Life special
        axiscolor = MapColor("Axis")
        stopcolor = 0x808080    # (grey) when firing an Stop/End/Close action
        passcolor = 0x0080ff    # (orange) when firing an Pass-this-point action
        branchcolor = 0xff8000  # (blue) alternate path-route
        mastercolor = 0x00af00  # (green) points to a multisource/train entity
        rotcolor = 0xff00ff # (magenta) rotation axis
        org1 = view.proj(org)
        if org1.visible:
            R1 = entity["radius"] # For env_sound:e
            R2 = entity["m_flRadius"] # For scripted_sequence:e
    # TFC - Begin
            R3 = entity["t_length"] # for info_tfgoal
    # TFC - End
            if R1 or R2 or R3:
                try:
                    if R1:
                        radius = float(R1) * view.scale(org)
                    elif R2:
                        radius = float(R2) * view.scale(org)
                    else:
                        radius = float(R3) * view.scale(org)
                    cv = view.canvas()
                    cv.pencolor = axiscolor
                    cv.brushcolor = axiscolor
                    cv.penwidth = 1
                    cv.brushstyle = BS_BDIAGONAL
                    cv.ellipse(org1.x-radius, org1.y-radius, org1.x+radius, org1.y+radius)
                except:
                    pass
            if entity.name in ["func_door_rotating:b","func_platrot:b","func_rotating:b","func_rot_button:b","func_pendulum:b","func_trackautochange:b","func_trackchange:b","momentary_rot_button:b"]:
                if entity.name == "func_rotating:b":
                    self.showoriginline(entity,4,8,view,rotcolor) # func_rotating has different bitvalues for X-axis and Y-axis
                else:
                    self.showoriginline(entity,64,128,view,rotcolor)
            elif entity.name in ["func_tank:b","func_tanklaser:b","func_tankmortar:b","func_tankrocket:b"]:
                orgpos = self.showoriginline(entity,0,0,view,rotcolor) # Tanks always rotate around Z-axis
                # I need an canvas.arc() drawing-function so I can display the yaw/pitch range of the tank.
                if orgpos is not None:
                    try:
                        by = int(entity["barrely"])
                    except:
                        by = 0
                    try:
                        bz = int(entity["barrelz"])
                    except:
                        bz = 0
                    try:
                        bx = int(entity["barrel"])
                    except:
                        bx = 0
                    try:
                        brly = orgpos + quarkx.vect(0, by, 0)
                        brlz = brly + quarkx.vect(0, 0, bz)
                        brlx = brlz + quarkx.vect(bx, 0, 0)
                        cv = view.canvas()
                        cv.pencolor = passcolor
                        cv.penwidth = 3 # So it the barrel pos gets more visual
                        vpos1, vpos2 = view.proj(orgpos), view.proj(brly)
                        cv.line(vpos1, vpos2)
                        vpos1, vpos2 = view.proj(brly), view.proj(brlz)
                        cv.line(vpos1, vpos2)
                        vpos1, vpos2 = view.proj(brlz), view.proj(brlx)
                        cv.line(vpos1, vpos2)
                    except:
                        pass
            elif entity.name == "func_tracktrain:b":
                orgpos = self.showoriginline(entity,0,0,view,rotcolor) # TrackTrain always rotate around Z-axis
                if orgpos is not None:
                    try:
                        wheelsdist = int(entity["wheels"]) / 2
                    except:
                        wheeldist = 0
                    try:
                        heightdist = int(entity["height"])
                    except:
                        heightdist = 0
                    try:
                        heit = orgpos - quarkx.vect(0, 0, heightdist)
                        whlxA = heit - quarkx.vect(0, wheelsdist, 0)
                        whlxB = heit + quarkx.vect(0, wheelsdist, 0)
                        whlAyA = whlxA - quarkx.vect(16,0,0)
                        whlAyB = whlxA + quarkx.vect(16,0,0)
                        whlByA = whlxB - quarkx.vect(16,0,0)
                        whlByB = whlxB + quarkx.vect(16,0,0)
                        cv = view.canvas()
                        cv.pencolor = 0x000000
                        cv.penwidth = 3 # So it the wheeldist gets more visual
                        vpos1, vpos2 = view.proj(orgpos), view.proj(heit)
                        cv.line(vpos1, vpos2)
                        vpos1, vpos2 = view.proj(whlxA), view.proj(whlxB)
                        cv.line(vpos1, vpos2)
                        vpos1, vpos2 = view.proj(whlAyA), view.proj(whlAyB)
                        cv.line(vpos1, vpos2)
                        vpos1, vpos2 = view.proj(whlByA), view.proj(whlByB)
                        cv.line(vpos1, vpos2)
                    except:
                        pass

    # TFC - Begin
        if entity["group_no"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "group_no", entity["group_no"], org, -1, 0x010101, view, entities, processentities)

        if entity["items"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "goal_no", entity["items"], org, -1, 0xFF88FF, view, entities, processentities)

        if entity["items_allowed"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "goal_no", entity["items_allowed"], org, 1, 0xFFFFFF, view, entities, processentities)
        if entity["has_item_from_group"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "group_no", entity["has_item_from_group"], org, -1, 0xCCCCCC, view, entities, processentities)
        if entity["if_goal_is_active"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "goal_no", entity["if_goal_is_active"], org, -1, 0xFFFFFF, view, entities, processentities)

        if entity["axhitme"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "goal_no", entity["axhitme"], org, 0, 0xFF8888, view, entities, processentities)
        if entity["restore_goal_no"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "goal_no", entity["restore_goal_no"], org, 0, 0x88FF88, view, entities, processentities)
        if entity["impulse"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "goal_no", entity["impulse"], org, 0, 0x88FF88, view, entities, processentities)
        if entity["remove_goal_no"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "goal_no", entity["remove_goal_no"], org, 0, 0x88FF88, view, entities, processentities)

        if entity["activate_group_no"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "group_no", entity["activate_group_no"], org, 0, 0x0088CC, view, entities, processentities)
    # TFC - End

        etargetname = entity["targetname"]
        if etargetname is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "master", etargetname, org, 1, mastercolor, view, entities, processentities)
            # Must insert arrows from other entities with special specific-names also!
            for i in entities:
                if i.name == "multi_manager:e":
                    if i[etargetname] is not None: # Does multi_manager has a specific that matches out targetname-value?
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities) # DECKER - Maybe add a text ("time "+i[etargetname])
                elif i["netname"] == etargetname:
                    if i.name  == "func_door:b":    # func_door.netname -> fire on close
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, stopcolor, view, processentities, "Fire on Close")
                    elif i.name == "func_button:b": # func_button.netname -> target path
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities, "Target Path")
                    elif i.name == "path_track:e":  # path_track.netname -> fire on dead end
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, stopcolor, view, processentities, "Fire on Dead End")
                    elif i.name == "monster_bigmomma:e": # monster_bigmomma.netname -> first node
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities)
                elif i.name in ["path_corner:e", "path_track:e"]:
                    if i["message"] == etargetname: # path_*.message -> fire on pass
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, passcolor, view, processentities, "Fire on Pass")
                    if i["altpath"] == etargetname: # path_track.altpath -> branch path
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, branchcolor, view, processentities, "Branch Path")
                elif i.name == "func_trackchange:b":
                    if i["train"] == etargetname:
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, mastercolor, view, processentities, "Train")
                    if i["toptrack"] == etargetname:
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities, "Top Track")
                    if i["bottomtrack"] == etargetname:
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, branchcolor, view, processentities, "Bottom Track")
                elif i.name == "func_guntarget:b":
                    if i["message"] == etargetname: # path_*.message -> fire on damage
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, passcolor, view, processentities, "Fire on damage")
                elif i.name == "env_beam:e":
                    if i["LightningStart"] == etargetname:
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities, "LightingStart")
                    if i["LightningEnd"] == etargetname:
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities, "LightingEnd")
                elif i.name == "trigger_changelevel:b":
                    if i["landmark"] == etargetname:
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities, "Landmark")
                elif i.name == "scripted_sequence:e":
                    if i["m_iszEntity"] == etargetname:
                        DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, axiscolor, view, processentities, "Scripted Sequence")
                elif i["TriggerTarget"] == etargetname:
                    DefaultDrawEntityLines.drawentityarrow(self, i, org, 1, branchcolor, view, processentities, "TriggerTarget")

        if entity["master"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["master"], org, 0, mastercolor, view, entities, processentities)
        if entity["netname"] is not None:
            if entity.name == "func_door:b":
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["netname"], org, 0, stopcolor, view, entities, processentities, "Fire on Close")
            elif entity.name == "func_button:b":
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["netname"], org, 0, axiscolor, view, entities, processentities, "Target Path")
            elif entity.name == "path_track:e":
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["netname"], org, 0, stopcolor, view, entities, processentities, "Fire on Dead End")
            elif entity.name == "monster_bigmomma:e":
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["netname"], org, 0, axiscolor, view, entities, processentities)
        if entity["TriggerTarget"] is not None:
            DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["TriggerTarget"], org, 0, branchcolor, view, entities, processentities, "TriggerTarget")
        # -- From here, its an if-elif structure --
        if entity.name == "multi_manager:e":
            # Targets is in specifics, must extract them and make arrows
            for i in entity.dictspec.keys():
                if i not in ["targetname", "origin"]: # Ignore the two known specifics
                    DefaultDrawEntityLines.drawentityarrows(self, "targetname", i, org, 0, axiscolor, view, entities, processentities) # DECKER - Maybe add a text ("time "+entity[i])
        elif entity.name == "path_corner:e":
            if entity["message"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["message"], org, 0, passcolor, view, entities, processentities, "Fire on Pass")
        elif entity.name == "path_track:e":
            if entity["message"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["message"], org, 0, passcolor, view, entities, processentities, "Fire on Pass")
            if entity["altpath"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["altpath"], org, 0, branchcolor, view, entities, processentities, "Branch Path")
        elif entity.name == "func_trackchange:b":
            if entity["train"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["train"], org, 0, mastercolor, view, entities, processentities, "Train")
            if entity["toptrack"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["toptrack"], org, 0, axiscolor, view, entities, processentities, "Top Track")
            if entity["bottomtrack"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["bottomtrack"], org, 0, branchcolor, view, entities, processentities, "Bottom Track")
        elif entity.name == "func_guntarget:b":
            if entity["message"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["message"], org, 0, passcolor, view, entities, processentities, "Fire on Damage")
        elif entity.name == "env_beam:e":
            if entity["LightningStart"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["LightningStart"], org, 0, axiscolor, view, entities, processentities, "LightningStart")
            if entity["LightningEnd"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["LightningEnd"], org, 0, axiscolor, view, entities, processentities, "LightningEnd")
        elif entity.name == "trigger_changelevel:b":
            if entity["landmark"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["landmark"], org, 0, axiscolor, view, entities, processentities, "Landmark")
        elif entity.name == "scripted_sequence:e":
            if entity["m_iszEntity"] is not None:
                DefaultDrawEntityLines.drawentityarrows(self, "targetname", entity["m_iszEntity"], org, 0, axiscolor, view, entities, processentities, "Scripted Sequence")
        elif entity.name == "multisource:e":
            # 'globalstate' points to an env_global entity which must have the same 'globalstate'
            pass # DECKER - Going to implement later


#
# Register this class with its gamename
#
quarkpy.mapentities.EntityLinesMapping.update({
  "Half-Life": HalfLifeDrawEntityLines()
})


# ----------- REVISION HISTORY ------------
#
#
# $Log: maphalflifeentitylines.py,v $
# Revision 1.7  2005/10/15 00:49:51  cdunde
# To reinstate headers and history
#
# Revision 1.4  2001/02/13 21:02:55  decker_dk
# Tabbing problem, which is a really serious problem with Python!!
#
# Revision 1.3  2000/06/03 10:25:30  alexander
# added cvs headers
#
#
#
#