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
// vid_x.c -- general x video driver

#define _BSD

typedef unsigned short PIXEL16;
typedef unsigned int PIXEL24;

#include <ctype.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xatom.h>
#include <X11/keysym.h>
#include <X11/extensions/XShm.h>

#ifdef USE_VMODE
#include <X11/extensions/xf86vmode.h>
#endif

#ifdef USE_DGA
#include <X11/extensions/xf86dga.h>
#endif

#include "quakedef.h"
#include "d_local.h"
#include "input.h"
#include "keys.h"

cvar_t vid_ref = { "vid_ref", "soft", CVAR_ROM };
cvar_t _windowed_mouse = { "_windowed_mouse", "0", CVAR_ARCHIVE };
cvar_t m_filter = { "m_filter", "0", CVAR_ARCHIVE };

qbool mouse_avail = false;
int mouse_buttons = 3;
int mouse_oldbuttonstate;
int mouse_buttonstate;
float mouse_x, mouse_y;
float old_mouse_x, old_mouse_y;
static qbool input_grabbed = false;

#ifdef USE_DGA
static qbool dgamouse = false;
#endif

#ifdef USE_VMODE
static int scrnum;
static qbool vidmode_ext = false;
static XF86VidModeModeInfo **vidmodes;
static int num_vidmodes;
static qbool vidmode_active = false;
#endif

extern viddef_t vid;			// global video state

static qbool doShm;
static Display *x_disp;
static Colormap x_cmap;
static Window x_win;
static GC x_gc;
static Visual *x_vis;
static XVisualInfo *x_visinfo;

static int x_shmeventtype;

static qbool oktodraw = false;

int XShmQueryExtension (Display *);
int XShmGetEventBase (Display *);

int current_framebuffer;
static XImage *x_framebuffer[2] = { 0, 0 };
static XShmSegmentInfo x_shminfo[2];

static int verbose = 0;

static byte current_palette[768];

static long X11_highhunkmark;
static long X11_buffersize;

int vid_surfcachesize;
void *vid_surfcache;

static PIXEL16 st2d_8to16table[256];
static PIXEL24 st2d_8to24table[256];
static int shiftmask_fl = 0;
static long r_shift, g_shift, b_shift;
static unsigned long r_mask, g_mask, b_mask;

static void shiftmask_init ();
static PIXEL16 xlib_rgb16 (int r, int g, int b);
static PIXEL24 xlib_rgb24 (int r, int g, int b);
static void st2_fixup (XImage *framebuf, int x, int y, int width, int height);
static void st3_fixup (XImage *framebuf, int x, int y, int width, int height);


static void shiftmask_init ()
{
	unsigned int x;
	r_mask = x_vis->red_mask;
	g_mask = x_vis->green_mask;
	b_mask = x_vis->blue_mask;

	if (r_mask > (1 << 31) || g_mask > (1 << 31) || b_mask > (1 << 31))
		Sys_Error ("XGetVisualInfo returned bogus rgb mask");

	for (r_shift = -8, x = 1; x < r_mask; x = x << 1)
		r_shift++;
	for (g_shift = -8, x = 1; x < g_mask; x = x << 1)
		g_shift++;
	for (b_shift = -8, x = 1; x < b_mask; x = x << 1)
		b_shift++;

	shiftmask_fl = 1;
}


static PIXEL16 xlib_rgb16 (int r, int g, int b)
{
	PIXEL16 p;

	if (shiftmask_fl == 0)
		shiftmask_init ();
	p = 0;

	if (r_shift > 0)
		p = (r << (r_shift)) & r_mask;
	else if (r_shift < 0)
		p = (r >> (-r_shift)) & r_mask;
	else
		p |= (r & r_mask);

	if (g_shift > 0)
		p |= (g << (g_shift)) & g_mask;
	else if (g_shift < 0)
		p |= (g >> (-g_shift)) & g_mask;
	else
		p |= (g & g_mask);

	if (b_shift > 0)
		p |= (b << (b_shift)) & b_mask;
	else if (b_shift < 0)
		p |= (b >> (-b_shift)) & b_mask;
	else
		p |= (b & b_mask);

	return p;
}


static PIXEL24 xlib_rgb24 (int r, int g, int b)
{
	PIXEL24 p;

	if (shiftmask_fl == 0)
		shiftmask_init ();
	p = 0;

	if (r_shift > 0)
		p = (r << (r_shift)) & r_mask;
	else if (r_shift < 0)
		p = (r >> (-r_shift)) & r_mask;
	else
		p |= (r & r_mask);

	if (g_shift > 0)
		p |= (g << (g_shift)) & g_mask;
	else if (g_shift < 0)
		p |= (g >> (-g_shift)) & g_mask;
	else
		p |= (g & g_mask);

	if (b_shift > 0)
		p |= (b << (b_shift)) & b_mask;
	else if (b_shift < 0)
		p |= (b >> (-b_shift)) & b_mask;
	else
		p |= (b & b_mask);

	return p;
}


