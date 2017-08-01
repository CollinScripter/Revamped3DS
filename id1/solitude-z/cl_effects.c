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

#include "quakedef.h"

#define ABSOLUTE_MIN_PARTICLES	512		// no fewer than this no matter what's
										// on the command line

enum
{
	pt_static, pt_grav, pt_fire, pt_explode, pt_explode2, pt_blob, pt_blob2, pt_rail
};

int		ramp1[8] = {0x6f, 0x6d, 0x6b, 0x69, 0x67, 0x65, 0x63, 0x61};
int		ramp2[8] = {0x6f, 0x6e, 0x6d, 0x6c, 0x6b, 0x6a, 0x68, 0x66};
int		ramp3[8] = {0x6d, 0x6b, 6, 5, 4, 3};

cparticle_t	*active_particles, *free_particles;

// processed locally
cparticle_t	*cl_particles;
int			cl_numparticles;	// should be named cl_maxparticles?

// sent to the renderer
int				cl_numvisparticles;
particle_t		*cl_visparticles;	// allocated on hunk


/*
===============
CL_InitParticles
===============
*/
void CL_InitParticles (void)
{
	int		i;

	i = COM_CheckParm ("-particles");

	if (i)
	{
		cl_numparticles = (int)(Q_atoi(com_argv[i+1]));
		if (cl_numparticles < ABSOLUTE_MIN_PARTICLES)
			cl_numparticles = ABSOLUTE_MIN_PARTICLES;
	}
	else
	{
		cl_numparticles = MAX_PARTICLES;
	}

	cl_particles = (cparticle_t *) Hunk_AllocName (cl_numparticles * sizeof(cparticle_t), "particles");
	cl_visparticles = (particle_t *) Hunk_AllocName (cl_numparticles * sizeof(particle_t), "visparticles");
}


/*
===============
CL_ClearParticles
===============
*/
void CL_ClearParticles (void)
{
	int		i;
	
	free_particles = &cl_particles[0];
	active_particles = NULL;

	for (i=0 ;i<cl_numparticles ; i++)
		cl_particles[i].next = &cl_particles[i+1];
	cl_particles[cl_numparticles-1].next = NULL;
}

static cparticle_t *new_particle (void)
{
	cparticle_t *p;

	if (!free_particles)
		return NULL;

	p = free_particles;
	free_particles = p->next;
	p->next = active_particles;
	active_particles = p;

	return p;
}

/*
===============
CL_ReadPointFile_f
===============
*/
void CL_ReadPointFile_f (void)
{
	FILE	*f;
	vec3_t	org;
	int		r;
	int		c;
	cparticle_t	*p;
	char	name[MAX_OSPATH];

	if (!com_serveractive && !r_refdef2.allow_cheats)
		return;

	sprintf (name, "maps/%s.pts", host_mapname.string);

	FS_FOpenFile (name, &f);
	if (!f)
	{
		Com_Printf ("couldn't open %s\n", name);
		return;
	}
	
	Com_Printf ("Reading %s...\n", name);
	c = 0;
	for ( ;; )
	{
		r = fscanf (f,"%f %f %f\n", &org[0], &org[1], &org[2]);
		if (r != 3)
			break;
		c++;
		
		if (!(p = new_particle()))
		{
			Com_Printf ("Not enough free particles\n");
			break;
		}

		p->die = 99999;
		p->color = (-c)&15;
		p->alpha = 1.0f;
		p->type = pt_static;
		VectorClear (p->vel);
		VectorCopy (org, p->org);
	}

	fclose (f);
	Com_Printf ("%i points read\n", c);
}
	
/*
===============
CL_ParticleExplosion
===============
*/
void CL_ParticleExplosion (vec3_t org)
{
	int			i, j;
	cparticle_t	*p;
	
	for (i=0 ; i<1024 ; i++)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 5;
		p->color = ramp1[0];
		p->alpha = 1.0f;
		p->ramp = rand()&3;
		p->type = (i & 1) ? pt_explode : pt_explode2;

		for (j=0 ; j<3 ; j++)
		{
			p->org[j] = org[j] + ((rand()%32)-16);
			p->vel[j] = (rand()%512)-256;
		}
	}
}


/*
===============
CL_ParticleExplosion2

NetQuake
===============
*/
void CL_ParticleExplosion2 (vec3_t org, int colorStart, int colorLength)
{
	int			i, j;
	int			colorMod = 0;
	cparticle_t	*p;
	
	for (i=0 ; i<1024 ; i++)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 0.3;
		p->alpha = 1.0f;
		p->color = colorStart + (colorMod % colorLength);
		colorMod++;

		p->type = pt_blob;
		for (j=0 ; j<3 ; j++)
		{
			p->org[j] = org[j] + ((rand()%32)-16);
			p->vel[j] = (rand()%512)-256;
		}
	}
}


