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
// cl_tent.c -- client side temporary entities

#include "quakedef.h"
#include "pmove.h"
#include "sound.h"

#define	MAX_BEAMS	32
typedef struct
{
	int		entity;
	struct model_s	*model;
	float	endtime;
	vec3_t	start, end;
} beam_t;

beam_t		cl_beams[MAX_BEAMS];

static vec3_t	playerbeam_end;


#define	MAX_EXPLOSIONS	32
typedef struct explosion_s
{
	struct explosion_s *prev, *next;
	vec3_t	origin;
	float	start;
	struct model_s	*model;
} explosion_t;

explosion_t	cl_explosions[MAX_EXPLOSIONS];
explosion_t cl_explosions_headnode, *cl_free_explosions;

static sfx_t			*cl_sfx_wizhit;
static sfx_t			*cl_sfx_knighthit;
static sfx_t			*cl_sfx_tink1;
static sfx_t			*cl_sfx_ric1;
static sfx_t			*cl_sfx_ric2;
static sfx_t			*cl_sfx_ric3;
static sfx_t			*cl_sfx_r_exp3;

static struct model_s	*cl_explo_mod;
static struct model_s	*cl_bolt1_mod;
static struct model_s	*cl_bolt2_mod;
static struct model_s	*cl_bolt3_mod;
static struct model_s	*cl_beam_mod;

cvar_t	cl_fakeshaft = {"cl_fakeshaft", "0"};
cvar_t	r_shaftalpha = {"r_shaftalpha", "1"};


/*
=================
CL_ParseTEnts
=================
*/
void CL_InitTEnts (void)
{
	Cvar_Register (&cl_fakeshaft);
	Cvar_Register (&r_shaftalpha);

	cl_sfx_wizhit = S_PrecacheSound ("wizard/hit.wav");
	cl_sfx_knighthit = S_PrecacheSound ("hknight/hit.wav");
	cl_sfx_tink1 = S_PrecacheSound ("weapons/tink1.wav");
	cl_sfx_ric1 = S_PrecacheSound ("weapons/ric1.wav");
	cl_sfx_ric2 = S_PrecacheSound ("weapons/ric2.wav");
	cl_sfx_ric3 = S_PrecacheSound ("weapons/ric3.wav");
	cl_sfx_r_exp3 = S_PrecacheSound ("weapons/r_exp3.wav");
}

/*
=================
CL_ClearTEnts
=================
*/
void CL_ClearTEnts (void)
{
	int i;

	cl_explo_mod = cl_beam_mod = NULL;
	cl_bolt1_mod = cl_bolt2_mod = cl_bolt3_mod = NULL;

	memset (&cl_beams, 0, sizeof(cl_beams));
	memset (&cl_explosions, 0, sizeof(cl_explosions));

	// link explosions
	cl_free_explosions = cl_explosions;
	cl_explosions_headnode.prev = &cl_explosions_headnode;
	cl_explosions_headnode.next = &cl_explosions_headnode;

	for (i = 0; i < MAX_EXPLOSIONS-1; i++)
		cl_explosions[i].next = &cl_explosions[i+1];
}

/*
=================
CL_AllocExplosion
=================
*/
explosion_t *CL_AllocExplosion (void)
{
	explosion_t *ex;

	if ( cl_free_explosions )
	{	// take a free explosion if possible
		ex = cl_free_explosions;
		cl_free_explosions = ex->next;
	} 
	else 
	{	// grab the oldest one otherwise
		ex = cl_explosions_headnode.prev;
		ex->prev->next = ex->next;
		ex->next->prev = ex->prev;
	}

	// put the explosion at the start of the list
	ex->prev = &cl_explosions_headnode;
	ex->next = cl_explosions_headnode.next;
	ex->next->prev = ex;
	ex->prev->next = ex;

	return ex;
}

/*
=================
CL_FreeExplosion
=================
*/
void CL_FreeExplosion (explosion_t *ex)
{
	// remove from linked active list
	ex->prev->next = ex->next;
	ex->next->prev = ex->prev;

	// insert into linked free list
	ex->next = cl_free_explosions;
	cl_free_explosions = ex;
}

