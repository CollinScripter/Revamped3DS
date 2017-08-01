/*
Copyright (C) 2005  Matthew T. Atkinson

client authentication -- record management routines

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

#ifndef _SV_AUTHLISTS_H_
#define _SV_AUTHLISTS_H_

#include "q_shared.h"
#include "common.h"

/*
    FIXME disable name command on servers with MAUTH
    FIXME disable team command on servers with AGRIP
*/

/*
    MAUTH DOCUMENTATION

    I have attempted to recreate the spirit of the old QW global stats
    philosophy.  This authentication system is part of the project.  To see
    an example of features it allows us to provide to end users, please visit
    http://stats.agrip.org.uk/

    By ``recreating the spirit'' I have tried to keep the best bits of global
    stats but improve some other parts and keep the whole thing as seamless as
    possible from the user's (client/server admin) point of view.

    This code and the website are Free Software -- please contact me if you
    would like to use the extended master server and the scripts that run that
    site in your own tournaments.
    
    The protocol is designed to provide a stumbling block for spammers and
    spoofers.  It is not meant to be a 100% secure system using public key
    cryptography.  Having said this, the in-built features of the Quake engine
    are used to increase security where possible -- MD4 is used to at least
    prevent passwords being sent plain text.

    The protocol allows a client to authenticate with a master server.  The
    authentication is for a specific game server -- not EVERY game server as
    the pre QW 1.5 implementation allowed.

    Most of the code is in ZQuake CVS, but the rest can be found at:

        http://www.agrip.org.uk/svn/

    This Subversion repository contains a reference implementation of the
    extended QW master server and an authentication client you can use with
    it (for those wishing to investigate adding MAUTH to their QW engines).

    The rest of this rant describes the technical bits as they relate to ZQ.


    AUTHENTICATION PROCESS AND TOKEN HANDLING

    The steps in client authentication and the handling of authentication
    tokens, from the server's perspective, are as follows:

        1.  Client sends C2M_AUTH_INIT to the master.
            This contains:
                + The client's name
                + The server (addr:port) they want to play on

        2.  The master sends back a M2C_AUTH_RND
            This contains the random string that the client must MD4 their
            password with.

        3.  The client produces a hash of their password + the random string
            and sends it back to the master (C2M_AUTH_HASH).

        4.  If the hashes match, the master sends M2S_AUTH_TOK to the server.
            This contains:
                + The player's name
                + The hash computed earlier
            A NACK will be returned to the client if the hash doesn't match
            the one computed by the master.

        5.  The server must check that the token it just recieved really was
            from the master.  It sends S2M_AUTH_TOK_CHK to its master.
            This contains:
                + The player's name
                + The hash it was given in the M2S_AUTH_TOK under question

        6.  The master may ACK or NACK.  At this point the master is free to
            forget about the player's temporary authentication details.

            NOTE THAT THE MECHANISM THE MASTER USES TO TEST THE VALIDITY OF
            PLAYERS IS COMPLETELY UP TO IT -- any method from simply allowing
            everyone, through querying a custom account database to querying
            the local UNIX account database, for example, may be used.

        7.  The server can now be assured that the authentication information
            is correct.  It can store the data in a queue (linked list) of
            ``auth tokens that are waiting for a client to connect''.  These
            are the tokens of clients that have authenticated but not yet
            connected to the server.  The queue only needs to hold a few sets
            of details at a time, as clients should soon connect to the server
            if they really want to.  If the queue becomes full, entries get
            overwritten.

        8.  When the client actually connects to the server, the temporary
            auth tokens queue is checked for their details.  If found, the
            token is moved from the temporary queue to an ``authenticated
            clients'' queue.
            The client supplies the hash to the server through the userinfo
            variable ``mauth_hash''.
            
            IF A CLIENT CONNECTS TO A NON-MAUTH SERVER, THIS USERINFO VARIABLE
            MAY BE MADE PUBLIC, AS THE SERVER DOES NOT KNOW TO REMOVE IT.
            -- However, because it is a once-only value this is not necessarily
            a major disaster.  Yes, MD4 is broken, but as metnioned above, this
            is here mainly as a deterrant.
            
        9.  When the client disconnects, their token is removed from the queue.


    IMPLEMENTATION NOTES

        * The extensions are all activated and used only if MAUTH is defined at
          compile time.

        * As with the password/spectator password userinfo keys, the hash key
          should be removed from the connecting client's userinfo after
          validation.

        * The name command must be DISABLED so that the players can only
          change their names via the official stats website.  This allows
          admins to control when and how players can change their names.
          Maybe it would allow them to migrate the stats to teh new name if
          they wanted.
          
        * Clients connecting on the local loopback are NEVER checked for
          authentication.

        * The ``-nomauth'' commandline option disables the authentication
          checks when a client connects (BUT NOT the handling of auth lists
          and *_AUTH_* network messages.  This is for servers only, of course.
*/

// type that stores details for a client
typedef struct authclient_s
{
    char *name;
    char *hash;
    int valid;
        // when in token queue, is a flag to say if we've validated them with
        // the master (set to 1 when validated).
        // when in connected client queue, is set to 0 when client disconnects
        // (map changes don't involve a disconnect so it is not decremented
        // during map changes).
	struct authclient_s *prev;
	struct authclient_s *next;
} authclient_t;

// header for queues of above type
typedef struct authqh_s
{
    int maxlen;
    int curlen;
    authclient_t *start;
} authqh_t;


qbool SV_AuthListAdd(authqh_t *header);
    // adds an entry to a queue
    // reads name and hash from incomming packet

void SV_AuthListRemove(authqh_t *header, authclient_t *rm);
    // Removes a record from the list, frees associated memory
    // and decrements list length

qbool SV_AuthListMove(authqh_t *src, authqh_t *dest, authclient_t *authclient);
    // adds an entry to a queue
    // reads name and hash from incomming packet

qbool SV_AuthListValidate(authqh_t *header);
    // sets valid bit in an entry if the data is valid according to master
    // reads data on who to validate from incoming packet

authclient_t *SV_AuthListFind(authqh_t *header, char *name);
    // find a player in the queue
    // returns NULL if not found

void SV_AuthListClean(authqh_t *header);
    // Removes all entries that have a valid flag of 0.
    // Call this on a temporary auth queue (i.e. not the one for clients
    // that have connected already) and you'll remove all the tokens!

void SV_AuthListPrint(authqh_t *header);
    // print whole of specified queue


#endif /* _SV_AUTHLISTS_H_ */

