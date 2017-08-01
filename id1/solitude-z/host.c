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
#include "version.h"
#include <setjmp.h>


#if !defined(CLIENTONLY) && !defined(SERVERONLY)
qbool		dedicated = false;
#endif

cvar_t		host_mapname = {"mapname", "", CVAR_ROM};

double		curtime;

qbool		host_initialized;		// true if into command execution
int			host_hunklevel;
int			host_memsize;
void		*host_membase;

jmp_buf 	host_abort;


/*
================
Host_Abort
================
*/
void Host_Abort (void)
{
	longjmp (host_abort, 1);
}

/*
================
Host_EndGame
================
*/
void Host_EndGame (void)
{
	SCR_EndLoadingPlaque ();

	SV_Shutdown ("Server was killed");
	CL_Disconnect ();

	// clear disconnect messages from loopback
	NET_ClearLoopback ();
}

/*
================
Host_Error

This shuts down both the client and server
================
*/
void Host_Error (char *error, ...)
{
	va_list		argptr;
	char		string[1024];
	static qbool inerror = false;
	
	if (inerror)
		Sys_Error ("Host_Error: recursively entered");
	inerror = true;

	Com_EndRedirect ();

	SCR_EndLoadingPlaque ();

	va_start (argptr,error);
#ifdef _WIN32
	_vsnprintf (string, sizeof(string) - 1, error, argptr);
	string[sizeof(string) - 1] = '\0';
#else
	vsnprintf (string, sizeof(string), error, argptr);
#endif // _WIN32
	va_end (argptr);

	Com_Printf ("\n===========================\n");
	Com_Printf ("Host_Error: %s\n",string);
	Com_Printf ("===========================\n\n");
	
	SV_Shutdown (va("server crashed: %s\n", string));
	CL_Disconnect ();
	CL_HandleHostError ();		// stop demo loop

	if (dedicated)
	{
		NET_Shutdown ();
		COM_Shutdown ();
		Sys_Error ("%s", string);
	}

	if (!host_initialized)
		Sys_Error ("Host_Error: %s", string);

	inerror = false;

	Host_Abort ();
}


// init whatever commands/cvars we need
// not many, really
void Host_InitLocal (void)
{
	Cvar_Register (&host_mapname);
}

/*
===============
Host_InitMemory

memsize is the recommended amount of memory to use for hunk
===============
*/
void Host_InitMemory (int memsize)
{
	int		t;

	if (COM_CheckParm ("-minmemory"))
		memsize = MINIMUM_MEMORY;

	if ((t = COM_CheckParm ("-heapsize")) != 0 && t + 1 < com_argc)
		memsize = Q_atoi (com_argv[t + 1]) * 1024;

	if ((t = COM_CheckParm ("-mem")) != 0 && t + 1 < com_argc)
		memsize = Q_atoi (com_argv[t + 1]) * 1024 * 1024;

	if (memsize < MINIMUM_MEMORY)
		Sys_Error ("Only %4.1f megs of memory reported, can't execute game", memsize / (float)0x100000);

	host_memsize = memsize;
	host_membase = Q_malloc (host_memsize);
	Memory_Init (host_membase, host_memsize);
}


extern void D_FlushCaches (void);
extern void Mod_ClearAll (void);

/*
===============
Host_ClearMemory

Free hunk memory up to host_hunklevel
Can only be called when changing levels!
===============
*/
void Host_ClearMemory ()
{
	// FIXME, move to CL_ClearState
	if (!dedicated)
		D_FlushCaches ();

	// FIXME, move to CL_ClearState
#ifndef SERVERONLY
	if (!dedicated)
		Mod_ClearAll ();
#endif

	CM_InvalidateMap ();

	// any data previously allocated on hunk is no longer valid
	Hunk_FreeToLowMark (host_hunklevel);
}


/*
===============
Host_Frame
===============
*/
void Host_Frame (double time)
{
	if (setjmp (host_abort))
		return;			// something bad happened, or the server disconnected

	curtime += time;

	if (dedicated)
		SV_Frame (time);
	else
		CL_Frame (time);	// will also call SV_Frame
}

// this will go elsewhere...
qbool NonLegacyDefaultCfg (void) {
	byte *data;
	data = FS_LoadTempFile ("default.cfg");
	if (!data)
		return false;
	if (fs_filesize == 1914 && Com_BlockChecksum(data, fs_filesize) == 0x2d7b72b9)
		return false;
	return true;
}

