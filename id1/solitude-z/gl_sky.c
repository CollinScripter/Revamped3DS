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
// gl_sky.c

#include "gl_local.h"
#include "rc_image.h"

extern	model_t	*loadmodel;

float	speedscale;		// for top sky and bottom sky
qbool	r_skyboxloaded;

/*
================
GL_BuildSkySurfacePoly

Just build the gl polys, don't subdivide

FIXME move to gl_model.c?
================
*/
void GL_BuildSkySurfacePolys (msurface_t *fa)
{
	vec3_t		verts[64];
	int			numverts;
	int			i;
	int			lindex;
	float		*vec;
	glpoly_t	*poly;
	float		*vert;

	//
	// convert edges back to a normal polygon
	//
	numverts = 0;
	for (i=0 ; i<fa->numedges ; i++)
	{
		lindex = loadmodel->surfedges[fa->firstedge + i];

		if (lindex > 0)
			vec = loadmodel->vertexes[loadmodel->edges[lindex].v[0]].position;
		else
			vec = loadmodel->vertexes[loadmodel->edges[-lindex].v[1]].position;
		VectorCopy (vec, verts[numverts]);
		numverts++;
	}

	poly = Hunk_Alloc (sizeof(glpoly_t) + (numverts-4) * VERTEXSIZE*sizeof(float));
	poly->next = NULL;
	fa->polys = poly;
	poly->numverts = numverts;
	vert = verts[0];
	for (i=0 ; i<numverts ; i++, vert+= 3)
		VectorCopy (vert, poly->verts[i]);
}


/*
=============
EmitSkyPolys
=============
*/
static void EmitSkyPolys (msurface_t *fa)
{
	glpoly_t	*p;
	float		*v;
	int			i;
	float	s, t;
	vec3_t	dir;
	float	length;

	for (p=fa->polys ; p ; p=p->next)
	{
		glBegin (GL_POLYGON);
		for (i=0,v=p->verts[0] ; i<p->numverts ; i++, v+=VERTEXSIZE)
		{
			VectorSubtract (v, r_origin, dir);
			dir[2] *= 3;	// flatten the sphere

			length = VectorLength (dir);
			length = 6*63/length;

			dir[0] *= length;
			dir[1] *= length;

			s = (speedscale + dir[0]) * (1.0/128);
			t = (speedscale + dir[1]) * (1.0/128);

			glTexCoord2f (s, t);
			glVertex3fv (v);
		}
		glEnd ();
	}
}

/*
=============
EmitFlatPoly
=============
*/
void EmitFlatPoly (msurface_t *fa)
{
	glpoly_t	*p;
	float		*v;
	int			i;

	for (p=fa->polys ; p ; p=p->next)
	{
		glBegin (GL_POLYGON);
		for (i=0,v=p->verts[0] ; i<p->numverts ; i++, v+=VERTEXSIZE)
			glVertex3fv (v);
		glEnd ();
	}
}

/*
===============
EmitBothSkyLayers

Does a sky warp on the pre-fragmented glpoly_t chain
This will be called for brushmodels, the world
will have them chained together.
===============
*/
void EmitBothSkyLayers (msurface_t *fa)
{
	GL_DisableMultitexture();

	if (r_fastsky.value) {
		glDisable (GL_TEXTURE_2D);
		glColor3ubv ((byte *)&d_8to24table[(byte)r_skycolor.value]);

		EmitFlatPoly (fa);

		glEnable (GL_TEXTURE_2D);
		glColor3f (1, 1, 1);
		return;
	}

	GL_Bind (solidskytexture);
	speedscale = r_refdef2.time*8;
	speedscale -= (int)speedscale & ~127;

	EmitSkyPolys (fa);

	glEnable (GL_BLEND);
	GL_Bind (alphaskytexture);
	speedscale = r_refdef2.time*16;
	speedscale -= (int)speedscale & ~127;

	EmitSkyPolys (fa);

	glDisable (GL_BLEND);
}

