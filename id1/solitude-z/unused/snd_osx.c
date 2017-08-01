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

#include "quakedef.h"
#include "sound.h"

#include <CoreAudio/AudioHardware.h>


#define OUTPUT_BUFFER_SIZE		(2 * 1024)

static AudioDeviceID 			gSndDeviceID;
static unsigned char 			gSndBuffer[64*1024];
static bool						gSndIOProcIsInstalled = false;
static UInt32					gSndBufferPosition,
gSndBufferByteCount;

OSStatus	SNDDMA_AudioIOProc (AudioDeviceID inDevice,
                             const AudioTimeStamp *inNow,
                             const AudioBufferList *inInputData,
                             const AudioTimeStamp *inInputTime,
                             AudioBufferList *outOutputData,
                             const AudioTimeStamp *inOutputTime,
                             void *inClientData)
{
    UInt16	i;
    short	*myDMA = ((short *) gSndBuffer) + gSndBufferPosition / (dma.samplebits >> 3);
    float	*myOutBuffer = (float *) outOutputData->mBuffers[0].mData;

    // convert the buffer to float, required by CoreAudio:
    for (i = 0; i < gSndBufferByteCount; i++)
    {
        *myOutBuffer++ = (*myDMA++) * (1.0f / 32768.0f);
    }

    // increase the bufferposition:
    gSndBufferPosition += gSndBufferByteCount * (dma.samplebits >> 3);
    if (gSndBufferPosition >= sizeof (gSndBuffer))
    {
        gSndBufferPosition = 0;
    }

    // return 0 = no error:
    return 0;
}

bool	SNDDMA_ReserveBufferSize (void)
{
    OSStatus		myError;
    AudioDeviceID	myAudioDevice;
    UInt32		myPropertySize;

    // this function has to be called before any QuickTime movie data is loaded, so that the QuickTime handler
    // knows about our custom buffersize!
    myPropertySize = sizeof (AudioDeviceID);
    myError = AudioHardwareGetProperty (kAudioHardwarePropertyDefaultOutputDevice,
            &myPropertySize,&myAudioDevice);

    if (!myError && myAudioDevice != kAudioDeviceUnknown)
    {
        UInt32		myBufferByteCount = OUTPUT_BUFFER_SIZE * sizeof (float);

        myPropertySize = sizeof (myBufferByteCount);

        // set the buffersize for the audio device:
        myError = AudioDeviceSetProperty (myAudioDevice, NULL, 0, false, kAudioDevicePropertyBufferSize,
                myPropertySize, &myBufferByteCount);

        if (!myError)
        {
            return (true);
        }
    }

    return (false);
}

qbool SNDDMA_Init(void)
{
    AudioStreamBasicDescription	myBasicDescription;
    UInt32 myPropertySize;

    SNDDMA_ReserveBufferSize ();

    Com_Printf ("Initializing CoreAudio...\n");
    myPropertySize = sizeof (gSndDeviceID);

    // find a suitable audio device:
    if (AudioHardwareGetProperty (kAudioHardwarePropertyDefaultOutputDevice, &myPropertySize, &gSndDeviceID))
    {
        Com_Printf ("Audio init fails: Can\t get audio device.\n");
        return false;
    }

    // is the device valid?
    if (gSndDeviceID == kAudioDeviceUnknown)
    {
        Com_Printf ("Audio init fails: Unsupported audio device.\n");
        return false;
    }

    // get the buffersize of the audio device [must previously be set via "SNDDMA_ReserveBufferSize ()"]:
    myPropertySize = sizeof (gSndBufferByteCount);
    if (AudioDeviceGetProperty (gSndDeviceID, 0, false, kAudioDevicePropertyBufferSize,
                                &myPropertySize, &gSndBufferByteCount) || gSndBufferByteCount == 0)
    {
        Com_Printf ("Audio init fails: Can't get audiobuffer.\n");
        return false;
    }

    //check the buffersize:
    gSndBufferByteCount /= sizeof (float);
    if (gSndBufferByteCount != OUTPUT_BUFFER_SIZE)
    {
        Com_Printf ("Audio init: Audiobuffer size is not sufficient for optimized playback!\n");
    }
    if (sizeof (gSndBuffer) % gSndBufferByteCount != 0 ||
            sizeof (gSndBuffer) / gSndBufferByteCount < 2)
    {
        Com_Printf ("Audio init: Bad audiobuffer size!\n");
        return false;
    }

    // get the audiostream format:
    myPropertySize = sizeof (myBasicDescription);
    if (AudioDeviceGetProperty (gSndDeviceID, 0, false, kAudioDevicePropertyStreamFormat,
                                &myPropertySize, &myBasicDescription))
    {
        Com_Printf ("Audio init fails.\n");
        return false;
    }

    // is the format LinearPCM?
    if (myBasicDescription.mFormatID != kAudioFormatLinearPCM)
    {
        Com_Printf ("Default Audio Device doesn't support Linear PCM!\n");
        return(0);
    }

    // is sound ouput suppressed?
    if (!COM_CheckParm ("-nosound"))
    {
        // add the sound FX IO:
        if (AudioDeviceAddIOProc (gSndDeviceID, SNDDMA_AudioIOProc, NULL))
        {
            Com_Printf ("Audio init fails: Can\'t install IOProc.\n");
            return false;
        }

        // start the sound FX:
        if (AudioDeviceStart (gSndDeviceID, SNDDMA_AudioIOProc))
        {
            Com_Printf ("Audio init fails: Can\'t start audio.\n");
            return false;
        }
        gSndIOProcIsInstalled = true;
    }
    else
    {
        gSndIOProcIsInstalled = false;
    }

    // setup Quake sound variables:
    dma.samplebits = 16;
    dma.speed = myBasicDescription.mSampleRate;
    dma.channels = myBasicDescription.mChannelsPerFrame;
    dma.samples = sizeof (gSndBuffer) / (dma.samplebits >> 3);
    dma.samplepos = 0;
    dma.submission_chunk = gSndBufferByteCount;
    dma.buffer = gSndBuffer;
    gSndBufferPosition = 0;

    // output a description of the sound format:
    if (!COM_CheckParm ("-nosound"))
    {
        Com_Printf ("Sound Channels: %d\n", dma.channels);
        Com_Printf ("Sound sample bits: %d\n", dma.samplebits);
    }

    return true;
}

int SNDDMA_GetDMAPos(void)
{
    if (gSndIOProcIsInstalled == false)
    {
        return 0;
    }
    return (gSndBufferPosition / (dma.samplebits >> 3));
}

void SNDDMA_Shutdown(void)
{
    // shut everything down:
    if (gSndIOProcIsInstalled == true)
    {
        AudioDeviceStop (gSndDeviceID, SNDDMA_AudioIOProc);
        AudioDeviceRemoveIOProc (gSndDeviceID, SNDDMA_AudioIOProc);
        gSndIOProcIsInstalled = false;
    }
}

void SNDDMA_Submit(void)
{}