static void st2_fixup (XImage *framebuf, int x, int y, int width, int height)
{
	int xi, yi;
	byte *src;
	PIXEL16 *dest;

	if ((x < 0) || (y < 0))
		return;

	for (yi = y; yi < (y + height); yi++)
	{
		src = (byte *) &framebuf->data[yi * framebuf->bytes_per_line];
		dest = (PIXEL16 *) src;
		for (xi = (x + width - 1); xi >= x; xi--)
			dest[xi] = st2d_8to16table[src[xi]];
	}
}


static void st3_fixup (XImage *framebuf, int x, int y, int width, int height)
{
	int xi, yi;
	byte *src;
	PIXEL24 *dest;

	if ((x < 0) || (y < 0))
		return;

	for (yi = y; yi < (y + height); yi++)
	{
		src = (byte *) &framebuf->data[yi * framebuf->bytes_per_line];
		dest = (PIXEL24 *) src;
		for (xi = (x + width - 1); xi >= x; xi--)
			dest[xi] = st2d_8to24table[src[xi]];
	}
}


// ========================================================================
// Tragic death handler
// ========================================================================

void TragicDeath (int signal_num)
{
	XAutoRepeatOn (x_disp);
	XCloseDisplay (x_disp);
	Sys_Error ("This death brought to you by the number %d\n", signal_num);
}

// ========================================================================
// makes a null cursor
// ========================================================================

static Cursor CreateNullCursor (Display *display, Window root)
{
	Pixmap cursormask;
	XGCValues xgc;
	GC gc;
	XColor dummycolour;
	Cursor cursor;

	cursormask = XCreatePixmap (display, root, 1, 1, 1 /*depth */ );
	xgc.function = GXclear;
	gc = XCreateGC (display, cursormask, GCFunction, &xgc);
	XFillRectangle (display, cursormask, gc, 0, 0, 1, 1);
	dummycolour.pixel = 0;
	dummycolour.red = 0;
	dummycolour.flags = 04;
	cursor = XCreatePixmapCursor (display, cursormask, cursormask,
								  &dummycolour, &dummycolour, 0, 0);
	XFreePixmap (display, cursormask);
	XFreeGC (display, gc);
	return cursor;
}

void ResetFrameBuffer (void)
{
	int mem;
	int pwidth;

	if (x_framebuffer[0])
	{
		Q_free (x_framebuffer[0]->data);	// right?
		free (x_framebuffer[0]);
	}

	if (d_pzbuffer)
	{
		D_FlushCaches ();
		Hunk_FreeToHighMark (X11_highhunkmark);
		d_pzbuffer = NULL;
	}
	X11_highhunkmark = Hunk_HighMark ();

// alloc an extra line in case we want to wrap, and allocate the z-buffer
	X11_buffersize = vid.width * vid.height * sizeof (*d_pzbuffer);

	vid_surfcachesize = D_SurfaceCacheForRes (vid.width, vid.height);

	X11_buffersize += vid_surfcachesize;

	d_pzbuffer = Hunk_HighAllocName (X11_buffersize, "video");
	if (d_pzbuffer == NULL)
		Sys_Error ("Not enough memory for video mode\n");

	vid_surfcache = (byte *) d_pzbuffer
		+ vid.width * vid.height * sizeof (*d_pzbuffer);

	D_InitCaches (vid_surfcache, vid_surfcachesize);

	pwidth = x_visinfo->depth / 8;
	if (pwidth == 3)
		pwidth = 4;
	mem = ((vid.width * pwidth + 7) & ~7) * vid.height;

	x_framebuffer[0] = XCreateImage (x_disp,
									 x_vis,
									 x_visinfo->depth,
									 ZPixmap,
									 0,
									 Q_malloc (mem),
									 vid.width, vid.height, 32, 0);

	if (!x_framebuffer[0])
		Sys_Error ("VID: XCreateImage failed\n");

	vid.buffer = (byte *) (x_framebuffer[0]);
}

