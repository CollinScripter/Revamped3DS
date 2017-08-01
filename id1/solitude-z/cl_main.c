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
// cl_main.c  -- client main loop

#ifndef _WIN32
#include <arpa/inet.h> // htons
#endif
#include "quakedef.h"
#include "winquake.h"
#include "cdaudio.h"
#include "input.h"
#include "keys.h"
#include "menu.h"
#include "cl_sbar.h"
#include "sound.h"
#include "version.h"
#include "teamplay.h"


cvar_t	*cl_rconPassword;
cvar_t	cl_rconAddress = {"rcon_address", ""};
cvar_t	cl_timeout = {"cl_timeout", "60"};
cvar_t	cl_shownet = {"cl_shownet", "0"};	// can be 0, 1, or 2
cvar_t	cl_maxfps	= {"cl_maxfps", "0", CVAR_ARCHIVE};
cvar_t	cl_writecfg = {"cl_writecfg", "1"};
cvar_t	host_speeds = {"host_speeds","0"};			// set for running times
cvar_t  localid = {"localid", ""};
static qbool allowremotecmd = true;

// ZQuake cvars
cvar_t	cl_muzzleflash = {"cl_muzzleflash", "1"};
cvar_t	cl_demospeed = {"cl_demospeed", "1"};
cvar_t	cl_staticsounds = {"cl_staticSounds", "1"};
cvar_t	cl_nofake = {"cl_nofake", "2"};
cvar_t	cl_parseWhiteText = {"cl_parseWhiteText", "1"};
cvar_t	cl_filterdrawviewmodel = {"cl_filterdrawviewmodel", "0"};
cvar_t	cl_demoPingInterval = {"cl_demoPingInterval", "5"};
cvar_t	cl_chatsound = {"cl_chatsound", "1"};
cvar_t	cl_confirmquit = {"cl_confirmquit", "0", CVAR_INIT};
cvar_t	cl_fakename = {"cl_fakename", ""};
cvar_t	cl_useproxy = {"cl_useproxy", "1"};
cvar_t	default_fov = {"default_fov", "0"};
cvar_t	qizmo_dir = {"qizmo_dir", "qizmo"};
void OnChangeSkinForcing(cvar_t *var, char *str, qbool *cancel);
cvar_t	noskins = {"noskins", "0", 0, OnChangeSkinForcing};
cvar_t	allskins = {"allskins", "", 0, OnChangeSkinForcing};
cvar_t	baseskin = {"baseskin", "", 0, OnChangeSkinForcing};
cvar_t	teamskin = {"teamskin", "", 0, OnChangeSkinForcing};
cvar_t	enemyskin = {"enemyskin", "", 0, OnChangeSkinForcing};
cvar_t	cl_independentPhysics = {"cl_independentPhysics", "1"};
cvar_t	cl_physfps = {"cl_physfps", "0"};


