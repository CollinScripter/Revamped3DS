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
// cmd.c -- Quake script command processing module

#include "common.h"

#ifndef SERVERONLY
qbool CL_CheckServerCommand (void);
#endif

cvar_t cl_warncmd = {"cl_warncmd", "0"};

cbuf_t	cbuf_main;
#ifndef SERVERONLY
cbuf_t	cbuf_safe;
cbuf_t	cbuf_svc;
#endif

cbuf_t	*cbuf_current = NULL;

//=============================================================================

/*
============
Cmd_Wait_f

Causes execution of the remainder of the command buffer to be delayed until
next frame.  This allows commands like:
bind g "impulse 5 ; +attack ; wait ; -attack ; impulse 2"
============
*/
void Cmd_Wait_f (void)
{
	if (cbuf_current)
		cbuf_current->wait = true;
}

/*
=============================================================================

						COMMAND BUFFER

=============================================================================
*/


void Cbuf_AddText (char *text) { Cbuf_AddTextEx (&cbuf_main, text); }
void Cbuf_InsertText (char *text) { Cbuf_InsertTextEx (&cbuf_main, text); }
void Cbuf_Execute () { Cbuf_ExecuteEx (&cbuf_main); }


//fuh : ideally we should have 'cbuf_t *Cbuf_Register(int maxsize, int flags, qbool (*blockcmd)(void))
//fuh : so that cbuf_svc and cbuf_safe can be registered outside cmd.c in cl_* .c
//fuh : flags can be used to deal with newline termination etc for cbuf_svc, and *blockcmd can be used for blocking cmd's for cbuf_svc
//fuh : this way cmd.c would be independant of '#ifdef CLIENTONLY's'.
//fuh : I'll take care of that one day.
static void Cbuf_Register (cbuf_t *cbuf, int maxsize) {
	assert(!host_initialized);
	cbuf->maxsize = maxsize;
	cbuf->text_buf = Hunk_Alloc(maxsize);
	cbuf->text_start = cbuf->text_end = (cbuf->maxsize >> 1);
	cbuf->wait = false;
}

/*
============
Cbuf_Init
============
*/
void Cbuf_Init (void)
{
	Cbuf_Register(&cbuf_main, 1 << 16);
#ifndef SERVERONLY
	Cbuf_Register(&cbuf_svc, 1 << 13);
	Cbuf_Register(&cbuf_safe, 1 << 11);
#endif
}

/*
============
Cbuf_AddText

Adds command text at the end of the buffer
============
*/
void Cbuf_AddTextEx (cbuf_t *cbuf, char *text)
{
	int		len;
	int		new_start;
	int		new_bufsize;
	
	len = strlen (text);

	if (cbuf->text_end + len <= cbuf->maxsize)
	{
		memcpy (cbuf->text_buf + cbuf->text_end, text, len);
		cbuf->text_end += len;
		return;
	}

	new_bufsize = cbuf->text_end-cbuf->text_start+len;
	if (new_bufsize > cbuf->maxsize)
	{
		Com_Printf ("Cbuf_AddText: overflow\n");
		return;
	}

	// Calculate optimal position of text in buffer
	new_start = (cbuf->maxsize - new_bufsize) / 2;

	memcpy (cbuf->text_buf + new_start, cbuf->text_buf + cbuf->text_start, cbuf->text_end-cbuf->text_start);
	memcpy (cbuf->text_buf + new_start + cbuf->text_end-cbuf->text_start, text, len);
	cbuf->text_start = new_start;
	cbuf->text_end = cbuf->text_start + new_bufsize;
}


/*
============
Cbuf_InsertText

Adds command text at the beginning of the buffer
============
*/
void Cbuf_InsertTextEx (cbuf_t *cbuf, char *text)
{
	int		len;
	int		new_start;
	int		new_bufsize;

	len = strlen(text);

	if (len <= cbuf->text_start)
	{
		memcpy (cbuf->text_buf + (cbuf->text_start - len), text, len);
		cbuf->text_start -= len;
		return;
	}

	new_bufsize = cbuf->text_end - cbuf->text_start + len;
	if (new_bufsize > cbuf->maxsize)
	{
		Com_Printf ("Cbuf_InsertText: overflow\n");
		return;
	}

	// Calculate optimal position of text in buffer
	new_start = (cbuf->maxsize - new_bufsize) / 2;

	memmove (cbuf->text_buf + (new_start + len), cbuf->text_buf + cbuf->text_start,
		cbuf->text_end - cbuf->text_start);
	memcpy (cbuf->text_buf + new_start, text, len);
	cbuf->text_start = new_start;
	cbuf->text_end = cbuf->text_start + new_bufsize;
}

