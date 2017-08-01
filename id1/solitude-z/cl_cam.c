/*
Copyright (C) 1996-1997 Id Software, Inc.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

*/
// cl_cam.c - client-side spectator functions

#include "quakedef.h"
#include "pmove.h"
#include "cl_sbar.h"
#include "teamplay.h"


qbool		cam_track;
int			cam_target;
qbool		cam_locked;
int			cam_curtarget;		// playernum or CAM_NOTARGET

static int	cam_oldbuttons;

cvar_t cl_hightrack = {"cl_hightrack", "0" };	// track high fragger

int Cam_PlayerNum (void)
{
	if (cl.spectator && cam_curtarget != CAM_NOTARGET)
		return cam_curtarget;
	else
		return cl.playernum;
}

// returns true if weapon model should be drawn in camera mode
qbool Cam_DrawViewModel (void)
{
	if (!cl.spectator)
		return true;

	if (cam_curtarget != CAM_NOTARGET)
		return true;

	return false;
}

// returns true if we should draw this player, we don't if we are chase-camming
qbool Cam_DrawPlayer (int playernum)
{
	if (cl.spectator && cam_curtarget == playernum)
		return false;
	return true;
}

#ifdef MVDPLAY
void Cam_Lock (int playernum)
{
	cam_track = true;
	cam_target = playernum;
	// not sure about the following two
	cam_locked = true;
	cam_curtarget = playernum;

	memcpy(cl.stats, cl.players[playernum].stats, sizeof(cl.stats));

	Sbar_Changed ();
    CL_UpdateSkins ();
}
#endif

int Cam_TargetCount (void)
{
	int	i, count = 0;
	for (i = 0; i < MAX_CLIENTS; i++) {
		if (i == cl.playernum || !cl.players[i].name[0] || cl.players[i].spectator)
			continue;
		count++;
	}
	// could cache the count and only update at players' connect/disconnect
	return count;
}


static void Cam_SendUnlockCommand (void)
{
	MSG_WriteByte (&cls.netchan.message, clc_stringcmd);
	MSG_WriteString (&cls.netchan.message, "ptrack");
}

static void Cam_SendPTrackCommand (int playernum)
{
	char st[40];

	sprintf(st, "ptrack %i", playernum);
	MSG_WriteByte (&cls.netchan.message, clc_stringcmd);
	MSG_WriteString (&cls.netchan.message, st);
}

static void Cam_FindTarget (void)
{
	int	i, num;

	// use the last tracked player if possible
	for (i = 0; i < MAX_CLIENTS; i++) {
		num = (cam_target + i) % MAX_CLIENTS;
		if (num == cl.playernum || !cl.players[num].name[0] || cl.players[num].spectator)
			continue;
		// found someone
		goto ok;
	}
	return;

ok:
	cam_track = true;
	cam_target = num;
	cam_locked = false;		// not yet

#ifdef MVDPLAY
	if (cls.mvdplayback) {
		cam_curtarget = cam_target;
		cam_locked = true;
		memcpy(cl.stats, cl.players[num].stats, sizeof(cl.stats));
	}
#endif

	Sbar_Changed ();
    CL_UpdateSkins ();
	Cam_SendPTrackCommand (num);
}

static void Cam_FindNextTarget (void)
{
	int	i, num;

	// find next target
	// start with cam_nexttarget so that we can switch targets quickly even if waiting
	for (i = 0; i < MAX_CLIENTS; i++) {
		num = (cam_target + 1 + i) % MAX_CLIENTS;
		if (num == cl.playernum || !cl.players[num].name[0] || cl.players[num].spectator)
			continue;
		// found someone
		goto ok;
	}
	// there is only one player
	return;

ok:
	cam_target = num;
	cam_locked = false;		// not yet

#ifdef MVDPLAY
	if (cls.mvdplayback) {
		cam_curtarget = cam_target;
		cam_locked = true;
		memcpy(cl.stats, cl.players[num].stats, sizeof(cl.stats));
	}
#endif

    Sbar_Changed ();
    CL_UpdateSkins ();
	Cam_SendPTrackCommand (num);
}


