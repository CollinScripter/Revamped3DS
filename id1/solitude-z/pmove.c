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

#include "common.h"
#include "pmove.h"

static movevars_t	movevars;
static playermove_t	*pm;

static float		pm_frametime;
static vec3_t		pm_forward, pm_right;

// these are referenced from other subsystems as well
vec3_t	player_mins = {-16, -16, -24};
vec3_t	player_maxs = {16, 16, 32};


void PM_Init (void)
{
}

#define	STEPSIZE	18
#define	MIN_STEP_NORMAL	0.7		// roughly 45 degrees

#define pm_flyfriction 4

#define BLOCKED_FLOOR	1
#define BLOCKED_STEP	2
#define BLOCKED_OTHER	4
#define BLOCKED_ANY		7


/*
** Add an entity to touch list, discarding duplicates
*/
static void PM_AddTouchedEnt (int num)
{
	int i;

	if (pm->numtouch == sizeof(pm->touchindex)/sizeof(pm->touchindex[0]))
		return;

	for (i = 0; i < pm->numtouch; i++)
		if (pm->touchindex[i] == num)
			return;		// already added

	pm->touchindex[pm->numtouch] = num;
	pm->numtouch++;
}


/*
==================
PM_ClipVelocity

Slide off of the impacting object
==================
*/
#define	STOP_EPSILON	0.1

void PM_ClipVelocity (vec3_t in, vec3_t normal, vec3_t out, float overbounce)
{
	float	backoff;
	float	change;
	int		i;
	
	backoff = DotProduct (in, normal) * overbounce;

	for (i=0 ; i<3 ; i++)
	{
		change = normal[i]*backoff;
		out[i] = in[i] - change;
		if (out[i] > -STOP_EPSILON && out[i] < STOP_EPSILON)
			out[i] = 0;
	}
}


/*
============
PM_SlideMove

The basic solid body movement clip that slides along multiple planes
============
*/
#define	MAX_CLIP_PLANES	5

int PM_SlideMove (void)
{
	int			bumpcount, numbumps;
	vec3_t		dir;
	float		d;
	int			numplanes;
	vec3_t		planes[MAX_CLIP_PLANES];
	vec3_t		primal_velocity, original_velocity;
	int			i, j;
	trace_t		trace;
	vec3_t		end;
	float		time_left;
	int			blocked;
	
	numbumps = 4;
	
	blocked = 0;
	VectorCopy (pm->velocity, original_velocity);
	VectorCopy (pm->velocity, primal_velocity);
	numplanes = 0;
	
	time_left = pm_frametime;

	for (bumpcount=0 ; bumpcount<numbumps ; bumpcount++)
	{
		for (i=0 ; i<3 ; i++)
			end[i] = pm->origin[i] + time_left * pm->velocity[i];

		trace = PM_PlayerTrace (pm, pm->origin, end);

		if (trace.startsolid || trace.allsolid)
		{	// entity is trapped in another solid
			VectorClear (pm->velocity);
			return 3;
		}

		if (trace.fraction > 0)
		{	// actually covered some distance
			VectorCopy (trace.endpos, pm->origin);
			numplanes = 0;
		}

		if (trace.fraction == 1)
			 break;		// moved the entire distance

		// save entity for contact
		PM_AddTouchedEnt (trace.e.entnum);

		if (trace.plane.normal[2] >= MIN_STEP_NORMAL)
			blocked |= BLOCKED_FLOOR;
		else if (!trace.plane.normal[2])
			blocked |= BLOCKED_STEP;
		else
			blocked |= BLOCKED_OTHER;

		time_left -= time_left * trace.fraction;
		
	// cliped to another plane
		if (numplanes >= MAX_CLIP_PLANES)
		{	// this shouldn't really happen
			VectorClear (pm->velocity);
			break;
		}

		VectorCopy (trace.plane.normal, planes[numplanes]);
		numplanes++;

//
// modify original_velocity so it parallels all of the clip planes
//
		for (i=0 ; i<numplanes ; i++)
		{
			PM_ClipVelocity (original_velocity, planes[i], pm->velocity, 1);
			for (j=0 ; j<numplanes ; j++)
				if (j != i)
				{
					if (DotProduct (pm->velocity, planes[j]) < 0)
						break;	// not ok
				}
			if (j == numplanes)
				break;
		}
		
		if (i != numplanes)
		{	// go along this plane
		}
		else
		{	// go along the crease
			if (numplanes != 2)
			{
				VectorClear (pm->velocity);
				break;
			}
			CrossProduct (planes[0], planes[1], dir);
			d = DotProduct (dir, pm->velocity);
			VectorScale (dir, d, pm->velocity);
		}

//
// if velocity is against the original velocity, stop dead
// to avoid tiny occilations in sloping corners
//
		if (DotProduct (pm->velocity, primal_velocity) <= 0)
		{
			VectorClear (pm->velocity);
			break;
		}
	}

	if (pm->waterjumptime)
	{
		VectorCopy (primal_velocity, pm->velocity);
	}
	return blocked;
}

