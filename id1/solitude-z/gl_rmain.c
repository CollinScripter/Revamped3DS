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
// gl_rmain.c

#include "gl_local.h"
#include "sound.h"
#include "rc_image.h"
#include "qlib.h"

model_t		*r_worldmodel;
entity_t	r_worldentity;

qbool		r_cache_thrash;		// compatability

vec3_t		modelorg, r_entorigin;
entity_t	*currententity;

int			r_visframecount;	// bumped when going to a new PVS
int			r_framecount;		// used for dlight push checking

mplane_t	frustum[4];

int			c_brush_polys, c_alias_polys;

int			currenttexture = -1;		// to avoid unnecessary texture sets
int			cnttextures[2] = {-1, -1};	// cached

//
// view origin
//
vec3_t	vup;
vec3_t	vpn;
vec3_t	vright;
vec3_t	r_origin;

//
// screen size info
//
refdef2_t	r_refdef2;

mleaf_t		*r_viewleaf, *r_oldviewleaf;
mleaf_t		*r_viewleaf2, *r_oldviewleaf2;	// for watervis hack

texture_t	*r_notexture_mip;

int		d_lightstylevalue[256];	// 8.8 fraction of base light value

cvar_t	r_norefresh = {"r_norefresh","0"};
cvar_t	r_drawentities = {"r_drawentities","1"};
cvar_t	r_drawflame = {"r_drawflame","1", CVAR_ARCHIVE};
cvar_t	r_speeds = {"r_speeds","0"};
cvar_t	r_fullbright = {"r_fullbright","0"};
cvar_t	r_lightmap = {"r_lightmap","0"};
cvar_t	r_shadows = {"r_shadows","0"};
cvar_t	r_wateralpha = {"r_wateralpha","1"};
cvar_t	r_dynamic = {"r_dynamic","1"};
cvar_t	r_novis = {"r_novis","0"};
cvar_t	r_netgraph = {"r_netgraph","0"};
cvar_t	r_fullbrightSkins = {"r_fullbrightSkins", "1", CVAR_ARCHIVE};
cvar_t	r_fastsky = {"r_fastsky", "0", CVAR_ARCHIVE};
cvar_t	r_skycolor = {"r_skycolor", "4", CVAR_ARCHIVE};
cvar_t	r_fastturb = {"r_fastturb", "0", CVAR_ARCHIVE};
cvar_t	r_farclip = {"r_farclip", "4096"};

cvar_t	gl_subdivide_size = {"gl_subdivide_size", "64", CVAR_ARCHIVE};
cvar_t	gl_clear = {"gl_clear","0"};
cvar_t	gl_cull = {"gl_cull","1"};
cvar_t	gl_texsort = {"gl_texsort","1"};
cvar_t	gl_ztrick = {"gl_ztrick", "1"};
cvar_t	gl_smoothmodels = {"gl_smoothmodels","1"};
cvar_t	gl_affinemodels = {"gl_affinemodels","0"};
cvar_t	gl_polyblend = {"gl_polyblend","1"};
cvar_t	gl_flashblend = {"gl_flashblend","0"};
cvar_t	gl_playermip = {"gl_playermip","0"};
cvar_t	gl_nocolors = {"gl_nocolors","0"};
cvar_t	gl_finish = {"gl_finish","0"};
cvar_t	gl_fb_depthhack = {"gl_fb_depthhack","1"};
cvar_t	gl_fb_bmodels = {"gl_fb_bmodels","0"};
cvar_t	gl_fb_models = {"gl_fb_models","0"};
cvar_t	gl_colorlights = {"gl_colorlights","1", CVAR_ARCHIVE};
cvar_t	gl_loadlitfiles = {"gl_loadlitfiles","1", CVAR_ARCHIVE};
cvar_t	gl_lightmode = {"gl_lightmode","2"};
cvar_t	gl_solidparticles = {"gl_solidparticles", "0"};
cvar_t	gl_shaftlight = {"gl_shaftlight", "1"};

int		lightmode = 2;

cvar_t	gl_strings = {"gl_strings", "", CVAR_ROM};
const char *gl_vendor;
const char *gl_renderer;
const char *gl_version;
const char *gl_extensions;

float		gldepthmin, gldepthmax;


