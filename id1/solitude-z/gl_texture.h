/*
Copyright (C) 1996-1997 Id Software, Inc.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the included (GNU.txt) GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

#ifndef __GL_TEXTURE_H
#define __GL_TEXTURE_H

#define MAX_GLTEXTURES 1024

// texture "mode" bits, passed to upload functions
#define TEX_MIPMAP			1	// build mipmaps
#define TEX_ALPHA			2	// has alpha pixels
#define	TEX_FULLBRIGHTMASK	4	// implies TEX_ALPHA
#define	TEX_BRIGHTEN		8	// apply palette hack
#define	TEX_NOSCALE			16	// don't apply gl_picmip
#define TEX_WORLD			32	// world, including inline brushes
#define TEX_MODEL			64	// alias + external brushes (e.g. health box)
#define TEX_TURB			128	// water, teleports (TEX_WORLD may also be set)
#define TEX_SPRITE			256	// wanna guess?

// TEX_MIPMAP, TEX_ALPHA
void GL_Upload32 (unsigned *data, int width, int height, int mode);

// TEX_MIPMAP, TEX_ALPHA, TEX_FULLBRIGHTMASK, TEX_BRIGHTEN, TEX_NOSCALE
// + TEX WORLD etc
void GL_Upload8 (byte *data, int width, int height, int mode);

// TEX_MIPMAP, TEX_ALPHA, TEX_FULLBRIGHTMASK, TEX_BRIGHTEN, TEX_NOSCALE
// + TEX WORLD etc
int GL_LoadTexture (char *identifier, int width, int height, byte *data, int mode);

// TEX_MIPMAP, TEX_ALPHA, TEX_BRIGHTEN(FIXME not yet)
// + TEX WORLD etc
int GL_LoadTexture32 (char *identifier, int width, int height, byte *data, int mode);

int GL_FindTexture (char *identifier);
//int GL_LoadPicTexture (char *name, mpic_t *pic, byte *data);


void GL_Bind (int texnum);

void GL_SelectTexture (GLenum target);
void GL_DisableMultitexture (void);
void GL_EnableMultitexture (void);

/*
// here's what enginez has...
void GL_Upload8 (byte *data, int width, int height, int mode);
void GL_Upload32 (unsigned *data, int width, int height, int mode);
int GL_LoadTexture (char *identifier, int width, int height, byte *data, int mode, int bpp);

byte *GL_LoadImagePixels (char *, int, int, int);
int GL_LoadTexturePixels (byte *, char *, int, int, int);
mpic_t *GL_LoadPicImage (char *, char *, int, int, int);
int GL_LoadCharsetImage (char *, char *);

void GL_Texture_Init(void);
*/
int GL_LoadTextureImage (char * , char *, int, int, int);

extern int gl_lightmap_format, gl_solid_format, gl_alpha_format;

extern int currenttexture;
extern int cnttextures[2];

extern int gl_max_texsize;

extern int texture_extension_number;

extern unsigned d_8to24table[256];
void R_SetPalette (byte *palette);

#endif	//__GL_TEXTURE_H
