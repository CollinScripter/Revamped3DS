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

#include "common.h"

#if defined(__linux__) || defined(sun) || defined(darwin) || defined(__APPLE__) || defined(hpux) || defined(__OpenBSD__)
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#endif

#ifdef _WIN32
#include "winquake.h"
#endif

#define	PACKET_HEADER	8

/*

packet header
-------------
31	sequence
1	does this message contain a reliable payload
31	acknowledge sequence
1	acknowledge receipt of even/odd message
16  qport

The remote connection never knows if it missed a reliable message, the
local side detects that it has been dropped by seeing a sequence acknowledge
higher than the last reliable sequence, but without the correct even/odd
bit for the reliable set.

If the sender notices that a reliable message has been dropped, it will be
retransmitted.  It will not be retransmitted again until a message after
the retransmit has been acknowledged and the reliable still failed to get there.

If the sequence number is -1, the packet should be handled without a netcon.

The reliable message can be added to at any time by doing
MSG_Write* (&netchan->message, <data>).

If the message buffer is overflowed, either by a single message, or by
multiple frames worth piling up while the last reliable transmit goes
unacknowledged, the netchan signals a fatal error.

Reliable messages are always placed first in a packet, then the unreliable
message is included if there is sufficient room.

To the receiver, there is no distinction between the reliable and unreliable
parts of the message, they are just processed out as a single larger message.

Illogical packet sequence numbers cause the packet to be dropped, but do
not kill the connection.  This, combined with the tight window of valid
reliable acknowledgement numbers provides protection against malicious
address spoofing.

The qport field is a workaround for bad address translating routers that
sometimes remap the client's source port on a packet during gameplay.

If the base part of the net address matches and the qport matches, then the
channel matches even if the IP port differs.  The IP port should be updated
to the new value before sending out any replies.


*/

#include <time.h>

cvar_t	showpackets = {"showpackets", "0"};
cvar_t	showdrop = {"showdrop", "0"};
cvar_t	qport = {"qport", "0"};

/*
===============
Netchan_Init

===============
*/
void Netchan_Init (void)
{
	int		port;

	// pick a port value that should be nice and random
#ifdef _WIN32
	port = ((int)(timeGetTime()*1000) * time(NULL)) & 0xffff;
#else
	port = ((int)(getpid()+getuid()*1000) * time(NULL)) & 0xffff;
#endif

	Cvar_Register (&showpackets);
	Cvar_Register (&showdrop);
	Cvar_Register (&qport);
	Cvar_SetValue(&qport, port);
}

/*
===============
Netchan_OutOfBand

Sends an out-of-band datagram
================
*/
void Netchan_OutOfBand (netsrc_t sock, netadr_t adr, int length, byte *data)
{
	sizebuf_t	send;
	byte		send_buf[MAX_MSGLEN + PACKET_HEADER];

// write the packet header
	SZ_Init (&send, send_buf, sizeof(send_buf));
	
	MSG_WriteLong (&send, -1);	// -1 sequence means out of band
	SZ_Write (&send, data, length);

// send the datagram
	NET_SendPacket (sock, send.cursize, send.data, adr);
}

/*
===============
Netchan_OutOfBandPrint

Sends a text message in an out-of-band datagram
================
*/
void Netchan_OutOfBandPrint (netsrc_t sock, netadr_t adr, char *format, ...)
{
	va_list		argptr;
	static char		string[8192];		// ??? why static?
	
	va_start (argptr, format);
#ifdef _WIN32
	_vsnprintf (string, sizeof(string) - 1, format, argptr);
	string[sizeof(string) - 1] = '\0';
#else
	vsnprintf (string, sizeof(string), format, argptr);
#endif // _WIN32
	va_end (argptr);

	Netchan_OutOfBand (sock, adr, strlen(string), (byte *)string);
}


/*
==============
Netchan_Setup

called to open a channel to a remote system
==============
*/
void Netchan_Setup (netsrc_t sock, netchan_t *chan, netadr_t adr, int qport)
{
	memset (chan, 0, sizeof(*chan));
	
	chan->sock = sock;
	chan->remote_address = adr;
	chan->qport = qport;

	chan->last_received = curtime;

	SZ_Init (&chan->message, chan->message_buf, sizeof(chan->message_buf));
	chan->message.allowoverflow = true;
	
	chan->rate = 1.0/2500;
}


