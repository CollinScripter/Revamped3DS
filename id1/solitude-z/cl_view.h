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
// cl_view.h
#ifndef _CL_VIEW_H_
#define _CL_VIEW_H_

extern	cvar_t		sw_gamma;
extern	cvar_t		sw_contrast;

#ifdef GLQUAKE
extern float v_blend[4];
#endif

void V_ClearScene (void);
void V_AddEntity (entity_t *ent);
void V_AddDlight(int key, vec3_t origin, float	radius, float minlight, dlighttype_t type);
void V_AddParticle (vec3_t origin, int color, float alpha);

void V_Init (void);
void V_NewMap (void);
void V_RenderView (void);
void V_UpdatePalette (void);
void V_ParseDamage (void);
void V_SetContentsColor (int contents);
void V_CalcBlend (void);

float V_CalcRoll (vec3_t angles, vec3_t velocity);

void V_StartPitchDrift (void);
void V_StopPitchDrift (void);

#endif /* _CL_VIEW_H_ */

