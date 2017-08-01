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
// cvar.c -- dynamic variable tracking

#include "common.h"

extern void CL_UserinfoChanged (char *key, char *string);
extern void SV_ServerinfoChanged (char *key, char *string);

static cvar_t	*cvar_hash[32];
static cvar_t	*cvar_vars;


/*
============
Cvar_Next

Use this to walk through all vars
============
*/
cvar_t *Cvar_Next (cvar_t *var)
{
	if (var)
		return var->next;
	else
		return cvar_vars;
}


/*
============
Cvar_Find
============
*/
cvar_t *Cvar_Find (char *name)
{
	cvar_t	*var;
	int		key;

	key = Com_HashKey (name);
	
	for (var=cvar_hash[key] ; var ; var=var->hash_next)
		if (!Q_stricmp (name, var->name))
			return var;

	return NULL;
}

/*
============
Cvar_Value
============
*/
float Cvar_Value (char *name)
{
	cvar_t	*var = Cvar_Find (name);
	if (!var)
		return 0;
	return Q_atof (var->string);
}


/*
============
Cvar_String
============
*/
char *Cvar_String (char *name)
{
	cvar_t *var = Cvar_Find (name);
	if (!var)
		return "";
	return var->string;
}


/*
============
Cvar_CompleteVariable
============
*/
char *Cvar_CompleteVariable (char *partial)
{
	cvar_t		*cvar;
	int			len;
	
	len = strlen(partial);
	
	if (!len)
		return NULL;
		
	// check exact match
	for (cvar=cvar_vars ; cvar ; cvar=cvar->next)
		if (!Q_stricmp (partial,cvar->name))
			return cvar->name;

	// check partial match
	for (cvar=cvar_vars ; cvar ; cvar=cvar->next)
		if (!Q_strnicmp (partial,cvar->name, len))
			return cvar->name;

	return NULL;
}

int Cvar_CompleteCountPossible (char *partial)
{
	cvar_t	*cvar;
	int		len;
	int		c = 0;
	
	len = strlen(partial);
	
	if (!len)
		return 0;
		
	// check partial match
	for (cvar=cvar_vars ; cvar ; cvar=cvar->next)
		if (!Q_strnicmp (partial, cvar->name, len))
			c++;

	return c;
}


/*
============
Cvar_Set
============
*/
void Cvar_Set (cvar_t *var, char *string)
{
	static qbool changing = false;

	if (!var)
		return;

	if (var->flags & CVAR_ROM)
	{
		Com_Printf ("\"%s\" is write protected\n", var->name);
		return;
	}

	if ((var->flags & CVAR_INIT) && host_initialized)
	{
		//if (cl_warncmd.value)
		//	Com_Printf ("\"%s\" cannot be changed from the console\n", var->name);
		return;
	}

	if (var->OnChange && !changing) {
		qbool cancel = false;
		changing = true;
		var->OnChange(var, string, &cancel);
		changing = false;
		if (cancel)
			return;
	}

	// FIXME, avoid reallocation if the new string has same size?

	Q_free (var->string);
	var->string = Q_strdup (string);

	var->value = Q_atof (var->string);

#ifndef CLIENTONLY
	if (var->flags & CVAR_SERVERINFO)
		SV_ServerinfoChanged (var->name, var->string);
#endif

#ifndef SERVERONLY
	if (var->flags & CVAR_USERINFO)
		CL_UserinfoChanged (var->name, var->string);
#endif
}

/*
============
Cvar_ForceSet
============
*/
void Cvar_ForceSet (cvar_t *var, char *string)
{
	int saved_flags;

	if (!var)
		return;

	saved_flags = var->flags;
	var->flags &= ~CVAR_ROM;
	Cvar_Set (var, string);
	var->flags = saved_flags;
}


/*
============
Cvar_SetValue
============
*/
void Cvar_SetValue (cvar_t *var, float value)
{
	char	val[128];
	int	i;
	
	snprintf (val, sizeof(val), "%f", value);

	for (i=strlen(val)-1 ; i>0 && val[i]=='0' ; i--)
		val[i] = 0;
	if (val[i] == '.')
		val[i] = 0;

	Cvar_Set (var, val);
}


