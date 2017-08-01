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
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
#include <limits.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <string.h>
#include <ctype.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <errno.h>

#ifdef SDL
#include <SDL.h>
#endif

#include "quakedef.h"

int			 noconinput	= 0;
int			 nostdout	= 0;

// BSD only defines FNDELAY:
#ifndef O_NDELAY
#  define O_NDELAY	FNDELAY
#endif

// =======================================================================
// General routines
// =======================================================================

void		 Sys_Printf (char *fmt, ...)
{
	va_list			 argptr;
	char			 text[2048];
	unsigned char	*p;

	va_start (argptr, fmt);
	vsnprintf (text, sizeof(text), fmt, argptr);
	va_end (argptr);

	if (strlen(text) > sizeof(text))
		Sys_Error("memory overwrite in Sys_Printf");

	if (nostdout)
		return;

	for (p = (unsigned char *)text; *p; p++)
#ifndef AGRIP
        {
		if ((*p > 128 || *p < 32) && *p != 10 && *p != 13 && *p != 9)
			printf("[%02x]", *p);
		else
			putc(*p, stdout);
        }
#else
        {
		if (!((*p > 128 || *p < 32) && *p != 10 && *p != 13 && *p != 9))
			putc(*p, stdout);
        }
        fflush(stdout);
#endif
}


void		 Sys_Quit (void)
{
	fcntl (0, F_SETFL, fcntl (0, F_GETFL, 0) & ~O_NDELAY);
	exit(0);
}


void		 Sys_Init(void)
{
}


void		 Sys_Error (char *error, ...)
{
	va_list	 argptr;
	char	 string[1024];

	// change stdin to non blocking
	fcntl (0, F_SETFL, fcntl (0, F_GETFL, 0) & ~O_NDELAY);

	va_start (argptr, error);
	vsnprintf (string, sizeof(string), error, argptr);
	va_end (argptr);
	fprintf(stderr, "Error: %s\n", string);

	Host_Shutdown ();
	exit (1);
}



void		 Sys_mkdir (char *path)
{
	mkdir (path, 0777);
}


double		 Sys_DoubleTime (void)
{
	struct timeval	 tp;
	struct timezone	 tzp;
	static int		 secbase	= 0;

	gettimeofday(&tp, &tzp);

	if (!secbase)
	{
		secbase = tp.tv_sec;
		return tp.tv_usec/1000000.0;
	}

	return (tp.tv_sec - secbase) + tp.tv_usec/1000000.0;
}

void		 floating_point_exception_handler(int whatever)
{
//	Sys_Warn("floating point exception\n");
	signal(SIGFPE, floating_point_exception_handler);
}

wchar		*Sys_GetClipboardTextW (void)
{
	return NULL;
}

// these are referenced by net_udp.c
qbool do_stdin = true, stdin_ready;

char		*Sys_ConsoleInput(void)
{
	static char	text[256];
	char	dummy[256];
	int	len;

	if (!dedicated || noconinput)
		return NULL;

	len = read (0, text, sizeof(text));
	if (len < 1)
		return NULL;

	// Tonik: if the line was longer than 256 chars,
	// through away the remainder (FIXME)
	while (read (0, dummy, sizeof(dummy)) > 0) {};

	text[len-1] = 0;    // rip off the /n and terminate

	return text;
}

#if !(defined(__APPLE__) && !defined(SDL))
int			 main (int argc, char **argv)
{
	double	 time, oldtime, newtime;

#ifdef PARANOID
	signal(SIGFPE, floating_point_exception_handler);
#else
	signal(SIGFPE, SIG_IGN);
#endif

#ifdef hpux
	// makes it possible to access unaligned pointers (e.g. inside structures)
	//   must be linked with libhpp.a to work (add -lhppa to LDFLAGS)
	allow_unaligned_data_access();
#endif

	// we need to check for -noconinput and -nostdout
	// before Host_Init is called
	COM_InitArgv (argc, argv);

	noconinput = COM_CheckParm("-noconinput");
	if (!noconinput)
		fcntl(0, F_SETFL, fcntl (0, F_GETFL, 0) | O_NDELAY);

	if (COM_CheckParm("-nostdout"))
		nostdout = 1;

#if id386
	Sys_SetFPCW();
#endif

	Host_Init (argc, argv, 16*1024*1024);

	oldtime = Sys_DoubleTime ();
	while (1)
	{
		if (dedicated)
			NET_Sleep (10);

		// find time spent rendering last frame
		newtime = Sys_DoubleTime ();
		time = newtime - oldtime;

		Host_Frame(time);
		oldtime = newtime;
	}
    return 0;
}
#endif


/*
================
Sys_MakeCodeWriteable
================
*/
void		 Sys_MakeCodeWriteable (unsigned long startaddr, unsigned long length)
{
	int		 r;
	unsigned long	 addr;
	int		 psize = getpagesize();

	addr = (startaddr & ~(psize-1)) - psize;

//	fprintf(stderr, "writable code %lx(%lx)-%lx, length=%lx\n", startaddr,
//	        addr, startaddr+length, length);

	r = mprotect((char*)addr, length + startaddr - addr + psize, 7);

	if (r < 0)
		Sys_Error("Protection change failed");
}