/*
===============
CL_BlobExplosion
===============
*/
void CL_BlobExplosion (vec3_t org)
{
	int			i, j;
	cparticle_t	*p;
	
	for (i=0 ; i<1024 ; i++)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 1 + (rand()&8)*0.05;
		p->alpha = 1.0f;

		if (i & 1)
		{
			p->type = pt_blob;
			p->color = 66 + rand()%6;
		}
		else
		{
			p->type = pt_blob2;
			p->color = 150 + rand()%6;
		}

		for (j=0 ; j<3 ; j++)
		{
			p->org[j] = org[j] + ((rand()%32)-16);
			p->vel[j] = (rand()%512)-256;
		}
	}
}

/*
===============
CL_RunParticleEffect
===============
*/
void CL_RunParticleEffect (vec3_t org, vec3_t dir, int color, int count)
{
	int			scale;

	if (count > 130)
		scale = 3;
	else if (count > 20)
		scale = 2;
	else
		scale = 1;

	CL_RunParticleEffect2 (org, dir, color, count, scale);
}

/*
===============
CL_RunParticleEffect2
===============
*/
void CL_RunParticleEffect2 (vec3_t org, vec3_t dir, int color, int count, int scale)
{
	int			i, j;
	cparticle_t	*p;

	for (i=0 ; i<count ; i++)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 0.1*(rand()%5);
		p->color = (color&~7) + (rand()&7);
		p->alpha = 1.0f;
		p->type = pt_grav;
		for (j=0 ; j<3 ; j++)
		{
			p->org[j] = org[j] + scale*((rand()&15)-8);
			p->vel[j] = dir[j]*15;
		}
	}
}

/*
===============
CL_LavaSplash
===============
*/
void CL_LavaSplash (vec3_t org)
{
	int			i, j, k;
	cparticle_t	*p;
	float		vel;
	vec3_t		dir;

	for (i=-16 ; i<16 ; i++)
		for (j=-16 ; j<16 ; j++)
			for (k=0 ; k<1 ; k++)
			{
				if (!(p = new_particle()))
					return;
		
				p->die = cl.time + 2 + (rand()&31) * 0.02;
				p->color = 224 + (rand()&7);
				p->alpha = 1.0f;
				p->type = pt_grav;

				dir[0] = j*8 + (rand()&7);
				dir[1] = i*8 + (rand()&7);
				dir[2] = 256;
				
				p->org[0] = org[0] + dir[0];
				p->org[1] = org[1] + dir[1];
				p->org[2] = org[2] + (rand()&63);

				VectorNormalize (dir);
				vel = 50 + (rand()&63);
				VectorScale (dir, vel, p->vel);
			}
}

/*
===============
CL_TeleportSplash
===============
*/
void CL_TeleportSplash (vec3_t org)
{
	int			i, j, k;
	cparticle_t	*p;
	float		vel;
	vec3_t		dir;

	for (i=-16 ; i<16 ; i+=4)
		for (j=-16 ; j<16 ; j+=4)
			for (k=-24 ; k<32 ; k+=4)
			{
				if (!(p = new_particle()))
					return;
		
				p->die = cl.time + 0.2 + (rand()&7) * 0.02;
				p->color = 7 + (rand()&7);
				p->alpha = 1.0f;
				p->type = pt_grav;

				dir[0] = j*8;
				dir[1] = i*8;
				dir[2] = k*8;
				
				p->org[0] = org[0] + i + (rand()&3);
				p->org[1] = org[1] + j + (rand()&3);
				p->org[2] = org[2] + k + (rand()&3);
				
				VectorNormalize (dir);
				vel = 50 + (rand()&63);
				VectorScale (dir, vel, p->vel);
			}
}

/*
===============
CL_SlightBloodTrail
===============
*/
void CL_SlightBloodTrail (vec3_t start, vec3_t end, vec3_t trail_origin)
{
	int		j, num_particles;
	vec3_t	vec, point;
	float	len;
	cparticle_t	*p;

	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);
	VectorScale (vec, 6, vec);
	VectorCopy (start, point);

	num_particles = len / 6;
	if (!num_particles)
		return;

	for (; num_particles; num_particles--)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 2;
		p->type = pt_grav;
		p->color = 67 + (rand()&3);
		p->alpha = 1.0f;
		VectorClear (p->vel);
		for (j=0 ; j<3 ; j++)
			p->org[j] = point[j] + ((rand()%6)-3);

		VectorAdd (point, vec, point);
	}
	VectorCopy (point, trail_origin);
}

