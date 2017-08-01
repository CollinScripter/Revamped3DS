# QuArK  -  Quake Army Knife
#
# Copyright (C) 1996-2000 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/mapbotwaypointer.py,v 1.13 2006/05/19 17:07:53 cdunde Exp $

## Fredrick_vamstad@hotmail.com

Info = {
   "plug-in":       "Bot Waypointer",
   "desc":          "Bot Waypointer",
   "date":          "? may 2002",
   "author":        "Decker,Peter,Fred",
   "author e-mail": "decker@planetquake.com",
   "quark":         "Version 6.5"
}

import sys
import struct
import quarkx
import quarkpy.qmacro
import quarkpy.mapmenus
from quarkpy.qeditor import *
from quarkpy.mapduplicator import *
from quarkpy.qhandles import *

#
# Base class for load/save bot-waypoint files
#
class BotWaypointConverter:
    m_waypoints = []

    def __init__(self):
        pass

    def Load(self, filename):
        raise

    def Save(self, filename):
        raise

#
# Class to load/save HPBBot v2.1 waypoint files
#
class BotWaypointConvertHPB(BotWaypointConverter):
    "HPB-Bot v2.1 .WPT file load/save"

    m_HPB_flags = \
        [(      1 ,"team_bit1"        ,"allow for 4 teams (0-3)"                                   ) \
        ,(      2 ,"team_bit2"        ,"allow for 4 teams (0-3)"                                   ) \
        ,(      4 ,"teamspecific"     ,"waypoint only for specified team"                          ) \
        ,(      8 ,"crouch"           ,"must crouch to reach this waypoint"                        ) \
        ,(     16 ,"ladder"           ,"waypoint on a ladder"                                      ) \
        ,(     32 ,"lift"             ,"wait for lift to be down before approaching this waypoint" ) \
        ,(     64 ,"door"             ,"wait for door to open"                                     ) \
        ,(    128 ,"health"           ,"health kit (or wall mounted) location"                     ) \
        ,(    256 ,"armor"            ,"armor (or HEV) location"                                   ) \
        ,(    512 ,"ammo"             ,"ammo location"                                             ) \
        ,(   1024 ,"sniper"           ,"sniper waypoint (a good sniper spot)"                      ) \
        ,(   2048 ,"flag"             ,"flag position (or hostage or president)"                   ) \
        ,(   2048 ,"flf_cap"          ,"Front Line Force capture point"                            ) \
        ,(   4096 ,"flag_goal"        ,"flag return position (or rescue zone)"                     ) \
        ,(   4096 ,"flf_defend"       ,"Front Line Force defend point"                             ) \
        ,(   8192 ,"prone"            ,"go prone (laying down)"                                    ) \
        ,(  16384 ,"aiming"           ,"aiming waypoint"                                           ) \
        ,(  32768 ,"sentrygun"        ,"sentry gun waypoint for TFC"                               ) \
        ,(  65536 ,"dispenser"        ,"dispenser waypoint for TFC"                                ) \
        ,( 131072 ,"weapon"           ,"weapon_ entity location"                                   ) \
        ,( 262144 ,"jump"             ,"jump waypoint"                                             ) \
        ]

    def FlagsToSpecs(self, flags, obj):
        for flag, spec, hint in self.m_HPB_flags:
            if (flag & flags) == flag:
                obj["_"+spec] = "1"
            else:
                obj["_"+spec] = "0"

    def SpecsToFlags(self, obj):
        flags = 0
        for flag, spec, hint in self.m_HPB_flags:
            try:
                flags = flags + (flag * int(obj["_"+spec] == "1"))
            except:
                pass
        return flags

    def Load(self, filename):
        self.m_waypoints = []

        f = open(filename, "rb")

        # Info on the 'struct' object: http://www.python.org/doc/current/lib/module-struct.html
        # filetype = f.read(8) Fred
        # Read the header
        filetype = f.read(8)
        waypoint_file_version, waypoint_file_flags, number_of_waypoints = struct.unpack("iii", f.read(4*3))
        mapname = f.read(32)

        # Check the header
        if (filetype != "HPB_bot\x00"):
            raise "Fail in file-header: Not 'HPB_bot', but '" + filetype + "'"
        if (waypoint_file_version != 4):
            raise "Fail in file-header: Not version '4', but '" + str(waypoint_file_version) +"'"

        # Read waypoint-coordinates
        for wp in range(number_of_waypoints):
            flags, vecx, vecy, vecz = struct.unpack("ifff", f.read(4 + (4*3)))

            obj = quarkx.newobj("dup botwaypointerpoint:d")
            obj["macro"] = "dup botwaypointerpoint"
            obj["origin"] = str(vecx)+" "+str(vecy)+" "+str(vecz)
            obj.translate(quarkx.vect(0, 0, 0))
            obj["targetname"] = "wp"+str(wp)
            self.FlagsToSpecs(flags, obj)

            self.m_waypoints.append(obj)

        # Read waypoint-paths
        for wp in range(number_of_waypoints):
            obj = self.m_waypoints[wp]
            num, = struct.unpack("H", f.read(2))
            for p in range(num):
                wp_idx, = struct.unpack("H", f.read(2))
                obj["target"+str(p)] = "wp"+str(wp_idx)

        f.close()

    def Save(self, filename):
        f = open(filename, "wb")

        # Write the header
        f.write("HPB_bot\x00")
        f.write(struct.pack("iii", 4, 0, len(self.m_waypoints)))
        data = filename.split("\\")[-1]
        data = data.split(".")[0]
        data = data + "\x00"*(31-len(data))+"\x00"
        f.write(data)

        # Write waypoint-coordinates
        for wp in range(len(self.m_waypoints)):
            obj = self.m_waypoints[wp]

            flags = self.SpecsToFlags(obj)
            f.write(struct.pack("i", flags))

            vecx, vecy, vecz = quarkx.vect(obj["origin"]).tuple
            f.write(struct.pack("fff", vecx, vecy, vecz))

        # Write waypoint-paths
        for wp in range(len(self.m_waypoints)):
            obj = self.m_waypoints[wp]
            p = 0
            wp_idxs = ""
            for i in range(16):
                arg = obj["target"+str(i)]
                if ((arg is not None) and (arg != "")):
                    for o in range(len(self.m_waypoints)):
                        if (self.m_waypoints[o]["targetname"] == arg):
                            wp_idxs = wp_idxs + struct.pack("H", o)
                            p = p + 1
                            break
            f.write(struct.pack("H", p))
            f.write(wp_idxs)

        f.close()

