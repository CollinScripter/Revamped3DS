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

#include "sv_authlists.h"

/*
   FOR DOCUMENTATION ON MAUTH, PLEASE READ ``sv_authlists.h''
*/


/*
===============
SV_AuthListAdd

Adds a player name and hash for that player to the beginning of the selected 
queue.  The hash was generated during auth with the master and is a random
string and their password MD4'd.  It will only last as long as the server is
up and avoids sending their password cleartext so provides some level of 
security in the form of deterrance for snoopers.

The player name and hash are read from the incoming network packet.
===============
*/
qbool SV_AuthListAdd(authqh_t *header)
{
    if( header->curlen == header->maxlen )
    {
        Com_Printf("SV_AuthListAdd: queue full.\n");
        return false;
    }
    
    authclient_t *new = Q_malloc(sizeof(authclient_t));
    char *msgline = NULL;
    char *newname = NULL;
    char *newhash = NULL;

    // Read name from incoming packet...
    msgline = MSG_ReadStringLine();
    if( !msgline )
    {
        Q_free(new);
        Com_Printf("SV_AuthListAdd: Malformed M2S_AUTH_TOK packet from %s.\n", NET_AdrToString (net_from));
        return false;
    }

    // Check that the name has not already been added to our queue...
    if( SV_AuthListFind(header, msgline) != NULL )
    {
        Q_free(new);
        return false;
    }
   
    // Allocate and store name...
    newname = Q_malloc(strlen(msgline)+1);
    new->name = strncpy(newname, msgline, strlen(msgline)+1);

    // Read, allocate and store hash...
    msgline = MSG_ReadStringLine();
    if( !msgline )
    {
        Q_free(newname);
        Q_free(new);
        Com_Printf("SV_AuthListAdd: Malformed M2S_AUTH_TOK packet from %s.\n", NET_AdrToString (net_from));
        return false;
    }
    newhash = Q_malloc(strlen(msgline)+1);
    new->hash = strncpy(newhash, msgline, strlen(msgline)+1);

    // We've not yet been told this is a valid record by the master...
    new->valid = false;

    // Link into beginning of list...
    if( header->start )
    {
        // only if there is a node to link to at start of header!
        header->start->prev = new;
    }
    new->next = header->start;
    new->prev = NULL;
    header->start = new;
    header->curlen++;

    Com_Printf("SV_AuthListAdd: Queued token for %s.\n", new->name);
    return true;
}


/*
===============
SV_AuthListRemove

Unlinks a player record from a list and frees the memory associated with it.
===============
*/
void SV_AuthListRemove(authqh_t *header, authclient_t *rm)
{
    if( rm->prev )
    {
        rm->prev->next = rm->next;
    }
    if( rm->next )
    {
        rm->next->prev = rm->prev;
    }

    Q_free(rm->name);
    Q_free(rm->hash);
    //Q_free(rm->valid);
    Q_free(rm);

    if( header->start == rm )
        header->start = NULL;

    header->curlen--;
}


/*
===============
SV_AuthListMove

Moves a player from the given source to the given destination queue.  They
will be added to the start of the destination queue.

The destination queue may be full -- in which case no move will take place.
Likewise if the destination queue already contains a client of same name.
===============
*/
qbool SV_AuthListMove(authqh_t *src, authqh_t *dest, authclient_t *authclient)
{
    // Check dest is not full...
    if( dest->curlen == dest->maxlen )
    {
        Com_Printf("SV_AuthListMove: destination queue full.\n");
        return false; 
    }
    
    // Check that the name has not already been added to our queue...
    if( SV_AuthListFind(dest, authclient->name) != NULL )
    {
        Com_Printf("SV_AuthListMove: destination queue already contains client.\n");
        return false;
    }
    
    // Unlink from src...
    if( authclient->prev )
    {
        // isnt't at start of list
        authclient->prev->next = authclient->next;
    }
    else
    {
        // is at start of list
        src->start = NULL;
    }
    if( authclient->next )
    {
        // isn't at end of list
        authclient->next->prev = authclient->prev;
    }
    /*else
    {
        // is at end of list
        // <don't need to do anything>
    }*/
    src->curlen--;

    // Hook up to dest...
    if( dest->start )
    {
        // only if there is a node to link to at the start of dest!
        dest->start->prev = authclient;
    }
    authclient->next = dest->start;
    dest->start = authclient;
    dest->start->prev = NULL;
    dest->curlen++;

    return true;
}


