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
#ifndef _RC_IMAGE_H_
#define _RC_IMAGE_H_

#ifdef WITH_PNG
#include "png.h"
#endif

#define IMAGE_MAX_DIMENSIONS 4096

#ifdef WITH_PNG
typedef struct
{
	byte *data;
	png_textp textchunks;
	size_t text_count;
} png_data;

png_textp Image_LoadPNG_Comments (char *filename, int *text_count);
png_data *Image_LoadPNG_All (FILE *fin, char *filename, int matchwidth, int matchheight, int loadflag);
byte *Image_LoadPNG (FILE *, char *, int, int);
byte *Image_LoadTGA (FILE *, char *, int, int);
byte *Image_LoadPCX (FILE *, char *, int, int);

int Image_WritePNG(char *filename, int compression, byte *pixels, int width, int height);
#ifdef GLQUAKE
int Image_WritePNGPLTE (char *filename, int compression, byte *pixels,
						int width, int height, byte *palette);
#else
int Image_WritePNGPLTE (char *filename, int compression, byte *pixels,
						int width, int height, int rowbytes, byte *palette);
#endif
#endif	// WITH_PNG

void LoadTGA (char *filename, byte **out, int *width, int *height);
void LoadPCX (char *filename, byte **pic, int *width, int *height);
void WritePCX (byte *data, int width, int height, int rowbytes, byte *palette,	// [in]
				   byte **pcxdata, int *pcxsize);								// [out]

void Image_Init(void);

#endif /* _RC_IMAGE_H_ */

