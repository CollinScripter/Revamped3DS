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
// r_light.c

#include "gl_local.h"

int	r_dlightframecount;


/*
==================
R_AnimateLight
==================
*/
void R_AnimateLight (void)
{
	int			i,j,l1,l2;
	float		lerpfrac;
	
//
// light animations
// 'm' is normal light, 'a' is no light, 'z' is double bright
	i = (int)(r_refdef2.time*10);
	lerpfrac = r_refdef2.time*10 - (int)(r_refdef2.time*10);
	for (j = 0; j < MAX_LIGHTSTYLES; j++)
	{
		if (!r_refdef2.lightstyles[j].length)
		{
			d_lightstylevalue[j] = 256;
			continue;
		}

		l1 = i % r_refdef2.lightstyles[j].length;
		l1 = (r_refdef2.lightstyles[j].map[l1] - 'a') * 22;
		l2 = (i + 1) % r_refdef2.lightstyles[j].length;
		l2 = (r_refdef2.lightstyles[j].map[l2] - 'a') * 22;

		if (l1 - l2 > 220 || l2 - l1 > 220)
			d_lightstylevalue[j] = l2;
		else
			d_lightstylevalue[j] = l1 + (l2 - l1) * lerpfrac;
	}	
}


/*
=============================================================================

DYNAMIC LIGHTS BLEND RENDERING

=============================================================================
*/

float bubble_sintable[17], bubble_costable[17];

void R_InitBubble(void) {
	float a;
	int i;
	float *bub_sin, *bub_cos;

	bub_sin = bubble_sintable;
	bub_cos = bubble_costable;

	for (i=16 ; i>=0 ; i--)
	{
		a = i/16.0 * M_PI*2;
		*bub_sin++ = sin(a);
		*bub_cos++ = cos(a);
	}
}


float bubblecolor[NUM_DLIGHTTYPES][4] = {
	{ 0.2, 0.1, 0.05 },		// dimlight or brightlight
	{ 0.05, 0.05, 0.3 },	// blue
	{ 0.5, 0.05, 0.05 },	// red
	{ 0.5, 0.05, 0.4 },		// red + blue
	{ 0.2, 0.1, 0.05 },		// muzzleflash
	{ 0.2, 0.1, 0.05 },		// explosion
	{ 0, 0, 0 }				// rocket (no light bubble)
};

void R_RenderDlight (dlight_t *light)
{
	int		i, j;
	vec3_t	v;
	vec3_t	v_right, v_up;
	float	length;
	float	rad;
	float	*bub_sin, *bub_cos;

	// don't draw our own powerup glow and muzzleflashes
	if (light->key == (r_refdef2.viewplayernum + 1) ||
		light->key == -(r_refdef2.viewplayernum + 1)) // muzzleflash keys are negative
		return;

	rad = light->radius * 0.35;
	VectorSubtract (light->origin, r_origin, v);
	length = VectorNormalize (v);

	if (length < rad) {
		// view is inside the dlight
		return;
	}

	glBegin (GL_TRIANGLE_FAN);
	glColor3fv (bubblecolor[light->type]);

	v_right[0] = v[1];
	v_right[1] = -v[0];
	v_right[2] = 0;
	VectorNormalize (v_right);
	CrossProduct (v_right, v, v_up);

	if (length - rad > 8)
		VectorScale (v, rad, v);
	else {
		// make sure the light bubble will not be clipped by
		// near z clip plane
		VectorScale (v, length-8, v);
	}
	VectorSubtract (light->origin, v, v);

	glVertex3fv (v);
	glColor3f (0, 0, 0);

	bub_sin = bubble_sintable;
	bub_cos = bubble_costable;

	for (i=16; i>=0; i--)
	{
		for (j = 0; j < 3; j++)
			v[j] = light->origin[j] + (v_right[j]*(*bub_cos) +
				+ v_up[j]*(*bub_sin)) * rad;
		bub_sin++; 
		bub_cos++;
		glVertex3fv (v);
	}

	glEnd ();
}

/*
=============
R_RenderDlights
=============
*/
void R_RenderDlights (void)
{
	int		i;
	dlight_t	*l;

	if (!gl_flashblend.value)
		return;

	r_dlightframecount = r_framecount + 1;	// because the count hasn't
											//  advanced yet for this frame
	glDepthMask (GL_FALSE);
	glDisable (GL_TEXTURE_2D);
	glShadeModel (GL_SMOOTH);
	glEnable (GL_BLEND);
	glBlendFunc (GL_ONE, GL_ONE);

	l = r_refdef2.dlights;
	for (i = 0; i < r_refdef2.numDlights; i++, l++)
	{
		if (l->type == lt_rocket)
			continue;
		R_RenderDlight (l);
	}

	glColor3f (1, 1, 1);
	glDisable (GL_BLEND);
	glEnable (GL_TEXTURE_2D);
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glDepthMask (GL_TRUE);
}


/*
=============================================================================

DYNAMIC LIGHTS

=============================================================================
*/