/*
============
Cbuf_Execute
============
*/
void Cbuf_ExecuteEx (cbuf_t *cbuf)
{
	int		i, j, cursize;
	char	*text;
	char	line[1024], *src, *dest;
	qbool	comment, quotes;

	cbuf_current = cbuf;

	while (cbuf->text_end > cbuf->text_start)
	{
		// find a \n or ; line break
		text = (char *)cbuf->text_buf + cbuf->text_start;

		cursize = cbuf->text_end - cbuf->text_start;
		comment = quotes = false;
		for (i = 0; i < cursize; i++)
		{
			if (text[i] == '\n')
				break;
			if (text[i] == '"')
				quotes = !quotes;
			if (comment || quotes)
				continue;

			if (text[i] == '/' && (i + 1) < cursize && text[i + 1] == '/')
				comment = true;
			else if (text[i] == ';')
				break;
		}

// don't execute lines without ending \n; this fixes problems with
// partially stuffed aliases not being executed properly
#ifndef SERVERONLY
		if (cbuf_current == &cbuf_svc && i == cursize)
			break;
#endif

		// Copy text to line, skipping carriage return chars
		src = text;
		dest = line;
		j = min (i, sizeof(line)-1);
		for ( ; j ; j--, src++) {
			if (*src != 13)
				*dest++ = *src;
		}
		*dest = 0;

// delete the text from the command buffer and move remaining commands down
// this is necessary because commands (exec, alias) can insert data at the
// beginning of the text buffer

		if (i == cursize)
		{
			cbuf->text_start = cbuf->text_end = cbuf->maxsize/2;
		}
		else
		{
			i++;
			cbuf->text_start += i;
		}

// execute the command line
		Cmd_ExecuteString (line);
		
		if (cbuf->wait)
		{	// skip out while text still remains in buffer, leaving it
			// for next frame
			cbuf->wait = false;
			break;
		}
	}

	cbuf_current = NULL;
}

/*
==============================================================================

						SCRIPT COMMANDS

==============================================================================
*/

/*
===============
Cbuf_AddEarlyCommands

Set commands are added early, so they are guaranteed to be set before
the client and server initialize for the first time.

Other commands are added late, after all initialization is complete.
===============
*/
void Cbuf_AddEarlyCommands (void)
{
	int		i;

	for (i=0 ; i<COM_Argc()-2 ; i++)
	{
		if (Q_stricmp(COM_Argv(i), "+set"))
			continue;
		Cbuf_AddText (va("set %s %s\n", COM_Argv(i+1), COM_Argv(i+2)));
		i+=2;
	}
}


/*
===============
Cmd_StuffCmds_f

Adds command line parameters as script statements
Commands lead with a +, and continue until a - or another +
quake +prog jctest.qp +cmd amlev1
quake -nosound +cmd amlev1
===============
*/
void Cmd_StuffCmds_f (void)
{
	int		i, j;
	int		s;
	char	*text, *build, c;
		
// build the combined string to parse from
	s = 0;
	for (i = 1; i < com_argc; i++)
		s += strlen (com_argv[i]) + 1;

	if (!s)
		return;
		
	text = Q_malloc (s+1);
	text[0] = 0;
	for (i = 1; i < com_argc; i++)
	{
		strcat (text, com_argv[i]);
		if (i != com_argc-1)
			strcat (text, " ");
	}
	
// pull out the commands
	build = Q_malloc (s+1);
	build[0] = 0;
	
	for (i = 0; i < s-1; i++)
	{
		if (text[i] == '+')
		{
			i++;

			for (j=i ; (text[j] != '+') && (text[j] != '-') && (text[j] != 0) ; j++)
				;

			c = text[j];
			text[j] = 0;
			
			strcat (build, text+i);
			strcat (build, "\n");
			text[j] = c;
			i = j-1;
		}
	}
	
	if (build[0])
		Cbuf_AddText (build);
	
	Q_free (text);
	Q_free (build);
}


