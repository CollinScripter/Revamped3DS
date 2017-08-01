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
#ifdef __APPLE__
#define FULLSCREENHACK
#endif

#include <SDL.h>
#include "quakedef.h"
#include "render.h"
#include "d_local.h"
#include "keys.h"
#include "input.h"

#ifdef FULLSCREENHACK
static byte *backbuf = NULL;
byte *ylookup[240];
qbool fullscreenhack = true;
qbool panscan = false;
#endif

static SDL_Surface *screen = NULL;
Uint32 flags = 0; // SDL flags
int bpp = 8; // 8bpp only

#define BASEWIDTH       320
#define BASEHEIGHT      200

unsigned short  d_8to16table[256];

cvar_t	_windowed_mouse = {"_windowed_mouse", "1", CVAR_ARCHIVE};

static qbool mouse_avail = true;
static int   mouse_x, mouse_y;
static int   old_mouse_x, old_mouse_y;
static int   mouse_oldbuttonstate = 0;

static cvar_t m_filter = {"m_filter", "0"};


// software specific

viddef_t    vid;                // global video state

int    VGA_width, VGA_height, VGA_rowbytes, VGA_bufferrowbytes = 0;
byte    *VGA_pagebase;

// No support for option menus
/* void (*vid_menudrawfn)(void) = NULL; */
/* void (*vid_menukeyfn)(int key) = NULL; */

#ifdef FULLSCREENHACK
/* This scales a 320x200 image to 640x400 This code has been optimized to
 * the max, because it's used a lot  */
void copyFullScreen(char* source, char* dest)
{
	int i, j, inRow, outRow1, outRow2;
	/* for(j = 0; j < 200; j++) { */
	for(j = 0; j < vid.height; j++) {
		inRow = ylookup[j];
		outRow1 = (j<<1)*640;
		outRow2 = ((j<<1)+1)*640;
		/* for(i = 0; i < 320; i++) { */
		for(i = 0; i < vid.width; i++) {
			dest[outRow2+(i<<1)+1] = dest[outRow2+(i<<1)] =
			dest[outRow1+(i<<1)+1] = dest[outRow1+(i<<1)] = source[inRow+i];
		}
	}
}
// The same as above but for scaling 320x200 to 640x480 so the aspect ratio
// is ruined
void copyFullScreenPanScan(char* source, char* dest)
{
	/* int i, j, inRow, outRow1, outRow2, outRow3; */
	unsigned long i, j, inRow, outRow1, outRow2, outRow3;
    for(j = 0; j < 40; j++) {
        inRow = 1600*j;
        outRow1 = 7680*j;
		outRow2 = outRow1+640;
		for(i = 0; i < 320; i++) {
			dest[outRow2+(i<<1)+1] = dest[outRow2+(i<<1)] =
			dest[outRow1+(i<<1)+1] = dest[outRow1+(i<<1)] = source[inRow+i];
		}
		inRow += 320;
		outRow1 += 1280;
		outRow2 += 1280;
		outRow3 = outRow2+640;
		for(i = 0; i < 320; i++) {
			dest[outRow3+(i<<1)+1] = dest[outRow3+(i<<1)] =
			dest[outRow2+(i<<1)+1] = dest[outRow2+(i<<1)] =
			dest[outRow1+(i<<1)+1] = dest[outRow1+(i<<1)] = source[inRow+i];
		}
		inRow += 320;
		outRow1 += 1920;
		outRow2 += 1920;
		for(i = 0; i < 320; i++) {
			dest[outRow2+(i<<1)+1] = dest[outRow2+(i<<1)] =
			dest[outRow1+(i<<1)+1] = dest[outRow1+(i<<1)] = source[inRow+i];
		}
		inRow += 320;
		outRow1 += 1280;
		outRow2 += 1280;
		outRow3 = outRow2+640;
		for(i = 0; i < 320; i++) {
			dest[outRow3+(i<<1)+1] = dest[outRow3+(i<<1)] =
			dest[outRow2+(i<<1)+1] = dest[outRow2+(i<<1)] =
			dest[outRow1+(i<<1)+1] = dest[outRow1+(i<<1)] = source[inRow+i];
		}
		inRow += 320;
		outRow1 += 1920;
		outRow2 += 1920;
		for(i = 0; i < 320; i++) {
			dest[outRow2+(i<<1)+1] = dest[outRow2+(i<<1)] =
			dest[outRow1+(i<<1)+1] = dest[outRow1+(i<<1)] = source[inRow+i];
		}
	}
}
#endif                   // !New!]

