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
// cl_ents.c -- entity parsing and management

#include "quakedef.h"
#include "pmove.h"
#include "teamplay.h"

extern cvar_t	cl_predict_players;
extern cvar_t	cl_solid_players;

cvar_t cl_lerp_monsters = {"cl_lerp_monsters", "1"};
cvar_t r_rocketlight = {"r_rocketLight", "1"};
cvar_t r_rockettrail = {"r_rocketTrail", "1"};
cvar_t r_grenadetrail = {"r_grenadeTrail", "1"};
cvar_t r_powerupglow = {"r_powerupGlow", "1"};
cvar_t r_lightflicker = {"r_lightflicker", "1"};
cvar_t	cl_deadbodyfilter = {"cl_deadbodyFilter", "0"};
cvar_t	cl_explosion = {"cl_explosion", "0"};
cvar_t	cl_gibfilter = {"cl_gibFilter", "0"};
cvar_t	cl_gibtime = {"cl_gibtime", "3"};
cvar_t	cl_r2g = {"cl_r2g", "0"};
cvar_t	cl_predict_players = {"cl_predict_players", "1"};
cvar_t	cl_solid_players = {"cl_solid_players", "1"};


static struct predicted_player {
	int		flags;
	qbool	active;
	vec3_t	origin;	// predicted origin
#ifdef MVDPLAY
	qbool predict;
	vec3_t	oldo;
	vec3_t	olda;
	vec3_t	oldv;
	vec3_t	vel;
	player_state_t *oldstate;
#endif
} predicted_players[MAX_CLIENTS];


extern	int		cl_spikeindex, cl_playerindex, cl_flagindex;

/*
=========================================================================

PACKET ENTITY PARSING / LINKING

=========================================================================
*/

/*
==================
CL_ParseDelta

Can go from either a baseline or a previous packet_entity
==================
*/
int	bitcounts[32];	/// just for protocol profiling
void CL_ParseDelta (entity_state_t *from, entity_state_t *to, int bits)
{
	int			i;

	// set everything to the state we are delta'ing from
	*to = *from;

	to->number = bits & 511;
	bits &= ~511;

	if (bits & U_MOREBITS)
	{	// read in the low order bits
		i = MSG_ReadByte ();
		bits |= i;
	}

	// count the bits for net profiling
	for (i=0 ; i<16 ; i++)
		if (bits&(1<<i))
			bitcounts[i]++;

	to->flags = bits;
	
	if (bits & U_MODEL)
		to->modelindex = MSG_ReadByte ();
		
	if (bits & U_FRAME)
		to->frame = MSG_ReadByte ();

	if (bits & U_COLORMAP)
		to->colormap = MSG_ReadByte();

	if (bits & U_SKIN)
		to->skinnum = MSG_ReadByte();

	if (bits & U_EFFECTS)
		to->effects = MSG_ReadByte();

	if (bits & U_ORIGIN1)
		to->s_origin[0] = MSG_ReadShort ();
		
	if (bits & U_ANGLE1)
		to->s_angles[0] = MSG_ReadByte ();

	if (bits & U_ORIGIN2)
		to->s_origin[1] = MSG_ReadShort ();
		
	if (bits & U_ANGLE2)
		to->s_angles[1] = MSG_ReadByte ();

	if (bits & U_ORIGIN3)
		to->s_origin[2] = MSG_ReadShort ();
		
	if (bits & U_ANGLE3)
		to->s_angles[2] = MSG_ReadByte ();

	if (bits & U_SOLID)
	{
		// FIXME
		// oldman: is this not used?
		// to->solid = MSG_ReadShort ();
		// Tonik: no, it is not used (alas!)
	}
}


/*
=================
FlushEntityPacket
=================
*/
void FlushEntityPacket (void)
{
	int			word;
	entity_state_t	olde, newe;

	Com_DPrintf ("FlushEntityPacket\n");

	memset (&olde, 0, sizeof(olde));

	cl.delta_sequence = 0;

	// read it all, but ignore it
	while (1)
	{
		word = (unsigned short)MSG_ReadShort ();
		if (msg_badread)
		{	// something didn't parse right...
			Host_Error ("msg_badread in packetentities");
			return;
		}

		if (!word)
			break;	// done

		CL_ParseDelta (&olde, &newe, word);
	}
}

entity_state_t *CL_GetBaseline (int number)
{
	return &cl_entities[number].baseline;
}

// bump lastframe and copy current state to previous
static void UpdateEntities (void)
{
	int		i;
	packet_entities_t *pack;
	entity_state_t *ent;
	centity_t	*cent;

#ifndef MVDPLAY
	assert (cl.validsequence);
#endif

	pack = &cl.frames[cl.validsequence & UPDATE_MASK].packet_entities;

	for (i = 0; i < pack->num_entities; i++) {
		ent = &pack->entities[i];
		cent = &cl_entities[ent->number];

		cent->prevframe = cent->lastframe;
		cent->lastframe = cl_entframecount;

		if (cent->prevframe == cl_entframecount - 1) {
			// move along, move along
			cent->previous = cent->current;
		} else {
			// not in previous message
			cent->previous = *ent;
			MSG_UnpackOrigin (ent->s_origin, cent->trail_origin);
		}

		cent->current = *ent;
	}
}