#ifndef _WIN32
qbool vid_hwgamma_enabled = false;	// dummy
#endif


void R_MarkLeaves (void);


/*
=================
R_CullBox

Returns true if the box is completely outside the frustom
=================
*/
qbool R_CullBox (vec3_t mins, vec3_t maxs)
{
	int		i;
	mplane_t *p;

	for (i=0,p=frustum ; i<4; i++,p++)
	{
		switch (p->signbits)
		{
		case 0:
			if (p->normal[0]*maxs[0] + p->normal[1]*maxs[1] + p->normal[2]*maxs[2] < p->dist)
				return true;
			break;
		case 1:
			if (p->normal[0]*mins[0] + p->normal[1]*maxs[1] + p->normal[2]*maxs[2] < p->dist)
				return true;
			break;
		case 2:
			if (p->normal[0]*maxs[0] + p->normal[1]*mins[1] + p->normal[2]*maxs[2] < p->dist)
				return true;
			break;
		case 3:
			if (p->normal[0]*mins[0] + p->normal[1]*mins[1] + p->normal[2]*maxs[2] < p->dist)
				return true;
			break;
		case 4:
			if (p->normal[0]*maxs[0] + p->normal[1]*maxs[1] + p->normal[2]*mins[2] < p->dist)
				return true;
			break;
		case 5:
			if (p->normal[0]*mins[0] + p->normal[1]*maxs[1] + p->normal[2]*mins[2] < p->dist)
				return true;
			break;
		case 6:
			if (p->normal[0]*maxs[0] + p->normal[1]*mins[1] + p->normal[2]*mins[2] < p->dist)
				return true;
			break;
		case 7:
			if (p->normal[0]*mins[0] + p->normal[1]*mins[1] + p->normal[2]*mins[2] < p->dist)
				return true;
			break;
		default:
			return false;
		}
	}

	return false;
}

/*
=================
R_CullSphere

Returns true if the sphere is completely outside the frustum
=================
*/
qbool R_CullSphere (vec3_t centre, float radius)
{
	int		i;
	mplane_t *p;

	for (i=0,p=frustum ; i<4; i++,p++)
	{
		if ( DotProduct (centre, p->normal) - p->dist <= -radius )
			return true;
	}

	return false;
}

void R_RotateForEntity (entity_t *e)
{
	glTranslatef (e->origin[0],  e->origin[1],  e->origin[2]);

	glRotatef (e->angles[1], 0, 0, 1);
	glRotatef (-e->angles[0], 0, 1, 0);
	glRotatef (e->angles[2], 1, 0, 0);
}

//==================================================================================

/*
=============
R_DrawEntitiesOnList
=============
*/
void R_DrawEntitiesOnList (void)
{
	int		i;
	qbool	draw_sprites;
	qbool	draw_translucent;

	if (!r_drawentities.value)
		return;

	draw_sprites = draw_translucent = false;

	for (i = 0; i < cl_numvisedicts; i++)
	{
		currententity = &cl_visedicts[i];

		switch (currententity->model->type)
		{
			case mod_alias:
				if (!(currententity->renderfx & RF_TRANSLUCENT))
					R_DrawAliasModel (currententity);
				else
					draw_translucent = true;
				break;

			case mod_brush:
				R_DrawBrushModel (currententity);
				break;

			case mod_sprite:
				draw_sprites = true;
				break;

			default:
				break;
		}
	}

	// draw sprites separately, because of alpha blending
	if (draw_sprites)
	{
		GL_DisableMultitexture ();
		glEnable (GL_ALPHA_TEST);
//		glDepthMask (GL_FALSE);

		for (i = 0; i < cl_numvisedicts; i++)
		{
			currententity = &cl_visedicts[i];

			if (currententity->model->type == mod_sprite)
				R_DrawSpriteModel (currententity);
		}

		glDisable (GL_ALPHA_TEST);
//		glDepthMask (GL_TRUE);
	}

	// draw translucent models
	if (draw_translucent)
	{
//		glDepthMask (GL_FALSE);		// no z writes
		for (i = 0; i < cl_numvisedicts; i++)
		{
			currententity = &cl_visedicts[i];

			if (currententity->model->type == mod_alias
					&& (currententity->renderfx & RF_TRANSLUCENT))
				R_DrawAliasModel (currententity);
		}
//		glDepthMask (GL_TRUE);
	}
}

