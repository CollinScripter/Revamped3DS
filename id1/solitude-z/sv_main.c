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
#include "version.h"

client_t	*sv_client;					// current client

cvar_t	sv_mintic = {"sv_mintic", "0.013"};	// bound the size of the
cvar_t	sv_maxtic = {"sv_maxtic", "0.1"};	// physics time tic

cvar_t	sv_timeout = {"sv_timeout", "65"};		// seconds without any message
cvar_t	sv_zombietime = {"sv_zombietime", "2"};	// seconds to sink messages
											// after disconnect

cvar_t	sv_rconPassword = {"rcon_password", ""};	// password for remote server commands
cvar_t	sv_password = {"password", ""};				// password for entering the game
cvar_t	sv_spectatorPassword = {"spectator_password", ""};	// password for entering as a sepctator

cvar_t	allow_download			= {"allow_download", "1"};
cvar_t	allow_download_skins	= {"allow_download_skins", "1"};
cvar_t	allow_download_models	= {"allow_download_models", "1"};
cvar_t	allow_download_sounds	= {"allow_download_sounds", "1"};
cvar_t	allow_download_maps		= {"allow_download_maps", "1"};
cvar_t	allow_download_pakmaps	= {"allow_download_pakmaps", "0"};
cvar_t	allow_download_gfx		= {"allow_download_gfx", "1"};
cvar_t	allow_download_other	= {"allow_download_other", "1"};	// make it 0 one day

cvar_t	sv_phs = {"sv_phs", "1"};
cvar_t	sv_pausable = {"sv_pausable", "1"};
cvar_t	sv_paused = {"sv_paused", "0", CVAR_ROM};
cvar_t	sv_maxrate = {"sv_maxrate", "0"};
cvar_t	sv_fastconnect = {"sv_fastconnect", "0"};

#ifdef MAUTH
#include "sv_authlists.h"
authqh_t authtokq;
authqh_t authclientq;
#define MAX_AUTH_TOK_QUEUE 4
#define MAX_AUTH_CLIENT_QUEUE 40
#endif

//
// game rules mirrored in svs.info
//
cvar_t	fraglimit = {"fraglimit","0",CVAR_SERVERINFO};
cvar_t	timelimit = {"timelimit","0",CVAR_SERVERINFO};
cvar_t	teamplay = {"teamplay","0",CVAR_SERVERINFO};
cvar_t	samelevel = {"samelevel","0",CVAR_SERVERINFO};
void OnChange_maxclients (cvar_t *var, char *str, qbool *cancel);
cvar_t	maxclients = {"maxclients","8",CVAR_SERVERINFO, OnChange_maxclients};
cvar_t	maxspectators = {"maxspectators","8",CVAR_SERVERINFO, OnChange_maxclients};
cvar_t	deathmatch = {"deathmatch","0",CVAR_SERVERINFO};			// 0, 1, or 2
cvar_t	hostname = {"hostname","unnamed",CVAR_SERVERINFO};
cvar_t	watervis = {"watervis","0",CVAR_SERVERINFO};

cvar_t	skill = {"skill", "1"};
cvar_t	coop = {"coop", "0", CVAR_SERVERINFO};

int		current_skill;			// for entity spawnflags checking

FILE	*sv_fraglogfile;

void SV_AcceptClient (netadr_t adr, int userid, char *userinfo);

//============================================================================

// handles both maxclients and maxspectators
void OnChange_maxclients (cvar_t *var, char *str, qbool *cancel) {
	int num = Q_atoi(str);
	num = bound(0, num, MAX_CLIENTS);
	Cvar_SetValue (var, num);
	*cancel = true;
}

static void SV_FreeHeadDelayedPacket(client_t *cl) {
	if (cl->packets) {
		packet_t *next = cl->packets->next;
		cl->packets->next = svs.free_packets;
		svs.free_packets = cl->packets;
		cl->packets = next;
	}
}


void SV_FreeDelayedPackets (client_t *cl) {
	while (cl->packets)
		SV_FreeHeadDelayedPacket(cl);
}

/*
==================
SV_FinalMessage

Used by SV_Shutdown to send a final message to all connected
clients before the server goes down.  The messages are sent immediately,
not just stuck on the outgoing message list, because the server is going
to totally exit after returning from this function.
==================
*/
void SV_FinalMessage (char *message)
{
	int			i;
	client_t	*cl;

	if (!sv.state)
		return;

	SZ_Clear (&net_message);
	MSG_WriteByte (&net_message, svc_print);
	MSG_WriteByte (&net_message, PRINT_HIGH);
	MSG_WriteString (&net_message, message);
	MSG_WriteByte (&net_message, svc_disconnect);

	for (i=0, cl = svs.clients ; i<MAX_CLIENTS ; i++, cl++)
		if (cl->state >= cs_spawned)
			Netchan_Transmit (&cl->netchan, net_message.cursize
			, net_message.data);
}


/*
================
SV_Shutdown

Quake calls this before calling Sys_Quit or Sys_Error
================
*/
void SV_Shutdown (char *finalmsg)
{
	int i, j;

	SV_FinalMessage (finalmsg);

	PR_FreeStrings ();

	Master_Shutdown ();
	NET_ServerConfig (false);

	if (sv_fraglogfile)
	{
		fclose (sv_fraglogfile);
		sv_fraglogfile = NULL;
	}

	memset (&sv, 0, sizeof(sv));
	sv.state = ss_dead;
	com_serveractive = false;

	for (i = 0; i < MAX_CLIENTS; i++) {
		SV_FreeDelayedPackets(&svs.clients[i]);
		for (j = 0; j < UPDATE_BACKUP; j++) {
			Q_free(svs.clients[i].frames[j].entities.entities);
			svs.clients[i].frames[j].entities.entities = NULL;
		}
	}

	memset (svs.clients, 0, sizeof(svs.clients));
	svs.lastuserid = 0;
}


