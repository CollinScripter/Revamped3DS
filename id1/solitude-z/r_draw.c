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

// r_draw.c

#include "quakedef.h"
#include "r_local.h"
#include "rc_wad.h"
#include "sound.h"
#include "version.h"

int			char_range[MAX_CHARSETS];	// 0x0400, etc; slot 0 is always 0x00
byte		*draw_chars[MAX_CHARSETS];				// 8*8 graphic characters
								// slot 0 is static, the rest are Q_malloc'd
mpic_t		*draw_disc;

//=============================================================================
/* Support Routines */

typedef struct cachepic_s
{
	mpic_t			pic;
	char			name[MAX_QPATH];
	// only one of the following two fields can be set
	byte			*data;		// raw data in a wad lump
	cache_user_t	cache;		// cached .lmp
} cachepic_t;

#define	MAX_CACHED_PICS		256
static cachepic_t	cachepics[MAX_CACHED_PICS];
static int			numcachepics;

mpic_t *R_CacheWadPic (char *name)
{
	int			i;
	cachepic_t	*cpic;
	qpic_t		*p;

	for (cpic = cachepics, i = 0; i < numcachepics; cpic++, i++)
		if (!strcmp (name, cpic->name))
			return &cpic->pic;

	p = W_GetLumpName (name, false);
	if (!p)
		return NULL;

	if (numcachepics == MAX_CACHED_PICS)
		Sys_Error ("numcachepics == MAX_CACHED_PICS");

	numcachepics++;
	strlcpy (cpic->name, name, sizeof(cpic->name));
	cpic->cache.data = NULL;

	cpic->pic.width = p->width;
	cpic->pic.height = p->height;
	cpic->data = p->data;
	cpic->pic.alpha = memchr (p->data, 255, p->width * p->height) != NULL;

	return &cpic->pic;
}

/*
================
R_CachePic
================
*/
mpic_t *R_CachePic (char *path)
{
	cachepic_t	*cpic;
	int			i;
	qpic_t		*dat;

	for (cpic = cachepics, i = 0; i < numcachepics; cpic++, i++)
		if (!strcmp (path, cpic->name))
			break;

	if (i == numcachepics)
	{
		if (numcachepics == MAX_CACHED_PICS)
			Sys_Error ("numcachepics == MAX_CACHED_PICS");
		numcachepics++;
		strlcpy (cpic->name, path, sizeof(cpic->name));
		cpic->cache.data = NULL;
	}
	else
	{
		dat = Cache_Check (&cpic->cache);

		if (dat) {
			cpic->data = dat->data;
			return &cpic->pic;
		}
	}

//
// load the pic from disk
//
	FS_LoadCacheFile (path, &cpic->cache);
	
	dat = (qpic_t *)(cpic->cache.data);
	if (!dat)
		Sys_Error ("R_CachePic: failed to load %s", path);

	SwapPic (dat);

	cpic->pic.width = dat->width;
	cpic->pic.height = dat->height;
	cpic->data = dat->data;
	cpic->pic.alpha = memchr (dat->data, 255,
					dat->width * dat->height) != NULL;

	return &cpic->pic;
}

// returns Q_malloc'd data, or NULL or error
static byte *LoadAlternateCharset (char *name)
{
	qpic_t *p;
	byte *data;
	
	p = (qpic_t *)FS_LoadTempFile (va("gfx/%s.lmp", name));
	// FIXME FIXME, why are we getting bogus fs_filesize values?
	//Com_Printf ("%i\n", fs_filesize);
	if (!p /* || fs_filesize != 128*128+8 */)
		return NULL;
	SwapPic (p);
	if (p->width != 128 || p->height != 128)
		return 0;
	data = Q_malloc (128*128);
	memcpy (data, p->data, 128*128);
	return data;
}

void R_Draw_Init ();

void R_FlushPics (void)
{
	int	i;
	cachepic_t	*cpic;

	for (cpic = cachepics, i = 0; i < numcachepics; cpic++, i++) {
		if (cpic->cache.data)
			Cache_Free (cpic->cache.data);

		// turn up any attempt to access an unregistered pic
		cpic->data = cpic->cache.data = NULL;
	}

	numcachepics = 0;

	draw_chars[0] = NULL;
	for (i = 1; i < MAX_CHARSETS; i++) {
		Q_free (draw_chars[i]);
		char_range[i] = 0;
	}
	draw_disc = NULL;

	R_Draw_Init ();
}


