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

#define CHAN_AUTO   0
#define CHAN_WEAPON 1
#define CHAN_VOICE  2
#define CHAN_ITEM   3
#define CHAN_BODY   4

extern cvar_t sv_phs;


/*
=============================================================================

Com_Printf redirection

=============================================================================
*/

redirect_t	sv_redirected;
static char	sv_outputbuf[MAX_MSGLEN - 1];

/*
==================
SV_FlushRedirect
==================
*/
void SV_FlushRedirect (void)
{
	if (sv_redirected == RD_PACKET)
	{
		// send even if sv_outputbuf is empty
		Netchan_OutOfBandPrint (NS_SERVER, net_from, "%c%s", A2C_PRINT,
			sv_outputbuf);
	}
	else if (sv_redirected == RD_CLIENT)
	{
		if (!sv_outputbuf[0])
			return;
		ClientReliableWrite_Begin (sv_client, svc_print);
		ClientReliableWrite_Byte (PRINT_HIGH);
		ClientReliableWrite_String (sv_outputbuf);
		ClientReliableWrite_End ();
	}

	// clear it
	sv_outputbuf[0] = 0;
}

void SV_RedirectedPrint (char *msg)
{
	if (strlen (msg) + strlen(sv_outputbuf) >= sizeof(sv_outputbuf))
		SV_FlushRedirect ();
	strcat (sv_outputbuf, msg);
}

/*
==================
SV_BeginRedirect

Send Com_Printf data to the remote client instead of the console
==================
*/
void SV_BeginRedirect (redirect_t rd)
{
	sv_redirected = rd;
	sv_outputbuf[0] = 0;
	Com_BeginRedirect (SV_RedirectedPrint);
}

void SV_EndRedirect (void)
{
	SV_FlushRedirect ();
	sv_redirected = RD_NONE;
	Com_EndRedirect ();
}


/*
=============================================================================

EVENT MESSAGES

=============================================================================
*/

static void SV_PrintToClient(client_t *cl, int level, char *string)
{
	ClientReliableWrite_Begin (cl, svc_print);
	ClientReliableWrite_Byte (level);
	ClientReliableWrite_String (string);
	ClientReliableWrite_End ();
}


/*
=================
SV_ClientPrintf

Sends text across to be displayed if the level passes
=================
*/
void SV_ClientPrintf (client_t *cl, int level, char *fmt, ...)
{
	va_list		argptr;
	char		string[1024];
	
	if (level < cl->messagelevel)
		return;
	
	va_start (argptr, fmt);
#ifdef _WIN32
	_vsnprintf (string, sizeof(string) - 1, fmt, argptr);
	string[sizeof(string) - 1] = '\0';
#else
	vsnprintf (string, sizeof(string), fmt, argptr);
#endif // _WIN32
	va_end (argptr);

	SV_PrintToClient(cl, level, string);
}

/*
=================
SV_BroadcastPrintf

Sends text to all active clients
=================
*/
void SV_BroadcastPrintf (int level, char *fmt, ...)
{
	va_list		argptr;
	char		string[1024];
	client_t	*cl;
	int			i;

	va_start (argptr, fmt);
#ifdef _WIN32
	_vsnprintf (string, sizeof(string) - 1, fmt, argptr);
	string[sizeof(string) - 1] = '\0';
#else
	vsnprintf (string, sizeof(string), fmt, argptr);
#endif // _WIN32
	va_end (argptr);

#ifndef AGRIP
	Sys_Printf ("%s", string);	// print to the console
#endif

	for (i=0, cl = svs.clients ; i<MAX_CLIENTS ; i++, cl++)
	{
		if (level < cl->messagelevel)
			continue;
		if (cl->state < cs_connected)
			continue;

		SV_PrintToClient(cl, level, string);
	}
}