/*
=============
PM_StepSlideMove

Each intersection will try to step over the obstruction instead of
sliding along it.
=============
*/
int PM_StepSlideMove (qbool in_air)
{
	vec3_t	dest;
	trace_t	trace;
	vec3_t	original, originalvel, down, up, downvel;
	float	downdist, updist;
	int		blocked;
	float	stepsize;

	// try sliding forward both on ground and up 16 pixels
	// take the move that goes farthest
	VectorCopy (pm->origin, original);
	VectorCopy (pm->velocity, originalvel);

	blocked = PM_SlideMove ();

	if (!blocked)
		return blocked;		// moved the entire distance

	if (in_air) {
		// don't let us step up unless it's indeed a step we bumped in
		// (that is, there's solid ground below)
		float *org;

		if (!(blocked & BLOCKED_STEP))
			return blocked;

		//FIXME: "pm->velocity < 0" ???? :)
		// Of course I meant pm->velocity[2], but I'm afraid I don't understand
		// the code's purpose any more, so let it stay just this way for now :)  -- Tonik
		org = (pm->velocity < 0) ? pm->origin : original;	// cryptic, eh?
		VectorCopy (org, dest);
		dest[2] -= STEPSIZE;
		trace = PM_PlayerTrace (pm, org, dest);
		if (trace.fraction == 1 || trace.plane.normal[2] < MIN_STEP_NORMAL)
			return blocked;

		// adjust stepsize, otherwise it would be possible to walk up a
		// a step higher than STEPSIZE
		stepsize = STEPSIZE - (org[2] - trace.endpos[2]);
	}
	else
		stepsize = STEPSIZE;

	VectorCopy (pm->origin, down);
	VectorCopy (pm->velocity, downvel);

	VectorCopy (original, pm->origin);
	VectorCopy (originalvel, pm->velocity);

// move up a stair height
	VectorCopy (pm->origin, dest);
	dest[2] += stepsize;
	trace = PM_PlayerTrace (pm, pm->origin, dest);
	if (!trace.startsolid && !trace.allsolid)
	{
		VectorCopy (trace.endpos, pm->origin);
	}

	PM_SlideMove ();

// press down the stepheight
	VectorCopy (pm->origin, dest);
	dest[2] -= stepsize;
	trace = PM_PlayerTrace (pm, pm->origin, dest);
	if (trace.fraction != 1 && trace.plane.normal[2] < MIN_STEP_NORMAL)
		goto usedown;
	if (!trace.startsolid && !trace.allsolid)
	{
		VectorCopy (trace.endpos, pm->origin);
	}

	if (pm->origin[2] < original[2])
		goto usedown;

	VectorCopy (pm->origin, up);

	// decide which one went farther
	downdist = (down[0] - original[0])*(down[0] - original[0])
		+ (down[1] - original[1])*(down[1] - original[1]);
	updist = (up[0] - original[0])*(up[0] - original[0])
		+ (up[1] - original[1])*(up[1] - original[1]);

	if (downdist >= updist)
	{
usedown:
		VectorCopy (down, pm->origin);
		VectorCopy (downvel, pm->velocity);
		return blocked;
	}
	
	// copy z value from slide move
	pm->velocity[2] = downvel[2];

	if (!pm->onground && pm->waterlevel < 2 && (blocked & BLOCKED_STEP)) {
		float scale;
		// in pm_airstep mode, walking up a 16 unit high step
		// will kill 16% of horizontal velocity
		scale = 1 - 0.01*(pm->origin[2] - original[2]);
		pm->velocity[0] *= scale;
		pm->velocity[1] *= scale;
	}

	return blocked;
}



