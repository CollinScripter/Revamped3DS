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
// rc_wad.c - .wad file loading

#include "quakedef.h"
#ifdef HALFLIFEBSP
#include "gl_local.h"
#endif
#include "rc_wad.h"
#include "crc.h"

#define	HARDCODED_OCRANA_LEDS

typedef struct
{
	char		identification[4];		// should be WAD2 or 2DAW
	int			numlumps;
	int			infotableofs;
} wadinfo_t;

static int			wad_numlumps;
static lumpinfo_t	*wad_lumps;
static byte			*wad_base = NULL;
static int			wad_filesize;

void SwapPic (qpic_t *pic);

/*
==================
W_CleanupName

Lowercases name and pads with spaces and a terminating 0 to the length of
lumpinfo_t->name.
Used so lumpname lookups can proceed rapidly by comparing 4 chars at a time
Space padding is so names can be printed nicely in tables.
Can safely be performed in place.
==================
*/
static void W_CleanupName (char *in, char *out)
{
	int		i;
	int		c;
	
	for (i=0 ; i<16 ; i++ )
	{
		c = (int)(unsigned char)in[i];
		if (!c)
			break;
			
		if ( isupper(c) )
			c += ('a' - 'A');
		out[i] = c;
	}
	
	for ( ; i< 16 ; i++ )
		out[i] = 0;
}



/*
====================
W_LoadWadFile
====================
*/
void W_FreeWadFile (void)
{
	Q_free (wad_base);
	wad_base = NULL;
	wad_lumps = NULL;
	wad_numlumps = 0;
	wad_filesize = 0;
}


/*
====================
W_LoadWadFile
====================
*/
void W_LoadWadFile (char *filename)
{
	lumpinfo_t		*lump_p;
	wadinfo_t		*header;
	unsigned		i;
	int				infotableofs;

	// only one .wad can be loaded at a time
	W_FreeWadFile ();

	wad_base = FS_LoadHeapFile (filename);
	if (!wad_base)
		Sys_Error ("W_LoadWadFile: couldn't load %s", filename);

	wad_filesize = fs_filesize;

	header = (wadinfo_t *)wad_base;
	
	if (header->identification[0] != 'W'
	|| header->identification[1] != 'A'
	|| header->identification[2] != 'D'
	|| header->identification[3] != '2')
		Sys_Error ("Wad file %s doesn't have WAD2 id",filename);
		
	wad_numlumps = LittleLong(header->numlumps);
	infotableofs = LittleLong(header->infotableofs);
	wad_lumps = (lumpinfo_t *)(wad_base + infotableofs);

	if (infotableofs + wad_numlumps * sizeof(lump_t) > wad_filesize)
		Sys_Error ("Wad lump table exceeds file size");
	
	for (i=0, lump_p = wad_lumps ; i<wad_numlumps ; i++,lump_p++)
	{
		lump_p->filepos = LittleLong(lump_p->filepos);
		lump_p->size = LittleLong(lump_p->size);
		lump_p->disksize = LittleLong(lump_p->disksize);
		W_CleanupName (lump_p->name, lump_p->name);

		if (lump_p->filepos < sizeof(wadinfo_t) ||
				lump_p->filepos + lump_p->disksize > wad_filesize)
			Sys_Error ("Wad lump %s exceeds file size", lump_p->name);

		if (lump_p->type == TYP_QPIC)
			SwapPic ( (qpic_t *)(wad_base + lump_p->filepos));
	}
}


/*
=============
W_GetLumpinfo
=============
*/
lumpinfo_t *W_GetLumpinfo (char *name, qbool crash)
{
	int		i;
	lumpinfo_t	*lump_p;
	char	clean[16];
	
	W_CleanupName (name, clean);
	
	for (lump_p=wad_lumps, i=0 ; i<wad_numlumps ; i++,lump_p++)
	{
		if (!strcmp(clean, lump_p->name))
			return lump_p;
	}
	
	if (crash)
		Sys_Error ("W_GetLumpinfo: %s not found", name);
	return NULL;
}


static void W_HackOcranaLedsIntoConchars (byte *data);

int wad_lump_disksize;

void *W_GetLumpName (char *name, qbool crash)
{
	lumpinfo_t	*lump;
	
	lump = W_GetLumpinfo (name, crash);
	if (!lump)
		return NULL;

	if ( lump->type == TYP_QPIC &&
			((qpic_t *)(wad_base + lump->filepos))->width *
			((qpic_t *)(wad_base + lump->filepos))->height > lump->disksize )
		Sys_Error ("Wad lump %s has incorrect size", lump->name);

	if (!strcmp(name, "conchars")) {
		if (lump->disksize < 16384)
			Sys_Error ("W_GetLumpName: conchars lump is < 16384 bytes");
#ifdef HARDCODED_OCRANA_LEDS
		if (798 == CRC_Block (wad_base + lump->filepos, lump->disksize))
			W_HackOcranaLedsIntoConchars (wad_base + lump->filepos);
#endif
	}

	wad_lump_disksize = lump->disksize;

	return (void *)(wad_base + lump->filepos);
}


