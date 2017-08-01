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

// cl_draw.h - 2d drawing functions which don't belong to refresh

#include "quakedef.h"

/*
================
Draw_Alt_String
================
*/
void Draw_Alt_String (int x, int y, const char *str)
{
	while (*str) {
		R_DrawChar (x, y, (*str) | 0x80);
		str++;
		x += 8;
	}
}


/*
================
Draw_TextBox
================
*/
void Draw_TextBox (int x, int y, int width, int lines)
{
	mpic_t	*p;
	int		cx, cy;
	int		n;

	// draw left side
	cx = x;
	cy = y;
	p = R_CachePic ("gfx/box_tl.lmp");
	R_DrawPic (cx, cy, p);
	p = R_CachePic ("gfx/box_ml.lmp");
	for (n = 0; n < lines; n++)
	{
		cy += 8;
		R_DrawPic (cx, cy, p);
	}
	p = R_CachePic ("gfx/box_bl.lmp");
	R_DrawPic (cx, cy+8, p);

	// draw middle
	cx += 8;
	while (width > 0)
	{
		cy = y;
		p = R_CachePic ("gfx/box_tm.lmp");
		R_DrawPic (cx, cy, p);
		p = R_CachePic ("gfx/box_mm.lmp");
		for (n = 0; n < lines; n++)
		{
			cy += 8;
			if (n == 1)
				p = R_CachePic ("gfx/box_mm2.lmp");
			R_DrawPic (cx, cy, p);
		}
		p = R_CachePic ("gfx/box_bm.lmp");
		R_DrawPic (cx, cy+8, p);
		width -= 2;
		cx += 16;
	}

	// draw right side
	cy = y;
	p = R_CachePic ("gfx/box_tr.lmp");
	R_DrawPic (cx, cy, p);
	p = R_CachePic ("gfx/box_mr.lmp");
	for (n = 0; n < lines; n++)
	{
		cy += 8;
		R_DrawPic (cx, cy, p);
	}
	p = R_CachePic ("gfx/box_br.lmp");
	R_DrawPic (cx, cy+8, p);
}


void Draw_Crosshair (void)
{
	extern cvar_t crosshair, cl_crossx, cl_crossy;

	if (cl.spectator && cam_curtarget == CAM_NOTARGET)
		return;

	if (!crosshair.value)
		return;

	R_DrawCrosshair (crosshair.value, cl_crossx.value, cl_crossy.value);
}
