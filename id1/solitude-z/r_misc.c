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
// r_misc.c

#include "quakedef.h"
#include "r_local.h"
#include "rc_image.h"
#include <time.h>


typedef struct r_translation_s {
	int topcolor;
	int bottomcolor;
	char skinname[32];
	byte colormap[VID_GRADES*256];
	struct skin_s *skin;
} r_translation_t;

static r_translation_t r_translations[MAX_CLIENTS];
static struct skin_s *r_baseskin;
static char cur_baseskin[32];

// dest must point to a VID_GRADES*256-byte buffer
static void BuildTranslation (int topcolor, int bottomcolor, byte *dest) 
{
		int		i, j;
		int		top, bottom;
		byte	*source;

		source = r_colormap;
		memcpy (dest, r_colormap, VID_GRADES*256);
		top = topcolor;
		if (top > 13 || top < 0)
			top = 13;
		top *= 16;
		bottom = bottomcolor;
		if (bottom > 13 || bottom < 0)
			bottom = 13;
		bottom *= 16;

		for (i=0 ; i<VID_GRADES ; i++, dest += 256, source+=256)
		{
			if (top < 128)	// the artists made some backwards ranges.  sigh.
				memcpy (dest + TOP_RANGE, source + top, 16);
			else
				for (j=0 ; j<16 ; j++)
					dest[TOP_RANGE+j] = source[top+15-j];
					
			if (bottom < 128)
				memcpy (dest + BOTTOM_RANGE, source + bottom, 16);
			else
				for (j=0 ; j<16 ; j++)
					dest[BOTTOM_RANGE+j] = source[bottom+15-j];		
		}
}


byte *R_GetColormap (int colormap)
{
	r_translation_t *cur;
	translation_info_t *new;

	assert (colormap >= 0 && colormap <= MAX_CLIENTS);

	if (colormap == 0)
		return r_colormap;

	cur = r_translations + (colormap - 1);
	new = r_refdef2.translations + (colormap - 1);

	// rebuild if necessary
	if (new->topcolor != cur->topcolor
		|| new->bottomcolor != cur->bottomcolor)
	{
		cur->topcolor = new->topcolor;
		cur->bottomcolor = new->bottomcolor;
		BuildTranslation (new->topcolor,
			new->bottomcolor, cur->colormap);
//		Com_Printf ("updated translation %i\n", colormap);
	}

	return cur->colormap;
}

// called on startup and every time gamedir changes
void R_FlushTranslations (void)
{
	int i;

	Skin_Flush ();
	for (i = 0; i < MAX_CLIENTS; i++) {
		r_translations[i].topcolor = -1; // this will force a rebuild
		r_translations[i].skinname[0] = 0;
		r_translations[i].skin = NULL;
	}
	r_baseskin = NULL;
	cur_baseskin[0] = 0;
}


byte *R_GetSkin (int colormap)
{
	r_translation_t *cur;
	translation_info_t *new;
	byte *data;

	assert (colormap >= 0 && colormap <= MAX_CLIENTS);
	if (!colormap)
		return NULL;

	cur = &r_translations[colormap - 1];
	new = &r_refdef2.translations[colormap - 1];

	if (strcmp(new->skinname, cur->skinname) || !new->skinname[0]) {
		strlcpy (cur->skinname, new->skinname, sizeof(cur->skinname));

//Com_Printf ("R_GetSkin: %s\n", r_translations[colormap - 1].skinname);
		if (!cur->skinname[0])
			return NULL;
		Skin_Find (r_translations[colormap - 1].skinname, &cur->skin);
	}

	data = Skin_Cache (cur->skin);
	if (!data) {
		if (r_refdef2.baseskin[0] && strcmp(r_refdef2.baseskin, cur->skinname)) {
			if (strcmp(cur_baseskin, r_refdef2.baseskin)) {
				strlcpy (cur_baseskin, r_refdef2.baseskin, sizeof(cur_baseskin));
				if (!cur_baseskin[0])
					return NULL;
				Skin_Find (r_refdef2.baseskin, &r_baseskin);
			}
			data = Skin_Cache (r_baseskin);
		}
	}

	return data;
}

