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
// r_misc.c

#include "gl_local.h"
#include "rc_image.h"
#include <time.h>


int solidskytexture, alphaskytexture;
int lightmap_textures;
int particletexture;	// little dot for particles
int	playertextures;		// up to 32 color translated skins
int	playerfbtextures[MAX_CLIENTS];
int	skyboxtextures;


void GL_AllocTextureSlots (void)
{
	netgraphtexture = texture_extension_number++;

	playertextures = texture_extension_number;
	texture_extension_number += MAX_CLIENTS * 2 /* normal and fullbright */;

	skyboxtextures = texture_extension_number;
	texture_extension_number += 6;

	solidskytexture = texture_extension_number++;
	alphaskytexture = texture_extension_number++;

	lightmap_textures = texture_extension_number;
	texture_extension_number += MAX_LIGHTMAPS;
}


/*
=============================================================

  TRANSLATED PLAYER SKINS

=============================================================
*/

typedef struct r_translation_s {
	int topcolor;
	int bottomcolor;
	char skinname[32];
} r_translation_t;

static r_translation_t r_translations[MAX_CLIENTS];
static struct skin_s *r_baseskin;
static char cur_baseskin[32];

// called on startup and every time gamedir changes
void R_FlushTranslations (void)
{
	int i;

	Skin_Flush ();
	for (i = 0; i < MAX_CLIENTS; i++) {
		r_translations[i].topcolor = -1; // this will force a rebuild
		r_translations[i].skinname[0] = 0;
	}
	r_baseskin = NULL;
	cur_baseskin[0] = 0;
}


void R_TranslatePlayerSkin (int playernum, byte *original)
{
	int		top, bottom;
	byte	translate[256];
	unsigned	translate32[256];
	int		i, j;
	unsigned	pixels[512*256], *out;
	int			scaled_width, scaled_height;
	int			inwidth, inheight;
	int			tinwidth, tinheight;
	byte		*inrow;
	unsigned	frac, fracstep;
	extern	byte		player_8bit_texels[320*200];

//Com_Printf ("R_TranslatePlayerSkin: %s %i\n", r_translations[playernum].skinname, r_translations[playernum].topcolor);

	GL_DisableMultitexture();

	top = r_translations[playernum].topcolor;
	bottom = r_translations[playernum].bottomcolor;
	top = (top < 0) ? 0 : ((top > 13) ? 13 : top);
	bottom = (bottom < 0) ? 0 : ((bottom > 13) ? 13 : bottom);
	top *= 16;
	bottom *= 16;

	for (i = 0; i < 256; i++)
			translate[i] = i;

	for (i = 0; i < 16; i++)
	{
		if (top < 128)	// the artists made some backwards ranges.  sigh.
			translate[TOP_RANGE+i] = top+i;
		else
			translate[TOP_RANGE+i] = top+15-i;

		if (bottom < 128)
			translate[BOTTOM_RANGE+i] = bottom+i;
		else
			translate[BOTTOM_RANGE+i] = bottom+15-i;
	}

	for (i=0 ; i<256 ; i++)
		translate32[i] = d_8to24table[translate[i]];


	//
	// locate the original skin pixels
	//
	// real model width
	tinwidth = 296;
	tinheight = 194;

	if (original) {
		//skin data width
		inwidth = 320;
		inheight = 200;
	} else {
		original = player_8bit_texels;
		inwidth = 296;
		inheight = 194;
	}


	// because this happens during gameplay, do it fast
	// instead of sending it through gl_upload 8
	GL_Bind(playertextures + playernum);

	scaled_width = min (gl_max_texsize, 512);
	scaled_height = min (gl_max_texsize, 256);

	// allow users to crunch sizes down even more if they want
	scaled_width >>= (int)gl_playermip.value;
	scaled_height >>= (int)gl_playermip.value;
	if (scaled_width < 1)
		scaled_width = 1;
	if (scaled_height < 1)
		scaled_height = 1;

	// scale and upload the texture
	out = pixels;
	memset(pixels, 0, sizeof(pixels));
	fracstep = tinwidth*0x10000/scaled_width;
	for (i=0 ; i<scaled_height ; i++, out += scaled_width)
	{
		inrow = original + inwidth*(i*tinheight/scaled_height);
		frac = fracstep >> 1;
		for (j=0 ; j<scaled_width ; j+=4)
		{
			out[j] = translate32[inrow[frac>>16]];
			frac += fracstep;
			out[j+1] = translate32[inrow[frac>>16]];
			frac += fracstep;
			out[j+2] = translate32[inrow[frac>>16]];
			frac += fracstep;
			out[j+3] = translate32[inrow[frac>>16]];
			frac += fracstep;
		}
	}

	glTexImage2D (GL_TEXTURE_2D, 0, gl_solid_format, 
		scaled_width, scaled_height, 0, GL_RGBA, 
		GL_UNSIGNED_BYTE, pixels);

	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

	playerfbtextures[playernum] = 0;
	if (Img_HasFullbrights ((byte *)original, inwidth*inheight))
	{
		playerfbtextures[playernum] = playertextures + playernum + MAX_CLIENTS;
		GL_Bind (playerfbtextures[playernum]);

		out = pixels;
		memset(pixels, 0, sizeof(pixels));
		fracstep = tinwidth*0x10000/scaled_width;

		// make all non-fullbright colors transparent
		for (i=0 ; i<scaled_height ; i++, out += scaled_width)
		{
			inrow = original + inwidth*(i*tinheight/scaled_height);
			frac = fracstep >> 1;
			for (j=0 ; j<scaled_width ; j+=4)
			{
				if (inrow[frac>>16] < 224)
					out[j] = translate32[inrow[frac>>16]] & LittleLong(0x00FFFFFF); // transparent
				else
					out[j] = translate32[inrow[frac>>16]]; // fullbright
				frac += fracstep;
				if (inrow[frac>>16] < 224)
					out[j+1] = translate32[inrow[frac>>16]] & LittleLong(0x00FFFFFF);
				else
					out[j+1] = translate32[inrow[frac>>16]];
				frac += fracstep;
				if (inrow[frac>>16] < 224)
					out[j+2] = translate32[inrow[frac>>16]] & LittleLong(0x00FFFFFF);
				else
					out[j+2] = translate32[inrow[frac>>16]];
				frac += fracstep;
				if (inrow[frac>>16] < 224)
					out[j+3] = translate32[inrow[frac>>16]] & LittleLong(0x00FFFFFF);
				else
					out[j+3] = translate32[inrow[frac>>16]];
				frac += fracstep;
			}
		}

		glTexImage2D (GL_TEXTURE_2D, 0, gl_alpha_format, 
			scaled_width, scaled_height, 0, GL_RGBA, 
			GL_UNSIGNED_BYTE, pixels);

		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	}
}