/*
===============
Cmd_Exec_f
===============
*/
void Cmd_Exec_f (void)
{
	char	*f;
	int		mark;
	char	name[MAX_OSPATH];

	if (Cmd_Argc () != 2)
	{
		Com_Printf ("exec <filename> : execute a script file\n");
		return;
	}

	strlcpy (name, Cmd_Argv(1), sizeof(name) - 4);
	mark = Hunk_LowMark ();
	f = (char *)FS_LoadHunkFile (name);
	if (!f)
	{
		char *p;

		p = COM_SkipPath (name);
		if (!strchr (p, '.')) {
			// no extension, so try the default (.cfg)
			strcat (name, ".cfg");
			f = (char *)FS_LoadHunkFile (name);
		}

		if (!f) {
			Com_Printf ("couldn't exec %s\n", Cmd_Argv(1));
			return;
		}
	}
	if (cl_warncmd.value || developer.value)
		Com_Printf ("execing %s\n", name);

#ifndef SERVERONLY
	if (cbuf_current == &cbuf_svc) {
		Cbuf_AddText (f);
		Cbuf_AddText ("\n");
	}
	else
#endif
	{
		Cbuf_InsertText ("\n");
		Cbuf_InsertText (f);
	}
	Hunk_FreeToLowMark (mark);
}


/*
===============
Cmd_Echo_f

Just prints the rest of the line to the console
===============
*/
void Cmd_Echo_f (void)
{
	int		i;
	
	for (i=1 ; i<Cmd_Argc() ; i++)
		Com_Printf ("%s ",Cmd_Argv(i));
	Com_Printf ("\n");
}

/*
=============================================================================

								ALIASES

=============================================================================
*/

static cmd_alias_t	*cmd_alias_hash[32];
static cmd_alias_t	*cmd_alias;

// use to enumerate all aliases
cmd_alias_t *Alias_Next (cmd_alias_t *alias)
{
	if (alias)
		return alias->next;
	else
		return cmd_alias;
}

cmd_alias_t *Cmd_FindAlias (char *name)
{
	int			key;
	cmd_alias_t *alias;

	key = Com_HashKey (name);
	for (alias = cmd_alias_hash[key] ; alias ; alias = alias->hash_next)
	{
		if (!Q_stricmp(name, alias->name))
			return alias;
	}
	return NULL;
}

char *Cmd_AliasString (char *name)
{
	int			key;
	cmd_alias_t *alias;

	key = Com_HashKey (name);
	for (alias = cmd_alias_hash[key] ; alias ; alias = alias->hash_next)
	{
		if (!Q_stricmp(name, alias->name))
			return alias->value;
	}
	return NULL;
}

/*
===============
Cmd_Viewalias_f
===============
*/
void Cmd_Viewalias_f (void)
{
	cmd_alias_t *alias;

	if (Cmd_Argc() < 2)
	{
		Com_Printf ("viewalias <aliasname> : view body of alias\n");
		return;
	}

	alias = Cmd_FindAlias(Cmd_Argv(1));

	if (alias)
		Com_Printf ("%s : \"%s\"\n", Cmd_Argv(1), alias->value);
	else
		Com_Printf ("No such alias: %s\n", Cmd_Argv(1));
}

/*
===============
Cmd_AliasList_f
===============
*/
void Cmd_AliasList_f (void)
{
	cmd_alias_t	*a;
	char *pattern;

	pattern = Cmd_Argc() > 1 ? Cmd_Argv(1) : NULL;

	if (!pattern)
		Com_Printf ("Current alias commands:\n");
	for (a = cmd_alias; a; a = a->next) {
		if (!pattern || Q_glob_match(pattern, a->name))
			Com_Printf ("%s : %s\n\n", a->name, a->value);
	}
}

/*
===============
Cmd_Alias_f

Creates a new command that executes a command string (possibly ; separated)
===============
*/
void Cmd_Alias_f (void)
{
	cmd_alias_t	*a;
	int			key;
	char		*name;

	if (Cmd_Argc() == 1)
	{
		Com_Printf ("alias <name> <command> : create or modify an alias\n");
		Com_Printf ("aliaslist : list all aliases\n");
		return;
	}

	name = Cmd_Argv(1);

	// see if there's already an alias by that name
	a = Cmd_FindAlias(name);

	if (a) {
		// reuse it
		Q_free (a->name);
		Q_free (a->value);
	}
	else {
		// allocate a new one
		a = Q_malloc (sizeof(cmd_alias_t));
		a->flags = 0;

		// link it in
		a->next = cmd_alias;
		cmd_alias = a;
		key = Com_HashKey(name);
		a->hash_next = cmd_alias_hash[key];
		cmd_alias_hash[key] = a;
	}

	a->name = Q_strdup(name);
	a->value = Q_strdup(Cmd_MakeArgs(2));	// copy the rest of the command line

#ifndef SERVERONLY
	if (cbuf_current == &cbuf_svc)
		a->flags |= ALIAS_STUFFED;
	else
		a->flags &= ALIAS_STUFFED;
#endif

	if (!Q_stricmp(Cmd_Argv(0), "aliasa"))
		a->flags |= ALIAS_ARCHIVE;

}