/*
===============
R_CheckVariables
===============
*/
void R_CheckVariables (void)
{
	static qbool	oldbright = false;
	qbool			fullbright;

	fullbright = (r_fullbright.value && r_refdef2.allow_cheats);
	if (fullbright != oldbright) {
		oldbright = r_fullbright.value;
		D_FlushCaches ();	// so all lighting changes
	}
}


/*
============
Show

Debugging use
============
*/
void Show (void)
{
	vrect_t	vr;

	vr.x = vr.y = 0;
	vr.width = vid.width;
	vr.height = vid.height;
	vr.pnext = NULL;
	VID_Update (&vr);
}

/*
====================
R_TimeRefresh_f

For program optimization
====================
*/
void R_TimeRefresh_f (void)
{
	int			i;
	float		start, stop, time;
	int			startangle;
	vrect_t		vr;

	if (cls.state != ca_active)
		return;

	startangle = r_refdef2.viewangles[1];
	
	start = Sys_DoubleTime ();
	for (i=0 ; i<128 ; i++)
	{
		r_refdef2.viewangles[1] = i/128.0*360.0;

		VID_LockBuffer ();

		R_RenderView ();

		VID_UnlockBuffer ();

		vr.x = r_refdef.vrect.x;
		vr.y = r_refdef.vrect.y;
		vr.width = r_refdef.vrect.width;
		vr.height = r_refdef.vrect.height;
		vr.pnext = NULL;
		VID_Update (&vr);
	}
	stop = Sys_DoubleTime ();
	time = stop-start;
	Com_Printf ("%f seconds (%f fps)\n", time, 128/time);
	
	r_refdef2.viewangles[1] = startangle;
}

/*
================
R_LineGraph

Only called by R_DisplayTime
================
*/
void R_LineGraph (int x, int y, int h)
{
	int		i;
	byte	*dest;
	int		s;
	int		color;

// FIXME: should be disabled on no-buffer adapters, or should be in the driver
	
//	x += r_refdef.vrect.x;
//	y += r_refdef.vrect.y;
	
	dest = vid.buffer + vid.rowbytes*y + x;
	
	s = r_graphheight.value;

	if (h == 10000)
		color = 0x6f;	// yellow
	else if (h == 9999)
		color = 0x4f;	// red
	else if (h == 9998)
		color = 0xd0;	// blue
	else
		color = 0xff;	// pink

	if (h>s)
		h = s;
	
	for (i=0 ; i<h ; i++, dest -= vid.rowbytes*2)
	{
		dest[0] = color;
//		*(dest-vid.rowbytes) = 0x30;
	}
#if 0
	for ( ; i<s ; i++, dest -= vid.rowbytes*2)
	{
		dest[0] = 0x30;
		*(dest-vid.rowbytes) = 0x30;
	}
#endif
}

/*
==============
R_TimeGraph

Performance monitoring tool
==============
*/
#define	MAX_TIMINGS		100
extern float mouse_x, mouse_y;
int		graphval;
void R_TimeGraph (void)
{
	static	int		timex;
	int		a;
	float	r_time2;
	static byte	r_timings[MAX_TIMINGS];
	int		x;
	
	r_time2 = Sys_DoubleTime ();

	a = (r_time2-r_time1)/0.01;
//a = fabs(mouse_y * 0.05);
//a = (int)((r_refdef2.vieworg[2] + 1024)/1)%(int)r_graphheight.value;
//a = (int)((pmove.velocity[2] + 500)/10);
//a = fabs(velocity[0])/20;
//a = ((int)fabs(origin[0])/8)%20;
//a = (cl.idealpitch + 30)/5;
//a = (int)(cl.simangles[YAW] * 64/360) & 63;
a = graphval;

	r_timings[timex] = a;
	a = timex;

	if (r_refdef.vrect.width <= MAX_TIMINGS)
		x = r_refdef.vrect.width-1;
	else
		x = r_refdef.vrect.width -
				(r_refdef.vrect.width - MAX_TIMINGS)/2;
	do
	{
		R_LineGraph (x, r_refdef.vrect.height-2, r_timings[a]);
		if (x==0)
			break;		// screen too small to hold entire thing
		x--;
		a--;
		if (a == -1)
			a = MAX_TIMINGS-1;
	} while (a != timex);

	timex = (timex+1)%MAX_TIMINGS;
}

