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
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <stdarg.h>
#include <stdio.h>
#include <signal.h>

#include "gl_local.h"
#include "keys.h"
#include "input.h"

#include <GL/glx.h>

#include <X11/keysym.h>
#include <X11/cursorfont.h>

#ifdef USE_VMODE
#include <X11/extensions/xf86vmode.h>
#endif

#ifdef USE_DGA
#include <X11/extensions/xf86dga.h>
#endif

static Display *x_disp = NULL;
static Window x_win;
static GLXContext ctx = NULL;

static float mouse_x, mouse_y, old_mouse_x, old_mouse_y;
static qbool input_grabbed =  false;

#define KEY_MASK (KeyPressMask | KeyReleaseMask)
#define MOUSE_MASK (ButtonPressMask | ButtonReleaseMask | \
		    PointerMotionMask | ButtonMotionMask )
#define X_MASK (KEY_MASK | MOUSE_MASK | VisibilityChangeMask | StructureNotifyMask )

//typedef void (APIENTRY *lpMTexFUNC) (GLenum, GLfloat, GLfloat);
lpMTexFUNC qglMultiTexCoord2f = NULL;

// setup gamma variables
unsigned short *currentgammaramp = NULL;
qbool vid_gammaworks = false;
// qbool vid_hwgamma_enabled = false;
qbool customgamma = false;

static int scrnum;

#ifdef USE_DGA
static qbool dgamouse = false;
#endif

#ifdef USE_VMODE
static qbool vidmode_ext = false;
static XF86VidModeModeInfo **vidmodes;
static int num_vidmodes;
static qbool vidmode_active = false;
static unsigned short systemgammaramp[3][256];
#endif

cvar_t	vid_ref = {"vid_ref", "gl", CVAR_ROM};
cvar_t	_windowed_mouse = {"_windowed_mouse", "1", CVAR_ARCHIVE};
cvar_t	vid_mode = {"vid_mode","0"};

static float mouse_x, mouse_y;
static float old_mouse_x, old_mouse_y;

cvar_t	m_filter = {"m_filter", "0"};
cvar_t	vid_hwgammacontrol = {"vid_hwgammacontrol", "1"};

/*-----------------------------------------------------------------------*/

qbool gl_mtexable = false;
qbool gl_mtexfbskins = false;

/*-----------------------------------------------------------------------*/

// direct draw software compatibility 

void VID_UnlockBuffer()
{
}

void VID_LockBuffer()
{
}

void D_BeginDirectRect (int x, int y, byte *pbitmap, int width, int height)
{
}

void D_EndDirectRect (int x, int y, int width, int height)
{
}

void VID_SetCaption (char *text)
{
	if (!x_disp)
		return;
	XStoreName (x_disp, x_win, text);
}

// handles a limited range of chars
// currently, only ascii and cyrillic
static int KeysymToUnicode (int k)
{
	extern byte koi2wc_table[64];
	wchar u;
	if (k >= 32 && k <= 126)
		u = k;
	else if (k >= 0x6c0 && k <= 0x6ff)
		u = koi2wc_table[k - 0x6c0] + 0x400;
	else if (k == 0x6a3)
		u = 0x451;		// cyrillic small yo
	else if (k == 0x6b3)
		u = 0x401;		// cyrillic capital YO 
	else if (k == 0x6a4)
		u = 0x454;		// ukrainian ie
	else if (k == 0x6b4)
		u = 0x404;		// ukrainian IE
	else if (k == 0x6a6)
		u = 0x456;		// ukrainian/belarusian i
	else if (k == 0x6b6)
		u = 0x406;		// ukrainian/belarusian I
	else if (k == 0x6a7)
		u = 0x457;		// ukrainian yi
	else if (k == 0x6b7)
		u = 0x407;		// ukrainian YI
	else if (k == 0x6ae)
		u = 0x45e;		// belarusian short u
	else if (k == 0x6b7)
		u = 0x40e;		// belarusian short U
	else
		u = 0;
	return u;
}

