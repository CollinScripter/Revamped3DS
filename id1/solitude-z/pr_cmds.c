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
#include "sv_world.h"


#define	RETURN_EDICT(e) (((int *)pr_globals)[OFS_RETURN] = EDICT_TO_PROG(e))
#define	RETURN_STRING(s) (((int *)pr_globals)[OFS_RETURN] = PR_SetString(s))


// Used when returning a string
// Let us hope it's large enough (no crashes, but result may be truncated)
// Well, QW had 128...
static char	pr_string_temp[512];

/*
===============================================================================

						BUILT-IN FUNCTIONS

===============================================================================
*/

/*
=================
PF_Fixme

Progs attempted to call a non-existent builtin function
=================
*/
static void PF_Fixme (void)
{
	PR_RunError ("unimplemented builtin");
}


// strcat all builtin parms starting with 'first' into a temp buffer
static char *PF_VarString (int first)
{
	int		i;
	static char out[2048];
	
	out[0] = 0;
	for (i = first; i < pr_argc; i++)
	{
		strlcat (out, G_STRING((OFS_PARM0 + i*3)), sizeof(out));
	}
	return out;
}


/*
=================
PF_error

This is a TERMINAL error, which will kill off the entire server.
Dumps self.

void error(string s, ...) = #10
=================
*/
static void PF_error (void)
{
	char	*s;
	edict_t	*ed;
	
	s = PF_VarString(0);
	Com_Printf ("======SERVER ERROR in %s:\n%s\n", PR_GetString(pr_xfunction->s_name) ,s);
	ed = PROG_TO_EDICT(pr_global_struct->self);
	ED_Print (ed);

	Host_Error ("Program error");
}


/*
=================
PF_objerror

Dumps out self, then an error message.  The program is aborted and self is
removed, but the level can continue.

void objerror(string s, ...) = #11
=================
*/
static void PF_objerror (void)
{
	char	*s;
	edict_t	*ed;
	
	s = PF_VarString(0);
	Com_Printf ("======OBJECT ERROR in %s:\n%s\n", PR_GetString(pr_xfunction->s_name),s);
	ed = PROG_TO_EDICT(pr_global_struct->self);
	ED_Print (ed);
	ED_Free (ed);
	
	Host_Error ("Program error");
}


/*
==============
PF_makevectors

Writes new values for v_forward, v_up, and v_right based on angles

void makevectors(entity e) = #1
==============
*/
static void PF_makevectors (void)
{
	AngleVectors (G_VECTOR(OFS_PARM0), PR_GLOBAL(v_forward), PR_GLOBAL(v_right), PR_GLOBAL(v_up));
}


/*
=================
PF_setorigin

This is the only valid way to move an object without using the physics of the world (setting velocity and waiting).  Directly changing origin will not set internal links correctly, so clipping would be messed up.  This should be called when an object is spawned, and then only if it is teleported.

void setorigin(entity e, vector origin) = #2
=================
*/
static void PF_setorigin (void)
{
	edict_t	*e;
	float	*org;
	
	e = G_EDICT(OFS_PARM0);
	org = G_VECTOR(OFS_PARM1);
	VectorCopy (org, e->v.origin);
	SV_LinkEdict (e, false);
}


/*
=================
PF_setsize

the size box is rotated by the current angle

void setsize(entity e, vector vmin, vector vmax) = #4
=================
*/
static void PF_setsize (void)
{
	edict_t	*e;
	float	*min, *max;

	e = G_EDICT(OFS_PARM0);
	min = G_VECTOR(OFS_PARM1);
	max = G_VECTOR(OFS_PARM2);
	VectorCopy (min, e->v.mins);
	VectorCopy (max, e->v.maxs);
	VectorSubtract (max, min, e->v.size);
	SV_LinkEdict (e, false);
}


/*
=================
PF_setmodel

Also sets size, mins, and maxs for inline bmodels

void setmodel(entity e, string m) = #3
=================
*/
static void PF_setmodel (void)
{
	int			i;
	edict_t		*e;
	char		*m, **check;
	cmodel_t	*mod;

	e = G_EDICT(OFS_PARM0);
	m = G_STRING(OFS_PARM1);

// check to see if model was properly precached
	for (i = 0, check = sv.model_name; i < MAX_MODELS && *check ; i++, check++)
		if (!strcmp(*check, m))
			goto ok;
	PR_RunError ("PF_setmodel: no precache: %s\n", m);
ok:

	e->v.model = G_INT(OFS_PARM1);
	e->v.modelindex = i;

// if it is an inline model, get the size information for it
	if (m[0] == '*') {
		mod = CM_InlineModel (m);
		VectorCopy (mod->mins, e->v.mins);
		VectorCopy (mod->maxs, e->v.maxs);
		VectorSubtract (mod->maxs, mod->mins, e->v.size);
		SV_LinkEdict (e, false);
	}
	else if (pr_nqprogs) {
		// hacks to make NQ progs happy
		if (!strcmp(PR_GetString(e->v.model), "maps/b_explob.bsp")) {
			VectorClear (e->v.mins);
			VectorSet (e->v.maxs, 32, 32, 64);
		} else {
			// FTE does this, so we do, too; I'm not sure if it makes a difference
			VectorSet (e->v.mins, -16, -16, -16);
			VectorSet (e->v.maxs, 16, 16, 16);
		}
		VectorSubtract (e->v.maxs, e->v.mins, e->v.size);
		SV_LinkEdict (e, false);
	}
}


/*
=================
PF_bprint

broadcast print to everyone on server

void bprint(string s, ...) = #23
=================
*/
static void PF_bprint (void)
{
	char		*s;
	int			level;
	
	if (pr_nqprogs) {
		level = PRINT_HIGH;
		s = PF_VarString(0);
	} else {
		level = G_FLOAT(OFS_PARM0);
		s = PF_VarString(1);
	}

	SV_BroadcastPrintf (level, "%s", s);
}


/*
=================
PF_sprint

single print to a specific client

void sprint(entity client, float level, string s, ...) = #24
=================
*/
static void PF_sprint (void)
{
	client_t	*cl;
	int			entnum;
	int			level;
	char		*buf, *str;
	int			buflen, len;
	int			i;
	qbool		flush = false, flushboth = false;
	
	entnum = G_EDICTNUM(OFS_PARM0);
	if (pr_nqprogs) {
		level = PRINT_HIGH;
		str = PF_VarString(1);
	} else {
		level = G_FLOAT(OFS_PARM1);
		str = PF_VarString(2);
	}
	
	if (entnum < 1 || entnum > MAX_CLIENTS)
	{
		Com_Printf ("tried to sprint to a non-client\n");
		return;
	}
		
	cl = &svs.clients[entnum-1];
	
	buf = cl->sprint_buf;
	buflen = strlen (buf);
	len = strlen (str);

	if (pr_nqprogs) {
		// This is a hack to prevent pickup messages from showing up with msg 1
		if (!buflen) {
			cl->sprint_nq_low_level = false;
			if (!strncmp(str, "You get ", 8) || !strncmp(str, "You got ", 8)
			|| !strncmp(str, "You receive ", 12))
				cl->sprint_nq_low_level = true;
		}
		if (cl->sprint_nq_low_level)
			level = PRINT_LOW;
		if (strchr(str, '\n'))
			cl->sprint_nq_low_level = false;
	}

	// flush the buffer if there's not enough space
	// also flush if sprint level has changed
	// or if str is a colored message
	if (len >= sizeof(cl->sprint_buf)
		|| str[0] == 1 || str[0] == 2)		// a colored message
		flushboth = true;
	else if (buflen + len >= sizeof(cl->sprint_buf)
		|| level != cl->sprint_level)
		flush = true;

	if ((flush || flushboth) && buflen) {
		SV_ClientPrintf (cl, cl->sprint_level, "%s", buf);
		buf[0] = 0;
	}

	if (flushboth) {
		SV_ClientPrintf (cl, level, "%s", str);
		return;
	}

	strcat (buf, str);
	cl->sprint_level = level;
	buflen += len;

	// flush complete (\n terminated) strings
	for (i=buflen-1 ; i>=0 ; i--) {
		if (buf[i] == '\n') {
			buf[i] = 0;
			SV_ClientPrintf (cl, cl->sprint_level, "%s\n", buf);
			// move the remainder to buffer beginning
			strcpy (buf, buf + i + 1);
			return;
		}
	}
}


/*
=================
PF_centerprint

single print to a specific client

void centerprint(entity client, string s, ...) = #73
=================
*/
static void PF_centerprint (void)
{
	char		*s;
	int			entnum;
	client_t	*cl;

	entnum = G_EDICTNUM(OFS_PARM0);
	s = PF_VarString(1);
	
	if (entnum < 1 || entnum > MAX_CLIENTS)
	{
		Com_Printf ("tried to sprint to a non-client\n");
		return;
	}
		
	cl = &svs.clients[entnum-1];

	ClientReliableWrite_Begin (cl, svc_centerprint);
	ClientReliableWrite_String (s);
	ClientReliableWrite_End ();
}


/*
=================
PF_normalize

vector normalize(vector v) = #9
=================
*/
static void PF_normalize (void)
{
	float	*value1;
	vec3_t	newvalue;
	float	new;
	
	value1 = G_VECTOR(OFS_PARM0);

	new = value1[0] * value1[0] + value1[1] * value1[1] + value1[2]*value1[2];
	
	if (new == 0)
		newvalue[0] = newvalue[1] = newvalue[2] = 0;
	else
	{
		new = 1/sqrt(new);
		newvalue[0] = value1[0] * new;
		newvalue[1] = value1[1] * new;
		newvalue[2] = value1[2] * new;
	}
	
	VectorCopy (newvalue, G_VECTOR(OFS_RETURN));	
}


