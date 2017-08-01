""" QuArK  -  Quake Army Knife

  Utility functions by Decker@post1.tele.dk
"""
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/plugins/deckerutils.py,v 1.11 2008/05/27 19:33:14 danielpharos Exp $
#

import quarkx
import quarkpy.mapentities
ObjectOrigin = quarkpy.mapentities.ObjectOrigin

def FindOriginTexPolyPos(entity):
    "Find origin by searching for poly under entity which has the ORIGIN texture"
    subpolys = entity.findallsubitems("", ":p", ":g")
    for i in subpolys:
        subfaces = i.findallsubitems("",":f",":g");
        # Make sure that all faces on poly contains the ORIGIN texture
        foundoriginpoly=1
        for j in subfaces:
            if not j["tex"]=="ORIGIN": # If just one face does not contain the ORIGIN texture, its not an origin-poly
                foundoriginpoly=0
                break
        if foundoriginpoly==1:
            return ObjectOrigin(i) # give me the origin of the poly
    return None

def FindOriginTexPolyPos2(entity):
    "Find origin by searching for poly under entity which has the common/origin texture"
    subpolys = entity.findallsubitems("", ":p", ":g")
    for i in subpolys:
        subfaces = i.findallsubitems("",":f",":g");
        # Make sure that all faces on poly contains the common/origin texture
        foundoriginpoly=1
        for j in subfaces:
            if not j["tex"]=="common/origin": # If just one face does not contain the common/origin texture, its not an origin-poly
                foundoriginpoly=0
                break
        if foundoriginpoly==1:
            return ObjectOrigin(i) # give me the origin of the poly
    return None

def FindOriginFlagPolyPos(entity):
    "Find origin by searching for poly under entity which has the Origin-texture-flag set"
    subpolys = entity.findallsubitems("", ":p", ":g")
    for i in subpolys:
        subfaces = i.findallsubitems("",":f",":g");
        # Make sure that all faces on poly contains the Origin-texture-flag
        foundoriginpoly, flags = 1, 0
        for j in subfaces:
            try:
                flags = int(j["Contents"])
            except:
                flags = 0
            if not (flags & 16777216): # If just one face does not contain the Origin-texture-flag, its not an origin-poly
                foundoriginpoly=0
                break
        if foundoriginpoly==1:
            return ObjectOrigin(i) # give me the origin of the poly
    return None

def NewXYZCube(x,y,z,tex):
    p = quarkx.newobj("poly:p")
    x,y,z = x*0.5, y*0.5, z*0.5

    f = quarkx.newobj("east:f");   f["v"] = (x, -x, -x, x, 128-x, -x, x, -x, 128-x)
    f["tex"] = tex
    p.appenditem(f)

    f = quarkx.newobj("west:f");   f["v"] = (-x, -x, -x, -x, -x, 128-x, -x, 128-x, -x)
    f["tex"] = tex             ;   f["m"] = "1"
    p.appenditem(f)

    f = quarkx.newobj("north:f");  f["v"] = (-y, y, -y, -y, y, 128-y, 128-y, y, -y)
    f["tex"] = tex              ;  f["m"] = "1"
    p.appenditem(f)

    f = quarkx.newobj("south:f");  f["v"] = (-y, -y, -y, 128-y, -y, -y, -y, -y, 128-y)
    f["tex"] = tex
    p.appenditem(f)

    f = quarkx.newobj("up:f");     f["v"] = (-z, -z, z, 128-z, -z, z, -z, 128-z, z)
    f["tex"] = tex
    p.appenditem(f)

    f = quarkx.newobj("down:f");   f["v"] = (-z, -z, -z, -z, 128-z, -z, 128-z, -z, -z)
    f["tex"] = tex             ;   f["m"] = "1"
    p.appenditem(f)

    return p


def GetEntityChain(firsttargetname, list):
    # Returns an ordered list of entities, which points to each other by target/targetname
    newlist = []
    for e in list:
        if e.type == ':g':
            newlist = newlist + e.findallsubitems("", ":e")
            newlist = newlist + e.findallsubitems("", ":b")
        else:
            newlist.append(e)

    def FindEntityByTargetname(name, list):
        for e in list:
            if (e["targetname"] == name):
                return e, e["target"]
        return None, None

    nextname = firsttargetname
    namelist = []
    entlist = []
    ent, nextname = FindEntityByTargetname(nextname, newlist)
    if (ent is not None):
        entlist.append(ent)
    while ((nextname is not None) and (not nextname in namelist)):
        namelist.append(nextname)
        ent, nextname = FindEntityByTargetname(nextname, newlist)
        if (ent is not None):
            entlist.append(ent)
    return entlist


def RegisterInToolbox(toolboxname, qtxfolder, obj):
# FIXME - Make so ':form' also can be added somewhere.
    toolboxes = quarkx.findtoolboxes(toolboxname)
    for t in toolboxes:
        for f in t[1].subitems:
            if (f.shortname == qtxfolder):
                # If object already is in toolbox, don't put it in again!
                o = f.findname(obj.name)
                if (o is None):
                    print "--adding"
                    f.appenditem(obj)
                return
        # Did not find a qtxfolder, create one
        newf = quarkx.newobj(qtxfolder+".qctx")
        print "--f"
        newf.appenditem(obj)
        print "--folder"
        t[1].parent.appenditem(newf)
        print "--folderadded"
        return

# ----------- REVISION HISTORY ------------
#$Log: deckerutils.py,v $
#Revision 1.11  2008/05/27 19:33:14  danielpharos
#Fix Delphi being called redundantly
#
#Revision 1.10  2008/05/25 21:55:04  cdunde
#Fixes and additions by X7 for rotation entities that use an origin brush.
#
#Revision 1.9  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.6  2001/01/06 18:33:52  decker_dk
#Use 4-spaces instead of 8-spaces 'tabs'
#
#Revision 1.5  2000/07/09 13:21:54  decker_dk
#New function
#
#Revision 1.4  2000/06/03 10:25:30  alexander
#added cvs headers
#
#Revision 1.3  2000/05/23 19:09:47  decker_dk
#Removed evil hidden TAB-characters
#
#