/*
=================
SV_BroadcastCommand

Sends text to all active clients
=================
*/
void SV_BroadcastCommand (char *fmt, ...)
{
	va_list		argptr;
	char		string[1024];
	
	if (!sv.state)
		return;
	va_start (argptr, fmt);
#ifdef _WIN32
	_vsnprintf (string, sizeof(string) - 1, fmt, argptr);
	string[sizeof(string) - 1] = '\0';
#else
	vsnprintf (string, sizeof(string), fmt, argptr);
#endif // _WIN32
	va_end (argptr);

	MSG_WriteByte (&sv.reliable_datagram, svc_stufftext);
	MSG_WriteString (&sv.reliable_datagram, string);
}


/*
=================
SV_Multicast

Sends the contents of sv.multicast to a subset of the clients,
then clears sv.multicast.

MULTICAST_ALL	same as broadcast
MULTICAST_PVS	send to clients potentially visible from org
MULTICAST_PHS	send to clients potentially hearable from org
=================
*/
void SV_Multicast (vec3_t origin, int to)
{
	client_t	*client;
	byte		*mask;
	int			leafnum;
	int			j;
	qbool		reliable;
	vec3_t		vieworg;

	reliable = false;

	switch (to)
	{
	case MULTICAST_ALL_R:
		reliable = true;	// intentional fallthrough
	case MULTICAST_ALL:
		mask = NULL;		// everything
		break;

	case MULTICAST_PHS_R:
		reliable = true;	// intentional fallthrough
	case MULTICAST_PHS:
		mask = CM_LeafPHS (CM_PointInLeaf(origin));
		break;

	case MULTICAST_PVS_R:
		reliable = true;	// intentional fallthrough
	case MULTICAST_PVS:
		mask = CM_LeafPVS (CM_PointInLeaf (origin));
		break;

	default:
		mask = NULL;
		Host_Error ("SV_Multicast: bad to: %i", to);
	}

	// send the data to all relevant clients
	for (j = 0, client = svs.clients; j < MAX_CLIENTS; j++, client++)
	{
		if (client->state != cs_spawned)
			continue;

		if (!mask)
			goto inrange;	// multicast to all

		VectorAdd (client->edict->v.origin, client->edict->v.view_ofs, vieworg);

		if (to == MULTICAST_PHS_R || to == MULTICAST_PHS) {
			vec3_t delta;
			VectorSubtract(origin, vieworg, delta);
			if (VectorLength(delta) <= 1024)
				goto inrange;
		}

		leafnum = CM_Leafnum(CM_PointInLeaf(vieworg));
		if (leafnum)
		{
			// -1 is because pvs rows are 1 based, not 0 based like leafs
			leafnum = leafnum - 1;
			if ( !(mask[leafnum>>3] & (1<<(leafnum&7)) ) )
			{
//				Com_Printf ("supressed multicast\n");
				continue;
			}
		}

inrange:
		if (reliable) {
			SV_AddToReliable (client, sv.multicast.data, sv.multicast.cursize);
		} else
			SZ_Write (&client->datagram, sv.multicast.data, sv.multicast.cursize);
	}

	SZ_Clear (&sv.multicast);
}


/*  
==================
SV_StartParticle

Back from NetQuake, now a protocol extension

Use svc_particle if the client supports the extension,
otherwise fall back to QW's temp entities
==================
*/
// quick hack: until I get rid of multicast, only send svc_particles if 
// EVERYONE supports them. Usually the case in single player :)
static qbool AllClientsWantSVCParticle (void)
{
	int i;
	client_t *cl;
	for (i = 0, cl = svs.clients; i < MAX_CLIENTS; i++, cl++) {
		// can't use cs_spawned, otherwise a client who was spawned this frame
		// has a chance of receiving and svc_particle he doesn't support
		if (cl->state < cs_connected)
			continue;
//		if (!(cl->extensions & Z_EXT_SVC_PARTICLE) || cl->uses_proxy)
//			return false;
		if (!cl->bot && cl->netchan.remote_address.type != NA_LOOPBACK)
			return false;
	}
	return true;
}

