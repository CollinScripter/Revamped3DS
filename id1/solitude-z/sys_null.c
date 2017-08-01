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
// sys_null.h -- null system driver to aid porting efforts

#include "quakedef.h"

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>


qbool do_stdin = true;
qbool stdin_ready;


void Sys_mkdir (char *path)
{
}


/*
===============================================================================

SYSTEM IO

===============================================================================
*/

void Sys_MakeCodeWriteable (unsigned long startaddr, unsigned long length)
{
}


void Sys_Error (char *error, ...)
{
	va_list	 argptr;

	printf ("Sys_Error: ");
	va_start (argptr,error);
	vprintf (error,argptr);
	va_end (argptr);
	printf ("\n");

	exit (1);
}


void Sys_Printf (char *fmt, ...)
{
	va_list		argptr;

	va_start (argptr,fmt);
	vprintf (fmt,argptr);
	va_end (argptr);
}


void Sys_Quit (void)
{
	exit (0);
}


double Sys_DoubleTime (void)
{
	static double	 t	= 0.0;

	t += 0.1;

	return t;
}


char *Sys_ConsoleInput (void)
{
	return NULL;
}


char *Sys_GetClipboardText (void)
{
	return NULL;
}


void Sys_SendKeyEvents (void)
{
}


void Sys_Init (void)
{
}

//=============================================================================

int main (int argc, char **argv)
{
#ifdef hpux
	// makes it possible to access unaligned pointers (e.g. inside structures)
	//   must be linked with libhpp.a to work (add -lhppa to LDFLAGS)
	allow_unaligned_data_access();
#endif

	printf ("Host_Init\n");
	Host_Init (argc, argv, 5861376);
	while (1)
	{
		Host_Frame (0.1);
	}

	return 0;
}