/*
===============
CL_BloodTrail
===============
*/
void CL_BloodTrail (vec3_t start, vec3_t end, vec3_t trail_origin)
{
	int		j, num_particles;
	vec3_t	vec, point;
	float	len;
	cparticle_t	*p;

	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);
	VectorScale (vec, 3, vec);
	VectorCopy (start, point);

	num_particles = len /3;
	if (!num_particles)
		return;

	for (; num_particles; num_particles--)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 2;
		p->type = pt_grav;
		p->color = 67 + (rand()&3);
		p->alpha = 1.0f;
		VectorClear (p->vel);
		for (j=0 ; j<3 ; j++)
			p->org[j] = point[j] + ((rand()%6)-3);

		VectorAdd (point, vec, point);
	}
	VectorCopy (point, trail_origin);
}

/*
===============
CL_VoorTrail
===============
*/
void CL_VoorTrail (vec3_t start, vec3_t end, vec3_t trail_origin)
{
	int		j, num_particles;
	vec3_t	vec, point;
	float	len;
	cparticle_t	*p;

	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);
	VectorScale (vec, 3, vec);
	VectorCopy (start, point);

	num_particles = len /3;
	if (!num_particles)
		return;

	for (; num_particles; num_particles--)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 2;
		p->color = 9*16 + 8 + (rand()&3);
		p->alpha = 1.0f;
		p->type = pt_static;
		p->die = cl.time + 0.3;
		VectorClear (p->vel);
		for (j=0 ; j<3 ; j++)
			p->org[j] = point[j] + ((rand()&15)-8);

		VectorAdd (point, vec, point);
	}
	VectorCopy (point, trail_origin);
}

/*
===============
CL_GrenadeTrail
===============
*/
void CL_GrenadeTrail (vec3_t start, vec3_t end, vec3_t trail_origin)
{
	int		j, num_particles;
	vec3_t	vec, point;
	float	len;
	cparticle_t	*p;

	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);
	VectorScale (vec, 3, vec);
	VectorCopy (start, point);

	num_particles = len / 3;
	if (!num_particles)
		return;

	for (; num_particles; num_particles--)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 2;
		p->ramp = (rand()&3) + 2;
		p->color = ramp3[(int)p->ramp];
		p->alpha = 1.0f;
		p->type = pt_fire;
		VectorClear (p->vel);
		for (j=0 ; j<3 ; j++)
			p->org[j] = point[j] + ((rand()%6)-3);

		VectorAdd (point, vec, point);
	}
	VectorCopy (point, trail_origin);
}

/*
===============
CL_RocketTrail
===============
*/
void CL_RocketTrail (vec3_t start, vec3_t end, vec3_t trail_origin)
{
	int		j, num_particles;
	vec3_t	vec, point;
	float	len;
	cparticle_t	*p;

	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);
	VectorScale (vec, 3, vec);
	VectorCopy (start, point);

	num_particles = len /3;
	if (!num_particles)
		return;

	for (; num_particles; num_particles--)
	{
		if (!(p = new_particle()))
			return;

		p->die = cl.time + 2;
		p->ramp = (rand()&3);
		p->color = ramp3[(int)p->ramp];
		p->alpha = 1.0f;
		p->type = pt_fire;
		VectorClear (p->vel);
		for (j=0 ; j<3 ; j++)
			p->org[j] = point[j] + ((rand()%6)-3);

		VectorAdd (point, vec, point);
	}
	VectorCopy (point, trail_origin);
}

/*
===============
CL_TracerTrail
===============
*/
void CL_TracerTrail (vec3_t start, vec3_t end, vec3_t trail_origin, int color)
{
	int		num_particles;
	vec3_t	vec, point;
	float	len;
	cparticle_t	*p;
	static int tracercount;

	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);
	VectorScale (vec, 3, vec);
	VectorCopy (start, point);

	num_particles = len /3;
	if (!num_particles)
		return;

	for (; num_particles; num_particles--)
	{
		if (!(p = new_particle()))
			return;
		
		p->die = cl.time + 0.5;
		p->type = pt_static;
		p->color = color + ((tracercount&4)<<1);
		p->alpha = 1.0f;

		tracercount++;

		VectorCopy (point, p->org);
		if (tracercount & 1)
		{
			p->vel[0] = 30*vec[1];
			p->vel[1] = 30*-vec[0];
		}
		else
		{
			p->vel[0] = 30*-vec[1];
			p->vel[1] = 30*vec[0];
		}

		p->vel[2] = 0;
		VectorAdd (point, vec, point);
	}
	VectorCopy (point, trail_origin);
}


