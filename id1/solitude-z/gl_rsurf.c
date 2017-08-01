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
// r_surf.c: surface-related refresh code

#include "gl_local.h"

int		skytexturenum;

float	wateralpha;		// 1 if watervis is disabled by server,
						// otherwise equal to r_wateralpha.value

int		lightmap_bytes;		// 1, 2, or 4

#define	BLOCK_WIDTH		128
#define	BLOCK_HEIGHT	128

#define MAX_LIGHTMAP_SIZE	4096
#define	MAX_LIGHTMAPS		64

unsigned int	blocklights[MAX_LIGHTMAP_SIZE*3];


typedef struct glRect_s {
	unsigned char l,t,w,h;
} glRect_t;

glpoly_t	*lightmap_polys[MAX_LIGHTMAPS];
qbool		lightmap_modified[MAX_LIGHTMAPS];
glRect_t	lightmap_rectchange[MAX_LIGHTMAPS];

int			allocated[MAX_LIGHTMAPS][BLOCK_WIDTH];

// the lightmap texture data needs to be kept in
// main memory so texsubimage can update properly
byte		lightmaps[4*MAX_LIGHTMAPS*BLOCK_WIDTH*BLOCK_HEIGHT];

// For gl_texsort 0
msurface_t  *skychain = NULL;
msurface_t  *waterchain = NULL;

msurface_t	*worldchain = NULL;

void R_RenderDynamicLightmaps (msurface_t *fa);

glpoly_t	*fullbright_polys[MAX_GLTEXTURES];
qbool		drawfullbrights = false;

void DrawGLPoly (glpoly_t *p);

void R_RenderFullbrights (void)
{
	int         i;
	glpoly_t   *p;

#if 1 // Baker .. disable fullbrights
	return;
#endif

	if (!drawfullbrights || !gl_fb_bmodels.value)
		return;

	GL_DisableMultitexture ();

	glDepthMask (GL_FALSE);	// don't bother writing Z

	if (gl_fb_depthhack.value)
	{
		float			depthdelta;
		extern cvar_t	gl_ztrick;
		extern int		gl_ztrickframe;

		if (gl_ztrick.value)
			depthdelta = gl_ztrickframe ? - 1.0/16384 : 1.0/16384;
		else
			depthdelta = -1.0/8192;

		// hack depth range to prevent flickering of fullbrights
		glDepthRange (gldepthmin + depthdelta, gldepthmax + depthdelta);
	}

	glEnable (GL_BLEND);
//	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);

	for (i=1 ; i<MAX_GLTEXTURES ; i++) {
		if (!fullbright_polys[i])
			continue;
		GL_Bind (i);
		for (p = fullbright_polys[i]; p; p = p->fb_chain) {
			DrawGLPoly (p);
		}
		fullbright_polys[i] = NULL;
	}


	glDisable (GL_BLEND);
	glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);

	glDepthMask (GL_TRUE);
	if (gl_fb_depthhack.value)
		glDepthRange (gldepthmin, gldepthmax);

	drawfullbrights = false;
}


//=============================================================
// Dynamic lights

typedef struct dlightinfo_s {
	int local[2];
	int rad;
	int minlight;	// rad - minlight
	int type;
} dlightinfo_t;

static dlightinfo_t dlightlist[MAX_DLIGHTS];
static int	numdlights;

/*
===============
R_BuildDlightList
===============
*/
void R_BuildDlightList (msurface_t *surf)
{
	int			lnum;
	float		dist;
	vec3_t		impact;
	int			i;
	int			smax, tmax;
	mtexinfo_t	*tex;
	int			irad, iminlight;
	int			local[2];
	int			tdmin, sdmin, distmin;
	dlightinfo_t	*light;

	numdlights = 0;

	smax = (surf->extents[0]>>4)+1;
	tmax = (surf->extents[1]>>4)+1;
	tex = surf->texinfo;

	for (lnum=0 ; lnum<r_refdef2.numDlights ; lnum++)
	{
		if ( !(surf->dlightbits & (1<<lnum) ) )
			continue;		// not lit by this light

		dist = DotProduct (r_refdef2.dlights[lnum].origin, surf->plane->normal) -
				surf->plane->dist;
		irad = (r_refdef2.dlights[lnum].radius - fabs(dist)) * 256;
		iminlight = r_refdef2.dlights[lnum].minlight * 256;
		if (irad < iminlight)
			continue;

		iminlight = irad - iminlight;

		for (i=0 ; i<3 ; i++) {
			impact[i] = r_refdef2.dlights[lnum].origin[i] -
				surf->plane->normal[i]*dist;
		}

		local[0] = DotProduct (impact, tex->vecs[0]) +
			tex->vecs[0][3] - surf->texturemins[0];
		local[1] = DotProduct (impact, tex->vecs[1]) +
			tex->vecs[1][3] - surf->texturemins[1];

		// check if this dlight will touch the surface
		if (local[1] > 0) {
			tdmin = local[1] - (tmax<<4);
			if (tdmin < 0)
				tdmin = 0;
		} else
			tdmin = -local[1];

		if (local[0] > 0) {
			sdmin = local[0] - (smax<<4);
			if (sdmin < 0)
				sdmin = 0;
		} else
			sdmin = -local[0];

		if (sdmin > tdmin)
			distmin = (sdmin<<8) + (tdmin<<7);
		else
			distmin = (tdmin<<8) + (sdmin<<7);

		if (distmin < iminlight)
		{
			// save dlight info
			light = &dlightlist[numdlights];
			light->minlight = iminlight;
			light->rad = irad;
			light->local[0] = local[0];
			light->local[1] = local[1];
			light->type = r_refdef2.dlights[lnum].type;
			numdlights++;
		}
	}
}