static int XLateKey(XKeyEvent *ev, wchar *unichar /*out*/)
{
    int key;
    char buf[64];
    KeySym shifted;
    KeySym keysym;

    keysym = XLookupKeysym (ev, 0);
    XLookupString (ev, buf, sizeof(buf), &shifted, 0);
	*unichar = KeysymToUnicode(shifted);

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
        if (keysym >= 32 && keysym <= 126) {
            key = tolower(keysym);
        }
        break;
    }

    return key;
}

// hide the mouse cursor when in window
static Cursor CreateNullCursor(Display *display, Window root)
{
    Pixmap cursormask;
    XGCValues xgc;
    GC gc;
    XColor dummycolour;
    Cursor cursor;

    cursormask = XCreatePixmap(display, root, 1, 1, 1/*depth*/);
    xgc.function = GXclear;
    gc =  XCreateGC(display, cursormask, GCFunction, &xgc);
    XFillRectangle(display, cursormask, gc, 0, 0, 1, 1);
    dummycolour.pixel = 0;
    dummycolour.red = 0;
    dummycolour.flags = 04;
    cursor = XCreatePixmapCursor(display, cursormask, cursormask,
                                 &dummycolour,&dummycolour, 0,0);
    XFreePixmap(display,cursormask);
    XFreeGC(display,gc);
    return cursor;
}

static void install_grabs(void)
{
    int MajorVersion, MinorVersion;

    input_grabbed = true;

    // don't show mouse cursor icon
    XDefineCursor(x_disp, x_win, CreateNullCursor(x_disp, x_win));

    XGrabPointer(x_disp, x_win,
                 True,
                 0,
                 GrabModeAsync, GrabModeAsync,
                 x_win,
                 None,
                 CurrentTime);

#ifdef USE_DGA
    if (!COM_CheckParm("-nodga") &&
            XF86DGAQueryVersion(x_disp, &MajorVersion, &MinorVersion)) {
        // let us hope XF86DGADirectMouse will work
        XF86DGADirectVideo(x_disp, DefaultScreen(x_disp), XF86DGADirectMouse);
        dgamouse = true;
        XWarpPointer(x_disp, None, x_win, 0, 0, 0, 0, 0, 0); // oldman: this should be here really
    }
    else
#endif
        XWarpPointer(x_disp, None, x_win,
                     0, 0, 0, 0,
                     vid.width / 2, vid.height / 2);

    XGrabKeyboard(x_disp, x_win,
                  False,
                  GrabModeAsync, GrabModeAsync,
                  CurrentTime);
}

static void uninstall_grabs(void)
{
    input_grabbed = false;

#ifdef USE_DGA
    XF86DGADirectVideo(x_disp, DefaultScreen(x_disp), 0);
    dgamouse = false;
#endif

    XUngrabPointer(x_disp, CurrentTime);
    XUngrabKeyboard(x_disp, CurrentTime);

    // show cursor again
    XUndefineCursor(x_disp, x_win);

}