void R_GetTranslatedPlayerSkin (int colormap, int *texture, int *fb_texture)
{
	struct skin_s *skin;
	byte *data;
	r_translation_t *cur;
	translation_info_t *new;

	assert (colormap >= 0 && colormap <= MAX_CLIENTS);
	if (!colormap)
		return;

	cur = r_translations + (colormap - 1);
	new = r_refdef2.translations + (colormap - 1);

	// rebuild if necessary
	if (new->topcolor != cur->topcolor
		|| new->bottomcolor != cur->bottomcolor
		|| strcmp(new->skinname, cur->skinname))
	{
		cur->topcolor = new->topcolor;
		cur->bottomcolor = new->bottomcolor;
		strlcpy (cur->skinname, new->skinname, sizeof(cur->skinname));

		if (!cur->skinname[0]) {
			data = NULL;
			goto inlineskin;
		}

		Skin_Find (r_translations[colormap - 1].skinname, &skin);
		data = Skin_Cache (skin);
		if (!data) {
			if (r_refdef2.baseskin[0] && strcmp(r_refdef2.baseskin, cur->skinname)) {
				if (strcmp(cur_baseskin, r_refdef2.baseskin))
				{
					strlcpy (cur_baseskin, r_refdef2.baseskin, sizeof(cur_baseskin));
					if (!cur_baseskin[0]) {
						data = NULL;
						goto inlineskin;
					}
					Skin_Find (r_refdef2.baseskin, &r_baseskin);
				}
				data = Skin_Cache (r_baseskin);
			}
		}

inlineskin:
		R_TranslatePlayerSkin (colormap - 1, data);
	}

	*texture = playertextures + (colormap - 1);
	*fb_texture = playerfbtextures[colormap - 1];
}


/*
===============
R_NewMap
===============
*/
void R_NewMap (struct model_s *worldmodel)
{
	int		i;

	for (i=0 ; i<256 ; i++)
		d_lightstylevalue[i] = 264;		// normal light value

	r_worldmodel = worldmodel;

	memset (&r_worldentity, 0, sizeof(r_worldentity));
	r_worldentity.model = r_worldmodel;

// clear out efrags in case the level hasn't been reloaded
// FIXME: is this one short?
	for (i = 0; i < r_worldmodel->numleafs; i++)
		r_worldmodel->leafs[i].efrags = NULL;
		 	
	r_viewleaf = NULL;

	GL_BuildLightmaps ();

	memset (playerfbtextures, 0, sizeof(playerfbtextures));

	// identify sky texture
	skytexturenum = -1;
	for (i = 0; i < r_worldmodel->numtextures; i++)
	{
		if (!r_worldmodel->textures[i])
			continue;
		if (!strncmp(r_worldmodel->textures[i]->name,"sky",3) )
			skytexturenum = i;
 		r_worldmodel->textures[i]->texturechain = NULL;
	}

	r_skyboxloaded = false;

	R_FlushTranslations ();
}