int dlightcolor[NUM_DLIGHTTYPES][3] = {
	{ 100, 90, 80 },	// dimlight or brightlight
	{ 0, 0, 128 },		// blue
	{ 128, 0, 0 },		// red
	{ 128, 0, 128 },	// red + blue
	{ 100, 50, 10 },		// muzzleflash
	{ 100, 50, 10 },		// explosion
	{ 90, 60, 7 }		// rocket
};

/*
===============
R_AddDynamicLights

NOTE: R_BuildDlightList must be called first!
===============
*/
void R_AddDynamicLights (msurface_t *surf)
{
	int			i;
	int			smax, tmax;
	int			s, t;
	int			sd, td;
	int			_sd, _td;
	int			irad, idist, iminlight;
	dlightinfo_t	*light;
	unsigned	*dest;
	int			color[3];
	int			tmp;

	smax = (surf->extents[0]>>4)+1;
	tmax = (surf->extents[1]>>4)+1;

	for (i=0,light=dlightlist ; i<numdlights ; i++,light++)
	{
		if (lightmap_bytes != 1) {
			color[0] = dlightcolor[light->type][0];
			color[1] = dlightcolor[light->type][1];
			color[2] = dlightcolor[light->type][2];
		}

		irad = light->rad;
		iminlight = light->minlight;

		_td = light->local[1];
		dest = blocklights;
		for (t = 0 ; t<tmax ; t++)
		{
			td = _td;
			if (td < 0)	td = -td;
			_td -= 16;
			_sd = light->local[0];
			if (lightmap_bytes == 1) {
				for (s=0 ; s<smax ; s++) {
					sd = _sd < 0 ? -_sd : _sd;
					_sd -= 16;
					if (sd > td)
						idist = (sd<<8) + (td<<7);
					else
						idist = (td<<8) + (sd<<7);
					if (idist < iminlight)
						*dest += irad - idist;
					dest++;
				}
			}
			else {
				for (s=0 ; s<smax ; s++) {
					sd = _sd < 0 ? -_sd : _sd;
					_sd -= 16;
					if (sd > td)
						idist = (sd<<8) + (td<<7);
					else
						idist = (td<<8) + (sd<<7);
					if (idist < iminlight) {
						tmp = (irad - idist) >> 7;
						dest[0] += tmp * color[0];
						dest[1] += tmp * color[1];
						dest[2] += tmp * color[2];
					}
					dest += 3;
				}
			}
		}
	}
}


/*
===============
R_BuildLightMap

Combine and scale multiple lightmaps into the 8.8 format in blocklights
===============
*/
void R_BuildLightMap (msurface_t *surf, byte *dest, int stride)
{
	int			smax, tmax;
	int			t;
	int			i, j, size, blocksize, lightmapsize;
	byte		*lightmap;
	unsigned	scale;
	int			maps;
	unsigned	*bl;

	surf->cached_dlight = !!numdlights;

	smax = (surf->extents[0]>>4)+1;
	tmax = (surf->extents[1]>>4)+1;
	size = smax*tmax;
	blocksize = size * lightmap_bytes;
	lightmapsize = size * 3;	// always three components, even if monochrome
	lightmap = surf->samples;

// set to full bright if no light data
	if ((r_fullbright.value && r_refdef2.allow_cheats) || !r_worldmodel->lightdata) {
		for (i=0 ; i<blocksize ; i++)
			blocklights[i] = 255*256;
		goto store;
	}

// clear to no light
	memset (blocklights, 0, blocksize * sizeof(int));

// add all the lightmaps
	if (lightmap)
		for (maps = 0; maps < MAXLIGHTMAPS && surf->styles[maps] != 255; maps++)
		{
			scale = d_lightstylevalue[surf->styles[maps]];
			surf->cached_light[maps] = scale;	// 8.8 fraction
			bl = blocklights;
			if (lightmap_bytes == 1) {
				for (i = 0; i < size; i++)
					*bl++ += lightmap[i * 3] * scale;
			} else {
				for (i = 0; i < blocksize; i++)
					*bl++ += lightmap[i] * scale;
			}
			lightmap += lightmapsize;	// skip to next lightmap
		}

// add all the dynamic lights
	if (numdlights)
		R_AddDynamicLights (surf);

// bound, invert, and shift
store:
	switch (gl_lightmap_format)
	{
	case GL_RGB:
		bl = blocklights;
		stride -= smax * 3;
		for (i=0 ; i<tmax ; i++, dest += stride)
		{
			if (lightmode == 2)
				for (j=smax; j ; j--) {
					t = bl[0]; t = (t >> 8) + (t >> 9); if (t > 255) t = 255;
					dest[0] = 255-t;
					t = bl[1]; t = (t >> 8) + (t >> 9); if (t > 255) t = 255;
					dest[1] = 255-t;
					t = bl[2]; t = (t >> 8) + (t >> 9); if (t > 255) t = 255;
					dest[2] = 255-t;
					bl+=3;
					dest+=3;
				}
			else
				for (j=smax; j; j--) {
					t = bl[0]; t = t >> 7; if (t > 255) t = 255;
					dest[0] = 255-t;
					t = bl[1]; t = t >> 7; if (t > 255) t = 255;
					dest[1] = 255-t;
					t = bl[2]; t = t >> 7; if (t > 255) t = 255;
					dest[2] = 255-t;
					bl+=3;
					dest+=3;
				}
		}
		break;
	case GL_LUMINANCE:
		bl = blocklights;
		stride -= smax;
		for (i=0 ; i<tmax ; i++, dest += stride)
		{
			if (lightmode == 2)
				for (j=0 ; j<smax ; j++) {
					t = *bl++;
					t = (t >> 8) + (t >> 9);
					if (t > 255)
						t = 255;
					*dest++ = 255-t;
				}
			else
				for (j=0 ; j<smax ; j++) {
					t = *bl++ >> 7;
					if (t > 255)
						t = 255;
					*dest++ = 255-t;
				}
		}
		break;
	default:
		Sys_Error ("Bad lightmap format");
	}
}


