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
// common.h  -- general definitions
#ifndef _COMMON_H_
#define _COMMON_H_

#include "q_shared.h"
#include "zone.h"
#include "cvar.h"
#include "cmd.h"
#include "net.h"
#include "protocol.h"
#include "cmodel.h"


//
// per-level limits
//
#define	MAX_CL_EDICTS	768			// the protocol can only handle 512, but not changing
									// for compatibility (QW svc_startsound & NQ demos)
#define	MAX_EDICTS		1024		// server limit, can be increased if needed
#define	MAX_LIGHTSTYLES	64
#define	MAX_MODELS		256			// these are sent over the net as bytes
#define MAX_VWEP_MODELS 32			// could be increased to 256
#define	MAX_SOUNDS		256			// so they cannot be blindly increased

#define	SAVEGAME_COMMENT_LENGTH	39

//============================================================================

// move these to gamedefs.h?

//
// stats are integers communicated to the client by the server
//
#define	MAX_CL_STATS		32
#define	STAT_HEALTH			0
//define	STAT_FRAGS			1
#define	STAT_WEAPON			2
#define	STAT_AMMO			3
#define	STAT_ARMOR			4
//define	STAT_WEAPONFRAME	5
#define	STAT_SHELLS			6
#define	STAT_NAILS			7
#define	STAT_ROCKETS		8
#define	STAT_CELLS			9
#define	STAT_ACTIVEWEAPON	10
#define	STAT_TOTALSECRETS	11
#define	STAT_TOTALMONSTERS	12
#define	STAT_SECRETS		13		// bumped on client side by svc_foundsecret
#define	STAT_MONSTERS		14		// bumped by svc_killedmonster
#define	STAT_ITEMS			15
#define	STAT_VIEWHEIGHT		16		// Z_EXT_VIEWHEIGHT extension
#define STAT_TIME			17		// Z_EXT_TIME extension


//
// item flags
//
#define	IT_SHOTGUN				1
#define	IT_SUPER_SHOTGUN		2
#define	IT_NAILGUN				4
#define	IT_SUPER_NAILGUN		8
#define	IT_GRENADE_LAUNCHER		16
#define	IT_ROCKET_LAUNCHER		32
#define	IT_LIGHTNING			64
#define	IT_SUPER_LIGHTNING		128
#define	IT_SHELLS				256
#define	IT_NAILS				512
#define	IT_ROCKETS				1024
#define	IT_CELLS				2048
#define	IT_AXE					4096
#define	IT_ARMOR1				8192
#define	IT_ARMOR2				16384
#define	IT_ARMOR3				32768
#define	IT_SUPERHEALTH			65536
#define	IT_KEY1					131072
#define	IT_KEY2					262144
#define	IT_INVISIBILITY			524288
#define	IT_INVULNERABILITY		1048576
#define	IT_SUIT					2097152
#define	IT_QUAD					4194304
#define	IT_SIGIL1				(1<<28)
#define	IT_SIGIL2				(1<<29)
#define	IT_SIGIL3				(1<<30)
#define	IT_SIGIL4				(1<<31)

//
// entity effects
//
#define	EF_BRIGHTFIELD			1
#define	EF_MUZZLEFLASH 			2
#define	EF_BRIGHTLIGHT 			4
#define	EF_DIMLIGHT 			8
#define	EF_FLAG1	 			16
#define	EF_FLAG2	 			32
#define EF_BLUE					64
#define EF_RED					128


//
// print flags
//
#define	PRINT_LOW			0		// pickup messages
#define	PRINT_MEDIUM			1		// death messages
#define	PRINT_HIGH			2		// critical messages
#define	PRINT_CHAT			3		// chat messages


// game types sent by serverinfo
// these determine which intermission screen plays
#define	GAME_COOP			0
#define	GAME_DEATHMATCH		1


//============================================================================

struct usercmd_s;
struct entity_state_s;
struct packet_entities_s;

extern struct usercmd_s nullcmd;


void MSG_WriteChar (sizebuf_t *sb, int c);
void MSG_WriteByte (sizebuf_t *sb, int c);
void MSG_WriteShort (sizebuf_t *sb, int c);
void MSG_WriteLong (sizebuf_t *sb, int c);
void MSG_WriteFloat (sizebuf_t *sb, float f);
void MSG_WriteString (sizebuf_t *sb, char *s);
void MSG_WriteCoord (sizebuf_t *sb, float f);
void MSG_WriteAngle (sizebuf_t *sb, float f);
void MSG_WriteAngle16 (sizebuf_t *sb, float f);
void MSG_WriteDeltaUsercmd (sizebuf_t *sb, struct usercmd_s *from, struct usercmd_s *cmd);
void MSG_EmitPacketEntities (struct packet_entities_s *from, int delta_sequence, struct packet_entities_s *to,
							sizebuf_t *msg, struct entity_state_s *(*GetBaseline)(int number));

extern	int		msg_readcount;
extern	qbool	msg_badread;		// set if a read goes beyond end of message

void MSG_BeginReading (void);
int MSG_GetReadCount(void);
int MSG_ReadChar (void);
int MSG_ReadByte (void);
int MSG_ReadShort (void);
int MSG_ReadLong (void);
float MSG_ReadFloat (void);
char *MSG_ReadString (void);
char *MSG_ReadStringLine (void);

