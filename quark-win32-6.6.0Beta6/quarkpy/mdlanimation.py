"""   QuArK  -  Quake Army Knife

The Animation Toolbar Palette.
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#
#$Header: /cvsroot/quark/runtime/quarkpy/mdlanimation.py,v 1.27 2011/11/17 01:19:02 cdunde Exp $


import qmenu
from mdlutils import *
import qbaseeditor
import mdlhandles
import qtoolbar
import qmacro
from qeditor import *
from qdictionnary import Strings

# Globals
# =========
playlist = []
playlistPerComp = {} # Contains the components to animate.
playNR = 0
holdselection = None

def drawanimation(self):
    global playNR
    import mdleditor
    editor = mdleditor.mdleditor
    if editor is None:
        return
    FPS = int(1000/quarkx.setupsubset(SS_MODEL, "Display")["AnimationFPS"][0])
    if quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] is None:
        playNR = int(round(playNR))
    if quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] == "1":
        import mdlmgr
        if mdlmgr.treeviewselchanged == 1:
            for v in editor.layout.views:
                if v.info["viewname"] == "XY" and v.viewmode == "wire" and quarkx.setupsubset(SS_MODEL, "Options")['AnimateZ2Dview'] == "1":
                    mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()
                elif v.info["viewname"] == "XZ" and v.viewmode == "wire" and quarkx.setupsubset(SS_MODEL, "Options")['AnimateY2Dview'] == "1":
                    mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()
                elif v.info["viewname"] == "YZ" and v.viewmode == "wire" and quarkx.setupsubset(SS_MODEL, "Options")['AnimateX2Dview'] == "1":
                    mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()
                else:
                    pass
            mdlmgr.treeviewselchanged = 0
        return FPS
    else:
        if quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] is None:
            try:
                frame = playlist[playNR]
            except:
                return
            if playNR == len(playlist) - 1:
                playNR = 0
            else:
                playNR = playNR + 1

            ### CFG Animation additional section.
            if MdlOption("AnimationCFGActive"):
                for comp in playlistPerComp.keys():
                    try:
                        playlistPerComp[comp][0].currentframe = playlistPerComp[comp][1][playNR]
                    except:
                        continue
        else: ### Interpolation section.
            if editor.layout.explorer.sellist != [] and not MdlOption("AnimationCFGActive"):
                editor.layout.explorer.uniquesel = None
                editor.layout.explorer.sellist = []
                editor.layout.explorer.invalidate()

            IPF = float(1/quarkx.setupsubset(SS_MODEL, "Display")["AnimationIPF"][0])
            FPS = int(FPS*(IPF*2)) # Speeds up animation as IPF increases (causing slower drawing).
            if len(playlist) == 1:
                # Can't loop with just one frame
                playNR = 0.0
            else:
                playNR = playNR + IPF
                if quarkx.setupsubset(SS_MODEL, "Options")['SmoothLooping'] is not None:
                    while playNR >= len(playlist):
                        playNR = playNR - len(playlist)
                else:
                    while playNR >= len(playlist) - 1:
                        playNR = playNR - (len(playlist) - 1)
            OldFrameVertices = {}
            for comp_name in playlistPerComp.keys():
                try:
                    newframe = LinearInterpolation(editor, playlistPerComp[comp_name][1], playNR)
                except:
                    continue
                currentframe = playlistPerComp[comp_name][0].currentframe
                if currentframe is None:
                    currentframe = playlistPerComp[comp_name][0].dictitems['Frames:fg'].subitems[0]
                # Swap the original frame's vertices (saving them) with the interpolation calculated vertices.
                OldFrameVertices[comp_name] = currentframe.vertices
                # To catch sudden animation stop so original 1st frame does not get messed up, which was happening.
                if editor.layout is None or (not MdlOption("AnimationActive") and not MdlOption("AnimationCFGActive")):
                    quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] = None
                    playNR = 0
                    quarkx.settimer(drawanimation, self, 0)
                    editor.layout.explorer.sellist = playlist
                    return 0
                currentframe.vertices = newframe.vertices

        # To catch any mishaps.
        if editor.layout is None or (not MdlOption("AnimationActive") and not MdlOption("AnimationCFGActive")):
            quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] = None
            quarkx.settimer(drawanimation, self, 0)
            editor.layout.explorer.sellist = playlist
            return 0
        else:
            ### CFG Animation section.
            if MdlOption("AnimationCFGActive"):
                editor.invalidateviews()
            ### Standard Animation section.
            elif quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] is None:
                editor.layout.explorer.uniquesel = frame
                editor.layout.selchange
            ### Interpolation section.
            else:
                editor.invalidateviews()

            for v in editor.layout.views:
                if v.info["viewname"] == "XY" and v.viewmode == "wire" and quarkx.setupsubset(SS_MODEL, "Options")['AnimateZ2Dview'] == "1":
                    mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()
                elif v.info["viewname"] == "XZ" and v.viewmode == "wire" and quarkx.setupsubset(SS_MODEL, "Options")['AnimateY2Dview'] == "1":
                    mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()
                elif v.info["viewname"] == "YZ" and v.viewmode == "wire" and quarkx.setupsubset(SS_MODEL, "Options")['AnimateX2Dview'] == "1":
                    mdleditor.setsingleframefillcolor(editor, v)
                    v.repaint()

            ### Interpolation section.
            if quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] is not None:
                # Swap the original frame's vertices back.
                for comp_name in playlistPerComp.keys():
                    currentframe = playlistPerComp[comp_name][0].currentframe
                    if currentframe is None:
                        currentframe = playlistPerComp[comp_name][0].dictitems['Frames:fg'].subitems[0]
                    try:
                        currentframe.vertices = OldFrameVertices[comp_name]
                    except:
                        continue
            return FPS



class DeactivateAnimation(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the Animation toolbar functions on and off."
    Hint = hintPlusInfobaselink("", "")

class DeactivateAnimationCFG(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the AnimationCFG toolbar functions on and off."
    Hint = hintPlusInfobaselink("", "")

class PauseAnimation(mdlhandles.RectSelDragObject):
    "This is just a place holder to Play or Pause the Animation."
    Hint = hintPlusInfobaselink("", "")

class Editor3Dview(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the Editor's 3D view Animation on and off."
    Hint = hintPlusInfobaselink("", "")

class X2Dview(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the X 2D Back view Animation on and off."
    Hint = hintPlusInfobaselink("", "")

class Y2Dview(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the Y 2D Back view Animation on and off."
    Hint = hintPlusInfobaselink("", "")

class Z2Dview(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the Z 2D Back view Animation on and off."
    Hint = hintPlusInfobaselink("", "")

class Floating3Dview(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the Editor's Floating 3D view Animation on and off."
    Hint = hintPlusInfobaselink("", "")

class DeactivateInterpolation(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the Interpolation toolbar functions on and off."
    Hint = hintPlusInfobaselink("", "")

class DeactivateSmoothLooping(mdlhandles.RectSelDragObject):
    "This is just a place holder to turn the Smooth Looping toolbar functions on and off."
    Hint = hintPlusInfobaselink("", "")

##############################################################
#
# The tool bar with the available animation modes.
# Add other animation modes from other plug-ins into this list :
#
               ## (the_object                                  ,icon_index)
AnimationModes = [(DeactivateAnimation         ,0)
                 ,(DeactivateAnimationCFG     ,12)
                 ,(PauseAnimation              ,4)
                 ,(Editor3Dview                ,5)
                 ,(X2Dview                     ,6)
                 ,(Y2Dview                     ,7)
                 ,(Z2Dview                     ,8)
                 ,(Floating3Dview              ,9)
                 ,(DeactivateInterpolation    ,10)
                 ,(DeactivateSmoothLooping    ,11)
                 ]

### This part effects each buttons selection mode.

def selectmode(btn):
    editor = mapeditor(SS_MODEL)
    if editor is None: return
    try:
        tb1 = editor.layout.toolbars["tb_animation"]
    except:
        return
    for b in tb1.tb.buttons:
        b.state = qtoolbar.normal
    select1(btn, tb1, editor)
    quarkx.update(editor.form)
    quarkx.setupsubset(SS_MODEL, "Building").setint("AnimationMode", btn.i)

def select1(btn, toolbar, editor):
    editor.MouseDragMode, dummyicon = AnimationModes[btn.i]
    btn.state = qtoolbar.selected

def UpdateplaylistPerComp(self):
    import mdleditor, operator
    global playlistPerComp, playlist
    editor = mdleditor.mdleditor
    playlistPerComp = {}
    if len(playlist) == 0:
        return

    if MdlOption("AnimationCFGActive"):
        sel = playlist
        tags = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':tag')  # get all tags
        for item in range(len(sel)):
            if sel[item].type == ':tag' and sel[item].dictspec.has_key("play_list1"):
                group = sel[item].name.split("_")
                weapon = "None"
                if sel[item].dictspec.has_key("weapon"):
                    weapon = sel[item].dictspec['weapon']
                play_list1 = sel[item].dictspec['play_list1'].split(",")
                first_frame1 = int(play_list1[1])
                num_frames1 = int(play_list1[2])
                looping_frames1 = int(play_list1[3])
                CFG_FPS1 = int(play_list1[4]) # Not being used yet.

                if play_list1[0].startswith("TORSO_"): # Handles NON - "BOTH_" (combination) sequences.
                    TORSO_tagframes = sel[item].subitems
                    max_BOTH = int(play_list1[5])
                    max_TORSO = int(play_list1[6])
                    play_list2 = sel[item].dictspec['play_list2'].split(",")
                    first_frame2 = int(play_list2[1])
                    first_frame2 = first_frame2 - max_TORSO + max_BOTH
                    num_frames2 = int(play_list2[2])
                    looping_frames2 = int(play_list2[3])
                    CFG_FPS2 = int(play_list2[4]) # Not being used yet.
                    LEGS_origins = [] # A list of tagframe origins as vectors for the LEGS frames.
                    LEGS_matrix = [] # A list of tagframe matrixs as vectors for the LEGS frames.
                    TORSO_origins = [] # A list of tagframe origins as vectors for the TORSO frames.

                    for frameindex in range(first_frame2, first_frame2 + num_frames2):
                        LEGS_origins = LEGS_origins + [TORSO_tagframes[frameindex].dictspec['origin']]
                        LEGS_matrix = LEGS_matrix + [TORSO_tagframes[frameindex].dictspec['rotmatrix']]
                    for frameindex in range(first_frame1, first_frame1 + num_frames1):
                        TORSO_origins = TORSO_origins + [TORSO_tagframes[frameindex].dictspec['origin']]

                    for comp in editor.Root.subitems:
                        if comp.type == ":mc" and (comp.name.startswith(group[0]) or (weapon != "None" and comp.name.startswith(weapon))):  # or not comp.name.startswith(group[0]):  # Not a component
                            pass
                        else:
                            continue
                        try: # In case a component does not have any frames or the same number of frames, it won't break.
                            FrameGroup = comp.dictitems['Frames:fg'].subitems # Get all the frames for this component.
                            compname = comp.shortname.split("_")
                            if compname[1] == "l":
                                if num_frames2 >= num_frames1: # Equal or more frames in LEGS part.
                                    for frameindex in range(first_frame2, first_frame2 + num_frames2):
                                        if playlistPerComp.has_key(comp.name):
                                            playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [FrameGroup[frameindex]]
                                        else:
                                            playlistPerComp[comp.name] = [comp, [FrameGroup[frameindex]]]
                                else: # Handles the component's legs, LOWER part frames if the component's UPPER part has more frames.
                                    legs_frames = []
                                    for frameindex in range(first_frame2, first_frame2 + num_frames2):
                                        legs_frames = legs_frames + [FrameGroup[frameindex]]
                                    framecount = loop = loopcount = 0
                                    for frameindex in range(first_frame1, first_frame1 + num_frames1):
                                        if framecount > len(legs_frames)-1:
                                            if looping_frames2 == 0:
                                                extra_frame = legs_frames[len(legs_frames)-1].copy()
                                            else:
                                                frame_index = framecount - (len(legs_frames)*loop)
                                                extra_frame = legs_frames[frame_index].copy()
                                            if playlistPerComp.has_key(comp.name):
                                                playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [extra_frame]
                                            else:
                                                playlistPerComp[comp.name] = [comp, [extra_frame]]
                                        else:
                                            frame_copy = legs_frames[framecount].copy()
                                            if playlistPerComp.has_key(comp.name):
                                                playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [frame_copy]
                                            else:
                                                playlistPerComp[comp.name] = [comp, [frame_copy]]
                                        framecount = framecount + 1
                                        loopcount = loopcount + 1
                                        if loopcount == len(legs_frames):
                                            loop = loop + 1
                                            loopcount = 0

                                playlist = playlistPerComp[comp.name][1]

                            else: # Handles the component's UPPER parts frames if legs equal or has more frames.
                                comp_frames = []
                                for frameindex in range(first_frame1, first_frame1 + num_frames1):
                                    comp_frames = comp_frames + [FrameGroup[frameindex]]
                                framecount = loop = loopcount = 0
                                if num_frames2 >= num_frames1: # Equal or more frames in LEGS part.
                                    for frameindex in range(first_frame2, first_frame2 + num_frames2):
                                        if framecount > len(comp_frames)-1:
                                            if looping_frames1 == 0:
                                                vtx_old = quarkx.vect(TORSO_origins[len(comp_frames)-1])
                                                vtx_new = quarkx.vect(LEGS_origins[framecount])
                                                n_r = LEGS_matrix[framecount]
                                                n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                                new_rotation = quarkx.matrix(n_r)
                                                extra_frame = comp_frames[len(comp_frames)-1].copy()
                                            else:
                                                frame_index = framecount - (len(comp_frames)*loop)
                                                vtx_old = quarkx.vect(TORSO_origins[frame_index])
                                                vtx_new = quarkx.vect(LEGS_origins[framecount])
                                                n_r = LEGS_matrix[framecount]
                                                n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                                new_rotation = quarkx.matrix(n_r)
                                                extra_frame = comp_frames[frame_index].copy()
                                            vertices = []
                                            for vtx in extra_frame.vertices:
                                                vtx = vtx - vtx_old
                                                vtx = (~new_rotation) * vtx
                                                vtx = vtx + vtx_new
                                                vertices = vertices + [vtx]
                                            extra_frame.vertices = vertices
                                            if playlistPerComp.has_key(comp.name):
                                                playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [extra_frame]
                                            else:
                                                playlistPerComp[comp.name] = [comp, [extra_frame]]
                                        else:
                                            vtx_old = quarkx.vect(TORSO_origins[framecount])
                                            vtx_new = quarkx.vect(LEGS_origins[framecount])
                                            n_r = LEGS_matrix[framecount]
                                            n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                            new_rotation = quarkx.matrix(n_r)
                                            vertices = []
                                            frame_copy = comp_frames[framecount].copy()
                                            for vtx in frame_copy.vertices:
                                                vtx = vtx - vtx_old
                                                vtx = (~new_rotation) * vtx
                                                vtx = vtx + vtx_new
                                                vertices = vertices + [vtx]
                                            frame_copy.vertices = vertices
                                            if playlistPerComp.has_key(comp.name):
                                                playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [frame_copy]
                                            else:
                                                playlistPerComp[comp.name] = [comp, [frame_copy]]
                                        framecount = framecount + 1
                                        loopcount = loopcount + 1
                                        if loopcount == len(comp_frames):
                                            loop = loop + 1
                                            loopcount = 0

                                else: # Handles the component's UPPER parts frames if it has more frames then the legs.
                                    if num_frames2 >= num_frames1: # Equal or more frames in LEGS part.
                                        for frameindex in range(first_frame1, first_frame1 + num_frames1):
                                            if playlistPerComp.has_key(comp.name):
                                                playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [FrameGroup[frameindex]]
                                            else:
                                                playlistPerComp[comp.name] = [comp, [FrameGroup[frameindex]]]
                                    else: # More frames in UPPER part.
                                        legs_frames = []
                                        for frameindex in range(first_frame2, first_frame2 + num_frames2):
                                            legs_frames = legs_frames + [FrameGroup[frameindex]]
                                        for frameindex in range(first_frame1, first_frame1 + num_frames1):
                                            if framecount > len(legs_frames)-1:
                                                if looping_frames2 == 0:
                                                    vtx_old = quarkx.vect(TORSO_origins[framecount])
                                                    vtx_new = quarkx.vect(LEGS_origins[len(legs_frames)-1])
                                                    n_r = LEGS_matrix[len(legs_frames)-1]
                                                    n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                                    new_rotation = quarkx.matrix(n_r)
                                                    fixed_frame = comp_frames[framecount].copy()
                                                else:
                                                    frame_index = framecount - (len(legs_frames)*loop)
                                                    vtx_old = quarkx.vect(TORSO_origins[framecount])
                                                    vtx_new = quarkx.vect(LEGS_origins[frame_index])
                                                    n_r = LEGS_matrix[frame_index]
                                                    n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                                    new_rotation = quarkx.matrix(n_r)
                                                    fixed_frame = comp_frames[framecount].copy()
                                                vertices = []
                                                for vtx in fixed_frame.vertices:
                                                    vtx = vtx - vtx_old
                                                    vtx = (~new_rotation) * vtx
                                                    vtx = vtx + vtx_new
                                                    vertices = vertices + [vtx]
                                                fixed_frame.vertices = vertices
                                                if playlistPerComp.has_key(comp.name):
                                                    playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [fixed_frame]
                                                else:
                                                    playlistPerComp[comp.name] = [comp, [fixed_frame]]
                                            else:
                                                vtx_old = quarkx.vect(TORSO_origins[framecount])
                                                vtx_new = quarkx.vect(LEGS_origins[framecount])
                                                n_r = LEGS_matrix[framecount]
                                                n_r = ((n_r[0],n_r[1],n_r[2]), (n_r[3],n_r[4],n_r[5]), (n_r[6],n_r[7],n_r[8]))
                                                new_rotation = quarkx.matrix(n_r)
                                                vertices = []
                                                fixed_frame = comp_frames[framecount].copy()
                                                for vtx in fixed_frame.vertices:
                                                    vtx = vtx - vtx_old
                                                    vtx = (~new_rotation) * vtx
                                                    vtx = vtx + vtx_new
                                                    vertices = vertices + [vtx]
                                                fixed_frame.vertices = vertices
                                                if playlistPerComp.has_key(comp.name):
                                                    playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [fixed_frame]
                                                else:
                                                    playlistPerComp[comp.name] = [comp, [fixed_frame]]
                                            framecount = framecount + 1
                                            loopcount = loopcount + 1
                                            if loopcount == len(legs_frames):
                                                loop = loop + 1
                                                loopcount = 0
                        except:
                            try:
                                tb1 = editor.layout.toolbars["tb_animation"]
                                buttons = tb1.tb.buttons
                                for b in range(len(buttons)):
                                    if buttons[b] is None:
                                        continue
                                    if buttons[b].state == qtoolbar.selected:
                                        buttons[b].state = qtoolbar.normal
                                    if b == 5:
                                        break
                                if MdlOption("AnimationActive"):
                                    quarkx.setupsubset(SS_MODEL, "Options")["AnimationActive"] = None
                                if MdlOption("AnimationCFGActive"):
                                    quarkx.setupsubset(SS_MODEL, "Options")["AnimationCFGActive"] = None
                                if MdlOption("AnimationPaused"):
                                    quarkx.setupsubset(SS_MODEL, "Options")["AnimationPaused"] = None
                                if quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"]:
                                    quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"] = None
                                editor.MouseDragMode = None
                                quarkx.update(editor.form)
                                # This terminates the animation timer stopping the repeditive drawing function.
                                quarkx.settimer(drawanimation, self, 0)
                                quarkx.msgbox("Insufficient Frames !\n\nComponent: " + comp.shortname + "\ndoes not have enough frames for CFG Animation.\n\nEither the model was imported using 'min. tag frames'\n\nor some action caused the above component's frame count\nnot to match other components of this 'group'.\n\nTry undoing the import and re-import with 'max. tag frames'\nor adding frames to this component to match the others.\n\nAction Canceled.", MT_ERROR, MB_OK)
                                Update_Editor_Views(editor)
                                return
                            except:
                                return

                else: # Handles "BOTH_" sequences.
                    for comp in editor.Root.subitems:
                        if comp.type == ":mc" and (comp.name.startswith(group[0]) or (weapon != "None" and comp.name.startswith(weapon))):  # or not comp.name.startswith(group[0]):  # Not a component
                            pass
                        else:
                            continue
                        compname = comp.shortname.split("_")
                        FrameGroup = comp.dictitems['Frames:fg'].subitems
                        try: # In case a component does not have any frames or the same number of frames, it won't break.
                            for frameindex in range(first_frame1, first_frame1 + num_frames1):
                                if playlistPerComp.has_key(comp.name):
                                    playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [FrameGroup[frameindex]]
                                else:
                                    playlistPerComp[comp.name] = [comp, [FrameGroup[frameindex]]]

                            if compname[1] == "l":
                                playlist = playlistPerComp[comp.name][1]
                        except:
                            try:
                                tb1 = editor.layout.toolbars["tb_animation"]
                                buttons = tb1.tb.buttons
                                for b in range(len(buttons)):
                                    if buttons[b] is None:
                                        continue
                                    if buttons[b].state == qtoolbar.selected:
                                        buttons[b].state = qtoolbar.normal
                                    if b == 5:
                                        break
                                if MdlOption("AnimationActive"):
                                    quarkx.setupsubset(SS_MODEL, "Options")["AnimationActive"] = None
                                if MdlOption("AnimationCFGActive"):
                                    quarkx.setupsubset(SS_MODEL, "Options")["AnimationCFGActive"] = None
                                if MdlOption("AnimationPaused"):
                                    quarkx.setupsubset(SS_MODEL, "Options")["AnimationPaused"] = None
                                if quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"]:
                                    quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"] = None
                                editor.MouseDragMode = None
                                quarkx.update(editor.form)
                                # This terminates the animation timer stopping the repeditive drawing function.
                                quarkx.settimer(drawanimation, self, 0)
                                quarkx.msgbox("Insufficient Frames !\n\nComponent: " + comp.shortname + "\ndoes not have enough frames for CFG Animation.\n\nEither the model was imported using 'min. tag frames'\n\nor some action caused the above component's frame count\nnot to match other components of this 'group'.\n\nTry undoing the import and re-import with 'max. tag frames'\nor adding frames to this component to match the others.\n\nAction Canceled.", MT_ERROR, MB_OK)
                                Update_Editor_Views(editor)
                                return
                            except:
                                return
                return

            if item == len(sel)-1:
                try:
                    tb1 = editor.layout.toolbars["tb_animation"]
                    buttons = tb1.tb.buttons
                    for b in range(len(buttons)):
                        if buttons[b] is None:
                            continue
                        if buttons[b].state == qtoolbar.selected:
                            buttons[b].state = qtoolbar.normal
                        if b == 5:
                            break
                    if MdlOption("AnimationActive"):
                        quarkx.setupsubset(SS_MODEL, "Options")["AnimationActive"] = None
                    if MdlOption("AnimationCFGActive"):
                        quarkx.setupsubset(SS_MODEL, "Options")["AnimationCFGActive"] = None
                    if MdlOption("AnimationPaused"):
                        quarkx.setupsubset(SS_MODEL, "Options")["AnimationPaused"] = None
                    if quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"]:
                        quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"] = None
                    editor.MouseDragMode = None
                    quarkx.update(editor.form)
                    # This terminates the animation timer stopping the repeditive drawing function.
                    quarkx.settimer(drawanimation, self, 0)
                    quarkx.msgbox("Improper Action !\n\nYou can only select frames from\nthe same component to animate.\n\nAction Canceled.", MT_ERROR, MB_OK)
                    Update_Editor_Views(editor)
                    return
                except:
                    return

    FrameGroup = playlist[0].parent.subitems
    framenumbers = []
    try:
        for item in playlist:
            listindex = operator.indexOf(FrameGroup, item)
            framenumbers = framenumbers + [listindex]
    except:
        try:
            tb1 = editor.layout.toolbars["tb_animation"]
            buttons = tb1.tb.buttons
            for b in range(len(buttons)):
                if buttons[b] is None:
                    continue
                if buttons[b].state == qtoolbar.selected:
                    buttons[b].state = qtoolbar.normal
                if b == 5:
                    break
            if MdlOption("AnimationActive"):
                quarkx.setupsubset(SS_MODEL, "Options")["AnimationActive"] = None
            if MdlOption("AnimationCFGActive"):
                quarkx.setupsubset(SS_MODEL, "Options")["AnimationCFGActive"] = None
            if MdlOption("AnimationPaused"):
                quarkx.setupsubset(SS_MODEL, "Options")["AnimationPaused"] = None
            if quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"]:
                quarkx.setupsubset(SS_MODEL, "Building")["AnimationMode"] = None
            editor.MouseDragMode = None
            quarkx.update(editor.form)
            # This terminates the animation timer stopping the repeditive drawing function.
            quarkx.settimer(drawanimation, self, 0)
            quarkx.msgbox("Improper Action !\n\nYou can only select frames from\nthe same component to animate.\n\nAction Canceled.", MT_ERROR, MB_OK)
            Update_Editor_Views(editor)
            return
        except:
            return

    for comp in editor.Root.subitems:
        if comp.type != ":mc":
            # Not a component
            continue
        FrameGroup = comp.dictitems['Frames:fg'].subitems
        for frameindex in framenumbers:
            try: # In case a component does not have any frames or the same number of frames, it won't break.
                if playlistPerComp.has_key(comp.name):
                    playlistPerComp[comp.name][1] = playlistPerComp[comp.name][1] + [FrameGroup[frameindex]]
                else:
                    playlistPerComp[comp.name] = [comp, [FrameGroup[frameindex]]]
            except:
                break


##### Below makes the toolbar and arainges its buttons #####

class AnimationBar(ToolBar):
    "The Animation tool bar with AnimationModes buttons."

    Caption = "Animation"
    DefaultPos = ((208, 102, 429, 152), "topdock", 0, 1, 1)

    def animate(self, btn):
        "Activates and deactivates animation."
        global playlist, playNR
        import mdleditor
        editor = mdleditor.mdleditor
        if not MdlOption("AnimationActive"): # Turns button ON
            if not MdlOption("AnimationCFGActive"):
                if editor.layout.explorer.sellist == [] or len(editor.layout.explorer.sellist) < 2:
                    quarkx.msgbox("Improper Action !\n\nYou need to select at least two frames\n(and no other types of sub-items)\nof the same component to activate animation.\n\nAction Canceled.", MT_ERROR, MB_OK)
                    return
                else:
                    sel = editor.layout.explorer.sellist
                    if sel[0].type != ':mf':
                        quarkx.msgbox("Improper Selection !\n\nYou need to select at least two frames\n(and no other types of sub-items)\nof the same component to activate animation.\n\nAction Canceled.", MT_ERROR, MB_OK)
                        return
            quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            if MdlOption("AnimationCFGActive"):
                quarkx.setupsubset(SS_MODEL, "Options")['AnimationCFGActive'] = None
                qtoolbar.toggle(self.tb.buttons[2])
                self.tb.buttons[2].state = qtoolbar.normal
            else:
                if quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] != "1" and quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] != "1":
                    playNR = 0
                playlist = editor.layout.explorer.sellist
            # Commenting out items below speeds up start and stop of animation.
            #    UpdateplaylistPerComp(self)
            #    for view in editor.layout.views:
            #        view.handles = []
            #        mdleditor.setsingleframefillcolor(editor, view)
            #        view.repaint()
                FPS = int(1000/quarkx.setupsubset(SS_MODEL, "Display")["AnimationFPS"][0])
                # This sets (starts) the timer and calls the drawing function for the first time.
                # The drawing function will be recalled each time that the timer goes off.
                quarkx.settimer(drawanimation, self, FPS)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            if not MdlOption("AnimationCFGActive") and quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] != "1" and quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] != "1":
                playNR = 0
                # This terminates the animation timer stopping the repeditive drawing function.
                quarkx.settimer(drawanimation, self, 0)
            if not MdlOption("AnimationCFGActive") and quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] != "1":
                editor.layout.explorer.sellist = playlist
            else:
                playlist = []
                btns = editor.layout.toolbars["tb_animation"].tb.buttons
                self.pauseanimation(btns[8]) # Turns off the AnimationPaused button.
                comps = editor.Root.findallsubitems("", ':mc')  # Get all components.
                for comp in comps:
                    comp.currentframe = comp.dictitems['Frames:fg'].subitems[0]
                editor.Root.currentcomponent.currentframe = editor.Root.currentcomponent.dictitems['Frames:fg'].subitems[0]
                editor.layout.explorer.sellist = [editor.Root.currentcomponent.currentframe]
        try:
            tb2 = editor.layout.toolbars["tb_objmodes"]
            tb3 = editor.layout.toolbars["tb_paintmodes"]
            tb4 = editor.layout.toolbars["tb_edittools"]
            tb5 = editor.layout.toolbars["tb_AxisLock"]
            for b in range(len(tb2.tb.buttons)):
                if b == 1:
                    tb2.tb.buttons[b].state = qtoolbar.selected
                else:
                    tb2.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb3.tb.buttons)):
                tb3.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb4.tb.buttons)):
                if b == 7:
                    tb4.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb5.tb.buttons)):
                if b == 5:
                    tb5.tb.buttons[b].state = qtoolbar.normal
        except:
            pass
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", 0)
        quarkx.setupsubset(SS_MODEL, "Building").setint("PaintMode", 0)
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
        editor.MouseDragMode = mdlhandles.RectSelDragObject
        for view in editor.layout.views:
            if MapOption("CrossCursor", SS_MODEL):
                view.cursor = CR_CROSS
                view.handlecursor = CR_ARROW
            else:
                view.cursor = CR_ARROW
                view.handlecursor = CR_CROSS

    def animateCFG(self, btn):
        "Activates and deactivates animationCFG."
        global playlist, playNR, holdselection
        import mdleditor
        editor = mdleditor.mdleditor
        if not MdlOption("AnimationCFGActive"): # Turns button ON
            if MdlOption("AnimationActive"):
                quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] = None
                qtoolbar.toggle(self.tb.buttons[0])
                self.tb.buttons[0].state = qtoolbar.normal
                quarkx.update(editor.form)
            if editor.layout.explorer.sellist == []:
                quarkx.msgbox("Improper Action !\n\nTo activate CFG animation\nyou need to select one Tag with the\nCFG text which would be a 'torso' tag\nand have imported all sections of that model,\nwhich will cause the 'animation.cfg' file\nof that model to also be loaded.\n\nAction Canceled.", MT_ERROR, MB_OK)
                return
            else:
                sel = editor.layout.explorer.sellist
                tags = editor.Root.dictitems['Misc:mg'].findallsubitems("", ':tag')  # get all tags
                for item in range(len(sel)):
                    if item == len(sel)-1 and sel[item].type != ':tag':
                        quarkx.msgbox("Improper Action !\n\nTo activate CFG animation\nyou need to select one Tag with the\nCFG text which would be a 'torso' tag\nand have imported all sections of that model,\nwhich will cause the 'animation.cfg' file\nof that model to also be loaded.\n\nAction Canceled.", MT_ERROR, MB_OK)
                        return
                    elif sel[item].type == ':tag':
                        group = sel[item].name.split("_")[0]
                        for tag in tags:
                            if tag.name.startswith(group) and tag.dictspec.has_key("play_list1"):
                                break
                    elif item == len(sel)-1:
                        quarkx.msgbox("CFG file not found !\n\nNone of the selected tags has an 'animation.cfg' file\nor the '.cfg' file is named improperly.\nCheck the model folders and correct.\n\nTo activate CFG animation\nyou need to select at least\none Tag and have imported all sections of that model,\nwhich will cause the 'animation.cfg' file\nof that model to also be loaded.\n\nAction Canceled.", MT_ERROR, MB_OK)
                        return
            quarkx.setupsubset(SS_MODEL, "Options")['AnimationCFGActive'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            playNR = 0
            holdselection = playlist = editor.layout.explorer.sellist
            UpdateplaylistPerComp(self)
            for view in editor.layout.views:
                view.handles = []
                mdleditor.setsingleframefillcolor(editor, view)
                view.repaint()
            FPS = int(1000/quarkx.setupsubset(SS_MODEL, "Display")["AnimationFPS"][0])
            # This sets (starts) the timer and calls the drawing function for the first time.
            # The drawing function will be recalled each time that the timer goes off.
            quarkx.settimer(drawanimation, self, FPS)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimationCFGActive'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            playNR = 0
            # This terminates the animation timer stopping the repeditive drawing function.
            quarkx.settimer(drawanimation, self, 0)
            editor.layout.explorer.sellist = holdselection
            comps = editor.Root.findallsubitems("", ':mc')  # Get all components.
            for comp in comps:
                comp.currentframe = comp.dictitems['Frames:fg'].subitems[0]
            editor.Root.currentcomponent.currentframe = editor.Root.currentcomponent.dictitems['Frames:fg'].subitems[0]
        try:
            tb2 = editor.layout.toolbars["tb_objmodes"]
            tb3 = editor.layout.toolbars["tb_paintmodes"]
            tb4 = editor.layout.toolbars["tb_edittools"]
            tb5 = editor.layout.toolbars["tb_AxisLock"]
            for b in range(len(tb2.tb.buttons)):
                if b == 1:
                    tb2.tb.buttons[b].state = qtoolbar.selected
                else:
                    tb2.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb3.tb.buttons)):
                tb3.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb4.tb.buttons)):
                if b == 7:
                    tb4.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb5.tb.buttons)):
                if b == 5:
                    tb5.tb.buttons[b].state = qtoolbar.normal
        except:
            pass
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", 0)
        quarkx.setupsubset(SS_MODEL, "Building").setint("PaintMode", 0)
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
        editor.MouseDragMode = mdlhandles.RectSelDragObject
        for view in editor.layout.views:
            if MapOption("CrossCursor", SS_MODEL):
                view.cursor = CR_CROSS
                view.handlecursor = CR_ARROW
            else:
                view.cursor = CR_ARROW
                view.handlecursor = CR_CROSS

    def incrementFPS(self, btn):
        "Implements the increase and decrease FPS (frames per second) buttons."
        editor = mapeditor()
        setup = quarkx.setupsubset(SS_MODEL, "Display")
        animationFPS = setup["AnimationFPS"]
        if animationFPS[0] + btn.delta < 1 or animationFPS[0] + btn.delta > 64:
            return
        animationFPS = animationFPS[0] + btn.delta
        setup["AnimationFPS"] = (animationFPS,)
        editor.layout.setanimationfps(animationFPS)

    def pauseanimation(self, btn):
        "Play or Pause animation."
        global playlist, playNR
        editor = mapeditor()
        if not MdlOption("AnimationPaused"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
            if quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] is not None:
                import mdlmgr
                mdlmgr.treeviewselchanged = 0
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimationPaused'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)
            if playlist != [] and editor.layout.explorer.sellist != []:
                if len(editor.layout.explorer.sellist) > 1:
                    playlist = editor.layout.explorer.sellist
                    UpdateplaylistPerComp(self)
                    playNR = 0
                else:
                    playlistcount = 0
                    for frame in playlist:
                        if frame.name == editor.layout.explorer.sellist[0].name:
                            playNR = playlistcount
                            break
                        else:
                            playlistcount = playlistcount + 1
        try:
            tb2 = editor.layout.toolbars["tb_objmodes"]
            tb3 = editor.layout.toolbars["tb_AxisLock"]
            tb4 = editor.layout.toolbars["tb_edittools"]
            for b in range(len(tb2.tb.buttons)):
                if b == 1:
                    tb2.tb.buttons[b].state = qtoolbar.selected
                else:
                    tb2.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb3.tb.buttons)):
                if b == 5:
                    tb3.tb.buttons[b].state = qtoolbar.normal
            for b in range(len(tb4.tb.buttons)):
                if b == 7:
                    tb4.tb.buttons[b].state = qtoolbar.normal
        except:
            pass
        quarkx.update(editor.form)
        quarkx.setupsubset(SS_MODEL, "Building").setint("ObjectMode", 0)
        quarkx.setupsubset(SS_MODEL, "Options")["MakeBBox"] = None
        quarkx.setupsubset(SS_MODEL, "Options")["FaceCutTool"] = None
        editor.MouseDragMode = mdlhandles.RectSelDragObject

    def interpolation(self, btn):
        "Activates and deactivates animation interpolation, added movement between two frames by calculation."
        global playNR
        editor = mapeditor()
        if not MdlOption("InterpolationActive"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
            if quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] is not None and quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] != "0" and editor.layout.explorer.uniquesel is not None:
                if not MdlOption("AnimationCFGActive"):
                    UpdateplaylistPerComp(self)
                    frames = editor.Root.currentcomponent.dictitems['Frames:fg'].subitems
                    for framenbr in range(len(frames)):
                        if frames[framenbr].name == editor.layout.explorer.uniquesel.name:
                            playNR = framenbr
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['InterpolationActive'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)
            if quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] is not None and quarkx.setupsubset(SS_MODEL, "Options")['AnimationActive'] != "0" and MdlOption("AnimationPaused"):
                if not MdlOption("AnimationCFGActive"):
                    if editor.layout.explorer.uniquesel is not None:
                        frames = editor.Root.currentcomponent.dictitems['Frames:fg'].subitems
                        for framenbr in range(len(frames)):
                            if frames[framenbr].name == editor.layout.explorer.uniquesel.name:
                                playNR = framenbr
                    import mdlmgr
                    mdlmgr.treeviewselchanged = 0
                    try:
                        playNR = int(round(playNR))
                        editor.layout.explorer.uniquesel = playlist[playNR]
                        editor.layout.explorer.invalidate()
                    except:
                        pass

    def smoothlooping(self, btn):
        "Activates and deactivates animation interpolation smooth looping, added movement between the last and first frames of a cycle by calculation."
        editor = mapeditor()
        if not MdlOption("SmoothLooping"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['SmoothLooping'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['SmoothLooping'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)

    def incrementIPF(self, btn):
        "Implements the increase and decrease IPF (interpolation frames) buttons."
        editor = mapeditor()
        setup = quarkx.setupsubset(SS_MODEL, "Display")
        animationIPF = setup["AnimationIPF"]
        if animationIPF[0] + btn.delta < 2 or animationIPF[0] + btn.delta > 20:
            return
        animationIPF = animationIPF[0] + btn.delta
        setup["AnimationIPF"] = (animationIPF,)
        editor.layout.setanimationipf(animationIPF)

    def animateeditor3dview(self, btn):
        "Editor's 3D view animation."
        editor = mapeditor()
        if not MdlOption("AnimateEd3Dview"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateEd3Dview'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateEd3Dview'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)

    def animatex2dview(self, btn):
        "Editor's X Back 2D view animation."
        editor = mapeditor()
        if not MdlOption("AnimateX2Dview"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateX2Dview'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateX2Dview'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)

    def animatey2dview(self, btn):
        "Editor's Y Side 2D view animation."
        editor = mapeditor()
        if not MdlOption("AnimateY2Dview"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateY2Dview'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateY2Dview'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)

    def animatez2dview(self, btn):
        "Editor's Z Top 2D view animation."
        editor = mapeditor()
        if not MdlOption("AnimateZ2Dview"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateZ2Dview'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateZ2Dview'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)

    def animatefloat3dview(self, btn):
        "Editor's Floating 3D view animation."
        editor = mapeditor()
        if not MdlOption("AnimateFloat3Dview"): # Turns button ON
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateFloat3Dview'] = "1"
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.selected
            quarkx.update(editor.form)
        else: # Turns button OFF
            quarkx.setupsubset(SS_MODEL, "Options")['AnimateFloat3Dview'] = None
            qtoolbar.toggle(btn)
            btn.state = qtoolbar.normal
            quarkx.update(editor.form)

    def buildbuttons(self, layout):
              # to build the single click button
        if not ico_dict.has_key('ico_mdlanim'):
            ico_dict['ico_mdlanim']=LoadIconSet1("mdlanim", 1.0)
        ico_mdlanim=ico_dict['ico_mdlanim']
              # to build the Mode buttons
        btns = []
        for i in range(len(AnimationModes)):
            obj, icon = AnimationModes[i]
            btn = qtoolbar.button(selectmode, obj.Hint, ico_mdlanim, icon)
            btn.i = i
            btns.append(btn)
        i = quarkx.setupsubset(SS_MODEL, "Building").getint("AnimationMode")
        select1(btns[i], self, layout.editor)

        animateonoff = qtoolbar.button(self.animate, "Animate on\off||Animate on\off:\n\nThis button will activate or de-activate the animation of the selected model component animation frames.\n\nYou must select two or more frames of the same component and no other sub-items for the animation to become available.\n\nTo return to regular operation mode you must click this button to turn 'Off' the animation function.\n\nPress 'F1' for InfoBase help\nof this function for details.", ico_mdlanim, 0, infobaselink="intro.modeleditor.toolpalettes.animation.html#animate")
        animateCFGonoff = qtoolbar.button(self.animateCFG, "AnimateCFG on\off||AnimateCFG on\off:\n\nThis button will activate or de-activate the animationCFG of the selected model component animation frames.\n\nOnly use for .md3 'Player' type models with tags and a 'animation.cfg' file in its folder.\n\nYou must select one Tag with the CFG text which would be a 'torso' tag and have imported all sections of that model for the animation to become available.\n\nTo return to regular operation mode you must click this button to turn 'Off' the animation cfg function.\n\nPress 'F1' for InfoBase help\nof this function for details.", ico_mdlanim, 12, infobaselink="intro.modeleditor.toolpalettes.animation.html#animatecfg")

        fpsbtn = qtoolbar.doublebutton(layout.toggleanimationfps, layout.getFPSmenu, "FPS||FPS or frames per second is the setting as to how fast or slow the selected model component animation frames will be drawn in the selected view(s) of the editor.\n\nYou can select a menu fps speed or use the arrows to the right to increase or decrease that speed while the frames are being animated.", ico_mdlanim, 1, infobaselink="intro.modeleditor.toolpalettes.animation.html#fps")
        setup = quarkx.setupsubset(SS_MODEL, "Display")
        animationFPS = setup["AnimationFPS"]
        fpsbtn.caption = quarkx.ftos(animationFPS[0])  # To determine the button width and show the current setting.
        increasefps = qtoolbar.button(self.incrementFPS, "Increase FPS", ico_mdlanim, 2)
        increasefps.delta = 1
        decreasefps = qtoolbar.button(self.incrementFPS, "Decrease FPS", ico_mdlanim, 3)
        decreasefps.delta = -1

        animatepaused = qtoolbar.button(self.pauseanimation, "Play\Pause||Play\Pause:\n\nTo temporarily pause the chosen animation sequence on the particular frame that was drawn when this button was clicked. Click this button again to continue on with the animation from that frame.\n\nIf another frame of the chosen sequence is selected during the pause, it will continue from that point.\n\nThe entire frame sequence selection can also be changed during a pause.\n\nIf a component has more then one skin, the skin can be changed during the pause.", ico_mdlanim, 4, infobaselink="intro.modeleditor.toolpalettes.animation.html#pause")
        interpolonoff = qtoolbar.button(self.interpolation, "Interpolation on\off||Interpolation on\off:\n\nThis button will activate or de-activate the interpolation (give smooth animation) of the selected model component animation frames.\n\nInterpolation calculates additional movement positions between two frames and draws them to smooth out the movement between those two frames.\n\nTo return to regular animation mode you must click this button to turn 'Off' the interpolation function.", ico_mdlanim, 10, infobaselink="intro.modeleditor.toolpalettes.animation.html#interpolation")
        smoothlooponoff = qtoolbar.button(self.smoothlooping, "Smooth Looping on\off||Smooth Looping on\off:\n\nThis button will activate or de-activate smooth looping, giving a smoother animation appearance of the selected model component animation frames when returning from the last to the first frame.\n\nTo return to regular looping mode you must click this button again to turn 'Off' this function.", ico_mdlanim, 11, infobaselink="intro.modeleditor.toolpalettes.animation.html#smooth")

        ipfbtn = qtoolbar.doublebutton(layout.toggleanimationipf, layout.getIPFmenu, "IPF||IPF or interpolation frames is the setting as to how many added computed position frames will be added to the selected model component animation to be drawn in the selected view(s) of the editor.\n\nYou can select a menu fps speed or use the arrows to the right to increase or decrease that number while the frames are being animated.", ico_mdlanim, 1, infobaselink="intro.modeleditor.toolpalettes.animation.html#ipf")
        animationIPF = setup["AnimationIPF"]
        ipfbtn.caption = quarkx.ftos(animationIPF[0])  # To determine the button width and show the current setting.
        increaseipf = qtoolbar.button(self.incrementIPF, "Increase IPF", ico_mdlanim, 2)
        increaseipf.delta = 1
        decreaseipf = qtoolbar.button(self.incrementIPF, "Decrease IPF", ico_mdlanim, 3)
        decreaseipf.delta = -1

        editor3dviewanimated = qtoolbar.button(self.animateeditor3dview, "Animate Editors 3D view||Animate Editors 3D view:\n\nActivate this button to animate in the Editor's 3D view.", ico_mdlanim, 5, infobaselink="intro.modeleditor.toolpalettes.animation.html#viewselector")
        x2dviewanimated = qtoolbar.button(self.animatex2dview, "Animate X Back 2D view||Animate X Back 2D view:\n\nActivate this button to animate in the Editor's X Back 2D view.", ico_mdlanim, 6, infobaselink="intro.modeleditor.toolpalettes.animation.html#viewselector")
        y2dviewanimated = qtoolbar.button(self.animatey2dview, "Animate Y Side 2D view||Animate Y Side 2D view:\n\nActivate this button to animate in the Editor's Y Side 2D view.", ico_mdlanim, 7, infobaselink="intro.modeleditor.toolpalettes.animation.html#viewselector")
        z2dviewanimated = qtoolbar.button(self.animatez2dview, "Animate Z Top 2D view||Animate Z Top 2D view:\n\nActivate this button to animate in the Editor's Z Top 2D view.", ico_mdlanim, 8, infobaselink="intro.modeleditor.toolpalettes.animation.html#viewselector")
        float3dviewanimated = qtoolbar.button(self.animatefloat3dview, "Animate Floating 3D view||Animate Floating 3D view:\n\nActivate this button to animate in the Editor's Floating 3D view.", ico_mdlanim, 9, infobaselink="intro.modeleditor.toolpalettes.animation.html#viewselector")

        if not MdlOption("AnimationActive"):
            animateonoff.state = qtoolbar.normal
        else:
            animateCFGonoff.state = qtoolbar.normal
            animateonoff.state = qtoolbar.selected

        if not MdlOption("AnimationCFGActive"):
            animateonoff.state = qtoolbar.normal
        else:
            animateonoff.state = qtoolbar.normal
            animateCFGonoff.state = qtoolbar.selected

        if not MdlOption("AnimationPaused"):
            animatepaused.state = qtoolbar.normal
        else:
            animatepaused.state = qtoolbar.selected

        if not MdlOption("InterpolationActive"):
            interpolonoff.state = qtoolbar.normal
        else:
            interpolonoff.state = qtoolbar.selected

        if not MdlOption("SmoothLooping"):
            smoothlooponoff.state = qtoolbar.normal
        else:
            smoothlooponoff.state = qtoolbar.selected

        if not MdlOption("AnimateEd3Dview"):
            editor3dviewanimated.state = qtoolbar.normal
        else:
            editor3dviewanimated.state = qtoolbar.selected

        if not MdlOption("AnimateX2Dview"):
            x2dviewanimated.state = qtoolbar.normal
        else:
            x2dviewanimated.state = qtoolbar.selected

        if not MdlOption("AnimateY2Dview"):
            y2dviewanimated.state = qtoolbar.normal
        else:
            y2dviewanimated.state = qtoolbar.selected

        if not MdlOption("AnimateZ2Dview"):
            z2dviewanimated.state = qtoolbar.normal
        else:
            z2dviewanimated.state = qtoolbar.selected

        if not MdlOption("AnimateFloat3Dview"):
            float3dviewanimated.state = qtoolbar.normal
        else:
            float3dviewanimated.state = qtoolbar.selected

        layout.buttons.update({"animate": animateonoff,
                               "animateCFG": animateCFGonoff,
                               "fps": fpsbtn,
                               "fpsup": increasefps,
                               "fpsdown": decreasefps,
                               "pause": animatepaused,
                               "interpolation": interpolonoff,
                               "smoothloop": smoothlooponoff,
                               "ipf": ipfbtn,
                               "ipfup": increaseipf,
                               "ipfdown": decreaseipf,
                               "animed3dview": editor3dviewanimated,
                               "animex2dview": x2dviewanimated,
                               "animey2dview": y2dviewanimated,
                               "animez2dview": z2dviewanimated,
                               "floatd3dview": float3dviewanimated
                             })

        return [animateonoff, qtoolbar.sep, animateCFGonoff, qtoolbar.sep,
                fpsbtn, increasefps, decreasefps, qtoolbar.sep,
                animatepaused, qtoolbar.sep, interpolonoff, smoothlooponoff, qtoolbar.sep,
                ipfbtn, increaseipf, decreaseipf, qtoolbar.sep,
                editor3dviewanimated, x2dviewanimated, y2dviewanimated, z2dviewanimated, float3dviewanimated]


# ----------- REVISION HISTORY ------------
#
#
#$Log: mdlanimation.py,v $
#Revision 1.27  2011/11/17 01:19:02  cdunde
#Setup BBox drag toolbar button to work correctly with other toolbar buttons.
#
#Revision 1.26  2011/03/04 06:50:28  cdunde
#Added new face cutting tool, for selected faces, like in the map editor with option to allow vertex separation.
#
#Revision 1.25  2011/02/12 08:36:37  cdunde
#Fixed auto turn off of Objects Maker not working with other toolbars.
#
#Revision 1.24  2010/05/25 21:43:32  cdunde
#To speed up start and stop of animations.
#
#Revision 1.23  2010/05/01 04:39:48  cdunde
#Fix to draw bones, if any, correctly after stopping animation with pause still on.
#
#Revision 1.22  2010/04/28 06:49:10  cdunde
#Fix to reselect first frame if animation is stopped with pause still active for proper bone positioning.
#
#Revision 1.21  2009/10/21 21:12:42  cdunde
#Removed unused code.
#
#Revision 1.20  2009/10/17 09:17:31  cdunde
#Added selection and playing of .md3 weapons with player models CFG Animation.
#
#Revision 1.19  2009/10/16 06:40:40  cdunde
#To catch sudden animation stop so original 1st frame does not get messed up, which was happening.
#
#Revision 1.18  2009/10/16 00:59:17  cdunde
#Add animation rotation of weapon, for .md3 imports, when attached to model.
#
#Revision 1.17  2009/10/14 08:12:31  cdunde
#Added complete section in the InfoBase Docs for the Model Editor about tags with F1 links.
#
#Revision 1.16  2009/10/14 00:20:47  cdunde
#Various fixes for CFG Animation and interpolation.
#
#Revision 1.15  2009/10/12 20:49:56  cdunde
#Added support for .md3 animationCFG (configuration) support and editing.
#
#Revision 1.14  2009/10/05 01:14:58  cdunde
#Removed constant component looping for max interpolation drawing speed
#and setup for possibly to only animate selected components and frames.
#
#Revision 1.13  2009/10/04 22:17:18  cdunde
#Setup correct switching from standard to interpolation animation methods.
#
#Revision 1.12  2009/10/03 06:16:07  cdunde
#Added support for animation interpolation in the Model Editor.
#(computation of added movement to emulate game action)
#
#Revision 1.11  2008/07/15 23:16:27  cdunde
#To correct typo error from MldOption to MdlOption in all files.
#
#Revision 1.10  2008/05/01 19:15:24  danielpharos
#Fix treeviewselchanged not updating.
#
#Revision 1.9  2008/05/01 13:52:32  danielpharos
#Removed a whole bunch of redundant imports and other small fixes.
#
#Revision 1.8  2008/02/23 04:41:11  cdunde
#Setup new Paint modes toolbar and complete painting functions to allow
#the painting of skin textures in any Model Editor textured and Skin-view.
#
#Revision 1.7  2008/02/04 05:07:41  cdunde
#Made toolbars interactive with one another to
#turn off buttons when needed, avoiding errors and crashes.
#
#Revision 1.6  2007/10/31 09:24:24  cdunde
#To stop errors and crash if editor or QuArK is closed while animation is running.
#
#Revision 1.5  2007/10/31 03:47:52  cdunde
#Infobase button link updates.
#
#Revision 1.4  2007/10/22 15:43:40  cdunde
#To remove unused code and clean up file.
#
#Revision 1.3  2007/10/22 02:21:46  cdunde
#Needed to change the Animation timer to be non-dependent on any view
#to allow proper redrawing of all views when the Animation is stopped
#and set fillcolor and repaint all views to properly clear handles drawn.
#
#Revision 1.2  2007/10/18 16:11:31  cdunde
#To implement selective view buttons for Model Editor Animation.
#
#Revision 1.1  2007/10/18 02:31:55  cdunde
#Setup the Model Editor Animation system, functions and toolbar.
#
#
#
#