void Cam_FinishMove (usercmd_t *cmd)
{
	int		buttons_pressed;

	if (!cl.spectator || cls.state != ca_active || cl.intermission)
		return;

	buttons_pressed = cmd->buttons & ~cam_oldbuttons;
	cam_oldbuttons = cmd->buttons;

	// user intentions
	if (buttons_pressed & BUTTON_ATTACK) {
		if (cam_track) {
			// leave tracking mode
			cam_track = false;
			cam_locked = false;
			cam_curtarget = CAM_NOTARGET;
			Sbar_Changed ();
            CL_UpdateSkins ();
			Cam_SendUnlockCommand ();
		}
		else {
			Cam_FindTarget ();
		}
	}
	else if (cam_track && (buttons_pressed & BUTTON_JUMP))
	{
		Cam_FindNextTarget ();
	}

	if (cam_track && !cam_locked) {
		// try to lock to desired target
		if (cl.frames[cl.validsequence & UPDATE_MASK].playerstate[cam_target].messagenum
				== cl.parsecount) {
			// good
			cam_locked = true;
			cam_curtarget = cam_target;
		}
	}

	if (cam_curtarget != CAM_NOTARGET) {
		player_state_t	*state;
		state = &cl.frames[cl.validsequence & UPDATE_MASK].playerstate[cam_curtarget];
		if (state->messagenum == cl.parsecount) {
			VectorCopy (state->viewangles, cl.simangles);
			VectorCopy (state->viewangles, cl.viewangles);
			VectorCopy (state->origin, cl.simorg);

			// move there so that we get correct PVS
			MSG_WriteByte (&cls.netchan.message, clc_tmove);
			MSG_WriteCoord (&cls.netchan.message, cl.simorg[0]);
			MSG_WriteCoord (&cls.netchan.message, cl.simorg[1]);
			MSG_WriteCoord (&cls.netchan.message, cl.simorg[2]);
		}
		else {
			// lost target (player disconnected?)
			cam_curtarget = CAM_NOTARGET;
			if (cam_locked) {
				// try next guy
				cam_locked = false;		// in case we don't find anyone
				Cam_FindNextTarget ();
			}
			else {
				// never mind, we're going to lock to a new player soon anyway
			}
		}
	}

	if (cam_track /* or check cam_curtarget? */) {
		cmd->forwardmove = cmd->sidemove = cmd->upmove = 0;
		cmd->buttons = 0;	// not sure about this
		//VectorCopy (cl.viewangles, cmd->angles);	// don't really need this
		// might be a better idea to clear cmd->angles to save bandwidth?
	}
}

void Cam_Reset (void)
{
	cam_track = 0;
	cam_locked = false;
	cam_target = 0;
	cam_curtarget = CAM_NOTARGET;
	cam_oldbuttons = 0;
}


/*
===============
Cam_TryLock

Fixes spectator chasecam demos
===============
*/
void Cam_TryLock (void)
{
	int		i, j;
	player_state_t *state;
	int		old_locked, old_target;
	static	float lastlocktime;

	if (!cl.validsequence)
		return;

	// this is to make sure lastlocktime is initialized (FIXME)
	if (!cam_track)
		lastlocktime = 0;

	old_locked = cam_locked;
	old_target = cam_target;

	state = cl.frames[cl.validsequence & UPDATE_MASK].playerstate;
	for (i=0 ; i<MAX_CLIENTS ; i++) {
		if (!cl.players[i].name[0] || cl.players[i].spectator ||
			state[i].messagenum != cl.parsecount)
			continue;
		if (fabs(state[i].command.angles[0] - cl.viewangles[0]) < 2 &&
			fabs(state[i].command.angles[1] - cl.viewangles[1]) < 2)
		{
			for (j=0 ; j<3 ; j++)
				if (fabs(state[i].origin[j] - state[cl.playernum].origin[j]) > 200)
					break;	// too far
			if (j < 3)
				continue;
			cam_track = true;
			cam_locked = true;
			cam_target = cam_curtarget = i;
			lastlocktime = cls.realtime;
			break;
		}
	}

	if (cls.realtime - lastlocktime > 0.3) {
		// Couldn't lock to any player for 0.3 seconds, so assume
		// the spectator switched to free spectator mode
		cam_track = false;
		cam_locked = false;
		cam_curtarget = CAM_NOTARGET;
	}

	if (cam_target != old_target || cam_locked != old_locked) {
		Sbar_Changed ();
        CL_UpdateSkins ();
    }
}

void CL_InitCam(void)
{
	Cvar_Register (&cl_hightrack);
}