#
# Class to load/save ACEBot/LTKBot waypoint files
#
class BotWaypointConvertACE(BotWaypointConverter):
    "ACEBot .LTK file load/save"

    m_ACE_types = \
        [(0 ,"MOVE"         ,"" ) \
        ,(1 ,"LADDER"       ,"" ) \
        ,(2 ,"PLATFORM"     ,"" ) \
        ,(3 ,"TELEPORTER"   ,"" ) \
        ,(4 ,"ITEM"         ,"" ) \
        ,(5 ,"WATER"        ,"" ) \
        ,(6 ,"GRAPPLE"      ,"" ) \
        ,(7 ,"JUMP"         ,"" ) \
        ,(8 ,"DOOR"         ,"" ) \
	,(99 ,"ALL"         ,"" ) \
	,(-1 ,"INVALID"     ,"" ) \
	,(9 ,"DANGER"       ,"" ) \
        ]


	 # This code is not compitable with Aq2 Bot release 0.6 only 0.5.x and any LTK version
	 #, dont mail the authour about this.
	 # Info about the DataTypes: 
	 # about this
	 #,(6 ,"GRAPPLE"      ,"" ) \ Data Type
	 #,(99 ,"ALL"         ,"" ) \ Data Type
	 #,(-1 ,"INVALID"     ,"" ) \ Invalid Link
         #,(9 ,"DANGER"       ,"" ) \ Danger Zone part of BotRelease a ltk successor.
	 # "Data Type" is not used in ltk or Bot release versions, but they
	 # are still a part of it's compressor.
	 # data should not be ignored.
	 # Ltk bot and Bot Release 0.5.x and higher "IF" link invalid 
         # the editor is aware of it and dont compress the data in a invalid
         # structure. - Fred 
					  
					   
    def TypeToSpec(self, master_type, obj):
        for type, spec, hint in self.m_ACE_types:
            if (type == master_type):
                obj["type"] = spec
                break

    def SpecToType(self, obj):
        for type, spec, hint in self.m_ACE_types:
            if (obj["type"] == spec):
                return type
        raise "ACEBot: Unknown spec-for-type: '"+obj["type"]+"'"

    def Load(self, filename):
        self.m_waypoints = []

        f = open(filename, "rb")

        # Read the header
        version, = struct.unpack("i", f.read(4)) # int

        # Check the header
        if (version != 4):
            raise "Fail in file-header: Not version '4', but '" + str(version) + "'"

        num_of_nodes, = struct.unpack("i", f.read(4))    # int
        num_of_items, = struct.unpack("i", f.read(4))    # int

        # setup a progress-indicator
        progressbar = quarkx.progressbar(509, (num_of_nodes * 2) + num_of_items)
        try:

            # read nodes
            for i in range(num_of_nodes):
                progressbar.progress()
                vecx, vecy, vecz = struct.unpack("fff", f.read(4*3))    # vec3_t
                node_type, = struct.unpack("i", f.read(4))              # int
                node_num, dummy = struct.unpack("hh", f.read(2+2))      # short int (+ 'short int' padded)

                obj = quarkx.newobj("dup botwaypointerpoint:d")
                obj["macro"] = "dup botwaypointerpoint"
                obj["origin"] = str(vecx)+" "+str(vecy)+" "+str(vecz)
                obj.translate(quarkx.vect(0, 0, 0))
                obj["targetname"] = "wp"+str(node_num)
                self.TypeToSpec(node_type, obj)

                for j in range(12):     # 12 = MAXLINKS
                    target_node, dummy, cost = struct.unpack("hhf", f.read(2+2+4)) # short int (+ 'short int' padded) float

                    if (target_node > 0):
                        obj["target"+str(j)] = "wp"+str(target_node)
                        obj["target"+str(j)+"_cost"] = str(int(cost))

                self.m_waypoints.append(obj)

            # read path_table, and compress it into minimal number of specs.
            for i in range(num_of_nodes):
                progressbar.progress()
                obj = self.m_waypoints[i]
                for j in range(num_of_nodes):
                    path_to_node, = struct.unpack("h", f.read(2)) # short int
                    if (path_to_node >= 0):
                        try:
                            value = obj["via_wp"+str(path_to_node)+"_to"] + ";" + "wp"+str(j)
                        except:
                            value = "wp"+str(j)
                        obj["via_wp"+str(path_to_node)+"_to"] = value

            # read items
            for i in range(num_of_items):
                progressbar.progress()
                item, weight, ent_ptr, node = struct.unpack("ifii", f.read(4 + 4 + 4 + 4))

        finally:
            progressbar.close()

        f.close()

    def Save(self, filename):
        f = open(filename, "wb")

        # Write the header
        f.write(struct.pack("i", 4)) # int - version 4

        num_of_nodes = len(self.m_waypoints)
        num_of_items = 0

        data = struct.pack("i", num_of_nodes) + struct.pack("i", num_of_items) # int int
        f.write(data)

        # Build translation-table for 'targetnames_to_nodenum'
        targetnames_to_nodenum = {}
        for i in range(num_of_nodes):
            obj = self.m_waypoints[i]
            targetnames_to_nodenum[obj["targetname"]] = i

        # setup a progress-indicator
        progressbar = quarkx.progressbar(5450, (num_of_nodes * 2) + num_of_items)
        try:

            # Write nodes
            for i in range(num_of_nodes):
                progressbar.progress()
                obj = self.m_waypoints[i]

                try:
                    vecx, vecy, vecz = quarkx.vect(obj["origin"]).tuple
                    f.write(struct.pack("fff", vecx, vecy, vecz))
                except:
                    raise "Error writing origin for "+obj["targetname"]

                try:
                    f.write(struct.pack("i", self.SpecToType(obj)))
                except:
                    raise "Error writing type for "+obj["targetname"]

                try:
                    node_num = targetnames_to_nodenum[obj["targetname"]]
                    dummy = 0
                    f.write(struct.pack("hh", node_num, dummy))
                except:
                    raise "Error writing node_num for "+obj["targetname"]

                cnt = 12
                for j in range(12):
                    target_node = obj["target"+str(j)]
                    cost = obj["target"+str(j)+"_cost"]
                    if ((target_node is not None) and (target_node != "")):
                        try:
                            node_num = targetnames_to_nodenum[target_node]
                            dummy = 0
                            f.write(struct.pack("hhf", node_num, dummy, float(cost))) # short int (+ 'short int' padded) float
                            cnt = cnt - 1
                        except:
                            raise "Error writing nodelist #"+str(j)+" for "+obj["targetname"]
                for j in range(cnt):
                    f.write(struct.pack("hhf", -1, 0, 0))

            # Write path_table. Uncompress it from its minimal 'structure'
            for i in range(num_of_nodes):
                progressbar.progress()
                obj = self.m_waypoints[i]

                node_path = []
                for j in range(num_of_nodes):
                    node_path = node_path + [int(-1)]

                for spec in obj.dictspec.keys():
                    if (spec[:4] == "via_"):
                        wp_num = spec.split("_")[1]
                        via_node_num = targetnames_to_nodenum[wp_num]
                        arg = obj[spec]
                        for wp_num in arg.split(";"):
                            node_path[targetnames_to_nodenum[wp_num]] = via_node_num

                for j in range(num_of_nodes):
                    f.write(struct.pack("h", node_path[j]))

            # Write items
            for i in range(num_of_items):
                progressbar.progress()

        finally:
            progressbar.close()

        f.close()

