/*
===============================================================================

LOAD / SAVE GAME

===============================================================================
*/

#include "server.h"
#include "sv_world.h"

// hmm...
extern int CL_Stat_Monsters(void), CL_Stat_TotalMonsters(void);
extern int CL_IntermissionRunning (void);
extern qbool scr_disabled_for_loading;

#define	SAVEGAME_COMMENT_LENGTH	39
#define	SAVEGAME_VERSION	6

/*
===============
SV_SavegameComment

Writes a SAVEGAME_COMMENT_LENGTH character comment

FIXME: What is the right place for this function?
If it stays in server, then the CL_Stat_Monsters is architecturally ugly
Move it to client?
On the other hand, if we make it fully client-independent, "save" and "load" could
be made to work even on dedicated servers.  Not sure though how useful that would be.
===============
*/
void SV_SavegameComment (char *text)
{
	int		i;
	char	kills[20];
	char	*levelname;

	for (i = 0; i < SAVEGAME_COMMENT_LENGTH; i++)
		text[i] = ' ';
	levelname = PR_GetString(sv.edicts->v.message);
	memcpy (text, levelname, min(strlen(levelname), 21));
	sprintf (kills, "kills:%3i/%-3i", CL_Stat_Monsters(), CL_Stat_TotalMonsters());
	memcpy (text+22, kills, strlen(kills));

// convert space to _ to make stdio happy
	for (i = 0; i < SAVEGAME_COMMENT_LENGTH; i++)
		if (text[i] == ' ')
			text[i] = '_';

	text[SAVEGAME_COMMENT_LENGTH] = '\0';
}


/*
===============
SV_SaveGame_f
===============
*/
void SV_SaveGame_f (void)
{
	char	name[256];
	FILE	*f;
	int		i;
	char	comment[SAVEGAME_COMMENT_LENGTH+1];

	if (Cmd_Argc() != 2) {
		Com_Printf ("save <savename> : save a game\n");
		return;
	}

	if (strstr(Cmd_Argv(1), "..")) {
		Com_Printf ("Relative pathnames are not allowed.\n");
		return;
	}

	if (sv.state != ss_active) {
		Com_Printf ("Not playing a local game.\n");
		return;
	}

	if (CL_IntermissionRunning()) {
		Com_Printf ("Can't save in intermission.\n");
		return;
	}

	if (deathmatch.value != 0 || coop.value != 0 || maxclients.value != 1) {
		Com_Printf ("Can't save multiplayer games.\n");
		return;
	}

	for (i = 1; i < MAX_CLIENTS; i++) {
		if (svs.clients[i].state == cs_spawned)
		{
			Com_Printf ("Can't save multiplayer games.\n");
			return;
		}
	}	
	
	if (svs.clients[0].state != cs_spawned) {
		Com_Printf ("Can't save, client #0 not spawned.\n");
		return;
	}

	sprintf (name, "%s/save/%s", com_gamedir, Cmd_Argv(1));
	COM_DefaultExtension (name, ".sav");
	
	Com_Printf ("Saving game to %s...\n", name);
	COM_CreatePath (name);
	f = fopen (name, "w");
	if (!f)
	{
		Com_Printf ("ERROR: couldn't open.\n");
		return;
	}
	
	fprintf (f, "%i\n", SAVEGAME_VERSION);
	SV_SavegameComment (comment);
	fprintf (f, "%s\n", comment);
	for (i=0 ; i<NUM_SPAWN_PARMS ; i++)
		fprintf (f, "%f\n", svs.clients->spawn_parms[i]);
	fprintf (f, "%d\n", current_skill);
	fprintf (f, "%s\n", sv.mapname);
	fprintf (f, "%f\n",sv.time);

// write the light styles
	for (i = 0; i < MAX_LIGHTSTYLES; i++)
	{
		if (sv.lightstyles[i])
			fprintf (f, "%s\n", sv.lightstyles[i]);
		else
			fprintf (f,"m\n");
	}


	ED_WriteGlobals (f);
	for (i=0 ; i<sv.num_edicts ; i++)
	{
		ED_Write (f, EDICT_NUM(i));
		fflush (f);
	}
	fclose (f);
	Com_Printf ("done.\n");
}