/*
=====================
SV_DropClient

Called when the player is totally leaving the server, either willingly
or unwillingly.  This is NOT called if the entire server is quiting
or crashing.
=====================
*/
void SV_DropClient (client_t *drop)
{
	int i;

	if (drop->bot) {
		SV_RemoveBot (drop);
		return;
	}

	// add the disconnect
	MSG_WriteByte (&drop->netchan.message, svc_disconnect);

	if (drop->state == cs_spawned)
	{
		if (!drop->spectator)
		{
			// call the prog function for removing a client
			// this will set the body to a dead frame, among other things
			pr_global_struct->self = EDICT_TO_PROG(drop->edict);
			PR_ExecuteProgram (PR_GLOBAL(ClientDisconnect));
		}
		else if (SpectatorDisconnect)
		{
			// call the prog function for removing a client
			// this will set the body to a dead frame, among other things
			pr_global_struct->self = EDICT_TO_PROG(drop->edict);
			PR_ExecuteProgram (SpectatorDisconnect);
		}
	}

#ifdef MAUTH
    // remove client from auth queue...
    authclient_t *dropclient;
    dropclient = SV_AuthListFind(&authclientq, Info_ValueForKey(drop->userinfo, "name"));
    if( dropclient )
       SV_AuthListRemove (&authclientq, dropclient);  
#endif

	if (drop->spectator)
		Com_Printf ("Spectator %s removed\n",drop->name);
	else
		Com_Printf ("Client %s removed\n",drop->name);

	if (drop->download)
	{
		fclose (drop->download);
		drop->download = NULL;
	}
	if (drop->upload)
	{
		fclose (drop->upload);
		drop->upload = NULL;
	}
	*drop->uploadfn = 0;

	drop->state = cs_zombie;		// become free in a few seconds
	drop->connection_started = svs.realtime;	// for zombie timeout

	drop->old_frags = 0;
	drop->edict->v.frags = 0;
//	drop->edict->inuse = false;
	drop->name[0] = 0;
	memset (drop->userinfo, 0, sizeof(drop->userinfo));

	SV_FreeDelayedPackets(drop);
	
	for (i = 0; i < UPDATE_BACKUP; i++) {
			Q_free(drop->frames[i].entities.entities);
			drop->frames[i].entities.entities = NULL;
	}

// send notification to all remaining clients
	SV_FullClientUpdate (drop, &sv.reliable_datagram);
}


//====================================================================

/*
===================
SV_CalcPing

===================
*/
int SV_CalcPing (client_t *cl)
{
	float		ping;
	int			i;
	int			count;
	register	client_frame_t *frame;

	if (cl->bot)
		return 0;

	ping = 0;
	count = 0;
	for (frame = cl->frames, i=0 ; i<UPDATE_BACKUP ; i++, frame++)
	{
		if (frame->ping_time > 0)
		{
			ping += frame->ping_time;
			count++;
		}
	}
	if (!count)
		return 9999;
	ping /= count;

	return ping*1000;
}

/*
===================
SV_FullClientUpdate

Writes all update values to a sizebuf
===================
*/
void SV_FullClientUpdate (client_t *client, sizebuf_t *buf)
{
	int		i;
	char	info[MAX_INFO_STRING];

	i = client - svs.clients;

	if (client->state == cs_free && sv_fastconnect.value)
		return;

	MSG_WriteByte (buf, svc_updatefrags);
	MSG_WriteByte (buf, i);
	MSG_WriteShort (buf, client->old_frags);
	
	MSG_WriteByte (buf, svc_updateping);
	MSG_WriteByte (buf, i);
	MSG_WriteShort (buf, SV_CalcPing (client));
	
	MSG_WriteByte (buf, svc_updatepl);
	MSG_WriteByte (buf, i);
	MSG_WriteByte (buf, client->lossage);
	
	MSG_WriteByte (buf, svc_updateentertime);
	MSG_WriteByte (buf, i);
	MSG_WriteFloat (buf, svs.realtime - client->connection_started);

	strcpy (info, client->userinfo);
	Info_RemovePrefixedKeys (info, '_');	// server passwords, etc
	Info_RemoveKey (info, "pmodel");
	Info_RemoveKey (info, "emodel");

	MSG_WriteByte (buf, svc_updateuserinfo);
	MSG_WriteByte (buf, i);
	MSG_WriteLong (buf, client->userid);
	MSG_WriteString (buf, info);
}

/*
===================
SV_FullClientUpdateToClient

Writes all update values to a client's reliable stream
===================
*/
void SV_FullClientUpdateToClient (client_t *client, client_t *cl)
{
	byte data[MAX_MSGLEN];
	sizebuf_t buf;
	
	SZ_Init (&buf, data, sizeof(data));
	SV_FullClientUpdate (client, &buf);
	SV_AddToReliable (cl, buf.data, buf.cursize);
}

/*
===================
SV_GenerateUserID

Returns a unique userid in 1..99 range
===================
*/
int SV_GenerateUserID (void)
{
	int			i;
	client_t	*cl;

	do {
		svs.lastuserid++;
		if (svs.lastuserid == 100)
			svs.lastuserid = 1;
		for (i = 0, cl = svs.clients; i < MAX_CLIENTS; i++, cl++)
			if (cl->state != cs_free && cl->userid == svs.lastuserid)
				break;
	} while (i != MAX_CLIENTS);
	
	return svs.lastuserid;
}


/*
==============================================================================

CONNECTIONLESS COMMANDS

==============================================================================
*/

/*
================
SVC_Status

Responds with all the info that qplug or qspy can see
This message can be up to around 5k with worst case string lengths.
================
*/
void SVC_Status (void)
{
	int		i;
	client_t	*cl;
	int		ping;
	int		top, bottom;

	SV_BeginRedirect (RD_PACKET);
	Com_Printf ("%s\n", svs.info);
	for (i=0 ; i<MAX_CLIENTS ; i++)
	{
		cl = &svs.clients[i];
		if ((cl->state == cs_connected || cl->state == cs_spawned ) && !cl->spectator)
		{
			top = atoi(Info_ValueForKey (cl->userinfo, "topcolor"));
			bottom = atoi(Info_ValueForKey (cl->userinfo, "bottomcolor"));
			top = (top < 0) ? 0 : ((top > 13) ? 13 : top);
			bottom = (bottom < 0) ? 0 : ((bottom > 13) ? 13 : bottom);
			ping = SV_CalcPing (cl);
			Com_Printf ("%i %i %i %i \"%s\" \"%s\" %i %i\n", cl->userid, 
				cl->old_frags, (int)(svs.realtime - cl->connection_started)/60,
				ping, cl->name, Info_ValueForKey (cl->userinfo, "skin"), top, bottom);
		}
	}
	SV_EndRedirect ();
}

/*
===================
SV_CheckLog

===================
*/
#define	LOG_HIGHWATER	(MAX_DATAGRAM - 128)
#define	LOG_FLUSH		10*60
void SV_CheckLog (void)
{
	sizebuf_t	*sz;

	sz = &svs.log[svs.logsequence&1];

	// bump sequence if allmost full, or ten minutes have passed and
	// there is something still sitting there
	if (sz->cursize > LOG_HIGHWATER
	|| (svs.realtime - svs.logtime > LOG_FLUSH && sz->cursize) )
	{
		// swap buffers and bump sequence
		svs.logtime = svs.realtime;
		svs.logsequence++;
		sz = &svs.log[svs.logsequence&1];
		sz->cursize = 0;
		Com_DPrintf ("beginning fraglog sequence %i\n", svs.logsequence);
	}

}

