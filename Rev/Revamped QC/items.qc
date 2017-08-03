/* ALL LIGHTS SHOULD BE 0 1 0 IN COLOR ALL OTHER ITEMS SHOULD
BE .8 .3 .4 IN COLOR */
void () W_SetCurrentAmmo;
void (float weap) W_WeaponSwitch;
void (entity ent) W_UpdateAmmoCounts;

void() SUB_regen =
{
	self.model = self.mdl;          // restore original model
	self.solid = SOLID_TRIGGER;     // allow it to be touched again
	sound (self, CHAN_VOICE, "items/itembk2.wav", 1, ATTN_NORM);    // play respawn sound
	setorigin (self, self.origin);
};



/*QUAKED noclass (0 0 0) (-8 -8 -8) (8 8 8)
prints a warning message when spawned
*/
void() noclass =
{
	dprint ("noclass spawned at");
	dprint (vtos(self.origin));
	dprint ("\n");
	remove (self);
};

// names of weapons function
string(float weap) I_WeaponName =
{
	switch (weap)
	{
	case IT_AXE:
		return "Axe";
	case IT_SHOTGUN:
		return "Shotgun";
	case IT_SUPER_SHOTGUN:
		return "Double-barrelled Shotgun";
	case IT_NAILGUN:
		return "Nailgun";
	case IT_SUPER_NAILGUN:
		return "Super Nailgun";
	case IT_GRENADE_LAUNCHER:
		return "Grenade Launcher";
	case IT_ROCKET_LAUNCHER:
		return "Rocket Launcher";
	case IT_LIGHTNING:
		return "Thunderbolt";
	}

	return "";
}



void() q_touch;