/*
==================
PM_Friction

Handles both ground friction and water friction
==================
*/
void PM_Friction (void)
{
	float	speed, newspeed, control;
	float	friction;
	float	drop;
	vec3_t	start, stop;
	trace_t	trace;
	
	if (pm->waterjumptime)
		return;

	speed = VectorLength(pm->velocity);
	if (speed < 1)
	{
		pm->velocity[0] = 0;
		pm->velocity[1] = 0;
		if (pm->pm_type == PM_FLY)
			pm->velocity[2] = 0;
		return;
	}

	if (pm->waterlevel >= 2)
		// apply water friction, even if in fly mode
		drop = speed*movevars.waterfriction*pm->waterlevel*pm_frametime;
	else if (pm->pm_type == PM_FLY) {
		// apply flymode friction
		drop = speed * pm_flyfriction * pm_frametime;
	}
	else if (pm->onground) {
		// apply ground friction
		friction = movevars.friction;

		// if the leading edge is over a dropoff, increase friction
		start[0] = stop[0] = pm->origin[0] + pm->velocity[0]/speed*16;
		start[1] = stop[1] = pm->origin[1] + pm->velocity[1]/speed*16;
		start[2] = pm->origin[2] + player_mins[2];
		stop[2] = start[2] - 34;
		trace = PM_PlayerTrace (pm, start, stop);
		if (trace.fraction == 1)
			friction *= 2;

		control = speed < movevars.stopspeed ? movevars.stopspeed : speed;
		drop = control*friction*pm_frametime;
	}
	else
		return;		// in air, no friction


// scale the velocity
	newspeed = speed - drop;
	if (newspeed < 0)
		newspeed = 0;

	VectorScale (pm->velocity, newspeed / speed, pm->velocity);
}


/*
==============
PM_Accelerate
==============
*/
void PM_Accelerate (vec3_t wishdir, float wishspeed, float accel)
{
	int			i;
	float		addspeed, accelspeed, currentspeed;

	if (pm->pm_type == PM_DEAD)
		return;
	if (pm->waterjumptime)
		return;

	currentspeed = DotProduct (pm->velocity, wishdir);
	addspeed = wishspeed - currentspeed;
	if (addspeed <= 0)
		return;
	accelspeed = accel*pm_frametime*wishspeed;
	if (accelspeed > addspeed)
		accelspeed = addspeed;
	
	for (i=0 ; i<3 ; i++)
		pm->velocity[i] += accelspeed*wishdir[i];
}

void PM_AirAccelerate (vec3_t wishdir, float wishspeed, float accel)
{
	int			i;
	float		addspeed, accelspeed, currentspeed, wishspd = wishspeed;
	float		originalspeed = 0.0, newspeed = 0.0, speedcap = 0.0;
		
	if (pm->pm_type == PM_DEAD)
		return;
	if (pm->waterjumptime)
		return;

	if (movevars.bunnyspeedcap > 0)
	{
		originalspeed = sqrt(pm->velocity[0]*pm->velocity[0] +
						pm->velocity[1]*pm->velocity[1]);
	}

	if (wishspd > 30)
		wishspd = 30;
	currentspeed = DotProduct (pm->velocity, wishdir);
	addspeed = wishspd - currentspeed;
	if (addspeed <= 0)
		return;
	accelspeed = accel * wishspeed * pm_frametime;
	if (accelspeed > addspeed)
		accelspeed = addspeed;
	
	for (i=0 ; i<3 ; i++)
		pm->velocity[i] += accelspeed*wishdir[i];

	if (movevars.bunnyspeedcap > 0)
	{
		newspeed = sqrt(pm->velocity[0]*pm->velocity[0] +
					pm->velocity[1]*pm->velocity[1]);
		if (newspeed > originalspeed)
		{
			speedcap = movevars.maxspeed * movevars.bunnyspeedcap;
			if (newspeed > speedcap)
			{
				if (originalspeed < speedcap)
					originalspeed = speedcap;
				pm->velocity[0] *= originalspeed / newspeed;
				pm->velocity[1] *= originalspeed / newspeed;
			}
		}
	}
}



