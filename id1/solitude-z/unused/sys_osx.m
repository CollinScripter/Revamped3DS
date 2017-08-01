//___________________________________________________________________________________________________________nFO
// "sys_osx.m" - MacOS X system functions.
//
// Written by:	Axel 'awe' Wefers		[mailto:awe@fruitz-of-dojo.de].
//		©2001-2002 Fruitz Of Dojo 	[http://www.fruitz-of-dojo.de].
//
// Quake™ is copyrighted by id software	[http://www.idsoftware.com].
//
// Version History:
// v1.0.9: Revised the event handling model [Uses now a NSTimer and a subclassed NSApplication instance].
// v1.0.8: Extended the GLQuake and GLQuakeWorld startup dialog with "FSAA Samples" option.
//	   Added dialog to Quake and QuakeWorld to enter and store command line parameters.
//	   Added option to show the startup dialog only when pressing the Option key.
// v1.0.7: From now on you will only be asked to locate the "id1" folder, if the application is not
//	   installed inside the same folder which holds the "id1" folder.
// v1.0.6: Fixed cursor vsisibility on system error.
//         Fixed loss of mouse control after CMD-TABing with the software renderer.
//         Fixed a glitch with the Quake/QuakeWorld options menu [see "menu.c"].
//         Reworked keypad code [is now hardware dependent] to avoid "sticky" keys.
//	   Moved fixing of linebreaks to "cmd.c".
// v1.0.5: Added support for numeric keypad.
//         Added support for paste [CMD-V and "Edit/Paste" menu].
//	   Added support for up to 5 mouse buttons.
//         Added "Connect To Server" service.
//	   Added support for CMD-M, CMD-H and CMD-Q.
//         Added web link to the help menu.
//	   Fixed keyboard repeat after application quit.
// v1.0.4: Changed all vsprintf () calls to vsnprintf (). vsnprintf () is cleaner.
// v1.0.3: Fixed the broken "drag MOD onto Quake icon" method [blame me].
//	   Enabled Num. Lock Key.
// v1.0.2: Reworked settings dialog.
//	   Reenabled keyboard repeat and mousescaling.
//         Some internal changes.
// v1.0.1: Added support for GLQuake.
//	   Obscure characters within the base pathname [like 'ƒ'...] are now allowed.
//	   Better support for case sensitive file systems.
//	   FIX: "mkdir" commmand [for QuakeWorld].
//	   FIX: The "id1" folder had to be lower case. Can now be upper or lower case.
// v1.0:   Initial release.
//______________________________________________________________________________________________________iNCLUDES

#pragma mark =Includes=

#import <AppKit/AppKit.h>
#import <Cocoa/Cocoa.h>
#import <Foundation/Foundation.h>
#import <mach-o/dyld.h>

#import <unistd.h>
#import <signal.h>
#import <stdlib.h>
#import <limits.h>
#import <sys/time.h>
#import <sys/types.h>
#import <unistd.h>
#import <fcntl.h>
#import <stdarg.h>
#import <stdio.h>
#import <sys/ipc.h>
#import <sys/shm.h>
#import <sys/stat.h>
#import <string.h>
#import <ctype.h>
#import <sys/wait.h>
#import <sys/mman.h>
#import <sys/param.h>
#import <errno.h>
#import <drivers/event_status_driver.h>

#if defined(SERVERONLY)

#import "qwsvdef.h"

#else

#import "quakedef.h"
#import "QuakeApplication.h"
#import "Quake.h"
#import "in_osx.h"
#import "sys_osx.h"
#import "vid_osx.h"
#import "keys.h"

#endif /* SERVERONLY */

#pragma mark -

#if 0
//_______________________________________________________________________________________________________dEFINES

#pragma mark =Defines=

#define	SYS_ID1_VALIDATION_FILE		@"/PAK0.PAK"
#define SYS_QWSV_BASE_PATH		"."
#define	SYS_STRING_SIZE			1024				// string size for vsnprintf ().

#pragma mark -

//_____________________________________________________________________________________________________vARIABLES

#pragma mark =Variables=

qboolean			isDedicated;

#if !defined (SERVERONLY)

SInt32				gSysArgCount;
char **				gSysArgValues = NULL;

#else

qboolean			stdin_ready;
cvar_t				sys_nostdout   = {"sys_nostdout","0"};
cvar_t				sys_extrasleep = {"sys_extrasleep","0"};