#
# Supported file-extension types
# added code for the new Bot release 0.6.0 and greater, when it is aviable
gBotFileExtFilter = ["Supported bot-types|*.wpt;*.ltk", "HPBBot (*.wpt)|*.wpt", "LTKBot/BR 0.5.1 (*.ltk)|*.ltk"]
#gBotFileExtFilterNew = ["Supported bot-types|*.nav", "Bot Release 0.6.x (*.nav)"]

#
# Load macro
#
def macro_botwaypointer_loadfile(self):
    editor = mapeditor()
    if editor is None:
        return
    dup = editor.layout.explorer.uniquesel
    if dup is None:
        return
 
    files = quarkx.filedialogbox("Load bot waypoint file...", "", gBotFileExtFilter, 0, "*.*")
    if len(files) == 1:
        files[0] = files[0].lower()
        if (files[0][-3:] == "wpt"):
            aObj = BotWaypointConvertHPB()
        elif (files[0][-3:] == "ltk"):
            aObj = BotWaypointConvertACE()
        else:
            raise "File-extension not supported '"+files[0][-3:]+"'."

# This is for future releases of Bot Release 0.6.0 and newer
# Fred www.franva.org
    #files = quarkx.filedialogbox("Load bot waypoint file...", "", gBotFileExtFilterNew, 0, "*.*")
    #if len(files) == 1:
        #files[0] = files[0].lower()
        #if (files[0][-3:] == "nav"):
            #aObj = BotWaypointConvertACE()
        #else:
            #raise "File-extension not supported '"+files[0][-3:]+"'."

        aObj.Load(files[0])

        # Setup undo/redo possibility
        undo = quarkx.action()

        undo.setspec(dup, "last_file", files[0])

        # Remove old waypoints (everything below the selected duplicator-object)
        for d in dup.subitems:
            undo.exchange(d, None)

        # Add the new waypoints
        for w in aObj.m_waypoints:
            undo.put(dup, w)

        # Do the undo/redo stuff, and redraw the views.
        editor.ok(undo, 'Load bot waypoint file')

        editor.layout.explorer.sellist = [dup]
        editor.invalidateviews()