/*
===============
R_Draw_Init
===============
*/
void R_Draw_Init (void)
{
	W_LoadWadFile ("gfx.wad");

	draw_chars[0] = W_GetLumpName ("conchars", true);
	draw_chars[1] = LoadAlternateCharset ("conchars-cyr");
	if (draw_chars[1])
		char_range[1] = 0x0400;

	draw_disc = R_CacheWadPic ("disc");
}


qbool R_CharAvailable (wchar num)
{
	int i;

	if (num == (num & 0xff))
		return true;

	for (i = 1; i < MAX_CHARSETS; i++)
		if (char_range[i] == (num & 0xFF00))
			return true;

	return false;
}

/*
================
R_DrawChar

Draws one 8*8 graphics character with 0 being transparent.
It can be clipped to the top of the screen to allow the console to be
smoothly scrolled off.
================
*/
void R_DrawCharW (int x, int y, wchar num)
{
	byte			*dest;
	byte			*source;
	unsigned short	*pusdest;
	int				drawline;	
	int				row, col, slot;

	if (y <= -8)
		return;			// totally off screen

	if (y > (int)vid.height - 8 || x < 0 || x > vid.width - 8)
		return;

	slot = 0;
	if ((num & 0xFF00) != 0)
	{
		int i;
		for (i = 1; i < MAX_CHARSETS; i++)
			if (char_range[i] == (num & 0xFF00)) {
				slot = i;
				break;
			}
		if (i == MAX_CHARSETS)
			num = '?';
	}

	row = (num>>4)&15;
	col = num&15;
	source = draw_chars[slot] + (row<<10) + (col<<3);

	if (y < 0)
	{	// clipped
		drawline = 8 + y;
		source -= 128*y;
		y = 0;
	}
	else
		drawline = 8;


	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y*vid.rowbytes + x;
	
		while (drawline--)
		{
			if (source[0])
				dest[0] = source[0];
			if (source[1])
				dest[1] = source[1];
			if (source[2])
				dest[2] = source[2];
			if (source[3])
				dest[3] = source[3];
			if (source[4])
				dest[4] = source[4];
			if (source[5])
				dest[5] = source[5];
			if (source[6])
				dest[6] = source[6];
			if (source[7])
				dest[7] = source[7];
			source += 128;
			dest += vid.rowbytes;
		}
	}
	else
	{
	// FIXME: pre-expand to native format?
		pusdest = (unsigned short *)
				((byte *)vid.buffer + y*vid.rowbytes + (x<<1));

		while (drawline--)
		{
			if (source[0])
				pusdest[0] = d_8to16table[source[0]];
			if (source[1])
				pusdest[1] = d_8to16table[source[1]];
			if (source[2])
				pusdest[2] = d_8to16table[source[2]];
			if (source[3])
				pusdest[3] = d_8to16table[source[3]];
			if (source[4])
				pusdest[4] = d_8to16table[source[4]];
			if (source[5])
				pusdest[5] = d_8to16table[source[5]];
			if (source[6])
				pusdest[6] = d_8to16table[source[6]];
			if (source[7])
				pusdest[7] = d_8to16table[source[7]];

			source += 128;
			pusdest += (vid.rowbytes >> 1);
		}
	}
}
void R_DrawChar (int x, int y, int num)
{
	R_DrawCharW (x, y, char2wc(num));
}

void R_DrawString (int x, int y, const char *str)
{
	while (*str)
	{
		R_DrawChar (x, y, *str);
		str++;
		x += 8;
	}
}

void R_DrawStringW (int x, int y, const wchar *ws)
{
	while (*ws)
	{
		R_DrawCharW (x, y, *ws);
		ws++;
		x += 8;
	}
}

void R_DrawPixel (int x, int y, byte color)
{
	byte			*dest;
	unsigned short	*pusdest;

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y*vid.rowbytes + x;
		*dest = color;
	}
	else
	{
	// FIXME: pre-expand to native format?
		pusdest = (unsigned short *)
				((byte *)vid.buffer + y*vid.rowbytes + (x<<1));
		*pusdest = d_8to16table[color];
	}
}