/*
=================
PF_vlen

float vlen(vector v) = #12
=================
*/
static void PF_vlen (void)
{
	float	*value1;
	float	new;
	
	value1 = G_VECTOR(OFS_PARM0);

	new = DotProduct(value1, value1);
	
	G_FLOAT(OFS_RETURN) = (new) ? sqrt(new) : 0;
}


/*
=================
PF_vectoyaw

float vectoyaw(vector v) = #13
=================
*/
static void PF_vectoyaw (void)
{
	float	*value1;
	float	yaw;
	
	value1 = G_VECTOR(OFS_PARM0);

	if (value1[1] == 0 && value1[0] == 0)
		yaw = 0;
	else
	{
		yaw = atan2(value1[1], value1[0]) * 180 / M_PI;
		if (yaw < 0)
			yaw += 360;
	}

	G_FLOAT(OFS_RETURN) = yaw;
}


/*
=================
PF_vectoangles

vector vectoangles(vector v) = #51
=================
*/
static void PF_vectoangles (void)
{
	vectoangles (G_VECTOR(OFS_PARM0), G_VECTOR(OFS_RETURN));
}


/*
=================
PF_Random

Returns a number from 0 <= num < 1

float random() = #7
=================
*/
static void PF_random (void)
{
	float		num;
		
	num = (rand ()&0x7fff) / ((float)0x7fff);
	
	G_FLOAT(OFS_RETURN) = num;
}


/*
=================
PF_particle

particle(origin, dir, color, count [,replacement_te [,replacement_count]]) = #48
=================
*/
static void PF_particle (void)
{
	float	*org, *dir;
	float	color, count;
	int		replacement_te;
	int		replacement_count = 0 /* suppress compiler warning */;
			
	org = G_VECTOR(OFS_PARM0);
	dir = G_VECTOR(OFS_PARM1);
	color = G_FLOAT(OFS_PARM2);
	count = G_FLOAT(OFS_PARM3);

	// Progs should provide a tempentity code and particle count for the case
	// when a client doesn't support svc_particle
	if (pr_argc >= 5) {
		replacement_te = G_FLOAT(OFS_PARM4);
		replacement_count = (pr_argc >= 6) ? G_FLOAT(OFS_PARM5) : 1;
	} else {
		// To aid porting of NQ mods, if the extra arguments are not provided, try
		// to figure out what progs want by inspecting color and count
		if (count == 255) {
			replacement_te = TE_EXPLOSION;		// count is not used
		} else if (color == 73) {
			replacement_te = TE_BLOOD;
			replacement_count = 1;	// FIXME: use count / <some value>?
		} else if (color == 225) {
			replacement_te = TE_LIGHTNINGBLOOD;	// count is not used
		} else {
			replacement_te = 0;		// don't send anything
		}
	}

	SV_StartParticle (org, dir, color, count, replacement_te, replacement_count);
}


/*
=================
PF_ambientsound

void ambientsound(vector pos, string samp, float vol, float atten) = #74
=================
*/
static void PF_ambientsound (void)
{
	char		**check;
	char		*samp;
	float		*pos;
	float 		vol, attenuation;
	int			i, soundnum;

	pos = G_VECTOR (OFS_PARM0);
	samp = G_STRING(OFS_PARM1);
	vol = G_FLOAT(OFS_PARM2);
	attenuation = G_FLOAT(OFS_PARM3);

// check to see if samp was properly precached
	for (soundnum = 1, check = sv.sound_name + 1;
		soundnum < MAX_SOUNDS && *check;
		check++, soundnum++)
	{
		if (!strcmp(*check, samp))
			break;
	}
			
	if (!*check)
	{
		Com_Printf ("no precache: %s\n", samp);
		return;
	}

// add an svc_spawnambient command to the level signon packet
	MSG_WriteByte (&sv.signon, svc_spawnstaticsound);
	for (i = 0; i < 3; i++)
		MSG_WriteCoord (&sv.signon, pos[i]);
	MSG_WriteByte (&sv.signon, soundnum);
	MSG_WriteByte (&sv.signon, vol*255);
	MSG_WriteByte (&sv.signon, attenuation*64);

}


/*
=================
PF_sound

Each entity can have eight independent sound sources, like voice,
weapon, feet, etc.

Channel 0 is an auto-allocate channel, the others override anything
already running on that entity/channel pair.

An attenuation of 0 will play full volume everywhere in the level.
Larger attenuations will drop off.

void sound(entity e, float chan, string samp) = #8

=================
*/
static void PF_sound (void)
{
	char		*sample;
	int			channel;
	edict_t		*entity;
	int 		volume;
	float attenuation;
		
	entity = G_EDICT(OFS_PARM0);
	channel = G_FLOAT(OFS_PARM1);
	sample = G_STRING(OFS_PARM2);
	volume = G_FLOAT(OFS_PARM3) * 255;
	attenuation = G_FLOAT(OFS_PARM4);
	
	SV_StartSound (entity, channel, sample, volume, attenuation, NULL);
}

/*
=================
PF_debugbreak

void debugbreak() = #6
=================
*/
static void PF_debugbreak (void)
{
	assert (false);		// drop to debugger
	PR_RunError ("break statement");	// just in case debugbreak is called in a release build
}


/*
=================
PF_traceline

Used for use tracing and shot targeting.
Traces are blocked by bbox and exact bsp entities, and also slide box entities,
unless nomonsters flag is set.

An entity will also be ignored for testing if ent == ignore,
ent == ignore->owner, or ent->owner == ignore.

void traceline(vector v1, vector v2, float nomonsters, entity ignore) = #16
=================
*/
static void PF_traceline (void)
{
	float	*v1, *v2;
	trace_t	trace;
	int		nomonsters;
	edict_t	*ent;

	v1 = G_VECTOR(OFS_PARM0);
	v2 = G_VECTOR(OFS_PARM1);
	nomonsters = G_FLOAT(OFS_PARM2);
	ent = G_EDICT(OFS_PARM3);

	trace = SV_Trace (v1, vec3_origin, vec3_origin, v2, nomonsters, ent);

	PR_GLOBAL(trace_allsolid) = trace.allsolid;
	PR_GLOBAL(trace_startsolid) = trace.startsolid;
	PR_GLOBAL(trace_fraction) = trace.fraction;
	PR_GLOBAL(trace_inwater) = trace.inwater;
	PR_GLOBAL(trace_inopen) = trace.inopen;
	VectorCopy (trace.endpos, PR_GLOBAL(trace_endpos));
	VectorCopy (trace.plane.normal, PR_GLOBAL(trace_plane_normal));
	PR_GLOBAL(trace_plane_dist) =  trace.plane.dist;	
	if (trace.e.ent)
		PR_GLOBAL(trace_ent) = EDICT_TO_PROG(trace.e.ent);
	else
		PR_GLOBAL(trace_ent) = EDICT_TO_PROG(sv.edicts);
}


//============================================================================

// Unlike Quake's Mod_LeafPVS, CM_LeafPVS returns a pointer to static data
// uncompressed at load time, so it's safe to store for future use
static byte	*checkpvs;

int PF_newcheckclient (int check)
{
	int		i;
	edict_t	*ent;
	vec3_t	org;

// cycle to the next one

	if (check < 1)
		check = 1;
	if (check > MAX_CLIENTS)
		check = MAX_CLIENTS;

	if (check == MAX_CLIENTS)
		i = 1;
	else
		i = check + 1;

	for ( ;  ; i++)
	{
		if (i == MAX_CLIENTS+1)
			i = 1;

		ent = EDICT_NUM(i);

		if (i == check)
			break;	// didn't find anything else

		if (!ent->inuse)
			continue;
		if (ent->v.health <= 0)
			continue;
		if ((int)ent->v.flags & FL_NOTARGET)
			continue;

	// anything that is a client, or has a client as an enemy
		break;
	}

// get the PVS for the entity
	VectorAdd (ent->v.origin, ent->v.view_ofs, org);
	checkpvs = CM_LeafPVS (CM_PointInLeaf(org));

	return i;
}


/*
=================
PF_checkclient

Returns a client (or object that has a client enemy) that would be a
valid target.

If there are more than one valid options, they are cycled each frame

If (self.origin + self.viewofs) is not in the PVS of the current target,
it is not returned at all.

entity checkclient() = #17
=================
*/
#define	MAX_CHECK	16
static void PF_checkclient (void)
{
	edict_t	*ent, *self;
	int		l;
	vec3_t	vieworg;
	
// find a new check if on a new frame
	if (sv.time - sv.lastchecktime >= 0.1)
	{
		sv.lastcheck = PF_newcheckclient (sv.lastcheck);
		sv.lastchecktime = sv.time;
	}

// return check if it might be visible	
	ent = EDICT_NUM(sv.lastcheck);
	if (!ent->inuse || ent->v.health <= 0)
	{
		RETURN_EDICT(sv.edicts);
		return;
	}

// if current entity can't possibly see the check entity, return 0
	self = PROG_TO_EDICT(pr_global_struct->self);
	VectorAdd (self->v.origin, self->v.view_ofs, vieworg);
	l = CM_Leafnum(CM_PointInLeaf(vieworg)) - 1;
	if ( (l<0) || !(checkpvs[l>>3] & (1<<(l&7)) ) )
	{
		RETURN_EDICT(sv.edicts);
		return;
	}

// might be able to see it
	RETURN_EDICT(ent);
}