void ResetSharedFrameBuffers (void)
{
	int size;
	int key;
	int minsize = getpagesize ();
	int frm;

	if (d_pzbuffer)
	{
		D_FlushCaches ();
		Hunk_FreeToHighMark (X11_highhunkmark);
		d_pzbuffer = NULL;
	}

	X11_highhunkmark = Hunk_HighMark ();

// alloc an extra line in case we want to wrap, and allocate the z-buffer
	X11_buffersize = vid.width * vid.height * sizeof (*d_pzbuffer);

	vid_surfcachesize = D_SurfaceCacheForRes (vid.width, vid.height);

	X11_buffersize += vid_surfcachesize;

	d_pzbuffer = Hunk_HighAllocName (X11_buffersize, "video");
	if (d_pzbuffer == NULL)
		Sys_Error ("Not enough memory for video mode\n");

	vid_surfcache = (byte *) d_pzbuffer
		+ vid.width * vid.height * sizeof (*d_pzbuffer);

	D_InitCaches (vid_surfcache, vid_surfcachesize);

	for (frm = 0; frm < 2; frm++)
	{

		// free up old frame buffer memory

		if (x_framebuffer[frm])
		{
			XShmDetach (x_disp, &x_shminfo[frm]);
			free (x_framebuffer[frm]);
			shmdt (x_shminfo[frm].shmaddr);
		}

		// create the image

		x_framebuffer[frm] = XShmCreateImage (x_disp,
											  x_vis,
											  x_visinfo->depth,
											  ZPixmap,
											  0,
											  &x_shminfo[frm],
											  vid.width, vid.height);

		// grab shared memory

		size = x_framebuffer[frm]->bytes_per_line * x_framebuffer[frm]->height;
		if (size < minsize)
			Sys_Error ("VID: Window must use at least %d bytes\n", minsize);

		key = random ();
		x_shminfo[frm].shmid = shmget ((key_t) key, size, IPC_CREAT | 0777);
		if (x_shminfo[frm].shmid == -1)
			Sys_Error ("VID: Could not get any shared memory\n");

		// attach to the shared memory segment
		x_shminfo[frm].shmaddr = (void *) shmat (x_shminfo[frm].shmid, 0, 0);

//		printf ("VID: shared memory id=%d, addr=0x%lx\n", x_shminfo[frm].shmid,
//				(long) x_shminfo[frm].shmaddr);

		x_framebuffer[frm]->data = x_shminfo[frm].shmaddr;

		// get the X server to attach to it

		if (!XShmAttach (x_disp, &x_shminfo[frm]))
			Sys_Error ("VID: XShmAttach() failed\n");
		XSync (x_disp, 0);
		shmctl (x_shminfo[frm].shmid, IPC_RMID, 0);

	}

}


static qbool x_error_caught = false;
static int handler(Display *disp, XErrorEvent *ev)
{
	x_error_caught = true;
	return 0;
}

// Called at startup to set up translation tables, takes 256 8 bit RGB values
// the palette data will go away after the call, so it must be copied off if
// the video driver will need it again