//===============================================================

/*
=============
R_InitSky

A sky texture is 256*128, with the right side being a masked overlay
==============
*/
void R_InitSky (texture_t *mt)
{
	int			i, j, p;
	byte		*src;
	unsigned	trans[128*128];
	unsigned	transpix;
	int			r, g, b;
	unsigned	*rgba;

	src = (byte *)mt + mt->offsets[0];

	// make an average value for the back to avoid
	// a fringe on the top level

	r = g = b = 0;
	for (i=0 ; i<128 ; i++)
		for (j=0 ; j<128 ; j++)
		{
			p = src[i*256 + j + 128];
			rgba = &d_8to24table[p];
			trans[(i*128) + j] = *rgba;
			r += ((byte *)rgba)[0];
			g += ((byte *)rgba)[1];
			b += ((byte *)rgba)[2];
		}

	((byte *)&transpix)[0] = r/(128*128);
	((byte *)&transpix)[1] = g/(128*128);
	((byte *)&transpix)[2] = b/(128*128);
	((byte *)&transpix)[3] = 0;

	GL_Bind (solidskytexture);
	glTexImage2D (GL_TEXTURE_2D, 0, gl_solid_format, 128, 128, 0, GL_RGBA, GL_UNSIGNED_BYTE, trans);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);


	for (i=0 ; i<128 ; i++)
		for (j=0 ; j<128 ; j++)
		{
			p = src[i*256 + j];
			if (p == 0)
				trans[(i*128) + j] = transpix;
			else
				trans[(i*128) + j] = d_8to24table[p];
		}

	GL_Bind(alphaskytexture);
	glTexImage2D (GL_TEXTURE_2D, 0, gl_alpha_format, 128, 128, 0, GL_RGBA, GL_UNSIGNED_BYTE, trans);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
}


/*
=================================================================

  Quake 2 environment sky

=================================================================
*/


/*
==================
R_SetSky
==================
*/
static char	*suf[6] = {"rt", "bk", "lf", "ft", "up", "dn"};
void R_SetSky (char *name)
{
	int		i;
	byte	*pic;
	int		width, height;
	char	pathname[MAX_OSPATH];

	if (!name[0]) {
		// disable skybox
		r_skyboxloaded = false;
		return;
	}

	for (i=0 ; i<6 ; i++)
	{
		snprintf (pathname, sizeof(pathname), "env/%s%s.tga", name, suf[i]);
		LoadTGA (pathname, &pic, &width, &height);
		if (!pic)
		{
			Com_Printf ("Couldn't load %s\n", pathname);
			r_skyboxloaded = false;
			return;
		}
		if (width > 512 || height > 512)	// just a sanity check
		{
			Com_Printf ("Bad image dimensions in %s\n", pathname);
			Q_free (pic);	// Q_malloc'ed by LoadTGA
			r_skyboxloaded = false;
			return;
		}

		// FIXME, scale image down if larger than gl_max_size
		// We're gonna run into trouble on a Voodoo

		GL_Bind (skyboxtextures + i);
		glTexImage2D (GL_TEXTURE_2D, 0, gl_solid_format, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pic);
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

		Q_free (pic);	// Q_malloc'ed by LoadTGA
	}

	r_skyboxloaded = true;
}


static vec3_t	skyclip[6] = {
	{1,1,0},
	{1,-1,0},
	{0,-1,1},
	{0,1,1},
	{1,0,1},
	{-1,0,1} 
};

// 1 = s, 2 = t, 3 = 2048
static int	st_to_vec[6][3] =
{
	{3,-1,2},
	{-3,1,2},

	{1,3,2},
	{-1,-3,2},

	{-2,-1,3},		// 0 degrees yaw, look straight up
	{2,-1,-3}		// look straight down

//	{-1,2,3},
//	{1,2,-3}
};

