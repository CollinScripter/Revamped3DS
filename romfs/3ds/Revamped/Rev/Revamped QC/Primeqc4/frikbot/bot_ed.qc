/***********************************************
*                                              *
*          FrikBot Waypoint Editor             *
*   "The 'wtf is this doing in my mod' code"   *
*                                              *
***********************************************/

/*
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

float saved1, saved2, saved3, scratch1, scratch2, scratch3, scratch4;
float bytecounter, filecount;

float MENU_MAIN 		= 1;
float MENU_WAYPOINTS 	= 2;
float MENU_LINKS 		= 3;
float MENU_FLAGS 		= 4;
float MENU_FLAGS2		= 5;
float MENU_BOTS 		= 6;
float MENU_WAYLIST	= 7;
// 8 = link way
// 9 = telelink way
// 10 = delete link
// 11 = create link X2
// 12 = delete link x2
// 13 = confirmation of delete all
// 14 = Teleport to way
// 15 = confirmation of delete point

void() BSPDumpWaypoints;
void() QCDumpWaypoints;
void() DumpWaypoints;
/*
// source for the menu strings...

-- Main Menu --\n
[1] >>Waypoint Management\n
[2] >>Link Management    \n
[3] >>AI Flag Management \n
[4] >>Bot Management     \n
[5] >>Waylist Management \n
[6] [#] Noclip           \n
[7] [#] Godmode          \n
[8] [#] Hold Select      \n
[9] Teleport to Way #    \n
[0] Close Menu           \n

// missing from main is show way info
// iffy on the teleport to way thing being on main...seems like either a bot or way list thing

-- Waypoint Management --\n
[1] Move Waypoint        \n
[2] Delete Waypoint      \n
[3] Make Waypoint        \n
[4] Make Way + Link      \n
[5] Make Way + Link X2   \n
[6] Make Way + Telelink  \n
[7] Show waypoint info   \n
[8] >>Link Management    \n
[9] >>AI Flag Management \n
[0] >>Main Menu          \n

-- Link Management --\n
[1] Unlink Waypoint      \n
[2] Create Link          \n
[3] Create Telelink      \n
[4] Delete Link          \n
[5] Create Link X2       \n
[6] Delete Link X2       \n
[7] >Make Waypoint       \n
[8] >>Waypoint Management\n
[9] >>AI Flag Management \n
[0] >>Main Menu          \n

// Ai flags...ugh

-- AI Flag Management --\n
[1] [#] Door Flag        \n
[2] [#] Precision        \n
[3] [#] Surface for air  \n
[4] [#] Blind mode       \n
[5] [#] Jump             \n
[6] [#] Dark             \n
[7] [#] Super Jump       \n
\n
[9] >>AI Flags page 2    \n
[0] >>Main Menu          \n

-- AI Flags pg. 2--\n
[1] [#] Difficult        \n
[2] [#] Wait for plat    \n
[3] [#] Ride train       \n
[4] [#] Door flag no open\n
[5] [#] Ambush           \n
[6] [#] Snipe            \n
[7] [#] Trace Test       \n
\n
[9] >>AI Flag Management \n
[0] >>Main Menu          \n

-- Bot Management --\n
[1] Add a Test Bot       \n
[2] Order Test Bot here  \n
[3] Remove Test Bot      \n
[4] Stop Test Bot        \n
[5] Teleport Bot here    \n
[6] Teleport to Way #    \n
\n
\n
\n
[0] >>Main Menu          \n 

-- Waylist Management --\n
[1] Delete ALL Waypoints \n
[2] Dump Waypoints       \n
[3] Check For Errors     \n
[4] Save Waypoints       \n
[5] [#] Dynamic Mode     \n
[6] [#] Dynamic Link     \n
[7] [#] WAY output       \n
[8] [#] QC output        \n
[9] [#] BSP ents output  \n
[0] Main Menu            \n

*/