float MSG_ReadCoord (void);
float MSG_ReadAngle (void);
float MSG_ReadAngle16 (void);
void MSG_ReadDeltaUsercmd (struct usercmd_s *from, struct usercmd_s *cmd, int protocol);

void MSG_PackOrigin (const vec3_t in, short out[3]);
void MSG_UnpackOrigin (const short in[3], vec3_t out);

void MSG_PackAngles (const vec3_t in, char out[3]);
void MSG_UnpackAngles (const char in[3], vec3_t out);

//============================================================================

extern	char	com_token[1024];
extern	qbool	com_eof;

char *COM_Parse (char *data);


extern	int		com_argc;
extern	char	**com_argv;

void COM_InitArgv (int argc, char **argv);
int	COM_Argc (void);
char *COM_Argv (int arg);	// range and null checked
void COM_ClearArgv (int arg);
int COM_CheckParm (char *parm);
void COM_AddParm (char *parm);


void COM_Init (void);
void COM_Shutdown (void);


char *COM_SkipPath (char *pathname);
char *COM_FileExtension (char *in);
void COM_StripExtension (char *in, char *out);
void COM_FileBase (char *in, char *out);
void COM_DefaultExtension (char *path, char *extension);
void COM_ForceExtension (char *path, char *extension);

char	*va(char *format, ...);
// does a varargs printf into a temp buffer

//============================================================================

extern int fs_filesize;
struct cache_user_s;

extern char	com_gamedir[MAX_OSPATH];
extern char	com_basedir[MAX_OSPATH];
extern char com_gamedirfile[MAX_QPATH];

extern qbool	file_from_pak;		// set if file came from a pak file
extern qbool	file_from_gamedir;	// set if file came from a gamedir (and gamedir wasn't id1/qw)

void FS_InitFilesystem (void);
void FS_SetGamedir (char *dir);
int FS_FOpenFile (char *filename, FILE **file);
qbool FS_FindFile (char *filename);
byte *FS_LoadStackFile (char *path, void *buffer, int bufsize);
byte *FS_LoadTempFile (char *path);
byte *FS_LoadHunkFile (char *path);
void FS_LoadCacheFile (char *path, struct cache_user_s *cu);
byte *FS_LoadHeapFile (char *path);

void COM_WriteFile (char *filename, void *data, int len);
void COM_CreatePath (char *path);

void COM_CheckRegistered (void);

//============================================================================

#define MAX_INFO_KEY			64

#ifndef AGRIP
    #define	MAX_INFO_STRING			196
#else
// AGRIP needs large userinfo strings (FIXME)
    #define	MAX_INFO_STRING			1024
#endif

#define	MAX_SERVERINFO_STRING	512
#define	MAX_LOCALINFO_STRING	32768

char *Info_ValueForKey (char *s, char *key);
void Info_RemoveKey (char *s, char *key);
void Info_RemovePrefixedKeys (char *start, char prefix);
void Info_SetValueForKey (char *s, char *key, char *value, int maxsize);
void Info_SetValueForStarKey (char *s, char *key, char *value, int maxsize);
void Info_Print (char *s);

//============================================================================

unsigned Com_BlockChecksum (void *buffer, int length);
void Com_BlockFullChecksum (void *buffer, int len, unsigned char *outbuf);
byte	COM_BlockSequenceCRCByte (byte *base, int length, int sequence);

//============================================================================

// com_mapcheck.c
int Com_TranslateMapChecksum (char *mapname, int checksum);

//============================================================================

void Com_BeginRedirect (void (*RedirectedPrint) (char *));
void Com_EndRedirect (void);
void Com_Printf (char *fmt, ...);
void Com_PrintW (wchar *msg);
void Com_DPrintf (char *fmt, ...);

//============================================================================

#ifdef SERVERONLY
#define	dedicated	1
#elif CLIENTONLY
#define	dedicated	0
#else
extern qbool	dedicated;
#endif

extern cvar_t	developer;
extern cvar_t	registered;

extern qbool	com_serveractive;	// true if sv.state != ss_dead
extern int		CL_ClientState ();	// returns cls.state

extern double	curtime;	// not bounded or scaled, shared by
								// local client and server

//
// host
//
extern qbool	host_initialized;
extern int		host_memsize;

extern cvar_t	host_mapname;

// functions that may be called accross subsystems (host, client, server)

void Host_Init (int argc, char **argv, int default_memsize);
void Host_ClearMemory ();
void Host_Shutdown (void);
void Host_Frame (double time);
void Host_Abort (void);					// longjmp() to Host_Frame
void Host_EndGame (void);				// kill local client and server
void Host_Error (char *error, ...);
void Host_Quit (void);

void CL_Init (void);
void CL_Shutdown (void);
void CL_GamedirChanged (void);
void CL_Frame (double time);
void CL_Disconnect (void);
void CL_HandleHostError (void);
void CL_BeginLocalConnection (void);
void Con_Init (void);
void Con_Print (char *txt);
void Con_PrintW (wchar *txt);
void Key_Init (void);
void SCR_EndLoadingPlaque (void);

void SV_Init (void);
void SV_Shutdown (char *finalmsg);
void SV_Frame (double time);

#endif /* _COMMON_H_ */