/*
============
Cvar_Register

Adds a freestanding variable to the variable list.

If the variable already exists, the value will not be set
The flags will be or'ed in if the variable exists.
============
*/
void Cvar_Register (cvar_t *var)
{
	char	string[512];
	int		key;
	cvar_t	*old;

	// first check to see if it has already been defined
	old = Cvar_Find (var->name);

	if (old && !(old->flags & CVAR_DYNAMIC)) {
		if (old == var)
			return;
		Com_Printf ("Can't register variable %s, already defined\n", var->name);
		return;
	}

#if 0
	// check for overlap with a command
	if (Cmd_Exists (var->name)) {
		Com_Printf ("Cvar_Register: %s is a command\n", var->name);
		return;
	}
#endif

	if (old)
	{
		var->flags |= old->flags & ~(CVAR_DYNAMIC|CVAR_TEMP);
		strlcpy (string, old->string, sizeof(string));
		Cvar_Delete (old->name);
		if (!(var->flags & CVAR_ROM))
			var->string = Q_strdup (string);
		else
			var->string = Q_strdup (var->string);
	}
	else
	{
		// allocate the string on heap because future sets will Q_free it
		var->string = Q_strdup (var->string);
	}
	
	var->value = Q_atof (var->string);

	// link the variable in
	key = Com_HashKey (var->name);
	var->hash_next = cvar_hash[key];
	cvar_hash[key] = var;
	var->next = cvar_vars;
	cvar_vars = var;

#ifndef CLIENTONLY
	if (var->flags & CVAR_SERVERINFO)
		SV_ServerinfoChanged (var->name, var->string);
#endif

#ifndef SERVERONLY
	if (var->flags & CVAR_USERINFO)
		CL_UserinfoChanged (var->name, var->string);
#endif
}


/*
============
Cvar_Command

Handles variable inspection and changing from the console
============
*/
qbool Cvar_Command (void)
{
	cvar_t		*var;

// check variables
	var = Cvar_Find (Cmd_Argv(0));
	if (!var)
		return false;

// perform a variable print or set
	if (Cmd_Argc() == 1)
	{
		Com_Printf ("\"%s\" is \"%s\"\n", var->name, var->string);
		return true;
	}

	Cvar_Set (var, Cmd_MakeArgs(1));
	return true;
}


/*
============
Cvar_WriteVariables

Writes lines containing "set variable value" for all variables
with the archive flag set to true.
============
*/
void Cvar_WriteVariables (FILE *f)
{
	cvar_t	*var;

	// write builtin cvars in a QW compatible way
	for (var = cvar_vars ; var ; var = var->next)
		if (var->flags & CVAR_ARCHIVE)
			fprintf (f, "%s \"%s\"\n", var->name, var->string);

	// write everything else
	for (var = cvar_vars ; var ; var = var->next)
		if (var->flags & CVAR_USER_ARCHIVE)
			fprintf (f, "seta %s \"%s\"\n", var->name, var->string);
}


/*
=============
Cvar_Toggle_f
=============
*/
void Cvar_Toggle_f (void)
{
	cvar_t *var;

	if (Cmd_Argc() != 2)
	{
		Com_Printf ("toggle <cvar> : toggle a cvar on/off\n");
		return;
	}

	var = Cvar_Find (Cmd_Argv(1));
	if (!var)
	{
		Com_Printf ("Unknown variable \"%s\"\n", Cmd_Argv(1));
		return;
	}

	Cvar_Set (var, var->value ? "0" : "1");
}

/*
===============
Cvar_CvarList_f

Lists all cvars
===============
*/
void Cvar_CvarList_f (void)
{
	cvar_t	*var;
	int count;
	char *pattern;

	pattern = (Cmd_Argc() > 1) ? Cmd_Argv(1) : NULL;

	count = 0;
	for (var = cvar_vars; var; var = var->next) {
		if (pattern && !Q_glob_match(pattern, var->name))
			continue;

		Com_Printf ("%c%c%c %s\n",
			var->flags & (CVAR_ARCHIVE|CVAR_USER_ARCHIVE) ? '*' : ' ',
			var->flags & CVAR_USERINFO ? 'u' : ' ',
			var->flags & CVAR_SERVERINFO ? 's' : ' ',
			var->name);
		count++;
	}

	Com_Printf ("------------\n%d %svariables\n", count, pattern ? "matching " : "");
}