// s = [0]/[2], t = [1]/[2]
static int	vec_to_st[6][3] =
{
	{-2,3,1},
	{2,3,-1},

	{1,3,2},
	{-1,3,-2},

	{-2,-1,3},
	{-2,1,-3}

//	{-1,2,3},
//	{1,2,-3}
};

static float	skymins[2][6], skymaxs[2][6];

static void DrawSkyPolygon (int nump, vec3_t vecs)
{
	int		i,j;
	vec3_t	v, av;
	float	s, t, dv;
	int		axis;
	float	*vp;

	// decide which face it maps to
	VectorClear (v);
	for (i=0, vp=vecs ; i<nump ; i++, vp+=3)
	{
		VectorAdd (vp, v, v);
	}
	av[0] = fabs(v[0]);
	av[1] = fabs(v[1]);
	av[2] = fabs(v[2]);
	if (av[0] > av[1] && av[0] > av[2])
	{
		if (v[0] < 0)
			axis = 1;
		else
			axis = 0;
	}
	else if (av[1] > av[2] && av[1] > av[0])
	{
		if (v[1] < 0)
			axis = 3;
		else
			axis = 2;
	}
	else
	{
		if (v[2] < 0)
			axis = 5;
		else
			axis = 4;
	}

	// project new texture coords
	for (i=0 ; i<nump ; i++, vecs+=3)
	{
		j = vec_to_st[axis][2];
		if (j > 0)
			dv = vecs[j - 1];
		else
			dv = -vecs[-j - 1];

		j = vec_to_st[axis][0];
		if (j < 0)
			s = -vecs[-j -1] / dv;
		else
			s = vecs[j-1] / dv;
		j = vec_to_st[axis][1];
		if (j < 0)
			t = -vecs[-j -1] / dv;
		else
			t = vecs[j-1] / dv;

		if (s < skymins[0][axis])
			skymins[0][axis] = s;
		if (t < skymins[1][axis])
			skymins[1][axis] = t;
		if (s > skymaxs[0][axis])
			skymaxs[0][axis] = s;
		if (t > skymaxs[1][axis])
			skymaxs[1][axis] = t;
	}
}

#define	MAX_CLIP_VERTS	64
static void ClipSkyPolygon (int nump, vec3_t vecs, int stage)
{
	float	*norm;
	float	*v;
	qbool	front, back;
	float	d, e;
	float	dists[MAX_CLIP_VERTS];
	int		sides[MAX_CLIP_VERTS];
	vec3_t	newv[2][MAX_CLIP_VERTS];
	int		newc[2];
	int		i, j;

	if (nump > MAX_CLIP_VERTS-2)
		Sys_Error ("ClipSkyPolygon: MAX_CLIP_VERTS");
	if (stage == 6)
	{	// fully clipped, so draw it
		DrawSkyPolygon (nump, vecs);
		return;
	}

	front = back = false;
	norm = skyclip[stage];
	for (i=0, v = vecs ; i<nump ; i++, v+=3)
	{
		d = DotProduct (v, norm);
		if (d > ON_EPSILON)
		{
			front = true;
			sides[i] = SIDE_FRONT;
		}
		else if (d < ON_EPSILON)
		{
			back = true;
			sides[i] = SIDE_BACK;
		}
		else
			sides[i] = SIDE_ON;
		dists[i] = d;
	}

	if (!front || !back)
	{	// not clipped
		ClipSkyPolygon (nump, vecs, stage+1);
		return;
	}

	// clip it
	sides[i] = sides[0];
	dists[i] = dists[0];
	VectorCopy (vecs, (vecs+(i*3)) );
	newc[0] = newc[1] = 0;

	for (i=0, v = vecs ; i<nump ; i++, v+=3)
	{
		switch (sides[i])
		{
		case SIDE_FRONT:
			VectorCopy (v, newv[0][newc[0]]);
			newc[0]++;
			break;
		case SIDE_BACK:
			VectorCopy (v, newv[1][newc[1]]);
			newc[1]++;
			break;
		case SIDE_ON:
			VectorCopy (v, newv[0][newc[0]]);
			newc[0]++;
			VectorCopy (v, newv[1][newc[1]]);
			newc[1]++;
			break;
		}

		if (sides[i] == SIDE_ON || sides[i+1] == SIDE_ON || sides[i+1] == sides[i])
			continue;

		d = dists[i] / (dists[i] - dists[i+1]);
		for (j=0 ; j<3 ; j++)
		{
			e = v[j] + d*(v[j+3] - v[j]);
			newv[0][newc[0]][j] = e;
			newv[1][newc[1]][j] = e;
		}
		newc[0]++;
		newc[1]++;
	}

	// continue
	ClipSkyPolygon (newc[0], newv[0][0], stage+1);
	ClipSkyPolygon (newc[1], newv[1][0], stage+1);
}