//============================================================================


/*
=================
PF_stuffcmd

Sends text over to the client's execution buffer

void stuffcmd(entity client, string s) = #21;
=================
*/
static void PF_stuffcmd (void)
{
	int		entnum;
	client_t	*cl;
	char	*buf, *str;
	int		buflen, newlen;
	int		i;
	
	entnum = G_EDICTNUM(OFS_PARM0);
	if (entnum < 1 || entnum > MAX_CLIENTS)
		PR_RunError ("Parm 0 not a client");
	cl = &svs.clients[entnum-1];
	str = G_STRING(OFS_PARM1);	

	buf = cl->stufftext_buf;

	if (!strcmp(str, "disconnect\n")) {
		// so long and thanks for all the fish
		cl->drop = true;
		buf[0] = 0;
		return;
	}

	buflen = strlen (buf);
	newlen = strlen (str);

	if (buflen + newlen >= MAX_STUFFTEXT-1) {
		// flush the buffer because there's no space left
		if (buflen) {
			ClientReliableWrite_Begin (cl, svc_stufftext);
			ClientReliableWrite_String (buf);
			ClientReliableWrite_End ();
			buf[0] = 0;
		}
		if (newlen >= MAX_STUFFTEXT-1) {
			ClientReliableWrite_Begin (cl, svc_stufftext);
			ClientReliableWrite_String (str);
			ClientReliableWrite_End ();
			return;
		}
	}

	strcat (buf, str);
	buflen += newlen;

	// flush complete (\n terminated) strings
	for (i=buflen-1 ; i>=0 ; i--) {
		if (buf[i] == '\n') {
			ClientReliableWrite_Begin (cl, svc_stufftext);
			ClientReliableWrite_SZ (buf, i+1);
			ClientReliableWrite_Byte (0);
			ClientReliableWrite_End ();

			// move the remainder to buffer beginning
			strcpy (buf, buf + i + 1);
			return;
		}
	}
}


/*
=================
PF_localcmd

Sends text over to the server's execution buffer

void localcmd(string cmd) = #46
=================
*/
static void PF_localcmd (void)
{
	char	*str;
	
	str = G_STRING(OFS_PARM0);

	if (pr_nqprogs && !strcmp(str, "restart\n")) {
		Cbuf_AddText (va("map %s\n", host_mapname.string));
		return;
	}

	Cbuf_AddText (str);
}


/*
=================
PF_cvar

float cvar(string) = #45
=================
*/
static void PF_cvar (void)
{
	char	*str, *temp;

	str = G_STRING(OFS_PARM0);

	if (!Q_stricmp (str, "pr_checkextension")) {
		// we do support PF_checkextension
		G_FLOAT(OFS_RETURN) = 1.0;
		return;
	}

	if (!Cvar_Find (str) && (temp = Cmd_LegacyCommandValue (str)))
		str = temp;

	G_FLOAT(OFS_RETURN) = Cvar_Value (str);
}



/*
=================
PF_cvar_set

void cvar_set(string var, string val) = #72
=================
*/
static void PF_cvar_set (void)
{
	char	*var_name, *val, *temp;
	cvar_t	*var;

	var_name = G_STRING(OFS_PARM0);
	val = G_STRING(OFS_PARM1);

	if (!(var = Cvar_Find (var_name)) && (temp = Cmd_LegacyCommandValue (var_name)))
		var = Cvar_Find (temp);

	if (!var) {
		Com_DPrintf ("PF_cvar_set: variable %s not found\n", var_name);
		return;
	}

	Cvar_Set (var, val);
}


/*
=================
PF_findradius

Returns a chain of entities that have origins within a spherical area

entity findradius(vector origin, float radius) = #22
=================
*/
static void PF_findradius (void)
{
	int			i, j, numtouch;
	edict_t		*touchlist[MAX_EDICTS], *ent, *chain;
	float		rad, rad2, *org;
	vec3_t		mins, maxs, eorg;

	org = G_VECTOR(OFS_PARM0);
	rad = G_FLOAT(OFS_PARM1);
	rad2 = rad * rad;

	for (i = 0; i < 3; i++)
	{
		mins[i] = org[i] - rad - 1;		// enlarge the bbox a bit
		maxs[i] = org[i] + rad + 1;
	}

	numtouch = SV_AreaEdicts (mins, maxs, touchlist, MAX_EDICTS, AREA_SOLID);
	numtouch += SV_AreaEdicts (mins, maxs, &touchlist[numtouch], MAX_EDICTS - numtouch, AREA_TRIGGERS);

	chain = (edict_t *)sv.edicts;

// touch linked edicts
	for (i = 0; i < numtouch; i++)
	{
		ent = touchlist[i];
		if (ent->v.solid == SOLID_NOT)
			continue;	// FIXME?

		for (j = 0; j < 3; j++)
			eorg[j] = org[j] - (ent->v.origin[j] + (ent->v.mins[j] + ent->v.maxs[j]) * 0.5);			
		if (DotProduct(eorg, eorg) > rad2)
			continue;

		ent->v.chain = EDICT_TO_PROG(chain);
		chain = ent;
	}

	RETURN_EDICT(chain);
}


/*
=================
PF_dprint

void dprint(string s, ...) = #25
=================
*/
static void PF_dprint (void)
{
	Com_Printf ("%s", PF_VarString(0));
}


/*
=================
PF_ftos

void ftos(string s) = #26
=================
*/
static void PF_ftos (void)
{
	float	v;
	int	i;

	v = G_FLOAT(OFS_PARM0);

	if (v == (int)v)
		snprintf (pr_string_temp, sizeof(pr_string_temp), "%d", (int)v);
	else
	{
		snprintf (pr_string_temp, sizeof(pr_string_temp), "%f", v);

		for (i=strlen(pr_string_temp)-1 ; i>0 && pr_string_temp[i]=='0' ; i--)
			pr_string_temp[i] = 0;
		if (pr_string_temp[i] == '.')
			pr_string_temp[i] = 0;
	}

	G_INT(OFS_RETURN) = PR_SetString(pr_string_temp);
}

/*
=================
PF_fabs

float fabs(float f) = #43
=================
*/
static void PF_fabs (void)
{
	float	v;
	v = G_FLOAT(OFS_PARM0);
	G_FLOAT(OFS_RETURN) = fabs(v);
}


/*
=================
PF_vtos

void vtos(string s) = #27
=================
*/
static void PF_vtos (void)
{
	sprintf (pr_string_temp, "'%5.1f %5.1f %5.1f'", G_VECTOR(OFS_PARM0)[0], G_VECTOR(OFS_PARM0)[1], G_VECTOR(OFS_PARM0)[2]);
	G_INT(OFS_RETURN) = PR_SetString(pr_string_temp);
}


/*
=================
PF_spawn

entity spawn() = #14
=================
*/
static void PF_Spawn (void)
{
	edict_t	*ed;
	ed = ED_Alloc();
	RETURN_EDICT(ed);
}


/*
=================
PF_remove

void remove(entity e) = #15
=================
*/
static void PF_Remove (void)
{
	edict_t	*ed;
	int		num;

	ed = G_EDICT(OFS_PARM0);

	num = NUM_FOR_EDICT(ed);
	if (num >= 0 && num <= MAX_CLIENTS)
		return;		// world and clients cannot be removed

	ED_Free (ed);
}


/*
=================
PF_find

entity find(entity start, .string field, string match) = #18;
=================
*/
static void PF_Find (void)
{
	int		e;	
	int		f;
	char	*s, *t;
	edict_t	*ed;
	
	e = G_EDICTNUM(OFS_PARM0);
	f = G_INT(OFS_PARM1);
	s = G_STRING(OFS_PARM2);
	if (!s)
		PR_RunError ("PF_Find: bad search string");
		
	for (e++ ; e < sv.num_edicts ; e++)
	{
		ed = EDICT_NUM(e);
		if (!ed->inuse)
			continue;
		t = E_STRING(ed,f);
		if (!t)
			continue;
		if (!strcmp(t,s))
		{
			RETURN_EDICT(ed);
			return;
		}
	}
	
	RETURN_EDICT(sv.edicts);
}


static void PR_CheckEmptyString (char *s)
{
	if (s[0] <= ' ')
		PR_RunError ("Bad string");
}


/*
===============
PF_precache_file

string precache_file(string s) = #68
===============
*/
static void PF_precache_file (void)
{	// precache_file is only used to copy files with qcc, it does nothing
	G_INT(OFS_RETURN) = G_INT(OFS_PARM0);
}


/*
===============
PF_precache_sound

void precache_sound(string s) = #19
===============
*/
static void PF_precache_sound (void)
{
	char	*s;
	int		i;
	
	if (sv.state != ss_loading)
		PR_RunError ("PF_Precache_*: Precache can only be done in spawn functions");
		
	s = G_STRING(OFS_PARM0);
	G_INT(OFS_RETURN) = G_INT(OFS_PARM0);
	PR_CheckEmptyString (s);
	
	for (i = 1; i < MAX_SOUNDS; i++)
	{
		if (!sv.sound_name[i]) {
			sv.sound_name[i] = s;
			return;
		}
		if (!strcmp(sv.sound_name[i], s))
			return;
	}
	PR_RunError ("PF_precache_sound: overflow");
}