extern void Key_EventEx (int key, int unichar, qbool down);
static void GetEvent(void)
{
    XEvent event;
    int b;
    qbool grab_input;

    if (!x_disp)
        return;

    XNextEvent(x_disp, &event);

    switch (event.type)
    {
    case KeyPress:
	case KeyRelease: {
			int keycode;
			wchar unichar;
			keycode = XLateKey(&event.xkey, &unichar);
			Key_EventEx (keycode, unichar, event.type == KeyPress);
		}
        break;

    case MotionNotify:
        if (input_grabbed)
        {
#ifdef USE_DGA
            if (dgamouse)
            {
                mouse_x += event.xmotion.x_root;
                mouse_y += event.xmotion.y_root;
            }
            else
#endif
            {
                mouse_x = (float) ((int)event.xmotion.x - (int)(vid.width/2));
                mouse_y = (float) ((int)event.xmotion.y - (int)(vid.height/2));

                /* move the mouse to the window center again */
                XSelectInput(x_disp, x_win, X_MASK & ~PointerMotionMask);
                XWarpPointer(x_disp, None, x_win, 0, 0, 0, 0,
                             (vid.width/2), (vid.height/2));
                XSelectInput(x_disp, x_win, X_MASK);
            }
        }
        break;

    case ButtonPress:
        b=-1;
        if (event.xbutton.button == 1)
            b = 0;
        else if (event.xbutton.button == 2)
            b = 2;
        else if (event.xbutton.button == 3)
            b = 1;
        if (b>=0)
            Key_Event(K_MOUSE1 + b, true);
        break;

    case ButtonRelease:
        b=-1;
        if (event.xbutton.button == 1)
            b = 0;
        else if (event.xbutton.button == 2)
            b = 2;
        else if (event.xbutton.button == 3)
            b = 1;
        if (b>=0)
            Key_Event(K_MOUSE1 + b, false);
        break;
    }

    grab_input = (_windowed_mouse.value != 0) && (key_dest == key_game);
#ifdef USE_VMODE
	if (vidmode_active)
		grab_input = true;
#endif

    if (grab_input && !input_grabbed) {
        /* grab the pointer */
        install_grabs();
    }
    else if (!grab_input && input_grabbed) {
        /* ungrab the pointer */
        uninstall_grabs();
    }
}

void signal_handler(int sig)
{
    printf("Received signal %d, exiting...\n", sig);
    Sys_Quit();
    exit(0);
}

void InitSig(void)
{
    signal(SIGHUP, signal_handler);
    signal(SIGINT, signal_handler);
    signal(SIGQUIT, signal_handler);
    signal(SIGILL, signal_handler);
    signal(SIGTRAP, signal_handler);
    signal(SIGIOT, signal_handler);
    signal(SIGBUS, signal_handler);
    signal(SIGFPE, signal_handler);
    signal(SIGSEGV, signal_handler);
    signal(SIGTERM, signal_handler);
}


/*
======================
VID_SetDeviceGammaRamp

Note: ramps must point to a static array
======================
*/
void VID_SetDeviceGammaRamp (unsigned short *ramps)
{
#ifdef USE_VMODE
    if (vid_gammaworks)
    {
        currentgammaramp = ramps;
        if (vid_hwgamma_enabled)
        {
            XF86VidModeSetGammaRamp(x_disp, scrnum, 256, ramps, ramps + 256, ramps + 512);
            customgamma = true;
        }
    }
#endif
}

void InitHWGamma (void)
{
#ifdef USE_VMODE
    int xf86vm_gammaramp_size;

    if (COM_CheckParm("-nohwgamma"))
        return;

    XF86VidModeGetGammaRampSize(x_disp, scrnum, &xf86vm_gammaramp_size);

    vid_gammaworks = (xf86vm_gammaramp_size == 256);

    if (vid_gammaworks)
    {
        XF86VidModeGetGammaRamp(x_disp,scrnum,xf86vm_gammaramp_size,
                                systemgammaramp[0], systemgammaramp[1], systemgammaramp[2]);
    }
    vid_hwgamma_enabled = vid_hwgammacontrol.value && vid_gammaworks; // && fullscreen?
#endif
}

void RestoreHWGamma (void)
{
#ifdef USE_VMODE
    if (vid_gammaworks && customgamma)
    {
        customgamma = false;
        XF86VidModeSetGammaRamp(x_disp, scrnum, 256, systemgammaramp[0], systemgammaramp[1], systemgammaramp[2]);
    }
#endif
}

//=================================================================


void GL_CheckExtensions (void)
{
}


