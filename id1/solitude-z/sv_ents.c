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

#include "server.h"
#include "pmove.h"

int SV_PMTypeForClient (client_t *cl);

//=============================================================================

// because there can be a lot of nails, there is a special
// network protocol for them
#define	MAX_NAILS	32
edict_t	*nails[MAX_NAILS];
int		numnails;

extern	int	sv_nailmodel, sv_supernailmodel, sv_playermodel;

#ifdef SERVERONLY
cvar_t	sv_nailhack	= {"sv_nailhack", "0"};
#else
cvar_t	sv_nailhack	= {"sv_nailhack", "1"};
#endif

qbool SV_AddNailUpdate (edict_t *ent)
{
	if (sv_nailhack.value)
		return false;

	if (ent->v.modelindex != sv_nailmodel
		&& ent->v.modelindex != sv_supernailmodel)
		return false;
	if (numnails == MAX_NAILS)
		return true;
	nails[numnails] = ent;
	numnails++;
	return true;
}

void SV_EmitNailUpdate (sizebuf_t *msg)
{
	byte	bits[6];	// [48 bits] xyzpy 12 12 12 4 8 
	int		n, i;
	edict_t	*ent;
	int		x, y, z, pitch, yaw;

	if (!numnails)
		return;

	MSG_WriteByte (msg, svc_nails);
	MSG_WriteByte (msg, numnails);

	for (n=0 ; n<numnails ; n++)
	{
		ent = nails[n];
		x = ((int)(ent->v.origin[0] + 4096 + 1) >> 1) & 4095;
		y = ((int)(ent->v.origin[1] + 4096 + 1) >> 1) & 4095;
		z = ((int)(ent->v.origin[2] + 4096 + 1) >> 1) & 4095;
		pitch = Q_rint(ent->v.angles[0]*(16.0/360.0)) & 15;
		yaw = Q_rint(ent->v.angles[1]*(256.0/360.0)) & 255;

		bits[0] = x;
		bits[1] = (x>>8) | (y<<4);
		bits[2] = (y>>4);
		bits[3] = z;
		bits[4] = (z>>8) | (pitch<<4);
		bits[5] = yaw;

		for (i=0 ; i<6 ; i++)
			MSG_WriteByte (msg, bits[i]);
	}
}

//=============================================================================

//
// returns translated entity number for sending to client
//
int SV_TranslateEntnum (int num)
{
	entity_translation_t	*trans, *best;
	double	besttime, trivial_accept;
	int	i;

	assert (num >= 0 && num < MAX_EDICTS);

	if (num <= MAX_CLIENTS)					// client entitites are never translated
		return num;

	if (sv.entmap[num]) {
		// see if the previous translation is still valid
		trans = &sv.translations[sv.entmap[num]];
		if (trans->original == num) {
			// translation is still valid
			trans->lastused = svs.realtime;
			return sv.entmap[num];
		}
	}

	trivial_accept = svs.realtime - 10;		// anything older than that will do

	if (num < 512) {
		// whenever possible, try to use the original number as translation
		trans = &sv.translations[num];
		if (!trans->lastused || trans->lastused < trivial_accept) {
			// good, we can use it
			trans->original = num;
			trans->lastused = svs.realtime;
			sv.entmap[num] = num;
			return num;
		}
	}

//Com_Printf ("looking for a new translation...\n");

	// find a new translation slot
	besttime = svs.realtime;
	best = NULL;

	for (i = MAX_CLIENTS + 1; i < 512; i++) {
		if (sv.edicts[i].baseline.modelindex)
			continue;		// never use slots with baselines

		trans = &sv.translations[i];
		if (!trans->lastused || trans->lastused < trivial_accept) {
			best = trans;
			break;
		}

		if (trans->lastused < besttime) {
			besttime = trans->lastused;
			best = trans;
		}
	}

	if (!best)
		Host_Error ("SV_TranslateEntnum: no free translation slots");

	best->lastused = svs.realtime;
	best->original = num;
	sv.entmap[num] =  best - sv.translations;

	return sv.entmap[num];
}

//=============================================================================

static int TranslateEffects (edict_t *ent)
{
	int fx = (int)ent->v.effects;
	if (pr_nqprogs)
		fx &= ~EF_MUZZLEFLASH;
	if (pr_nqprogs && (fx & EF_DIMLIGHT)) {
		if ((int)ent->v.items & IT_QUAD)
			fx |= EF_BLUE;
		if ((int)ent->v.items & IT_INVULNERABILITY)
			fx |= EF_RED;
	}
	return fx;
}


