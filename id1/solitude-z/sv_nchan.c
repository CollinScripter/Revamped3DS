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
// sv_nchan.c - user reliable data stream writes

#include "server.h"

static byte backbuf_data[MAX_MSGLEN];
static sizebuf_t backbuf;
static client_t *backbuf_dest;
static qbool backbuf_write_started = false;


void ClientReliableWrite_Begin0 (client_t *cl)
{
	assert (!backbuf_write_started);
	backbuf_write_started = true;
	backbuf_dest = cl;
	SZ_Init (&backbuf, backbuf_data, sizeof(backbuf_data));
}

void ClientReliableWrite_Begin (client_t *cl, int c)
{
	ClientReliableWrite_Begin0 (cl);
	MSG_WriteByte (&backbuf, c);
}

void ClientReliableWrite_End (void)
{
	assert (backbuf_write_started);
	backbuf_write_started = false;

	SV_AddToReliable (backbuf_dest, backbuf.data, backbuf.cursize);
}

void ClientReliableWrite_Angle (float f)
{
	assert (backbuf_write_started);
	MSG_WriteAngle (&backbuf, f);
}

void ClientReliableWrite_Angle16 (float f)
{
	assert (backbuf_write_started);
	MSG_WriteAngle16 (&backbuf, f);
}

void ClientReliableWrite_Byte (int c)
{
	assert (backbuf_write_started);
	MSG_WriteByte (&backbuf, c);
}

void ClientReliableWrite_Char (int c)
{
	assert (backbuf_write_started);
	MSG_WriteChar (&backbuf, c);
}

void ClientReliableWrite_Float (float f)
{
	assert (backbuf_write_started);
	MSG_WriteFloat (&backbuf, f);
}

void ClientReliableWrite_Coord (float f)
{
	assert (backbuf_write_started);
	MSG_WriteCoord (&backbuf, f);
}

void ClientReliableWrite_Long (int c)
{
	assert (backbuf_write_started);
	MSG_WriteLong (&backbuf, c);
}

void ClientReliableWrite_Short (int c)
{
	assert (backbuf_write_started);
	MSG_WriteShort (&backbuf, c);
}

void ClientReliableWrite_String (char *s)
{
	assert (backbuf_write_started);
	MSG_WriteString(&backbuf, s);
}

void ClientReliableWrite_SZ (void *data, int len)
{
	assert (backbuf_write_started);
	SZ_Write (&backbuf, data, len);
}


static void SV_AddToBackbuf (client_t *cl, const byte *data, int size)
{
	if (!cl->num_backbuf) {
		SZ_Init (&cl->backbuf, cl->backbuf_data[0], sizeof(cl->backbuf_data[0]));
		cl->backbuf_size[0] = 0;
		cl->num_backbuf++;
	}

	if (cl->backbuf.cursize + size > cl->backbuf.maxsize) {
		if (cl->num_backbuf == MAX_BACK_BUFFERS) {
			Com_Printf ("WARNING: MAX_BACK_BUFFERS for %s\n", cl->name);
			cl->backbuf.cursize = 0; // don't overflow without allowoverflow set
			cl->netchan.message.overflowed = true; // this will drop the client
			return;
		}
		SZ_Init (&cl->backbuf, cl->backbuf_data[cl->num_backbuf], sizeof(cl->backbuf_data[cl->num_backbuf]));
		cl->backbuf_size[cl->num_backbuf] = 0;
		cl->num_backbuf++;
	}

	// write it to the backbuf
	SZ_Write (&cl->backbuf, data, size);
	cl->backbuf_size[cl->num_backbuf-1] = cl->backbuf.cursize;
}

void SV_AddToReliable (client_t *cl, const byte *data, int size)
{
	/* +1 is so that there's always space for the disconnect message (FIXME) */

	if (!cl->num_backbuf &&
		cl->netchan.message.cursize + size + 1 <= cl->netchan.message.maxsize)
	{
		// it will fit into the current message
		SZ_Write (&cl->netchan.message, data, size);
	}
	else
	{
		// save it for next
		SV_AddToBackbuf (cl, data, size);
	}
}

// flush data from client's reliable buffers to netchan
void SV_FlushBackbuf (client_t *cl)
{
	int i;

	// check to see if we have a backbuf to stick into the reliable
	if (cl->num_backbuf) {
		// will it fit?
		if (cl->netchan.message.cursize + cl->backbuf_size[0] <
			cl->netchan.message.maxsize) {

			Com_DPrintf ("%s: backbuf %d bytes\n",
				cl->name, cl->backbuf_size[0]);

			// it'll fit
			SZ_Write (&cl->netchan.message, cl->backbuf_data[0],
				cl->backbuf_size[0]);
			
			// move along, move along
			for (i = 1; i < cl->num_backbuf; i++) {
				memcpy(cl->backbuf_data[i - 1], cl->backbuf_data[i],
					cl->backbuf_size[i]);
				cl->backbuf_size[i - 1] = cl->backbuf_size[i];
			}

			cl->num_backbuf--;
			if (cl->num_backbuf) {
				SZ_Init (&cl->backbuf, cl->backbuf_data[cl->num_backbuf - 1],
					sizeof(cl->backbuf_data[cl->num_backbuf - 1]));
				cl->backbuf.cursize = cl->backbuf_size[cl->num_backbuf - 1];
			}
		}
	}
}

void SV_ClearBackbuf (client_t *cl)
{
	cl->num_backbuf = 0;
}

// clears both cl->netchan.message and backbuf
void SV_ClearReliable (client_t *cl)
{
	SZ_Clear (&cl->netchan.message);
	SV_ClearBackbuf (cl);
}
