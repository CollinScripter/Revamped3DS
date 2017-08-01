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
#ifndef _CVAR_H_
#define _CVAR_H_

// cvar flags
#define CVAR_ARCHIVE		1
#define CVAR_USERINFO		2       // mirrored to userinfo
#define CVAR_SERVERINFO		4		// mirrored to serverinfo
#define CVAR_ROM			8		// read only
#define CVAR_INIT			16		// can only be set during initialization
#define	CVAR_DYNAMIC		32		// allocated on heap, not static
#define	CVAR_USER_ARCHIVE	64		// created by a seta command
#define CVAR_TEMP			128		// created during initial config.cfg loading

typedef struct cvar_s
{
	char	*name;
	char	*string;
	int		flags;
	void	(*OnChange)(struct cvar_s *var, char *value, qbool *cancel);
	float	value;
	struct cvar_s *hash_next;
	struct cvar_s *next;
} cvar_t;


// registers a cvar that already has the name, string, and optionally the
// flags set
void Cvar_Register (cvar_t *var);

// returns existing var or creates a new, dynamic one.  cvarflags will be or'ed in
cvar_t *Cvar_Get (char *name, char *string, int cvarflags);

// equivalent to "<name> <variable>" typed at the console
void Cvar_Set (cvar_t *var, char *string);

// force a set even if the cvar is read only
void Cvar_ForceSet (cvar_t *var, char *string);

// expands value to a string and calls Cvar_Set
void Cvar_SetValue (cvar_t *var, float value);

// returns 0 if not defined or non-numeric
float Cvar_Value (char *name);

// returns an empty string if not defined
char *Cvar_String (char *name);

// attempts to match a partial variable name for command line completion
// returns NULL if nothing fits
char  *Cvar_CompleteVariable (char *partial);

// called by Cmd_ExecuteString when Cmd_Argv(0) doesn't match a known
// command.  Returns true if the command was a variable reference that
// was handled. (print or change)
qbool Cvar_Command (void);

// Writes lines containing "set variable value" for all variables
// with the archive flag set to true.
void Cvar_WriteVariables (FILE *f);

cvar_t *Cvar_Find (char *name);
qbool Cvar_Delete (char *name);

// Use this to walk through all vars
cvar_t *Cvar_Next (cvar_t *var);

qbool Cvar_CreateTempVar (void);	// when parsing config.cfg
void Cvar_CleanUpTempVars (void);	// clean up afterwards

void Cvar_Init (void);

#endif /* _CVAR_H_ */