/*
==================
CL_ParsePacketEntities

An svc_packetentities has just been parsed, deal with the
rest of the data stream.
==================
*/
void CL_ParsePacketEntities (qbool delta)
{
	int			oldpacket, newpacket;
	packet_entities_t	*oldp, *newp, dummy;
	int			oldindex, newindex;
	int			word, newnum, oldnum;
	qbool		full;
	byte		from;
	entity_state_t newents[BIG_MAX_PACKET_ENTITIES];
#ifdef MVDPLAY
	int maxents = cls.mvdplayback ? BIG_MAX_PACKET_ENTITIES	: MAX_PACKET_ENTITIES;
#else
	int maxents = MAX_PACKET_ENTITIES;
#endif

	newpacket = cls.netchan.incoming_sequence&UPDATE_MASK;
	newp = &cl.frames[newpacket].packet_entities;
	cl.frames[newpacket].valid = false;	// will set to true after we parse everything

	if (delta)
	{
		from = MSG_ReadByte ();

		oldpacket = cl.frames[newpacket].delta_sequence;

#ifdef MVDPLAY
		if (cls.mvdplayback)
			from = oldpacket = (cls.netchan.incoming_sequence-1);
#endif

		if (cls.netchan.outgoing_sequence - cls.netchan.incoming_sequence >= UPDATE_BACKUP-1)
		{	// there are no valid frames left, so drop it
			FlushEntityPacket ();
			cl.validsequence = 0;
			return;
		}

		if ( (from&UPDATE_MASK) != (oldpacket&UPDATE_MASK) ) {
			Com_DPrintf ("WARNING: from mismatch\n");
			FlushEntityPacket ();
			cl.validsequence = 0;
			return;
		}

		if (cls.netchan.outgoing_sequence - oldpacket >= UPDATE_BACKUP-1)
		{	// we can't use this, it is too old
			FlushEntityPacket ();
			// don't clear cl.validsequence, so that frames can
			// still be rendered; it is possible that a fresh packet will
			// be received before (outgoing_sequence - incoming_sequence)
			// exceeds UPDATE_BACKUP-1
			return;
		}

		oldp = &cl.frames[oldpacket&UPDATE_MASK].packet_entities;
		full = false;
	}
	else
	{	// this is a full update that we can start delta compressing from now
		oldp = &dummy;
		dummy.num_entities = 0;
		dummy.entities = NULL;
		full = true;
	}

	cl.oldvalidsequence = cl.validsequence;
	cl.validsequence = cls.netchan.incoming_sequence;
	cl.delta_sequence = cl.validsequence;

	oldindex = 0;
	newindex = 0;
	newp->num_entities = 0;

	while (1)
	{
		word = (unsigned short)MSG_ReadShort ();
		if (msg_badread)
		{	// something didn't parse right...
			Host_Error ("msg_badread in packetentities");
			return;
		}

		if (!word)
		{
			while (oldindex < oldp->num_entities)
			{	// copy all the rest of the entities from the old packet
				if (newindex >= maxents)
					Host_Error ("CL_ParsePacketEntities: newindex == MAX_PACKET_ENTITIES");
				newents[newindex] = oldp->entities[oldindex];
				newindex++;
				oldindex++;
			}
			break;
		}
		newnum = word&511;
		oldnum = oldindex >= oldp->num_entities ? 9999 : oldp->entities[oldindex].number;

		while (newnum > oldnum)
		{
			if (full)
			{
				Com_Printf ("WARNING: oldcopy on full update");
				FlushEntityPacket ();
				cl.validsequence = 0;	// can't render a frame
				return;
			}

			// copy one of the old entities over to the new packet unchanged
			if (newindex >= maxents)
				Host_Error ("CL_ParsePacketEntities: newindex == MAX_PACKET_ENTITIES");
			newents[newindex] = oldp->entities[oldindex];
			newindex++;
			oldindex++;
			oldnum = oldindex >= oldp->num_entities ? 9999 : oldp->entities[oldindex].number;
		}

		if (newnum < oldnum)
		{	// new from baseline

			if (word & U_REMOVE)
			{
				if (full)
				{
					Com_Printf ("WARNING: U_REMOVE on full update\n");
					FlushEntityPacket ();
					cl.validsequence = 0;	// can't render a frame
					return;
				}
				continue;
			}
			if (newindex >= maxents)
				Host_Error ("CL_ParsePacketEntities: newindex == MAX_PACKET_ENTITIES");
			CL_ParseDelta (&cl_entities[newnum].baseline, &newents[newindex], word);
			newindex++;
			continue;
		}

		if (newnum == oldnum)
		{	// delta from previous
			if (full)
			{
				cl.validsequence = 0;
				cl.delta_sequence = 0;
				Com_Printf ("WARNING: delta on full update");
			}
			if (word & U_REMOVE)
			{
				oldindex++;
				continue;
			}

			CL_ParseDelta (&oldp->entities[oldindex], &newents[newindex], word);

			newindex++;
			oldindex++;
		}
	}

	newp->num_entities = newindex;
	Q_free (newp->entities);
	newp->entities = Q_malloc (sizeof(entity_state_t) * newp->num_entities);
	memcpy (newp->entities, newents, sizeof(entity_state_t) * newp->num_entities);

	cl.frames[newpacket].valid = true;

	cl_entframecount++;
	UpdateEntities ();

	if (cls.demorecording) {
		// write uncompressed packetentities to the demo
		MSG_EmitPacketEntities (NULL, -1, newp, &cls.demomessage, CL_GetBaseline);
		cls.demomessage_skipwrite = true;
	}

	// we can now render a frame
	if (cls.state == ca_onserver)
		CL_Spawn();
}


extern int	cl_playerindex; 
extern int	cl_rocketindex, cl_grenadeindex;