/*
===============
Netchan_CanPacket

Returns true if the bandwidth choke isn't active
================
*/
#define	MAX_BACKUP	200
qbool Netchan_CanPacket (netchan_t *chan)
{
	// unlimited bandwidth for local client
	if (chan->remote_address.type == NA_LOOPBACK)
		return true;

	if (chan->cleartime < curtime + MAX_BACKUP*chan->rate)
		return true;
	return false;
}


/*
===============
Netchan_CanReliable

Returns true if the bandwidth choke isn't 
================
*/
qbool Netchan_CanReliable (netchan_t *chan)
{
	if (chan->reliable_length)
		return false;			// waiting for ack
	return Netchan_CanPacket (chan);
}

/*
===============
Netchan_Transmit

tries to send an unreliable message to a connection, and handles the
transmition / retransmition of the reliable messages.

A 0 length will still generate a packet and deal with the reliable messages.
================
*/
#define NETFLAG_LENGTH_MASK	0x0000ffff
#define NETFLAG_DATA		0x00010000
#define NETFLAG_ACK			0x00020000
#define NETFLAG_NAK			0x00040000
#define NETFLAG_EOM			0x00080000
#define NETFLAG_UNRELIABLE	0x00100000
#define NETFLAG_CTL			0x80000000

void Netchan_Transmit (netchan_t *chan, int length, byte *data)
{
	extern cvar_t sv_paused;
	sizebuf_t	send;
	byte		send_buf[MAX_MSGLEN + PACKET_HEADER];
	qbool		send_reliable;
	unsigned	w1, w2;
	int			i;

	if (chan->nqprotocol)
	{
		float rate = 5000;	// FIXME

		send.data = send_buf;
		send.maxsize = MAX_NQMSGLEN + PACKET_HEADER;
		send.cursize = 0;

		if (!chan->reliable_length && chan->message.cursize)
		{
			memcpy (chan->reliable_buf, chan->message_buf, chan->message.cursize);
			chan->reliable_length = chan->message.cursize;
			chan->reliable_start = 0;
			chan->message.cursize = 0;
		}

		i = chan->reliable_length - chan->reliable_start;
		if (i>0)
		{
			MSG_WriteLong(&send, 0);
			MSG_WriteLong(&send, LongSwap(chan->reliable_sequence));
			if (i > MAX_NQDATAGRAM)
				i = MAX_NQDATAGRAM;

			SZ_Write (&send, chan->reliable_buf+chan->reliable_start, i);
			if (send.cursize + length < send.maxsize)
			{	//throw the unreliable packet into the same one as the reliable (but not sent reliably)
				SZ_Write (&send, data, length);
				length = 0;
			}


			if (chan->reliable_start+i == chan->reliable_length)
				*(int*)send_buf = BigLong(NETFLAG_DATA | NETFLAG_EOM | send.cursize);
			else
				*(int*)send_buf = BigLong(NETFLAG_DATA | send.cursize);
			NET_SendPacket (chan->sock, send.cursize, send.data, chan->remote_address);

			if (chan->cleartime < curtime)
				chan->cleartime = curtime + send.cursize/(float)rate;
			else
				chan->cleartime += send.cursize/(float)rate;
		}

		//send out the unreliable (if still unsent)
		if (length)
		{
			MSG_WriteLong(&send, 0);
			MSG_WriteLong(&send, LongSwap(chan->outgoing_unreliable));
			chan->outgoing_unreliable++;

			SZ_Write (&send, data, length);

			*(int*)send_buf = BigLong(NETFLAG_UNRELIABLE | send.cursize);
			NET_SendPacket (chan->sock, send.cursize, send.data, chan->remote_address);

			if (chan->cleartime < curtime)
				chan->cleartime = curtime + send.cursize/(float)rate;
			else
				chan->cleartime += send.cursize/(float)rate;

			send.cursize = 0;
		}
		return;
	}

// check for message overflow
	if (chan->message.overflowed)
	{
		chan->fatal_error = true;
		Com_Printf ("%s:Outgoing message overflow\n"
			, NET_AdrToString (chan->remote_address));
		return;
	}

// if the remote side dropped the last reliable message, resend it
	send_reliable = false;

	if (chan->incoming_acknowledged > chan->last_reliable_sequence
	&& chan->incoming_reliable_acknowledged != chan->reliable_sequence)
		send_reliable = true;

// if the reliable transmit buffer is empty, copy the current message out
	if (!chan->reliable_length && chan->message.cursize)
	{
		memcpy (chan->reliable_buf, chan->message_buf, chan->message.cursize);
		chan->reliable_length = chan->message.cursize;
		chan->message.cursize = 0;
		chan->reliable_sequence ^= 1;
		send_reliable = true;
	}

// write the packet header
	SZ_Init (&send, send_buf, sizeof(send_buf));

	w1 = chan->outgoing_sequence | (send_reliable<<31);
	w2 = chan->incoming_sequence | (chan->incoming_reliable_sequence<<31);

	chan->outgoing_sequence++;

	MSG_WriteLong (&send, w1);
	MSG_WriteLong (&send, w2);

	// send the qport if we are a client
	if (chan->sock == NS_CLIENT)
		MSG_WriteShort (&send, chan->qport);

// copy the reliable message to the packet first
	if (send_reliable)
	{
		SZ_Write (&send, chan->reliable_buf, chan->reliable_length);
		chan->last_reliable_sequence = chan->outgoing_sequence;
	}
	
// add the unreliable part if space is available
	if (send.maxsize - send.cursize >= length)
		SZ_Write (&send, data, length);

// send the datagram
	i = chan->outgoing_sequence & (MAX_LATENT-1);
	chan->outgoing_size[i] = send.cursize;
	chan->outgoing_time[i] = curtime;

	NET_SendPacket (chan->sock, send.cursize, send.data, chan->remote_address);

	if (chan->cleartime < curtime)
		chan->cleartime = curtime + send.cursize*chan->rate;
	else
		chan->cleartime += send.cursize*chan->rate;
#ifndef CLIENTONLY
	if (chan->sock == NS_SERVER && sv_paused.value)
		chan->cleartime = curtime;
#endif

	if (showpackets.value)
		Com_Printf ("--> s=%i(%i) a=%i(%i) %i\n"
			, chan->outgoing_sequence
			, send_reliable
			, chan->incoming_sequence
			, chan->incoming_reliable_sequence
			, send.cursize);

}