/*
===============
R_DrawParticles
===============
*/
void R_DrawParticles (void)
{
	int				i;
	byte			color[4];
	vec3_t			up, right;
	float			dist, scale;
	particle_t		*p;
	float			r_partscale;
	
	r_partscale = 0.004 * tan (r_refdef2.fov_x * (M_PI/180) * 0.5f);

	VectorScale (vup, 1.5, up);
	VectorScale (vright, 1.5, right);

	GL_Bind (particletexture);
	
	glEnable (GL_BLEND);
	if (!gl_solidparticles.value)
		glDepthMask (GL_FALSE);
	glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
	glBegin (GL_TRIANGLES);

	for (i = 0, p = r_refdef2.particles; i < r_refdef2.numParticles; i++, p++)
	{
		// hack a scale up to keep particles from disapearing
		dist = (p->org[0] - r_origin[0])*vpn[0] + (p->org[1] - r_origin[1])*vpn[1]
			+ (p->org[2] - r_origin[2])*vpn[2];
		scale = 1 + dist * r_partscale;

		*(int *)color = d_8to24table[p->color];
		color[3] = p->alpha * 255;

		glColor4ubv (color);

		glTexCoord2f (0, 0);
		glVertex3fv (p->org);

		glTexCoord2f (0.9, 0);
		glVertex3f (p->org[0] + up[0]*scale, 
			p->org[1] + up[1]*scale, 
			p->org[2] + up[2]*scale);

		glTexCoord2f (0, 0.9);
		glVertex3f (p->org[0] + right[0]*scale,
			p->org[1] + right[1]*scale, 
			p->org[2] + right[2]*scale);
	}

	glEnd ();
	glDisable (GL_BLEND);
	glDepthMask (GL_TRUE);
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
	glColor3f (1, 1, 1);
}

/*
============
R_PolyBlend
============
*/
void R_PolyBlend (void)
{
	extern cvar_t	gl_hwblend;

	if (vid_hwgamma_enabled && (gl_hwblend.value && !cl.teamfortress))
		return;
	if (!v_blend[3])
		return;

	glDisable (GL_ALPHA_TEST);
	glEnable (GL_BLEND);
	glDisable (GL_TEXTURE_2D);

	glColor4fv (v_blend);

	glBegin (GL_QUADS);
	glVertex2f (r_refdef2.vrect.x, r_refdef2.vrect.y);
	glVertex2f (r_refdef2.vrect.x + r_refdef2.vrect.width, r_refdef2.vrect.y);
	glVertex2f (r_refdef2.vrect.x + r_refdef2.vrect.width, r_refdef2.vrect.y + r_refdef2.vrect.height);
	glVertex2f (r_refdef2.vrect.x, r_refdef2.vrect.y + r_refdef2.vrect.height);
	glEnd ();

	glDisable (GL_BLEND);
	glEnable (GL_TEXTURE_2D);
	glEnable (GL_ALPHA_TEST);

	glColor3f (1, 1, 1);
}

/*
================
R_BrightenScreen
================
*/
void R_BrightenScreen (void)
{
	float	f;

	if (vid_hwgamma_enabled)
		return;
	if (gl_contrast.value <= 1.0)
		return;

	f = gl_contrast.value;
	if (f > 3)
		f = 3;

	glDisable (GL_TEXTURE_2D);
	glEnable (GL_BLEND);
	glBlendFunc (GL_DST_COLOR, GL_ONE);
	glBegin (GL_QUADS);
	while (f > 1)
	{
		if (f >= 2)
			glColor3f (1, 1, 1);
		else
			glColor3f (f - 1, f - 1, f - 1);
		glVertex2f (0, 0);
		glVertex2f (vid.width, 0);
		glVertex2f (vid.width, vid.height);
		glVertex2f (0, vid.height);
		f *= 0.5;
	}
	glEnd ();
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glEnable (GL_TEXTURE_2D);
	glDisable (GL_BLEND);
	glColor3f (1, 1, 1);
}

int SignbitsForPlane (mplane_t *out)
{
	int	bits, j;

	// for fast box on planeside test

	bits = 0;
	for (j=0 ; j<3 ; j++)
	{
		if (out->normal[j] < 0)
			bits |= 1<<j;
	}
	return bits;
}