/*
===================
PM_WaterMove
===================
*/
void PM_WaterMove (void)
{
	int		i;
	vec3_t	wishvel;
	float	wishspeed;
	vec3_t	wishdir;

//
// user intentions
//
	for (i=0 ; i<3 ; i++)
		wishvel[i] = pm_forward[i]*pm->cmd.forwardmove + pm_right[i]*pm->cmd.sidemove;

	if (pm->pm_type != PM_FLY && !pm->cmd.forwardmove && !pm->cmd.sidemove && !pm->cmd.upmove)
		wishvel[2] -= 60;		// drift towards bottom
	else
		wishvel[2] += pm->cmd.upmove;

	VectorCopy (wishvel, wishdir);
	wishspeed = VectorNormalize(wishdir);

	if (wishspeed > movevars.maxspeed) {
		VectorScale (wishvel, movevars.maxspeed/wishspeed, wishvel);
		wishspeed = movevars.maxspeed;
	}
	wishspeed *= 0.7;

//
// water acceleration
//
	PM_Accelerate (wishdir, wishspeed, movevars.wateraccelerate);

	PM_StepSlideMove (false);
}


/*
*/
void PM_FlyMove ()
{
	int		i;
	vec3_t	wishvel;
	float	wishspeed;
	vec3_t	wishdir;

	for (i=0 ; i<3 ; i++)
		wishvel[i] = pm_forward[i]*pm->cmd.forwardmove + pm_right[i]*pm->cmd.sidemove;
	
	wishvel[2] += pm->cmd.upmove;

	VectorCopy (wishvel, wishdir);
	wishspeed = VectorNormalize(wishdir);
	
	if (wishspeed > movevars.maxspeed) {
		VectorScale (wishvel, movevars.maxspeed/wishspeed, wishvel);
		wishspeed = movevars.maxspeed;
	}
	
	PM_Accelerate (wishdir, wishspeed, movevars.accelerate);
	
	PM_StepSlideMove (false);
}


/*
===================
PM_AirMove

===================
*/
void PM_AirMove (void)
{
	int			i;
	vec3_t		wishvel;
	float		fmove, smove;
	vec3_t		wishdir;
	float		wishspeed;

	fmove = pm->cmd.forwardmove;
	smove = pm->cmd.sidemove;
	
	pm_forward[2] = 0;
	pm_right[2] = 0;
	VectorNormalize (pm_forward);
	VectorNormalize (pm_right);

	for (i=0 ; i<2 ; i++)
		wishvel[i] = pm_forward[i]*fmove + pm_right[i]*smove;
	wishvel[2] = 0;

	VectorCopy (wishvel, wishdir);
	wishspeed = VectorNormalize(wishdir);

//
// clamp to server defined max speed
//
	if (wishspeed > movevars.maxspeed)
	{
		VectorScale (wishvel, movevars.maxspeed/wishspeed, wishvel);
		wishspeed = movevars.maxspeed;
	}
	
	if (pm->onground)
	{
		if (movevars.slidefix)
		{
			pm->velocity[2] = min(pm->velocity[2], 0);	// bound above by 0
			PM_Accelerate (wishdir, wishspeed, movevars.accelerate);
			// add gravity
			pm->velocity[2] -= movevars.entgravity * movevars.gravity * pm_frametime;
		}
		else
		{
			pm->velocity[2] = 0;
			PM_Accelerate (wishdir, wishspeed, movevars.accelerate);
		}

		if (!pm->velocity[0] && !pm->velocity[1]) {
			pm->velocity[2] = 0;
			return;
		}

		PM_StepSlideMove(false);
	}
	else
	{
		int blocked;
		
		// not on ground, so little effect on velocity
		PM_AirAccelerate (wishdir, wishspeed, movevars.accelerate);

		// add gravity
		pm->velocity[2] -= movevars.entgravity * movevars.gravity * pm_frametime;

		if (movevars.airstep)
			blocked = PM_StepSlideMove (true);
		else
			blocked = PM_SlideMove ();

		if (movevars.pground)
		{
			if (blocked & BLOCKED_FLOOR)
				pm->onground = true;
		}
	}
}