void VID_Init (unsigned char *palette)
{
	int pnum, i;
	XVisualInfo template;
	int num_visuals;
	int template_mask;

	Cvar_Register (&vid_ref);

	vid.width = 320;
	vid.height = 240;
	vid.aspect = 1;
// Tonik: I dunno if it's a bug, but window contents seem to get garbaged
// every frame, so we need to redraw everything every frame
	vid.numpages = 0x7FFFFFFF;	// "infinite"
//	vid.numpages = 2;

	srandom (getpid ());

	verbose = COM_CheckParm ("-verbose");

// open the display
	x_disp = XOpenDisplay (0);
	if (!x_disp)
	{
		if (getenv ("DISPLAY"))
			Sys_Error ("VID: Could not open display [%s]\n",
					   getenv ("DISPLAY"));
		else
			Sys_Error ("VID: Could not open local display\n");
	}

// catch signals so i can turn on auto-repeat

	{
		struct sigaction sa;
		sigaction (SIGINT, 0, &sa);
		sa.sa_handler = TragicDeath;
		sigaction (SIGINT, &sa, 0);
		sigaction (SIGTERM, &sa, 0);
	}

	XAutoRepeatOff (x_disp);

// for debugging only
	XSynchronize (x_disp, True);

// check for command-line window size
	if ((pnum = COM_CheckParm ("-winsize")))
	{
		if (pnum >= com_argc - 2)
			Sys_Error ("VID: -winsize <width> <height>\n");
		vid.width = Q_atoi (com_argv[pnum + 1]);
		vid.height = Q_atoi (com_argv[pnum + 2]);
		if (!vid.width || !vid.height)
			Sys_Error ("VID: Bad window width/height\n");
	}
	if ((pnum = COM_CheckParm ("-width")))
	{
		if (pnum >= com_argc - 1)
			Sys_Error ("VID: -width <width>\n");
		vid.width = Q_atoi (com_argv[pnum + 1]);
		if (!vid.width)
			Sys_Error ("VID: Bad window width\n");
	}
	if ((pnum = COM_CheckParm ("-height")))
	{
		if (pnum >= com_argc - 1)
			Sys_Error ("VID: -height <height>\n");
		vid.height = Q_atoi (com_argv[pnum + 1]);
		if (!vid.height)
			Sys_Error ("VID: Bad window height\n");
	}

	template_mask = 0;

// specify a visual id
	if ((pnum = COM_CheckParm ("-visualid")))
	{
		if (pnum >= com_argc - 1)
			Sys_Error ("VID: -visualid <id#>\n");
		template.visualid = Q_atoi (com_argv[pnum + 1]);
		template_mask = VisualIDMask;
	}

// If not specified, use default visual
	else
	{
		int screen;
		screen = XDefaultScreen (x_disp);
		template.visualid =
			XVisualIDFromVisual (XDefaultVisual (x_disp, screen));
		template_mask = VisualIDMask;
	}

// pick a visual- warn if more than one was available
	x_visinfo =
		XGetVisualInfo (x_disp, template_mask, &template, &num_visuals);
	if (num_visuals > 1)
	{
		printf ("Found more than one visual id at depth %d:\n",
				template.depth);
		for (i = 0; i < num_visuals; i++)
			printf ("	-visualid %d\n", (int) (x_visinfo[i].visualid));
	}
	else if (num_visuals == 0)
	{
		if (template_mask == VisualIDMask)
			Sys_Error ("VID: Bad visual id %d\n", template.visualid);
		else
			Sys_Error ("VID: No visuals at depth %d\n", template.depth);
	}

	if (verbose)
	{
		printf ("Using visualid %d:\n", (int) (x_visinfo->visualid));
		printf ("	screen %d\n", x_visinfo->screen);
		printf ("	red_mask 0x%x\n", (int) (x_visinfo->red_mask));
		printf ("	green_mask 0x%x\n", (int) (x_visinfo->green_mask));
		printf ("	blue_mask 0x%x\n", (int) (x_visinfo->blue_mask));
		printf ("	colormap_size %d\n", x_visinfo->colormap_size);
		printf ("	bits_per_rgb %d\n", x_visinfo->bits_per_rgb);
	}

	x_vis = x_visinfo->visual;

#ifdef USE_VMODE
{
	// check vmode extensions supported
	int MajorVersion, MinorVersion;
	if (!XF86VidModeQueryVersion(x_disp, &MajorVersion, &MinorVersion))
		vidmode_ext = false;
	else
	{
		Com_Printf("Using XFree86-VidModeExtension Version %d.%d\n", MajorVersion, MinorVersion);
		vidmode_ext = true;
    }

    if (vidmode_ext && !COM_CheckParm("-window"))
    {
        int best_fit, best_dist, dist, x, y;

		scrnum = DefaultScreen(x_disp);

        XF86VidModeGetAllModeLines(x_disp, scrnum, &num_vidmodes, &vidmodes);

        best_dist = 9999999;
        best_fit = -1;

        for (i = 0; i < num_vidmodes; i++)
        {
            if (vid.width > vidmodes[i]->hdisplay || vid.height > vidmodes[i]->vdisplay)
                continue;

            x = vid.width - vidmodes[i]->hdisplay;
            y = vid.height - vidmodes[i]->vdisplay;
            dist = x * x + y * y;
            if (dist < best_dist)
            {
                best_dist = dist;
                best_fit = i;
            }
        }

        if (best_fit != -1)
        {
			XF86VidModeModeLine *current_vidmode;

			// This nice hack comes from the SDL source code
			// makes switching back to original vide mode on shutdown actually work
			current_vidmode = (XF86VidModeModeLine*)((char*)vidmodes[0] + sizeof(vidmodes[0]->dotclock));
			XF86VidModeGetModeLine(x_disp, scrnum, (int*)&vidmodes[0]->dotclock, current_vidmode);

            // change to the mode
			x_error_caught = false;
			XSetErrorHandler (handler);
            XF86VidModeSwitchToMode(x_disp, scrnum, vidmodes[best_fit]);
			XSync (x_disp, false);
			XSetErrorHandler (NULL);
			if (!x_error_caught)
			{
	            // Move the viewport to top left
    	        XF86VidModeSetViewPort(x_disp, scrnum, 0, 0);
        	    vidmode_active = true;
				vid.aspect = ((float) vidmodes[best_fit]->vdisplay
								/ (float) vidmodes[best_fit]->hdisplay) * (320.0 / 240.0);	
			}
			else
					Com_Printf ("Failed to set fullscreen mode\n");
        }
        else
        	Com_Printf ("Couldn't find an appropriate fullscreen video mode\n");
    }
}
#endif	// USE_VMODE


// setup attributes for main window
	{
		int attribmask = CWEventMask | CWColormap | CWBorderPixel;
		XSetWindowAttributes attribs;
		Colormap tmpcmap;

		tmpcmap = XCreateColormap (x_disp, XRootWindow (x_disp,
														x_visinfo->screen),
								   x_vis, AllocNone);

		attribs.event_mask = StructureNotifyMask | KeyPressMask
			| KeyReleaseMask | ExposureMask | PointerMotionMask |
			ButtonPressMask | ButtonReleaseMask;
		attribs.border_pixel = 0;
		attribs.colormap = tmpcmap;

    // if fullscreen, disable window manager decoration
#ifdef USE_VMODE
    if (vidmode_active)
    {
        attribmask = CWBackPixel | CWColormap | CWSaveUnder | CWBackingStore |
               CWEventMask | CWOverrideRedirect;
        attribs.override_redirect = True;
        attribs.backing_store = NotUseful;
        attribs.save_under = False;
    }
#endif

// create the main window
	 	x_win = XCreateWindow (x_disp, XRootWindow (x_disp, x_visinfo->screen),
							   0, 0,	// x, y
							   vid.width, vid.height,
							   0,		// border width
							   x_visinfo->depth,
							   InputOutput, x_vis, attribmask, &attribs);
		XStoreName (x_disp, x_win, PROGRAM);


		if (x_visinfo->class != TrueColor)
			XFreeColormap (x_disp, tmpcmap);

	}

	if (x_visinfo->depth == 8)
	{

		// create and upload the palette
		if (x_visinfo->class == PseudoColor)
		{
			x_cmap = XCreateColormap (x_disp, x_win, x_vis, AllocAll);
			VID_SetPalette (palette);
			XSetWindowColormap (x_disp, x_win, x_cmap);
		}

	}

// create the GC
	{
		XGCValues xgcvalues;
		int valuemask = GCGraphicsExposures;
		xgcvalues.graphics_exposures = False;
		x_gc = XCreateGC (x_disp, x_win, valuemask, &xgcvalues);
	}

// map the window
	XMapWindow (x_disp, x_win);

// wait for first exposure event
	{
		XEvent event;
		do
		{
			XNextEvent (x_disp, &event);
			if (event.type == Expose && !event.xexpose.count)
				oktodraw = true;
		}
		while (!oktodraw);
	}
// now safe to draw

// even if MITSHM is available, make sure it's a local connection
	if (XShmQueryExtension (x_disp))
	{
		char *displayname;
		doShm = true;
		displayname = (char *) getenv ("DISPLAY");
		if (displayname)
		{
			char *d = displayname;
			while (*d && (*d != ':'))
				d++;
			if (*d)
				*d = 0;
			if (!(!Q_stricmp (displayname, "unix") || !*displayname))
				doShm = false;
		}
	}

	if (doShm)
	{
		x_shmeventtype = XShmGetEventBase (x_disp) + ShmCompletion;
		ResetSharedFrameBuffers ();
	}
	else
		ResetFrameBuffer ();

	current_framebuffer = 0;
	vid.rowbytes = x_framebuffer[0]->bytes_per_line;
	vid.buffer = (pixel_t *)x_framebuffer[0]->data;
	vid.direct = 0;

//  XSynchronize(x_disp, False);

}