/*
===============
CL_LinkPacketEntities

===============
*/
void CL_LinkPacketEntities (void)
{
	entity_t			ent;
	centity_t			*cent;
	packet_entities_t	*pack;
	entity_state_t		*state;
	float				f;
	struct model_s		*model;
	int					modelflags;
	vec3_t				cur_origin;
	vec3_t				old_origin;
	float				autorotate, flicker;
	int					i;
	int					pnum;
	extern cvar_t		cl_nolerp;

	pack = &cl.frames[cl.validsequence&UPDATE_MASK].packet_entities;

	autorotate = anglemod (100*cl.time);

#ifdef MVDPLAY
	if (cls.mvdplayback) {
		f = bound(0, (cls.demotime - cls.mvd_oldtime) / (cls.mvd_newtime - cls.mvd_oldtime), 1);
	}
	else
#endif
	if (cl_nolerp.value)
		f = 1;
	else
	{
		float t, simtime;

		simtime = cls.realtime - cl.entlatency;
		if (simtime > cl.frames[cl.validsequence&UPDATE_MASK].receivedtime) {
			cl.entlatency = cls.realtime - cl.frames[cl.validsequence&UPDATE_MASK].receivedtime;
		} else if (simtime < cl.frames[cl.oldvalidsequence&UPDATE_MASK].receivedtime) {
			cl.entlatency = cls.realtime - cl.frames[cl.oldvalidsequence&UPDATE_MASK].receivedtime;
		} else {
			// drift towards ideal latency
		}

		t = cl.frames[cl.validsequence&UPDATE_MASK].receivedtime -
			cl.frames[cl.oldvalidsequence&UPDATE_MASK].receivedtime;
		if (t)
			f = (cls.realtime - cl.entlatency - cl.frames[cl.oldvalidsequence&UPDATE_MASK].receivedtime) / t;
		else
			f = 1;
		f = bound (0, f, 1);
	}

	for (pnum=0 ; pnum<pack->num_entities ; pnum++)
	{
		state = &pack->entities[pnum];
		cent = &cl_entities[state->number];

#ifdef MVDPLAY
		if (!cls.mvdplayback)
#endif
		{ assert(cent->lastframe == cl_entframecount);
		assert(!memcmp(state, &cent->current, sizeof(*state))); }

		MSG_UnpackOrigin (state->s_origin, cur_origin);

		// control powerup glow for bots
		if (state->modelindex != cl_playerindex || r_powerupglow.value)
		{
			flicker = r_lightflicker.value ? (rand() & 31) : 10;
			// spawn light flashes, even ones coming from invisible objects
			if ((state->effects & (EF_BLUE | EF_RED)) == (EF_BLUE | EF_RED))
				V_AddDlight (state->number, cur_origin, 200 + flicker, 0, lt_redblue);
			else if (state->effects & EF_BLUE)
				V_AddDlight (state->number, cur_origin, 200 + flicker, 0, lt_blue);
			else if (state->effects & EF_RED)
				V_AddDlight (state->number, cur_origin, 200 + flicker, 0, lt_red);
			else if (state->effects & EF_BRIGHTLIGHT) {
				vec3_t	tmp;
				VectorCopy (cur_origin, tmp);
				tmp[2] += 16;
				V_AddDlight (state->number, tmp, 400 + flicker, 0, lt_default);
			} else if (state->effects & EF_DIMLIGHT)
				V_AddDlight (state->number, cur_origin, 200 + flicker, 0, lt_default);
		}

		if (state->effects & EF_BRIGHTFIELD)
			CL_EntityParticles (cur_origin);

		// if set to invisible, skip
		if (!state->modelindex)
			continue;

		if (state->modelindex == cl_playerindex) {
			int f = state->frame;
			if (cl_deadbodyfilter.value == 2 && f >= 41 && f <= 102)
				continue;
			if (cl_deadbodyfilter.value && (f==49 || f==60 || f==69 || f==84 || f==93 || f==102))
				continue;
		}

		memset (&ent, 0, sizeof(ent));

		if (cl.modelinfos[state->modelindex] == mi_gib) {
			if (!cent->gib_start)
				cent->gib_start = cl.time;
			if (cl_gibfilter.value == 2) {
				if (cent->gib_start && cl.time - cent->gib_start > cl_gibtime.value)
					continue;
				// start to fade away 1 second before cl_gibtime is up
				if (cent->gib_start && cl.time - cent->gib_start > cl_gibtime.value - 1) {
					ent.alpha = cl_gibtime.value - (cl.time - cent->gib_start);
					ent.renderfx |= RF_TRANSLUCENT;
				}
			} else if (cl_gibfilter.value)
				continue;
		}
		else
			cent->gib_start = 0;

		ent.model = model = cl.model_precache[state->modelindex];
		if (!model)
			Host_Error ("CL_LinkPacketEntities: bad modelindex");

		if (cl_r2g.value && cl_grenadeindex != -1)
			if (state->modelindex == cl_rocketindex)
				ent.model = cl.model_precache[cl_grenadeindex];

		// set colormap
		if (state->colormap >= 1 && state->colormap <= MAX_CLIENTS
			&& state->modelindex == cl_playerindex
		)
			ent.colormap = state->colormap;
		else
			ent.colormap = 0;

		// set skin
		ent.skinnum = state->skinnum;
		
		// set frame
		ent.frame = state->frame;

		// decide whether to lerp frames
		if (cent->prevframe != cl_entframecount - 1) {
			// not in previous message
			cent->framelerp_start = 0;
		}
		else if (cent->current.frame != cent->previous.frame) {
//			Com_Printf ("%i -> %i\n", cent->current.frame, cent->previous.frame);
			cent->framelerp_start = cl.time;
			cent->oldframe = cent->previous.frame;
		}
		if (cent->framelerp_start) {
			ent.oldframe = cent->oldframe;
			ent.backlerp = 1 - (cl.time - cent->framelerp_start)*10;
			ent.backlerp = bound (0, ent.backlerp, 1);
//			if (ent.backlerp < 1)
//				Com_Printf ("backlerp %f\n", ent.backlerp);
		}

		modelflags = R_ModelFlags (model);

		//
		// calculate angles
		//
		if (modelflags & MF_ROTATE)
		{	// rotate binary objects locally
			ent.angles[0] = 0;
			ent.angles[1] = autorotate;
			ent.angles[2] = 0;
		}
		else if (cl.modelinfos[state->modelindex] == mi_monster && cl_lerp_monsters.value)
		{
			// monster angles interpolation
			if (cent->prevframe != cl_entframecount - 1) {
				// not in previous message
				cent->monsterlerp_angles_start = 0;
			}
			else {
				for (i=0 ; i<3 ; i++)
					if (cent->current.s_angles[i] != cent->previous.s_angles[i])
						break;
				if (i != 3) {
					cent->monsterlerp_angles_start = cl.time;
					MSG_UnpackAngles (cent->previous.s_angles, cent->monsterlerp_angles);
				}
			}
			if (cent->monsterlerp_angles_start) {
				float backlerp;
				vec3_t	cur;
				backlerp = 1 - (cl.time - cent->monsterlerp_angles_start)*10;
				backlerp = bound (0, backlerp, 1);
				MSG_UnpackAngles (cent->current.s_angles, cur);
				LerpAngles (cur, cent->monsterlerp_angles, backlerp, ent.angles);
			} else {
				MSG_UnpackAngles (cent->current.s_angles, ent.angles);
			}
		}
		else
		{
			// generic angles interpolation
			vec3_t	old, cur;
			MSG_UnpackAngles (cent->previous.s_angles, old);
			MSG_UnpackAngles (cent->current.s_angles, cur);
			LerpAngles (old, cur, f, ent.angles);
		}

		//
		// calculate origin
		//
		if (cl.modelinfos[state->modelindex] == mi_monster && cl_lerp_monsters.value) {
			// monster origin interpolation
			if (cent->prevframe != cl_entframecount - 1) {
				// not in previous message
				cent->monsterlerp_start = 0;
			}
			else {
				for (i=0 ; i<3 ; i++)
					if (cent->current.s_origin[i] != cent->previous.s_origin[i])
						break;
				if (i != 3) {
					cent->monsterlerp_start = cl.time;
					MSG_UnpackOrigin (cent->previous.s_origin, cent->monsterlerp_origin);
				}
			}
			if (cent->monsterlerp_start) {
				float backlerp;
				backlerp = 1 - (cl.time - cent->monsterlerp_start)*10;
				backlerp = bound (0, backlerp, 1);
				LerpVector (cur_origin, cent->monsterlerp_origin, backlerp, ent.origin);
			} else {
				VectorCopy (cur_origin, ent.origin);
			}
		}
		else {
			// generic origin interpolation
			for (i=0 ; i<3 ; i++)
				ent.origin[i] = cent->previous.s_origin[i] * 0.125 + 
					f * (cur_origin[i] - cent->previous.s_origin[i] * 0.125);
		}

		// add automatic particle trails
		if (modelflags & ~MF_ROTATE)
		{
			VectorCopy (cent->trail_origin, old_origin);

			for (i=0 ; i<3 ; i++)
				if (abs(old_origin[i] - ent.origin[i]) > 128)
				{	// no trail if too far
					VectorCopy (ent.origin, old_origin);
					break;
				}

			if (modelflags & MF_ROCKET)
			{
				if (r_rockettrail.value) {
					if (r_rockettrail.value == 2)
						CL_GrenadeTrail (old_origin, ent.origin, cent->trail_origin);
					else
						CL_RocketTrail (old_origin, ent.origin, cent->trail_origin);
				} else
					VectorCopy (ent.origin, cent->trail_origin);

				if (r_rocketlight.value)
					CL_NewDlight (state->number, ent.origin, 200, 0.1, lt_rocket);
			}
			else if (modelflags & MF_GRENADE && r_grenadetrail.value)
				CL_GrenadeTrail (old_origin, ent.origin, cent->trail_origin);
			else if (modelflags & MF_GIB)
				CL_BloodTrail (old_origin, ent.origin, cent->trail_origin);
			else if (modelflags & MF_ZOMGIB)
				CL_SlightBloodTrail (old_origin, ent.origin, cent->trail_origin);
			else if (modelflags & MF_TRACER)
				CL_TracerTrail (old_origin, ent.origin, cent->trail_origin, 52);
			else if (modelflags & MF_TRACER2)
				CL_TracerTrail (old_origin, ent.origin, cent->trail_origin, 230);
			else if (modelflags & MF_TRACER3)
				CL_VoorTrail (old_origin, ent.origin, cent->trail_origin);
		}

		V_AddEntity (&ent);
	}
}