plane_t	groundplane;

/*
=============
PM_CategorizePosition
=============
*/
void PM_CategorizePosition (playermove_t *pm)
{
	vec3_t		point;
	int			cont;
	trace_t	trace;

// if the player hull point one unit down is solid, the player
// is on ground

// see if standing on something solid
	point[0] = pm->origin[0];
	point[1] = pm->origin[1];
	point[2] = pm->origin[2] - 1;
	if (pm->velocity[2] > 180)
	{
		pm->onground = false;
	}
	else if (!movevars.pground || pm->onground)
	{
		trace = PM_PlayerTrace (pm, pm->origin, point);
		if (trace.fraction == 1 || trace.plane.normal[2] < MIN_STEP_NORMAL)
			pm->onground = false;
		else
		{
			pm->onground = true;
			pm->groundent = trace.e.entnum;
			groundplane = trace.plane;
			pm->waterjumptime = 0;
		}

		// standing on an entity other than the world
		if (trace.e.entnum > 0)
			PM_AddTouchedEnt (trace.e.entnum);
	}

//
// get waterlevel
//
	pm->waterlevel = 0;
	pm->watertype = CONTENTS_EMPTY;

	point[2] = pm->origin[2] + player_mins[2] + 1;
	cont = PM_PointContents (pm, point);

	if (cont <= CONTENTS_WATER)
	{
		pm->watertype = cont;
		pm->waterlevel = 1;
		point[2] = pm->origin[2] + (player_mins[2] + player_maxs[2])*0.5;
		cont = PM_PointContents (pm, point);
		if (cont <= CONTENTS_WATER)
		{
			pm->waterlevel = 2;
			point[2] = pm->origin[2] + 22;
			cont = PM_PointContents (pm, point);
			if (cont <= CONTENTS_WATER)
				pm->waterlevel = 3;
		}
	}

	if (!movevars.pground)
	{
		if (pm->onground && pm->pm_type != PM_FLY && pm->waterlevel < 2)
		{
			// snap to ground so that we can't jump higher than we're supposed to
			if (!trace.startsolid && !trace.allsolid)
				VectorCopy (trace.endpos, pm->origin);
		}
	}
}


/*
=============
PM_CheckJump
=============
*/
void PM_CheckJump (void)
{
	if (pm->pm_type == PM_FLY)
		return;

	if (pm->pm_type == PM_DEAD)
	{
		pm->jump_held = true;	// don't jump on respawn
		return;
	}

	if (!(pm->cmd.buttons & BUTTON_JUMP))
	{
		pm->jump_held = false;
		return;
	}

	if (pm->waterjumptime)
		return;

	if (pm->waterlevel >= 2)
	{	// swimming, not jumping
		pm->onground = false;

		if (pm->watertype == CONTENTS_WATER)
			pm->velocity[2] = 100;
		else if (pm->watertype == CONTENTS_SLIME)
			pm->velocity[2] = 80;
		else
			pm->velocity[2] = 50;
		return;
	}

	if (!pm->onground)
		return;		// in air, so no effect

#ifdef SERVERONLY
	if (pm->jump_held)
		return;		// don't pogo stick
#else
	if (pm->jump_held && !pm->jump_msec)
		return;		// don't pogo stick
#endif

	if (!movevars.pground)
	{
		// check for jump bug
		// groundplane normal was set in the call to PM_CategorizePosition
		if (pm->velocity[2] < 0 &&
			DotProduct(pm->velocity, groundplane.normal) < -0.1)
		{
			// pm->velocity is pointing into the ground, clip it
			PM_ClipVelocity (pm->velocity, groundplane.normal, pm->velocity, 1);
		}
	}

	pm->onground = false;
	pm->velocity[2] += 270;

	if (movevars.ktjump > 0)
	{
		if (movevars.ktjump > 1)
			movevars.ktjump = 1;
		if (pm->velocity[2] < 270)
			pm->velocity[2] = pm->velocity[2] * (1 - movevars.ktjump)
				+ 270 * movevars.ktjump;
	}

	pm->jump_held = true;		// don't jump again until released

#ifndef SERVERONLY
	pm->jump_msec = pm->cmd.msec;
#endif
}