/*
==============
R_NetGraph
==============
*/
void R_NetGraph (void)
{
	extern cvar_t	r_netgraph;
	int		a, x, y, y2, w, i;
	int		lost;
	char	st[80];

	if (vid.width - 16 <= NET_TIMINGS)
		w = vid.width - 16;
	else
		w = NET_TIMINGS;

	x =	0;
	y = vid.height - sb_lines - 24 - (int)r_graphheight.value*2 - 2;

	if (r_netgraph.value != 2 && r_netgraph.value != 3)
		Draw_TextBox (x, y, (w+7)/8, ((int)r_graphheight.value*2+7)/8 + 1);

	y2 = y + 8;
	y = vid.height - sb_lines - 8 - 2;

	x = 8;
	lost = CL_CalcNet();
	for (a=NET_TIMINGS-w ; a<w ; a++)
	{
		i = (cls.netchan.outgoing_sequence-a) & NET_TIMINGSMASK;
		R_LineGraph (x+w-1-a, y, packet_latency[i]);
	}

	if (r_netgraph.value != 3) {
		sprintf(st, "%3i%% packet loss", lost);
		R_DrawString (8, y2, st);
	}
}

/*
==============
R_ZGraph
==============
*/
void R_ZGraph (void)
{
	int		a, x, w, i;
	static	int	height[256];

	if (r_refdef.vrect.width <= 256)
		w = r_refdef.vrect.width;
	else
		w = 256;

	height[r_framecount&255] = ((int)r_origin[2]) & 31;

	x = 0;
	for (a=0 ; a<w ; a++)
	{
		i = (r_framecount-a) & 255;
		R_LineGraph (x+w-1-a, r_refdef.vrect.height-2, height[i]);
	}
}

/*
=============
R_PrintTimes
=============
*/
void R_PrintTimes (void)
{
	float	r_time2;
	float		ms;

	r_time2 = Sys_DoubleTime ();

	ms = 1000* (r_time2 - r_time1);
	
	Com_Printf ("%5.1f ms %3i/%3i/%3i poly %3i surf\n",
				ms, c_faceclip, r_polycount, r_drawnpolycount, c_surf);
	c_surf = 0;
}


/*
=============
R_PrintDSpeeds
=============
*/
void R_PrintDSpeeds (void)
{
	float	ms, dp_time, r_time2, rw_time, db_time, se_time, de_time, dv_time;

	r_time2 = Sys_DoubleTime ();

	dp_time = (dp_time2 - dp_time1) * 1000;
	rw_time = (rw_time2 - rw_time1) * 1000;
	db_time = (db_time2 - db_time1) * 1000;
	se_time = (se_time2 - se_time1) * 1000;
	de_time = (de_time2 - de_time1) * 1000;
	dv_time = (dv_time2 - dv_time1) * 1000;
	ms = (r_time2 - r_time1) * 1000;

	Com_Printf ("%3i %4.1fp %3iw %4.1fb %3is %4.1fe %4.1fv\n",
				(int)ms, dp_time, (int)rw_time, db_time, (int)se_time, de_time,
				dv_time);
}


/*
=============
R_PrintAliasStats
=============
*/
void R_PrintAliasStats (void)
{
	Com_Printf ("%3i polygon model drawn\n", r_amodels_drawn);
}


void WarpPalette (void)
{
	int		i,j;
	byte	newpalette[768];
	int		basecolor[3];
	
	basecolor[0] = 130;
	basecolor[1] = 80;
	basecolor[2] = 50;

// pull the colors halfway to bright brown
	for (i=0 ; i<256 ; i++)
	{
		for (j=0 ; j<3 ; j++)
		{
			newpalette[i*3+j] = (host_basepal[i*3+j] + basecolor[j])/2;
		}
	}
	
	VID_ShiftPalette (newpalette);
}


/*
===================
R_TransformFrustum
===================
*/
void R_TransformFrustum (void)
{
	int		i;
	vec3_t	v, v2;
	
	for (i=0 ; i<4 ; i++)
	{
		v[0] = screenedge[i].normal[2];
		v[1] = -screenedge[i].normal[0];
		v[2] = screenedge[i].normal[1];

		v2[0] = v[1]*vright[0] + v[2]*vup[0] + v[0]*vpn[0];
		v2[1] = v[1]*vright[1] + v[2]*vup[1] + v[0]*vpn[1];
		v2[2] = v[1]*vright[2] + v[2]*vup[2] + v[0]*vpn[2];

		VectorCopy (v2, view_clipplanes[i].normal);

		view_clipplanes[i].dist = DotProduct (modelorg, v2);
	}
}