/*
=============
R_MarkLights
=============
*/
void R_MarkLights (dlight_t *light, int bit, mnode_t *node)
{
	mplane_t	*splitplane;
	float		dist;
	msurface_t	*surf;
	int			i;
	
	if (node->contents < 0)
		return;

	splitplane = node->plane;
	dist = DotProduct (light->origin, splitplane->normal) - splitplane->dist;
	
	if (dist > light->radius)
	{
		R_MarkLights (light, bit, node->children[0]);
		return;
	}
	if (dist < -light->radius)
	{
		R_MarkLights (light, bit, node->children[1]);
		return;
	}
		
// mark the polygons
	surf = r_worldmodel->surfaces + node->firstsurface;
	for (i=0 ; i<node->numsurfaces ; i++, surf++)
	{
		if (surf->dlightframe != r_dlightframecount)
		{
			surf->dlightbits = 0;
			surf->dlightframe = r_dlightframecount;
		}
		surf->dlightbits |= bit;
	}

	R_MarkLights (light, bit, node->children[0]);
	R_MarkLights (light, bit, node->children[1]);
}


/*
=============
R_PushDlights
=============
*/
void R_PushDlights (void)
{
	int		i;
	dlight_t	*l;

	if (gl_flashblend.value)
		return;

	r_dlightframecount = r_framecount + 1;	// because the count hasn't
											//  advanced yet for this frame
	l = r_refdef2.dlights;

	for (i=0 ; i<r_refdef2.numDlights ; i++, l++)
	{
		R_MarkLights ( l, 1<<i, r_worldmodel->nodes );
	}
}


/*
=============================================================================

LIGHT SAMPLING

=============================================================================
*/

mplane_t		*lightplane;
vec3_t			lightspot;
static int		lightcolor[3];

int RecursiveLightPoint (mnode_t *node, vec3_t start, vec3_t end)
{
	int			r;
	float		front, back, frac;
	int			side;
	mplane_t	*plane;
	vec3_t		mid;
	msurface_t	*surf;
	int			s, t, ds, dt;
	int			i;
	mtexinfo_t	*tex;
	byte		*lightmap;
	unsigned	scale;
	int			maps;

	if (node->contents < 0)
		return -1;		// didn't hit anything
	
// calculate mid point

// FIXME: optimize for axial
	plane = node->plane;
	front = DotProduct (start, plane->normal) - plane->dist;
	back = DotProduct (end, plane->normal) - plane->dist;
	side = front < 0;
	
	if ( (back < 0) == side)
		return RecursiveLightPoint (node->children[side], start, end);
	
	frac = front / (front-back);
	mid[0] = start[0] + (end[0] - start[0])*frac;
	mid[1] = start[1] + (end[1] - start[1])*frac;
	mid[2] = start[2] + (end[2] - start[2])*frac;
	
// go down front side	
	r = RecursiveLightPoint (node->children[side], start, mid);
	if (r >= 0)
		return r;		// hit something
		
	if ( (back < 0) == side )
		return -1;		// didn't hit anything
		
// check for impact on this node
	VectorCopy (mid, lightspot);
	lightplane = plane;

	surf = r_worldmodel->surfaces + node->firstsurface;
	for (i=0 ; i<node->numsurfaces ; i++, surf++)
	{
		if (surf->flags & SURF_UNLIT)
			continue;	// no lightmaps

		tex = surf->texinfo;
		
		s = DotProduct (mid, tex->vecs[0]) + tex->vecs[0][3];
		t = DotProduct (mid, tex->vecs[1]) + tex->vecs[1][3];;

		if (s < surf->texturemins[0] || t < surf->texturemins[1])
			continue;
		
		ds = s - surf->texturemins[0];
		dt = t - surf->texturemins[1];
		
		if (ds > surf->extents[0] || dt > surf->extents[1])
			continue;

		if (!surf->samples)
			return 0;

		ds >>= 4;
		dt >>= 4;

		lightmap = surf->samples + (dt * ((surf->extents[0]>>4)+1) + ds) * 3 /* RGB */;

		for (maps = 0; maps < MAXLIGHTMAPS && surf->styles[maps] != 255;
				maps++)
		{
			scale = d_lightstylevalue[surf->styles[maps]];
			lightcolor[0] += lightmap[0] * scale;
			lightcolor[1] += lightmap[1] * scale;
			lightcolor[2] += lightmap[2] * scale;
			lightmap += ((surf->extents[0]>>4)+1) *
					((surf->extents[1]>>4)+1) * 3 /* RGB */;
		}

		r = max(lightcolor[0], max(lightcolor[1], lightcolor[2])) >> 8;
		//r = ((lightcolor[0] + lightcolor[1] + lightcolor[2]) / 3) >> 8;
		
		return r;
	}

// go down back side
	return RecursiveLightPoint (node->children[!side], mid, end);
}

int R_LightPoint (vec3_t p, /* out */ vec3_t color)
{
	vec3_t		end;
	int			r;
	
	if (!r_worldmodel->lightdata) {
		VectorSet (color, 255, 255, 255);
		return 255;
	}

	VectorClear (lightcolor);
	
	end[0] = p[0];
	end[1] = p[1];
	end[2] = p[2] - 2048;

	r = RecursiveLightPoint (r_worldmodel->nodes, p, end);
	
	if (r == -1) {
		r = 0;
		VectorClear (lightcolor);
	}

	color[0] = lightcolor[0] / 256.0f;
	color[1] = lightcolor[1] / 256.0f;
	color[2] = lightcolor[2] / 256.0f;

	return r;
}