/*
===============
PF_precache_model

void precache_model(string s) = #20
===============
*/
static void PF_precache_model (void)
{
	char	*s;
	int		i;
	
	if (sv.state != ss_loading)
		PR_RunError ("PF_Precache_*: Precache can only be done in spawn functions");
		
	s = G_STRING(OFS_PARM0);
	G_INT(OFS_RETURN) = G_INT(OFS_PARM0);
	PR_CheckEmptyString (s);

	for (i = 1; i < MAX_MODELS; i++)
	{
		if (!sv.model_name[i]) {
			sv.model_name[i] = s;
			return;
		}
		if (!strcmp(sv.model_name[i], s))
			return;
	}
	PR_RunError ("PF_precache_model: overflow");
}


/*
===============
PF_coredump

void coredump() = #28
===============
*/
static void PF_coredump (void)
{
	ED_PrintEdicts_f ();
}


/*
===============
PF_traceon

void traceon() = #29
===============
*/
static void PF_traceon (void)
{
	pr_trace = true;
}


/*
===============
PF_traceoff

void traceoff() = #30
===============
*/
static void PF_traceoff (void)
{
	pr_trace = false;
}


/*
===============
PF_eprint

debug print an entire entity

void eprint(entity e) = #31
===============
*/
static void PF_eprint (void)
{
	ED_PrintNum (G_EDICTNUM(OFS_PARM0));
}


/*
===============
PF_walkmove

float walkmove(float yaw, float dist) = #32
===============
*/
static void PF_walkmove (void)
{
	edict_t	*ent;
	float	yaw, dist;
	vec3_t	move;
	dfunction_t	*oldf;
	int 	oldself;
	
	ent = PROG_TO_EDICT(pr_global_struct->self);
	yaw = G_FLOAT(OFS_PARM0);
	dist = G_FLOAT(OFS_PARM1);
	
	if ( !( (int)ent->v.flags & (FL_ONGROUND|FL_FLY|FL_SWIM) ) )
	{
		G_FLOAT(OFS_RETURN) = 0;
		return;
	}

	yaw = yaw*M_PI*2 / 360;
	
	move[0] = cos(yaw)*dist;
	move[1] = sin(yaw)*dist;
	move[2] = 0;

// save program state, because SV_movestep may call other progs
	oldf = pr_xfunction;
	oldself = pr_global_struct->self;
	
	G_FLOAT(OFS_RETURN) = SV_movestep(ent, move, true);
	
	
// restore program state
	pr_xfunction = oldf;
	pr_global_struct->self = oldself;
}


/*
===============
PF_droptofloor

void droptofloor() = #34
===============
*/
static void PF_droptofloor (void)
{
	edict_t		*ent;
	vec3_t		end;
	trace_t		trace;
	
	ent = PROG_TO_EDICT(pr_global_struct->self);

	VectorCopy (ent->v.origin, end);
	end[2] -= 256;
	
	trace = SV_Trace (ent->v.origin, ent->v.mins, ent->v.maxs, end, false, ent);

	if (trace.fraction == 1 || trace.allsolid)
		G_FLOAT(OFS_RETURN) = 0;
	else
	{
		VectorCopy (trace.endpos, ent->v.origin);
		SV_LinkEdict (ent, false);
		ent->v.flags = (int)ent->v.flags | FL_ONGROUND;
		ent->v.groundentity = EDICT_TO_PROG(trace.e.ent);
		G_FLOAT(OFS_RETURN) = 1;
	}
}


/*
===============
PF_lightstyle

void lightstyle(float style, string value) = #35
===============
*/
static void PF_lightstyle (void)
{
	int		style;
	char	*val;
	client_t	*client;
	int			j;
	
	style = G_FLOAT(OFS_PARM0);
	val = G_STRING(OFS_PARM1);

// change the string in sv
	sv.lightstyles[style] = val;
	
// send message to all clients on this server
	if (sv.state != ss_active)
		return;
	
	for (j=0, client = svs.clients ; j<MAX_CLIENTS ; j++, client++)
		if ( client->state == cs_spawned )
		{
			ClientReliableWrite_Begin (client, svc_lightstyle);
			ClientReliableWrite_Char (style);
			ClientReliableWrite_String (val);
			ClientReliableWrite_End ();
		}
}


/*
===============
PF_rint

float rint(float f) = #36
===============
*/
static void PF_rint (void)
{
	float	f;
	f = G_FLOAT(OFS_PARM0);
	if (f > 0)
		G_FLOAT(OFS_RETURN) = (int)(f + 0.5);
	else
		G_FLOAT(OFS_RETURN) = (int)(f - 0.5);
}


/*
===============
PF_floor

float floor(float f) = #37
===============
*/
static void PF_floor (void)
{
	G_FLOAT(OFS_RETURN) = floor(G_FLOAT(OFS_PARM0));
}


/*
===============
PF_ceil

float ceil(float f) = #38
===============
*/
static void PF_ceil (void)
{
	G_FLOAT(OFS_RETURN) = ceil(G_FLOAT(OFS_PARM0));
}


/*
=============
PF_checkbottom

float checkbottom(entity e) = #40
=============
*/
static void PF_checkbottom (void)
{
	edict_t	*ent;
	
	ent = G_EDICT(OFS_PARM0);

	G_FLOAT(OFS_RETURN) = SV_CheckBottom (ent);
}


/*
=============
PF_pointcontents

float pointcontents(vector v) = #41
=============
*/
static void PF_pointcontents (void)
{
	float	*v;
	
	v = G_VECTOR(OFS_PARM0);

	G_FLOAT(OFS_RETURN) = SV_PointContents (v);	
}


/*
=================
PF_nextent

entity nextent(entity) = #47
=================
*/
static void PF_nextent (void)
{
	int		i;
	edict_t	*ent;
	
	i = G_EDICTNUM(OFS_PARM0);
	while (1)
	{
		i++;
		if (i == sv.num_edicts)
		{
			RETURN_EDICT(sv.edicts);
			return;
		}
		ent = EDICT_NUM(i);
		if (ent->inuse || i <= MAX_CLIENTS /* compatibility */)
		{
			RETURN_EDICT(ent);
			return;
		}
	}
}


/*
=================
PF_aim

Used to pick a vector for the player to shoot along.
Now a stub.

vector aim(entity, missilespeed) = #44
=================
*/
static void PF_aim (void)
{
//	ent = G_EDICT(OFS_PARM0);
//	speed = G_FLOAT(OFS_PARM1);
	VectorCopy (PR_GLOBAL(v_forward), G_VECTOR(OFS_RETURN));
}


/*
=================
PF_changeyaw

This was a major timewaster in progs, so it was converted to C

void changeyaw() = #49
=================
*/
void PF_changeyaw (void)
{
	edict_t		*ent;
	float		ideal, current, move, speed;
	
	ent = PROG_TO_EDICT(pr_global_struct->self);
	current = anglemod( ent->v.angles[1] );
	ideal = ent->v.ideal_yaw;
	speed = ent->v.yaw_speed;
	
	if (current == ideal)
		return;
	move = ideal - current;
	if (ideal > current)
	{
		if (move >= 180)
			move = move - 360;
	}
	else
	{
		if (move <= -180)
			move = move + 360;
	}
	if (move > 0)
	{
		if (move > speed)
			move = speed;
	}
	else
	{
		if (move < -speed)
			move = -speed;
	}
	
	ent->v.angles[1] = anglemod (current + move);
}


/*
===============================================================================

MESSAGE WRITING

===============================================================================
*/

#define	MSG_BROADCAST	0		// unreliable to all
#define	MSG_ONE			1		// reliable to one (msg_entity)
#define	MSG_ALL			2		// reliable to all
#define	MSG_INIT		3		// write to the init string
#define	MSG_MULTICAST	4		// for multicast()

sizebuf_t *WriteDest (void)
{
	int		dest;
//	int		entnum;
//	edict_t	*ent;

	dest = G_FLOAT(OFS_PARM0);
	switch (dest)
	{
	case MSG_BROADCAST:
		return &sv.datagram;
	
	case MSG_ONE:
		Host_Error("Shouldn't be at MSG_ONE");
#if 0
		ent = PROG_TO_EDICT(PR_GLOBAL(msg_entity));
		entnum = NUM_FOR_EDICT(ent);
		if (entnum < 1 || entnum > MAX_CLIENTS)
			PR_RunError ("WriteDest: not a client");
		return &svs.clients[entnum-1].netchan.message;
#endif
		
	case MSG_ALL:
		return &sv.reliable_datagram;
	
	case MSG_INIT:
		if (sv.state != ss_loading)
			PR_RunError ("PF_Write_*: MSG_INIT can only be written in spawn functions");
		return &sv.signon;

	case MSG_MULTICAST:
		return &sv.multicast;

	default:
		PR_RunError ("WriteDest: bad destination");
		break;
	}
	
	return NULL;
}


static client_t *Write_GetClient(void)
{
	int		entnum;
	edict_t	*ent;

	ent = PROG_TO_EDICT(PR_GLOBAL(msg_entity));
	entnum = NUM_FOR_EDICT(ent);
	if (entnum < 1 || entnum > MAX_CLIENTS)
		PR_RunError ("WriteDest: not a client");
	return &svs.clients[entnum-1];
}


