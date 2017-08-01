/*
Copyright (C) 1996-1997 Anton 'Tonik' Gavrilov

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
// rc_null.c - for when you don't want to video output at all

#include "common.h"
#include "vid.h"
#include "render.h"

//FIXMEs
short *d_pzbuffer;
void R_PushDlights (void) {}
void R_InitEfrags (void) {}
void R_AddEfrags (entity_t *ent) {}
void R_RemoveEfrags (entity_t *ent) {}
void D_DisableBackBufferAccess () {}
void D_EnableBackBufferAccess () {}


refdef2_t r_refdef2;

#define NUMVERTEXNORMALS	162
float	r_avertexnormals[NUMVERTEXNORMALS][3] = {
#include "anorms.h"
};

void R_Init (unsigned char *palette) {}
void R_InitTextures (void) {}
void R_RenderView (void) {}
void R_SetSky (char *name) {}
void R_NewMap (struct model_s *worldmodel) {}
void R_RSShot (byte **pcxdata, int *pcxsize) {}

// surface cache related
qbool r_cache_thrash;
int D_SurfaceCacheForRes (int width, int height) { return 0; }
void D_FlushCaches (void) {}
void D_InitCaches (void *buffer, int size) {}


// 2D drawing functions
void R_DrawChar (int x, int y, int num) {}
void R_DrawCharW (int x, int y, wchar num) {}
void R_DrawString (int x, int y, const char *str) {}
void R_DrawStringW (int x, int y, const wchar *str) {}
void R_DrawPixel (int x, int y, byte color) {}
void R_DrawPic (int x, int y, mpic_t *pic) {}
void R_DrawSubPic (int x, int y, mpic_t *pic, int srcx, int srcy, int width, int height) {}
void R_DrawTransPicTranslate (int x, int y, mpic_t *pic, byte *translation) {}
void R_DrawFilledRect (int x, int y, int w, int h, int c) {}
void R_DrawTile (int x, int y, int w, int h, mpic_t *pic) {}
void R_FadeScreen (void) {}
void R_DrawDebugChar (char num) {}
void R_BeginDisc (void) {}
void R_EndDisc (void) {}
mpic_t *R_CachePic (char *path) { return NULL; }
mpic_t *R_CacheWadPic (char *name) { return NULL; }
void R_FlushPics (void) {}
void R_DrawStretchPic (int x, int y, int width, int height, mpic_t *pic, float alpha) {}
void R_DrawCrosshair (int num, int crossx, int crossy) {}

// model loading
void Mod_ClearAll (void) {}
void Mod_TouchModel (char *name) {}
struct model_s *Mod_ForName (char *name, qbool crash) { return NULL; }
int R_ModelFlags (const struct model_s *model) { return 0; }
unsigned short R_ModelChecksum (const struct model_s *model) { return 0; }
void R_LoadModelTextures (struct model_s *m) {}