void R_DrawCrosshair (int num, int crossx, int crossy)
{
	int	x, y;
	extern vrect_t		scr_vrect;	// FIXME
	extern cvar_t crosshaircolor;
	byte color;

	color = (int)crosshaircolor.value;

	x = scr_vrect.x + scr_vrect.width/2 + crossx; 
	y = scr_vrect.y + scr_vrect.height/2 + crossy;

	if (num == 2) {
		R_DrawPixel (x - 1, y, color);
		R_DrawPixel (x - 3, y, color);
		R_DrawPixel (x + 1, y, color);
		R_DrawPixel (x + 3, y, color);
		R_DrawPixel (x, y - 1, color);
		R_DrawPixel (x, y - 3, color);
		R_DrawPixel (x, y + 1, color);
		R_DrawPixel (x, y + 3, color);
	} else if (num == 3) {
		R_DrawPixel (x, y, color);
		R_DrawPixel (x - 1, y, color);
		R_DrawPixel (x + 1, y, color);
		R_DrawPixel (x, y - 1, color);
		R_DrawPixel (x, y + 1, color);
	} else if (num == 4) {
		R_DrawPixel (x, y, color);
	} else
		R_DrawChar (x - 4, y - 4, '+');
}


/*
================
R_DrawDebugChar

Draws a single character directly to the upper right corner of the screen.
This is for debugging lockups by drawing different chars in different parts
of the code.
================
*/
void R_DrawDebugChar (char num)
{
	byte			*dest;
	byte			*source;
	int				drawline;	
	int				row, col;

	if (!vid.direct)
		return;		// don't have direct FB access, so no debugchars...

	drawline = 8;

	row = num>>4;
	col = num&15;
	source = draw_chars[0] + (row<<10) + (col<<3);

	dest = vid.direct + 312;

	while (drawline--)
	{
		dest[0] = source[0];
		dest[1] = source[1];
		dest[2] = source[2];
		dest[3] = source[3];
		dest[4] = source[4];
		dest[5] = source[5];
		dest[6] = source[6];
		dest[7] = source[7];
		source += 128;
		dest += 320;
	}
}


static void R_DrawSolidPic (int x, int y, mpic_t *pic)
{
	byte			*dest, *source;
	unsigned short	*pusdest;
	int				v, u;

	source = ((cachepic_t *)pic)->data;

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y * vid.rowbytes + x;

		for (v=0 ; v<pic->height ; v++)
		{
			memcpy (dest, source, pic->width);
			dest += vid.rowbytes;
			source += pic->width;
		}
	}
	else
	{
	// FIXME: pretranslate at load time?
		pusdest = (unsigned short *)vid.buffer + y * (vid.rowbytes >> 1) + x;

		for (v=0 ; v<pic->height ; v++)
		{
			for (u=0 ; u<pic->width ; u++)
			{
				pusdest[u] = d_8to16table[source[u]];
			}

			pusdest += vid.rowbytes >> 1;
			source += pic->width;
		}
	}
}


static void R_DrawTransPic (int x, int y, mpic_t *pic)
{
	byte	*dest, *source, tbyte;
	unsigned short	*pusdest;
	int				v, u;

	source = ((cachepic_t *)pic)->data;

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y * vid.rowbytes + x;

		if (pic->width & 7)
		{	// general
			for (v=0 ; v<pic->height ; v++)
			{
				for (u=0 ; u<pic->width ; u++)
					if ( (tbyte=source[u]) != TRANSPARENT_COLOR)
						dest[u] = tbyte;
	
				dest += vid.rowbytes;
				source += pic->width;
			}
		}
		else
		{	// unwound
			for (v=0 ; v<pic->height ; v++)
			{
				for (u=0 ; u<pic->width ; u+=8)
				{
					if ( (tbyte=source[u]) != TRANSPARENT_COLOR)
						dest[u] = tbyte;
					if ( (tbyte=source[u+1]) != TRANSPARENT_COLOR)
						dest[u+1] = tbyte;
					if ( (tbyte=source[u+2]) != TRANSPARENT_COLOR)
						dest[u+2] = tbyte;
					if ( (tbyte=source[u+3]) != TRANSPARENT_COLOR)
						dest[u+3] = tbyte;
					if ( (tbyte=source[u+4]) != TRANSPARENT_COLOR)
						dest[u+4] = tbyte;
					if ( (tbyte=source[u+5]) != TRANSPARENT_COLOR)
						dest[u+5] = tbyte;
					if ( (tbyte=source[u+6]) != TRANSPARENT_COLOR)
						dest[u+6] = tbyte;
					if ( (tbyte=source[u+7]) != TRANSPARENT_COLOR)
						dest[u+7] = tbyte;
				}
				dest += vid.rowbytes;
				source += pic->width;
			}
		}
	}
	else
	{
	// FIXME: pretranslate at load time?
		pusdest = (unsigned short *)vid.buffer + y * (vid.rowbytes >> 1) + x;

		for (v=0 ; v<pic->height ; v++)
		{
			for (u=0 ; u<pic->width ; u++)
			{
				tbyte = source[u];

				if (tbyte != TRANSPARENT_COLOR)
				{
					pusdest[u] = d_8to16table[tbyte];
				}
			}

			pusdest += vid.rowbytes >> 1;
			source += pic->width;
		}
	}
}