static BOOL			gSysDoStdIn = YES;

#endif /* SERVERONLY */

#pragma mark -

//___________________________________________________________________________________________fUNCTION_pROTOTYPES

#pragma mark =Function Prototypes=

SInt 		main (SInt, const char **);

#pragma mark -

//____________________________________________________________________________________________________Sys_Init()

#if defined(SERVERONLY)

void Sys_Init (void)
{
    Cvar_RegisterVariable (&sys_nostdout);
    Cvar_RegisterVariable (&sys_extrasleep);
}

#endif /* SERVERONLY */

//______________________________________________________________________________________________Sys_SwitchCase()

void Sys_SwitchCase (char *theString, UInt16 thePosition)
{
    while (theString[thePosition] != 0x00)
    {
        if (theString[thePosition] >= 'a' && theString[thePosition] <= 'z')
        {
            theString[thePosition] += ('A' - 'a');
        }
        else
        {
            if (theString[thePosition] >= 'A' && theString[thePosition] <= 'Z')
                theString[thePosition] += ('a' - 'A');
        }
        thePosition++;
    }
}

//______________________________________________________________________________________Sys_FixForFileNameCase()

void Sys_FixFileNameCase (char *thePath)
{
    FILE	*myFile = NULL;
   
    if ((myFile = fopen (thePath, "rb")) == NULL)
    {
        UInt16		myPathEnd = 0, i;

        for (i = 0; i < strlen (thePath); i++)
        {
            if (thePath[i] == '/')
            {
                myPathEnd = i;
            }
        }
        if (myPathEnd)
        {
            char		myBaseDir[MAXPATHLEN];
            UInt16		myPathStart;

            getcwd (myBaseDir, MAXPATHLEN);
            for (i = 0; thePath[i] != '/'; i++);
            myPathStart = i++;
            while (i <= myPathEnd)
            {
                if (thePath[i] == '/')
                {
                    thePath[i] = 0x00;
                    if (chdir (thePath))
                    {
                        Sys_SwitchCase (thePath, myPathStart);
                        chdir (myBaseDir);
                        if(chdir (thePath))
                        {
                            Sys_SwitchCase (thePath, myPathStart);
                            thePath[i] = '/';
                            chdir (myBaseDir);
                            return;
                        }
                    }
                    myPathStart = i + 1;
                    thePath[i] = '/';
                    chdir (myBaseDir);
                }
                i++;
            }
            chdir (myBaseDir);
        }
        if((i = strlen (thePath)) == 0)
        {
            return;
        } 
        if ((myFile = fopen (thePath, "rb")) == NULL)
        {
            i--;
            while (i)
            {
                if(thePath[i - 1] == '/')
                {
                    break;
                }
                i--;
            }
            Sys_SwitchCase (thePath, i);
            if (!(myFile = fopen (thePath, "rb")))
            {
                Sys_SwitchCase (thePath, i);
            }
        }
    }
    if (myFile != NULL)
    {
        fclose (myFile);
    }
}

//____________________________________________________________________________________________Sys_FileOpenRead()

SInt Sys_FileOpenRead (char *thePath, SInt *theHandle)
{
    SInt		myHandle;
    struct stat		myFileInfo;

    Sys_FixFileNameCase (thePath);

    myHandle = open (thePath, O_RDONLY, 0666);
    *theHandle = myHandle;
    
    if (myHandle == -1)
    {
        return -1;
    }
        
    if (fstat (myHandle, &myFileInfo) == -1)
    {
        Sys_Error ("Can\'t open file \"%s\", reason: \"%s\".", thePath, strerror (errno));
    }
        
    return (myFileInfo.st_size);
}

//___________________________________________________________________________________________Sys_FileOpenWrite()

SInt	Sys_FileOpenWrite (char *thePath)
{
    SInt     myHandle;

    umask (0);
    myHandle = open (thePath, O_RDWR | O_CREAT | O_TRUNC, 0666);
    
    if (myHandle == -1)
    {
        Sys_Error ("Can\'t open file \"%s\" for writing, reason: \"%s\".", thePath, strerror(errno));
    }
        
    return (myHandle);
}

//_______________________________________________________________________________________________Sys_FileClose()

void Sys_FileClose (SInt theHandle)
{
    close (theHandle);
}

//________________________________________________________________________________________________Sys_FileSeek()