qbool Cmd_DeleteAlias (char *name)
{
	cmd_alias_t	*a, *prev;
	int			key;

	key = Com_HashKey (name);

	prev = NULL;
	for (a = cmd_alias_hash[key] ; a ; a = a->hash_next)
	{
		if (!Q_stricmp(a->name, name))
		{
			// unlink from hash
			if (prev)
				prev->hash_next = a->hash_next;
			else
				cmd_alias_hash[key] = a->hash_next;
			break;
		}
		prev = a;
	}

	if (!a)
		return false;	// not found

	prev = NULL;
	for (a = cmd_alias ; a ; a = a->next)
	{
		if (!Q_stricmp(a->name, name))
		{
			// unlink from alias list
			if (prev)
				prev->next = a->next;
			else
				cmd_alias = a->next;

			// free
			Q_free (a->name);
			Q_free (a->value);
			Q_free (a);
			return true;
		}
		prev = a;
	}

	assert(!"Cmd_DeleteAlias: alias list broken");
	return false;	// shut up compiler
}

void Cmd_UnAlias_f (void)
{
	char	*name;

	if (Cmd_Argc() != 2)
	{
		Com_Printf ("unalias <alias>: erase an existing alias\n");
		return;
	}

	name = Cmd_Argv(1);

	if (!Cmd_DeleteAlias(name)) {
		if (cl_warncmd.value || developer.value)
			Com_Printf ("No such alias: \"%s\"\n", name);
	}
}

// remove all aliases
void Cmd_UnAliasAll_f (void)
{
	cmd_alias_t	*a, *next;
	int i;

	for (a=cmd_alias ; a ; a=next) {
		next = a->next;
		Q_free (a->name);
		Q_free (a->value);
		Q_free (a);
	}
	cmd_alias = NULL;

	// clear hash
	for (i=0 ; i<32 ; i++) {
		cmd_alias_hash[i] = NULL;
	}
}


void Cmd_RemoveStuffedAliases (void)
{
	cmd_alias_t	*a, *next;

	for (a=cmd_alias ; a ; a=next) {
		next = a->next;
		
		if (a->flags & ALIAS_STUFFED)
			Cmd_DeleteAlias (a->name);
	}
}


void Cmd_WriteAliases (FILE *f)
{
	cmd_alias_t	*a;

	for (a = cmd_alias ; a ; a=a->next)
		if (a->flags & ALIAS_ARCHIVE)
			fprintf (f, "aliasa %s \"%s\"\n", a->name, a->value);
}

/*
=============================================================================

					LEGACY COMMANDS

=============================================================================
*/

typedef struct legacycmd_s {
	char *oldname, *newname;
	struct legacycmd_s *next;
} legacycmd_t;

static legacycmd_t *legacycmds = NULL;


static legacycmd_t *Cmd_GetLegacyCommand (char *oldname)
{
	legacycmd_t *cmd;

	for (cmd = legacycmds; cmd; cmd = cmd->next) {
		if (!Q_stricmp (cmd->oldname, oldname))
			return cmd;
	}
	return NULL;
}

void Cmd_AddLegacyCommand (char *oldname, char *newname)
{
	legacycmd_t *cmd;
	cmd = (legacycmd_t *) Q_malloc (sizeof(legacycmd_t));
	cmd->next = legacycmds;
	legacycmds = cmd;

	cmd->oldname = oldname;
	cmd->newname = newname;
}

qbool Cmd_IsLegacyCommand (char *oldname)
{
	return Cmd_GetLegacyCommand (oldname) != NULL;
}

char *Cmd_LegacyCommandValue (char *oldname)
{
	legacycmd_t *cmd;

	if (!(cmd = Cmd_GetLegacyCommand (oldname)))
		return NULL;
	return cmd->newname;
}

static qbool Cmd_LegacyCommand (void)
{
	qbool recursive = false;
	legacycmd_t *cmd;
	char	text[1024];

	if (!(cmd = Cmd_GetLegacyCommand (Cmd_Argv (0))))
		return false;

	if (!cmd->newname[0])
		return true;		// just ignore this command

	// build new command string
	strcpy (text, cmd->newname);
	strcat (text, " ");
	strlcat (text, Cmd_Args(), sizeof(text));

	assert (!recursive);
	recursive = true;
	Cmd_ExecuteString (text);
	recursive = false;

	return true;
}