#if !id386

/*
================
TransformVector
================
*/
void TransformVector (vec3_t in, vec3_t out)
{
	out[0] = DotProduct(in,vright);
	out[1] = DotProduct(in,vup);
	out[2] = DotProduct(in,vpn);		
}

#endif



/*
===============
R_SetUpFrustumIndexes
===============
*/
void R_SetUpFrustumIndexes (void)
{
	int		i, j, *pindex;

	pindex = r_frustum_indexes;

	for (i=0 ; i<4 ; i++)
	{
		for (j=0 ; j<3 ; j++)
		{
			if (view_clipplanes[i].normal[j] < 0)
			{
				pindex[j] = j;
				pindex[j+3] = j+3;
			}
			else
			{
				pindex[j] = j+3;
				pindex[j+3] = j;
			}
		}

	// FIXME: do just once at start
		pfrustum_indexes[i] = pindex;
		pindex += 6;
	}
}


/*
===============
R_ViewChanged

Called every time the vid structure or r_refdef changes.
Guaranteed to be called before the first refresh
===============
*/
void R_ViewChanged (float aspect)
{
	int		i;
	float	res_scale;
#if id386
	extern void		*colormap;
#endif
	extern cvar_t	r_aliastransbase, r_aliastransadj;

	r_refdef.horizontalFieldOfView = 2.0 * tan (r_refdef2.fov_x/360*M_PI);
	r_refdef.fvrectx = (float)r_refdef.vrect.x;
	r_refdef.fvrectx_adj = (float)r_refdef.vrect.x - 0.5;
	r_refdef.vrect_x_adj_shift20 = (r_refdef.vrect.x<<20) + (1<<19) - 1;
	r_refdef.fvrecty = (float)r_refdef.vrect.y;
	r_refdef.fvrecty_adj = (float)r_refdef.vrect.y - 0.5;
	r_refdef.vrectright = r_refdef.vrect.x + r_refdef.vrect.width;
	r_refdef.vrectright_adj_shift20 = (r_refdef.vrectright<<20) + (1<<19) - 1;
	r_refdef.fvrectright = (float)r_refdef.vrectright;
	r_refdef.fvrectright_adj = (float)r_refdef.vrectright - 0.5;
	r_refdef.vrectrightedge = (float)r_refdef.vrectright - 0.99;
	r_refdef.vrectbottom = r_refdef.vrect.y + r_refdef.vrect.height;
	r_refdef.fvrectbottom = (float)r_refdef.vrectbottom;
	r_refdef.fvrectbottom_adj = (float)r_refdef.vrectbottom - 0.5;

	r_refdef.aliasvrect.x = (int)(r_refdef.vrect.x * r_aliasuvscale);
	r_refdef.aliasvrect.y = (int)(r_refdef.vrect.y * r_aliasuvscale);
	r_refdef.aliasvrect.width = (int)(r_refdef.vrect.width * r_aliasuvscale);
	r_refdef.aliasvrect.height = (int)(r_refdef.vrect.height * r_aliasuvscale);
	r_refdef.aliasvrectright = r_refdef.aliasvrect.x +
			r_refdef.aliasvrect.width;
	r_refdef.aliasvrectbottom = r_refdef.aliasvrect.y +
			r_refdef.aliasvrect.height;

	pixelAspect = aspect;
	xOrigin = r_refdef.xOrigin;
	yOrigin = r_refdef.yOrigin;
	
	screenAspect = r_refdef.vrect.width*pixelAspect /
			r_refdef.vrect.height;
// 320*200 1.0 pixelAspect = 1.6 screenAspect
// 320*240 1.0 pixelAspect = 1.3333 screenAspect
// proper 320*200 pixelAspect = 0.8333333

	verticalFieldOfView = r_refdef.horizontalFieldOfView / screenAspect;

// values for perspective projection
// if math were exact, the values would range from 0.5 to to range+0.5
// hopefully they wll be in the 0.000001 to range+.999999 and truncate
// the polygon rasterization will never render in the first row or column
// but will definately render in the [range] row and column, so adjust the
// buffer origin to get an exact edge to edge fill
	xcenter = ((float)r_refdef.vrect.width * XCENTERING) +
			r_refdef.vrect.x - 0.5;
	aliasxcenter = xcenter * r_aliasuvscale;
	ycenter = ((float)r_refdef.vrect.height * YCENTERING) +
			r_refdef.vrect.y - 0.5;
	aliasycenter = ycenter * r_aliasuvscale;

	xscale = r_refdef.vrect.width / r_refdef.horizontalFieldOfView;
	aliasxscale = xscale * r_aliasuvscale;
	xscaleinv = 1.0 / xscale;
	yscale = xscale * pixelAspect;
	aliasyscale = yscale * r_aliasuvscale;
	yscaleinv = 1.0 / yscale;
	xscaleshrink = (r_refdef.vrect.width-6)/r_refdef.horizontalFieldOfView;
	yscaleshrink = xscaleshrink*pixelAspect;

// left side clip
	screenedge[0].normal[0] = -1.0 / (xOrigin*r_refdef.horizontalFieldOfView);
	screenedge[0].normal[1] = 0;
	screenedge[0].normal[2] = 1;
	screenedge[0].type = PLANE_ANYZ;
	
// right side clip
	screenedge[1].normal[0] =
			1.0 / ((1.0-xOrigin)*r_refdef.horizontalFieldOfView);
	screenedge[1].normal[1] = 0;
	screenedge[1].normal[2] = 1;
	screenedge[1].type = PLANE_ANYZ;
	
// top side clip
	screenedge[2].normal[0] = 0;
	screenedge[2].normal[1] = -1.0 / (yOrigin*verticalFieldOfView);
	screenedge[2].normal[2] = 1;
	screenedge[2].type = PLANE_ANYZ;
	
// bottom side clip
	screenedge[3].normal[0] = 0;
	screenedge[3].normal[1] = 1.0 / ((1.0-yOrigin)*verticalFieldOfView);
	screenedge[3].normal[2] = 1;	
	screenedge[3].type = PLANE_ANYZ;
	
	for (i=0 ; i<4 ; i++)
		VectorNormalize (screenedge[i].normal);

	res_scale = sqrt ((double)(r_refdef.vrect.width * r_refdef.vrect.height) /
			          (320.0 * 152.0)) *
			(2.0 / r_refdef.horizontalFieldOfView);
	r_aliastransition = r_aliastransbase.value * res_scale;
	r_resfudge = r_aliastransadj.value * res_scale;

// TODO: collect 386-specific code in one place
#if id386
	if (r_pixbytes == 1)
	{
		Sys_MakeCodeWriteable ((long)R_Surf8Start,
						     (long)R_Surf8End - (long)R_Surf8Start);
		colormap = r_colormap;
		R_Surf8Patch ();
	}
	else
	{
		Sys_MakeCodeWriteable ((long)R_Surf16Start,
						     (long)R_Surf16End - (long)R_Surf16Start);
		colormap = r_colormap16;
		R_Surf16Patch ();
	}
#endif	// id386

	D_ViewChanged ();
}