quarkpy.qmacro.MACRO_botwaypointer_loadfile = macro_botwaypointer_loadfile

#
# Save macro
#
def macro_botwaypointer_savefile(self):
    editor = mapeditor()
    if editor is None:
        return
    dup = editor.layout.explorer.uniquesel
    if dup is None:
        return

    last_file = dup["last_file"]

    files = quarkx.filedialogbox("Save bot waypoint file...", "", gBotFileExtFilter, 1, last_file)
    if len(files) == 1:
        files[0] = files[0].lower()
        if (files[0][-3:] == "wpt"):
            aObj = BotWaypointConvertHPB()
        elif (files[0][-3:] == "ltk"):
            aObj = BotWaypointConvertACE()
        else:
            raise "File-extension not supported '"+files[0][-3:]+"'."

        dup["last_file"] = files[0]

        # Store the waypoints
        for w in dup.subitems:
            aObj.m_waypoints.append(w)

        aObj.Save(files[0])

quarkpy.qmacro.MACRO_botwaypointer_savefile = macro_botwaypointer_savefile


#
#
#
colors = [0xB00000,
          0x00B000,
          0x0000B0,
          0xB0B000,
          0x00B0B0,
          0xB000B0,
          0xB0B0B0]

def FindEntityByTargetname(name, list):
    for e in list:
        if (e["targetname"] == name):
            return e
    return None

