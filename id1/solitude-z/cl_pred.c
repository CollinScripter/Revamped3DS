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
#include "quakedef.h"
#include "pmove.h"

cvar_t	cl_nopred = {"cl_nopred", "1"};
cvar_t	cl_nolerp = {"cl_nolerp", "0"};

/*
==============
CL_PredictUsercmd
==============
*/
void CL_PredictUsercmd (player_state_t *from, player_state_t *to, usercmd_t *u)
{
	// split up very long moves
	if (u->msec > 50)
	{
		player_state_t	temp;
		usercmd_t	split;

		split = *u;
		split.msec /= 2;

		CL_PredictUsercmd (from, &temp, &split);
		CL_PredictUsercmd (&temp, to, &split);
		return;
	}

	VectorCopy (from->origin, cl.pmove.origin);
//	VectorCopy (from->viewangles, pmove.angles);
	VectorCopy (u->angles, cl.pmove.angles);
	VectorCopy (from->velocity, cl.pmove.velocity);

	if (cl.z_ext & Z_EXT_PM_TYPE)
		cl.pmove.jump_msec = 0;
	else
		cl.pmove.jump_msec = from->jump_msec;
	cl.pmove.jump_held = from->jump_held;
	cl.pmove.waterjumptime = from->waterjumptime;
	cl.pmove.pm_type = from->pm_type;
	cl.pmove.onground = from->onground;
	cl.pmove.cmd = *u;

	PM_PlayerMove (&cl.pmove, &cl.movevars);

	to->waterjumptime = cl.pmove.waterjumptime;
	to->pm_type = cl.pmove.pm_type;
	to->jump_held = cl.pmove.jump_held;
	to->jump_msec = cl.pmove.jump_msec;
	cl.pmove.jump_msec = 0;

	VectorCopy (cl.pmove.origin, to->origin);
	VectorCopy (cl.pmove.angles, to->viewangles);
	VectorCopy (cl.pmove.velocity, to->velocity);
	to->onground = cl.pmove.onground;

	to->weaponframe = from->weaponframe;
}


/*
==================
CL_CategorizePosition

Used when cl_nopred is 1 to determine whether we are on ground,
otherwise stepup smoothing code produces ugly jump physics
==================
*/
void CL_CategorizePosition (void)
{
	if (cl.spectator && cam_curtarget == CAM_NOTARGET) {
		cl.onground = false;	// in air
		cl.waterlevel = 0;
		return;
	}
	VectorClear (cl.pmove.velocity);
	VectorCopy (cl.simorg, cl.pmove.origin);
	cl.pmove.numtouch = 0;
	PM_CategorizePosition (&cl.pmove);
	cl.onground = cl.pmove.onground;
	cl.waterlevel = cl.pmove.waterlevel;
}


/*
==============
CL_CalcCrouch

Smooth out stair step ups.
Called before CL_EmitEntities so that the player's lightning model
origin is updated properly
==============
*/
void CL_CalcCrouch (void)
{
	static vec3_t	oldorigin;
	static float	oldz;
	static float	extracrouch;
	static float	crouchspeed = 100;
	int	i;

	for (i=0 ; i<3 ; i++)
		if (fabs(cl.simorg[i] - oldorigin[i]) > 40)
			break;

	VectorCopy (cl.simorg, oldorigin);

	if (i < 3) {
		// possibly teleported or respawned
		oldz = cl.simorg[2];
		extracrouch = 0;
		crouchspeed = 100;
		cl.crouch = 0;
		return;
	}

	if (cl.onground && cl.simorg[2] - oldz > 0)
	{
		if (cl.simorg[2] - oldz > 20) {
			// if on steep stairs, increase speed
			if (crouchspeed < 160) {
				extracrouch = cl.simorg[2] - oldz - cls.frametime*200 - 15;
				if (extracrouch > 5)
					extracrouch = 5;
			}
			crouchspeed = 160;
		}
		
		oldz += cls.frametime * crouchspeed;
		if (oldz > cl.simorg[2])
			oldz = cl.simorg[2];
		
		if (cl.simorg[2] - oldz > 15 + extracrouch)
			oldz = cl.simorg[2] - 15 - extracrouch;
		extracrouch -= cls.frametime*200;
		if (extracrouch < 0)
			extracrouch = 0;
		
		cl.crouch = oldz - cl.simorg[2];
	} else {
		// in air or moving down
		oldz = cl.simorg[2];
		cl.crouch += cls.frametime * 150;
		if (cl.crouch > 0)
			cl.crouch = 0;
		crouchspeed = 100;
		extracrouch = 0;
	}
}