/*
=================
CL_ParseBeam
=================
*/
void CL_ParseBeam (int type)
{
	int		ent;
	vec3_t	start, end;
	beam_t	*b;
	struct model_s *m;
	int		i;
	
	ent = MSG_ReadShort ();
	
	start[0] = MSG_ReadCoord ();
	start[1] = MSG_ReadCoord ();
	start[2] = MSG_ReadCoord ();
	
	end[0] = MSG_ReadCoord ();
	end[1] = MSG_ReadCoord ();
	end[2] = MSG_ReadCoord ();

	// an experimental protocol extension:
	// TE_LIGHTNING1 with entity num in -512..-1 range is a rail trail
	if (type == 1 && (ent >= -512 && ent <= -1)) {
		int colors[8] = { 6 /* white (change to something else?) */,
			208 /* blue */,
			180 /* green */, 35 /* light blue */, 224 /* red */,
			133 /* magenta... kinda */, 192 /* yellow */, 6 /* white */};
		int color;
		int pnum, cnum;

		// -512..-257 are colored trails assigned to a specific
		// player, so overrides can be applied; encoded as follows:
		// 7654321076543210
		// 1111111nnnnnnccc  (n = player num, c = color code)
		cnum = ent & 7;
		pnum = (ent >> 3) & 63;
		if (pnum < MAX_CLIENTS)
		{
			// TODO: apply team/enemy overrides
		}
		color = colors[cnum];

		CL_RailTrail (start, end, color);
		return;
	}

	switch (type) {
	case 1:
		if (!cl_bolt1_mod)
			cl_bolt1_mod = Mod_ForName ("progs/bolt.mdl", true, false);
		m = cl_bolt1_mod;
		break;
	case 2:
		if (!cl_bolt2_mod)
			cl_bolt2_mod = Mod_ForName ("progs/bolt2.mdl", true, false);
		m = cl_bolt2_mod;
		break;
	case 3:
		if (!cl_bolt3_mod)
			cl_bolt3_mod = Mod_ForName ("progs/bolt3.mdl", true, false);
		m = cl_bolt3_mod;
		break;
	case 4: default:
		if (!cl_beam_mod)
			cl_beam_mod = Mod_ForName ("progs/beam.mdl", true, false);
		m = cl_beam_mod;
		break;
	}

	if (ent == Cam_PlayerNum() + 1)
		VectorCopy (end, playerbeam_end);	// for cl_fakeshaft

// override any beam with the same entity
	for (i = 0, b = cl_beams; i < MAX_BEAMS; i++, b++)
		if (b->entity == ent)
		{
			b->model = m;
			b->endtime = cl.time + 0.2;
			VectorCopy (start, b->start);
			VectorCopy (end, b->end);
			return;
		}

// find a free beam
	for (i = 0, b = cl_beams; i < MAX_BEAMS; i++, b++)
	{
		if (!b->model || b->endtime < cl.time)
		{
			b->entity = ent;
			b->model = m;
			b->endtime = cl.time + 0.2;
			VectorCopy (start, b->start);
			VectorCopy (end, b->end);
			return;
		}
	}

	Com_DPrintf ("beam list overflow!\n");	
}