/*
=================
Netchan_Process

called when the current net_message is from remote_address
modifies net_message so that it points to the packet payload
=================
*/
qbool Netchan_Process (netchan_t *chan)
{
	unsigned		sequence, sequence_ack;
	unsigned		reliable_ack, reliable_message;

// get sequence numbers		
	MSG_BeginReading ();
	sequence = MSG_ReadLong ();
	sequence_ack = MSG_ReadLong ();

	// read the qport if we are a server
	if (chan->sock == NS_SERVER)
		MSG_ReadShort ();

	reliable_message = sequence >> 31;
	reliable_ack = sequence_ack >> 31;

	sequence &= ~(1<<31);	
	sequence_ack &= ~(1<<31);	

	if (showpackets.value)
		Com_Printf ("<-- s=%i(%i) a=%i(%i) %i\n"
			, sequence
			, reliable_message
			, sequence_ack
			, reliable_ack
			, net_message.cursize);

//
// discard stale or duplicated packets
//
	if (sequence <= (unsigned)chan->incoming_sequence)
	{
		if (showdrop.value)
			Com_Printf ("%s:Out of order packet %i at %i\n"
				, NET_AdrToString (chan->remote_address)
				,  sequence
				, chan->incoming_sequence);
		return false;
	}

//
// dropped packets don't keep the message from being used
//
	chan->dropped = sequence - (chan->incoming_sequence+1);
	if (chan->dropped > 0)
	{
		chan->drop_count += 1;

		if (showdrop.value)
			Com_Printf ("%s:Dropped %i packets at %i\n"
			, NET_AdrToString (chan->remote_address)
			, chan->dropped
			, sequence);
	}

//
// if the current outgoing reliable message has been acknowledged
// clear the buffer to make way for the next
//
	if (reliable_ack == (unsigned)chan->reliable_sequence)
		chan->reliable_length = 0;	// it has been received
	
//
// if this message contains a reliable message, bump incoming_reliable_sequence 
//
	chan->incoming_sequence = sequence;
	chan->incoming_acknowledged = sequence_ack;
	chan->incoming_reliable_acknowledged = reliable_ack;
	if (reliable_message)
		chan->incoming_reliable_sequence ^= 1;

//
// the message can now be read from the current message pointer
// update statistics counters
//
	chan->frame_latency = chan->frame_latency*OLD_AVG
		+ (chan->outgoing_sequence-sequence_ack)*(1.0-OLD_AVG);
	chan->frame_rate = chan->frame_rate*OLD_AVG
		+ (curtime - chan->last_received)*(1.0-OLD_AVG);		
	chan->good_count += 1;

	chan->last_received = curtime;

	return true;
}