/*
=========================================================================

NAIL PARSING / LINKING

=========================================================================
*/

#define	MAX_NAILS	32

typedef struct {
	byte	number;
	vec3_t	origin;
	vec3_t	angles;
} nail_t;

static nail_t			cl_nails[MAX_NAILS];

#ifdef MVDPLAY
typedef struct {
	int		newindex;
	int		sequence[2];
	vec3_t	origin[2];
} lerped_nail_t;

static lerped_nail_t	cl_lerped_nails[256];
#endif


void CL_ClearNails (void)
{
#ifdef MVDPLAY
	memset(cl_nails, 0, sizeof(cl_nails));
	memset(cl_lerped_nails, 0, sizeof(cl_lerped_nails));
#endif
}

#ifdef MVDPLAY
void CL_ParseNails (qbool tagged)
#else
void CL_ParsNails (void)
#endif
{
	byte bits[6];
	int i, c, j, num = 0;
	nail_t *pr;

	c = MSG_ReadByte();

	for (i = 0; i < c && cl.num_nails < MAX_NAILS; i++) {
#ifdef MVDPLAY
		num = tagged ? MSG_ReadByte() : 0;
#endif

		for (j = 0; j < 6; j++)
			bits[j] = MSG_ReadByte();

		pr = &cl_nails[cl.num_nails++];

		pr->origin[0] = (( bits[0] + ((bits[1] & 15) << 8)) << 1) - 4096;
		pr->origin[1] = (((bits[1] >> 4) + (bits[2] << 4)) << 1) - 4096;
		pr->origin[2] = ((bits[3] + ((bits[4] & 15) << 8)) << 1) - 4096;
		pr->angles[0] = 360 * (bits[4] >> 4) / 16;
		pr->angles[1] = 360 * bits[5] / 256;

#ifdef MVDPLAY
		if ((pr->number = num)) {
			int newindex = cl_lerped_nails[num].newindex = !cl_lerped_nails[num].newindex;
			cl_lerped_nails[num].sequence[newindex] = cl.validsequence;
			VectorCopy(pr->origin, cl_lerped_nails[num].origin[newindex]);
		}
#endif
	}
}

static void CL_LinkNails (void)
{
	int i;
	entity_t ent;
	nail_t *pr;
#ifdef MVDPLAY
	float f;
#endif

	memset(&ent, 0, sizeof(entity_t));
	ent.model = cl.model_precache[cl_spikeindex];
	ent.colormap = 0;

#ifdef MVDPLAY
	f = bound(0, (cls.demotime - cls.mvd_oldtime) / (cls.mvd_newtime - cls.mvd_oldtime), 1);
#endif

	for (i = 0, pr = cl_nails; i < cl.num_nails; i++, pr++)	{
#ifdef MVDPLAY
		int num;
		if ((num = cl_nails[i].number)) {
			lerped_nail_t *lpr = &cl_lerped_nails[num];
			if (cl.oldparsecount && lpr->sequence[!lpr->newindex] == cl.oldparsecount) {
				LerpVector(lpr->origin[!lpr->newindex], lpr->origin[lpr->newindex], f, ent.origin);
				goto done_origin;
			}
		}
#endif
		VectorCopy(pr->origin, ent.origin);
		goto done_origin;		// suppress warning
done_origin:
		VectorCopy(pr->angles, ent.angles);
		V_AddEntity(&ent);
	}
}