static int SDL_LateKey(SDL_keysym *sym)
{
	int key = 0;

	switch(sym->sym)
	{
		case SDLK_PAGEUP:
			key = K_PGUP;
			break;

		case SDLK_PAGEDOWN:
			key = K_PGDN;
			break;

		case SDLK_HOME:
			key = K_HOME;
			break;

		case SDLK_END:
			key = K_END;
			break;

		case SDLK_LEFT:
			key = K_LEFTARROW;
			break;

		case SDLK_RIGHT:
			key = K_RIGHTARROW;
			break;

		case SDLK_DOWN:
			key = K_DOWNARROW;
			break;

		case SDLK_UP:
			key = K_UPARROW;
			break;

		case SDLK_ESCAPE:
			key = K_ESCAPE;
			break;

		case SDLK_RETURN:
		case SDLK_KP_ENTER:
			key = K_ENTER;
			break;

		case SDLK_TAB:
			key = K_TAB;
			break;

		case SDLK_F1:
			key = K_F1;
			break;

		case SDLK_F2:
			key = K_F2;
			break;

		case SDLK_F3:
			key = K_F3;
			break;

		case SDLK_F4:
			key = K_F4;
			break;

		case SDLK_F5:
			key = K_F5;
			break;

		case SDLK_F6:
			key = K_F6;
			break;

		case SDLK_F7:
			key = K_F7;
			break;

		case SDLK_F8:
			key = K_F8;
			break;

		case SDLK_F9:
			key = K_F9;
			break;

		case SDLK_F10:
			key = K_F10;
			break;

		case SDLK_F11:
			key = K_F11;
			break;

		case SDLK_F12:
			key = K_F12;
			break;

		case SDLK_BACKSPACE:
			key = K_BACKSPACE;
			break;

		case SDLK_DELETE:
			key = K_DEL;
			break;

		case SDLK_PAUSE:
			key = K_PAUSE;
			break;

        case SDLK_CAPSLOCK:
            key = K_CAPSLOCK;
            break;

		case SDLK_LSHIFT:
		case SDLK_RSHIFT:
			key = K_SHIFT;
			break;

		case SDLK_LCTRL:
		case SDLK_RCTRL:
			key = K_CTRL;
			break;

		case SDLK_LALT:
		case SDLK_RALT:
			key = K_ALT;
			break;

            // FIXME: oldman keypad support should be added (not had access
            // to non laptop keyboard before :)
		case SDLK_KP0:
			key = '0';
			break;
		case SDLK_KP1:
			key = '1';
			break;
		case SDLK_KP2:
			key = '2';
			break;
		case SDLK_KP3:
			key = '3';
			break;
		case SDLK_KP4:
			key = '4';
			break;
		case SDLK_KP5:
			key = '5';
			break;
		case SDLK_KP6:
			key = '6';
			break;
		case SDLK_KP7:
			key = '7';
			break;
		case SDLK_KP8:
			key = '8';
			break;
		case SDLK_KP9:
			key = '9';
			break;

		case SDLK_INSERT:
			key = K_INS;
			break;

		case SDLK_KP_MULTIPLY:
			key = '*';
			break;

		case SDLK_KP_PLUS:
			key = '+';
			break;

		case SDLK_KP_MINUS:
			key = '-';
			break;

		case SDLK_KP_DIVIDE:
			key = '/';
			break;

		default:
			key = sym->sym;
			break;
	}

	return key;
}


void HotKey_Iconify(void)
{
	printf("Ctrl-Z: iconifying window!\n");
	SDL_WM_IconifyWindow();
}