float crand(void)
{
	return (rand()&32767)* (2.0/32767) - 1;
}

float frand(void)
{
	return (rand()&32767)* (1.0/32767);
}


/*
===============
CL_RailTrail
===============
*/
void CL_RailTrail (vec3_t start, vec3_t end, int color)
{
	vec3_t		move;
	vec3_t		vec;
	float		len;
	int			j;
	cparticle_t	*p;
	float		dec;
	vec3_t		right, up;
	int			i;
	float		d, c, s;
	vec3_t		dir;
//	byte		clr = 208;	// blue

	VectorCopy (start, move);
	VectorSubtract (end, start, vec);
	len = VectorNormalize (vec);

	MakeNormalVectors (vec, right, up);

	// blue spiral
	for (i=0 ; i<len ; i++)
	{
		if (!free_particles)
			return;

		p = free_particles;
		free_particles = p->next;
		p->next = active_particles;
		active_particles = p;
		
		p->type = pt_rail;

		//p->time = cl.time;
		p->die = cl.time + 2;

		d = i * 0.1;
		c = cos(d);
		s = sin(d);

		VectorScale (right, c, dir);
		VectorMA (dir, s, up, dir);

		p->alpha = 1.0;
		p->alphavel = -1.0 / (1+frand()*0.2);
		p->color = color + (rand()&7);
		for (j=0 ; j<3 ; j++)
		{
			p->org[j] = move[j] + dir[j]*3;
			p->vel[j] = dir[j]*6;
		}

		VectorAdd (move, vec, move);
	}

	dec = 1.5;		// Q2 uses 0.75, but I don't want that many particles
	VectorScale (vec, dec, vec);
	VectorCopy (start, move);

	// white core
	while (len > 0)
	{
		len -= dec;

		if (!free_particles)
			return;
		p = free_particles;
		free_particles = p->next;
		p->next = active_particles;
		active_particles = p;

		p->type = pt_rail;

//		p->time = cl.time;
		p->die = cl.time + 2;	// will die when alpha runs out

		p->alpha = 1.0;
		p->alphavel = -1.0 / (0.6+frand()*0.2);
		p->color = 0x0 + (rand()&15);

		for (j=0 ; j<3 ; j++)
		{
			p->org[j] = move[j] + crand()* 2;	// Q2 has crand()* 3
			p->vel[j] = crand()*3;
		}

		VectorAdd (move, vec, move);
	}

}


/*
===============
CL_EntityParticles
===============
*/
#define NUMVERTEXNORMALS	162
extern float	r_avertexnormals[NUMVERTEXNORMALS][3];	// FIXME, links to renderer
vec3_t	avelocities[NUMVERTEXNORMALS];
void CL_EntityParticles (vec3_t org)
{
	int			i;
	cparticle_t	*p;
	float		angle;
	float		sr, sp, sy, cr, cp, cy;
	vec3_t		forward;
	const float		dist = 64;
	const float		beamlength = 16;

if (!avelocities[0][0])
{
	for (i=0 ; i<NUMVERTEXNORMALS*3 ; i++)
		avelocities[0][i] = (rand()&255) * 0.01;
	}

	for (i=0 ; i<NUMVERTEXNORMALS ; i++)
	{
		if (!(p = new_particle()))
			return;

		angle = cl.time * avelocities[i][0];
		sy = sin(angle);
		cy = cos(angle);
		angle = cl.time * avelocities[i][1];
		sp = sin(angle);
		cp = cos(angle);
		angle = cl.time * avelocities[i][2];
		sr = sin(angle);
		cr = cos(angle);

		forward[0] = cp*cy;
		forward[1] = cp*sy;
		forward[2] = -sp;

		p->die = cl.time + 0.01;
		p->color = 0x6f;
		p->type = pt_explode;

		p->org[0] = org[0] + r_avertexnormals[i][0]*dist + forward[0]*beamlength;
		p->org[1] = org[1] + r_avertexnormals[i][1]*dist + forward[1]*beamlength;
		p->org[2] = org[2] + r_avertexnormals[i][2]*dist + forward[2]*beamlength;
	}
}