/*
================
SVC_Log

Responds with all the logged frags for ranking programs.
If a sequence number is passed as a parameter and it is
the same as the current sequence, an A2A_NACK will be returned
instead of the data.
================
*/
void SVC_Log (void)
{
	int		seq;
	char	data[MAX_DATAGRAM+64];

	if (Cmd_Argc() == 2)
		seq = atoi(Cmd_Argv(1));
	else
		seq = -1;

	if (seq == svs.logsequence-1 || !sv_fraglogfile)
	{	// they already have this data, or we aren't logging frags
		data[0] = A2A_NACK;
		NET_SendPacket (NS_SERVER, 1, data, net_from);
		return;
	}

	Com_DPrintf ("sending log %i to %s\n", svs.logsequence-1, NET_AdrToString(net_from));

	sprintf (data, "stdlog %i\n", svs.logsequence-1);
	strcat (data, (char *)svs.log_buf[((svs.logsequence-1)&1)]);

	NET_SendPacket (NS_SERVER, strlen(data)+1, data, net_from);
}

/*
================
SVC_Ping

Just responds with an acknowledgement
================
*/
void SVC_Ping (void)
{
	char	data;

	data = A2A_ACK;

	NET_SendPacket (NS_SERVER, 1, &data, net_from);
}

/*
=================
SVC_GetChallenge

Returns a challenge number that can be used
in a subsequent client_connect command.
We do this to prevent denial of service attacks that
flood the server with invalid connection IPs.  With a
challenge, they must give a valid IP address.
=================
*/
void SVC_GetChallenge (void)
{
	int		i;
	int		oldest;
	int		oldestTime;

	oldest = 0;
	oldestTime = 0x7fffffff;

	// see if we already have a challenge for this ip
	for (i = 0 ; i < MAX_CHALLENGES ; i++)
	{
		if (NET_CompareBaseAdr (net_from, svs.challenges[i].adr))
			break;
		if (svs.challenges[i].time < oldestTime)
		{
			oldestTime = svs.challenges[i].time;
			oldest = i;
		}
	}

	if (i == MAX_CHALLENGES)
	{
		// overwrite the oldest
		svs.challenges[oldest].challenge = (rand() << 16) ^ rand();
		svs.challenges[oldest].adr = net_from;
		svs.challenges[oldest].time = svs.realtime;
		i = oldest;
	}

	// send it back
	Netchan_OutOfBandPrint (NS_SERVER, net_from, "%c%i", S2C_CHALLENGE, 
			svs.challenges[i].challenge);
}