//========================================

#ifdef MVDPLAY

int TranslateFlags(int src)
{
	int dst = 0;

	if (src & DF_EFFECTS)
		dst |= PF_EFFECTS;
	if (src & DF_SKINNUM)
		dst |= PF_SKINNUM;
	if (src & DF_DEAD)
		dst |= PF_DEAD;
	if (src & DF_GIB)
		dst |= PF_GIB;
	if (src & DF_WEAPONFRAME)
		dst |= PF_WEAPONFRAME;
	if (src & DF_MODEL)
		dst |= PF_MODEL;

	return dst;
}


static void MVD_ParsePlayerState (void)
{
	int			flags;
	player_info_t	*info;
	player_state_t	*state, *oldstate;
	static player_state_t dummy;	// all zeroes
	int			num;
	int			i;

	num = MSG_ReadByte ();
	if (num >= MAX_CLIENTS)
		Host_Error ("CL_ParsePlayerState: bad num");

	info = &cl.players[num];

	if (cls.mvd_findtarget && info->stats[STAT_HEALTH] != 0)
	{
		Cam_Lock (num);
		cls.mvd_findtarget = false;
	}

	state = &cl.frames[cl.parsecount & UPDATE_MASK].playerstate[num];

	if (info->prevcount > cl.parsecount || !cl.parsecount) {
		oldstate = &dummy;
	} else {
		if (cl.parsecount - info->prevcount >= UPDATE_BACKUP-1)
			oldstate = &dummy;
		else 
			oldstate = &cl.frames[info->prevcount&UPDATE_MASK].playerstate[num];
	}

	info->prevcount = cl.parsecount;

	memcpy(state, oldstate, sizeof(player_state_t));

	flags = MSG_ReadShort ();
	state->flags = TranslateFlags(flags);

	state->messagenum = cl.parsecount;
	state->command.msec = 0;

	state->frame = MSG_ReadByte ();

	state->state_time = cls.realtime;
	state->command.msec = 0;

	for (i=0; i <3; i++)
		if (flags & (DF_ORIGIN << i))
			state->origin[i] = MSG_ReadCoord ();

	for (i=0; i <3; i++)
		if (flags & (DF_ANGLES << i))
			state->command.angles[i] = MSG_ReadAngle16 ();


	if (flags & DF_MODEL)
		state->modelindex = MSG_ReadByte ();
		
	if (flags & DF_SKINNUM)
		state->skinnum = MSG_ReadByte ();
		
	if (flags & DF_EFFECTS)
		state->effects = MSG_ReadByte ();
	
	if (flags & DF_WEAPONFRAME)
		state->weaponframe = MSG_ReadByte ();
		
	VectorCopy (state->command.angles, state->viewangles);
}

#endif	// MVDPLAY


/*
===================
CL_ParsePlayerState
===================
*/
void CL_ParsePlayerState (void)
{
	int			msec;
	int			flags;
	player_info_t	*info;
	player_state_t	*state;
	int			num;
	int			i;

#ifdef MVDPLAY
	if (cls.mvdplayback)
	{
		MVD_ParsePlayerState ();
		return;
	}
#endif

	num = MSG_ReadByte ();
	if (num >= MAX_CLIENTS)
		Host_Error ("CL_ParsePlayerState: bad num");

	info = &cl.players[num];

	state = &cl.frames[cl.parsecount & UPDATE_MASK].playerstate[num];

	flags = state->flags = MSG_ReadShort ();

	state->messagenum = cl.parsecount;
	state->origin[0] = MSG_ReadCoord ();
	state->origin[1] = MSG_ReadCoord ();
	state->origin[2] = MSG_ReadCoord ();

	state->frame = MSG_ReadByte ();

	// the other player's last move was likely some time
	// before the packet was sent out, so accurately track
	// the exact time it was valid at
	if (flags & PF_MSEC)
	{
		msec = MSG_ReadByte ();
		state->state_time = cl.frames[cl.parsecount & UPDATE_MASK].senttime - msec*0.001;
	}
	else
		state->state_time = cl.frames[cl.parsecount & UPDATE_MASK].senttime;

	if (flags & PF_COMMAND)
		MSG_ReadDeltaUsercmd (&nullcmd, &state->command, cl.protocol);

#ifdef VWEP_TEST
	if (cl.z_ext & Z_EXT_VWEP)
		state->vw_index = state->command.impulse;
	else
		state->vw_index = 0;
#endif

	for (i=0 ; i<3 ; i++)
	{
		if (flags & (PF_VELOCITY1<<i) )
			state->velocity[i] = MSG_ReadShort();
		else
			state->velocity[i] = 0;
	}
	if (flags & PF_MODEL)
		state->modelindex = MSG_ReadByte ();
	else
		state->modelindex = cl_playerindex;

	if (flags & PF_SKINNUM)
		state->skinnum = MSG_ReadByte ();
	else
		state->skinnum = 0;

	if (flags & PF_EFFECTS)
		state->effects = MSG_ReadByte ();
	else
		state->effects = 0;

	if (flags & PF_WEAPONFRAME)
		state->weaponframe = MSG_ReadByte ();
	else
		state->weaponframe = 0;

	if (cl.z_ext & Z_EXT_PM_TYPE)
	{
		int pm_code = (flags >> PF_PMC_SHIFT) & PF_PMC_MASK;

		if (pm_code == PMC_NORMAL || pm_code == PMC_NORMAL_JUMP_HELD) {
			if (flags & PF_DEAD)
				state->pm_type = PM_DEAD;
			else
			{
				state->pm_type = PM_NORMAL;
				state->jump_held = (pm_code == PMC_NORMAL_JUMP_HELD);
			}
		}
		else if (pm_code == PMC_OLD_SPECTATOR)
			state->pm_type = PM_OLD_SPECTATOR;
		else {
			if (cl.z_ext & Z_EXT_PM_TYPE_NEW) {
				if (pm_code == PMC_SPECTATOR)
					state->pm_type = PM_SPECTATOR;
				else if (pm_code == PMC_FLY)
					state->pm_type = PM_FLY;
				else if (pm_code == PMC_NONE)
					state->pm_type = PM_NONE;
				else if (pm_code == PMC_FREEZE)
					state->pm_type = PM_FREEZE;
				else {
					// future extension?
					goto guess_pm_type;
				}
			}
			else {
				// future extension?
				goto guess_pm_type;
			}
		}
	}
	else
	{
guess_pm_type:
		if (cl.players[num].spectator)
			state->pm_type = PM_OLD_SPECTATOR;
		else if (flags & PF_DEAD)
			state->pm_type = PM_DEAD;
		else
			state->pm_type = PM_NORMAL;
	}

	if (cl.z_ext & Z_EXT_PF_ONGROUND)
		state->onground = (flags & PF_ONGROUND) != 0;
	else
		state->onground = false;

	VectorCopy (state->command.angles, state->viewangles);
}


