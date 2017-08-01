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
// vid_ddraw.c - experimental Win32 DirectDraw vid driver

#include "quakedef.h"
#include "winquake.h"
#include "resource.h"
#include "d_local.h"
#include "keys.h"
#include "sound.h"


void AppActivate (BOOL fActive, BOOL minimize);

extern qbool Minimized;

HWND	mainwindow;

qbool	DDActive;

int		window_center_x, window_center_y, window_x, window_y, window_width, window_height;
RECT	window_rect;

#define	BASEWIDTH	320
#define	BASEHEIGHT	200

byte	vid_buffer[BASEWIDTH*BASEHEIGHT];
short	zbuffer[BASEWIDTH*BASEHEIGHT];
//byte	surfcache[256*1024];
byte	surfcache[320*200*4];

cvar_t	vid_ref = {"vid_ref", "soft", CVAR_ROM};
cvar_t	_windowed_mouse = {"_windowed_mouse", "0"};

static HICON	hIcon;
static qbool	in_mode_set = false;  // what's it for?
static qbool	vid_initialized = false;


LPDIRECTDRAW lpDirectDraw;
LPDIRECTDRAWSURFACE lpddsFrontBuffer;	// video card display memory front buffer
LPDIRECTDRAWSURFACE lpddsBackBuffer;	// system memory backbuffer
LPDIRECTDRAWSURFACE lpddsOffScreenBuffer;	// system memory backbuffer
LPDIRECTDRAWPALETTE	lpddpPalette;		// DirectDraw palette