void Sys_FileSeek (SInt theHandle, SInt thePosition)
{
    lseek (theHandle, thePosition, SEEK_SET);
}

//________________________________________________________________________________________________Sys_FileRead()

SInt Sys_FileRead (SInt theHandle, void *theDest, SInt theCount)
{
    return (read (theHandle, theDest, theCount));
}

//_______________________________________________________________________________________________Sys_FileWrite()

SInt Sys_FileWrite (SInt theHandle, void *theData, SInt theCount)
{
    return (write (theHandle, theData, theCount));
}

//________________________________________________________________________________________________Sys_FileTime()

int	Sys_FileTime (char *thePath)
{
    struct stat		myBuffer;

    return (stat (thePath, &myBuffer) == -1 ? -1 : myBuffer.st_mtime);
}

//___________________________________________________________________________________________________Sys_mkdir()

void Sys_mkdir (char *thePath)
{
    if (mkdir (thePath, 0777) != -1)
    {
        return;
    }
    
    if (errno != EEXIST)
    {
        Sys_Error ("\"mkdir %s\" failed, reason: \"%s\".", thePath, strerror(errno));
    }
}

//_______________________________________________________________________________________Sys_MakeCodeWriteable()

void Sys_MakeCodeWriteable (UInt32 theStartAddress, UInt32 theLength)
{
    SInt 		myPageSize = getpagesize();
    unsigned long 	myAddress = (theStartAddress & ~(myPageSize - 1)) - myPageSize;
    
#if defined (SERVERONLY)

    fprintf (stderr, "writable code %lx(%lx)-%lx, length=%lx\n", theStartAddress, myAddress,
                                                                 theStartAddress + theLength, theLength);

#endif /* SERVERONLY */

    if (mprotect ((char*)myAddress, theLength + theStartAddress - myAddress + myPageSize, 7) < 0)
    {
        Sys_Error ("Memory protection change failed!\n");
    }
}

//___________________________________________________________________________________________________Sys_Error()

void Sys_Error (char *theError, ...)
{
    va_list     myArgPtr;
    char        myString[SYS_STRING_SIZE];

    fcntl (0, F_SETFL, fcntl (0, F_GETFL, 0) & ~FNDELAY);
    
    va_start (myArgPtr, theError);
    vsnprintf (myString, SYS_STRING_SIZE, theError, myArgPtr);
    va_end (myArgPtr);

#ifdef SERVERONLY

    fprintf (stderr, "Error: %s\n", myString);
    
    exit (1);

#else

    Host_Shutdown();
    [[NSApp delegate] setHostInitialized: NO];
    
    IN_ShowCursor (YES);
    IN_SetKeyboardRepeatEnabled (YES);
    IN_SetF12EjectEnabled (YES);
    
    NSRunCriticalAlertPanel (@"An error has occured:", [NSString stringWithCString: myString],
                             NULL, NULL, NULL);
    NSLog (@"An error has occured: %@\n", [NSString stringWithCString: myString]);

    exit (1);

#endif /* SERVERONLY */
}

//____________________________________________________________________________________________________Sys_Warn()

void	Sys_Warn (char *theWarning, ...)
{
    va_list     myArgPtr;
    char        myString[SYS_STRING_SIZE];
    
    va_start (myArgPtr, theWarning);
    vsnprintf (myString, SYS_STRING_SIZE, theWarning, myArgPtr);
    va_end (myArgPtr);

#if defined (SERVERONLY)
    fprintf (stderr, "Warning: %s\n", myString);
#else
    NSLog (@"Warning: %s\n", myString);
#endif /* SERVERONLY */
} 

//_________________________________________________________________________________________________Sys_sprintf()

char *	Sys_sprintf (char *theFormat, ...)
{
    va_list     	myArgPtr;
    static char		myString[SYS_STRING_SIZE];
    
    va_start (myArgPtr, theFormat);
    vsnprintf (myString, SYS_STRING_SIZE, theFormat, myArgPtr);
    va_end (myArgPtr);
    
    return(myString);
}

//__________________________________________________________________________________________________Sys_Printf()