/*
==================
SVC_DirectConnect

A connection request that did not come from the master
==================
*/
void SVC_DirectConnect (void)
{
	char		userinfo[1024];
	netadr_t	adr;
	int			i;
	client_t	*cl, *newcl;
	edict_t		*ent;
	int			edictnum;
	char		*s;
	int			clients, spectators;
	qbool		spectator;
	int			qport;
	int			version;
	int			challenge;

	version = atoi(Cmd_Argv(1));
	if (version != PROTOCOL_VERSION)
	{
		Netchan_OutOfBandPrint (NS_SERVER, net_from, "%c\nServer is version %4.2f.\n", A2C_PRINT, QW_VERSION);
		Com_Printf ("* rejected connect from version %i\n", version);
		return;
	}

	qport = atoi(Cmd_Argv(2));
	challenge = atoi(Cmd_Argv(3));

	// note an extra byte is needed to replace spectator key
	strlcpy (userinfo, Cmd_Argv(4), sizeof(userinfo)-1);

	// see if the challenge is valid
	if (net_from.type != NA_LOOPBACK)
	{
		for (i=0 ; i<MAX_CHALLENGES ; i++)
		{
			if (NET_CompareBaseAdr (net_from, svs.challenges[i].adr))
			{
				if (challenge == svs.challenges[i].challenge)
					break;		// good
				Netchan_OutOfBandPrint (NS_SERVER, net_from, "%c\nBad challenge.\n", A2C_PRINT);
				return;
			}
		}
		if (i == MAX_CHALLENGES)
		{
			Netchan_OutOfBandPrint (NS_SERVER, net_from, "%c\nNo challenge for address.\n", A2C_PRINT);
			return;
		}
	}

	// check for password or spectator_password
	s = Info_ValueForKey (userinfo, "spectator");
	if (s[0] && strcmp(s, "0"))
	{
		if (sv_spectatorPassword.string[0] && 
			Q_stricmp(sv_spectatorPassword.string, "none") &&
			strcmp(sv_spectatorPassword.string, s) )
		{	// failed
			Com_Printf ("%s:spectator password failed\n", NET_AdrToString (net_from));
			Netchan_OutOfBandPrint (NS_SERVER, net_from, "%c\nrequires a spectator password\n\n", A2C_PRINT);
			return;
		}
		Info_RemoveKey (userinfo, "spectator");
		Info_SetValueForStarKey (userinfo, "*spectator", "1", MAX_INFO_STRING);
		spectator = true;
	}
	else
	{
		s = Info_ValueForKey (userinfo, "password");
		if (sv_password.string[0] && 
			Q_stricmp(sv_password.string, "none") &&
			strcmp(sv_password.string, s) )
		{
			Com_Printf ("%s:password failed\n", NET_AdrToString (net_from));
			Netchan_OutOfBandPrint (NS_SERVER, net_from, "%c\nserver requires a password\n\n", A2C_PRINT);
			return;
		}
		spectator = false;
		Info_RemoveKey (userinfo, "password");
	}

#ifdef MAUTH
    // Check that the client is allowed to connect...
	if( net_from.type != NA_LOOPBACK && !COM_CheckParm("-nomauth") )
    {
        authclient_t *authclient;
    
        // Try the auth token queue first...
        authclient = SV_AuthListFind(&authtokq, Info_ValueForKey(userinfo, "name"));
        if( authclient == NULL )
        {
            // Fall back to checking if they had already connected and are in the
            // client queue already (i.e. were on here before a map change)...
            authclient = SV_AuthListFind(&authclientq, Info_ValueForKey(userinfo, "name"));
            if( authclient == NULL )
            {
                // FIXME drop with reason
                Com_Printf ("MAUTH: Client %s not in a queue; connect refused.\n", Info_ValueForKey(userinfo, "name"));
                return;
            }
        }
        else
        {
            // They're valid, so move them to the main client queue from the
            // auth cache queue...
            SV_AuthListMove(&authtokq, &authclientq, authclient);
        }

        // Move to auth'd clients queue if they're valid...
        if( !authclient->valid )
        {
            // FIXME drop with reason
            Com_Printf ("MAUTH: Client %s not validated yet; connect refused.\n", Info_ValueForKey(userinfo, "name"));
            return;
        }
        
        // debugging:
        SV_AuthListPrint(&authtokq);
        SV_AuthListPrint(&authclientq);
        
        Com_Printf ("MAUTH: Client %s connection allowed.\n", Info_ValueForKey(userinfo, "name"));
    }
    else
    {
        Com_Printf("MAUTH: loopback or disabled; allowing client connection.\n");
    }
#endif

	adr = net_from;

	// if there is already a slot for this ip, reuse it
	for (i = 0, cl = svs.clients; i < MAX_CLIENTS; i++, cl++)
	{
		if (cl->state == cs_free)
			continue;
		if (NET_CompareBaseAdr (adr, cl->netchan.remote_address)
			&& ( cl->netchan.qport == qport 
			|| adr.port == cl->netchan.remote_address.port ))
		{
			if (cl->state == cs_connected) {
				Com_Printf ("%s:dup connect\n", NET_AdrToString (adr));
				return;
			}

			Com_Printf ("%s:reconnect\n", NET_AdrToString (adr));
			if (cl->state == cs_spawned)
			{
				SV_DropClient (cl);
				SV_ClearReliable (cl);	// don't send the disconnect
			}
			cl->state = cs_free;
			break;
		}
	}

	// count up the clients and spectators and find an empty client slot
	clients = spectators = 0;
	newcl = NULL;
	for (i = 0, cl = svs.clients; i < MAX_CLIENTS; i++,cl++)
	{
		if (cl->state == cs_free) {
			if (!newcl)
				newcl = cl;		// grab first available slot
			continue;
		}
		if (cl->spectator)
			spectators++;
		else
			clients++;
	}

	// if at server limits, refuse connection
	if ( (spectator && spectators >= (int)maxspectators.value)
		|| (!spectator && clients >= (int)maxclients.value)
		|| !newcl)
	{
		Com_Printf ("%s:full connect\n", NET_AdrToString (adr));
		Netchan_OutOfBandPrint (NS_SERVER, adr, "%c\nserver is full\n\n", A2C_PRINT);
		return;
	}

	// build a new connection
	// accept the new client
	// this is the only place a client_t is ever initialized
	memset (newcl, 0, sizeof(*newcl));
	newcl->userid = SV_GenerateUserID();

	strlcpy (newcl->userinfo, userinfo, sizeof(newcl->userinfo));

	Netchan_OutOfBandPrint (NS_SERVER, adr, "%c", S2C_CONNECTION );

	Netchan_Setup (NS_SERVER, &newcl->netchan, adr, qport);

	newcl->state = cs_connected;

	SZ_Init (&newcl->datagram, newcl->datagram_buf, sizeof(newcl->datagram_buf));
	newcl->datagram.allowoverflow = true;

	// spectator mode can ONLY be set at join time
	newcl->spectator = spectator;

	// extract extensions bits
	newcl->extensions = atoi(Info_ValueForKey(newcl->userinfo, "*z_ext"));
	Info_RemoveKey (newcl->userinfo, "*z_ext");

#ifdef VWEP_TEST
	newcl->extensions |= atoi(Info_ValueForKey(newcl->userinfo, "*vwtest")) ? Z_EXT_VWEP : 0;
	Info_RemoveKey (newcl->userinfo, "*vwtest");
#endif

	// See if the client is using a proxy. The best test I can come up with for now...
	newcl->uses_proxy = *Info_ValueForKey(newcl->userinfo, "Qizmo") ? true : false;

	edictnum = (newcl - svs.clients) + 1;
	ent = EDICT_NUM(edictnum);	
	ent->inuse = true;
	newcl->edict = ent;
	
	// parse some info from the info strings
	SV_ExtractFromUserinfo (newcl);

	// JACK: Init the floodprot stuff.
	for (i=0; i<10; i++)
		newcl->whensaid[i] = 0.0;
	newcl->whensaidhead = 0;
	newcl->lockedtill = 0;

	// call the progs to get default spawn parms for the new client
	PR_ExecuteProgram (PR_GLOBAL(SetNewParms));
	for (i=0 ; i<NUM_SPAWN_PARMS ; i++)
		newcl->spawn_parms[i] = (&PR_GLOBAL(parm1))[i];

	if (newcl->spectator)
		Com_Printf ("Spectator %s connected\n", newcl->name);
	else
		Com_DPrintf ("Client %s connected\n", newcl->name);

	newcl->sendinfo = true;
}

int Rcon_Validate (void)
{
	if (!strlen (sv_rconPassword.string))
		return 0;

	if (strcmp (Cmd_Argv(1), sv_rconPassword.string) )
		return 0;

	return 1;
}

/*
===============
SVC_RemoteCommand

A client issued an rcon command.
Shift down the remaining args
Redirect all printfs
===============
*/
void SVC_RemoteCommand (void)
{
	if (!Rcon_Validate ()) {
		Com_Printf ("Bad rcon from %s:\n%s\n", NET_AdrToString (net_from), net_message.data+4);

		SV_BeginRedirect (RD_PACKET);
		Com_Printf ("Bad rcon_password\n");
	}
	else {
		Com_Printf ("Rcon from %s:\n%s\n", NET_AdrToString (net_from), net_message.data+4);

		SV_BeginRedirect (RD_PACKET);
		Cmd_ExecuteString (Cmd_MakeArgs(2));
	}

	SV_EndRedirect ();
}