LONG WINAPI MainWndProc (HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

modestate_t	modestate = MS_UNINIT;

	HRESULT ddrval;
	DDSURFACEDESC ddsd;
	DDSCAPS ddscaps;
	PALETTEENTRY palentries[256];



byte		currentpalette[1024];



/*
================
VID_SetCaption
================
*/
void VID_SetCaption (char *text)
{
	if (vid_initialized)
		SetWindowText (mainwindow, text);
}


/*
================
VID_UpdateWindowStatus
================
*/
void VID_UpdateWindowStatus (void)
{

	window_rect.left = window_x;
	window_rect.top = window_y;
	window_rect.right = window_x + window_width;
	window_rect.bottom = window_y + window_height;
	window_center_x = (window_rect.left + window_rect.right) / 2;
	window_center_y = (window_rect.top + window_rect.bottom) / 2;

	IN_UpdateClipCursor ();
}



void VID_LockBuffer (void)
{
}

void VID_UnlockBuffer (void)
{
}

void VID_Update (vrect_t *rects)
{
	HRESULT rval;
	RECT r;
	DDSURFACEDESC ddsd;

	r.left = 0;
	r.top = 0;
	r.right = vid.width;
	r.bottom = vid.height;

	lpddsOffScreenBuffer->lpVtbl->Unlock( lpddsOffScreenBuffer
		, vid.buffer /* wtf? -- tonik */ );
	
	if ( ( rval = lpddsBackBuffer->lpVtbl->BltFast( lpddsFrontBuffer,
															0, 0,
															lpddsOffScreenBuffer, 
															&r, 
															DDBLTFAST_WAIT ) ) == DDERR_SURFACELOST )
	{
		// Com_Printf ("DDERR_SURFACELOST\n");
		lpddsBackBuffer->lpVtbl->Restore( lpddsFrontBuffer );
		lpddsBackBuffer->lpVtbl->BltFast( lpddsFrontBuffer,
													0, 0,
													lpddsOffScreenBuffer, 
													&r, 
													DDBLTFAST_WAIT);
	}

	memset( &ddsd, 0, sizeof( ddsd ) );
	ddsd.dwSize = sizeof( ddsd );

	lpddsOffScreenBuffer->lpVtbl->Lock ( lpddsOffScreenBuffer, NULL, &ddsd, DDLOCK_WAIT, NULL );

	vid.buffer = ddsd.lpSurface;
	vid.direct = vid.buffer;
	vid.rowbytes = ddsd.lPitch;

}

void setcurrentpalette (char *palette)
{
	int i;

	for ( i = 0; i < 256; i++ )
	{
		currentpalette[i*4+0] = palette[i*3+0];
		currentpalette[i*4+1] = palette[i*3+1];
		currentpalette[i*4+2] = palette[i*3+2];
	}
}

/*
** DDRAW_SetPalette
**
** Sets the color table in our DIB section, and also sets the system palette
** into an identity mode if we're running in an 8-bit palettized display mode.
**
** The palette is expected to be 1024 bytes, in the format:
**
** R = offset 0
** G = offset 1
** B = offset 2
** A = offset 3
*/
void DDRAW_SetPalette( const unsigned char *pal )
{
	PALETTEENTRY palentries[256];
	int i;

	if (!lpddpPalette)
		return;

	for ( i = 0; i < 256; i++, pal += 4 )
	{
		palentries[i].peRed   = pal[0];
		palentries[i].peGreen = pal[1];
		palentries[i].peBlue  = pal[2];
		palentries[i].peFlags = PC_RESERVED | PC_NOCOLLAPSE;
	}

	if ( lpddpPalette->lpVtbl->SetEntries( lpddpPalette,
		                                        0,
												0,
												256,
												palentries ) != DD_OK )
	{
		//Com_Printf( "DDRAW_SetPalette() - SetEntries failed\n" );
	}
}


void VID_ShiftPalette (unsigned char *palette)
{
	VID_SetPalette (palette);
}

void VID_SetPalette (unsigned char *palette)
{
	setcurrentpalette (palette);
	DDRAW_SetPalette (currentpalette);
}

	

void DDraw_Init (void)
{
	int		i;

	if (DirectDrawCreate (NULL, &lpDirectDraw, NULL) != DD_OK)
		Sys_Error ("DirectDrawCreate failed");

	if (lpDirectDraw->lpVtbl->SetCooperativeLevel (lpDirectDraw, mainwindow,
		DDSCL_EXCLUSIVE | DDSCL_FULLSCREEN ) != DD_OK )
	{
		Sys_Error ("SetCooperativeLevel failed");
	}

	if (lpDirectDraw->lpVtbl->SetDisplayMode (lpDirectDraw, vid.width, vid.height, 8) != DD_OK )
	{
		Sys_Error ("SetDisplayMode failed");
	}

	memset( &ddsd, 0, sizeof( ddsd ) );
	ddsd.dwSize = sizeof( ddsd );
	ddsd.dwFlags = DDSD_CAPS | DDSD_BACKBUFFERCOUNT;
	ddsd.ddsCaps.dwCaps = DDSCAPS_PRIMARYSURFACE | DDSCAPS_FLIP | DDSCAPS_COMPLEX;
	ddsd.dwBackBufferCount = 1;

	Com_Printf ("...creating front buffer: ");
	if ( ( ddrval = lpDirectDraw->lpVtbl->CreateSurface( lpDirectDraw, &ddsd, &lpddsFrontBuffer, NULL ) ) != DD_OK )
	{
		//Com_Printf ("failed - %s\n", DDrawError( ddrval ) );
		Sys_Error ("");
	}
	Com_Printf ( "ok\n" );


	/*
	** create our back buffer
	*/
	ddsd.ddsCaps.dwCaps = DDSCAPS_BACKBUFFER;

	Com_Printf ("...creating back buffer: " );
	if ( ( ddrval = lpddsFrontBuffer->lpVtbl->GetAttachedSurface( lpddsFrontBuffer, &ddsd.ddsCaps, &lpddsBackBuffer ) ) != DD_OK )
	{
		//Com_Printf( "failed - %s\n", DDrawError( ddrval ) );
		//goto fail;
		Sys_Error ("GetAttachedSurface failed");
	}
	Com_Printf( "ok\n" );


	/*
	** create our rendering buffer
	*/
	memset( &ddsd, 0, sizeof( ddsd ) );
	ddsd.dwSize = sizeof( ddsd );
	ddsd.dwFlags = DDSD_WIDTH | DDSD_HEIGHT | DDSD_CAPS;
	ddsd.dwHeight = vid.height;
	ddsd.dwWidth = vid.width;
	ddsd.ddsCaps.dwCaps = DDSCAPS_OFFSCREENPLAIN | DDSCAPS_SYSTEMMEMORY;

	Com_Printf( "...creating offscreen buffer: " );
	if ( ( ddrval = lpDirectDraw->lpVtbl->CreateSurface( lpDirectDraw, &ddsd, &lpddsOffScreenBuffer, NULL ) ) != DD_OK )
	{
		//Com_Printf( "failed - %s\n", DDrawError( ddrval ) );
		goto fail;
	}
	Com_Printf( "ok\n" );


	/*
	** create our DIRECTDRAWPALETTE
	*/
	Com_Printf ( "...creating palette: " );
	if ( ( ddrval = lpDirectDraw->lpVtbl->CreatePalette( lpDirectDraw,
														DDPCAPS_8BIT | DDPCAPS_ALLOW256,
														palentries,
														&lpddpPalette,
														NULL ) ) != DD_OK )
	{
		//Com_Printf( "failed - %s\n", DDrawError( ddrval ) );
		goto fail;
	}
	Com_Printf( "ok\n" );

	Com_Printf( "...setting palette: " );
	if ( ( ddrval = lpddsFrontBuffer->lpVtbl->SetPalette( lpddsFrontBuffer,
														 lpddpPalette ) ) != DD_OK )
	{
		//Com_Printf ("failed - %s\n", DDrawError(ddrval));
		goto fail;
	}
	Com_Printf( "ok\n" );

	DDRAW_SetPalette( ( const unsigned char * ) currentpalette );

	/*
	** lock the back buffer
	*/
	memset( &ddsd, 0, sizeof( ddsd ) );
	ddsd.dwSize = sizeof( ddsd );
	
	Com_Printf ( "...locking backbuffer: " );
	if ( ( ddrval = lpddsOffScreenBuffer->lpVtbl->Lock( lpddsOffScreenBuffer, NULL, &ddsd, DDLOCK_WAIT, NULL ) ) != DD_OK )
	{
		//Com_Printf( "failed - %s\n", DDrawError( ddrval ) );
		goto fail;
	}
	Com_Printf ("ok\n" );

	//*ppbuffer = ddsd.lpSurface;
	vid.buffer = ddsd.lpSurface;
	vid.direct = vid.buffer;

	//*ppitch   = ddsd.lPitch;
	vid.rowbytes = ddsd.lPitch;

	for ( i = 0; i < vid.height; i++ )
	{
		//memset( *ppbuffer + i * *ppitch, 0, *ppitch );
		memset( vid.buffer + i * vid.rowbytes, 0, vid.rowbytes );
	}

//	sww_state.palettized = true;

	modestate = MS_FULLDIB;

	return;

fail:
	Sys_Error ("directdraw failure");
}

void VID_Init (unsigned char *palette)
{
	DWORD		WindowStyle, ExWindowStyle;
	WNDCLASS		wc;
//	HDC				hdc;

	Cvar_Register (&vid_ref);

	vid.width = BASEWIDTH;
	vid.height = BASEHEIGHT;
	vid.aspect = ((float)vid.height / (float)vid.width) *
				(320.0 / 240.0);


//	vid.numpages = 1;
	vid.numpages = 2;	// TESTING

	vid.buffer = vid_buffer;
	vid.rowbytes = BASEWIDTH;
	
	d_pzbuffer = zbuffer;

	D_InitCaches (surfcache, sizeof(surfcache));


	if (hwnd_dialog)
		DestroyWindow (hwnd_dialog);


//create window class
	hIcon = LoadIcon (global_hInstance, MAKEINTRESOURCE (IDI_APPICON));

	/* Register the frame class */
	wc.style         = 0;
	wc.lpfnWndProc   = (WNDPROC)MainWndProc;
	wc.cbClsExtra    = 0;
	wc.cbWndExtra    = 0;
	wc.hInstance     = global_hInstance;
	wc.hIcon         = 0;
	wc.hCursor       = LoadCursor (NULL,IDC_ARROW);
	wc.hbrBackground = NULL;
	wc.lpszMenuName  = 0;
	wc.lpszClassName = "WinQuake";

	if (!RegisterClass (&wc) )
		Sys_Error ("Couldn't register window class");


//create main window
	WindowStyle = WS_POPUP | WS_SYSMENU | WS_CLIPSIBLINGS | WS_CLIPCHILDREN;
/*
	WindowStyle = WS_OVERLAPPED | WS_BORDER | WS_CAPTION | WS_SYSMENU |
				  WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_CLIPSIBLINGS |
				  WS_CLIPCHILDREN;*/
	ExWindowStyle = 0;
	mainwindow = CreateWindowEx (
		ExWindowStyle,
		"WinQuake",
		PROGRAM,
		WindowStyle,
		0, 0,
		320,
		200,
		NULL,
		NULL,
		global_hInstance,
		NULL);
	
	if (!mainwindow)
		Sys_Error ("Couldn't create DIB window");

	ShowWindow (mainwindow, SW_SHOWDEFAULT);
	UpdateWindow (mainwindow);

	setcurrentpalette (palette);

	DDraw_Init ();

	window_width = vid.width;
	window_height = vid.height;

	VID_UpdateWindowStatus ();

	vid_initialized = true;
}


void VID_Shutdown (void)
{
	if (vid_initialized)
	{
		//if (modestate == MS_FULLDIB)
		//	ChangeDisplaySettings (NULL, CDS_FULLSCREEN);

		PostMessage (HWND_BROADCAST, WM_PALETTECHANGED, (WPARAM)mainwindow, (LPARAM)0);
		PostMessage (HWND_BROADCAST, WM_SYSCOLORCHANGE, (WPARAM)0, (LPARAM)0);

		AppActivate(false, false);
		//DestroyDIBWindow ();
		//DestroyFullscreenWindow ();
		//DestroyFullDIBWindow ();

		if (hwnd_dialog)
			DestroyWindow (hwnd_dialog);

		if (mainwindow)
			DestroyWindow(mainwindow);

		//vid_testingmode = 0;
		vid_initialized = 0;
	}
}


/*
================
ClearAllStates
================
*/
void ClearAllStates (void)
{
	extern void IN_ClearStates (void);
	extern qbool keydown[256];
	int		i;
	
// send an up event for each key, to make sure the server clears them all
	for (i=0 ; i<256 ; i++)
	{
		if (keydown[i])
			Key_Event (i, false);
	}

	Key_ClearStates ();
	IN_ClearStates ();
}




void AppActivate(BOOL fActive, BOOL minimize)
/****************************************************************************
*
* Function:     AppActivate
* Parameters:   fActive - True if app is activating
*
* Description:  If the application is activating, then swap the system
*               into SYSPAL_NOSTATIC mode so that our palettes will display
*               correctly.
*
****************************************************************************/
{
	static BOOL	sound_active;

	ActiveApp = fActive;
	Minimized = minimize;

// enable/disable sound on focus gain/loss
	if (!ActiveApp && sound_active)
	{
		S_BlockSound ();
		sound_active = false;
	}
	else if (ActiveApp && !sound_active)
	{
		S_UnblockSound ();
		sound_active = true;
	}

	if (fActive) {
		IN_ActivateMouse ();
		IN_HideMouse ();
	}
	else
	{
		IN_DeactivateMouse ();
		IN_ShowMouse ();
	}
}

/*
===================================================================

MAIN WINDOW

===================================================================
*/

int IN_TranslateKeyEvent (int lParam, int wParam, qbool down);

LONG WINAPI MainWndProc (HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	int				fActive, fMinimized;
	int				temp;
	LONG			lRet = 0;
	PAINTSTRUCT		ps;
	HDC				hdc;

	switch (uMsg)
	{
		case WM_CREATE:
			break;

		case WM_MOVE:
			window_x = (int) LOWORD(lParam);
			window_y = (int) HIWORD(lParam);
			VID_UpdateWindowStatus ();

			//if ((modestate == MS_WINDOWED) && !in_mode_set && !Minimized)
			//	VID_RememberWindowPos ();

			break;

   	    case WM_CLOSE:
		// this causes Close in the right-click task bar menu not to work, but right
		// now bad things happen if Close is handled in that case (garbage and a
		// crash on Win95)
			//if (!in_mode_set)
			{
				if (MessageBox (mainwindow, "Are you sure you want to quit?", "Confirm Exit",
							MB_YESNO | MB_SETFOREGROUND | MB_ICONQUESTION) == IDYES)
				{
					Host_Quit ();
				}
			}
			break;

		case WM_ACTIVATE:
			fActive = LOWORD(wParam);
			fMinimized = (BOOL) HIWORD(wParam);
			AppActivate(!(fActive == WA_INACTIVE), fMinimized);

		// fix the leftover Alt from any Alt-Tab or the like that switched us away
			ClearAllStates ();

			/*if (!in_mode_set)
			{
				if (windc)
					MGL_activatePalette(windc,true);

				VID_SetPalette(vid_curpal);
			}*/

			break;

		case WM_PAINT:
			hdc = GetDC (mainwindow);	// FIXME
			hdc = BeginPaint(hWnd, &ps);

			//Com_Printf ("WM_PAINT\n");	// TESTING

			/*
			if (!in_mode_set && host_initialized) {
				SCR_InvalidateScreen ();
				SCR_UpdateScreen ();
			}
			*/

			EndPaint(hWnd, &ps);
			break;

		case WM_KEYDOWN:
		case WM_SYSKEYDOWN:
			if (!in_mode_set)
				IN_TranslateKeyEvent (lParam, wParam, true);
			break;

		case WM_KEYUP:
		case WM_SYSKEYUP:
			if (!in_mode_set)
				IN_TranslateKeyEvent (lParam, wParam, false);
			break;

	// this is complicated because Win32 seems to pack multiple mouse events into
	// one update sometimes, so we always check all states and look for events
		case WM_LBUTTONDOWN:
		case WM_LBUTTONUP:
		case WM_RBUTTONDOWN:
		case WM_RBUTTONUP:
		case WM_MBUTTONDOWN:
		case WM_MBUTTONUP:
		case WM_XBUTTONDOWN:
		case WM_XBUTTONUP:
		case WM_MOUSEMOVE:
			if (!in_mode_set)
			{
				temp = 0;

				if (wParam & MK_LBUTTON)
					temp |= 1;

				if (wParam & MK_RBUTTON)
					temp |= 2;

				if (wParam & MK_MBUTTON)
					temp |= 4;

				// Win2k/XP let us bind button4 and button5
				if (wParam & MK_XBUTTON1)
					temp |= 8;

				if (wParam & MK_XBUTTON2)
					temp |= 16;

				IN_MouseEvent (temp);
			}
			break;

		// JACK: This is the mouse wheel with the Intellimouse
		// Its delta is either positive or neg, and we generate the proper
		// Event.
		case WM_MOUSEWHEEL: 
			if (in_mwheeltype != MWHEEL_DINPUT)
			{
				in_mwheeltype = MWHEEL_WINDOWMSG;

				if ((short) HIWORD(wParam) > 0) {
					Key_Event(K_MWHEELUP, true);
					Key_Event(K_MWHEELUP, false);
				} else {
					Key_Event(K_MWHEELDOWN, true);
					Key_Event(K_MWHEELDOWN, false);
				}
			}
			break;

		default:
            /* pass all unhandled messages to DefWindowProc */
            lRet = DefWindowProc (hWnd, uMsg, wParam, lParam);
	        break;

	}

    /* return 0 if handled message, 1 if not */
    return lRet;
}



/*
================
D_BeginDirectRect
================
*/
void D_BeginDirectRect (int x, int y, byte *pbitmap, int width, int height)
{
}


/*
================
D_EndDirectRect
================
*/
void D_EndDirectRect (int x, int y, int width, int height)
{
}