/*
=================
CL_ParseTEnt
=================
*/
void CL_ParseTEnt (void)
{
	int		type;
	vec3_t	pos;
	cdlight_t	*dl;
	int		rnd;
	explosion_t	*ex;
	int		cnt;

	type = MSG_ReadByte ();
	switch (type)
	{
	case TE_WIZSPIKE:			// spike hitting wall
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_RunParticleEffect (pos, vec3_origin, 20, 30);
		S_StartSound (-1, 0, cl_sfx_wizhit, pos, 1, 1);
		break;

	case TE_KNIGHTSPIKE:			// spike hitting wall
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_RunParticleEffect (pos, vec3_origin, 226, 20);
		S_StartSound (-1, 0, cl_sfx_knighthit, pos, 1, 1);
		break;

	case TE_SPIKE:			// spike hitting wall
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_RunParticleEffect (pos, vec3_origin, 0, 10);

		if ( rand() % 5 )
			S_StartSound (-1, 0, cl_sfx_tink1, pos, 1, 1);
		else
		{
			rnd = rand() & 3;
			if (rnd == 1)
				S_StartSound (-1, 0, cl_sfx_ric1, pos, 1, 1);
			else if (rnd == 2)
				S_StartSound (-1, 0, cl_sfx_ric2, pos, 1, 1);
			else
				S_StartSound (-1, 0, cl_sfx_ric3, pos, 1, 1);
		}
		break;

	case TE_SUPERSPIKE:			// super spike hitting wall
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_RunParticleEffect (pos, vec3_origin, 0, 20);

		if ( rand() % 5 )
			S_StartSound (-1, 0, cl_sfx_tink1, pos, 1, 1);
		else
		{
			rnd = rand() & 3;
			if (rnd == 1)
				S_StartSound (-1, 0, cl_sfx_ric1, pos, 1, 1);
			else if (rnd == 2)
				S_StartSound (-1, 0, cl_sfx_ric2, pos, 1, 1);
			else
				S_StartSound (-1, 0, cl_sfx_ric3, pos, 1, 1);
		}
		break;

	case TE_EXPLOSION:			// rocket explosion
	// particles

		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();

		if (cl_explosion.value == 6)
			CL_TeleportSplash (pos);
		else if (cl_explosion.value == 7)
			CL_RunParticleEffect (pos, vec3_origin, 73, 20*32);
		else if (cl_explosion.value == 8)
			CL_RunParticleEffect (pos, vec3_origin, 225, 50);
		else
		{

		// Tonik: explosion modifiers...
			if (cl_explosion.value != 1 && cl_explosion.value != 3)
			{
				CL_ParticleExplosion (pos);
			}
		
		// light
			if (cl_explosion.value != 2 && cl_explosion.value != 3)
			{
				dl = CL_AllocDlight (0);
				VectorCopy (pos, dl->origin);
				dl->radius = 350;
				dl->die = cl.time + 0.5;
				dl->decay = 300;
				dl->type = lt_explosion;
			}
		}

	// sound
		S_StartSound (-1, 0, cl_sfx_r_exp3, pos, 1, 1);

	// sprite
		if (cl_explosion.value != 6 && cl_explosion.value != 7 && cl_explosion.value != 8)
		{
			if (!cl_explo_mod)
				cl_explo_mod = Mod_ForName ("progs/s_explod.spr", true, false);
			ex = CL_AllocExplosion ();
			VectorCopy (pos, ex->origin);
			ex->start = cl.time;
			ex->model = cl_explo_mod;
		}
		break;

	case TE_TAREXPLOSION:			// tarbaby explosion
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_BlobExplosion (pos);

		S_StartSound (-1, 0, cl_sfx_r_exp3, pos, 1, 1);
		break;

	case TE_LIGHTNING1:			// lightning bolts
		CL_ParseBeam (1);
		break;

	case TE_LIGHTNING2:			// lightning bolts
		CL_ParseBeam (2);
		break;

	case TE_LIGHTNING3:			// lightning bolts
		CL_ParseBeam (3);
		break;

	case TE_LAVASPLASH:	
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_LavaSplash (pos);
		break;

	case TE_TELEPORT:
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_TeleportSplash (pos);
		break;

	case TE_GUNSHOT:			// bullet hitting wall
		if (cls.nqprotocol)
			cnt = 1;
		else
			cnt = MSG_ReadByte ();
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_RunParticleEffect (pos, vec3_origin, 0, 20*cnt);
		break;

	case TE_BLOOD:				// bullets hitting body
		if (cls.nqprotocol) {
			// NQ_TE_EXPLOSION2
			int colorStart, colorLength;
			pos[0] = MSG_ReadCoord ();
			pos[1] = MSG_ReadCoord ();
			pos[2] = MSG_ReadCoord ();
			colorStart = MSG_ReadByte ();
			colorLength = MSG_ReadByte ();
			CL_ParticleExplosion2 (pos, colorStart, colorLength);
			dl = CL_AllocDlight (0);
			VectorCopy (pos, dl->origin);
			dl->radius = 350;
			dl->die = cl.time + 0.5;
			dl->decay = 300;
			S_StartSound (-1, 0, cl_sfx_r_exp3, pos, 1, 1);
			break;
		}
		cnt = MSG_ReadByte ();
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_RunParticleEffect (pos, vec3_origin, 73, 20*cnt);
		break;

	case TE_LIGHTNINGBLOOD:		// lightning hitting body
		if (cls.nqprotocol) {
			// NQ_TE_BEAM - grappling hook beam
			CL_ParseBeam (4);
			break;
		}
		pos[0] = MSG_ReadCoord ();
		pos[1] = MSG_ReadCoord ();
		pos[2] = MSG_ReadCoord ();
		CL_RunParticleEffect (pos, vec3_origin, 225, 50);
		break;

	default:
		Host_Error ("CL_ParseTEnt: bad type");
	}
}