/*
=================
SV_ConnectionlessPacket

A connectionless packet has four leading 0xff
characters to distinguish it from a game channel.
Clients that are in the game can still send
connectionless packets.
=================
*/
void SV_ConnectionlessPacket (void)
{
	char	*s;
	char	*c;

	MSG_BeginReading ();
	MSG_ReadLong ();		// skip the -1 marker

	s = MSG_ReadStringLine ();
	s[1023] = 0;

	Cmd_TokenizeString (s);

	c = Cmd_Argv(0);

	if (!strcmp(c, "ping") || ( c[0] == A2A_PING && (c[1] == 0 || c[1] == '\n')) )
	{
		SVC_Ping ();
		return;
	}
	if (c[0] == A2A_ACK && (c[1] == 0 || c[1] == '\n') )
	{
		Com_Printf ("A2A_ACK from %s\n", NET_AdrToString (net_from));
		return;
	}
	else if (!strcmp(c,"status"))
	{
		SVC_Status ();
		return;
	}
	else if (!strcmp(c,"log"))
	{
		SVC_Log ();
		return;
	}
	else if (!strcmp(c,"connect"))
	{
		SVC_DirectConnect ();
		return;
	}
#ifdef MAUTH
	else if (!strcmp(c,M2S_AUTH_TOK))
	{
        // Provisionally add auth record...
        if (SV_AuthListAdd(&authtokq))
        {
            Com_Printf("MAUTH: Added token to auth queue (from %s)\n", NET_AdrToString(net_from));
            SV_AuthListPrint(&authtokq);
            SV_AuthListPrint(&authclientq);
            // Send S2M_AUTH_TOK_CHK as a spoofing check...
            Master_AuthTokChk(authtokq.start->name, authtokq.start->hash);
        }
        else
        {
            Com_Printf("MAUTH: Failure to add token -- already added? (from %s)\n", NET_AdrToString(net_from));
            // FIXME Send S2M_AUTH_TOK_NACK
        }
		return;
	}
	else if (!strcmp(c,M2S_AUTH_TOK_ACK))
	{
        // The master is sending us the correct name and hash;
        // check that what we've got agrees with this.

        // FIXME do we trust this packet?

        SV_AuthListValidate(&authtokq);
        SV_AuthListPrint(&authtokq);
        SV_AuthListPrint(&authclientq);
		return;
	}
    /*else if (!strcmp(c,M2S_AUTH_TOK_NACK))
    {
        // Master said this token not valid -- FIXME how can we trust this?
        // FIXME remove player details from auth queue.
    }*/
#endif
	else if (!strcmp(c,"getchallenge"))
	{
		SVC_GetChallenge ();
		return;
	}
	else if (!strcmp(c, "rcon"))
		SVC_RemoteCommand ();
	else
		Com_Printf ("bad connectionless packet from %s:\n%s\n"
		, NET_AdrToString (net_from), s);
}

/*
==============================================================================

PACKET FILTERING
 

You can add or remove addresses from the filter list with:

addip <ip>
removeip <ip>

The ip address is specified in dot format, and any unspecified digits will match any value, so you can specify an entire class C network with "addip 192.246.40".

Removeip will only remove an address specified exactly the same way.  You cannot addip a subnet, then removeip a single host.

listip
Prints the current list of filters.

writeip
Dumps "addip <ip>" commands to listip.cfg so it can be execed at a later date.  The filter lists are not saved and restored by default, because I beleive it would cause too much confusion.

filterban <0 or 1>

If 1 (the default), then ip addresses matching the current list will be prohibited from entering the game.  This is the default setting.

If 0, then only addresses matching the list will be allowed.  This lets you easily set up a private game, or a game that only allows players from your local network.


==============================================================================
*/


typedef struct
{
	unsigned	mask;
	unsigned	compare;
} ipfilter_t;

#define	MAX_IPFILTERS	1024

ipfilter_t	ipfilters[MAX_IPFILTERS];
int			numipfilters;

cvar_t	filterban = {"filterban", "1"};

/*
=================
StringToFilter
=================
*/
qbool StringToFilter (char *s, ipfilter_t *f)
{
	char	num[128];
	int		i, j;
	byte	b[4];
	byte	m[4];
	
	for (i=0 ; i<4 ; i++)
	{
		b[i] = 0;
		m[i] = 0;
	}
	
	for (i=0 ; i<4 ; i++)
	{
		if ( !isdigit((int)(unsigned char)*s) )
		{
			Com_Printf ("Bad filter address: %s\n", s);
			return false;
		}

		for (j = 0;  isdigit((int)(unsigned char)*s); s++)
		{
			if (j + 1 < sizeof(num))
				num[j++] = *s;
		}
		num[j] = 0;
		b[i] = atoi(num);
		if (b[i] != 0)
			m[i] = 255;

		if (!*s)
			break;
		s++;
	}
	
	f->mask = *(unsigned *)m;
	f->compare = *(unsigned *)b;
	
	return true;
}

/*
=================
SV_AddIP_f
=================
*/
void SV_AddIP_f (void)
{
	int		i;
	
	for (i=0 ; i<numipfilters ; i++)
		if (ipfilters[i].compare == 0xffffffff)
			break;		// free spot
	if (i == numipfilters)
	{
		if (numipfilters == MAX_IPFILTERS)
		{
			Com_Printf ("IP filter list is full\n");
			return;
		}
		numipfilters++;
	}
	
	if (!StringToFilter (Cmd_Argv(1), &ipfilters[i]))
		ipfilters[i].compare = 0xffffffff;
}

/*
=================
SV_RemoveIP_f
=================
*/
void SV_RemoveIP_f (void)
{
	ipfilter_t	f;
	int			i, j;

	if (!StringToFilter (Cmd_Argv(1), &f))
		return;
	for (i=0 ; i<numipfilters ; i++)
		if (ipfilters[i].mask == f.mask
		&& ipfilters[i].compare == f.compare)
		{
			for (j=i+1 ; j<numipfilters ; j++)
				ipfilters[j-1] = ipfilters[j];
			numipfilters--;
			Com_Printf ("Removed.\n");
			return;
		}
	Com_Printf ("Didn't find %s.\n", Cmd_Argv(1));
}

/*
=================
SV_ListIP_f
=================
*/
void SV_ListIP_f (void)
{
	int		i;
	byte	b[4];

	Com_Printf ("Filter list:\n");
	for (i=0 ; i<numipfilters ; i++)
	{
		*(unsigned *)b = ipfilters[i].compare;
		Com_Printf ("%3i.%3i.%3i.%3i\n", b[0], b[1], b[2], b[3]);
	}
}

/*
=================
SV_WriteIP_f
=================
*/
void SV_WriteIP_f (void)
{
	FILE	*f;
	char	name[MAX_OSPATH];
	byte	b[4];
	int		i;

	sprintf (name, "%s/listip.cfg", com_gamedir);

	Com_Printf ("Writing %s.\n", name);

	f = fopen (name, "wb");
	if (!f)
	{
		Com_Printf ("Couldn't open %s\n", name);
		return;
	}
	
	for (i=0 ; i<numipfilters ; i++)
	{
		*(unsigned *)b = ipfilters[i].compare;
		fprintf (f, "addip %i.%i.%i.%i\n", b[0], b[1], b[2], b[3]);
	}
	
	fclose (f);
}

/*
=================
SV_SendBan
=================
*/
void SV_SendBan (void)
{
	char		data[128];

	data[0] = data[1] = data[2] = data[3] = 0xff;
	data[4] = A2C_PRINT;
	data[5] = 0;
	strcat (data, "\nbanned.\n");
	
	NET_SendPacket (NS_SERVER, strlen(data), data, net_from);
}

/*
=================
SV_FilterPacket

Returns true if net_from.ip is banned
=================
*/
qbool SV_FilterPacket (void)
{
	int		i;
	unsigned	in;

	if (net_from.type == NA_LOOPBACK)
		return false;	// the local client can't be banned
	
	in = *(unsigned *)net_from.ip;

	for (i=0 ; i<numipfilters ; i++)
		if ( (in & ipfilters[i].mask) == ipfilters[i].compare)
			return filterban.value;

	return !filterban.value;
}

