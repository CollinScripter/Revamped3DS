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
// version.h
#ifndef _VERSION_H_
#define _VERSION_H_

#define	QW_VERSION	2.40
#define PROGRAM_VERSION	"0.17"

//#define RELEASE_VERSION

#ifdef _WIN32
#define QW_PLATFORM	"Win32"
#endif
#ifdef __APPLE__
#define QW_PLATFORM "MacOSX"
#endif
#ifndef QW_PLATFORM
#define QW_PLATFORM	"Linux"
#endif

#ifdef GLQUAKE
#define QW_RENDERER	"GL"
#else
#define QW_RENDERER "Soft"
#endif


int build_number (void);
void CL_Version_f (void);
char *VersionString (void);

#endif /* _VERSION_H_ */