void	Sys_Printf (char *theFormat, ...)
{
// only required by qwsv [command line only]:

#if defined(SERVERONLY)
    
    va_list         	myArgPtr;
    unsigned char	*myChar;
    char		myString[SYS_STRING_SIZE * 2];
    
    if (sys_nostdout.value != 0.0f)
    {
        return;
    }
    
    va_start (myArgPtr, theFormat);
    vsnprintf (myString, SYS_STRING_SIZE * 2, theFormat, myArgPtr);
    va_end (myArgPtr);
    
    for (myChar = (unsigned char *) myString; *myChar; myChar++)
    {
        *myChar &= 0x7f;
        if ((*myChar > 128 || *myChar < 32) && *myChar != 10 && *myChar != 13 && *myChar != 9)
        {
            fprintf (stderr, "[%02x]", *myChar);
        }
        else
        {
            putc (*myChar, stderr);
        }
    }
    
    fflush (stderr);

#else

    return;

#endif /* SERVERONLY */
}

//____________________________________________________________________________________________________Sys_Quit()

void	Sys_Quit (void)
{
#if !defined (SERVERONLY)

#ifdef GLQUAKE

    extern cvar_t	gl_fsaa;
    NSUserDefaults	*myDefaults = [NSUserDefaults standardUserDefaults];
    NSString		*myString;
    SInt		mySamples = gl_fsaa.value;

#endif /* GLQUAKE */

    // shutdown host:
    Host_Shutdown ();
    [[NSApp delegate] setHostInitialized: NO];
    IN_SetKeyboardRepeatEnabled (YES);
    IN_SetF12EjectEnabled (YES);
    fcntl (0, F_SETFL, fcntl (0, F_GETFL, 0) & ~FNDELAY);
    fflush (stdout);

#ifdef GLQUAKE

    // save the FSAA setting again [for Radeon users]:
    if (mySamples != 0 && mySamples != 4 && mySamples != 8)
    {
        mySamples = 0;
    }
    myString = [NSString stringWithFormat: @"%d", mySamples];
    if ([myString isEqualToString: INITIAL_GL_SAMPLES])
    {
        [myDefaults removeObjectForKey: DEFAULT_GL_SAMPLES];
    }
    else
    {
        [myDefaults setObject: myString forKey: DEFAULT_GL_SAMPLES];
    }
    [myDefaults synchronize];

#endif /* GLQUAKE */
    
#endif /* SERVERONLY */

    exit (0);
}

//_______________________________________________________________________________________________Sys_FloatTime()

double	Sys_FloatTime (void)
{
    struct timeval 	myTimeValue;
    struct timezone 	myTimeZone; 
    static SInt      	myStartSeconds; 
    
    // return deltaT since the first call:
    gettimeofday (&myTimeValue, &myTimeZone);

    if (myStartSeconds == 0)
    {
        myStartSeconds = myTimeValue.tv_sec;
        return (myTimeValue.tv_usec / 1000000.0);
    }
    
    return ((myTimeValue.tv_sec - myStartSeconds) + (myTimeValue.tv_usec / 1000000.0));
}

//____________________________________________________________________________________________Sys_ConsoleInput()

char *	Sys_ConsoleInput (void)
{
    // only required by "qwsv", since it's the only app that runs from the command line:

#if defined (SERVERONLY)

    static char		myText[256];
    SInt		myLength;

    if (stdin_ready == NO || gSysDoStdIn == NO)
    {
        return NULL;
    }
    stdin_ready = 0;
    myLength = read (0, myText, sizeof (myText));
    if (myLength == 0)
    {
        gSysDoStdIn = YES;
	return (NULL);
    }
    if (myLength < 1)
    {
        return(NULL);
    }
    myText[myLength - 1] = 0x00;
    return (myText);

#else

    return (NULL);

#endif /* SERVERONLY */
}

//_________________________________________________________________________________________Sys_HighFPPrecision()

void	Sys_HighFPPrecision (void)
{
}

//__________________________________________________________________________________________Sys_LowFPPrecision()

void	Sys_LowFPPrecision (void)
{
}

//______________________________________________________________________________________________Sys_DoubleTime()

double	Sys_DoubleTime (void)
{
    return (Sys_FloatTime ());
}

//________________________________________________________________________________________________Sys_DebugLog()

void	Sys_DebugLog (char *theFile, char *theFormat, ...)
{
    va_list 		myArgPtr; 
    static char 	myText[SYS_STRING_SIZE];
    SInt 		myFileDescriptor;

    // get the format:
    va_start (myArgPtr, theFormat);
    vsnprintf (myText, SYS_STRING_SIZE, theFormat, myArgPtr);
    va_end (myArgPtr);

    // append the message to the debug logfile:
    myFileDescriptor = open (theFile, O_WRONLY | O_CREAT | O_APPEND, 0666);
    write (myFileDescriptor, myText, strlen (myText));
    close (myFileDescriptor);
}