/*
=============
SV_WritePlayersToClient

=============
*/
void SV_WritePlayersToClient (client_t *client, byte *pvs, sizebuf_t *msg)
{
	int			i, j;
	client_t	*cl;
	edict_t		*ent;
	int			msec;
	usercmd_t	cmd;
	int			pflags;
	int			pm_type = 0, pm_code = 0;

	for (j=0,cl=svs.clients ; j<MAX_CLIENTS ; j++,cl++)
	{
		if (cl->state != cs_spawned)
			continue;

		ent = cl->edict;

		// ZOID visibility tracking
		if (cl != client &&
			!(client->spec_track && client->spec_track - 1 == j)) 
		{
			if (cl->spectator)
				continue;

			// ignore if not touching a PV leaf
			for (i=0 ; i < ent->num_leafs ; i++)
				if (pvs[ent->leafnums[i] >> 3] & (1 << (ent->leafnums[i]&7) ))
					break;
			if (i == ent->num_leafs)
				continue;		// not visible
		}
		
		pflags = PF_MSEC | PF_COMMAND;
		
		if (ent->v.modelindex != sv_playermodel)
			pflags |= PF_MODEL;
		for (i=0 ; i<3 ; i++)
			if (ent->v.velocity[i])
				pflags |= PF_VELOCITY1<<i;
		if (ent->v.effects)
			pflags |= PF_EFFECTS;
		if (ent->v.skin)
			pflags |= PF_SKINNUM;
		if (ent->v.health <= 0)
			pflags |= PF_DEAD;
		if (ent->v.mins[2] != -24)
			pflags |= PF_GIB;

		if (cl->spectator)
		{	// only send origin and velocity to spectators
			pflags &= PF_VELOCITY1 | PF_VELOCITY2 | PF_VELOCITY3;
		}
		else if (cl == client)
		{	// don't send a lot of data on personal entity
			pflags &= ~(PF_MSEC|PF_COMMAND);
			if (ent->v.weaponframe)
				pflags |= PF_WEAPONFRAME;
		}

		// Z_EXT_PM_TYPE protocol extension
		// encode pm_type and jump_held into pm_code
		pm_type = SV_PMTypeForClient (cl);
		switch (pm_type) {
		case PM_DEAD:
			pm_code = PMC_NORMAL;	// plus PF_DEAD
			break;
		case PM_NORMAL:
			pm_code = PMC_NORMAL;
			if (cl->jump_held)
				pm_code = PMC_NORMAL_JUMP_HELD;
			break;
		case PM_OLD_SPECTATOR:
			pm_code = PMC_OLD_SPECTATOR;
			break;
		case PM_SPECTATOR:
			pm_code = PMC_SPECTATOR;
			break;
		case PM_FLY:
			pm_code = PMC_FLY;
			break;
		case PM_NONE:
			pm_code = PMC_NONE;
			break;
		case PM_FREEZE:
			pm_code = PMC_FREEZE;
			break;
		default:
			assert (false);
		}
		pflags |= pm_code << PF_PMC_SHIFT;

		// Z_EXT_PF_ONGROUND protocol extension
		if ((int)ent->v.flags & FL_ONGROUND)
			pflags |= PF_ONGROUND;

		if (client->spec_track && client->spec_track - 1 == j &&
			ent->v.weaponframe) 
			pflags |= PF_WEAPONFRAME;

		MSG_WriteByte (msg, svc_playerinfo);
		MSG_WriteByte (msg, j);
		MSG_WriteShort (msg, pflags);

		for (i=0 ; i<3 ; i++)
			MSG_WriteCoord (msg, ent->v.origin[i]);
		
		MSG_WriteByte (msg, ent->v.frame);

		if (pflags & PF_MSEC)
		{
			msec = 1000*(svs.realtime - cl->cmdtime);
			if (msec > 255)
				msec = 255;
			MSG_WriteByte (msg, msec);
		}
		
		if (pflags & PF_COMMAND)
		{
			cmd = cl->lastcmd;

			if (ent->v.health <= 0)
			{	// don't show the corpse looking around...
				cmd.angles[0] = 0;
				cmd.angles[1] = ent->v.angles[1];
				cmd.angles[0] = 0;
			}

			cmd.msec = 0;		// unlike qwsv, but no one really needs this
			cmd.buttons = 0;	// never send buttons
			cmd.impulse = 0;	// never send impulses

#ifdef VWEP_TEST
			// @@VWep test
			if ((client->extensions & Z_EXT_VWEP) && sv.vw_model_name[0]
			&& fofs_vw_index) {
				cmd.impulse = EdictFieldFloat (ent, fofs_vw_index);
			}
#endif

			MSG_WriteDeltaUsercmd (msg, &nullcmd, &cmd);
		}

		for (i=0 ; i<3 ; i++)
			if (pflags & (PF_VELOCITY1<<i) )
				MSG_WriteShort (msg, ent->v.velocity[i]);

		if (pflags & PF_MODEL)
			MSG_WriteByte (msg, ent->v.modelindex);

		if (pflags & PF_SKINNUM)
			MSG_WriteByte (msg, ent->v.skin);

		if (pflags & PF_EFFECTS)
			MSG_WriteByte (msg, TranslateEffects(ent));

		if (pflags & PF_WEAPONFRAME)
			MSG_WriteByte (msg, ent->v.weaponframe);
	}
}