/*
=============================================================================

					COMMAND EXECUTION

=============================================================================
*/

#define	MAX_ARGS		80

static	int			cmd_argc;
static	char		*cmd_argv[MAX_ARGS];
static	char		*cmd_null_string = "";
static	char		*cmd_args = NULL;

cmd_function_t	*cmd_hash_array[32];
/*static*/ cmd_function_t	*cmd_functions;		// possible commands to execute

/*
============
Cmd_Argc
============
*/
int Cmd_Argc (void)
{
	return cmd_argc;
}

/*
============
Cmd_Argv
============
*/
char *Cmd_Argv (int arg)
{
	if ( arg >= cmd_argc )
		return cmd_null_string;
	return cmd_argv[arg];	
}

/*
============
Cmd_Args

Returns a single string containing argv(1) to argv(argc()-1)
============
*/
char *Cmd_Args (void)
{
	if (!cmd_args)
		return "";
	return cmd_args;
}


/*
============
Cmd_MakeArgs

Returns a single string containing argv(start) to argv(argc()-1)
Unlike Cmd_Args, shrinks spaces between argvs
============
*/
char *Cmd_MakeArgs (int start)
{
	static char	text[1024];
	int		i;

	text[0] = 0;

	for (i = start; i < Cmd_Argc(); i++) {
		if (i > start)
			strcat (text, " ");
		strcat (text, Cmd_Argv(i));
	}

	return text;
}


/*
============
Cmd_TokenizeString

Parses the given string into command line tokens.
============
*/
void Cmd_TokenizeString (char *text)
{
	int			idx;
	static char	argv_buf[1024];
	
	idx = 0;
		
	cmd_argc = 0;
	cmd_args = NULL;
	
	while (1)
	{
		// skip whitespace
		while (*text == ' ' || *text == '\t' || *text == '\r')
		{
			text++;
		}
		
		if (*text == '\n')
		{	// a newline separates commands in the buffer
			text++;
			break;
		}

		if (!*text)
			return;
	
		if (cmd_argc == 1)
			 cmd_args = text;
			
		text = COM_Parse (text);
		if (!text)
			return;

		if (cmd_argc < MAX_ARGS)
		{
			cmd_argv[cmd_argc] = argv_buf + idx;
			strcpy (cmd_argv[cmd_argc], com_token);
			idx += strlen(com_token) + 1;
			cmd_argc++;
		}
	}
	
}


/*
============
Cmd_AddCommand
============
*/
void Cmd_AddCommand (char *cmd_name, xcommand_t function)
{
	cmd_function_t	*cmd;
	int	key;
	
	if (host_initialized)	// because hunk allocation would get stomped
		assert(!"Cmd_AddCommand after host_initialized");

#if 0
// fail if the command is a variable name
	if (Cvar_Find(cmd_name)) {
		Com_Printf ("Cmd_AddCommand: %s already defined as a var\n", cmd_name);
		return;
	}
#endif

	key = Com_HashKey (cmd_name);

// fail if the command already exists
	for (cmd=cmd_hash_array[key] ; cmd ; cmd=cmd->hash_next)
	{
		if (!Q_stricmp (cmd_name, cmd->name))
		{
			Com_Printf ("Cmd_AddCommand: %s already defined\n", cmd_name);
			return;
		}
	}

	cmd = Hunk_Alloc (sizeof(cmd_function_t));
	cmd->name = cmd_name;
	cmd->function = function;
	cmd->next = cmd_functions;
	cmd_functions = cmd;
	cmd->hash_next = cmd_hash_array[key];
	cmd_hash_array[key] = cmd;
}


/*
============
Cmd_Exists
============
*/
qbool Cmd_Exists (char *cmd_name)
{
	int	key;
	cmd_function_t	*cmd;

	key = Com_HashKey (cmd_name);
	for (cmd=cmd_hash_array[key] ; cmd ; cmd=cmd->hash_next)
	{
		if (!Q_stricmp (cmd_name, cmd->name))
			return true;
	}

	return false;
}


/*
============
Cmd_FindCommand
============
*/
cmd_function_t *Cmd_FindCommand (char *cmd_name)
{
	int	key;
	cmd_function_t	*cmd;

	key = Com_HashKey (cmd_name);
	for (cmd=cmd_hash_array[key] ; cmd ; cmd=cmd->hash_next)
	{
		if (!Q_stricmp (cmd_name, cmd->name))
			return cmd;
	}

	return NULL;
}