void GL_EndRendering (void)
{
    static qbool old_hwgamma_enabled;

    vid_hwgamma_enabled = vid_hwgammacontrol.value && vid_gammaworks;
    if (vid_hwgamma_enabled != old_hwgamma_enabled)
    {
        old_hwgamma_enabled = vid_hwgamma_enabled;
        if (vid_hwgamma_enabled && currentgammaramp)
            VID_SetDeviceGammaRamp (currentgammaramp);
        else
            RestoreHWGamma ();
    }

    glFlush();
    glXSwapBuffers(x_disp, x_win);
}

void VID_Shutdown(void)
{
    if (!ctx)
        return;

    uninstall_grabs();

    RestoreHWGamma();

#ifdef USE_VMODE
    if (x_disp)
    {
        glXDestroyContext(x_disp, ctx);
        if (x_win)
            XDestroyWindow(x_disp, x_win);
        if (vidmode_active)
            XF86VidModeSwitchToMode(x_disp, scrnum, vidmodes[0]);
        XCloseDisplay(x_disp);
        vidmode_active = false;
    }
#else
    glXDestroyContext(x_disp, ctx);
#endif
}

static qbool x_error_caught = false;
static int handler(Display *disp, XErrorEvent *ev)
{
	x_error_caught = true;
	return 0;
}