def ShortestRouteTree(view, cv, obj, waypoints, cnt=0):
    if (cnt >= 90):
        # a simple test to ensure we don't get into an endless loop
        print "Possible cyclic path:", cnt, obj["targetname"], waypoints
        if (cnt >= 100):
            # stop traversing
            return 1

    pp2 = view.proj(obj.origin)
    for spec in obj.dictspec.keys():
        if (spec[0:4] == "via_"):
            viaobj = FindEntityByTargetname(spec.split("_")[1], obj.treeparent.subitems)
            if (viaobj is not None):
                routes = obj[spec].split(";")

                # Use only those waypoint-names, which exists in both lists ('routes' and 'waypoints').
                def isinlist(wp, routes=routes):
                    if wp in routes:
                        return 1
                    return 0
                theseroutes = filter(isinlist, waypoints)

                # Remove from the 'waypoints' list, those waypoint-names who also exists in the 'theseroutes' list.
                def isnotinlist(wp, theseroutes=theseroutes):
                    if wp in theseroutes:
                        return 0
                    return 1
                newwaypoints = filter(isnotinlist, waypoints)
                waypoints = newwaypoints

                # If there are any waypoint-names in 'theseroutes' list, traverse them too.
                if (len(theseroutes) > 0):
                    cv.line(view.proj(viaobj.origin), pp2)
                    if (ShortestRouteTree(view, cv, viaobj, theseroutes, cnt+1) != 0):
                        return 1
    return 0

#
#
#
def FindSelectedOne(list):
    for e in list:
        if (e.selected):
            return e
    return None

