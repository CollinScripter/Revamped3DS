// vid_null.c -- null video driver to aid porting efforts

#import	<AppKit/AppKit.h>
#import <IOKit/graphics/IOGraphicsTypes.h>
#import <OpenGL/OpenGL.h>
#import <OpenGL/gl.h>
#import <OpenGL/glu.h>
#import <OpenGL/glext.h>

#import "quakedef.h"
#import "gl_local.h"
#import "vid_osx.h"
#import "in_osx.h"
#import "quakeview.h"

#define VID_MAX_DISPLAYS 		100
#define VID_FADE_DURATION		1.0f

#define VID_GAMMA_TABLE_SIZE	256
#define VID_FONT_WIDTH			8
#define	VID_FONT_HEIGHT			8


//viddef_t	vid;				// global video state

NSWindow	*gVidWindow;
float		gVidWindowPosX, gVidWindowPosY;

NSDictionary *					gVidDisplayMode;
CGDirectDisplayID				gVidDisplayList[VID_MAX_DISPLAYS];
CGDisplayCount					gVidDisplayCount;
NSWindow *						gVidWindow;
BOOL							gVidDisplayFullscreen = YES;
BOOL							gVidFadeAllDisplays;
BOOL							gVidIsMinimized = NO;
UInt32							gVidDisplay;
float							gVidWindowPosX, gVidWindowPosY;
SInt32                          gGLMultiSamples = 0;

//static const float				gGLTruformAmbient[4] = { 1.0f, 1.0f, 1.0f, 1.0f };
//static GLuint					gGLGrowboxTexture;
//static BOOL						gGLGrowboxInitialised = NO;
static NSDictionary *			gGLOriginalMode;
NSOpenGLContext *				gGLContext;
static QuakeView *				gGLWindowView = NULL;
static NSImage *				gGLMiniWindow = NULL;
static NSBitmapImageRep *		gGLMiniWindowBuffer = NULL;
static NSRect					gGLMiniWindowRect;
static BOOL						gGLDisplayIs8Bit;
//static BOOL gGLAnisotropic = NO;
//static BOOL gGLMultiTextureAvailable = NO;
//static BOOL gGLMultiTexture = NO;
UInt32							gGLDisplayWidth, 
gGLDisplayHeight;
static float					gGLVideoWait = 0.0f;
//static float					gGLFSAALevel = 1.0f;
//static float					gGLPNTriangleLevel = -1.0f;

/*
 static SInt8					gGLMenuMaxLine,
gGLMenuLine = VID_FIRST_MENU_LINE;
static vid_menuitem_t           gGLMenuItem = VID_MENUITEM_WAIT;
static vid_glpntrianglesiatix_t	gGLPNTrianglesiATIX = NULL;
static vid_glpntrianglesfatix_t	gGLPNTrianglesfATIX = NULL;
*/

cvar_t	_windowed_mouse = {"_windowed_mouse", "0"};
cvar_t	vid_hwgammacontrol = {"vid_hwgammacontrol","1", 0};
// qbool	vid_hwgamma_enabled = FALSE;
extern qbool	vid_hwgamma_enabled;

cvar_t	vid_vsync = {"vid_vsync", "0"};

extern cvar_t	gl_strings;


//FIXMEs
qbool gl_mtexfbskins = false;
qbool gl_mtexable = false;
void GL_CheckExtensions (void) {};
lpMTexFUNC qglMultiTexCoord2f = NULL;
//void Sys_SendKeyEvents (void) {};
void VID_SetDeviceGammaRamp (unsigned short *ramps) {};



//__________________________________________________________________________________________________________________iNTERFACES

#pragma mark =ObjC Interfaces=

@interface NSOpenGLContext (CGLContextAccess)
- (CGLContextObj) cglContext;
@end

#pragma mark -

//___________________________________________________________________________________________________________________vARIABLES


//________________________________________________________________________________iMPLEMENTATION_NSOpenGLContext 
@implementation NSOpenGLContext (CGLContextAccess)

//___________________________________________________________________________________________________cglContext:

- (CGLContextObj) cglContext;
{
    return (_contextAuxiliary);
}

@end