static void AddSkyBoxSurface (msurface_t *fa)
{
	int		i;
	vec3_t	verts[MAX_CLIP_VERTS];
	glpoly_t	*p;

	// calculate vertex values for sky box
	for (p=fa->polys ; p ; p=p->next)
	{
		for (i=0 ; i<p->numverts ; i++)
		{
			VectorSubtract (p->verts[i], r_origin, verts[i]);
		}
		ClipSkyPolygon (p->numverts, verts[0], 0);
	}
}


static void ClearSky (void)
{
	int		i;

	for (i=0 ; i<6 ; i++)
	{
		skymins[0][i] = skymins[1][i] = 9999;
		skymaxs[0][i] = skymaxs[1][i] = -9999;
	}
}

static void MakeSkyVec (float s, float t, int axis)
{
	vec3_t      v, b;
	int         j, k;
	float		skybox_range;

	skybox_range = max(r_farclip.value, 4096) * 0.577; // 0.577 < 1/sqrt(3)
	b[0] = s*skybox_range;
	b[1] = t*skybox_range;
	b[2] = skybox_range;

	for (j=0 ; j<3 ; j++)
	{
		k = st_to_vec[axis][j];
		if (k < 0)
			v[j] = -b[-k - 1];
		else
			v[j] = b[k - 1];
		v[j] += r_origin[j];
	}

	// avoid bilerp seam
	s = (s+1)*0.5;
	t = (t+1)*0.5;

	if (s < 1.0/512)
		s = 1.0/512;
	else if (s > 511.0/512)
		s = 511.0/512;
	if (t < 1.0/512)
		t = 1.0/512;
	else if (t > 511.0/512)
		t = 511.0/512;

	t = 1.0 - t;
	glTexCoord2f (s, t);
	glVertex3fv (v);
}

/*
==============
R_DrawSkyBox
==============
*/
static int	skytexorder[6] = {0,2,1,3,4,5};
static void R_DrawSkyBox (void)
{
	int		i;

	for (i = 0; i < 6; i++)
	{
		if ((skymins[0][i] >= skymaxs[0][i]	|| skymins[1][i] >= skymaxs[1][i]))
			continue;

		GL_Bind (skyboxtextures + skytexorder[i]);

		glBegin (GL_QUADS);
		MakeSkyVec (skymins[0][i], skymins[1][i], i);
		MakeSkyVec (skymins[0][i], skymaxs[1][i], i);
		MakeSkyVec (skymaxs[0][i], skymaxs[1][i], i);
		MakeSkyVec (skymaxs[0][i], skymins[1][i], i);
		glEnd ();
	}
}

static void EmitSkyVert (vec3_t v)
{
	vec3_t dir;
	float	s, t;
	float	length;

	VectorSubtract (v, r_origin, dir);
	dir[2] *= 3;	// flatten the sphere

	length = VectorLength (dir);
	length = 6*63/length;

	dir[0] *= length;
	dir[1] *= length;

	s = (speedscale + dir[0]) * (1.0/128);
	t = (speedscale + dir[1]) * (1.0/128);

	glTexCoord2f (s, t);
	glVertex3fv (v);
}