/*
================
CL_AddFlagModels

Called when the CTF flags are set
================
*/
void CL_AddFlagModels (entity_t *ent, int team)
{
	int		i;
	float	f;
	vec3_t	v_forward, v_right;
	entity_t	newent;

	if (cl_flagindex == -1)
		return;

	f = 14;
	if (ent->frame >= 29 && ent->frame <= 40) {
		if (ent->frame >= 29 && ent->frame <= 34) { //axpain
			if      (ent->frame == 29) f = f + 2; 
			else if (ent->frame == 30) f = f + 8;
			else if (ent->frame == 31) f = f + 12;
			else if (ent->frame == 32) f = f + 11;
			else if (ent->frame == 33) f = f + 10;
			else if (ent->frame == 34) f = f + 4;
		} else if (ent->frame >= 35 && ent->frame <= 40) { // pain
			if      (ent->frame == 35) f = f + 2; 
			else if (ent->frame == 36) f = f + 10;
			else if (ent->frame == 37) f = f + 10;
			else if (ent->frame == 38) f = f + 8;
			else if (ent->frame == 39) f = f + 4;
			else if (ent->frame == 40) f = f + 2;
		}
	} else if (ent->frame >= 103 && ent->frame <= 118) {
		if      (ent->frame >= 103 && ent->frame <= 104) f = f + 6;  //nailattack
		else if (ent->frame >= 105 && ent->frame <= 106) f = f + 6;  //light 
		else if (ent->frame >= 107 && ent->frame <= 112) f = f + 7;  //rocketattack
		else if (ent->frame >= 112 && ent->frame <= 118) f = f + 7;  //shotattack
	}

	memset (&newent, 0, sizeof(entity_t));

	newent.model = cl.model_precache[cl_flagindex];
	newent.skinnum = team;
	newent.colormap = 0;

	AngleVectors (ent->angles, v_forward, v_right, NULL);
	v_forward[2] = -v_forward[2]; // reverse z component
	for (i=0 ; i<3 ; i++)
		newent.origin[i] = ent->origin[i] - f*v_forward[i] + 22*v_right[i];
	newent.origin[2] -= 16;

	VectorCopy (ent->angles, newent.angles);
	newent.angles[2] -= 45;

	V_AddEntity (&newent);
}


/*
================
CL_AddVWepModel
================
*/
#ifdef VWEP_TEST
static qbool CL_AddVWepModel (entity_t *ent, int vw_index, int vw_frame)
{
	entity_t	newent;

	if ((unsigned)vw_index >= MAX_VWEP_MODELS)
		return false;

	if (!strcmp(cl.vw_model_name[vw_index], "-"))
		return true;	// empty vwep model

	if (!cl.vw_model_precache[vw_index])
		return false;	// vwep model not present - draw default player.mdl

	// build the weapon entity
	memset (&newent, 0, sizeof(entity_t));
	VectorCopy (ent->origin, newent.origin);
	VectorCopy (ent->angles, newent.angles);
	newent.model = cl.vw_model_precache[vw_index];
	newent.frame = vw_frame;
	newent.skinnum = 0;
	newent.colormap = 0;
	newent.renderfx = RF_PLAYERMODEL;	// not really, but use same lighting rules

	V_AddEntity (&newent);
	return true;
}
#endif