//______________________________________________________________________________________iMPLEMENTATION_QuakeView


void VID_SetCaption (char *text)
{
    if (gVidWindow != NULL)
    {
        NSString	*myTitle = [NSString stringWithCString: text];
        
        if (myTitle != NULL)
        {
            [gVidWindow setTitle: myTitle];
        }
    }
}

void VID_SetPalette (unsigned char *palette)
{
}

void VID_ShiftPalette (unsigned char *palette)
{
}

//___________________________________________________________________________________________________VID_CreateGLPixelFormat()

NSOpenGLPixelFormat *	VID_CreateGLPixelFormat (BOOL theFullscreenMode)
{
    NSOpenGLPixelFormat				*myPixelFormat;
    NSOpenGLPixelFormatAttribute	myAttributeList[32];
    UInt32							myDisplayDepth;
    UInt16							i = 0;
	
    myAttributeList[i++] = NSOpenGLPFANoRecovery;
	
    myAttributeList[i++] = NSOpenGLPFAClosestPolicy;
	
#ifdef VID_HWA_ONLY
    myAttributeList[i++] = NSOpenGLPFAAccelerated;
#endif /* VID_HWA_ONLY */
	
    myAttributeList[i++] = NSOpenGLPFADoubleBuffer;
	
    myAttributeList[i++] = NSOpenGLPFADepthSize;
    myAttributeList[i++] = 1;
	
    myAttributeList[i++] = NSOpenGLPFAAlphaSize;
    myAttributeList[i++] = 0;
    
    myAttributeList[i++] = NSOpenGLPFAStencilSize;
    myAttributeList[i++] = 0;
	
    myAttributeList[i++] = NSOpenGLPFAAccumSize;
    myAttributeList[i++] = 0;
	
    if (theFullscreenMode == YES)
    {
        myDisplayDepth = [[gVidDisplayMode objectForKey: (id)kCGDisplayBitsPerPixel] intValue];
        
        myAttributeList[i++] = NSOpenGLPFAFullScreen;
        myAttributeList[i++] = NSOpenGLPFAScreenMask;
        myAttributeList[i++] = CGDisplayIDToOpenGLDisplayMask (gVidDisplayList[gVidDisplay]);
    }
    else
    {
        myDisplayDepth = [[gGLOriginalMode objectForKey: (id)kCGDisplayBitsPerPixel] intValue];
        myAttributeList[i++] = NSOpenGLPFAWindow;
    }
	
    myAttributeList[i++] = NSOpenGLPFAColorSize;
    myAttributeList[i++] = myDisplayDepth;
	
    if (gGLMultiSamples > 0)
    {
        if (gGLMultiSamples > 8)
        {
            gGLMultiSamples = 8;
        }
        myAttributeList[i++] = NSOpenGLPFASampleBuffers;
        myAttributeList[i++] = 1;
        myAttributeList[i++] = NSOpenGLPFASamples;
        myAttributeList[i++] = gGLMultiSamples;
    }
	
    myAttributeList[i++] = 0;
	
    myPixelFormat = [[NSOpenGLPixelFormat alloc] initWithAttributes: myAttributeList];
    gGLDisplayIs8Bit = (myDisplayDepth == 8);
	
    return (myPixelFormat);
}

//_______________________________________________________________________________________________________________VID_SetWait()

void VID_SetWait (UInt32 theState)
{
	const long params = theState;
	
    // set theState to 1 to enable, to 0 to disable VBL syncing.
    [gGLContext makeCurrentContext];
    if(CGLSetParameter (CGLGetCurrentContext (), kCGLCPSwapInterval, &params) == CGDisplayNoErr)
    {
        gGLVideoWait = vid_vsync.value;
        if (theState == 0)
        {
            Com_Printf ("video wait successfully disabled!\n");
        }
        else
        {
            Com_Printf ("video wait successfully enabled!\n");
        }
    }
    else
    {
        vid_vsync.value = gGLVideoWait;
        Com_Printf ("Error while trying to change video wait!\n");
    }    
}

//_______________________________________________________________________________________________________________VID_SetMode()

