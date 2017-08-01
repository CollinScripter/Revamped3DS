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
// gl_ralias.c - GL rendering of alias models (*.mdl)

#include "gl_local.h"


/*
=============================================================

  ALIAS MODELS

=============================================================
*/


#define NUMVERTEXNORMALS	162

// also used in cl_effects.c
float	r_avertexnormals[NUMVERTEXNORMALS][3] = {
#include "anorms.h"
};

static vec3_t	shadevector;
static float	shadescale = 0;

static vec3_t	shadelight_v, ambientlight_v;

// precalculated dot products for quantized angles
#define SHADEDOT_QUANT 16
static float	r_avertexnormal_dots[SHADEDOT_QUANT][256] =
#include "anorm_dots.h"
;

static float	*shadedots = r_avertexnormal_dots[0];

static int	lastpose;

/*
=============
GL_DrawAliasFrame
=============
*/
static void GL_DrawAliasFrame (aliashdr_t *paliashdr, int pose, int oldpose, float backlerp, qbool mtex)
{
	int		i;
	float	l_v[4];
	vec3_t	vec;
	trivertx_t	*verts, *oldverts;
	int		*order;
	int		count;
	float	blerp;

	if (currententity->renderfx & RF_TRANSLUCENT)
	{
		glEnable (GL_BLEND);
		l_v[3] = currententity->alpha;
	}
	else
		l_v[3] = 1.0;

	backlerp = bound (0, backlerp, 1);
	lastpose = backlerp < 0.5 ? pose : oldpose;

	verts = oldverts = (trivertx_t *)((byte *)paliashdr + paliashdr->posedata);
	verts += pose * paliashdr->poseverts;
	oldverts += oldpose * paliashdr->poseverts;
	order = (int *)((byte *)paliashdr + paliashdr->commands);

	while ((count = *order++))
	{
		// get the vertex count and primitive type
		if (count < 0)
		{
			count = -count;
			glBegin (GL_TRIANGLE_FAN);
		}
		else
			glBegin (GL_TRIANGLE_STRIP);

		do
		{
			// texture coordinates come from the draw list
			if (mtex) {
				qglMultiTexCoord2f (GL_TEXTURE0_ARB, ((float *) order)[0], ((float *) order)[1]);
				qglMultiTexCoord2f (GL_TEXTURE1_ARB, ((float *) order)[0], ((float *) order)[1]);
			}
			else {
				glTexCoord2f (((float *) order)[0], ((float *) order)[1]);
			}

			order += 2;

			blerp = backlerp;
			if (currententity->renderfx & RF_LIMITLERP) {
				vec3_t diff;
				VectorSubtract (verts->v, oldverts->v, diff);
				if (VectorLengthSquared(diff) > 18225) // 18225 == (135*135)
					blerp = 0;
			}

			// normals and vertexes come from the frame list
			{
			float tmp = LerpFloat(shadedots[verts->lightnormalindex], shadedots[oldverts->lightnormalindex], blerp);
			for (i = 0; i < 3; i++) {
				l_v[i] = (tmp * shadelight_v[i] + ambientlight_v[i]) / 256.0;

				if (l_v[i] > 1)
					l_v[i] = 1;
			}
			}
			glColor4fv (l_v);
			vec[0] = LerpFloat(verts->v[0], oldverts->v[0], blerp);
			vec[1] = LerpFloat(verts->v[1], oldverts->v[1], blerp);
			vec[2] = LerpFloat(verts->v[2], oldverts->v[2], blerp);
			glVertex3fv (vec);
			verts++;
			oldverts++;
		} while (--count);

		glEnd ();
	}

	if (currententity->renderfx & RF_TRANSLUCENT)
		glDisable (GL_BLEND);
}


/*
=============
GL_DrawAliasShadow
=============
*/
extern	vec3_t			lightspot;

static void GL_DrawAliasShadow (aliashdr_t *paliashdr, int posenum)
{
	trivertx_t	*verts;
	int		*order;
	vec3_t	point;
	int		count;
	float	lheight = currententity->origin[2] - lightspot[2];
	float	height = 1 - lheight;

	verts = (trivertx_t *)((byte *)paliashdr + paliashdr->posedata);
	verts += posenum * paliashdr->poseverts;
	order = (int *)((byte *)paliashdr + paliashdr->commands);

	while ((count = *order++))
	{
		// get the vertex count and primitive type
		if (count < 0)
		{
			count = -count;
			glBegin (GL_TRIANGLE_FAN);
		}
		else
			glBegin (GL_TRIANGLE_STRIP);

		do
		{
			// texture coordinates come from the draw list
			// (skipped for shadows) glTexCoord2fv ((float *)order);
			order += 2;

			// normals and vertexes come from the frame list
			point[0] = verts->v[0] * paliashdr->scale[0] + paliashdr->scale_origin[0];
			point[1] = verts->v[1] * paliashdr->scale[1] + paliashdr->scale_origin[1];
			point[2] = verts->v[2] * paliashdr->scale[2] + paliashdr->scale_origin[2];

			point[0] -= shadevector[0]*(point[2]+lheight);
			point[1] -= shadevector[1]*(point[2]+lheight);
			point[2] = height;
//			height -= 0.001;
			glVertex3fv (point);

			verts++;
		} while (--count);

		glEnd ();
	}	
}