//============================================================================

/*
=================
SV_ReadPackets
=================
*/
void SV_ReadPackets (void)
{
	int			i;
	client_t	*cl;
	int			qport;

	// first deal with delayed packets from connected clients
	for (i = 0, cl=svs.clients; i < MAX_CLIENTS; i++, cl++) {
		if (cl->state == cs_free)
			continue;

		net_from = cl->netchan.remote_address;

		while (cl->packets && svs.realtime - cl->packets->time >= cl->delay) {
			SZ_Clear(&net_message);
			SZ_Write(&net_message, cl->packets->msg.data, cl->packets->msg.cursize);
			SV_ExecuteClientMessage(cl);
			SV_FreeHeadDelayedPacket(cl);
		}		
	}

	// now deal with new packets
	while (NET_GetPacket(NS_SERVER))
	{
		if (SV_FilterPacket ())
		{
			SV_SendBan ();	// tell them we aren't listening...
			continue;
		}

		// check for connectionless packet (0xffffffff) first
		if (*(int *)net_message.data == -1)
		{
			SV_ConnectionlessPacket ();
			continue;
		}
		
		// read the qport out of the message so we can fix up
		// stupid address translating routers
		MSG_BeginReading ();
		MSG_ReadLong ();		// sequence number
		MSG_ReadLong ();		// sequence number
		qport = MSG_ReadShort () & 0xffff;

		// check which client sent this packet
		for (i=0, cl=svs.clients ; i<MAX_CLIENTS ; i++,cl++)
		{
			if (cl->state == cs_free)
				continue;
			if (!NET_CompareBaseAdr (net_from, cl->netchan.remote_address))
				continue;
			if (cl->netchan.qport != qport)
				continue;
			if (cl->netchan.remote_address.port != net_from.port)
			{
				Com_DPrintf ("SV_ReadPackets: fixing up a translated port\n");
				cl->netchan.remote_address.port = net_from.port;
			}

			break;
		}

		if (i == MAX_CLIENTS)
			continue;

		// ok, we know who sent this packet, but do we need to delay executing it?
		if (cl->delay > 0) {
			if (!svs.free_packets) // packet has to be dropped..
				break;

			// insert at end of list
			if (!cl->packets) {
				cl->last_packet = cl->packets = svs.free_packets;
			} else {
				// this works because '=' associates from right to left
				cl->last_packet = cl->last_packet->next = svs.free_packets;
			}

			svs.free_packets = svs.free_packets->next;
			cl->last_packet->next = NULL;
			
			cl->last_packet->time = svs.realtime;
			SZ_Clear(&cl->last_packet->msg);
			SZ_Write(&cl->last_packet->msg, net_message.data, net_message.cursize);
		} else {
			SV_ExecuteClientMessage (cl);
		}
	}
}


/*
==================
SV_CheckTimeouts

If a packet has not been received from a client in timeout.value
seconds, drop the conneciton.

When a client is normally dropped, the client_t goes into a zombie state
for a few seconds to make sure any final reliable message gets resent
if necessary
==================
*/
void SV_CheckTimeouts (void)
{
	int		i;
	client_t	*cl;
	float	droptime;
	int	nclients;
	
	droptime = curtime - sv_timeout.value;
	nclients = 0;

	for (i=0,cl=svs.clients ; i<MAX_CLIENTS ; i++,cl++)
	{
		if (cl->state == cs_connected || cl->state == cs_spawned) {
			if (!cl->spectator)
				nclients++;
			if (cl->netchan.last_received < droptime) {
				SV_BroadcastPrintf (PRINT_HIGH, "%s timed out\n", cl->name);
				SV_DropClient (cl); 
				cl->state = cs_free;	// don't bother with zombie state
			}
		}
		if (cl->state == cs_zombie && 
			svs.realtime - cl->connection_started > sv_zombietime.value)
		{
			cl->state = cs_free;	// can now be reused
		}
	}

	if (((int) sv_paused.value & 1) && !nclients) {
		// nobody left, unpause the server
		if (GE_ShouldPause) {
			pr_global_struct->time = sv.time;
			pr_global_struct->self = EDICT_TO_PROG(sv.edicts);
			G_FLOAT(OFS_PARM0) = 0 /* newstate = false */;
			PR_ExecuteProgram (GE_ShouldPause);
			if (!G_FLOAT(OFS_RETURN))
				return;		// progs said don't unpause
		}
		SV_TogglePause(false, "Pause released since no players are left.\n");
	}
}

/*
===================
SV_GetConsoleCommands

Add them exactly as if they had been typed at the console
===================
*/
void SV_GetConsoleCommands (void)
{
	char	*cmd;

	while (1)
	{
		cmd = Sys_ConsoleInput ();
		if (!cmd)
			break;
		Cbuf_AddText (cmd);
		Cbuf_AddText ("\n");
	}
}


/*
===================
SV_BoundRate
===================
*/
int SV_BoundRate (int rate)
{
	if (!rate)
		rate = 2500;

	if (sv_maxrate.value)
		rate = min(rate, sv_maxrate.value);
	else
		rate = min(rate, 10000);

	if (rate < 500)		// not less than 500 no matter what sv_maxrate is
		rate = 500;

	return rate;
}


/*
===================
SV_CheckVars

===================
*/
void SV_CheckVars (void)
{
	static char pw[MAX_INFO_STRING]="", spw[MAX_INFO_STRING]="";
	static float old_maxrate = 0;
	int			v;

// check password and spectator_password
	if (strcmp(sv_password.string, pw) ||
		strcmp(sv_spectatorPassword.string, spw))
	{
		strlcpy (pw, sv_password.string, sizeof(pw));
		strlcpy (spw, sv_spectatorPassword.string, sizeof(spw));
		Cvar_Set (&sv_password, pw);
		Cvar_Set (&sv_spectatorPassword, spw);
		
		v = 0;
		if (pw && pw[0] && strcmp(pw, "none"))
			v |= 1;
		if (spw && spw[0] && strcmp(spw, "none"))
			v |= 2;
		
		Com_DPrintf ("Updated needpass.\n");
		if (!v)
			Info_SetValueForKey (svs.info, "needpass", "", MAX_SERVERINFO_STRING);
		else
			Info_SetValueForKey (svs.info, "needpass", va("%i",v), MAX_SERVERINFO_STRING);
	}

// check sv_maxrate
	if (sv_maxrate.value != old_maxrate) {
		client_t	*cl;
		int			i;
		char		*val;

		old_maxrate = sv_maxrate.value;

		for (i=0, cl = svs.clients ; i<MAX_CLIENTS ; i++, cl++)
		{
			if (cl->state < cs_connected)
				continue;

			val = Info_ValueForKey (cl->userinfo, "rate");
			cl->netchan.rate = 1.0 / SV_BoundRate (atoi(val));
		}
	}
}