/*
===============
SV_LoadGame_f
===============
*/
void SV_LoadGame_f (void)
{
	char	name[MAX_OSPATH];
	FILE	*f;
	char	mapname[MAX_QPATH];
	float	time, tfloat;
	char	str[32768], *start;
	int		i, r;
	edict_t	*ent;
	int		entnum;
	int		version;
	float	spawn_parms[NUM_SPAWN_PARMS];
	qbool	save_disabled_for_loading;

	if (Cmd_Argc() != 2) {
		Com_Printf ("load <savename> : load a game\n");
		return;
	}

	sprintf (name, "%s/save/%s", com_gamedir, Cmd_Argv(1));
	COM_DefaultExtension (name, ".sav");
	
// we can't call SCR_BeginLoadingPlaque, because too much stack space has
// been used.  The menu calls it before stuffing loadgame command
//	SCR_BeginLoadingPlaque ();

	Com_Printf ("Loading game from %s...\n", name);
	f = fopen (name, "r");
	if (!f)
	{
		Com_Printf ("ERROR: couldn't open.\n");
		return;
	}

	fscanf (f, "%i\n", &version);
	if (version != SAVEGAME_VERSION)
	{
		fclose (f);
		Com_Printf ("Savegame is version %i, not %i\n", version, SAVEGAME_VERSION);
		return;
	}
	fscanf (f, "%s\n", str);
	for (i=0 ; i<NUM_SPAWN_PARMS ; i++)
		fscanf (f, "%f\n", &spawn_parms[i]);
// this silliness is so we can load 1.06 save files, which have float skill values
	fscanf (f, "%f\n", &tfloat);
	current_skill = (int)(tfloat + 0.1);
	Cvar_Set (&skill, va("%i", current_skill));

	Cvar_SetValue (&deathmatch, 0);
	Cvar_SetValue (&coop, 0);
	Cvar_SetValue (&teamplay, 0);
	Cvar_SetValue (&maxclients, 1);

	fscanf (f, "%s\n",mapname);
	fscanf (f, "%f\n",&time);

	save_disabled_for_loading = scr_disabled_for_loading;

	Host_EndGame ();

	// Host_EndGame disables the loading plaque, restore it
	scr_disabled_for_loading = save_disabled_for_loading;

	CL_BeginLocalConnection ();

	SV_SpawnServer (mapname, false);
	if (sv.state != ss_active)
	{
		Com_Printf ("Couldn't load map\n");
		return;
	}
	Cvar_ForceSet (&sv_paused, "1");	// pause until all clients connect
	sv.loadgame = true;

// load the light styles

	for (i=0 ; i<MAX_LIGHTSTYLES ; i++)
	{
		fscanf (f, "%s\n", str);
		sv.lightstyles[i] = Hunk_Alloc (strlen(str)+1);
		strcpy (sv.lightstyles[i], str);
	}

// load the edicts out of the savegame file
	entnum = -1;		// -1 is the globals
	while (!feof(f))
	{
		for (i=0 ; i<sizeof(str)-1 ; i++)
		{
			r = fgetc (f);
			if (r == EOF || !r)
				break;
			str[i] = r;
			if (r == '}')
			{
				i++;
				break;
			}
		}
		if (i == sizeof(str)-1)
			Host_Error ("Loadgame buffer overflow");
		str[i] = 0;
		start = str;
		start = COM_Parse(str);
		if (!com_token[0])
			break;		// end of file
		if (strcmp(com_token,"{"))
			Host_Error ("First token isn't a brace");
			
		if (entnum == -1)
		{	// parse the global vars
			ED_ParseGlobals (start);
		}
		else
		{	// parse an edict
			ent = EDICT_NUM(entnum);
			memset (&ent->v, 0, progs->entityfields * 4);
			ent->inuse = true;
			ED_ParseEdict (start, ent);
	
			// link it into the bsp tree
			if (ent->inuse)
				SV_LinkEdict (ent, false);
		}

		entnum++;
	}
	
	sv.num_edicts = entnum;
	sv.time = time;

	fclose (f);

	// FIXME: this assumes the player is using client slot #0
	for (i = 0; i < NUM_SPAWN_PARMS; i++)
		svs.clients->spawn_parms[i] = spawn_parms[i];
}