void VID_ShiftPalette (unsigned char *p)
{
	VID_SetPalette (p);
}



void VID_SetPalette (unsigned char *palette)
{
	int i;
	XColor colors[256];

	for (i = 0; i < 256; i++)
	{
		st2d_8to16table[i] =
			xlib_rgb16 (palette[i * 3], palette[i * 3 + 1],
						palette[i * 3 + 2]);
		st2d_8to24table[i] =
			xlib_rgb24 (palette[i * 3], palette[i * 3 + 1],
						palette[i * 3 + 2]);
	}

	if (x_visinfo->class == PseudoColor && x_visinfo->depth == 8)
	{
		if (palette != current_palette)
			memcpy (current_palette, palette, 768);
		for (i = 0; i < 256; i++)
		{
			colors[i].pixel = i;
			colors[i].flags = DoRed | DoGreen | DoBlue;
			colors[i].red = palette[i * 3] * 257;
			colors[i].green = palette[i * 3 + 1] * 257;
			colors[i].blue = palette[i * 3 + 2] * 257;
		}
		XStoreColors (x_disp, x_cmap, colors, 256);
	}
}

static void uninstall_grabs ();
void VID_Shutdown (void)
{
	if (!x_disp)
		return;

	Com_Printf ("VID_Shutdown\n");

	uninstall_grabs ();

	XAutoRepeatOn (x_disp);

#ifdef USE_VMODE
    if (x_disp)
    {
//        if (x_win)
//          XDestroyWindow(x_disp, x_win);
		if (vidmode_active)
			XF86VidModeSwitchToMode(x_disp, scrnum, vidmodes[0]);
		vidmode_active = false;
    }
#endif

	XCloseDisplay (x_disp);
}