//__________________________________________________________________________________________Sys_GetProcAddress()

#if !defined (SERVERONLY)

void *	Sys_GetProcAddress (const char *theName, Boolean theSafeMode)
{
    NSSymbol	mySymbol = NULL;
    char *	mySymbolName = malloc (strlen (theName) + 2);

    if (mySymbolName != NULL)
    {
        strcpy (mySymbolName + 1, theName);
        mySymbolName[0] = '_';

        mySymbol = NULL;
        if (NSIsSymbolNameDefined (mySymbolName))
            mySymbol = NSLookupAndBindSymbol (mySymbolName);

        free (mySymbolName);
    }
    
    if (theSafeMode == YES && mySymbol == NULL)
    {
        Sys_Error ("Failed to import a required function!\n");
    }
    
    return ((mySymbol != NULL) ? NSAddressOfSymbol (mySymbol) : NULL);
}

//________________________________________________________________________________________Sys_GetClipboardData()

char *	Sys_GetClipboardData (void)
{
    NSPasteboard	*myPasteboard = NULL;
    NSArray 		*myPasteboardTypes = NULL;

    myPasteboard = [NSPasteboard generalPasteboard];
    myPasteboardTypes = [myPasteboard types];
    if ([myPasteboardTypes containsObject: NSStringPboardType])
    {
        NSString	*myClipboardString;

        myClipboardString = [myPasteboard stringForType: NSStringPboardType];
        if (myClipboardString != NULL && [myClipboardString length] > 0)
        {
            return (strdup ([myClipboardString cString]));
        }
    }
    return (NULL);
}

//_____________________________________________________________________________________Sys_CheckForIDDirectory()

void	Sys_CheckForIDDirectory (void)
{
    char		*myBaseDir = NULL;
    SInt		myResult,
                        myPathLength;
    BOOL		myFirstRun = YES,
                        myDefaultPath = YES,
                        myPathChanged = NO,
                        myIDPath = NO;
    NSOpenPanel		*myOpenPanel;
    NSUserDefaults 	*myDefaults;
    NSArray		*myFolder;
    NSString		*myValidatePath = NULL,
                        *myBasePath = NULL;

    // get the user defaults:
    myDefaults = [NSUserDefaults standardUserDefaults];

    // prepare the open panel for requesting the "id1" folder:
    myOpenPanel = [NSOpenPanel openPanel];
    [myOpenPanel setAllowsMultipleSelection: NO];
    [myOpenPanel setCanChooseFiles: NO];
    [myOpenPanel setCanChooseDirectories: YES];
    [myOpenPanel setTitle: @"Please locate the \"id1\" folder:"];
    
    // get the "id1" path from the prefs:
    myBasePath = [myDefaults stringForKey: DEFAULT_BASE_PATH];
    
    while (1)
    {
        if (myBasePath != NULL)
        {
            // check if the path exists:
            myValidatePath = [myBasePath stringByAppendingPathComponent: SYS_ID1_VALIDATION_FILE];
            myIDPath = [[NSFileManager defaultManager] fileExistsAtPath: myValidatePath];
            if (myIDPath == YES)
            {
                // get a POSIX version of the path:
                myBaseDir = (char *) [myBasePath fileSystemRepresentation];
                myPathLength = strlen (myBaseDir);
                
                // check if the last component was "id1":
                if (myPathLength >= 3)
                {
                    if ((myBaseDir[myPathLength - 3] == 'i' || myBaseDir[myPathLength - 3] == 'I') &&
                        (myBaseDir[myPathLength - 2] == 'd' || myBaseDir[myPathLength - 2] == 'D') &&
                         myBaseDir[myPathLength - 1] == '1')
                    {
                        // remove "id1":
                        myBaseDir[myPathLength - 3] = 0x00;
                        
                        // change working directory to the selected path:
                        if (!chdir (myBaseDir))
                        {
                            if (myPathChanged)
                            {
                                [myDefaults setObject: myBasePath forKey: DEFAULT_BASE_PATH];
                                [myDefaults synchronize];
                            }
                            break;
                        }
                        else
                        {
                            NSRunCriticalAlertPanel (@"Can\'t change to the selected path!",
                                                     @"The selection was: \"%@\"", NULL, NULL, NULL,
                                                     myBasePath);
                        }
                    }
                }
            }
        }
        
        // if the path from the user defaults is bad, look if the id1 folder is located at the same
        // folder as our Quake application:
        if (myDefaultPath == YES)
        {
            myBasePath = [[[[NSBundle mainBundle] bundlePath] stringByDeletingLastPathComponent]
                                              stringByAppendingPathComponent: INITIAL_BASE_PATH];
            myPathChanged = YES;
            myDefaultPath = NO;
            continue;
        }
        else
        {
            // if we run for the first time or the location of the "id1" folder changed, show a dialog:
            if (myFirstRun == YES)
            {
                NSRunInformationalAlertPanel (@"You will now be asked to locate the \"id1\" folder.",
                                              @"This folder is part of the standard installation of "
                                              @"Quake. You will only be asked for it again, if you "
                                              @"change the location of this folder.",
                                              NULL, NULL, NULL);
                myFirstRun = NO;
            }
            else
            {
                if (myIDPath == NO)
                {
                    NSRunInformationalAlertPanel (@"You have not selected the \"id1\" folder.",
                                                  @"The \"id1\" folder comes with the shareware or retail "
                                                  @"version of Quake and has to contain at least the two "
                                                  @"files \"PAK0.PAK\" and \"PAK1.PAK\".",
                                                  NULL, NULL, NULL);
                }
            }

        }
        
        // request the "id1" folder:
        myResult = [myOpenPanel runModalForDirectory:nil file: nil types: nil];
        
        // if the user selected "Cancel", quit Quake:
        if (myResult == NSCancelButton)
        {
            [NSApp terminate: nil];
        }
        
        // get the selected path:
        myFolder = [myOpenPanel filenames];
        if (![myFolder count])
        {
            continue;
        }
        myBasePath = [myFolder objectAtIndex: 0];
        myPathChanged = YES;
    }
    
    // just check if the mod is located at the same folder as the id1 folder:
    if ([[NSApp delegate] wasDragged] == YES &&
        [[[NSApp delegate] modFolder] isEqualToString: [myBasePath stringByDeletingLastPathComponent]] == NO)
    {
        Sys_Error ("The mission pack has to be located within the same folder as the \"id1\" folder.");
    }
}