void R_DrawPic (int x, int y, mpic_t *pic)
{
	if (!pic)
		return;

	if ((x < 0) || (x + pic->width > vid.width) ||
		(y < 0) || (y + pic->height > vid.height))
	{
		Sys_Error ("R_DrawPic: bad coordinates");
	}

	if (pic->alpha)
		R_DrawTransPic (x, y, pic);
	else
		R_DrawSolidPic (x, y, pic);
}


static void R_DrawTransSubPic (int x, int y, mpic_t *pic, int srcx, int srcy, int width, int height)
{
	byte	*dest, *source, tbyte;
	unsigned short	*pusdest;
	int				v, u;

	source = ((cachepic_t *)pic)->data + srcy * pic->width + srcx;

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y * vid.rowbytes + x;

		if (width & 7)
		{	// general
			for (v=0 ; v<height ; v++)
			{
				for (u=0 ; u<width ; u++)
					if ( (tbyte=source[u]) != TRANSPARENT_COLOR)
						dest[u] = tbyte;
	
				dest += vid.rowbytes;
				source += pic->width;
			}
		}
		else
		{	// unwound
			for (v=0 ; v<height ; v++)
			{
				for (u=0 ; u<width ; u+=8)
				{
					if ( (tbyte=source[u]) != TRANSPARENT_COLOR)
						dest[u] = tbyte;
					if ( (tbyte=source[u+1]) != TRANSPARENT_COLOR)
						dest[u+1] = tbyte;
					if ( (tbyte=source[u+2]) != TRANSPARENT_COLOR)
						dest[u+2] = tbyte;
					if ( (tbyte=source[u+3]) != TRANSPARENT_COLOR)
						dest[u+3] = tbyte;
					if ( (tbyte=source[u+4]) != TRANSPARENT_COLOR)
						dest[u+4] = tbyte;
					if ( (tbyte=source[u+5]) != TRANSPARENT_COLOR)
						dest[u+5] = tbyte;
					if ( (tbyte=source[u+6]) != TRANSPARENT_COLOR)
						dest[u+6] = tbyte;
					if ( (tbyte=source[u+7]) != TRANSPARENT_COLOR)
						dest[u+7] = tbyte;
				}
				dest += vid.rowbytes;
				source += pic->width;
			}
		}
	}
	else
	{
	// FIXME: pretranslate at load time?
		pusdest = (unsigned short *)vid.buffer + y * (vid.rowbytes >> 1) + x;

		for (v=0 ; v<height ; v++)
		{
			for (u=0 ; u<width ; u++)
			{
				tbyte = source[u];

				if (tbyte != TRANSPARENT_COLOR)
				{
					pusdest[u] = d_8to16table[tbyte];
				}
			}

			pusdest += vid.rowbytes >> 1;
			source += pic->width;
		}
	}
}