static int XLateKey (XKeyEvent *ev)
{

	int key;
//	char buf[64];
//	KeySym shifted;
	KeySym keysym;

	keysym = XLookupKeysym (ev, 0);
//	XLookupString (ev, buf, sizeof buf, &shifted, 0);

	key = 0;

	switch (keysym)
	{
	case XK_KP_Page_Up:
	case XK_Page_Up:
		key = K_PGUP;
		break;

	case XK_KP_Page_Down:
	case XK_Page_Down:
		key = K_PGDN;
		break;

	case XK_KP_Home:
	case XK_Home:
		key = K_HOME;
		break;

	case XK_KP_End:
	case XK_End:
		key = K_END;
		break;

	case XK_KP_Left:
	case XK_Left:
		key = K_LEFTARROW;
		break;

	case XK_KP_Right:
	case XK_Right:
		key = K_RIGHTARROW;
		break;

	case XK_KP_Down:
	case XK_Down:
		key = K_DOWNARROW;
		break;

	case XK_KP_Up:
	case XK_Up:
		key = K_UPARROW;
		break;

	case XK_Escape:
		key = K_ESCAPE;
		break;

	case XK_KP_Enter:
	case XK_Return:
		key = K_ENTER;
		break;

	case XK_Tab:
		key = K_TAB;
		break;

	case XK_F1:
		key = K_F1;
		break;

	case XK_F2:
		key = K_F2;
		break;

	case XK_F3:
		key = K_F3;
		break;

	case XK_F4:
		key = K_F4;
		break;

	case XK_F5:
		key = K_F5;
		break;

	case XK_F6:
		key = K_F6;
		break;

	case XK_F7:
		key = K_F7;
		break;

	case XK_F8:
		key = K_F8;
		break;

	case XK_F9:
		key = K_F9;
		break;

	case XK_F10:
		key = K_F10;
		break;

	case XK_F11:
		key = K_F11;
		break;

	case XK_F12:
		key = K_F12;
		break;

	case XK_BackSpace:
		key = K_BACKSPACE;
		break;

	case XK_KP_Delete:
	case XK_Delete:
		key = K_DEL;
		break;

	case XK_Pause:
		key = K_PAUSE;
		break;

	case XK_Shift_L:
	case XK_Shift_R:
		key = K_SHIFT;
		break;

	case XK_Execute:
	case XK_Control_L:
	case XK_Control_R:
		key = K_CTRL;
		break;

	case XK_Alt_L:
	case XK_Meta_L:
	case XK_Alt_R:
	case XK_Meta_R:
		key = K_ALT;
		break;

	case XK_KP_Begin:
		key = '5';
		break;

	case XK_KP_Insert:
	case XK_Insert:
		key = K_INS;
		break;

	case XK_KP_Multiply:
		key = '*';
		break;
	case XK_KP_Add:
		key = '+';
		break;
	case XK_KP_Subtract:
		key = '-';
		break;
	case XK_KP_Divide:
		key = '/';
		break;

	case XK_Caps_Lock:
		key = K_CAPSLOCK;
		break;
	case XK_Scroll_Lock:
		key = K_SCROLLLOCK;
		break;
	case XK_Num_Lock:
		key = KP_NUMLOCK;
		break;

	default:
		if (keysym >= 32 && keysym <= 126)
		{
			key = tolower (keysym);
		}
		break;
	}

	return key;
}

