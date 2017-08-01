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

#include <SDL.h>
#include "quakedef.h"
#include "gl_local.h"
#include "keys.h"
#include "input.h"

static SDL_Surface *screen = NULL;
Uint32 flags = 0; // SDL flags
int bpp = 0;

cvar_t	_windowed_mouse = {"_windowed_mouse", "1", CVAR_ARCHIVE};

static qbool mouse_avail = true;
static qbool mouse_active = false;
static int   mouse_x, mouse_y;
static int   old_mouse_x, old_mouse_y;
static int   mouse_oldbuttonstate = 0;

static cvar_t m_filter = {"m_filter", "0"};

static int scr_width, scr_height;

qbool gl_mtexable = false;
qbool gl_mtexfbskins = false;

typedef void (APIENTRY *lpMTexFUNC) (GLenum, GLfloat, GLfloat);
lpMTexFUNC qglMultiTexCoord2f = NULL;

/*-----------------------------------------------------------------------*/


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


static void install_grabs(void)
{
	SDL_Event event;

#if 0
	if(!fullscreen)
		SDL_WarpMouse(scr_width/2, scr_height/2);
#endif

	/* Com_Printf("installing grabs!\n"); */
	SDL_WM_GrabInput(SDL_GRAB_ON);
	SDL_ShowCursor(SDL_DISABLE);

	mouse_active = true;

	/* FIXME: check this doesn't do damage */
	/* remove junk from SDL event queue */
	while (SDL_PollEvent(&event)) {
		/* do nothing */
	}
}

static void uninstall_grabs(void)
{
	/* Com_Printf("uninstalling grabs!\n"); */
	SDL_WM_GrabInput(SDL_GRAB_OFF);
	SDL_ShowCursor(SDL_ENABLE);

	mouse_active = false;
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

void HotKey_ToggleGrab(void)
{
	SDL_GrabMode mode;

	printf("Ctrl-G: toggling input grab!\n");
	mode = SDL_WM_GrabInput(SDL_GRAB_QUERY);
	if ( mode == SDL_GRAB_ON ) {
		printf("Grab was on\n");
	} else {
		printf("Grab was off\n");
	}
	mode = SDL_WM_GrabInput(!mode);
	if ( mode == SDL_GRAB_ON ) {
		printf("Grab is now on\n");
	} else {
		printf("Grab is now off\n");
	}
}

void HotKey_Iconify(void)
{
	printf("Ctrl-Z: iconifying window!\n");
	SDL_WM_IconifyWindow();
}

void IN_DeactivateMouse( void )
{
#ifdef NOT_TESTING_WINDOWED
	if (!mouse_avail || !screen)
		return;
#endif

	if (mouse_active) {
		uninstall_grabs();
		mouse_active = false;
	}
}

void IN_ActivateMouse( void )
{
#ifdef NOT_TESTING_WINDOWED
	if (!mouse_avail || !screen)
		return;
#endif
	/* Com_Printf("IN_ActivateMouse entered\n"); */

	if (!mouse_active) {
		mouse_x = mouse_y = 0; // don't spazz
		install_grabs();
		mouse_active = true;
	}
}

void GL_CheckExtensions (void)
{
}

/*
=================
GL_BeginRendering

=================
*/
void GL_BeginRendering (int *x, int *y, int *width, int *height)
{
	*x = *y = 0;
	*width = scr_width;
	*height = scr_height;

//	glViewport (*x, *y, *width, *height);
}


void GL_EndRendering (void)
{
	Uint8 appstate;

	glFlush();
	SDL_GL_SwapBuffers();

	//react on appstate changes
	appstate = SDL_GetAppState();

	if( !( appstate & SDL_APPMOUSEFOCUS ) || !( appstate & SDL_APPINPUTFOCUS ) ) {
		if(mouse_active == true) {
			/* Com_Printf("appstate nonfocused: %d\n", appstate); */
			uninstall_grabs();
		}
	}
	else if( ( appstate & SDL_APPMOUSEFOCUS ) && ( appstate & SDL_APPINPUTFOCUS ) ) {
		if(mouse_active == false) {
			/* Com_Printf("appstate focused: %d\n", appstate); */
			install_grabs();
		}
	}
}

void VID_Init(unsigned char *palette)
{
	int i;
	int width = 640, height = 400;
	/* Information about the current video settings. */
	const SDL_VideoInfo* info = NULL;

	flags = SDL_OPENGL;		   // to use open gl
	/* flags |= SDL_GL_DOUBLEBUFFER; // have a double buffer (SDL_Flip();) */
	flags |= SDL_HWPALETTE;	   // use hardware palette
	/* flags |= SDL_ANYFORMAT;	   // use anything as last resort */
	flags |= SDL_SWSURFACE;

	Cvar_Register (&m_filter);
	Cvar_Register (&_windowed_mouse);

	if (!(COM_CheckParm("-window")) )
		flags |= SDL_FULLSCREEN;

	if ((i = COM_CheckParm("-bpp")) != 0)
		bpp = atoi(com_argv[i+1]);

	if ((i = COM_CheckParm("-width")) != 0)
		width = atoi(com_argv[i+1]);

	if ((i = COM_CheckParm("-height")) != 0)
		height = atoi(com_argv[i+1]);

	if ((i = COM_CheckParm("-conwidth")) != 0)
		vid.width = Q_atoi(com_argv[i+1]);
	else
		vid.width = 640;

	vid.width &= 0xfff8; // make it a multiple of eight

	if (vid.width < 320)
		vid.width = 320;

	// pick a conheight that matches with correct aspect
	vid.height = vid.width*3 / 4;

	if ((i = COM_CheckParm("-conheight")) != 0)
		vid.height = Q_atoi(com_argv[i+1]);
	if (vid.height < 200)
		vid.height = 200;

	// Load the SDL library
	if (SDL_Init(SDL_INIT_VIDEO) < 0)
		Sys_Error("VID: Couldn't load SDL: %s", SDL_GetError());

	/* get some video information. */
	info = SDL_GetVideoInfo( );

	/* if bpp wasn't set on cmdline use current display mode */
	if (bpp == 0)
		bpp = info->vfmt->BitsPerPixel;

	if (bpp >= 32)
	{
		SDL_GL_SetAttribute (SDL_GL_RED_SIZE, 8);
		SDL_GL_SetAttribute (SDL_GL_GREEN_SIZE, 8);
		SDL_GL_SetAttribute (SDL_GL_BLUE_SIZE, 8);
		SDL_GL_SetAttribute (SDL_GL_DEPTH_SIZE, 24);
	}
	else {
		SDL_GL_SetAttribute( SDL_GL_RED_SIZE, 5 );
		SDL_GL_SetAttribute( SDL_GL_GREEN_SIZE, 5 );
		SDL_GL_SetAttribute( SDL_GL_BLUE_SIZE, 5 );
		SDL_GL_SetAttribute( SDL_GL_DEPTH_SIZE, 16 );
	}

	SDL_GL_SetAttribute( SDL_GL_DOUBLEBUFFER, 1 );

	if (!(screen = SDL_SetVideoMode(width, height, bpp, flags) )) {
		Sys_Error("VID: Couldn't set video mode: %s\n", SDL_GetError());
	}

	scr_width = width;
	scr_height = height;
	vid.realwidth = width;
	vid.realheight = height;

	if (vid.height > height)
		vid.height = height;
	if (vid.width > width)
		vid.width = width;
	vid.width = vid.width;
	vid.height = vid.height;

	vid.aspect = ((float)vid.height / (float)vid.width) * (320.0 / 240.0);
	vid.numpages = 2;

	GL_Init();

	SDL_WM_SetCaption("zquake-glsdl","zquake-glsdl");

	Com_Printf ("Video mode %dx%dx%d initialized.\n", width, height, bpp);

	SCR_InvalidateScreen ();

	// hide the mouse
	SDL_ShowCursor(0);

    // turn on key repeating
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);
}