/*
===============
R_SetupFrame
===============
*/
void R_SetupFrame (void)
{
	int				edgecount;
	float			w, h;
	qbool			viewchanged;
	static refdef2_t	r_oldrefdef2;
	static float oldfov_x, oldfov_y;
	static pixel_t *old_vid_buffer;

	if (r_numsurfs.value)
	{
		if ((surface_p - surfaces) > r_maxsurfsseen)
			r_maxsurfsseen = surface_p - surfaces;

		Com_Printf ("Used %d of %d surfs; %d max\n", surface_p - surfaces,
				surf_max - surfaces, r_maxsurfsseen);
	}

	if (r_numedges.value)
	{
		edgecount = edge_p - r_edges;

		if (edgecount > r_maxedgesseen)
			r_maxedgesseen = edgecount;

		Com_Printf ("Used %d of %d edges; %d max\n", edgecount,
				r_numallocatededges, r_maxedgesseen);
	}

	r_refdef.ambientlight = r_refdef2.allow_cheats ? min((int)r_ambient.value, 0) : 0;

	R_CheckVariables ();
	
	R_AnimateLight ();

	r_framecount++;

// build the transformation matrix for the given view angles
	VectorCopy (r_refdef2.vieworg, modelorg);
	VectorCopy (r_refdef2.vieworg, r_origin);

	AngleVectors (r_refdef2.viewangles, vpn, vright, vup);

// current viewleaf
	r_oldviewleaf = r_viewleaf;
	r_viewleaf = Mod_PointInLeaf (r_origin, r_worldmodel);

	r_dowarpold = r_dowarp;
	r_dowarp = r_waterwarp.value && (r_viewleaf->contents <= CONTENTS_WATER);

	viewchanged = false;

	if (r_refdef2.vrect.x != r_oldrefdef2.vrect.x ||
		r_refdef2.vrect.y != r_oldrefdef2.vrect.y ||
		r_refdef2.vrect.width != r_oldrefdef2.vrect.width ||
		r_refdef2.vrect.height != r_oldrefdef2.vrect.height ||
		r_refdef2.fov_x != oldfov_x || r_refdef2.fov_y != oldfov_y ||
		r_dowarp != r_dowarpold ||
		vid.buffer != old_vid_buffer)
	{
		viewchanged = true;
	}

	r_oldrefdef2 = r_refdef2;
	oldfov_x = r_refdef2.fov_x;
	oldfov_y = r_refdef2.fov_y;
	old_vid_buffer = vid.buffer;

	if (viewchanged)
	{
		if (r_dowarp)
		{
			if ((vid.width <= WARP_WIDTH) &&
				(vid.height <= WARP_HEIGHT))
			{
				r_refdef.vrect.x = 0;
				r_refdef.vrect.y = 0;
				r_refdef.vrect.width = vid.width;
				r_refdef.vrect.height = vid.height;

				R_ViewChanged (vid.aspect);
			}
			else
			{
				w = vid.width;
				h = vid.height;

				if (w > WARP_WIDTH)
				{
					h *= (float)WARP_WIDTH / w;
					w = WARP_WIDTH;
				}

				if (h > WARP_HEIGHT)
				{
					h = WARP_HEIGHT;
					w *= (float)WARP_HEIGHT / h;
				}

				r_refdef.vrect.x = 0;
				r_refdef.vrect.y = 0;
				r_refdef.vrect.width = (int)w;
				r_refdef.vrect.height = (int)h;

				R_ViewChanged (vid.aspect /* * (h / w) *
								 ((float)vid.width / (float)vid.height)*/);
			}
		}
		else
		{
			r_refdef.vrect = r_refdef2.vrect;

			R_ViewChanged (vid.aspect);
		}
	}

// start off with just the four screen edge clip planes
	R_TransformFrustum ();

// save base values
	VectorCopy (vpn, base_vpn);
	VectorCopy (vright, base_vright);
	VectorCopy (vup, base_vup);
	VectorCopy (modelorg, base_modelorg);

	R_SetSkyFrame ();

	R_SetUpFrustumIndexes ();

	r_cache_thrash = false;

// clear frame counts
	c_faceclip = 0;
	d_spanpixcount = 0;
	r_polycount = 0;
	r_drawnpolycount = 0;
	r_wholepolycount = 0;
	r_amodels_drawn = 0;
	r_outofsurfaces = 0;
	r_outofedges = 0;

	D_SetupFrame ();
}