void SV_StartParticle (vec3_t org, vec3_t dir, int color, int count,
					   int replacement_te, int replacement_count)
{
	int		i, v;
	qbool	send_count;

	if (AllClientsWantSVCParticle())
	{
		MSG_WriteByte (&sv.multicast, nq_svc_particle);
		MSG_WriteCoord (&sv.multicast, org[0]);
		MSG_WriteCoord (&sv.multicast, org[1]);
		MSG_WriteCoord (&sv.multicast, org[2]);
		for (i=0 ; i<3 ; i++)
		{
			v = dir[i]*16;
			if (v > 127)
				v = 127;
			else if (v < -128)
				v = -128;
			MSG_WriteChar (&sv.multicast, v);
		}
		MSG_WriteByte (&sv.multicast, count);
		MSG_WriteByte (&sv.multicast, color);
	}
	else
	{
		if (replacement_te == TE_EXPLOSION || replacement_te == TE_LIGHTNINGBLOOD)
			send_count = false;
		else if (replacement_te == TE_BLOOD || replacement_te == TE_GUNSHOT)
			send_count = true;
		else
			return;		// don't send anything

		MSG_WriteByte (&sv.multicast, svc_temp_entity);
		MSG_WriteByte (&sv.multicast, replacement_te);
		if (send_count)
			MSG_WriteByte (&sv.multicast, replacement_count);
		MSG_WriteCoord (&sv.multicast, org[0]);
		MSG_WriteCoord (&sv.multicast, org[1]);
		MSG_WriteCoord (&sv.multicast, org[2]);
	}

	SV_Multicast (org, MULTICAST_PVS);
}           


/*  
==================
SV_StartSound

Each entity can have eight independent sound sources, like voice,
weapon, feet, etc.

Channel 0 is an auto-allocate channel, the others override anything
already running on that entity/channel pair.

An attenuation of 0 will play full volume everywhere in the level.
Larger attenuations will drop off.  (max 4 attenuation)

If to_client is not NULL, the message will be sent to one client only
==================
*/  
void SV_StartSound (edict_t *entity, int channel, char *sample, int volume,
    float attenuation, client_t *to_client)
{       
	int         sound_num;
	int			field_mask;
	int			i;
	int			ent;
	vec3_t		origin;
	qbool		use_phs;
	qbool		reliable = false;
	byte		buf_data[MAX_MSGLEN];
	sizebuf_t	buf, *msg;

	if (volume < 0 || volume > 255)
		Host_Error ("SV_StartSound: volume = %i", volume);

	if (attenuation < 0 || attenuation > 4)
		Host_Error ("SV_StartSound: attenuation = %f", attenuation);

	if (channel < 0 || channel > 15)
		Host_Error ("SV_StartSound: channel = %i", channel);

// find precache number for sound
	for (sound_num = 1; sound_num < MAX_SOUNDS
		&& sv.sound_name[sound_num]; sound_num++)
		if (!strcmp(sample, sv.sound_name[sound_num]))
			break;
    
	if (sound_num == MAX_SOUNDS || !sv.sound_name[sound_num])
	{
		Com_Printf ("SV_StartSound: %s not precached\n", sample);
		return;
	}
    
	ent = SV_TranslateEntnum(NUM_FOR_EDICT(entity));

	if ((channel & 8) || !sv_phs.value)	// no PHS flag
	{
		if (channel & 8)
			reliable = true; // sounds that break the phs are reliable
		use_phs = false;
		channel &= 7;
	}
	else
		use_phs = true;

//	if (channel == CHAN_BODY || channel == CHAN_VOICE)
//		reliable = true;

	channel = (ent<<3) | channel;

	field_mask = 0;
	if (volume != DEFAULT_SOUND_PACKET_VOLUME)
		channel |= SND_VOLUME;
	if (attenuation != DEFAULT_SOUND_PACKET_ATTENUATION)
		channel |= SND_ATTENUATION;

	// use the entity origin unless it is a bmodel
	if (entity->v.solid == SOLID_BSP)
	{
		for (i=0 ; i<3 ; i++)
			origin[i] = entity->v.origin[i]+0.5*(entity->v.mins[i]+entity->v.maxs[i]);
	}
	else
	{
		VectorCopy (entity->v.origin, origin);
	}

	if (to_client) {
		// to one
		msg = &buf;
		SZ_Init (&buf, buf_data, sizeof(buf_data));
	}
	else // to all
		msg = &sv.multicast;

	MSG_WriteByte (msg, svc_sound);
	MSG_WriteShort (msg, channel);
	if (channel & SND_VOLUME)
		MSG_WriteByte (msg, volume);
	if (channel & SND_ATTENUATION)
		MSG_WriteByte (msg, attenuation*64);
	MSG_WriteByte (msg, sound_num);
	for (i=0 ; i<3 ; i++)
		MSG_WriteCoord (msg, origin[i]);

	if (to_client) {
		// to one
		// No PHS/range checks just to keep the code cleaner
		if (reliable)
			SV_AddToReliable (to_client, msg->data, msg->cursize);
		else
			SZ_Write (&to_client->datagram, msg->data, msg->cursize);
	}
	else {
		// to all
		if (use_phs)
			SV_Multicast (origin, reliable ? MULTICAST_PHS_R : MULTICAST_PHS);
		else
			SV_Multicast (origin, reliable ? MULTICAST_ALL_R : MULTICAST_ALL);
	}
}           