void() q_touch =
{
	local string s, t;

	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

	self.mdl = self.model;

	sound (other, CHAN_VOICE, self.noise, 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	self.solid = SOLID_NOT;
	other.items = other.items | IT_QUAD;
	self.model = string_null;
		if (deathmatch == 4)
		{
			other.armortype = 0;
			other.armorvalue = 0;
			other.ammo_cells_real = 0;
			W_UpdateAmmoCounts(other);
		}

// do the apropriate action
	other.super_time = 1;
	other.super_damage_finished = self.cnt;

	s=ftos(rint(other.super_damage_finished - time));
	t = " recovered a Quad with ";
	if (deathmatch == 4)
		t = " recovered an OctaPower with ";

	bprint4 (PRINT_LOW, other.netname, t, s, " seconds remaining!\n");

	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};


void(float timeleft) DropQuad =
{
	local entity    item;

	item = spawn();
	item.origin = self.origin;
	
	item.velocity_z = 300;
	item.velocity_x = -100 + (random() * 200);
	item.velocity_y = -100 + (random() * 200);
	
	item.flags = FL_ITEM;
	item.solid = SOLID_TRIGGER;
	item.movetype = MOVETYPE_TOSS;
	item.noise = "items/damage.wav";
	setmodel (item, "progs/quaddama.mdl");
	setsize (item, '-16 -16 -24', '16 16 32');
	item.cnt = time + timeleft;
	item.touch = q_touch;
	item.nextthink = time + timeleft;    // remove it with the time left on it
	item.think = SUB_Remove;
};


void() r_touch;

void() r_touch =
{
local string    s;

	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

	self.mdl = self.model;

	sound (other, CHAN_VOICE, self.noise, 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	self.solid = SOLID_NOT;
	other.items = other.items | IT_INVISIBILITY;
	self.model = string_null;

// do the apropriate action
	other.invisible_time = 1;
	other.invisible_finished = self.cnt;
	s=ftos(rint(other.invisible_finished - time));
	bprint4 (PRINT_LOW, other.netname, " recovered a Ring with ", s, " seconds remaining!\n");
      

	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};


void(float timeleft) DropRing =
{
	local entity    item;

	item = spawn();
	item.origin = self.origin;
	
	item.velocity_z = 300;
	item.velocity_x = -100 + (random() * 200);
	item.velocity_y = -100 + (random() * 200);
	
	item.flags = FL_ITEM;
	item.solid = SOLID_TRIGGER;
	item.movetype = MOVETYPE_TOSS;
	item.noise = "items/inv1.wav";
	setmodel (item, "progs/invisibl.mdl");
	setsize (item, '-16 -16 -24', '16 16 32');
	item.cnt = time + timeleft;
	item.touch = r_touch;
	item.nextthink = time + timeleft;    // remove after 30 seconds
	item.think = SUB_Remove;
};

/*
============
PlaceItem

plants the object on the floor
============
*/
void() PlaceItem =
{
	local float     oldz;

	self.mdl = self.model;          // so it can be restored on respawn
	self.flags = FL_ITEM;           // make extra wide
	self.solid = SOLID_TRIGGER;
	self.movetype = MOVETYPE_TOSS;  
	self.velocity = '0 0 0';
	self.origin_z = self.origin_z + 6;
	oldz = self.origin_z;
	if (!droptofloor())
	{
		dprint ("Bonus item fell out of level at ");
		dprint (vtos(self.origin));
		dprint ("\n");
		remove(self);
		return;
	}
};

/*
============
StartItem

Sets the clipping size and plants the object on the floor
============
*/
void() StartItem =
{
	self.nextthink = time + 0.2;    // items start after other solids
	self.think = PlaceItem;
};

/*
=========================================================================

HEALTH BOX

=========================================================================
*/
//
// T_Heal: add health to an entity, limiting health to max_health
// "ignore" will ignore max_health limit
//
float (entity e, float hamount, float ignore) T_Heal =
{
	if (e.health <= 0)
		return 0;
	if ((!ignore) && (e.health >= other.max_health))
		return 0;
	hamount = ceil(hamount);

	e.health = e.health + hamount;
	if ((!ignore) && (e.health >= other.max_health))
		e.health = other.max_health;
	
		
	if (e.health > e.max_health + 150)
		e.health = e.max_health + 150;

	e.healdecay = time + 5;
	return 1;
};

/*QUAKED item_health (.3 .3 1) (0 0 0) (32 32 32) rotten megahealth
Health box. Normally gives 25 points.
Rotten box heals 5-10 points,
megahealth will add 100 health, then 
rot you down to your maximum health limit, 
one point per second.
*/

void() health_touch;

void() item_health =
{       
	self.touch = health_touch;

	if (self.spawnflags & H_ROTTEN)
	{
		precache_model("progs/health.mdl");

		precache_sound("items/r_item1.wav");
		setmodel(self, "progs/health.mdl");
		self.noise = "items/r_item1.wav";
		self.healamount = 15;
		self.healtype = 0;
	}
	else
	if (self.spawnflags & H_MEGA)
	{
		precache_model("progs/health.mdl");
		precache_sound("items/r_item2.wav");
		setmodel(self, "progs/health.mdl");
		self.noise = "items/r_item2.wav";
		self.healamount = 100;
		self.healtype = 2;
	}
	else
	{
		precache_model("progs/health.mdl");
		precache_sound("items/health1.wav");
		setmodel(self, "progs/health.mdl");
		self.noise = "items/health1.wav";
		self.healamount = 25;
		self.healtype = 1;
	}
	setsize (self, '0 0 0', '32 32 56');
	StartItem ();
};


void() health_touch =
{
	local   string  s;
	
	if (deathmatch == 4)
		if (other.invincible_time > time)
			return;

	if (other.classname != "player")
		return;
	
	if (self.healtype == H_MEGA) // Megahealth?  Ignore max_health...
	{
		if (other.health >= other.max_health + 150)
			return;
		if (!T_Heal(other, self.healamount, 1))
			return;
	}
	else
	{
		if (!T_Heal(other, self.healamount, 0))
			return;
	}
	
	s = ftos(self.healamount);
	sprint3(other, PRINT_LOW, "You receive ", s, " health\n");
	
// health touch sound
	sound(other, CHAN_ITEM, self.noise, 1, ATTN_NORM);

	stuffcmd (other, "bf\n");
	
	self.model = string_null;
	self.solid = SOLID_NOT;

	// Megahealth = rot down the player's super health
	if (deathmatch) // TODO: are these rules right?
	{
		if (deathmatch != 2)            // deathmatch 2 is the silly old rules
		{
			if (self.healtype == H_MEGA)
				self.nextthink = time + 45; // should I account for health healed instead?
			else
				self.nextthink = time + 20;
			self.think = SUB_regen;
		}
	}
	
	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};      

/*
===============================================================================

ARMOR

===============================================================================
*/

void() armor_touch;

void() armor_touch =
{
	local   float   type, value, bit;
	
	if (other.health <= 0)
		return;
	if (other.classname != "player")
		return;

	if (deathmatch == 4)

		if (other.invincible_time > 0)
			return;

	switch (self.classname)
	{
	case "item_armor1":
		type = 0.3;
		value = 100;
		bit = IT_ARMOR1;
		break;
	case "item_armor2":
		type = 0.6;
		value = 150;
		bit = IT_ARMOR2;
		break;
	case "item_armorInv":
		type = 0.8;
		value = 200;
		bit = IT_ARMOR3;
		break;
	}

	if (other.armortype*other.armorvalue >= type*value)
		return;
		
	other.armortype = type;
	other.armorvalue = value;
	other.items = other.items - (other.items & (IT_ARMOR1 | IT_ARMOR2 | IT_ARMOR3)) + bit;

	self.solid = SOLID_NOT;
	self.model = string_null;
	if (deathmatch && deathmatch != 2)
	{
		self.nextthink = time + 20;
		self.think = SUB_regen;
	}

	sprint1(other, PRINT_LOW, "You got armor\n");
// armor touch sound
	sound(other, CHAN_ITEM, "items/armor1.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	
	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};


/*QUAKED item_armor1 (0 .5 .8) (-16 -16 0) (16 16 32)
*/

void() item_armor1 =
{
	self.touch = armor_touch;
	precache_model ("progs/armor.mdl");
	setmodel (self, "progs/armor.mdl");
	self.skin = 0;
	setsize (self, '-16 -16 0', '16 16 56');
	StartItem ();
};

/*QUAKED item_armor2 (0 .5 .8) (-16 -16 0) (16 16 32)
*/

void() item_armor2 =
{
	self.touch = armor_touch;
	precache_model ("progs/armor.mdl");
	setmodel (self, "progs/armor.mdl");
	self.skin = 1;
	setsize (self, '-16 -16 0', '16 16 56');
	StartItem ();
};

/*QUAKED item_armorInv (0 .5 .8) (-16 -16 0) (16 16 32)
*/

void() item_armorInv =
{
	self.touch = armor_touch;
	precache_model ("progs/armor.mdl");
	setmodel (self, "progs/armor.mdl");
	self.skin = 2;
	setsize (self, '-16 -16 0', '16 16 56');
	StartItem ();
};

/*
===============================================================================

WEAPONS

===============================================================================
*/

void() bound_other_ammo =
{
	if (other.ammo_shells_real > 100)
		other.ammo_shells_real = 100;
	if (other.ammo_nails_real > 200)
		other.ammo_nails_real = 200;
	if (other.ammo_rockets_real > 100)
		other.ammo_rockets_real = 100;               
	if (other.ammo_cells_real > 100)
		other.ammo_cells_real = 100;         

	if ((other.exshells > 100))
	{
		other.exshells = 100;
	}
	if ((other.exnails > 200))
	{
		other.exnails = 200;
	}
	if ((other.exrockets > 100))
	{
		other.exrockets = 100;
	}
	if ((other.excells > 100))
	{
		other.excells = 100;
	}
};


float(float w) RankForWeapon =
{
	if (w == IT_LIGHTNING)	
		return 1;
	if (w == IT_ROCKET_LAUNCHER)
		return 2;
	if (w == IT_SUPER_NAILGUN)
		return 3;
	if (w == IT_GRENADE_LAUNCHER)
		return 4;
	if (w == IT_SUPER_SHOTGUN)
		return 5;
	if (w == IT_NAILGUN)
		return 6;
	return 7;
};

float (float w) WeaponCode =
{
	if (w == IT_SUPER_SHOTGUN)
		return 3;
	if (w == IT_NAILGUN)
		return 4;
	if (w == IT_SUPER_NAILGUN)
		return 5;
	if (w == IT_GRENADE_LAUNCHER)
		return 6;
	if (w == IT_ROCKET_LAUNCHER)
		return 7;
	if (w == IT_LIGHTNING)
		return 8;
	return 1;
};

/*
=============
Deathmatch_Weapon

Deathmatch weapon change rules for picking up a weapon

.float          ammo_shells, ammo_nails, ammo_rockets, ammo_cells;
=============
*/
void(float old, float new) Deathmatch_Weapon =
{
	local float or, nr;

// change self.weapon if desired
	or = RankForWeapon (self.weapon);
	nr = RankForWeapon (new);

	if ( nr == IT_LIGHTNING && self.waterlevel > 1 )
		return;

	if ( nr < or )
		W_WeaponSwitch (new);
};

/*
=============
weapon_touch
=============
*/
float() W_BestWeapon;
void() weapon_touch;		// sol_items.qc




/*
===============================================================================

AMMO

===============================================================================
*/

void () ammo_touch =
{
	local entity stemp;
	local float best;

	if ((other.classname != "player"))
	{
		return;
	}
	if ((other.health <= MSG_BROADCAST))
	{
		return;
	}
	stemp = self;
	self = other;
	best = W_BestWeapon ();
	self = stemp;
	if ((self.weapon == H_ROTTEN))
	{
		if ((other.exshells >= 100))
		{
			return;
		}
		other.exshells = (other.exshells + self.aflag);
	}
	if ((self.weapon == H_MEGA))
	{
		if ((other.exnails >= 200))
		{
			return;
		}
		other.exnails = (other.exnails + self.aflag);
	}
	if ((self.weapon == AS_MELEE))
	{
		if ((other.exrockets >= 100))
		{
			return;
		}
		other.exrockets = (other.exrockets + self.aflag);
	}
	if ((self.weapon == AS_MISSILE))
	{
		if ((other.excells >= 100))
		{
			return;
		}
		other.excells = (other.excells + self.aflag);
	}
	bound_other_ammo ();
	sprint (other, "You got the ");
	sprint (other, self.netname);
	sprint (other, "\n");
	sound (other, CHAN_ITEM, "weapons/lock4.wav", H_ROTTEN, ATTN_NORM);
	stuffcmd (other, "bf\n");
	stemp = self;
	self = other;
	self = stemp;
	self.model = string_null;
	self.solid = SOLID_NOT;
	if ((deathmatch == H_ROTTEN))
	{
		self.nextthink = (time + SVC_INTERMISSION);
	}
	self.think = SUB_regen;
	activator = other;
	SUB_UseTargets ();
};
/*
void() ammo_touch =
{
local entity    stemp;
local float             best;

	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

// if the player was using his best weapon, change up to the new one if better          
	stemp = self;
	self = other;
	best = W_BestWeapon();
	self = stemp;


	switch (self.weapon)
	{
	case 1: // shotgun
		if (other.ammo_shells_real >= 100)
			return;
		other.ammo_shells_real = other.ammo_shells_real + self.ammo_count;
		break;
	case 2: // spikes
		if (other.ammo_nails_real >= 200)
			return;
		other.ammo_nails_real = other.ammo_nails_real + self.ammo_count;
		break;
	case 3: // rockets
		if (other.ammo_rockets_real >= 100)
			return;
		other.ammo_rockets_real = other.ammo_rockets_real + self.ammo_count;
		break;
	case 4: // cells
		if (other.ammo_cells_real >= 100)
			return;
		other.ammo_cells_real = other.ammo_cells_real + self.ammo_count;
		break;
	}

	bound_other_ammo ();
	
	sprint3 (other, PRINT_LOW, "You got the ", self.netname, "\n");
// ammo touch sound
	sound (other, CHAN_ITEM, "weapons/lock4.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");

// change to a better weapon if appropriate

	stemp = self;
	self = other;

	if ( self.weapon == best )
		W_WeaponSwitch (W_BestWeapon ());
	else
		W_UpdateAmmoCounts (self);

	self = stemp;

// remove it in single player, or setup for respawning in deathmatch
	self.model = string_null;
	self.solid = SOLID_NOT;
	if (deathmatch)
	{
		if (deathmatch != 2)
			self.nextthink = time + 30;

		// Xian -- If playing in DM 3.0 mode, halve the time ammo respawns        
		if (deathmatch == 3 || deathmatch == 5)        
			self.nextthink = time + 15;

		self.think = SUB_regen;
	}

	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};
*/



float WEAPON_BIG2 = 1;

void () item_shells =
{
	self.touch = ammo_touch;
	if ((self.spawnflags & WEAPON_BIG2))
	{
		precache_model ("maps/b_shell1.bsp");
		setmodel (self, "maps/b_shell1.bsp");
		self.aflag = 40;
	}
	else
	{
		precache_model ("maps/b_shell0.bsp");
		setmodel (self, "maps/b_shell0.bsp");
		self.aflag = 20;
	}
	self.weapon = WEAPON_BIG2;
	self.netname = "shells";
	setsize (self, VEC_ORIGIN, '32 32 56');
	StartItem ();
};

void () item_spikes =
{
	self.touch = ammo_touch;
	if ((self.spawnflags & WEAPON_BIG2))
	{
		precache_model ("maps/b_nail1.bsp");
		setmodel (self, "maps/b_nail1.bsp");
		self.aflag = 50;
	}
	else
	{
		precache_model ("maps/b_nail0.bsp");
		setmodel (self, "maps/b_nail0.bsp");
		self.aflag = 25;
	}
	self.weapon = H_MEGA;
	self.netname = "nails";
	setsize (self, VEC_ORIGIN, '32 32 56');
	StartItem ();
};

void () item_rockets =
{
	self.touch = ammo_touch;
	if ((self.spawnflags & WEAPON_BIG2))
	{
		precache_model ("maps/b_rock1.bsp");
		setmodel (self, "maps/b_rock1.bsp");
		self.aflag = TE_LAVASPLASH;
	}
	else
	{
		precache_model ("maps/b_rock0.bsp");
		setmodel (self, "maps/b_rock0.bsp");
		self.aflag = TE_LIGHTNING1;
	}
	self.weapon = AS_MELEE;
	self.netname = "rockets";
	setsize (self, VEC_ORIGIN, '32 32 56');
	StartItem ();
};

void () item_cells =
{
	self.touch = ammo_touch;
	if ((self.spawnflags & WEAPON_BIG2))
	{
		precache_model ("maps/b_batt1.bsp");
		setmodel (self, "maps/b_batt1.bsp");
		self.aflag = 12;
	}
	else
	{
		precache_model ("maps/b_batt0.bsp");
		setmodel (self, "maps/b_batt0.bsp");
		self.aflag = TE_LIGHTNING2;
	}
	self.weapon = AS_MISSILE;
	self.netname = "cells";
	setsize (self, VEC_ORIGIN, '32 32 56');
	StartItem ();
};


/*QUAKED item_weapon (0 .5 .8) (0 0 0) (32 32 32) shotgun rocket spikes big
DO NOT USE THIS!!!! IT WILL BE REMOVED!
*/

#define WEAPON_SHOTGUN 	1
float WEAPON_ROCKET = 2;
float WEAPON_SPIKES = 4;
float WEAPON_MASK = 7;
float WEAPON_BIG = 8;
void () item_weapon =
{
	self.touch = ammo_touch;
	if ((self.spawnflags & WEAPON_SHOTGUN))
	{
		if ((self.spawnflags & WEAPON_BIG))
		{
			precache_model ("maps/b_shell1.bsp");
			setmodel (self, "maps/b_shell1.bsp");
			self.aflag = 40;
		}
		else
		{
			precache_model ("maps/b_shell0.bsp");
			setmodel (self, "maps/b_shell0.bsp");
			self.aflag = 20;
		}
		self.weapon = WEAPON_SHOTGUN;
		self.netname = "shells";
	}
	if ((self.spawnflags & WEAPON_SPIKES))
	{
		if ((self.spawnflags & WEAPON_BIG))
		{
			precache_model ("maps/b_nail1.bsp");
			setmodel (self, "maps/b_nail1.bsp");
			self.aflag = 40;
		}
		else
		{
			precache_model ("maps/b_nail0.bsp");
			setmodel (self, "maps/b_nail0.bsp");
			self.aflag = 20;
		}
		self.weapon = WEAPON_ROCKET;
		self.netname = "spikes";
	}
	if ((self.spawnflags & WEAPON_ROCKET))
	{
		if ((self.spawnflags & WEAPON_BIG))
		{
			precache_model ("maps/b_rock1.bsp");
			setmodel (self, "maps/b_rock1.bsp");
			self.aflag = TE_LAVASPLASH;
		}
		else
		{
			precache_model ("maps/b_rock0.bsp");
			setmodel (self, "maps/b_rock0.bsp");
			self.aflag = TE_LIGHTNING1;
		}
		self.weapon = AS_MELEE;
		self.netname = "rockets";
	}
	setsize (self, VEC_ORIGIN, '32 32 56');
	StartItem ();
};


/*
===============================================================================

KEYS

===============================================================================
*/

void() key_touch =
{
	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;
	if (other.items & self.items)
		return;

	sprint3 (other, PRINT_LOW, "You got the ", self.netname, "\n");

	sound (other, CHAN_ITEM, self.noise, 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	other.items = other.items | self.items;

	self.solid = SOLID_NOT;
	self.model = string_null;

	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};


void() key_setsounds =
{
	switch (world.worldtype)
	{
	case WT_MEDIEVAL:
		precache_sound ("misc/medkey.wav");
		self.noise = "misc/medkey.wav";
		break;
	case WT_METAL:
		precache_sound ("misc/runekey.wav");
		self.noise = "misc/runekey.wav";
		break;
	case WT_BASE:
		precache_sound2 ("misc/basekey.wav");
		self.noise = "misc/basekey.wav";
		break;
	}
};

/*QUAKED item_key1 (0 .5 .8) (-16 -16 -24) (16 16 32)
SILVER key
In order for keys to work
you MUST set your maps
worldtype to one of the
following:
0: medieval
1: metal
2: base
*/

void() item_key1 =
{
	if (deathmatch)
	{
		remove(self);
		return;
	}

	switch (world.worldtype)
	{
	case WT_MEDIEVAL:
		precache_model ("progs/w_s_key.mdl");
		setmodel (self, "progs/w_s_key.mdl");
		self.netname = "silver key";
		break;
	case WT_METAL:
		precache_model ("progs/m_s_key.mdl");
		setmodel (self, "progs/m_s_key.mdl");
		self.netname = "silver runekey";
		break;
	case WT_BASE:
		precache_model2 ("progs/b_s_key.mdl");
		setmodel (self, "progs/b_s_key.mdl");
		self.netname = "silver keycard";
		break;
	}

	key_setsounds();
	self.touch = key_touch;
	self.items = IT_KEY1;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};

/*QUAKED item_key2 (0 .5 .8) (-16 -16 -24) (16 16 32)
GOLD key
In order for keys to work
you MUST set your maps
worldtype to one of the
following:
0: medieval
1: metal
2: base
*/

void() item_key2 =
{
	if (deathmatch)
	{
		remove(self);
		return;
	}

	switch (world.worldtype)
	{
	case WT_MEDIEVAL:
		precache_model ("progs/w_g_key.mdl");
		setmodel (self, "progs/w_g_key.mdl");
		self.netname = "gold key";
		break;
	case WT_METAL:
		precache_model ("progs/m_g_key.mdl");
		setmodel (self, "progs/m_g_key.mdl");
		self.netname = "gold runekey";
		break;
	case WT_BASE:
		precache_model2 ("progs/b_g_key.mdl");
		setmodel (self, "progs/b_g_key.mdl");
		self.netname = "gold keycard";
		break;
	}
	key_setsounds();
	self.touch = key_touch;
	self.items = IT_KEY2;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};



/*
===============================================================================

END OF LEVEL RUNES

===============================================================================
*/

void() sigil_touch =
{
	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

	centerprint (other, "You got the rune!");

	sound (other, CHAN_ITEM, self.noise, 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	self.solid = SOLID_NOT;
	self.model = string_null;
	serverflags = serverflags | (self.spawnflags & 15);
	self.classname = "";            // so rune doors won't find it
	
	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};


/*QUAKED item_sigil (0 .5 .8) (-16 -16 -24) (16 16 32) E1 E2 E3 E4
End of level sigil, pick up to end episode and return to jrstart.
*/

void() item_sigil =
{
	if (deathmatch)
	{
		remove(self);
		return;
	}

	if (!self.spawnflags)
		objerror ("no spawnflags");

	precache_sound ("misc/runekey.wav");
	self.noise = "misc/runekey.wav";

	switch (self.spawnflags & 15)
	{
	case 1:
		precache_model ("progs/end1.mdl");
		setmodel (self, "progs/end1.mdl");
		break;
	case 2:
		precache_model2 ("progs/end2.mdl");
		setmodel (self, "progs/end2.mdl");
		break;
	case 4:
		precache_model2 ("progs/end3.mdl");
		setmodel (self, "progs/end3.mdl");
		break;
	case 8:
		precache_model2 ("progs/end4.mdl");
		setmodel (self, "progs/end4.mdl");
		break;
	}
	
	self.touch = sigil_touch;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};

/*
===============================================================================

POWERUPS

===============================================================================
*/

void() powerup_touch =
{
	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

	sprint3 (other, PRINT_LOW, "You got the ",  self.netname, "\n");

	self.mdl = self.model;

	if (deathmatch)
	{	
		if (self.items & (IT_INVULNERABILITY | IT_INVISIBILITY))
			self.nextthink = time + 60*5;
		else
			self.nextthink = time + 60;
	
		self.think = SUB_regen;
	}

	sound (other, CHAN_VOICE, self.noise, 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	self.solid = SOLID_NOT;
	other.items = other.items | self.items;
	self.model = string_null;

// do the apropriate action
	switch (self.items)
	{
	case IT_SUIT:
		other.rad_time = 1;
		other.radsuit_finished = time + 30;
		break;
	case IT_INVULNERABILITY:
		other.invincible_time = 1;
		other.invincible_finished = time + 30;
		break;
	case IT_INVISIBILITY:
		other.invisible_time = 1;
		other.invisible_finished = time + 30;
		break;
	case IT_QUAD:
		if (deathmatch == 4)
		{
			other.armortype = 0;
			other.armorvalue = 0;
			other.ammo_cells_real = 0;
			W_UpdateAmmoCounts(other);
		}
		other.super_time = 1;
		other.super_damage_finished = time + 30;
		break;
	}

	activator = other;
	SUB_UseTargets();                               // fire all targets / killtargets
};



/*QUAKED item_artifact_invulnerability (0 .5 .8) (-16 -16 -24) (16 16 32)
Player is invulnerable for 30 seconds
*/
void() item_artifact_invulnerability =
{
	self.touch = powerup_touch;

	precache_model ("progs/invulner.mdl");
	precache_sound ("items/protect.wav");
	precache_sound ("items/protect2.wav");
	precache_sound ("items/protect3.wav");
	self.noise = "items/protect.wav";
	setmodel (self, "progs/invulner.mdl");
	self.netname = "Pentagram of Protection";
	self.effects = self.effects | ef_red;
	self.items = IT_INVULNERABILITY;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};

/*QUAKED item_artifact_envirosuit (0 .5 .8) (-16 -16 -24) (16 16 32)
Player takes no damage from water or slime for 30 seconds
*/
void() item_artifact_envirosuit =
{
	self.touch = powerup_touch;

	precache_model ("progs/suit.mdl");
	precache_sound ("items/suit.wav");
	precache_sound ("items/suit2.wav");
	self.noise = "items/suit.wav";
	setmodel (self, "progs/suit.mdl");
	self.netname = "Biosuit";
	self.items = IT_SUIT;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};


/*QUAKED item_artifact_invisibility (0 .5 .8) (-16 -16 -24) (16 16 32)
Player is invisible for 30 seconds
*/
void() item_artifact_invisibility =
{
	self.touch = powerup_touch;

	precache_model ("progs/invisibl.mdl");
	precache_sound ("items/inv1.wav");
	precache_sound ("items/inv2.wav");
	precache_sound ("items/inv3.wav");
	self.noise = "items/inv1.wav";
	setmodel (self, "progs/invisibl.mdl");
	self.netname = "Ring of Shadows";
	self.items = IT_INVISIBILITY;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};


/*QUAKED item_artifact_super_damage (0 .5 .8) (-16 -16 -24) (16 16 32)
The next attack from the player will do 4x damage
*/
void() item_artifact_super_damage =
{
	self.touch = powerup_touch;

	precache_model ("progs/quaddama.mdl");
	precache_sound ("items/damage.wav");
	precache_sound ("items/damage2.wav");
	precache_sound ("items/damage3.wav");
	self.noise = "items/damage.wav";
	setmodel (self, "progs/quaddama.mdl");
	if (deathmatch == 4)
		self.netname = "OctaPower";	
	else
		self.netname = "Quad Damage";
	self.items = IT_QUAD;
	self.effects = self.effects | ef_blue;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};



/*
===============================================================================

PLAYER BACKPACKS

===============================================================================
*/

void () BackpackTouch =
{
	local string s;
	local float best;
	local float old;
	local float new;
	local entity stemp;
	local float acount;

	if ((other.classname != "player"))
	{
		return;
	}
	if ((other.health <= MSG_BROADCAST))
	{
		return;
	}
	acount = MSG_BROADCAST;
	sprint (other, "You get ");
	if (self.items)
	{
		if (((other.items & self.items) == MSG_BROADCAST))
		{
			acount = WEAPON_SHOTGUN;
			sprint (other, "the ");
			sprint (other, self.netname);
		}
	}
	stemp = self;
	self = other;
	best = W_BestWeapon ();
	self = stemp;
	other.exshells = (other.exshells + self.exshells);
	other.exnails = (other.exnails + self.exnails);
	other.exrockets = (other.exrockets + self.exrockets);
	other.excells = (other.excells + self.excells);
	new = self.items;
	if (!new)
	{
		new = other.weapon;
	}
	old = other.items;
	other.items = (other.items | new);
	bound_other_ammo ();
	if (self.exshells)
	{
		if (acount)
		{
			sprint (other, ", ");
		}
		acount = WEAPON_SHOTGUN;
		s = ftos (self.exshells);
		sprint (other, s);
		sprint (other, " shells");
	}
	if (self.exnails)
	{
		if (acount)
		{
			sprint (other, ", ");
		}
		acount = WEAPON_SHOTGUN;
		s = ftos (self.exnails);
		sprint (other, s);
		sprint (other, " nails");
	}
	if (self.exrockets)
	{
		if (acount)
		{
			sprint (other, ", ");
		}
		acount = WEAPON_SHOTGUN;
		s = ftos (self.exrockets);
		sprint (other, s);
		sprint (other, " rockets");
	}
	if (self.excells)
	{
		if (acount)
		{
			sprint (other, ", ");
		}
		acount = WEAPON_SHOTGUN;
		s = ftos (self.excells);
		sprint (other, s);
		sprint (other, " cells");
	}
	sprint (other, "\n");
	sound (other, CHAN_ITEM, "weapons/lock4.wav", WEAPON_SHOTGUN, ATTN_NORM);
	stuffcmd (other, "bf\n");
	remove (self);
	self = other;
};

void () DropBackpack =
{
	local entity item;

	if (!(((self.exshells + self.exnails) + self.exrockets) + self.excells))
	{
		return;
	}
	item = spawn ();
	item.origin = (self.origin - '0 0 24');
	item.items = self.weapon;
	if ((item.items == IT_AXE))
	{
		item.netname = "Axe";
	}
	else
	{
		if ((item.items == IT_SHOTGUN))
		{
			item.netname = "Pistol";
		}
		else
		{
			if ((item.items == IT_SUPER_SHOTGUN))
			{
				item.netname = "SMG";
			}
			else
			{
				if ((item.items == IT_NAILGUN))
				{
					item.netname = "Rifle";
				}
				else
				{
					if ((item.items == IT_SUPER_NAILGUN))
					{
						item.netname = "Super Nailgun";
					}
					else
					{
						if ((item.items == IT_GRENADE_LAUNCHER))
						{
							item.netname = "Grenade Launcher";
						}
						else
						{
							if ((item.items == IT_ROCKET_LAUNCHER))
							{
								item.netname = "Rocket Launcher";
							}
							else
							{
								if ((item.items == IT_LIGHTNING))
								{
									item.netname = "Thunderbolt";
								}
								else
								{
									item.netname = "";
								}
							}
						}
					}
				}
			}
		}
	}
	item.exshells = self.exshells;
	item.exnails = self.exnails;
	item.exrockets = self.exrockets;
	item.excells = self.excells;
	item.velocity_z = 300;
	item.velocity_x = (-100 + (random () * 200));
	item.velocity_y = (-100 + (random () * 200));
	item.flags = FL_ITEM;
	item.solid = SOLID_TRIGGER;
	item.movetype = MOVETYPE_TOSS;
	setmodel (item, "progs/backpack.mdl");
	setsize (item, '-16 -16 0', '16 16 56');
	item.touch = BackpackTouch;
	item.nextthink = (time + 120);
	item.think = SUB_Remove;
};

/*
========================
Grenades By mexicouger
------------------------
*/
void() plasma_nade_touch =
{
if (other.classname != "player")
		return;
	
	if (other.plasma_lives >= 4) {
	}
	
	else {
	other.plasma_lives += 1;
	sprint (other, "picked up a Plasma grenade\n");
	sound (self, CHAN_WEAPON, "weapons/pbounce.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	self.mdl = self.model;
	self.model = string_null;
	self.solid = SOLID_NOT;
	
	if (deathmatch) {
	self.nextthink = time + 20;
	self.think = SUB_regen;
	}
	activator = other;
	SUB_UseTargets();           
}                    
};

void() nade_touch =
{
if (other.classname != "player")
		return;
	
	if (other.nade_lives >= 4) {
	}
	
	else {
	other.nade_lives += 1;
	sprint (other, "picked up a Frag grenade\n");
	sound (self, CHAN_WEAPON, "weapons/grenpick.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	self.mdl = self.model;
	self.model = string_null;
	self.solid = SOLID_NOT;
	
	if (deathmatch) {
	self.nextthink = time + 20;
	self.think = SUB_regen;
	}
	activator = other;
	SUB_UseTargets();           
}                    
};

void() item_nade =
{
	self.touch = nade_touch;
	setmodel(self, "progs/fraggren.mdl");
	precache_sound ("weapons/grenpick.wav");
	setsize (self, '0 0 0', ' 2 2 2');
	StartItem();
};

void() item_plasma_nade =
{
	self.touch = plasma_nade_touch;
	setmodel(self, "progs/plasgren.mdl");
	setsize (self, '0 0 0', ' 2 2 2');
	StartItem();
};