void	GL_SetMiniWindowBuffer (void)
{
    if (gGLMiniWindowBuffer == NULL ||
        [gGLMiniWindowBuffer pixelsWide] != gGLDisplayWidth ||
        [gGLMiniWindowBuffer pixelsHigh] != gGLDisplayHeight)
    {
        [gGLMiniWindowBuffer release];
        gGLMiniWindowBuffer = [[NSBitmapImageRep alloc] initWithBitmapDataPlanes: NULL
                                                                      pixelsWide: gGLDisplayWidth
                                                                      pixelsHigh: gGLDisplayHeight
                                                                   bitsPerSample: 8
                                                                 samplesPerPixel: 4
                                                                        hasAlpha: YES
                                                                        isPlanar: NO
                                                                  colorSpaceName: NSDeviceRGBColorSpace
                                                                     bytesPerRow: gGLDisplayWidth * 4
                                                                    bitsPerPixel: 32];
        if (gGLMiniWindowBuffer == NULL)
        {
            Sys_Error ("Unabled to allocate the window buffer!\n");
        }
    }
}


qbool VID_SetDisplayMode (void)
{
    NSOpenGLPixelFormat		*myPixelFormat;
	
    // just for security:
    if (gVidDisplayList == NULL || gVidDisplayCount == 0)
    {
        Sys_Error ("Invalid list of active displays!");
    }

    // save the old display mode:
    gGLOriginalMode = (NSDictionary *) CGDisplayCurrentMode (gVidDisplayList[gVidDisplay]);
    
    if (gVidDisplayFullscreen == YES)
    {
        // hide cursor:
        IN_ShowCursor (NO);
		
        // fade the display(s) to black:
//        VSH_FadeGammaOut (gVidFadeAllDisplays, VID_FADE_DURATION);

        // capture display(s);
        if (VSH_CaptureDisplays (gVidFadeAllDisplays) == NO)
            Sys_Error ("Unable to capture display(s)!");

        // switch the display mode:
        if (CGDisplaySwitchToMode (gVidDisplayList[gVidDisplay], (CFDictionaryRef) gVidDisplayMode)
            != CGDisplayNoErr)
        {
            Sys_Error ("Unable to switch the displaymode!");
        }
    }
    
    // get the pixel format:
    if ((myPixelFormat = VID_CreateGLPixelFormat (gVidDisplayFullscreen)) == NULL)
        Sys_Error ("Unable to find a matching pixelformat. Please try other displaymode(s).");
	
    // initialize the OpenGL context:
    if (!(gGLContext = [[NSOpenGLContext alloc] initWithFormat: myPixelFormat shareContext: nil]))
        Sys_Error ("Unable to create an OpenGL context. Please try other displaymode(s).");
	
    // get rid of the pixel format:
    [myPixelFormat release];
	
    if (gVidDisplayFullscreen)
    {
        // set the OpenGL context to fullscreen:
        if (CGLSetFullScreen ([gGLContext cglContext]) != CGDisplayNoErr)
            Sys_Error ("Unable to use the selected displaymode for fullscreen OpenGL.");
        
        // fade the gamma back:
//        VSH_FadeGammaIn (gVidFadeAllDisplays, 0.0f);
    }
    else
    {
		Com_Printf ("set up the window\n");
		
		// setup the window according to our settings:
		NSRect				myContentRect	= NSMakeRect (0, 0, gGLDisplayWidth, gGLDisplayHeight);
		
        gVidWindow = [[NSWindow alloc] initWithContentRect: myContentRect
                                                 styleMask: NSTitledWindowMask |
			NSClosableWindowMask |
			NSMiniaturizableWindowMask |
			NSResizableWindowMask
                                                   backing: NSBackingStoreBuffered
                                                     defer: NO];
        [gVidWindow setTitle: @"ZQuake-GL"];
		
        gGLWindowView = [[QuakeView alloc] initWithFrame: myContentRect];
		
        if (gGLWindowView == NULL)
        {
            Sys_Error ("Unable to create content view!\n");
        }

        // setup the view for tracking the window location:
        [gVidWindow setDocumentEdited: YES];
        [gVidWindow setMinSize: myContentRect.size];
        [gVidWindow setShowsResizeIndicator: NO];
        [gVidWindow setBackgroundColor: [NSColor blackColor]];
        [gVidWindow useOptimizedDrawing: NO];
        [gVidWindow setContentView: gGLWindowView];
        [gVidWindow makeFirstResponder: gGLWindowView];
        [gVidWindow setDelegate: gGLWindowView];
		
        // attach the OpenGL context to the window:
        [gGLContext setView: [gVidWindow contentView]];
        
        // finally show the window:
		[gVidWindow center];
        [gVidWindow setAcceptsMouseMovedEvents: YES];
        [gVidWindow makeKeyAndOrderFront: nil];
        [gVidWindow makeMainWindow];
		[gVidWindow center];
        [gVidWindow flushWindow];
		
        // setup the miniwindow [if one alloc fails, the miniwindow will not be drawn]:
        gGLMiniWindow = [[NSImage alloc] initWithSize: NSMakeSize (128.0f, 128.0f)];
        gGLMiniWindowRect = NSMakeRect (0.0f, 0.0f, [gGLMiniWindow size].width, [gGLMiniWindow size].height);
        [gGLMiniWindow setFlipped: YES];
//@@        VSH_DisableQuartzInterpolation (gGLMiniWindow);
        
        // obtain window buffer:
        gGLMiniWindowBuffer = [[NSBitmapImageRep alloc] initWithBitmapDataPlanes: NULL
                                                                      pixelsWide: NSWidth (gGLMiniWindowRect)
                                                                      pixelsHigh: NSHeight (gGLMiniWindowRect)
                                                                   bitsPerSample: 8
                                                                 samplesPerPixel: 4
                                                                        hasAlpha: YES
                                                                        isPlanar: NO
                                                                  colorSpaceName: NSDeviceRGBColorSpace
                                                                     bytesPerRow: NSWidth (gGLMiniWindowRect) * 4
                                                                    bitsPerPixel: 32];
        if (gGLMiniWindowBuffer == NULL)
        {
            Sys_Error ("Unabled to allocate the window buffer!\n");
        }
    }
    
    // Lock the OpenGL context to the refresh rate of the display [for clean rendering], if desired:
    VID_SetWait((UInt32) vid_vsync.value);
    
    return (YES);
}