// this is an extremely nasty hack
static void CheckIntermission (void)
{
	sizebuf_t *msg = WriteDest();

	if (G_FLOAT(OFS_PARM1) != svc_intermission)
		return;

	if ( (msg->cursize == 2 && msg->data[0] == svc_cdtrack)	/* QW progs send svc_cdtrack first */
		|| msg->cursize == 0  /* just in case */ )
	{
		sv.intermission_running = true;
		sv.intermission_hunt = 1;	// start looking for WriteCoord's
		// prefix the svc_intermission message with an sv.time update
		// to make sure intermission screen has the right value
		MSG_WriteByte (&sv.reliable_datagram, svc_updatestatlong);
		MSG_WriteByte (&sv.reliable_datagram, STAT_TIME);
		MSG_WriteLong (&sv.reliable_datagram, (int)(sv.time * 1000));
	}
}


#ifdef WITH_NQPROGS
static byte nqp_buf_data[1024] /* must be large enough for svc_finale text */;
static sizebuf_t nqp_buf;
static qbool nqp_ignore_this_frame;
static int nqp_expect;

void NQP_Reset (void)
{
	nqp_ignore_this_frame = false;
	nqp_expect = 0;
	SZ_Init (&nqp_buf, nqp_buf_data, sizeof(nqp_buf_data));
}

static void NQP_Flush (int count)
{
// FIXME, we make no distinction reliable or not
	assert (count <= nqp_buf.cursize);
	SZ_Write (&sv.reliable_datagram, nqp_buf_data, count);
	memcpy (nqp_buf_data, nqp_buf_data + count, nqp_buf.cursize - count);
	nqp_buf.cursize -= count;
}

static void NQP_Skip (int count)
{
	assert (count <= nqp_buf.cursize);
	memcpy (nqp_buf_data, nqp_buf_data + count, nqp_buf.cursize - count);
	nqp_buf.cursize -= count;
}

static void NQP_Process (void)
{
	int cmd;

	if (nqp_ignore_this_frame) {
		SZ_Clear (&nqp_buf);
		return;
	}

	while (1) {
		if (nqp_expect) {
			if (nqp_buf.cursize >= nqp_expect) {
				NQP_Flush (nqp_expect);
				nqp_expect = 0;
			}
			else
				break;
		}

		if (!nqp_buf.cursize)
			break;

		nqp_expect = 0;

		cmd = nqp_buf_data[0];
		if (cmd == svc_killedmonster || cmd == svc_foundsecret || cmd == svc_sellscreen)
			nqp_expect = 1;
		else if (cmd == svc_cdtrack) {
			if (nqp_buf.cursize < 3)
				goto waitformore;
			NQP_Flush (2);
			NQP_Skip (1);
		}
		else if (cmd == svc_finale) {
			byte *p = memchr (nqp_buf_data + 1, 0, nqp_buf.cursize - 1);
			if (!p)
				goto waitformore;
			nqp_expect = (p - nqp_buf_data) + 1;
		}
		else if (cmd == svc_intermission) {
			int i;
			NQP_Flush (1);
			for (i = 0; i < 3; i++)
				MSG_WriteCoord (&sv.reliable_datagram, svs.clients[0].edict->v.origin[i]);
			for (i = 0; i < 3; i++)
				MSG_WriteAngle (&sv.reliable_datagram, svs.clients[0].edict->v.angles[i]);
		}
		else if (cmd == nq_svc_cutscene) {
			byte *p = memchr (nqp_buf_data + 1, 0, nqp_buf.cursize - 1);
			if (!p)
				goto waitformore;
			MSG_WriteByte (&sv.reliable_datagram, svc_stufftext);
			MSG_WriteString (&sv.reliable_datagram, "//cutscene\n"); // ZQ extension
			NQP_Skip (p - nqp_buf_data + 1);
		}
		else if (nqp_buf_data[0] == svc_temp_entity) {
			if (nqp_buf.cursize < 2)
				break;

switch (nqp_buf_data[1]) {
  case TE_SPIKE:
  case TE_SUPERSPIKE:
  case TE_EXPLOSION:
  case TE_TAREXPLOSION:
  case TE_WIZSPIKE:
  case TE_KNIGHTSPIKE:
  case TE_LAVASPLASH:
  case TE_TELEPORT:
		nqp_expect = 8;
		break;
  case TE_GUNSHOT:
		if (nqp_buf.cursize < 8)
			goto waitformore;
		NQP_Flush (2);
		MSG_WriteByte (&sv.reliable_datagram, 1);
		NQP_Flush (6);
		break;

  case TE_LIGHTNING1:
  case TE_LIGHTNING2:
  case TE_LIGHTNING3:
		nqp_expect = 16;
	  break;
  case NQ_TE_BEAM:
		NQP_Skip (16);
		break;

  case NQ_TE_EXPLOSION2:
		nqp_expect = 10;
		break;
  default:
		Com_Printf ("WARNING: progs.dat sent an unsupported svc_temp_entity: %i\n", nqp_buf_data[1]);
	    goto ignore;
}

		}
		else {
			Com_Printf ("WARNING: progs.dat sent an unsupported svc: %i\n", cmd);
ignore:
			nqp_ignore_this_frame = true;
			break;
		}
	}
waitformore:;
}

#else // !WITH_NQPROGS
#define NQP_Process()
#endif

/*
=================
PF_WriteByte

void WriteByte(float to, float f) = #52
=================
*/
static void PF_WriteByte (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteByte (&nqp_buf, G_FLOAT(OFS_PARM1));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_Byte (G_FLOAT(OFS_PARM1));
		ClientReliableWrite_End ();
	} else {
		if (G_FLOAT(OFS_PARM0) == MSG_ALL)
			CheckIntermission ();
		MSG_WriteByte (WriteDest(), G_FLOAT(OFS_PARM1));
	}
}


/*
=================
PF_WriteChar

void WriteChar(float to, float f) = #53
=================
*/
static void PF_WriteChar (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteByte (&nqp_buf, G_FLOAT(OFS_PARM1));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_Char (G_FLOAT(OFS_PARM1));
		ClientReliableWrite_End ();
	} else
		MSG_WriteChar (WriteDest(), G_FLOAT(OFS_PARM1));
}


/*
=================
PF_WriteShort

void WriteShort(float to, float f) = #54
=================
*/
static void PF_WriteShort (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteShort (&nqp_buf, G_FLOAT(OFS_PARM1));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_Short (G_FLOAT(OFS_PARM1));
		ClientReliableWrite_End ();
	} else
		MSG_WriteShort (WriteDest(), G_FLOAT(OFS_PARM1));
}


/*
=================
PF_WriteLong

void WriteLong(float to, float f) = #55
=================
*/
static void PF_WriteLong (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteLong (&nqp_buf, G_FLOAT(OFS_PARM1));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_Long (G_FLOAT(OFS_PARM1));
		ClientReliableWrite_End ();
	} else
		MSG_WriteLong (WriteDest(), G_FLOAT(OFS_PARM1));
}


/*
=================
PF_WriteAngle

void WriteAngle(float to, float f) = #57
=================
*/
static void PF_WriteAngle (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteAngle (&nqp_buf, G_FLOAT(OFS_PARM1));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_Angle (G_FLOAT(OFS_PARM1));
		ClientReliableWrite_End ();
	} else
		MSG_WriteAngle (WriteDest(), G_FLOAT(OFS_PARM1));
}


/*
=================
PF_WriteCoord

void WriteCoord(float to, float f) = #56
=================
*/
static void PF_WriteCoord (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteCoord (&nqp_buf, G_FLOAT(OFS_PARM1));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_Coord (G_FLOAT(OFS_PARM1));
		ClientReliableWrite_End ();
	}
	else
	{
		if (sv.intermission_hunt) {
			sv.intermission_origin[sv.intermission_hunt - 1] = G_FLOAT(OFS_PARM1);
			sv.intermission_hunt++;
			if (sv.intermission_hunt == 4) {
				sv.intermission_origin_valid = true;
				sv.intermission_hunt = 0;
			}
		}

		MSG_WriteCoord (WriteDest(), G_FLOAT(OFS_PARM1));
	}
}


/*
=================
PF_WriteString

void WriteString(float to, string s) = #58
=================
*/
static void PF_WriteString (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteString (&nqp_buf, G_STRING(OFS_PARM1));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_String (G_STRING(OFS_PARM1));
		ClientReliableWrite_End ();
	} else
		MSG_WriteString (WriteDest(), G_STRING(OFS_PARM1));
}


/*
=================
PF_WriteEntity

void WriteEntity(float to, entity e) = #59
=================
*/
static void PF_WriteEntity (void)
{
	if (pr_nqprogs) {
		if (G_FLOAT(OFS_PARM0) == MSG_ONE || G_FLOAT(OFS_PARM0) == MSG_INIT)
			return;	// we don't support this
		MSG_WriteShort (&nqp_buf, SV_TranslateEntnum(G_EDICTNUM(OFS_PARM1)));
		NQP_Process ();
		return;
	}

	if (G_FLOAT(OFS_PARM0) == MSG_ONE) {
		ClientReliableWrite_Begin0 (Write_GetClient());
		ClientReliableWrite_Short (SV_TranslateEntnum(G_EDICTNUM(OFS_PARM1)));
		ClientReliableWrite_End ();
	} else
		MSG_WriteShort (WriteDest(), SV_TranslateEntnum(G_EDICTNUM(OFS_PARM1)));
}

//=============================================================================

/*
=================
PF_sin

DP_QC_SINCOSSQRTPOW
float sin(float x) = #60
=================
*/
static void PF_sin (void)
{
	G_FLOAT(OFS_RETURN) = sin(G_FLOAT(OFS_PARM0));
}