/*
================
R_UpdateSurfaceLightMap
================
*/
void R_UpdateSurfaceLightMap (msurface_t *fa)
{
	byte		*base;
	int			maps;
	glRect_t    *theRect;
	int			smax, tmax;
	qbool		lightstyle_modified = false;

	// check for lightmap modification
	for (maps=0 ; maps<MAXLIGHTMAPS && fa->styles[maps] != 255 ; maps++)
		if (d_lightstylevalue[fa->styles[maps]] != fa->cached_light[maps]) {
			lightstyle_modified = true;
			break;
		}

	if (fa->dlightframe == r_framecount)
		R_BuildDlightList (fa);
	else
		numdlights = 0;

	if (numdlights == 0 && !fa->cached_dlight && !lightstyle_modified)
		return;

	lightmap_modified[fa->lightmaptexturenum] = true;
	theRect = &lightmap_rectchange[fa->lightmaptexturenum];
	if (fa->light_t < theRect->t) {
		if (theRect->h)
			theRect->h += theRect->t - fa->light_t;
		theRect->t = fa->light_t;
	}
	if (fa->light_s < theRect->l) {
		if (theRect->w)
			theRect->w += theRect->l - fa->light_s;
		theRect->l = fa->light_s;
	}
	smax = (fa->extents[0]>>4)+1;
	tmax = (fa->extents[1]>>4)+1;
	if ((theRect->w + theRect->l) < (fa->light_s + smax))
		theRect->w = (fa->light_s-theRect->l)+smax;
	if ((theRect->h + theRect->t) < (fa->light_t + tmax))
		theRect->h = (fa->light_t-theRect->t)+tmax;
	base = lightmaps + fa->lightmaptexturenum*lightmap_bytes*BLOCK_WIDTH*BLOCK_HEIGHT;
	base += fa->light_t * BLOCK_WIDTH * lightmap_bytes + fa->light_s * lightmap_bytes;
	R_BuildLightMap (fa, base, BLOCK_WIDTH*lightmap_bytes);
}

/*
===============
R_UploadLightMap
===============
*/
void R_UploadLightMap (int lightmapnum)
{
	glRect_t	*theRect;

	lightmap_modified[lightmapnum] = false;
	theRect = &lightmap_rectchange[lightmapnum];
	glTexSubImage2D (GL_TEXTURE_2D, 0, 0, theRect->t,
		BLOCK_WIDTH, theRect->h, gl_lightmap_format, GL_UNSIGNED_BYTE,
		lightmaps+(lightmapnum*BLOCK_HEIGHT + theRect->t)*BLOCK_WIDTH*lightmap_bytes);
	theRect->l = BLOCK_WIDTH;
	theRect->t = BLOCK_HEIGHT;
	theRect->h = 0;
	theRect->w = 0;
}

/*
===============
R_TextureAnimation

Returns the proper texture for a given time and base texture
===============
*/
texture_t *R_TextureAnimation (texture_t *base)
{
	int		relative;
	int		count;

	if (currententity->frame)
	{
		if (base->alternate_anims)
			base = base->alternate_anims;
	}

	if (!base->anim_total)
		return base;

	relative = (int)(r_refdef2.time*10) % base->anim_total;

	count = 0;
	while (base->anim_min > relative || base->anim_max <= relative)
	{
		base = base->anim_next;
		if (!base)
			Host_Error ("R_TextureAnimation: broken cycle");
		if (++count > 100)
			Host_Error ("R_TextureAnimation: infinite cycle");
	}

	return base;
}