/*
============
Cmd_CompleteCommand
============
*/
char *Cmd_CompleteCommand (char *partial)
{
	cmd_function_t	*cmd;
	int				len;
	cmd_alias_t		*alias;
	
	len = strlen(partial);
	
	if (!len)
		return NULL;

// check for exact match
	for (cmd=cmd_functions ; cmd ; cmd=cmd->next)
		if (!Q_stricmp (partial, cmd->name))
			return cmd->name;
	for (alias=cmd_alias ; alias ; alias=alias->next)
		if (!Q_stricmp (partial, alias->name))
			return alias->name;

// check for partial match
	for (cmd=cmd_functions ; cmd ; cmd=cmd->next)
		if (!Q_strnicmp (partial, cmd->name, len))
			return cmd->name;
	for (alias=cmd_alias ; alias ; alias=alias->next)
		if (!Q_strnicmp (partial, alias->name, len))
			return alias->name;

	return NULL;
}

int Cmd_CompleteCountPossible (char *partial)
{
	cmd_function_t	*cmd;
	int		len, c = 0;
	
	len = strlen(partial);
	if (!len)
		return 0;

	for (cmd=cmd_functions ; cmd ; cmd=cmd->next)
		if (!Q_strnicmp (partial, cmd->name, len))
			c++;

	return c;
}

int Cmd_AliasCompleteCountPossible (char *partial)
{
	cmd_alias_t		*alias;
	int		len, c = 0;
	
	len = strlen(partial);
	if (!len)
		return 0;

	for (alias=cmd_alias ; alias ; alias=alias->next)
		if (!Q_strnicmp (partial, alias->name, len))
			c++;

	return c;
}


/*
===========
Cmd_CmdList_f

cmdlist [pattern [pattern2 ...]]

List commands matching any of the wildcards, or all commands
if no wildcard is specified
===========
*/
void Cmd_CmdList_f (void)
{
	cmd_function_t	*cmd;
	int	count;
	char *pattern;

	pattern = Cmd_Argc() > 1 ? Cmd_Argv(1) : NULL;
	
	count = 0;
	for (cmd = cmd_functions; cmd; cmd = cmd->next) {
		if (pattern && !Q_glob_match(pattern, cmd->name))
			continue;
		Com_Printf ("%s\n", cmd->name);
		count++;
	}

	Com_Printf ("------------\n%d %scommands\n", count, pattern ? "matching " : "");
}


/*
===========
Cmd_Z_Cmd_f

_z_cmd <command>
Just executes the rest of the string.
Can be used to do some ZQuake-specific action, e.g. "_z_cmd exec tonik_z.cfg"
===========
*/
void Cmd_Z_Cmd_f (void)
{
	Cbuf_InsertText ("\n");
	Cbuf_InsertText (Cmd_Args());
}


/*
================
Cmd_ExpandString

Expands all $cvar expressions to cvar values
If not SERVERONLY, also expands $macro expressions
Note: dest must point to a 1024 byte buffer
================
*/
char *TP_MacroString (char *s);
void Cmd_ExpandString (char *data, char *dest)
{
	unsigned int	c;
	char	buf[255];
	int		i, len;
	cvar_t	*var, *bestvar;
	int		quotes = 0;
	char	*str = NULL;
	int		name_length = 0;
#ifndef SERVERONLY
	extern int	macro_length;
#endif

	len = 0;

	while ( (c = *data) != 0)
	{
		if (c == '"')
			quotes++;

		if (c == '$' && !(quotes&1))
		{
			data++;

			// Copy the text after '$' to a temp buffer
			i = 0;
			buf[0] = 0;
			bestvar = NULL;
			while ((c = *data) > 32)
			{
				if (c == '$')
					break;
				data++;
				buf[i++] = c;
				buf[i] = 0;
				if ( (var = Cvar_Find(buf)) != NULL )
					bestvar = var;
			}

#ifndef SERVERONLY
			if (dedicated)
				str = NULL;
			else {
				str = TP_MacroString (buf);
				name_length = macro_length;
			}
			if (bestvar && (!str || (strlen(bestvar->name) > macro_length))) {
				str = bestvar->string;
				name_length = strlen(bestvar->name);
			}
#else
			if (bestvar) {
				str = bestvar->string;
				name_length = strlen(bestvar->name);
			} else
				str = NULL;
#endif

			if (str)
			{
				// check buffer size
				if (len + strlen(str) >= 1024-1)
					break;

				strcpy(&dest[len], str);
				len += strlen(str);
				i = name_length;
				while (buf[i])
					dest[len++] = buf[i++];
			}
			else
			{
				// no matching cvar or macro
				dest[len++] = '$';
				if (len + strlen(buf) >= 1024-1)
					break;
				strcpy (&dest[len], buf);
				len += strlen(buf);
			}
		}
		else
		{
			dest[len] = c;
			data++;
			len++;
			if (len >= 1024-1)
				break;
		}
	};

	dest[len] = 0;
}

