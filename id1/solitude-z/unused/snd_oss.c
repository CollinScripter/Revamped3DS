// Linux OSS Sound Output

#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/shm.h>
#include <sys/wait.h>
#include <linux/soundcard.h>
#include <stdio.h>

#include "quakedef.h"
#include "sound.h"

int audio_fd;
extern int snd_inited;

static int tryrates[] = { 11025, 22051, 44100, 8000 };

qbool SNDDMA_Init_OSS(void)
{

	int rc;
    int fmt;
	int tmp;
    int i;
    char *s;
	struct audio_buf_info info;
	int caps;

// open /dev/dsp, confirm capability to mmap, and get size of dma buffer

    audio_fd = open("/dev/dsp", O_RDWR, O_NONBLOCK);
    if (audio_fd < 0)
	{
		perror("/dev/dsp");
        Com_Printf ("Could not open /dev/dsp\n");
		return 0;
	}

    rc = ioctl(audio_fd, SNDCTL_DSP_RESET, 0);
    if (rc < 0)
	{
		perror("/dev/dsp");
		Com_Printf ("Could not reset /dev/dsp\n");
		close(audio_fd);
		return 0;
	}

	if (ioctl(audio_fd, SNDCTL_DSP_GETCAPS, &caps)==-1)
	{
		perror("/dev/dsp");
        Com_Printf ("Sound driver too old\n");
		close(audio_fd);
		return 0;
	}

	if (!(caps & DSP_CAP_TRIGGER) || !(caps & DSP_CAP_MMAP))
	{
		Com_Printf ("Sorry but your soundcard can't do this\n");
		close(audio_fd);
		return 0;
	}

    if (ioctl(audio_fd, SNDCTL_DSP_GETOSPACE, &info)==-1)
    {   
        perror("GETOSPACE");
		Com_Printf ("Um, can't do GETOSPACE?\n");
		close(audio_fd);
		return 0;
    }
    
// set sample bits & speed

    s = getenv("QUAKE_SOUND_SAMPLEBITS");
    if (s) dma.samplebits = atoi(s);
	else if ((i = COM_CheckParm("-sndbits")) != 0)
		dma.samplebits = atoi(com_argv[i+1]);
	if (dma.samplebits != 16 && dma.samplebits != 8)
    {
        ioctl(audio_fd, SNDCTL_DSP_GETFMTS, &fmt);
        if (fmt & AFMT_S16_LE) dma.samplebits = 16;
        else if (fmt & AFMT_U8) dma.samplebits = 8;
    }

    s = getenv("QUAKE_SOUND_SPEED");
    if (s) dma.speed = atoi(s);
	else if ((i = COM_CheckParm("-sndspeed")) != 0)
		dma.speed = atoi(com_argv[i+1]);
    else
    {
        for (i=0 ; i<sizeof(tryrates)/4 ; i++)
            if (!ioctl(audio_fd, SNDCTL_DSP_SPEED, &tryrates[i])) break;
        dma.speed = tryrates[i];
    }

    s = getenv("QUAKE_SOUND_CHANNELS");
    if (s) dma.channels = atoi(s);
	else if ((i = COM_CheckParm("-sndmono")) != 0)
		dma.channels = 1;
	else if ((i = COM_CheckParm("-sndstereo")) != 0)
		dma.channels = 2;
    else dma.channels = 2;

	dma.samples = info.fragstotal * info.fragsize / (dma.samplebits/8);
	dma.submission_chunk = 1;

// memory map the dma buffer

	dma.buffer = (unsigned char *) mmap(NULL, info.fragstotal
		* info.fragsize, PROT_WRITE, MAP_FILE|MAP_SHARED, audio_fd, 0);
	if (!dma.buffer)
	{
		perror("/dev/dsp");
		Com_Printf ("Could not mmap /dev/dsp\n");
		close(audio_fd);
		return 0;
	}

	tmp = 0;
	if (dma.channels == 2)
		tmp = 1;
    rc = ioctl(audio_fd, SNDCTL_DSP_STEREO, &tmp);
    if (rc < 0)
    {
		perror("/dev/dsp");
        Com_Printf ("Could not set /dev/dsp to stereo=%d", dma.channels);
		close(audio_fd);
        return 0;
    }
	if (tmp)
		dma.channels = 2;
	else
		dma.channels = 1;

    rc = ioctl(audio_fd, SNDCTL_DSP_SPEED, &dma.speed);
    if (rc < 0)
    {
		perror("/dev/dsp");
        Com_Printf ("Could not set /dev/dsp speed to %d", dma.speed);
		close(audio_fd);
        return 0;
    }

    if (dma.samplebits == 16)
    {
        rc = AFMT_S16_LE;
        rc = ioctl(audio_fd, SNDCTL_DSP_SETFMT, &rc);
        if (rc < 0)
		{
			perror("/dev/dsp");
			Com_Printf ("Could not support 16-bit data.  Try 8-bit.\n");
			close(audio_fd);
			return 0;
		}
    }
    else if (dma.samplebits == 8)
    {
        rc = AFMT_U8;
        rc = ioctl(audio_fd, SNDCTL_DSP_SETFMT, &rc);
        if (rc < 0)
		{
			perror("/dev/dsp");
			Com_Printf ("Could not support 8-bit data.\n");
			close(audio_fd);
			return 0;
		}
    }
	else
	{
		perror("/dev/dsp");
		Com_Printf ("%d-bit sound not supported.", dma.samplebits);
		close(audio_fd);
		return 0;
	}

// toggle the trigger & start her up

    tmp = 0;
    rc  = ioctl(audio_fd, SNDCTL_DSP_SETTRIGGER, &tmp);
	if (rc < 0)
	{
		perror("/dev/dsp");
		Com_Printf ("Could not toggle.\n");
		close(audio_fd);
		return 0;
	}
    tmp = PCM_ENABLE_OUTPUT;
    rc = ioctl(audio_fd, SNDCTL_DSP_SETTRIGGER, &tmp);
	if (rc < 0)
	{
		perror("/dev/dsp");
		Com_Printf ("Could not toggle.\n");
		close(audio_fd);
		return 0;
	}

	dma.samplepos = 0;

	return 1;

}

int SNDDMA_GetDMAPos_OSS(void)
{

	struct count_info count;

	if (ioctl(audio_fd, SNDCTL_DSP_GETOPTR, &count)==-1)
	{
		perror("/dev/dsp");
		Com_Printf ("Uh, sound dead.\n");
		close(audio_fd);
		snd_inited = 0;
		return 0;
	}
//	dma.samplepos = (count.bytes / (dma.samplebits / 8)) & (dma.samples-1);
//	fprintf(stderr, "%d    \r", count.ptr);
	dma.samplepos = count.ptr / (dma.samplebits / 8);

	return dma.samplepos;

}

void SNDDMA_Shutdown_OSS(void)
{
    if (dma.buffer) {
        // close it properly, so we can go and restart it later.
	munmap(dma.buffer, dma.samples * (dma.samplebits/8));
    }
}

/*
==============
SNDDMA_Submit

Send sound to device if buffer isn't really the dma buffer
===============
*/
void SNDDMA_Submit_OSS(void)
{
}