/*
===============
CL_LinkParticles
===============
*/
void CL_LinkParticles (void)
{
	cparticle_t		*p, *kill;
	float			grav;
	int				i;
	float			time1, time2, time3;
	float			dvel;
	float			frametime;

	frametime = cls.frametime;
	time1 = frametime * 5;
	time2 = frametime * 10; // 15;
	time3 = frametime * 15;
	grav = frametime * 800 * 0.05;
	dvel = 4 * frametime;

	for ( ;; ) 
	{
		kill = active_particles;
		if (kill && kill->die < cl.time)
		{
			active_particles = kill->next;
			kill->next = free_particles;
			free_particles = kill;
			continue;
		}
		break;
	}

	for (p=active_particles ; p ; p=p->next)
	{
		for ( ;; )
		{
			kill = p->next;
			if (kill && kill->die < cl.time)
			{
				p->next = kill->next;
				kill->next = free_particles;
				free_particles = kill;
				continue;
			}
			break;
		}

		V_AddParticle (p->org, p->color, p->alpha);

		p->org[0] += p->vel[0] * frametime;
		p->org[1] += p->vel[1] * frametime;
		p->org[2] += p->vel[2] * frametime;

		switch (p->type)
		{
			case pt_static:
				break;

			case pt_fire:
				p->ramp += time1;
				if (p->ramp >= 6)
					p->die = -1;
				else
				{
					p->color = ramp3[(int)p->ramp];
					p->alpha = (6-p->ramp)/6;
				}
				p->vel[2] += grav;
				break;

			case pt_explode:
				p->ramp += time2;
				if (p->ramp >=8)
					p->die = -1;
				else
					p->color = ramp1[(int)p->ramp];
				for (i=0 ; i<3 ; i++)
					p->vel[i] += p->vel[i]*dvel;
				p->vel[2] -= grav;
				break;

			case pt_explode2:
				p->ramp += time3;
				if (p->ramp >=8)
					p->die = -1;
				else
					p->color = ramp2[(int)p->ramp];
				for (i=0 ; i<3 ; i++)
					p->vel[i] -= p->vel[i]*frametime;
				p->vel[2] -= grav;
				break;

			case pt_blob:
				for (i=0 ; i<3 ; i++)
					p->vel[i] += p->vel[i]*dvel;
				p->vel[2] -= grav;
				break;

			case pt_blob2:
				for (i=0 ; i<2 ; i++)
					p->vel[i] -= p->vel[i]*dvel;
				p->vel[2] -= grav;
				break;

			case pt_grav:
				p->vel[2] -= grav;
				break;

			case pt_rail:
				p->alpha += p->alphavel * cls.frametime;
				if (p->alpha <= 0)
					p->die = 0;	// die next frame :)
				break;
		}
	}
}

//============================================================

static cdlight_t	cl_dlights[MAX_DLIGHTS];

// sent to the renderer
int				cl_numvisdlights;
dlight_t		cl_visdlights[MAX_DLIGHTS];

/*
===============
CL_AllocDlight

===============
*/
cdlight_t *CL_AllocDlight (int key)
{
	int		i;
	cdlight_t	*dl;

// first look for an exact key match
	if (key)
	{
		dl = cl_dlights;
		for (i=0 ; i<MAX_DLIGHTS ; i++, dl++)
		{
			if (dl->key == key)
				goto init;
		}
	}

// then look for anything else
	dl = cl_dlights;
	for (i=0 ; i<MAX_DLIGHTS ; i++, dl++)
	{
		if (dl->die < cl.time)
			goto init;
	}

	dl = &cl_dlights[0];
init:
	memset (dl, 0, sizeof(*dl));
	dl->key = key;
	dl->starttime = cl.time;
	return dl;
}

/*
===============
CL_NewDlight
===============
*/
void CL_NewDlight (int key, vec3_t origin, float radius, float time, dlighttype_t type)
{
	cdlight_t	*dl;

	dl = CL_AllocDlight (key);
	VectorCopy (origin, dl->origin);
	dl->radius = radius;
	dl->die = cl.time + time;
	dl->type = type;
}


/*
===============
CL_LinkDlights

===============
*/
void CL_LinkDlights (void)
{
	int			i;
	cdlight_t	*dl;
	float		radius;

	dl = cl_dlights;
	for (i=0 ; i<MAX_DLIGHTS ; i++, dl++)
	{
		if (dl->die < cl.time)
			continue;

		radius = dl->radius - (cl.time - dl->starttime) * dl->decay;

		if (radius <= 0) {
			dl->die = 0;
			continue;
		}

		V_AddDlight(dl->key, dl->origin, radius, dl->minlight, dl->type);
	}
}

/*
===============
CL_ClearDlights

===============
*/
void CL_ClearDlights (void)
{
	memset (cl_dlights, 0, sizeof(cl_dlights));
}