void R_DrawSubPic (int x, int y, mpic_t *pic, int srcx, int srcy, int width, int height)
{
	byte			*dest, *source;
	unsigned short	*pusdest;
	int				v, u;

	if (!pic)
		return;

	if ((x < 0) || (x + width > vid.width) ||
		(y < 0) || (y + height > vid.height))
	{
		Sys_Error ("R_DrawPic: bad coordinates");
	}

	if (pic->alpha) {
		R_DrawTransSubPic (x, y, pic, srcx, srcy, width, height);
		return;
	}

	source = ((cachepic_t *)pic)->data + srcy * pic->width + srcx;

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y * vid.rowbytes + x;

		for (v=0 ; v<height ; v++)
		{
			memcpy (dest, source, width);
			dest += vid.rowbytes;
			source += pic->width;
		}
	}
	else
	{
	// FIXME: pretranslate at load time?
		pusdest = (unsigned short *)vid.buffer + y * (vid.rowbytes >> 1) + x;

		for (v=0 ; v<height ; v++)
		{
			for (u=srcx ; u<(srcx+width) ; u++)
			{
				pusdest[u] = d_8to16table[source[u]];
			}

			pusdest += vid.rowbytes >> 1;
			source += pic->width;
		}
	}
}


/*
=============
R_DrawTransPicTranslate
=============
*/
void R_DrawTransPicTranslate (int x, int y, mpic_t *pic, byte *translation)
{
	byte	*dest, *source, tbyte;
	unsigned short	*pusdest;
	int				v, u;

	if (!pic)
		return;

	if (x < 0 || (unsigned)(x + pic->width) > vid.width || y < 0 ||
		 (unsigned)(y + pic->height) > vid.height)
	{
		Sys_Error ("Draw_TransPic: bad coordinates");
	}
		
	source = ((cachepic_t *)pic)->data;

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y * vid.rowbytes + x;

		if (pic->width & 7)
		{	// general
			for (v=0 ; v<pic->height ; v++)
			{
				for (u=0 ; u<pic->width ; u++)
					if ( (tbyte=source[u]) != TRANSPARENT_COLOR)
						dest[u] = translation[tbyte];

				dest += vid.rowbytes;
				source += pic->width;
			}
		}
		else
		{	// unwound
			for (v=0 ; v<pic->height ; v++)
			{
				for (u=0 ; u<pic->width ; u+=8)
				{
					if ( (tbyte=source[u]) != TRANSPARENT_COLOR)
						dest[u] = translation[tbyte];
					if ( (tbyte=source[u+1]) != TRANSPARENT_COLOR)
						dest[u+1] = translation[tbyte];
					if ( (tbyte=source[u+2]) != TRANSPARENT_COLOR)
						dest[u+2] = translation[tbyte];
					if ( (tbyte=source[u+3]) != TRANSPARENT_COLOR)
						dest[u+3] = translation[tbyte];
					if ( (tbyte=source[u+4]) != TRANSPARENT_COLOR)
						dest[u+4] = translation[tbyte];
					if ( (tbyte=source[u+5]) != TRANSPARENT_COLOR)
						dest[u+5] = translation[tbyte];
					if ( (tbyte=source[u+6]) != TRANSPARENT_COLOR)
						dest[u+6] = translation[tbyte];
					if ( (tbyte=source[u+7]) != TRANSPARENT_COLOR)
						dest[u+7] = translation[tbyte];
				}
				dest += vid.rowbytes;
				source += pic->width;
			}
		}
	}
	else
	{
	// FIXME: pretranslate at load time?
		pusdest = (unsigned short *)vid.buffer + y * (vid.rowbytes >> 1) + x;

		for (v=0 ; v<pic->height ; v++)
		{
			for (u=0 ; u<pic->width ; u++)
			{
				tbyte = source[u];

				if (tbyte != TRANSPARENT_COLOR)
				{
					pusdest[u] = d_8to16table[tbyte];
				}
			}

			pusdest += vid.rowbytes >> 1;
			source += pic->width;
		}
	}
}


