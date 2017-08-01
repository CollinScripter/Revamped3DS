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

#include "quakedef.h"
#include "rc_image.h"
#include "teamplay.h"

#ifdef GLQUAKE
#include "gl_local.h"
#else
#include "r_local.h"
#endif


#define	MAX_CACHED_SKINS		128
static skin_t skins[MAX_CACHED_SKINS];
static int numskins;

/*
================
Skin_Find

================
*/
void Skin_Find (char *skinname, struct skin_s **sk)
{
	skin_t		*skin;
	int			i;
	char		name[MAX_OSPATH];

	strlcpy (name, skinname, sizeof(name));

	for (i=0 ; i<numskins ; i++)
	{
		if (!strcmp (name, skins[i].name))
		{
			*sk = &skins[i];
			Skin_Cache (*sk);
			return;
		}
	}

	if (numskins == MAX_CACHED_SKINS)
	{	// ran out of spots, so flush everything
		extern void R_FlushTranslations ();
//		Skin_Flush ();
		R_FlushTranslations ();
	}

	skin = &skins[numskins];
	*sk = skin;
	numskins++;

	memset (skin, 0, sizeof(*skin));
	strlcpy (skin->name, name, sizeof(skin->name));
}


/*
==========
Skin_Cache

Returns a pointer to the skin bitmap, or NULL to use the default
==========
*/
byte *Skin_Cache (skin_t *skin)
{
	int		y;
	byte	*pic, *out, *pix;
	int		width, height;
	char	name[MAX_OSPATH];

	if (skin->failedload)
		return NULL;

	out = Cache_Check (&skin->cache);
	if (out)
		return out;

//
// load the pic from disk
//
	snprintf (name, sizeof(name), "skins/%s.pcx", skin->name);
	LoadPCX (name, &pic, &width, &height);
	if (!pic || width > 320 || height > 200)
	{
		if (pic)
			Q_free (pic);	// Q_malloc'ed by LoadPCX
		Com_Printf ("Couldn't load skin %s\n", name);

		skin->failedload = true;
		return NULL;
	}

	out = pix = Cache_Alloc (&skin->cache, 320*200, skin->name);
	if (!out)
		Sys_Error ("Skin_Cache: couldn't allocate");

	memset (out, 0, 320*200);
	for (y=0 ; y<height ; y++, pix += 320)
		memcpy (pix, pic + y*width, width);

	Q_free (pic);	// Q_malloc'ed by LoadPCX

	skin->failedload = false;

	return out;
}


void Skin_Flush (void)
{
	int		i;

	for (i=0 ; i<numskins ; i++)
		if (skins[i].cache.data)
			Cache_Free (&skins[i].cache);

	numskins = 0;
}