// passed to qsort
static int entity_state_compare (const void *p1, const void *p2)
{
	return ((entity_state_t *) p1)->number - ((entity_state_t *) p2)->number;
}

// passed to MSG_EmitPacketEntities
static entity_state_t *SV_GetBaseline (int number)
{
	return &EDICT_NUM(number)->baseline;
}


/*
=============
SV_WriteEntitiesToClient

Encodes the current state of the world as
a svc_packetentities messages and possibly
a svc_nails message and
svc_playerinfo messages
=============
*/
void SV_WriteEntitiesToClient (client_t *client, sizebuf_t *msg)
{
	int		e, i;
	byte	*pvs;
	vec3_t	org;
	edict_t	*ent;
	packet_entities_t	*pack;
	edict_t	*clent;
	client_frame_t	*frame;
	entity_state_t	*state;
	entity_state_t	newents[MAX_PACKET_ENTITIES];

	// this is the frame we are creating
	frame = &client->frames[client->netchan.incoming_sequence & UPDATE_MASK];

	if (sv.intermission_running && sv.intermission_origin_valid) {
		pvs = CM_FatPVS (sv.intermission_origin);
	}
	else {
		// find the client's PVS
		clent = client->edict;
		VectorAdd (clent->v.origin, clent->v.view_ofs, org);
		pvs = CM_FatPVS (org);
	}

	// send over the players in the PVS
	SV_WritePlayersToClient (client, pvs, msg);
	
	// put other visible entities into either a packet_entities or a nails message
	pack = &frame->entities;
	pack->num_entities = 0;

	numnails = 0;

	for (e=MAX_CLIENTS+1, ent=EDICT_NUM(e) ; e < sv.num_edicts ; e++, ent = NEXT_EDICT(ent))
	{
		// ignore ents without visible models
		if (!ent->v.modelindex || !*PR_GetString(ent->v.model))
			continue;

		// ignore if not touching a PV leaf
		for (i=0 ; i < ent->num_leafs ; i++)
			if (pvs[ent->leafnums[i] >> 3] & (1 << (ent->leafnums[i]&7) ))
				break;
			
		if (i == ent->num_leafs)
			continue;		// not visible

		if (SV_AddNailUpdate (ent))
			continue;	// added to the special update list

		// add to the packetentities
		if (pack->num_entities == MAX_PACKET_ENTITIES)
			continue;	// all full

		state = &newents[pack->num_entities];
		pack->num_entities++;

		state->number = SV_TranslateEntnum(e);
		state->flags = 0;
		MSG_PackOrigin (ent->v.origin, state->s_origin);
		MSG_PackAngles (ent->v.angles, state->s_angles);
		state->modelindex = ent->v.modelindex;
		state->frame = ent->v.frame;
		state->colormap = ent->v.colormap;
		state->skinnum = ent->v.skin;
		state->effects = TranslateEffects(ent);
	}

	// entity translation might have broken original entnum order, so sort them
	qsort (newents, pack->num_entities, sizeof(newents[0]), entity_state_compare);

	Q_free (pack->entities);
	pack->entities = Q_malloc (sizeof(newents[0]) * pack->num_entities);
	memcpy (pack->entities, newents, sizeof(newents[0]) * pack->num_entities);

	if (client->delta_sequence != -1) {
		// encode the packet entities as a delta from the
		// last packetentities acknowledged by the client
		MSG_EmitPacketEntities (&client->frames[client->delta_sequence & UPDATE_MASK].entities,
			client->delta_sequence, pack, msg, SV_GetBaseline);
	}
	else {
		// no delta
		MSG_EmitPacketEntities (NULL, 0, pack, msg, SV_GetBaseline);
	}

	// now add the specialized nail update
	SV_EmitNailUpdate (msg);

	// Translate NQ progs' EF_MUZZLEFLASH to svc_muzzleflash
	if (pr_nqprogs)
	for (e=1, ent=EDICT_NUM(e) ; e < sv.num_edicts ; e++, ent = NEXT_EDICT(ent))
	{
		// ignore ents without visible models
		if (!ent->v.modelindex || !*PR_GetString(ent->v.model))
			continue;

		// ignore if not touching a PV leaf
		for (i=0 ; i < ent->num_leafs ; i++)
			if (pvs[ent->leafnums[i] >> 3] & (1 << (ent->leafnums[i]&7) ))
				break;

		if ((int)ent->v.effects & EF_MUZZLEFLASH) {
			ent->v.effects = (int)ent->v.effects & ~EF_MUZZLEFLASH;
			MSG_WriteByte (msg, svc_muzzleflash);
			MSG_WriteShort (msg, e);
		}
	}			
}

/* vi: set noet ts=4 sts=4 ai sw=4: */