void VID_Shutdown(void)
{
	IN_DeactivateMouse();
	SDL_Quit();

	screen = NULL;
}


void Sys_SendKeyEvents(void)
{
	SDL_Event event;

	/* Check if there's a pending event. */
	while( SDL_PollEvent( &event ) ) {
		switch (event.type) {
#if 0
		case SDL_ACTIVEEVENT:
		printf( "app %s ", event.active.gain ? "gained" : "lost" );
		if ( event.active.state & SDL_APPACTIVE ) {
			printf( "active " );
		} else if ( event.active.state & SDL_APPMOUSEFOCUS ) {
			printf( "mouse " );
		} else if ( event.active.state & SDL_APPINPUTFOCUS ) {
			printf( "input " );
		}
		printf( "focus\n" );
		break;
#endif

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
			if (mouse_active) {
                mouse_x += event.motion.xrel;
                mouse_y += event.motion.yrel;
			}
			break;

#if 0
		case SDL_MOUSEBUTTONDOWN:
			b=-1;
			if (event.button.button == SDL_BUTTON_LEFT)
				b = 0;
			else if (event.button.button == SDL_BUTTON_RIGHT)
				b = 1;
			else if (event.button.button == SDL_BUTTON_MIDDLE)
				b = 2;
			if (b>=0)
				Key_Event(K_MOUSE1 + b, true);
			break;

		case SDL_MOUSEBUTTONUP:
			b=-1;
			if (event.button.button == SDL_BUTTON_LEFT)
				b = 0;
			else if (event.button.button == SDL_BUTTON_RIGHT)
				b = 1;
			else if (event.button.button == SDL_BUTTON_MIDDLE)
				b = 2;
			if (b>=0)
				Key_Event(K_MOUSE1 + b, false);
			break;


		case SDL_VIDEOEXPOSE:
			break;
#endif
		}
	}
}

#if 0
void Force_CenterView_f (void)
{
	cl.viewangles[PITCH] = 0;
}
#endif

void IN_Init(void)
{
	if ( COM_CheckParm ("-nomouse") )
		return;
	mouse_x = mouse_y = 0;
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

void VID_SetCaption (char *text) {
	SDL_WM_SetCaption(text, text);
}
void VID_SetDeviceGammaRamp (unsigned short *ramps) {
	SDL_SetGammaRamp (ramps, ramps + 256, ramps + 512);
}

