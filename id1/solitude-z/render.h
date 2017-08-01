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
// render.h -- public interface to rendering functions
#ifndef _RENDER_H_
#define _RENDER_H_

#define	TOP_RANGE		16			// soldier uniform colors
#define	BOTTOM_RANGE	96

#define	MAX_VISEDICTS			256
#define MAX_PARTICLES			4096	// default max # of particles at one
										// time

// entity->renderfx
#define RF_WEAPONMODEL	1
#define RF_PLAYERMODEL	2
#define RF_TRANSLUCENT	4
#define RF_LIMITLERP	8

//=============================================================================

typedef struct
{
	int		length;
	char	map[64];
} lightstyle_t;


#define	MAX_DLIGHTS		32

typedef enum {	lt_default, lt_blue, lt_red, lt_redblue, lt_muzzleflash,
				lt_explosion, lt_rocket, NUM_DLIGHTTYPES
} dlighttype_t;

typedef struct
{
	int				key;		// FIXME
	vec3_t			origin;
	float			radius;
	float			minlight;
	dlighttype_t	type;
} dlight_t;

typedef struct efrag_s
{
	struct mleaf_s		*leaf;
	struct efrag_s		*leafnext;
	struct entity_s		*entity;
	struct efrag_s		*entnext;
} efrag_t;

typedef struct entity_s
{
	vec3_t					origin;
	vec3_t					angles;
	struct model_s			*model;			// NULL = no model
	int						frame;
	int						oldframe;		// frame to lerp from
	float					backlerp;
	int						colormap;
	int						skinnum;		// for alias models
	int						renderfx;		// RF_WEAPONMODEL, etc
	float					alpha;

	struct efrag_s			*efrag;			// linked list of efrags (FIXME)
	int						visframe;		// last frame this entity was
											// found in an active leaf
											// only used for static objects

// FIXME: could turn these into a union
	int						trivial_accept;
	struct mnode_s			*topnode;		// for bmodels, first world node
											//  that splits bmodel, or NULL if
											//  not split
} entity_t;

// !!! if this is changed, it must be changed in d_ifacea.h too !!!
typedef struct particle_s
{
	vec3_t		org;
	int			color;
	float		alpha;
} particle_t;


typedef struct translation_info_s {
	int		topcolor;
	int		bottomcolor;
	char	skinname[32];
} translation_info_t;


// eye position, enitiy list, etc - filled in before calling R_RenderView
typedef struct {
	vrect_t			vrect;			// subwindow in video for refresh

	vec3_t			vieworg;
	vec3_t			viewangles;
	float			fov_x, fov_y;

	float			time;
	qbool			allow_cheats;
	qbool			allow_fbskins;
	int				viewplayernum;	// don't draw own glow when gl_flashblend 1
	qbool			watervis;

	lightstyle_t	*lightstyles;
	int				numDlights;
	dlight_t		*dlights;
	int				numParticles;
	particle_t		*particles;

	translation_info_t	*translations;	// [MAX_CLIENTS]
	char			baseskin[32];
} refdef2_t;


typedef struct mpic_s
{
	int			width;
	int			height;
	qbool		alpha;	// will be true if there are any transparent pixels
} mpic_t;

//====================================================


//
// refresh
//
extern refdef2_t	r_refdef2;

void R_Init (unsigned char *palette);
void R_InitTextures (void);
void R_InitEfrags (void);
void R_RenderView (void);		// must set r_refdef first
void R_SetSky (char *name);				// Quake2 skybox
// called whenever r_refdef or vid change

void R_AddEfrags (entity_t *ent);
void R_RemoveEfrags (entity_t *ent);

void R_NewMap (struct model_s *worldmodel);

void R_PushDlights (void);

// memory pointed to by pcxdata is allocated using Hunk_TempAlloc
// never store this pointer for later use!
void R_RSShot (byte **pcxdata, int *pcxsize);

//
// surface cache related
//
extern qbool	r_cache_thrash;	// set if thrashing the surface cache

int	D_SurfaceCacheForRes (int width, int height);
void D_FlushCaches (void);
void D_InitCaches (void *buffer, int size);

// 2D drawing functions
void R_DrawChar (int x, int y, int num);
void R_DrawCharW (int x, int y, wchar num);
void R_DrawString (int x, int y, const char *str);
void R_DrawStringW (int x, int y, const wchar *str);
void R_DrawPixel (int x, int y, byte color);
void R_DrawPic (int x, int y, mpic_t *pic);
void R_DrawSubPic (int x, int y, mpic_t *pic, int srcx, int srcy, int width, int height);
void R_DrawTransPicTranslate (int x, int y, mpic_t *pic, byte *translation);
void R_DrawFilledRect (int x, int y, int w, int h, int c);
void R_DrawTile (int x, int y, int w, int h, mpic_t *pic);
void R_FadeScreen (void);
void R_DrawDebugChar (char num);
void R_BeginDisc (void);
void R_EndDisc (void);
mpic_t *R_CachePic (char *path);
mpic_t *R_CacheWadPic (char *name);
void R_FlushPics (void);
void R_DrawStretchPic (int x, int y, int width, int height, mpic_t *pic, float alpha);
void R_DrawCrosshair (int num, int crossx, int crossy);

#define GetPicWidth(pic) (pic->width)
#define GetPicHeight(pic) (pic->height)

// model flags
#define	MF_ROCKET	1			// leave a trail
#define	MF_GRENADE	2			// leave a trail
#define	MF_GIB		4			// leave a trail
#define	MF_ROTATE	8			// rotate (bonus items)
#define	MF_TRACER	16			// green split trail
#define	MF_ZOMGIB	32			// small blood trail
#define	MF_TRACER2	64			// orange split trail + rotate
#define	MF_TRACER3	128			// purple trail

void Mod_ClearAll (void);
void Mod_TouchModel (char *name);
struct model_s *Mod_ForName (char *name, qbool crash, qbool worldmodel);
int R_ModelFlags (const struct model_s *model);
unsigned short R_ModelChecksum (const struct model_s *model);
void R_LoadModelTextures (struct model_s *m);

#endif /* _RENDER_H_ */