/*
=================
R_SetupAliasFrame

=================
*/
static void R_SetupAliasFrame (int frame, int oldframe, float backlerp, aliashdr_t *paliashdr, qbool mtex)
{
	int				pose, oldpose, numposes;
	float			interval;

	if ((frame >= paliashdr->numframes) || (frame < 0))
	{
		Com_DPrintf ("R_AliasSetupFrame: no such frame %d\n", frame);
		frame = 0;
	}

	if ((oldframe >= paliashdr->numframes) || (oldframe < 0))
	{
		Com_DPrintf ("R_AliasSetupFrame: no such frame %d\n", oldframe);
		oldframe = 0;
		backlerp = 0;
	}

	pose = paliashdr->frames[frame].firstpose;
	numposes = paliashdr->frames[frame].numposes;
	if (numposes > 1)
	{
		interval = paliashdr->frames[frame].interval;
		pose += (int)(r_refdef2.time / interval) % numposes;
	}

	oldpose = paliashdr->frames[oldframe].firstpose;
	if (paliashdr->frames[oldframe].numposes > 1)
	{
		interval = paliashdr->frames[oldframe].interval;
		oldpose += (int)(r_refdef2.time / interval) % paliashdr->frames[oldframe].numposes;
	}

	GL_DrawAliasFrame (paliashdr, pose, oldpose, backlerp, mtex);
}


// Because of poor quality of the lits out there, in many situations
// I'd prefer the models not to be colored at all.
// This is an attempt to compromise
static void DesaturateColor (vec3_t color, float white_level)
{
#define white_fraction 0.5
	int i;
	for (i = 0; i < 3; i++) {
		color[i] = color[i] * (1 - white_fraction) + white_level * white_fraction;
	}
}