void R_SetFrustum (void)
{
	int		i;

	// rotate VPN right by FOV_X/2 degrees
	RotatePointAroundVector( frustum[0].normal, vup, vpn, -(90-r_refdef2.fov_x / 2 ) );
	// rotate VPN left by FOV_X/2 degrees
	RotatePointAroundVector( frustum[1].normal, vup, vpn, 90-r_refdef2.fov_x / 2 );
	// rotate VPN up by FOV_X/2 degrees
	RotatePointAroundVector( frustum[2].normal, vright, vpn, 90-r_refdef2.fov_y / 2 );
	// rotate VPN down by FOV_X/2 degrees
	RotatePointAroundVector( frustum[3].normal, vright, vpn, -( 90 - r_refdef2.fov_y / 2 ) );

	for (i=0 ; i<4 ; i++)
	{
		frustum[i].type = PLANE_ANYZ;
		frustum[i].dist = DotProduct (r_origin, frustum[i].normal);
		frustum[i].signbits = SignbitsForPlane (&frustum[i]);
	}
}



/*
===============
R_SetupFrame
===============
*/
void R_SetupFrame (void)
{
	vec3_t	testorigin;
	mleaf_t	*leaf;
	extern float	wateralpha;

	// use wateralpha only if the server allows
	wateralpha = r_refdef2.watervis ? r_wateralpha.value : 1;

	R_AnimateLight ();

	r_framecount++;

// build the transformation matrix for the given view angles
	VectorCopy (r_refdef2.vieworg, r_origin);

	AngleVectors (r_refdef2.viewangles, vpn, vright, vup);

// current viewleaf
	r_oldviewleaf = r_viewleaf;
	r_oldviewleaf2 = r_viewleaf2;

	r_viewleaf = Mod_PointInLeaf (r_origin, r_worldmodel);
	r_viewleaf2 = NULL;

	// check above and below so crossing solid water doesn't draw wrong
	if (r_viewleaf->contents <= CONTENTS_WATER && r_viewleaf->contents >= CONTENTS_LAVA)
	{
		// look up a bit
		VectorCopy (r_origin, testorigin);
		testorigin[2] += 10;
		leaf = Mod_PointInLeaf (testorigin, r_worldmodel);
		if (leaf->contents == CONTENTS_EMPTY)
			r_viewleaf2 = leaf;
	}
	else if (r_viewleaf->contents == CONTENTS_EMPTY)
	{
		// look down a bit
		VectorCopy (r_origin, testorigin);
		testorigin[2] -= 10;
		leaf = Mod_PointInLeaf (testorigin, r_worldmodel);
		if (leaf->contents <= CONTENTS_WATER &&	leaf->contents >= CONTENTS_LAVA)
			r_viewleaf2 = leaf;
	}

	V_SetContentsColor (r_viewleaf->contents);
	V_CalcBlend ();

	r_cache_thrash = false;

	c_brush_polys = 0;
	c_alias_polys = 0;

}


void MYgluPerspective( GLdouble fovy, GLdouble aspect,
			GLdouble zNear, GLdouble zFar )
{
	GLdouble xmin, xmax, ymin, ymax;
	
	ymax = zNear * tan( fovy * M_PI / 360.0 );
	ymin = -ymax;
	
	xmin = ymin * aspect;
	xmax = ymax * aspect;
	
	glFrustum( xmin, xmax, ymin, ymax, zNear, zFar );
}