// for .qwd demo playback
static void CL_LerpMove (float msgtime)
{
	static int		lastsequence = 0;
	static vec3_t	lerp_angles[3];
	static vec3_t	lerp_origin[3];
	static float	lerp_times[3];
	static qbool	nolerp[2];
	static float	demo_latency = 0.01;
	float	frac;
	float	simtime;
	int		i;
	int		from, to;

	if (cl_nolerp.value)
		return;

	if (cls.netchan.outgoing_sequence < lastsequence) {
		// reset
		lastsequence = -1;
		lerp_times[0] = -1;
		demo_latency = 0.01;
	}

	if (cls.netchan.outgoing_sequence > lastsequence) {
		lastsequence = cls.netchan.outgoing_sequence;
		// move along
		lerp_times[2] = lerp_times[1];
		lerp_times[1] = lerp_times[0];
		lerp_times[0] = msgtime;

		VectorCopy (lerp_origin[1], lerp_origin[2]);
		VectorCopy (lerp_origin[0], lerp_origin[1]);
		VectorCopy (cl.simorg, lerp_origin[0]);

		VectorCopy (lerp_angles[1], lerp_angles[2]);
		VectorCopy (lerp_angles[0], lerp_angles[1]);
		VectorCopy (cl.simangles, lerp_angles[0]);

		nolerp[1] = nolerp[0];
		nolerp[0] = false;
		for (i = 0; i < 3; i++)
			if (fabs(lerp_origin[0][i] - lerp_origin[1][i]) > 40)
				break;
		if (i < 3)
			nolerp[0] = true;	// a teleport or something
	}

	simtime = cls.realtime - demo_latency;

	// adjust latency
	if (simtime > lerp_times[0]) {
		// Com_DPrintf ("HIGH clamp\n");
		demo_latency = cls.realtime - lerp_times[0];
	}
	else if (simtime < lerp_times[2]) {
		// Com_DPrintf ("   low clamp\n");
		demo_latency = cls.realtime - lerp_times[2];
	} else {
		// drift towards ideal latency
		float ideal_latency = (lerp_times[0] - lerp_times[2]) * 0.6;
		if (demo_latency > ideal_latency)
			demo_latency = max(demo_latency - cls.frametime * 0.1, ideal_latency);
	}

	// decide where to lerp from
	if (simtime > lerp_times[1]) {
		from = 1;
		to = 0;
	} else {
		from = 2;
		to = 1;
	}

	if (nolerp[to])
		return;

	frac = (simtime - lerp_times[from]) / (lerp_times[to] - lerp_times[from]);
	frac = bound (0, frac, 1);

	LerpVector (lerp_origin[from], lerp_origin[to], frac, cl.simorg);
	LerpAngles (lerp_angles[from], lerp_angles[to], frac, cl.simangles);
}


static void CL_LerpMovePhys (double msgtime, float f)
{	
	static int		lastsequence = 0;
	static vec3_t	lerp_origin[3];
	static double	lerp_times[3];
	static qbool	nolerp[2];
	static double	demo_latency = 0.01;
	float	frac;
	float	simtime;
	int		i;
	int		from, to;
	extern cvar_t cl_nolerp;

	if (cl_nolerp.value) 
	{
		lastsequence = ((unsigned)-1) >> 1;	//reset
		return;
	}

	if (cls.netchan.outgoing_sequence < lastsequence) 
	{
		// reset
		lastsequence = -1;
		lerp_times[0] = -1;
		demo_latency = 0.01;
	}

	if (cls.physframe) 
	{
		lastsequence = cls.netchan.outgoing_sequence;

		// move along
		lerp_times[2] = lerp_times[1];
		lerp_times[1] = lerp_times[0];
		lerp_times[0] = msgtime;

		VectorCopy (lerp_origin[1], lerp_origin[2]);
		VectorCopy (lerp_origin[0], lerp_origin[1]);
		VectorCopy (cl.simorg, lerp_origin[0]);

		nolerp[1] = nolerp[0];
		nolerp[0] = false;

		for (i = 0; i < 3; i++)
		{
			if (fabs(lerp_origin[0][i] - lerp_origin[1][i]) > 100)
			{
				break;
			}
		}

		if (i < 3)
		{
			// a teleport or something
			nolerp[0] = true;	
		}
	}

	simtime = cls.realtime - demo_latency;

	// Adjust latency
	if (simtime > lerp_times[0]) {
		// High clamp
		demo_latency = cls.realtime - lerp_times[0];
	}
	else if (simtime < lerp_times[2]) {
		// Low clamp
		demo_latency = cls.realtime - lerp_times[2];
	} 
	else
	{
		// Drift towards ideal latency.
		float ideal_latency = 0;

		if (cls.physframe) {
			if (demo_latency > ideal_latency)
				demo_latency = max(demo_latency - cls.frametime * 0.1, ideal_latency);
			
			if (demo_latency < ideal_latency)
				demo_latency = min(demo_latency + cls.frametime * 0.1, ideal_latency);
		}
	}

	// decide where to lerp from
	if (simtime > lerp_times[1]) 
	{
		from = 1;
		to = 0;
	} 
	else 
	{
		from = 2;
		to = 1;
	}

	if (nolerp[to])
	{
		return;
	}

    	frac = (simtime - lerp_times[from]) / (lerp_times[to] - lerp_times[from]);
    	frac = bound (0, frac, 1);

	for (i = 0; i < 3; i++)
	{
		cl.simorg[i] = lerp_origin[from][i] + (lerp_origin[to][i] - lerp_origin[from][i]) * frac;
	}
}