/*
===============================================================================

FRAME UPDATES

===============================================================================
*/

int		sv_nailmodel, sv_supernailmodel, sv_playermodel;

void SV_FindModelNumbers (void)
{
	int		i;

	sv_nailmodel = -1;
	sv_supernailmodel = -1;
	sv_playermodel = -1;

	for (i = 1; i < MAX_MODELS; i++)
	{
		if (!sv.model_name[i])
			break;
		if (!strcmp(sv.model_name[i],"progs/spike.mdl"))
			sv_nailmodel = i;
		if (!strcmp(sv.model_name[i],"progs/s_spike.mdl"))
			sv_supernailmodel = i;
		if (!strcmp(sv.model_name[i],"progs/player.mdl"))
			sv_playermodel = i;
	}
}


/*
==================
SV_WriteClientdataToMessage

==================
*/
void SV_WriteClientdataToMessage (client_t *client, sizebuf_t *msg)
{
	int		i;
	edict_t	*other;
	edict_t	*ent;

	ent = client->edict;

	// send the chokecount for r_netgraph
	if (client->chokecount)
	{
		MSG_WriteByte (msg, svc_chokecount);
		MSG_WriteByte (msg, client->chokecount);
		client->chokecount = 0;
	}

	// send a damage message if the player got hit this frame
	if (ent->v.dmg_take || ent->v.dmg_save)
	{
		other = PROG_TO_EDICT(ent->v.dmg_inflictor);
		MSG_WriteByte (msg, svc_damage);
		MSG_WriteByte (msg, ent->v.dmg_save);
		MSG_WriteByte (msg, ent->v.dmg_take);
		for (i=0 ; i<3 ; i++)
			MSG_WriteCoord (msg, other->v.origin[i] + 0.5*(other->v.mins[i] + other->v.maxs[i]));
	
		ent->v.dmg_take = 0;
		ent->v.dmg_save = 0;
	}

	// a fixangle might get lost in a dropped packet.  Oh well.
	if ( ent->v.fixangle )
	{
		MSG_WriteByte (msg, svc_setangle);
		for (i=0 ; i < 3 ; i++)
			MSG_WriteAngle (msg, ent->v.angles[i]);
		ent->v.fixangle = 0;
	}

	// Z_EXT_TIME protocol extension
	// every now and then, send an update so that extrapolation
	// on client side doesn't stray too far off
	if (svs.realtime - client->lastservertimeupdate > 10)
	{
		MSG_WriteByte (msg, svc_updatestatlong);
		MSG_WriteByte (msg, STAT_TIME);
		MSG_WriteLong (msg, (int)(sv.time * 1000));

		client->lastservertimeupdate = svs.realtime;
	}
}