void R_32To8bit (unsigned int *in, int inwidth, int inheight, byte *out, int outwidth, int outheight)
{
	if (!d_15to8table_made) {
		R_Build15to8table ();
		d_15to8table_made = true;
	}

	assert(outwidth <= inwidth && outheight <= inheight);

	if (inwidth == outwidth && inheight == outheight) {
		int	i;
		for (i = inwidth*inheight; i; i--, in++)
			*out++ = d_15to8table[((*in & 0xf8)>>3) +	((*in & 0xf800)>>6) + ((*in & 0xf80000)>>9)];
	}
	else
	{	// scale down
		int i, j, pix;
		unsigned frac, fracstep;
		unsigned int *inrow;

		fracstep = (inwidth * 0x10000) / outwidth;
		for (i = 0; i < outheight; i++)
		{
			inrow = (unsigned int *)in + inwidth*(i*inheight/outheight);
			frac = fracstep >> 1;
			for (j = outwidth >> 2 ; j ; j--)
			{
				pix = inrow[frac >> 16]; frac += fracstep;
				out[0] = d_15to8table[((pix & 0xf8)>>3) + ((pix & 0xf800)>>6) + ((pix & 0xf80000)>>9)];
				pix = inrow[frac >> 16]; frac += fracstep;
				out[1] = d_15to8table[((pix & 0xf8)>>3) + ((pix & 0xf800)>>6) + ((pix & 0xf80000)>>9)];
				pix = inrow[frac >> 16]; frac += fracstep;
				out[2] = d_15to8table[((pix & 0xf8)>>3) + ((pix & 0xf800)>>6) + ((pix & 0xf80000)>>9)];
				pix = inrow[frac >> 16]; frac += fracstep;
				out[3] = d_15to8table[((pix & 0xf8)>>3) + ((pix & 0xf800)>>6) + ((pix & 0xf80000)>>9)];
				out += 4;
			}
			for (j = outwidth & 3 ; j ; j--)
			{
				pix = inrow[frac >> 16]; frac += fracstep;
				*out++ = d_15to8table[((pix & 0xf8)>>3) + ((pix & 0xf800)>>6) + ((pix & 0xf80000)>>9)];
			}
		}
	}
}