/*
===========
Cvar_Get
===========
*/
cvar_t *Cvar_Get (char *name, char *string, int cvarflags)
{
	cvar_t		*var;
	int			key;

	var = Cvar_Find(name);
	if (var) {
		var->flags &= ~CVAR_TEMP;
		var->flags |= cvarflags;
		return var;
	}

	// allocate a new cvar
	var = (cvar_t *) Q_malloc (sizeof(cvar_t));

	// link it in
	var->next = cvar_vars;
	cvar_vars = var;
	key = Com_HashKey (name);
	var->hash_next = cvar_hash[key];
	cvar_hash[key] = var;

	// Q_malloc returns unitialized memory, so make sure all fields
	// are initialized here
	var->name = Q_strdup (name);
	var->string = Q_strdup (string);
	var->flags = cvarflags | CVAR_DYNAMIC;
	var->value = Q_atof (var->string);
	var->OnChange = NULL;

	// FIXME, check userinfo/serverinfo

	return var;
}

/*
===========
Cvar_Delete
===========
returns true if the cvar was found (and deleted)
*/
qbool Cvar_Delete (char *name)
{
	cvar_t	*var, *prev;
	int		key;

	// unlink from hash
	key = Com_HashKey (name);
	prev = NULL;
	for (var = cvar_hash[key] ; var ; var=var->hash_next)
	{
		if (!Q_stricmp(var->name, name)) {
			if (prev)
				prev->hash_next = var->hash_next;
			else
				cvar_hash[key] = var->hash_next;
			break;
		}
		prev = var;
	}

	if (!var)
		return false;

	// unlink from cvar list and free
	prev = NULL;
	for (var = cvar_vars ; var ; var=var->next)
	{
		if (!Q_stricmp(var->name, name)) {
			if (prev)
				prev->next = var->next;
			else
				cvar_vars = var->next;

			// free
			Q_free (var->string);
			Q_free (var->name);
			Q_free (var);
			return true;
		}
		prev = var;
	}

	assert(!"Cvar list broken");
	return false;	// shut up compiler
}


// if an unknown command with parameters was encountered when loading
// config.cfg, assume it's a cvar set and spawn a temp var
qbool Cvar_CreateTempVar (void)
{
	char *name = Cmd_Argv(0);
	// FIXME, make sure it's a valid cvar name, return false if not
	Cvar_Get (name, Cmd_MakeArgs(1), CVAR_TEMP);
	return true;
}

// if none of the subsystems claimed the cvar from config.cfg, remove it
void Cvar_CleanUpTempVars (void)
{
	cvar_t *var, *next;

	for (var = cvar_vars; var; var = next) {
		next = var->next;
		if (var->flags & CVAR_TEMP)
			Cvar_Delete (var->name);
	}
}


static qbool cvar_seta = false;

void Cvar_Set_f (void)
{
	cvar_t *var;
	char *name;

	if (Cmd_Argc() != 3)
	{
		Com_Printf ("usage: set <cvar> <value>\n");
		return;
	}

	name = Cmd_Argv (1);
	var = Cvar_Find (name);

	if (var)
	{
		Cvar_Set (var, Cmd_Argv(2));
	}
	else
	{
		if (Cmd_Exists(name))
		{
			Com_Printf ("\"%s\" is a command\n", name);
			return;
		}

		var = Cvar_Get (name, Cmd_Argv(2), 0);
	}

	if (cvar_seta)
		var->flags |= CVAR_USER_ARCHIVE;
}


void Cvar_Seta_f (void)
{
	cvar_seta = true;
	Cvar_Set_f ();
	cvar_seta = false;
}


void Cvar_Inc_f (void)
{
	int		c;
	cvar_t	*var;
	float	delta;

	c = Cmd_Argc();
	if (c != 2 && c != 3) {
		Com_Printf ("inc <cvar> [value]\n");
		return;
	}

	var = Cvar_Find (Cmd_Argv(1));
	if (!var) {
		Com_Printf ("Unknown variable \"%s\"\n", Cmd_Argv(1));
		return;
	}

	if (c == 3)
		delta = atof (Cmd_Argv(2));
	else
		delta = 1;

	Cvar_SetValue (var, var->value + delta);
}

void Cvar_Init (void)
{
	Cmd_AddCommand ("cvarlist", Cvar_CvarList_f);
	Cmd_AddCommand ("toggle", Cvar_Toggle_f);
	Cmd_AddCommand ("set", Cvar_Set_f);
	Cmd_AddCommand ("seta", Cvar_Seta_f);
	Cmd_AddCommand ("inc", Cvar_Inc_f);
}