/*
==================
SV_TogglePause

'menu' is set when the player pauses the game by bringing up the menu
in single player games
==================
*/
void SV_TogglePause (qbool menu, const char *msg)
{
	int i;
	client_t *cl;
	int	newval;

	if (menu)
		newval = (int)sv_paused.value ^ 2;
	else
		newval = (int)sv_paused.value ^ 1;

	if (!sv_paused.value && newval)
		sv.pausedstart = curtime;
	Cvar_ForceSet (&sv_paused, va("%i", newval));

	if (msg && *msg)
		SV_BroadcastPrintf (PRINT_HIGH, "%s", msg);

	// send notification to all clients
	for (i=0, cl = svs.clients ; i<MAX_CLIENTS ; i++, cl++)
	{
		if (cl->state < cs_connected)
			continue;
		ClientReliableWrite_Begin (cl, svc_setpause);
		ClientReliableWrite_Byte (sv_paused.value ? 1 : 0);
		ClientReliableWrite_End ();

		cl->lastservertimeupdate = -99;	// force an update to be sent
	}
}


static void PausedTic (void)
{
	if (GE_PausedTic /* && pr_ext_enabled.zq_pause*/) {
		G_FLOAT(OFS_PARM0) = curtime - sv.pausedstart;
		PR_ExecuteProgram (GE_PausedTic);
	}
}

/*
==================
SV_Frame

==================
*/
void SV_Frame (double time)
{
	static double	start, end;

	start = Sys_DoubleTime ();
	svs.stats.idle += start - end;
	
// keep the random time dependent
	rand ();

// decide the simulation time
	if (!sv_paused.value)
	{
		// FIXME, would it be better to advance svs.realtime even when paused?
		svs.realtime += time;
		sv.time += time;
	}

// check timeouts
	SV_CheckTimeouts ();

// toggle the log buffer if full
	SV_CheckLog ();

// move autonomous things around if enough time has passed
	if (!sv_paused.value)
		SV_Physics ();
	else {
		PausedTic ();
		SV_RunBots ();	// just update network stuff, but don't run physics
	}

// get packets
	SV_ReadPackets ();

	if (dedicated)
	{
	// check for commands typed to the host
		SV_GetConsoleCommands ();
		
	// process console commands
		Cbuf_Execute ();
	}

	SV_CheckVars ();

// send messages back to the clients that had packets read this frame
	SV_SendClientMessages ();

// send a heartbeat to the master if needed
	Master_Heartbeat ();

// collect timing statistics
	end = Sys_DoubleTime ();
	svs.stats.active += end-start;
	if (++svs.stats.count == STATFRAMES)
	{
		svs.stats.latched_active = svs.stats.active;
		svs.stats.latched_idle = svs.stats.idle;
		svs.stats.latched_packets = svs.stats.packets;
		svs.stats.active = 0;
		svs.stats.idle = 0;
		svs.stats.packets = 0;
		svs.stats.count = 0;
	}
}

/*
===============
SV_InitLocal
===============
*/
void SV_InitLocal (void)
{
	int		i;
	extern cvar_t	sv_spectalk;
	extern cvar_t	sv_mapcheck;
	extern cvar_t	sv_minping;
	extern cvar_t	sv_maxpitch;
	extern cvar_t	sv_minpitch;
	extern cvar_t	sv_nailhack;
	extern cvar_t	sv_loadentfiles;
	extern cvar_t	sv_maxvelocity;
	extern cvar_t	sv_gravity;
	extern cvar_t	pm_stopspeed;
	extern cvar_t	pm_spectatormaxspeed;
	extern cvar_t	pm_accelerate;
	extern cvar_t	pm_airaccelerate;
	extern cvar_t	pm_wateraccelerate;
	extern cvar_t	pm_friction;
	extern cvar_t	pm_waterfriction;
	extern cvar_t	pm_bunnyspeedcap;
	extern cvar_t	pm_ktjump;
	extern cvar_t	pm_slidefix;
	extern cvar_t	pm_airstep;
	extern cvar_t	pm_pground;
	packet_t		*packet_freeblock;	// initialise delayed packet free block

	SV_InitOperatorCommands	();

	Cvar_Register (&sv_rconPassword);
	Cvar_Register (&sv_password);
	Cvar_Register (&sv_spectatorPassword);

	Cvar_Register (&sv_phs);
	Cvar_Register (&sv_paused);
	Cvar_Register (&sv_pausable);
	Cmd_AddLegacyCommand ("pausable", "sv_pausable");
	Cvar_Register (&sv_nailhack);
	Cvar_Register (&sv_maxrate);
	Cvar_Register (&sv_fastconnect);
	Cvar_Register (&sv_loadentfiles);
	if (!dedicated)
		sv_mintic.string = "0";		// a value of 0 will tie physics tics to screen updates
	Cvar_Register (&sv_mintic);
	Cvar_Register (&sv_maxtic);
	Cvar_Register (&sv_timeout);
	Cmd_AddLegacyCommand ("timeout", "sv_timeout");
	Cvar_Register (&sv_zombietime);
	Cmd_AddLegacyCommand ("zombietime", "sv_zombietime");
	Cvar_Register (&sv_spectalk);
	Cvar_Register (&sv_mapcheck);
	if (dedicated)
		Cvar_Register (&sv_minping);
	Cvar_Register (&sv_maxpitch);
	Cvar_Register (&sv_minpitch);

	Cvar_Register (&deathmatch);
	Cvar_Register (&teamplay);
	Cvar_Register (&skill);
	Cvar_Register (&coop);
	Cvar_Register (&fraglimit);
	Cvar_Register (&timelimit);
	Cvar_Register (&samelevel);
	Cvar_Register (&maxclients);
	Cvar_Register (&maxspectators);
	Cvar_Register (&hostname);
	Cvar_Register (&watervis);

	Cvar_Register (&sv_maxvelocity);
	Cvar_Register (&sv_gravity);
	Cvar_Register (&pm_stopspeed);
	Cvar_Register (&pm_maxspeed);
	Cvar_Register (&pm_spectatormaxspeed);
	Cvar_Register (&pm_accelerate);
	Cvar_Register (&pm_airaccelerate);
	Cvar_Register (&pm_wateraccelerate);
	Cvar_Register (&pm_friction);
	Cvar_Register (&pm_waterfriction);
	Cvar_Register (&pm_bunnyspeedcap);
	Cvar_Register (&pm_ktjump);
	Cvar_Register (&pm_slidefix);
	Cvar_Register (&pm_airstep);
	Cvar_Register (&pm_pground);

	Cvar_Register (&allow_download);
	Cvar_Register (&allow_download_skins);
	Cvar_Register (&allow_download_models);
	Cvar_Register (&allow_download_sounds);
	Cvar_Register (&allow_download_maps);
	Cvar_Register (&allow_download_pakmaps);
	Cvar_Register (&allow_download_gfx);
	Cvar_Register (&allow_download_other);

	Cvar_Register (&filterban);
	Cmd_AddCommand ("addip", SV_AddIP_f);
	Cmd_AddCommand ("removeip", SV_RemoveIP_f);
	Cmd_AddCommand ("listip", SV_ListIP_f);
	Cmd_AddCommand ("writeip", SV_WriteIP_f);

	for (i=1 ; i<MAX_MODELS ; i++)
		sprintf (localmodels[i], "*%i", i);

	Info_SetValueForStarKey (svs.info, "*version", va(PROGRAM " %s", VersionString()), MAX_SERVERINFO_STRING);
	Info_SetValueForStarKey (svs.info, "*z_ext", va("%i", SERVER_EXTENSIONS), MAX_SERVERINFO_STRING);
#ifdef VWEP_TEST
	Info_SetValueForStarKey (svs.info, "*vwtest", "1", MAX_SERVERINFO_STRING);
#endif

	if (strcmp(com_gamedirfile, "qw"))
		Info_SetValueForStarKey (svs.info, "*gamedir", com_gamedirfile, MAX_SERVERINFO_STRING);

	// init fraglog stuff
	svs.logsequence = 1;
	svs.logtime = svs.realtime;
	SZ_Init (&svs.log[0], svs.log_buf[0], sizeof(svs.log_buf[0]));
	svs.log[0].allowoverflow = true;

	SZ_Init (&svs.log[1], svs.log_buf[1], sizeof(svs.log_buf[1]));
	svs.log[1].allowoverflow = true;

	packet_freeblock = Hunk_AllocName(MAX_DELAYED_PACKETS * sizeof(packet_t), "delayed_packets");

	for (i = 0; i < MAX_DELAYED_PACKETS; i++) {
		SZ_Init (&packet_freeblock[i].msg, packet_freeblock[i].buf, sizeof(packet_freeblock[i].buf));
		packet_freeblock[i].next = &packet_freeblock[i + 1];
	}
	packet_freeblock[MAX_DELAYED_PACKETS - 1].next = NULL;
	svs.free_packets = &packet_freeblock[0];

#ifdef MAUTH
    // Set up queues for temporary auth tokens and auth'd clients...
    authtokq.maxlen = MAX_AUTH_TOK_QUEUE;
    authtokq.curlen = 0;
    authtokq.start = NULL;
    authclientq.maxlen = MAX_AUTH_CLIENT_QUEUE;
    authclientq.curlen = 0;
    authclientq.start = NULL;
#endif
}