void HotKey_ToggleFullScreen(void)
{
	SDL_Surface *screen;

	screen = SDL_GetVideoSurface();
	if ( SDL_WM_ToggleFullScreen(screen) ) {
		printf("Toggled fullscreen mode - now %s\n",
		    (screen->flags&SDL_FULLSCREEN) ? "fullscreen" : "windowed");
	} else {
		Com_Printf("Unable to toggle fullscreen mode\n");
        flags ^= SDL_FULLSCREEN;
        screen = SDL_SetVideoMode(screen->w, screen->h, bpp, flags);
	}
}


void    VID_Init (unsigned char *palette)
{
    int i, j;
    int chunk;
    byte *cache;
    int cachesize;

    // Set video width, height and flags
    flags = (SDL_SWSURFACE|SDL_HWPALETTE);

	Cvar_Register (&m_filter);
    Cvar_Register (&_windowed_mouse);

    if (!(COM_CheckParm ("-window")) )
        flags |= SDL_FULLSCREEN;

    if ((i = COM_CheckParm("-width")) != 0)
        vid.width = atoi(com_argv[i+1]);
    else
        vid.width = BASEWIDTH;

    if ((i = COM_CheckParm("-height")) != 0)
        vid.height = atoi(com_argv[i+1]);
    else
        vid.height = BASEHEIGHT;

    // Load the SDL library
    if (SDL_Init(SDL_INIT_VIDEO) < 0)
        Sys_Error("VID: Couldn't load SDL: %s", SDL_GetError());

    // Initialize display
#ifdef FULLSCREENHACK
    if ((i = COM_CheckParm("-panscan")) != 0 && vid.height == 200) {
        panscan = true;
    }

    if (vid.width == 320 && vid.height == 200) {
        if(panscan == true) {
            if (!(screen = SDL_SetVideoMode(640, 480, 8, flags)))
                Sys_Error("VID: Couldn't set video mode: %s\n", SDL_GetError());
        }
        else {
            if (!(screen = SDL_SetVideoMode(640, 400, 8, flags)))
                Sys_Error("VID: Couldn't set video mode: %s\n", SDL_GetError());
        }
        backbuf = malloc(320*200);
    }
    else if (vid.width == 320 && vid.height == 240) {
        if (!(screen = SDL_SetVideoMode(640, 480, 8, flags)))
            Sys_Error("VID: Couldn't set video mode: %s\n", SDL_GetError());
        backbuf = malloc(320*240);
    }
    else {
        if (!(screen = SDL_SetVideoMode(vid.width, vid.height, 8, flags)))
            Sys_Error("VID: Couldn't set video mode: %s\n", SDL_GetError());
        fullscreenhack = false;
    }

    for(j = 0; j < vid.height; j++) {
        ylookup[j] = 320*j;
    }

#else
    if (!(screen = SDL_SetVideoMode(vid.width, vid.height, 8, flags)))
        Sys_Error("VID: Couldn't set video mode: %s\n", SDL_GetError());
#endif
    Com_Printf("Video mode initialised to: %dx%d\n", vid.width, vid.height);
    VID_SetPalette(palette);
    SDL_WM_SetCaption("zquake-sdl","zquake-sdl");
    // now know everything we need to know about the buffer
#if 0
    VGA_width = vid.conwidth = vid.width;
    VGA_height = vid.conheight = vid.height;
#endif
    VGA_width = vid.width;
    VGA_height = vid.height;
    vid.aspect = ((float)vid.height / (float)vid.width) * (320.0 / 240.0);
    vid.numpages = 1;
#ifdef FULLSCREENHACK
    if(fullscreenhack == true) {
        VGA_pagebase = vid.buffer = backbuf;
        VGA_rowbytes = vid.rowbytes = 320;
    }
    else {
#endif
        VGA_pagebase = vid.buffer = screen->pixels;
        VGA_rowbytes = vid.rowbytes = screen->pitch;
#ifdef FULLSCREENHACK
    }
#endif
    vid.direct = 0;

    // allocate z buffer and surface cache
    chunk = vid.width * vid.height * sizeof (*d_pzbuffer);
    cachesize = D_SurfaceCacheForRes (vid.width, vid.height);
    chunk += cachesize;
    d_pzbuffer = Hunk_HighAllocName(chunk, "video");
    if (d_pzbuffer == NULL)
        Sys_Error ("Not enough memory for video mode\n");

    // initialize the cache memory
    cache = (byte *) d_pzbuffer
        + vid.width * vid.height * sizeof (*d_pzbuffer);
    D_InitCaches (cache, cachesize);

	Com_Printf ("Video mode %dx%dx%d initialized.\n", vid.width, vid.height, bpp);

    // hide the mouse
    SDL_ShowCursor(0);

    // turn on key repeating
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);
}