//________________________________________________________________________________________Sys_CheckSpecialKeys()

int	Sys_CheckSpecialKeys (int theKey)
{
    extern qboolean	keydown[];
    int			myKey;

    // do a fast evaluation:
    if (keydown[K_COMMAND] == false)
    {
        return (0);
    }
    
    myKey = toupper (theKey);
    
    // check the keys:
    switch (myKey)
    {
        case K_TAB:
        case 'H':
            if (gVidDisplayFullscreen == NO)
            {
                // hide application if windowed [CMD-TAB handled by system]:
                if (myKey == 'H')
                {
                    [NSApp hide: NULL];

                    return (1);
                }
            }
#if !defined (GLQUAKE)
            else
            {
                [NSApp hide: NULL];

                return (1);
            }
#endif /* !GLQUAKE */            
            break;
        case 'M':
            // minimize window [CMD-M]:
            if (gVidDisplayFullscreen == NO && gVidIsMinimized == NO && gVidWindow != NULL)
            {
                [gVidWindow miniaturize: NULL];

                return (1);
            }
            break;
        case 'Q':
            // application quit [CMD-Q]:
            [NSApp terminate: NULL];
            return (1);
        case '?':
            if (gVidDisplayFullscreen == NO)
            {
                [NSApp showHelp: NULL];
                
                return (1);
            }
            break;
    }

    // paste [CMD-V] already checked inside "keys.c" and "menu.c"!
    return (0);
}

//___________________________________________________________________________________________Sys_SendKeyEvents()
#endif //!SERVERONLY
#endif //0

void Sys_DoEvents (NSEvent *, NSEventType);

void Sys_SendKeyEvents (void)
{
    NSEvent			*myEvent;
    NSAutoreleasePool 		*myPool;

    // required for [y]es/[n]o dialogs within Quake:
	// (ZQuake doesn't really use them, but just in case)
    myPool = [[NSAutoreleasePool alloc] init];
    myEvent = [NSApp nextEventMatchingMask: NSAnyEventMask
                                 untilDate: [[NSApp delegate] distantPast]
                                    inMode: NSDefaultRunLoopMode
                                   dequeue: YES];
                                        
    Sys_DoEvents (myEvent, [myEvent type]);
    
    [myPool release];
}