#
#
#
class BotWaypointerPointHandle(CenterHandle):

    def __init__(self, points_to_list, routes_to_list, pos, centerof, color=RED, caninvert=0):
        CenterHandle.__init__(self, pos, centerof, color, caninvert)
        self.points_to_list = points_to_list
        self.routes_to_list = routes_to_list
        self.hint = "'"+centerof["targetname"]+"' = targetname.||The black thin arrows, shows which other waypoints this one directly points to, by using its 'target##' specifics.\n\nThe thick colored lines illustrates its nearest neighbours, which are used for the shortest-path-matrix, by using its 'via_wp###_to' specifics."

    def draw(self, view, cv, draghandle=None):
        myparent = self.centerof.treeparent
        myself = self.centerof
        if (myself.selected):
            myparent["lastwaypointorigin"] = myself["origin"]
        if (myparent["shortestpathdisplay"] == "1"):
            if (myself.selected):
                nextclr = 0
                for spec in myself.dictspec.keys():
                    if (spec[0:4] == "via_"):
                        cv.pencolor = colors[nextclr]
                        nextclr = (nextclr + 1) % 6
                        viaobj = FindEntityByTargetname(spec.split("_")[1], myparent.subitems)
                        if (viaobj is not None):
                            pp2 = view.proj(viaobj.origin)
                            cv.penwidth = 3
                            cv.line(view.proj(self.pos), pp2)
                            cv.penwidth = 1
                            via_routes = myself[spec].split(";")
                            if (ShortestRouteTree(view, cv, viaobj, via_routes) != 0):
                                raise "Possible cyclic path"
                           #for wp in via_routes:
                           #    obj = FindEntityByTargetname(wp, myparent.subitems)
                           #    if (obj is not None):
                           #        cv.line(view.proj(obj.origin), pp2)
        else:
            if (self.routes_to_list is not None):
                cv.penwidth = 3
                nextclr = 0
                pp2 = view.proj(self.pos)
                for route_to in self.routes_to_list:
                    cv.pencolor = colors[nextclr]
                    nextclr = (nextclr + 1) % 6
                    cv.line(view.proj(route_to), pp2)
        if (self.points_to_list is not None):
            cv.pencolor = 0
            cv.penwidth = 1
            for point_to in self.points_to_list:
                Arrow(cv, view, self.pos, point_to)
        CenterHandle.draw(self, view, cv, draghandle)


    def menu(self, editor, view):

        def AddTwoWayClick(m, self=self, editor=editor):
            myparent = self.centerof.treeparent
            myself   = self.centerof
            theSelected = FindSelectedOne(myparent.subitems)
            if (theSelected is not None):
                undo = quarkx.action()

                try:
                    use_specname = None
                    use_num = 0
                    for spec in theSelected.dictspec.keys():
                        if (spec[:6] == "target" and spec != "targetname"):
                            if (theSelected[spec] == myself["targetname"]):
                                raise "already exist"
                            if (theSelected[spec] is None or theSelected[spec] == ""):
                                use_specname = spec
                            use_num = max(use_num, int(spec[6:]))
                    if (use_specname is None):
                        use_specname = "target" + str(use_num + 1)
                    undo.setspec(theSelected, use_specname, myself["targetname"])
                except:
                    pass

                try:
                    use_specname = None
                    use_num = 0
                    for spec in myself.dictspec.keys():
                        if (spec[:6] == "target" and spec != "targetname"):
                            if (myself[spec] == theSelected["targetname"]):
                                raise "already exist"
                            if (myself[spec] is None or myself[spec] == ""):
                                use_specname = spec
                            use_num = max(use_num, int(spec[6:]))
                    if (use_specname is None):
                        use_specname = "target" + str(use_num + 1)
                    undo.setspec(myself, use_specname, theSelected["targetname"])
                except:
                    pass

                undo.ok(editor.Root, "add two-way target")
                editor.invalidateviews()

        def AddOneWayClick(m, self=self, editor=editor):
            myparent = self.centerof.treeparent
            myself   = self.centerof
            theSelected = FindSelectedOne(myparent.subitems)
            if (theSelected is not None):
                undo = quarkx.action()

                try:
                    use_specname = None
                    use_num = 0
                    for spec in theSelected.dictspec.keys():
                        if (spec[:6] == "target" and spec != "targetname"):
                            if (theSelected[spec] == myself["targetname"]):
                                raise "already exist"
                            if (theSelected[spec] is None or theSelected[spec] == ""):
                                use_specname = spec
                            use_num = max(use_num, int(spec[6:]))
                    if (use_specname is None):
                        use_specname = "target" + str(use_num + 1)
                    undo.setspec(theSelected, use_specname, myself["targetname"])
                except:
                    pass

                undo.ok(editor.Root, "add two-way target")
                editor.invalidateviews()

        def RemTwoWayClick(m, self=self, editor=editor):
            myparent = self.centerof.treeparent
            myself   = self.centerof
            theSelected = FindSelectedOne(myparent.subitems)
            if (theSelected is not None):
                undo = quarkx.action()
                for spec in theSelected.dictspec.keys():
                    if (theSelected[spec] == myself["targetname"]):
                        undo.setspec(theSelected, spec, None)
                for spec in myself.dictspec.keys():
                    if (myself[spec] == theSelected["targetname"]):
                        undo.setspec(myself, spec, None)
                undo.ok(editor.Root, "remove two-way target")
                editor.invalidateviews()

        def RemOneWayClick(m, self=self, editor=editor):
            myparent = self.centerof.treeparent
            myself   = self.centerof
            theSelected = FindSelectedOne(myparent.subitems)
            if (theSelected is not None):
                undo = quarkx.action()
                for spec in theSelected.dictspec.keys():
                    if (theSelected[spec] == myself["targetname"]):
                        undo.setspec(theSelected, spec, None)
                undo.ok(editor.Root, "remove one-way target")
                editor.invalidateviews()

        def ShortestPathDisplayClick(m, self=self, editor=editor):
            myparent = self.centerof.treeparent
            shortestpathdisplay = not int(myparent["shortestpathdisplay"])
            m.state = quarkpy.qmenu.checked and shortestpathdisplay
            myparent["shortestpathdisplay"] = str(shortestpathdisplay)
            editor.invalidateviews()

        myparent = self.centerof.treeparent

        menu_add_twoway = quarkpy.qmenu.item("Add two-way target",    AddTwoWayClick, "|stuff to type here...")
        menu_add_oneway = quarkpy.qmenu.item("Add one-way target",    AddOneWayClick, "|stuff to type here...")
        menu_rem_twoway = quarkpy.qmenu.item("Remove two-way target", RemTwoWayClick, "|stuff to type here...")
        menu_rem_oneway = quarkpy.qmenu.item("Remove one-way target", RemOneWayClick, "|stuff to type here...")

        theSelected = FindSelectedOne(myparent.subitems)

        # Enable/disable menu-items depending on the state and spec/args of the two in question.
        if (theSelected is None or theSelected == self.centerof):
            menu_add_twoway.state = quarkpy.qmenu.disabled
            menu_add_oneway.state = quarkpy.qmenu.disabled
            menu_rem_twoway.state = quarkpy.qmenu.disabled
            menu_rem_oneway.state = quarkpy.qmenu.disabled
        else:
            # Figure out, who targets who.
            myself_targetname       = self.centerof["targetname"]
            theselected_targetname  = theSelected["targetname"]
            i_target_selected   = 0
            selected_targets_me = 0
            for spec in self.centerof.dictspec.keys():
                if (spec[:6] == "target" and self.centerof[spec] == theselected_targetname):
                    i_target_selected = 1
                    break
            for spec in theSelected.dictspec.keys():
                if (spec[:6] == "target" and theSelected[spec] == myself_targetname):
                    selected_targets_me = 1
                    break
            menu_add_twoway.state = not (not i_target_selected or not selected_targets_me) and quarkpy.qmenu.disabled
            menu_add_oneway.state = not (not selected_targets_me)                          and quarkpy.qmenu.disabled
            menu_rem_twoway.state = not (i_target_selected and selected_targets_me)        and quarkpy.qmenu.disabled
            menu_rem_oneway.state = not (selected_targets_me)                              and quarkpy.qmenu.disabled

        # Set up 'shortest path display' menuitem-checkbox
        menu_shortestpath = quarkpy.qmenu.item("Path display. WARNING, this is a slow process", ShortestPathDisplayClick, "|stuff to type here...")
        try:
            shortestpathdisplay = int(myparent["shortestpathdisplay"])
        except:
            shortestpathdisplay = 0
        myparent["shortestpathdisplay"] = str(shortestpathdisplay)
        menu_shortestpath.state = quarkpy.qmenu.checked and shortestpathdisplay

        return [menu_add_twoway, menu_add_oneway, menu_rem_twoway, menu_rem_oneway, qmenu.sep, menu_shortestpath]