void() bot_menu_display =
{
// build options
	local string s1, s2, s3, s4, s5, s6, s7, h;
	local entity t;

// check impulses
	if (self.impulse > 0 && self.impulse < 11 && self.b_menu)
	{
		if (self.b_menu == MENU_MAIN)
		{
			if (self.impulse == 1)
			{
				self.b_menu = MENU_WAYPOINTS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_LINKS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 3)
			{
				self.b_menu = MENU_FLAGS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 4)
			{
				self.b_menu = MENU_BOTS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 5)
			{
				self.b_menu = MENU_WAYLIST;
				self.b_menu_time = time;
			}
			else if (self.impulse == 6)
			{
				if (self.movetype == MOVETYPE_NOCLIP)
					self.movetype = MOVETYPE_WALK;
				else
					self.movetype = MOVETYPE_NOCLIP;
				self.b_menu_time = time;

			}
			else if (self.impulse == 7)
			{
				if (self.flags & FL_GODMODE)
					self.flags = self.flags - FL_GODMODE;
				else
					self.flags = self.flags | FL_GODMODE;
				self.b_menu_time = time;

			}
			else if (self.impulse == 8)
			{
				if (self.b_aiflags & AI_HOLD_SELECT)
					self.b_aiflags = self.b_aiflags - AI_HOLD_SELECT;
				else
					self.b_aiflags = self.b_aiflags | AI_HOLD_SELECT;
				self.b_menu_time = time;
			}
			else if (self.impulse == 9)
			{
				self.b_menu = 14;
				self.b_menu_time = time;
			}
			else if (self.impulse == 10)
				bot_way_edit();
		}
		else if (self.b_menu == MENU_WAYPOINTS)
		{
			if (self.impulse == 1)
			{
				if (self.current_way)
					setorigin(self.current_way, self.origin + self.view_ofs);
			}
			else if (self.impulse == 2)
			{
				if (self.current_way)
				{
					self.b_menu = 15;
					self.b_menu_time = time;
					self.last_way = self.current_way;
				}
			}
			else if (self.impulse == 3)
			{
				make_waypoint(self.origin + self.view_ofs);
			}
			else if (self.impulse == 4)
			{
				t = make_waypoint(self.origin + self.view_ofs);
				if (!LinkWays(self.current_way, t))
					sprint(self, "Unable to link them\n");
			}
			else if (self.impulse == 5)
			{
				t = make_waypoint(self.origin + self.view_ofs);
				if (!LinkWays(self.current_way, t))
					sprint(self, "Unable to link old to new\n");
				LinkWays(t, self.current_way);
			}
			else if (self.impulse == 6)
			{
				t = make_waypoint(self.origin + self.view_ofs);
				if (!TeleLinkWays(self.current_way, t))
					sprint(self, "Unable to link them\n");
			}
			else if (self.impulse == 7)
			{
				if (self.current_way)
				{
					sprint(self, "\nwaypoint info for waypoint #");
					h = ftos(self.current_way.count);
					sprint(self, h);
					sprint(self, "\nAI Flag value: ");
					h = ftos(self.current_way.b_aiflags);
					sprint(self, h);

					if (self.current_way.target1)
					{
						h = ftos(self.current_way.target1.count);
						if (self.current_way.b_aiflags & AI_TELELINK_1)
							sprint(self, "\nTelelink1 to:");
						else
							sprint(self, "\nLink1 to:");
						sprint(self, h);
					}
					if (self.current_way.target2)
					{
						h = ftos(self.current_way.target2.count);
						if (self.current_way.b_aiflags & AI_TELELINK_2)
							sprint(self, "\nTelelink2 to:");
						else
							sprint(self, "\nLink2 to:");
						sprint(self, h);
					}
					if (self.current_way.target3)
					{
						h = ftos(self.current_way.target3.count);
						if (self.current_way.b_aiflags & AI_TELELINK_3)
							sprint(self, "\nTelelink3 to:");
						else
							sprint(self, "\nLink3 to:");
						sprint(self, h);
					}
					if (self.current_way.target4)
					{
						h = ftos(self.current_way.target4.count);
						if (self.current_way.b_aiflags & AI_TELELINK_4)
							sprint(self, "\nTelelink4 to:");
						else
							sprint(self, "\nLink4 to:");
						sprint(self, h);
					}
					sprint(self, "\n\n");
				}

			}
			if (self.impulse == 8)
			{
				self.b_menu = MENU_LINKS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 9)
			{
				self.b_menu = MENU_FLAGS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 10)
			{
				self.b_menu = MENU_MAIN;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == MENU_LINKS)
		{
			if (self.impulse == 1)
			{
				if (self.current_way)
					self.current_way.target1 = self.current_way.target2 = self.current_way.target3 = self.current_way.target4 = world;
			}
			else if (self.impulse == 2)
			{
				self.b_menu = 8;
				self.b_menu_time = time;
				self.last_way = self.current_way;
			}
			else if (self.impulse == 3)
			{
				self.b_menu = 9;
				self.b_menu_time = time;
				self.last_way = self.current_way;
			}
			else if (self.impulse == 4)
			{
				self.b_menu = 10;
				self.b_menu_time = time;
				self.last_way = self.current_way;
			}
			else if (self.impulse == 5)
			{
				self.b_menu = 11;
				self.b_menu_time = time;
				self.last_way = self.current_way;
			}
			else if (self.impulse == 6)
			{
				self.b_menu = 12;
				self.b_menu_time = time;
				self.last_way = self.current_way;
			}
			else if (self.impulse == 7)
				make_waypoint(self.origin + self.view_ofs);
			else if (self.impulse == 8)
			{
				self.b_menu = MENU_WAYPOINTS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 9)
			{
				self.b_menu = MENU_FLAGS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 10)
			{
				self.b_menu = MENU_MAIN;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == MENU_FLAGS)
		{

			if (self.current_way)
			{
				if (self.impulse == 1)
				{
					if (self.current_way.b_aiflags & AI_DOORFLAG)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_DOORFLAG);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_DOORFLAG;
	
					self.b_menu_time = time;
				}
				else if (self.impulse == 2)
				{
					if (self.current_way.b_aiflags & AI_PRECISION)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_PRECISION);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_PRECISION;
					self.b_menu_time = time;
				}
				else if (self.impulse == 3)
				{
					if (self.current_way.b_aiflags & AI_SURFACE)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_SURFACE);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_SURFACE;
					self.b_menu_time = time;
				}
				else if (self.impulse == 4)
				{
					if (self.current_way.b_aiflags & AI_BLIND)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_BLIND);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_BLIND;
					self.b_menu_time = time;
				}
				else if (self.impulse == 5)
				{
					if (self.current_way.b_aiflags & AI_JUMP)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_JUMP);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_JUMP;
					self.b_menu_time = time;
				}
				else if (self.impulse == 6)
				{
					if (self.current_way.b_aiflags & AI_DIRECTIONAL)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_DIRECTIONAL);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_DIRECTIONAL;
					self.b_menu_time = time;
				}
				else if (self.impulse == 7)
				{
					if (self.current_way.b_aiflags & AI_SUPER_JUMP)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_SUPER_JUMP);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_SUPER_JUMP;
					self.b_menu_time = time;
				}
			}
			if (self.impulse == 9)
			{
				self.b_menu = MENU_FLAGS2;
				self.b_menu_time = time;
			}
			else if (self.impulse == 10)
			{
				self.b_menu = MENU_MAIN;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == MENU_FLAGS2)
		{

			if (self.current_way)
			{
				if (self.impulse == 1)
				{
					if (self.current_way.b_aiflags & AI_DIFFICULT)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_DIFFICULT);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_DIFFICULT;								self.b_menu_time = time;	
				}
				else if (self.impulse == 2)
				{
					if (self.current_way.b_aiflags & AI_PLAT_BOTTOM)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_PLAT_BOTTOM);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_PLAT_BOTTOM;
					self.b_menu_time = time;
				}
				else if (self.impulse == 3)
				{
					if (self.current_way.b_aiflags & AI_RIDE_TRAIN)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_RIDE_TRAIN);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_RIDE_TRAIN;
					self.b_menu_time = time;
				}
				else if (self.impulse == 4)
				{
					if (self.current_way.b_aiflags & AI_DOOR_NO_OPEN)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_DOOR_NO_OPEN);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_DOOR_NO_OPEN;
					self.b_menu_time = time;
				}
				else if (self.impulse == 5)
				{
					if (self.current_way.b_aiflags & AI_AMBUSH)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_AMBUSH);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_AMBUSH;
					self.b_menu_time = time;
				}
				else if (self.impulse == 6)
				{
					if (self.current_way.b_aiflags & AI_SNIPER)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_SNIPER);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_SNIPER;
					self.b_menu_time = time;
				}
				else if (self.impulse == 7)
				{
					if (self.current_way.b_aiflags & AI_TRACE_TEST)
						self.current_way.b_aiflags = self.current_way.b_aiflags - (self.current_way.b_aiflags & AI_TRACE_TEST);
					else
						self.current_way.b_aiflags = self.current_way.b_aiflags | AI_TRACE_TEST;
					self.b_menu_time = time;
				}

			}
			if (self.impulse == 9)
			{
				self.b_menu = MENU_FLAGS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 10)
			{
				self.b_menu = MENU_MAIN;
				self.b_menu_time = time;
			}
		}

		else if (self.b_menu == MENU_BOTS)
		{
			if (self.impulse == 1)
			{
				self.impulse = 100;
				return;
			}
			else if (self.impulse == 2)
			{
				b_temp3 = self;
				self = player_head;
				while(self)
				{
					if (!self.ishuman)
					{
						target_add(b_temp3);
						bot_get_path(b_temp3, TRUE);
						self = world;
					}
					else
						self = self._next;
				}
				self = b_temp3;
			}
			else if (self.impulse == 3)
			{
				self.impulse = 102;
				return;
			}
			else if (self.impulse == 4)
			{
				b_temp1 = self;
				self = player_head;
				while(self)
				{
					if (!self.ishuman)
					{
						self.target1 = self.target2 = self.target3 = self.target4 = world;
						route_table = world;
					}
					self = self._next;
				}
				self = b_temp1;
			}
			else if (self.impulse == 5)
			{
				if (self.current_way)
				{
					b_temp1 = self;
					self = player_head;
					while(self)
					{
						if (!self.ishuman)
						{
							setorigin(self, b_temp1.current_way.origin);
						}
						self = self._next;
					}
					self = b_temp1;
				}
				else
					sprint(self, "select a waypoint first\n");
			}
			else if (self.impulse == 6)
			{
				self.b_menu = 14;
				self.b_menu_time = time;
			}
			else if (self.impulse == 10)
			{
				self.b_menu = MENU_MAIN;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == MENU_WAYLIST)
		{
			if (self.impulse == 1)
			{
				self.b_menu = 13;
				self.b_menu_time = time;
			}
			else if (self.impulse == 2)
			{
				if (dump_mode == 0)
					DumpWaypoints();
				else if (dump_mode == 1)
					QCDumpWaypoints();
				else if (dump_mode == 2)
					BSPDumpWaypoints();
			}
			else if (self.impulse == 3)
			{
				t = way_head;
				while(t)
				{
					if ((t.target1 == world) && (t.target2 == world) && (t.target3 == world) && (t.target4 == world))
					{
						sprint(self, "Waypoint #");
						h = ftos(t.count);
						sprint(self, h);
						sprint(self, " has no outbound links\n");
					}
					if ((t.target1 == t) || (t.target2 == t) || (t.target3 == t) || (t.target4 == t))
					{
						sprint(self, "Waypoint #");
						h = ftos(t.count);
						sprint(self, h);
						sprint(self, " links to itself (??)\n");
					}
					t = t._next;
				}
				sprint(self, "Error check complete\n");
			}
			else if (self.impulse == 4)
			{
				sprint(self, "not in this version (FBX 0.10.0)\n");
			}
			else if (self.impulse == 5)
			{
				if (waypoint_mode == WM_EDITOR_DYNAMIC)
					waypoint_mode = WM_EDITOR;
				else
					waypoint_mode = WM_EDITOR_DYNAMIC;
				self.b_menu_time = time;

			}
			else if (self.impulse == 6)
			{
				if (waypoint_mode == WM_EDITOR_DYNLINK)
					waypoint_mode = WM_EDITOR;
				else
					waypoint_mode = WM_EDITOR_DYNLINK;
				self.b_menu_time = time;
			}
			else if (self.impulse == 7)
			{
				dump_mode = 0;
				self.b_menu_time = time;
			}
			else if (self.impulse == 8)
			{
				dump_mode = 1;
				self.b_menu_time = time;
			}
			else if (self.impulse == 9)
			{
				dump_mode = 2;
				self.b_menu_time = time;
			}
			else if (self.impulse == 10)
			{
				self.b_menu = MENU_MAIN;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == 8)
		{
			if (self.impulse == 1)
			{
				if (self.current_way)
				{
					if (!LinkWays(self.last_way, self.current_way))
						sprint(self, "Unable to link them\n");
					self.b_menu = MENU_LINKS;
					self.b_menu_time = time;
				}
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_LINKS;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == 9)
		{
			if (self.impulse == 1)
			{
				if (self.current_way)
				{
					if (!TeleLinkWays(self.last_way, self.current_way))
						sprint(self, "Unable to link them\n");
					self.b_menu = MENU_LINKS;
					self.b_menu_time = time;
				}
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_LINKS;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == 10)
		{
			if (self.impulse == 1)
			{
				if (self.current_way)
				{
					UnlinkWays(self.last_way, self.current_way);
					self.b_menu = MENU_LINKS;
					self.b_menu_time = time;
				}
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_LINKS;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == 11)
		{
			if (self.impulse == 1)
			{
				if (self.current_way)
				{
					if (!LinkWays(self.last_way, self.current_way))
						sprint(self, "Unable to link 1 to 2\n");
					if (!LinkWays(self.current_way, self.last_way))
						sprint(self, "Unable to link 2 to 1\n");
					self.b_menu = MENU_LINKS;
					self.b_menu_time = time;
				}
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_LINKS;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == 12)
		{
			if (self.impulse == 1)
			{
				if (self.current_way)
				{
					UnlinkWays(self.last_way, self.current_way);
					UnlinkWays(self.current_way, self.last_way);
					self.b_menu = MENU_LINKS;
					self.b_menu_time = time;
				}
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_LINKS;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == 13)
		{
			if (self.impulse == 1)
			{
				ClearAllWays();
				self.b_menu = MENU_WAYLIST;
				self.b_menu_time = time;
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_WAYLIST;
				self.b_menu_time = time;
			}
		}
		else if (self.b_menu == 14)
		{
			if (self.impulse == 10)
				self.impulse = 0;
			self.b_menu_value = self.b_menu_value * 10 + self.impulse;
			self.b_menu_time = 0;
		}
		else if (self.b_menu == 15)
		{
			if (self.impulse == 1)
			{
				delete_waypoint(self.last_way);
				self.b_menu = MENU_WAYPOINTS;
				self.b_menu_time = time;
			}
			else if (self.impulse == 2)
			{
				self.b_menu = MENU_WAYPOINTS;
				self.b_menu_time = time;
			}
		}
		self.impulse = 0;
		
	}
	if (self.b_menu_time < time)
	{
		if (self.b_menu == MENU_MAIN)
		{
			s1 = "-- Main Menu --\n[1] >>Waypoint Management\n[2] >>Link Management    \n[3] >>AI Flag Management \n[4] >>Bot Management     \n[5] >>Waylist Management \n";
			if (self.movetype == MOVETYPE_NOCLIP)
				s2 = "[6] [#] Noclip           \n";
			else
				s2 = "[6] [ ] Noclip           \n";
			
			if (self.flags & FL_GODMODE)
				s3 = "[7] [#] Godmode          \n";
			else
				s3 = "[7] [ ] Godmode          \n";
			if (self.b_aiflags & AI_HOLD_SELECT)
				s4 = "[8] [#] Hold Select      \n";
			else
				s4 = "[8] [ ] Hold Select      \n";
			s5 = "[9] Teleport to Way #    \n[0] Close Menu           \n";
		}
		else if (self.b_menu == MENU_WAYPOINTS)
		{
			s1 = "-- Waypoint Management --\n[1] Move Waypoint        \n[2] Delete Waypoint      \n[3] Make Waypoint        \n[4] Make Way + Link      \n[5] Make Way + Link X2   \n[6] Make Way + Telelink  \n[7] Show waypoint info   \n[8] >>Link Management    \n[9] >>AI Flag Management \n[0] >>Main Menu          \n";
		}
		else if (self.b_menu == MENU_LINKS)
		{
			s1 = "-- Link Management --\n[1] Unlink Waypoint      \n[2] Create Link          \n[3] Create Telelink      \n[4] Delete Link          \n[5] Create Link X2       \n[6] Delete Link X2       \n[7] >Make Waypoint       \n[8] >>Waypoint Management\n[9] >>AI Flag Management \n[0] >>Main Menu          \n";
		}
		else if (self.b_menu == MENU_FLAGS)
		{
			if (self.current_way.b_aiflags & AI_DOORFLAG)
				s1 = "-- AI Flag Management --\n[1] [#] Door Flag        \n";
			else
				s1 = "-- AI Flag Management --\n[1] [ ] Door Flag        \n";

			if (self.current_way.b_aiflags & AI_PRECISION)
				s2 = "[2] [#] Precision        \n";
			else
				s2 = "[2] [ ] Precision        \n";

			if (self.current_way.b_aiflags & AI_SURFACE)
				s3 = "[3] [#] Surface for air  \n";
			else
				s3 = "[3] [ ] Surface for air  \n";

			if (self.current_way.b_aiflags & AI_BLIND)
				s4 = "[4] [#] Blind mode       \n";
			else
				s4 = "[4] [ ] Blind mode       \n";

			if (self.current_way.b_aiflags & AI_JUMP)
				s5 = "[5] [#] Jump             \n";
			else
				s5 = "[5] [ ] Jump             \n";

			if (self.current_way.b_aiflags & AI_DIRECTIONAL)
				s6 = "[6] [#] Directional      \n";
			else
				s6 = "[6] [ ] Directional      \n";

			if (self.current_way.b_aiflags & AI_SUPER_JUMP)
				s7 = "[7] [#] Super Jump       \n\n[9] >>AI Flags page 2    \n[0] >>Main Menu          \n";
			else
				s7 = "[7] [ ] Super Jump       \n\n[9] >>AI Flags page 2    \n[0] >>Main Menu          \n";
		}
		else if (self.b_menu == MENU_FLAGS2)
		{
			if (self.current_way.b_aiflags & AI_DIFFICULT)
				s1 = "-- AI Flags pg. 2--\n[1] [#] Difficult        \n";
			else
				s1 = "-- AI Flags pg. 2--\n[1] [ ] Difficult        \n";

			if (self.current_way.b_aiflags & AI_PLAT_BOTTOM)
				s2 = "[2] [#] Wait for plat    \n";
			else
				s2 = "[2] [ ] Wait for plat    \n";

			if (self.current_way.b_aiflags & AI_RIDE_TRAIN)
				s3 = "[3] [#] Ride train       \n";
			else
				s3 = "[3] [ ] Ride train       \n";

			if (self.current_way.b_aiflags & AI_DOOR_NO_OPEN)
				s4 = "[4] [#] Door flag no open\n";
			else
				s4 = "[4] [ ] Door flag no open\n";

			if (self.current_way.b_aiflags & AI_AMBUSH)
				s5 = "[5] [#] Ambush           \n";
			else
				s5 = "[5] [ ] Ambush           \n";

			if (self.current_way.b_aiflags & AI_SNIPER)
				s6 = "[6] [#] Snipe            \n";
			else
				s6 = "[6] [ ] Snipe            \n";

			if (self.current_way.b_aiflags & AI_TRACE_TEST)
				s7 = "[7] [#] Trace Test       \n\n[9] >>AI Flag Management \n[0] >>Main Menu          \n";
			else
				s7 = "[7] [ ] Trace Test       \n\n[9] >>AI Flag Management \n[0] >>Main Menu          \n";

		}
		else if (self.b_menu == MENU_BOTS)
		{
			s1 = "-- Bot Management --\n[1] Add a Test Bot       \n[2] Order Test Bot here  \n[3] Remove Test Bot      \n[4] Stop Test Bot        \n[5] Teleport Bot here    \n[6] Teleport to Way #    \n\n\n\n[0] >>Main Menu          \n";
		}
		else if (self.b_menu == MENU_WAYLIST)
		{
			s1 = "-- Waylist Management --\n[1] Delete ALL Waypoints \n[2] Dump Waypoints       \n[3] Check For Errors     \n[4] Save Waypoints       \n";
			
			if (waypoint_mode == WM_EDITOR_DYNAMIC)
				s2 = "[5] [#] Dynamic Mode     \n[6] [#] Dynamic Link     \n";
			else if (waypoint_mode == WM_EDITOR_DYNLINK)
				s2 = "[5] [ ] Dynamic Mode     \n[6] [#] Dynamic Link     \n";
			else
				s2 = "[5] [ ] Dynamic Mode     \n[6] [ ] Dynamic Link     \n";
			if (dump_mode == 0)
				s3 = "[7] [#] WAY output       \n[8] [ ] QC output        \n[9] [ ] BSP ents output  \n[0] Main Menu            \n";
			else if (dump_mode == 1)
				s3 = "[7] [ ] WAY output       \n[8] [#] QC output        \n[9] [ ] BSP ents output  \n[0] Main Menu            \n";
			else if (dump_mode == 2)
				s3 = "[7] [ ] WAY output       \n[8] [ ] QC output        \n[9] [#] BSP ents output  \n[0] Main Menu            \n";

		}
		else if (self.b_menu == 8)
			s1 = "-- Link Ways --\n\nSelect another way and push 1\nor press 2 to cancel";
		else if (self.b_menu == 9)
			s1 = "-- Telelink Ways --\n\nSelect another way and push 1\nor press 2 to cancel";
		else if (self.b_menu == 10)
			s1 = "-- Delete Link --\n\nSelect another way and push 1\nor press 2 to cancel";
		else if (self.b_menu == 11)
			s1 = "-- Create Link X2 --\n\nSelect another way and push 1\nor press 2 to cancel";
		else if (self.b_menu == 12)
			s1 = "-- Delete Link X2 --\n\nSelect another way and push 1\nor press 2 to cancel";
		else if (self.b_menu == 13)
			s1 = "-- Delete ALL Ways --\n\nAre you sure? Push 1 to go\nthrough with it, 2 to cancel";
		else if (self.b_menu == 14)
		{
			s1 = "-- Teleport to Way # --\n\nEnter way number and press\nimpulse 104 to warp\n\nWaypoint #";
			s2 = ftos(self.b_menu_value);

		}
		else if (self.b_menu == 15)
			s1 = "-- Delete Waypoint --\n\nAre you sure? Push 1 to go\nthrough with it, 2 to cancel";
		frik_big_centerprint(self, s1, s2, s3, s4, s5, s6, s7);
		self.b_menu_time = time + 1.25;
	}
};


// engage menu
void() bot_way_edit =
{
	local entity t;
	local float f;
	if (self.b_menu_value)
	{
		if (self.b_menu == 14)
		{
			t = WaypointForNum(self.b_menu_value);
			if (t)
				setorigin(self, t.origin - self.view_ofs);
			else
				sprint(self, "No waypoint with that number\n");

			self.b_menu = MENU_MAIN;
			self.b_menu_time = time;
		}
		self.b_menu_value = 0;
		return;
	}
	if (waypoint_mode < WM_EDITOR)
	{
		self.b_menu = MENU_MAIN;
		waypoint_mode = WM_EDITOR;
		self.b_menu_time = 0;
		cvar_set("saved2", "0");
		WriteByte(MSG_ALL, 8);
		WriteByte(MSG_ALL, 1);
		WriteString(MSG_ALL, "MAKE SURE THE FOLLOWING LINE CONTAINS -CONDEBUG BEFORE PROCEEDING\n");
		localcmd("cmdline\n");
		t = way_head;
		while (t)
		{
			setmodel(t, "progs/s_bubble.spr"); // show the waypoints
			t = t._next;
		}
		if (self.current_way)
			setmodel(self.current_way, "progs/s_light.spr");
	}
	else
	{
		saved2 = cvar("saved2");
		if (saved2 != 0)
		{
			f = self.b_menu;
			self.b_menu = floor(saved2/16);
			self.impulse = saved2 & 15;
			bot_menu_display();
			self.b_menu = f;
			cvar_set("saved2", "0");
			return;
		}
		self.b_menu = 0;
		waypoint_mode = WM_LOADED;
		t = way_head;
		while (t)
		{
			setmodel(t, string_null); // hide the waypoints
			t = t._next;
		}
	}
};


/*
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Waypoint Saving to file. 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
*/


// bytecount is really iffy
// since there is no true way to determine the length of an ftos
// it uses an approximate of 5
// various other things are guesses, but I don't cut it at the absolute
// max so it should be okay

void() PrintWaypoint =
{
	local entity t;
	local float needcolon;
	local string h;
	
	if (self.enemy == world)
		t = way_head;
	else
		t = self.enemy._next;
	if (bytecounter >= 8000)
	{
		bprint("exec maps/");
		bprint(mapname);
		bprint(".wa");
		h = ftos(filecount);
		bprint(h);
		filecount = filecount + 1;
		bprint("\n// **** break here **** \n");
		bytecounter = 26;
	}
	if (t == world)
	{
		remove(self);
		fixer = world;
		bprint("saved4 3\n// end waypoint dump\n");
		bytecounter = bytecounter + 27;
		return;
	}
	if ((t.origin_x != saved1) || (t.count == 1))
	{
		bprint("saved1 ");
		h = ftos(t.origin_x);
		bprint(h);
		saved1 = t.origin_x;
		bytecounter = bytecounter + 12;
		needcolon = TRUE;
	}
	if ((t.origin_y != saved2) || (t.count == 1))
	{
		if (needcolon)
		{
			bprint("; ");
			bytecounter = bytecounter + 2;
		}
		else
			needcolon = TRUE;
		bprint("saved2 ");
		h = ftos(t.origin_y);
		bprint(h);
		bytecounter = bytecounter + 12;
		saved2 = t.origin_y;
	}
	if ((t.origin_z != saved3) || (t.count == 1))
	{
		if (needcolon)
		{
			bprint("; ");
			bytecounter = bytecounter + 2;
		}
		else
			needcolon = TRUE;
		bprint("saved3 ");
		h = ftos(t.origin_z);
		bprint(h);
		bytecounter = bytecounter + 12;
		saved3 = t.origin_z;
	}
	bytecounter = bytecounter + 1;
	bprint("\n");
	needcolon = FALSE;
	if ((scratch1 != t.target1.count) || t.count == 1)
	{
		needcolon = TRUE;
		bprint("scratch1 ");
		bytecounter = bytecounter + 14;
		h = ftos(t.target1.count);
		bprint(h);
		scratch1 = t.target1.count;
	}
	if ((scratch2 != t.target2.count) || t.count == 1)
	{
		if (needcolon)
		{
			bprint("; ");
			bytecounter = bytecounter + 2;
		}
		else
			needcolon = TRUE;
		bprint("scratch2 ");
		bytecounter = bytecounter + 14;
		h = ftos(t.target2.count);
		bprint(h);
		scratch2 = t.target2.count;
	}
	if ((scratch3 != t.target3.count) || t.count == 1)
	{
		if (needcolon)
		{
			bprint("; ");
			bytecounter = bytecounter + 2;
		}
		else
			needcolon = TRUE;
		bprint("scratch3 ");
		bytecounter = bytecounter + 14;
		h = ftos(t.target3.count);
		bprint(h);
		scratch3 = t.target3.count;
	}
	if ((scratch4 != t.target4.count) || t.count == 1)
	{
		if (needcolon)
		{
			bprint("; ");
			bytecounter = bytecounter + 2;
		}
		else
			needcolon = TRUE;
		bprint("scratch4 ");
		bytecounter = bytecounter + 14;
		h = ftos(t.target4.count);
		bprint(h);
		scratch4 = t.target4.count;
	}
	bprint("\nsaved4 ");
	bytecounter = bytecounter + 19;
	if (t.count != 1)
		h = ftos(t.b_aiflags * 4 + 2);
	else 
		h = ftos(t.b_aiflags * 4 + 1);
	bprint(h);
	bprint ("; wait\n");
	self.nextthink = time + 0.01;
	self.enemy = t;
};

// to allow for 100+ waypoints, we need to trick the runaway loop counter
void() DumpWaypoints =
{
	bytecounter = 50; 
	filecount = 1;

	bprint("// ");
	bprint(world.message);
	bprint("- maps/");
	bprint(mapname);
	bprint(".way\n");
	bprint("// Ways by ");
	bprint(self.netname);
	bprint("\n");
	if (!fixer)
	{
		fixer = spawn();
		fixer.nextthink = time + 0.01;
		fixer.think = PrintWaypoint;
		fixer.enemy = world;
	}
};

void() PrintQCWaypoint =
{
	local entity t;
	local string h;
	
	if (self.enemy == world)
		t = way_head;
	else
		t = self.enemy._next;

	if (t == world)
	{
		remove(self);
		fixer = world;
		bprint("};\n\n// End dump\n");
		return;
	}
	bprint("	make_way(");
	h = vtos(t.origin);
	bprint(h);
	bprint(", '");
	h = ftos(t.target1.count);
	bprint(h);
	bprint(" ");
	h = ftos(t.target2.count);
	bprint(h);
	bprint(" ");
	h = ftos(t.target3.count);
	bprint(h);
	bprint("', ");
	h = ftos(t.target4.count);
	bprint(h);
	bprint(", ");
	h = ftos(t.b_aiflags);
	bprint(h);
	bprint(");\n");
	self.nextthink = time + 0.01;
	self.enemy = t;

};
void() QCDumpWaypoints =
{
	bprint("/* QC Waypoint Dump - src/frikbot/map_");

	bprint(mapname);
	bprint(".qc\nFor instructions please read the\nreadme.html that comes with FrikBot */\n\nvoid(vector org, vector bit1, float bit4, float flargs) make_way;\n");
	bprint("// Ways by ");
	bprint(self.netname);
	bprint("\n\n");

	bprint("void() map_");
	bprint(mapname);
	bprint(" =\n{\n");


	if (!fixer)
	{
		fixer = spawn();
		fixer.nextthink = time + 0.01;
		fixer.think = PrintQCWaypoint;
		fixer.enemy = world;
	}
};

void() PrintBSPWaypoint =
{
	local entity t;
	local string h;

	if (self.enemy == world)
		t = way_head;
	else
		t = self.enemy._next;

	if (t == world)
	{
		bprint("\n\n// End dump\n");
		remove(self);
		fixer = world;
		return;
	}
	bprint("{\n\"classname\" \"waypoint\"\n\"origin\" \"");
	h = ftos(t.origin_x);
	bprint(h);
	bprint(" ");
	h = ftos(t.origin_y);
	bprint(h);
	bprint(" ");
	h = ftos(t.origin_z);
	bprint(h);
	if (t.target1.count)
	{
		bprint("\"\n\"b_pants\" \"");
		h = ftos(t.target1.count);
		bprint(h);
	}
	if (t.target2.count)
	{
		bprint("\"\n\"b_skill\" \"");
		h = ftos(t.target2.count);
		bprint(h);
	}
	if (t.target3.count)
	{
		bprint("\"\n\"b_shirt\" \"");
		h = ftos(t.target3.count);
		bprint(h);
	}
	if (t.target4.count)
	{
		bprint("\"\n\"b_frags\" \"");
		h = ftos(t.target4.count);
		bprint(h);
	}
	if (t.b_aiflags)
	{
		bprint("\"\n\"b_aiflags\" \"");
		h = ftos(t.b_aiflags);
		bprint(h);
	}
	bprint("\"\n}\n");
	self.nextthink = time + 0.01;
	self.enemy = t;

};
void() BSPDumpWaypoints =
{
	bprint("/* BSP entities Dump - maps/");

	bprint(mapname);
	bprint(".ent\nFor instructions please read the\nreadme.html that comes with FrikBot */\n\n\n");

	if (!fixer)
	{
		fixer = spawn();
		fixer.nextthink = time + 0.01;
		fixer.think = PrintBSPWaypoint;
		fixer.enemy = world;
	}
};