void ExecDefaultConfig (void) 
{
	// the user provided his own default.cfg, so use it
	if (NonLegacyDefaultCfg()) {
		Cbuf_AddText ("exec default.cfg\n");
		return;
	}

	Cbuf_AddText (

"unbindall\n"

"bind w +forward;"
"bind s +back;"
"bind a +moveleft;"
"bind d +moveright;"
"bind c +movedown;"
#ifdef AGRIP
"bind alt +strafe;"
#else
"bind alt +movedown;"
#endif
"bind space +jump;"
"bind enter +jump;"
"bind ctrl +attack;"

"bind mouse1 +attack;"
"bind mouse2 impulse 8;"
"bind mouse3 impulse 3 2;"

"bind shift impulse 7;"
"bind f impulse 6;"

"bind uparrow +forward;"
"bind downarrow +back;"
"bind leftarrow +left;"
"bind rightarrow +right;"
"bind del +lookdown;"
"bind pgdn +lookup;"
"bind end centerview;"

"bind 1 impulse 1;"
"bind 2	impulse 2;"
"bind 3	impulse 3;"
"bind 4	impulse 4;"
"bind 5	impulse 5;"
"bind 6	impulse 6;"
"bind 7	impulse 7;"
"bind 8	impulse 8;"
"bind 9 impulse 9;"
"bind / impulse 10;"
"bind [ impulse 12;"
"bind ] impulse 10;"
"bind mwheelup impulse 12;"
"bind mwheeldown impulse 10;"

"bind F1 help;"
"bind F2 menu_save;"
"bind F3 menu_load;"
"bind F4 menu_options;"
"bind F5 menu_multiplayer;"
"bind F6 \"echo Quicksaving...; wait; save quick\";"
"bind F9 \"echo Quickloading...; wait; load quick\";"
"bind F10 quit;"
"bind F12 screenshot;"

"bind tab +showscores;"
"bind pause pause;"
"bind ~ toggleconsole;"
"bind `	toggleconsole;"

"bind t	messagemode;"
"bind y	messagemode2;"

"bind +	sizeup;"
"bind =	sizeup;"
"bind - sizedown;"
"bind KP_PLUS sizeup;"
"bind KP_MINUS sizedown;"
);
}

/*
====================
Host_Init
====================
*/
void Host_Init (int argc, char **argv, int default_memsize)
{
	COM_InitArgv (argc, argv);

#if !defined(CLIENTONLY) && !defined(SERVERONLY)
	if (COM_CheckParm("-dedicated"))
		dedicated = true;
#endif

	Host_InitMemory (default_memsize);

	Cbuf_Init ();
	Cmd_Init ();
	Cvar_Init ();
	COM_Init ();
	Key_Init ();

	FS_InitFilesystem ();
	COM_CheckRegistered ();

	Con_Init ();

	if (!dedicated) {
		//Cbuf_AddText ("exec default.cfg\n");
		ExecDefaultConfig ();
		Cbuf_AddText ("exec config.cfg\n");
		Cbuf_Execute ();
	}

	Cbuf_AddEarlyCommands ();
	Cbuf_Execute ();

	NET_Init ();
	Netchan_Init ();
	Sys_Init ();
	CM_Init ();
	PM_Init ();
	Host_InitLocal ();

	SV_Init ();
	CL_Init ();

	Cvar_CleanUpTempVars ();

	Hunk_AllocName (0, "-HOST_HUNKLEVEL-");
	host_hunklevel = Hunk_LowMark ();

	host_initialized = true;

	Com_Printf ("Exe: "__TIME__" "__DATE__"\n");
	Com_Printf ("%4.1f megs RAM used.\n", host_memsize / (1024*1024.0));
	Com_Printf ("\n========= " PROGRAM " Initialized =========\n");


	if (dedicated)
	{
		Cbuf_AddText ("exec server.cfg\n");
		Cmd_StuffCmds_f ();		// process command line arguments
		Cbuf_Execute ();

	// if a map wasn't specified on the command line, spawn start map
		if (!com_serveractive)
			Cmd_ExecuteString ("map start");
		if (!com_serveractive)
			Host_Error ("Couldn't spawn a server");
	}
	else
	{
		FILE *f;
		if (FS_FOpenFile("autoexec.cfg", &f) != -1) {
			fclose(f);
			Cbuf_AddText ("exec autoexec.cfg\n");
		}
		Cmd_StuffCmds_f ();		// process command line arguments
		Cbuf_AddText ("cl_warncmd 1\n");
	}
}


/*
===============
Host_Shutdown

FIXME: this is a callback from Sys_Quit and Sys_Error.  It would be better
to run quit through here before the final handoff to the sys code.
===============
*/
void Host_Shutdown (void)
{
	static qbool isdown = false;
	
	if (isdown)
	{
		printf ("recursive shutdown\n");
		return;
	}
	isdown = true;

	SV_Shutdown ("Server quit\n");
	CL_Shutdown ();
	NET_Shutdown ();
	COM_Shutdown ();
}

/*
===============
Host_Quit
===============
*/
void Host_Quit (void)
{
	Host_Shutdown ();
	Sys_Quit ();
}