/*
=============================================================================

automatic byte swapping

=============================================================================
*/

void SwapPic (qpic_t *pic)
{
	pic->width = LittleLong(pic->width);
	pic->height = LittleLong(pic->height);	
}


/*
=============================================================================

hardcoded Ocrana LEDs

=============================================================================
*/

#ifdef HARDCODED_OCRANA_LEDS

static byte ocrana_leds[4][8][8] =
{
	{
		// green
		{ 0x00,0x38,0x3b,0x3b,0x3b,0x3b,0x35,0x00 },
		{ 0x38,0x3b,0x3d,0x3f,0x3f,0x3d,0x38,0x35 },
		{ 0x3b,0x3d,0xfe,0x3f,0x3f,0x3f,0x3b,0x35 },
		{ 0x3b,0x3f,0x3f,0x3f,0x3f,0x3f,0x3b,0x35 },
		{ 0x3b,0x3f,0x3f,0x3f,0x3f,0x3d,0x3b,0x35 },
		{ 0x3b,0x3d,0x3f,0x3f,0x3d,0x3b,0x38,0x35 },
		{ 0x35,0x38,0x3b,0x3b,0x3b,0x38,0x35,0x35 },
		{ 0x00,0x35,0x35,0x35,0x35,0x35,0x35,0x00 }
	},
	{
		// red
		{ 0x00,0xf8,0xf9,0xf9,0xf9,0xf9,0x4c,0x00 },
		{ 0xf8,0xf9,0xfa,0xfb,0xfb,0xfa,0xf8,0x4c },
		{ 0xf9,0xfa,0xfe,0xfb,0xfb,0xfb,0xf9,0x4c },
		{ 0xf9,0xfb,0xfb,0xfb,0xfb,0xfb,0xf9,0x4c },
		{ 0xf9,0xfb,0xfb,0xfb,0xfb,0xfa,0xf9,0x4c },
		{ 0xf9,0xfa,0xfb,0xfb,0xfa,0xf9,0xf8,0x4c },
		{ 0x4c,0xf8,0xf9,0xf9,0xf9,0xf8,0x4c,0x4c },
		{ 0x00,0x4c,0x4c,0x4c,0x4c,0x4c,0x4c,0x00 }
	},
	{
		// yellow
		{ 0x00,0xc8,0xc5,0xc5,0xc5,0xc5,0xcb,0x00 },
		{ 0xc8,0xc5,0xc2,0x6f,0x6f,0xc2,0xc8,0xcb },
		{ 0xc5,0xc2,0xfe,0x6f,0x6f,0x6f,0xc5,0xcb },
		{ 0xc5,0x6f,0x6f,0x6f,0x6f,0x6f,0xc5,0xcb },
		{ 0xc5,0x6f,0x6f,0x6f,0x6f,0xc2,0xc5,0xcb },
		{ 0xc5,0xc2,0x6f,0x6f,0xc2,0xc5,0xc8,0xcb },
		{ 0xcb,0xc8,0xc5,0xc5,0xc5,0xc8,0xcb,0xcb },
		{ 0x00,0xcb,0xcb,0xcb,0xcb,0xcb,0xcb,0x00 }
	},
	{
		// blue
		{ 0x00,0xd8,0xd5,0xd5,0xd5,0xd5,0xdc,0x00 },
		{ 0xd8,0xd5,0xd2,0xd0,0xd0,0xd2,0xd8,0xdc },
		{ 0xd5,0xd2,0xfe,0xd0,0xd0,0xd0,0xd5,0xdc },
		{ 0xd5,0xd0,0xd0,0xd0,0xd0,0xd0,0xd5,0xdc },
		{ 0xd5,0xd0,0xd0,0xd0,0xd0,0xd2,0xd5,0xdc },
		{ 0xd5,0xd2,0xd0,0xd0,0xd2,0xd5,0xd8,0xdc },
		{ 0xdc,0xd8,0xd5,0xd5,0xd5,0xd8,0xdc,0xdc },
		{ 0x00,0xdc,0xdc,0xdc,0xdc,0xdc,0xdc,0x00 }
	}
};

static void W_HackOcranaLedsIntoConchars (byte *data)
{
	byte	*leddata;
	int		i, x, y;

	for (i = 0; i < 4; i++) {
		leddata = data + (0x80>>4<<10) + (0x06<<3) + (i << 3);

		for (y = 0; y < 8; y++) {
			for (x = 0; x < 8; x++)
				*leddata++ = ocrana_leds[i][y][x];
			leddata += 128 - 8;
		}
	}
}

#endif	// HARDCODED_OCRANA_LEDS


/*
=============================================================================

WAD3 Texture Loading

=============================================================================
*/

#ifdef HALFLIFEBSP

#define TEXWAD_MAXIMAGES 16384

typedef struct {
	char name[MAX_QPATH];
	FILE *file;
	int position;
	int size;
} texwadlump_t;

static texwadlump_t texwadlump[TEXWAD_MAXIMAGES];
static int wad3_numlumps = 0;