/*
=============
PM_CheckWaterJump
=============
*/
void PM_CheckWaterJump (void)
{
	vec3_t	spot;
	int		cont;
	vec3_t	flatforward;

	if (pm->waterjumptime)
		return;

	// don't hop out if we just jumped in
	if (pm->velocity[2] < -180)
		return;

	// see if near an edge
	flatforward[0] = pm_forward[0];
	flatforward[1] = pm_forward[1];
	flatforward[2] = 0;
	VectorNormalize (flatforward);

	VectorMA (pm->origin, 24, flatforward, spot);
	spot[2] += 8;
	cont = PM_PointContents (pm, spot);
	if (cont != CONTENTS_SOLID)
		return;
	spot[2] += 24;
	cont = PM_PointContents (pm, spot);
	if (cont != CONTENTS_EMPTY)
		return;
	// jump out of water
	VectorScale (flatforward, 50, pm->velocity);
	pm->velocity[2] = 310;
	pm->waterjumptime = 2;	// safety net
	pm->jump_held = true;		// don't jump again until released
}

/*
=================
PM_NudgePosition

If pm->origin is in a solid position,
try nudging slightly on all axis to
allow for the cut precision of the net coordinates
=================
*/
void PM_NudgePosition (void)
{
	vec3_t	base;
	int		x, y, z;
	int		i;
	static int	sign[3] = {0, -1, 1};

	VectorCopy (pm->origin, base);

	for (i=0 ; i<3 ; i++)
		pm->origin[i] = ((int)(pm->origin[i]*8)) * 0.125;

	for (z=0 ; z<=2 ; z++)
	{
		for (x=0 ; x<=2 ; x++)
		{
			for (y=0 ; y<=2 ; y++)
			{
				pm->origin[0] = base[0] + (sign[x] * 1.0/8);
				pm->origin[1] = base[1] + (sign[y] * 1.0/8);
				pm->origin[2] = base[2] + (sign[z] * 1.0/8);
				if (PM_TestPlayerPosition (pm, pm->origin))
					return;
			}
		}
	}

	// some maps spawn the player several units into the ground
	for (z=1 ; z<=18 ; z++)
	{
		pm->origin[0] = base[0];
		pm->origin[1] = base[1];
		pm->origin[2] = base[2] + z;
		if (PM_TestPlayerPosition(pm, pm->origin))
			return;
	}

	VectorCopy (base, pm->origin);
//	Com_DPrintf ("NudgePosition: stuck\n");
}