/*
====================
R_TimeRefresh_f

For program optimization
====================
*/
void R_TimeRefresh_f (void)
{
	int			i;
	float		start, stop, time;

	if (cls.state != ca_active)
		return;

	glDrawBuffer  (GL_FRONT);
	glFinish ();

	start = Sys_DoubleTime ();
	for (i = 0; i < 128; i++)
	{
		r_refdef2.viewangles[1] = i * (360.0 / 128.0);
		R_RenderView ();
	}

	glFinish ();
	stop = Sys_DoubleTime ();
	time = stop-start;
	Com_Printf ("%f seconds (%f fps)\n", time, 128/time);

	glDrawBuffer  (GL_BACK);
	GL_EndRendering ();
}

void D_FlushCaches (void)
{
	// maybe it's not the right place for this code, but it serves
	// its purpose - set lightmode to gl_lightmode before loading
	// any models for a new map
	lightmode = gl_lightmode.value;
	if (lightmode < 0 || lightmode > 2)
		lightmode = 2;

	// FIXME - remove this when gl_lightmode 1 is implemented!
	if (lightmode == 1)
		lightmode = 2;
}


void R_LoadSky_f ()
{
	if (Cmd_Argc() < 2) {
		Com_Printf ("loadsky <name> : load a custom skybox\n");
		return;
	}

	R_SetSky (Cmd_Argv(1));
}


/* 
============================================================================== 
 
						SCREEN SHOTS 
 
============================================================================== 
*/ 

typedef struct _TargaHeader {
	unsigned char   id_length, colormap_type, image_type;
	unsigned short  colormap_index, colormap_length;
	unsigned char   colormap_size;
	unsigned short  x_origin, y_origin, width, height;
	unsigned char   pixel_size, attributes;
} TargaHeader;


/* 
================== 
R_ScreenShot_f
================== 
*/  
void R_ScreenShot_f (void)
{
	byte	*buffer;
	char	pcxname[MAX_OSPATH]; 
	char	checkname[MAX_OSPATH];
	int		i, c, temp;
	FILE	*f;

	if (Cmd_Argc() == 2) {
		strlcpy (pcxname, Cmd_Argv(1), sizeof(pcxname));
		COM_ForceExtension (pcxname, ".tga");
	}
	else
	{
		// 
		// find a file name to save it to 
		// 
		strcpy(pcxname,"quake00.tga");
		
		for (i = 0; i <= 99; i++) 
		{ 
			pcxname[5] = i/10 + '0'; 
			pcxname[6] = i%10 + '0'; 
			sprintf (checkname, "%s/%s", cls.gamedir, pcxname);
			f = fopen (checkname, "rb");
			if (!f)
				break;  // file doesn't exist
			fclose (f);
		} 
		if (i==100) 
		{
			Com_Printf ("R_ScreenShot_f: Couldn't create a TGA file\n"); 
			return;
		}
	}		

	buffer = Q_malloc (vid.realwidth * vid.realheight * 3 + 18);
	memset (buffer, 0, 18);
	buffer[2] = 2;          // uncompressed type
	buffer[12] = vid.realwidth&255;
	buffer[13] = vid.realwidth>>8;
	buffer[14] = vid.realheight&255;
	buffer[15] = vid.realheight>>8;
	buffer[16] = 24;        // pixel size

	glReadPixels (0, 0, vid.realwidth, vid.realheight, GL_RGB, GL_UNSIGNED_BYTE, buffer+18 ); 

	// swap rgb to bgr
	c = 18 + vid.realwidth * vid.realheight * 3;
	for (i=18 ; i<c ; i+=3)
	{
		temp = buffer[i];
		buffer[i] = buffer[i+2];
		buffer[i+2] = temp;
	}
	COM_WriteFile (va("%s/%s", cls.gamedirfile, pcxname), buffer, vid.realwidth*vid.realheight*3 + 18 );

	Q_free (buffer);
	Com_Printf ("Wrote %s\n", pcxname);
} 
 