/*
=============
CL_LinkPlayers

Create visible entities in the correct position
for all current players
=============
*/
void CL_LinkPlayers (void)
{
	int				j;
	player_info_t	*info;
	player_state_t	*state;
	player_state_t	exact;
	double			playertime;
	entity_t		ent;
	centity_t		*cent;
	int				msec;
	frame_t			*frame;
	int				oldphysent;
	vec3_t			org;
	float			flicker;

	playertime = cls.realtime - cls.latency + 0.02;
	if (playertime > cls.realtime)
		playertime = cls.realtime;

	frame = &cl.frames[cl.parsecount&UPDATE_MASK];

	memset (&ent, 0, sizeof(entity_t));

	for (j=0, info=cl.players, state=frame->playerstate ; j < MAX_CLIENTS 
		; j++, info++, state++)
	{
		if (state->messagenum != cl.parsecount)
			continue;	// not present this frame

		// spawn light flashes, even ones coming from invisible objects
		if (r_powerupglow.value && !(r_powerupglow.value == 2 && j == Cam_PlayerNum()))
		{
			if (j == Cam_PlayerNum()) {
				VectorCopy (cl.simorg, org);
			} else
				VectorCopy (state->origin, org);

			flicker = r_lightflicker.value ? (rand() & 31) : 10;

			if ((state->effects & (EF_BLUE | EF_RED)) == (EF_BLUE | EF_RED))
				V_AddDlight (j+1, org, 200 + flicker, 0, lt_redblue);
			else if (state->effects & EF_BLUE)
				V_AddDlight (j+1, org, 200 + flicker, 0, lt_blue);
			else if (state->effects & EF_RED)
				V_AddDlight (j+1, org, 200 + flicker, 0, lt_red);
			else if (state->effects & EF_BRIGHTLIGHT) {
				vec3_t	tmp;
				VectorCopy (org, tmp);
				tmp[2] += 16;
				V_AddDlight (j+1, org, 200 + flicker, 0, lt_default);
			}
			else if (state->effects & EF_DIMLIGHT)
				V_AddDlight (j+1, org, 200 + flicker, 0, lt_default);
		}

		if (!state->modelindex)
			continue;

		cent = &cl_entities[j+1];
		cent->previous = cent->current;
		MSG_PackOrigin (state->origin, cent->current.s_origin);

		// the player object never gets added
		if (j == cl.playernum)
			continue;

		if (state->modelindex == cl_playerindex) {
			int f = state->frame;
			if (cl_deadbodyfilter.value == 2 && f >= 41 && f <= 102)
				continue;
			if (cl_deadbodyfilter.value && (f==49 || f==60 || f==69 || f==84 || f==93 || f==102))
				continue;
		}
		
		if (!Cam_DrawPlayer(j))
			continue;

		ent.model = cl.model_precache[state->modelindex];
		if (!ent.model)
			Host_Error ("CL_LinkPlayers: bad modelindex");
		ent.skinnum = state->skinnum;
		ent.frame = state->frame;
		ent.colormap = j + 1;

		if (state->frame != cent->current.frame) {
			cent->framelerp_start = cl.time;
			cent->oldframe = cent->current.frame;
			cent->current.frame = state->frame;
		}
		if (cent->framelerp_start) {
			ent.oldframe = cent->oldframe;
			ent.backlerp = 1 - (cl.time - cent->framelerp_start)*10;
		}

		//
		// angles
		//
		ent.angles[PITCH] = -state->viewangles[PITCH]/3;
		ent.angles[YAW] = state->viewangles[YAW];
		ent.angles[ROLL] = 0;
		ent.angles[ROLL] = V_CalcRoll (ent.angles, state->velocity)*4;

		// only predict half the move to minimize overruns
		msec = 1000 * (playertime - state->state_time);
		if (msec <= 0 || !cl_predict_players.value)
		{
			VectorCopy (state->origin, ent.origin);
		}
		else
		{
			// predict players movement
			if (msec > 255)
				msec = 255;
			state->command.msec = msec;

			oldphysent = cl.pmove.numphysent;
			CL_SetSolidPlayers (j);
			CL_PredictUsercmd (state, &exact, &state->command);
			cl.pmove.numphysent = oldphysent;
			VectorCopy (exact.origin, ent.origin);
		}

		if (state->effects & EF_FLAG1)
			CL_AddFlagModels (&ent, 0);
		else if (state->effects & EF_FLAG2)
			CL_AddFlagModels (&ent, 1);

#ifdef VWEP_TEST
		if (cl.vwep_enabled && state->vw_index) {
			qbool vwep;
			vwep = CL_AddVWepModel (&ent, state->vw_index, state->frame);
			if (vwep) {
				if (strcmp(cl.vw_model_name[0], "-")) {
					ent.model = cl.vw_model_precache[0];
					ent.renderfx = RF_PLAYERMODEL;
					V_AddEntity (&ent);
				} else {
					// server said don't add vwep player model
				}
			}
			else
				V_AddEntity (&ent);
		}
		else
#endif
			V_AddEntity (&ent);
	}
}

//======================================================================

/*
===============
CL_SetSolid

Builds all the pmove physents for the current frame
===============
*/
void CL_SetSolidEntities (void)
{
	int		i;
	frame_t	*frame;
	packet_entities_t	*pak;
	entity_state_t		*state;

	cl.pmove.physents[0].model = cl.clipmodels[1];
	VectorClear (cl.pmove.physents[0].origin);
	cl.pmove.physents[0].info = 0;
	cl.pmove.numphysent = 1;

	frame = &cl.frames[cl.parsecount & UPDATE_MASK];
	pak = &frame->packet_entities;

	for (i=0 ; i<pak->num_entities ; i++) {
		state = &pak->entities[i];
		if (!state->modelindex)
			continue;
		if (cl.clipmodels[state->modelindex]) {
			if (cl.pmove.numphysent == MAX_PHYSENTS)
				break;
			cl.pmove.physents[cl.pmove.numphysent].model = cl.clipmodels[state->modelindex];
			MSG_UnpackOrigin (state->s_origin, cl.pmove.physents[cl.pmove.numphysent].origin);
			cl.pmove.numphysent++;
		}
	}

}

#ifdef MVDPLAY

#define ISDEAD(i) ( (i) >=41 && (i) <=102 )

void MVD_InitInterpolation (void)
{
    int		i,j;
    struct predicted_player *pplayer;
    frame_t	*frame, *oldframe;
    player_state_t	*state, *oldstate;
    vec3_t	dist;

    if (!cl.validsequence)
        return;

    frame = &cl.frames[cl.parsecount&UPDATE_MASK];
    oldframe = &cl.frames[(cl.oldparsecount)&UPDATE_MASK];

    // clients
    for (i=0, pplayer = predicted_players, state=frame->playerstate, oldstate=oldframe->playerstate; 
            i < MAX_CLIENTS;
            i++, pplayer++, state++, oldstate++) {

        if (pplayer->predict)
        {
            VectorCopy(pplayer->oldo, oldstate->origin);
            VectorCopy(pplayer->olda, oldstate->command.angles);
        }

        pplayer->predict = false;

        if (cl.mvd_fixangle & 1 << i)
        {
            if (i == cam_curtarget) {
                VectorCopy(cl.viewangles, state->command.angles);
                VectorCopy(cl.viewangles, state->viewangles);
            }

            // no angle interpolation
            VectorCopy(state->command.angles, oldstate->command.angles);

            cl.mvd_fixangle &= ~(1 << i);
            //continue;
        }

        if (state->messagenum != cl.parsecount) {
            continue;	// not present this frame
        }

        if (oldstate->messagenum != cl.oldparsecount || !oldstate->messagenum) {
            continue;	// not present last frame
        }

        // we dont interpolate ourself if we are spectating
        if (i == cl.playernum) {
            if (cl.spectator)
                continue;
        }

        if (!ISDEAD(state->frame) && ISDEAD(oldstate->frame))
            continue;

        VectorSubtract(state->origin, oldstate->origin, dist);
        if (VectorLength(dist) > 150)
            continue;

        VectorCopy(state->origin, pplayer->oldo);
        VectorCopy(state->command.angles, pplayer->olda);

        pplayer->oldstate = oldstate;
        pplayer->predict = true;

        assert (cls.mvd_newtime > cls.mvd_oldtime);
        for (j = 0; j < 3; j++)
            pplayer->vel[j] = (state->origin[j] - oldstate->origin[j]) / (cls.mvd_newtime - cls.mvd_oldtime);
    }

}

void MVD_ClearPredict(void)
{
    memset(predicted_players, 0, sizeof(predicted_players));
}