//============================================================================

/*
=================
SV_ExtractFromUserinfo

Pull specific info from a newly changed userinfo string
into a more C freindly form.
=================
*/
void SV_ExtractFromUserinfo (client_t *cl)
{
	char	*val, *p, *q;
	int		i;
	client_t	*client;
	int		dupc = 1;
	char	newname[80];

	// name for C code
	val = Info_ValueForKey (cl->userinfo, "name");

	// trim user name
	strlcpy (newname, val, sizeof(newname));

	for (p = newname; (*p == ' ' || *p == '\r' || *p == '\n') && *p; p++)
		;

	if (p != newname && !*p) {
		//white space only
		strcpy(newname, "unnamed");
		p = newname;
	}

	if (p != newname && *p) {
		for (q = newname; *p; *q++ = *p++)
			;
		*q = 0;
	}
	for (p = newname + strlen(newname) - 1; p != newname && (*p == ' ' || *p == '\r' || *p == '\n') ; p--)
		;
	p[1] = 0;

	if (strcmp(val, newname)) {
		Info_SetValueForKey (cl->userinfo, "name", newname, MAX_INFO_STRING);
		val = Info_ValueForKey (cl->userinfo, "name");
	}

	if (!val[0] || !Q_stricmp(val, "console")) {
		Info_SetValueForKey (cl->userinfo, "name", "unnamed", MAX_INFO_STRING);
		val = Info_ValueForKey (cl->userinfo, "name");
	}

	// check to see if another user by the same name exists
	while (1) {
		for (i=0, client = svs.clients ; i<MAX_CLIENTS ; i++, client++) {
			if (client->state != cs_spawned || client == cl)
				continue;
			if (!Q_stricmp(client->name, val))
				break;
		}
		if (i != MAX_CLIENTS) { // dup name
			if (strlen(val) > sizeof(cl->name) - 1)
				val[sizeof(cl->name) - 4] = 0;
			p = val;

			if (val[0] == '(') {
				if (val[2] == ')')
					p = val + 3;
				else if (val[3] == ')')
					p = val + 4;
			}

			sprintf(newname, "(%d)%-.40s", dupc++, p);
			Info_SetValueForKey (cl->userinfo, "name", newname, MAX_INFO_STRING);
			val = Info_ValueForKey (cl->userinfo, "name");
		} else
			break;
	}
	
	if (strncmp(val, cl->name, strlen(cl->name))) {
		if (!sv_paused.value) {
			if (!cl->lastnametime || svs.realtime - cl->lastnametime > 5) {
				cl->lastnamecount = 0;
				cl->lastnametime = svs.realtime;
			} else if (cl->lastnamecount++ > 4) {
				SV_BroadcastPrintf (PRINT_HIGH, "%s was kicked for name spam\n", cl->name);
				SV_ClientPrintf (cl, PRINT_HIGH, "You were kicked from the game for name spamming\n");
				SV_DropClient (cl); 
				return;
			}
		}
				
		if (cl->state >= cs_spawned && !cl->spectator)
			SV_BroadcastPrintf (PRINT_HIGH, "%s changed name to %s\n", cl->name, val);
	}


	strlcpy (cl->name, val, sizeof(cl->name));

	// rate
	val = Info_ValueForKey (cl->userinfo, "rate");
	cl->netchan.rate = 1.0 / SV_BoundRate (atoi(val));

	// message level
	val = Info_ValueForKey (cl->userinfo, "msg");
	if (strlen(val))
	{
		cl->messagelevel = atoi(val);
	}

}


//============================================================================

/*
====================
SV_Init
====================
*/
void SV_Init (void)
{
	PR_Init ();
	SV_InitLocal ();

	if (dedicated)
		NET_ServerConfig (true);

	svs.last_heartbeat = -99999;		// send immediately
}