//
// negative y values are allowed
//
void R_DrawStretchPic (int x, int y, int width, int height, mpic_t *pic, float alpha)
{
	int			i, j;
	byte		*src, *dest;
	int			startline;
	unsigned	frac, fracstep;

	if (!pic || !alpha)
		return;

	if ((x < 0) || (x + width > vid.width) || (y + height > vid.height)) {
		Sys_Error ("R_DrawStretchPic: bad coordinates");
	}

	if (y + height <= 0)
		return;			// completely outside the screen

	startline = (y >= 0) ? 0 : -y;

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + (y + startline) * vid.rowbytes + x;
		fracstep = pic->width * 0x10000 / width;

		for (i = startline; i < height; i++)
		{
			src = ((cachepic_t *)pic)->data
							+ pic->width * (i * pic->height / height);
			if (width == pic->width) {
				memcpy (dest, src, width);
				src += pic->width;
				dest += vid.rowbytes;
			}
			else {
				frac = fracstep >> 1;
				for (j = width >> 2; j; j--)
				{
					dest[0] = src[frac>>16];	frac += fracstep;
					dest[1] = src[frac>>16];	frac += fracstep;
					dest[2] = src[frac>>16];	frac += fracstep;
					dest[3] = src[frac>>16];	frac += fracstep;
					dest += 4;
				}
				for (j = width & 3; j; j--)
				{
					*dest = src[frac>>16];	frac += fracstep;
					dest++;
				}
				src += pic->width;
				dest += vid.rowbytes - width;
			}
		}
	}
	else {
/*		unsigned short	*pusdest;

		pusdest = (unsigned short *)vid.buffer;

		for (y=0 ; y<lines ; y++, pusdest += (vid.rowbytes >> 1))
		{
		// FIXME: pre-expand to native format?
		// FIXME: does the endian switching go away in production?
			v = (vid.conheight - lines + y)*200/vid.conheight;
			src = conback->data + v*320;
			frac = 0;
			fracstep = 320*0x10000/vid.width;
			for (x=0 ; x<vid.width ; x+=4)
			{
				pusdest[x] = d_8to16table[src[frac>>16]];
				frac += fracstep;
				pusdest[x+1] = d_8to16table[src[frac>>16]];
				frac += fracstep;
				pusdest[x+2] = d_8to16table[src[frac>>16]];
				frac += fracstep;
				pusdest[x+3] = d_8to16table[src[frac>>16]];
				frac += fracstep;
			}
		}
*/
	}
}

/*
==============
R_DrawRect8
==============
*/
void R_DrawRect8 (vrect_t *prect, int rowbytes, byte *psrc,
	int transparent)
{
	byte	t;
	int		i, j, srcdelta, destdelta;
	byte	*pdest;

	pdest = vid.buffer + (prect->y * vid.rowbytes) + prect->x;

	srcdelta = rowbytes - prect->width;
	destdelta = vid.rowbytes - prect->width;

	if (transparent)
	{
		for (i=0 ; i<prect->height ; i++)
		{
			for (j=0 ; j<prect->width ; j++)
			{
				t = *psrc;
				if (t != TRANSPARENT_COLOR)
				{
					*pdest = t;
				}

				psrc++;
				pdest++;
			}

			psrc += srcdelta;
			pdest += destdelta;
		}
	}
	else
	{
		for (i=0 ; i<prect->height ; i++)
		{
			memcpy (pdest, psrc, prect->width);
			psrc += rowbytes;
			pdest += vid.rowbytes;
		}
	}
}


/*
==============
R_DrawRect16
==============
*/
void R_DrawRect16 (vrect_t *prect, int rowbytes, byte *psrc,
	int transparent)
{
	byte			t;
	int				i, j, srcdelta, destdelta;
	unsigned short	*pdest;

// FIXME: would it be better to pre-expand native-format versions?

	pdest = (unsigned short *)vid.buffer +
			(prect->y * (vid.rowbytes >> 1)) + prect->x;

	srcdelta = rowbytes - prect->width;
	destdelta = (vid.rowbytes >> 1) - prect->width;

	if (transparent)
	{
		for (i=0 ; i<prect->height ; i++)
		{
			for (j=0 ; j<prect->width ; j++)
			{
				t = *psrc;
				if (t != TRANSPARENT_COLOR)
				{
					*pdest = d_8to16table[t];
				}

				psrc++;
				pdest++;
			}

			psrc += srcdelta;
			pdest += destdelta;
		}
	}
	else
	{
		for (i=0 ; i<prect->height ; i++)
		{
			for (j=0 ; j<prect->width ; j++)
			{
				*pdest = d_8to16table[*psrc];
				psrc++;
				pdest++;
			}

			psrc += srcdelta;
			pdest += destdelta;
		}
	}
}


/*
=============
R_DrawTile

This repeats a 64*64 tile graphic to fill the screen around a sized down
refresh window.
=============
*/

// FIXME: clean this up!
typedef struct {
	vrect_t	rect;
	int		width;
	int		height;
	byte	*ptexbytes;
	int		rowbytes;
} rectdesc_t;
static rectdesc_t	r_rectdesc;