void VID_Init(unsigned char *palette)
{
    int i;
    int attrib[] = {
                       GLX_RGBA,
                       GLX_RED_SIZE, 1,
                       GLX_GREEN_SIZE, 1,
                       GLX_BLUE_SIZE, 1,
                       GLX_DOUBLEBUFFER,
                       GLX_DEPTH_SIZE, 1,
                       None
                   };
    int width = 640, height = 480;
    XSetWindowAttributes attr;
    unsigned long mask;
    Window root;
    XVisualInfo *visinfo;

#ifdef USE_VMODE
    qbool fullscreen = true;
    int MajorVersion, MinorVersion;
    int actualWidth, actualHeight;
#endif

    Cvar_Register (&vid_ref);
    Cvar_Register (&vid_mode);
    Cvar_Register (&vid_hwgammacontrol);
    Cvar_Register (&_windowed_mouse);
    Cvar_Register (&m_filter);

    // interpret command-line params
    // fullscreen cmdline check
#ifdef USE_VMODE
    if (COM_CheckParm("-window"))
        fullscreen = false;
#endif
    // set vid parameters
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

    if (!(x_disp = XOpenDisplay(NULL)))
    {
        fprintf(stderr, "Error couldn't open the X display\n");
        exit(1);
    }

    scrnum = DefaultScreen(x_disp);
    root = RootWindow(x_disp, scrnum);

#ifdef USE_VMODE
    // check vmode extensions supported
    // Get video mode list
    MajorVersion = MinorVersion = 0;
    if (!XF86VidModeQueryVersion(x_disp, &MajorVersion, &MinorVersion))
    {
        vidmode_ext = false;
    }
    else
    {
        Com_Printf("Using XFree86-VidModeExtension Version %d.%d\n", MajorVersion, MinorVersion);
        vidmode_ext = true;
    }
#endif

    visinfo = glXChooseVisual(x_disp, scrnum, attrib);
    if (!visinfo)
    {
        fprintf(stderr, "qkHack: Error couldn't get an RGB, Double-buffered, Depth visual\n");
        exit(1);
    }

    // setup fullscreen size to fit display -->
#ifdef USE_VMODE
    if (vidmode_ext)
    {
        int best_fit, best_dist, dist, x, y;

        XF86VidModeGetAllModeLines(x_disp, scrnum, &num_vidmodes, &vidmodes);

        // Are we going fullscreen?  If so, let's change video mode
        if (fullscreen)
        {
			XF86VidModeModeLine *current_vidmode;

			// This nice hack comes from the SDL source code
			// makes switching back to original vide mode on shutdown actually work
			// (don't you just love X11?)
			current_vidmode = (XF86VidModeModeLine*)((char*)vidmodes[0] + sizeof(vidmodes[0]->dotclock));
			XF86VidModeGetModeLine(x_disp, scrnum, (int*)&vidmodes[0]->dotclock, current_vidmode);

            best_dist = 9999999;
            best_fit = -1;

            for (i = 0; i < num_vidmodes; i++)
            {
                if (width > vidmodes[i]->hdisplay || height > vidmodes[i]->vdisplay)
                    continue;

                x = width - vidmodes[i]->hdisplay;
                y = height - vidmodes[i]->vdisplay;
                dist = x * x + y * y;
                if (dist < best_dist)
                {
                    best_dist = dist;
                    best_fit = i;
                }
            }

            if (best_fit != -1)
            {
                actualWidth = vidmodes[best_fit]->hdisplay;
                actualHeight = vidmodes[best_fit]->vdisplay;
                // change to the mode
				x_error_caught = false;
				XSetErrorHandler (handler);
                XF86VidModeSwitchToMode(x_disp, scrnum, vidmodes[best_fit]);
				XSync (x_disp, false);
				XSetErrorHandler (NULL);
				if (!x_error_caught)
				{
					vidmode_active = true;
	                // Move the viewport to top left
					XF86VidModeSetViewPort(x_disp, scrnum, 0, 0);
				}
				else
					Com_Printf ("Failed to set fullscreen mode\n");
            }
        }
    }
#endif
    /* window attributes */
    attr.background_pixel = 0;
    attr.border_pixel = 0;
    attr.colormap = XCreateColormap(x_disp, root, visinfo->visual, AllocNone);
    attr.event_mask = X_MASK;
    mask = CWBackPixel | CWBorderPixel | CWColormap | CWEventMask;

    // if fullscreen disable window manager decoration
#ifdef USE_VMODE
    if (vidmode_active)
    {
        mask = CWBackPixel | CWColormap | CWSaveUnder | CWBackingStore |
               CWEventMask | CWOverrideRedirect;
        attr.override_redirect = True;
        attr.backing_store = NotUseful;
        attr.save_under = False;
    }
#endif
    x_win = XCreateWindow(x_disp, root, 0, 0, width, height,
                        0, visinfo->depth, InputOutput,
                        visinfo->visual, mask, &attr);
    XStoreName(x_disp, x_win, PROGRAM);
    XMapWindow(x_disp, x_win);

#ifdef USE_VMODE
    if (vidmode_active)
    {
        XRaiseWindow(x_disp, x_win);
        XWarpPointer(x_disp, None, x_win, 0, 0, 0, 0, 0, 0);
        XFlush(x_disp);
        // Move the viewport to top left
        XF86VidModeSetViewPort(x_disp, scrnum, 0, 0);
    }
#endif
    XFlush(x_disp);

    ctx = glXCreateContext(x_disp, visinfo, NULL, True);

    glXMakeCurrent(x_disp, x_win, ctx);

    vid.realwidth = width;
    vid.realheight = height;

    if (vid.height > height)
        vid.height = height;
    if (vid.width > width)
        vid.width = width;

    vid.aspect = ((float)vid.height / (float)vid.width) * (320.0 / 240.0);
    vid.numpages = 2;

    InitSig(); // trap evil signals

    GL_Init();

    InitHWGamma();

    Com_Printf ("Video mode %dx%d initialized.\n", width, height);

	SCR_InvalidateScreen ();
}

void Sys_SendKeyEvents(void)
{
    if (x_disp)
    {
        while (XPending(x_disp))
            GetEvent();
    }
}

void Force_CenterView_f (void)
{
    cl.viewangles[PITCH] = 0;
}

void IN_Init(void)
{
    Cmd_AddCommand ("force_centerview", Force_CenterView_f);
}

void IN_Shutdown(void)
{}

/*
===========
IN_Commands
===========
*/
void IN_Commands (void)
{}

/*
===========
IN_Move
===========
*/
void IN_MouseMove (usercmd_t *cmd)
{
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

void IN_Move (usercmd_t *cmd)
{
    IN_MouseMove(cmd);
}

/* vi: set noet ts=4 sts=4 ai sw=4: */
