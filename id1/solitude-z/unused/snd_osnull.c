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
// snd_osnull.c -- empty stub for SNDDMA_xx functions for OS which don't
//   support sound (or where it have not been ported - yet :-)

#include <stdio.h>

#include "quakedef.h"
#include "sound.h"

static int			 snd_inited = 0;

qbool SNDDMA_Init(void)
{
	snd_inited = 0;
	return 0;
}


int SNDDMA_GetDMAPos(void)
{
	return (snd_inited);
}


void SNDDMA_Shutdown(void)
{
	snd_inited = 0;
}


/*
==============
SNDDMA_Submit

Send sound to device if buffer isn't really the dma buffer
===============
*/
void SNDDMA_Submit(void)
{
}