void WAD3_LoadWadFile (char *filename)
{
	lumpinfo_t *lumps, *lump_p;
	wadinfo_t header;
	int i, j, infotableofs, numlumps, lowmark;
	FILE *file;

	if (wad3_numlumps == TEXWAD_MAXIMAGES)
		return;

	if (FS_FOpenFile (va("textures/halflife/%s", filename), &file) != -1)
		goto loaded;
	if (FS_FOpenFile (va("textures/%s", filename), &file) != -1)
		goto loaded;
	if (FS_FOpenFile (filename, &file) != -1)
		goto loaded;

	Host_Error ("Couldn't load halflife wad \"%s\"", filename);

loaded:
	if (fread(&header, 1, sizeof(wadinfo_t), file) != sizeof(wadinfo_t)) {
		Com_Printf ("WAD3_LoadWadFile: unable to read wad header\n");
		return;
	}

	if (memcmp(header.identification, "WAD3", 4)) {
		Com_Printf ("WAD3_LoadWadFile: Wad file %s doesn't have WAD3 id\n",filename);
		return;
	}

	numlumps = LittleLong(header.numlumps);
	if (numlumps < 1 || numlumps > TEXWAD_MAXIMAGES) {
		Com_Printf ("WAD3_LoadWadFile: invalid number of lumps (%i)\n", numlumps);
		return;
	}

	infotableofs = LittleLong(header.infotableofs);
	if (fseek(file, infotableofs, SEEK_SET)) {
		Com_Printf ("WAD3_LoadWadFile: unable to seek to lump table\n");
		return;
	}

	lowmark = Hunk_LowMark();
	if (!(lumps = Hunk_Alloc(sizeof(lumpinfo_t) * numlumps))) {
		Com_Printf ("WAD3_LoadWadFile: unable to allocate temporary memory for lump table\n");
		return;
	}

	if (fread(lumps, 1, sizeof(lumpinfo_t) * numlumps, file) != sizeof(lumpinfo_t) * numlumps) {
		Com_Printf ("WAD3_LoadWadFile: unable to read lump table\n");
		Hunk_FreeToLowMark(lowmark);
		return;
	}

	for (i = 0, lump_p = lumps; i < numlumps; i++,lump_p++) {
		W_CleanupName (lump_p->name, lump_p->name);
		for (j = 0; j < wad3_numlumps; j++) {
			if (!strcmp(lump_p->name, texwadlump[j].name))
				goto skip_duplicate;
		}
		strlcpy (texwadlump[j].name, lump_p->name, sizeof(texwadlump[j].name));
		texwadlump[j].file = file;
		texwadlump[j].position = LittleLong(lump_p->filepos);
		texwadlump[j].size = LittleLong(lump_p->disksize);
		wad3_numlumps++;
		if (wad3_numlumps == TEXWAD_MAXIMAGES)
			break;
skip_duplicate:;
	}

	Hunk_FreeToLowMark(lowmark);
	//leaves the file open
}


//converts paletted to rgba
byte *ConvertWad3ToRGBA(int width, int height, byte *in, qbool alpha)
{
	byte *data, *pal;
	int i, p, image_size;

	image_size = width * height;
	data = Q_malloc (image_size * 4);

	pal = (byte *) in + ((image_size * 85) / 64) + 2;

	for (i = 0; i < image_size; i++) {
		p = *in++;
		if (p == 255 && alpha) {
			((int *) data)[i] = 0;
		} else {
			p *= 3;
			data[i * 4 + 0] = pal[p];
			data[i * 4 + 1] = pal[p + 1];
			data[i * 4 + 2] = pal[p + 2];
			data[i * 4 + 3] = 255;
		}
	}
	return data;
}

byte *WAD3_LoadTexture (texture_t *tx)
{
	int i, j = 0;
	miptex_t *mt;
	byte *data;
	FILE *file;

	if (tx->offsets[0])
		return ConvertWad3ToRGBA(tx->width, tx->height, (byte *)(tx + 1),
								(tx->name[0] == '{'));

	for (i = 0; i < wad3_numlumps; i++) {
		if (Q_stricmp(tx->name, texwadlump[i].name))
			continue;
		
		file = texwadlump[i].file;
		if (fseek(file, texwadlump[i].position, SEEK_SET)) {
			Com_Printf("WAD3_LoadTexture: corrupt WAD3 file\n");
			return NULL;
		}
		mt = Q_malloc(texwadlump[i].size);
		if (fread(mt, 1, texwadlump[i].size, file) < texwadlump[i].size) {
			Com_Printf("WAD3_LoadTexture: corrupt WAD3 file\n");
			Q_free (mt);
			return NULL;
		}
		mt->width = LittleLong(mt->width);
		mt->height = LittleLong(mt->height);
		if (mt->width != tx->width || mt->height != tx->height) {
			Q_free (mt);
			return NULL;
		}
		for (j = 0;j < MIPLEVELS;j++)
			mt->offsets[j] = LittleLong(mt->offsets[j]);
		data = ConvertWad3ToRGBA(mt->width, mt->height, (byte *)(mt + 1),
													(tx->name[0] == '{'));
		Q_free (mt);
		return data;
	}
	return NULL;
}

#endif