//
// info mirrors
//
cvar_t	*password;
cvar_t	spectator = {"spectator", "", CVAR_USERINFO};
cvar_t	name = {"name", "player", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	team = {"team", "", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	topcolor = {"topcolor","0", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	bottomcolor = {"bottomcolor","0", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	skin = {"skin", "", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	rate = {"rate", "3500", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	msg = {"msg", "1", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	noaim = {"noaim", "", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	w_switch = {"w_switch", "", CVAR_ARCHIVE|CVAR_USERINFO};
cvar_t	b_switch = {"b_switch", "", CVAR_ARCHIVE|CVAR_USERINFO};


client_persistent_t	cls;
client_state_t		cl;

centity_t		cl_entities[MAX_CL_EDICTS];
efrag_t			cl_efrags[MAX_EFRAGS];
entity_t		cl_static_entities[MAX_STATIC_ENTITIES];
lightstyle_t	cl_lightstyle[MAX_LIGHTSTYLES];

// used to determine if an entity was present in the last or previous message
int				cl_entframecount;

double			connect_time = 0;		// for connection retransmits

static qbool	host_skipframe;			// used in demo playback

byte		*host_basepal;

int			fps_count;

// emodel and pmodel are encrypted to prevent llamas from easily hacking them
char emodel_name[] = { 'e'^0xe5, 'm'^0xe5, 'o'^0xe5, 'd'^0xe5, 'e'^0xe5, 'l'^0xe5, 0 };
char pmodel_name[] = { 'p'^0xe5, 'm'^0xe5, 'o'^0xe5, 'd'^0xe5, 'e'^0xe5, 'l'^0xe5, 0 };

static void simple_crypt (char *buf, int len)
{
	while (len--)
		*buf++ ^= 0xe5;
}

static void CL_FixupModelNames (void)
{
	simple_crypt (emodel_name, sizeof(emodel_name) - 1);
	simple_crypt (pmodel_name, sizeof(pmodel_name) - 1);
}

//============================================================================

void OnChangeSkinForcing(cvar_t *var, char *str, qbool *cancel)
{
	if (cl.teamfortress || (cl.fpd & FPD_NO_FORCE_SKIN))
		return;

	Cvar_Set (var, str);

	if (cls.state == ca_active)
		CL_UpdateSkins ();
}

//============================================================================

int CL_ClientState (void)
{
	return cls.state;
}

// just for sv_save.c
int CL_IntermissionRunning (void) { return cl.intermission; }
int CL_Stat_Monsters (void) { return cl.stats[STAT_MONSTERS]; }
int CL_Stat_TotalMonsters (void) { return cl.stats[STAT_TOTALMONSTERS]; }

/*
*/
void CL_GamedirChanged (void)
{
	if (dedicated || !cls.initialized)
		return;

	// free old data and load a new gfx.wad
	R_FlushPics ();

	// register the pics we need
	SCR_RegisterPics ();
	Sbar_RegisterPics ();
}

/*
==================
CL_UserinfoChanged

Cvar system calls this when a CVAR_USERINFO cvar changes
==================
*/
void CL_UserinfoChanged (char *key, char *string)
{
	char *s;

	s = TP_ParseFunChars (string, false);

	if (strcmp(s, Info_ValueForKey (cls.userinfo, key)))
	{
		Info_SetValueForKey (cls.userinfo, key, s, MAX_INFO_STRING);

		if (cls.state >= ca_connected)
		{
			MSG_WriteByte (&cls.netchan.message, clc_stringcmd);
			SZ_Print (&cls.netchan.message, va("setinfo \"%s\" \"%s\"\n", key, s));
		}
	}
}


/*
=======================
CL_SendConnectPacket

called by CL_Connect_f and CL_CheckResend
======================
*/
void CL_SendConnectPacket (void)
{
	char	data[2048];
	char	biguserinfo[MAX_INFO_STRING + 32];

	if (cls.state != ca_disconnected)
		return;

	connect_time = cls.realtime;	// for retransmit requests

	cls.qport = Cvar_Value("qport");

	// let the server know what extensions we support
	strcpy (biguserinfo, cls.userinfo);
	Info_SetValueForStarKey (biguserinfo, "*z_ext", va("%i", CLIENT_EXTENSIONS), sizeof(biguserinfo));

	sprintf (data, "\xff\xff\xff\xff" "connect %i %i %i \"%s\"\n",
		PROTOCOL_VERSION, cls.qport, cls.challenge, biguserinfo);
	NET_SendPacket (NS_CLIENT, strlen(data), data, cls.server_adr);
}

/*
=================
CL_CheckForResend

Resend a connect message if the last one has timed out
=================
*/
void CL_CheckForResend (void)
{
	char	data[2048];
	double t1, t2;

	if (cls.state == ca_disconnected && com_serveractive) {
		// if the local server is running and we are not, then connect
		cls.nqprotocol = false;
		strlcpy (cls.servername, "local", sizeof(cls.servername));
		NET_StringToAdr ("local", &cls.server_adr);
		CL_SendConnectPacket ();	// we don't need a challenge on the local server
		// FIXME: cls.state = ca_connecting so that we don't send the packet twice?
		return;
	}

	if (cls.state != ca_disconnected || !connect_time)
		return;
	if (cls.realtime - connect_time < 5.0)
		return;

	t1 = Sys_DoubleTime ();
	if (!NET_StringToAdr (cls.servername, &cls.server_adr))
	{
		Com_Printf ("Bad server address\n");
		connect_time = 0;
		return;
	}
	t2 = Sys_DoubleTime ();
	connect_time = cls.realtime + t2 - t1;	// for retransmit requests

	if (cls.server_adr.port == 0)
		cls.server_adr.port = BigShort (cls.nqprotocol ? 26000 : PORT_SERVER);

	Com_Printf ("Connecting to %s...\n", cls.servername);

	if (cls.nqprotocol) {
		memcpy (data, "\x80\x00\x00\x0C" "\x01" "QUAKE\x00" "\x03", 12);
		NET_SendPacket (NS_CLIENT, 12, data, cls.server_adr);
	}
	else {
		sprintf (data, "\xff\xff\xff\xff" "getchallenge\n");
		NET_SendPacket (NS_CLIENT, strlen(data), data, cls.server_adr);
	}
}

void CL_BeginServerConnect(void)
{
	connect_time = -999;	// CL_CheckForResend() will fire immediately
	CL_CheckForResend();
}

#ifndef MAUTH
/*
================
CL_Connect_f

================
*/
void CL_Connect_f (void)
{
	char	*server;

	if (Cmd_Argc() != 2)
	{
		Com_Printf ("usage: connect <server>\n");
		return;
	}
	
	server = Cmd_Argv (1);

	Host_EndGame ();

	cls.nqprotocol = false;
	strlcpy (cls.servername, server, sizeof(cls.servername));
	CL_BeginServerConnect();
}
#else // MAUTH
/*
================
CL_Connect_f

MAUTH version -- kick off an authentication sequence as first part of
connection routine.
================
*/
void CL_Connect_f (void)
{
	char	*server;
	char	*masterserver;
    char    data[2048];

	if (Cmd_Argc() != 3)
	{
		Com_Printf ("usage: connect <master> <server>\n");
		return;
	}
	
	Host_EndGame ();
	
    server = Cmd_Argv (1);
	strlcpy (cls.servername, server, sizeof(cls.servername));

    // Have to check for valid server address here as we must send to master...
	if (!NET_StringToAdr (cls.servername, &cls.server_adr))
	{
		Com_Printf ("Bad server address\n");
		return;
	}
	if (cls.server_adr.port == 0)
		cls.server_adr.port = BigShort (PORT_SERVER);

	masterserver = Cmd_Argv (2);
	strlcpy (cls.masterservername, masterserver, sizeof(cls.masterservername));

    // Start off auth sequence before trying to connect...
	if (!NET_StringToAdr (cls.masterservername, &cls.masterserver_adr))
	{
		Com_Printf ("Bad master server address\n");
		return;
	}
	if (cls.masterserver_adr.port == 0)
		cls.masterserver_adr.port = BigShort (27000);  // master port

	Com_Printf ("Attempting to auth with %s...\n", cls.masterservername);
	sprintf (data, "%c\n%s\n%s:%d\n",
            C2M_AUTH_INIT,
            Cvar_String("name"),
            cls.servername,
            cls.server_adr.port);
	NET_SendPacket (NS_CLIENT, strlen(data), data, cls.masterserver_adr);

    // Normal connection procedure...
    // FIXME wait?
    // FIXME use some qbools to work out if we get a NACK to stop trying to connect -- ie preserve state
	CL_BeginServerConnect();
}
#endif  // !MAUTH

void CL_NQConnect_f (void)
{
	char	*server;

	if (Cmd_Argc() != 2)
	{
		Com_Printf ("usage: nqconnect <server>\n");
		return;
	}
	
	server = Cmd_Argv (1);

	Host_EndGame ();

	cls.nqprotocol = true;
	strlcpy (cls.servername, server, sizeof(cls.servername));
	CL_BeginServerConnect();
}

/*
=====================
CL_Spawn

=====================
*/
void CL_Spawn (void)
{		
	// first update is the final signon stage
	cls.state = ca_active;

	if (cls.demoplayback)
		host_skipframe = true;

	if (!cls.demoplayback)
		VID_SetCaption (va(PROGRAM ": %s", cls.servername));

	Con_ClearNotify ();
	SCR_EndLoadingPlaque ();

	TP_ExecTrigger ("f_spawn");
}


/*
=====================
CL_ClearState

=====================
*/
void CL_ClearState (void)
{
	int			i;
	extern float	scr_centertime_off;

	S_StopAllSounds (true);

	Com_DPrintf ("Clearing memory\n");

	if (!com_serveractive)
	{
		Host_ClearMemory ();
	}

	CL_ClearTEnts ();
	CL_ClearDlights ();
	CL_ClearParticles ();
	CL_ClearNails ();

	for (i = 0; i < UPDATE_BACKUP; i++)
		Q_free (cl.frames[i].packet_entities.entities);

// wipe the entire cl structure
	memset (&cl, 0, sizeof(cl));

	SZ_Clear (&cls.netchan.message);

// clear other arrays	
	memset (cl_efrags, 0, sizeof(cl_efrags));
	memset (cl_lightstyle, 0, sizeof(cl_lightstyle));
	memset (cl_entities, 0, sizeof(cl_entities));

	cl_entframecount = 2;		// so that cl_entframecount - 1 != 0
	cl.viewheight = DEFAULT_VIEWHEIGHT;
	cl.minpitch = -70;
	cl.maxpitch = 80;

	V_NewMap ();

// make sure no centerprint messages are left from previous level
	scr_centertime_off = 0;

//
// allocate the efrags and chain together into a free list
//
	cl.free_efrags = cl_efrags;
	for (i=0 ; i<MAX_EFRAGS-1 ; i++)
		cl.free_efrags[i].entnext = &cl.free_efrags[i+1];
	cl.free_efrags[i].entnext = NULL;
}

/*
=====================
CL_Disconnect

Sends a disconnect message to the server
This is also called on Host_Error, so it shouldn't cause any errors
=====================
*/
void CL_Disconnect (void)
{
	byte	final[10];

	VID_SetCaption (PROGRAM);

	// stop sounds (especially looping!)
	S_StopAllSounds (true);
	
	Cmd_RemoveStuffedAliases ();

	cl.paused = 0;

	if (cls.demorecording && cls.state != ca_disconnected)
		CL_Stop_f ();

	if (cls.demoplayback)
	{
		CL_StopPlayback ();
	}
	else if (cls.state != ca_disconnected)
	{
		int size;
		if (cls.nqprotocol) {
			final[0] = 2 /* clc_disconnect */;
			Netchan_Transmit (&cls.netchan, 1, final);
			size = 1;
		} else {
			final[0] = clc_stringcmd;
			strcpy ((char *)(final+1), "drop");
			Netchan_Transmit (&cls.netchan, 6, final);
			size = 6;
		}
		// don't choke the loopback buffers
		if (cls.netchan.remote_address.type != NA_LOOPBACK)
		{
			Netchan_Transmit (&cls.netchan, size, final);
			Netchan_Transmit (&cls.netchan, size, final);
		}
	}

	Cam_Reset();

	if (cls.download) {
		fclose(cls.download);
		cls.download = NULL;
	}

	CL_StopUpload ();

	// don't accept any remote packets
	cls.server_adr = net_null;
	cls.netchan.remote_address = net_null;

	cls.state = ca_disconnected;
	connect_time = 0;
}

void CL_Disconnect_f (void)
{
	cl.intermission = 0;
	cls.playdemos = 0;	// stop demo loop
	Host_EndGame ();
}

void CL_HandleHostError (void)
{
	cls.playdemos = 0;	// stop demo loop
}

/*
=================
CL_Reconnect_f

The server is changing levels
=================
*/
void CL_Reconnect_f (void)
{
	if (cls.download)  // don't change when downloading
		return;

	S_StopAllSounds (true);

	if (cls.nqprotocol && cls.state >= ca_connected) {
		extern int nq_signon;
		cls.state = ca_connected;
		nq_signon = 0;
		return;
	};

	if (cls.state == ca_connected) {
		Com_Printf ("reconnecting...\n");
		MSG_WriteChar (&cls.netchan.message, clc_stringcmd);
		MSG_WriteString (&cls.netchan.message, "new");
		return;
	}

	if (!*cls.servername) {
		Com_Printf ("No server to reconnect to.\n");
		return;
	}

	CL_Disconnect();	// FIXME: replace with Host_EndGame?
	CL_BeginServerConnect();
}


extern double qstat_senttime;
extern void CL_PrintQStatReply (char *s);

/*
=================
CL_ConnectionlessPacket

Responses to broadcasts, etc
=================
*/
void CL_ConnectionlessPacket (void)
{
	char	*s;
	int		c;

	MSG_BeginReading ();
	MSG_ReadLong ();		// skip the -1

	c = MSG_ReadByte ();

	if (msg_badread)
		return;	// runt packet
    
#ifdef MAUTH
    // Deal with authentication messages...
    if (c == M2C_AUTH_RND)
    {
        char *tmpstr;
        char *hash_md4;
        char data[1024];

        // FIXME compute and send hash to master
        // FIXME ensure this is our master somehow?
        // FIXME malformed packets shouldn't crash server

        MSG_ReadStringLine();
        
        // Check player name...
        tmpstr = MSG_ReadStringLine();
        if( !tmpstr || strcmp(Cvar_String("name"),tmpstr) )
        {
            // FIXME return NACK
            return;
        }
        
        // Show random string...
        tmpstr = MSG_ReadString();
        if( !tmpstr )
        {
            // FIXME return NACK
            return;
        }
        Sys_Printf("MAUTH: random string is %s.\n", tmpstr);

        // Compute hash with Com_BlockFullChecksum() from name + rnd...
        strcat(tmpstr,"mp2");
        Com_BlockFullChecksum(tmpstr,sizeof(tmpstr),hash_md4);
        Sys_Printf("MAUTH: str is %s.\n", tmpstr);
        Sys_Printf("MAUTH: str size is %d.\n", sizeof(tmpstr));
        Sys_Printf("MAUTH: hash is %s.\n", hash_md4);
        Sys_Printf("MAUTH: hash size is %d.\n", sizeof(hash_md4));
        
        // Send hash to master...
        sprintf(data, "%c\n%s\n%s\n", C2M_AUTH_HASH, Cvar_String("name"), hash_md4);
		NET_SendPacket (NS_CLIENT, sizeof(data), data, net_from);
        return;
    }
#endif

	// remote command from GUI frontend
	if (c == A2C_CLIENT_COMMAND) {
		char	cmdtext[2048];

		Com_Printf ("%s: client command\n", NET_AdrToString(net_from));

		if (!NET_IsLocalAddress(net_from))
		{
			Com_Printf ("Command packet from remote host.  Ignored.\n");
			return;
		}

#ifdef _WIN32
		ShowWindow (mainwindow, SW_RESTORE);
		SetForegroundWindow (mainwindow);
#endif

		s = MSG_ReadString ();
		strlcpy (cmdtext, s, sizeof(cmdtext));

		s = MSG_ReadString ();

		while (*s && isspace((int)(unsigned char)*s))
			s++;
		while (*s && isspace((int)(unsigned char)s[strlen(s) - 1]))
			s[strlen(s) - 1] = 0;

		if (!allowremotecmd && (!*localid.string || strcmp(localid.string, s))) {
			if (!*localid.string) {
				Com_Printf ("===========================\n");
				Com_Printf ("Command packet received from local host, but no "
					"localid has been set.  You may need to upgrade your server "
					"browser.\n");
				Com_Printf ("===========================\n");
				return;
			}
			Com_Printf ("===========================\n");
			Com_Printf ("Invalid localid on command packet received from local host. "
				"\n|%s| != |%s|\n"
				"You may need to reload your server browser and QuakeWorld.\n",
				s, localid.string);
			Com_Printf ("===========================\n");
			Cvar_Set(&localid, "");
			return;
		}

		Cbuf_AddText (cmdtext);
		Cbuf_AddText ("\n");
		allowremotecmd = false;
		return;
	}

	// print command from somewhere
	if (c == A2C_PRINT) {
		if (net_message.data[msg_readcount] == '\\') {
			if (qstat_senttime && curtime - qstat_senttime < 10) {
				CL_PrintQStatReply (MSG_ReadString());
				return;
			}
		}

		Com_Printf ("%s: print\n", NET_AdrToString(net_from));

		s = MSG_ReadString ();
		Com_Printf ("%s", s);
		return;
	}

	// only allow packets from the server we connected to
	// (except for A2C_CLIENT_COMMAND and A2C_PRINT which are processed earlier)
	if (!cls.demoplayback && !NET_CompareAdr(net_from, cls.server_adr))
		return;

	if (c == S2C_CHALLENGE) {
		Com_Printf ("%s: challenge\n", NET_AdrToString(net_from));

		s = MSG_ReadString ();
		cls.challenge = atoi(s);
		CL_SendConnectPacket ();
		return;
	}

	if (c == S2C_CONNECTION) {
		if (!com_serveractive || developer.value)
			Com_Printf ("%s: connection\n", NET_AdrToString(net_from));
		if (cls.state >= ca_connected)
		{
			if (!cls.demoplayback)
				Com_Printf ("Dup connect received.  Ignored.\n");
			return;
		}
		Netchan_Setup (NS_CLIENT, &cls.netchan, net_from, cls.qport);
		MSG_WriteChar (&cls.netchan.message, clc_stringcmd);
		MSG_WriteString (&cls.netchan.message, "new");	
		cls.state = ca_connected;
		if (!com_serveractive || developer.value)
			Com_Printf ("Connected.\n");
		allowremotecmd = false; // localid required now for remote cmds
		return;
	}

	// ping from somewhere
	if (c == A2A_PING) {
		char	data[6];

		Com_Printf ("%s: ping\n", NET_AdrToString(net_from));

		data[0] = 0xff;
		data[1] = 0xff;
		data[2] = 0xff;
		data[3] = 0xff;
		data[4] = A2A_ACK;
		data[5] = 0;
		
		NET_SendPacket (NS_CLIENT, sizeof(data), data, net_from);
		return;
	}

	if (c == svc_disconnect) {
		if (cls.demoplayback) {
			Com_Printf ("\n======== End of demo ========\n\n");
			CL_NextDemo ();
			Host_EndGame ();
			Host_Abort ();
		}
		return;
	}

	Com_Printf ("Bad connectionless command: 0x%X\n", c);
}

#define NETFLAG_CTL			0x80000000
#define NETFLAG_LENGTH_MASK	0x0000ffff
#define CCREP_ACCEPT		0x81
#define CCREP_REJECT		0x82

void CLNQ_ConnectionlessPacket(void)
{
	char *s;
	int length;

	MSG_BeginReading ();
	length = LongSwap(MSG_ReadLong ());
	if (!(length & NETFLAG_CTL))
		return;	//not an nq control packet.
	length &= NETFLAG_LENGTH_MASK;
	if (length != net_message.cursize)
		return;	//not an nq packet.

	switch(MSG_ReadByte())
	{
	case CCREP_ACCEPT:
		if (cls.state >= ca_connected)
		{
//			if (cls.demoplayback == DPB_NONE)
//				Con_TPrintf (TLC_DUPCONNECTION);
			return;
		}
		net_from.port = htons((short)MSG_ReadLong());

		Netchan_Setup (NS_CLIENT, &cls.netchan, net_from, cls.qport);
		cls.netchan.nqprotocol = true;
		cls.state = ca_connected;

		//send a dummy packet.
		//this makes our local nat think we initialised the conversation.
		NET_SendPacket(NS_CLIENT, 0, "", net_from);
		return;

	case CCREP_REJECT:
		s = MSG_ReadString();
		Com_Printf("Connect failed\n%s\n", s);
		return;
	}
}

extern void CheckQizmoCompletion ();

/*
====================
CL_GetMessage

Handles playback of demos, on top of NET_ code
====================
*/
qbool CL_GetMessage (void)
{
#ifdef _WIN32
	CheckQizmoCompletion ();
#endif

	if (cls.demoplayback)
		return CL_GetDemoMessage ();

	if (!NET_GetPacket(NS_CLIENT))
		return false;

	return true;
}


/*
=================
CL_ReadPackets
=================
*/
void CL_ReadPackets (void)
{
	if (cls.nqprotocol && cls.demoplayback) {
		NQD_ReadPackets ();
		return;
	}

#ifdef MVDPLAY
	if (cls.mvdplayback) {
		while (CL_GetMessage())
		{
			MSG_BeginReading();
			CL_ParseServerMessage ();
		}
		return;
	}
#endif

	while (CL_GetMessage())
	{
		if (cls.nqprotocol && cls.state == ca_disconnected)
		{	//connect to nq servers, but don't get confused with sequenced packets.
			CLNQ_ConnectionlessPacket ();
			continue;	//ignore it. We arn't connected.
		}

		if (cls.nqprotocol) {
			switch(NQNetchan_Process(&cls.netchan))
			{
			case 0:
				break;
			case 1://datagram
				cls.netchan.incoming_sequence = cls.netchan.outgoing_sequence - 3;
				/* fall through */
			case 2://reliable
				CLNQ_ParseServerMessage ();
				break;
			}
			continue;
		}

		//
		// remote command packet
		//
		if (*(int *)net_message.data == -1)
		{
			CL_ConnectionlessPacket ();
			continue;
		}

		if (net_message.cursize < 8)
		{
			Com_DPrintf ("%s: Runt packet\n", NET_AdrToString(net_from));
			continue;
		}

		//
		// packet from server
		//
		if (!cls.demoplayback && 
			!NET_CompareAdr (net_from, cls.netchan.remote_address))
		{
			Com_DPrintf ("%s: sequenced packet without connection\n"
				,NET_AdrToString(net_from));
			continue;
		}
		if (!Netchan_Process(&cls.netchan))
			continue;		// wasn't accepted for some reason
		CL_ParseServerMessage ();
	}

	//
	// check timeout
	//
	if (!cls.demoplayback && cls.state >= ca_connected && curtime - cls.netchan.last_received > cl_timeout.value)
	{
		Com_Printf ("\nServer connection timed out.\n");
		Host_EndGame ();
		return;
	}
	
}


void CL_SendToServer (void)
{
	// when recording demos, request new ping times every 5 seconds
	if (cls.demorecording && !cls.demoplayback && cls.state == ca_active
		&& cl_demoPingInterval.value > 0) {
		if (cls.realtime - cl.last_ping_request > cl_demoPingInterval.value)
		{
			cl.last_ping_request = cls.realtime;
			MSG_WriteByte (&cls.netchan.message, clc_stringcmd);
			SZ_Print (&cls.netchan.message, "pings");
		}
	}

	// send intentions now
	// resend a connection request if necessary
	if (cls.state == ca_disconnected) {
		CL_CheckForResend ();
	} else
		CL_SendCmd ();
}

// this is callback from VID after a vid_restart
void CL_ReloadTextures (void)
{
	int i;

	// register the pics we need
	SCR_RegisterPics ();
	Sbar_RegisterPics ();

	if (cls.state == ca_active) {
		for (i = 1; i < MAX_MODELS; i++)
		{
			if (!cl.model_name[i][0])
				break;
			R_LoadModelTextures (cl.model_precache[i]);
		}
	}
}

//=============================================================================

void CL_InitCommands (void);

void CL_InitLocal (void)
{
	Cvar_Register (&host_speeds);

	Cvar_Register (&cl_warncmd);
	Cvar_Register (&cl_shownet);
	Cvar_Register (&cl_maxfps);
	Cvar_Register (&cl_timeout);
	Cvar_Register (&cl_writecfg);

	cl_rconPassword = Cvar_Get ("rcon_password", "", 0);
	Cvar_Register (&cl_rconAddress);

	Cvar_Register (&localid);

	Cvar_Register (&noskins);
	Cvar_Register (&allskins);
	Cvar_Register (&baseskin);
	Cvar_Register (&teamskin);
	Cvar_Register (&enemyskin);

	// ZQuake cvars
	Cvar_Register (&cl_demospeed);
	Cmd_AddLegacyCommand ("demotimescale", "cl_demospeed");
	Cvar_Register (&cl_muzzleflash);
	Cvar_Register (&cl_staticsounds);
	Cvar_Register (&cl_nofake);
	Cvar_Register (&cl_parseWhiteText);
	Cvar_Register (&cl_filterdrawviewmodel);
	Cvar_Register (&cl_demoPingInterval);
	Cvar_Register (&cl_chatsound);
	Cvar_Register (&cl_confirmquit);
	Cvar_Register (&cl_fakename);
	Cvar_Register (&cl_useproxy);
	Cvar_Register (&default_fov);
	Cvar_Register (&qizmo_dir);
	Cvar_Register (&cl_independentPhysics);
	Cvar_Register (&cl_physfps);

#ifndef RELEASE_VERSION
	// inform everyone that we're using a development version
//	Info_SetValueForStarKey (cls.userinfo, "*ver", va(PROGRAM " %s", VersionString()), MAX_INFO_STRING);
#endif

#ifdef VWEP_TEST
	Info_SetValueForStarKey (cls.userinfo, "*vwtest", "1", MAX_INFO_STRING);
#endif

	//
	// info mirrors
	//
	password = Cvar_Get ("password", "",  CVAR_USERINFO);
	Cvar_Register (&spectator);
	Cvar_Register (&name);
	Cvar_Register (&team);
	Cvar_Register (&topcolor);
	Cvar_Register (&bottomcolor);
	Cvar_Register (&skin);
	Cvar_Register (&rate);
	Cvar_Register (&msg);
	Cvar_Register (&noaim);
	Cvar_Register (&w_switch);
	Cvar_Register (&b_switch);

	CL_InitCommands ();

	Cmd_AddCommand ("disconnect", CL_Disconnect_f);
	Cmd_AddCommand ("connect", CL_Connect_f);
	Cmd_AddCommand ("nqconnect", CL_NQConnect_f);
	Cmd_AddCommand ("reconnect", CL_Reconnect_f);
}

static void CL_CheckGfxWad (void)
{
	FILE *f;
	FS_FOpenFile ("gfx.wad", &f);
	if (!f) {
		Sys_Error ("Couldn't find gfx.wad.\n"
			"Make sure you start " PROGRAM
			" from your Quake directory or use -basedir <path>");
	}
	fclose (f);
}

/*
=================
CL_Init
=================
*/
void CL_Init (void)
{
	if (dedicated)
		return;

	cls.state = ca_disconnected;

	strcpy (cls.gamedirfile, com_gamedirfile);
	strcpy (cls.gamedir, com_gamedir);

	CL_CheckGfxWad ();

	host_basepal = (byte *)FS_LoadHunkFile ("gfx/palette.lmp");
	if (!host_basepal)
		Sys_Error ("Couldn't load gfx/palette.lmp");

	Sys_mkdir(va("%s/%s", com_basedir, "qw"));

	V_Init ();

#ifdef __linux__
	IN_Init ();
#endif

	VID_Init (host_basepal);

#ifndef __linux__
	IN_Init ();
#endif


	R_Init (host_basepal);

	S_Init ();
	CDAudio_Init ();

	CL_InitLocal ();
	CL_FixupModelNames ();
	CL_InitInput ();
	CL_InitTEnts ();
	CL_InitPrediction ();
	CL_InitCam ();
	CL_InitParticles ();
	CL_Ents_Init ();
	TP_Init ();
	SCR_Init ();
	Sbar_Init ();
	M_Init ();

	NET_ClientConfig (true);

#if 0
	// bring up the main menu
	M_Menu_Main_f ();
#endif

	cls.initialized = true;
}


//============================================================================

void CL_BeginLocalConnection (void)
{
	S_StopAllSounds (true);
	SCR_BeginLoadingPlaque ();

	if (com_serveractive)
	{
		if (cls.state == ca_active)
			cls.state = ca_connected;
	}
	else
	{
		// make sure we're not connected to an external server,
		// and demo playback is stopped
		CL_Disconnect ();
	}
}


extern void SV_TogglePause (qbool menu, const char *msg);
extern cvar_t sv_paused;

// automatically pause the game when going into the menus in single player
static void CL_CheckAutoPause (void)
{
#ifndef CLIENTONLY
	if (com_serveractive && cls.state == ca_active && !cl.deathmatch && cl.maxclients == 1
		&& (key_dest == key_menu /*|| key_dest == key_console*/))
	{
		if (!((int)sv_paused.value & 2))
			SV_TogglePause (true, NULL);
	}
	else {
		if ((int)sv_paused.value & 2)
			SV_TogglePause (true, NULL);
	}
#endif
}


/*
===================
CL_MinFrameTime

Can't run a frame if enough time hasn't passed
===================
*/
static double CL_MinFrameTime ()
{
	double fps, fpscap;

	if (cls.timedemo)
		return 0;

	if (cls.demoplayback) {
		if (!cl_maxfps.value)
			return 0;
		fps = max (30.0, cl_maxfps.value);
	}
	else {
		if (cl_independentPhysics.value) 
			fps = cl_maxfps.value ? max(cl_maxfps.value, 30) : 999999;
		else {
			fpscap = cl.maxfps ? max (30.0, cl.maxfps) : 72.0;

			if (cl_maxfps.value)
				fps = bound (30.0, cl_maxfps.value, fpscap);
			else
			{
				if (com_serveractive)
					fps = fpscap;
				else
					fps = bound (30.0, rate.value/80.0, fpscap);
			}
		}
	}

	return 1.0/fps;
}

static double MinPhysFrameTime ()
{
	// server policy
	float fpscap = (cl.maxfps ? cl.maxfps : 72.0);

	// the user can lower it for testing
	if (cl_physfps.value)
		fpscap = min(fpscap, cl_physfps.value);

	// not less than this no matter what
	fpscap = max(fpscap, 10);

	return 1 / fpscap;
}

/*
==================
CL_Frame

==================
*/
void CL_Frame (double time)
{
	double		time1 = 0.0, time2 = 0.0;
	static double	time3 = 0.0;
	int		pass1, pass2, pass3;
	static double	extratime = 0.001;
	double		minframetime;
	static double	extraphysframetime;

	extratime += time;

	minframetime = CL_MinFrameTime();
	if (extratime < minframetime)
		return;

	cls.trueframetime = extratime - 0.001;
	if (cls.trueframetime < minframetime)
		cls.trueframetime = minframetime;
	extratime -= cls.trueframetime;

	cls.frametime = min (cls.trueframetime, 0.2);

	if (cl_independentPhysics.value && !cls.demoplayback) 
	{
		double minphysframetime = MinPhysFrameTime();

		extraphysframetime += cls.frametime;
		if (extraphysframetime < minphysframetime)
			cls.physframe = false;
		else 
		{
			cls.physframe = true;

			if (extraphysframetime > minphysframetime*2)// FIXME: this is for the case when
				cls.physframetime = extraphysframetime;		// actual fps is too low
			else										// Dunno how to do it right
				cls.physframetime = minphysframetime;
			extraphysframetime -= cls.physframetime;
		}	
	} else {
		extraphysframetime = 0;
		cls.physframe = true;
	}

	if (cls.demoplayback) {
		cls.frametime *= bound (0, cl_demospeed.value, 100);
		if (cl.paused & PAUSED_DEMO)
			cls.frametime = 0;
		if (!host_skipframe)
			cls.demotime += cls.frametime;
		host_skipframe = false;
	}

	cls.realtime += cls.frametime;		// go on even if paused (dunno why...)

	if (cl.paused)
		cls.frametime = 0;

	cl.time += cls.frametime;
	cl.servertime += cls.frametime;
	cl.stats[STAT_TIME] = cl.servertime * 1000;	// for demos' sake

if (cls.physframe)
{
	// get new key events
	Sys_SendKeyEvents ();

	// allow mice or other external controllers to add commands
	IN_Commands ();

	// process console commands
	Cbuf_Execute ();
	CL_CheckAutoPause ();

	// if running a local server, send the move command now
//	if (com_serveractive && !cls.demorecording)
//		CL_SendToServer ();

	if (com_serveractive)
		SV_Frame (cls.physframetime);

	// fetch results from server
	CL_ReadPackets ();

#ifdef MVDPLAY
	if (cls.mvdplayback)
		MVD_Interpolate ();
#endif

	// process stuffed commands
	Cbuf_ExecuteEx (&cbuf_svc);

//	if (!(com_serveractive && !cls.demorecording))
		CL_SendToServer ();
}
else {
	usercmd_t dummy;
	IN_Move (&dummy);
	CL_AdjustAngles ();
}

	// predict all players
	CL_PredictMovement ();

	// build a refresh entity list
	CL_EmitEntities ();

	// update video
	if (host_speeds.value)
		time1 = Sys_DoubleTime ();

	SCR_RunConsole ();
	SCR_UpdateScreen ();

	if (host_speeds.value)
		time2 = Sys_DoubleTime ();

	// update audio
	if (cls.state == ca_active) {
		vec3_t forward, right, up;
		AngleVectors (r_refdef2.viewangles, forward, right, up);
		S_Update (r_refdef2.vieworg, forward, right, up);
	}
	else
		S_Update (vec3_origin, vec3_origin, vec3_origin, vec3_origin);

	CDAudio_Update();

	if (host_speeds.value)
	{
		pass1 = (time1 - time3)*1000;
		time3 = Sys_DoubleTime ();
		pass2 = (time2 - time1)*1000;
		pass3 = (time3 - time2)*1000;
		Com_Printf ("%3i tot %3i server %3i gfx %3i snd\n",
					pass1+pass2+pass3, pass1, pass2, pass3);
	}

	cls.framecount++;
	fps_count++;
}

//============================================================================

/*
===============
CL_Shutdown
===============
*/
void CL_Shutdown (void)
{
	CL_Disconnect ();

	CL_WriteConfiguration ();

	CDAudio_Shutdown ();
	S_Shutdown();
	IN_Shutdown ();
	if (host_basepal)
		VID_Shutdown();
}