// Commands allowed for msg_trigger
char *safe_commands[] = {
	"play",
	"playvol",
	"stopsound",
	"set",
	"echo",
	"say",
	"say_team",
	"alias",
	"unalias",
	"msg_trigger",
	"inc",
	"bind",
	"unbind",
	"record",
	"easyrecord",
	"stop",
	"if",
	NULL
};

/*
============
Cmd_ExecuteString

A complete command line has been parsed, so try to execute it

FIXME: this function is getting really messy...
============
*/
void Cmd_ExecuteString (char *text)
{	
	cmd_function_t	*cmd;
	cmd_alias_t		*a;
	int				key;
	static char		buf[1024];
	cbuf_t			*inserttarget;
#ifndef SERVERONLY
	char			**s;
#endif

	Cmd_ExpandString (text, buf);
	Cmd_TokenizeString (buf);

// execute the command line
	if (!Cmd_Argc())
		return;		// no tokens

	inserttarget = &cbuf_main;

#ifndef SERVERONLY
	if (cbuf_current == &cbuf_safe)
		inserttarget = &cbuf_safe;

	if (cbuf_current == &cbuf_svc) {
		if (CL_CheckServerCommand())
			return;
	}
#endif

	key = Com_HashKey (cmd_argv[0]);

// check functions
	for (cmd=cmd_hash_array[key] ; cmd ; cmd=cmd->hash_next)
	{
		if (!Q_stricmp (cmd_argv[0], cmd->name))
		{
#ifndef SERVERONLY
			// special check for msg_trigger commands
			if (cbuf_current == &cbuf_safe) {
				for (s = safe_commands; *s; s++) {
					if (!Q_stricmp(cmd_argv[0], *s))
						break;
				}
				if (!*s) {
					if (cl_warncmd.value || developer.value)
						Com_Printf ("\"%s\" cannot be used in message triggers\n", cmd_argv[0]);
					return;
				}
			}
#endif
			if (cmd->function)
				cmd->function ();
			else
				Cmd_ForwardToServer ();
			return;
		}
	}

// some bright guy decided to use "skill" as a mod command in Custom TF, sigh
	if (!strcmp(Cmd_Argv(0), "skill") && Cmd_Argc() == 1 && Cmd_FindAlias("skill"))
		goto checkaliases;

// check cvars
	if (Cvar_Command())
		return;

// check alias
checkaliases:
	for (a=cmd_alias_hash[key] ; a ; a=a->hash_next)
	{
		if (!Q_stricmp (cmd_argv[0], a->name))
		{
#ifndef SERVERONLY
			if (cbuf_current == &cbuf_svc) {
				Cbuf_AddText (a->value);
				Cbuf_AddText ("\n");
			}
			else
#endif
			{
				Cbuf_InsertTextEx (inserttarget, "\n");

				// if the alias value is a command or cvar and
				// the alias is called with parameters, add them
				if (Cmd_Argc() > 1 && !strchr(a->value, ' ') && !strchr(a->value, '\t')
					&& (Cvar_Find(a->value) || (Cmd_FindCommand(a->value)
					&& a->value[0] != '+' && a->value[0] != '-')))
				{
					Cbuf_InsertTextEx (inserttarget, Cmd_Args());
					Cbuf_InsertTextEx (inserttarget, " ");
				}

				Cbuf_InsertTextEx (inserttarget, a->value);
			}
			return;
		}
	}

	if (Cmd_LegacyCommand())
		return;

	if (!host_initialized && Cmd_Argc() > 1) {
		if (Cvar_CreateTempVar())
			return;
	}

#ifndef SERVERONLY
	if (cbuf_current != &cbuf_svc)
#endif
		if (cl_warncmd.value || developer.value)
			Com_Printf ("Unknown command \"%s\"\n", Cmd_Argv(0));
}