// s and t range from -1 to 1
static void MakeSkyVec2 (float s, float t, int axis, vec3_t v)
{
	vec3_t		b;
	int			j, k;
	float		skybox_range;

	skybox_range = max(r_farclip.value, 4096) * 0.577; // 0.577 < 1/sqrt(3)
	b[0] = s*skybox_range;
	b[1] = t*skybox_range;
	b[2] = skybox_range;

	for (j=0 ; j<3 ; j++)
	{
		k = st_to_vec[axis][j];
		if (k < 0)
			v[j] = -b[-k - 1];
		else
			v[j] = b[k - 1];
		v[j] += r_origin[j];
	}

}

#define SUBDIVISIONS	10

static void DrawSkyFace (int axis)
{
	int i, j;
	vec3_t	vecs[4];
	float s, t;

	float fstep = 2.0 / SUBDIVISIONS;

	glBegin (GL_QUADS);

	for (i = 0; i < SUBDIVISIONS; i++)
	{
		s = (float)(i*2 - SUBDIVISIONS) / SUBDIVISIONS;

		if (s + fstep < skymins[0][axis] || s > skymaxs[0][axis])
			continue;

		for (j = 0; j < SUBDIVISIONS; j++) {
			t = (float)(j*2 - SUBDIVISIONS) / SUBDIVISIONS;

			if (t + fstep < skymins[1][axis] || t > skymaxs[1][axis])
				continue;

			MakeSkyVec2 (s, t, axis, vecs[0]);
			MakeSkyVec2 (s, t + fstep, axis, vecs[1]);
			MakeSkyVec2 (s + fstep, t + fstep, axis, vecs[2]);
			MakeSkyVec2 (s + fstep, t, axis, vecs[3]);

			EmitSkyVert (vecs[0]);
			EmitSkyVert (vecs[1]);
			EmitSkyVert (vecs[2]);
			EmitSkyVert (vecs[3]);
		}
	}

	glEnd ();
}


static void R_DrawSkyDome (void)
{
	int i;

	GL_DisableMultitexture();
	GL_Bind (solidskytexture);

	speedscale = r_refdef2.time*8;
	speedscale -= (int)speedscale & ~127;

	for (i = 0; i < 6; i++) {
		if ((skymins[0][i] >= skymaxs[0][i]	|| skymins[1][i] >= skymaxs[1][i]))
			continue;
		DrawSkyFace (i);
	}

	glEnable (GL_BLEND);
	GL_Bind (alphaskytexture);

	speedscale = r_refdef2.time*16;
	speedscale -= (int)speedscale & ~127;

	for (i = 0; i < 6; i++) {
		if ((skymins[0][i] >= skymaxs[0][i]	|| skymins[1][i] >= skymaxs[1][i]))
			continue;
		DrawSkyFace (i);
	}
}

