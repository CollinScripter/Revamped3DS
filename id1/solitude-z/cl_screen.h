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
// cl_screen.h
#ifndef _CL_SCREEN_H_
#define _CL_SCREEN_H_

void SCR_Init (void);
void SCR_RegisterPics (void);
void SCR_UpdateScreen (void);
void SCR_InvalidateScreen (void);	// force full redraw
void SCR_BeginLoadingPlaque (void);
void SCR_EndLoadingPlaque (void);
void SCR_CenterPrint (char *str);
void SCR_TileClear (int	y, int height);
void SCR_RunConsole (void);

extern	float	scr_con_current;
extern	float	scr_conlines;		// lines of console to display

extern	int		sb_lines;

extern	int		clearnotify;	// set to 0 whenever notify text is drawn
extern	qbool	scr_disabled_for_loading;

extern	cvar_t	scr_viewsize;

// only the refresh window will be updated unless these variables are flagged 
extern	int		scr_copytop;
extern	int		scr_copyeverything;

extern qbool	scr_skipupdate;
extern qbool	block_drawing;

#endif /* _CL_SCREEN_H_ */