void MVD_Interpolate(void)
{
	int i;
	float f;
	frame_t	*frame, *oldframe;
	entity_state_t *oldents;
	player_state_t *state, *oldstate;
	struct predicted_player *pplayer;
	static float old;

	if (old != cls.mvd_newtime) {
		old = cls.mvd_newtime;
		MVD_InitInterpolation ();
	}

	cls.netchan.outgoing_sequence = cl.parsecount + 1;

	if (!cl.validsequence)
		return;

	if (cls.mvd_newtime <= cls.mvd_oldtime)
		return;

	frame = &cl.frames[cl.parsecount & UPDATE_MASK];
	oldframe = &cl.frames[cl.oldparsecount & UPDATE_MASK];
	oldents = oldframe->packet_entities.entities;

//Com_Printf ("%f of %f\n", cls.demotime - cls.mvd_oldtime, cls.mvd_newtime - cls.mvd_oldtime);
	f = bound(0, (cls.demotime - cls.mvd_oldtime) / (cls.mvd_newtime - cls.mvd_oldtime), 1);

	// interpolate clients
	for (i = 0; i < MAX_CLIENTS; i++) {
		pplayer = &predicted_players[i];
		state = &frame->playerstate[i];
		oldstate = &oldframe->playerstate[i];

		if (pplayer->predict) {
			LerpAngles (oldstate->command.angles, pplayer->olda, f, state->viewangles);
			LerpVector (oldstate->origin, pplayer->oldo, f, state->origin);
			LerpVector (oldstate->velocity, pplayer->oldv, f, state->velocity);
		}
	}
}

#endif

/*
===
Calculate the new position of players, without other player clipping

We do this to set up real player prediction.
Players are predicted twice, first without clipping other players,
then with clipping against them.
This sets up the first phase.
===
*/
void CL_SetUpPlayerPrediction (qbool dopred)
{
	int				j;
	player_state_t	*state;
	player_state_t	exact;
	double			playertime;
	int				msec;
	frame_t			*frame;
	struct predicted_player *pplayer;

	playertime = cls.realtime - cls.latency + 0.02;
	if (playertime > cls.realtime)
		playertime = cls.realtime;

	frame = &cl.frames[cl.parsecount&UPDATE_MASK];

	for (j=0, pplayer = predicted_players, state=frame->playerstate; 
		j < MAX_CLIENTS;
		j++, pplayer++, state++) {

		pplayer->active = false;

		if (state->messagenum != cl.parsecount)
			continue;	// not present this frame

		if (!state->modelindex)
			continue;

		pplayer->active = true;
		pplayer->flags = state->flags;

		// note that the local player is special, since he moves locally
		// we use his last predicted postition
		if (j == cl.playernum) {
			VectorCopy(cl.frames[cls.netchan.outgoing_sequence&UPDATE_MASK].playerstate[cl.playernum].origin,
				pplayer->origin);
		} else {
			// only predict half the move to minimize overruns
			msec = 500*(playertime - state->state_time);
#ifdef MVDPLAY
			if (msec <= 0 || !cl_predict_players.value || !dopred || cls.mvdplayback)
#else
			if (msec <= 0 || !cl_predict_players.value || !dopred)
#endif
			{
				VectorCopy (state->origin, pplayer->origin);
			}
			else
			{
				// predict players movement
				if (msec > 255)
					msec = 255;
				state->command.msec = msec;

				CL_PredictUsercmd (state, &exact, &state->command);
				VectorCopy (exact.origin, pplayer->origin);
			}
		}
	}
}

/*
===============
CL_SetSolid

Builds all the pmove physents for the current frame
Note that CL_SetUpPlayerPrediction() must be called first!
pmove must be setup with world and solid entity hulls before calling
(via CL_PredictMove)
===============
*/
void CL_SetSolidPlayers (int playernum)
{
	int		j;
	extern	vec3_t	player_mins;
	extern	vec3_t	player_maxs;
	struct predicted_player *pplayer;
	physent_t *pent;

	if (!cl_solid_players.value)
		return;

	pent = cl.pmove.physents + cl.pmove.numphysent;

	for (j=0, pplayer = predicted_players; j < MAX_CLIENTS;	j++, pplayer++) {

		if (!pplayer->active)
			continue;	// not present this frame

		// the player object never gets added
		if (j == playernum)
			continue;

		if (pplayer->flags & PF_DEAD)
			continue; // dead players aren't solid

		if (cl.pmove.numphysent == MAX_PHYSENTS)
			break;

		pent->model = 0;
		VectorCopy(pplayer->origin, pent->origin);
		VectorCopy(player_mins, pent->mins);
		VectorCopy(player_maxs, pent->maxs);
		cl.pmove.numphysent++;
		pent++;
	}
}


/*
===============
CL_EmitEntities

Builds the visedicts array for cl.time

Made up of: clients, packet_entities, nails, and tents
===============
*/
void CL_EmitEntities (void)
{
	if (cls.state != ca_active)
		return;
	if (!cl.validsequence && !cls.nqprotocol)
		return;

	V_ClearScene ();

	if (cls.nqprotocol)
		NQD_LinkEntities ();
	else {
		CL_LinkPlayers ();
		CL_LinkPacketEntities ();
		CL_LinkNails ();
	}
	CL_LinkDlights ();
	CL_LinkParticles ();

	CL_UpdateTEnts ();
}

void CL_Ents_Init (void)
{
	Cvar_Register (&cl_lerp_monsters);
	Cvar_Register (&r_rocketlight);
	Cvar_Register (&r_rockettrail);
	Cvar_Register (&r_grenadetrail);
	Cvar_Register (&r_powerupglow);
	Cvar_Register (&r_lightflicker);
	Cvar_Register (&cl_deadbodyfilter);
	Cvar_Register (&cl_explosion);
	Cvar_Register (&cl_gibfilter);
	Cvar_Register (&cl_gibtime);
	Cvar_Register (&cl_r2g);
	Cvar_Register (&cl_predict_players);
	Cvar_Register (&cl_solid_players);
	// Just for compatibility with ZQuake 0.14 (remove one day)
	Cmd_AddLegacyCommand ("cl_predictPlayers", "cl_predict_players");
	Cmd_AddLegacyCommand ("cl_solidPlayers", "cl_solid_players");
}