/*
Find closest color in the palette for named color
*/
int MipColor(int r, int g, int b)
{
	int i;
	float dist;
	int best = 0;
	float bestdist;
	int r1, g1, b1;
	static int lr = -1, lg = -1, lb = -1;
	static int lastbest;

	if (r == lr && g == lg && b == lb)
		return lastbest;

	bestdist = 256*256*3;

	for (i = 0; i < 256; i++) {
		r1 = host_basepal[i*3] - r;
		g1 = host_basepal[i*3+1] - g;
		b1 = host_basepal[i*3+2] - b;
		dist = r1*r1 + g1*g1 + b1*b1;
		if (dist < bestdist) {
			bestdist = dist;
			best = i;
		}
	}
	lr = r; lg = g; lb = b;
	lastbest = best;
	return best;
}

// from gl_draw.c
extern byte		*draw_chars;				// 8*8 graphic characters

void R_DrawCharToSnap (int num, byte *dest, int width)
{
	int		row, col;
	byte	*source;
	int		drawline;
	int		x;

	row = num>>4;
	col = num&15;
	source = draw_chars + (row<<10) + (col<<3);

	drawline = 8;

	while (drawline--)
	{
		for (x=0 ; x<8 ; x++)
			if (source[x])
				dest[x] = source[x];
			else
				dest[x] = 98;
		source += 128;
		dest -= width;
	}

}

void R_DrawStringToSnap (const char *s, byte *buf, int x, int y, int width)
{
	byte *dest;
	const unsigned char *p;

	dest = buf + ((y * width) + x);

	p = (const unsigned char *)s;
	while (*p) {
		R_DrawCharToSnap(*p++, dest, width);
		dest += 8;
	}
}


/* 
================== 
R_RSShot

Memory pointed to by pcxdata is allocated using Hunk_TempAlloc
Never store this pointer for later use!

On failure (not enough memory), *pcxdata will be set to NULL
================== 
*/  
#define RSSHOT_WIDTH 320
#define RSSHOT_HEIGHT 200
void R_RSShot (byte **pcxdata, int *pcxsize)
{ 
	int     x, y;
	unsigned char	*src, *dest;
	unsigned char	*newbuf;
	int w, h;
	int dx, dy, dex, dey, nx;
	int r, b, g;
	int count;
	float fracw, frach;
	char st[80];
	time_t now;
	extern cvar_t name;

// 
// save the pcx file 
// 
	newbuf = Q_malloc (vid.realheight * vid.realwidth * 3);

	glReadPixels (0, 0, vid.realwidth, vid.realheight, GL_RGB, GL_UNSIGNED_BYTE, newbuf);

	w = min (vid.realwidth, RSSHOT_WIDTH);
	h = min (vid.realheight, RSSHOT_HEIGHT);

	fracw = (float)vid.realwidth / (float)w;
	frach = (float)vid.realheight / (float)h;

	for (y = 0; y < h; y++) {
		dest = newbuf + (w*3 * y);

		for (x = 0; x < w; x++) {
			r = g = b = 0;

			dx = x * fracw;
			dex = (x + 1) * fracw;
			if (dex == dx) dex++; // at least one
			dy = y * frach;
			dey = (y + 1) * frach;
			if (dey == dy) dey++; // at least one

			count = 0;
			for (/* */; dy < dey; dy++) {
				src = newbuf + (vid.realwidth * 3 * dy) + dx * 3;
				for (nx = dx; nx < dex; nx++) {
					r += *src++;
					g += *src++;
					b += *src++;
					count++;
				}
			}
			r /= count;
			g /= count;
			b /= count;
			*dest++ = r;
			*dest++ = g;
			*dest++ = b;
		}
	}

	// convert to eight bit
	for (y = 0; y < h; y++) {
		src = newbuf + (w * 3 * y);
		dest = newbuf + (w * y);

		for (x = 0; x < w; x++) {
			*dest++ = MipColor(src[0], src[1], src[2]);
			src += 3;
		}
	}

	time(&now);
	strcpy(st, ctime(&now));
	st[strlen(st) - 1] = 0;
	R_DrawStringToSnap (st, newbuf, w - strlen(st)*8, h - 1, w);

	strlcpy (st, cls.servername, sizeof(st));
	R_DrawStringToSnap (st, newbuf, w - strlen(st)*8, h - 11, w);

	strlcpy (st, name.string, sizeof(st));
	R_DrawStringToSnap (st, newbuf, w - strlen(st)*8, h - 21, w);

	// +w*(h-1) and -w are because we have the data upside down in newbuf
	WritePCX (newbuf + w*(h-1), w, h, -w, host_basepal, pcxdata, pcxsize);

	Q_free (newbuf);

	// return with pcxdata and pcxsize
} 

//=============================================================================