/*
=======================
SV_UpdateClientStats

Performs a delta update of the stats array.  This should only be performed
when a reliable message can be delivered this frame.
=======================
*/
void SV_UpdateClientStats (client_t *client)
{
	edict_t	*ent;
	int		stats[MAX_CL_STATS];
	int		i;
	
	ent = client->edict;
	memset (stats, 0, sizeof(stats));
	
	// if we are a spectator and we are tracking a player, we get his stats
	// so our status bar reflects his
	if (client->spectator && client->spec_track > 0)
		ent = svs.clients[client->spec_track - 1].edict;

	stats[STAT_HEALTH] = ent->v.health;
	stats[STAT_WEAPON] = SV_ModelIndex(PR_GetString(ent->v.weaponmodel));
	stats[STAT_AMMO] = ent->v.currentammo;
	stats[STAT_ARMOR] = ent->v.armorvalue;
	stats[STAT_SHELLS] = ent->v.ammo_shells;
	stats[STAT_NAILS] = ent->v.ammo_nails;
	stats[STAT_ROCKETS] = ent->v.ammo_rockets;
	stats[STAT_CELLS] = ent->v.ammo_cells;
	if (!client->spectator)
		stats[STAT_ACTIVEWEAPON] = ent->v.weapon;
	// stuff the sigil bits into the high bits of items for sbar
	stats[STAT_ITEMS] = (int)ent->v.items | ((int)PR_GLOBAL(serverflags) << 28);
	if (fofs_items2)	// ZQ_ITEMS2 extension
		stats[STAT_ITEMS] |= (int)EdictFieldFloat(ent, fofs_items2) << 23;

	if (ent->v.health > 0 || client->spectator)	// viewheight for PF_DEAD & PF_GIB is hardwired
		stats[STAT_VIEWHEIGHT] = ent->v.view_ofs[2];

	for (i=0 ; i<MAX_CL_STATS ; i++)
		if (stats[i] != client->stats[i])
		{
			client->stats[i] = stats[i];
			if (stats[i] >=0 && stats[i] <= 255)
			{
				ClientReliableWrite_Begin (client, svc_updatestat);
				ClientReliableWrite_Byte (i);
				ClientReliableWrite_Byte (stats[i]);
				ClientReliableWrite_End ();
			}
			else
			{
				ClientReliableWrite_Begin (client, svc_updatestatlong);
				ClientReliableWrite_Byte (i);
				ClientReliableWrite_Long (stats[i]);
				ClientReliableWrite_End ();
			}
		}
}

/*
=======================
SV_SendClientDatagram
=======================
*/
qbool SV_SendClientDatagram (client_t *client)
{
	byte		msg_buf[MAX_DATAGRAM];
	sizebuf_t	msg;

	SZ_Init (&msg, msg_buf, sizeof(msg_buf));
	msg.allowoverflow = true;

	// add the client specific data to the datagram
	SV_WriteClientdataToMessage (client, &msg);

	// send over all the objects that are in the PVS
	// this will include clients, a packetentities, and
	// possibly a nails update
	SV_WriteEntitiesToClient (client, &msg);

	// copy the accumulated multicast datagram
	// for this client out to the message
	if (client->datagram.overflowed)
		Com_Printf ("WARNING: datagram overflowed for %s\n", client->name);
	else
		SZ_Write (&msg, client->datagram.data, client->datagram.cursize);
	SZ_Clear (&client->datagram);

	// send deltas over reliable stream
	if (Netchan_CanReliable (&client->netchan))
		SV_UpdateClientStats (client);

	if (msg.overflowed)
	{
		Com_Printf ("WARNING: msg overflowed for %s\n", client->name);
		SZ_Clear (&msg);
	}

	// send the datagram
	Netchan_Transmit (&client->netchan, msg.cursize, msg.data);

	return true;
}