void    VID_Shutdown (void)
{
    SDL_Quit();
#ifdef FULLSCREENHACK
    if(backbuf != NULL) {
        free(backbuf);
        backbuf = NULL;
    }
#endif
}

void    VID_ShiftPalette (unsigned char *palette)
{
    VID_SetPalette(palette);
}

void    VID_SetPalette (unsigned char *palette)
{
    int i;
    SDL_Color colors[256];

    for ( i=0; i<256; ++i )
    {
        colors[i].r = *palette++;
        colors[i].g = *palette++;
        colors[i].b = *palette++;
    }
    SDL_SetColors(screen, colors, 0, 256);
}

void    VID_Update (vrect_t *rects)
{
    SDL_Rect *sdlrects;
    int n, i;
    vrect_t *rect;

    // Two-pass system, since Quake doesn't do it the SDL way...

    // First, count the number of rectangles
    n = 0;
    for (rect = rects; rect; rect = rect->pnext)
        ++n;

    // Second, copy them to SDL rectangles and update
    if (!(sdlrects = (SDL_Rect *)alloca(n*sizeof(*sdlrects))))
        Sys_Error("Out of memory");
    i = 0;
    for (rect = rects; rect; rect = rect->pnext)
    {
#ifdef FULLSCREENHACK
    if(fullscreenhack == true) {
        if(panscan == true) {
            sdlrects[i].x = rect->x * (640/320);
            sdlrects[i].y = rect->y * (480/200);
            sdlrects[i].w = rect->width * (640/320);
            sdlrects[i].h = rect->height * (480/200);
            sdlrects[i].h += 80; // FIXME: doesn't seem to like above ratios
        }
        else {
            sdlrects[i].x = rect->x * (640/320);
            sdlrects[i].y = rect->y * (400/200);
            sdlrects[i].w = rect->width * (640/320);
            sdlrects[i].h = rect->height * (400/200);
        }
    }
    else {
#endif
        sdlrects[i].x = rect->x;
        sdlrects[i].y = rect->y;
        sdlrects[i].w = rect->width;
        sdlrects[i].h = rect->height;
#ifdef FULLSCREENHACK
    }
#endif
        ++i;
    }
#ifdef FULLSCREENHACK
    /* SDL_UpdateRects(backbuf, n, sdlrects); */
    /* scale2x(backbuf, screen, 0, 0); */
    if(fullscreenhack == true) {
        if(panscan == true) {
            copyFullScreenPanScan(backbuf, (char*)screen->pixels);
        }
        else {
            copyFullScreen(backbuf, (char*)screen->pixels);
        }
    }
#endif
    SDL_UpdateRects(screen, n, sdlrects);
}

/*
================
Sys_SendKeyEvents
================
*/

void Sys_SendKeyEvents(void)
{
    SDL_Event event;

    while (SDL_PollEvent( &event )) {
        switch (event.type) {
            case SDL_KEYDOWN:
            case SDL_KEYUP:
                if ( (event.key.keysym.sym == SDLK_z) &&
                        (event.key.keysym.mod & KMOD_CTRL) ) {
                    HotKey_Iconify();
                }
                else if ( (event.key.keysym.sym == SDLK_RETURN) &&
                        (event.key.keysym.mod & KMOD_ALT) &&
                        (event.type == SDL_KEYDOWN) ) {
                    HotKey_ToggleFullScreen();
                }
                else {
                    Key_Event(SDL_LateKey(&event.key.keysym), event.type == SDL_KEYDOWN);
                }
                break;

            case SDL_MOUSEMOTION:
                if ( (event.motion.x != (vid.width/2)) || (event.motion.y != (vid.height/2)) ) {
                    mouse_x = event.motion.xrel;
                    mouse_y = event.motion.yrel;
                    if ( (event.motion.x < ((vid.width/2)-(vid.width/4))) ||
                         (event.motion.x > ((vid.width/2)+(vid.width/4))) ||
                         (event.motion.y < ((vid.height/2)-(vid.height/4))) ||
                         (event.motion.y > ((vid.height/2)+(vid.height/4))) ) {
                        SDL_WarpMouse(vid.width/2, vid.height/2);
                    }
                }
                break;

            default:
                break;
        }
    }
}