/*
=============================================================

	BRUSH MODELS

=============================================================
*/


extern	float	speedscale;		// for top sky and bottom sky

/*
================
R_DrawSequentialPoly

Systems that have fast state and texture changes can
just do everything as it passes with no need to sort
================
*/
void R_DrawSequentialPoly (msurface_t *s)
{
	glpoly_t	*p;
	float		*v;
	int			i, lnum;
	texture_t	*t;

	if (s->flags & SURF_DRAWSKY)
	{	// This is a bmodel, otherwise it would've been linked into
		// the sky texture chain
		// We don't subdivide sky surfaces, so it is going to look bad
		// if it's large enough... but who's using sky textures in bmodels?
		if (!r_skyboxloaded)
			EmitBothSkyLayers (s);
		else {
			// hmm... no luck
		}
		return;
	}

	//
	// subdivided water surface warp
	//
	if (s->flags & SURF_DRAWTURB)
	{
		GL_DisableMultitexture ();
		GL_Bind (s->texinfo->texture->gl_texturenum);
		EmitWaterPolys (s);
		return;
	}

	//
	// normal lightmapped poly
	//
	R_RenderDynamicLightmaps (s);
	if (gl_mtexable) {
		p = s->polys;

		t = R_TextureAnimation (s->texinfo->texture);
		lnum = s->lightmaptexturenum;

		// Binds world to texture env 0
		GL_SelectTexture (GL_TEXTURE0_ARB);
		GL_Bind (t->gl_texturenum);
		glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);

		// Binds lightmap to texenv 1
		GL_EnableMultitexture (); // Same as SelectTexture (TEXTURE1)
		GL_Bind (lightmap_textures + lnum);

		if (lightmap_modified[lnum])
			R_UploadLightMap (lnum);

		glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND);
		glBegin (GL_POLYGON);
		v = p->verts[0];
		for (i=0 ; i<p->numverts ; i++, v+= VERTEXSIZE)
		{
			qglMultiTexCoord2f (GL_TEXTURE0_ARB, v[3], v[4]);
			qglMultiTexCoord2f (GL_TEXTURE1_ARB, v[5], v[6]);
			glVertex3fv (v);
		}
		glEnd ();
	} else {
		p = s->polys;

		t = R_TextureAnimation (s->texinfo->texture);
		lnum = s->lightmaptexturenum;

		GL_Bind (t->gl_texturenum);
		glBegin (GL_POLYGON);
		v = p->verts[0];
		for (i=0 ; i<p->numverts ; i++, v+= VERTEXSIZE)
		{
			glTexCoord2f (v[3], v[4]);
			glVertex3fv (v);
		}
		glEnd ();

		GL_Bind (lightmap_textures + lnum);

		if (lightmap_modified[lnum])
			R_UploadLightMap (lnum);

		glEnable (GL_BLEND);
		glBlendFunc (GL_ZERO, GL_ONE_MINUS_SRC_COLOR);
		glBegin (GL_POLYGON);
		v = p->verts[0];
		for (i=0 ; i<p->numverts ; i++, v+= VERTEXSIZE)
		{
			glTexCoord2f (v[5], v[6]);
			glVertex3fv (v);
		}
		glEnd ();
		glDisable (GL_BLEND);
		glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	}

	if (t->fb_texturenum) {
		s->polys->fb_chain = fullbright_polys[t->fb_texturenum];
		fullbright_polys[t->fb_texturenum] = s->polys;
		drawfullbrights = true;
	}
}


/*
================
DrawGLPoly
================
*/
void DrawGLPoly (glpoly_t *p)
{
	int		i;
	float	*v;

	glBegin (GL_POLYGON);
	v = p->verts[0];
	for (i=0 ; i<p->numverts ; i++, v+= VERTEXSIZE)
	{
		glTexCoord2f (v[3], v[4]);
		glVertex3fv (v);
	}
	glEnd ();
}


/*
================
R_BlendLightmaps
================
*/
void R_BlendLightmaps (void)
{
	int			i, j;
	glpoly_t	*p;
	float		*v;

	if (!gl_texsort.value)
		return;
	if (r_fullbright.value && r_refdef2.allow_cheats)
		return;

	glDepthMask (GL_FALSE);		// don't bother writing Z
	glBlendFunc (GL_ZERO, GL_ONE_MINUS_SRC_COLOR);

	if (!(r_lightmap.value && r_refdef2.allow_cheats)) {
		glEnable (GL_BLEND);
	}

	for (i=0 ; i<MAX_LIGHTMAPS ; i++)
	{
		p = lightmap_polys[i];
		if (!p)
			continue;
		GL_Bind(lightmap_textures+i);
		if (lightmap_modified[i])
			R_UploadLightMap (i);

		for ( ; p ; p=p->chain)
		{
			glBegin (GL_POLYGON);
			v = p->verts[0];
			for (j=0 ; j<p->numverts ; j++, v+= VERTEXSIZE)
			{
				glTexCoord2f (v[5], v[6]);
				glVertex3fv (v);
			}
			glEnd ();
		}
	}

	glDisable (GL_BLEND);
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glDepthMask (GL_TRUE);		// back to normal Z buffering
}