/*
=================
CL_UpdateBeams
=================
*/
void CL_UpdateBeams (void)
{
	int			i;
	beam_t		*b;
	vec3_t		dist, org;
	float		d, dec;
	entity_t	ent;
	vec3_t		angles;

	dec = 30;
	memset (&ent, 0, sizeof(entity_t));
	ent.colormap = 0;

// update lightning
	for (i = 0, b = cl_beams; i < MAX_BEAMS; i++, b++)
	{
		if (!b->model || b->endtime < cl.time)
			continue;

	// if coming from the player, update the start position
		if (b->entity == Cam_PlayerNum() + 1 && !cl.intermission)
		{
			VectorCopy (cl.simorg, b->start);
			b->start[2] += cl.crouch;
			if (cl_fakeshaft.value && cl.allow_fakeshaft)
			{
				vec3_t	forward;
				vec3_t	v, org;
				vec3_t	ang;
				float	f, delta;
				trace_t	trace;

				f = max(0, min(1, cl_fakeshaft.value));

				VectorSubtract (playerbeam_end, cl.simorg, v);
				v[2] -= 22;		// adjust for view height
				vectoangles (v, ang);

				// lerp pitch
				ang[0] = -ang[0];
				if (ang[0] < -180)
					ang[0] += 360;
				ang[0] += (cl.simangles[0] - ang[0]) * f;

				// lerp yaw
				delta = cl.simangles[1] - ang[1];
				if (delta > 180)
					delta -= 360;
				if (delta < -180)
					delta += 360;
				ang[1] += delta*f;
				ang[2] = 0;

				AngleVectors (ang, forward, NULL, NULL);
				VectorScale (forward, 600, forward);
				VectorCopy (cl.simorg, org);
				org[2] += 16;
				VectorAdd (org, forward, b->end);

				trace = PM_TraceLine (&cl.pmove, org, b->end);
				if (trace.fraction < 1)
					VectorCopy (trace.endpos, b->end);
			}
		}

	// calculate pitch and yaw
		VectorSubtract (b->end, b->start, dist);
		vectoangles (dist, angles);

	// add new entities for the lightning
		VectorCopy (b->start, org);
		d = VectorNormalize (dist);
		VectorScale (dist, dec, dist);

		while (d > 0)
		{
			VectorCopy (org, ent.origin);
			ent.model = b->model;
			ent.angles[PITCH] = angles[PITCH];
			ent.angles[YAW] = angles[YAW];
			ent.angles[ROLL] = rand()%360;
			if (b->model == cl_bolt2_mod) {
				ent.alpha = r_shaftalpha.value;
				ent.renderfx |= RF_TRANSLUCENT;
			}

			V_AddEntity (&ent);

			d -= dec;
			VectorAdd (org, dist, org);
		}
	}
}

/*
=================
CL_UpdateExplosions
=================
*/
#define EXPLOSION_FRAMES 6
void CL_UpdateExplosions (void)
{
	int			f;
	explosion_t	*ex;
	explosion_t *next, *hnode;
	entity_t	ent;

	memset (&ent, 0, sizeof(entity_t));
	ent.colormap = 0;

	hnode = &cl_explosions_headnode;
	for (ex = hnode->next; ex != hnode; ex = next)
	{
		next = ex->next;
		f = 10 * (cl.time - ex->start);

		if (f >= EXPLOSION_FRAMES)
		{
			CL_FreeExplosion (ex);
			continue;
		}

		VectorCopy (ex->origin, ent.origin);
		ent.model = ex->model;
		ent.frame = f;

		V_AddEntity (&ent);
	}
}

/*
=================
CL_UpdateTEnts
=================
*/
void CL_UpdateTEnts (void)
{
	CL_UpdateBeams ();
	CL_UpdateExplosions ();
}