void IN_Init (void)
{
    if ( COM_CheckParm ("-nomouse") )
        return;
    mouse_x = mouse_y = 0.0;
    mouse_avail = 1;
}

void IN_Shutdown(void)
{
    mouse_avail = 0;
}

/*
===========
IN_Commands
===========
*/
void IN_Commands (void)
{
    int i;
    int mouse_buttonstate;

    if (!mouse_avail) return;

    i = SDL_GetMouseState(NULL, NULL);
    /* Quake swaps the second and third buttons */
    mouse_buttonstate = (i & ~0x06) | ((i & 0x02)<<1) | ((i & 0x04)>>1);
    for (i=0 ; i<3 ; i++) {
        if ( (mouse_buttonstate & (1<<i)) && !(mouse_oldbuttonstate & (1<<i)) )
            Key_Event (K_MOUSE1 + i, true);

        if ( !(mouse_buttonstate & (1<<i)) && (mouse_oldbuttonstate & (1<<i)) )
            Key_Event (K_MOUSE1 + i, false);
    }

    if ( (mouse_buttonstate & (1<<3)) && !(mouse_oldbuttonstate & (1<<3)) )
        Key_Event (K_MWHEELUP, true);

    if ( (mouse_buttonstate & (1<<3)) && (mouse_oldbuttonstate & (1<<3)) )
        Key_Event (K_MWHEELUP, false);

    if ( (mouse_buttonstate & (1<<4)) && !(mouse_oldbuttonstate & (1<<4)) )
        Key_Event (K_MWHEELDOWN, true);

    if ( (mouse_buttonstate & (1<<4)) && (mouse_oldbuttonstate & (1<<4)) )
        Key_Event (K_MWHEELDOWN, true);

    mouse_oldbuttonstate = mouse_buttonstate;
}

/*
===========
IN_Move
===========
*/
void IN_Move (usercmd_t *cmd)
{
    if (!mouse_avail)
        return;

	if (m_filter.value)
	{
		mouse_x = (mouse_x + old_mouse_x) * 0.5;
		mouse_y = (mouse_y + old_mouse_y) * 0.5;
	}
	old_mouse_x = mouse_x;
	old_mouse_y = mouse_y;

    mouse_x *= sensitivity.value;
    mouse_y *= sensitivity.value;

    // add mouse X/Y movement to cmd
    if ( (in_strafe.state & 1) || (lookstrafe.value && mlook_active))
        cmd->sidemove += m_side.value * mouse_x;
    else
        cl.viewangles[YAW] -= m_yaw.value * mouse_x;

	if (mlook_active)
        V_StopPitchDrift ();

	if ( mlook_active && !(in_strafe.state & 1))
	{
		cl.viewangles[PITCH] += m_pitch.value * mouse_y;
		if (cl.viewangles[PITCH] > cl.maxpitch)
			cl.viewangles[PITCH] = cl.maxpitch;
		if (cl.viewangles[PITCH] < cl.minpitch)
			cl.viewangles[PITCH] = cl.minpitch;
    }
    else
    {
            cmd->forwardmove -= m_forward.value * mouse_y;
    }
	mouse_x = mouse_y = 0.0;
}

// direct draw software compatability stuff
void VID_LockBuffer(void) {}
void VID_UnlockBuffer(void) {}
void D_BeginDirectRect (int x, int y, byte *pbitmap, int width, int height) {}
void D_EndDirectRect (int x, int y, int width, int height) {}

void GL_EndRendering(void) {}

void VID_SetCaption (char *text) {
    SDL_WM_SetCaption(text, text);
}
void VID_SetDeviceGammaRamp (unsigned short *ramps) {
    SDL_SetGammaRamp (ramps, ramps + 256, ramps + 512);
}