//________________________________________________________________________________________________Sys_DoEvents()

void Sys_DoEvents (NSEvent *myEvent, NSEventType myType)
{
    static NSString		*myKeyboardBuffer;
    static CGMouseDelta		myMouseDeltaX, myMouseDeltaY, myMouseWheel;
    static unichar		myCharacter;
    static UInt8		i;
    static UInt16		myKeyPad;
    static UInt32	 	myFilteredMouseButtons, myMouseButtons, myLastMouseButtons = 0, 
                                myKeyboardBufferSize, myFilteredFlags, myFlags, myLastFlags = 0;

    // we check here for events:
    switch (myType)
    {
        // mouse buttons [max. number of supported buttons is defined via IN_MOUSE_BUTTONS]:
        case NSSystemDefined:
            SYS_CHECK_MOUSE_ENABLED ();
            
            if ([myEvent subtype] == 7)
            {
                myMouseButtons = [myEvent data2];
                myFilteredMouseButtons = myLastMouseButtons ^ myMouseButtons;
                
                for (i = 0; i < IN_MOUSE_BUTTONS; i++)
                {
                    if(myFilteredMouseButtons & (1 << i))
                        Key_Event (K_MOUSE1 + i, (myMouseButtons & (1 << i)) ? 1 : 0);
                }
                
                myLastMouseButtons = myMouseButtons;
            }
            break;
        // scroll wheel:
        case NSScrollWheel:
            SYS_CHECK_MOUSE_ENABLED ();
            
            myMouseWheel = [myEvent deltaY];

            if(myMouseWheel > 0)
            {
                Key_Event (K_MWHEELUP, true);
                Key_Event (K_MWHEELUP, false);
            }
            else
            {
                Key_Event (K_MWHEELDOWN, true);
                Key_Event (K_MWHEELDOWN, false);
            }
            break;
           
        // mouse movement:
        case NSMouseMoved:
        case NSLeftMouseDragged:
        case NSRightMouseDragged:
        case NSOtherMouseDragged:
            SYS_CHECK_MOUSE_ENABLED ();
            
            CGGetLastMouseDelta (&myMouseDeltaX, &myMouseDeltaY);
            IN_ReceiveMouseMove (myMouseDeltaX, myMouseDeltaY);
            break;
            
        // key up and down:
        case NSKeyDown:
        case NSKeyUp:
            myKeyboardBuffer = [myEvent charactersIgnoringModifiers];
            myKeyboardBufferSize = [myKeyboardBuffer length];
            
            for (i = 0; i < myKeyboardBufferSize; i++)
            {
                myCharacter = [myKeyboardBuffer characterAtIndex: i];
                
                if ((myCharacter & 0xFF00) ==  0xF700)
                {
                    myCharacter -= 0xF700;
                    if (myCharacter < 0x47)
                    {
                        Key_Event (gInSpecialKey[myCharacter], (myType == NSKeyDown));
                    }
                }
                else
                {
                    myFlags = [myEvent modifierFlags];
                    
                    // v1.0.6: we will now check hardware codes for the keypad,
                    // otherwise we can not distinguish between between keypad numbers
                    // and normal number keys. We will only check for the keypad, if
                    // the flag for the keypad is set!
                    if (myFlags & NSNumericPadKeyMask)
                    {
                        myKeyPad = [myEvent keyCode];
            
                        if (myKeyPad < 0x5D && gInNumPadKey[myKeyPad] != 0x00)
                        {
                            Key_Event (gInNumPadKey[myKeyPad], (myType == NSKeyDown));
                            break;
                        }
                    }
                    if (myCharacter < 0x80)
                    {
                        if (myCharacter >= 'A' && myCharacter <= 'Z')
                            myCharacter += 'a' - 'A';
                        Key_Event (myCharacter, (myType == NSKeyDown));
                    }
                }
            }
            
            break;
        
        // special keys:
        case NSFlagsChanged:
            myFlags = [myEvent modifierFlags];
            myFilteredFlags = myFlags ^ myLastFlags;
            myLastFlags = myFlags;
            
            if (myFilteredFlags & NSAlphaShiftKeyMask)
                Key_Event (K_CAPSLOCK, (myFlags & NSAlphaShiftKeyMask) ? 1:0);
                
            if (myFilteredFlags & NSShiftKeyMask)
                Key_Event (K_SHIFT, (myFlags & NSShiftKeyMask) ? 1:0);
                
            if (myFilteredFlags & NSControlKeyMask)
                Key_Event (K_CTRL, (myFlags & NSControlKeyMask) ? 1:0);
                
            if (myFilteredFlags & NSAlternateKeyMask)
                Key_Event (K_ALT, (myFlags & NSAlternateKeyMask) ? 1:0);
                
            if (myFilteredFlags & NSCommandKeyMask)
                Key_Event (K_COMMAND, (myFlags & NSCommandKeyMask) ? 1:0);
                
            if (myFilteredFlags & NSNumericPadKeyMask)
                Key_Event (KP_NUMLOCK, (myFlags & NSNumericPadKeyMask) ? 1:0);
            
            break;
        
        // pass anything else to NSApp:
        default:
            [NSApp sendSuperEvent: myEvent];
            break;
    }
}