static void install_grabs (void)
{
	int MajorVersion, MinorVersion;

	input_grabbed = true;

	// don't show mouse cursor icon
	XDefineCursor (x_disp, x_win, CreateNullCursor (x_disp, x_win));

	XGrabPointer (x_disp, x_win,
				  True,
				  0, GrabModeAsync, GrabModeAsync, x_win, None, CurrentTime);

#ifdef USE_DGA
	if (!COM_CheckParm ("-nodga") &&
		XF86DGAQueryVersion (x_disp, &MajorVersion, &MinorVersion))
	{
		// let us hope XF86DGADirectMouse will work
		XF86DGADirectVideo (x_disp, DefaultScreen (x_disp),
							XF86DGADirectMouse);
		dgamouse = true;
		XWarpPointer (x_disp, None, x_win, 0, 0, 0, 0, 0, 0);
	}
	else
#endif
		XWarpPointer (x_disp, None, x_win,
					  0, 0, 0, 0, vid.width / 2, vid.height / 2);

	XGrabKeyboard (x_disp, x_win,
				   False, GrabModeAsync, GrabModeAsync, CurrentTime);
}

static void uninstall_grabs (void)
{
	input_grabbed = false;

#ifdef USE_DGA
	XF86DGADirectVideo (x_disp, DefaultScreen (x_disp), 0);
	dgamouse = false;
#endif

	XUngrabPointer (x_disp, CurrentTime);
	XUngrabKeyboard (x_disp, CurrentTime);

	// show cursor again
	XUndefineCursor (x_disp, x_win);

}

int config_notify = 0;
int config_notify_width;
int config_notify_height;

void GetEvent (void)
{
	XEvent x_event;
	int b;
	qbool grab_input;

	XNextEvent (x_disp, &x_event);
	switch (x_event.type)
	{
	case KeyPress:
	case KeyRelease:
		Key_Event (XLateKey (&x_event.xkey), x_event.type == KeyPress);
		break;

	case MotionNotify:
		if (input_grabbed)
		{
#ifdef USE_DGA
			if (dgamouse)
			{
				mouse_x += x_event.xmotion.x_root;
				mouse_y += x_event.xmotion.y_root;
			}
			else
#endif
			{
				mouse_x =
					(float) ((int) x_event.xmotion.x - (int) (vid.width / 2));
				mouse_y =
					(float) ((int) x_event.xmotion.y - (int) (vid.height / 2));
//printf("m: x=%d,y=%d, mx=%3.2f,my=%3.2f\n", 
//  x_event.xmotion.x, x_event.xmotion.y, mouse_x, mouse_y);

				/* move the mouse to the window center again */
				XSelectInput (x_disp, x_win, StructureNotifyMask | KeyPressMask
							  | KeyReleaseMask | ExposureMask
							  | ButtonPressMask | ButtonReleaseMask);
				XWarpPointer (x_disp, None, x_win, 0, 0, 0, 0,
							  (vid.width / 2), (vid.height / 2));
				XSelectInput (x_disp, x_win, StructureNotifyMask | KeyPressMask
							  | KeyReleaseMask | ExposureMask
							  | PointerMotionMask | ButtonPressMask
							  | ButtonReleaseMask);
			}
		}
		break;

	case ButtonPress:
		b = -1;
		if (x_event.xbutton.button == 1)
			b = 0;
		else if (x_event.xbutton.button == 2)
			b = 2;
		else if (x_event.xbutton.button == 3)
			b = 1;
		if (b >= 0)
			mouse_buttonstate |= 1 << b;
		break;

	case ButtonRelease:
		b = -1;
		if (x_event.xbutton.button == 1)
			b = 0;
		else if (x_event.xbutton.button == 2)
			b = 2;
		else if (x_event.xbutton.button == 3)
			b = 1;
		if (b >= 0)
			mouse_buttonstate &= ~(1 << b);
		break;

	case ConfigureNotify:
//printf("config notify\n");
		config_notify_width = x_event.xconfigure.width;
		config_notify_height = x_event.xconfigure.height;
		config_notify = 1;
		break;

	default:
		if (doShm && x_event.type == x_shmeventtype)
			oktodraw = true;
	}

    grab_input = (_windowed_mouse.value != 0) && (key_dest == key_game);
#ifdef USE_VMODE
	if (vidmode_active)
		grab_input = true;
#endif

	if (grab_input && !input_grabbed)
	{
		/* grab the pointer */
		install_grabs ();
	}
	else if (!grab_input && input_grabbed)
	{
		/* ungrab the pointer */
		uninstall_grabs ();
	}
}