void R_DrawTile (int x, int y, int w, int h, mpic_t *pic)
{
	int				width, height, tileoffsetx, tileoffsety;
	byte			*psrc;
	vrect_t			vr;

	r_rectdesc.width = pic->width;
	r_rectdesc.rowbytes = pic->width;
	r_rectdesc.height = pic->height;
	r_rectdesc.ptexbytes = ((cachepic_t *)pic)->data;

	r_rectdesc.rect.x = x;
	r_rectdesc.rect.y = y;
	r_rectdesc.rect.width = w;
	r_rectdesc.rect.height = h;

	vr.y = r_rectdesc.rect.y;
	height = r_rectdesc.rect.height;

	tileoffsety = vr.y % r_rectdesc.height;

	while (height > 0)
	{
		vr.x = r_rectdesc.rect.x;
		width = r_rectdesc.rect.width;

		if (tileoffsety != 0)
			vr.height = r_rectdesc.height - tileoffsety;
		else
			vr.height = r_rectdesc.height;

		if (vr.height > height)
			vr.height = height;

		tileoffsetx = vr.x % r_rectdesc.width;

		while (width > 0)
		{
			if (tileoffsetx != 0)
				vr.width = r_rectdesc.width - tileoffsetx;
			else
				vr.width = r_rectdesc.width;

			if (vr.width > width)
				vr.width = width;

			psrc = r_rectdesc.ptexbytes +
					(tileoffsety * r_rectdesc.rowbytes) + tileoffsetx;

			if (r_pixbytes == 1)
			{
				R_DrawRect8 (&vr, r_rectdesc.rowbytes, psrc, 0);
			}
			else
			{
				R_DrawRect16 (&vr, r_rectdesc.rowbytes, psrc, 0);
			}

			vr.x += vr.width;
			width -= vr.width;
			tileoffsetx = 0;	// only the left tile can be left-clipped
		}

		vr.y += vr.height;
		height -= vr.height;
		tileoffsety = 0;		// only the top tile can be top-clipped
	}
}


/*
=============
R_DrawFilledRect

Fills a box of pixels with a single color
=============
*/
void R_DrawFilledRect (int x, int y, int w, int h, int c)
{
	byte			*dest;
	unsigned short	*pusdest;
	unsigned		uc;
	int				u, v;

	if (x < 0 || x + w > vid.width ||
		y < 0 || y + h > vid.height) {
		Sys_Error ("Bad R_DrawFilledRect (%d, %d, %d, %d, %c)", x, y, w, h, c);
		return;
	}

	if (r_pixbytes == 1)
	{
		dest = vid.buffer + y*vid.rowbytes + x;
		for (v=0 ; v<h ; v++, dest += vid.rowbytes)
			for (u=0 ; u<w ; u++)
				dest[u] = c;
	}
	else
	{
		uc = d_8to16table[c];

		pusdest = (unsigned short *)vid.buffer + y * (vid.rowbytes >> 1) + x;
		for (v=0 ; v<h ; v++, pusdest += (vid.rowbytes >> 1))
			for (u=0 ; u<w ; u++)
				pusdest[u] = uc;
	}
}
//=============================================================================

void R_FadeScreen (void)
{
	int			x,y;
	byte		*pbuf;

	S_ExtraUpdate ();

	for (y=0 ; y<vid.height ; y++)
	{
		int	t;

		pbuf = (byte *)(vid.buffer + vid.rowbytes*y);
		t = (y & 1) << 1;

		for (x=0 ; x<vid.width ; x++)
		{
			if ((x & 3) != t)
				pbuf[x] = 0;
		}
	}

	S_ExtraUpdate ();
}

//=============================================================================

/*
================
R_BeginDisc

Draws the little blue disc in the corner of the screen.
Call before beginning any disc IO.
================
*/
void R_BeginDisc (void)
{
	if (!draw_disc)
		return;

	D_BeginDirectRect (vid.width - 24, 0, ((cachepic_t *)draw_disc)->data, 24, 24);
}


/*
================
R_EndDisc

Erases the disc icon.
Call after completing any disc IO
================
*/
void R_EndDisc (void)
{
	if (!draw_disc)
		return;

	D_EndDirectRect (vid.width - 24, 0, 24, 24);
}