static qbool is_numeric (char *c)
{	
	return ( isdigit((int)(unsigned char)*c) ||
		((*c == '-' || *c == '+') && (c[1] == '.' || isdigit((int)(unsigned char)c[1]))) ||
		(*c == '.' && isdigit((int)(unsigned char)c[1])) );
}
/*
================
Cmd_If_f
================
*/
void Cmd_If_f (void)
{
	int		i, c;
	char	*op;
	qbool	result;
	char	buf[256];

	c = Cmd_Argc ();
	if (c < 5) {
		Com_Printf ("usage: if <expr1> <op> <expr2> <command> [else <command>]\n");
		return;
	}

	op = Cmd_Argv (2);
	if (!strcmp(op, "==") || !strcmp(op, "=") || !strcmp(op, "!=")
		|| !strcmp(op, "<>"))
	{
		if (is_numeric(Cmd_Argv(1)) && is_numeric(Cmd_Argv(3)))
			result = Q_atof(Cmd_Argv(1)) == Q_atof(Cmd_Argv(3));
		else
			result = !strcmp(Cmd_Argv(1), Cmd_Argv(3));

		if (op[0] != '=')
			result = !result;
	}
	else if (!strcmp(op, ">"))
		result = Q_atof(Cmd_Argv(1)) > Q_atof(Cmd_Argv(3));
	else if (!strcmp(op, "<"))
		result = Q_atof(Cmd_Argv(1)) < Q_atof(Cmd_Argv(3));
	else if (!strcmp(op, ">="))
		result = Q_atof(Cmd_Argv(1)) >= Q_atof(Cmd_Argv(3));
	else if (!strcmp(op, "<="))
		result = Q_atof(Cmd_Argv(1)) <= Q_atof(Cmd_Argv(3));
	else if (!strcmp(op, "isin"))
		result = strstr(Cmd_Argv(3), Cmd_Argv(1)) != NULL;
	else if (!strcmp(op, "!isin"))
		result = strstr(Cmd_Argv(3), Cmd_Argv(1)) == NULL;
	else {
		Com_Printf ("unknown operator: %s\n", op);
		Com_Printf ("valid operators are ==, =, !=, <>, >, <, >=, <=, isin, !isin\n");
		return;
	}		

	buf[0] = '\0';
	if (result)
	{
		for (i=4; i < c ; i++) {
			if ((i == 4) && !Q_stricmp(Cmd_Argv(i), "then"))
				continue;
			if (!Q_stricmp(Cmd_Argv(i), "else"))
				break;
			if (buf[0])
				strcat (buf, " ");
			strcat (buf, Cmd_Argv(i));
		}
	}
	else
	{
		for (i=4; i < c ; i++) {
			if (!Q_stricmp(Cmd_Argv(i), "else"))
				break;
		}

		if (i == c)
			return;
		
		for (i++ ; i < c ; i++) {
			if (buf[0])
				strcat (buf, " ");
			strcat (buf, Cmd_Argv(i));
		}
	}

	strcat (buf, "\n");
	if (!cbuf_current)
		cbuf_current = &cbuf_main;
	Cbuf_InsertTextEx (cbuf_current, buf);
}


/*
================
Cmd_CheckParm

Returns the position (1 to argc-1) in the command's argument list
where the given parameter apears, or 0 if not present
================
*/
int Cmd_CheckParm (char *parm)
{
	int i;
	
	if (!parm)
		assert(!"Cmd_CheckParm: NULL");

	for (i = 1; i < Cmd_Argc (); i++)
		if (! Q_stricmp (parm, Cmd_Argv (i)))
			return i;
			
	return 0;
}

		
/*
============
Cmd_Init
============
*/
void Cmd_Init (void)
{
//
// register our commands
//
	Cmd_AddCommand ("exec", Cmd_Exec_f);
	Cmd_AddCommand ("echo", Cmd_Echo_f);
	Cmd_AddCommand ("aliaslist", Cmd_AliasList_f);
	Cmd_AddCommand ("aliasa", Cmd_Alias_f);
	Cmd_AddCommand ("alias", Cmd_Alias_f);
	Cmd_AddCommand ("viewalias", Cmd_Viewalias_f);
	Cmd_AddCommand ("unaliasall", Cmd_UnAliasAll_f);
	Cmd_AddCommand ("unalias", Cmd_UnAlias_f);
	Cmd_AddCommand ("wait", Cmd_Wait_f);
	Cmd_AddCommand ("cmdlist", Cmd_CmdList_f);
	Cmd_AddCommand ("if", Cmd_If_f);
	Cmd_AddCommand ("_z_cmd", Cmd_Z_Cmd_f);	// ZQuake
}

/* vi: set noet ts=4 sts=4 ai sw=4: */