/*
=================
PF_cos

DP_QC_SINCOSSQRTPOW
float cos(float x) = #61
=================
*/
static void PF_cos (void)
{
	G_FLOAT(OFS_RETURN) = cos(G_FLOAT(OFS_PARM0));
}


/*
=================
PF_sqrt

DP_QC_SINCOSSQRTPOW
float sqrt(float x) = #62
=================
*/
static void PF_sqrt (void)
{
	G_FLOAT(OFS_RETURN) = sqrt(G_FLOAT(OFS_PARM0));
}


/*
=================
PF_etos

DP_QC_ETOS
string etos(entity ent) = #65
=================
*/
static void PF_etos (void)
{
	snprintf (pr_string_temp, sizeof(pr_string_temp), "entity %i", G_EDICTNUM(OFS_PARM0));

	G_INT(OFS_RETURN) = PR_SetString(pr_string_temp);
}

//=============================================================================

/*
=================
PF_makestatic

void makestatic(entity e) = #69
=================
*/
static void PF_makestatic (void)
{
	edict_t	*ent;
	int		i;
	
	ent = G_EDICT(OFS_PARM0);

	MSG_WriteByte (&sv.signon,svc_spawnstatic);

	MSG_WriteByte (&sv.signon, SV_ModelIndex(PR_GetString(ent->v.model)));

	MSG_WriteByte (&sv.signon, ent->v.frame);
	MSG_WriteByte (&sv.signon, ent->v.colormap);
	MSG_WriteByte (&sv.signon, ent->v.skin);
	for (i=0 ; i<3 ; i++)
	{
		MSG_WriteCoord(&sv.signon, ent->v.origin[i]);
		MSG_WriteAngle(&sv.signon, ent->v.angles[i]);
	}

// throw the entity away now
	ED_Free (ent);
}

//=============================================================================

/*
==============
PF_setspawnparms

void setspawnparms(entity e) = #78
==============
*/
static void PF_setspawnparms (void)
{
	edict_t	*ent;
	int		i;
	client_t	*client;

	ent = G_EDICT(OFS_PARM0);
	i = NUM_FOR_EDICT(ent);
	if (i < 1 || i > MAX_CLIENTS)
		PR_RunError ("Entity is not a client");

	// copy spawn parms out of the client_t
	client = svs.clients + (i-1);

	for (i=0 ; i< NUM_SPAWN_PARMS ; i++)
		(&PR_GLOBAL(parm1))[i] = client->spawn_parms[i];
}


/*
==============
PF_changelevel

void changelevel(string s) = #70
==============
*/
static void PF_changelevel (void)
{
	char	*s;
	static	int	last_spawncount;

// make sure we don't issue two changelevels
	if (svs.spawncount == last_spawncount)
		return;
	last_spawncount = svs.spawncount;
	
	s = G_STRING(OFS_PARM0);
	Cbuf_AddText (va("map %s\n",s));
}


/*
==============
PF_logfrag

void logfrag(entity killer, entity killee) = #79
==============
*/
static void PF_logfrag (void)
{
	edict_t	*ent1, *ent2;
	int		e1, e2;
	char	*s;

	ent1 = G_EDICT(OFS_PARM0);
	ent2 = G_EDICT(OFS_PARM1);

	e1 = NUM_FOR_EDICT(ent1);
	e2 = NUM_FOR_EDICT(ent2);
	
	if (e1 < 1 || e1 > MAX_CLIENTS
	|| e2 < 1 || e2 > MAX_CLIENTS)
		return;

#ifdef AGRIP
	// If bots are involved, DON'T LOG the frag
	// (it pollutes the stats system).
	// Put this in braces to avoid the obnoxious VC
	// error ``missing ; before type''...
	{
		client_t *cl1, *cl2;
		// Don't log frags where bots kill players
		// OR when players kill bots...
		cl1 = &svs.clients[e1-1];
		cl2 = &svs.clients[e2-1];
		if (cl1->bot || cl2->bot)
			return;
	}
#endif
	
	s = va("\\%s\\%s\\\n",svs.clients[e1-1].name, svs.clients[e2-1].name);

	SZ_Print (&svs.log[svs.logsequence&1], s);
	if (sv_fraglogfile) {
		fprintf (sv_fraglogfile, s);
		fflush (sv_fraglogfile);
	}
}


/*
==============
PF_infokey

string infokey(entity e, string key) = #80
==============
*/
static void PF_infokey (void)
{
	edict_t	*e;
	int		e1;
	char	*value;
	char	*key;
	static	char ov[256];

	e = G_EDICT(OFS_PARM0);
	e1 = NUM_FOR_EDICT(e);
	key = G_STRING(OFS_PARM1);

	if (e1 == 0) {
		if ((value = Info_ValueForKey (svs.info, key)) == NULL || !*value)
			value = Info_ValueForKey(localinfo, key);
	} else if (e1 <= MAX_CLIENTS) {
		if (!strcmp(key, "ip"))
			value = strcpy(ov, NET_BaseAdrToString (svs.clients[e1-1].netchan.remote_address));
		else if (!strcmp(key, "*z_ext")) {
			sprintf(ov, "%d", svs.clients[e1-1].extensions);
			value = ov;
		} else if (!strcmp(key, "ping")) {
			int ping = SV_CalcPing (&svs.clients[e1-1]);
			sprintf(ov, "%d", ping);
			value = ov;
		} else
			value = Info_ValueForKey (svs.clients[e1-1].userinfo, key);
	} else
		value = "";

	RETURN_STRING(value);
}


/*
==============
PF_stof

float stof(string s) = #81
==============
*/
static void PF_stof (void)
{
	char	*s;

	s = G_STRING(OFS_PARM0);

	G_FLOAT(OFS_RETURN) = atof(s);
}


/*
==============
PF_multicast

void multicast(vector where, float set) = #82
==============
*/
static void PF_multicast (void)
{
	float	*o;
	int		to;

	o = G_VECTOR(OFS_PARM0);
	to = G_FLOAT(OFS_PARM1);

	SV_Multicast (o, to);
}


/*
=================
PF_tracebox

Like traceline but traces a box of the size specified
(NOTE: currently the hull size can only be one of the sizes used in the map
for bmodel collisions, entity collisions will pay attention to the exact size
specified however, this is a collision code limitation in quake itself,
and will be fixed eventually).

DP_QC_TRACEBOX

void(vector v1, vector mins, vector maxs, vector v2, float nomonsters, entity ignore) tracebox = #90;
=================
*/
static void PF_tracebox (void)
{
        float       *v1, *v2, *mins, *maxs;
        edict_t     *ent;
        int          nomonsters;
        trace_t      trace;

        v1 = G_VECTOR(OFS_PARM0);
        mins = G_VECTOR(OFS_PARM1);
        maxs = G_VECTOR(OFS_PARM2);
        v2 = G_VECTOR(OFS_PARM3);
        nomonsters = G_FLOAT(OFS_PARM4);
        ent = G_EDICT(OFS_PARM5);

        trace = SV_Trace (v1, mins, maxs, v2, nomonsters, ent);

        PR_GLOBAL(trace_allsolid) = trace.allsolid;
        PR_GLOBAL(trace_startsolid) = trace.startsolid;
        PR_GLOBAL(trace_fraction) = trace.fraction;
        PR_GLOBAL(trace_inwater) = trace.inwater;
        PR_GLOBAL(trace_inopen) = trace.inopen;
        VectorCopy (trace.endpos, PR_GLOBAL(trace_endpos));
        VectorCopy (trace.plane.normal, PR_GLOBAL(trace_plane_normal));
        PR_GLOBAL(trace_plane_dist) =  trace.plane.dist;
        if (trace.e.ent)
                PR_GLOBAL(trace_ent) = EDICT_TO_PROG(trace.e.ent);
        else
                PR_GLOBAL(trace_ent) = EDICT_TO_PROG(sv.edicts);
}


/*
=================
PF_randomvec

DP_QC_RANDOMVEC
vector randomvec() = #91
=================
*/
static void PF_randomvec (void)
{
	vec3_t temp;

	do
	{
		temp[0] = (rand() & 0x7fff) * (2.0 / 0x7fff) - 1.0;
		temp[1] = (rand() & 0x7fff) * (2.0 / 0x7fff) - 1.0;
		temp[2] = (rand() & 0x7fff) * (2.0 / 0x7fff) - 1.0;
	} while (DotProduct(temp, temp) >= 1);

	VectorCopy (temp, G_VECTOR(OFS_RETURN));
}


/*
=================
PF_min

Returns the minimum of two or more floats

DP_QC_MINMAXBOUND
float min(float a, float b, ...) = #94
=================
*/
static void PF_min (void)
{
	int i;
	float min, *f;
	
	min = G_FLOAT(OFS_PARM0);
	for (i = 1, f = &G_FLOAT(OFS_PARM1); i < pr_argc; i++, f += 3) {
		if (*f < min)
			min = *f;
	}

	G_FLOAT(OFS_RETURN) = min;
}


/*
=================
PF_max

Returns the maximum of two or more floats

DP_QC_MINMAXBOUND
float max(float a, float b, ...) = #95
=================
*/
void PF_max (void)
{
	int i;
	float max, *f;
	
	max = G_FLOAT(OFS_PARM0);
	for (i = 1, f = &G_FLOAT(OFS_PARM1); i < pr_argc; i++, f += 3) {
		if (*f > max)
			max = *f;
	}

	G_FLOAT(OFS_RETURN) = max;
}