/*
================
R_RenderBrushPoly
================
*/
void R_RenderBrushPoly (msurface_t *fa)
{
	texture_t	*t;

	c_brush_polys++;

	if (fa->flags & SURF_DRAWSKY)
	{	// This is a bmodel, otherwise it would've been linked into
		// the sky texture chain
		// We don't subdivide sky surfaces, so it is going to look bad
		// if it's large enough... but who's using sky textures in bmodels?
		if (!r_skyboxloaded)
			EmitBothSkyLayers (fa);
		else {
			// hmm... no luck
		}
		return;
	}

	t = R_TextureAnimation (fa->texinfo->texture);
	GL_Bind (t->gl_texturenum);

	if (fa->flags & SURF_DRAWTURB)
	{	// warp texture, no lightmaps
		EmitWaterPolys (fa);
		return;
	}

	DrawGLPoly (fa->polys);

	// add the poly to the proper lightmap chain
	fa->polys->chain = lightmap_polys[fa->lightmaptexturenum];
	lightmap_polys[fa->lightmaptexturenum] = fa->polys;

	if (t->fb_texturenum) {
		fa->polys->fb_chain = fullbright_polys[t->fb_texturenum];
		fullbright_polys[t->fb_texturenum] = fa->polys;
		drawfullbrights = true;
	}

	if (!r_dynamic.value)
		return;

	R_UpdateSurfaceLightMap (fa);
}


/*
================
R_RenderDynamicLightmaps
Multitexture
================
*/
void R_RenderDynamicLightmaps (msurface_t *fa)
{
	c_brush_polys++;

	if (fa->flags & ( SURF_DRAWSKY | SURF_DRAWTURB) )
		return;

	fa->polys->chain = lightmap_polys[fa->lightmaptexturenum];
	lightmap_polys[fa->lightmaptexturenum] = fa->polys;

	if (!r_dynamic.value)
		return;

	R_UpdateSurfaceLightMap (fa);
}


/*
================
R_DrawWaterSurfaces
================
*/
void R_DrawWaterSurfaces (void)
{
	int			i;
	msurface_t	*s;
	texture_t	*t;

	if (wateralpha == 1.0 && gl_texsort.value)
		return;

	if (wateralpha < 1.0) {
		glEnable (GL_BLEND);
		glColor4f (1, 1, 1, wateralpha);
		glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
		if (wateralpha < 0.9)
			glDepthMask (GL_FALSE);
	}

	if (!gl_texsort.value) {
		if (!waterchain)
			return;

		for (s=waterchain ; s ; s=s->texturechain) {
			GL_Bind (s->texinfo->texture->gl_texturenum);
			EmitWaterPolys (s);
		}

		waterchain = NULL;
	} else {

		for (i = 0; i < r_worldmodel->numtextures; i++)
		{
			t = r_worldmodel->textures[i];
			if (!t)
				continue;
			s = t->texturechain;
			if (!s)
				continue;
			if ( !(s->flags & SURF_DRAWTURB ) )
				continue;

			// set modulate mode explicitly

			GL_Bind (t->gl_texturenum);

			for ( ; s ; s=s->texturechain)
				EmitWaterPolys (s);

			t->texturechain = NULL;
		}

	}

	if (wateralpha < 1.0) {
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);

		glColor3f (1, 1, 1);
		glDisable (GL_BLEND);
		if (wateralpha < 0.9)
			glDepthMask (GL_TRUE);
	}
}


/*
================
DrawTextureChains
================
*/
void DrawTextureChains (void)
{
	int		i;
	msurface_t	*s;
	texture_t	*t;

	if (!gl_texsort.value) {
		// render all world textures
		for (s = worldchain; s; s = s->texturechain)
			R_DrawSequentialPoly (s);
		worldchain = NULL;

		GL_DisableMultitexture();	// FIXME, not needed any more?
		return;
	}

	for (i = 0; i < r_worldmodel->numtextures; i++)
	{
		t = r_worldmodel->textures[i];
		if (!t)
			continue;
		s = t->texturechain;
		if (!s)
			continue;
		if ((s->flags & SURF_DRAWTURB) && wateralpha != 1.0)
			continue;	// draw translucent water later

		for ( ; s ; s=s->texturechain)
			R_RenderBrushPoly (s);

		t->texturechain = NULL;
	}
}