void VID_Init (unsigned char *palette)
{
	int i;
	
	vid.width = 640;
	vid.height = 480;
	vid.aspect = 1.0;
	vid.numpages = 1;
	vid.buffer = NULL;

    Cvar_Register (&vid_vsync);
	Cvar_Register(&vid_hwgammacontrol);
    Cvar_Register (&_windowed_mouse);
//    Cvar_Register (&gl_anisotropic);
//    Cvar_Register (&gl_fsaa);
//    Cvar_Register (&gl_truform);
//    Cvar_Register (&gl_multitexture);

	
	// Tonik:
	// retrieve displays list
    if (CGGetActiveDisplayList (VID_MAX_DISPLAYS, gVidDisplayList, &gVidDisplayCount) != CGDisplayNoErr)
    {
        Sys_Error ("Can\'t build display list!");
    }
    
	// get the list of display modes:
	{
		NSArray		*myDisplayModes;
		CGDirectDisplayID	mySelectedDisplay;
		int			myDisplayIndex = 0;
		
#define SYS_CHECK_MALLOC(MEM_PTR)	if ((MEM_PTR) == NULL) Sys_Error ("Out of memory!");
		
		mySelectedDisplay = gVidDisplayList[myDisplayIndex];
		
		myDisplayModes = [(NSArray *) CGDisplayAvailableModes (mySelectedDisplay) retain];
		SYS_CHECK_MALLOC (myDisplayModes);
		
		gVidDisplayMode = [myDisplayModes objectAtIndex: 8];		// OMG OMG OMG
	}

	if (COM_CheckParm("-window"))
		gVidDisplayFullscreen = NO;
	else if (COM_CheckParm("-fullscreen"))
		gVidDisplayFullscreen = YES;
		
	if (gVidDisplayFullscreen) {
		gGLDisplayWidth  = [[gVidDisplayMode objectForKey: (id)kCGDisplayWidth] intValue];
		gGLDisplayHeight = [[gVidDisplayMode objectForKey: (id)kCGDisplayHeight] intValue];
	} else {
		gGLDisplayWidth  = 640;
		gGLDisplayHeight = 480;
	}
		
	// get width from command line parameters [only for windowed mode]:
    if ((i = COM_CheckParm("-width")))
        gGLDisplayWidth = atoi (com_argv[i+1]);
	
    // get height from command line parameters [only for windowed mode]:
    if ((i = COM_CheckParm("-height")))
        gGLDisplayHeight = atoi (com_argv[i+1]);

	
    // switch the video mode:
    if (VID_SetDisplayMode() == NO)
        Sys_Error ("Can't initialize video!");
	
	vid.realwidth = gGLDisplayWidth;
	vid.realheight = gGLDisplayHeight;
	
    // setup console width according to display width:
    if ((i = COM_CheckParm("-conwidth")) && i + 1 < com_argc)
        vid.width = Q_atoi (com_argv[i+1]);
    else
        vid.width = 320;
	
    vid.width &= 0xfff8; // make it a multiple of eight
	
    // pick a conheight that matches with correct aspect
    vid.height = vid.width * 3 / 4;
	
    // setup console height according to display height:
    if ((i = COM_CheckParm("-conheight")) && i + 1 < com_argc)
        vid.height = Q_atoi (com_argv[i+1]);
    else
        vid.height = 240;
	
    if (vid.width < 320)
        vid.width = 320;
	
    if (vid.height < 200)
        vid.height = 200;
	
    // check the console size:
    if (vid.width > gGLDisplayWidth)
        vid.width = gGLDisplayWidth;
    if (vid.height > gGLDisplayHeight)
        vid.height = gGLDisplayHeight;

    vid.aspect = ((float) vid.height / (float) vid.width) * (320.0f / 240.0f);
    vid.numpages = 2;
	
    // setup OpenGL:
    GL_Init ();
	
    // enable the video options menu:
//    vid_menudrawfn = VID_MenuDraw;
//    vid_menukeyfn = VID_MenuKey;
    
    // finish up initialization:
//    VID_SetPalette (palette);
    Com_Printf ("Video mode %dx%d initialized.\n", gGLDisplayWidth, gGLDisplayHeight);
}