#
#
#
class BotWaypointerPoint(DuplicatorManager):

    def buildimages(self, singleimage=None):
        pass

    def handles(self, editor, view):
        myparent = self.dup.treeparent
        myself = self.dup
        hndls = []

        # Examine the spec/args for directly associated waypoints to myself
        points_to_list = []
        routes_to_list = []
        to_list = []
        for spec in myself.dictspec.keys():
            if (spec[:6] == "target" and myself[spec] is not None and myself[spec] != ""):
                points_to = FindEntityByTargetname(myself[spec], myparent.subitems)
                if (points_to is not None):
                    points_to_list.append(points_to.origin)
                    if (points_to not in to_list):
                        to_list.append(points_to)
            if (spec[:4] == "via_" and myself[spec] is not None and myself[spec] != ""):
                routes_to = FindEntityByTargetname(spec.split("_")[1], myparent.subitems)
                if (routes_to is not None):
                    routes_to_list.append(routes_to.origin)
                    if (routes_to not in to_list):
			    points_to_list.append
			    

        # First add the selected handle, so it will be drawn first (z-order of drawn lines)
        hndls.append(BotWaypointerPointHandle(points_to_list, routes_to_list, self.dup.origin, self.dup))

        # Then append those found in the spec/args.
        def createhandle(o):
            return BotWaypointerPointHandle(None, None, o.origin, o)
        hndls = hndls + map(createhandle, to_list)

        # Lastly show also the rest within a sphere of 512 units
        for obj in myparent.subitems:
            if (obj in hndls):
                # Don't take objects with twice!
                continue
            if abs(obj.origin - self.dup.origin) < 512:
                # Only those within 512 units
                hndls.append(BotWaypointerPointHandle(None, None, obj.origin, obj))

        # And return the list of handles
        return hndls


#
#
#
class BotWaypointer(StandardDuplicator):

    def buildimages(self, singleimage=None):
        # Don't allow dissociate images to work
        if (singleimage is not None):
            return []
        # Local function to create dummy entity, so the waypoints become visible in the 2D-views
        # without the need to have this duplicator selected.
        def makeentitiy(obj):
            newobj = quarkx.newobj("info_waypoint:e")
            newobj["origin"] = str(obj.origin)
            newobj.translate(quarkx.vect(0, 0, 0)) # damn - if this isn't here, the entities will not show in the views
            return newobj
        # Create the list of dummy entities
        botwaypointerpointentities = map(makeentitiy, self.dup.subitems)
        return botwaypointerpointentities

    def handles(self, editor, view):
        def makehandle(obj):
            return quarkpy.qhandles.CenterHandle(obj.origin, obj)
        botwaypointerpointhandles = map(makehandle, self.dup.subitems)
        return botwaypointerpointhandles

#
#
#
def NewWaypointTargetname(list):
    MaxNum = 0
    for e in list:
        if (e["targetname"][:2] == "wp"):
            Num = int(e["targetname"][2:])
            if (Num > MaxNum):
                MaxNum = Num
    MaxNum = MaxNum + 1
    MaxTargetname = "wp" + str(MaxNum)

    return MaxTargetname