/*
=================
R_DrawBrushModel
=================
*/
void R_DrawBrushModel (entity_t *e)
{
	int			i;
	int			k;
	vec3_t		mins, maxs;
	msurface_t	*psurf;
	float		dot;
	mplane_t	*pplane;
	model_t		*clmodel;
	qbool		rotated;

	currententity = e;
	currenttexture = -1;

	clmodel = e->model;

	VectorAdd (e->origin, clmodel->mins, mins);
	VectorAdd (e->origin, clmodel->maxs, maxs);

	if (e->angles[0] || e->angles[1] || e->angles[2])
	{
		vec3_t	center;

		rotated = true;

		VectorAdd (mins, maxs, center);
		VectorScale (center, 0.5, center);

		if (R_CullSphere (center, clmodel->radius))
			return;
	}
	else
	{
		rotated = false;

		if (R_CullBox (mins, maxs))
			return;
	}

	memset (lightmap_polys, 0, sizeof(lightmap_polys));
//	if (gl_fb_bmodels.value)
//		memset (fullbright_polys, 0, sizeof(fullbright_polys));

	VectorSubtract (r_refdef2.vieworg, e->origin, modelorg);
	if (rotated)
	{
		vec3_t	temp;
		vec3_t	forward, right, up;

		VectorCopy (modelorg, temp);
		AngleVectors (e->angles, forward, right, up);
		modelorg[0] = DotProduct (temp, forward);
		modelorg[1] = -DotProduct (temp, right);
		modelorg[2] = DotProduct (temp, up);
	}

	psurf = &clmodel->surfaces[clmodel->firstmodelsurface];

// calculate dynamic lighting for bmodel if it's not an
// instanced model
	if (clmodel->firstmodelsurface != 0 && !gl_flashblend.value)
	{
		for (k = 0; k < r_refdef2.numDlights; k++)
		{
			R_MarkLights (&r_refdef2.dlights[k], 1<<k,
				clmodel->nodes + clmodel->firstnode);
		}
	}

    glPushMatrix ();

	glTranslatef (e->origin[0],  e->origin[1],  e->origin[2]);
	glRotatef (e->angles[1], 0, 0, 1);
	glRotatef (e->angles[0], 0, 1, 0);
	glRotatef (e->angles[2], 1, 0, 0);

	//
	// draw texture
	//
	for (i = 0; i < clmodel->nummodelsurfaces; i++, psurf++)
	{
		// find which side of the node we are on
		pplane = psurf->plane;

		dot = DotProduct (modelorg, pplane->normal) - pplane->dist;

	// draw the polygon
		if (((psurf->flags & SURF_PLANEBACK) && (dot < -BACKFACE_EPSILON)) ||
			(!(psurf->flags & SURF_PLANEBACK) && (dot > BACKFACE_EPSILON)))
		{
			if (gl_texsort.value)
				R_RenderBrushPoly (psurf);
			else
				R_DrawSequentialPoly (psurf);
		}
	}

	R_BlendLightmaps ();

	R_RenderFullbrights ();

	glPopMatrix ();
}

/*
=============================================================

	WORLD MODEL

=============================================================
*/

/*
================
R_RecursiveWorldNode
================
*/
void R_RecursiveWorldNode (mnode_t *node, int clipflags)
{
	int			c, side, sidebit;
	mplane_t	*plane;
	msurface_t	*surf, **mark;
	mleaf_t		*pleaf;
	float		dot;
	int			clipped;
	mplane_t	*clipplane;

	while (1)
	{
		if (node->contents == CONTENTS_SOLID)
			return;		// solid
		if (node->visframe != r_visframecount)
			return;
		for (c=0,clipplane=frustum ; c<4 ; c++,clipplane++)
		{
			if (!(clipflags & (1<<c)))
				continue;	// don't need to clip against it

			clipped = BoxOnPlaneSide (node->minmaxs, node->minmaxs+3, clipplane);
			if (clipped == 2)
				return;
			else if (clipped == 1)
				clipflags &= ~(1<<c);	// node is entirely on screen
		}

		if (node->contents < 0)
			break;

	// node is just a decision point, so go down the apropriate sides

	// find which side of the node we are on
		plane = node->plane;

		if (plane->type < 3)
			dot = modelorg[plane->type] - plane->dist;
		else
			dot = DotProduct (modelorg, plane->normal) - plane->dist;

		if (dot >= 0) {
			side = 0;
			sidebit = 0;
		}
		else {
			side = 1;
			sidebit = SURF_PLANEBACK;
		}

	// recurse down the children, front side first
		R_RecursiveWorldNode (node->children[side], clipflags);

	// draw stuff
		c = node->numsurfaces;

		if (c)
		{
			surf = r_worldmodel->surfaces + node->firstsurface;

			for ( ; c ; c--, surf++)
			{
				if (surf->visframe != r_framecount)
					continue;

				if ((surf->flags & SURF_PLANEBACK) != sidebit)
					continue;		// wrong side

				if (surf->flags & SURF_DRAWSKY) {
					surf->texturechain = skychain;
					skychain = surf;
					continue;
				}

				if (gl_texsort.value) {
					surf->texturechain = surf->texinfo->texture->texturechain;
					surf->texinfo->texture->texturechain = surf;
				} else if (surf->flags & SURF_DRAWTURB) {
					surf->texturechain = waterchain;
					waterchain = surf;
				} else	{
					surf->texturechain = worldchain;
					worldchain = surf;
				}
			}

		}

		// recurse down the back side
		node = node->children[!side];
	}

// if a leaf node, draw stuff
	pleaf = (mleaf_t *)node;

	mark = pleaf->firstmarksurface;
	c = pleaf->nummarksurfaces;

	if (c)
	{
		do
		{
			(*mark)->visframe = r_framecount;
			mark++;
		} while (--c);
	}

// deal with model fragments in this leaf
	if (pleaf->efrags)
		R_StoreEfrags (&pleaf->efrags);
}