/*
=================
PF_bound

Clamp value to supplied range

DP_QC_MINMAXBOUND
float bound(float min, float value, float max) = #96
=================
*/
void PF_bound (void)
{
	G_FLOAT(OFS_RETURN) = bound(G_FLOAT(OFS_PARM0), G_FLOAT(OFS_PARM1), G_FLOAT(OFS_PARM2));
}


/*
=================
PF_pow

DP_QC_SINCOSSQRTPOW
float pow(float x, float y) = #97;
=================
*/
static void PF_pow (void)
{
	G_FLOAT(OFS_RETURN) = pow(G_FLOAT(OFS_PARM0), G_FLOAT(OFS_PARM1));
}


/*
=================
PF_cvar_string

QSG_CVARSTRING DP_QC_CVAR_STRING
string cvar_string(string varname) = #103;
=================
*/
static void PF_cvar_string (void)
{
	char	*str;
	cvar_t	*var;

	str = G_STRING(OFS_PARM0);

	var = Cvar_Find(str);
	if (!var) {
		// TODO: Cmd_LegacyCommandValue?
		G_INT(OFS_RETURN) = 0;
		return;
	}

	strlcpy (pr_string_temp, var->string, sizeof(pr_string_temp));
	RETURN_STRING(pr_string_temp);
}


/*
=================
PF_strlen

ZQ_QC_STRINGS
float strlen(string s) = #114;
=================
*/
static void PF_strlen (void)
{
	G_FLOAT(OFS_RETURN) = strlen(G_STRING(OFS_PARM0));
}


/*
=================
PF_strcat

ZQ_QC_STRINGS
string strcat(string s1, string s2, ...) = #115; 
=================
*/
static void PF_strcat (void)
{
	int i;

	pr_string_temp[0] = '\0';
	for (i = 0; i < pr_argc; i++)
		strlcat (pr_string_temp, G_STRING(OFS_PARM0 + i * 3), sizeof(pr_string_temp));

	RETURN_STRING(pr_string_temp);
}


/*
=================
PF_substr

ZQ_QC_STRINGS
string substr(string s, float start, float count) = #116;
=================
*/
static void PF_substr (void)
{
	int		start, count;
	char	*s;

	s = G_STRING(OFS_PARM0);
	start = (int)G_FLOAT(OFS_PARM1);
	count = (int)G_FLOAT(OFS_PARM2);

	if (start < 0)
		Host_Error ("PF_substr: start < 0");

	if (count <= 0 || strlen(s) <= start) {
		G_INT(OFS_RETURN) = 0;
		return;
	}

	// up to count characters, or until buffer size is exceeded
	strlcpy (pr_string_temp, s + start, min(count + 1, sizeof(pr_string_temp)));

	RETURN_STRING(pr_string_temp);
}


/*
=================
PF_substr

returns vector value from a string

vector stov(string s) = #117
=================
*/
void PF_stov(void)
{
	int		 i;
	char	*s		= NULL;
	float	*out	= NULL;

	s = PF_VarString(0);
	out = G_VECTOR(OFS_RETURN);
	VectorClear(out);

	if (*s == '\'')
		s++;

	for (i = 0; i < 3; i++)
	{
		// ignore whitespaces:
		while (*s == ' ' || *s == '\t')
			s++;
		out[i] = atof (s);
		if (!out[i] && *s != '-' && *s != '+' && (*s < '0' || *s > '9'))
			break; // not a number
		while (*s && *s != ' ' && *s !='\t' && *s != '\'')
			s++;
		if (*s == '\'')
			break;
	}
}


/*
=================
PF_strzone


ZQ_QC_STRINGS
string strzone(string s) = #118
=================
*/
static void PF_strzone (void)
{
	int i;
	char *s;

	if (pr_argc >= 1)
		s = G_STRING(OFS_PARM0);
	else
		s = "";

	for (i = MAX_PRSTR; i < MAX_PRSTR + MAX_DYN_PRSTR; i++) {
		if (pr_strtbl[i] != pr_strings)
			continue;
		// found an empty slot
		pr_strtbl[i] = Q_strdup(s);
		G_INT(OFS_RETURN) = -i;
		return;
	}

	Host_Error ("PF_strzone: no free strings");
}


/*
=================
PF_strunzone

ZQ_QC_STRINGS
void strunzone(string s) = #119
=================
*/
static void PF_strunzone (void)
{
	int num;

	num = G_INT(OFS_PARM0);
	if (num > -MAX_PRSTR)
		Host_Error ("PF_strunzone: not a dynamic string");

	if (num <= -(MAX_PRSTR + MAX_DYN_PRSTR))
		Host_Error ("PF_strunzone: bad string");

	if (pr_strtbl[-num] == pr_strings)
		return;	// allow multiple strunzone on the same string (like free in C)

	Q_free (pr_strtbl[-num]);
	pr_strtbl[-num] = pr_strings;
}


/*
==============
PF_checkextension

float checkextension(string extension) = #99;
==============
*/
static void PF_checkextension (void)
{
	static char *supported_extensions[] = {
		"DP_CON_SET",
		"DP_HALFLIFE_MAP_CVAR",
		"DP_QC_CVAR_STRING",
		"DP_QC_ETOS",
		"DP_QC_MINMAXBOUND",
		"DP_QC_RANDOMVEC",
		"DP_QC_SINCOSSQRTPOW",
		"DP_QC_TRACEBOX",
		"QSG_CVARSTRING",
		"ZQ_CLIENTCOMMAND",
		"ZQ_INPUTBUTTONS",
		"ZQ_ITEMS2",
		"ZQ_MOVETYPE_NOCLIP",
		"ZQ_MOVETYPE_FLY",
		"ZQ_MOVETYPE_NONE",
		"ZQ_PAUSE",
		"ZQ_QC_PARTICLE",
		"ZQ_QC_STRINGS",
		"ZQ_QC_TOKENIZE",
		"ZQ_SOUNDTOCLIENT",
		"ZQ_TESTBOT",
#ifdef VWEP_TEST
		"ZQ_VWEP_TEST",
#endif
		NULL
	};
	char **pstr, *extension;
	extension = G_STRING(OFS_PARM0);

	for (pstr = supported_extensions; *pstr; pstr++) {
		if (!Q_stricmp(*pstr, extension)) {
			G_FLOAT(OFS_RETURN) = 1.0;	// supported

			if (!strcmp(extension, "ZQ_CLIENTCOMMAND"))
				pr_ext_enabled.zq_clientcommand = true;
			else if (!strcmp(extension, "ZQ_CONSOLECOMMAND"))
				pr_ext_enabled.zq_consolecommand = true;
			else if (!strcmp(extension, "ZQ_PAUSE"))
				pr_ext_enabled.zq_pause = true;

			return;
		}
	}

	G_FLOAT(OFS_RETURN) = 0.0;	// not supported
}


// Tonik's experiments -->
static void PF_testbot (void)
{
	edict_t	*ed;
	ed = SV_CreateBot (G_STRING(OFS_PARM0));
	RETURN_EDICT(ed);
}


static void PF_setinfo (void)
{
	int entnum;
	char *key, *value;

	entnum = G_EDICTNUM(OFS_PARM0);

	if (entnum < 1 || entnum > MAX_CLIENTS)
		PR_RunError ("Entity is not a client");

	key = G_STRING(OFS_PARM1);
	value = G_STRING(OFS_PARM2);

	Info_SetValueForStarKey (svs.clients[entnum-1].userinfo, key, value, MAX_INFO_STRING);
	svs.clients[entnum-1].spectator = value[0] ? true : false;

	// FIXME?
	SV_ExtractFromUserinfo (&svs.clients[entnum-1]);

	// FIXME
	MSG_WriteByte (&sv.reliable_datagram, svc_setinfo);
	MSG_WriteByte (&sv.reliable_datagram, entnum - 1);
	MSG_WriteString (&sv.reliable_datagram, key);
	MSG_WriteString (&sv.reliable_datagram, value);
}


#ifdef VWEP_TEST
static void PF_precache_vwep_model (void)
{
	char	*s;
	int		i;
	
	if (sv.state != ss_loading)
		PR_RunError ("PF_Precache_*: Precache can only be done in spawn functions");
		
	i = G_FLOAT(OFS_PARM0);
	s = G_STRING(OFS_PARM1);
	G_INT(OFS_RETURN) = G_INT(OFS_PARM1);	// FIXME, remove?
	PR_CheckEmptyString (s);

	if (i < 0 || i >= MAX_VWEP_MODELS)
		PR_RunError ("PF_precache_vwep_model: bad index %i", i);

	sv.vw_model_name[i] = s;
}
#endif
// <-- Tonik's experiments


/*
==============
PF_soundtoclient

ZQ_SOUNDTOCLIENT
For the AGRIP project
Same as PF_sound, but sends the sound to one client only

void soundtoclient(entity client, entity e, float chan, string samp, float vol, float atten) = #530
==============
*/
static void PF_soundtoclient (void)
{
	char		*sample;
	int			channel, clientnum;
	edict_t		*entity;
	int 		volume;
	float		attenuation;

    clientnum = G_EDICTNUM(OFS_PARM0);
	entity = G_EDICT(OFS_PARM1);
	channel = G_FLOAT(OFS_PARM2);
	sample = G_STRING(OFS_PARM3);
	volume = G_FLOAT(OFS_PARM4) * 255;
	attenuation = G_FLOAT(OFS_PARM5);

	if (clientnum < 1 || clientnum > MAX_CLIENTS) {
		Com_Printf ("tried to send a sound to a non-client\n");
		return;
	}

	SV_StartSound (entity, channel, sample, volume, attenuation,
											&svs.clients[clientnum-1]);
}