/*
=================
R_DrawAliasModel

=================
*/
void R_DrawAliasModel (entity_t *ent)
{
	int			lnum;
	vec3_t		dist;
	float		add;
	vec3_t		mins, maxs;
	aliashdr_t	*paliashdr;
	int			anim, skinnum;
	qbool		full_light;
	model_t		*clmodel = ent->model;
	int			texture, fb_texture;
	vec3_t		lightcolor;
	float		shadelight, ambientlight;
	float	original_light;

	VectorAdd (ent->origin, clmodel->mins, mins);
	VectorAdd (ent->origin, clmodel->maxs, maxs);

	if (ent->angles[0] || ent->angles[1] || ent->angles[2])
	{
		if (R_CullSphere (ent->origin, clmodel->radius))
			return;
	}
	else
	{
		if (R_CullBox (mins, maxs))
			return;
	}

	VectorCopy (ent->origin, r_entorigin);
	VectorSubtract (r_origin, r_entorigin, modelorg);

	//
	// get lighting information
	//

// make thunderbolt and torches full light
	if (clmodel->modhint == MOD_THUNDERBOLT || clmodel->modhint == MOD_THUNDERBOLT2) {
		ambientlight = 60 + 150 * (clmodel->modhint == MOD_THUNDERBOLT2 ?
									bound(0, gl_shaftlight.value, 1) : 1);
		shadelight = 0;
		VectorSet (ambientlight_v, ambientlight, ambientlight, ambientlight);
		VectorClear (shadelight_v);
		full_light = true;
	} else if (clmodel->modhint == MOD_FLAME) {
		ambientlight = 255;
		shadelight = 0;
		VectorSet (ambientlight_v, 255, 255, 255);
		VectorClear (shadelight_v);
		full_light = true;
	}
	else if ((clmodel->modhint == MOD_PLAYER || ent->renderfx & RF_PLAYERMODEL)
			&& r_fullbrightSkins.value && r_refdef2.allow_fbskins) {
		ambientlight = shadelight = 128;
		VectorSet (ambientlight_v, 128, 128, 128);
		VectorSet (shadelight_v, 128, 128, 128);
		full_light = true;
	}
	else
	{
		// normal lighting 
		full_light = false;
		original_light = ambientlight = shadelight = R_LightPoint (ent->origin, lightcolor);

		DesaturateColor (lightcolor, original_light);

		for (lnum = 0; lnum < r_refdef2.numDlights; lnum++)
		{

			VectorSubtract (ent->origin,
				r_refdef2.dlights[lnum].origin,
				dist);
			add = r_refdef2.dlights[lnum].radius - VectorLength(dist);
			
			if (add > 0)
				ambientlight += add;
		}
		
		// clamp lighting so it doesn't overbright as much
		if (ambientlight > 128)
			ambientlight = 128;
		if (ambientlight + shadelight > 192)
			shadelight = 192 - ambientlight;
		
		// always give the gun some light
		if ((ent->renderfx & RF_WEAPONMODEL) && ambientlight < 24)
			ambientlight = shadelight = 24;
		
		// never allow players to go totally black
		if (clmodel->modhint == MOD_PLAYER || ent->renderfx & RF_PLAYERMODEL) {
			if (ambientlight < 8)
				ambientlight = shadelight = 8;
		}

		if (original_light) {
			VectorScale (lightcolor, ambientlight / original_light, ambientlight_v);
			VectorScale (lightcolor, shadelight / original_light, shadelight_v);
		} else {
			VectorSet (ambientlight_v, ambientlight, ambientlight, ambientlight);
			VectorSet (shadelight_v, shadelight, shadelight, shadelight);
		}
	}

	shadedots = r_avertexnormal_dots[((int)(ent->angles[1] * (SHADEDOT_QUANT / 360.0))) & (SHADEDOT_QUANT - 1)];

	//
	// locate the proper data
	//
	paliashdr = (aliashdr_t *)Mod_Extradata (ent->model);

	c_alias_polys += paliashdr->numtris;

	//
	// draw all the triangles
	//

	glPushMatrix ();
	R_RotateForEntity (ent);

	if (clmodel->modhint == MOD_EYES) {
		glTranslatef (paliashdr->scale_origin[0], paliashdr->scale_origin[1], paliashdr->scale_origin[2] - (22 + 8));
	// double size of eyes, since they are really hard to see in gl
		glScalef (paliashdr->scale[0]*2, paliashdr->scale[1]*2, paliashdr->scale[2]*2);
	} else {
		glTranslatef (paliashdr->scale_origin[0], paliashdr->scale_origin[1], paliashdr->scale_origin[2]);
		glScalef (paliashdr->scale[0], paliashdr->scale[1], paliashdr->scale[2]);
	}

	anim = (int)(r_refdef2.time*10) & 3;
	skinnum = ent->skinnum;
	if ((skinnum >= paliashdr->numskins) || (skinnum < 0)) {
		Com_DPrintf ("R_DrawAliasModel: no such skin # %d\n", skinnum);
		skinnum = 0;
	}

	texture = paliashdr->gl_texturenum[skinnum][anim];
	fb_texture = paliashdr->fb_texturenum[skinnum][anim];

	// we can't dynamically colormap textures, so they are cached
	// separately for the players.  Heads are just uncolored.
	if (ent->colormap && (clmodel->modhint == MOD_PLAYER || ent->renderfx & RF_PLAYERMODEL)
		&& !gl_nocolors.value)
	{
		R_GetTranslatedPlayerSkin (ent->colormap, &texture, &fb_texture);
	}

	if (full_light || !gl_fb_models.value) {
		fb_texture = 0;
	}

	if (gl_smoothmodels.value)
		glShadeModel (GL_SMOOTH);

	if (gl_affinemodels.value)
		glHint (GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST);


	// hack the depth range to prevent view model from poking into walls
	if (ent->renderfx & RF_WEAPONMODEL)
		glDepthRange (gldepthmin, gldepthmin + 0.3*(gldepthmax-gldepthmin));


	if (fb_texture && gl_mtexfbskins) {
		GL_SelectTexture (GL_TEXTURE0_ARB);
		GL_Bind (texture);
		glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);

		GL_EnableMultitexture ();
		GL_Bind (fb_texture);
		glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL);

		R_SetupAliasFrame (ent->frame, ent->oldframe, ent->backlerp, paliashdr, true);

		GL_DisableMultitexture ();
	}
	else
	{
		GL_DisableMultitexture();
		GL_Bind (texture);
		glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);

		R_SetupAliasFrame (ent->frame, ent->oldframe, ent->backlerp, paliashdr, false);

		if (fb_texture) {
			glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
			glEnable (GL_BLEND);
			GL_Bind (fb_texture);

			R_SetupAliasFrame (ent->frame, ent->oldframe, ent->backlerp, paliashdr, false);

			glDisable (GL_BLEND);
		}
	}

	if (ent->renderfx & RF_WEAPONMODEL)
		glDepthRange (gldepthmin, gldepthmax);	// restore normal depth range


	glShadeModel (GL_FLAT);
	if (gl_affinemodels.value)
		glHint (GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);

	glPopMatrix ();

	if (r_shadows.value && !full_light && !(ent->renderfx & RF_WEAPONMODEL))
	{
		float an = -ent->angles[1] / 180 * M_PI;
		
		if (!shadescale)
			shadescale = 1/sqrt(2);

		shadevector[0] = cos(an) * shadescale;
		shadevector[1] = sin(an) * shadescale;
		shadevector[2] = shadescale;

		glPushMatrix ();

		glTranslatef (ent->origin[0],  ent->origin[1],  ent->origin[2]);
		glRotatef (ent->angles[1],  0, 0, 1);

		//FIXME glRotatef (-ent->angles[0],  0, 1, 0);
		//FIXME glRotatef (ent->angles[2],  1, 0, 0);

		glDisable (GL_TEXTURE_2D);
		glEnable (GL_BLEND);
		glColor4f (0, 0, 0, 0.5);
		GL_DrawAliasShadow (paliashdr, lastpose);
		glEnable (GL_TEXTURE_2D);
		glDisable (GL_BLEND);
		glPopMatrix ();
	}

	glColor3f (1, 1, 1);
}