/*
=============
R_DrawWorld
=============
*/
void R_DrawWorld (void)
{
	entity_t	ent;

	memset (&ent, 0, sizeof(ent));
	ent.model = r_worldmodel;

	VectorCopy (r_refdef2.vieworg, modelorg);

	currententity = &ent;
	currenttexture = -1;

	glColor3f (1, 1, 1);
	memset (lightmap_polys, 0, sizeof(lightmap_polys));
	if (gl_fb_bmodels.value)
		memset (fullbright_polys, 0, sizeof(fullbright_polys));

	R_RecursiveWorldNode (r_worldmodel->nodes, 15);

	R_DrawSky ();

	DrawTextureChains ();

	R_BlendLightmaps ();

	R_RenderFullbrights ();
}


/*
===============
R_MarkLeaves
===============
*/
void R_MarkLeaves (void)
{
	byte	*vis;
	mnode_t	*node;
	int		i;
	byte	solid[MAX_MAP_LEAFS/8];

	if (!r_novis.value && r_oldviewleaf == r_viewleaf
		&& r_oldviewleaf2 == r_viewleaf2)	// watervis hack
		return;

	r_visframecount++;
	r_oldviewleaf = r_viewleaf;

	if (r_novis.value)
	{
		vis = solid;
		memset (solid, 0xff, (r_worldmodel->numleafs+7)>>3);
	}
	else
	{
		vis = Mod_LeafPVS (r_viewleaf, r_worldmodel);

		if (r_viewleaf2) {
			int			i, count;
			unsigned	*src, *dest;

			// merge visibility data for two leafs
			count = (r_worldmodel->numleafs+7)>>3;
			memcpy (solid, vis, count);
			src = (unsigned *) Mod_LeafPVS (r_viewleaf2, r_worldmodel);
			dest = (unsigned *) solid;
			count = (count + 3)>>2;
			for (i=0 ; i<count ; i++)
				*dest++ |= *src++;
			vis = solid;
		}
	}

	for (i = 0; i < r_worldmodel->numleafs; i++)
	{
		if (vis[i>>3] & (1<<(i&7)))
		{
			node = (mnode_t *) &r_worldmodel->leafs[i+1];
			do
			{
				if (node->visframe == r_visframecount)
					break;
				node->visframe = r_visframecount;
				node = node->parent;
			} while (node);
		}
	}
}



/*
=============================================================================

  LIGHTMAP ALLOCATION

=============================================================================
*/

// returns a texture number and the position inside it
int AllocBlock (int w, int h, int *x, int *y)
{
	int		i, j;
	int		best, best2;
	int		texnum;

	for (texnum=0 ; texnum<MAX_LIGHTMAPS ; texnum++)
	{
		best = BLOCK_HEIGHT;

		for (i=0 ; i<BLOCK_WIDTH-w ; i++)
		{
			best2 = 0;

			for (j=0 ; j<w ; j++)
			{
				if (allocated[texnum][i+j] >= best)
					break;
				if (allocated[texnum][i+j] > best2)
					best2 = allocated[texnum][i+j];
			}
			if (j == w)
			{	// this is a valid spot
				*x = i;
				*y = best = best2;
			}
		}

		if (best + h > BLOCK_HEIGHT)
			continue;

		for (i=0 ; i<w ; i++)
			allocated[texnum][*x + i] = best + h;

		return texnum;
	}

	Sys_Error ("AllocBlock: full");
	return 0;
}


mvertex_t	*r_pcurrentvertbase;
model_t		*currentmodel;