#
#
#
def PasteBotWaypointClick(m):
    editor = mapeditor()
    if (editor is None):
        return
    # Check that the correct object is in the ClipBoard
    clipboard = quarkx.pasteobj(1)
    if ((len(clipboard) != 1) or (clipboard[0]["macro"] != "dup botwaypointerpoint")):
        quarkx.msgbox("Clipboard does not contain exactly one 'dup botwaypointerpoint' entity.", MT_ERROR, MB_OK)
        return
    # Find our master 'Bot Waypointer' (must be only one named like that)
    masters = editor.Root.findallsubitems("Bot Waypointer", ':d')
    if (len(masters) != 1):
        if (len(masters) > 1):
            quarkx.msgbox("A single 'Bot Waypointer' entity could not be determined. Please remove or rename the ones you are not editing for to something else.", MT_ERROR, MB_OK)
        else:
            quarkx.msgbox("Could not find a 'Bot Waypointer' entity. May it have been renamed to something else?", MT_ERROR, MB_OK)
        return
    master = masters[0]

    #
    newobj = clipboard[0].copy()
    x, y, z = m.pos.x, m.pos.y, m.pos.z
    mx, my, mz = tuple(master["lastwaypointorigin"].split())
    if   m.view.info["type"] == "XY": z = float(mz)
    elif m.view.info["type"] == "XZ": y = float(my)
    elif m.view.info["type"] == "YZ": x = float(mx)
    newobj["origin"] = str(editor.aligntogrid(quarkx.vect(x, y, z)))
    newobj.translate(quarkx.vect(0, 0, 0)) # damn - if this isn't here, the entity will not show in the views
    newobj["targetname"] = NewWaypointTargetname(master.subitems)

    undo = quarkx.action()
    undo.put(master, newobj, None)
    undo.setspec(master, "lastwaypointorigin", newobj["origin"])
    undo.ok(editor.Root, "paste waypoint")
    editor.layout.actionmpp()

#
#
#
def backmenu(editor, view=None, origin=None, oldbackmenu=quarkpy.mapmenus.BackgroundMenu):
    # Build the normal context-menu
    menu = oldbackmenu(editor, view, origin)
    # Create a new menu-item, and store the cursor's origin in it.
    menupastebotwaypoint = quarkpy.qmenu.item("&Paste waypoint", PasteBotWaypointClick, "|To paste a bot waypoint, you must first have copied (CTRL+C) a single 'dup botwaypointerpoint' entity into the clipboard.\n\nThis action also creates a new targetname for the waypoint, and keeps it aligned with the previous waypoint selected.|intro.mapeditor.rmb_menus.noselectionmenu.html#botwaypointer")
    menupastebotwaypoint.pos = origin
    menupastebotwaypoint.view = view
    # If there is nothing to paste, disable the menu (note: it could be anything in the clipboard,
    # but we'll test agains that once the user actully performs the action)
    if ((quarkx.pasteobj(0) == 0) or (view is None) or (origin is None)):
        menupastebotwaypoint.state = quarkpy.qmenu.disabled
    # Create a sub-menu that contains the Bot waypointer special menuitems
    popup = quarkpy.qmenu.popup("&Bot waypointer", [menupastebotwaypoint])
    # Put the new sub-menu on top of the context-menu list, and return the lot...
    menu[:0] = [popup]
    return menu

quarkpy.mapmenus.BackgroundMenu = backmenu

#
#
#
quarkpy.mapduplicator.DupCodes.update({
  "dup botwaypointer":       BotWaypointer,
  "dup botwaypointerpoint":  BotWaypointerPoint,
})

# ----------- REVISION HISTORY ------------
#$Log: mapbotwaypointer.py,v $
#Revision 1.13  2006/05/19 17:07:53  cdunde
#To add links to docs on RMB menus and background image function.
#
#Revision 1.12  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.9  2005/07/03 17:41:58  alexander
#fixed logging line in footer
#
#
# Revision 1.7  2005/06/29 13:04:56  cdunde
# Fred -Fixed a bug with the waypoint savings "missing datatypes".
# Added code for future releases of Bot Release 0.6.0 which
# is the latest Aq2 community bot out there.
#
# Revision 1.6  2005/04/12 00:17:04  cdunde
# One last fix by Fred
# 
# Revision 1.5 2005/11/4 01:30 Fred
# Fixed possible the last bug.
#
# Revision 1.4 2005/10/4 01:30 Fred
# Fixed a bug wich had been introduced in a later release
# 
# Revision 1.8  2005/06/29 13:35:09  cdunde
# To try and fix version numbering.
#
# Revision 1.3  2003/12/18 21:51:46  peter-b
# Removed reliance on external string library from Python scripts (second try ;-)
#
# Revision 1.2  2002/08/02 19:17:08  decker_dk
# Uhm... Lots of things changed, of which I've forgotten.
#
# Revision 1.1  2002/06/11 17:12:57  decker_dk
# A Bot waypoint-editor. At the moment only works for HPBBot(Half-Life) and LTK/ACEBot(Quake-2)
#