/* 
============================================================================== 
 
						SCREEN SHOTS 
 
============================================================================== 
*/ 


/* 
================== 
R_ScreenShot_f
================== 
*/  
void R_ScreenShot_f (void) 
{ 
	int			i; 
	char		pcxname[MAX_OSPATH]; 
	char		checkname[MAX_OSPATH];
	extern byte	current_pal[768];	// Tonik
	FILE		*f;
	byte		*pcxdata;
	int			pcxsize;

	if (Cmd_Argc() == 2) {
		strlcpy (pcxname, Cmd_Argv(1), sizeof(pcxname));
		COM_ForceExtension (pcxname, ".pcx");
	}
	else
	{
		// 
		// find a file name to save it to 
		// 
		strcpy(pcxname,"quake00.pcx");
		
		for (i=0 ; i<=99 ; i++) 
		{ 
			pcxname[5] = i/10 + '0'; 
			pcxname[6] = i%10 + '0'; 
			sprintf (checkname, "%s/%s", cls.gamedir, pcxname);
			f = fopen (checkname, "rb");
			if (!f)
				break;  // file doesn't exist
			fclose (f);
		} 
		if (i==100) 
		{
			Com_Printf ("R_ScreenShot_f: Couldn't create a PCX"); 
			return;
		}
	}
 
// 
// save the pcx file 
// 
	D_EnableBackBufferAccess ();

	WritePCX (vid.buffer, vid.width, vid.height, vid.rowbytes,
				  current_pal, &pcxdata, &pcxsize);

	D_DisableBackBufferAccess ();

	COM_WriteFile (va("%s/%s", cls.gamedirfile, pcxname), pcxdata, pcxsize);

	Com_Printf ("Wrote %s\n", pcxname);
} 

/*
Find closest color in the palette for named color
*/
int MipColor(int r, int g, int b)
{
	int i = 0;
	float dist = 0.0;
	int best = -1;
	float bestdist;
	int r1 = 0, g1 = 0, b1 = 0;
	static int lr = -1, lg = -1, lb = -1;
	static int lastbest = -1;

	if (r == lr && g == lg && b == lb)
		return lastbest;

	bestdist = 256*256*3;

	for (i = 0; i < 256; i++) {
		r1 = host_basepal[i*3] - r;
		g1 = host_basepal[i*3+1] - g;
		b1 = host_basepal[i*3+2] - b;
		dist = r1*r1 + g1*g1 + b1*b1;
		if (dist < bestdist) {
			bestdist = dist;
			best = i;
		}
	}
	lr = r; lg = g; lb = b;
	lastbest = best;
	return best;
}

void R_DrawCharToSnap (int num, byte *dest, int width)
{
	int		row, col;
	byte	*source;
	int		drawline;
	int		x;

	row = num>>4;
	col = num&15;
	source = draw_chars[0] + (row<<10) + (col<<3);

	drawline = 8;

	while (drawline--)
	{
		for (x=0 ; x<8 ; x++)
			if (source[x])
				dest[x] = source[x];
			else
				dest[x] = 98;
		source += 128;
		dest += width;
	}

}