//#endif /* !SERVERONLY */

#pragma mark -

//________________________________________________________________________________________________________main()

#if 0
SInt main (SInt theArgCount, const char **theArgValues)
{
#if defined (SERVERONLY)

    extern SInt		net_socket;

    double		myTime, myOldtime, myNewtime;
    quakeparms_t	myParameters;
    fd_set		myDescriptor;
    struct timeval	myTimeout;
    SInt 		j;

    // do some nice credits:
    Con_Printf ("\n=============================================\n");
    Con_Printf ("QuakeWorld Server for MacOS X -- Version %0.2f\n", MACOSX_VERSION);
    Con_Printf ("        Ported by: awe^fruitz of dojo\n");
    Con_Printf ("     Visit: http://www.fruitz-of-dojo.de\n");
    Con_Printf ("\n        tiger style kung fu is strong\n");
    Con_Printf ("       but our style is more effective!\n");
    Con_Printf ("=============================================\n\n");
    
    // init the server:
    memset (&myParameters, 0, sizeof (myParameters));
    COM_InitArgv (theArgCount, (char **) theArgValues);
    myParameters.argc = com_argc;
    myParameters.argv = com_argv;
    myParameters.basedir = SYS_QWSV_BASE_PATH;    
    myParameters.memsize = 16*1024*1024;
    j = COM_CheckParm("-mem");
    
    if (j) myParameters.memsize = (int) (Q_atof (com_argv[j+1]) * 1024 * 1024);
    if ((myParameters.membase = malloc (myParameters.memsize)) == NULL)
    {
        Sys_Error ("Can't allocate %ld bytes of memory.\n", myParameters.memsize);
    }
        
    SV_Init (&myParameters);
    SV_Frame (0.1);
    
    myOldtime = Sys_DoubleTime () - 0.1;
    
    // our main loop:
    while (1)
    {
        FD_ZERO (&myDescriptor);
	if (gSysDoStdIn == YES)
        {
            FD_SET (0, &myDescriptor);
        }
        FD_SET (net_socket, &myDescriptor);
	
        myTimeout.tv_sec = 1;
	myTimeout.tv_usec = 0;
	if (select (net_socket+1, &myDescriptor, NULL, NULL, &myTimeout) == -1)
            continue;
	stdin_ready = FD_ISSET (0, &myDescriptor);
	myNewtime = Sys_DoubleTime ();
	myTime = myNewtime - myOldtime;
        myOldtime = myNewtime;
	
        SV_Frame (myTime);
        
	if (sys_extrasleep.value)
            usleep (sys_extrasleep.value);
    }	

#else

    // the Finder passes "-psn_x_xxxxxxx". remove it.
    if (theArgCount == 2 && theArgValues[1] != NULL && strstr (theArgValues[1], "-psn_") == theArgValues[1])
    {
        gSysArgCount = 1;
    }
    else
    {
        gSysArgCount = theArgCount;
    }
    gSysArgValues = (char **) theArgValues;

    // just startup the application [if we have no commandline app]:    
    return (NSApplicationMain (theArgCount, theArgValues));

#endif /* SERVERONLY */
}

//___________________________________________________________________________________________________________eOF

#endif



int main_argc;
char **main_argv;

int main(int argc, char *argv[])
{
	main_argc = argc;
	main_argv = argv;
	
    return NSApplicationMain(argc,  (const char **) argv);
}