/*
=======================
SV_UpdateToReliableMessages
=======================
*/
void SV_UpdateToReliableMessages (void)
{
	int			i, j;
	client_t *client;
	edict_t *ent;

// check for changes to be sent over the reliable streams to all clients
	for (i=0, sv_client = svs.clients ; i<MAX_CLIENTS ; i++, sv_client++)
	{
		if (sv_client->state != cs_spawned)
			continue;
		if (sv_client->sendinfo)
		{
			sv_client->sendinfo = false;
			SV_FullClientUpdate (sv_client, &sv.reliable_datagram);
		}

		ent = sv_client->edict;

		if (sv_client->old_frags != (int)ent->v.frags)
		{
			for (j=0, client = svs.clients ; j<MAX_CLIENTS ; j++, client++)
			{
				if (client->state < cs_connected)
					continue;
				ClientReliableWrite_Begin (client, svc_updatefrags);
				ClientReliableWrite_Byte (i);
				ClientReliableWrite_Short (ent->v.frags);
				ClientReliableWrite_End ();
			}

			sv_client->old_frags = ent->v.frags;
		}

		// maxspeed/entgravity changes
		if (fofs_gravity && sv_client->entgravity != EdictFieldFloat(ent, fofs_gravity)) {
			sv_client->entgravity = EdictFieldFloat(ent, fofs_gravity);
			ClientReliableWrite_Begin (sv_client, svc_entgravity);
			ClientReliableWrite_Float (sv_client->entgravity);
			ClientReliableWrite_End ();
		}

		if (fofs_maxspeed && sv_client->maxspeed != EdictFieldFloat(ent, fofs_maxspeed)) {
			sv_client->maxspeed = EdictFieldFloat(ent, fofs_maxspeed);
			ClientReliableWrite_Begin (sv_client, svc_maxspeed);
			ClientReliableWrite_Float (sv_client->maxspeed);
			ClientReliableWrite_End ();
		}
	}

	if (sv.datagram.overflowed)
		SZ_Clear (&sv.datagram);

	// append the broadcast messages to each client messages
	for (j=0, client = svs.clients ; j<MAX_CLIENTS ; j++, client++)
	{
		if (client->state < cs_connected)
			continue;	// reliables go to all connected or spawned

		SV_AddToReliable (client, sv.reliable_datagram.data, sv.reliable_datagram.cursize);

		if (client->state != cs_spawned)
			continue;	// datagrams only go to spawned
		SZ_Write (&client->datagram
			, sv.datagram.data
			, sv.datagram.cursize);
	}

	SZ_Clear (&sv.reliable_datagram);
	SZ_Clear (&sv.datagram);
}


#ifdef _MSC_VER
#pragma optimize( "", off )
#endif


/*
=======================
SV_SendClientMessages
=======================
*/
void SV_SendClientMessages (void)
{
	int			i;
	client_t	*c;

// update frags, names, etc
	SV_UpdateToReliableMessages ();

// build individual updates
	for (i=0, c = svs.clients ; i<MAX_CLIENTS ; i++, c++)
	{
		if (!c->state)
			continue;

		if (c->drop) {
			SV_DropClient(c);
			c->drop = false;
			continue;
		}

		// flush back-buffered reliable data if room enough
		// FIXME: do it after Netchan_Transmit/SV_SendClientDatagram?
		SV_FlushBackbuf (c);

		// if the reliable message overflowed,
		// drop the client
		if (c->netchan.message.overflowed)
		{
			SZ_Clear (&c->netchan.message);
			SZ_Clear (&c->datagram);
			SV_BroadcastPrintf (PRINT_HIGH, "%s overflowed\n", c->name);
			Com_Printf ("WARNING: reliable overflow for %s\n",c->name);
			SV_DropClient (c);
			c->send_message = true;
			c->netchan.cleartime = 0;	// don't choke this message
		}

		// only send messages if the client has sent one
		// and the bandwidth is not choked
		if (!c->send_message)
			continue;
		c->send_message = false;	// try putting this after choke?
		if (!sv_paused.value && !Netchan_CanPacket (&c->netchan))
		{
			c->chokecount++;
			continue;		// bandwidth choke
		}

		if (c->state == cs_spawned)
			SV_SendClientDatagram (c);
		else
			Netchan_Transmit (&c->netchan, 0, NULL);	// just update reliable
	}
}

#ifdef _MSC_VER
#pragma optimize( "", on )
#endif



/*
=======================
SV_SendMessagesToAll

FIXME: does this sequence right?
=======================
*/
void SV_SendMessagesToAll (void)
{
	int			i;
	client_t	*c;

	for (i=0, c = svs.clients ; i<MAX_CLIENTS ; i++, c++)
		if (c->state >= cs_connected)		// FIXME: should this only send to active?
			c->send_message = true;
	
	SV_SendClientMessages ();
}