/*
===============
PM_SpectatorMove
===============
*/
void PM_SpectatorMove (void)
{
	float	speed, drop, friction, control, newspeed;
	float	currentspeed, addspeed, accelspeed;
	int			i;
	vec3_t		wishvel;
	float		fmove, smove;
	vec3_t		wishdir;
	float		wishspeed;

	// friction

	speed = VectorLength (pm->velocity);
	if (speed < 1)
	{
		VectorClear (pm->velocity);
	}
	else
	{
		drop = 0;

		friction = movevars.friction*1.5;	// extra friction
		control = speed < movevars.stopspeed ? movevars.stopspeed : speed;
		drop += control*friction*pm_frametime;

		// scale the velocity
		newspeed = speed - drop;
		if (newspeed < 0)
			newspeed = 0;
		newspeed /= speed;

		VectorScale (pm->velocity, newspeed, pm->velocity);
	}

	// accelerate
	fmove = pm->cmd.forwardmove;
	smove = pm->cmd.sidemove;
	
	VectorNormalize (pm_forward);
	VectorNormalize (pm_right);

	for (i=0 ; i<3 ; i++)
		wishvel[i] = pm_forward[i]*fmove + pm_right[i]*smove;
	wishvel[2] += pm->cmd.upmove;

	VectorCopy (wishvel, wishdir);
	wishspeed = VectorNormalize(wishdir);

	//
	// clamp to server defined max speed
	//
	if (wishspeed > movevars.spectatormaxspeed)
	{
		VectorScale (wishvel, movevars.spectatormaxspeed/wishspeed, wishvel);
		wishspeed = movevars.spectatormaxspeed;
	}

	currentspeed = DotProduct(pm->velocity, wishdir);
	addspeed = wishspeed - currentspeed;

	// Buggy QW spectator mode, kept for compatibility
	if (pm->pm_type == PM_OLD_SPECTATOR) {
		if (addspeed <= 0)
			return;
	}

	if (addspeed > 0) {
		accelspeed = movevars.accelerate*pm_frametime*wishspeed;
		if (accelspeed > addspeed)
			accelspeed = addspeed;
		
		for (i=0 ; i<3 ; i++)
			pm->velocity[i] += accelspeed*wishdir[i];	
	}

	// move
	VectorMA (pm->origin, pm_frametime, pm->velocity, pm->origin);
}

/*
=============
PM_PlayerMove

Returns with origin, angles, and velocity modified in place.

Numtouch and touchindex[] will be set if any of the physents
were contacted during the move.
=============
*/
void PM_PlayerMove (playermove_t *pmove, movevars_t *_movevars)
{
	qbool oldonground;
	vec3_t oldvelocity;

	pm = pmove;
	movevars = *_movevars;

	pm_frametime = pm->cmd.msec * 0.001;
	pm->numtouch = 0;
	pm->landspeed = 0;

	if (pm->pm_type == PM_NONE || pm->pm_type == PM_FREEZE) {
		PM_CategorizePosition (pm);
		return;
	}

	// take angles directly from command
	VectorCopy (pm->cmd.angles, pm->angles);
	AngleVectors (pm->angles, pm_forward, pm_right, NULL);

	if (pm->pm_type == PM_SPECTATOR || pm->pm_type == PM_OLD_SPECTATOR)
	{
		PM_SpectatorMove ();
		pm->onground = false;
		return;
	}

	PM_NudgePosition ();

	// set onground, watertype, and waterlevel
	PM_CategorizePosition (pm);

	VectorCopy (pm->velocity, oldvelocity);
	oldonground = pm->onground;

	if (pm->waterlevel == 2 && pm->pm_type != PM_FLY)
		PM_CheckWaterJump ();

	if (pm->velocity[2] < 0 || pm->pm_type == PM_DEAD)
		pm->waterjumptime = 0;

	if (pm->waterjumptime) {
		pm->waterjumptime -= pm_frametime;
		if (pm->waterjumptime < 0)
			pm->waterjumptime = 0;
	}

#ifndef SERVERONLY
	if (pm->jump_msec) {
		pm->jump_msec += pm->cmd.msec;
		if (pm->jump_msec > 50)
			pm->jump_msec = 0;
	}
#endif

	PM_CheckJump ();

	PM_Friction ();

	if (pm->waterlevel >= 2)
		PM_WaterMove ();
	else if (pm->pm_type == PM_FLY)
		PM_FlyMove ();
	else
		PM_AirMove ();

	// set onground, watertype, and waterlevel for final spot
	PM_CategorizePosition (pm);

	if (pm->onground && !oldonground)
		pm->landspeed = oldvelocity[2];

	if (!movevars.pground)
	{
		// this is to make sure landing sound is not played twice
		// and falling damage is calculated correctly
		if (pm->onground && pm->velocity[2] < -300
			&& DotProduct(pm->velocity, groundplane.normal) < -0.1)
		{
			PM_ClipVelocity (pm->velocity, groundplane.normal, pm->velocity, 1);
		}
	}
}

/* vi: set noet ts=4 sts=4 ai sw=4: */