void VID_Shutdown (void)
{
}

void VID_LockBuffer (void)
{
}

void VID_UnlockBuffer (void)
{
}

void VID_Update (vrect_t *rects)
{
}

void GL_EndRendering (void)
{
    // flush OpenGL buffers:
    glFlush ();
    CGLFlushDrawable ([gGLContext cglContext]);//CGLGetCurrentContext ());
		
#if 0
	// set the gamma if fullscreen:
    if (gVidDisplayFullscreen == YES)
    {
        VID_SetGamma ();
		if (cl_multiview.value && CURRVIEW == 1 || !cl_multiview.value) {
			CGLFlushDrawable ([gGLContext cglContext]);//CGLGetCurrentContext ());
	}
    }
    else
    {
        // if minimized, render inside the Dock!
        GL_RenderInsideDock ();
    }
#endif
	
    // check if video_wait changed:
    if(vid_vsync.value != gGLVideoWait)
    {
        VID_SetWait ((UInt32) vid_vsync.value);
    }
	
#if 0
    // check if anisotropic texture filtering changed:
    if (gl_anisotropic.value != gGLAnisotropic)
    {
        GL_SetTextureFilterAnisotropic ((UInt32) gl_anisotropic.value);
    }
	
    // check if vid_fsaa changed:
    if (gl_fsaa.value != gGLFSAALevel)
    {
        GL_SetFSAA ((UInt32) gl_fsaa.value);
    }
	
    // check if truform changed:
    if (gl_truform.value != gGLPNTriangleLevel)
    {
        GL_SetPNTriangles ((SInt32) gl_truform.value);
    }
	
    // check if multitexture changed:
    if (gl_multitexture.value != gGLMultiTexture)
    {
        GL_SetMultiTexture ((UInt32) gl_multitexture.value);
    }
#endif
}

void D_BeginDirectRect (int x, int y, byte *pbitmap, int width, int height)
{
}

void D_EndDirectRect (int x, int y, int width, int height)
{
}