/*
=============
R_SetupGL
=============
*/
void R_SetupGL (void)
{
	float	screenaspect;
	int		x, x2, y2, y, w, h, farclip;

	//
	// set up viewpoint
	//
	glMatrixMode(GL_PROJECTION);
    glLoadIdentity ();
	x = (r_refdef2.vrect.x * vid.realwidth) / vid.width;
	x2 = ((r_refdef2.vrect.x + r_refdef2.vrect.width) * vid.realwidth) / vid.width;
	y = ((vid.height - r_refdef2.vrect.y) * vid.realheight) / vid.height;
	y2 = ((vid.height - (r_refdef2.vrect.y + r_refdef2.vrect.height)) * vid.realheight) / vid.height;

	// fudge around because of frac screen scale
	if (x > 0)
		x--;
	if (x2 < vid.realwidth)
		x2++;
	if (y2 < 0)
		y2--;
	if (y < vid.realheight)
		y++; 

	w = x2 - x;
	h = y - y2;

	glViewport (x, y2, w, h);
	screenaspect = (float)r_refdef2.vrect.width/r_refdef2.vrect.height * vid.aspect;
	farclip = max((int) r_farclip.value, 4096);
	MYgluPerspective (r_refdef2.fov_y,  screenaspect,  4,  farclip);

	glCullFace(GL_FRONT);

	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity ();

	glRotatef (-90,  1, 0, 0);		// put Z going up
	glRotatef (90,	0, 0, 1);		// put Z going up
	glRotatef (-r_refdef2.viewangles[2],  1, 0, 0);
	glRotatef (-r_refdef2.viewangles[0],  0, 1, 0);
	glRotatef (-r_refdef2.viewangles[1],  0, 0, 1);
	glTranslatef (-r_refdef2.vieworg[0], -r_refdef2.vieworg[1], -r_refdef2.vieworg[2]);

	//
	// set drawing parms
	//
	if (gl_cull.value)
		glEnable(GL_CULL_FACE);
	else
		glDisable(GL_CULL_FACE);

	glDisable(GL_BLEND);
	glDisable(GL_ALPHA_TEST);
	glEnable(GL_DEPTH_TEST);
}


extern void R_InitBubble (void);
extern void R_Draw_Init (void);
extern void R_SetPalette (byte *palette);

/*
===============
R_Init
===============
*/
void R_Init (unsigned char *palette)
{
	Cmd_AddCommand ("timerefresh", R_TimeRefresh_f);
	Cmd_AddCommand ("screenshot", R_ScreenShot_f);
	Cmd_AddCommand ("loadsky", R_LoadSky_f);

	Cvar_Register (&r_norefresh);
	Cvar_Register (&r_lightmap);
	Cvar_Register (&r_fullbright);
	Cvar_Register (&r_drawentities);
	Cvar_Register (&r_drawflame);
	Cvar_Register (&r_shadows);
	Cvar_Register (&r_wateralpha);
	Cvar_Register (&r_dynamic);
	Cvar_Register (&r_novis);
	Cvar_Register (&r_speeds);
	Cvar_Register (&r_netgraph);
	Cvar_Register (&r_fullbrightSkins);
	Cvar_Register (&r_skycolor);
	Cvar_Register (&r_fastsky);
	Cvar_Register (&r_fastturb);
	Cvar_Register (&r_farclip);

	Cvar_Register (&gl_subdivide_size);
	Cvar_Register (&gl_clear);
	Cvar_Register (&gl_texsort);
	Cvar_Register (&gl_cull);
	Cvar_Register (&gl_ztrick);
	Cvar_Register (&gl_smoothmodels);
	Cvar_Register (&gl_affinemodels);
	Cvar_Register (&gl_polyblend);
	Cvar_Register (&gl_flashblend);
	Cvar_Register (&gl_playermip);
	Cvar_Register (&gl_nocolors);
	Cvar_Register (&gl_finish);
	Cvar_Register (&gl_fb_depthhack);
	Cvar_Register (&gl_fb_bmodels);
	Cvar_Register (&gl_fb_models);
	Cvar_Register (&gl_colorlights);
	Cvar_Register (&gl_loadlitfiles);
	Cvar_Register (&gl_lightmode);
	Cvar_Register (&gl_solidparticles);
	Cvar_Register (&gl_shaftlight);

	// assume gl_texsort 0 is faster if the card supports multitexture
	if (gl_mtexable)
		Cvar_SetValue (&gl_texsort, 0);

	// this minigl driver seems to slow us down if the particles
	// are drawn WITHOUT Z buffer bits
	if (!strcmp(gl_vendor, "METABYTE/WICKED3D"))
		Cvar_SetValue(&gl_solidparticles, 1);

	R_SetPalette (palette);
	R_InitTextures ();
	R_Draw_Init ();
	R_InitBubble ();
	Mod_Init ();
	QLib_Init ();
	Image_Init ();
}