/*
==============
R_DrawSky

Draw either the classic cloudy quake sky or a skybox
==============
*/
void R_DrawSky (void)
{
	msurface_t	*fa;
	qbool		ignore_z;
	extern msurface_t *skychain;

	GL_DisableMultitexture ();

	if (r_fastsky.value) {
		glDisable (GL_TEXTURE_2D);
		glColor3ubv ((byte *)&d_8to24table[(byte)r_skycolor.value]);
		
		for (fa = skychain; fa; fa = fa->texturechain)
			EmitFlatPoly (fa);
		skychain = NULL;

		glEnable (GL_TEXTURE_2D);
		glColor3f (1, 1, 1);
		return;
	}

	if (r_viewleaf->contents == CONTENTS_SOLID) {
		// always draw if we're in a solid leaf (probably outside the level)
		// FIXME: we don't really want to add all six planes every time!
		// FIXME: also handle r_fastsky case
		int i;
		for (i = 0; i < 6; i++) {
			skymins[0][i] = skymins[1][i] = -1;
			skymaxs[0][i] = skymaxs[1][i] = 1;
		}
		ignore_z = true;
	}
	else {
		if (!skychain)
			return;		// no sky at all

		// figure out how much of the sky box we need to draw
		ClearSky ();
		for (fa = skychain; fa; fa = fa->texturechain)
			AddSkyBoxSurface (fa);

		ignore_z = false;
	}

	// turn off Z tests & writes to avoid problems on large maps
	glDisable (GL_DEPTH_TEST);

	// draw a skybox or classic quake clouds
	if (r_skyboxloaded)
		R_DrawSkyBox ();
	else
		R_DrawSkyDome ();

	glEnable (GL_DEPTH_TEST);

	// draw the sky polys into the Z buffer
	// don't need depth test yet
	if (!ignore_z) {
		glDisable(GL_TEXTURE_2D);
		glColorMask (GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE);

		glEnable(GL_BLEND);
		glBlendFunc(GL_ZERO, GL_ONE);

		for (fa = skychain; fa; fa = fa->texturechain)
			EmitFlatPoly (fa);

		glEnable (GL_TEXTURE_2D);
		glColorMask (GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
		glDisable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	}

	skychain = NULL;
}

/*

This works better (with gl_ztrick 0) on aerowalk where otherwise the sky
shows in bright pixels through holes in walls, of which on aerowalk there
are plenty.
But problems arise on large maps like q1dm17 where the sky tends
to hide parts of the level.
We could just put the far clip plane further of course...

void R_DrawSky (void)
{
	msurface_t	*fa;
	qbool		ignore_z;
	extern cvar_t	gl_ztrick;
	extern int		gl_ztrickframe;
	extern msurface_t *skychain;

	GL_DisableMultitexture ();

	if (r_fastsky.value) {
		glDisable (GL_TEXTURE_2D);
		glColor3ubv ((byte *)&d_8to24table[(byte)r_skycolor.value]);
		
		for (fa = skychain; fa; fa = fa->texturechain)
			EmitFlatPoly (fa);
		skychain = NULL;

		glEnable (GL_TEXTURE_2D);
		glColor3f (1, 1, 1);
		return;
	}

	if (r_viewleaf->contents == CONTENTS_SOLID) {
		// always draw if we're in a solid leaf (probably outside the level)
		// FIXME: we don't really want to add all six planes every time!
		int i;
		for (i = 0; i < 6; i++) {
			skymins[0][i] = skymins[1][i] = -1;
			skymaxs[0][i] = skymaxs[1][i] = 1;
		}
		ignore_z = true;
	}
	else {
		if (!skychain)
			return;		// no sky at all

		// figure out how much of the sky box we need to draw
		ClearSky ();
		for (fa = skychain; fa; fa = fa->texturechain)
			AddSkyBoxSurface (fa);

		ignore_z = false;
	}

	// draw the sky polys into the Z buffer
	if (!ignore_z) {
		glDisable(GL_TEXTURE_2D);
		glColorMask (GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE);

		glEnable(GL_BLEND);
		glBlendFunc(GL_ZERO, GL_ONE);

		for (fa = skychain; fa; fa = fa->texturechain)
			EmitFlatPoly (fa);

		glEnable (GL_TEXTURE_2D);
		glColorMask (GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
		glDisable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	}

	if (!ignore_z) {
		// only write portions of the sky behind the Z polygons we rendered
		if (gl_ztrick.value && !gl_ztrickframe)
			glDepthFunc (GL_LEQUAL);
		else
			glDepthFunc (GL_GEQUAL);

		glDepthMask (GL_FALSE);	// don't bother writing Z
	}

	// draw a skybox or classic quake clouds
	if (r_skyboxloaded)
		R_DrawSkyBox ();
	else
		R_DrawSkyDome ();

	if (!ignore_z) {
		// back to normal Z test
		if (gl_ztrick.value && !gl_ztrickframe)
			glDepthFunc (GL_GEQUAL);
		else
			glDepthFunc (GL_LEQUAL);

		glDepthMask (GL_TRUE);	// re-enable Z writes
	}

	skychain = NULL;
}
*/