// flushes the given rectangles from the view buffer to the screen
void VID_Update (vrect_t *rects)
{
	// if the window changes dimension, skip this frame
	if (config_notify)
	{
//		fprintf (stderr, "config notify\n");
		config_notify = 0;
		vid.width = config_notify_width & ~7;
		vid.height = config_notify_height;
		if (doShm)
			ResetSharedFrameBuffers ();
		else
			ResetFrameBuffer ();
		vid.rowbytes = x_framebuffer[0]->bytes_per_line;
		vid.buffer = (pixel_t *)x_framebuffer[current_framebuffer]->data;
		SCR_InvalidateScreen ();
		Con_CheckResize ();
		Con_Clear_f ();
		return;
	}

	if (doShm)
	{
		while (rects)
		{
			if (x_visinfo->depth == 24)
			{
				st3_fixup (x_framebuffer[current_framebuffer],
						   rects->x, rects->y, rects->width, rects->height);
			}
			else if (x_visinfo->depth == 16)
			{
				st2_fixup (x_framebuffer[current_framebuffer],
						   rects->x, rects->y, rects->width, rects->height);
			}

			if (!XShmPutImage (x_disp, x_win, x_gc,
							   x_framebuffer[current_framebuffer], rects->x,
							   rects->y, rects->x, rects->y, rects->width,
							   rects->height, True))
			{
				Sys_Error ("VID_Update: XShmPutImage failed\n");
			}

			oktodraw = false;
			while (!oktodraw)
				GetEvent ();
			rects = rects->pnext;
		}
		current_framebuffer = !current_framebuffer;
		vid.buffer = (pixel_t *)x_framebuffer[current_framebuffer]->data;
		XSync (x_disp, False);
	}
	else
	{
		while (rects)
		{
			if (x_visinfo->depth == 24)
			{
				st3_fixup (x_framebuffer[current_framebuffer],
						   rects->x, rects->y, rects->width, rects->height);
			}
			else if (x_visinfo->depth == 16)
			{
				st2_fixup (x_framebuffer[current_framebuffer],
						   rects->x, rects->y, rects->width, rects->height);
			}

			XPutImage (x_disp, x_win, x_gc, x_framebuffer[0], rects->x,
					   rects->y, rects->x, rects->y, rects->width,
					   rects->height);
			rects = rects->pnext;
		}
		XSync (x_disp, False);
	}
}

void Sys_SendKeyEvents (void)
{
	// get events from x server
	if (x_disp)
	{
		while (XPending (x_disp))
			GetEvent ();
	}
}

#if 0
char *Sys_ConsoleInput (void)
{
	static char text[256];
	int len;
	fd_set readfds;
	int ready;
	struct timeval timeout;

	timeout.tv_sec = 0;
	timeout.tv_usec = 0;
	FD_ZERO (&readfds);
	FD_SET (0, &readfds);
	ready = select (1, &readfds, 0, 0, &timeout);

	if (ready > 0)
	{
		len = read (0, text, sizeof (text));
		if (len >= 1)
		{
			text[len - 1] = 0;	// rip off the /n and terminate
			return text;
		}
	}

	return 0;
}
#endif

void D_BeginDirectRect (int x, int y, byte *pbitmap, int width, int height)
{
// direct drawing of the "accessing disk" icon isn't supported under Linux
}

void D_EndDirectRect (int x, int y, int width, int height)
{
// direct drawing of the "accessing disk" icon isn't supported under Linux
}

void IN_Init (void)
{
	mouse_avail = false;
	Cvar_Register (&_windowed_mouse);
	Cvar_Register (&m_filter);
	if (COM_CheckParm ("-nomouse"))
		return;
	mouse_x = mouse_y = 0.0;
	mouse_avail = true;
}

void IN_Shutdown (void)
{
	mouse_avail = false;
}

void IN_Commands (void)
{
	int i;

	if (!mouse_avail)
		return;

	for (i = 0; i < mouse_buttons; i++)
	{
		if ((mouse_buttonstate & (1 << i))
			&& !(mouse_oldbuttonstate & (1 << i)))
			Key_Event (K_MOUSE1 + i, true);

		if (!(mouse_buttonstate & (1 << i))
			&& (mouse_oldbuttonstate & (1 << i)))
			Key_Event (K_MOUSE1 + i, false);
	}
	mouse_oldbuttonstate = mouse_buttonstate;
}

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

	if ((in_strafe.state & 1) || (lookstrafe.value && mlook_active))
		cmd->sidemove += m_side.value * mouse_x;
	else
		cl.viewangles[YAW] -= m_yaw.value * mouse_x;

	if (mlook_active)
		V_StopPitchDrift ();

	if (mlook_active && !(in_strafe.state & 1))
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

void VID_LockBuffer (void)
{
}

void VID_UnlockBuffer (void)
{
}

void VID_SetCaption (char *text)
{
	if (!x_disp)
		return;
	XStoreName (x_disp, x_win, text);
}
