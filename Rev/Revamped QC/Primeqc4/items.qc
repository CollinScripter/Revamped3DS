void() W_SetCurrentAmmo;
/* ALL LIGHTS SHOULD BE 0 1 0 IN COLOR ALL OTHER ITEMS SHOULD
BE .8 .3 .4 IN COLOR */

void() SUB_regen =
{
	self.model = self.mdl;		// restore original model
	self.solid = SOLID_TRIGGER;	// allow it to be touched again
	sound (self, CHAN_VOICE, "items/itembk2.wav", 1, ATTN_NORM);	// play respawn sound
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



/*
============
PlaceItem

plants the object on the floor
============
*/
void() PlaceItem =
{
	self.mdl = self.model;
	self.flags = FL_ITEM;	
	self.solid = SOLID_TRIGGER;
	self.movetype = MOVETYPE_NONE;	
	self.velocity = '0 0 0';
	if (self.classname == "etank")
	setorigin(self, self.origin);	//The metroid Float
	else	
	setorigin(self, self.origin + '0 0 40');
};

/*
============
StartItem

Sets the clipping size and plants the object on the floor
============
*/
void() StartItem =
{
	self.nextthink = time + 0.2;	// items start after other solids
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
float (entity e, float healamount, float ignore) T_Heal =
{
	if (e.health <= 0)
		return 0;
	if ((!ignore) && (e.health >= other.max_health))
		return 0;
	healamount = ceil(healamount);

	e.health = e.health + healamount;
	if ((!ignore) && (e.health >= other.max_health))
		e.health = other.max_health;
		
	return 1;
};

/*QUAKED item_health (.3 .3 1) (0 0 0) (32 32 32) rotten megahealth
Health box. Normally gives 25 points.
Rotten box heals 5-10 points,
megahealth will add 100 health, then 
rot you down to your maximum health limit, 
one point per second.
*/

float	H_ROTTEN = 1;
float	H_MEGA = 2;
.float	healamount, healtype;
void() health_touch;
void() item_megahealth_rot;

void() item_health =
{	
	self.touch = health_touch;

	if (self.spawnflags & H_ROTTEN)
	{
		precache_model("maps/b_bh10.bsp");

		precache_sound("items/r_item1.wav");
		setmodel(self, "maps/b_bh10.bsp");
		self.noise = "items/r_item1.wav";
		self.healamount = 15;
		self.healtype = 0;
	}
	else
	if (self.spawnflags & H_MEGA)
	{
		precache_model("maps/b_bh100.bsp");
		precache_sound("items/r_item2.wav");
		setmodel(self, "maps/b_bh100.bsp");
		self.noise = "items/r_item2.wav";
		self.healamount = 100;
		self.healtype = 2;
	}
	else
	{
		precache_model("maps/b_bh25.bsp");
		precache_sound("items/health1.wav");
		setmodel(self, "maps/b_bh25.bsp");
		self.noise = "items/health1.wav";
		self.healamount = 25;
		self.healtype = 1;
	}
	setsize (self, '0 0 0', '32 32 56');
	StartItem ();
};
//Prime Health 1
void() item_health1 =
{
	precache_model("progs/health3.spr");
		precache_sound("items/r_item1.wav");
		setmodel(self, "progs/health3.spr");
		self.noise = "items/r_item1.wav";
		self.classname = "health1";
		self.touch = health_touch;	
		self.healtype = 0;
		setsize (self, '-7 -7 0', '7 7 7');
		StartItem ();
};
//Prime health2
void() item_health2 =
{
	precache_model("progs/health.spr");
		precache_sound("items/r_item1.wav");
		setmodel(self, "progs/health.spr");
		self.noise = "items/r_item1.wav";
		self.classname = "health2";
		self.touch = health_touch;
		self.healtype = 0;
		setsize (self, '-7 -7 0', '7 7 7');
		StartItem ();
};
//Prime health3
void() item_health3 =
{
	precache_model("progs/health2.spr");
		precache_sound("items/r_item1.wav");
		setmodel(self, "progs/health2.spr");
		self.noise = "items/r_item1.wav";
		self.classname = "health3";
		self.touch = health_touch;
		self.healtype = 0;
		setsize (self, '-7 -7 0', '7 7 7');
		StartItem ();
};
void() health_touch =
{
	local	string	s;
	
	if (other.classname != "player")
		return;
	
	if (self.classname == "health1")	//Oh my... So much globbered code Just for Health...
{
	if (other.energy == 0)
		{
	if (other.health >= 99)
	return;
	other.health = other.health + 20;
	if (other.health >= 99)
	other.health = 99;
	}
	if (other.energy == 1)
	{
	if (other.health >= 199)
	return;
	other.health = other.health + 20;
	if (other.health >= 199)
	other.health = 199;
	}
	if (other.energy == 2)
		{
	if (other.health >= 299)
	return;
	other.health = other.health + 20;
	if (other.health >= 299)
	other.health = 299;
	}
	if (other.energy == 3)
		{
	if (other.health >= 399)
	return;
	other.health = other.health + 20;
	if (other.health >= 399)
	other.health = 399;
	}
	if (other.energy == 4)
		{
	if (other.health >= 499)
	return;
	other.health = other.health + 20;
	if (other.health >= 499)
	other.health = 499;
	}
	if (other.energy == 5)
		{
	if (other.health >= 599)
	return;
	other.health = other.health + 20;
	if (other.health >= 599)
	other.health = 599;
	}
	if (other.energy == 6)
		{
	if (other.health >= 699)
	return;
	other.health = other.health + 20;
	if (other.health >= 699)
	other.health = 699;
	}
	if (other.energy == 7)
		{
	if (other.health >= 799)
	return;
	other.health = other.health + 20;
	if (other.health >= 799)
	other.health = 799;
	}
	if (other.energy == 8)
		{
	if (other.health >= 899)
	return;
	other.health = other.health + 20;
	if (other.health >= 899)
	other.health = 899;
	}
	if (other.energy == 9)
		{
	if (other.health >= 999)
	return;
	other.health = other.health + 20;
	if (other.health >= 999)
	other.health = 999;
	}
}
	
	if (self.classname == "health2")
{
	if (other.energy == 0)
		{
	if (other.health >= 99)
	return;
	other.health = other.health + 50;
	if (other.health >= 99)
	other.health = 99;
	}
	if (other.energy == 1)
	{
	if (other.health >= 199)
	return;
	other.health = other.health + 50;
	if (other.health >= 199)
	other.health = 199;
	}
	if (other.energy == 2)
		{
	if (other.health >= 299)
	return;
	other.health = other.health + 50;
	if (other.health >= 299)
	other.health = 299;
	}
	if (other.energy == 3)
		{
	if (other.health >= 399)
	return;
	other.health = other.health + 50;
	if (other.health >= 399)
	other.health = 399;
	}
	if (other.energy == 4)
		{
	if (other.health >= 499)
	return;
	other.health = other.health + 50;
	if (other.health >= 499)
	other.health = 499;
	}
	if (other.energy == 5)
		{
	if (other.health >= 599)
	return;
	other.health = other.health + 50;
	if (other.health >= 599)
	other.health = 599;
	}
	if (other.energy == 6)
		{
	if (other.health >= 699)
	return;
	other.health = other.health + 50;
	if (other.health >= 699)
	other.health = 699;
	}
	if (other.energy == 7)
		{
	if (other.health >= 799)
	return;
	other.health = other.health + 50;
	if (other.health >= 799)
	other.health = 799;
	}
	if (other.energy == 8)
		{
	if (other.health >= 899)
	return;
	other.health = other.health + 50;
	if (other.health >= 899)
	other.health = 899;
	}
	if (other.energy == 9)
		{
	if (other.health >= 999)
	return;
	other.health = other.health + 50;
	if (other.health >= 999)
	other.health = 999;
	}
}
	
	else
{
	if (other.energy == 0)
		{
	if (other.health >= 99)
	return;
	other.health = other.health + 100;
	if (other.health >= 99)
	other.health = 99;
	}
	if (other.energy == 1)
	{
	if (other.health >= 199)
	return;
	other.health = other.health + 100;
	if (other.health >= 199)
	other.health = 199;
	}
	if (other.energy == 2)
		{
	if (other.health >= 299)
	return;
	other.health = other.health + 100;
	if (other.health >= 299)
	other.health = 299;
	}
	if (other.energy == 3)
		{
	if (other.health >= 399)
	return;
	other.health = other.health + 100;
	if (other.health >= 399)
	other.health = 399;
	}
	if (other.energy == 4)
		{
	if (other.health >= 499)
	return;
	other.health = other.health + 100;
	if (other.health >= 499)
	other.health = 499;
	}
	if (other.energy == 5)
		{
	if (other.health >= 599)
	return;
	other.health = other.health + 100;
	if (other.health >= 599)
	other.health = 599;
	}
	if (other.energy == 6)
		{
	if (other.health >= 699)
	return;
	other.health = other.health + 100;
	if (other.health >= 699)
	other.health = 699;
	}
	if (other.energy == 7)
		{
	if (other.health >= 799)
	return;
	other.health = other.health + 100;
	if (other.health >= 799)
	other.health = 799;
	}
	if (other.energy == 8)
		{
	if (other.health >= 899)
	return;
	other.health = other.health + 100;
	if (other.health >= 899)
	other.health = 899;
	}
	if (other.energy == 9)
		{
	if (other.health >= 999)
	return;
	other.health = other.health + 100;
	if (other.health >= 999)
	other.health = 999;
	}
}

	sprint(other, "You receive ");
	s = ftos(other.health);
	sprint(other, s);
	sprint(other, " health\n");
	
// health touch sound
	sound(other, CHAN_ITEM, self.noise, 1, ATTN_NORM);

	stuffcmd (other, "bf\n");
	
	self.model = string_null;
	self.solid = SOLID_NOT;

		if (deathmatch != 2)		// deathmatch 2 is the silly old rules
		{
			if (deathmatch)
				self.nextthink = time + 20;
			self.think = SUB_regen;
		}
	
	activator = other;
	SUB_UseTargets();				// fire all targets / killtargets
};	

void() item_megahealth_rot =
{
	other = self.owner;
	
	if (other.health > other.max_health)
	{
		other.health = other.health - 1;
		self.nextthink = time + 1;
		return;
	}

// it is possible for a player to die and respawn between rots, so don't
// just blindly subtract the flag off
	other.items = other.items - (other.items & IT_SUPERHEALTH);
	
	if (deathmatch == 1)	// deathmatch 2 is silly old rules
	{
		self.nextthink = time + 20;
		self.think = SUB_regen;
	}
};

/*
===============================================================================

ARMOR

===============================================================================
*/

void() armor_touch;

void() armor_touch =
{
	local	float	type, value, bit;
	
	if (other.health <= 0)
		return;
	if (other.classname != "player")
		return;

	if (self.classname == "item_armor1")
	{
		type = 0.3;
		value = 100;
		bit = IT_ARMOR1;
	}
	if (self.classname == "item_armor2")
	{
		type = 0.6;
		value = 150;
		bit = IT_ARMOR2;
	}
	if (self.classname == "item_armorInv")
	{
		type = 0.8;
		value = 200;
		bit = IT_ARMOR3;
	}
	if (other.armortype*other.armorvalue >= type*value)
		return;
		
	other.armortype = type;
	other.armorvalue = value;
	other.items = other.items - (other.items & (IT_ARMOR1 | IT_ARMOR2 | IT_ARMOR3)) + bit;

	self.solid = SOLID_NOT;
	self.model = string_null;
	if (deathmatch == 1)
		self.nextthink = time + 20;
	self.think = SUB_regen;

	sprint(other, "You got armor\n");
// armor touch sound
	sound(other, CHAN_ITEM, "items/armor1.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	
	activator = other;
	SUB_UseTargets();				// fire all targets / killtargets
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
	if (other.ammo_shells > 100)
		other.ammo_shells = 100;
	if (other.ammo_nails > 200)
		other.ammo_nails = 200;
	if (other.ammo_rockets > 100)
		other.ammo_rockets = 100;		
	if (other.ammo_cells > 100)
		other.ammo_cells = 100;		
};


float(float w) RankForWeapon =
{
	if (w == IT_LIGHTNING)
		return 1;
	if (w == IT_MAGMA)
		return 2;
	if (w == IT_SNIPER)
		return 3;
	if (w == IT_GRENADE_LAUNCHER)
		return 4;
	if (w == IT_ROCKET)
		return 5;
	if (w == IT_SPLASER)
		return 6;
	return 7;
};

/*
=============
Deathmatch_Weapon

Deathmatch weapon change rules for picking up a weapon

.float		ammo_shells, ammo_nails, ammo_rockets, ammo_cells;
=============
*/
void(float old, float new) Deathmatch_Weapon =
{
	local float or, nr;

// change self.weapon if desired
	or = RankForWeapon (self.weapon);
	nr = RankForWeapon (new);
	if ( nr < or )
		self.weapon = new;
};

/*
=============
weapon_touch
=============
*/
//float() W_BestWeapon;

void() weapon_touch =
{
	local	float	hadammo, new, old;
	local	entity	stemp;
	local	float	leave;

	if (!(other.flags & FL_CLIENT))
		return;

// if the player was using his best weapon, change up to the new one if better		
	stemp = self;
	self = other;
	self = stemp;

	if (deathmatch == 2 || coop)
		leave = 1;
	else
		leave = 0;
	
	if (self.classname == "weapon_nailgun")
	{
		if (leave && (other.items & IT_SPLASER) )
			return;
		hadammo = other.ammo_nails;			
		new = IT_SPLASER;
		if (self.ammo_nails >= 45)
		return;
		other.ammo_nails = other.ammo_nails + 8;
		if (self.ammo_nails >= 45)
		self.ammo_nails = 45;
	}
	else if (self.classname == "weapon_sniper")
	{
		if (leave && (other.items & IT_SNIPER) )
			return;
		hadammo = other.ammo_rockets;			
		new = IT_SNIPER;
		if (self.ammo_sniper >= 20)
		return;
		other.ammo_sniper = other.ammo_sniper + 4;
		if (self.ammo_sniper >= 20)
		self.ammo_sniper = 20;
	}
	else if (self.classname == "weapon_supershotgun")
	{
		if (leave && (other.items & IT_ROCKET) )
			return;
		hadammo = other.ammo_rockets;			
		new = IT_ROCKET;
		if (other.ammo_rockets >= 25)
		return;
		other.ammo_rockets = other.ammo_rockets + 5;
		if (other.ammo_rockets >= 25)
		other.ammo_rockets = 25;
	}
	else if (self.classname == "weapon_magma")
	{
		if (leave && (other.items & IT_MAGMA) )
			return;
		hadammo = other.ammo_lava;			
		new = IT_MAGMA;
		if (other.ammo_lava >= 45)
		return;
		other.ammo_lava = other.ammo_lava + 10;
		if (other.ammo_lava >= 45)
		other.ammo_rockets = 45;
	}
	else if (self.classname == "weapon_grenadelauncher")
	{
		if (leave && (other.items & IT_GRENADE_LAUNCHER) )
			return;
		hadammo = other.ammo_rockets;			
		new = IT_GRENADE_LAUNCHER;
		other.ammo_rockets = other.ammo_rockets + 5;
	}
	else if (self.classname == "weapon_lightning")
	{
		if (leave && (other.items & IT_LIGHTNING) )
			return;
		hadammo = other.ammo_rockets;			
		new = IT_LIGHTNING;
		other.ammo_cells = other.ammo_cells + 15;
	}
	else if (self.classname == "weapon_ric")
	{
		if (leave && (other.items & IT_RIC) )
			return;
		hadammo = other.ammo_rockets;			
		new = IT_RIC;
		if (other.ammo_ric >= 100)
		return;
		other.ammo_ric = other.ammo_ric + 25;
		if (other.ammo_ric >= 80)
		other.ammo_ric = 100;
	}

	else
		objerror ("weapon_touch: unknown classname");

	sprint (other, "You got the ");
	sprint (other, self.netname);
	sprint (other, "\n");
// weapon touch sound
	sound (other, CHAN_ITEM, "weapons/pkup.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");

	bound_other_ammo ();

// change to the weapon
	old = other.items;
	other.items = other.items | new;
	
	stemp = self;
	self = other;

	if (!deathmatch)
		self.weapon = new;
	else
		Deathmatch_Weapon (old, new);

	W_SetCurrentAmmo();

	self = stemp;

	if (leave)
		return;

// remove it in single player, or setup for respawning in deathmatch
	self.model = string_null;
	self.solid = SOLID_NOT;
	if (deathmatch == 1)
		self.nextthink = time + 30;
	self.think = SUB_regen;
	
	activator = other;
	SUB_UseTargets();				// fire all targets / killtargets
};


/*Prime Weapon Rocket Launcher
*/
void() weapon_supershotgun =
{
	precache_model ("progs/item_rocket.mdl");
	setmodel (self, "progs/item_rocket.mdl");
	self.weapon = IT_ROCKET;
	self.netname = "Rocket Launcher";
	self.touch = weapon_touch;
	self.effects = EF_DIMLIGHT;
	setsize (self, '-7 -7 0', '7 7 7');
	StartItem ();
};

/*Prime Weapon Splaser
*/

void() weapon_nailgun =
{
	precache_model ("progs/item_splaser.spr");
	setmodel (self, "progs/item_splaser.spr");
	self.weapon = IT_SPLASER;
	self.netname = "Splaser";
	self.touch = weapon_touch;
	setsize (self, '-7 -7 0', '7 7 7');
	StartItem ();
};

/* Prime Weapon SNiper
*/

void() weapon_sniper =
{
	precache_model ("progs/item_sniper.spr");
	setmodel (self, "progs/item_sniper.spr");
	self.weapon = IT_SNIPER;
	self.classname = "weapon_sniper";
	self.netname = "Sniper";
	self.touch = weapon_touch;
	setsize (self, '-7 -7 0', '7 7 7');
	StartItem ();
};

/*QUAKED weapon_grenadelauncher (0 .5 .8) (-16 -16 0) (16 16 32)
*/

void() weapon_grenadelauncher =
{
	precache_model ("progs/g_rock.mdl");
	setmodel (self, "progs/g_rock.mdl");
	self.weapon = 3;
	self.netname = "Grenade Launcher";
	self.touch = weapon_touch;
	setsize (self, '-16 -16 0', '16 16 56');
	StartItem ();
};

/*Prime Weapon Magma beam
*/

void() weapon_magma =
{
	precache_model ("progs/item_magma.spr");
	setmodel (self, "progs/item_magma.spr");
	self.weapon = 3;
	self.classname = "weapon_magma";
	self.netname = "Magma Beam";
	self.touch = weapon_touch;
	setsize (self, '-16 -16 0', '16 16 56');
	StartItem ();
};


/*QUAKED weapon_lightning (0 .5 .8) (-16 -16 0) (16 16 32)
*/

void() weapon_lightning =
{
	precache_model ("progs/g_light.mdl");
	setmodel (self, "progs/g_light.mdl");
	self.weapon = 3;
	self.netname = "Thunderbolt";
	self.touch = weapon_touch;
	setsize (self, '-16 -16 0', '16 16 56');
	StartItem ();
};

/*Prime Weapon Richochet beam
*/
void() weapon_ric =
{
	precache_model ("progs/item_ric.spr");
	setmodel (self, "progs/item_ric.spr");
	self.weapon = IT_RIC;
	self.classname = "weapon_ric";
	self.netname = "Richochet Beam";
	self.touch = weapon_touch;
	setsize (self, '-7 -7 0', '7 7 7');
	StartItem ();
};



/*
===============================================================================

AMMO

===============================================================================
*/

void() ammo_touch =
{
local entity	stemp;


	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

// if the player was using his best weapon, change up to the new one if better		
	stemp = self;
	self = other;
	self = stemp;


// shotgun
	if (self.weapon == 1)
	{
		if (other.ammo_shells >= 100)
			return;
		other.ammo_shells = other.ammo_shells + self.aflag;
	}

//	rockets
	if (self.weapon == 3)
	{
		if (other.ammo_rockets >= 100)
			return;
		other.ammo_rockets = other.ammo_rockets + self.aflag;
	}

//	cells
	if (self.weapon == 4)
	{
		if (other.ammo_cells >= 100)
			return;
		other.ammo_cells = other.ammo_cells + self.aflag;
	}

	bound_other_ammo ();
	
	sprint (other, "You got the ");
	sprint (other, self.netname);
	sprint (other, "\n");
// ammo touch sound
	sound (other, CHAN_ITEM, "weapons/lock4.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");


// if changed current ammo, update it
	stemp = self;
	self = other;
	W_SetCurrentAmmo();
	self = stemp;

// remove it in single player, or setup for respawning in deathmatch
	self.model = string_null;
	self.solid = SOLID_NOT;
	if (deathmatch == 1)
		self.nextthink = time + 30;
	self.think = SUB_regen;

	activator = other;
	SUB_UseTargets();				// fire all targets / killtargets
};




float WEAPON_BIG2 = 1;

/*QUAKED item_shells (0 .5 .8) (0 0 0) (32 32 32) big
*/

void() item_shells =
{
	self.touch = ammo_touch;

	if (self.spawnflags & WEAPON_BIG2)
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
	self.weapon = 1;
	self.netname = "shells";
	setsize (self, '0 0 0', '32 32 56');
	StartItem ();
};

/*QUAKED item_spikes (0 .5 .8) (0 0 0) (32 32 32) big
*/

void() item_spikes =
{
	self.touch = ammo_touch;

	if (self.spawnflags & WEAPON_BIG2)
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
	self.weapon = 2;
	self.netname = "nails";
	setsize (self, '0 0 0', '32 32 56');
	StartItem ();
};

/*QUAKED item_rockets (0 .5 .8) (0 0 0) (32 32 32) big
*/

void() item_rockets =
{
	self.touch = ammo_touch;

	if (self.spawnflags & WEAPON_BIG2)
	{
		precache_model ("maps/b_rock1.bsp");
		setmodel (self, "maps/b_rock1.bsp");
		self.aflag = 10;
	}
	else
	{
		precache_model ("maps/b_rock0.bsp");
		setmodel (self, "maps/b_rock0.bsp");
		self.aflag = 5;
	}
	self.weapon = 3;
	self.netname = "rockets";
	setsize (self, '0 0 0', '32 32 56');
	StartItem ();
};


/*QUAKED item_cells (0 .5 .8) (0 0 0) (32 32 32) big
*/

void() item_cells =
{
	self.touch = ammo_touch;

	if (self.spawnflags & WEAPON_BIG2)
	{
		precache_model ("maps/b_batt1.bsp");
		setmodel (self, "maps/b_batt1.bsp");
		self.aflag = 12;
	}
	else
	{
		precache_model ("maps/b_batt0.bsp");
		setmodel (self, "maps/b_batt0.bsp");
		self.aflag = 6;
	}
	self.weapon = 4;
	self.netname = "cells";
	setsize (self, '0 0 0', '32 32 56');
	StartItem ();
};


/*QUAKED item_weapon (0 .5 .8) (0 0 0) (32 32 32) shotgun rocket spikes big
DO NOT USE THIS!!!! IT WILL BE REMOVED!
*/

float WEAPON_SHOTGUN = 1;
float WEAPON_ROCKET = 2;
float WEAPON_SPIKES = 4;
float WEAPON_BIG = 8;
void() item_weapon =
{
	self.touch = ammo_touch;

	if (self.spawnflags & WEAPON_SHOTGUN)
	{
		if (self.spawnflags & WEAPON_BIG)
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
		self.weapon = 1;
		self.netname = "shells";
	}

	if (self.spawnflags & WEAPON_SPIKES)
	{
		if (self.spawnflags & WEAPON_BIG)
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
		self.weapon = 2;
		self.netname = "spikes";
	}

	if (self.spawnflags & WEAPON_ROCKET)
	{
		if (self.spawnflags & WEAPON_BIG)
		{
			precache_model ("maps/b_rock1.bsp");
			setmodel (self, "maps/b_rock1.bsp");
			self.aflag = 10;
		}
		else
		{
			precache_model ("maps/b_rock0.bsp");
			setmodel (self, "maps/b_rock0.bsp");
			self.aflag = 5;
		}
		self.weapon = 3;
		self.netname = "rockets";
	}
	
	setsize (self, '0 0 0', '32 32 56');
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

	sprint (other, "You got the ");
	sprint (other, self.netname);
	sprint (other,"\n");

	sound (other, CHAN_ITEM, self.noise, 1, ATTN_NORM);
	stuffcmd (other, "bf\n");
	other.items = other.items | self.items;

	if (!coop)
	{	
		self.solid = SOLID_NOT;
		self.model = string_null;
	}

	activator = other;
	SUB_UseTargets();				// fire all targets / killtargets
};


void() key_setsounds =
{
	if (world.worldtype == 0)
	{
		precache_sound ("misc/medkey.wav");
		self.noise = "misc/medkey.wav";
	}
	if (world.worldtype == 1)
	{
		precache_sound ("misc/runekey.wav");
		self.noise = "misc/runekey.wav";
	}
	if (world.worldtype == 2)
	{
		precache_sound2 ("misc/basekey.wav");
		self.noise = "misc/basekey.wav";
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
	if (world.worldtype == 0)
	{
		precache_model ("progs/w_s_key.mdl");
		setmodel (self, "progs/w_s_key.mdl");
		self.netname = "silver key";
	}
	else if (world.worldtype == 1)
	{
		precache_model ("progs/m_s_key.mdl");
		setmodel (self, "progs/m_s_key.mdl");
		self.netname = "silver runekey";
	}
	else if (world.worldtype == 2)
	{
		precache_model2 ("progs/b_s_key.mdl");
		setmodel (self, "progs/b_s_key.mdl");
		self.netname = "silver keycard";
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
	if (world.worldtype == 0)
	{
		precache_model ("progs/w_g_key.mdl");
		setmodel (self, "progs/w_g_key.mdl");
		self.netname = "gold key";
	}
	if (world.worldtype == 1)
	{
		precache_model ("progs/m_g_key.mdl");
		setmodel (self, "progs/m_g_key.mdl");
		self.netname = "gold runekey";
	}
	if (world.worldtype == 2)
	{
		precache_model2 ("progs/b_g_key.mdl");
		setmodel (self, "progs/b_g_key.mdl");
		self.netname = "gold keycard";
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
	self.classname = "";		// so rune doors won't find it
	
	activator = other;
	SUB_UseTargets();				// fire all targets / killtargets
};


/*QUAKED item_sigil (0 .5 .8) (-16 -16 -24) (16 16 32) E1 E2 E3 E4
End of level sigil, pick up to end episode and return to jrstart.
*/

void() item_sigil =
{
	if (!self.spawnflags)
		objerror ("no spawnflags");

	precache_sound ("misc/runekey.wav");
	self.noise = "misc/runekey.wav";

	if (self.spawnflags & 1)
	{
		precache_model ("progs/end1.mdl");
		setmodel (self, "progs/end1.mdl");
	}
	if (self.spawnflags & 2)
	{
		precache_model2 ("progs/end2.mdl");
		setmodel (self, "progs/end2.mdl");
	}
	if (self.spawnflags & 4)
	{
		precache_model2 ("progs/end3.mdl");
		setmodel (self, "progs/end3.mdl");
	}
	if (self.spawnflags & 8)
	{
		precache_model2 ("progs/end4.mdl");
		setmodel (self, "progs/end4.mdl");
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

void() powerup_touch;


void() powerup_touch =
{

	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

	sprint (other, "You got the ");
	sprint (other, self.netname);
	sprint (other,"\n");

	if (deathmatch)
	{
		self.mdl = self.model;
		
		if ((self.classname == "item_artifact_invulnerability") ||
			(self.classname == "item_artifact_invisibility"))
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
	if (self.classname == "item_artifact_envirosuit")
	{
		other.rad_time = 1;
		other.radsuit_finished = time + 30;
	}
	
	if (self.classname == "item_artifact_invulnerability")
	{
		other.invincible_time = 1;
		other.invincible_finished = time + 30;
	}
	
	if (self.classname == "item_artifact_invisibility")
	{
		other.invisible_time = 1;
		other.invisible_finished = time + 30;
	}

	if (self.classname == "item_artifact_super_damage")
	{
		other.super_time = 1;
		other.super_damage_finished = time + 30;
	}	

	activator = other;
	SUB_UseTargets();				// fire all targets / killtargets
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
	self.netname = "Quad Damage";
	self.items = IT_QUAD;
	setsize (self, '-16 -16 -24', '16 16 32');
	StartItem ();
};



/*
===============================================================================

PLAYER BACKPACKS

===============================================================================
*/

void() BackpackTouch =
{
	local string	s;
	local	float	old, new;
	local		entity	stemp;
	local	float	acount;
	
	if (other.classname != "player")
		return;
	if (other.health <= 0)
		return;

	acount = 0;
	sprint (other, "You get ");

	if (self.items)
		if ((other.items & self.items) == 0)
		{
			acount = 1;
			sprint (other, "the ");
			sprint (other, self.netname);
		}

// if the player was using his best weapon, change up to the new one if better		
	stemp = self;
	self = other;
	//best = W_BestWeapon();
	self = stemp;

// change weapons
	other.ammo_shells = other.ammo_shells + self.ammo_shells;
	other.ammo_nails = other.ammo_nails + self.ammo_nails;
	other.ammo_rockets = other.ammo_rockets + self.ammo_rockets;
	other.ammo_cells = other.ammo_cells + self.ammo_cells;

	new = self.items;
	if (!new)
		new = other.weapon;
	old = other.items;
	other.items = other.items | new;
	
	bound_other_ammo ();

	if (self.ammo_shells)
	{
		if (acount)
			sprint(other, ", ");
		acount = 1;
		s = ftos(self.ammo_shells);
		sprint (other, s);
		sprint (other, " shells");
	}
	if (self.ammo_nails)
	{
		if (acount)
			sprint(other, ", ");
		acount = 1;
		s = ftos(self.ammo_nails);
		sprint (other, s);
		sprint (other, " nails");
	}
	if (self.ammo_rockets)
	{
		if (acount)
			sprint(other, ", ");
		acount = 1;
		s = ftos(self.ammo_rockets);
		sprint (other, s);
		sprint (other, " rockets");
	}
	if (self.ammo_cells)
	{
		if (acount)
			sprint(other, ", ");
		acount = 1;
		s = ftos(self.ammo_cells);
		sprint (other, s);
		sprint (other, " cells");
	}
	
	sprint (other, "\n");
// backpack touch sound
	sound (other, CHAN_ITEM, "weapons/lock4.wav", 1, ATTN_NORM);
	stuffcmd (other, "bf\n");

// remove the backpack, change self to the player
	remove(self);
	self = other;

// change to the weapon
	if (!deathmatch)
		self.weapon = new;
	else
		Deathmatch_Weapon (old, new);

	W_SetCurrentAmmo ();
};

/*
===============
DropBackpack
===============
*/
void() DropBackpack =
{
	local entity	item;

	if (!(self.ammo_shells + self.ammo_nails + self.ammo_rockets + self.ammo_cells))
		return;	// nothing in it

	item = spawn();
	item.origin = self.origin - '0 0 24';
	
	item.items = self.weapon;
	if (item.items == IT_MORPHBALL)
		item.netname = "Axe";
	else if (item.items == IT_BLASTER)
		item.netname = "Shotgun";
	else if (item.items == IT_ROCKET)
		item.netname = "Double-barrelled Shotgun";
	else if (item.items == IT_SPLASER)
		item.netname = "Nailgun";
	else if (item.items == IT_SNIPER)
		item.netname = "Super Nailgun";
	else if (item.items == IT_GRENADE_LAUNCHER)
		item.netname = "Grenade Launcher";
	else if (item.items == IT_MAGMA)
		item.netname = "Rocket Launcher";
	else if (item.items == IT_LIGHTNING)
		item.netname = "Thunderbolt";
	else
		item.netname = "";

	item.ammo_shells = self.ammo_shells;
	item.ammo_nails = self.ammo_nails;
	item.ammo_rockets = self.ammo_rockets;
	item.ammo_cells = self.ammo_cells;

	item.velocity_z = 300;
	item.velocity_x = -100 + (random() * 200);
	item.velocity_y = -100 + (random() * 200);
	
	item.flags = FL_ITEM;
	item.solid = SOLID_TRIGGER;
	item.movetype = MOVETYPE_TOSS;
	setmodel (item, "progs/backpack.mdl");
	setsize (item, '-16 -16 0', '16 16 56');
	item.touch = BackpackTouch;
	
	item.nextthink = time + 120;	// remove after 2 minutes
	item.think = SUB_Remove;
};
void() energy_touch =
{
if (other.classname != "player")
	return;
other.energy = other.energy + 1;
if (other.energy == 1)
{
other.health = 199;
other.max_health = 199;
}
else if (other.energy == 2)
{
other.health = 299;
other.max_health = 299;
}
else if (other.energy == 3)
{
other.health = 399;
other.max_health = 399;
}
else if (other.energy == 4)
{
other.health = 499;
other.max_health = 499;
}
else if (other.energy == 5)
{
other.health = 599;
other.max_health = 599;
}
else if (other.energy == 6)
{
other.health = 699;
other.max_health = 699;
}
else if (other.energy == 7)
{
other.health = 799;
other.max_health = 799;
}
else if (other.energy == 8)
{
other.health = 899;
other.max_health = 899;
}
else if (other.energy == 9)
{
other.health = 999;
other.max_health = 999;
}
else
other.max_health = 99;

self.model = string_null;
self.solid = SOLID_NOT;

activator = other;
SUB_UseTargets();				// fire all targets / killtargets
};
void() item_energytank =
{	
		if (deathmatch)
		remove(self);
		precache_model("progs/etank.mdl");
		precache_sound("items/r_item1.wav");
		setmodel(self, "progs/etank.mdl");
		self.noise = "items/r_item1.wav";
		self.classname = "etank";
		self.effects = EF_DIMLIGHT;
		self.healamount = other.max_health;
		self.touch = energy_touch;
		setsize (self, '-7 -7 0', '7 7 7');
		StartItem ();
}; 