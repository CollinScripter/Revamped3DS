$Id: README.txt,v 1.15 2009/07/12 12:45:21 danielpharos Exp $

   ########                    ####                  ####    ####
  ####  ####                 ########                ####   ####
 ####    #### ####    #### ####    #### ####    #### ####  ####
 ####    #### ####    #### ####    #### #### ####### #### ####
 ####    #### ####    #### ####    #### #######      ######
 ####    #### ####    #### ############ ####         #### ####
 ####    #### ####    #### ####    #### ####         ####  ####
  ####  ####   ####   #### ####    #### ####         ####   ####
   ########     ########## ####    #### ####         ####    ####
       #####
        #####    Quake Army Knife Readme


Contents
--------

1. What is QuArK?
2. Where can I get QuArK?
3. What are the system requirements for QuArk?
4. How do I install QuArK?
5. How do I get help?
6. What's New
7. License
8. Who works on QuArK?
9. What is the GameCodeList.txt file?


1. What is QuArK?
-----------------

QuArK is the Quake Army Knife, a multi-purpose tool for games based on
or similar to the Quake engine by id Software.  QuArK has the ability
to directly edit maps, and to a limited extent, models, and can
import, export and convert sounds, textures and various other game
assets. It is also able to modify .pak and .pk3 files, as well as
importing compiled BSP's in order to study the entities as well as
add/change/delete entities from these files.

QuArK is completely different from and not related to the desktop
publishing program Quark.

You can find out more about QuArK from the official website at
http://quark.sourceforge.net/.  See also the QuArK Infobase,
located at http://quark.sourceforge.net/infobase/, and the
QuArK Forums at http://quark.sourceforge.net/forums/.


2. Where can I get QuArK?
-------------------------

QuArK for 32-bit Windows is available as a free download from the 
QuArK website as an executable installer or as a zip archive.

The latest release is always available from
http://sourceforge.net/projects/quark.

Source archives are also available, or you could use anonymous cvs to
checkout the sources from our SourceForge cvs repository (the project
name is `quark`).


3. What are the system requirements for QuArk?
----------------------------------------------

Although the exact minimum system requirements are unknown and prone
to changes, you will need at least Windows 95 or compatible to run
QuArK.  You will need about 40 MB of free disk space to install QuArK,
and the minimum amount of RAM needed differs per game, but at least
64 MB is advised.  Almost any Intel Pentium or compatible CPU will be
able to handle QuArK, but the slower the CPU, the slower QuArK will
be.  Also, Internet Explorer 4.0 or higher is needed.
(Note: Although you do not actually need to use Internet Explorer to
display the Infobase files, some components of Internet Explorer are
used by QuArK, so you still need to have it installed.)


4. How do I install QuArK?
--------------------------

4.1. Installation on Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you downloaded a release with an installation program, you need to
run the installer and follow the on-screen instructions.

If you downloaded a snapshot .zip archive, just extract the files to a
directory somewhere on your hard disk.  You might need to extract the
files into a directory containing the latest available version of
QuArK.

If you downloaded the source code, please see the relevant Infobase
pages for instructions for building QuArK.

4.2. Installation on GNU Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For installation instructions for GNU Linux systems, please see:

http://quark.sourceforge.net/infobase/intro.quarkonlinux.installing.html

If you require further assistance, please see the next section.


5. How do I get help?
---------------------

Help on using and developing QuArK is available using the Help menu
(the one with a question mark), which will take you to the QuArK
Infobase (a centralized repository for all QuArK documentation).
N.B. that the Infobase is also available online at the QuArK website.

If you don't know what something does, point at it with the mouse and
look at the bottom left corner of the editor.  If some help is
available on that item, a message saying "Press F1 for help" should
appear.  Well, you guessed it, you press F1 for help.  If any further
info is available, an Infobase button will be in the bottom corner of
the help snippet, and will take you to the relevant Infobase page
or you can simply press F1 a second time to go to that page.

The Help menu also has links you can click on that will take you directly
to the 'QuArK web site' where you will find other links to assist you
and the 'QuArK Forums site' for a wealth of information on the use of QuArK,
specific game it supports, tutorials and the opportunity to join the forums
and post questions and get answers to suit your particular needs.


6. What's New
-------------

Read the `NEWS.txt` file in the same directory as this file, which is the
folder that QuArK was installed in. This file gives a listing of new and
improved items for this installation and previous versions of QuArK in
their distribution order.


7. License
----------

QuArK is distributed under the Gnu Public License.  See `COPYING.txt` in the
same directory as this file, which is the folder that QuArK was installed in.


8. Who works on QuArK?
----------------------

A list of past and present developers of QuArK can be found in the 'AUTHORS.txt'
file in the same directory as this file, which is the folder that QuArK was
installed in. This file also tries to give their last known e-mail address.
However, because some have moved on they may not always still be active, and
might not want to be contacted about QuArK. Please don't bother people this way
is you need help: see section 5.


9. What is the GameCodeList.txt file?
-------------------------------------

When ever a new game is introduced and supported by QuArK a 'Game Code' must be
assigned to it for various reasons of organization and control as to how that
game support is handled by QuArK. This file, located in the QuArK install folder,
gives further detail of how that structure is set up and used as games are added.