/*
===============
SV_AuthListValidate

When a master tells us that the said player is indeed valid, we can set the
valid flag in their record.

The details from the incoming packet are compared with those we have already
stored in the given queue (this will be the queue for new auth information;
when the client actually connects their data will be sent to the queue for
connected clients if the client supplies correct auth info).

IT IS UP TO THE CALLING FUNCTION TO DECIDE IF WE TRUST THIS PACKET THAT WE HAVE
SUPPOSEDLY RECEIVED FROM THE MASTER.
===============
*/
qbool SV_AuthListValidate(authqh_t *header)
{
    authclient_t *testrec;  // compare the incoming details against stored ones
    
    char *msgline = NULL;   // temporary pointer so we can find what
                            //    MSG_ReadStringLine() returned.
    
    // Read name from incoming packet...
    msgline = MSG_ReadStringLine();
    if( !msgline )
    {
        Com_Printf("SV_AuthListValidate: Malformed M2S_AUTH_TOK_ACK packet from %s.\n", NET_AdrToString (net_from));
        return false;
    }

    // Check that the name is listed...
    testrec = SV_AuthListFind(header, msgline);
    if( testrec == NULL )
    {
        Com_Printf("SV_AuthListValidate: Player %s doesn't exist in queue.\n", msgline);
        return false;
    }

    // Grab incoming hash...
    msgline = MSG_ReadStringLine();
    if( !msgline )
    {
        Com_Printf("SV_AuthListValidate: Malformed M2S_AUTH_TOK_ACK packet from %s.\n", NET_AdrToString (net_from));
        return false;
    }

    // Compare incoming details to thsoe stored...
    if( !strcmp(testrec->hash,msgline) )
    {
        Com_Printf("SV_AuthListValidate: Token validated for %s.\n", testrec->name);
        testrec->valid = 1;
        return true;
    }
    else
    {
        Com_Printf("SV_AuthListValidate: Token NOT validated for %s.\n", testrec->name);
        return true;
    }
}


/*
===============
SV_AuthListFind

Ascertain if we already have an entry for the given player name in the
given queue.
===============
*/
authclient_t *SV_AuthListFind(authqh_t *header, char *name)
{
    authclient_t *temp;

    temp = header->start;
    while( temp != NULL )
    {
        if( !strcmp(temp->name, name) )
        {
            return temp;
        }
        temp = temp->next;
    }
    return NULL;
}


/*
===============
SV_AuthListClean

Removes all auth tokens in the given queue that have a valid of zero.

NOTE: Call this on a temporary auth queue (i.e. not the one for clients
      that have connected already) and you'll remove all the tokens!
===============
*/
void SV_AuthListClean(authqh_t *header)
{
    authclient_t *temp;

    temp = header->start;

    Com_Printf("SV_AuthListClean: maxlen %d, curlen %d\n", header->maxlen, header->curlen);

    Com_Printf("\tSV_AuthListClean: start.\n");
    while( temp != NULL )
    {
        Com_Printf("\t\tac: %s, %s, %d\n", temp->name, temp->hash, temp->valid);
        temp = temp->next;
    }
    Com_Printf("\tSV_AuthListClean: end.\n");
}


/*
===============
SV_AuthListPrint

Print out all members of the selected auth details queue.

DO NOT USE THIS IN PRODUCTION CODE
(it prints out sensitive information)
===============
*/
void SV_AuthListPrint(authqh_t *header)
{
    authclient_t *temp;

    temp = header->start;

    Com_Printf("SV_AuthListPrint: maxlen %d, curlen %d\n", header->maxlen, header->curlen);

    Com_Printf("\tSV_AuthListPrint: start.\n");
    while( temp != NULL )
    {
        Com_Printf("\t\tac: %s, %s, %i\n", temp->name, temp->hash, temp->valid);
        temp = temp->next;
    }
    Com_Printf("\tSV_AuthListPrint: end.\n");
}