/*
==============
CL_PredictLocalPlayer
==============
*/
static void CL_PredictLocalPlayer (void)
{
	qbool		nopred;
	int			i;
	frame_t		*from = NULL, *to;
	int			oldphysent;
	extern cvar_t cl_smartjump;
	float		landspeed = 0;

	if (cls.nqprotocol) {
		if (!cls.demoplayback)
			VectorCopy (cl.viewangles, cl.simangles);
		goto out;
	}

	if (!cl.validsequence || cls.netchan.outgoing_sequence - cl.validsequence >= UPDATE_BACKUP-1)
		return;

	if (cam_track && !cls.demoplayback /* FIXME */)
		return;


	// this is the last valid frame received from the server
	to = &cl.frames[cl.validsequence & UPDATE_MASK];

	// setup cl.simangles + decide whether to predict local player
	if (cls.demoplayback && cl.spectator && cam_curtarget != CAM_NOTARGET) {
		VectorCopy (to->playerstate[Cam_PlayerNum()].viewangles, cl.simangles);
		nopred = true;		// FIXME
	} else {
		VectorCopy (cl.viewangles, cl.simangles);
		nopred = (cl_nopred.value || cls.netchan.outgoing_sequence - cl.validsequence <= 1);
	}

	if (nopred)
	{
		VectorCopy (to->playerstate[Cam_PlayerNum()].velocity, cl.simvel);
		VectorCopy (to->playerstate[Cam_PlayerNum()].origin, cl.simorg);
		if (cl.z_ext & Z_EXT_PF_ONGROUND) {
			if (cl_smartjump.value)
				CL_CategorizePosition ();
			cl.onground = to->playerstate[Cam_PlayerNum()].onground;
			landspeed = cl.pmove.landspeed;
		}
		else
			CL_CategorizePosition ();
		goto out;
	}


	oldphysent = cl.pmove.numphysent;
	CL_SetSolidPlayers (cl.playernum);

	// run frames
	for (i=1 ; i < cls.netchan.outgoing_sequence - cl.validsequence; i++)
	{
		from = to;
		to = &cl.frames[(cl.validsequence+i) & UPDATE_MASK];
		CL_PredictUsercmd (&from->playerstate[cl.playernum]
			, &to->playerstate[cl.playernum], &to->cmd);
		cl.onground = cl.pmove.onground;
		cl.waterlevel = cl.pmove.waterlevel;
	}

	cl.pmove.numphysent = oldphysent;

	// copy results out for rendering
	VectorCopy (to->playerstate[cl.playernum].velocity, cl.simvel);
	VectorCopy (to->playerstate[cl.playernum].origin, cl.simorg);

	if (cls.demoplayback)
		CL_LerpMove (to->senttime);
	else if (cl_independentPhysics.value)
		CL_LerpMovePhys (cls.realtime, to->senttime);

out:
	CL_CalcCrouch ();

	if (cl.pmove.landspeed < -650 && !cl.landtime)
		cl.landtime = cl.time;
}


/*
==============
CL_PredictMovement

Predict the local player and other players
==============
*/
void CL_PredictMovement (void)
{
	if (cls.state != ca_active)
		return;

	if (cl.intermission) {
		cl.crouch = 0;

		if ((cl.intermission == 2 || cl.intermission == 3) && !cls.nqprotocol)
			// svc_finale and svc_cutscene don't send origin or angles;
			// we expect progs to move the player to the intermission spot
			// and set their angles correctly.  This is unlike qwcl, but
			// QW never used svc_finale so this should't break anything
			VectorCopy (cl.frames[cl.validsequence & UPDATE_MASK]
				.playerstate[Cam_PlayerNum()].origin, cl.simorg);

		return;
	}

#ifdef MVDPLAY
	if (cls.mvdplayback && !cam_track)
	{
		player_state_t	state;

		memset (&state, 0, sizeof(state));
		state.pm_type = PM_SPECTATOR;
		VectorCopy (cl.simorg, state.origin);
		VectorCopy (cl.simvel, state.velocity);

		CL_PredictUsercmd (&state, &state, &cl.lastcmd);

		VectorCopy (state.origin, cl.simorg);
		VectorCopy (state.velocity, cl.simvel);
		VectorCopy (cl.viewangles, cl.simangles);
		cl.onground = false;
		return;
	}
#endif

	if (cl.paused)
		return;

	// set up prediction for other players
	CL_SetUpPlayerPrediction (false);

	// predict the local player, lerp movement, etc
	CL_PredictLocalPlayer ();

	// predict other players
	CL_SetUpPlayerPrediction (true);
}


/*
==============
CL_InitPrediction
==============
*/
void CL_InitPrediction (void)
{
	Cvar_Register (&cl_nopred);
	Cvar_Register (&cl_nolerp);
}