void R_DrawStringToSnap (const char *s, byte *buf, int x, int y, int width)
{
	byte *dest;
	const unsigned char *p;

	dest = buf + ((y * width) + x);

	p = (const unsigned char *)s;
	while (*p) {
		R_DrawCharToSnap(*p++, dest, width);
		dest += 8;
	}
}


/* 
================== 
R_RSShot

Memory pointed to by pcxdata is allocated using Hunk_TempAlloc
Never store this pointer for later use!

On failure (not enough memory), *pcxdata will be set to NULL
================== 
*/  
#define RSSHOT_WIDTH 320
#define RSSHOT_HEIGHT 200
void R_RSShot (byte **pcxdata, int *pcxsize)
{ 
	int     x, y;
	unsigned char		*src, *dest;
	unsigned char		*newbuf;
	int w, h;
	int dx, dy, dex, dey, nx;
	int r, b, g;
	int count;
	float fracw, frach;
	char st[80];
	time_t now;
	extern cvar_t name;

// 
// save the pcx file 
// 
	D_EnableBackBufferAccess ();

	w = (vid.width < RSSHOT_WIDTH) ? vid.width : RSSHOT_WIDTH;
	h = (vid.height < RSSHOT_HEIGHT) ? vid.height : RSSHOT_HEIGHT;

	fracw = (float)vid.width / (float)w;
	frach = (float)vid.height / (float)h;

	newbuf = Q_malloc (w*h);

	for (y = 0; y < h; y++) {
		dest = newbuf + (w * y);

		for (x = 0; x < w; x++) {
			r = g = b = 0;

			dx = x * fracw;
			dex = (x + 1) * fracw;
			if (dex == dx) dex++; // at least one
			dy = y * frach;
			dey = (y + 1) * frach;
			if (dey == dy) dey++; // at least one

			count = 0;
			for (/* */; dy < dey; dy++) {
				src = vid.buffer + (vid.rowbytes * dy) + dx;
				for (nx = dx; nx < dex; nx++) {
					r += host_basepal[*src * 3];
					g += host_basepal[*src * 3+1];
					b += host_basepal[*src * 3+2];
					src++;
					count++;
				}
			}
			r /= count;
			g /= count;
			b /= count;
			*dest++ = MipColor(r, g, b);
		}
	}

	D_DisableBackBufferAccess ();

	time(&now);
	strcpy(st, ctime(&now));
	st[strlen(st) - 1] = 0;		// remove the trailing \n
	R_DrawStringToSnap (st, newbuf, w - strlen(st)*8, 0, w);

	strlcpy (st, cls.servername, sizeof(st));
	R_DrawStringToSnap (st, newbuf, w - strlen(st)*8, 10, w);

	strlcpy (st, name.string, sizeof(st));
	R_DrawStringToSnap (st, newbuf, w - strlen(st)*8, 20, w);

	WritePCX (newbuf, w, h, w, host_basepal, pcxdata, pcxsize);

	Q_free (newbuf);

	// return with pcxdata and pcxsize
} 

//=============================================================================


void R_Build15to8table (void)
{
	unsigned r, g, b;
	unsigned v;
	int     r1, g1, b1;
	int		j, k, l;
	unsigned short i;
	unsigned char *pal;

	// JACK: 3D distance calcs - k is last closest, l is the distance.
	// FIXME: Precalculate this and cache to disk.
	for (i=0; i < (1<<15); i++)
	{
		/* Maps
			000000000000000
			000000000011111 = Red  = 0x1F
			000001111100000 = Blue = 0x03E0
			111110000000000 = Grn  = 0x7C00
		*/
		r = ((i & 0x1F) << 3)+4;
		g = ((i & 0x03E0) >> 2)+4;
		b = ((i & 0x7C00) >> 7)+4;
		pal = r_palette;

		for (v = 0, k = 0, l = 10000*10000; v < 256; v++, pal += 3)
		{
			r1 = r - pal[0];
			g1 = g - pal[1];
			b1 = b - pal[2];

			j = (r1*r1) + (g1*g1) + (b1*b1);
			if (j < l)
			{
				k = v;
				l = j;
			}
		}

		d_15to8table[i] = k;
	}
}

/* vi: set noet ts=4 sts=4 ai sw=4: */