/*
================
BuildSurfaceDisplayList
================
*/
void BuildSurfaceDisplayList (msurface_t *fa)
{
	int			i, lindex, lnumverts;
	medge_t		*pedges, *r_pedge;
	int			vertpage;
	float		*vec;
	float		s, t;
	glpoly_t	*poly;

// reconstruct the polygon
	pedges = currentmodel->edges;
	lnumverts = fa->numedges;
	vertpage = 0;

	//
	// draw texture
	//
	poly = Hunk_Alloc (sizeof(glpoly_t) + (lnumverts-4) * VERTEXSIZE*sizeof(float));
	poly->next = fa->polys;
	fa->polys = poly;
	poly->numverts = lnumverts;

	for (i=0 ; i<lnumverts ; i++)
	{
		lindex = currentmodel->surfedges[fa->firstedge + i];

		if (lindex > 0)
		{
			r_pedge = &pedges[lindex];
			vec = r_pcurrentvertbase[r_pedge->v[0]].position;
		}
		else
		{
			r_pedge = &pedges[-lindex];
			vec = r_pcurrentvertbase[r_pedge->v[1]].position;
		}
		s = DotProduct (vec, fa->texinfo->vecs[0]) + fa->texinfo->vecs[0][3];
		s /= fa->texinfo->texture->width;

		t = DotProduct (vec, fa->texinfo->vecs[1]) + fa->texinfo->vecs[1][3];
		t /= fa->texinfo->texture->height;

		VectorCopy (vec, poly->verts[i]);
		poly->verts[i][3] = s;
		poly->verts[i][4] = t;

		//
		// lightmap texture coordinates
		//
		s = DotProduct (vec, fa->texinfo->vecs[0]) + fa->texinfo->vecs[0][3];
		s -= fa->texturemins[0];
		s += fa->light_s*16;
		s += 8;
		s /= BLOCK_WIDTH*16; //fa->texinfo->texture->width;

		t = DotProduct (vec, fa->texinfo->vecs[1]) + fa->texinfo->vecs[1][3];
		t -= fa->texturemins[1];
		t += fa->light_t*16;
		t += 8;
		t /= BLOCK_HEIGHT*16; //fa->texinfo->texture->height;

		poly->verts[i][5] = s;
		poly->verts[i][6] = t;
	}

	poly->numverts = lnumverts;
}

/*
========================
GL_CreateSurfaceLightmap
========================
*/
void GL_CreateSurfaceLightmap (msurface_t *surf)
{
	int		smax, tmax;
	byte	*base;

	if (surf->flags & (SURF_DRAWSKY|SURF_DRAWTURB))
		return;

	smax = (surf->extents[0]>>4)+1;
	tmax = (surf->extents[1]>>4)+1;

	if (smax > BLOCK_WIDTH)
		Host_Error("GL_CreateSurfaceLightmap: smax = %i > BLOCK_WIDTH", smax);
	if (tmax > BLOCK_HEIGHT)
		Host_Error("GL_CreateSurfaceLightmap: tmax = %i > BLOCK_HEIGHT", tmax);
	if (smax * tmax > MAX_LIGHTMAP_SIZE)
		Host_Error("GL_CreateSurfaceLightmap: smax * tmax = %i > MAX_LIGHTMAP_SIZE", smax * tmax);

	surf->lightmaptexturenum = AllocBlock (smax, tmax, &surf->light_s, &surf->light_t);
	base = lightmaps + surf->lightmaptexturenum*lightmap_bytes*BLOCK_WIDTH*BLOCK_HEIGHT;
	base += (surf->light_t * BLOCK_WIDTH + surf->light_s) * lightmap_bytes;
	numdlights = 0;
	R_BuildLightMap (surf, base, BLOCK_WIDTH*lightmap_bytes);
}


/*
==================
GL_BuildLightmaps

Builds the lightmap texture
with all the surfaces from all brush models
==================
*/
void GL_BuildLightmaps (void)
{
	int		i, j;
	model_t	*m;

	memset (allocated, 0, sizeof(allocated));

	r_framecount = 1;		// no dlightcache

	if (gl_colorlights.value) {
		gl_lightmap_format = GL_RGB;
		lightmap_bytes = 3;
	} else {
		gl_lightmap_format = GL_LUMINANCE;
		lightmap_bytes = 1;
	}

	for (j=1 ; j<MAX_MODELS ; j++)
	{
		m = cl.model_precache[j];
		if (!m)
			break;
		if (m->name[0] == '*')
			continue;
		r_pcurrentvertbase = m->vertexes;
		currentmodel = m;
		for (i=0 ; i<m->numsurfaces ; i++)
		{
			GL_CreateSurfaceLightmap (m->surfaces + i);
			if ( m->surfaces[i].flags & (SURF_UNLIT) )
				continue;
			BuildSurfaceDisplayList (m->surfaces + i);
		}
	}

 	if (!gl_texsort.value)
 		GL_SelectTexture(GL_TEXTURE1_ARB);

	//
	// upload all lightmaps that were filled
	//
	for (i=0 ; i<MAX_LIGHTMAPS ; i++)
	{
		if (!allocated[i][0])
			break;		// no more used
		lightmap_modified[i] = false;
		lightmap_rectchange[i].l = BLOCK_WIDTH;
		lightmap_rectchange[i].t = BLOCK_HEIGHT;
		lightmap_rectchange[i].w = 0;
		lightmap_rectchange[i].h = 0;
		GL_Bind(lightmap_textures + i);
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
		glTexImage2D (GL_TEXTURE_2D, 0, lightmap_bytes
		, BLOCK_WIDTH, BLOCK_HEIGHT, 0,
		gl_lightmap_format, GL_UNSIGNED_BYTE, lightmaps+i*BLOCK_WIDTH*BLOCK_HEIGHT*lightmap_bytes);
	}

	if (!gl_texsort.value)
 		GL_SelectTexture(GL_TEXTURE0_ARB);
}