/*
===============
GL_Init
===============
*/
extern void GL_CheckExtensions (void);
void GL_Init (void)
{
	gl_vendor = (const char *) glGetString (GL_VENDOR);
	Com_Printf ("GL_VENDOR: %s\n", gl_vendor);
	gl_renderer = (const char *) glGetString (GL_RENDERER);
	Com_Printf ("GL_RENDERER: %s\n", gl_renderer);
	gl_version = (const char *) glGetString (GL_VERSION);
	Com_Printf ("GL_VERSION: %s\n", gl_version);
	gl_extensions = (const char *) glGetString (GL_EXTENSIONS);
//	Com_Printf ("GL_EXTENSIONS: %s\n", gl_extensions);

	Cvar_Register (&gl_strings);
	Cvar_ForceSet (&gl_strings, va("GL_VENDOR: %s\nGL_RENDERER: %s\n"
		"GL_VERSION: %s\nGL_EXTENSIONS: %s", gl_vendor, gl_renderer, gl_version, gl_extensions));

	glClearColor (1,0,0,0);
	glCullFace(GL_FRONT);
	glEnable(GL_TEXTURE_2D);

	glEnable(GL_ALPHA_TEST);
	glAlphaFunc(GL_GREATER, 0.666);

	glPolygonMode (GL_FRONT_AND_BACK, GL_FILL);
	glShadeModel (GL_FLAT);

	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);

	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);

	GL_CheckExtensions();
}


/*
================
R_RenderScene

r_refdef must be set before the first call
================
*/
void R_RenderScene (void)
{
	R_SetupFrame ();

	R_SetFrustum ();

	R_SetupGL ();

	R_MarkLeaves ();	// done here so we know if we're in water

	R_DrawWorld ();		// adds static entities to the list

	S_ExtraUpdate ();	// don't let sound get messed up if going slow

	R_DrawEntitiesOnList ();

	GL_DisableMultitexture();

	R_RenderDlights ();
}


/*
=============
R_Clear
=============
*/
int gl_ztrickframe = 0;
void R_Clear (void)
{
	static qbool cleartogray;
	qbool	clear = false;

	if (gl_clear.value) {
		clear = true;
		if (cleartogray) {
			glClearColor (1, 0, 0, 0);
			cleartogray = false;
		}
	}
	else if (!vid_hwgamma_enabled && gl_contrast.value > 1) {
		clear = true;
		if (!cleartogray) {
			glClearColor (0.1, 0.1, 0.1, 0);
			cleartogray = true;
		}
	}

	if (gl_ztrick.value)
	{
		if (clear)
			glClear (GL_COLOR_BUFFER_BIT);

		gl_ztrickframe = !gl_ztrickframe;
		if (gl_ztrickframe)
		{
			gldepthmin = 0;
			gldepthmax = 0.49999;
			glDepthFunc (GL_LEQUAL);
		}
		else
		{
			gldepthmin = 1;
			gldepthmax = 0.5;
			glDepthFunc (GL_GEQUAL);
		}
	}
	else
	{
		if (clear)
			glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
		else
			glClear (GL_DEPTH_BUFFER_BIT);
		gldepthmin = 0;
		gldepthmax = 1;
		glDepthFunc (GL_LEQUAL);
	}

	glDepthRange (gldepthmin, gldepthmax);
}

/*
================
R_RenderView

r_refdef must be set before the first call
================
*/
void R_RenderView (void)
{
	double	time1 = 0, time2;

	if (r_norefresh.value)
		return;

	if (!r_worldentity.model || !r_worldmodel)
		Sys_Error ("R_RenderView: NULL worldmodel");

	if (r_speeds.value)
	{
		glFinish ();
		time1 = Sys_DoubleTime ();
		c_brush_polys = 0;
		c_alias_polys = 0;
	}

	if (gl_finish.value)
		glFinish ();

	R_Clear ();

	// render normal view
	R_RenderScene ();
	R_DrawWaterSurfaces ();
	R_DrawParticles ();

	if (r_speeds.value)
	{
//		glFinish ();
		time2 = Sys_DoubleTime ();
		Com_Printf ("%3i ms  %4i wpoly %4i epoly\n", (int)((time2-time1)*1000), c_brush_polys, c_alias_polys); 
	}
}