// returns 0 = bad  1 = datagram   2 = reliable
int NQNetchan_Process(netchan_t *chan)
{
	int header;
	int sequence;
	int drop;

	MSG_BeginReading ();

	header = LongSwap(MSG_ReadLong());
	if (net_message.cursize != (header & NETFLAG_LENGTH_MASK))
		return false;	//size was wrong, couldn't have been ours.

	if (header & NETFLAG_CTL)
		return false;	//huh?

	sequence = LongSwap(MSG_ReadLong());

	if (header & NETFLAG_ACK)
	{
		if (sequence == chan->reliable_sequence)
		{
			chan->reliable_start += MAX_NQDATAGRAM;
			if (chan->reliable_start >= chan->reliable_length)
			{
				chan->reliable_length = 0;	//they got the entire message
				chan->reliable_start = 0;
			}
			chan->incoming_reliable_acknowledged = chan->reliable_sequence;
			chan->reliable_sequence++;

			chan->last_received = curtime;
		}
		else if (sequence < chan->reliable_sequence)
			Com_DPrintf("Stale ack received\n");
		else if (sequence > chan->reliable_sequence)
			Com_DPrintf("Future ack received\n");

		return false;	//don't try execing the 'payload'. I hate ack packets.
	}

	if (header & NETFLAG_UNRELIABLE)
	{
		if (sequence < chan->incoming_unreliable)
		{
			Com_DPrintf("Stale datagram received\n");
			return false;
		}
		drop = sequence - chan->incoming_unreliable - 1;
		if (drop > 0)
		{
			Com_DPrintf("Dropped %i datagrams\n", drop);
			chan->drop_count += drop;
		}
		chan->incoming_unreliable = sequence;

		chan->last_received = curtime;

		chan->incoming_acknowledged++;
		chan->good_count++;
		return 1;
	}

	if (header & NETFLAG_DATA)
	{
		int runt[2];
		//always reply. a stale sequence probably means our ack got lost.
		runt[0] = BigLong(NETFLAG_ACK | 8);
		runt[1] = BigLong(sequence);
		NET_SendPacket (chan->sock, 8, runt, net_from);

		chan->last_received = curtime;
		if (sequence == chan->incoming_reliable_sequence)
		{
			chan->incoming_reliable_sequence++;

			if (chan->in_fragment_length + net_message.cursize-8 >= sizeof(chan->in_fragment_buf))
			{
				chan->fatal_error = true;
				return false;
			}

			memcpy(chan->in_fragment_buf + chan->in_fragment_length, net_message.data+8, net_message.cursize-8);
			chan->in_fragment_length += net_message.cursize-8;

			if (header & NETFLAG_EOM)
			{
				SZ_Clear(&net_message);
				SZ_Write(&net_message, chan->in_fragment_buf, chan->in_fragment_length);
				chan->in_fragment_length = 0;
				MSG_BeginReading();
				return 2;	//we can read it now
			}
		}
		else
			Com_DPrintf("Stale reliable (%i)\n", sequence);
		return false;
	}

	return false;	//not supported.
}