/*
** ZQ_QC_TOKENIZE
** float(string s) tokenize = #84;
*/
// FIXME, make independent of Cmd_TokenizeString?
void PF_tokenize (void)
{
	char *str;

	str = G_STRING(OFS_PARM0);
	Cmd_TokenizeString (str);
	G_FLOAT(OFS_RETURN) = Cmd_Argc();
}

/*
** ZQ_QC_TOKENIZE
** float() argc = #85;
*/
void PF_argc (void)
{
	G_FLOAT(OFS_RETURN) = Cmd_Argc();
}

/*
** ZQ_QC_TOKENIZE
** string(float n) argv = #86;
*/
void PF_argv (void)
{
	int num;

	num = G_FLOAT(OFS_PARM0);
	if (num < 0 || num >= Cmd_Argc())
		RETURN_STRING("");
	RETURN_STRING(Cmd_Argv(num));
}

/*
** ZQ_PAUSE
** void(float pause) setpause = #531;
*/
void PF_setpause (void)
{
	qbool pause;

	pause = G_FLOAT(OFS_PARM0) ? true : false;
	if (pause != (((int)sv_paused.value & 1) ? true : false))
		SV_TogglePause (false, NULL);
}

//=============================================================================

static builtin_t std_builtins[] =
{
PF_Fixme,
PF_makevectors,		// void(entity e) makevectors 			= #1;
PF_setorigin,		// void(entity e, vector o) setorigin	= #2;
PF_setmodel,		// void(entity e, string m) setmodel	= #3;
PF_setsize,			// void(entity e, vector min, vector max) setsize = #4;
PF_Fixme,
PF_debugbreak,		// void() debugbreak					= #6;
PF_random,			// float() random						= #7;
PF_sound,			// void(entity e, float chan, string samp) sound = #8;
PF_normalize,		// vector(vector v) normalize			= #9;
PF_error,			// void(string s, ...) error			= #10;
PF_objerror,		// void(string s, ...) objerror			= #11;
PF_vlen,			// float(vector v) vlen					= #12;
PF_vectoyaw,		// float(vector v) vectoyaw				= #13;
PF_Spawn,			// entity() spawn						= #14;
PF_Remove,			// void(entity e) remove				= #15;
PF_traceline,		// float(vector v1, vector v2, float nomonsters, entity ignore) traceline = #16;
PF_checkclient,		// entity() checkclient					= #17;
PF_Find,			// entity(entity start, .string fld, string match) find = #18;
PF_precache_sound,	// void(string s) precache_sound		= #19;
PF_precache_model,	// void(string s) precache_model		= #20;
PF_stuffcmd,		// void(entity client, string s) stuffcmd = #21;
PF_findradius,		// entity(vector org, float rad) findradius = #22;
PF_bprint,			// void(string s, ...) bprint			= #23;
PF_sprint,			// void(entity client, float level, string s, ...) sprint = #24;
PF_dprint,			// void(string s, ...) dprint			= #25;
PF_ftos,			// void(string s) ftos					= #26;
PF_vtos,			// void(string s) vtos					= #27;
PF_coredump,		// void() coredump						= #28;
PF_traceon,			// void() traceon						= #29;
PF_traceoff,		// void() traceoff						= #30;
PF_eprint,			// void(entity e)						= #31;
PF_walkmove,		// float(float yaw, float dist) walkmove = #32;
PF_Fixme,
PF_droptofloor,		// float() droptofloor					= #34
PF_lightstyle,		// void(float style, string value) lightstyle = #35
PF_rint,			// float(float f) rint					= #36
PF_floor,			// float(float f) floor					= #37
PF_ceil,			// float(float f) ceil					= #38
PF_Fixme,
PF_checkbottom,		// float(entity e) checkbottom			= #40
PF_pointcontents,	// float(vector v) pointcontents		= #41
PF_Fixme,
PF_fabs,			// float(float f) fabs					= #43
PF_aim,				// vector(entity e, float speed) aim	= #44
PF_cvar,			// float(string s) cvar					= #45
PF_localcmd,		// void(string cmd) localcmd			= #46
PF_nextent,			// entity(entity e) nextent				= #47
PF_particle,
PF_changeyaw,		// void() changeyaw						= #49
PF_Fixme,
PF_vectoangles,		// vector(vector v) vectoangles			= #51

PF_WriteByte,		// void(float to, float f) WriteByte	= #52
PF_WriteChar,		// void(float to, float f) WriteChar	= #53
PF_WriteShort,		// void(float to, float f) WriteShort	= #54
PF_WriteLong,		// void(float to, float f) WriteLong	= #55
PF_WriteCoord,		// void(float to, float f) WriteCoord	= #56
PF_WriteAngle,		// void(float to, float f) WriteAngle	= #57
PF_WriteString,		// void(float to, string s) WriteString	= #58
PF_WriteEntity,		// void(float to, entity e) WriteEntity	= #59

PF_sin,				// float(float x) sin					= #60
PF_cos,				// float(float x) cos					= #61
PF_sqrt,			// float(float x) sqrt					= #62

PF_Fixme,
PF_Fixme,
PF_etos,			// string(entity ent) etos				= #65
PF_Fixme,

SV_MoveToGoal,		// void(float step) movetogoal			= #67
PF_precache_file,	// string(string s) precache_file		= #68
PF_makestatic,		// void(entity e) makestatic			= #69

PF_changelevel,		// void(string s) changelevel			= #70
PF_Fixme,

PF_cvar_set,		// void(string var, string val) cvar_set = #72
PF_centerprint,		// void(entity client, string s, ...) centerprint = #73;

PF_ambientsound,	// void(vector vpos, string samp, float vol, float atten) ambientsound = #74

PF_precache_model,	// string(string s) precache_model2		= #75 (only for qcc)
PF_precache_sound,	// string(string s) precache_sound2		= #76 (only for qcc)
PF_precache_file,	// string(string s) precache_file2		= #77 (only for qcc)

PF_setspawnparms,	// void(entity e) setspawnparms			= #78

PF_logfrag,			// void(entity killer, entity killee) logfrag = #79

PF_infokey,			// string(entity e, string key) infokey	= #80
PF_stof,			// float(string s) stof					= #81
PF_multicast,		// void(vector where, float set) multicast = #82
};

#define num_std_builtins (sizeof(std_builtins)/sizeof(std_builtins[0]))

static struct { int num; builtin_t func; } ext_builtins[] =
{
{84, PF_tokenize},		// float(string s) tokenize							= #84;
{85, PF_argc},			// float() argc										= #85;
{86, PF_argv},			// string(float n) argv								= #86;

{90, PF_tracebox},		// void (vector v1, vector mins, vector maxs, vector v2, float nomonsters, entity ignore) tracebox = #90;
{91, PF_randomvec},		// vector() randomvec								= #91;
////
{94, PF_min},			// float(float a, float b, ...) min					= #94;
{95, PF_max},			// float(float a, float b, ...) max					= #95;
{96, PF_bound},			// float(float min, float value, float max) bound	= #96;
{97, PF_pow},			// float(float x, float y) pow						= #97;
////
{99, PF_checkextension},// float(string name) checkextension				= #99;
////
{103, PF_cvar_string},	// string(string varname) cvar_string				= #103;
////
{114, PF_strlen},		// float(string s) strlen							= #114;
{115, PF_strcat},		// string(string s1, string s2, ...) strcat			= #115;
{116, PF_substr},		// string(string s, float start, float count) substr = #116;
{117, PF_stov},			// vector(string s) stov							= #117;
{118, PF_strzone},		// string(string s) strzone							= #118;
{119, PF_strunzone},	// void(string s) strunzone							= #119;
{448, PF_cvar_string},	// string(string varname) cvar_string				= #448;
{530, PF_soundtoclient},	// void(entity client, entity e, float chan, string samp, float vol, float atten) soundtoclient = #530;
{531, PF_setpause},		// void(float pause) setpause						= #531;

// Experimental and/or deprecated:
{0x5a08, PF_soundtoclient},
#ifdef VWEP_TEST
{0x5a09, PF_precache_vwep_model},
#endif
{0x5a0A, PF_testbot},
{0x5a0B, PF_setinfo},
};

#define num_ext_builtins (sizeof(ext_builtins)/sizeof(ext_builtins[0]))

builtin_t *pr_builtins;
int pr_numbuiltins;

void PR_InitBuiltins (void)
{
	int i;

	// find highest builtin number to see how much space we need
	pr_numbuiltins = num_std_builtins;
	for (i = 0; i < num_ext_builtins; i++)
		if (ext_builtins[i].num + 1 > pr_numbuiltins)
			pr_numbuiltins = ext_builtins[i].num + 1;

	pr_builtins = Q_malloc(pr_numbuiltins * sizeof(builtin_t));
	memcpy (pr_builtins, std_builtins, sizeof(std_builtins));
	for (i = num_std_builtins; i < pr_numbuiltins; i++)
		pr_builtins[i] = PF_Fixme;
	for (i = 0; i < num_ext_builtins; i++) {
		assert (ext_builtins[i].num >= 0);
		pr_builtins[ext_builtins[i].num] = ext_builtins[i].func;
	}
}

/* vi: set noet ts=4 sts=4 ai sw=4: */
